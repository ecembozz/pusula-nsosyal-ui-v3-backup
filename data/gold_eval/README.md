# Gold Evaluation Set

Bu klasör Semantic V2'nin bağımsız değerlendirme setidir.

Hedef boyut: 200–300 Türkçe gönderi.

Kurallar:
- model/prompt geliştirme sırasında örnekler kullanılmaz
- mümkün olduğunda her kayıt en az 2 insan tarafından etiketlenir
- tek sınıf yerine 4D niyet vektörü + clickbait puanı verilir
- anlaşmazlıklar not edilir; zor/ambiguous örnekler silinmez
- gerçek kişi kimliği veya birebir gerçek sosyal medya postu tutulmaz

Ölçülecek temel metrikler:
- dominant intent accuracy
- 4D mean absolute error (MAE)
- per-dimension / macro F1 için threshold edilmiş görünüm
- clickbait precision, recall, F1
- confidence calibration

Bu setin amacı yüksek sayı üretmek değil, sentetik baseline üzerindeki iyimser ölçümü kırmak ve gerçekçi genelleme davranışını görmek.
