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

/* Real frosted glass: almost-clear fill + backdrop contrast, so pale artwork still reads through. */
#intentModal .pusulaCompassModal .pcIntent{
  background:rgba(232,244,255,.10)!important;
  border-color:rgba(57,145,220,.18)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.34),0 6px 18px rgba(21,52,84,.028)!important;
  backdrop-filter:blur(26px) saturate(1.35) brightness(.96)!important;
  -webkit-backdrop-filter:blur(26px) saturate(1.35) brightness(.96)!important;
}
#intentModal .pusulaCompassModal .pcIntent:hover{
  background:rgba(232,244,255,.16)!important;
  border-color:rgba(46,143,226,.28)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.4),0 8px 22px rgba(29,126,197,.05)!important;
}
#intentModal .pusulaCompassModal .pcIntent.active{
  background:rgba(75,166,255,.13)!important;
  border-color:rgba(35,145,238,.58)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.38),0 0 0 1px rgba(39,149,243,.07),0 8px 22px rgba(31,128,206,.06)!important;
}
#intentModal .pusulaCompassModal .pcIntentIcon{
  background:rgba(224,241,255,.14)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.28)!important;
  backdrop-filter:blur(16px) saturate(1.28) brightness(.97)!important;
  -webkit-backdrop-filter:blur(16px) saturate(1.28) brightness(.97)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntent{
  background:rgba(15,28,46,.16)!important;
  border-color:rgba(92,170,241,.20)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.055),0 7px 20px rgba(0,0,0,.08)!important;
  backdrop-filter:blur(26px) saturate(1.22) brightness(1.10)!important;
  -webkit-backdrop-filter:blur(26px) saturate(1.22) brightness(1.10)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntent:hover{
  background:rgba(20,37,60,.24)!important;
  border-color:rgba(91,181,255,.34)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntent.active{
  background:rgba(28,102,177,.22)!important;
  border-color:rgba(71,172,255,.62)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntentIcon{
  background:rgba(28,57,88,.20)!important;
  backdrop-filter:blur(16px) saturate(1.18) brightness(1.08)!important;
  -webkit-backdrop-filter:blur(16px) saturate(1.18) brightness(1.08)!important;
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