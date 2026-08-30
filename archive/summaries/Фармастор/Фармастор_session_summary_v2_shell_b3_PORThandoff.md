# Фармастор v2 — session summary: SHELL b3 → PORT handoff

**Статус:** чистий шелл готовий і device-перевірений (b3). Наступний крок — **порт логіки §3 + видимий FILL-рендер**. Виконувати в новому чаті з повним бюджетом.

---

## 1. ЩО ЗРОБЛЕНО ЦЬОГО ЧАТУ (locked)

- **Рішення:** Фармастор v2 будуємо з нуля. Дизайн — новий за стандартами; логіку — портуємо. Старий v1.3-дизайн + legacy-міст + xlsx-lib (−425КБ) викинуто.
- **Шелл `b3`** (`Фармастор_замовлення_v2_shell_b3.html`, ~16КБ) — device✓:
  - Токени §6 дослівно з MASTER_LOCK: нейтрали §6.1 + **teal §6.2 Konst-tuned** (`hsl(162 82% 27%)` light / `hsl(163 46% 46%)` dark, inkStr 14/15). Старий harness-акцент `#0d7c66` НЕ використовуємо.
  - **Auto-dark dual-selector §7** (`[data-theme=dark]` + `@media(prefers-color-scheme:dark){:root:not([data-theme=light])}`) + **FOUC** inline-скрипт у `<head>`.
  - **Full-canvas тема:** фон `var(--bg)` на `html`+`.wrap`+`.app` (фікс «пісочного» дефолту сендбокса — тема тепер перемальовує всю площину).
  - **Нейтральний хедер** (§3/§6.1, без teal-банера, без емоджі-іконок): Home (назва мережі + •••) та Fill (back ‹ + «Аптека №168 · Proxima 102520» + тір-чіпи OTC B/IW C + progress + •••).
  - **Тема — у ••• sheet** (перший пункт, тап-цикл auto→☀→☾), доступна з усіх екранів. НЕ окрема кнопка в хедері.
  - **Лінійна IA §5, без tab-bar.** Порожні екрани `#s-home`/`#s-fill` (плейсхолдер-скафолди) + toast.
  - **Прес A67 pointer-driven** (iOS-надійний, спрацьовує на `pointerdown` до навігації): chip **.88** · CTA **.92** · sheet-item **.97**; press-down `.06s`, release `.22s` spring `cubic-bezier(.34,1.56,.64,1)`. `:active` НЕ використовуємо (Safari не тригерить на кнопках).
  - Quality floor: focus-visible, reduced-motion guard, orientation-lock overlay, solo-scroll (§7).
  - `APP_BUILD='v2.0.0-shell.b3'`; конфіг-шар мереж `const NETWORK={name,tagline,tg}` (§0/§8 — бренд=конфіг).

- **Дані витягнуто й звірено** → `farmastor_v2_data.js` (~28КБ, чистий JS, без xlsx-lib):
  - `const MSL=[…83…]` поля: `{n,c,A,B,C,D,k,p}` (name, category OTC|IW, норми по тірах A–D, kode, price).
  - `const PH=[…63…]` поля: `{px,area,city,addr,net,oTC,iW}` (Proxima ID, область, місто, адреса, мережа, тір-OTC, тір-IW).
  - Покриття: OTC 38 · IW 45; тіри реально вживані **A–D** (D є!); 15 міст, 3 області (Дніпропетровська 47 · Полтавська 10 · Кіровоградська 6).

---

## 2. LOGIC — правило норм §3 (ПІДТВЕРДЖЕНО Konst)

- Тіри A/B/C/D — категорії аптек за товарообігом, **окремо** для OTC і IW. Кожна бізнес-лінія має **свій набір MSL**: навіть тір A/A дає різні цифри OTC vs IW (різні рядки MSL).
- **Резолвер §3:** OTC-SKU → `ph.oTC` → колонка MSL цього SKU; IW-SKU → `ph.iW` → колонка MSL цього SKU. Донор це вже робить: `pcat = cat==='OTC' ? ph.oTC : ph.iW; norm = sku[pcat]`.
- **FYI (не блокер, баг на боці Excel):** у хмарному `Фармастор_замовлення_тт.xlsx` колонка «Кількіть MSL» рахує IW через **OTC-тір** (100% на 2835 IW-рядках). Це ймовірна помилка формули там (VLOOKUP на Category OTC протягнутий). Додаток рахує §3 правильно; корпоративний Excel Konst перегляне окремо.

---

## 3. НАСТУПНИЙ КРОК — ПОРТ §3 + FILL-РЕНДЕР (по вузлах, кожен device-review)

База: `shell_b3.html` (каркас) + `farmastor_v2_data.js` (дані).

1. **Вклеїти дані** (MSL/PH) у `<script>`; прибрати демо-скафолди Fill.
2. **Ліфт harness-компонент-CSS** дослівно з `Farmastor_multibrand_harness_v1.html` `<style>`: `.fld` (well 60×46 r15), `.dchip` (кутовий δ-чіп), `.ebrow` (tick+hairline+ink), `.row`/`.rv`/`.rpk`/`.ck`, `.row.settled.tint`, `.brand`/`.bhdr`/`.bbody`. **Кольори — на токени §6.2** (не harness `#0d7c66`).
3. **getBrand** (донор л.454, anchored regex, §8-баг уже фікснутий — перевірити всі 6 брендів) + **bKey** (л.464) + **groupByBrand** (л.508/516).
4. **getSubGroup + relabel §2** — у коді ЩЕ НЕМА (harness має це як hand-authored DATA, л.296–408). **Реалізувати за MASTER_LOCK §2 детекторами**, застосувати до реальних MSL-назв; звірити згрупування з harness DATA 296–408 як еталоном (`{eb, rows:[{rv,pk}]}`).
5. **norm-resolver рендер §3** — на кожен рядок: `norm = sku[cat==='OTC'?ph.oTC:ph.iW]`; ghost-норма + δ-чіп per аптека (НЕ плоска колонка A). silent-ok A59: сигнал лише на дефіциті.
6. **v2-стан §1** — будуємо з нуля (донор має лише старий `farmstore_v1` плоский kode-map): `visits[]` per аптека `{date,vals,tier,transferred}`, snapshot-on-copy (A1), same-day overwrite, одноразова міграція.
7. **Home-список** — картки аптек (3 стани), тір-профіль, прогрес; навігація Home→Fill з реальною аптекою. (Кандидати з мокапів: ліва акцент-смуга статусу, агрегат-прогрес.)
8. **Copy-контракт §4** — 83 значення by-kode у master-порядку → clipboard (+ textarea fallback) → toast «Скопійовано»; тиха CSV-страховка в •••.
9. **Picker §5** (fast-follow) + **Історія/Порівняння §5.1** (fast-follow; δ-колір = дистанція-до-норми, НЕ напрям).

---

## 4. ВПІЙМАНІ ПИТАННЯ (тримати на радарі)

- **Джерело «№168» / «M{X}»-якоря** — у `тт.xlsx` НЕМА (є лише Proxima `px`). Потрібно Konst: звідки короткий №/M-код (корпоративний хмарний Excel?). Впливає на Fill-хедер, copy §4 дуальний якір, toast «встав у M168». Зараз плейсхолдер.
- IW Excel-колонка (див. §2 FYI) — Konst перевіряє формулу окремо.

---

## 5. ДИЗАЙН — рішення/гардрейли

- **Варіант A:** компонент-CSS ліфтиться у FILL-кроці (не в шеллі).
- **Мокапи GPT** = лише дизайн/меню-натяки; логіку їх ІГНОРУВАТИ.
  - Перейняти (кандидати, harness-first): ліва акцент-смуга статусу на Home-картках; A-Я скрол-рейка в Picker; агрегат-прогрес на Home.
  - Відкинути: нижній таб-бар (проти лінійної IA §5); англ. статуси (усе укр.); **δ-чіп за напрямом** + «краще=збільшення» (проти §5.1 — колір = дистанція до норми).
- UI-копірайт: активний голос, дія тримає ім'я через флоу («Копіювати»→«Скопійовано»).

---

## 6. READ-FIRST для нового чату

1. `Фармастор_v2_MASTER_LOCK.md` — токени §6 / стан §1 / резолвер §3 / copy §4 / relabel+getSubGroup §2 / IA §5.
2. `Farmastor_multibrand_harness_v1.html` — visual truth: компонент-CSS + relabel DATA (л.296–408) + nameLine(л.479)/metaLine(л.485).
3. `Фармастор_замовлення_v2_step2_FILL.html` — донор ЛОГІКИ (JS): getMSLval(л.376), getBrand(л.454), bKey(л.464), groupByBrand(л.508/516), resolver call-site(л.516/537). Дизайн/старий стан/exportXLSX — НЕ чіпати.
4. `Work_Standard.md` → `Lens_iOS_cookbook.md` — стандарти (A45/A48/A59/A67).
5. Ця самері + база: `Фармастор_замовлення_v2_shell_b3.html` + `farmastor_v2_data.js`.

**Принцип:** plan→confirm→code (wsd 1.5) · grep-before-claim (12.1) · harness-first, device-арбітр (12.9) · memory ≠ канон.
