# Dataset V4 + multilingual-e5-base development benchmark

> Development-only. V4 dev-64 is synthetic/original and separate from training, but it is not final human gold.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`

Clear-intent classifier: accuracy `1.000`, macro-F1 `1.000`, top-50% `1.000`.

| Vector head | Dev acc. | F1 | 4D MAE | Cosine | Unseen max share | Unseen distribution | Collapse? |
|---|---:|---:|---:|---:|---:|---|---|
| knn_k7_all320 | 0.984 | 0.984 | 0.105 | 0.956 | 0.616 | ogretici:37, eglendirici:197, haber:10, sosyal:76 | no |
| class_prototype_clear256 | 1.000 | 1.000 | 0.167 | 0.920 | 0.478 | ogretici:47, eglendirici:153, haber:2, sosyal:118 | no |
| knn_proto_blend_0.25 | 1.000 | 1.000 | 0.119 | 0.953 | 0.597 | ogretici:36, eglendirici:191, haber:8, sosyal:85 | no |
| knn_proto_blend_0.50 | 1.000 | 1.000 | 0.135 | 0.946 | 0.575 | ogretici:38, eglendirici:184, haber:6, sosyal:92 | no |
| ridge_0.05_all320 | 0.984 | 0.984 | 0.114 | 0.952 | 0.556 | ogretici:49, eglendirici:178, haber:4, sosyal:89 | no |
| ridge_0.1_all320 | 0.984 | 0.984 | 0.118 | 0.951 | 0.519 | ogretici:50, eglendirici:166, haber:3, sosyal:101 | no |
| ridge_0.5_all320 | 1.000 | 1.000 | 0.152 | 0.927 | 0.491 | ogretici:49, eglendirici:157, haber:5, sosyal:109 | no |
| ridge_1_all320 | 1.000 | 1.000 | 0.180 | 0.901 | 0.466 | ogretici:52, eglendirici:149, haber:7, sosyal:112 | no |
| ridge_5_all320 | 0.984 | 0.984 | 0.258 | 0.784 | 0.428 | ogretici:50, eglendirici:130, haber:3, sosyal:137 | no |

Development recommendation: `knn_k7_all320`

Train/dev max char-TFIDF similarity: `0.740`; pairs >=0.90: `0`.
