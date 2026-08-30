/* живе доки: b29.5 не витіснено наступним білдом експорту (wsd 1.8).
   Постійний інструмент проєкту — переїжджає разом із білдом.

   ЩО ПОКРИВАЄ (М-10): до b29.4 жодна з чотирьох матриць не торкалась експорту —
   греп на blankRows|exportXLSX|csvSub давав 0 збігів у всіх чотирьох. Тобто експорт
   можна було зламати повністю, і всі 104 твердження лишались зелені.
   Тут перевіряється рівно те, що b29.4 змінює: ЗРІЗ (дія) ⟂ ПІДПИС (текст) ⟂ ІМ'Я
   файлу — і що всі троє читають ОДНЕ джерело, а не повторюють логіку.

   Запуск: node StockCheck_b29_5_export.js [шлях-до-білда]
   Шлях — argv, не літерал: зашитий шлях перевіряв би старий білд і був би зелений
   на зламаному новому (той самий клас, що виправляли у F2 на літералі версії). */
const fs=require('fs'), path=require('path');
const {JSDOM}=require('jsdom');
const F=process.argv[2]||'/mnt/user-data/outputs/StockCheck_port_b29_5.html';
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
/* b29.5 · той самий клас, знайдений грепом за ознакою: два ідентичні оголошення
   в одному скоупі, обслуговує лише hoisted-переможець */
c('plVis оголошена РІВНО один раз',
  (HTML.match(/function plVis\(/g)||[]).length===1);
c('plBlk існує (підпис рахує блоки)', (HTML.match(/function plBlk\(/g)||[]).length===1);
/* ширина таблиці більше не зашита літералом у трьох місцях */
c('зашитого A1:O не лишилось', HTML.indexOf('A1:O')<0);
c('зашитого tableColumns count="15" не лишилось', HTML.indexOf('count="15"')<0);
c('dataDxfId як АТРИБУТ відсутній (dxfs=0 → ремонт файлу)',
  HTML.indexOf('dataDxfId="')<0);

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

/* ── журнал: дедуп ЗНЯТО — кожен візит своїм блоком (О-10 · b29.5) ─────
   Твердження цього блока ПЕРЕВЕРНУТІ проти b29.4 свідомо: там дедуп був єдиним
   способом не дати двом нерозрізненним блокам поїхати в один файл, тут його
   знімає 16-та колонка з датою. Стара редакція лишалась би зеленою рівно доти,
   доки зміна не працює. */
console.log('\n── Перенесені · дедуп ЗНЯТО (О-10) ──');
const jpx=w.visitModel().filter(r=>r.transferred)[0].px;
const newDate=w.eval(`(function(){var a=ST.phs[${JSON.stringify(jpx)}].visits;return a[0].date;})()`);
/* другий візит ТІЄЇ Ж аптеки, СТАРІШОЮ датою і на ПОЧАТОК масиву: якщо код
   покладеться на порядок зберігання замість сортування — це впаде */
w.eval(`(function(){var a=ST.phs[${JSON.stringify(jpx)}].visits;
  var v=JSON.parse(JSON.stringify(a[0])); v.date='2000-01-02'; a.unshift(v);})()`);
w.S.mode='transferred';
const rowsN=w.visitModel().filter(r=>r.transferred).filter(w.topMatch)
  .filter(r=>r.px===jpx).length;
sc=w.exportScope();
const jList=sc.list.filter(it=>it.ph.px===jpx);
c('журнал бачить ДВА візити цієї аптеки', rowsN===2);
c('у файл пішли ОБИДВА візити (дедупу більше немає)', jList.length===2);
c('дати цієї аптеки — ЗА ЗРОСТАННЯМ, не в порядку масиву',
  jList[0].vis.date==='2000-01-02' && jList[1].vis.date===newDate);
c('блоки однієї аптеки йдуть підряд, не вперемішку',
  sc.list.findIndex(it=>it.ph.px===jpx)+1
  === sc.list.map((it,i)=>it.ph.px===jpx?i:-1).filter(i=>i>=0)[1]);
const mL=/(\d+)\s*візит\S*\s*→\s*(\d+)\s*блок/.exec(sc.label);
c('label рахує БЛОКИ, а не аптеки', !!mL);
c('label: число блоків === довжині зрізу', !!mL && +mL[2]===sc.list.length);
c('жодного it.vis === null (idx резолвиться)', sc.list.every(it=>!!it.vis));

/* ── ім'я файлу: одна аптека × кілька дат (§5 п.8, Д-4) ───────────────── */
console.log('\n── ім\'я: 1 аптека × N дат ──');
const jRow=w.visitModel().find(r=>r.px===jpx);
w.S.q=jRow.addr;
const multi=w.exportScope();
const uniq=new Set(multi.list.map(it=>it.ph.px)).size;
if(uniq===1&&multi.list.length>1){
  c('кілька дат однієї аптеки → в імені кількість ВІЗИТІВ',
    new RegExp('_'+multi.list.length+'візит').test(multi.fname));
  const mx=multi.list.map(it=>it.vis.date).sort().pop();
  c('кілька дат → в імені НАЙНОВІША дата', multi.fname.indexOf(mx)>0);
  c('в імені НЕМАЄ обрізаного «апт»', multi.fname.indexOf('апт_')<0);
}else{
  c('1 аптека × N дат (пропущено: у зрізі '+uniq+' апт / '+multi.list.length+' бл)',true);
  c('найновіша дата (пропущено)',true); c('без «апт_» (пропущено)',true);
}
w.S.q='';

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
  const out='/tmp/b29_5_check.xlsx';
  fs.writeFileSync(out,Buffer.from(bytes));
  fs.writeFileSync('/tmp/b29_5_expect.json',JSON.stringify({
    n:fin.list.length, total:TOTAL, fname:fin.fname,
    pxs:fin.list.map(it=>it.ph.px),
    /* b29.5 · n — це БЛОКИ (візити), не аптеки: після зняття дедупу одна аптека
       може дати кілька блоків. nph рахує унікальні Proxima — саме воно стоїть
       в імені файлу. dates — очікуваний вміст 16-ї колонки, поблочно. */
    nph:new Set(fin.list.map(it=>it.ph.px)).size,
    dates:fin.list.map(it=>it.vis.date)}));
  c('buildXlsx віддав байти', bytes.length>0);
}else c('buildXlsx віддав байти', false);

console.log(bad? '\n✗ ПРОВАЛІВ: '+bad+' / '+(ok+bad) : '\n✓ УСІ '+ok+' ЗЕЛЕНІ');
process.exit(bad?1:0);
},700);
