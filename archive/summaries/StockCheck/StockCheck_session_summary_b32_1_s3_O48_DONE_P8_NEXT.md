# StockCheck b32.1 — session summary (О-48 ЗАКРИТО · P8 mini-mark відкрито)

> **живе доки:** до закриття **P8** (mini-mark netBtn) у b32.1 з device-верифікацією; після — device-чек усього + канонізація, тоді архів.
> Джерело правди коду — файл, не це самері (wsd 12.1). Рядки-якорі можуть зсунутись — грепати наживо.

---

## §0 · СТАН ФАЙЛІВ

- **Робоча копія (жива):** `StockCheck_port_b32_1_s3_O48.html` — О-48 внесено, **gate-clean по суті**, штамп `v2.25.0 / stockcheck-pwa.b32.1 / 10.08.2026` (НЕ бампнуто — див. §2).
- **Попередня база:** `StockCheck_port_b32_1_s2.html` (звідки почали цю сесію).
- **Гейт:** `Lens_validate.py` НЕ на диску → raw `https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/kernel/Lens_validate.py`. Перед видачею: `python3 Lens_validate.py --html <файл>`.
- **node --check:** `.html` напряму не бере — витягати inline `<script>` у `/tmp/*.js`, тоді `node --check`.

---

## §1 · ВІДКРИТІ ПИТАННЯ (зверху = наступне)

### P8 — mini-mark обраної мережі в netBtn (косметика/correctness UI · ПРІОРИТЕТ 1 зараз)
**Баг (оператор підтвердив наживо):** маленька іконка в кнопці мережі захардкоджена і показує «Фармастор» незалежно від вибору.
**Корінь:** видима іконка — статичний SVG у HTML (р.**1273**): `.ntile > .bscale > svg` = `NET_PICK_GLYPH`-ланцюжок, stroke `--ntile-gl`. `updateNetBtn()` (р.**2795**) переписує ЛИШЕ `aria-label`, сам SVG не чіпає → застиг. Фармастор — ЄДИНА мережа з `kind:'glyph'` і той самий ланцюжок → застиглий дефолт візуально = Фармастор.
**Треба:** `updateNetBtn()` має ще й перебудовувати `innerHTML` плитки за `S.net`:
- `S.net===''` → нейтральний ланцюжок (поточний дефолт, «Всі мережі»);
- `S.net` задано → mark обраної мережі: знайти `net` у NETS за `S.net`, рендерити лого — растр `NET_ASSETS[slug].mark` (`<img>`) або кольоровий гліф (`kind:'glyph'`, `NET_PICK_GLYPH.replaceAll('NET_INK',color)`).

**План P8 (ще НЕ код — потрібен bench + device):**
1. **Bench обов'язковий** (правило П-7, порт без harness заборонено): растрове лого 35px — чи читається? scale/crop у плитці `.ntile` (35×35, `.bscale` scale 1.55)? обидві теми (світла/OLED)? Гліф-нети (Фармастор) — колір на плитці. Донор геометрії — існуюча `.ntile` + `networkPlate` з пікера.
2. **Helper mini-mark:** окрема функція `netTileMark(net)` — рендерить mark під геометрію ntile (НЕ `networkPlate`: той має білий фон/бордер/padding пікера, не пасує 35px плитці). Гліф → кольоровий SVG; растр → `<img>` з `NET_PICK_DURI+asset.mark`, вписаний object-fit:contain.
3. **updateNetBtn перебудова:** після aria-label — `var tile=b.querySelector('.ntile'); tile.innerHTML = S.net ? netTileMark(netObjOf(S.net)) : DEFAULT_NTILE_GLYPH;` (винести дефолтний ланцюжок у const, щоб не дублювати з HTML).
4. **Виклики updateNetBtn:** уже стоять у `selectNetwork` (р.2824), area-handler (р.2910), init (р.3757) — mini-mark оновиться автоматично на кожному з них.
5. **Мікроскоп 5 осей + device-арбітр** перед канонізацією.

**Якорі P8 (grep-verified у _s3):**
- netBtn HTML: р.**1271-1273** (`.netbtn > .ntile > .bscale > svg`)
- `.ntile` CSS: р.**673-690** (35px, `.bscale` scale 1.55, `--ntile-gl` світла/dark/auto-dark)
- `.netbtn` CSS: р.**664** (44px)
- `updateNetBtn`: р.**2795** · IIFE-клік: р.**2711**
- `networkPlate(net)`: р.**2803** (донор рендеру mark) · `NET_PICK_GLYPH`: р.~2779 · `NET_PICK_DURI`: р.~2780 · `NET_ASSETS[slug].mark`: у `nets_assets_v2.js` (inline у білді)
- `NETS[]` (пошук net-об'єкта за ключем): р.~2753 · `netLabel(n)`: р.2782

### Успадковані (з попередніх самері)
- **sh device-чек:** sh=23 (глибша тінь, реверс A65) — звірити на device (світла: чи не «висить» над нішею; OLED: tone120-заглибленість).
- **`@media(max-width:359px)`** — поза scope, NOT VERIFIED.
- **Device-чек Фармастор** після закриття P8.

---

## §2 · ЗРОБЛЕНО ЦЮ СЕСІЮ (О-48 · locked)

**О-48 — region-scope пікер мереж (correctness) ✓** у `StockCheck_port_b32_1_s3_O48.html`. Три правки, всі JS, HTML/CSS не чіпано (diff довів рівно 4 змінені блоки, жодного «заодно»):

| # | правка | якір (s3) |
|---|---|---|
| 1 | helper `netsOf(a)` — distinct `p.net` де `p.area===a`; дзеркало `citiesOf` БЕЗ sort (порядок задає NETS.filter) | після р.2733 (нова р.~2737) |
| 2a | `networkTotal(n,a)` — параметризовано опційною областю: `p.net===n&&(!a||p.area===a)`; зворотно-сумісно | р.**2801** |
| 2b | у `networkCard` лічильник → `networkTotal(net.net,S.area)` (обидва виклики) — збіг із `topMatch` (який завжди відсіює `m.area!==S.area`) | р.**2811** |
| 3 | у `renderNetworkPicker`: `scope=netsOf(S.area)`; `(scope.length?NETS.filter(...):NETS).map(networkCard)` — лише мережі області, fallback порожня→всі | р.**2822-2823** |

**Замір (node на живому PH):** Дніпро 16→**12** (мінус Дорра-Груп/Ліки Полтавщини/Тріоль/Зайцева) · Полтава→**13** · Кіровоградська→**7** · порожня область→**16** (fallback) · лічильник 9-1-1 у Дніпрі **90** (був app-wide 196) · порядок карток зберігає NETS-реєстр.

**Гейти:** H1 `node --check` ✓✓. H2 (div 172/171 · span 194/192 · a 4/3), H3 (A69 9 селекторів), H4 (голі класи) — **успадкований борг = base** (§3), НЕ введено О-48 (diff-доведено).

**ver НЕ бампнуто:** О-48 — correctness у тому ж b32.1-арку, ще не деплой/канонізація. Штамп і changelog APP_BUILD (р.2574) правити на канонізації після P8+device (щоб не множити ризикові правки APP_BUILD мід-арк).

---

## §3 · УСПАДКОВАНИЙ БОРГ (= base, ПОЗА b32.1)
- **H3 A69:** 9 селекторів без auto-dark твіна — `.money.pos/.neg/.fa.pos/.fa.neg/.fb.pos/.fb.neg`, `.kv`, `.about-logo`. Кандидат на окрему governance-сесію.
- **H2 tag-diff** (div 172/171 · span 194/192 · a 4/3) — легітимні JS-літерали в шаблонах, = base, НЕ регрес.
- **H4** голі класи: `card, lbl, list, row` (ризик колізії, b26_1 §4).

---

## §4 · НЕ ЧІПАТИ
kNets(16/16) · Р-46/EB · DATA · geometry картки/журналу · `.netbtn` база (44px) · **tone.L** · topMatch-логіка · homeModel/visitModel · `m:2+i*83` · tierForBrand · **sh=23 (свідомий реверс, НЕ відновлювати sh12)**.
**P8-виняток:** `.ntile` innerHTML і `--ntile-gl`/геометрію плитки чіпати МОЖНА (це і є задача P8); `.netbtn` 44px-каркас — ні.

---

## §5 · PASTE-READY СТАРТ ДЛЯ НОВОГО ЧАТУ

```
Мова — українська. Продовжуємо StockCheck b32.1. О-48 ЗАКРИТО. Наступне — P8 (mini-mark netBtn).

СТАРТ (wsd 1.1): Lens_INDEX.md → це самері (StockCheck_session_summary_b32_1_s3_O48_DONE_P8_NEXT.md, відкриті зверху) → Work_Standard.md → cookbook том за індексом (P8 торкається iOS/UI — том потрібен).

ФАЙЛ-ЦІЛЬ: StockCheck_port_b32_1_s3_O48.html (О-48 внесено, gate-clean, штамп v2.25.0/b32.1/10.08.2026, ver НЕ бампнуто). Грепати точково, НЕ вантажити цілком. НЕ грепати рядок APP_BUILD р.2574 (гігантський коментар — роздуває контекст).

ДЖЕРЕЛО ПРАВДИ — репо (Lens_INDEX §0/§8). Lens_validate.py з raw.githubusercontent.com/Konst-Andre/lens-governance/main/kernel/Lens_validate.py. node --check: витягати inline script у /tmp/*.js, .html напряму не бере.

ЦИКЛ (wsd 1.5+1.9): план → МІКРОСКОП ПЛАНУ окремим блоком → підтвердження → код. HTML/CSS перед JS. Device — фінальний арбітр. Порт без bench заборонено (П-7).

ЗАДАЧА P8 (mini-mark, пріоритет 1): маленька іконка в netBtn захардкоджена (статичний SVG р.1273), показує Фармастор незалежно від вибору. updateNetBtn (р.2795) чіпає лише aria-label. Треба: updateNetBtn перебудовує innerHTML плитки .ntile за S.net — обрана мережа → її mark (растр NET_ASSETS[slug].mark або кольоровий гліф), S.net='' → нейтральний ланцюжок. Bench обов'язковий: читабельність лого 35px, scale/crop, обидві теми, гліф-колір. Детальний план — §1 самері.

НЕ ЧІПАТИ: kNets(16/16) · Р-46/EB · DATA · geometry · tone.L · topMatch · .netbtn база 44px · sh=23. P8-виняток: .ntile innerHTML/геометрію можна.

Перед видачею: python3 Lens_validate.py --html <файл>.

МАРКЕР НАВАНТАЖЕННЯ — жорстко останнім рядком КОЖНОЇ відповіді (wsd 1.2), дубль у question віджета ask_user_input_v0.
```
