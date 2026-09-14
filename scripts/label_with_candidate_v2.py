#!/usr/bin/env python3
"""Offline PUSULA Semantic Candidate V2 batch labeler.

Candidate V2 uses the corrected Dataset V4 semantics:
- frozen multilingual-e5-base encoder
- auxiliary dominant classifier trained only on 256 clear-intent rows
- canonical 4D vector + clickbait trained with semantic k-NN on all
  320 V4 rows (256 clear + 64 neutral/mixed)
- dominant_intent is only argmax(vector) for diagnostics/compatibility
- ranking consumes the full 4D vector
- low vector top1-top2 margin is exposed as mixed_intent instead of forcing
  an interpretation that the content is semantically single-class

Inference is offline. The web runtime consumes cached labels only.
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

CLEAR = ROOT / "data/v4_calibrated/train_clear.jsonl"
NEUTRAL = ROOT / "data/v4_calibrated/train_neutral_mixed.jsonl"
MODEL_NAME = "intfloat/multilingual-e5-base"
METHOD = "pusula-semantic-candidate-v2"


def load_v4(path: Path):
    rows = []
    for row in read_jsonl(path):
        rows.append({
            "id": str(row["id"]),
            "text": str(row["metin"]),
            "auxiliary": row.get("auxiliary_label"),
            "role": str(row["training_role"]),
            "intent_vector": np.asarray(row["gercek_niyet"], dtype=float),
            "clickbait": float(row["clickbait"]),
        })
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

    rows, seen = [], set()
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


def fit_heads(x_clear, clear_rows, x_all, all_rows):
    labels = np.asarray([r["auxiliary"] for r in clear_rows])
    clf = LogisticRegression(
        C=4.0,
        class_weight="balanced",
        max_iter=5000,
        solver="lbfgs",
        random_state=42,
    )
    clf.fit(x_clear, labels)

    y_all = np.asarray(
        [list(r["intent_vector"]) + [r["clickbait"]] for r in all_rows],
        dtype=float,
    )
    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(x_all, y_all)

    train_sim = x_all @ x_all.T
    np.fill_diagonal(train_sim, -1.0)
    nearest_train = np.max(train_sim, axis=1)
    ood_threshold = float(np.quantile(nearest_train, 0.05))
    return clf, knn, ood_threshold


def class_probabilities(clf, x):
    raw = clf.predict_proba(x)
    probs = np.zeros((len(x), 4), dtype=float)
    mapping = {name: i for i, name in enumerate(clf.classes_)}
    for j, name in enumerate(INTENTS):
        probs[:, j] = raw[:, mapping[name]]
    return probs


def screening_score(probs, nearest, ood_threshold):
    sorted_probs = np.sort(probs, axis=1)
    cls_margin = np.clip(sorted_probs[:, -1] - sorted_probs[:, -2], 0.0, 1.0)
    max_prob = np.max(probs, axis=1)
    # Diagnostic support score only; not a calibrated correctness probability.
    proximity = np.clip((nearest - ood_threshold) / max(1e-6, 1.0 - ood_threshold), 0.0, 1.0)
    score = np.clip(0.50 * proximity + 0.30 * max_prob + 0.20 * cls_margin, 0.0, 1.0)
    score = np.where(nearest < ood_threshold, score * 0.50, score)
    return score, cls_margin, max_prob


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--text-key", default="text")
    ap.add_argument("--id-key", default="id")
    ap.add_argument("--model", default=MODEL_NAME)
    ap.add_argument("--mixed-margin", type=float, default=0.15)
    args = ap.parse_args()

    clear = load_v4(CLEAR)
    neutral = load_v4(NEUTRAL)
    all_train = clear + neutral
    input_rows = read_input(Path(args.input), args.text_key, args.id_key)

    if len(clear) != 256 or len(neutral) != 64 or len(all_train) != 320:
        raise SystemExit(f"unexpected V4 sizes clear={len(clear)} neutral={len(neutral)} total={len(all_train)}")
    if Counter(r["auxiliary"] for r in clear) != Counter({k: 64 for k in INTENTS}):
        raise SystemExit("V4 clear set is no longer 64x4 balanced")
    if any(r["auxiliary"] is not None for r in neutral):
        raise SystemExit("neutral/mixed rows must not carry auxiliary hard labels")

    texts = [r["text"] for r in all_train] + [r["text"] for r in input_rows]
    x, revision = encode_texts(texts, args.model, batch_size=16)
    x_train = x[:320]
    x_clear = x_train[:256]
    x_input = x[320:]

    clf, knn, ood_threshold = fit_heads(x_clear, clear, x_train, all_train)
    pred = np.clip(np.asarray(knn.predict(x_input), dtype=float), 0.0, 1.0)
    probs = class_probabilities(clf, x_input)

    dominant_idx = np.argmax(pred[:, :4], axis=1)
    dominant = [INTENTS[int(i)] for i in dominant_idx]
    aux_idx = np.argmax(probs, axis=1)
    auxiliary = [INTENTS[int(i)] for i in aux_idx]

    intent_sorted = np.sort(pred[:, :4], axis=1)
    intent_margin = np.clip(intent_sorted[:, -1] - intent_sorted[:, -2], 0.0, 1.0)
    mixed = intent_margin < float(args.mixed_margin)

    nearest = np.max(x_input @ x_train.T, axis=1)
    confidence, cls_margin, max_prob = screening_score(probs, nearest, ood_threshold)
    ood = nearest < ood_threshold

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, row in enumerate(input_rows):
            payload = {
                "id": row["id"],
                "text": row["text"],
                "intent_vector": [round(float(v), 6) for v in pred[i, :4]],
                "clickbait": round(float(pred[i, 4]), 6),
                "dominant_intent": dominant[i],
                "mixed_intent": bool(mixed[i]),
                "confidence": round(float(confidence[i]), 6),
                "method": METHOD,
                "model": args.model,
                "prompt_version": None,
                "schema_version": "pusula-label-v2",
                "diagnostics": {
                    "intent_top1_top2_margin": round(float(intent_margin[i]), 6),
                    "mixed_margin_threshold": float(args.mixed_margin),
                    "auxiliary_dominant_intent": auxiliary[i],
                    "auxiliary_dominant_probability": round(float(max_prob[i]), 6),
                    "auxiliary_dominant_margin": round(float(cls_margin[i]), 6),
                    "canonical_auxiliary_agree": dominant[i] == auxiliary[i],
                    "nearest_train_cosine": round(float(nearest[i]), 6),
                    "ood": bool(ood[i]),
                    "ood_threshold": round(float(ood_threshold), 6),
                    "encoder_revision": revision,
                    "classifier_training_rows": 256,
                    "vector_training_rows": 320,
                    "clear_training_rows": 256,
                    "neutral_mixed_training_rows": 64,
                },
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    summary = {
        "method": METHOD,
        "model": args.model,
        "encoder_revision": revision,
        "input_count": len(input_rows),
        "dominant_distribution": dict(Counter(dominant)),
        "auxiliary_distribution": dict(Counter(auxiliary)),
        "canonical_auxiliary_agreement_rate": float(np.mean([a == b for a, b in zip(dominant, auxiliary)])),
        "mixed_intent_count": int(np.sum(mixed)),
        "mixed_intent_rate": float(np.mean(mixed)),
        "mean_intent_margin": float(np.mean(intent_margin)),
        "mean_screening_confidence": float(np.mean(confidence)),
        "ood_count": int(np.sum(ood)),
        "ood_rate": float(np.mean(ood)),
        "ood_threshold": ood_threshold,
        "mean_clickbait": float(np.mean(pred[:, 4])),
        "clickbait_ge_0_50": int(np.sum(pred[:, 4] >= 0.50)),
        "output": str(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
