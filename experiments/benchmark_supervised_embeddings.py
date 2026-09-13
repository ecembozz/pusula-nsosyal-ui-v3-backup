from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
INTENTS = ["ogretici", "eglendirici", "haber", "sosyal"]
LABEL_FILE = ROOT / "data/gold_eval/draft_labels_annotator_a.jsonl"
TEXT_FILES = [
    ROOT / "data/gold_eval/candidate_hard_cases.jsonl",
    ROOT / "data/gold_eval/candidate_news_cases.jsonl",
]


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_dataset():
    texts = {}
    for path in TEXT_FILES:
        for row in read_jsonl(path):
            texts[row["id"]] = row["text"]

    rows = []
    for label in read_jsonl(LABEL_FILE):
        if label["id"] not in texts:
            raise KeyError(f"Text missing for {label['id']}")
        rows.append(
            {
                "id": label["id"],
                "text": texts[label["id"]],
                "dominant": label["dominant_intent"],
                "y": [float(label["intent"][k]) for k in INTENTS]
                + [float(label["clickbait"])],
            }
        )
    return rows


def mean_pool(last_hidden, attention_mask):
    mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
    summed = torch.sum(last_hidden * mask, dim=1)
    denom = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / denom


def encode_texts(texts, model_name: str, batch_size: int = 16):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    device = torch.device("cpu")
    model.to(device)

    chunks = []
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch = ["query: " + t for t in texts[start : start + batch_size]]
            toks = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=192,
                return_tensors="pt",
            ).to(device)
            out = model(**toks)
            emb = mean_pool(out.last_hidden_state, toks["attention_mask"])
            emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            chunks.append(emb.cpu().numpy())

    revision = getattr(model.config, "_commit_hash", None)
    return np.vstack(chunks).astype(np.float32), revision


def cosine_rows(a, b):
    na = np.linalg.norm(a, axis=1)
    nb = np.linalg.norm(b, axis=1)
    den = np.maximum(na * nb, 1e-12)
    return np.sum(a * b, axis=1) / den


def dominant_from_scores(scores):
    return [INTENTS[int(i)] for i in np.argmax(scores[:, :4], axis=1)]


def metrics(y_true, y_pred, dom_true):
    y_pred = np.clip(y_pred, 0.0, 1.0)
    dom_pred = dominant_from_scores(y_pred)
    intent_mae = float(np.mean(np.abs(y_true[:, :4] - y_pred[:, :4])))
    clickbait_mae = float(np.mean(np.abs(y_true[:, 4] - y_pred[:, 4])))
    cos = float(np.mean(cosine_rows(y_true[:, :4], y_pred[:, :4])))
    return {
        "dominant_accuracy": float(accuracy_score(dom_true, dom_pred)),
        "macro_f1": float(f1_score(dom_true, dom_pred, labels=INTENTS, average="macro", zero_division=0)),
        "intent_mae": intent_mae,
        "mean_cosine_similarity": cos,
        "clickbait_mae": clickbait_mae,
        "pred_distribution": dict(Counter(dom_pred)),
    }


def confidence_report(y_pred, nearest_sim, ood_flags, dom_true):
    y_pred = np.clip(y_pred, 0.0, 1.0)
    dom_pred = dominant_from_scores(y_pred)
    scores = np.sort(y_pred[:, :4], axis=1)
    margin = np.clip(scores[:, -1] - scores[:, -2], 0.0, 1.0)

    # Similarity mostly lives in a high range for normalized multilingual embeddings.
    # This simple transform is deliberately transparent and is NOT a calibrated probability.
    proximity = np.clip((nearest_sim - 0.45) / 0.55, 0.0, 1.0)
    confidence = 0.65 * proximity + 0.35 * margin

    correct = np.asarray([a == b for a, b in zip(dom_true, dom_pred)], dtype=bool)
    report = {
        "mean_confidence": float(np.mean(confidence)),
        "ood_rate": float(np.mean(ood_flags)),
        "id_accuracy": float(np.mean(correct[~ood_flags])) if np.any(~ood_flags) else None,
        "ood_accuracy": float(np.mean(correct[ood_flags])) if np.any(ood_flags) else None,
    }
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(confidence) * coverage)))
        idx = np.argsort(-confidence)[:n]
        report[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
        report[f"confidence_threshold_{int(coverage*100)}pct"] = float(confidence[idx[-1]])
    return report


def build_estimators(n_train):
    n_neighbors = min(5, max(2, n_train // 6))
    pca_components = min(16, max(4, n_train - 2))
    return {
        "ridge": Ridge(alpha=12.0),
        "semantic_knn": KNeighborsRegressor(
            n_neighbors=n_neighbors,
            weights="distance",
            metric="cosine",
        ),
        "pca_mlp": Pipeline(
            [
                ("pca", PCA(n_components=pca_components, random_state=42)),
                ("scale", StandardScaler()),
                (
                    "mlp",
                    MLPRegressor(
                        hidden_layer_sizes=(32,),
                        alpha=0.05,
                        learning_rate_init=0.002,
                        max_iter=2500,
                        random_state=42,
                    ),
                ),
            ]
        ),
    }


def cross_validate(x, y, dom, ids):
    skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
    all_results = {}

    for model_name in ("ridge", "semantic_knn", "pca_mlp"):
        oof = np.zeros_like(y, dtype=float)
        nearest = np.zeros(len(y), dtype=float)
        ood = np.zeros(len(y), dtype=bool)
        folds = []

        for fold, (tr, va) in enumerate(skf.split(x, dom), start=1):
            estimators = build_estimators(len(tr))
            estimator = estimators[model_name]
            estimator.fit(x[tr], y[tr])
            pred = np.asarray(estimator.predict(x[va]), dtype=float)
            oof[va] = pred

            train_sim = x[tr] @ x[tr].T
            np.fill_diagonal(train_sim, -1.0)
            train_nearest = np.max(train_sim, axis=1)
            threshold = float(np.quantile(train_nearest, 0.10))

            val_sim = x[va] @ x[tr].T
            val_nearest = np.max(val_sim, axis=1)
            nearest[va] = val_nearest
            ood[va] = val_nearest < threshold

            folds.append(
                {
                    "fold": fold,
                    "n_train": int(len(tr)),
                    "n_val": int(len(va)),
                    "ood_threshold": threshold,
                    "val_ids": [ids[i] for i in va],
                }
            )

        base = metrics(y, oof, dom)
        base["confidence_ood"] = confidence_report(oof, nearest, ood, dom)
        base["folds"] = folds
        base["rows"] = [
            {
                "id": ids[i],
                "gold_dominant": dom[i],
                "pred_dominant": dominant_from_scores(oof[i : i + 1])[0],
                "nearest_train_cosine": float(nearest[i]),
                "ood": bool(ood[i]),
                "gold_vector": [float(v) for v in y[i, :4]],
                "pred_vector": [float(v) for v in np.clip(oof[i, :4], 0, 1)],
                "gold_clickbait": float(y[i, 4]),
                "pred_clickbait": float(np.clip(oof[i, 4], 0, 1)),
            }
            for i in range(len(y))
        ]
        all_results[model_name] = base

    return all_results


def markdown_summary(result):
    lines = [
        "# Supervised multilingual embedding pilot",
        "",
        "> Development-only result. The 48 labels are single-annotator draft labels and are not final competition gold.",
        "",
        f"Embedding model: `{result['embedding_model']}`",
        f"Embedding revision: `{result.get('embedding_revision')}`",
        f"Examples: **{result['n']}**; evaluation: **4-fold stratified out-of-fold CV**.",
        "",
        "| Head | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE | OOD rate | Acc @ 50% conf. |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, r in result["models"].items():
        c = r["confidence_ood"]
        lines.append(
            f"| {name} | {r['dominant_accuracy']:.3f} | {r['macro_f1']:.3f} | {r['intent_mae']:.3f} | "
            f"{r['mean_cosine_similarity']:.3f} | {r['clickbait_mae']:.3f} | {c['ood_rate']:.3f} | "
            f"{c['accuracy_at_50pct_coverage']:.3f} |"
        )
    lines += [
        "",
        "## Interpretation rules",
        "",
        "- This pilot only tests whether supervised semantic embeddings are promising on the current 48-case development set.",
        "- OOD is based on fold-local nearest-neighbour cosine similarity; it is a transparent screening signal, not a calibrated probability.",
        "- No result from this file should be presented as final competition performance.",
        "- If a supervised head shows a meaningful gain, expand the independently written labeled development corpus before tuning further.",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--output", default="experiments/results/supervised_embedding_cv.json")
    ap.add_argument("--summary", default="experiments/results/supervised_embedding_cv.md")
    args = ap.parse_args()

    rows = load_dataset()
    ids = [r["id"] for r in rows]
    texts = [r["text"] for r in rows]
    dom = np.asarray([r["dominant"] for r in rows])
    y = np.asarray([r["y"] for r in rows], dtype=float)

    x, revision = encode_texts(texts, args.model)
    models = cross_validate(x, y, dom, ids)

    result = {
        "status": "development_only_single_annotator_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "n": len(rows),
        "gold_distribution": dict(Counter(dom)),
        "evaluation": "4-fold stratified out-of-fold cross-validation",
        "models": models,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = ROOT / args.summary
    summary.write_text(markdown_summary(result), encoding="utf-8")

    compact = {
        "embedding_model": result["embedding_model"],
        "embedding_revision": result["embedding_revision"],
        "n": result["n"],
        "gold_distribution": result["gold_distribution"],
        "models": {
            k: {
                "dominant_accuracy": v["dominant_accuracy"],
                "macro_f1": v["macro_f1"],
                "intent_mae": v["intent_mae"],
                "mean_cosine_similarity": v["mean_cosine_similarity"],
                "clickbait_mae": v["clickbait_mae"],
                "confidence_ood": v["confidence_ood"],
            }
            for k, v in models.items()
        },
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
