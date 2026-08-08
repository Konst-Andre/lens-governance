/* живе доки: знак money не переглянуто вдруге (вузол C — амбер для оверстоку).
   StockCheck · матриця H1 — ЗНАК грошового бейджа.
   Запуск:  node StockCheck_h1_money_sign.js [шлях_до_html]
   jsdom НЕ потрібен: під тестом чисті функції + фейковий el.
   Код НЕ дублюється — витягується з живого білда за якорями (wsd 12.1).

   Контракт, який тримає ця матриця:
     оверсток (порахував > MSL)  →  s > 0  →  клас 'pos'  →  «+N грн»
     нестача  (порахував < MSL)  →  s < 0  →  клас 'neg'  →  «−N грн»
   Еталон семантики — .dchip картки, який рахує нестачу як «-N» з b27. */

const fs = require('fs'), path = require('path'), vm = require('vm');
const FILE = process.argv[2] || path.join(__dirname, 'StockCheck_port_b30.html');
const src = fs.readFileSync(FILE, 'utf8');

function grab(re, name) { const m = re.exec(src); if (!m) throw new Error('якір не знайдено: ' + name); return m[0]; }
const chunk = [
  grab(/function fmtMoney\(v\)\{[^\n]*\n/, 'fmtMoney'),
  grab(/function brandMoney\(bk,tier,data\)\{[\s\S]*?return \{s:s,any:any\};\}/, 'brandMoney'),
  grab(/function catMoney\(list,tier,data\)\{[^\n]*\n/, 'catMoney'),
  grab(/function normFor\(k,tier\)\{[^\n]*\n/, 'normFor'),
  grab(/function setMoney\(el,fam,m\)\{[\s\S]*?fmtMoney\(m\.s\);\}/, 'setMoney')
].join('\n');

/* стаби оточення — рівно те, що функції споживають */
const sandbox = {
  MSL_BY_K: { K1: { A: 4, B: 3, C: 2, D: 1 }, K2: { A: 8, B: 6, C: 4, D: 2 } },
  MONEY_PRICE: { K1: 100, K2: 50 },
  LAYOUT: { NUR: { subs: [{ rows: [{ k: 'K1' }, { k: 'K2' }] }] } },
  OTC_BRANDS: ['NUR'], IW_BRANDS: []
};
vm.createContext(sandbox);
vm.runInContext(chunk, sandbox);
const { fmtMoney, brandMoney, catMoney, setMoney } = sandbox;

let pass = 0, fail = 0;
const chk = (n, c) => { c ? (pass++, console.log('  ✓ ' + n)) : (fail++, console.log('  ✗ ' + n)); };

/* ярус C: K1 норма 2 (×100), K2 норма 4 (×50) */
const T = 'C';
const el = () => ({ className: '', textContent: '' });

console.log('\n— знак суми —');
const under = brandMoney('NUR', T, { K1: 0, K2: 4 });      /* K1 нестача 2 → −200 */
chk('нестача → s<0   (s=' + under.s + ')', under.s === -200);

const over = brandMoney('NUR', T, { K1: 5, K2: 4 });        /* K1 надлишок 3 → +300 */
chk('оверсток → s>0  (s=' + over.s + ')', over.s === 300);

const exact = brandMoney('NUR', T, { K1: 2, K2: 4 });
chk('рівно норма → s=0 (s=' + exact.s + ')', exact.s === 0);

const mixed = brandMoney('NUR', T, { K1: 5, K2: 0 });       /* +300 −200 */
chk('змішано → алгебраїчна сума (s=' + mixed.s + ')', mixed.s === 100);

console.log('\n— клас (варіант A: клас лишився на знаку) —');
let a = el(); setMoney(a, 'fb', under);
chk("нестача → 'neg' (" + a.className + ')', /\bneg\b/.test(a.className));
let b = el(); setMoney(b, 'fb', over);
chk("оверсток → 'pos' (" + b.className + ')', /\bpos\b/.test(b.className));

console.log('\n— текст —');
chk('нестача друкує «−» (' + fmtMoney(under.s) + ')', fmtMoney(under.s).indexOf('\u2212') === 0);
chk('оверсток друкує «+» (' + fmtMoney(over.s) + ')', fmtMoney(over.s).indexOf('+') === 0);

console.log('\n— не введене не рахується —');
const none = brandMoney('NUR', T, {});
chk('порожньо → any=false', none.any === false && none.s === 0);
let c = el(); setMoney(c, 'fb', none);
chk("порожньо → 'empty' (" + c.className + ')', /\bempty\b/.test(c.className) && c.textContent === '');

console.log('\n— агрегація категорії успадковує знак —');
chk('catMoney(OTC) = brandMoney', catMoney(['NUR'], T, { K1: 0, K2: 4 }).s === -200);

console.log('\n' + (fail ? '✗ ' : '✓ ') + `H1 money-sign: ${pass} pass, ${fail} fail\n`);
process.exit(fail ? 1 : 0);
