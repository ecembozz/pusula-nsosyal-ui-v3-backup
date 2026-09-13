#!/usr/bin/env python3
"""Validate semantic predictions and build a deterministic PUSULA cache.

Input is provider-independent JSONL. Each row must contain `id`, `text` and
semantic scores compatible with `LabelResult`. This script never calls a model;
it separates expensive/offline inference from cheap/runtime consumption.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.labeling import LabelResult, text_fingerprint


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Provider output JSONL")
    ap.add_argument("--output", default="data/processed/semantic_labels.json")
    ap.add_argument("--rejects", default="data/processed/semantic_rejects.jsonl")
    ap.add_argument("--minimum-confidence", type=float, default=0.0)
    args = ap.parse_args()

    cache = {}
    rejects = []
    seen_ids = set()

    for row_number, row in enumerate(load_jsonl(Path(args.input)), start=1):
        try:
            record_id = str(row["id"])
            text = str(row["text"])
            if not record_id or not text.strip():
                raise ValueError("empty id/text")
            if record_id in seen_ids:
                raise ValueError(f"duplicate id: {record_id}")
            seen_ids.add(record_id)

            label = LabelResult.from_mapping(row)
            if label.confidence is not None and label.confidence < args.minimum_confidence:
                raise ValueError(f"confidence below threshold: {label.confidence}")

            fp = text_fingerprint(text)
            cache[fp] = {
                "id": record_id,
                "text_fingerprint": fp,
                **label.to_dict(),
            }
        except Exception as exc:
            rejects.append({"row": row_number, "id": row.get("id"), "error": str(exc)})

    payload = {
        "schema_version": "pusula-semantic-cache-v1",
        "record_count": len(cache),
        "reject_count": len(rejects),
        "minimum_confidence": args.minimum_confidence,
        "labels_by_text_fingerprint": dict(sorted(cache.items())),
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    reject_path = Path(args.rejects)
    reject_path.parent.mkdir(parents=True, exist_ok=True)
    reject_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rejects), encoding="utf-8")

    print(json.dumps({"accepted": len(cache), "rejected": len(rejects), "output": str(output)}, ensure_ascii=False))
    if rejects:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
