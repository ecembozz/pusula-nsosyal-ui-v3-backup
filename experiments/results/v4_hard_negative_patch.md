# V4 hard-negative patch benchmark

> Development-only. Hard negatives were added after inspecting V4 contrastive development errors; these are tuning results, not final evaluation.

| Method | Pair order | >=0.10 | Mean delta | Low false-high | High capture | 4D MAE | Cosine | Unseen max share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base_knn_k7_320 | 0.938 | 0.896 | 0.393 | 0.146 | 0.708 | 0.142 | 0.858 | 0.616 |
| base_knn_proto_blend_0.25 | 0.958 | 0.875 | 0.371 | 0.104 | 0.729 | 0.156 | 0.862 | 0.597 |
| patched_knn_k7_352 | 1.000 | 0.979 | 0.445 | 0.021 | 0.625 | 0.106 | 0.888 | 0.616 |
| patched_knn_proto_blend_0.25 | 1.000 | 0.979 | 0.410 | 0.021 | 0.646 | 0.128 | 0.884 | 0.591 |

Development recommendation: `patched_knn_k7_352`

## Per-axis patched vs base

### base_knn_k7_320
- `eglendirici`: order 0.750, margin>=0.10 0.667, delta 0.144, low-leak 0.167
- `haber`: order 1.000, margin>=0.10 0.917, delta 0.397, low-leak 0.417
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.471, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.558, low-leak 0.000

### base_knn_proto_blend_0.25
- `eglendirici`: order 0.833, margin>=0.10 0.583, delta 0.120, low-leak 0.167
- `haber`: order 1.000, margin>=0.10 0.917, delta 0.401, low-leak 0.250
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.435, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.528, low-leak 0.000

### patched_knn_k7_352
- `eglendirici`: order 1.000, margin>=0.10 0.917, delta 0.256, low-leak 0.000
- `haber`: order 1.000, margin>=0.10 1.000, delta 0.443, low-leak 0.083
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.550, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.532, low-leak 0.000

### patched_knn_proto_blend_0.25
- `eglendirici`: order 1.000, margin>=0.10 0.917, delta 0.204, low-leak 0.000
- `haber`: order 1.000, margin>=0.10 1.000, delta 0.436, low-leak 0.083
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.494, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.508, low-leak 0.000
