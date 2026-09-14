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
V3_FILES = [
    ROOT / "data/v3_realistic/train_ogretici_v1.jsonl",
    ROOT / "data/v3_realistic/train_eglendirici_v1.jsonl",
    ROOT / "data/v3_realistic/train_haber_v1.jsonl",
    ROOT / "data/v3_realistic/train_sosyal_v1.jsonl",
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


def load_v3():
    rows = []
    for path in V3_FILES:
        for r in read_jsonl(path):
            rows.append(
                {
                    "id": r["id"],
                    "text": r["metin"],
                    "dominant": r["dominant_intent"],
                    "y": [float(x) for x in r["gercek_niyet"]] + [float(r["clickbait"])],
                    "source": "dataset_v3_realistic",
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


def train_eval(x_train, y_train, d_train, x_test, y_test, d_test):
    k = min(11, max(5, len(x_train) // 24))
    knn = KNeighborsRegressor(n_neighbors=k, weights="distance", metric="cosine")
    knn.fit(x_train, y_train)
    p_knn = np.asarray(knn.predict(x_test), dtype=float)

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
        "balanced_logistic_dominant": cls_metrics(d_test, d_pred.tolist(), probs),
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
    v3 = load_v3()
    hard = load_hard_eval()
    if len(old) != 136:
        raise SystemExit(f"expected 136 old balanced rows, got {len(old)}")
    if len(v3) != 128:
        raise SystemExit(f"expected 128 v3 rows, got {len(v3)}")
    if len(hard) != 48:
        raise SystemExit(f"expected 48 hard rows, got {len(hard)}")

    all_rows = old + v3 + hard
    x, revision = encode_texts([r["text"] for r in all_rows], args.model, batch_size=16)
    n_old, n_v3 = len(old), len(v3)
    xo = x[:n_old]
    xv = x[n_old:n_old+n_v3]
    xh = x[n_old+n_v3:]

    yo = np.asarray([r["y"] for r in old], dtype=float)
    yv = np.asarray([r["y"] for r in v3], dtype=float)
    yh = np.asarray([r["y"] for r in hard], dtype=float)
    do = np.asarray([r["dominant"] for r in old])
    dv = np.asarray([r["dominant"] for r in v3])
    dh = np.asarray([r["dominant"] for r in hard])

    scenarios = {
        "old_136_only": train_eval(xo, yo, do, xh, yh, dh),
        "v3_128_only": train_eval(xv, yv, dv, xh, yh, dh),
        "combined_264": train_eval(
            np.vstack([xo, xv]),
            np.vstack([yo, yv]),
            np.concatenate([do, dv]),
            xh, yh, dh,
        ),
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
        "| Training source | Classifier acc. | Classifier F1 | Top-50% conf. acc. | Hybrid acc. | Hybrid F1 | Hybrid 4D MAE | Hybrid cosine |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in ("old_136_only", "v3_128_only", "combined_264"):
        r = scenarios[key]
        c = r["balanced_logistic_dominant"]
        h = r["hybrid_vector"]
        lines.append(
            f"| {key} | {c['dominant_accuracy']:.3f} | {c['macro_f1']:.3f} | "
            f"{c['accuracy_at_50pct_coverage']:.3f} | {h['dominant_accuracy']:.3f} | "
            f"{h['macro_f1']:.3f} | {h['intent_mae']:.3f} | {h['mean_cosine_similarity']:.3f} |"
        )
    lines += [
        "",
        "## Policy",
        "",
        "The old 2,000-post templated pool is intentionally excluded from these training scenarios. It remains a baseline/demo fixture only.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
