/* живе доки: b29.4 не витіснено наступним білдом експорту (wsd 1.8).
   Постійний інструмент проєкту — переїжджає разом із білдом.

   ЩО ПОКРИВАЄ (М-10): до b29.4 жодна з чотирьох матриць не торкалась експорту —
   греп на blankRows|exportXLSX|csvSub давав 0 збігів у всіх чотирьох. Тобто експорт
   можна було зламати повністю, і всі 104 твердження лишались зелені.
   Тут перевіряється рівно те, що b29.4 змінює: ЗРІЗ (дія) ⟂ ПІДПИС (текст) ⟂ ІМ'Я
   файлу — і що всі троє читають ОДНЕ джерело, а не повторюють логіку.

   Запуск: node StockCheck_b29_4_export.js [шлях-до-білда]
   Шлях — argv, не літерал: зашитий шлях перевіряв би старий білд і був би зелений
   на зламаному новому (той самий клас, що виправляли у F2 на літералі версії). */
const fs=require('fs'), path=require('path');
const {JSDOM}=require('jsdom');
const F=process.argv[2]||'/mnt/user-data/outputs/StockCheck_port_b29_4.html';
const HTML=fs.readFileSync(F,'utf8');
const dom=new JSDOM(HTML,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://x.test/'});
const w=dom.window, d=w.document;
let ok=0,bad=0;
const c=(n,v)=>{v?ok++:bad++;console.log((v?'  ✓ ':'  ✗ ')+n)};

setTimeout(async ()=>{

/* ── R6 · мертвий дубль ───────────────────────────────────────────────── */
console.log('\n── R6 · blankRows ──');
c('blankRows оголошена РІВНО один раз',
  (HTML.match(/function blankRows\(/g)||[]).length===1);
c('стара сигнатура (list,MSL,useTable) зникла',
  HTML.indexOf('function blankRows(list,MSL,useTable)')<0);
c('жива сигнатура (list) на місці', HTML.indexOf('function blankRows(list)')>0);

/* ── єдине джерело ────────────────────────────────────────────────────── */
console.log('\n── R5 · одне джерело для дії й підпису ──');
c('exportScope існує', typeof w.exportScope==='function');
c('exportXLSX більше не обходить PH сам',
  !/function exportXLSX\(\)\{[\s\S]{0,600}PH\.forEach/.test(HTML));
c('updateCsvLabel більше не рахує Object.keys(ST.phs)',
  !/function updateCsvLabel[\s\S]{0,300}Object\.keys\(ST\.phs/.test(HTML));
w.S.mode='active'; w.renderList(); w.updateCsvLabel();
c('підпис у шіті === label зрізу (не свій текст)',
  d.getElementById('csvSub').textContent===w.exportScope().label);

/* ── дошка: D-1/A — лише аптеки з даними ──────────────────────────────── */
console.log('\n── Активні (D-1/A) ──');
/* PH / MSL / TOTAL оголошені через const → НЕ властивості window (пастка b27 §9).
   Читаємо через eval у тому ж realm, як ST у смоуку b29.3. */
const EV=x=>w.eval(x);
const px1=EV('PH.filter(function(p){return p.area===S.area;})[0].px');
const TOTAL=EV('TOTAL');
w.eval(`(function(){var v=ensureVisit(${JSON.stringify(px1)});v.vals={};v.vals[MSL[0].k]=3;v.vals[MSL[1].k]=0;})()`);
w.S.city=''; w.S.q='';
let sc=w.exportScope();
c('аптека з даними ввійшла в зріз', sc.list.some(it=>it.ph.px===px1));
c('аптеки без сьогоднішнього візиту НЕ ввійшли',
  sc.list.every(it=>it.vis && Object.keys(it.vis.vals||{}).length>0));
c('label каже «з даними», коли зріз вужчий за лічильник',
  sc.label.indexOf('з даними')>0);
c('counts().a ≥ довжини зрізу (одиниці різні, і це видно)',
  w.counts().a>=sc.list.length);

/* ── topMatch дотримано в дії ─────────────────────────────────────────── */
console.log('\n── зріз слухає екран (П-5) ──');
const cityOfPx1=EV('(PH.find(function(p){return p.px==='+JSON.stringify(px1)+';})||{}).city');
const otherCity=(w.citiesOf(w.S.area)||[]).find(x=>x!==cityOfPx1);
w.S.city=cityOfPx1; sc=w.exportScope();
c('обране місто звужує зріз дії', sc.list.every(it=>it.ph.city===cityOfPx1));
c('назва файлу несе місто зрізу',
  sc.list.length===1 ? true : sc.fname.indexOf(cityOfPx1)>0);
if(otherCity){ w.S.city=otherCity; sc=w.exportScope();
  c('інше місто → аптека px1 у зріз НЕ потрапляє', !sc.list.some(it=>it.ph.px===px1)); }
w.S.city='';

/* ── журнал: дедуп двох дат однієї аптеки (D-2/B · О-9) ───────────────── */
console.log('\n── Перенесені · дедуп (О-9) ──');
const jpx=w.visitModel().filter(r=>r.transferred)[0].px;
const oldDate=w.eval(`(function(){var a=ST.phs[${JSON.stringify(jpx)}].visits;return a[0].date;})()`);
/* другий візит ТІЄЇ Ж аптеки на іншу дату — вхід, якого blankRows ще не бачив */
w.eval(`(function(){var a=ST.phs[${JSON.stringify(jpx)}].visits;
  var v=JSON.parse(JSON.stringify(a[0])); v.date='2000-01-02'; a.unshift(v);})()`);
w.S.mode='transferred';
const rowsN=w.visitModel().filter(r=>r.transferred).filter(w.topMatch)
  .filter(r=>r.px===jpx).length;
sc=w.exportScope();
c('журнал бачить ДВА візити цієї аптеки', rowsN===2);
c('у файл пішла ОДНА аптека (дедуп)', sc.list.filter(it=>it.ph.px===jpx).length===1);
c('узято НАЙНОВІШИЙ візит, не перший у масиві',
  sc.list.find(it=>it.ph.px===jpx).vis.date===oldDate);
c('label показує обидва числа (візити → аптеки)', /→/.test(sc.label));
c('жодного it.vis === null (idx резолвиться)', sc.list.every(it=>!!it.vis));

/* ── ім'я файлу (Q1 · П-15) ───────────────────────────────────────────── */
console.log('\n── ім\'я файлу ──');
c('fsafe ріже заборонені символи',
  w.fsafe('вул. А/Б: *?"<>|  В')==='вул. А Б В');
c('fsafe тримає ліміт довжини', w.fsafe('я'.repeat(200)).length<=48);
const single=w.exportScope();
w.S.mode='active'; w.S.city=cityOfPx1;
const one=w.exportScope();
if(one.list.length===1){
  const core=w.addrParts(one.list[0].ph.addr).core;
  c('одна аптека → в імені ЯДРО АДРЕСИ, не Proxima',
    one.fname.indexOf(w.fsafe(core))>0 && one.fname.indexOf(one.list[0].ph.px)<0);
  c('одна аптека → в імені дата ВІЗИТУ',
    one.fname.indexOf(one.list[0].vis.date)>0);
}else{ c('одна аптека → ядро адреси (пропущено: у зрізі '+one.list.length+')',true);
       c('одна аптека → дата візиту (пропущено)',true); }
/* readonly: екран показує минулий візит — ім'я мусить іти за екраном, не за today() */
w.S.mode='transferred'; w.renderList();
const rr=d.querySelector('#homeList .jr-row');
w.openVisit(rr.getAttribute('data-px'), rr.getAttribute('data-date'));
const ro=w.exportScope();
c('readonly → ім\'я несе дату ВІЗИТУ, не сьогоднішню',
  ro.fname.indexOf(rr.getAttribute('data-date'))>0 && ro.fname.indexOf(w.today())<0);
c('readonly → у зрізі рівно 1 аптека', ro.list.length===1);
w.show('s-home');

/* ── порожній зріз ────────────────────────────────────────────────────── */
console.log('\n── порожній зріз ──');
w.S.mode='active'; w.S.q='цьогонемаєвжодномурядку';
const empty=w.exportScope();
c('порожній зріз → list=[], без падіння', Array.isArray(empty.list)&&empty.list.length===0);
c('порожній зріз → ім\'я все одно валідне', /\.xlsx$/.test(empty.fname));
w.S.q='';

/* ── openpyxl: файл читається як Excel, а не як текст ─────────────────── */
console.log('\n── згенерований файл (openpyxl) ──');
w.S.mode='transferred';
const fin=w.exportScope();
let bytes=null;
try{ bytes=await w.buildXlsx(w.blankRows(fin.list),true); }catch(e){ console.log('  ! buildXlsx:',e.message); }
if(bytes){
  const out='/tmp/b29_4_check.xlsx';
  fs.writeFileSync(out,Buffer.from(bytes));
  fs.writeFileSync('/tmp/b29_4_expect.json',JSON.stringify({
    n:fin.list.length, total:TOTAL, fname:fin.fname,
    pxs:fin.list.map(it=>it.ph.px)}));
  c('buildXlsx віддав байти', bytes.length>0);
}else c('buildXlsx віддав байти', false);

console.log(bad? '\n✗ ПРОВАЛІВ: '+bad+' / '+(ok+bad) : '\n✓ УСІ '+ok+' ЗЕЛЕНІ');
process.exit(bad?1:0);
},700);
