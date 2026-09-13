# Upstream provenance

PUSULA Semantic V2, takımın daha önce kullandığı araştırma çekirdeğini koruyarak geliştirilmektedir.

## Kaynak

- Repository: `asimonmsz-design/pusula`
- Pinned commit: `78cdd15dd14adbed7e722a13b99171d84956f665`
- Commit tarihi: 2026-08-19
- Upstream çekirdek: `kod/`
- Upstream sentetik veri: `kod/veri/`

Bu commit bilinçli olarak sabitlenmiştir. Upstream repository daha sonra değişse bile deneyler ve karşılaştırmalar aynı başlangıç noktasından tekrar üretilebilmelidir.

## Semantic V2 politikası

1. Upstream dosyalar `research/upstream_snapshot/` altında **değiştirilmeden** saklanır.
2. Yeni ürün/araştırma kodu `core/`, `scripts/`, `experiments/` altında geliştirilir.
3. Eski 2000 gönderilik sentetik havuz `data/v1_synthetic/` altında baseline olarak korunur.
4. Yeni gerçekçi veri `data/v2_realistic/` altında ayrı tutulur.
5. Bağımsız insan etiketli değerlendirme seti `data/gold_eval/` altında tutulur ve üretim/kalibrasyon sırasında kullanılmaz.
6. Çalışan UI ve production akışı bu geliştirme tamamlanıp doğrulanana kadar değiştirilmez.

## Lisans / katkı notu

Pinned upstream repository kökünde bu çalışma sırasında ayrı bir `LICENSE` dosyası görülmedi. Bu nedenle upstream snapshot yeniden lisanslanmış kabul edilmez. Kaynak ve katkı açıkça belirtilir; yarışma/public dağıtım öncesinde takım içi kullanım/dağıtım izni ayrıca kayıt altına alınmalıdır.
