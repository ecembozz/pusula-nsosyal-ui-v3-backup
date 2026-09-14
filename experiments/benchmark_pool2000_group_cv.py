from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.neighbors import KNeighborsRegressor

from benchmark_supervised_embeddings import INTENTS, cosine_rows, dominant_from_scores, encode_texts

ROOT = Path(__file__).resolve().parents[1]


def load_pool(path: Path):
    rows = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for r in rows:
        gt = [float(x) for x in r["gercek_niyet"]]
        current = [float(x) for x in r.get("tahmin_niyet", [0, 0, 0, 0])]
        out.append({
            "id": str(r["id"]),
            "text": str(r["metin"]),
            "author": str(r.get("yazar", "unknown")),
            "category": str(r.get("kategori", "unknown")),
            "y": gt,
            "current": current,
            "dominant": INTENTS[int(np.argmax(gt))],
            "clickbait": float(r.get("clickbait", 0.0)),
        })
    return out


def vector_metrics(y_true, y_pred, dom_true):
    pred = np.clip(np.asarray(y_pred, dtype=float), 0.0, 1.0)
    dom_pred = dominant_from_scores(pred)
    return {
        "dominant_accuracy": float(accuracy_score(dom_true, dom_pred)),
        "macro_f1": float(f1_score(dom_true, dom_pred, labels=INTENTS, average="macro", zero_division=0)),
        "intent_mae": float(np.mean(np.abs(y_true - pred))),
        "mean_cosine_similarity": float(np.mean(cosine_rows(y_true, pred))),
        "pred_distribution": dict(Counter(dom_pred)),
        "per_class_accuracy": {
            cls: float(np.mean([dom_pred[i] == cls for i in np.where(np.asarray(dom_true) == cls)[0]]))
            if np.any(np.asarray(dom_true) == cls) else None
            for cls in INTENTS
        },
    }


def classifier_metrics(dom_true, pred, probs):
    correct = np.asarray([a == b for a, b in zip(dom_true, pred)], dtype=bool)
    sorted_p = np.sort(probs, axis=1)
    margin = sorted_p[:, -1] - sorted_p[:, -2]
    out = {
        "dominant_accuracy": float(accuracy_score(dom_true, pred)),
        "macro_f1": float(f1_score(dom_true, pred, labels=INTENTS, average="macro", zero_division=0)),
        "pred_distribution": dict(Counter(pred)),
        "per_class_accuracy": {
            cls: float(np.mean([pred[i] == cls for i in np.where(np.asarray(dom_true) == cls)[0]]))
            if np.any(np.asarray(dom_true) == cls) else None
            for cls in INTENTS
        },
    }
    for cov in (0.50, 0.75, 0.90):
        n = max(1, int(round(len(pred) * cov)))
        idx = np.argsort(-margin)[:n]
        out[f"accuracy_at_{int(cov*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def fit_predict(x_tr, y_tr, d_tr, x_va, k):
    knn = KNeighborsRegressor(n_neighbors=k, weights="distance", metric="cosine")
    knn.fit(x_tr, y_tr)
    p_knn = np.asarray(knn.predict(x_va), dtype=float)

    ridge = Ridge(alpha=4.0)
    ridge.fit(x_tr, y_tr)
    p_ridge = np.asarray(ridge.predict(x_va), dtype=float)

    clf = LogisticRegression(C=4.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    clf.fit(x_tr, d_tr)
    d_pred = clf.predict(x_va)
    raw = clf.predict_proba(x_va)
    p_cls = np.zeros((len(x_va), 4), dtype=float)
    col = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        if cls in col:
            p_cls[:, j] = raw[:, col[cls]]

    hybrid = np.clip(0.70 * p_knn + 0.15 * np.clip(p_ridge, 0, 1) + 0.15 * p_cls, 0, 1)
    return p_knn, p_ridge, hybrid, d_pred, p_cls


def run_cv(x, y, dom, groups, rows, splitter, mode_name, k=11):
    n = len(rows)
    pred_knn = np.zeros_like(y)
    pred_ridge = np.zeros_like(y)
    pred_hybrid = np.zeros_like(y)
    pred_cls = np.empty(n, dtype=object)
    prob_cls = np.zeros((n, 4), dtype=float)
    fold_meta = []

    if mode_name == "author_group_cv":
        split_iter = splitter.split(x, dom, groups)
    else:
        split_iter = splitter.split(x, dom)

    for fold, (tr, va) in enumerate(split_iter, start=1):
        pk, pr, ph, dc, pc = fit_predict(x[tr], y[tr], dom[tr], x[va], k)
        pred_knn[va] = pk
        pred_ridge[va] = pr
        pred_hybrid[va] = ph
        pred_cls[va] = dc
        prob_cls[va] = pc
        fold_meta.append({
            "fold": fold,
            "n_train": int(len(tr)),
            "n_val": int(len(va)),
            "train_authors": int(len(set(groups[tr]))),
            "val_authors": int(len(set(groups[va]))),
        })

    return {
        "semantic_knn": vector_metrics(y, pred_knn, dom),
        "ridge": vector_metrics(y, pred_ridge, dom),
        "hybrid": vector_metrics(y, pred_hybrid, dom),
        "balanced_logistic_dominant": classifier_metrics(dom, pred_cls.tolist(), prob_cls),
        "folds": fold_meta,
        "oof_predictions": [
            {
                "id": rows[i]["id"],
                "author": rows[i]["author"],
                "category": rows[i]["category"],
                "gold": [float(v) for v in y[i]],
                "current": [float(v) for v in rows[i]["current"]],
                "hybrid": [float(v) for v in np.clip(pred_hybrid[i], 0, 1)],
                "gold_dominant": dom[i],
                "classifier_dominant": pred_cls[i],
                "classifier_confidence": float(np.max(prob_cls[i])),
            }
            for i in range(n)
        ],
    }


def clickbait_cv(x, click, groups):
    # Dataset clickbait values are scores; treat >= 0.75 as positive for this diagnostic.
    target = (click >= 0.75).astype(int)
    if len(np.unique(target)) < 2:
        return {"available": False}
    splitter = GroupKFold(n_splits=5)
    probs = np.zeros(len(target), dtype=float)
    preds = np.zeros(len(target), dtype=int)
    for tr, va in splitter.split(x, target, groups):
        clf = LogisticRegression(C=2.0, class_weight="balanced", max_iter=3000, random_state=42)
        clf.fit(x[tr], target[tr])
        probs[va] = clf.predict_proba(x[va])[:, 1]
        preds[va] = (probs[va] >= 0.5).astype(int)
    return {
        "available": True,
        "positive_n": int(np.sum(target)),
        "roc_auc": float(roc_auc_score(target, probs)),
        "f1": float(f1_score(target, preds, zero_division=0)),
        "accuracy": float(accuracy_score(target, preds)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--model", default="intfloat/multilingual-e5-base")
    ap.add_argument("--output", default="experiments/results/pool2000_e5_base_group_cv.json")
    ap.add_argument("--summary", default="experiments/results/pool2000_e5_base_group_cv.md")
    ap.add_argument("--predictions", default="experiments/results/pool2000_e5_base_oof.jsonl")
    args = ap.parse_args()

    rows = load_pool(Path(args.input))
    texts = [r["text"] for r in rows]
    y = np.asarray([r["y"] for r in rows], dtype=float)
    current = np.asarray([r["current"] for r in rows], dtype=float)
    dom = np.asarray([r["dominant"] for r in rows])
    groups = np.asarray([r["author"] for r in rows])
    click = np.asarray([r["clickbait"] for r in rows], dtype=float)

    x, revision = encode_texts(texts, args.model, batch_size=16)

    current_metrics = vector_metrics(y, current, dom)
    author_cv = run_cv(x, y, dom, groups, rows, GroupKFold(n_splits=5), "author_group_cv", k=11)
    random_cv = run_cv(x, y, dom, groups, rows, StratifiedKFold(n_splits=5, shuffle=True, random_state=42), "random_stratified_cv", k=11)
    click_result = clickbait_cv(x, click, groups)

    result = {
        "status": "dataset_benchmark_not_real_world_final",
        "source": "asimonmsz-design/pusula:kod/veri/etiketli_havuz.json",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "n": len(rows),
        "author_n": len(set(groups)),
        "category_distribution": dict(Counter(r["category"] for r in rows)),
        "dominant_distribution": dict(Counter(dom)),
        "current_tahmin_niyet": current_metrics,
        "author_group_cv": {k: v for k, v in author_cv.items() if k != "oof_predictions"},
        "random_stratified_cv": {k: v for k, v in random_cv.items() if k != "oof_predictions"},
        "clickbait_author_group_cv": click_result,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    pred_path = ROOT / args.predictions
    with pred_path.open("w", encoding="utf-8") as f:
        for row in author_cv["oof_predictions"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    a = author_cv
    r = random_cv
    lines = [
        "# PUSULA 2,000-post E5-base benchmark",
        "",
        "> Uses the dataset-supplied `gercek_niyet` vectors as labels. This measures performance on the synthetic/curated PUSULA pool, not real-world user traffic.",
        "",
        f"Encoder: `{args.model}` @ `{revision}`",
        f"Posts: **{len(rows)}**; unique authors: **{len(set(groups))}**.",
        "",
        "## Existing `tahmin_niyet` vs candidate",
        "",
        "| Evaluation | Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |",
        "|---|---|---:|---:|---:|---:|",
        f"| full pool | existing tahmin_niyet | {current_metrics['dominant_accuracy']:.3f} | {current_metrics['macro_f1']:.3f} | {current_metrics['intent_mae']:.3f} | {current_metrics['mean_cosine_similarity']:.3f} |",
    ]
    for name in ("semantic_knn", "ridge", "hybrid"):
        m = a[name]
        lines.append(f"| author-group 5-fold | {name} | {m['dominant_accuracy']:.3f} | {m['macro_f1']:.3f} | {m['intent_mae']:.3f} | {m['mean_cosine_similarity']:.3f} |")
    c = a["balanced_logistic_dominant"]
    lines += [
        f"| author-group 5-fold | logistic dominant | {c['dominant_accuracy']:.3f} | {c['macro_f1']:.3f} | - | - |",
        "",
        f"Author-group classifier top-50% confidence accuracy: **{c['accuracy_at_50pct_coverage']:.3f}**.",
        "",
        "## Random stratified upper-bound check",
        "",
        "| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("semantic_knn", "ridge", "hybrid"):
        m = r[name]
        lines.append(f"| {name} | {m['dominant_accuracy']:.3f} | {m['macro_f1']:.3f} | {m['intent_mae']:.3f} | {m['mean_cosine_similarity']:.3f} |")
    rc = r["balanced_logistic_dominant"]
    lines += [
        f"| logistic dominant | {rc['dominant_accuracy']:.3f} | {rc['macro_f1']:.3f} | - | - |",
        "",
        "## Clickbait diagnostic",
        "",
        f"`{click_result}`",
        "",
        "Author-group CV is the primary development estimate because no author appears in both train and validation folds. Random stratified CV is shown only as an optimistic upper-bound check for template/style leakage.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "n": len(rows),
        "authors": len(set(groups)),
        "current": current_metrics,
        "author_group": {k: v for k, v in a.items() if k not in ("oof_predictions", "folds")},
        "random": {k: v for k, v in r.items() if k not in ("oof_predictions", "folds")},
        "clickbait": click_result,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
