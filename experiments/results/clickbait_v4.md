# Clickbait contrastive benchmark V4

> Development-only. The expanded presentation rules were tuned with knowledge of these development patterns; no result here is final competition evidence.

| Method | Pair order | >=0.30 margin | Low false-positive | High capture | Acc@0.50 | F1@0.50 | MAE | Mean low | Mean high |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| semantic_knn_candidate_v3 | 1.000 | 0.375 | 0.000 | 0.375 | 0.688 | 0.545 | 0.303 | 0.086 | 0.357 |
| upstream_heuristic_v1 | 0.833 | 0.833 | 0.000 | 0.833 | 0.917 | 0.909 | 0.130 | 0.000 | 0.742 |
| presentation_rules_dev_v1 | 1.000 | 1.000 | 0.000 | 0.958 | 0.979 | 0.979 | 0.066 | 0.000 | 0.847 |

Development recommendation: `presentation_rules_dev_v1`

## Family breakdown

### semantic_knn_candidate_v3

- `entertainment_parody`: order 1.000, high-capture 0.500, low-FP 0.000, delta 0.400
- `known_phrase`: order 1.000, high-capture 0.000, low-FP 0.000, delta 0.069
- `novel_curiosity`: order 1.000, high-capture 0.600, low-FP 0.000, delta 0.455
- `novel_exclusivity`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.443
- `novel_fear`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.513
- `novel_promise`: order 1.000, high-capture 0.000, low-FP 0.000, delta 0.248
- `novel_urgency`: order 1.000, high-capture 0.500, low-FP 0.000, delta 0.248
- `social_prompt`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.516
- `subtle_curiosity_gap`: order 1.000, high-capture 0.000, low-FP 0.000, delta 0.007
- `subtle_overpromise`: order 1.000, high-capture 0.000, low-FP 0.000, delta 0.004
- `subtle_withholding`: order 1.000, high-capture 0.000, low-FP 0.000, delta 0.251

### upstream_heuristic_v1

- `entertainment_parody`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.825
- `known_phrase`: order 1.000, high-capture 1.000, low-FP 0.000, delta 1.000
- `novel_curiosity`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.790
- `novel_exclusivity`: order 1.000, high-capture 1.000, low-FP 0.000, delta 1.000
- `novel_fear`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.750
- `novel_promise`: order 1.000, high-capture 1.000, low-FP 0.000, delta 1.000
- `novel_urgency`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.725
- `social_prompt`: order 1.000, high-capture 1.000, low-FP 0.000, delta 1.000
- `subtle_curiosity_gap`: order 0.000, high-capture 0.000, low-FP 0.000, delta 0.000
- `subtle_overpromise`: order 0.000, high-capture 0.000, low-FP 0.000, delta 0.000
- `subtle_withholding`: order 0.000, high-capture 0.000, low-FP 0.000, delta 0.000

### presentation_rules_dev_v1

- `entertainment_parody`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.770
- `known_phrase`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.947
- `novel_curiosity`: order 1.000, high-capture 0.800, low-FP 0.000, delta 0.864
- `novel_exclusivity`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.820
- `novel_fear`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.870
- `novel_promise`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.990
- `novel_urgency`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.935
- `social_prompt`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.940
- `subtle_curiosity_gap`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.530
- `subtle_overpromise`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.520
- `subtle_withholding`: order 1.000, high-capture 1.000, low-FP 0.000, delta 0.780
