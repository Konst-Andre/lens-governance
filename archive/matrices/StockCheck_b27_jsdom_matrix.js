/* StockCheck · b27 runtime-матриця (доповнення до StockCheck_maint_jsdom_matrix.js)
   Секції: S sweep-гарди · T тост-копія · Q блідість .mi.quiet · R регресія Node 2.2
   Запуск: node StockCheck_b27_jsdom_matrix.js
   ⚠ Клітина-сторож S0: якщо підміна matchMedia не спрацювала — валиться явно. */
const fs=require('fs');const {JSDOM}=require('jsdom');
const PATH=process.env.SC_BUILD||process.argv[2]||'/mnt/user-data/outputs/StockCheck_port_b29_1.html';
const HTML=fs.readFileSync(PATH,'utf8');

const UA_SAFARI='Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1';

function boot(opts={}){
  return new JSDOM(HTML,{runScripts:'dangerously',url:'https://konst-andre.github.io/stockcheck/',
    pretendToBeVisual:true,
    beforeParse(w){
      Object.defineProperty(w.navigator,'userAgent',{value:UA_SAFARI,configurable:true});
      Object.defineProperty(w.navigator,'platform',{value:'iPhone',configurable:true});
      w.matchMedia=q=>({
        matches: q.includes('prefers-reduced-motion') ? !!opts.reduce
               : q.includes('display-mode: standalone') ? !!opts.standalone
               : false,
        media:q,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
      w.fetch=()=>Promise.reject(new Error('offline'));
      w.scrollTo=()=>{};
      /* clipboard: керований успіх/відмова */
      Object.defineProperty(w.navigator,'clipboard',{
        value: opts.noClipboard ? undefined :
          { writeText:()=> opts.clipFail ? Promise.reject(new Error('denied')) : Promise.resolve() },
        configurable:true});
      if(opts.execFail)w._execFail=true;
    }});
}
const wait=ms=>new Promise(r=>setTimeout(r,ms));
let fails=0;
const chk=(n,c)=>{if(!c)fails++;console.log((c?'  \u2713 ':'  \u2717 FAIL ')+n);};

function btn(d){return d.window.document.querySelector('#s-fill .btn-copy');}
function css(d){return [...d.window.document.querySelectorAll('style')].map(s=>s.textContent).join('\n');}
/* PH/curPx оголошені через const/let → НЕ потрапляють на window. Беремо px із DOM. */
function firstPx(d){const c=d.window.document.querySelector('#homeList .card');
  if(!c)throw new Error('СТОРОЖ: #homeList порожній — Home не відрендерився');
  return c.dataset.px;}

(async()=>{

/* ── S · SWEEP: гарди й життєвий цикл ─────────────────────────────── */
console.log('\n── S · handoff-sweep ──');
{
  const d=boot();
  await wait(60);
  const w=d.window;

  // S0 СТОРОЖ: підміна matchMedia працює. Без цього S3 «зелений» дарма.
  chk('S0 сторож: reduceOn() === false при matches:false', w.reduceOn()===false);

  const b=btn(d);
  chk('S1 розмітка: .cta-lbl усередині кнопки', !!b.querySelector('.cta-lbl'));
  chk('S1b розмітка: .cta-sweep усередині кнопки', !!b.querySelector('.cta-sweep'));
  chk('S1c напис не голий текстовий вузол (має z-контекст)',
      b.querySelector('.cta-lbl').textContent.trim()==='Копіювати 83 значення');

  // S2 запуск на успіх clipboard
  w.openFill(firstPx(d));
  w.copyValues();
  await wait(80);
  chk('S2 клас sweeping навішено після успішного копіювання', b.classList.contains('sweeping'));
  chk('S2b dataset-замок виставлено', b.dataset.sweeping==='1');

  // S4 анти-повтор: другий виклик під час програвання нічого не змінює
  const before=b.className;
  w.fireSweep();
  chk('S4 повторний fireSweep під час програвання — no-op', b.className===before && b.dataset.sweeping==='1');
}

/* S3 · reduced-motion: клас НЕ навішується взагалі */
{
  const d=boot({reduce:true});
  await wait(60);
  const w=d.window;
  chk('S3 сторож: reduceOn() === true при matches:true', w.reduceOn()===true);
  w.openFill(firstPx(d));
  w.copyValues();
  await wait(80);
  chk('S3b при reduced-motion клас sweeping НЕ навішується', !btn(d).classList.contains('sweeping'));
  chk('S3c dataset-замок лишається порожнім', btn(d).dataset.sweeping!=='1');
}

/* S5 · відмова clipboard → падає у fallback; нагорода лише за фактом успіху */
{
  const d=boot({clipFail:true});
  await wait(60);
  const w=d.window;
  w.openFill(firstPx(d));
  // execCommand у jsdom не реалізовано → fallback кине → нагороди бути не має
  w.document.execCommand=()=>{throw new Error('unsupported');};
  w.copyValues();
  await wait(80);
  chk('S5 clipboard відмовив + fallback кинув → sweep НЕ грає', !btn(d).classList.contains('sweeping'));
  chk('S5b тост повідомляє про невдачу',
      w.document.getElementById('toast').textContent.indexOf('Не вдалось')>=0);
}

/* S6 · шлях без clipboard API (webview) → fallback успішний → нагорода Є */
{
  const d=boot({noClipboard:true});
  await wait(60);
  const w=d.window;
  w.openFill(firstPx(d));
  w.document.execCommand=()=>true;
  w.copyValues();
  await wait(80);
  chk('S6 fallback успішний → sweep грає', btn(d).classList.contains('sweeping'));
}

/* S7 · тривалість читається з токена, не з дубля-числа */
{
  const d=boot(); await wait(40);
  chk('S7 --swDur визначено у :root', /--swDur:\s*1400ms/.test(css(d)));
  chk('S7b JS читає --swDur, а не літерал', /getPropertyValue\('--swDur'\)/.test(HTML));
}

/* ── T · ТОСТ ─────────────────────────────────────────────────────── */
console.log('\n── T · тост ──');
{
  const d=boot(); await wait(60);
  const w=d.window;
  w.openFill(firstPx(d));
  w.copyValues();
  await wait(80);
  const t=w.document.getElementById('toast').textContent;
  chk('T1 копія містить рівно один \\n (детерміновані 2 рядки)', (t.match(/\n/g)||[]).length===1);
  chk('T2 1-й рядок = підтвердження', t.split('\n')[0].indexOf('Скопійовано 83 значення')>=0);
  chk('T3 2-й рядок = дія + M-рядок + Proxima',
      /^Вставити у M\d+ · Proxima /.test(t.split('\n')[1]));
  chk('T4 CSS: white-space:pre-line у .toast', /\.toast\{[^}]*white-space:pre-line/s.test(css(d)));
  chk('T5 CSS: підйом bottom 78px (над CTA)', /\.toast\{[^}]*bottom:calc\(78px \+ env\(safe-area-inset-bottom\)\)/s.test(css(d)));
  chk('T6 старої геометрії 22px не лишилось', !/bottom:calc\(22px \+ env\(safe-area-inset-bottom\)\)/.test(css(d)));
}

/* ── Q · БЛІДІСТЬ «Обслуговування» ────────────────────────────────── */
console.log('\n── Q · .mi.quiet ──');
{
  const d=boot(); await wait(40);
  const c=css(d);
  chk('Q1 .mi.quiet b більше НЕ фарбує заголовок', !/\.mi\.quiet b\{[^}]*color:/.test(c));
  chk('Q2 .mi.quiet b лишає лише вагу', /\.mi\.quiet b\{font-weight:700\}/.test(c));
  chk('Q3 .mi.quiet зберігає cursor:default (неінтерактивність)', /\.mi\.quiet\{cursor:default\}/.test(c));
  chk('Q4 базове .mi-tx b на --text не зачеплено', /\.mi-tx b\{[^}]*color:var\(--text\)\}/.test(c));
  chk('Q5 семантичний прецедент .mi.danger b цілий', /\.mi\.danger b\{color:var\(--crit\)\}/.test(c));
}

/* ── R · РЕГРЕСІЯ Node 2.2 + білд ─────────────────────────────────── */
console.log('\n── R · регресія ──');
{
  const d=boot(); await wait(900);
  const w=d.window;
  /* APP_BUILD — const, не на window. Читаємо крізь DOM, куди його пише білд. */
  const abv=w.document.getElementById('ab-ver').textContent.trim();
  const abb=w.document.getElementById('ab-build').textContent.trim();
  /* wsd 1.10 — звірка з оголошенням: About мусить показувати APP_BUILD ЦЬОГО файлу,
     а не літерал попереднього білда (до b29.1 тут було зашито b27/v2.16.0). */
  const DB=/build:'([^']+)'/.exec(HTML)[1], DV=/ver:'([^']+)'/.exec(HTML)[1];
  chk('R1 About-щит показує APP_BUILD цього білда ('+DB+' · '+DV+')', abb===DB && abv===DV);
  chk('R2 блок «Обслуговування» рендериться', !!w.document.getElementById('mtCard').textContent.trim());
  chk('R3 Node 2.2 коректно деградує офлайн (fetch rejected)',
      w.document.getElementById('mtCard').textContent.indexOf('Не вдалося перевірити')>=0);
  chk('R4 CTA-ряд цілий: .btn-copy + .btn-form',
      !!w.document.querySelector('#s-fill .btn-copy') && !!w.document.querySelector('#s-fill .btn-form'));
  chk('R5 .btn-copy має overflow-контейнер для шару',
      /\.btn-copy\{[^}]*position:relative;overflow:hidden/s.test(css(d)));
  /* ⚠ Детектор мусить рахувати ОГОЛОШЕННЯ, не будь-яке входження селектора:
     `.btn-copy.sweeping .cta-sweep{` — легітимне ДРУГЕ входження підрядка,
     але не друге оголошення. Якірем береться початок рядка. (Перший прогін
     дав хибний ✗ саме через це — дефект клітини, не коду.) */
  const C=css(d);
  chk('R6 колізій імен нема: по одному ОГОЛОШЕННЮ .cta-lbl/.cta-sweep/swGo',
      (C.match(/(^|\n)\.cta-lbl\{/g)||[]).length===1 &&
      (C.match(/(^|\n)\.cta-sweep\{/g)||[]).length===1 &&
      (C.match(/@keyframes swGo/g)||[]).length===1);
  chk('R7 голих імен .lbl/.sweep у продукті нема (пастка b26_1 §4)',
      !/(^|\n)\.lbl\{/.test(C) && !/(^|\n)\.sweep\{/.test(C));
}

console.log('\n'+(fails? '\u2717 ПРОВАЛІВ: '+fails : '\u2713 ВСІ ЗЕЛЕНІ')+'\n');
process.exit(fails?1:0);
})();
