const RAW_POOL = 'https://raw.githubusercontent.com/asimonmsz-design/pusula/main/kod/veri/etiketli_havuz.json';

const INTENTS = {
  ogrenmek: [1.00, 0.15, 0.15, 0.05],
  eglenmek: [0.10, 1.00, 0.05, 0.25],
  haberdar: [0.20, 0.05, 1.00, 0.10],
  sosyallesmek: [0.10, 0.30, 0.05, 1.00],
  dolasmak: [0.40, 0.55, 0.40, 0.45],
};
const INTENT_LABELS = {
  ogrenmek: 'Öğrenmek', eglenmek: 'Eğlenmek', haberdar: 'Haberdar olmak',
  sosyallesmek: 'Sosyalleşmek', dolasmak: 'Sadece dolaşmak',
};
const ALIASES = {
  learn:'ogrenmek', ogrenmek:'ogrenmek', öğrenmek:'ogrenmek',
  fun:'eglenmek', eglenmek:'eglenmek', eğlenmek:'eglenmek',
  news:'haberdar', haberdar:'haberdar', haberdar_olmak:'haberdar',
  social:'sosyallesmek', sosyallesmek:'sosyallesmek', sosyalleşmek:'sosyallesmek',
  wander:'dolasmak', dolasmak:'dolasmak', dolaşmak:'dolasmak',
};
const CATEGORY_LABELS = {
  egitim_anlatim:'Eğitim', egitim_uygulama:'Eğitim', bilim_teknoloji:'Bilim & teknoloji',
  haber_gundem:'Gündem', haber_duyuru:'Gündem', eglence_video:'Eğlence', mizah:'Mizah',
  arkadas_paylasimi:'Arkadaş paylaşımı', topluluk_soru:'Topluluk', sosyal_sohbet:'Sosyal',
  clickbait_kiskirtici:'Clickbait / kışkırtıcı', clickbait_merak:'Clickbait / merak',
};
const SOURCE = { repo:'asimonmsz-design/pusula', path:'kod/veri/etiketli_havuz.json', pool_size:2000, ranking:'kod/siralama.py' };

let cache = { data:null, at:0 };
const CACHE_MS = 5 * 60 * 1000;

function canonicalIntent(v){ return ALIASES[String(v || 'learn').toLocaleLowerCase('tr-TR')] || 'ogrenmek'; }
function clamp(n,min,max){ return Math.max(min,Math.min(max,n)); }
function cosine(a=[],b=[]){ let dot=0,na=0,nb=0; for(let i=0;i<Math.min(a.length,b.length);i++){dot+=Number(a[i]||0)*Number(b[i]||0);na+=Number(a[i]||0)**2;nb+=Number(b[i]||0)**2;} return na&&nb?dot/(Math.sqrt(na)*Math.sqrt(nb)):0; }
function classicScore(p){ return .70*Number(p.etkilesim_puani||0)+.20*Number(p.tazelik||0)+.10*(1-Number(p.clickbait||0)); }
function pusulaParts(p,target){ const fit=cosine(p.tahmin_niyet,target), quality=1-Number(p.clickbait||0); const base=.70*fit+.15*Number(p.tazelik||0)+.15*Number(p.etkilesim_puani||0); return {fit,quality,base,score:base*quality}; }
function diverse(items, scoreFn, limit){
  const sorted=[...items].sort((a,b)=>scoreFn(b)-scoreFn(a)); const out=[], counts={};
  for(const p of sorted){ if(out.length>=limit)break; const k=p.kategori||'diger'; if((counts[k]||0)>=5)continue; out.push(p); counts[k]=(counts[k]||0)+1; }
  if(out.length<limit){ for(const p of sorted){ if(out.length>=limit)break; if(!out.includes(p))out.push(p); } }
  return out;
}
function initials(name=''){ const parts=String(name).trim().split(/\s+/).filter(Boolean); return (parts.length>1?parts[0][0]+parts[1][0]:(parts[0]||'?').slice(0,2)).toLocaleUpperCase('tr-TR'); }
function enrich(p, rank, intent, mode){
  const target=INTENTS[intent]; const parts=pusulaParts(p,target); const score=mode==='pusula'?parts.score:classicScore(p);
  return { id:p.id, rank, yazar:p.yazar, initials:initials(p.yazar), metin:p.metin, kategori:p.kategori,
    kategori_adi:CATEGORY_LABELS[p.kategori] || String(p.kategori||'Diğer').replaceAll('_',' '),
    tahmin_niyet:p.tahmin_niyet || [0,0,0,0], etkilesim_puani:Number(p.etkilesim_puani||0),
    pismanlik_olasiligi:Number(p.pismanlik_olasiligi||0), tazelik:Number(p.tazelik||0), clickbait:Number(p.clickbait||0),
    score, fit:parts.fit, quality:parts.quality, base:mode==='pusula'?parts.base:0 };
}
function metrics(posts,intent){
  if(!posts.length)return {niyet_uyumu:0,pismanlik:0,etkilesim:0,clickbait_orani:0,tatmin:0};
  const target=INTENTS[intent], n=posts.length;
  const fit=posts.reduce((s,p)=>s+cosine(p.tahmin_niyet,target),0)/n;
  const regret=posts.reduce((s,p)=>s+Number(p.pismanlik_olasiligi||0),0)/n;
  const engagement=posts.reduce((s,p)=>s+Number(p.etkilesim_puani||0),0)/n;
  const cb=posts.filter(p=>Number(p.clickbait||0)>.4).length/n;
  return {niyet_uyumu:fit,pismanlik:regret,etkilesim:engagement,clickbait_orani:cb,tatmin:fit*(1-regret)};
}
async function loadPool(){
  if(cache.data && Date.now()-cache.at<CACHE_MS)return cache.data;
  const ctrl=new AbortController(); const timer=setTimeout(()=>ctrl.abort(),8000);
  try{
    const r=await fetch(RAW_POOL,{headers:{'User-Agent':'PUSULA-Vercel-Demo'},signal:ctrl.signal,cache:'no-store'});
    if(!r.ok)throw new Error('GitHub '+r.status);
    const data=await r.json(); if(!Array.isArray(data))throw new Error('Geçersiz veri havuzu');
    cache={data,at:Date.now()}; SOURCE.pool_size=data.length; return data;
  } finally { clearTimeout(timer); }
}
function ranked(pool,intent,mode,limit){
  const target=INTENTS[intent]; const scoreFn=mode==='pusula'?(p)=>pusulaParts(p,target).score:classicScore;
  const selected=diverse(pool,scoreFn,limit); return selected.map((p,i)=>enrich(p,i+1,intent,mode));
}

module.exports = async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  res.setHeader('Access-Control-Allow-Origin','*');
  res.setHeader('Content-Type','application/json; charset=utf-8');
  if(req.method==='OPTIONS'){ res.statusCode=204; return res.end(); }
  try{
    const action=String(req.query?.action || 'meta');
    const intent=canonicalIntent(req.query?.intent);
    const limit=clamp(parseInt(req.query?.limit || '20',10)||20,1,50);
    if(action==='meta'){
      // Keep this lightweight but verify GitHub availability/pool size so the UI status is meaningful.
      try{ await loadPool(); }catch(_e){}
      return res.status(200).json({ok:true,source:SOURCE,intents:INTENTS});
    }
    const pool=await loadPool();
    if(action==='feed'){
      const mode=String(req.query?.mode)==='pusula'?'pusula':'classic';
      const posts=ranked(pool,intent,mode,limit);
      return res.status(200).json({ok:true,source:SOURCE,mode,intent,intent_label:INTENT_LABELS[intent],posts,metrics:metrics(posts,intent)});
    }
    if(action==='compare'){
      const classic=ranked(pool,intent,'classic',limit), pusula=ranked(pool,intent,'pusula',limit);
      return res.status(200).json({ok:true,source:SOURCE,intent,intent_label:INTENT_LABELS[intent],classic:{posts:classic,metrics:metrics(classic,intent)},pusula:{posts:pusula,metrics:metrics(pusula,intent)}});
    }
    return res.status(400).json({ok:false,error:'Bilinmeyen action'});
  }catch(err){
    console.error('PUSULA API error',err);
    return res.status(502).json({ok:false,error:'GitHub veri havuzuna erişilemedi'});
  }
};

module.exports._test={canonicalIntent,cosine,classicScore,pusulaParts,diverse,enrich,metrics,ranked};
