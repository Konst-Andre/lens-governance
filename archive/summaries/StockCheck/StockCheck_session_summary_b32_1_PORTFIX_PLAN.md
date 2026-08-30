# StockCheck · Session Summary — B32.1 Port-Fix (Plan + Locks)

живе доки: активна до старту патч-сесії b32.1; після device-verify всіх патчів — закрити/переписати наступним самері
Дата фіксації: 09.08.2026
Аудитований артефакт: `StockCheck_port_b32_0_Codex.html` (810 КБ) — це результат інтеграції Codex, ОКРЕМИЙ від базового `StockCheck_port_b32_0.html` (523 КБ, «ШОВ»). Патчимо Codex-файл.

---

## 0. СТАРТ НАСТУПНОГО ЧАТУ (paste-ready → одразу в блок КОД)

```
Мова — українська. Продовжуємо StockCheck b32.1 (port-fix Codex-файлу).

СТАРТ (wsd 1.1): Lens_INDEX.md → цей самері (StockCheck_session_summary_b32_1_PORTFIX_PLAN.md, відкриті питання зверху) → Work_Standard.md → cookbook том за індексом (O-47/Р-46/A45).

Файл-ціль: StockCheck_port_b32_0_Codex.html. Грепати точково, НЕ вантажити цілком.

Починаємо ОДРАЗУ з патчів, Крок 1 (CSS). Порядок фіксований у §4 самері:
  Крок 1 CSS: plate 82→73 · зняти min-height:162 (cardH дерайв ≈144.3) · wellH fallback 374→339 · tone.D dark-override =120 (заглиблена ніша) · sh 16→12
  Крок 2 JS: region-reset (S.net='' при зміні області, р.2903) · «Всі мережі» лишається · БАМП БІЛДУ b32.1
  Крок 3 JS+HTML: mini-mark обраної мережі в .ntile (updateNetBtn)

Цикл: план-мікро вже пройдено (§6), тож на кожен крок — короткий мікроскоп-дельта → підтвердження → код. HTML/CSS перед JS. Device — фінальний арбітр.
Перед видачею: python3 Lens_validate.py --html <файл>.

НЕ чіпати: kNets(16/16), Р-46/EB, DATA, geometry картки/журналу, P1L, .netbtn база, tone.L=100.
```

---

## 1. ВІДКРИТІ ПИТАННЯ (зверху)

1. **sh12 — точні числа.** Світла тінь картки: спек `sh12` (було sh16). Codex зараз `box-shadow:0 2.7px 7.3px rgba(20,50,42,.145)`. Перед патчем P4 — грепнути формулу стенду `--tileSh` у `StockCheck_netmark_stagebench_v3_7.html`, вивести точний box-shadow для sh12. НЕ вгадувати.
2. **Номер ver при бампі.** Пропоную `v2.25.0` (feature-batch). Підтвердити при патчі Кроку 2.
3. **`@media(max-width:359px)`** — при plate=73 базово там plate 64 / min-height 134 / rad 23. Поза scope цього батчу, лишити з міткою NOT VERIFIED (див. §7).
4. **Device-check Фармастора** після P6 (гліф + per-net scale в .ntile).

---

## 2. ЩО ЗРОБЛЕНО ЦІЄЇ СЕСІЇ (forensic audit)

Проведено forensic port audit Codex-файлу проти stagebench v3.7 + device-lock. Ланцюг: HANDOFF → STAGEBENCH v3.7 → CODEX PORT → LOCK. Грепано точково.

O-47 підтверджено PASS проти LOCK: rad26 · scrim.42(спільний) · dur380 · peek16 · fade24 · wellRad20 · wellPad10 · tone.L100 · calc-height (Р-48 формула жива) · cardH/wellH = outputs.
Р-46 (eyebrow) PASS: eb-card 12/700/.42/UP/mb2/ink100 · eb-jr 12/600/.42/UP/mb2/ink100 · rep=all. НЕ чіпати.
kNets 16/16 = спеку. diagBg не портовано (коректно, intentional).

Знайдені реальні розбіжності → стали рішеннями §3 / патчами §4.

---

## 3. РІШЕННЯ, ЗАФІКСОВАНІ (канон-кандидати; повний текст, не «в буфер» — 14.29)

**D1 · plate = 73.** P0-конфлікт HANDOFF (73 actual P1L vs 82 explicit) закрито оператором на користь **73** (як у стенді, розмір іконки). cardH144.3 / wellH339 — ВИХІДНІ від plate=73 (2·144.3+14+16+20 ≈ 339), не важелі. Codex мав 82.

**D2 · tone.D = 120 (dark, заглиблена ніша).** Оператор підтвердив: LOCK=120 вірний для dark. Семантика стенду: `wt>100 → color-mix(in srgb,#000 (wt-100)%,var(--bg))` = затемнення dark-well на 20% = recessed (Р-49). Codex захардкодив `var(--bg)` = tone100 (ймовірно підхопив scene-default v3.7 р.750, а не LOCK.o47 р.782) → **STALE/PORT BUG, патчиться**. tone.L лишається 100.

**D3 · «Всі мережі» — ЛИШАЄМО.** У stagebench v3.7 такого контролу НЕМА (Codex додав reset-картку `#npAll` + `#npSub "Всі мережі"`). Рішення оператора: лишити — це видима поверхня стану `S.net=''`, узгоджено з базовою фільтр-моделлю.

**D4 · region-reset.** Codex НЕ скидає `S.net` при зміні області → stale-фільтр може дати 0 аптек у новому регіоні. Рішення: у хендлері зміни області (р.2903) додати `S.net='';saveNet();updateNetBtn();`. Дата-ліку немає — `topMatch` фільтрує area+net, список коректний; чиниться саме stale selected-net.

**D5 · trigger mini-mark sync.** `.ntile` (кнопка netBtn, р.1271) показує ЗАХАРДКОДЖЕНИЙ generic grid SVG; `updateNetBtn` (р.2789) ставить лише aria-label. Фікс `.bscale:scale(1.55)` — badge-scale під generic, не під mark мережі. Рішення: `updateNetBtn` рендерить mark обраної мережі: растр → `NET_ASSETS[slug].mini`, Фармастор → гліф, масштаб per-net через `NET_PICK_SCALE` (не фікс 1.55); `S.net=''` → generic grid fallback. Причину встановлено (trigger-шлях), НЕ правити CSS-розміром. Закриває HANDOFF Known Issue #3/#5.

**D6 · sh = 12.** Світла тінь картки: 16→12 (Крок6 spec). Точні числа — за формулою стенду `--tileSh` (див. §1.1).

**D7 · БАМП БІЛДУ (обов'язково).** Codex НЕ оновив білд-маркер (лишив b32.0/v2.24.0/08.08.2026 через Р-35 — «ШОВ» без видимих змін). У b32.1 є видимі зміни (plate, ntile-mark, recessed dark-well, region-reset) → wsd 10.6 вимагає бампу. Патч: `APP_BUILD` → build `stockcheck-pwa.b32.1`, ver `v2.25.0` (підтвердити), date `09.08.2026`.

**D8 · НЕ чіпати** (verified intact): kNets 16/16, Р-46/EB, DATA-блок, geometry картки/журналу, P1L, `.netbtn` база, tone.L=100.

---

## 4. ПЛАН ПАТЧІВ b32.1 (1:1, HTML/CSS → JS)

### Крок 1 — CSS
- **P1.** `#sh-network{...--npPlate:82px...}` → `73px`
- **P2.** `.np-card{...min-height:162px...}` → зняти підлогу (cardH дерайв ≈144.3); `.np-label{min-height:calc(--npLbl*2.36)}` тримає 2 рядки → без джитеру
- **P3.** `.np-well{max-height:var(--npWellH,374px)}` → фолбек `339px` (measureNetworkWell перерахує в рантаймі)
- **P4.** світла `.np-card box-shadow` sh16→**sh12** (точні числа з формули стенду `--tileSh`)
- **P5.** **tone.D dark-override:** додати `[data-theme="dark"] #sh-network{--npWellBg:color-mix(in srgb,#000 20%,var(--bg))}` (+ дубль у `@media(prefers-color-scheme:dark):root:not([data-theme="light"])`) = tone 120, заглиблена ніша

### Крок 2 — JS + білд
- **P6.** р.2903 (зміна області): додати `S.net='';saveNet();updateNetBtn();` (region-reset). «Всі мережі» лишається.
- **P7.** `APP_BUILD` бамп: build `stockcheck-pwa.b32.1` · ver `v2.25.0` (підтвердити) · date `09.08.2026`

### Крок 3 — JS + HTML
- **P8.** `updateNetBtn` рендерить mark обраної мережі в `.ntile`: растр `NET_ASSETS[slug].mini` / Фармастор гліф / per-net scale через `NET_PICK_SCALE`; `S.net=''` → generic grid. Замінити фікс `.bscale:1.55` на per-net. Device-check Фармастора.

---

## 5. DEVICE-LOCK O-47 / Крок6 (АКТУАЛЬНИЙ — з поправкою tone.D=120)

```
NETMARK v3.7 · Крок6 | xs | cols=3 plate=73 rad=16 gX=10 gY=14 pad=9 lbl=12 cnt=10
|| K_MARK=1.00 signPad=3
   kNets[ANC:1.12 A911:1.12 PODOROZHNYK:1.28 BAZHAEMO:1.11 MED_SERVIS:1.05 FARMASTOR:1.35
         UAH:1.28 NARODNA:1.10 FAKULTET:1.25 ZAITSEVA:1.29 TRIOL:1.10 MOYA_APTEKA:1.15
         LIKY_POLTAVSHCHYNY:1.12 LINDA_FARM:1.02 CENTRALNA:1.19 APTEKA_NC:1.03]
|| ACT.L=acc/w1/a42/t44/chk0/lift4/sc105/plR0/lbl0
   ACT.D=acc/w1/a73/t38/chk0/lift4/sc105/plR1/lbl1
|| MAT.L=bg28/bd82/sh12/plM0/plB73/ro0
   MAT.D=bg37/bd73/ridge20/plM0/plB50/ro1
|| EB on1 rep=all C=12/700/0.42/UP/g2 J=12/600/0.42/UP/g2(+2) ink.L=100/100 ink.D=100/100
|| O47 шіт rad26 scrim42 dur380 | well peek16 rad20 pad10 fade24 tone.L100 tone.D120
   cardH144.3 wellH339 || diagBg=8
```

ПОПРАВКА проти мого чат-повідомлення від сьогодні: у Крок6-спеку оператора було `tone.D100` — оператор скоригував на **tone.D=120** (LOCK вірний для dark). Тут зафіксовано 120. cardH/wellH — outputs.

---

## 6. МІКРОСКОП ПЛАНУ (перенесено 1:1)

1. **Числа.** plate=73 (не 82). cardH144.3/wellH339 = OUTPUTS: дерайвити (зняти min-height:162 + фолбек 339), НЕ хардкодити (cardH/wellH ≠ важелі). tone.D=120 (не 100). sh12 exact = pending грепу стенду `--tileSh`. kNets 16/16 = спеку → не чіпати. tone.L=100.
2. **Детектор на правильному виході.** wellH міряється `measureNetworkWell` з живого `card.offsetHeight` ПІСЛЯ зняття підлоги → 375-device підтверджує natural ≈144.3.
3. **Покриття.** plate каскадить у `@media(max-width:359px)` — поза scope, мітка NOT VERIFIED. Label 2-line reserve захищає від джитеру.
4. **Залежності.** sh12 ← формула стенду. P8 ← `.mini` для 15 растрів + гліф Фармастора (підтверджено в NET_ASSETS). P6 ← без `saveNet()+updateNetBtn()` персистенція/лейбл протухнуть. P5 ← дубль dark-override у `@media auto-dark`, інакше тече в auto-light (A69).
5. **Роутинг.** P1–P5 CSS-first. P6–P8 JS/HTML, після CSS. «Всі мережі» лишається. НЕ чіпати: kNets, Р-46/EB, DATA, geometry, .netbtn.

---

## 7. NOT VERIFIED / DEVICE-CHECK

- tone.D=120 після P5 — перцептивна заглибленість ніші на OLED.
- responsive `<360` (plate 64 / cardH 134 / rad 23) — не звірено при plate=73 базі.
- journal eyebrow eff-gap (mb2 + parent gap 2 = 4) — HANDOFF NOT VERIFIED.
- Фармастор гліф у `.ntile` (P8) — device.
- PWA/offline + повний regression після патчів.

---

## 8. НЕ ЧІПАТИ

kNets (16/16) · Р-46/EB (eb-card/eb-jr токени) · DATA-блок · geometry картки/журналу · P1L · `.netbtn` база · tone.L=100 · diagBg (не портувати).

---

## 9. ФАЙЛИ / ANCHORS (Codex-файл)

- `#sh-network{...}` р.1208 (rad26/dur380/pad-bottom calc) · CSS-змінні netpick р.1221–1222
- `.np-well` р.1223–1226 (max-height fallback, fade::after) · `.np-card` р.1228–1230 (min-height162, box-shadow)
- dark overrides `.np-card/.np-plate` р.1239–1245 · `@media(max-width:359px)` р.1246
- `.ntile`/`.bscale` р.673–690 · netBtn HTML р.1270–1271
- `NET_PICK_SCALE` р.2774–2776 · `NET_PICK_GLYPH` р.2777 · `networkPlate` р.2797 · `networkCard` р.2802
- `updateNetBtn` р.2789 · `measureNetworkWell` р.2806 · `renderNetworkPicker`/`#npAll` р.2811 · `selectNetwork` р.2816
- area-change (region-reset target) р.2903 · `APP_BUILD` р.2572
