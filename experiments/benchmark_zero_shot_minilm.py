#!/usr/bin/env python3
"""Pilot semantic benchmark using multilingual MiniLM XNLI zero-shot classification.

This is an offline experiment, not a runtime dependency. The goal is to test
whether a compact semantic model materially outperforms the V1 keyword
heuristic on the same draft hard evaluation set.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from transformers import pipeline

MODEL_ID = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"
DIMS = ("ogretici", "eglendirici", "haber", "sosyal")
LABEL_TEXT = {
    "ogretici": "öğretici ve bilgilendirici içerik",
    "eglendirici": "eğlendirici, mizahi veya keyif verici içerik",
    "haber": "haber, duyuru veya güncel gelişme",
    "sosyal": "kişisel, sosyal veya sohbet odaklı paylaşım",
    "clickbait": "clickbait, yanıltıcı veya merak boşluğu oluşturan içerik",
}
HYPOTHESIS_TEMPLATE = "Bu gönderi {} içeriyor."


def read_jsonl(path: str):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def macro_f1(gold, pred):
    vals = []
    per_class = {}
    for label in DIMS:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(g == label for g in gold)}
        vals.append(f1)
    return sum(vals) / len(vals), per_class


def main():
    cases = {}
    for p in ["data/gold_eval/candidate_hard_cases.jsonl", "data/gold_eval/candidate_news_cases.jsonl"]:
        for row in read_jsonl(p):
            cases[row["id"]] = row["text"]
    gold = read_jsonl("data/gold_eval/draft_labels_annotator_a.jsonl")

    classifier = pipeline("zero-shot-classification", model=MODEL_ID, device=-1)
    model_commit = getattr(getattr(classifier.model, "config", None), "_commit_hash", None)

    candidate_labels = [LABEL_TEXT[d] for d in DIMS] + [LABEL_TEXT["clickbait"]]
    reverse = {v: k for k, v in LABEL_TEXT.items()}

    per_dim_abs = defaultdict(list)
    click_abs = []
    cosines = []
    gold_dom, pred_dom = [], []
    rows = []

    for item in gold:
        text = cases[item["id"]]
        out = classifier(
            text,
            candidate_labels=candidate_labels,
            multi_label=True,
            hypothesis_template=HYPOTHESIS_TEMPLATE,
        )
        score_by_key = {reverse[label]: float(score) for label, score in zip(out["labels"], out["scores"])}
        pv = tuple(score_by_key[d] for d in DIMS)
        gv = tuple(float(item["intent"][d]) for d in DIMS)
        for d, g, p in zip(DIMS, gv, pv):
            per_dim_abs[d].append(abs(g - p))
        click_abs.append(abs(float(item["clickbait"]) - score_by_key["clickbait"]))
        cosines.append(cosine(gv, pv))
        gd = item["dominant_intent"]
        pd = DIMS[max(range(4), key=lambda i: pv[i])]
        gold_dom.append(gd)
        pred_dom.append(pd)
        rows.append({"id": item["id"], "gold_dominant": gd, "pred_dominant": pd, "gold_vector": list(gv), "pred_vector": list(pv)})

    per_dim_mae = {d: sum(v) / len(v) for d, v in per_dim_abs.items()}
    acc = sum(g == p for g, p in zip(gold_dom, pred_dom)) / len(gold_dom)
    mf1, per_class = macro_f1(gold_dom, pred_dom)
    result = {
        "benchmark_status": "pilot_against_draft_single_annotator_not_final_gold",
        "model": MODEL_ID,
        "model_commit": model_commit,
        "n": len(gold),
        "hypothesis_template": HYPOTHESIS_TEMPLATE,
        "label_text": LABEL_TEXT,
        "gold_distribution": dict(Counter(gold_dom)),
        "pred_distribution": dict(Counter(pred_dom)),
        "dominant_accuracy": acc,
        "macro_f1": mf1,
        "intent_mae": sum(per_dim_mae.values()) / len(DIMS),
        "intent_mae_by_dimension": per_dim_mae,
        "mean_cosine_similarity": sum(cosines) / len(cosines),
        "clickbait_mae": sum(click_abs) / len(click_abs),
        "per_class": per_class,
        "rows": rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    Path("/tmp/minilm_zero_shot_draft48.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
