# QR Lens — Session Summary: A58-motion план + SR-persistence рішення (PRE-IMPL)

**Дата:** 08.07.2026 · **База:** `QR_Lens_preview_batch56_2.html` (batch56/rev2/phase4, device✓)
**Тип сесії:** розсуди/рішення — **коду НЕ шипнуто.** Наступна сесія = імплементація.

---

## 0. Дві правки на старті (обидві grep-підтверджені)

1. **A58 НЕ закрито.** B56/B56.1 закрили лише **матеріал/структуру/прес** (device✓). **Рух** щита (поява / закриття / «щоб було видно натиск» / як виглядає відкриття) — це теж A58, і він **відкритий**. Канон (14.18a) — передчасний, поки рух не залочено. **Знято рекомендацію «канон-first».**
2. **A54 Tab-1 Топ/Фокус 2-segment — ЗРОБЛЕНО давно (B42/A54).** Верифіковано: `.a54-cap`+`.a54-thumb` 500ms spring, `switchTab1Mode` (р.1452), `placeTab1Thumb` (р.1494, коментар «A54-канон single-container»), повна seg-токен-система. Це **стейл-хвіст**, що заповз у 3 місця → **видалити з черги:** starter §C / попереднє самері NEXT#3 / `wsd_TODO_running.md` #3 (post-A58 queue).

---

## 1. ЗАЛОЧЕНИЙ НАПРЯМ (сиквенс)

- **T1 (першим):** file-scoped **SR-persistence** (localStorage), ключ = `EXPORT_DATE`.
- **T2 (після):** **motion-harness** для щита вибору SR (поява + вибір), з бюджетом руху, **переозначеним** через T1.

**Наскрізна нитка:** persistence — *upstream* руху. Зробили T1 → щит рідко-open (~2×/тижд) → багатший рух доречний. Без T1 → 15×/день → мінімал/снап.

---

## 2. T1 — SR-PERSISTENCE (залочений дизайн)

**Чому взагалі:** зараз вибір НЕ зберігається → **15×/день** треба перевибирати себе (кожне відкриття PWA скидає `S.sr`). З persistence → перевибір лише при новому експорті даних → **~2×/тижд**. Прибирає найчастіше денне тертя.

**Ключове відкриття, що зняло страх:** застосунок **УЖЕ персиститься** — тему (`qr-theme`, 3-state, FOUC-фікс у `<head>`, try/catch private-mode; р.15/24/2203–2247). Тобто «нічого не зберігається» = не точно; SR-пам'ять — **дзеркало наявного патерну**, не новий виняток.

**Дизайн (простий, file-scoped — інстинкт Konst, кращий за «стабільний ідентифікатор»):**
- Ключувати на `EXPORT_DATE` (р.1045). Новий експорт → ключ не збігся → **авто-скид** = саме та безпека («стейл не переживає апдейт»), вбудована в ключ.
- Індекс безпечно відновлювати ПРЯМО (не треба id-ревалідації), бо відновлюється лише проти **того самого експорту** → той самий `DATA` → нема index-drift.
- **init restore:** `try{const s=JSON.parse(localStorage.getItem('qr-sr')); if(s&&s.d===EXPORT_DATE) S.sr=s.i}catch{}`
- **у `selSR` (р.1966):** `try{localStorage.setItem('qr-sr',JSON.stringify({d:EXPORT_DATE,i}))}catch{}`
- Fallback (not-found / стемп-mismatch / private-mode): поточна поведінка (нічого не обрано / default). Дзеркалить theme-guard.

**Відкриті дрібниці (вирішити в імпл):**
- назва ключа (`qr-sr` vs конвенція теми);
- **same-day re-export edge:** два експорти в один день ділять `EXPORT_DATE` → якщо того дня переставив реп, індекс міг з'їхати. Копійчана страховка: fingerprint = `EXPORT_DATE`+`DATA.length` (чи +перше ім'я). Прийняти edge чи страхуватись — рішення Konst.

**Excel/VBA:** **0 змін даних/логіки** (використовує наявний `EXPORT_DATE`). Єдине — **регенерувати вбудований HTML-шаблон** у `.xlsm` з пропатченого HTML (`DATA`→`/*__DATA__*/`), стандартний post-patch крок. В імпл: грепнути шаблон на `selSR`+init, якщо стейл — регенерувати.

**Device-матриця T1:** обрав→переоткрив PWA→**лишився** · новий `EXPORT_DATE`→**скид** · private-mode→**не падає** (boot). XS iOS18 + 15Pro iOS26.

**Гейт:** `node --check` + tag-balance + grep-anchors; APP_BUILD +rev (10.6); working-копія в outputs (1.6).

**Рекомендація:** шипнути T1 як **окремий маленький батч** ПЕРЕД harness (логіка, не візуал — harness не потрібен; лише device-матриця вище).

---

## 3. T2 — MOTION-HARNESS (планований склад)

**Осі (3 незалежні) + N-slider:**
- `Поява [none / E2-плита / E1-каскад]` × `Announce [E3 off/on]` × `Вибір [A / B / C / D-мінімал]`
- `N-rows slider (3/6/12)` — row-count **data-driven** (preview=6 = `DATA.length` р.1043; varies per export) → рух має читатись на діапазоні.

**Механічна база (grep✓):** рядки sh-sr будуються `innerHTML` на **КОЖНЕ** відкриття (р.1955) → свіжий DOM → `staggerRows` (A71) чіпляється тривіально одразу після (як eq-list р.2153). Persistent-DOM засторог нема. Щит = стандартна A18-оболонка (`.sh-bg`/`.sh-box`/`.sh-grip`/`.sh-body`/`.gcard#sh-sr-list`, р.993–998).

**Варіанти (описи для збірки):**
- **Поява E1 «Каскад»** — A71 row-stagger згори-вниз зі слайдом; cap total-dur (щоб довгий список не тягнувся) + min-step (щоб короткий не був непомітним).
- **Поява E2 «Плита»** — БЕЗ по-рядкового; `.gcard` fade+micro-scale(.98→1) як один об'єкт; римується з grounded-плитою (A45). Найтихіша.
- **Announce E3** — ring поточного вибору 1-shot scale(1.1→1.0)+glow-fade; **тільки на open, НІКОЛИ loop** (A71-анти). Модифікатор поверх бази, не сиблінг.
- **Вибір A «Тихе підтвердження»** *(реком.)* — press-lift(B56.1) → ring кросфейд на новий + згасання на старому + **micro-grow(.9→1)** = «фокус конденсується» → settle-пауза → close. Римується з E3 (ring = єдиний токен фокуса).
- **Вибір B «Ring несе фокус»** — ring травел-по-Y (A54-thumb метафора) + **graceful-fallback→A**, якщо старий/новий не обидва на екрані (страхує довгу дистанцію на data-driven списку).
- **Вибір C «Штамп»** — over-scale pop; ймовірно off-brand (для тихого тула забагато); тримати для контрасту.
- **Вибір D «Мінімал» (control)** — лише press-lift + static ring, 0 доданої затримки. **Серйозний претендент**, якщо T1 НЕ роблять (15×/день).

**Оновлена робоча гіпотеза:** T1-зроблено → рідко-open → **E1/E3 + A(settle)** доречні; T1-нема → **D-мінімал/снап**.

**Канон-натяки:**
- settle-then-close: A18.1 «контрол у шіті, що закриває → відклади close ~250ms» → **розширюємо ~380–460ms** для ring-reveal (лочити на device).
- reduced-motion → снап (A71 reduceOn + settle→instant).
- Harness = дзеркало `brand_harness_v6` spine; dual-theme; реальний слайд+свіжі рядки; replay «↻Відкрити»/«↻Обрати»; per-axis sliders; Copy-ALL. About-футер НЕ каскадимо (тихий бекдроп).

---

## 4. Verified code-anchors (12.1)

| Що | Де |
|---|---|
| `selSR` миттєвий close+render | р.1966 |
| ring статичний box-shadow (`.sr-opt.sel .sr-av`) | р.788 |
| sh-sr shell (A18 standard) | р.993–998 |
| sr-рядки `innerHTML` на open | р.1955 |
| `DATA` = 6 реп | р.1043 |
| `EXPORT_DATE` (freshness + persist-key) | р.1045 |
| theme-persist (patтерн для дзеркала) | р.15/24/2203–2247 |
| A54 thumb 500ms spring (DONE) | р.1494 |
| `staggerRows` вживання | р.1461/2071/2153 |

---

## 5. NEXT (для нового чату)

1. **T1 SR-persistence** — окремий маленький батч (HTML-first ~5 рядків → device-матриця → gate → regenerate template у .xlsm).
2. **T2 motion-harness** — після T1, склад §3.
3. Прибрати A54-хвіст із `wsd_TODO_running.md` #3.
4. Канон 14.18a (B52→B56.1 + T1/T2) — **тільки після** T2 device✓.

---

## 6. PASTE-READY СТАРТЕР (копіювати в новий чат)

```
Привіт! QR Lens. Продовжуємо з самері QR_Lens_session_summary_A58motion_persist_PLAN.md.

Читай через view ПЕРЕД кодом:
1. Work_Standard.md (wsd v2.24) — протокол
2. Lens_iOS_cookbook.md — UI/iOS/motion (A18/A18.1 sheet+settle, A45, A54 spring, A69, A71 stagger)
3. QR_Lens_session_summary_A58motion_persist_PLAN.md — контекст + локи цієї сесії
4. wsd_TODO_running.md

База: QR_Lens_preview_batch56_2.html (batch56/rev2/phase4, device✓).

РОБИМО T1 — SR-persistence (окремий маленький батч, ПЕРЕД motion-harness):
• file-scoped localStorage, ключ EXPORT_DATE; дзеркало theme-persist (р.15/24/2203-2247, try/catch guard).
• init: try{const s=JSON.parse(localStorage.getItem('qr-sr')); if(s&&s.d===EXPORT_DATE) S.sr=s.i}catch{}
• selSR (р.1966): try{localStorage.setItem('qr-sr',JSON.stringify({d:EXPORT_DATE,i}))}catch{}
• fallback: mismatch/private-mode → поточна поведінка (default).
• вирішити: назва ключа + same-day-export fingerprint (EXPORT_DATE+DATA.length) — yes/no.
• Excel/VBA: 0 змін даних/логіки; тільки регенерувати HTML-шаблон у .xlsm (DATA→/*__DATA__*/) — грепнути selSR+init у шаблоні.
• Device-матриця: обрав→переоткрив PWA→лишився · новий EXPORT_DATE→скид · private-mode→не падає.

Порядок: grep база ПЕРЕД claim (12.1); HTML-first (1.5) Plan→confirm→код; auto-dark A69; scoped-descendant grep (10.8); APP_BUILD +rev (10.6); гейт node --check + tag-balance + grep; working-копії в outputs (1.6). Маркер навантаження — останнім рядком, дубльований у ask_user_input_v0.

Далі T2 — motion-harness (Поява[none/E2/E1] × Announce[E3] × Вибір[A/B/C/D] + N-slider), склад у §3 самері. Гіпотеза: T1-зроблено → рідко-open → багатший рух.

Прибрати A54-хвіст із TODO#3 (A54 Топ/Фокус ЗРОБЛЕНО B42/A54, р.1494).
```
