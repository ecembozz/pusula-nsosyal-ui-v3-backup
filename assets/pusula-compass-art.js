(function(){
  const ASSET='/assets/pusula-compass-sprite.png.b64';
  let cache=null;
  async function load(){
    if(cache)return cache;
    const r=await fetch(ASSET,{cache:'force-cache'});
    if(!r.ok)throw new Error('PUSULA PNG asset yüklenemedi');
    const b64=(await r.text()).trim();
    if(!b64||b64==='PLACEHOLDER')throw new Error('PUSULA PNG asset hazır değil');
    cache='data:image/png;base64,'+b64;
    document.documentElement.style.setProperty('--pc-png-sprite','url("'+cache+'")');
    return cache;
  }
  const st=document.createElement('style');
  st.id='pusula-compass-png-art-fix';
  st.textContent=`
.pcCompassBody,.pcNeedle{background-image:var(--pc-png-sprite,none)!important;background-size:200% 200%!important;background-repeat:no-repeat!important;image-rendering:auto!important}
.pcCompassBody{background-position:left top!important}
.pcNeedle{inset:auto!important;width:100%!important;height:100%!important;left:-.69%!important;top:-7.32%!important;background-position:left bottom!important;transform-origin:50% 50%!important;will-change:transform!important}
.pcDialHit{left:49.31%!important;top:42.68%!important}
html[data-theme="dark"] .pcCompassBody{background-position:right top!important}
html[data-theme="dark"] .pcNeedle{left:-.38%!important;top:-6.70%!important;background-position:right bottom!important}
html[data-theme="dark"] .pcDialHit{left:49.62%!important;top:43.30%!important}
`;
  document.head.appendChild(st);
  window.__pusulaCompassPngReady=load();
})();