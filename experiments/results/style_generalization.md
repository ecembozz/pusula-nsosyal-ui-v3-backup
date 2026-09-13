# Cross-style generalization pilot

> Development-only. All labels are single-annotator drafts; this is not final competition gold.

Embedding: `intfloat/multilingual-e5-small` @ `614241f622f53c4eeff9890bdc4f31cfecc418b3`
Base training examples: **96**; hard-style evaluation examples: **48**.

Scenario A = train only on 80 topic/style-balanced raw posts + 16 independent synthetic news posts, then test on all 48 hand-written hard cases.

Scenario B = the same 96 base examples plus half of the hard-style examples in each 2-fold split, evaluated out-of-fold on the other half.

## Scenario A — zero target-style supervision

| Head | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | OOD rate | Acc @ 50% conf. |
|---|---:|---:|---:|---:|---:|---:|
| ridge | 0.312 | 0.119 | 0.242 | 0.810 | 0.250 | 0.417 |
| semantic_knn | 0.458 | 0.387 | 0.211 | 0.831 | 0.250 | 0.458 |
| pca_mlp | 0.354 | 0.315 | 0.239 | 0.807 | 0.250 | 0.458 |

## Scenario B — small target-style adaptation

| Head | Dominant acc. | Macro-F1 | 4D MAE | Mean cosine | OOD rate | Acc @ 50% conf. |
|---|---:|---:|---:|---:|---:|---:|
| ridge | 0.312 | 0.119 | 0.241 | 0.818 | 0.125 | 0.417 |
| semantic_knn | 0.417 | 0.353 | 0.196 | 0.851 | 0.125 | 0.500 |
| pca_mlp | 0.438 | 0.361 | 0.213 | 0.820 | 0.125 | 0.500 |

## Reading this result

- Scenario A is the direct answer to whether a model trained on more regular social posts can transfer to slang, irony, mixed intent and other harder styles.
- Scenario B shows how much a modest amount of target-style labeling helps without fine-tuning the multilingual encoder itself.
- OOD is a nearest-embedding screening signal, not a probability of correctness.
- Final claims require independently double-annotated held-out data that was not used in this development cycle.
