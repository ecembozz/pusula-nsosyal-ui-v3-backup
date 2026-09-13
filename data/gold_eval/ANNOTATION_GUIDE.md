# PUSULA Gold Evaluation Annotation Guide

Bu dosya PUSULA Semantic V2 için insan etiketleme kurallarını tanımlar. Amaç tek-sınıf sınıflandırması değil, her gönderinin dört bağımsız ihtiyaca ne ölçüde hizmet ettiğini 0–1 arasında puanlamaktır.

## Boyutlar

### `ogretici`
Gönderi okuyucuya açıklama, öneri, yöntem, çıkarım, pratik bilgi veya öğrenilebilir bir ders sunuyorsa yükselir.

### `eglendirici`
Mizah, ironi, oyun, hikâye, eğlence veya keyif verme değeri varsa yükselir. Sadece emoji olması tek başına yüksek puan nedeni değildir.

### `haber`
Kamusal/güncel bir olay, duyuru, sonuç, takvim değişikliği veya yeni gelişme aktarıyorsa yükselir. Kişisel durum güncellemesi haber sayılmaz.

### `sosyal`
Kişisel deneyim, duygu, sohbet daveti, ilişki/ekip bağlamı, fikir paylaşımı veya topluluk etkileşimi baskınsa yükselir.

Boyutların toplamı 1 olmak zorunda değildir. Bir gönderi aynı anda hem öğretici hem sosyal olabilir.

## Puanlama ölçeği

- `0.00`: bu ihtiyaca hizmet etmiyor
- `0.25`: zayıf/ikincil sinyal
- `0.50`: belirgin fakat baskın değil
- `0.75`: güçlü
- `1.00`: içeriğin temel işlevlerinden biri

Ara değerler kullanılabilir.

## Clickbait

`clickbait` ayrı değerlendirilir. Merak boşluğu, yanıltıcı abartı, bilgiyi kasıtlı saklama veya içeriğin vaat ettiğinden fazlasını ima etme yükseltir. Mizah, ünlem veya güçlü görüş tek başına clickbait değildir.

## Dominant intent

Dört boyuttaki en yüksek değer `dominant_intent` olur. Çok yakın iki puan varsa annotator confidence düşürülmelidir; puanlar yapay biçimde ayrıştırılmamalıdır.

## Annotation confidence

Bu alan model güveni değildir; insan annotatorün kendi etiketinden ne kadar emin olduğunu gösterir.

- `0.90–1.00`: oldukça açık
- `0.75–0.89`: makul fakat ikincil yorum mümkün
- `<0.75`: tartışmalı; adjudication önceliği

## Gold statüsü

`draft_single_annotator` kayıtlar final gold değildir. Final `gold_v1` için:

1. Aynı örnek en az iki annotator tarafından birbirinin cevabını görmeden etiketlenir.
2. Boyut başına mutlak farklar ve dominant intent uyuşması hesaplanır.
3. Büyük anlaşmazlıklar adjudication ile çözülür.
4. Final set ayrıca model/prompt seçiminde kullanılmayacak bir holdout bölümüne ayrılır.

## Haber için önemli ayrım

- “YKS sonucum geldi, çok sevindim.” → esas olarak sosyal.
- “YKS sonuç ekranı erişime açıldı.” → haber değeri yüksek.
- “Sonuç ekranı açıldı, tercih kılavuzunda da değişiklik var.” → haber + öğretici olabilir.

## Etiketleyiciye verilmemesi gereken bilgiler

Annotator yalnız `text` alanını görmelidir. `challenge`, topic family veya başka üretim metadata'sı etiketlemeyi yönlendirmemelidir.
