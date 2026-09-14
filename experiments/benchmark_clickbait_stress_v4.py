from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, precision_score, recall_score
from sklearn.neighbors import KNeighborsRegressor

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

from benchmark_supervised_embeddings import encode_texts, read_jsonl
from core.clickbait import analyze_clickbait
from core.heuristic_labeler import HeuristicLabeler

CLEAR = ROOT / "data/v4_calibrated/train_clear.jsonl"
NEUTRAL = ROOT / "data/v4_calibrated/train_neutral_mixed.jsonl"
HARDNEG = ROOT / "data/v4_calibrated/hard_negative_neutral_v1.jsonl"
STRESS = ROOT / "data/dev_labels/v4_clickbait_stress_32.jsonl"


def load_train():
    rows=[]
    for path in (CLEAR,NEUTRAL,HARDNEG):
        for r in read_jsonl(path):
            rows.append({
                'text':r['metin'],
                'intent':[float(x) for x in r['gercek_niyet']],
                'clickbait':float(r['clickbait']),
            })
    return rows


def metrics(name,scores,rows):
    scores=np.clip(np.asarray(scores,dtype=float),0,1)
    y=np.asarray([int(r['label']) for r in rows],dtype=int)
    target=np.asarray([float(r['target']) for r in rows],dtype=float)
    pred=(scores>=.50).astype(int)
    groups=defaultdict(list)
    for i,r in enumerate(rows):
        groups[r['group']].append(i)
    by_group={}
    for group,idxs in sorted(groups.items()):
        idx=np.asarray(idxs,dtype=int)
        by_group[group]={
            'n':int(len(idx)),
            'positive_rate':float(np.mean(y[idx])),
            'mean_score':float(np.mean(scores[idx])),
            'accuracy_at_0_50':float(np.mean(pred[idx]==y[idx])),
        }
    failures=[]
    for i,r in enumerate(rows):
        if pred[i]!=y[i]:
            failures.append({
                'id':r['id'],'group':r['group'],'label':int(y[i]),
                'score':float(scores[i]),'text':r['text'],
            })
    return {
        'accuracy_at_0_50':float(accuracy_score(y,pred)),
        'precision_at_0_50':float(precision_score(y,pred,zero_division=0)),
        'recall_at_0_50':float(recall_score(y,pred,zero_division=0)),
        'f1_at_0_50':float(f1_score(y,pred,zero_division=0)),
        'mae':float(mean_absolute_error(target,scores)),
        'mean_positive_score':float(np.mean(scores[y==1])),
        'mean_negative_score':float(np.mean(scores[y==0])),
        'score_separation':float(np.mean(scores[y==1])-np.mean(scores[y==0])),
        'false_positive_count':int(np.sum((pred==1)&(y==0))),
        'false_negative_count':int(np.sum((pred==0)&(y==1))),
        'by_group':by_group,
        'failures':failures,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',default='intfloat/multilingual-e5-base')
    ap.add_argument('--output',default='experiments/results/clickbait_stress_v4.json')
    ap.add_argument('--summary',default='experiments/results/clickbait_stress_v4.md')
    args=ap.parse_args()

    train=load_train()
    rows=list(read_jsonl(STRESS))
    if len(train)!=352 or len(rows)!=32:
        raise SystemExit(f'unexpected sizes train={len(train)} stress={len(rows)}')
    if sum(int(r['label']) for r in rows)!=16:
        raise SystemExit('stress set must be balanced 16 positive / 16 negative')

    texts=[r['text'] for r in train]+[r['text'] for r in rows]
    x,revision=encode_texts(texts,args.model,batch_size=16)
    xt=x[:352]; xs=x[352:]
    ytrain=np.asarray([r['intent']+[r['clickbait']] for r in train],dtype=float)
    knn=KNeighborsRegressor(n_neighbors=7,weights='distance',metric='cosine')
    knn.fit(xt,ytrain)
    semantic=np.clip(np.asarray(knn.predict(xs),dtype=float)[:,4],0,1)

    old=HeuristicLabeler()
    upstream=np.asarray([float(old.label(r['text']).clickbait) for r in rows],dtype=float)

    frozen=[]; reasons={}
    for r in rows:
        result=analyze_clickbait(r['text'])
        frozen.append(result.score)
        reasons[r['id']]=list(result.reasons)
    frozen=np.asarray(frozen,dtype=float)

    methods={
        'semantic_knn_candidate_v3':metrics('semantic',semantic,rows),
        'upstream_heuristic_v1':metrics('upstream',upstream,rows),
        'frozen_presentation_rules_v1':metrics('frozen',frozen,rows),
    }
    ranked=sorted(methods.items(),key=lambda kv:(-kv[1]['f1_at_0_50'],-kv[1]['accuracy_at_0_50'],kv[1]['mae']))
    result={
        'status':'development_stress_after_rule_freeze_not_final_gold',
        'embedding_model':args.model,
        'embedding_revision':revision,
        'stress_n':len(rows),
        'positive_n':16,
        'negative_n':16,
        'recommended_on_stress':ranked[0][0],
        'methods':methods,
        'frozen_rule_reasons':reasons,
    }
    out=ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=[
        '# Clickbait frozen-rule stress test V4','',
        '> Development stress set authored after the presentation rule was frozen. Still not human gold and not a final competition claim.','',
        '| Method | Accuracy | Precision | Recall | F1 | MAE | Pos mean | Neg mean | Separation | FP | FN |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|'
    ]
    for name,r in methods.items():
        lines.append(f"| {name} | {r['accuracy_at_0_50']:.3f} | {r['precision_at_0_50']:.3f} | {r['recall_at_0_50']:.3f} | {r['f1_at_0_50']:.3f} | {r['mae']:.3f} | {r['mean_positive_score']:.3f} | {r['mean_negative_score']:.3f} | {r['score_separation']:.3f} | {r['false_positive_count']} | {r['false_negative_count']} |")
    lines += ['',f"Stress-set recommendation: `{ranked[0][0]}`",'', '## Frozen-rule failures','']
    for failure in methods['frozen_presentation_rules_v1']['failures']:
        lines.append(f"- `{failure['id']}` [{failure['group']}] gold={failure['label']} score={failure['score']:.3f}: {failure['text']}")
    lines.append('')
    (ROOT/args.summary).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
