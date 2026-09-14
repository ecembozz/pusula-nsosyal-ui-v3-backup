from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import KNeighborsRegressor

from benchmark_supervised_embeddings import INTENTS, cosine_rows, encode_texts, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
CLEAR = ROOT / "data/v4_calibrated/train_clear.jsonl"
NEUTRAL = ROOT / "data/v4_calibrated/train_neutral_mixed.jsonl"
DEV = ROOT / "data/dev_labels/v4_semantic_dev_64.jsonl"
UNSEEN = ROOT / "data/v2_realistic/raw_posts.jsonl"


def load_train(path: Path):
    rows = []
    for r in read_jsonl(path):
        rows.append({
            "id": r["id"],
            "text": r["metin"],
            "y": [float(x) for x in r["gercek_niyet"]] + [float(r["clickbait"])],
            "auxiliary": r.get("auxiliary_label"),
            "role": r["training_role"],
        })
    return rows


def load_dev():
    rows = []
    for r in read_jsonl(DEV):
        intent = r["intent"]
        if isinstance(intent, dict):
            vec = [float(intent[k]) for k in INTENTS]
        elif isinstance(intent, list) and len(intent) == 4:
            vec = [float(x) for x in intent]
        else:
            raise ValueError(f"{r.get('id')}: intent must be a 4-value list or intent mapping")
        rows.append({
            "id": r["id"],
            "text": r["text"],
            "y": vec + [float(r["clickbait"])],
            "auxiliary": r["auxiliary_label"],
        })
    return rows


def probs4(clf, x):
    raw = clf.predict_proba(x)
    out = np.zeros((len(x), 4), dtype=float)
    cmap = {c: i for i, c in enumerate(clf.classes_)}
    for j, cls in enumerate(INTENTS):
        out[:, j] = raw[:, cmap[cls]]
    return out


def argmax_labels(pred4):
    return [INTENTS[int(i)] for i in np.argmax(np.asarray(pred4), axis=1)]


def vector_metrics(y_true, pred4, click_pred, labels_true):
    pred4 = np.clip(np.asarray(pred4, dtype=float), 0, 1)
    click_pred = np.clip(np.asarray(click_pred, dtype=float), 0, 1)
    labels_pred = argmax_labels(pred4)
    return {
        "dominant_accuracy": float(accuracy_score(labels_true, labels_pred)),
        "macro_f1": float(f1_score(labels_true, labels_pred, labels=INTENTS, average="macro", zero_division=0)),
        "intent_mae": float(np.mean(np.abs(y_true[:, :4] - pred4))),
        "mean_cosine_similarity": float(np.mean(cosine_rows(y_true[:, :4], pred4))),
        "clickbait_mae": float(np.mean(np.abs(y_true[:, 4] - click_pred))),
        "pred_distribution": dict(Counter(labels_pred)),
        "per_class_accuracy": {
            cls: float(np.mean([labels_pred[i] == cls for i in np.where(np.asarray(labels_true) == cls)[0]]))
            for cls in INTENTS
        },
    }


def cls_metrics(labels_true, probs):
    pred = argmax_labels(probs)
    correct = np.asarray([a == b for a, b in zip(labels_true, pred)], dtype=bool)
    sorted_p = np.sort(probs, axis=1)
    margin = sorted_p[:, -1] - sorted_p[:, -2]
    out = {
        "accuracy": float(accuracy_score(labels_true, pred)),
        "macro_f1": float(f1_score(labels_true, pred, labels=INTENTS, average="macro", zero_division=0)),
        "pred_distribution": dict(Counter(pred)),
        "per_class_accuracy": {
            cls: float(np.mean([pred[i] == cls for i in np.where(np.asarray(labels_true) == cls)[0]]))
            for cls in INTENTS
        },
    }
    for coverage in (0.50, 0.75):
        n = max(1, int(round(len(pred) * coverage)))
        idx = np.argsort(-margin)[:n]
        out[f"accuracy_at_{int(coverage*100)}pct_coverage"] = float(np.mean(correct[idx]))
    return out


def dist_probe(pred4):
    labels = argmax_labels(pred4)
    counts = Counter(labels)
    n = len(labels)
    return {
        "counts": {k: int(counts.get(k, 0)) for k in INTENTS},
        "shares": {k: float(counts.get(k, 0) / n) for k in INTENTS},
        "max_class_share": float(max(counts.values()) / n),
        "mean_vector": [float(x) for x in np.mean(pred4, axis=0)],
    }


def train_dev_similarity(train_rows, dev_rows):
    rows = train_rows + dev_rows
    texts = [r["text"] for r in rows]
    mat = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1).fit_transform(texts)
    sim = cosine_similarity(mat[len(train_rows):], mat[:len(train_rows)])
    idx = np.unravel_index(np.argmax(sim), sim.shape)
    return {
        "max_char_tfidf_similarity": float(sim[idx]),
        "dev_id": dev_rows[idx[0]]["id"],
        "train_id": train_rows[idx[1]]["id"],
        "pairs_ge_0_90": int(np.sum(sim >= 0.90)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/multilingual-e5-base")
    ap.add_argument("--output", default="experiments/results/dataset_v4_e5_base.json")
    ap.add_argument("--summary", default="experiments/results/dataset_v4_e5_base.md")
    args = ap.parse_args()

    clear = load_train(CLEAR)
    neutral = load_train(NEUTRAL)
    train = clear + neutral
    dev = load_dev()
    unseen = [{"id": r["id"], "text": r["text"]} for r in read_jsonl(UNSEEN)]

    if len(clear) != 256 or len(neutral) != 64 or len(dev) != 64 or len(unseen) != 320:
        raise SystemExit(f"unexpected sizes clear={len(clear)} neutral={len(neutral)} dev={len(dev)} unseen={len(unseen)}")
    if Counter(r["auxiliary"] for r in clear) != Counter({k: 64 for k in INTENTS}):
        raise SystemExit("V4 clear training set is not 64x4 balanced")
    if Counter(r["auxiliary"] for r in dev) != Counter({k: 16 for k in INTENTS}):
        raise SystemExit("V4 dev set is not 16x4 balanced")

    overlap = train_dev_similarity(train, dev)
    if overlap["pairs_ge_0_90"]:
        raise SystemExit(f"train/dev near-duplicate leakage >=0.90: {overlap}")

    texts = [r["text"] for r in train] + [r["text"] for r in dev] + [r["text"] for r in unseen]
    x, revision = encode_texts(texts, args.model, batch_size=16)
    xt = x[:320]
    xc = xt[:256]
    xd = x[320:384]
    xu = x[384:]

    yt = np.asarray([r["y"] for r in train], dtype=float)
    yd = np.asarray([r["y"] for r in dev], dtype=float)
    lc = np.asarray([r["auxiliary"] for r in clear])
    ld = np.asarray([r["auxiliary"] for r in dev])

    clf = LogisticRegression(C=4.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    clf.fit(xc, lc)
    pd = probs4(clf, xd)
    pu = probs4(clf, xu)
    classifier = cls_metrics(ld, pd)

    knn = KNeighborsRegressor(n_neighbors=7, weights="distance", metric="cosine")
    knn.fit(xt, yt)
    kd = np.clip(np.asarray(knn.predict(xd), dtype=float), 0, 1)
    ku = np.clip(np.asarray(knn.predict(xu), dtype=float), 0, 1)
    click_d = kd[:, 4]

    proto = np.vstack([
        np.mean(np.asarray([r["y"][:4] for r in clear if r["auxiliary"] == cls], dtype=float), axis=0)
        for cls in INTENTS
    ])
    protod = np.clip(pd @ proto, 0, 1)
    protou = np.clip(pu @ proto, 0, 1)

    methods = {
        "knn_k7_all320": (kd[:, :4], ku[:, :4]),
        "class_prototype_clear256": (protod, protou),
        "knn_proto_blend_0.25": (np.clip(.75*kd[:, :4]+.25*protod,0,1), np.clip(.75*ku[:, :4]+.25*protou,0,1)),
        "knn_proto_blend_0.50": (np.clip(.50*kd[:, :4]+.50*protod,0,1), np.clip(.50*ku[:, :4]+.50*protou,0,1)),
    }
    for alpha in (0.05, 0.1, 0.5, 1.0, 5.0):
        ridge = Ridge(alpha=alpha)
        ridge.fit(xt, yt[:, :4])
        methods[f"ridge_{alpha:g}_all320"] = (
            np.clip(ridge.predict(xd), 0, 1),
            np.clip(ridge.predict(xu), 0, 1),
        )

    results = {}
    for name, (dev4, unseen4) in methods.items():
        results[name] = {
            "dev64": vector_metrics(yd, dev4, click_d, ld),
            "unseen_v2_320": dist_probe(unseen4),
        }
        results[name]["collapse_flag_over_75pct_one_class"] = bool(
            results[name]["unseen_v2_320"]["max_class_share"] > 0.75
        )

    eligible = [(name, r) for name, r in results.items() if not r["collapse_flag_over_75pct_one_class"]]
    eligible.sort(key=lambda item: (item[1]["dev64"]["intent_mae"], -item[1]["dev64"]["mean_cosine_similarity"]))
    recommended = eligible[0][0] if eligible else None

    payload = {
        "status": "development_only_v4_semantics_not_final_gold",
        "embedding_model": args.model,
        "embedding_revision": revision,
        "training": {"clear":256,"neutral_mixed":64,"vector_total":320},
        "dev64_distribution": dict(Counter(ld)),
        "train_dev_similarity_audit": overlap,
        "classifier_clear256": classifier,
        "class_prototypes": {INTENTS[i]: [float(x) for x in proto[i]] for i in range(4)},
        "recommended_vector_head": recommended,
        "selection_rule": "reject >75% one-class unseen collapse; then minimize dev64 4D MAE; tie-break by cosine",
        "vector_heads": results,
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    lines = [
        "# Dataset V4 + multilingual-e5-base development benchmark",
        "",
        "> Development-only. V4 dev-64 is synthetic/original and separate from training, but it is not final human gold.",
        "",
        f"Encoder: `{args.model}` @ `{revision}`",
        "",
        f"Clear-intent classifier: accuracy `{classifier['accuracy']:.3f}`, macro-F1 `{classifier['macro_f1']:.3f}`, top-50% `{classifier['accuracy_at_50pct_coverage']:.3f}`.",
        "",
        "| Vector head | Dev acc. | F1 | 4D MAE | Cosine | Unseen max share | Unseen distribution | Collapse? |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for name, r in results.items():
        d=r["dev64"]; u=r["unseen_v2_320"]
        dist=", ".join(f"{k}:{u['counts'][k]}" for k in INTENTS)
        lines.append(f"| {name} | {d['dominant_accuracy']:.3f} | {d['macro_f1']:.3f} | {d['intent_mae']:.3f} | {d['mean_cosine_similarity']:.3f} | {u['max_class_share']:.3f} | {dist} | {'YES' if r['collapse_flag_over_75pct_one_class'] else 'no'} |")
    lines += ["", f"Development recommendation: `{recommended}`", "", f"Train/dev max char-TFIDF similarity: `{overlap['max_char_tfidf_similarity']:.3f}`; pairs >=0.90: `{overlap['pairs_ge_0_90']}`.", ""]
    (ROOT / args.summary).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
