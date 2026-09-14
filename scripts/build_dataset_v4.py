#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "data/v3_realistic"
V4 = ROOT / "data/v4_calibrated"
V3_FILES = [
    V3 / "train_ogretici_v1.jsonl",
    V3 / "train_ogretici_v2.jsonl",
    V3 / "train_eglendirici_v1.jsonl",
    V3 / "train_eglendirici_v2.jsonl",
    V3 / "train_haber_v1.jsonl",
    V3 / "train_haber_v2.jsonl",
    V3 / "train_sosyal_v1.jsonl",
    V3 / "train_sosyal_v2.jsonl",
]
SOCIAL_ADDITIONS = V4 / "social_clear_additions.jsonl"
INTENTS = ["ogretici", "eglendirici", "haber", "sosyal"]

STRONG_SOCIAL = [
    "ne düşünüyorsunuz", "ne dusunuyorsunuz", "sizce", "öneri", "oneri",
    "öneriniz", "oneriniz", "yazın", "yazin", "yazabilir", "var mı", "var mi",
    "katılan", "katilan", "buluş", "bulus", "birlikte", "kimler", "paylaşabilir",
    "paylasabilir", "deneyimi olan", "yardım", "yardim", "fikir", "+1", "grup kuralım",
    "grup kuralim", "haberleş", "haberles", "eşleş", "esles", "selam versin",
]
SOCIAL_RELATIONAL = [
    "teşekkür", "tesekkur", "iyi ki", "ekip", "topluluk", "arkadaş", "arkadas",
    "herkes", "hepimiz", "karşılıklı", "karsilikli", "muhabbet", "destek",
]


def read_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )


def norm_text(text: str):
    return " ".join(str(text).casefold().split())


def social_secondary_score(text: str) -> float:
    t = norm_text(text)
    score = 0.08
    if "?" in text:
        score += 0.18
    if any(cue in t for cue in STRONG_SOCIAL):
        score += 0.24
    if any(cue in t for cue in SOCIAL_RELATIONAL):
        score += 0.10
    # Replies/comments generally imply an interpersonal context, but text semantics
    # still determine whether the score becomes strong.
    return round(min(0.55, score), 2)


def argmax_intent(vec):
    return INTENTS[max(range(4), key=lambda i: float(vec[i]))]


def recalibrate_clear(row):
    out = dict(row)
    vec = [float(x) for x in row["gercek_niyet"]]
    vec[3] = social_secondary_score(row["metin"])
    out["source_id"] = row["id"]
    out["id"] = "v4c_" + row["id"]
    out["gercek_niyet"] = [round(x, 3) for x in vec]
    out["dominant_intent"] = argmax_intent(vec)
    out["auxiliary_label"] = row["dominant_intent"]
    out["training_role"] = "clear_intent"
    out["label_source"] = "assistant_recalibrated_development_v4"
    if out["dominant_intent"] != out["auxiliary_label"]:
        raise ValueError(f"clear row lost primary intent after calibration: {row['id']}")
    return out


def convert_old_social_to_neutral(row):
    old = [float(x) for x in row["gercek_niyet"]]
    # Old V3 social rows frequently represented personal reflection rather than
    # interpersonal intent. Keep them as realistic mixed text, but do not train a
    # hard class label from them. The browsing goal can still match these mixed vectors.
    vec = [
        min(0.55, max(0.08, 0.55 * old[0] + 0.08)),
        min(0.65, max(0.16, 0.55 * old[1] + 0.22)),
        min(0.45, max(0.05, 0.45 * old[2] + 0.06)),
        min(0.55, max(0.12, social_secondary_score(row["metin"]))),
    ]
    out = dict(row)
    out["source_id"] = row["id"]
    out["id"] = "v4n_" + row["id"]
    out["gercek_niyet"] = [round(float(x), 3) for x in vec]
    out["dominant_intent"] = argmax_intent(vec)
    out["auxiliary_label"] = None
    out["training_role"] = "neutral_mixed"
    out["label_source"] = "assistant_recalibrated_development_v4"
    return out


def validate_social_addition(row):
    required = {"id", "metin", "gercek_niyet", "dominant_intent", "auxiliary_label", "training_role"}
    missing = required - set(row)
    if missing:
        raise ValueError(f"social addition missing {sorted(missing)}")
    if row["auxiliary_label"] != "sosyal" or row["training_role"] != "clear_intent":
        raise ValueError(f"invalid social addition role: {row['id']}")
    if argmax_intent(row["gercek_niyet"]) != "sosyal":
        raise ValueError(f"social addition vector is not social-dominant: {row['id']}")


def main():
    v3_rows = []
    for path in V3_FILES:
        v3_rows.extend(read_jsonl(path))
    if len(v3_rows) != 256:
        raise SystemExit(f"expected 256 V3 rows, got {len(v3_rows)}")

    clear = []
    neutral = []
    for row in v3_rows:
        if row["dominant_intent"] == "sosyal":
            neutral.append(convert_old_social_to_neutral(row))
        else:
            clear.append(recalibrate_clear(row))

    additions = read_jsonl(SOCIAL_ADDITIONS)
    if len(additions) != 64:
        raise SystemExit(f"expected 64 clear social additions, got {len(additions)}")
    for row in additions:
        validate_social_addition(row)
    clear.extend(additions)

    if len(clear) != 256 or len(neutral) != 64:
        raise SystemExit(f"unexpected V4 sizes clear={len(clear)} neutral={len(neutral)}")

    dist = Counter(r["auxiliary_label"] for r in clear)
    expected = Counter({k: 64 for k in INTENTS})
    if dist != expected:
        raise SystemExit(f"clear auxiliary balance mismatch: {dist}")

    all_rows = clear + neutral
    ids = [r["id"] for r in all_rows]
    texts = [norm_text(r["metin"]) for r in all_rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate V4 ids")
    if len(texts) != len(set(texts)):
        raise SystemExit("duplicate V4 texts")

    write_jsonl(V4 / "train_clear.jsonl", clear)
    write_jsonl(V4 / "train_neutral_mixed.jsonl", neutral)

    prototypes = {}
    for intent in INTENTS:
        arr = [r["gercek_niyet"] for r in clear if r["auxiliary_label"] == intent]
        prototypes[intent] = [round(sum(float(v[i]) for v in arr) / len(arr), 4) for i in range(4)]

    summary = {
        "schema": "pusula-dataset-v4-calibrated-development",
        "clear_n": len(clear),
        "neutral_mixed_n": len(neutral),
        "total_n": len(all_rows),
        "clear_auxiliary_distribution": dict(dist),
        "clear_class_prototypes": prototypes,
        "social_semantics": "interpersonal_or_community_function_not_generic_personal_post",
        "source_policy": {
            "v3_non_social_rows": "retained_text_recalibrated_social_secondary_axis",
            "v3_social_rows": "retained_text_as_neutral_mixed_no_auxiliary_hard_label",
            "new_social_rows": "64_original_clear_interaction_examples",
        },
    }
    (V4 / "build_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
