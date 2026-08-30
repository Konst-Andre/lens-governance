# StockCheck b32.1 — session summary (Крок 1+2 ЗАКРИТО · О-48 + P8 відкриті)

> **живе доки:** до закриття **О-48** (region-scope пікер) і **P8** (mini-mark) у b32.1 з device-верифікацією; після — архів.
> Джерело правди коду — файл, не це самері (wsd 12.1). Рядки-якорі можуть зсунутись — грепати наживо.

---

## §0 · СТАН ФАЙЛІВ

- **Робоча копія (жива):** `StockCheck_port_b32_1_s2.html` — Крок 1+2 внесено, **gate-clean**, штамп `v2.25.0 / stockcheck-pwa.b32.1 / 10.08.2026`.
- **Source-порт:** `StockCheck_port_b32_0_Codex.html` (звідки почали; 810 КБ, ніколи не вантажити цілком — грепати).
- **Гейт:** `Lens_validate.py` НЕ на диску Project → тягнеться з raw:
  `https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/kernel/Lens_validate.py`
  Перед видачею: `python3 Lens_validate.py --html <файл>`.

---

## §1 · ВІДКРИТІ ПИТАННЯ (зверху = наступне)

### О-48 — region-scope пікер мереж (НОВЕ · correctness · ПРІОРИТЕТ 1)
**Баг:** `renderNetworkPicker()` (р.2818) робить `NETS.map(networkCard)` — малює **всі 16** мереж застосунку незалежно від області.
**Треба:** показувати лише мережі з ≥1 аптекою в `S.area`. Дніпро → БЕЗ Зайцева / Тріоль / Ліки Полтавщини / Центральна аптека (вони тільки в Полтаві). Те саме для Кіровоградської. Показ мережі, якої нема в регіоні = обман користувача.
**«Всі мережі» = всі В ЦІЙ ОБЛАСТІ**, не в усьому застосунку.
→ підхід зафіксовано у §3.

### P8 — mini-mark обраної мережі (косметика · ПРІОРИТЕТ 2)
mini-mark обраної мережі всередині `.ntile` (кнопка netBtn) через `updateNetBtn` (р.2791). JS+HTML. Детально ще НЕ спланований — потрібен греп структури netBtn + `updateNetBtn`. Оператор підтвердив: робити обов'язково.

### Успадковані (з PORTFIX-самері)
- **sh device-чек:** тепер **sh=23** (глибша тінь, РЕВЕРС A65-recess) — звірити на device, чи картка не «висить» над нішею на світлій; чи tone120-заглибленість читається на OLED.
- **`@media(max-width:359px)`** — поза scope, **NOT VERIFIED**.
- **Device-чек Фармастор** після закриття всіх кроків b32.1.

---

## §2 · ЗРОБЛЕНО ЦЮ СЕСІЮ (locked)

### Крок 1 — CSS (P1–P5) ✓
| P | зміна | якір |
|---|---|---|
| P1 | `--npPlate` 82→**73**px | р.1221 |
| P2 | знято `min-height:162px` (cardH natural ≈**144.3**) | р.1228 |
| P3 | `--npWellH` fallback 374→**339**px (переміряється рантайм `measureNetworkWell`) | р.1223 |
| P4 | light shadow sh16→**sh23** = `0 3.8px 10.5px rgba(20,50,42,.209)` | р.1230 |
| P5 | `--npWellBg`=**tone120** `color-mix(#000 20%,--bg)`, dark **+** auto-dark твін (A69) | після 1239 / 1245 |

**⚠ P4 — важливо для наступних сесій:** sh=23 — це **свідомий реверс** плану D6 (sh12) і §5-device-лока (MAT.L=sh12) і матеріального A65-recess-винятку. Рішення оператора цієї сесії. **§5-лок sh12 СКАСОВАНО, чинне sh23** (pending device). НЕ «відновлювати» sh12 як «помилку».
Формула стенду (light): `0 (sh/6)px (sh/2.2)px rgba(20,50,42, sh/110)`.
Dark-гілка shadow = `none` (A45, OLED). P4 чіпнув ЛИШЕ light-рядок.

### Крок 2 — JS + build (P6–P7) ✓
- **P6** region-reset (р.2905, гілка `data-area`): при зміні області `S.net=''` + `saveNet()` + `updateNetBtn()` перед ре-рендером → netBtn показує «Всі мережі», журнал = всі аптеки нової області. Гілки city (р.2912) / filter (р.2908) НЕ чіпано (місто звужує в межах області; статус ортогональний).
- **P7** штамп `v2.25.0 / stockcheck-pwa.b32.1 / 10.08.2026` + повний b32.1-changelog у коментарі APP_BUILD (історія b32.0 збережена). **ver БАМПНУТО:** region-reset — user-visible, Р-35 незастосовний.

**Гейти обох кроків:** H1 `node --check` ✓✓. H2/H3 дельти = **0** проти base Codex (доведено diff-прогоном).

---

## §3 · ПЛАН О-48 (зафіксований підхід, ще НЕ код)

1. helper `netsOf(area)` — distinct `p.net` серед `PH` де `p.area===area`. **Дзеркало `citiesOf(a)`** (р.2732).
2. у `renderNetworkPicker` (р.2818): `NETS.filter(n => scope.indexOf(n.net)>=0).map(networkCard)` замість `NETS.map(networkCard)`, де `scope=netsOf(S.area)`.
3. **fallback:** порожня/невідома область (scope порожній) → показати **всі** NETS (щоб не спорожнити пікер).
4. **caveat для мікроскопа:** перевірити `networkCard` (р.2804) — якщо картка показує лічильник, він має бути **обласний**, НЕ app-wide `networkTotal(n)` (р.2797, рахує PH.filter p.net===n по всьому застосунку).
5. wellH адаптується сам (`measureNetworkWell` rAF) — менше карток НЕ конфліктує з P3.
6. Цикл: план → мікроскоп-дельта окремим блоком → підтвердження → код (HTML/CSS перед JS). Device — фінальний арбітр.

**Порядок b32.1:** О-48 (correctness) → P8 (mini-mark) → device-чек усього → канонізація.

---

## §4 · ЯКОРІ (grep-verified у _s2; рядки орієнтовні)

- `renderNetworkPicker` р.2813–2818 · `NETS.map(networkCard)` р.**2818** ← точка правки О-48
- `networkCard(net)` р.2804 · `networkTotal(n)` р.2797 · `netLabel(n)` р.2782
- `citiesOf(a)` р.2732 (патерн для `netsOf`) · `AREA_ORDER` р.2723 · `AREAS` р.2724
- PH-запис має **`p.net`** (р.2797 доводить) · `p.area` · `p.city`
- area-handler (вже з region-reset) р.2905 · `updateNetBtn` р.2791 · `saveNet` р.2790
- `selectNetwork` р.2819 · `openNetworkPicker` р.2822 · `APP_BUILD` р.2574

---

## §5 · НЕ ЧІПАТИ
kNets(16/16) · Р-46/EB · DATA · geometry картки/журналу · P1L · `.netbtn` база · **tone.L** · topMatch-логіка · homeModel/visitModel · `m:2+i*83` · tierForBrand.

---

## §6 · УСПАДКОВАНИЙ БОРГ (виявив гейт цієї сесії — ПОЗА b32.1)
- **H3 A69:** 9 селекторів без auto-dark твіна — `.money.pos/.neg/.fa.pos/.fa.neg/.fb.pos/.fb.neg`, `.kv`, `.about-logo` (журнал/about-екран). Хардкод-значення течуть у auto-light. **Кандидат на окрему governance/фікс-сесію.**
- **H2 tag-diff** (div 172/171 · span 194/192 · a 4/3) — легітимні JS-літерали в шаблонах, = base Codex, НЕ регрес.
- **H4** голі класи без префікса: `card, lbl, list, row` (ризик колізії, b26_1 §4).

---

## §7 · PASTE-READY СТАРТ ДЛЯ НОВОГО ЧАТУ

```
Мова — українська. Продовжуємо StockCheck b32.1. Наступне — О-48 (region-scope пікер мереж), потім P8 (mini-mark).

СТАРТ (wsd 1.1): Lens_INDEX.md → це самері (StockCheck_session_summary_b32_1_s1s2_DONE_O48_NEXT.md, відкриті зверху) → Work_Standard.md → cookbook том за індексом (якщо торкається iOS/PWA/UI).

ФАЙЛ-ЦІЛЬ: StockCheck_port_b32_1_s2.html (Крок 1+2 вже внесено, gate-clean, штамп v2.25.0/b32.1/10.08.2026). Грепати точково, НЕ вантажити цілком. Source-порт: StockCheck_port_b32_0_Codex.html.

ДЖЕРЕЛО ПРАВДИ — репо (Lens_INDEX §0/§8): github.com/Konst-Andre/lens-governance → kernel/ · products/ · archive/. Lens_validate.py НЕ на диску — тягнути з raw.githubusercontent.com/Konst-Andre/lens-governance/main/kernel/Lens_validate.py.

ЦИКЛ (wsd 1.5+1.9): план → МІКРОСКОП ПЛАНУ окремим видимим блоком → підтвердження → код. HTML/CSS перед JS. Device — фінальний арбітр. Без «заодно поправив».

ЗАДАЧА О-48 (correctness, пріоритет 1): пікер мереж показує всі 16 незалежно від області — має показувати ЛИШЕ мережі з ≥1 аптекою в S.area. Дніпро без Зайцева/Тріоль/Ліки Полтавщини/Центральна аптека. «Всі мережі» = всі в області.
Підхід (зафіксований, див. §3 самері): helper netsOf(area) дзеркалом citiesOf(р.2732) → у renderNetworkPicker(р.2818) NETS.filter(scope).map(networkCard) замість NETS.map. Fallback: порожня область → всі NETS. Caveat: лічильник у networkCard(р.2804) має бути обласний, не app-wide networkTotal(р.2797).

ЗАФІКСОВАНІ РІШЕННЯ ЦІЄЇ СЕСІЇ (див. §2):
· Крок 1 CSS: plate 73 · знято min-height:162 · wellH fallback 339 · light shadow sh23 (0 3.8px 10.5px .209 — РЕВЕРС A65, §5-лок sh12 СКАСОВАНО, НЕ відновлювати) · dark+auto-dark --npWellBg tone120.
· Крок 2: region-reset р.2905 (S.net='' при зміні області) · бамп v2.25.0/b32.1/10.08.

НЕ ЧІПАТИ: kNets(16/16) · Р-46/EB · DATA · geometry · tone.L · topMatch · .netbtn база.
Перед видачею: python3 Lens_validate.py --html <файл>.

МАРКЕР НАВАНТАЖЕННЯ — жорстко останнім рядком КОЖНОЇ відповіді (wsd 1.2), дубль у question віджета ask_user_input_v0.
```
