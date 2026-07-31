> живе доки: назавжди (вічне, wsd 1.8) — значення грошового блоку Home

# StockCheck / Фармастор — Money-Home valuesLOCK

**Статус:** BENCH-LOCKED (stagebench v2, device-locked XS + 15Pro, обидві теми) — pending in-product device verify після порту.
**Джерело:** `StockCheck_money_home_stagebench_v2.html`
**Ціль порту:** `StockCheck_port_b19.html` (= той самий Фармастор, ребренд).

---

## 1. Що це
Показ **грошового розриву vs MSL** прямо на філ-екрані: скільки ₴ треба довезти (плюс) або перезатарено (мінус). Дві точки показу («дім»):
- **Родина A — бейдж-дім:** біля верхніх бейджів **OTC / IW** — сума по категорії.
- **Родина B — акордеон-дім:** у хедері кожного **бренд-акордеона** — сума по бренду. Бейджа там НЕ треба (бренд сам каже категорію).

## 2. Арифметика (реальна, по-SKU)
```
order(SKU)  = MSL_ярус − порахував        // MSL_ярус = поле A/B/C/D за ярусом точки для категорії SKU
money(SKU)  = order(SKU) × p              // p = Custom.Price (поле "p" у MSL[])
категорія₴  = Σ money(SKU) по c ∈ {OTC,IW}
бренд₴      = Σ money(SKU) по бренду
```
- Знак: **+** = недозавантаження (треба закупити) · **−** = overstock (перезатарено). Показуємо обидва (мінус, як в оригіналі Excel: N=MSL−Залишок, O=N×Price).
- Жива: перераховується при кожній зміні лічби SKU.
- Реальні орієнтири (ярус C/D, порахував=0): OTC +13 849 · IW +7 079 · Нурофен +8 275 · Стрепсілс +3 727 · Гавіскон +1 847.

## 3. Залочені візуальні значення
Спільне (обидві родини): формат **повний** («13 849 грн») · знак **семантичний +/−** · дім **пігулка** · розмір **12px** · вага **700** · валюта **грн**.

| важіль | A (бейдж) | B (акордеон) |
|---|---|---|
| gap назва↔дім | 6 | 2 |
| scope | — | **Бренд** |
| **LIGHT** tint / border(✦accent-край) / shadow | 7 / 37 / 2 | 7 / 30 / 2 |
| **DARK** tint / border(accent-край) / ridge | 12 / 37 / 14 | 12 / 28 / 8 |

Матеріал пігулки (A45 per-theme, різні набори важелів):
```css
/* LIGHT pill — border МУСИТЬ бути accent-край (A45 прав.4), інакше soft розчиняється */
.money.h-pill.pos{ background:color-mix(in srgb,var(--accent-soft) 7%,var(--card));
                   border:1px solid color-mix(in srgb,var(--accent) 37%,transparent);   /* A:37 · B:30 */
                   box-shadow:0 1px 2px rgba(20,50,42,.16); color:var(--mpos); }
.money.h-pill.neg{ background:color-mix(in srgb,var(--negsoft) 7%,var(--card));
                   border:1px solid color-mix(in srgb,var(--mneg) 37%,transparent);
                   box-shadow:0 1px 2px rgba(80,20,20,.14); color:var(--mneg); }
/* DARK pill — ridge (top hl) замість drop-shadow */
.money.h-pill.pos{ background:color-mix(in srgb,var(--accent-soft) 12%,transparent);
                   border:1px solid color-mix(in srgb,var(--accent) 37%,transparent);   /* A:37 · B:28 */
                   box-shadow:inset 0 1px 0 rgba(255,255,255,.14); color:var(--mpos); } /* rg A:14 · B:8 */
.money{ font:700 12px/1 var(--font); font-variant-numeric:tabular-nums; padding:2.5px 7px; border-radius:9px; }
```
Токени знаку: `--mpos` L `hsl(162 82% 27%)` / D `hsl(163 52% 60%)` · `--mneg` L `#c0392b` / D `#e07a6f` · `--negsoft` L `#eab8b2` / D `hsl(6 42% 22%)`.

## 4. Вирівнювання (баг, який ловили)
Дім у бренд-хедері «пливе» через різну ширину лічильника SKU (0/20 vs 0/7). **Фікс:** фіксований слот лічильника `.bhdr .bcnt{min-width:50px}` (у стенді). **Порт:** розмір слота під найширше **«NN/NN»** (~56px), щоб дім стояв стабільно і в процесі лічби.

## 5. Скоуп акордеона
Дефолт **Бренд** (одиниця згортання; згорнув → бачиш тотал бренду). Опції: Під-секція / Обидва. Сума на під-секції рендериться **лише де секцій ≥2** (напр. Гавіскон: Таблетки/Суспензія). Пласкі бренди в режимі «тільки Під-секція» лишаються без цифри — навмисно (тому Бренд = must-have).

## 6. Феасибіліті
Все in-app: `p` (ціна), `A/B/C/D` (MSL ярусу), `c` (категорія) вже у `MSL[]`. Нічого доганяти з Excel.

## 7. Хвости / наперед
- Контур (outline) поки на фіксованому A45-коректному матеріалі — якщо колись оберемо контур, дати йому per-theme важелі.
- Stagebench-канон: додати **стейдж-зум +/−** та чіткий **hide-panel** (обов'язкові в стенді) — у `Lens_stagebench_manifest`.
