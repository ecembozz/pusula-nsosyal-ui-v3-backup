from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsRegressor

from benchmark_style_generalization import load_base_training, load_hard_eval
from benchmark_supervised_embeddings import INTENTS, cosine_rows, dominant_from_scores, encode_texts, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
BALANCED = ROOT / "data/dev_labels/intent_balanced_training_v1.jsonl"


def to_y(row):
    return [float(row["intent"][k]) for k in INTENTS] + [float(row["clickbait"])]


def load_balanced():
    return [
        {
            "id": r["id"],
            "text": r["text"],
            "dominant": r["dominant_intent"],
            "y": to_y(r),
            "style_bucket": r.get("style_bucket", "unknown"),
        }
        for r in read_jsonl(BALANCED)
    ]


def inverse_class_weights(dom):
    counts = Counter(dom)
    n = len(dom)
    return {c: n / (len(INTENTS) * counts[c]) for c in INTENTS}


def class_sample_weight(dom):
    w = inverse_class_weights(dom)
    return np.asarray([w[x] for x in dom], dtype=float)


def evaluate_vector(y_true, pred, dom_true):
    pred = np.clip(np.asarray(pred, dtype=float), 0.0, 1.0)
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


def evaluate_classifier(dom_true, pred, probs):
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
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(pred) * coverage)))
        idx = np.argsort(-margin)[:n]
        out[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def challenge_report(hard_rows, y_true, pred_vector, dom_true):
    bucket = defaultdict(list)
    for i, row in enumerate(hard_rows):
        for tag in row.get("challenge", []):
            bucket[tag].append(i)
    dom_pred = dominant_from_scores(np.clip(pred_vector, 0, 1))
    out = {}
    for tag, idxs in sorted(bucket.items()):
        if len(idxs) < 3:
            continue
        idx = np.asarray(idxs, dtype=int)
        out[tag] = {
            "n": int(len(idx)),
            "dominant_accuracy": float(np.mean([dom_pred[i] == dom_true[i] for i in idx])),
            "intent_mae": float(np.mean(np.abs(y_true[idx, :4] - pred_vector[idx, :4]))),
        }
    return out


def fit_suite(x_train, y_train, dom_train, x_test, y_test, dom_test, hard_rows):
    sw = class_sample_weight(dom_train)

    # Vector head 1: semantic nearest-neighbour regression.
    knn = KNeighborsRegressor(n_neighbors=min(9, max(3, len(x_train) // 24)), weights="distance", metric="cosine")
    knn.fit(x_train, y_train)
    knn_pred = np.asarray(knn.predict(x_test), dtype=float)

    # Vector head 2: globally smooth weighted linear regression.
    ridge = Ridge(alpha=6.0)
    ridge.fit(x_train, y_train, sample_weight=sw)
    ridge_pred = np.asarray(ridge.predict(x_test), dtype=float)

    # Dominant auxiliary head with explicit class balancing.
    clf = LogisticRegression(
        C=4.0,
        class_weight="balanced",
        max_iter=5000,
        solver="lbfgs",
        random_state=42,
    )
    clf.fit(x_train, dom_train)
    cls_pred = clf.predict(x_test)
    raw_probs = clf.predict_proba(x_test)
    class_to_col = {c: i for i, c in enumerate(clf.classes_)}
    probs = np.zeros((len(x_test), 4), dtype=float)
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw_probs[:, class_to_col[cls]]

    # The classifier only nudges the intent vector; it does not replace multi-intent regression.
    hybrid = np.zeros_like(knn_pred)
    hybrid[:, :4] = 0.70 * np.clip(knn_pred[:, :4], 0, 1) + 0.30 * probs
    hybrid[:, 4] = np.clip(knn_pred[:, 4], 0, 1)

    # A slightly smoother ensemble helps if nearest-neighbour estimates are noisy.
    ensemble = np.zeros_like(knn_pred)
    ensemble[:, :4] = 0.55 * np.clip(knn_pred[:, :4], 0, 1) + 0.25 * np.clip(ridge_pred[:, :4], 0, 1) + 0.20 * probs
    ensemble[:, 4] = 0.7 * np.clip(knn_pred[:, 4], 0, 1) + 0.3 * np.clip(ridge_pred[:, 4], 0, 1)

    models = {
        "semantic_knn": evaluate_vector(y_test, knn_pred, dom_test),
        "weighted_ridge": evaluate_vector(y_test, ridge_pred, dom_test),
        "hybrid_knn_logistic": evaluate_vector(y_test, hybrid, dom_test),
        "ensemble_knn_ridge_logistic": evaluate_vector(y_test, ensemble, dom_test),
        "balanced_logistic_dominant": evaluate_classifier(dom_test, cls_pred, probs),
    }
    for name, vec in {
        "semantic_knn": knn_pred,
        "weighted_ridge": ridge_pred,
        "hybrid_knn_logistic": hybrid,
        "ensemble_knn_ridge_logistic": ensemble,
    }.items():
        models[name]["by_challenge"] = challenge_report(hard_rows, y_test, np.clip(vec, 0, 1), dom_test)
    return models


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--output", default="experiments/results/intent_balanced_corpus.json")
    ap.add_argument("--summary", default="experiments/results/intent_balanced_corpus.md")
    args = ap.parse_args()

    balanced = load_balanced()
    base = load_base_training()
    hard = load_hard_eval()

    all_rows = balanced + base + hard
    x_all, revision = encode_texts([r["text"] for r in all_rows], args.model)
    nb, nbase = len(balanced), len(base)
    xb = x_all[:nb]
    xbase = x_all[nb:nb+nbase]
    xh = x_all[nb+nbase:]

    yb = np.asarray([r["y"] for r in balanced], dtype=float)
    db = np.asarray([r["dominant"] for r in balanced])
    ybase = np.asarray([r["y"] for r in base], dtype=float)
    dbase = np.asarray([r["dominant"] for r in base])
    yh = np.asarray([r["y"] for r in hard], dtype=float)
    dh = np.asarray([r["dominant"] for r in hard])

    scenarios = {
        "intent_balanced_only": fit_suite(xb, yb, db, xh, yh, dh, hard),
        "intent_balanced_plus_old_base": fit_suite(
            np.vstack([xb, xbase]),
            np.vstack([yb, ybase]),
            np.concatenate([db, dbase]),
            xh, yh, dh, hard,
        ),
    }

    result = {
        "status": "development_only_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "balanced_train_n": len(balanced),
        "balanced_train_distribution": dict(Counter(db)),
        "balanced_style_distribution": dict(Counter(r["style_bucket"] for r in balanced)),
        "old_base_n": len(base),
        "old_base_distribution": dict(Counter(dbase)),
        "hard_eval_n": len(hard),
        "hard_eval_distribution": dict(Counter(dh)),
        "scenarios": scenarios,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Intent-balanced style-diverse supervised pilot",
        "",
        "> Development-only. Training labels are assistant-authored synthetic development labels; the 48 hard labels are single-annotator drafts. Not final competition metrics.",
        "",
        f"Embedding: `{args.model}` @ `{revision}`",
        f"Balanced training: **{len(balanced)}** = `{dict(Counter(db))}`",
        f"Hard evaluation: **{len(hard)}** = `{dict(Counter(dh))}`",
        "",
    ]
    for skey, title in [
        ("intent_balanced_only", "136 intent-balanced examples only"),
        ("intent_balanced_plus_old_base", "136 balanced + 96 earlier base examples"),
    ]:
        lines += [
            f"## {title}", "",
            "| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for name in ("semantic_knn", "weighted_ridge", "hybrid_knn_logistic", "ensemble_knn_ridge_logistic"):
            r = scenarios[skey][name]
            lines.append(f"| {name} | {r['dominant_accuracy']:.3f} | {r['macro_f1']:.3f} | {r['intent_mae']:.3f} | {r['mean_cosine_similarity']:.3f} | {r['clickbait_mae']:.3f} |")
        c = scenarios[skey]["balanced_logistic_dominant"]
        lines += [
            "",
            f"Dominant-only balanced logistic: accuracy **{c['dominant_accuracy']:.3f}**, macro-F1 **{c['macro_f1']:.3f}**, top-50% confidence accuracy **{c.get('accuracy_at_50pct_coverage', 0):.3f}**.",
            f"Per-class: `{c['per_class_accuracy']}`",
            "",
        ]
    lines += [
        "## Interpretation",
        "",
        "This experiment asks whether intent-balanced, style-diverse supervision transfers better to the hand-written hard-style development set than topic-balanced supervision. It is explicitly a model-selection experiment and cannot be used as a final competition claim.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
