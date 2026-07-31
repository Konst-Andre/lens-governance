> живе доки: назавжди (вічне, wsd 1.8) — канон Фармастор v2, попередника StockCheck

# Фармастор Залишки v2 — MASTER LOCK
> **Єдине джерело правди.** Для цих пунктів переважає над розкиданими самері. При побудові harness / порту — токени й рішення беруться ЗВІДСИ.
> Маркери: **✓ LOCKED** (рішення прийнято) · **? OPEN** (потрібне рішення/harness/device) · *rationale* (обґрунтування, не лок).
> Провенанс: grep-verified зі STEP-локів, самері, `multibrand_harness_v1` (device✓), per-секційні harness-файли. **Актуально 20.07.2026.** Останній canon-merge **b13/b14** (20.07): §5.1 верхівка + Δ-колір(модель B) · §5.2 перенесена-ринг + Home-бейдж «Історія» · §5.4 status-фільтр · §6.5 — усі **device✓ в продукті**, злиті в канон. Ранні upd-нотатки згорнуто (git/самері). Активні хвости → §11.

---

## §0 · ПОЗИЦІЮВАННЯ ✓
- **НЕ Lens-сім'я.** Самостійний, **мережа-агностичний** функц. інструмент збору залишків по SKU в онлайн-Excel. Простіший/легший підхід, та ж якість (дизайн+логіка).
- **НЕ тягнути Lens-брендинг:** dot-логотип, Slate-Teal, family chrome — заборонено.
- **Власний колір продукту, НЕ колір мережі** (Konst, явно): мереж буде багато, у кожної свій колір → підлаштовуватись під мережу = перефарбовувати щоразу. Бренд мережі (лого/назва) = окремий **конфіг-шар**, якщо колись треба (§8).
- iOS/PWA-патерни з Lens-практики лишаються (це якість, не брендинг) → §7.

---

## §1 · ДАТА-МОДЕЛЬ ✓
- **Зберігання за kode** (не за позицією): `ST.phs[phId][kode]=val`.
- **Стовпчик = ітерація MSL у порядку майстра**, значення по kode: `MSL.forEach(s=> …d[s.k]…)` (v1.3 р.587).
- **3 стани комірки + ghost:**

| Стан | Умова | Поле | Рядок |
|---|---|---|---|
| не торкався | kode **absent** | ghost-норма (блідо, opacity .34) | активний |
| ввів >0 | present, val>0 | суцільне число | заспокоєний (бліднішає/✓) |
| ввів явний 0 | present, val=0 | суцільний «0» = ДАНІ | заспокоєний |

- **Стейт-модель v2** (ключ `farmstore_v2`) — **історія знімків per-аптека:**
```js
{ ver:2, phs:{ [phId]:{ visits:[
  { date:'YYYY-MM-DD', vals:{[kode]:number}, tier:{oTC:'B', iW:'C'}, transferred:false }
] } } }
// vals: absent = не торкався · 0 = явний нуль (absent≠0 діє і всередині знімків)
// tier = тір-профіль НА МОМЕНТ візиту (стара норма не бреше, якщо тір аптеки зміниться)
```
- **Життя знімка ✓ (A1 · snapshot-on-copy):** поточний рахунок = останній visit за сьогодні (`transferred:false`); **📋 Копіювати → `transferred=true`** (дубль-копія того ж дня = перезапис знімка, НЕ 2-й візит); новий день у FILL → push `{date:today, vals:{}, tier, transferred:false}`. Порахував і не скопіював → знімок лишається un-transferred (незавершений — чесно).
- **Порівняння (§5.1) споживає `transferred` знімки.** Абандонні un-transferred — з маркером (деталь, не блокер порту).
- **Міграція v1→v2** (одноразово): обгорнути кожен phId → `{visits:[{date:<стара глоб. date|today>, vals:<стара kode-мапа>, tier:<поточний>, transferred:false}]}`; **історію НЕ бекфілимо** (старт чисто); `farmstore_v1` недоторканий (rollback-safe).

---

## §2 · 83 НАЗВИ ✓ (+ reorder)
- **Канонічне джерело назв:** `Farmastor_multibrand_harness_v1.html` DATA-блок (device✓, фіналізовано). НЕ дублюю 83 рядки тут — щоб уникнути розсинхрону; беру звідти при порті.
- 6 брендів: Стрепсілс · Нурофен · Гавіскон (OTC) · Durex · Contex · Evitest/Eviplan (IW).
- **Нурофен reorder** ✓: таблетки/капсули 13 · **супозиторії 7 nested під Суспензія** (зміна проти STEP1 13/6/1).
- **getSubGroup детектори** — LOCKED (nested під-групи, sticky eyebrow).
- ⚠️ **getBrand — має баг** (див. §8), STEP1-«не чіпати» скасовано цим.

---

## §3 · NORM-RESOLVER ✓ (найважливіша логіка)
- Норма SKU **залежить від тіру аптеки**, окремо для OTC і IW.
- Резолвер: `SKU.Category (OTC|IW)` → обрати тір аптеки для цієї категорії (`pharmacy.oTC` | `pharmacy.iW`, літера A/B/C/D) → колонка `MSL[літера]` = **норма**.
  - OTC-товари (Стрепсілс·Нурофен·Гавіскон) → `pharmacy.oTC`.
  - IW-товари (Durex·Contex·Evitest) → `pharmacy.iW`.
- MSL-структура майстра: `SKY | Category | A | B | C | D | Kode | Price` (83 SKU, `Фармастор_замовлення_тт.xlsx`).
- *rationale:* у harness норма показувалась колонкою A плоско (демо) — у проді ghost-норма й δ-чіп **різні для кожної аптеки**. **У порт нести ЛИШЕ назви, НЕ A-норми як істину.**
- **Наслідок-лок:** картка аптеки **явно несе тір-профіль** (напр. `OTC B · IW C`) — бо він міняє всю сітку норм.

---

## §4 · COPY-КОНТРАКТ + EXCEL DEEP-LINK ✓ (замість bulk-export)

### 4.1 Copy (головна дія) ✓
- Головна дія картки аптеки = **Копіювати** (83 значення, master-order, by-kode):
```js
MSL.map(s => (d[s.k]!==undefined ? d[s.k] : '')).join('
')
// пропуск = порожній рядок (не затирає чуже нулем); незалежно від reorder відображення
```
- Дуальний якір на картці: **→ M{X} · Proxima {ID}** (напр. `M168 · Proxima 102520`) — sort-robust фолбек.
- Тост після копії: «✓ Скопійовано 83 → встав у M168 · Proxima {ID}».
- *Воркфлоу:* переносити ОДРАЗУ після кожної аптеки (мін. вікно «дані у двох місцях»).
- copy-on → `visit.transferred=true` + saveST (снапшот A1, §1).

### 4.2 Excel deep-link ✓ LOCK (b10 — розширення copy-контракту)
- **Суть:** лінк на онлайн-форму замовлення (SharePoint Excel) — копі→вставка без походу в Telegram. Звужує §4-вікно «дані у двох місцях».
- **Розміщення (ОБИДВА):**
  - **(a) FILL, всередині картки** — post-copy вставка, головний шлях. Поруч із копі-кнопкою, **layout 2.5:1** (копі:Excel).
  - **(b) Home ••• меню** рядком — утиліта «просто відкрити» + масштабований дім для N-лінків (майбутнє: група A58 eyebrow «ФОРМИ»).
- **Лейбл LOCK = «Excel»** (не «Форма»): конкретне, само-пояснює двокрок `Копіювати→Excel`. Гліф — external-link SVG (box-arrow, **mono, currentColor** — не емодзі).
- **Механіка (техн.):** `<a href=ORDER_FORM_URL target="_blank" rel="noopener">` — **НЕ `window.open()`** (Universal Links надійніше на живому anchor-тапі: домен sharepoint прописаний за Excel-app на OS-рівні → відкриває Excel як із Telegram). URL = єдиний `const ORDER_FORM_URL`; усі лінки читають його (`.js-order-link`, href ставиться в init). Clipboard переживає app-switch (системний буфер) ✓.
  - **DEVICE-TEST pending:** UL-стрибок PWA→зовні (рідкісний кейс). Якщо UL не спрацює на конкретному пристрої — фолбек лишається браузерна вкладка з формою (не блокер).
- **МАЙБУТНЄ (deferred):** N-лінків → меню-група (A58 eyebrow «ФОРМИ»); URL per-network у даних; свайп-по-картці — не треба поки один лінк.

**`ORDER_FORM_URL` (дослівно):**
```
https://rbcom-my.sharepoint.com/:x:/r/personal/yuliia_syniuhina_reckitt_com/_layouts/15/Doc.aspx?sourcedoc=%7B361AB6BF-2AE9-410C-A81F-2AA3502C4EAD%7D&file=%25u0424%25u0430%25u0440%25u043c%25u0430%25u0441%25u0442%25u043e%25u0440%20%25u0437%25u0430%25u043c%25u043e%25u0432%25u043b%25u0435%25u043d%25u043d%25u044f%20%25u0442%25u0442.xlsx&wdLOR=c06833412-A6C7-4B15-AE95-76BCF4AB9FD6&openShare=true&fromShare=true&action=default&mobileredirect=true
```

### 4.3 MATERIAL LOCK — FILL копі + Excel CTA ✓ (device✓ Konst XS+Pro, b11)
> Форма-стиль = **soft**. Layout = **поруч 2.5:1**. Розв'язано material-bench v2 (A45-манифест: РІЗНІ набори важелів per-theme). Порт-готові CSS @ locked values.

**LIGHT · копі (`.btn-copy`):**
```css
background:linear-gradient(180deg,color-mix(in srgb,#fff 16%,var(--accent)),var(--accent));
box-shadow:0 3px 10px -3px color-mix(in srgb,var(--accent) 27%,transparent),0 1px 2px rgba(20,50,42,.14);
color:#fff;
```
**LIGHT · форма soft (`.btn-form`):**
```css
background:color-mix(in srgb,var(--accent) 9%,#fff);
border:1.5px solid color-mix(in srgb,var(--accent) 20%,transparent);
color:color-mix(in srgb,var(--accent-ink) 63%,var(--accent));
box-shadow:0 1.5px 4px -2px rgba(20,50,42,.10);
```
**DARK · копі (`[data-theme=dark] .btn-copy`)** — власна насичена зелень, **НЕ `--accent` токен** (токен приглушений заради тексту → як велика заливка washed «салатовий»; A45-манифест rule 1/3):
```css
background:linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%));
box-shadow:inset 0 1px 0 rgba(255,255,255,.10);
color:#fff;
```
**DARK · форма soft (`[data-theme=dark] .btn-form`):**
```css
background:color-mix(in srgb,var(--accent) 18%,var(--surface-3));
border:1px solid color-mix(in srgb,var(--accent) 26%,var(--border));
color:color-mix(in srgb,var(--accent-ink) 58%,var(--accent));
box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
```
- **Провенанс dark-копі:** Konst device-pick `hsl(163 55% 30%)` — S=55 тримає густоту без OLED-неону, L=30 дає тіло. Баланс «не приглушено / не кричить». `.btn-copy{color:#fff}` — контраст ок на L=30.
- **Press (A67):** `.btn-copy.is-pressed,.btn-form.is-pressed{transform:scale(.96);transition-duration:.06s}` (велика капсула → м'яка магнітуда).
- **A69-паритет:** обидва dark-правила мірорити в `@media(prefers-color-scheme:dark){:root:not([data-theme="light"]) …}` (§7 auto-dark dual-selector).

### 4.4 CSV — контекст-split ✓ LOCK (тиха страховка в ••• меню, не герой)
- **Home-меню** = «усі дані (N аптек)» · **FILL-меню** = «ця аптека».
- *Rationale (Konst):* масштаб на команду — не всі аптеки твої → не вантажити чужі → не чистити вручну. Single-файл рідкісний але незамінний (shareable для комерц-відділу; copyValues = ефемерний буфер).
- **Механіка:** і Home і FILL кличуть спільний `openSheet()` → детект активного екрана (`#s-fill.active`?curPx:Home) → динам-лейбл CSV-рядка + `exportCSV()` детектить scope сам. БЕЗ нового UI.
- **Формат:** роздільник `;` (укр-локаль Excel + назви містять коми), поля з `;`/`"`/`
` — у лапках з `""`-екрануванням, **UTF-8 BOM** (кирилиця в Excel). Доставка: `navigator.share({files})` → фолбек Blob-download.
  - single (FILL): `Kode;Назва;Категорія;Норма;Залишок` × 83 SKU curPx (норма per-tier-per-visit §1).
  - all (Home): `Proxima;Місто;Адреса;M;Kode;Назва;Категорія;Норма;Залишок;Дата` — по аптеках із visits, останній візит, лише SKU зі значенням.
- Per-card іконка — відхилено. Свайп — deferred.
- **ВИДАЛЕНО (b9 ✓):** `xlsx-js-style` (−~86 КБ від v1), стильний .xlsx, колонка «→ Замовлення».


## §5 · IA + HOME + ПІКЕР
- **IA лінійна, БЕЗ tab-bar** ✓. *rationale:* Фармастор задачний (зайшов→полічив→вставив→вийшов), не browse як QR/Drive. Лін: **Home (маршрут) → drill FILL → назад**; About/CSV/очистити — у хедер-меню (•••).
- **Home / «Мої аптеки»** ✓ (**весь список, НЕ route «на сьогодні» — §8.1 RESOLVED**; *rationale:* per-візит дати роблять «сеанс сьогодні» неоднозначним + прив'язка до розкладу = scope creep, ще й окремо під колегу-тестера):
  - **3 стани картки:** не почато · заповнено X/83 → 📋 готове · перенесено ✓✓ (пригашена). Активні спливають угору, перенесені тонуть/згортаються. **→ детальна анатомія + значення LOCKED у §5.2 / §6.4.**
  - Дуальний якір M{X}+Proxima на картці (§4).
  - **Home-бейдж «Історія · N»** — футер-чип входу в §5.1 (clock + N + chevron), **завжди видимий**, disabled при N≤1. Свап зі старого «Динаміка»-афорданса. Деталі §5.2.
  - «Очистити сеанс» — **сховати з-під ока** (зараз великий рожевий конкурує) + гард-підтвердження.
- **Пікер / TopArea** ✓ **LOCKED (§5.3, harness v4 device✓ 15.07)**: L-A = breadcrumb-область(persist) + chip-band міст(swipe) + пошук-well + список. Band-swap місто⇄область. *Стара ідея «sticky city-групи / 2 міні-чіпи» — переглянута: область-перша вісь (мульти-юзер), картка §5.2 (тінт-тір, не чіпи).*

### §5.1 · ЕКРАН ПОРІВНЯННЯ (динаміка залишків) — ВЕРХІВКА ✓ CANON (device✓ в продукті b13, 20.07.2026)
> Мета: «стало краще чи гірше» між візитами (10-те vs 18-те). **Дата-контракт (§1) залочено; ВЕРХІВКА екрана device-відшліфована на harness — design-lock (нижче); повний canon-merge — після порт-батчу в продукт (як §10 для b11–b12).**
> **Джерело-істина верхівки:** `Farmastor_dynamika_harness_v4_3.html` (device✓ XS/Pro) + `Фармастор_session_summary_v2_dynamika_v4_LOCK.md` (повний стан + harness-lock'и + черга). Значення НЕ дублюю тут — беру звідти при порті (як §2).
- **Вхід:** з Home-картки бейдж «Історія · N» (§5.2, активний при N≥2). Per-аптека (порівнюєш візити ОДНІЄЇ аптеки).
- **Що з чим:** обираєш два знімки **«від / до»** (дефолт — останні два `transferred`). Повний тренд по SKU — пізніша амбіція.
- **Розкладка:** реюз **FILL-акордеона** (бренд/під-група, sticky eyebrow — безкоштовно). Рядок: `SKU · <дата-від> · <дата-до> · Δ`. Тумблер **«тільки зміни»** (сховати нерухомі). Дефолт-сорт master-order + опція «за рухом».
- **Кодування руху ⚠️ (крук) — ✓ CANON — МОДЕЛЬ B (device✓ в продукті b13):** напрям ≠ добре/погано. **Колір Δ = за НЕДОБОРОМ `s=max(0,MSL−V)`, НЕ за дистанцією і НЕ за напрямом.** *Реопен (19.07):* стара «дистанція» фарбувала падіння під норму зеленим (7→4 / MSL5 = «наблизився» = green, хоча 4<5 = дозамов) — на девайсі розчеплення колір↔сире-число не читалось. **Рівні B:** недобір скоротився/закрився → **improve / accent** (навіть якщо ще нижче норми — траєкторія ↑); недобір виріс / впав у дефіцит → **degrade / warn**; застряг нижче (`sT=sF>0`) → **stuck / warn**; обидва ≥ MSL → **stable / muted**; порожня (V=0) → **crit**. **critK = 0** (лише порожня полиця = crit-червоний; фіксований поріг 1-6 **відкинуто** — не масштабується під per-SKU норму; «все червоне» **відкинуто** — вбиває тріаж, червоний має лишатись рідкісним = терміновим). **+ видиме сире число** (магнітуда). **Розчеплення (ядро B):** Δ-колір = ТРАЄКТОРІЯ (краще/гірше); а «нижче норми ЗАРАЗ» ловлять фільтр «Проблемні» (§5.4 = СТАН) + сире число. Модель B вирівнює й «Проблемні» під §5.4 (нижче норми = `sT>0`), тоді як A фільтрувала за траєкторією. *Джерело: `Farmastor_dynamika_deltacolor_harness_v1.html` (device✓); sync-TODO: пере-навести на b13 після порт-девайсу.*
- **Absent-чесність:** SKU present в одному знімку й absent в іншому → «—», НЕ фейкова Δ.
- **Шапка-вердикт:** `↑N краще · ↓N гірше · =N без змін` + одне слово («Загалом: погіршилось»). Вердикт-слово авто-похідне від tally (свап моделі → перефарбовує). **tally = ТРАЄКТОРІЯ** (не рядок-колір): `stuck` (нижче, незмінно між візитами) рахується в «без змін», хоча рядок warn (СТАН) — узгоджено з розчепленням B.

**Верхівка екрана — ✓ CANON (device✓ в продукті b13):**
- **Sumcard-уніфікація** — верхівка = **1 картка `.sumcard`, 3 інтегровані зони** (`[статус+tally]` · тонкий дільник · `[фільтр-тунель]`). Нічого не висить на фоні (прибрано стару «розірваність»: вердикт-біла-картка + band «безпритульні»). Фікс «чорноти»: `.scroll{background:var(--bg)}` явний + `<meta color-scheme>` + `:root/[dark]{color-scheme}`.
- **Композиція A** (робочий напрям): дата-пігулка горизонтально згори-праворуч, **3 плитки на всю ширину** + нижча картка. (B = верт. дата-стовп справа — тумблером у harness, не обрано.)
- **Dark-tile матеріал** = tone-lift (A45/A66.1): плитка помітно СВІТЛІША за картку + верхній ридж + нижня темна грань, **drop=0** (OLED). Значення `Dlift10/Dridge16/Dgrane12/Dbord7` → **§6.5**. Світлі плитки — drop **16px** (A66: <14 = «потемнів край», не lift) + верт.градієнт + hairline. Плитки ПІДНЯТІ — свідомо ≠ інсет-well рядків (well=recess=поле; tile=lift=summary).
- **KPI-контекст (tally «відносно чого»)** — whisper-caption **«відносно MSL» ПІД словом-статусом**, сидить у наявних 34px висоти іконки → **0 доданої висоти**; контекстуалізує вердикт і всі 3 плитки.
- **Підписи плиток = «до норми / від норми / без змін»** (Konst-вибір проти ліну «ближче/далі»). **Зв'язка залочена: caption ON + до/від норми.**
- **Стан-вердикт (3)**: `up=Покращилось` (тренд↑ SVG, accent) · `down=Погіршилось` (тренд↓ SVG, warn) · `flat=Без змін` (=, muted). Іконка в м'якому кольор-кружку (світла 13% mix · темна 22% у surface-3). device✓ обидві теми.
- **Анатомія рядків (нести без змін):** гібрид-анатомія · **Δ=T2-гніздо** (світла глянець+drop / темна A66.1 tone-lift) · **Δ-колір=НЕДОБІР `s=max(0,MSL−V)` (Модель B, critK=0 — див. крук вище)** · cross-norm=**WARN** (B обробляє через sF/sT: нижче нової норми=warn) · Проблемні=**СТАН** (`sT>0`, не рух) · Змінилось=будь-яка сира зміна · **вердикт-стрілки лише в шапці** (без row-стрілок) · **Нурофен=1 картка+nested eyebrow**.
- ⚠️ **`? OPEN` (лишається на порт-батч):** colhead «18.06 · 02.07 · ЗМІНА» — власна тонка смуга-поверхня (HIGH-3) · date-picker механіка (тап діапазону → міні-шіт **A58 від/до**, зараз заглушка).

### §5.2 · HOME-КАРТКА — АНАТОМІЯ ✓ LOCKED (harness v3.4, device✓ 14.07.2026)
> Джерело-істина: `Farmastor_home_harness_v3_4.html`. GPT-мокап оцінено ЛИШЕ по layout (governance) → взято 2-колонкову композицію + кільце-статус; логіку/семантику лишено за §5/§3.6.

**Композиція — 2 колонки + футер:**
- Grid: `[ідентичність 1fr | герой auto] / футер на всю ширину`. *rationale:* вбиває L-подібну порожнечу старого вигляду (чіпи top-right + число mid-right лишали мертву зону).
- **Ліва (ідентичність):** addr (жирний, **2 рядки wrap** ellipsis-clamp) → місто (muted) → **тір-рядок**.
- **Права (герой):** кільце-статус, число всередині.
- **Футер:** якір `M{X} · Proxima {ID}` ліворуч · **Динаміка** (visits-gated, центр) · дата праворуч.

**Кільце-статус (лягає ПОВЕРХ 3-станової §5, НЕ замість):**
- **не почато** (state=new): порожнє сіре кільце (`--ringTrack`) + «**—**» по центру, **БЕЗ слова** (Konst-lock 14.07). *rationale:* «—» достатньо; порожнеча під кільцем чесно = «нічого не зроблено»; внутр. інструмент — патерн вивчається за 2 рази. «0%» заборонено (бреше: не поміряно ≠ нуль).
- **готове частк.** (filled 1-82): дуга-заповнення **partial-hue** + число `X/83` + «`%`» у розриві.
- **повне** (filled 83): повна дуга **full-hue** + «`100%`».
- **перенесено** ✓ CANON (device✓ в продукті b14_2, 20.07.2026): **НЕ ховаємо ринг** — картка тримає **ринг + fill + гepo-число** (як ready), лише dim. `✓✓` **у розриві дуги** (замість `%`, P1) + tiny-caption «перенесено» під рингом. *rationale (Konst):* стара голі-`✓✓`-заміна ховала дизайн, який дорого зробили; ще й суперечність — усі неактивні картки мали неактивну дугу, тож «схована власним успіхом» (§5.2-deferred hole). Показ рингу на перенесеній підсилює «переніс усі показники» + картка читається преміальніше.
  - **Механіка dim (harness v2):** dim БЕЗ whole-card opacity (bg-mix §6.4 `dimMix` + `saturate dimSat`); текст (idcol/foot) ghost на `dimOp`; ринг тримається окремо на **`--arcLift=.82`** (device-tuned) → лишається «живим» попри dim. У секції «Перенесені (N)».
  - Це **статичне** закриття hole «дуга схована»; **celebration-на-копі** (програти дугу як нагороду в момент 📋) = hole #1 **motion**, лишається deferred (§9).
- **Слово-статус = режим «дуга»:** число-%/слово у **розриві кільця ~90° внизу** (дуга огинає текст — як у мокапі). Rotate 135°, pathLength=100, gap 90° знизу.
- **Копі-слово = `%`** (`54%` / `100%`), НЕ «готове/повне». *rationale:* «готове» дублювалось (частк.=«готове» І повне=«повне·готове» → «готове» двічі = обман); % чесніше + дає магнітуду.
- **число-герой збережено** (§3.4-напрям): число всередині кільця — герой; кільце = його **статус-рамка + прогрес**, не заміна.
- **Двоколірний fill (hue за станом):** partial = бірюзовіший, full = зеленіший → миттєве «в процесі vs готово» без зайвого слова (реалізує оригінальну teal→green ідею мокапа через hue). Значення §6.4.
- **Тір = тінтований inline-рядок** `OTC B · IW C` (НЕ чіпи, НЕ top-right) — тримає ідентичність цілісною колонкою; тінт per-тема (§6.4). *Порівняно проти чіпів/нейтралу в harness — тінт-рядок обрано.*
- **Рейки НЕМА** (§3.3-дисципліна, свідомо).
- **Home-бейдж «Історія · N» ✓ CANON (device✓ в продукті b14, 20.07):** футер-чип (icon=clock · label «Історія» · `N=visits.length` · chevron) = вхід у §5.1. **Завжди видимий**, disabled при `N≤1` (не ховається — discoverability). cap 7 (`N>7→«7+»`). Прес A67 делегований scale .88, **ізольований** (прес лише бейдж, картка статична; клік `stopPropagation→openCmp`). Футер став 2-слот (`.date` прибрано з Home → живе в §5.1 dpill). Значення L/D soft-fill split: `Фармастор_history_badge_valuesLOCK.md`. *Свап зі старого афорданса «Динаміка ›/показники ›».*

**⏸ Deferred (не лочено, наступні harness):**
- Анімація заповнення дуги (`stroke-dashoffset`, A70: не box-shadow → без шимеру; **НЕ анімувати всі кільця на mount** — тільки щойно-заповнену/on-state-change). Значення — окремий motion-пас.
- All-done reward при 83/83 (§9 черга, поки motion свіжий).

### §5.3 · TOPAREA / ПІКЕР — ✓ LOCKED (harness v4, device✓ 15.07.2026)
> Джерело-істина: `Farmastor_toparea_harness_v4.html`. IA = **L-A** (обрано device з L-A/B/C). Мульти-юзер: **область = перша вісь** (колега → своя область, ставить раз).

**Композиція (зверху вниз, під app-хедером):**
- **Breadcrumb** — область ЛИШЕ («Область ▾», nowrap). **Persist per-колега** (localStorage, B57 name-guard: `{a:areaName}`, guard=область ∈ AREAS).
- **Chip-band (одна стрічка)** — за замовч. міста обраної області (+ «Всі»); горизонт. свайп + **edge-fade** (динам. `ov-l/ov-r` mask — край тане там, де є контент = підказка «гортається»).
- **Пошук** — well-поле (§6.3/A45), фільтр addr/місто/Proxima в межах область+місто. Іконка = **inline SVG** (НЕ емодзі — лок, щоб не портонути).
- **Список** — Home-картки §5.2; при обраному місті per-картка city-рядок ховається (дублює контекст).

**Band-swap (ключова механіка — БЕЗ модала/vert-push):**
- Тап **breadcrumb ▾** → стрічка перемикає вміст **місто ⇄ область у ТОМУ Ж рядку** (crossfade `bandin .18s ease`; нуль зміни висоти → нуль jank; каретка ▾→▲). Вибір області → назад на міста нової обл. (renderTop, scroll=0, picking='city').
- *rationale:* вертикальний pop (max-height) штовхав список → jank (device 15.07). Band-swap вбиває jank І робить область свайпабельною.

**Вибір міста — scroll-preserve (device-lock 15.07):**
- Тап міста → ЛИШЕ переставити `.on`-підсвітку **на місці** (НЕ rebuild стрічки) + оновити список. Scroll стрічки зберігається → обране лишається в полі зору. *rationale:* rebuild скидав scrollLeft → обране зникало, треба скролити знову.

**Матеріал чіпів — per-тема (A45):**
- Світла: `linear-gradient(180deg,#fff,#eef4f1)` + border + `0 1px 2px rgba(20,50,42,.07)`.
- Темна: **tone-lift** `linear-gradient(180deg,#26332d,#1e2924)` + `inset 0 1px 0 rgba(255,255,255,.06)`, БЕЗ drop (OLED).
- Активний: акцент-градієнт (світла `hsl(162 82% 31→26%)` / темна `hsl(163 46% 50→44%)`).

**Прес — pointer-driven, device-locked (15.07):**
- Механізм: `.is-pressed` через pointerdown/up (**iOS `:active` ненадійний у PWA** → Cookbook-кандидат, розшир. A67).
- Значення: **місто scale .90 / 80ms · область scale .88 / 110ms** (важче=трохи повільніше — A67-драбина). Konst-tuned device.

**Пошук-well (§6.3/A45):**
- Світла: inset-well `color-mix(bg-soft 82%, card)` + `inset 0 1px 2px rgba(20,50,42,.15)`.
- Темна: dip+ridge `color-mix(card, #000 24%)` + `inset 0 2px 5px rgba(0,0,0,.55)` + `inset 0 -1px 0 rgba(255,255,255,.12)`.

**Геометрія (device-locked CFG):** chipH 30 · chipGap 6 · chipPadX 14 · chipRad 10 · searchH 40 · taGap 8. vcost ~143px (XS) / ~156px (15Pro).

**Відкинуто / поза scope:**
- **Sticky-collapse на скрол** — показано в harness, Konst: на примітку, НЕ в роботу.
- **Scope-crumb** «Обл › Місто» у breadcrumb — прибрано (місто вже видно активним чіпом → дубль + ламало рядок довгим містом).
- **«залипло ✓» badge** — прибрано (persist тихий).
- **L-B / L-C** — не обрано.

**⏸ Deferred (Node 5 build / пізніше):**
- Повний display-resolver: с./смт (стоп-геп ловить лише «м.»), дедуп «м.Самар»↔city, обрізка ТЦ/прим-хвоста (§9 LABELING).
- «Нещодавні/закріплені» секція — пізніше (scope).

### §5.4 · STATUS-ФІЛЬТР (усі/активні/перенесені) — ✓ CANON (device✓ в продукті b13) · ⚠ хвіст: чип-count висота/ширина → §11
> Джерело-істина: `Farmastor_status_filter_harness_v2.html` + `Farmastor_status_filter_harness_v1.html`. Закриває дві діри: **discoverability Динаміки** (REOPENED §5.2) + **перегляд перенесених аптек** (довгий скрол до низу списку).

- **Комбо-чіп біля області** (НЕ в правому кутку — Konst-мокап). Мова = C1+C3 на чіп-поверхні (§5.3-матеріал `.bc`): `[глиф] Мітка · N ▾`.
  - Глиф-слот (mono, нуль емодзі): **Усі** = порожнє muted-кільце · **Активні** = залитий accent-dot · **Перенесені** = `✓` (accent-ink/accent).
  - Лічильник поточного фільтра в чіпі (Активні/Перенесені); загальний `N апт.` лишається справа (область-total). Каретка ▾.
- **Механіка = band-swap (як область, §5.3)** — тап по чіпу → нижня стрічка (міста) міняється на `[Усі][Активні][Перенесені]` тим самим `bandin .18s` crossfade; **нуль доданої висоти**, нуль модала. Вибір → стрічка вертається на міста, чіп оновлюється. `picking='filter'` (поряд із `'city'`/`'area'`). *rationale:* одна ідіома жестів на весь топ; ▾ явно каже «тут вибір» (discoverability > німий цикл-тап). Цикл-тап порівняно в harness (`Відкриття: Цикл-тап`) — **band-swap обрано** (Konst device).
- **Список:** `mode` фільтрує поверх область+місто; `all`=активні-перші+секція «Перенесені (N)» (поточна поведінка); `active`/`transferred`=лише свій підмн. Перенесені у своєму режимі — без секції-дільника.
- **Прес:** `.bc`-чіп pointer-driven (розшир. A67, §5.3). Свап-стрічка = реюз `renderBand`-механіки §5.3 (scroll=0, `.swap`-крос-фейд).
- **Відкинуто:** C2 seg-контрол (найчистіший UX, але окремий рядок = +висота проти цілі «нуль висоти» + колізія з довгою областю) · C3 голий `●8·✓4` на breadcrumb (Konst: «точка+галочка на голій поверхні» → на чіп-поверхню).




## §6 · ТОКЕНИ · ГЕОМЕТРІЯ ✓
> Провенанс: color_harness_v2 + STEP2 CFG (device✓). §6.1 нейтрали · §6.2 акцент · §6.3 компонент-геометрія · §6.4 Home-картка.

### 6.1 Нейтрали ✓ (device-locked, обидві теми)
```css
[light] --bg:#eef3f1; --bg-soft:#e4ece9; --card:#ffffff; --surface-2:#f4f8f6; --surface-3:#eef4f1;
        --text:#182c28; --text-2:#3c574f; --muted:#6b8c84; --border:#d4e5df; --border-subtle:#e1ebe7;
        --ok:#1f9d57; --crit:#c0392b; --warn:#c8811b;
[dark]  --bg:#0d1512; --bg-soft:#151e1a; --card:#18221e; --surface-2:#1c2723; --surface-3:#212d28;
        --text:#e8f0ec; --text-2:#a7c0b8; --muted:#7c968d; --border:#2a3833; --border-subtle:#222e29;
        --ok:#33c06f; --crit:#e0685c; --warn:#e0a94a;
```

### 6.2 АКЦЕНТ — TEAL ✓ LOCKED (Konst-tuned, color_harness_v2, 12.07.2026)
> Переважає над старим baked `#0d7c66`. *rationale вибору:* teal — єдиний хью, що одночасно достатньо зелений (δ-ok «+N» читається як «в нормі»: світлофор ok→low(warn)→crit) і достатньо синій (не зливається з чистим `--ok`/✓). Бренд І статус в одному. Нуль ре-тюну (все вже device✓).

| токен | ☀︎ light | ☾ dark |
|---|---|---|
| `--accent` | `hsl(162 82% 27%)` | `hsl(163 46% 46%)` |
| `--accent-soft` | `hsl(162 64% 88%)` | `hsl(163 37% 17%)` |
| `--accent-ink` | `hsl(162 82% 16%)` | `hsl(163 46% 68%)` |
| `--inkStr` | 14 | 15 |
| `--tintMix` (settled-заливка) | 50 | 50 |
| `--mutL` | 46 | 46 |
| `--valL` / `--ghostOp` | 100 / .34 | 100 / .34 |

- δ-чіп семантика: **lv-ok = `--accent`** · lv-low = `--warn` · lv-crit = `--crit`. (Розчеплення ok→власний `--ok` — відкладена опція, §8.)

### 6.3 Компонент-геометрія ✓ (device-locked, CFG STEP2 §1)
- **Комірка (field-well):** `W:60 H:46 radius:15 numW:800`; ghostOp .34; zeroTint 55. Light: inset-well (lWellBg 82, depth 1.2, α .28). Dark: dip 24, inset 5, ridge-light .12.
- **δ-чіп:** `fill:soft · border:on(55%) · knock:off · sign:hyphen`; кут-офсет `chOffX/Y:6` (над полем, top/right −6); `rad:9 padX:5.5 padY:3 size:10.5`; per-theme `chFillInt:0 / chBorderInt:55` → карт-фон + 55% sig-рамка + sig-текст.
- **Eyebrow:** tick `3×16 r3` (accent, tickOp 1) · hairline **top** `2px` inset 7 · `inkStr:10` (акцент у напис) · `ebSize:11 ebSpace:1.2 ebWeight:700` · band OFF.
- Роздільник рядків: `border-subtle`, rowGap 6.

### 6.4 HOME-КАРТКА values ✓ LOCKED (harness v3.4, обидві теми, device✓ 14.07.2026)
> Копі-конфіг harness (JSON) — істина. Нижче зведено.

**Геометрія (спільна обом темам):** `cardRadius 20 · cardPad 12 · cardGap 9 · appPad 14 · ringSize 62 · ringStroke 5 · numSize 23 · numWeight 800 · statusSize 11 · underH 3 · addrSize 15 · addrWeight 650 · citySize 12.5 · anchorMut 46`. Нюдж: `statusX/Y` = 0/1 (light) · 0/0 (dark); `ringX/Y` = 0/0.

**Fill кільця — ДВОКОЛІРНИЙ (hue за станом, per-тема):**
| тема | full 100% `H S% L%` | partial 1-99% `H S% L%` |
|---|---|---|
| ☀ light | `150 55 46` | `175 60 46` |
| ☾ dark | `155 55 50` | `168 55 50` |
- Логіка: `filled>=83 → full` інакше `partial`. Реалізація: `hsl(var(--fillFull*) )` / `hsl(var(--fillPart*))`, вибір per-circle inline.

**Статус-слово (%) `H S% L%`:** ☀ `160 58 37` · ☾ `163 55 55`.

**Тінт TIER `H S% L%`:**
| тема | OTC | IW |
|---|---|---|
| ☀ light | `160 55 40` | `210 48 44` |
| ☾ dark | `162 46 55` | `210 48 60` |

**Перенесено (dim):**
| тема | →bg % | saturate % | opacity % |
|---|---|---|---|
| ☀ light | 16 | 70 | 60 |
| ☾ dark | 30 | 60 | 50 |

- **Кільце (ринг) геометрія:** SVG `pathLength=100`; full-mode rotate −90 (старт зверху); **arc-mode rotate 135°, gap 90° знизу** (дуга-статус); `stroke-linecap:round`; track = `--ringTrack` (light `#dbe8e2` / dark `#2a3833`).
- **⚠️ Нюанс на device-порт (не блокер):** addrWeight 650 vs numWeight 800 — число важче за адресу; на 63-списку перевірити чи адреса (ціль скану) не рецесивна. statusL 37 (%-слово) на XS 11px — перевірити на сонці.

### 6.5 DYNAMIKA-ПЛИТКИ + ПЕРЕНЕСЕНА-РИНГ ✓ CANON (device✓ в продукті b13/b14_2)
> §5.1 верхівка + §5.2 перенесена. Значення device✓ в продукті (b13/b14_2). Канон.

- **Dark-tile матеріал (§5.1 плитки, tone-lift A45/A66.1):** `Dlift=10` (біле% у surface-3 = тон-lift) · `Dridge=16` (верхній світловий ридж ×.01α) · `Dgrane=12` (нижня темна грань ×.01α) · `Dbord=7` (підсвітка рамки біле%). **drop=0** (OLED).
- **Light-tile:** drop blur **16px** (A66: <14 = «потемнів край», не lift) + легкий верт.градієнт + hairline.
- **Перенесена-ринг (§5.2):** `--arcLift=.82` — opacity рингу перенесеної картки (тримається окремо від dim тексту). Dim картки: `dimMix/dimSat/dimOp` = §6.4 (light 16/70/60 · dark 30/60/50) — БЕЗ whole-card opacity (bg-mix + saturate; ринг на arcLift, текст на dimOp).


---

## §7 · iOS/PWA ЯКІСТЬ-ПАТЕРНИ ✓ (не брендинг — якість)
- `dvh` для max/min-height (не `vh`); `env(safe-area-inset-bottom)` без `+12px`.
- **Auto-dark dual-selector:** `[data-theme="dark"]` + `@media(prefers-color-scheme:dark){:root:not([data-theme="light"])}` для кожного hardcoded dark-оверрайду.
- **FOUC:** inline `<head>`-скрипт читає localStorage і ставить `data-theme` ДО першого paint.
- Dark elevation = tone-lift (не drop-shadow на OLED); `border` не `box-shadow:inset` для selection-ring.
- **Bottom-sheet swipe-close:** grip-зона dy>40px завжди; контент-зона тільки якщо `scrollTop===0` при touchstart AND dy>64px.
- **harness-first** для будь-якого eye/motion-рішення; **device = фінальний арбітр** (compare-lock ≠ canon).
- Solo-скрол: рамка `flex:1;overflow:hidden`, внутрішній `.app{height:100%;overflow-y:auto}` (інакше flex-center-clip з'їдає верх).

---

## §8 · ПОРТ-ЧЕКЛИСТ + OPEN
**Порт v1.3 → v2 (тема-агностична оболонка):**
- [ ] Всі 83 назви з `multibrand_harness_v1` DATA.
- [ ] Нейтрали §6.1 + teal-акцент §6.2 + геометрія §6.3.
- [ ] norm-resolver §3 (категорія→тір→MSL-колонка) — НЕ A-плоско.
- [ ] Тір-профіль на картці аптеки (`OTC B · IW C`).
- [ ] Copy-контракт §4 + видалити xlsx-стек (−425 КБ).
- [ ] Стейт-модель v2 + міграція v1→v2 (§1).
- [ ] `visits[]` знімки-масив per-аптека + snapshot-on-copy A1 (§1) — екран порівняння §5.1 fast-follow.
- [ ] **getBrand-фікс:** р.408 `«містить Durex»` (substring) ловить 12 гелів «Гель Durex…» → точний матч бренду, не substring.
- [ ] Auto-dark dual-selector + FOUC-скрипт (§7).
- [ ] **Конфіг-шар мереж** (§0): бренд-токени мережі = конфіг, не хардкод — закласти ЗАРАЗ (дешево), не ретрофітити.
- [ ] Copy-param-set повний (harness 📋 має виводити mutL/valL/ghostOp — діра, знайдена 12.07).

**? OPEN (рішення потрібне):**
1. ✅ **RESOLVED → Home = весь список** (НЕ «на сьогодні»). Route-прив'язку не робимо (scope creep + колега-тестер). Історія по днях = §1 `visits[]` + екран §5.1. Див. §5.
2. ✅ **RESOLVED → TopArea §5.3** (L-A band-swap, harness v4 device✓ 15.07).
3. **δ-ok розчеплення** (опція) — лишити lv-ok=accent (teal, поточне) чи розчепити на власний `--ok` (якщо бренд колись піде в не-зелений). Зараз teal → не актуально.

---

## §9 · ЩО ДАЛІ (upd b6, 13.07.2026)

**Motion reward — LOCKED v2 (device✓ dark, bake ×1):**
- shared: collapseDur 700ms/ease-in-out · popDur 800ms/ease-in-out · popOver 4.5%
- dark (glow німб ::after): glowDur 900ms · glowSpread 16 (unitless) · glowOp 0.9
- light (wash+ring ::before): washDur 900ms · washOp 0.7 · ringW 5 (unitless) · ringOp 0.9
- lead-before-collapse 140ms · collapse = grid-rows 1fr→0fr
- Тригер: brand→done у refreshCounters → fireReward (resolvedTheme гілкує dark/light).
- Харнес-істина: Farmastor_motion_harness_collapse_glow_v2.html (raw-важелі, per-theme, frame-gap).

**Node-черга (порт-план 8 нод; 1-5 FILL злиті у b-серії):**
- ✅ Node 1-5 FILL (b4/b5): поле, ghost-норма, δ-чіп, eyebrow A48, copy-preview.
- ✅ Motion reward port (b6).
- ▶ Node 6 — СТАН v2: visits[] знімки + snapshot-on-copy A1 + міграція v1→v2 (§1). Чиста логіка, беквбон, розблоковує §5.1.
- ✅ Node 7 — HOME: 3-станові картки. **PORT DONE (b7_2, device✓ 15.07):** Hybrid-стан (today-scoped + «ост.дата» на new), двоколірний fill, дуга-%, тір з visit.tier, Динаміка visits≥2. + addr street-led стоп-геп (b7_3 картка / b7_4 FILL-хедер).
- Node 8 — COPY §4: 📋→M{X}, знести xlsx-стек −425 КБ. (Прим.: copyValues by-kode вже є у b5/b6 як preview; xlsx-стек ще не знесений — звірити.)
- ▶ Node 5 — ПІКЕР/TopArea: **дизайн LOCKED §5.3** (harness v4 device✓). Лишається BUILD у продукт (band-swap + persist + пошук-фільтр + область→місто). Далі — окремий чат.
- §5.1 ПОРІВНЯННЯ: **верхівка DESIGN-LOCKED §5.1** (harness v4_3 device✓ 18.07). Лишається BUILD у продукт (sumcard + dark-tile §6.5 + caption + до/від норми + стан-іконки) + `? OPEN` colhead-«дім» (HIGH-3) + date-picker A58.

**✅ ПОРТ-БАТЧ b13/b14 — DONE (device✓ в продукті · canon-merge 20.07):**
- §5.4 status-фільтр · §5.1 верхівка + Δ-колір(B) · §5.2 перенесена-ринг + Home-бейдж «Історія» · §6.5 матеріал — усі злиті в канон (секції вище). ⚠ хвіст §5.4: чип-count висота/ширина → §11.

**▶ НАСТУПНЕ (окремі чати):**
1. **Motion-стенд (hole #1)** — celebration-заповнення (дуга-нагорода при поверненні на Home) + reorder-спуск картки у «Перенесені» = **пара зчеплених рухів** (slow-mo harness, frame-gap, wsd 2.4). ← наступна велика задача.
2. **Хвости (§11)** — status-фільтр чип-fix · About-щит A58-рестайл · dark-меню tone-lift.

**Ідея-тріаж:**
- 🔜 **Hole #1 MOTION (celebration-на-копі)** — програти дугу як нагороду в момент 📋 (у FILL або на поверненні Home). Статику «дуга схована» вже закрито §5.2 (ринг лишається на перенесеній); celebration = окремий motion-harness (slow-mo + frame-gap, wsd 2.4). Узгодити з All-done-reward нижче.
- 🔜 All-done reward — коли аптека 83/83 (фліпає Home-картку). Наступний harness, поки motion свіжий.
- ⏸ Витягнути акордеон спільним примітивом — ВІДКЛАДЕНО (передчасно, поки FILL не стабільний; Konst).
- 💡 Invariant-тест absent≠0 — named-invariant у валідацію після node 6 (сторож проти val||'' пастки).

**? OPEN-design (harness-first, device-арбітр):** ~~Home-картка (3 стани)~~ ✅ LOCKED §5.2/§6.4 · ~~пікер-рядок~~ ✅ §5.3 · ~~§5.1 UI верхівка~~ ✅ DESIGN-LOCKED §5.1 · ~~status-фільтр~~ ✅ §5.4 · **лишається:** colhead-«дім» (§5.1 HIGH-3) · date-picker A58 від/до · hole #1 motion.

**🆕 NODE-5 LABELING (device-surfaced 13.07):** назва аптеки = `[TIER] Місто — Область, м.Місто, вул.X, N` → місто дублюється 2-3×, область баласт. На FILL-хедері ідентифікатор (вулиця) обрізається за «Дніпропетровська обл., м.Дніпро…». Фікс: display-name resolver (зняти область, дедуп місто) → ідентич-лінія ВЕДЕ вулицею, місто тихо/на рівні групи. Пікер: місто=sticky-група (§5 вже планує), рядок=вулиця сильна+Proxima дрібним. FILL-title=вулиця, не область. **✅ Стоп-геп SHIPPED (b7_4, device✓ 15.07):** `displayAddr=strip(/^Україна,/)+strip(/обл.,/)+strip(/^м.[^,]*,/)` → addr ВЕДЕ вулицею, на Home-картках + FILL-хедері. Місто-дубль знято. ▶ **Node 5 повний resolver ще треба:** с./смт (стоп-геп ловить лише «м.»), дедуп «м.Самар»↔city, обрізка ТЦ/прим-хвоста. ⚠️ дата-кейв'ят: parse крихко АБО почистити джерело.

-----

## §10 · b11–b12 POLISH LOCKS ✓ (device✓ Konst XS+Pro · canon-merge 17.07.2026)
> Провенанс: `Фармастор_замовлення_v2_port_b12_2.html` (live-code grep, wsd 12.1) + самері b11 + compare `Farmastor_container_material_compare_v1.html` (device✓). Раніше жили лише в самері → тепер канон (wsd 12.8a / 12.9).

### 10.1 Меню-шіт A58 (b11) ✓
- **Статичний DOM** для ФІКСОВАНОГО меню (свідомо, НЕ декларативний `renderMenu()`) — оминає A54 lesson-3 rebuild-пастку (thumb постійний). Нюанс до канону A58: `renderMenu` виправданий лише при ЗМІННОМУ вмісті (SR-список QR).
- Grouped-cards eyebrow **ВИГЛЯД / ДІЇ / СЕАНС**. `.gcard` surface-3 + border-subtle(dark:border) rad14; `.mi` flat-рядки з border-bottom-дільником (НЕ пігулки-кнопки); `.eb` 800 10.5px uppercase.
- Вміст: тема-сегмент 3-в-1 (§10.2) · Excel deep-link (§4.2) · Експорт CSV (§4.4) · Про додаток (About A58) · Очистити (danger, останнім). Іконки — mono inline-SVG (нуль емодзі).

### 10.2 Тема-сегмент ковзний thumb (A54) ✓ LOCK
- 3 сегменти Авто/Світла/Темна, статичний DOM → thumb постійний. `setTheme(mode)`; `applyThemeSeg`/`placeThemeThumb`; хуки init/fonts.ready/resize/openSheet (снап), тап (слайд).
- **Motion device✓:** `--seg-dur:500ms; --seg-ease:cubic-bezier(.34,1.80,.64,1)` (harness v1, Konst «середній баланс»). thumb: light `background:var(--accent)` · dark `linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%))`.

### 10.3 confirmAction (A59) ✓
- Один `sh-confirm` (title+desc+[Скасувати]/[Видалити-crit]). **cloneNode-reset** one-shot handler; handoff меню→confirm `setTimeout(…,120)`. `closeSheets`/scrim закривають і confirm.
- **Context-aware Очистити:** FILL→«Очистити підрахунок» (`todayVisit.vals={}`, історія visits[] лишається §1); Home→«Очистити всі дані» (`ST.phs={}`).

### 10.4 Прес A67 — делегований ✓
- Глобально: `document pointerdown → closest('.pressable')||closest('.chip') → +is-pressed`; pointerup/pointercancel → `clearPressed`. iOS `:active` ненадійний → pointer-driven (розшир. A67).
- **Магнітуди (split):** `.icon-btn .88` · `.btn-copy .96` · `.btn-form .92` · `.card .985` · `.chip scale(var(--pcs))` (місто .90/область .88 §5.3) · `.cf-*`/`.tgpill .96`. Велика капсула = м'якша магнітуда.
- **Рядки меню `.mi` = bg-tint** (НЕ scale): `.mi.is-pressed{background:color-mix(in srgb,var(--surface-3),var(--text) 5%)}` (iOS table-row ідіома). **b12_2:** усі 4 тапабельні рядки несуть `.pressable` (Excel-рядок був єдиний без → допаровано).

### 10.5 Container material — icon-btn + mi-ic (b12) ✓ LOCK (compare device✓)
> Compare `Farmastor_container_material_compare_v1.html`; Konst-pick. Проблема: світлі контейнери тонули (A66 — світлу елевацію дає hairline+drop, не світліша заливка). Обидва контейнери = одна material-мова.

| важіль ☀ | знач | важіль ☾ | знач |
|---|---|---|---|
| Lfill | 55 | Dlift | 42 |
| Lbord | 55 | Dridge | 60 |
| Ldrop | 45 | Dbord | 45 |
| Linset | 0 | | |

**CSS (порт-готове; спільне для `.icon-btn` і `.mi-ic`; + A69 auto-dark мірор):**
- Світла: fill `color-mix(in srgb,#fff 55%,<backdrop>)` (icon-btn backdrop=`--bg` · mi-ic backdrop=`--surface-3`); border `1px solid rgba(20,50,42,.12)`; drop `0 1.4px 3.6px rgba(20,50,42,.081)`.
- Темна: fill `color-mix(in srgb,#fff 6%,var(--surface-3))`; border-color `rgba(255,255,255,.045)`; ridge `inset 0 1px 0 rgba(255,255,255,.096)` (БЕЗ drop — A45).
- **Back-кнопка = Контейнер** (не ghost): уніфікована під `.icon-btn` = пара з «•••»; текстова `‹` → SVG-шеврон (штрих як `.mi-chev`). Мертве `.icon-btn.ghost` знято.

### 10.6 iOS fixes (b12) ✓
- **Захист від нативних взаємодій (глобально):** `*{…;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}` + виняток `input,textarea,[contenteditable]{-webkit-user-select:text;user-select:text;-webkit-touch-callout:default}` (пошук `#q` + комірки `.fld-in` редаговані). Zoom вже глушив viewport `user-scalable=no`.
- **A55 height-model:** `html{height:100%;min-height:calc(100% + env(safe-area-inset-top))}` — захист під black-translucent installed-PWA (bg-matched → безпечно; Konst-keep).
- **Нижня смуга-банди — root cause + fix:** `.sheet box-shadow:0 -8px 30px` при ЗАКРИТОМУ шіті (`translateY(100%)`, край під viewport) кидав тінь ВГОРУ в низ екрана; 3 закриті шіти → банди на всіх екранах, тема-незалежно. **Фікс:** тінь лише на `.sheet.on` (закриті нічого не кидають). NB: це НЕ A55 — A55 був хибним первинним діагнозом (device спростував).

-----

## §11 · ХВОСТИ / TAILS (device-surfaced 20.07.2026 — план дій, не блокують стенд)
> Дрібні полірувальні борги з device-тесту b14_2. Кожен = харнес-first + device-арбітр. Порядок вільний; можна пакетувати в один polish-батч.

### 11.1 · Status-фільтр чип-count: висота/ширина ⚠ (діагноз готовий)
- **Симптом (Konst, скріни 3 стани):** при «Активні»/«Перенесені» статус-чип росте вгору (зсув `.bcrow`) + вширш (тисне регіон-чип → жорсткий ellipsis «Дніпропе…»).
- **Корінь (grep b13_2):** внутрішній `.cnt`-бейдж (46/1) успадковує **важкий FILL-стиль** `.cnt` (р.373): `min-width:42px` + `padding:3px 8px` + border + фон. На 1-2 цифри = завелика пігулка → +ширина (42px+) і +висота (верт. padding+border вищі за текст чипа).
- **План-фікс:** де-пігулити `.bc.filt .cnt` — прибрати `min-width/padding/border/background/border-radius`, лишити плоске tabular-число з малим `margin-left` (як `.h-n` бейджа «Історія»). Belt: зафіксувати висоту `.bc`/`.bcrow` + регіон-чип `flex:1;min-width:0`.
- **Питання Konst → рішення:** внутрішній count (filtered 46/1) ≠ бічний «47 апт.» (total) — **різні числа, обидва осмислені** («46 з 47»). Проблема = СТИЛЬ, не існування. Бічний «47 апт.» не винен (`margin-left:auto`, не росте). Рекомендація: **лишити обидва**, лише полегшити внутрішній.

### 11.2 · About-щит — старий дизайн → A58-рестайл
- **Симптом:** шіт «Про додаток» (версія/збірка/розробник/Telegram) — стара верстка, не в мові оновленого меню (grouped-cards A58 §10.1).
- **План:** A58-патерн — grouped-card surface-3 + `.mi`-рядки з border-bottom-дільником; Telegram-лінк як `.mi` external-link (§4.2 anchor, mono-SVG). Матеріал — §10.5. Кнопка **робоча**, борг лише візуальний.

### 11.3 · Dark-меню рядки «скло» → tone-lift
- **Симптом (Konst):** на темній під-рядки/картки меню читаються як «скло на бекграунді» — гірше за світлу.
- **Гіпотеза (A45/A66):** dark-елевація = **tone-lift** (світліша заливка surface-3), не напівпрозорість/backdrop («floating glass»). Ймовірно `.gcard`/`.mi` на темній беруть translucent-fill замість суцільного tone-lift.
- **План:** харнес dark-меню — звірити fill `.gcard`/`.mi` проти §10.5 (fill `color-mix(#fff 6%,surface-3)`, ridge, **без drop** — OLED); прибрати backdrop-blur/translucency → суцільний tone-lift. Device-compare L↔D поряд.

**Гігієна-нотатка:** борги CSV-експорт + About-**існування** ✅ закриті (обидва в проді, b11–b12). Лишався тільки візуал About → 11.2.
