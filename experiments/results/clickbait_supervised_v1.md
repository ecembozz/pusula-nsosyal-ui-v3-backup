# Dedicated clickbait classifier benchmark

> Development-only. Stress-32 was inspected before this training corpus was authored, so it is tuning data, not final evaluation.

## 5-fold OOF on clickbait training corpus

| Head | Accuracy | Precision | Recall | F1 | ROC-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|
| e5_logistic | 0.953 | 0.939 | 0.969 | 0.954 | 0.989 | 0.133 |
| tfidf_logistic | 0.844 | 0.806 | 0.906 | 0.853 | 0.955 | 0.118 |

## Stress-32 development comparison

| Method | Accuracy | Precision | Recall | F1 | ROC-AUC | Brier | MAE | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e5_logistic | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.100 | 0.188 | 0 | 0 |
| tfidf_logistic | 0.969 | 0.941 | 1.000 | 0.970 | 0.992 | 0.059 | 0.131 | 1 | 0 |
| semantic_knn_candidate_v3 | 0.562 | 1.000 | 0.125 | 0.222 | 0.820 | 0.324 | 0.339 | 0 | 14 |
| upstream_heuristic_v1 | 0.562 | 0.667 | 0.250 | 0.364 | 0.340 | 0.453 | 0.452 | 2 | 12 |
| frozen_presentation_rules_v1 | 0.344 | 0.000 | 0.000 | 0.000 | 0.111 | 0.509 | 0.525 | 5 | 16 |

Development recommendation: `e5_logistic`

## Recommended-head stress failures

