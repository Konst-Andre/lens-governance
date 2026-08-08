/* живе доки: b32.0 не пройдено device-тест. Далі — в archive/stands/ разом із H4 самері.
   StockCheck · матриця b32.0 «шов» — BASELINE (М-20) + пост-асерти.
   Запуск:  node StockCheck_b32_0_matrix.js [шлях_до_html] [--post]
     без --post : BASELINE, знімається з b31 ДО патча, друкує числа
     з --post   : ті самі заміри + асерти інертності/очікуваних змін на b32.0

   ЧОМУ vm, а не jsdom: під тестом чисті data-функції. DOM не потрібен, npm — теж.
   Код НЕ дублюється — витягується з живого білда за якорями (wsd 12.1).

   Д-2 (мікроскоп): асерт «числа рівні» на дефолтній області дав би ХИБНИЙ ✗ —
   п.7 навмисно міняє AREAS[0]. Тому кожен зріз береться з ЯВНО заданою областю,
   а порядок AREAS перевіряється окремим асертом-очікуванням.
   Д-3: інертні ЧИСЛА. Рядки fname/label міняються за побудовою (пп.4/5). */

const fs = require('fs'), path = require('path'), vm = require('vm');
const args = process.argv.slice(2);
const POST = args.includes('--post');
const FILE = args.find(a => !a.startsWith('--')) || path.join(__dirname, 'b31.html');
const src = fs.readFileSync(FILE, 'utf8');

function grab(re, name) {
  const m = re.exec(src);
  if (!m) throw new Error('якір не знайдено: ' + name);
  return m[0];
}

/* ── витяг із білда. AREA_ORDER / netScopeLabel можуть не існувати (b31) ──── */
function grabSafe(re) { const m = re.exec(src); return m ? m[0] : ''; }

const parts = [
  /* М-21 (мікроскоп b32.0): netScopeLabel читає label із реєстру → без NETS і
     netLabel пісочниця валиться «NETS is not defined» на ПРАВИЛЬНОМУ білді.
     grabSafe, бо в b31 їх іще немає — baseline мусить зніматись тим же файлом. */
  grabSafe(/const NETS=\[[\s\S]*?\n\];/),
  grabSafe(/function netLabel\(n\)\{[^\n]*\n/),
  grab(/const PH=\[[\s\S]*?\n\];/, 'PH'),
  grabSafe(/const AREA_ORDER=[^\n]*\n/),
  grab(/const AREAS=[\s\S]*?\n(?=function citiesOf)/, 'AREAS'),
  grab(/function citiesOf\(a\)\{[\s\S]*?\n(?=var S=)/, 'citiesOf'),
  grab(/var S=\{[^\n]*\n/, 'S'),
  grab(/function topMatch\(m\)\{[\s\S]*?\n\}/, 'topMatch'),
  grab(/function displayAddr\(a\)\{[^\n]*\n/, 'displayAddr'),
  grab(/var ADDR_SPLIT=[^\n]*\n/, 'ADDR_SPLIT'),
  grab(/function addrExt\(a\)\{[\s\S]*?\.trim\(\);\}/, 'addrExt'),
  grab(/function addrParts\(a\)\{[\s\S]*?note:''\};\}/, 'addrParts'),
  grab(/function visitModel\(\)\{[\s\S]*?\n\}/, 'visitModel'),
  grab(/function journalGroups\(\)\{[\s\S]*?\n\}/, 'journalGroups'),
  grab(/function homeModel\(\)\{[\s\S]*?\n\}/, 'homeModel'),
  grab(/function plApt\(n\)\{[^\n]*\n/, 'plApt'),
  grab(/function plVis\(n\)\{[^\n]*\n/, 'plVis'),
  grab(/function fsafe\(s\)\{[^\n]*\n/, 'fsafe'),
  grab(/function scopeArea\(\)\{[^\n]*\n/, 'scopeArea'),
  grab(/function scopeName\(list\)\{[\s\S]*?\n\}/, 'scopeName'),
  grabSafe(/function netScopeLabel\(list\)\{[\s\S]*?\n\}/),
  /* const/let у vm.runInContext лексичні — на sandbox не потрапляють. Експорт явний. */
  'globalThis.__E={PH:PH,AREAS:AREAS,S:S,topMatch:topMatch,homeModel:homeModel,' +
  'visitModel:visitModel,journalGroups:journalGroups,scopeName:scopeName,' +
  "netScopeLabel:(typeof netScopeLabel==='function'?netScopeLabel:null)};"
].join('\n');

/* ── стаби оточення: рівно те, що споживають витягнуті функції ────────────── */
const sandbox = {
  ST: { phs: {} },
  TOTAL: 83,
  today: () => '2026-08-08',
  todayVisit: px => { const e = sandbox.ST.phs[px]; if (!e || !e.visits) return null;
    return e.visits.filter(v => v.date === '2026-08-08')[0] || null; },
  getPh: px => sandbox.PH.filter(p => p.px === px)[0] || null,
  esc: s => '' + s,
  console
};
vm.createContext(sandbox);
vm.runInContext(parts, sandbox);
const { PH, AREAS, S, topMatch, homeModel, visitModel, journalGroups, scopeName,
        netScopeLabel } = sandbox.__E;
/* §5 самері H4.1, детектор К2: жодна сутність не undefined ДО першого заміру */
Object.entries(sandbox.__E).forEach(([k, v]) => {
  if (v === undefined) throw new Error('витяг порожній: ' + k);
});

/* ── детермінований ST: 3 аптеки × 2 візити, по одній на область ──────────── */
const pick = a => PH.filter(p => p.area === a)[0];
const SEEDS = ['Дніпропетровська', 'Полтавська', 'Кіровоградська'].map(pick);
SEEDS.forEach((p, k) => {
  sandbox.ST.phs[p.px] = { visits: [
    { date: '2026-08-06', transferred: true, vals: { a: 1, b: 2 }, tier: null },
    { date: '2026-08-08', transferred: k === 0, vals: { a: 1 }, tier: null }
  ] };
});

/* ── замір ────────────────────────────────────────────────────────────────── */
let pass = 0, fail = 0;
const chk = (n, c) => { c ? (pass++, console.log('  ✓ ' + n)) : (fail++, console.log('  ✗ ' + n)); };
const M = {};

console.log('\n══ A · РЕЄСТР ОБЛАСТЕЙ ══');
M.areas = AREAS.slice();
M.areaCounts = AREAS.map(a => PH.filter(p => p.area === a).length);
console.log('  AREAS      = ' + JSON.stringify(M.areas));
console.log('  лічильники = ' + JSON.stringify(M.areaCounts));
console.log('  AREAS[0]   = ' + M.areas[0]);

console.log('\n══ B · ДОШКА — homeModel().filter(topMatch) ══');
console.log('  (Д-2: область задається ЯВНО, не з дефолту S.area)');
M.board = {};
AREAS.forEach(a => {
  S.area = a; S.city = ''; S.q = '';
  M.board[a] = homeModel().filter(topMatch).length;
  console.log('  ' + a.padEnd(20) + ' → ' + M.board[a]);
});
S.area = 'Дніпропетровська'; S.city = 'Дніпро'; S.q = '';
M.boardCity = homeModel().filter(topMatch).length;
console.log('  Дніпропетровська/Дніпро → ' + M.boardCity);
S.city = ''; S.q = 'наук';
M.boardQ = homeModel().filter(topMatch).length;
console.log('  Дніпропетровська + q="наук" → ' + M.boardQ);

console.log('\n══ C · ЖУРНАЛ — visitModel / journalGroups ══');
S.area = 'Дніпропетровська'; S.city = ''; S.q = '';
M.visits = visitModel().length;
M.jGroups = journalGroups().length;
M.jRows = journalGroups().reduce((s, g) => s + (g.rows ? g.rows.length : (g[1] ? g[1].length : 0)), 0);
console.log('  visitModel()            = ' + M.visits);
console.log('  journalGroups()  груп   = ' + M.jGroups);
console.log('  journalGroups()  рядків = ' + M.jRows);

console.log('\n══ D · ІМЕНА ФАЙЛІВ — scopeName ══');
const mk = (p, d) => ({ ph: p, vis: { date: d } });
const L1 = [mk(SEEDS[0], '2026-08-06')];
const L2 = [mk(SEEDS[0], '2026-08-06'), mk(SEEDS[0], '2026-08-08')];
const L3 = SEEDS.map(p => mk(p, '2026-08-06'));
S.area = 'Дніпропетровська'; S.city = '';
M.fn1 = scopeName(L1); M.fn2 = scopeName(L2); M.fn3 = scopeName(L3);
console.log('  1 аптека           → ' + M.fn1);
console.log('  1 аптека / 2 дати  → ' + M.fn2);
console.log('  3 аптеки           → ' + M.fn3);

console.log('\n══ E · МЕРЕЖІ ══');
M.nets = {}; PH.forEach(p => { M.nets[p.net] = (M.nets[p.net] || 0) + 1; });
console.log('  унікальних net = ' + Object.keys(M.nets).length);
M.netInSeeds = SEEDS.map(p => p.net);
console.log('  net сідів      = ' + JSON.stringify(M.netInSeeds));
M.hasNetField = { visitModel: 'net' in (visitModel()[0] || {}),
                  homeModel: 'net' in (homeModel()[0] || {}) };
console.log('  net у моделях  = ' + JSON.stringify(M.hasNetField));

/* ── асерти ───────────────────────────────────────────────────────────────── */
const BASE = path.join(__dirname, 'b32_0_baseline.json');

if (!POST) {
  fs.writeFileSync(BASE, JSON.stringify(M, null, 1));
  console.log('\n══ BASELINE записано → ' + BASE + ' ══');
  console.log('  965 аптек · 3 області · ' + Object.keys(M.nets).length + ' мереж');
  console.log('\n  ОЧІКУВАНІ ЗМІНИ в b32.0 (оголошено ДО патча, Д-2/Д-3):');
  console.log('   · AREAS[0] : ' + M.areas[0] + ' → Дніпропетровська');
  console.log('   · AREAS    : порядок появи → AREA_ORDER');
  console.log('   · fname    : Фармастор_… → мітка мережі зі зрізу');
  console.log('   · net у моделях : false → true (обидві)');
  console.log('  ІНЕРТНЕ: усі лічильники B/C, лічильники областей, склад мереж.');
} else {
  const B = JSON.parse(fs.readFileSync(BASE, 'utf8'));
  console.log('\n══ F · АСЕРТИ ІНЕРТНОСТІ (числа) ══');
  AREAS.forEach(a => chk('дошка ' + a + ' = ' + B.board[a], M.board[a] === B.board[a]));
  chk('дошка Дніпро/місто = ' + B.boardCity, M.boardCity === B.boardCity);
  chk('дошка пошук "наук" = ' + B.boardQ, M.boardQ === B.boardQ);
  chk('visitModel() = ' + B.visits, M.visits === B.visits);
  chk('журнал груп = ' + B.jGroups, M.jGroups === B.jGroups);
  chk('журнал рядків = ' + B.jRows, M.jRows === B.jRows);
  chk('лічильники областей незмінні', JSON.stringify(M.areaCounts.slice().sort()) ===
      JSON.stringify(B.areaCounts.slice().sort()));
  chk('склад мереж незмінний (16)', Object.keys(M.nets).length === Object.keys(B.nets).length);

  console.log('\n══ G · АСЕРТИ ОЧІКУВАНИХ ЗМІН ══');
  chk('Д-27 · AREAS[0] === Дніпропетровська', M.areas[0] === 'Дніпропетровська');
  chk('Д-27 · порядок = Дніпро → Полтава → Кіровоград',
      JSON.stringify(M.areas) === JSON.stringify(['Дніпропетровська', 'Полтавська', 'Кіровоградська']));
  chk('Д-11 · net у visitModel()', M.hasNetField.visitModel === true);
  chk('Д-11 · net у homeModel()', M.hasNetField.homeModel === true);
  chk('Д-6 · fname 1 аптека БЕЗ хардкоду Фармастор_', M.fn1.indexOf('Фармастор_') !== 0);
  chk('Д-6 · fname 3 аптеки БЕЗ хардкоду Фармастор_', M.fn3.indexOf('Фармастор_') !== 0);
  chk('Д-6 · fname лишається .xlsx', /\.xlsx$/.test(M.fn1) && /\.xlsx$/.test(M.fn3));
  chk('Д-8 · S.net існує і дефолт пустий', 'net' in S && S.net === '');
  chk('Р-30 · netScopeLabel існує', typeof netScopeLabel === 'function');
  chk('Р-30 · одна мережа → label з реєстру ("Аптека 9-1-1")',
      netScopeLabel(L1) === 'Аптека 9-1-1');
  chk('М-25/A · кілька мереж → "Всі мережі" (пробіл, не дефіс)',
      netScopeLabel(L3) === 'Всі мережі');
  chk('М-26 · порожній зріз → форма "кілька"', netScopeLabel([]) === 'Всі мережі');
  chk('Р-30 · fname 1 аптека починається з мітки мережі',
      M.fn1.indexOf('Аптека 9-1-1_') === 0);
  chk('п.3 · topMatch при S.net="" — no-op',
      (() => { S.area = 'Дніпропетровська'; S.city = ''; S.q = ''; S.net = '';
        return homeModel().filter(topMatch).length === B.board['Дніпропетровська']; })());
  chk('п.3 · topMatch при S.net="АНЦ" — ріже',
      (() => { S.net = 'АНЦ';
        const n = homeModel().filter(topMatch).length; S.net = '';
        return n > 0 && n < B.board['Дніпропетровська']; })());

  console.log('\n' + (fail ? '✗ ' : '✓ ') + pass + ' pass · ' + fail + ' fail');
  process.exit(fail ? 1 : 0);
}
