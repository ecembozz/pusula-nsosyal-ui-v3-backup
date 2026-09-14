# PUSULA 2,000 → hard-48 cross-style transfer

> Train labels come from the pool's dataset-supplied `gercek_niyet`. The 48 hard-style examples are excluded from training. They are a repeatedly inspected development set, not a final untouched test set.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`
Training pool: **2000**; hard-style development set: **48**.

| Method | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine |
|---|---:|---:|---:|---:|
| semantic_knn | 0.479 | 0.505 | 0.254 | 0.748 |
| ridge | 0.521 | 0.539 | 0.246 | 0.820 |
| hybrid | 0.479 | 0.505 | 0.242 | 0.773 |
| logistic dominant | 0.396 | 0.425 | - | - |

Classifier top-50% confidence accuracy: **0.458**.
Per-class classifier accuracy: `{'ogretici': 0.3333333333333333, 'eglendirici': 0.23076923076923078, 'haber': 0.625, 'sosyal': 0.4666666666666667}`
OOD rate against the 2k pool: **1.000**; mean nearest cosine: **0.880**.

This is the key style-transfer development benchmark: unlike the 2k cross-validation result, these evaluation texts were independently authored in a different style and are not templated copies of the pool.
