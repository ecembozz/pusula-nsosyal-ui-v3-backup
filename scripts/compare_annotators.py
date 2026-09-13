#!/usr/bin/env python3
"""Compare two independent PUSULA annotation JSONL files.

Outputs agreement statistics and a compact adjudication queue. This script does
not decide which annotator is correct; it only identifies disagreements.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

DIMS = ("ogretici", "eglendirici", "haber", "sosyal")


def read_jsonl(path: Path):
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[row["id"]] = row
    return rows


def pearson(xs, ys):
    if len(xs) < 2:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return sum(x*y for x, y in zip(dx, dy)) / den if den else 0.0


def cohen_kappa(a, b, labels):
    n = len(a)
    if not n:
        return 0.0
    po = sum(x == y for x, y in zip(a, b)) / n
    ca = Counter(a)
    cb = Counter(b)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--cases", nargs="+", default=[
        "data/gold_eval/candidate_hard_cases.jsonl",
        "data/gold_eval/candidate_news_cases.jsonl",
    ])
    ap.add_argument("--report", default="/tmp/annotation_agreement.json")
    ap.add_argument("--queue", default="/tmp/adjudication_queue.jsonl")
    ap.add_argument("--dimension-threshold", type=float, default=0.30)
    args = ap.parse_args()

    ann_a = read_jsonl(Path(args.a))
    ann_b = read_jsonl(Path(args.b))
    common = sorted(set(ann_a) & set(ann_b))
    if not common:
        raise SystemExit("No common annotation IDs")

    texts = {}
    for path in args.cases:
        texts.update({r["id"]: r["text"] for r in read_jsonl(Path(path)).values()})

    dim_stats = {}
    per_item = []
    dom_a, dom_b = [], []
    click_diffs = []

    for dim in DIMS:
        xa = [float(ann_a[i]["intent"][dim]) for i in common]
        xb = [float(ann_b[i]["intent"][dim]) for i in common]
        diffs = [abs(x-y) for x, y in zip(xa, xb)]
        dim_stats[dim] = {
            "mae_between_annotators": sum(diffs) / len(diffs),
            "pearson_r": pearson(xa, xb),
            "within_0_20_rate": sum(d <= 0.20 for d in diffs) / len(diffs),
            "within_0_30_rate": sum(d <= 0.30 for d in diffs) / len(diffs),
        }

    for i in common:
        a = ann_a[i]
        b = ann_b[i]
        da = a["dominant_intent"]
        db = b["dominant_intent"]
        dom_a.append(da)
        dom_b.append(db)
        cba = float(a.get("clickbait", 0.0))
        cbb = float(b.get("clickbait", 0.0))
        click_diffs.append(abs(cba-cbb))
        dim_diff = {d: abs(float(a["intent"][d]) - float(b["intent"][d])) for d in DIMS}
        needs = da != db or max(dim_diff.values()) > args.dimension_threshold or abs(cba-cbb) > args.dimension_threshold
        per_item.append({
            "id": i,
            "text": texts.get(i, ""),
            "dominant_a": da,
            "dominant_b": db,
            "dimension_abs_diff": dim_diff,
            "clickbait_abs_diff": abs(cba-cbb),
            "needs_adjudication": needs,
        })

    report = {
        "n_common": len(common),
        "dominant_exact_agreement": sum(x == y for x, y in zip(dom_a, dom_b)) / len(common),
        "dominant_cohen_kappa": cohen_kappa(dom_a, dom_b, DIMS),
        "dimension_agreement": dim_stats,
        "clickbait_mae_between_annotators": sum(click_diffs) / len(click_diffs),
        "adjudication_count": sum(r["needs_adjudication"] for r in per_item),
        "adjudication_threshold": args.dimension_threshold,
    }

    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with Path(args.queue).open("w", encoding="utf-8") as fh:
        for row in per_item:
            if row["needs_adjudication"]:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
