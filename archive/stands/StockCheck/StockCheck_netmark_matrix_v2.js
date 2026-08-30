/* StockCheck · netmark v2 — матриця пар (wsd 2.5: судиться комбінація, не важіль)
   живе доки: стенд v2 живий. Запуск: node nm2_smoke.js (jsdom з /home/claude) */
const fs=require('fs'),{JSDOM}=require('jsdom');
const html=fs.readFileSync('/home/claude/StockCheck_netmark_stagebench_v2.html','utf8');
let pass=0,fail=0,warn=0;
const T=(name,cond,note)=>{cond?(pass++,console.log('  ✓ '+name)):(fail++,console.log('  ✗ '+name+(note?' — '+note:'')));};
const W=(name,msg)=>{warn++;console.log('  ⚠ '+name+' — '+msg);};
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,
  beforeParse(w){Object.defineProperty(w.navigator,'userAgent',
    {value:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1',configurable:true});}});
const w=dom.window,d=w.document,NM=w.__NM;

console.log('\n── 0 · САМОПЕРЕВІРКА СТЕНДА (Д-В: інакше матриця перевіряє себе) ──');
T('UA-підміна спрацювала',/iPhone OS 18_7/.test(w.navigator.userAgent));
T('__NM експортовано',!!NM);
T('16 мереж',NM&&NM.NETS.length===16);
T('RAW 463 · зріз 458',NM&&NM.PH.length===463&&NM.PH.filter(p=>p.dn).length===458);

console.log('\n── 1 · NETS ⟂ АССЕТИ ⟂ RAW-ІНДЕКСИ ──');
const A=NM.ASSETS;
T('15 растрів у ассетах',Object.keys(A).length===15,'знайдено '+Object.keys(A).length);
T('Фармастор — вектор, не растр',!A['FARMASTOR']&&NM.NETS.some(n=>n.slug==='FARMASTOR'&&n.glyph));
T('кожен НЕ-гліф має mark+mini',NM.NETS.filter(n=>!n.glyph).every(n=>A[n.slug]&&A[n.slug].mark&&A[n.slug].mini));
T('kNet є на всі 16',NM.NETS.every(n=>typeof NM.ST.kNets[n.slug]==='number'));
T('kNet FARMASTOR=1.35 (§1 H3.9)',NM.ST.kNets.FARMASTOR===1.35);
T('ACT.L device-lock acc/w1/a42/t44',NM.ST.act.light.bd==='acc'&&NM.ST.act.light.ringW===1
   &&NM.ST.act.light.ringA===42&&NM.ST.act.light.tone===44,'P1 із файлу b6 дав би neu/w2/a82/t84');
T('plate=73 · pad=9 · lbl=12',NM.ST.plate===73&&NM.ST.pad===9&&NM.ST.lblSz===12);
/* RAW-порядок: якщо переставити NETS, мережі тихо перемішаються по 463 аптеках */
const anc=NM.PH.filter(p=>p.net==='АНЦ').length;
T('RAW-індекси не перемішані (АНЦ=147 у зрізі 458)',
   NM.PH.filter(p=>p.dn&&p.net==='АНЦ').length===147,'фактично '+NM.PH.filter(p=>p.dn&&p.net==='АНЦ').length);

console.log('\n── 2 · МАТРИЦЯ ПАР: ebRepeat × scope ──');
[8,60,458].forEach(sc=>{
  NM.setScope(sc);
  ['all','first','change'].forEach(r=>{
    NM.setRep(r);
    const total=d.querySelectorAll('#list .eb').length;
    const hidden=d.querySelectorAll('#list .eb.rep-off').length;
    const vis=total-hidden;
    if(r==='all') T(`scope=${sc} rep=all: жодного погашеного`,hidden===0);
    else {
      /* коректний очікуваний результат: гасити є ЩО лише коли в зрізі є сусідні однакові.
         Без цієї умови детектор давав хибний ✗ на scope=8, де всі мережі різні (К2). */
      const L=NM.scoped(); let adj=0;
      for(let i=1;i<L.length;i++) if(L[i].net===L[i-1].net) adj++;
      T(`scope=${sc} rep=${r}: погашено ${hidden} (сусідніх однакових ${adj})`,
        adj>0?hidden>0:hidden===0, adj>0?'важіль не подіяв':'погасив там, де сусідніх однакових немає');
    }
  });
});
NM.setRep('all');NM.setScope(458);

console.log('\n── 3 · МАТРИЦЯ ПАР: mode × family (спліт важелів) ──');
NM.setScope(60);
[['card',1,0],['jr',0,1],['both',1,1]].forEach(([m,c,j])=>{
  NM.setMode(m);
  const cards=d.querySelectorAll('#list .card').length, rows=d.querySelectorAll('#list .jr-row').length;
  T(`mode=${m}: card ${cards>0?'є':'нема'} · jr ${rows>0?'є':'нема'}`,(cards>0)===!!c&&(rows>0)===!!j);
});
NM.setMode('both');
T('картка й журнал читають РІЗНІ змінні (2.6)',
  /\.jr-txt \.eb\{font-size:var\(--ebSzJ\)/.test(html.replace(/\s+/g,' ').replace(/ \{/g,'{')) 
  || html.includes('--ebSzJ'));

console.log('\n── 4 · ГЕОМЕТРІЯ КАРТКИ НЕ ЧІПАНА (§3.4) ──');
T('grid-areas "id rt" / "foot foot"',html.includes('grid-template-areas:"id rt" "foot foot"'));
T('hero присутній у кожній картці',
  d.querySelectorAll('#list .card').length===d.querySelectorAll('#list .card .rt .ring').length);
T('eyebrow — ПЕРШИЙ у .idcol, перед .addr',(()=>{
  const c=d.querySelector('#list .card .idcol');
  return c&&c.children[0].classList.contains('eb')&&c.children[1].classList.contains('addr');})());
T('eyebrow у журналі — перед .jr-name',(()=>{
  const t=d.querySelector('#list .jr-txt');
  return t&&t.children[0].classList.contains('eb')&&t.children[1].classList.contains('jr-name');})());
T('m:2+i*83 формула не змінена',html.includes('2+p.i*83'));

console.log('\n── 5 · КОНТЕЙНЕРИ (О-47): sheet ⟂ dropdown ──');
['sheet','dropdown'].forEach(c=>{
  NM.setCont(c);NM.open();
  const on=c==='sheet'?d.getElementById('sheetGrid'):d.getElementById('ddGrid');
  const off=c==='sheet'?d.getElementById('ddGrid'):d.getElementById('sheetGrid');
  T(`${c}: відкрився саме він`,on.classList.contains('on')&&!off.classList.contains('on'));
  T(`${c}: scrim on`,d.getElementById('scrim').classList.contains('on'));
  T(`${c}: скрол списку заблокований`,d.getElementById('stgScroll').classList.contains('locked'));
  T(`${c}: сітка має 16 плиток`,on.querySelectorAll('.ncard').length===16);
  NM.close(false);
  T(`${c}: закрився, скрол відпущено`,!on.classList.contains('on')
     &&!d.getElementById('stgScroll').classList.contains('locked'));
});
T('свайпу шіта НЕ додано (у b32.0 його немає)',
  !/getElementById\('shGrip'\)[\s\S]{0,80}(addEventListener|ontouch)/.test(html),
  'на #shGrip навішано жест');

console.log('\n── 6 · ЄДИНИЙ ТРИГЕР: вибір у сітці ⟂ чіп-стрічка ──');
T('чіп-стрічки немає',!html.includes('chip-strip')&&d.querySelectorAll('.tchip').length===0);
NM.setCont('sheet');NM.open();
const tile=d.querySelector('#sheetGrid .ncard[data-i="1"]');
tile.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
T('тап плитки змінив зріз',NM.S.net===NM.NETS[1].net);
T('тап плитки закрив контейнер',!NM.isOpen());
T('список звузився до однієї мережі',
  new Set([...d.querySelectorAll('#list .card .eb')].map(e=>e.textContent)).size<=1);
NM.setNet('');

console.log('\n── 7 · ЛІЧИЛЬНИК ПЛИТКИ = ФАКТ СТЕНДА (М-1/М-4) ──');
NM.setScope(458);
const c458=NM.gridCounts();
T('сума лічильників = зріз 458',Object.values(c458).reduce((a,b)=>a+b,0)===458);
T('A911 у плитці ≠ nBase 196',c458['A911']!==196&&c458['A911']>0,'плитка '+c458['A911']+' · база 196');
NM.setScope(8);
T('scope=8: сума лічильників = 8',Object.values(NM.gridCounts()).reduce((a,b)=>a+b,0)===8);

console.log('\n── 8 · ЗАМІР Д-29 ДРУКУЄ ТРИ ЧИСЛА ──');
NM.setScope(60);
const m=NM.measure();
T('плашка друкує «сире»',/сире/.test(m));
T('плашка друкує множник ÷',/÷[\d.]+/.test(m),'фрагмент: '+(m.split('\n')[0]||'').slice(0,80));
T('offscreen-заміри позначені як сирі',/СИРІ|сирі/.test(m));
T('Д-30: рядків на екран є в заміру',/рядків на екран/.test(m));
T('стеля kNet рахується формулою',/стеля kNet/.test(m));

console.log('\n── 9 · ЗАБОРОНИ ──');
T('ebInk не має accent-ink/text-2',
  /\.eb\{[^}]*color:var\(--muted\)/.test(html.replace(/\s*\n\s*/g,''))
  && !/\.eb\{[^}]*var\(--text-2\)/.test(html.replace(/\s*\n\s*/g,''))
  && !/\.eb\{[^}]*accent/.test(html.replace(/\s*\n\s*/g,'')));
T('A48 лишився РЕФЕРЕНСОМ, не дефолтом',html.includes('A48:')&&NM.EB.card.sz===12&&NM.EB.card.w===600);
T('mDot не застосований до eyebrow',!/\.eb[\s\S]{0,120}mDot/.test(html));
T('О-45 плашка в панелі, не в сцені',
  !!d.querySelector('#panel #expLbl')&&!d.querySelector('.sbox #expLbl'));
T('box-sizing:border-box оголошено (A70)',html.includes('*,*::before,*::after{box-sizing:border-box}'));

console.log(`\n═══ ${pass} ✓ · ${fail} ✗ · ${warn} ⚠ ═══`);
process.exit(fail?1:0);
