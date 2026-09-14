#!/usr/bin/env python3
"""Offline PUSULA Semantic Candidate V4 batch labeler.

Candidate V4 freezes the development architecture into two separate heads over
one multilingual-e5-base embedding pass:

- intent vector: semantic k-NN over 352 V4 intent rows
  (256 clear + 64 neutral/mixed + 32 targeted hard negatives)
- auxiliary dominant classifier: logistic regression over the 256 clear rows;
  this remains diagnostics-only and does not drive ranking
- clickbait: dedicated logistic classifier over 128 balanced presentation
  examples (64 manipulative + 64 clean/hard-negative)

The web runtime does not run E5 or either head. It consumes the cached output.
Development benchmarks used to choose these heads are not final competition
evaluation evidence.
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
HARDNEG = ROOT / "data/v4_calibrated/hard_negative_neutral_v1.jsonl"
CLICKBAIT_FILES = [
    ROOT / "data/v4_calibrated/clickbait_train_pos_a.jsonl",
    ROOT / "data/v4_calibrated/clickbait_train_pos_b.jsonl",
    ROOT / "data/v4_calibrated/clickbait_train_neg_a.jsonl",
    ROOT / "data/v4_calibrated/clickbait_train_neg_b.jsonl",
]
MODEL_NAME = "intfloat/multilingual-e5-base"
METHOD = "pusula-semantic-candidate-v4"


def load_intent_rows(path: Path):
    rows = []
    for r in read_jsonl(path):
        rows.append(
            {
                "id": str(r["id"]),
                "text": str(r["metin"]),
                "auxiliary": r.get("auxiliary_label"),
                "role": str(r["training_role"]),
                "intent_vector": np.asarray(r["gercek_niyet"], dtype=float),
            }
        )
    return rows


def load_clickbait_rows():
    rows = []
    for path in CLICKBAIT_FILES:
        for r in read_jsonl(path):
            rows.append(
                {
                    "id": str(r["id"]),
                    "text": str(r["text"]),
                    "label": int(r["label"]),
                    "target": float(r["clickbait"]),
                }
            )
    return rows


def read_input(path: Path, text_key: str, id_key: str):
    if path.suffix.lower() == ".jsonl":
        raw = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    elif path.suffix.lower() == ".json":
        parsed = json.loads(path.read_text(encoding="utf-8"))
        raw = (parsed.get("posts") or parsed.get("items") or parsed.get("data")) if isinstance(parsed, dict) else parsed
    else:
        raise ValueError("input must be .jsonl or .json")
    if not isinstance(raw, list):
        raise ValueError("input must resolve to a list")

    rows, seen = [], set()
    for i, r in enumerate(raw, 1):
        if not isinstance(r, dict):
            raise ValueError(f"row {i}: expected object")
        rid = str(r.get(id_key, i))
        text = str(r.get(text_key, "")).strip()
        if not text:
            raise ValueError(f"row {i}: empty {text_key}")
        if rid in seen:
            raise ValueError(f"duplicate id: {rid}")
        seen.add(rid)
        rows.append({"id": rid, "text": text})
    return rows


def class_probs(clf, x):
    raw = clf.predict_proba(x)
    out = np.zeros((len(x), 4), dtype=float)
    cmap = {c: i for i, c in enumerate(clf.classes_)}
    for j, name in enumerate(INTENTS):
        out[:, j] = raw[:, cmap[name]]
    return out


def screening_score(probs, nearest, ood_threshold):
    ordered = np.sort(probs, axis=1)
    cls_margin = np.clip(ordered[:, -1] - ordered[:, -2], 0, 1)
    max_prob = np.max(probs, axis=1)
    proximity = np.clip((nearest - ood_threshold) / max(1e-6, 1.0 - ood_threshold), 0, 1)
    # Diagnostic support score only; not a calibrated probability of correctness.
    score = np.clip(0.50 * proximity + 0.30 * max_prob + 0.20 * cls_margin, 0, 1)
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

    clear = load_intent_rows(CLEAR)
    neutral = load_intent_rows(NEUTRAL)
    hardneg = load_intent_rows(HARDNEG)
    intent_train = clear + neutral + hardneg
    click_train = load_clickbait_rows()
    input_rows = read_input(Path(args.input), args.text_key, args.id_key)

    if len(clear) != 256 or len(neutral) != 64 or len(hardneg) != 32 or len(intent_train) != 352:
        raise SystemExit(
            f"unexpected intent sizes clear={len(clear)} neutral={len(neutral)} hardneg={len(hardneg)} total={len(intent_train)}"
        )
    if Counter(r["auxiliary"] for r in clear) != Counter({k: 64 for k in INTENTS}):
        raise SystemExit("clear set is no longer 64x4 balanced")
    if any(r["auxiliary"] is not None for r in neutral + hardneg):
        raise SystemExit("neutral/hard-negative rows must not carry auxiliary hard labels")
    if len(click_train) != 128 or Counter(r["label"] for r in click_train) != Counter({0: 64, 1: 64}):
        raise SystemExit("clickbait training set must be exactly 128 balanced rows")

    texts = [r["text"] for r in intent_train] + [r["text"] for r in click_train] + [r["text"] for r in input_rows]
    x, revision = encode_texts(texts, args.model, batch_size=16)
    x_intent = x[:352]
    x_clear = x_intent[:256]
    x_click = x[352:480]
    x_input = x[480:]

    # Diagnostics-only dominant-intent classifier.
    aux_labels = np.asarray([r["auxiliary"] for r in clear])
    aux_clf = LogisticRegression(
        C=4.0,
        class_weight="balanced",
        max_iter=5000,
        solver="lbfgs",
        random_state=42,
    )
    aux_clf.fit(x_clear, aux_labels)
    aux_probs = class_probs(aux_clf, x_input)

    # Canonical 4D vector head. Clickbait is deliberately excluded from this target.
    y_intent = np.asarray([r["intent_vector"] for r in intent_train], dtype=float)
    intent_knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    intent_knn.fit(x_intent, y_intent)
    pred_intent = np.clip(np.asarray(intent_knn.predict(x_input), dtype=float), 0.0, 1.0)

    # Dedicated clickbait presentation head. Its probability is used as the
    # separate quality signal by PUSULA ranking (quality = 1 - clickbait).
    click_y = np.asarray([r["label"] for r in click_train], dtype=int)
    click_clf = LogisticRegression(
        C=3.0,
        class_weight="balanced",
        max_iter=5000,
        solver="liblinear",
        random_state=42,
    )
    click_clf.fit(x_click, click_y)
    click_prob = np.clip(click_clf.predict_proba(x_input)[:, 1], 0.0, 1.0)

    train_sim = x_intent @ x_intent.T
    np.fill_diagonal(train_sim, -1.0)
    ood_threshold = float(np.quantile(np.max(train_sim, axis=1), 0.05))
    nearest = np.max(x_input @ x_intent.T, axis=1)
    confidence, cls_margin, max_prob = screening_score(aux_probs, nearest, ood_threshold)
    ood = nearest < ood_threshold

    dominant_idx = np.argmax(pred_intent, axis=1)
    dominant = [INTENTS[int(i)] for i in dominant_idx]
    aux_idx = np.argmax(aux_probs, axis=1)
    auxiliary = [INTENTS[int(i)] for i in aux_idx]
    ordered = np.sort(pred_intent, axis=1)
    intent_margin = np.clip(ordered[:, -1] - ordered[:, -2], 0, 1)
    mixed = intent_margin < float(args.mixed_margin)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, row in enumerate(input_rows):
            payload = {
                "id": row["id"],
                "text": row["text"],
                "intent_vector": [round(float(v), 6) for v in pred_intent[i]],
                "clickbait": round(float(click_prob[i]), 6),
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
                    "intent_head": "knn_k7_cosine_distance_352",
                    "clickbait_head": "e5_logistic_balanced_128",
                    "classifier_training_rows": 256,
                    "vector_training_rows": 352,
                    "clickbait_training_rows": 128,
                    "clear_training_rows": 256,
                    "neutral_mixed_training_rows": 64,
                    "hard_negative_training_rows": 32,
                },
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    summary = {
        "method": METHOD,
        "model": args.model,
        "encoder_revision": revision,
        "input_count": len(input_rows),
        "intent_head": "knn_k7_cosine_distance_352",
        "clickbait_head": "e5_logistic_balanced_128",
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
        "mean_clickbait_probability": float(np.mean(click_prob)),
        "clickbait_probability_ge_0_50": int(np.sum(click_prob >= 0.50)),
        "output": str(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
