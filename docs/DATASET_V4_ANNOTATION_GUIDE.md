# PUSULA Dataset V4 — Annotation Guide

Status: **development annotation policy, not final gold**

## Why V4 exists

Dataset V3 improved style realism but used `sosyal` too broadly. In several records,
first-person or reflective status updates were treated as strongly social simply because
they looked like social-media posts. That is not the upstream PUSULA meaning.

Upstream PUSULA separates the user goals `ogrenmek`, `eglenmek`, `haberdar_olmak`,
`sosyallesmek`, and `dolasmak`. Content still receives a four-dimensional vector:

1. `ogretici`
2. `eglendirici`
3. `haber`
4. `sosyal`

The `sosyal` axis therefore means **serving a social/interpersonal need**, not merely
"this text could appear on a social network".

## Dimension definitions

### `ogretici`

High when the content helps the reader learn, understand, solve, compare, or perform
something. Explanations, steps, useful examples, troubleshooting and practical guidance
are strong signals.

A personal experience is not automatically educational. It becomes educational when the
post turns the experience into transferable explanation or advice.

### `eglendirici`

High when amusement, humour, surprise, playful storytelling, absurdity, performance or
light entertainment is a primary function.

A personal status can be mildly entertaining without being primarily entertainment.

### `haber`

High when the content's value depends on conveying a current factual update, announcement,
result, schedule change, release, event or other time-sensitive information.

Opinion about a current event may carry a news score, but opinion alone is not news.

### `sosyal`

High when the content explicitly serves interaction, relationship or community needs:
asking other people for opinions/experience, inviting replies, coordinating a meetup or
shared activity, thanking/supporting a community, collaborating, checking in with others,
or continuing an interpersonal conversation.

**Do not assign a high social score merely because:**

- the author uses first person,
- the post describes their day or feelings,
- it is casual, slang-heavy or contains emoji,
- it is a status/caption posted on a social platform.

A plain personal update with no interpersonal function can have a low or moderate `sosyal`
score and still be useful to the `dolasmak` user goal through its mixed four-dimensional
vector.

## Neutral / mixed content

Some realistic posts do not have one clear semantic function. Examples include personal
reflection, ordinary daily-life status, low-stakes observations and mixed posts that do not
strongly teach, entertain, report news or invite interaction.

V4 keeps these records instead of forcing them into one of the four classes.

- `training_role = "neutral_mixed"`
- `auxiliary_label = null`
- the 4D vector remains valid and is used by the vector head
- the record is excluded from the auxiliary single-label classifier

Clear examples use:

- `training_role = "clear_intent"`
- `auxiliary_label = ogretici|eglendirici|haber|sosyal`

`dominant_intent` may still be stored as the argmax of the 4D vector for compatibility,
but it is a diagnostic field, not permission to train every record as a hard class.

## Score anchors

These are annotation anchors rather than mathematical requirements.

- `0.00–0.15`: little or no service to this intent
- `0.15–0.35`: weak secondary relevance
- `0.35–0.60`: meaningful secondary relevance
- `0.60–0.80`: strong relevance
- `0.80–1.00`: primary / very strong relevance

Dimensions are independent and do not need to sum to one.

## Social-axis examples

Personal reflection, no invitation:

> “Bugün ilk kez tek başıma sunum yaptım; beklediğimden sakin geçti.”

Expected `sosyal`: low/moderate, not dominant.

Interaction request:

> “İlk kez tek başıma sunum yapacağım; heyecanı azaltmak için siz ne yapıyorsunuz?”

Expected `sosyal`: high, with possible secondary `ogretici` relevance.

Community coordination:

> “Yarın kampüste proje çalışacak olan varsa öğleden sonra kütüphanede buluşalım mı?”

Expected `sosyal`: very high.

## Clickbait

`clickbait` stays independent. A post can be news, educational, entertaining or social and
also use manipulative presentation. Clickbait is not an intent dimension.

## Provenance and evaluation

V4 remains synthetic/original development data. It contains no copied private user post and
must not be reported as final human gold evidence. The final competition holdout must be
untouched and independently double-annotated after model/data decisions are frozen.
