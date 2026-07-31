# Фармастор v2 — session summary · b10 SHIP + b11 PLAN (handoff)

**Продукт:** Фармастор замовлення v2 (standalone, NOT Lens family — техн-патерни iOS/PWA застосовні)
**База b11:** `Фармастор_замовлення_v2_port_b10.html` (1173 р., ~100 КБ) — у outputs цього чату
**Версія:** `APP_BUILD = { ver:'v2.4.0', build:'node8.b10', date:'16.07.2026' }` (об'єкт, wsd 10.6)
**Дата:** 16.07.2026

---

## 1 · SHIPPED у b10 (device-verified ✓)

Node8-хвіст + §4-контракт реалізовано і **підтверджено на пристрої** (Konst XS iOS18 + 15Pro iOS26):
- **Excel deep-link** — FILL CTA-row **2.5:1** (`.btn-copy` + `.btn-form` anchor, material LOCK обидві теми) + Home ••• рядок. `<a href=ORDER_FORM_URL target=_blank rel=noopener>` → **відкриває Excel-застосунок** ✓. Єдиний `ORDER_FORM_URL` → усі `.js-order-link` (href в init).
- **CSV context-split** — `openSheet` детектить `#s-fill.active` → лейбл «Ця аптека»/«Усі дані·N аптек»; `exportCSV` сам детектить scope. `;` + UTF-8 BOM + екранування; share→download фолбек. **Працює** (single=6КБ, відкрився в Excel) ✓.
- **About sheet (A58)** — handoff 120ms, version/build/date з APP_BUILD-об'єкта, `.tgpill`. Scrim `closeSheets()` закриває обидва ✓.
- Матеріал-кнопки, count-бар при повному (83/83) — читаються ✓.

**§4 док-патч** віддано окремо (`MASTER_LOCK_§4_update_b11.md`) — Konst має вставити у MASTER_LOCK.

---

## 2 · LOCKED рішення для b11 (усе device-погоджено в цьому чаті)

### 2.1 Меню — A58 grouped-redesign (harness device✓)
Пласкі `.sheet-item` → **grouped-cards + eyebrow-секції**. Порядок (згори):
- **eyebrow ВИГЛЯД** → gcard: **Тема — сегмент 3-в-1** (Авто / Світла / Темна), активний = accent-заливка (dark = `linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%))`).
  - **+ПРУЖИНА (b11 нове, Konst):** ковзний thumb під активним сегментом з `--spring` — **порт патерну анімованого перемикача з Drive Lens** (є і в QR). Легкий spring-slide. → device-звірка руху (можливо міні-motion-harness АБО прямий порт Drive-значень; рекоменд. порт + device-look).
- **eyebrow ДІЇ** → gcard: **«Excel онлайн»** (external-icon + саб «Форма замовлення для вставки» + `.doact` «Відкрити») · **«Експорт CSV»** (download-icon + context-саб + `.doact` «CSV»).
- **eyebrow СЕАНС** → gcard: **«Про додаток»** (info + chevron → About) · **«Очистити …»** (danger, **ОСТАННІМ** — щоб не влучити ненароком).

Гарнес-структура — файл `Farmastor_filltail_harness_v1.html` (outputs). Класи A58: `.eb` `.gcard` `.mi` `.mi-ic` `.mi-tx` `.doact` `.mi-chev` `.thseg`.

### 2.2 Count-бар track — A45-манифест per-theme (device✓, values LOCKED)
Діра: трек `--surface-3` = хедер `--bg` (Δ=1) → порожній трек невидимий; QR-рецидив «низ каналу зникає». Розв'язано per-theme (різні важелі):

**Селектори в b10:** `.progress` (трек, р.102) · `[data-theme="dark"] .progress` (р.103) · `.progress > i`/`#fillBar` (fill, р.104) · A69-мірор (р.403) · markup р.461 · width-апдейт р.1083.

**Порт-CSS @ locked values:**
```css
/* LIGHT трек (border+inset, і верх і низ каналу читаються) */
.progress{flex:1;min-width:80px;height:6px;border-radius:6px;overflow:hidden;
  background:color-mix(in srgb,var(--bg-soft),var(--border) 37%);              /* LtrkMix 37 */
  border:1px solid color-mix(in srgb,var(--border),transparent 45%);          /* Lborder 55 */
  box-shadow:inset 0 1px .5px rgba(20,50,42,.16),                             /* Linset .5 · LinsetOp 16 */
             inset 0 -1px 0 rgba(20,50,42,.06)}                               /* LfloorOp 6 */
.progress > i{display:block;height:100%;border-radius:6px;background:var(--accent);width:0}
/* DARK трек (tone-lift + ridge; Dfloor 0) + fill sat/lit */
[data-theme="dark"] .progress{background:color-mix(in srgb,var(--bg),#fff 16%);border:none;   /* Dlift 16 */
  box-shadow:inset 0 1px 0 rgba(255,255,255,.16)}                            /* Dridge .16 */
[data-theme="dark"] .progress > i{background:hsl(163 52% 46%)}               /* DfillS 52 · DfillL 46 */
```
**A69-паритет:** мірорити обидва dark-правила у `@media(prefers-color-scheme:dark){:root:not([data-theme="light"]) …}` (замінити стару р.403 `.progress{background:#0f1714}` + додати `.progress>i`).

### 2.3 CSV — колонки (LOCKED)
- `Норма → MSL` (збіг із застосунком «MSL N»).
- Прибрати SKU-`Kode` (Konst: шум, не інформативний).
- `Назва → Товар` (щоб не плутати з аптекою).
- **ця аптека (FILL):** `Товар;Категорія;MSL;Залишок` (Proxima в імені файлу).
- **усі дані (Home):** `Proxima;Місто;Адреса;M;Товар;Категорія;MSL;Залишок;Дата`.
- Механіка (BOM, `;`, екранування, share→download, guard «немає даних») — БЕЗ змін. Правити лише заголовки+колонки у `csvSingle`/`csvAll` (р.~1108–1135) + `normOfVisit` лишається.

### 2.4 Очистити — context-aware + confirm (LOCKED scope)
- **Заміна стуба** р.491 (зараз `onclick="closeSheet()"`, нічого не робить).
- **Scope (device-погоджено):** FILL → скидає **поточний підрахунок цієї аптеки** (today-visit vals; історія `visits[]` ЛИШАЄТЬСЯ — потрібна §5.1 Динаміці); Home → **повний вайп** `ST.phs`.
- **Лейбли (людяні):** FILL = **«Очистити підрахунок»** (альт «Очистити заповнені дані»); Home = **«Очистити всі дані»». Короткий рядок, БЕЗ довгого сабу.
- **Confirm-діалог** (міні-модал/центр-шіт): коротке людське пояснення + **[Скасувати] / [Видалити]** (Видалити — `--crit` червона). Тап рядка → діалог (не одразу дія).
- Реалізація: детект `#s-fill.active` (як CSV/label). FILL-clear = скинути `todayVisit(curPx).vals={}` (або видалити today-visit) + `saveST` + `renderFill`. Home-clear = `ST.phs={}` + `saveST` + `renderHome`.
- **Чому не повний вайп на FILL:** §5.1 «Динаміка» читатиме `visits[]` історію — FILL-скид не має її зносити.

### 2.5 Дрібні продукт-фікси (LOCKED)
- **About:** «Створив» → **«Розробник»** (рядок кредиту, DOM `.about-credit`).
- **Excel-прес:** зараз `.btn-form.is-pressed{scale(.96)}` = як копі, АЛЕ прес «з'їдає» перехід у Excel-застосунок. Фікс: лишити .96 (рівень копі) + `-webkit-tap-highlight-color:transparent` на `.btn-form` (прибрати iOS gray-flash, щоб коротка мить пресу читалась). Пояснити Konst: після тапу PWA йде у фон → spring-return грає при поверненні; це природа anchor-навігації, не баг.

---

## 3 · b11 CODE CHECKLIST (порядок; код на команду; harness→device для руху сегмента)
1. **Count-бар track** — порт §2.2 CSS (light+dark+A69). Найпростіше, ізольовано.
2. **CSV колонки** §2.3 — заголовки+рядки `csvSingle`/`csvAll`.
3. **About «Розробник»** + **Excel-прес** §2.5.
4. **Меню A58-редизайн** §2.1 — новий DOM+CSS (`.eb`/`.gcard`/`.mi`/`.thseg`), «Excel онлайн», порядок, Про-вище-Очистити.
5. **Тема-сегмент пружина** §2.1 — thumb+spring (порт Drive Lens; device-звірка руху; можливо міні-harness).
6. **Очистити context-aware + confirm-діалог** §2.4 — реальна логіка + модал.
→ бамп `APP_BUILD.build = 'menu.b11'`, ім'я `..._port_b11.html`.

---

## 4 · REQUIRED READING для b11 (ЛИШЕ це — берегти контекст)

**Work_Standard.md (wsd):** Кластер 1 (сесійний протокол + маркер 1.2), Кластер 3 (pre-patch: grep live-code 12.1, ls-verify), Кластер 10 (валідація: node --check · tag-balance · grep-anchors · absent≠0 · diff-scope), Кластер 11 (структура патча). *(2, 5, 6 — пропустити.)*

**Lens_iOS_cookbook.md:** **A58** (grouped-card sheet + eyebrow) · **A54** (+ Drive Lens patterns — анімований сегмент-перемикач з пружиною) · **A67** (pointer-press) · **A45** (material lever manifest — довідка, count-бар вже locked §2.2) · **A69** (dark dual-selector паритет). *(δ-чіп, решта — не треба.)*

**Фармастор_v2_MASTER_LOCK.md:** §4 (copy/Excel/CSV — + твій §4-док-патч якщо вставив) · §6.1/§6.2 (токени) · §7 (iOS/A69) · §5.1 (чому Очистити-scope береже `visits[]`).

**Продукт:** `Фармастор_замовлення_v2_port_b10.html` (база). **Гарнес-реф:** `Farmastor_filltail_harness_v1.html` (меню-структура + count-бар values).

**Drive Lens (для §2.1 пружини):** знайти патерн анімованого таб/сегмент-перемикача — `Drive_Lens_session_summary_Batch*` (glass tab-bar spring) + Cookbook A54. Читати ТІЛЬКИ коли дійдемо до кроку 5.

---

## 5 · ТОКЕНИ (щоб не грепати; §6.1/§6.2)

**LIGHT:** `--bg:#eef3f1 · --bg-soft:#e4ece9 · --card:#fff · --surface-2:#f4f8f6 · --surface-3:#eef4f1 · --text:#182c28 · --text-2:#3c574f · --muted:#6b8c84 · --border:#d4e5df · --border-subtle:#e1ebe7 · --ok:#1f9d57 · --crit:#c0392b · --warn:#c8811b · --accent:hsl(162 82% 27%) · --accent-soft:hsl(162 64% 88%) · --accent-ink:hsl(162 82% 16%)`

**DARK:** `--bg:#0d1512 · --bg-soft:#151e1a · --card:#18221e · --surface-2:#1c2723 · --surface-3:#212d28 · --text:#e8f0ec · --text-2:#a7c0b8 · --muted:#7c968d · --border:#2a3833 · --border-subtle:#222e29 · --ok:#33c06f · --crit:#e0685c · --warn:#e0a94a · --accent:hsl(163 46% 46%) · --accent-soft:hsl(163 37% 17%) · --accent-ink:hsl(163 46% 68%)`

**--spring:** `cubic-bezier(.34,1.56,.64,1)` · **font:** Manrope

**Material LOCK кнопки (§4.3, device✓):** копі LIGHT `linear-gradient(180deg,color-mix(in srgb,#fff 16%,var(--accent)),var(--accent))` + shadow; копі DARK `linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%))`; форма soft (див. §4 док-патч). Press `.btn-*.is-pressed{scale(.96);dur .06s}`.

**Count-бар LOCKED:** light track `color-mix(bg-soft,border 37%)` + border `color-mix(border,transparent 45%)` + inset .16/floor .06; dark track `color-mix(bg,#fff 16%)` + ridge .16; dark fill `hsl(163 52% 46%)`; light fill `--accent`.

**ORDER_FORM_URL** — у b10 (const, р.~694) + §4 док-патч.

---

## 6 · PENDING device (не блокери)
- Рух тема-сегмента (пружина) — device-звірка при кроці 5.
- Confirm-діалог Очистити — device-погляд (модал vs центр-шіт).
- UL-стрибок Excel PWA→зовні (рідкісний) · CSV share-sheet iOS.

## 7 · ВІДКЛАДЕНО (не b11)
Дуга-кільце схована успіхом (🔴 design, harness-first) · §5.1 метрика shortfall + Динаміка UI · governance-split + мерж A45-дельти (`canon_delta_A45_material_lever_manifest.md`) + §4 у MASTER_LOCK.

---

## 8 · СТАРТОВЕ повідомлення для нового чату (b11)

```
Перед будь-якими діями з кодом/PQ/VBA/патчами — прочитай (wsd 1.1), АЛЕ лише вказані секції (берегти контекст):

1. Work_Standard.md — Кластери 1 (протокол+маркер 1.2), 3 (pre-patch/grep-live 12.1), 10 (валідація), 11 (патч-структура). Решту пропустити.
2. Lens_iOS_cookbook.md — A58 · A54 (+Drive Lens анім-сегмент) · A67 · A45 (довідка) · A69. Решту не читати.
3. Фармастор_v2_MASTER_LOCK.md — §4 · §6.1/§6.2 (токени) · §7 · §5.1.
4. Фармастор_session_summary_v2_b10_ship_b11plan.md — ПОВНИЙ стан + усі locked-значення + b11-чеклист + токени.
5. Продукт-база: Фармастор_замовлення_v2_port_b10.html
6. Гарнес-реф: Farmastor_filltail_harness_v1.html

Маркер навантаження — останнім рядком КОЖНОЇ відповіді (wsd 1.2), дублювати в ask_user_input_v0 (question, «(💬 ~N%)»).
Working-копію (b11 preview/патч/самері) — зберігати в /mnt/user-data/outputs по ходу (wsd 1.6).

ЗАВДАННЯ — Фармастор v2 b10 → b11, порядок (код на команду; §-посилання = самері b10):
1. Count-бар track — порт §2.2 CSS (light border+inset / dark lift+ridge / A69-мірор). Селектори: .progress р.102, [dark] р.103, .progress>i р.104, A69 р.403.
2. CSV колонки §2.3 — Норма→MSL, прибрати SKU-Kode, Назва→Товар. FILL: Товар;Категорія;MSL;Залишок. Home: Proxima;Місто;Адреса;M;Товар;Категорія;MSL;Залишок;Дата. (csvSingle/csvAll р.~1108–1135, механіка без змін.)
3. About «Створив»→«Розробник» + Excel-прес: +-webkit-tap-highlight-color:transparent на .btn-form (§2.5).
4. Меню A58-редизайн §2.1 — grouped-cards+eyebrow (ВИГЛЯД/ДІЇ/СЕАНС), «Excel онлайн», порядок Про-вище-Очистити. Класи .eb/.gcard/.mi/.mi-ic/.mi-tx/.doact/.mi-chev/.thseg (див. Farmastor_filltail_harness_v1.html).
5. Тема-сегмент ПРУЖИНА §2.1 — ковзний thumb+--spring, порт Drive Lens анім-сегмента (Cookbook A54 + Drive_Lens batch summaries). Device-звірка руху (за потреби міні-motion-harness).
6. Очистити context-aware §2.4 — FILL «Очистити підрахунок» (скид today-visit vals, історію лишити) / Home «Очистити всі дані» (вайп ST.phs). Confirm-діалог [Скасувати]/[Видалити]. Замінити стуб р.491.
→ бамп APP_BUILD.build='menu.b11', ім'я ..._port_b11.html.

PENDING device: рух сегмента · confirm-модал вигляд · UL/share iOS.
ВІДКЛАДЕНО: дуга-кільце схована · §5.1 Динаміка UI · governance-мерж.

ПРАВИЛА: подвійне пояснення тех.рішень · без емодзі в UI (SVG/моно) · harness-first для руху · план→підтвердж→код · маркер останнім рядком · валідація перед delivery (node --check · tag-balance · grep-anchors · absent≠0 · diff-scope) · грепати live-code (wsd 12.1), не довіряти самері понад код.
```
