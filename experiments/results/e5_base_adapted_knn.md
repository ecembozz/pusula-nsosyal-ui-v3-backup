# Task-adapted encoder + semantic k-NN pilot

> Development-only. The encoder sees only the 136 balanced development training examples. The 48 hard-style examples never receive gradient updates. They are still a repeatedly inspected development set, not a final untouched test set.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`
Training examples: **136**; hard-style development examples: **48**.
k-NN: **k=7**; hybrid classifier blend: **0.15**.

| Epoch | Loss | kNN acc. | kNN F1 | kNN MAE | kNN cosine | Hybrid acc. | Hybrid F1 | Hybrid MAE |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 (frozen) | - | 0.500 | 0.458 | 0.186 | 0.870 | 0.500 | 0.458 | 0.184 |
| 1 | 1.4817 | 0.479 | 0.425 | 0.187 | 0.869 | 0.458 | 0.415 | 0.184 |
| 2 | 1.4559 | 0.479 | 0.425 | 0.184 | 0.873 | 0.479 | 0.425 | 0.182 |
| 3 | 1.4322 | 0.458 | 0.415 | 0.179 | 0.877 | 0.458 | 0.415 | 0.177 |
| 4 | 1.4060 | 0.458 | 0.415 | 0.177 | 0.877 | 0.458 | 0.415 | 0.175 |
| 5 | 1.3833 | 0.458 | 0.416 | 0.175 | 0.879 | 0.458 | 0.416 | 0.173 |

## Best development checkpoint

Epoch **2**: hybrid accuracy **0.479**, macro-F1 **0.425**, 4D MAE **0.182**, cosine **0.879**.
