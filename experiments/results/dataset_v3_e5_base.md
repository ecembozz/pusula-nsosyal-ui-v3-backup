# Dataset V3 + multilingual-e5-base development benchmark

> Development-only. The hard-48 set is repeatedly inspected and is not final competition gold.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`

All scenarios use the same frozen encoder, classifier settings and k-NN k=7. The old 2,000-post templated pool is excluded.

| Training source | Classifier acc. | Classifier F1 | Top-50% conf. acc. | Hybrid acc. | Hybrid F1 | Hybrid 4D MAE | Hybrid cosine |
|---|---:|---:|---:|---:|---:|---:|---:|
| old_136_only | 0.688 | 0.688 | 0.792 | 0.500 | 0.475 | 0.176 | 0.886 |
| v3_128_only | 0.708 | 0.707 | 0.833 | 0.500 | 0.482 | 0.179 | 0.875 |
| v3_256_only | 0.625 | 0.637 | 0.875 | 0.521 | 0.491 | 0.175 | 0.885 |

## Policy

V3 tranche 2 deliberately targets teaching↔social and entertainment↔social boundary cases instead of merely adding more easy examples.
The old 2,000-post templated pool remains a baseline/demo fixture only and is not used to train these candidate models.
