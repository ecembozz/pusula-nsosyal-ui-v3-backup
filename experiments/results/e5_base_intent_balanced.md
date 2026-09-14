# Intent-balanced style-diverse supervised pilot

> Development-only. Training labels are assistant-authored synthetic development labels; the 48 hard labels are single-annotator drafts. Not final competition metrics.

Embedding: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`
Balanced training: **136** = `{np.str_('ogretici'): 34, np.str_('eglendirici'): 34, np.str_('haber'): 34, np.str_('sosyal'): 34}`
Hard evaluation: **48** = `{np.str_('sosyal'): 15, np.str_('ogretici'): 12, np.str_('eglendirici'): 13, np.str_('haber'): 8}`

## 136 intent-balanced examples only

| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE |
|---|---:|---:|---:|---:|---:|
| semantic_knn | 0.542 | 0.521 | 0.180 | 0.872 | 0.078 |
| weighted_ridge | 0.312 | 0.119 | 0.237 | 0.846 | 0.059 |
| hybrid_knn_logistic | 0.562 | 0.555 | 0.173 | 0.889 | 0.078 |
| ensemble_knn_ridge_logistic | 0.500 | 0.473 | 0.182 | 0.892 | 0.072 |

Dominant-only balanced logistic: accuracy **0.688**, macro-F1 **0.688**, top-50% confidence accuracy **0.792**.
Per-class: `{'ogretici': 0.3333333333333333, 'eglendirici': 0.7692307692307693, 'haber': 0.875, 'sosyal': 0.8}`

## 136 balanced + 96 earlier base examples

| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE |
|---|---:|---:|---:|---:|---:|
| semantic_knn | 0.479 | 0.408 | 0.174 | 0.892 | 0.034 |
| weighted_ridge | 0.333 | 0.179 | 0.227 | 0.861 | 0.035 |
| hybrid_knn_logistic | 0.521 | 0.500 | 0.169 | 0.909 | 0.034 |
| ensemble_knn_ridge_logistic | 0.479 | 0.420 | 0.180 | 0.905 | 0.032 |

Dominant-only balanced logistic: accuracy **0.625**, macro-F1 **0.643**, top-50% confidence accuracy **0.750**.
Per-class: `{'ogretici': 0.4166666666666667, 'eglendirici': 0.6153846153846154, 'haber': 0.875, 'sosyal': 0.6666666666666666}`

## Interpretation

This experiment asks whether intent-balanced, style-diverse supervision transfers better to the hand-written hard-style development set than topic-balanced supervision. It is explicitly a model-selection experiment and cannot be used as a final competition claim.
