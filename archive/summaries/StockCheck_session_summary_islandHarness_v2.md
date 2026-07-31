# StockCheck · session summary — island-harness v2

## 0. Контекст
StockCheck = мульти-мережева еволюція Фармастора. Цю сесію: залочили бренд-значення (зі скріншотів, бо copy-bet у head-bench v7 був підв'язаний до старого набору важелів), зафіксували glass/island findings, побудували materiality-harness (v1→v2). Konst зараз device-тестує острівець; детальні коментарі — у наступному чаті.

## 1. Зроблено цю сесію
1. **`StockCheck_brand_valuesLOCK.md`** — фінальні бренд-піки, зчитані зі скріншотів Konst і **звірені 1:1 з `S{}`/слайдерами** head-bench. Статус: `BENCH-LOCKED`, pending in-product device verify. *(вже в проекті)*
2. **`StockCheck_island_glass_FINDINGS.md`** — робочий канон «як працювати зі склом+острівцем». §1–§6 принципи = canon-ready; значення пресетів = pending device. *(вже в проекті)*
3. **`StockCheck_island_harness_v2.html`** — materiality stage-bench. *(поточний; v1 = fallback)*

## 2. 🔑 Ключові рішення / виправлення
- **Net-модель ВИПРАВЛЕНО:** Фармастор = «Аптека доброго дня» (АДД) **+ 1 соц.аптека під ОДНИМ юрназвою** → це **ОДНА мережа, ОДНА іконка** («доброго дня»). НЕ дві. Мульти-мережа = **інші** мережі (АНЦ, Подорожник…) з'являться пізніше.
- **Scroll-дисонанс Konst-а = ПІДТВЕРДЖЕНО правильно.** Плаваюче скло + жорстко-фіксований сусідній tier = анти-патерн C (мертве скло вгорі + «два шматки хрому»). Два чистих виходи: **A·unlock** (search+фільтри скролляться, пінниться лише острівець) / **B·collapse** (бренд згортається на скрол, search+фільтри = піннутий glass-бар). **Ставка Claude: B.** Фінал — за device-піком Konst.
- **Скло: ставка ТАК** (P2 Liquid — основна ставка), але це важіль-діапазон, не хардкод.
- **Бейдж НЕ тоне** (findings §3): тайл = власний якір, НЕ успадковує прозорість острівця. Незалежні важелі: badge-op / badge-lift / plate(contrast-floor). Дві кольор-осі: island-tint ⟂ badge-fill.

## 3. Залочені бренд-значення (valuesLOCK, стисло)
- Бренд: icon **comet ✦**, wordmark **SC-caps**, case **StockCheck** (camel), wSize **24**, weight **800**, tracking **−1.2px** (слайдер −12), iconSize **34**, gap **4**.
- Комета: gapC **335** · gapW **62** · tilt **0** · tail **taper** · cometW **6.2** · checkW **4.4** · csL **72** / csD **48**.
- Accent A45 (hue **162** — поза зоною колізії 176–182): світла S82/L28 · темна S50/L46. Токени: light `hsl(162 82% 28%)`, dark `hsl(162 50% 46%)`.
- Бейдж-тайл: **35 / R16 / inset4** · scale **1.28** · моно-фолбек off (авто-запобіжник).
- Кнопки: **44**.
- Хедер-тип: **DEFERRED** (острівець обрано в бенчі, але порт чекає на materiality — саме це зараз у harness).

## 4. Harness v2 — що всередині
- **Scroll-тумблер A·unlock ⇄ B·collapse** + `Скло УВІМК`(інакше суцільний P0).
- **Пресети:** P0 Attached solid (контроль) · P1 Frost · P2 Liquid (ставка) · P3 Tinted(accent-162).
- **Важелі острівця (per-theme):** blur(≤12) · sat · bg-opacity · tint(нейтр/accent) · rim · lift · inset · radius.
- **Бейдж-захист:** badge-op · badge-lift · plate(contrast-floor) · net-cycle (1 real Фармастор + edge-стендіни: коротка/довга/світла/темна/teal-колізія).
- **Текст:** val-L / mut-L.
- **Stage-bench:** XS+15Pro реальні пропорції, per-frame device+theme, zoom, **copy-bet на ВЕСЬ набір**, **⚙ Сховати/Панель** (collapse панелі вправо → вертикальний скрол; канон wsd 2.4(d)), компактний хедер.
- Валідація: node --check ✓, теги збалансовані.

## 5. Roadmap (наступні кроки)
1. **Konst device-тестує harness** → copy-bet переможця (пресет + точні значення per-theme) + вибір **A vs B** + детальні коментарі по важелях.
2. Claude локає значення у **FINDINGS §4-preset** + оновлює valuesLOCK (хедер-секцію).
3. **Канонізувати stage-bench патерн** (XS/15Pro пропорції + per-frame device/theme + zoom + copy-bet + collapse-тогл 2.4(d)) як окремий тип compare-тулінгу у wsd/cookbook. + island/glass FINDINGS → Cookbook нова A-entry.
4. **NETS-реєстр:** 1 real anchor (Фармастор/доброг.дня) + принципові edge-case стендіни (мок-фікстури > реальні дані — канон). Реальний список мереж по SKU-зрізу від стейкхолдерів ще НЕ надано → не блокуємось, будуємо на синтетиці.
5. **Порт у білд** (`Фармастор_замовлення_v2_port_b14_2.html`): ребренд хедера (StockCheck-бренд + net-switcher) з обраною scroll-моделлю + island-матеріалом → in-product device verify → тоді канон.

## 6. Booked (не забути, окремий трек)
- Фармастор motion hole#1 (celebration-fill + reorder-спуск у «Перенесені», coupled motion, harness→device→порт).
- Фармастор v2 §11 ХВОСТИ: chip-sizing bug (`.cnt`), About A58-restyle, dark-menu tone-lift.

## 7. Файли (outputs цієї сесії)
- `StockCheck_brand_valuesLOCK.md` *(в проекті)*
- `StockCheck_island_glass_FINDINGS.md` *(в проекті)*
- `StockCheck_island_harness_v2.html` *(поточний)* · `_v1.html` *(fallback)*

---

## 📋 PASTE-READY STARTER (наступний чат)

```
Привіт! StockCheck — острівець-матеріальність, продовжуємо.
База: StockCheck_island_harness_v2.html. Самері: StockCheck_session_summary_islandHarness_v2.md.

Read-економія:
1. Work_Standard.md — Кластер 1 (протокол+маркер 1.2) + bench-дисципліна 2.4 (a/d — collapse-панель)
2. Lens_iOS_cookbook.md — A45 + A55/A56 (glass-токени) + A66 (елевація per-theme)
3. StockCheck_island_glass_FINDINGS.md — glass/island робочий канон
4. StockCheck_brand_valuesLOCK.md — залочений бренд
5. StockCheck_island_harness_v2.html — harness (scroll A/B × P0–P3)
6. StockCheck_session_summary_islandHarness_v2.md — це самері

СТАН: harness v2 доставлено. Я device-тестую острівець.
Даю: copy-bet переможця (пресет + значення per-theme) + вибір scroll A·unlock / B·collapse + коментарі по важелях.

ЗАДАЧА: залочити острівець-значення у FINDINGS §4-preset + оновити хедер-секцію valuesLOCK →
далі NETS-реєстр (Фармастор=доброг.дня як 1 real + edge-стендіни) → порт у Фармастор_замовлення_v2_port_b14_2.html.

🔑 Не забути: канонізувати stage-bench патерн (+collapse-тогл 2.4(d)) у wsd/cookbook; island FINDINGS → нова A-entry.

Маркер навантаження — у КІНЦІ КОЖНОЇ відповіді (wsd 1.2), + дублювати в ask_user_input_v0.
Working-копії у /mnt/user-data/outputs по ходу.
```
