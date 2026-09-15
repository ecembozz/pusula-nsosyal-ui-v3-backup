(function(){
  function bootBase(){
    const s=document.createElement('script');
    s.src='/polish.base.js';
    s.async=false;
    s.onload=installTourFix;
    document.head.appendChild(s);
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
html.pusulaTourLocked,html.pusulaTourLocked body{overflow:hidden!important;overscroll-behavior:none!important}
html.pusulaTourLocked #feedBody{overflow:hidden!important;overscroll-behavior:none!important}
`;
      document.head.appendChild(st);
    }
    let raf=0;
    const align=()=>{
      cancelAnimationFrame(raf);
      raf=requestAnimationFrame(()=>{
        const root=document.getElementById('pusulaTour'),target=document.getElementById('pusulaBar'),card=root?.querySelector('.pusulaTourCard');
        if(!root||!target||!card)return;
        const r=target.getBoundingClientRect(),vw=window.innerWidth;
        const radius=Math.max(18,Math.min(24,Math.round((r.height+16)*.12)));
        root.style.setProperty('--tour-r',radius+'px');
        const lf=root.querySelector('[data-tourfog="left"]'),rf=root.querySelector('[data-tourfog="right"]');
        if(lf){lf.style.borderTopRightRadius='0px';lf.style.borderBottomRightRadius='0px'}
        if(rf){rf.style.borderTopLeftRadius='0px';rf.style.borderBottomLeftRadius='0px'}
        const desktop=window.matchMedia('(min-width:721px)').matches;
        const spotX=Math.max(8,r.left-8);
        const spotW=Math.min(vw-spotX-8,r.width+16);
        const width=desktop?spotW:Math.min(vw-24,r.width);
        const center=desktop?(spotX+spotW/2):(r.left+r.width/2);
        const left=Math.max(12,Math.min(vw-width-12,center-width/2));
        card.style.setProperty('width',Math.round(width)+'px','important');
        card.style.setProperty('max-width','none','important');
        card.style.setProperty('left',Math.round(left)+'px','important');
        card.style.setProperty('right','auto','important');
        card.style.setProperty('transform','none','important');
      });
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
      align();setTimeout(align,80);setTimeout(align,180);
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