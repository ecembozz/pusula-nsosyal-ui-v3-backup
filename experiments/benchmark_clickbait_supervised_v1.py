from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.neighbors import KNeighborsRegressor

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
if str(ROOT/'experiments') not in sys.path:
    sys.path.insert(0,str(ROOT/'experiments'))

from benchmark_supervised_embeddings import encode_texts, read_jsonl
from core.clickbait import score_clickbait
from core.heuristic_labeler import HeuristicLabeler

CB_FILES=[
    ROOT/'data/v4_calibrated/clickbait_train_pos_a.jsonl',
    ROOT/'data/v4_calibrated/clickbait_train_pos_b.jsonl',
    ROOT/'data/v4_calibrated/clickbait_train_neg_a.jsonl',
    ROOT/'data/v4_calibrated/clickbait_train_neg_b.jsonl',
]
VECTOR_FILES=[
    ROOT/'data/v4_calibrated/train_clear.jsonl',
    ROOT/'data/v4_calibrated/train_neutral_mixed.jsonl',
    ROOT/'data/v4_calibrated/hard_negative_neutral_v1.jsonl',
]
STRESS=ROOT/'data/dev_labels/v4_clickbait_stress_32.jsonl'


def load_cb_train():
    rows=[]
    for p in CB_FILES:
        rows.extend(list(read_jsonl(p)))
    return rows


def load_vector_train():
    rows=[]
    for p in VECTOR_FILES:
        rows.extend(list(read_jsonl(p)))
    return rows


def tfidf_model():
    features=FeatureUnion([
        ('char',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=12000,sublinear_tf=True)),
        ('word',TfidfVectorizer(analyzer='word',ngram_range=(1,2),min_df=2,max_features=8000,sublinear_tf=True)),
    ])
    return Pipeline([
        ('features',features),
        ('clf',LogisticRegression(C=3.0,class_weight='balanced',max_iter=5000,solver='liblinear',random_state=42)),
    ])


def logistic_model():
    return LogisticRegression(C=3.0,class_weight='balanced',max_iter=5000,solver='liblinear',random_state=42)


def evaluate(scores,rows):
    scores=np.clip(np.asarray(scores,dtype=float),0,1)
    y=np.asarray([int(r['label']) for r in rows],dtype=int)
    target=np.asarray([float(r['target'] if 'target' in r else r['clickbait']) for r in rows],dtype=float)
    pred=(scores>=.5).astype(int)
    return {
        'accuracy':float(accuracy_score(y,pred)),
        'precision':float(precision_score(y,pred,zero_division=0)),
        'recall':float(recall_score(y,pred,zero_division=0)),
        'f1':float(f1_score(y,pred,zero_division=0)),
        'roc_auc':float(roc_auc_score(y,scores)),
        'brier':float(brier_score_loss(y,scores)),
        'mae_to_continuous_target':float(mean_absolute_error(target,scores)),
        'mean_positive':float(np.mean(scores[y==1])),
        'mean_negative':float(np.mean(scores[y==0])),
        'false_positive_count':int(np.sum((pred==1)&(y==0))),
        'false_negative_count':int(np.sum((pred==0)&(y==1))),
        'failures':[
            {'id':rows[i]['id'],'label':int(y[i]),'score':float(scores[i]),'text':rows[i]['text']}
            for i in range(len(rows)) if pred[i]!=y[i]
        ],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',default='intfloat/multilingual-e5-base')
    ap.add_argument('--output',default='experiments/results/clickbait_supervised_v1.json')
    ap.add_argument('--summary',default='experiments/results/clickbait_supervised_v1.md')
    args=ap.parse_args()

    train=load_cb_train()
    vector_train=load_vector_train()
    stress=list(read_jsonl(STRESS))
    if len(train)!=128 or sum(int(r['label']) for r in train)!=64:
        raise SystemExit(f'clickbait training set must be 128 / 64 positive, got {len(train)} / {sum(int(r["label"]) for r in train)}')
    if len(vector_train)!=352 or len(stress)!=32:
        raise SystemExit(f'unexpected vector/stress sizes {len(vector_train)} / {len(stress)}')

    train_text=[r['text'] for r in train]
    stress_text=[r['text'] for r in stress]
    vector_text=[r['metin'] for r in vector_train]
    all_text=train_text+vector_text+stress_text
    x,revision=encode_texts(all_text,args.model,batch_size=16)
    x_cb=x[:128]
    x_vec=x[128:480]
    x_stress=x[480:]
    y=np.asarray([int(r['label']) for r in train],dtype=int)

    cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=42)

    # Dedicated e5 logistic head.
    e5=logistic_model()
    e5_oof=cross_val_predict(e5,x_cb,y,cv=cv,method='predict_proba')[:,1]
    e5.fit(x_cb,y)
    e5_stress=e5.predict_proba(x_stress)[:,1]

    # Tiny text-only baseline.
    tfidf=tfidf_model()
    tfidf_oof=cross_val_predict(tfidf,train_text,y,cv=cv,method='predict_proba')[:,1]
    tfidf.fit(train_text,y)
    tfidf_stress=tfidf.predict_proba(stress_text)[:,1]

    # Existing Candidate V3 KNN regression baseline.
    vector_y=np.asarray([
        [float(v) for v in r['gercek_niyet']]+[float(r['clickbait'])]
        for r in vector_train
    ],dtype=float)
    knn=KNeighborsRegressor(n_neighbors=7,weights='distance',metric='cosine')
    knn.fit(x_vec,vector_y)
    semantic_stress=np.clip(knn.predict(x_stress)[:,4],0,1)

    upstream=HeuristicLabeler()
    old_stress=np.asarray([float(upstream.label(t).clickbait) for t in stress_text])
    frozen_rules=np.asarray([float(score_clickbait(t)) for t in stress_text])

    # OOF rows need continuous targets from training.
    train_eval=[{**r,'target':float(r['clickbait'])} for r in train]
    result={
        'status':'development_only_supervised_clickbait_not_final_gold',
        'embedding_model':args.model,
        'embedding_revision':revision,
        'train_n':128,
        'train_balance':{'positive':64,'negative':64},
        'note':'Stress-32 has already been inspected and is now development/tuning data, not an untouched holdout.',
        'oof_5fold_on_training':{
            'e5_logistic':evaluate(e5_oof,train_eval),
            'tfidf_logistic':evaluate(tfidf_oof,train_eval),
        },
        'stress32':{
            'e5_logistic':evaluate(e5_stress,stress),
            'tfidf_logistic':evaluate(tfidf_stress,stress),
            'semantic_knn_candidate_v3':evaluate(semantic_stress,stress),
            'upstream_heuristic_v1':evaluate(old_stress,stress),
            'frozen_presentation_rules_v1':evaluate(frozen_rules,stress),
        },
    }
    ranked=sorted(
        [('e5_logistic',result['stress32']['e5_logistic']),('tfidf_logistic',result['stress32']['tfidf_logistic'])],
        key=lambda kv:(-kv[1]['f1'],-kv[1]['roc_auc'],kv[1]['brier'])
    )
    result['development_recommendation']=ranked[0][0]

    out=ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=[
        '# Dedicated clickbait classifier benchmark','',
        '> Development-only. Stress-32 was inspected before this training corpus was authored, so it is tuning data, not final evaluation.','',
        '## 5-fold OOF on clickbait training corpus','',
        '| Head | Accuracy | Precision | Recall | F1 | ROC-AUC | Brier |','|---|---:|---:|---:|---:|---:|---:|'
    ]
    for name,r in result['oof_5fold_on_training'].items():
        lines.append(f"| {name} | {r['accuracy']:.3f} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} | {r['roc_auc']:.3f} | {r['brier']:.3f} |")
    lines += ['', '## Stress-32 development comparison','', '| Method | Accuracy | Precision | Recall | F1 | ROC-AUC | Brier | MAE | FP | FN |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,r in result['stress32'].items():
        lines.append(f"| {name} | {r['accuracy']:.3f} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} | {r['roc_auc']:.3f} | {r['brier']:.3f} | {r['mae_to_continuous_target']:.3f} | {r['false_positive_count']} | {r['false_negative_count']} |")
    lines += ['',f"Development recommendation: `{result['development_recommendation']}`",'', '## Recommended-head stress failures','']
    for f in result['stress32'][result['development_recommendation']]['failures']:
        lines.append(f"- `{f['id']}` gold={f['label']} score={f['score']:.3f}: {f['text']}")
    lines.append('')
    (ROOT/args.summary).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
