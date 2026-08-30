/* живе доки: стенд NetPick v3 не витіснено наступною версією (b7+) або не портовано в b32.
   Що це. Матриця смоук судить ТЕКСТ (чи є конструкція). Цей прогін судить ПОВЕДІНКУ:
   він відкриває стенд у jsdom, рухає повзунок і дивиться, що насправді сталося.
   Заведений у b6, бо Д-24 неможливо довести грепом: «kNet діє на всі 16» — це
   твердження про кадр, а не про рядок коду. Регекс бачив би 16 записів і мовчав би
   навіть тоді, коли картки читають чужу змінну.
   Запуск: node StockCheck_netpick_v3_live_b6.js  (з /home/claude — jsdom резолвиться
   від теки скрипта). */
"use strict";
const fs=require('fs'), {JSDOM}=require('jsdom');
const FILE=process.argv[2]||'StockCheck_netpick_stagebench_v3_b6.html';

let ok=0,bad=0;
const t=(n,c,why)=>{ if(c){ok++;console.log('  ✓ '+n);} else {bad++;console.log('  ✗ '+n+'  — '+why);} };

const dom=new JSDOM(fs.readFileSync(FILE,'utf8'),{runScripts:"dangerously",pretendToBeVisual:true});
const {window}=dom, D=window.document;

/* Лічильник перебудов. #scene — той самий елемент завжди, тож ловимо не заміну вузла,
   а присвоєння innerHTML: саме воно вбивало кадр у b4 (Д-23). */
let rebuilds=0;
const scene=D.getElementById('scene');
const proto=Object.getPrototypeOf(scene);
const desc=Object.getOwnPropertyDescriptor(proto,'innerHTML')
        || Object.getOwnPropertyDescriptor(window.Element.prototype,'innerHTML');
Object.defineProperty(scene,'innerHTML',{
  get(){return desc.get.call(this);},
  set(v){rebuilds++; desc.set.call(this,v);}
});

const frame=D.getElementById('sbox');
/* ⚠ ВУЗЛИ ПАНЕЛІ ЖИВУТЬ ДО ПЕРШОГО ТАПУ. Тап по картці кличе buildPanel(), яка
   перебудовує ряди важелів: попередньо збережене посилання лишається валідним
   об'єктом, але від'єднаним від документа — і проба тихо міряє мертвий вузол
   (перший прогін b6: capOut «не оновлювався», хоча оновлювався його наступник).
   Тому кожен доступ — свіжий запит, а не змінна. */
const lev=k=>[...D.querySelectorAll('.lv[data-k="'+k+'"] input')][0];
const out=id=>D.getElementById(id).textContent;
const push=(k,v)=>{ const i=lev(k); i.value=String(v); i.dispatchEvent(new window.Event('input',{bubbles:true})); };
const move=v=>push('kNet',v);
const isoSlug=()=>D.querySelector('#grid .ncard.is-sel').getAttribute('style').match(/--k-([A-Z0-9_]+)/)[1];

console.log('\nЛ1 · Д-24 — шістнадцять шкал замість однієї');
{
  const cards=[...D.querySelectorAll('#grid .ncard')];
  t('на сітці 16 карток', cards.length===16, 'знайдено '+cards.length);
  /* Кожна картка мусить читати ВЛАСНУ змінну. Спільна змінна на всіх — це той самий
     дефект, лише переодягнений: рух повзунка знову рухав би все разом. */
  const refs=cards.map(c=>(c.getAttribute('style')||'').match(/var\(--k-([A-Z0-9_]+)/));
  t('кожна картка читає власну змінну', refs.every(Boolean) && new Set(refs.map(m=>m[1])).size===16,
    'спільна змінна = той самий Д-24 в іншому одязі');

  /* Повзунок пише k ОБРАНОЇ мережі — питаємо в стенда, яка обрана, а не вгадуємо. */
  const sl=isoSlug();
  const before=frame.style.getPropertyValue('--k-'+sl);
  move(1.42);
  const after=frame.style.getPropertyValue('--k-'+sl);
  const written=[...D.querySelectorAll('#grid .ncard')]
      .map(c=>c.getAttribute('style').match(/--k-([A-Z0-9_]+)/)[1])
      .filter(sl=>frame.style.getPropertyValue('--k-'+sl)!=='');
  t('повзунок пише змінну кадру', before!==after&&parseFloat(after)===1.42, sl+': '+before+' → '+after);
  t('усі 16 змінних оголошені на кадрі', written.length===16, 'оголошено '+written.length+' із 16');
}

console.log('\nЛ2 · К-10 — рух важеля не перебудовує сцену');
{
  rebuilds=0;
  for(let i=0;i<40;i++) move(0.70+i*0.02);
  t('40 рухів повзунка → 0 перебудов', rebuilds===0, 'перебудов: '+rebuilds);
}

console.log('\nЛ3 · Д-23 — тап по картці не множить слухачів');
{
  rebuilds=0;
  const cards=[...D.querySelectorAll('#grid .ncard')];
  for(let i=0;i<20;i++) cards[i%16].dispatchEvent(new window.Event('click',{bubbles:true}));
  t('20 тапів → 0 перебудов сцени', rebuilds===0, 'перебудов: '+rebuilds);
  t('вибір таки перемкнувся', D.querySelectorAll('#grid .ncard.is-sel').length===1,
    'клас вибору мусить лишатись рівно на одній картці');
}

console.log('\nЛ4 · О-39 — стеля жива, гліф без стелі');
{
  const isoTap=slug=>{ const c=[...D.querySelectorAll('#grid .ncard')]
      .find(e=>e.getAttribute('style').includes('--k-'+slug+','));
    c.dispatchEvent(new window.Event('click',{bubbles:true})); };
  isoTap('MOYA_APTEKA');
  const rasterTxt=out('capOut');
  t('для растра друкується число стелі', /^≤ \d\.\d\d /.test(rasterTxt), rasterTxt);
  /* Формула мусить рухатись за plate — інакше це літерал у новому одязі (К-12). */
  const capAt=p=>{ push('plate',p); return parseFloat(out('capOut').match(/≤ (\d\.\d\d)/)[1]); };
  const c60=capAt(60), c90=capAt(90);
  t('стеля падає, коли plate росте', c60>c90, `plate60 → ${c60} · plate90 → ${c90}`);
  isoTap('FARMASTOR');
  t('гліф оголошений без стелі', /вектор/.test(out('capOut')), out('capOut'));
}

console.log('\n'+'─'.repeat(58));
console.log(bad===0?`🟢 ЗЕЛЕНИЙ · ${ok} перевірок`:`🔴 ЧЕРВОНИЙ · ${ok} ✓ / ${bad} ✗`);
process.exit(bad?1:0);
