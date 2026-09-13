(function(){
  const UP='/polish.core-06a9d80c.js';
  const NAV={home:'house',notifications:'bell',messages:'message-circle',explore:'compass',game:'gamepad-2',communities:'users-round',saved:'bookmark',likes:'heart',settings:'settings'};
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
    if(changed){try{lucide.createIcons({attrs:{'stroke-width':1.8}})}catch(e){}}
  }
  function ensurePostFlex(){
    if(document.getElementById('post-flex-v2'))return;
    const style=document.createElement('style');
    style.id='post-flex-v2';
    style.textContent=`
      .post{
        display:flex!important;
        grid-template-columns:none!important;
        align-items:flex-start!important;
        gap:14px!important;
        padding-top:20px!important;
        padding-bottom:20px!important;
        padding-left:max(28px,calc((100% - 840px)/2))!important;
        padding-right:max(28px,calc((100% - 840px)/2))!important;
      }
      .post>.avatar{
        grid-column:auto!important;
        grid-row:auto!important;
        flex:0 0 41px!important;
      }
      .post>.postMain{
        grid-column:auto!important;
        grid-row:auto!important;
        flex:1 1 auto!important;
        min-width:0!important;
      }
      @media(max-width:720px){
        .post{
          gap:12px!important;
          padding:18px 16px!important;
        }
        .post>.avatar{
          flex-basis:38px!important;
          width:38px!important;
          height:38px!important;
        }
      }
    `;
    document.head.appendChild(style);
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
      requestAnimationFrame(function(){requestAnimationFrame(function(){root.classList.remove('theme-switching')})});
      return result;
    };
    themeWrapped=true;
  }
  function finish(){
    ensurePostFlex();
    settleHome();
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