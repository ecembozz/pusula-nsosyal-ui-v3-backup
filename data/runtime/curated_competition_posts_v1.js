const CATEGORY_LABELS={
  egitim_yks:'Eğitim',teknoloji_ai:'Yapay zekâ & teknoloji',teknofest_maker:'Teknoloji & maker',
  spor_futbol:'Spor',kultur_sanat:'Kültür & sanat',ekonomi_butce:'Ekonomi & bütçe',
  oyun_espor:'Oyun & e-spor',kampus_is:'Kampüs & iş',gundelik_yasam:'Gündelik yaşam',
  sosyal_sohbet:'Sosyal'
};

const AUTHORS=[
  ['Ada K.','curated_user_01'],['Baran T.','curated_user_02'],['Ceren A.','curated_user_03'],
  ['Deniz E.','curated_user_04'],['Efe M.','curated_user_05'],['Gizem S.','curated_user_06'],
  ['İlayda N.','curated_user_07'],['Kaan D.','curated_user_08'],['Lara Y.','curated_user_09'],
  ['Mertcan O.','curated_user_10'],['Nehir B.','curated_user_11'],['Oğuz P.','curated_user_12'],
  ['Pelin Ç.','curated_user_13'],['Rana G.','curated_user_14'],['Selim V.','curated_user_15'],
  ['Sude İ.','curated_user_16'],['Tolga R.','curated_user_17'],['Yağmur H.','curated_user_18'],
  ['Zeynep U.','curated_user_19'],['Arda L.','curated_user_20']
];

const rows=[
  // Teknoloji & maker — yarışma hazırlığı, prototip ve saha gerçekliği
  ['teknofest_maker','TEKNOFEST uçuş testinden önce kontrol listesini iki kişi ayrı ayrı okuyunca gevşek kalan güç bağlantısını fark ettik. Beş dakikalık kontrol, bütün günü kurtardı.',[.82,.08,.30,.22],.01,.55,.98],
  ['teknofest_maker','TEKNOFEST sunumunda yalnızca çalışan tarafı değil, üç başarısız denemeyi de göstereceğiz. Çözümün neden böyle olduğunu en iyi onlar anlatıyor.',[.78,.10,.42,.28],.02,.61,.96],
  ['teknofest_maker','Prototip masasında bugün lehim kokusu, soğumuş kahve ve sonunda düzgün gelen sensör verisi vardı. Küçük zafer ama ekipçe iyi geldi. 🔧',[.38,.62,.12,.58],.00,.72,.94],
  ['teknofest_maker','TEKNOFEST mentörünün “özelliği anlatmayın, hangi problemi çözdüğünüzü gösterin” cümlesi sunumun yarısını değiştirdi.',[.72,.06,.24,.34],.00,.58,.91],
  ['teknofest_maker','Demo sırasında internet kesilirse diye çevrimdışı senaryoyu da hazırladık. Yarışma günü sürpriz azaltmanın en iyi yolu sanırım biraz paranoyak olmak.',[.67,.32,.18,.26],.01,.64,.89],

  // Yapay zekâ & teknoloji — açıklanabilirlik ve PUSULA bağlamı
  ['teknoloji_ai','Bir öneri sisteminin “bunu neden gördüm?” sorusuna cevap verememesi artık eksik bir özellik gibi geliyor. Skor kadar açıklaması da ürünün parçası olmalı.',[.90,.04,.34,.12],.01,.47,.97],
  ['teknoloji_ai','PUSULA testinde aynı gönderi, öğrenmek isteyen kullanıcıda yukarı çıkarken eğlenmek isteyen kullanıcıda geriye düştü. Asıl görmek istediğimiz davranış tam olarak buydu.',[.78,.10,.40,.20],.01,.66,.95],
  ['teknoloji_ai','Küçük dil modeli telefonda biraz daha az şey biliyor ama gecikme ve gizlilik tarafında ciddi avantaj sağlıyor. Her projede en büyük modeli seçmek gerekmiyor.',[.86,.08,.36,.10],.02,.51,.90],
  ['teknoloji_ai','Yarışma demosunda içeriği bir kez analiz edip sonuçları saklamak, her akış isteğinde modeli yeniden çağırmaktan çok daha mantıklı çıktı. Maliyet düştü, sıralama da hızlandı.',[.94,.03,.28,.08],.00,.54,.87],
  ['teknoloji_ai','Modelin güven skorunu ekrana koymak tek başına açıklanabilirlik değil. Hangi sinyallerin kararı etkilediğini de kullanıcı dilinde anlatmak gerekiyor.',[.92,.03,.32,.10],.01,.45,.84],

  // Eğitim
  ['egitim_yks','Bir konuyu gerçekten öğrenip öğrenmediğimi, onu ekip arkadaşına sade biçimde anlatmaya çalışınca anlıyorum. Slayt hazırlamak bu yüzden iyi bir testmiş.',[.88,.08,.12,.34],.00,.49,.93],
  ['egitim_yks','TEKNOFEST raporunu yazarken kaynak göstermenin yalnızca akademik bir kural olmadığını fark ettim; jüri aynı karara nasıl ulaştığını görebiliyor.',[.84,.05,.30,.18],.01,.52,.90],
  ['egitim_yks','Bugün kosinüs benzerliğini formülden değil, iki niyet vektörünü çizerek çalıştım. Görselleştirince “yön benzerliği” fikri yerine oturdu.',[.96,.04,.10,.08],.00,.43,.88],
  ['egitim_yks','Final haftasıyla proje teslimi aynı güne yaklaşınca görevleri 25 dakikalık parçalara böldüm. Mucize değil ama nereden başlayacağımı düşünmeyi bıraktım.',[.55,.18,.08,.20],.00,.59,.83],
  ['egitim_yks','Bir teknik sunumda her ayrıntıyı anlatmak yerine, problem–yöntem–sonuç zincirini net tutmak daha ikna edici oluyor. Bugünkü prova bunu gösterdi.',[.87,.04,.22,.18],.00,.46,.80],

  // Kampüs & iş
  ['kampus_is','Kulüp odasında beş farklı bölümden insan aynı prototipe bakınca herkes başka bir risk gördü. Disiplinler arası ekip lafı ilk kez bu kadar somut geldi.',[.48,.16,.18,.82],.00,.67,.96],
  ['kampus_is','Staj görüşmesinde yaptığım projeyi anlatırken kullandığım teknoloji listesinden çok, karşılaştığım hatayı nasıl çözdüğüm soruldu.',[.74,.05,.16,.28],.00,.53,.92],
  ['kampus_is','TEKNOFEST için şehir dışına gidecek ekipte görev dağılımı yaptık: donanım, sunum, lojistik ve “her şeyi son kez kontrol eden kişi”.',[.38,.28,.20,.76],.00,.65,.89],
  ['kampus_is','Toplantı notlarını karar, sorumlu ve tarih şeklinde yazmaya başladık. Bir haftadır “onu kim yapacaktı?” cümlesini duymadım.',[.72,.05,.12,.36],.00,.48,.85],
  ['kampus_is','Portföye yalnızca bitmiş ekran görüntüsü koymak yerine süreçte aldığım teknik kararları da ekledim. Proje sonunda çok daha anlaşılır görünüyor.',[.86,.04,.14,.18],.00,.44,.82],

  // Ekonomi & bütçe
  ['ekonomi_butce','Prototip bütçesinde en pahalı parçayı değil, arızalandığında yerine koyması en zor parçayı ayrıca işaretledik. Risk hesabı toplam fiyattan farklıymış.',[.82,.03,.28,.08],.00,.42,.95],
  ['ekonomi_butce','Aynı sensör üç mağazada üç farklı fiyatta. Kargo ve teslim süresini ekleyince ilk bakışta ucuz görünen seçenek aslında en pahalı oldu.',[.76,.08,.34,.10],.01,.56,.90],
  ['ekonomi_butce','Öğrenci ekibi için sponsorluk dosyasında “bize destek olun” demek yetmiyor; karşı tarafa hangi görünürlüğü ve çıktıyı sunduğunu net yazmak gerekiyor.',[.79,.04,.22,.24],.00,.47,.86],
  ['ekonomi_butce','TEKNOFEST yolculuğu için konaklama, ulaşım ve yedek parça giderlerini ayrı tuttuğumuzda bütçe sonunda gerçekten okunabilir hale geldi.',[.66,.04,.38,.14],.00,.40,.82],
  ['ekonomi_butce','Bu ay dışarıda kahve sayısını azaltıp elektronik parça bütçesine aktardım. Bir kart geldi, sosyal hayat biraz beklemede. 😅',[.20,.62,.06,.34],.00,.63,.77],

  // Kültür & sanat
  ['kultur_sanat','Teknoloji sergisindeki en sevdiğim iş, sensörleri saklamayan bir yerleştirmeydi. Mekanizma görünür olunca eser daha az değil, daha çok şey anlattı.',[.62,.28,.22,.18],.00,.45,.94],
  ['kultur_sanat','Kısa film gösteriminden sonra yönetmenin kurgu kararlarını anlatması filmi ikinci kez izlemişim gibi hissettirdi.',[.46,.42,.16,.30],.00,.51,.90],
  ['kultur_sanat','TEKNOFEST alanında teknik projelerin yanında dijital sanat işleri görmek güzel olurdu; aynı araçlar bambaşka sorular sorabiliyor.',[.34,.36,.18,.70],.00,.58,.86],
  ['kultur_sanat','Kitap fuarında listeyle gezmeyi denedim ama yine hiç planlamadığım iki deneme kitabıyla çıktım. Bu kısmı algoritmaya bırakamıyorum.',[.18,.76,.08,.32],.00,.69,.81],
  ['kultur_sanat','Bir afişte kullanılan boşluk bazen başlıktan daha çok şey söylüyor. Sunum tasarlarken her köşeyi bilgiyle doldurmamak gerektiğini yeni anladım.',[.71,.12,.10,.14],.00,.41,.78],

  // Spor
  ['spor_futbol','Kampüs turnuvasında ilk maçı kaybettik ama ikinci maçta savunma düzenini tamamen değiştirdik. Skordan çok o uyum hoşuma gitti.',[.16,.46,.14,.78],.00,.64,.93],
  ['spor_futbol','Maç verilerinde yalnızca toplam koşu mesafesine bakınca iyi görünen oyuncu, yüksek tempolu koşularda geride kalmış. Tek metrik yine yanıltmış.',[.72,.14,.30,.10],.00,.49,.88],
  ['spor_futbol','Final maçını proje ekibiyle izlemek hata olabilir; herkes taktik konuşurken biri hâlâ sunumdaki eksik grafiği düşünüyor. ⚽',[.08,.82,.08,.58],.00,.73,.84],
  ['spor_futbol','Sabah koşusuna çıkmadan önce “yalnızca yirmi dakika” dedim. Başlamak için hedefi küçültmek gerçekten işe yarıyormuş.',[.38,.18,.06,.22],.00,.52,.79],
  ['spor_futbol','Robot futbol maçlarında mekanik tasarım kadar takım stratejisini izlemek de keyifli. Kodun sahada nasıl karar verdiği hemen belli oluyor.',[.54,.52,.18,.24],.00,.60,.75],

  // Oyun & e-spor
  ['oyun_espor','Takımla oynadığımız co-op bölümünde en zor bulmacayı çözdük, sonra çıkış kapısını on dakika bulamadık. Başarı oranımız tartışmalı. 😂',[.12,.94,.04,.68],.00,.78,.95],
  ['oyun_espor','Bir oyunun eğitim bölümü, kullanıcı arayüzü için iyi bir ders: gereken bilgiyi tam ihtiyaç anında veriyor, geri kalanını saklıyor.',[.82,.38,.08,.14],.00,.55,.91],
  ['oyun_espor','E-spor maçında skor tablosundan çok görüş kontrolü grafiğine bakınca geri dönüşün nasıl başladığı daha net görünüyor.',[.68,.30,.32,.12],.00,.48,.87],
  ['oyun_espor','Drone simülasyonunda rüzgârı biraz artırınca rahat kullandığım ayarlar dağıldı. Gerçek teste geçmeden önce iyi ki denemişiz.',[.78,.30,.14,.16],.00,.57,.83],
  ['oyun_espor','Yeni sezonda görev ekranını sadeleştirmişler; daha az rozet var ama ne yapmam gerektiğini ilk kez tek bakışta anladım.',[.42,.56,.28,.10],.00,.62,.78],

  // Gündelik yaşam
  ['gundelik_yasam','Yarışma yolculuğu için çanta hazırlarken yedek kablo sayısının kıyafet sayısını geçtiğini fark ettim. Öncelikler belli.',[.12,.82,.08,.36],.00,.74,.96],
  ['gundelik_yasam','Şarjı yüzde 8 kalan telefonla dönüş yolunu bulmaya çalışmak, günün beklenmedik mühendislik problemi oldu.',[.10,.78,.04,.28],.00,.67,.91],
  ['gundelik_yasam','Sabah ilk iş bildirimleri açmak yerine on dakika gün planı yaptım. Akşam olunca yarım kalan iş sayısı gerçekten azdı.',[.48,.10,.06,.16],.00,.43,.86],
  ['gundelik_yasam','Prova uzayınca akşam yemeği yine tost oldu. Ekipçe “yarın düzgün yeriz” sözünü kaçıncı kez verdiğimizi saymıyoruz.',[.08,.76,.04,.52],.00,.71,.82],
  ['gundelik_yasam','Yağmur başlayınca test alanından ekipmanı beş dakikada topladık. Organizasyon becerimiz en çok böyle anlarda gelişiyor sanırım.',[.34,.24,.12,.66],.00,.59,.77],

  // Sosyal
  ['sosyal_sohbet','TEKNOFEST’te daha önce yalnızca çevrimiçi konuştuğumuz başka bir ekiple sonunda yüz yüze tanıştık. İlk konu yine ortak hata mesajımızdı.',[.18,.42,.12,.96],.00,.76,.97],
  ['sosyal_sohbet','Sunum provası için dışarıdan birine anlatmak isteyen ekip var mı? Biz de karşılığında akış ve anlaşılabilirlik konusunda not verebiliriz.',[.44,.10,.08,.98],.00,.68,.93],
  ['sosyal_sohbet','Bugünkü geri bildirimde en değerli cümle “burayı anlamadım” oldu. İnsanlar nazikçe geçmeyince ürün gerçekten iyileşiyor.',[.58,.06,.10,.84],.00,.57,.88],
  ['sosyal_sohbet','Aynı şehirden yarışmaya gidecek ekipler için küçük bir ulaşım grubu açsak işe yarar mı? Saat ve güzergâh paylaşabiliriz.',[.16,.08,.26,.98],.00,.63,.84],
  ['sosyal_sohbet','Uzun süredir konuşmadığım arkadaşıma proje linkini attım; beş dakika sonra bulduğumuz en ciddi kullanılabilirlik hatasını söyledi.',[.36,.18,.08,.88],.00,.61,.79]
];

module.exports=rows.map((row,index)=>{
  const [kategori,metin,tahmin_niyet,clickbait,etkilesim_puani,tazelik]=row;
  const [yazar,author_id]=AUTHORS[index%AUTHORS.length];
  const sorted=[...tahmin_niyet].sort((a,b)=>b-a);
  return {
    id:`curated_${String(index+1).padStart(3,'0')}`,
    yazar,author_id,metin,kategori,kategori_adi:CATEGORY_LABELS[kategori],topic_family:kategori,
    style:'curated_natural',tahmin_niyet,clickbait,mixed_intent:sorted[1]>=.45,
    semantic_confidence:.94,semantic_method:'human_curated_intent_v1',etkilesim_puani,tazelik,
    content_provenance:'curated_original_competition_demo',
    source_basis:'competition_demo_editorial_set',
    author_provenance:'fictional_demo_pseudonym',
    ranking_metadata_provenance:'deterministic_curated_seed_plus_live_events'
  };
});
