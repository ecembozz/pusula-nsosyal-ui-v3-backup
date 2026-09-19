(function(){
  if(window.__pusulaCompassGuideInstalled)return;
  window.__pusulaCompassGuideInstalled=true;

  let shown=false;
  let root=null;
  let resizeRaf=0;
  let guideStep=0;

  const COPY=[
    {title:"PUSULA",text:"Bu oturumda ne görmek istediğini seç.",selector:'.pcIntent[data-intent="learn"]',pad:8},
    {title:"Yönünü seç",text:"Pusulayı sürükle veya bir yöne dokun. Hızlı çevir; PUSULA senin için seçsin.",selector:'.pcArt',pad:18},
    {title:"Yönler",text:"Öğrenmek, Eğlenmek, Haberdar olmak, Sosyalleşmek veya Sadece dolaşmak.",selector:'.pcIntent[data-intent="news"]',pad:8},
    {title:"Kategori seç",text:"İstersen akışı tek bir kategoriyle sınırla; varsayılan olarak tüm kategoriler seçilir.",selector:'.pcCategoryRow',pad:7},
    {title:"Süre",text:"15 dk, 30 dk, Sınırsız seç veya süreyi kendin gir.",selector:'.budgetRow',pad:7},
    {title:"Hemen dene",text:"Akışını oluştur.",selector:'[data-apply]',pad:7}
  ];

  function ensureStyle(){
    if(document.getElementById('pusula-compass-guide-style'))return;
    const s=document.createElement('style');
    s.id='pusula-compass-guide-style';
    s.textContent=`
#pusulaCompassGuide{position:fixed;inset:0;z-index:12000;font-family:inherit;color:#12233f;isolation:isolate}
#pusulaCompassGuide .pcgHitPlane{position:absolute;inset:0;z-index:0;background:transparent;cursor:default}
#pusulaCompassGuide .pcgMaskSvg,#pusulaCompassGuide .pcgArrowSvg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
#pusulaCompassGuide .pcgMaskSvg{z-index:1}#pusulaCompassGuide .pcgArrowSvg{z-index:4;overflow:visible}
#pusulaCompassGuide .pcgGlow{display:none!important}
#pusulaCompassGuide .pcgDesktopCards{display:none!important}
#pusulaCompassGuide .pcgMobileCard{display:block;position:fixed;z-index:6;width:min(360px,calc(100vw - 32px));box-sizing:border-box;border-radius:18px;background:rgba(255,255,255,.98);border:1px solid rgba(95,179,255,.7);box-shadow:0 16px 46px rgba(7,35,75,.26);padding:14px 15px 13px 56px;color:#10213d;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);transition:top .16s ease,bottom .16s ease,left .16s ease}
#pusulaCompassGuide .pcgNum{position:absolute;left:11px;top:12px;width:36px;height:36px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#20bfe3,#2768f7);color:white;font-weight:800;font-size:18px;box-shadow:0 5px 14px rgba(36,112,246,.32)}
#pusulaCompassGuide .pcgTitle{font-size:14px;line-height:1.2;font-weight:800;letter-spacing:-.01em}
#pusulaCompassGuide .pcgText{margin-top:3px;font-size:11px;line-height:1.35;color:#5b6f8e}
#pusulaCompassGuide .pcgMobileActions{display:flex;justify-content:flex-end;align-items:center;gap:8px;margin-top:10px}
#pusulaCompassGuide .pcgCount{margin-right:auto;font-size:10px;color:#72849c;font-weight:700}
#pusulaCompassGuide .pcgNext{border:0;border-radius:999px;padding:8px 15px;background:linear-gradient(115deg,#20bed5,#3974ff);color:#fff;font-size:11px;font-weight:800;cursor:pointer}
#pusulaCompassGuide .pcgStableLowerCard{height:104px;min-height:104px;box-sizing:border-box}
#pusulaCompassGuide .pcgClose{position:fixed;right:18px;top:18px;z-index:7;border:1px solid rgba(255,255,255,.56);background:rgba(255,255,255,.9);color:#27405f;height:34px;padding:0 13px;border-radius:999px;font-weight:700;font-size:11px;box-shadow:0 8px 24px rgba(16,43,76,.12);backdrop-filter:blur(12px);cursor:pointer}
html[data-theme="dark"] #pusulaCompassGuide .pcgMobileCard{background:rgba(22,28,39,.98);color:#f4f8fd;border-color:rgba(61,157,255,.62);box-shadow:0 16px 44px rgba(0,0,0,.34),0 0 0 1px rgba(73,167,255,.12)}
html[data-theme="dark"] #pusulaCompassGuide .pcgText{color:#a9bad0}
html[data-theme="dark"] #pusulaCompassGuide .pcgClose{background:rgba(24,31,43,.92);color:#edf5ff;border-color:rgba(93,130,166,.45)}
html.pusulaCompassGuideLocked,html.pusulaCompassGuideLocked body{overflow:hidden!important;overscroll-behavior:none!important}
html.pusulaCompassGuideLocked #intentModal .pusulaCompassModal{overscroll-behavior:none!important}
@media(max-width:720px){
 #pusulaCompassGuide .pcgClose{top:10px;right:10px;height:31px;font-size:10px;padding:0 11px}
 #pusulaCompassGuide .pcgMobileCard{left:12px!important;right:12px!important;width:auto;bottom:calc(12px + env(safe-area-inset-bottom));padding:13px 13px 12px 54px}
 #pusulaCompassGuide .pcgMobileCard .pcgNum{left:10px;top:12px}
 #pusulaCompassGuide .pcgStableLowerCard{height:102px;min-height:102px}
}
`;
    document.head.appendChild(s);
  }

  function clamp(n,min,max){return Math.max(min,Math.min(max,n))}

  function rectFor(el,pad){
    if(!el)return null;
    const r=el.getBoundingClientRect();
    if(!r.width||!r.height)return null;
    const p=pad||0;
    return {x:r.left-p,y:r.top-p,w:r.width+p*2,h:r.height+p*2,cx:r.left+r.width/2,cy:r.top+r.height/2};
  }

  function getTargets(){
    const modal=document.querySelector('#intentModal.show .pusulaCompassModal');
    if(!modal)return null;
    const targets=COPY.map(c=>({copy:c,el:modal.querySelector(c.selector)}));
    return targets.every(t=>t.el)?{modal,targets}:null;
  }

  function layoutMask(rects,activeIndex){
    if(!root)return;
    const svg=root.querySelector('.pcgMaskSvg');
    const mask=svg.querySelector('#pcgMask');
    mask.querySelectorAll('.pcgHole').forEach(n=>n.remove());
    svg.querySelectorAll('.pcgGlow').forEach(n=>n.remove());
    rects.forEach((r,i)=>{
      if(i!==activeIndex)return;
      const rr=Math.min(22,Math.max(10,Math.min(r.w,r.h)*.18));
      const hole=document.createElementNS('http://www.w3.org/2000/svg','rect');
      hole.setAttribute('class','pcgHole');hole.setAttribute('x',r.x);hole.setAttribute('y',r.y);hole.setAttribute('width',r.w);hole.setAttribute('height',r.h);hole.setAttribute('rx',rr);hole.setAttribute('fill','black');mask.appendChild(hole);
    });
  }

  function updateCard(card){
    card.querySelector('.pcgNum').textContent=guideStep+1;
    card.querySelector('.pcgTitle').textContent=COPY[guideStep].title;
    card.querySelector('.pcgText').textContent=COPY[guideStep].text;
    card.querySelector('.pcgCount').textContent=(guideStep+1)+' / '+COPY.length;
    card.querySelector('.pcgNext').textContent=guideStep===COPY.length-1?'Bitir':'İleri';
    card.classList.toggle('pcgStableLowerCard',guideStep>=3);
  }

  function placeCard(card,target,modal,isMobile){
    if(isMobile){
      if(guideStep<3){
        card.style.top='auto';
        card.style.bottom='calc(12px + env(safe-area-inset-bottom))';
        return;
      }
      const anchor=guideStep>=3?(modal.querySelector('.pcCategoryRow')||target):target;
      const tr=anchor.getBoundingClientRect();
      const cr=card.getBoundingClientRect();
      const top=clamp(tr.top-cr.height-24,76,window.innerHeight-cr.height-18);
      card.style.bottom='auto';
      card.style.top=Math.round(top)+'px';
      return;
    }

    const cr=card.getBoundingClientRect();
    const mr=modal.getBoundingClientRect();
    card.style.bottom='auto';

    if(guideStep<3){
      const left=clamp(mr.left+(mr.width-cr.width)/2,18,window.innerWidth-cr.width-18);
      const top=clamp(mr.bottom-cr.height-22,24,window.innerHeight-cr.height-20);
      card.style.left=Math.round(left)+'px';
      card.style.top=Math.round(top)+'px';
      return;
    }

    const anchor=guideStep>=3?(modal.querySelector('.pcCategoryRow')||target):target;
    const ar=anchor.getBoundingClientRect();
    const left=clamp(mr.left+(mr.width-cr.width)/2,18,window.innerWidth-cr.width-18);
    const top=clamp(ar.top-cr.height-26,24,window.innerHeight-cr.height-20);
    card.style.left=Math.round(left)+'px';
    card.style.top=Math.round(top)+'px';
  }

  function budgetControlsRect(target){
    const controls=[...target.querySelectorAll('[data-modalbudget],.pcCustomBudget')].filter(el=>{
      const r=el.getBoundingClientRect();return r.width&&r.height;
    });
    if(!controls.length)return null;
    const rects=controls.map(el=>el.getBoundingClientRect());
    return {
      left:Math.min(...rects.map(r=>r.left)),
      right:Math.max(...rects.map(r=>r.right)),
      top:Math.min(...rects.map(r=>r.top)),
      bottom:Math.max(...rects.map(r=>r.bottom))
    };
  }

  function specialEnd(target,step){
    const tr=target.getBoundingClientRect();
    if(step===1)return {x:tr.left+10,y:tr.top+tr.height*.53};
    if(step===3){
      const trigger=target.querySelector?.('.pcCategoryTrigger');
      const rr=trigger?.getBoundingClientRect()||tr;
      return {x:rr.left+rr.width*.72,y:rr.top-7};
    }
    if(step===4){
      const controls=budgetControlsRect(target);
      if(controls)return {x:controls.left+(controls.right-controls.left)*.72,y:controls.top-8};
      return {x:tr.left+tr.width*.70,y:tr.top-7};
    }
    if(step===5)return {x:tr.left+tr.width*.72,y:tr.top-7};
    return null;
  }

  function arrowPath(card,target,step){
    const cr=card.getBoundingClientRect();
    const tr=target.getBoundingClientRect();
    const bias=[.82,.18,.82,.64,.82,.72][step]||.78;
    let start,end=specialEnd(target,step);

    if(step===1){
      start={x:cr.left+cr.width*.23,y:cr.top-8};
    }else if(step===3){
      start={x:cr.right-1,y:cr.top+cr.height*.38};
    }else if(step===4){
      start={x:cr.left+1,y:cr.top+cr.height*.62};
    }else if(step===5){
      start={x:cr.right-1,y:cr.top+cr.height*.72};
    }else if(cr.bottom<=tr.top){
      start={x:cr.left+cr.width*bias,y:cr.bottom+8};
    }else if(cr.top>=tr.bottom){
      start={x:cr.left+cr.width*bias,y:cr.top-8};
    }else if(tr.left>=cr.right){
      start={x:cr.right+8,y:cr.top+cr.height*.26};
    }else{
      start={x:cr.left-8,y:cr.top+cr.height*.26};
    }

    if(!end){
      if(cr.bottom<=tr.top){
        end={x:clamp(tr.left+tr.width/2,tr.left+10,tr.right-10),y:tr.top-8};
      }else if(cr.top>=tr.bottom){
        end={x:clamp(tr.left+tr.width/2,tr.left+10,tr.right-10),y:tr.bottom+8};
      }else if(tr.left>=cr.right){
        end={x:tr.left-8,y:clamp(tr.top+tr.height/2,tr.top+8,tr.bottom-8)};
      }else{
        end={x:tr.right+8,y:clamp(tr.top+tr.height/2,tr.top+8,tr.bottom-8)};
      }
    }

    const mx=(start.x+end.x)/2,my=(start.y+end.y)/2;
    const dx=end.x-start.x,dy=end.y-start.y,len=Math.max(1,Math.hypot(dx,dy));
    const nx=-dy/len,ny=dx/len;
    let bend,dir;
    if(step===1){bend=30;dir=-1}
    else if(step===3){bend=28;dir=-1}
    else if(step===4){bend=30;dir=1}
    else if(step===5){bend=26;dir=-1}
    else{bend=34;dir=step%2===0?1:-1}
    return `M ${start.x.toFixed(1)} ${start.y.toFixed(1)} Q ${(mx+nx*bend*dir).toFixed(1)} ${(my+ny*bend*dir).toFixed(1)} ${end.x.toFixed(1)} ${end.y.toFixed(1)}`;
  }

  function drawArrow(card,target){
    const arrowSvg=root.querySelector('.pcgArrowSvg');
    arrowSvg.querySelectorAll('.pcgArrow').forEach(n=>n.remove());
    if(!target)return;
    const path=document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('class','pcgArrow');
    path.setAttribute('d',arrowPath(card,target,guideStep));
    path.setAttribute('fill','none');
    path.setAttribute('stroke','#168cff');
    path.setAttribute('stroke-width','3');
    path.setAttribute('stroke-linecap','round');
    path.setAttribute('marker-end','url(#pcgArrowHead)');
    path.setAttribute('filter','drop-shadow(0 2px 5px rgba(22,140,255,.35))');
    arrowSvg.appendChild(path);
  }

  function layoutStep(scrollTarget){
    if(!root)return;
    const data=getTargets();if(!data)return;
    const isMobile=window.matchMedia('(max-width:720px)').matches;
    root.classList.toggle('pcgMobile',isMobile);
    const item=data.targets[guideStep];
    if(scrollTarget&&isMobile){
      try{item.el.scrollIntoView({block:'center',behavior:'smooth'})}catch(e){}
      setTimeout(()=>layoutStep(false),260);
    }
    const rects=data.targets.map(x=>rectFor(x.el,x.copy.pad));
    layoutMask(rects,guideStep);
    const card=root.querySelector('.pcgMobileCard');
    updateCard(card);
    requestAnimationFrame(()=>{
      placeCard(card,item.el,data.modal,isMobile);
      requestAnimationFrame(()=>drawArrow(card,item.el));
    });
  }

  function buildRoot(){
    const el=document.createElement('div');
    el.id='pusulaCompassGuide';
    el.className='pcgStepGuide';
    el.innerHTML=`
      <div class="pcgHitPlane" aria-label="Rehberi kapat"></div>
      <svg class="pcgMaskSvg" aria-hidden="true"><defs><mask id="pcgMask"><rect width="100%" height="100%" fill="white"/></mask></defs><rect class="pcgDim" width="100%" height="100%" fill="rgba(7,15,28,.52)" mask="url(#pcgMask)"/></svg>
      <svg class="pcgArrowSvg" aria-hidden="true"><defs><marker id="pcgArrowHead" markerWidth="8" markerHeight="8" refX="6.5" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="none" stroke="#168cff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker></defs></svg>
      <div class="pcgMobileCard"><span class="pcgNum">1</span><div class="pcgTitle"></div><div class="pcgText"></div><div class="pcgMobileActions"><span class="pcgCount"></span><button type="button" class="pcgNext">İleri</button></div></div>
      <button type="button" class="pcgClose">Anladım</button>`;
    el.querySelector('.pcgHitPlane').addEventListener('click',closeGuide);
    el.querySelector('.pcgClose').addEventListener('click',closeGuide);
    el.querySelector('.pcgNext').addEventListener('click',()=>{
      if(guideStep>=COPY.length-1){closeGuide();return}
      guideStep++;
      layoutStep(true);
    });
    return el;
  }

  function layout(){
    if(!root)return;
    cancelAnimationFrame(resizeRaf);
    resizeRaf=requestAnimationFrame(()=>{
      const data=getTargets();if(!data){closeGuide();return}
      layoutStep(false);
    });
  }

  function blockScroll(e){if(root)e.preventDefault()}
  function blockKeys(e){if(!root)return;if(e.key==='Escape'){e.preventDefault();closeGuide();return}if(['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(e.key))e.preventDefault()}

  function showGuide(){
    if(shown||root)return;
    const data=getTargets();if(!data)return;
    shown=true;guideStep=0;ensureStyle();root=buildRoot();document.body.appendChild(root);document.documentElement.classList.add('pusulaCompassGuideLocked');
    window.addEventListener('resize',layout,{passive:true});window.addEventListener('orientationchange',layout,{passive:true});window.addEventListener('wheel',blockScroll,{passive:false,capture:true});window.addEventListener('touchmove',blockScroll,{passive:false,capture:true});document.addEventListener('keydown',blockKeys,true);
    layout();
  }

  function closeGuide(){
    if(!root)return;
    root.remove();root=null;document.documentElement.classList.remove('pusulaCompassGuideLocked');window.removeEventListener('resize',layout);window.removeEventListener('orientationchange',layout);window.removeEventListener('wheel',blockScroll,true);window.removeEventListener('touchmove',blockScroll,true);document.removeEventListener('keydown',blockKeys,true);
  }

  function wrapOpenIntent(){
    const fn=window.openIntent;
    if(typeof fn!=='function'||fn.__pcgWrapped)return false;
    const wrapped=function(){const out=fn.apply(this,arguments);setTimeout(showGuide,120);return out};
    wrapped.__pcgWrapped=true;window.openIntent=wrapped;return true;
  }

  function boot(){
    ensureStyle();
    if(!wrapOpenIntent()){
      let tries=0;const t=setInterval(()=>{tries++;if(wrapOpenIntent()||tries>40)clearInterval(t)},100);
    }
    const mo=new MutationObserver(()=>{if(!shown&&document.querySelector('#intentModal.show .pusulaCompassModal'))setTimeout(showGuide,80)});
    mo.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();