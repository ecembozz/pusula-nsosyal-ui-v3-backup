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

  function fixBudgetArrow(root,card,step){
    if(step!==4)return;
    const arrow=root.querySelector('.pcgArrowSvg .pcgArrow');
    const row=document.querySelector('#intentModal.show .pusulaCompassModal .budgetRow');
    if(!arrow||!row)return;
    const controls=[...row.querySelectorAll('[data-modalbudget],.pcCustomBudget')].filter(el=>{
      const r=el.getBoundingClientRect();return r.width&&r.height;
    });
    if(!controls.length)return;

    const rects=controls.map(el=>el.getBoundingClientRect());
    const left=Math.min(...rects.map(r=>r.left));
    const right=Math.max(...rects.map(r=>r.right));
    const top=Math.min(...rects.map(r=>r.top));
    const cr=card.getBoundingClientRect();

    /* Desktop step 4: descend on the right, then make one soft left turn.
       Keeping the final control point to the right of the target guarantees
       that the arrow head approaches the budget controls from right to left. */
    const end={x:left+(right-left)*.52,y:top-8};
    const preferredStart=Math.max(cr.left+cr.width*.82,end.x+72);
    const start={x:Math.min(cr.right-18,preferredStart),y:cr.bottom+8};
    const c1={x:start.x+2,y:start.y+34};
    const c2={x:Math.min(start.x-16,end.x+46),y:end.y};
    const d=`M ${start.x.toFixed(1)} ${start.y.toFixed(1)} C ${c1.x.toFixed(1)} ${c1.y.toFixed(1)} ${c2.x.toFixed(1)} ${c2.y.toFixed(1)} ${end.x.toFixed(1)} ${end.y.toFixed(1)}`;
    if(arrow.getAttribute('d')!==d)arrow.setAttribute('d',d);
  }

  function sync(){
    raf=0;
    if(!matchMedia('(min-width:721px)').matches)return;
    const root=document.getElementById('pusulaCompassGuide');
    const card=root?.querySelector('.pcgMobileCard');
    if(!root||!card||root.classList.contains('pcgMobile'))return;
    const step=Math.max(1,Math.min(5,parseInt(card.querySelector('.pcgNum')?.textContent||'1',10)||1));
    const upper=step<=3;
    const changed=card.classList.contains('pcgDesktopUpperStable')!==upper;
    card.classList.toggle('pcgDesktopUpperStable',upper);
    card.classList.toggle('pcgDesktopLowerStable',!upper);
    if(changed)requestAnimationFrame(()=>window.dispatchEvent(new Event('resize')));
    requestAnimationFrame(()=>fixBudgetArrow(root,card,step));
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