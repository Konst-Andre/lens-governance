# StockCheck b32.1 — session summary (s4 · PICKER REWORK: crop + «Всі»-картка · план погоджено, код не почато)

> **живе доки:** до закриття батчу пікер-рework (crop плити 73px + «Всі»-картка) у b32.1 з device-верифікацією. Після — P8 (netBtn mini-mark, окремо) → device на все → канонізація.
> Джерело правди коду — файл, не це самері (wsd 12.1). Якорі р.XXXX grep-verified у `_s3`, можуть зсунутись — грепати наживо.

---

## §0 · СТАН ФАЙЛІВ

- **База батчу (жива):** `StockCheck_port_b32_1_s3_O48.html` — О-48 внесено, gate-clean по суті, штамп `v2.25.0 / stockcheck-pwa.b32.1 / 10.08.2026` (ver НЕ бампнуто).
- **Стенд (лочені важелі, читати точково — НЕ вантажити цілком):** `StockCheck_netmark_stagebench_v3_7.html`.
- **Handoff лочених значень:** `StockCheck_B32_STAGEBENCH_HANDOFF.md` (§5 lock-spec, §7 kNets всі PASS).
- **Гейт:** `Lens_validate.py` НЕ на диску → raw `https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/kernel/Lens_validate.py`. Перед видачею: `python3 Lens_validate.py --html <файл>`.
- **node --check:** `.html` напряму не бере — inline `<script>` у `/tmp/*.js`.

---

## §1 · ВІДКРИТІ ПИТАННЯ (зверху = наступне)

### БАТЧ ПІКЕР-РEWORK (correctness UI · ПРІОРИТЕТ 1) — план погоджено оператором
Дві речі в одній зоні `#sh-network` (обидві — те, що Codex «навигадував» у порту, оператор НЕ погоджував):

**(A) Crop плити 73px** — лого/гліф Фармастора лізе в край плитки картки пікера (device-скрін підтвердив). Це НЕ те саме, що P8.

**(B) «Всі мережі» → «Всі»-картка** — банер прибрати, зробити «Всі» першою карткою сітки (рішення оператора, лід-варіант).

**План (HTML/CSS перед JS, один арк):**
1. **Крок 1 (CSS/HTML) — crop.** Перенести лочені важелі стенду в плиту: (а) повернути множник `1.55` у scale-ланцюг плити (`.np-plate img`/`.np-glyph` зараз `npKMark×npScale`=чистий `k`, БЕЗ 1.55); (б) дати `NET_PICK_GLYPH` власні `width/height`; (в) звірити `padding` плити з `sgPad` стенду (порт зараз `--npSignPad:3%`). `contain` → box-відносно, впис зберігається 35px→73px. **Harness навколо реальної плити 73px** (гліф Фармастора + 2 растри, обидві теми) → device.
2. **Крок 2 (HTML/CSS) — «Всі»-картка.** Прибрати банер `.np-all` (HTML+CSS+лістенер). Додати першу картку сітки в мові `.np-card`: нейтральний «усі»-гліф, підпис «Всі мережі», без лічильника. `.is-sel` коли `S.net===''`.
3. **Крок 3 (JS) — рендер.** `renderNetworkPicker` вставляє «Всі»-картку першою в `npGrid`; клік-делегат ловить її → `selectNetwork('')`; зняти ВСІ згадки `npAll` (греп перед видачею). Виклики `updateNetBtn` НЕ чіпати.
4. **Крок 4 —** гейти + device на все.

**Якорі (grep-verified _s3):**
- `#sh-network` CSS-vars (plate 73px): р.**1221-1222**
- `.np-plate` р.**1233** · `.np-plate img` р.**1234** · `.np-glyph` р.**1235**
- `.np-all` CSS: р.~**1210-1217** · `.np-all-ic` р.1215
- `.np-all` HTML: р.**1461** · `#npSub` р.1460 · `#npGrid` р.1462
- `NET_PICK_SCALE` р.**2780** · `NET_PICK_GLYPH` р.**2783** (viewBox 0 0 24 24, БЕЗ w/h) · `NET_PICK_DURI` р.2784
- `networkPlate(net)` р.**2803** · `networkCard(net)` р.**2808**
- `renderNetworkPicker` р.**2817** · sub.textContent р.2819 · npAll.innerHTML р.**2821** · grid.innerHTML р.**2823**
- `selectNetwork` р.**2824** · npAll listener р.**2828** · npGrid delegate р.**2829**
- **Стенд:** `.mini` р.**208-210** (35px, `padding:calc(35px*sgPad/100)`, white bg, contain) · `.mini .bscale` р.**228** (`scale(1.55*kThis)`) · glyph/img build р.1476-1478.

### P8 — mini-mark netBtn (ОКРЕМИЙ БАТЧ, ПОТІМ)
**Переназвано:** P8 = ТІЛЬКИ тулбар-кнопка `netBtn` (35px `.ntile`), НЕ пікер. Іконка захардкоджена (статичний SVG р.1273), `updateNetBtn` (р.2795) чіпає лише aria-label. Треба: `updateNetBtn` перебудовує innerHTML плитки за `S.net`. Якорі: netBtn CSS р.**664-690**, HTML р.**1271-1273**, `updateNetBtn` р.**2795**. Робити ПІСЛЯ пікер-батчу.

### Успадковані
- **sh=23** device-чек (глибша тінь, реверс A65) — світла/OLED.
- **`@media(max-width:359px)`** — поза scope, NOT VERIFIED.
- **Device-чек Фармастор** після закриття батчів.

---

## §2 · FINDING ЦІЄЇ СЕСІЇ (повний текст — 14.29)

**F-crop (причина + лікування, не ре-бенч):** зсув лого в край плити пікера — порт-Codex викинув важіль `bScale 1.55` (плита рахує `npKMark×npScale`=чистий `k`, тоді як стенд рахував `1.55×kThis`), а `NET_PICK_GLYPH` не має `width/height` → інлайн-SVG розтягується під `overflow:hidden`. Плюс порт-фікс зменшив плиту `82→73` (APP_BUILD-коммент), що підсилило тісноту. **Лікування:** перенести лочені важелі стенду (множник 1.55 + власні габарити гліфа + звірка padding із sgPad), а НЕ переміряти заново. `contain` робить масштаб box-відносним, тож впис зберігається з 35px на 73px; **device підтверджує** (mark 224² на плиті vs mini 112² у стенді — різна роздільність асета, contain нормалізує).

**D-picker-vsi (design, locked, оператор погодив):** банер «Всі мережі» Codex-порту → замінити на «Всі»-картку першою в `npGrid` (мова `.np-card`, дзеркалить чіп «Всі» фільтра області). Банер `.np-all` (HTML р.1461, CSS ~1210-1217, лістенер р.2828) прибрати.

---

## §3 · УСПАДКОВАНИЙ БОРГ (= base, ПОЗА b32.1)
- **H3 A69:** 9 селекторів без auto-dark твіна (`.money.pos/.neg`, `.fa/.fb.pos/.neg`, `.kv`, `.about-logo`) — кандидат на окрему governance-сесію.
- **H2 tag-diff** — легітимні JS-літерали в шаблонах, = base, НЕ регрес.
- **H4** голі класи (`card, lbl, list, row`).

---

## §4 · НЕ ЧІПАТИ
kNets(16/16, всі PASS) · Р-46/EB · DATA · geometry картки/журналу · **.netbtn/.ntile 44/35 каркас (P8 — окремий батч)** · **tone.L** · topMatch · homeModel/visitModel · tierForBrand · **виклики `updateNetBtn`** · **sh=23 (свідомий реверс, НЕ відновлювати sh12)**.
**Дозволено в цьому батчі:** `.np-plate/.np-glyph/.np-plate img` scale+padding+glyph-габарити (Крок 1); `.np-all`→`.np-card`-«Всі», `renderNetworkPicker`, npGrid-делегат, прибрати npAll (Кроки 2-3).

---

## §5 · PASTE-READY СТАРТ ДЛЯ НОВОГО ЧАТУ

```
Мова — українська. StockCheck b32.1. План пікер-рework ПОГОДЖЕНО, код не почато. Наступне — Крок 1 (crop плити, HTML/CSS).

СТАРТ (wsd 1.1): Lens_INDEX.md → це самері (StockCheck_session_summary_b32_1_s4_PICKER_REWORK_PLAN.md, §1 зверху) → Work_Standard.md → cookbook том (торкається iOS/UI).

ФАЙЛ-БАЗА: StockCheck_port_b32_1_s3_O48.html. Грепати точково, НЕ вантажити цілком. НЕ грепати APP_BUILD р.2574 і НЕ грепати блок NET_ASSECT base64 (величезний — роздуває контекст).

БАТЧ = дві речі в зоні #sh-network: (A) crop плити 73px — перенести важелі стенду (множник 1.55 у scale + власні w/h гліфу NET_PICK_GLYPH + звірка padding із sgPad), harness 73px обидві теми → device; (B) «Всі мережі» банер прибрати → «Всі»-картка першою в npGrid. Деталі, якорі, finding F-crop/D-picker-vsi — §1/§2 самері.

P8 (netBtn mini-mark, 35px .ntile) — ОКРЕМИЙ батч ПОТІМ, не плутати з пікером.

ЦИКЛ: план → мікроскоп → підтвердження → код. HTML/CSS перед JS. Device — фінальний арбітр. Стенд StockCheck_netmark_stagebench_v3_7.html читати ТОЧКОВО (.mini р.208-210, .mini .bscale р.228). Перед видачею: python3 Lens_validate.py --html <файл>.

НЕ ЧІПАТИ: kNets 16/16 · R-46/EB · DATA · geometry · .netbtn/.ntile каркас (P8) · tone.L · topMatch · виклики updateNetBtn · sh=23.

МАРКЕР НАВАНТАЖЕННЯ — жорстко останнім рядком КОЖНОЇ відповіді (wsd 1.2), дубль у question віджета ask_user_input_v0.
```
