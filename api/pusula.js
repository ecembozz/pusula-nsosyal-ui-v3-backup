const RUNTIME_POOL = require('../data/runtime/feed_v5.json');
const RUNTIME_META = require('../data/runtime/feed_v5_meta.json');
const { dbConfigured, listReadyRuntimePosts, listInteractionSnapshot } = require('../lib/db');
const { engagementScore, mergeCounts } = require('../lib/engagement');

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
  egitim_yks:'Eğitim', teknoloji_ai:'Yapay zekâ & teknoloji', teknofest_maker:'Teknoloji & maker',
  spor_futbol:'Spor', kultur_sanat:'Kültür & sanat', ekonomi_butce:'Ekonomi & bütçe',
  oyun_espor:'Oyun & e-spor', kampus_is:'Kampüs & iş', gundelik_yasam:'Gündelik yaşam',
  sosyal_sohbet:'Sosyal',
};
const SOURCE = {
  repo:'ecembozz/pusula-nsosyal-ui-v3-backup',
  path:'data/runtime/feed_v5.json',
  pool_size:RUNTIME_POOL.length,
  ranking:'PUSULA transparent ranking v5',
  semantic_candidate:RUNTIME_META?.semantic_architecture?.candidate || 'V5',
  semantic_encoder:RUNTIME_META?.semantic_architecture?.encoder || 'intfloat/multilingual-e5-base',
  semantic_inference:'offline_cached',
  text_provenance:RUNTIME_META?.text_provenance,
  author_provenance:RUNTIME_META?.author_provenance,
  ranking_metadata_provenance:RUNTIME_META?.engagement_freshness_provenance,
  external_runtime_dependency:false,
};

function canonicalIntent(v){ return ALIASES[String(v || 'learn').toLocaleLowerCase('tr-TR')] || 'ogrenmek'; }
function canonicalCategory(v){ const key=String(v||'all'); return key==='all'||Object.prototype.hasOwnProperty.call(CATEGORY_LABELS,key)?key:'all'; }
function filterPoolByCategory(pool,category){ return category==='all'?pool:pool.filter(p=>p.kategori===category); }
function clamp(n,min,max){ return Math.max(min,Math.min(max,n)); }
function cosine(a=[],b=[]){
  let dot=0,na=0,nb=0;
  for(let i=0;i<Math.min(a.length,b.length);i++){
    const av=Number(a[i]||0), bv=Number(b[i]||0);
    dot+=av*bv; na+=av*av; nb+=bv*bv;
  }
  return na&&nb?dot/(Math.sqrt(na)*Math.sqrt(nb)):0;
}
function classicScore(p){
  return .70*Number(p.etkilesim_puani||0)+.20*Number(p.tazelik||0)+.10*(1-Number(p.clickbait||0));
}
function pusulaParts(p,target){
  const vector=p.tahmin_niyet || p.intent_vector || [0,0,0,0];
  const fit=cosine(vector,target);
  const quality=clamp(1-Number(p.clickbait||0),0,1);
  const base=.70*fit+.15*Number(p.tazelik||0)+.15*Number(p.etkilesim_puani||0);
  return {fit,quality,base,score:base*quality};
}
function diverse(items,scoreFn,limit){
  const sorted=[...items].sort((a,b)=>scoreFn(b)-scoreFn(a));
  const out=[], counts={};
  for(const p of sorted){
    if(out.length>=limit)break;
    const key=p.kategori||p.topic_family||'diger';
    if((counts[key]||0)>=5)continue;
    out.push(p); counts[key]=(counts[key]||0)+1;
  }
  if(out.length<limit){
    for(const p of sorted){
      if(out.length>=limit)break;
      if(!out.includes(p))out.push(p);
    }
  }
  return out;
}
function initials(name=''){
  const parts=String(name).trim().split(/\s+/).filter(Boolean);
  return (parts.length>1?parts[0][0]+parts[1][0]:(parts[0]||'?').slice(0,2)).toLocaleUpperCase('tr-TR');
}
function attachEngagement(post,snapshot={totals:{},viewer:{}}){
  const counts=mergeCounts(post,snapshot.totals?.[post.id]);
  const viewer=snapshot.viewer?.[post.id]||{};
  return {
    ...post,
    ...counts,
    etkilesim_puani:engagementScore(counts),
    viewer_liked:Boolean(viewer.liked),
    viewer_shared:Boolean(viewer.reposted),
    viewer_comment_count:Number(viewer.comment_count||0),
  };
}
function enrich(p,rank,intent,mode){
  const target=INTENTS[intent];
  const parts=pusulaParts(p,target);
  const score=mode==='pusula'?parts.score:classicScore(p);
  return {
    id:String(p.id), rank, yazar:p.yazar, author_id:p.author_id, initials:initials(p.yazar), metin:p.metin,
    kategori:p.kategori, kategori_adi:p.kategori_adi || CATEGORY_LABELS[p.kategori] || String(p.kategori||'Diğer').replaceAll('_',' '),
    tahmin_niyet:p.tahmin_niyet || p.intent_vector || [0,0,0,0],
    mixed_intent:Boolean(p.mixed_intent), semantic_confidence:p.semantic_confidence ?? null,
    semantic_method:p.semantic_method || 'pusula-semantic-candidate-v5',
    etkilesim_puani:Number(p.etkilesim_puani||0), tazelik:Number(p.tazelik||0), clickbait:Number(p.clickbait||0),
    like_count:Number(p.like_count||0),comment_count:Number(p.comment_count||0),share_count:Number(p.share_count||0),
    viewer_liked:Boolean(p.viewer_liked),viewer_shared:Boolean(p.viewer_shared),
    viewer_comment_count:Number(p.viewer_comment_count||0),
    score, fit:parts.fit, quality:parts.quality, base:mode==='pusula'?parts.base:0,
    metadata_simulated:p.ranking_metadata_provenance==='deterministic_demo_simulation_not_platform_telemetry',
  };
}
function metrics(posts,intent){
  if(!posts.length)return {
    niyet_uyumu:0, niyet_kalite:0, kalite:0, etkilesim:0, tazelik:0,
    clickbait_ortalama:0, clickbait_yuksek_orani:0, konu_sayisi:0, yazar_sayisi:0,
  };
  const target=INTENTS[intent], n=posts.length;
  const fits=posts.map(p=>cosine(p.tahmin_niyet,target));
  const qualities=posts.map(p=>clamp(1-Number(p.clickbait||0),0,1));
  const fit=fits.reduce((a,b)=>a+b,0)/n;
  const quality=qualities.reduce((a,b)=>a+b,0)/n;
  const intentQuality=fits.reduce((s,v,i)=>s+v*qualities[i],0)/n;
  const engagement=posts.reduce((s,p)=>s+Number(p.etkilesim_puani||0),0)/n;
  const freshness=posts.reduce((s,p)=>s+Number(p.tazelik||0),0)/n;
  const clickbait=posts.reduce((s,p)=>s+Number(p.clickbait||0),0)/n;
  const highClickbait=posts.filter(p=>Number(p.clickbait||0)>=.50).length/n;
  return {
    niyet_uyumu:fit, niyet_kalite:intentQuality, kalite:quality, etkilesim:engagement, tazelik:freshness,
    clickbait_ortalama:clickbait, clickbait_yuksek_orani:highClickbait,
    konu_sayisi:new Set(posts.map(p=>p.kategori)).size,
    yazar_sayisi:new Set(posts.map(p=>p.author_id||p.yazar)).size,
  };
}
function loadPool(){
  if(!Array.isArray(RUNTIME_POOL) || RUNTIME_POOL.length!==320)throw new Error('Geçersiz Candidate V5 runtime havuzu');
  return RUNTIME_POOL;
}
async function loadFeedPool(viewerId=''){
  const base=loadPool();
  if(!dbConfigured())return {pool:base.map(p=>attachEngagement(p)),liveCount:0};
  try{
    const [live,snapshot]=await Promise.all([
      listReadyRuntimePosts(500),
      listInteractionSnapshot(viewerId)
    ]);
    return {pool:[...live,...base].map(p=>attachEngagement(p,snapshot)),liveCount:live.length};
  }catch(err){
    console.error('PUSULA live pool error',err);
    return {pool:base.map(p=>attachEngagement(p)),liveCount:0};
  }
}
function ranked(pool,intent,mode,limit){
  const target=INTENTS[intent];
  const scoreFn=mode==='pusula'?(p)=>pusulaParts(p,target).score:classicScore;
  const selected=diverse(pool,scoreFn,limit);
  return selected.map((p,i)=>enrich(p,i+1,intent,mode));
}
function behaviorBenchmark(pool,limit=20){
  return Object.keys(INTENTS).map(intent=>{
    const classic=ranked(pool,intent,'classic',limit);
    const pusula=ranked(pool,intent,'pusula',limit);
    const classicMetrics=metrics(classic,intent);
    const pusulaMetrics=metrics(pusula,intent);
    return {
      intent,
      intent_label:INTENT_LABELS[intent],
      classic:classicMetrics,
      pusula:pusulaMetrics,
      delta:{
        niyet_uyumu:pusulaMetrics.niyet_uyumu-classicMetrics.niyet_uyumu,
        niyet_kalite:pusulaMetrics.niyet_kalite-classicMetrics.niyet_kalite,
        kalite:pusulaMetrics.kalite-classicMetrics.kalite,
        clickbait_ortalama:pusulaMetrics.clickbait_ortalama-classicMetrics.clickbait_ortalama,
      },
    };
  });
}

module.exports = async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  res.setHeader('Access-Control-Allow-Origin','*');
  res.setHeader('Content-Type','application/json; charset=utf-8');
  if(req.method==='OPTIONS'){ res.statusCode=204; return res.end(); }
  try{
    const action=String(req.query?.action || 'meta');
    const intent=canonicalIntent(req.query?.intent);
    const category=canonicalCategory(req.query?.category);
    const limit=clamp(parseInt(req.query?.limit || '20',10)||20,1,50);
    const viewerId=String(req.query?.viewer_id||'').trim().slice(0,120);
    if(action==='meta'){
      return res.status(200).json({
        ok:true,
        source:{...SOURCE,live_posts_enabled:dbConfigured(),ingestion_semantics:'analyze_once_then_cache'},
        intents:INTENTS,
        runtime_meta:RUNTIME_META
      });
    }
    const loaded=await loadFeedPool(viewerId);
    const fullPool=loaded.pool;
    const pool=filterPoolByCategory(fullPool,category);
    const responseSource={
      ...SOURCE,
      pool_size:fullPool.length,
      static_pool_size:RUNTIME_POOL.length,
      live_pool_size:loaded.liveCount,
      live_posts_enabled:dbConfigured(),
      semantic_inference:loaded.liveCount?'cached_static_plus_gemini_ingest':'offline_cached',
      category,
      category_label:category==='all'?'Tüm kategoriler':CATEGORY_LABELS[category],
      filtered_pool_size:pool.length
    };
    if(action==='feed'){
      const mode=String(req.query?.mode)==='pusula'?'pusula':'classic';
      const posts=ranked(pool,intent,mode,limit);
      return res.status(200).json({ok:true,source:responseSource,mode,intent,intent_label:INTENT_LABELS[intent],category,category_label:responseSource.category_label,posts,metrics:metrics(posts,intent)});
    }
    if(action==='compare'){
      const classic=ranked(pool,intent,'classic',limit), pusula=ranked(pool,intent,'pusula',limit);
      return res.status(200).json({ok:true,source:responseSource,intent,intent_label:INTENT_LABELS[intent],category,category_label:responseSource.category_label,classic:{posts:classic,metrics:metrics(classic,intent)},pusula:{posts:pusula,metrics:metrics(pusula,intent)}});
    }
    if(action==='benchmark'){
      return res.status(200).json({
        ok:true,
        status:'runtime_behavior_smoke_not_final_human_gold_accuracy',
        source:SOURCE,
        limit,
        rows:behaviorBenchmark(loadPool(),limit),
      });
    }
    return res.status(400).json({ok:false,error:'Bilinmeyen action'});
  }catch(err){
    console.error('PUSULA API error',err);
    return res.status(500).json({ok:false,error:'Candidate V5 runtime havuzu yüklenemedi'});
  }
};

module.exports._test={SOURCE,RUNTIME_META,canonicalIntent,canonicalCategory,filterPoolByCategory,cosine,classicScore,pusulaParts,diverse,attachEngagement,enrich,metrics,loadPool,loadFeedPool,ranked,behaviorBenchmark};
