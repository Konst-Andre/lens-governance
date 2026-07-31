> живе доки: назавжди (вічне, wsd 1.8) · читається ТОЧКОВО за індексом
> KERNEL v1 · 30.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)

# Lens — iOS / PWA Cookbook

> **Що це.** Крос-продуктовий каталог перевірених iOS PWA + UI/UX патернів для всіх Lens (KPI / QR / Drive / наступні). Це **ЩО ми будуємо** (рецепти-рішення). Як ми працюємо (протокол, pre/post-patch, UX, sync) → `Work_Standard.md` (wsd).
> 
> **Джерело.** Консолідовано з: Drive Lens `concept_v1.2 §14` (46 гранулярних пунктів, перенесених з QR Lens), wsd Кластери 7/8/9 (+7.10, 8.2). Source-of-truth точного коду:
> 
> - стандартні патерни → `QR_Lens_preview_batch22.html` (grep по назві патерну);
> - swipe-пігулка + sheet enter/exit → `Drive_Lens_preview_batch10_2.html`.
> 
> **Тестова база.** iPhone XS iOS 18 PWA (vh≈812 roomy / Safari≈762 default / Safari згорнутий≈715 tight); вторинна — iOS 26.
> 
> **Маркування:**
> 
> - ✅ **Універсальне** — переносимо у будь-який Lens 1:1.
> - 🔧 **Адаптовано** — той самий патерн, інші параметри/назви під продукт.
> - 🆕🔒 **Продукт-специфічне** — НЕ універсальне, прив’язане до конкретного продукту, валідація може бути pending. Не тягнути в інші Lens без перегляду. Винесено в Частину B.
> 
> **Власність (анти-дубль із wsd):** iOS/PWA/UI патерни живуть ТУТ. wsd на них лише посилається. Не дублювати — крос-посилання за назвою.

-----

## Індекс — задача → секція

|Роблю…                                                      |Дивлюсь                |
|------------------------------------------------------------|-----------------------|
|Новий HTML-кістяк продукту (head/manifest/icons)            |A1–A4                  |
|Тема (light/dark/auto), FOUC                                |A5–A8                  |
|Підсвітка обраного = глянцева капсула «D2» (toggle/select)  |A6 §3                  |
|Повноекранний layout, висоти, viewport                      |A9–A13                 |
|Каркас екрана (top stack, nav, app-bar)                     |A14–A16                |
|Bottom sheet (структура / анімація / свайп)                 |A17–A21                |
|Свайп рядка списку з діями (edit/delete)                    |A22                    |
|Блокування (orientation / zoom / long-press)                |A23–A25                |
|Доступність, motion, sync теми між вікнами                  |A26–A28                |
|Іконки, поліш, z-index, empty state                         |A29–A32                |
|Тип картки: accent-rail + кольорова семантика               |A34–A35                |
|Chrome форма + dark-elevation (pinned-зона)                 |A61                    |
|Range-календар / date-range scope у sheet                   |A33                    |
|Ховаю елемент `[hidden]` поряд з `display:flex`             |A36                    |
|Два хрести в полі пошуку (нативний + власний)               |B3.1                   |
|Native-контроли (date/time/select) в один рядок             |A40                    |
|Native picker сірий/не міняє тему в PWA                     |A41                    |
|Текст поверх ілюстрації/SVG → скрим                         |A42                    |
|Inline layered SVG як фон картки/геро                       |A43                    |
|Об’єм на темній: тон, не тінь                               |A45                    |
|Картки: card-in-card + стат-плитки (3 в ряд)                |A46–A47                |
|Секція-eyebrow (uppercase) + лінія-роздільник зон           |A48                    |
|Чіп-плашка частки + підсилення числа (`.n`)                 |A49                    |
|Підняв картки → підніми хром; власний токен, не реюз surface|A62                    |
|Картки в шіті/панелі зливаються (card-on-card) → recess     |A63                    |
|Баланс контрол-ряду між хедером і списком (подвійний зазор) |A64                    |
|Тогл-перемикач увімк/вимк (`.sw`)                           |A52                    |
|Кастом тап-селект замість нативного `<select>`              |A53                    |
|Анімований повзунок у сегмент-перемикачі (slide)            |A54                    |
|PWA: гола смуга знизу / overlay-бар зі склом                |A55 (+A1/A9/A10/A15)   |
|Bottom-nav — ПОВНИЙ еталон (скло+капсула+іконки)            |A56 (база A54/A55)     |
|Motion-мова: драбина тривалостей + easing + снап/слайд      |A57 (звід A18/27/54/56)|
|Sheet-меню/профіль (genSheet+grouped-cards+About+кредит)    |A58                    |
|Мікро: toast / sync-pill / sparkline / confirmAction        |A59                    |
|Місяць-пікер 3×4 + floor-guard + рік-пігулка (core)         |A60 (промоут A50)      |
|Дві мови глибини: well-поле (deboss) vs кнопка (lift); токен|A65 (промоут A51)      |
|Elevation асиметричний між темами (drop≥14px / світло-зверх)|A66 (розшир. A45)      |
|Press-механіка тапу: JS pointerdown/up; scale∝1/розмір      |A67                    |
|Card-select (велика картка): persistent-DOM+opacity-ring+WAAPI|A67.1 (база A67/A54)  |
|Прев'ю-пісочниця Claude: лише console.log/warn/error         |A68                    |
|Cross-theme fused-шов: дизайнити по кожній темі; auto-override|A69 (інстанс A39)     |
|Кільце/обведення під layout-рухом: border > box-shadow       |A70 (база A67.1/A57)   |
|Row-stagger reveal — каскадна поява рядків (generic)         |A71                    |
|Scroll-linked: рівність вартості > її величина; rAF-демпфер  |A72 (база A70/A45)     |
|Offline / черга / realtime / клавіатура / форми             |B (продукт-специфіка)  |

-----

# Частина A — Універсальні iOS PWA патерни ✅

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

## A6. Theme dropdown 3-mode (auto/light/dark) + глянцева капсула обраного ✅

3-режимний перемикач теми в app-bar: trigger-кнопка (іконка sun/moon crossfade) відкриває `role="menu"` з 3× `role="menuitemradio"`. Обраний режим = **глянцева капсула «D2»** (об’єм від блік+градієнт, не від насиченості → на темній не «світиться»). Auto-режим: капсула на тій строці, що зараз active — прив’язка до **СТАНУ**, не до фіксованої теми.

### §1 — HTML (структура)

```html
<div class="theme-wrap">
  <button class="icon-btn" id="btnTheme" aria-label="Тема" aria-haspopup="true" aria-expanded="false">
    <!-- sun/moon crossfade svg (опц., product-specific) -->
  </button>
  <div class="theme-menu" id="themeMenu" role="menu" hidden>
    <button class="theme-item" data-mode="light" role="menuitemradio">
      <svg class="ti-icon" …></svg><span class="ti-label">Світла</span><svg class="ti-check" …></svg>
    </button>
    <button class="theme-item" data-mode="dark"  role="menuitemradio"> … Темна … </button>
    <button class="theme-item" data-mode="auto"  role="menuitemradio"> … Системна … </button>
  </div>
</div>
```

### §2 — CSS (контейнер + пункт)

```css
.theme-wrap{position:relative;flex-shrink:0}
.theme-menu{position:absolute;top:calc(100% + 6px);right:0;min-width:168px;
  background:var(--surface-2);border:1px solid var(--border-default);
  border-radius:var(--rs);box-shadow:var(--sh2);padding:4px;
  display:flex;flex-direction:column;gap:3px;          /* gap:3px — повітря під glossy-капсулу */
  z-index:200;animation:tm-in .12s ease-out}
.theme-menu[hidden]{display:none}
@keyframes tm-in{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}
@media (prefers-reduced-motion:reduce){.theme-menu{animation:none}}

.theme-item{display:flex;align-items:center;gap:9px;width:100%;padding:9px 10px;
  border-radius:var(--rxs);font-size:13px;color:var(--text-primary);text-align:left;
  border:1px solid transparent;                          /* резервує 1px → active не зсуває layout */
  transition:background .1s,box-shadow .12s ease,border-color .12s ease;cursor:pointer}
.theme-item:active{background:var(--surface-3)}
.theme-item .ti-icon{flex-shrink:0;color:var(--text-secondary)}
.theme-item .ti-label{flex:1}
.theme-item .ti-check{flex-shrink:0;color:var(--accent);opacity:0;transition:opacity .1s}
```

**Концентричні кути (не на око):** меню `--rs`=10, пункт `--rxs`=6, gutter=`padding` 4 → 10−4=6 → дуги паралельні. Зміниш padding — перерахуй `--rxs`, інакше кути «гуляють».

**gap:3px — стеля, не довільно.** Світла капсула має drop-тінь `0 3px 7px` (зсув 3px): gap 3 кладе зсув на фон меню, а не на сусідній рядок. <3 — тінь бруднить сусіда; >3 — меню «розсипається» на окремі картки + темна тема (без drop-тіні) лише розсувається без виграшу. Одна геометрія на обидві теми.

### §3 — CSS: глянцева капсула обраного «D2» (канон)

```css
/* обрана тема = глянцева капсула. Світла = баланс «m» (світліший верх + стримана тінь).
   Текст/іконка/галка = --accent-text. */
.theme-item.active{
  color:var(--accent-text);font-weight:600;
  background:linear-gradient(180deg,
    color-mix(in srgb,var(--accent-soft) 66%,#fff),
    color-mix(in srgb,var(--accent-soft) 96%,var(--accent)));
  border-color:color-mix(in srgb,var(--accent) 24%,transparent);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.95),   /* специлярний блік зверху */
             inset 0 -1px 0 rgba(20,30,25,.07),       /* нижня внутр. грань */
             0 1px 2px rgba(20,30,25,.11),            /* контактна тінь */
             0 3px 7px rgba(20,30,25,.07);            /* м'яка drop-тінь (тільки СВІТЛА) */
}
.theme-item.active .ti-icon{color:var(--accent-text)}
.theme-item.active .ti-check{opacity:1;color:var(--accent-text)}

[data-theme="dark"] .theme-item.active{                /* tone+inset, БЕЗ drop (A45/A39) */
  background:linear-gradient(180deg,
    color-mix(in srgb,var(--surface-4) 88%,var(--accent)),var(--surface-3));
  border-color:color-mix(in srgb,var(--accent) 14%,transparent);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.06),inset 0 -1px 0 rgba(0,0,0,.2);
}
```

**Чому світла й темна РІЗНІ:** на темній drop-тіні невидимі (A45) → об’єм несе тон (`surface-4` зверху → `surface-3` знизу) + легкий inset-блік. Drop-шарів на темній **нема навмисно**.

### §4 — JS (логіка, persist, listeners)

**FOUC inline — у `<head>`, ДО CSS і first paint (A5):**

```html
<meta name="theme-color" content="#0E1311">   <!-- default dark для PWA splash -->
<script>(function(){try{
  var saved=localStorage.getItem('dl-theme'), mode=saved||'auto';
  var dark=mode==='dark'||(mode==='auto'&&matchMedia('(prefers-color-scheme:dark)').matches);
  var html=document.documentElement;
  html.setAttribute('data-theme',dark?'dark':'light');
  html.setAttribute('data-theme-mode',mode);
  var meta=document.querySelector('meta[name="theme-color"]'); if(meta)meta.content=dark?'#0E1311':'#F4F7F5';
}catch(e){document.documentElement.setAttribute('data-theme','dark');
  document.documentElement.setAttribute('data-theme-mode','auto');}})();</script>
```

**Body JS:**

```js
const THEME_KEY='dl-theme';
function getThemeMode(){try{return localStorage.getItem(THEME_KEY)||'auto';}catch(e){return 'auto';}}
function applyTheme(){
  const mode=getThemeMode();
  const dark=mode==='dark'||(mode==='auto'&&matchMedia('(prefers-color-scheme:dark)').matches);
  const html=document.documentElement;
  html.setAttribute('data-theme',dark?'dark':'light');
  html.setAttribute('data-theme-mode',mode);
  const meta=document.querySelector('meta[name="theme-color"]'); if(meta)meta.content=dark?'#0E1311':'#F4F7F5';
  document.querySelectorAll('.theme-item').forEach(it=>it.classList.toggle('active',it.dataset.mode===mode));
  const lbl=mode==='auto'?'Системна':mode==='dark'?'Темна':'Світла';
  $('btnTheme').setAttribute('aria-label','Тема: '+lbl);   // VoiceOver читає стан
  placeAllThumbs(true);   // ⚠ PRODUCT-HOOK: re-snap анімованих thumb після зміни теми. НЕМА thumb → ВИДАЛИТИ.
}
function setThemeMode(mode){try{if(mode==='auto')localStorage.removeItem(THEME_KEY);else localStorage.setItem(THEME_KEY,mode);}catch(e){}applyTheme();}

document.documentElement.classList.add('no-transition');        // A27 — без миготіння на init
applyTheme();
requestAnimationFrame(()=>requestAnimationFrame(()=>document.documentElement.classList.remove('no-transition')));

matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if(getThemeMode()==='auto')applyTheme();}); // live в auto, iOS 18+
window.addEventListener('storage',e=>{if(e.key===THEME_KEY)applyTheme();});   // A28 multi-window

const btnTheme=$('btnTheme'),themeMenu=$('themeMenu');
btnTheme.addEventListener('click',e=>{e.stopPropagation();const opening=themeMenu.hidden;themeMenu.hidden=!opening;btnTheme.setAttribute('aria-expanded',String(opening));});
document.querySelectorAll('.theme-item').forEach(item=>{item.addEventListener('click',e=>{e.stopPropagation();setThemeMode(item.dataset.mode);themeMenu.hidden=true;btnTheme.setAttribute('aria-expanded','false');});});
document.addEventListener('click',e=>{if(!themeMenu.hidden&&!themeMenu.contains(e.target)&&!btnTheme.contains(e.target)){themeMenu.hidden=true;btnTheme.setAttribute('aria-expanded','false');}});
```

**`stopPropagation` на btn І item — обов’язковий**, інакше outside-click listener закриє меню одразу.

### §5 — Залежності (перенесеш компонент — перенеси і їх)

- **A24** — `button{background:none}` у global reset **ОБОВ’ЯЗКОВО**. `.theme-item` прозора, фон дає `.theme-menu`. Без — iOS малює ButtonFace (#e7e7e9) → панель «сіра» лише в цьому компоненті. Симптом: семпл пікселя #e7e7e9.
- **A8** — специфічність: `.theme-item.active`(0,2,0) ПІСЛЯ `.theme-item:active`(0,2,0); `[data-theme=dark] .theme-item.active`(0,3,0) виграє на темній. Конфлікту нема (звірено B42).
- **A5** — FOUC inline ДО CSS. **A26** — a11y: `aria-haspopup/expanded` на btn; `role=menu/menuitemradio`; динамічний `aria-label='Тема: '+lbl`. **A7** — 3-шарові токени. **A27** — `no-transition` на init (double-rAF). **A28** — `storage` listener (синк вкладок).
- **product-hook** — хвіст `applyTheme` (`placeAllThumbs`) re-снапить анімовані повзунки. Нема таких → **прибрати рядок**.

### §6 — Портативність (копіпаст у інший Lens)

Структура HTML + усі **формули** (gradient/border/shadow/gap/радіуси) переносяться **1:1**. Міняються **лише токени** під палітру: `--surface-2` (фон меню), `--surface-3/4` (низ/верх dark-капсули + `:active`), `--border-default` (бордер), `--accent / --accent-soft / --accent-text` (градієнт/бордер/текст), `--rs/--rxs` (радіуси — тримай rs−padding=rxs), `--sh2` (тінь меню).

**Хардкоди, не токени** (свідомо): `#fff` (специлярний блік — універсальний); `rgba(20,30,25,…)` (near-ink тінт тіні — лиши нейтральним або підстав найтемніший ink продукту); meta `theme-color` (свої splash-кольори).

**Compare ОБОВ’ЯЗКОВИЙ під чужу палітру (A39):** ті самі формули читаються по-різному на іншому hue/контрасті. Обидві теми на device перш ніж лочити (балансні ступені light: a/b/**m**). gap теж перевірити — стеля 3px, оптимум залежить від сили тіні палітри.

### §7 — Анти

- ❌ Звужувати капсулу в «острівець» з полями — ламає концентричний нест + менш нативно (iOS меню підсвічує рядок майже на всю ширину).
- ❌ gap >3px — меню розпадається на картки; темна без drop-тіні лише розсувається.
- ❌ Забути `button{background:none}` (A24) → ButtonFace.
- ❌ `.active` перед `:active` (A8 — мовчазний clobber).
- ❌ drop-тінь на ТЕМНІЙ капсулі — невидима + неправильно; темна = tone+inset.
- ❌ Забути динамічний `theme-color` meta → не той колір splash/статус-бару PWA.
- ❌ Прибрати `stopPropagation` → меню закриється одразу при відкритті.

**Зв’язок:** A5 (FOUC), A7 (токени), A8 (специфічність), A24 (button reset), A26 (a11y), A27 (init), A28 (multi-window), A45/A39 (об’єм тоном на темній / світла≠темна). 🔧 ключ `<prod>-theme`. *Source: B42 — CSS р.166–189, HTML р.897–920, JS р.20–35 (FOUC)+2702–2728. Drive Lens B42 (капсула D2) + gap:3px.*

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

## A15. Bottom nav — 3-state padding (критичний fix)

```css
.bottom-nav{ padding-bottom:8px; }                          /* Safari */
@media(display-mode:standalone){ .bottom-nav{ padding-bottom:0; } }  /* PWA: контейнер БЕЗ padding */
html.pwa-full .nav-i{ padding-top:8px; padding-bottom:calc(8px + var(--sab)); }  /* PWA: padding на ЕЛЕМЕНТ */
```

Інакше: порожнеча між іконками і home indicator АБО іконки під ним (нетапаються). Anti-pattern: padding на контейнер у PWA.

## A16. App-bar scroll elevation

`box-shadow` на app-bar коли `.scroll-a` скролили >8px. Кешований `_appBar` + RAF-throttle на scroll listener; reset `.scrolled` при tab switch. Premium-feel native.

## A17. Bottom sheet — структура

`.sh-bg` (fixed inset:0, backdrop, flex-end, z:300) → `.sh-box` (`border-radius:16px 16px 0 0`, `max-height:85dvh`, `overflow-y:auto`, `padding-bottom:env(safe-area-inset-bottom)`) → `.sh-grip-w/.sh-grip` + `.sh-head`(title+×).

## A18. Bottom sheet — enter/exit анімація

**Проблема:** `display:none↔flex` не анімується («пстрик»). **Default = CSS visibility/opacity/transform:**

```css
.sh-bg{ position:fixed; inset:0; display:flex; align-items:flex-end; z-index:300; background:rgba(0,0,0,.5);
  visibility:hidden; opacity:0; pointer-events:none;
  transition:opacity .24s ease, visibility 0s linear .26s; }      /* visibility ховається ПІСЛЯ слайду */
.sh-bg.open{ visibility:visible; opacity:1; pointer-events:auto; transition:opacity .24s ease, visibility 0s; }
.sh-box{ transform:translateY(100%); transition:transform .26s cubic-bezier(.32,.72,0,1); }   /* iOS easing */
.sh-bg.open .sh-box{ transform:translateY(0); }
@media(prefers-reduced-motion:reduce){ .sh-bg,.sh-box{ transition:none } }
```

**Обов’язково:** `pointer-events:none` на закритому (бо тепер завжди flex); delayed `visibility` (лишається видимим весь слайд, ховається після); **без `will-change`** (постійний GPU-шар = композитинг-шви); ніде не покладатись на `display:none`.

**Передумова безпеки:** swipe-to-close — **end-only** (A19). Якщо колись live-follow → вимикати transition на час drag.

**Альтернативи (НЕ default):** `@starting-style`+`transition-behavior:allow-discrete` (iOS 17.4+, без UX-виграшу); **JS Web Animations API** `el.animate()` — лише для складного/переривчастого руху, springs, послідовностей; ціна: ловити `anim.finished` перед приховуванням, `anim.cancel()` на швидкий повтор, init/reduced-motion вручну = більше точок злому. *(Параметри: Drive Lens Batch 10.2.)*

### A18.1 Асиметрія open/close + close-«примара» root-fix (QR B39, device✓) ✅

**(1) Open ≠ close — це ОКРЕМІ дизайн-рішення.** Симетрична крива відчувається мляво на закритті. Канон:
- **OPEN = decel** `cubic-bezier(.32,.72,0,1)` ~260ms — «рішуче прибуття» (швидкий старт, м'яке гальмо в кінці).
- **CLOSE = accel-in** `cubic-bezier(.4,0,1,1)` + мікро-`scale(.98)` — «рішучий відхід» (повільний старт, прискорення геть). Accel-in читається рішучіше за decel-out на закритті.

**(2) Close-«примара / розчинення» — root-fix.** Якщо `.sh-box` — **ДИТИНА** opacity-бекдропу `.sh-bg`, гасіння `opacity` БАТЬКА тане і бокс → на трохи довшому close (≈360–405ms) читається не як «з'їхав униз», а як «розчинився на місці» (на коротких 240ms ще збігало за слайд). **Фікс (used):** тримати оверлей `opacity:1` (твердий → бокс непрозорий), дим гасити через **`background:rgba(0,0,0,.5)→rgba(0,0,0,0)`**, бокс з'їжджає off-screen НЕПРОЗОРИМ. **Альт-фікс:** зробити бокс **сиблінгом** бекдропу (не дитиною) — тоді opacity батька його не чіпає (як у scratch-комперах #bg/#sheet сиблінги).

```css
.sh-bg{ --sh-close:360ms; ... visibility:hidden;opacity:0;pointer-events:none;
  transition:opacity .24s ease,visibility 0s linear .26s; }
.sh-bg.open{ visibility:visible;opacity:1;pointer-events:auto;transition:opacity .24s ease,visibility 0s; }
.sh-box{ transform:translateY(100%); transition:transform .26s cubic-bezier(.32,.72,0,1); } /* OPEN decel */
.sh-bg.open .sh-box{ transform:translateY(0); }

/* CLOSE-фаза (клас .closing на час закриття) */
.sh-bg.closing{ opacity:1; background:rgba(0,0,0,0);                 /* оверлей твердий, дим гасне фоном */
  transition:background calc(var(--sh-close) - 40ms) ease, visibility 0s linear var(--sh-close); }
.sh-bg.closing .sh-box{ transform:translateY(100%) scale(.98);
  transition:transform var(--sh-close) cubic-bezier(.4,0,1,1); }     /* CLOSE accel-in + micro-scale */
@media(prefers-reduced-motion:reduce){ .sh-bg,.sh-box,.sh-bg.closing,.sh-bg.closing .sh-box{transition:none} }
```
```js
function closeSheet(bg){
  if(bg._ct) clearTimeout(bg._ct);                 // guard rapid open/close
  bg.classList.add('closing');
  bg._ct=setTimeout(()=>{ bg.classList.remove('open','closing'); bg._ct=null; }, parseFloat(getComputedStyle(bg).getPropertyValue('--sh-close'))||360);
}
```

**Один токен `--sh-close`** керує: transform боксу + тривалістю згасання фону (`-40ms`, щоб дим зник трохи раніше за слайд) + затримкою `visibility` (ховаємо ПІСЛЯ повного слайду). Одна ручка тюнить усе закриття.

**Контрол усередині шіта, що закриває:** якщо кнопка В шіті тригерить close (напр. «Скинути»), **відклади close** на ~250ms — щоб її власна press-пружина встигла прочитатись перед слайдом (інакше шіт зникає раніше за фідбек кнопки).

**device✓ значення (QR B39, Konst):** open 260ms decel · close `--sh-close:360ms` accel-in + `scale(.98)` · backdrop-fade `320ms` (`-40`) · reset-delay 255ms. **Slow-mo BAKE-провенанс (wsd 2.4):** тюнено на ×1.5 (270→405 / 170→255); у проді ретюнено вниз до 360 (×1 не потребував 405). **ПОРТ:** ✅ універсальний для будь-якого bottom-sheet (KPI/Drive). **Зв'язок:** A57 (close-асиметрія в motion-мові), A20 (3 способи закриття — усі через `closeSheet`). *Source: `QR_Lens_preview_batch41_1.html` р.523–528.*

## A19. Bottom sheet — swipe-to-close (end-only)

```js
function addSwipeClose(bgId, closeFn){
  const box = document.querySelector('#'+bgId+' .sh-box');
  if(!box || box._sw) return; box._sw = true;                 // guard (A21)
  let sy=0, ss=0, gt=false, ig=false;
  box.addEventListener('touchstart', e=>{ sy=e.touches[0].clientY; ss=box.scrollTop;
    gt=!!e.target.closest('.sh-grip-w');
    ig=!!e.target.closest('.fg-grid')||!!e.target.closest('.pk-list')||!!e.target.closest('.cal-grid')||!!e.target.closest('.mg-grid')||!!e.target.closest('.mg-y');
  },{passive:true});
  box.addEventListener('touchend', e=>{ const dy=e.changedTouches[0].clientY-sy;
    if(gt && dy>40) closeFn();                                // grip: dy>40 завжди
    else if(!ig && ss===0 && dy>64) closeFn(); },{passive:true});  // content: scrollTop===0 AND dy>64 AND не на ig-елементі
}
```

Grip `dy>40` завжди; контент закриває ТІЛЬКИ якщо `scrollTop===0` на старті AND `dy>64`. **Не** просте `dy>N` без scrollTop — агресивне закриття при скролі вгору.

**❗ Прапор `ig` (ignore-list) — обов’язкова частина, не опція (batch41).** Якщо touchstart почався на внутрішньому скрольному/інтерактивному елементі (`.fg-grid` гейдж · `.pk-list` тап-селект · `.cal-grid`/`.mg-grid` сітки календаря · `.mg-y` рік-пігулка) — вертикальний свайп там НЕ закриває шіт (`!ig`-гард). Без нього скрол списку всередині шіта або горизонт-свайп по сітці тягне шіт донизу й закриває його. **При порту/новому шіті:** будь-який доданий усередину скрольний список або власний-свайп елемент (A44) ОБОВ’ЯЗКОВО додати в `ig`-набір. Крос-реф: A33 (cal/mg-grid), A44 (горизонт-свайп), A53 (pk-list), A50/A60 (рік-пігулка). *(Drive Lens, підтверджено аудитом batch41 Round 3.)*

## A20. Bottom sheet — 3 способи закриття

(1) `×` у head; (2) свайп вниз (A19); (3) тап на backdrop: `if(e.target===e.currentTarget) close()` (саме на `.sh-bg`, не на `.sh-box`).

## A21. Listener registration «once-for-life»

Guard через property на DOM-елементі: `if(box._sw) return; box._sw=true;`. Sheet-елементи persist у DOM (не destroyed при close) → без guard кожне відкриття додає listener → N callbacks per swipe. (Альтернатива — WeakSet, але property простіше.)

## A22. Swipe-row — рамка-пігулка (single-frame), tap=edit / swipe-left=дії

**Нюанс (головне):** заокруглення-силует — властивість **ОДНОГО зовнішнього фрейму** (`.sw-row`), НЕ продубльована на картці й панелі дій. Картка й дії — співмешканці фрейму, а не дві рівноправні закруглені картки. Картка віддає власну рамку (`border:none; margin-bottom:0`); панель дій не має радіуса (бере від `overflow:hidden` фрейму); при відкритті у картки сплющуються лише ЗАДНІ кути → шов «картка→дії» прямий. *Це «майже як картка, але навмисно не зовсім».*

```css
.sw-row{ position:relative; margin-bottom:8px; border-radius:var(--r); overflow:hidden; border:1px solid var(--border-subtle); }
.sw-row .rec,.sw-row .rf{ margin-bottom:0; position:relative; z-index:1; border:none;
  transition:transform .2s cubic-bezier(.4,0,.2,1), border-radius .2s; }
.sw-row.sw-open .rec,.sw-row.sw-open .rf{ transform:translateX(-148px);          /* == 2×74 */
  border-top-right-radius:0; border-bottom-right-radius:0; }
.sw-actions{ position:absolute; top:0; right:0; bottom:0; display:flex; z-index:0;
  visibility:hidden; transition:visibility 0s linear .2s; }
.sw-row.sw-open .sw-actions{ visibility:visible; transition-delay:0s; }
.sw-act{ width:74px; … } .sw-act.edit{ background:var(--accent) } .sw-act.del{ background:var(--crit) }
```

**Обов’язково:** (1) ширина зсуву == сума ширин дій (`148==2×74` — єдина точка зв’язку); (2) картка над діями `z-index:1` vs `0`; (3) delayed `visibility` на `.sw-actions` (клікабельні поки відкрито, ховаються після); (4) transition картки включає `border-radius` (інакше кути стрибають); (5) `overflow:hidden` на фреймі — обов’язково.

**Жест — end-only** (як A18): рішення лише на `touchend` (поріг `SW_TRIG=44`, slop `SW_SLOP=10`), без live-follow. Горизонт>вертикаль і |dx|>SW_TRIG → відкрити/закрити; тап (не свайп) закритого → edit, відкритого → закрити; тап поза рядком → `closeAllSwipe()` (документний listener з guard); лише один рядок відкритий. Кнопки дій — `stopPropagation` → close → дія. *(Drive Lens Batch 10/10.2, device-валідовано.)*

**❗ Scroll-захист — `passive:false` + `preventDefault()` ЛИШЕ на осі `x` (batch41-корекція).** Раніше тут писалось «end-only passive без preventDefault» — це **невірно** для реального коду. `.sw-row` сидить у вертикально-скрольному списку (`.scroll-a` журнал), тож `touchmove` мусить бути `{passive:false}` і гасити нативний скрол `preventDefault()` **виключно** коли вісь зафіксована в `x` (axis-lock 10px) — інакше неохайний горизонт-свайп або закриття смикає сторінку (page-jump). Вертикальний скрол лишається рідним (preventDefault не на `y`). Це **той самий механізм, що A44** — A22 і A44 не «passive vs passive:false», а один axis-lock; різниця лише, КУДИ вішати слухач (A22 — сам рядок-`front`; A44 — nav-смужка, бо там під свайпом тап-цілі). Рішення (відкрити/закрити) — усе одно на `touchend` (end-only). *(Drive Lens, підтверджено аудитом batch41 Round 3.)*

> ✅ **Direction-lock — device-валідовано (Batch 11, iPhone XS PWA).** Розрізнення горизонт-свайп (дії рядка) vs вертикальний скрол на `touchend` (slop=10, trig=44) на пристрої комфортне — скрол не плутається з відкриттям дій. Лишаємо end-only; live-follow (нижче) НЕ потрібен для цього UX.

> 💭 Можливий варіант на майбутнє: **live-follow** (Telegram-стиль, transform слідує за пальцем + spring). Тоді обов’язково: direction-lock у перші px + `{passive:false}` preventDefault на горизонталі + transition-off під час drag + spring-snap на release. Більше точок злому — прототипувати окремо, не чіпаючи валідований end-only.

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

## A26. A11y attributes

Theme dropdown: `aria-label/aria-haspopup/aria-expanded`, `role="menu"`+`role="menuitemradio"`, dynamic `aria-label='Тема: '+lbl` (VoiceOver читає стан). Іконкові nav-кнопки: `aria-label` («Попередній день» тощо).

## A27. Reduce-motion + no-transition при init

`@media(prefers-reduced-motion:reduce){ animation:none }`. Anti-fade на launch (CSS vars міняються при applyTheme): додати `.no-transition` (`transition:none!important`) → `applyTheme()` → зняти через **double `requestAnimationFrame`** (гарантія, що клас додано й знято в різних frames). Косметичний uplift.

## A28. Storage event — multi-window sync

```js
addEventListener('storage', e => { if (e.key==='<prod>-theme') applyTheme(); });
```

Тема змінена в Safari tab → PWA оновлюється (між Safari↔PWA standalone: iOS 17.4+).

## A29. SVG icons — inline + стандартні розміри

Усі inline (не icon-font): `stroke="currentColor"`, `fill="none"`, `stroke-width` 2/1.8/2.5, `linecap/linejoin="round"`. Розміри: chevron 12; menu/search/filter 14; theme/close 16; nav tabs 20; nav arrows 18; empty state 34.

## A30. Premium polish

1. **Scroll-fade краї chips:** `mask-image:linear-gradient(to right,transparent,#000 20px,#000 calc(100% - 20px),transparent)` + `scrollbar-width:none`.
1. **Status-tint фон:** `background:linear-gradient(180deg,var(--card),color-mix(in srgb,var(--warn) 6%,var(--card)))` (Safari ≥16.2).
1. **Micro tap:** `:active{ transform:scale(.97) }` — лише на ключових CTA.
1. **Live pulse:** `@keyframes livePulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.75)}}` (sync/live dot).

## A31. Z-index стек

app-bar(scrolled) 20 · theme menu 200 · bottom sheets 250–300 · onboarding 9000 · orientation lock 9999/10000. Тримати єдиний стек на продукт.

## A32. Empty state

`.empty-state{ min-height:55dvh; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px }` (vertical centering на будь-якому vh) + `.empty-ico` коло 76px + текст/підказка + `.goto-btn` (accent CTA).

## A33. Range-календар у bottom sheet (tap-based, sweep)

**Задача:** ізолювати день/діапазон у списку; нативний `<input type=date>` НЕ вміє range-sweep (лише один день).

**Рішення — власний грид у sheet:**

- **Пн-перший грид:** `lead=(dowISO(firstISO)+6)%7`; `dim=new Date(y,m,0).getDate()`.
- **State machine** (`calS`/`calE` — temp ISO): тап коли `!calS` або (`calS && calE`) → новий старт (`calS=iso, calE=null`); інакше `calE=iso`. `renderCal` нормалізує `lo/hi` (`s<e`).
- **Sweep CSS:** in-range `.r0`=`--accent-soft`; кінці `.r1/.r2`=solid `--accent` + border-radius cap (21px з одного боку); single `.r3`=pill 21px. today-dot `::after` (білий на solid).
- **Apply** → `S.scopeStart/scopeEnd` + `activeDay=lo`. Список фільтрує через `inScope(d)`: `(!start||!end)?true:(d>=start&&d<=end)`.
- **date-btn label** = `fmtRange(s,e)`: same-day→`fmtShort`; same-month→`15–30 тра`; інакше `1 тра – 3 чер`.

**Хедер `◂ лейбл ▸`** (Batch 24): стрілки по краях, лейбл по центру; спільний клас `.cal-nav-btn` (34px, radius 10, surface-3, `.off`=opacity .34 + `pointer-events:none`). Уніфікувати по ВСІХ календарях Lens (день-грид + місяць-пікер 3×4). **Лейбл = пігулка** (Batch 25.2): не плоский текст, а `surface-3 + border + radius` (height 34, як стрілки) — афорданс «це інтерактивно, чіпай/свайпай». ❗ У bottom-sheet НЕ копіювати Tab-4 `.mo-lbl` дослівно (там `surface-2` на сторінці-`surface-1`): sheet=`surface-2` → пігулка має бути `surface-3`, інакше зіллється з фоном шіта. Tap-feedback `:active{background:surface-4}`.

**Навігація-межі** (Batch 24): назад = `dataFloor()` (місяць найранішого запису; гасити prev на floor + cells до floor `disabled`); **вперед — БЕЗ межі**. ❗ НЕ прибивати на «кінець року» — це прихована стіна на переході Гру→Січ (клас помилки). Котити рік через `m++;if(m>12){m=1;y++}`.

**Свайп вліво/вправо = бонус** (Batch 25.1), стрілки — основний. ❗ **Вішати на ХЕДЕР-смужку (`◂лейбл▸`, `id=calHdr`), НЕ на сітку днів.** Сітка володіє тапом (вибір дня) — свайп на ній краде тап: навіть «неохайний» тап з горизонт. зсувом >10px лочиться в осі `x`, `preventDefault` гасить `click`, і день не вибирається (саме так зламалось у Batch 25 → виправлено 25.1). Порт місяць-свайпу: axis-lock end-only (lock 10px → спрацювання 50px), горизонт→`calStep`, вертикаль→віддати sheet-у. `touchmove` під `{passive:false}` з `preventDefault()` **лише** на осі `x` (див. **A44**). На хедері `_swiped` гасить хибний `click` по стрілці (щоб свайп+синтетик-клік не дали подвійний крок). Логіка кроку — спільна `calStep(dir)` для стрілок І свайпу (DRY, одна точка floor-guard).

**Фікс-висота = 6 рядків завжди** (Batch 25): добивати порожніми `.cal-c.blank` до **42 комірок** (`trail=42-(lead+dim)`). Місяці мають 4/5/6 тижнів → без фіксу висота стрибає до ~88px при гортанні (комірка 42px + row-gap 2px: 4р=174 / 5р=218 / 6р=262). Стрибок = палець був на одному рівні, після зміни місяця вікно поїхало. `visibility:hidden` блокам тримає бокс у потоці → стала висота. **Майже передумова свайпу** — без неї контейнер плигає посеред жесту.

**Вікенд-маркер Сб/Нд** (Batch 25.1): **лише шапка** — `.cal-wd span.we{color:var(--text-secondary)}` (Сб/Нд темніші за будні-`--text-muted`). ❗ НЕ семантичний акцент і НЕ заливка: вихідні — це **структура календаря**, не категорія даних. Усі акценти зайняті значенням (зелений=дія/вибране, охра `--vibe`=вайб-поїздки, синій `--info`=паливо) → будь-який з них дав би фальшивий зчит. *Device-урок (25→25.1): нейтральна заливка комірок (`--surface-4`) на пристрої виглядала важко/зайво — відкотили до шапки-маркера. Compare-файл «виглядав ок», device сказав ні (wsd 2.4 — фінальний арбітр пристрій).*

**iOS / пастка:** swipe-to-close sheet (A19) МУСИТЬ тримати `.cal-grid` (і `.mg-grid`) у прапорі `ig` (`touchstart`), інакше вертикальний свайп по гриду закриває sheet. Власний горизонт-свайп календаря (A44) із цим не конфліктує: горизонталь → `preventDefault`+`calStep`; вертикаль → ax=‘y’, без preventDefault, але `.cal-grid` в `ig` → sheet не закривається (нейтрально). Tap-target клітинки `height:42px`.

**Reuse:** KPI Lens періоди, QR Lens вікно візитів — будь-який Lens із date-range scope. Drop-in: грид+state-machine+хедер+свайп+фікс-висота+вікенд-тинт — цілісний компонент.
*(Tap/sweep/ignore — Drive Lens Batch 11, device-валідовано iPhone dark+light. Хедер/межі — Batch 24. Свайп/фікс-висота/вікенд-тинт — Batch 25, **device-test pending**.)*

-----

## A34. Accent rail — ліва смужка-ідентифікатор типу на картці-рядку ✅

**Що.** Вертикальна смужка ~4px на лівому краї картки-рядка (`.rec`/`.rf`/будь-який list item); колір = тип. Миттєвий тип-маркер без тексту.

**Реалізація:** `::before` на картці (НЕ окремий DOM-вузол), картка `position:relative; overflow:hidden` (клип смужки під радіус):

```css
.rec{position:relative;overflow:hidden}
.rec::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px}
.rec.work::before{background:var(--accent)}   /* робота = зелений */
.rec.vibe::before{background:var(--vibe)}     /* вайб   = бурштин */
.rf::before{background:var(--info)}            /* заправка = синій */
```

**Обов’язково:** (1) `overflow:hidden` на картці — інакше смужка стирчить за заокруглення; (2) колір за кольоровою семантикою (A35), не довільний; (3) `::before`, не зайвий вузол.

**Reuse:** будь-який Lens зі списком типізованих рядків. *(Drive Lens, device-валідовано: світла+темна.)*

## A35. Кольорова семантика Lens ✅

Єдина крос-продуктова мова кольору. **Колір = зміст, не оздоблення.**

|Зміст                       |Токен                 |Де                                                           |
|----------------------------|----------------------|-------------------------------------------------------------|
|Робота                      |`--accent` (зелений)  |робочі поїздки, фільтр-чіп, accent rail work                 |
|Вайб / власне               |`--vibe` (бурштин)    |вайб-поїздки, vibe rail, split «власне»                      |
|Паливо                      |`--info` (синій)      |крапля скрізь, гейдж, кружок-заправка, fuel-тинт, split-літри|
|Нейтральне / типо-агностичне|`--text-primary` (ink)|дії, що НЕ належать одному типу (кнопка «Запис»)             |
|Критичне                    |`--crit`              |низький рівень палива, помилка                               |

**Правила:**

1. **Гліф позичає категорійний колір лише якщо однозначно тієї категорії.** Крапля = паливо → завжди синя. «Запис» може бути робота АБО вайб → нейтральна (НЕ зелена: зелений уже = робота).
1. **Ієрархія насиченістю, не хʼю.** Первинний маркер (кружок-заправка, KPI-клітинка, гейдж) — повний `--info`; вторинний inline-гліф у щільному списку — приглушений (`color-mix(in srgb,var(--info) 62%,var(--text-muted))`).
1. **Не змішувати в одному компоненті.** Паливний гейдж = весь синій (бари+краплі+значення), НЕ зелені бари + сині краплі.

*(Сформульовано з Drive Lens Batch 14 — уніфікація крапельки + нейтральні CTA.)*

## A36. `[hidden]` vs явний `display` — атрибут програє класу ✅

**Симптом.** `el.hidden=true` не ховає елемент, хоча в JS усе виглядає правильно.

**Корінь (не вгадувати).** UA-стиль `[hidden]{display:none}` має специфічність (0,1,0). Якщо у автора є `.X{display:flex}` (чи grid/block) — теж (0,1,0), РІВНА → перемагає **пізніший у коді** = авторський `.X{display:flex}`. Атрибут `hidden` мовчки ігнорується.

**Рішення:** підняти специфічність приховування під клас:

```css
.X[hidden]{display:none}   /* (0,2,0) > (0,1,0) */
```

**Grep-перевірка:** для кожного `.hidden=` / `hidden=` у JS — чи цільовий клас має явний `display`? Якщо так → потрібен `.X[hidden]{display:none}`.

**Прецедент:** Drive Lens Batch 15 — `filter-row{display:flex}` не давав `setTab` сховати панель на Паливі/Місяці (намір був, баг тихий). Споріднено з **A8** (theme-override specificity guard) — той самий клас «рівна специфічність б’є намір».

## A39. Подвійно-тематичний поліш — однакове число ≠ однаковий характер ✅

**Принцип.** Будь-який тематичний візуальний поліш (рамка, тинт, fill, тінь) планувати **на обидві теми одразу**, не порт однієї на іншу. Корінь: те, що формула токен-адаптивна (отже дає різний *колір* у темах) — НЕ гарантує однаковий *перцептивний характер*.

**Дві окремі речі (не плутати):**

1. **Токен-адаптивна формула** — `color-mix(in srgb,var(--X) P%,var(--surface-2))`. Сама дає різний рендер у кожній темі, бо `--X` і `--surface-2` різні. Це **правильний** механізм за замовчуванням (не хардкод hex).
1. **Перцептивна вага** — навіть при адаптивних токенах однакове `P%` читається інакше. Причини:

- **хʼю-контраст до surface** — теплий тон на холодному surface поппить (vibe-бурштин на зелено-сірому); cool-тон на cool-surface зливається (info-синій на тому ж зелено-сірому);
- око **найменш чутливе до синього** каналу (luminance-вага B = 0.07 проти G = 0.72);
- малі тинти на **темному** surface перцептивно стиснуті;
- **хроматичний** елемент важчий за **ахроматичний** при рівному `P%` (синя рамка > сіра рамка).

**Практика (a)/(b)/(c):**

- **(a)** формула токен-адаптивна за замовчуванням (color-mix із surface-токеном);
- **(b)** перевіряти **обидві** теми на колажі **на перцептивну вагу** — не лише ту, де народилась проблема. Колаж світла+темна = вхід (споріднено wsd 2.3);
- **(c)** якщо одна тема не тримає → **спліт через `[data-theme]` оверрайд** із власним числом, **A8-aware** (специфічність ≥ бази). НЕ компроміс посередині, що псує обидві.

**Діагностика — міряти, не гадати (споріднено wsd 14.7):** коли «на одній темі інакше» — порахувати рендер color-mix + **luminance-lift** (`0.2126R+0.7152G+0.0722B` від surface) + **хʼю-контраст до surface**. `P%` (= luminance) часто НЕ той важіль; буває, проблема в хʼю-сусідстві, і буп `P%` лише переб’є в інший бік.

**Тригер:** будь-який тематичний поліш рамки/тинту/fill/тіні.
**Анти-патерн:** «покращив темну → порт на світлу без перевірки»; «одне число на обидві, бо так чистіше».

**Зв’язок:** дзеркало surround-ефекту (wsd 14.8 — той самий hex інакший за **контекстом**; тут — за **темою**). Спліт реалізується механізмом A8.

**Прецеденти (Drive Lens):**

- **Пігулки Робочий/Вайб у шіті** (17.1) — спільну логіку зробили, світлу активну пігулку довелось фіксати **окремо** (soft-тинт + кольоровий текст; темну не чіпали).
- **CTA-баланс Запис/Заправка** (17.2) — рамку Заправки приглушено токен-адаптивно `info 58%`; перевірено обидві теми на колажі.
- **Hero fuel-тинт** — на світлій синій fuel найвидніший (lum-lift −12.8, темний хʼю на білому); на темній **читається** найтьмянішим попри середній luminance (+12.1), бо cool-на-cool зливається з зелено-сірим surface. Лік (якщо рівняти 2×2-ритм): спліт — світла 9% / темна ~14% (виміряно: +15.4 ≈ vibe +14.7, не кричить). Чистий приклад: **різне число на тему, бо однакове % читається інакше.**

**Прецедент-доповнення (Drive Lens Batch 30) — тон-даун великого жирного ГЕРО-числа.**
Симптом: геро-сума на темній (primary near-white, 26px/800) «підсвічує екран», топить ієрархію.
ХИБНИЙ важіль: мікс `primary↔secondary` — субперцептивний навіть на 60%. Дві причини: (1) обидва кінці світлі (secondary `#A1AAA6` теж яскравий) → крок ~4/канал нижче порога розрізнення; (2) велике жирне число дає МАСУ — око чіпляється за неї, не за дрібний зсув кольору.
РОБОЧИЙ важіль: мікс у бік **`--text-muted`** — `color-mix(in srgb,var(--text-primary) X%,var(--text-muted))` — реальний провал luminance. Лендинг 55% (`#B4BBB8` на темній): present, але не кричить. Dark-only спліт (A8): світлу НЕ чіпати — там primary=темний текст, проблеми нема.
Урок: коли «приглушення числа кольором не працює» — перевір, чи кінці міксу не обидва світлі. Важіль = мікс до **muted**, не до secondary.

**Прецедент-доповнення (QR Lens Phase 3, B37→B38) — S (насиченість) = домінантний неон-важіль на ТЕМНІЙ.**
Симптом: активний чіп на темній «неонить» (кричить), хоча fill не критично світлий.
ХИБНИЙ важіль: гасити **luminance** (затемнити fill) → губиться «обраність», а неон лишається.
РОБОЧИЙ важіль: **десатурація border/fill (S↓)** — border `S54→S30` при майже тій самій L: неон гасне у спокійний грей-тіл, заливка не темніє. Урок: на темному фоні «неон» несе **НАСИЧЕНІСТЬ**, не яскравість; важіль = **S**, не L (дзеркало геро-числа вище, де важіль — luminance-до-muted; тут — saturation).
**Дрейф значень (грепати КОД, не історію коментаря — wsd 12.1):** B37 `bg#152826 / text#98CDC8 / border#3D716C` (перший тон-даун, glow-кільце OFF) → B38 `bg#264a46 / text#fff / border#8ae5dc` (фінальний tone-lift, A66.1). `APP_BUILD`-коментар показує ОБИДВА — правда = **останнє в коді** (`batch41_1` р.485/541). Канон-приклад дрейфу: «device-pending» лейбли стають сталими, значення мігрують між батчами.

## A40. Native-контроли у флекс-рядку — інтринзік-ширина б’ється з flex ✅

**Принцип.** Коли кілька native form-контролів з нестандартною інтринзік-шириною (`input[type=date]`, `input[type=time]`, `select`, number-спінери) стоять поруч в одному flex-рядку — наївний розподіл flex дає одну з двох поломок. Не розтягувати жоден контрол ширший за його контент.

**Дві поломки (обидві device-спостережені, Drive Lens B19):**

1. **Тіснота** — рівний `flex:1` (50/50) морить контентно-довге поле (локалізована дата «6 черв. 2026 р.») → текст впирається в бордер.
1. **Float + overflow** — зробив одне поле `flex:1` (росте) → бокс ширший за контент, а native date **не ліво-вирівнює** значення у завеликому боксі → значення «плаває» (порожнеча збоку). Сусід `flex:0 0 auto` (shrink:0) при цьому жорсткий і **виштовхує рядок за контейнер** → горизонтальний overflow (виміряно +20px проти еталонного правого бордера).

**Корінь (два факти):**

- **CSSWG #6347 асиметрія:** `input[type=date]` **може** стискатись нижче контенту у flex; `input[type=time]`/text — **ні** (не нижче content min-width). Тому flex поводиться нерівно по рядку.
- **Native date не ліво-вирівнює** значення, коли бокс ширший за контент → «float».

**Рішення (device-валідовано, 3 раунди): обидва поля по контенту, ліво-пак, довге — зі `shrink:1` як анти-overflow guard.** Скоуп через `:has()`, щоб інші рядки (text+text) лишались 50/50.

```css
/* рядок з native date+time: обидва по контенту, ліво-пак */
.fld-row .fld:has(input[type=time]){flex:0 0 auto}                          /* короткий (час): фікс по контенту */
.fld-row:has(input[type=time]) .fld:has(input[type=date]){flex:0 1 auto}    /* довгий (дата): по контенту, shrink:1 = анти-overflow */
.fld-row:has(input[type=time]) .fld:has(input[type=date]) .inp{width:auto;max-width:100%}  /* native date: контентна ширина, НЕ 100% */
```

**Ключові важелі:**

- `width:auto` на native-інпуті → контентна ширина (НЕ `100%`, бо `100%` у широкому боксі = float).
- Довге поле `flex:0 1 auto` (shrink дозволено) → якщо сума контенту колись перевищить контейнер, воно **стискається**, а не вилазить.
- Коротке поле `flex:0 0 auto` → притиснуте по контенту.
- `:has()`-скоуп: специфічність `.fld-row:has(input[type=time]) .fld:has(input[type=date])` = (0,4,2) > бази `.fld-row .fld` (0,2,0) — виграє без `!important` (A8-aware). iOS Safari 15.4+ (XS iOS18 / 15Pro iOS26 — ОК).

**Анти-патерни (що провалилось):**

- ❌ 50/50 (`flex:1` обом) → довге поле тісне.
- ❌ довге `flex:1` + коротке `flex:0 0 auto` → довге плаває + коротке жорстке → +20px overflow.
- ❌ «one число на обидва поля» — ігнорує асиметрію date↔time.

**Узагальнення (на майбутнє, інші проєкти):** діє для **будь-якої** суміші інтринзік-контролів у flex-рядку. Правило: **не розтягувати native-контрол за контент; найдовший — зі `shrink:1`; пакувати вліво.** Сумнів → **два рядки** (нуль горизонтального натягу) — куленепробивний резерв.

**Діагностика — міряти, не гадати (споріднено wsd 14.7):** «випирає/плаває» = піксельний факт. Інструмент: PIL-семпл країв проти **еталонного full-width поля** (де закінчується правий бордер), або пунктирна напрямна в compare-прев’ю. Для самого **вибору layout** → comparison preview з **реальними native-інпутами** + обидві теми (wsd 2.4); мок-поля не відтворять native float/overflow.

**Прецедент:** Drive Lens B19 — рядок Дата+Час у шітах «Заправка»/«Новий запис». batch18 50/50 = тісно; batch19 (date flex:1) = float +20px overflow; **batch19_1 Variant A** = зійшлось чисто, обидві теми, обидва шіти.

-----

## A41. Native picker (date/time) у standalone-PWA — color-scheme заморожений ✅

**Симптом.** `input[type=date]`/`[type=time]` picker (інлайн-календар, спінер) рендериться **сірим/темним** і **не міняє тему**, навіть коли:

- перемикаєш тему всередині застосунку (`data-theme`/`color-scheme`), **і**
- перемикаєш **системну** тему iOS (Налаштування → Екран).

**При цьому власна UI застосунку темиться коректно.** Тобто проблема **тільки** в native-пікері.

**Корінь.** У **standalone-PWA** (display-mode:standalone) native picker читає `color-scheme` **на момент запуску PWA** і **заморожує** його. Живі зміни (ні CSS, ні системні) на picker не діють до **повного перезапуску** застосунку (kill + open). Задокументований баг iOS PWA (Apple Forums; «fixed in iOS 18» стосувалось `prefers-color-scheme` сторінки, але picker-оверлей лишається залежним від launch-time схеми).

**Що це НЕ.** Це **не** баг нашого CSS. Правильна прив’язка `color-scheme` до `data-theme` (`:root`→light, `[data-theme="dark"]`→dark, media-fallback) **коректна** і працює у звичайному **Safari** та після рестарту PWA. Лишати її — не шкодить.

**Що робити:**

- **Прийняти** як стелю платформи (picker видно лише на мить вибору) — дефолт.
- Якщо тема пікера критична → **власний date-picker компонент** (наш themed-календар темиться нормально), не native. Окремий build.
- Не патчити `color-scheme` наосліп удруге — CSS цього не лікує.

**Діагностика (ізолює причину, ~10 сек):** (1) системна тема iOS? (2) той самий файл у Safari (не PWA) → picker світлий? Якщо світлий у Safari + темний у PWA = саме цей PWA-баг.

## **Прецедент:** Drive Lens B19 — #2 (color-scheme для native календаря) закрито як обмеження iOS, не наш дефект.

## A42. Текст поверх ілюстрації / SVG → токен-скрим ✅

**Симптом.** Текст лежить поверх багатотонової ілюстрації (банер, геро-картка). Верхні рядки на світлій смузі читаються; **нижні** рядки (синопсис, тихий сірий) над темнішою/строкатою смугою сцени провалюють контраст — фон наближається до яскравості тексту. Перевірено WCAG: сірий над смугою гір 1.1–2.4 (нижче AA).

**Корінь.** Текст-токени (`--text-secondary`/`--text-muted`) розраховані на **суцільну** поверхню (`surface-1/2`). Ілюстрація — не суцільна → пара «текст-на-surface» не виконується локально.

**Рішення — токен-скрим `::before`** (НЕ `text-shadow`: ореол брудний, проти flat-мови):

```css
:root        { --scrim-1:rgba(244,247,245,.92); --scrim-2:rgba(244,247,245,.55); }
[data-theme="dark"]{ --scrim-1:rgba(14,19,17,.94); --scrim-2:rgba(14,19,17,.55); }
.b-txt::before{content:"";position:absolute;inset:0;
  background:linear-gradient(120deg,var(--scrim-1) 0%,var(--scrim-2) 40%,transparent 70%);pointer-events:none}
.b-txt>*{position:relative}            /* текст над скримом */
```

Скрим = surface-токен (вгорі, де текст — щільний) → прозорий (внизу/збоку, де сцена дихає). Token-driven: light/dark з одного правила (A39). Повертає текст у штатну пару «текст-на-surface»: синопсис → AA; тихий сірий → задуманий «тихий, але видимий».

**Перевіряти.** Контраст **нижніх** рядків над **найтемнішою І найсвітлішою** смугою сцени (не лише над небом угорі), обидві теми. Кут градієнта (тут `120deg`) тримає правий-нижній кут сцени відкритим — звірити, що жоден текстовий рядок туди не дістає.

**Складанка-деталі (Drive Lens Batch 22).** Ключове число хедера банера — єдина кольорова точка над сценою: `.b-h .km{color:var(--accent)}` (решта тексту тримається скрим-нейтралі). Синопсис обмежити `max-width:64%`, щоб рядок не заходив у правий-нижній **відкритий кут** скриму — градієнт `120deg` лишає той кут прозорим, і текст там провалив би контраст (та сама перевірка, що в «Перевіряти» вище).

**Прецедент.** Drive Lens Batch 22 — банер Tab-4 «Місяць» (сезонний SVG під заголовком+синопсисом+сірим рядком). Перший Lens із текстом поверх ілюстрації.

-----

## A43. Inline layered SVG як фон картки / геро (переносний патерн) ✅

**Контекст.** Фон картки = ілюстрація, що темиться й має варіанти (сезони/стани). Растр цього не вміє (2 теми × N варіантів = 2N файлів, не векторні). Рішення: **inline `<svg>` із шарами-`<path fill="var(--token)">`**; варіант через `[data-season]`/клас на предку; усе на CSS-токенах. Один HTML-файл, A39-темування з коробки, вектор-чіткість, дешеві варіанти.

**Правила (з прецеденту, перевірені на device):**

- **Порядок глибини для силует-стилю:** задній шар найсвітліший → передній **найтемніший**. Інакше передній силует зливається з шаром позаду. Контраст сусідніх шарів ≥ ~1.2 (урок: весна-dark «загубила ліс», коли `near≈mid`).
- **Декор-токени НЕ дублювати з фоном сторінки:** нижній стоп градієнта-неба ≠ `--surface-1`, інакше низ картки тоне у сторінку (немає краю). Перевірити край картки проти фону на **dark** (там тіні слабкі).
- **Об’єм на dark = рамка, не тінь:** `border:1px solid var(--border-default)` (.12). На світлій рамку теж тримати .12 — світла ілюстрація на світлій сторінці не дає верхнього краю від базової .06.
- **Опційні елементи — окремий токен, не базове значення.** Сезонний елемент (сніг) видимий лише де треба (зима) через свій токен; решта сезонів `transparent`. Якщо база-тема несе «зимове» значення — зловиш «літо зі снігом» (саме цей баг ловився в iter).
- **Сезон-без-оверайду = базовий `.forest`.** Один сезон (літо) лишити на базових токенах без `[data-season="…"]` правила — менше дублювання; базовий клас і Є літо.

**A39-нюанс.** Той самий шар читається різно у light/dark: на light шари лишаємо як у compare-файлі; на dark **усі** варіанти підняти над фоном окремо (не покладатись, що темна тема «сама притемнить» — низ провалиться). Фінальний арбітр — device, обидві теми (wsd 2.4).

**Прецедент.** Drive Lens Batch 22 — банер Tab-4 (4 сезони × 2 теми, far→mid→near + туман + птахи + сніг-взимку). Перший Lens із layered SVG як фоном картки.

## A44. Горизонт-свайп поверх скрол/тап-контенту — axis-lock + `passive:false` ✅

**Задача.** Додати горизонтальний свайп (зміна місяця / сторінки / вкладки) на елемент, що водночас **вертикально скролиться** і/або має **тап-цілі** (клітинки, кнопки). Три загрози: (1) нативний вертикальний скрол смикає вікно під час горизонт-жесту; (2) горизонт-свайп випадково спрацьовує як тап; (3) sheet/сторінка закривається вертикальним «хвостом» жесту.

**❗ Куди вішати — головне.** НЕ на поверхню, що володіє **тап-цілями** (сітка днів, список-вибір). Свайп там краде тап: «неохайний» тап із горизонт. зсувом >10px лочиться в `x`, `preventDefault` гасить `click`. Вішати на **виділену nav-смужку** (хедер `◂лейбл▸`, таб-бар), де тап-цілі — лише стрілки (а їх захищає `_swiped`-guard). *(Прецедент: Drive Lens Batch 25 повісив свайп на `.cal-grid` → зламав вибір днів; 25.1 переніс на `#calHdr`.)*

**Канон — axis-lock end-only (3 слухачі):**

```js
function bindSwipeX(el, step){              // step(dir): -1 назад / +1 вперед
  if(el._sw)return; el._sw=true;
  let sx=0,sy=0,ax=null;
  el.addEventListener('touchstart',e=>{sx=e.touches[0].clientX;sy=e.touches[0].clientY;ax=null;el._swiped=false;},{passive:true});
  el.addEventListener('touchmove',e=>{const cx=e.touches[0].clientX-sx,cy=e.touches[0].clientY-sy;
    if(ax===null&&(Math.abs(cx)>10||Math.abs(cy)>10))ax=Math.abs(cx)>Math.abs(cy)?'x':'y';
    if(ax==='x'){e.preventDefault();el._swiped=true;}},{passive:false});   // ❗ preventDefault ЛИШЕ на x
  el.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;
    if(ax==='x'&&Math.abs(dx)>Math.abs(dy)&&Math.abs(dx)>50)step(dx<0?1:-1);},{passive:true});
}
```

**Чому саме так (кожен рядок — захист):**

- **`touchmove` під `{passive:false}` + `preventDefault()` ЛИШЕ коли `ax==='x'`** — ключ проти «дьоргання». Якщо лишити touchmove `passive:true` (або preventDefault на будь-якій осі) — браузер під час горизонт-свайпу **паралельно котить вертикальний скрол**, і вікно стрибає вгору-вниз. `preventDefault` тільки на зафіксованій осі x глушить нативний скрол **виключно** для горизонт-наміру; вертикальний скрол лишається рідним.
- **Поріг axis-lock 10px** — лочимо вісь раніше, ніж щось рухнеться помітно (порівняй A22 slop=10).
- **Спрацювання 50px на `touchend`** (end-only, як A18/A19/A22) — без live-follow; рішення одне, на відпусканні.
- **Прапор `_swiped`** — у `click`-хендлері контенту перша дія: `if(el._swiped){el._swiped=false;return;}`. Інакше довгий горизонт-свайп може довести `click` і вибрати клітинку «під пальцем».
- **`_sw` once-for-life** — слухачі вішати один раз на сам елемент (він переживає `innerHTML`-перемальовку дітей), не на щораз новий вузол (A21).

**Спорідненість.** A22 (swipe-row) — **той самий axis-lock end-only механізм** (не «passive без preventDefault», як писалось раніше). ⚠️ **Корекція (batch41):** swipe-row теж під `{passive:false}` + `preventDefault()` ЛИШЕ на осі `x`, бо `.sw-row` сидить у вертикально-скрольному списку → без цього горизонт-свайп смикає сторінку. Різниця A22↔A44 не в `passive`, а в тому, **КУДИ вішати** слухач: A22 — на сам рядок-`front` (тап-ціль = весь рядок, edit/close арбітрить `moved`-прапор); A44 — на виділену nav-смужку (бо під свайпом Є дрібні тап-цілі стрілок). **Правило вибору (спрощене):** під свайпом Є вертикальний скрол АБО sheet-close? → `passive:false`+preventDefault-на-`x` (майже завжди — обидва A22/A44). «Чистий passive без preventDefault» — лише якщо під елементом ГАРАНТОВАНО нема ні вертикального скролу, ні sheet-close (рідко).

**Співжиття зі sheet-swipe-close (A19).** Якщо елемент усередині bottom sheet — тримати його в прапорі `ig` слухача A19 (`.cal-grid`/`.mg-grid`/`.fg-grid`/`.pk-list`), щоб вертикаль не закривала sheet. Горизонталь свою бере A44, вертикаль — нейтральна (ні скрол, ні close).

**Доповнення — пігулка-рік: свайп + тап на ОДНОМУ елементі (Drive Lens B29/B29.1).** Рік-пігулка `◂2026▸` бере свайп року через `bindSwipeX` напряму. Ключовий нюанс: **той самий елемент може нести І свайп (`bindSwipeX`), І тап-дію (`click`)** — арбітр `_swiped`. У B29.1 тап рік-пігулки = «назад до днів»; `click`-хендлер першим рядком `if(el._swiped){el._swiped=false;return;}` (читає прапор, що його ставить власний `bindSwipeX` цього ж елемента). Тобто `_swiped`-guard захищає не лише стрілки-сусіди, а й **тап-дію самої свайп-смужки**. Пігулка — спільний клас `.mg-y` для range-календаря (`calMgY`) і Tab-4 (`mgYear`); тап-назад чіпляти **тільки до `calMgY` через id** (Tab-4 не має денної в’юшки — toggle-мови там нема; ізоляція 14.10). *Device-validated B29.1.*

*(Drive Lens: місяць-свайп Tab-4 Batch 22 — base; календар-діапазон Batch 25 — переніс із `preventDefault`. Узагальнено з A22 Batch 11. Свайп календаря — device-test pending.)*

## A45. Об’єм / elevation на ТЕМНІЙ темі: через тон, не тінь ✅

**Симптом.** Картка/плитка з тінню має «масу» на світлій темі, але на темній стає пласкою.

**Корінь.** Drop-shadow на темному фоні майже невидимий (споріднено A61 dark-gotcha) — око читає об’єм на світлому через падаючу тінь, якої на темному нема.

**Рішення — об’єм тоном (не тінню):**

1. **Градієнт** `linear-gradient(180deg, світліший-верх, темніший-низ)` — імітує світло згори.
1. **Верхній inset-хайлайт** `inset 0 1px 0 rgba(255,255,255,.06–.08)` — світло «лягає» на верхнє ребро.
1. **Нижня inset-грань** `inset 0 -1px 0 rgba(0,0,0,.2)` — підняте ребро знизу.
1. **Світла тема ДОДАЄ** звичайний `box-shadow` drop (там він працює).

Спліт через `[data-theme="dark"]` (A8-aware: окреме правило, не одна тінь на обидві теми).

**Тригер:** будь-яка «підведена» поверхня, що має читатись об’ємно на обох темах (плитки, картки-кнопки, чипи з елевацією).
**Анти:** «зробив тінь, на темній зникла, забив».

**Прецедент:** Drive Lens Tab-3 плитки «Гроші» (Batch 26).
**Розширення (QR B30):** асиметрія між темами уточнена → **A66** (світла = ШИРОКА drop ≥14px, бо світло-зверху мертве на білому; темна = світло-зверху, бо drop мертва на OLED; градієнт обидві). **Активний/обраний стан** (accent-fill + tone-lift, контекст-залежна сила drop) → **A66.1**.

## A46. Card-in-card (вкладені під-картки) для двоблокової картки ✅

Один зовнішній `.fl-card`, всередині грид із `.sub`-під-карток (`surface-3` + `border` + `radius`). На темній під-картка = `color-mix(in srgb, surface-3 80%, surface-2)` + верхній inset-хайлайт (A45), щоб не злитись із зовнішньою карткою.

**Ієрархія тексту (щоб не було «трьох білих»):** білий — лише заголовок зовнішньої картки (`.sec-t`) + ключові дані всередині (бренди/значення). **Стовпці-заголовки під-карток (`.colh`) — сірі** (`--text-secondary`), не білі: інакше конкурують із заголовком картки та даними.

**Спільна візуальна мова** зі стат-плитками (A47): однаковий `radius`, `border`, dark-elevation-патерн.

**Reuse:** будь-яка картка, що ділить два паралельні логічні блоки в одному контейнері (Звички / Станції; Було / Стало; Тиждень / Місяць).

**Прецедент:** Drive Lens Tab-3 «Заправки» — Звички + Де заправляюся, грид 50/50 (Batch 26).

## A47. Стат-плитки (3 у ряд): іконка + значення + підпис ✅

Грид `repeat(3,1fr)`, кожна плитка — вертикальний стек: **іконка** (24px, по центру) / **значення** (`tabular-nums`) / **підпис** (`--text-muted`).

**Колір тинту = за змістом (A35), НЕ світлофор:** усі плитки одного семантичного блоку — один тон (паливо → синій `--info`), не «зелена/жовта/червона» розкладка. Об’єм — через A45 (градієнт + inset-грані, спліт по темах).

**Значення** підкручене до тинту: `color-mix(in srgb, var(--info) 60%, var(--text-primary))` на світлій, `80%` на темній (темна потребує більше тинту, щоб синій читався).

**Прецедент:** Drive Lens Tab-3 «Гроші» (Batch 26).

## A37. Поділки-риски під дискретним баром (без дробових гліфів) ✅

> ℹ️ *Нумерація A37/A38 історична — фізично стоять між A47 і A48 (внесені тим самим Batch 26, контентно належать до сімейства карток A46/A47). Лишено на місці свідомо: через позицію ніхто не посилається, тож перенос дав би нуль користі при ненульовому ризику.*

*(Борг з Drive Lens 16c — внесено Batch 26.)*

Під дискретним баром (напр. гейдж на 12 поділів) риски-орієнтири ставити **дзеркаленням структури грида окремим рядком**: той самий грид/флекс, що й комірки, але вміст — риска в центрі щілини між групами через `transform:translateX(calc(50% + Npx))` (N = піврозміру gap). **Центральна риска вища** (`½`-позначка), бічні нижчі.

**Анти:** ставити гліфи дробів (¼ ½ ¾) як текст — вони не вирівнюються до реальних меж комірок і «пливуть» при зміні ширини. Риска прибита до геометрії грида — пливти нема куди.

**Прецедент:** Drive Lens «Зараз у баку» — `.fs-scale`/`.fs-tick` (риски E—½—F).

## A38. Вирівнювання колонок у багаторядковій легенді: grid + `display:contents` ✅

*(Борг з Drive Lens 16c — внесено Batch 26.)*

Для легенди, де кожен рядок = [іконка/дот] [підпис] [значення], і треба, щоб **значення стартували з однієї вертикалі** попри різну ширину підписів — контейнер `display:grid` із фіксованими треками (`auto 1fr auto`), а кожен логічний рядок — обгортка з `display:contents` (її діти стають прямими учасниками грида й вирівнюються по треках).

**Анти:** магічні `min-width` на підписах, підібрані на око під найдовший рядок — ламаються при зміні даних/локалі.

**Прецедент:** Drive Lens Tab-3 «Розподіл пробігу» — `.pb-grid`/`.pb-li` (`display:contents`), Tab-1 split-легенда (Batch 26).

## A48. Секція-eyebrow (uppercase) + лінія-роздільник зон ✅

*(Нугет Drive Lens Batch 27 — Tab-1 мікс, device-валідовано обидві теми.)*

Два споріднені роздільники структури екрана, обидва токен-driven, обидва крокують по темах (`--border-subtle` на світлій → `--border-default` на темній, бо subtle на темній майже невидима):

**Eyebrow-хедер секції** — заголовок дня/секції як тихий «надпис» + нижня лінія замість важкого болда:

```css
.sec-h.dl .sec-t{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-secondary)}
.sec-h.dl{border-bottom:1px solid var(--border-subtle);padding-bottom:7px}
[data-theme="dark"] .sec-h.dl{border-bottom-color:var(--border-default)}
```

**Лінія зон** — 1px роздільник між логічними зонами одного екрана (геро ↔ дії):

```css
.zone-div{height:1px;background:var(--border-subtle);margin:4px 2px 13px}
[data-theme="dark"] .zone-div{background:var(--border-default)}
```

**Правила:**

- **`dl` — opt-in per header.** Клас `dl` чіпляти ЛИШЕ там, де треба eyebrow-трактування (у Drive Lens — тільки Tab-1 хедери дня в `renderRecords()`); решта (картки-дні Tab-2) лишається на чистому `.sec-h`. Один варіант-клас, не глобальне перевизначення `.sec-h` — інакше зачепиш усі секції.
- **Лінію зон вставляти у точці, що завжди рендериться після верхньої зони** (у Drive Lens — початок `renderCTA()`, який завжди йде після `renderSummary()`).
- **Темна = крок subtle→default.** `--border-subtle` на темному фоні ледь видима — обидва роздільники піднімати на `--border-default` через `[data-theme="dark"]` (A8-aware: окреме правило, не одна лінія на дві теми).

**Reuse:** будь-який Lens, де екран ділиться на зони або секції мають тихі заголовки-надписи. Споріднено з A61 (chrome-роздільники) — там edge-to-edge слаб, тут — внутрішньо-екранні лінії.

## A49. Чіп-плашка частки + підсилення числа (число сильніше, одиниця тихіше) ✅

*(Нугет Drive Lens Batch 27 — Tab-3 «Розподіл» чіп B, device-валідовано обидві теми.)*

**Чіп-плашка %/частки** — відсоток/частку класти у мінімальну плашку (не голий текст у рядку): плашка дає поверхню, що тримає число окремо від сусідів навіть при однаковому кольорі/вазі.

```css
.pb-chip{display:inline-flex;align-items:center;justify-content:center;
  min-width:46px;padding:3px 9px;border-radius:9px;
  font-variant-numeric:tabular-nums;font-weight:700;color:var(--text-secondary);
  background:var(--surface-2);border:1px solid var(--border-subtle);
  box-shadow:0 1px 2px rgba(20,30,25,.08)}
[data-theme="dark"] .pb-chip{background:var(--surface-3);border-color:var(--border-default);box-shadow:none}
```

- `min-width` — однакова ширина плашок → числа вирівнюються в колонку (з `tabular-nums`).
- Темна: плашка на `--surface-3` (світліша за фон), тінь геть (A45 — об’єм тоном, не тінню).

**Підсилення числа в рядку-описі** — у щільному рядку «318 км · ≈ 20.5 л · 1 112 ₴» носій даних = число, одиниця = тихий підпис. Обгорнути число в `.n`, підняти, одиницю лишити muted:

```css
.pb-sub{font-size:12px;color:var(--text-muted)}      /* одиниці км/л/₴ — тихо */
.pb-sub .n{color:var(--text-secondary);font-weight:700}  /* число — носій даних */
```

**⚠ Ієрархія-застереження (3 яруси, не 2).** Якщо в тому ж компоненті є **підпис-слово** (категорія: Робота/Вайб), він НЕ може бути на тому ж ярусі, що й підсилене число — обидва `secondary/700` зіллються (саме цей дефект ловиться оком). Тримати три яруси: **підпис-слово → primary**, **число-дані → secondary**, **одиниця → muted**. Підпис тоді ще й римується з геро-значенням блока спільним primary. Плашка-чіп окремо: її поверхня (bg/border) відділяє навіть при рівному кольорі з числами. Споріднено з A46 («не три білих»: сірі заголовки колонок, щоб не конкурували з даними).

**Reuse:** будь-який блок-розклад «категорія — частка — деталь» (split-легенди, бюджет-рядки, частки палива/витрат).

## A50. Range-календар: in-sheet drill день↔місяць (calMY-свап) + антистрибок + каретка-мова ✅

**Задача.** Дати швидкий «стрибок» по місяцях усередині range-календаря (A33) без окремого пікера — і назад, без закриття шіта.

**Свап у ТОМУ Ж шіті (B28).** Тап по пілюлі-лейблу `calMY` (`◂назва місяця▸`, хедер денної в’юшки) → ховаємо `calDayView`, показуємо `calMonView` (сітка місяців 3×4, реюз `.mg-*` CSS A33). Драйвить `calView` (стан range-календаря), **НЕ** `S.monthView` Tab-4. ❗ Окремі id `calMg*` (`calMgY`, `calMgGrid`…), щоб не зіткнутись із `mgGrid`/`mgYear` Tab-4 — **ізоляція стану (14.10)**. Вибір клітинки місяця → `calView={y,m}` + `showCalDays()` + `renderCal()` (перехід). Floor-guard: місяці до 1-го запису `disabled`; рік-стрілка `prev` гасне на `dataFloor().y`, вперед — без межі (як A33).

**Антистрибок висоти (B29).** При свапі `calMonView.minHeight = calDayView.offsetHeight` (місячна сітка нижча за денну з її підказкою+Сьогодні+футером). Інакше шіт «худне» при день→місяць і «товстіє» назад — стрибок. На `showCalDays()` пін скидати (`minHeight=''`). **Наслідок-урок:** пінена свап-в’юшка успадковує whitespace найвищої — порожнечу під сіткою вирішувати **свідомо** (лишити дихання / центрувати layout-ом / заробити контентом). Drive Lens обрав «зверху, дихає»; filler заради простору відкинуто (= капкан, як зайве поле/риска).

**Назад до днів + каретка-мова (B29.1).** Несиметрія до фіксу: з денної є афорданс ПІТИ на місяці (тап `calMY`), а назад — лише `×` або вибір місяця. Фікс: **рік-пігулка `calMgY` тапабельна** → `showCalDays()` (повертає на той самий місяць, `calView` без змін, нічого не обрано — чистий «передумав»). Гард `_swiped` (тап≠свайп року; див. доповнення A44). **Одна каретка-мова на обох пілюлях:** ▾ на `calMY` (дні → «розкрити в місяці»), ▴ на `calMgY` (місяці → «згорнути в дні») — ідіома Apple Calendar, каретка вказує напрям drill. Реалізація: число у дочірній `.pill-v` span + каретка-сусід (inline SVG-chevron), бо пілюлі оновлюються через `.textContent` (стер би дочірній вузол). Каретка `--text-muted` (читається, не кричить). ❗ Каретку/тап-назад — **лише до пілюль range-календаря (id-скоуп)**, НЕ до спільного `.mg-y` (Tab-4 `mgYear` без днів → без каретки).

**Крос-реф.** База — A33 (tap-based range grid). **Спільне місяць-ядро (3×4 grid + floor-guard + рік-пігулка) промоутнуто в → A60** — тут лишається ЛИШЕ range-специфіка (calMY-свап день↔місяць, антистрибок, каретка-мова). Свайп року/днів — A44. Sheet-close співжиття — A19/A44. Ізоляція станів — wsd 14.10. *Device-validated повністю (B28→B29.1).*

## A51. Втоплене поле (tactile well) — афорданс «можна пожамкати»; світла≠темна ✅

**Симптом.** Поле вводу (search/input) `surface-2` на сторінці `surface-1` зі слабкою рамкою `.06` — на СВІТЛІЙ майже зливається (ΔL*≈3, рамка невидима), читається лише за ВМІСТОМ (іконка+плейсхолдер), не за контейнером. На темній те саме поле тримається ТОНОМ (s2>s1, ~×2.5 luminance).

**Рішення — well ЛИШЕ на світлій, темна = база.**

- Світла: `[data-theme="light"] .X{background:var(--surface-3);border-color:var(--border-default);box-shadow:inset 0 2px 4px rgba(0,0,0,.10)}` — поле «вирізане» в сторінці, inset дає глибину ВСЕРЕДИНУ → афорданс «торкни/впиши».
- Темна: НЕ чіпати. Об’єм уже несе тон; inset на темному слабкий; додавання робить «пересвідчено». Світла й темна — РІЗНИЙ підхід (A39/A45).

**Чому не зовнішня drop-тінь.** Над полем (журнал) стоїть filter-row зі своєю світлою drop-тінню; друга drop поруч → стекінг/шум. Inset не конфліктує (споріднено A61 — одна тінь на межі).

**Специфічність (A8):** `[data-theme="light"] .X` = (0,2,0) > гола `.X` (0,1,0). Border-shorthand бази лишається, override б’є лише `border-color`/`background`/`box-shadow`.

**Анти:** «inset на обидві теми» (на темній не читається, важко); «drop поруч із chrome-тінню» (стекінг).
**Зв’язок:** A45 (об’єм на темній — тон, не тінь), A39 (формула однакова ≠ характер однаковий → спліт по темі), A61 (chrome-тінь/межі). *Drive Lens Batch 30, search-row журналу.*
**Промоут (QR B30):** well формалізовано у токен-стандарт `--well-bg`/`--well-sh` + «дві мови глибини» (well-поле vs elevation-кнопка) → **A65**. Реалізація well-афордансу тепер через ці токени.

## A52. Toggle-switch (`.sw`) — нативний checkbox під стильованим треком ✅

**Що це:** iOS-style перемикач увімк/вимк у шітах налаштувань (Drive Lens: Нагадування, Автозбереження). Назва компонента — `.sw`. Коли треба тогл — кажемо «`.sw`-тогл», без двозначності.

**Чому саме так:** `<label>` обгортає **прихований нативний** `<input type="checkbox">` (зберігає a11y/focus/VoiceOver + рідну поведінку стану) поверх стильованого треку `.sw-tr`. Стан несе `:checked`, без JS для самого тогла.

**Розмітка:**

```html
<label class="sw"><input type="checkbox" id="set-rem"><span class="sw-tr"></span></label>
```

**CSS:**

```css
.sw{position:relative;width:46px;height:28px;flex-shrink:0;cursor:pointer}
.sw input{position:absolute;opacity:0;width:100%;height:100%;margin:0;cursor:pointer}
.sw-tr{position:absolute;inset:0;background:var(--surface-4);border-radius:14px;transition:background .18s}
.sw-tr::after{content:"";position:absolute;top:3px;left:3px;width:22px;height:22px;background:#fff;border-radius:50%;transition:transform .18s;box-shadow:0 1px 3px rgba(0,0,0,.25)}
.sw input:checked + .sw-tr{background:var(--accent)}
.sw input:checked + .sw-tr::after{transform:translateX(18px)}
```

**Геометрія (щоб не вгадувати):** трек 46×28, радіус 14 (повна капсула); палець 22×22, відступ 3px; хід = 46−22−2×3 = **18px** → `translateX(18px)`. Змінюєш ширину/палець — перерахуй хід, інакше не дотисне до краю.

**Кольори/теми:** OFF-трек `--surface-4` (нейтраль, червоного в Drive Lens нема); ON-трек `--accent`; палець `#fff` в обох темах (білий читається і на світлій, і на темній — перцептивно).

**Стан:** boolean пишеться через `input.checked` у JS (`SETTINGS.x=e.target.checked; saveSettings()`), не через клас — тогл є джерелом правди.

**Анти:** стилізувати div без нативного checkbox (втрата a11y); забути перерахувати хід пальця при зміні розмірів.
**Зв’язок:** мова контролів шіту (select/input на `--surface`), але окремий тип — не уніфікувати з select-пілюлями (вибір зі списку ≠ бінарний перемикач). *Drive Lens Batch 31, шіт Налаштування.*

## A53. Кастом тап-селект `.pk` — заміна нативного `<select>` ✅

**Що це:** керований дропдаун замість `<select>` (на iOS native select дає jank-«барабан» + замерзлий `color-scheme` у standalone-PWA, див. A41). Один фабричний `makePicker(cfg)` живить усі екземпляри. Реюз у Drive Lens: **АЗС** (з «Інша…»), **Тип палива**, **Одиниці**, **Валюта** (Налаштування).

**Розмітка:**

```html
<div class="pk" id="f-type-pk">
  <button class="pk-btn" id="f-type-btn" type="button">
    <span id="f-type-cur">Бензин A-95</span>
    <svg class="pk-chev" ...><path d="M6 9l6 6 6-6"/></svg>
  </button>
  <div class="pk-list" id="f-type-list" hidden></div>   <!-- .pk-opt будуються JS -->
</div>
```

**CSS (ядро + дві варіації):**

```css
.pk{position:relative}
.pk-btn{display:flex;align-items:center;justify-content:space-between;width:100%;text-align:left;gap:8px;cursor:pointer;font-size:16px}
.pk-btn .pk-chev{width:14px;height:14px;color:var(--text-muted);transition:transform .15s}
.pk.open .pk-chev{transform:rotate(180deg)}
.pk-list{margin-top:6px;background:var(--surface-2);border:1px solid var(--border-default);border-radius:var(--rs);max-height:232px;overflow-y:auto;-webkit-overflow-scrolling:touch}
.pk-opt{display:block;width:100%;text-align:left;padding:12px 13px;background:transparent;border:none;border-bottom:1px solid var(--border-subtle);color:var(--text-primary);font-size:15px;font-weight:600;cursor:pointer}
.pk-opt:last-child{border-bottom:none}
.pk-opt:active{background:var(--surface-3)}
.pk-opt.sel{color:var(--accent-text)}
.pk-opt.other{color:var(--text-secondary);font-style:italic}
/* компактна пілюля в рядку Налаштувань + float-right дропдаун */
.set-pk .pk-btn{width:auto;gap:6px;padding:8px 12px;background:var(--surface-3);border:1px solid var(--border-subtle);border-radius:var(--rs);font-size:14px;font-weight:700;color:var(--text-primary)}
.set-pk .pk-list{position:absolute;right:0;top:calc(100% + 6px);min-width:168px;z-index:5;box-shadow:var(--sh1)}
.set-pk.pk-up .pk-list{top:auto;bottom:calc(100% + 6px)}  /* flip-up коли знизу мало місця (останній рядок шіта) */
```

**Фабрика:**

```js
function makePicker(cfg){ // {root,btn,cur,list,options,allowOther,otherInput,flip,onChange}
  const root=$(cfg.root),btn=$(cfg.btn),cur=$(cfg.cur),list=$(cfg.list);
  const norm=o=>typeof o==='string'?{v:o,l:o}:o;
  function build(){list.innerHTML=cfg.options.map(o=>{const x=norm(o);return `<button type="button" class="pk-opt" data-val="${esc(x.v)}">${esc(x.l)}</button>`;}).join('')
    +(cfg.allowOther?`<button type="button" class="pk-opt other" data-val="__other">Інша…</button>`:'');}
  function mark(val){list.querySelectorAll('.pk-opt').forEach(o=>o.classList.toggle('sel',o.dataset.val===val));}
  function set(val,label){btn.dataset.val=val;cur.textContent=label;mark(val);}
  function open(o){root.classList.toggle('open',o);list.hidden=!o;if(cfg.flip)root.classList.toggle('pk-up',o);}
  build();
  btn.addEventListener('click',()=>open(list.hidden));
  list.addEventListener('click',e=>{const opt=e.target.closest('.pk-opt');if(!opt)return;const val=opt.dataset.val;
    if(cfg.allowOther&&val==='__other'){set('__other','Інша…');open(false);const ot=$(cfg.otherInput);ot.style.display='block';ot.focus();} // focus синхронно в gesture → клавіатура без блимання
    else{set(val,opt.textContent);open(false);if(cfg.otherInput)$(cfg.otherInput).style.display='none';}
    if(cfg.onChange)cfg.onChange(btn.dataset.val);});
  // A21: один document-listener на root-id (шіт перебудовується genSheet'ом → інакше стек listeners); re-resolve по id
  if(!makePicker._docBound)makePicker._docBound={};
  if(!makePicker._docBound[cfg.root]){makePicker._docBound[cfg.root]=true;
    document.addEventListener('click',e=>{const L=$(cfg.list),R=document.getElementById(cfg.root);if(L&&!L.hidden&&!(e.target.closest&&e.target.closest('#'+cfg.root))){L.hidden=true;if(R)R.classList.remove('open');}});}
  return {set,open,build,get:()=>btn.dataset.val};
}
```

**Ключові деталі:**

- **«Інша…» + сінхронний focus.** Вибір `__other` → показати текст-інпут і `.focus()` **синхронно в gesture** — інакше iOS не підніме клавіатуру (правило F12 / B3).
- **Document-listener один на root-id (A21).** Шіт Налаштувань `genSheet`’иться щоразу → прямий listener стекувався б; тому прапор `_docBound[root]` + re-resolve вузла по id.
- **Float-right + flip-up.** У рядку Налаштувань дропдаун якориться `right:0`; для останніх рядків (Валюта) — `pk-up` відкриває вгору, щоб не вилазив за шіт.
- **Співжиття зі swipe-close шіта.** `.pk-list` має бути в `ig`-наборі touchstart-guard (поряд з `.fg-grid`/`.cal-grid`) — інакше скрол списку конфліктує зі свайпом-закриттям (A19).

**Анти:** нативний `<select>` у PWA (jank + замерзлий color-scheme A41); прямий document-listener на екземпляр, що перебудовується (стек). **Зв’язок:** A41 (native picker замерзлий), A21 (listener once-for-life), B3 (форми/focus), A19 (`ig`-guard свайпу). *Drive Lens Batch 9.1 / 32 (settings-варіант).*

## A54. Анімований повзунок сегмент-перемикача (constant-width slide) ✅

**Що це:** активна «пілюля» в сегмент-перемикачі **їде** до обраного сегмента (slide + легка пружина), а не блимає. Один механізм покриває всі перемикачі продукту: еталон `#seg` (фільтр Огляд/Журнал, він же в Tab-4 «Місяць»), `#r-type` (тип запису в шіті, **кольоро-залежний**), `#flSeg` (період на табі Паливо).

**Принцип:** сегменти — рівні `flex:1`; окремий абсолютний `.seg-thumb` позиціюється під активним через **вимір `getBoundingClientRect`** (не CSS-формула — стійко до різної ширини тексту). Анімуються `transform` (зсув) + `width`. Per-instance (кожен перемикач має свій thumb). Текст сегментів — над thumb (`z-index`), фон/тінь активного несе сам thumb.

**CSS:**

```css
:root{--seg-dur:450ms; --seg-ease:cubic-bezier(.34,1.56,.64,1);}  /* пружина B; 450 = DRIVE seg device-валідовано (300 задовгий навіть для 3-seg, 14.13). QR A54-капсула розійшлась device-тюном → 500ms/cubic-bezier(.34,1.70,.64,1) (batch44_2 р.73) — per-product, не дрейф */
.seg{display:flex;background:var(--surface-3);border-radius:var(--rs);padding:3px;gap:2px;flex:1;position:relative;overflow:hidden;min-width:min-content}
.seg-i{flex:1;...;color:var(--text-secondary);transition:color .14s;position:relative;z-index:1}  /* лише текст+колір */
.seg-i.act{color:var(--accent)}
.seg-thumb{position:absolute;top:3px;bottom:3px;left:0;width:0;border-radius:8px;background:var(--thumb-bg);box-shadow:var(--thumb-sh);border:1px solid var(--thumb-bd);transition:transform var(--seg-dur) var(--seg-ease),width var(--seg-dur) var(--seg-ease);pointer-events:none;z-index:0;opacity:0}
.seg-thumb.seg-no-anim{transition:none}  /* снап на лейаут/тему/resize/init — без слайду */
@media(prefers-reduced-motion:reduce){.seg-thumb{transition:none}}
/* кольоро-залежний підтип (type-seg): thumb міняє колір під активний тип через [data-active] */
.type-seg[data-active="work"] .seg-thumb{background:var(--accent-soft);box-shadow:var(--sh1);border-color:transparent}
.type-seg[data-active="vibe"] .seg-thumb{background:var(--vibe-soft);box-shadow:var(--sh1);border-color:transparent}
[data-theme="dark"] .type-seg[data-active] .seg-thumb{background:var(--surface-4)}  /* темна: обидва типи surface-4 (об'єм тоном, A45) */
```

**JS:**

```js
function ensureThumb(seg){let t=seg.querySelector('.seg-thumb');if(!t){t=document.createElement('span');t.className='seg-thumb';t.setAttribute('aria-hidden','true');seg.insertBefore(t,seg.firstChild);}return t;}
function placeThumb(seg,snap){
  if(!seg)return;const t=ensureThumb(seg),act=seg.querySelector('.seg-i.act, .ty-i.act');
  if(!act){t.style.opacity='0';return;}
  if(seg.classList.contains('type-seg'))seg.dataset.active=act.dataset.ty;   // кольоро-залежність
  const sr=seg.getBoundingClientRect(),r=act.getBoundingClientRect();
  if(r.width===0){t.style.opacity='0';return;}   // ще не в лейауті (схований таб/рядок) — переміряємо наступним хуком
  const apply=()=>{t.style.width=r.width+'px';t.style.transform='translateX('+(r.left-sr.left)+'px)';t.style.opacity='1';};
  if(snap){t.classList.add('seg-no-anim');apply();requestAnimationFrame(()=>requestAnimationFrame(()=>t.classList.remove('seg-no-anim')));}
  else apply();
}
function placeAllThumbs(snap){document.querySelectorAll('.seg,.type-seg').forEach(s=>placeThumb(s,snap));}
```

**Коли снап (`snap=true`), коли слайд (`false`):** слайд — лише на **реальну зміну вибору** (тап). Снап — на init, зміну теми, resize, показ табу, відкриття шіта, зміну ширини сусіда. Прапор «змінилось?» тримати окремо (`_lastFilter`, `_lastFuelScope`), а не виводити з факту виклику render.

**Хуки перерахунку (де кликати `placeAllThumbs`/`placeThumb`):** `DOMContentLoaded`, `document.fonts.ready`, `resize` (через rAF), перемикання теми, перемикання табу, **відкриття шіта** (закритий шіт = width 0 → guard; снап у `requestAnimationFrame` коли видимий).

**Урок 1 — `overflow:hidden` на флекс-ЕЛЕМЕНТі обнуляє його `min-width:auto`→0.** `.seg` має `overflow:hidden` (кліпає overshoot пружини) — це скидає `min-width:auto` в 0, і перемикач стискається нижче суми сегментів (обрізає «Всі»). Фікс: `min-width:min-content`. **Scope-guard:** потрібен **лише** коли елемент тисне флекс-сусід (`.seg` поряд з date-btn у `.filter-row`); `.type-seg` у блочному `.fld` сусіда не має → `min-width` не треба. Не переносити фікс наосліп — перевіряти причину (wsd 14.6-споріднено).

**Урок 2 — перераховувати позицію thumb на БУДЬ-ЯКУ зміну лейауту/видимості сусіда.** Ширина date-btn змінилась (інша дата) → релейаут seg → thumb зміщується: снап. Показ табу / відкриття шіта: width 0→N → переміряти. Тобто thumb прив’язаний не до «кроку анімації», а до геометрії, яку треба заміряти після кожної зовнішньої зміни.

**Урок 3 (b34) — animated thumb вимагає ПОСТІЙНОГО seg-DOM.** Якщо панель навколо перемикача ре-рендериться (`innerHTML` перебудова щотапу) — thumb знищується й народжується на місці → **снап замість слайду**, навіть з усією правильною CSS-інфрою. Корінь fuel-seg бага: `renderFuel` перебудовував увесь `fl-scroll`. Фікс: **відділити seg від тіла, що оновлюється** — seg рендериться раз (постійний), дані живуть в окремому контейнері (`#fl-body`), на тапі — лише тогл `.act` + `placeThumb(…,false)`. «Та сама CSS» ≠ «та сама поведінка», якщо життєвий цикл елемента різний (wsd 14.13).

**Узагальнення (QR Phase 3, B37) — persistent-DOM для БУДЬ-ЯКОГО анімованого стан-тоглу, не лише seg-thumb.** Той самий клас бага вбиває press-пружину (A67) на **чіпах фільтра**: якщо `render*` перебудовує `innerHTML` списку чіпів на кожен тап — чіп знищується посеред spring-повернення → смик замість пружини. Фікс ідентичний за духом: тогл стану **`data-v`-атрибутом** на ПОСТІЙНИХ вузлах (`el.classList.toggle('on', el.dataset.v===cur)` без rebuild) + **делегований `bindChipPress`** на постійний контейнер (переживає будь-який ре-рендер тіла). Сімейство: seg-thumb (цей A54), чіпи (тут), велика картка (A67.1 sig-guard) — **усі вимагають живого вузла на час анімації.**

**Анти:** перебудовувати seg на вибір (rebuild → снап); `placeThumb(true)` там, де очікується слайд; CSS-формула позиції замість виміру (ламається на різній ширині тексту); забути хук перерахунку при показі табу/шіта (thumb «застряг» на opacity 0). **Зв’язок:** A45 (об’єм тоном на темній — для thumb), A44/A50 (перерахунок лейауту календаря — спорідненість «міряй після зовнішньої зміни»), A53 (поряд у шіті Запис). *Drive Lens Batch 32 (база) → 33 (type-seg + 450) → 34 (fuel-seg постійний DOM).*

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

## A56. Bottom-nav — ПОВНИЙ еталон компонента (скло + анімована капсула + іконки) ✅

**Що це.** Повний поточний стан таб-бару Drive Lens (Batch 35→41) як **копі-пейст-еталон** для всіх Lens — минулих і майбутніх: «взяв, підставив, отримав преміальний бар одразу». Об’єднує: overlay+скло+висоту (A55), анімовану капсулу активного табу (та сама slide-механіка, що A54), іконки, дворежимну тему. Source-of-truth коду: `Drive_Lens_preview_batch41.html`.

### Токени (light = default, dark — оверрайд)

```css
:root{
  --nav-dur:400ms; --nav-ease:cubic-bezier(.34,1.3,.64,1); /* капсула: мʼякша пружина, ніж seg (450/1.56) */
  --glass-blur:12px; --glass-sat:180%;
  --glass-bg:rgba(231,238,233,.72); --glass-rim:rgba(0,0,0,.06);
  --glass-lift:0 -1px 1px rgba(20,30,25,.05),0 -8px 22px rgba(20,30,25,.09);
  --cap-bg:var(--accent-soft); /* світла: ніжно-зелена плашка */
}
[data-theme="dark"]{
  --glass-bg:rgba(20,28,24,.70); --glass-rim:rgba(255,255,255,.04);
  --glass-lift:0 -1px 2px rgba(0,0,0,.28),0 -10px 24px rgba(0,0,0,.20);
  --cap-bg:var(--surface-4); /* темна: обʼєм тоном (A45), не кольором */
}
```

### HTML (капсула — ПЕРШИЙ, постійний дочірній елемент)

```html
<nav class="bottom-nav" id="bnav">
  <span class="tb-cap" aria-hidden="true"></span>          <!-- постійна капсула, A54-механіка -->
  <button class="nav-i act" data-tab="overview"><svg …/>Огляд</button>
  <button class="nav-i"     data-tab="journal"><svg …/>Журнал</button>
  <button class="nav-i"     data-tab="fuel"><svg …/>Паливо</button>
  <button class="nav-i"     data-tab="month"><svg …/>Місяць</button>
</nav>
```

Іконки — inline lucide-style SVG: `viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap/linejoin="round"`. `stroke="currentColor"` → іконка успадковує колір `.nav-i` (muted→accent на active). Без emoji (правило Lens).

### CSS

```css
/* бар: overlay-в-#app + скло (див. A55(2)) */
.bottom-nav{position:absolute;left:0;right:0;bottom:0;z-index:50;display:flex;
  padding:6px 6px max(9px,var(--sab));        /* sab у padding → скло фарбує home-indicator зсередини */
  background:var(--glass-bg);
  backdrop-filter:blur(var(--glass-blur)) saturate(var(--glass-sat));
  -webkit-backdrop-filter:blur(var(--glass-blur)) saturate(var(--glass-sat));
  border-top:1px solid var(--glass-rim);box-shadow:var(--glass-lift)}

/* капсула активного табу — slide (A54-механіка для нав) */
.tb-cap{position:absolute;left:0;top:0;border-radius:14px;z-index:0;opacity:0;pointer-events:none;
  background:var(--cap-bg);
  box-shadow:0 1px 2px rgba(20,30,25,.14),0 2px 6px rgba(20,30,25,.09),0 6px 14px rgba(20,30,25,.07),inset 0 1px 0 rgba(255,255,255,.9),inset 0 -1.5px 1px rgba(20,30,25,.06);
  border:1px solid color-mix(in srgb,var(--accent) 16%,transparent);
  transition:transform var(--nav-dur) var(--nav-ease),width var(--nav-dur) var(--nav-ease),height var(--nav-dur) var(--nav-ease)}
.tb-cap.cap-no-anim{transition:none}                 /* снап на init/resize/reflow */
[data-theme="dark"] .tb-cap{border:none;            /* темна: inset-рим замість бордера */
  box-shadow:0 1px 2px rgba(0,0,0,.3),0 4px 12px rgba(0,0,0,.2),0 8px 20px rgba(0,0,0,.14),inset 0 1px 0 rgba(255,255,255,.14),inset 0 -1px 0 rgba(0,0,0,.18),inset 0 0 0 1px color-mix(in srgb,var(--accent) 16%,transparent)}

/* пункт навігації — над капсулою (z:1 > z:0) */
.nav-i{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;
  padding:8px 4px;font-size:10px;font-weight:600;line-height:1;color:var(--text-muted);
  position:relative;z-index:1;transition:color .15s,transform .12s;cursor:pointer}
.nav-i:active{transform:scale(.96)}                  /* тактильний відгук тапу */
.nav-i svg{width:22px;height:22px}
.nav-i[data-tab="fuel"] svg{transform:translateX(2.5px)} /* оптичне центрування асиметричної іконки */
.nav-i.act{color:var(--accent-text)}                 /* світла #2E7355 */
[data-theme="dark"] .nav-i.act{color:#48A074}         /* G1 залочено (мʼякший за --accent-text #4FAE7A) */

/* fallback: нема backdrop-filter → щільний непрозорий фон */
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
  .bottom-nav{background:rgba(255,255,255,.96)}
  [data-theme="dark"] .bottom-nav{background:rgba(20,28,24,.96)}
}
/* a11y: «Зменшити прозорість» → непрозорий бар (як native) */
@media(prefers-reduced-transparency:reduce){
  .bottom-nav{background:var(--surface-2);backdrop-filter:none;-webkit-backdrop-filter:none;border-top:1px solid var(--border-subtle)}
}
@media(prefers-reduced-motion:reduce){.tb-cap{transition:none}}
```

### JS (вимір + slide/snap + хуки)

```js
function measureNav(){const n=$('bnav');if(n)document.documentElement.style.setProperty('--nav-h',n.offsetHeight+'px');}
function placeCap(snap){
  const nav=$('bnav');if(!nav)return;
  const cap=nav.querySelector('.tb-cap'),btn=nav.querySelector('.nav-i.act');
  if(!cap||!btn){if(cap)cap.style.opacity='0';return;}
  const nr=nav.getBoundingClientRect(),r=btn.getBoundingClientRect();
  if(r.width===0){cap.style.opacity='0';return;}      // нав ще не в лейауті → переміряємо хуком
  const apply=()=>{cap.style.width=r.width+'px';cap.style.height=r.height+'px';
    cap.style.transform='translate('+(r.left-nr.left)+'px,'+(r.top-nr.top)+'px)';cap.style.opacity='1';};
  if(snap){cap.classList.add('cap-no-anim');apply();requestAnimationFrame(()=>requestAnimationFrame(()=>cap.classList.remove('cap-no-anim')));}
  else apply();
}
// перемикання табу: boot=snap, далі=слайд
function setTab(t){
  document.querySelectorAll('.nav-i').forEach(b=>b.classList.toggle('act',b.dataset.tab===t));
  placeCap(!_navReady);_navReady=true;
  document.querySelectorAll('.screen').forEach(s=>s.classList.toggle('active',s.id==='sc-'+t));
  /* … renderContent() … */
}
$('bnav').addEventListener('click',e=>{const b=e.target.closest('.nav-i');if(b)setTab(b.dataset.tab);});
// хуки перерахунку (вимір ширини капсули має відбутись ПІСЛЯ кожної зовнішньої зміни геометрії)
function _navSync(){measureNav();placeCap(true);}     // snap
window.addEventListener('resize',_navSync,{passive:true});
if(window.visualViewport)window.visualViewport.addEventListener('resize',_navSync,{passive:true});
window.addEventListener('load',_navSync);
// ⚠️ при порту ДОДАТИ: document.fonts.ready → placeCap(true) (ширина підписів зсувається на завантаженні шрифту;
//    у Drive Lens fonts.ready наразі сінкає лише seg-thumbs — капсулу варто додати в той самий хук)
```

### Принципи (чому так)

- **Капсула = постійний елемент, вимір getBoundingClientRect, не CSS-формула** (та сама A54-механіка) — стійко до різної ширини підписів. Анімуються `transform`+`width`+`height`. Boot/resize/reflow = снап (`cap-no-anim`), тап = слайд.
- **Капсула ПОЗАДУ підписів** (`z:0` vs `.nav-i z:1`). Скло на барі, капсула — на склі, підписи — над капсулою.
- **Дворежимна тема (A45):** світла — піднята плашка (border + зовнішня тінь); темна — обʼєм inset-рімом і темнішими тінями, `--cap-bg:--surface-4` (тоном, не кольором).
- **Active-колір — окреме залочене значення на тему** (світла `--accent-text #2E7355`; темна `#48A074` G1 — НЕ `--accent-text #4FAE7A`, мʼякший).
- **Іконки stroke=currentColor** → автоматично йдуть за станом `.nav-i` (muted→accent). Per-icon оптичні нюджі (`fuel +2.5px`).

**Анти:** перебудовувати капсулу/бар на тап (rebuild → снап замість слайду; tb-cap МАЄ бути постійним — A54 Урок 3); CSS-формула позиції замість виміру; забути `load`/`resize`/`fonts.ready` снап (капсула застрягне на `opacity:0`, бо міряли при width 0); покласти капсулу над підписами. **Зв’язок:** **A54** (slide-механіка thumb — спільна), **A55** (overlay+скло+висота бару), **A45** (обʼєм тоном на темній), **A15** (nav padding 3-state — тут overlay-варіант з sab у padding). *Drive Lens Batch 35 (скло) → 41 (overlay+height+повний еталон).*

## A57. Motion-мова — драбина тривалостей + словник easing + снап/слайд ✅

**Що це.** Єдина система руху всіх Lens: одна **драбина тривалостей**, фіксований **словник easing**, і принцип **«снап на лейаут, анімуй на дію»**. Зводить розрізнені рішення A18/A27/A54/A56 в одну мову. Значення — з batch41, усі device-валідовані. Нова анімована поверхня **бере час із драбини**, не вигадує свій.

### Драбина тривалостей

|Час   |Для чого                                                |Приклади (batch41)                                                   |
|------|--------------------------------------------------------|---------------------------------------------------------------------|
|`.10s`|тактильний прес `:active{transform:scale(.96–.97)}`     |CTA, sum-cell, btn-pri, fl-cta, fg-cell, nav-i                       |
|`.12s`|фон-фідбек дрібних поверхонь                            |пігулки, icon-btn, menu-i, sh-x, chip-btn, date-btn, `tm-in` поп меню|
|`.14s`|колір/бордер/фон карток-рядків                          |rec, rf, inp, seg-i, ty-i, jd, cta-btn                               |
|`.15s`|app-bar elevation · nav-i колір · pk-chev оберт         |                                                                     |
|`.16s`|мульти-проп картка (border+bg+shadow+transform)         |sum-cell, sum-val                                                    |
|`.18s`|chevron-оберт · `.sw`-тогл (трек + палець)              |jd-chev, sw-tr(::after)                                              |
|`.20s`|swipe-row слайд `cubic-bezier(.4,0,.2,1)` · toast in/out|                                                                     |
|`.24s`|backdrop-fade (sh-bg opacity)                           |                                                                     |
|`.25s`|crossfade іконки теми (sun↔moon)                        |                                                                     |
|`.26s`|sheet-slide + sheet visibility-delay                    |                                                                     |

### Словник easing

- **короткий UI-фідбек (.10–.18s)** → `ease`/лінійний: миттєвий, без характеру.
- **структурний рух (sheets)** → `cubic-bezier(.32,.72,0,1)` — iOS-крива, м’який вихід (A18).
- **swipe-рядок** → `cubic-bezier(.4,0,.2,1)` — стандарт-decelerate (A22).
- **«живий» вибір (повзунок/капсула)** → **пружина з овершутом** (per-product, device-розійшлися — НЕ дрейф): seg-thumb — QR A54-капсула `--seg-dur:500ms` `--seg-ease:cubic-bezier(.34,1.70,.64,1)` (A54, `batch44_2` р.73); Drive `.type-seg` `450ms` `cubic-bezier(.34,1.56,.64,1)` (b33, 14.13); nav-капсула `--nav-dur:400ms` `--nav-ease:cubic-bezier(.34,1.3,.64,1)` (A56 — **м’якша** пружина, бо шлях довший). Пружина ТІЛЬКИ на selection-thumb, НЕ на структурному русі.
- **живий пульс** → `livePulse 1.4s ease-in-out infinite` (sync/live dot, A30).
- **«характер»-жест (expressive)** → WAAPI overshoot-pop **поза драбиною**: функц-фідбек тримається в драбині (стеля .26s), а expressive «характер» (велика картка card-select, **950ms** `cubic-bezier(.34,1.56,.64,1)`) — окремий **НЕ-блокуючий** шар ПОВЕРХ, її стелю не порушує (A67.1). easing працює ЛИШЕ в парі з тривалістю — та сама крива на 140ms і на 950ms = різний характер.
- **layout-driven reveal (банер / акордеон-розкриття)** → **candidate-A hybrid** (device✓ B46): банер лишає in-flow `height` 0→H на **main-thread** (unfold-характер збережено) + список (`.screen`) їде **composite** `translateY` синхронно (`.bnr-pin`: `position:absolute` @ `header_h`, `will-change` ЛИШЕ на видимому екрані) + **снап@onfinish** (1 repaint). **decel** `cubic-bezier(.4,0,.2,1)`, **~600ms, overshoot-FREE.** Пружина/овершут ЗАБОРОНЕНІ (layout-shift розміру → овершут = «гумовий» лейаут; пружина лише на selection-thumb/капсулі). Token-guard проти flush при швидкому open→close; reduced-motion = снап. **Чому hybrid, а не pure in-flow `height` (B36):** in-flow height = layout-prop → 14 карток repaint щокадру = 30–40ms спайки на XS (frame-gap довів, wsd 2.4); hybrid відчіпляє пейнт списку → dropped=0 / max-gap 17–27ms. **Чому НЕ composite-only (FLIP-overlay, candidate C):** C гладший, але дає «descend» (банер сповзає з-під хедера) — Konst device-відхилив характер; «unfold на місці» (низ банера зчеплений з верхом 1-ї картки) ФІЗИЧНО вимагає cross-thread sync = A (свідома «поступка»: ледь помітний мікродрейф на стику, device-прийнятний). *(QR Lens — `#ph-banner` reveal Tab-2; bannerJank RESOLVED, wsd 14.20.)*
- **mode-switch close на context-switch табі → VT-crossfade** (device✓ B47): коли × / close міняє НЕ лише позицію, а **весь вид** (текстура fused→норм + поява filter-row + content swap) — обгортка `render()` у `document.startViewTransition` кросфейдить увесь diff як ОДНУ зміну. Семантика: **VT-crossfade = context switch** (Tab-1/3/4) ПРОТИ **slide = same-context reclaim** (Tab-2 candidate-A банер). per-context motion ≠ непослідовність. per-tab `--vt-cross` device-pick (overview500/qr400/equip500). Гард-набір — wsd 2.4 (feature-detect+фолбек · reduced-motion вручну · швидкий синхр. колбек · `[data-vt]`-scope проти колізії з тема-VT B28). *(QR Lens 14.20.)*
- **VT володіє морфом** (device✓ B47.1): під VT-перехід **гасити власну entry-анімацію** елемента — кросфейд САМ морфить значення. Прецедент: gauge переграв 2200ms width-fill ВСЕРЕДИНІ 500ms VT → (а) fps-просадка (width=layout-prop thrash A70 під VT-композитом на XS) + (б) «порожній бар→refill» (rAF-reset 0% ПІСЛЯ синхр. VT-колбека → пустий new-snapshot). Фікс: ранній вихід entry-аніми під VT-прапор → `.sg-seg` лишаються на фінальній inline-ширині → VT морфить 67%→80% сам. Особливо критично для **layout-prop** анімацій (width/height) — вони і так thrash-небезпечні (A70), а під VT-композитом ще й конфліктують зі знімком.
- **асиметрія open/close — ОКРЕМІ криві, не дзеркало** (A18.1): open = decel `(.32,.72,0,1)` «рішуче прибуття»; close = accel-in `(.4,0,1,1)` + micro-`scale(.98)` «рішучий відхід». Симетрична крива на close відчувається мляво. *(QR Lens Phase 3 — sheet-close B39.)*

### Принцип: «вимір → снап на лейаут, слайд на дію»

- Геометрію міряти (`getBoundingClientRect`), не CSS-формула (A54/A56).
- **Снап** (`.seg-no-anim`/`.cap-no-anim`, через double-`requestAnimationFrame`) на: init, зміну теми, resize, показ табу/шіта, `fonts.ready`.
- **Слайд** лише на **реальну зміну вибору** (тап). Прапор «змінилось?» тримати окремо (`_lastFilter`/`_lastFuelScope`/`_navReady`), НЕ виводити з факту виклику render.
- `.no-transition,.no-transition *{transition:none!important}` + double-rAF на launch (A27) — щоб зміна CSS-vars при `applyTheme()` не блимала.

**Наскрізь:** кожна анімація має `@media(prefers-reduced-motion:reduce){…transition:none}` (присутній у seg-thumb, tb-cap, sh-bg/box, theme-menu — додавати на КОЖНУ нову). НЕ `will-change` на постійних шарах (A18 — композитинг-шви).

**Тригер:** нова анімована поверхня. **Анти:** магічний час поза драбиною (.19s/.35s); пружина на структурному русі (sheet з овершутом = «гумовий»); забути reduced-motion; ручний slide там, де разом міняється контент/текстура (роз'їзд — бери VT); власна entry-аніма елемента під VT-перехід (competition — гаси, VT володіє морфом); layout-prop (width/height) аніма під VT-композитом на слабкому залізі (thrash A70); судити motion-фікс лише оком без frame-gap-readout (ms — штатна база, wsd 2.4). **Зв’язок:** A18 (sheet enter/exit), A27 (reduce-motion+init), A30 (livePulse), A54 (seg-thumb), A56 (nav-капсула), A70 (layout-prop thrash під рухом/VT), wsd 2.4 (frame-gap трійка + VT-best-practice), wsd 14.20 (banner-motion arc). *Зведено аудитом batch41 (Round 2); banner-reveal→candidate-A + VT-close додано B46/B47 (`batch47_2`, 14.20); seg-канон **per-product**: Drive 450ms/(.34,1.56) з wsd 14.13 (slow-mo показав 300 задовгим навіть для 3-seg), QR A54-капсула розійшлась device-тюном до 500ms/(.34,1.70,.64,1) — `batch44_2` р.73, 14.19.*

## A58. Sheet-меню / профіль-система (genSheet + grouped-cards + About + кредит) ✅🔧

**Що це.** Avatar-пігулка → меню-шіт → grouped action-рядки → generic під-шіти (Налаштування/Архів/Допомога/Про). Крос-продуктова. 🔧 у QR/KPI замість профіль-дій там список SR → підміняти вміст `MENU[]`, каркас 1:1.

### Декларативний `MENU[]` → `renderMenu()`

- group = `{eb?, items:[…]}`; item = `{key, label, icon, act?, disabled?, note?}`.
- рендериться у `.gcard` (grouped-card) з `.eb`-eyebrow заголовком групи. Портативність: інший продукт підміняє вміст `MENU[]`, рендер незмінний.

### genSheet — один generic-шіт

`genSheet(title,bodyHtml)` пише в `#gen-title`/`#gen-body` і відкриває `sh-gen`. Один шіт обслуговує Налаштування/Архів/Допомога/Про/Синхронізацію — **не плодити окремі DOM-шіти** під кожну дію.

### Двоступеневий sheet→sheet handoff (реюзабельний жест)

```js
b.addEventListener('click',()=>{closeSheet('sh-menu');setTimeout(()=>menuAction(key),120);});
```

Закрити поточний шіт → `setTimeout(…,120)` (≈ fade меню, драбина A57 `.12s`) → відкрити наступний. Без затримки два шіти **накладаються/блимають**. 120 = синхрон із закриттям.

### Grouped-cards мова (`.gcard`/`.eb`)

```css
.gcard{background:var(--surface-3);border:1px solid var(--border-subtle);border-radius:var(--rs);padding:0 12px;overflow:hidden}
[data-theme="dark"] .gcard{border-color:var(--border-default)}
.eb{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text-muted);margin:18px 4px 7px}
.gcard .menu-i{border-radius:0;padding:13px 0;border-bottom:1px solid var(--border-subtle)}  /* плоскі рядки з дільником, НЕ пігулки-кнопки */
.gcard .mi-ico{background:var(--surface-4)}  /* іконка на surface-3-картці піднята на surface-4, щоб не злилась */
```

Темна: дільники subtle→default (A48 dark-bump). `.eb` — та сама eyebrow-мова, що A48, але для груп налаштувань.

### Disabled-рядок з нотаткою = візуальна форма wsd 3.9 «без заглушок»

`{disabled:true, note:'Доступно після…(Етап 2)'}` → `.menu-i:disabled` (приглушені лейбл+іконка) + `.mi-note` пояснення. Майбутня фіча показується як **disabled з видимою причиною**, не прихована й не фейк-клікабельна.

### `.doact` — дія замість шеврона

```css
.doact{font-size:11px;font-weight:700;color:var(--accent-text);flex-shrink:0}
```

Навігаційний рядок → `.mi-chev` шеврон; рядок-що-робить-дію (Export) → тиха зелена позначка формату (`JSON`) замість шеврона.

### About-шіт

- version-рядки читають `APP_BUILD` (wsd 10.6) — нуль хардкодів: Версія/Дата збірки з констант.
- `.about-row` (k/v); `a.ar-v{color:var(--accent-text)}` = link.
- кредит автора + **`.tgpill` Telegram-капсула** (токени `--tg:#229ED9; --tg-soft; --tg-bd`): badge-кружок + нік + стрілка-out. **Крос-продуктовий контакт** — той самий у всіх Lens.
- `.note-banner` — інфо-смуга (icon `--accent-text` + текст, `surface-3`).

Вхід: `.av-pill` (прізвище-пігулка в app-bar) → `renderMenu();openSheet('sh-menu')`.

**Анти:** окремий DOM-шіт під кожну дію (замість genSheet); відкривати наступний шіт без 120ms-затримки (накладання); фейк-рядок майбутньої фічі без disabled+причина (wsd 3.9); пігулки-кнопки в grouped-card замість плоских рядків. **Зв’язок:** A48 (eyebrow+dark-bump), A52 (`.sw` у Налаштуваннях), A53 (`.pk` у Налаштуваннях), A57 (handoff = `.12s`), A59 (toast «Збережено» в onChange), wsd 3.9 (no-stubs), wsd 10.6 (APP_BUILD). *Drive Lens Batch 31 (grouped-cards) → 41 (повна система, аудит Round 2).*

## A59. Мікро-компоненти: toast / sync-pill / sparkline / confirmAction ✅

### toast (слайд-ап над таб-баром)

```css
.toast{position:fixed;left:50%;bottom:calc(var(--nav-h,64px) + 14px);transform:translateX(-50%) translateY(20px);background:var(--text-primary);color:var(--surface-1);padding:11px 18px;border-radius:22px;z-index:400;opacity:0;transition:opacity .2s,transform .2s;pointer-events:none}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
```

```js
let _tt=null;
function toast(msg){const t=$('toast');t.textContent=msg;t.classList.add('show');clearTimeout(_tt);_tt=setTimeout(()=>t.classList.remove('show'),1900);}
```

Offset над баром через `--nav-h` (той самий вимір A55/A56); slide-up `.2s` (A57); **`_tt` clearTimeout** — повторний toast не плодить таймери; `pointer-events:none` (не краде тапи).

### sync-pill — ідіома «тихо на успіху, гучно на проблемі»

```css
.sync-pill{…;max-width:0;overflow:hidden;transition:background .12s,border-color .12s,color .12s}
.sync-pill[data-state="synced"]{max-width:34px;padding:5px;color:var(--text-muted)}  /* лише дот */
.sync-pill[data-state="syncing"]{max-width:200px;color:var(--accent);border-color:var(--border-subtle)}
.sync-pill[data-state="pending"]{max-width:200px;color:var(--warn);border-color:var(--warn)}
.sync-pill[data-state="offline"]{max-width:200px;color:var(--crit);border-color:var(--crit);background:color-mix(in srgb,var(--crit) 8%,transparent)}
.sync-pill:not([data-state="synced"]) .sp-text{display:inline}
```

Ширина анімується `0→34`(дот)`→200`(дот+текст). Успіх — мінімальний слід; проблема — розкривається з кольором стану (A35: warn/crit). `setSync(state,extra)` пише `data-state` + `aria-label`. livePulse (A57/A30) на syncing-доті.

### sparkline (inline-SVG примітив)

```js
function sparkline(vals){ /* 88×30, нормалізація min/max */
  …return `<svg class="spark" viewBox="0 0 88 30" fill="none"><path d="…" stroke="var(--info)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle … r="2.6" fill="var(--info)"/></svg>`;}
```

Колір токеном (`--info`); остання точка = крапка-маркер. У Drive Lens **RESERVED** (відкладений Tab-1 hero) — дозволений «примітив під рішення» (wsd 3.9), не видаляти без рішення.

### confirmAction (деструктив-підтвердження, реюз)

```js
function confirmAction(title,desc,onOk){
  $('cf-title').textContent=title;$('cf-desc').textContent=desc||'';
  const ok=$('cf-ok'),fresh=ok.cloneNode(true);ok.parentNode.replaceChild(fresh,ok); // скинути попередній handler
  fresh.addEventListener('click',()=>{closeSheet('sh-confirm');onOk();});
  openSheet('sh-confirm');
}
```

Один шіт `sh-confirm` під будь-яке видалення (запис/заправка). **cloneNode-reset:** кнопка постійна в DOM, `onOk` щоразу інший → клонувати вузол, щоб скинути попередній listener. Це не guard (A21), а свідомий **reset one-shot handler** на постійній кнопці.

**Анти:** toast без `clearTimeout` (накладання таймерів); sync гучний на synced (шум); прямий `addEventListener` на постійну confirm-кнопку без reset (стек old-handlers). **Зв’язок:** A55/A56 (`--nav-h` для toast), A57 (тривалості), A30 (livePulse), A35 (кольори станів), A21 (listener-стек — confirmAction вирішує reset’ом), wsd 3.9 (sparkline як дозволений RESERVED). *Drive Lens: toast/sync Batch 13–16; confirmAction Batch 10; sparkline RESERVED 16a. Зведено аудитом Round 2.*

## A60. Місяць-пікер 3×4 + floor-guard + рік-пігулка (універсальний core) ✅

**Що це.** Спільне ядро навігації місяцями — промоутнуте з A50/Частина B, бо однакове для **Tab-Місяць** і **range-календаря**. Тут — універсальна частина; range-специфіка (drill день↔місяць) лишається в A50.

### 3×4 сітка місяців (`.mg-*`)

- `.mg-grid` = 12 кнопок `MON_AB` (Січ…Гру); `.mg-cell.cur` = поточний; `.mg-cell.off[disabled]` = до floor.
- живе в шіті: `sh-month` (Tab-4) / `calMonView` (range-drill A50).

### floor-guard (КЛАС помилки — не ставити стіну вперед)

- **назад** = `dataFloor()` (місяць/рік 1-го запису): рік-стрілка `prev` гасне на floor; клітинки до floor `disabled`.
- **вперед — БЕЗ межі.** Котити через Н.Р.: `if(m>12){m=1;y++}`. ❗ НЕ прибивати на «кінець року» — прихована стіна на переході Гру→Січ (та сама помилка, що ловилась у A33).

### Рік-пігулка `.mg-y` (свайп + тап на одному елементі)

- `◂2026▸`; свайп року через `bindSwipeX` (A44); `_swiped`-guard відділяє свайп від тапу.
- спільний клас `.mg-y`, **окремі id** на консумент (`mgYear` Tab-4 / `calMgY` range) — ізоляція стану (wsd 14.10). Каретка-мова (▾/▴) — ЛИШЕ range (A50); Tab-4 без денної в’юшки → без каретки.

### Два консументи

- **Tab-Місяць nav:** `openMonthPicker()`→`renderMonthGrid()`; `monthStep(dir)` (floor-guard, одна точка для стрілок І свайпу — DRY); `bindMonthSwipe` (свайп = бонус A44, стрілки `.mo-arrow` = основне; пігулка-місяць `.mo-lbl` на сторінці-`surface-2`). `renderMonth()` виставляє `document.documentElement.dataset.season=seasonOf(m)` → **драйвить A43-банер** (хто перемикає сезон — оце тут; сам банер в A42/A43).
- **range-календар drill (A50):** той самий grid у `calMonView`, ids `calMg*` + drill-специфіка (лишається в A50).

**Анти:** forward-стіна на кінці року (прихований баг Гру→Січ); спільні id між консументами (зіткнення стану); вішати свайп на сітку днів замість пігулки/смужки (A44 — краде тап). **Зв’язок:** A33 (range-grid база), A50 (drill-специфіка → посилається сюди), A44 (свайп+`_swiped`), A43 (season-банер драйвиться `renderMonth`), wsd 14.10 (ізоляція id). *Drive Lens Tab-4 Batch 22 (base) → range Batch 25–29.1. Промоутнуто аудитом Round 2.*

-----

## A61. Chrome (pinned-зона під app-bar) — форма та dark-elevation

**Стек chrome (Журнал, Drive Lens Batch 11d–f):** `app-bar → filter-row (seg+date) → status-line (jStats)` — усі pinned, статичні; search = перший елемент **скролу** (не chrome).

**Обрана форма = edge-to-edge слаб** (на всю ширину, без радіуса). Обʼєм:

- **Світла:** низхідна тінь на контент `box-shadow:0 4px 12px rgba(20,30,25,.06)`. Тінь верхнього chrome-бенду ховається за непрозорим нижнім (пізніший sibling малюється поверх) → одна тінь на межі chrome↔контент, без ліній між бендами.
- **Темна:** `box-shadow:none` — тіні на темному фоні невидимі. Обʼєм виключно через **тон** (s2 хром → s3 страйп → s1 контент).

**❗ Dark gotcha (root-cause, не вгадувати):** chrome-страйп НЕ повинен мати `background:var(--surface-1)` на темній — це колір фону сторінки (#0D1110) → страйп зливається у «чорну порожнечу», ледь видимий. Рішення: на темній підняти на `--surface-3` (світліший за фон) + лише faint `--border-subtle`. Хайлайт `inset 0 1px 0 rgba(255,255,255,.05)` та товстий `--border-default` — **зайві**, дають «лінії що вибиваються». На світлій `--surface-1` (мʼякий сірий) — норм, бо ≠ білого app-bar.

**Search у скролі:** заокруглений бокс — `border:1px solid var(--border-subtle)` + `border-radius:var(--rs)` + `padding:8px 14px` (НЕ `border-bottom`-only — дає гострі кути). Дихає завдяки `.scroll-a padding-top` (спільний).

**Компакт:** однорядковий status-line — `padding:7px 14px` (не 10px); нижче 6px текст тисне до бордера.

> 💭 **Бек-лог на майбутнє: «острів-картка».** Альтернатива edge-to-edge: filter+stats як один заокруглений острів (inset бокові поля + `border-radius:var(--r)` + тінь на світлій / світліший фон+хайлайт на темній). Візуально симпатичніше/камерніше, АЛЕ ламає поточну edge-to-edge Lens-логіку → відкладено. Якщо колись — застосовувати по всіх Lens-ах консистентно. (Порівняння: `Drive_Lens_chrome_compare.html`, Batch 11.)

-----

## A62. Підняв картки → підніми й хром (elevation-паритет); власний токен, не реюз спільного surface ✅

**Симптом.** Після підняття елевації карток (ширша дельта `card↔bg`) хром/смуга (пошук, фільтр, банер) лишилися на «підлозі» сторінки → внутрішній дисбаланс: картки злетіли (+18), смуга провисла (+3–4), хром виглядає нижчим за контент.

**Корінь (два).**

1. **Елевація відносна.** Підняли один ярус (картки) — решта ярусів того ж екрана мовчки лишаються на місці. Око читає елевацію як *різницю*, не абсолют.
1. **Реюз спільного surface-токена.** Смуга сиділа на службовому токені (`--bg-soft`), який ще жере купа елементів (pill, icon-btn, nav active, rank-кружок, ctx-strip). Підняти смугу через цей токен = зачепити ВСІХ.

**Правила.**

- **Підняв ярус — перевір усі сусідні chrome-яруси** того ж екрана (банер/пошук/фільтр).
- **НЕ перетюнюй спільний surface-токен заради одного елемента.** Зміна базового surface каскадить на КОЖНОГО споживача (selected-картка, смуга, хром, пігулки). Дай піднятому елементу **власний токен** (`--band`/`--band-sh`), тема-спліт. Перед дотиком до токена — `grep` усіх споживачів.
- **Тема-спліт елевації (A39):** смуга читається різно по темах → **темна = лифт** (`color-mix` до `--card` + A45 top-хайлайт; є хедрум над near-black підлогою), **світла = well** (A51 inset; смуга вже втоплена). Той самий елемент, протилежна метафора по темі.
- **Спорідненість тем несе акцент + мова елевації, не збіг hue фону.** (selected обрали як *well* на обох темах, не teal-елевацію — однаковий характер крізь теми.)

**Тригер:** будь-яке підняття елевації карток/контенту, що лишає хром на старому рівні.
**Анти:** «підняв картки, забив на смугу»; «перетюнив `--bg-soft`, бо швидше» (зламав 5 інших споживачів).

**Зв’язок:** A45 (об’єм тоном на темній), A51 (well на світлій), A39 (однакове ≠ однаковий характер; спліт по темі), A8 (специфічність токен-оверрайдів), A61 (chrome-форма). *Прецедент: QR Lens Фаза 1 (Batch 25.1→25.2) — +Lift розширив `card↔bg`; selected-картка (well `#1a212c`), warm-worst тинт (по всій картці top+bottom > лише низ, % перетюнено під холоднішу/світлішу Lift-картку — Вебер+hue-cancel, A39), потім смуга через власний `--band` (темна Lift-M ≈+10 / світла Well) + rail 3→4px.*

## A63. Втоплена поверхня під картками у sheet/панелі (card-on-card → recess) — паритет зі сторінкою; тема-спліт ✅

**Симптом.** Картки (`--card`) всередині шіта/панелі, чий фон теж `--card` → однакова заливка, розділяє лише бордер → пласко, без елевації. На сторінці (Tab) та сама картка лежить на `--bg` → чіткий об’єм.

**Корінь.** Картці потрібна **інша поверхня під нею**, щоб читатись піднятою. Панель = `--card` забирає цей контраст.

**Рішення — втопити LIST-зону шіта у фон-сторінки** (iOS grouped-list ідіома: картки на grouped-grey). Тема-спліт (A39):

- **Світла → `--bg`** — делікатний grouped-grey, паритет зі сторінкою.
- **Темна → `--bg-soft`, НЕ `--bg`.** Повний `--bg` (near-black) під рамкою `--card`, поверх затемненого бекдропа шіта, читається як **«діра»** (зливається з бекдропом). `--bg-soft` лишається контейнером і дає картці поп (+~15).
- **+ нижній padding** списку, щоб поверхня тяглася під останню картку.

**Scope:** лише list-зона з картками. Рядкові шіти (опції-список, чіп-фільтри) цього не потребують — там роздільники несуть структуру.

**Тригер:** картки в шіті/панелі на тому ж surface, що й панель.
**Анти:** «бордер же є» (бордер ≠ елевація); «`--bg` на обох темах» (на темній — діра).

**Зв’язок:** A46 (card-in-card surfaces), A45 (об’єм тоном), A39 (спліт по темі), A8 (дуальний-селектор оверрайд). *Прецедент: QR Lens Фаза 1 (Batch 25.2) — drill-шіт обладнання (`#sh-eq-list` ph-картки): світла `--bg` / темна `--bg-soft`. Закрило відкрите «картки шіта на чисто-білому».*

## A64. Баланс контрол-ряду між хедером і списком — подвійний зазор ✅

**Симптом.** Контрол-ряд (пошук+фільтр) між хедером/банером і списком відчувається зміщеним угору — під ним більше повітря, ніж над.

**Корінь.** `padding-bottom` ряду **складається** з `padding-top` списку (`.ph-list`/`.eq-cards`) → зазор знизу ≈ 2× зазору згори (10+10=20 проти ~10–14).

**Рішення — симетричні ЗОВНІШНІ зазори.** Врахувати `padding-top` списку в `padding-bottom` ряду: ряд `padding: N 16px small`, де `small + список-padding-top ≈ N`. «Повітря над рядом» класти у `padding-top` ряду, а не в ad-hoc `margin-top`-милиці.

```css
/* список має padding-top:10 → ряд: 14 згори / 4 знизу = 14/14 зовні */
.filter-row{padding:14px 16px 4px}
```

**Тригер:** контрол-ряд, за яким одразу йде список зі своїм `padding-top`.
**Анти:** симетричний `padding` ряду БЕЗ урахування padding списку (= знов подвійний зазор знизу); `margin-top`-хак для «повітря згори» (дає 18/14 дисбаланс).

**Зв’язок:** A15 (nav padding 3-state), A61 (chrome-стек). *Прецедент: QR Lens Фаза 1 (Batch 25.2) — filter-row Tab2/Tab4: 10/10+10 → 14/4(+10)=14/14, прибрано no-banner `margin-top:4`.*

## A65. Дві мови глибини: ПОЛЕ=well (deboss) vs КНОПКА/ЧІП=elevation (lift); well-токен-стандарт ✅

**Принцип.** Глибина — не один ефект, а **дві протилежні мови**, що несуть різний афорданс:

- **ПОЛЕ вводу/контейнер-вмісту** (search-row, filter-кнопка, GUID-бокс) = **DEBOSS / well** — втоплене в сторінку, inset-тінь усередину. Семантика: «торкни/впиши/жамкай» (A51).
- **КНОПКА/ЧІП-дія** (фільтр-чіп, CTA, капсула) = **ELEVATION / lift** — піднята над сторінкою, drop+градієнт. Семантика: «натисни мене».

Плутати їх не можна: підняте поле читається як картка-результат (а не ввід), втоплена кнопка — як неактивна/disabled.

**Дзеркальність по темах (well, A39/A45-aware):**

|                      |СВІТЛА                             |ТЕМНА                                                                                                   |
|----------------------|-----------------------------------|--------------------------------------------------------------------------------------------------------|
|**well (поле)**       |inset тінь усередину (чорна зверху)|inset тінь зверху-внутр + **світло знизу** (білий .098) — на OLED чиста inset «діра», нижнє світло рятує|
|**elevation (кнопка)**|широка drop-тінь + градієнт (→A66) |світло зверху + слабка drop + градієнт (→A66)                                                           |

**well-токен-стандарт** — формалізувати well у два токени, не повторювати inset по місцях:

```css
:root{
  --well-bg:var(--bg-soft);
  --well-sh:inset 0 1px 5px rgba(0,0,0,.115);
}
[data-theme="dark"]{           /* + ДЗЕРКАЛО у @media(prefers-color-scheme:dark) auto-dark */
  --well-bg:color-mix(in srgb,var(--bg-soft) 70%,var(--card));
  --well-sh:inset 0 1.5px 2px rgba(0,0,0,.30),inset 0 -1px 0 rgba(255,255,255,.098);
}
```

Споживачі: `.guid-box`, `.ph-srch`, `.flt-btn` → `background:var(--well-bg);box-shadow:var(--well-sh)`. Одна правка токена = всі well-поля обох тем.

**⚠ Не плутати з `--band`/`--band-sh` (хедер-родина).** `--band` несе ВАЖЧИЙ хедер-тір (sr-pill/icon-btn, device-locked .37/.09) — окрема родина, НЕ well. Раніше `.ph-srch`/`.flt-btn` помилково тягли `--band-sh` (на темній `inset 0 1px 0 rgba(255,255,255,.05)` = біле ЗГОРИ = **EMBOSS** → поля читались як ПІДНЯТІ). Фікс = перевести їх на `--well-*`. **НЕ чіпати** окремими well-правками: `#ph-banner` (мʼякий lift — банер, не поле) і хедер-родину.

**Хедер-родина dark DEBOSS — повний блок (sr-pill/icon-btn, B27.2, device-locked):**
```css
/* світла недоторкана (--band-sh inset 2px на світлому fill — already well-feel) */
[data-theme="dark"] .sr-pill,[data-theme="dark"] .icon-btn{
  background:color-mix(in srgb,var(--bg-soft) 70%,var(--card));        /* глибший recess-fill (band 70%) */
  box-shadow:inset 0 1.5px 2px rgba(0,0,0,.37),                        /* тінь ЗВЕРХУ-внутр → втоплено */
             inset 0 -1px 0 rgba(255,255,255,.09)}                     /* світло ЗНИЗУ → рятує від «діри» на OLED */
/* auto-dark близнюк ОБОВ'ЯЗКОВИЙ (A69 — значення ХАРДКОД, не токени) */
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]) .sr-pill,:root:not([data-theme="light"]) .icon-btn{
  background:color-mix(in srgb,var(--bg-soft) 70%,var(--card));
  box-shadow:inset 0 1.5px 2px rgba(0,0,0,.37),inset 0 -1px 0 rgba(255,255,255,.09)}}
```
Це **DEBOSS** (well, A51) — на відміну від chip/qr-chip-LIFT (A66.1). Скоуп ЛИШЕ хедер-родина (`--band`/`--band-sh` недоторкані → `ph-banner`/`srch`/`flt` цілі). *Source: `batch41_1` р.165–168; auto-dark близнюк B31.3.*

**Чому окремий токен, а не реюз `--bg-soft`.** `--bg-soft` — спільний (sr-pill/icon-btn/ph-rank/press-стани); ретюн його = каскад-регрес (регрес-урок QR Batch 25.2). well-зміни — у власний `--well-*` (споріднено A62 — підняв картки→підніми хром власним токеном, не реюз спільного).

**RECESS-таця — ground під елементами (B31).** Recess застосовується не лише до ПОЛЯ вводу (well), а й до **ground-поверхні**: таця за чіпами втоплена (`--tray-*`), щоб чіп читався як **figure без важкого власного drop**. Саме тому A66 світлий drop зменшено `.120→.07` — figure-ground несе западина, а не тінь чіпа («важкий drop у западині = висить над ямою»). Окремий токен, не реюз `--well-*`/`--bg-soft`:

```css
:root{
  --tray-bg:color-mix(in srgb,var(--bg),var(--border-2) 30%);
  --tray-sh:inset 0 2px 6px rgba(0,0,0,.14);                          /* світла: recess тінню */
}
[data-theme="dark"]{           /* + ДЗЕРКАЛО у @media(prefers-color-scheme:dark) auto-dark */
  --tray-bg:color-mix(in srgb,var(--bg),var(--card) 35%);
  --tray-sh:inset 0 2px 2px rgba(0,0,0,.16),inset 0 -1px 0 rgba(255,255,255,.05);   /* темна: tone-recess */
}
```

Споживач: `.qr-chips`. **recess/lift/flat — вибір device:** таця тестувалась у 3 станах (recess=втоплена / lift=піднята / flat=рівна) → обрано **recess** (найчистіший figure-ground для чіпів).

**Named patterns — recess vs tone-recess** (два способи досягти втоплення):
- **recess** = inset-тінь усередину несе западину (світла таця: `.14` blur).
- **tone-recess** = западину несе **тон-плейн** (color-mix зсуває саму поверхню), коли inset слабкий/«душить». Темна таця: на near-black inset важкий → відділення несе тон (mix bg+card 35%, A45), inset лише підкреслює дип. Споріднено A45 (обʼєм тоном на темній) і A63 (recess-поверхня в sheet/панелі).

**Специфічність (A8):** well-токени тема-driven через `:root`/`[data-theme]` — конфлікту станів нема (поля без `.act/.sel` на well-проп).
**Анти:** «одна тінь well на обидві теми» (на OLED inset невидимий → «пересвідчено»/«діра»); реюз `--bg-soft` під well-зміну; well на банер/disabled.
**Зв’язок:** A51 (well-афорданс, тепер через `--well-*`), A45/A66 (elevation — інша мова), A39 (однакове число ≠ однаковий характер → спліт), A62 (власний токен замість реюзу спільного), A63 (recess-поверхня в sheet — споріднено tone-recess). *Source-of-truth: `QR_Lens_preview_batch31_3.html` — well `:root р.79 / dark р.102 / auto-dark р.122`, споживачі `.guid-box р.334 / .ph-srch р.396 / .flt-btn р.405`; tray `:root р.81 / dark р.103 / auto-dark р.123`, споживач `.qr-chips р.461`. ✅ device-confirmed (B30 well, B31 tray).*

## A66. Elevation асиметричний між темами: drop≥14px (світла) vs світло-зверху (темна), grad обидві ✅

**Принцип (розширення A45).** Підняту поверхню (чіп/плитка/кнопка-дія) не можна освітлювати однаково в обох темах: **інструмент об’єму різний, бо «мертвий» бік різний.**

- **СВІТЛА:** inset-світло зверху МЕРТВЕ (біле-на-білому не видно) → обʼєм несе **ШИРОКА мʼяка drop-тінь** (blur **≥14px**) + градієнт. Вузька тінь (≤4px) читається як потемніння КРАЮ, не як lift. **Виняток — recess-ground (A65):** якщо елемент сидить у втопленій таці, drop **мінімізується** (QR-чіп B31.1: `.07`, вузька) — западина вже дає figure-ground, широкий drop там = «висить над ямою». **Уточнення форми винятку (StockCheck b16):** падає саме **blur**, а **alpha ЛИШАЄТЬСЯ** (`dropB 3` при `dropA 14`) — предмет у ямі відкидає **коротку контактну** тінь, а не слабку. «Мінімізувати drop» ≠ «прибрати силу».
- **ТЕМНА:** drop-тінь МЕРТВА на OLED (A45) → обʼєм несе **inset-світло зверху** (`rgba(255,255,255,.11)`) + слабка drop + градієнт.
- **Градієнт `linear-gradient(180deg, +Fff, +000)` (±8%) — в ОБОХ темах** (імітує світло згори, дешевий і працює всюди).

```css
.qr-chip:not(.act){
  background:linear-gradient(180deg,
    color-mix(in srgb,var(--card) 92%,#fff),
    color-mix(in srgb,var(--card) 92%,#000));
  box-shadow:0 1px 2px rgba(0,0,0,.055),0 2px 6px rgba(0,0,0,.07);   /* B31.1: drop ВУЗЬКА .07 — чіп у recess-таці (A65); figure-ground несе западина, не тінь */
}
[data-theme="dark"] .qr-chip:not(.act),
:root:not([data-theme="light"]) .qr-chip:not(.act){   /* explicit-dark + auto-dark (A69) */
  box-shadow:inset 0 1px 0 rgba(255,255,255,.11),0 1px 2px rgba(0,0,0,.027),0 5px 14px rgba(0,0,0,.060); /* темна: топ-світло .11 + слабка drop */
}
```

**🔑 Узагальнення (StockCheck b16, device+product): амплітуда елевації = функція ҐРУНТУ, не функція родини.** Recess-виняток вище — окремий випадок ширшого правила. Три ґрунти: **сторінка** (непрозорий `--bg`) → шкала A66 як є · **западина** (таця A65) → drop-blur падає · **голе скло** (елемент поза тацею, на floating-island) → амплітуда **росте над базою**. Тому сусідні контролі однієї родини законно різні, якщо лежать на різному ґрунті; і навпаки — **всередині** западини recess діє на всю групу однаково, «головних» контролів там нема. *Розгорнуто: `StockCheck_island_glass_FINDINGS.md` §3f (таблиця ґрунтів + числа γ′).*
**Скоуп `:not(.act)`** — активний елемент має власний glow/fill, його НЕ чіпати (A8: `[data-theme] .X:not(.act)` (0,3,0) > `.X:not(.act)` (0,2,0) > база (0,1,0); `.X.act` мутуально-виключний).
**Тригер:** будь-яка підведена дія-поверхня, що читається об’ємно на обох темах.
**Анти:** «зробив тінь, на темній зникла» (A45); вузька drop (≤4px) на світлій = «потемнів край», не lift; одна тінь на обидві теми.
**Зв’язок:** A45 (об’єм тоном на темній — база), A39 (спліт по перцепції), A65 (це ELEVATION-мова, протилежна well; + RECESS-виняток для drop), A69 (auto-dark близнюк селектора). *Source-of-truth: `QR_Lens_preview_batch31_3.html` `.qr-chip:not(.act)` `р.472` (світла) / `р.473` (dark+auto-dark). ✅ device-confirmed (B31.1).*

### A66.1 Активний/обраний стан — UNIFIED tone-lift family + контекст-залежна сила drop (QR Phase 3, B38/B39) ✅

Коли елемент стає **ОБРАНИМ** (chip шіта / filter-button / Tab-3 qr-chip — у QR це один вигляд-родина), elevation-мова та сама асиметрія A66, але з фіксованим **accent-fill**:

```css
/* LIGHT — accent fill + drop (drop ∝ КОНТЕКСТ, таблиця нижче) */
.X.on{background:#dcefed;color:#0e2f2c;border-color:#33ccbd;          /* fill=accent-soft · text=accent-ink · border=accent */
  box-shadow:0 3px 6px rgba(0,0,0,.14),0 7px 18px rgba(0,0,0,.196)}   /* приклад: filter-button на сторінці */
/* DARK — tone-lift (drop мертва на OLED → fill світліша за сусідів + top-ридж) */
[data-theme="dark"] .X.on{background:#264a46;color:#fff;border-color:#8ae5dc;
  box-shadow:inset 0 1.2px 0 rgba(255,255,255,.26),  /* top-світло ридж (emboss-об'єм) */
             inset 0 -1px 0 rgba(0,0,0,.11),          /* нижня темна грань */
             0 6px 20px rgba(0,0,0,.15)}              /* слабка drop — декор, не несуча */
/* + auto-dark близнюк через @media (A69 — значення ХАРДКОД, не токени) */
```

**Dark tone-lift — ЧОМУ так (не glow, не drop):**
- **fill `#264a46` СВІТЛІША за неактивних сусідів** → фігура виступає тоном (advance);
- **низька S** (спокій, не неон) — десатурація, не luminance (A39 neon-S-урок; еволюція від B37 neon-тон-дауну `#152826`→B38 `#264a46`);
- **top-ридж `inset .26`** = emboss-світло на верхньому ребрі (несе об'єм), нижня грань `-.11`; drop `.15` — лише натяк.
- **Урок (device, Konst):** «lift 0 чи 100 — однаково» → elevation-через-drop на OLED НЕ працює; на темній lift несе ТОН. Якщо слабко у проді → підняти fill-L, **НЕ** elevation.

**Light drop — сила ∝ КОНТЕКСТ (generalizable):** та сама accent-fill, але blur/alpha drop масштабуються під фон-під-елементом:

|контекст|drop `0 3px 6px / 0 7px 18px` alpha|чому|
|---|---|---|
|чіп у світлій таці шіта|`.185 / .259`|світла таця тисне сильніше → гучніший lift|
|кнопка-фільтр на сторінці|`.14 / .196`|сторінка нейтральніша|
|чіп Tab-3 над recess-зоною|`.10 / .14`|найтихіший — близько до A65 recess-винятку|

→ **drop ∝ яскравість/тиск контексту** (таця > сторінка > recess). Один accent-fill — три сили drop.

**Border-owner — коли вибір І статус претендують на бордер (generalizable).** Елемент-чіп може нести і **статус** (колір-бордер `.ok/.warn/.late`), і **вибір** (accent-бордер `.act`). Конфлікт: хто володіє бордером? Резолюція (QR Tab-3):
- **вибір володіє бордером + fill + lift + accent-текстом**; **статус володіє dot-крапкою** (окремий елемент, JS).
- Реалізація — **специфічністю, не порядком:** `.qr-chips .qr-chip.act` (0,3,0 light / 0,4,0 dark) перебиває статус `.qr-chip.warn` (0,2,0) в ОБОХ темах. Раніше статус вигравав за source-order на світлій → вибір майже не видно. Підняти специфічність селектора вибору (контекст-префікс `.qr-chips`) > будь-який статус-клас.
- Анти: різати специфічність урівень (0,2,0=0,2,0) → виграє останній у файлі (крихко, тема-залежно). Дай вибору **вищу** специфічність явно.

**ПОРТ:** ✅ family **універсальна** (KPI Lens чіпи/фільтри, Drive Lens — будь-який select/toggle-стан). QR-hex `#dcefed`/`#264a46`/`#33ccbd`/`#8ae5dc` прив'язані до QR-accent → у іншому продукті взяти власний `accent-soft`/`accent-ink`/`accent`, ЗБЕРЕГТИ структуру тіней (light drop / dark tone-lift inset-ридж). **Зв'язок:** A39 (S-важіль + дрейф), A45 (тон-не-тінь база), A65 (recess-виняток), A70 (якщо елемент несе ще й opacity-кільце під рухом). *Source: `QR_Lens_preview_batch41_1.html` — `.chip.on` р.540/541, `.flt-btn.on` р.414/415, `.qr-chips .qr-chip.act` р.483/485 (+auto-dark близнюки). compare-locked → device✓ (Фаза 3, Konst).*

## A67. Press-механіка тапу: JS `pointerdown/up`, не чистий `:active`; down швидко / return пружно; scale∝1/розмір ✅

**Симптом.** Чистий `:active{transform:scale(.92)}` показує масштаб **лише поки палець тримає** → на швидкий тап (down+up за <100ms) око не встигає побачити стиск. Фідбек «є в CSS, але непомітний».

**Рішення — JS-керований клас `.pressing`** (стиск тримається через transition, навіть якщо палець уже відпустив):

```css
.qr-chip{transition:transform 280ms cubic-bezier(.34,1.5,.64,1)} /* return: довше + ПРУЖИНА; прибрати transition:all */
.qr-chip.pressing{transform:scale(.92);transition-duration:80ms}  /* down: ШВИДКО, лінійно */
```

```js
// Делегація на ПОСТІЙНИЙ контейнер (переживає innerHTML re-render списку чіпів — A54/14.13)
(function(){
  const row=document.getElementById('qr-chips-row'); if(!row||row._pressBound)return; row._pressBound=true;
  let cur=null; const rel=()=>{ if(cur){cur.classList.remove('pressing');cur=null;} };
  row.addEventListener('pointerdown',e=>{const c=e.target.closest('.qr-chip');if(!c)return;cur=c;c.classList.add('pressing');});
  row.addEventListener('pointerup',rel); row.addEventListener('pointercancel',rel); row.addEventListener('pointerleave',rel);
})();
```

**Канон-значення:** down **80ms** (лінійно) / return **280ms** + пружина `cubic-bezier(.34,1.5,.64,1)`.

**Магнітуда ∝ 1/розмір (обернено) + контекст-модифікатор.** Дрібний елемент стискається сильніше й пружинить різкіше; великий — м’якше (інакше великий «плескає»). **Контекст-модифікатор:** якщо елемент **перекривається** оверлеєм/тацею на час відгуку (sheet накриває чіп ~260ms), прес ще **глибший** — щоб жест зчитався крізь перекриття:

|елемент|scale|spring / жест|нота|
|---|---|---|---|
|**чіп ШІТА** (дрібний, у bottom-sheet)|`.84`|`280ms (.34,1.5,.64,1)`|**контекст-виняток:** менший + шіт накриває ~260ms → глибше за фільтр-чіп|
|**filter-button / reset** (кнопка на сторінці)|`.90`|`280ms (.34,1.5,.64,1)`|шіт може накривати reset → глибше за qr-chip|
|**чіп фільтр-ряду** (qr-chip, на сторінці)|`.92`|`280ms (.34,1.5,.64,1)`|базовий дрібний|
|**eq-card** (drill-картка, не select)|`.92`|WAAPI `1.07@70% / 800ms` spring|велика, але drill → магнітуда чіпа, не card-select|
|**велика капсула** (Drive Запис/Заправка)|`.95`|`1.3`|—|
|**ph-card** (велика картка SELECT)|`.96`|WAAPI `1.045@70% / 950ms` (A67.1)|найбільша → найм'якша + «один жест»|

down скрізь **80ms** лінійно. **`.84` — свідомий виняток** (не «помилка проти 1/розмір»): менші чіпи шіта + перекриття тацею вимагають гучнішого тактильного відгуку, ніж фільтр-чіпи на відкритій сторінці.

**Делегація, не per-element.** Якщо контейнер ре-рендериться (`innerHTML=…` щотапу, як `#qr-chips-row`) — per-chip listeners злітають при кожному рендері. Біндити ОДИН делегований listener на **постійний** контейнер (`_pressBound`-гард, wsd 10.2). `pointerleave` на контейнері знімає стиск при слайді пальця геть; `pointercancel` — при scroll-перехопленні (ряд чіпів горизонтально скролиться). Урок lifecycle-DOM — A54/14.13.
**Тригер:** будь-який тап-елемент, де треба тактильний стиск (чіпи, фільтр-кнопки, CTA-капсули).
**Анти:** чистий `:active{scale}` для швидкого тапу (непомітно); `transition:all` (тягне зайві проп); per-element listener на ре-рендер-контейнері (злітає); однаковий scale на чіп і велику капсулу (велика «плескає»).
**Зв’язок:** A56 (`.nav-i:active{scale(.96)}` — там OK, бо nav-кнопки постійні в DOM, не ре-рендеряться), A54 (постійний DOM для анімованих елементів), A8 (`.pressing` не конфліктує — окрема проп). *Source-of-truth: `QR_Lens_preview_batch31_3.html` — `.qr-chip`/`.pressing р.470`, делегований IIFE `р.1775–1777` (`#qr-chips-row`). ✅ device-confirmed (B30). **Phase-3 — РЕАЛІЗОВАНО → A67.1** (card-select на `.ph-card`; реальна device-locked магнітуда `scale .96` + WAAPI-overshoot, а НЕ передбачені `.98`).*

## A67.1. Card-select (велика картка): persistent-DOM + pseudo-opacity ring + WAAPI «один жест» ✅ (B32, device-locked)

**Що це.** Анім-вибір картки аптеки на Tab-2. Розширення A67 на **великий** елемент: той самий press-фундамент, але інша моторика — велика картка має інерцію, тож «характер»-жест повільніший і пружніший за чіп.

**Два press-патерни однієї теми, різне використання:**

|елемент|press|моторика|
|---|---|---|
|**чіп / дрібна кнопка** (A67)|короткий/різкий|down 80ms / return 280ms spring `(.34,1.5,.64,1)`, scale .92|
|**велика картка** (A67.1)|повільний інерційний «один жест»|depth → overshoot → settle ОДНИМ арком|

**Механіка (B32):**
1. **Persistent-DOM.** `renderPharmacies` має sig-guard `sig=[S.sr,S.fNet,S.fCity,S.fSt,S.phSrch]` (р.1082): якщо не змінився і картки є → змінився ЛИШЕ вибір → тогл `.sel` на живих вузлах (`data-idx`), **БЕЗ innerHTML-rebuild**. Rebuild лише на фільтр/пошук/ТП. Корінь усунення «снапу» (A54/14.13).
2. **Кільце = pseudo `::after` opacity** — `opacity 0→1` (composite, не paint/reflow). Border картки **константний 1px** (НЕ міняється на `.sel` → нуль зсуву); кільце несе `::after`. Фон+rank на `.sel`. **PAINT кільця змінено (B41, governance-sync 12.6):** було `box-shadow:inset 0 0 0 1.5px var(--accent)` → **тепер `border:1.5px solid var(--accent)`** на псевдо (`inset:0; box-sizing:border-box` → позиція 1:1). Opacity-reveal-механізм незмінний (140ms), АЛЕ box-shadow-кільце шимерило під banner-reveal layout-рухом (`.scroll-a` resize щокадру) → border shimmer-immune. **Деталі + чому layer-promote/outset/contain не лікують → A70.** *(batch41_1 р.434.)*
3. **Функц-фідбек = `--sel-dur:140ms`** `(.4,0,.2,1)` (р.86) — кільце+фон+rank синхронно, ШВИДКО.
4. **Press = делегований `pointerdown/up/cancel/leave` на постійний `#ph-list`** (р.1815–1817; переживає rebuild — A54). `pointerdown`→`.pressing` (depth scale .96 за `--press-down:80ms`, р.422); `pointerup`→зняти + `selectOutlet` + `playCardGesture`; `cancel/leave`→зняти (список вертикально скролиться → scroll-перехоплення НЕ обирає картку).
5. **«Характер» = WAAPI `playCardGesture`** (р.1805): `[.96@0 → 1.045@.7 → 1@1]`, **950ms** `cubic-bezier(.34,1.56,.64,1)`, `fill:none`. Не-блокуючий шар ПОВЕРХ швидкого функц-фідбеку (метафора піаніно — життя там, де палець; A57).
6. **reduced-motion** → `.ph-card`/`::after`/`.ph-rank` `transition:none` (р.443) + `reduceOn()`-гард у `playCardGesture` (жест не грає).

**Канон-значення (device-locked: compare v2.1 + B32-патч + 12-card scroll-test):**

|параметр|значення|
|---|---|
|глибина втиску|4% (scale .96)|
|швидкість втиску|80ms (`--press-down`)|
|висота вистрибу|+4.5% (1.045)|
|пік вистрибу|70%|
|тривалість жесту (РЕАЛЬНА)|950ms (slow-mo множника в проді НЕМА)|
|плавність жесту|Пружна `cubic-bezier(.34,1.56,.64,1)`|
|sel-dur (кільце+фон+rank)|140ms `(.4,0,.2,1)`|

**ПОРТ:** KPI Lens Tab-2 = **ті самі картки** → значення переносяться **НАПРЯМУ**. Drive Lens — **НЕ напряму**: інша поведінка (повний список що розгортається, інший розмір картки) → **патерн** портується, **цифри перетюнити** (інерція ∝ розмір). Принцип Konst: мати цифри готовими в каноні, не витягувати з еталона щоразу — лише підправити під елемент.

**Тригер:** великий тап-елемент зі станом вибору. **Анти:** rebuild innerHTML на вибір (вбиває жест — A54); кільце через border-зсув (reflow) чи box-shadow на самій картці (лагає за фоном — тому `::after`); два беати (модель B — на великій картці читається як смик); чіпова магнітуда на картці (.92 «плескає»). **Зв'язок:** A67 (база press), A54 (persistent-DOM), A57 («характер» поза драбиною), A65/A66 (фон-elevation `.sel`). *Source-of-truth: `QR_Lens_preview_batch32_1.html` — токени р.86, CSS р.419–443, `renderPharmacies` sig-guard р.1067–1086, `selectOutlet` р.1504, `playCardGesture` р.1805, делегований IIFE р.1815. ✅ device-confirmed B32 (вибір + скрол). **Ring-paint sync B41:** `::after` box-shadow→border у `batch41_1` р.434 (A70); device✓ B41.*

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

## A70. Кільце/обведення під layout-driven рухом: `border` > `box-shadow` (i inset, i outset) ✅

**Проблема.** Кільце-обведення обраного елемента (вибір / активний фільтр), намальоване через `box-shadow:inset 0 0 0 Npx` (або outset `0 0 0 Npx`), **шимерить / дрижить**, коли елемент рухається сабпікселем під layout-driven анімацією ПРЕДКА (не власним transform). Прецедент QR: банер-reveal анімує `height` 600ms → `.screens(flex:1)` стискається → `.scroll-a` ре-лейаутиться щокадру → картки + filter-row (живуть ВСЕРЕДИНІ `.scroll-a`) сунуться дробовим пікселем → `box-shadow`-кільце **ре-растеризується щокадру** = мерехтіння (+ відомий WebKit inset-shadow re-raster, баг #209930).

**Фікс — кільце через CSS-`border` на псевдоелементі:**
```css
*,*::before,*::after{box-sizing:border-box}        /* ОБОВ'ЯЗКОВО — border не зсуває позицію (= inset 1:1) */

.card::after{content:"";position:absolute;inset:0;border-radius:inherit;
  border:1.5px solid var(--accent);opacity:0;pointer-events:none;
  transition:opacity var(--sel-dur) var(--sel-ease)}   /* --sel-dur:140ms; --sel-ease:cubic-bezier(.4,0,.2,1) */
.card.sel::after{opacity:1}
```
`border` малюється як **частина боксу** (не окремий shadow-pass) → не ре-растеризується на сабпіксельному зсуві → чітке. При `box-sizing:border-box` позиція 1:1 з `inset box-shadow` (нуль візуального зсуву); миттєвість reveal зберігає `opacity` (composite-only, не paint).

**Що НЕ лікує (закрито device-тестом — wsd 14.18):**
- **layer-promote (`will-change:transform` / WAAPI-шар):** елемент уже на власному GPU-шарі через жест — `box-shadow` усе одно перемальовується (box-paint re-raster ≠ composite). Не лікує.
- **`outset`/`spread` замість `inset`:** ОБИДВА box-shadow-шляхи шимерять. Paper/research-ставка «inset-WebKit-баг → виправить outset» ПРОГРАЛА на device.
- **`contain:layout` на дитині:** не лікує resize ПРЕДКА-в'юпорта + де-оптимізує WebKit-композитинг (B40 device-регрес, відкат).

**Універсальне правило:** під layout-driven рухом предка анімувати/тримати чітким можна ЛИШЕ `opacity`/`transform`; будь-який `box-shadow` (inset|outset) на елементі, що сунеться сабпікселем — кандидат на шимер → виноси обведення в `border` псевдоелемента.

**Порт:** ✅ **універсальний** — будь-який select/active-ring у списку, що ре-лейаутиться при анімації сусіда/контейнера (KPI Lens картки-рядки, Drive Lens swipe-row). **НЕ** плутати з кільцем на статичному елементі (там inset box-shadow ок). **Зв'язок:** A67.1 (card-select — кільце тепер цим патерном), A45/A66 (elevation-мови сусідять), A57 (banner-reveal = джерело руху). *Source: `QR_Lens_preview_batch41_1.html` р.434 (`.ph-card::after`) + р.413 (`.flt-btn::after`); токени р.86; `box-sizing` р.129. Device✓ B41 (Konst: border не дрижить; inset/outset/+wc — шимерять). Компер-джерело: `QR_Lens_ring_compare_v1.html`.*

## A71. Row-stagger reveal — каскадна поява рядків (generic) ✅

**Що це.** Рядки/картки в шіті чи списку зʼявляються **каскадом** (кожен наступний — із затримкою), а не всі разом. Дешевий «преміум» при відкритті drill-шіта / зміні фільтра. Generic-функція, керована об'єктом-конфігом.

```js
function staggerRows(nodes,o){
  if(reduceOn()||!nodes||!nodes.length)return;                    // reduced-motion → миттєво, без каскаду
  nodes=[...nodes];
  const STEP=o.step,OFF=o.off||0,DUR=o.dur,DIST=o.dist,EASE=o.ease||'cubic-bezier(.32,.72,0,1)'; // decel за замовч.
  nodes.forEach(k=>{k.style.transition='none';k.style.opacity='0';k.style.transform='translateY('+DIST+'px)';});
  requestAnimationFrame(()=>requestAnimationFrame(()=>{           // double-rAF: ставимо hidden-стан ПЕРШ ніж анімувати (без flash 1-го кадру)
    nodes.forEach((k,i)=>{
      const d=OFF+i*STEP;                                         // per-node затримка
      k.style.transition='opacity '+DUR+'ms '+EASE+' '+d+'ms,transform '+DUR+'ms '+EASE+' '+d+'ms';
      k.style.opacity='1';k.style.transform='translateY(0)';
    });
    const total=OFF+(nodes.length-1)*STEP+DUR+50;
    setTimeout(()=>nodes.forEach(k=>{k.style.transition='';k.style.opacity='';k.style.transform='';}),total); // ПРИБРАТИ inline-стилі після (інакше липнуть → ламають подальші стани)
  }));
}
```

**Канон-конфіги (QR Phase 3, device✓):**
- drill-шіт рядки: `{step:120, off:160, dur:800, dist:10}` (повільніше, м'якше — змістовний контент);
- фільтр-шіт секції: `{step:90, off:0, dur:780, dist:16}` на `.sh-sec,.chip-row,.sh-reset` (трохи різкіше, більший зсув).

**Обов'язково:** (1) `reduceOn()`-гард (reduced-motion → миттєвий показ); (2) **double-rAF** (інакше перший кадр блисне у фінальному стані до hidden); (3) **cleanup inline-стилів** через `setTimeout(total)` — бо інакше `opacity/transform` залишаються інлайн і ламають наступні стани/теми елемента; (4) `OFF` = глобальна стартова затримка (синхрон зі слайдом шіта), `STEP` = крок між сусідами.

**Тригер:** відкриття шіта / зміна списку, де хочеться «жвавого» прибуття. **Анти:** stagger на КОЖЕН ре-рендер (дратує при частих оновленнях — лише на відкриття/значиму зміну); забути cleanup (липкі inline-стилі); забути reduceOn. **ПОРТ:** ✅ повністю generic — `nodes` + конфіг; KPI Lens (drill-таблиці), Drive Lens (списки записів). **Зв'язок:** A18.1 (open-слайд шіта — stagger стартує синхронно), A57 (decel-ease з мови руху), A27 (reduced-motion). *Source: `QR_Lens_preview_batch41_1.html` `staggerRows` р.1632, виклики р.1650 (фільтр) / р.1730 (drill-eq). device✓ B34.*

-----

-----

## A72. Scroll-linked анімація: РІВНІСТЬ вартості важливіша за її величину; rAF-демпфер замість транзиції ✅ (StockCheck §5-B, b17_2…b18, device-locked)

**Що це.** Клас патерну: властивість (transform, opacity, blur) керується позицією скролу — «острівець їде вгору», «хедер тане», «бар стискається». На iOS такі анімації **виглядають рвано навіть коли за цифрами все добре**. Цей пункт пояснює чому і дає робочу форму.

### Корінь: iOS коалесує scroll-івенти

Скрол на iOS живе **не на головному потоці**. Під час інерції (momentum) `scroll`-івенти приходять **пачками**, не по кадру, і `scrollTop` стрибає великими шматками. Тому сире scroll-linked значення (`p = scrollTop / Δ`) — це **сходинки**, а не безперервна величина. У повільному пальцевому скролі це майже не видно; в інерції — коле.

### 🔑 Знахідка №1: CSS-транзиція на scroll-linked властивості — ОДНОЧАСНО вартість і компенсатор

Типовий «баг», який хочеться прибрати: на властивість, яку JS пише **щокадру**, повішена `transition` → кожен кадр стартує нову транзицію. Виглядає як чиста марна робота.

**Але транзиція `opacity` виконується на композиторному потоці**, окремо від JS. Тобто вона паралельно працює як **згладжувач (low-pass фільтр)**: JS подає рвані значення — композитор домальовує між ними безперервну інтерполяцію.

> **Прибираючи транзицію «для швидкості», ти прибираєш згладжування.**
> Це не оптимізація, а **обмін**: дешевші кадри ↔ рвана картинка. Обмін мусить бути зважений на девайсі, а не вирішений з коду.

⚠️ Прецедент: StockCheck b17_3 — прибрали `transition:opacity 140ms` як «мертву». Прилад не показав **жодного** виграшу (викиди лишились), а користувач одразу зчитав регрес: «грубіше, дьоргано, різко». Діагноз був правильний, вирок — ні.

### 🔑 Знахідка №2: рівність вартості > величина вартості

Заміри `max frame-gap` (StockCheck, обидві теми):

| режим | темна | що відчувається |
|---|---|---|
| CSS-транзиція (згладжує лише opacity) | 21 · 27 ms, викиди до 38 | смикає |
| сире значення (без згладжування) | ~ те саме, викиди лишились | смикає сильніше |
| **rAF-демпфер** | **31 · 33 · 35 ms** (розкид 4) | **«як нативний застосунок»** |

Демпфер **дорожчий приблизно на 9 ms** — і при цьому виглядає незрівнянно плавніше.

> **Оптимізувати треба дисперсію, а не середнє.** Кадр, що стабільно коштує 33 ms, читається плавнішим за кадр, що коштує 24 ms із випадковими стрибками до 38. Око бачить **нерівність**, а не вартість.

Демпфер саме це й робить: **розмазує роботу рівно по кадрах** замість того, щоб віддавати її пачками разом із коалесованими scroll-івентами.

### Робоча форма (порт 1:1)

```js
var K=0.28;                       // частка залишку до цілі за кадр
var tgtP=0, curP=0, rafD=0;

function write(p){ /* єдина точка запису стилів */ }

function dampStep(){
  rafD=0;
  var d=tgtP-curP;
  if(Math.abs(d)<0.0015){ curP=tgtP; }          // сів → петля зупиняється
  else{ curP+=d*K; rafD=requestAnimationFrame(dampStep); }
  write(curP);
}
function onScrollFrame(){
  tgtP = clamp01(Math.max(0,SC.scrollTop)/DELTA);
  if(!rafD) rafD=requestAnimationFrame(dampStep);   // не плодити петель
}
```

**Обов'язкові умови:**
1. **Жодної CSS-транзиції** на властивостях, які пише демпфер — інакше подвійне згладжування і конфлікт.
2. **Одна петля.** `if(!rafD)` — інакше кожен scroll-івент плодить свій rAF.
3. **Петля мусить зупинятись** (поріг `|d| < 0.0015`), інакше вічний rAF їсть батарею.
4. **`resetDamp()` ПЕРЕД будь-яким `clearInline()`** (guard, reset, зміна екрана). Інакше петля в польоті перезапише щойно очищене вже наступним кадром.
5. `K` — device-lever, не константа з голови. 0.28 = StockCheck-lock; менше = масляніше й ліниво тягнеться за пальцем, більше = чіткіше й ближче до рваності.

### 🔑 Знахідка №3: стенд frame-gap НЕ міряє плавність

Вимірювач крутить скрол **програмно** (`sc.scrollTop = y` кожні 16 ms). Програмний скрол віддає івенти рівно й синхронно — **інерційної коалесенції там немає взагалі**. Тобто прилад фізично не може відтворити те, на що скаржиться око.

> **Розподіл ролей:** плавність арбітрує **око на живому пальцевому скролі**; прилад відповідає лише на питання **«скільки це коштує»**. Плутати їх — значить оптимізувати не ту величину (і саме так народився регрес b17_3).

⚠️ **Шумовий поріг.** Два прогони **однакового** конфігу дали 25 і 35 ms. Розкид приладу — до 10 ms. Мінімум **3 прогони на конфіг**; різницю менше ~10 ms сигналом не вважати. Дев-панель, що висить у DOM під час заміру, теж входить у цифру — фінальний замір робити на **чистому** білді.

**Зв'язок:** A70 (вибір властивості під layout-рухом) · A45/A66 (вартість матеріалу) · A55 (модель висоти) · wsd 2.4 (стенд/бенч/харнес) · wsd 1.5 (device = фінальний арбітр). *Source-of-truth: `StockCheck_port_b18.html` — `ISLC` (`K`/`FMUL`/`dampStep`/`resetDamp`). Стенд арбітражу: `StockCheck_port_b17_4.html` (сегмент `none/css/damp` + слайдери `k`/`fade mult`) — знято з продукту в b18.*

# Частина B — Продукт-специфічне 🆕🔒

> **НЕ універсальне.** Прив’язане до контексту конкретного продукту; частина — forward-специфікації (валідація на пристрої pending). Не переносити в інші Lens без окремого перегляду.

## B1. Drive Lens — read-write контекст (offline / sync)

> Привід: QR Lens read-only → offline = «дивимось локальне». Drive Lens read-write → offline = «записати зараз, синкнути пізніше». Статус: специфікація concept v1.2, **імплементація/валідація pending**.

- **Service Worker + offline queue** — install: cache static; fetch: cache-first static / network-first Supabase; sync event: flush черги (Background Sync де є). Register на `load`, `?v=batchN`. Listeners `online→syncPendingQueue()`, `offline→updateSyncIndicator`.
- **IndexedDB черга** (не localStorage: 5MB+синхронний блок) — stores `snapshots_queue` / `refuels_queue` / `days_cache`; запис `{...data, id:crypto.randomUUID(), created_at, sync_status:'pending'}`.
- **Sync indicator у app-bar** (4 стани): `synced`🟢(зникає 2с) / `syncing`🟡+live-dot(A30.4) / `pending`🟠 N у черзі / `offline`🔴(+pending). Тап → деталі черги (опц.).
- **Supabase realtime** (один user, кілька пристроїв) — `channel.on('postgres_changes',{event:'*',table,filter:user_id})`. Optimistic UI: queue→UI одразу→async POST→success: sync_status synced+видалити з черги; conflict→last-write-wins + toast.

## B2. VisualViewport — клавіатура в bottom sheet 🆕

Клавіатура перекриває CTA «Зберегти». Listener `visualViewport.resize`: якщо `initialHeight-vv.height>100` → `sheetBox.style.maxHeight=calc(vv.height px - 20px)` + `paddingBottom=20px` (override env — клавіатура замість home indicator). **Реєструвати лише при відкритті sheet з формою** (resize спрацьовує і на Safari toolbar).

## B3. Input attributes — форми 🔧+🆕

Базово (QR Lens, search): `type="search" autocomplete="off"`. Drive Lens числові форми:

|Поле    |Attributes (ключове)                                                               |
|--------|-----------------------------------------------------------------------------------|
|Одометр |`inputmode="decimal" pattern="[0-9]*\.?[0-9]*" enterkeyhint="next"`                |
|Запас км|`inputmode="numeric" pattern="[0-9]*"`                                             |
|Літри   |`inputmode="decimal" enterkeyhint="done"`                                          |
|Email   |`type="email" inputmode="email" autocomplete="email"`                              |
|OTP     |`inputmode="numeric" pattern="[0-9]{6}" autocomplete="one-time-code" maxlength="6"`|

`inputmode="decimal"` = numeric з крапкою; `pattern` = fallback старих iOS; `autocomplete="one-time-code"` = OTP з SMS.

**Focus-стан (Drive Lens, родоначальник).** Поле при фокусі піднімається — рамка-акцент + трохи світліший фон; пошук НАВМИСНО без рінга (втоплене well A51 уже несе афорданс «чіпай»):

```css
.inp:focus{outline:none;border-color:var(--border-accent);background:var(--surface-2)}
.sr-inp{outline:none}   /* пошук без focus-рінга — навмисно (well A51) */
```

**B3.1. `type="search"` малює власний нативний `::-webkit-search-cancel-button`** — видимий хрест у Chrome на ПК (на iOS Safari майже невидимий, тому легко прогледіти). При власній clear-кнопці виходить **два хрести**. Завжди глушити нативний, інакше дубль:

```css
.sr-inp::-webkit-search-cancel-button{display:none;-webkit-appearance:none}
```

Джерело: Drive Lens `.sr-inp` (родоначальник). Двічі вкусило при перенесенні clear-× у QR (batch23.1) і KPI (batch14.2) — обидва мали `type="search"` без глушіння. Глушити в тій же сесії, що й додаєш свій clear-×.

## B4. Numeric fuel gauge — 12 поділів 🆕 (Drive Lens)

Не `<input type="number">`, а візуальний `role="slider"` (12 ticks, кожен 3-й major), `.fg-fill` width%, tap/drag/arrow-keys, `aria-valuemin/max/now`. + опц. «Запас ходу» numeric input.

## B5. QR Lens — QR-код розмір + Tab-3 layout (Phase 3) 🆕 (QR Lens)

> Продукт-специфіка QR Lens; решта Phase 3 (active-family A66.1 · ring A70 · press A67 · banner/close-motion A57/A18.1 · row-stagger A71) — **універсальна, у Частині A**.

**QR-код width-responsive (`--qr-sz`).** Канвас QR генерується на МАКСИМУМ (290px) і масштабується **лише ВНИЗ** (down-scale чіткий, up-scale мильний):
```css
.qr-wrap canvas,.qr-wrap img{width:var(--qr-sz,260px);height:var(--qr-sz,260px)}
/* --qr-sz:clamp(200px, min(100vw*.7125, 100vh*.34), 290px) — лідер ШИРИНА */
```
**Урок (generalizable):** коли елемент масштабується per-device — (1) рендер на максимумі + scale DOWN (чіткість); (2) **обрати важіль, що реально керує перцепцією.** Тут важіль = **ШИРИНА**, не висота: 15 Pro (393pt) ширший за XS (375pt) → ті самі 260px читались дрібно на ширшому екрані. Device-pick: XS→267 / 15 Pro→280 (1:1 між собою). `#app≤430` обмежує верх.

**Tab-3 layout-fix — `space-between` на ОДНОМУ flex-дитині = no-op.** qr-area мала один child (`#qr-content`); `justify-content:space-between` з єдиним дитям нічого не розподіляє → елемент якориться ВГОРІ → на вищому 15 Pro (vh852) надлишок збирався порожнечею ВНИЗУ (між well↔чіпами). Фікс: **`center`** — ділить надлишок верх/низ симетрично. **Generalizable gotcha:** `space-between`/`space-around` з одним flex-дитям — no-op (топ-якір); для балансу надлишку при одному child → `center`. *Source: `batch41_1` qr-area / `--qr-sz` р.460. device-pick Konst (B38).*

-----

# Частина C — Чек-лист deploy (перед видачею колегам)

manifest валідний · 7 іконок · cache-bust `?v=` синк HTML(5)+manifest(3) · SW registered · FOUC inline ПЕРЕД CSS · theme auto/light/dark persist · `dvh` всюди · `env()` без зайвих px · bottom nav padding Safari+PWA · sheet: ×/swipe/backdrop · swipe-close grip40/content64+scrollTop · orientation lock landscape · input `font-size:16px` · pinch blocked · numeric inputmode/pattern · (Drive) keyboard handling · offline→pending→online→green · multi-device realtime · system theme live (iOS 18+) · storage event sync.

-----

**Кінець.** Будь-який пункт Частини A валідований на iPhone XS iOS 18 PWA через QR Lens production. Точний код — grep у `QR_Lens_preview_batch22.html` (стандарт) / `Drive_Lens_preview_batch10_2.html` (swipe-пігулка A22, sheet-анімація A18).