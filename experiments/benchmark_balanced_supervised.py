from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsRegressor

from benchmark_style_generalization import load_base_training, load_hard_eval
from benchmark_supervised_embeddings import INTENTS, cosine_rows, dominant_from_scores, encode_texts

ROOT = Path(__file__).resolve().parents[1]


def class_weights(dom):
    c = Counter(dom)
    n = len(dom)
    return {k: n / (len(INTENTS) * c[k]) for k in INTENTS}


def sample_weights(dom):
    cw = class_weights(dom)
    return np.asarray([cw[x] for x in dom], dtype=float)


def balanced_resample(x, y, dom):
    dom = np.asarray(dom)
    counts = Counter(dom)
    target = max(counts.values())
    xs, ys, ds = [], [], []
    rng = np.random.default_rng(42)
    for cls in INTENTS:
        idx = np.where(dom == cls)[0]
        if len(idx) == 0:
            continue
        reps = target // len(idx)
        rem = target % len(idx)
        chosen = list(idx) * reps
        if rem:
            chosen += list(rng.choice(idx, size=rem, replace=False))
        xs.append(x[chosen])
        ys.append(y[chosen])
        ds.extend([cls] * len(chosen))
    return np.vstack(xs), np.vstack(ys), np.asarray(ds)


def eval_vector(y_true, pred, dom_true):
    pred = np.clip(pred, 0, 1)
    dom_pred = dominant_from_scores(pred)
    return {
        "dominant_accuracy": float(accuracy_score(dom_true, dom_pred)),
        "macro_f1": float(f1_score(dom_true, dom_pred, labels=INTENTS, average="macro", zero_division=0)),
        "intent_mae": float(np.mean(np.abs(y_true[:, :4] - pred[:, :4]))),
        "mean_cosine_similarity": float(np.mean(cosine_rows(y_true[:, :4], pred[:, :4]))),
        "clickbait_mae": float(np.mean(np.abs(y_true[:, 4] - pred[:, 4]))),
        "pred_distribution": dict(Counter(dom_pred)),
        "per_class_accuracy": {
            cls: float(np.mean([dom_pred[i] == cls for i in np.where(np.asarray(dom_true) == cls)[0]]))
            for cls in INTENTS
        },
    }


def eval_class(dom_true, pred, probs=None):
    out = {
        "dominant_accuracy": float(accuracy_score(dom_true, pred)),
        "macro_f1": float(f1_score(dom_true, pred, labels=INTENTS, average="macro", zero_division=0)),
        "pred_distribution": dict(Counter(pred)),
        "per_class_accuracy": {
            cls: float(np.mean([pred[i] == cls for i in np.where(np.asarray(dom_true) == cls)[0]]))
            for cls in INTENTS
        },
    }
    if probs is not None:
        sorted_p = np.sort(probs, axis=1)
        margin = sorted_p[:, -1] - sorted_p[:, -2]
        correct = np.asarray([a == b for a, b in zip(dom_true, pred)], dtype=bool)
        for coverage in (0.50, 0.75):
            n = max(1, int(round(len(pred) * coverage)))
            idx = np.argsort(-margin)[:n]
            out[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--output", default="experiments/results/balanced_supervised.json")
    ap.add_argument("--summary", default="experiments/results/balanced_supervised.md")
    args = ap.parse_args()

    base = load_base_training()
    hard = load_hard_eval()
    texts = [r["text"] for r in base] + [r["text"] for r in hard]
    x, revision = encode_texts(texts, args.model)
    n = len(base)
    xb, xh = x[:n], x[n:]
    yb = np.asarray([r["y"] for r in base], dtype=float)
    yh = np.asarray([r["y"] for r in hard], dtype=float)
    db = np.asarray([r["dominant"] for r in base])
    dh = np.asarray([r["dominant"] for r in hard])

    sw = sample_weights(db)

    ridge = Ridge(alpha=8.0)
    ridge.fit(xb, yb, sample_weight=sw)
    ridge_pred = ridge.predict(xh)

    x_bal, y_bal, d_bal = balanced_resample(xb, yb, db)
    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(x_bal, y_bal)
    knn_pred = np.asarray(knn.predict(xh), dtype=float)

    clf = LogisticRegression(
        C=3.0,
        class_weight="balanced",
        max_iter=4000,
        solver="lbfgs",
        random_state=42,
    )
    clf.fit(xb, db)
    clf_pred = clf.predict(xh)
    raw_probs = clf.predict_proba(xh)
    class_to_col = {c: i for i, c in enumerate(clf.classes_)}
    probs = np.zeros((len(xh), 4), dtype=float)
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw_probs[:, class_to_col[cls]]

    # Keep semantic regression as the main signal; the balanced classifier only nudges
    # the dominant intent and cannot erase multi-intent information.
    hybrid = np.zeros_like(knn_pred)
    hybrid[:, :4] = 0.72 * np.clip(knn_pred[:, :4], 0, 1) + 0.28 * probs
    hybrid[:, 4] = np.clip(knn_pred[:, 4], 0, 1)

    result = {
        "status": "development_only_single_annotator_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "train_n": len(base),
        "test_n": len(hard),
        "train_distribution": dict(Counter(db)),
        "class_weights": class_weights(db),
        "balanced_resample_distribution": dict(Counter(d_bal)),
        "models": {
            "weighted_ridge_vector": eval_vector(yh, ridge_pred, dh),
            "balanced_knn_vector": eval_vector(yh, knn_pred, dh),
            "balanced_logistic_dominant": eval_class(dh, clf_pred, probs),
            "hybrid_knn_plus_logistic": eval_vector(yh, hybrid, dh),
        },
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Class-balanced supervised diagnostic",
        "",
        "> Development-only; single-annotator draft labels. Not final competition metrics.",
        "",
        f"Embedding: `{args.model}` @ `{revision}`",
        f"Train: **{len(base)}**; hard-style test: **{len(hard)}**.",
        f"Original train distribution: `{dict(Counter(db))}`",
        f"Balanced k-NN resample: `{dict(Counter(d_bal))}`",
        "",
        "| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("weighted_ridge_vector", "balanced_knn_vector", "hybrid_knn_plus_logistic"):
        r = result["models"][name]
        lines.append(f"| {name} | {r['dominant_accuracy']:.3f} | {r['macro_f1']:.3f} | {r['intent_mae']:.3f} | {r['mean_cosine_similarity']:.3f} |")
    c = result["models"]["balanced_logistic_dominant"]
    lines += [
        "",
        "## Balanced dominant-intent classifier",
        "",
        f"Accuracy: **{c['dominant_accuracy']:.3f}**; macro-F1: **{c['macro_f1']:.3f}**; top-50%-confidence accuracy: **{c.get('accuracy_at_50pct_coverage', 0):.3f}**.",
        f"Per-class accuracy: `{c['per_class_accuracy']}`",
        "",
        "This diagnostic tests whether the previous collapse was mainly caused by intent imbalance. It does not replace a larger, independently labeled development set.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
