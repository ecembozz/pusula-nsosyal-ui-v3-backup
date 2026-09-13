from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

from benchmark_supervised_embeddings import (
    INTENTS,
    build_estimators,
    cosine_rows,
    dominant_from_scores,
    encode_texts,
    read_jsonl,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_POSTS = ROOT / "data/v2_realistic/raw_posts.jsonl"
RAW_LABELS = ROOT / "data/dev_labels/raw_training_draft_annotator_a_v1.jsonl"
NEWS_TRAIN = ROOT / "data/dev_labels/news_training_draft_annotator_a_v1.jsonl"
HARD_LABELS = ROOT / "data/gold_eval/draft_labels_annotator_a.jsonl"
HARD_TEXTS = [
    ROOT / "data/gold_eval/candidate_hard_cases.jsonl",
    ROOT / "data/gold_eval/candidate_news_cases.jsonl",
]


def label_to_y(row):
    return [float(row["intent"][k]) for k in INTENTS] + [float(row["clickbait"])]


def load_base_training():
    raw_map = {r["id"]: r for r in read_jsonl(RAW_POSTS)}
    rows = []
    for lab in read_jsonl(RAW_LABELS):
        src = raw_map[lab["id"]]
        rows.append(
            {
                "id": lab["id"],
                "text": src["text"],
                "dominant": lab["dominant_intent"],
                "y": label_to_y(lab),
                "source": "raw_realistic_synthetic",
                "topic_family": src.get("topic_family"),
            }
        )
    for lab in read_jsonl(NEWS_TRAIN):
        rows.append(
            {
                "id": lab["id"],
                "text": lab["text"],
                "dominant": lab["dominant_intent"],
                "y": label_to_y(lab),
                "source": "synthetic_news_training",
                "topic_family": "news_training",
            }
        )
    return rows


def load_hard_eval():
    meta = {}
    for path in HARD_TEXTS:
        for row in read_jsonl(path):
            meta[row["id"]] = row
    rows = []
    for lab in read_jsonl(HARD_LABELS):
        src = meta[lab["id"]]
        rows.append(
            {
                "id": lab["id"],
                "text": src["text"],
                "dominant": lab["dominant_intent"],
                "y": label_to_y(lab),
                "challenge": list(src.get("challenge", [])),
            }
        )
    return rows


def metric_block(y_true, y_pred, dom_true):
    pred = np.clip(np.asarray(y_pred, dtype=float), 0.0, 1.0)
    dom_pred = dominant_from_scores(pred)
    return {
        "dominant_accuracy": float(accuracy_score(dom_true, dom_pred)),
        "macro_f1": float(
            f1_score(dom_true, dom_pred, labels=INTENTS, average="macro", zero_division=0)
        ),
        "intent_mae": float(np.mean(np.abs(y_true[:, :4] - pred[:, :4]))),
        "mean_cosine_similarity": float(
            np.mean(cosine_rows(y_true[:, :4], pred[:, :4]))
        ),
        "clickbait_mae": float(np.mean(np.abs(y_true[:, 4] - pred[:, 4]))),
        "pred_distribution": dict(Counter(dom_pred)),
    }


def ood_threshold(x_train):
    sim = x_train @ x_train.T
    np.fill_diagonal(sim, -1.0)
    nearest = np.max(sim, axis=1)
    return float(np.quantile(nearest, 0.10))


def selective_report(y_pred, y_true, dom_true, nearest, threshold):
    pred = np.clip(y_pred, 0.0, 1.0)
    dom_pred = dominant_from_scores(pred)
    correct = np.asarray([a == b for a, b in zip(dom_true, dom_pred)], dtype=bool)
    sorted_scores = np.sort(pred[:, :4], axis=1)
    margin = np.clip(sorted_scores[:, -1] - sorted_scores[:, -2], 0, 1)
    proximity = np.clip((nearest - 0.45) / 0.55, 0, 1)
    confidence = 0.65 * proximity + 0.35 * margin
    ood = nearest < threshold
    result = {
        "ood_threshold": float(threshold),
        "ood_rate": float(np.mean(ood)),
        "id_accuracy": float(np.mean(correct[~ood])) if np.any(~ood) else None,
        "ood_accuracy": float(np.mean(correct[ood])) if np.any(ood) else None,
        "mean_nearest_train_cosine": float(np.mean(nearest)),
    }
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(confidence) * coverage)))
        idx = np.argsort(-confidence)[:n]
        result[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return result


def per_class_report(y_true, y_pred, dom_true):
    pred_dom = dominant_from_scores(np.clip(y_pred, 0, 1))
    out = {}
    for cls in INTENTS:
        idx = np.where(np.asarray(dom_true) == cls)[0]
        if len(idx) == 0:
            continue
        out[cls] = {
            "n": int(len(idx)),
            "accuracy": float(np.mean([pred_dom[i] == cls for i in idx])),
            "intent_mae": float(np.mean(np.abs(y_true[idx, :4] - y_pred[idx, :4]))),
        }
    return out


def challenge_report(hard_rows, y_true, y_pred, dom_true):
    bucket = defaultdict(list)
    for i, row in enumerate(hard_rows):
        for tag in row.get("challenge", []):
            bucket[tag].append(i)
    pred_dom = dominant_from_scores(np.clip(y_pred, 0, 1))
    out = {}
    for tag, idxs in sorted(bucket.items()):
        if len(idxs) < 3:
            continue
        idx = np.asarray(idxs, dtype=int)
        out[tag] = {
            "n": int(len(idx)),
            "dominant_accuracy": float(
                np.mean([pred_dom[i] == dom_true[i] for i in idx])
            ),
            "intent_mae": float(np.mean(np.abs(y_true[idx, :4] - y_pred[idx, :4]))),
        }
    return out


def fit_predict_heads(x_train, y_train, x_test):
    preds = {}
    estimators = build_estimators(len(x_train))
    for name, estimator in estimators.items():
        estimator.fit(x_train, y_train)
        preds[name] = np.asarray(estimator.predict(x_test), dtype=float)
    return preds


def scenario_base_only(x_base, y_base, x_hard, y_hard, dom_hard, hard_rows):
    threshold = ood_threshold(x_base)
    nearest = np.max(x_hard @ x_base.T, axis=1)
    out = {}
    for name, pred in fit_predict_heads(x_base, y_base, x_hard).items():
        clipped = np.clip(pred, 0, 1)
        block = metric_block(y_hard, clipped, dom_hard)
        block["selective_ood"] = selective_report(clipped, y_hard, dom_hard, nearest, threshold)
        block["per_class"] = per_class_report(y_hard, clipped, dom_hard)
        block["by_challenge"] = challenge_report(hard_rows, y_hard, clipped, dom_hard)
        out[name] = block
    return out


def scenario_half_target_adaptation(x_base, y_base, x_hard, y_hard, dom_hard, hard_rows):
    splitter = StratifiedKFold(n_splits=2, shuffle=True, random_state=42)
    model_names = ["ridge", "semantic_knn", "pca_mlp"]
    oof = {name: np.zeros_like(y_hard, dtype=float) for name in model_names}
    nearest_all = np.zeros(len(y_hard), dtype=float)
    threshold_all = np.zeros(len(y_hard), dtype=float)

    for hard_train_idx, hard_val_idx in splitter.split(x_hard, dom_hard):
        x_train = np.vstack([x_base, x_hard[hard_train_idx]])
        y_train = np.vstack([y_base, y_hard[hard_train_idx]])
        threshold = ood_threshold(x_train)
        nearest = np.max(x_hard[hard_val_idx] @ x_train.T, axis=1)
        nearest_all[hard_val_idx] = nearest
        threshold_all[hard_val_idx] = threshold

        preds = fit_predict_heads(x_train, y_train, x_hard[hard_val_idx])
        for name in model_names:
            oof[name][hard_val_idx] = preds[name]

    out = {}
    # Fold-local thresholds vary slightly; selective_report needs row-specific OOD.
    for name in model_names:
        clipped = np.clip(oof[name], 0, 1)
        block = metric_block(y_hard, clipped, dom_hard)
        dom_pred = dominant_from_scores(clipped)
        correct = np.asarray([a == b for a, b in zip(dom_hard, dom_pred)], dtype=bool)
        sorted_scores = np.sort(clipped[:, :4], axis=1)
        margin = np.clip(sorted_scores[:, -1] - sorted_scores[:, -2], 0, 1)
        proximity = np.clip((nearest_all - 0.45) / 0.55, 0, 1)
        confidence = 0.65 * proximity + 0.35 * margin
        ood = nearest_all < threshold_all
        selective = {
            "ood_rate": float(np.mean(ood)),
            "id_accuracy": float(np.mean(correct[~ood])) if np.any(~ood) else None,
            "ood_accuracy": float(np.mean(correct[ood])) if np.any(ood) else None,
            "mean_nearest_train_cosine": float(np.mean(nearest_all)),
        }
        for coverage in (0.50, 0.75):
            n = max(1, int(round(len(confidence) * coverage)))
            idx = np.argsort(-confidence)[:n]
            selective[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
        block["selective_ood"] = selective
        block["per_class"] = per_class_report(y_hard, clipped, dom_hard)
        block["by_challenge"] = challenge_report(hard_rows, y_hard, clipped, dom_hard)
        out[name] = block
    return out


def summary_md(result):
    lines = [
        "# Cross-style generalization pilot",
        "",
        "> Development-only. All labels are single-annotator drafts; this is not final competition gold.",
        "",
        f"Embedding: `{result['embedding_model']}` @ `{result.get('embedding_revision')}`",
        f"Base training examples: **{result['base_train_n']}**; hard-style evaluation examples: **{result['hard_eval_n']}**.",
        "",
        "Scenario A = train only on 80 topic/style-balanced raw posts + 16 independent synthetic news posts, then test on all 48 hand-written hard cases.",
        "",
        "Scenario B = the same 96 base examples plus half of the hard-style examples in each 2-fold split, evaluated out-of-fold on the other half.",
        "",
    ]
    for scenario_key, title in [
        ("base_only", "Scenario A — zero target-style supervision"),
        ("half_target_adaptation", "Scenario B — small target-style adaptation"),
    ]:
        lines += [
            f"## {title}",
            "",
            "| Head | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | OOD rate | Acc @ 50% conf. |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for name, r in result["scenarios"][scenario_key].items():
            s = r["selective_ood"]
            lines.append(
                f"| {name} | {r['dominant_accuracy']:.3f} | {r['macro_f1']:.3f} | {r['intent_mae']:.3f} | "
                f"{r['mean_cosine_similarity']:.3f} | {s['ood_rate']:.3f} | {s['accuracy_at_50pct_coverage']:.3f} |"
            )
        lines.append("")
    lines += [
        "## Reading this result",
        "",
        "- Scenario A is the direct answer to whether a model trained on more regular social posts can transfer to slang, irony, mixed intent and other harder styles.",
        "- Scenario B shows how much a modest amount of target-style labeling helps without fine-tuning the multilingual encoder itself.",
        "- OOD is a nearest-embedding screening signal, not a probability of correctness.",
        "- Final claims require independently double-annotated held-out data that was not used in this development cycle.",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--output", default="experiments/results/style_generalization.json")
    ap.add_argument("--summary", default="experiments/results/style_generalization.md")
    args = ap.parse_args()

    base = load_base_training()
    hard = load_hard_eval()
    texts = [r["text"] for r in base] + [r["text"] for r in hard]
    x_all, revision = encode_texts(texts, args.model)
    n_base = len(base)
    x_base, x_hard = x_all[:n_base], x_all[n_base:]
    y_base = np.asarray([r["y"] for r in base], dtype=float)
    y_hard = np.asarray([r["y"] for r in hard], dtype=float)
    dom_base = np.asarray([r["dominant"] for r in base])
    dom_hard = np.asarray([r["dominant"] for r in hard])

    result = {
        "status": "development_only_single_annotator_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "base_train_n": n_base,
        "hard_eval_n": len(hard),
        "base_train_distribution": dict(Counter(dom_base)),
        "hard_eval_distribution": dict(Counter(dom_hard)),
        "scenarios": {
            "base_only": scenario_base_only(x_base, y_base, x_hard, y_hard, dom_hard, hard),
            "half_target_adaptation": scenario_half_target_adaptation(
                x_base, y_base, x_hard, y_hard, dom_hard, hard
            ),
        },
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = ROOT / args.summary
    summary.write_text(summary_md(result), encoding="utf-8")

    compact = {
        "embedding_model": result["embedding_model"],
        "embedding_revision": result["embedding_revision"],
        "base_train_n": result["base_train_n"],
        "base_train_distribution": result["base_train_distribution"],
        "hard_eval_n": result["hard_eval_n"],
        "scenarios": {
            s: {
                m: {
                    "dominant_accuracy": r["dominant_accuracy"],
                    "macro_f1": r["macro_f1"],
                    "intent_mae": r["intent_mae"],
                    "mean_cosine_similarity": r["mean_cosine_similarity"],
                    "ood_rate": r["selective_ood"]["ood_rate"],
                    "accuracy_at_50pct_coverage": r["selective_ood"]["accuracy_at_50pct_coverage"],
                }
                for m, r in result["scenarios"][s].items()
            }
            for s in result["scenarios"]
        },
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
