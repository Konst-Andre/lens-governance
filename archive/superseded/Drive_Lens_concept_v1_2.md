# Drive Lens — Concept v1.2

**Статус:** Concept fixed з повними iOS PWA технічними специфікаціями
**Дата фіксації:** 26.05.2026 (v1.1) · 27.05.2026 (v1.2 — додано розділ 14)
**Сімейство:** Lens (KPI Lens, QR Lens, Drive Lens)

**Зміни v1.1 → v1.2:**

- Додано розділ 14 “iOS PWA технічні специфікації” з 46 пунктами
- Усі базові патерни перейнято з QR Lens (Batch 8h–24.1), задокументованих як перевірена база
- Додано Drive Lens-specific вимоги яких не було в QR Lens: offline mode, форми вводу, Supabase realtime sync

-----

## 1. Концепція в одному реченні

**Drive Lens — особистий журнал службового авто з акцентом на швидкість щоденного запису, мультикористувацький з ізоляцією даних.**

Не CRM, не fleet management, не інструмент контролю керівництва. Розумний блокнот з аналітикою, що масштабується від однієї людини до команди без перетину даних між користувачами.

-----

## 2. Користувацький контекст

**Користувач:** торговий представник з корпоративним авто
**Поточна система:** Apple Notes — щоденний рядок з маршрутом, км, одометром, заправками
**Проблема:** немає автоматичної аналітики, немає історії, дані прив’язані до одного пристрою

**Реальний паттерн нотаток (приклад):**

```
06.04 Каменское - дмк-свободи + оборуд.арбузи - 125км 17126км на веч. 🔴 30л
17.04 север-калин-правда - 32км 17627км + вайб 16км 17643
```

**Ключові інсайти з реального workflow:**

- “Вайб” як inline-тег особистих поїздок
- Райони як скорочення, не точні адреси
- Одометр на вечір, не per-trip
- Тижневі підсумки рахуються вручну
- Лікарняний як окремий тип дня

**Drive Lens не повинен бути повільнішим за поточний Notes-блокнот.**

-----

## 3. Структура — 4 таби + PHBanner

### PHBanner (постійний, на всіх табах)

Показує **активний день** — глобальний контекст продукту.

- Дефолт: сьогодні
- Тап по банеру → календар з вибором дати
- Кнопка “🏠 Сьогодні” поруч для швидкого повернення
- Управляє контекстом 3 з 4 табів (Огляд, Журнал, Паливо)

### Таб 1 — Огляд

**Роль:** деталі активного дня. Швидкий ввід.

Структура:

- Status line: `🔧 75км · 👤 16км · 💧 8/12 · Запас 222км`
- Picker зверху: `Тип дня: Робочий ▾` — змінює тип дня
- Chips: `[Робочий] [Вайб]` — режим вводу (видимий тільки на `Робочий` день)
- Список записів дня (snapshots з часом, одометром, рівнем палива)
- Кнопки: `[+ Додати запис]` `[+ Заправка]`

**Логіка чіпів за типом дня:**

- `Робочий` → чіпи `[Робочий] [Вайб]` (дефолт Робочий)
- `Вихідний / Свято / Лікарняний / Відпустка` → чіпи приховані, всі записи автоматично `Вайб`

**НЕ показує:** історію інших днів, місячну аналітику.

### Таб 2 — Журнал

**Роль:** хронологічний список усіх днів.

- Chips фільтра: `[Всі] [Робочі] [Вайб]`
- Групування: по тижнях / по місяцях
- Тап по дню → день стає активним у PHBanner

**НЕ показує:** деталі поточного дня (це робить Огляд).

### Таб 3 — Паливо

**Роль:** паливний потік окремо.

Два режими через chip:

- `[День]` — паливо активного дня (рівень, запас, споживання)
- `[Місяць]` — заправки за місяць активного дня + ліміт WOG

Показує:

- Розрахункове добове споживання (з одометра + рівня палива)
- Журнал заправок (ручний ввід WOG-подій)
- Витрата L/100км

### Таб 4 — Місяць

**Роль:** агрегований підсумок місяця активного дня.

- Загальний пробіг
- Робочий vs особистий
- Заправки + літри
- Витрата
- Залишок ліміту

**НЕ керується PHBanner-днем,** показує цілий місяць (місяць активного дня).
**Чисто читання,** жодного вводу.

-----

## 4. Дата-модель

### Snapshot (запис)

Точка в часі з фіксацією одометра + палива.

```
{
  timestamp: "2026-05-26T08:30",
  odometer: 17627,
  fuel_level: 8,        // 0-12 поділів паливоміра
  range_km: 222,        // опціонально, запас ходу
  note: "ранок"
}
```

### Trip (поїздка)

Відрізок між двома snapshot-ами.

```
{
  type: "work" | "personal",
  from_snapshot: snapshot_id,
  to_snapshot: snapshot_id,
  distance_km: calculated,
  fuel_used: calculated_approximate,
  route: "север-калин-правда"
}
```

**Обмеження по типу:**

- `work` дозволений тільки на день з `day_type = work`
- `personal` дозволений на будь-якому типі дня
- На вихідних/святах/лікарняних/відпустках усі поїздки автоматично `personal`

### Refuel (заправка)

Окрема подія, не залежить від snapshot.

```
{
  timestamp: "2026-05-26T18:35",
  liters: 30,
  station: "АЗС Дніпродзержинськ",
  fuel_type: "А-95",
  source: "manual" | "wog_import"
}
```

### Day (день)

Контейнер для snapshot-ів і refuel-ів одного дня.

```
{
  date: "2026-05-26",
  day_type: "work" | "weekend" | "holiday" | "sick" | "vacation",
  day_type_source: "auto" | "manual",  // звідки прийшов тип
  snapshots: [...],
  refuels: [...],
  trips: [...]  // обчислюються з snapshots
}
```

**Авто-логіка визначення day_type:**

1. Дата у списку свят (див. розділ 6.5) → `holiday`
1. Інакше Сб/Нд → `weekend`
1. Інакше Пн-Пт → `work`
1. Користувач може вручну змінити будь-який день — це override з `day_type_source = manual`

-----

## 5. Паливо — модель вводу

### Первинне джерело: візуальний паливомір

- **12 поділів** (4 великі × 3 малі), бак 50л → 1 поділ ≈ 4.2л
- Візуальний селектор у формі (tap на рівні)
- Швидкий ввід, відповідає тому що бачиш на приладці

### Опційне поле: запас ходу (км)

- Цифрове поле, можна не заповнювати
- Drive Lens використовує для додаткової валідації споживання
- Не перевантажує інтерфейс (одне маленьке поле)

### Розрахунок добового споживання

- Snapshot ранку: рівень X, одометр Y₁
- Snapshot вечора: рівень X’, одометр Y₂
- Споживання ≈ (X - X’) × 4.2л
- Пробіг = Y₂ - Y₁
- Витрата = споживання / пробіг × 100

Точність ±4л на день — достатньо для розуміння динаміки.

-----

## 6. WOG — підхід

**MVP: ручний ввід заправок.**

Форма:

- Дата (auto = сьогодні)
- Літри
- АЗС (опціонально)
- Тип палива (default А-95)

Чому не автоімпорт у MVP:

- WOG `oldonline2.wog.ua` — SPA, потрібен headless browser
- Потребує Puppeteer на бекенді (Render) — окремий рівень складності
- 4-5 заправок на місяць × 30 секунд = 2.5 хв/міс ручного вводу — прийнятно

### V2 ідея — WOG quick-access

Кнопка-картка в таб Паливо: “Відкрити WOG”. Веде на збережений URL картки користувача. Не автоімпорт, а швидкий доступ до перегляду.

### V3 ідея — автоімпорт через Puppeteer

Тільки якщо ручний ввід реально надокучить.

-----

## 6.5. Календар святкових днів Reckitt 2026

Built-in JSON-таблиця у коді (або таблиця в Supabase):

```js
const reckitt_holidays_2026 = [
  { date: "2026-01-01", name: "Новий рік" },
  { date: "2026-04-12", name: "Великдень" },
  { date: "2026-04-13", name: "Великдень (перенесено)" },
  { date: "2026-05-01", name: "День праці" },
  { date: "2026-05-08", name: "День памʼяті та перемоги" },
  { date: "2026-05-31", name: "Трійця" },
  { date: "2026-06-01", name: "Трійця (перенесено)" },
  { date: "2026-06-28", name: "День Конституції" },
  { date: "2026-06-29", name: "День Конституції (перенесено)" },
  { date: "2026-07-15", name: "День Української Державності" },
  { date: "2026-08-24", name: "День Незалежності" },
  { date: "2026-10-01", name: "День захисників та захисниць" },
  { date: "2026-12-25", name: "Різдво Христове" }
];
```

**Логіка застосування:** при створенні дня в моделі чек на дату → якщо є в списку → `day_type = holiday` автоматично.

**Гібридна модель:**

- ✅ Авто: 13 днів зі списку + Сб/Нд за замовч.
- ✅ Ручний override: будь-який день → будь-який тип
- ✅ Особисті дні (Лікарняний/Відпустка/особистий вихідний): завжди вручну

**Щорічне оновлення:** на початку кожного року Reckitt публікує новий календар. Список оновлюється правкою одного файлу (~5 хвилин). У майбутньому можна винести в Supabase-таблицю для оновлення без релізу.

-----

## 7. Auth і конфіденційність

### Модель приватності

- **Кожен користувач бачить тільки свої дані**
- Анти-surveillance: керівництво не може використати як інструмент контролю
- Дані ізольовані через Supabase Row Level Security
- Сценарій: ділиться URL з колегою → колега створює свій ізольований акаунт

### Auth: Supabase + Email OTP

**Чому OTP, не magic link:**
Microsoft Defender Safe Links у корпоративних поштах “пре-клікає” magic link для перевірки → споживає одноразовий токен → користувач отримує “expired link”. Це широко документована проблема. OTP-код (6 цифр) — текст, не URL, тому Safe Links не може його зламати.

**Flow для користувача:**

1. Відкрив Drive Lens → ввів email
1. Через 10 секунд прийшов лист з 6-значним кодом
1. Ввів код → залогінений
1. Сесія тримається тижнями, далі без re-login

**Рекомендація email:**

- **Особистий email (Gmail, Ukr.net) — кращий вибір** — обходить корпоративні фільтри, виживає звільнення, посилює анти-surveillance
- **Робочий @reckitt.com — теж працює** (OTP не зламається), але доставка не гарантована
- Перед розгортанням на колег: тестовий лист на власну робочу пошту для перевірки

-----

## 8. Технологічний стек

|Шар        |Інструмент                         |Чому                                        |
|-----------|-----------------------------------|--------------------------------------------|
|Frontend   |GitHub Pages (HTML/CSS/JS, PWA)    |Знайомий, безкоштовний, статичний           |
|Backend    |Supabase (PostgreSQL + Auth + REST)|Безкоштовний tier, RLS, нуль серверного коду|
|Auth       |Supabase Email OTP                 |Імунітет до Safe Links                      |
|Keep-alive |GitHub Actions cron                |Запобігає 7-денній паузі Supabase           |
|Hosting URL|`username.github.io/drive-lens/`   |Безкоштовно, кастомний домен опційно        |

### Supabase free tier — підтверджено (травень 2026)

- 500 МБ БД (вистачить на ~1300 користувачів)
- 5 ГБ трафіку
- 50K MAU
- 2 проекти
- Auth + Storage + Edge Functions включено

**Ризик паузи:** проект засне після 7 днів неактивності → пінг через GitHub Actions раз на 3-4 дні закриває.

-----

## 9. Що НЕ входить у MVP

- **OCR одометра** — Tesseract ненадійний на цифровому кокпіті, Google Vision дорого. Фото = пам’ять (зберігається опціонально як підтвердження), цифри вводяться вручну.
- **Автоімпорт WOG** — складність не виправдана для MVP.
- **Множинні авто на одного користувача** — один user = одне авто.
- **Експорт даних** — додамо в v2 (PDF/CSV).
- **Push-сповіщення** — не потрібні для журналу.

-----

## 10. Edge cases — рішення

### 10.1. Типи днів (вихідний / свято / лікарняний / відпустка)

Кожен день має `day_type`. Авто-логіка (див. розділ 4):

- Дата у списку свят → `holiday`
- Сб/Нд → `weekend`
- Інакше → `work`

Користувач може вручну змінити тип у Огляді (picker `Тип дня`).

**Контекст типів:**

- `weekend` — субота/неділя за замовч., поїздки є але вони `personal`
- `holiday` — свято з календаря Reckitt, поїздки `personal`
- `sick` — лікарняний, поїздки до клініки/аптеки = `personal`
- `vacation` — відпустка, можливі особисті поїздки або їх відсутність
- `work` — робочий день, дозволені поїздки `work` і `personal`

### 10.2. Багатоденний період (лікарняний 21-23, відпустка тиждень)

Функція **“Позначити період”** в Місяці або Журналі.

- Тап на іконку календаря → range picker → обираєш діапазон → ставиш тип
- За один тап можна замаркувати 3-7+ днів
- Підтримує всі manual-типи: `sick`, `vacation`, `holiday`

### 10.3. Забув закрити вчора

М’який нагадник, без блокувань.

Логіка: якщо у попередньому дні є тільки ранковий snapshot — при відкритті Огляду сьогодні показується картка:

> *“Вчора (25.05) — день не закритий. Останній одометр: 17 627. Доповнити?”*

Тап → відкриває вчора в Огляді. Можна закрити (ввести вечірній snapshot) або відхилити (“Так і має бути”).

### 10.4. Помилка вводу (одометр, паливо, заправка)

Long-press на запис → меню `[Редагувати] [Видалити]`.

Усі похідні розрахунки (пробіг, споживання, місячні підсумки) **перераховуються автоматично**, бо обчислюються з snapshots/refuels, а не зберігаються окремо.

### 10.5. Дні тільки з особистими поїздками

Не справжній edge case — працює природньо завдяки моделі типів дня.

На `weekend / holiday / sick / vacation` всі поїздки автоматично `personal`. Status line м’яко обробляє “0 робочих” — це факт, не помилка.

### 10.6. Перший вхід (onboarding)

Мінімалістичний flow з 3 екранів:

1. **Welcome** → “Drive Lens — твій журнал авто. Дані тільки твої.”
1. **Auth** → введення email + 6-значний OTP
1. **Setup** → “Введи поточний одометр і рівень палива — це твоя стартова точка.”

Після setup — одразу в Огляд з готовим першим snapshot-ом.

**Опційно:** tooltip-картка з підказкою “💡 Тапни ‘+ Додати запис’ щоб додати поїздку”.

### 10.7. Заміна авто

**MVP:** не реалізуємо. У документації: “При зміні авто звернутися до адміна для скидання.” Я (адмін) очищу дані через Supabase.

**V2:** Settings → “Замінити авто” → діалог “Дані будуть архівовані, новий одометр стартує з 0”. Архів доступний через окремий розділ.

-----

## 11. V2+ фантазія

- Predictive refuel: “Наступна заправка ймовірно 02.06”
- Cost split: “Особисті поїздки коштували X UAH”
- Map view (privacy-aware, opt-in)
- Експорт PDF/CSV
- Multi-vehicle підтримка
- Telegram-bot інтеграція для quick-add записів

-----

## 12. Naming

**Drive Lens** — затверджено.

Чому:

- “Drive” — дія, не об’єкт. Не “про машину”, а “про водіння”
- Вписується в Lens-сімейство
- Семантично гнучкий (особистий журнал, не корпоративний інструмент)

Назви табів:

- **Огляд** (не “Сьогодні” — щоб не конфліктувати з PHBanner-датою)
- **Журнал**
- **Паливо**
- **Місяць**

-----

## 13. Принципи дизайну (для GPT-промпта)

1. **Швидкість понад все** — кожен зайвий тап = втрата на користувача
1. **Mobile-first** — все проектується під телефон, ноут це бонус
1. **Один таб — одна роль** — без дублювання логіки
1. **PHBanner як глобальний контекст** — патерн з KPI/QR Lens
1. **Chips для switching, summary cards для metrics** — не плутати
1. **Темна тема за замовч.** — як в Notes де ведеться зараз
1. **Без емодзі в production UI** — лаконічно

-----

## 14. iOS PWA технічні специфікації

> **Джерело:** усі патерни перейнято з QR Lens production (Batch 8h–24.1). Тестова база — iPhone XS iOS 18 PWA. Деталі реалізації — `QR_Lens_preview_batch22.html`, цей розділ — їх перенос-довідник для Drive Lens.
> 
> **Категоризація кожного пункту:**
> 
> - ✅ **1:1** — переносимо без змін (універсальне iOS PWA правило)
> - 🔧 **Адаптовано** — той самий патерн, інші параметри/назви для Drive Lens
> - 🆕 **Нове** — не було в QR Lens, специфічне для Drive Lens (read-write контекст)

-----

### 14.1 HTML head — обов’язкові meta tags ✅ 1:1

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Drive Lens">
<meta name="theme-color" content="#0d1117">
```

**Критичне:**

- `viewport-fit=cover` — БЕЗ цього `env(safe-area-*)` повертає 0 → safe-area не працює
- `apple-mobile-web-app-capable: yes` — БЕЗ цього не запускається у standalone mode
- `black-translucent` — БЕЗ цього статус-бар буде з білою смугою у PWA
- `maximum-scale=1, user-scalable=no` — блокує pinch-zoom (доповнюється JS gesture block, бо iOS Safari ігнорує цю частину meta)

-----

### 14.2 PWA manifest.json ✅ 1:1

```json
{
  "id": "/drive-lens/",
  "start_url": "/drive-lens/",
  "scope": "/drive-lens/",
  "name": "Drive Lens",
  "short_name": "Drive Lens",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#0d1117",
  "theme_color": "#0d1117",
  "icons": [
    { "src": "icons/icon-192.png?v=batch01", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "icons/icon-512.png?v=batch01", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "icons/icon-512-maskable.png?v=batch01", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

**Примітка:** `orientation: "portrait"` у manifest iOS **ігнорує** — orientation lock робиться через CSS overlay (див. 14.19).

-----

### 14.3 Icon pack (7 файлів) ✅ 1:1

|Файл                   |Розмір            |Призначення                                       |
|-----------------------|------------------|--------------------------------------------------|
|`icon-16.png`          |16×16             |Browser tab favicon                               |
|`icon-32.png`          |32×32             |Browser tab favicon (HiDPI)                       |
|`icon-180.png`         |180×180           |apple-touch-icon (iOS home screen)                |
|`icon-192.png`         |192×192           |PWA standard                                      |
|`icon-512.png`         |512×512           |PWA standard (great resolution)                   |
|`icon-512-maskable.png`|512×512           |Android adaptive icons (safe-zone 80% = 410/512px)|
|`favicon.ico`          |multi-res 16/32/48|Legacy browsers                                   |

**Критичне правило:** source іконка має бути **full-bleed без власних чорних полів навколо squircle**. iOS прикладає squircle-маску ПОВЕРХ канвасу — якщо є власні поля, видно чорну рамку.

**Workflow:** source PNG → symmetric crop bbox (32px з усіх боків) → Lanczos resize до 7 цільових розмірів. Maskable варіант — з padding 10% з кожного боку (safe-zone 80%).

-----

### 14.4 Cache-busting versioning ✅ 1:1

```html
<!-- В HTML head — 5 місць -->
<link rel="manifest" href="manifest.json?v=batch01">
<link rel="apple-touch-icon" sizes="180x180" href="icons/icon-180.png?v=batch01">
<link rel="icon" type="image/png" sizes="32x32" href="icons/icon-32.png?v=batch01">
<link rel="icon" type="image/png" sizes="16x16" href="icons/icon-16.png?v=batch01">
<link rel="shortcut icon" href="icons/favicon.ico?v=batch01">

<!-- В manifest.json — 3 місця в icons[] -->
```

**Sync обов’язковий:** при зміні іконки інкрементувати `?v=batchN` у HTML (5x) + manifest (3x) одночасно. Manifest читається браузером окремо від HTML і має власний кеш.

**Файли `icon-*.png` НЕ перейменовуються** — змінюється лише URL у query. Браузер бачить новий URL → fetch’ить файл заново попри HTTP-кеш.

-----

### 14.5 FOUC prevention inline script ✅ 1:1

**Inline script у `<head>` ПЕРЕД будь-яким CSS link/style.** Встановлює `data-theme` атрибут на `<html>` до first paint.

```html
<script>
  (function(){
    try {
      var saved = localStorage.getItem('dl-theme');           // null|'auto'|'light'|'dark'
      var mode  = saved || 'auto';
      var dark  = mode === 'dark' || (mode === 'auto' && matchMedia('(prefers-color-scheme:dark)').matches);
      var html  = document.documentElement;
      html.setAttribute('data-theme', dark ? 'dark' : 'light');
      html.setAttribute('data-theme-mode', mode);
      var meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.content = dark ? '#0d1117' : '#f7f4ec';
    } catch(e) {
      // Safari Private Mode → localStorage заблоковано → fallback
      document.documentElement.setAttribute('data-theme', 'dark');
      document.documentElement.setAttribute('data-theme-mode', 'auto');
    }
  })();
</script>
```

**Правила pattern:**

1. **IIFE wrapper** — не забруднюємо global scope
1. **try/catch обов’язково** — Safari Private Browsing throws на localStorage
1. **Synchronous only** — НЕ async/Promise/setTimeout
1. **Attributes на `<html>`**, не на `<body>` — у момент виконання inline script body ще не існує у DOM
1. **Meta theme-color sync** — оновлюється в тому ж script для status bar

🔧 **Адаптовано для Drive Lens:** ключ `dl-theme` замість `qr-theme`.

-----

### 14.6 Theme dropdown 3-mode (auto/light/dark) ✅ 1:1

**HTML структура** — button + dropdown у app bar:

```html
<div class="theme-wrap">
  <button class="icon-btn" id="btnTheme" aria-label="Тема" aria-haspopup="true" aria-expanded="false">
    <svg class="th-svg" ... > <!-- sun + moon з opacity transitions --> </svg>
  </button>
  <div class="theme-menu" id="themeMenu" role="menu" hidden>
    <button class="theme-item" data-mode="auto"  role="menuitemradio">Авто</button>
    <button class="theme-item" data-mode="light" role="menuitemradio">Світла</button>
    <button class="theme-item" data-mode="dark"  role="menuitemradio">Темна</button>
  </div>
</div>
```

**JS логіка:**

- `getThemeMode()` / `setThemeMode(mode)` — persistent через localStorage
- `applyTheme()` — sync data-theme + theme-color meta + dropdown active state + aria-label
- System listener: `matchMedia('(prefers-color-scheme:dark)').addEventListener('change', ...)` — iOS 18+ live reaction в auto mode
- Click handlers: btn toggle menu, items setMode+close, document click outside, **`stopPropagation` обов’язковий** щоб btnTheme/item клік не закривав через document listener

-----

### 14.7 CSS Variables архітектура ✅ 1:1

**3-шарова схема для теми:**

```css
:root{
  /* Default = light values */
  --bg:#f7f4ec; --card:#fff; --ink:#1a1b1e; --accent:#2A8C84;
  /* ...повний tokens набір */
  --sab: env(safe-area-inset-bottom, 0px);
}

[data-theme="dark"]{
  /* Manual dark override (через dropdown) */
  --bg:#0d1117; --card:#1c2128; --ink:#e6edf3;
}

@media(prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    /* Auto dark (system preference + no manual light override) */
    --bg:#0d1117; --card:#1c2128; --ink:#e6edf3;
  }
}
```

**Логіка:**

- `data-theme="light"` → завжди light (override media)
- `data-theme="dark"` → завжди dark (override media)
- Без `data-theme` атрибуту → media query керує (auto = system)
- `html{background: var(--bg)}` — overscroll bounce показує правильний колір теми

-----

### 14.8 Viewport units — `dvh` замість `vh` ✅ 1:1

```css
#app           { height: 100dvh; }
.sh-box        { max-height: 85dvh; }
.empty-state   { min-height: 55dvh; }
```

`vh` (static) використовує найбільший viewport з PWA контексту — у Safari з видимим toolbar дає БІЛЬШЕ ніж видимий простір → layout вилазить за межі.

`dvh` = реальний видимий viewport в момент рендеру (Safari toolbar tracked).

**Підтримка:** iOS Safari 15.4+ (iPhone XS iOS 18 — OK).

-----

### 14.9 Safe-area-inset правила ✅ 1:1

```css
.app-bar {
  padding: max(18px, calc(env(safe-area-inset-top, 0px) + 12px)) 16px 8px;
}

.sh-box {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

:root {
  --sab: env(safe-area-inset-bottom, 0px);
}
```

**Правила:**

- НЕ додавати арбітрарні pixels поверх `env(safe-area-*)` (Apple HIG: 21pt вже достатньо, env() повертає ≥34pt)
- `max(18px, ...)` — fallback якщо env() недоступний (старі браузери, Safari без viewport-fit=cover)
- `--sab` CSS variable: PWA = 34pt, Safari = 0 (Safari toolbar бере відповідальність на себе)

**НЕ базувати detection PWA-режиму на `--sab` значенні** — використовувати `@media (display-mode: standalone)` або `navigator.standalone`.

-----

### 14.10 PWA detection — display-mode + heuristic ✅ 1:1

```js
(function(){
  const isS = window.matchMedia('(display-mode:standalone)').matches || navigator.standalone;
  if(!isS) return;
  const sab = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sab')) || 0;
  if(sab > 0){
    const d = window.innerHeight - (screen.height - sab);
    if(d > sab * .5) document.documentElement.classList.add('pwa-full');
  }
})();
```

**Логіка:**

1. `matchMedia('(display-mode:standalone)')` — стандарт для PWA detection
1. `navigator.standalone` — iOS Safari додає це property на window для додатків з home screen
1. Heuristic перевірка через різницю `innerHeight` vs `screen.height - sab` — додає клас `pwa-full` на html для умовних стилів (особливо bottom nav)

-----

### 14.11 VisualViewport API — tight-vh / roomy-vh ✅ 1:1

**Реактивне відстеження висоти viewport через `visualViewport` API** (синхронно з появою/зникненням Safari toolbar).

```js
(function(){
  const vv = window.visualViewport;
  function checkVh(){
    const vh = vv ? vv.height : window.innerHeight;
    document.body.classList.toggle('tight-vh', vh < 720);
    document.body.classList.toggle('roomy-vh', vh > 790);
  }
  if(vv){
    vv.addEventListener('resize', checkVh);
    vv.addEventListener('scroll', checkVh);  // Safari toolbar show/hide
  } else {
    window.addEventListener('resize', checkVh);
  }
  checkVh();
})();
```

**3-режимна архітектура:**

- `vh < 720` → `body.tight-vh` (iPhone SE / Safari toolbar активний на старих)
- `720 ≤ vh ≤ 790` → default (Safari toolbar ON на сучасних, iPhone XS PWA = 778)
- `vh > 790` → `body.roomy-vh` (PWA на iPhone Pro+, Safari toolbar OFF на сучасних)

CSS використовує ці класи для конкретних адаптацій (для Drive Lens: розмір паливоміра у формі, padding у `.empty-state`, font-size у Status line).

-----

### 14.12 5-layer top stack architecture ✅ 1:1

```html
<div id="app">
  <header class="app-bar">           <!-- Brand + active day pill + theme btn + sync indicator -->
  <div id="ph-banner">               <!-- PHBanner: активний день (тап→календар) + 🏠 -->
  <div id="ctx-layer">               <!-- Status line: "🔧 75км · 👤 16км · 💧 8/12 · Запас 222км" -->
  <div class="screens">              <!-- Контейнер 4 табів з .scroll-a всередині -->
    <div class="screen active" id="sc-overview">...
    <div class="screen" id="sc-journal">...
    <div class="screen" id="sc-fuel">...
    <div class="screen" id="sc-month">...
  </div>
  <nav class="bottom-nav">           <!-- 4-tab navigation -->
</div>
```

**Та сама архітектура що у QR Lens** — переноситься 1:1, лише вміст табів інший.

🔧 **Адаптовано:**

- `app-bar` → додатково `.sync-pill` (offline indicator) праворуч від `.sr-pill`
- `ph-banner` → дата замість аптеки, тап → date picker замість sheet вибору
- `ctx-layer` → 4 status pills (робочий пробіг, особистий, паливо, запас)
- `screens` → нові ID (sc-overview, sc-journal, sc-fuel, sc-month)
- `bottom-nav` → нові tab labels (Огляд, Журнал, Паливо, Місяць)

-----

### 14.13 Bottom Nav — 3-state padding (Batch 8h critical) ✅ 1:1

**Найважливіший fix для tab bar у PWA:**

```css
.bottom-nav{
  display: flex;
  background: var(--card);
  border-top: 1px solid var(--border);
  padding-bottom: 8px;                                /* Safari default */
}

@media(display-mode:standalone){
  .bottom-nav{ padding-bottom: 0; }                   /* PWA: контейнер БЕЗ padding */
}

html.pwa-full .nav-i{                                 /* PWA: padding на ELEMENT */
  padding-top: 8px;
  padding-bottom: calc(8px + var(--sab));
}
```

**Чому 3 стани:**

- **Safari:** nav контейнер має 8px знизу — нормальна відстань
- **PWA standalone:** контейнер БЕЗ padding-bottom бо кожна `.nav-i` кнопка отримує власний padding всередині через клас `pwa-full`
- **Anti-pattern (попередня версія Batch 8e):** додавав padding на контейнер у PWA → надмірна порожнеча між іконками і home indicator

**Без цього у Drive Lens буде:** або порожнеча між іконками і home indicator, або іконки під home indicator (нетапаються).

-----

### 14.14 App-bar scroll elevation ✅ 1:1

App-bar отримує `box-shadow` коли активний `.scroll-a` контейнер скроливсь >8px — premium feel native додатка.

```css
.app-bar{
  transition: box-shadow .15s, border-color .15s;
}
.app-bar.scrolled{ box-shadow: var(--sh2); }
```

```js
const _appBar = document.querySelector('.app-bar');
document.querySelectorAll('.scroll-a').forEach(el => {
  const screen = el.closest('.screen');
  let ticking = false;
  el.addEventListener('scroll', () => {
    if(ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      if(screen && screen.classList.contains('active')){
        _appBar.classList.toggle('scrolled', el.scrollTop > 8);
      }
      ticking = false;
    });
  }, {passive: true});
});

// Reset при tab switch
function setTab(t){
  // ...
  document.querySelector('.app-bar').classList.remove('scrolled');
}
```

**Кешований селектор `_appBar` + RAF throttle** — оптимально для performance.

-----

### 14.15 Bottom sheet — структура ✅ 1:1

```html
<div class="sh-bg" id="sh-add-snapshot">
  <div class="sh-box">
    <div class="sh-grip-w"><div class="sh-grip"></div></div>
    <div class="sh-head">
      <span class="sh-title">Додати запис</span>
      <button class="sh-x" onclick="closeSheet('sh-add-snapshot')">×</button>
    </div>
    <!-- content -->
  </div>
</div>
```

```css
.sh-bg{
  position: fixed; inset: 0;
  background: rgba(0,0,0,.5);
  z-index: 300;
  display: none;
  align-items: flex-end;
}
.sh-bg.open{ display: flex; }

.sh-box{
  background: var(--card);
  border-radius: 16px 16px 0 0;
  width: 100%;
  max-height: 85dvh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  box-shadow: 0 -4px 20px rgba(0,0,0,.10);
}

.sh-grip-w{ padding: 10px 0 4px; display: flex; justify-content: center; }
.sh-grip{ width: 36px; height: 4px; background: var(--border-2); border-radius: 2px; }
```

-----

### 14.16 Bottom sheet — swipe-to-close (wsd canonical pattern) ✅ 1:1

```js
function addSwipeClose(bgId, closeFn){
  const box = document.querySelector('#' + bgId + ' .sh-box');
  if(!box || box._sw) return;     // ← guard: listener реєструється раз за life
  box._sw = true;
  let sy = 0, ss = 0, gt = false;
  box.addEventListener('touchstart', e => {
    sy = e.touches[0].clientY;
    ss = box.scrollTop;
    gt = !!e.target.closest('.sh-grip-w');
  }, {passive: true});
  box.addEventListener('touchend', e => {
    const dy = e.changedTouches[0].clientY - sy;
    if(gt && dy > 40) closeFn();                  // grip: dy > 40px
    else if(ss === 0 && dy > 64) closeFn();       // content: scrollTop===0 AND dy > 64px
  }, {passive: true});
}
```

**Правила:**

- Grip зона: `dy > 40px` → завжди закриває
- Контент зона: закриває ТІЛЬКИ якщо `scrollTop === 0` при touchstart AND `dy > 64px`
- Один touchstart listener фіксує `startY` + `startScroll` + `gripTouch`

**Не використовувати** просте `dy > N` без перевірки `scrollTop` — це агресивне закриття при спробі скролити контент вгору.

-----

### 14.17 Bottom sheet — 3 способи закриття ✅ 1:1

```js
// 1. Кнопка X у sh-head
<button class="sh-x" onclick="closeSheet('sh-add-snapshot')">×</button>

// 2. Свайп вниз (grip dy>40 АБО content + scrollTop===0 + dy>64)
addSwipeClose(id, closeFn);

// 3. Тап на backdrop (e.target === e.currentTarget = тап саме на .sh-bg, не на .sh-box всередині)
document.getElementById('sh-add-snapshot').addEventListener('click', e => {
  if(e.target === e.currentTarget) closeSheet('sh-add-snapshot');
});
```

-----

### 14.18 Listener registration “once for life” ✅ 1:1

**Pattern guard через property на DOM element:**

```js
function addSwipeClose(bgId, closeFn){
  const box = document.querySelector('#' + bgId + ' .sh-box');
  if(!box || box._sw) return;     // ← guard
  box._sw = true;
  // ... listener registration
}
```

**Чому:** елементи sheet persist у DOM (не destroyed при close). Без guard кожне відкриття додає listener → N відкриттів = N callbacks per swipe → accumulation bug.

**Альтернатива:** WeakSet для трекінгу зареєстрованих елементів. Але DOM property простіше і працює.

-----

### 14.19 Orientation lock через CSS overlay ✅ 1:1

```css
@media (orientation:landscape) and (max-width:900px){
  body{ overflow: hidden; }
  #app{ display: none !important; }
  body::before{
    content: "";
    position: fixed; inset: 0; z-index: 9999;
    background: var(--bg);
    display: flex; align-items: center; justify-content: center;
  }
  body::after{
    content: "Поверніть телефон вертикально";
    position: fixed; inset: 0; z-index: 10000;
    display: flex; align-items: center; justify-content: center;
    color: var(--ink);
    font-size: 17px; font-weight: 600; text-align: center;
    padding: 32px; letter-spacing: -0.2px; line-height: 1.4;
  }
}
```

**Чому CSS overlay, не native API:**

- iOS НЕ підтримує `screen.orientation.lock()` (native-only)
- `manifest "orientation": "portrait"` iOS **ігнорує**
- `max-width: 900px` виключає планшети-у-landscape (там layout природно адаптується)

-----

### 14.20 iOS системні CSS правила ✅ 1:1

```css
/* Глобальні reset + iOS-specific */
*,*::before,*::after{ box-sizing: border-box; margin: 0; padding: 0; }
html, body, #app{ touch-action: pan-x pan-y; }
html{ -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }  /* Batch 17: блок double-tap autofit */
html{ background: var(--bg); }                                   /* overscroll bounce = theme color */
html, body{ height: 100%; overflow: hidden; overscroll-behavior: none; }
body{
  font-family: 'Manrope', sans-serif;
  color: var(--ink);
  font-size: 14px; line-height: 1.4;
  -webkit-font-smoothing: antialiased;
  touch-action: manipulation;
  -webkit-user-select: none; user-select: none; -webkit-touch-callout: none;  /* Batch 18: блок long-press menu */
}
input, textarea{
  -webkit-user-select: text; user-select: text;
  -webkit-touch-callout: default;
}
input, select, textarea{ font-size: 16px !important; font-family: inherit; }  /* anti-zoom */
*{ -webkit-tap-highlight-color: transparent; }
button:disabled{ touch-action: none; pointer-events: none; }
.scroll-a{ -webkit-overflow-scrolling: touch; scrollbar-width: thin; }
#app{ max-width: 430px; margin: 0 auto; }                       /* desktop limit */
```

**Що кожне правило блокує:**

- `webkit-text-size-adjust:100%` — iOS auto text scaling при double-tap (Batch 17)
- `user-select:none` + `touch-callout:none` — long-press selection menu (Batch 18)
- `font-size:16px` на inputs — iOS auto-zoom при focus
- `tap-highlight-color:transparent` — сірий highlight на тап
- `touch-action:pan-x pan-y` — точне керування touch, доповнюється JS gesture block
- `overscroll-behavior:none` — pull-to-refresh + scroll chain
- `pointer-events:none` на display-only elements з inline `<em>` — double-tap autofit (Batch 17)

-----

### 14.21 Pinch-zoom JS block ✅ 1:1

**iOS Safari ігнорує `user-scalable=no` в meta** — треба JS preventDefault на gesture events:

```js
['gesturestart', 'gesturechange', 'gestureend'].forEach(ev => {
  document.addEventListener(ev, e => e.preventDefault(), {passive: false});
});
```

**`{passive: false}` обов’язково** — без цього `preventDefault()` не працює на iOS.

-----

### 14.22 Input attributes для форм 🔧 Адаптовано + 🆕 Нове

У QR Lens мінімум — тільки search inputs:

```html
<input type="search" autocomplete="off">
```

🆕 **Для Drive Lens числові форми** (snapshot одометра, заправка літрів) — повний набір:

|Поле               |Attributes                                                                                                           |
|-------------------|---------------------------------------------------------------------------------------------------------------------|
|Одометр (17 643.5) |`type="text" inputmode="decimal" pattern="[0-9]*\.?[0-9]*" enterkeyhint="next" autocomplete="off" spellcheck="false"`|
|Запас ходу (222 км)|`type="text" inputmode="numeric" pattern="[0-9]*" enterkeyhint="next" autocomplete="off"`                            |
|Літри (30.50)      |`type="text" inputmode="decimal" pattern="[0-9]*\.?[0-9]*" enterkeyhint="done" autocomplete="off"`                   |
|АЗС (text)         |`type="text" enterkeyhint="next" autocomplete="off" spellcheck="false"`                                              |
|Route notes        |`type="text" enterkeyhint="done" autocomplete="off" spellcheck="false"`                                              |
|Email (login)      |`type="email" inputmode="email" enterkeyhint="next" autocomplete="email"`                                            |
|OTP code           |`type="text" inputmode="numeric" pattern="[0-9]{6}" autocomplete="one-time-code" enterkeyhint="done" maxlength="6"`  |

**Критичне:**

- `inputmode="decimal"` — iOS показує numeric keyboard з крапкою
- `inputmode="numeric"` — тільки цифри (без крапки)
- `pattern="[0-9]*"` — fallback для старих iOS Safari
- `enterkeyhint` — label на Return key (Next/Done)
- `autocomplete="one-time-code"` — iOS пропонує OTP з SMS

-----

### 14.23 A11y attributes ✅ 1:1

**Theme dropdown:**

```html
<button aria-label="Тема" aria-haspopup="true" aria-expanded="false">...</button>
<div role="menu" hidden>
  <button role="menuitemradio">Авто</button>
</div>
```

**Dynamic update aria-label:** `'Тема: ' + lbl` (де lbl = “авто/світла/темна”) — VoiceOver читає поточний стан.

**Iconованiй кнопки навігації:**

```html
<button aria-label="Попередній день">←</button>
<button aria-label="Наступний день">→</button>
```

-----

### 14.24 Reduce motion + no-transition pattern ✅ 1:1

**Respect system reduce motion:**

```css
@media (prefers-reduced-motion: reduce){
  .theme-menu{ animation: none; }
  /* інші анімації */
}
```

**Prevent transition fade на launch** (CSS vars змінюються при applyTheme):

```css
.no-transition,
.no-transition *{ transition: none !important; }
```

```js
document.documentElement.classList.add('no-transition');
applyTheme();
requestAnimationFrame(() => {
  requestAnimationFrame(() => {            // ← double rAF
    document.documentElement.classList.remove('no-transition');
  });
});
```

**Double `requestAnimationFrame`** — стандартний trick (React/Vue) щоб гарантувати клас додано і видалено в різних frames.

-----

### 14.25 Storage event listener — multi-window sync ✅ 1:1

Користувач змінив тему у Safari tab → PWA на home screen теж оновиться:

```js
window.addEventListener('storage', (e) => {
  if (e.key === 'dl-theme') applyTheme();
});
```

**Працює:** Safari/Chromium/Firefox. Між Safari tab і PWA standalone — потребує iOS 17.4+.

🆕 **Для Drive Lens** — також синк activeDay якщо у localStorage:

```js
window.addEventListener('storage', (e) => {
  if (e.key === 'dl-theme') applyTheme();
  if (e.key === 'dl-active-day') refreshPHBanner();
});
```

-----

### 14.26 SVG icons inline + стандартні розміри ✅ 1:1

**Усі icons inline SVG, не external icon font:**

- `stroke="currentColor"` → керується через CSS `color`
- `fill="none"` для outline стилю
- `stroke-width="2"` (стандарт), `1.8` (subtle), `2.5` (bold)
- `stroke-linecap="round" stroke-linejoin="round"` — м’які лінії

**Стандартні розміри (QR Lens):**

|Контекст                         |Розмір|
|---------------------------------|------|
|Chevron (sr-pill, картки)        |12×12 |
|Icons у menu items, search/filter|14×14 |
|Theme button, sh-x close         |16×16 |
|Bottom nav tabs                  |20×20 |
|Empty state                      |34×34 |
|QR-nav arrows                    |18×18 |

🆕 **Для Drive Lens нові icons** (треба знайти/намалювати):

- Машина (для empty state Журналу)
- Паливна колонка (для taб Паливо)
- Календар (для PHBanner trigger)
- 🏠 Home (для “Сьогодні” button у PHBanner)
- Графік / chart (для табу Місяць)
- Sync indicator (cloud / refresh / wifi-off)

**Зберегти:** sun + moon (theme), magnifying glass (search), funnel (filter), X (close), chevrons (nav), checkmark (active state).

-----

### 14.27 Premium polish ✅ 1:1

**1. Horizontal scroll fade edges (для chips):**

```css
.dl-chips{
  display: flex;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-mask-image: linear-gradient(to right,
    transparent 0, #000 20px,
    #000 calc(100% - 20px), transparent 100%);
  mask-image: linear-gradient(...);
}
.dl-chips::-webkit-scrollbar{ display: none; }
```

**2. Status tint backgrounds через `color-mix`:**

```css
.day-card[data-type="sick"]{
  background: linear-gradient(180deg, var(--card) 0%,
              color-mix(in srgb, var(--warn) 6%, var(--card)) 100%);
}
```

Працює iOS Safari ≥ 16.2 (iPhone XS iOS 18 OK).

**3. Micro tap feedback з `transform: scale`:**

```css
.cta-btn:active{
  background: var(--accent-soft);
  transform: scale(.97);
  color: var(--accent);
}
```

Не на всіх кнопках — тільки на ключових (CTA “+ Додати запис”, picker “Тип дня”, PHBanner trigger).

**4. Live indicator pulse:**

```css
.live-dot{
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--ok);
  animation: livePulse 2s ease-in-out infinite;
}
@keyframes livePulse{
  0%, 100%{ opacity: 1; transform: scale(1); }
  50%{ opacity: .35; transform: scale(.75); }
}
```

🆕 **Для Drive Lens — використовується у sync indicator** при стані “Sync…”.

-----

### 14.28 Z-index стек ✅ 1:1

|Шар                     |z-index     |
|------------------------|------------|
|App-bar (scrolled state)|20          |
|Theme menu dropdown     |200         |
|Bottom sheets (.sh-bg)  |300         |
|Orientation lock overlay|9999 / 10000|

🆕 **Drive Lens додатково:**

- Date picker bottom sheet — 300 (як інші sheets)
- Sync toast (top of screen) — 250 (вище app-bar, нижче sheets)
- Onboarding overlay — 9000 (вище всього крім orientation lock)

-----

### 14.29 Empty state pattern ✅ 1:1

```css
.empty-state{
  padding: 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  min-height: 55dvh;          /* vertical centering на будь-якому vh */
}
.empty-ico{
  width: 76px; height: 76px;
  background: var(--bg-soft);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.empty-txt{ font-size: 15px; font-weight: 600; color: var(--muted); }
.empty-hint{ font-size: 13px; color: var(--muted-2); line-height: 1.55; }
.goto-btn{
  padding: 10px 24px;
  background: var(--accent);
  color: #fff;
  border-radius: var(--r);
  font-size: 13px; font-weight: 700;
  border: none; cursor: pointer;
}
```

🆕 **Drive Lens empty states:**

- Журнал (нема даних) → “Поки немає записів. Тапни ‘+ Додати запис’ на Огляді щоб почати.”
- Паливо · Місяць (нема заправок) → “Заправок у цьому місяці немає”
- Onboarding finished → first Огляд з готовим snapshot-ом (не empty state)

-----

## Нове для Drive Lens — не було в QR Lens

### 14.30 🆕 Service Worker + offline queue (HIGH PRIORITY)

QR Lens read-only → offline = “перегляньмо що є локально”. Drive Lens read-write → offline = “записати поїздку зараз, синкнути пізніше”.

**Архітектура:**

```
sw.js (Service Worker)
├─ Install: cache static assets (HTML, CSS, JS, icons)
├─ Fetch: cache-first для static, network-first для Supabase API
└─ Sync event: try flush offline queue (Background Sync API де доступно)

IndexedDB
├─ Store "snapshots_queue" — pending writes
├─ Store "refuels_queue" — pending writes
└─ Store "cache" — last synced data для read-only під час offline
```

**Worker registration:**

```js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/drive-lens/sw.js?v=batch01');
  });
}
```

**Online/offline listeners:**

```js
window.addEventListener('online',  () => syncPendingQueue());
window.addEventListener('offline', () => updateSyncIndicator('offline'));
```

-----

### 14.31 🆕 IndexedDB для unsaved snapshots

**Чому не localStorage:**

- localStorage = 5MB ліміт, синхронне API (блокує main thread)
- IndexedDB = асинхронне, великий ліміт, indexed queries

**Структура:**

```js
const DB_NAME = 'drive-lens-db';
const DB_VERSION = 1;
const stores = ['snapshots_queue', 'refuels_queue', 'days_cache'];

// Wrapper над IDB (можна використати idb-keyval бібліотеку)
async function queueSnapshot(snapshot){
  const db = await openDB();
  await db.put('snapshots_queue', {
    ...snapshot,
    id: crypto.randomUUID(),
    created_at: new Date().toISOString(),
    sync_status: 'pending'
  });
  updateSyncIndicator('pending', await countPending());
}
```

-----

### 14.32 🆕 Sync indicator у app-bar

**Розміщення:** у `.app-bar` зправа від `.sr-pill` (де у QR Lens був theme button).

**4 стани:**

|Стан     |UI                                             |Колір |
|---------|-----------------------------------------------|------|
|`synced` |`🟢 Синхронізовано` (зникає через 2с після sync)|green |
|`syncing`|`🟡 Синхронізую...` + `.live-dot` pulse         |accent|
|`pending`|`🟠 N записів у черзі`                          |warn  |
|`offline`|`🔴 Offline` + `pending` суфікс якщо є черга    |crit  |

```html
<button class="sync-pill" id="syncBtn" aria-label="Стан синхронізації">
  <span class="sp-dot live-dot"></span>
  <span class="sp-text" id="syncText">Синхронізовано</span>
</button>
```

**Тап на pill** → відкриває bottom sheet з деталями черги (опційно у v1).

-----

### 14.33 🆕 Supabase realtime sync (один user, кілька пристроїв)

Користувач має iPhone + iPad. Записав поїздку на iPhone — iPad має оновитись.

```js
const channel = supabase
  .channel('user_changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'snapshots',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    handleRealtimeChange(payload);
  })
  .subscribe();
```

**Optimistic UI flow:**

1. User додає snapshot → запис у IndexedDB queue з `sync_status: 'pending'`
1. UI оновлюється одразу (snapshot з’являється у Огляді)
1. Async: POST до Supabase
1. Success → IDB `sync_status: 'synced'`, видалити з queue, оновити sync indicator
1. Conflict (timestamp clash) → last-write-wins, alert toast “Запис оновлено з іншого пристрою”

-----

### 14.34 🆕 VisualViewport для клавіатури в bottom sheet

**Проблема:** у формі snapshot/refuel iOS клавіатура з’являється при focus → перекриває CTA “Зберегти” → користувач не бачить кнопку.

**Рішення:** `window.visualViewport.height` listener — переміщує bottom sheet (або resize) при появі клавіатури.

```js
function trackKeyboard(sheetBoxEl){
  if(!window.visualViewport) return;
  const vv = window.visualViewport;
  const initialHeight = vv.height;
  vv.addEventListener('resize', () => {
    const kbHeight = initialHeight - vv.height;
    if(kbHeight > 100){
      sheetBoxEl.style.maxHeight = `calc(${vv.height}px - 20px)`;
      sheetBoxEl.style.paddingBottom = '20px';  // override env() — клавіатура замість home indicator
    } else {
      sheetBoxEl.style.maxHeight = '';
      sheetBoxEl.style.paddingBottom = '';
    }
  });
}
```

**Реєструвати при відкритті sheet з формою** (не глобально — `visualViewport.resize` спрацьовує і на Safari toolbar appear).

-----

### 14.35 🆕 Numeric input — кастомний паливомір (12 поділів)

**Не звичайний `<input type="number">`** — візуальний селектор 12 поділів (4 великі × 3 малі).

```html
<div class="fuel-gauge" role="slider"
     aria-label="Рівень палива"
     aria-valuemin="0" aria-valuemax="12" aria-valuenow="8">
  <div class="fg-track">
    <div class="fg-tick" data-value="0"></div>
    <div class="fg-tick fg-tick-major" data-value="3"></div>
    <div class="fg-tick" data-value="1"></div>
    <!-- ...12 ticks total, кожен 3-й major -->
  </div>
  <div class="fg-fill" style="width: 66.67%"></div>  <!-- 8/12 -->
  <div class="fg-value">8/12 (≈ 33.6 л)</div>
</div>
```

**Логіка вводу:**

- Tap на tick → встановити значення
- Drag по track → smooth selection
- A11y: arrow keys для accessibility (←/→)

**Опційне поле “Запас ходу”:**

```html
<input type="text" inputmode="numeric" pattern="[0-9]*"
       placeholder="Запас ходу (км)" autocomplete="off">
```

-----

## Чек-лист імплементації iOS PWA

Перед deploy на колег пройти:

- [ ] Manifest.json валідний (Chrome DevTools → Application → Manifest)
- [ ] Усі 7 іконок створено та доступні
- [ ] Cache-busting `?v=batch01` синк у HTML(5x) + manifest(3x)
- [ ] Service Worker registered і встановився (Application → Service Workers)
- [ ] FOUC inline script у `<head>` ПЕРЕД CSS link
- [ ] Theme dropdown працює: auto/light/dark, persist після reload
- [ ] `dvh` всюди (не `vh`) для max/min-height
- [ ] `env(safe-area-*)` без додаткових pixels
- [ ] Bottom nav padding correct у Safari + PWA mode
- [ ] Bottom sheets: X / swipe / backdrop — всі 3 способи закриття
- [ ] Swipe-to-close: grip 40px / content 64px + scrollTop check
- [ ] Orientation lock CSS overlay показується у landscape
- [ ] Input zoom prevention: `font-size: 16px !important`
- [ ] Pinch-zoom blocked (gesture events preventDefault)
- [ ] Numeric inputs: inputmode/pattern/enterkeyhint правильні
- [ ] VisualViewport keyboard handling у формах sheets
- [ ] Offline mode: запис без мережі → з’являється у Огляді → з sync indicator pending
- [ ] Online відновлено → автоматичний sync → indicator green
- [ ] Multi-device: запис на iPhone → з’являється на iPad через realtime
- [ ] System theme change (iOS Settings) → auto mode реагує live (iOS 18+)
- [ ] Storage event: theme change у Safari tab → PWA window оновлюється

-----

**Кінець розділу 14 / Concept v1.2.**

Усі реалізаційні патерни мають перевірений source у `QR_Lens_preview_batch22.html`. Для будь-якого пункту з цього розділу — точний referenced code знайти grep’ом у тому файлі.