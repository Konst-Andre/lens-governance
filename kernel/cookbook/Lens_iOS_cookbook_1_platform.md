> живе доки: назавжди (вічне, wsd 1.8) · читається ТОЧКОВО за індексом
> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)

# Lens — iOS / PWA Cookbook · Том 1 — Оболонка й платформа

> **Тригер тому.** заводжу або лагоджу оболонку продукту: head, manifest, теми-інфраструктура, висоти, safe-area, середовище виконання
>
> **Маршрутизатор — `Lens_cookbook_INDEX.md`**: задача → запис → том, і мапа номер → том.
> Загальний контекст (джерело коду, тестова база, маркування ✅ / 🔧 / 🆕🔒) живе там і **тут не дублюється**.
>
> **Записи тому (23):** A1, A2, A3, A4, A5, A7, A8, A9, A10, A11, A12, A13, A14, A23, A24, A25, A27, A28, A31, A55, A68, A69, A75
>
> **Зовнішні залежності.** A6 (сам дропдаун теми) → том 4 · A15/A56 (bottom-nav) → том 2
>
> **Нумерація наскрізна для всіх томів** — A-номери не змінювались при розпилі. Діапазони розривні; адресує індекс, не діапазон.

-----

## A1. HTML head — обов’язкові meta tags

```html
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0d1117">
```

- `viewport-fit=cover` — БЕЗ нього `env(safe-area-*)` = 0.
- `apple-mobile-web-app-capable: yes` — БЕЗ нього не стартує у standalone.
- `black-translucent` — інакше біла смуга статус-бара в PWA. **⚠️ Має побічний ефект:** у standalone зсуває весь документ угору → з `html{height:100%}` оголює голу смугу знизу = висота верхнього inset. Фікс → **A55**.
- `maximum-scale=1, user-scalable=no` — блок pinch (доповнюється JS, A25 — iOS Safari ігнорує meta-частину).

## A2. PWA manifest.json

Ключі: `id` / `start_url` / `scope` (під шлях продукту), `display:"standalone"`, `background_color` + `theme_color`, `icons[]` (192/512/512-maskable). `orientation:"portrait"` iOS **ігнорує** → lock через CSS overlay (A23).

## A3. Icon pack (7 файлів) + squircle-правило

16/32 (favicon), 180 (apple-touch), 192/512 (PWA), 512-maskable (Android safe-zone 80%), favicon.ico. **Критично:** source full-bleed **без власних чорних полів** навколо squircle — iOS накладає squircle-маску поверх, інакше видно чорну рамку. Workflow: crop bbox → Lanczos resize у 7 розмірів; maskable з padding 10%.

## A4. Cache-busting versioning

`?v=batchN` у **HTML (5 місць: manifest+4 icon links)** + **manifest.json (3 місця в icons[])** — синк одночасно. Manifest кешується окремо від HTML. Файли НЕ перейменовуються — змінюється лише query-URL.

## A5. FOUC prevention — inline script (канонічний)

**Inline `<script>` у `<head>` ПЕРЕД будь-яким CSS link/style.** Встановлює `data-theme` на `<html>` до first paint.

```html
<script>
  (function(){
    try {
      var saved = localStorage.getItem('<prod>-theme');     // null|'auto'|'light'|'dark'
      var mode  = saved || 'auto';
      var dark  = mode==='dark' || (mode==='auto' && matchMedia('(prefers-color-scheme:dark)').matches);
      var html  = document.documentElement;
      html.setAttribute('data-theme', dark?'dark':'light');
      html.setAttribute('data-theme-mode', mode);
      var meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.content = dark ? '#0d1117' : '#f7f4ec';
    } catch(e) {                                              // Safari Private → localStorage throws
      document.documentElement.setAttribute('data-theme','dark');
      document.documentElement.setAttribute('data-theme-mode','auto');
    }
  })();
</script>
```

**Обов’язково:** (1) IIFE — не бруднити global; (2) try/catch — Safari Private throws; (3) **synchronous only** — НЕ async/Promise/setTimeout/DOMContentLoaded (буде flash); (4) атрибути на `<html>`, не `<body>` (body ще не існує); (5) sync `theme-color` тут же.

**Антипатерни:** `<script async>`, `DOMContentLoaded`, атрибут на `body`, media-залежний `<meta theme-color media=...>` разом із JS-driven update (конфлікт — лиши один dynamic meta + JS sync).

🔧 ключ `<prod>-theme` (`qr-theme` / `dl-theme` / …).

## A7. CSS variables — 3-шарова тема

```css
:root{ /* default = light */ --bg:#f7f4ec; --card:#fff; --ink:#1a1b1e; --accent:#2A8C84; --sab:env(safe-area-inset-bottom,0px); }
[data-theme="dark"]{ --bg:#0d1117; --card:#1c2128; --ink:#e6edf3; }            /* manual dark */
@media(prefers-color-scheme:dark){ :root:not([data-theme="light"]){ /* auto dark */ --bg:#0d1117; … } }
```

`html{background:var(--bg)}` — overscroll-bounce у колір теми. Logic: `light`→завжди light; `dark`→завжди dark; без атрибута→media (auto).

## A8. Theme-override specificity guard

`[data-theme="dark"]` має вагу класу → (0,1,0). Отже `[data-theme] .X` = **(0,2,0) = РІВНА** `.X.modifier` → при рівності виграє пізніше правило; тематичні оверрайди йдуть ПІСЛЯ базових → **мовчки перебивають** стани (`.on/.act/.accent/.sel/.open`).

**При додаванні `[data-theme] .X`:** перевір чи є `.X.<modifier>` на ту саму властивість (`background/border-color/box-shadow`). Якщо так — або підняти специфічність `[data-theme] .X.<modifier>` (0,3,0), або скоупити базу `[data-theme] .X:not(.<modifier>)`. State-оверрайди — ПІСЛЯ базових тематичних.

Grep (post-patch): `\[data-theme=[^]]+\] \.[a-z-]+\{` + `\.X\.(on|act|accent|sel|open)\{`. *(Привід: Drive Lens Batch 9.2–9.4 — fuel-сегменти/hero-рамка.)*

## A9. `dvh` замість `vh`

ЗАВЖДИ `dvh` для `max-height`/`height`/`min-height` повноекранних контейнерів, sheet, empty-state. `vh` (static) = найбільший viewport → у Safari з toolbar layout вилазить. `dvh` = реальний видимий. iOS Safari 15.4+ (XS iOS 18 OK). ❌`80vh` ✅`85dvh`.

## A10. Safe-area-inset

```css
.app-bar{ padding: max(18px, calc(env(safe-area-inset-top,0px)+12px)) 16px 8px; }
.sh-box { padding-bottom: env(safe-area-inset-bottom,0px); }
:root   { --sab: env(safe-area-inset-bottom,0px); }
```

- **НЕ** додавати арбітрарні pixels поверх `env()` (Apple HIG: 21pt досить; env()≥34pt). ❌`calc(12px+var(--sab))` ✅`env(safe-area-inset-bottom,0px)`. Виняток: візуальний padding ВСЕРЕДИНІ елемента з власною зоною тапу (tabbar) — не на контейнер.
- `max(18px,…)` — fallback без viewport-fit.
- **Ніколи не зменшувати** `env(safe-area-*)` — кнопки під home indicator/notch + відмова App Store review. «Компактніший sheet» вирішувати layout-ом (flex margin-top:auto, density), не зменшенням sab.
- `--sab`: PWA=34pt, Safari=0 (toolbar бере на себе) → **detection PWA не базувати на –sab**, лише `@media(display-mode:standalone)`/`navigator.standalone`.
- **Зазор знизу = верхній inset (НЕ bottom-проблема).** Якщо в standalone унизу гола смуга кольору фону, що ЧИСЛОВО = верхньому inset — це зсув документа від `black-translucent`, не позиціювання бару. Фікс → **A55**.

## A11. PWA detection — display-mode + heuristic

```js
const isS = matchMedia('(display-mode:standalone)').matches || navigator.standalone;
// + heuristic: різниця innerHeight vs (screen.height - sab) > sab*.5 → html.classList.add('pwa-full')
```

`pwa-full` клас → умовні стилі (особливо bottom nav, A15).

## A12. VisualViewport — tight/roomy-vh

```js
const vv = window.visualViewport;
function checkVh(){ const vh = vv?vv.height:innerHeight;
  document.body.classList.toggle('tight-vh', vh<720);
  document.body.classList.toggle('roomy-vh', vh>790); }
vv ? (vv.addEventListener('resize',checkVh), vv.addEventListener('scroll',checkVh)) : addEventListener('resize',checkVh); checkVh();
```

`<720` tight / `720–790` default / `>790` roomy. **Пороги залежать від пристрою** (XS PWA≈812 roomy, Safari≈762 default, згорнутий≈715 tight; iPhone 17 PWA≈870–932). Перед діагнозом «X не працює у режимі Y» — точно з’ясуй режим пристрою user-а, не припускай roomy для всіх PWA.

## A13. `max-height` обмежує, не задає (діагностика)

Sheet `max-height:85dvh` + контент 600px на vh 900 → висота=600px. Перед «sheet задовгий» перевір що sheet>content (часто причина — padding-bottom, не max-height). **Перед патчем розмірів — порахуй математику:** груба висота контенту в px → порівняй з max-height на конкретному vh → перевір чи max активується (content>max). Якщо ні — патч max-height марний. Math не сходиться зі скрін-відчуттям → чесно «не гарантую без debug data».

## A14. 5-layer top stack

`#app` → `header.app-bar` → `#ph-banner` (глобальний контекст) → `#ctx-layer` (status line) → `.screens` (таби з `.scroll-a`) → `nav.bottom-nav`. `#app{max-width:430px;margin:0 auto}` (desktop limit). Переноситься 1:1, міняється лише вміст табів.

## A23. Orientation lock — CSS overlay

```css
@media (orientation:landscape) and (max-width:900px){
  #app{ display:none !important; }
  body::after{ content:"Поверніть телефон вертикально"; position:fixed; inset:0; z-index:10000;
    display:flex; align-items:center; justify-content:center; … }
}
```

iOS НЕ підтримує `screen.orientation.lock()` (native-only); `manifest orientation` ігнорує. `max-width:900px` виключає планшети.

## A24. iOS системні CSS правила (що кожне блокує)

```css
*,*::before,*::after{ box-sizing:border-box; margin:0; padding:0; }
html{ -webkit-text-size-adjust:100%; background:var(--bg); }     /* double-tap autofit / overscroll колір */
html,body{ height:100%; overflow:hidden; overscroll-behavior:none; }   /* pull-to-refresh + scroll chain */
html,body,#app{ touch-action:pan-x pan-y; }
body{ -webkit-user-select:none; user-select:none; -webkit-touch-callout:none; touch-action:manipulation; }  /* long-press menu */
input,select,textarea{ font-size:16px !important; }              /* anti auto-zoom при focus */
input,textarea{ -webkit-user-select:text; -webkit-touch-callout:default; }
*{ -webkit-tap-highlight-color:transparent; }                    /* сірий tap highlight */
button{ font-family:inherit; border:none; cursor:pointer; background:none; color:inherit; }  /* ❗ background:none ОБОВ'ЯЗКОВО */
button:disabled{ touch-action:none; pointer-events:none; }
.scroll-a{ -webkit-overflow-scrolling:touch; }
```

display-only елементи з inline `<em>` → `pointer-events:none` (double-tap autofit).

**❗ `button{background:none}` — критичний, не косметика.** Без нього iOS малює системний `ButtonFace` (≈`#e7e7e9`) на будь-якій `<button>` БЕЗ явного `background`. Кнопки з власним фоном (пілюлі, CTA) виглядають ок → баг невидимий, поки не зʼявиться кнопка, що покладається на фон **батька** (напр. `.theme-item` у дропдауні: фон дає `.theme-menu{background:var(--card)}`, сама кнопка прозора). Тоді ButtonFace перекриває тематичний `--card` → панель «сіра/інвертована» лише в одному компоненті. Симптом-якір: семпл пікселя дає `#e7e7e9`, а сусідні картки — правильний `--card`. *(Прецедент: KPI Lens Batch 14.1 — theme dropdown; root-cause знайдено семплом пікселя, не на око.)*

## A25. Pinch-zoom — JS block

```js
['gesturestart','gesturechange','gestureend'].forEach(ev =>
  document.addEventListener(ev, e=>e.preventDefault(), {passive:false}));
```

`{passive:false}` обов’язково (iOS ігнорує `user-scalable=no` в meta).

## A27. Reduce-motion + no-transition при init

`@media(prefers-reduced-motion:reduce){ animation:none }`. Anti-fade на launch (CSS vars міняються при applyTheme): додати `.no-transition` (`transition:none!important`) → `applyTheme()` → зняти через **double `requestAnimationFrame`** (гарантія, що клас додано й знято в різних frames). Косметичний uplift.

## A28. Storage event — multi-window sync

```js
addEventListener('storage', e => { if (e.key==='<prod>-theme') applyTheme(); });
```

Тема змінена в Safari tab → PWA оновлюється (між Safari↔PWA standalone: iOS 17.4+).

## A31. Z-index стек

app-bar(scrolled) 20 · theme menu 200 · bottom sheets 250–300 · onboarding 9000 · orientation lock 9999/10000. Тримати єдиний стек на продукт.

## A55. PWA standalone: модель висоти документа + overlay-бар зі склом (Liquid Glass) ✅

Дві **пов’язані** речі, що довго плутали (Drive Lens Batch 36–41, device-валідовано XS iOS 18 + 15 Pro iOS 26). Лікувати їх треба окремо й у правильному порядку: **спершу висота, потім скло.**

### (1) Гола смуга знизу = ВЕРХНІЙ safe-area inset

**Симптом:** у standalone (PWA) унизу екрана гола смуга кольору фону (`--surface-1`); bottom-бар «не доїжджає» до фізичного низу. У Safari норм (тулбар фізично маскує низ; `env-bottom`=0 у Safari).

**Корінь — модель висоти документа, НЕ позиціювання бару.** Комбо `apple-mobile-web-app-status-bar-style: black-translucent` (A1) + `viewport-fit=cover` + `html{height:100%}` → translucent-статусбар зсуває **весь документ угору** (контент стартує під вирізом), а `height:100%` тримає документ рівно на висоту екрана → знизу лишається порожнеча, що **ЧИСЛОВО = висоті верхнього inset**.

**Симптом-якір:** зазор знизу = відомий top-inset (виріз 44pt / Dynamic Island 59pt; ×3 у px = 132 / 177). Збіг із top-inset = це воно. fixed/in-flow/manifest цього **не лікують** (лікують не той кінець).

**Фікс (один рядок):**

```css
html{ min-height:calc(100% + env(safe-area-inset-top)); }
```

**Нюанс при `html,body{height:100%;overflow:hidden}`:** РОЗДІЛИТИ правило — `html` бере `min-height:calc(100% + env(safe-area-inset-top))` **без** `height:100%`; `body` лишає `height:100%`. `overflow:hidden` лишається (скрол на внутрішньому контейнері `.scroll-a`, не на body).

### (2) Скляний bottom-бар (Liquid Glass) вимагає контенту ПОЗАДУ

`backdrop-filter:blur()` розмиває лише те, що намальовано **позаду** елемента. **In-flow (relative) бар не має контенту позаду** (контент над ним у флекс-потоці) → скло розмиває суцільний фон = ефект мертвий. Для живого скла бар має **оверлеїти** скрол-контент.

**Рішення, що тримає І desktop-width, І живе скло:**

```css
#app{ max-width:430px; height:100dvh; position:relative; overflow:hidden; }
.bottom-nav{ position:absolute; left:0; right:0; bottom:0; /* НЕ fixed */
  backdrop-filter:blur(var(--glass-blur)) saturate(var(--glass-sat));
  padding:6px 6px max(9px,var(--sab)); /* скло заливає зону home-indicator зсередини */ }
.scroll-a{ padding-bottom:calc(var(--nav-h,64px) + 14px); } /* інакше останній запис за склом */
```

- **`absolute`-в-`#app`, НЕ `fixed`.** `fixed` якориться до viewport — той самий слизький ґрунт, що оголює зсув висоти (саме тому overlay-спроби в Batch 36 «не діставали низу»). `absolute` якориться до низу `#app` (100dvh, уже полагоджений фіксом (1)) → бар на справжньому фізичному низу.
- **`--nav-h`** ставиться JS-виміром (`measureNav()` → `el.offsetHeight` → CSS-змінна), fallback `64px`. Той самий `--nav-h` живить `.toast` bottom-offset.
- Зона home-indicator стає **скляною**, бо `padding-bottom:max(Npx,var(--sab))` самого бару фарбує скло вниз через sab (не зменшувати sab — A10).

**Анти:** лікувати зазор позиціюванням бару (3 чати марно — fixed/in-flow/manifest нічого не дали, бо корінь = висота); `fixed;bottom:0` для overlay в standalone (зсув висоти оголює низ); `backdrop-filter` на in-flow барі (нема що розмивати). **Зв’язок:** A1 (black-translucent), A9 (dvh), A10 (safe-area — не зменшувати), A14 (5-layer stack: #app як positioned-предок), A15 (bottom-nav padding). *Drive Lens Batch 36–41; корінь знайдено колориметрією device-скрінів — зазор ЧИСЛОВО = top-inset (14.7-споріднено: міряй, не гадай).*

## A68. Прев’ю-пісочниця Claude: безпечні лише `console.log/warn/error` — `info/debug/table/group` undefined → TypeError валить скрипт ✅

**Симптом.** Inline-прев’ю артефакта (iOS-застосунок І desktop-web) — порожній контент + `Uncaught Error: Script error.` На GitHub Pages (Safari) і в jsdom — рендериться ідеально.

**Причина.** Пісочниця підміняє `console` власним стабом: є `.log/.warn/.error`, але **нема `.info`** (ймовірно й `.debug/.table/.group`). `console.info(...)` на top-level → `TypeError: console.info is not a function` → головний скрипт падає ДО `render()` → порожньо. На реальному Safari/деплої `console.info` існує → баг **невидимий поза прев’ю**.

**Канон.** У коді, що крутиться у прев’ю-пісочниці, — лише `console.log/warn/error`, або guard:
```js
try{ (console.info||console.log||function(){}).call(console,'msg',data); }catch(_){}
```
Console-маркер версії на старті взагалі зайвий на реальному PWA (консоль юзеру невидима) — версія йде в About-поверхню (A58), не в консоль.

**Друга причина-клас — ASI-склейка (parse-valid / runtime-fatal).** `const DATA=[…]` **без `;`**, а наступний токен — `(` (інжект-IIFE) або `[`: ASI НЕ вставляє крапку з комою (`[…]\n(…)` — валідне продовження виразу) → масив **викликається як функція** → `TypeError: […] is not a function` на top-level → скрипт падає ДО `render()` → той самий «жива на вигляд, мертва» симптом, і в sandbox, **і на GH Pages**. `node --check` **мовчить** (синтаксично валідно — це runtime, не парсинг). Фікс: `;` після масиву. Профілактика: при інжекті scroll-bloat-даних (wsd 3.10) завжди термінувати масив `;`. *Прецедент: QR Lens scrolltest 12-card (19.06) — IIFE-інжект 12 аптек одразу після `DATA` без `;`; jsdom розкрив за 1 прогін.*

**Метод — не гадати про опачний `Script error`.** Cross-origin маскує деталі (`window.onerror` бачить лише «Script error»). РОЗМАСКУВАТИ перш ніж гадати: (1) in-page error-overlay (`addEventListener('error',…)` → у видимий div); (2) per-stage трасування + top-level `try/catch`, що репортить РЕАЛЬНІ `e.name/message/stack` (try/catch бачить деталі навіть коли onerror маскує). Арбітри відтворення: **GitHub Pages + jsdom** (обидва ALL OK → код справний, проблема суто пісочниця).
**Анти:** гадати причину опачного Script error in-sandbox; `console.info/debug/table` без guard у прев’ю-коді; inline-прев’ю як єдиний рендер-арбітр (GH Pages/device — справжній).
**Зв’язок:** 12.1 (реальний код/рендер > припущення), 1.5 (device-арбітр). *Прецедент: QR Lens B30.1→B30.4 (`console.info('QR Lens build',APP_BUILD)` валив рендер; ~година на розмаскування — застосувати ОДРАЗУ).*

## A69. Cross-theme fused-шов — дизайнити по кожній темі; auto-mode override коректність ✅

**Дизайн-урок (інстанс A39).** Дві «зрощені» поверхні (банер↔статус-ряд, секція↔секція) — **сепарацію шва дизайнити окремо по кожній темі**: однаковий токен має різну перцептивну вагу. Кейси QR:
- **B31.1 ph-banner (темна):** ембоз помилково читався як lift → фікс на дебоз-well (тон-крок).
- **B31.2 статус-лінія:** нижня `--border` на світлій майже невидима (на темній `#333b46` = чиста світла основа) → спліт **лише світла** `--border→--border-2`; темну не чіпати.
- Урок: «fused-шов одним токеном на обидві теми» = на одній темі шов зникає/інвертується. Звіряти обидві теми на колажі (A39), спліт за потреби.

**Тех-патерн — auto-mode override коректність.** Тематичний оверрайд із ХАРДКОД-значеннями (не токенами) мусить розрізняти explicit-dark і auto-dark:
```css
[data-theme="dark"] .X{ /* хардкод-дебоз */ }                                       /* explicit-dark */
@media(prefers-color-scheme:dark){ :root:not([data-theme="light"]) .X{ /* той самий */ } }  /* auto-dark ONLY */
```
**Анти — топ-рівневий `:root:not([data-theme="light"])` із хардкод-тінню.** Матчить auto **незалежно від системи** → в auto-**light** накладе dark-тінь на світлу поверхню (витік). Безпечний лише з ТОКЕННИМИ значеннями (токен сам фліпне по `@media`); для хардкодів — обов’язково `@media`.
**Дзеркало для світла:** `[data-theme="light"] .X` + `@media(prefers-color-scheme:light){:root:not([data-theme="dark"]) .X}` (патерн B31.2).
**Тригер:** будь-який тема-оверрайд із хардкод-тінню/кольором, що має працювати і в auto.
**Анти:** хардкод-оверрайд лише через `[data-theme="dark"]` (auto-dark падає на базу → FINDING B31.3: хедер-контролі давали ембоз замість дебозу в auto-dark); топ-рівневий `:root:not()` із хардкодом (витік у протилежну auto-тему).
**Зв’язок:** A8 (специфічність тема-оверрайдів — це її auto-вимір), A39 (однаковий токен ≠ однаковий характер), A45/A51 (well/elevation мови, що «зрощуються»). *Прецедент QR: B31.1→B31.2→B31.3. Source `QR_Lens_preview_batch31_3.html`: хедер `р.165/167`, ph-banner `р.225/226`, статус-лінія `р.292/293`.*

## A75. Іконки PWA: генерація з локнутого гліфа + межі платформи ✅

> Пара до **A2** (manifest) і **A3** (icon pack) — цей же том. A74 — зарезервований номер, не перевикористовувати.

**Статус:** StockCheck b25 — device-verified (встановлено на 15 Pro, iOS 26).
**Дім у Cookbook:** поруч із A2/A3 (manifest + PWA-head) — та сама тема «оболонка застосунку».

### Принцип: іконка — не окрема картинка, а рендер гліфа продукту

Найпоширеніша помилка — намалювати іконку «за зразком» логотипа. Тоді вона живе власним
життям: гліф у продукті змінюють, іконку забувають, і розбіжність ніхто не помічає роками.

**Правило:** іконка генерується **з тієї самої `d`-стрічки**, що стоїть у продукті.
Генератор лишається в теці як частина канону, не як разовий скрипт.

Якщо контур гліфа складається лише з `M`/`L`-сегментів (без Безьє) — SVG-рушій не потрібен
взагалі: контур парситься як полігон і заливається тим самим лінійним градієнтом
із тими ж `userSpaceOnUse`-координатами. Одна залежність (`Pillow`), відтворювано.

### Набір файлів

| файл | розмір | призначення |
|---|---|---|
| `apple-touch-icon.png` | 180 | iOS home screen |
| `icon-192.png` / `icon-512.png` | 192 / 512 | manifest `purpose:"any"` |
| `icon-192-mask.png` / `icon-512-mask.png` | 192 / 512 | manifest `purpose:"maskable"` |
| `favicon-32.png` | 32 | вкладка |

### Тверді обмеження

| # | Правило | Чому |
|---|---------|------|
| 1 | `apple-touch-icon` — **непрозорий** PNG | iOS підкладає під альфу чорне → прозорий фон дає чорну пляму |
| 2 | **Не заокруглювати самому** | iOS накладає власну маску-скваркл; своє заокруглення = подвійний кант |
| 3 | **Maskable = окремий рендер**, не той самий файл меншим | Android може обрізати до кола; гарантована лише центральна зона **80%**. Габарит гліфа: `any` ≈ 0.66 сторони, `maskable` ≈ 0.50 |
| 4 | Маніфест — **окремий файл поруч з `index.html`** | у `data:`-URI немає базового URL → відносні `"./"` і `icons[]` резолвити нема від чого |
| 5 | `"id":"./"` у маніфесті | без нього зміна `start_url` робить застосунок **новим** для Android → друга іконка поруч зі старою |
| 6 | Усі посилання з `?v=<білд>` | wsd 6.5 — GitHub Pages віддає `max-age=600` |

### Механізм: чому іконка не перемикається за темою

**Іконка робочого столу — статичний ресурс оболонки ОС, узятий у момент встановлення.
Застосунок не має каналу впливу на неї після встановлення.** Тема застосунку живе в
`localStorage`, до якого оболонка доступу не має; щоб іконка «слухала» тему, оболонка мусила б
отримати від нас **декларацію двох файлів**. JS тут безсилий принципово: він виконується
всередині застосунку, а іконка живе зовні.

**Наслідок для процесу:** після заміни `apple-touch-icon` уже встановлений ярлик своєї картинки
**не перечитує ніколи** — його треба видалити й додати заново.

> `[07.2026]` Каналу декларації light/dark/tinted-варіантів для веб-клипів не існує
> (для нативних застосунків він з'явився в iOS 18). **Перевірити при виході наступного
> мажорного iOS.** *(формат запису — wsd 12.10)*

### Вибір фону — device-рішення, не смак

iOS не малює іконкам ані рамки, ані тіні під маскою. Тому **темна іконка на темних шпалерах
втрачає силует** — судити треба на світлих, темних і фото-шпалерах, у реальному масштабі 60pt
і **серед сусідів**, а не окремо на порожньому тлі.

Стенд для цього — `icon-compare`, іменований варіант у `Lens_stagebench_manifest.md` §4-варіанти.

### Джерело

`StockCheck_session_summary_b25_PWA.md` · `StockCheck_icon_gen.py` · `manifest.json` ·
`StockCheck_port_b25.html` р.10–16.

## A79. Блок «Обслуговування»: самоперевірка версії + встановлення на робочий стіл ✅

**Задача.** Односторінковий PWA, розданий колегам за посиланням, не має каналу сказати
користувачеві «ти на старому білді». Магазину застосунків немає, push немає, бекенду немає.

**Механізм.** Застосунок — **один HTML-файл**, тому він може перевірити себе сам:
`fetch(location.pathname,{cache:'no-store'})` тягне власне тіло, регекс дістає з відповіді
константу `APP_BUILD` (wsd 10.6) і порівнює з тією, що вже в пам'яті. Розбіжність = є оновлення.
Застосування — `location.replace(pathname+'?v='+ver)`: query-рядок обходить HTTP-кеш,
бо для браузера це інший URL.

**Чому не service worker.** SW купує лише вікно `max-age` хоста ціною власного кешу,
циклу оновлення SW і класу помилок «застряг на старій версії SW». Заміряно на GitHub Pages:
`max-age=600` — кеш протухає сам за 10 хв звичайного користування, після чого свіжа версія
підтягується без жодного коду. Постійна складність в обмін на десятихвилинну затримку — невигідно.
*(StockCheck b27 §6 → рішення 08.2026; повний розбір у `Lens_module_maint_v1.md` §1.)*

**Встановлення — дві різні платформи, дві різні гілки:**

| платформа | канал | що робимо |
|---|---|---|
| Android / Chrome | `beforeinstallprompt` | перехопити подію, `preventDefault()`, зберегти її; `prompt()` викликати **лише за тапом користувача** |
| iOS / Safari | каналу немає | покрокова інструкція «Поділитись → На екран Додому» |

Без `preventDefault()` браузер показує власний банер у свій момент — користувач його змахує,
і подія більше не приходить **ніколи** за цей візит. Перехоплення переносить рішення в те місце
інтерфейсу, де людина його шукає. `appinstalled` прибирає кнопку після успіху.

**Детект режиму — `display-mode:standalone`**, не `--sab` і не сам `navigator.standalone`
(A11/A12). `env(safe-area-inset-bottom)` дорівнює 0 у Safari і ~34px у PWA, але це **наслідок**
режиму, а не його ознака: на пристрої без вирізу він 0 в обох.

**Датовані спостереження (wsd 12.10):**
- `[08.2026]` `beforeinstallprompt` у Safari **відсутній**. Перевірити при наступному мажорному iOS.
- `[08.2026]` GitHub Pages `Cache-Control: max-age=600`. **При зміні хостингу висновок про SW
  не переноситься** — на хості з довгим `max-age` вікно застарілості інше.

**Анти-приклад.** Класи блоку в першій редакції звалися `.sec`/`.pri`. Вони зіткнулися
з глобальними `.sec` (секційний заголовок списку) — і колізія доїхала до девайса. Скоуп
`.ins-cta .sec` не рятує: він перебиває лише **оголошені** властивості, а `text-transform` /
`display` / `margin` протікають далі. Перейменовано на `.ins-sec`/`.ins-pri`.

**Детектор (К2).** Перед вставкою модуля в новий продукт — `grep '\.ins-'` і `grep 'fx-duo'`
дають **0** збігів. Після вставки — device-тест **трьох** оточень (Safari · webview · standalone),
бо гілка встановлення в кожному поводиться інакше.

**Код:** `Lens_module_maint_v1.md` — CSS 182 · HTML 36 · JS 298 рядків, знято з
`StockCheck_port_b28.html` (device✓ XS/iOS 18 · 15 Pro/iOS 26 · Android).
**Матриця:** `StockCheck_maint_jsdom_matrix.js`, 61 твердження.

-----

## A80. Мінімальний xlsx-writer без бібліотек (ZIP+XML вручну) ✅

**Задача.** Віддати табличні дані назовні так, щоб файл однаково відкривався на ПК-Excel,
мобільному Excel і у в'юверах — з офлайн-PWA, без CDN і без збірки.

**Чому не CSV.** CSV **не несе інформації про власний роздільник** — його обирає програма
адресата за системним *List separator*. Той самий файл, що правильний у нас, розсипається
в іншій локалі. Будь-який «фікс роздільника» лише переносить помилку на іншу локаль,
а не усуває клас. Формат для міжлокального обміну має бути **самоописовим**.
*(StockCheck b28: назви SKU з комами рвались навпіл у керівника, у нас виглядали правильно.)*

**Чому не SpreadsheetML.** Дає діалог «формат не відповідає розширенню» при кожному відкритті.

**Що таке xlsx насправді:** ZIP із XML-частин. Мінімальний робочий набір — 5 файлів:
`[Content_Types].xml` · `_rels/.rels` · `xl/workbook.xml` · `xl/_rels/workbook.xml.rels` ·
`xl/worksheets/sheet1.xml`. Плюс `xl/tables/table1.xml` + зв'язок, якщо потрібна Excel-таблиця.

**Три вузли, на яких падають саморобні генератори:**

1. **CRC32 обов'язковий** на кожен запис ZIP — без нього архів не відкривається взагалі.
   Таблиця з 256 значень будується один раз при старті.
2. **`inlineStr` замість `sharedStrings`** — на порядок простіший генератор; після deflate
   виграш від таблиці рядків — одиниці відсотків, не варте ускладнення.
3. **Формули пишуться з кешованим `<v>`.** В'ювери формул **не рахують**: без кешу
   обчислювані колонки порожні саме там, де файл показують керівнику. Excel перерахує сам,
   в'ювер покаже кеш — обидва сценарії закриті.

**Стиль таблиці — один атрибут**, не інструментарій: `TableStyleMedium7` у `tableStyleInfo`.
⚠ **Межа формату:** xlsx **не зберігає** кольори вбудованих стилів — у файлі лише **ім'я** стилю,
палітру тримає Excel. LibreOffice і сторонні в'ювери покажуть інший відтінок. Це не дефект
генератора: оригінальний корпоративний файл поводиться так само.

**Детектор (К2).** Формат, що йде назовні, перевіряти **парсером адресата** (`openpyxl` ≈ Excel),
а не оком: око не бачить класу помилок «залежить від локалі отримувача». Замір = «N рядків,
таблиця «X», кеш комірки N2=…» — конкретні числа, не «виглядає правильно» (wsd 6.6, 10.5).

**Код:** `StockCheck_port_b28.html` — `crc32`/`CRC_T` · `deflateRaw` · `zipBuild` ·
`xe`/`colName`/`u8` · `sheetXml` · `tableXml` · `STYLES` · `buildXlsx`.
Заміряно: 218 КБ сирих → 25 КБ у файлі; device✓ ПК-Excel · мобільний Excel · iOS.

-----

## A81. `CompressionStream('deflate-raw')` — нативна заміна ZIP-бібліотеки ✅

**Задача.** Стиснути дані всередині PWA без JSZip/pako: single-file архітектура, офлайн, без CDN.

**Механізм.** `new CompressionStream('deflate-raw')` — вбудований у платформу
потоковий deflate. `deflate-raw` дає **голий** deflate-потік без zlib-обгортки — рівно те,
що очікує ZIP-запис із `method 8`. Варіант `'deflate'` додав би 2-байтовий заголовок
і 4 байти Adler-32, і архів не відкрився б.

**Фолбек на `store` (method 0) обов'язковий.** ZIP дозволяє нестиснені записи, тож при
відсутності API файл усе одно валідний — просто важчий. Гілку фолбеку треба лишати
навіть коли підтримка виглядає повною: вона коштує кілька рядків і рятує від тихої відмови.

**Детектор (К2) — вага файлу.** Store дає **×8–9** проти deflate на тих самих даних.
Це дешевший і надійніший симптом, ніж лог: користувач бачить розмір у шері й одразу знає,
якою гілкою пішов код. StockCheck b28: deflate 10–16 КБ · store дав би 80–140 КБ.
Іменований симптом замість консолі — та сама вимога, що й wsd 6.6.

**Датоване спостереження (wsd 12.10):** `[08.2026]` `CompressionStream` — Safari 16.4+,
Chrome 80+. Перевірити при зміні мінімальної цільової версії iOS.

**Код:** `deflateRaw()` у `StockCheck_port_b28.html`. Пара до **A80**.

-----

-----

# Частина C — Чек-лист deploy (перед видачею колегам)

manifest валідний · 7 іконок · cache-bust `?v=` синк HTML(5)+manifest(3) · SW registered · FOUC inline ПЕРЕД CSS · theme auto/light/dark persist · `dvh` всюди · `env()` без зайвих px · bottom nav padding Safari+PWA · sheet: ×/swipe/backdrop · swipe-close grip40/content64+scrollTop · orientation lock landscape · input `font-size:16px` · pinch blocked · numeric inputmode/pattern · (Drive) keyboard handling · offline→pending→online→green · multi-device realtime · system theme live (iOS 18+) · storage event sync.

-----

**Кінець.** Будь-який пункт Частини A валідований на iPhone XS iOS 18 PWA через QR Lens production. Точний код — grep у `QR_Lens_preview_batch22.html` (стандарт) / `Drive_Lens_preview_batch10_2.html` (swipe-пігулка A22, sheet-анімація A18).
