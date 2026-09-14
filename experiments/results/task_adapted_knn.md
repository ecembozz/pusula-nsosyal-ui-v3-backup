# Task-adapted encoder + semantic k-NN pilot

> Development-only. The encoder sees only the 136 balanced development training examples. The 48 hard-style examples never receive gradient updates. They are still a repeatedly inspected development set, not a final untouched test set.

Encoder: `intfloat/multilingual-e5-small` @ `614241f622f53c4eeff9890bdc4f31cfecc418b3`
Training examples: **136**; hard-style development examples: **48**.
k-NN: **k=7**; hybrid classifier blend: **0.15**.

| Epoch | Loss | kNN acc. | kNN F1 | kNN MAE | kNN cosine | Hybrid acc. | Hybrid F1 | Hybrid MAE |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 (frozen) | - | 0.479 | 0.432 | 0.204 | 0.853 | 0.479 | 0.432 | 0.201 |
| 1 | 1.4827 | 0.479 | 0.432 | 0.205 | 0.852 | 0.479 | 0.432 | 0.202 |
| 2 | 1.4533 | 0.458 | 0.400 | 0.205 | 0.849 | 0.458 | 0.400 | 0.201 |
| 3 | 1.4218 | 0.479 | 0.425 | 0.207 | 0.844 | 0.479 | 0.425 | 0.203 |
| 4 | 1.3873 | 0.479 | 0.413 | 0.197 | 0.848 | 0.479 | 0.413 | 0.193 |
| 5 | 1.3299 | 0.438 | 0.356 | 0.204 | 0.838 | 0.438 | 0.356 | 0.198 |
| 6 | 1.2390 | 0.521 | 0.437 | 0.196 | 0.846 | 0.521 | 0.437 | 0.189 |
| 7 | 1.1260 | 0.521 | 0.448 | 0.198 | 0.842 | 0.521 | 0.448 | 0.191 |
| 8 | 1.0140 | 0.500 | 0.416 | 0.197 | 0.841 | 0.500 | 0.416 | 0.189 |

## Best development checkpoint

Epoch **7**: hybrid accuracy **0.521**, macro-F1 **0.448**, 4D MAE **0.191**, cosine **0.851**.
