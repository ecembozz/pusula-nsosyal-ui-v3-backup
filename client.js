window.G={f:[],c:null,m:null,b:null,l:true,e:null,n:30,q:'',tab:'feed',tm:null,st:0};
const E=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]||c));
const F=x=>Number(x||0).toFixed(3);
const AC=id=>['cyan','green','orange','pink'][Array.from(String(id)).reduce((s,c)=>s+c.codePointAt(0),0)%4];
const MEDIA_CATS=new Set(['kultur_sanat','oyun_espor','spor_futbol']);
const TECH_META_V5={
  overview:['Genel bakış','Sistemin çalışan teknik özeti.'],
  models:['Model karşılaştırması','Semantik adayların aynı development setindeki karşılaştırması.'],
  compare:['Canlı karşılaştırma','Aynı 320 gönderide klasik ve PUSULA sıralamasını yan yana incele.'],
  math:['Matematik & skor ayrıştırma','Niyet uyumu, kalite, tazelik ve etkileşim sinyallerini adım adım gör.'],
  experiment:['Runtime davranış testi','Beş niyette aynı 320 gönderinin Klasik vs PUSULA top-20 davranışı.'],
  architecture:['Mimari & doğrulama','Offline semantic labeling, Candidate V5 cache ve runtime ranking zinciri.'],
};

async function A(p){let r=await fetch('/api/pusula?'+new URLSearchParams(p),{cache:'no-store'}),d=await r.json();if(!r.ok||!d.ok)throw Error(d.error||r.status);return d}
async function LF(m){G.l=true;if(G.f.length)render();try{let d=await A({action:'feed',intent:S.intent||'learn',mode:m||(!S.intent?'classic':S.mode),limit:G.n});G.f=d.posts;G.src=d.source;G.fm=d.metrics;G.e=null;if(S.intent)LC()}catch(e){G.e=e.message;G.f=[]}G.l=false;render()}
async function LC(){try{G.c=await A({action:'compare',intent:S.intent,limit:20});BACKEND.ok=true}catch(e){G.c=null}metrics();let a=document.querySelector('.techPane.active');if(a)renderTech(a.id.replace('tech-',''))}
async function LM(){try{G.m=await A({action:'meta'});BACKEND.ok=true}catch(e){BACKEND.ok=false}}
async function LB(){try{G.b=await A({action:'benchmark',limit:20});BACKEND.ok=true}catch(e){G.b=null;BACKEND.ok=false}return G.b}

function ff(){let a=G.f,q=G.q.trim().toLocaleLowerCase('tr-TR');if(G.tab==='media')a=a.filter(p=>MEDIA_CATS.has(p.kategori));if(q)a=a.filter(p=>(p.metin+' '+p.yazar+' '+p.kategori_adi).toLocaleLowerCase('tr-TR').includes(q.replace(/^#/,'')));return a}
function pc(p){let fit=S.intent&&S.mode==='pusula'?Math.round(p.fit*100)+'% niyet uyumu':'';let id=E(p.id);return `<article class="post"><div class="postInner"><div class="avatar ${AC(p.id)}">${E(p.initials)}</div><div class="postMain"><div class="head"><span class="name">${E(p.yazar)}</span><span class="handle">· ${E(p.kategori_adi)}</span><button class="moreBtn" onclick="toast('Gönderi ${id}')">${svg('more')}</button></div><div class="postText">${E(p.metin)}</div><div class="postMeta">${fit?`<span class="fitTag">${fit}</span>`:''}<button class="why" onclick="reason('${id}')">Neden bunu görüyorum?</button></div><div class="reason" id="r${id}"><b>${E(why(p))}</b><div class="raw">sıra #${p.rank} · skor ${F(p.score)} · uyum ${F(p.fit)} · kalite ${F(p.quality)} · tazelik ${F(p.tazelik)} · etkileşim ${F(p.etkilesim_puani)} · clickbait ${F(p.clickbait)}</div></div><div class="postActions"><button class="act" onclick="this.classList.toggle('on')">${svg('comment')}<span>Yanıtla</span></button><button class="act" onclick="this.classList.toggle('on')">${svg('repeat')}<span>Paylaş</span></button><button class="act" onclick="this.classList.toggle('on');this.querySelector('span').textContent=this.classList.contains('on')?'Beğenildi':'Beğen'">${svg('heart')}<span>Beğen</span></button><button class="act" onclick="toast('Bağlantı kopyalandı · demo')">${svg('share')}</button></div></div></div></article>`}

function render(){
  document.getElementById('app').classList.toggle('jury',S.jury);
  document.getElementById('main').classList.toggle('pusula-on',!!S.intent&&S.mode==='pusula');
  document.getElementById('modeP').classList.toggle('active',S.mode==='pusula');
  document.getElementById('modeK').classList.toggle('active',S.mode==='classic');
  document.getElementById('juryLabel').textContent=S.jury?'Kullanıcı modu':'Jüri modu';
  let b=document.getElementById('pusulaBar');b.style.display=S.dismissed&&!S.intent?'none':'block';b.classList.toggle('active',!!S.intent);b.classList.toggle('compact',!!S.intent);
  document.getElementById('pusulaCta').textContent=S.intent?'Değiştir':'Yönünü seç';document.getElementById('dismissPusula').style.display=S.intent?'none':'grid';
  const count=G.src?.pool_size||G.m?.source?.pool_size||320;
  const candidate=G.src?.semantic_candidate||G.m?.source?.semantic_candidate||'V5';
  document.getElementById('pusulaSub').textContent=S.intent?`${I[S.intent].label} · Candidate ${candidate} ile offline etiketlenmiş ${count} gizlilik güvenli gönderi sıralanıyor.`:`PUSULA kapalı · ${count} gizlilik güvenli gönderi klasik demo sıralamasında.`;
  if(S.intent){document.getElementById('intentStatus').textContent=I[S.intent].label;UB()}
  let r=document.getElementById('posts');
  if(G.l){r.innerHTML='<div class="pageEmpty"><h2>PUSULA havuzu sıralanıyor</h2><p>Candidate V5 offline etiketleri hazırlanıyor…</p></div>';metrics();return}
  if(G.e){r.innerHTML=`<div class="pageEmpty"><h2>Akış yüklenemedi</h2><p>${E(G.e)}.</p><button class="simpleBack" onclick="LF()">Tekrar dene</button></div>`;return}
  let a=ff();r.innerHTML=(a.length?a.map(pc).join(''):'<div class="pageEmpty"><h2>Sonuç yok</h2><p>Arama veya sekmeyi değiştir.</p></div>')+(!G.q&&G.tab==='feed'&&G.n<50?'<div style="padding:16px;text-align:center"><button class="simpleBack" onclick="G.n=Math.min(50,G.n+10);LF()">Daha fazla göster</button></div>':'');metrics()
}

function why(p){if(!S.intent)return`Klasik demo sıralamasında #${p.rank}. Etkileşim ve tazelik sentetik test sinyalidir; skor ${F(p.score)}.`;if(S.mode==='classic')return`Klasik sıralama açık; ${I[S.intent].label} niyeti skora dahil değil. Skor ${F(p.score)}.`;return`${I[S.intent].label} niyetinle %${Math.round(p.fit*100)} uyumlu. Tazelik ve etkileşim demo sinyali olarak %15'er; kalite çarpanı ${F(p.quality)}.`}
function UB(){let e=document.getElementById('budgetStatus');if(!S.budget){e.textContent='Sınırsız';document.querySelector('.progressTrack i').style.width='0%';return}let x=Math.floor((Date.now()-G.st)/1000),t=S.budget*60,z=Math.max(0,t-x);e.textContent=Math.floor(z/60)+':'+String(z%60).padStart(2,'0');document.querySelector('.progressTrack i').style.width=Math.min(100,x/t*100)+'%';if(!z&&!G.end){G.end=1;showSession()}}
function clock(){clearInterval(G.tm);G.st=Date.now();G.end=0;UB();if(S.budget)G.tm=setInterval(UB,1000)}
function clearIntent(){clearInterval(G.tm);S.intent=null;S.budget=0;S.modalIntent=null;S.dismissed=false;S.mode='classic';G.c=null;document.getElementById('intentModal').classList.remove('show');LF('classic');toast('Standart demo akışı')}
async function applyIntent(){if(!S.modalIntent)return toast('Önce bir yön seç');S.intent=S.modalIntent;S.budget=S.modalBudget;S.mode='pusula';S.dismissed=false;document.getElementById('intentModal').classList.remove('show');clock();toast(`${I[S.intent].label} · ${S.budget?S.budget+' dk':'sınırsız'}`);await LF('pusula')}
async function setMode(m){if(m==='pusula'&&!S.intent){S.mode='classic';render();return toast('Önce bir yön seç')}S.mode=m;await LF(m);toast(m==='classic'?'Klasik sıralama':'PUSULA sıralaması')}

function metrics(){
  let b=document.getElementById('metrics');
  if(!S.intent)return b.innerHTML='<div class="juryMetricEmpty">Karşılaştırma için bir niyet seç.</div>';
  if(!G.c)return b.innerHTML='<div class="juryMetricEmpty">Karşılaştırma hesaplanıyor…</div>';
  const a=G.c.classic.metrics,p=G.c.pusula.metrics;
  const nf=new Intl.NumberFormat('tr-TR',{minimumFractionDigits:1,maximumFractionDigits:1});
  const pct=v=>nf.format(Number(v||0)*100)+'%';
  const diff=(x,y)=>{
    const d=(Number(y||0)-Number(x||0))*100;
    return (d>0?'+':d<0?'−':'')+nf.format(Math.abs(d))+' puan';
  };
  const row=(name,x,y,lowerBetter=false)=>{
    const d=Number(y||0)-Number(x||0),good=lowerBetter?d<=0:d>=0;
    return `<div class="metric"><span>${name}</span><b>${pct(x)}</b><b class="p">${pct(y)}</b><b class="${good?'deltaGood':'deltaBad'}">${diff(x,y)}</b></div>`;
  };
  const budget=S.budget?S.budget+' dk':'Sınırsız';
  b.innerHTML=`<div class="juryMetricContext"><b>${E(I[S.intent].label)} · ${budget}</b></div><div class="metric metricHead"><span></span><b>Klasik</b><b class="p">PUSULA</b><b>Fark</b></div>`
    +row('Niyet benzerliği',a.niyet_uyumu,p.niyet_uyumu)
    +row('Niyet-kalite skoru',a.niyet_kalite,p.niyet_kalite)
    +row('Clickbait ortalaması ↓',a.clickbait_ortalama,p.clickbait_ortalama,true)
}

function showSession(s='pause'){let o=document.getElementById('sessionModal'),c=document.getElementById('session');o.classList.add('show');if(s==='pause')c.innerHTML=`<h2>${S.budget?'Zaman bütçen tamamlandı.':'Oturumu bitirmek ister misin?'}</h2><p>Akış zorla kapanmıyor. Bu oturumda ${G.f.length} demo gönderisi getirildi.</p><div class="stats"><div class="stat"><b>${G.f.length}</b><span>gönderi</span></div><div class="stat"><b>${S.intent?I[S.intent].short:'—'}</b><span>niyet</span></div><div class="stat"><b>${S.budget?S.budget+' dk':'∞'}</b><span>bütçe</span></div></div><div class="modalFooter"><button class="secondary" onclick="sessionModal.classList.remove('show')">Devam et</button><button class="primary" onclick="showSession('mood')">Bitir</button></div>`;else if(s==='mood')c.innerHTML='<h2>Bu oturum amacına ulaştı mı?</h2><p>Mevcut demoda geri bildirim henüz sıralamayı çevrimiçi eğitmiyor.</p><div class="moods"><button class="mood" onclick="pick(3,this)">😊</button><button class="mood" onclick="pick(2,this)">😐</button><button class="mood" onclick="pick(1,this)">😞</button></div><div class="modalFooter"><button class="primary" onclick="showSession(\'summary\')">Özeti gör</button></div>';else c.innerHTML=`<h2>Oturum özeti</h2><div class="stats"><div class="stat"><b>${S.intent?I[S.intent].label:'Standart'}</b><span>niyet</span></div><div class="stat"><b>${G.f.length}</b><span>gönderi</span></div><div class="stat"><b>${G.fm?Math.round(G.fm.niyet_uyumu*100)+'%':'—'}</b><span>uyum</span></div></div><div class="modalFooter"><button class="primary" onclick="newSession()">Yeni oturum</button></div>`}
function newSession(){clearInterval(G.tm);S.intent=null;S.budget=0;S.mode='classic';G.c=null;document.getElementById('sessionModal').classList.remove('show');LF('classic')}
function switchTab(t){G.tab=t;tabFeed.classList.toggle('active',t==='feed');tabMedia.classList.toggle('active',t==='media');render()}
function searchFeed(q){G.q=q;render()}
function selectTrend(t){searchInput.value=t;G.q=t;render()}
function composerTool(k){toast(k+' · demo')}
function toggleTheme(){toast('Final demo koyu temada')}
function openPage(p,b){document.querySelectorAll('.navBtn[data-page]').forEach(x=>x.classList.remove('active'));if(b)b.classList.add('active');toast(({home:'Ana Sayfa',notifications:'Bildirimler',messages:'Mesajlar',explore:'Keşfet',game:'Nod Oyna',communities:'Topluluklar',saved:'Kaydedilenler',likes:'Beğeniler',settings:'Ayarlar',profile:'Profil'})[p]||p)}

function syncTechChrome(){}
function techTab(name,btn){
  document.querySelectorAll('.techPane').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.techTab').forEach(x=>x.classList.remove('active'));
  const pane=document.getElementById('tech-'+name);if(pane)pane.classList.add('active');if(btn)btn.classList.add('active');
  const meta=TECH_META_V5[name]||TECH_META_V5.overview;
  document.getElementById('techTitle').textContent=meta[0];document.getElementById('techSub').textContent=meta[1];
  syncTechChrome();
  if(name==='experiment'&&!G.b){techExperiment();LB().then(()=>techExperiment());return}
  renderTech(name)
}
async function syncBackend(){await LM();if(S.intent)await LC();if(matchMedia('(max-width:720px)').matches&&!G.b)await LB();syncTechChrome();renderTech(document.querySelector('.techPane.active')?.id?.replace('tech-','')||'overview')}
function sourceStatus(){return ''}
function techOverview(){
  const r=document.getElementById('tech-overview');if(!r)return;
  const meta=G.m?.runtime_meta,src=G.m?.source;
  const click=meta?.clickbait||{};
  const active=G.c?.pusula?.metrics,classic=G.c?.classic?.metrics;
  const delta=active&&classic?active.niyet_uyumu-classic.niyet_uyumu:null;
  const nf=new Intl.NumberFormat('tr-TR',{minimumFractionDigits:1,maximumFractionDigits:1});
  const pct=v=>nf.format(Number(v||0)*100)+'%';
  const point=v=>(Number(v||0)>=0?'+':'−')+nf.format(Math.abs(Number(v||0))*100)+' puan';
  r.innerHTML=`<div class="techGrid overviewGrid">
    <div class="techCard span4 overviewStat techStatCard"><div class="miniLabel techStatLabel">Semantik model</div><div class="modelName techStatValue">${E((src?.semantic_encoder||'intfloat/multilingual-e5-base').split('/').pop())}</div><div class="overviewCardNote techStatNote">Gönderilerin anlamını ve seçilen niyetle benzerliğini ölçer.</div></div>
    <div class="techCard span4 overviewStat techStatCard"><div class="miniLabel techStatLabel">İçerik havuzu</div><div class="bigNum techStatValue">${src?.pool_size||320}</div><div class="overviewCardNote techStatNote">Sıralamada kullanılan gönderi havuzu.</div></div>
    <div class="techCard span4 overviewStat techStatCard"><div class="miniLabel techStatLabel">Clickbait ortalaması</div><div class="bigNum techStatValue">${pct(click.mean)}</div><div class="overviewCardNote techStatNote">İçeriklerin ortalama clickbait riski.</div></div>

    <div class="techCard span8 overviewRanking"><h3>Sıralama modeli</h3><div class="formulaBox overviewFormula">Skor = (<b>0.70 × niyet uyumu</b> + 0.15 × tazelik + 0.15 × etkileşim) × <b>(1 − clickbait)</b></div><div class="overviewSignals"><div><b>Niyet uyumu</b><span>Kullanıcı ne istiyor?</span></div><div><b>Tazelik</b><span>İçerik hâlâ güncel mi?</span></div><div><b>Etkileşim</b><span>İçerik insanlar için ilgi çekici mi?</span></div><div><b>Clickbait</b><span>İçeriği yukarı taşımak kaliteli bir tercih mi?</span></div></div></div>
    <div class="techCard span4 overviewIntent"><h3>${S.intent?'Aktif niyet · '+E(I[S.intent].label):'Aktif niyet'}</h3>${delta===null?'<div class="overviewExplain">Niyet seçildiğinde Klasik ve PUSULA sonucu burada karşılaştırılır.</div>':`<div class="calcLine"><span>Klasik niyet benzerliği</span><strong>${pct(classic.niyet_uyumu)}</strong></div><div class="calcLine"><span>PUSULA niyet benzerliği</span><strong>${pct(active.niyet_uyumu)}</strong></div><div class="calcLine"><span>Fark</span><strong class="deltaGood">${point(delta)}</strong></div>`}</div>

    <div class="techCard span12 overviewChain"><h3>Veri zinciri</h3><div class="overviewFlow">
      <div class="flowNode"><b>Gönderi</b><span>Metni al</span></div><div class="arrow" aria-hidden="true">→</div>
      <div class="flowNode"><b>Semantik model</b><span>Anlamını çıkar</span></div><div class="arrow" aria-hidden="true">→</div>
      <div class="flowNode"><b>Niyet uyumu</b><span>Niyetle karşılaştır</span></div><div class="arrow" aria-hidden="true">→</div>
      <div class="flowNode"><b>Clickbait kontrolü</b><span>Kaliteyi kontrol et</span></div><div class="arrow" aria-hidden="true">→</div>
      <div class="flowNode"><b>Sıralama</b><span>Akışı sırala</span></div>
    </div></div>
  </div>`
}
function techModels(){
  const r=document.getElementById('tech-models');if(!r)return;
  const rows=[
    {name:'multilingual-e5-base',acc:.688,f1:.688,mae:.173,selected:true},
    {name:'mDeBERTa / NLI',acc:.375,f1:.324,mae:.354},
    {name:'Qwen2.5-0.5B-Instruct',acc:.250,f1:.100,mae:.381}
  ];
  const pct=v=>new Intl.NumberFormat('tr-TR',{minimumFractionDigits:1,maximumFractionDigits:1}).format(v*100)+'%';
  r.innerHTML=`<div class="techGrid"><div class="techCard span12"><h3>Semantik aday karşılaştırması</h3><div class="sub">Aynı development seti · ortak metrikler</div><div style="overflow:auto"><table class="expTable modelTable"><thead><tr><th>Model</th><th>Baskın niyet doğruluğu</th><th>Macro-F1</th><th>4D MAE ↓</th></tr></thead><tbody>${rows.map(x=>`<tr class="${x.selected?'avg':''}"><td>${E(x.name)}${x.selected?' · seçilen':''}</td><td>${pct(x.acc)}</td><td>${x.f1.toFixed(3)}</td><td>${x.mae.toFixed(3)}</td></tr>`).join('')}</tbody></table></div><div class="modelDecision"><b>multilingual-e5-base seçildi</b><span>En yüksek doğruluk ve Macro-F1, en düşük 4D MAE.</span></div></div></div>`;
}
function techCompare(){let r=document.getElementById('tech-compare');if(!G.c)return r.innerHTML=sourceStatus()+'<div class="pageEmpty"><h2>Önce niyet seç</h2><p>Aynı Candidate V5 havuzu iki algoritmayla karşılaştırılacak.</p></div>';let C=(a,k)=>a.slice(0,5).map(p=>`<div class="feedMiniItem"><b>${p.rank}. ${E(p.yazar)}</b><span class="scorePill ${k?'k':''}">${F(p.score)}</span><p>${E(p.metin.slice(0,100))}</p></div>`).join('');r.innerHTML=sourceStatus()+`<div class="compareCols" style="margin-top:14px"><div class="feedMini"><div class="feedMiniHead">Klasik · aynı V5 havuzu</div>${C(G.c.classic.posts,1)}</div><div class="feedMini"><div class="feedMiniHead pusulaHead">PUSULA · aynı V5 havuzu</div>${C(G.c.pusula.posts,0)}</div></div><p class="techFootnote">İki kolon aynı 320 gönderiden gelir. Fark yalnız sıralama hedefidir; model runtime’da yeniden çalıştırılmaz.</p>`}
function techMath(){let r=document.getElementById('tech-math'),p=G.c?.pusula?.posts?.[0]||G.f[0];if(!p)return r.innerHTML=sourceStatus()+'<div class="pageEmpty"><h2>Önce akışı yükle</h2></div>';r.innerHTML=sourceStatus()+`<div class="techGrid"><div class="techCard span6"><h3>Gönderi ${E(p.id)}</h3><div class="sub">${E(p.yazar)} · ${E(p.kategori_adi)}</div><div class="vector">${p.tahmin_niyet.map((x,i)=>`<span class="vec">${['Ö','E','H','S'][i]} ${F(x)}</span>`).join('')}</div></div><div class="techCard span6"><h3>API skoru</h3><div class="calcLine"><span>Niyet uyumu</span><strong>${F(p.fit)}</strong></div><div class="calcLine"><span>Tazelik (demo)</span><strong>${F(p.tazelik)}</strong></div><div class="calcLine"><span>Etkileşim (demo)</span><strong>${F(p.etkilesim_puani)}</strong></div><div class="calcLine"><span>Clickbait</span><strong>${F(p.clickbait)}</strong></div><div class="calcLine"><span>Kalite = 1 − clickbait</span><strong>${F(p.quality)}</strong></div><div class="calcLine"><span>Nihai skor</span><strong>${F(p.score)}</strong></div></div><div class="techCard span12"><h3>Neden kalite çarpan?</h3><div class="formulaBox">yüksek uyum + yüksek etkileşim tek başına yeterli değil<br>nihai = taban × <b>kalite</b><br>clickbait yükseldikçe içerik skoru orantılı biçimde aşağı çekilir</div></div></div>`}
function techExperiment(){
  const r=document.getElementById('tech-experiment');if(!r)return;
  if(!G.b){r.innerHTML=sourceStatus()+'<div class="pageEmpty"><h2>Runtime davranış tablosu hesaplanıyor</h2><p>Aynı 320 gönderi, beş niyet ve top-20.</p></div>';return}
  const rows=(G.b.rows||[]).map(x=>`<tr><td>${E(x.intent_label)}</td><td>${F(x.classic.niyet_uyumu)}</td><td>${F(x.pusula.niyet_uyumu)}</td><td class="deltaGood">+${F(x.delta.niyet_uyumu)}</td><td>${F(x.classic.niyet_kalite)}</td><td>${F(x.pusula.niyet_kalite)}</td><td>${F(x.pusula.kalite)}</td><td>${F(x.pusula.clickbait_ortalama)}</td><td>${x.pusula.konu_sayisi}</td></tr>`).join('');
  r.innerHTML=sourceStatus()+`<div class="techGrid"><div class="techCard span12"><h3>Candidate V5 runtime davranış testi</h3><div class="sub">Aynı 320 gönderi · her niyette top-20 · aynı kategori başına en fazla 5 kuralı</div><div style="overflow:auto"><table class="expTable"><thead><tr><th>Niyet</th><th>Uyum K</th><th>Uyum P</th><th>Δ uyum</th><th>Niyet×kalite K</th><th>Niyet×kalite P</th><th>Kalite P</th><th>CB ort. P</th><th>Konu</th></tr></thead><tbody>${rows}</tbody></table></div><p class="techFootnote"><b>Bu tablo final doğruluk ölçümü değildir.</b> İnsan-gold bağımsız test yerine çalışan ranking davranışını gösterir. Etkileşim/tazelik deterministik demo sinyalidir.</p></div><div class="techCard span6"><h3>Semantic development sonuçları</h3><div class="calcLine"><span>Intent head</span><strong>k-NN · 352</strong></div><div class="calcLine"><span>Clickbait head</span><strong>Ridge α=0.05 · 192</strong></div><div class="calcLine"><span>Clickbait dev MAE</span><strong>0.101</strong></div><div class="calcLine"><span>Clickbait dev F1@.50</span><strong>0.968</strong></div><div class="calcLine"><span>5-fold OOF MAE</span><strong>0.138</strong></div><p class="techFootnote">Development setleri model seçimi için kullanıldı; yarışma/final insan-gold doğruluğu olarak sunulmamalı.</p></div><div class="techCard span6"><h3>Background sanity</h3><div class="calcLine"><span>Ortalama clickbait</span><strong>${F(G.m?.runtime_meta?.clickbait?.mean)}</strong></div><div class="calcLine"><span>Maksimum</span><strong>${F(G.m?.runtime_meta?.clickbait?.max)}</strong></div><div class="calcLine"><span>≥ 0.50</span><strong>${G.m?.runtime_meta?.clickbait?.ge_0_50??0} / 320</strong></div><div class="calcLine"><span>Cache reject</span><strong>0 / 320</strong></div></div></div>`
}
function techArchitecture(){
  const r=document.getElementById('tech-architecture');if(!r)return;
  r.innerHTML=sourceStatus()+`<div class="techGrid"><div class="techCard span12"><h3>Teknik zincir</h3><div class="flow"><div class="flowNode"><b>1 · Corpus</b><span>privacy-safe sentetik Türkçe feed</span></div><div class="arrow">→</div><div class="flowNode"><b>2 · E5 encoder</b><span>multilingual-e5-base · offline</span></div><div class="arrow">→</div><div class="flowNode"><b>3A · Niyet</b><span>4D k-NN · 352 örnek</span></div><div class="arrow">+</div><div class="flowNode"><b>3B · Clickbait</b><span>continuous Ridge · 192 örnek</span></div><div class="arrow">→</div><div class="flowNode"><b>4 · Cache</b><span>runtime model çağrısı yok</span></div><div class="arrow">→</div><div class="flowNode"><b>5 · Ranking</b><span>şeffaf formül + çeşitlilik</span></div></div></div><div class="techCard span6"><h3>Bugün gerçekten çalışan</h3><div class="limitList"><div class="limit"><i>✓</i><div><b>Candidate V5 semantic cache</b><span>320/320 kayıt, reject yok.</span></div><em>çalışıyor</em></div><div class="limit"><i>✓</i><div><b>Offline E5 semantic pipeline</b><span>Niyet ve clickbait ayrı head’lerde.</span></div><em>çalışıyor</em></div><div class="limit"><i>✓</i><div><b>Runtime ranking API</b><span>Model yüklemeden aynı cache’i sıralıyor.</span></div><em>çalışıyor</em></div><div class="limit"><i>✓</i><div><b>Açıklanabilir skor</b><span>Uyum, kalite, tazelik ve etkileşim kullanıcıya gösterilebilir.</span></div><em>çalışıyor</em></div></div></div><div class="techCard span6"><h3>Sınırlar / dürüst kapsam</h3><div class="limitList"><div class="limit"><i>!</i><div><b>Corpus sentetik</b><span>Gerçek kullanıcı postları kopyalanmadı; insan-gold bağımsız test hâlâ gerekli.</span></div><em>sınır</em></div><div class="limit"><i>!</i><div><b>Etkileşim ve tazelik simüle</b><span>NSosyal/X telemetrisi olarak raporlanmamalı.</span></div><em>sınır</em></div><div class="limit"><i>!</i><div><b>Online öğrenme yok</b><span>Oturum sonu geri bildirim prototipte modeli yeniden eğitmiyor.</span></div><em>Faz 3</em></div><div class="limit"><i>!</i><div><b>Final accuracy iddiası yok</b><span>Development benchmark ve runtime behavior testleri ayrı tutuluyor.</span></div><em>metodoloji</em></div></div></div></div>`
}

(async()=>{
  S.mode='classic';
  syncTechChrome();
  const sub=document.getElementById('pusulaSub');
  if(sub)sub.textContent='PUSULA kapalı · 320 gizlilik güvenli gönderi klasik demo sıralamasında.';
  await LM();
  await LF('classic');
})();