#!/usr/bin/env python3
"""Build a blind annotation packet without draft-A labels or challenge metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CASE_FILES = [
    Path("data/gold_eval/candidate_hard_cases.jsonl"),
    Path("data/gold_eval/candidate_news_cases.jsonl"),
]


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="data/gold_eval/annotator_b_packet.jsonl")
    args = ap.parse_args()

    rows = []
    for path in CASE_FILES:
        for source in read_jsonl(path):
            rows.append({
                "id": source["id"],
                "text": source["text"],
                "intent": {
                    "ogretici": None,
                    "eglendirici": None,
                    "haber": None,
                    "sosyal": None,
                },
                "clickbait": None,
                "dominant_intent": None,
                "annotation_confidence": None,
                "notes": "",
                "annotation_status": "pending_blind_annotator_b",
            })

    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate IDs in annotation packet")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(f"wrote {len(rows)} blind cases to {out}")


if __name__ == "__main__":
    main()
