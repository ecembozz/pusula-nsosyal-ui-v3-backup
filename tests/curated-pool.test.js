const test=require('node:test');
const assert=require('node:assert/strict');
const posts=require('../data/runtime/curated_competition_posts_v1');

const CATEGORIES=[
  'egitim_yks','teknoloji_ai','teknofest_maker','spor_futbol','kultur_sanat',
  'ekonomi_butce','oyun_espor','kampus_is','gundelik_yasam','sosyal_sohbet'
];

test('curated competition pool has five posts per category',()=>{
  assert.equal(posts.length,50);
  for(const category of CATEGORIES){
    assert.equal(posts.filter(post=>post.kategori===category).length,5,category);
  }
});

test('curated posts have unique natural text and valid intent vectors',()=>{
  assert.equal(new Set(posts.map(post=>post.id)).size,posts.length);
  assert.equal(new Set(posts.map(post=>post.metin)).size,posts.length);
  for(const post of posts){
    assert.ok(post.metin.length>=70,post.id);
    assert.ok(post.metin.length<=320,post.id);
    assert.equal(post.tahmin_niyet.length,4,post.id);
    assert.ok(post.tahmin_niyet.every(value=>value>=0&&value<=1),post.id);
    assert.ok(post.clickbait>=0&&post.clickbait<=1,post.id);
    assert.ok(post.etkilesim_puani>=0&&post.etkilesim_puani<=1,post.id);
    assert.ok(post.tazelik>=0&&post.tazelik<=1,post.id);
  }
});

test('competition set is relevant without turning the whole feed into an ad',()=>{
  const competitionMentions=posts.filter(post=>/teknofest|yarışma|jüri|prototip/i.test(post.metin));
  assert.ok(competitionMentions.length>=15);
  assert.ok(competitionMentions.length<=30);
  assert.ok(posts.filter(post=>post.clickbait<=.05).length>=45);
});
