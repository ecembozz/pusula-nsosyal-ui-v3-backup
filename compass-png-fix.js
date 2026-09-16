(function(){
  if(document.getElementById('pusula-compass-original-png-fix'))return;
  const st=document.createElement('style');
  st.id='pusula-compass-original-png-fix';
  st.textContent=`
/* Original user-provided PNG assets. No sprite/WebP conversion. */
:root{--pc-compass-y:14px}
.pcCompassBody{
  position:absolute!important;
  inset:0!important;
  background-image:url('/assets/pusula/light.png')!important;
  background-repeat:no-repeat!important;
  background-position:center!important;
  background-size:100% 100%!important;
  image-rendering:auto!important;
  transform-origin:49.45% 43.55%!important;
  transform:translateY(var(--pc-compass-y)) scale(1.40)!important;
}
html[data-theme="dark"] .pcCompassBody{
  background-image:url('/assets/pusula/dark.png')!important;
}

/* The rotating node itself is the real compass pivot. The PNG is centered on it. */
.pcNeedle{
  position:absolute!important;
  inset:auto!important;
  left:49.45%!important;
  top:calc(43.55% + var(--pc-compass-y))!important;
  width:0!important;
  height:0!important;
  background:none!important;
  transform-origin:0 0!important;
  will-change:transform!important;
  backface-visibility:hidden!important;
  -webkit-backface-visibility:hidden!important;
  filter:none!important;
  overflow:visible!important;
}
.pcNeedle::before{
  content:"";
  position:absolute;
  left:0;
  top:0;
  width:150px;
  height:150px;
  transform:translate(-50%,-50%);
  transform-origin:50% 50%;
  background-image:url('/assets/pusula/neddle-light.png');
  background-repeat:no-repeat;
  background-position:center;
  background-size:100% 100%;
  filter:drop-shadow(0 4px 6px rgba(13,61,118,.16));
  pointer-events:none;
}
html[data-theme="dark"] .pcNeedle::before{
  background-image:url('/assets/pusula/neddle-dark.png');
}

/* Pointer math and visual rotation share exactly the same physical center. */
.pcDialHit{
  left:49.45%!important;
  top:calc(43.55% + var(--pc-compass-y))!important;
}

/* Interaction performance: avoid expensive repaint work while the needle is moving. */
.pcStage.dragging .pcArt,.pcStage.spinning .pcArt{filter:none!important}
.pcStage.dragging .pcNeedle::before,.pcStage.spinning .pcNeedle::before{filter:none!important}
.pcStage.dragging .pcIntent,.pcStage.spinning .pcIntent,
.pcStage.dragging .pcIntentIcon,.pcStage.spinning .pcIntentIcon{
  backdrop-filter:none!important;
  -webkit-backdrop-filter:none!important;
}
.pcStage.spinning .pcDialHit{cursor:default!important}

/* Reduced-motion must not leave the UI waiting with no visible response. Keep only the essential compass feedback. */
@media(prefers-reduced-motion:reduce){
  .pcStage.spinning .pcNeedle{transition:transform 1.85s cubic-bezier(.12,.74,.18,1)!important}
}

@media(max-width:720px){
  :root{--pc-compass-y:10px}
  .pcNeedle::before{width:120px;height:120px}
}
@media(max-width:390px){
  .pcNeedle::before{width:110px;height:110px}
}
`;
  document.head.appendChild(st);

  /* High-polling mice and some touch stacks can emit several pointermove events per frame.
     Let the selector process at most one move per animation frame; the visual result stays
     responsive while avoiding repeated layout/style work that cannot be displayed anyway. */
  function bindMoveThrottle(hit){
    if(!hit||hit.dataset.pcMoveThrottle)return;
    hit.dataset.pcMoveThrottle='1';
    let frameOpen=true;
    hit.addEventListener('pointermove',e=>{
      if(frameOpen){
        frameOpen=false;
        requestAnimationFrame(()=>{frameOpen=true});
        return;
      }
      e.stopImmediatePropagation();
    },true);
  }
  function scanHits(){
    document.querySelectorAll('#intentModal .pcDialHit').forEach(bindMoveThrottle);
  }
  const mo=new MutationObserver(scanHits);
  mo.observe(document.body,{childList:true,subtree:true});
  scanHits();
})();