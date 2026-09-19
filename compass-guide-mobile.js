(function(){
  if(window.__pusulaCompassGuideMobileInstalled)return;
  window.__pusulaCompassGuideMobileInstalled=true;

  const SELECTORS=[
    '.pcIntent[data-intent="learn"]',
    '.pcArt',
    '.pcIntent[data-intent="news"]',
    '.pcCategoryRow',
    '.budgetRow',
    '[data-apply]'
  ];
  const START_BIAS=[.82,.18,.82,.64,.82,.72];
  let raf=0;

  const style=document.createElement('style');
  style.id='pusula-compass-guide-mobile-style';
  style.textContent=`
@media(max-width:720px){
  #pusulaCompassGuide.pcgMobile .pcgGlow{display:none!important}
  #pusulaCompassGuide.pcgMobile .pcgMobileCard{transition:top .16s ease,bottom .16s ease}
  #pusulaCompassGuide.pcgMobile .pcgMobileCard.pcgStableLowerCard{height:102px!important;min-height:102px!important;box-sizing:border-box!important}
}
`;
  document.head.appendChild(style);

  function clamp(n,min,max){return Math.max(min,Math.min(max,n))}

  function currentStep(root){
    const n=parseInt(root.querySelector('.pcgMobileCard .pcgNum')?.textContent||'1',10)-1;
    return clamp(Number.isFinite(n)?n:0,0,SELECTORS.length-1);
  }

  function placeCard(root,card,target,step,modal){
    if(step<3){
      card.style.top='auto';
      card.style.bottom='calc(12px + env(safe-area-inset-bottom))';
      return;
    }

    const anchor=step>=3?(modal.querySelector('.pcCategoryRow')||target):target;
    const tr=anchor.getBoundingClientRect();
    const cr=card.getBoundingClientRect();
    const gap=24;
    const top=clamp(tr.top-cr.height-gap,76,window.innerHeight-cr.height-18);
    card.style.bottom='auto';
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

    if(step===1){
      return {x:tr.left+10,y:tr.top+tr.height*.53};
    }

    if(step===3){
      const trigger=target.querySelector?.('.pcCategoryTrigger');
      const rr=trigger?.getBoundingClientRect()||tr;
      return {x:rr.left+rr.width*.70,y:rr.top-7};
    }

    if(step===4){
      const controls=budgetControlsRect(target);
      if(controls)return {x:controls.left+(controls.right-controls.left)*.70,y:controls.top-8};
      return {x:tr.left+tr.width*.68,y:tr.top-7};
    }

    if(step===5){
      return {x:tr.left+tr.width*.70,y:tr.top-7};
    }

    return null;
  }

  function arrowPath(card,target,step){
    const cr=card.getBoundingClientRect();
    const tr=target.getBoundingClientRect();
    const bias=START_BIAS[step]||.78;
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

    if(step>=3&&step<=5){
      const dy=end.y-start.y;
      const toward=dy>=0?1:-1;
      const curve=Math.min(36,Math.max(20,Math.abs(dy)*.28));
      const control={x:end.x,y:end.y-toward*curve};
      return `M ${start.x.toFixed(1)} ${start.y.toFixed(1)} Q ${control.x.toFixed(1)} ${control.y.toFixed(1)} ${end.x.toFixed(1)} ${end.y.toFixed(1)}`;
    }

    const mx=(start.x+end.x)/2,my=(start.y+end.y)/2;
    const dx=end.x-start.x,dy=end.y-start.y,len=Math.max(1,Math.hypot(dx,dy));
    const nx=-dy/len,ny=dx/len;

    let bend,dir;
    if(step===1){bend=30;dir=-1}
    else if(step===3||step===5){bend=16;dir=-1}
    else{bend=34;dir=step%2===0?1:-1}

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

    card.classList.toggle('pcgStableLowerCard',step>=3);
    placeCard(root,card,target,step,modal);
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