# E5-base hard-style error analysis

> Development-only diagnostic. The 48 hard cases are already architecture-development data, not a final holdout.

Accuracy: **0.688**

## Confusion matrix

| Gold \ Pred | Öğretici | Eğlendirici | Haber | Sosyal |
|---|---:|---:|---:|---:|
| ogretici | 4 | 1 | 1 | 6 |
| eglendirici | 1 | 10 | 0 | 2 |
| haber | 1 | 0 | 7 | 0 |
| sosyal | 1 | 2 | 0 | 12 |

## Misclassified teaching-intent cases

- `goldcand_002` → predicted **haber** (margin 0.067); nearest train `balanced_102` / haber / cosine 0.869. Text: Bugün kayıt için üç farklı sayfa gezdim; sonunda resmi duyurudaki iki satır bütün karmaşayı çözdü.
- `goldcand_015` → predicted **eglendirici** (margin 0.035); nearest train `balanced_115` / sosyal / cosine 0.888. Text: Uçuş öncesi checklist sıkıcı geliyordu, bugün bir gevşek bağlantıyı yakaladı. fikrimi geri alıyorum.
- `goldcand_019` → predicted **sosyal** (margin 0.030); nearest train `balanced_133` / sosyal / cosine 0.882. Text: Skor güzel, oyun için aynı şeyi söyleyemeyeceğim. sonuçla performansı aynı şey saymak bana garip geliyor.
- `goldcand_023` → predicted **sosyal** (margin 0.154); nearest train `balanced_118` / sosyal / cosine 0.882. Text: Açık hava konseri güzel de eve dönüş planını konserden önce yapmak gerekiyormuş, bunu biraz geç öğrendik 😅
- `goldcand_026` → predicted **sosyal** (margin 0.371); nearest train `balanced_116` / sosyal / cosine 0.894. Text: Bu ay harcamaları yazınca küçük küçük aldıklarımın toplamı moral bozdu. büyük alışveriş değil, görünmeyenler yoruyor.
- `goldcand_027` → predicted **sosyal** (margin 0.122); nearest train `balanced_132` / sosyal / cosine 0.881. Text: Market fiyatlarını geçen ayla kıyaslamak için fiş saklamaya başladım. beklemediğim kadar faydalı oldu.
- `goldcand_030` → predicted **sosyal** (margin 0.160); nearest train `balanced_115` / sosyal / cosine 0.892. Text: Abonelikleri tek tek görünce ucuz, topluca görünce başka bir hikâye. iki tanesini sonunda kapattım.
- `goldcand_034` → predicted **sosyal** (margin 0.025); nearest train `balanced_115` / sosyal / cosine 0.879. Text: Oyunun grafikleri normal ama ses tasarımı kulaklıkla bambaşka hissettiriyor. fragmanda hiç dikkat etmemiştim.

## Challenge buckets

- `attitude_change`: n=3, accuracy=0.667
- `budget`: n=6, accuracy=0.333
- `culture`: n=5, accuracy=0.600
- `daily`: n=3, accuracy=0.667
- `gaming`: n=6, accuracy=0.667
- `humor`: n=12, accuracy=0.750
- `irony`: n=6, accuracy=0.667
- `news`: n=8, accuracy=0.875
- `reflection`: n=5, accuracy=0.600
- `social`: n=4, accuracy=1.000
- `sports`: n=3, accuracy=0.333
