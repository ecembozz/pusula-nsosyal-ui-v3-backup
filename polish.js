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
  function settleHome(){
    const home=document.querySelector('.navBtn[data-page="home"]');if(!home)return;
    const anyActive=document.querySelector('.navBtn[data-page].active');
    if(!anyActive)home.classList.add('active');
  }
  let wrapped=false;
  function finish(){
    settleHome();
    normalize();
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