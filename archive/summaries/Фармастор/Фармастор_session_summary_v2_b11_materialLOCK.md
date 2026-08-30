# Фармастор v2 — session summary · b11 (material LOCK + A45 canon-delta)

Продовження після b10 (CTA-дизайн-лок). Ця сесія: **material-bench v1→v2 device-locked** + канон-дельта (корінь місячної light/dark friction). Код у продукт НЕ писався. Наступний чат: MASTER_LOCK-апдейт + **код Node8-хвоста**.

---

## 0 · Файли створені цю сесію (outputs)
- `Farmastor_material_bench_v1.html` — перший material-bench (пресети+per-theme розчеплені). **Superseded v2.**
- `Farmastor_material_bench_v2.html` — **АКТУАЛЬНИЙ**. Dark-копі керується КОЛЬОРОМ (sat/lit/glift/ridge), світлий shadow-важіль прибрано з dark (A45). Konst: «преміум-оформлення, інший рівень».
- `canon_delta_A45_material_lever_manifest.md` — **канон-дельта, чекає мержу** (governance-сесія, НЕ inline у Cookbook).
- `_konst_bench_v1_readout.md` — проміжний readout (ігнор).
- цей самері.

---

## 1 · ЗАЛОЧЕНО цю сесію

### 1.1 MATERIAL LOCK — FILL копі+Excel CTA (device✓ Konst, XS+Pro)
Форма-стиль = **soft** (не out·neu). Layout = **поруч 2.5:1** (лідер, Konst «подобається» — фінальний device-підтвердж на першому погляді наступного чату; НЕ переоткривати без сигналу).

**Розв'язані CSS (порт-готові, з bench v2 builders @ locked values):**

LIGHT · копі (`.btn-copy`):
```css
background:linear-gradient(180deg,color-mix(in srgb,#fff 16%,var(--accent)),var(--accent));
box-shadow:0 3px 10px -3px color-mix(in srgb,var(--accent) 27%,transparent),0 1px 2px rgba(20,50,42,.14);
```
LIGHT · форма soft (`.btn-form`):
```css
background:color-mix(in srgb,var(--accent) 9%,#fff);
border:1.5px solid color-mix(in srgb,var(--accent) 20%,transparent);
color:color-mix(in srgb,var(--accent-ink) 63%,var(--accent));
box-shadow:0 1.5px 4px -2px rgba(20,50,42,.10);
```
DARK · копі (`[data-theme=dark] .btn-copy`) — **власна насичена зелень, НЕ --accent токен:**
```css
background:linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%));
box-shadow:inset 0 1px 0 rgba(255,255,255,.10);
```
DARK · форма soft (`[data-theme=dark] .btn-form`):
```css
background:color-mix(in srgb,var(--accent) 18%,var(--surface-3));
border:1px solid color-mix(in srgb,var(--accent) 26%,var(--border));
color:color-mix(in srgb,var(--accent-ink) 58%,var(--accent));
box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
```
**Провенанс dark-копі:** Konst device-pick `hsl(163 55% 30%)` — S=55 тримає густоту без OLED-неону, L=30 дає тіло. Баланс «не приглушено / не кричить». `.btn-copy{color:#fff}` — білий лейбл (контраст ок на L=30).

### 1.2 Excel deep-link + CSV-split + About — контракт незмінний з b10
(розміщення, ORDER_FORM_URL, UL-механіка, context-split лейбли, A58 About) — див. b10 §1.1–1.3. Готове до коду.

**ORDER_FORM_URL (дослівно):**
```
https://rbcom-my.sharepoint.com/:x:/r/personal/yuliia_syniuhina_reckitt_com/_layouts/15/Doc.aspx?sourcedoc=%7B361AB6BF-2AE9-410C-A81F-2AA3502C4EAD%7D&file=%25u0424%25u0430%25u0440%25u043c%25u0430%25u0441%25u0442%25u043e%25u0440%20%25u0437%25u0430%25u043c%25u043e%25u0432%25u043b%25u0435%25u043d%25u043d%25u044f%20%25u0442%25u0442.xlsx&wdLOR=c06833412-A6C7-4B15-AE95-76BCF4AB9FD6&openShare=true&fromShare=true&action=default&mobileredirect=true
```

### 1.3 Канон-дельта A45 → material lever MANIFEST (device-незалежне)
Корінь місячної friction «важелі темна/світла»: A45 давав ПРИНЦИП, не операційний чек-лист важелів → Claude переносив світлову модель глибини (shadow+white-grad) на темну = мертвий shadow-важіль + пропущений sat/lit. Дельта = **манифест базових важелів per роль×тема** + 5 твердих правил. Файл `canon_delta_A45_material_lever_manifest.md`. **Рішення governance: БАНК (не inline у роздутий Cookbook) → мерж у governance/split-сесії як чистий Skills-запис.**

---

## 2 · ВІДКРИТІ ЗАДАЧІ

### 🔴 HIGH
- **CODE Node8-хвоста** (наступний чат, на команду) — у продукт `b9→b10`:
  1. Excel deep-link: FILL-кнопка (поруч 2.5:1 + material LOCK §1.1) + Home ••• меню-рядок; `ORDER_FORM_URL` const; `<a target=_blank rel=noopener>`.
  2. CSV context-split: `openSheet` детект екрана (curPx/s-fill) + динам-лейбл + CSV-генератор (§4).
  3. About sheet (A58): APP_BUILD + автор + `.tgpill`.
  - Спершу: апдейт MASTER_LOCK §4 (Excel deep-link + material LOCK CSS §1.1).
- **ДИЗАЙН-ДІРА: дуга-кільце схована власним успіхом.** Анімацію arc-fill (§5.2/§6.4, довго робили) видно ЛИШЕ на кинутому шляху (заповнив картку → вийшов БЕЗ копі). Основний шлях (копі → «перенесено» бліда картка з 2-галочками) кільце ХОВАЄ. Клас: «на якому шляху юзер реально це бачить?». Напрями (harness-first, device): (a) показати дугу/її версію і в transferred-стані; (b) програти arc-fill як нагороду-celebration у момент копі (FILL або повернення на Home); (c) переосмислити де живе дуга. НЕ вирішено — design open.

### 🟡 MEDIUM
- **Count-бар у шапці FILL майже невидимий** (0→83 прогрес до повного SKU). Світла — 0 видимості, темна — ледь. → прямий тест-кейс нового A45-манифесту (fill+track контраст per-theme, val-L/mut-L обидві). Полагодити при коді Node8 або окремо.
- **MASTER_LOCK §5.1 — переписати метрику на shortfall-траєкторію** (з b10 §1.4): `s=max(0,N−V)`; s↓=ok, s↑=warn→crit, s=0=muted, s>0-застряг=warn; V1=0→crit форсовано; tier-per-visit; absent→«—». Δ first-class; шапка count-strip `↑N↓N=N` + слово-вердикт TBD.
- **Динаміка §5.1 UI** — harness-рядок (shortfall-колір + V0→V1 + Δ-чіп + count-strip; слово both-ways) → mock-first екран `s-dyn` (реюз catSec/brandCard/dchip). Слово-вердикт pending device: «Дозавантажили/Недозавантажили» [лідер] / «Стало краще/гірше» / «Норму тримає/Просіли».

### 🟢 LOW / GOVERNANCE
- **Мерж канон-дельти A45-манифесту** → у governance/split-сесії (не зараз). Додати в `wsd_TODO_running`.
- **Governance-розбиття величезних файлів** (Cookbook/wsd) на Skills-подібні гострі референси — TODO, окрема сесія. Konst-пріоритет: спершу продукт (Node8), потім governance.
- MASTER_LOCK §4: Excel deep-link (розміщення+URL+UL) — ДОДАТИ при §1.1-апдейті.

---

## 3 · Токени/якорі (реф)
- Продукт: `Фармастор_замовлення_v2_port_b9.html` (copy-cta р.357 · openSheet Home р.400 / FILL р.417 · copyValues р.1002) — НЕ змінений цю сесію.
- Кольори: `--accent hsl(162 82% 27%)` light / `hsl(163 46% 46%)` dark · `--accent-ink` · `--surface-3` · dark-копі-fill = **власна `hsl(163 55% 30%)`** (не токен).
- Cookbook: A45 (dark tone-lift → **+ material lever MANIFEST дельта**) · A57 (motion) · A58 (About/grouped) · A67 (press) · δ-чіп `.dchip`.
- MASTER_LOCK: §1 visits/tier · §3 norm · §4 copy+CSV+Excel · §5.1 Динаміка · §5.2/§6.4 Home-картка+arc.

---

## 4 · Уроки цієї сесії (generalizable)
- **Theme-aware матеріал = РІЗНІ НАБОРИ важелів per-theme, не спільний набір із різними значеннями.** Глибина народжується різною фізикою: світла = shadow+white-sheen; темна = сам колір заливки (sat/lit)+tone-lift+ridge. Корінь місячної friction: Claude переносить світлову модель → мертвий dark-shadow важіль + пропущені sat/lit.
- **Dark solid-fill: saturation(S)+lightness(L) заливки — ЦЕ матеріал.** Accent-токен приглушений заради легібельності тексту → як велика заливка = washed «салатовий». `glift` = in-hue tone-lift верху, НІКОЛИ white-inject (білий сіро-гасить відтінок). Велика dark-кнопка може мати власний насичений fill ≠ text-accent токен.
- **Governance-файли = де-факто Skills.** Роздуті файли розбивати на гострі single-responsibility референси; новий канон при наявності split-TODO — **банкувати як чистий standalone-запис до split-моменту**, не вливати в роздутий файл (розгрібати двічі).
- **Design-logic діра-клас: любовно зроблена анімація може бути структурно схована основним успішним шляхом.** Перевірка: «на якому шляху юзер це реально бачить?» (arc-ring видно лише на кинутому fill-no-copy шляху).
- **Компер-якість зросла (Konst «преміум, інший рівень»):** grouped слайдер-картки з eyebrow-хедерами, копі-кнопка значень, пресети-бети, міні-легенда inline. Тримати цей стандарт оформлення бенчів.

---

## 5 · Перехід у новий чат — стартове повідомлення

```
Привіт! Продовжуємо Фармастор v2 — MASTER_LOCK-апдейт (material LOCK) + КОД Node8-хвоста.

Прочитай ПЕРЕД (wsd 1.1):
1. Work_Standard.md — протокол
2. Lens_iOS_cookbook.md — A45(+material lever manifest) · A57 · A58 · A67 · δ-чіп
3. Фармастор_v2_MASTER_LOCK.md — §4 · §5.1 · §5.2/§6.4
4. Фармастор_session_summary_v2_b11_materialLOCK.md — ПОВНИЙ стан + material LOCK CSS + відкриті задачі
5. canon_delta_A45_material_lever_manifest.md — канон-дельта (банк, мерж у governance-сесії)
6. Продукт: Фармастор_замовлення_v2_port_b9.html
7. Бенч-реф: Farmastor_material_bench_v2.html (device-locked значення)

ЗАВДАННЯ (по черзі, код на команду):
1. Апдейт MASTER_LOCK §4: material LOCK CSS (b11 §1.1) + Excel deep-link (розміщення+ORDER_FORM_URL+UL).
2. КОД Node8-хвоста у продукт b9→b10: (a) Excel deep-link FILL-кнопка [поруч 2.5:1 + material LOCK] + Home ••• меню-рядок, <a target=_blank rel=noopener>; (b) CSV context-split (openSheet детект екрана + динам-лейбл + генератор §4); (c) About sheet (A58).
3. Полагодити count-бар шапки FILL (невидимий; тест-кейс A45-манифесту, контраст per-theme).

ВІДКЛАДЕНО (не цей чат): дуга-кільце схована успіхом (🔴 design, harness-first) · §5.1 метрика shortfall + Динаміка UI · governance-split + мерж A45-дельти.

PENDING device: layout поруч 2.5:1 (фінальний погляд) · UL Excel-стрибок PWA→зовні · слово-вердикт Динаміки.

ПРАВИЛА: подвійне пояснення · без емодзі в UI (SVG/моно) · mock-first · harness-first · план→підтвердж→код · маркер останнім рядком · валідація перед delivery (node --check · tag-balance · grep-anchors · absent≠0 · diff-scope).
```
