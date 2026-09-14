# Dataset V3 + multilingual-e5-base development benchmark

> Development-only. The hard-48 set is repeatedly inspected and is not final competition gold.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`

All scenarios use the same frozen encoder, classifier settings and k-NN k=7. The old 2,000-post templated pool is excluded.

| Training source | Classifier acc. | Classifier F1 | Top-50% conf. acc. | Hybrid acc. | Hybrid F1 | Hybrid 4D MAE | Hybrid cosine |
|---|---:|---:|---:|---:|---:|---:|---:|
| old_136_only | 0.688 | 0.688 | 0.792 | 0.500 | 0.475 | 0.176 | 0.886 |
| v3_128_only | 0.708 | 0.707 | 0.833 | 0.500 | 0.482 | 0.179 | 0.875 |
| v3_256_only | 0.625 | 0.637 | 0.875 | 0.521 | 0.491 | 0.175 | 0.885 |

## Margin-aware dominant classifier

### v3_128_only

| Label margin | Train n | Accuracy | Macro-F1 | Top-50% conf. acc. |
|---:|---:|---:|---:|---:|
| 0.15 | 128 | 0.708 | 0.707 | 0.833 |
| 0.25 | 126 | 0.708 | 0.707 | 0.833 |
| 0.35 | 110 | 0.562 | 0.557 | 0.708 |

### v3_256_only

| Label margin | Train n | Accuracy | Macro-F1 | Top-50% conf. acc. |
|---:|---:|---:|---:|---:|
| 0.15 | 255 | 0.625 | 0.637 | 0.875 |
| 0.25 | 247 | 0.688 | 0.685 | 0.875 |
| 0.35 | 221 | 0.688 | 0.691 | 0.875 |

## Policy

V3 tranche 2 deliberately targets teaching↔social and entertainment↔social boundary cases instead of merely adding more easy examples.
Ambiguous rows remain valuable for the 4D vector head. Margin-aware experiments test whether they should be excluded only from the auxiliary single-dominant classifier.
The old 2,000-post templated pool remains a baseline/demo fixture only and is not used to train these candidate models.
