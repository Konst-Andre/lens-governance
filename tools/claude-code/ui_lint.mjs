// живе доки: агент Claude Code будує інтерфейси (HTML/CSS, PWA, Mini App) для Konst. Дім — lens-governance:tools/claude-code/ (бриф §HOOK-2.5, «так» Konst 10.10.2026).
// ui_lint — машинна частина огляду UI: те, що видно програмі, ловить програма, а не Konst («капсула прилипла», «текст обрізаний», «іконка вище»).
// Очі агента лишаються: машина бачить ~третину вад (розвідка 10.10: axe/WCAG-огляди), решта — чек-лист воріт ui-review-gate.
//
// Запуск:  node ui_lint.mjs <url|файл.html> [--state "<js>"]… [--scope <корінь острова>] [--repo <тека>] [--width 390] [--height 844] [--json] [--baseline <файл>]   (низький екран Safari: --width 375 --height 634)
//          кожен --state — окремий стан (JS виконується на сторінці; між станами сторінка перезавантажується); без --state — лише початковий.
//          --state — ВИРАЗ, не модуль: `await` верхнього рівня → ✗ «JS стану впав»; чекати — `new Promise(r=>setTimeout(()=>{…;r()},1800))` (QR CC-13, 15.10.2026: шіт відкривається з затримкою).
//          Обидві теми (prefers-color-scheme light/dark) завжди. --repo: ✗ 0 → позначка для воріт (той самий хеш диффу, що в ui-review-gate).
//          <repo>/.ui-lint-accept — відомі вади, прийняті Konst: рядок «вид | шматок адреси елемента | причина · дата» → ⓘ (не блокує, але друкується щоразу).
//          node ui_lint.mjs selftest — зуби: сторінка з підкинутими вадами (кожна мусить дати свій рядок) і чиста (0).
// Перевірки: 1 скрол убік · 2 обрізано · 3 прилипло / вилазить · 4 контраст (4-б — на градієнті пікселем знімка) · 5 шрифт · 6 тап, без назви, iOS-зум · 7 накладання · 8 ряд · 9 текст (сміття, жаргон) ·
// 10 дія в прокрутці · 11 кнопки ряду · 12 сирота · 13 злито · 14 однакові заголовки · 15 дата й час · 16 зливається (16-б край кнопки) · 17 паритет тем · 18 кромка · 19 картка-список · 20 вкладена прокрутка · 21 шапка в прокрутці · 22 емодзі в кнопці · 23 нативне вікно · 24 фон у рамці · 25 кант рветься · 26 поле губиться; поза probe — натискання (:active / JS pointerdown, touchstart).
// 31 форма виділення · 32 пунктир < 3:1 · 22 емодзі-значок без підпису → ✗ · 33 різнобій списків — AE S94, 20.10.2026.
// 27 плашка в тон тла · 28 панелі зливаються · 29 список-таблиця · 30 чуже правило (--scope <корінь острова>) — AE S93, 19.10.2026.
// Звідки кожна (пропуск Konst, QR CC-N, рецепт кукбуку) — коментар біля неї.
// Вивід: ✗ (ворота не пустять) · ⚠ (подивись очима) · ⓘ (не виміряно); exit 1 на ✗.
// Пороги: контраст 4,5:1 (великий текст 3:1) — WCAG 2.x AA · ціль тапу 24 px ✗ (WCAG 2.2 2.5.8) / 44 px ⚠ (Apple HIG) · поле вводу < 16 px — iOS Safari збільшує сторінку ·
// текст < 11 px ⚠ (HIG) · прилипання < 2 px до краю картки — наш поріг (QR CC-5 «капсула», CC-6 бейдж). Джерела й дати — бриф §HOOK-2.5.
import { execFileSync } from 'node:child_process';
import { writeFileSync, mkdtempSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { inflateSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';

const PW = ['/opt/node-tools/node_modules/playwright/index.mjs', 'playwright'];
async function pw() { for (const p of PW) { try { return await import(p); } catch {} } throw new Error('Playwright не знайдено'); }

// ── перевірки — виконуються В СТОРІНЦІ (жодних залежностей; лише DOM і getComputedStyle) ──
function probe() {
  const out = [], add = (lvl, kind, el, msg) => out.push({ lvl, kind, where: path(el), msg });
  const path = el => { if (!el || el === document.body) return 'body'; const id = el.id ? '#' + el.id : ''; const pc = !id && !el.classList.length && el.parentElement?.classList[0] ? '.' + el.parentElement.classList[0] + ' › ' : ''; const c = [...el.classList].slice(0, 2).map(x => '.' + x).join('');
    const t = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 28); return `${pc}${el.tagName.toLowerCase()}${id}${c}${t ? ` «${t}»` : ''}`; };
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
    if (own && el.textContent.trim().length > 1) { const fg = rgba(s.color), bg = bgOf(el), px = parseFloat(s.fontSize), big = px >= 24 || (px >= 18.66 && +s.fontWeight >= 700), need = big ? 3 : 4.5;
      if (fg && bg) { const f = fg[3] < 1 ? blend(fg, bg) : fg, a = lum(f), b = lum(bg), cr = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        if (cr < need) add('✗', 'контраст', el, `контраст ${cr.toFixed(2)}:1 < ${need}:1 — погано читається`); }
      else if (fg && !el.closest('[class*="brand"],[data-logo]')) { const cx = r.left + r.width / 2, cy = r.top + r.height / 2, hit = cx >= 0 && cy >= 0 && cx < innerWidth && cy < innerHeight && (t => t && (t === el || el.contains(t)))(document.elementFromPoint(cx, cy));
        // 4-б. фон — градієнт / картинка: міряє Node пікселем знімка (кільце довкола тексту); текст поза екраном чи під шаром — «не виміряно»; логотип (клас *brand*, data-logo) — виняток WCAG 1.4.3
        out.push({ lvl: hit ? 'px' : 'ⓘ', kind: 'контраст', where: path(el), msg: 'фон — градієнт чи картинка: контраст не виміряно, глянь очима', rect: [r.left, r.top, r.width, r.height], fg, need }); }
      // 5. дрібний текст
      if (px < 11) add('⚠', 'шрифт', el, `текст ${px}px < 11 — на телефоні дрібно`); }
    // 6. цілі тапу; поле вводу < 16 px
    if (el.matches('a[href],button,[role=button],input:not([type=hidden]),select,textarea,summary')) {
      const lbl = (el.innerText || el.value || el.getAttribute('aria-label') || el.title || '').trim();
      // ціль = площа, що ловить дотик (з розширенням ::before/::after — modern-css.com «larger touch targets», 19.10.2026): зонд elementFromPoint від центру
      // в обидва боки по кожній осі; коробку лише коли зонд не дістає (поза екраном, під шаром). Хибне QR 18.10: ✕ 25×25 з ::after 44 → «25 < 44».
      let tw = r.width, th = r.height;
      if (tw < 44 || th < 44) { const cx = r.left + r.width / 2, cy = r.top + r.height / 2, on = (x, y) => x >= 0 && y >= 0 && x < innerWidth && y < innerHeight && (t => t && (t === el || el.contains(t)))(document.elementFromPoint(x, y));
        if (on(cx, cy)) { const span = (dx, dy) => { let a = 0, b = 0; while (a < 40 && on(cx - dx * (a + 1), cy - dy * (a + 1))) a++; while (b < 40 && on(cx + dx * (b + 1), cy + dy * (b + 1))) b++; return a + b + 1; };
          tw = Math.max(tw, span(1, 0)); th = Math.max(th, span(0, 1)); } }
      if (tw < 24 || th < 24) add('✗', 'тап', el, `ціль ${Math.round(tw)}×${Math.round(th)} px < 24 — важко влучити (WCAG 2.2)`);
      else if (tw < 44 || th < 44) add('⚠', 'тап', el, `ціль ${Math.round(tw)}×${Math.round(th)} px < 44 (Apple)`);
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
  // 10. дія в прокрутці (QR CC-7, пропуск Konst: у високому шіті «Закрити» ховалась під краєм прокрутки): остання кнопка прокручуваного блока — дія —
  //     видна повністю без прокрутки, інакше закріпити кнопки поза прокруткою. Рядок списку (≥ 3 однакових сусідів) — не судимо: обрізаний край списку — норма.
  for (const sc of [...document.querySelectorAll('body *')].filter(e => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 2 && vis(e))) {
    // дія шіта = широка кнопка (≥ 60 % ширини блока), найнижча на екрані — не «остання в коді» (CSS order міняє порядок) і не кнопка рядка вмісту (кошик у картці)
    const q = sc.getBoundingClientRect(), bs = [...sc.querySelectorAll('button, a[href], [role=button]')].filter(vis).filter(b => b.getBoundingClientRect().width >= q.width * 0.6);
    const last = bs.sort((x, y) => y.getBoundingClientRect().bottom - x.getBoundingClientRect().bottom)[0]; if (!last) continue;
    let inList = false; for (let e = last; e && e !== sc; e = e.parentElement) { const p = e.parentElement; if (p && [...p.children].filter(c => c.className === e.className && c.tagName === e.tagName).length >= 3) { inList = true; break; } }
    const r = last.getBoundingClientRect();
    if (!inList && r.bottom > q.bottom + 1) add('✗', 'дія в прокрутці', last, `кнопку дії видно не повністю без прокрутки (${Math.max(0, Math.round(q.bottom - r.top))} з ${Math.round(r.height)} px) — закріпити кнопки поза прокруткою (кукбук A108)`);
  }
  // 11. кнопки одного ряду різної висоти (QR CC-7, пропуск Konst: «Ще раз» 34 px ⟂ кошик 44 px): сусідні кнопки рядка flex — одна висота або одне тіло (перемикач)
  for (const row of [...document.querySelectorAll('body *')].filter(e => /flex/.test(getComputedStyle(e).display) && !/column/.test(getComputedStyle(e).flexDirection) && vis(e))) {
    const ks = [...row.children].filter(c => vis(c) && c.matches('button, a[href], [role=button]')); if (ks.length < 2) continue;
    const hs = ks.map(k => Math.round(k.getBoundingClientRect().height));
    if (Math.max(...hs) - Math.min(...hs) > 4) add('⚠', 'кнопки ряду', ks[0], `кнопки в одному ряду різної висоти: ${hs.join('·')} px — одна висота або одне тіло (перемикач)`);
  }
  // 12–14 (QR CC-8, пропуск Konst: «Історія» — «текст у підвалі читається злитно»): рядок тексту, який людина не розбирає з одного погляду
  const inl = el => [...el.children].every(c => /inline|contents/.test(getComputedStyle(c).display) && !/inline-(block|flex|grid)/.test(getComputedStyle(c).display));
  const seen = new Set(), once = (lvl, kind, el, msg) => { const k = kind + path(el); if (!seen.has(k)) { seen.add(k); add(lvl, kind, el, msg); } };
  for (const el of all) {
    if (!el.childNodes.length || !inl(el) || !el.textContent.trim() || el.matches('svg, svg *')) continue;
    const s = getComputedStyle(el), px = parseFloat(s.fontSize);
    // 12. сирота: останній рядок — 1–2 знаки («збірка 26 / с») — розрив усередині шматка, що мав бути цілим
    const rg = document.createRange(); rg.selectNodeContents(el); const lines = {};
    for (const q of rg.getClientRects()) if (q.width > 0) { const k = Math.round(q.top / 3); lines[k] = (lines[k] || 0) + q.width; }
    const ks = Object.keys(lines).map(Number).sort((x, y) => x - y);
    if (ks.length >= 2 && lines[ks[ks.length - 1]] < px * 1.6) once('⚠', 'сирота', el, `останній рядок — ${Math.round(lines[ks[ks.length - 1]])} px (1–2 знаки) — розрив усередині шматка; тримати цілим (white-space: nowrap / нерозривний пробіл)`);
    // 13. злитий підпис: дата/час і ще ≥ 2 різні речі через «·» в одному рядку — око не відділяє «коли» від «що» й «стан» (стан — значком, що — заголовком)
    const seg = el.innerText.split('·').map(x => x.trim()).filter(Boolean), dt = x => /^[\d.:\s]+$/.test(x) && /\d{1,2}[.:]\d{2}/.test(x);
    if (seg.length >= 3 && seg.some(x => /\d{1,2}[.:]\d{2}/.test(x)) && seg.filter(x => !dt(x)).length >= 2) once('⚠', 'злито', el, `в одному рядку дата і ще ${seg.filter(x => !dt(x)).length} різні речі через «·» («${el.innerText.trim().slice(0, 40)}») — один рядок — одна річ`);
  }
  // 15. дата й час злиплись (QR CC-8, пропуск Konst: «09.10 18:53» — однієї ваги поруч, «де дата, а де час»): в одному текстовому вузлі «дд.мм гг:хх»
  for (const el of all) for (const n of el.childNodes) if (n.nodeType === 3 && /(^|[^\d])\d{1,2}\.\d{2}(\.\d{2,4})?\s+\d{1,2}:\d{2}(?!\d)/.test(n.textContent))
    once('⚠', 'дата й час', el, `дата й час одним шматком однакової ваги («${n.textContent.trim().slice(0, 24)}») — день словом або підзаголовком, час окремо`);
  // 16. верхній край картки зливається з тлом (QR CC-8, пропуск Konst: шапка картки в шіті світлої теми «розчиняється»): тон краю ≈ тло, рамка ледь видна,
  //     і нема ні широкої мʼякої тіні (blur ≥ 14 — A66, світла), ні світла зверху (inset, темна) — краю нічим триматись. Градієнт на краю — «не виміряно».
  const layers = sh => sh === 'none' ? [] : sh.split(/,(?![^(]*\))/).map(x => { const c = rgba(x) || [0, 0, 0, 0], nums = (x.replace(/rgba?\([^)]*\)|color\([^)]*\)/, '').match(/-?[\d.]+px/g) || []).map(parseFloat); return { inset: /inset/.test(x), a: c[3], y: nums[1] || 0, blur: nums[2] || 0 }; });
  const cr = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  // фон як bgOf, але однотонний градієнт (усі точки однакові — «шар кольору», як у карток QR) читається кольором, а не «картинкою»
  const flatBg = el => { const st = []; for (let e = el; e; e = e.parentElement) { const s = getComputedStyle(e);   // стек згори вниз: шар градієнта над кольором фону
      if (s.backgroundImage !== 'none') { const cs = (s.backgroundImage.match(/rgba?\([^)]*\)|color\([^)]*\)/g) || []).map(rgba); if (!/^linear-gradient/.test(s.backgroundImage) || !cs.length || cs.some(x => !x || x.join() !== cs[0].join())) return null; if (cs[0][3] > 0) st.push(cs[0]); }
      const c = rgba(s.backgroundColor); if (c && c[3] > 0) { st.push(c); if (c[3] >= 0.99) break; } }
    let bg = [255, 255, 255, 1]; if (!st.length || st[st.length - 1][3] < 0.99) { const h = rgba(getComputedStyle(document.documentElement).backgroundColor); if (h && h[3] > 0) bg = h; }
    for (let i = st.length - 1; i >= 0; i--) bg = blend(st[i], bg); return bg; };
  for (const c of all) { const s = getComputedStyle(c); if (parseFloat(s.borderTopLeftRadius) < 6) continue;
    const own = (rgba(s.backgroundColor) || [0, 0, 0, 0])[3] > 0.05 || s.backgroundImage !== 'none'; if (!own) continue;
    const r = c.getBoundingClientRect(); if (r.width < 120 || r.height < 40 || r.top < 0 || r.top > innerHeight - 10) continue;
    const ground = c.parentElement && flatBg(c.parentElement); if (!ground) continue;
    const at = document.elementsFromPoint(r.left + r.width / 2, r.top + 2).find(e => c.contains(e) && ((rgba(getComputedStyle(e).backgroundColor) || [0, 0, 0, 0])[3] > 0.05 || getComputedStyle(e).backgroundImage !== 'none')) || c;
    const edge = flatBg(at); if (!edge) continue;   // справжній градієнт на краю — свідомий хід, не судимо
    const bc = rgba(s.borderTopColor) || [0, 0, 0, 0], bw = parseFloat(s.borderTopWidth) || 0, bline = bw > 0 && bc[3] > 0 ? cr(blend(bc, ground), ground) : 1;
    const L = layers(s.boxShadow), halo = L.some(l => !l.inset && l.blur >= 14 && l.a >= 0.05), lit = L.some(l => l.inset && l.y > 0 && l.a >= 0.06);
    if (cr(edge, ground) < 1.06 && bline < 1.2 && !halo && !lit) add('⚠', 'зливається', c, `верхній край майже кольору тла (${cr(edge, ground).toFixed(2)}:1), рамка ${bline.toFixed(2)}:1, нема широкої тіні чи світла зверху — краю нічим триматись (A66: світла — blur ≥ 14, темна — inset зверху; не жирна рамка)`); }
  // 16-б. край кнопки (QR CC-13, пропуск Konst 15.10: «Ні», «Закрити», «Змінити» на шіті — «ледь видно, де кнопка закінчується», обидві теми): кнопка майже кольору
  //     підкладки (верх і низ градієнта), а лінії краю нема (рамка чи кант-кільце `0 0 0 .5px` ≥ 1.15:1). Широка мʼяка тінь картку тримає (A66), кнопку — ні: окреслює лише низ.
  //     Поріг — не 3:1 WCAG 1.4.11 (там край обовʼязковий, лише коли він єдина ознака кнопки; у нас є текст), а «легкий кант» Konst (не жирна рамка) — тому ⚠, не ✗.
  const stops = s => { const m = (s.backgroundImage.match(/rgba?\([^)]*\)|color\([^)]*\)/g) || []).map(rgba).filter(Boolean); const c = rgba(s.backgroundColor) || [0, 0, 0, 0]; return m.length ? m : c[3] > 0.05 ? [c] : []; };
  for (const b of all) { if (!b.matches('button,[role=button],a[href]')) continue; const s = getComputedStyle(b), r = b.getBoundingClientRect();
    if (r.width < 24 || r.height < 24 || r.top < 0 || r.bottom > innerHeight || s.visibility === 'hidden' || parseFloat(s.opacity) < 0.5) continue;
    const st = stops(s); if (!st.length || st.some(x => x[3] < 0.9)) continue;   // прозора чи напівпрозора — це не тіло
    const ground = b.parentElement && flatBg(b.parentElement); if (!ground) continue;
    const fill = Math.min(...[st[0], st[st.length - 1]].map(x => cr(blend(x, ground), ground)));
    const bw = parseFloat(s.borderTopWidth) || 0, bc = rgba(s.borderTopColor) || [0, 0, 0, 0], border = bw > 0 && bc[3] > 0 ? cr(blend(bc, ground), ground) : 1;
    const ring = s.boxShadow === 'none' ? 1 : Math.max(1, ...s.boxShadow.split(/,(?![^(]*\))/).filter(x => !/inset/.test(x)).map(x => { const c = rgba(x), n = (x.replace(/rgba?\([^)]*\)|color\([^)]*\)/, '').match(/-?[\d.]+px/g) || []).map(parseFloat); return c && (n[2] || 0) === 0 && (n[3] || 0) > 0 ? cr(blend(c, ground), ground) : 1; }));
    if (fill < 1.08 && Math.max(border, ring) < 1.15) add('⚠', 'край кнопки', b, `кнопка майже кольору підкладки (${fill.toFixed(2)}:1), лінії краю нема (рамка/кант ${Math.max(border, ring).toFixed(2)}:1) — тінь окреслює лише низ; кант 0,5 px + тінь, як у ✕ (A66)`); }
  // 17 (збір). обʼєм поверхні — для паритету тем (QR CC-8, пропуск Konst: «покращили світлу — темна відстала»): градієнт (не однотонний), широка мʼяка тінь, світло зверху
  for (const el of all) { const s = getComputedStyle(el), r = el.getBoundingClientRect(); if (r.width < 120 || r.height < 24) continue;
    const own = (rgba(s.backgroundColor) || [0, 0, 0, 0])[3] > 0.05 || s.backgroundImage !== 'none'; if (!own) continue;
    const cs = (s.backgroundImage.match(/rgba?\([^)]*\)|color\([^)]*\)/g) || []).map(rgba), grad = /gradient/.test(s.backgroundImage) && cs.length > 1 && cs.some(x => x && cs[0] && x.join() !== cs[0].join());
    const L = layers(s.boxShadow), v = [grad && 'градієнт', L.some(l => !l.inset && l.blur >= 14 && l.a >= 0.03) && 'тінь', L.some(l => l.inset && l.y !== 0 && l.a >= 0.06) && 'вставка'].filter(Boolean);   // вставка: світло зверху (темна) чи западина (світла) — обидва прийоми обʼєму (A65/A66); широка тінь навіть ледь помітна — свідомий обʼєм
    out.push({ lvl: 'vol', kind: 'обʼєм', where: path(el), msg: v.join('+') }); }
  // 18. кромка прокрутки (A109, QR CC-8): блок прокрутки в шіті (предок position: fixed), вміст ховається ≥ 40 px, маски нема — людина не бачить, що нижче ще є
  for (const sc of all.filter(e => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 40)) {
    let fx = false; for (let e = sc.parentElement; e; e = e.parentElement) if (getComputedStyle(e).position === 'fixed') { fx = true; break; }
    const m = getComputedStyle(sc).maskImage || getComputedStyle(sc).webkitMaskImage || 'none';
    if (fx && m === 'none') add('⚠', 'кромка', sc, `прокрутка в шіті без кромки: схована частина ${sc.scrollHeight - sc.clientHeight} px, маски нема — підказати «нижче ще є» (кукбук A109)`); }
  // 22. емодзі в кнопці (пропуск Konst QR CC-12, 14.10.2026: «▶ рух» на iPhone став кольоровою картинкою-емодзі серед SVG-іконок): символ з Extended_Pictographic у тексті кнопки чи посилання
  for (const el of all.filter(e => /^(BUTTON|A)$/.test(e.tagName) || e.getAttribute('role') === 'button')) { const t = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('');
    const m = t.match(/\p{Extended_Pictographic}/u); if (!m) continue;
    // AE S94 (пропуск Konst: «☀» перемикача рейки — емодзі замість SVG; ⚠ було, агент пройшов повз): значок без підпису — ✗; емодзі поруч зі словом — ⚠
    const only = !el.innerText.replace(/[\p{Extended_Pictographic}\uFE0F\u200D\s\p{P}]/gu, '').trim();
    add(only ? '✗' : '⚠', 'емодзі', el, `символ «${m[0]}» у кнопці${only ? ' — єдиний її вміст (значок без підпису)' : ''} — iOS малює його кольоровою картинкою, не в мові іконок; іконка — SVG (currentColor)`); }
  // 24. фон у рамці (пропуск Konst QR CC-15, 16.10.2026: «бліда смуга знизу» кнопки в темній): градієнт фону з початком від внутрішнього краю (background-origin: padding-box,
  //     типово) і повтором малюється й під рамкою (background-clip: border-box) → у прозорій чи напівпрозорій рамці знизу видно смужку ВЕРХУ градієнта (MDN background-origin, 16.10.2026)
  for (const el of all) { const s = getComputedStyle(el); if (!/gradient/.test(s.backgroundImage) || s.backgroundOrigin !== 'padding-box' || !/(^|\s)repeat/.test(s.backgroundRepeat) || s.backgroundClip !== 'border-box') continue;
    const st = stops(s); if (st.length < 2) continue; const [g0, g1] = [st[0], st[st.length - 1]].map(x => blend(x, [128, 128, 128, 1]));
    // видимість, не механізм (хибне на шапці QR CC-15: верх і низ градієнта шапки різняться на 1–2 рівні — під рамкою не видно): під верхньою рамкою мав би бути верх, а лягає низ, і навпаки
    const side = ['Top', 'Bottom'].find(k => { const c = rgba(s['border' + k + 'Color']) || [0, 0, 0, 0]; return parseFloat(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none' && c[3] < 0.99 && cr(blend(c, g0), blend(c, g1)) > 1.05; });
    if (side) add('✗', 'фон у рамці', el, `фон-градієнт повторюється під прозорою рамкою (${side === 'Top' ? 'згори' : 'знизу'}) — смужка протилежного краю градієнта; фон \`<градієнт> border-box no-repeat\``); }
  // 25. кант рветься (пропуск Konst QR CC-15, 16.10.2026: «коло, обрізане знизу»): різні кольори сусідніх сторін рамки на круглому куті сходяться по діагоналі (так малює WebKit —
  //     w3.org/TR/css-borders-4; webkit different-color-borders) → кант «обривається». Світло згори й кромка знизу — тінями, що йдуть по дузі: inset 0 1px 0 · 0 1px 0
  for (const el of all) { const s = getComputedStyle(el); if (!(parseFloat(s.borderTopLeftRadius) > 2 || parseFloat(s.borderBottomRightRadius) > 2)) continue;
    const sd = ['Top', 'Right', 'Bottom', 'Left'].map(k => parseFloat(s['border' + k + 'Width']) > 0 && s['border' + k + 'Style'] !== 'none' ? rgba(s['border' + k + 'Color']) : null);
    const g = [255, 255, 255, 1], k = [0, 0, 0, 1], seen = c => c && c[3] > 0.04 ? c : null;
    const torn = [0, 1, 2, 3].some(i => { const a = sd[i], b = sd[(i + 1) % 4]; if (!a || !b || !(seen(a) || seen(b))) return false;
      return Math.max(cr(blend(a, g), blend(b, g)), cr(blend(a, k), blend(b, k))) > 1.25; });
    if (torn) add('⚠', 'кант рветься', el, 'різні кольори сторін рамки на круглому куті — шов по діагоналі, кант «обривається»; світло згори / кромка знизу — box-shadow (inset 0 1px 0 · 0 1px 0)'); }
  // 26. поле губиться (пропуск Konst QR CC-15, 17.10.2026: поле пошуку й GUID без кільця в темній — «верхній край ледь помітний, розчиняється з тлом»):
  //     поле вводу (контейнер з input / textarea) — і тон, і рамка до ґрунту < 1.2:1 → межі поля не видно. Поріг — вирок Konst: 1,13 губиться, 1,37 тримається.
  for (const el of all) { if (!el.querySelector(':scope > input:not([type=hidden]), :scope > textarea')) continue; const s = getComputedStyle(el), r = el.getBoundingClientRect(); if (r.width < 80) continue;
    const ground = el.parentElement && flatBg(el.parentElement); if (!ground) continue;
    const bgc = rgba(s.backgroundColor) || [0, 0, 0, 0]; if (bgc[3] < 0.05 && s.backgroundImage === 'none') continue;   // голе поле без тіла — не наш випадок
    const fill = blend(bgc, ground), bc = rgba(s.borderTopColor) || [0, 0, 0, 0], bw = parseFloat(s.borderTopWidth) || 0;
    const top = bw > 0 && s.borderTopStyle !== 'none' ? cr(blend(bc, fill), ground) : 1, tone = cr(fill, ground);
    if (Math.max(top, tone) < 1.2) add('⚠', 'поле губиться', el, `межа поля до тла: тон ${tone.toFixed(2)}:1, верхній край ${top.toFixed(2)}:1 — поле розчиняється (поріг 1,2 — вирок Konst QR CC-15); тихе кільце 1 px (~1,35) або тон світліше`); }
  // 21. шапка в прокрутці (A108 п.1; пропуск Konst QR CC-12, 14.10.2026: у колег більше мереж — шіт фільтрів гортався ВЕСЬ, шапка з ✕ їхала геть, протяг показував тло):
  //     прокрутка в нерухомому шарі (предок або сама position: fixed), серед перших трьох її дітей — шапка (header / h1–h3 / клас head|title) з кнопкою, не sticky
  for (const sc of all.filter(e => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 40)) {
    let fx = false; for (let e = sc; e; e = e.parentElement) if (getComputedStyle(e).position === 'fixed') { fx = true; break; }
    const hd = [...sc.children].slice(0, 3).find(k => (/^(HEADER|H1|H2|H3)$/.test(k.tagName) || /head|title/i.test(k.className)) && k.querySelector('button') && getComputedStyle(k).position !== 'sticky');
    if (fx && hd) add('✗', 'шапка в прокрутці', hd, `шапка шіта гортається разом із вмістом (сховано ${sc.scrollHeight - sc.clientHeight} px) — рама стоїть, гортається лише середина: flex-колонка, шапка й кнопки flex:none, середина flex:1; min-height:0; overflow-y:auto; overscroll-behavior:contain (кукбук A108 п.1)`); }
  // 19. картка-список у шіті (A109 «картка зі своєю прокруткою», пропуск Konst QR CC-11: Київ 10 людей розтягнув картку на 582 px — «Сповіщення» під нею недосяжні):
  //     картка (радіус + тло) у прокрутці шіта, ≥ 6 однакових рядків, вища за половину видимої прокрутки, власної прокрутки нема
  for (const c of all.filter(e => { const s = getComputedStyle(e); return parseFloat(s.borderTopLeftRadius) > 0 && ((rgba(s.backgroundColor) || [0, 0, 0, 0])[3] > 0.05 || s.backgroundImage !== 'none'); })) {
    let sc = null, fx = false; for (let e = c.parentElement; e; e = e.parentElement) { const s = getComputedStyle(e); if (!sc && /auto|scroll/.test(s.overflowY) && e.scrollHeight > e.clientHeight) sc = e; if (s.position === 'fixed') { fx = true; break; } }
    if (!fx || !sc) continue;
    const host = c.children.length === 1 ? c.firstElementChild : c, g = {};
    for (const k of host.children) { const key = k.tagName + '.' + [...k.classList].filter(x => !/^(sel|on|active|pressing|open)$/.test(x)).join('.'); (g[key] ||= []).push(k); }
    const n = Math.max(0, ...Object.values(g).map(x => x.length)), own = /auto|scroll/.test(getComputedStyle(host).overflowY) && host.scrollHeight > host.clientHeight + 2, h = c.getBoundingClientRect().height;
    if (n >= 6 && !own && h > sc.clientHeight * 0.5) add('⚠', 'картка-список', c, `список у картці шіта: ${n} рядків, ${Math.round(h)} px > половини прокрутки (${sc.clientHeight} px) — дай картці свою прокрутку з кромкою (кукбук A109 «картка зі своєю прокруткою»)`); }
  // 20. вкладена прокрутка без overscroll-behavior: contain (A109, QR CC-11): доїхав до краю картки — жест перескакує на шіт
  for (const sc of all.filter(e => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 8)) {
    let outer = false; for (let e = sc.parentElement; e; e = e.parentElement) if (/auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 8) { outer = true; break; }
    if (outer && !/contain|none/.test(getComputedStyle(sc).overscrollBehaviorY)) add('⚠', 'вкладена прокрутка', sc, 'прокрутка всередині прокрутки без overscroll-behavior: contain — доїхав до краю, і жест перескакує на зовнішню (кукбук A109)'); }
  // 14. однакові заголовки рядків: ≥ 3 сусіди-рядки з тим самим першим жирним текстом — різниця схована в сірому підписі
  for (const p of new Set(all.map(e => e.parentElement))) { if (!p) continue;
    const g = {}; for (const k of p.children) if (all.includes(k)) { const h = k.querySelector('b, strong, h1, h2, h3, h4'); if (h && h.textContent.trim()) (g[k.tagName + '.' + k.className + '|' + h.textContent.trim()] ||= []).push(k); }
    for (const [key, ks] of Object.entries(g)) if (ks.length >= 3) add('⚠', 'однакові заголовки', ks[0], `${ks.length} рядки з однаковим заголовком «${key.split('|')[1].slice(0, 30)}» — у заголовок те, чим рядки відрізняються`); }
  // ── міра відтінку: CIELAB (D65). Яскравість WCAG тону не бачить: жовте на кремовому 1,06:1 ⟂ на білому 1,07:1 — однаково, а око бачить різне (AE S93, ΔE 16,6 ⟂ 20,7)
  const lab = ([r, g, b]) => { const f = x => { x /= 255; return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }; const R = f(r), G = f(g), B = f(b);
    const X = (0.4124 * R + 0.3576 * G + 0.1805 * B) / 0.95047, Y = 0.2126 * R + 0.7152 * G + 0.0722 * B, Z = (0.0193 * R + 0.1192 * G + 0.9505 * B) / 1.08883;
    const t = v => v > 0.008856 ? Math.cbrt(v) : 7.787 * v + 16 / 116; return [116 * t(Y) - 16, 500 * (t(X) - t(Y)), 200 * (t(Y) - t(Z))]; };
  const chroma = l => Math.hypot(l[1], l[2]), hueOf = l => (Math.atan2(l[2], l[1]) * 180 / Math.PI + 360) % 360, dE = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
  // 27. плашка в тон тла (пропуск Konst AE S93, 19.10.2026: жовтий рядок товару на кремовому тлі «змазується по кольорах, по мітці», на білій картці — виділявся):
  //     бліда кольорова заливка (хрома ≥ 8, ΔE до ґрунту 3–25) на ґрунті ТОГО САМОГО відтінку (хрома ґрунту ≥ 2,5, тон ближче 35°) — мітка кольором не працює. Кольорова мітка — на нейтральному ґрунті
  //     (біла / сіра поверхня), або плашка іншого тону. Сама плашка без власної різниці з ґрунтом (ΔE < 3) — не плашка, пропуск.
  { const seen = new Set();
    for (const el of all) { const s = getComputedStyle(el), c = rgba(s.backgroundColor); if (!c || c[3] < 0.3 || s.backgroundImage !== 'none') continue;
      const r = el.getBoundingClientRect(); if (r.width < 60 || r.height < 20 || r.height > 120) continue;   // > 120 px — поверхня, не плашка: тон одного відтінку різної глибини — задумана ієрархія (M3 surface container)
      const ground = el.parentElement && flatBg(el.parentElement); if (!ground) continue;
      const fl = lab(blend(c, ground)), gl = lab(ground), fc = chroma(fl), gc = chroma(gl); const de = dE(fl, gl); if (fc < 8 || gc < 2.5 || de < 3 || de >= 25) continue;   // ΔE ≥ 25 — насичена плашка (жовта кнопка на кремі ~70) видна й так; біда — бліда (рядок 16,6)
      const dh = Math.abs(hueOf(fl) - hueOf(gl)), d = Math.min(dh, 360 - dh); if (d >= 35) continue;
      const key = el.tagName + '.' + [...el.classList].sort().join('.'); if (seen.has(key)) continue; seen.add(key);
      add('⚠', 'плашка в тон тла', el, `заливка (хрома ${fc.toFixed(0)}) на ґрунті того самого відтінку (хрома ${gc.toFixed(1)}, тон ближче ${d.toFixed(0)}°) — мітка кольором змазується; поклади на нейтральну поверхню (біла картка) або зміни тон плашки`); } }
  // 28. панелі зливаються (пропуск Konst AE S93: рейка меню й список сценаріїв — одне тло, межа лише рискою; «все пласке, наче 2D»): дві сусідні високі панелі (≥ 50 % висоти вікна) впритул,
  //     тло однакове (ΔE < 2), тіні нема — ієрархію тримає лише лінія. Поверхні розводять тоном (Material 3 surface container: тло → контейнер → вищий контейнер) чи тінню, не рискою.
  { const tall = all.filter(e => { const r = e.getBoundingClientRect(); return r.height >= innerHeight * 0.5 && r.width >= 56 && r.width < innerWidth * 0.6; }), seen = new Set();
    for (const a of tall) for (const b of tall) { if (a === b || a.contains(b) || b.contains(a)) continue; const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
      if (Math.abs(rb.left - ra.right) > 2 || Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top) < innerHeight * 0.4) continue;
      const fa = flatBg(a), fb = flatBg(b); if (!fa || !fb) continue; const d = dE(lab(fa), lab(fb)); if (d >= 2) continue;
      if (getComputedStyle(a).boxShadow !== 'none' || getComputedStyle(b).boxShadow !== 'none') continue;
      const k = Math.round(ra.right); if (seen.has(k)) continue; seen.add(k);
      add('⚠', 'панелі зливаються', a, `панель праворуч (${path(b)}) того самого тла (ΔE ${d.toFixed(1)}), тіні нема — межу тримає лише риска; дай поверхням різний тон чи тінь`); } }
  // 29. список-таблиця (пропуск Konst AE S93: «купа рисок… щоб це не була наче таблиця»): ≥ 6 рядків одного батька, ≥ 80 % з нижньою лінією на всю ширину — список вибору читається
  //     як таблиця. Для списку — лінія з відступом від тексту (inset) або проміжок + підсвітка рядка; суцільні лінії — для справжньої таблиці.
  for (const p of new Set(all.map(e => e.parentElement))) { if (!p || p.tagName === 'TBODY' || p.tagName === 'TABLE') continue; const kids = [...p.children].filter(k => all.includes(k)); if (kids.length < 6) continue;
    const pw = p.getBoundingClientRect().width, lined = kids.filter(k => { const s = getComputedStyle(k); return parseFloat(s.borderBottomWidth) >= 1 && s.borderBottomStyle !== 'none' && (rgba(s.borderBottomColor) || [0, 0, 0, 0])[3] > 0.1 && k.getBoundingClientRect().width >= pw - 2; });
    if (lined.length >= 6 && lined.length >= kids.length * 0.8) add('⚠', 'список-таблиця', p, `${lined.length} рядків з лінією на всю ширину — список читається як таблиця; лінія з відступом від тексту (inset) або проміжок і підсвітка рядка`); }
  // 31. форма виділення (пропуск Konst AE S94, 20.10.2026: капсула активного пункту рейки — «зліва прямий край, справа скруглений»): вибраний елемент
  //     (aria-current · aria-selected · клас active / on / selected) з різними радіусами кутів (одні ≈ 0, інші > 4), а смужки збоку, під яку така форма робилась, нема →
  //     обрубана капсула. Форма виділення — симетрична (Material 3 rail: індикатор — окрема форма за значком; developer.android.com NavigationRailView, 20.10.2026).
  for (const el of all) { if (!el.matches('[aria-current]:not([aria-current=false]),[aria-selected=true],.active,.on,.selected,.is-active')) continue;
    const s = getComputedStyle(el), rad = ['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft'].map(k => parseFloat(s['border' + k + 'Radius']) || 0);
    if (!(Math.max(...rad) > 4 && Math.min(...rad) < 1)) continue;
    const side = ['Left', 'Right'].some(k => parseFloat(s['border' + k + 'Width']) >= 2 && s['border' + k + 'Style'] !== 'none' && (rgba(s['border' + k + 'Color']) || [0, 0, 0, 0])[3] > 0.1);
    const pseudo = ['::before', '::after'].some(ps => { const q = getComputedStyle(el, ps); return q.content !== 'none' && q.display !== 'none' && parseFloat(q.width) <= 4 && (rgba(q.backgroundColor) || [0, 0, 0, 0])[3] > 0.1; });
    if (!side && !pseudo) add('⚠', 'форма виділення', el, `радіуси кутів ${rad.join(' ')} — одні прямі, інші круглі, а смужки збоку нема: виділення читається обрубаним; симетрична форма (однакові радіуси)`); }
  // 32. пунктир (пропуск Konst AE S94, 20.10.2026: «+ Додати» поруч з категоріями — «штрих-пунктир ледь помітний»): керуючий елемент з пунктирною
  //     чи крапковою межею, яка до тла < 3:1 — межа тут і є ознака керуючого (WCAG 1.4.11 «non-text contrast», w3.org/WAI/WCAG21/Understanding/non-text-contrast, 20.10.2026)
  for (const el of all) { if (!el.matches('button,select,a[href],input,textarea,[role=button]')) continue; const s = getComputedStyle(el);
    const k = ['Top', 'Right', 'Bottom', 'Left'].find(x => /dashed|dotted/.test(s['border' + x + 'Style']) && parseFloat(s['border' + x + 'Width']) > 0); if (!k) continue;
    const ground = el.parentElement && flatBg(el.parentElement); if (!ground) continue;
    const c = rgba(s['border' + k + 'Color']) || [0, 0, 0, 0], ratio = cr(blend(c, ground), ground);
    if (ratio < 3) add('✗', 'пунктир', el, `пунктирна межа керуючого ${ratio.toFixed(2)}:1 до тла (< 3:1) — ледь видно, що тут дія; темніший пунктир або суцільна межа`); }
  // 33. різнобій списків (пропуск агента AE S94, 20.10.2026 — Konst: «ти зробив власні випадайки для характеру й груп, а для “Додати” — ні; я ж не буду перечисляти всі пункти»):
  //     видимі select екрана з різним appearance (base-select ⟂ none ⟂ auto) — однорідне виглядає по-різному; меншість — ⚠. Рецепт — кукбук A117.
  { const sel = all.filter(e => e.tagName === 'SELECT' && e.getBoundingClientRect().width > 0), g = {};
    for (const e of sel) (g[getComputedStyle(e).appearance] ||= []).push(e);
    const ks = Object.keys(g).sort((a, b) => g[b].length - g[a].length);
    if (ks.length > 1) for (const k of ks.slice(1)) for (const e of g[k]) add('⚠', 'різнобій списків', e, `${g[k].length} з ${sel.length} списків екрана мають інший вигляд (appearance: ${k} ⟂ ${ks[0]} у решти) — однорідне має виглядати однаково (кукбук A117)`); }
  // 9. текст для людини: сміття з коду — ✗; жаргон — ⚠
  const txt = document.body.innerText;
  for (const bad of ['undefined', 'NaN', '[object', 'null']) if (new RegExp(`(^|[^\\w])${bad.replace('[', '\\[')}($|[^\\w])`).test(txt)) add('✗', 'текст', document.body, `на екрані «${bad}» — дані не підставились`);
  const jar = (txt.match(/(^|[^а-яіїєґ\w])(репо|репозитор\w*|хеш\w*|sha\b|API|JSON|токен\w*|коміт\w*|PR #?\d*|blob)(?=$|[^а-яіїєґ\w])/giu) || []).map(x => x.trim());
  if (jar.length) add('⚠', 'текст', document.body, `технічні слова в тексті для людини: ${[...new Set(jar)].slice(0, 6).join(', ')} — простіше можна?`);
  return out;
}

// 30. чуже правило (лише з --scope <селектор кореня острова>; пропуск Konst AE S93: прес, червона пляма, список на 11 рядків, поля по боках — одна причина: правила тренажера
//     з тими самими іменами класів доходили до редактора-острова). @scope / префікс не рятують ЗОВНІ ВСЕРЕДИНУ (глобальне правило однаково досягає — blog.openreplay.com
//     «native css scope», 2026), тому — замір: правило, чий селектор не згадує корінь острова, але влучає в його елементи й ставить коробку (відступи, розмір, рамка, прокрутка,
//     положення, курсор, трансформація, тло). Базові скидання (лише теги / *) — пропуск. ⚠ — ліки: префікс у чужого правила (його екран) або перекриття в острові.
function leaks(scope) {
  const roots = [...document.querySelectorAll(scope)]; if (!roots.length) return [{ lvl: '⚠', kind: 'чуже правило', where: scope, msg: `корінь острова «${scope}» не знайдено — перевірку витоків не виміряно` }];
  const els = roots.flatMap(r => [r, ...r.querySelectorAll('*')]), tok = scope.replace(/^[.#]/, ''), out = [], seen = new Set();
  const BOX = /^(padding|margin|width|height|min-|max-|border(?!-collapse)|overflow|position|top|right|bottom|left|inset|display|transform|cursor|background|box-shadow|grid|flex|gap|z-index|outline)/;
  const walk = list => { for (const r of list) { if (r.cssRules && !r.selectorText) { walk(r.cssRules); continue; } if (!r.selectorText || r.selectorText.includes(tok)) continue;
    const props = [...r.style].filter(x => BOX.test(x)); if (!props.length) continue;
    for (const sel of r.selectorText.split(',').map(x => x.trim())) { if (!/[.#\[]/.test(sel.replace(/:[a-z-]+(\([^)]*\))?/g, ''))) continue;   // лише теги / * — скидання
      let n = 0; try { n = els.filter(e => e.matches(sel)).length; } catch { continue; } if (!n || seen.has(sel)) continue; seen.add(sel);
      out.push({ lvl: '⚠', kind: 'чуже правило', where: sel, msg: `правило поза «${scope}» влучає в ${n} ел. острова: ${[...new Set(props.map(x => x.replace(/-(top|right|bottom|left|block|inline).*$/, '')))].slice(0, 5).join(', ')} — префікс у чужого правила або перекриття в острові` }); } } };
  for (const sh of document.styleSheets) { let rs; try { rs = sh.cssRules; } catch { continue; } walk(rs); }
  return out;
}
let SCOPE = '';   // --scope

const SELF = `<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>
body{margin:0;font:15px/1.4 sans-serif;background:#fff;color:#111}@media(prefers-color-scheme:dark){body{background:#111;color:#eee}}
.card{margin:16px;padding:14px;border-radius:14px;background:#f2f2f2;position:relative}@media(prefers-color-scheme:dark){.card{background:#222}}
.pill{display:inline-block;padding:2px 8px;border-radius:99px;background:#237770;color:#fff}.tl{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}.ic{width:30px;height:30px;border-radius:50%;background:#bbb}.row{display:flex;gap:8px}.tile{flex:1;border-radius:10px;background:#ddd;padding:8px}
.x44{position:relative;width:26px;height:26px;padding:0}.x44::after{content:'';position:absolute;inset:-12px}.grey{color:#aaa}.clip{width:60px;overflow:hidden;white-space:nowrap}button:active{transform:scale(.97)}.jsp{color:inherit}.jsp.pressing{transform:scale(.9)}</style><script>document.addEventListener('touchstart',()=>{},{passive:true});document.addEventListener('pointerdown',e=>{const c=e.target.closest('.jsp');if(c)c.classList.add('pressing')});document.addEventListener('pointercancel',()=>document.querySelectorAll('.pressing').forEach(x=>x.classList.remove('pressing')))</script></head><body>
<div class=card id=ok><button class=x44 aria-label="Закрити">✕</button> <button style="min-height:48px;padding:0 16px">Завантажити KPI</button> <span class=pill>6 дн.</span> <a class=jsp href="#j" style="display:inline-block;padding:14px 18px">Відкрити (A67)</a></div>
<div class=card><div style="height:96px;overflow-y:auto">${[1, 2, 3, 4].map(i => `<div class=li style="padding:4px 0">Рядок ${i} <button style="min-height:44px">Повернути</button></div>`).join('')}</div></div>
${'BAD'}</body></html>`;
const DEFECTS = {
  'прилипло': `<div class=card><span class=pill style="position:absolute;top:1px;right:30px">прилипла</span>.</div>`,
  'обрізано': `<div class=card><div class=clip>Дуже довгий підпис</div></div>`,
  'контраст': `<div class=card><span class=grey>сірий на сірому</span></div>`,
  'контраст ': `<div style="margin:16px;padding:14px;border-radius:14px;background:linear-gradient(180deg,#f6f6f6,#e9e9e9)"><span style="color:#b0b0b0">сірий на градієнті</span></div>`,   // 4-б: пікселем (QR CC-17)
  'тап': `<div class=card><button style="width:20px;height:20px;padding:0">x</button></div>`,
  'iOS-зум': `<div class=card><input value="пошук" style="font-size:14px;min-height:44px"></div>`,
  'скрол': `<div style="width:600px;height:4px"></div>`,
  'ряд': `<div class="card row"><div class="tile tl"><i class=ic></i>Сайт</div><div class="tile tl"><i class=ic></i>Історія</div><div class="tile tl"><i class=ic></i>KPI<br>6 дн.</div></div>`,   // вада QR CC-6: другий рядок підняв значок
  'текст': `<div class=card>Дані: undefined · хеш у репо</div>`,
  'дія в прокрутці': `<div class=card><div style="height:110px;overflow-y:auto"><p style="height:160px;margin:0">Довгий текст шіта</p><button style="min-height:48px;width:100%">Закрити</button></div></div>`,   // QR CC-7: кнопки шіта в прокрутці
  'дія в прокрутці ': `<div class=card><div style="height:120px;overflow-y:auto"><p style="height:150px;margin:0">Текст</p><div style="display:flex;flex-direction:column"><button style="min-height:48px;width:100%">Закрити</button><button style="min-height:48px;width:100%;order:-1">Скопіювати</button></div></div></div>`,   // QR CC-7: CSS order — дія візуально нижче, ніж у коді
  'кнопки ряду': `<div class=card style="display:flex;gap:8px;align-items:center"><button style="height:34px;padding:0 14px">Ще раз</button><button style="height:44px;width:44px" aria-label="Прибрати">x</button></div>`,   // QR CC-7: «Ще раз» ⟂ кошик
  'сирота': `<div class=card><div style="width:126px;font:15px monospace">збірка-0000026 с</div></div>`,   // QR CC-8: «збірка 26 / с» на 375 px
  'злито': `<div class=card><small>10.10 22:46 · оновлення адмінки · успішно</small></div>`,   // QR CC-8: «Історія» — дата · чому · стан в одній сірій смузі
  'однакові заголовки': `<div class=card>${[1, 2, 3].map(i => `<div class=hr><b>Бот зібрав дані</b><br><small>10.10 1${i}:00</small></div>`).join('')}</div>`,   // QR CC-8: шість «Бот зібрав дані»
  'кромка': `<div style="position:fixed;left:0;right:0;bottom:0;height:200px;background:#fff"><div style="height:180px;overflow-y:auto">${Array.from({length:12},(_, i)=>`<p style="margin:0;padding:10px">Рядок ${i}</p>`).join('')}</div></div>`,   // QR CC-8: шіт із прокруткою без кромки
  'картка-список': `<div style="position:fixed;left:0;right:0;bottom:0;height:300px;background:#fff"><div style="height:280px;overflow-y:auto;-webkit-mask-image:linear-gradient(#000 90%,transparent);mask-image:linear-gradient(#000 90%,transparent)"><div style="margin:8px;border-radius:14px;background:#f2f2f2">${Array.from({length:8},(_, i)=>`<div class=r style="padding:12px">Людина ${i}</div>`).join('')}</div><p style="height:200px;margin:0">Про застосунок</p></div></div>`,   // QR CC-11: Київ 10 людей
  'вкладена прокрутка': `<div style="position:fixed;left:0;right:0;bottom:0;height:240px;background:#fff"><div style="height:220px;overflow-y:auto;-webkit-mask-image:linear-gradient(#000 90%,transparent);mask-image:linear-gradient(#000 90%,transparent)"><div style="height:120px;overflow-y:auto;-webkit-mask-image:linear-gradient(#000 80%,transparent);mask-image:linear-gradient(#000 80%,transparent)"><p style="height:300px;margin:0">Список</p></div><p style="height:300px;margin:0">Решта шіта</p></div></div>`,   // QR CC-11: картка в шіті без contain
  'шапка в прокрутці': `<div style="position:fixed;left:0;right:0;bottom:0;height:220px;overflow-y:auto;background:#fff"><div class=sh-head style="display:flex;justify-content:space-between;padding:12px"><b>Фільтр аптек</b><button style="width:44px;height:44px">✕</button></div>${Array.from({length:12},(_, i)=>`<p style="margin:0;padding:10px">Мережа ${i}</p>`).join('')}</div>`,   // QR CC-12: шіт гортався з шапкою
  'емодзі': `<div class=card><button style="min-height:44px;padding:0 14px">▶ рух</button></div>`,   // QR CC-12: «▶» став емодзі на iPhone
  'нативне вікно': `<div class=card>.</div><script>setTimeout(() => prompt('Твій підпис'), 50)</script>`,   // QR CC-12: «свій підпис» → prompt
  'паритет тем': `<style>.ph{border-radius:14px;padding:14px;background:linear-gradient(180deg,#fff,#e3ebe9)}@media(prefers-color-scheme:dark){.ph{background:#232a35}}</style><div class=card><div class=ph>Шапка</div></div>`,   // QR CC-8: шапка обʼємна у світлій, пласка в темній
  'дата й час': `<div class=card><small>09.10 18:53 · QR Admin</small></div>`,   // QR CC-8: «Історія»
  'зливається': `<div style="background:#eef3f2;padding:16px"><div style="border-radius:16px;background:#fff;border:1px solid rgba(211,222,219,.4);box-shadow:0 3px 8px rgba(0,0,0,.06)"><div style="background:rgba(227,235,233,.6);padding:12px">На сайті</div><div style="padding:12px">рядок</div></div></div>`,   // QR CC-8: шапка картки в шіті світлої теми
  'край кнопки': `<div style="background:#fff;padding:16px"><button style="height:48px;width:160px;border:0;border-radius:14px;background:linear-gradient(180deg,#fff,#f0f0f0);box-shadow:0 1px 2px rgba(20,40,35,.06),0 4px 14px rgba(20,40,35,.09)">Ні</button></div>`,   // QR CC-13: «Ні» в підтвердженні пульта
  'фон у рамці': `<div class=card><button style="min-height:48px;width:160px;border:1px solid transparent;border-radius:14px;background:linear-gradient(180deg,#fff,#555)">Закрити</button></div>`,   // QR CC-15: бліда смуга знизу
  'кант рветься': `<div class=card><button style="min-height:48px;width:160px;border:1px solid;border-color:rgba(255,255,255,.5) rgba(255,255,255,.2) #000;border-radius:14px;background:#888">Закрити</button></div>`,   // QR CC-15: «коло, обрізане знизу»
  'поле губиться': `<div style="background:#0a0e14;padding:16px"><div style="background:#161c25;border:1px solid transparent;border-radius:10px;padding:8px"><input style="background:none;border:0;font-size:16px;color:#ccc;min-height:44px" value="пошук"></div></div>`,   // QR CC-15: поле без кільця на майже чорному
  'натискання': `<div class=card><a href="#x" style="display:inline-block;padding:14px 18px">Відкрити звіт</a></div>`,
  'плашка в тон тла': `<div style="background:#FFFEF6;padding:16px"><div style="background:#FFF8D0;padding:10px;width:220px">Нурофен форте №12</div></div>`,   // AE S93: жовтий рядок на кремовому
  'панелі зливаються': `<div style="display:flex;height:100vh"><nav style="width:72px;background:#fff;border-right:1px solid #e7e7e7"></nav><section style="width:200px;background:#fff">Сценарії</section></div>`,   // AE S93: рейка й список
  'список-таблиця': `<div class=card><div>${Array.from({length: 7}, (_, i) => `<div style="padding:10px 0;border-bottom:1px solid #ccc">Сценарій ${i}</div>`).join('')}</div></div>`,   // AE S93: «купа рисок»
  'форма виділення': `<div class=card><a href="#x" class=active style="display:inline-block;padding:10px 16px;background:#ffe241;border-radius:0 10px 10px 0">Сценарії</a></div>`,   // AE S94: капсула 0 8 8 0
  'пунктир': `<div class=card><button style="min-height:44px;padding:0 16px;border:1px dashed #e7e7e7;background:transparent;border-radius:999px;color:#00658f">+ Додати</button></div>`,   // AE S94: пунктир 1,2:1
  'різнобій списків': `<div class=card><select><option>А</option></select> <select><option>Б</option></select> <select style="appearance:none;-webkit-appearance:none;border:1px solid #999;padding:8px">
<option>+ Додати</option></select></div>`,   // AE S94: 3 з 7 списків на base-select, решта — ні
  'емодзі ': `<div class=card><button aria-label="Рейка" style="min-width:44px;min-height:44px">☀</button></div>`,   // AE S94: значок-емодзі без підпису → ✗
  'чуже правило': `<style>.err{padding:10px 14px;border:1px solid #c00}</style><div class=isl><span class="dot err" style="display:inline-block;width:8px;height:8px;background:#c00"></span></div>`,   // AE S93: .err тренажера → крапка редактора; selftest з --scope .isl
};

// 4-б. контраст на градієнті — пікселем (пропуск Konst QR CC-17, 18.10.2026: підвал героблока 2,55 / 2,97, а ui_lint писав «не виміряно»;
//     axe-core теж лишає такі випадки на ручну перевірку — docs.deque.com devtools-color-contrast-resolver, 18.10.2026).
//     Знімок екрана ×2 (PNG 8 біт, без чергування) → фон = медіана пікселів кільця на 2 px довкола рамки тексту;
//     кільце строкате (менше 60 % пікселів у межах 40 від медіани — картинка, сусідній предмет) → «не виміряно», як і раніше.
function png(buf) {
  let o = 8, w = 0, h = 0, ct = 0; const idat = [];
  while (o < buf.length) { const n = buf.readUInt32BE(o), t = buf.toString('ascii', o + 4, o + 8), d = buf.subarray(o + 8, o + 8 + n);
    if (t === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; } else if (t === 'IDAT') idat.push(d); else if (t === 'IEND') break; o += 12 + n; }
  const bpp = ct === 6 ? 4 : 3, raw = inflateSync(Buffer.concat(idat)), stride = w * bpp, px = Buffer.alloc(h * stride);
  for (let y = 0; y < h; y++) { const f = raw[y * (stride + 1)], src = y * (stride + 1) + 1, dst = y * stride;
    for (let x = 0; x < stride; x++) { const a = x >= bpp ? px[dst + x - bpp] : 0, b = y ? px[dst - stride + x] : 0, c = x >= bpp && y ? px[dst - stride + x - bpp] : 0, v = raw[src + x];
      const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
      px[dst + x] = (f === 0 ? v : f === 1 ? v + a : f === 2 ? v + b : f === 3 ? v + ((a + b) >> 1) : v + (pa <= pb && pa <= pc ? a : pb <= pc ? b : c)) & 255; } }
  return { w, h, bpp, px };
}
function ringContrast(img, f) {
  const [x, y, w, h] = f.rect.map(v => Math.round(v * 2)), pts = [];   // знімок ×2 (deviceScaleFactor контексту)
  const at = (X, Y) => { if (X < 0 || Y < 0 || X >= img.w || Y >= img.h) return; const i = (Y * img.w + X) * img.bpp; pts.push([img.px[i], img.px[i + 1], img.px[i + 2]]); };
  for (let X = x - 4; X <= x + w + 4; X += 2) { at(X, y - 4); at(X, y + h + 4); }
  for (let Y = y - 4; Y <= y + h + 4; Y += 2) { at(x - 4, Y); at(x + w + 4, Y); }
  if (pts.length < 8) return null;
  const med = c => { const v = pts.map(p => p[c]).sort((a, b) => a - b); return v[v.length >> 1]; }, bg = [med(0), med(1), med(2)];
  if (pts.filter(p => Math.max(...p.map((v, c) => Math.abs(v - bg[c]))) <= 40).length < pts.length * 0.6) return null;   // строкате кільце — чесно не міряємо
  const L = ([r, g, b]) => { const q = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * q(r) + 0.7152 * q(g) + 0.0722 * q(b); };
  const a = f.fg[3] ?? 1, t = [0, 1, 2].map(c => f.fg[c] * a + bg[c] * (1 - a)), A = L(t), B = L(bg);
  return (Math.max(A, B) + 0.05) / (Math.min(A, B) + 0.05);
}

async function lint(target, states, width, theme, browser) {
  const ctx = await browser.newContext({ viewport: { width, height: HEIGHT }, deviceScaleFactor: 2, colorScheme: theme });
  const p = await ctx.newPage(), errs = [], dlg = []; p.on('pageerror', e => errs.push(e.message)); p.on('dialog', d => { dlg.push(d.type() + ': ' + d.message()); d.dismiss().catch(() => {}); });   // 23. нативне вікно (пропуск Konst QR CC-12: «свій підпис» відкрив prompt браузера) p.on('console', m => m.type() === 'error' && !/Failed to load resource/.test(m.text()) && errs.push(m.text()));
  const res = [];
  for (const [i, st] of [null, ...states].entries()) {   // початковий екран — завжди, далі кожен стан
    await p.goto(target, { waitUntil: 'load' }); await p.waitForTimeout(400);
    if (st) { try { await p.evaluate(st); } catch (e) { res.push({ lvl: '✗', kind: 'стан', where: `стан ${i}`, msg: 'JS стану впав: ' + e.message.split('\n')[0] }); } await p.waitForTimeout(700); }
    const found = await p.evaluate(probe), pxs = found.filter(f => f.lvl === 'px');
    if (pxs.length) { const img = png(await p.screenshot({ type: 'png' })); for (const f of pxs) { const m = ringContrast(img, f); if (m == null) { f.lvl = 'ⓘ'; continue; }
      // допуск 0,15 — похибка кільця (згладжування, сусідні пікселі): ✗ лише явно нижче порогу, «на межі» — ⚠ (замір QR CC-17: 4,33–4,39 на межі, 4,07 і 2,52 — вади)
      if (m < f.need - 0.15) { f.lvl = '✗'; f.msg = `контраст ${m.toFixed(2)}:1 < ${f.need}:1 — погано читається (фон — градієнт, заміряно пікселем)`; }
      else if (m < f.need) { f.lvl = '⚠'; f.msg = `контраст ${m.toFixed(2)}:1 — на межі ${f.need}:1 (фон — градієнт, пікселем ± 0,15) — глянь очима`; } else f.lvl = 'ok'; } }
    for (const f of found.filter(f => f.lvl !== 'ok')) { delete f.rect; delete f.fg; delete f.need; res.push({ ...f, state: st ? `стан ${i}` : 'початковий' }); }
    if (SCOPE) for (const f of await p.evaluate(leaks, SCOPE)) res.push({ ...f, state: st ? `стан ${i}` : 'початковий' });   // 30. чуже правило
    // натискання: притиснути, виміряти, відпустити ПОЗА елементом (клік не спрацює). Однаковий вигляд → ⚠ «нема відгуку» (Konst 10.10: анімація пресу)
    const sig = await p.evaluate(() => { const seen = new Set(), out = [];
      for (const e of document.querySelectorAll('a[href],button,[role=button],summary,label[for]')) { const s = getComputedStyle(e); if (s.display === 'none' || !e.getClientRects().length) continue; e.scrollIntoView({ block: 'center', behavior: 'instant' }); const r = e.getBoundingClientRect();
        if (!r.width || !r.height || s.visibility === 'hidden' || e.disabled || e.closest('[hidden]')) continue;
        const k = e.tagName + '.' + [...e.classList].sort().join('.'); if (seen.has(k)) continue;
        // досяжна пальцем: у центрі — саме вона (не під шаром, не в закритому шіті); інакше беремо наступну таку саму
        const c = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (!c || !(c === e || e.contains(c))) continue;
        seen.add(k); e.dataset.uilPress = out.length; out.push(k); }
      return out; });
    // вмикаємо :active примусово (DevTools CSS.forcePseudoState) — без кліків: справжнє натискання мишею закривало шіт (тап «по фону») і псувало решту вимірів
    const cdp = await p.context().newCDPSession(p); await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
    const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
    for (let j = 0; j < Math.min(sig.length, 40); j++) {
      const el = p.locator(`[data-uil-press="${j}"]`);
      // вигляд = сама кнопка + її підкладка ::before + перший вкладений елемент (стиск часто на них: квадратик галочки, капсула в полі); колір тексту — ні: браузер сам фарбує посилання на :active
      const look = () => el.evaluate(e => [getComputedStyle(e), getComputedStyle(e, '::before'), e.firstElementChild && getComputedStyle(e.firstElementChild)].filter(Boolean).map(s => [s.transform, s.backgroundColor, s.boxShadow, s.opacity, s.filter].join('|')).join('#'));
      let nodeId; try { ({ nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: `[data-uil-press="${j}"]` })); } catch { continue; }
      if (!nodeId) continue;
      const before = await look();
      await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: ['active'] }); await p.waitForTimeout(400);   // довше за будь-який перехід відгуку
      const css = await look();
      await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: [] }); await p.waitForTimeout(350);
      // і JS-натискання (кукбук A67: клас .pressing на pointerdown) — синтетична подія без кліку
      await el.evaluate(e => e.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerType: 'touch', isPrimary: true }))); await p.waitForTimeout(200);
      const js = await look();
      await el.evaluate(e => e.dispatchEvent(new PointerEvent('pointercancel', { bubbles: true, pointerType: 'touch', isPrimary: true }))); await p.waitForTimeout(350);
      if (before === css && before === js) res.push({ lvl: '⚠', kind: 'натискання', where: sig[j].toLowerCase(), msg: 'на натискання вигляд не змінюється (ні :active, ні JS pointerdown) — палець не відчуває кнопку; рецепт — кукбук A67', state: st ? `стан ${i}` : 'початковий' });
    }
    await cdp.detach();
    if (i === 0 && !(await p.evaluate(() => /touchstart/.test([...document.scripts].map(x => x.textContent).join(' ')) || document.body.hasAttribute('ontouchstart'))))
      res.push({ lvl: '⚠', kind: 'натискання', where: 'сторінка', msg: 'нема слухача touchstart — у Safari iOS :active на дотик не спрацює (додай document.addEventListener(\'touchstart\', () => {}, { passive: true }))', state: '' });
  }
  for (const e of errs) res.push({ lvl: '✗', kind: 'JS', where: 'консоль', msg: e.slice(0, 160), state: '' });
  for (const e of [...new Set(dlg)]) res.push({ lvl: '✗', kind: 'нативне вікно', where: 'сторінка', msg: `${e.slice(0, 80)} — вікно браузера (prompt / alert / confirm) посеред застосунку: поле чи шіт у мові продукту`, state: '' });
  await ctx.close(); return res;
}

async function run(target, states, width) {
  const { chromium } = await pw(); const b = await chromium.launch();
  const out = {}; for (const t of ['light', 'dark']) out[t] = await lint(target, states, width, t, b);
  await b.close();
  // 17. паритет тем: та сама поверхня має обʼєм в одній темі й пласка в іншій (інструмент може різнитись — A66: світла тінь, темна світло зверху)
  const V = t => Object.fromEntries(out[t].filter(f => f.lvl === 'vol').map(f => [f.state + '|' + f.where, f.msg]));
  const L = V('light'), D = V('dark'), seen = new Set();
  for (const k of Object.keys(L)) if (k in D && !!L[k] !== !!D[k]) { const [st, where] = k.split('|'); const key = where.replace(/ «.*$/, ''); if (seen.has(key)) continue; seen.add(key);
    out.light.push({ lvl: '⚠', kind: 'паритет тем', where, state: st, msg: L[k] ? `обʼєм лише у світлій (${L[k]}), у темній плоско — підтягни темну (A66: світло зверху + мʼяка тінь)` : `обʼєм лише в темній (${D[k]}), у світлій плоско — підтягни світлу (A66: широка мʼяка тінь)` }); }
  for (const t of ['light', 'dark']) out[t] = out[t].filter(f => f.lvl !== 'vol');
  return out;
}

const here = dirname(fileURLToPath(import.meta.url));
let HEIGHT = 844;   // --height: Safari з панеллю ≈ 634 на 375 px (QR CC-7: шіт влазив у 844, а на телефоні — ні)
const a = process.argv.slice(2);
if (a[0] === 'selftest') {
  const d = mkdtempSync(join(tmpdir(), 'uilint-')); let bad = 0;
  const page = (x, n) => { const f = join(d, n + '.html'); writeFileSync(f, SELF.replace('BAD', x)); return 'file://' + f; };
  const clean = await run(page('', 'clean'), [], 390); const cl = [...clean.light, ...clean.dark].filter(x => x.lvl !== 'ⓘ');
  console.log((cl.length ? '✗' : '✓') + ` чиста сторінка → тиша (${cl.length ? cl.map(x => x.kind + ': ' + x.msg).join(' | ') : '0'})`); bad += !!cl.length;
  for (const [k, html] of Object.entries(DEFECTS)) { SCOPE = k === 'чуже правило' ? '.isl' : ''; const r = await run(page(html, k), [], 390); const hit = [...r.light, ...r.dark].some(x => x.kind === k.trim() && x.lvl !== 'ⓘ');
    console.log((hit ? '✓' : '✗') + ` підкинуто «${k}» → спіймано`); bad += !hit; }
  console.log(`─── ui_lint selftest: ${Object.keys(DEFECTS).length + 1 - bad}/${Object.keys(DEFECTS).length + 1} ───`); process.exit(bad ? 1 : 0);
}
if (!a[0]) { console.log('node ui_lint.mjs <url|файл> [--state "<js>"]… [--repo <тека>] [--width 390] [--height 844] [--json] | selftest'); process.exit(2); }
let target = a[0]; if (!/^\w+:\/\//.test(target)) target = 'file://' + resolve(target);
const states = [], opt = {}; for (let i = 1; i < a.length; i++) { if (a[i] === '--state') states.push(a[++i]); else if (a[i] === '--repo') opt.repo = a[++i]; else if (a[i] === '--width') opt.width = +a[++i]; else if (a[i] === '--height') HEIGHT = +a[++i]; else if (a[i] === '--scope') SCOPE = a[++i]; else if (a[i] === '--json') opt.json = true; else if (a[i] === '--baseline') opt.base = a[++i]; }
const r = await run(target, states, opt.width || 390);
const acc = []; const af = opt.repo && join(resolve(opt.repo), '.ui-lint-accept');
if (af && existsSync(af)) for (const l of (await import('node:fs')).readFileSync(af, 'utf8').split('\n')) { const [k, w, why] = l.split('|').map(x => (x || '').trim()); if (k && w && !k.startsWith('#')) acc.push({ k, w, why }); }
for (const t of ['light', 'dark']) for (const f of r[t]) { const m = acc.find(a => a.k === f.kind && f.where.includes(a.w)); if (m && f.lvl !== 'ⓘ') { f.msg += ` — прийнято: ${m.why}`; f.lvl = 'ⓘ'; f.acc = true; } }
if (opt.json) { console.log(JSON.stringify(r, null, 1)); }
// --baseline <файл>: база відомих ✗ (Android Lint · SwiftLint --use-baseline; ключ — вид + елемент, не рядок: вставка рядків вище не робить старе «новим» —
// claudeissues 82589, 07.2026). Файлу нема → записати поточні ✗ і вийти; є → блокує лише ✗ поза базою, виправлене з бази — назвати. Перезапис — лише руками (rm).
if (opt.base) { const key = f => `${f.kind}|${f.where}`, cur = [...new Set(['light', 'dark'].flatMap(t => r[t].filter(f => f.lvl === '✗').map(key)))];
  if (!existsSync(opt.base)) { writeFileSync(opt.base, JSON.stringify(cur, null, 1)); console.log(`✓ база ui_lint записана: ${cur.length} ✗ → ${opt.base} (до правки; після — той самий --baseline)`); process.exit(0); }
  const base = new Set(JSON.parse((await import('node:fs')).readFileSync(opt.base, 'utf8'))), gone = [...base].filter(k => !cur.includes(k));
  for (const t of ['light', 'dark']) for (const f of r[t]) if (f.lvl === '✗' && base.has(key(f))) { f.lvl = 'ⓘ'; f.acc = true; f.msg += ' — з бази (було до правки)'; }
  if (gone.length) console.log(`ⓘ виправлено з бази: ${gone.length} (${gone.slice(0, 3).join(' · ')}${gone.length > 3 ? ' …' : ''})`); }
let x = 0, w = 0;
for (const t of ['light', 'dark']) {
  const seen = new Set(); const rows = r[t].filter(f => { const k = f.lvl + f.kind + f.where + f.msg; if (seen.has(k)) return false; seen.add(k); return true; });
  x += rows.filter(f => f.lvl === '✗').length; w += rows.filter(f => f.lvl === '⚠').length;
  if (!opt.json) { console.log(`— ${t === 'light' ? 'світла' : 'темна'} тема`); for (const f of rows.filter(f => f.lvl !== 'ⓘ')) console.log(`  ${f.lvl} ${f.kind} · ${f.state || ''} · ${f.where} — ${f.msg}`);
    for (const f of rows.filter(f => f.acc)) console.log(`  ⓘ ${f.kind} · ${f.where} — ${f.msg}`);
    const n = rows.filter(f => f.lvl === 'ⓘ' && !f.acc).length; if (n) console.log(`  ⓘ не виміряно контраст на ${n} елементах (градієнт / картинка) — глянь очима`); }
}
console.log(`─── ui_lint: ✗ ${x} · ⚠ ${w} · екранів ${states.length + 1} (початковий + станів ${states.length}) × 2 теми ───`);
if (opt.repo && !x) {   // позначка для воріт: той самий хеш диффу UI, що рахує ui-review-gate
  const hx = execFileSync('bash', [join(here, 'hooks/ui-review-gate.sh'), 'hash', resolve(opt.repo)], { encoding: 'utf8' }).trim();
  if (hx) { writeFileSync(`/tmp/lens-uilint-${hx}`, `${new Date().toISOString()} ✗0 ⚠${w} ${target} states=${states.length || 1}\n`); console.log(`✓ позначка ui_lint для диффу ${hx.slice(0, 8)} — ворота огляду приймуть done`); }
}
process.exit(x ? 1 : 0);
