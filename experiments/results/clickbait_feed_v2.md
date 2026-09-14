# Clickbait feed-distribution benchmark V2

> Development-only. This benchmark was created after Candidate V4 exposed false-positive pressure on normal-feed text. It is not final competition evidence.

## Feed-style development eval

| Method | Acc | Prec | Recall | F1 | ROC-AUC | Brier | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| e5_base128_balanced | 0.812 | 0.727 | 1.000 | 0.842 | 0.993 | 0.149 | 12 | 0 |
| e5_aug192_unweighted | 0.906 | 1.000 | 0.812 | 0.897 | 0.998 | 0.122 | 0 | 6 |
| e5_aug192_balanced | 0.969 | 0.941 | 1.000 | 0.970 | 0.999 | 0.101 | 2 | 0 |
| tfidf_aug192_unweighted | 0.938 | 1.000 | 0.875 | 0.933 | 0.986 | 0.083 | 0 | 4 |
| tfidf_aug192_balanced | 0.953 | 0.968 | 0.938 | 0.952 | 0.986 | 0.074 | 1 | 2 |
| blend_e5_tfidf_unweighted | 0.906 | 1.000 | 0.812 | 0.897 | 1.000 | 0.106 | 0 | 6 |

## Unlabeled V2-320 background sanity

| Method | Mean | Median | P90 | P95 | >=.50 | >=.65 | >=.75 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| e5_base128_balanced | 0.514 | 0.530 | 0.619 | 0.650 | 183 | 16 | 0 | 0.717 |
| e5_aug192_unweighted | 0.260 | 0.265 | 0.357 | 0.377 | 0 | 0 | 0 | 0.492 |
| e5_aug192_balanced | 0.363 | 0.372 | 0.482 | 0.503 | 21 | 0 | 0 | 0.626 |
| tfidf_aug192_unweighted | 0.216 | 0.189 | 0.374 | 0.462 | 12 | 5 | 2 | 0.821 |
| tfidf_aug192_balanced | 0.281 | 0.254 | 0.473 | 0.565 | 28 | 9 | 5 | 0.880 |
| blend_e5_tfidf_unweighted | 0.247 | 0.249 | 0.334 | 0.349 | 1 | 0 | 0 | 0.509 |

## 5-fold OOF on augmented 192-row train

| Method | Acc | Prec | Recall | F1 | ROC-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|
| e5_aug192_unweighted | 0.828 | 0.943 | 0.516 | 0.667 | 0.970 | 0.132 |
| e5_aug192_balanced | 0.917 | 0.853 | 0.906 | 0.879 | 0.971 | 0.136 |
| tfidf_aug192_unweighted | 0.818 | 0.796 | 0.609 | 0.690 | 0.920 | 0.125 |

Development recommendation: `e5_aug192_balanced`

## Recommended method: highest background scores

- `v2r_0008` score=0.626: ders seçimi için küçük bir kontrol listesi yaptım; iki maddeyi son anda fark ettim başka yaşayan var mı?
- `v2r_0108` score=0.574: maç sonrası yorumlar hakkında yorum yapmadan önce tekrarını izlemek lazım, ilk anda çok farklı görünüyor siz ne düşünüyorsunuz?
- `v2r_0104` score=0.573: son dakikadaki gol hakkında yorum yapmadan önce tekrarını izlemek lazım, ilk anda çok farklı görünüyor siz ne düşünüyorsunuz?
- `v2r_0068` score=0.547: son test videosu sonrası ekipçe 10 dakika sessizce ekrana baktık. çalışınca insan inanamıyor başka yaşayan var mı?
- `v2r_0012` score=0.541: yurt başvurusu için küçük bir kontrol listesi yaptım; iki maddeyi son anda fark ettim; sizde de böyle mi?
- `v2r_0048` score=0.526: sesli asistan güzel de gizlilik ayarlarını bulmak niye bu kadar zor 😅; sizde de böyle mi?
- `v2r_0036` score=0.526: otomatik özet aracı konusunda küçük modeller bazen beklediğimden daha mantıklı sonuç veriyor; sizde de böyle mi?
- `v2r_0051` score=0.524: açık kaynak bir model konusunda küçük modeller bazen beklediğimden daha mantıklı sonuç veriyor. 🙃
- `v2r_0180` score=0.520: ulaşım masrafı için bir haftalık deneme yaptım, beklediğimden fazla fark etti siz ne düşünüyorsunuz?
- `v2r_0128` score=0.516: VAR kararı için arkadaş grubunda skor tahmini şimdiden kavgaya döndü 😄 başka yaşayan var mı?
- `v2r_0040` score=0.514: telefonun yeni yapay zekâ özelliği güzel de gizlilik ayarlarını bulmak niye bu kadar zor 😅; sizde de böyle mi?
- `v2r_0017` score=0.513: ders seçimi tamam da şu belge listesini tek yerde toplayan biri var mı?

## Recommended method: feed-eval failures

- `cbfe_n019` gold=0 score=0.525: bu sonuç beni şaşırttı: küçük model testte büyük modelle neredeyse aynı skoru aldı.
- `cbfe_n032` gold=0 score=0.524: sizce bu tasarım daha okunaklı mı? iki seçenek arasında kaldım, özellikle mobilde emin olamadım.
