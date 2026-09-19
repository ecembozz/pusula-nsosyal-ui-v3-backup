const test=require('node:test');
const assert=require('node:assert/strict');
const pool=require('../data/runtime/feed_v5.json');
const {engagementScore,seededCounts,mergeCounts}=require('../lib/engagement');

test('all static posts receive deterministic non-negative counters',()=>{
  for(const post of pool){
    const first=seededCounts(post);
    const second=seededCounts(post);
    assert.deepEqual(first,second);
    assert.ok(first.like_count>=0);
    assert.ok(first.comment_count>=0);
    assert.ok(first.share_count>=0);
    assert.ok(Number.isInteger(first.like_count));
    assert.ok(Number.isInteger(first.comment_count));
    assert.ok(Number.isInteger(first.share_count));
  }
});

test('live posts start from their database counters',()=>{
  const post={id:'live_test',content_provenance:'live_user_post',like_count:2,comment_count:1,share_count:3};
  assert.deepEqual(seededCounts(post),{like_count:2,comment_count:1,share_count:3});
});

test('interaction deltas increase counts and engagement',()=>{
  const post=pool[0];
  const before=mergeCounts(post);
  const after=mergeCounts(post,{like_delta:1,comment_delta:1,share_delta:1});
  assert.deepEqual(after,{
    like_count:before.like_count+1,
    comment_count:before.comment_count+1,
    share_count:before.share_count+1,
  });
  assert.ok(engagementScore(after)>engagementScore(before));
});

test('weighted engagement remains normalized',()=>{
  assert.equal(engagementScore({}),0);
  assert.ok(engagementScore({like_count:10,comment_count:2,share_count:1})<1);
  assert.ok(engagementScore({like_count:10000,comment_count:10000,share_count:10000})<=1);
});
