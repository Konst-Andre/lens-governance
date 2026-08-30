/* живе доки: стенд журналу v3 не закрито device-проходом і рішення не перенесені в порт b29
   (wsd 1.8). Постійний інструмент стенду — переїжджає разом зі стендом.

   Головне проти v2: МАТРИЦЯ ПАР (П-8-bis). Одиниця чесності стенду — не важіль,
   а комбінація: N сегментів оголошують N-вимірний простір, і якщо частина клітинок
   не рендериться, панель збрехала, хоча кожен окремий важіль чесний.
   Тому перевірка тут не «важіль працює», а «для кожної пари: або спостережувана
   властивість змінилась, або важіль ВИДИМО згашений і назвав винуватця».

   Запуск: node StockCheck_jr_stagebench_smoke_v3.js  (поряд із HTML) */
const {JSDOM}=require('jsdom'),fs=require('fs');
const errs=[];
const dom=new JSDOM(fs.readFileSync('StockCheck_journal_stagebench_v3.html','utf8'),
 {runScripts:'dangerously',pretendToBeVisual:true});
dom.window.addEventListener('error',e=>errs.push(e.message));
const d=dom.window.document,W=dom.window;
let bad=0;
const t=(n,c)=>{let r;try{r=c()}catch(e){r=false;n+=' → '+e.message}if(!r)bad++;console.log((r?'✓':'✗')+' '+n)};
const q=x=>d.querySelectorAll(x), N=x=>q(x).length;
const click=(el)=>el.dispatchEvent(new W.MouseEvent('click',{bubbles:true}));
/* повний прохід одного стану: сегменти → застосувати → перемалювати */
const set=(o)=>{Object.keys(o).forEach(k=>W.SEG[k]=o[k]);W.applyVars();W.renderJournal();};
/* «важіль згашений» = і логіка назвала винуватця, і панель це показала */
const gated=(id)=>{const g=W.gates(), lv=d.querySelector('.lv[data-lv="'+id+'"]');
  return !!g[id] && !!lv && lv.classList.contains('off')
      && /^⟂ ./.test((lv.querySelector('.why')||{}).textContent||'');};
const live=(id)=>{const g=W.gates(), lv=d.querySelector('.lv[data-lv="'+id+'"]');
  return !g[id] && !!lv && !lv.classList.contains('off') && !lv.querySelector('.why');};

setTimeout(()=>{
console.log('── база ──');
 t('PH = 63',()=>W.PH.length===63);
 t('рантайм-помилок нема',()=>errs.length===0||console.log(errs));
 t('старт = пресет P3 (набір Konst)',()=>W.SEG.wrap==='card'&&W.NUM.rows===7&&W.NUM.groups===4
   &&W.INK.dark.bdA===82&&N('.jr-row')===28);
 t('P3 дослівний: divL/divR 17, hdrGapT 10, tierHome=tail',()=>W.NUM.divL===17&&W.NUM.divR===17
   &&W.NUM.hdrGapT===10&&W.SEG.tierHome==='tail'&&W.SEG.tierStyle==='plate');

console.log('── знахідки v2 не зламані (З-3 · П-9 · D-4) ──');
 t('addrSplit ріже хвіст: ядро ≤34',()=>{set({addrSplit:'on',dataMix:'mix'});
   return Math.max(...[...q('.jr-name')].map(x=>x.textContent.length))<=34;});
 t('вибірка mix містить крайній >80 навіть на 6 рядках',()=>{
   W.NUM.rows=6;W.NUM.groups=1;set({addrSplit:'off',dataMix:'mix'});
   const m=Math.max(...[...q('.jr-name')].map(x=>x.textContent.length));
   W.NUM.rows=7;W.NUM.groups=4;set({addrSplit:'on'});return m>80;});
 t('інваріант filled ≥ 1 (нема 0/83)',()=>{set({cnt:'on'});
   return N('.jr-cnt')>0&&![...q('.jr-cnt')].some(x=>x.textContent.startsWith('0/'));});
 t('кільце: dashoffset у діапазоні 0..75',()=>[...q('.jr-ring circle[stroke-dashoffset]')]
   .every(x=>{const v=+x.getAttribute('stroke-dashoffset');return v>=0&&v<=75;}));

console.log('── g · тир: дім × подача × підпис ──');
 t('tierHome=meta → .jr-mtier у кожному рядку, хвоста нема',()=>{set({tierHome:'meta',tierStyle:'ink',cnt:'off'});
   return N('.jr-mtier')===28&&N('.jr-tail')===0;});
 t('tierStyle=ink → кольорові .jr-otc/.jr-iw, плити нема',()=>N('.jr-otc')===28&&N('.jr-iw')===28&&N('.jr-tag')===0);
 t('tierStyle=plate → 2 плити на рядок, кольорових нема',()=>{set({tierStyle:'plate'});
   return N('.jr-tag')===56&&N('.jr-otc')===0;});
 t('tierLab=pref додає префікси OTC/IW',()=>{set({tierStyle:'ink',tierLab:'pref'});
   return /^OTC /.test(q('.jr-otc')[0].textContent)&&/^IW /.test(q('.jr-iw')[0].textContent);});
 t('tierLab=slash міняє роздільник на /',()=>{set({tierLab:'slash'});
   return q('.jr-dot')[1].textContent==='/';});
 t('tierHome=tail → тир у .jr-tail, у meta його нема',()=>{set({tierHome:'tail',tierLab:'plain'});
   return N('.jr-tail')===28&&N('.jr-mtier')===0&&N('.jr-otc')===28;});
 t('tierHome=none → жодного тира в DOM (не клас-перемикач, а факт)',()=>{set({tierHome:'none'});
   return N('.jr-otc')===0&&N('.jr-tag')===0&&N('.jr-mtier')===0;});
 t('РЕГРЕС-СТОРОЖ: tierHome=none + cnt=off НЕ ховає шеврон',()=>{set({tierHome:'none',cnt:'off',chev:'on'});
   return N('.jr-tail')===0&&N('.jr-chev')===28;});

console.log('── D-7 · meta розщеплено (плита більше не ріжеться) ──');
 t('.jr-meta має окремий .jr-mt із еліпсисом',()=>{set({tierHome:'meta',tierStyle:'plate'});
   return N('.jr-mt')===28&&q('.jr-mtier .jr-tag').length===56;});
 t('текст орієнтира живе в .jr-mt, не поруч із плитою',()=>{set({metaLine:'note'});
   const mt=q('.jr-mt')[0];return mt.querySelectorAll('.jr-tag').length===0&&mt.textContent.length>0;});

console.log('── a · дім заголовка ──');
 t('hdrPos=above → заголовок ПОЗА карткою',()=>{set({wrap:'card',hdrPos:'above'});
   return q('.jr-grp .jr-hdr').length===0&&N('.jr-hdr')===4;});
 t('hdrPos=in → заголовок УСЕРЕДИНІ картки',()=>{set({hdrPos:'in'});
   return q('.jr-grp .jr-hdr').length===4;});
 t('wrap=flat → заголовок у групі, hdrPos не діє',()=>{set({wrap:'flat'});
   return q('.jr-grp .jr-hdr').length===4;});

console.log('── b · роздільник розщеплено ──');
 t('divL ≠ divR доїжджають у CSS-змінні',()=>{W.NUM.divL=53;W.NUM.divR=0;W.applyVars();
   const st=d.getElementById('sbox').style;
   return st.getPropertyValue('--jrDivL')==='53px'&&st.getPropertyValue('--jrDivR')==='0px';});

console.log('── g/h · кольори і шеврон у змінних, per-theme ──');
 t('OTC/IW S+L доїжджають у CSS-змінні',()=>{const st=d.getElementById('sbox').style;
   return st.getPropertyValue('--jrOtcS')==='55'&&st.getPropertyValue('--jrIwL')==='44';});
 t('chevOp per-theme незалежні',()=>{
   click(d.querySelector('#tgTheme button[data-t="dark"]'));
   W.INK.dark.chevOp=70;W.applyVars();
   const dk=d.getElementById('sbox').style.getPropertyValue('--jrChevOp');
   click(d.querySelector('#tgTheme button[data-t="light"]'));W.applyVars();
   const lt=d.getElementById('sbox').style.getPropertyValue('--jrChevOp');
   return dk==='0.70'&&lt==='0.42'&&W.INK.light.chevOp===42;});
 t('tagBd збирається з S+L теми',()=>{const v=d.getElementById('sbox').style.getPropertyValue('--jrTagBd');
   return v==='hsl(162 25% 86%)';});

console.log('── d · підлога картки править лише темну ──');
 t('світла: cardFloor не змінює --jrCardBg',()=>{set({wrap:'card',cardFloor:'soft'});
   return d.getElementById('sbox').style.getPropertyValue('--jrCardBg')==='var(--card)';});
 t('темна: cardFloor опускає підлогу',()=>{click(d.querySelector('#tgTheme button[data-t="dark"]'));
   set({cardFloor:'soft'});const a=d.getElementById('sbox').style.getPropertyValue('--jrCardBg');
   set({cardFloor:'s2'});const b=d.getElementById('sbox').style.getPropertyValue('--jrCardBg');
   click(d.querySelector('#tgTheme button[data-t="light"]'));W.applyVars();
   return a==='var(--bg-soft)'&&b==='var(--surface-2)';});

console.log('── П-8-bis · МАТРИЦЯ ПАР: скасований важіль згашено ВИДИМО ──');
 t('wrap=card × hdrPos=in → hdrBg/hdrMode/stickyTop згашені + названо винуватця',()=>{
   set({wrap:'card',hdrPos:'in'});
   return gated('hdrBg')&&gated('hdrMode')&&gated('stickyTop')&&gated('fitSticky');});
 t('wrap=card × hdrPos=above → ті самі важелі ЖИВІ',()=>{set({hdrPos:'above',hdrMode:'sticky'});
   return live('hdrBg')&&live('hdrMode')&&live('stickyTop');});
 t('wrap=flat → hdrPos згашено, hdrBg живий',()=>{set({wrap:'flat'});
   return gated('hdrPos')&&live('hdrBg');});
 t('hdrMode=flow → stickyTop і кнопка згашені',()=>{set({hdrMode:'flow'});
   return gated('stickyTop')&&gated('fitSticky');});
 t('comp=table → ringSz/ringNum/ringSide згашені, кільця нема в DOM',()=>{set({comp:'table',hdrMode:'sticky'});
   return gated('ringSz')&&gated('ringNum')&&gated('ringSide')&&N('.jr-ring svg')===0;});
 t('comp=ring → ті самі важелі живі, кільце в DOM',()=>{set({comp:'ring'});
   return live('ringSz')&&live('ringSide')&&N('.jr-ring svg')===28;});
 t('chev=off → chevSz/chevOp згашені, шеврона нема в DOM',()=>{set({chev:'off'});
   return gated('chevSz')&&gated('chevOp')&&N('.jr-chev')===0;});
 t('tierHome=none → tierStyle/tierLab/усі колірні згашені',()=>{set({chev:'on',tierHome:'none'});
   return gated('tierStyle')&&gated('tierLab')&&gated('otcS')&&gated('iwL')&&gated('tagBdL');});
 t('tierStyle=ink → колірні живі, плитові згашені',()=>{set({tierHome:'meta',tierStyle:'ink'});
   return live('otcS')&&live('iwL')&&gated('tagBdS')&&gated('tagBdL');});
 t('tierStyle=plate → навпаки',()=>{set({tierStyle:'plate'});
   return gated('otcS')&&live('tagBdS')&&live('tagBdL');});
 t('divider=none → divL/divR/lastDiv/кнопка згашені',()=>{set({divider:'none'});
   return gated('divL')&&gated('divR')&&gated('lastDiv')&&gated('fitDiv');});
 t('divider=line → ті самі живі',()=>{set({divider:'line'});
   return live('divL')&&live('divR')&&live('lastDiv');});
 t('e · rowH оголошує себе мертвим, коли вміст вищий',()=>{
   W.MEASH=58;W.NUM.rowH=44;W.applyGates();
   const okDead=gated('rowH')&&d.querySelector('.lv[data-lv="rowH"] label b').classList.contains('dead');
   W.MEASH=40;W.applyGates();
   const okLive=live('rowH');W.MEASH=0;W.applyGates();return okDead&&okLive;});
 t('ДЕТЕКТОР НЕ ВГАДУЄ: жоден живий важіль не має ярлика ⟂',()=>{
   W.applyPreset('p4');
   return [...q('.lv[data-lv]')].every(lv=>lv.classList.contains('off')===!!lv.querySelector('.why'));});

console.log('── f · пресети ──');
 t('P3 повертає набір Konst цілком (SEG+NUM+INK)',()=>{W.applyPreset('p3');
   return W.SEG.hdrBg==='well'&&W.NUM.divL===17&&W.INK.light.mutL===90&&W.INK.dark.bdA===82;});
 t('P3: hdrBg=well ВИБРАНО, але згашено — саме той випадок, що ловить П-8-bis',()=>
   W.SEG.hdrBg==='well'&&gated('hdrBg'));
 t('P4 — ставка: дуга ліворуч, тир кольором у meta, праворуч лише шеврон',()=>{W.applyPreset('p4');
   return W.SEG.ringSide==='left'&&W.SEG.tierHome==='meta'&&W.SEG.tierStyle==='ink'
     &&N('.jr-tail')===0&&N('.jr-chev')===28&&N('.jr-mtier')===28;});
 t('пресет пересинхронив повзунки',()=>{const r=d.querySelector('input[data-k="divL"]');
   return +r.value===14&&d.getElementById('o_divL').textContent=='14';});
 t('усі 5 кнопок пресетів живі',()=>W.PIDS.every(x=>!!d.getElementById(x)));

console.log('── стенд ──');
 t('COPY-BET маркований v3 і несе обидві теми',()=>{W.writeBet();
   const v=d.getElementById('betOut').value;
   return v.startsWith('JRv3 ')&&/INK\.light/.test(v)&&/INK\.dark/.test(v)&&/tierHome=/.test(v);});
 t('ISLC фабрика + вимір spacer',()=>!!W.ISL&&d.querySelector('.isl-spacer').style.height!=='');
 t('хрестик показ/очищення',()=>{const i=d.getElementById('q');i.value='П';
   i.dispatchEvent(new W.Event('input'));
   const a=d.getElementById('srch').classList.contains('has-q');click(d.getElementById('clrBtn'));
   return a&&i.value===''&&!d.getElementById('srch').classList.contains('has-q');});
 t('INK роздільні по темах',()=>{click(d.querySelector('#tgTheme button[data-t="dark"]'));
   W.INK.dark.valL=70;W.applyVars();
   return d.getElementById('sbox').style.getPropertyValue('--jrValL')==='70'&&W.INK.light.valL===100;});

 console.log('\n'+(bad?('✗ ПРОВАЛЕНО: '+bad):'✓ УСЕ ЧИСТО'));
 process.exit(bad?1:0);
},400);
