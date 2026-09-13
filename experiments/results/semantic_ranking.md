# Direct semantic ranking benchmark

> Development-only. This benchmark isolates the semantic intent component of PUSULA. Freshness, engagement and diversity terms are intentionally held out so the intent-vector quality can be measured directly.

Gold relevance is cosine similarity between each simulated user-intent profile and the draft gold 4D post vector. Predicted relevance uses the model-produced 4D vector.

| Encoder / vector method | mean nDCG@10 | mean top-10 overlap | mean Spearman | pairwise concordance | worst nDCG@10 |
|---|---:|---:|---:|---:|---:|
| intfloat/multilingual-e5-small / knn_vector | 0.832 | 0.562 | 0.483 | 0.670 | 0.663 |
| intfloat/multilingual-e5-small / logistic_probability_vector | 0.850 | 0.538 | 0.539 | 0.690 | 0.659 |
| intfloat/multilingual-e5-small / hybrid_vector | 0.847 | 0.562 | 0.498 | 0.675 | 0.699 |
| intfloat/multilingual-e5-base / knn_vector | 0.882 | 0.588 | 0.597 | 0.717 | 0.743 |
| intfloat/multilingual-e5-base / logistic_probability_vector | 0.907 | 0.637 | 0.616 | 0.723 | 0.741 |
| intfloat/multilingual-e5-base / hybrid_vector | 0.885 | 0.588 | 0.622 | 0.726 | 0.689 |

## User-intent profiles

- `pure_ogretici`: `[1.0, 0.0, 0.0, 0.0]`
- `pure_eglendirici`: `[0.0, 1.0, 0.0, 0.0]`
- `pure_haber`: `[0.0, 0.0, 1.0, 0.0]`
- `pure_sosyal`: `[0.0, 0.0, 0.0, 1.0]`
- `ogretici_haber`: `[0.8, 0.05, 0.65, 0.1]`
- `ogretici_sosyal`: `[0.8, 0.05, 0.05, 0.6]`
- `eglendirici_sosyal`: `[0.05, 0.8, 0.05, 0.65]`
- `haber_sosyal`: `[0.1, 0.05, 0.85, 0.5]`

## Guardrails

- The 48 hard cases are architecture-development data, not an untouched final test set.
- These metrics evaluate only semantic intent ordering. A later end-to-end ranking test must reintroduce freshness, engagement, clickbait penalty and diversity constraints.
- Final claims require a new independently annotated holdout after architecture selection is frozen.
