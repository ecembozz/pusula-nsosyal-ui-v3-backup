from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor

from benchmark_supervised_embeddings import INTENTS, cosine_rows, encode_texts, read_jsonl

ROOT = Path(__file__).resolve().parents[1]
CLEAR = ROOT / "data/v4_calibrated/train_clear.jsonl"
NEUTRAL = ROOT / "data/v4_calibrated/train_neutral_mixed.jsonl"
PAIRS = ROOT / "data/dev_labels/v4_contrastive_pairs_48.jsonl"
AXIS_INDEX = {name: i for i, name in enumerate(INTENTS)}


def load_train(path: Path):
    rows=[]
    for r in read_jsonl(path):
        rows.append({
            "id":r["id"],
            "text":r["metin"],
            "vec":np.asarray(r["gercek_niyet"],dtype=float),
            "aux":r.get("auxiliary_label"),
        })
    return rows


def class_probs(clf, x):
    raw=clf.predict_proba(x)
    out=np.zeros((len(x),4),dtype=float)
    cmap={c:i for i,c in enumerate(clf.classes_)}
    for j,name in enumerate(INTENTS):
        out[:,j]=raw[:,cmap[name]]
    return out


def evaluate(name, low4, high4, pairs):
    low4=np.clip(np.asarray(low4,dtype=float),0,1)
    high4=np.clip(np.asarray(high4,dtype=float),0,1)
    low_true=np.asarray([p["low_vector"] for p in pairs],dtype=float)
    high_true=np.asarray([p["high_vector"] for p in pairs],dtype=float)

    rows=[]
    by_axis=defaultdict(list)
    for i,p in enumerate(pairs):
        ai=AXIS_INDEX[p["axis"]]
        delta=float(high4[i,ai]-low4[i,ai])
        record={
            "id":p["id"],
            "axis":p["axis"],
            "low_score":float(low4[i,ai]),
            "high_score":float(high4[i,ai]),
            "delta":delta,
            "ordered":bool(delta>0),
            "ordered_margin_0_10":bool(delta>=0.10),
            "low_false_high":bool(low4[i,ai]>=0.60),
            "high_captured":bool(high4[i,ai]>=0.60),
            "high_axis_is_top1":bool(int(np.argmax(high4[i]))==ai),
        }
        rows.append(record)
        by_axis[p["axis"]].append(record)

    def agg(group):
        n=len(group)
        return {
            "n":n,
            "pair_order_accuracy":float(sum(r["ordered"] for r in group)/n),
            "pair_order_margin_0_10_rate":float(sum(r["ordered_margin_0_10"] for r in group)/n),
            "mean_axis_delta":float(np.mean([r["delta"] for r in group])),
            "low_false_high_rate":float(sum(r["low_false_high"] for r in group)/n),
            "high_capture_rate":float(sum(r["high_captured"] for r in group)/n),
            "high_axis_top1_rate":float(sum(r["high_axis_is_top1"] for r in group)/n),
        }

    all_true=np.vstack([low_true,high_true])
    all_pred=np.vstack([low4,high4])
    metrics=agg(rows)
    metrics.update({
        "vector_mae":float(np.mean(np.abs(all_true-all_pred))),
        "mean_cosine_similarity":float(np.mean(cosine_rows(all_true,all_pred))),
        "by_axis":{axis:agg(items) for axis,items in sorted(by_axis.items())},
        "failed_pairs":[r for r in rows if not r["ordered"]],
    })
    return metrics


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="intfloat/multilingual-e5-base")
    ap.add_argument("--output",default="experiments/results/v4_contrastive_pairs.json")
    ap.add_argument("--summary",default="experiments/results/v4_contrastive_pairs.md")
    args=ap.parse_args()

    clear=load_train(CLEAR)
    neutral=load_train(NEUTRAL)
    train=clear+neutral
    pairs=list(read_jsonl(PAIRS))
    if len(clear)!=256 or len(neutral)!=64 or len(pairs)!=48:
        raise SystemExit(f"unexpected sizes clear={len(clear)} neutral={len(neutral)} pairs={len(pairs)}")
    axes=[p["axis"] for p in pairs]
    if {a:axes.count(a) for a in INTENTS}!={a:12 for a in INTENTS}:
        raise SystemExit("contrastive set must contain 12 pairs per axis")

    texts=[r["text"] for r in train]
    texts += [p["low_text"] for p in pairs]
    texts += [p["high_text"] for p in pairs]
    x,revision=encode_texts(texts,args.model,batch_size=16)
    xt=x[:320]
    xl=x[320:368]
    xh=x[368:416]
    xc=xt[:256]

    y=np.asarray([r["vec"] for r in train],dtype=float)
    labels=np.asarray([r["aux"] for r in clear])

    clf=LogisticRegression(C=4.0,class_weight="balanced",max_iter=5000,solver="lbfgs",random_state=42)
    clf.fit(xc,labels)
    pl=class_probs(clf,xl)
    ph=class_probs(clf,xh)
    proto=np.vstack([
        np.mean(np.asarray([r["vec"] for r in clear if r["aux"]==cls],dtype=float),axis=0)
        for cls in INTENTS
    ])

    knn=KNeighborsRegressor(n_neighbors=7,weights="distance",metric="cosine")
    knn.fit(xt,y)
    kl=np.clip(knn.predict(xl),0,1)
    kh=np.clip(knn.predict(xh),0,1)

    ridge=Ridge(alpha=0.05)
    ridge.fit(xt,y)
    rl=np.clip(ridge.predict(xl),0,1)
    rh=np.clip(ridge.predict(xh),0,1)

    protol=np.clip(pl@proto,0,1)
    protoh=np.clip(ph@proto,0,1)

    methods={
        "knn_k7_all320":(kl,kh),
        "class_prototype_clear256":(protol,protoh),
        "knn_proto_blend_0.25":(np.clip(.75*kl+.25*protol,0,1),np.clip(.75*kh+.25*protoh,0,1)),
        "ridge_0.05_all320":(rl,rh),
    }
    results={name:evaluate(name,lo,hi,pairs) for name,(lo,hi) in methods.items()}

    ranked=sorted(
        results.items(),
        key=lambda kv:(
            -kv[1]["pair_order_accuracy"],
            -kv[1]["pair_order_margin_0_10_rate"],
            kv[1]["low_false_high_rate"],
            kv[1]["vector_mae"],
        )
    )
    recommended=ranked[0][0]

    payload={
        "status":"development_only_contrastive_not_final_gold",
        "embedding_model":args.model,
        "embedding_revision":revision,
        "train_clear_n":256,
        "train_neutral_n":64,
        "contrastive_pairs_n":48,
        "pairs_per_axis":12,
        "recommended_vector_head":recommended,
        "selection_rule":"maximize pair ordering, then >=0.10 ordering margin, minimize low-side false-high leakage, then vector MAE",
        "methods":results,
    }
    out=ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    lines=[
        "# V4 contrastive intent benchmark",
        "",
        "> Development-only. Each pair keeps topic/context similar and changes the intended semantic function. Not final human gold.",
        "",
        "| Head | Pair order | >=0.10 margin | Mean axis delta | Low false-high | High capture | High axis top-1 | 4D MAE | Cosine |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name,r in results.items():
        lines.append(
            f"| {name} | {r['pair_order_accuracy']:.3f} | {r['pair_order_margin_0_10_rate']:.3f} | "
            f"{r['mean_axis_delta']:.3f} | {r['low_false_high_rate']:.3f} | {r['high_capture_rate']:.3f} | "
            f"{r['high_axis_top1_rate']:.3f} | {r['vector_mae']:.3f} | {r['mean_cosine_similarity']:.3f} |"
        )
    lines += ["",f"Development recommendation: `{recommended}`","","## Per-axis ordering",""]
    for name,r in results.items():
        lines.append(f"### {name}")
        lines.append("")
        for axis,a in r["by_axis"].items():
            lines.append(f"- `{axis}`: order {a['pair_order_accuracy']:.3f}, margin>=0.10 {a['pair_order_margin_0_10_rate']:.3f}, delta {a['mean_axis_delta']:.3f}, low-leak {a['low_false_high_rate']:.3f}")
        lines.append("")
    (ROOT/args.summary).write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(payload,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
