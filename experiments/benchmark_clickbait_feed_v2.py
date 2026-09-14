from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import FeatureUnion, Pipeline

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


def tfidf_model(class_weight=None):
    return Pipeline([
        ('features',FeatureUnion([
            ('char',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=16000,sublinear_tf=True)),
            ('word',TfidfVectorizer(analyzer='word',ngram_range=(1,2),min_df=2,max_features=10000,sublinear_tf=True)),
        ])),
        ('clf',LogisticRegression(C=3.0,class_weight=class_weight,max_iter=5000,solver='liblinear',random_state=42)),
    ])


def e5_model(class_weight=None):
    return LogisticRegression(C=3.0,class_weight=class_weight,max_iter=5000,solver='liblinear',random_state=42)


def metrics(scores,rows):
    scores=np.clip(np.asarray(scores,dtype=float),0,1)
    y=np.asarray([int(r['label']) for r in rows],dtype=int)
    pred=(scores>=.5).astype(int)
    return {
        'accuracy':float(accuracy_score(y,pred)),
        'precision':float(precision_score(y,pred,zero_division=0)),
        'recall':float(recall_score(y,pred,zero_division=0)),
        'f1':float(f1_score(y,pred,zero_division=0)),
        'roc_auc':float(roc_auc_score(y,scores)),
        'brier':float(brier_score_loss(y,scores)),
        'false_positive_count':int(np.sum((pred==1)&(y==0))),
        'false_negative_count':int(np.sum((pred==0)&(y==1))),
        'mean_positive':float(np.mean(scores[y==1])),
        'mean_negative':float(np.mean(scores[y==0])),
        'failures':[{'id':rows[i]['id'],'label':int(y[i]),'score':float(scores[i]),'text':rows[i]['text']} for i in range(len(rows)) if pred[i]!=y[i]],
    }


def background_stats(scores,rows):
    scores=np.clip(np.asarray(scores,dtype=float),0,1)
    order=np.argsort(-scores)
    return {
        'n':len(rows),
        'mean':float(np.mean(scores)),
        'median':float(np.median(scores)),
        'p90':float(np.quantile(scores,.90)),
        'p95':float(np.quantile(scores,.95)),
        'max':float(np.max(scores)),
        'ge_0_50':int(np.sum(scores>=.50)),
        'ge_0_65':int(np.sum(scores>=.65)),
        'ge_0_75':int(np.sum(scores>=.75)),
        'top12':[{'id':rows[int(i)]['id'],'score':float(scores[int(i)]),'text':rows[int(i)]['text']} for i in order[:12]],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',default='intfloat/multilingual-e5-base')
    ap.add_argument('--output',default='experiments/results/clickbait_feed_v2.json')
    ap.add_argument('--summary',default='experiments/results/clickbait_feed_v2.md')
    args=ap.parse_args()

    base=load_many(BASE_FILES)
    hard=list(read_jsonl(HARDNEG))
    aug=base+hard
    eva=list(read_jsonl(EVAL))
    bg=list(read_jsonl(BACKGROUND))
    if len(base)!=128 or sum(int(r['label']) for r in base)!=64:
        raise SystemExit('base clickbait set must remain 128 / 64 positive')
    if len(hard)!=64 or any(int(r['label'])!=0 for r in hard):
        raise SystemExit('feed hard-negative set must be exactly 64 negatives')
    if len(aug)!=192 or sum(int(r['label']) for r in aug)!=64:
        raise SystemExit('augmented clickbait train must be 192 rows / 64 positive')
    if len(eva)!=64 or sum(int(r['label']) for r in eva)!=32:
        raise SystemExit('feed eval must be 64 balanced rows')
    if len(bg)!=320:
        raise SystemExit('background corpus must remain 320 rows')

    base_text=[r['text'] for r in base]
    aug_text=[r['text'] for r in aug]
    eval_text=[r['text'] for r in eva]
    bg_text=[r['text'] for r in bg]

    # Encode each unique block once. First 128 augmented rows are the original base set.
    all_text=aug_text+eval_text+bg_text
    x,revision=encode_texts(all_text,args.model,batch_size=16)
    x_aug=x[:192]
    x_base=x_aug[:128]
    x_eval=x[192:256]
    x_bg=x[256:]
    y_base=np.asarray([int(r['label']) for r in base],dtype=int)
    y_aug=np.asarray([int(r['label']) for r in aug],dtype=int)

    methods={}

    base_e5=e5_model('balanced')
    base_e5.fit(x_base,y_base)
    methods['e5_base128_balanced']=(base_e5.predict_proba(x_eval)[:,1],base_e5.predict_proba(x_bg)[:,1])

    e5_unweighted=e5_model(None)
    e5_unweighted.fit(x_aug,y_aug)
    methods['e5_aug192_unweighted']=(e5_unweighted.predict_proba(x_eval)[:,1],e5_unweighted.predict_proba(x_bg)[:,1])

    e5_balanced=e5_model('balanced')
    e5_balanced.fit(x_aug,y_aug)
    methods['e5_aug192_balanced']=(e5_balanced.predict_proba(x_eval)[:,1],e5_balanced.predict_proba(x_bg)[:,1])

    tf_unweighted=tfidf_model(None)
    tf_unweighted.fit(aug_text,y_aug)
    methods['tfidf_aug192_unweighted']=(tf_unweighted.predict_proba(eval_text)[:,1],tf_unweighted.predict_proba(bg_text)[:,1])

    tf_balanced=tfidf_model('balanced')
    tf_balanced.fit(aug_text,y_aug)
    methods['tfidf_aug192_balanced']=(tf_balanced.predict_proba(eval_text)[:,1],tf_balanced.predict_proba(bg_text)[:,1])

    # Lightweight agreement blend; still offline and deterministic.
    methods['blend_e5_tfidf_unweighted']=(
        .70*methods['e5_aug192_unweighted'][0]+.30*methods['tfidf_aug192_unweighted'][0],
        .70*methods['e5_aug192_unweighted'][1]+.30*methods['tfidf_aug192_unweighted'][1],
    )

    result={
        'status':'development_only_feed_distribution_clickbait_benchmark',
        'embedding_model':args.model,
        'embedding_revision':revision,
        'base_train_n':128,
        'feed_hard_negative_n':64,
        'augmented_train_n':192,
        'augmented_balance':{'positive':64,'negative':128},
        'feed_eval_n':64,
        'background_n':320,
        'note':'Feed eval and V2 background are development diagnostics, not final human gold.',
        'methods':{},
    }
    for name,(es,bs) in methods.items():
        result['methods'][name]={'feed_eval':metrics(es,eva),'background':background_stats(bs,bg)}

    # Primary criterion is balanced feed-eval F1/AUC. If essentially tied,
    # prefer lower false-positive pressure on the unlabeled normal-feed background.
    ranked=sorted(result['methods'].items(),key=lambda kv:(-kv[1]['feed_eval']['f1'],-kv[1]['feed_eval']['roc_auc'],kv[1]['background']['ge_0_50'],kv[1]['feed_eval']['brier']))
    result['development_recommendation']=ranked[0][0]

    # OOF only for the recommended training family candidates; this catches blatant memorization.
    cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
    oof={}
    for name,model,data in [
        ('e5_aug192_unweighted',e5_model(None),x_aug),
        ('e5_aug192_balanced',e5_model('balanced'),x_aug),
        ('tfidf_aug192_unweighted',tfidf_model(None),aug_text),
    ]:
        scores=cross_val_predict(model,data,y_aug,cv=cv,method='predict_proba')[:,1]
        oof[name]=metrics(scores,aug)
    result['oof_5fold_augmented_train']=oof

    out=ROOT/args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=['# Clickbait feed-distribution benchmark V2','',
        '> Development-only. This benchmark was created after Candidate V4 exposed false-positive pressure on normal-feed text. It is not final competition evidence.','',
        '## Feed-style development eval','',
        '| Method | Acc | Prec | Recall | F1 | ROC-AUC | Brier | FP | FN |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,r in result['methods'].items():
        m=r['feed_eval']
        lines.append(f"| {name} | {m['accuracy']:.3f} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['roc_auc']:.3f} | {m['brier']:.3f} | {m['false_positive_count']} | {m['false_negative_count']} |")
    lines += ['', '## Unlabeled V2-320 background sanity','',
        '| Method | Mean | Median | P90 | P95 | >=.50 | >=.65 | >=.75 | Max |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,r in result['methods'].items():
        b=r['background']
        lines.append(f"| {name} | {b['mean']:.3f} | {b['median']:.3f} | {b['p90']:.3f} | {b['p95']:.3f} | {b['ge_0_50']} | {b['ge_0_65']} | {b['ge_0_75']} | {b['max']:.3f} |")
    lines += ['', '## 5-fold OOF on augmented 192-row train','',
        '| Method | Acc | Prec | Recall | F1 | ROC-AUC | Brier |','|---|---:|---:|---:|---:|---:|---:|']
    for name,m in oof.items():
        lines.append(f"| {name} | {m['accuracy']:.3f} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['roc_auc']:.3f} | {m['brier']:.3f} |")
    lines += ['',f"Development recommendation: `{result['development_recommendation']}`",'', '## Recommended method: highest background scores','']
    for r in result['methods'][result['development_recommendation']]['background']['top12']:
        lines.append(f"- `{r['id']}` score={r['score']:.3f}: {r['text']}")
    lines += ['', '## Recommended method: feed-eval failures','']
    for r in result['methods'][result['development_recommendation']]['feed_eval']['failures']:
        lines.append(f"- `{r['id']}` gold={r['label']} score={r['score']:.3f}: {r['text']}")
    lines.append('')
    (ROOT/args.summary).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
