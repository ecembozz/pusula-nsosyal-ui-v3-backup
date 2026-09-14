from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
from sklearn.neighbors import KNeighborsRegressor

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

from benchmark_supervised_embeddings import encode_texts, read_jsonl
from core.heuristic_labeler import HeuristicLabeler

CLEAR = ROOT / "data/v4_calibrated/train_clear.jsonl"
NEUTRAL = ROOT / "data/v4_calibrated/train_neutral_mixed.jsonl"
HARDNEG = ROOT / "data/v4_calibrated/hard_negative_neutral_v1.jsonl"
PAIRS = ROOT / "data/dev_labels/v4_clickbait_pairs_24.jsonl"


# Development baseline: intentionally simple and inspectable. These phrases were
# chosen from generic clickbait presentation patterns and the development pairs;
# therefore this detector is tuned development code, not final evaluation evidence.
PHRASE_WEIGHTS = {
    "şok": 0.42,
    "inanamayacaks": 0.50,
    "kimsenin söylemediği": 0.55,
    "gerçek ortaya çıktı": 0.48,
    "dikkat": 0.34,
    "herkes yanılıyor": 0.48,
    "asıl sebep": 0.38,
    "yapanlar dikkat": 0.52,
    "bunu görmeden": 0.48,
    "çoğu kişi bunu bilmiyor": 0.52,
    "son şans": 0.52,
    "son fırsat": 0.52,
    "sakın": 0.42,
    "tek bir ayrıntı": 0.34,
    "tek bir değişiklik": 0.34,
    "her şeyi değiştirdi": 0.36,
    "hayatını değiştirecek": 0.55,
    "sadece gerçek": 0.44,
    "reklamlarda göstermedikleri": 0.52,
    "interneti ikiye böldü": 0.46,
    "kaçırırsan": 0.34,
    "çok şey kaybeder": 0.38,
    "şaşıracaks": 0.38,
    "sonuç beklediğim gibi değildi": 0.30,
    "gözden kaçırdığı": 0.30,
    "tamamen değiştirebilir": 0.30,
    "sebebi düşündüğünüz şey değil": 0.38,
    "kritik ayrıntı sonda": 0.40,
    "tahmin etmek zor": 0.22,
    "asıl farkı yaratan": 0.24,
    "sonunda buldum": 0.22,
}


def normalize(text: str) -> str:
    text = text.replace("İ", "i").replace("I", "ı").casefold()
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split())


def presentation_clickbait_score(text: str) -> float:
    norm = normalize(text)
    score = 0.0
    matched = []
    for phrase, weight in PHRASE_WEIGHTS.items():
        if phrase in norm:
            score += weight
            matched.append(phrase)

    # Structural amplification. Capped so punctuation alone cannot make a post clickbait.
    caps = re.findall(r"\b[A-ZÇĞİÖŞÜ]{4,}\b", text)
    score += min(0.30, 0.10 * len(caps))
    score += min(0.20, 0.07 * text.count("!"))
    if "!!!" in text or "???" in text:
        score += 0.08

    # Emoji can amplify an already manipulative headline but must not create one alone.
    if score >= 0.20 and re.search(r"[😱😳👀🔥⏰👇]", text):
        score += 0.08

    return float(min(1.0, score))


def load_train():
    rows = []
    for path in (CLEAR, NEUTRAL, HARDNEG):
        for r in read_jsonl(path):
            rows.append({
                "text": r["metin"],
                "intent": [float(x) for x in r["gercek_niyet"]],
                "clickbait": float(r["clickbait"]),
            })
    return rows


def evaluate_method(name: str, low_scores, high_scores, pairs):
    low = np.asarray(low_scores, dtype=float)
    high = np.asarray(high_scores, dtype=float)
    low_gold = np.asarray([float(p["low_clickbait"]) for p in pairs], dtype=float)
    high_gold = np.asarray([float(p["high_clickbait"]) for p in pairs], dtype=float)
    y_true = np.concatenate([low_gold, high_gold])
    y_pred = np.clip(np.concatenate([low, high]), 0.0, 1.0)
    cls_true = np.asarray([0] * len(pairs) + [1] * len(pairs), dtype=int)
    cls_pred = (y_pred >= 0.50).astype(int)

    records = []
    by_family = defaultdict(list)
    for i, p in enumerate(pairs):
        delta = float(high[i] - low[i])
        record = {
            "id": p["id"],
            "family": p["family"],
            "low": float(low[i]),
            "high": float(high[i]),
            "delta": delta,
            "ordered": bool(delta > 0),
            "margin_0_30": bool(delta >= 0.30),
            "low_false_positive": bool(low[i] >= 0.50),
            "high_captured": bool(high[i] >= 0.50),
        }
        records.append(record)
        by_family[p["family"]].append(record)

    def agg(rows):
        n = len(rows)
        return {
            "n": n,
            "pair_order_accuracy": float(sum(r["ordered"] for r in rows) / n),
            "pair_margin_0_30_rate": float(sum(r["margin_0_30"] for r in rows) / n),
            "mean_delta": float(np.mean([r["delta"] for r in rows])),
            "low_false_positive_rate": float(sum(r["low_false_positive"] for r in rows) / n),
            "high_capture_rate": float(sum(r["high_captured"] for r in rows) / n),
        }

    result = agg(records)
    result.update({
        "balanced_accuracy_at_0_50": float(accuracy_score(cls_true, cls_pred)),
        "f1_at_0_50": float(f1_score(cls_true, cls_pred, zero_division=0)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mean_low_score": float(np.mean(low)),
        "mean_high_score": float(np.mean(high)),
        "by_family": {k: agg(v) for k, v in sorted(by_family.items())},
        "failed_pairs": [r for r in records if not r["ordered"] or not r["high_captured"] or r["low_false_positive"]],
    })
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-base")
    ap.add_argument("--output", default="experiments/results/clickbait_v4.json")
    ap.add_argument("--summary", default="experiments/results/clickbait_v4.md")
    args = ap.parse_args()

    train = load_train()
    pairs = list(read_jsonl(PAIRS))
    if len(train) != 352 or len(pairs) != 24:
        raise SystemExit(f"unexpected sizes train={len(train)} pairs={len(pairs)}")

    texts = [r["text"] for r in train] + [p["low_text"] for p in pairs] + [p["high_text"] for p in pairs]
    x, revision = encode_texts(texts, args.model, batch_size=16)
    xt = x[:352]
    xl = x[352:376]
    xh = x[376:400]

    y = np.asarray([r["intent"] + [r["clickbait"]] for r in train], dtype=float)
    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(xt, y)
    semantic_low = np.clip(np.asarray(knn.predict(xl), dtype=float)[:, 4], 0, 1)
    semantic_high = np.clip(np.asarray(knn.predict(xh), dtype=float)[:, 4], 0, 1)

    old = HeuristicLabeler()
    old_low = np.asarray([float(old.label(p["low_text"]).clickbait) for p in pairs])
    old_high = np.asarray([float(old.label(p["high_text"]).clickbait) for p in pairs])

    rule_low = np.asarray([presentation_clickbait_score(p["low_text"]) for p in pairs])
    rule_high = np.asarray([presentation_clickbait_score(p["high_text"]) for p in pairs])

    methods = {
        "semantic_knn_candidate_v3": evaluate_method("semantic", semantic_low, semantic_high, pairs),
        "upstream_heuristic_v1": evaluate_method("old", old_low, old_high, pairs),
        "presentation_rules_dev_v1": evaluate_method("rules", rule_low, rule_high, pairs),
    }

    ranked = sorted(
        methods.items(),
        key=lambda kv: (
            -kv[1]["pair_order_accuracy"],
            -kv[1]["high_capture_rate"],
            kv[1]["low_false_positive_rate"],
            kv[1]["mae"],
        ),
    )
    recommended = ranked[0][0]

    result = {
        "status": "development_only_clickbait_contrastive_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "pairs_n": len(pairs),
        "semantic_training_rows": len(train),
        "recommended": recommended,
        "selection_rule": "maximize pair ordering and high capture, minimize low false positives and MAE",
        "methods": methods,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Clickbait contrastive benchmark V4",
        "",
        "> Development-only. The expanded presentation rules were tuned with knowledge of these development patterns; no result here is final competition evidence.",
        "",
        "| Method | Pair order | >=0.30 margin | Low false-positive | High capture | Acc@0.50 | F1@0.50 | MAE | Mean low | Mean high |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, r in methods.items():
        lines.append(
            f"| {name} | {r['pair_order_accuracy']:.3f} | {r['pair_margin_0_30_rate']:.3f} | "
            f"{r['low_false_positive_rate']:.3f} | {r['high_capture_rate']:.3f} | "
            f"{r['balanced_accuracy_at_0_50']:.3f} | {r['f1_at_0_50']:.3f} | "
            f"{r['mae']:.3f} | {r['mean_low_score']:.3f} | {r['mean_high_score']:.3f} |"
        )
    lines += ["", f"Development recommendation: `{recommended}`", "", "## Family breakdown", ""]
    for name, r in methods.items():
        lines.append(f"### {name}")
        lines.append("")
        for family, fr in r["by_family"].items():
            lines.append(
                f"- `{family}`: order {fr['pair_order_accuracy']:.3f}, high-capture {fr['high_capture_rate']:.3f}, low-FP {fr['low_false_positive_rate']:.3f}, delta {fr['mean_delta']:.3f}"
            )
        lines.append("")
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
