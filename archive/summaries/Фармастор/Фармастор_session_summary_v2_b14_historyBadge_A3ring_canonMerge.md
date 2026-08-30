# Фармастор v2 — Session Summary: Badge «Історія» + A3 перенесена-ринг + MASTER canon-merge
**Дата:** 20.07.2026 · **Білди:** b13_2 → **b14** → **b14_2** (поточний) · **MASTER:** canon-merged

---

## ЩО ЗРОБЛЕНО (device✓ Konst XS+15Pro)

### 1. Home-бейдж «Історія · N» — ПОРТ (b14) ✓ device✓
- Свап старого афорданса «Динаміка ›/показники ›» → **soft-fill чип** (icon=clock · label «Історія» · N · chevron), вхід у §5.1.
- Футер **3→2-слот**: `.date` прибрано з Home (живе в §5.1 dpill — перевірено `cmpDpillHTML`).
- Wire: `N=visits.length` · disabled `N≤1` · cap 7 (`N>7→«7+»`) · **завжди видимий** (discoverability).
- **Ізоляція пресу (ключове):** у делегованому `pointerdown` бейдж-перевірка ПЕРШОЮ → `.pressing` scale .88 + `return` → **картка НЕ пресується**. Клік `.hist:not(.dis)` → `stopPropagation`→`openCmp`. Disabled → `pointer-events:none` (провал на картку).
- Значення (L/D split soft-fill): `Фармастор_history_badge_valuesLOCK.md`.

### 2. A3 · Перенесена-ринг §5.2 — ПОРТ (b14_2) ✓ device✓
- **Перенесена картка тримає ринг + fill + число** (як ready), **✓✓ у розриві дуги** (акцентом) замість %, tiny-caption «перенесено» під рингом.
- **Dim БЕЗ whole-card opacity:** прибрано `.card.tr{opacity}`; лишено `saturate + bg-mix`; текст (`.idcol/.foot`) привид на `dimOp`; **ринг живий на `arcLift .82`**.
- Джерело device✓: `Farmastor_status_filter_harness_v2.html`. Значення: §6.5 (arcLift .82 · dim L16/70/60 · D30/60/50).
- Мертві `.trmk/.trl/.trcol` прибрані.

### 3. MASTER_LOCK — CANON-MERGE (гігієна)
- §5.1 верхівка + Δ-колір(B) · §5.2 перенесена-ринг · §5.4 status-фільтр · §6.5 → флаги `BUILD pending` → **✓ CANON (device✓ в проді b13/b14_2)**.
- §5.2: додано **канон бейджа «Історія · N»**; усі згадки входу в §5.1 переназвано.
- Роздутий changelog (р.4) → чистий 396-знаковий. §9: b13/b14 = **DONE**, наступне = стенд+хвости.
- **Додано §11 ХВОСТИ** з планами дій (нижче).

### 4. Виправлені застарілі записи пам'яті
- «Про додаток» **та** «Експорт CSV» — **ОБИДВІ робочі** (`exportCSV()` р.772+1523; About-шіт активний). Старий запис «мертвий стуб» = хибний. Лишається лише **візуал About** (старий дизайн → §11.2).

---

## ФАЙЛИ (в /mnt/user-data/outputs, канонічні)
- **`Фармастор_замовлення_v2_port_b14_2.html`** — ПОТОЧНА продукт-база (badge + A3-ринг).
- **`Фармастор_v2_MASTER_LOCK.md`** — оновлене джерело істини (canon-merged).
- `Фармастор_замовлення_v2_port_b14.html` — проміжний (лише badge).

---

## ROADMAP (наступні чати, окремо)

**▶ 1. MOTION-СТЕНД (hole #1) — наступна велика задача**
Пара **зчеплених** рухів (motion завжди coupled, wsd 2.4):
- **a. Celebration-заповнення** — при поверненні з FILL на Home картка щойно-заповненої аптеки «святкує» (дуга-як-нагорода). NB: copy-wash уже є в FILL (`.brand.washing`); Home-дуга-нагорода — ні.
- **b. Reorder-спуск** — картка з'їжджає вниз у «Перенесені (N)» (FLIP-реордер).
Робити повноцінним motion-харнесом (slow-mo + frame-gap, обидві теми, слайдери з початку). Device = арбітр.

**▶ 2. ХВОСТИ §11 (polish-батч, не блокують стенд)**
- **11.1 status-фільтр чип** — при «Активні/Перенесені» чип росте вгору+вширш. Корінь: `.bc.filt .cnt` успадковує важкий FILL-`.cnt` (`min-width:42px`+padding+border). Фікс: де-пігулити (плоске tabular-число, як `.h-n`). Обидва лічильники лишити (46/1 filtered ≠ 47 total).
- **11.2 About-щит** — старий дизайн → A58-рестайл (grouped-card + `.mi`-рядки; §10.5 матеріал).
- **11.3 dark-меню «скло»** — translucency → tone-lift (A45/A66: fill `color-mix(#fff 6%,surface-3)`, без drop).

---

## READ-ЕКОНОМІЯ ДЛЯ НАСТУПНОГО ЧАТУ

**Завжди:** `Work_Standard.md` — Кластер 1 (протокол+маркер 1.2). За потреби коду — К10 (валідація) · 10.8 (scoped-grep).

**Якщо MOTION-стенд:**
1. wsd — Кластер 2 (motion-дисципліна 2.4: slow-mo/frame-gap/coupled-pair).
2. `Lens_iOS_cookbook.md` — reward/spring-ентрі (motion), A70.
3. `Фармастор_v2_MASTER_LOCK.md` — §9 (Motion reward LOCKED v2 значення) · §5.2 · §1 (snapshot-on-copy — тригер).
4. Reference-харнес: `Farmastor_motion_harness_collapse_glow_v2.html` (raw-важелі, per-theme).
5. Продукт-база: `Фармастор_замовлення_v2_port_b14_2.html`.

**Якщо ХВОСТИ (polish):**
1. wsd — Кластер 1 + К10.
2. cookbook — A45/A66 (матеріал/dark-елевація, для 11.3) · A58 (grouped-card, для 11.2) · A67.
3. MASTER — §11 (плани) · §10.5 (container material значення).
4. Продукт-база: `Фармастор_замовлення_v2_port_b14_2.html`.

---

## СТАРТЕР ДЛЯ НОВОГО ЧАТУ (paste-ready)

```
Привіт! Фармастор v2 — продовжуємо. Поточна база: Фармастор_замовлення_v2_port_b14_2.html.
MASTER (canon-merged) = джерело істини.

ЗАДАЧА: MOTION-СТЕНД (hole #1) — celebration-заповнення + reorder-спуск у «Перенесені».
Пара зчеплених рухів (motion coupled, wsd 2.4). Спершу харнес (slow-mo + frame-gap,
обидві теми, слайдери з початку), device-тюн, потім порт у продукт.

Прочитай (read-економія):
1. Work_Standard.md — Кластер 1 (протокол+маркер 1.2) · Кластер 2 (motion 2.4). Решту не читай.
2. Lens_iOS_cookbook.md — reward/spring motion-ентрі · A70. Решту не читай.
3. Фармастор_v2_MASTER_LOCK.md — §9 (Motion reward LOCKED v2 значення) · §5.2 · §1 (snapshot-on-copy).
4. Farmastor_motion_harness_collapse_glow_v2.html — reference raw-важелів (per-theme, frame-gap).
5. Фармастор_замовлення_v2_port_b14_2.html — продукт-база (порт ОНТО цього).

Маркер навантаження чату — у КІНЦІ КОЖНОЇ відповіді (wsd 1.2), + дублювати в ask_user_input_v0.
Working-копії у /mnt/user-data/outputs по ходу.

🔑 ПЕРЕД харнесом: грепни поточний reward-тригер (fireReward/refreshCounters) + де
рендериться список Home (секції Активні/Перенесені) — щоб знати точку входу реордера.
Celebration + спуск узгодити з All-done-reward (§9). Почни з плану харнеса. Код після підтвердження.

(Альтернатива, якщо не стенд: polish-хвости §11 — status-фільтр чип-fix / About A58 / dark-меню tone-lift.)
```

---
*Session-close b14_2 · canon-merged · наступне = стенд (новий чат).*
