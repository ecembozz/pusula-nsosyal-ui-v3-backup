#!/usr/bin/env python3
"""Build the privacy-safe PUSULA Candidate V5 runtime feed.

This joins the realistic Turkish text corpus with the frozen Candidate V5
semantic outputs. Social metadata required by the ranking demo (author,
engagement, freshness) is deterministic simulation metadata, not observed
NSosyal/X telemetry. The generated rows state that provenance explicitly.

No real usernames, handles or copied posts are introduced by this script.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/v2_realistic/raw_posts.jsonl"
LABELS = ROOT / "experiments/results/candidate_v5_v2_320.jsonl"
OUTPUT = ROOT / "data/runtime/feed_v5.json"
META = ROOT / "data/runtime/feed_v5_meta.json"

# Fictional demo display names. These are pseudonyms, not scraped identities.
AUTHORS = [
    "Deniz A.", "Mert K.", "Selin D.", "Arda T.", "Eylül N.", "Bora S.",
    "İrem Y.", "Kerem C.", "Ada M.", "Emir B.", "Duru G.", "Can O.",
    "Elif R.", "Baran P.", "Lina E.", "Ozan V.", "Sude H.", "Eren L.",
    "Melis U.", "Kaan F.", "Ceren I.", "Atlas Z.", "Nisa Ç.", "Yiğit Ş.",
    "Zeynep A.", "Doruk K.", "Aslı D.", "Umut T.", "Naz N.", "Alp S.",
    "Defne Y.", "Onur C.",
]

TOPIC_LABELS = {
    "egitim_yks": "Eğitim",
    "ekonomi_butce": "Ekonomi & bütçe",
    "gundelik_yasam": "Gündelik yaşam",
    "kampus_is": "Kampüs & iş",
    "kultur_sanat": "Kültür & sanat",
    "oyun_espor": "Oyun & e-spor",
    "sosyal_sohbet": "Sosyal",
    "spor_futbol": "Spor",
    "teknofest_maker": "Teknoloji & maker",
    "teknoloji_ai": "Yapay zekâ & teknoloji",
}


def jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def stable_unit(seed: str, offset: int) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    value = int.from_bytes(digest[offset:offset+4], "big")
    return value / 0xFFFFFFFF


def main():
    raw = jsonl(RAW)
    labels = jsonl(LABELS)
    if len(raw) != 320 or len(labels) != 320:
        raise SystemExit(f"expected 320 raw + 320 labels, got {len(raw)} + {len(labels)}")

    by_id = {str(row["id"]): row for row in labels}
    if len(by_id) != 320:
        raise SystemExit("candidate V5 labels contain duplicate ids")

    output = []
    for row in raw:
        rid = str(row["id"])
        label = by_id.get(rid)
        if label is None:
            raise SystemExit(f"missing Candidate V5 label for {rid}")
        if str(label["text"]) != str(row["text"]):
            raise SystemExit(f"text mismatch for {rid}")

        u_author = stable_unit(rid + ":author", 0)
        author_index = min(len(AUTHORS) - 1, int(u_author * len(AUTHORS)))
        # Deliberately independent from semantic intent. These values only make
        # the ranking demo non-degenerate; they are not claims about real users.
        engagement = round(0.22 + 0.68 * stable_unit(rid + ":engagement", 4), 6)
        freshness = round(0.38 + 0.62 * stable_unit(rid + ":freshness", 8), 6)
        author_id = f"demo_user_{author_index+1:02d}"
        topic = str(row["topic_family"])

        output.append({
            "id": rid,
            "yazar": AUTHORS[author_index],
            "author_id": author_id,
            "metin": row["text"],
            "kategori": topic,
            "kategori_adi": TOPIC_LABELS.get(topic, topic.replace("_", " ").title()),
            "topic_family": topic,
            "style": row.get("style"),
            "tahmin_niyet": label["intent_vector"],
            "clickbait": float(label["clickbait"]),
            "mixed_intent": bool(label.get("mixed_intent", False)),
            "semantic_confidence": label.get("confidence"),
            "semantic_method": label.get("method"),
            "etkilesim_puani": engagement,
            "tazelik": freshness,
            "content_provenance": row.get("provenance", "synthetic_original"),
            "source_basis": row.get("source_basis", "public_topic_ecology_not_user_posts"),
            "author_provenance": "fictional_demo_pseudonym",
            "ranking_metadata_provenance": "deterministic_demo_simulation_not_platform_telemetry",
        })

    ids = [r["id"] for r in output]
    texts = [r["metin"] for r in output]
    if len(set(ids)) != 320 or len(set(texts)) != 320:
        raise SystemExit("runtime feed must retain 320 unique ids/texts")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    click = [float(r["clickbait"]) for r in output]
    meta = {
        "schema_version": "pusula-runtime-feed-v5",
        "record_count": len(output),
        "semantic_architecture": {
            "candidate": "V5",
            "encoder": labels[0].get("model"),
            "intent_head": labels[0].get("diagnostics", {}).get("intent_head"),
            "clickbait_head": labels[0].get("diagnostics", {}).get("clickbait_head"),
            "inference": "offline_cached",
        },
        "text_provenance": "synthetic_original_privacy_safe_not_copied_user_posts",
        "author_provenance": "fictional_demo_pseudonyms",
        "engagement_freshness_provenance": "deterministic_demo_simulation_not_platform_telemetry",
        "topic_distribution": dict(Counter(r["topic_family"] for r in output)),
        "author_count": len(set(r["author_id"] for r in output)),
        "clickbait": {
            "mean": sum(click) / len(click),
            "max": max(click),
            "ge_0_50": sum(v >= 0.50 for v in click),
        },
        "guardrails": [
            "Do not report simulated engagement/freshness as observed NSosyal/X metrics.",
            "Do not report development smoke results as final human-gold accuracy.",
            "Runtime performs no LLM or embedding inference; semantic labels are cached offline.",
        ],
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
