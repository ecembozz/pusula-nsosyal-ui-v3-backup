#!/usr/bin/env python3
"""Offline PUSULA Semantic Candidate V1 batch labeler.

This script deliberately keeps model inference out of the web runtime.
It trains lightweight heads on Dataset V3, embeds input posts with a frozen
multilingual-e5-base encoder, and writes provider-independent JSONL that can be
validated by `scripts/build_semantic_cache.py`.

Candidate policy:
- dominant intent + confidence: V3 tranche 1 (128 cleaner rows)
- 4D intent vector + clickbait: all V3 rows (256, including boundary cases)
- OOD diagnostic: nearest cosine against all V3 training embeddings

Development note: `confidence` is a screening score derived from the auxiliary
classifier. It is not claimed to be a calibrated probability of correctness.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsRegressor

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

from benchmark_supervised_embeddings import INTENTS, encode_texts, read_jsonl

V1_FILES = [
    ROOT / "data/v3_realistic/train_ogretici_v1.jsonl",
    ROOT / "data/v3_realistic/train_eglendirici_v1.jsonl",
    ROOT / "data/v3_realistic/train_haber_v1.jsonl",
    ROOT / "data/v3_realistic/train_sosyal_v1.jsonl",
]
V2_FILES = [
    ROOT / "data/v3_realistic/train_ogretici_v2.jsonl",
    ROOT / "data/v3_realistic/train_eglendirici_v2.jsonl",
    ROOT / "data/v3_realistic/train_haber_v2.jsonl",
    ROOT / "data/v3_realistic/train_sosyal_v2.jsonl",
]
MODEL_NAME = "intfloat/multilingual-e5-base"
METHOD = "pusula-semantic-candidate-v1"


def load_training(paths):
    rows = []
    for path in paths:
        for row in read_jsonl(path):
            rows.append(
                {
                    "id": str(row["id"]),
                    "text": str(row["metin"]),
                    "dominant": str(row["dominant_intent"]),
                    "intent_vector": np.asarray(row["gercek_niyet"], dtype=float),
                    "clickbait": float(row["clickbait"]),
                }
            )
    return rows


def read_input(path: Path, text_key: str, id_key: str):
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        raw = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    elif suffix == ".json":
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            raw = parsed.get("posts") or parsed.get("items") or parsed.get("data")
            if raw is None:
                raise ValueError("JSON object input requires posts/items/data array")
        else:
            raw = parsed
    else:
        raise ValueError("input must be .jsonl or .json")

    if not isinstance(raw, list):
        raise ValueError("input must resolve to a list of records")

    rows = []
    seen = set()
    for index, row in enumerate(raw, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {index}: expected object")
        record_id = str(row.get(id_key, index))
        text = str(row.get(text_key, "")).strip()
        if not text:
            raise ValueError(f"row {index}: empty {text_key}")
        if record_id in seen:
            raise ValueError(f"duplicate id: {record_id}")
        seen.add(record_id)
        rows.append({"id": record_id, "text": text})
    return rows


def fit_heads(x_v1, v1_rows, x_all, all_rows):
    dom = np.asarray([r["dominant"] for r in v1_rows])
    clf = LogisticRegression(
        C=4.0,
        class_weight="balanced",
        max_iter=5000,
        solver="lbfgs",
        random_state=42,
    )
    clf.fit(x_v1, dom)

    y_all = np.asarray(
        [list(r["intent_vector"]) + [r["clickbait"]] for r in all_rows],
        dtype=float,
    )
    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(x_all, y_all)

    train_sim = x_all @ x_all.T
    np.fill_diagonal(train_sim, -1.0)
    nearest_train = np.max(train_sim, axis=1)
    # Conservative development screening threshold. A final threshold must be
    # re-estimated on untouched human-annotated data before a competition claim.
    ood_threshold = float(np.quantile(nearest_train, 0.05))
    return clf, knn, ood_threshold


def class_probabilities(clf, x):
    raw = clf.predict_proba(x)
    probs = np.zeros((len(x), 4), dtype=float)
    mapping = {name: i for i, name in enumerate(clf.classes_)}
    for j, name in enumerate(INTENTS):
        probs[:, j] = raw[:, mapping[name]]
    return probs


def screen_confidence(probs, nearest, ood_threshold):
    sorted_probs = np.sort(probs, axis=1)
    margin = np.clip(sorted_probs[:, -1] - sorted_probs[:, -2], 0.0, 1.0)
    max_prob = np.max(probs, axis=1)

    # Nearest-cosine is included only as an OOD guard. Keep the user-visible
    # confidence score easy to interpret and bounded; this is not calibration.
    score = np.clip(0.65 * max_prob + 0.35 * margin, 0.0, 1.0)
    score = np.where(nearest < ood_threshold, score * 0.55, score)
    return score, margin, max_prob


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--text-key", default="text")
    ap.add_argument("--id-key", default="id")
    ap.add_argument("--model", default=MODEL_NAME)
    args = ap.parse_args()

    input_rows = read_input(Path(args.input), args.text_key, args.id_key)
    v1 = load_training(V1_FILES)
    v2 = load_training(V2_FILES)
    all_train = v1 + v2

    if len(v1) != 128 or len(all_train) != 256:
        raise SystemExit(f"unexpected candidate training sizes: v1={len(v1)} all={len(all_train)}")
    if Counter(r["dominant"] for r in v1) != Counter({k: 32 for k in INTENTS}):
        raise SystemExit("V3 tranche 1 is no longer intent-balanced")
    if Counter(r["dominant"] for r in all_train) != Counter({k: 64 for k in INTENTS}):
        raise SystemExit("V3-256 is no longer intent-balanced")

    # One encoder pass makes the offline pipeline deterministic and efficient.
    all_texts = [r["text"] for r in all_train] + [r["text"] for r in input_rows]
    x, revision = encode_texts(all_texts, args.model, batch_size=16)
    x_train = x[: len(all_train)]
    x_v1 = x_train[: len(v1)]
    x_input = x[len(all_train) :]

    clf, knn, ood_threshold = fit_heads(x_v1, v1, x_train, all_train)
    vector_pred = np.clip(np.asarray(knn.predict(x_input), dtype=float), 0.0, 1.0)
    probs = class_probabilities(clf, x_input)
    dominant_index = np.argmax(probs, axis=1)
    dominant = [INTENTS[int(i)] for i in dominant_index]

    nearest = np.max(x_input @ x_train.T, axis=1)
    confidence, probability_margin, max_prob = screen_confidence(probs, nearest, ood_threshold)
    ood = nearest < ood_threshold

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, row in enumerate(input_rows):
            vec = vector_pred[i, :4]
            payload = {
                "id": row["id"],
                "text": row["text"],
                "intent_vector": [round(float(v), 6) for v in vec],
                "clickbait": round(float(vector_pred[i, 4]), 6),
                "dominant_intent": dominant[i],
                "confidence": round(float(confidence[i]), 6),
                "method": METHOD,
                "model": args.model,
                "prompt_version": None,
                "schema_version": "pusula-label-v2",
                "diagnostics": {
                    "dominant_probability": round(float(max_prob[i]), 6),
                    "dominant_margin": round(float(probability_margin[i]), 6),
                    "nearest_train_cosine": round(float(nearest[i]), 6),
                    "ood": bool(ood[i]),
                    "ood_threshold": round(float(ood_threshold), 6),
                    "encoder_revision": revision,
                    "dominant_head_training_rows": 128,
                    "vector_head_training_rows": 256,
                },
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    summary = {
        "method": METHOD,
        "model": args.model,
        "encoder_revision": revision,
        "input_count": len(input_rows),
        "dominant_distribution": dict(Counter(dominant)),
        "mean_confidence": float(np.mean(confidence)) if len(confidence) else None,
        "low_confidence_lt_0_50": int(np.sum(confidence < 0.50)),
        "ood_count": int(np.sum(ood)),
        "ood_rate": float(np.mean(ood)) if len(ood) else None,
        "ood_threshold": ood_threshold,
        "output": str(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
