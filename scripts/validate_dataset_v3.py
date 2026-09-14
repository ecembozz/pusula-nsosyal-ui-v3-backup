from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
INTENTS = ["ogretici", "eglendirici", "haber", "sosyal"]
FILES = [
    ROOT / "data/v3_realistic/train_ogretici_v1.jsonl",
    ROOT / "data/v3_realistic/train_eglendirici_v1.jsonl",
    ROOT / "data/v3_realistic/train_haber_v1.jsonl",
    ROOT / "data/v3_realistic/train_sosyal_v1.jsonl",
    ROOT / "data/v3_realistic/train_ogretici_v2.jsonl",
    ROOT / "data/v3_realistic/train_eglendirici_v2.jsonl",
    ROOT / "data/v3_realistic/train_haber_v2.jsonl",
    ROOT / "data/v3_realistic/train_sosyal_v2.jsonl",
]


def read_rows(path: Path):
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception as exc:
            raise ValueError(f"{path}:{n}: invalid JSON: {exc}") from exc
    return out


def validate_row(row):
    required = {
        "id", "metin", "gercek_niyet", "dominant_intent", "clickbait",
        "style_bucket", "content_type", "topic_family", "difficulty",
        "label_source", "provenance",
    }
    missing = required - set(row)
    if missing:
        raise ValueError(f"{row.get('id')}: missing {sorted(missing)}")
    vec = row["gercek_niyet"]
    if not isinstance(vec, list) or len(vec) != 4:
        raise ValueError(f"{row['id']}: gercek_niyet must be length 4")
    vals = [float(x) for x in vec]
    if any(x < 0 or x > 1 for x in vals):
        raise ValueError(f"{row['id']}: intent score outside [0,1]")
    cb = float(row["clickbait"])
    if cb < 0 or cb > 1:
        raise ValueError(f"{row['id']}: clickbait outside [0,1]")
    if row["dominant_intent"] not in INTENTS:
        raise ValueError(f"{row['id']}: unknown dominant_intent")
    expected = INTENTS[int(np.argmax(vals))]
    if expected != row["dominant_intent"]:
        raise ValueError(
            f"{row['id']}: dominant_intent={row['dominant_intent']} but vector argmax={expected}"
        )
    if row["label_source"] != "assistant_authored_development":
        raise ValueError(f"{row['id']}: unexpected label_source")
    if row["provenance"] != "synthetic_original_not_copied_user_post":
        raise ValueError(f"{row['id']}: unexpected provenance")


def near_duplicate_report(rows, threshold: float):
    texts = [r["metin"] for r in rows]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1).fit_transform(texts)
    sim = cosine_similarity(vec)
    np.fill_diagonal(sim, 0.0)
    pairs = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if sim[i, j] >= threshold:
                pairs.append(
                    {
                        "a": rows[i]["id"],
                        "b": rows[j]["id"],
                        "similarity": float(sim[i, j]),
                    }
                )
    max_idx = np.unravel_index(np.argmax(sim), sim.shape)
    return {
        "threshold": threshold,
        "pair_count": len(pairs),
        "pairs": sorted(pairs, key=lambda x: -x["similarity"]),
        "max_similarity": float(sim[max_idx]),
        "max_pair": [rows[max_idx[0]]["id"], rows[max_idx[1]]["id"]],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--near-duplicate-threshold", type=float, default=0.90)
    ap.add_argument("--output", default="experiments/results/dataset_v3_audit.json")
    args = ap.parse_args()

    rows = []
    for path in FILES:
        part = read_rows(path)
        if len(part) != 32:
            raise SystemExit(f"{path}: expected 32 rows, got {len(part)}")
        rows.extend(part)

    for row in rows:
        validate_row(row)

    ids = [r["id"] for r in rows]
    texts = [r["metin"].strip().casefold() for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate ids found")
    if len(texts) != len(set(texts)):
        raise SystemExit("exact duplicate texts found")

    dominant = Counter(r["dominant_intent"] for r in rows)
    expected = {k: 64 for k in INTENTS}
    if dict(dominant) != expected:
        raise SystemExit(f"dominant balance mismatch: {dominant}")

    clickbait_positive = Counter(
        r["dominant_intent"] for r in rows if float(r["clickbait"]) >= 0.75
    )
    if sum(clickbait_positive.values()) < 16:
        raise SystemExit("need at least 16 explicit clickbait-positive examples")
    if any(clickbait_positive.get(k, 0) < 4 for k in INTENTS):
        raise SystemExit("need at least four clickbait positives per dominant intent")

    styles = Counter(r["style_bucket"] for r in rows)
    content_types = Counter(r["content_type"] for r in rows)
    topics = Counter(r["topic_family"] for r in rows)
    difficulties = Counter(r["difficulty"] for r in rows)
    near = near_duplicate_report(rows, args.near_duplicate_threshold)

    result = {
        "status": "development_training_not_gold",
        "n": len(rows),
        "dominant_distribution": dict(dominant),
        "clickbait_positive_n": int(sum(clickbait_positive.values())),
        "clickbait_positive_by_intent": dict(clickbait_positive),
        "style_bucket_count": len(styles),
        "style_distribution": dict(styles),
        "content_type_count": len(content_types),
        "content_type_distribution": dict(content_types),
        "topic_family_count": len(topics),
        "topic_distribution": dict(topics),
        "difficulty_distribution": dict(difficulties),
        "near_duplicate_audit": near,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if near["pair_count"]:
        raise SystemExit(
            f"near-duplicate audit failed: {near['pair_count']} pairs >= {args.near_duplicate_threshold}"
        )


if __name__ == "__main__":
    main()
