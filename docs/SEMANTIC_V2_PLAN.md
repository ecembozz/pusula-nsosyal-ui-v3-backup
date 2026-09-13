# PUSULA Semantic V2 — Uygulama Planı

## Amaç

PUSULA'nın ürün iddiasını değiştirmeden içerik anlayışını gerçekçi hâle getirmek:

> Kullanıcının niyeti tahmin edilmez; kullanıcı tarafından beyan edilir. İçerik ise semantik olarak anlaşılır ve bu niyete ne kadar hizmet ettiği ölçülür.

## Korunan temel

PUSULA ana skoru korunur:

```text
base = 0.70 * intent_fit + 0.15 * freshness + 0.15 * engagement
score = base * quality
quality = 1 - clickbait
```

Bu formül projenin kimliğidir. Semantic V2'nin amacı bu formülü karmaşıklaştırmak değil, giriş sinyallerini daha gerçek ve güvenilir hâle getirmektir.

## Fazlar

### F0 — Güvenli çalışma hattı

- `main`: çalışan production
- `stable-ui-2026-09-13`: donmuş geri dönüş noktası
- `semantic-v2`: bütün yeni geliştirme

Production, Semantic V2 doğrulanana kadar değiştirilmez.

### F1 — Repo ve provenance

- upstream çekirdeği pinned commit ile snapshot olarak sakla
- v1 sentetik baseline'ı taşı
- UI/runtime ile araştırma kodunu ayır
- dataset/model dokümantasyonu oluştur

### F2 — Dataset V2

Hedef:
- 800–1500 özgün, anonim, gerçekçi Türkçe sosyal medya gönderisi
- farklı uzunluk, emoji, hashtag, yazım hatası, argo, ironi, retorik soru
- tek ve çoklu niyet örnekleri
- gerçek haber + yorum, eğitici mizah, clickbait ama bilgi taşıyan örnekler
- kişisel veri veya gerçek kullanıcı postunun birebir kopyası yok

Ayrı `gold_eval` seti:
- 200–300 elle etiketlenmiş örnek
- üretim/prompt kalibrasyonu sırasında görülmez

### F3 — Etiketleme V2

Ortak çıktı şeması:

```json
{
  "intent": {
    "ogretici": 0.0,
    "eglendirici": 0.0,
    "haber": 0.0,
    "sosyal": 0.0
  },
  "clickbait": 0.0,
  "confidence": 0.0,
  "method": "heuristic|semantic|hybrid"
}
```

Katmanlar:
1. `heuristic`: mevcut sözlük/yapısal sinyaller — offline fallback
2. `semantic`: Türkçe destekli model/LLM — içerik başına bir kez
3. `hybrid`: semantic sonuç + güven eşiği + fallback

Canlı feed sırasında her gönderi için LLM çağrısı yapılmaz. Etiket sonucu önceden hesaplanır ve cache/veri kümesine yazılır.

### F4 — Benchmark

Aynı `gold_eval` üzerinde:
- dominant intent accuracy
- intent MAE
- macro-F1
- confidence calibration
- clickbait precision / recall / F1
- latency
- gerekiyorsa model/API maliyeti

Heuristic, semantic ve hybrid aynı tabloda karşılaştırılır.

### F5 — Ranking V2

PUSULA skorundan sonra sade reranking:
- previously-seen filter
- author diversity decay
- semantic diversity (MMR)
- opsiyonel controlled exploration / new-author boost

MMR örneği:

```text
rerank_score = alpha * pusula_score
             - (1-alpha) * max_similarity_to_selected
```

X'in açık kaynak feed mimarisinden fikir alınır; Phoenix gibi ağır modeli kopyalamak hedef değildir.

### F6 — Jüri Teknik Merkezi

Gönderi bazında göster:
- labeling method
- confidence
- 4D intent vector
- user intent
- cosine similarity
- freshness / engagement / quality
- base/final score
- author diversity adjustment
- semantic diversity adjustment
- final rank

Benchmark ekranı:
- Heuristic vs Semantic vs Hybrid
- Dataset V1 vs Gold Eval

### F7 — Release Candidate

Semantic V2 yalnız şu kontrollerden sonra `main` adayı olur:
- UI smoke test
- API smoke test
- deterministic dataset build
- benchmark raporu
- no-secret check
- preview demo doğrulaması
- rollback branch doğrulaması

## Şimdilik yapılmayacaklar

- ödül modeli / RL ile ağırlıkları öğrenme
- gerçek kullanıcı kişisel verisi toplama
- izinsiz NSosyal/X scraping
- Phoenix'in tamamını projeye alma
- production'da canlı LLM bağımlılığı
