# Dataset V3 + multilingual-e5-base development benchmark

> Development-only. The hard-48 set is repeatedly inspected and is not final competition gold.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`

| Training source | Classifier acc. | Classifier F1 | Top-50% conf. acc. | Hybrid acc. | Hybrid F1 | Hybrid 4D MAE | Hybrid cosine |
|---|---:|---:|---:|---:|---:|---:|---:|
| old_136_only | 0.688 | 0.688 | 0.792 | 0.562 | 0.555 | 0.173 | 0.888 |
| v3_128_only | 0.708 | 0.707 | 0.833 | 0.562 | 0.552 | 0.178 | 0.873 |
| combined_264 | 0.688 | 0.688 | 0.833 | 0.542 | 0.530 | 0.173 | 0.882 |

## Policy

The old 2,000-post templated pool is intentionally excluded from these training scenarios. It remains a baseline/demo fixture only.
