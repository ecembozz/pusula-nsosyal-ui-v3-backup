(function(){
  const UP='/polish.core-06a9d80c.js';
  const NAV={home:'house',notifications:'bell',messages:'message-circle',explore:'compass',game:'gamepad-2',communities:'users-round',saved:'bookmark',likes:'heart',settings:'settings'};
  const TRENDS=[
    ['TEKNOFEST','688 gönderi'],
    ['NSosyal','284 gönderi'],
    ['YapayZekâ','146 gönderi'],
    ['Sosyalİnovasyon','132 gönderi'],
    ['DijitalDönüşüm','118 gönderi']
  ];
  function injectUiFixes(){
    if(document.getElementById('pusula-ui-fixes-v5'))return;
    const style=document.createElement('style');
    style.id='pusula-ui-fixes-v5';
    style.textContent=`
html[data-theme="light"]{
  --ui-soft-surface:#f4f7fa;
  --ui-soft-surface-2:#edf3f8;
  --ui-soft-border:#dce5ed;
  --ui-badge-blue-bg:#eaf5fd;
  --ui-badge-blue-border:#cfe7f8;
  --ui-badge-blue-text:#176a9b;
  --ui-badge-green-bg:#edf8f1;
  --ui-badge-green-border:#cce8d6;
  --ui-badge-green-text:#287542;
  --ui-badge-red-bg:#fff0f1;
  --ui-badge-red-border:#f2ced2;
  --ui-badge-red-text:#a4454e;
  --ui-score-bg:#eaf5fd;
  --ui-score-text:#176a9b;
  --ui-score-classic-bg:#edf1f5;
  --ui-score-classic-text:#536173;
  --ui-status-bg:#edf2f6;
  --ui-status-text:#667388;
}
html[data-theme="light"] .stats .stat{
  background:var(--ui-soft-surface)!important;
  border-color:var(--ui-soft-border)!important;
  color:var(--text)!important;
}
html[data-theme="light"] .stats .stat b{color:var(--text)!important}
html[data-theme="light"] .stats .stat span{color:var(--muted)!important}
html[data-theme="light"] .sourceBadge{
  background:var(--ui-badge-blue-bg)!important;
  border-color:var(--ui-badge-blue-border)!important;
  color:var(--ui-badge-blue-text)!important;
}
html[data-theme="light"] .backendStatus{
  background:var(--ui-badge-green-bg)!important;
  border-color:var(--ui-badge-green-border)!important;
  color:var(--ui-badge-green-text)!important;
}
html[data-theme="light"] .backendStatus.off{
  background:var(--ui-badge-red-bg)!important;
  border-color:var(--ui-badge-red-border)!important;
  color:var(--ui-badge-red-text)!important;
}
html[data-theme="light"] .backendStatus .statusDot{
  box-shadow:none!important;
}
html[data-theme="light"] .scorePill{
  background:var(--ui-score-bg)!important;
  color:var(--ui-score-text)!important;
  border:1px solid var(--ui-badge-blue-border)!important;
}
html[data-theme="light"] .scorePill.k{
  background:var(--ui-score-classic-bg)!important;
  color:var(--ui-score-classic-text)!important;
  border-color:var(--ui-soft-border)!important;
}
html[data-theme="light"] .limit i{
  background:var(--ui-status-bg)!important;
  color:var(--ui-status-text)!important;
  border:1px solid var(--ui-soft-border)!important;
}
@media(min-width:721px){
  .postInner{
    width:100%!important;
    max-width:none!important;
    margin:0!important;
    padding:20px clamp(22px,2.2vw,36px)!important;
    box-sizing:border-box!important;
  }
  .postInner>.postMain{width:100%!important;min-width:0!important}
  .postActions{
    width:min(100%,560px)!important;
    max-width:560px!important;
    margin:8px auto 0!important;
    align-items:center!important;
    justify-content:space-evenly!important;
    gap:8px!important;
  }
  .postActions .act{
    flex:1 1 0!important;
    justify-content:center!important;
  }
  #tech-overview .flow,#tech-architecture .flow{
    display:grid!important;
    align-items:stretch!important;
    gap:10px!important;
    overflow:visible!important;
    padding-bottom:0!important;
  }
  #tech-overview .flow{grid-template-columns:repeat(5,minmax(0,1fr))!important}
  #tech-architecture .flow{grid-template-columns:repeat(6,minmax(0,1fr))!important}
  #tech-overview .flow>.arrow,#tech-architecture .flow>.arrow{display:none!important}
  #tech-overview .flowNode,#tech-architecture .flowNode{
    min-width:0!important;
    width:auto!important;
    height:100%!important;
  }
}
@media(min-width:721px) and (max-width:1100px){
  #tech-overview .flow,#tech-architecture .flow{grid-template-columns:repeat(3,minmax(0,1fr))!important}
}
`;
    document.head.appendChild(style);
  }
  injectUiFixes();
  function syncThemeControl(){
    const dark=document.documentElement.dataset.theme==='dark';
    const sw=document.getElementById('themeToggle');
    const label=document.getElementById('themeLabel');
    const btn=document.getElementById('themeBtn');
    if(sw)sw.classList.toggle('on',dark);
    if(label)label.textContent=dark?'Karanlık mod':'Açık mod';
    if(btn)btn.setAttribute('aria-pressed',dark?'true':'false');
  }
  syncThemeControl();
  function icon(name,cls){return '<i data-lucide="'+name+'" class="'+(cls||'i')+'"></i>'}
  function ensureIcon(slot,name,cls){
    if(!slot||!name)return false;
    const svg=slot.querySelector('svg.lucide');
    const pending=slot.querySelector('[data-lucide]');
    const current=(svg&&Array.from(svg.classList).find(c=>c.indexOf('lucide-')===0&&c!=='lucide'))||'';
    if(current==='lucide-'+name||pending?.getAttribute('data-lucide')===name)return false;
    const badge=slot.querySelector('.badgeDot');
    slot.innerHTML=icon(name,cls||'i');
    if(badge)slot.appendChild(badge);
    return true;
  }
  function polishTrends(){
    document.querySelectorAll('.trend').forEach(function(row,i){
      const item=TRENDS[i];if(!item)return;
      const title=row.querySelector('b'),count=row.querySelector('small');
      if(title)title.textContent=item[0];
      if(count)count.textContent=item[1];
      row.onclick=function(){if(typeof window.selectTrend==='function')window.selectTrend(item[0])};
    });
  }
  function normalize(){
    if(!window.lucide)return;
    let changed=false;
    document.querySelectorAll('.navBtn[data-page]').forEach(function(btn){
      if(btn.classList.contains('active'))return;
      changed=ensureIcon(btn.querySelector('.navIcon'),NAV[btn.dataset.page]||btn.dataset.page,'i')||changed;
    });
    changed=ensureIcon(document.querySelector('#themeBtn .navIcon'),'moon','i')||changed;
    changed=ensureIcon(document.querySelector('.navBtn[data-page="settings"] .navIcon'),'settings','i')||changed;
    document.querySelectorAll('.rightHead button').forEach(function(btn){
      if(!(btn.textContent||'').includes('Tümünü gör'))return;
      if(btn.querySelector('.lucide-chevron-right,[data-lucide="chevron-right"]'))return;
      btn.innerHTML='<span>Tümünü gör</span>'+icon('chevron-right','i sm inlineIcon');
      changed=true;
    });
    polishTrends();
    if(changed){try{lucide.createIcons({attrs:{'stroke-width':1.8}})}catch(e){}}
  }
  function settleHome(){
    const home=document.querySelector('.navBtn[data-page="home"]');if(!home)return;
    const anyActive=document.querySelector('.navBtn[data-page].active');
    if(!anyActive)home.classList.add('active');
  }
  let wrapped=false;
  let themeWrapped=false;
  function wrapTheme(){
    if(themeWrapped||typeof window.toggleTheme!=='function')return;
    const upstreamToggle=window.toggleTheme;
    window.toggleTheme=function(){
      const root=document.documentElement;
      root.classList.add('theme-switching');
      const result=upstreamToggle.apply(this,arguments);
      syncThemeControl();
      requestAnimationFrame(function(){requestAnimationFrame(function(){root.classList.remove('theme-switching')})});
      return result;
    };
    themeWrapped=true;
  }
  function finish(){
    settleHome();
    syncThemeControl();
    normalize();
    wrapTheme();
    if(!wrapped && typeof window.openPage==='function'){
      const upstreamOpenPage=window.openPage;
      window.openPage=function(p,b){const r=upstreamOpenPage(p,b);normalize();return r;};
      wrapped=true;
    }
  }
  const s=document.createElement('script');
  s.src=UP;s.async=true;
  s.onload=function(){requestAnimationFrame(finish)};
  document.head.appendChild(s);
  if(document.readyState==='complete')requestAnimationFrame(finish);
  else window.addEventListener('load',function(){requestAnimationFrame(finish)},{once:true});
})();