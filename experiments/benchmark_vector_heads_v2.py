from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor

from benchmark_dataset_v3_e5_base import (
    V3_V1_FILES,
    V3_V2_FILES,
    fit_classifier,
    load_v3,
    vec_metrics,
)
from benchmark_style_generalization import load_hard_eval
from benchmark_supervised_embeddings import INTENTS, encode_texts, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
UNSEEN = ROOT / "data/v2_realistic/raw_posts.jsonl"


def class_prototypes(rows):
    by_class = {k: [] for k in INTENTS}
    for row in rows:
        by_class[row["dominant"]].append(np.asarray(row["y"][:4], dtype=float))
    return np.vstack([np.mean(by_class[k], axis=0) for k in INTENTS])


def attach_clickbait(intent4, clickbait):
    intent4 = np.clip(np.asarray(intent4, dtype=float), 0.0, 1.0)
    clickbait = np.clip(np.asarray(clickbait, dtype=float).reshape(-1, 1), 0.0, 1.0)
    return np.hstack([intent4, clickbait])


def distribution(pred4):
    labels = [INTENTS[int(i)] for i in np.argmax(np.asarray(pred4), axis=1)]
    counts = Counter(labels)
    n = max(1, len(labels))
    return {
        "counts": {k: int(counts.get(k, 0)) for k in INTENTS},
        "shares": {k: float(counts.get(k, 0) / n) for k in INTENTS},
        "max_class_share": float(max(counts.values()) / n) if counts else 0.0,
        "mean_vector": [float(x) for x in np.mean(np.asarray(pred4), axis=0)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-base")
    ap.add_argument("--output", default="experiments/results/vector_heads_v2.json")
    ap.add_argument("--summary", default="experiments/results/vector_heads_v2.md")
    args = ap.parse_args()

    v3_128 = load_v3(V3_V1_FILES, "dataset_v3_tranche1")
    v3_256 = v3_128 + load_v3(V3_V2_FILES, "dataset_v3_tranche2")
    hard = load_hard_eval()
    unseen_raw = read_jsonl(UNSEEN)
    unseen = [{"id": r["id"], "text": r["text"]} for r in unseen_raw]

    if len(v3_128) != 128 or len(v3_256) != 256 or len(hard) != 48 or len(unseen) != 320:
        raise SystemExit(
            f"unexpected sizes: v3_128={len(v3_128)} v3_256={len(v3_256)} hard={len(hard)} unseen={len(unseen)}"
        )

    rows = v3_256 + hard + unseen
    x, revision = encode_texts([r["text"] for r in rows], args.model, batch_size=16)
    xv = x[:256]
    xh = x[256:304]
    xu = x[304:]
    xv128 = xv[:128]

    yv = np.asarray([r["y"] for r in v3_256], dtype=float)
    yh = np.asarray([r["y"] for r in hard], dtype=float)
    dv128 = np.asarray([r["dominant"] for r in v3_128])
    dh = np.asarray([r["dominant"] for r in hard])

    # Auxiliary class probabilities come only from the cleaner first tranche.
    clf, _, ph, _ = fit_classifier(xv128, dv128, xh, dh)
    raw_u = clf.predict_proba(xu)
    pu = np.zeros((len(xu), 4), dtype=float)
    cmap = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        pu[:, j] = raw_u[:, cmap[cls]]

    # k-NN remains the reference non-parametric multi-intent head.
    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(xv, yv)
    kh = np.clip(np.asarray(knn.predict(xh), dtype=float), 0.0, 1.0)
    ku = np.clip(np.asarray(knn.predict(xu), dtype=float), 0.0, 1.0)
    click_h = kh[:, 4]
    click_u = ku[:, 4]

    proto = class_prototypes(v3_256)
    proto_h = np.clip(ph @ proto, 0.0, 1.0)
    proto_u = np.clip(pu @ proto, 0.0, 1.0)

    candidates = {
        "knn_k7": (kh[:, :4], ku[:, :4]),
        "class_prototype": (proto_h, proto_u),
    }

    for alpha in (0.25, 0.50, 0.75):
        candidates[f"knn_prototype_blend_{alpha:.2f}"] = (
            np.clip((1.0 - alpha) * kh[:, :4] + alpha * proto_h, 0.0, 1.0),
            np.clip((1.0 - alpha) * ku[:, :4] + alpha * proto_u, 0.0, 1.0),
        )

    for alpha in (0.1, 1.0, 10.0, 100.0):
        ridge = Ridge(alpha=alpha)
        ridge.fit(xv, yv[:, :4])
        candidates[f"ridge_{alpha:g}"] = (
            np.clip(ridge.predict(xh), 0.0, 1.0),
            np.clip(ridge.predict(xu), 0.0, 1.0),
        )

    methods = {}
    for name, (hard4, unseen4) in candidates.items():
        hard5 = attach_clickbait(hard4, click_h)
        metrics = vec_metrics(yh, hard5, dh)
        collapse = distribution(unseen4)
        methods[name] = {
            "hard48": metrics,
            "unseen_v2_320": collapse,
            "collapse_flag_over_75pct_one_class": bool(collapse["max_class_share"] > 0.75),
        }

    # Ranking is development-only: lower MAE first, then higher cosine, while rejecting severe unseen collapse.
    eligible = [
        (name, r)
        for name, r in methods.items()
        if not r["collapse_flag_over_75pct_one_class"]
    ]
    eligible.sort(
        key=lambda item: (
            item[1]["hard48"]["intent_mae"],
            -item[1]["hard48"]["mean_cosine_similarity"],
        )
    )
    recommendation = eligible[0][0] if eligible else None

    result = {
        "status": "development_only_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "train_vector_n": 256,
        "train_auxiliary_classifier_n": 128,
        "hard_eval_n": 48,
        "unseen_distribution_probe_n": 320,
        "selection_rule": "reject >75% one-class unseen argmax collapse; then minimize hard48 4D MAE; tie-break by cosine",
        "recommended_vector_head": recommendation,
        "class_prototypes": {INTENTS[i]: [float(x) for x in proto[i]] for i in range(4)},
        "methods": methods,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Candidate V2 vector-head development comparison",
        "",
        "> Development-only. Hard-48 is repeatedly inspected and V2-320 has no gold labels.",
        "",
        f"Encoder: `{args.model}` @ `{revision}`",
        "",
        "| Head | Hard48 acc. | F1 | 4D MAE | Cosine | Unseen max-class share | Unseen distribution | Collapse? |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for name, row in methods.items():
        h = row["hard48"]
        u = row["unseen_v2_320"]
        dist = ", ".join(f"{k}:{u['counts'][k]}" for k in INTENTS)
        lines.append(
            f"| {name} | {h['dominant_accuracy']:.3f} | {h['macro_f1']:.3f} | "
            f"{h['intent_mae']:.3f} | {h['mean_cosine_similarity']:.3f} | "
            f"{u['max_class_share']:.3f} | {dist} | "
            f"{'YES' if row['collapse_flag_over_75pct_one_class'] else 'no'} |"
        )
    lines += [
        "",
        f"Development recommendation: `{recommendation}`",
        "",
        "Selection rejects severe one-class collapse on the unlabeled unseen corpus, then uses hard-48 vector MAE and cosine only as development criteria. This is not a final competition metric.",
        "",
    ]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
