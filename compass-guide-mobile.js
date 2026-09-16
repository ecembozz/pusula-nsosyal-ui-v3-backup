(function(){
  if(window.__pusulaCompassGuideMobileInstalled)return;
  window.__pusulaCompassGuideMobileInstalled=true;

  const SELECTORS=[
    '.pcIntent[data-intent="learn"]',
    '.pcArt',
    '.pcIntent[data-intent="news"]',
    '.budgetRow',
    '[data-apply]'
  ];
  const START_BIAS=[.82,.18,.82,.76,.82];
  let raf=0;

  const style=document.createElement('style');
  style.id='pusula-compass-guide-mobile-style';
  style.textContent=`
@media(max-width:720px){
  #pusulaCompassGuide.pcgMobile .pcgGlow{display:none!important}
  #pusulaCompassGuide.pcgMobile .pcgMobileCard{transition:top .16s ease,bottom .16s ease}
}
`;
  document.head.appendChild(style);

  function clamp(n,min,max){return Math.max(min,Math.min(max,n))}

  function currentStep(root){
    const n=parseInt(root.querySelector('.pcgMobileCard .pcgNum')?.textContent||'1',10)-1;
    return clamp(Number.isFinite(n)?n:0,0,SELECTORS.length-1);
  }

  function placeCard(root,card,target,step){
    if(step<3){
      card.style.top='auto';
      card.style.bottom='calc(12px + env(safe-area-inset-bottom))';
      return;
    }
    const tr=target.getBoundingClientRect();
    const cr=card.getBoundingClientRect();
    const top=clamp(tr.top-cr.height-24,76,window.innerHeight-cr.height-18);
    card.style.bottom='auto';
    card.style.top=Math.round(top)+'px';
  }

  function arrowPath(card,target,step){
    const cr=card.getBoundingClientRect();
    const tr=target.getBoundingClientRect();
    const bias=START_BIAS[step]||.78;
    let start,end;

    if(cr.bottom<=tr.top){
      start={x:cr.left+cr.width*bias,y:cr.bottom+8};
      end={x:clamp(tr.left+tr.width/2,tr.left+10,tr.right-10),y:tr.top-8};
    }else if(cr.top>=tr.bottom){
      start={x:cr.left+cr.width*bias,y:cr.top-8};
      end={x:clamp(tr.left+tr.width/2,tr.left+10,tr.right-10),y:tr.bottom+8};
    }else if(tr.left>=cr.right){
      start={x:cr.right+8,y:cr.top+cr.height*.26};
      end={x:tr.left-8,y:clamp(tr.top+tr.height/2,tr.top+8,tr.bottom-8)};
    }else{
      start={x:cr.left-8,y:cr.top+cr.height*.26};
      end={x:tr.right+8,y:clamp(tr.top+tr.height/2,tr.top+8,tr.bottom-8)};
    }

    const mx=(start.x+end.x)/2,my=(start.y+end.y)/2;
    const dir=step%2===0?1:-1;
    const dx=end.x-start.x,dy=end.y-start.y,len=Math.max(1,Math.hypot(dx,dy));
    const nx=-dy/len,ny=dx/len;
    const bend=step>=3?22:34;
    return `M ${start.x.toFixed(1)} ${start.y.toFixed(1)} Q ${(mx+nx*bend*dir).toFixed(1)} ${(my+ny*bend*dir).toFixed(1)} ${end.x.toFixed(1)} ${end.y.toFixed(1)}`;
  }

  function fix(){
    raf=0;
    if(!matchMedia('(max-width:720px)').matches)return;
    const root=document.getElementById('pusulaCompassGuide');
    if(!root||!root.classList.contains('pcgMobile'))return;
    const modal=document.querySelector('#intentModal.show .pusulaCompassModal');
    const card=root.querySelector('.pcgMobileCard');
    if(!modal||!card)return;
    const step=currentStep(root);
    const target=modal.querySelector(SELECTORS[step]);
    if(!target)return;

    placeCard(root,card,target,step);
    requestAnimationFrame(()=>{
      const arrow=root.querySelector('.pcgArrowSvg .pcgArrow');
      if(!arrow)return;
      const d=arrowPath(card,target,step);
      if(arrow.getAttribute('d')!==d)arrow.setAttribute('d',d);
    });
  }

  function schedule(){
    if(raf)return;
    raf=requestAnimationFrame(fix);
  }

  const mo=new MutationObserver(schedule);
  mo.observe(document.body,{childList:true,subtree:true});
  document.addEventListener('click',e=>{
    if(e.target.closest?.('#pusulaCompassGuide .pcgNext')){
      setTimeout(schedule,40);
      setTimeout(schedule,300);
    }
  },true);
  window.addEventListener('resize',schedule,{passive:true});
  window.addEventListener('orientationchange',()=>setTimeout(schedule,120),{passive:true});
  schedule();
})();