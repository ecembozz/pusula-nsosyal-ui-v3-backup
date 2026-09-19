(function(){
  if(window.__pusulaCompassGuideDesktopPolishInstalled)return;
  window.__pusulaCompassGuideDesktopPolishInstalled=true;

  const style=document.createElement('style');
  style.id='pusula-compass-guide-desktop-style';
  style.textContent=`
@media(min-width:721px){
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard{
    width:min(500px,calc(100vw - 72px))!important;
    max-width:500px!important;
    min-width:440px!important;
    padding:16px 18px 16px 62px!important;
    border-radius:20px!important;
    box-sizing:border-box!important;
    overflow:hidden!important;
  }
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard.pcgDesktopUpperStable{
    height:126px!important;
    min-height:126px!important;
  }
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard.pcgDesktopLowerStable{
    height:116px!important;
    min-height:116px!important;
  }
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard .pcgNum{
    left:12px!important;
    top:14px!important;
    width:38px!important;
    height:38px!important;
    font-size:18px!important;
  }
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard .pcgTitle{
    font-size:15px!important;
    line-height:1.2!important;
  }
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard .pcgText{
    margin-top:4px!important;
    font-size:12px!important;
    line-height:1.38!important;
    padding-right:6px!important;
  }
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard .pcgMobileActions{
    position:absolute!important;
    left:62px!important;
    right:16px!important;
    bottom:13px!important;
    margin:0!important;
    display:flex!important;
    align-items:center!important;
    gap:10px!important;
  }
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard .pcgNext{
    flex:0 0 auto!important;
    min-width:58px!important;
    padding:9px 16px!important;
  }
}
@media(min-width:721px) and (max-width:860px){
  #pusulaCompassGuide:not(.pcgMobile) .pcgMobileCard{
    width:calc(100vw - 48px)!important;
    min-width:0!important;
    max-width:500px!important;
  }
}
`;
  document.head.appendChild(style);

  let raf=0;

  function fixLowerArrow(root,card,step){
    if(step<4||step>6)return;
    const arrow=root.querySelector('.pcgArrowSvg .pcgArrow');
    const modal=document.querySelector('#intentModal.show .pusulaCompassModal');
    if(!arrow||!modal)return;

    let end=null;
    if(step===4){
      const trigger=modal.querySelector('.pcCategoryTrigger');
      if(!trigger)return;
      const r=trigger.getBoundingClientRect();
      end={x:r.left+r.width*.72,y:r.top-7};
    }else if(step===5){
      const row=modal.querySelector('.budgetRow');
      if(!row)return;
      const controls=[...row.querySelectorAll('[data-modalbudget],.pcCustomBudget')].filter(el=>{
        const r=el.getBoundingClientRect();return r.width&&r.height;
      });
      if(!controls.length)return;
      const rects=controls.map(el=>el.getBoundingClientRect());
      const left=Math.min(...rects.map(r=>r.left));
      const right=Math.max(...rects.map(r=>r.right));
      const top=Math.min(...rects.map(r=>r.top));
      end={x:left+(right-left)*.72,y:top-8};
    }else{
      const apply=modal.querySelector('[data-apply]');
      if(!apply)return;
      const r=apply.getBoundingClientRect();
      end={x:r.left+r.width*.72,y:r.top-7};
    }

    const cr=card.getBoundingClientRect();
    const start={x:cr.right+8,y:cr.top+cr.height*.68};
    const vertical=Math.max(30,(end.y-start.y)*.58);
    const c1={x:start.x,y:start.y+vertical};
    const c2={x:end.x+38,y:end.y-8};
    const d=`M ${start.x.toFixed(1)} ${start.y.toFixed(1)} C ${c1.x.toFixed(1)} ${c1.y.toFixed(1)} ${c2.x.toFixed(1)} ${c2.y.toFixed(1)} ${end.x.toFixed(1)} ${end.y.toFixed(1)}`;
    if(arrow.getAttribute('d')!==d)arrow.setAttribute('d',d);
  }

  function sync(){
    raf=0;
    if(!matchMedia('(min-width:721px)').matches)return;
    const root=document.getElementById('pusulaCompassGuide');
    const card=root?.querySelector('.pcgMobileCard');
    if(!root||!card||root.classList.contains('pcgMobile'))return;
    const step=Math.max(1,Math.min(6,parseInt(card.querySelector('.pcgNum')?.textContent||'1',10)||1));
    const upper=step<=3;
    const changed=card.classList.contains('pcgDesktopUpperStable')!==upper;
    card.classList.toggle('pcgDesktopUpperStable',upper);
    card.classList.toggle('pcgDesktopLowerStable',!upper);
    if(changed)requestAnimationFrame(()=>window.dispatchEvent(new Event('resize')));
    requestAnimationFrame(()=>fixLowerArrow(root,card,step));
  }
  function schedule(){if(raf)return;raf=requestAnimationFrame(sync)}

  const mo=new MutationObserver(schedule);
  mo.observe(document.body,{childList:true,subtree:true,characterData:true});
  document.addEventListener('click',e=>{
    if(e.target.closest?.('#pusulaCompassGuide .pcgNext')){
      setTimeout(schedule,30);
      setTimeout(()=>window.dispatchEvent(new Event('resize')),80);
    }
  },true);
  window.addEventListener('resize',schedule,{passive:true});
  schedule();
})();