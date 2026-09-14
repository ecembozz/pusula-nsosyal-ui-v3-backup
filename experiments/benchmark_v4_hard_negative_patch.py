from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsRegressor

from benchmark_supervised_embeddings import INTENTS, encode_texts, read_jsonl
from benchmark_v4_contrastive_pairs import evaluate, class_probs

ROOT=Path(__file__).resolve().parents[1]
CLEAR=ROOT/'data/v4_calibrated/train_clear.jsonl'
NEUTRAL=ROOT/'data/v4_calibrated/train_neutral_mixed.jsonl'
HARDNEG=ROOT/'data/v4_calibrated/hard_negative_neutral_v1.jsonl'
PAIRS=ROOT/'data/dev_labels/v4_contrastive_pairs_48.jsonl'
UNSEEN=ROOT/'data/v2_realistic/raw_posts.jsonl'


def load_train(path):
    rows=[]
    for r in read_jsonl(path):
        rows.append({
            'id':r['id'],
            'text':r['metin'],
            'vec':np.asarray(r['gercek_niyet'],dtype=float),
            'aux':r.get('auxiliary_label'),
        })
    return rows


def distribution(pred4):
    labels=[INTENTS[int(i)] for i in np.argmax(np.asarray(pred4),axis=1)]
    c=Counter(labels); n=len(labels)
    return {
        'counts':{k:int(c.get(k,0)) for k in INTENTS},
        'shares':{k:float(c.get(k,0)/n) for k in INTENTS},
        'max_class_share':float(max(c.values())/n),
        'mean_vector':[float(x) for x in np.mean(pred4,axis=0)],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',default='intfloat/multilingual-e5-base')
    ap.add_argument('--output',default='experiments/results/v4_hard_negative_patch.json')
    ap.add_argument('--summary',default='experiments/results/v4_hard_negative_patch.md')
    args=ap.parse_args()

    clear=load_train(CLEAR)
    neutral=load_train(NEUTRAL)
    hardneg=load_train(HARDNEG)
    base=clear+neutral
    patched=base+hardneg
    pairs=list(read_jsonl(PAIRS))
    unseen=[{'id':r['id'],'text':r['text']} for r in read_jsonl(UNSEEN)]

    if len(clear)!=256 or len(neutral)!=64 or len(hardneg)!=32 or len(pairs)!=48 or len(unseen)!=320:
        raise SystemExit(f'unexpected sizes clear={len(clear)} neutral={len(neutral)} hardneg={len(hardneg)} pairs={len(pairs)} unseen={len(unseen)}')
    if Counter(r.get('aux') for r in hardneg)!={None:32}:
        raise SystemExit('hard negatives must not have auxiliary hard labels')

    texts=[r['text'] for r in patched]
    texts += [p['low_text'] for p in pairs]
    texts += [p['high_text'] for p in pairs]
    texts += [r['text'] for r in unseen]
    x,revision=encode_texts(texts,args.model,batch_size=16)
    xp=x[:352]
    xb=xp[:320]
    xc=xp[:256]
    xl=x[352:400]
    xh=x[400:448]
    xu=x[448:]

    yb=np.asarray([r['vec'] for r in base],dtype=float)
    yp=np.asarray([r['vec'] for r in patched],dtype=float)
    labels=np.asarray([r['aux'] for r in clear])

    clf=LogisticRegression(C=4.0,class_weight='balanced',max_iter=5000,solver='lbfgs',random_state=42)
    clf.fit(xc,labels)
    pl=class_probs(clf,xl); ph=class_probs(clf,xh); pu=class_probs(clf,xu)
    proto=np.vstack([
        np.mean(np.asarray([r['vec'] for r in clear if r['aux']==cls],dtype=float),axis=0)
        for cls in INTENTS
    ])
    protol=np.clip(pl@proto,0,1); protoh=np.clip(ph@proto,0,1); protou=np.clip(pu@proto,0,1)

    def fit_predict(xtrain,ytrain):
        knn=KNeighborsRegressor(n_neighbors=7,weights='distance',metric='cosine')
        knn.fit(xtrain,ytrain)
        return (
            np.clip(knn.predict(xl),0,1),
            np.clip(knn.predict(xh),0,1),
            np.clip(knn.predict(xu),0,1),
        )

    bl,bh,bu=fit_predict(xb,yb)
    pl2,ph2,pu2=fit_predict(xp,yp)

    methods={
        'base_knn_k7_320':(bl,bh,bu),
        'base_knn_proto_blend_0.25':(
            np.clip(.75*bl+.25*protol,0,1),
            np.clip(.75*bh+.25*protoh,0,1),
            np.clip(.75*bu+.25*protou,0,1),
        ),
        'patched_knn_k7_352':(pl2,ph2,pu2),
        'patched_knn_proto_blend_0.25':(
            np.clip(.75*pl2+.25*protol,0,1),
            np.clip(.75*ph2+.25*protoh,0,1),
            np.clip(.75*pu2+.25*protou,0,1),
        ),
    }

    results={}
    for name,(lo,hi,unseen4) in methods.items():
        results[name]={
            'contrastive':evaluate(name,lo,hi,pairs),
            'unseen_v2_320':distribution(unseen4),
        }

    ranked=sorted(
        results.items(),
        key=lambda kv:(
            -kv[1]['contrastive']['pair_order_accuracy'],
            -kv[1]['contrastive']['pair_order_margin_0_10_rate'],
            kv[1]['contrastive']['low_false_high_rate'],
            kv[1]['contrastive']['vector_mae'],
            kv[1]['unseen_v2_320']['max_class_share'],
        )
    )
    recommended=ranked[0][0]

    payload={
        'status':'development_only_hard_negative_tuning_not_final_gold',
        'embedding_model':args.model,
        'embedding_revision':revision,
        'base_vector_train_n':320,
        'hard_negative_n':32,
        'patched_vector_train_n':352,
        'hard_negative_distribution':dict(Counter(r['id'].split('_')[1][0] for r in hardneg)),
        'recommended':recommended,
        'methods':results,
    }
    out=ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=[
        '# V4 hard-negative patch benchmark','',
        '> Development-only. Hard negatives were added after inspecting V4 contrastive development errors; these are tuning results, not final evaluation.','',
        '| Method | Pair order | >=0.10 | Mean delta | Low false-high | High capture | 4D MAE | Cosine | Unseen max share |','|---|---:|---:|---:|---:|---:|---:|---:|---:|'
    ]
    for name,r in results.items():
        c=r['contrastive']; u=r['unseen_v2_320']
        lines.append(f"| {name} | {c['pair_order_accuracy']:.3f} | {c['pair_order_margin_0_10_rate']:.3f} | {c['mean_axis_delta']:.3f} | {c['low_false_high_rate']:.3f} | {c['high_capture_rate']:.3f} | {c['vector_mae']:.3f} | {c['mean_cosine_similarity']:.3f} | {u['max_class_share']:.3f} |")
    lines += ['',f'Development recommendation: `{recommended}`','', '## Per-axis patched vs base','']
    for name in methods:
        lines.append(f'### {name}')
        for axis,a in results[name]['contrastive']['by_axis'].items():
            lines.append(f"- `{axis}`: order {a['pair_order_accuracy']:.3f}, margin>=0.10 {a['pair_order_margin_0_10_rate']:.3f}, delta {a['mean_axis_delta']:.3f}, low-leak {a['low_false_high_rate']:.3f}")
        lines.append('')
    (ROOT/args.summary).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(payload,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
