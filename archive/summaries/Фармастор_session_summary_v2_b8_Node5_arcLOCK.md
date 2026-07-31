# Фармастор v2 — Node 5 TopArea BUILD (b8) + arc-fill motion LOCK + dots-H іконка
**Сесія:** 15.07.2026 · порт у продукт + motion-harness lock + icon-compare. Усе device✓ (XS+15Pro, обидві теми).

---

## Що зроблено

### 1. Node 5 · TopArea — ПОРТ у продукт `b8` (device✓)
Портовано з `Farmastor_toparea_harness_v4.html` (§5.3 LOCKED) у реальний Home (`b7_4` → **b8**):
- **Композиція:** `[breadcrumb Область ▾ · лічильник] → [chip-band міста +«Всі»] → [пошук-well] → список §5.2`.
- **Пін:** хедер + TopArea обгорнуто в `.home-sticky` (пінимо разом, видимі при скролі, БЕЗ collapse — collapse свідомо зняли). `#s-home .home-sticky .hdr{position:static}` (fill-хедер не чіпано).
- **Лічильник** (Konst-рішення: корисний, sanity «чи всі підвантажились»): **контекстний на breadcrumb справа** (`N апт.`) — нуль додаткової вертикалі, реюз мертвої зони рядка. «Всі»→по області, місто→у місті, пошук→збіги. Краще за статичне «(N)».
- **Band-swap місто⇄область:** тап `breadcrumb ▾` → `renderBand()` перемикає вміст `#cityrow` (crossfade `bandin .18s`, каретка ▾→▲, БЕЗ vert-push). Вибір області → `renderTop()`+`renderHome()`, scroll=0, picking='city'.
- **Вибір міста — scroll-preserve:** in-place `.on` (НЕ rebuild стрічки) + `renderHome()`. Scroll стрічки зберігається.
- **Пошук:** well (§6.3/A45), inline SVG-іконка (не емодзі); haystack = `displayAddr + місто + Proxima` у межах область+місто; S.q зберігається при зміні області (як harness).
- **Картка:** city-рядок ховається коли місто обране (`(S.city?'':...)`). Empty-state при порожньому фільтрі.
- **Прес чіпів — BAKED (не важелі, прод):** місто `scale .90/80ms` · область `.88/110ms` (pointer-driven `.is-pressed`, глобальний listener `closest('.pressable')||closest('.chip')`).
- **Матеріал чіпів A45 per-тема** (світла gradient+shadow / темна tone-lift+inset) + **auto-dark паритет A69** для `.bc/.chip/.chip.on/.srch`.
- **Persist області:** `farmstore_area` localStorage `{a}`, B57 name-guard (область ∈ AREAS).
- Підзаголовок хедера → «Мої аптеки»; `.hh` прибрано (+ орфан-CSS знято).
- `homeModel()` +поле `area`; `renderHome()` фільтрує `topMatch` + empty + пише лічильник у `#bcCount`.
- **Гейти:** node --check (обидва script) ✓ · tag-balance div55/55 ✓ · grep анкерів ✓ · absent≠0 (fill недоторканий, `onInput`: `v===''→delete` / `else→vals[k]=Number`) ✓. Логіка верифікована на реальних PH: 3 області (Дніпроп.47/Полтав.10/Кіровогр.6=63), пошук вулиця/Proxima працює.

### 2. arc-fill motion — **LOCK v1** (harness `Farmastor_arc_anim_harness_v1.html`, device✓)
§5.2 deferred «анімація дуги» → залочено:
- **`sweep · count-up ON · gauge-tick OFF · pulse-on-full ON · dur 1600 · CW · effDur 1600 (slow×1)`**.
- rationale Konst: 1600 = баланс плавність-швидкість; це expressive-момент «дивись як заповнюється» (off-ladder, як card-select 950 — A57 дозволяє).
- Констрейнти §5.2: тільки `stroke-dashoffset` (A70, без шимеру) · грає ЛИШЕ on-state-change, НЕ всі кільця на mount.
- Відкинуто: B2 overshoot (нечесно «зайшло за N і вернулось»), B3 depth («loading»).

### 3. Іконка меню = **dots-H SVG** (compare `Farmastor_menuicon_compare_v1.html`, device✓)
- Обрано dots-H над burger. Конвенція: `⋯`=overflow/більше-дій → рівно вміст шіта (Тема/Про/Експорт/Очистити); `burger`=обіцяє навігацію між розділами (яких нема) → mismatch. Проблема старого була не «три крапки», а текст-гліф (тонкий/нерівний) → inline-SVG.
- Вшито у 2 кнопки (home+fill хедери). Прес уже був (A67 `.pressable` scale .88). `APP_BUILD v2.2.1-node5.b8`.

---

## Канонічні параметри (нові/змінені цієї сесії)
- **arc-fill LOCK v1:** sweep · count-up ON · gauge-tick OFF · pulse-on-full ON · dur 1600ms · CW · decel-ease (`1-(1-t)³`). → у §5.2/§6.4 при канонізації.
- **Прес чіпів TopArea (BAKED):** місто .90/80ms · область .88/110ms (§5.3, вже локнуто).
- **Лічильник Home:** контекстний `filtered().length + ' апт.'` на breadcrumb-рядку справа.
- **dots-H** menu-icon (inline SVG, 19px).

---

## Що НЕ зроблено / відкриті задачі

### HIGH
- **arc-fill ПОРТ у b8** (завершення A). Motion залочено в harness — треба вбудувати в реальні home-card кільця. **Порт-питання:**
  1. Реальні переходи = **old→new** (напр. 45→60 при доповненні), не завжди 0→target. Механізм той самий (dashoffset old→new, pulse лише на 100). **Малий δ (+1) теж 1600ms, чи масштабувати dur під дистанцію?** — вирішити при порті.
  2. Тригер: **лише щойно-змінене кільце on-state-change**, НЕ всі на mount (§5.2).

### MED
- **D · Node 8 звірка:** copyValues §4 (📋→M{X}·Proxima, transferred, toast — вже є, р.832) + чи знесений xlsx-стек (−425 КБ). Схоже вже знесений у rebuild (файл ~1000 рядків, бібліотеки нема) — grep-підтвердити.
- **§5.1 «Динаміка» (порівняння візитів) — РОЗБЛОКОВАНО.** НЕ чекати польових даних (урок нижче): будувати з **мок-фікстурою** `visits[]` (wsd 3.6 — реальні SKU-kode+аптека, dev-прапор, той самий контракт §1). Крафтиш edge-кейси (absent-в-одному→«—», явний 0, все+/все−/mixed, same-day overwrite). Вхід «Динаміка ›» вже gated visits≥2.

### LOW
- Повний display-resolver с./смт (LABELING §9) — стоп-геп ловить лише «м.»; дедуп «м.Самар»↔city, ТЦ/прим-хвіст.
- All-done reward 83/83 (§9, зчеплено з pulse-on-full).

---

## Канон-борг (governance, наступна канон-сесія)
- **§9 Node 5 `▶` → `✅`** (BUILD device✓ b8).
- **Cookbook A67 розширення:** pointer-driven чіп-прес (`.is-pressed`, iOS `:active` ненадійний у PWA) — device✓ .90/80 / .88/110. (§5.3 вже позначив «Cookbook-кандидат, розшир. A67».)
- **arc-fill → A57 expressive off-ladder** (1600ms, як card-select 950) + §5.2/§6.4 LOCK-значення.
- **band-swap crossfade** (місто⇄область same-row, БЕЗ vert-push) — реюзабельний патерн-кандидат.
- Уточнення wsd 1.5/12.9: **mock-first legitimate для data-driven екранів** (device-арбітр судить перцептивне на мок-фікстурі; реальні дані = лише польова валідація корисності, не гейт).

---

## Файли в проекті
**Поточний продукт:**
- `Фармастор_замовлення_v2_port_b8.html` — **b8**: Node 5 TopArea + dots-H, device✓. `APP_BUILD v2.2.1-node5.b8`.

**Істина/scratch (не batch):**
- `Farmastor_arc_anim_harness_v1.html` — motion-істина arc-fill (device✓).
- `Farmastor_menuicon_compare_v1.html` — icon-compare (dots-H обрано).
- `Farmastor_toparea_harness_v4.html` — TopArea істина (§5.3).
- `Фармастор_v2_MASTER_LOCK.md` — §5.2/§5.3/§6/§1/§3/§9 (єдине джерело правди токенів/IA/стану).

**Legacy:** `Фармастор_замовлення_v2_port_b7_4.html` (база порту, до Node 5).

---

## Уроки цієї сесії
- **Mock-first для data-driven екранів (уточнення 1.5/12.9).** Перестрахувався «чекати реальних даних для §5.1» — Konst корректно оспорив: device-арбітр судить **перцептивне/візуальне**, а це чудово тестується на **мок-фікстурі** (ба більше — крафтиш edge-кейси, яких поле тижнями не дасть). Реальні дані ≠ гейт збірки; це лише фінальне польове судження корисності.
- **Контекстний лічильник на «мертвому» боці рядка** = корисна інфа за нуль вертикалі (breadcrumb-рядок мав порожню праву зону). Краще за окремий `.hh (N)` рядок, що з'їдав вертикаль і конкурував.
- **Іконка меню — читати обіцянку патерна, не лише «гарність».** `⋯`=overflow (чесно до вмісту), `burger`=навігація-drawer (обіцяє розділи, яких нема). Реальна проблема старого «⋯» була текст-гліф (тонкий) → inline-SVG. Юзер-модель («репи читають ☰ як меню») — валідний контр-аргумент, але семантичний mismatch переважив.
- **Пін ≠ collapse.** «Sticky-collapse» (стискання) зняли; «пін» (видимий при скролі) — інше й потрібне для picker+пошук над довгим списком.

---

## Перехід у новий чат — стартове повідомлення

```
Продовжуємо Фармастор v2 — ПОРТ arc-fill анімації в b8 (Node 5+7 done, motion LOCKED).

Прочитай ПЕРЕД кодом (wsd 1.1):
1. /mnt/project/Work_Standard.md (wsd) — протокол
2. /mnt/project/Lens_iOS_cookbook.md — A45/A57(motion+expressive off-ladder)/A67(press)/A69/A70(dashoffset не box-shadow)
3. /mnt/project/Фармастор_v2_MASTER_LOCK.md — §5.2 (Home-картка, дуга-deferred) + §6.4 (значення) + §1 (visits[]/стан) + §5.3 (TopArea) + §9 (черга)
4. Самері: Фармастор_session_summary_v2_b8_Node5_arcLOCK.md — ПОВНИЙ стан
5. Продукт (база порту): Фармастор_замовлення_v2_port_b8.html — Node 5 TopArea + dots-H, device✓
6. Motion-істина: Farmastor_arc_anim_harness_v1.html — arc-fill device✓

СТАН: Node 5 TopArea + Node 7 Home-картки у b8 device✓. arc-fill motion ЗАЛОЧЕНО (harness v1):
sweep · count-up ON · gauge-tick OFF · pulse-on-full ON · dur 1600 · CW · effDur 1600 (slow×1).
Констрейнти §5.2: тільки stroke-dashoffset (A70) · грає ЛИШЕ on-state-change, НЕ всі кільця на mount.

ЗАВДАННЯ: порт arc-fill у реальні home-card кільця (ringSVG зараз малює статично).
ПОРТ-ПИТАННЯ (вирішити планом):
  (1) реальні переходи old→new (не завжди 0→target) — малий δ (+1) теж 1600ms чи масштабувати dur під дистанцію?
  (2) тригер = лише щойно-змінене кільце on-state-change (порівнювати prev filled vs new), НЕ всі на mount.
Спершу план (wsd 1.5), без коду до команди. Рейку не дефолтити; критичний дизайн-фідбек прямо.

Альтернативи якщо схочу перемкнутись: D — звірка Node 8 (copyValues §4 + чи знесений xlsx-стек, швидко) · §5.1 «Динаміка» (mock-first, wsd 3.6, НЕ чекати польових даних).

Маркер навантаження — ОСТАННІМ рядком КОЖНОЇ відповіді (wsd 1.2): <70% короткий · ~70-85% + [!самері] · 85%+ САМ роблю [!самері]+переїзд. Дублювати маркер у ask_user_input_v0 (поле question).
Working-копії → /mnt/user-data/outputs по ходу (wsd 1.6).
```
