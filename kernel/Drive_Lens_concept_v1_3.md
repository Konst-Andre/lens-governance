> живе доки: назавжди (вічне, wsd 1.8) — чинний концепт Drive Lens

# Drive Lens — Concept v1.3

**Статус:** Concept update після Batch05 — закриті критичні architectural decisions з GPT round 1 review
**Дата фіксації:** 28.05.2026
**База:** v1.2 (27.05.2026) — інкрементальний апдейт, не повний rewrite
**Сімейство:** Lens (KPI Lens, QR Lens, Drive Lens)

-----

## Changelog v1.2 → v1.3

Цей документ — **інкрементальний апдейт v1.2**. Всі розділи v1.2 що не згадані тут — **залишаються чинними без змін**.

### Що нового в v1.3

1. **Архітектура chrome layer уточнена** (Розділ 3 оновлений):
- Avatar action menu — 6 функціональних пунктів (новий)
- Theme switcher — 3 опції dropdown окремою кнопкою (новий)
- Sync pill 4-state — заміняє “● Оновлено: дата” status line (новий)
- Filter row — toggle + date picker (без іконки “хати”)
1. **Summary widget — 2×2 grid** (новий, замість 1×4 row)
1. **CTA pattern уніфікований** — без знаку “+”, з SVG іконками тематично (новий)
1. **Fuel selector канон** — 12 cells з visual grouping + tap+swipe gesture (новий)
1. **Records list — без іконок поряд** — numbered circle = маркер
1. **Cards vs lists — різні density patterns** (новий, документований)
1. **Modal forms — паралельна пара actions** (Скасувати + Зберегти)
1. **Українська локалізація типу палива** — А-95 (не “Pulls 95”)
1. **Icons policy** — SVG-only, селективно (новий явний розділ)
1. **Tokens v4 — monochromatic Pine Forest** — відмова від multi-color semantic (orange/cyan) (новий)
1. **Backend roadmap** — 4 етапи інтеграції Supabase (новий)
1. **Без заглушок принцип** — обов’язково функціональні UI elements (новий, посилання на wsd Кластер 3.9)

### Що відмінено від GPT round 1 draft

- Multi-color semantic system (orange + cyan + green) — не приймається
- Sync pill як виразний на synced state — змінено на тиху ієрархію
- App-bar з green tint — змінено на neutral
- “Хата” іконка справа від date picker — прибрана
- Emoji у UI — повна відмова (повторно явно, на основі v1.2 принципу 7)
- Status line “● Оновлено: дата” — замінено sync pill

### Що залишається з v1.2 без змін

- Розділ 1 — Концепція в одному реченні
- Розділ 2 — Користувацький контекст
- Розділ 4 — Дата-модель
- Розділ 5 — Паливо модель вводу
- Розділ 6 — WOG підхід
- Розділ 6.5 — Календар свят Reckitt 2026
- Розділ 7 — Auth і конфіденційність
- Розділ 8 — Технологічний стек
- Розділ 9 — Що НЕ входить у MVP
- Розділ 10 — Edge cases
- Розділ 11 — V2+ фантазія
- Розділ 12 — Naming
- Розділ 13 — Принципи дизайну (з підкресленням принципу 7)
- Розділ 14 — iOS PWA технічні специфікації (inherited from QR Lens)

-----

## Розділ 3 (оновлений) — Структура та chrome layer

### 3.1 Глобальна структура

Залишається 4 таби + PHBanner з v1.2. Структура табів незмінна:

- **Tab 1 — Огляд** (деталі активного дня + швидкий ввід)
- **Tab 2 — Журнал** (хронологічний список днів)
- **Tab 3 — Паливо** (паливний потік окремо)
- **Tab 4 — Місяць** (агрегати + WOG ліміт)

### 3.2 Chrome layer — компоненти зверху вниз

Chrome layer = ті елементи що видні на **всіх 4 табах**. Content area змінюється, chrome — constant.

**Композиція (зверху вниз):**

1. **App-bar** (50pt висота):
- Лого `Drive·Lens` (middle-dot стиль, Lens family) — зліва
- Avatar з ініціалом “K” + ім’я “Konstantinov A.” + chevron ▼ — центр-зліва (відкриває **Action menu**, див. 3.3)
- Theme switcher (іконка сонця/місяця/системного маркера) — праворуч (відкриває **Theme dropdown**, див. 3.4)
- Sync pill (4-state індикатор) — праворуч від theme switcher (див. 3.5)
1. **Filter row** (44pt висота) — під app-bar:
- Toggle “Робочий / Вайб / Всі” з chevron ▼ — accent border на active
- Date picker “26.05.2026 · Сьогодні” з calendar SVG іконкою
- (Без іконки “хати” — функція дублювалась з Tab Огляд)
1. **Content area** — змінний за табом
1. **Bottom nav** (50pt висота + safe-area):
- 4 таби: Огляд / Журнал / Паливо / Місяць
- Active з accent fill + accent label

### 3.3 Avatar Action Menu

**Тригер:** тап на avatar / ім’я / chevron ▼ у app-bar.

**Відкриття:** bottom sheet з 6 пунктами (списком).

**Пункти MVP:**

|Пункт        |Реалізація на Етапі 1 (MVP)                                                                                       |Етап повної готовності  |
|-------------|------------------------------------------------------------------------------------------------------------------|------------------------|
|Налаштування |Bottom sheet з реальними toggle/select: одиниці (км/милі), валюта (₴/USD/EUR), нагадування, autosave              |Етап 1 ✓                |
|Експорт даних|Реальний `Blob` + `download` атрибут → `drive-lens-export-YYYY-MM-DD.json` або `.csv`                             |Етап 1 ✓                |
|Архів        |Bottom sheet зі списком попередніх місяців. Empty state коли даних ще нема: “Поки немає архівних даних — після…”  |Етап 1 ✓ (з empty state)|
|Допомога     |Bottom sheet з FAQ (3-5 пунктів реального static контенту: як додати запис, switch режиму, snapshot fuel pin тощо)|Етап 1 ✓                |
|Про додаток  |Bottom sheet з версією, датою публікації, link на GitHub repo, credits                                            |Етап 1 ✓                |
|Sign out     |**Disabled з tooltip “Доступно після підключення акаунту (Етап 2)”** — reminder без забуття                       |Активується на Етапі 2/3|

**Чому Sign out лишається disabled:** на Етапі 1 немає Supabase auth, але прибирати його з UI ризиковано — можна забути додати при переході на Етап 2. Disabled з visible reason служить **активним reminder-ом** (див. wsd Кластер 3.9 — Без заглушок, edge case 1).

**Theme switcher НЕ входить у це меню** — він окрема кнопка справа в app-bar (див. 3.4). Це Lens family pattern: KPI Lens і QR Lens мали theme як окремий контрол.

### 3.4 Theme switcher

**Тригер:** тап на іконку сонця/місяця/системного маркера в app-bar (справа).

**Відкриття:** компактний dropdown з 3 опціями:

- **Світла** — explicit override на light theme
- **Темна** — explicit override на dark theme (default)
- **Системна** — підлаштовується під iOS Settings → Appearance (auto)

**Технічна реалізація:** inherited from QR Lens preview_batch22, wsd Кластер 9 (Persistent UI preferences — FOUC prevention).

- Inline `<script>` у `<head>` ПЕРЕД першим CSS link
- Читає `localStorage.driveLensTheme` (default = “Системна”)
- Виставляє `data-pref="dark"` або `data-pref="light"` на `<html>` до first paint
- Якщо “Системна” — обчислює effective через `window.matchMedia('(prefers-color-scheme: dark)').matches`
- Sync meta `theme-color` для status bar до first paint
- try/catch для Safari Private Mode де localStorage throw-ить

**Перейменування з QR Lens:** “Авто” → **“Системна”** (точніше передає що тема підлаштовується під iOS системну тему).

### 3.5 Sync pill (4 states)

**Заміняє** колишній status line “● Оновлено: дата” з v1.2 (бо дублювався з date picker нижче).

**Розміщення:** в app-bar праворуч (після theme switcher).

**4 стани (ієрархія від тихого до виразного):**

|Стан       |Візуал                                             |Token         |Коли активний                            |
|-----------|---------------------------------------------------|--------------|-----------------------------------------|
|**Synced** |Тиха зелена точка `● Синхронізовано`, без border   |`--text-muted`|Все ОК, остання sync успішна             |
|**Syncing**|Pulsing accent dot `◐ Синхронізація...`            |`--accent`    |Зараз триває upload/download             |
|**Pending**|Помаранчева точка з border `● Очікує синхронізації`|`--warn`      |Local changes ще не відправлені на server|
|**Offline**|Червона точка з alert background `⚠ Офлайн`        |`--crit`      |Немає мережі або server не відповідає    |

**Принцип:** **тихо на synced, виразно на проблемах**. Apple-pattern (Files.app sync, iCloud status).

**На Етапі 1 (mock data без Supabase)** — sync pill показує постійно `Synced` (статично). На Етапі 3 (підключення до Supabase) — починає реально реагувати на стан мережі і pending queue.

-----

## Розділ A (новий) — Summary widget

### A.1 Розташування

Під Filter row, перед CTA pair, у Tab 1 (Огляд).

### A.2 Layout — 2×2 grid

**Замість 1×4 row** (як було у GPT draft). Причина: на iPhone XS ширина 375pt − 32 padding = 343pt. 4 метрики в один ряд = ~85pt на метрику з 2-рядковим текстом — cramped. 2×2 grid дає ~170pt × 60pt на метрику — comfortably readable.

**Структура:**

```
┌─────────────────┬─────────────────┐
│ 75 км робочий   │ 16 км вайб      │
├─────────────────┼─────────────────┤
│ 8/12 ≈33.6 л    │ Запас 222 км    │
└─────────────────┴─────────────────┘
```

### A.3 Smart accent — реакція на toggle

**Замість** статичного multi-color (orange/cyan/green) — **monochromatic з context-aware акцентом**:

- За замовчуванням: усі 4 метрики **neutral text-secondary** (`--text-muted`, `#A1AAA6` у Pine Forest).
- Toggle = “Робочий” → метрика “75 км робочий” акцентована `--accent` (`#40916C`), інші 3 muted.
- Toggle = “Вайб” → метрика “16 км вайб” акцентована, інші 3 muted.
- Toggle = “Всі” → усі 4 neutral (нічого не виділене).

**Архітектурно:** один CSS class toggle на active metric. Без додаткових tokens, без зайвих рендерів.

**Бонус:** перемикання toggle візуально реагує — додає feedback на саму дію toggle. Краще ніж статичне розфарбування.

### A.4 Іконки — open question

Розглядаються два варіанти:

- **(A) Прибрати всі 4** — текст самодостатній (“75 км робочий”). Чистіше, automotive notebook mood.
- **(B) Залишити всі 4 з SVG** — briefcase (робочий), home (вайб), drop (паливо), road (запас). Glanceable dashboard mood.

**Default**: (A) для MVP. Якщо при тестуванні на пристрої не вистачає visual cue — перейти на (B).

-----

## Розділ B (новий) — CTA pattern

### B.1 Розташування

Під Summary widget, перед списком записів. **Вгорі**, не внизу — щоб не скролити до конкретного запису для додавання.

### B.2 Композиція — без знаку “+”

**Замість** `[+ Додати запис]` `[+ Заправка]` (виглядає примітивно з “+”) — **тематична SVG іконка + label**, без плюса.

```
┌────────────────────┬────────────────────┐
│ 📝 Запис           │ 💧 Заправка        │ (SVG, не emoji)
└────────────────────┴────────────────────┘
```

- “Запис” — pencil або notebook SVG icon
- “Заправка” — drop SVG icon (consistent з Card заправка pattern, див. Розділ C)

**Стиль:** primary action buttons з accent border, не filled (зберігає elegant feel). При hover/active — fill з accent.

### B.3 Поведінка

Тап на “Запис” → bottom sheet “Новий запис” (форма Image 2).
Тап на “Заправка” → bottom sheet “+ Заправка” (форма Image 1).

-----

## Розділ C (новий) — Cards vs lists patterns

### C.1 Принцип — різна density для різних контекстів

Drive Lens використовує **два різні формати** для відображення одного типу даних (наприклад заправки) у різних views. Це **intentional**, не inconsistency. Apple-pattern (Mail list view vs Mail message view).

### C.2 Compact list item (Tab 1)

**Контекст:** список записів сьогодні, компактний overview, scrolling багатьох items.

**Layout:**

- Drop іконка (SVG) — простий, зліва, маленький (16pt)
- Час · АЗС — 1 рядок
- Сума muted — 1 рядок під ним (secondary)
- Об’єм accent (зеленим) справа + chevron `>`

**Висота item:** ~56pt. Mінімалістично.

### C.3 Rich card (Tab Паливо, деталі заправки)

**Контекст:** Tab Паливо — заправка є primary subject. Деталі однієї заправки після тапу.

**Layout (як у Image 3, спроектований Konstantinov):**

- Drop SVG у зеленому tinted circle (`--accent-soft`) — лівий блок, ~48pt
- Час · АЗС — primary text великим
- Ціна + ₴/л muted — secondary
- Об’єм accent великий зеленим справа + chevron

**Висота card:** ~80pt. Premium feel.

### C.4 Коли який format

|View                          |Format      |
|------------------------------|------------|
|Tab 1 → “Заправка сьогодні”   |Compact list|
|Tab 1 → “Записи сьогодні”     |Compact list|
|Tab Паливо → список заправок  |Rich card   |
|Tab Журнал → день з заправкою |Compact list|
|Деталі однієї заправки (sheet)|Rich card   |
|Tab Місяць → агрегати         |Rich card   |

-----

## Розділ D (новий) — Fuel selector канон

### D.1 Візуальна форма

**Варіант 1 з Image 4** (як спроектовано в нашому design exploration):

- 12 cells горизонтально в один ряд
- **Visual grouping через gaps**: 4 групи по 3 cells, між групами більший gap (~12pt vs ~4pt всередині групи)
- Active = `--accent` (`#40916C`) filled
- Inactive = `--surface-3` (`#1F2A26`) dim
- Поточне значення підпис під grid: `8/12 (≈ 33.6 л)` з accent на числі

**Causes automotive ludometer feeling без втрати горизонтального простору.** Більш compact ніж 4×3 vertical grid.

### D.2 Взаємодія — tap + swipe одночасно

**Tap на cell:** встановлює значення = position of tapped cell.

**Swipe (drag horizontally) по container:** continuous adjust з live value update + haptic feedback:

- iOS Safari PWA — haptic недоступний (немає API), використовується visual scale feedback на cells при переході через них
- Android Chrome — `navigator.vibrate(5)` на кожному переході через cell

**Технічна реалізація:**

- `touchstart` фіксує `startX` + cell width
- `touchmove` обчислює delta → cellIndex → updates value live
- `touchend` фіксує final value у state

**Альтернатива якщо складно** (fallback): тільки tap на cell. Swipe можна додати пізніше як enhancement.

### D.3 Розміщення в UI

- **Inline у формах** (“+ Запис”, “+ Заправка”) — як у Image 2
- **Інтерактивний у Tab Паливо** — як головний контрол
- **Read-only у records list** — як fuel pin (просто число “8/12”, без grid)

-----

## Розділ E (новий) — Records list pattern

### E.1 Структура item

**Без іконок поряд з кожним записом** — numbered circle справа з функцією маркера.

```
[●1] 08:15  Лівий берег → Центр              32 км
     Одеська 171 · ТЦ Міст                   8/12 >
     [Робочий]
```

- Numbered circle (1, 2, 3…) — accent outline (active week pattern from QR Lens)
- Time · Route — primary line
- Address muted — secondary line
- KM accent — top-right
- Fuel pin snapshot (8/12) — bottom-right (snapshot момент запису, не поточний)
- Chip “Робочий”/“Вайб” — **тільки коли toggle = Всі** (інакше дублювання)

### E.2 Snapshot fuel pin

Кожен запис фіксує рівень палива **на момент створення**, не показує поточний рівень. Це **бізнес-логіка**:

- Запис 08:15: був 9/12 на момент створення
- Запис 11:40: був 8/12
- Запис 15:30: був 7/12

Це і фактична інформація (історія рівня), і вирішує дублювання з “Поточний стан” widget.

### E.3 “Робочий” chip під записом — conditional

- Toggle = “Робочий” → chip не показується (всі записи робочі, тавтологія).
- Toggle = “Вайб” → chip не показується (всі записи вайб).
- Toggle = “Всі” → chip показується на кожному записі для розпізнавання типу.

-----

## Розділ F (новий) — Modal forms pattern

### F.1 Структура — універсальна для всіх форм

Уніфікований pattern для **усіх** bottom sheet модальних форм (Новий запис, +Заправка, Налаштування, тощо):

- Header: title + close X справа
- Sections (з накопиченням донизу)
- Footer: **паралельна пара actions** (Скасувати outline + Зберегти accent filled)

### F.2 Чому паралельна пара (Image 1 style), не stacked (Image 2 style)

- Стандарт iOS modal pattern з двома actions (Apple HIG)
- Виглядає premium і decisive
- Зменшує вертикальний простір у footer

### F.3 Конкретні форми

**“+ Заправка” (Image 1 style — після уніфікації):**

- Час і місце (Час | АЗС)
- Обсяг (Кількість літрів | shortcut “Повний бак”)
- Ціна і сума (Ціна за літр | Сума | Тип палива)
- Одометр і паливо (Одометр | Рівень після — inline fuel selector з Розділу D)
- Примітка (textarea, 0/120)
- Footer: [Скасувати] [Зберегти заправку]

**“Новий запис” (переробити з stacked на parallel):**

- Час | Запас ходу
- Одометр (full-width)
- Рівень палива (inline fuel selector з Розділу D)
- Примітка з прикладами в placeholder
- Footer: [Скасувати] [Зберегти запис]

### F.4 Тип палива — українські стандарти

Замість “Pulls 95” (typo з GPT draft) — українські стандарти:

- **А-95** (стандарт)
- **А-95 Преміум** / **Pulsar 95** (premium grade)
- А-92, А-98, ДП (дизель), Газ (LPG/CNG)

Default selection: **А-95** (твій звичайний).

-----

## Розділ G (новий) — Icons policy

### G.1 Загальний принцип

**SVG only. Ніколи emoji.** Підтверджує v1.2 принцип 7 (“Без емодзі в production UI — лаконічно”).

### G.2 Де залишаємо іконки

- **Bottom nav** — 4 SVG іконки (Огляд / Журнал / Паливо / Місяць) — стандарт iOS
- **Toggle modes у filter row** — SVG іконки (валіза для робочого, home/heart для вайбу, etc) — швидке recognition
- **Theme switcher** — SVG (сонце / місяць / системний індикатор)
- **Date picker** — calendar SVG
- **CTA buttons** — pencil SVG для “Запис”, drop SVG для “Заправка” (заміняють знак “+”)
- **Drop у Card заправка** (rich format) — продуктовий маркер
- **Chevrons** (>, ▾) для navigation affordance
- **Close X** у modal headers

### G.3 Де прибираємо іконки

- **Поряд з кожною метрикою у Summary widget** — default (A), текст самодостатній (див. Розділ A.4)
- **Поряд з кожним записом у списку** — numbered circle = маркер
- **“Хата” справа від date picker** — функція дублюється з Tab Огляд

### G.4 SVG sprite або inline?

**Inline SVG** з `<symbol id="...">` блоком у `<defs>` і `<use href="#...">` в використанні. Як у QR Lens preview_batch22. Кеширується, дешево.

**Альтернатива:** окремі `<svg>` теги inline в кожному компоненті. Простіше для початку, можна refactor пізніше.

### G.5 Розмір і колір

- Стандартний розмір: 24×24pt для navigation/CTA, 16×16pt для inline/secondary, 48×48pt для hero (Card заправка circle)
- Колір: `currentColor` → успадковує від батьківського element (легко змінювати через CSS)
- Stroke width: 1.5pt-2pt (consistent з iOS SF Symbols style)

-----

## Розділ H (новий) — Tokens v4

### H.1 Принципи v4

- **Monochromatic Pine Forest** — один accent колір (`#40916C` Pine/Forest) + tonal variations
- **Без multi-color semantic** (no orange, no cyan, no extra hues)
- **Disciplined set** — ~25-30 tokens total (Apple HIG range)
- **Inline коментарі about intended use** для кожного token

### H.2 Token list (preliminary draft, фіналізується в HTML)

```css
:root {
  /* ===== Surfaces (3 levels for depth) ===== */
  --surface-1: #0D1110;       /* app background, deepest */
  --surface-2: #151E1C;       /* cards / sheets background */
  --surface-3: #1F2A26;       /* nested elements, dim fuel cells */
  --surface-4: #2A3531;       /* hover / active surfaces */

  /* ===== Text (3 levels of emphasis) ===== */
  --text-primary: #F0F4F2;    /* main copy */
  --text-secondary: #A1AAA6;  /* secondary copy, muted labels */
  --text-muted: #6B7570;      /* lowest emphasis */

  /* ===== Accent (Pine Forest mono) ===== */
  --accent: #40916C;          /* primary action, active state */
  --accent-hover: #52B788;    /* hover/pressed state */
  --accent-soft: #1E3A2D;     /* tinted backgrounds (e.g. drop circle) */
  --accent-text: #4FAE7A;     /* accent text on dark, numbers */

  /* ===== Status (semantic, sparingly used) ===== */
  --ok: #4FAE7A;              /* success states */
  --warn: #D4A055;            /* warnings, pending sync */
  --crit: #C75450;            /* errors, offline */
  --info: #6B9BB8;            /* tooltips, info notes (rarely) */

  /* ===== Borders & dividers ===== */
  --border-subtle: rgba(255,255,255,0.06);  /* hairline dividers */
  --border-default: rgba(255,255,255,0.12); /* default outlines */
  --border-accent: #40916C;                 /* active outline */

  /* ===== App-bar specific ===== */
  --appbar-bg-dark: rgba(13,17,16,0.85);    /* neutral, slight green tint */
  --appbar-bg-light: rgba(248,250,248,0.85);
}
```

### H.3 Light theme (mirror palette)

Light theme використовує ту саму structure з інверсією surfaces і text. Accent залишається той самий `#40916C` (виглядає природно в обох темах). Конкретні значення фіналізуються при імплементації Розділу 3.4 (Theme switcher).

### H.4 Що було відкинуто з v3 (GPT draft)

- `--color-work` / `--color-vacation` semantic tokens — не потрібно з smart accent (Розділ A.3)
- `--btn-primary-bg` (дублював `--accent`)
- `--fuel-filled` (дублював `--accent`)
- `--info` semantic для fuel readings — fuel використовує accent

-----

## Розділ I (новий) — Backend roadmap

### I.1 Етапи інтеграції

**Етап 1 — Preview HTML з mock data** (~1-2 сесії)

- Single HTML файл з inline JSON mock data
- Реальні render-функції що читають з mock
- localStorage для persistence preferences (theme, settings)
- Sync pill статично показує “Synced” (фейкова стабільність)
- Тестування UX на iPhone XS PWA

**Етап 2 — Supabase schema + auth + RLS** (~2-3 сесії)

- Schema design (tables: records, fueling, settings, vehicles)
- Row Level Security policies (мультикористувацька ізоляція)
- Auth setup (email + password або magic link)
- Types generation (supabase-js TypeScript)

**Етап 3 — Підключення HTML до Supabase** (~2 сесії)

- supabase-js клієнт інтегрований у HTML
- CRUD operations для всіх entities
- Error handling з UI feedback
- Optimistic updates для responsive UX
- Sign out — активується тут (раніше disabled)

**Етап 4 — Service Worker + IndexedDB cache + sync queue** (~2-3 сесії)

- Offline-first architecture
- IndexedDB для local cache всіх даних
- Sync queue для pending uploads коли offline
- Sync pill починає реально відображати 4 states (синхронізація / pending / offline)
- Background sync через Service Worker

### I.2 Рекомендована послідовність

Етап 1 → Етап 2 → Етап 3 → Етап 4. Не змішувати дизайн і backend в одному pass — це wsd Кластер 3.1 (Збір всіх змін перед видачею) на проектному рівні.

### I.3 Що дозволяє починати з Етапу 1

- Швидкий visual feedback на дизайн рішеннях
- iPhone XS PWA тестування без потреби в auth
- Mock data flow повторює production data flow (зміниться тільки джерело)
- Etap 2-3 рефакторинг буде локалізований (заміна джерела даних, не структури)

-----

## Розділ J (новий) — Без заглушок принцип

### J.1 Посилання

Див. `wsd_addition_no_stubs.md` (пропозиція для wsd Кластер 3.9) — повний опис правила, edge cases, self-check, anti-pattern vs pattern examples.

### J.2 Drive Lens специфічне застосування

- **Кожен пункт avatar menu** — реальна функція або disabled з visible reason.
- **Sign out — інтенціональний reminder** (disabled з tooltip), не заглушка.
- **Усі toggle / checkbox / select** у Settings — реальний `localStorage.setItem` + read on launch.
- **Export** — реальний `Blob` + download, не TODO.
- **Empty states** — реальні conditional renders на основі `data.length === 0`, не permanent placeholders.

### J.3 Self-check на момент видачі preview HTML

Прогнати чеклист 15 пунктів з wsd 3.9. Не видавати HTML поки не пройдено.

-----

## Розділ 13 (підкреслено) — Принципи дизайну

З v1.2 без змін. Підкреслюється **принцип 7 (явно):**

> **7. Без емодзі в production UI — лаконічно.**

Цей принцип був порушений у GPT round 1 draft (emoji використано як decoration в багатьох місцях). В v1.3 повертаємось до канону: **SVG only, скрізь, завжди**.

-----

## Розділ 14 (без змін) — iOS PWA технічні специфікації

Усі 46 пунктів inherited from QR Lens preview_batch22 — без змін. Див. v1.2 рядки 453-1289.

**Drive Lens-specific extensions** з v1.2 розділу “Нове для Drive Lens”:

- Service Worker для offline mode
- Форми вводу з iOS-friendly keyboards (`inputmode`, `pattern`)
- Supabase realtime sync (Етап 4)

Без додавань у v1.3.

-----

## Розділ N — Open questions (для тестування)

Закриваються при першому device test preview HTML:

1. **Summary widget icons** — варіант (A) без іконок чи (B) з SVG? Default (A), тестується на пристрої.
1. **Fuel selector swipe gesture** — наскільки comfortable на real iPhone XS PWA. Якщо не working — fallback на tap-only.
1. **2×2 grid summary fit** — підтвердити що не cramped на iPhone XS 375pt width.
1. **Card vs list густина** — підтвердити що user розуміє patterns в реальному використанні.

-----

## Summary — що приймаємо як canonical для Етапу 1

**Chrome layer:**

- App-bar neutral з avatar+menu + theme switcher + sync pill (4 states)
- Filter row toggle + date (без хати)
- Bottom nav 4 tabs

**Content patterns:**

- Summary widget 2×2 з smart accent
- CTA пара з SVG іконками без +
- Fuel selector 12 cells visual-grouped, tap+swipe
- Records numbered without inline icons, fuel pin snapshot
- Cards rich vs list compact — різні density для контекстів
- Modal forms parallel actions

**Visual system:**

- Monochromatic Pine Forest tokens v4
- SVG only icons (selective placement)
- No emoji, no multi-color semantic

**Functional discipline:**

- No stubs — кожен UI element функціональний або disabled з reason
- Sign out — інтенціональний reminder через disabled

**Backend roadmap:**

- Етап 1 → 4, починаємо з mock data preview HTML

-----

## Наступний крок

1. Прийняти v1.3 як canonical → переходимо до preview HTML implementation (Етап 1).
1. Або: спочатку складаємо окремий tokens v4 file для review перед HTML.