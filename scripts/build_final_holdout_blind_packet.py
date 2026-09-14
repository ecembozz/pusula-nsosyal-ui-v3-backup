#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEAR = ROOT / "data/final_holdout/holdout_a_v1.jsonl"
NEUTRAL = ROOT / "data/final_holdout/holdout_neutral_a_v1.jsonl"
OUT_JSONL = ROOT / "data/final_holdout/annotator_b_packet_v1.jsonl"
OUT_CSV = ROOT / "data/final_holdout/annotator_b_packet_v1.csv"
OUT_KEY = ROOT / "data/final_holdout/annotator_b_key_v1.json"
SEED = 20260914


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    source = [("clear", r) for r in read_jsonl(CLEAR)] + [("neutral_mixed", r) for r in read_jsonl(NEUTRAL)]
    if len(source) != 96:
        raise SystemExit(f"expected 96 holdout rows, got {len(source)}")

    rng = random.Random(SEED)
    rng.shuffle(source)

    packet = []
    key = []
    for idx, (subset, row) in enumerate(source, start=1):
        eval_id = f"eval_{idx:03d}"
        packet.append({
            "eval_id": eval_id,
            "text": row["text"],
            "intent": {
                "ogretici": None,
                "eglendirici": None,
                "haber": None,
                "sosyal": None,
            },
            "clickbait": None,
            "dominant_intent": None,
            "neutral_mixed": None,
            "annotation_confidence": None,
            "notes": "",
            "annotation_status": "pending_blind_annotator_b",
        })
        key.append({"eval_id": eval_id, "source_id": row["id"], "source_subset": subset})

    OUT_JSONL.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in packet),
        encoding="utf-8",
    )

    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "eval_id", "text", "ogretici", "eglendirici", "haber", "sosyal",
                "clickbait", "dominant_intent", "neutral_mixed", "annotation_confidence", "notes",
            ],
        )
        writer.writeheader()
        for row in packet:
            writer.writerow({
                "eval_id": row["eval_id"],
                "text": row["text"],
                "ogretici": "",
                "eglendirici": "",
                "haber": "",
                "sosyal": "",
                "clickbait": "",
                "dominant_intent": "",
                "neutral_mixed": "",
                "annotation_confidence": "",
                "notes": "",
            })

    OUT_KEY.write_text(
        json.dumps(
            {
                "status": "internal_mapping_do_not_share_with_blind_annotator",
                "shuffle_seed": SEED,
                "rows": key,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(f"wrote {len(packet)} blinded rows; source labels/style metadata are absent from packet")


if __name__ == "__main__":
    main()
