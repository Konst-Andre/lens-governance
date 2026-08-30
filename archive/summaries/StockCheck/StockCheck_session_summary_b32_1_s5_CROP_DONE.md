# StockCheck b32.1 — session summary (s5 · CROP-фікс Фармастора ЗАКРИТО на device)

> **живе доки:** до закриття батчу пікер-рework (лишились Крок 2-3 «Всі»-картка) у b32.1. Після — P8 (netBtn mini-mark) → device на все → канонізація.
> Джерело правди коду — файл, не це самері (wsd 12.1). Якорі р.XXXX grep-verified у `_s5`, можуть зсунутись — грепати наживо.

---

## §0 · СТАН ФАЙЛІВ

- **База батчу (жива):** `StockCheck_port_b32_1_s5_cropfix.html` — crop-фікс Фармастора внесено, device ✓, штамп `v2.25.0 / stockcheck-pwa.b32.1 / 10.08.2026` (ver НЕ бампнуто).
- **Стенд (лочені важелі, читати точково):** `StockCheck_netmark_stagebench_v3_7.html`.
- **Handoff:** `StockCheck_B32_STAGEBENCH_HANDOFF.md` (⚠ §7 FARMASTOR Required 1.35 — ЗАСТАРІВ, див. техборг).
- **Гейт:** raw `https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/kernel/Lens_validate.py`. Прогін s5: node ✓, H2 тотожний s3 (нуль нових тегів), решта ⚠/✗ = борг §3.

---

## §1 · ВІДКРИТІ ПИТАННЯ (зверху = наступне)

### ЗАЛИШОК ПІКЕР-РEWORK — Крок 2-3: «Всі мережі» банер → «Всі»-картка (D-picker-vsi, оператор погодив)
Crop (Крок 1) ЗАКРИТО. Лишилось з плану s4:
- **Крок 2 (HTML/CSS):** прибрати банер `.np-all` (HTML р.~1461, CSS ~1210-1220, лістенер р.~2828). Додати першу картку сітки в мові `.np-card`: нейтральний «усі»-гліф, підпис «Всі мережі», без лічильника. `.is-sel` коли `S.net===''`.
- **Крок 3 (JS):** `renderNetworkPicker` (р.~2817) вставляє «Всі»-картку першою в `npGrid`; клік-делегат (р.~2829) ловить її → `selectNetwork('')`; зняти ВСІ згадки `npAll` (греп перед видачею). Виклики `updateNetBtn` НЕ чіпати.
- Якорі грепати наживо в `_s5` (зсув після crop-правок мінімальний — CSS +2 рядки біля 1235).

### P8 — mini-mark netBtn (ОКРЕМИЙ БАТЧ, ПОТІМ)
`netBtn` тулбар (35px `.ntile`), іконка статичний SVG р.~1273, `updateNetBtn` (р.~2795) чіпає лише aria. Треба: `updateNetBtn` перебудовує innerHTML плитки за `S.net`. Робити ПІСЛЯ пікер-батчу.

### ТЕХБОРГ, знайдений у s5 (окремими ходами)
- **padding-баг плити:** `.np-plate` (р.1233) має `padding:calc(var(--npPlate) * var(--npSignPad))`, а `--npSignPad:3%` (р.1221) — тобто `calc(73px * 3%)` = **невалідний CSS calc** (множення length×percentage заборонене) → padding резолвиться в **0**. Стенд робить правильно: `.plate` (стенд р.155) = `calc(plate * sgPad / 100)`, `--sgPad:3` (**число**) = 2.19px. Зараз ПРИХОВАНИЙ (гліф зменшено, не впирається в край), але плити не мають задуманого канта. **Фікс окремим ходом:** `--npSignPad:3%`→`3` + формула `calc(var(--npPlate) * var(--npSignPad) / 100)` (дзеркало стенду 1:1). Зачепить усі плити.
- **handoff §7 застарів:** «FARMASTOR Required 1.35 = PASS» — на device 1.35 роздував (лізло). Ревізовано → **1.05** (з glyph w/h 62%). §7 таблиця для цього рядка більше не істина.

### Успадковані
- **sh=23** device-чек (реверс A65) — світла/OLED.
- **`@media(max-width:359px)`** — поза scope, NOT VERIFIED.
- **Device-чек Фармастор** решта екранів після закриття батчів.

---

## §2 · FINDING ЦІЄЇ СЕСІЇ (повний текст — 14.29)

**F-glyph-crop (справжня причина, device-locked):** Фармастор має `kind:'glyph'` (р.2769) — рендериться через `NET_PICK_GLYPH` (р.2783, зелений заокруглений плюс `#0A8336`), НЕ растр. Порт-`NET_PICK_GLYPH` — inline `<svg viewBox="0 0 24 24">` **без атрибутів width/height**; у боксі `.np-glyph{width:100%;height:100%;display:grid}` (р.1235) SVG без габаритів WebKit розкладає на ~весь бокс → плюс `scale(npScale 1.35)` доштовхує за край. Стенд `plateHTML` glyph-гілка (р.1232-34) навмисно дає `width/height=round(sz*.62)` (62% плити) — тому на стенді Фармастор вписаний.
**Лікування (device ✓):** CSS `#sh-network .np-glyph svg{width:62%;height:62%}` (box-відносно, впис однаковий 35→73px; зачіпає ЛИШЕ Фармастор — єдина `kind:'glyph'` з 16) + `NET_PICK_SCALE.FARMASTOR 1.35→1.05` (device: 0.95 виявився замалий, 1.05 — як сусіди).
**Хибні сліди, спалені в цій сесії (щоб не вертатись):**
1. «повернути множник **1.55**» (F-crop s4) — ХИБНИЙ: 1.55 живе на `.bscale` (р.221/228), тобто на mini/netBtn **еталонах-порівняння** S2-iso стенду. Плита стенду `.plate img/.glyphwrap` (р.164-169) рахує `kMark(1.00)×kThis` — 1.55 у ній нема ніколи. Ставити `npKMark:1.55` = роздути в 1.55× = регрес.
2. «плита 73 vs 82» — реальний конфлікт handoff §214, але НЕ причина цього crop (дельта 6%, а спостерігали ~40%).
3. «padding=0» — реальний баг (див. техборг), але для glyph-crop другорядний (2px не дають 40% дельти).
Справжня дельта 40% = glyph w/h (62% vs ~100%). Урок: `grep kind:` до діагнозу — самурі s4 називало Фармастор і «лого» (натяк на растр), а він glyph.

---

## §3 · УСПАДКОВАНИЙ БОРГ (= base, ПОЗА b32.1)
- **H3 A69:** 9 селекторів без auto-dark твіна (`.money.pos/.neg`, `.fa/.fb.pos/.neg`, `.kv`, `.about-logo`) — окрема governance-сесія.
- **H2 tag-diff** — легітимні JS-літерали (s5 тотожний s3), НЕ регрес.
- **H4** голі класи (`card, lbl, list, row`).

---

## §4 · НЕ ЧІПАТИ
kNets(15/16 raster PASS) · Р-46/EB · DATA · geometry картки/журналу (plate=73, §226 не рушено) · `.netbtn/.ntile` каркас (P8 окремо) · tone.L · topMatch · homeModel/visitModel · виклики `updateNetBtn` · sh=23.
**Device-locked у s5 (не вертати):** `#sh-network .np-glyph svg{62%/62%}` · `NET_PICK_SCALE.FARMASTOR=1.05`.

---

## §5 · PASTE-READY СТАРТ ДЛЯ НОВОГО ЧАТУ

```
Мова — українська. StockCheck b32.1. Crop Фармастора ЗАКРИТО на device (s5). Наступне — Крок 2-3 пікер-рework: банер «Всі мережі» → «Всі»-картка першою в npGrid.

СТАРТ (wsd 1.1): Lens_INDEX.md → це самері (StockCheck_session_summary_b32_1_s5_CROP_DONE.md, §1 зверху) → Work_Standard.md точково → cookbook том точково (торкається UI).

ФАЙЛ-БАЗА: StockCheck_port_b32_1_s5_cropfix.html. Грепати точково, НЕ вантажити цілком. НЕ грепати APP_BUILD і блок NET_ASSETS base64.

БАТЧ = Крок 2-3 (D-picker-vsi, оператор погодив): прибрати банер .np-all (HTML/CSS/лістенер, зняти всі npAll — греп), додати «Всі»-картку першою в npGrid (мова .np-card, нейтральний гліф, підпис «Всі мережі», без лічильника, .is-sel коли S.net===''). renderNetworkPicker вставляє її першою; делегат npGrid → selectNetwork(''). Виклики updateNetBtn НЕ чіпати. Деталі/якорі — §1 самері.

ТЕХБОРГ (окремими ходами, не плутати): (1) padding-баг .np-plate calc(73px*3%)→0, фікс = --npSignPad 3%→3 + /100; (2) handoff §7 FARMASTOR застарів → 1.05. Повний текст — §1/§2 самері.

P8 (netBtn mini-mark, 35px .ntile) — ОКРЕМИЙ батч ПОТІМ.

ЦИКЛ: план → мікроскоп (5 осей) → підтвердження → код. HTML/CSS перед JS. Device — фінальний арбітр. grep kind:/значення наживо ДО діагнозу (урок s5: Фармастор — kind:glyph, не растр). Перед видачею: python3 Lens_validate.py --html <файл>.

НЕ ЧІПАТИ: kNets · R-46/EB · DATA · geometry (plate=73) · .netbtn/.ntile каркас (P8) · tone.L · topMatch · виклики updateNetBtn · sh=23 · glyph svg 62% + FARMASTOR 1.05 (device-locked s5).

МАРКЕР НАВАНТАЖЕННЯ — жорстко останнім рядком КОЖНОЇ відповіді (wsd 1.2), дубль у question віджета ask_user_input_v0.
```
