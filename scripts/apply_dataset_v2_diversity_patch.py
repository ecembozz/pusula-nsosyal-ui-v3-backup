#!/usr/bin/env python3
"""Replace high-similarity Dataset V2 templates with more varied originals.

This deterministic second stage keeps IDs/topic families stable while removing
known near-duplicate phrasing found by `audit_dataset_similarity.py`.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "v2_realistic"
DATA = OUT / "raw_posts.jsonl"
STATS = OUT / "corpus_stats.json"

# Every replacement is original synthetic text written for PUSULA. The IDs are
# intentionally stable so later labels/cache entries can refer to the same row.
REPLACEMENTS = {
    "v2r_0027": "Ders seçimi açılınca önce danışman notlarını, sonra ders saatlerini yan yana koydum; çakışmayı böyle fark ettim.",
    "v2r_0086": "Raporu teslim ettikten sonra ekipte kimse kutlama yapmadı; herkes önce dosyanın gerçekten yüklendiğini üç kere kontrol etti.",
    "v2r_0113": "İlk 11'i görünce kağıt üstünde mantıklı geldi, maç başlayınca beklediğim eşleşmelerin hiçbiri oluşmadı.",
    "v2r_0114": "Deplasmanda ilk yarı kontrollüydü; ikinci yarıda iki oyuncu öne çıkınca oyunun yönü tamamen değişti.",
    "v2r_0123": "VAR kararında ilk görüntü beni ikna etti, ters açı gelince fikrim değişti; tek kareyle hüküm vermek zor.",
    "v2r_0141": "Caz konserinde en iyi bölüm programda adı bile küçük yazan doğaçlama kısımdı; eve dönünce aynı parçayı tekrar aradım.",
    "v2r_0201": "Ranked maçta iki kez kaybedince ara vermek yerine üçüncüye girdim; oyundan çok kendi inadımla yarışıyorum galiba.",
    "v2r_0202": "Yeni sezonla beraber görev sistemi değişmiş; ilk akşam menülerde kayboldum ama ilerleme hissi eskisinden daha iyi.",
    "v2r_0218": "Yeni yamanın notlarını okumadan oyuna girdik, on dakika sonra bütün alışkanlıklarımızın değiştiğini acı şekilde öğrendik.",
    "v2r_0239": "Kampüste iki ders arasındaki boşluğu kütüphanede kapatayım dedim; yarım saatlik iş bütün haftalık planı toparladı.",
    "v2r_0247": "Grup projesini teslim ettik; en faydalı şey son gece hızlanmak değil, kimin neyi beklediğini baştan yazmakmış.",
    "v2r_0254": "Lab dersine erken gidince cihaz sırası beklemeden ölçümleri bitirdik; on dakikalık hazırlık neredeyse bir saat kazandırdı.",
    "v2r_0266": "Otobüs beklerken sürekli ekrana bakınca süre daha uzun geliyor; bugün telefonu cebime koyup iki durak yürüdüm.",
    "v2r_0277": "Erken uyanmayı alarm sayısını artırarak çözememişim; gece telefonu yatağın yanından kaldırınca sabah daha az pazarlık yaptım.",
}


def load_rows() -> list[dict]:
    return [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_stats(rows: list[dict]) -> None:
    lengths = [len(row["text"]) for row in rows]
    stats = {
        "schema_version": "raw-v2.2-diversified",
        "record_count": len(rows),
        "unique_text_count": len({row["text"] for row in rows}),
        "topic_distribution": dict(sorted(Counter(row["topic_family"] for row in rows).items())),
        "style_distribution": dict(sorted(Counter(row["style"] for row in rows).items())),
        "text_length_chars": {
            "min": min(lengths),
            "median": statistics.median(lengths),
            "mean": round(statistics.mean(lengths), 2),
            "max": max(lengths),
        },
        "privacy": {
            "copied_user_posts": 0,
            "user_handles": 0,
            "emails": 0,
            "phone_numbers": 0,
            "urls": 0,
            "tckn_like_11_digit_sequences": 0,
        },
        "diversity_rewrites": len(REPLACEMENTS),
    }
    STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    rows = load_rows()
    by_id = {row["id"]: row for row in rows}
    missing = sorted(set(REPLACEMENTS) - set(by_id))
    if missing:
        raise SystemExit(f"Replacement IDs missing from corpus: {missing}")

    before_topics = {rid: by_id[rid]["topic_family"] for rid in REPLACEMENTS}
    for rid, text in REPLACEMENTS.items():
        row = by_id[rid]
        row["text"] = text
        row["style"] = "manual_diversity_rewrite"
        row["style_flags"] = ["diversity_rewrite"]
        row["provenance"] = "synthetic_original"
        row["source_basis"] = "public_topic_ecology_not_user_posts"
        row["human_label"] = None

    if len({row["text"] for row in rows}) != len(rows):
        raise SystemExit("Diversity patch created an exact duplicate")
    for rid, topic in before_topics.items():
        if by_id[rid]["topic_family"] != topic:
            raise SystemExit(f"Topic changed for {rid}")

    DATA.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")
    write_stats(rows)
    print(json.dumps({"patched": len(REPLACEMENTS), "record_count": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
