from __future__ import annotations

import argparse
import gc
import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import KNeighborsRegressor
from transformers import AutoModel, AutoTokenizer

from benchmark_intent_balanced_corpus import load_balanced
from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS

ROOT = Path(__file__).resolve().parents[1]
MODEL_SPECS = [
    {"name": "intfloat/multilingual-e5-small", "prefix": "query: "},
    {"name": "intfloat/multilingual-e5-base", "prefix": "query: "},
    {"name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "prefix": ""},
]


def mean_pool(last_hidden, attention_mask):
    mask = attention_mask.unsqueeze(-1).float()
    return (last_hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)


def encode(texts, model_name, prefix, batch_size=16, max_length=128):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    chunks = []
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch = [prefix + t for t in texts[start:start+batch_size]]
            x = tok(batch, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            out = model(**x)
            emb = mean_pool(out.last_hidden_state, x["attention_mask"])
            emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            chunks.append(emb.cpu().numpy())
    revision = getattr(model.config, "_commit_hash", None)
    hidden = int(model.config.hidden_size)
    del model, tok
    gc.collect()
    return np.vstack(chunks).astype(np.float32), revision, hidden


def sample_weights(dom):
    counts = Counter(dom)
    n = len(dom)
    w = {c: n / (len(INTENTS) * counts[c]) for c in INTENTS}
    return np.asarray([w[x] for x in dom], dtype=float)


def dominant_from_vec(v):
    return np.argmax(v[:, :4], axis=1)


def vec_metrics(y_true, pred, dom_true):
    pred = np.clip(pred, 0, 1)
    dom_pred = dominant_from_vec(pred)
    dom_gold = np.asarray([INTENTS.index(x) for x in dom_true])
    cosine = np.sum(y_true[:, :4] * pred[:, :4], axis=1) / np.maximum(
        np.linalg.norm(y_true[:, :4], axis=1) * np.linalg.norm(pred[:, :4], axis=1), 1e-12
    )
    return {
        "dominant_accuracy": float(accuracy_score(dom_gold, dom_pred)),
        "macro_f1": float(f1_score(dom_gold, dom_pred, labels=list(range(4)), average="macro", zero_division=0)),
        "intent_mae": float(np.mean(np.abs(y_true[:, :4] - pred[:, :4]))),
        "mean_cosine_similarity": float(np.mean(cosine)),
        "clickbait_mae": float(np.mean(np.abs(y_true[:, 4] - pred[:, 4]))),
        "pred_distribution": dict(Counter(INTENTS[i] for i in dom_pred)),
        "per_class_accuracy": {
            cls: float(np.mean(dom_pred[np.where(dom_gold == i)[0]] == i))
            for i, cls in enumerate(INTENTS)
        },
    }


def cls_metrics(dom_true, pred, probs):
    gold = np.asarray([INTENTS.index(x) for x in dom_true])
    pred_idx = np.asarray([INTENTS.index(x) for x in pred])
    correct = pred_idx == gold
    sorted_p = np.sort(probs, axis=1)
    margin = sorted_p[:, -1] - sorted_p[:, -2]
    out = {
        "dominant_accuracy": float(accuracy_score(gold, pred_idx)),
        "macro_f1": float(f1_score(gold, pred_idx, labels=list(range(4)), average="macro", zero_division=0)),
        "pred_distribution": dict(Counter(pred)),
        "per_class_accuracy": {
            cls: float(np.mean(pred_idx[np.where(gold == i)[0]] == i))
            for i, cls in enumerate(INTENTS)
        },
    }
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(gold) * coverage)))
        idx = np.argsort(-margin)[:n]
        out[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def run_heads(x_train, y_train, dom_train, x_test, y_test, dom_test):
    sw = sample_weights(dom_train)

    ridge = Ridge(alpha=6.0)
    ridge.fit(x_train, y_train, sample_weight=sw)
    ridge_pred = np.asarray(ridge.predict(x_test), dtype=float)

    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(x_train, y_train)
    knn_pred = np.asarray(knn.predict(x_test), dtype=float)

    clf = LogisticRegression(C=4.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    clf.fit(x_train, dom_train)
    cls_pred = clf.predict(x_test)
    raw = clf.predict_proba(x_test)
    probs = np.zeros((len(x_test), 4), dtype=float)
    class_to_col = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw[:, class_to_col[cls]]

    hybrid = np.zeros_like(knn_pred)
    hybrid[:, :4] = 0.65 * np.clip(knn_pred[:, :4], 0, 1) + 0.35 * probs
    hybrid[:, 4] = np.clip(knn_pred[:, 4], 0, 1)

    # Convert dominant classifier probabilities into a calibrated-ish four-vector by
    # preserving the average intensity of the semantic regressor.
    prob_vector = np.zeros_like(knn_pred)
    scale = np.clip(np.sum(knn_pred[:, :4], axis=1, keepdims=True), 0.7, 2.4)
    prob_vector[:, :4] = np.clip(probs * scale, 0, 1)
    prob_vector[:, 4] = np.clip(knn_pred[:, 4], 0, 1)

    return {
        "balanced_logistic_dominant": cls_metrics(dom_test, cls_pred, probs),
        "semantic_knn_vector": vec_metrics(y_test, knn_pred, dom_test),
        "weighted_ridge_vector": vec_metrics(y_test, ridge_pred, dom_test),
        "hybrid_knn_logistic_vector": vec_metrics(y_test, hybrid, dom_test),
        "logistic_probability_vector": vec_metrics(y_test, prob_vector, dom_test),
    }


def markdown(result):
    lines = [
        "# Multilingual encoder capacity sweep",
        "",
        "> Development-only. The same 136 assistant-authored balanced training examples and the same 48 single-annotator hard-style development examples are used for every encoder.",
        "",
        "| Encoder | Hidden | Logistic acc. | Logistic macro-F1 | Top-50% acc. | Best vector MAE | Best vector cosine |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, r in result["models"].items():
        c = r["heads"]["balanced_logistic_dominant"]
        vector_heads = [v for k, v in r["heads"].items() if "vector" in k]
        best_mae = min(v["intent_mae"] for v in vector_heads)
        best_cos = max(v["mean_cosine_similarity"] for v in vector_heads)
        lines.append(
            f"| {name} | {r['hidden_size']} | {c['dominant_accuracy']:.3f} | {c['macro_f1']:.3f} | "
            f"{c['accuracy_at_50pct_coverage']:.3f} | {best_mae:.3f} | {best_cos:.3f} |"
        )
    lines += [
        "",
        "## Guardrail",
        "",
        "This is an architecture-selection benchmark on an already-used development set. It is useful for choosing an encoder, not for a final competition claim.",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="experiments/results/encoder_sweep.json")
    ap.add_argument("--summary", default="experiments/results/encoder_sweep.md")
    args = ap.parse_args()

    train = load_balanced()
    hard = load_hard_eval()
    texts = [r["text"] for r in train] + [r["text"] for r in hard]
    n = len(train)
    y_train = np.asarray([r["y"] for r in train], dtype=float)
    y_test = np.asarray([r["y"] for r in hard], dtype=float)
    dom_train = np.asarray([r["dominant"] for r in train])
    dom_test = np.asarray([r["dominant"] for r in hard])

    result = {
        "status": "development_only_not_final_gold",
        "train_n": len(train),
        "test_n": len(hard),
        "train_distribution": dict(Counter(dom_train)),
        "test_distribution": dict(Counter(dom_test)),
        "models": {},
    }

    for spec in MODEL_SPECS:
        x, revision, hidden = encode(texts, spec["name"], spec["prefix"])
        heads = run_heads(x[:n], y_train, dom_train, x[n:], y_test, dom_test)
        result["models"][spec["name"]] = {
            "revision": revision,
            "prefix": spec["prefix"],
            "hidden_size": hidden,
            "heads": heads,
        }
        compact = heads["balanced_logistic_dominant"]
        print(json.dumps({
            "model": spec["name"],
            "revision": revision,
            "hidden_size": hidden,
            "logistic_accuracy": compact["dominant_accuracy"],
            "macro_f1": compact["macro_f1"],
            "accuracy_at_50pct_coverage": compact["accuracy_at_50pct_coverage"],
            "hybrid": heads["hybrid_knn_logistic_vector"],
        }, ensure_ascii=False, indent=2))

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / args.summary).write_text(markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
