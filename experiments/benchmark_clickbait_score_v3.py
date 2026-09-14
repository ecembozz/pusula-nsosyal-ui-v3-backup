from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import f1_score, mean_absolute_error, mean_squared_error, precision_score, recall_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.neighbors import KNeighborsRegressor

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT/'experiments') not in sys.path:
    sys.path.insert(0,str(ROOT/'experiments'))
from benchmark_supervised_embeddings import encode_texts, read_jsonl

BASE_FILES=[
    ROOT/'data/v4_calibrated/clickbait_train_pos_a.jsonl',
    ROOT/'data/v4_calibrated/clickbait_train_pos_b.jsonl',
    ROOT/'data/v4_calibrated/clickbait_train_neg_a.jsonl',
    ROOT/'data/v4_calibrated/clickbait_train_neg_b.jsonl',
]
HARDNEG=ROOT/'data/v4_calibrated/clickbait_feed_hardneg_v2.jsonl'
EVAL=ROOT/'data/dev_labels/v4_clickbait_feed_eval_64.jsonl'
BACKGROUND=ROOT/'data/v2_realistic/raw_posts.jsonl'


def load_many(paths):
    rows=[]
    for p in paths:
        rows.extend(list(read_jsonl(p)))
    return rows


def evaluate(scores,rows):
    s=np.clip(np.asarray(scores,dtype=float),0,1)
    target=np.asarray([float(r['clickbait']) for r in rows],dtype=float)
    y=np.asarray([int(r['label']) for r in rows],dtype=int)
    pred=(s>=.50).astype(int)
    rho=float(spearmanr(target,s).statistic)
    if not np.isfinite(rho): rho=0.0
    return {
        'mae':float(mean_absolute_error(target,s)),
        'rmse':float(np.sqrt(mean_squared_error(target,s))),
        'spearman':rho,
        'precision_at_0_50':float(precision_score(y,pred,zero_division=0)),
        'recall_at_0_50':float(recall_score(y,pred,zero_division=0)),
        'f1_at_0_50':float(f1_score(y,pred,zero_division=0)),
        'mean_positive':float(np.mean(s[y==1])),
        'mean_negative':float(np.mean(s[y==0])),
        'fp':int(np.sum((pred==1)&(y==0))),
        'fn':int(np.sum((pred==0)&(y==1))),
    }


def bgstats(scores):
    s=np.clip(np.asarray(scores,dtype=float),0,1)
    return {
        'mean':float(np.mean(s)),
        'median':float(np.median(s)),
        'p90':float(np.quantile(s,.90)),
        'p95':float(np.quantile(s,.95)),
        'max':float(np.max(s)),
        'ge_0_50':int(np.sum(s>=.50)),
        'ge_0_65':int(np.sum(s>=.65)),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',default='intfloat/multilingual-e5-base')
    ap.add_argument('--output',default='experiments/results/clickbait_score_v3.json')
    ap.add_argument('--summary',default='experiments/results/clickbait_score_v3.md')
    args=ap.parse_args()

    train=load_many(BASE_FILES)+list(read_jsonl(HARDNEG))
    eva=list(read_jsonl(EVAL))
    bg=list(read_jsonl(BACKGROUND))
    if len(train)!=192 or sum(int(r['label']) for r in train)!=64 or len(eva)!=64 or len(bg)!=320:
        raise SystemExit('unexpected clickbait benchmark dataset sizes')

    train_text=[r['text'] for r in train]
    eval_text=[r['text'] for r in eva]
    bg_text=[r['text'] for r in bg]
    x,revision=encode_texts(train_text+eval_text+bg_text,args.model,batch_size=16)
    xt=x[:192]; xe=x[192:256]; xb=x[256:]
    target=np.asarray([float(r['clickbait']) for r in train],dtype=float)
    binary=np.asarray([int(r['label']) for r in train],dtype=int)

    methods={}
    for alpha in (0.05,0.2,1.0,5.0):
        m=Ridge(alpha=alpha)
        m.fit(xt,target)
        methods[f'e5_ridge_{alpha:g}']=(np.clip(m.predict(xe),0,1),np.clip(m.predict(xb),0,1),m)

    for k in (5,7,11):
        m=KNeighborsRegressor(n_neighbors=k,weights='distance',metric='cosine')
        m.fit(xt,target)
        methods[f'e5_knn_k{k}']=(np.clip(m.predict(xe),0,1),np.clip(m.predict(xb),0,1),m)

    # Classification probability remains as a reference, not automatically a quality score.
    logit=LogisticRegression(C=3.0,class_weight='balanced',max_iter=5000,solver='liblinear',random_state=42)
    logit.fit(xt,binary)
    methods['e5_logistic_balanced_probability']=(logit.predict_proba(xe)[:,1],logit.predict_proba(xb)[:,1],logit)

    result={
        'status':'development_only_clickbait_continuous_score_benchmark',
        'embedding_model':args.model,
        'embedding_revision':revision,
        'train_n':192,
        'feed_eval_n':64,
        'background_n':320,
        'methods':{},
    }
    for name,(es,bs,_) in methods.items():
        result['methods'][name]={'feed_eval':evaluate(es,eva),'background':bgstats(bs)}

    # We need a continuous quality signal: prioritize low MAE, then high F1,
    # then lower normal-feed background pressure.
    reg_names=[n for n in methods if n!='e5_logistic_balanced_probability']
    ranked=sorted(reg_names,key=lambda n:(result['methods'][n]['feed_eval']['mae'],-result['methods'][n]['feed_eval']['f1_at_0_50'],result['methods'][n]['background']['mean'],result['methods'][n]['background']['ge_0_50']))
    result['development_recommendation']=ranked[0]

    # 5-fold regression OOF for the candidate regressors.
    cv=KFold(n_splits=5,shuffle=True,random_state=42)
    oof={}
    for name in reg_names:
        if name.startswith('e5_ridge_'):
            alpha=float(name.rsplit('_',1)[1])
            model=Ridge(alpha=alpha)
        else:
            k=int(name.rsplit('k',1)[1])
            model=KNeighborsRegressor(n_neighbors=k,weights='distance',metric='cosine')
        s=np.clip(cross_val_predict(model,xt,target,cv=cv),0,1)
        oof[name]=evaluate(s,train)
    result['oof_5fold_train']=oof

    out=ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=['# Continuous clickbait score benchmark V3','',
        '> Development-only. Goal: estimate the existing 0–1 clickbait quality signal, not merely a balanced-class probability.','',
        '## Feed-style development eval','',
        '| Method | MAE | RMSE | Spearman | F1@.50 | Prec | Recall | Mean pos | Mean neg | FP | FN |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,r in result['methods'].items():
        m=r['feed_eval']
        lines.append(f"| {name} | {m['mae']:.3f} | {m['rmse']:.3f} | {m['spearman']:.3f} | {m['f1_at_0_50']:.3f} | {m['precision_at_0_50']:.3f} | {m['recall_at_0_50']:.3f} | {m['mean_positive']:.3f} | {m['mean_negative']:.3f} | {m['fp']} | {m['fn']} |")
    lines += ['', '## Unlabeled V2-320 background sanity','',
        '| Method | Mean | Median | P90 | P95 | >=.50 | >=.65 | Max |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for name,r in result['methods'].items():
        b=r['background']
        lines.append(f"| {name} | {b['mean']:.3f} | {b['median']:.3f} | {b['p90']:.3f} | {b['p95']:.3f} | {b['ge_0_50']} | {b['ge_0_65']} | {b['max']:.3f} |")
    lines += ['', '## 5-fold OOF on 192-row continuous training target','',
        '| Method | MAE | RMSE | Spearman | F1@.50 |','|---|---:|---:|---:|---:|']
    for name,m in oof.items():
        lines.append(f"| {name} | {m['mae']:.3f} | {m['rmse']:.3f} | {m['spearman']:.3f} | {m['f1_at_0_50']:.3f} |")
    lines += ['',f"Development recommendation: `{result['development_recommendation']}`",'']
    (ROOT/args.summary).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
