/* живе доки: до наступної версії стенда (v18) — далі перейменовується разом із базою
   EquipLens · смоук стенда v17 (v17_13). Перевіряє МЕХАНІКУ, НЕ значення важелів:
   числа живуть у EquipLens_head_valuesLOCK.md, смоук про них нічого не знає (S9, крок 1б).
   Запуск: node smoke_v17_13.js           — чистий прогін
           node smoke_v17_13.js --inject   — підкинутий дефект (wsd 12.12)
           node smoke_v17_13.js <файл>     — база явно, якщо ім'я інше

   БАЗА ОГОЛОШУЄТЬСЯ, А НЕ ВГАДУЄТЬСЯ (wsd 1.10). Раніше ім'я було вшите в
   readFileSync і відставало від бази — файл доводилось перейменовувати перед
   кожним прогоном. Глоб по теці тут був би гіршим лікуванням: детектор, що
   САМ обирає, який білд перевіряти, мовчки перевірить не той. */
const {JSDOM}=require('jsdom'), fs=require('fs');
const INJECT=process.argv.includes('--inject');
let ok=0, bad=0; const T=(n,c)=>{ c?(ok++):(bad++,console.log('  ✗ '+n)); };

const BASE = process.argv.find(a => a.endsWith('.html')) || 'EquipLens_headbench_v17_13.html';
if (!fs.existsSync(BASE)){
  console.log(`✗ бази немає: ${BASE}\n  оголоси інше ім'я аргументом: node ${require('path').basename(__filename)} <файл>`);
  process.exit(1);
}
let html=fs.readFileSync(BASE,'utf8');
if (INJECT){
  /* Дефект класу «мовчазне підхоплення»: протухлий ключ падає прямо в LOCKS
     замість LOCK_STALE. Саме те, від чого гейт мусить закричати. */
  html=html.replace(
    "Object.keys(o.v || {}).forEach(k => { (k in S) ? LOCKS[k] = o.v[k] : LOCK_STALE.push(k); });",
    "Object.keys(o.v || {}).forEach(k => { LOCKS[k] = o.v[k]; });");
  /* Дефект класу «порядок шарів» — рівно та регресія v11, через яку контактна
     тінь тонула під дальньою і оператор крутив невидимий важіль (§0-1). */
  html=html.replace(
    "  outer.push(far);\n  outer.forEach(p => parts.push(p));",
    "  outer.unshift(far);\n  outer.forEach(p => parts.push(p));");
  /* Дефект класу «шар не там»: блік іде під тілом замість над ним. Візуально
     це «пляма зникла», і без детектора списалось би на слабке значення. */
  /* v17 · Дефект класу «намальовано, але не підключено» — рівно той, що
     оператор зловив на девайсі: пікер існує в розмітці, а pick() його не знає. */
  html=html.replace("pick('pkBg','bg');","");
  /* v17_13-б · Дефект «важіль оголошено, але не підключено» — рівно те, що
     проїхало на девайс у К10'. Знімається рядок реєстрації; паритет К20 при
     цьому лишається зеленим, бо data-k і ключ S на місці. */
  html=html.replace("['edgeX',v=>v+'px',1],","");
  /* v17_13 · К21 · Дефект класу «тихий дубль при переїзді»: рядок важеля
     скопійовано в чужий таб замість того, щоб бути перенесеним. Паритет 1-4
     ловить його як дубль id, 5-6 — як важіль у двох табах. Обидва боки. */
  html=html.replace('<div class="bx-tab" data-tab="pal">',
    '<div class="bx-tab" data-tab="pal"><div class="bx-lv" data-k="dkH">'
    +'<label>відтінок<i></i></label><input type="range" id="dkH" min="0" max="330" step="5"><o></o></div>');
  /* v17 · К1 · Дефект класу «паспорт пише сам». Паспорт збирає фон завжди для
     світлої теми — тобто розходиться зі стендом мовчки, рівно той дефект, проти
     якого cssPassport колись стала іменованою функцією. */
  html=html.replace("const aurCss = aurLayers(dark);","const aurCss = aurLayers(false);");
  /* v17_4 · хід 2 · Дефект класу «спільне число на дві теми» (A39) на осі
     відтінку — рівно те, що роз'їжджалось цим ходом. */
  html=html.replace(
    "  const hu = dark ? [S.bgH1D, S.bgH2D, S.bgH3D] : [S.bgH1L, S.bgH2L, S.bgH3L];",
    "  const hu = [S.bgH1L, S.bgH2L, S.bgH3L];");
  /* v17_4 · Дефект класу «міграція пакетна, не поключова»: успадкує лише перша
     ціль, друга мовчки лишиться без локу. */
  html=html.replace("    LOCK_MIGRATE[old].forEach(to => {","    [LOCK_MIGRATE[old][0]].forEach(to => {");
  /* v17_5 · хід 3 · Дефект класу «форми немає»: еліпс знову без радіусів, тобто
     ~кругла пляма, якою капсулу накрити фізично неможливо (М-2). */
  html=html.replace(
    "    `radial-gradient(ellipse ${Math.round(p[2] * sp)}% ${Math.round(p[3] * sp)}% `\n    + `at ${p[0]}% ${p[1]}%, `",
    "    `radial-gradient(ellipse at ${p[0]}% ${p[1]}%, `");
  /* v17_5 · Дефект класу «один повзунок міняє дві незалежні речі»: bgSpread
     повертається на стоп і тягне м'якість краю разом із розміром. */
  html=html.replace("+ `transparent ${p[4]}%)`);","+ `transparent ${Math.round(p[4] * sp)}%)`);");
  /* v17_3 · К0-б · Дефект класу «детектор дивиться в одну функцію, а паспорт
     збирається з двох» (З-11). Хибний ✗ — стабільний і завжди на тих самих
     іменах, тому найнебезпечніший: привчає читати червоне як фон. */
  html=html.replace(
    "        src=cssPassport.toString() + aurLayers.toString();",
    "        src=cssPassport.toString();");
  /* v17_9 · К20 · Дефект класу «тихий переїзд»: при ручному перекладанні
     важеля в іншу групу губиться data-k, а input лишається цілим. Повзунок
     видно, він рухається — і не керує нічим, бо paintDead/markLock шукають
     по data-k. Око цього не ловить у принципі. */
  html=html.replace('<div class="bx-lv" data-k="bH">','<div class="bx-lv">');

  /* v17 · К1 · Дефект класу «спільне число на дві теми» (A39) на новій осі:
     сили аврори перестають розходитись по темах. Візуально це «на темній
     блякло», і без детектора списалось би на слабке значення. */
  html=html.replace(
    "  const al = dark ? [S.bgA1D, S.bgA2D, S.bgA3D] : [S.bgA1L, S.bgA2L, S.bgA3L];",
    "  const al = [S.bgA1L, S.bgA2L, S.bgA3L];");
  /* v17_6 · К7-а · Дефект класу «намальовано, але не підключено» на новій осі:
     пікер заливки існує в розмітці, а pick() його не знає — рівно те, що
     оператор колись зловив на девайсі з pkBg. */
  html=html.replace("pick('pkTzFill','tzFill');","");
  /* v17_6 · К7-а · Дефект класу «фолбек ховає мертвий важіль»: замість
     transparent змінна просто не ставиться, і var(--tzbg,var(--canvas))
     мовчки повертає заливку. Пікер клікається, картинка стоїть. */
  html=html.replace(
    "  s.setProperty('--tzbg', S.tzFill==='canvas' ? 'var(--canvas)' : 'transparent');","");
  /* v17_6 · К7-а · Дефект класу «прозорість знесла перекриття»: разом із
     заливкою зникає sticky, і верхня зона починає їхати зі списком. Це не
     те, що ми просили, і оком на короткому списку не видно. */
  html=html.replace(
    ".el-ctxhead{padding:2px 14px 10px;background:var(--tzbg,var(--canvas));position:sticky;top:0;z-index:5}",
    ".el-ctxhead{padding:2px 14px 10px;background:var(--tzbg,var(--canvas))}");
  /* v17_7 · К7-б · Дефект класу «намальовано, але не підключено» на атрибуті:
     гілки існують у CSS, а розмітка про них не знає — [data-tz] не ставиться,
     і всі чотири кнопки дають одну картинку. Пікер при цьому клікається. */
  html=html.replace(
    'return `<div class="el-ctxhead" data-tz="${S.tzFill}" data-srch=',
    'return `<div class="el-ctxhead" data-srch=');
  /* v17_7 · К7-б · Дефект класу «скло намальоване, але не працює»: правило
     гілки лишається, backdrop-filter із нього зникає. Візуально це «блюр
     слабкий» — і важіль крутили б замість того, щоб шукати механіку. */
  html=html.replace(
    "  -webkit-backdrop-filter:blur(var(--tzBlur,14px)) saturate(var(--tzSat,160%));\n  backdrop-filter:blur(var(--tzBlur,14px)) saturate(var(--tzSat,160%))}",
    "  -webkit-backdrop-filter:blur(var(--tzBlur,14px)) saturate(var(--tzSat,160%))}");
  /* v17_7 · К7-б · Дефект класу «спільне число на дві теми» (A39) на alpha
     скла зони: обидві теми починають брати світле значення. За A100 це рівно
     той випадок, коли скло калібрували на одній підкладці й перенесли на іншу. */
  html=html.replace(
    "  s.setProperty('--tzA', (dark ? S.tzAD : S.tzAL) + '%');",
    "  s.setProperty('--tzA', S.tzAL + '%');");
  /* Дефект класу «повернувся border»: кант знову малюється рамкою, тобто всі
     три механізми краю оживають разом. Саме те, що ми щойно вилікували. */
  html=html.replace(
    "  background-clip:padding-box;\n  backdrop-filter:blur(var(--fab-blur,16px))",
    "  border:1px solid var(--fab-rim);\n  backdrop-filter:blur(var(--fab-blur,16px))");
  html=html.replace(
    "    : `radial-gradient(circle ${S.shSpecS}px at ${S.shX}% ${S.shY}%, rgba(255,255,255,${shSpc}) 0%, rgba(255,255,255,0) 100%),`\n    + `radial-gradient(circle at ${S.shX}% ${S.shY}%,",
    "    : `radial-gradient(circle at ${S.shX}% ${S.shY}%, rgba(255,255,255,${shTop}) 0%, rgba(255,255,255,0) 52%, rgba(0,0,0,${shBot}) 100%),`\n    + `radial-gradient(circle ${S.shSpecS}px at ${S.shX}% ${S.shY}%,");  /* v15 · Дефект класу «кант з'їдає кільце»: кільце знову відлічується від
     кромки, а не від внутрішнього краю канта. Візуально це «кільце зникло при
     товстому канті» — рівно та скарга оператора, яку крок 0 і лікував. */
  html=html.replace(
    "  const ringW = rimW + S.fabRingW / 10;",
    "  const ringW = S.fabRingW / 10;");
  /* v16 · Дефект класу «спільне число на дві теми» (A39): полюс шейдингу знову
     читається без гілки теми. Візуально це «крутиш темну — ламається світла»,
     тобто рівно та сліпота, через яку розщеплення й робилось. */
  html=html.replace(
    "  const shX = dark ? S.shXD : S.shXL;\n  const shY = dark ? S.shYD : S.shYL;",
    "  const shX = S.shXL;\n  const shY = S.shYL;");
  /* v17_8 · К9' · Дефект класу «фолбек ховає мертвий важіль» (З-20 на новій осі):
     щілина повертається на константу. Пікер клікається, гілка вмикається,
     повзунок крутиться — картинка стоїть, бо CSS про змінну більше не знає. */
  html=html.replace(
    '.el-list[data-row="slit"]{gap:var(--slitW,1px)}',
    '.el-list[data-row="slit"]{gap:1px}');
  /* v17_8 · К9' · Дефект класу «ДВА НОСІЇ ОДНОГО ЯВИЩА» (З-36) — рівно те,
     заради чого гілка й писалась. Кант .el-sw повертається: 1 на шкалі дає
     2px на екрані, і число, що поїде в valuesLOCK, бреше вдвічі. Оком це
     «щілина якась широка», тобто списалось би на значення, не на механіку. */
  html=html.replace(
    '.el-list[data-row="slit"] .el-sw{border:none;border-radius:0;box-shadow:none}',
    '.el-list[data-row="slit"] .el-sw{border:1px solid transparent;border-radius:0;box-shadow:none}');
  /* v17_8 · К9' · Дефект класу «важіль вічно живий» (З-9 · З-30): рядок
     залежності зникає, slitW оголошується живим і в «рядку», і в «картці».
     Оператор крутить те, чого на екрані немає, а паспорт друкує неповний
     вирок як повний. */
  html=html.replace(
    "    ['щілина', 'таб має список і рядок = щілина', hasHead && S.row==='slit', ['slitW']],",
    "");
}

/* Розбір списку CSS-шарів. Регекс із lookahead працює на box-shadow і мовчки
   бреше на градієнтах: у `rgba(..) 0%, rgba(..)` кома між стопами виглядає
   для нього як роздільник шарів. Дужки рахуємо лічильником, не маскою. */
function splitTop(v){
  const out=[]; let d=0, cur='';
  for (const ch of v){
    if (ch==='(') d++;
    else if (ch===')') d--;
    if (ch===',' && d===0){ out.push(cur.trim()); cur=''; continue; }
    cur+=ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}

const errs=[];
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,
  url:'https://konst-andre.github.io/',
  beforeParse(w){
    w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
    w.confirm=()=>true; w.alert=()=>{};
    /* Сховище засіяне ДО парсингу: один валідний ключ і один протухлий.
       Валідний доводить, що лок переживає перезавантаження; протухлий — що
       ключ від зниклого важеля не потрапляє в регістр мовчки. */
    try{ w.localStorage.setItem('EL_LOCK', JSON.stringify(
      {b:'v9', t:Date.now(), v:{fabS:56, notchR:34}})); }catch(e){}
    w.onerror=m=>errs.push(String(m));
    const ce=w.console.error; w.console.error=(...a)=>errs.push(a.join(' '));
  }});

setTimeout(()=>{
 const w=dom.window, d=w.document;
 /* `const S` у стенді — лексична глобаль: вона НЕ лежить на window.
    Читати її ззовні можна тільки через w.eval. Це не хак смоука, це семантика
    класичного скрипта: var потрапляє на window, let/const — ні. */
 const G=e=>w.eval(e), S=G('S');
 const q=s=>d.querySelector(s), qa=s=>[...d.querySelectorAll(s)];

 console.log(INJECT?'=== ПРОГІН ІЗ ПІДКИНУТИМ ДЕФЕКТОМ ===':'=== ЧИСТИЙ ПРОГІН ===');

 console.log('— A · рантайм і встановлення кнопок —');
 T('рантайм без помилок', errs.length===0);
 const rows=qa('.bx-lv[data-k]'), picks=qa('.bx-pick[data-dk]');
 T('рядків важелів знайдено', rows.length>0);
 T('пікерів знайдено', picks.length>0);
 T('кожен рядок має замок', rows.every(r=>r.querySelector('.bx-lock')));
 T('кожен пікер має замок', picks.every(p=>p.querySelector('.bx-lock')));
 T('замків рівно стільки, скільки важелів', qa('.bx-lock').length===rows.length+picks.length);
 T('жоден замок не має data-v (не сплутається з опцією)',
   qa('.bx-lock').every(b=>b.dataset.v===undefined));
 T('замок не отримав aria-pressed від syncPicks',
   qa('.bx-pick .bx-lock').every(b=>!b.hasAttribute('aria-pressed')));

 console.log('— B · сховище пережило перезавантаження —');
 T('валідний ключ fabS підхоплено з localStorage', G('LOCKS').fabS===56);
 T('ЛОК-регістр не порожній на старті', Object.keys(G('LOCKS')).length>0);
 T('LOCK_MEM=false (сховище доступне)', G('LOCK_MEM')===false);

 console.log('— C · ПРОТУХЛИЙ КЛЮЧ не підхоплюється мовчки —');
 /* notchR — важіль, знятий у v9 разом із вирізом. Його в S немає. */
 T('notchR відсутній у стані', !('notchR' in S));
 T('notchR НЕ потрапив у LOCKS', !('notchR' in G('LOCKS')));
 T('notchR оголошений у LOCK_STALE', G('LOCK_STALE').indexOf('notchR')>-1);
 T('лічильник друкує «протухло»', q('#meter').textContent.indexOf('протухло')>-1);

 console.log('— D · три стани замка —');
 const rowFab=rows.find(r=>r.dataset.k==='fabS');
 T('рядок fabS знайдено', !!rowFab);
 /* Сід сховища (56) — про механіку читання. Стан «on» вимагає рівності
    важеля й локу, тому тест сам зводить важіль до засіяного числа. */
 G('S.fabS=56; render();');
 T('fabS у стані on (значення = локу)', rowFab.querySelector('.bx-lock').dataset.st==='on');
 T('ярлик друкує «= ЛОК»', rowFab.querySelector('label i').textContent.indexOf('= ЛОК')>-1);
 /* Зсув: крутимо важіль геть від зафіксованого значення */
 G('S.fabS=48; render();');
 T('після зсуву стан drift', rowFab.querySelector('.bx-lock').dataset.st==='drift');
 T('ярлик друкує старий ЛОК, а не новий стан',
   rowFab.querySelector('label i').textContent.indexOf('ЛОК 56')>-1);
 T('рядок помічений is-drift', rowFab.classList.contains('is-drift'));
 T('лічильник друкує «зсунуто»', q('#meter').textContent.indexOf('зсунуто')>-1);

 console.log('— E · тап по замку фіксує і знімає —');
 const rowGap=rows.find(r=>r.dataset.k==='fabGap');
 const before=Object.keys(G('LOCKS')).length;
 rowGap.querySelector('.bx-lock').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
 T('фіксація додала ключ', Object.keys(G('LOCKS')).length===before+1);
 T('значення взято поточне', G('LOCKS').fabGap===S.fabGap);
 T('кнопка перейшла в on', rowGap.querySelector('.bx-lock').dataset.st==='on');
 rowGap.querySelector('.bx-lock').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
 T('повторний тап зняв фіксацію', !('fabGap' in G('LOCKS')));
 T('кнопка повернулась в off', rowGap.querySelector('.bx-lock').dataset.st==='off');

 console.log('— F · замок у пікері не псує стан (капітальний ризик) —');
 const pk=picks.find(p=>p.dataset.dk==='fabTone');
 T('пікер fabTone знайдено', !!pk);
 const toneBefore=S.fabTone;
 pk.querySelector('.bx-lock').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
 T('S.fabTone не змінився від тапу по замку', S.fabTone===toneBefore);
 T('S.fabTone не став undefined', S.fabTone!==undefined);
 T('пікер зафіксовано', G('LOCKS').fabTone===toneBefore);

 console.log('— G · запис у сховище —');
 let saved=null; try{ saved=JSON.parse(w.localStorage.getItem('EL_LOCK')); }catch(e){}
 T('сховище перезаписано валідним JSON', !!saved && !!saved.v);
 /* Штамп звіряється з ЖИВИМ LOCK_BUILD, а не з рядком у тесті: інакше кожен
     новий білд валить два асерти, які нічого не стережуть (2-А). */
  T('штамп білда у сховищі = поточний білд', saved && saved.b===G('LOCK_BUILD'));
 T('fabTone доїхав у сховище', saved && saved.v.fabTone===toneBefore);
 T('протухлий notchR НЕ записаний назад', saved && !('notchR' in saved.v));

 console.log('— H · експорт ЛОКу окремий від паспорта —');
 q('#lockExp').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
 const exp=q('#out').value;
 T('експорт має шапку valuesLOCK', exp.indexOf('head valuesLOCK')>-1);
 T('експорт несе рядок «живе доки»', exp.indexOf('живе доки')>-1);
 T('експорт попереджає, що це не канон', exp.indexOf('не канон')>-1);
 T('експорт називає зсув', exp.indexOf('зсунуто після фіксації')>-1);
 T('експорт друкує протухлі', exp.indexOf('notchR')>-1);
 T('експорт НЕ містить мертвих важелів паспорта', exp.indexOf('ЖИВІ =')===-1);

 console.log('— I · паспорт Copy-ALL підхопив ЛОК —');
 q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
 const pass=q('#out').value;
 T('паспорт має блок ЗАЛОЧЕНО', pass.indexOf('ЗАЛОЧЕНО =')>-1);
 T('паспорт має рядок ЗСУНУТО З ЛОКУ', pass.indexOf('ЗСУНУТО З ЛОКУ')>-1);
 T('паспорт має рядок ПРОТУХЛІ', pass.indexOf('ПРОТУХЛІ ключі')>-1);
 T('паспорт лишився паспортом (ЖИВІ на місці)', pass.indexOf('ЖИВІ =')>-1);
 T('ЗАЛОЧЕНО парситься як JSON', (()=>{ try{
     JSON.parse(pass.split('ЗАЛОЧЕНО = ')[1].split('\n')[0]); return true; }catch(e){ return false; } })());

 console.log('— J · скидання —');
 q('#lockRst').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
 T('регістр очищено', Object.keys(G('LOCKS')).length===0);
 T('протухлі очищено', G('LOCK_STALE').length===0);
 T('усі замки в off', qa('.bx-lock').every(b=>b.dataset.st==='off'));
 T('лічильник показує ЛОК 0', /ЛОК 0\//.test(q('#meter').textContent));

 console.log('— K · КРОК 1 · два дефекти —');
 const css=d.querySelector('style').textContent;
 T('Д-1: --r-ctl на світлій має валідне px-значення', /--r-ctl:\s*\d+(\.\d+)?px/.test(
   css.slice(css.indexOf('[data-theme="light"]'), css.indexOf('[data-theme="dark"]'))));
 T('Д-1: сліду \'v6\'px у токенах немає', css.indexOf("'v6'px")===-1);
 T('Д-1: обидві теми оголошують --r-ctl', (css.match(/--r-ctl:/g)||[]).length>=2);
 T('Д-1: жоден токен теми не має значення в лапках', !/--[a-z-]+:\s*'[^']*'/.test(css));
 T('Д-2: .el-scr замикає контекст (z-index:0)',
   /\.el-scr\{[^}]*z-index:0/.test(css.replace(/\n/g,'')));
 T('Д-2: .el-nav має явний z-index', /\.el-nav\{[^}]*z-index:12/.test(css.replace(/\n/g,'')));
 T('Д-2: острівець і бульбашка в одному шарі', (()=>{
    const f=css.replace(/\n/g,'');
    const a=(f.match(/\.el-nav\{[^}]*z-index:(\d+)/)||[])[1];
    const b=(f.match(/\.el-fabw\{[^}]*z-index:(\d+)/)||[])[1];
    return a && b && a===b; })());
 T('Д-2: рядок списку лишився з z-index:1 (фікс не чіпав симптом)',
   /\.el-sw \.el-item\{[^}]*z-index:1/.test(css.replace(/\n/g,'')));

 console.log('— L · КРОК 2 · скло шапки —');
 const css2=d.querySelector('style').textContent.replace(/\n/g,'');
 T('старого спільного hpTone у стані немає', !('hpTone' in S));
 ['hpToneL','hpToneD','hpRimL','hpRimD','hpRidgeL','hpRidgeD','hpElev','hpShA'].forEach(k=>
   T('ключ '+k+' живий і числовий', (k in S) && typeof S[k]==='number'));
 ['hpToneL','hpToneD','hpRimL','hpRimD','hpRidgeL','hpRidgeD','hpElev','hpShA'].forEach(k=>
   T('повзунок #'+k+' є', !!q('#'+k)));
 T('скло і контроль ділять одне правило матеріалу',
   /\.el-hgrp\[data-g="glass"\],\.el-hgrp\[data-g="flat"\]\{/.test(css2));
 T('кант пігулки більше не прибитий до --line',
   !/\.el-hgrp\[data-g="(surf|well|float)"\]\{[^}]*border:1px solid var\(--line\)/.test(css2));
 T('--hp-rim вживається', css2.indexOf('var(--hp-rim)')>-1);
 T('--hp-sh вживається', css2.indexOf('var(--hp-sh)')>-1);
 /* Асерт стеріг ТЕКСТ («backdrop-filter одразу після дужки») і впав від
    правильної правки — вставки background-clip. Перевіряємо механіку:
    blur є у правилі скла і його немає у спільному правилі скло+контроль. */
 T('blur лишився ТІЛЬКИ у скла', (()=>{
    const glass=(css2.match(/\.el-hgrp\[data-g="glass"\]\{[\s\S]*?\}/)||[''])[0];
    const both=(css2.match(/\.el-hgrp\[data-g="glass"\],\.el-hgrp\[data-g="flat"\]\{[\s\S]*?\}/)||[''])[0];
    return glass.indexOf('backdrop-filter')>-1 && both.indexOf('backdrop-filter')===-1; })());

 /* ГОЛОВНЕ: тема мусить МІНЯТИ обчислені токени при незмінних важелях.
    Саме цього не було до кроку 2 — і саме це анти-приклад wsd 2.8. */
 const sb=q('#sbox'), gv=n=>w.getComputedStyle(sb).getPropertyValue(n).trim();
 G("S.hgrp='glass'; render();");
 /* Умову «числа рівні» тест ставить САМ. Спиратись на збіг дефолтів не можна:
    запікання вироків розводить hpToneL/hpToneD і валить тест, який нічого не зловив. */
 G("S.hpToneL=8; S.hpToneD=8; render();");
 G("themeMode='light'; render();");
 const bgL=gv('--hp-bg'), rimL=gv('--hp-rim'), shL=gv('--hp-sh');
 G("themeMode='dark'; render();");
 const bgD=gv('--hp-bg'), rimD=gv('--hp-rim'), shD=gv('--hp-sh');
 T('--hp-rim роздільний по темах', rimL!==rimD && !!rimL && !!rimD);
 T('--hp-sh роздільний по темах', shL!==shD);
 /* Було: /0 2px \d+px/ — асерт стеріг ПРИБИТИЙ зсув 2px і зламався в ту мить,
    коли зсув став важелем. Перевіряємо механіку: тінь є і слухається важеля. */
 T('на світлій тінь малюється', /rgba\(16,16,24,/.test(shL));
 G("themeMode='light'; S.hpShY=0; render();");
 const shY0=gv('--hp-sh');
 G("S.hpShY=6; render();");
 T('зсув тіні пігулки керується важелем', shY0!==gv('--hp-sh'));
 G("S.hpShY=1; themeMode='dark'; render();");
 T('A45: на темній тіні НЕМАЄ', !/0 2px/.test(shD));
 T('A45: на темній блік по верхньому ребру Є', /inset 0 1px 0/.test(shD));
 T('тон однаковий при рівних важелях (рівність поставлена тестом)', bgL===bgD);
 G("S.hpToneD=30; render();");
 T('зсув тільки темного важеля міняє тон на темній', gv('--hp-bg')!==bgD);
 G("themeMode='light'; render();");
 T('зсув темного важеля НЕ зачепив світлу', gv('--hp-bg')===bgL);
 G("S.hpToneD=8; themeMode='dark'; render();");

 console.log('— M · контроль лишився контролем (валідність вироку §0-2) —');
 const mat=n=>{ G(`S.hgrp='${n}'; render();`); const e=q('.el-hgrp');
   const st=w.getComputedStyle(e);
   return [st.getPropertyValue('background-color'), st.getPropertyValue('border-top-color'),
           st.getPropertyValue('box-shadow'), st.getPropertyValue('padding-top')].join('|'); };
 const gl=mat('glass'), fl=mat('flat');
 T('скло і заливка збігаються в тоні/канті/тіні/падінгу', gl===fl);
 G("S.hgrp='glass'; themeMode='dark'; render();");

 console.log('— N · нові важелі оголошені в таблиці мертвих —');
 const dt=q('#deadTable').textContent;
 ['тон пігулки · св.','тон пігулки · тем.','кант пігулки · св.','кант пігулки · тем.',
  'блік верху · св.','блік верху · тем.','тінь пігулки'].forEach(n=>
   T('таблиця називає «'+n+'»', dt.indexOf(n)>-1));
 T('тінь пігулки називає A45 як винуватця', dt.indexOf('A45')>-1);

 console.log('— O · КРОК 2б · роздільник —');
 G("S.hgrp='glass'; S.hdiv=1; themeMode='light'; render();");
 T('роздільник у DOM є', !!q('.el-hdiv'));
 ['hdvIn','hdvW','hdvGap','hdvAL','hdvAD'].forEach(k=>
   T('ключ '+k+' живий і числовий', (k in S) && typeof S[k]==='number'));
 ['hdvIn','hdvW','hdvGap','hdvAL','hdvAD'].forEach(k=> T('повзунок #'+k+' є', !!q('#'+k)));
 T('другої альфи (opacity) на роздільнику немає',
   !/\.el-hdiv\{[^}]*opacity:/.test(d.querySelector('style').textContent.replace(/\n/g,'')));
 T('роздільник більше не прибитий до --line-hard',
   !/\.el-hdiv\{[^}]*background:var\(--line-hard\)/.test(d.querySelector('style').textContent.replace(/\n/g,'')));
 /* jsdom не підставляє var() в getComputedStyle — читаємо ТОКЕН, а не властивість.
    Що CSS справді споживає ці токени, доводять грепи по правилу вище. */
 T('CSS роздільника споживає всі чотири токени', ['--hdv-w','--hdv-in','--hdv-gap','--hdv-col']
   .every(t => /\.el-hdiv\{[^}]*\}/.exec(d.querySelector('style').textContent.replace(/\n/g,''))[0].indexOf('var('+t)>-1));
 const colL=gv('--hdv-col');
 G("themeMode='dark'; render();");
 T('колір роздільника роздільний по темах', gv('--hdv-col')!==colL && !!colL);
 G("themeMode='light'; S.hdvIn=0; render();");
 T('вріз 0 = на всю висоту', gv('--hdv-in')==='0px');
 G("S.hdvIn=7; S.hdvW=20; render();");
 T('товщина рахується як /10', gv('--hdv-w')==='2.0px');
 G("S.hdvW=10; S.hdvAL=0; render();");
 T('сила 0 гасить лінію повністю', /,\s*0\.00\)/.test(gv('--hdv-col')));
 G("S.hdvAL=9; render();");
 const dt2=q('#deadTable').textContent;
 ['роздільник · геометрія','роздільник · св.','роздільник · тем.'].forEach(n=>
   T('таблиця називає «'+n+'»', dt2.indexOf(n)>-1));
 G("S.hdiv=0; render();");
 T('при вимкненому роздільнику важелі оголошені мертвими',
   q('#deadTable').textContent.indexOf('роздільник · геометрія')>-1);
 T('роздільника в DOM немає', !q('.el-hdiv'));
 G("S.hdiv=1; themeMode='dark'; render();");

 console.log('— P · КРОК 3 · матеріал активного стану (B3) —');
 T('пікер ctlOn є', !!q('#pkCtlOn'));
 T('ctlOn — рядок із чотирьох дозволених',
   ['solid','tint','well','mark'].indexOf(S.ctlOn)>-1);
 ['ctlOnTintL','ctlOnTintD','ctlOnDep','ctlOnRim','ctlOnInk'].forEach(k=>
   T('ключ '+k+' живий і числовий', (k in S) && typeof S[k]==='number'));
 ['ctlOnTintL','ctlOnTintD','ctlOnDep','ctlOnRim','ctlOnInk'].forEach(k=>
   T('повзунок #'+k+' є', !!q('#'+k)));
 const css3=d.querySelector('style').textContent.replace(/\n/g,'');
 T('беззастережного правила активного чіпа більше немає',
   !/(^|\})\.el-chip\[data-on="1"\]\{/.test(css3));
 T('беззастережного правила активної кнопки більше немає',
   !/(^|\})\.el-cbtn\[data-on="1"\]\{/.test(css3));
 ['solid','tint','well','mark'].forEach(v=>{
   const sel='[data-onmat="'+v+'"] .el-chip[data-on="1"],[data-onmat="'+v+'"] .el-cbtn[data-on="1"]{';
   T('варіант '+v+' покриває І чіп, І кнопку', css3.indexOf(sel)>-1); });
 G("themeMode='light'; S.ctlOn='tint'; render();");
 T('сцена несе data-onmat', sb.dataset.onmat==='tint');
 const tL=gv('--on-tint'), rL=gv('--on-rim');
 G("themeMode='dark'; render();");
 T('тінт роздільний по темах', gv('--on-tint')!==tL);
 T('кант активного роздільний по темах', gv('--on-rim')!==rL);
 G("S.ctlOn='well'; render();");
 T('втоплення — це inset і тільки inset', /^inset /.test(gv('--on-dep')));
 T('втоплення не містить зовнішньої тіні', gv('--on-dep').indexOf(',0 ')===-1);
 G("S.ctlOnDep=0; render();");
 T('глибина 0 знімає втоплення', gv('--on-dep')==='none');
 G("S.ctlOnDep=8; render();");
 const dt3=q('#deadTable').textContent;
 ['тінт активного · св.','тінт активного · тем.','втоплення активного',
  'кант активного','чорнило активного'].forEach(n=>
   T('таблиця називає «'+n+'»', dt3.indexOf(n)>-1));
 G("S.ctlOn='solid'; render();");
 T('при суцільному кант і чорнило оголошені мертвими', (()=>{
    const t=q('#deadTable').textContent; return t.indexOf('кант активного')>-1; })());
 G("S.ctlOn='tint'; render();");

 console.log('— U · v11 · КРОК 5 · об\'єм: контактна + дальня тінь —');
 {
  G("themeMode='light'; S.fabTone='glass'; S.fabShCA=14; render();");
  const shl=q('#sbox').style.getPropertyValue('--fab-sh');
  T('на світлій дві тіні в одному box-shadow', (shl.match(/rgba\(0,0,0,/g)||[]).length>=2);
  G("S.fabShCA=0; render();");
  T('контактна вимикається нулем сили',
    (q('#sbox').style.getPropertyValue('--fab-sh').match(/rgba\(0,0,0,/g)||[]).length===1);
  /* Зсув 0 = тінь замикається рівним кільцем по діаметру — відповідь на «тінь
     тільки знизу». Перевіряємо, що нуль реально доїжджає до CSS. */
  G("S.fabShCA=14; S.fabShY=0; render();");
  T('дальня тінь уміє стати «по діаметру» (зсув 0)',
    /0 0px \d+px/.test(q('#sbox').style.getPropertyValue('--fab-sh')));
  G("S.fabShY=8; themeMode='dark'; render();");
  T('контактної тіні на темній немає (A45)',
    (q('#sbox').style.getPropertyValue('--fab-sh').match(/rgba\(0,0,0,/g)||[]).length===1);
  G("themeMode='dark'; render();");
 }

 console.log('— T · v11 · КРОК 4 · розчеплення важелів по темах —');
 {
  /* Пара мусить існувати ОБОМА половинами: половина без пари означає, що
     один із двох вироків нікуди записати — рівно те, що сталось з ctInk. */
  [['ctInkL','ctInkD'],['hbInkL','hbInkD'],['fabRimAL','fabRimAD'],
   ['fabRingAL','fabRingAD'],['aHL','aH'],['aSL','aS'],['aLL','aL'],['aSoftL','aSoft']]
   .forEach(([l,dk])=>{
     T('пара '+l+'/'+dk+' повна', (l in S) && (dk in S));
     T('повзунок #'+l+' є', !!q('#'+l));
   });
  /* Суфікс D більше не означає одночасно «дельта» і «dark» в одному наборі. */
  T('fabBlur/fabSat перейменовано з ...D', (('fabBlur' in S)&&('fabSat' in S)) && !('fabBlurD' in S) && !('fabSatD' in S));
  T('старі спільні ключі прибрано',
    !('ctInk' in S) && !('hbInk' in S) && !('fabRimA' in S) && !('fabRingA' in S));

  /* Розчеплення має СЕНС лише тоді, коли половини справді дають різний результат. */
  G("S.ctInkL=95; S.ctInkD=5; themeMode='light'; render();");
  const inkL=q('#sbox').style.getPropertyValue('--ct-ink');
  G("themeMode='dark'; render();");
  const inkD=q('#sbox').style.getPropertyValue('--ct-ink');
  T('чорнило міста різне на темах', inkL!==inkD && !!inkL);

  /* Акцент світлої був прибитий у :root — важіль мусить його зрушити. */
  G("themeMode='light'; S.aHL=200; render();");
  const acc1=q('#sbox').style.getPropertyValue('--accent');
  G("S.aHL=340; render();");
  const acc2=q('#sbox').style.getPropertyValue('--accent');
  T('акцент світлої керується важелем', !!acc1 && acc1!==acc2);
  G("themeMode='dark'; render();");
 }

 console.log('— S · v11 · КРОК 0б · паспорт добирає CSS за ознакою —');
 {
  T('cssPassport — іменована функція', typeof w.cssPassport==='function');
  T('cssCovered читає її текст', typeof w.cssCovered==='function' && w.cssCovered().size>20);
  T('cssGap існує', typeof w.cssGap==='function');
  /* Головне: непокриття рахується від ЖИВИХ, і зараз воно нульове. */
  const dead=w.deadSet(), live={}; Object.keys(S).forEach(k=>{ if(!dead.has(k)) live[k]=S[k]; });
  T('живих важелів поза CSS-секцією немає', w.cssGap(live).length===0);
  /* Доведення детектора: вигаданий живий ключ мусить проявитись у щілині. */
  T('підкинутий ключ ловиться як непокритий',
    w.cssGap(Object.assign({__probe__:1}, live)).indexOf('__probe__')>-1);
  w.document.getElementById('copyBtn').click();
  const pass=q('#out').value;
  T('паспорт друкує рядок непокриття', /CSS-СЕКЦІЯ НЕ ПОКРИВАЄ \d+ живих важелів/.test(pass));
  T('штамп білда в паспорті не протухлий', pass.indexOf('headbench '+G('LOCK_BUILD'))>-1);
 }

 console.log('— R · v11 · Д-3 · заголовок не штовхає групу кнопок —');
 {
  const cssR=d.querySelector('style').textContent.replace(/\n/g,'');
  T('заголовок уміє стискатись (min-width:0)',
    /\.el-inlinettl\{[^}]*min-width:0/.test(cssR));
  T('група кнопок оголошена нестисним якорем (flex:none)',
    /\.el-hgrp\{flex:none\}/.test(cssR));
  /* Структурний бік: група мусить бути ОСТАННІМ вузлом appbar на всіх табах,
     інакше «якір правого краю» — це слова, а не верстка. */
  ['ph','eq','ov'].forEach(t=>{
    G("tab='"+t+"'; render();");
    const ab=q('.el-appbar'), last=ab && ab.lastElementChild;
    T('таб '+t+': останній вузол appbar — група або кебаб',
      !!last && (last.classList.contains('el-hgrp') || last.classList.contains('el-hbtn')));
  });
  G("tab='ph'; render();");
  T('інлайн-заголовок у DOM є', !!q('.el-inlinettl'));
 }

 console.log('— Q · КРОКИ 4–6 · місто · низ · бейдж —');
 const K=['ctH','ctSize','ctR','ctPx','ctRimL','ctRimD','ctFill','ctInkL','ctInkD',
          'navH','nvSz','nvSw','nvLbl','nvGap','bdH','bdR','bdSize','bdFillL','bdFillD'];
 K.forEach(k=>{ T('повзунок #'+k+' є', !!q('#'+k)); T('стан має '+k, k in S); });
 const css4=d.querySelector('style').textContent.replace(/\n/g,'');
 T('місто: висота явна, не з padding', /\.el-city\{[^}]*height:var\(--ct-h/.test(css4));
 T('місто: вміст центрується', /\.el-city\{[^}]*align-items:center/.test(css4));
 T('місто більше не прибите до --line', !/\.el-city\{[^}]*var\(--line\)/.test(css4));
 T('нав-іконка параметрична', /\.el-nav svg\{[^}]*var\(--nv-sz/.test(css4));
 T('бейдж параметричний', /\.el-badge\{[^}]*var\(--bd-h/.test(css4));
 G("themeMode='light'; render();");
 const cR=gv('--ct-rim'), bF=gv('--bd-fill');
 G("themeMode='dark'; render();");
 T('кант міста роздільний по темах', gv('--ct-rim')!==cR && !!cR);
 T('підкладка бейджа роздільна по темах', gv('--bd-fill')!==bF && !!bF);
 G("S.ctFill=0; render();");
 T('заливка 0 = прозоро (форму несе кант)', gv('--ct-fill')==='transparent');
 G("S.navH=72; render();");
 T('navH керує токеном', gv('--navH')==='72px');
 T('навігація і бульбашка ділять --navH',
   /\.el-fabw\{[^}]*var\(--navH/.test(css4) && /\.el-nav\{[^}]*var\(--navH/.test(css4));
 T('нижній відступ списку теж їде за --navH', /\.el-scr\{[^}]*var\(--navH/.test(css4));
 G("S.navH=60; render();");
 const dt4=q('#deadTable').textContent;
 ['пігулка міста · геометрія','пігулка міста · кант тем.','пігулка міста · заливка',
  'низ · геометрія','бейдж · геометрія','бейдж · підкладка тем.'].forEach(n=>
   T('таблиця називає «'+n+'»', dt4.indexOf(n)>-1));
 const pass2=(q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true})), q('#out').value);
 ['.el-city{','.el-nav{','.el-badge{'].forEach(n=>
   T('паспорт друкує '+n, pass2.indexOf(n)>-1));
 T('паспорт називає «+» як пару до navH', pass2.indexOf('пара до navH')>-1);

 console.log('— V · v12 · КРОК 5б · spread, товщина кільця, порядок шарів —');
 {
  /* Розбір списку тіней: кома всередині rgba(...) не є роздільником шарів. */
  const split = splitTop;
  const sh = () => q('#sbox').style.getPropertyValue('--fab-sh');

  /* Ключі існують і числові — форма, не значення (2-А). */
  ['fabShS','fabShCS','fabRingW'].forEach(k=>{
    T('ключ '+k+' існує і числовий', (k in S) && typeof S[k]==='number');
    T('повзунок #'+k+' є', !!q('#'+k));
  });
  T('ключ fabShOrd існує', 'fabShOrd' in S);
  T('пікер #pkShOrd є і має два варіанти',
    !!q('#pkShOrd') && qa('#pkShOrd button[data-v]').length===2);

  G("themeMode='light'; S.fabTone='glass'; S.fabEdge='both'; S.fabShCA=14; S.fabShS=-6; S.fabShCS=0; S.fabShOrd='over'; render();");
  /* Головне: четвертий параметр узагалі доїжджає в CSS — у v11 його не було. */
  T('дальня тінь має четвертий параметр (spread)', /0 \d+px \d+px -?\d+px rgba/.test(sh()));
  T("від'ємний spread лишається від'ємним", /px -\d+px rgba/.test(sh()));
  G("S.fabShS=4; render();");
  T('додатний spread теж доїжджає', / 4px rgba/.test(sh()));
  G("S.fabShS=-6; render();");

  /* Порядок: перша в списку малюється ЗВЕРХУ. Контактну впізнаємо за її
     власним розмиттям, дальню — за елевацією; числа ставить сам тест. */
  G("S.fabShCB=2; S.fabElev=14; render();");
  const iOf = (arr,re) => arr.findIndex(x=>re.test(x));
  let L = split(sh()).filter(x=>!/^inset/.test(x));
  const iC = iOf(L,/ 2px -?\d+px rgba\(0,0,0/), iF = iOf(L,/ 14px -?\d+px rgba\(0,0,0/);
  T('контактна і дальня обидві в списку', iC>-1 && iF>-1);
  T('контактна лежить ПЕРЕД дальньою (малюється зверху)', iC>-1 && iF>-1 && iC<iF);

  /* Порядок відносно ореолу — керований, а не константа. */
  const iH1 = iOf(L,/rgba\(255,255,255/);
  T("при «над» контактна перед ореолом", iH1>-1 && iC<iH1);
  G("S.fabShOrd='under'; render();");
  L = split(sh()).filter(x=>!/^inset/.test(x));
  const iC2 = iOf(L,/ 2px -?\d+px rgba\(0,0,0/), iH2 = iOf(L,/rgba\(255,255,255/);
  T("при «під» ореол перед контактною", iH2>-1 && iC2>-1 && iH2<iC2);
  T('дальня лишається найнижчою в обох порядках',
    iOf(L,/ 14px -?\d+px rgba\(0,0,0/)===L.length-1);
  G("S.fabShOrd='over'; render();");

  /* Нуль spread не ламає формат: параметр присутній завжди, інакше рядок
     став би трипараметричним і наступний важіль читався б як колір. */
  G("S.fabShCS=0; render();");
  T('нульовий spread контактної не ламає формат', / 2px 0px rgba\(0,0,0/.test(sh()));

  /* Товщина кільця — важіль, а не прибиті 1.5px.
     v15 · переписано з ЛІТЕРАЛА на ВІДНОШЕННЯ (2-Е самері S10): кільце тепер
     відлічується від внутрішнього краю канта, і прибите «0.5px» померло б від
     ПРАВИЛЬНОЇ правки. Стережемо поведінку, а не позицію символів. */
  const rad = () => split(sh()).filter(x => /^inset 0 0 0 /.test(x))
                      .map(x => parseFloat(x.match(/inset 0 0 0 ([\d.]+)px/)[1]));
  G("S.fabEdge='both'; S.fabRimW=10; S.fabRingW=15; render();");
  const r15 = rad();
  G("S.fabRingW=5; render();");
  const r5 = rad();
  T('товщина кільця керується важелем', r15.length===2 && r5.length===2 && r15[1] > r5[1]);
  T('кільце лишається inset', /^inset /.test(sh()));
  /* Головний детектор кроку 0. */
  T('кільце ЗАВЖДИ ширше за кант — кант його не з\'їдає',
    r5[1] > r5[0] && r15[1] > r15[0]);
  G("S.fabRimW=30; render();");
  const rMax = rad();
  T('посилення канта штовхає кільце вглиб, а не гасить його',
    rMax[0] > r5[0] && rMax[1] > r5[1]);
  T('видима товщина кільця не залежить від канта',
    (rMax[1]-rMax[0]).toFixed(1) === (r5[1]-r5[0]).toFixed(1));
  G("S.fabRimW=0; render();");
  T('кант знято — кільце лягає на кромку без зсуву', rad().length===1 && rad()[0]===0.5);
  G("S.fabRimW=10; S.fabRingW=5; render();");

  /* Мертві за умовою: порядок без ореолу судити нічим. */
  G("S.fabEdge='ring'; render();");
  T('без ореолу порядок оголошений мертвим',
    q('#deadTable').textContent.indexOf('порядок тіней «+»')>-1);
  G("S.fabEdge='none'; render();");
  T('без краю товщина кільця оголошена мертвою',
    q('#deadTable').textContent.indexOf('товщина кільця')>-1);
  G("S.fabEdge='both'; themeMode='dark'; render();");
  T('на темній контактної немає, spread дальньої лишається (A45)',
    split(sh()).filter(x=>/rgba\(0,0,0/.test(x)).length===1 && /px -?\d+px rgba\(0,0,0/.test(sh()));
  G("themeMode='light'; render();");

  /* Паспорт мусить нести всі чотири — інакше вирок нікуди записати. */
  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  const pV=q('#out').value;
  T('паспорт друкує spread дальньої', /дальня тінь 0 \d+px \d+px -?\d+px/.test(pV));
  T('паспорт друкує spread контактної', /контактна 0 \d+px \d+px -?\d+px/.test(pV));
  T('паспорт друкує ЕФЕКТИВНУ товщину кільця + видиму', /кільце [\d.]+×[\d.]+px \(видимих [\d.]+\)/.test(pV));
  T('паспорт друкує порядок шарів', pV.indexOf('порядок ')>-1);
  T('щілина покриття CSS лишилась 0', /CSS-СЕКЦІЯ НЕ ПОКРИВАЄ 0 живих важелів/.test(pV));
 }

 console.log('— W · v13 · КРОК 5в-1 · шейдинг тіла як матеріал родини —');
 {
  const gv2=n=>q('#sbox').style.getPropertyValue(n);
  const sh=()=>q('#sbox').style.getPropertyValue('--fab-sh');

  /* Пари по темах — ВХІДНА умова важеля, не пост-фікс (правило S10). */
  [['shTopL','shTopD'],['shBotL','shBotD'],['shSpecL','shSpecD'],['shRimL','shRimD']]
    .forEach(([l,d])=>{
      T('пара '+l+'/'+d+' повна', (l in S)&&(d in S));
      T('повзунок #'+l+' є', !!q('#'+l));
      T('повзунок #'+d+' є', !!q('#'+d));
    });
  /* v16 · було: «спільний важіль shX існує». Асерт кодував ПОПЕРЕДНЮ конструкцію
     і помер від правильної правки — третій випадок за три сесії (2-Е самері S10).
     Тепер стережемо не спільність, а РОЗДІЛЬНІСТЬ: чотири ключі геометрії мають
     існувати парами, і старих імен не має лишитись жодного. */
  ['shX','shY','shSpecS','shRimB'].forEach(k=>
    T('старий спільний ключ '+k+' знято', !(k in S)));
  ['shX','shY','shSpecS','shRimB'].forEach(k=>
    T('геометрія '+k+' розщеплена по темах',
      typeof S[k+'L']==='number' && typeof S[k+'D']==='number'));
  T('пікер #pkShWho має чотири області', qa('#pkShWho button[data-v]').length===4);

  /* Вимкнено = справді none на всіх трьох, а не «прозорий градієнт». */
  G("themeMode='light'; S.shWho='off'; render();");
  T('вимкнено: усі три поверхні чисті',
    gv2('--fab-shade').trim()==='none' && gv2('--nav-shade').trim()==='none' && gv2('--hp-shade').trim()==='none');

  G("S.shWho='fab'; render();");
  T('«лише +»: шейдинг тільки на бульбашці',
    gv2('--fab-shade').indexOf('radial-gradient')>-1
    && gv2('--nav-shade').trim()==='none' && gv2('--hp-shade').trim()==='none');
  G("S.shWho='fabnav'; render();");
  T('«+ і острівець»: капсула шапки лишається чистою',
    gv2('--nav-shade').indexOf('radial-gradient')>-1 && gv2('--hp-shade').trim()==='none');
  G("S.shWho='all'; render();");
  T('«усі три»: капсула теж отримала шейдинг', gv2('--hp-shade').indexOf('radial-gradient')>-1);
  T('три поверхні несуть ОДНАКОВЕ значення (одна мова матеріалу)',
    gv2('--fab-shade')===gv2('--nav-shade') && gv2('--nav-shade')===gv2('--hp-shade'));

  /* Два шари, і блік — ПЕРШИЙ, тобто зверху. Це те, що ловить ін'єкція. */
  const layers = splitTop(gv2('--fab-shade'));
  T('шейдинг має рівно два шари', layers.length===2);
  T('блік лежить ПЕРШИМ (малюється зверху)', /circle \d+px at/.test(layers[0]));
  T('тіло лежить другим і несе затемнення низу', /rgba\(0,0,0,/.test(layers[1]||''));

  /* Радіус бліка у px — інакше на широкій капсулі пляма стала б еліпсом. */
  T('радіус бліка заданий у px, не у %', !/circle \d+% at/.test(gv2('--fab-shade')));
  G("S.shSpecSL=30; render();");
  T('радіус бліка керується важелем', /circle 30px at/.test(gv2('--fab-shade')));
  G("S.shSpecSL=12; render();");

  /* v16 · було: «позиція джерела НЕ залежить від теми». Це твердження і було
     дефектом — A39 у новому місці. Тепер вимога протилежна. */
  G("S.shXL=70; S.shXD=20; render();"); const x1=gv2('--fab-shade');
  G("themeMode='dark'; render();");
  T('позиція джерела ЗАЛЕЖИТЬ від теми',
    /at 70%/.test(x1) && /at 20%/.test(gv2('--fab-shade')) && x1!==gv2('--fab-shade'));
  /* А сили — залежать, інакше розчеплення було б декоративним. */
  G("S.shTopL=5; S.shTopD=55; themeMode='light'; render();");
  const t1=gv2('--fab-shade'); G("themeMode='dark'; render();");
  T('сила світла тіла різна на темах', t1!==gv2('--fab-shade'));
  G("themeMode='light'; S.shXL=38; S.shXD=32; S.shTopL=24; S.shTopD=16; render();");

  /* Rim: inset, після кільця, і зникає разом із шейдингом. */
  G("S.fabTone='glass'; S.fabEdge='both'; S.shWho='fab'; S.shRimL=26; render();");
  /* Позиції не прибиваємо: у v14 перед кільцем став кант, і асерт на індекс
     помер би від правильної зміни. Перевіряємо ВІДНОШЕННЯ — rim після кільця. */
  const insets = splitTop(sh()).filter(x=>/^inset/.test(x));
  const iRing = insets.findIndex(x=>/inset 0 0 0 1\.5px/.test(x));
  const iRim  = insets.findIndex(x=>/inset 0 -\d+px/.test(x));
  T('rim присутній окремим inset', iRim>-1);
  T('rim іде ПІСЛЯ кільця', iRing>-1 && iRim>iRing);
  G("S.shWho='off'; render();");
  T('вимкнений шейдинг знімає і rim',
    splitTop(sh()).filter(x=>/inset 0 -\d+px/.test(x)).length===0);
  G("S.shWho='fab'; S.shRimL=0; render();");
  T('нульова сила rim знімає шар',
    splitTop(sh()).filter(x=>/inset 0 -/.test(x)).length===0);
  G("S.shRimL=26; render();");

  /* Мертві за умовою. */
  G("S.shWho='off'; render();");
  T('вимкнений шейдинг оголошує геометрію мертвою',
    q('#deadTable').textContent.indexOf('шейдинг · геометрія')>-1);
  G("S.shWho='fab'; themeMode='light'; render();");
  T('на світлій темні важелі шейдингу мертві',
    q('#deadTable').textContent.indexOf('шейдинг · темна')>-1);

  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  const pW=q('#out').value;
  T('паспорт друкує рядок шейдингу', pW.indexOf('шейдинг:')>-1);
  T('паспорт друкує rim', /rim \d+px\//.test(pW));
  T('щілина покриття CSS лишилась 0 після 13 нових важелів',
    /CSS-СЕКЦІЯ НЕ ПОКРИВАЄ 0 живих важелів/.test(pW));
 }

 console.log('— X · v14 · ФІКС КРАЮ · кант не рамкою —');
 {
  const css=[...d.querySelectorAll('style')].map(x=>x.textContent).join('\n');
  const fabRule=(css.match(/\.el-fab\[data-t="glass"\]\{[\s\S]*?\}/)||[''])[0];
  T('бульбашка більше не має border', fabRule.indexOf('border:1px')===-1);
  T('бульбашка обрізає фон по padding-box', /background-clip:padding-box/.test(fabRule));
  T('острівець обрізає фон по padding-box',
    /\.el-nav\{[\s\S]*?background-clip:padding-box/.test(css));
  T('капсула шапки обрізає фон по padding-box',
    /\.el-hgrp\[data-g="glass"\]\{background-clip:padding-box/.test(css));

  G("themeMode='light'; S.fabTone='glass'; S.fabEdge='both'; S.shWho='off'; S.fabRimW=10; render();");
  const ins=()=>splitTop(q('#sbox').style.getPropertyValue('--fab-sh')).filter(x=>/^inset/.test(x));
  T('кант приїхав inset-тінню', ins().some(x=>/inset 0 0 0 1px/.test(x)));
  /* v15 · відношення замість літералів: порядок шарів + кільце глибше канта. */
  T('кант стоїть ПЕРЕД кільцем і кільце глибше', (()=>{
    const r = ins().filter(x=>/^inset 0 0 0 /.test(x))
                   .map(x=>parseFloat(x.match(/inset 0 0 0 ([\d.]+)px/)[1]));
    return r.length===2 && r[1] > r[0]; })());
  G("S.fabRimW=25; render();");
  T('товщина канта керується важелем', ins().some(x=>/inset 0 0 0 2\.5px/.test(x)));
  G("S.fabRimW=0; render();");
  T('нуль знімає кант зовсім', !ins().some(x=>/inset 0 0 0 [\d.]+px rgba\(20,20,30/.test(x)));
  G("S.fabRimW=10; render();");
  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  T('паспорт друкує товщину канта', /кант ×[\d.]+px/.test(q('#out').value));
 }

 console.log('— Y · v16 · КРОК 1 · геометрія шейдингу роздільна по темах —');
 {
  const sh=()=>q('#sbox').style.getPropertyValue('--fab-shade');
  G("S.shWho='fab'; themeMode='light'; S.shXL=38; S.shYL=18; S.shXD=70; S.shYD=80; render();");
  const L=sh();
  G("themeMode='dark'; render();");
  const D=sh();
  /* Відношення, не літерали (2-Е): вимагаємо РОЗХОДЖЕННЯ, не конкретних чисел —
     числа живуть у valuesLOCK, смоук про них нічого не знає (S9, крок 1б). */
  T('полюс шейдингу розходиться між темами', L!==D);
  T('полюс читається з темного двійника на темній', D.indexOf('70% 80%')>-1);
  T('полюс читається зі світлого двійника на світлій', L.indexOf('38% 18%')>-1);
  G("S.shSpecSL=12; S.shSpecSD=30; themeMode='light'; render();");
  const rL=sh(); G("themeMode='dark'; render();");
  T('радіус бліка розходиться між темами', rL!==sh());
  G("S.shRimL=26; S.shRimD=26; S.shRimBL=4; S.shRimBD=16; themeMode='light'; render();");
  const iL=q('#sbox').style.getPropertyValue('--fab-sh');
  G("themeMode='dark'; render();");
  T('розтяг rim розходиться між темами',
    /inset 0 -4px 6px/.test(iL) && /inset 0 -16px 18px/.test(q('#sbox').style.getPropertyValue('--fab-sh')));

  /* Мертві по темі: геометрія другої теми мусить називатись мертвою, інакше
     темний борг знову стане невидимим (той самий клас, що §3-п.13б). */
  G("themeMode='light'; render();");
  const dt=q('#deadTable').textContent;
  T('на світлій темна геометрія оголошена мертвою', dt.indexOf('шейдинг · геометрія тем.')>-1);
  G("themeMode='dark'; render();");
  T('на темній світла геометрія оголошена мертвою',
    q('#deadTable').textContent.indexOf('шейдинг · геометрія св.')>-1);
  G("themeMode='light'; render();");

  /* Міграція ключів (1д): старий ключ переїхав, а не протух. */
  T('стара геометрія більше не існує в S', G("['shX','shY','shSpecS','shRimB'].filter(k=>k in S).length")===0);
  /* v17_4 · хід 2: ціль стала масивом, і чотирьох ключів уже мало. Твердження
     оновлені, не зняті — форма змінилась, вимога лишилась. */
  T('карта міграції накриває стару геометрію',
    G("['shX','shY','shSpecS','shRimB'].every(k=>k in LOCK_MIGRATE)"));
  T('геометрія шейдингу цілиться у СВІТЛІ двійники',
    G("['shX','shY','shSpecS','shRimB'].every(k=>LOCK_MIGRATE[k].length===1 && /L$/.test(LOCK_MIGRATE[k][0]) && (LOCK_MIGRATE[k][0] in S))"));
  T('міграція не воскрешає вже переставлений ключ', (()=>{
    G("LOCKS['shXL']=99; LOCK_STALE=['shX']; o_v_cache={shX:38}; lockMigrate();");
    return G("LOCKS['shXL']")===99 && G("LOCK_STALE.length")===0; })());
  T('міграція переносить значення, коли цілі ще немає', (()=>{
    G("delete LOCKS['shXL']; LOCK_STALE=['shX']; o_v_cache={shX:38}; lockMigrate();");
    return G("LOCKS['shXL']")===38; })());
  G("delete LOCKS['shXL']; LOCK_STALE=[]; S.shXL=38; S.shYL=18; S.shXD=32; S.shYD=26; "
    +"S.shSpecSL=12; S.shSpecSD=12; S.shRimBL=10; S.shRimBD=6; S.shRimL=4; S.shRimD=34; render();");

  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  T('паспорт друкує полюс поточної теми', /джерело \d+%\/\d+%/.test(q('#out').value));
  T('щілина покриття CSS не зросла від 8 нових важелів',
    /CSS-СЕКЦІЯ НЕ ПОКРИВАЄ 0 живих важелів/.test(q('#out').value));
 }

 console.log('— Ф0 · v17 · пікери підключені, не лише намальовані —');
 {
  /* Клас дефекту, спійманий оператором на девайсі у v17: розмітка пікера є,
     важіль у S є, таблиця мертвих про нього знає — а `pick(id,key)` не викликано.
     Кнопки німі, і ЖОДЕН наявний детектор цього не бачив, бо всі вони писали
     в S напряму через G("S.bg='all'"), обходячи саму кнопку.
     Гейт — суцільний і generic: кожен пікер у документі мусить реагувати. */
  const picks = qa('.bx-pick[data-dk]');
  T('пікери в документі є', picks.length > 0);
  const mute = [];
  picks.forEach(p => {
    const k = p.dataset.dk, cur = String(G('S.'+JSON.stringify(k).slice(1,-1)) ?? G('S["'+k+'"]'));
    const alt = [...p.querySelectorAll('button[data-v]')]
      .find(b => b.dataset.v !== cur && !b.classList.contains('bx-lock'));
    if (!alt) return;                       /* єдина опція — нема що перемикати */
    const want = alt.dataset.v;
    alt.dispatchEvent(new w.MouseEvent('click', {bubbles:true}));
    if (String(G('S["'+k+'"]')) !== want) mute.push(k);
    G('S["'+k+'"]=' + (isNaN(+cur) ? JSON.stringify(cur) : cur) + '; render();');
  });
  T('жоден пікер не німий (усі зареєстровані в pick())',
    mute.length === 0 || (console.log('    німі: ' + mute.join(', ')), false));
 }

 console.log('— Ф · v17 · К1 · фон екрана як підкладка скла —');
 {
  const aur=()=>q('#sbox').style.getPropertyValue('--bg-aur');
  const dead=()=>q('#deadTable').textContent;

  /* 1. Аркуш = ВІДСУТНЯ властивість, не порожня. Фолбек var(--bg-aur,none)
     спрацьовує лише на відсутній; порожній рядок лишив би недійсне значення. */
  G("S.bg='sheet'; themeMode='light'; render();");
  T('аркуш не ставить --bg-aur зовсім', aur()==='');
  T('носій оголошений у CSS, а не окремим шаром',
    /\.screenbox\{background-image:var\(--bg-aur,none\)\}/.test(html));
  T('аврора не заведена псевдоелементом', !/\.screenbox::before[^}]*radial-gradient/.test(html));

  /* 2. Режим = позиції. Три еліпси в обох робочих режимах, і позиції РІЗНІ. */
  G("S.bg='all'; render();");
  const A=aur();
  T('режим «всюди» дає три еліпси', (A.match(/radial-gradient/g)||[]).length===3);
  G("S.bg='chrome'; render();");
  const C=aur();
  T('режим «під хромом» дає три еліпси', (C.match(/radial-gradient/g)||[]).length===3);
  T('режими розходяться позиціями, не силою', A!==C);
  T('під хромом плями зсунуті вниз', /at 50% 97%/.test(C));
  T('всюди плями розкладені по площі', /at 20% 40%/.test(A));

  /* 3. A39 на новій осі: сила роздільна по темах, відтінок спільний. */
  /* ⚠ Друга пастка хибного ✓ (wsd 1.15), спіймана на впорскуванні: перевірка
     «рядки різні» тут НІЧОГО не доводить — світлота еліпса теж перемикається
     темою (70/55), тож рядок розходиться навіть зі спільними альфами.
     Судимо саме АЛЬФУ, витягнуту з першого шару, а не рядок цілком. */
  const a1 = () => { const m = aur().match(/hsl\([^)]*\/ ([\d.]+)\)/); return m ? +m[1] : NaN; };
  G("S.bg='all'; S.bgA1L=10; S.bgA1D=40; themeMode='light'; render();");
  const aL = a1(); G("themeMode='dark'; render();");
  const aD = a1();
  T('альфа аврори читається з важеля світлої', Math.abs(aL-0.10)<1e-6);
  T('альфа аврори читається з важеля темної', Math.abs(aD-0.40)<1e-6);
  T('сила аврори роздільна по темах, не спільна', aL!==aD);
  /* v17_4 · хід 2 · ЦЕ ТВЕРДЖЕННЯ ПЕРЕВЕРНУТО СВІДОМО. У v17 воно вимагало
     СПІЛЬНОГО кута на обох темах; хід 2 довів, що спільним він бути не може:
     світіння й кольорова тінь — різні явища. Твердження не знято, а
     розвернуто — інакше зникла б згадка, що тут колись стояла інша вимога. */
  G("S.bgH1L=300; S.bgH1D=120; themeMode='light'; render();");
  const hL=aur(); G("themeMode='dark'; render();");
  T('відтінок РОЗДІЛЬНИЙ — кут іде з гілки своєї теми',
    /hsl\(300/.test(hL) && /hsl\(120/.test(aur()) && !/hsl\(300/.test(aur()));

  /* 4. Нахил — окремий носій, і він ОСТАННІЙ шар (найглибший). */
  G("S.bgTiltD=0; render();");
  T('нуль нахилу не додає лінійного шару', !/linear-gradient/.test(aur()));
  G("S.bgTiltD=8; render();");
  T('нахил додається окремим шаром', /linear-gradient\(170deg/.test(aur()));
  T('нахил лежить останнім, під плямами',
    aur().lastIndexOf('linear-gradient') > aur().lastIndexOf('radial-gradient'));
  G("S.bgTiltD=0; render();");

  /* 5. Покриття. ⚠ Пастка хибного ✓, спіймана на собі при написанні цього
     смоука: таблиця друкує ВСІ рядки й позначає кожен «живий ‖ мертвий», тому
     перевірка «мітка присутня» проходить ЗАВЖДИ і нічого не доводить (wsd 1.15 —
     детектор перевіряється в обидва боки). Читаємо СТАН біля мітки, не мітку. */
  const st = lbl => {
    const m = dead().match(new RegExp(
      lbl.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + '[\\s\\S]{0,120}?(живий|мертвий)'));
    return m ? m[1] : '—'; };
  G("S.bg='sheet'; themeMode='light'; render();");
  T('аркуш робить відтінки МЕРТВИМИ', st('фон · відтінки · св.')==='мертвий');
  T('аркуш робить розмах МЕРТВИМ', st('фон · розмах')==='мертвий');
  T('аркуш робить сили світлої МЕРТВИМИ', st('фон · сили · св.')==='мертвий');
  G("S.bg='all'; render();");
  T('робочий режим ОЖИВЛЯЄ відтінки', st('фон · відтінки · св.')==='живий');
  T('робочий режим оживляє сили поточної теми', st('фон · сили · св.')==='живий');
  T('на світлій сили ТЕМНОЇ лишаються мертвими', st('фон · сили · тем.')==='мертвий');
  G("themeMode='dark'; render();");
  T('перемикання теми міняє, чия сила жива', st('фон · сили · тем.')==='живий'
    && st('фон · сили · св.')==='мертвий');

  /* 6. Паспорт бере рядок із ТІЄЇ Ж функції — звіряємо байт-у-байт зі стендом. */
  G("S.bg='all'; themeMode='dark'; S.bgA1D=33; render();");
  const live=aur();
  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  T('паспорт друкує фон', /background-image:radial-gradient/.test(q('#out').value));
  T('паспорт збігається зі стендом байт-у-байт', q('#out').value.indexOf(live)>-1);
  G("S.bg='sheet'; themeMode='light'; render();");
  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  T('паспорт називає аркуш явно, а не мовчить', /фон: аркуш/.test(q('#out').value));
 }

 /* ---- Ф2 · v17_2 · К1-б · КОНСТАНТА → ВАЖІЛЬ ------------------------------
    Клас дефекту, від якого страхує ця секція: важіль ІСНУЄ, але його межа або
    його зчитування лишились старими — стенд показує повзунок, який фізично не
    доводить до зони суду. Саме так `dkL` мовчки тримав раунд у 4–12 %, коли
    робоча зона починається з 15 %. Повзунок без діапазону = німий пікер (1.20). */
 {
  console.log('— Ф2 · v17_2 · К1-б · константа стала важелем —');

  /* 1 · стеля ґрунту дотягується до робочої зони GlassKit (15–25 %). */
  T('dkL max ≥ 22 — стеля покриває зону 15–25 %',
    +q('#dkL').max >= 22 && +q('#dkL').min <= 4);

  /* 2 · чотири нові важелі присутні як контроли, а не лише як ключі стану. */
  T('bgLtL · bgLtD · bgSatL · bgSatD існують у DOM',
    ['bgLtL','bgLtD','bgSatL','bgSatD'].every(k => q('#'+k)));

  /* 3 · Головне. Рендер мусить ЧИТАТИ важіль, а не хардкод. Перевіряємо не
     наявність контрола, а зміну ВИХОДУ: зсув світлоти зобов'язаний змінити
     рядок градієнта. Твердження на присутність ключа тут проспало б дефект,
     бо ключ можна додати й не підключити. */
  G("S.bg='chrome'; themeMode='light'; render();");
  const bgA = G("aurLayers(false)");
  G("S.bgLtL=40; render();");
  const bgB = G("aurLayers(false)");
  G("S.bgLtL=70; S.bgSatL=20; render();");
  const bgC = G("aurLayers(false)");
  T('bgLtL реально керує світлотою еліпса', bgA && bgB && bgA !== bgB);
  T('bgSatL реально керує насиченістю еліпса', bgC && bgC !== bgA);

  /* 4 · Роздільність за темою — не косметика: світла пляма мусить бути темнішою
     за канву (кольорова тінь), темна — світлішою (світіння). Спільне число
     фізично не може обслуговувати обидва явища. */
  G("S.bgLtL=58; S.bgLtD=55; S.bg='chrome'; render();");
  T('світла й темна беруть РІЗНІ джерела світлоти',
    G("aurLayers(false)") !== G("aurLayers(true)"));

  /* 5 · Оголошення дому. Нові важелі мусять жити в таблиці залежностей поруч
     зі своїми родичами по темі, інакше вони «живі» при фоні=аркуш і мовчки
     осідають у щілині покриття паспорта (§3-Б). */
  G("S.bg='sheet'; render();");
  const dead = G("Array.from(deadSet())");
  T('нові важелі оголошені мертвими при фоні=аркуш',
    ['bgLtL','bgLtD','bgSatL','bgSatD'].every(k => dead.indexOf(k)>-1));

  G("S.bg='sheet'; S.bgLtL=70; S.bgLtD=55; S.bgSatL=65; S.bgSatD=65; render();");
 }

 /* ---- Ф3 · v17_3 · К0-б · ПАСПОРТ ЗБИРАЄТЬСЯ З ДВОХ ФУНКЦІЙ ----------------
    Клас дефекту: рядок непокриття рахує ключі по ОДНІЙ функції, а паспорт
    годують дві (cssPassport + aurLayers). Наслідок — не пропуск, а ХИБНИЙ ✗:
    десять аврорних імен, чиї значення в паспорті Є. Стабільна брехня гірша за
    мовчання: її швидко починають читати як фон, і справжній пропуск тоне. */
 {
  console.log('— Ф3 · v17_3 · К0-б · рядок непокриття не бреше —');

  /* 1 · Ознака, не список. Аврорні ключі мусять потрапляти в покриття тому,
     що вони згадані в генераторі паспорта, а не тому, що їх вписали руками. */
  G("S.bg='chrome'; themeMode='light'; render();");
  const cov = G("Array.from(cssCovered())");
  T('cssCovered бачить ключі з aurLayers, не лише з cssPassport',
    ['bgH1L','bgH2L','bgH3L','bgSpread','bgLtL','bgSatL','bgA1L','bgTiltL']
      .every(k => cov.indexOf(k)>-1));

  /* 2 · Головне: вихід, а не наявність. У стані «під хромом» рядок непокриття
     мусить бути ПОРОЖНІЙ на обох темах — саме там жив хибний ✗. */
  const gapOf = () => G("cssGap(Object.fromEntries(Object.keys(S).filter(k=>!deadSet().has(k)).map(k=>[k,S[k]])))");
  T('під хромом · світла: непокриття порожнє', gapOf().length === 0);
  G("themeMode='dark'; render();");
  T('під хромом · темна: непокриття порожнє',  gapOf().length === 0);

  /* 3 · Контр-проба (1.15): детектор мусить лишатись ЗДАТНИМ кричати. Якщо
     ключ справді випав з обох генераторів — він зобов'язаний з'явитись у
     непокритті. Інакше ми не полагодили детектор, а вимкнули його. */
  G("window.__cssPassport_orig = cssPassport;");
  const stillCatches = G(
    "(function(){var live={};Object.keys(S).forEach(function(k){if(!deadSet().has(k))live[k]=S[k];});"
    + "live.__fake_lever__=1;return cssGap(live).indexOf('__fake_lever__')>-1;})()");
  T('детектор і далі ловить справді непокритий важіль', stillCatches === true);

  G("S.bg='sheet'; themeMode='light'; render();");
 }

 /* ---- Ф4 · v17_4 · ХІД 2 · ВІДТІНОК РОЗДІЛЬНИЙ ПО ТЕМАХ -------------------
    Клас дефекту: одне число обслуговує два РІЗНІ фізичні явища — світіння на
    темній і кольорову тінь на світлій (A39 на осі відтінку). Другий клас,
    дорожчий: розщеплення ключа спалює device-вироки, бо старе ім'я падає в
    LOCK_STALE. Тут судиться і те, і те. */
 {
  console.log('— Ф4 · v17_4 · хід 2 · відтінок роздільний по темах —');

  /* 1 · Контроли існують парами, старого спільного імені більше немає. */
  T('шість повзунків відтінку в DOM',
    ['bgH1L','bgH2L','bgH3L','bgH1D','bgH2D','bgH3D'].every(k => q('#'+k)));
  T('спільний ключ bgH1/2/3 більше не існує в S',
    G("['bgH1','bgH2','bgH3'].filter(k=>k in S).length")===0);

  /* 2 · Головне: ВИХІД, не наявність. Різні відтінки по темах зобов'язані
     дати різний рядок фону — інакше повзунок є, а гілки немає. */
  G("S.bg='chrome'; S.bgH1L=42; S.bgH1D=195; render();");
  T('світла й темна беруть РІЗНІ відтінки',
    G("aurLayers(false)") !== G("aurLayers(true)"));
  T('світла гілка читає саме світлий важіль',
    G("(function(){S.bgH1L=42;var a=aurLayers(false);S.bgH1L=300;var b=aurLayers(false);S.bgH1L=42;return a!==b;})()"));
  T('темна гілка НЕ реагує на світлий важіль',
    G("(function(){var a=aurLayers(true);S.bgH1L=300;var b=aurLayers(true);S.bgH1L=42;return a===b;})()"));

  /* 3 · Оголошення дому: без запису в таблицю залежностей нові важелі вважались
     би вічно живими й осіли б у щілині покриття паспорта (З-9). */
  G("S.bg='sheet'; render();");
  const dead4 = G("Array.from(deadSet())");
  T('шість відтінків мертві при фоні=аркуш',
    ['bgH1L','bgH2L','bgH3L','bgH1D','bgH2D','bgH3D'].every(k => dead4.indexOf(k)>-1));
  G("S.bg='chrome'; themeMode='light'; render();");
  T('на світлій темна трійка оголошена мертвою',
    q('#deadTable').textContent.indexOf('фон · відтінки · тем.')>-1);

  /* 4 · МІГРАЦІЯ. Старе спільне число мусить лягти в ОБИДВІ гілки: воно
     фізично діяло на обох темах. Втрата половини вироку — не економія. */
  T('міграція відтінку веде у дві цілі',
    G("['bgH1','bgH2','bgH3'].every(k=>LOCK_MIGRATE[k].length===2)"));
  T('старе число успадковують обидві гілки', (()=>{
    G("LOCKS={}; LOCK_STALE=['bgH2']; LOCK_INHERIT=[]; o_v_cache={bgH2:34}; lockMigrate();");
    return G("LOCKS['bgH2L']")===34 && G("LOCKS['bgH2D']")===34 && G("LOCK_STALE.length")===0; })());

  /* 5 · Поключово, не пакетно: вже переставлена гілка не воскрешається, але
     сусідня однаково успадковує. Пакетна умова втратила б сусіда мовчки. */
  T('переставлена гілка не воскресає, сусідня успадковує', (()=>{
    G("LOCKS={bgH3L:99}; LOCK_STALE=['bgH3']; LOCK_INHERIT=[]; o_v_cache={bgH3:190}; lockMigrate();");
    return G("LOCKS['bgH3L']")===99 && G("LOCKS['bgH3D']")===190; })());

  /* 6 · Слід. Успадковане НЕ дорівнює висудженому, і паспорт мусить це казати:
     інакше нова гілка видасть спадок за власний вирок (ризик П-2). */
  T('паспорт друкує успадковані ключі окремим рядком', (()=>{
    G("LOCKS={}; LOCK_STALE=['bgH1']; LOCK_INHERIT=[]; o_v_cache={bgH1:180}; lockMigrate();");
    q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    const t=q('#out').value;
    return /УСПАДКОВАНО зі спільного ключа/.test(t) && /bgH1L ← bgH1/.test(t); })());

  G("LOCKS={}; LOCK_STALE=[]; LOCK_INHERIT=[]; S.bg='sheet'; themeMode='light'; S.bgH1L=180; S.bgH1D=180; render();");
 }

 /* ---- Ф5 · v17_5 · ХІД 3 · ЕЛІПС МАЄ ФОРМУ --------------------------------
    Клас дефекту: `ellipse at` без радіусів мовчки вироджується у farthest-corner,
    тобто в ~круглу пляму. Це не «трохи не та форма» — круглою плямою неможливо
    накрити капсулу, не заливши список під нею, а В-2 вимагає рівно протилежного.
    Другий клас: один повзунок, що міняє дві незалежні речі (розмір і м'якість
    краю), робить обидві несудимими. */
 {
  console.log('— Ф5 · v17_5 · хід 3 · еліпс має форму —');
  const aur5 = () => G("aurLayers(true)");

  /* 1 · Таблиця описує форму, а не лише позицію. */
  T('AUR тримає п\'ять чисел на еліпс',
    G("Object.values(AUR).every(m=>m.every(p=>p.length===5))"));

  /* 2 · Головне: АНІЗОТРОПІЯ. Радіуси мусять потрапити в CSS РІЗНИМИ — саме
     різниця й накриває смугу хрому, не чіпаючи середини полотна. */
  G("S.bg='chrome'; S.bgSpread=100; render();");
  T('еліпс друкується з двома радіусами',
    /radial-gradient\(ellipse \d+% \d+% at /.test(aur5()));
  T('радіуси РІЗНІ — пляма широка й низька, не куля', (()=>{
    const m = aur5().match(/ellipse (\d+)% (\d+)% at /);
    return m && +m[1] > +m[2] * 2; })());

  /* 3 · bgSpread рухає РОЗМІР і НЕ рухає стоп. Перевірка в обидва боки: сам
     факт «рядок змінився» тут нічого не доводить — треба, щоб змінилось саме
     те, що має, і НЕ змінилось те, що не має. */
  /* Null-safe навмисно: під --inject форма зникає, і смоук, що ПАДАЄ замість
     друкувати ✗, — непридатний гейт. Детектор мусить пережити той дефект,
     який ловить, інакше решта тверджень нижче не виконується взагалі. */
  const shape = () => { const m = aur5().match(/ellipse (\d+)% (\d+)% at/); return m ? [+m[1],+m[2]] : [0,0]; };
  const stop  = () => { const m = aur5().match(/transparent (\d+)%/); return m ? +m[1] : null; };
  const s100 = shape(), t100 = stop();
  G("S.bgSpread=140; render();");
  const s140 = shape(), t140 = stop();
  T('розмах збільшує ОБИДВА радіуси', s140[0] > s100[0] && s140[1] > s100[1]);
  T('розмах НЕ чіпає стоп — м\'якість краю лишається властивістю матеріалу',
    t140 === t100);
  G("S.bgSpread=100; render();");

  /* 4 · Режими різні за формою, не лише за позицією: chrome — смуга, all —
     близьке до кола. Спільні радіуси зрівняли б два різні явища. */
  const ratio = mode => { G("S.bg='"+mode+"'; render();");
    const m = aur5().match(/ellipse (\d+)% (\d+)% at/); return m ? m[1]/m[2] : 0; };
  T('chrome пласкіший за all', ratio('chrome') > ratio('all'));
  G("S.bg='chrome'; render();");

  /* 5 · Паспорт годується тією ж функцією — форма мусить доїхати в експорт. */
  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  T('паспорт друкує форму еліпса, а не лише позицію',
    /ellipse \d+% \d+% at /.test(q('#out').value));

  /* 6 · Підстава залоченого bgSpread змінилась — ключ той самий, зміст інший.
     LOCK_STALE такого не ловить у принципі, тому кричить паспорт. */
  T('паспорт попереджає про змінену підставу bgSpread', (()=>{
    G("LOCKS['bgSpread']=100;");
    q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    const t=q('#out').value; G("delete LOCKS['bgSpread'];");
    return /bgSpread ЗАЛОЧЕНО ДО v17_5/.test(t); })());

  G("S.bg='sheet'; themeMode='light'; render();");
 }

 /* ---- Ф6 · v17_6 · К7-а · ЗАЛИВКА ВЕРХНЬОЇ ЗОНИ ----------------------------
    Клас дефекту (З-20): непрозорий шар поверх того, що ми судимо. Заливка
    var(--canvas) на .el-ctxhead перекривала верхній еліпс AUR.chrome (at 50% 3%);
    на табі з пошуком це 23 % висоти екрана, де аврори фізично не було видно.
    Оператор упирався в стелю bgSpread, тоді як обмежував шар над плямою.
    Другий клас — «фолбек ховає мертвий важіль»: var(--tzbg,var(--canvas))
    повертає заливку, якщо змінну просто не поставити, і пікер виглядає живим
    при мертвій механіці. Тому перевіряється ЕФЕКТ, а не наявність кнопки. */
 {
  console.log('— Ф6 · v17_6 · К7-а · заливка верхньої зони —');
  const tz = () => { const el=q('.el-ctxhead');
    return el ? w.getComputedStyle(el).getPropertyValue('background-color') : null; };
  const tzvar = () => G("sbox.style.getPropertyValue('--tzbg')");

  /* 1 · Пікер підключений: клік мусить міняти СТАН, не лише aria-pressed. */
  G("tab='ph'; S.srch='always'; render();");
  T('пікер заливки існує в розмітці', !!q('#pkTzFill'));
  T('пікер заливки підключений до pick()', (()=>{
    G("S.tzFill='canvas'; syncPicks(); render();");
    const b=q('#pkTzFill button[data-v="none"]'); if(!b) return false;
    b.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    return G("S.tzFill")==='none'; })());

  /* 2 · Головне: змінна справді ставиться. Без цього фолбек мовчки повертає
     канву, і весь крок стає косметикою в розмітці. */
  T('«прозоро» ставить --tzbg у transparent', /transparent/.test(tzvar()||''));
  T('«канва» повертає --tzbg на var(--canvas)', (()=>{
    G("S.tzFill='canvas'; applyVars(); render();");
    return /canvas/.test(tzvar()||''); })());

  /* 3 · Прозорість НЕ сміє знести перекриття: sticky і z-index — окрема
     механіка, вона лишається обома станами пікера. */
  const stick = () => { const el=q('.el-ctxhead');
    return el ? w.getComputedStyle(el).position : null; };
  G("S.tzFill='none'; applyVars(); render();");
  T('sticky живий при прозорій зоні', stick()==='sticky');
  G("S.tzFill='canvas'; applyVars(); render();");
  T('sticky живий при залитій зоні', stick()==='sticky');

  /* 4 · Паспорт друкує стан заливки словом, а не лише ключем: вирок читає
     людина, і «tzFill=none» їй нічого не каже про те, що видно на екрані. */
  G("S.tzFill='none'; applyVars(); render();");
  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  const pass = q('#out').value;
  /* v17_7: К7-б перейменував рядок «заливка зони» → «матеріал зони», бо гілок
     стало чотири і дві з них нічого не заливають. Твердження йде за об'єктом,
     а не за словом: перевіряється, що паспорт ДРУКУЄ стан зони, і що він
     називає наслідок для аврори. */
  T('паспорт друкує матеріал зони', /матеріал зони=/.test(pass));
  T('паспорт називає наслідок для аврори', /аврора видна|аврора перекрита/.test(pass));

  /* 5 · Важіль живий лише там, де верхня зона є. На табі без неї він мертвий
     за таблицею залежностей — це не пропуск, а оголошена умова. */
  T('tzFill оголошений у таблиці залежностей',
    G("conds().some(c=>c[3].includes('tzFill'))"));

  G("S.tzFill='canvas'; S.bg='sheet'; themeMode='light'; applyVars(); render();");
 }


 /* ---- Ф7 · v17_7 · К7-б · МАТЕРІАЛ ВЕРХНЬОЇ ЗОНИ + Н-11 ---------------------
    К7-а лишив зону з двома станами: залито або нічого. Девайс відповів (З-24):
    «нічого» ріже назви аптек текстом фільтрів. К7-б додає ДВА МАТЕРІАЛИ —
    оптичний (скло) і речовий (тіло під контролами).
    Перевіряється ЕФЕКТ, не наявність кнопки: атрибут [data-tz] мусить доїжджати
    до розмітки, backdrop-filter — до обчисленого стилю, alpha — розходитись по
    темах. Твердження «ключ є в S» проспало б усі три (З-10).
    ⚠ jsdom не рендерить скло. Він може підтвердити, що ПРАВИЛО дійшло і що
    змінні розійшлись; чи це виглядає склом — судить тільки девайс, і тільки
    на 1:1 (радіус блюру масштабується разом зі стендом). */
 {
  console.log('— Ф7 · v17_7 · К7-б · матеріал верхньої зони —');
  const cs = () => { const el=q('.el-ctxhead');
    return el ? w.getComputedStyle(el) : null; };
  const dtz = () => { const el=q('.el-ctxhead'); return el ? el.getAttribute('data-tz') : null; };

  G("tab='ph'; S.srch='always'; S.tzFill='canvas'; applyVars(); render();");

  /* 1 · Чотири гілки існують і всі підключені до pick(). */
  T('пікер зони має 4 гілки',
    q('#pkTzFill') && q('#pkTzFill').querySelectorAll('button:not(.bx-lock)').length===4);
  ['blur','body'].forEach(v => {
    T(`гілка «${v}» підключена до pick()`, (()=>{
      G("S.tzFill='canvas'; syncPicks(); render();");
      const b=q(`#pkTzFill button[data-v="${v}"]`); if(!b) return false;
      b.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
      return G("S.tzFill")===v; })());
  });

  /* 2 · Атрибут доїжджає до розмітки. Без нього всі гілки — одна картинка. */
  ['canvas','none','blur','body'].forEach(v => {
    G(`S.tzFill='${v}'; applyVars(); render();`);
    T(`[data-tz] у розмітці = ${v}`, dtz()===v);
  });

  /* 3 · Скло: правило гілки справді несе backdrop-filter, і воно зникає на
     інших гілках. Одностороння перевірка пропустила б «скло завжди». */
  const bf = () => { const c=cs(); if(!c) return '';
    return (c.backdropFilter || c.getPropertyValue('backdrop-filter') ||
            c.webkitBackdropFilter || c.getPropertyValue('-webkit-backdrop-filter') || ''); };
  /* ⚠ Регістр без якоря початку властивості ловив би -webkit-близнюка й
     проходив би при знятому НЕПРЕФІКСНОМУ правилі — тобто «скло є в Safari,
     немає ніде більше». Пара перевіряється обома половинами окремо. */
  const rule = () => (G("[...document.querySelectorAll('style')].map(s=>s.textContent).join('')")
      .replace(/\s+/g,' ').match(/\.el-ctxhead\[data-tz="blur"\][^}]*}/)||[''])[0];
  T('правило гілки blur несе backdrop-filter',
    /(?:^|[;{ ])backdrop-filter\s*:\s*blur/.test(rule()));
  T('правило гілки blur має -webkit-близнюка',
    /-webkit-backdrop-filter\s*:\s*blur/.test(rule()));
  T('правило гілки blur несе saturate',
    /saturate\(var\(--tzSat/.test(G("[...document.querySelectorAll('style')].map(s=>s.textContent).join('')")));

  /* 4 · --tzbg мусить бути ПРОЗОРИМ під склом: непрозора канва під backdrop-filter
     дала б блюр самої канви замість аврори — гілка жива, оптика мертва. */
  const tzvar = () => G("sbox.style.getPropertyValue('--tzbg')");
  G("S.tzFill='blur'; applyVars(); render();");
  T('під склом --tzbg прозорий', /transparent/.test(tzvar()||''));
  G("S.tzFill='body'; applyVars(); render();");
  T('під тілом --tzbg прозорий', /transparent/.test(tzvar()||''));

  /* 5 · Alpha РОЗХОДИТЬСЯ по темах (A39 · В-7), блюр і насиченість — ні. */
  G("S.tzFill='blur'; S.tzAL=90; S.tzAD=20; themeMode='light'; applyVars(); render();");
  const aL = G("sbox.style.getPropertyValue('--tzA')");
  G("themeMode='dark'; applyVars(); render();");
  const aD = G("sbox.style.getPropertyValue('--tzA')");
  T('alpha скла зони розходиться по темах', aL !== aD && /90/.test(aL) && /20/.test(aD));
  T('блюр зони спільний для тем', /14|30|0/.test(G("sbox.style.getPropertyValue('--tzBlur')")||''));

  /* 6 · Важелі оголошені в таблиці залежностей — інакше вічно живі й у щілині
     покриття cssGap (З-9), а паспорт друкує неповний вирок як повний. */
  ['tzBlur','tzSat','tzAL','tzAD'].forEach(k =>
    T(`${k} оголошений у таблиці залежностей`, G(`conds().some(c=>c[3].includes('${k}'))`)));
  G("S.tzFill='canvas'; applyVars(); render();");
  T('важелі скла мертві поза гілкою blur', G("deadSet().has('tzBlur') && deadSet().has('tzSat')"));

  /* 7 · Паспорт друкує гілку СЛОВОМ і наслідком для аврори — вирок читає людина. */
  G("S.tzFill='blur'; themeMode='dark'; applyVars(); render();");
  q('#copyBtn').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  const pass = q('#out').value;
  T('паспорт друкує матеріал зони', /матеріал зони=/.test(pass));
  T('паспорт називає гілку скла словом', /СКЛО/.test(pass));
  T('паспорт несе числа скла', /backdrop-filter:blur\(/.test(pass));
  T('паспорт покриває нові важелі', (()=>{
    const cov = G("[...cssCovered()]");
    return ['tzBlur','tzSat','tzAD','tzAL'].every(k => cov.includes(k)); })());

  /* 8 · Н-11 · поле пошуку дістало НУЛЬ матеріалу третьою гілкою. */
  T('pkMat має гілку plain', !!q('#pkMat button[data-v="plain"]'));
  T('гілка plain доїжджає до поля', (()=>{
    G("S.mat='plain'; render();");
    const se=q('.el-search'); return se && se.getAttribute('data-mat')==='plain'; })());
  T('plain позначається як перебите тезою', (()=>{
    G("S.mat='plain'; paintDead();");
    const b=q('#pkMat button[data-v="plain"]'); return b && b.classList.contains('bx-ovr'); })());

  G("S.tzFill='canvas'; S.mat='well'; S.bg='sheet'; themeMode='light'; applyVars(); render();");
 }

 /* ---- Ф8 · v17_8 · К9\' · ЩІЛИНА ЗАМІСТЬ ЛІНІЇ (І-1) + К17 -------------------
    Гілка `slit` — не третя картинка, а третій МЕХАНІЗМ межі: у «картці» межу
    несе рамка, у «рядку» — волосинка, тут — порожнеча між рядками, крізь яку
    видно аврору.
    Що саме перевіряється і чому не інакше:
    · greep по <style>, а не computed rowGap — jsdom не резолвить фолбек
      var(--slitW,1px) і віддає `normal`. Твердження на computed було б хибним ✗
      на справному коді, а хибний ✗ шкідливіший за відсутній детектор (G8).
    · кант `.el-sw` перевіряється ОКРЕМИМ твердженням і в ОБИДВА боки: у «рядку»
      він мусить лишитись (там він і несе лінію), у «щілині» — зникнути. Це
      єдина справжня пастка ходу (З-36): два носії дають число, яке бреше вдвічі.
    · паспорт судиться двосторонньо. «Друкує щілину» пропустило б «друкує щілину
      завжди», і в valuesLOCK поїхало б число з гілки, яка не судилась.
    · К17 (оснастка) сидить тут же, бо в нього немає власної секції й не буде:
      одне твердження, клас Г-9 — поле виносу мусить оголосити виняток явно. */
 {
  console.log('— Ф8 · v17_8 · К9\' · щілина + К17 —');
  const css = () => G("[...document.querySelectorAll('style')].map(s=>s.textContent).join('')").replace(/\s+/g,' ');
  const listEl = () => q('.el-list');
  const swEl = () => q('.el-list .el-sw');

  G("tab='ph'; S.row='row'; applyVars(); render();");

  /* 1 · Три гілки існують і третя справді підключена до pick(). */
  T('пікер рядка має 3 гілки',
    q('#pkRow') && q('#pkRow').querySelectorAll('button:not(.bx-lock)').length===3);
  T('гілка «slit» підключена до pick()', (()=>{
    G("S.row='row'; syncPicks(); render();");
    const b=q('#pkRow button[data-v="slit"]'); if(!b) return false;
    b.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    return G("S.row")==='slit'; })());

  /* 2 · Атрибут доїжджає до розмітки — в обидва боки. */
  G("S.row='slit'; render();");
  T('[data-row] у розмітці = slit', listEl() && listEl().getAttribute('data-row')==='slit');
  G("S.row='row'; render();");
  T('[data-row] повертається в row', listEl() && listEl().getAttribute('data-row')==='row');

  /* 3 · Правило гілки несе ЗМІННУ, а не константу. Константа = мертвий важіль
     при живому пікері (той самий клас, що фолбек --tzbg у К7-а). */
  T('правило гілки slit несе gap із важеля',
    /\.el-list\[data-row="slit"\]\{gap:var\(--slitW/.test(css()));
  T('правило гілки slit знімає кант .el-sw',
    /\.el-list\[data-row="slit"\] \.el-sw\{[^}]*border:none/.test(css()));

  /* 4 · З-36 · носій ОДИН. Двостороння перевірка: у «рядку» кант мусить бути,
     інакше ми вилікували щілину, зламавши лінію. */
  G("S.row='row'; render();");
  T('у гілці row кант .el-sw лишається',
    (()=>{ const e=swEl(); return !!e && w.getComputedStyle(e).borderTopStyle==='solid'; })());
  G("S.row='slit'; render();");
  T('у гілці slit канта .el-sw немає',
    (()=>{ const e=swEl(); return !!e && w.getComputedStyle(e).borderTopStyle==='none'; })());

  /* 5 · Змінна ставиться БЕЗУМОВНО. Умовне setProperty дало б важіль, що діє
     через раз: фолбек var(--slitW,1px) спрацьовує лише на ВІДСУТНІЙ змінній. */
  G("S.row='row'; S.slitW=1; applyVars();");
  T('--slitW ставиться навіть поза гілкою', /px/.test(G("sbox.style.getPropertyValue('--slitW')")||''));
  G("S.row='slit'; S.slitW=3.5; applyVars(); render();");
  T('--slitW доїжджає після зсуву', /3\.5px/.test(G("sbox.style.getPropertyValue('--slitW')")||''));

  /* 6 · Таблиця залежностей — обидва боки. Тільки «живий у slit» пропустило б
     «живий завжди», а це рівно З-30: оператор крутить те, чого не видно. */
  T('slitW оголошений у таблиці залежностей', G("conds().some(c=>c[3].includes('slitW'))"));
  T('slitW живий у гілці slit',
    G("S.row='slit'; conds().filter(c=>c[3].includes('slitW')).map(c=>c[2])[0]")===true);
  T('slitW мертвий у гілці row',
    G("S.row='row'; conds().filter(c=>c[3].includes('slitW')).map(c=>c[2])[0]")===false);

  /* 7 · Паспорт. Число без згадки про знятий кант — це число, яке на іншій
     верстці дасть інший результат, тому обидва рядки перевіряються разом. */
  G("S.row='slit'; S.slitW=3.5; applyVars();");
  const pass8 = G("cssPassport(true)");
  T('паспорт друкує щілину числом', /data-row="slit"\]\{gap:3\.5px\}/.test(pass8));
  T('паспорт друкує знятий кант поруч із числом', /\.el-sw\{border:none\}/.test(pass8));
  G("S.row='row'; applyVars();");
  T('паспорт у гілці row про щілину МОВЧИТЬ', !/data-row="slit"/.test(G("cssPassport(true)")));
  T('паспорт покриває важіль slitW', G("[...cssCovered()]").includes('slitW'));

  /* 8 · К17 · Г-9 · оснастка. body{user-select:none} успадковується в textarea;
     WebKit на iOS робить виняток, Blink і Gecko — ні. Поле виносу мусить
     оголосити виняток ЯВНО, на власному селекторі. */
  T('поле виносу оголосило виняток виділення',
    /\.bx-out\{[^}]*user-select:text/.test(css()));
  T('виділення в полі виносу видиме', /\.bx-out::selection\{/.test(css()));


  /* ⚠ Знахідка К20 на першому ж прогоні, виправлена тут-таки: смоук писав
     S.tab='ph' у трьох місцях. Ключа tab у S немає — таб живе окремою
     глобальною змінною (р.1265 бази). Тобто присвоєння створювало ФАНТОМНИЙ
     ключ у S і не керувало нічим; реальний стан ставив сусідній tab='ph'.
     Дефект жив у самому детекторі й не був видимий, поки не з'явився паритет.

     9 · К20 · ПАРИТЕТ S <-> РОЗМІТКА (спека K21 §6, твердження 1-4).
     Навіщо. K21 переносить 172 рядки панелі в іншу структуру. Ручний перенос
     мовчки губить або дублює: дубльований id дає повзунок, що рухається й не
     керує; втрачений — важіль живий за conds() і невидимий на екрані. Обидва
     дефекти тихі, тому детектор іде ПЕРЕД переїздом, а не після (§8.12-г).
     Твердження 5-6 (розкладка по табах) фізично неможливі до існування табів. */
  {
   const lv   = qa('.bx-lv[data-k]');
   const keys = Object.keys(G('S'));
   const dk   = lv.map(e => e.dataset.k);
   const pk   = qa('[data-dk]').map(e => e.dataset.dk);

   /* Виняток ОГОЛОШЕНИЙ літералом і ДРУКУЄТЬСЯ. Список імен усередині
      детектора тухне мовчки (§13-ж) — надрукований не може: він на очах
      у кожного прогону. thesis керується власною розміткою #pkThesis і не
      несе ні data-k, ні data-dk, тому не входить у ЛОК-покриття взагалі.
      Дім лікування — K21, де розмітка й так переписується. */
   /* v17_13 · К21 · З-49 закрито: #pkThesis дістав data-dk="thesis" у тому ж
      ході, де розмітка панелі й так переписувалась (В-18). Виняток спорожнів —
      але ЛІТЕРАЛ ЛИШАЄТЬСЯ й далі друкується. Прибрати порожній масив означало б
      прибрати й рядок паритету, який показує, що винятків НЕМА; наступний
      безознаковий контроль тоді знову з'явиться мовчки. */
   const EXEMPT = [];
   const orphan = keys.filter(k => !dk.includes(k) && !pk.includes(k));
   console.log(`  · паритет: S=${keys.length} = важелі ${dk.length}`
     + ` + пікери ${pk.length} + без ознаки [${orphan.join(', ')}]`);

   /* 1. Розклад БЕЗ ЗАЛИШКУ — звіркою МНОЖИН, а не сумою.
         Сума каже «не сходиться» і мовчить про винуватця; множина його називає.
         Детектор, що не називає імені, змушує шукати руками — тобто повертає
         роботу оператору, від якого його й писали (§8.7). */
   T('ключі S без ознаки === оголошені винятки',
     orphan.length === EXEMPT.length && orphan.every(k => EXEMPT.includes(k)));
   T('S розкладається без залишку: важелі + пікери + винятки',
     keys.length === dk.length + pk.length + EXEMPT.length);

   /* 2. Зворотний бік (wsd 1.15): не лише «S покритий розміткою», а й
         «розмітка не вигадала ключа, якого в S немає». */
   T('кожен data-k має ключ у S', dk.every(k => keys.includes(k)));

   /* 3. id === data-k. Розходження дає найтихіший сорт: markLock/paintDead
         працюють по data-k, а slider() — по id; вони просто розійдуться. */
   T('кожен .bx-lv несе <input id>, і id === data-k',
     lv.every(e => { const i = e.querySelector('input[id]'); return i && i.id === e.dataset.k; }));

   /* 4. Дублі. Другий однаковий id — це повзунок, який рухається й не керує:
         getElementById поверне лише перший. */
   T('жоден id важеля не зустрічається двічі', new Set(dk).size === dk.length);

   /* Контроль самого детектора: якщо панель раптом порожня, усі чотири
      твердження вище пройдуть на порожніх множинах (пастка хибного ✓,
      wsd 1.15). Тому окремо — що предмет суду взагалі існує. */
   T('панель непорожня — детектор має що перевіряти', lv.length > 100);

   /* ===== К13-3 · механіка «ставки» =====
      ЧИСЛА тут НЕ судяться свідомо: дефолти фону — device-матеріал, вони
      мусять рухатись кожного раунду, і гейт, що їх стереже, ламався б на
      КОЖНІЙ правильній правці. Судиться рівно те, що числам не дасть зникнути. */
   /* ===== К10' · механіка краю аркуша ===== */
   /* Псевдоелементи лежать ПОВЕРХ рядків. Без pointer-events:none вони з'їли б
      тап і свайп A22 — і дефект виглядав би як «свайп зламався», а не як
      «край аркуша ловить палець». */
   /* ===== УНІВЕРСАЛЬНИЙ · важіль ПІДКЛЮЧЕНИЙ, а не лише оголошений =====
      Паритет К20 звіряє data-k з ключем у S — і дає ✓ важелю, для якого
      забули викликати slider(). Саме так К10' поїхав на девайс із п'ятьма
      мертвими повзунками. Ознака підключення видима ззовні: slider() пише
      у <output> при першому ж малюнку, тому порожній вивід = немає обробника. */
   T('кожен важіль підключений — <output> заповнений', (() => {
     const nil = lv.filter(e => !(e.querySelector('output')||{}).textContent)
                   .map(e => e.dataset.k);
     if (nil.length) console.log('     без обробника:', nil.join(' · '));
     return nil.length === 0;
   })());

   T("край аркуша не перехоплює тап",
     /\.el-list::before,\.el-list::after\{[^}]*pointer-events:none/.test(html));
   /* Мапа мусить покривати РІВНО кнопки пікера: зайвий ключ — мертвий код,
      відсутній — кнопка, що мовчки не робить нічого (§8.7-в). */
   T('EDGE-мапа покриває рівно кнопки pkEdge', (() => {
     const btns = qa('#pkEdge button[data-v]').map(b => b.dataset.v);
     const map  = Object.keys(G('EDGE'));
     return btns.length === 4 && btns.every(v => map.includes(v)) && map.length === btns.length;
   })());
   /* border-image не дружить із border-radius, тому на гілці «картка» кант
      вимкнений СТИЛЕМ — отже мусить бути мертвим і за conds, інакше три
      важелі керують нічим (Д-З: носій судиться той, що названий). */
   T("кант мертвий на гілці «картка»", (() => {
     const was = G('S.row'), w2 = G("S.pkEdge");
     G("S.row='card'; S.pkEdge='both';");
     const dead = G("[...deadSet()]");
     G(`S.row='${was}'; S.pkEdge='${w2}'; render();`);
     return ['edgeAL','edgeAD','edgeStop'].every(k => dead.includes(k));
   })());

   T('S0 — знімок, а не посилання на S',
     /const S0 = Object\.assign\(\{\}, S\);/.test(html));
   T('кнопка «ставка» існує і підключена',
     !!q('#betBtn') && /getElementById\('betBtn'\)\.addEventListener/.test(html));
   /* bg='sheet' означає «аврори нема взагалі» — саме той дефолт, через який
      К9'/К13 прорізали в полотні вікна, а показувати в них було нічого (З-41). */
   /* ⚠ Перша редакція читала G('S.bg') і падала: попередні блоки лишають S у
      робочому стані, тобто вона судила СТАН НАПРИКІНЦІ ПРОГОНУ, а не дефолт.
      Третій випадок Д-З(в) за дві сесії. Читається S0 — він незмінний за
      побудовою, тому заразом підтверджує, що знімок справді знімок. */
   T("дефолт bg не 'sheet' — вікна полотна мають що показувати",
     G('S0.bg') !== 'sheet');
   T('S0 не мутував разом із S протягом прогону',
     G('S0.bg') !== G('S.bg') || G("JSON.stringify(S0)!==JSON.stringify(S)"));

   /* ===== К21 · твердження 5-8: розкладка по табах =====
      До К21 їх не можна було написати — табів не існувало (спека §6). Саме
      вони роблять переїзд механічним: 1-4 стережуть ВАЖІЛЬ, а пікер і нотатка
      паритету не порушують взагалі (ADDENDUM §4-б п.0) — тобто без 7-8 частина
      переїзду лишилась би без страховки. */
   const tabs = qa('.bx-tab[data-tab]');
   const inTab = e => e.closest('.bx-tab');

   /* 5. Рівно в ОДНОМУ табі. closest() повертає найближчий — вкладеність
         .bx-tab у .bx-tab дала б хибне ✓, тому вкладеність перевіряється окремо. */
   T('усі 7 табів на місці і жоден не вкладений в інший',
     tabs.length === 7 && tabs.every(t => !inTab(t.parentElement)));
   /* ⚠ Перша редакція цього рядка була lv.every(e => !!inTab(e)) — «кожен
      важіль у ЯКОМУСЬ табі». Прогін --inject показав, що дубль у чужому табі
      вона пропускає: обидва екземпляри лежать у табах, отже ✓. Твердження було
      написане валідно й не судило рівно того слова, заради якого існує —
      «РІВНО в одному» (клас З-45). Судиться множина табів на ІМ'Я. */
   const byTab = {};
   tabs.forEach(t => t.querySelectorAll('.bx-lv[data-k]').forEach(e => {
     (byTab[e.dataset.k] = byTab[e.dataset.k] || new Set()).add(t.dataset.tab);
   }));
   T('кожен важіль лежить рівно в одному табі',
     lv.every(e => byTab[e.dataset.k] && byTab[e.dataset.k].size === 1));

   /* 6. Сума. Твердження 5 каже «кожен десь є», 6 — «і більше ніде нікого»:
         разом вони закривають і втрату, і зайвину (wsd 1.15, обидва боки). */
   const sum = tabs.reduce((a,t) => a + t.querySelectorAll('.bx-lv[data-k]').length, 0);
   T('сума важелів по табах === кількість .bx-lv у панелі', sum === lv.length);

   /* 7. Нотатки. ЗАМІРЯНО на v17_9 = 47. ADDENDUM §3 оголошував 45; число взято
         з заміру, не з оголошення (wsd 1.10) — інакше гейт кричав би ✗ на
         ПРАВИЛЬНОМУ переїзді, тобто дефект жив би в самому детекторі (З-45). */
   T('нотаток у панелі рівно 48 — жодна не загубилась',
     qa('#panel .bx-note').length === 48);

   /* 8. Пікери. thesis свідомо ПОЗА рейкою: він судить обидві гілки одночасно,
         отже не належить жодному табу. Виняток названий тут, а не мовчазний. */
   const pkEls = qa('#panel [data-dk]');
   const pkOut = pkEls.filter(e => !inTab(e)).map(e => e.dataset.dk);
   T('пікерів 33 (32 у табах + thesis у шапці)', pkEls.length === 33);
   T('поза табами лежить рівно thesis',
     pkOut.length === 1 && pkOut[0] === 'thesis');
  }

  G("S.row='row'; S.slitW=1; applyVars(); render();");
 }

 console.log(`\nГЕЙТ: ✓${ok} · ✗${bad}`);
 if (INJECT) console.log(bad>0
   ? '✅ детектор ЗЛОВИВ підкинутий дефект — гейт придатний (wsd 12.12)'
   : '❌ детектор ПРОСПАВ підкинутий дефект — гейт непридатний');
 process.exit(INJECT ? (bad>0?0:1) : (bad?1:0));
},400);
