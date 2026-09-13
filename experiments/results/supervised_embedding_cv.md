# Supervised multilingual embedding pilot

> Development-only result. The 48 labels are single-annotator draft labels and are not final competition gold.

Embedding model: `intfloat/multilingual-e5-small`
Embedding revision: `614241f622f53c4eeff9890bdc4f31cfecc418b3`
Examples: **48**; evaluation: **4-fold stratified out-of-fold CV**.

| Head | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE | OOD rate | Acc @ 50% conf. |
|---|---:|---:|---:|---:|---:|---:|---:|
| ridge | 0.312 | 0.119 | 0.250 | 0.820 | 0.005 | 0.125 | 0.417 |
| semantic_knn | 0.417 | 0.348 | 0.196 | 0.868 | 0.005 | 0.125 | 0.375 |
| pca_mlp | 0.396 | 0.355 | 0.235 | 0.820 | 0.046 | 0.125 | 0.333 |

## Interpretation rules

- This pilot only tests whether supervised semantic embeddings are promising on the current 48-case development set.
- OOD is based on fold-local nearest-neighbour cosine similarity; it is a transparent screening signal, not a calibrated probability.
- No result from this file should be presented as final competition performance.
- If a supervised head shows a meaningful gain, expand the independently written labeled development corpus before tuning further.
