from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsRegressor

from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS, cosine_rows, dominant_from_scores, encode_texts
from benchmark_pool2000_group_cv import load_pool, softmax_np if False else None

ROOT = Path(__file__).resolve().parents[1]


def softmax_np(x):
    x = x - np.max(x, axis=1, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=1, keepdims=True)


def vec_metrics(y_true, pred, dom_true):
    pred = np.clip(np.asarray(pred, dtype=float), 0, 1)
    dom_pred = dominant_from_scores(pred)
    return {
        "dominant_accuracy": float(accuracy_score(dom_true, dom_pred)),
        "macro_f1": float(f1_score(dom_true, dom_pred, labels=INTENTS, average="macro", zero_division=0)),
        "intent_mae": float(np.mean(np.abs(y_true - pred))),
        "mean_cosine_similarity": float(np.mean(cosine_rows(y_true, pred))),
        "pred_distribution": dict(Counter(dom_pred)),
        "per_class_accuracy": {
            cls: float(np.mean([dom_pred[i] == cls for i in np.where(np.asarray(dom_true) == cls)[0]]))
            for cls in INTENTS
        },
    }


def cls_metrics(dom_true, pred, probs):
    correct = np.asarray([a == b for a, b in zip(dom_true, pred)], dtype=bool)
    sorted_p = np.sort(probs, axis=1)
    margin = sorted_p[:, -1] - sorted_p[:, -2]
    out = {
        "dominant_accuracy": float(accuracy_score(dom_true, pred)),
        "macro_f1": float(f1_score(dom_true, pred, labels=INTENTS, average="macro", zero_division=0)),
        "pred_distribution": dict(Counter(pred)),
        "per_class_accuracy": {
            cls: float(np.mean([pred[i] == cls for i in np.where(np.asarray(dom_true) == cls)[0]]))
            for cls in INTENTS
        },
    }
    for cov in (0.50, 0.75):
        n = max(1, int(round(len(pred) * cov)))
        idx = np.argsort(-margin)[:n]
        out[f"accuracy_at_{int(cov*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--model", default="intfloat/multilingual-e5-base")
    ap.add_argument("--output", default="experiments/results/pool2000_to_hard48.json")
    ap.add_argument("--summary", default="experiments/results/pool2000_to_hard48.md")
    args = ap.parse_args()

    pool = load_pool(Path(args.pool))
    hard = load_hard_eval()
    texts = [r["text"] for r in pool] + [r["text"] for r in hard]
    x, revision = encode_texts(texts, args.model, batch_size=16)
    n = len(pool)
    xp, xh = x[:n], x[n:]
    yp = np.asarray([r["y"] for r in pool], dtype=float)
    dp = np.asarray([r["dominant"] for r in pool])
    yh = np.asarray([r["y"][:4] for r in hard], dtype=float)
    dh = np.asarray([r["dominant"] for r in hard])

    knn = KNeighborsRegressor(n_neighbors=15, weights="distance", metric="cosine")
    knn.fit(xp, yp)
    p_knn = np.asarray(knn.predict(xh), dtype=float)

    ridge = Ridge(alpha=4.0)
    ridge.fit(xp, yp)
    p_ridge = np.asarray(ridge.predict(xh), dtype=float)

    clf = LogisticRegression(C=4.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    clf.fit(xp, dp)
    d_pred = clf.predict(xh)
    raw_probs = clf.predict_proba(xh)
    probs = np.zeros((len(xh), 4), dtype=float)
    cmap = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw_probs[:, cmap[cls]]

    hybrid = np.clip(0.70 * p_knn + 0.15 * np.clip(p_ridge, 0, 1) + 0.15 * probs, 0, 1)

    # OOD screening against the actual 2k training pool.
    nearest = np.max(xh @ xp.T, axis=1)
    pool_sim = xp @ xp.T
    np.fill_diagonal(pool_sim, -1.0)
    threshold = float(np.quantile(np.max(pool_sim, axis=1), 0.05))
    ood = nearest < threshold

    result = {
        "status": "development_cross_style_transfer_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "train_pool_n": len(pool),
        "hard_eval_n": len(hard),
        "train_dominant_distribution": dict(Counter(dp)),
        "hard_dominant_distribution": dict(Counter(dh)),
        "semantic_knn": vec_metrics(yh, p_knn, dh),
        "ridge": vec_metrics(yh, p_ridge, dh),
        "hybrid": vec_metrics(yh, hybrid, dh),
        "balanced_logistic_dominant": cls_metrics(dh, d_pred.tolist(), probs),
        "ood": {
            "threshold": threshold,
            "ood_rate": float(np.mean(ood)),
            "mean_nearest_pool_cosine": float(np.mean(nearest)),
            "min_nearest_pool_cosine": float(np.min(nearest)),
        },
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# PUSULA 2,000 → hard-48 cross-style transfer",
        "",
        "> Train labels come from the pool's dataset-supplied `gercek_niyet`. The 48 hard-style examples are excluded from training. They are a repeatedly inspected development set, not a final untouched test set.",
        "",
        f"Encoder: `{args.model}` @ `{revision}`",
        f"Training pool: **{len(pool)}**; hard-style development set: **{len(hard)}**.",
        "",
        "| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("semantic_knn", "ridge", "hybrid"):
        m = result[name]
        lines.append(f"| {name} | {m['dominant_accuracy']:.3f} | {m['macro_f1']:.3f} | {m['intent_mae']:.3f} | {m['mean_cosine_similarity']:.3f} |")
    c = result["balanced_logistic_dominant"]
    lines += [
        f"| logistic dominant | {c['dominant_accuracy']:.3f} | {c['macro_f1']:.3f} | - | - |",
        "",
        f"Classifier top-50% confidence accuracy: **{c['accuracy_at_50pct_coverage']:.3f}**.",
        f"Per-class classifier accuracy: `{c['per_class_accuracy']}`",
        f"OOD rate against the 2k pool: **{result['ood']['ood_rate']:.3f}**; mean nearest cosine: **{result['ood']['mean_nearest_pool_cosine']:.3f}**.",
        "",
        "This is the key style-transfer development benchmark: unlike the 2k cross-validation result, these evaluation texts were independently authored in a different style and are not templated copies of the pool.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
