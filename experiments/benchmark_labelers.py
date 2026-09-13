#!/usr/bin/env python3
"""Benchmark PUSULA labelers against draft/final gold JSONL files.

The script intentionally uses only the Python stdlib so CI remains lightweight.
It can be extended with semantic/hybrid predictions later without changing the
metric definitions.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.heuristic_labeler import HeuristicLabeler

DIMS = ("ogretici", "eglendirici", "haber", "sosyal")


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def dominant(vector):
    return DIMS[max(range(4), key=lambda i: vector[i])]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def macro_f1(gold, pred):
    f1s = []
    details = {}
    for label in DIMS:
        tp = sum(1 for g, p in zip(gold, pred) if g == label and p == label)
        fp = sum(1 for g, p in zip(gold, pred) if g != label and p == label)
        fn = sum(1 for g, p in zip(gold, pred) if g == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        details[label] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(g == label for g in gold)}
        f1s.append(f1)
    return sum(f1s) / len(f1s), details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default="data/gold_eval/draft_labels_annotator_a.jsonl")
    ap.add_argument("--cases", nargs="+", default=[
        "data/gold_eval/candidate_hard_cases.jsonl",
        "data/gold_eval/candidate_news_cases.jsonl",
    ])
    ap.add_argument("--json-out")
    args = ap.parse_args()

    case_map = {}
    for path in args.cases:
        for row in read_jsonl(Path(path)):
            case_map[row["id"]] = row["text"]

    gold_rows = read_jsonl(Path(args.gold))
    missing = [row["id"] for row in gold_rows if row["id"] not in case_map]
    if missing:
        raise SystemExit(f"Missing case text for IDs: {missing}")

    labeler = HeuristicLabeler()
    per_dim_abs = defaultdict(list)
    cosine_scores = []
    clickbait_abs = []
    gold_dom = []
    pred_dom = []
    rows = []

    for gold in gold_rows:
        pred = labeler.label(case_map[gold["id"]])
        gv = tuple(float(gold["intent"][d]) for d in DIMS)
        pv = pred.intent_vector
        for dim, g, p in zip(DIMS, gv, pv):
            per_dim_abs[dim].append(abs(g - p))
        cosine_scores.append(cosine(gv, pv))
        clickbait_abs.append(abs(float(gold["clickbait"]) - pred.clickbait))
        gd = gold["dominant_intent"]
        pd = pred.dominant_intent
        gold_dom.append(gd)
        pred_dom.append(pd)
        rows.append({
            "id": gold["id"],
            "gold_dominant": gd,
            "pred_dominant": pd,
            "gold_vector": list(gv),
            "pred_vector": list(pv),
        })

    acc = sum(g == p for g, p in zip(gold_dom, pred_dom)) / len(gold_dom)
    mf1, per_class = macro_f1(gold_dom, pred_dom)
    per_dim_mae = {d: sum(v) / len(v) for d, v in per_dim_abs.items()}
    overall_mae = sum(per_dim_mae.values()) / len(DIMS)

    confusion = {g: Counter() for g in DIMS}
    for g, p in zip(gold_dom, pred_dom):
        confusion[g][p] += 1

    result = {
        "benchmark_status": "draft_single_annotator_not_final_gold",
        "n": len(gold_rows),
        "labeler": labeler.name,
        "gold_distribution": dict(Counter(gold_dom)),
        "pred_distribution": dict(Counter(pred_dom)),
        "dominant_accuracy": acc,
        "macro_f1": mf1,
        "intent_mae": overall_mae,
        "intent_mae_by_dimension": per_dim_mae,
        "mean_cosine_similarity": sum(cosine_scores) / len(cosine_scores),
        "clickbait_mae": sum(clickbait_abs) / len(clickbait_abs),
        "per_class": per_class,
        "confusion": {g: dict(confusion[g]) for g in DIMS},
        "rows": rows,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
