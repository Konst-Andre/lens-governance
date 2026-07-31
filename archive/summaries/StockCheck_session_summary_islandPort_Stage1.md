# StockCheck · session summary — island port Stage 1 (b15_1) + microscope

## 0. Контекст
StockCheck = мульти-мережева еволюція Фармастора. Ця сесія: залочили острівець-материал
(device-pick), звели NETS-реєстр, винесли stage-bench у окремий канон-файл, і **портували StockCheck-острівець
у реальний білд** (`Фармастор_замовлення_v2_port_b14_2.html` → `StockCheck_port_b15_1.html`), Stage 1 = HTML/CSS shell.
Konst device-тестував Stage 1 → мікроскоп зловив 2 корені (нижче §3).

## 1. Зроблено цю сесію
1. **Острівець-материал ЗАЛОЧЕНО** (device-pick harness v2, Konst-bet) → `StockCheck_island_glass_FINDINGS.md` §4-preset (пресет **Frosted-Liquid** = P1↔P2 гібрид) + per-theme деривативи + 4 port-carry-over. valuesLOCK §6 DEFERRED→✅.
2. **NETS-реєстр** → `StockCheck_NETS_register.md` — схема, fallback-ланцюг, 1 real якір (`add`=Аптека доброго дня, sun/green), 5 edge-стабів, net-switcher UI-масштаб за N (1→статик/2-6→switcher/≥7→пошук), paste-ready JS.
3. **Stage-bench канон** → `Lens_stagebench_manifest.md` (standalone; wsd/Cookbook **лінкують сюди**, не дублюють — де-роздута мета). Названо верхній рівень «stage-bench ⭐ = harness у девайс-симуляторі».
4. **Порт Stage 1** → `StockCheck_port_b15_1.html` (APP_BUILD `v2.6.0 · stockcheck-island.b15_1`): Route-1 скрол-конверсія (.app→host, екрани→absolute-fill скролери, #s-home = inner `.home-scroll` + острівець-оверлей + spacer), острівець-материал §4-preset per-theme (+auto-dark A69), comet(статик SVG)+SC-wordmark, net-badge(sun/green)+•••(44px), carry-over #2 (gap9) + #1-b (`overscroll-behavior:none`). toparea переїхав усередину острівця (transparent). Валідація: node --check ✓, теги ✓, 14 якорів ✓.

## 2. Канонічні параметри (актуальні)
- **Острівець §4-preset (device-locked, in-product verify pending):** scroll **B** · Frosted-Liquid · blur12 sat170 **op0.82** rim0.8 lift0.8 inset12 radius24 · val/mut 1. Per-theme: L `rgba(245,249,247,.82)`/rim`.137`/drop · D `rgba(38,51,46,.82)`/rim`.091`/ridge`.06`/lift`0 6px 18px -8px rgba(0,0,0,.40)`. Badge op1 lift0.5 **plate:false**. Comet-токени: L`hsl(162 72% 30%)`/`hsl(162 55% 66%)` · D`hsl(162 48% 42%)`/`hsl(162 40% 68%)`.
- **NETS:** 1 real `add` + стаби gated з прод. Badge 35/R16/inset4, scale1.28. N=1→статик.
- **accent global:** НЕ чіпано (білд L162/D163; StockCheck лочив 162 — 1° hue незначимо; global-зміна = рикошет). Комета має власні токени.

## 3. 🔬 МІКРОСКОП — device-знахідки Stage 1 (критично для наступної сесії)

### 3a. 🔴 BUG — колізія класу `.brand` («підкладка під брендом»)
Білд ВЖЕ має `.brand` (р.430 — картка бренду-препарату: `background:var(--cardBg);border-radius:16px;margin:8px 12px 0` + `::before/::after` glow/wash). Мій острівцевий `.brand` (р.354) **успадкував cardBg-плитку+radius+margin** → фантомна підкладка за StockCheck, якої в харнесі не було. Тільки статичні props бліднули (pseudo не активні без `.popping/.glowing`).
- **FIX:** перейменувати острівцевий `.brand`→`.sc-brand` (+ нащадки `.brand .sc-ic`→`.sc-brand .sc-ic`, `.brand .sc-wm`→`.sc-brand .sc-wm`). Тривіально.
- **OPEN Q (Konst):** підкладка сама по собі — може лишити як **навмисну** чисту brand-plate (дизайн-рішення), не колізію. Konst «можливо так краще / можливо ні». Рішення до фіксу.

### 3b. 🟡 FINDING — контроли ТОНУТЬ на склі (generalized findings §3, device-підтверджено)
Чіпи міст/область-пігулка/пошук/net-btn/••• **втратили матеріальність** — «втонули у склі». **Це НЕ порт-діра — реальна дизайн-проблема; стенд-флет-чіпи були раннім сигналом (Konst: «стенд був правий»).**
- **Корінь (точний):** figure-ground контролу = **Δтон(fill, поверхня-позаду)**. Непрозора сторінка: позаду `--bg` ≠ surface-2/3 fill → контраст є. Frost-острівець: позаду тон скла **≈ surface-2/3** → Δтон→0 → тоне. Бейдж(зелений)+активний чіп(зелений) виживають — тон далеко від скла.
- **Наслідок:** generalized findings §3 — **БУДЬ-ЯКИЙ** контроль на склі потребує власного захищеного матеріалу, каліброваного проти ОСТРІВЦЯ (не сторінки). Зниження op НЕ поможе (гірша криза ідентичності §3).
- **FIX = materiality-бенч** (значеннєве рішення, wsd 2.4 → бенч+пресети, обидві теми): **Route α** контроли плавають на склі (підсил. fill/border/A66-vs-скло) · **Route β** filter-tier = власна recess-таця · **Route γ** гібрид (бренд+бейдж на склі, filter-tier дістає backing). → потім розширити **FINDINGS §3** device-числами.
- Дійсно і після колапсу (Stage 3 B: search+filters пінняться як glass-бар) → вирішувати незалежно.

## 4. Що НЕ зроблено / відкриті (за пріоритетом)
**HIGH (наступна сесія):**
1. **Fix `.brand`→`.sc-brand`** (§3a) + вирішити OPEN Q (навмисна brand-plate y/n).
2. **Materiality-бенч** (§3b) — Route α/β/γ, пресет-ставки, обидві теми → device → розширити FINDINGS §3.

**MEDIUM:**
3. **Stage 2 — net-switcher** (NETS-реєстр): тайл + fallback, N=1 статик (switcher-код схований), стаби gated.
4. **Stage 3 — collapse-on-scroll (модель B)** + **4 port-carry-over**: #1 defense-in-depth (clamp+overscroll-behavior[вже]+clean-rest+frame-gap на device→translate-fade фолбек), #3 (чіпи — тепер відомо: це §3b, не артефакт), #4 (plate — deferred). Frame-gap трійка обов'язково.
5. **In-product device verify** → тоді Cookbook island **A-entry** (принципи §1-§6 + §4-preset) + wsd-лінки на `Lens_stagebench_manifest.md` + `canon_delta`-стиль.

**LOW:**
6. accent-162 global (deferred — 1° hue, рикошет-ризик); contrast-floor plate безрамковий concentric (edge-нети); Фармастор motion hole#1 + §11 ХВОСТИ (окремий трек).

## 5. Файли
**Outputs цієї сесії (актуальні):**
- `StockCheck_port_b15_1.html` — Stage 1 shell (база для наступного; містить відомий §3a баг — фіксити першим).
- `StockCheck_island_glass_FINDINGS.md` — §4-preset LOCKED + §4-port carry-over (§3 буде розширено §3b).
- `StockCheck_brand_valuesLOCK.md` — §6 хедер ✅.
- `StockCheck_NETS_register.md`.
- `Lens_stagebench_manifest.md` — bench-канон standalone.
**Проект:** `StockCheck_island_harness_v2.html` (stage-bench еталон), `Фармастор_замовлення_v2_port_b14_2.html` (порт-джерело b14_2).

## 6. Уроки цієї сесії (generalizable)
- **Клас-колізія при порті:** переносячи компонент у чужий білд, грепати імена НОВИХ класів проти бази ПЕРЕД видачею (`.brand` вже існував → cardBg-bleed). Дешевий grep рятує device-цикл. *(→ кандидат у wsd pre-patch / Cookbook.)*
- **Liquid Glass identity crisis = ВСІ контроли, не лише бейдж:** будь-який елемент на напівпрозорому склі тоне, якщо Δтон(fill, скло)→0. Материал контролів калібрувати проти ОСТРІВЦЯ, не сторінки. *(→ FINDINGS §3 generalized.)*
- **Стенд-сигнал ≠ артефакт:** «флет-чіпи» на харнесі виглядали як не-портовані токени, а насправді передбачили реальну on-glass-проблему. Дефект на достовірному стенді трактувати як сигнал, поки не спростовано.

---

## 📋 PASTE-READY STARTER (наступний чат)

```
Привіт! StockCheck — острівець-порт, Stage 1 доставлено, продовжуємо фіксами.
База: StockCheck_port_b15_1.html. Самері: StockCheck_session_summary_islandPort_Stage1.md.

Read-економія:
1. Work_Standard.md — Кластер 1 (протокол+маркер 1.2) + 2.4 (bench-дисципліна)
2. Lens_stagebench_manifest.md — НАШ канон стендів (standalone; wsd лінкує сюди)
3. Lens_iOS_cookbook.md — A45 + A55/A56 (glass) + A66 (елевація per-theme)
4. StockCheck_island_glass_FINDINGS.md — glass/island канон (§4-preset LOCKED; §3 розширити §3b)
5. StockCheck_brand_valuesLOCK.md — залочений бренд
6. StockCheck_NETS_register.md — мережевий шар
7. StockCheck_port_b15_1.html — Stage 1 shell (база)
8. StockCheck_session_summary_islandPort_Stage1.md — це самері

СТАН: Stage 1 (HTML/CSS shell) на device. Мікроскоп зловив 2 корені (самері §3):
 • §3a 🔴 колізія .brand → фантомна підкладка під брендом (fix: →.sc-brand). OPEN Q: навмисна brand-plate y/n?
 • §3b 🟡 контроли ТОНУТЬ на склі (generalized findings §3) — реальна проблема, стенд був правий.

ЗАДАЧА (за пріоритетом):
1. Fix .brand→.sc-brand + рішення OPEN Q.
2. Materiality-бенч (Route α float / β filter-tray / γ hybrid, пресет-ставки, обидві теми) → device → FINDINGS §3.
Далі: Stage 2 (net-switcher) → Stage 3 (collapse B + 4 carry-over, frame-gap на device) → device verify → Cookbook island A-entry.

Маркер навантаження — у КІНЦІ КОЖНОЇ відповіді (wsd 1.2) + дубль в ask_user_input_v0.
Working-копії у /mnt/user-data/outputs по ходу.
```
