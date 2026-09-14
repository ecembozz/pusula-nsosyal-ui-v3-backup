#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
CLEAR = ROOT / "data/final_holdout/holdout_a_v1.jsonl"
NEUTRAL = ROOT / "data/final_holdout/holdout_neutral_a_v1.jsonl"
OUTPUT = ROOT / "data/final_holdout/audit_v1.json"

# Every source below was used for training, tuning, hard-negative mining, smoke review,
# or model selection. The final holdout must not be a near-copy of any of them.
REFERENCE_FILES = [
    ROOT / "data/v4_calibrated/train_clear.jsonl",
    ROOT / "data/v4_calibrated/train_neutral_mixed.jsonl",
    ROOT / "data/v4_calibrated/hard_negative_neutral_v1.jsonl",
    ROOT / "data/v4_calibrated/clickbait_feed_hardneg_v2.jsonl",
    ROOT / "data/v4_calibrated/clickbait_train_neg_a.jsonl",
    ROOT / "data/v4_calibrated/clickbait_train_neg_b.jsonl",
    ROOT / "data/v4_calibrated/clickbait_train_pos_a.jsonl",
    ROOT / "data/v4_calibrated/clickbait_train_pos_b.jsonl",
    ROOT / "data/dev_labels/v4_semantic_dev_64.jsonl",
    ROOT / "data/dev_labels/v4_contrastive_pairs_48.jsonl",
    ROOT / "data/dev_labels/v4_clickbait_pairs_24.jsonl",
    ROOT / "data/dev_labels/v4_clickbait_stress_32.jsonl",
    ROOT / "data/dev_labels/v4_clickbait_feed_eval_64.jsonl",
    ROOT / "data/gold_eval/candidate_hard_cases.jsonl",
    ROOT / "data/gold_eval/candidate_news_cases.jsonl",
    ROOT / "data/v2_realistic/raw_posts.jsonl",
]

INTENTS = ["ogretici", "eglendirici", "haber", "sosyal"]
FAIL_THRESHOLD = 0.90
REPORT_THRESHOLD = 0.82


def read_jsonl(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).casefold()).strip()


def row_text(row: dict) -> str:
    for key in ("text", "metin"):
        if isinstance(row.get(key), str) and row[key].strip():
            return row[key]
    raise ValueError(f"row has no primary text field: {row.get('id')}")


def extract_reference_texts(value, source: str, row_id: str | None = None):
    found = []
    if isinstance(value, dict):
        current_id = str(value.get("id", row_id or "?"))
        for key, child in value.items():
            key_l = str(key).casefold()
            if isinstance(child, str) and (key_l == "metin" or "text" in key_l):
                if child.strip():
                    found.append({"text": child, "source": source, "id": current_id, "field": key})
            elif isinstance(child, (dict, list)):
                found.extend(extract_reference_texts(child, source, current_id))
    elif isinstance(value, list):
        for child in value:
            found.extend(extract_reference_texts(child, source, row_id))
    return found


def main():
    clear = read_jsonl(CLEAR)
    neutral = read_jsonl(NEUTRAL)
    holdout = clear + neutral

    if len(clear) != 80:
        raise SystemExit(f"expected 80 clear holdout rows, got {len(clear)}")
    if len(neutral) != 16:
        raise SystemExit(f"expected 16 neutral holdout rows, got {len(neutral)}")

    dist = Counter(r.get("auxiliary_label") for r in clear)
    expected = Counter({k: 20 for k in INTENTS})
    if dist != expected:
        raise SystemExit(f"clear holdout distribution mismatch: {dict(dist)}")
    if any(r.get("auxiliary_label") is not None for r in neutral):
        raise SystemExit("neutral holdout must not contain auxiliary hard labels")

    ids = [str(r["id"]) for r in holdout]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate holdout ids")
    holdout_texts = [row_text(r) for r in holdout]
    holdout_norm = [norm(t) for t in holdout_texts]
    if len(holdout_norm) != len(set(holdout_norm)):
        raise SystemExit("exact duplicate text inside holdout")

    refs = []
    for path in REFERENCE_FILES:
        for row in read_jsonl(path):
            refs.extend(extract_reference_texts(row, str(path.relative_to(ROOT))))
    # Dedupe exact reference text so repeated development files do not distort the matrix.
    dedup = {}
    for item in refs:
        n = norm(item["text"])
        if n:
            dedup.setdefault(n, item)
    refs = list(dedup.values())
    ref_norm = [norm(r["text"]) for r in refs]

    exact_leaks = []
    ref_exact = {t: refs[i] for i, t in enumerate(ref_norm)}
    for i, t in enumerate(holdout_norm):
        if t in ref_exact:
            exact_leaks.append({"holdout_id": ids[i], "reference": ref_exact[t]})

    all_text = holdout_norm + ref_norm
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, sublinear_tf=True)
    mat = vec.fit_transform(all_text)
    hmat = mat[: len(holdout)]
    rmat = mat[len(holdout) :]
    cross = cosine_similarity(hmat, rmat)

    high_pairs = []
    max_cross = {"similarity": -1.0}
    for i in range(cross.shape[0]):
        j = int(np.argmax(cross[i]))
        score = float(cross[i, j])
        if score > max_cross["similarity"]:
            max_cross = {
                "similarity": score,
                "holdout_id": ids[i],
                "holdout_text": holdout_texts[i],
                "reference_source": refs[j]["source"],
                "reference_id": refs[j]["id"],
                "reference_field": refs[j]["field"],
                "reference_text": refs[j]["text"],
            }
        if score >= REPORT_THRESHOLD:
            high_pairs.append({
                "similarity": score,
                "holdout_id": ids[i],
                "reference_source": refs[j]["source"],
                "reference_id": refs[j]["id"],
                "reference_text": refs[j]["text"],
            })

    within = cosine_similarity(hmat)
    np.fill_diagonal(within, 0.0)
    within_pairs = []
    max_within = {"similarity": 0.0}
    for i in range(len(holdout)):
        for j in range(i + 1, len(holdout)):
            score = float(within[i, j])
            if score > max_within["similarity"]:
                max_within = {"similarity": score, "a": ids[i], "b": ids[j]}
            if score >= FAIL_THRESHOLD:
                within_pairs.append({"similarity": score, "a": ids[i], "b": ids[j]})

    failures = [p for p in high_pairs if p["similarity"] >= FAIL_THRESHOLD]
    payload = {
        "status": "PASS" if not exact_leaks and not failures and not within_pairs else "FAIL",
        "policy": {
            "fail_similarity_threshold": FAIL_THRESHOLD,
            "report_similarity_threshold": REPORT_THRESHOLD,
            "similarity": "character_wb_tfidf_3_5_cosine",
        },
        "holdout": {
            "clear_n": len(clear),
            "neutral_mixed_n": len(neutral),
            "total_n": len(holdout),
            "clear_distribution": dict(dist),
        },
        "references": {
            "files": [str(p.relative_to(ROOT)) for p in REFERENCE_FILES],
            "unique_text_n": len(refs),
        },
        "exact_leaks": exact_leaks,
        "cross_reference_pairs_ge_0_90": failures,
        "within_holdout_pairs_ge_0_90": within_pairs,
        "max_cross_reference_similarity": max_cross,
        "max_within_holdout_similarity": max_within,
        "reported_pairs_ge_0_82": sorted(high_pairs, key=lambda x: -x["similarity"])[:30],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if payload["status"] != "PASS":
        raise SystemExit("final holdout leakage audit failed")


if __name__ == "__main__":
    main()
