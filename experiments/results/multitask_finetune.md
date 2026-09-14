# Multitask encoder fine-tuning pilot

> Development-only. Trained only on the 136 intent-balanced assistant-authored development examples. The 48 hard-style examples remain completely held out from gradient updates. Not final competition metrics.

Base encoder: `intfloat/multilingual-e5-small` @ `614241f622f53c4eeff9890bdc4f31cfecc418b3`
Unfrozen transformer layers: **last 2**
Trainable parameters: **3,568,521 / 117,657,225 (3.03%)**
Training examples: **136**; hard-style held-out evaluation: **48**.

## Held-out hard-style result

- Dominant accuracy: **0.542**
- Macro-F1: **0.536**
- 4D intent MAE: **0.269**
- Mean intent cosine: **0.814**
- Clickbait MAE: **0.260**
- OOD rate: **0.083**
- Accuracy at 50% confidence coverage: **0.583**
- Per-class accuracy: `{'ogretici': 0.25, 'eglendirici': 0.15384615384615385, 'haber': 1.0, 'sosyal': 0.8666666666666667}`

## Training curve

| Epoch | Train loss | Hard acc. | Hard macro-F1 | 4D MAE | Cosine |
|---:|---:|---:|---:|---:|---:|
| 1 | 1.2560 | 0.354 | 0.290 | 0.308 | 0.776 |
| 2 | 1.2123 | 0.375 | 0.267 | 0.296 | 0.787 |
| 3 | 1.1718 | 0.521 | 0.558 | 0.287 | 0.795 |
| 4 | 1.1439 | 0.521 | 0.522 | 0.281 | 0.800 |
| 5 | 1.1221 | 0.542 | 0.488 | 0.277 | 0.803 |
| 6 | 1.1017 | 0.583 | 0.561 | 0.274 | 0.806 |
| 7 | 1.0837 | 0.562 | 0.593 | 0.273 | 0.808 |
| 8 | 1.0672 | 0.562 | 0.539 | 0.271 | 0.811 |
| 9 | 1.0492 | 0.521 | 0.527 | 0.270 | 0.813 |
| 10 | 1.0395 | 0.542 | 0.536 | 0.269 | 0.814 |

This is a model-selection experiment only. Because the same 48 hard examples are inspected across development rounds, they are not a final untouched test set.
