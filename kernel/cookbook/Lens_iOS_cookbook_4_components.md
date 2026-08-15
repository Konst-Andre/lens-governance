> живе доки: назавжди (вічне, wsd 1.8) · читається ТОЧКОВО за індексом
> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)

# Lens — iOS / PWA Cookbook · Том 4 — Компоненти й контроли

> **Тригер тому.** треба конкретний контрол: селект, тогл, чіп, плитка, тост, нативне поле
>
> **Маршрутизатор — `Lens_cookbook_INDEX.md`**: задача → запис → том, і мапа номер → том.
> Загальний контекст (джерело коду, тестова база, маркування ✅ / 🔧 / 🆕🔒) живе там і **тут не дублюється**.
>
> **Записи тому (16):** A6, A26, A29, A30, A32, A36, A37, A38, A40, A41, A47, A49, A52, A53, A59, A64
>
> **Зовнішні залежності.** A6 доповнює тема-інфраструктуру **A5/A7/A8** (том 1) · press-механіка контролів — **A67** (том 5)
>
> **Нумерація наскрізна для всіх томів** — A-номери не змінювались при розпилі. Діапазони розривні; адресує індекс, не діапазон.

-----

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

## A26. A11y attributes

Theme dropdown: `aria-label/aria-haspopup/aria-expanded`, `role="menu"`+`role="menuitemradio"`, dynamic `aria-label='Тема: '+lbl` (VoiceOver читає стан). Іконкові nav-кнопки: `aria-label` («Попередній день» тощо).

## A29. SVG icons — inline + стандартні розміри

Усі inline (не icon-font): `stroke="currentColor"`, `fill="none"`, `stroke-width` 2/1.8/2.5, `linecap/linejoin="round"`. Розміри: chevron 12; menu/search/filter 14; theme/close 16; nav tabs 20; nav arrows 18; empty state 34.

## A30. Premium polish

1. **Scroll-fade краї chips:** `mask-image:linear-gradient(to right,transparent,#000 20px,#000 calc(100% - 20px),transparent)` + `scrollbar-width:none`.
1. **Status-tint фон:** `background:linear-gradient(180deg,var(--card),color-mix(in srgb,var(--warn) 6%,var(--card)))` (Safari ≥16.2).
1. **Micro tap:** `:active{ transform:scale(.97) }` — лише на ключових CTA.
1. **Live pulse:** `@keyframes livePulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.75)}}` (sync/live dot).

## A32. Empty state

`.empty-state{ min-height:55dvh; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px }` (vertical centering на будь-якому vh) + `.empty-ico` коло 76px + текст/підказка + `.goto-btn` (accent CTA).

## A36. `[hidden]` vs явний `display` — атрибут програє класу ✅

**Симптом.** `el.hidden=true` не ховає елемент, хоча в JS усе виглядає правильно.

**Корінь (не вгадувати).** UA-стиль `[hidden]{display:none}` має специфічність (0,1,0). Якщо у автора є `.X{display:flex}` (чи grid/block) — теж (0,1,0), РІВНА → перемагає **пізніший у коді** = авторський `.X{display:flex}`. Атрибут `hidden` мовчки ігнорується.

**Рішення:** підняти специфічність приховування під клас:

```css
.X[hidden]{display:none}   /* (0,2,0) > (0,1,0) */
```

**Grep-перевірка:** для кожного `.hidden=` / `hidden=` у JS — чи цільовий клас має явний `display`? Якщо так → потрібен `.X[hidden]{display:none}`.

**Прецедент:** Drive Lens Batch 15 — `filter-row{display:flex}` не давав `setTab` сховати панель на Паливі/Місяці (намір був, баг тихий). Споріднено з **A8** (theme-override specificity guard) — той самий клас «рівна специфічність б’є намір».

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

> **Прецедент:** Drive Lens B19 — #2 (color-scheme для native календаря) закрито як обмеження iOS, не наш дефект.

## A47. Стат-плитки (3 у ряд): іконка + значення + підпис ✅

Грид `repeat(3,1fr)`, кожна плитка — вертикальний стек: **іконка** (24px, по центру) / **значення** (`tabular-nums`) / **підпис** (`--text-muted`).

**Колір тинту = за змістом (A35), НЕ світлофор:** усі плитки одного семантичного блоку — один тон (паливо → синій `--info`), не «зелена/жовта/червона» розкладка. Об’єм — через A45 (градієнт + inset-грані, спліт по темах).

**Значення** підкручене до тинту: `color-mix(in srgb, var(--info) 60%, var(--text-primary))` на світлій, `80%` на темній (темна потребує більше тинту, щоб синій читався).

**Прецедент:** Drive Lens Tab-3 «Гроші» (Batch 26).

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

## A86. Індикатор запасу не має права показувати нуль, коли ресурс є ✅

**Тригер.** У UI з'явився бар/шкала/відсоток, що показує заповнення ресурсу
(сховище, квота, ліміт), і знаменник великий відносно типового кроку.

**Дія — два обов'язкові гарди.**

```js
/* 1 · мінімальна видима комірка */
if (used > 0 && pct < 1) pct = 1;

/* 2 · підпис називає ФАКТ, а не лише відсоток */
if (!count) { sub.textContent = 'Даних нема · сховище ' + (used/1024).toFixed(1) + ' КБ'; return; }
sub.textContent = count + ' ' + plural(count) + ' · ще ~' + left;
```

**Чому.** `Math.round(used/CAP*100)` при `CAP = 5 МБ` віддає `0%` на всьому діапазоні
до **~25 КБ**. Якщо одиниця обліку важить ~2 КБ, то дюжина реальних записів малює
**порожній бар**. Порожній бар читається не як «мало», а як «нема» або «зламано» —
і саме так читається у полі, де консолі немає й перевірити нічим.

**Одиниця підпису — та, якою оператор мислить**, не та, в якій міряє машина.
«340 КБ» не відповідає на жодне його питання; «12 візитів · ще ~2600» відповідає
на обидва — скільки зібрано і скільки ще влізе.

**Анти-приклад.** StockCheck b32.5: підпис `0% · ще ~2700 візитів` показувався
однаково і при порожньому сховищі, і при живому з десятком візитів. Формально
правдивий рядок, практично — дезінформація в обох напрямках.

**Детектор (К2).** Регекс на наявність рядка тут недостатній: дефект живе в
ПОВЕДІНЦІ, не в тексті. Функція витягується з файлу і виконується в пісочниці з
підставленими джерелами (`storeBytes`/`visitCount`), судиться те, що побачить око —
ширина заливки і текст підпису. Зразок: `StockCheck_b32_6_s20_smoke.js` §N2, де
`run(24*1024, 12).w === '1%'` падає на старій базі й проходить на новій.

-----
