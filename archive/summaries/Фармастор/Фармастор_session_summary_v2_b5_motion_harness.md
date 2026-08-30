# Фармастор v2 — сесія: FILL порт b4→b5 (auto-parity) + motion-харнес (згортання+глоу)

Хендофф-артефакт. Мова: українська, стиль прямий. Device (iPhone XS iOS18 + 15Pro iOS26) = фінальний арбітр.
Читати перед кодом (wsd 1.1): `Work_Standard.md` · `Lens_iOS_cookbook.md` (A45/A48/A59/A67/A69) · `Фармастор_v2_MASTER_LOCK.md` · **цей самері**.

**USER PREF (жорстко):** маркер навантаження чату останнім рядком КОЖНОЇ відповіді (`<70% короткий; ~70-85% + [!самері]; ~85%+ САМ роблю [!самері]+переїзд`), дублювати в `ask_user_input_v0` (поле question).

---

## ЩО ЗРОБЛЕНО ЦІЄЮ СЕСІЄЮ

### 1. FILL порт — вузли 1-5 злиті (b4 → b5)
Файл: **`Фармастор_замовлення_v2_port_b5.html`** (outputs). APP_BUILD `v2.1.1-port.b5`.
- **Дані вшиті:** 83 SKU + 63 аптеки (з `farmastor_v2_data.js`).
- **relabel (вузол 4) = LAYOUT-таблиця за kode** — портовано device✓ гарнес-DATA (`Farmastor_multibrand_harness_v1.html` 296-408) як `const LAYOUT={brand,subs:[{eb,rows:[{k,v,pk,fd}]}]}`, вирівняно до MSL. **Верифіковано python:** усі 83 kode, кожен раз; strep/durex/contex/evi = чистий zip; nuro/gavis = explicit MSL-index MAP (`nuro=[0..10,18,19,11..17]`, `gavis=[2,3,4,1,5,0,6]`), звірено по контенту. Генератор: `/home/claude/layout_gen.js`. **Принцип:** relabel редакторський+декоративний (§2/§60), не regex — тому таблиця з золота, не re-derive.
- **§3 резолвер** працює: норма = kode→MSL→колонка тіру (OTC-бренди по `oTC`, IW по `iW`). Смоук: strep-3020906 дає A/B/C/D = 8/6/4/2. Headless-рендер: 83 рядки × 6 брендів × 7 eyebrows, 0 undefined.
- Компонентний CSS з гарнеса: well 60×46 · δ-чіп кутовий (silent-ok A59) · eyebrow tick+hairline+ink · settled=tint · rpk-чіп · живі лічильники бренд+під-група.
- Поле = **input** з 3 станами §1: порожнє=ghost-placeholder / >0=val / явний 0=zeroval-tint.
- Акордеон брендів: default open, **collapse-on-complete = ЛИШЕ логіка (миттєве display→grid), БЕЗ motion** (див. нижче).
- Хедер FILL динамічний (адреса · місто · Proxima · тір-чіпи · прогрес N/83).

### 2. 🐛 AUTO-THEME PARITY — виправлено в b5 (A69)
**Баг:** мої компонентні стилі (`.fld`, лічильники, `.ebrow`, `.rpk`) + shell-ові (`.icon-btn/.tchip/.progress/.sheet/.demo-btn`) чіплялись ЛИШЕ на `[data-theme="dark"]`/`[data-theme="light"]`. На **авто-темі** (без атрибута) жоден не спрацьовував → токени темні, а конструкції ні → **гнізда невидимі**, авто виглядала «напівтемною».
**Фікс:** світле гніздо стало БАЗОВИМ (unprefixed `.fld`); кожне dark-компонентне правило (shell+моє, 11 шт.) віддзеркалено в `@media(prefers-color-scheme:dark){:root:not([data-theme="light"]) …}`. Konst device-підтвердив на явних світлій/темній ще до фіксу («все як у харнесі»); авто-фікс на ре-тесті.
**⚠️ Урок → wsd/Cookbook A69:** будь-яке `[data-theme]`-gated *компонентне* правило ОБОВ'ЯЗКОВО дублювати в auto-dark media. Base = світле; dark = `[data-theme="dark"]` + media-дзеркало.

### 3. Motion-харнес — збудований (НЕ залочений)
Файл: **`Farmastor_motion_harness_collapse_glow_v1.html`** (outputs).
- Картка Гавіскону (реальний relabel-gold, 3 під-групи, 7 рядків), старт 6/7.
- Послідовність на complete: **glow-німб** (`.brand::after` box-shadow pulse) + **pop** (scale overshoot keyframe) → lead 140ms → **collapse** (`.bwrap` grid-template-rows 1fr→0fr).
- Бенч-важелі (bake ×1): `--collapseDur/Ease`, `--popDur/Ease/Over`, `--glowDur/Spread/Op`. Slow-mo ×1/2/3 (множить лише durations; bake = base). 📋-копі, легенда ефективних значень, перемикач тем, slow-mo×bake дотримано.
- **Стартові дефолти:** collapse 520ms spring-soft `cubic-bezier(.34,1.56,.64,1)` · pop 620ms/spring-soft/overshoot 4.5% · glow 900ms/spread 22px/op .55 · lead 140ms. (З QR Lens large-card патерну — Konst тюнить/підтверджує на девайсі.)

---

## СТАН / ВІДКРИТЕ

- **Motion — чекає device-lock.** Konst тюнить харнес на XS/15Pro → копіює значення (📋) → у новому чаті **порт у b5→b6** (grid-rows collapse + glow-німб + pop у продукт, за реальним `refreshCounters` collapse-on-complete).
- **Статус-гейдж (прогрес):** на явній темній трек `#0f1714` затемний (майже зливається). Konst свідомо відклав як окремий gauge-вигляд. Auto-parity вже зробив трек авто=темна. TODO: підняти контраст треку / повноцінний статус-гейдж (харнес).
- **M-якір (node 8) — РОЗВ'ЯЗАНО з файлу:** лист «АП» у `Фармастор_замовлення_тт.xlsx`: **колонка M = «Залишок»**; 63 аптеки × 83 рядки стосом у порядку PH[]; kode-порядок у блоці = MSL master-order (copy §4 by-kode вставиться 1:1). **M-рядок вираховує додаток:** `M{2 + phIndex*83}` (102520→M2 · 119016→M85 · 121825→M168). «M168·Proxima102520» було неузгоджене — #168 вигадка-приклад, реального «№168» нема. **PENDING від Konst (при node 8):** (1) вставляєш саме в «АП» стовпчик M? (2) тримаєш «АП» у цьому порядку (не сортуєш)? Якщо тримаєш → M{X}+Proxima; якщо сортуєш → Proxima головний якір, M{X} зручність. У b5 кнопка вже реально копіює 83 by-kode + тост показує обчислений `M{X}·Proxima{px}` (node-8 preview).
- **Плаский стан** (`farmstore_v1`, `ST.phs[px][k]`) — node 6 обгорне у `visits[]` + snapshot A1 + міграція.
- **Тимчасовий Home-пікер** (native select, 63 аптеки, ✓ visited, [O·I] тіри) — node 5/7 замінить.
- **IW Excel «Кількіть MSL»** рахує IW через OTC-тір (баг формули в хмарному Excel; додаток рахує §3 правильно) — Konst перевіряє формулу окремо.

---

## ПЛАН — ПРІОРИТИЗОВАНИЙ БЕКЛОГ

**🔴 HIGH (робити першими):**
1. **Motion-порт у b6** — залочені значення харнеса → collapse+glow+pop у продукт (grid-rows у `.bbody`, `::after` німб, pop-keyframe; тригер = `refreshCounters` при done). Device-тест.
2. **Node 6 — стан v2:** `visits[]` per аптека `{date,vals,tier,transferred}`, snapshot-on-copy (A1), same-day overwrite, міграція `farmstore_v1`→`farmstore_v2`.
3. **Node 7 — Home «Мої аптеки»:** картки 3 стани, тір-профіль, агрегат-прогрес (замінити тимч. пікер разом з node 5).

**🟠 MEDIUM:**
4. **Node 5 — пошук-пікер** (§5): назва/адреса/Proxima, групування по місту (sticky), замінити native select.
5. **Node 8 — copy-контракт §4 фінал:** dual-anchor картка `M{X}·Proxima`, CSV-страховка в •••, resolve M-anchor flow (2 питання вище).
6. **Статус-гейдж** — контраст треку на темній / повноцінний вигляд (харнес).
7. **§5.1 екран порівняння** — `visits[]` δ-колір = дистанція-до-норми (НЕ напрям).

**🟢 LOW / поліш:**
8. **eyebrow sticky** з offset під хедер (зараз non-sticky в b5 — свідомо).
9. **eyebrow ink** — зараз 10 (гарнес device✓); §6.2 має --inkStr 14/15 — вирішити на девайсі.
10. Press-механіка A67 на brand-хедері (зараз tap-toggle без press-фідбеку).

---

## ПРИНЦИПИ (тримати)
plan→confirm→code (wsd 1.5) · grep-before-claim на живих файлах (12.1) · harness-first, motion лочиться на девайсі slow-mo (12.9) · compare-lock≠canon (канон лише після патч+девайс) · memory≠канон · no truncation даних · relabel=конфіг за kode · silent-ok A59 · `ask_user_input_v0` після патчу завжди «Спрацювало ✓/Є баг» · APP_BUILD++ кожен батч · working→outputs (версія в імені), source→/mnt/project (read-only).

## КЛЮЧОВІ ФАЙЛИ
- Продукт: `Фармастор_замовлення_v2_port_b5.html` (база для b6)
- Motion-харнес: `Farmastor_motion_harness_collapse_glow_v1.html`
- Візуальна правда: `Farmastor_multibrand_harness_v1.html` · Логіка/токени: `Фармастор_v2_MASTER_LOCK.md`
- Дані: `farmastor_v2_data.js` (MSL/PH) · `Фармастор_замовлення_тт.xlsx` (корпоративний, лист «АП» col M) · генератор LAYOUT: `/home/claude/layout_gen.js`
