# Class-balanced supervised diagnostic

> Development-only; single-annotator draft labels. Not final competition metrics.

Embedding: `intfloat/multilingual-e5-small` @ `614241f622f53c4eeff9890bdc4f31cfecc418b3`
Train: **96**; hard-style test: **48**.
Original train distribution: `{np.str_('sosyal'): 54, np.str_('ogretici'): 15, np.str_('eglendirici'): 11, np.str_('haber'): 16}`
Balanced k-NN resample: `{np.str_('ogretici'): 54, np.str_('eglendirici'): 54, np.str_('haber'): 54, np.str_('sosyal'): 54}`

| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |
|---|---:|---:|---:|---:|
| weighted_ridge_vector | 0.312 | 0.119 | 0.249 | 0.826 |
| balanced_knn_vector | 0.458 | 0.431 | 0.204 | 0.826 |
| hybrid_knn_plus_logistic | 0.438 | 0.401 | 0.207 | 0.844 |

## Balanced dominant-intent classifier

Accuracy: **0.375**; macro-F1: **0.404**; top-50%-confidence accuracy: **0.542**.
Per-class accuracy: `{'ogretici': 0.5, 'eglendirici': 0.15384615384615385, 'haber': 0.625, 'sosyal': 0.3333333333333333}`

This diagnostic tests whether the previous collapse was mainly caused by intent imbalance. It does not replace a larger, independently labeled development set.
