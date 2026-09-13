from __future__ import annotations

import argparse
import json
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, ndcg_score

from benchmark_encoder_sweep import encode
from benchmark_intent_balanced_corpus import load_balanced
from benchmark_supervised_embeddings import INTENTS

ROOT = Path(__file__).resolve().parents[1]
MODEL = "intfloat/multilingual-e5-base"
SOURCE_COMMIT = "78cdd15dd14adbed7e722a13b99171d84956f665"
SOURCE_PATH = "kod/veri/etiketli_havuz.json"
SOURCE_URL = f"https://raw.githubusercontent.com/asimonmsz-design/pusula/{SOURCE_COMMIT}/{SOURCE_PATH}"

PROFILES = {
    "pure_ogretici": [1.0, 0.0, 0.0, 0.0],
    "pure_eglendirici": [0.0, 1.0, 0.0, 0.0],
    "pure_haber": [0.0, 0.0, 1.0, 0.0],
    "pure_sosyal": [0.0, 0.0, 0.0, 1.0],
    "ogretici_haber": [0.80, 0.05, 0.65, 0.10],
    "ogretici_sosyal": [0.80, 0.05, 0.05, 0.60],
    "eglendirici_sosyal": [0.05, 0.80, 0.05, 0.65],
    "haber_sosyal": [0.10, 0.05, 0.85, 0.50],
}


def fetch_pool():
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "pusula-semantic-v2-benchmark"})
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read()
    rows = json.loads(raw.decode("utf-8"))
    if not isinstance(rows, list) or len(rows) != 2000:
        raise ValueError(f"Expected pinned 2000-post pool, got {type(rows).__name__} / {len(rows) if isinstance(rows, list) else 'n/a'}")
    required = {"id", "metin", "kategori", "gercek_niyet", "tahmin_niyet", "etkilesim_puani", "tazelik", "clickbait"}
    for i, row in enumerate(rows):
        missing = required - set(row)
        if missing:
            raise KeyError(f"Pool row {i} missing {sorted(missing)}")
        if len(row["gercek_niyet"]) != 4 or len(row["tahmin_niyet"]) != 4:
            raise ValueError(f"Pool row {i} has invalid intent vector length")
    return rows


def cosine_rows(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.sum(a * b, axis=1) / np.maximum(np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1), 1e-12)


def cosine_profile(vectors, profile):
    p = np.asarray(profile, dtype=float)
    v = np.asarray(vectors, dtype=float)
    return (v @ p) / np.maximum(np.linalg.norm(v, axis=1) * np.linalg.norm(p), 1e-12)


def vector_metrics(gold, pred):
    gold = np.asarray(gold, dtype=float)
    pred = np.clip(np.asarray(pred, dtype=float), 0.0, 1.0)
    gold_dom = np.argmax(gold, axis=1)
    pred_dom = np.argmax(pred, axis=1)
    return {
        "intent_mae": float(np.mean(np.abs(gold - pred))),
        "mean_cosine_similarity": float(np.mean(cosine_rows(gold, pred))),
        "dominant_accuracy": float(accuracy_score(gold_dom, pred_dom)),
        "macro_f1": float(f1_score(gold_dom, pred_dom, labels=list(range(4)), average="macro", zero_division=0)),
        "pred_distribution": dict(Counter(INTENTS[i] for i in pred_dom)),
        "gold_distribution": dict(Counter(INTENTS[i] for i in gold_dom)),
        "per_class_accuracy": {
            cls: float(np.mean(pred_dom[np.where(gold_dom == i)[0]] == i)) if np.any(gold_dom == i) else None
            for i, cls in enumerate(INTENTS)
        },
    }


def pusula_score(intent_vectors, profile, freshness, engagement, clickbait):
    semantic = cosine_profile(intent_vectors, profile)
    return (0.70 * semantic + 0.15 * freshness + 0.15 * engagement) * (1.0 - clickbait)


def pairwise_concordance(gold, pred, max_pairs=250000, seed=42):
    n = len(gold)
    total = n * (n - 1) // 2
    rng = np.random.default_rng(seed)
    if total <= max_pairs:
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    else:
        # Deterministic sampled estimate for the 2000-post corpus.
        pairs = []
        seen = set()
        while len(pairs) < max_pairs:
            i = int(rng.integers(0, n))
            j = int(rng.integers(0, n - 1))
            if j >= i:
                j += 1
            if i > j:
                i, j = j, i
            key = (i, j)
            if key not in seen:
                seen.add(key)
                pairs.append(key)
    wins = 0.0
    comparable = 0
    for i, j in pairs:
        gd = gold[i] - gold[j]
        if abs(gd) < 1e-12:
            continue
        pd = pred[i] - pred[j]
        comparable += 1
        if gd * pd > 0:
            wins += 1.0
        elif abs(pd) < 1e-12:
            wins += 0.5
    return float(wins / comparable) if comparable else 1.0


def ranking_metrics(oracle_score, predicted_score, k=20):
    oracle_score = np.asarray(oracle_score, dtype=float)
    predicted_score = np.asarray(predicted_score, dtype=float)
    oracle_order = np.argsort(-oracle_score)
    predicted_order = np.argsort(-predicted_score)
    rho = spearmanr(oracle_score, predicted_score).statistic
    if np.isnan(rho):
        rho = 0.0
    return {
        "ndcg_at_20": float(ndcg_score(oracle_score.reshape(1, -1), predicted_score.reshape(1, -1), k=k)),
        "top20_overlap": float(len(set(oracle_order[:k]) & set(predicted_order[:k])) / k),
        "spearman": float(rho),
        "pairwise_concordance_sampled": pairwise_concordance(oracle_score, predicted_score),
    }


def diversified_order(scores, categories, k=20, max_per_category=5):
    order = np.argsort(-np.asarray(scores, dtype=float))
    counts = Counter()
    selected = []
    for i in order:
        cat = str(categories[i])
        if counts[cat] >= max_per_category:
            continue
        counts[cat] += 1
        selected.append(int(i))
        if len(selected) >= k:
            break
    return selected


def dcg(relevances):
    rel = np.asarray(relevances, dtype=float)
    if len(rel) == 0:
        return 0.0
    discounts = 1.0 / np.log2(np.arange(2, len(rel) + 2))
    return float(np.sum((np.power(2.0, rel) - 1.0) * discounts))


def diversified_metrics(oracle_score, predicted_score, categories, k=20):
    ideal = diversified_order(oracle_score, categories, k=k, max_per_category=5)
    pred = diversified_order(predicted_score, categories, k=k, max_per_category=5)
    ideal_dcg = dcg(np.asarray(oracle_score)[ideal])
    pred_dcg = dcg(np.asarray(oracle_score)[pred])
    return {
        "top20_overlap": float(len(set(ideal) & set(pred)) / k),
        "dcg_ratio_to_oracle_diversified": float(pred_dcg / ideal_dcg) if ideal_dcg > 0 else 1.0,
        "selected_n": len(pred),
    }


def aggregate_profile_metrics(by_profile, keys):
    return {k: float(np.mean([v[k] for v in by_profile.values()])) for k in keys}


def aggregate_worst(by_profile, keys):
    return {k: float(np.min([v[k] for v in by_profile.values()])) for k in keys}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="experiments/results/full_pool_e5_base.json")
    ap.add_argument("--summary", default="experiments/results/full_pool_e5_base.md")
    args = ap.parse_args()

    pool = fetch_pool()
    train = load_balanced()
    train_texts = [r["text"] for r in train]
    pool_texts = [r["metin"] for r in pool]
    all_texts = train_texts + pool_texts

    x, revision, hidden = encode(all_texts, MODEL, "query: ", batch_size=24, max_length=128)
    n_train = len(train)
    x_train, x_pool = x[:n_train], x[n_train:]
    dom_train = np.asarray([r["dominant"] for r in train])

    clf = LogisticRegression(C=4.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    clf.fit(x_train, dom_train)
    raw_probs = clf.predict_proba(x_pool)
    probs = np.zeros((len(pool), 4), dtype=float)
    class_to_col = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw_probs[:, class_to_col[cls]]

    gold = np.asarray([r["gercek_niyet"] for r in pool], dtype=float)
    current = np.asarray([r["tahmin_niyet"] for r in pool], dtype=float)
    new = probs
    freshness = np.asarray([float(r["tazelik"]) for r in pool], dtype=float)
    engagement = np.asarray([float(r["etkilesim_puani"]) for r in pool], dtype=float)
    clickbait = np.asarray([float(r["clickbait"]) for r in pool], dtype=float)
    categories = np.asarray([str(r["kategori"]) for r in pool])

    methods = {"current_tahmin_niyet": current, "e5_base_logistic_probability": new}
    result = {
        "status": "development_benchmark_external_generated_ground_truth_not_human_gold",
        "source": {
            "repository": "asimonmsz-design/pusula",
            "commit": SOURCE_COMMIT,
            "path": SOURCE_PATH,
            "url": SOURCE_URL,
            "n": len(pool),
        },
        "model": MODEL,
        "model_revision": revision,
        "hidden_size": hidden,
        "train_n": len(train),
        "train_distribution": dict(Counter(dom_train)),
        "vector_metrics": {},
        "ranking": {},
    }

    for method_name, vectors in methods.items():
        result["vector_metrics"][method_name] = vector_metrics(gold, vectors)
        by_profile = {}
        by_profile_div = {}
        for profile_name, profile in PROFILES.items():
            oracle = pusula_score(gold, profile, freshness, engagement, clickbait)
            predicted = pusula_score(vectors, profile, freshness, engagement, clickbait)
            by_profile[profile_name] = ranking_metrics(oracle, predicted, k=20)
            by_profile_div[profile_name] = diversified_metrics(oracle, predicted, categories, k=20)

        rank_keys = ["ndcg_at_20", "top20_overlap", "spearman", "pairwise_concordance_sampled"]
        div_keys = ["top20_overlap", "dcg_ratio_to_oracle_diversified"]
        result["ranking"][method_name] = {
            "macro": aggregate_profile_metrics(by_profile, rank_keys),
            "worst_profile": aggregate_worst(by_profile, rank_keys),
            "by_profile": by_profile,
            "diversified_macro": aggregate_profile_metrics(by_profile_div, div_keys),
            "diversified_worst_profile": aggregate_worst(by_profile_div, div_keys),
            "diversified_by_profile": by_profile_div,
        }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# PUSULA 2000-post E5-base end-to-end development benchmark",
        "",
        "> The pool's `gercek_niyet` is treated as benchmark ground truth from the project dataset, but it is not independently double-annotated human gold. Do not present these values as final human-evaluation metrics.",
        "",
        f"Pinned source: `asimonmsz-design/pusula@{SOURCE_COMMIT}` → `{SOURCE_PATH}`",
        f"Pool: **{len(pool)} posts**. New semantic encoder: `{MODEL}` @ `{revision}`.",
        "",
        "## Intent-vector prediction",
        "",
        "| Method | 4D MAE | Mean cosine | Dominant acc. | Macro-F1 |",
        "|---|---:|---:|---:|---:|",
    ]
    for method_name, v in result["vector_metrics"].items():
        lines.append(f"| {method_name} | {v['intent_mae']:.4f} | {v['mean_cosine_similarity']:.4f} | {v['dominant_accuracy']:.4f} | {v['macro_f1']:.4f} |")

    lines += [
        "",
        "## Full PUSULA ranking (semantic + freshness + engagement + clickbait)",
        "",
        "| Method | mean nDCG@20 | mean top-20 overlap | mean Spearman | pairwise | worst nDCG@20 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method_name, r in result["ranking"].items():
        m, w = r["macro"], r["worst_profile"]
        lines.append(f"| {method_name} | {m['ndcg_at_20']:.4f} | {m['top20_overlap']:.4f} | {m['spearman']:.4f} | {m['pairwise_concordance_sampled']:.4f} | {w['ndcg_at_20']:.4f} |")

    lines += [
        "",
        "## With category diversity cap (max 5/category in top 20)",
        "",
        "| Method | mean diversified top-20 overlap | mean DCG ratio vs oracle | worst DCG ratio |",
        "|---|---:|---:|---:|",
    ]
    for method_name, r in result["ranking"].items():
        m, w = r["diversified_macro"], r["diversified_worst_profile"]
        lines.append(f"| {method_name} | {m['top20_overlap']:.4f} | {m['dcg_ratio_to_oracle_diversified']:.4f} | {w['dcg_ratio_to_oracle_diversified']:.4f} |")

    lines += [
        "",
        "## Methodology guardrails",
        "",
        "- Only the semantic vector differs between the two compared systems. Freshness, engagement and clickbait inputs are identical.",
        "- Oracle ordering uses the same PUSULA formula with `gercek_niyet` substituted for the semantic vector.",
        "- This is a large reproducible development benchmark, not final human gold evaluation.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")

    compact = {
        "source_commit": SOURCE_COMMIT,
        "pool_n": len(pool),
        "model_revision": revision,
        "vector_metrics": result["vector_metrics"],
        "ranking_macro": {k: v["macro"] for k, v in result["ranking"].items()},
        "ranking_worst": {k: v["worst_profile"] for k, v in result["ranking"].items()},
        "diversified_macro": {k: v["diversified_macro"] for k, v in result["ranking"].items()},
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
