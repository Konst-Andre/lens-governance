/* живе доки: вузол F2 не закрито (b29.4 зібрано + device✓). Далі — в archive/ разом із b28.
   StockCheck · матриця моделі b29.1 — драбина адреси (З-1/З-3) + visitModel/journalGroups (R1).
   Запуск:  node StockCheck_b29_1_jsdom_matrix.js  [шлях_до_html]
   DOM не потрібен: під тестом чисті data-функції. Код НЕ дублюється —
   витягується з живого білда за якорями, інакше матриця перевіряє свою копію (wsd 12.1). */
const fs=require('fs'),path=require('path'),vm=require('vm');
const FILE=process.argv[2]||path.join(__dirname,'StockCheck_port_b29_1.html');
const src=fs.readFileSync(FILE,'utf8');

function grab(re,name){const m=re.exec(src);if(!m)throw new Error('якір не знайдено: '+name);return m[0];}
const chunk=[
  grab(/function displayAddr\(a\)\{[^\n]*\n/,'displayAddr'),
  grab(/function addrExt\(a\)\{[\s\S]*?\.trim\(\);\}/,'addrExt'),
  grab(/var ADDR_SPLIT=[^\n]*\n/,'ADDR_SPLIT'),
  grab(/function addrParts\(a\)\{[\s\S]*?note:''\};\}/,'addrParts'),
  grab(/function visitModel\(\)\{[\s\S]*?\n\}/,'visitModel'),
  grab(/function journalGroups\(\)\{[\s\S]*?\n\}/,'journalGroups')
].join('\n');

/* стаби оточення — рівно ті, що модель споживає, і не більше */
const sandbox={PH:[],ST:{phs:{}},S:{area:'',city:'',q:''}};
sandbox.topMatch=function(m){
  if(m.area!==sandbox.S.area)return false;
  if(sandbox.S.city&&m.city!==sandbox.S.city)return false;
  const q=sandbox.S.q.trim().toLowerCase();
  if(q){const h=(m.addr+' '+m.city+' '+m.px).toLowerCase();if(h.indexOf(q)<0)return false;}
  return true;
};
vm.createContext(sandbox);
vm.runInContext(chunk,sandbox);
const {addrExt,addrParts,visitModel,journalGroups}=sandbox;

let pass=0,fail=0;
const chk=(n,c)=>{c?(pass++,console.log('  ✓ '+n)):(fail++,console.log('  ✗ '+n));};
const eq=(n,a,b)=>chk(n+'  →  '+JSON.stringify(a),a===b);

const A1='Україна, Дніпропетровська обл., м.Дніпро, вул.Нижньодніпровська, 17. ТЦ Караван, тер. Слобожанського с/р, комплекс буд. та спор., 17';
const A2='Україна, Полтавська обл., Зіньківський р-н., м.Зіньків, вул.Воздвиженська, 49Д. Літ. А-2 поряд Кулиничі';
const A3='Україна, Дніпропетровська обл., м.Дніпро, вул.Калинова, 82Б';

console.log('\nA · ДРАБИНА АДРЕСИ');
eq('A1 донор уже досить — ext не змінює',addrExt(A1),'вул.Нижньодніпровська, 17. ТЦ Караван, тер. Слобожанського с/р, комплекс буд. та спор., 17');
eq('A2 ext зрізає р-н + тип поселення (донор не бачить)',addrExt(A2),'вул.Воздвиженська, 49Д. Літ. А-2 поряд Кулиничі');
chk('A3 донор НЕ зрізає р-н — сходинки різні, не дубль',
  sandbox.displayAddr(A2).startsWith('Зіньківський р-н.'));
chk('ідемпотентність: ext(ext(x)) === ext(x)',addrExt(addrExt(A2))===addrExt(A2));

console.log('\nB · СПЛІТ');
eq('B1 ядро A1',addrParts(A1).core,'вул.Нижньодніпровська, 17');
chk('B2 хвіст A1 не порожній',addrParts(A1).note.indexOf('ТЦ Караван')===0);
eq('B3 ядро A2',addrParts(A2).core,'вул.Воздвиженська, 49Д');
eq('B4 хвіст A2',addrParts(A2).note,'Літ. А-2 поряд Кулиничі');
eq('B5 без хвоста → note порожній',addrParts(A3).note,'');
eq('B6 без хвоста → core = вся адреса',addrParts(A3).core,'вул.Калинова, 82Б');
chk('B7 ядро НІКОЛИ не порожнє',[A1,A2,A3,'','вул.Миру'].every(a=>{
  const p=addrParts(a);return p.core===addrExt(a)||p.core.length>0;}));

console.log('\nC · visitModel — одиниця = ВІЗИТ');
sandbox.PH=[{px:'P1',area:'Дніпро',city:'Дніпро',addr:A1,oTC:'B',iW:'A'},
            {px:'P2',area:'Дніпро',city:'Зіньків',addr:A2,oTC:'C',iW:'D'},
            {px:'P3',area:'Дніпро',city:'Дніпро',addr:A3,oTC:'A',iW:'A'}];
sandbox.ST={phs:{
  P1:{visits:[{date:'2026-07-28',vals:{a:1,b:2},transferred:true,tier:{oTC:'B',iW:'A'}},
              {date:'2026-08-01',vals:{a:1},transferred:true,tier:{oTC:'A',iW:'A'}}]},
  P2:{visits:[{date:'2026-08-01',vals:{a:1,b:2,c:3},transferred:true}]},
  P3:{visits:[{date:'2026-08-02',vals:{a:1},transferred:false}]}}};
let VM=visitModel();
eq('C1 одна аптека з 2 візитами → 2 записи',VM.filter(r=>r.px==='P1').length,2);
eq('C2 усього записів (незданий теж у моделі)',VM.length,4);
eq('C3 filled = кількість ключів vals',VM.find(r=>r.px==='P2').filled,3);
eq('C4 tier візиту перекриває tier аптеки',VM.filter(r=>r.px==='P1')[1].otc,'A');
eq('C5 tier аптеки як фолбек, коли візит без tier',VM.find(r=>r.px==='P2').otc,'C');
chk('C6 запис несе core/note зі спліту',VM.find(r=>r.px==='P2').core==='вул.Воздвиженська, 49Д');
sandbox.ST={phs:{}};
eq('C7 аптеки без visits → нуль записів',visitModel().length,0);

console.log('\nD · journalGroups — зріз, порядок, фільтр');
sandbox.ST={phs:{
  P1:{visits:[{date:'2026-07-28',vals:{a:1},transferred:true},
              {date:'2026-08-01',vals:{a:1},transferred:true}]},
  P2:{visits:[{date:'2026-08-01',vals:{a:1},transferred:true}]},
  P3:{visits:[{date:'2026-08-02',vals:{a:1},transferred:false}]}}};
sandbox.S={area:'Дніпро',city:'',q:''};
let G=journalGroups();
eq('D1 незданий візит у журнал НЕ потрапляє',G.length,2);
eq('D2 групи спадно за датою',G[0].date,'2026-08-01');
eq('D3 друга група',G[1].date,'2026-07-28');
eq('D4 у групі 01.08 два записи',G[0].rows.length,2);
eq('D5 усередині групи спершу місто (Дніпро < Зіньків)',G[0].rows[0].city,'Дніпро');
sandbox.S={area:'Дніпро',city:'Зіньків',q:''};
G=journalGroups();
eq('D6 topMatch застосовано: фільтр міста ріже',G.length,1);
eq('D7 лишився саме Зіньків',G[0].rows[0].px,'P2');
sandbox.S={area:'Львів',city:'',q:''};
eq('D8 порожній зріз → [] , не падіння',journalGroups().length,0);

console.log('\n──────────────');
console.log(fail?`✗ ${fail} провалено, ${pass} пройдено`:`✓ усі ${pass} пройдено`);
process.exit(fail?1:0);
