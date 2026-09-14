window.G={f:[],c:null,m:null,l:true,e:null,n:30,q:'',tab:'feed',tm:null,st:0};
const E=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const F=x=>Number(x||0).toFixed(3);
const AC=id=>['cyan','green','orange','pink'][Array.from(String(id)).reduce((s,c)=>s+c.codePointAt(0),0)%4];
const MEDIA_CATS=new Set(['kultur_sanat','oyun_espor','spor_futbol']);

async function A(p){let r=await fetch('/api/pusula?'+new URLSearchParams(p),{cache:'no-store'}),d=await r.json();if(!r.ok||!d.ok)throw Error(d.error||r.status);return d}
async function LF(m){G.l=true;if(G.f.length)render();try{let d=await A({action:'feed',intent:S.intent||'learn',mode:m||(!S.intent?'classic':S.mode),limit:G.n});G.f=d.posts;G.src=d.source;G.fm=d.metrics;G.e=null;if(S.intent)LC()}catch(e){G.e=e.message;G.f=[]}G.l=false;render()}
async function LC(){try{G.c=await A({action:'compare',intent:S.intent,limit:20});BACKEND.ok=true}catch(e){G.c=null}metrics();let a=document.querySelector('.techPane.active');if(a)renderTech(a.id.replace('tech-',''))}
async function LM(){try{G.m=await A({action:'meta'});BACKEND.ok=true}catch(e){BACKEND.ok=false}}

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
async function setMode(m){S.mode=m;await LF(m);toast(m==='classic'?'Klasik sıralama':'PUSULA sıralaması')}

function metrics(){
  let b=document.getElementById('metrics');
  const count=G.m?.source?.pool_size||320;
  if(!S.intent)return b.innerHTML=`<div class="judgeNote">Niyet seçildiğinde aynı ${count} Candidate V5 gönderisinin iki sıralaması karşılaştırılır. Etkileşim ve tazelik değerleri demo simülasyonudur.</div>`;
  if(!G.c)return b.innerHTML='<div class="judgeNote">İki akış hesaplanıyor…</div>';
  let a=G.c.classic.metrics,p=G.c.pusula.metrics,R=(n,x,y)=>`<div class="metric"><span>${n}</span><b>${Math.round(Number(x||0)*100)}%</b><b class="p">${Math.round(Number(y||0)*100)}%</b></div>`;
  b.innerHTML='<div class="metric"><span></span><b>Klasik</b><b class="p">PUSULA</b></div>'+R('Niyet uyumu',a.niyet_uyumu,p.niyet_uyumu)+R('Niyet × kalite',a.niyet_kalite,p.niyet_kalite)+R('Ortalama kalite',a.kalite,p.kalite)+R('Clickbait ort.',a.clickbait_ortalama,p.clickbait_ortalama)+R('Etkileşim (demo)',a.etkilesim,p.etkilesim)
}

function showSession(s='pause'){let o=document.getElementById('sessionModal'),c=document.getElementById('session');o.classList.add('show');if(s==='pause')c.innerHTML=`<h2>${S.budget?'Zaman bütçen tamamlandı.':'Oturumu bitirmek ister misin?'}</h2><p>Akış zorla kapanmıyor. Bu oturumda ${G.f.length} demo gönderisi getirildi.</p><div class="stats"><div class="stat"><b>${G.f.length}</b><span>gönderi</span></div><div class="stat"><b>${S.intent?I[S.intent].short:'—'}</b><span>niyet</span></div><div class="stat"><b>${S.budget?S.budget+' dk':'∞'}</b><span>bütçe</span></div></div><div class="modalFooter"><button class="secondary" onclick="sessionModal.classList.remove('show')">Devam et</button><button class="primary" onclick="showSession('mood')">Bitir</button></div>`;else if(s==='mood')c.innerHTML='<h2>Bu oturum amacına ulaştı mı?</h2><p>Mevcut demoda geri bildirim henüz sıralamayı çevrimiçi eğitmiyor.</p><div class="moods"><button class="mood" onclick="pick(3,this)">😊</button><button class="mood" onclick="pick(2,this)">😐</button><button class="mood" onclick="pick(1,this)">😞</button></div><div class="modalFooter"><button class="primary" onclick="showSession(\'summary\')">Özeti gör</button></div>';else c.innerHTML=`<h2>Oturum özeti</h2><div class="stats"><div class="stat"><b>${S.intent?I[S.intent].label:'Standart'}</b><span>niyet</span></div><div class="stat"><b>${G.f.length}</b><span>gönderi</span></div><div class="stat"><b>${G.fm?Math.round(G.fm.niyet_uyumu*100)+'%':'—'}</b><span>uyum</span></div></div><div class="modalFooter"><button class="primary" onclick="newSession()">Yeni oturum</button></div>`}
function newSession(){clearInterval(G.tm);S.intent=null;S.budget=0;S.mode='classic';G.c=null;document.getElementById('sessionModal').classList.remove('show');LF('classic')}
function switchTab(t){G.tab=t;tabFeed.classList.toggle('active',t==='feed');tabMedia.classList.toggle('active',t==='media');render()}
function searchFeed(q){G.q=q;render()}
function selectTrend(t){searchInput.value=t;G.q=t;render()}
function composerTool(k){toast(k+' · demo')}
function toggleTheme(){toast('Final demo koyu temada')}
function openPage(p,b){document.querySelectorAll('.navBtn[data-page]').forEach(x=>x.classList.remove('active'));if(b)b.classList.add('active');toast(({home:'Ana Sayfa',notifications:'Bildirimler',messages:'Mesajlar',explore:'Keşfet',game:'Nod Oyna',communities:'Topluluklar',saved:'Kaydedilenler',likes:'Beğeniler',settings:'Ayarlar',profile:'Profil'})[p]||p)}

async function syncBackend(){await LM();if(S.intent)await LC();renderTech(document.querySelector('.techPane.active')?.id?.replace('tech-','')||'overview')}
function sourceStatus(){let c=G.m?.source?.pool_size||320,v=G.m?.source?.semantic_candidate||'V5';return `<span class="sourceBadge">${c} gizlilik güvenli gönderi</span> <span class="backendStatus"><i class="statusDot"></i>Vercel API + Candidate ${E(v)} offline cache</span>`}
function techCompare(){let r=document.getElementById('tech-compare');if(!G.c)return r.innerHTML=sourceStatus()+'<div class="pageEmpty"><h2>Önce niyet seç</h2></div>';let C=(a,k)=>a.slice(0,5).map(p=>`<div class="feedMiniItem"><b>${p.rank}. ${E(p.yazar)}</b><span class="scorePill ${k?'k':''}">${F(p.score)}</span><p>${E(p.metin.slice(0,100))}</p></div>`).join('');r.innerHTML=sourceStatus()+`<div class="compareCols" style="margin-top:14px"><div class="feedMini"><div class="feedMiniHead">Klasik · aynı V5 havuzu</div>${C(G.c.classic.posts,1)}</div><div class="feedMini"><div class="feedMiniHead" style="color:#8fd9ff">PUSULA · aynı V5 havuzu</div>${C(G.c.pusula.posts,0)}</div></div>`}
function techMath(){let r=document.getElementById('tech-math'),p=G.c?.pusula?.posts?.[0]||G.f[0];if(!p)return;r.innerHTML=sourceStatus()+`<div class="techGrid"><div class="techCard span6"><h3>Gönderi ${E(p.id)}</h3><div class="sub">${E(p.yazar)} · ${E(p.kategori_adi)}</div><div class="vector">${p.tahmin_niyet.map((x,i)=>`<span class="vec">${['Ö','E','H','S'][i]} ${F(x)}</span>`).join('')}</div></div><div class="techCard span6"><h3>API skoru</h3><div class="calcLine"><span>Niyet uyumu</span><strong>${F(p.fit)}</strong></div><div class="calcLine"><span>Tazelik (demo)</span><strong>${F(p.tazelik)}</strong></div><div class="calcLine"><span>Etkileşim (demo)</span><strong>${F(p.etkilesim_puani)}</strong></div><div class="calcLine"><span>Kalite</span><strong>${F(p.quality)}</strong></div><div class="calcLine"><span>Nihai skor</span><strong>${F(p.score)}</strong></div></div></div>`}

(async()=>{await LM();await LF('classic')})();
