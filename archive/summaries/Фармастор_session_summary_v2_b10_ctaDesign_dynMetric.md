# Фармастор v2 — session summary · b10 (CTA-design + Dynamics metric microscope)

Продовження після b9 (arc-fill port ✓ device, Node8 xlsx знесено ✓). Ця сесія — **дизайн-лок** (код НЕ писався у продукт; лише compare-харнеси). Наступний чат: material-bench → тоді код Node8-хвоста.

---

## 0 · Файли створені цю сесію (outputs)
- `Farmastor_fillcta_compare_v1/v2/v3.html` — компер копі+Excel CTA. **v3 = актуальний** (важелі-пресети: theme·width·form·Mat·label; reveal на grid 0fr→1fr; реальний form-link для UL-тесту).
- цей самері.

---

## 1 · ЗАЛОЧЕНО цю сесію

### 1.1 Excel deep-link (НОВА фіча — розширення §4 copy-contract)
- **Суть:** кнопка/лінк на онлайн-форму замовлення (SharePoint Excel), щоб копі→вставка без походу в Telegram. Звужує §4-вікно «дані у двох місцях».
- **Розміщення LOCK:** ОБИДВА — (a) **FILL, всередині картки** (post-copy вставка, головний шлях); (b) **Home ••• меню** рядком (утиліта «просто відкрити» + масштабований дім для N-лінків).
- **Лейбл LOCK = «Excel»** (не «Форма»): конкретне, само-пояснює двокрок `Копіювати→Excel`, закриває «колега не зрозуміє». Гліф — external-link SVG (box-arrow, mono, currentColor).
- **Механіка (техн.):** `<a href=ORDER_FORM_URL target="_blank" rel="noopener">` — НЕ `window.open()` (Universal Links надійніше на живому anchor-тапі). URL = const `ORDER_FORM_URL`. Universal Links = OS-рівень (домен sharepoint прописаний за Excel-app) → має відкрити Excel так само як з Telegram. **DEVICE-TEST pending** (рідкісні PWA→зовні кейси). Clipboard переживає app-switch (системний буфер) ✓.
- **Спліт (side-by-side) LOCK = 2.5:1** (копі:Excel).
- **МАЙБУТНЄ (deferred):** N-лінків → меню стає групою (A58 eyebrow «ФОРМИ»); URL per-network у даних; свайп-по-картці — відкладено (не треба поки один лінк).

**ORDER_FORM_URL (зберегти дослівно):**
```
https://rbcom-my.sharepoint.com/:x:/r/personal/yuliia_syniuhina_reckitt_com/_layouts/15/Doc.aspx?sourcedoc=%7B361AB6BF-2AE9-410C-A81F-2AA3502C4EAD%7D&file=%25u0424%25u0430%25u0440%25u043c%25u0430%25u0441%25u0442%25u043e%25u0440%20%25u0437%25u0430%25u043c%25u043e%25u0432%25u043b%25u0435%25u043d%25u043d%25u044f%20%25u0442%25u0442.xlsx&wdLOR=c06833412-A6C7-4B15-AE95-76BCF4AB9FD6&openShare=true&fromShare=true&action=default&mobileredirect=true
```

### 1.2 CSV-експорт — контекст-split LOCK
- Home-меню = «усі дані (N аптек)» · FILL-меню = «ця аптека».
- **Rationale (Konst):** масштаб на команду — не всі аптеки твої → не вантажити чужі → не чистити вручну. Single-файл рідкісний але незамінний (shareable для комерц-відділу; copyValues = ефемерний буфер).
- **Механіка:** і Home (р.400) і FILL (р.417) вже кличуть `openSheet()` → детект активного екрана (curPx/s-fill) в openSheet → динам-лейбл export-рядка. БЕЗ нового UI.
- Per-card іконка — відхилено. Свайп — deferred.

### 1.3 About sheet — LOCK (тривіально)
A58 pattern: `APP_BUILD` версія + автор + Telegram-піл. Без обговорення.

### 1.4 Динаміка §5.1 — МЕТРИКА переписана (мікроскоп)
**Було (b9 §2.4, ХИБНО):** колір за `d=|V−N|` (closer=ok/farther=warn/стоїть=muted).
**Два баги:** (1) над-норма: V0=N+5→V1=N+10 → |V−N|↑ → кодує warn (а це БІЛЬШЕ запасу = добре). Дистанція симетрична, MSL — ні (це підлога). (2) «стоїть=muted» неоднозначне: V0=V1<норми = дефіцит не закрито = «не дозавантажили» = те що інструмент ЛОВИТЬ, має бути warn.

**СТАЛО (LOCK) — метрика = shortfall (провал під мінімум):** `s = max(0, N−V)`
- s1<s0 (провал зменшився/закрився) → **покращення** → ok/accent
- s1>s0 (глибше під норму / впав із забезпечення в дефіцит) → **погіршення** → warn→crit
- s0=s1=0 (забезпечено обидва рази) → **спокій/muted** (бажаний стан)
- s0=s1>0 (застряг під нормою) → **warn** — «не дозавантажили»
- **V1=0 (порожня полиця) → crit ФОРСОВАНО** (успадкування FILL-семантики `saved===0→crit`, поверх траєкторії)
- tier-per-visit (§1): s0 рахується N0, s1 — N1; підняли тір → запас коректно «забезпечено→дефіцит». Це сила моделі.
- absent в одному візиті → «—»

**Важливо:** ця корекція виведена з НАШОГО §5.1 («нижче норми = сигнал», норма=floor), НЕ з GPT. GPT-роздуми (upload) спрацювали як ліхтарик — підсвітили дрейф b9-§2.4 від §5.1. **Канон виграв, GPT був інструментом (сторонньою думкою, не над каноном).**

### 1.5 Δ та шапка — ретракт моїх передчасних GPT-зсувів
- **Δ лишається first-class** (магнітуда = скільки дозамовляти). «Вторинний» (GPT) стосується ЛИШЕ того що колір веде норма-траєкторія, а не знак Δ. (Відкликав своє надмірне «Δ вторинний».)
- **Шапка:** лічильник `↑N ↓N =N` (фільтр-афорданс) — ЛИШАЄТЬСЯ. Editorializing-СЛОВО-вердикт → harness both-ways (з словом/без), device-вирішить. (Відкликав передчасний downgrade — порушував harness-first.)
- Роут `s-dyn` окремий — ЛИШАЄТЬСЯ (Fill=сьогодні, Динаміка=два минулі знімки; конфляція шкідлива). Візуально Fill-mode клон. GPT «режим Fill» = архітектурний реюз, примирено.

---

## 2 · PENDING (device-вердикт / наступний чат)

### 2.1 FILL layout копі+Excel — device-pick
Кандидати (компер v3): **поруч (2.5:1)** [мій лідер] / стек / reveal (grid 0fr→1fr). Konst: поруч подобається, але не докрутив через пресети.

### 2.2 MATERIAL — потрібен REAL slider-bench (наступний чат) 🔴
Кнопки були пласкі/бляклі («бракує матеріалу»). Додав Mat-пресети (flat/lift/rich, theme-aware, A45: light=тінь+градієнт, dark=tone-lift+ridge). Dark-паритет форми полагоджено (soft/out-neu підняті над карткою).
**АЛЕ пресети ≠ контроль.** Konst-мікроскоп на v3 rich:
- **light: форма-soft РОЗЧИНЯЄТЬСЯ** (бліда м'ята на білому, без краю → безформна). → потребує **hairline-бордер** (accent ~30-40%).
- **dark: копі-rich НАДТО ГУЧНИЙ** (accent+24% білого). → прибрати назад (~до lift-рівня, accent ~84%).
- Треба **per-theme розчеплені слайдери**.

### 2.3 Слово-вердикт Динаміки — pending pick
Напрям (harness fit+read): «Дозавантажили/Недозавантажили» [лідер, домен-верб] / «Стало краще/гірше» / «Норму тримає/Просіли» / своє.

### 2.4 Форма-стиль (soft vs out-neu) — злитий з material-bench (2.2)

---

## 3 · НАСТУПНИЙ ЧАТ — план

**A. Material-lock bench (перше):**
- Слайдери **per-theme (light/dark розчеплені):**
  - hero: gradient top-white-mix% · shadow-strength · (dark) inset-highlight-op
  - form(soft): fill-tint% · **border-op (light КРИТИЧНО — дати край)** · shadow
- обидві теми одночасно, copy-values (📋→string), пресети flat/lift/rich як «бети», міні-легенда.
- **Прогноз значень (старт бенча не з нуля):** light-soft +hairline border accent~35% · dark-copy rich→~accent84% (як lift) · lift лишається базою.
- Заодно докрутити form-стиль (soft vs out-neu vs +edge).

**B. Тоді КОД Node8-хвоста** (у продукт b9→b10):
1. Excel deep-link: FILL-кнопка (обраний layout+material) + Home-меню-рядок; ORDER_FORM_URL const; `<a target=_blank rel=noopener>`.
2. CSV контекст-split: openSheet детект екрана + динам-лейбл + CSV-генератор (§4).
3. About sheet (A58).

**C. Динаміка:** harness-рядок (shortfall-траєкторія колір + V0→V1 + Δ-чіп + count-strip; слово both-ways) → mock-first екран s-dyn (§5.1, реюз catSec/brandCard).

**Валідація перед delivery:** node --check · tag-balance · grep-anchors · absent≠0 invariant · diff-scope (wsd).

---

## 4 · Токени/якорі (реф)
- Продукт: `Фармастор_замовлення_v2_port_b9.html` (copy-cta р.357 · openSheet Home р.400 / FILL р.417 · copyValues р.1002)
- Кольори: `--accent hsl(162 82% 27%)` light / `hsl(163 46% 46%)` dark · `--accent-soft` · `--ok/--warn/--crit` · `--spring cubic-bezier(.34,1.56,.64,1)`
- Cookbook: A45 (dark=tone-lift) · A57 (motion) · A58 (grouped/About/disabled-reason) · A67 (press pointerdown/.is-pressed scale) · δ-чіп `.dchip` (FILL, реюз Динаміці)
- MASTER_LOCK: §1 visits/tier-per-visit · §3 norm-resolver · §4 copy+CSV · §5.1 Динаміка · §5.2 · §6.4

## 5 · Канон-борг (докинути у файли)
- MASTER_LOCK §4: Excel deep-link (розміщення+URL+UL-механіка) — ДОДАТИ
- MASTER_LOCK §5.1: перезаписати метрику на shortfall-траєкторію (замінити |V−N|); V1=0→crit; Δ first-class; шапка=count-strip+word-TBD
- Cookbook: material theme-split (A45-розширення: hero градієнт/тінь/ridge per-theme) — кандидат після bench-lock
