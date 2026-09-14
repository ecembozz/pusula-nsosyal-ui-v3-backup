# Clickbait frozen-rule stress test V4

> Development stress set authored after the presentation rule was frozen. Still not human gold and not a final competition claim.

| Method | Accuracy | Precision | Recall | F1 | MAE | Pos mean | Neg mean | Separation | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| semantic_knn_candidate_v3 | 0.562 | 1.000 | 0.125 | 0.222 | 0.339 | 0.222 | 0.086 | 0.136 | 0 | 14 |
| upstream_heuristic_v1 | 0.562 | 0.667 | 0.250 | 0.364 | 0.452 | 0.231 | 0.312 | -0.081 | 2 | 12 |
| frozen_presentation_rules_v1 | 0.344 | 0.000 | 0.000 | 0.000 | 0.525 | 0.098 | 0.388 | -0.290 | 5 | 16 |

Stress-set recommendation: `upstream_heuristic_v1`

## Frozen-rule failures

- `cbs_p01` [positive_unseen_curiosity] gold=1 score=0.000: Bu ayarı ben de gereksiz sanıyordum; sonucu görünce fikrim tamamen değişti. Sonuna kadar bak.
- `cbs_p02` [positive_unseen_curiosity] gold=1 score=0.000: Bir dakikanı ayır: neden telefonun gece bu kadar pil yediğini görünce şaşırabilirsin.
- `cbs_p03` [positive_unseen_exclusivity] gold=1 score=0.000: Sana bunu kimse anlatmıyor: küçük bir alışkanlık ay sonunda beklediğinden çok daha fazla para bırakabilir.
- `cbs_p04` [positive_unseen_curiosity] gold=1 score=0.000: Ben de inanmıyordum, ta ki aynı testi üç kez yapana kadar. Sonuç düşündüğümün tam tersiydi.
- `cbs_p05` [positive_unseen_withholding] gold=1 score=0.000: Bu detayı atlayan herkes aynı hataya düşüyor. İkinci adımın neden önemli olduğunu sona gelince anlayacaksın.
- `cbs_p06` [positive_caps_curiosity] gold=1 score=0.380: NEDEN HERKES BUNU YAPMAYA BAŞLADI? Cevap sandığınız kadar basit değil 👀
- `cbs_p07` [positive_caps_hype] gold=1 score=0.450: GÖRDÜĞÜM EN ÇILGIN SONUÇ! Aynı veri, sadece bir ayarla bambaşka göründü 😱
- `cbs_p08` [positive_overpromise] gold=1 score=0.000: Bunu öğrendikten sonra eski yönteme dönmek istemeyeceksin. Küçük görünüyor ama etkisi beklediğimden büyük.
- `cbs_p09` [positive_withholding] gold=1 score=0.000: Herkes ilk seçeneğe bakıyor ama asıl mesele başka yerde. En sonda fark ettiğim detay sonucu değiştirdi.
- `cbs_p10` [positive_caps_withholding] gold=1 score=0.370: BU VİDEOYU KAPATMADAN ÖNCE SON 10 SANİYEYİ İZLE! Ne olduğunu görünce nedenini anlayacaksın.
- `cbs_p11` [positive_fear] gold=1 score=0.000: Birçok kişinin yaptığı bu hata fark edilmeden haftalarca devam ediyor. Sen de yapıyor olabilirsin.
- `cbs_p12` [positive_personal_hype] gold=1 score=0.000: Bugün denedim ve gerçekten beklemiyordum: küçücük bir değişiklik bütün çalışma akışımı tersine çevirdi.
- `cbs_p13` [positive_curiosity_gap] gold=1 score=0.000: İlk bakışta sıradan geliyor ama üçüncü örnekte ne demek istediğimi anlayacaksın.
- `cbs_p14` [positive_caps_promise] gold=1 score=0.370: BİR DAHA AYNI HATAYI YAPMAYACAKSIN! Sebebi öğrendiğimde ben de şaşırdım.
- `cbs_p15` [positive_withholding] gold=1 score=0.000: Bu sonuç neden kimsenin konuşmadığı kadar önemli? Cevap son grafikte saklı.
- `cbs_p16` [positive_direct_hook] gold=1 score=0.000: Sadece 30 saniye ver; kullandığın ayarın neden yanlış olabileceğini göstereceğim.
- `cbs_n05` [negative_quoted_clickbait] gold=0 score=0.550: ‘Kimsenin söylemediği gerçek’ gibi başlıklar güvenilirlik hissini azaltabiliyor.
- `cbs_n06` [negative_quoted_clickbait] gold=0 score=0.600: Haberde ‘İNANAMAYACAKSINIZ’ ifadesi kullanılmış; metnin geri kalanı ise sıradan bir ürün duyurusu.
- `cbs_n07` [negative_caps_warning] gold=0 score=0.520: SAKINCA: Bu yöntem küçük örneklemde test edildi; sonuçları genellemek doğru değil.
- `cbs_n10` [negative_metalinguistic] gold=0 score=0.520: Son fırsat kavramı pazarlamada yapay kıtlık oluşturmak için sık kullanılan bir yöntemdir.
- `cbs_n14` [negative_caps_explanation] gold=0 score=0.640: DİKKAT EDİLMESİ GEREKEN NOKTA: iki grup başlangıçta aynı büyüklükte değildi.
