# QR Lens — Session Summary · sr-pill LOCK complete → impl-план

**База:** `QR_Lens_preview_batch54_4.html` (B54, rev:4) — незмінна цієї сесії (лише harness-раунди).
**Режим сесії:** harness-арбітраж + values-lock (compare/harness 2.4, план→confirm 1.5). Код у базу НЕ вносили.
**Девайси-арбітр:** iPhone XS (375) + 15 Pro (393), обидві теми (12.9).
**Артефакти:** `QR_Lens_srpill_LOCK_harness_v3.html` (фінал), `QR_Lens_srpill_valuesLOCK.md` (CSS-снипети).

---

## 1. ЩО ЗРОБЛЕНО (фінальний стан)
Усі значення sr-pill + Tab-3 empty-охайність **device-locked у harness v3** (обидві теми, XS+15Pro). Готово до імплементації в базу наступним батчем. **НЕ canon** (12.9 — canon лише після патч-у-прод + device-тест ТАМ).

---

## 2. КАНОНІЧНІ ПАРАМЕТРИ (ЗАЛОЧЕНО — імплементувати 1:1)

### 2.1 Сіблінг-аватар (`.avatar` — ЛИШЕ пілюля; dropdown `.sr-av` НЕ чіпати)
```css
.avatar{background:color-mix(in srgb,var(--accent) 15%,var(--card));color:var(--accent-text);box-shadow:0 2.5px 5px -1px rgba(0,0,0,.22)}
[data-theme="dark"] .avatar{background:color-mix(in srgb,var(--accent) 18%,var(--card));color:#45A194;box-shadow:inset 0 1px 0 rgba(255,255,255,.158),inset 0 -1px 0 rgba(0,0,0,.22)}
```
- tint **L15%**(=1:1 qr-tile)/**D18%** · init **L#237770**(=`--accent-text`≈hsl178,55,32)/**D#45A194**(=`--brand-acc`) · size **24** · rad **50% коло** (диференціація від squircle-плитки) · елевація L drop=qr-tile / D inset-тон (A45).
- dark-твін: `[data-theme=dark]` + `@media` A69 (обидва).

### 2.2 Ім'я → `fmtSrName` (display-only; ЕКСПОРТ верифіковано безпечним — grep+VBA, потік односторонній)
```js
function fmtSrName(nm){const p=String(nm).trim().split(/\s+/);return p.length>1?p[0]+' '+p[1].charAt(0)+'.':nm;}
```
- `srNm.textContent = fmtSrName(nm)` (обидва місця рендеру хедера). Повне ФІО лишається в sh-sr/dropdown.

### 2.3 Прес + chevron
- sr-pill: `transition:transform 100ms` (додати; `:active{scale(.96)}` вже є — фікс «мертвого» снапу, персистентний вузол → `:active` ок як icon-btn).
- chevron: rotate **on**, `transition:transform 380ms`; `.sr-pill.open .chev-ico{transform:rotate(180deg)}`; `.open` тогл на open/close `sh-sr`.

### 2.4 Tab-3 «Перейти до Аптек» (`.goto-btn`)
- матеріал **grounded**: solid accent + `box-shadow:0 3px 9px -2px rgba(42,140,132,.5),inset 0 1px 0 rgba(255,255,255,.22)` (L) / `inset 0 1px 0 rgba(255,255,255,.16)` (D, A45).
- прес: JS `.pressing scale(.90)` down 80ms lin / return **spring 280ms** `cubic-bezier(.34,1.5,.64,1)` (A67; делегація на постійний вузол, `:active` прибрати).

### 2.5 empty-hint ОХАЙНІСТЬ (усі 5 інстанцій — grep-verified спільний клас)
```css
.empty-hint{max-width:240px;text-wrap:balance; /* + колір: */ color:hsl(160,7%,55%)}
[data-theme="dark"] .empty-hint{color:hsl(210,6%,55%)}
```
- `hint-mw` **240px** + `text-wrap:balance` (тісний центр-блок, рівні рядки, без сироти).
- легібельність: L `hsl(160,7%,55%)` / D `hsl(210,6%,55%)`.
- **⚠ ПРИБРАТИ хардкод `<br>`** у «Немає обладнання» ×3 (р.1180/1520/1751 `не встановлено<br>QR-обладнання`) — інакше б'ється з balance.
- Покриває: Tab-3 «Оберіть аптеку» (р.888/1510) + «Немає обладнання» Tab-1/3/4.

---

## 3. IMPL-ЧЕКЛІСТ (новий чат — HTML першим 1.5; VBA НЕ треба, ім'я display-only)
1. `.avatar` → Сіблінг §2.1 (звірити: `.avatar` лише пілюля; dark-твін `@media`+`[data-theme]`).
2. `srNm.textContent=fmtSrName(nm)` + хелпер §2.2.
3. sr-pill `transition:transform .1s`; chevron rotate + `.open` тогл.
4. `.goto-btn` grounded + JS-прес A67 §2.4.
5. `.empty-hint` max-width 240 + text-wrap balance + колір §2.5 + **прибрати `<br>` ×3**.
6. `APP_BUILD` +rev (10.6); гейт node --check + tag-balance + grep 0-хардкодів; auto-dark A69 на dark-хардкоди.
7. device XS+15Pro обидві теми → **аж тоді canon** (12.9).

---

## 4. ХВОСТИ / ВІДКРИТІ (не забути)

**HIGH**
- [ ] **Timestamp freshness** — `.live-dot` хардкод `var(--ok)`. Impl: parse `EXPORT_DATE`→вік у днях vs now→поріг→`--ok/warn/late`. Пороги ≤30 ok / 30-90 warn / >90 late (30д=каденс). Pulse приглушити на late.

**MEDIUM**
- [ ] **Canon-борг** (governance-сесія, rule 14.18a — канон перед кодом наступної фази): B54.4 TopArea (device✓ eligible) + черга B52/B52.1/B53/B54/B54.1/B54.2.
- [ ] **v6 TODO-фікс:** `wsd_TODO_running.md` посилається на `brand_harness_v5` → оновити на **v6** (новий еталон).
- [ ] **HARNESS-STANDARD** (додати до еталону wsd 2.4 / §HARNESS-ШАБЛОН на канон-сесії — схвалив Konst):
  - «**?**»-тогл легенди (інструкція за іконкою, згорнутий дефолт — не з'їдає екран).
  - **карет згортання доку** (2.4d — чистий контекст-скрін; док внизу thumb-zone).
  - уроки v1→v3: лупа-через-`scale()`=overlap-баг (магніф-режим ≠ голий scale); harness-прес=JS `.pressing` A67 (не `:active`, iOS ненадійний) + глоб tap-highlight off; важелі ВНИЗУ (2.4).

**LOW / великий workstream**
- [ ] **A58** — grouped-card SR selector (заміна sh-sr/MENU[]) + About-футер (`APP_BUILD` + `t.me/Konst_Andre` `.tgpill`). Адаптувати НЕ 1:1 (12.4): зберегти інфо-архітектуру, пере-скінити матеріал під QR-канон (grounded gcards A45/A66), пере-таймити рух (VT/candidate-A, press A67). Плитка `qr3d`=аватар About-футера. Включити sr-pill press-transition + chevron сюди якщо не увійшло раніше.

---

## 5. ФАЙЛИ В ПРОЕКТІ
**Поточні (для нового чату):**
- `QR_Lens_preview_batch54_4.html` — БАЗА (патчити).
- `QR_Lens_session_summary_srpill_implPLAN.md` — цей файл (усі локи + чекліст + хвости).
- `QR_Lens_srpill_valuesLOCK.md` — CSS-снипети + harness-standard (companion, опц.).
- `QR_Lens_srpill_LOCK_harness_v3.html` — візуальний еталон (опц. reference).
- `Work_Standard.md`, `Lens_iOS_cookbook.md` — протокол/патерни.

**Legacy (не вантажити):** harness v1/v2, srpill_name_harness_v3, попередні session summaries.

---

## 6. УРОКИ ЦІЄЇ СЕСІЇ (generalizable)
- **Лупа через `transform:scale()` — overlap-міна:** масштабований контент вилазить за контейнер, малюється поверх сусідів. Магніф-режим потребує `overflow`-контейнера або нативно більших px, НЕ голого scale. (harness v1→v2 фікс.)
- **Harness-прес = JS `.pressing` (A67), не `:active`:** на iOS `:active` ненадійний; юзер бачить дефолтний tap-highlight («рамка») замість scale. Завжди + глоб `-webkit-tap-highlight-color:transparent`.
- **Важелі ВНИЗУ, стейдж зверху (2.4):** інакше при драгу слайдера не видно зміну. Не порушувати навіть коли важелів багато (компактні + власний скрол доку).
- **Значеннєве рішення → важіль, не хардкод (2.4 bench-vs-hardcode):** hint-охайність (точний max-width) віддано повзунком + превʼю обох текстів, а не зашитим здогадом.
- **Спільний клас → одна правка масштабується (12.1):** grep підтвердив 5 empty-hint = один `.empty-hint` → фікс охайності покрив усі Tab-1/3/4 разом; але виявив хардкод-`<br>`, що вимагає окремого прибирання.

---

## 7. НОВОВВЕДЕННЯ НАСТУПНОГО БАТЧУ (дуже коротко)
1. **sr-pill:** Сіблінг-аватар + ім'я «Прізвище В.» + прес-transition + chevron rotate.
2. **empty-hint (Tab-1/3/4):** max-width 240 + text-wrap balance (прибрати `<br>`×3) + колір.
3. **goto-btn:** grounded матеріал + JS-прес A67.

---

## 8. СТАРТОВЕ ПОВІДОМЛЕННЯ ДЛЯ НОВОГО ЧАТУ (paste-ready)

```
Привіт! Читай протокол: (1) Work_Standard.md (wsd), (2) Lens_iOS_cookbook.md,
(3) QR_Lens_session_summary_srpill_implPLAN.md — контекст + усі локи цієї сесії.

База: QR_Lens_preview_batch54_4.html (B54, rev:4) — ПАТЧИМО її цього батчу.
Минулу сесію ми harness-арбітрували й ЗАЛОЧИЛИ (device✓ XS+15Pro, обидві теми)
значення. Цей чат = ІМПЛЕМЕНТАЦІЯ в базу.

ЩО ІМПЛЕМЕНТУЄМО (деталі+CSS-снипети у самері §2-3):
1. sr-pill: Сіблінг-аватар (accent-15/18% tint + tile-елевація, init D=#45A194,
   коло) + srNm=fmtSrName («Бутуліна В.», display-only, експорт-safe) +
   прес transition:transform .1s + chevron rotate ▾→▴ (380ms, .open).
2. empty-hint (усі 5 інстанцій Tab-1/3/4): max-width 240 + text-wrap balance +
   колір L hsl(160,7%,55%)/D hsl(210,6%,55%). ⚠ ПРИБРАТИ хардкод <br> ×3 у
   «Немає обладнання» (р.1180/1520/1751).
3. goto-btn «Перейти до Аптек»: grounded матеріал + JS-прес A67 (.pressing .90,
   down 80 / return spring 280).

Порядок: HTML/CSS першим (1.5); dark-твін у @media A69 + [data-theme]; grep база
ПЕРЕД claim (12.1); APP_BUILD +rev (10.6); гейт node --check + tag-balance + grep
0-хардкодів; working-копії в outputs (1.6). VBA НЕ треба (ім'я display-only).
Device XS+15Pro обидві теми = фінальний арбітр → аж тоді canon (12.9).

ХВОСТИ (не забудь, у самері §4): freshness (EXPORT_DATE→--ok/warn/late) →
canon-сесія (B54.4 + черга B52-B54.2 + v6 TODO-фікс + harness-standard: «?»-тогл
+ карет-згортання доку) → A58 (grouped-card SR selector + About-футер, не 1:1).

Маркер навантаження — останнім рядком КОЖНОЇ відповіді (дубль у ask_user_input_v0).
```
