#!/usr/bin/env python3
"""Audit near-duplicate text pairs in Dataset V2 using stdlib only."""

from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zçğıöşü0-9\s]", " ", text)
    return " ".join(text.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/v2_realistic/raw_posts.jsonl")
    ap.add_argument("--output", default="/tmp/dataset_similarity_audit.json")
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    rows = load_jsonl(Path(args.input))
    normalized = [(row["id"], row["text"], normalize(row["text"])) for row in rows]
    pairs = []
    for i in range(len(normalized)):
        id_a, text_a, norm_a = normalized[i]
        for j in range(i + 1, len(normalized)):
            id_b, text_b, norm_b = normalized[j]
            # Length prefilter prevents expensive comparisons for clearly
            # different strings without changing the high-similarity tail.
            la, lb = len(norm_a), len(norm_b)
            if max(la, lb) and min(la, lb) / max(la, lb) < 0.65:
                continue
            ratio = SequenceMatcher(None, norm_a, norm_b, autojunk=False).ratio()
            if ratio >= 0.70:
                pairs.append({"a": id_a, "b": id_b, "similarity": round(ratio, 4), "text_a": text_a, "text_b": text_b})

    pairs.sort(key=lambda x: x["similarity"], reverse=True)
    report = {
        "record_count": len(rows),
        "pair_count_ge_0_70": len(pairs),
        "pair_count_ge_0_80": sum(p["similarity"] >= 0.80 for p in pairs),
        "pair_count_ge_0_90": sum(p["similarity"] >= 0.90 for p in pairs),
        "max_similarity": pairs[0]["similarity"] if pairs else 0.0,
        "top_pairs": pairs[: args.top],
        "note": "Audit only. Thresholds are descriptive until corpus quality targets are frozen.",
    }
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
