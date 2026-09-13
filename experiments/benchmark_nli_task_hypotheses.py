#!/usr/bin/env python3
"""Task-aligned NLI benchmark for PUSULA intent labeling.

Hypotheses are derived from the annotation guide, not tuned to individual
examples. This script is only for offline model selection; runtime PUSULA does
not load these transformer models.
"""

from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

from transformers import pipeline

MODEL_ID = os.environ.get("PUSULA_NLI_MODEL", "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli")
DIMS = ("ogretici", "eglendirici", "haber", "sosyal")

HYPOTHESES = {
    "ogretici": "Bu paylaşımın temel amacı okuyucuya bilgi, açıklama, yöntem veya faydalı öneri sunmaktır.",
    "eglendirici": "Bu paylaşımın temel amacı okuyucuyu eğlendirmek, güldürmek veya keyif vermektir.",
    "haber": "Bu paylaşımın temel amacı kamusal ya da güncel bir gelişmeyi, duyuruyu veya sonucu aktarmaktır.",
    "sosyal": "Bu paylaşımın temel amacı kişisel deneyim, duygu veya fikir paylaşmak ya da sohbet ve etkileşim kurmaktır.",
    "clickbait": "Bu paylaşım bilgiyi kasıtlı saklayarak, yanıltıcı abartı veya merak boşluğu kullanarak tıklama isteği yaratmaktadır.",
}


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


def entailment_score(classifier, text: str, hypothesis: str) -> float:
    # The zero-shot pipeline takes candidate labels, not arbitrary completed
    # hypotheses. We use the model tokenizer/model directly so each PUSULA
    # definition is evaluated as an explicit premise-hypothesis NLI pair.
    tokenizer = classifier.tokenizer
    model = classifier.model
    import torch

    encoded = tokenizer(text, hypothesis, return_tensors="pt", truncation=True, max_length=256)
    with torch.inference_mode():
        logits = model(**encoded).logits[0]

    label2id = {str(k).lower(): int(v) for k, v in model.config.label2id.items()}
    entail_idx = None
    for name, idx in label2id.items():
        if "entail" in name:
            entail_idx = idx
            break
    if entail_idx is None:
        # Common MNLI ordering: contradiction, neutral, entailment.
        entail_idx = int(logits.numel() - 1)
    probs = torch.softmax(logits, dim=-1)
    return float(probs[entail_idx].item())


def main():
    cases = {}
    for p in ["data/gold_eval/candidate_hard_cases.jsonl", "data/gold_eval/candidate_news_cases.jsonl"]:
        for row in read_jsonl(p):
            cases[row["id"]] = row["text"]
    gold = read_jsonl("data/gold_eval/draft_labels_annotator_a.jsonl")

    classifier = pipeline("zero-shot-classification", model=MODEL_ID, device=-1)
    model_commit = getattr(getattr(classifier.model, "config", None), "_commit_hash", None)

    per_dim_abs = defaultdict(list)
    click_abs = []
    cosines = []
    gold_dom, pred_dom = [], []
    rows = []

    for item in gold:
        text = cases[item["id"]]
        scores = {key: entailment_score(classifier, text, hyp) for key, hyp in HYPOTHESES.items()}
        pv = tuple(scores[d] for d in DIMS)
        gv = tuple(float(item["intent"][d]) for d in DIMS)
        for d, g, p in zip(DIMS, gv, pv):
            per_dim_abs[d].append(abs(g - p))
        click_abs.append(abs(float(item["clickbait"]) - scores["clickbait"]))
        cosines.append(cosine(gv, pv))
        gd = item["dominant_intent"]
        pd = DIMS[max(range(4), key=lambda i: pv[i])]
        gold_dom.append(gd)
        pred_dom.append(pd)
        rows.append({"id": item["id"], "gold_dominant": gd, "pred_dominant": pd, "gold_vector": list(gv), "pred_vector": list(pv), "clickbait": scores["clickbait"]})

    per_dim_mae = {d: sum(v) / len(v) for d, v in per_dim_abs.items()}
    acc = sum(g == p for g, p in zip(gold_dom, pred_dom)) / len(gold_dom)
    mf1, per_class = macro_f1(gold_dom, pred_dom)
    result = {
        "benchmark_status": "development_set_single_annotator_not_final_gold",
        "model": MODEL_ID,
        "model_commit": model_commit,
        "n": len(gold),
        "hypothesis_source": "data/gold_eval/ANNOTATION_GUIDE.md",
        "hypotheses": HYPOTHESES,
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
    safe_name = MODEL_ID.replace("/", "__")
    Path(f"/tmp/{safe_name}_task_nli.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
