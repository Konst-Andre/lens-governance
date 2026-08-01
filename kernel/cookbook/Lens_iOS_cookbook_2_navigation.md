> живе доки: назавжди (вічне, wsd 1.8) · читається ТОЧКОВО за індексом
> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)

# Lens — iOS / PWA Cookbook · Том 2 — Навігація, оверлеї, пікери

> **Тригер тому.** будую навігацію, bottom sheet, свайп рядка або календар/пікер у шіті
>
> **Маршрутизатор — `Lens_cookbook_INDEX.md`**: задача → запис → том, і мапа номер → том.
> Загальний контекст (джерело коду, тестова база, маркування ✅ / 🔧 / 🆕🔒) живе там і **тут не дублюється**.
>
> **Записи тому (14):** A15, A16, A17, A18, A19, A20, A21, A22, A33, A50, A56, A58, A60, A61
>
> **Зовнішні залежності.** A56 = база **A54** (том 5) + **A55** (том 1) · A18 підпорядкований драбині тривалостей **A57** (том 5) · A44 (axis-lock жесту) → том 5
>
> **Нумерація наскрізна для всіх томів** — A-номери не змінювались при розпилі. Діапазони розривні; адресує індекс, не діапазон.

-----

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

## A50. Range-календар: in-sheet drill день↔місяць (calMY-свап) + антистрибок + каретка-мова ✅

**Задача.** Дати швидкий «стрибок» по місяцях усередині range-календаря (A33) без окремого пікера — і назад, без закриття шіта.

**Свап у ТОМУ Ж шіті (B28).** Тап по пілюлі-лейблу `calMY` (`◂назва місяця▸`, хедер денної в’юшки) → ховаємо `calDayView`, показуємо `calMonView` (сітка місяців 3×4, реюз `.mg-*` CSS A33). Драйвить `calView` (стан range-календаря), **НЕ** `S.monthView` Tab-4. ❗ Окремі id `calMg*` (`calMgY`, `calMgGrid`…), щоб не зіткнутись із `mgGrid`/`mgYear` Tab-4 — **ізоляція стану (14.10)**. Вибір клітинки місяця → `calView={y,m}` + `showCalDays()` + `renderCal()` (перехід). Floor-guard: місяці до 1-го запису `disabled`; рік-стрілка `prev` гасне на `dataFloor().y`, вперед — без межі (як A33).

**Антистрибок висоти (B29).** При свапі `calMonView.minHeight = calDayView.offsetHeight` (місячна сітка нижча за денну з її підказкою+Сьогодні+футером). Інакше шіт «худне» при день→місяць і «товстіє» назад — стрибок. На `showCalDays()` пін скидати (`minHeight=''`). **Наслідок-урок:** пінена свап-в’юшка успадковує whitespace найвищої — порожнечу під сіткою вирішувати **свідомо** (лишити дихання / центрувати layout-ом / заробити контентом). Drive Lens обрав «зверху, дихає»; filler заради простору відкинуто (= капкан, як зайве поле/риска).

**Назад до днів + каретка-мова (B29.1).** Несиметрія до фіксу: з денної є афорданс ПІТИ на місяці (тап `calMY`), а назад — лише `×` або вибір місяця. Фікс: **рік-пігулка `calMgY` тапабельна** → `showCalDays()` (повертає на той самий місяць, `calView` без змін, нічого не обрано — чистий «передумав»). Гард `_swiped` (тап≠свайп року; див. доповнення A44). **Одна каретка-мова на обох пілюлях:** ▾ на `calMY` (дні → «розкрити в місяці»), ▴ на `calMgY` (місяці → «згорнути в дні») — ідіома Apple Calendar, каретка вказує напрям drill. Реалізація: число у дочірній `.pill-v` span + каретка-сусід (inline SVG-chevron), бо пілюлі оновлюються через `.textContent` (стер би дочірній вузол). Каретка `--text-muted` (читається, не кричить). ❗ Каретку/тап-назад — **лише до пілюль range-календаря (id-скоуп)**, НЕ до спільного `.mg-y` (Tab-4 `mgYear` без днів → без каретки).

**Крос-реф.** База — A33 (tap-based range grid). **Спільне місяць-ядро (3×4 grid + floor-guard + рік-пігулка) промоутнуто в → A60** — тут лишається ЛИШЕ range-специфіка (calMY-свап день↔місяць, антистрибок, каретка-мова). Свайп року/днів — A44. Sheet-close співжиття — A19/A44. Ізоляція станів — wsd 14.10. *Device-validated повністю (B28→B29.1).*

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
