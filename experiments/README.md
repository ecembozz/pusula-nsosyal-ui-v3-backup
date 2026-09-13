# Semantic V2 Experiments

Amaç: yeni yaklaşımın gerçekten daha iyi olup olmadığını aynı bağımsız veri üzerinde ölçmek.

Karşılaştırılacak etiketleyiciler:
1. `heuristic`
2. `semantic`
3. `hybrid`

Aynı `data/gold_eval/` seti üzerinde raporlanacak metrikler:
- dominant intent accuracy
- 4D MAE
- macro-F1
- clickbait precision / recall / F1
- düşük güvenli örnek oranı
- latency
- varsa API/model maliyeti

Ranking benchmark'ında aynı aday havuzu ve aynı kullanıcı niyeti kullanılır. Değiştirilen mekanizma açıkça belirtilir:
- baseline PUSULA
- + seen filter
- + author diversity
- + MMR semantic diversity

Her deney sonucu tarih, kod commit SHA, dataset sürümü ve parametrelerle birlikte `experiments/results/` altında JSON + okunabilir Markdown olarak kaydedilir.

Sonuçlar iyi çıkmadığında mekanizma production'a taşınmaz. Semantic V2'nin amacı özellik sayısını artırmak değil, savunulabilir iyileştirme üretmektir.
