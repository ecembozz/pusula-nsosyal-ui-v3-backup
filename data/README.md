# PUSULA Data

Bu klasör Semantic V2 veri hattının tek kaynağıdır.

## Klasörler

- `v1_synthetic/`: eski 2000 gönderilik kontrollü sentetik baseline. Sonuçların geriye dönük karşılaştırması için korunur.
- `v2_realistic/`: gerçek sosyal medya dilinin biçimsel özelliklerinden esinlenen fakat özgün ve anonim yeni Türkçe gönderiler.
- `gold_eval/`: model/prompt geliştirme sırasında kullanılmayan, insan tarafından doğrulanmış bağımsız değerlendirme seti.
- `processed/`: etiketleyici çıktıları ve runtime'a verilecek türetilmiş dosyalar. Kaynak veri değildir.

## Gizlilik ve veri ilkesi

Dataset V2 için gerçek kişilerin sosyal medya gönderileri birebir kopyalanmaz. Gerçek platformlar yalnız dil ve biçim özelliklerini anlamak için gözlemsel referans olabilir. Dataset içine kullanıcı adı, profil bağlantısı, ID, konum, telefon, e-posta, yüz/medya veya kişiyi tekrar tanımlamaya yarayabilecek özgün ayrıntı konmaz.

Amaç "anonimleştirilmiş gerçek post arşivi" oluşturmak değil, **gerçekçi fakat özgün sentetik/izinli Türkçe sosyal medya örnekleri** üretmektir.

## Canonical intent dimensions

Sıra değişmez:

```text
[ogretici, eglendirici, haber, sosyal]
```

Her değer `0.0–1.0` aralığındadır ve tek etiket zorunlu değildir.

## Dataset V2 kayıt şeması

```json
{
  "id": "v2_000001",
  "text": "...",
  "source_type": "synthetic_realistic|consented_team_written",
  "style_tags": ["short", "emoji", "informal"],
  "topic": "...",
  "created_at_bucket": "recent",
  "metadata": {
    "author_id": "synthetic_author_001",
    "language": "tr"
  }
}
```

Gerçek kişi adı kullanılmaz.

## Gold evaluation şeması

```json
{
  "id": "gold_0001",
  "text": "...",
  "labels": {
    "ogretici": 0.75,
    "eglendirici": 0.20,
    "haber": 0.10,
    "sosyal": 0.45,
    "clickbait": 0.05
  },
  "annotators": 2,
  "agreement": 0.90,
  "notes": "mixed educational/social"
}
```

Gold kayıtları üretim dataset'inin kopyası olmamalıdır.
