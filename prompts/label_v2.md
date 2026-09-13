# PUSULA Semantic Label Prompt — v2

Bu prompt provider/model bağımsız batch etiketleme sözleşmesidir. Amaç sosyal medya metninin **hangi kullanıcı ihtiyacına ne kadar hizmet ettiğini** puanlamaktır; konu sınıflandırması yapmak değildir.

## Çıktı

Yalnız geçerli JSON döndür:

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
  "signals": ["kısa kanıt etiketi"]
}
```

## Boyutlar

- `ogretici`: açıklıyor, öğretiyor, yöntem/örnek/veri sağlıyor, kullanıcıya bilgi veya beceri kazandırıyor.
- `eglendirici`: mizah, şaşırtma, estetik/duygusal eğlence, oyun veya keyif için tüketiliyor.
- `haber`: yeni/güncel olay, duyuru, gelişme, resmî bilgi veya kamusal gündem hakkında haberdar ediyor.
- `sosyal`: konuşma başlatıyor, ilişki/aidiyet kuruyor, soru soruyor, görüş/deneyim istiyor veya kişisel paylaşım üzerinden etkileşim davet ediyor.

Her boyut bağımsız olarak `0–1` arasıdır. Toplamlarının 1 olması gerekmez. Bir gönderi aynı anda birden fazla ihtiyaca güçlü hizmet edebilir.

## Clickbait

`clickbait` niyet değildir. İçeriğin sunum biçiminin merak/öfke/korku yaratarak vaat ettiği değerle gerçek bilgi arasında ne kadar kopukluk oluşturduğunu `0–1` arasında puanla.

Başlığın dikkat çekici olması tek başına clickbait değildir. Gerçek ve açık bir duyuru "SON DAKİKA" içerebilir. Asılsız kesinlik, gizli bilgi vaadi, aşırı ünlem, "kimsenin söylemediği", sonucu saklama ve içerikten büyük vaat clickbait sinyalidir.

## Confidence

`confidence`, dört niyet puanı ve clickbait kararının metinden ne kadar güvenle çıkarılabildiğini gösterir.

- `0.85–1.00`: açık sinyaller
- `0.65–0.84`: makul ama karma içerik
- `0.40–0.64`: bağlam eksik / ironi / belirsizlik
- `<0.40`: güvenilir semantik karar için yetersiz bağlam

## Kurallar

1. Kullanıcı kimliği, takipçi sayısı veya siyasi/kişisel özellikler hakkında çıkarım yapma.
2. Yalnız metinde görülen işleve göre puanla.
3. İroniyi mümkünse anlamlandır; emin değilsen confidence düşür.
4. "Haber" ile "öğretici" birlikte yüksek olabilir: güncel veriyi açıklayan analiz gibi.
5. "Sosyal" soru işareti var diye otomatik yüksek verilmez; gerçek etkileşim daveti aranır.
6. Kısa ve bozuk yazılmış metinleri cezalandırma; içerik işlevini değerlendir.
7. `signals` en fazla 3 kısa gözlem içersin; gizli muhakeme/uzun açıklama üretme.

## Girdi biçimi

```text
Gönderi:
{TEXT}
```

Prompt version: `label-v2.0`
