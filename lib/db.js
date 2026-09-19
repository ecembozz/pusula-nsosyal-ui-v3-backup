const { neon } = require('@neondatabase/serverless');

let sqlClient = null;
let schemaReady = null;

function connectionString(){
  return process.env.DATABASE_URL || process.env.POSTGRES_URL || '';
}
function dbConfigured(){
  return Boolean(connectionString());
}
function sql(){
  if(!dbConfigured()) throw new Error('DATABASE_URL yapılandırılmamış');
  if(!sqlClient) sqlClient = neon(connectionString());
  return sqlClient;
}
async function ensureSchema(){
  if(!dbConfigured()) throw new Error('DATABASE_URL yapılandırılmamış');
  if(schemaReady) return schemaReady;
  schemaReady=(async()=>{
    const q=sql();
    await q`
      CREATE TABLE IF NOT EXISTS pusula_posts (
        id TEXT PRIMARY KEY,
        author_id TEXT NOT NULL,
        author_name TEXT NOT NULL,
        content TEXT NOT NULL,
        analysis_status TEXT NOT NULL DEFAULT 'pending',
        analysis_error TEXT,
        like_count INTEGER NOT NULL DEFAULT 0,
        comment_count INTEGER NOT NULL DEFAULT 0,
        share_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await q`
      CREATE TABLE IF NOT EXISTS pusula_post_analysis (
        post_id TEXT PRIMARY KEY REFERENCES pusula_posts(id) ON DELETE CASCADE,
        category TEXT NOT NULL,
        intent_vector JSONB NOT NULL,
        clickbait_risk DOUBLE PRECISION NOT NULL,
        semantic_confidence DOUBLE PRECISION NOT NULL,
        mixed_intent BOOLEAN NOT NULL DEFAULT FALSE,
        topics JSONB NOT NULL DEFAULT '[]'::jsonb,
        semantic_method TEXT NOT NULL,
        analysis_model TEXT NOT NULL,
        analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `;
    await q`CREATE INDEX IF NOT EXISTS pusula_posts_ready_created_idx ON pusula_posts (analysis_status, created_at DESC)`;
    await q`CREATE INDEX IF NOT EXISTS pusula_analysis_category_idx ON pusula_post_analysis (category)`;
    return true;
  })().catch(err=>{schemaReady=null;throw err});
  return schemaReady;
}
async function createPendingPost({id,authorId,authorName,content}){
  await ensureSchema();
  const q=sql();
  const rows=await q`
    INSERT INTO pusula_posts (id,author_id,author_name,content,analysis_status)
    VALUES (${id},${authorId},${authorName},${content},'pending')
    RETURNING *
  `;
  return rows[0];
}
async function saveAnalysis(postId,a){
  await ensureSchema();
  const q=sql();
  const vector=JSON.stringify(a.intent_vector);
  const topics=JSON.stringify(a.topics||[]);
  await q`
    INSERT INTO pusula_post_analysis
      (post_id,category,intent_vector,clickbait_risk,semantic_confidence,mixed_intent,topics,semantic_method,analysis_model)
    VALUES
      (${postId},${a.category},${vector}::jsonb,${a.clickbait_risk},${a.semantic_confidence},${a.mixed_intent},${topics}::jsonb,${a.semantic_method},${a.analysis_model})
    ON CONFLICT (post_id) DO UPDATE SET
      category=EXCLUDED.category,
      intent_vector=EXCLUDED.intent_vector,
      clickbait_risk=EXCLUDED.clickbait_risk,
      semantic_confidence=EXCLUDED.semantic_confidence,
      mixed_intent=EXCLUDED.mixed_intent,
      topics=EXCLUDED.topics,
      semantic_method=EXCLUDED.semantic_method,
      analysis_model=EXCLUDED.analysis_model,
      analyzed_at=NOW()
  `;
  await q`UPDATE pusula_posts SET analysis_status='ready',analysis_error=NULL,updated_at=NOW() WHERE id=${postId}`;
  return getPost(postId);
}
async function markAnalysisFailed(postId,error){
  await ensureSchema();
  const q=sql();
  const message=String(error||'analysis_failed').slice(0,500);
  await q`UPDATE pusula_posts SET analysis_status='failed',analysis_error=${message},updated_at=NOW() WHERE id=${postId}`;
}
async function getPost(id){
  await ensureSchema();
  const q=sql();
  const rows=await q`
    SELECT p.*,a.category,a.intent_vector,a.clickbait_risk,a.semantic_confidence,
           a.mixed_intent,a.topics,a.semantic_method,a.analysis_model,a.analyzed_at
    FROM pusula_posts p
    LEFT JOIN pusula_post_analysis a ON a.post_id=p.id
    WHERE p.id=${id}
    LIMIT 1
  `;
  return rows[0]||null;
}
async function listRecentPosts(limit=20){
  await ensureSchema();
  const q=sql();
  const n=Math.max(1,Math.min(100,Number(limit)||20));
  return q`
    SELECT p.*,a.category,a.intent_vector,a.clickbait_risk,a.semantic_confidence,
           a.mixed_intent,a.topics,a.semantic_method,a.analysis_model,a.analyzed_at
    FROM pusula_posts p
    LEFT JOIN pusula_post_analysis a ON a.post_id=p.id
    ORDER BY p.created_at DESC
    LIMIT ${n}
  `;
}
function freshnessScore(createdAt,now=Date.now()){
  const ageMs=Math.max(0,now-new Date(createdAt).getTime());
  const ageHours=ageMs/3600000;
  return Math.max(0,Math.min(1,Math.exp(-Math.LN2*ageHours/72)));
}
function engagementScore({like_count=0,comment_count=0,share_count=0}={}){
  const weighted=Math.max(0,Number(like_count)||0)+2*Math.max(0,Number(comment_count)||0)+3*Math.max(0,Number(share_count)||0);
  return Math.max(0,Math.min(1,1-Math.exp(-weighted/20)));
}
function vectorValue(v){
  if(Array.isArray(v)) return v.map(Number);
  if(typeof v==='string'){
    try{return JSON.parse(v).map(Number)}catch(e){return [0,0,0,0]}
  }
  return [0,0,0,0];
}
async function listReadyRuntimePosts(limit=500){
  if(!dbConfigured()) return [];
  await ensureSchema();
  const q=sql();
  const n=Math.max(1,Math.min(2000,Number(limit)||500));
  const rows=await q`
    SELECT p.id,p.author_id,p.author_name,p.content,p.like_count,p.comment_count,p.share_count,p.created_at,
           a.category,a.intent_vector,a.clickbait_risk,a.semantic_confidence,a.mixed_intent,a.semantic_method,a.analysis_model
    FROM pusula_posts p
    JOIN pusula_post_analysis a ON a.post_id=p.id
    WHERE p.analysis_status='ready'
    ORDER BY p.created_at DESC
    LIMIT ${n}
  `;
  return rows.map(r=>({
    id:r.id,
    yazar:r.author_name,
    author_id:r.author_id,
    metin:r.content,
    kategori:r.category,
    topic_family:r.category,
    style:'live',
    tahmin_niyet:vectorValue(r.intent_vector),
    clickbait:Number(r.clickbait_risk||0),
    mixed_intent:Boolean(r.mixed_intent),
    semantic_confidence:Number(r.semantic_confidence||0),
    semantic_method:r.semantic_method||'gemini_structured_intent_v1',
    analysis_model:r.analysis_model||null,
    etkilesim_puani:engagementScore(r),
    tazelik:freshnessScore(r.created_at),
    created_at:r.created_at,
    content_provenance:'live_user_post',
    source_basis:'live_user_post',
    author_provenance:'live_demo_user',
    ranking_metadata_provenance:'live_dynamic_freshness_engagement'
  }));
}
async function updateEngagement(id,event,delta=1){
  await ensureSchema();
  const q=sql();
  const d=delta<0?-1:1;
  if(event==='like'){
    await q`UPDATE pusula_posts SET like_count=GREATEST(0,like_count+${d}),updated_at=NOW() WHERE id=${id}`;
  }else if(event==='comment'){
    await q`UPDATE pusula_posts SET comment_count=GREATEST(0,comment_count+${d}),updated_at=NOW() WHERE id=${id}`;
  }else if(event==='share'){
    await q`UPDATE pusula_posts SET share_count=GREATEST(0,share_count+${d}),updated_at=NOW() WHERE id=${id}`;
  }else{
    throw new Error('Geçersiz etkileşim türü');
  }
  return getPost(id);
}

module.exports={
  dbConfigured,ensureSchema,createPendingPost,saveAnalysis,markAnalysisFailed,getPost,
  listRecentPosts,listReadyRuntimePosts,updateEngagement,freshnessScore,engagementScore
};
