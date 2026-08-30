# KPI Lens — Категорії: імплементація в Excel (Batch 15)

> HTML готовий і зафіксований. Тепер Excel: **PQ → VBA**. Усе append-only, числа недоторкані.
> **Порядок: спершу PQ (+Refresh), потім VBA.** VBA-читання захищене `UBound`, тож не впаде навіть якщо запустиш до Refresh.

---

## КРОК 1 — Power Query (безпечно, без порпання)

Спосіб: вкладка запиту → **Home → Advanced Editor** → `Ctrl+A` (виділити все) → вставити мій код → **Done**. Заміняєш запит цілком — помилитись «не туди» неможливо.

### 1.1 Запит `Export_IMS_грн`
Відкрий його Advanced Editor, `Ctrl+A`, встав це:

```m
let
    Params   = Параметри,
    FilePath = Params[Файл_шлях],

    Source = Excel.Workbook(File.Contents(FilePath), null, true),
    Sheet  = Source{[Item="IMS",Kind="Sheet"]}[Data],

    FindHeader   = Table.Skip(Sheet, each ([Column1] <> "Area")),
    Headers      = Table.PromoteHeaders(FindHeader, [PromoteAllScalars=true]),
    CleanHeaders = Table.TransformColumnNames(Headers, Text.Trim),
    ColNames     = Table.ColumnNames(CleanHeaders),

    AnchorGuard = let a = List.PositionOf(ColNames, "Category IW")
                  in if a = -1
                     then error "Export_IMS: колонку 'Category IW' не знайдено."
                     else a,
    M1 = ColNames{AnchorGuard + 1},
    M2 = ColNames{AnchorGuard + 2},
    M3 = ColNames{AnchorGuard + 3},

    Renamed = Table.RenameColumns(CleanHeaders, {
        {ColNames{AnchorGuard - 1}, "Cat_OTC"}, {ColNames{AnchorGuard}, "Cat_IW"},
        {ColNames{AnchorGuard + 1}, "IW_1"},    {ColNames{AnchorGuard + 2}, "IW_2"},    {ColNames{AnchorGuard + 3}, "IW_3"},
        {ColNames{AnchorGuard + 4}, "OTC_1"},   {ColNames{AnchorGuard + 5}, "OTC_2"},   {ColNames{AnchorGuard + 6}, "OTC_3"},
        {ColNames{AnchorGuard + 7}, "Tests_1"}, {ColNames{AnchorGuard + 8}, "Tests_2"}, {ColNames{AnchorGuard + 9}, "Tests_3"}
    }),

    SuperClean = (txt) =>
        let
            t        = Text.From(txt),
            noSpaces = Text.Replace(t, Character.FromNumber(160), " "),
            trimmed  = Text.Trim(Text.Clean(noSpaces))
        in trimmed,

    CleanAll    = Table.TransformColumns(Renamed, {{"Outlet Address", SuperClean}}),
    DropEmptySR = Table.SelectRows(CleanAll,
                      each [SR] <> null and Text.Trim(Text.From([SR])) <> "" and [SR] <> "SR"),
    ValidSRs   = List.Buffer(SR_List[SR]),
    FilteredSR = Table.SelectRows(DropEmptySR, each List.Contains(ValidSRs, [SR])),                  

    Selected = Table.SelectColumns(FilteredSR, {
        "SR","Network","Outlet Address","City",
        "IW_1","IW_2","IW_3",
        "OTC_1","OTC_2","OTC_3",
        "Tests_1","Tests_2","Tests_3",
        "Cat_OTC","Cat_IW"
    }),
    Unpivoted = Table.UnpivotOtherColumns(Selected,
        {"SR","Network","Outlet Address","City","Cat_OTC","Cat_IW"}, "КатМісяць","Грн"),
    SplitCol = Table.SplitColumn(Unpivoted,"КатМісяць",
        Splitter.SplitTextByDelimiter("_", QuoteStyle.Csv),
        {"Категорія","Місяць_код"}),

    MonthLabel = Table.AddColumn(SplitCol, "Місяць_назва", each
        if   [Місяць_код] = "1" then M1
        else if [Місяць_код] = "2" then M2
        else M3),

    Final = Table.TransformColumnTypes(
        Table.SelectColumns(MonthLabel, {
            "SR","Network","Outlet Address","City",
            "Категорія","Місяць_назва","Грн",
            "Cat_OTC","Cat_IW"
        }),{{"Грн", type number}})
in
    Final
```

### 1.2 Запит `Export_Offtake_грн`
Те саме — його Advanced Editor, `Ctrl+A`, встав:

```m
let
    Params   = Параметри,
    FilePath = Params[Файл_шлях],

    Source = Excel.Workbook(File.Contents(FilePath), null, true),
    Sheet  = Source{[Item="Offtake",Kind="Sheet"]}[Data],

    FindHeader   = Table.Skip(Sheet, each ([Column1] <> "Area")),
    Headers      = Table.PromoteHeaders(FindHeader, [PromoteAllScalars=true]),
    CleanHeaders = Table.TransformColumnNames(Headers, Text.Trim),
    ColNames     = Table.ColumnNames(CleanHeaders),

    AnchorGuard = let a = List.PositionOf(ColNames, "Category IW")
                  in if a = -1
                     then error "Export_Offtake: колонку 'Category IW' не знайдено."
                     else a,
    RikStr = Text.End(Text.Trim(ColNames{AnchorGuard + 1}), 4),

    Renamed = Table.RenameColumns(CleanHeaders, {
        {ColNames{AnchorGuard - 1}, "Cat_OTC"}, {ColNames{AnchorGuard}, "Cat_IW"},
        {ColNames{AnchorGuard + 1}, "IW_Jan"},    {ColNames{AnchorGuard + 2}, "IW_Feb"},    {ColNames{AnchorGuard + 3}, "IW_Mar"},
        {ColNames{AnchorGuard + 4}, "OTC_Jan"},   {ColNames{AnchorGuard + 5}, "OTC_Feb"},   {ColNames{AnchorGuard + 6}, "OTC_Mar"},
        {ColNames{AnchorGuard + 7}, "Tests_Jan"}, {ColNames{AnchorGuard + 8}, "Tests_Feb"}, {ColNames{AnchorGuard + 9}, "Tests_Mar"}
    }),

    SuperClean = (txt) =>
        let
            t        = Text.From(txt),
            noSpaces = Text.Replace(t, Character.FromNumber(160), " "),
            trimmed  = Text.Trim(Text.Clean(noSpaces))
        in trimmed,

    CleanAll    = Table.TransformColumns(Renamed, {{"Outlet Address", SuperClean}}),
    DropEmptySR = Table.SelectRows(CleanAll,
                      each [SR] <> null and Text.Trim(Text.From([SR])) <> "" and [SR] <> "SR"),
    ValidSRs   = List.Buffer(SR_List[SR]),
    FilteredSR = Table.SelectRows(DropEmptySR, each List.Contains(ValidSRs, [SR])),                  

    Selected = Table.SelectColumns(FilteredSR, {
        "SR","Network","Outlet Address","City",
        "IW_Jan","IW_Feb","IW_Mar",
        "OTC_Jan","OTC_Feb","OTC_Mar",
        "Tests_Jan","Tests_Feb","Tests_Mar",
        "Cat_OTC","Cat_IW"
    }),
    Unpivoted = Table.UnpivotOtherColumns(Selected,
        {"SR","Network","Outlet Address","City","Cat_OTC","Cat_IW"}, "КатМісяць","Грн"),
    SplitCol = Table.SplitColumn(Unpivoted,"КатМісяць",
        Splitter.SplitTextByDelimiter("_", QuoteStyle.Csv),
        {"Категорія","Місяць_код"}),

    MonthLabel = Table.AddColumn(SplitCol, "Місяць_назва", each
        if      [Місяць_код]="Jan" then "January "   & RikStr
        else if [Місяць_код]="Feb" then "February "  & RikStr
        else if [Місяць_код]="Mar" then "March "     & RikStr
        else if [Місяць_код]="Apr" then "April "     & RikStr
        else if [Місяць_код]="May" then "May "       & RikStr
        else if [Місяць_код]="Jun" then "June "      & RikStr
        else if [Місяць_код]="Jul" then "July "      & RikStr
        else if [Місяць_код]="Aug" then "August "    & RikStr
        else if [Місяць_код]="Sep" then "September " & RikStr
        else if [Місяць_код]="Oct" then "October "   & RikStr
        else if [Місяць_код]="Nov" then "November "  & RikStr
        else if [Місяць_код]="Dec" then "December "  & RikStr
        else [Місяць_код] & " " & RikStr),

    Final = Table.TransformColumnTypes(
        Table.SelectColumns(MonthLabel, {
            "SR","Network","Outlet Address","City",
            "Категорія","Місяць_назва","Грн",
            "Cat_OTC","Cat_IW"
        }),{{"Грн", type number}})
in
    Final
```

> Що змінилось у кожному (4 точки): (1) `Renamed` — додано `Cat_OTC`/`Cat_IW` через якір (`AnchorGuard-1` / `AnchorGuard`); (2) `Selected` — +2 в кінець; (3) `Unpivoted` — +2 у keep-список; (4) `Final` — +2 в самий кінець (поз. 8, 9). Поз. 1–7 не зрушені → числа байт-у-байт.

Після обох вставок → **Close & Load** / **Refresh All**. Перевір: сума Грн по аптеці = як до змін.

---

## КРОК 2 — VBA (`ExportModule`)

У VBA `Ctrl+F` є. Три вставки в `AggGRN` + одна в `SerializePharmacy`.

### 2.1 Оголошення змінних
**Знайди:**
```vb
    Dim grn As Double, midx As Long, dk As String, cn As String
```
**Заміни на:**
```vb
    Dim grn As Double, midx As Long, dk As String, cn As String
    Dim catO As String, catI As String
```

### 2.2 Читання категорій (захищене UBound)
**Знайди:**
```vb
        grn = SafeNum(arr(r, 7))
```
**Заміни на:**
```vb
        grn = SafeNum(arr(r, 7))
        If UBound(arr, 2) >= 9 Then
            catO = Trim(CStr(arr(r, 8))): catI = Trim(CStr(arr(r, 9)))
        Else
            catO = "": catI = ""
        End If
```

### 2.3 Збереження в запис аптеки (перший рядок виграє — детерміновано)
**Знайди:**
```vb
            pr("nm") = net: pr("addr") = addr: pr("city") = city
```
**Заміни на:**
```vb
            pr("nm") = net: pr("addr") = addr: pr("city") = city
            pr("cat_otc") = catO: pr("cat_iw") = catI
```

### 2.4 Віддати в JSON — `SerializePharmacy`
**Знайди:**
```vb
    s = s & """city"":""" & EscapeJSON(CStr(pr("city"))) & ""","
```
**Заміни на:**
```vb
    s = s & """city"":""" & EscapeJSON(CStr(pr("city"))) & ""","
    s = s & """cat_otc"":""" & EscapeJSON(CStr(pr("cat_otc"))) & ""","
    s = s & """cat_iw"":"""  & EscapeJSON(CStr(pr("cat_iw")))  & ""","
```

> `AggGRN` викликається лише для IMS та Offtake GRN (9 колонок). SKU не торкається.

---

## КРОК 3 — Перевірка
- [ ] PQ Refresh без помилок; сума Грн по 1 аптеці × міс × категорія = як до змін.
- [ ] Export → у JSON кожної аптеки є `cat_otc`/`cat_iw`.
- [ ] Аптека лише з IMS (одна з 36) має категорію.
- [ ] Категорія в картці / банері / ТОП АПТЕК.
- [ ] Числа в HTML = KPI (один-в-один).

## КРОК 4 — Template (після успіху)
Регенерувати `KPI_Lens_template_v2.html`: `const DATA = [...]` → `/*__DATA__*/`.

## Відкладено (на цю фазу)
- SKU-крякозябра (Tab-3) → дельта
- wsd-правило: `Table.Distinct` по ключу перед `Table.Join` (прецедент МоїТТ_Keys/Дяченко)
- опційно `МоїТТ_Keys = Table.Distinct(...)` — захист від подвоєння (тер. Дяченко)
