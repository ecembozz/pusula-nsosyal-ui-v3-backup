# PUSULA Semantic Candidate V1

Status: **development candidate, not final competition model**

## Decision

The old 2,000-post templated pool is not used as training data. It remains a baseline/demo fixture only.

Candidate V1 uses a frozen `intfloat/multilingual-e5-base` encoder with two different lightweight heads:

1. **Dominant intent + confidence**
   - training source: Dataset V3 tranche 1 only (`128` rows; `32` per dominant intent)
   - head: class-balanced logistic regression
   - reason: this clean tranche gave the strongest hard-48 dominant-intent development result (`0.708` accuracy, `0.707` macro-F1; `0.833` accuracy at the most-confident 50% coverage).

2. **4D intent vector + clickbait**
   - training source: all Dataset V3 rows (`256`; `64` per dominant intent)
   - head: semantic k-NN (`k=7`, cosine, distance weighted)
   - optional blend: k-NN vector with the dominant classifier probability vector for diagnostics only
   - reason: the deliberately ambiguous boundary cases in tranche 2 improve vector fidelity and clickbait MAE, but add noise when every row is forced into one dominant class.

The hard-48 set has been repeatedly inspected during development and **must not be reported as final test performance**.

## Current development evidence

Frozen encoder: `intfloat/multilingual-e5-base` revision `d128750597153bb5987e10b1c3493a34e5a4502a`.

- V3-128 dominant classifier: accuracy `0.708`, macro-F1 `0.707`, top-50%-confidence accuracy `0.833`.
- V3-256 standard dominant classifier: accuracy `0.625`, macro-F1 `0.637`.
- V3-256 margin-filtered dominant classifier (label margin >= 0.25 or 0.35): accuracy `0.688`; still below V3-128.
- V3-256 hybrid vector: 4D MAE `0.175`, cosine `0.885`; top-50%-confidence dominant accuracy `0.875`.
- Dataset V3-256 audit: `64/64/64/64` balance, `16` clickbait-positive rows, `0` pairs at character TF-IDF cosine >= `0.90`.

## Runtime policy

The model is **not** intended to run inside a Vercel feed request.

1. New/candidate posts are processed offline in batch.
2. The encoder produces embeddings.
3. Candidate V1 produces the four intent scores, clickbait score, dominant intent and confidence diagnostics.
4. Results are schema-validated and cached with a text fingerprint.
5. The lightweight Vercel API consumes only the cached labels during ranking.
6. Low-confidence / out-of-distribution cases are reserved for a stronger offline LLM or human review fallback; they are never silently forced into a confident label.

## What is still required before a competition claim

- Create an untouched holdout not used in prompt/model/data decisions.
- Have at least two independent human annotators label that holdout using the same annotation guide.
- Adjudicate disagreements and report inter-annotator agreement.
- Evaluate dominant intent, macro-F1, 4D MAE, cosine similarity and clickbait metrics on that final holdout.
- Separately evaluate feed-ranking quality; PUSULA ultimately ranks using the 4D vector rather than only a single dominant label.
