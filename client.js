function persistentId(key,prefix){
  try{
    let value=localStorage.getItem(key);
    if(!value){value=prefix+(globalThis.crypto?.randomUUID?globalThis.crypto.randomUUID():Date.now().toString(36)+Math.random().toString(36).slice(2));localStorage.setItem(key,value)}
    return value;
  }catch(e){return prefix+Date.now().toString(36)+Math.random().toString(36).slice(2)}
}
window.G={f:[],c:null,m:null,b:null,l:true,e:null,n:30,q:'',tab:'feed',tm:null,st:0,actor:persistentId('pusula_actor_id','anon_'),session:persistentId('pusula_session_id','session_')};
const E=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]||c));
const F=x=>Number(x||0).toFixed(3);
const AC=id=>['cyan','green','orange','pink'][Array.from(String(id)).reduce((s,c)=>s+c.codePointAt(0),0)%4];
const MEDIA_CATS=new Set(['kultur_sanat','oyun_espor','spor_futbol']);
const CATEGORY_FILTERS={all:'Tüm kategoriler',egitim_yks:'Eğitim',teknoloji_ai:'Yapay zekâ & teknoloji',teknofest_maker:'Teknoloji & maker',spor_futbol:'Spor',kultur_sanat:'Kültür & sanat',ekonomi_butce:'Ekonomi & bütçe',oyun_espor:'Oyun & e-spor',kampus_is:'Kampüs & iş',gundelik_yasam:'Gündelik yaşam',sosyal_sohbet:'Sosyal'};
const TECH_META_V5={
  overview:['Genel bakış','Sistemin çalışan teknik özeti.'],
  models:['Niyet analizi','PUSULA’nın içerikleri niyet uzayında nasıl temsil ettiğini ve model seçimini incele.'],
  compare:['Canlı karşılaştırma','Klasik sıralama ile PUSULA sıralamasını karşılaştır.'],
  math:['Matematik & skor ayrıştırma','Niyet uyumu, kalite, tazelik ve etkileşim sinyallerini adım adım gör.'],
  experiment:['Deney sonuçları','PUSULA’nın farklı niyetlerde klasik sıralamaya göre nasıl davrandığını incele.'],
  architecture:['Mimari & kapsam','PUSULA’nın içeriği nasıl analiz ettiğini ve kullanıcı niyetine göre akışı nasıl oluşturduğunu incele.'],
};

async function A(p){let r=await fetch('/api/pusula?'+new URLSearchParams({...p,viewer_id:G.actor}),{cache:'no-store'}),d=await r.json();if(!r.ok||!d.ok)throw Error(d.error||r.status);return d}
async function LF(m){G.l=true;if(G.f.length)render();try{let d=await A({action:'feed',intent:S.intent||'learn',category:S.category||'all',mode:m||(!S.intent?'classic':S.mode),limit:G.n});G.f=d.posts;G.src=d.source;G.fm=d.metrics;G.e=null;if(S.intent)LC()}catch(e){G.e=e.message;G.f=[]}G.l=false;render()}
async function LC(){try{G.c=await A({action:'compare',intent:S.intent,category:S.category||'all',limit:20});BACKEND.ok=true}catch(e){G.c=null}metrics();let a=document.querySelector('.techPane.active');if(a)renderTech(a.id.replace('tech-',''))}
async function LM(){try{G.m=await A({action:'meta'});BACKEND.ok=true}catch(e){BACKEND.ok=false}}
async function LB(){try{G.b=await A({action:'benchmark',limit:20});BACKEND.ok=true}catch(e){G.b=null;BACKEND.ok=false}return G.b}

function ff(){let a=G.f,q=G.q.trim().toLocaleLowerCase('tr-TR');if(G.tab==='media')a=a.filter(p=>MEDIA_CATS.has(p.kategori));if(q)a=a.filter(p=>(p.metin+' '+p.yazar+' '+p.kategori_adi).toLocaleLowerCase('tr-TR').includes(q.replace(/^#/,'')));return a}
function pc(p){
  let fit=S.intent&&S.mode==='pusula'?Math.round(p.fit*100)+'% niyet uyumu':'';
  let id=E(p.id);
  const verifiedSource=S.jury&&p.style==='verified_news'&&p.source_url
    ?`<a class="verifiedSource" href="${E(p.source_url)}" target="_blank" rel="noopener noreferrer" title="${E(p.source_name||'Kaynak')}">✓ Doğrulanmış kaynak</a>`
    :'';
  return `<article class="post" data-post-id="${id}"><div class="postInner"><div class="avatar ${AC(p.id)}">${E(p.initials)}</div><div class="postMain"><div class="head"><span class="name">${E(p.yazar)}</span><span class="handle">· ${E(p.kategori_adi)}</span><button class="moreBtn" onclick="toast('Gönderi ${id}')">${svg('more')}</button></div><div class="postText">${E(p.metin)}</div><div class="postMeta">${fit?`<span class="fitTag">${fit}</span>`:''}<button class="why" onclick="reason('${id}')">Neden bunu görüyorum?</button>${verifiedSource}</div><div class="reason" id="r${id}"><b>${E(why(p))}</b><div class="raw">sıra #${p.rank} · skor ${F(p.score)} · uyum ${F(p.fit)} · kalite ${F(p.quality)} · tazelik ${F(p.tazelik)} · etkileşim ${F(p.etkilesim_puani)} · clickbait ${F(p.clickbait)}</div></div><div class="postActions"><button class="act" aria-label="Yorum yap" onclick="toggleComment('${id}')">${svg('comment')}<span>${p.comment_count}</span></button><button class="act ${p.viewer_shared?'on':''}" aria-label="Yeniden paylaş" onclick="interact('${id}','share',this)">${svg('repeat')}<span>${p.share_count}</span></button><button class="act ${p.viewer_liked?'on liked':''}" aria-label="Beğen" onclick="interact('${id}','like',this)">${svg('heart')}<span>${p.like_count}</span></button><button class="act" aria-label="Bağlantıyı paylaş" onclick="copyPost('${id}')">${svg('share')}</button></div><div class="commentComposer" id="comment-${id}"><input maxlength="240" placeholder="Yorumunu yaz…" onkeydown="if(event.key==='Enter'){event.preventDefault();submitComment('${id}',this)}"><button onclick="submitComment('${id}',this.previousElementSibling)">Gönder</button></div></div></div></article>`
}

function updatePostScore(p){
  if(S.mode==='pusula'){
    p.base=.70*Number(p.fit||0)+.15*Number(p.tazelik||0)+.15*Number(p.etkilesim_puani||0);
    p.score=p.base*Number(p.quality||0);
  }else p.score=.70*Number(p.etkilesim_puani||0)+.20*Number(p.tazelik||0)+.10*(1-Number(p.clickbait||0));
}
async function interact(id,event,button,commentText=''){
  const p=G.f.find(x=>String(x.id)===String(id));
  if(!p||button?.disabled)return;
  const active=event==='like'?!p.viewer_liked:event==='share'?!p.viewer_shared:true;
  if(button)button.disabled=true;
  try{
    const r=await fetch('/api/posts?action=interact',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      id,event,active,actor_id:G.actor,session_id:G.session,intent:S.intent||'classic',mode:S.mode||'classic',rank:p.rank,comment:commentText
    })});
    const d=await r.json();
    if(!r.ok||!d.ok)throw Error(d.error||'Etkileşim kaydedilemedi');
    p.like_count=d.counts.like_count;p.comment_count=d.counts.comment_count;p.share_count=d.counts.share_count;
    p.viewer_liked=Boolean(d.viewer.liked);p.viewer_shared=Boolean(d.viewer.shared);p.viewer_comment_count=Number(d.viewer.comment_count||0);
    p.etkilesim_puani=Number(d.engagement_score||0);updatePostScore(p);render();
    toast(event==='like'?(p.viewer_liked?'Beğenildi':'Beğeni kaldırıldı'):event==='share'?(p.viewer_shared?'Yeniden paylaşıldı':'Paylaşım geri alındı'):'Yorum eklendi');return true;
  }catch(e){toast(e.message||'Etkileşim kaydedilemedi');if(button)button.disabled=false;return false}
}
function toggleComment(id){
  const box=document.getElementById('comment-'+id);if(!box)return;
  box.classList.toggle('show');if(box.classList.contains('show'))box.querySelector('input')?.focus();
}
async function submitComment(id,input){
  const text=String(input?.value||'').trim();if(!text)return toast('Yorumunu yaz');
  input.disabled=true;const saved=await interact(id,'comment',null,text);if(saved)input.value='';input.disabled=false;
}
async function copyPost(id){
  const url=location.origin+location.pathname+'#post-'+encodeURIComponent(id);
  try{await navigator.clipboard.writeText(url);toast('Bağlantı kopyalandı')}catch(e){toast('Bağlantı kopyalanamadı')}
}

function render(){
  document.getElementById('app').classList.toggle('jury',S.jury);
  document.getElementById('main').classList.toggle('pusula-on',!!S.intent&&S.mode==='pusula');
  document.getElementById('modeP').classList.toggle('active',S.mode==='pusula');
  document.getElementById('modeK').classList.toggle('active',S.mode==='classic');
  document.getElementById('juryLabel').textContent=S.jury?'Kullanıcı modu':'Jüri modu';
  let b=document.getElementById('pusulaBar');b.style.display=S.dismissed&&!S.intent?'none':'block';b.classList.toggle('active',!!S.intent);b.classList.toggle('compact',!!S.intent);
  document.getElementById('pusulaCta').textContent=S.intent?'Değiştir':'Yönünü seç';document.getElementById('dismissPusula').style.display=S.intent?'none':'grid';
  const count=G.src?.filtered_pool_size||G.src?.pool_size||G.m?.source?.pool_size||320;
  const candidate=G.src?.semantic_candidate||G.m?.source?.semantic_candidate||'V5';
  const categoryLabel=CATEGORY_FILTERS[S.category||'all']||CATEGORY_FILTERS.all;document.getElementById('pusulaSub').textContent=S.intent?`${I[S.intent].label} · ${categoryLabel} · ${count} gönderi içinden sıralanıyor.`:`PUSULA kapalı · ${count} gizlilik güvenli gönderi klasik demo sıralamasında.`;
  if(S.intent){document.getElementById('intentStatus').textContent=I[S.intent].label;UB()}
  let r=document.getElementById('posts');
  if(G.l){r.innerHTML='<div class="pageEmpty"><h2>PUSULA havuzu sıralanıyor</h2><p>Candidate V5 offline etiketleri hazırlanıyor…</p></div>';metrics();return}
  if(G.e){r.innerHTML=`<div class="pageEmpty"><h2>Akış yüklenemedi</h2><p>${E(G.e)}.</p><button class="simpleBack" onclick="LF()">Tekrar dene</button></div>`;return}
  let a=ff();r.innerHTML=(a.length?a.map(pc).join(''):'<div class="pageEmpty"><h2>Sonuç yok</h2><p>Arama veya sekmeyi değiştir.</p></div>')+(!G.q&&G.tab==='feed'&&G.n<50?'<div style="padding:16px;text-align:center"><button class="simpleBack" onclick="G.n=Math.min(50,G.n+10);LF()">Daha fazla göster</button></div>':'');metrics()
}

function why(p){const interaction=p.metadata_simulated?'Başlangıç etkileşimi simüle; kullanıcı hareketleri canlı güncellenir.':'Etkileşim canlı sayaçlardan hesaplanır.';if(!S.intent)return`Klasik sıralamada #${p.rank}. ${interaction} Skor ${F(p.score)}.`;if(S.mode==='classic')return`Klasik sıralama açık; ${I[S.intent].label} niyeti skora dahil değil. ${interaction} Skor ${F(p.score)}.`;return`${I[S.intent].label} niyetinle %${Math.round(p.fit*100)} uyumlu. ${interaction} Kalite çarpanı ${F(p.quality)}.`}
function UB(){let e=document.getElementById('budgetStatus');if(!S.budget){e.textContent='Sınırsız';document.querySelector('.progressTrack i').style.width='0%';return}let x=Math.floor((Date.now()-G.st)/1000),t=S.budget*60,z=Math.max(0,t-x);e.textContent=Math.floor(z/60)+':'+String(z%60).padStart(2,'0');document.querySelector('.progressTrack i').style.width=Math.min(100,x/t*100)+'%';if(!z&&!G.end){G.end=1;showSession()}}
function clock(){clearInterval(G.tm);G.st=Date.now();G.end=0;UB();if(S.budget)G.tm=setInterval(UB,1000)}
function clearIntent(){clearInterval(G.tm);S.intent=null;S.budget=0;S.modalIntent=null;S.category='all';S.modalCategory='all';S.dismissed=false;S.mode='classic';G.c=null;const category=document.getElementById('intentCategory');if(category)category.value='all';document.getElementById('intentModal').classList.remove('show');LF('classic');toast('Standart demo akışı')}
async function applyIntent(){if(!S.modalIntent)return toast('Önce bir yön seç');S.intent=S.modalIntent;S.budget=S.modalBudget;S.category=S.modalCategory||'all';S.mode='pusula';S.dismissed=false;document.getElementById('intentModal').classList.remove('show');clock();const category=CATEGORY_FILTERS[S.category]||CATEGORY_FILTERS.all;toast(`${I[S.intent].label} · ${category} · ${S.budget?S.budget+' dk':'sınırsız'}`);await LF('pusula')}
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
  const budget=S.budget?S.budget+' dk':'Sınırsız',category=CATEGORY_FILTERS[S.category||'all']||CATEGORY_FILTERS.all;
  b.innerHTML=`<div class="juryMetricContext"><b>${E(I[S.intent].label)} · ${E(category)} · ${budget}</b></div><div class="metric metricHead"><span></span><b>Klasik</b><b class="p">PUSULA</b><b>Fark</b></div>`
    +row('Niyet benzerliği',a.niyet_uyumu,p.niyet_uyumu)
    +row('Niyet-kalite skoru',a.niyet_kalite,p.niyet_kalite)
    +row('Clickbait ortalaması ↓',a.clickbait_ortalama,p.clickbait_ortalama,true)
}

function showSession(s='pause'){let o=document.getElementById('sessionModal'),c=document.getElementById('session');o.classList.add('show');if(s==='pause')c.innerHTML=`<h2>${S.budget?'Zaman bütçen tamamlandı.':'Oturumu bitirmek ister misin?'}</h2><p>Akış zorla kapanmıyor. Bu oturumda ${G.f.length} demo gönderisi getirildi.</p><div class="stats"><div class="stat"><b>${G.f.length}</b><span>gönderi</span></div><div class="stat"><b>${S.intent?I[S.intent].short:'—'}</b><span>niyet</span></div><div class="stat"><b>${S.budget?S.budget+' dk':'∞'}</b><span>bütçe</span></div></div><div class="modalFooter"><button class="secondary" onclick="sessionModal.classList.remove('show')">Devam et</button><button class="primary" onclick="showSession('mood')">Bitir</button></div>`;else if(s==='mood')c.innerHTML='<h2>Bu oturum amacına ulaştı mı?</h2><div class="moods"><button class="mood" onclick="pick(3,this)">😊</button><button class="mood" onclick="pick(2,this)">😐</button><button class="mood" onclick="pick(1,this)">😞</button></div><div class="modalFooter"><button class="primary" onclick="showSession(\'summary\')">Özeti gör</button></div>';else c.innerHTML=`<h2>Oturum özeti</h2><div class="stats"><div class="stat"><b>${S.intent?I[S.intent].label:'Standart'}</b><span>niyet</span></div><div class="stat"><b>${G.f.length}</b><span>gönderi</span></div><div class="stat"><b>${G.fm?Math.round(G.fm.niyet_uyumu*100)+'%':'—'}</b><span>uyum</span></div></div><div class="modalFooter"><button class="primary" onclick="newSession()">Yeni oturum</button></div>`}
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
  const nf=new Intl.NumberFormat('tr-TR',{minimumFractionDigits:1,maximumFractionDigits:1});
  const pct=v=>nf.format(Number(v||0)*100)+'%';
  r.innerHTML=`<div class="techGrid overviewGrid">
    <div class="techCard span4 overviewStat techStatCard"><div class="miniLabel techStatLabel">Semantik model</div><div class="modelName techStatValue">${E((src?.semantic_encoder||'intfloat/multilingual-e5-base').split('/').pop())}</div></div>
    <div class="techCard span4 overviewStat techStatCard"><div class="miniLabel techStatLabel">İçerik havuzu</div><div class="bigNum techStatValue">${src?.pool_size||320}</div></div>
    <div class="techCard span4 overviewStat techStatCard"><div class="miniLabel techStatLabel">Havuzda clickbait riski</div><div class="bigNum techStatValue">${pct(click.mean)}</div></div>

    <div class="techCard span12 overviewRanking"><h3>Sıralama modeli</h3><div class="formulaBox overviewFormula">Skor = (<b>0.70 × niyet uyumu</b> + 0.15 × tazelik + 0.15 × etkileşim) × <b>(1 − clickbait)</b></div><div class="overviewSignals"><div><i aria-hidden="true"></i><b>Niyet uyumu</b><span>Kullanıcı ne istiyor?</span></div><div><i aria-hidden="true"></i><b>Tazelik</b><span>İçerik hâlâ güncel mi?</span></div><div><i aria-hidden="true"></i><b>Etkileşim</b><span>İçerik insanlar için ilgi çekici mi?</span></div><div><i aria-hidden="true"></i><b>Clickbait</b><span>Kaliteli bir tercih mi?</span></div></div></div>

    <div class="techCard span12 overviewChain"><h3>Veri zinciri</h3><div class="overviewPipeline">
      <div class="pipelineMain">
        <div class="flowNode pipelineNode"><b>Gönderi</b><span>Metni al</span></div>
        <div class="arrow pipelineArrow" aria-hidden="true">→</div>
        <div class="flowNode pipelineNode"><b>Semantik analiz</b><span>Anlamını çıkar</span></div>
        <div class="arrow pipelineArrow" aria-hidden="true">→</div>
        <div class="pipelineSignalsBox">
          <div class="pipelineSignalsHead"><b>Sıralama sinyalleri</b></div>
          <div class="pipelineSignalsGrid">
            <div class="flowNode pipelineSignal"><b>Niyet uyumu</b></div>
            <div class="flowNode pipelineSignal"><b>Clickbait riski</b></div>
            <div class="flowNode pipelineSignal"><b>Tazelik</b></div>
            <div class="flowNode pipelineSignal"><b>Etkileşim</b></div>
          </div>
        </div>
        <div class="arrow pipelineArrow" aria-hidden="true">→</div>
        <div class="flowNode pipelineNode pipelineScore"><b>PUSULA skoru</b><span>Tüm sinyalleri birleştir</span></div>
        <div class="arrow pipelineArrow" aria-hidden="true">→</div>
        <div class="flowNode pipelineNode"><b>Akış</b><span>İçerikleri sırala</span></div>
      </div>
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
  r.innerHTML=`<div class="techGrid modelCompareGrid">
    <div class="techCard span12 modelSpaceCard">
      <h3>Niyet uzayı</h3>
      <div class="sub">Her gönderi dört boyutta temsil edilir; seçilen niyet bu uzayda bir hedef oluşturur.</div>

      <div class="modelAxes">
        <span>Öğretici</span>
        <span>Eğlendirici</span>
        <span>Haber</span>
        <span>Sosyal</span>
      </div>

      <div class="modelExamplesLabel">Örnek hedefler</div>
      <div class="modelIntentRows">
        <div class="modelIntentRow">
          <b>Öğrenmek</b>
          <small>Belirgin hedef</small>
          <code>[1.00, 0.15, 0.15, 0.05]</code>
          <span>Öğretici boyut baskındır; diğer boyutlar tamamen sıfırlanmaz.</span>
        </div>
        <div class="modelIntentRow">
          <b>Sadece dolaşmak</b>
          <small>Dengeli hedef</small>
          <code>[0.40, 0.55, 0.40, 0.45]</code>
          <span>Tek bir boyutu baskınlaştırmaz; dört boyuta daha dengeli yaklaşır.</span>
        </div>
      </div>

      <div class="modelMetricBox">
        <div class="modelMetricList">
          <div><i></i><b>Niyet doğruluğu ↑</b><span>Baskın niyeti doğru buluyor mu?</span></div>
          <div><i></i><b>Macro-F1 ↑</b><span>Tüm niyetlerde dengeli başarı gösteriyor mu?</span></div>
          <div><i></i><b>Niyet vektörü hatası ↓</b><span>Dört boyutlu profil hedefe ne kadar yakın?</span></div>
        </div>
      </div>
    </div>

    <div class="techCard span12">
      <h3>Niyet analizi için model seçimi</h3>
      <div class="sub">Aynı değerlendirme koşullarında üç model karşılaştırıldı.</div>
      <div style="overflow:auto"><table class="expTable modelTable"><thead><tr><th>Model</th><th>Niyet doğruluğu ↑</th><th>Macro-F1 ↑</th><th>Niyet vektörü hatası ↓</th></tr></thead><tbody>${rows.map(x=>`<tr class="${x.selected?'avg':''}"><td>${E(x.name)}${x.selected?' · seçilen':''}</td><td>${pct(x.acc)}</td><td>${x.f1.toFixed(3)}</td><td>${x.mae.toFixed(3)}</td></tr>`).join('')}</tbody></table></div>
    </div>
  </div>`;
}
function techCompare(){let r=document.getElementById('tech-compare');if(!G.c)return r.innerHTML=sourceStatus()+'<div class="pageEmpty"><h2>Önce niyet seç</h2><p>Bir niyet seçildiğinde Klasik ve PUSULA sıralaması aynı içerik havuzunda karşılaştırılır.</p></div>';let C=a=>a.slice(0,5).map(p=>`<div class="feedMiniItem"><b>${p.rank}. ${E(p.yazar)}</b><p>${E(p.metin.slice(0,100))}</p></div>`).join('');const intent=I[S.intent]?.label||'Seçilmedi';r.innerHTML=sourceStatus()+`<div class="compareIntent"><span>Aktif niyet</span><b>${E(intent)}</b></div><div class="compareCols"><div class="feedMini"><div class="feedMiniHead">Klasik sıralama</div>${C(G.c.classic.posts)}</div><div class="feedMini"><div class="feedMiniHead pusulaHead">PUSULA sıralaması</div>${C(G.c.pusula.posts)}</div></div>`}
function techMath(){let r=document.getElementById('tech-math'),p=G.c?.pusula?.posts?.[0]||G.f[0];if(!p)return r.innerHTML=sourceStatus()+'<div class="pageEmpty"><h2>Önce akışı yükle</h2></div>';r.innerHTML=sourceStatus()+`<div class="techGrid"><div class="techCard span6"><h3>Gönderi ${E(p.id)}</h3><div class="sub">${E(p.yazar)} · ${E(p.kategori_adi)}</div><div class="vector">${p.tahmin_niyet.map((x,i)=>`<span class="vec">${['Ö','E','H','S'][i]} ${F(x)}</span>`).join('')}</div></div><div class="techCard span6"><h3>API skoru</h3><div class="calcLine"><span>Niyet uyumu</span><strong>${F(p.fit)}</strong></div><div class="calcLine"><span>Tazelik (demo)</span><strong>${F(p.tazelik)}</strong></div><div class="calcLine"><span>Etkileşim (demo)</span><strong>${F(p.etkilesim_puani)}</strong></div><div class="calcLine"><span>Clickbait</span><strong>${F(p.clickbait)}</strong></div><div class="calcLine"><span>Kalite = 1 − clickbait</span><strong>${F(p.quality)}</strong></div><div class="calcLine"><span>Nihai skor</span><strong>${F(p.score)}</strong></div></div><div class="techCard span12"><h3>Neden kalite çarpan?</h3><div class="formulaBox">yüksek uyum + yüksek etkileşim tek başına yeterli değil<br>nihai = taban × <b>kalite</b><br>clickbait yükseldikçe içerik skoru orantılı biçimde aşağı çekilir</div></div></div>`}
function techExperiment(){
  const r=document.getElementById('tech-experiment');if(!r)return;
  if(!G.b){r.innerHTML=sourceStatus()+'<div class="pageEmpty"><h2>Deney sonuçları hazırlanıyor</h2><p>Beş niyet için Klasik ve PUSULA sıralaması karşılaştırılıyor.</p></div>';return}
  const data=G.b.rows||[];
  const nf=new Intl.NumberFormat('tr-TR',{minimumFractionDigits:1,maximumFractionDigits:1});
  const pct=v=>nf.format(Number(v||0)*100)+'%';
  const point=v=>'+'+nf.format(Number(v||0)*100)+' puan';
  const avg=a=>a.length?a.reduce((s,v)=>s+Number(v||0),0)/a.length:0;
  const rows=data.map(x=>`<tr><td>${E(x.intent_label)}</td><td>${pct(x.classic.niyet_uyumu)}</td><td><b>${pct(x.pusula.niyet_uyumu)}</b></td><td class="deltaGood">${point(x.delta.niyet_uyumu)}</td></tr>`).join('');
  const avgDelta=avg(data.map(x=>x.delta.niyet_uyumu));
  const classicClick=avg(data.map(x=>x.classic.clickbait_ortalama));
  const pusulaClick=avg(data.map(x=>x.pusula.clickbait_ortalama));
  const clickDelta=pusulaClick-classicClick;
  const topics=data.map(x=>Number(x.pusula.konu_sayisi||0)).filter(Boolean);
  const topicMin=topics.length?Math.min(...topics):0,topicMax=topics.length?Math.max(...topics):0;
  r.innerHTML=sourceStatus()+`<div class="techGrid experimentGrid">
    <div class="techCard span12 experimentMain">
      <h3>Niyet uyumu karşılaştırması</h3>
      <div class="sub">Her niyet için aynı 320 içeriklik havuzdan ilk 20 sonuç karşılaştırıldı.</div>
      <div class="experimentTableWrap"><table class="expTable experimentTable"><thead><tr><th>Niyet</th><th>Klasik</th><th>PUSULA</th><th>Değişim</th></tr></thead><tbody>${rows}</tbody></table></div>
    </div>

    <div class="techCard span12 experimentSummary">
      <h3>Sonuç özeti</h3>
      <div class="experimentSummaryGrid">
        <div class="experimentStat techStatCard">
          <div class="miniLabel techStatLabel">Ortalama niyet uyumu artışı</div>
          <div class="bigNum techStatValue experimentPositive">+${nf.format(avgDelta*100)} puan</div>
        </div>
        <div class="experimentStat techStatCard experimentStatDetail">
          <div class="miniLabel techStatLabel">Clickbait riski azalması</div>
          <div class="bigNum techStatValue experimentPositive">${nf.format(Math.abs(clickDelta)*100)} puan</div>
          <div class="experimentStatSub">Klasik ${pct(classicClick)} → PUSULA ${pct(pusulaClick)}</div>
        </div>
        <div class="experimentStat techStatCard">
          <div class="miniLabel techStatLabel">İlk 20'de kategori çeşitliliği</div>
          <div class="bigNum techStatValue">${topicMin}–${topicMax} / 10 kategori</div>
        </div>
      </div>
      <div class="experimentCategories"><b>Kategoriler:</b> Eğitim · Yapay zekâ & teknoloji · Teknoloji & maker · Spor · Kültür & sanat · Ekonomi & bütçe · Oyun & e-spor · Kampüs & iş · Gündelik yaşam · Sosyal</div>
    </div>
  </div>`
}
function techArchitecture(){
  const r=document.getElementById('tech-architecture');if(!r)return;
  r.innerHTML=sourceStatus()+`<div class="techGrid architectureGrid">
    <div class="techCard span12 architectureFlowCard">
      <h3>Sistem mimarisi</h3>

      <div class="architectureStage">
        <div class="architectureStageHead">
          <b>İçerik hazırlanırken</b>
          <span>Her gönderinin anlamı bir kez analiz edilir.</span>
        </div>
        <div class="architectureFlow">
          <div class="architectureNode"><b>Gönderi</b><span>İçerik metni</span></div>
          <div class="architectureArrow" aria-hidden="true">→</div>
          <div class="architectureNode"><b>Semantik analiz</b><span>Metnin anlamını çıkar</span></div>
          <div class="architectureArrow" aria-hidden="true">→</div>
          <div class="architectureNode architectureNodeWide"><b>Niyet profili + Clickbait riski</b><span>İçeriğin özelliklerini belirle</span></div>
          <div class="architectureArrow" aria-hidden="true">→</div>
          <div class="architectureNode"><b>Analiz sonuçları</b><span>Sıralama için saklanır</span></div>
        </div>
      </div>

      <div class="architectureStage">
        <div class="architectureStageHead">
          <b>Akış oluşturulurken</b>
          <span>Kullanıcının seçtiği niyet kayıtlı analiz sonuçlarıyla eşleştirilir.</span>
        </div>
        <div class="architectureFlow">
          <div class="architectureNode"><b>Kullanıcı niyeti</b><span>Örn. Öğrenmek</span></div>
          <div class="architectureArrow" aria-hidden="true">→</div>
          <div class="architectureNode"><b>Kayıtlı analiz sonuçları</b><span>Niyet, kalite ve diğer sinyaller</span></div>
          <div class="architectureArrow" aria-hidden="true">→</div>
          <div class="architectureNode"><b>PUSULA skoru</b><span>İçerikleri karşılaştır</span></div>
          <div class="architectureArrow" aria-hidden="true">→</div>
          <div class="architectureNode"><b>Sıralanmış akış</b><span>En uygun içerikleri göster</span></div>
        </div>
      </div>
    </div>

    <div class="techCard span7 architectureReady">
      <h3>Hazır ve çalışan</h3>
      <div class="architectureCheckList">
        <div><i>✓</i><span><b>320 içerik analiz edildi</b><small>Tüm demo havuzunun semantik özellikleri hazır.</small></span></div>
        <div><i>✓</i><span><b>Niyet analizi çalışıyor</b><small>İçerikler dört boyutlu niyet profiline dönüştürülüyor.</small></span></div>
        <div><i>✓</i><span><b>Clickbait analizi çalışıyor</b><small>Her içerik için clickbait riski bulunuyor.</small></span></div>
        <div><i>✓</i><span><b>Niyete göre sıralama çalışıyor</b><small>Seçilen niyete göre ilk içerikler yeniden sıralanıyor.</small></span></div>
      </div>
    </div>

    <div class="techCard span5 architectureScope">
      <h3>Demo kapsamı</h3>
      <div class="architectureScopeList">
        <div><i aria-hidden="true"></i><span><b>İçerik havuzu</b><small>Sentetik Türkçe gönderiler</small></span></div>
        <div><i aria-hidden="true"></i><span><b>Tazelik ve etkileşim</b><small>Demo verileriyle temsil ediliyor</small></span></div>
        <div><i aria-hidden="true"></i><span><b>Geri bildirimle öğrenme</b><small>Sonraki geliştirme aşaması</small></span></div>
      </div>
    </div>
  </div>`
}

(async()=>{
  S.mode='classic';
  syncTechChrome();
  const sub=document.getElementById('pusulaSub');
  if(sub)sub.textContent='PUSULA kapalı · 320 gizlilik güvenli gönderi klasik demo sıralamasında.';
  await LM();
  await LF('classic');
})();
