> живе доки: назавжди (вічне, wsd 1.8) — рецепт регенерації template, переживає окремі батчі

# QR Lens — Export Contract (template-build recipe)

**Версія:** v1.1 (31.07.2026 — §4 парс адреси переписано під новий формат KPI-файлу) · **Виведено з:** `QR_Lens___html_export.xlsm` (VBA `ExportModule`/`Module1`) + `QR_Lens_preview_batch58_2.html`, 09.07.2026.
**Мета:** щоб регенерація HTML-template була 5-хвилинним грепом-за-рецептом, а НЕ повторним розслідуванням .xlsm щоразу. Читай цей файл замість того, щоб розпаковувати .xlsm і читати VBA заново.

> Generic-правила (HTML-first, regenerate-from-preview, DATA→placeholder) живуть у **wsd Кластер 6** — тут лише продукт-специфіка QR Lens. Якщо конфлікт — wsd головніший на процес, цей файл головніший на конкретику (імена/рядки/схему).

---

## 0. TL;DR — регенерація за 4 кроки

1. `cp <останній device✓ preview>.html  → QR_Lens_template_v2.html` (в outputs, 1.6).
2. Два свопи (нічого більше):
   - `const DATA = [ … ];`  →  `const DATA = /*__DATA__*/;`
   - `const EXPORT_DATE = "DD.MM.YYYY";`  →  `const EXPORT_DATE = /*__EXPORT_DATE__*/;`
3. Гейти: рівно 1×`/*__DATA__*/` + 1×`/*__EXPORT_DATE__*/`, нуль лишкових літералів, **UTF-8 без BOM**, tag-balance, node --check на симульованому інжекті.
4. Віддати `QR_Lens_template_v2.html`. **VBA НЕ чіпати**, якщо батч UI-only.

Решта файлу — розшифровка «чому саме так».

---

## 1. Топологія пайплайну

```
Excel (KPI-джерело) → Power Query → _QR_Data (ListObject "QR_Data")
        │
        │  VBA ExportModule.ExportToHTML
        ▼
  BuildQRJSON()  →  JSON-масив [ {SR}, … ]
        │
        │  ReadTextFile(QR_Lens_template_v2.html)   ← ТЕМПЛЕЙТ (наш deliverable)
        │  Replace("/*__DATA__*/",       json)
        │  Replace("/*__EXPORT_DATE__*/", "DD.MM.YYYY")
        ▼
   WriteTextFile(qr_lens.html)   ← фінальний застосунок (UTF-8, no BOM)
```

Template = останній **device✓** single-file preview, у якому два літерали замінені на дві мітки. Усе інше (CSS/JS/motion/material) template несе байт-у-байт із preview — тому UI-батчі їдуть у template **безкоштовно**, без роботи над VBA.

---

## 2. Незмінний контракт (durable — міняється рідко)

| Що | Значення | Джерело у VBA |
|----|----------|---------------|
| Ім'я темплейту | `QR_Lens_template_v2.html` | `Const TPL_NAME` |
| Ім'я виходу | `qr_lens.html` | `Const OUT_NAME` |
| Мітка даних | `/*__DATA__*/` | `Const PLACEHOLDER` |
| Мітка дати | `/*__EXPORT_DATE__*/` | `Const PH_DATE` |
| Формат дати | `"DD.MM.YYYY"` у лапках (VBA сам додає лапки) | `Format(Now,"DD.MM.YYYY")` |
| Кодування I/O | **UTF-8 без BOM** | `ADODB.Stream Charset="utf-8"` |
| Розташування | template лежить **у тій самій папці**, що й .xlsm | `wbPath & "\" & TPL_NAME` |

**ДВІ мітки, не одна.** Найлегша пастка: замінити тільки DATA і лишити дату-літерал. Тоді `Replace(html, PH_DATE, …)` не знайде мітку → **дата експорту замерзне** назавжди, freshness-крапка (B55 §2.6) рахуватиме вік від хибної дати. Обидві мітки обов'язкові.

**BOM.** VBA `ReadTextFile` читає як utf-8; якщо у template є BOM (EF BB BF), він потрапить у `<` перед `<!DOCTYPE` → бите перше правило/парс. Писати template завжди без BOM.

---

## 3. Цільові рядки у preview (де саме свопати)

У поточному коді (batch58_2) — дві прості одно-рядкові декларації в головному inline-`<script>`:

```js
const DATA = [{"n":"…", … }];          // ← увесь тест-масив, ~20KB, один рядок
const EXPORT_DATE = "26.05.2026";      // ← літерал дати
```

Грепи-якорі (мають дати рівно 1 збіг кожен):
- `^const DATA = \[`
- `^const EXPORT_DATE = "`

Якщо якір дає ≠1 — код переструктурували, перевір вручну перед свопом (grep-before-claim, wsd 12.1).

---

## 4. JSON-схема (що VBA емітить у DATA)

Масив SR-об'єктів. Порядок ключів — як у серіалізаторі (`SerializeSR`/`SerializeOutlet`):

```
SR      : { "n":str, "t":int, "ok":int, "w":int, "l":int, "c":int, "o":[outlet…] }
outlet  : { "a":str, "net":str, "city":str, "ok":int, "w":int, "l":int, "c":int, "i":[item…] }
item    : { "pos":str, "qr":str, "st":str, "d":str, "sk":int }
```

- `st` (статус item) нормалізується VBA (LCase): `ok` / `w|warn|warning`→w / `l|late`→l / `c|crit|critical`→c; будь-що інше → ok.
- `n` = ім'я SR без префікса `"PSR "` (`RemovePSRPrefix`).
- `city` = коротка назва міста, `a` = адреса ВІД міста включно (`ExtractCity` → `ShortAddress`).

**Парс адреси — v1.1 (31.07.2026).** `ExtractCity` = ОДИН патерн, якорений на `^`:

```
^(?:Україна,\s*)?(?:[^,]*обл\.,\s*)?(?:[^,]*р-н\.,\s*)?(м\.|смт\.|с\.|сел\.|пос\.|с-ще\s|селище\s)\s*([^,]+?)\s*,
```

Країна / область / район — **опційні** префікси; якір = перший маркер населеного пункту.
`ShortAddress` ріже все до знайденого `cityFull` — місто ЛИШАЄТЬСЯ в короткій адресі.
Промах парсера → `Array("","")` → `ShortAddress` вертає адресу як є (тихий фолбек, не виняток).

> **Чому переписано.** v1 мав два патерни, обидва прив'язані до `обл\.,`. У KPI-файлі
> від 28.07.2026 джерело перейшло на адмін-нарізку **району**: `Україна, Дніпровський р-н.,
> м.Дніпро, вул…` — без «обл.». Плюс з'явились типи `сел.` / `пос.`. Замір на 1888 унікальних
> адрес: **старий код 870 промахів, новий патерн 0**; місто на спільній множині збігається 1:1.
>
> **Детектор на майбутнє.** Симптом промаху подвійний і видимий у продукті: адреса в картці
> НЕ обрізана **І** зник підпис міста під мережею. Побачив обидва разом → джерело змінило формат
> адреси, дивитись сюди, не в HTML.

**Ключ точки:** `outletKey = network & "|" & shortAddr`. Зміна парсера = зміна ключів
для раніше-непарсених точок. Разова міграція, очікувана.

**Сортування (у JSON вже впорядковано):**
- SR — за іменем A→Я (`SortKeysAsc`).
- Outlets — за `minSK` ↑, потім адреса A→Я (`SortOutletsByCritThenName`).
- Items — за `sk` ↑, потім `pos` A→Я (`SortItemsBySKThenPos`).

**Vestigial `sk`:** VBA емітить `sk` на кожен item, але фронтенд його **не читає** (grep `.sk` у preview = 0). Це нешкідливе зайве поле (VBA використовує `sk`/`minSK` лише для власного сортування). Preview-тест-дані можуть його не містити — це ОК, схему не ламає.

---

## 5. Коли VBA (ExportModule) ТРЕБА міняти, а коли НІ

**НЕ треба** (більшість батчів — template-only регенерація):
- будь-які CSS/motion/material зміни;
- JS-логіка UI (селектори, анімації, стани), що читає ту саму DATA-схему;
- freshness/persist/about — усе, що не додає нового поля в DATA і не змінює мітки.

**Треба** міняти VBA, якщо:
- фронтенд починає **читати нове поле** item/outlet/SR → додати його у відповідний `Serialize*`;
- змінюється **мітка** чи їх кількість → синхронити `PLACEHOLDER`/`PH_DATE` + `Replace`-виклики + template;
- змінюється **джерело** (структура `_QR_Data`/PQ-колонки) → `COL_*` константи + `ReadLOData`.

Правило-детектор: перед регенерацією грепни у preview нові `DATA[i].<key>` / `.o[].<key>` / `.i[].<key>`, яких немає у схемі §4. Порожньо → VBA не чіпати.

## 5a. Ключові entry-points VBA (мапа, якщо все ж треба лізти)

| Sub/Func | Роль |
|----------|------|
| `ExportToHTML` | точка входу (кнопка «Експорт у HTML»): RefreshAll → BuildQRJSON → 2×Replace → write |
| `BuildQRJSON` | обхід `_QR_Data`, агрегація в SR→outlet→item, серіалізація |
| `SerializeSR` / `SerializeOutlet` | форма JSON (порядок ключів = §4) |
| `Sort*` | три сортування §4 |
| `ExtractCity`/`ShortAddress`/`RemovePSRPrefix`/`EscapeJSON` | парс/очистка полів (`ExtractCity` — v1.1, §4) |
| `ReadTextFile`/`WriteTextFile` | UTF-8 без BOM I/O |
| `Module1.*` | PickKPIFile, RefreshAllData, EnsureButtons (кнопки), OneShot_*Sheets |

---

## 6. Гейти регенерації (copy-paste чекліст)

```
1. grep -c '/\*__DATA__\*/'         == 1
2. grep -c '/\*__EXPORT_DATE__\*/'  == 1
3. grep -c 'const DATA = \['        == 0   (лишку немає)
4. grep -c '"DD.MM.YYYY стара"'     == 0   (стара дата-літерал прибрана)
5. BOM: head -c3 | od → НЕ efbbbf
6. tag-balance: script/style/div/span/button/svg парні
7. node --check на sim-інжекті: DATA→[], date→"01.01.2026" → PASS
8. розмір ≈ preview − (розмір DATA-масиву)
```

---

## 7. Провенанс / підтримка цього файлу

- Виведено з реального VBA (olevba на `QR_Lens___html_export.xlsm`) — не з пам'яті, не з summary (12.1).
- Якщо .xlsm/Excel колись зміниться (нове поле, нова мітка, інша схема) — оновити §2/§4/§5 і бампнути на v2. Дрейф виявляється грепом якорів §3 + детектором §5.
- Дзеркальний контракт для KPI Lens (якщо знадобиться) — окремий `KPI_Lens_export_contract_v1.md` за тим самим шаблоном (свій JSON-схема + `KPI_Lens_template_v2.html`).
