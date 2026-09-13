#!/usr/bin/env python3
from __future__ import annotations
import json, random, re, statistics
from collections import Counter
from itertools import combinations
from pathlib import Path

SEED=26
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'v2_realistic'

TOPICS={
'egitim_yks':(
['yerleştirme sonucu','üniversite kayıt işi','ders seçimi','hazırlık muafiyet sınavı','yurt başvurusu','bölümün ders planı','kampüse ilk gidiş','seçmeli dersler'],
['{s} açıklanınca ilk baktığım şey şehir değil ders planı oldu 😅','{s} konusunda herkes başka bir şey söylüyor, resmi duyuruyu bulunca rahatladım.','{s} tamam da şu belge listesini tek yerde toplayan biri var mı?','{s} için küçük bir kontrol listesi yaptım; iki maddeyi son anda fark ettim.','Bugün {s} işini hallettim. sandığım kadar korkunç değilmiş, sadece sabır istiyor.','{s} yüzünden sabah üç sekme, iki PDF ve bir kahveyle başladım güne.','{s} yaklaşınca insan bir anda bölüm grubundaki bütün mesajları okumaya başlıyor.','{s} sonrası en mantıklısı önce takvimi yazmakmış; kafam biraz toparlandı.']),
'teknoloji_ai':(
['yerelde çalışan küçük dil modeli','telefonun yeni yapay zekâ özelliği','kod tamamlama aracı','açık kaynak bir model','GPU belleği','yeni tarayıcı özelliği','otomatik özet aracı','sesli asistan'],
['{s} denedim; demo etkileyici ama günlük işte hız daha önemliymiş.','{s} için herkes model boyutunu konuşuyor, ben hâlâ gecikme süresine bakıyorum.','{s} bugün bir işimi gerçekten hızlandırdı, ilk kez “tamam bu işe yarıyor” dedim.','{s} güzel de gizlilik ayarlarını bulmak niye bu kadar zor 😅','{s} konusunda küçük modeller bazen beklediğimden daha mantıklı sonuç veriyor.','{s} ile 20 dakikalık işi 5 dakikaya indirdim ama çıktıyı yine elle kontrol ettim.','{s} kullanırken en çok hoşuma giden şey hız değil, tekrar eden işi azaltması oldu.','{s} için benchmark paylaşan varsa atabilir mi? sadece reklam videosuna güvenemiyorum.']),
'teknofest_maker':(
['uçuş öncesi kontrol','son test videosu','rapor teslimi','sensör kalibrasyonu','motor testi','sunum provası','kablolama düzeni','final öncesi son gün'],
['{s} bitti sanıyorsun, sonra bir vida çıkıp bütün akşamı sahipleniyor.','{s} için ekipçe aynı checklist’i kullanmak hayat kurtarıyor.','{s} tamamlandı ✅ şimdi sırada gerçekten çalıştığını tekrar tekrar kanıtlamak var.','{s} sırasında küçük bir hata bulduk; iyi ki sahaya çıkmadan yakaladık.','TEKNOFEST haftasında {s} diye bir şey varsa uykudan feragat ediyorsun biraz 😅','{s} konusunda bugün en büyük ders: kabloyu etiketle, sonra kendine teşekkür edersin.','{s} sonrası ekipçe 10 dakika sessizce ekrana baktık. çalışınca insan inanamıyor.','{s} için son değişikliği yapmamak bazen en doğru mühendislik kararıymış.']),
'spor_futbol':(
['milli maç','hafta sonu maçı','son dakikadaki gol','VAR kararı','ilk 11','deplasman maçı','kalecinin kurtarışı','maç sonrası yorumlar'],
['{s} için arkadaş grubunda skor tahmini şimdiden kavgaya döndü 😄','{s} sonrası herkes teknik direktör oldu yine.','{s} güzeldi ama ikinci yarıda tempo resmen başka maça dönüştü.','{s} konusunda tribün sesi televizyondan bile ayrı bir şey.','{s} için “bu kez sakin izlerim” dedim, 15 dakika sürdü.','{s} sonrası özet izlemek yetmedi, pozisyonları tek tek geri sardım.','{s} bence sonucu değil oyunun gidişini değiştirdi.','{s} hakkında yorum yapmadan önce tekrarını izlemek lazım, ilk anda çok farklı görünüyor.']),
'kultur_sanat':(
['açık hava konseri','şehirdeki festival','yeni bir sergi','bağımsız film gösterimi','küçük bir tiyatro oyunu','caz konseri','kitap fuarı','sokak performansı'],
['{s} için “bir saat kalırım” diye gittim, kapanışa kadar çıkamadım.','{s} beklediğimden çok daha iyiydi; özellikle kalabalığın enerjisi güzeldi.','{s} gibi etkinliklerin şehirde daha sık olması lazım.','{s} sonrası eve dönerken hâlâ müzik kafamda dönüyordu.','{s} için bilet alıp son anda gitmekten vazgeçmeyin, iyi ki gitmişim dedim.','{s} hakkında hiç beklentim yoktu, en sevdiğim şey bu oldu galiba.','{s} kalabalıktı ama organizasyon şaşırtıcı derecede rahattı.','{s} için tek eleştirim: keşke programı daha erken paylaşsalardı.']),
'ekonomi_butce':(
['market sepeti','kahve fiyatı','öğrenci bütçesi','abonelikler','ulaşım masrafı','evde yemek yapmak','indirim kampanyası','aylık harcama tablosu'],
['{s} konusunda bu ay ilk kez gerçekten not tutmaya başladım.','{s} küçük görünüyordu ama ay sonunda en çok orası toplamış.','{s} için fiyat karşılaştırmadan almak artık içime sinmiyor.','{s} konusunda “nasıl olsa az” dediğim şeyler birleşince bayağı oluyor.','{s} için bir haftalık deneme yaptım, beklediğimden fazla fark etti.','{s} yüzünden bütçe uygulamasını yeniden açtım 😅','{s} konusunda en işe yarayan şey kampanya kovalamak değil plan yapmakmış.','{s} için eski fişlere bakınca fiyat hissim tamamen bozulmuş onu fark ettim.']),
'oyun_espor':(
['ranked maç','yeni sezon','co-op oyun','indirimde aldığım oyun','gece yapılan turnuva','yeni yama','boss savaşı','oyunun ses tasarımı'],
['{s} için “bir el girip çıkarım” dedim, saat olmuş 2.','{s} sonrası ekipçe konuşmadan lobiye döndük 😭','{s} beklediğimden iyi çıktı; mekanikler ilk yarım saatte oturuyor.','{s} konusunda herkes meta konuşuyor, ben eğleniyor muyum ona bakıyorum.','{s} ile ilgili en iyi şey grafik değil, akışın hiç kesilmemesi.','{s} sonrası patch notlarını gerçekten okumaya başladım.','{s} için arkadaşla girmek oyunu tek başına oynamaktan tamamen farklı.','{s} biraz sinir etti ama bırakamadım, iyi tasarım böyle bir şey herhalde.']),
'kampus_is':(
['ilk staj günü','toplantı trafiği','kampüste boş ders','sunum hazırlığı','grup projesi','uzaktan çalışma günü','lab dersi','deadline haftası'],
['{s} beklediğimden daha sakin geçti, stresin çoğunu ben üretmişim.','{s} için yapılacakları üçe bölünce bir anda daha yönetilebilir oldu.','{s} bugün bütün planı bozdu ama en faydalı konuşma da orada çıktı.','{s} sırasında herkes aynı anda “küçük bir değişiklik” isteyince işler büyüdü 😅','{s} sonrası notları düzenlemek işin kendisinden uzun sürdü.','{s} için erken başlamanın neden söylendiğini bugün bir kez daha anladım.','{s} boyunca kahve değil su içmeyi hatırlamak başarı sayılır.','{s} bitti; geriye sadece “bir daha son güne bırakmayacağım” sözü kaldı.']),
'gundelik_yasam':(
['otobüs beklemek','sabah kahvesi','çamaşır günü','evde internetin gitmesi','telefon şarjı','alışveriş listesi','erken uyanmak','akşam yürüyüşü'],
['{s} bugün gereksiz yere hayatımın ana olayı oldu.','{s} konusunda küçük bir düzen kurunca gün gerçekten daha az yoruyor.','{s} için “5 dakika sürer” dediğim her şey gibi 40 dakika sürdü.','{s} sırasında insanın sabrının yüzde kaç kaldığını ölçen uygulama lazım.','{s} sonrası dünya biraz daha yaşanabilir geldi.','{s} ile ilgili tek hedefim bunu düşünmeden yapabildiğim bir rutin haline getirmek.','{s} bugün tam bir karakter gelişimi bölümüydü 😅','{s} yüzünden plan değişti ama sonunda daha iyi oldu.']),
'sosyal_sohbet':(
['eski arkadaşla denk gelmek','grup sohbeti','doğum günü planı','yeni biriyle tanışmak','uzun bir telefon konuşması','kahve buluşması','ortak playlist','hafta sonu planı'],
['{s} bazen bütün haftanın modunu değiştiriyor.','{s} için plan yaparken 20 mesaj atıp sonunda ilk seçeneğe dönmek klasik.','{s} beklediğimden daha iyi geldi; biraz sosyalleşmek lazımmış.','{s} sonrası eve gelip “iyi ki gitmişim” dedim.','{s} konusunda en zor kısım saat belirlemekmiş, gerisi kolay.','{s} ile günün nasıl geçtiğini anlamadım.','{s} bugün çok basit bir şeydi ama moralimi bayağı düzeltti.','{s} için bu kadar uzun konuşacağımızı kimse tahmin etmiyordu 😄'])}

SOURCE_NOTES='''# Dataset V2 — Web araştırması ve kaynak notları\n\nBu korpus gerçek kullanıcı gönderilerinin kopyası değildir. Web araştırması yalnızca Türkiye'deki güncel kamusal konu ekolojisini belirlemek için kullanıldı; tüm metinler PUSULA Semantic V2 için özgün olarak üretildi.\n\nKonu sinyalleri: DataReportal Digital 2026 Turkey; ÖSYM 2026-YKS duyuruları; TEKNOFEST 2026 resmi sayfaları; TFF resmi fikstürü; TÜİK Ağustos 2026 TÜFE bülteni; kamuya açık kültür-sanat festival haberleri.\n\nGerçek kullanıcı adı, gönderi URL'si, telefon, e-posta veya başka kişisel tanımlayıcı tutulmaz. İlk tranche 320 kayıttır; önce kalite ve benchmark doğrulanır, gerekirse 480–600 aralığına genişletilir.\n'''

def toks(s): return set(re.findall(r'\w+',s.lower(),flags=re.UNICODE))

def build():
    random.seed(SEED); rows=[]; rid=1
    for topic,(subjects,templates) in TOPICS.items():
        combos=[(s,t) for s in subjects for t in templates]; random.shuffle(combos)
        for i,(s,t) in enumerate(combos[:32]):
            text=t.format(s=s); style='plain'
            if i%4==1: text=text[0].lower()+text[1:]; style='casual_lower'
            elif i%4==2: text+=random.choice([' 🙂',' 🙃',' 😂',' ✨',' 🤝',' 👀']); style='emoji_end'
            elif i%4==3: text=text.rstrip('.!?')+random.choice(['; sizde de böyle mi?',' siz ne düşünüyorsunuz?',' başka yaşayan var mı?']); style='question'
            flags=[]
            if i%9==4 and 'bir ' in text: text=text.replace('bir ','bi ',1); flags.append('colloquial')
            if re.search(r'[😅😄😭🙂🙃😂✨🤝👀✅]',text): flags.append('emoji')
            if '?' in text: flags.append('question')
            if topic in {'teknoloji_ai','teknofest_maker'}: flags.append('tech')
            rows.append({'id':f'v2r_{rid:04d}','text':text,'topic_family':topic,'style':style,'style_flags':sorted(set(flags)),'provenance':'synthetic_original','source_basis':'public_topic_ecology_not_user_posts','human_label':None}); rid+=1
    return rows

def validate(rows):
    assert len(rows)==320 and len({r['id'] for r in rows})==320 and len({r['text'] for r in rows})==320
    counts=Counter(r['topic_family'] for r in rows); assert set(counts.values())=={32}
    pii=[re.compile(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b'),re.compile(r'https?://|www\.',re.I),re.compile(r'(?<!\d)(?:\+?90\s*)?0?5\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)'),re.compile(r'(?<!\d)\d{11}(?!\d)'),re.compile(r'(?<!\w)@[A-Za-z0-9_]{2,}')]
    for r in rows:
        assert 20<=len(r['text'])<=280
        assert r['provenance']=='synthetic_original' and r['human_label'] is None
        assert not any(p.search(r['text']) for p in pii)
    sets=[toks(r['text']) for r in rows]
    for i,j in combinations(range(len(rows)),2):
        u=sets[i]|sets[j]; sim=len(sets[i]&sets[j])/len(u) if u else 1
        assert sim<.90,(rows[i]['id'],rows[j]['id'],sim)

def main():
    rows=build(); validate(rows); OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'raw_posts.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in rows)+'\n',encoding='utf-8')
    lens=[len(r['text']) for r in rows]
    stats={'schema_version':'raw-v2.1','record_count':len(rows),'unique_text_count':len({r['text'] for r in rows}),'topic_distribution':dict(sorted(Counter(r['topic_family'] for r in rows).items())),'style_distribution':dict(sorted(Counter(r['style'] for r in rows).items())),'text_length_chars':{'min':min(lens),'median':statistics.median(lens),'mean':round(statistics.mean(lens),2),'max':max(lens)},'privacy':{'copied_user_posts':0,'user_handles':0,'emails':0,'phone_numbers':0,'urls':0,'tckn_like_11_digit_sequences':0}}
    (OUT/'corpus_stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'SOURCE_NOTES.md').write_text(SOURCE_NOTES,encoding='utf-8')
    print('OK',len(rows),'records')

if __name__=='__main__': main()
