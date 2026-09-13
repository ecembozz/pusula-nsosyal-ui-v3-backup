# Semantic V2 — labeling pilot results (2026-09-13)

> Status: **development pilot only**. The 48-case set currently has a single draft annotator and is **not final gold**. These numbers are for model/architecture selection, not for the final competition claim.

## Evaluation set

- 48 hand-written hard cases
- dominant intent distribution: 12 `ogretici`, 13 `eglendirici`, 8 `haber`, 15 `sosyal`
- 4 independent intent scores in `[0,1]`; dimensions do not need to sum to 1
- final gold still requires a second blind human annotation + agreement/adjudication + a separate holdout

## Pilot A — pinned V1 heuristic

Model: `heuristic-v1-pinned`

| Metric | Result |
|---|---:|
| Dominant intent accuracy | 0.2500 |
| Macro-F1 | 0.1465 |
| 4D intent MAE | 0.3010 |
| Mean cosine similarity | 0.7137 |
| Clickbait MAE | 0.0217 |

Prediction distribution: 45 `ogretici`, 2 `haber`, 1 `sosyal`, 0 `eglendirici`.

Interpretation: the V1 keyword heuristic collapses strongly toward `ogretici` on realistic/mixed Turkish text. This supports the report's earlier warning that V1's high synthetic-set score was inflated by generator/labeler coupling.

## Pilot B — multilingual MiniLM zero-shot NLI

Model: `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli`

Pinned model revision observed during CI: `0a71e92a985b6e1ad1828cf67ce9c459639c1dca`

Initial generic hypothesis template: `Bu gönderi {} içeriyor.`

| Metric | Result |
|---|---:|
| Dominant intent accuracy | 0.2500 |
| Macro-F1 | 0.1000 |
| 4D intent MAE | 0.3456 |
| Mean cosine similarity | 0.6468 |
| Clickbait MAE | 0.5842 |

Prediction distribution: 48 `ogretici`.

Interpretation: this first zero-shot formulation is **rejected**. A semantic/NLI model by itself is not sufficient; the hypothesis semantics matter, and this generic formulation over-entails the broad `ogretici` label. It is worse than the heuristic on several metrics.

## Next controlled experiment

To avoid prompt-overfitting, the next hypotheses are derived from `data/gold_eval/ANNOTATION_GUIDE.md`, not from individual test cases. We will compare the same task-aligned hypotheses with:

1. the same compact MiniLM model, and
2. `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` as a stronger but heavier NLI candidate.

The 48-case set is now treated as a **development/model-selection set**. Final reported performance must be measured on a separate, independently annotated holdout that was not used to choose the model or hypotheses.
