const CATEGORY_LABELS={
  egitim_yks:'Eğitim',teknoloji_ai:'Yapay zekâ & teknoloji',teknofest_maker:'Teknoloji & maker',
  spor_futbol:'Spor',kultur_sanat:'Kültür & sanat',ekonomi_butce:'Ekonomi & bütçe',
  oyun_espor:'Oyun & e-spor',kampus_is:'Kampüs & iş',gundelik_yasam:'Gündelik yaşam',
  sosyal_sohbet:'Sosyal'
};

const TEKNOFEST_HOME='https://www.teknofest.org/en/';
const rows=[
  // TEKNOFEST 2026 — official announcements and calendar
  ['teknofest','gundelik_yasam','2026-09-10','TEKNOFEST',TEKNOFEST_HOME,'TEKNOFEST Güneydoğu için ziyaretçi kaydı açıldı','Festival 30 Eylül–4 Ekim 2026 tarihlerinde Şanlıurfa GAP Havalimanı’nda düzenlenecek. Katılım ücretsiz; ziyaretçilerin çevrim içi kayıt oluşturması gerekiyor.'],
  ['teknofest','teknofest_maker','2026-09-18','TEKNOFEST',TEKNOFEST_HOME,'Sıfır Atık ve Döngüsel Ekonomi Yarışması sonuçlandı','TEKNOFEST 2026 Sıfır Atık ve Döngüsel Ekonomi Yarışması’nın final sonuçları resmî duyuru sayfasında yayımlandı. Takımlar sonuç belgesini kaynak bağlantısından inceleyebiliyor.'],
  ['teknofest','teknofest_maker','2026-09-17','TEKNOFEST',TEKNOFEST_HOME,'Hyperloop Geliştirme Yarışması final değerlendirmesi açıklandı','Hyperloop Geliştirme Yarışması’nın final değerlendirme sonuçları yayımlandı. Duyuru, yarışmacıları resmî sonuç belgesine yönlendiriyor.'],
  ['teknofest','teknofest_maker','2026-09-17','TEKNOFEST',TEKNOFEST_HOME,'Efficiency Challenge elektrikli araç sonuçları yayımlandı','Uluslararası Efficiency Challenge Elektrikli Araç Yarışması’nın final değerlendirme sonuçları TEKNOFEST tarafından duyuruldu.'],
  ['teknofest','teknoloji_ai','2026-09-15','TEKNOFEST',TEKNOFEST_HOME,'Kuantum Teknolojileri Yarışması final sonuçları açıklandı','TEKNOFEST 2026 Kuantum Teknolojileri Yarışması’nın final sonuçları resmî duyuru akışında yayımlandı.'],
  ['teknofest','teknoloji_ai','2026-09-15','TEKNOFEST',TEKNOFEST_HOME,'5G ve Yapay Zekâ Destekli Akıllı Yol Güvenliği sıralaması belli oldu','5G ve Yapay Zekâ Destekli Akıllı Yol Güvenliği Yarışması’nın final sıralaması TEKNOFEST tarafından ilan edildi.'],
  ['teknofest','teknofest_maker','2026-09-15','TEKNOFEST',TEKNOFEST_HOME,'Sürü İHA Yarışması finalist sıralaması yayımlandı','TEKNOFEST 2026 Sürü İHA Yarışması’nın finalist sıralaması resmî duyuruyla erişime açıldı.'],
  ['teknofest','teknoloji_ai','2026-09-15','TEKNOFEST',TEKNOFEST_HOME,'Nükleer Enerji Teknolojileri Tasarım Yarışması sonuçlandı','Nükleer Enerji Teknolojileri Tasarım Yarışması’nın final sıralaması TEKNOFEST duyurularında yayımlandı.'],
  ['teknofest','teknoloji_ai','2026-09-15','TEKNOFEST',TEKNOFEST_HOME,'Robotaksi yarışmasının final sıralaması açıklandı','Robotaksi Binek Otonom Araç Yarışması’nın final sıralaması yayımlandı. Sonuç ayrıntıları resmî TEKNOFEST duyurusundan görüntülenebiliyor.'],
  ['teknofest','teknofest_maker','2026-09-14','TEKNOFEST',TEKNOFEST_HOME,'Savaşan İHA Yıldızlar Yarışması final sonuçları yayımlandı','Savaşan İHA Yıldızlar kategorisinin final sonuçları TEKNOFEST’in resmî duyuru akışında paylaşıldı.'],
  ['teknofest','teknofest_maker','2026-09-14','TEKNOFEST',TEKNOFEST_HOME,'Savaşan İHA Yarışması final sıralaması belli oldu','TEKNOFEST 2026 Savaşan İHA Yarışması’nın final sıralaması yarışmacılar için erişime açıldı.'],
  ['teknofest','teknofest_maker','2026-09-14','TEKNOFEST',TEKNOFEST_HOME,'Su Altı Roket Yarışması final aşaması tamamlandı','Su Altı Roket Yarışması’nın final aşaması sonuçları resmî TEKNOFEST kanallarından duyuruldu.'],
  ['teknofest','teknoloji_ai','2026-09-14','TEKNOFEST',TEKNOFEST_HOME,'Pardus öneri ve hata bulma yarışmasının kazananları açıklandı','Pardus Öneri ve Hata Yakalama Yarışması’nda dereceye giren takımlar TEKNOFEST tarafından açıklandı.'],
  ['teknofest','teknoloji_ai','2026-09-11','TEKNOFEST',TEKNOFEST_HOME,'Sağlıkta Yapay Zekâ yarışmasında rapor sonuçları yayımlandı','Sağlıkta Yapay Zekâ Yarışması’nın proje detay raporu değerlendirme sonuçları duyuruldu.'],
  ['teknofest','kultur_sanat','2026-09-09','TEKNOFEST',TEKNOFEST_HOME,'“Sahne Senin” başvuruları TEKNOFEST Güneydoğu için açıldı','Şanlıurfa’daki festival programına yönelik “Sahne Senin” duyurusu yayımlandı; başvuru ayrıntıları resmî sayfada yer alıyor.'],
  ['teknofest','kampus_is','2026-09-07','TEKNOFEST',TEKNOFEST_HOME,'TEKNOFEST Spotter Kulesi başvuruları başladı','TEKNOFEST Güneydoğu kapsamında Spotter Kulesi başvurularının açıldığı duyuruldu. Koşullar ve başvuru yönlendirmesi resmî sayfada.'],
  ['teknofest','sosyal_sohbet','2026-09-04','TEKNOFEST',TEKNOFEST_HOME,'Diyarbakır ziyaretçi kaydı erişime açıldı','TEKNOFEST Güneydoğu’nun Diyarbakır ayağı için ziyaretçi kayıtlarının başladığı duyuruldu.'],
  ['teknofest','egitim_yks','2026-09-04','TEKNOFEST',TEKNOFEST_HOME,'Biyoteknoloji İnovasyon Yarışması rapor sonuçları açıklandı','Biyoteknoloji İnovasyon Yarışması proje detay raporu değerlendirme sonuçları yayımlandı.'],
  ['teknofest','egitim_yks','2026-09-04','TEKNOFEST',TEKNOFEST_HOME,'İnsanlık Yararına Teknoloji ortaokul sunum sıralaması yayımlandı','Ortaokul seviyesindeki İnsanlık Yararına Teknoloji Yarışması için proje sunumu sıralaması açıklandı.'],
  ['teknofest','teknofest_maker','2026-09-04','TEKNOFEST',TEKNOFEST_HOME,'Jet Motor Tasarım Yarışması detaylı tasarım sonuçları açıklandı','Jet Motor Tasarım Yarışması’nın detaylı tasarım raporu değerlendirme sonuçları TEKNOFEST tarafından yayımlandı.'],

  // Artificial intelligence — original summaries of official product/research posts
  ['ai','teknoloji_ai','2025-04-16','OpenAI','https://openai.com/index/introducing-o3-and-o4-mini/','OpenAI, o3 ve o4-mini modellerini tanıttı','Yeni akıl yürütme modelleri; web araması, dosya analizi, Python ve görsel araçları gerektiğinde birlikte kullanabilecek şekilde tasarlandı.'],
  ['ai','kampus_is','2025-04-16','OpenAI','https://openai.com/index/introducing-o3-and-o4-mini/','Codex CLI açık kaynaklı deney olarak yayımlandı','OpenAI, terminalde kod tabanıyla çalışabilen Codex CLI aracını o3 ve o4-mini duyurusuyla birlikte açık kaynak olarak paylaştı.'],
  ['ai','egitim_yks','2025-02-02','OpenAI','https://openai.com/index/introducing-deep-research/','ChatGPT için derin araştırma özelliği duyuruldu','Derin araştırma, çok adımlı internet araştırmalarını tamamlayıp bulguları kaynaklarla birlikte raporlamak üzere tasarlandı.'],
  ['ai','teknoloji_ai','2025-03-25','OpenAI','https://openai.com/index/introducing-4o-image-generation/','GPT-4o ile yerleşik görsel üretimi kullanıma sunuldu','OpenAI, görsel üretimini sohbet akışına yerleştiren ve metin talimatlarını daha yakından izlemeyi hedefleyen yeni sistemi tanıttı.'],
  ['ai','kampus_is','2025-03-11','OpenAI','https://openai.com/index/new-tools-for-building-agents/','OpenAI, ajan geliştirmek için Responses API’yi duyurdu','Responses API; web araması, dosya araması ve bilgisayar kullanımı gibi araçları ajan uygulamalarında birleştirmek için sunuldu.'],
  ['ai','teknoloji_ai','2025-05-22','Anthropic','https://www.anthropic.com/news/claude-4','Anthropic, Claude Opus 4 ve Sonnet 4’ü tanıttı','Claude 4 ailesi özellikle kodlama, gelişmiş akıl yürütme ve uzun süren görevler için geliştirilen iki yeni modelle duyuruldu.'],
  ['ai','kampus_is','2025-02-24','Anthropic','https://www.anthropic.com/news/claude-3-7-sonnet','Claude 3.7 Sonnet hibrit akıl yürütmeyle duyuruldu','Anthropic, hızlı yanıt ile daha uzun düşünme biçimlerini aynı modelde birleştiren Claude 3.7 Sonnet’i tanıttı.'],
  ['ai','sosyal_sohbet','2025-05-01','Anthropic','https://www.anthropic.com/news/integrations','Claude için Integrations ve gelişmiş Research geldi','Anthropic, Claude’un uzak araç ve veri kaynaklarına bağlanmasını sağlayan Integrations özelliğini ve genişletilmiş araştırma modunu duyurdu.'],
  ['ai','teknoloji_ai','2025-03-25','Google DeepMind','https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-model-thinking-updates-march-2025/','Google, Gemini 2.5 Pro’yu duyurdu','Gemini 2.5 serisi, yanıt öncesinde akıl yürütmeye odaklanan yeni model ailesi olarak tanıtıldı.'],
  ['ai','kampus_is','2025-03-12','Google','https://blog.google/technology/developers/gemma-3/','Google, açık model ailesi Gemma 3’ü yayımladı','Gemma 3; metin ve görsel girdileri destekleyen, farklı donanım ölçeklerine yönelik açık ağırlıklı modellerle duyuruldu.'],
  ['ai','teknoloji_ai','2025-05-20','Google','https://blog.google/technology/google-deepmind/google-gemini-updates-io-2025/','Google I/O’da Gemini güncellemeleri açıklandı','Google, Gemini modelleri ve ürünleri için canlı etkileşim, araştırma ve geliştirici araçlarına uzanan bir dizi yenilik paylaştı.'],
  ['ai','egitim_yks','2025-04-05','Meta AI','https://ai.meta.com/blog/llama-4-multimodal-intelligence/','Meta, Llama 4 model ailesini duyurdu','Llama 4, metin ve görsel girdileri birlikte işleyebilen açık ağırlıklı modellerden oluşan yeni aile olarak tanıtıldı.'],
  ['ai','teknoloji_ai','2025-02-19','Microsoft Research','https://www.microsoft.com/en-us/research/blog/phi-4-multimodal-and-phi-4-mini-now-available-on-azure-ai-foundry/','Phi-4-mini ve Phi-4-multimodal erişime açıldı','Microsoft, küçük model ailesine metin, görüntü ve konuşma senaryolarını hedefleyen iki yeni Phi-4 modeli ekledi.'],
  ['ai','egitim_yks','2025-02-27','Hugging Face','https://huggingface.co/blog/smolagents','Hugging Face, smolagents kütüphanesini tanıttı','Açık kaynaklı smolagents, dil modellerinin araç kullandığı ajan akışlarını az kodla kurmayı hedefliyor.'],
  ['ai','teknoloji_ai','2025-05-12','Hugging Face','https://huggingface.co/blog/agents-course','Hugging Face ajan eğitimi için ücretsiz kurs yayımladı','Ücretsiz Agents Course, araç kullanan yapay zekâ ajanlarını temel kavramlardan uygulamalı örneklere kadar ele alıyor.'],
  ['ai','ekonomi_butce','2025-01-21','Mistral AI','https://mistral.ai/news/mistral-small-3','Mistral Small 3 açık kaynak olarak yayımlandı','Mistral AI, düşük gecikmeli metin görevleri ve yerel kullanım senaryolarına odaklanan Mistral Small 3 modelini duyurdu.'],
  ['ai','teknoloji_ai','2025-05-06','NVIDIA','https://blogs.nvidia.com/blog/llama-nemotron-reasoning-models/','NVIDIA, Llama Nemotron akıl yürütme modellerini paylaştı','NVIDIA’nın model ailesi; ajan, kodlama ve çok adımlı akıl yürütme uygulamalarına yönelik açık modeller sunuyor.'],
  ['ai','gundelik_yasam','2025-04-29','Microsoft','https://blogs.microsoft.com/blog/2025/04/29/introducing-copilot-mode-in-microsoft-edge/','Microsoft Edge için Copilot Mode duyuruldu','Yeni tarayıcı modu, açık sekmeler ve web görevleri üzerinde Copilot destekli yardım sunmayı hedefliyor.'],
  ['ai','kultur_sanat','2025-01-15','Adobe','https://blog.adobe.com/en/publish/2025/04/24/new-firefly-models-and-creative-cloud-innovations','Adobe, Firefly ve Creative Cloud yeniliklerini tanıttı','Adobe; görsel üretim modelleri, yaratıcı kontroller ve Creative Cloud uygulamalarındaki yapay zekâ özelliklerini genişletti.'],
  ['ai','kampus_is','2025-02-06','GitHub','https://github.blog/news-insights/product-news/github-copilot-the-agent-awakens/','GitHub Copilot için agent mode tanıtıldı','Agent mode, bir geliştirme görevi boyunca dosyaları düzenleme, komut çalıştırma ve hataları yinelemeli biçimde düzeltme akışı sunuyor.'],

  // Software and developer ecosystem — official release notes
  ['software','teknoloji_ai','2025-05-06','Node.js','https://nodejs.org/en/blog/release/v24.0.0','Node.js 24 yayımlandı','Node.js 24 yeni V8 sürümü, güncellenmiş npm ve çalışma zamanı iyileştirmeleriyle kullanıma sunuldu.'],
  ['software','kampus_is','2025-10-07','Python','https://www.python.org/downloads/release/python-3140/','Python 3.14 kararlı sürümü yayımlandı','Python 3.14; dil, standart kütüphane, hata mesajları ve performans alanlarında bir dizi yenilik getiriyor.'],
  ['software','teknoloji_ai','2025-04-04','GitHub','https://github.blog/changelog/2025-04-04-copilot-code-review-now-generally-available/','GitHub Copilot code review genel kullanıma açıldı','Copilot code review, pull request ve seçili kod değişiklikleri için yapay zekâ destekli inceleme önerileri sunuyor.'],
  ['software','kampus_is','2025-02-06','GitHub','https://github.blog/news-insights/product-news/github-copilot-the-agent-awakens/','GitHub Copilot agent mode VS Code’a geldi','Agent mode, geliştiricinin verdiği hedef doğrultusunda kod tabanında çok adımlı değişiklikler yapabilen bir çalışma biçimi sunuyor.'],
  ['software','teknoloji_ai','2025-02-13','Rust','https://blog.rust-lang.org/2025/02/13/Rust-1.84.1/','Rust 1.84.1 düzeltme sürümü yayımlandı','Rust ekibi, kararlı araç zinciri için hata düzeltmeleri içeren 1.84.1 sürümünü duyurdu.'],
  ['software','kampus_is','2025-03-05','TypeScript','https://devblogs.microsoft.com/typescript/announcing-typescript-5-8/','TypeScript 5.8 yayımlandı','TypeScript 5.8, modül sistemi kontrolleri ve derleyici davranışlarında geliştirmelerle genel kullanıma sunuldu.'],
  ['software','teknoloji_ai','2025-04-29','Microsoft','https://devblogs.microsoft.com/typescript/typescript-native-port/','TypeScript derleyicisinin yerel portu duyuruldu','Microsoft, TypeScript araçlarının performansını artırmayı hedefleyen Go tabanlı yerel port çalışmasını paylaştı.'],
  ['software','kampus_is','2025-03-27','Docker','https://www.docker.com/blog/introducing-docker-model-runner/','Docker Model Runner duyuruldu','Docker, yapay zekâ modellerini yerel ortamda indirip çalıştırmaya yönelik Model Runner özelliğini tanıttı.'],
  ['software','teknoloji_ai','2025-05-20','Google','https://developers.googleblog.com/en/android-studio-narwhal-feature-drop/','Android Studio Narwhal özellikleri duyuruldu','Android geliştirme ortamının yeni özellikleri; üretkenlik, kalite kontrolleri ve Gemini destekli geliştirme akışlarına odaklanıyor.'],
  ['software','kampus_is','2025-03-19','Kubernetes','https://kubernetes.io/blog/2025/03/19/kubernetes-v1-33-release/','Kubernetes 1.33 sürüm süreci duyuruldu','Kubernetes topluluğu 1.33 sürümündeki özellikleri ve küme yöneticilerini ilgilendiren değişiklikleri resmî blogda topladı.'],
  ['software','teknoloji_ai','2025-04-30','Ubuntu','https://ubuntu.com/blog/canonical-releases-ubuntu-25-04-plucky-puffin','Ubuntu 25.04 yayımlandı','Plucky Puffin kod adlı Ubuntu 25.04, güncel çekirdek ve masaüstü bileşenleriyle kullanıma sunuldu.'],
  ['software','kampus_is','2025-04-15','GitLab','https://about.gitlab.com/releases/2025/04/17/gitlab-17-11-released/','GitLab 17.11 kullanıma sunuldu','GitLab’ın yeni sürümü yazılım yaşam döngüsü, güvenlik ve ekip iş birliğine yönelik iyileştirmeler içeriyor.'],
  ['software','oyun_espor','2025-03-19','Unity','https://unity.com/releases/editor/whats-new/6000.1.0','Unity 6.1 yayımlandı','Unity 6.1; render, performans ve çoklu platform geliştirme araçlarında güncellemelerle erişime açıldı.'],
  ['software','kultur_sanat','2025-04-15','Blender','https://www.blender.org/download/releases/4-4/','Blender 4.4 yayımlandı','Blender 4.4; modelleme, animasyon, render ve üretim hattı araçlarına yönelik yenilikler getiriyor.'],
  ['software','teknoloji_ai','2025-05-15','Cloudflare','https://blog.cloudflare.com/containers-are-available-in-public-beta-for-simple-global-and-programmable/','Cloudflare Containers genel betaya açıldı','Cloudflare, konteyner tabanlı iş yüklerini küresel altyapıda çalıştırmaya yönelik hizmetini genel beta olarak duyurdu.'],
  ['software','kampus_is','2025-04-08','PostgreSQL','https://www.postgresql.org/about/news/postgresql-175-169-1513-1418-and-1321-released-3055/','PostgreSQL bakım sürümleri yayımlandı','PostgreSQL projesi desteklenen ana sürümler için hata ve güvenlik düzeltmeleri içeren bakım güncellemelerini duyurdu.'],
  ['software','teknoloji_ai','2025-05-14','Vercel','https://vercel.com/blog/ai-sdk-5-beta','Vercel AI SDK 5 beta duyuruldu','AI SDK 5 beta; ajan döngüleri, araç kullanımı ve sohbet uygulamalarındaki veri akışını geliştiren yeni arayüzler sunuyor.'],
  ['software','kampus_is','2025-04-22','React','https://react.dev/blog/2025/04/21/react-compiler-rc','React Compiler sürüm adayı yayımlandı','React ekibi, bileşen ve hook optimizasyonlarını otomatikleştirmeyi amaçlayan derleyicinin sürüm adayını paylaştı.'],
  ['software','teknoloji_ai','2025-03-04','Mozilla','https://developer.mozilla.org/en-US/blog/mdn-curriculum-learn-web-development/','MDN web geliştirme öğrenme yolunu yeniledi','MDN Curriculum, temel web becerilerini düzenli bir öğrenme sırasıyla sunan açık eğitim kaynağı olarak güncellendi.'],
  ['software','ekonomi_butce','2025-04-09','Linux Foundation','https://www.linuxfoundation.org/press/linux-foundation-launches-agent2agent-protocol-project','Agent2Agent protokol projesi Linux Foundation’a taşındı','A2A projesi, farklı yapay zekâ ajanlarının birlikte çalışabilmesi için açık bir standart geliştirmeyi amaçlıyor.']
];

module.exports=rows.map((row,index)=>{
  const [news_kind,kategori,news_date,source_name,source_url,headline,metin]=row;
  const ageBoost=news_date.startsWith('2026')?.98:.88;
  const intent=news_kind==='teknofest'?[.34,.04,1,.10]:news_kind==='ai'?[.62,.03,.98,.06]:[.72,.02,.94,.05];
  return {
    id:`news_${String(index+1).padStart(3,'0')}`,
    yazar:source_name,author_id:`source_${source_name.toLocaleLowerCase('tr-TR').replace(/[^a-z0-9]+/g,'_')}`,
    headline,metin,kategori,kategori_adi:CATEGORY_LABELS[kategori],topic_family:kategori,
    style:'verified_news',news_kind,news_date,source_name,source_url,
    tahmin_niyet:intent,clickbait:.01,mixed_intent:intent[0]>=.60,
    semantic_confidence:.98,semantic_method:'human_editorial_official_source_v1',
    etkilesim_puani:.58+(index%7)*.035,tazelik:ageBoost-(index%5)*.012,
    like_count:24+(index*17)%430,comment_count:3+(index*7)%58,share_count:5+(index*11)%120,
    content_provenance:'official_source_news_summary',source_basis:'official_primary_source',
    author_provenance:'official_source_identity',ranking_metadata_provenance:'deterministic_editorial_seed_plus_live_events'
  };
});
