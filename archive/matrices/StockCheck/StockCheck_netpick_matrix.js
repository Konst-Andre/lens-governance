/* живе доки: не закритий вузол H3 · матриця стенда netpick (wsd 2.5 — матриця пар)
   запуск: node StockCheck_netpick_matrix.js <файл_стенда.html> */
const {JSDOM}=require('jsdom'),fs=require('fs');
const FILE=process.argv[2]||'/mnt/user-data/outputs/StockCheck_netpick_stagebench_v2.html';
let pass=0,fail=0;
function ok(c,m){c?(pass++):(fail++,console.log('  ✗ '+m));}

const dom=new JSDOM(fs.readFileSync(FILE,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window,d=w.document;
w.addEventListener('error',e=>{fail++;console.log('  ✗ UNCAUGHT: '+e.message);});

const seg=(id,v)=>{const b=[...d.querySelectorAll('#'+id+' button')].find(x=>x.getAttribute('data-v')===v);
  b.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));};
const stage=id=>d.getElementById(id);

setTimeout(()=>{
  console.log('\n── А · РЕЄСТР ↔ СІТКА ──');
  /* const/let у класичному скрипті НЕ стають властивостями window → тягнемо через eval */
  const NETS=w.eval('NETS'),CNT=w.eval('CNT'),AREAS=w.eval('AREAS');
  ok(NETS.length===16,'реєстр 16 рядків, отримано '+NETS.length);
  ok(NETS.filter(n=>n.kind==='glyph').length===1,'рівно один векторний знак');
  ok(NETS.filter(n=>!n.slug).length===1,'рівно одна монограма');
  ok(NETS.find(n=>n.net==='Фармастор').label==='Фармастор','label Фармастора = «Фармастор»');
  ok(NETS.every(n=>/^#[0-9A-F]{6}$/i.test(n.color)),'усі color — валідний HEX');
  ok(Object.keys(CNT).length===16,'зріз даних покриває 16 мереж');

  console.log('\n── Б · КЛІК ПО КОЖНІЙ ПЛИТЦІ · МОДЕЛЬ A ──');
  seg('sg-model','A');
  AREAS.forEach(area=>{
    seg('sg-area',area);
    const tl=[...stage('st-l').querySelectorAll('.ntl')];
    tl.forEach(t=>{
      const key=t.getAttribute('data-net');
      ok(key!=='[object Object]','data-net не об\'єкт ('+area+')');
      ok(key==='__ALL__'||NETS.some(n=>n.net===key),'ключ «'+key+'» є в реєстрі');
      t.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    });
  });

  setTimeout(()=>{
    console.log('\n── В · МОДЕЛЬ B · плитка «Всі» ──');
    seg('sg-model','B');
    const first=stage('st-l').querySelector('.ntl');
    ok(first.getAttribute('data-net')==='__ALL__','перша плитка моделі B = «Всі»');
    ok(stage('st-l').querySelectorAll('.ntl').length===17,'B дає 17 плиток (16+Всі), маємо '
       +stage('st-l').querySelectorAll('.ntl').length);
    seg('sg-model','A');
    ok(stage('st-l').querySelectorAll('.ntl').length===16,'A дає 16 плиток без «Всі»');

    console.log('\n── Г · ЛІЧИЛЬНИК ⟂ СПИСОК (дефект b28) ──');
    w.eval('AREAS').forEach(area=>{
      seg('sg-area',area);
      const foot=stage('st-l').querySelector('.np-foot').textContent;
      const m=foot.match(/Σ плиток\s+(\d+)\s+· в області\s+(\d+)/);
      ok(m&&m[1]===m[2],'Σ плиток == в області ('+area+'): '+(m?m[1]+'/'+m[2]:'не розпарсено'));
      ok(foot.indexOf('✗')<0,'детектор не червоний ('+area+')');
    });

    console.log('\n── Д · НУЛІ: ховати ⟂ сірити ──');
    seg('sg-area','Кіровоградська');
    seg('sg-zero','grey');
    const grey=stage('st-l').querySelectorAll('.ntl').length;
    seg('sg-zero','hide');
    const hide=stage('st-l').querySelectorAll('.ntl').length;
    ok(grey===16&&hide===7,'Кіровоградська: сірі 16 / ховати 7, маємо '+grey+'/'+hide);
    seg('sg-zero','grey');

    console.log('\n── Е · ВИД ЗНАКА НА ПЛИТЦІ ──');
    seg('sg-area','Полтавська');
    const tiles=[...stage('st-l').querySelectorAll('.ntl')];
    const fp=tiles.find(t=>t.getAttribute('data-net')==='Фармастор');
    ok(fp&&fp.querySelector('.gl svg'),'Фармастор рендериться вектором, не растром');
    ok(fp&&!fp.querySelector('img'),'у Фармастора немає <img>');
    const zp=tiles.find(t=>t.getAttribute('data-net')==='Зайцева Л.В.');
    ok(zp&&zp.querySelector('.mono')&&zp.querySelector('.mono').textContent==='З','монограма Зайцевої = «З»');
    ok(tiles.filter(t=>t.querySelector('img')).length===14,'растрових плиток 14 (15 знаків − Фармастор)');

    console.log('\n── Ж · НАБОРИ ВАЖЕЛІВ РОЗДІЛЕНІ (A45) ──');
    const L=stage('st-l'),D=stage('st-d');
    ok(L.style.getPropertyValue('--shBlur')!=='','світлий стейдж отримав shBlur');
    ok(L.style.getPropertyValue('--npFloorL')==='','світлий НЕ отримав floor (набір темної)');
    ok(D.style.getPropertyValue('--npFloorL')!=='','темний стейдж отримав floor');
    ok(D.style.getPropertyValue('--shBlur')==='','темний НЕ отримав shBlur (набір світлої)');

    console.log('\n── З · 128 ⟂ 192 ──');
    seg('sg-asset','128');
    const src128=stage('st-l').querySelector('.ntl img').getAttribute('src').length;
    seg('sg-asset','192');
    const src192=stage('st-l').querySelector('.ntl img').getAttribute('src').length;
    ok(src192>src128,'192 важчий за 128 ('+src128+' → '+src192+')');
    seg('sg-asset','128');

    console.log('\n'+(fail?'✗ ПРОВАЛЕНО: '+fail+' · пройдено: '+pass:'✓ УСІ '+pass+' ТВЕРДЖЕНЬ ПРОЙДЕНО'));
    process.exit(fail?1:0);
  },400);
},400);
