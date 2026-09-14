from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsRegressor

from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS, cosine_rows, dominant_from_scores, encode_texts, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
OLD_BALANCED = ROOT / "data/dev_labels/intent_balanced_training_v1.jsonl"
V3_V1_FILES = [
    ROOT / "data/v3_realistic/train_ogretici_v1.jsonl",
    ROOT / "data/v3_realistic/train_eglendirici_v1.jsonl",
    ROOT / "data/v3_realistic/train_haber_v1.jsonl",
    ROOT / "data/v3_realistic/train_sosyal_v1.jsonl",
]
V3_V2_FILES = [
    ROOT / "data/v3_realistic/train_ogretici_v2.jsonl",
    ROOT / "data/v3_realistic/train_eglendirici_v2.jsonl",
    ROOT / "data/v3_realistic/train_haber_v2.jsonl",
    ROOT / "data/v3_realistic/train_sosyal_v2.jsonl",
]


def load_old():
    rows = []
    for r in read_jsonl(OLD_BALANCED):
        rows.append(
            {
                "id": r["id"],
                "text": r["text"],
                "dominant": r["dominant_intent"],
                "y": [float(r["intent"][k]) for k in INTENTS] + [float(r["clickbait"])],
                "source": "balanced136_v1",
            }
        )
    return rows


def load_v3(paths, source):
    rows = []
    for path in paths:
        for r in read_jsonl(path):
            rows.append(
                {
                    "id": r["id"],
                    "text": r["metin"],
                    "dominant": r["dominant_intent"],
                    "y": [float(x) for x in r["gercek_niyet"]] + [float(r["clickbait"])],
                    "source": source,
                }
            )
    return rows


def vec_metrics(y_true, pred, dom_true):
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
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(pred) * coverage)))
        idx = np.argsort(-margin)[:n]
        out[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def fit_classifier(x_train, d_train, x_test, d_test):
    clf = LogisticRegression(
        C=4.0,
        class_weight="balanced",
        max_iter=5000,
        solver="lbfgs",
        random_state=42,
    )
    clf.fit(x_train, d_train)
    d_pred = clf.predict(x_test)
    raw_probs = clf.predict_proba(x_test)
    probs = np.zeros((len(x_test), 4), dtype=float)
    cmap = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw_probs[:, cmap[cls]]
    return clf, d_pred, probs, cls_metrics(d_test, d_pred.tolist(), probs)


def margin_aware_classifiers(x_train, y_train, d_train, x_test, d_test):
    intent = np.asarray(y_train[:, :4], dtype=float)
    sorted_scores = np.sort(intent, axis=1)
    label_margin = sorted_scores[:, -1] - sorted_scores[:, -2]
    out = {}
    for threshold in (0.15, 0.25, 0.35):
        keep = label_margin >= threshold
        kept_classes = Counter(d_train[keep])
        if not all(kept_classes.get(cls, 0) >= 2 for cls in INTENTS):
            continue
        _, _, _, metrics = fit_classifier(x_train[keep], d_train[keep], x_test, d_test)
        out[f"margin_{threshold:.2f}"] = {
            "label_margin_threshold": threshold,
            "train_n": int(np.sum(keep)),
            "train_distribution": dict(kept_classes),
            **metrics,
        }
    return out


def train_eval(x_train, y_train, d_train, x_test, y_test, d_test):
    # Fixed k isolates training-data effects in the 128-vs-256 comparison.
    k = 7
    knn = KNeighborsRegressor(n_neighbors=k, weights="distance", metric="cosine")
    knn.fit(x_train, y_train)
    p_knn = np.asarray(knn.predict(x_test), dtype=float)

    _, d_pred, probs, standard_cls = fit_classifier(x_train, d_train, x_test, d_test)

    hybrid = np.zeros_like(p_knn)
    hybrid[:, :4] = 0.72 * np.clip(p_knn[:, :4], 0, 1) + 0.28 * probs
    hybrid[:, 4] = np.clip(p_knn[:, 4], 0, 1)

    sim_train = x_train @ x_train.T
    np.fill_diagonal(sim_train, -1.0)
    threshold = float(np.quantile(np.max(sim_train, axis=1), 0.10))
    nearest = np.max(x_test @ x_train.T, axis=1)

    return {
        "train_n": int(len(x_train)),
        "train_distribution": dict(Counter(d_train)),
        "knn_k": int(k),
        "semantic_knn": vec_metrics(y_test, p_knn, d_test),
        "hybrid_vector": vec_metrics(y_test, hybrid, d_test),
        "balanced_logistic_dominant": standard_cls,
        "margin_aware_dominant": margin_aware_classifiers(
            x_train, y_train, d_train, x_test, d_test
        ),
        "ood": {
            "threshold": threshold,
            "ood_rate": float(np.mean(nearest < threshold)),
            "mean_nearest_train_cosine": float(np.mean(nearest)),
            "min_nearest_train_cosine": float(np.min(nearest)),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-base")
    ap.add_argument("--output", default="experiments/results/dataset_v3_e5_base.json")
    ap.add_argument("--summary", default="experiments/results/dataset_v3_e5_base.md")
    args = ap.parse_args()

    old = load_old()
    v3_128 = load_v3(V3_V1_FILES, "dataset_v3_tranche1")
    v3_second = load_v3(V3_V2_FILES, "dataset_v3_tranche2")
    v3_256 = v3_128 + v3_second
    hard = load_hard_eval()

    if len(old) != 136:
        raise SystemExit(f"expected 136 old balanced rows, got {len(old)}")
    if len(v3_128) != 128:
        raise SystemExit(f"expected 128 v3 tranche-1 rows, got {len(v3_128)}")
    if len(v3_second) != 128:
        raise SystemExit(f"expected 128 v3 tranche-2 rows, got {len(v3_second)}")
    if len(v3_256) != 256:
        raise SystemExit(f"expected 256 v3 rows, got {len(v3_256)}")
    if len(hard) != 48:
        raise SystemExit(f"expected 48 hard rows, got {len(hard)}")

    all_rows = old + v3_256 + hard
    x, revision = encode_texts([r["text"] for r in all_rows], args.model, batch_size=16)
    n_old, n_v3 = len(old), len(v3_256)
    xo = x[:n_old]
    xv256 = x[n_old:n_old+n_v3]
    xv128 = xv256[:128]
    xh = x[n_old+n_v3:]

    yo = np.asarray([r["y"] for r in old], dtype=float)
    yv256 = np.asarray([r["y"] for r in v3_256], dtype=float)
    yv128 = yv256[:128]
    yh = np.asarray([r["y"] for r in hard], dtype=float)
    do = np.asarray([r["dominant"] for r in old])
    dv256 = np.asarray([r["dominant"] for r in v3_256])
    dv128 = dv256[:128]
    dh = np.asarray([r["dominant"] for r in hard])

    scenarios = {
        "old_136_only": train_eval(xo, yo, do, xh, yh, dh),
        "v3_128_only": train_eval(xv128, yv128, dv128, xh, yh, dh),
        "v3_256_only": train_eval(xv256, yv256, dv256, xh, yh, dh),
    }

    result = {
        "status": "development_only_hard48_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "hard_eval_n": len(hard),
        "hard_distribution": dict(Counter(dh)),
        "scenarios": scenarios,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Dataset V3 + multilingual-e5-base development benchmark",
        "",
        "> Development-only. The hard-48 set is repeatedly inspected and is not final competition gold.",
        "",
        f"Encoder: `{args.model}` @ `{revision}`",
        "",
        "All scenarios use the same frozen encoder, classifier settings and k-NN k=7. The old 2,000-post templated pool is excluded.",
        "",
        "| Training source | Classifier acc. | Classifier F1 | Top-50% conf. acc. | Hybrid acc. | Hybrid F1 | Hybrid 4D MAE | Hybrid cosine |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in ("old_136_only", "v3_128_only", "v3_256_only"):
        r = scenarios[key]
        c = r["balanced_logistic_dominant"]
        h = r["hybrid_vector"]
        lines.append(
            f"| {key} | {c['dominant_accuracy']:.3f} | {c['macro_f1']:.3f} | "
            f"{c['accuracy_at_50pct_coverage']:.3f} | {h['dominant_accuracy']:.3f} | "
            f"{h['macro_f1']:.3f} | {h['intent_mae']:.3f} | {h['mean_cosine_similarity']:.3f} |"
        )

    lines += ["", "## Margin-aware dominant classifier", ""]
    for key in ("v3_128_only", "v3_256_only"):
        lines.append(f"### {key}")
        lines.append("")
        lines.append("| Label margin | Train n | Accuracy | Macro-F1 | Top-50% conf. acc. |")
        lines.append("|---:|---:|---:|---:|---:|")
        for name, m in scenarios[key]["margin_aware_dominant"].items():
            lines.append(
                f"| {m['label_margin_threshold']:.2f} | {m['train_n']} | "
                f"{m['dominant_accuracy']:.3f} | {m['macro_f1']:.3f} | "
                f"{m['accuracy_at_50pct_coverage']:.3f} |"
            )
        lines.append("")

    lines += [
        "## Policy",
        "",
        "V3 tranche 2 deliberately targets teaching↔social and entertainment↔social boundary cases instead of merely adding more easy examples.",
        "Ambiguous rows remain valuable for the 4D vector head. Margin-aware experiments test whether they should be excluded only from the auxiliary single-dominant classifier.",
        "The old 2,000-post templated pool remains a baseline/demo fixture only and is not used to train these candidate models.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
