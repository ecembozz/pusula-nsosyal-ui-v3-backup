(function(){
  function bootBase(){
    // DEMO: onboarding'i her sayfa açılışında göstermek için "bir kez göster" kaydını temizle.
    // Demo sonrası bu satırı kaldırmak yeterli; polish.base.js içindeki normal localStorage davranışı geri döner.
    try{localStorage.removeItem('pusula-onboarding-update-3')}catch(e){}
    const s=document.createElement('script');
    s.src='/polish.base.js';
    s.async=false;
    s.onload=()=>{installTourFix();scheduleCompassSelector()};
    document.head.appendChild(s);
  }
  function bootCompassCleanup(){
    if(document.querySelector('script[data-pusula-compass-cleanup]'))return;
    const s=document.createElement('script');
    s.src='/compass-cleanup.js';
    s.async=false;
    s.dataset.pusulaCompassCleanup='1';
    document.head.appendChild(s);
  }
  function bootCompassGuide(){
    if(document.querySelector('script[data-pusula-compass-guide]')){bootCompassCleanup();return}
    const s=document.createElement('script');
    s.src='/compass-guide.js';
    s.async=false;
    s.dataset.pusulaCompassGuide='1';
    s.onload=bootCompassCleanup;
    document.head.appendChild(s);
  }
  function bootCompassPngFix(){
    if(document.querySelector('script[data-pusula-compass-png-fix]')){bootCompassGuide();return}
    const s=document.createElement('script');
    s.src='/compass-png-fix.js';
    s.async=false;
    s.dataset.pusulaCompassPngFix='1';
    s.onload=bootCompassGuide;
    document.head.appendChild(s);
  }
  function bootCompassSelector(){
    if(document.querySelector('script[data-pusula-compass-selector]'))return;
    const s=document.createElement('script');
    s.src='/compass-selector.js';
    s.async=false;
    s.dataset.pusulaCompassSelector='1';
    s.onload=bootCompassPngFix;
    document.head.appendChild(s);
  }
  function scheduleCompassSelector(){
    const run=()=>setTimeout(bootCompassSelector,80);
    if(document.readyState==='complete')run();
    else window.addEventListener('load',run,{once:true});
  }
  function installTourFix(){
    if(!document.getElementById('pusula-tour-shape-fix-v4')){
      const st=document.createElement('style');
      st.id='pusula-tour-shape-fix-v4';
      st.textContent=`
.pusulaTourFog{background:rgba(7,15,28,.40)!important;backdrop-filter:blur(3px) saturate(.98)!important;-webkit-backdrop-filter:blur(3px) saturate(.98)!important}
.pusulaTourSpot{border:0!important;box-shadow:none!important;background:transparent!important}
.pusulaTourArrow path{stroke:#168cff!important;stroke-width:3!important;stroke-dasharray:none!important;stroke-linecap:round!important;stroke-linejoin:round!important;filter:drop-shadow(0 2px 5px rgba(22,140,255,.35))!important}
.pusulaTourArrow marker path{stroke:#168cff!important;stroke-width:1.8!important;stroke-linecap:round!important;stroke-linejoin:round!important;filter:none!important}
.pusulaTourFog[data-tourfog="left"],.pusulaTourFog[data-tourfog="right"]{overflow:visible!important;border-radius:0!important}
.pusulaTourFog[data-tourfog="left"]::before,.pusulaTourFog[data-tourfog="left"]::after,.pusulaTourFog[data-tourfog="right"]::before,.pusulaTourFog[data-tourfog="right"]::after{content:"";position:absolute;width:var(--tour-r,20px);height:var(--tour-r,20px);pointer-events:auto}
.pusulaTourFog[data-tourfog="left"]::before{right:calc(-1 * var(--tour-r,20px));top:0;background:radial-gradient(circle at 100% 100%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,15,28,.40) var(--tour-r,20px))}
.pusulaTourFog[data-tourfog="left"]::after{right:calc(-1 * var(--tour-r,20px));bottom:0;background:radial-gradient(circle at 100% 0%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,15,28,.40) var(--tour-r,20px))}
.pusulaTourFog[data-tourfog="right"]::before{left:calc(-1 * var(--tour-r,20px));top:0;background:radial-gradient(circle at 0% 100%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,15,28,.40) var(--tour-r,20px))}
.pusulaTourFog[data-tourfog="right"]::after{left:calc(-1 * var(--tour-r,20px));bottom:0;background:radial-gradient(circle at 0% 0%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,15,28,.40) var(--tour-r,20px))}
.pusulaTourCard{box-sizing:border-box!important}
.pusulaTourText{line-height:1.5!important}
.pusulaTourSteps{display:flex!important;align-items:center!important;justify-content:flex-start!important;gap:20px!important;margin-top:13px!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important}
.pusulaTourStep{gap:7px!important;font-size:11.5px!important;color:var(--text)!important}
.pusulaTourStep .lucide{width:17px!important;height:17px!important}
.pusulaTourStepArrow{display:none!important}
#pusulaBar .betaChip,#pusulaBar .pusulaSub,#pusulaBar .dismiss,#pusulaBar .sessionMeta{display:none!important}
#pusulaBar .pusulaRow{min-height:58px!important;padding:10px 12px!important;gap:10px!important}
#pusulaBar .compassIcon{width:34px!important;height:34px!important;border-radius:11px!important}
#pusulaBar .pusulaCopy{display:flex!important;align-items:center!important;min-width:0!important}
#pusulaBar .pusulaTitle{font-size:14px!important;line-height:1!important;gap:0!important;white-space:nowrap!important}
#pusulaBar .pusulaCta{margin-left:auto!important;height:36px!important;min-width:96px!important;padding:0 16px!important;border-radius:11px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important}
@media(min-width:721px){
  .pusulaTourCard{width:var(--tour-card-w,560px)!important;max-width:none!important;min-width:0!important}
  #pusulaCompassGuide:not(.pcgPositioned) .pcgMobileCard{opacity:0!important;visibility:hidden!important;transition:none!important}
  #pusulaCompassGuide.pcgPositioned .pcgMobileCard{opacity:1!important;visibility:visible!important}
}
@media(max-width:720px){
  .pusulaTourCard{min-width:0!important;max-width:calc(100vw - 24px)!important}
  .pusulaTourSteps{gap:14px!important;flex-wrap:wrap!important}
  #pusulaBar .pusulaRow{min-height:56px!important;padding:9px 10px!important}
  #pusulaBar .pusulaCta{height:34px!important;min-width:94px!important;padding:0 14px!important}
}
html.pusulaTourLocked,html.pusulaTourLocked body{overflow:hidden!important;overscroll-behavior:none!important}
html.pusulaTourLocked #feedBody{overflow:hidden!important;overscroll-behavior:none!important}
`;
      document.head.appendChild(st);
    }
    const align=()=>{
      const root=document.getElementById('pusulaTour'),target=document.getElementById('pusulaBar');
      if(!root||!target)return;
      const r=target.getBoundingClientRect(),vw=window.innerWidth;
      const radius=Math.max(18,Math.min(24,Math.round((r.height+16)*.12)));
      root.style.setProperty('--tour-r',radius+'px');
      const desktop=window.matchMedia('(min-width:721px)').matches;
      if(desktop){
        const x=Math.max(8,r.left-8);
        const w=Math.min(vw-x-8,r.width+16);
        root.style.setProperty('--tour-card-w',Math.round(w)+'px');
      }else{
        root.style.removeProperty('--tour-card-w');
      }
    };
    const syncIntroCopy=root=>{
      if(!root||root.dataset.copyPolished)return;
      root.dataset.copyPolished='1';
      const text=root.querySelector('.pusulaTourText');
      if(text)text.textContent='Bu oturumda ne görmek istediğini seç. Dilersen ne kadar kalacağını da belirle.';
      const labels=root.querySelectorAll('.pusulaTourStep span');
      if(labels[0])labels[0].textContent='Yönünü seç';
      if(labels[1])labels[1].textContent='Süreni belirle';
    };
    const armGuidePositionGuard=()=>{
      if(!window.matchMedia('(min-width:721px)').matches)return;
      const guide=document.getElementById('pusulaCompassGuide');
      if(!guide||guide.dataset.positionGuard)return;
      const card=guide.querySelector('.pcgMobileCard');
      if(!card)return;
      guide.dataset.positionGuard='1';
      const reveal=()=>{
        if(card.style.left&&card.style.top)guide.classList.add('pcgPositioned');
      };
      const cardObserver=new MutationObserver(reveal);
      cardObserver.observe(card,{attributes:true,attributeFilter:['style']});
      requestAnimationFrame(reveal);
    };
    const syncTourState=()=>{
      const root=document.getElementById('pusulaTour');
      document.documentElement.classList.toggle('pusulaTourLocked',!!root);
      if(root){
        syncIntroCopy(root);
        if(!root.dataset.fogDismissBound){
          root.dataset.fogDismissBound='1';
          root.querySelectorAll('.pusulaTourFog').forEach(f=>f.addEventListener('click',e=>{
            if(e.target===f)root.querySelector('.pusulaTourSkip')?.click();
          }));
        }
        align();
      }
      armGuidePositionGuard();
    };
    const blockScroll=e=>{if(document.getElementById('pusulaTour'))e.preventDefault()};
    const blockKeys=e=>{
      if(!document.getElementById('pusulaTour'))return;
      if(['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(e.key))e.preventDefault();
    };
    window.addEventListener('wheel',blockScroll,{passive:false,capture:true});
    window.addEventListener('touchmove',blockScroll,{passive:false,capture:true});
    document.addEventListener('keydown',blockKeys,true);
    const mo=new MutationObserver(syncTourState);
    mo.observe(document.body,{childList:true,subtree:true});
    window.addEventListener('resize',()=>{align();armGuidePositionGuard()},{passive:true});
    window.addEventListener('orientationchange',()=>{align();armGuidePositionGuard()},{passive:true});
    syncTourState();
  }
  bootBase();
})();