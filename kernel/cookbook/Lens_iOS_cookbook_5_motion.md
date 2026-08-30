> живе доки: назавжди (вічне, wsd 1.8) · читається ТОЧКОВО за індексом
> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)

# Lens — iOS / PWA Cookbook · Том 5 — Рух і жест

> **Тригер тому.** воно рухається не так · жест б'ється зі скролом · тап не відчувається · джанк на девайсі
>
> **Маршрутизатор — `Lens_cookbook_INDEX.md`**: задача → запис → том, і мапа номер → том.
> Загальний контекст (джерело коду, тестова база, маркування ✅ / 🔧 / 🆕🔒) живе там і **тут не дублюється**.
>
> **Записи тому (9):** A44, A54, A57, A67, A67.1, A70, A71, A72, A73
>
> **Зовнішні залежності.** A57 — звід над **A18** (том 2), **A27** (том 1), A54/A56 · A67.1 = база **A67** + **A54** (тут же) · A72 = база **A70** (тут же) + **A45** (том 3)
>
> **Нумерація наскрізна для всіх томів** — A-номери не змінювались при розпилі. Діапазони розривні; адресує індекс, не діапазон.

-----

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

-----

## A73. Хіт-експандер: тач-таргет ⟂ візуальна плашка ✅

> Родина жесту: **A67 / A67.1** (press-механіка, цей же том) — A73 відповідає за *межі* тач-таргета, A67 — за *реакцію* на тап.

**Статус:** StockCheck b22_2 — device-verified (іконо-дії хедера, шеврон+кебаб).
**Дім у Cookbook:** поруч із A67 (press-механіка тапу) — та сама тема «палець vs елемент».

### Проблема

Плитована іконо-дія виглядає добре на 34–38px, але Apple HIG вимагає **44pt** тач-таргету.
Звичний хід — збільшити плашку до 44 — ламає композицію: кнопка стає гладкою й важкою,
перетягує вагу з контенту. Компроміс «або гарно, або зручно».

### Патерн

Це **дві незалежні величини**, і їх треба задавати окремо: плашку малюєш такою,
як добре виглядає; зону ловлі невидимо добираєш псевдоелементом.

```css
:root{ --icoBtn:38px; --icoRad:11px; }

.icon-btn{
  position:relative;                       /* обов'язково — якір для ::after */
  width:var(--icoBtn); height:var(--icoBtn);
  border-radius:var(--icoRad);
}
/* невидимо добирає зону до 44pt; від'ємний inset = розширення назовні */
.icon-btn::after{
  content:"";
  position:absolute;
  inset:calc((var(--icoBtn) - 44px) / 2);
}
```

Ключове — **`calc` від власної змінної**, а не зашите друге число.
Крутиш `--icoBtn` — зона підлаштовується сама. Другого значення в голові тримати не треба,
і немає класичного багу «змінив розмір, забув оновити хітбокс».

### Обмеження й пастки

| # | Правило | Чому |
|---|---------|------|
| 1 | **`--icoBtn` ≤ 44px** | при >44 `inset` стає **додатним** і зону **звужує** — патерн працює навиворіт |
| 2 | `position:relative` на плашці | без нього `::after` якориться не туди |
| 3 | `gap` між сусідніми кнопками ≥ 2×\|inset\| | інакше розширені зони **перекриваються**, край однієї краде тапи в іншої. При 38px: inset = −3px → потрібен gap ≥ 6px |
| 4 | `::after` на цій кнопці має бути **вільний** | якщо він уже зайнятий під кільце/бордер (A70) — брати `::before` або окремий шар |
| 5 | Зона невидима, але **клікабельна** — не ставити всередину `pointer-events:none` | інакше сенсу нема |

### Де застосувати далі

Плитовані іконо-дії того ж класу є у **QR Lens** і **Drive Lens** — та сама проблема
прийде туди. Патерн переносний як є, змінюється лише ім'я токена.

### Джерело

`StockCheck_session_summary_b22_anchoredTile.md` §РІШЕННЯ ·
`StockCheck_port_b22_2.html` р.34–36, 141–147.

-----

## A82. Handoff-sweep — нагорода моменту «ПЕРЕДАНО», не «завершено» ✅

**Задача.** Дія, що **віддає вміст назовні** (копіювання в буфер, експорт, шер), не має
природного візуального відгуку: буфер обміну невидимий. Потрібен знак «пішло», який
не бреше і не коштує кадрів.

**Семантичне розрізнення, з якого все випливає.** «Завершено» і «передано» — **різні події**,
і плутати їх дорого. Завершення (заповнив усе) уже нагороджене раніше й по-своєму;
момент 📋 нагороджує **передачу**. Тому форма руху мусить кодувати **напрям**, а не стан.

**Механіка.** Дочірній шар усередині кнопки (`position:relative;overflow:hidden` на кнопці),
смуга проходить `translateX(-160%) → translateX(400%)` з нахилом і плавним входом/виходом
за непрозорістю. Тільки `transform` + `opacity` → composite-only, без repaint.

**Device-locked значення** (StockCheck b27, обидві теми, iPhone XS + 15 Pro):
```
--swDur   1400ms      ← БАЛАНС, не «повільно»: коротші (≈650) око не встигає зареєструвати
--swW     40 (%)
--swOp    55          ← однаковий в обох темах → БЕЗ theme-split (рідкісний випадок, A39)
--swSkew  -14 (deg)
easing    cubic-bezier(.32,.72,0,1)
keyframes 0% op0 · 12% op1 · 88% op1 · 100% op0
```

**Чому смуга, а не border-beam** (три незалежні причини — жодна сама не вирішальна):
1. **напрям кодує сенс** — смуга виходить за край = вектор «звідси туди»; замкнена петля
   кодує «об'єкт активний», а не «вміст пішов»;
2. **вартість кадру** — смуга composite-only; периметральна петля = per-frame repaint по рамці (A70/A72);
3. **трендовий маркер** — border beam у 2025–26 читається як підпис «AI-інтерфейс»,
   той самий клас ризику, що й лівий accent-rail (wsd 2.4).

**Три гарди — кожен закриває свій відмовний режим:**

| гард | що ловить | що буде без нього |
|---|---|---|
| `reduce-motion` перевірка **в JS**, не лише в `@media` | системне налаштування | клас навішується, анімація глушиться CSS — але стан лишається брудним |
| `dataset.sweeping` | подвійний тап | другий запуск накладається на недограний прохід |
| **запуск лише на УСПІХ** (`.then` + успішна гілка фолбеку) | відмову clipboard | смуга «значення пішли» зіграла, а буфер порожній — **інтерфейс збрехав саме там, де людина йде в Excel** |

Третій гард — головний. Нагорода, що грає незалежно від результату, гірша за відсутність нагороди:
вона перетворює зворотний зв'язок на декорацію.

**Іменування.** Усі класи префіксовані (`.cta-lbl`, `.cta-sweep`, `@keyframes swGo`) —
зворотний аудит проти попереднього білда дав 0 збігів на кожен. **`.cta-lbl` обов'язковий:**
голий текстовий вузол не має власного z-index і пішов би **під** смугу.

**Детектор (К2).** Сторож у jsdom-матриці валиться, якщо в продукті з'являються голі
`.lbl{` / `.sweep{`. ⚠ Регекс сторожа має ловити **тільки** голе оголошення: перша редакція
ловила й легітимне `.btn-copy.sweeping .cta-sweep{` і давала хибний ✗.

**Код:** `fireSweep()` у `StockCheck_port_b28.html`; матриця `StockCheck_b27_jsdom_matrix.js`
(34 твердження, сторожі S/T/Q/R).

**Пов'язане:** A70 (композит під рухом) · A67 (press) · wsd 2.4 (анти-патерн декоративного акценту).

---

## A83. View Transitions API — перший кандидат для mode-switch, не ручний FLIP ✅

> *Перенесено з `Work_Standard.md` 2.4 (13.08.2026, прополка v2.29): це патерн реалізації,
> а не протокол роботи, тому дім — Cookbook.*

**Задача.** Перехід між двома DOM-станами **виду** (close/open, зміна режиму, перебудова
списку). Ручний slide/fade припускає **стабільний destination** — і ламається рівно тоді,
коли разом із рухом міняється контент, текстура або кількість рядків.

**Механіка.** `document.startViewTransition(cb)` — браузер знімає old-стан, виконує колбек,
знімає new-стан і кросфейдить **увесь diff як ОДНУ скоординовану зміну**. Same-document VT —
Baseline, Safari 18+.

**Чому першим кандидатом.** Ручний FLIP вимагає перелічити, що саме рухається; VT не вимагає —
він працює з різницею, а не зі списком елементів. Усе, що ти забув перелічити, у FLIP
з'являється стрибком, а у VT кросфейдиться разом з рештою.

**Гард-набір — обов'язковий при застосуванні:**
1. **feature-detect** `document.startViewTransition` + фолбек на снап/instant;
2. **reduced-motion — ВРУЧНУ** (`matchMedia('(prefers-reduced-motion:reduce)')`): браузер
   сам VT **не пропускає**;
3. **колбек швидкий і синхронний** — важкий sync DOM морозить знімок;
4. якщо на сторінці вже є інший VT (напр. перефарб теми) — **розпаралелити** через
   `[data-vt="…"]`-scope на `:root` (специфічність 0,1,0 перебиває голі
   `::view-transition-*(root)` 0,0,0) або через VT-types. Інакше другий VT підхопить
   чужу `@keyframes`.

**Семантика per-context ≠ непослідовність:** slide = same-context reclaim,
VT-crossfade = context switch. Один продукт може мати обидва — вони кодують різні події.

*Прецедент 14.20: QR Lens B47, close Tab-1/3/4.*
**Пов'язане:** A57 (тривалість ⟂ крива) · A18.1 · A70 (композит під рухом).
