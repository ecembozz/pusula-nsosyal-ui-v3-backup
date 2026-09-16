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
  function bootCompassGuide(){
    if(document.querySelector('script[data-pusula-compass-guide]'))return;
    const s=document.createElement('script');
    s.src='/compass-guide.js';
    s.async=false;
    s.dataset.pusulaCompassGuide='1';
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
.pusulaTourFog{background:rgba(7,13,22,.28)!important;backdrop-filter:blur(3px) saturate(.97)!important;-webkit-backdrop-filter:blur(3px) saturate(.97)!important}
.pusulaTourFog[data-tourfog="left"],.pusulaTourFog[data-tourfog="right"]{overflow:visible!important;border-radius:0!important}
.pusulaTourFog[data-tourfog="left"]::before,.pusulaTourFog[data-tourfog="left"]::after,.pusulaTourFog[data-tourfog="right"]::before,.pusulaTourFog[data-tourfog="right"]::after{content:"";position:absolute;width:var(--tour-r,20px);height:var(--tour-r,20px);pointer-events:auto}
.pusulaTourFog[data-tourfog="left"]::before{right:calc(-1 * var(--tour-r,20px));top:0;background:radial-gradient(circle at 100% 100%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,13,22,.28) var(--tour-r,20px))}
.pusulaTourFog[data-tourfog="left"]::after{right:calc(-1 * var(--tour-r,20px));bottom:0;background:radial-gradient(circle at 100% 0%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,13,22,.28) var(--tour-r,20px))}
.pusulaTourFog[data-tourfog="right"]::before{left:calc(-1 * var(--tour-r,20px));top:0;background:radial-gradient(circle at 0% 100%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,13,22,.28) var(--tour-r,20px))}
.pusulaTourFog[data-tourfog="right"]::after{left:calc(-1 * var(--tour-r,20px));bottom:0;background:radial-gradient(circle at 0% 0%,transparent 0 calc(var(--tour-r,20px) - 1px),rgba(7,13,22,.28) var(--tour-r,20px))}
.pusulaTourCard{box-sizing:border-box!important}
@media(min-width:721px){
  .pusulaTourCard{width:var(--tour-card-w,560px)!important;max-width:none!important;min-width:0!important}
}
@media(max-width:720px){.pusulaTourCard{min-width:0!important;max-width:calc(100vw - 24px)!important}}
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
    const syncTourState=()=>{
      const root=document.getElementById('pusulaTour');
      document.documentElement.classList.toggle('pusulaTourLocked',!!root);
      if(!root)return;
      if(!root.dataset.fogDismissBound){
        root.dataset.fogDismissBound='1';
        root.querySelectorAll('.pusulaTourFog').forEach(f=>f.addEventListener('click',e=>{
          if(e.target===f)root.querySelector('.pusulaTourSkip')?.click();
        }));
      }
      align();
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
    window.addEventListener('resize',align,{passive:true});
    window.addEventListener('orientationchange',align,{passive:true});
    syncTourState();
  }
  bootBase();
})();