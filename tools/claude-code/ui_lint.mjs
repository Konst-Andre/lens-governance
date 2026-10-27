// живе доки: агент Claude Code будує інтерфейси (HTML/CSS, PWA, Mini App) для Konst. Дім — lens-governance:tools/claude-code/ (бриф §HOOK-2.5, «так» Konst 10.10.2026).
// ui_lint — машинна частина огляду UI: те, що видно програмі, ловить програма, а не Konst («капсула прилипла», «текст обрізаний», «іконка вище»).
// Рух НЕ судить — лише статичні кадри (переходи на час натискання й наведення вимкнено, AE S103); рух — окремий прилад, kernel/Lens_MOTION-1_brief.md.
// Очі агента лишаються: машина бачить ~третину вад (розвідка 10.10: axe/WCAG-огляди), решта — чек-лист воріт ui-review-gate.
//
// Запуск:  node ui_lint.mjs <url|файл.html> [--state "<js>"]… [--scope <корінь острова>] [--repo <тека>] [--width 390] [--height 844] [--themes light|dark|both] [--serial] [--json] [--baseline <файл>] [--ready "<js-умова>"]   (низький екран Safari: --width 375 --height 634)
//          кожен --state — окремий стан (JS виконується на сторінці; між станами сторінка перезавантажується); без --state — лише початковий.
//          --state — ВИРАЗ, не модуль: `await` верхнього рівня → ✗ «JS стану впав»; чекати — `new Promise(r=>setTimeout(()=>{…;r()},1800))` (QR CC-13, 15.10.2026: шіт відкривається з затримкою).
//          Теми (prefers-color-scheme): типово обидві, паралельно; --themes light|dark — продукт з однією схемою (AE S103: темний прохід AE = копія світлого). --repo: ✗ 0 → позначка для воріт (той самий хеш диффу, що в ui-review-gate).
//          <repo>/.ui-lint-accept — відомі вади, прийняті Konst: рядок «вид | шматок адреси елемента | причина · дата» → ⓘ (не блокує, але друкується щоразу).
//          node ui_lint.mjs selftest — зуби: сторінка з підкинутими вадами (кожна мусить дати свій рядок) і чиста (0).
// Перевірки: 1 скрол убік · 2 обрізано · 3 прилипло / вилазить · 4 контраст (4-б — на градієнті пікселем знімка) · 5 шрифт · 6 тап, без назви, iOS-зум · 7 накладання · 8 ряд · 9 текст (сміття, жаргон) ·
// 10 дія в прокрутці · 11 кнопки ряду · 12 сирота · 13 злито · 14 однакові заголовки · 15 дата й час · 16 зливається (16-б край кнопки) · 17 паритет тем · 18 кромка · 19 картка-список · 20 вкладена прокрутка · 21 шапка в прокрутці · 22 емодзі в кнопці · 23 нативне вікно · 24 фон у рамці · 25 кант рветься · 26 поле губиться; поза probe — натискання (:active / JS pointerdown, touchstart).
// 31 форма виділення · 32 пунктир < 3:1 · 22 емодзі-значок без підпису → ✗ · 33 різнобій списків — AE S94, 20.10.2026.
// 34 пояснення під кнопкою (→ «i») · 35 наведення (ПК, ≥ 1024: нема або ледь видно; S107 — і «лише тінь < 0,12») — AE S96, 20.10.2026.
// 43 список угорі (закритий base-select не flex — текст притиснутий догори; рецепт A117) — пропуск Konst, AE S107, 26.10.2026.
// 42 знак не по центру (1–2 знаки чи один значок у маленькій кнопці / бейджі: «чорнило» зсунуте ≥ 1 px або ≥ 0,5 px впритул до краю — пікселем) — пропуск Konst, AE S102, 23.10.2026.
// 41 інструкція в повідомленні (порада про клавішу, «Передумали», «✕», > 1 речення в помилці, повтор «i») — правило Konst «форма пояснює себе», AE S101 В-211, 23.10.2026.
// 40 підказка стрибає (popover у першому видимому кадрі не на своєму місці — ставлять у «toggle», що приходить після показу) — пропуск Konst, AE S101, 22.10.2026.
// 39 край розчиняється (поверхня ≥ 320×160 майже в тон тла, ΔE < 6, без рамки й тіні) — пропуск Konst, AE S99, 21.10.2026.
// 38 пояснення абзацом (≥ 20 слів дрібного тексту поза «i» / вікном / таблицею / повідомленням → «i») — пропуск Konst, AE S99, 21.10.2026.
// 37 налізає — текст ширший за свій блок при overflow: visible (не обрізаний, а виходить на сусіда) — пропуск Konst, AE S97, 21.10.2026 (вікно «Групи»).
// 36 кадр не встиг (екран ще змінювався під час заміру) — AE S97, 21.10.2026: замір чекає шрифти, --ready і тишу DOM (до 3 с), а не фіксовані 400 мс;
//    --json — чистий JSON у stdout (решта — stderr), --baseline бере і масив ключів, і звіт --json; 3 не судить прокручене за край обрізального предка.
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
    // AE S109: випадне меню / вікно (role=menu|dialog|listbox, absolute|fixed) виходить за картку за будовою — не «вилазить» (хибне: вікно «Дані» примірки v10)
    const pop = /^(absolute|fixed)$/.test(s.position) && el.matches('[role=menu],[role=dialog],[role=listbox]');
    const c = chip && !pop && card(el);
    // AE S97: між капсулою й карткою буває прокрутка (список з overflow auto) — прокручене за її край не «вилазить», а сховане; судимо лише видиме в ній.
    // Абсолютний елемент предок зі static не обрізає (Cypress #28638; Floating UI detectOverflow — «clipping ancestors», 21.10.2026), fixed — жоден.
    let k = null; if (c && s.position !== 'fixed') for (let e = el.parentElement; e && e !== c; e = e.parentElement) { const o = getComputedStyle(e);
      if ((o.overflowX !== 'visible' || o.overflowY !== 'visible') && !(s.position === 'absolute' && o.position === 'static')) { k = e; break; } }
    const kr = k && k.getBoundingClientRect(), cut = !!kr && (r.top < kr.top - 1 || r.bottom > kr.bottom + 1 || r.left < kr.left - 1 || r.right > kr.right + 1);
    if (c && c !== el && !cut) { const q = c.getBoundingClientRect(), d = [r.top - q.top, q.right - r.right, q.bottom - r.bottom, r.left - q.left];
      const full = r.width >= q.width - 2 || /^(TH|TD)$/.test(el.tagName);   // на всю ширину картки (рядок, смужка) — не капсула; клітинка таблиці торкається краю картки за будовою (хибне AE S99, Г4)
      if (!full && d.some(x => x < -1) && getComputedStyle(c).overflow === 'visible') add('✗', 'вилазить', el, `виходить за межі «${path(c)}» на ${Math.round(-Math.min(...d))} px`);
      else if (!full && d.some(x => x >= -1 && x < 2) && !(r.height >= q.height - 2)) add('✗', 'прилипло', el, `майже торкається краю «${path(c)}» (${d.map(x => Math.round(x)).join('/')} px) — «приклеєна капсула»`); }
    // 37. налізає (пропуск Konst AE S97: «за замовчуванням» у колонці 96 px, nowrap, ліз під кошик): текст ширший за власний блок і НЕ обрізаний — він виходить
    //     за межі й лягає на сусіда; «обрізано» (№2) бачить лише hidden / clip. Блок із власною шириною (не inline), видимий вміст за правим краєм > 1 px.
    //     Міряємо межі САМОГО тексту (Range), не scrollWidth: той рахує й ::after зони кліку (x44 у самоперевірці). Обидва боки — вирівняне праворуч лізе ліворуч.
    if (own && s.display !== 'inline' && el.clientWidth > 0 && s.overflowX === 'visible' && s.textOverflow !== 'ellipsis') {
      let L = Infinity, R = -Infinity; const rg = document.createRange();
      for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) { rg.selectNodeContents(n); const b = rg.getBoundingClientRect(); if (b.width) { L = Math.min(L, b.left); R = Math.max(R, b.right); } }
      const over = Math.max(R - r.right, r.left - L);
      if (over > 1) add('✗', 'налізає', el, `текст виходить за свій блок на ${Math.round(over)} px і не обрізаний — заходить на сусіда (дай місце, перенос або «…»)`); }
    // 4. контраст тексту
    if (own && el.textContent.trim().length > 1) { const fg = rgba(s.color), bg = bgOf(el), px = parseFloat(s.fontSize), big = px >= 24 || (px >= 18.66 && +s.fontWeight >= 700), need = big ? 3 : 4.5;
      if (fg && bg) { const f = fg[3] < 1 ? blend(fg, bg) : fg, a = lum(f), b = lum(bg), cr = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        if (cr < need) add('✗', 'контраст', el, `контраст ${cr.toFixed(2)}:1 < ${need}:1 — погано читається`); }
      else if (fg && !el.closest('[class*="brand"],[data-logo]')) { const cx = r.left + r.width / 2, cy = r.top + r.height / 2, hit = cx >= 0 && cy >= 0 && cx < innerWidth && cy < innerHeight && (t => t && (t === el || el.contains(t)))(document.elementFromPoint(cx, cy));
        // 4-б. фон — градієнт / картинка: міряє Node пікселем знімка (кільце довкола тексту); текст поза екраном чи під шаром — «не виміряно»; логотип (клас *brand*, data-logo) — виняток WCAG 1.4.3
        // AE S109: кільце — довкола ВЛАСНОГО тексту, не всього елемента: у кнопки-чипа кільце довкола рамки міряло тло сторінки за кнопкою (хибне 1,00:1 — білий на синьому градієнті)
        const tr = (q => q.length ? [Math.min(...q.map(v => v.left)), Math.min(...q.map(v => v.top)), Math.max(...q.map(v => v.right)), Math.max(...q.map(v => v.bottom))] : null)([...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).map(n => { const g = document.createRange(); g.selectNodeContents(n); return g.getBoundingClientRect(); }).filter(v => v.width));
        out.push({ lvl: hit ? 'px' : 'ⓘ', kind: 'контраст', where: path(el), msg: 'фон — градієнт чи картинка: контраст не виміряно, глянь очима', rect: tr ? [tr[0], tr[1], tr[2] - tr[0], tr[3] - tr[1]] : [r.left, r.top, r.width, r.height], fg, need }); }
      // 5. дрібний текст
      if (px < 11) add('⚠', 'шрифт', el, `текст ${px}px < 11 — на телефоні дрібно`); }
    // 6. цілі тапу; поле вводу < 16 px
    // AE S100: під відкритим модальним вікном решта сторінки інертна (HTML «modal dialog» — inert) — натиснути її не можна, ціль не судимо;
    //   зонд elementFromPoint влучав у тло вікна й міряв голу коробку («i» 18 px з ::before 26 → «18 < 24», хибне на вікні-переліку каталогу AE).
    const modal = document.querySelector('dialog:modal');
    if (el.matches('a[href],button,[role=button],input:not([type=hidden]),select,textarea,summary') && !(modal && !modal.contains(el))) {
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
  // 39. край розчиняється (пропуск Konst AE S99: тіло таблиці біле на кремовому тлі, ΔE ≈ 4, без рамки й тіні — «по краях розчиняється»):
  //     поверхня (власне тло, а в таблиці — тло клітинок) площею від 320×160 px, майже в тон тла під нею (ΔE < 6), без тіні й без рамки,
  //     помітної на тому тлі, — ⚠; ліки — рамка чи тінь картки (як картки редактора), або тон поверхні виразніший.
  { const vis = (s, side, under) => parseFloat(s['border' + side + 'Width']) > 0 && s['border' + side + 'Style'] !== 'none' && (() => { const c = rgba(s['border' + side + 'Color']); return c && c[3] > 0.2 && dE(lab(c), lab(under)) >= 6; })();
    for (const el of all) { const r = el.getBoundingClientRect(); if (r.width < 320 || r.height < 160 || !el.parentElement) continue;
      if (r.width >= innerWidth * 0.9 && r.height >= innerHeight * 0.9) continue;   // сама сторінка — тло, не картка (хибне на корені .v2, AE S99)
      const s = getComputedStyle(el); let surf = rgba(s.backgroundColor), from = el;
      if ((!surf || surf[3] < 0.99) && el.tagName === 'TABLE') { const td = el.querySelector('tbody td'); if (td) { surf = rgba(getComputedStyle(td).backgroundColor); from = td; } }
      if (!surf || surf[3] < 0.99) continue;
      const under = flatBg(el.parentElement); if (!under) continue; const d = dE(lab(surf), lab(under)); if (d < 0.5 || d >= 6) continue;
      if (s.boxShadow !== 'none' || ['Top', 'Right', 'Bottom', 'Left'].filter(x => vis(s, x, under)).length >= 2) continue;
      if (from !== el && getComputedStyle(from.closest('tbody') || from).boxShadow !== 'none') continue;
      add('⚠', 'край розчиняється', el, `поверхня ${Math.round(r.width)}×${Math.round(r.height)} майже в тон тла під нею (ΔE ${d.toFixed(1)}), без рамки й тіні — край тоне; дай картці рамку або тінь`); } }
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
  // 34. пояснення під кнопкою (пропуск Konst AE S96, 20.10.2026: «Модель зіграє клієнта за цим сценарієм… — зайвий шум; пояснення — у букву «i», що розгортається»):
  //     дрібний (≤ 12,5 px) текст-речення (≥ 6 слів) одразу після керуючого (сам або в невеликій обгортці, ≤ 3 дітей) — ⚠; ліки — кнопка «i» з popover поруч (кукбук A117).
  //     Кнопка-«i» (popovertarget) — не керуючий тут: підпис біля неї — інша розмова.
  { const ctl = e => e && (e.matches('button:not([popovertarget]),[role=button]') || (e.children.length <= 3 && [...e.children].some(c => c.matches('button:not([popovertarget]),[role=button]'))));
    for (const el of all) { if (!/^(SMALL|P|SPAN|DIV)$/.test(el.tagName) || el.children.length || !el.getBoundingClientRect().width) continue;
      const t = (el.textContent || '').trim(); if (t.split(/\s+/).length < 6 || parseFloat(getComputedStyle(el).fontSize) > 12.5) continue;
      if (ctl(el.previousElementSibling)) add('⚠', 'пояснення під кнопкою', el, `«${t.slice(0, 40)}…» — підпис-пояснення під кнопкою; на робочому екрані це шум — перенести в «i» поруч з кнопкою (кукбук A117)`); } }
  // 38. пояснення абзацом (пропуск Konst AE S99, 21.10.2026: абзац-пояснення в панелі й рядок клавіш під таблицею — «пояснення — у «i», не блоком тексту»):
  //     блок, у якому ≥ 20 слів дрібного (≤ 13 px) тексту, без керуючих усередині (посилання й <kbd> — можна), поза «i» / вікном / таблицею — ⚠;
  //     звітуємо найглибший такий блок. Не чіпаємо: дані (таблиця, поле), повідомлення про помилку й стан (role=alert/status, aria-live) —
  //     те, без чого не виконати дію, лишається на екрані; додаткове пояснення — у «i» (Carbon «Tooltip usage», Coloplast «Toggletip», 21.10.2026).
  { const words = t => (t.match(/[\p{L}\p{N}₴]+/gu) || []).length;
    const small = el => { const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n;
      while ((n = w.nextNode())) if (n.textContent.trim() && parseFloat(getComputedStyle(n.parentElement).fontSize) > 13) return false; return true; };
    const cand = el => !/^(HTML|BODY|MAIN|TABLE|THEAD|TBODY|TR|TD|TH|UL|OL|SELECT|TEXTAREA|BUTTON|INPUT|LABEL|SCRIPT|STYLE)$/.test(el.tagName)
      && el.getBoundingClientRect().width && !el.closest('[popover],dialog,[role=tooltip],.tip,table,label,button,[role=alert],[role=status],[aria-live]')
      && !el.querySelector('button,input,select,textarea,[role=button],[contenteditable]')
      && words(el.innerText || '') >= 20 && small(el);
    for (const el of all) { if (!cand(el) || [...el.children].some(cand)) continue;
      add('⚠', 'пояснення абзацом', el, `«${(el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 40)}…» — ${words(el.innerText || '')} слів пояснення блоком на робочому екрані; пояснення — у «i» поруч із тим, що пояснює (кукбук A116 · A117)`); } }
  // 41. інструкція в повідомленні (правило Konst AE S101, 23.10.2026, В-211: «ми не інструкцію пишемо — треба, щоб користувач користувався сайтом так, наче вже знає
  //     інструкцію»): повідомлення (помилка, стан, тост — role=alert/status, короткий aria-live, клас msg/err/error/toast, текст із «✕» на початку) — ⚠, коли в ньому
  //     (а) порада про клавішу («Esc — …», «натисніть Enter») — клавіші живуть в «i»; (б) «Передумали — …» — дію вже видно кнопкою «↶» поруч;
  //     (в) «✕» перед текстом — за виглядом це «закрити», а помилку кажуть значок і тон; (г) помилка (role=alert) довша за одне речення;
  //     (д) речення з «i» сторінки (≥ 5 слів) повторено — пояснене раз не повторюється. «i», вікна й підказки не судимо — там клавішам і місце.
  //     Практика: inline error — одне коротке речення «що не так» (Shopify Polaris «Inline error»; NN/g «Error-Message Guidelines», 23.10.2026).
  { const norm = t => (t || '').replace(/\s+/g, ' ').trim(), wc = t => (t.match(/[\p{L}\p{N}]+/gu) || []).length;
    const tips = [...document.querySelectorAll('[popover],[role=tooltip],.tip')].map(e => norm(e.textContent).toLowerCase()).filter(Boolean);
    const isMsg = el => !el.closest('[popover],[role=tooltip],.tip,kbd') && !/^(BUTTON|INPUT|TEXTAREA|SELECT|OPTION)$/.test(el.tagName)
      && (el.matches('[role=alert],[role=status],.msg,.err,.error,.toast') || (el.matches('[aria-live]:not([aria-live=off])') && wc(el.innerText || '') <= 40)
          || /^\s*[✕×✖]\s+\S/.test([...el.childNodes].map(n => n.nodeType === 3 ? n.textContent : '').join('')));
    const seen = new Set();
    for (const el of all) { if (!isMsg(el) || [...seen].some(p => p.contains(el))) continue; seen.add(el);
      const t = norm(el.innerText), why = []; if (!t) continue;
      if (/(^|[^\p{L}])(Esc|Enter|Tab|Ctrl|Shift|Alt|Cmd)(\s*\+\s*\S+)?\s*[—–:-]\s*\p{L}|натисн\p{L}*\s+(клавішу\s+)?«?(Esc|Enter|Tab|Ctrl|Shift)/iu.test(t)) why.push('порада про клавішу (клавіші — в «i»)');
      if (/передумал\p{L}*/iu.test(t)) why.push('«Передумали — …» (дію вже видно кнопкою поруч)');
      if (/^[✕×✖]\s/.test(t)) why.push('«✕» перед текстом (виглядає як «закрити»; помилку кажуть значок і тон)');
      const sent = t.split(/(?<=[.!?])\s+(?=[\p{Lu}«])/u).filter(x => wc(x) >= 2);
      if (el.closest('[role=alert]') && sent.length > 1) why.push(`${sent.length} речення (помилка — одне: що не так)`);
      const rep = sent.find(x => wc(x) >= 5 && tips.some(p => p.includes(x.replace(/[.!?]$/, '').toLowerCase())));
      if (rep) why.push(`повтор пояснення з «i»: «${rep.slice(0, 40)}»`);
      if (why.length) add('⚠', 'інструкція в повідомленні', el, `«${t.slice(0, 48)}» — ${why.join('; ')}; форма пояснює себе, текст — лише те, чого не видно (В-211 AE)`); } }
  // 43. текст у списку притиснутий догори (пропуск Konst AE S107, «Сортувати»: «текст прижатий до поверхні, не відцентрований»): закритий <select> з
  //     appearance: base-select ставить текст угору, якщо сам список не flex (рецепт A117: display:inline-flex; align-items:center; W3C CSSWG, березень 2026 —
  //     «button-like elements don't do any vertical alignment», 26.10.2026). Дешево — лише обчислений стиль.
  for (const el of document.querySelectorAll('select')) { const s = getComputedStyle(el); if (!vis(el) || s.appearance !== 'base-select') continue;
    const lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.2, room = el.clientHeight - parseFloat(s.paddingTop) - parseFloat(s.paddingBottom);   // відступи вже центрують — тиші (AE: «+ Додати позицію»)
    if ((!/flex|grid/.test(s.display) || !/center/.test(s.alignItems)) && room > lh * 1.25) add('⚠', 'список угорі', el, `закритий список (base-select) — display:${s.display}, align-items:${s.alignItems}: текст притиснутий догори; display:inline-flex; align-items:center (A117)`); }
  // 42. знак не по центру (пропуск Konst AE S102, 23.10.2026: «/» у пошуку «торкається верхівки» — замір пікселями: 4 px згори, 6 знизу;
  //     рамка тексту (Range) цього не бачить — шрифт ставить «/» вище своєї рамки). Кандидат: маленька кнопка чи бейдж (≤ 48×32 px) з рамкою або тлом,
  //     у якому 1–2 знаки або один значок SVG; міряє Node пікселями знімка (рамка «чорнила», як optical-properties; «оптичний центр мас» — ні, суб'єктивний).
  //     Кандидати — і з aria-hidden (декоративна підказка клавіші «/» прихована від читача екрана, але її бачать очі; AE S102 — vis() її пропускав).
  const seen42 = [...document.querySelectorAll('body *')].filter(e => { const s = getComputedStyle(e), r = e.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 0 && !e.closest('[hidden]') && !e.closest('svg'); });
  for (const el of seen42) { const r = el.getBoundingClientRect(); if (r.width > 48 || r.height > 32 || r.width < 12 || r.height < 12) continue;
    const s = getComputedStyle(el), boxed = parseFloat(s.borderTopWidth) > 0 || (rgba(s.backgroundColor) || [0, 0, 0, 0])[3] > 0.05; if (!boxed) continue;
    const t = (el.textContent || '').replace(/\s+/g, ''), svg = el.querySelectorAll('svg').length, kids = el.querySelectorAll('*').length;
    if (!((t.length >= 1 && t.length <= 2 && !svg && !el.children.length) || (!t && svg === 1 && el.children.length === 1))) continue; void kids;
    const pe = el.style.pointerEvents; el.style.pointerEvents = 'auto';   // підказка клавіші «/» — pointer-events:none: без цього під нею «знаходиться» поле
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2, top = document.elementFromPoint(cx, cy), top2 = document.elementFromPoint(cx, r.top + 2); el.style.pointerEvents = pe;
    if (!top || !(top === el || el.contains(top)) || !top2 || !(top2 === el || el.contains(top2))) continue;   // під іншим шаром (липка шапка списку) — пікселі чужі (хибне AE S102: «.sid» 2,8 px)
    const bt = parseFloat(s.borderTopWidth) || 0, bb = parseFloat(s.borderBottomWidth) || 0, bl = parseFloat(s.borderLeftWidth) || 0, br = parseFloat(s.borderRightWidth) || 0;
    out.push({ lvl: 'ink', kind: 'знак не по центру', where: path(el), msg: '', rad: parseFloat(s.borderTopLeftRadius) || 0, rect: [r.left + bl, r.top + bt, r.width - bl - br, r.height - bt - bb] }); }
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
  const BOX = /^(padding|margin|width|height|min-|max-|border(?!-collapse)|overflow|position|top|right|bottom|left|inset|display|transform|cursor|background|box-shadow|grid|flex|gap|z-index|outline|font-family$|font-size$)/;   // + шрифт (пропуск AE S99: моно-цифри тренажера .num протекли в суми редактора)
  const walk = list => { for (const r of list) { if (r.cssRules && !r.selectorText) { walk(r.cssRules); continue; } if (!r.selectorText || r.selectorText.includes(tok)) continue;
    const props = [...r.style].filter(x => BOX.test(x)); if (!props.length) continue;
    for (const sel of r.selectorText.split(',').map(x => x.trim())) { if (!/[.#\[]/.test(sel.replace(/:[a-z-]+(\([^)]*\))?/g, ''))) continue;   // лише теги / * — скидання
      let n = 0; try { n = els.filter(e => e.matches(sel)).length; } catch { continue; } if (!n || seen.has(sel)) continue; seen.add(sel);
      out.push({ lvl: '⚠', kind: 'чуже правило', where: sel, msg: `правило поза «${scope}» влучає в ${n} ел. острова: ${[...new Set(props.map(x => x.replace(/-(top|right|bottom|left|block|inline).*$/, '')))].slice(0, 5).join(', ')} — префікс у чужого правила або перекриття в острові` }); } } };
  for (const sh of document.styleSheets) { let rs; try { rs = sh.cssRules; } catch { continue; } walk(rs); }
  return out;
}
let THEMES = ['light', 'dark'];   // --themes light|dark|both (AE S103)
let SERIAL = false;   // --serial — теми по черзі (AE S103, аудит)
let SCOPE = '';   // --scope
let READY = '';   // --ready: JS-умова готовності сторінки (S97); чекаємо після кожного завантаження, до 10 с

const SELF = `<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>
body{margin:0;font:15px/1.4 sans-serif;background:#fff;color:#111}@media(prefers-color-scheme:dark){body{background:#111;color:#eee}}
.card{margin:16px;padding:14px;border-radius:14px;background:#f2f2f2;position:relative}@media(prefers-color-scheme:dark){.card{background:#222}}
.pill{display:inline-block;padding:2px 8px;border-radius:99px;background:#237770;color:#fff}.tl{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}.ic{width:30px;height:30px;border-radius:50%;background:#bbb}.row{display:flex;gap:8px}.tile{flex:1;border-radius:10px;background:#ddd;padding:8px}
.x44{position:relative;width:26px;height:26px;padding:0}.x44::after{content:'';position:absolute;inset:-12px}.grey{color:#aaa}.clip{width:60px;overflow:hidden;white-space:nowrap}button:active{transform:scale(.97)}.jsp{color:inherit}.jsp.pressing{transform:scale(.9)}</style><script>document.addEventListener('touchstart',()=>{},{passive:true});document.addEventListener('pointerdown',e=>{const c=e.target.closest('.jsp');if(c)c.classList.add('pressing')});document.addEventListener('pointercancel',()=>document.querySelectorAll('.pressing').forEach(x=>x.classList.remove('pressing')))</script></head><body>
<div class=card id=ok><button class=x44 aria-label="Закрити">✕</button> <button style="min-height:48px;padding:0 16px">Завантажити KPI</button> <span class=pill>6 дн.</span> <a class=jsp href="#j" style="display:inline-block;padding:14px 18px">Відкрити (A67)</a></div>
<div class=card><div style="height:96px;overflow-y:auto">${[1, 2, 3, 4].map(i => `<div class=li style="padding:4px 0">Рядок ${i} <span class=pill>група</span> <button style="min-height:44px">Повернути</button></div>`).join('')}</div></div>
${'BAD'}</body></html>`;
const DEFECTS = {
  'налізає': `<div class=card style="display:flex;align-items:center;gap:4px"><small style="display:block;width:60px;white-space:nowrap">за замовчуванням</small><button aria-label="Видалити" style="min-height:44px;min-width:44px">✕</button></div>`,   // 37 (S97)
  'кадр': `<div class=card id=tick>0</div><script>setInterval(()=>{tick.textContent+=1},150)</script>`,   // 36: екран не вщухає (S97)
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
  'пояснення під кнопкою': `<div class=card><div><button style="min-height:44px;padding:0 14px">Пробна розмова</button><small style="font-size:11.5px;display:block">Модель зіграє клієнта за цим сценарієм, як для фармацевта.</small></div></div>`,   // AE S96: підпис під «Пробна розмова»
  'підказка стрибає': `<style>.tp{position:fixed;inset:auto;margin:0;padding:8px;border:1px solid #888;background:#fff}</style><div class=card><button popovertarget=tp1 style="min-height:44px;min-width:120px;margin-left:200px">i</button><div popover id=tp1 class=tp>Пояснення</div></div><script>document.addEventListener('toggle',e=>{const t=e.target;if(e.newState!=='open')return;const r=document.querySelector('[popovertarget=tp1]').getBoundingClientRect();t.style.left=r.left+'px';t.style.top=(r.bottom+6)+'px'},true)</script>`,
  'наведення ': `<style>.hv2{min-height:44px;padding:0 14px;border:1px solid #ddd;background:#fff;transition:none}.hv2:hover{box-shadow:0 6px 18px rgba(28,30,36,.08)}</style><div class=card><button class=hv2>Плитка</button></div>`,   // AE S107: лише тінь .08
  'список угорі': `<style>select.sb{appearance:base-select;height:34px;padding:0 10px}</style><div class=card><select class=sb aria-label=Сортувати><option>За назвою</option></select></div>`,   // AE S107
  'наведення': `<style>.hv{min-height:44px;padding:0 14px;border:0;background:#fff}.hv:hover{background:#FFFEF6}</style><div class=card><button class=hv>Рядок списку</button></div>`,   // AE S96: наведення кремовим на білому — 1,01:1
  'пояснення абзацом': `<div class=card><div style="font-size:12.5px;color:#555;background:#F6F7F8;padding:10px">Змінили бонус — сценарії з цією позицією в наборі перерахують орієнтир; якщо набір стане не дорожчим за замовлення, біля сценарію з’явиться позначка.</div></div>`,   // AE S99: абзац у панелі замість «i»
  'знак не по центру': `<div class=card><kbd aria-hidden="true" style="display:inline-block;height:20px;padding:0 5px;border:1px solid #999;border-radius:5px;background:#fff;color:#111;font:600 12px/13px sans-serif;vertical-align:top">/</kbd></div>`,   // AE S102: «/» у пошуку вище центру
  'інструкція в повідомленні': `<div class=card><span role=alert style="font-size:13px">✕ Назва не може бути порожньою. Esc — повернути як було.</span></div>`,   // AE S101, В-211: помилка клітинки каталогу
  'край розчиняється': `<div style="background:#FEFDF5;padding:20px"><table style="border-collapse:collapse;width:600px"><tbody>${Array.from({length: 8}, () => '<tr><td style="background:#fff;padding:10px">Позиція</td><td style="background:#fff;padding:10px">12,00</td></tr>').join('')}</tbody></table></div>`,   // AE S99: тіло таблиці на тлі без краю
  'чуже правило ': `<style>.num{font-family:monospace}</style><div class=isl><b class=num style="display:inline-block;min-height:44px">647,00 ₴</b></div>`,   // AE S99: шрифт тренажера в острові
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
// 42. рамка «чорнила» всередині рамки кнопки: тло — медіана пікселів 1-го внутрішнього рядка згори й знизу; «чорнило» — відхилення > 60 у будь-якому каналі.
//     «чорнило» — ядро знака: відхилення > 70 % найбільшого в кнопці (без згладжування). Зсув = (зазор згори − зазор знизу) / 2 у CSS-px; ⚠ від 1 px, або від 0,5 px, коли знак ближче 3 px до краю. Поза знімком / нема чорнила / строкате тло — не міряємо (тиша).
function inkOffset(img, f) {
  const [x, y, w, h] = f.rect.map(v => Math.round(v * 2)); if (x < 0 || y < 0 || x + w > img.w || y + h > img.h || w < 8 || h < 8) return null;
  // поза заокругленими кутами: крізь кут видно тло сторінки — світлі пікселі кута «чорнилом» на темній кнопці (хибне AE S102: активний номер 2,8 px)
  const rr = Math.min(f.rad || 0, h / 4, w / 4) * 2;   // радіус кута у пікселях знімка
  const ins = Y => { const dy = Math.min(Y - y, y + h - 1 - Y); return 3 + (dy >= rr ? 0 : Math.ceil(rr - Math.sqrt(Math.max(0, rr * rr - (rr - dy) ** 2)))); };   // відступ від краю на рядку Y — лише в дузі кута
  const x0 = x, x1 = x + w;
  const at = (X, Y) => { const i = (Y * img.w + X) * img.bpp; return [img.px[i], img.px[i + 1], img.px[i + 2]]; };
  const edge = []; for (const Y of [y + 1, y + h - 2]) for (let X = x0 + ins(Y); X < x1 - ins(Y); X++) edge.push(at(X, Y));
  const med = c => { const v = edge.map(p => p[c]).sort((a, b) => a - b); return v[v.length >> 1]; }, bg = [med(0), med(1), med(2)];
  if (edge.filter(p => Math.max(...p.map((v, c) => Math.abs(v - bg[c]))) <= 24).length < edge.length * 0.8) return null;
  const dif = q => Math.max(...q.map((v, c) => Math.abs(v - bg[c]))); let mx = 0;
  for (let Y = y + 3; Y < y + h - 3; Y++) for (let X = x0 + ins(Y); X < x1 - ins(Y); X++) mx = Math.max(mx, dif(at(X, Y)));
  if (mx < 60) return null;   // знака не видно на тлі — не міряємо
  // ядро знака — 70 % найбільшого відхилення в кнопці (адаптивний поріг від місцевого діапазону — US10572751): сталий поріг 60 / 110
  // зміщував замір «/» через згладжування (AE S102: −0,25 / −0,5 px замість −1,0); 0,7 — замір агента на двох білдах (rev 6 −1,0 ⟂ новий 0,0)
  const ink = Y => { for (let X = x0 + ins(Y); X < x1 - ins(Y); X++) if (dif(at(X, Y)) > 0.7 * mx) return true; return false; };
  let top = -1, bot = -1; for (let Y = y + 3; Y < y + h - 3; Y++) if (ink(Y)) { if (top < 0) top = Y; bot = Y; }
  if (top < 0) return null;
  const gt = (top - y) / 2, gb = (y + h - 1 - bot) / 2;   // зазори згори / знизу, CSS-px (знімок ×2)
  return { d: (gt - gb) / 2, gap: Math.min(gt, gb) };
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

async function lint(target, states, width, theme, browser, scope = SCOPE) {
  const ctx = await browser.newContext({ viewport: { width, height: HEIGHT }, deviceScaleFactor: 2, colorScheme: theme });
  const p = await ctx.newPage(), errs = [], dlg = []; p.on('pageerror', e => errs.push(e.message)); p.on('dialog', d => { dlg.push(d.type() + ': ' + d.message()); d.dismiss().catch(() => {}); });   // 23. нативне вікно (пропуск Konst QR CC-12: «свій підпис» відкрив prompt браузера) p.on('console', m => m.type() === 'error' && !/Failed to load resource/.test(m.text()) && errs.push(m.text()));
  // AE S103 (wsd 1.21, аудит 24.10.2026: «ui_lint сам має паузи без “чому N”»): пауза після завантаження й після стану — «тиша до N» (pw_quiet.js:
  //   таймери сторінки з терміном у вікні · скінченні анімації · запити · два кадри), а не простій; QUIET=0 — старі паузи (негативний контроль).
  const QOFF = process.env.QUIET === '0'; if (!QOFF) await p.addInitScript({ path: join(here, 'pw_quiet.js') });
  const quiet = ms => QOFF ? p.waitForTimeout(ms) : p.evaluate(m => window.__aeQuiet ? window.__aeQuiet(m) : new Promise(r => setTimeout(r, m)), ms).catch(() => p.waitForTimeout(ms));
  const res = [];
  for (const [i, st] of [null, ...states].entries()) {   // початковий екран — завжди, далі кожен стан
    await p.goto(target, { waitUntil: 'load' }); await quiet(400);
    // 36. готовність кадру (AE S97: дані приходять мережею після load — 400 мс то встигали, то ні, і та сама сторінка давала 0 або 35 ✗)
    try { await p.evaluate(() => document.fonts.ready.then(() => 1)); } catch {}
    if (READY) { try { await p.waitForFunction(READY, null, { timeout: 10000 }); } catch { res.push({ lvl: '✗', kind: 'стан', where: st ? `стан ${i}` : 'початковий', msg: `умова --ready не настала за 10 с: ${READY.slice(0, 60)}` }); } }
    if (st) { try { await p.evaluate(st); } catch (e) { res.push({ lvl: '✗', kind: 'стан', where: `стан ${i}`, msg: 'JS стану впав: ' + e.message.split('\n')[0] }); } await quiet(700); }
    { const sig = () => p.evaluate(() => document.querySelectorAll('*').length + ':' + document.body.innerText.length); let a0 = await sig(), still = false;
      for (let n = 0; n < 5 && !still; n++) { await p.waitForTimeout(600);   /* pause-ok: вікно тиші DOM (№36) — справжній час за задумом */ const a1 = await sig(); still = a1 === a0; a0 = a1; }
      if (!still) res.push({ lvl: '⚠', kind: 'кадр', where: 'body', state: st ? `стан ${i}` : 'початковий', msg: `екран ще змінювався через 3 с після ${st ? 'стану' : 'завантаження'} — замір міг зловити проміжний кадр; дай --ready "<умова готовності>" або зупини таймер у стані` }); }
    const found = await p.evaluate(probe), pxs = found.filter(f => f.lvl === 'px'), inks = found.filter(f => f.lvl === 'ink');
    if (inks.length) { const img = png(await p.screenshot({ type: 'png' })); for (const f of inks) { const m = inkOffset(img, f), d = m && m.d;
      // тісно: зсув ≥ 0,5 px і знак ближче 3 px до краю — «торкається верхівки» («/» у 18 px: 3 ⟂ 4 px, Konst побачив, AE S102); інакше ⚠ від 1 px.
      // 0,5 без тісноти — межа точності знімка ×2 («K» із зазорами 5 / 6 px давав 0,5)
      if (m == null || !(Math.abs(d) >= 1 || (Math.abs(d) >= 0.5 && m.gap <= 3))) { f.lvl = 'ok'; continue; }
      f.lvl = '⚠'; f.msg = `знак зсунутий ${d < 0 ? 'вгору' : 'вниз'} на ${Math.abs(d).toFixed(1)} px від центру своєї кнопки, до краю ${m.gap} px (пікселі «чорнила», не рамка шрифту) — вирівняти: line-height / padding, не на око`; } }
    if (pxs.length) { const img = png(await p.screenshot({ type: 'png' })); for (const f of pxs) { const m = ringContrast(img, f); if (m == null) { f.lvl = 'ⓘ'; continue; }
      // допуск 0,15 — похибка кільця (згладжування, сусідні пікселі): ✗ лише явно нижче порогу, «на межі» — ⚠ (замір QR CC-17: 4,33–4,39 на межі, 4,07 і 2,52 — вади)
      if (m < f.need - 0.15) { f.lvl = '✗'; f.msg = `контраст ${m.toFixed(2)}:1 < ${f.need}:1 — погано читається (фон — градієнт, заміряно пікселем)`; }
      else if (m < f.need) { f.lvl = '⚠'; f.msg = `контраст ${m.toFixed(2)}:1 — на межі ${f.need}:1 (фон — градієнт, пікселем ± 0,15) — глянь очима`; } else f.lvl = 'ok'; } }
    for (const f of found.filter(f => f.lvl !== 'ok')) { delete f.rect; delete f.fg; delete f.need; res.push({ ...f, state: st ? `стан ${i}` : 'початковий' }); }
    if (scope) for (const f of await p.evaluate(leaks, scope)) res.push({ ...f, state: st ? `стан ${i}` : 'початковий' });   // 30. чуже правило
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
    // AE S103 (24.10.2026, AE-SPEED): паузи 400/350/200/350 мс на кнопку (з першої версії, «довше за будь-який перехід») — 1,3 с × 40 кнопок × стан × тема.
    //   Перевіряється КІНЦЕВИЙ вигляд, не рух → на час натискання й наведення переходи вимкнено (як Playwright animations:'disabled' — домотує
    //   до кінця; itechguides · macmyths, 24.10.2026), і досить двох кадрів. Анімації (@keyframes) не чіпаємо — за два кадри вигляд уже інший.
    //   Стиль не застосувався (CSP сторінки тощо — перевіряємо самим transition-duration) → старі паузи: зуби не губляться за жодних умов.
    const fz = await p.evaluate(() => { try { const s = new CSSStyleSheet(); s.replaceSync('*,*::before,*::after{transition-duration:0s!important;transition-delay:0s!important}');
      document.adoptedStyleSheets = [...document.adoptedStyleSheets, s]; window.__uilFz = s;
      const t = document.createElement('i'); t.style.transition = 'opacity 9s'; document.body.appendChild(t); const ok = getComputedStyle(t).transitionDuration === '0s'; t.remove(); return ok; } catch { return false; } });
    const settle = ms => fz ? p.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))) : p.waitForTimeout(ms);
    const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
    for (let j = 0; j < Math.min(sig.length, 40); j++) {
      const el = p.locator(`[data-uil-press="${j}"]`);
      // вигляд = сама кнопка + її підкладка ::before + перший вкладений елемент (стиск часто на них: квадратик галочки, капсула в полі); колір тексту — ні: браузер сам фарбує посилання на :active
      const look = () => el.evaluate(e => [getComputedStyle(e), getComputedStyle(e, '::before'), e.firstElementChild && getComputedStyle(e.firstElementChild)].filter(Boolean).map(s => [s.transform, s.backgroundColor, s.boxShadow, s.opacity, s.filter].join('|')).join('#'));
      let nodeId; try { ({ nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: `[data-uil-press="${j}"]` })); } catch { continue; }
      if (!nodeId) continue;
      const before = await look();
      await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: ['active'] }); await settle(400);   // довше за будь-який перехід відгуку
      const css = await look();
      await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: [] }); await settle(350);
      // і JS-натискання (кукбук A67: клас .pressing на pointerdown) — синтетична подія без кліку
      await el.evaluate(e => e.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerType: 'touch', isPrimary: true }))); await settle(200);
      const js = await look();
      await el.evaluate(e => e.dispatchEvent(new PointerEvent('pointercancel', { bubbles: true, pointerType: 'touch', isPrimary: true }))); await settle(350);
      if (before === css && before === js) res.push({ lvl: '⚠', kind: 'натискання', where: sig[j].toLowerCase(), msg: 'на натискання вигляд не змінюється (ні :active, ні JS pointerdown) — палець не відчуває кнопку; рецепт — кукбук A67', state: st ? `стан ${i}` : 'початковий' });
    }
    // 35. наведення (пропуск Konst AE S96, 20.10.2026 з ПК: «рядок під курсором ледь помітний… кнопки не мають ховера взагалі») — лише ПК (ширина ≥ 1024: миша).
    //     :hover примусово (CSS.forcePseudoState, як :active вище); вигляд = тло · межа · тінь · колір · підкреслення · обведення. Не змінився → ⚠ «без наведення»;
    //     змінилось лише тло, і нове до старого < 1,12:1 (на тлі батька) → ⚠ «ледь видно». Поріг — замір AE: #FFFEF6 на білому 1,01 (Konst: «ледь помітно»), #EFEEE8 — 1,16 (видно).
    //     WCAG наведення сам не нормує (1.4.11 — фокус і стан; accessibleweb.com «hover state contrast», 20.10.2026: для наведення радять виразне тло або межу).
    //     Примусовий стан ≠ справжня миша (WebKit 199165: правила з :not(:hover)) — тому лише ⚠, не ✗.
    if (width >= 1024) {
      const hv = await p.evaluate(() => { const seen = new Set(), out = [];
        for (const e of document.querySelectorAll('a[href],button,[role=button],select,input:not([type=hidden]):not([type=checkbox]):not([type=radio]),textarea')) { const s = getComputedStyle(e); if (s.display === 'none' || !e.getClientRects().length) continue;
          e.scrollIntoView({ block: 'center', behavior: 'instant' }); const r = e.getBoundingClientRect();
          if (!r.width || !r.height || s.visibility === 'hidden' || e.disabled || e.closest('[hidden]')) continue;
          const k = e.tagName + '.' + [...e.classList].sort().join('.'); if (seen.has(k)) continue;
          const c = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (!c || !(c === e || e.contains(c))) continue;
          seen.add(k); e.dataset.uilHover = out.length; out.push(k); }
        return out; });
      const lumN = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
      const crN = (x, y) => { const a = lumN(x), b = lumN(y); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };
      for (let j = 0; j < Math.min(hv.length, 40); j++) {
        const el = p.locator(`[data-uil-hover="${j}"]`);
        const look = () => el.evaluate(e => { const rg = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return [0, 0, 0, 0]; const v = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [v[0], v[1], v[2], v[3] ?? 1]; };
          let g = e.parentElement, gc = [255, 255, 255, 1]; while (g) { const x = rg(getComputedStyle(g).backgroundColor); if (x[3] > 0.5) { gc = x; break; } g = g.parentElement; }
          const s = getComputedStyle(e); return { bg: rg(s.backgroundColor), ground: gc, sh: s.boxShadow, rest: [s.borderTopColor, s.borderBottomColor, s.color, s.textDecorationLine, s.outlineStyle, s.backgroundImage, s.filter, s.transform].join('|') }; });
        let nodeId; try { ({ nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: `[data-uil-hover="${j}"]` })); } catch { continue; }
        if (!nodeId) continue;
        const before = await look();
        await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: ['hover'] }); await settle(300);
        const after = await look();
        await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: [] });
        const on = (c, g) => { const a = c[3]; return [c[0] * a + g[0] * (1 - a), c[1] * a + g[1] * (1 - a), c[2] * a + g[2] * (1 - a)]; };
        const b0 = on(before.bg, before.ground), b1 = on(after.bg, after.ground), shSame = before.sh === after.sh, same = before.rest === after.rest && shSame, bgSame = b0.every((v, q) => Math.abs(v - b1[q]) < 1);
        // AE S107 (пропуск Konst: «ховер ледь помітний» — плитка, лише тінь rgba(…,.08)): змінилась лише тінь, і найтемніша її частина прозоріша за 0,12 → «ледь видно»
        const shA = (after.sh.match(/rgba?\([^)]*\)/g) || []).map(c => { const v = c.slice(c.indexOf('(') + 1, -1).split(/[ ,/]+/).filter(Boolean).map(Number); return v[3] ?? 1; });
        if (!shSame && before.rest === after.rest && bgSame && shA.length && Math.max(...shA) < 0.12) { res.push({ lvl: '⚠', kind: 'наведення', where: hv[j].toLowerCase(), state: st ? `стан ${i}` : 'початковий', msg: `наведення ледь видно: змінюється лише тінь з прозорістю ${Math.max(...shA).toFixed(2)} (< 0,12) — дай підйом (тінь ≥ 0,2 або зсув) чи межу` }); continue; }
        if (same && bgSame) res.push({ lvl: '⚠', kind: 'наведення', where: hv[j].toLowerCase(), state: st ? `стан ${i}` : 'початковий', msg: 'на наведення мишею вигляд не змінюється — на ПК не видно, що це можна натиснути (тло на тон темніше, межа або підкреслення)' });
        else if (same && crN(b0, b1) < 1.12) res.push({ lvl: '⚠', kind: 'наведення', where: hv[j].toLowerCase(), state: st ? `стан ${i}` : 'початковий', msg: `наведення ледь видно: тло змінюється лише на ${crN(b0, b1).toFixed(2)}:1 (< 1,12) — помітніше тло або межа` });
      }
    }
    if (fz) await p.evaluate(() => { document.adoptedStyleSheets = document.adoptedStyleSheets.filter(s => s !== window.__uilFz); });   // №40 дивиться справжні кадри — переходи назад
    // 40. підказка стрибає (пропуск Konst AE S101, 22.10.2026 з ПК: «натискаю на букву і — на мить зліва з'являється табличка й зникає»).
    //     Кнопка з popovertarget → клік → запис кадрів (requestAnimationFrame) прямокутника підказки: перший ВИДИМИЙ відкритий кадр далі ніж 4 px
    //     від останнього → ✗. Причина в AE: позиція ставилась у «toggle», а браузер шле його вже після показу (MDN «Using the Popover API», 22.10.2026).
    //     Лік — ставити до показу (CSS anchor positioning: anchor() / position-area; Chrome «Introducing the popover API») або ховати до місця
    //     (visibility:hidden, доки «toggle» не поставив — так у AE). Справжні кадри, не примусовий стан — тому ✗.
    {
      const pv = await p.evaluate(() => { const out = [];
        for (const b of document.querySelectorAll('[popovertarget]')) { const t = document.getElementById(b.getAttribute('popovertarget')); const r = b.getBoundingClientRect();
          if (!t || !r.width || !r.height || b.disabled || getComputedStyle(b).visibility === 'hidden' || t.matches(':popover-open')) continue;
          const c = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (!c || !(c === b || b.contains(c))) continue;
          b.dataset.uilPop = out.length; out.push(b.tagName.toLowerCase() + (b.id ? '#' + b.id : '') + '[popovertarget=' + t.id + ']'); if (out.length >= 8) break; }
        return out; });
      for (let j = 0; j < pv.length; j++) {
        const fr = await p.evaluate(j => new Promise(done => { const b = document.querySelector(`[data-uil-pop="${j}"]`), t = document.getElementById(b.getAttribute('popovertarget')), fr = [];
          const shot = () => { const r = t.getBoundingClientRect(), s = getComputedStyle(t); fr.push({ open: t.matches(':popover-open'), vis: s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 0, x: Math.round(r.left), y: Math.round(r.top) }); };
          let n = 0; const tick = () => { shot(); if (++n < 8) requestAnimationFrame(tick); else { try { t.hidePopover(); } catch {} done(fr); } };
          b.click(); shot(); requestAnimationFrame(tick); }), j);
        const seen = fr.filter(f => f.open && f.vis);
        if (seen.length > 1) { const a = seen[0], z = seen[seen.length - 1], d = Math.round(Math.hypot(a.x - z.x, a.y - z.y));
          if (d > 4) res.push({ lvl: '✗', kind: 'підказка стрибає', where: pv[j], state: st ? `стан ${i}` : 'початковий', msg: `видима підказка спершу в (${a.x}, ${a.y}), потім стрибає на ${d} px до (${z.x}, ${z.y}) — блимає на краю екрана; ставити до показу (CSS anchor positioning) або ховати, доки не на місці (visibility:hidden до «toggle»)` }); }
      }
    }
    await cdp.detach();
    if (i === 0 && !(await p.evaluate(() => /touchstart/.test([...document.scripts].map(x => x.textContent).join(' ')) || document.body.hasAttribute('ontouchstart'))))
      res.push({ lvl: '⚠', kind: 'натискання', where: 'сторінка', msg: 'нема слухача touchstart — у Safari iOS :active на дотик не спрацює (додай document.addEventListener(\'touchstart\', () => {}, { passive: true }))', state: '' });
  }
  for (const e of errs) res.push({ lvl: '✗', kind: 'JS', where: 'консоль', msg: e.slice(0, 160), state: '' });
  for (const e of [...new Set(dlg)]) res.push({ lvl: '✗', kind: 'нативне вікно', where: 'сторінка', msg: `${e.slice(0, 80)} — вікно браузера (prompt / alert / confirm) посеред застосунку: поле чи шіт у мові продукту`, state: '' });
  await ctx.close(); return res;
}

// AE S103 (AE-SPEED): теми — паралельно, контекстами одного браузера (BrowserStack «waitForTimeout», 24.10.2026: ізоляція — контекст, не процес);
//   --themes light|dark — продукт з однією схемою (AE: prefers-color-scheme у сайті нема, темний прохід = копія світлого). Типово — обидві.
//   browser — спільний (самоперевірка: один запуск Chromium на всі сторінки замість запуску на кожну).
async function run(target, states, width, { browser, scope = SCOPE, themes = THEMES } = {}) {
  const own = !browser; const b = browser || await (await pw()).chromium.launch();
  const out = { light: [], dark: [] };
  if (SERIAL) for (const t of themes) out[t] = await lint(target, states, width, t, b, scope);   // --serial — діагностика (wsd 1.21 п.3; як Playwright --workers=1): паралельний дав ✗, послідовний ні → вада під навантаженням
  else await Promise.all(themes.map(async t => { out[t] = await lint(target, states, width, t, b, scope); }));
  if (own) await b.close();
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
  // AE S103 (AE-SPEED): один браузер на всі сторінки й черга по 4 (було — запуск Chromium на кожну сторінку, послідовно, ≈ 10 хв).
  //   Вивід — у порядку випадків, незалежно від того, хто закінчив першим.
  const d = mkdtempSync(join(tmpdir(), 'uilint-')); const B = await (await pw()).chromium.launch(); const t0 = Date.now();
  const page = (x, n) => { const f = join(d, n + '.html'); writeFileSync(f, SELF.replace('BAD', x)); return 'file://' + f; };
  const R = (html, n, width = 390, scope = '') => run(page(html, n), [], width, { browser: B, scope }).then(r => [...r.light, ...r.dark]);
  const T = [];   // кожен випадок — () => [рядок, вада?]
  T.push(async () => { const cl = (await R('', 'clean')).filter(x => x.lvl !== 'ⓘ');
    return [(cl.length ? '✗' : '✓') + ` чиста сторінка → тиша (${cl.length ? cl.map(x => x.kind + ': ' + x.msg).join(' | ') : '0'})`, !!cl.length]; });
  T.push(async () => { // AE S100: хибне спрацювання — мала ціль ПІД відкритим модальним вікном інертна, «тап» мовчить; та сама кнопка без вікна — ✗ (зуби)
    const [pm, pn] = await Promise.all([R(`<button style="width:18px;height:18px;padding:0">i</button><dialog id=md><button style="min-height:44px;min-width:120px">Гаразд</button></dialog><script>md.showModal()</script>`, 'modal'),
      R(`<button style="width:18px;height:18px;padding:0">i</button>`, 'nomodal')]);
    const tm = pm.some(x => x.kind === 'тап' && x.lvl === '✗'), tn = pn.some(x => x.kind === 'тап' && x.lvl === '✗');
    return [(!tm && tn ? '✓' : '✗') + ` мала ціль під модальним вікном → тиша; без вікна → «тап» ✗ (${tm} · ${tn})`, !(!tm && tn)]; });
  T.push(async () => { // AE S109: білий текст на синьому градієнті кнопки з дочірнім елементом — кільце довкола тексту → тиша (було 1,00:1 — кільце довкола рамки кнопки)
    const g = (await R(`<div class=card><button style="display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 14px;border:0;border-radius:999px;background:linear-gradient(180deg,#0E8CC6,#0071A3);color:#fff;font:600 15px system-ui">Усі<i style="font-style:normal;margin-left:5px">21</i></button></div>`, 'gradbtn')).filter(x => x.kind === 'контраст' && x.lvl === '✗');
    return [(!g.length ? '✓' : '✗') + ` білий на синьому градієнті кнопки → тиша (${g.map(x => x.msg).join(' | ') || '0'})`, !!g.length]; });
  T.push(async () => { // AE S109: випадне меню (role=menu, absolute) виходить за картку → «вилазить» мовчить; той самий блок без ролі — ✗ (зуби)
    const box = r => `<div class=card style="position:relative;height:60px"><div ${r} style="position:absolute;top:40px;left:20px;width:200px;height:160px;border-radius:12px;border:1px solid #ddd;background:#fff">Пункт</div></div>`;
    const [pm, pn] = await Promise.all([R(box('role=menu'), 'popmenu'), R(box(''), 'popnone')]);
    const m = pm.some(x => x.kind === 'вилазить'), n = pn.some(x => x.kind === 'вилазить');
    return [(!m && n ? '✓' : '✗') + ` випадне меню за карткою → тиша; той самий блок без ролі → «вилазить» (${m} · ${n})`, !(!m && n)]; });
  T.push(async () => { // AE S101: та сама підказка, але схована до місця (visibility:hidden, доки «toggle» не поставив) → «підказка стрибає» мовчить (зуби в обидва боки)
    const jf = (await R(`<style>.tp{position:fixed;inset:auto;margin:0;padding:8px;border:1px solid #888;background:#fff}.tp:popover-open:not([data-placed]){visibility:hidden}</style><div class=card><button popovertarget=tp1 style="min-height:44px;min-width:120px;margin-left:200px">i</button><div popover id=tp1 class=tp>Пояснення</div></div><script>document.addEventListener('toggle',e=>{const t=e.target;if(e.newState!=='open'){t.removeAttribute('data-placed');return}const r=document.querySelector('[popovertarget=tp1]').getBoundingClientRect();t.style.left=r.left+'px';t.style.top=(r.bottom+6)+'px';t.setAttribute('data-placed','')},true)</script>`, 'popfixed')).some(x => x.kind === 'підказка стрибає');
    return [(!jf ? '✓' : '✗') + ` підказка, схована до місця → «підказка стрибає» мовчить (${jf})`, jf]; });
  T.push(async () => { // AE S101 · В-211: «інструкція в повідомленні» — зуби кожної ознаки окремо (а–д) і тиша на правильному: одне речення без порад; клавіші в «i» — законні
    const tip = `<div popover id=tq>Значення правляться прямо в клітинках таблиці каталогу. <kbd>Esc</kbd> — повернути як було</div>`;
    const cases = [['а клавіша', `<span role=status>Збережено. Ctrl+S — опублікувати.</span>`], ['б передумали', `<div class=toast>Позиція зникне після «Опублікувати». Передумали — «↶ Повернути»</div>`],
      ['в ✕', `<div class="msg e">✕ <span>опис настрою містить цифру</span></div>`], ['г два речення', `<span role=alert>Ціна — число. Наприклад 188 або 188,50 гривень.</span>`],
      ['д повтор «i»', `<span role=status>Значення правляться прямо в клітинках таблиці каталогу.</span>${tip}`]];
    const hits = await Promise.all(cases.map(([n, h]) => R(`<div class=card>${h}</div>`, 'msg-' + n.split(' ')[0]).then(r => r.some(x => x.kind === 'інструкція в повідомленні'))));
    const miss = cases.filter((_, i) => !hits[i]).map(([n]) => n), ok = cases.length - miss.length;
    const gf = (await R(`<div class=card><span role=alert>Назва не може бути порожньою.</span>${tip}</div>`, 'msg-good')).some(x => x.kind === 'інструкція в повідомленні');
    return [(ok === cases.length && !gf ? '✓' : '✗') + ` «інструкція в повідомленні»: ознаки а–д ${ok}/${cases.length}${miss.length ? ' (не спіймано: ' + miss.join(', ') + ')' : ''}, правильне повідомлення + клавіші в «i» → тиша (${!gf})`, !(ok === cases.length && !gf)]; });
  for (const [k, html] of Object.entries(DEFECTS)) T.push(async () => {
    const hit = (await R(html, 'd' + Object.keys(DEFECTS).indexOf(k), k.trim() === 'наведення' ? 1280 : 390, k.trim() === 'чуже правило' ? '.isl' : '')).some(x => x.kind === k.trim() && x.lvl !== 'ⓘ');
    return [(hit ? '✓' : '✗') + ` підкинуто «${k}» → спіймано`, !hit]; });
  const out = new Array(T.length); let next = 0;
  await Promise.all(Array.from({ length: Math.min(4, T.length) }, async () => { while (next < T.length) { const j = next++; out[j] = await T[j](); } }));
  await B.close(); let bad = 0; for (const [line, b] of out) { console.log(line); bad += b; }
  console.log(`─── ui_lint selftest: ${T.length - bad}/${T.length} · ${Math.round((Date.now() - t0) / 1000)} с ───`); process.exit(bad ? 1 : 0);
}
if (!a[0]) { console.log('node ui_lint.mjs <url|файл> [--state "<js>"]… [--repo <тека>] [--width 390] [--height 844] [--themes light|dark|both] [--serial] [--json] | selftest'); process.exit(2); }
let target = a[0]; if (!/^\w+:\/\//.test(target)) target = 'file://' + resolve(target);
const states = [], opt = {}; for (let i = 1; i < a.length; i++) { if (a[i] === '--state') states.push(a[++i]); else if (a[i] === '--repo') opt.repo = a[++i]; else if (a[i] === '--width') opt.width = +a[++i]; else if (a[i] === '--height') HEIGHT = +a[++i]; else if (a[i] === '--scope') SCOPE = a[++i]; else if (a[i] === '--json') opt.json = true; else if (a[i] === '--baseline') opt.base = a[++i]; else if (a[i] === '--ready') READY = a[++i]; else if (a[i] === '--serial') SERIAL = true; else if (a[i] === '--themes') { const v = a[++i]; THEMES = v === 'both' ? ['light', 'dark'] : [v]; if (!THEMES.every(x => x === 'light' || x === 'dark')) { console.error('--themes light|dark|both'); process.exit(2); } } }
const T0 = Date.now(); const r = await run(target, states, opt.width || 390);
const acc = []; const af = opt.repo && join(resolve(opt.repo), '.ui-lint-accept');
if (af && existsSync(af)) for (const l of (await import('node:fs')).readFileSync(af, 'utf8').split('\n')) { const [k, w, why] = l.split('|').map(x => (x || '').trim()); if (k && w && !k.startsWith('#')) acc.push({ k, w, why }); }
for (const t of ['light', 'dark']) for (const f of r[t]) { const m = acc.find(a => a.k === f.kind && f.where.includes(a.w)); if (m && f.lvl !== 'ⓘ') { f.msg += ` — прийнято: ${m.why}`; f.lvl = 'ⓘ'; f.acc = true; } }
const say = (...m) => (opt.json ? console.error : console.log)(...m);   // --json: stdout — лише JSON (S97: рядок підсумку ламав файл бази)
// --baseline <файл>: база відомих ✗ (Android Lint · SwiftLint --use-baseline; ключ — вид + елемент, не рядок: вставка рядків вище не робить старе «новим» —
// claudeissues 82589, 07.2026). Файлу нема → записати поточні ✗ і вийти; є → блокує лише ✗ поза базою, виправлене з бази — назвати. Перезапис — лише руками (rm).
if (opt.base) { const key = f => `${f.kind}|${f.where}`, cur = [...new Set(['light', 'dark'].flatMap(t => r[t].filter(f => f.lvl === '✗').map(key)))];
  if (!existsSync(opt.base)) { writeFileSync(opt.base, JSON.stringify(cur, null, 1)); say(`✓ база ui_lint записана: ${cur.length} ✗ → ${opt.base} (до правки; після — той самий --baseline)`); process.exit(0); }
  let B = JSON.parse((await import('node:fs')).readFileSync(opt.base, 'utf8')); if (!Array.isArray(B)) B = ['light', 'dark'].flatMap(t => (B[t] || []).filter(f => f.lvl === '✗').map(key));   // база — масив ключів або звіт --json
  const base = new Set(B), gone = [...base].filter(k => !cur.includes(k));
  for (const t of ['light', 'dark']) for (const f of r[t]) if (f.lvl === '✗' && base.has(key(f))) { f.lvl = 'ⓘ'; f.acc = true; f.msg += ' — з бази (було до правки)'; }
  if (gone.length) say(`ⓘ виправлено з бази: ${gone.length} (${gone.slice(0, 3).join(' · ')}${gone.length > 3 ? ' …' : ''})`); }
let x = 0, w = 0;
for (const t of ['light', 'dark']) {
  const seen = new Set(); const rows = r[t].filter(f => { const k = f.lvl + f.kind + f.where + f.msg; if (seen.has(k)) return false; seen.add(k); return true; });
  x += rows.filter(f => f.lvl === '✗').length; w += rows.filter(f => f.lvl === '⚠').length;
  if (!opt.json) { console.log(`— ${t === 'light' ? 'світла' : 'темна'} тема`); for (const f of rows.filter(f => f.lvl !== 'ⓘ')) console.log(`  ${f.lvl} ${f.kind} · ${f.state || ''} · ${f.where} — ${f.msg}`);
    for (const f of rows.filter(f => f.acc)) console.log(`  ⓘ ${f.kind} · ${f.where} — ${f.msg}`);
    const n = rows.filter(f => f.lvl === 'ⓘ' && !f.acc).length; if (n) console.log(`  ⓘ не виміряно контраст на ${n} елементах (градієнт / картинка) — глянь очима`); }
}
if (opt.json) console.log(JSON.stringify(r, null, 1));
say(`─── ui_lint: ✗ ${x} · ⚠ ${w} · екранів ${states.length + 1} (початковий + станів ${states.length}) × ${THEMES.length === 2 ? '2 теми' : 'тема ' + (THEMES[0] === 'light' ? 'світла' : 'темна')} · ${Math.round((Date.now() - T0) / 1000)} с ───`);
if (opt.repo && !x) {   // позначка для воріт: той самий хеш диффу UI, що рахує ui-review-gate
  const hx = execFileSync('bash', [join(here, 'hooks/ui-review-gate.sh'), 'hash', resolve(opt.repo)], { encoding: 'utf8' }).trim();
  if (hx) { writeFileSync(`/tmp/lens-uilint-${hx}`, `${new Date().toISOString()} ✗0 ⚠${w} ${target} states=${states.length || 1} themes=${THEMES.join('+')}\n`); say(`✓ позначка ui_lint для диффу ${hx.slice(0, 8)} — ворота огляду приймуть done`); }
}
process.exit(x ? 1 : 0);
