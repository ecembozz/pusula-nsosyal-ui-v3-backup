(function(){
  if(window.__pusulaCompassGuideInstalled)return;
  window.__pusulaCompassGuideInstalled=true;

  let shown=false;
  let root=null;
  let resizeRaf=0;
  let mobileStep=0;

  const COPY=[
    {title:"PUSULA’ya hoş geldin",text:"İlgi alanını seçerek akışını kişiselleştirebilirsin.",selector:'.pcIntent[data-intent="learn"]',pad:8},
    {title:"Yönünü seç",text:"Pusulayı sürükleyerek veya seçeneklerden birine dokunarak yön belirle.",selector:'.pcArt',pad:18},
    {title:"Kategoriler",text:"Öğrenmek, Eğlenmek, Haberdar olmak, Sosyalleşmek ve Sadece dolaşmak arasında seçim yap.",selector:'.pcIntent[data-intent="news"]',pad:8},
    {title:"Zaman bütçesi",text:"15 dk, 30 dk veya Sınırsız seçenekleriyle oturum süreni belirle.",selector:'.budgetRow',pad:7},
    {title:"Devam et",text:"Hazırsan Akışı düzenle ile devam et.",selector:'[data-apply]',pad:7}
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
#pusulaCompassGuide .pcgGlow{fill:none;stroke:#21a4ff;stroke-width:2.2;filter:drop-shadow(0 0 8px rgba(21,143,255,.68))}
#pusulaCompassGuide .pcgCard{position:fixed;z-index:5;width:238px;box-sizing:border-box;padding:12px 14px 12px 54px;border-radius:17px;background:rgba(255,255,255,.97);border:1px solid rgba(116,190,255,.7);box-shadow:0 14px 42px rgba(8,40,86,.22),0 0 0 1px rgba(255,255,255,.55);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);color:#10213d}
#pusulaCompassGuide .pcgNum{position:absolute;left:10px;top:10px;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#20bfe3,#2768f7);color:white;font-weight:800;font-size:18px;box-shadow:0 5px 14px rgba(36,112,246,.32)}
#pusulaCompassGuide .pcgTitle{font-size:14px;line-height:1.2;font-weight:800;letter-spacing:-.01em}
#pusulaCompassGuide .pcgText{margin-top:3px;font-size:11px;line-height:1.32;color:#5b6f8e}
#pusulaCompassGuide .pcgClose{position:fixed;right:18px;top:18px;z-index:6;border:1px solid rgba(255,255,255,.56);background:rgba(255,255,255,.9);color:#27405f;height:34px;padding:0 13px;border-radius:999px;font-weight:700;font-size:11px;box-shadow:0 8px 24px rgba(16,43,76,.12);backdrop-filter:blur(12px);cursor:pointer}
html[data-theme="dark"] #pusulaCompassGuide .pcgCard{background:rgba(23,29,40,.96);color:#f5f8fc;border-color:rgba(61,157,255,.62);box-shadow:0 16px 44px rgba(0,0,0,.34),0 0 0 1px rgba(73,167,255,.12)}
html[data-theme="dark"] #pusulaCompassGuide .pcgText{color:#a9bad0}
html[data-theme="dark"] #pusulaCompassGuide .pcgClose{background:rgba(24,31,43,.92);color:#edf5ff;border-color:rgba(93,130,166,.45)}
html.pusulaCompassGuideLocked,html.pusulaCompassGuideLocked body{overflow:hidden!important;overscroll-behavior:none!important}
html.pusulaCompassGuideLocked #intentModal .pusulaCompassModal{overscroll-behavior:none!important}
#pusulaCompassGuide.pcgMobile .pcgDesktopCards{display:none}
#pusulaCompassGuide .pcgMobileCard{display:none}
@media(max-width:720px){
 #pusulaCompassGuide .pcgClose{top:10px;right:10px;height:31px;font-size:10px;padding:0 11px}
 #pusulaCompassGuide.pcgMobile .pcgMobileCard{display:block;position:fixed;z-index:6;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));border-radius:18px;background:rgba(255,255,255,.98);border:1px solid rgba(95,179,255,.7);box-shadow:0 16px 46px rgba(7,35,75,.26);padding:13px 13px 12px 54px;color:#10213d}
 html[data-theme="dark"] #pusulaCompassGuide.pcgMobile .pcgMobileCard{background:rgba(22,28,39,.98);color:#f4f8fd}
 #pusulaCompassGuide .pcgMobileCard .pcgNum{left:10px;top:12px}
 #pusulaCompassGuide .pcgMobileActions{display:flex;justify-content:flex-end;align-items:center;gap:8px;margin-top:9px}
 #pusulaCompassGuide .pcgCount{margin-right:auto;font-size:10px;color:#72849c;font-weight:700}
 #pusulaCompassGuide .pcgNext{border:0;border-radius:999px;padding:8px 14px;background:linear-gradient(115deg,#20bed5,#3974ff);color:#fff;font-size:11px;font-weight:800;cursor:pointer}
}
`;
    document.head.appendChild(s);
  }

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

  function clamp(n,min,max){return Math.max(min,Math.min(max,n))}

  function cardPosition(i,modalRect,vw,vh){
    const w=238;
    const top=modalRect.top;
    const bottom=modalRect.bottom;
    const pos=[
      {x:modalRect.left+modalRect.width*.56,y:top+70},
      {x:Math.max(14,modalRect.left-6),y:top+300},
      {x:modalRect.right-w-12,y:top+190},
      {x:modalRect.right-w-18,y:bottom-170},
      {x:modalRect.left+modalRect.width*.43,y:bottom-88}
    ][i];
    return {x:clamp(pos.x,12,vw-w-12),y:clamp(pos.y,12,vh-88)};
  }

  function edgePoint(card,target){
    const cx=card.left+card.width/2,cy=card.top+card.height/2;
    const dx=target.cx-cx,dy=target.cy-cy;
    if(Math.abs(dx)>Math.abs(dy))return {x:dx>0?card.right:card.left,y:clamp(target.cy,card.top+12,card.bottom-12)};
    return {x:clamp(target.cx,card.left+14,card.right-14),y:dy>0?card.bottom:card.top};
  }

  function pathBetween(a,b,index){
    const mx=(a.x+b.x)/2,my=(a.y+b.y)/2;
    const bend=(index%2?1:-1)*18;
    const dx=b.x-a.x,dy=b.y-a.y,len=Math.max(1,Math.hypot(dx,dy));
    const nx=-dy/len,ny=dx/len;
    return `M ${a.x.toFixed(1)} ${a.y.toFixed(1)} Q ${(mx+nx*bend).toFixed(1)} ${(my+ny*bend).toFixed(1)} ${b.x.toFixed(1)} ${b.y.toFixed(1)}`;
  }

  function buildRoot(){
    const el=document.createElement('div');
    el.id='pusulaCompassGuide';
    el.innerHTML=`
      <div class="pcgHitPlane" aria-label="Rehberi kapat"></div>
      <svg class="pcgMaskSvg" aria-hidden="true"><defs><mask id="pcgMask"><rect width="100%" height="100%" fill="white"/></mask></defs><rect class="pcgDim" width="100%" height="100%" fill="rgba(7,15,28,.52)" mask="url(#pcgMask)"/></svg>
      <svg class="pcgArrowSvg" aria-hidden="true"><defs><marker id="pcgArrowHead" markerWidth="8" markerHeight="8" refX="6.5" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="none" stroke="#168cff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></marker></defs></svg>
      <div class="pcgDesktopCards">${COPY.map((c,i)=>`<div class="pcgCard" data-i="${i}"><span class="pcgNum">${i+1}</span><div class="pcgTitle">${c.title}</div><div class="pcgText">${c.text}</div></div>`).join('')}</div>
      <div class="pcgMobileCard"><span class="pcgNum">1</span><div class="pcgTitle"></div><div class="pcgText"></div><div class="pcgMobileActions"><span class="pcgCount"></span><button type="button" class="pcgNext">İleri</button></div></div>
      <button type="button" class="pcgClose">Anladım</button>`;
    el.querySelector('.pcgHitPlane').addEventListener('click',closeGuide);
    el.querySelector('.pcgClose').addEventListener('click',closeGuide);
    el.querySelector('.pcgNext').addEventListener('click',()=>{
      if(mobileStep>=COPY.length-1){closeGuide();return}
      mobileStep++;
      layoutMobile(true);
    });
    return el;
  }

  function layoutMask(rects,activeIndex){
    if(!root)return;
    const svg=root.querySelector('.pcgMaskSvg');
    const mask=svg.querySelector('#pcgMask');
    mask.querySelectorAll('.pcgHole').forEach(n=>n.remove());
    svg.querySelectorAll('.pcgGlow').forEach(n=>n.remove());
    rects.forEach((r,i)=>{
      if(activeIndex!=null&&i!==activeIndex)return;
      const rr=Math.min(22,Math.max(10,Math.min(r.w,r.h)*.18));
      const hole=document.createElementNS('http://www.w3.org/2000/svg','rect');
      hole.setAttribute('class','pcgHole');hole.setAttribute('x',r.x);hole.setAttribute('y',r.y);hole.setAttribute('width',r.w);hole.setAttribute('height',r.h);hole.setAttribute('rx',rr);hole.setAttribute('fill','black');mask.appendChild(hole);
      const glow=document.createElementNS('http://www.w3.org/2000/svg','rect');
      glow.setAttribute('class','pcgGlow');glow.setAttribute('x',r.x);glow.setAttribute('y',r.y);glow.setAttribute('width',r.w);glow.setAttribute('height',r.h);glow.setAttribute('rx',rr);svg.appendChild(glow);
    });
  }

  function layoutDesktop(data){
    const vw=window.innerWidth,vh=window.innerHeight,mr=data.modal.getBoundingClientRect();
    const rects=data.targets.map(t=>rectFor(t.el,t.copy.pad));
    layoutMask(rects,null);
    const arrowSvg=root.querySelector('.pcgArrowSvg');
    arrowSvg.querySelectorAll('.pcgArrow').forEach(n=>n.remove());
    root.querySelectorAll('.pcgCard').forEach((card,i)=>{
      const p=cardPosition(i,mr,vw,vh);
      card.style.left=p.x+'px';card.style.top=p.y+'px';
    });
    requestAnimationFrame(()=>{
      root.querySelectorAll('.pcgCard').forEach((card,i)=>{
        const cr=card.getBoundingClientRect(),target=rects[i];
        if(!target)return;
        const start=edgePoint(cr,target);
        const end={x:target.cx,y:target.cy};
        const path=document.createElementNS('http://www.w3.org/2000/svg','path');
        path.setAttribute('class','pcgArrow');path.setAttribute('d',pathBetween(start,end,i));path.setAttribute('fill','none');path.setAttribute('stroke','#168cff');path.setAttribute('stroke-width','3');path.setAttribute('stroke-linecap','round');path.setAttribute('marker-end','url(#pcgArrowHead)');path.setAttribute('filter','drop-shadow(0 2px 5px rgba(22,140,255,.35))');arrowSvg.appendChild(path);
      });
    });
  }

  function layoutMobile(scrollTarget){
    if(!root)return;
    const data=getTargets();if(!data)return;
    const t=data.targets[mobileStep];
    if(scrollTarget){try{t.el.scrollIntoView({block:'center',behavior:'smooth'})}catch(e){}setTimeout(()=>layoutMobile(false),260);}
    const rects=data.targets.map(x=>rectFor(x.el,x.copy.pad));
    layoutMask(rects,mobileStep);
    const card=root.querySelector('.pcgMobileCard');
    card.querySelector('.pcgNum').textContent=mobileStep+1;
    card.querySelector('.pcgTitle').textContent=COPY[mobileStep].title;
    card.querySelector('.pcgText').textContent=COPY[mobileStep].text;
    card.querySelector('.pcgCount').textContent=(mobileStep+1)+' / '+COPY.length;
    card.querySelector('.pcgNext').textContent=mobileStep===COPY.length-1?'Bitir':'İleri';
    const arrowSvg=root.querySelector('.pcgArrowSvg');arrowSvg.querySelectorAll('.pcgArrow').forEach(n=>n.remove());
    const target=rects[mobileStep];
    if(target){
      requestAnimationFrame(()=>{
        const cr=card.getBoundingClientRect(),start=edgePoint(cr,target),end={x:target.cx,y:target.cy};
        const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('class','pcgArrow');path.setAttribute('d',pathBetween(start,end,mobileStep));path.setAttribute('fill','none');path.setAttribute('stroke','#168cff');path.setAttribute('stroke-width','3');path.setAttribute('stroke-linecap','round');path.setAttribute('marker-end','url(#pcgArrowHead)');arrowSvg.appendChild(path);
      });
    }
  }

  function layout(){
    if(!root)return;
    cancelAnimationFrame(resizeRaf);
    resizeRaf=requestAnimationFrame(()=>{
      const data=getTargets();if(!data){closeGuide();return}
      const mobile=window.matchMedia('(max-width:720px)').matches;
      root.classList.toggle('pcgMobile',mobile);
      if(mobile)layoutMobile(false);else layoutDesktop(data);
    });
  }

  function blockScroll(e){if(root)e.preventDefault()}
  function blockKeys(e){if(!root)return;if(e.key==='Escape'){e.preventDefault();closeGuide();return}if(['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(e.key))e.preventDefault()}

  function showGuide(){
    if(shown||root)return;
    const data=getTargets();if(!data)return;
    shown=true;mobileStep=0;ensureStyle();root=buildRoot();document.body.appendChild(root);document.documentElement.classList.add('pusulaCompassGuideLocked');
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