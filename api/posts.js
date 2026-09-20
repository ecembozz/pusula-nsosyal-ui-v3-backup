const crypto=require('crypto');
const RUNTIME_POOL=require('../data/runtime/feed_v5.json');
const CURATED_POOL=require('../data/runtime/curated_competition_posts_v1');
const {
  dbConfigured,ensureSchema,createPendingPost,saveAnalysis,markAnalysisFailed,getPost,
  listRecentPosts,updateEngagement,updateInteraction
}=require('../lib/db');
const {engagementScore,mergeCounts}=require('../lib/engagement');
const {analyzePost,DEFAULT_MODEL}=require('../lib/gemini');

function jsonBody(req){
  if(req.body&&typeof req.body==='object')return req.body;
  if(typeof req.body==='string'&&req.body.trim()){
    try{return JSON.parse(req.body)}catch(e){return {}}
  }
  return {};
}
function safeText(v,max){
  return String(v||'').trim().slice(0,max);
}
function publicPost(p){
  if(!p)return null;
  return {
    id:p.id,
    author_id:p.author_id,
    author_name:p.author_name,
    content:p.content,
    analysis_status:p.analysis_status,
    analysis_error:p.analysis_error||null,
    category:p.category||null,
    intent_vector:p.intent_vector||null,
    clickbait_risk:p.clickbait_risk==null?null:Number(p.clickbait_risk),
    semantic_confidence:p.semantic_confidence==null?null:Number(p.semantic_confidence),
    mixed_intent:p.mixed_intent==null?null:Boolean(p.mixed_intent),
    topics:p.topics||[],
    semantic_method:p.semantic_method||null,
    analysis_model:p.analysis_model||null,
    like_count:Number(p.like_count||0),
    comment_count:Number(p.comment_count||0),
    share_count:Number(p.share_count||0),
    created_at:p.created_at,
    analyzed_at:p.analyzed_at||null
  };
}
async function analyzeAndPersist(id,content){
  try{
    const analysis=await analyzePost(content);
    const row=await saveAnalysis(id,analysis);
    return {ok:true,row};
  }catch(err){
    await markAnalysisFailed(id,err?.message||err);
    return {ok:false,error:err?.message||'Gemini analizi başarısız'};
  }
}

module.exports=async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  res.setHeader('Access-Control-Allow-Origin','*');
  res.setHeader('Access-Control-Allow-Headers','Content-Type');
  res.setHeader('Access-Control-Allow-Methods','GET,POST,PATCH,OPTIONS');
  res.setHeader('Content-Type','application/json; charset=utf-8');
  if(req.method==='OPTIONS'){res.statusCode=204;return res.end();}
  try{
    const action=String(req.query?.action||'').toLowerCase();

    if(req.method==='GET'&&action==='status'){
      return res.status(200).json({
        ok:true,
        database_configured:dbConfigured(),
        gemini_configured:Boolean(process.env.GEMINI_API_KEY),
        gemini_model:process.env.GEMINI_MODEL||DEFAULT_MODEL
      });
    }

    if(!dbConfigured()){
      return res.status(503).json({ok:false,error:'DATABASE_URL yapılandırılmamış'});
    }
    await ensureSchema();

    if(req.method==='GET'){
      const limit=Math.max(1,Math.min(100,parseInt(req.query?.limit||'20',10)||20));
      const rows=await listRecentPosts(limit);
      return res.status(200).json({ok:true,posts:rows.map(publicPost)});
    }

    if(req.method==='POST'&&action==='retry'){
      const body=jsonBody(req);
      const id=safeText(req.query?.id||body.id,120);
      if(!id)return res.status(400).json({ok:false,error:'Post id gerekli'});
      const post=await getPost(id);
      if(!post)return res.status(404).json({ok:false,error:'Gönderi bulunamadı'});
      if(!process.env.GEMINI_API_KEY)return res.status(503).json({ok:false,error:'GEMINI_API_KEY yapılandırılmamış'});
      const result=await analyzeAndPersist(id,post.content);
      if(!result.ok)return res.status(502).json({ok:false,error:result.error,post:publicPost(await getPost(id))});
      return res.status(200).json({ok:true,post:publicPost(result.row)});
    }

    if(req.method==='POST'){
      if(!process.env.GEMINI_API_KEY)return res.status(503).json({ok:false,error:'GEMINI_API_KEY yapılandırılmamış'});
      const body=jsonBody(req);
      const content=safeText(body.content,1000);
      if(content.length<2)return res.status(400).json({ok:false,error:'Gönderi metni çok kısa'});
      const authorName=safeText(body.author_name||'Sen',80)||'Sen';
      const authorId=safeText(body.author_id||'demo_current_user',120)||'demo_current_user';
      const id='live_'+crypto.randomUUID();
      await createPendingPost({id,authorId,authorName,content});
      const started=Date.now();
      const result=await analyzeAndPersist(id,content);
      if(!result.ok){
        return res.status(202).json({
          ok:true,
          analysis_status:'failed',
          analysis_ms:Date.now()-started,
          post:publicPost(await getPost(id)),
          warning:'Gönderi veritabanına kaydedildi ancak semantik analiz tamamlanamadı.',
          analysis_error:result.error
        });
      }
      return res.status(201).json({
        ok:true,
        analysis_status:'ready',
        analysis_ms:Date.now()-started,
        post:publicPost(result.row)
      });
    }

    if(req.method==='PATCH'){
      const body=jsonBody(req);
      const id=safeText(body.id||req.query?.id,120);
      const event=safeText(body.event||req.query?.event,20);
      if(!id)return res.status(400).json({ok:false,error:'Post id gerekli'});
      if(action==='interact'){
        const actorId=safeText(body.actor_id,120);
        if(!actorId)return res.status(400).json({ok:false,error:'Anonim kullanıcı kimliği gerekli'});
        if(!['like','comment','share'].includes(event))return res.status(400).json({ok:false,error:'Geçersiz etkileşim türü'});
        const live=await getPost(id);
        const seeded=[...CURATED_POOL,...RUNTIME_POOL].find(p=>String(p.id)===id);
        if(!live&&!seeded)return res.status(404).json({ok:false,error:'Gönderi bulunamadı'});
        const interaction=await updateInteraction({
          postId:id,
          actorId,
          event,
          active:body.active!==false,
          comment:safeText(body.comment,240),
          sessionId:safeText(body.session_id,120),
          intent:safeText(body.intent,30),
          mode:safeText(body.mode,20),
          rank:Number.isFinite(Number(body.rank))?Math.max(1,Math.min(500,Number(body.rank))):null
        });
        const source=live?{
          id:live.id,
          content_provenance:'live_user_post',
          like_count:live.like_count,
          comment_count:live.comment_count,
          share_count:live.share_count
        }:seeded;
        const counts=mergeCounts(source,interaction.totals);
        return res.status(200).json({
          ok:true,
          id,
          event,
          changed:interaction.changed,
          counts,
          engagement_score:engagementScore(counts),
          viewer:{
            liked:interaction.viewer.liked,
            shared:interaction.viewer.reposted,
            comment_count:interaction.viewer.comment_count
          }
        });
      }
      const delta=Number(body.delta??req.query?.delta??1)<0?-1:1;
      const row=await updateEngagement(id,event,delta);
      if(!row)return res.status(404).json({ok:false,error:'Gönderi bulunamadı'});
      return res.status(200).json({ok:true,post:publicPost(row)});
    }

    return res.status(405).json({ok:false,error:'Method not allowed'});
  }catch(err){
    console.error('PUSULA posts API error',err);
    return res.status(500).json({ok:false,error:'Gönderi işlemi tamamlanamadı'});
  }
};
