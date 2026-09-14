# PUSULA Dataset V3 — Realistic Development Training Corpus

## Purpose

Dataset V3 is the task-specific training corpus for the semantic intent labeler. It replaces the old 2,000-post pool as the primary **model-development training source** because the legacy pool is highly templated and produces unrealistically optimistic in-pool scores.

The legacy 2,000-post pool remains in the repository only as a historical baseline and ranking-demo fixture. It must not be used to claim real-world semantic generalization.

## Label semantics

Intent order is fixed everywhere:

1. `ogretici`
2. `eglendirici`
3. `haber`
4. `sosyal`

`gercek_niyet` is a four-dimensional multi-intent vector in `[0, 1]`. Dimensions are independent and do **not** need to sum to 1.

`dominant_intent` is the strongest intended function of the text. It is useful for auxiliary classification and diagnostics, but PUSULA ranking should continue to use the full 4D vector.

`clickbait` is independent of the four intent dimensions.

## Canonical record

```json
{
  "id": "v3_0001",
  "metin": "...",
  "gercek_niyet": [0.88, 0.08, 0.04, 0.34],
  "dominant_intent": "ogretici",
  "clickbait": 0.02,
  "style_bucket": "casual",
  "content_type": "status",
  "topic_family": "technology",
  "difficulty": "medium",
  "label_source": "assistant_authored_development",
  "provenance": "synthetic_original_not_copied_user_post"
}
```

## What is deliberately NOT included

`etkilesim_puani`, `pismanlik_olasiligi`, `tazelik`, likes, reposts and other feed/ranking metadata are not intrinsic semantic labels. They are therefore not fabricated inside the semantic training corpus. A separate feed-fixture export may simulate those values later if the UI/ranking demo requires them.

## Coverage requirements

Each development tranche should be balanced by dominant intent and deliberately cross topic/style boundaries. Topic balance is not a substitute for intent balance.

Required style coverage includes at least:

- plain edited Turkish
- casual conversational Turkish
- slang / internet language
- spelling and punctuation noise
- emoji
- questions
- short fragments
- longer explanatory text
- irony / sarcasm
- mixed-intent text
- Turkish-English code switching
- headline + summary
- replies/comments
- captions
- thread hooks

Training examples may look like posts, replies, captions, questions, notes or short content summaries. The task is semantic intent understanding, not imitation of one platform UI format.

## Quality rules

- No real private user post is copied verbatim.
- No handle, phone, email, exact personal identifier or private personal detail is required.
- Exact duplicate text is forbidden.
- Near-duplicates should be audited before promotion into the canonical training file.
- Clickbait positives must occur under more than one dominant intent.
- Mixed-intent examples must remain genuinely multi-dimensional rather than converting the task into four mutually exclusive classes.
- `label_source=assistant_authored_development` means the record is valid for development/training but is **not final gold evidence**.

## Evaluation policy

The repeatedly inspected `hard-48` set is a development generalization set only. Final competition metrics must come from a new, untouched, independently double-annotated holdout set. Model selection, threshold tuning and prompt tuning may not use that final holdout.
