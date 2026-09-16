(function(){
  if(window.__pusulaCompassBudgetInstalled)return;
  window.__pusulaCompassBudgetInstalled=true;

  const style=document.createElement('style');
  style.id='pusula-compass-budget-style';
  style.textContent=`
#intentModal .pusulaCompassModal .budgetRow{display:flex!important;align-items:center!important;gap:8px!important;flex-wrap:wrap!important}
#intentModal .pusulaCompassModal .budgetRow>b{margin-right:auto!important}
.pcCustomBudget{height:34px;display:inline-flex;align-items:center;gap:4px;padding:0 10px;border:1px solid var(--line-soft);border-radius:999px;background:var(--panel-2);color:var(--muted);transition:border-color .16s ease,box-shadow .16s ease,background .16s ease}
.pcCustomBudget:focus-within,.pcCustomBudget.active{border-color:color-mix(in srgb,var(--brand) 72%,var(--line-soft));box-shadow:0 0 0 2px color-mix(in srgb,var(--brand) 10%,transparent);background:color-mix(in srgb,var(--brand) 5%,var(--panel-2))}
.pcCustomBudget input{width:48px;min-width:0;border:0!important;outline:0!important;background:transparent!important;color:var(--text)!important;font:inherit;font-size:11px;font-weight:700;text-align:right;padding:0!important;box-shadow:none!important;-moz-appearance:textfield}
.pcCustomBudget input::-webkit-outer-spin-button,.pcCustomBudget input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.pcCustomBudget input::placeholder{color:var(--muted);opacity:.5}
.pcCustomBudget span{font-size:10px;color:var(--muted);font-weight:600;pointer-events:none}
@media(max-width:720px){
 #intentModal .pusulaCompassModal .budgetRow{gap:7px!important;width:100%!important}
 #intentModal .pusulaCompassModal .budgetRow>b{flex:1 0 100%;margin:0 0 3px!important}
 #intentModal .pusulaCompassModal .budgetRow>[data-modalbudget],
 #intentModal .pusulaCompassModal .budgetRow>.pcCustomBudget{
   flex:1 1 0!important;
   min-width:0!important;
   width:auto!important;
   justify-content:center!important;
   box-sizing:border-box!important;
   margin:0!important;
 }
 #intentModal .pusulaCompassModal .budgetRow>[data-modalbudget]{padding-left:6px!important;padding-right:6px!important}
 .pcCustomBudget{height:32px;padding:0 7px!important;gap:3px!important}
 .pcCustomBudget input{width:28px!important;font-size:10.5px;text-align:center}
 .pcCustomBudget span{font-size:9.5px}
}
`;
  document.head.appendChild(style);

  function chooseUnlimited(row,input,custom){
    S.modalBudget=0;
    input.value='';
    custom.classList.remove('active');
    row.querySelectorAll('[data-modalbudget]').forEach(b=>b.classList.toggle('active',+b.dataset.modalbudget===0));
  }

  function enhance(reset){
    const box=document.querySelector('#intentModal .pusulaCompassModal');
    const row=box?.querySelector('.budgetRow');
    if(!row)return;

    const title=row.querySelector('b');
    title?.querySelector('span')?.remove();

    let custom=row.querySelector('.pcCustomBudget');
    if(!custom){
      custom=document.createElement('label');
      custom.className='pcCustomBudget';
      custom.setAttribute('aria-label','Özel zaman bütçesi');
      custom.innerHTML='<input class="pcCustomBudgetInput" type="number" min="1" step="1" inputmode="numeric" placeholder="45" aria-label="Dakika"><span>dk</span>';
      row.appendChild(custom);

      const input=custom.querySelector('input');
      input.addEventListener('keydown',e=>{
        if(['-','+','e','E','.',','].includes(e.key))e.preventDefault();
      });
      input.addEventListener('input',()=>{
        const raw=input.value.trim();
        if(!raw){chooseUnlimited(row,input,custom);return}
        const n=Math.floor(Number(raw));
        if(!Number.isFinite(n)||n<1){input.value='';chooseUnlimited(row,input,custom);return}
        input.value=String(n);
        S.modalBudget=n;
        row.querySelectorAll('[data-modalbudget]').forEach(b=>b.classList.remove('active'));
        custom.classList.add('active');
      });
      row.querySelectorAll('[data-modalbudget]').forEach(btn=>btn.addEventListener('click',()=>{
        input.value='';
        custom.classList.remove('active');
      }));
    }

    const input=custom.querySelector('input');
    if(reset)chooseUnlimited(row,input,custom);
  }

  function wrapOpenIntent(){
    const fn=window.openIntent;
    if(typeof fn!=='function'||fn.__pcBudgetWrapped)return false;
    const wrapped=function(){
      const out=fn.apply(this,arguments);
      setTimeout(()=>enhance(true),0);
      return out;
    };
    wrapped.__pcBudgetWrapped=true;
    window.openIntent=wrapped;
    return true;
  }

  function boot(){
    if(!wrapOpenIntent()){
      let tries=0;
      const timer=setInterval(()=>{tries++;if(wrapOpenIntent()||tries>40)clearInterval(timer)},100);
    }
    const mo=new MutationObserver(()=>enhance(false));
    mo.observe(document.body,{childList:true,subtree:true});
    enhance(false);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
  else boot();
})();