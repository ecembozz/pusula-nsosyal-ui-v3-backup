# V4 contrastive intent benchmark

> Development-only. Each pair keeps topic/context similar and changes the intended semantic function. Not final human gold.

| Head | Pair order | >=0.10 margin | Mean axis delta | Low false-high | High capture | High axis top-1 | 4D MAE | Cosine |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| knn_k7_all320 | 0.938 | 0.896 | 0.393 | 0.146 | 0.708 | 0.979 | 0.142 | 0.858 |
| class_prototype_clear256 | 0.896 | 0.833 | 0.306 | 0.125 | 0.708 | 1.000 | 0.201 | 0.841 |
| knn_proto_blend_0.25 | 0.958 | 0.875 | 0.371 | 0.104 | 0.729 | 0.979 | 0.156 | 0.862 |
| ridge_0.05_all320 | 0.917 | 0.896 | 0.488 | 0.104 | 0.896 | 0.979 | 0.149 | 0.816 |

Development recommendation: `knn_proto_blend_0.25`

## Per-axis ordering

### knn_k7_all320

- `eglendirici`: order 0.750, margin>=0.10 0.667, delta 0.144, low-leak 0.167
- `haber`: order 1.000, margin>=0.10 0.917, delta 0.397, low-leak 0.417
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.471, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.558, low-leak 0.000

### class_prototype_clear256

- `eglendirici`: order 0.583, margin>=0.10 0.333, delta 0.046, low-leak 0.500
- `haber`: order 1.000, margin>=0.10 1.000, delta 0.415, low-leak 0.000
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.326, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.437, low-leak 0.000

### knn_proto_blend_0.25

- `eglendirici`: order 0.833, margin>=0.10 0.583, delta 0.120, low-leak 0.167
- `haber`: order 1.000, margin>=0.10 0.917, delta 0.401, low-leak 0.250
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.435, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.528, low-leak 0.000

### ridge_0.05_all320

- `eglendirici`: order 0.667, margin>=0.10 0.583, delta 0.150, low-leak 0.417
- `haber`: order 1.000, margin>=0.10 1.000, delta 0.575, low-leak 0.000
- `ogretici`: order 1.000, margin>=0.10 1.000, delta 0.536, low-leak 0.000
- `sosyal`: order 1.000, margin>=0.10 1.000, delta 0.691, low-leak 0.000
