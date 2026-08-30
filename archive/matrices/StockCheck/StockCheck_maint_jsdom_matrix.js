const fs=require('fs');const {JSDOM}=require('jsdom');
const PATH=process.env.SC_BUILD||process.argv[2]||'StockCheck_port_b29_1.html';
const HTML=fs.readFileSync(PATH,'utf8');
/* wsd 1.10 — детектор звіряє з ОГОЛОШЕННЯМ (APP_BUILD у самому білді), не з літералом.
   До b29.1 тут стояли зашиті 'b26' і 'v2.15.0': матриця валилась на КОРЕКТНОМУ новому
   білді, і 12 червоних привчали ігнорувати червоне. */
const CURB=/build:'([^']+)'/.exec(HTML)[1];
const CURV=/ver:'([^']+)'/.exec(HTML)[1];
const NEXTV='v2.99.0';

const UA={
  safari:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1',
  telegram:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Telegram-iOS',
  android:'Mozilla/5.0 (Linux; Android 16; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Mobile Safari/537.36',
};

function boot(ua,opts={}){
  const dom=new JSDOM(HTML,{runScripts:'dangerously',url:'https://konst-andre.github.io/stockcheck/',
    pretendToBeVisual:true,
    beforeParse(w){
      /* jsdom 30 ігнорує опцію userAgent → підміняємо на екземплярі navigator */
      Object.defineProperty(w.navigator,'userAgent',{value:ua,configurable:true});
      Object.defineProperty(w.navigator,'platform',{value:opts.platform||'iPhone',configurable:true});
      w.matchMedia=q=>({matches: q.includes('display-mode: standalone')?!!opts.standalone:false,
        media:q,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
      w.fetch=()=>opts.fetch?opts.fetch(w):Promise.reject(new Error('offline'));
      if(opts.tgProxy)w.TelegramWebviewProxy={};
      w.scrollTo=()=>{};
    }});
  return dom;
}
const T=(n,c)=>console.log((c?'  ✓ ':'  ✗ FAIL ')+n);
const txt=d=>d.window.document.getElementById('mtCard').textContent.replace(/\s+/g,' ').trim();
const has=(d,s)=>d.window.document.getElementById('mtCard').innerHTML.includes(s);
const wait=ms=>new Promise(r=>setTimeout(r,ms));

const REMOTE=same=>HTML.replace("build:'"+CURB+"'","build:'"+(same?CURB:CURB+'.next')+"'")
                       .replace("ver:'"+CURV+"'","ver:'"+(same?CURV:NEXTV)+"'");

(async()=>{
let fails=0; const chk=(n,c)=>{if(!c)fails++;T(n,c);};

console.log('\n── A · середовища × стан idle (перед відповіддю fetch) ──');
for(const [name,ua,o] of [
  ['safari',UA.safari,{}],
  ['telegram (UA)',UA.telegram,{}],
  ['telegram (proxy, UA без мітки)',UA.safari,{tgProxy:1}],
  ['android_np',UA.android,{}],
  ['standalone',UA.safari,{standalone:1}],
]){
  const d=boot(ua,o); await wait(60);
  const t=txt(d);
  console.log('   ['+name+'] → '+t);
  chk(name+': рядок версії живе завжди (варіант B)', t.includes('Версія '+CURV));
  if(name==='standalone') chk('  standalone: рядок встановлення прибрано', !t.includes('Додому')&&!t.includes('Встановити'));
  else chk('  рядок встановлення присутній', t.includes('Додому')||t.includes('Встановити'));
  if(name.startsWith('telegram')) chk('  підпис = Спершу відкрити в Safari', t.includes('Спершу відкрити в Safari'));
  if(name==='safari') chk('  підпис = Без адресного рядка', t.includes('Без адресного рядка'));
  if(name==='android_np') chk('  підпис = Через меню браузера', t.includes('Через меню браузера'));
  chk('  слот-хвіст .mi-act у кожному рядку',
      d.window.document.querySelectorAll('#mtCard .mi').length===d.window.document.querySelectorAll('#mtCard .mi-act').length);
  d.window.close();
}

console.log('\n── B · стани перевірки версії ──');
for(const [name,f,exp,dot] of [
  ['актуальна',   w=>Promise.resolve({ok:true,text:()=>Promise.resolve(REMOTE(true))}), 'Версія актуальна', false],
  ['є оновлення', w=>Promise.resolve({ok:true,text:()=>Promise.resolve(REMOTE(false))}), 'Оновити до '+NEXTV, true],
  ['офлайн',      w=>Promise.reject(new Error('net')),                                    'Не вдалося перевірити', false],
  ['HTTP 404',    w=>Promise.resolve({ok:false,text:()=>Promise.resolve('')}),            'Не вдалося перевірити', false],
  ['сміття у відповіді', w=>Promise.resolve({ok:true,text:()=>Promise.resolve('<html>nope</html>')}),'Не вдалося перевірити', false],
]){
  const d=boot(UA.safari,{fetch:f}); await wait(1100);
  chk(name+' → «'+exp+'»', txt(d).includes(exp));
  const dots=[...d.window.document.querySelectorAll('.js-kdot')];
  chk('  крапка на 3 кебабах = '+dot, dots.length===3 && dots.every(x=>x.classList.contains('on')===dot));
  d.window.close();
}

console.log('\n── C · заморозка станів (Д5) ──');
{
  let resolve; const p=new Promise(r=>resolve=r);
  const d=boot(UA.safari,{fetch:()=>p});
  await wait(900);
  d.window.openSheet();                                   // меню відкрите
  resolve({ok:true,text:()=>Promise.resolve(REMOTE(false))});
  await wait(120);
  chk('під відкритим шітом рядок НЕ підмінився', txt(d).includes('Перевіряємо оновлення'));
  d.window.closeSheets();
  await wait(400);
  chk('після закриття стан застосувався', txt(d).includes('Оновити до '+NEXTV));
  chk('крапка засвітилась після зливу',
      [...d.window.document.querySelectorAll('.js-kdot')].every(x=>x.classList.contains('on')));
  d.window.close();
}

console.log('\n── D · гард зливу не спрацьовує на передачі меню→About ──');
{
  let resolve; const p=new Promise(r=>resolve=r);
  const d=boot(UA.safari,{fetch:()=>p});
  await wait(900);
  d.window.openSheet();
  resolve({ok:true,text:()=>Promise.resolve(REMOTE(false))});
  await wait(60);
  d.window.openAbout();                                   // closeSheet + 120ms → sh-about
  await wait(400);
  chk('під About злив НЕ відбувся', txt(d).includes('Перевіряємо оновлення'));
  chk('sh-about відкритий', d.window.document.getElementById('sh-about').classList.contains('on'));
  d.window.closeSheets();
  await wait(400);
  chk('після повного закриття злив стався', txt(d).includes('Оновити до '+NEXTV));
  d.window.close();
}

console.log('\n── E · beforeinstallprompt / appinstalled ──');
{
  const d=boot(UA.android,{}); await wait(60);
  chk('до події: інструкція, не мертва кнопка', txt(d).includes('Через меню браузера'));
  const ev=new d.window.Event('beforeinstallprompt');
  let prompted=false, choice;
  ev.prompt=()=>{prompted=true;};
  ev.userChoice=Promise.resolve({outcome:'accepted'});
  d.window.dispatchEvent(ev);
  await wait(30);
  chk('після події: рядок став кнопкою', txt(d).includes('Встановити застосунок'));
  chk('  афорданс = пігулка «Встановити»', has(d,'doact'));
  d.window.document.getElementById('miIns').dispatchEvent(new d.window.Event('click'));
  await wait(60);
  chk('  prompt() викликано', prompted);
  chk('  після вибору подія відпущена → назад до інструкції', txt(d).includes('Через меню браузера'));
  d.window.dispatchEvent(new d.window.Event('appinstalled'));
  await wait(60);
  chk('appinstalled → рядок зник без перезавантаження', !txt(d).includes('Додому')&&!txt(d).includes('Встановити'));
  chk('  рядок версії лишився', txt(d).includes('Версія'));
  d.window.close();
}

console.log('\n── F · шіт інструкції ──');
for(const [name,ua,o,hd,step0] of [
  ['safari',UA.safari,{},'Додати на екран Додому',false],
  ['telegram',UA.telegram,{},'Додати на екран Додому',true],
  ['android_np',UA.android,{},'Встановити застосунок',false],
]){
  const d=boot(ua,o); await wait(60);
  const doc=d.window.document;
  chk(name+': заголовок = '+hd, doc.getElementById('insHd').textContent===hd);
  chk('  крок 0 банером = '+step0, !!doc.querySelector('#insBody .step0b')===step0);
  chk('  стиль glyph (є .gl, немає .n)', !!doc.querySelector('#insBody .stp .gl') && !doc.querySelector('#insBody .stp .n'));
  chk('  3 кроки', doc.querySelectorAll('#insBody .stp').length===3);
  doc.getElementById('miIns').dispatchEvent(new d.window.Event('click'));
  await wait(200);
  chk('  меню→install передача', doc.getElementById('sh-install').classList.contains('on')
      && !doc.getElementById('sheet').classList.contains('on'));
  d.window.closeSheets(); await wait(30);
  chk('  closeSheets гасить sh-install', !doc.getElementById('sh-install').classList.contains('on'));
  // регресія b26_1: колізія імен класів у CTA-ряду (прецедент dpicker b24)
  const btns=[...doc.querySelectorAll('.ins-cta button')];
  chk('  CTA: 2 кнопки, обидві префіксовані', btns.length===2
      && btns.every(x=>/\bins-(sec|pri)\b/.test(x.className))
      && !btns.some(x=>/(^|\s)(sec|pri)(\s|$)/.test(x.className)));
  d.window.close();
}

console.log('\n── G · двигун ефекту duo ──');
{
  const d=boot(UA.safari,{fetch:()=>Promise.resolve({ok:true,text:()=>Promise.resolve(REMOTE(false))})});
  await wait(1100);
  const doc=d.window.document, body=doc.body;
  d.window.openSheet();
  chk('одразу після openSheet класу ще немає', !body.classList.contains('fx-duo'));
  await wait(500);                                        // 340 страхувальний + 120 delay
  chk('страхувальний таймер запустив ефект', body.classList.contains('fx-duo'));
  d.window.closeSheets(); await wait(20);
  chk('на закритті клас знято', !body.classList.contains('fx-duo'));
  // подія + таймер = рівно один запуск
  d.window.openSheet();
  const ev=new d.window.Event('transitionend'); Object.defineProperty(ev,'propertyName',{value:'transform'});
  doc.getElementById('sheet').dispatchEvent(ev);
  await wait(500);
  chk('transitionend + таймер → одноразовість тримається', body.classList.contains('fx-duo'));
  d.window.closeSheets(); await wait(20);
  d.window.close();
}
{
  const d=boot(UA.safari,{fetch:()=>Promise.resolve({ok:true,text:()=>Promise.resolve(REMOTE(true))})});
  await wait(1100);
  d.window.openSheet(); await wait(500);
  chk('без апдейта ефект не грає', !d.window.document.body.classList.contains('fx-duo'));
  d.window.close();
}

console.log('\n── H · тротлінг visibilitychange ──');
{
  let n=0;
  const d=boot(UA.safari,{fetch:()=>{n++;return Promise.reject(new Error('x'));}});
  await wait(900);
  const c=n;
  for(let i=0;i<5;i++) d.window.document.dispatchEvent(new d.window.Event('visibilitychange'));
  await wait(80);
  chk('5 повернень у фокус за 5 хв → 0 зайвих запитів', n===c);
  d.window.close();
}

console.log(fails? '\n✗ ПРОВАЛІВ: '+fails : '\n✓ УСІ КЛІТИНИ ПРОЙДЕНО');
process.exit(fails?1:0);
})();
