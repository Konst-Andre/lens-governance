# Фармастор v2 — Session Summary · b13 (Динаміка core + §5.4 status-фільтр)

**Дата:** 19.07.2026 · **Білд:** `v2.5.0 · dynamika.b13`
**Файл:** `Фармастор_замовлення_v2_port_b13.html` (база наступного = ЦЕЙ)
**Попередня база:** `..._port_b12_3.html`

---

## ЗРОБЛЕНО в b13 (в продукті, ЩЕ НЕ device-tested)

### Ядро екрана Динаміки (Крок0+1→3) — `#s-cmp`
- **Новий екран `s-cmp`** (3-й: s-home/s-fill/s-cmp), у `.app` scroll-контейнері.
- **Скоуп-рішення (R3):** УВЕСЬ CSS Динаміки під `#s-cmp` — уникає колізії з FILL (`.row/.dyn/.dchip/.well/.dbox/.brand/.ebrow`). Токени Динаміки на `#s-cmp` (не `:root`), бо `--chRad` зайнятий FILL δ-chip. Dark через per-theme токени з dual-guard (`[data-theme="dark"] #s-cmp` + `@media auto-dark` — §7/A69, бо продукт лишає data-theme відсутнім в auto).
- **Крок1 — colhead-ДІМ G:** `.gdome` (глобальний, sticky). Локи baked: `Lbg20/Lbord70/Ldrop7 · Dbg12/DbordC10/DridgeC14/Ddip28 · chH25/chRad6`. Per-brand colhead НЕ емітиться (тільки глобальний dome). Акордеон-каркас (`.brand/.bhdr/.bwrap/.bbody/.ebrow/.rows`) + ebrow-дільник (border-top:2px, НЕ sticky).
- **R2 sticky-офсет:** gdome `top:var(--cmpHdrH,52px)`; `--cmpHdrH` виміряється в `openCmp` через `#cmp-hdr` offsetHeight (rAF після show). ⚠️ **DEVICE-VERIFY:** чи pin точно під хедером.
- **Крок2 — sumcard (§5.1 композиція A):** `.sumcard` = 3 зони. Зона1 `.sum-top.mode-a`: `.st-line`(status-голова + dpill в рядок) → `.tally`(3 плитки raised §6.5, лейбли «до норми/від норми/без змін», caption «відносно MSL»). Зона2 `.sum-div`. Зона3 `.sum-fil` → `.sfilter` (SKU-фільтр Усі/Проблемні/Змінилось, A54-thumb через `cmpPlaceThumb`).
- **Крок3 — рядки + Δ-колір Модель B (A8):** `.row`(info + `.cmp-dyn`[well-was·well-now·dbox-Δ]). `cmpLevel(f,t,nF,nT)` = МОДЕЛЬ B, **critK=0**: na(absent) · crit(t=0) · stable(sF=0&sT=0) · improve(sT<sF) · degrade(sT>sF) · stuck(sT=sF>0). `cmpLvClass`: improve→lv-ok · degrade/stuck→lv-low · crit→lv-crit · stable/na→lv-none. `cmpTraj` (tally-бакет = ТРАЄКТОРІЯ): improve→b · degrade/crit→w · stable/stuck→s · na→none. dbox T2-гніздо (light глянець / dark A66.1 tone-lift). **absent-чесність:** `cmpFmt` null→«—».
- **Δ-колір ЮНІТ-ТЕСТ пройдено** (MSL=5, vs локнутий харнес): 7→4 degrade/w · 9→2 degrade/w · 6→5 stable/s · 4→7 improve/b · 4→4 stuck(lv-low,traj-s) · 5→0 crit · null→x na. Розчеплення колір↔стан підтверджено.
- **Адаптер R5:** `cmpBuild(px)` — `cmpPickVisits` (дефолт = останні 2 transferred, fallback останні 2 з даними) → model (cat→brand→sub→items), per-visit tier (cross-norm nF≠nT показує «MSL X→Y»).
- **Вхід:** Home-картка `Динаміка ›` (visits≥2) → клас `cmp-go`+data-px → перехоплення в homeList-click (`e.target.closest('.cmp-go')` → `openCmp`, stopPropagation) → відкриває s-cmp.

### §5.4 status-фільтр (Крок4) — HOME, аптека-рівень
- Розширення наявних `renderTop/bindTop/renderBand` (band-swap crossfade вже device✓).
- `S.mode` ('all'|'active'|'transferred'). Комбо-чіп `.bc.filt` (гліф `.g` all/active/transferred + лейбл + `.cnt` + каретка) між area-bc і `.bc-count`. area-bc → `.area-bc .lbl` (ellipsis overflow) + `pressable`.
- `picking==='filter'` → `filterChips()` (band з `.fg` гліфами + `.cn` лічильниками, data-filt).
- `bindTop`: filt-bc toggle filter/city + `renderCrumbState` (каретка) + `renderBand`; band data-filt → set mode.
- `counts()` = ОБЛАСТЬ-total (не city/q): a=non-transferred, t=transferred, all. filt-chip показує mode-лічильник; **bc-count справа = counts().all (область-total, §5.4-lock — ЗМІНА vs b12_3 де було M.length)**.
- `renderHome`: mode-фільтр list (active→act · transferred→tr · all→act+секція «Перенесені»). Empty-msg mode-aware. arc-fill loop на M з null-guard (безпечно з mode-фільтром).
- press-біндер продукту (р.~1481): `pointerdown` → `.pressable||.chip` gets `.is-pressed` (авто). `.bc.is-pressed{scale(.93)}` додано.

### Валідація (wsd 10.2) — ПРОЙДЕНО
node --check OK · div 119/119 · section 3/3 · R3 скоуп чистий (усі Динаміка-селектори #s-cmp, FILL цілий) · усі нові функції ×1 (без дублів) · absent-чесність · Модель B==харнес.

---

## PENDING (наступний чат)

### 1. Бейдж «Історія» на картці (Konst-мокап 19.07 · GPT) — ЗАМІНА текстового афорданса
**Рішення прийняте:** перейменувати вхід «Динаміка» → **«Історія»** на картці (дворівнева IA: бейдж=«Історія · N» вхід/колекція, екран=порівняння/динаміка). Заголовок екрана лишається адресою.
**Концепт:** outline-пігулка в службовому рядку (де M2243 · Proxima), у порожньому правому кутку. Icon + «Історія · N» + chevron. Press ЛИШЕ на бейдж (верх картки статичний, A67). Disabled при N≤1 (треба ≥2 візити).
**Claude-бети для аудиту (design-only, фінал=девайс):**
- Фаворит = **A-family** (outline · годинник · «Історія · N» · chevron, НЕЙТРАЛЬНИЙ монохром).
- ПРОТИ кольор-кодингу за к-стю даних (мокап G оранж/H green-filled): кільце вже несе fill-колір → другий колірний сигнал = шум. Filled (H) читається як primary-action (A45), а це навігація.
- E (дата-range на картці) — прибрати: вже є як dpill всередині sumcard, на картці дубль+тіснота.
- B(лише число)/C(англ) — відкинути.
- Disabled N≤1 — так (матч мокапу).
**Процес (wsd harness-first):** зібрати ХАРНЕС рефайнутих A-family варіантів (+ альт-іконки: годинник vs stack-візитів vs міні-спарклайн) з бетами, обидві теми, у контексті картки → device XS+15Pro → лок → порт у картку (§5.2 сусід).

### 2. МОК-СІД для device-тесту Динаміки (Konst погодив)
Згенерувати одноразовий localStorage-seed: 1 аптека, 2 крафтнуті visits[]-знімки, що покривають УСІ кольор-стани (improve/degrade/stuck/stable/crit/absent/cross-norm). Paste у devtools → device-тест усього екрана Динаміки без реальних даних. НЕ в продукт-файл (не заглушка). Принцип «mock > real для build/device-test».

### 3. Крок5 — перенесена-ринг §5.2 + §6.5 dark-tile
`--arcLift=.82` + dim (bg-mix+saturate, НЕ whole-opacity) на Home-картці перенесеної (Node 7). Ізольована правка Home-картки.

### 4. Device-тест b13 (арбітр) — обидві теми
- **R2 sticky G-дому** (pin під хедером?)
- матеріал dbox/плиток на OLED (tone-lift читається?)
- `cmp-dyn`-грид вписаність на XS (38+38+50+2×6=150px cluster)
- §5.4 band-swap на filter-mode, press на area-bc/filt-bc
- compare-lock≠canon → §5.1(+A8)+§5.4 канонити ЛИШЕ після device У ПРОДУКТІ b13

---

## Governance-борг (накопичується)
- §5.1(+A8 Δ-колір B) · §5.4 — device-verify → канон.
- wsd: List.Buffer rule · compare-tooling black-log · bench/harness/compare словник · маркер-дубль ask_user_input · подвійне пояснення — виділений governance-чат.
