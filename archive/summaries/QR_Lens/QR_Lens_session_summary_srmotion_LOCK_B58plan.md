# QR Lens — Session Summary: SR-motion LOCK → B58 port plan

**Дата:** 09.07.2026 · **Арка:** A58 (Phase 4) · **Статус:** harness v4 device-locked, готово до порту в базу.

---

## 1. Що зроблено цієї сесії

**Проблема (device✓ Konst):** E3a ring на E1-каскаді НЕ було видно — 1-shot пульс проходив на ~260ms, поки рядки ще їхали (каскад до ~1100ms). На статичній E2-плиті ринг видно. Треба секвенсувати: announce ПІСЛЯ каскаду.

**Рішення (b+d):** пульс-скейл → **settle-glow**, тригер `transitionend('transform')` саме `.sel`-рядка (self-sync зі slow-mo/ease) + safety-fallback. Glow бʼє коли обраний аватар приземлився, не посеред руху. Механіка злягла як **glow + whisper-pop гібрид**.

**Артефакт:** `QR_Lens_srmotion_harness_v4.html` (гейти: node --check ✓ · jsdom DOM-driven матриця 36 комбо ✓ · прямий виклик playSettleGlow/hexRgb ✓ 0 err).

## 2. ЗАЛОЧЕНІ значення (device✓) — повна версія у `QR_Lens_srmotion_valuesLOCK.md`

**E1 каскад:** `off140 · step90 · dur540 · dist26 · ease=spring cubic-bezier(.34,1.56,.64,1)`
**E3a settle-glow:** `glowDur760 · glowSize8 · glowInt45 · glowScale112`
- тригер: `transitionend('transform')` .sel-рядка + safety `setTimeout(off+selIdx*step+dur+80)`
- матеріал: base accent-ring НЕ чіпати; outer-glow additive (bloom→gone) + scale 1.12→1.0 на glowDur; `reduced-motion`→skip
**Вибір: A** (device✓ «A відчувається») — `aGrow90 · aRingDur260 · aSettle420` (settle→close A18.1)
**Спільне:** `openDur240 · rowSc92 · downMs70`
**frame-gap:** non-blocking (glowSize8 малий blur); підтвердити на реальному B58-білді, не блокує.

## 3. МІСІЯ наступного чату: B58-порт у базу

База: `QR_Lens_preview_batch57_1.html` (batch57/rev1/phase4) → ціль **batch58/rev1**.

**План (grep ПЕРЕД claim — 12.1):**
1. Grep у batch57_1: `selSR|staggerRows|sr-opt|sr-av|closeSheet|APP_BUILD` — зʼясувати ПОТОЧНИЙ стан SR-open анімації (що вже є, чого нема).
2. Портувати E1-каскад: staggerRows params → `{step:90,off:140,dur:540,dist:26,ease:spring}`.
3. Портувати settle-glow: функція playSettleGlow (base-ring preserved + outer-glow bloom→gone + scale112) + прив'язка через `transitionend('transform')` .sel-рядка + safety-fallback. hexRgb-хелпер для theme-correct accent (світла 42,140,132 / темна 69,161,148).
4. Вибір A: settle-then-close 420ms (показати ring/grow ПЕРЕД closeSheet).
5. Прибрати старий announce-механізм якщо є в базі (фіксований-offset пульс).
6. APP_BUILD → batch58/rev1/phase4/09.07.2026 (10.6).
7. Гейти: node --check + tag-balance + jsdom-матриця + targeted grep усіх якорів. Working-копія в outputs з версією у назві (1.6).
8. HTML-only (Drive Lens? — ні, це QR Lens, має Excel-pipeline: після patch перевірити template-drift, але SR-selector — UI-only, VBA не чіпає. Підтвердити.).

## 4. Читати на старті наступного чату (wsd 1.1/2.5)
1. `Work_Standard.md` (wsd v2.24) — 1.5 plan→confirm→код · 12.1 grep-before-claim · 10.6 APP_BUILD · 6.x HTML+VBA sync
2. `Lens_iOS_cookbook.md` — A18/A18.1 sheet+settle-close · A45 elevation · A54 spring/persistent-DOM · A69 auto-dark · A71 row-stagger/reduceOn
3. `QR_Lens_srmotion_valuesLOCK.md` — залочені значення (канон цієї роботи)
4. `QR_Lens_session_summary_srmotion_LOCK_B58plan.md` — цей файл
5. Base: `QR_Lens_preview_batch57_1.html`

## 5. Канон-борг (НЕ зараз — на канон-сесії після A58-арки; Konst: лишити висіти)
B52→B57 un-canonized + **нові precept-и:**
- **ring-after-cascade** — announce-glow привʼязувати до `transitionend` .sel-рядка, НЕ фіксований offset (1-shot тоне в каскаді)
- **glow+whisper-pop** — коли announce секвенсовано ПІСЛЯ руху, малий scale не шум а пунктуація
- E1 **spring/dist26** як дефолт SR-selector каскаду
- Cookbook A71-ext: settle-glow announce-патерн (base-ring preserved, additive outer-glow)
- harness-під-субʼєкт; v6=орієнтир-не-шаблон; T2-патерн (з попередніх сесій)
- A54-хвіст у TODO#3 — лишити висіти до канон-сесії

---

## 6. PASTE-READY STARTER (копіювати в новий чат)

```
Привіт! QR Lens. Продовжуємо — B58-порт залочених SR-motion напрацювань у базу.

Читай через view ПЕРЕД кодом:
1. Work_Standard.md (wsd v2.24) — 1.5 plan→confirm→код · 12.1 grep-before-claim · 10.6 APP_BUILD · 6.x HTML+VBA sync
2. Lens_iOS_cookbook.md — A18/A18.1 sheet+settle-close · A45 elevation · A54 spring/persistent-DOM · A69 auto-dark · A71 row-stagger/reduceOn
3. QR_Lens_srmotion_valuesLOCK.md — ЗАЛОЧЕНІ значення (канон)
4. QR_Lens_session_summary_srmotion_LOCK_B58plan.md — план порту
5. wsd_TODO_running.md

База (device✓): QR_Lens_preview_batch57_1.html (batch57/rev1/phase4) → ціль batch58/rev1.

ЗАВДАННЯ: портувати в базу залочені значення —
 • E1-каскад: staggerRows {step:90, off:140, dur:540, dist:26, ease:spring cubic-bezier(.34,1.56,.64,1)}
 • E3a settle-glow: glowDur760/glowSize8/glowInt45/glowScale112; тригер = transitionend('transform') .sel-рядка + safety-fallback setTimeout(off+selIdx*step+dur+80); base accent-ring НЕ чіпати, outer-glow additive bloom→gone + scale 1.12→1.0; hexRgb theme-correct accent; reduced-motion→skip
 • Вибір A: settle-then-close 420ms (ring/grow ПЕРЕД closeSheet)
 • Спільне: openDur240, press 92/70
 • APP_BUILD → batch58/rev1/phase4/[дата]

Порядок: grep batch57_1 ПЕРЕД claim (12.1) — зʼясувати поточний SR-open стан; Plan→confirm→код (1.5); гейти node --check+tag-balance+jsdom+grep; working-копія в outputs з версією (1.6). Після patch — перевірити VBA template-drift (SR — UI-only, але підтвердити). Маркер навантаження — останнім рядком, дубльований у ask_user_input_v0.

frame-gap glow — non-blocking, підтвердити на реальному білді.
Канон B52→B57 + нові precept-и — НЕ зараз, на канон-сесії після A58-арки.
```
