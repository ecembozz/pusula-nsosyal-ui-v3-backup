const test=require('node:test');
const assert=require('node:assert/strict');
const posts=require('../data/runtime/curated_news_posts_v1');
const pusula=require('../api/pusula')._test;

test('news pool contains 60 source-backed items across three editorial desks',()=>{
  assert.equal(posts.length,60);
  assert.deepEqual(new Set(posts.map(post=>post.news_kind)),new Set(['teknofest','ai','software']));
  for(const kind of ['teknofest','ai','software'])assert.ok(posts.filter(post=>post.news_kind===kind).length>=20,kind);
});

test('every news item has safe source metadata and a news-shaped intent profile',()=>{
  assert.equal(new Set(posts.map(post=>post.id)).size,posts.length);
  assert.equal(new Set(posts.map(post=>post.headline)).size,posts.length);
  for(const post of posts){
    assert.match(post.news_date,/^20\d\d-\d\d-\d\d$/,post.id);
    assert.match(post.source_url,/^https:\/\//,post.id);
    assert.ok(post.source_name.length>=3,post.id);
    assert.ok(post.headline.length>=18&&post.headline.length<=100,post.id);
    assert.ok(post.metin.length>=75&&post.metin.length<=260,post.id);
    assert.equal(post.style,'verified_news',post.id);
    assert.equal(post.content_provenance,'official_source_news_summary',post.id);
    assert.ok(post.tahmin_niyet[2]>=.9,post.id);
    assert.ok(post.like_count>=0&&post.comment_count>=0&&post.share_count>=0,post.id);
  }
});

test('Haberdar olmak feed is dominated by verified news rather than casual posts',()=>{
  const ranked=pusula.ranked(pusula.loadPool(),'haberdar','pusula',20);
  assert.ok(ranked.filter(post=>post.style==='verified_news').length>=16);
  assert.ok(ranked.filter(post=>post.source_url).length>=16);
  for(const kind of ['teknofest','ai','software']){
    assert.ok(ranked.filter(post=>post.news_kind===kind).length>=4,kind);
  }
});
