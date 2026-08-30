> живе доки: доки відкрита черга QR Lens (продуктовий план, wsd 1.8)
# QR Lens — forward plan (product TODO)

> Це **plan-TODO** (продуктові кроки, що чекають), НЕ wsd-канон. Правила/інструменти канонізуються одразу у wsd/Cookbook і ЗВІДСИ виносяться. Тут лишається тільки план подальших дій. Канон-черга governance — вести у wsd changelog, не тут.
> *Оновлено 05.07.2026: **TopArea + sr-pill арк ЗАКРИТО** — B54.4 + B55, усе device✓. **NEXT = A58.***
> *Оновлено 07.07.2026: **A58-АРК ЗАКРИТО** — B56 (grouped-card SR-селектор + About-Quiet-футер + матеріал scoped #sh-sr) + B56.1 (row-press lift-vs-sink фікс A39/A45 + tgpill тактильний прес + delegated-pointer-прес), обидва **device✓ XS iOS18 + 15Pro iOS26 обидві теми**. База `QR_Lens_preview_batch56_2.html`. Деталі+локнуті values: `QR_Lens_session_summary_B56_B56_1_A58close.md`. **NEXT = КАНОН-СЕСІЯ 14.18a** (борг B52→B56.1 ~9-10 un-canon) АБО settle-бенч. Черга нижче.*

## NEXT — черга (A58 ЗАКРИТО ✅ — обери наступне)

1. **КАНОН-СЕСІЯ 14.18a** (рекомендовано першою) — A58 закрито, борг ~9-10 батчів, drift-ризик. Винести B52→B56.1 у wsd+Cookbook. Заодно 3 скрипт-ідеї + harness-шаблон. Деталі готових-канонити нижче.
2. **SETTLE-БЕНЧ** (свідомо відкладено з B56) — `selSR` settle-then-close delay (~380-460ms перед `closeSheet`) + **row-stagger на open** + **ring-reveal timing** (показати новий вибір ПЕРЕД закриттям). Прес-lift зараз показується під пальцем, але вибір не встигає проявитись до миттєвого закриття. Окремий бенч (не regres — спліт).
3. **A54 Tab-1 Топ/Фокус** — animated 2-segment control (post-A58 queue).
4. **V3-ring фінал** (12.9) — провізорний accent-ring аватара підтверджено device✓; фіналізувати рішення в канон.

Порядок: HTML/CSS-first (1.5); harness→device→lock (12.9); `APP_BUILD +rev`; auto-dark A69; scoped-descendant grep (10.8); гейт `node --check` + tag-balance + grep.

### A58 (B56/B56.1) — device✓, готові канонити:
- **grouped-card SR-матеріал** scoped `#sh-sr` (10.8): `.sh-body` втоплений тарель (A45: L `inset 0 1px 3px rgba(20,40,35,.28)`/D `bg-soft + inset 0 -1px 0 rgba(255,255,255,.28)`) + `.gcard` піднята плита (L drop/D inset-top+drop). filter/eq-шіти не зачеплені.
- **grounded 34px SR-аватар** scoped `#sh-sr-list` — дзеркало хедер `.avatar` B55 §2.1 (tint L15/D18, init L=`--accent-text`/D=`#45A194`, елевація L drop/D inset-тон, font14/800). `.sr-av` вживається ТІЛЬКИ в sh-sr-list → скоуп повний.
- **V3 sel = accent-ring на аватарі** (`box-shadow:0 0 0 2px accent,…`) + ім'я accent/700; прибрано legacy `.sr-av.sel` fill. Статичний шіт → A70 н/з (box-shadow-ring ок). ⚠ **провізорний до proof у проді** (12.9) — фіналізувати.
- **About-Quiet** k/v (device-reviewed; chip/none відхилено): іконки 18px muted stroke1.6; Версія/Оновлено читають `APP_BUILD` (10.6). Eyebrow над About, НЕ над списком (заголовок покриває).
- **`.tgpill` крос-продукт** (`--tg`/`--tg-soft`/`--tg-bd` ×3 блоки A69; light `#229ED9`/dark `#3AAFEA` S-lift): badge+`t.me/нік`+out-стрілка; inline-значення рядка «Зв'язок».
- **row-press LIFT-vs-SINK (A39/A45 — важливий precept):** одна `:active`-формула читається різно per-theme. dark `--bg-soft` темніший за картку → «провал» (хибний affordance). Фікс: **per-theme `--sr-press`** (dark = **LIFT** над card rgb(41,53,62) acc8/wt3/bk5; light = gentle **darken** rgb(228,235,234)). `.sr-opt.pressing{--sr-press + scale(.92)}` dur160. **Урок: press-тон ЗАВЖДИ тестувати обидві теми — lift на OLED, не sink.**
- **tgpill тактильний прес:** `.92` / down70 linear / return280 spring `cubic-bezier(.34,1.70,.64,1)` (over1.70). Дрібний елемент = різкий (A67-драбина).
- **delegated pointer-прес** на статичний контейнер (`#sh-sr`, `closest('.sr-opt,.tgpill')`, one-time) — iOS-надійно, переживає rebuild, НЕ `:active`.

## Parked

- **Border капсули** — Konst думає, чи прибирати вагу бордера. PARKED, рішення за ним.

---

## Governance — канон-сесія (ПІСЛЯ A58, за рішенням Konst)

**⚠ 14.18a-борг РОСТЕ: тепер `B52 / B52.1 / B53 / B54 / B54.1 / B54.2 / B54.4(TopArea) / B55 / B56 / B56.1(A58)` = ~9-10 батчів device✓ un-canon.** Konst: канон стоїть ЗА активним build-арком. **A58 ЗАКРИТО → флаг активний: канон-сесія = гарячий кандидат на наступну** (drift-ризик, який 14.18a і покриває). A58-кандидати — у секції NEXT вище.

### Device✓ — готові канонити (з `batch55_1`, сесія sr-pill/freshness):
- **sr-pill grounded сіблінг-аватар** (B55 §2.1): accent-tint L15/D18 + init L=`--accent-text`(#237770)/D=`#45A194`(коло; НЕ реюз токен `--brand-acc`) + елевація L drop/D inset-тон (A45). Диференціація коло↔squircle-плитка = роль (rep-identity vs brand). Auto-dark A69.
- **fmtSrName «Прізвище В.»** (B55 §2.2): хедер display-only, повне ФІО лишається у dropdown/`sh-sr`; ЕКСПОРТ/VBA не чіпано (потік DATA→HTML односторонній). Однослівне → як є.
- **chevron rotate ▾→▴** (B55 §2.3): 380ms decel `cubic-bezier(.32,.72,0,1)` + `.sr-pill.open`; `.open` ставиться в trigger-лістенері, знімається у `closeSheet(id==='sh-sr')` → покриває ВСІ close-шляхи (бекдроп/×/свайп/selSR); reduced-motion снап.
- **empty-hint tidy** (B55 §2.5): `max-width:240` + `text-wrap:balance` + per-theme колір (L `hsl(160,7,55)`/D `hsl(210,6,55)`); спільний клас → 5 інстанцій Tab-1/3/4 одним фіксом; прибрано хардкод `<br>×3`.
- **goto-btn grounded + A67 press `.90`** (B55 §2.4): делегація на ПОСТІЙНИЙ `#app` (`closest('.goto-btn')` — переживає renderQR/selectOutlet rebuild статик+JS); L drop(accent-tint .5)+top-gloss / D inset-only (A45). onclick=навігація лишена.
- **freshness-семафор** (B55 §2.6 — ← був candidate «timestamp freshness», тепер IMPL+device✓): `.live-dot` колір за віком `EXPORT_DATE`(DD.MM.YYYY) → клас `st-warn`/`st-late`; **ПОРОГИ ≤3 ok / 4–7 warn / ≥8 late** (device-cadence Konst: KPI оновлюється 2×/тижд → 30-90 завеликий); pulse OFF на late; токен-колір theme-aware (A69-твін НЕ треба — токени флипаються самі). Фолбек: не-парситься → лишається ok.

### Device✓ — TopArea (з `batch54_4`, порт зроблено):
- **grounded-бар (H1)** + **subtitle-timestamp** + **бренд-лок-ап (H2)**. Значення обох тем у `QR_Lens_session_summary_TopArea_H1_LOCK.md` + `..._TopArea_H2v5.md`. Бренд-еталон = **`QR_Lens_brand_harness_v6.html`** (v6, не v5).
- **F1 (harness-fidelity + A66-нотатка):** top-bar ridge перекритий статус-баром (safe-area) → ridge = інструмент для елементів із видимим верхнім краєм (hero/eq/A66), НЕ top-бару; harness верхньої зони МУСИТЬ симулювати статус-бар.
- **F2 (нове Axx «scroll-edge separator»):** dark scroll-state = яскравіший hairline по нижньому краю (iOS scrollEdge→standard), НЕ drop-тінь A45; `scrollElev` = theme-split важіль (light=drop / dark=hairline-brightness).
- **grounded-chrome:** Apple deference+depth реалізуємо СВОЇМ механізмом (grounded), не копіюємо скло; таббар лишається єдиним склом.
- **timestamp = subtitle** (не well — deboss бреше афордансом). *(freshness-семафор → перенесено вище, B55 device✓.)*
- **branded-house lock-ap** (FedEx-модель: константа `·Lens`+рамка / змінна префікс+колір+гліф per-product; QR=QR×3, KPI=bars, Drive=gauge, ВТМ=receipt).
- **Процес-precept (wsd 2.x):** на будь-якому elevation/shadow-коді — звіряти A45 + theme-split ДО першої чернетки, не після device-catch.

### Cookbook-кандидати — device✓ (з `batch54_3`, сесія Tab4E):
- **Concentric-radius:** outer radius = inner radius + padding. Прецедент: eq-card тарель radius+slotGap=18 (harness v3, device✓).
- **Copy-confirm icon morph:** контекстний своп 📋→✓ CSS-only крос-фейд, обидва гліфи в DOM (grid-стек), opacity+scale(.25→1)+blur(4→0), dur 300, ease `cubic-bezier(.2,0,0,1)`, bounce 0, interruptible, revert ~2000 (device✓).
- **text-wrap:** `balance` заголовки / `pretty` тіло (device✓).
- **PRESS-таксономія → Cookbook A67-розширення (з B56.1, device✓):** (1) **list-row select-press = background TONE, не scale-домінанта** — per-theme `--press` (dark LIFT над картку / light gentle darken; A39/A45); опц. `scale(.92)` як «плаваюча плитка». Тон ЗАВЖДИ обидві теми (dark sink = хибний affordance на OLED). (2) **small link-pill (tgpill) press** = `scale(.92)`, down linear ~70ms / return spring ~280ms over~1.70 — дрібний елемент, різкий (драбина: large card інерційний 950ms → chip .84-.92 → pill .92/спринг). (3) **delegated pointer-прес на статичний контейнер** (`.pressing`, не `:active`) — iOS-надійно, переживає innerHTML-rebuild динамічних дітей.

### Запарковані eq-card патерни (з `eqcard_harness_v1`, не вжиті, можуть знадобитись):
- A Module-tile+left status spine · B Gauge-native instrument channel (matte) · C Conservative refine (thin edge status line) · AB spine+channel · D Tag/label top-strip.

---

> **30.07.2026 (governance-пас, сесія A).** Секція «Процес-кандидати у wsd» (колишні р.62–74)
> переїхала у **`wsd_delta_running.md`** — вона ніколи не була продуктовим планом QR Lens.
> Файл перейменовано `wsd_TODO_running.md` → `QR_Lens_forward_plan.md`: ім'я тепер відповідає вмісту.
> живе доки: доки відкрита черга QR Lens (продуктовий план, wsd 1.8).
