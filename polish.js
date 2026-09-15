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
  const MOBILE_MENU=[
    ['notifications','Bildirimler','bell'],['messages','Mesajlar','message-circle'],['explore','Keşfet','compass'],['game','Nod Oyna','gamepad-2'],
    ['communities','Topluluklar','users-round'],['saved','Kaydedilenler','bookmark'],['likes','Beğeniler','heart'],['settings','Ayarlar','settings']
  ];
  const MOBILE_TECH=[
    ['overview','Genel bakış','layout-dashboard'],
    ['compare','Canlı karşılaştırma','columns-2'],
    ['math','Matematik & skor','sigma'],
    ['experiment','Deney sonuçları','table-2'],
    ['architecture','Mimari & doğrulama','workflow']
  ];

  function injectUiFixes(){
    if(document.getElementById('pusula-ui-fixes-v5'))return;
    const style=document.createElement('style');
    style.id='pusula-ui-fixes-v5';
    style.textContent=`
html[data-theme="light"]{
  --ui-soft-surface:#f4f7fa;--ui-soft-surface-2:#edf3f8;--ui-soft-border:#dce5ed;
  --ui-badge-blue-bg:#eaf5fd;--ui-badge-blue-border:#cfe7f8;--ui-badge-blue-text:#176a9b;
  --ui-badge-green-bg:#edf8f1;--ui-badge-green-border:#cce8d6;--ui-badge-green-text:#287542;
  --ui-badge-red-bg:#fff0f1;--ui-badge-red-border:#f2ced2;--ui-badge-red-text:#a4454e;
  --ui-score-bg:#eaf5fd;--ui-score-text:#176a9b;--ui-score-classic-bg:#edf1f5;--ui-score-classic-text:#536173;
  --ui-status-bg:#edf2f6;--ui-status-text:#667388;
}
html[data-theme="light"] .stats .stat{background:var(--ui-soft-surface)!important;border-color:var(--ui-soft-border)!important;color:var(--text)!important}
html[data-theme="light"] .stats .stat b{color:var(--text)!important}
html[data-theme="light"] .stats .stat span{color:var(--muted)!important}
html[data-theme="light"] .sourceBadge{background:var(--ui-badge-blue-bg)!important;border-color:var(--ui-badge-blue-border)!important;color:var(--ui-badge-blue-text)!important}
html[data-theme="light"] .backendStatus{background:var(--ui-badge-green-bg)!important;border-color:var(--ui-badge-green-border)!important;color:var(--ui-badge-green-text)!important}
html[data-theme="light"] .backendStatus.off{background:var(--ui-badge-red-bg)!important;border-color:var(--ui-badge-red-border)!important;color:var(--ui-badge-red-text)!important}
html[data-theme="light"] .backendStatus .statusDot{box-shadow:none!important}
html[data-theme="light"] .scorePill{background:var(--ui-score-bg)!important;color:var(--ui-score-text)!important;border:1px solid var(--ui-badge-blue-border)!important}
html[data-theme="light"] .scorePill.k{background:var(--ui-score-classic-bg)!important;color:var(--ui-score-classic-text)!important;border-color:var(--ui-soft-border)!important}
html[data-theme="light"] .limit i{background:var(--ui-status-bg)!important;color:var(--ui-status-text)!important;border:1px solid var(--ui-soft-border)!important}
@media(max-width:720px){
  html[data-theme="light"] .main,html[data-theme="light"] .feedBody,html[data-theme="light"] #posts{background:var(--panel)!important}
  html[data-theme="light"] .modalFooter{background:var(--panel)!important}
  body{padding-bottom:calc(70px + env(safe-area-inset-bottom))!important}
  .demoTools{display:none!important}
  .mobileDock{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:80!important;display:grid!important;grid-template-columns:repeat(4,1fr)!important;gap:3px!important;padding:6px 8px calc(6px + env(safe-area-inset-bottom))!important;border-top:1px solid var(--line-soft)!important;background:color-mix(in srgb,var(--panel) 94%,transparent)!important;backdrop-filter:blur(18px) saturate(1.15)!important;-webkit-backdrop-filter:blur(18px) saturate(1.15)!important;box-shadow:0 -10px 28px rgba(14,35,55,.08)!important}
  .mobileDockBtn{height:50px!important;border:0!important;border-radius:12px!important;background:transparent!important;color:var(--muted)!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:3px!important;font-size:10px!important;font-weight:600!important;line-height:1!important;touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important;transition:transform .08s ease,background .12s ease,color .12s ease!important}
  .mobileDockBtn:active{transform:scale(.95)!important}
  .mobileDockBtn .lucide,.mobileDockBtn>[data-lucide]{width:21px!important;height:21px!important}
  .mobileDockBtn.active{color:var(--brand)!important;background:color-mix(in srgb,var(--brand) 9%,transparent)!important}
  .mobileNavOverlay{align-items:flex-end!important;padding:0!important}
  .mobileNavOverlay .modal{width:100%!important;max-height:82vh!important;border-radius:20px 20px 0 0!important;border-bottom:0!important;padding-bottom:calc(18px + env(safe-area-inset-bottom))!important;overscroll-behavior:contain!important}
  .mobilePanelHead{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:10px!important;margin-bottom:12px!important}
  .mobilePanelHead h2{margin:0!important}
  .mobilePanelClose{width:36px!important;height:36px!important;border:0!important;border-radius:10px!important;background:var(--panel-2)!important;color:var(--muted)!important;display:grid!important;place-items:center!important;touch-action:manipulation!important}
  .mobileNavGrid{display:grid!important;grid-template-columns:1fr 1fr!important;gap:8px!important}
  .mobileNavItem,.mobileTrendItem,.mobileJuryAction{border:0!important;border-radius:12px!important;background:var(--panel-2)!important;color:var(--text)!important;min-height:48px!important;padding:10px 12px!important;display:flex!important;align-items:center!important;gap:9px!important;text-align:left!important;font-weight:600!important;touch-action:manipulation!important}
  .mobileNavItem .lucide,.mobileJuryAction .lucide{width:18px!important;height:18px!important;color:var(--brand)!important;flex:none!important}
  .mobileThemeItem{grid-column:1/-1!important}.mobileThemeItem small{margin-left:auto!important;color:var(--muted)!important;font-weight:500!important}
  .mobileTrendList{display:grid!important;gap:7px!important}.mobileTrendItem{display:grid!important;grid-template-columns:30px 1fr auto!important}.mobileTrendItem .hash{font-size:24px!important}.mobileTrendItem small{display:block!important;color:var(--muted)!important;font-size:10px!important;margin-top:2px!important}
  .mobileJuryState{padding:11px 12px!important;border-radius:12px!important;background:var(--jury-surface)!important;margin-bottom:9px!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:10px!important}
  .mobileJuryState small{display:block!important;color:var(--muted)!important;margin-top:2px!important}
  .mobileJuryToggle{height:34px!important;min-width:80px!important;border:0!important;border-radius:999px!important;background:var(--panel-3)!important;color:var(--text)!important;font-weight:700!important;touch-action:manipulation!important;transition:.12s ease!important}
  .mobileJuryToggle.on{background:var(--brand)!important;color:#fff!important}
  .mobileModeGrid{display:grid!important;grid-template-columns:1fr 1fr!important;gap:8px!important;margin-bottom:8px!important}
  .mobileModeBtn{height:38px!important;border:0!important;border-radius:10px!important;background:var(--panel-2)!important;color:var(--muted)!important;font-weight:650!important;touch-action:manipulation!important;transition:.12s ease!important}
  .mobileModeBtn.active{background:var(--nav-icon-bg)!important;color:var(--brand)!important}
  .mobileModeBtn.busy{opacity:.65!important}
  .mobileJuryActions{display:grid!important;gap:8px!important}
  .mobileJuryAction.primaryMobile{background:var(--brand)!important;color:#fff!important}.mobileJuryAction.primaryMobile .lucide{color:#fff!important}
  .mobileTechSection{margin-top:14px!important;padding-top:12px!important;border-top:1px solid var(--line-soft)!important}
  .mobileTechTitle{display:flex!important;align-items:end!important;justify-content:space-between!important;gap:12px!important;margin:0 2px 8px!important}.mobileTechTitle b{font-size:13px!important}.mobileTechTitle small{color:var(--muted)!important;font-size:10px!important}
  .mobileTechAccordion{display:grid!important;gap:7px!important}
  .mobileTechItem{border:1px solid var(--line-soft)!important;border-radius:12px!important;background:var(--panel-2)!important;overflow:hidden!important}
  .mobileTechAccordionBtn{width:100%!important;min-height:48px!important;border:0!important;background:transparent!important;color:var(--text)!important;padding:10px 12px!important;display:grid!important;grid-template-columns:22px 1fr 20px!important;align-items:center!important;gap:9px!important;text-align:left!important;font-weight:700!important;touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important}
  .mobileTechAccordionBtn>.lucide:first-child{width:18px!important;height:18px!important;color:var(--brand)!important}.mobileTechAccordionBtn>.lucide:last-child{width:17px!important;height:17px!important;color:var(--muted)!important;transition:transform .16s ease!important}
  .mobileTechAccordionBtn.open>.lucide:last-child{transform:rotate(180deg)!important}
  .mobileTechBody{padding:0 10px 11px!important;border-top:1px solid var(--line-soft)!important;background:var(--panel)!important;overflow-x:hidden!important}
  .mobileTechBody[hidden]{display:none!important}
  .mobileTechBody .techGrid{grid-template-columns:1fr!important;gap:8px!important;margin-top:10px!important}.mobileTechBody .span4,.mobileTechBody .span5,.mobileTechBody .span6,.mobileTechBody .span7,.mobileTechBody .span8,.mobileTechBody .span12{grid-column:1/-1!important}
  .mobileTechBody .techCard{padding:12px!important}.mobileTechBody .compareCols{grid-template-columns:1fr!important}.mobileTechBody .flow{grid-template-columns:1fr!important}.mobileTechBody .arrow{display:none!important}.mobileTechBody .sourceBadge,.mobileTechBody .backendStatus{margin-top:10px!important}.mobileTechBody .expTable{min-width:720px!important}
  .mobileTechLoading{padding:14px 4px!important;color:var(--muted)!important;font-size:11px!important}
}
@media(min-width:721px){.mobileDock,.mobileNavOverlay{display:none!important}}
@media(min-width:721px){
  .postInner{width:100%!important;max-width:none!important;margin:0!important;padding:20px clamp(22px,2.2vw,36px)!important;box-sizing:border-box!important}
  .postInner>.postMain{width:100%!important;min-width:0!important}
  .postActions{width:min(100%,560px)!important;max-width:560px!important;margin:8px auto 0!important;align-items:center!important;justify-content:space-evenly!important;gap:8px!important}
  .postActions .act{flex:1 1 0!important;justify-content:center!important}
  #tech-overview .flow,#tech-architecture .flow{display:grid!important;align-items:stretch!important;gap:10px!important;overflow:visible!important;padding-bottom:0!important}
  #tech-overview .flow{grid-template-columns:repeat(5,minmax(0,1fr))!important}#tech-architecture .flow{grid-template-columns:repeat(6,minmax(0,1fr))!important}
  #tech-overview .flow>.arrow,#tech-architecture .flow>.arrow{display:none!important}
  #tech-overview .flowNode,#tech-architecture .flowNode{min-width:0!important;width:auto!important;height:100%!important}
}
@media(min-width:721px) and (max-width:1100px){#tech-overview .flow,#tech-architecture .flow{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
`;
    document.head.appendChild(style);
  }
  injectUiFixes();

  function syncThemeControl(){
    const dark=document.documentElement.dataset.theme==='dark';
    const sw=document.getElementById('themeToggle'),label=document.getElementById('themeLabel'),btn=document.getElementById('themeBtn');
    if(sw)sw.classList.toggle('on',dark);if(label)label.textContent=dark?'Karanlık mod':'Açık mod';if(btn)btn.setAttribute('aria-pressed',dark?'true':'false');
    const ml=document.getElementById('mobileThemeLabel');if(ml)ml.textContent=dark?'Karanlık mod':'Açık mod';
  }
  syncThemeControl();

  function icon(name,cls){return '<i data-lucide="'+name+'" class="'+(cls||'i')+'"></i>'}
  function ensureIcon(slot,name,cls){
    if(!slot||!name)return false;
    const svg=slot.querySelector('svg.lucide'),pending=slot.querySelector('[data-lucide]');
    const current=(svg&&Array.from(svg.classList).find(c=>c.indexOf('lucide-')===0&&c!=='lucide'))||'';
    if(current==='lucide-'+name||pending?.getAttribute('data-lucide')===name)return false;
    const badge=slot.querySelector('.badgeDot');slot.innerHTML=icon(name,cls||'i');if(badge)slot.appendChild(badge);return true;
  }
  function paintIcons(){if(window.lucide)try{lucide.createIcons({attrs:{'stroke-width':1.8}})}catch(e){}}
  function polishTrends(){
    document.querySelectorAll('.trend').forEach(function(row,i){const item=TRENDS[i];if(!item)return;const title=row.querySelector('b'),count=row.querySelector('small');if(title)title.textContent=item[0];if(count)count.textContent=item[1];row.onclick=function(){if(typeof window.selectTrend==='function')window.selectTrend(item[0])};});
  }

  function mobileActive(k){document.querySelectorAll('.mobileDockBtn').forEach(b=>b.classList.toggle('active',b.dataset.mobile===k))}
  function mobileClose(){document.getElementById('mobileNavOverlay')?.classList.remove('show');mobileActive('feed')}
  function mobileHead(t){return '<div class="modalGrab"></div><div class="mobilePanelHead"><h2>'+t+'</h2><button class="mobilePanelClose" type="button" data-mclose>'+icon('x','i')+'</button></div>'}
  function mobileMenu(){
    const d=document.documentElement.dataset.theme==='dark';
    return mobileHead('Menü')+'<button class="mobileJuryAction primaryMobile" type="button" data-mcompose>'+icon('send-horizontal','i')+'<span>Yeni Gönderi</span></button><div class="mobileNavGrid" style="margin-top:8px">'+MOBILE_MENU.map(x=>'<button class="mobileNavItem" type="button" data-mpage="'+x[0]+'">'+icon(x[2],'i')+'<span>'+x[1]+'</span></button>').join('')+'<button class="mobileNavItem mobileThemeItem" id="mobileThemeBtn" type="button">'+icon(d?'sun':'moon','i')+'<span>Tema</span><small id="mobileThemeLabel">'+(d?'Karanlık mod':'Açık mod')+'</small></button></div>';
  }
  function mobilePopular(){return mobileHead('Popüler')+'<div class="mobileTrendList">'+TRENDS.map(x=>'<button class="mobileTrendItem" type="button" data-mtrend="'+x[0]+'"><span class="hash">#</span><span><b>'+x[0]+'</b><small>'+x[1]+'</small></span>'+icon('chevron-right','i')+'</button>').join('')+'</div>'}
  function mobileTechAccordion(){
    return '<div class="mobileTechSection"><div class="mobileTechTitle"><b>Teknik Merkez</b><small>Başlığa dokunarak aç / kapat</small></div><div class="mobileTechAccordion">'+MOBILE_TECH.map(x=>'<div class="mobileTechItem"><button type="button" class="mobileTechAccordionBtn" data-mtech="'+x[0]+'">'+icon(x[2],'i')+'<span>'+x[1]+'</span>'+icon('chevron-down','i')+'</button><div class="mobileTechBody" data-mtechbody="'+x[0]+'" hidden></div></div>').join('')+'</div></div>';
  }
  function mobileJury(){
    const st=typeof S!=='undefined'?S:null,j=!!st?.jury,m=st?.mode||'classic';
    return mobileHead('Jüri')+'<div class="mobileJuryState"><span><b>Jüri görünümü</b><small data-mjurysub>'+(j?'Teknik kontroller açık':'Kullanıcı görünümü açık')+'</small></span><button class="mobileJuryToggle '+(j?'on':'')+'" type="button" data-mjury>'+(j?'Açık':'Kapalı')+'</button></div><div class="mobileModeGrid"><button class="mobileModeBtn '+(m==='classic'?'active':'')+'" data-mmode="classic">Klasik</button><button class="mobileModeBtn '+(m==='pusula'?'active':'')+'" data-mmode="pusula">PUSULA</button></div><div class="mobileJuryActions"><button class="mobileJuryAction" data-mintent>'+icon('compass','i')+'<span>Yön / niyet seç</span></button><button class="mobileJuryAction" data-msession>'+icon('clock','i')+'<span>Oturum sonunu göster</span></button></div>'+mobileTechAccordion();
  }
  function syncMobileJuryState(){
    const q=document.getElementById('mobileNavModal');if(!q)return;
    const st=typeof S!=='undefined'?S:null,j=!!st?.jury,m=st?.mode||'classic';
    const toggle=q.querySelector('[data-mjury]'),sub=q.querySelector('[data-mjurysub]');
    if(toggle){toggle.classList.toggle('on',j);toggle.textContent=j?'Açık':'Kapalı'}if(sub)sub.textContent=j?'Teknik kontroller açık':'Kullanıcı görünümü açık';
    q.querySelectorAll('[data-mmode]').forEach(b=>b.classList.toggle('active',b.dataset.mmode===m));
  }
  function renderMobileTech(name,body){
    if(!body)return;
    try{if(typeof window.renderTech==='function')window.renderTech(name)}catch(e){}
    const source=document.getElementById('tech-'+name);
    body.innerHTML=source&&source.innerHTML?source.innerHTML:'<div class="mobileTechLoading">Teknik içerik hazırlanamadı.</div>';
  }
  function refreshOpenMobileTech(){
    const btn=document.querySelector('.mobileTechAccordionBtn.open');if(!btn)return;
    renderMobileTech(btn.dataset.mtech,document.querySelector('[data-mtechbody="'+btn.dataset.mtech+'"]'));
  }
  let mobileTechWarm=false;
  function warmMobileTech(){
    if(mobileTechWarm)return;mobileTechWarm=true;
    try{const p=typeof window.syncBackend==='function'?window.syncBackend():null;if(p&&typeof p.then==='function')p.then(refreshOpenMobileTech).catch(()=>{})}catch(e){}
  }
  function toggleMobileTech(btn){
    const name=btn.dataset.mtech,body=document.querySelector('[data-mtechbody="'+name+'"]'),wasOpen=btn.classList.contains('open');
    document.querySelectorAll('.mobileTechAccordionBtn.open').forEach(b=>b.classList.remove('open'));
    document.querySelectorAll('.mobileTechBody').forEach(b=>b.hidden=true);
    if(wasOpen)return;
    btn.classList.add('open');body.hidden=false;body.innerHTML='<div class="mobileTechLoading">İçerik hazırlanıyor…</div>';
    requestAnimationFrame(()=>renderMobileTech(name,body));
  }

  function mobileBind(t){
    const q=document.getElementById('mobileNavModal');if(!q)return;
    q.querySelector('[data-mclose]')?.addEventListener('click',mobileClose);
    if(t==='menu'){
      q.querySelector('[data-mcompose]')?.addEventListener('click',()=>{mobileClose();window.focusComposer?.()});
      q.querySelectorAll('[data-mpage]').forEach(b=>b.onclick=()=>{const p=b.dataset.mpage,d=document.querySelector('.navBtn[data-page="'+p+'"]');mobileClose();window.openPage?.(p,d)});
      q.querySelector('#mobileThemeBtn')?.addEventListener('click',()=>{window.toggleTheme?.();requestAnimationFrame(()=>{q.innerHTML=mobileMenu();mobileBind('menu');paintIcons()})});
    }
    if(t==='popular')q.querySelectorAll('[data-mtrend]').forEach(b=>b.onclick=()=>{mobileClose();window.selectTrend?.(b.dataset.mtrend);window.scrollTo({top:0,behavior:'smooth'})});
    if(t==='jury'){
      q.querySelector('[data-mjury]')?.addEventListener('click',()=>{window.toggleJury?.();syncMobileJuryState()});
      q.querySelectorAll('[data-mmode]').forEach(b=>b.onclick=()=>{
        const mode=b.dataset.mmode;q.querySelectorAll('[data-mmode]').forEach(x=>{x.classList.toggle('active',x===b);x.classList.toggle('busy',x===b)});
        Promise.resolve(window.setMode?.(mode)).finally(()=>{q.querySelectorAll('[data-mmode]').forEach(x=>x.classList.remove('busy'));syncMobileJuryState();refreshOpenMobileTech()});
      });
      q.querySelector('[data-mintent]')?.addEventListener('click',()=>{mobileClose();window.openIntent?.()});
      q.querySelector('[data-msession]')?.addEventListener('click',()=>{mobileClose();window.showSession?.()});
      q.querySelectorAll('[data-mtech]').forEach(b=>b.addEventListener('click',()=>toggleMobileTech(b)));
      setTimeout(warmMobileTech,60);
    }
  }
  function mobileOpen(t){
    if(!matchMedia('(max-width:720px)').matches)return;
    const o=document.getElementById('mobileNavOverlay'),q=document.getElementById('mobileNavModal');if(!o||!q)return;
    mobileActive(t);q.innerHTML=t==='menu'?mobileMenu():t==='popular'?mobilePopular():mobileJury();mobileBind(t);o.classList.add('show');paintIcons();
  }
  function ensureMobileNav(){
    if(document.getElementById('mobileDock'))return;
    const n=document.createElement('nav');n.id='mobileDock';n.className='mobileDock';n.setAttribute('aria-label','Mobil gezinme');
    n.innerHTML='<button class="mobileDockBtn" data-mobile="menu">'+icon('menu','i')+'<span>Menü</span></button><button class="mobileDockBtn active" data-mobile="feed">'+icon('house','i')+'<span>Akış</span></button><button class="mobileDockBtn" data-mobile="popular">'+icon('hash','i')+'<span>Popüler</span></button><button class="mobileDockBtn" data-mobile="jury">'+icon('settings','i')+'<span>Jüri</span></button>';
    const o=document.createElement('div');o.id='mobileNavOverlay';o.className='overlay mobileNavOverlay';o.innerHTML='<div class="modal" id="mobileNavModal"></div>';document.body.append(n,o);
    const menu=n.querySelector('[data-mobile="menu"]'),feed=n.querySelector('[data-mobile="feed"]'),popular=n.querySelector('[data-mobile="popular"]'),jury=n.querySelector('[data-mobile="jury"]');
    menu.onclick=()=>mobileOpen('menu');feed.onclick=()=>{mobileClose();window.scrollTo({top:0,behavior:'smooth'})};popular.onclick=()=>mobileOpen('popular');jury.onclick=()=>mobileOpen('jury');
    [menu,popular,jury].forEach(b=>b.addEventListener('pointerdown',()=>mobileActive(b.dataset.mobile),{passive:true}));
    o.onclick=e=>{if(e.target===o)mobileClose()};document.addEventListener('keydown',e=>{if(e.key==='Escape'&&o.classList.contains('show'))mobileClose()});paintIcons();
  }

  function normalize(){
    if(!window.lucide)return;let changed=false;
    document.querySelectorAll('.navBtn[data-page]').forEach(btn=>{if(btn.classList.contains('active'))return;changed=ensureIcon(btn.querySelector('.navIcon'),NAV[btn.dataset.page]||btn.dataset.page,'i')||changed});
    changed=ensureIcon(document.querySelector('#themeBtn .navIcon'),'moon','i')||changed;changed=ensureIcon(document.querySelector('.navBtn[data-page="settings"] .navIcon'),'settings','i')||changed;
    document.querySelectorAll('.rightHead button').forEach(btn=>{if(!(btn.textContent||'').includes('Tümünü gör'))return;if(btn.querySelector('.lucide-chevron-right,[data-lucide="chevron-right"]'))return;btn.innerHTML='<span>Tümünü gör</span>'+icon('chevron-right','i sm inlineIcon');changed=true});
    polishTrends();if(changed)paintIcons();
  }
  function settleHome(){const home=document.querySelector('.navBtn[data-page="home"]');if(!home)return;if(!document.querySelector('.navBtn[data-page].active'))home.classList.add('active')}
  let wrapped=false,themeWrapped=false;
  function wrapTheme(){
    if(themeWrapped||typeof window.toggleTheme!=='function')return;const upstreamToggle=window.toggleTheme;
    window.toggleTheme=function(){const root=document.documentElement;root.classList.add('theme-switching');const result=upstreamToggle.apply(this,arguments);syncThemeControl();requestAnimationFrame(()=>requestAnimationFrame(()=>root.classList.remove('theme-switching')));return result};themeWrapped=true;
  }
  function finish(){
    settleHome();syncThemeControl();normalize();wrapTheme();ensureMobileNav();
    if(!wrapped&&typeof window.openPage==='function'){const upstreamOpenPage=window.openPage;window.openPage=function(p,b){const r=upstreamOpenPage(p,b);normalize();return r};wrapped=true}
  }
  const s=document.createElement('script');s.src=UP;s.async=true;s.onload=()=>requestAnimationFrame(finish);document.head.appendChild(s);
  if(document.readyState==='complete')requestAnimationFrame(finish);else window.addEventListener('load',()=>requestAnimationFrame(finish),{once:true});
})();