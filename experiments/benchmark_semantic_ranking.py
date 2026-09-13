from __future__ import annotations

import argparse
import gc
import json
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ndcg_score
from sklearn.neighbors import KNeighborsRegressor

from benchmark_encoder_sweep import encode
from benchmark_intent_balanced_corpus import load_balanced
from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS

ROOT = Path(__file__).resolve().parents[1]

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

MODEL_SPECS = [
    {"name": "intfloat/multilingual-e5-small", "prefix": "query: "},
    {"name": "intfloat/multilingual-e5-base", "prefix": "query: "},
]


def cosine_to_profile(vectors, profile):
    v = np.asarray(vectors, dtype=float)
    p = np.asarray(profile, dtype=float)
    return (v @ p) / np.maximum(np.linalg.norm(v, axis=1) * np.linalg.norm(p), 1e-12)


def pairwise_concordance(gold, pred):
    wins = 0
    comparable = 0
    for i in range(len(gold)):
        for j in range(i + 1, len(gold)):
            gd = gold[i] - gold[j]
            if abs(gd) < 1e-9:
                continue
            pd = pred[i] - pred[j]
            comparable += 1
            if gd * pd > 0:
                wins += 1
            elif abs(pd) < 1e-12:
                wins += 0.5
    return float(wins / comparable) if comparable else 1.0


def ranking_metrics(gold_scores, pred_scores, k=10):
    gold_scores = np.asarray(gold_scores, dtype=float)
    pred_scores = np.asarray(pred_scores, dtype=float)
    gold_order = np.argsort(-gold_scores)
    pred_order = np.argsort(-pred_scores)
    top_gold = set(gold_order[:k])
    top_pred = set(pred_order[:k])
    rho = spearmanr(gold_scores, pred_scores).statistic
    if np.isnan(rho):
        rho = 0.0
    return {
        "ndcg_at_10": float(ndcg_score(gold_scores.reshape(1, -1), pred_scores.reshape(1, -1), k=k)),
        "top10_overlap": float(len(top_gold & top_pred) / k),
        "spearman": float(rho),
        "pairwise_concordance": pairwise_concordance(gold_scores, pred_scores),
    }


def fit_vectors(x_train, y_train, dom_train, x_test):
    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(x_train, y_train)
    knn_pred = np.asarray(knn.predict(x_test), dtype=float)

    clf = LogisticRegression(C=4.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    clf.fit(x_train, dom_train)
    raw = clf.predict_proba(x_test)
    probs = np.zeros((len(x_test), 4), dtype=float)
    class_to_col = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw[:, class_to_col[cls]]

    hybrid = 0.65 * np.clip(knn_pred[:, :4], 0, 1) + 0.35 * probs
    return {
        "knn_vector": np.clip(knn_pred[:, :4], 0, 1),
        "logistic_probability_vector": probs,
        "hybrid_vector": np.clip(hybrid, 0, 1),
    }


def evaluate_vector_method(gold_vectors, pred_vectors):
    by_profile = {}
    for name, profile in PROFILES.items():
        gold_rel = cosine_to_profile(gold_vectors, profile)
        pred_rel = cosine_to_profile(pred_vectors, profile)
        by_profile[name] = ranking_metrics(gold_rel, pred_rel, k=10)
    keys = ["ndcg_at_10", "top10_overlap", "spearman", "pairwise_concordance"]
    macro = {k: float(np.mean([v[k] for v in by_profile.values()])) for k in keys}
    worst = {k: float(np.min([v[k] for v in by_profile.values()])) for k in keys}
    return {"macro": macro, "worst_profile": worst, "by_profile": by_profile}


def markdown(result):
    lines = [
        "# Direct semantic ranking benchmark",
        "",
        "> Development-only. This benchmark isolates the semantic intent component of PUSULA. Freshness, engagement and diversity terms are intentionally held out so the intent-vector quality can be measured directly.",
        "",
        "Gold relevance is cosine similarity between each simulated user-intent profile and the draft gold 4D post vector. Predicted relevance uses the model-produced 4D vector.",
        "",
        "| Encoder / vector method | mean nDCG@10 | mean top-10 overlap | mean Spearman | pairwise concordance | worst nDCG@10 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model_name, mr in result["models"].items():
        for method, r in mr["methods"].items():
            m = r["macro"]
            w = r["worst_profile"]
            lines.append(
                f"| {model_name} / {method} | {m['ndcg_at_10']:.3f} | {m['top10_overlap']:.3f} | "
                f"{m['spearman']:.3f} | {m['pairwise_concordance']:.3f} | {w['ndcg_at_10']:.3f} |"
            )
    lines += [
        "",
        "## User-intent profiles",
        "",
    ]
    for name, p in PROFILES.items():
        lines.append(f"- `{name}`: `{p}`")
    lines += [
        "",
        "## Guardrails",
        "",
        "- The 48 hard cases are architecture-development data, not an untouched final test set.",
        "- These metrics evaluate only semantic intent ordering. A later end-to-end ranking test must reintroduce freshness, engagement, clickbait penalty and diversity constraints.",
        "- Final claims require a new independently annotated holdout after architecture selection is frozen.",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="experiments/results/semantic_ranking.json")
    ap.add_argument("--summary", default="experiments/results/semantic_ranking.md")
    args = ap.parse_args()

    train = load_balanced()
    hard = load_hard_eval()
    texts = [r["text"] for r in train] + [r["text"] for r in hard]
    n = len(train)
    y_train = np.asarray([r["y"] for r in train], dtype=float)
    dom_train = np.asarray([r["dominant"] for r in train])
    gold_vectors = np.asarray([r["y"][:4] for r in hard], dtype=float)

    result = {
        "status": "development_only_semantic_component",
        "train_n": len(train),
        "hard_n": len(hard),
        "profiles": PROFILES,
        "models": {},
    }

    for spec in MODEL_SPECS:
        x, revision, hidden = encode(texts, spec["name"], spec["prefix"], batch_size=16, max_length=128)
        vectors = fit_vectors(x[:n], y_train, dom_train, x[n:])
        methods = {name: evaluate_vector_method(gold_vectors, vec) for name, vec in vectors.items()}
        result["models"][spec["name"]] = {
            "revision": revision,
            "hidden_size": hidden,
            "methods": methods,
        }
        print(json.dumps({"model": spec["name"], "methods": {k: v["macro"] for k, v in methods.items()}}, ensure_ascii=False, indent=2))
        del x, vectors
        gc.collect()

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / args.summary).write_text(markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
