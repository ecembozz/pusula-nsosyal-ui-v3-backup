# PUSULA 2000-post E5-base end-to-end development benchmark

> The pool's `gercek_niyet` is treated as benchmark ground truth from the project dataset, but it is not independently double-annotated human gold. Do not present these values as final human-evaluation metrics.

Pinned source: `asimonmsz-design/pusula@78cdd15dd14adbed7e722a13b99171d84956f665` → `kod/veri/etiketli_havuz.json`
Pool: **2000 posts**. New semantic encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`.

## Intent-vector prediction

| Method | 4D MAE | Mean cosine | Dominant acc. | Macro-F1 |
|---|---:|---:|---:|---:|
| current_tahmin_niyet | 0.2002 | 0.9000 | 0.9650 | 0.9637 |
| e5_base_logistic_probability | 0.1826 | 0.8827 | 0.6460 | 0.6257 |

## Full PUSULA ranking (semantic + freshness + engagement + clickbait)

| Method | mean nDCG@20 | mean top-20 overlap | mean Spearman | pairwise | worst nDCG@20 |
|---|---:|---:|---:|---:|---:|
| current_tahmin_niyet | 0.9609 | 0.3812 | 0.8640 | 0.8549 | 0.8948 |
| e5_base_logistic_probability | 0.9671 | 0.4375 | 0.7911 | 0.8053 | 0.9103 |

## With category diversity cap (max 5/category in top 20)

| Method | mean diversified top-20 overlap | mean DCG ratio vs oracle | worst DCG ratio |
|---|---:|---:|---:|
| current_tahmin_niyet | 0.2938 | 0.9104 | 0.8607 |
| e5_base_logistic_probability | 0.1813 | 0.9000 | 0.8338 |

## Methodology guardrails

- Only the semantic vector differs between the two compared systems. Freshness, engagement and clickbait inputs are identical.
- Oracle ordering uses the same PUSULA formula with `gercek_niyet` substituted for the semantic vector.
- This is a large reproducible development benchmark, not final human gold evaluation.
