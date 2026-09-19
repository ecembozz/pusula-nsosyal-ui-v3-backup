function clamp(n,min=0,max=1){
  return Math.max(min,Math.min(max,Number(n)||0));
}

function engagementScore({like_count=0,comment_count=0,share_count=0}={}){
  const likes=Math.max(0,Number(like_count)||0);
  const comments=Math.max(0,Number(comment_count)||0);
  const shares=Math.max(0,Number(share_count)||0);
  const weighted=likes+2*comments+3*shares;
  return clamp(1-Math.exp(-weighted/20));
}

function stableFraction(value){
  let hash=2166136261;
  for(const char of String(value||'')){
    hash^=char.codePointAt(0);
    hash=Math.imul(hash,16777619);
  }
  return (hash>>>0)/4294967295;
}

function seededCounts(post={}){
  if(post.content_provenance==='live_user_post' || String(post.id||'').startsWith('live_')){
    return {
      like_count:Math.max(0,Number(post.like_count)||0),
      comment_count:Math.max(0,Number(post.comment_count)||0),
      share_count:Math.max(0,Number(post.share_count)||0),
    };
  }
  const score=clamp(post.etkilesim_puani,0,.985);
  const weighted=Math.max(0,Math.round(-20*Math.log(Math.max(.015,1-score))));
  const seed=stableFraction(post.id);
  const share_count=Math.min(Math.floor(weighted/3),Math.floor(weighted*(.055+.045*seed)/3));
  const comment_count=Math.min(Math.floor((weighted-3*share_count)/2),Math.floor(weighted*(.13+.08*(1-seed))/2));
  const like_count=Math.max(0,weighted-2*comment_count-3*share_count);
  return {like_count,comment_count,share_count};
}

function mergeCounts(post,deltas={}){
  const base=seededCounts(post);
  return {
    like_count:base.like_count+Math.max(0,Number(deltas.like_delta)||0),
    comment_count:base.comment_count+Math.max(0,Number(deltas.comment_delta)||0),
    share_count:base.share_count+Math.max(0,Number(deltas.share_delta)||0),
  };
}

module.exports={engagementScore,seededCounts,mergeCounts,stableFraction};
