# Intent-balanced style-diverse supervised pilot

> Development-only. Training labels are assistant-authored synthetic development labels; the 48 hard labels are single-annotator drafts. Not final competition metrics.

Embedding: `intfloat/multilingual-e5-small` @ `614241f622f53c4eeff9890bdc4f31cfecc418b3`
Balanced training: **136** = `{np.str_('ogretici'): 34, np.str_('eglendirici'): 34, np.str_('haber'): 34, np.str_('sosyal'): 34}`
Hard evaluation: **48** = `{np.str_('sosyal'): 15, np.str_('ogretici'): 12, np.str_('eglendirici'): 13, np.str_('haber'): 8}`

## 136 intent-balanced examples only

| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE |
|---|---:|---:|---:|---:|---:|
| semantic_knn | 0.479 | 0.451 | 0.211 | 0.841 | 0.081 |
| weighted_ridge | 0.312 | 0.119 | 0.240 | 0.841 | 0.057 |
| hybrid_knn_logistic | 0.500 | 0.484 | 0.200 | 0.857 | 0.081 |
| ensemble_knn_ridge_logistic | 0.417 | 0.363 | 0.204 | 0.864 | 0.073 |

Dominant-only balanced logistic: accuracy **0.521**, macro-F1 **0.543**, top-50% confidence accuracy **0.625**.
Per-class: `{'ogretici': 0.3333333333333333, 'eglendirici': 0.38461538461538464, 'haber': 0.75, 'sosyal': 0.6666666666666666}`

## 136 balanced + 96 earlier base examples

| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE |
|---|---:|---:|---:|---:|---:|
| semantic_knn | 0.417 | 0.322 | 0.195 | 0.861 | 0.043 |
| weighted_ridge | 0.312 | 0.123 | 0.231 | 0.853 | 0.034 |
| hybrid_knn_logistic | 0.458 | 0.400 | 0.189 | 0.878 | 0.043 |
| ensemble_knn_ridge_logistic | 0.438 | 0.362 | 0.197 | 0.878 | 0.038 |

Dominant-only balanced logistic: accuracy **0.500**, macro-F1 **0.530**, top-50% confidence accuracy **0.708**.
Per-class: `{'ogretici': 0.4166666666666667, 'eglendirici': 0.46153846153846156, 'haber': 0.625, 'sosyal': 0.5333333333333333}`

## Interpretation

This experiment asks whether intent-balanced, style-diverse supervision transfers better to the hand-written hard-style development set than topic-balanced supervision. It is explicitly a model-selection experiment and cannot be used as a final competition claim.
