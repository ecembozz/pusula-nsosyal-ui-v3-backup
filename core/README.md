# PUSULA Core — Semantic V2

Yeni araştırma/ürün mantığı bu klasörde geliştirilir. `research/upstream_snapshot/` altındaki pinned upstream kopyalar değiştirilmez.

Planlanan modüller:

- `labeling.py`: ortak etiketleme arayüzü, 4D niyet vektörü ve confidence
- `heuristic_labeler.py`: mevcut sözlük yaklaşımının temiz fallback sürümü
- `semantic_labeler.py`: Türkçe destekli semantik model/LLM adapter'ı
- `hybrid_labeler.py`: confidence-gated semantic + fallback
- `clickbait.py`: kalite sinyali, niyet vektöründen bağımsız
- `ranking.py`: PUSULA ana skor formülü
- `reranking.py`: seen filter, author diversity ve MMR
- `metrics.py`: bağımsız benchmark metrikleri

Temel ilke: model bağımlılığı ranking koduna gömülmez. Ranking yalnız önceden üretilmiş etiketleri tüketir. Böylece demo sırasında model/API erişimi kesilse bile etiketlenmiş dataset deterministik biçimde çalışabilir.
