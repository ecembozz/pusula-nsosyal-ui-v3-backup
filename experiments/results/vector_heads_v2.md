# Candidate V2 vector-head development comparison

> Development-only. Hard-48 is repeatedly inspected and V2-320 has no gold labels.

Encoder: `intfloat/multilingual-e5-base` @ `d128750597153bb5987e10b1c3493a34e5a4502a`

| Head | Hard48 acc. | F1 | 4D MAE | Cosine | Unseen max-class share | Unseen distribution | Collapse? |
|---|---:|---:|---:|---:|---:|---|---|
| knn_k7 | 0.458 | 0.413 | 0.188 | 0.861 | 0.916 | ogretici:12, eglendirici:10, haber:5, sosyal:293 | YES |
| class_prototype | 0.375 | 0.263 | 0.200 | 0.882 | 1.000 | ogretici:0, eglendirici:0, haber:0, sosyal:320 | YES |
| knn_prototype_blend_0.25 | 0.458 | 0.413 | 0.186 | 0.873 | 0.950 | ogretici:10, eglendirici:4, haber:2, sosyal:304 | YES |
| knn_prototype_blend_0.50 | 0.438 | 0.380 | 0.187 | 0.882 | 0.956 | ogretici:10, eglendirici:4, haber:0, sosyal:306 | YES |
| knn_prototype_blend_0.75 | 0.417 | 0.334 | 0.192 | 0.885 | 0.981 | ogretici:5, eglendirici:1, haber:0, sosyal:314 | YES |
| ridge_0.1 | 0.542 | 0.525 | 0.180 | 0.901 | 0.831 | ogretici:20, eglendirici:34, haber:0, sosyal:266 | YES |
| ridge_1 | 0.438 | 0.351 | 0.184 | 0.902 | 0.963 | ogretici:12, eglendirici:0, haber:0, sosyal:308 | YES |
| ridge_10 | 0.312 | 0.119 | 0.233 | 0.847 | 1.000 | ogretici:0, eglendirici:0, haber:0, sosyal:320 | YES |
| ridge_100 | 0.312 | 0.119 | 0.255 | 0.814 | 1.000 | ogretici:0, eglendirici:0, haber:0, sosyal:320 | YES |

Development recommendation: `None`

Selection rejects severe one-class collapse on the unlabeled unseen corpus, then uses hard-48 vector MAE and cosine only as development criteria. This is not a final competition metric.
