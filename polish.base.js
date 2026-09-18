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
    ['models','Model karşılaştırması','brain-circuit'],
    ['compare','Canlı karşılaştırma','columns-2'],
    ['math','Matematik & skor','sigma'],
    ['experiment','Deney sonuçları','table-2'],
    ['architecture','Mimari & doğrulama','workflow']
  ];
  const TOUR_KEY='pusula-onboarding-update-3';

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
html[data-theme="light"] .calcLine{border-bottom-color:var(--ui-soft-border)!important}
.pusulaTour{position:fixed;inset:0;z-index:170;pointer-events:none}
.pusulaTourFog{position:fixed;z-index:1;background:rgba(7,13,22,.34);backdrop-filter:blur(4px) saturate(.94);-webkit-backdrop-filter:blur(4px) saturate(.94);pointer-events:auto}
.pusulaTourSpot{position:fixed;z-index:2;border:1.5px dashed color-mix(in srgb,var(--brand) 75%,#fff 25%);border-radius:20px;box-shadow:0 0 0 1px color-mix(in srgb,var(--brand) 18%,transparent),0 0 28px color-mix(in srgb,var(--brand) 16%,transparent),0 14px 38px rgba(16,69,118,.14);pointer-events:auto;cursor:pointer}
.pusulaTourCard{position:fixed;z-index:4;width:min(470px,calc(100vw - 30px));overflow:hidden;border:1px solid color-mix(in srgb,var(--line-soft) 78%,var(--brand) 22%);border-radius:25px;background:var(--panel);color:var(--text);box-shadow:0 32px 90px rgba(7,20,34,.28);pointer-events:auto}
.pusulaTourVisual{position:relative;height:190px;overflow:hidden;display:flex;align-items:center;justify-content:center;background:linear-gradient(155deg,color-mix(in srgb,var(--brand) 12%,var(--panel)) 0%,color-mix(in srgb,#22c7dc 13%,var(--panel)) 45%,color-mix(in srgb,#496cff 13%,var(--panel)) 100%)}
.pusulaTourVisual:before{content:"";position:absolute;inset:-20px;background:linear-gradient(31deg,transparent 44%,color-mix(in srgb,var(--brand) 13%,transparent) 45%,color-mix(in srgb,var(--brand) 13%,transparent) 47%,transparent 48%),linear-gradient(143deg,transparent 53%,color-mix(in srgb,#2fc6df 12%,transparent) 54%,color-mix(in srgb,#2fc6df 12%,transparent) 56%,transparent 57%);background-size:92px 92px,128px 128px;opacity:.72;transform:rotate(-6deg)}
.pusulaTourVisual:after{content:"";position:absolute;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,color-mix(in srgb,var(--brand) 18%,transparent),transparent 68%);filter:blur(2px)}
.pusulaTourKicker{position:absolute;left:20px;top:18px;z-index:2;display:inline-flex;align-items:center;gap:6px;padding:6px 9px;border:1px solid color-mix(in srgb,var(--brand) 22%,transparent);border-radius:999px;background:color-mix(in srgb,var(--panel) 84%,transparent);color:var(--brand);font-size:10px;font-weight:850;letter-spacing:.045em;backdrop-filter:blur(12px)}
.pusulaTourKicker .lucide{width:13px;height:13px}
.pusulaTourCompass{position:relative;z-index:2;width:112px;height:112px;border-radius:50%;display:grid;place-items:center;border:1px solid color-mix(in srgb,var(--brand) 33%,transparent);background:color-mix(in srgb,var(--panel) 84%,transparent);box-shadow:0 18px 44px rgba(29,126,197,.18),inset 0 0 0 11px color-mix(in srgb,var(--brand) 6%,transparent);backdrop-filter:blur(12px)}
.pusulaTourCompass:before,.pusulaTourCompass:after{content:"";position:absolute;left:50%;top:50%;background:color-mix(in srgb,var(--brand) 26%,transparent);transform:translate(-50%,-50%)}
.pusulaTourCompass:before{width:1px;height:82px}.pusulaTourCompass:after{height:1px;width:82px}
.pusulaTourCompass .lucide{width:54px;height:54px;color:var(--brand);stroke-width:1.45}
.pusulaTourNorth,.pusulaTourSouth{position:absolute;left:50%;z-index:3;transform:translateX(-50%);font-size:10px;font-weight:900;color:var(--brand)}
.pusulaTourNorth{top:12px}.pusulaTourSouth{bottom:11px}
.pusulaTourBody{padding:20px 22px 19px}
.pusulaTourTitle{font-size:22px;font-weight:900;letter-spacing:-.025em;margin:0 0 7px}
.pusulaTourText{margin:0;color:var(--muted);font-size:12.5px;line-height:1.55}
.pusulaTourSteps{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:10px;margin-top:17px;padding:12px;border:1px solid var(--line-soft);border-radius:15px;background:var(--panel-2)}
.pusulaTourStep{display:flex;align-items:center;gap:9px;min-width:0;font-size:11.5px;font-weight:800}.pusulaTourStep .lucide{width:18px;height:18px;flex:none;color:var(--brand)}
.pusulaTourStepArrow{color:var(--muted);display:grid;place-items:center}.pusulaTourStepArrow .lucide{width:16px;height:16px}
.pusulaTourActions{display:grid;grid-template-columns:1fr auto;align-items:center;gap:9px;margin-top:17px}
.pusulaTourTry{height:43px;border:0;border-radius:12px;padding:0 17px;background:linear-gradient(115deg,#20bed5,#3974ff);color:#fff;font-size:12px;font-weight:850;box-shadow:0 8px 22px rgba(44,125,255,.20)}
.pusulaTourSkip{height:43px;border:0;border-radius:12px;padding:0 14px;background:transparent;color:var(--muted);font-size:11.5px;font-weight:750}
.pusulaTourSkip:hover{background:var(--panel-2);color:var(--text)}
.pusulaTourArrow{position:fixed;inset:0;z-index:3;width:100vw;height:100vh;overflow:visible;pointer-events:none}
.pusulaTourArrow path{fill:none;stroke:var(--brand);stroke-width:2;stroke-linecap:round;stroke-dasharray:6 7;filter:drop-shadow(0 2px 4px rgba(35,145,220,.20))}
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
  .mobileJuryMetrics{margin:0 0 10px!important;border-radius:12px!important;background:var(--jury-surface)!important;overflow:hidden!important}
  .mobileJuryMetricContext{display:grid!important;grid-template-columns:minmax(0,1fr) 52px 56px 68px!important;gap:5px!important;padding:10px 10px 5px!important;background:linear-gradient(180deg,rgba(45,168,255,.045),rgba(45,168,255,0))!important}
  .mobileJuryMetricContext b{grid-column:2/5!important;text-align:center!important;font-size:11px!important;font-weight:800!important;color:var(--text)!important;white-space:nowrap!important}
  .mobileMetric{display:grid!important;grid-template-columns:minmax(0,1fr) 52px 56px 68px!important;gap:5px!important;align-items:center!important;padding:8px 10px!important;border-top:1px solid var(--line-soft)!important;font-size:10px!important}
  .mobileMetric>span{min-width:0!important;line-height:1.25!important}.mobileMetric>b{text-align:right!important;white-space:nowrap!important;font-variant-numeric:tabular-nums!important;font-size:10px!important}
  .mobileMetric .p{color:var(--brand)!important}.mobileMetric .deltaGood{color:#35b86f!important}.mobileMetric .deltaBad{color:#e26670!important}
  .mobileMetricHead{padding-top:4px!important;border-top:0!important;color:var(--muted)!important}.mobileMetricHead>b{font-size:9px!important;font-weight:700!important}
  .mobileJuryMetricEmpty{padding:10px 12px!important;color:var(--muted)!important;font-size:10.5px!important}
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
  .mobileTechBody .techCard{padding:12px!important}.mobileTechBody .compareCols{grid-template-columns:1fr!important}.mobileTechBody .flow{grid-template-columns:1fr!important}.mobileTechBody .arrow{display:none!important}.mobileTechBody #tech-overview .pipelineMain{grid-template-columns:1fr!important;gap:5px!important}.mobileTechBody #tech-overview .pipelineMain>.pipelineArrow{display:grid!important;place-items:center!important;transform:rotate(90deg)!important;height:18px!important;color:var(--brand)!important}.mobileTechBody #tech-overview .pipelineSignalsGrid{grid-template-columns:1fr!important}.mobileTechBody #tech-overview .pipelineSignalsHead{align-items:flex-start!important;flex-direction:column!important;gap:2px!important}.mobileTechBody #tech-overview .pipelineSignalsHead span{text-align:left!important}.mobileTechBody #tech-overview .overviewFormula{white-space:normal!important}.mobileTechBody .sourceBadge,.mobileTechBody .backendStatus{margin-top:10px!important}.mobileTechBody .expTable{min-width:720px!important}
  .mobileTechLoading{padding:14px 4px!important;color:var(--muted)!important;font-size:11px!important}
  .pusulaTourCard{width:calc(100vw - 24px);border-radius:22px}
  .pusulaTourVisual{height:160px}.pusulaTourCompass{width:94px;height:94px}.pusulaTourCompass .lucide{width:45px;height:45px}.pusulaTourCompass:before{height:70px}.pusulaTourCompass:after{width:70px}
  .pusulaTourBody{padding:17px 17px 16px}.pusulaTourTitle{font-size:19px}.pusulaTourSteps{margin-top:14px;padding:10px;gap:7px}.pusulaTourStep{font-size:10.5px;gap:6px}.pusulaTourActions{margin-top:14px}.pusulaTourTry,.pusulaTourSkip{height:40px}
}
@media(min-width:721px){.mobileDock,.mobileNavOverlay{display:none!important}}
@media(min-width:721px){
  .postInner{width:100%!important;max-width:none!important;margin:0!important;padding:20px clamp(22px,2.2vw,36px)!important;box-sizing:border-box!important}
  .postInner>.postMain{width:100%!important;min-width:0!important}
  .postActions{width:min(100%,560px)!important;max-width:560px!important;margin:8px auto 0!important;align-items:center!important;justify-content:space-evenly!important;gap:8px!important}
  .postActions .act{flex:1 1 0!important;justify-content:center!important}
  #tech-overview .flow,#tech-architecture .flow{display:grid!important;align-items:stretch!important;gap:10px!important;overflow:visible!important;padding-bottom:0!important}
  #tech-overview .flow{grid-template-columns:repeat(5,minmax(0,1fr))!important}#tech-architecture .flow{grid-template-columns:repeat(6,minmax(0,1fr))!important}
  #tech-architecture .flow>.arrow{display:none!important}
  #tech-overview .flowNode,#tech-architecture .flowNode{min-width:0!important;width:auto!important;height:100%!important}
  #tech-overview .overviewCardNote{color:var(--muted)!important;font-size:10px;line-height:1.35}
  #tech-overview .overviewExplain{margin:9px 0 0;color:var(--muted)!important;font-size:10.5px;line-height:1.45}
  #tech-overview .overviewSignals{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:6px 28px!important;margin-top:9px!important;max-width:760px!important}
  #tech-overview .overviewSignals>div{min-width:0!important;display:grid!important;grid-template-columns:5px auto minmax(0,1fr)!important;align-items:baseline!important;column-gap:7px!important}
  #tech-overview .overviewSignals i{width:5px!important;height:5px!important;border-radius:50%!important;background:var(--brand)!important;align-self:center!important}
  #tech-overview .overviewSignals b{font-size:10.5px!important;color:var(--text)!important;white-space:nowrap!important}
  #tech-overview .overviewSignals span{font-size:10px!important;line-height:1.35!important;color:var(--muted)!important}
  #tech-overview .overviewFormula{white-space:nowrap!important;overflow:visible!important;font-size:10.7px!important;letter-spacing:-.025em!important;padding:12px 11px!important}
  #tech-overview .overviewPipeline{display:grid!important;gap:9px!important}
  #tech-overview .pipelineMain{display:grid!important;grid-template-columns:minmax(100px,.75fr) 20px minmax(125px,.9fr) 20px minmax(330px,2.2fr) 20px minmax(130px,.95fr) 20px minmax(95px,.7fr)!important;align-items:center!important;gap:6px!important}
  #tech-overview .pipelineNode,#tech-overview .pipelineSignal{min-width:0!important}
  #tech-overview .pipelineArrow{display:grid!important;place-items:center!important;color:var(--brand)!important;font-size:18px!important;font-weight:800!important}
  #tech-overview .pipelineSignalsBox{min-width:0!important;border:1px solid var(--line-soft)!important;border-radius:12px!important;background:color-mix(in srgb,var(--brand) 3%,var(--panel))!important;padding:10px!important;display:grid!important;gap:9px!important}
  #tech-overview .pipelineSignalsHead{display:flex!important;align-items:baseline!important;justify-content:space-between!important;gap:10px!important}
  #tech-overview .pipelineSignalsHead b{font-size:10.5px!important;color:var(--text)!important}
  #tech-overview .pipelineSignalsHead span{font-size:9px!important;color:var(--muted)!important;text-align:right!important}
  #tech-overview .pipelineSignalsSection{display:grid!important;gap:5px!important}
  #tech-overview .pipelineSectionLabel{font-size:8.8px!important;font-weight:700!important;color:var(--muted)!important}
  #tech-overview .pipelineSignalsGrid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:7px!important}
  #tech-overview .pipelineSignal{height:auto!important;padding:9px 10px!important}
  #tech-overview .pipelineScore{background:color-mix(in srgb,var(--brand) 7%,var(--panel-2))!important}
  #tech-overview .pipelineNote{margin:1px 0 0!important;font-size:9.5px!important;line-height:1.4!important;color:var(--muted)!important}
}
@media(min-width:721px) and (max-width:1100px){
  #tech-overview .overviewRanking,#tech-overview .overviewIntent{grid-column:1/-1!important}
  #tech-overview .overviewFormula{white-space:normal!important}
  #tech-overview .pipelineMain{grid-template-columns:1fr!important;gap:5px!important}
  #tech-overview .pipelineMain>.pipelineArrow{transform:rotate(90deg)!important;height:18px!important}
  #tech-overview .pipelineSignalsGrid{grid-template-columns:1fr 1fr!important}
  #tech-overview .overviewSignals{grid-template-columns:1fr!important;gap:6px!important;max-width:none!important}
  #tech-overview .overviewSignals>div{grid-template-columns:5px auto minmax(0,1fr)!important;align-items:baseline!important;column-gap:7px!important}
  #tech-architecture .flow{grid-template-columns:repeat(3,minmax(0,1fr))!important}
}
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

  function tourSeen(){try{return localStorage.getItem(TOUR_KEY)==='1'}catch(e){return false}}
  function tourMark(){try{localStorage.setItem(TOUR_KEY,'1')}catch(e){}}
  let tourReflow=null;
  function closePusulaTour(mark){
    const root=document.getElementById('pusulaTour');
    if(mark!==false)tourMark();
    if(tourReflow){window.removeEventListener('resize',tourReflow);window.removeEventListener('orientationchange',tourReflow);window.removeEventListener('scroll',tourReflow,true);tourReflow=null}
    root?.remove();
  }
  function positionPusulaTour(){
    const root=document.getElementById('pusulaTour'),target=document.getElementById('pusulaBar'),cta=document.getElementById('pusulaCta');if(!root||!target||!cta)return;
    const r=target.getBoundingClientRect(),t=cta.getBoundingClientRect(),pad=8,vw=window.innerWidth,vh=window.innerHeight;
    const x=Math.max(8,r.left-pad),y=Math.max(8,r.top-pad),w=Math.min(vw-x-8,r.width+pad*2),h=Math.min(vh-y-8,r.height+pad*2);
    const radius=Math.max(18,Math.min(24,Math.round(Math.min(w,h)*.12)));
    const spot=root.querySelector('.pusulaTourSpot');Object.assign(spot.style,{left:x+'px',top:y+'px',width:w+'px',height:h+'px',borderRadius:radius+'px'});
    const topFog=root.querySelector('[data-tourfog="top"]'),leftFog=root.querySelector('[data-tourfog="left"]'),rightFog=root.querySelector('[data-tourfog="right"]'),bottomFog=root.querySelector('[data-tourfog="bottom"]');
    Object.assign(topFog.style,{left:'0px',top:'0px',width:vw+'px',height:Math.max(0,y)+'px'});
    Object.assign(leftFog.style,{left:'0px',top:y+'px',width:Math.max(0,x)+'px',height:h+'px',borderTopRightRadius:radius+'px',borderBottomRightRadius:radius+'px'});
    Object.assign(rightFog.style,{left:(x+w)+'px',top:y+'px',width:Math.max(0,vw-x-w)+'px',height:h+'px',borderTopLeftRadius:radius+'px',borderBottomLeftRadius:radius+'px'});
    Object.assign(bottomFog.style,{left:'0px',top:(y+h)+'px',width:vw+'px',height:Math.max(0,vh-y-h)+'px'});
    const card=root.querySelector('.pusulaTourCard');
    const targetW=Math.min(vw-24,Math.max(340,Math.min(560,w)));
    card.style.width=targetW+'px';
    const cardW=card.offsetWidth,cardH=card.offsetHeight;
    const left=Math.max(12,Math.min(vw-cardW-12,x+(w-cardW)/2));card.style.left=left+'px';
    const canBelow=r.bottom+26+cardH<vh-12,canAbove=r.top-26-cardH>12;
    const top=canBelow?r.bottom+26:canAbove?r.top-26-cardH:Math.max(12,Math.min(vh-cardH-12,(vh-cardH)/2));card.style.top=top+'px';
    const c=card.getBoundingClientRect(),below=c.top>=r.bottom,sx=c.left+c.width*.55,sy=below?c.top:c.bottom,ex=t.left+t.width/2,ey=below?t.bottom:t.top,dy=Math.max(38,Math.abs(ey-sy)*.38);
    root.querySelector('.pusulaTourArrow path').setAttribute('d',`M ${sx} ${sy} C ${sx} ${below?sy-dy:sy+dy}, ${ex} ${below?ey+dy:ey-dy}, ${ex} ${ey}`);
  }
  function startPusulaTour(){closePusulaTour(true);setTimeout(()=>window.openIntent?.(),40)}
  function showPusulaTour(force){
    if(document.getElementById('pusulaTour'))return;
    if(!force&&tourSeen())return;
    if(typeof S!=='undefined'&&(S.intent||S.dismissed))return;
    const target=document.getElementById('pusulaBar');if(!target||target.offsetParent===null)return;
    const root=document.createElement('div');root.id='pusulaTour';root.className='pusulaTour';root.setAttribute('role','dialog');root.setAttribute('aria-label','PUSULA güncellemesi');
    root.innerHTML='<div class="pusulaTourFog" data-tourfog="top"></div><div class="pusulaTourFog" data-tourfog="left"></div><div class="pusulaTourFog" data-tourfog="right"></div><div class="pusulaTourFog" data-tourfog="bottom"></div><div class="pusulaTourSpot" title="PUSULA yönünü seç"></div><svg class="pusulaTourArrow" aria-hidden="true"><defs><marker id="pusulaTourArrowHead" markerWidth="8" markerHeight="8" refX="6.5" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="none" stroke="var(--brand)" stroke-width="1.6"/></marker></defs><path marker-end="url(#pusulaTourArrowHead)"></path></svg><div class="pusulaTourCard"><div class="pusulaTourVisual"><div class="pusulaTourKicker">'+icon('sparkles','i')+'<span>YENİ GÜNCELLEME</span></div><div class="pusulaTourCompass"><span class="pusulaTourNorth">N</span>'+icon('compass','i')+'<span class="pusulaTourSouth">S</span></div></div><div class="pusulaTourBody"><div class="pusulaTourTitle">Akışının yönünü sen seç</div><p class="pusulaTourText">Ne için geldiğini seç. İstersen ne kadar kalmak istediğini de belirle.</p><div class="pusulaTourSteps"><div class="pusulaTourStep">'+icon('compass','i')+'<span>Amacını seç</span></div><div class="pusulaTourStepArrow">'+icon('arrow-right','i')+'</div><div class="pusulaTourStep">'+icon('clock-3','i')+'<span>Süreni belirle</span></div></div><div class="pusulaTourActions"><button type="button" class="pusulaTourTry">Şimdi dene</button><button type="button" class="pusulaTourSkip">Geç</button></div></div></div>';
    document.body.appendChild(root);root.querySelector('.pusulaTourTry').onclick=startPusulaTour;root.querySelector('.pusulaTourSpot').onclick=startPusulaTour;root.querySelector('.pusulaTourSkip').onclick=()=>closePusulaTour(true);paintIcons();
    tourReflow=()=>positionPusulaTour();window.addEventListener('resize',tourReflow,{passive:true});window.addEventListener('orientationchange',tourReflow,{passive:true});window.addEventListener('scroll',tourReflow,true);requestAnimationFrame(()=>{positionPusulaTour();setTimeout(positionPusulaTour,120)});
  }
  function maybeShowPusulaTour(){
    let force=false;try{force=new URLSearchParams(location.search).get('tour')==='1'}catch(e){}
    if(!force&&tourSeen())return;setTimeout(()=>showPusulaTour(force),520);
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
  function mobileJuryMetrics(){
    const st=typeof S!=='undefined'?S:null;
    if(!st?.intent)return '';
    if(typeof G==='undefined'||!G.c)return '<div class="mobileJuryMetrics"><div class="mobileJuryMetricEmpty">Karşılaştırma hesaplanıyor…</div></div>';
    const a=G.c.classic.metrics,p=G.c.pusula.metrics;
    const nf=new Intl.NumberFormat('tr-TR',{minimumFractionDigits:1,maximumFractionDigits:1});
    const pct=v=>nf.format(Number(v||0)*100)+'%';
    const diff=(x,y)=>{const d=(Number(y||0)-Number(x||0))*100;return (d>0?'+':d<0?'−':'')+nf.format(Math.abs(d))+' puan'};
    const row=(name,x,y,lowerBetter)=>{const d=Number(y||0)-Number(x||0),good=lowerBetter?d<=0:d>=0;return '<div class="mobileMetric"><span>'+name+'</span><b>'+pct(x)+'</b><b class="p">'+pct(y)+'</b><b class="'+(good?'deltaGood':'deltaBad')+'">'+diff(x,y)+'</b></div>'};
    const budget=st.budget?st.budget+' dk':'Sınırsız';
    return '<div class="mobileJuryMetrics"><div class="mobileJuryMetricContext"><b>'+I[st.intent].label+' · '+budget+'</b></div><div class="mobileMetric mobileMetricHead"><span></span><b>Klasik</b><b class="p">PUSULA</b><b>Fark</b></div>'+row('Niyet benzerliği',a.niyet_uyumu,p.niyet_uyumu,false)+row('Niyet-kalite skoru',a.niyet_kalite,p.niyet_kalite,false)+row('Clickbait ortalaması ↓',a.clickbait_ortalama,p.clickbait_ortalama,true)+'</div>';
  }
  function syncMobileJuryMetrics(){
    const q=document.getElementById('mobileNavModal'),slot=q?.querySelector('[data-mmetrics]');if(!slot)return;
    slot.innerHTML=mobileJuryMetrics();
  }
  function mobileJury(){
    const st=typeof S!=='undefined'?S:null,j=!!st?.jury,m=st?.mode||'classic';
    return mobileHead('Jüri')+'<div class="mobileJuryState"><span><b>Jüri görünümü</b><small data-mjurysub>'+(j?'Teknik kontroller açık':'Kullanıcı görünümü açık')+'</small></span><button class="mobileJuryToggle '+(j?'on':'')+'" type="button" data-mjury>'+(j?'Açık':'Kapalı')+'</button></div><div class="mobileModeGrid"><button class="mobileModeBtn '+(m==='classic'?'active':'')+'" data-mmode="classic">Klasik</button><button class="mobileModeBtn '+(m==='pusula'?'active':'')+'" data-mmode="pusula">PUSULA</button></div><div data-mmetrics>'+mobileJuryMetrics()+'</div><div class="mobileJuryActions"><button class="mobileJuryAction" data-mintent>'+icon('compass','i')+'<span>Yön / niyet seç</span></button><button class="mobileJuryAction" data-msession>'+icon('clock','i')+'<span>Oturum sonunu göster</span></button></div>'+mobileTechAccordion();
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
    try{const p=typeof window.syncBackend==='function'?window.syncBackend():null;if(p&&typeof p.then==='function')p.then(()=>{syncMobileJuryMetrics();refreshOpenMobileTech()}).catch(()=>{})}catch(e){}
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
        Promise.resolve(window.setMode?.(mode)).finally(()=>{q.querySelectorAll('[data-mmode]').forEach(x=>x.classList.remove('busy'));syncMobileJuryState();syncMobileJuryMetrics();refreshOpenMobileTech()});
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
    settleHome();syncThemeControl();normalize();wrapTheme();ensureMobileNav();maybeShowPusulaTour();
    if(!wrapped&&typeof window.openPage==='function'){const upstreamOpenPage=window.openPage;window.openPage=function(p,b){const r=upstreamOpenPage(p,b);normalize();return r};wrapped=true}
  }
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.getElementById('pusulaTour'))closePusulaTour(true)});
  const s=document.createElement('script');s.src=UP;s.async=true;s.onload=()=>requestAnimationFrame(finish);document.head.appendChild(s);
  if(document.readyState==='complete')requestAnimationFrame(finish);else window.addEventListener('load',()=>requestAnimationFrame(finish),{once:true});
})();
