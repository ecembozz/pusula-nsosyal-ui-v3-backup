# Partial multilingual E5 multitask fine-tuning pilot

> Development-only model-selection experiment. The 48 hard-style labels remain single-annotator draft labels and are not final competition gold.

Encoder: `intfloat/multilingual-e5-small` @ `614241f622f53c4eeff9890bdc4f31cfecc418b3`
Training corpus: **136** intent-balanced/style-diverse examples; hard-style development set: **48** examples.
Internal split: **112 train / 24 validation**, stratified by dominant intent.

The hard-style set is not used for gradient updates, epoch selection, or early stopping.

| Variant | Unfrozen encoder layers | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE | Top-50% acc. | OOD rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| frozen_encoder_multitask | 0 | 0.375 | 0.375 | 0.258 | 0.817 | 0.345 | 0.417 | 0.042 |
| unfreeze_last_1_multitask | 1 | 0.417 | 0.404 | 0.264 | 0.814 | 0.375 | 0.458 | 0.042 |

## Per-class hard-style accuracy

- **frozen_encoder_multitask:** `{'ogretici': 0.25, 'eglendirici': 0.23076923076923078, 'haber': 0.375, 'sosyal': 0.6}`
- **unfreeze_last_1_multitask:** `{'ogretici': 0.25, 'eglendirici': 0.23076923076923078, 'haber': 0.375, 'sosyal': 0.7333333333333333}`

## Interpretation guardrails

- Compare the partially fine-tuned encoder against the frozen-encoder multitask control; improvement must be visible on the untouched hard-style development set, not only on the internal validation split.
- The 48-case hard set has already been used for architecture decisions in this development cycle, so it cannot later be relabeled as an untouched final test set.
- A final competition claim requires a new independently double-annotated holdout collected after model selection is frozen.
