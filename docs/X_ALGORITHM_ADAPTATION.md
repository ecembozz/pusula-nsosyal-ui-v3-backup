# X Algorithm → PUSULA adaptation notes

Reviewed public repository: `xai-org/x-algorithm`

Reference commit observed during review: `6bb4594253cdfa9ea19983a54a401d5ce8f8275d`.

This document records **conceptual adaptations**, not a claim that PUSULA embeds or reproduces X's full ranking stack. PUSULA keeps its own user-declared-intent objective and transparent score formula.

## What we intentionally keep unique to PUSULA

PUSULA's primary score remains:

```text
(0.70 * intent_fit + 0.15 * freshness + 0.15 * engagement) * quality
```

The user declares the session intent. The system does **not** infer what the user secretly wants and optimize for that hidden objective.

## 1. Candidate/filter/ranking separation

The X repository separates candidate sourcing/filtering from scoring/reranking. Its `home-mixer/filters/` module includes dedicated filters, including previously-seen and previously-served post filters.

PUSULA adaptation:

- candidate pool
- hard filters (`seen`, invalid/low-quality where applicable)
- transparent PUSULA score
- diversity reranking
- final feed

Why: this keeps business rules out of the primary relevance formula and makes every stage inspectable in the jury view.

## 2. Previously-seen / served state

X query structures explicitly carry `seen_ids` and `served_ids`, and the repository contains `previously_seen_posts_filter` / `previously_served_posts_filter` modules.

PUSULA adaptation:

- `core.reranking.filter_seen(...)` already exists in Semantic V2.
- Runtime integration will keep a bounded per-session set of served/seen post IDs.
- This is a hard filter, not an opaque relevance penalty.

## 3. Author diversity decay

X documents an author-diversity adjustment: posts after an author's first result receive a decaying multiplier, down to a floor. Its params expose author-diversity decay/floor controls.

PUSULA adaptation:

- repeated authors are gradually deprioritized after their first selected item;
- the adjustment is a separate, explainable factor;
- parameters are **not** copied blindly from X and must be chosen using our own ranking benchmark.

The Semantic V2 core already contains author diversity decay and tests for repeated-author deprioritization.

## 4. Semantic diversity after relevance scoring

X's public README describes a post-score reranking service that uses a determinantal point process (DPP) over embeddings to trade a small amount of score for lower similarity between neighbouring results.

PUSULA adaptation:

We use a simpler Maximal Marginal Relevance (MMR) style reranker when embeddings are available:

```text
selection_score = relevance - lambda * max_similarity_to_already_selected
```

Why MMR instead of copying DPP:

- easier to explain to jury/users;
- easier to test with a small dataset;
- lower implementation complexity;
- preserves PUSULA's transparent-design goal.

No claim is made that MMR is the same algorithm as X's DPP reranker; it is an adaptation of the **principle of a separate embedding-based diversity stage**.

## 5. New-author exploration (experimental only)

X documents a new-author boost for authors below an impression threshold.

PUSULA status:

- not enabled by default;
- may be benchmarked as a small exploration bonus;
- must not override strong intent mismatch;
- will be omitted if it does not improve diversity without harming intent alignment.

## What we deliberately do NOT copy

- Phoenix/X's full prediction model
- X's production-scale feature stack
- platform-specific social graph assumptions
- exact weights/thresholds
- engagement-maximization as PUSULA's main objective
- proprietary-scale candidate infrastructure

## Attribution / licensing

If source code is ever copied rather than independently reimplemented, its original license and attribution requirements must be preserved. Current Semantic V2 ranking/reranking functions are independent PUSULA implementations based on public architectural ideas.

## Jury-safe wording

Recommended wording:

> “PUSULA'nın niyet-odaklı skorunu koruduk. X'in açık kaynak akış mimarisindeki previously-seen filtering, author diversity ve post-score semantic diversity gibi tasarım ilkelerini inceleyip, daha sade ve açıklanabilir biçimde kendi sistemimize uyarladık. X'in modelini veya sıralama ağırlıklarını kopyalamadık.”
