# PUSULA 2,000-post E5-base benchmark

> Uses the dataset-supplied `gercek_niyet` vectors as labels. This measures performance on the synthetic/curated PUSULA pool, not real-world user traffic.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`
Posts: **2000**; unique authors: **49**.

## Existing `tahmin_niyet` vs candidate

| Evaluation | Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |
|---|---|---:|---:|---:|---:|
| full pool | existing tahmin_niyet | 0.965 | 0.964 | 0.200 | 0.900 |
| author-group 5-fold | semantic_knn | 1.000 | 1.000 | 0.043 | 0.995 |
| author-group 5-fold | ridge | 0.943 | 0.939 | 0.095 | 0.972 |
| author-group 5-fold | hybrid | 1.000 | 1.000 | 0.046 | 0.994 |
| author-group 5-fold | logistic dominant | 1.000 | 1.000 | - | - |

Author-group classifier top-50% confidence accuracy: **1.000**.

## Random stratified upper-bound check

| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |
|---|---:|---:|---:|---:|
| semantic_knn | 1.000 | 1.000 | 0.042 | 0.995 |
| ridge | 0.985 | 0.984 | 0.086 | 0.978 |
| hybrid | 1.000 | 1.000 | 0.046 | 0.994 |
| logistic dominant | 1.000 | 1.000 | - | - |

## Clickbait diagnostic

`{'available': True, 'positive_n': 140, 'roc_auc': 1.0, 'f1': 1.0, 'accuracy': 1.0}`

Author-group CV is the primary development estimate because no author appears in both train and validation folds. Random stratified CV is shown only as an optimistic upper-bound check for template/style leakage.
