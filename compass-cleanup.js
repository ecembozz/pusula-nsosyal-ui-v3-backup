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

/* Passive cards: almost clear, low blur so the compass artwork remains visible. */
#intentModal .pusulaCompassModal .pcIntent{
  background:rgba(255,255,255,.025)!important;
  border:0!important;
  box-shadow:0 5px 16px rgba(21,52,84,.035)!important;
  backdrop-filter:blur(6px)!important;
  -webkit-backdrop-filter:blur(6px)!important;
}
#intentModal .pusulaCompassModal .pcIntent:hover{
  background:rgba(255,255,255,.055)!important;
  border:0!important;
  box-shadow:0 8px 20px rgba(29,126,197,.06)!important;
  backdrop-filter:blur(8px)!important;
  -webkit-backdrop-filter:blur(8px)!important;
}
/* Active choice: blue frosted glass, no outline. */
#intentModal .pusulaCompassModal .pcIntent.active{
  background:rgba(48,151,255,.18)!important;
  border:0!important;
  box-shadow:0 10px 26px rgba(31,128,206,.16),inset 0 1px 0 rgba(255,255,255,.22)!important;
  backdrop-filter:blur(16px)!important;
  -webkit-backdrop-filter:blur(16px)!important;
}
#intentModal .pusulaCompassModal .pcIntentIcon{
  background:rgba(255,255,255,.04)!important;
  box-shadow:none!important;
  backdrop-filter:blur(5px)!important;
  -webkit-backdrop-filter:blur(5px)!important;
}
#intentModal .pusulaCompassModal .pcIntent.active .pcIntentIcon{
  background:rgba(255,255,255,.16)!important;
  backdrop-filter:blur(12px)!important;
  -webkit-backdrop-filter:blur(12px)!important;
}

html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntent{
  background:rgba(8,14,24,.035)!important;
  border:0!important;
  box-shadow:0 6px 18px rgba(0,0,0,.08)!important;
  backdrop-filter:blur(6px)!important;
  -webkit-backdrop-filter:blur(6px)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntent:hover{
  background:rgba(8,14,24,.075)!important;
  border:0!important;
  backdrop-filter:blur(8px)!important;
  -webkit-backdrop-filter:blur(8px)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntent.active{
  background:rgba(32,126,225,.24)!important;
  border:0!important;
  box-shadow:0 10px 28px rgba(0,92,190,.22),inset 0 1px 0 rgba(255,255,255,.08)!important;
  backdrop-filter:blur(16px)!important;
  -webkit-backdrop-filter:blur(16px)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntentIcon{
  background:rgba(8,14,24,.05)!important;
  backdrop-filter:blur(5px)!important;
  -webkit-backdrop-filter:blur(5px)!important;
}
html[data-theme="dark"] #intentModal .pusulaCompassModal .pcIntent.active .pcIntentIcon{
  background:rgba(255,255,255,.08)!important;
  backdrop-filter:blur(12px)!important;
  -webkit-backdrop-filter:blur(12px)!important;
}

/* Session feedback cards follow the active theme. */
html[data-theme="light"] #sessionModal .mood{
  background:var(--panel-2,#f5f7fa)!important;
  border-color:var(--line-soft,#dce5ed)!important;
  color:var(--text,#182335)!important;
  box-shadow:0 4px 14px rgba(20,46,74,.05)!important;
}
html[data-theme="light"] #sessionModal .mood:hover{
  background:#eef6ff!important;
  border-color:#b9dcf5!important;
}
html[data-theme="light"] #sessionModal .mood.active{
  background:#e4f3ff!important;
  border-color:#2da8ff!important;
  box-shadow:0 0 0 2px rgba(45,168,255,.12),0 8px 20px rgba(33,131,204,.10)!important;
}

/* Time-complete screen: product copy + compact, useful session facts. */
#sessionModal .sessionPause h2{margin-bottom:6px!important}
#sessionModal .sessionPause>p{margin:0!important;max-width:48ch!important;color:var(--muted,#667388)!important}
#sessionModal .sessionFacts{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;
  margin:18px 0 16px!important;
}
#sessionModal .sessionFact{
  min-width:0!important;
  padding:13px 14px!important;
  border:1px solid var(--line-soft,var(--line,#dce5ed))!important;
  border-radius:14px!important;
  background:var(--panel-2,#f5f7fa)!important;
  box-shadow:none!important;
}
#sessionModal .sessionFact span{
  display:block!important;
  margin-bottom:4px!important;
  color:var(--muted,#667388)!important;
  font-size:10.5px!important;
  line-height:1.25!important;
  font-weight:500!important;
}
#sessionModal .sessionFact b{
  display:block!important;
  color:var(--text,#182335)!important;
  font-size:14px!important;
  line-height:1.3!important;
  font-weight:600!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
}
#sessionModal .sessionPause .modalFooter{margin-top:0!important}
html[data-theme="dark"] #sessionModal .sessionFact{
  background:var(--panel-2,#20242b)!important;
  border-color:var(--line-soft,#2b3139)!important;
}
@media(max-width:420px){
  #sessionModal .sessionFacts{gap:8px!important}
  #sessionModal .sessionFact{padding:12px!important}
  #sessionModal .sessionFact b{font-size:13px!important}
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

  function elapsedLabel(){
    if(typeof S!=='undefined'&&S.budget)return S.budget+' dk';
    const start=Number(typeof G!=='undefined'&&G?G.st:0);
    if(!start)return '—';
    const seconds=Math.max(0,Math.floor((Date.now()-start)/1000));
    if(seconds<60)return Math.max(1,seconds)+' sn';
    return Math.max(1,Math.round(seconds/60))+' dk';
  }

  function polishSessionPause(){
    if(typeof window.showSession!=='function'||window.__pusulaSessionPausePolished)return;
    const baseShowSession=window.showSession;
    window.__pusulaSessionPausePolished=true;
    window.showSession=function(s='pause'){
      if(s!=='pause')return baseShowSession(s);
      const overlay=document.getElementById('sessionModal');
      const content=document.getElementById('session');
      if(!overlay||!content)return baseShowSession(s);
      overlay.classList.add('show');
      const hasState=typeof S!=='undefined';
      const hasIntents=typeof I!=='undefined';
      const intent=hasState&&hasIntents&&S.intent&&I[S.intent]
        ?String(I[S.intent].label||I[S.intent].short||'').replace(/^Sadece\s+/i,'')
        :'Standart';
      const timed=hasState&&!!S.budget;
      content.innerHTML=`<div class="sessionPause"><h2>${timed?'Süren doldu':'Oturumu bitirmek ister misin?'}</h2><p>${timed?'Seçtiğin süre sona erdi. İstersen biraz daha devam edebilirsin.':'İstersen oturuma devam edebilir veya oturumu burada tamamlayabilirsin.'}</p><div class="sessionFacts"><div class="sessionFact"><span>Niyet</span><b>${intent}</b></div><div class="sessionFact"><span>Geçirilen süre</span><b>${elapsedLabel()}</b></div></div><div class="modalFooter"><button class="secondary" onclick="sessionModal.classList.remove('show')">Devam et</button><button class="primary" onclick="showSession('mood')">Oturumu bitir</button></div></div>`;
    };
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

  const mo=new MutationObserver(()=>{clean();polishSessionPause()});
  mo.observe(document.body,{childList:true,subtree:true});
  clean();
  polishSessionPause();
  bootBudget();
})();