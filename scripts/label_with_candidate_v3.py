#!/usr/bin/env python3
"""Offline PUSULA Semantic Candidate V3 batch labeler.

Candidate V3 keeps inference out of the web runtime and uses:
- frozen multilingual-e5-base encoder
- auxiliary classifier trained on 256 clear-intent V4 rows
- canonical 4D vector + clickbait from semantic k-NN over 352 rows:
  256 clear + 64 neutral/mixed + 32 targeted hard negatives
- dominant_intent only as argmax(vector) for compatibility/diagnostics
- mixed_intent when vector top1-top2 margin is low

The 32 hard negatives were added after development error analysis to reduce
false news/entertainment activation on neutral personal/commentary text. This
is development tuning, not final evaluation evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsRegressor

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT/'experiments') not in sys.path:
    sys.path.insert(0,str(ROOT/'experiments'))

from benchmark_supervised_embeddings import INTENTS, encode_texts, read_jsonl

CLEAR=ROOT/'data/v4_calibrated/train_clear.jsonl'
NEUTRAL=ROOT/'data/v4_calibrated/train_neutral_mixed.jsonl'
HARDNEG=ROOT/'data/v4_calibrated/hard_negative_neutral_v1.jsonl'
MODEL_NAME='intfloat/multilingual-e5-base'
METHOD='pusula-semantic-candidate-v3'


def load_rows(path:Path):
    out=[]
    for r in read_jsonl(path):
        out.append({
            'id':str(r['id']),
            'text':str(r['metin']),
            'auxiliary':r.get('auxiliary_label'),
            'role':str(r['training_role']),
            'intent_vector':np.asarray(r['gercek_niyet'],dtype=float),
            'clickbait':float(r['clickbait']),
        })
    return out


def read_input(path:Path,text_key:str,id_key:str):
    if path.suffix.lower()=='.jsonl':
        raw=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    elif path.suffix.lower()=='.json':
        parsed=json.loads(path.read_text(encoding='utf-8'))
        raw=(parsed.get('posts') or parsed.get('items') or parsed.get('data')) if isinstance(parsed,dict) else parsed
    else:
        raise ValueError('input must be .jsonl or .json')
    if not isinstance(raw,list):
        raise ValueError('input must resolve to a list')
    rows=[]; seen=set()
    for i,r in enumerate(raw,1):
        if not isinstance(r,dict):
            raise ValueError(f'row {i}: expected object')
        rid=str(r.get(id_key,i)); text=str(r.get(text_key,'')).strip()
        if not text:
            raise ValueError(f'row {i}: empty {text_key}')
        if rid in seen:
            raise ValueError(f'duplicate id: {rid}')
        seen.add(rid); rows.append({'id':rid,'text':text})
    return rows


def class_probs(clf,x):
    raw=clf.predict_proba(x)
    out=np.zeros((len(x),4),dtype=float)
    cmap={c:i for i,c in enumerate(clf.classes_)}
    for j,name in enumerate(INTENTS):
        out[:,j]=raw[:,cmap[name]]
    return out


def screening_score(probs,nearest,ood_threshold):
    ordered=np.sort(probs,axis=1)
    cls_margin=np.clip(ordered[:,-1]-ordered[:,-2],0,1)
    max_prob=np.max(probs,axis=1)
    proximity=np.clip((nearest-ood_threshold)/max(1e-6,1.0-ood_threshold),0,1)
    # Diagnostic support score; deliberately not described as calibrated accuracy.
    score=np.clip(0.50*proximity+0.30*max_prob+0.20*cls_margin,0,1)
    score=np.where(nearest<ood_threshold,score*0.50,score)
    return score,cls_margin,max_prob


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--text-key',default='text')
    ap.add_argument('--id-key',default='id')
    ap.add_argument('--model',default=MODEL_NAME)
    ap.add_argument('--mixed-margin',type=float,default=0.15)
    args=ap.parse_args()

    clear=load_rows(CLEAR)
    neutral=load_rows(NEUTRAL)
    hardneg=load_rows(HARDNEG)
    vector_train=clear+neutral+hardneg
    input_rows=read_input(Path(args.input),args.text_key,args.id_key)

    if len(clear)!=256 or len(neutral)!=64 or len(hardneg)!=32 or len(vector_train)!=352:
        raise SystemExit(f'unexpected training sizes clear={len(clear)} neutral={len(neutral)} hardneg={len(hardneg)} total={len(vector_train)}')
    if Counter(r['auxiliary'] for r in clear)!=Counter({k:64 for k in INTENTS}):
        raise SystemExit('clear set is no longer 64x4 balanced')
    if any(r['auxiliary'] is not None for r in neutral+hardneg):
        raise SystemExit('neutral/hard-negative rows must not carry hard labels')

    texts=[r['text'] for r in vector_train]+[r['text'] for r in input_rows]
    x,revision=encode_texts(texts,args.model,batch_size=16)
    xt=x[:352]; xc=xt[:256]; xi=x[352:]

    labels=np.asarray([r['auxiliary'] for r in clear])
    clf=LogisticRegression(C=4.0,class_weight='balanced',max_iter=5000,solver='lbfgs',random_state=42)
    clf.fit(xc,labels)

    y=np.asarray([list(r['intent_vector'])+[r['clickbait']] for r in vector_train],dtype=float)
    knn=KNeighborsRegressor(n_neighbors=7,weights='distance',metric='cosine')
    knn.fit(xt,y)
    pred=np.clip(np.asarray(knn.predict(xi),dtype=float),0,1)
    probs=class_probs(clf,xi)

    train_sim=xt@xt.T
    np.fill_diagonal(train_sim,-1.0)
    ood_threshold=float(np.quantile(np.max(train_sim,axis=1),0.05))
    nearest=np.max(xi@xt.T,axis=1)
    confidence,cls_margin,max_prob=screening_score(probs,nearest,ood_threshold)
    ood=nearest<ood_threshold

    dominant_idx=np.argmax(pred[:,:4],axis=1)
    dominant=[INTENTS[int(i)] for i in dominant_idx]
    aux_idx=np.argmax(probs,axis=1)
    auxiliary=[INTENTS[int(i)] for i in aux_idx]
    ordered=np.sort(pred[:,:4],axis=1)
    intent_margin=np.clip(ordered[:,-1]-ordered[:,-2],0,1)
    mixed=intent_margin<float(args.mixed_margin)

    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8') as f:
        for i,row in enumerate(input_rows):
            payload={
                'id':row['id'],
                'text':row['text'],
                'intent_vector':[round(float(v),6) for v in pred[i,:4]],
                'clickbait':round(float(pred[i,4]),6),
                'dominant_intent':dominant[i],
                'mixed_intent':bool(mixed[i]),
                'confidence':round(float(confidence[i]),6),
                'method':METHOD,
                'model':args.model,
                'prompt_version':None,
                'schema_version':'pusula-label-v2',
                'diagnostics':{
                    'intent_top1_top2_margin':round(float(intent_margin[i]),6),
                    'mixed_margin_threshold':float(args.mixed_margin),
                    'auxiliary_dominant_intent':auxiliary[i],
                    'auxiliary_dominant_probability':round(float(max_prob[i]),6),
                    'auxiliary_dominant_margin':round(float(cls_margin[i]),6),
                    'canonical_auxiliary_agree':dominant[i]==auxiliary[i],
                    'nearest_train_cosine':round(float(nearest[i]),6),
                    'ood':bool(ood[i]),
                    'ood_threshold':round(float(ood_threshold),6),
                    'encoder_revision':revision,
                    'classifier_training_rows':256,
                    'vector_training_rows':352,
                    'clear_training_rows':256,
                    'neutral_mixed_training_rows':64,
                    'hard_negative_training_rows':32,
                },
            }
            f.write(json.dumps(payload,ensure_ascii=False)+'\n')

    summary={
        'method':METHOD,
        'model':args.model,
        'encoder_revision':revision,
        'input_count':len(input_rows),
        'dominant_distribution':dict(Counter(dominant)),
        'auxiliary_distribution':dict(Counter(auxiliary)),
        'canonical_auxiliary_agreement_rate':float(np.mean([a==b for a,b in zip(dominant,auxiliary)])),
        'mixed_intent_count':int(np.sum(mixed)),
        'mixed_intent_rate':float(np.mean(mixed)),
        'mean_intent_margin':float(np.mean(intent_margin)),
        'mean_screening_confidence':float(np.mean(confidence)),
        'ood_count':int(np.sum(ood)),
        'ood_rate':float(np.mean(ood)),
        'ood_threshold':ood_threshold,
        'mean_clickbait':float(np.mean(pred[:,4])),
        'clickbait_ge_0_50':int(np.sum(pred[:,4]>=0.50)),
        'output':str(out),
    }
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
