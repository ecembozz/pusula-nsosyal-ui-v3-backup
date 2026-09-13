# Semantic V2 — labeling pilot results (2026-09-13)

> Status: **development pilot only**. The 48-case set currently has a single draft annotator and is **not final gold**. These numbers are for model/architecture selection, not for the final competition claim.

## Evaluation set

- 48 hand-written hard cases
- dominant intent distribution: 12 `ogretici`, 13 `eglendirici`, 8 `haber`, 15 `sosyal`
- 4 independent intent scores in `[0,1]`; dimensions do not need to sum to 1
- final gold still requires a second blind human annotation + agreement/adjudication + a separate holdout

## Summary

| Pilot | Dominant accuracy | Macro-F1 | 4D MAE | Mean cosine | Clickbait MAE | Decision |
|---|---:|---:|---:|---:|---:|---|
| V1 heuristic | 0.2500 | 0.1465 | 0.3010 | 0.7137 | 0.0217 | baseline/fallback only |
| MiniLM generic zero-shot | 0.2500 | 0.1000 | 0.3456 | 0.6468 | 0.5842 | rejected |
| MiniLM task-aligned NLI | 0.2917 | 0.2009 | 0.2766 | 0.7143 | 0.2848 | insufficient |
| mDeBERTa task-aligned NLI | 0.3750 | 0.3237 | 0.3543 | 0.6670 | 0.0667 | insufficient |
| Qwen2.5-0.5B-Instruct | pending | pending | pending | pending | pending | pending |

These rows are **not final competition metrics** because the labels currently come from one draft annotator and the same 48 cases are being used for model selection.

## Pilot A — pinned V1 heuristic

Model: `heuristic-v1-pinned`

Prediction distribution: 45 `ogretici`, 2 `haber`, 1 `sosyal`, 0 `eglendirici`.

Interpretation: the V1 keyword heuristic collapses strongly toward `ogretici` on realistic/mixed Turkish text. This supports the report's earlier warning that V1's high synthetic-set score was inflated by generator/labeler coupling.

## Pilot B — multilingual MiniLM generic zero-shot NLI

Model: `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli`

Pinned model revision observed during CI: `0a71e92a985b6e1ad1828cf67ce9c459639c1dca`

Initial generic hypothesis template: `Bu gönderi {} içeriyor.`

Prediction distribution: 48 `ogretici`.

Interpretation: **rejected**. A multilingual semantic/NLI model by itself is not sufficient; the hypothesis semantics matter, and this generic formulation over-entails the broad `ogretici` label.

## Pilot C — MiniLM task-aligned NLI

Model: `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli`

Hypotheses were derived from `data/gold_eval/ANNOTATION_GUIDE.md` and evaluate each PUSULA dimension as a separate premise/hypothesis NLI pair. Independent label scores use `P(entailment | contradiction, entailment)`, matching multi-label zero-shot normalization rather than a three-class softmax including neutral.

Results:

- dominant accuracy: `0.2916667`
- macro-F1: `0.2008961`
- 4D MAE: `0.2766444`
- mean cosine: `0.7143310`
- clickbait MAE: `0.2848201`

Interpretation: task-aware hypotheses remove the one-class collapse and improve vector MAE, but intent classification remains too weak for production labeling.

## Pilot D — mDeBERTa task-aligned NLI

Model: `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`

Pinned model revision observed during CI: `8adb042d524ecd5c26d3e3ba0e3fbcf7e2d0864c`

Results:

- dominant accuracy: `0.3750`
- macro-F1: `0.3237204`
- 4D MAE: `0.3543060`
- mean cosine: `0.6669827`
- clickbait MAE: `0.0667226`

Prediction distribution: 15 `eglendirici`, 14 `haber`, 19 `sosyal`, **0 `ogretici`**.

Interpretation: the larger NLI model improves dominant accuracy and news/social separation, but completely misses the dominant `ogretici` class and produces worse 4D MAE than both the heuristic and task-aligned MiniLM. It is therefore **not accepted as the standalone PUSULA semantic labeler**.

## Current model-selection conclusion

The two NLI families are useful baselines but do not solve PUSULA's multi-dimensional intent-scoring task reliably enough. The next controlled candidate is a small instruction-tuned language model used **offline only** to return the exact five-score JSON schema. The web application will never load or call this model per feed request.

If the small instruction model is also insufficient, the next step is a stronger batch instruction model/API rather than forcing a weak local model into production.

The 48-case set remains a **development/model-selection set**. Final reported performance must be measured on a separate, independently annotated holdout that was not used to choose the model, prompt, thresholds, or calibration.
