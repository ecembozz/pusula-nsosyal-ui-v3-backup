(function(){
  if(window.__pusulaCompassCleanupInstalled)return;
  window.__pusulaCompassCleanupInstalled=true;

  const style=document.createElement('style');
  style.id='pusula-compass-cleanup-style';
  style.textContent=`
#intentModal .pusulaCompassModal>p,
#intentModal .pusulaCompassModal .pcCenterHint,
#intentModal .pusulaCompassModal .pcSelected,
#intentModal .pusulaCompassModal .pcFlickHint{display:none!important}
#intentModal .pusulaCompassModal .pcStage{margin-top:8px!important}
#intentModal .pusulaCompassModal .budgetRow{margin-top:2px!important}

/* Strong frosted-glass treatment so cards merge with the compass artwork. */
#intentModal .pusulaCompassModal .pcIntent{
  background:color-mix(in srgb,var(--panel) 32%,transparent)!important;
  border-color:color-mix(in srgb,var(--brand) 12%,var(--line-soft))!important;
  box-shadow:0 6px 18px rgba(21,52,84,.03)!important;
  backdrop-filter:blur(24px) saturate(1.14)!important;
  -webkit-backdrop-filter:blur(24px) saturate(1.14)!important;
}
#intentModal .pusulaCompassModal .pcIntent:hover{
  background:color-mix(in srgb,var(--panel) 38%,transparent)!important;
  border-color:color-mix(in srgb,var(--brand) 30%,var(--line-soft))!important;
  box-shadow:0 8px 22px rgba(29,126,197,.055)!important;
}
#intentModal .pusulaCompassModal .pcIntent.active{
  background:color-mix(in srgb,var(--brand) 9%,color-mix(in srgb,var(--panel) 36%,transparent))!important;
  border-color:color-mix(in srgb,var(--brand) 52%,var(--line-soft))!important;
  box-shadow:0 0 0 1px color-mix(in srgb,var(--brand) 8%,transparent),0 8px 22px rgba(31,128,206,.07)!important;
}
#intentModal .pusulaCompassModal .pcIntentIcon{
  background:color-mix(in srgb,var(--panel-2) 28%,transparent)!important;
  backdrop-filter:blur(14px) saturate(1.08)!important;
  -webkit-backdrop-filter:blur(14px) saturate(1.08)!important;
}

@media(min-width:721px){
  #intentModal .pusulaCompassModal .pcIntent{
    width:144px!important;
    min-width:144px!important;
    max-width:144px!important;
    height:52px!important;
    min-height:52px!important;
    box-sizing:border-box!important;
    padding:8px 10px!important;
    gap:8px!important;
    border-radius:15px!important;
  }
  #intentModal .pusulaCompassModal .pcIntentCopy{
    min-width:0!important;
    display:flex!important;
    align-items:center!important;
    min-height:31px!important;
  }
  #intentModal .pusulaCompassModal .pcIntentCopy b{
    font-size:11px!important;
    line-height:1.18!important;
  }
  #intentModal .pusulaCompassModal .pcIntentCopy span{display:none!important}
  #intentModal .pusulaCompassModal .pcIntent[data-intent="learn"]{
    left:50%!important;
    top:2px!important;
    transform:translateX(-50%)!important;
  }
  #intentModal .pusulaCompassModal .pcIntent[data-intent="learn"]:hover{
    transform:translateX(-50%) translateY(-2px)!important;
  }
  #intentModal .pusulaCompassModal .pcIntent[data-intent="fun"]{
    left:28px!important;
    top:116px!important;
  }
  #intentModal .pusulaCompassModal .pcIntent[data-intent="news"]{
    right:28px!important;
    top:116px!important;
  }
  #intentModal .pusulaCompassModal .pcIntent[data-intent="social"]{
    left:56px!important;
    bottom:28px!important;
  }
  #intentModal .pusulaCompassModal .pcIntent[data-intent="wander"]{
    right:56px!important;
    bottom:28px!important;
  }
}
`;
  document.head.appendChild(style);

  function clean(){
    const box=document.querySelector('#intentModal .pusulaCompassModal');
    if(!box)return;
    const h=box.querySelector('h2');
    if(h&&h.textContent!=='PUSULA yönünü seç')h.textContent='PUSULA yönünü seç';
  }

  function bootGuideDesktop(){
    if(document.querySelector('script[data-pusula-compass-guide-desktop]'))return;
    const s=document.createElement('script');
    s.src='/compass-guide-desktop.js';
    s.async=false;
    s.dataset.pusulaCompassGuideDesktop='1';
    document.head.appendChild(s);
  }

  function bootGuideMobile(){
    if(document.querySelector('script[data-pusula-compass-guide-mobile]')){bootGuideDesktop();return}
    const s=document.createElement('script');
    s.src='/compass-guide-mobile.js';
    s.async=false;
    s.dataset.pusulaCompassGuideMobile='1';
    s.onload=bootGuideDesktop;
    document.head.appendChild(s);
  }

  function bootBudget(){
    if(document.querySelector('script[data-pusula-compass-budget]')){bootGuideMobile();return}
    const s=document.createElement('script');
    s.src='/compass-budget.js';
    s.async=false;
    s.dataset.pusulaCompassBudget='1';
    s.onload=bootGuideMobile;
    document.head.appendChild(s);
  }

  const mo=new MutationObserver(clean);
  mo.observe(document.body,{childList:true,subtree:true});
  clean();
  bootBudget();
})();