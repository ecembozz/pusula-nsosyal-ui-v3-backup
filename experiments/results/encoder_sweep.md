# Multilingual encoder capacity sweep

> Development-only. The same 136 assistant-authored balanced training examples and the same 48 single-annotator hard-style development examples are used for every encoder.

| Encoder | Hidden | Logistic acc. | Logistic macro-F1 | Top-50% acc. | Best vector MAE | Best vector cosine |
|---|---:|---:|---:|---:|---:|---:|
| intfloat/multilingual-e5-small | 384 | 0.521 | 0.543 | 0.625 | 0.196 | 0.880 |
| intfloat/multilingual-e5-base | 768 | 0.688 | 0.688 | 0.792 | 0.177 | 0.900 |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 384 | 0.521 | 0.535 | 0.625 | 0.188 | 0.874 |

## Guardrail

This is an architecture-selection benchmark on an already-used development set. It is useful for choosing an encoder, not for a final competition claim.
