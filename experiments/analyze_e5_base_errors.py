from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

from benchmark_encoder_sweep import encode
from benchmark_intent_balanced_corpus import load_balanced
from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS

ROOT = Path(__file__).resolve().parents[1]
MODEL = "intfloat/multilingual-e5-base"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="experiments/results/e5_base_error_analysis.json")
    ap.add_argument("--summary", default="experiments/results/e5_base_error_analysis.md")
    args = ap.parse_args()

    train = load_balanced()
    hard = load_hard_eval()
    texts = [r["text"] for r in train] + [r["text"] for r in hard]
    x, revision, hidden = encode(texts, MODEL, "query: ", batch_size=16, max_length=128)
    n = len(train)
    xt, xh = x[:n], x[n:]
    yt = np.asarray([r["dominant"] for r in train])
    yh = np.asarray([r["dominant"] for r in hard])

    clf = LogisticRegression(C=4.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    clf.fit(xt, yt)
    pred = clf.predict(xh)
    raw = clf.predict_proba(xh)
    class_to_col = {c: i for i, c in enumerate(clf.classes_)}
    probs = np.zeros((len(hard), 4), dtype=float)
    for j, cls in enumerate(INTENTS):
        probs[:, j] = raw[:, class_to_col[cls]]

    sim = xh @ xt.T
    rows = []
    challenge_stats = defaultdict(lambda: {"n": 0, "correct": 0})
    for i, row in enumerate(hard):
        nearest_idx = np.argsort(-sim[i])[:5]
        ranked = np.argsort(-probs[i])
        item = {
            "id": row["id"],
            "text": row["text"],
            "gold": row["dominant"],
            "pred": str(pred[i]),
            "correct": bool(pred[i] == row["dominant"]),
            "margin": float(probs[i, ranked[0]] - probs[i, ranked[1]]),
            "probs": {INTENTS[j]: float(probs[i, j]) for j in range(4)},
            "challenge": list(row.get("challenge", [])),
            "nearest_training": [
                {
                    "id": train[j]["id"],
                    "dominant": train[j]["dominant"],
                    "style_bucket": train[j].get("style_bucket", "unknown"),
                    "cosine": float(sim[i, j]),
                    "text": train[j]["text"],
                }
                for j in nearest_idx
            ],
        }
        rows.append(item)
        for tag in row.get("challenge", []):
            challenge_stats[tag]["n"] += 1
            challenge_stats[tag]["correct"] += int(item["correct"])

    cm = confusion_matrix(yh, pred, labels=INTENTS)
    result = {
        "status": "development_only_error_analysis",
        "model": MODEL,
        "revision": revision,
        "hidden_size": hidden,
        "n_train": len(train),
        "n_hard": len(hard),
        "accuracy": float(np.mean(pred == yh)),
        "confusion_matrix": {gold: {guess: int(cm[i, j]) for j, guess in enumerate(INTENTS)} for i, gold in enumerate(INTENTS)},
        "challenge_accuracy": {
            tag: {"n": v["n"], "accuracy": float(v["correct"] / v["n"])}
            for tag, v in sorted(challenge_stats.items()) if v["n"] >= 3
        },
        "errors": [r for r in rows if not r["correct"]],
        "all_rows": rows,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# E5-base hard-style error analysis",
        "",
        "> Development-only diagnostic. The 48 hard cases are already architecture-development data, not a final holdout.",
        "",
        f"Accuracy: **{result['accuracy']:.3f}**",
        "",
        "## Confusion matrix",
        "",
        "| Gold \\ Pred | Öğretici | Eğlendirici | Haber | Sosyal |",
        "|---|---:|---:|---:|---:|",
    ]
    for gold in INTENTS:
        d = result["confusion_matrix"][gold]
        lines.append(f"| {gold} | {d['ogretici']} | {d['eglendirici']} | {d['haber']} | {d['sosyal']} |")

    lines += ["", "## Misclassified teaching-intent cases", ""]
    teaching_errors = [r for r in result["errors"] if r["gold"] == "ogretici"]
    for r in teaching_errors:
        nearest = r["nearest_training"][0]
        lines.append(
            f"- `{r['id']}` → predicted **{r['pred']}** (margin {r['margin']:.3f}); "
            f"nearest train `{nearest['id']}` / {nearest['dominant']} / cosine {nearest['cosine']:.3f}. Text: {r['text']}"
        )

    lines += ["", "## Challenge buckets", ""]
    for tag, v in result["challenge_accuracy"].items():
        lines.append(f"- `{tag}`: n={v['n']}, accuracy={v['accuracy']:.3f}")
    lines.append("")
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "accuracy": result["accuracy"],
        "confusion_matrix": result["confusion_matrix"],
        "challenge_accuracy": result["challenge_accuracy"],
        "teaching_errors": teaching_errors,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
