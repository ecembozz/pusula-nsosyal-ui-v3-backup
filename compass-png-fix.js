(function(){
  if(document.getElementById('pusula-compass-original-png-fix'))return;
  const st=document.createElement('style');
  st.id='pusula-compass-original-png-fix';
  st.textContent=`
/* Original user-provided PNG assets. No sprite/WebP conversion. */
.pcCompassBody{
  position:absolute!important;
  inset:0!important;
  background-image:url('/assets/pusula/light.png')!important;
  background-repeat:no-repeat!important;
  background-position:center!important;
  background-size:100% 100%!important;
  image-rendering:auto!important;
  transform-origin:49.45% 43.55%!important;
  transform:scale(1.34)!important;
}
html[data-theme="dark"] .pcCompassBody{
  background-image:url('/assets/pusula/dark.png')!important;
}

/* The rotating node itself is the real compass pivot. The PNG is centered on it. */
.pcNeedle{
  position:absolute!important;
  inset:auto!important;
  left:49.45%!important;
  top:43.55%!important;
  width:0!important;
  height:0!important;
  background:none!important;
  transform-origin:0 0!important;
  will-change:transform!important;
  filter:none!important;
  overflow:visible!important;
}
.pcNeedle::before{
  content:"";
  position:absolute;
  left:0;
  top:0;
  width:252px;
  height:252px;
  transform:translate(-50%,-50%);
  transform-origin:50% 50%;
  background-image:url('/assets/pusula/neddle-light.png');
  background-repeat:no-repeat;
  background-position:center;
  background-size:100% 100%;
  filter:drop-shadow(0 5px 7px rgba(13,61,118,.18));
  pointer-events:none;
}
html[data-theme="dark"] .pcNeedle::before{
  background-image:url('/assets/pusula/neddle-dark.png');
}

/* Pointer math and visual rotation share exactly the same physical center. */
.pcDialHit{
  left:49.45%!important;
  top:43.55%!important;
}

@media(max-width:720px){
  .pcNeedle::before{width:201px;height:201px}
}
@media(max-width:390px){
  .pcNeedle::before{width:185px;height:185px}
}
`;
  document.head.appendChild(st);
})();