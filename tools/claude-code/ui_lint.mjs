// живе доки: агент Claude Code будує інтерфейси (HTML/CSS, PWA, Mini App) для Konst. Дім — lens-governance:tools/claude-code/ (бриф §HOOK-2.5, «так» Konst 10.10.2026).
// ui_lint — машинна частина огляду UI: те, що видно програмі, ловить програма, а не Konst («капсула прилипла», «текст обрізаний», «іконка вище»).
// Очі агента лишаються: машина бачить ~третину вад (розвідка 10.10: axe/WCAG-огляди), решта — чек-лист воріт ui-review-gate.
//
// Запуск:  node ui_lint.mjs <url|файл.html> [--state "<js>"]… [--repo <тека>] [--width 390] [--json]
//          кожен --state — окремий стан (JS виконується на сторінці; між станами сторінка перезавантажується); без --state — лише початковий.
//          Обидві теми (prefers-color-scheme light/dark) завжди. --repo: ✗ 0 → позначка для воріт (той самий хеш диффу, що в ui-review-gate).
//          <repo>/.ui-lint-accept — відомі вади, прийняті Konst: рядок «вид | шматок адреси елемента | причина · дата» → ⓘ (не блокує, але друкується щоразу).
//          node ui_lint.mjs selftest — зуби: сторінка з підкинутими вадами (кожна мусить дати свій рядок) і чиста (0).
// Вивід: ✗ (ворота не пустять) · ⚠ (подивись очима) · ⓘ (не виміряно); exit 1 на ✗.
// Пороги: контраст 4,5:1 (великий текст 3:1) — WCAG 2.x AA · ціль тапу 24 px ✗ (WCAG 2.2 2.5.8) / 44 px ⚠ (Apple HIG) · поле вводу < 16 px — iOS Safari збільшує сторінку ·
// текст < 11 px ⚠ (HIG) · прилипання < 2 px до краю картки — наш поріг (QR CC-5 «капсула», CC-6 бейдж). Джерела й дати — бриф §HOOK-2.5.
import { execFileSync } from 'node:child_process';
import { writeFileSync, mkdtempSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const PW = ['/opt/node-tools/node_modules/playwright/index.mjs', 'playwright'];
async function pw() { for (const p of PW) { try { return await import(p); } catch {} } throw new Error('Playwright не знайдено'); }

// ── перевірки — виконуються В СТОРІНЦІ (жодних залежностей; лише DOM і getComputedStyle) ──
function probe() {
  const out = [], add = (lvl, kind, el, msg) => out.push({ lvl, kind, where: path(el), msg });
  const path = el => { if (!el || el === document.body) return 'body'; const id = el.id ? '#' + el.id : ''; const c = [...el.classList].slice(0, 2).map(x => '.' + x).join('');
    const t = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 28); return `${el.tagName.toLowerCase()}${id}${c}${t ? ` «${t}»` : ''}`; };
  const vis = el => { const s = getComputedStyle(el), r = el.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 0 && r.height > 0 && !el.closest('[hidden],[aria-hidden="true"]:not(.zv-bdg)'); };
  const rgba = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (m) { const v = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [v[0], v[1], v[2], v[3] ?? 1]; }
    const n = c.match(/color\(srgb ([^)]+)\)/); if (n) { const v = n[1].split(/[ /]+/).filter(Boolean).map(Number); return [v[0] * 255, v[1] * 255, v[2] * 255, v[3] ?? 1]; } return null; };
  const lum = ([r, g, b]) => { const f = x => { x /= 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const blend = (top, bot) => { const a = top[3]; return [top[0] * a + bot[0] * (1 - a), top[1] * a + bot[1] * (1 - a), top[2] * a + bot[2] * (1 - a), 1]; };
  // фон під елементом: знизу вгору до першого непрозорого; градієнт / картинка на шляху — «не виміряно» (чесно, без вигаданого числа)
  const bgOf = el => { const st = []; for (let e = el; e; e = e.parentElement) { const s = getComputedStyle(e); if (s.backgroundImage !== 'none') return null; const c = rgba(s.backgroundColor); if (c && c[3] > 0) { st.push(c); if (c[3] >= 0.99) break; } }
    let bg = [255, 255, 255, 1]; if (!st.length || st[st.length - 1][3] < 0.99) { const h = rgba(getComputedStyle(document.documentElement).backgroundColor); if (h && h[3] > 0) bg = h; }
    for (let i = st.length - 1; i >= 0; i--) bg = blend(st[i], bg); return bg; };
  const card = el => { for (let e = el.parentElement; e && e !== document.body; e = e.parentElement) { const s = getComputedStyle(e);
    if ((s.backgroundImage !== 'none' || (rgba(s.backgroundColor) || [0, 0, 0, 0])[3] > 0.05 || parseFloat(s.borderTopWidth) > 0 || s.boxShadow !== 'none') && parseFloat(s.borderTopLeftRadius) > 0) return e; } return null; };
  const W = innerWidth;
  // 1. горизонтальний скрол
  if (document.documentElement.scrollWidth > W + 1) add('✗', 'скрол', document.body, `сторінка ширша за екран: ${document.documentElement.scrollWidth} > ${W} px — скрол убік`);
  const all = [...document.querySelectorAll('body *')].filter(e => !e.closest('svg') || e.tagName.toLowerCase() === 'svg').filter(vis);   // нутрощі іконок SVG накладаються задумано
  for (const el of all) {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    // 2. обрізаний текст
    if (own && /hidden|clip/.test(s.overflowX + s.overflowY) && (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 2) && s.textOverflow !== 'ellipsis' && !s.webkitLineClamp?.match(/\d/))
      add('✗', 'обрізано', el, `текст не влазить (${el.scrollWidth}×${el.scrollHeight} у ${el.clientWidth}×${el.clientHeight}) — частину не видно`);
    if (own && s.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1) add('⚠', 'обрізано', el, 'текст скорочено «…» — це задумано? людина не побачить кінця');
    // 3. прилипання до краю картки / вилазить за картку: капсули, бейджі, кнопки — елементи з власним тлом чи рамкою
    const chip = ((rgba(s.backgroundColor) || [0, 0, 0, 0])[3] > 0.05 || parseFloat(s.borderTopWidth) > 0 || s.backgroundImage !== 'none') && parseFloat(s.borderTopLeftRadius) > 0;
    const c = chip && card(el);
    if (c && c !== el) { const q = c.getBoundingClientRect(), d = [r.top - q.top, q.right - r.right, q.bottom - r.bottom, r.left - q.left];
      const full = r.width >= q.width - 2;   // на всю ширину картки (рядок, смужка) — не капсула
      if (!full && d.some(x => x < -1) && getComputedStyle(c).overflow === 'visible') add('✗', 'вилазить', el, `виходить за межі «${path(c)}» на ${Math.round(-Math.min(...d))} px`);
      else if (!full && d.some(x => x >= -1 && x < 2) && !(r.height >= q.height - 2)) add('✗', 'прилипло', el, `майже торкається краю «${path(c)}» (${d.map(x => Math.round(x)).join('/')} px) — «приклеєна капсула»`); }
    // 4. контраст тексту
    if (own && el.textContent.trim().length > 1) { const fg = rgba(s.color), bg = bgOf(el), px = parseFloat(s.fontSize), big = px >= 24 || (px >= 18.66 && +s.fontWeight >= 700);
      if (fg && bg) { const f = fg[3] < 1 ? blend(fg, bg) : fg, a = lum(f), b = lum(bg), cr = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05), need = big ? 3 : 4.5;
        if (cr < need) add('✗', 'контраст', el, `контраст ${cr.toFixed(2)}:1 < ${need}:1 — погано читається`); }
      else if (fg) out.push({ lvl: 'ⓘ', kind: 'контраст', where: path(el), msg: 'фон — градієнт чи картинка: контраст не виміряно, глянь очима' });
      // 5. дрібний текст
      if (px < 11) add('⚠', 'шрифт', el, `текст ${px}px < 11 — на телефоні дрібно`); }
    // 6. цілі тапу; поле вводу < 16 px
    if (el.matches('a[href],button,[role=button],input:not([type=hidden]),select,textarea,summary')) {
      const lbl = (el.innerText || el.value || el.getAttribute('aria-label') || el.title || '').trim();
      if (r.width < 24 || r.height < 24) add('✗', 'тап', el, `ціль ${Math.round(r.width)}×${Math.round(r.height)} px < 24 — важко влучити (WCAG 2.2)`);
      else if (r.width < 44 || r.height < 44) add('⚠', 'тап', el, `ціль ${Math.round(r.width)}×${Math.round(r.height)} px < 44 (Apple)`);
      if (!lbl && !el.matches('input,select,textarea')) add('⚠', 'без назви', el, 'кнопка без тексту й без aria-label — що вона робить?');
      if (el.matches('input:not([type=checkbox]):not([type=radio]):not([type=file]),select,textarea') && parseFloat(s.fontSize) < 16) add('✗', 'iOS-зум', el, `поле ${s.fontSize} < 16px — iPhone збільшить сторінку при тапі й не поверне`); }
  }
  // 7. накладання елементів у потоці (сусіди одного батька)
  for (const p of new Set(all.map(e => e.parentElement))) { if (!p) continue;
    const kids = [...p.children].filter(k => all.includes(k) && !/absolute|fixed|sticky/.test(getComputedStyle(k).position) && getComputedStyle(k).display !== 'inline');
    for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) { const a = kids[i].getBoundingClientRect(), b = kids[j].getBoundingClientRect();
      const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left), iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ix > 2 && iy > 2) add('✗', 'накладання', kids[j], `налазить на «${path(kids[i])}» (${Math.round(ix)}×${Math.round(iy)} px)`); } }
  // 8. ряд нерівний: однакові сусіди (тег + класи) у рядку — різна висота або вміст на різній висоті; у стовпці — різна ширина
  for (const p of new Set(all.map(e => e.parentElement))) { if (!p) continue;
    const g = {}; for (const k of p.children) if (all.includes(k) && getComputedStyle(k).display !== 'inline') (g[k.tagName + '.' + [...k.classList].filter(x => !/old|on|act|sel|dis/.test(x)).sort().join('.')] ||= []).push(k);
    for (const ks of Object.values(g)) { if (ks.length < 2) continue; const R = ks.map(k => k.getBoundingClientRect());
      const row = R.every(x => Math.abs(x.top - R[0].top) < 4), col = R.every(x => Math.abs(x.left - R[0].left) < 4);
      if (row) { const hs = R.map(x => Math.round(x.height)); if (Math.max(...hs) - Math.min(...hs) > 1) add('⚠', 'ряд', ks[0], `однакові елементи в ряду різної висоти: ${hs.join('·')} px`);
        const tops = ks.map(k => { const f = k.firstElementChild; return f ? Math.round(f.getBoundingClientRect().top - k.getBoundingClientRect().top) : null; });
        if (tops.every(x => x != null) && Math.max(...tops) - Math.min(...tops) > 1) add('⚠', 'ряд', ks[0], `вміст у ряду на різній висоті (від верху ${tops.join('·')} px) — значки «стрибають»`); }
      else if (col) { const ws = R.map(x => Math.round(x.width)); if (Math.max(...ws) - Math.min(...ws) > 2) add('⚠', 'ряд', ks[0], `однакові елементи в стовпці різної ширини: ${ws.join('·')} px`); } } }
  // 9. текст для людини: сміття з коду — ✗; жаргон — ⚠
  const txt = document.body.innerText;
  for (const bad of ['undefined', 'NaN', '[object', 'null']) if (new RegExp(`(^|[^\\w])${bad.replace('[', '\\[')}($|[^\\w])`).test(txt)) add('✗', 'текст', document.body, `на екрані «${bad}» — дані не підставились`);
  const jar = (txt.match(/(^|[^а-яіїєґ\w])(репо|репозитор\w*|хеш\w*|sha\b|API|JSON|токен\w*|коміт\w*|PR #?\d*|blob)(?=$|[^а-яіїєґ\w])/giu) || []).map(x => x.trim());
  if (jar.length) add('⚠', 'текст', document.body, `технічні слова в тексті для людини: ${[...new Set(jar)].slice(0, 6).join(', ')} — простіше можна?`);
  return out;
}

const SELF = `<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>
body{margin:0;font:15px/1.4 sans-serif;background:#fff;color:#111}@media(prefers-color-scheme:dark){body{background:#111;color:#eee}}
.card{margin:16px;padding:14px;border-radius:14px;background:#f2f2f2;position:relative}@media(prefers-color-scheme:dark){.card{background:#222}}
.pill{display:inline-block;padding:2px 8px;border-radius:99px;background:#237770;color:#fff}.tl{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}.ic{width:30px;height:30px;border-radius:50%;background:#bbb}.row{display:flex;gap:8px}.tile{flex:1;border-radius:10px;background:#ddd;padding:8px}
.grey{color:#aaa}.clip{width:60px;overflow:hidden;white-space:nowrap}</style></head><body>
<div class=card id=ok><button style="min-height:48px;padding:0 16px">Завантажити KPI</button> <span class=pill>6 дн.</span></div>
${'BAD'}</body></html>`;
const DEFECTS = {
  'прилипло': `<div class=card><span class=pill style="position:absolute;top:1px;right:30px">прилипла</span>.</div>`,
  'обрізано': `<div class=card><div class=clip>Дуже довгий підпис</div></div>`,
  'контраст': `<div class=card><span class=grey>сірий на сірому</span></div>`,
  'тап': `<div class=card><button style="width:20px;height:20px;padding:0">x</button></div>`,
  'iOS-зум': `<div class=card><input value="пошук" style="font-size:14px;min-height:44px"></div>`,
  'скрол': `<div style="width:600px;height:4px"></div>`,
  'ряд': `<div class="card row"><div class="tile tl"><i class=ic></i>Сайт</div><div class="tile tl"><i class=ic></i>Історія</div><div class="tile tl"><i class=ic></i>KPI<br>6 дн.</div></div>`,   // вада QR CC-6: другий рядок підняв значок
  'текст': `<div class=card>Дані: undefined · хеш у репо</div>`,
};

async function lint(target, states, width, theme, browser) {
  const ctx = await browser.newContext({ viewport: { width, height: 844 }, deviceScaleFactor: 2, colorScheme: theme });
  const p = await ctx.newPage(), errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && !/Failed to load resource/.test(m.text()) && errs.push(m.text()));
  const res = [];
  for (const [i, st] of (states.length ? states : [null]).entries()) {
    await p.goto(target, { waitUntil: 'load' }); await p.waitForTimeout(400);
    if (st) { try { await p.evaluate(st); } catch (e) { res.push({ lvl: '✗', kind: 'стан', where: `стан ${i + 1}`, msg: 'JS стану впав: ' + e.message.split('\n')[0] }); } await p.waitForTimeout(700); }
    for (const f of await p.evaluate(probe)) res.push({ ...f, state: st ? `стан ${i + 1}` : 'початковий' });
  }
  for (const e of errs) res.push({ lvl: '✗', kind: 'JS', where: 'консоль', msg: e.slice(0, 160), state: '' });
  await ctx.close(); return res;
}

async function run(target, states, width) {
  const { chromium } = await pw(); const b = await chromium.launch();
  const out = {}; for (const t of ['light', 'dark']) out[t] = await lint(target, states, width, t, b);
  await b.close(); return out;
}

const here = dirname(fileURLToPath(import.meta.url));
const a = process.argv.slice(2);
if (a[0] === 'selftest') {
  const d = mkdtempSync(join(tmpdir(), 'uilint-')); let bad = 0;
  const page = (x, n) => { const f = join(d, n + '.html'); writeFileSync(f, SELF.replace('BAD', x)); return 'file://' + f; };
  const clean = await run(page('', 'clean'), [], 390); const cl = [...clean.light, ...clean.dark].filter(x => x.lvl !== 'ⓘ');
  console.log((cl.length ? '✗' : '✓') + ` чиста сторінка → тиша (${cl.length ? cl.map(x => x.kind + ': ' + x.msg).join(' | ') : '0'})`); bad += !!cl.length;
  for (const [k, html] of Object.entries(DEFECTS)) { const r = await run(page(html, k), [], 390); const hit = [...r.light, ...r.dark].some(x => x.kind === k && x.lvl !== 'ⓘ');
    console.log((hit ? '✓' : '✗') + ` підкинуто «${k}» → спіймано`); bad += !hit; }
  console.log(`─── ui_lint selftest: ${Object.keys(DEFECTS).length + 1 - bad}/${Object.keys(DEFECTS).length + 1} ───`); process.exit(bad ? 1 : 0);
}
if (!a[0]) { console.log('node ui_lint.mjs <url|файл> [--state "<js>"]… [--repo <тека>] [--width 390] [--json] | selftest'); process.exit(2); }
let target = a[0]; if (!/^\w+:\/\//.test(target)) target = 'file://' + resolve(target);
const states = [], opt = {}; for (let i = 1; i < a.length; i++) { if (a[i] === '--state') states.push(a[++i]); else if (a[i] === '--repo') opt.repo = a[++i]; else if (a[i] === '--width') opt.width = +a[++i]; else if (a[i] === '--json') opt.json = true; }
const r = await run(target, states, opt.width || 390);
const acc = []; const af = opt.repo && join(resolve(opt.repo), '.ui-lint-accept');
if (af && existsSync(af)) for (const l of (await import('node:fs')).readFileSync(af, 'utf8').split('\n')) { const [k, w, why] = l.split('|').map(x => (x || '').trim()); if (k && w && !k.startsWith('#')) acc.push({ k, w, why }); }
for (const t of ['light', 'dark']) for (const f of r[t]) { const m = acc.find(a => a.k === f.kind && f.where.includes(a.w)); if (m && f.lvl !== 'ⓘ') { f.msg += ` — прийнято: ${m.why}`; f.lvl = 'ⓘ'; f.acc = true; } }
if (opt.json) { console.log(JSON.stringify(r, null, 1)); }
let x = 0, w = 0;
for (const t of ['light', 'dark']) {
  const seen = new Set(); const rows = r[t].filter(f => { const k = f.lvl + f.kind + f.where + f.msg; if (seen.has(k)) return false; seen.add(k); return true; });
  x += rows.filter(f => f.lvl === '✗').length; w += rows.filter(f => f.lvl === '⚠').length;
  if (!opt.json) { console.log(`— ${t === 'light' ? 'світла' : 'темна'} тема`); for (const f of rows.filter(f => f.lvl !== 'ⓘ')) console.log(`  ${f.lvl} ${f.kind} · ${f.state || ''} · ${f.where} — ${f.msg}`);
    for (const f of rows.filter(f => f.acc)) console.log(`  ⓘ ${f.kind} · ${f.where} — ${f.msg}`);
    const n = rows.filter(f => f.lvl === 'ⓘ' && !f.acc).length; if (n) console.log(`  ⓘ не виміряно контраст на ${n} елементах (градієнт / картинка) — глянь очима`); }
}
console.log(`─── ui_lint: ✗ ${x} · ⚠ ${w} · станів ${states.length || 1} × 2 теми ───`);
if (opt.repo && !x) {   // позначка для воріт: той самий хеш диффу UI, що рахує ui-review-gate
  const hx = execFileSync('bash', [join(here, 'hooks/ui-review-gate.sh'), 'hash', resolve(opt.repo)], { encoding: 'utf8' }).trim();
  if (hx) { writeFileSync(`/tmp/lens-uilint-${hx}`, `${new Date().toISOString()} ✗0 ⚠${w} ${target} states=${states.length || 1}\n`); console.log(`✓ позначка ui_lint для диффу ${hx.slice(0, 8)} — ворота огляду приймуть done`); }
}
process.exit(x ? 1 : 0);
