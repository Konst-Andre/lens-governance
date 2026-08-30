# QR Lens — Session Summary: B59 Tab-2 perf-арк — МІКРОСКОП + WEB discovery (harness ще НЕ побудовано)

**Дата:** 09.07.2026 · **Арка:** B58.2 у проді → **perf-арк (Tab-2 ~180 карток)** · discovery-фаза завершена, harness = наступний крок.
**Статус:** корінь grep-підтверджено · мої ранні твердження двічі виправлено мікроскопом · web-пас дав канонічні важелі · **ставка визначена, harness-спека готова, код НЕ починався** (plan→confirm→код, 1.5).

---

## 0. Що це за чат (для наступного)

Discovery-only сесія: **НЕ писали код.** Пройшли методом wsd: grep-before-claim (12.1) → мікроскоп-аудит ВЛАСНИХ тверджень → web best-practice пас → синтез важелів. Наступний чат **будує 3-тестовий harness** (нижче §5) → device-вимір Konst → вибір фіксу → патч B59.

---

## 1. Проблема (два симптоми, ОДИН корінь-родина)

Реальні дані ~180 аптек/SR (видно ~7). Обидва симптоми — на масштабі; на mockup 5-12 було ідеально.

- **Симптом A — select «цегляна».** Тап на картку → анімація вибору фрізить, low-FPS, обидві теми. Найгірше на **зміні вибору** (deselect+select).
- **Симптом B — банер «болісно виштовхує 180».** `selectOutlet` показує банер (candidate-A reveal) → **перша поява дуже неплавна**, пхає всі рядки; далі «більш-менш ок».
- **Позиційність (Konst device):** обираєш **топ**-картку → джанк помітний; обираєш **низ** (170-175, доскролив) → майже гладко. Логіка: банер живе зверху; топ-select = reveal+push У В'ЮПОРТІ; низ-select = reveal поза екраном.
- **Зв'язок A↔B:** select І показ банера — ОДНА подія. Симптоми переплетені.

---

## 2. Мікроскоп — grep-підтверджено (реальний код batch58_2)

**Windowing ВІДСУТНІЙ.** `renderPharmacies` р.1562: `list.innerHTML=outs.map(...)` — усі ~180 `.ph-row` у DOM. `.slice(0,5)` р.1476/1477 = Tab-1 top/focus, НЕ ph-список.

**Per-row paint важкий ×180:**
- `.ph-card` р.627-635 = **5-шаровий стек-градієнт** (contact/gloss/ridge/glass/base) + **3 box-shadow**
- `.ph-back` р.619 = плита, градієнт + `box-shadow 0 4px 10px` + transform-transition 950ms
- `::after` кільце (р.597/643) + `.ph-rank`

**Симптом A — тригер re-raster (select):**
- `.ph-card` р.635 transition містить **`box-shadow .14s`** (box=paint-проп) + **`filter`**
- `.ph-row.is-sel .ph-card` р.645 = **`filter:drop-shadow(...)`** → окремий filter-render-surface + новий stacking-context + re-raster під час concurrent transform-spring (playCardGesture 950ms, р.~2410)
- Механізм: filtered-картка в shared-layer форсить re-composite сусідів; топ = ~170 важких рядків після неї → дорого; низ = мало.

**Симптом B — candidate-A банер (bnrIn р.1172):**
- `.bnr-pin` (р.292) → `.screens` position:absolute@header_h; `.screen.active` отримує **`will-change:transform`** (р.293)
- reveal: банер `height 0→H` main-thread (р.1186) + `.screen.active` **composite `translateY 0→H` 600ms** (р.1188) + `.ph-b-in` шторка
- end-snap (р.1189-1193): `remove('bnr-pin')` → un-pin + un-promote → **180 карток re-raster у main-layer = repaint-спайк у КІНЦІ**
- **форсовані sync layout** на старті: `el.offsetHeight` читання р.1178, 1183
- **candidate-A device-locked на 14 картках** — 180 для цього механізму НЕ тестовано.

### ⚠ ВИПРАВЛЕННЯ моїх ранніх тверджень (мікроскоп зловив ДВІЧІ):
1. **«CV clip» — ПІДТВЕРДЖЕНО фактом** (не гіпотеза). `content-visibility:auto` завжди вмикає `contain:paint` (і на видимих рядках); paint-containment **обрізає ink-overflow** (drop-shadow за боксом, декоративні bleeds) — MDN/CSS-Wizardry/web.dev/W3C. Геометрія bleed: `.ph-back` `--hc-peeky:4` + `box-shadow 0 4px 10px` (~14px нижче боксу) + E2-halo drop-shadow (~2.6px) + spring overshoot scale 1.045 (~2.7px). → CV гарантовано обріже B45 shelf-peek+halo. **АЛЕ:** W3C spec — clip поважає **`overflow-clip-margin`** → `overflow-clip-margin:14px` на CV-рядку може ДОЗВОЛИТИ bleed попри contain:paint (Safari-fidelity = device-питання).
2. **«12000px промоутнутий layer» — ХИБНЕ, знято.** `.screen.active` містить `.scroll-a` (`overflow-y:auto`, р.294) — скролер САМ клипить → промоутнутий layer в'юпорт-розміру, НЕ 12000px. 180-залежність банера — НЕ transform, а **O(180) boundary-кости** (forced sync layout + end-snap un-promote raster). **Наслідок:** CV таки ймовірно допоможе банеру, але через зменшення off-screen layout/paint (boundary-кости), НЕ через «стиснути layer».

---

## 3. Web best-practice пас (web=гіпотези, device=вирок — 14.18)

- **2b канонічний = pseudo-opacity glow** (Tobias Ahlin / SitePoint / StudioLimb, збіжно): не анімуй filter/тінь — тримай glow на `::before` при `opacity:0`, reveal через `opacity` (композит, GPU). StudioLimb прямо: «filter:drop-shadow НЕ на анімованих елементах». Збіжно з нашим A70/A57.
- **filter дорогий + нелокальний:** «rasterize+sample alpha mask», новий stacking-context (css3shapes); W3C: filter має non-local repaint. Конфлікт джерел (частина: «drop-shadow GPU-прискорений») → GPU-виграш лише для СТАТИЧНОГО/ізольованого filter; у нас — concurrent transform + huge layer → «compositor-only = умовна обіцянка» (cr0x). → **device вирішує.**
- **банер candidate-A = вже правильний FLIP** (Paul Lewis/Motion/Josh Comeau: рухати список лише transform). VT НЕ краще (Motion: «VT знімає скріншот+width/height — гірше на багатьох елементах»). 180-cost = boundary layout/paint, не сам transform.
- **cr0x diagnostic:** «paint dominates → reduce paint area / remove filters; compositing dominates → avoid huge layers». «If the fix only works on dev — it's a demo» = наш device-арбітр (1.5/12.9).

---

## 4. Ставка + стратегія (НЕ lock — device-arbitrated)

| Важіль | Лікує | Впевненість | Ризик |
|---|---|---|---|
| **CV + `overflow-clip-margin`** | ОБИДВА (O(180) layout+paint) | середньо-висока | hinges на Safari clip-margin fidelity + **fast-scroll blank-flash** |
| **2b composite-glow** | select filter re-raster | висока | нуль (on-canon A70/A57, матеріал цілий) |
| virtual scroll | обидва назавжди + scroll headroom | резерв | ризик persist-DOM select/sig-guard/banner-pin/stagger/scroll-restore |

**Стратегія хірургічно→ескалація:** дешевий CSS-шлях **CV+clip-margin (+2b комплемент)** ПЕРШИМ. Device підтверджує (а) clip-margin зберігає shelf+halo, (б) frame-gap чистий на select+банер, (в) **fast-scroll без blank-flash** → шиплять 1-2 CSS-фікси, нуль реструктуризації. Якщо clip-margin не тримає shelf на Safari АБО fast-scroll блимає → 2b(select) + банер окремо / virtual.

**Матеріал-гарантія (відповідь Konst):** 2b скрол не чіпає (безпечний). CV зберігає ВИГЛЯД матеріалу (clip-margin) — єдиний ризик = fast-scroll blank-flash (рядок не встиг намалюватись) → harness має окремий fast-scroll тест.

---

## 5. HARNESS-СПЕКА (наступний чат будує) — `QR_Lens_perf_harness_v1.html`

Scratch (поза нумерацією batch). **3 тести на спільній 180-поверхні** (батчинг 2.4). Harness мусить ТОЧНО відтворити прод-структуру (14.18 — інакше баг не відтвориться).

**Матеріал:** реальний B45 1:1 з batch58_2 (5-градієнт `.ph-card` + `.ph-back` peek + `::after` + `.ph-rank` + is-sel filter+halo + playCardGesture spring 950ms + parallax back). Токени --hc-* (р.576-588, обидві теми explicit+auto-dark). **ЗМІННА висота рядків** (мікс 1/2-рядкові адреси — ловить CV scroll-jump).

**Тести:**
1. **select-cycle** — auto-cycle б'є **ТОП-картки** (worst-case; faithful deselect+select одним render-pass). frame-gap на анімації.
2. **banner-reveal @180** — candidate-A порт (bnrIn: pin+will-change+composite translateY+height+end-snap). frame-gap на reveal + окремо на end-snap.
3. **fast-scroll** — програмний швидкий скрол; візуальний blank-flash watch (CV on/off).

**Інструментація:** **frame-gap трійка** (max-gap ms · dropped>33 · Δ-baseline; baseline після idle, відкинути перші N — 2.4 NB) великим шрифтом, читається на device. 📋-копі (буфер+текст-бокс). Міні-легенда в чат (назви повзунків НЕ перекладати).

**Контроли:** rowcount **12↔180** · select-позиція **топ↔низ** · тема-тогл · тогли (одна змінна за раунд, 14.14):
- `[composite-glow]` (2b: filter→box-shadow-glow на `::before` opacity-reveal + прибрати box-shadow з transition р.635)
- `[CV]` (content-visibility:auto на `.ph-row`)
- `[clip-margin]` (overflow-clip-margin — з видимим shelf+halo, щоб БАЧИТИ чи визирає)
- `[contain-intrinsic-size]`
- `[isolate]` (transient will-change:transform на 1-2 анімовані картки — лише ПІСЛЯ 2b має сенс, A70)

**Послідовність device (XS iOS18 + 15Pro iOS26, обидві теми):**
1. 180 baseline (все OFF): select-топ + банер + fast-scroll → трійка = КОРІНЬ
2. 12 baseline → чистий контроль
3. `[composite-glow]` сам → select чистий? банер трохи легше?
4. `[CV]+[clip-margin]` → обидва чистіші? shelf+halo визирають? fast-scroll блимає?
5. рішення: CV+clip-margin(+2b) vs 2b+окремий банер vs virtual

---

## 6. Decision-tree (після device)
- CV+clip-margin чистить обидва + shelf цілий + fast-scroll ОК → **шип CV+clip-margin (+2b bonus)**. Один-два CSS-фікси.
- clip-margin НЕ тримає shelf / fast-scroll блимає → **2b для select** + банер: reduce boundary-cost інакше / accept / virtual.
- нічого дешеве не тримає при 180 → **virtual scroll** (резерв, окремий обережний арк).

---

## 7. Метод (wsd) + що НЕ регресувати
- **Спершу вимір** (2.4 frame-gap) → корінь ПЕРЕД правкою. **Harness-first** (2.4). **Device=арбітр** (1.5/12.9). **Одна змінна** (14.14). **grep-before-claim** (12.1). **plan→confirm→код** (1.5).
- **НЕ чіпати/регресувати:** event delegation (р.2428/2431), persistent-DOM sig-guard (р.1543), border-ring B41/A70 (р.597/643), candidate-A банер, VT-close (B47)/VT-drill (B49), SR-motion (E1/E3a/Вибір-A), freshness-семафор, B58.2 у проді.
- Perf-фікс = **новий batch B59**; `APP_BUILD +rev`; гейти (node --check + tag-balance + jsdom/grep); auto-dark A69 паритет; scoped-descendant grep (10.8).

---

## 8. Ключові код-якорі (batch58_2)
- renderPharmacies + windowing: **р.1528-1570** (innerHTML р.1562; sig-guard fast-path р.1543-1550)
- `.ph-card` матеріал+transition: **р.591, 627-635**; is-sel filter: **р.645**; `.ph-back`: **р.619**; ring: **р.597/643**; токени --hc-*: **р.576-588**
- playCardGesture spring 950ms: пошук `function playCardGesture`
- банер: bnrIn **р.1172-1196**, bnrOut р.1197-1215, `.bnr-pin` CSS **р.292-293**, renderBanner р.1132-1149, `_bnrFinalizeNow` р.1161
- select delegation: **р.2428-2431**

---

## 9. Побічне (зроблено цієї сесії)
- **wsd TODO оновлено** (`/mnt/user-data/outputs/wsd_TODO_running.md`): мікроскоп-запис р.65 розширено — **«мікроскоп + web-пас = спарена discovery-фаза перед lock»** (ідея Konst, прецедент B59). Web=важелі, device=вирок. → занести в wsd 2.4 на канон-сесії.
- **Канон-борг 14.18a** (B52→B58 ~10 un-canon) — досі відкладено, ПІСЛЯ perf-фіксу.

---

## 10. Стартове повідомлення для нового чату

```
Привіт! QR Lens, perf-арк B59 (Tab-2 ~180 карток). Discovery завершено — будуємо harness.

КОНТЕКСТ: B58.2 у проді (export device✓). Два симптоми на 180 картках (mockup 12 = ідеально):
(A) select «цегляна»/low-FPS, найгірше на зміні вибору; (B) банер candidate-A «болісно виштовхує 180» на першій появі. Позиційно: топ-картка = джанк, низ = гладко. A+B — одна подія (select показує банер).

Читай ПЕРЕД кодом (view):
1. Work_Standard.md (wsd v2.24) — 2.4 frame-gap трійка+harness-first+bench/harness словник · 3.10 тест-обсяг · 12.1 grep-before-claim · 14.14 одна-змінна · 14.18 (research дає гіпотезу, device вирок; layer-promote не лікує box-paint) · 1.5 plan→confirm→код
2. Lens_iOS_cookbook.md — A70 (border>box-shadow під рухом; layer-promote не лікує box-paint) · A45/A57 (banner-mech candidate-A)
3. QR_Lens_session_summary_B59_perf_MICROSCOPE_WEB.md — ПОВНИЙ контекст: grep-корінь, мікроскоп-виправлення, web-синтез, ставка, HARNESS-СПЕКА §5, decision-tree §6, код-якорі §8
4. QR_Lens_preview_batch58_2.html — база (harness відтворює B45-матеріал 1:1)
5. wsd_TODO_running.md

ЗАВДАННЯ: побудувати QR_Lens_perf_harness_v1.html за спекою §5 самері — 3 тести (select-cycle топ-worst / banner-reveal@180 candidate-A порт / fast-scroll blank-flash) на реальному B45-матеріалі, змінна висота рядків, обидві теми, frame-gap трійка, тогли [composite-glow(2b)]/[CV]/[clip-margin]/[contain-intrinsic-size]/[isolate], rowcount 12↔180, позиція топ↔низ, 📋-копі. Одна змінна за раунд. НЕ починати код без confirm (1.5) — спершу план harness-структури, потім будуємо.

СТАВКА (device-arbitrated): CV+overflow-clip-margin = обидва симптоми одним (hinges Safari clip-margin fidelity + fast-scroll blank-flash) + 2b composite-glow = select-hygiene on-canon. Virtual scroll = резерв.

NB: НЕ регресувати event-delegation/persist-DOM sig-guard/border-ring/candidate-A/VT-close/VT-drill/SR-motion/freshness (§7 самері). Perf = новий batch B59, APP_BUILD +rev, гейти. Після perf → канон 14.18a (борг B52→B58).
```
