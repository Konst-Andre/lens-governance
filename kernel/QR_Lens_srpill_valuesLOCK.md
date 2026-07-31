> живе доки: назавжди (вічне, wsd 1.8) — значення sr-пігулки QR Lens

# QR Lens — sr-pill LOCK (values) + Tab-3 hint-охайність · harness v3

**База:** `QR_Lens_preview_batch54_4.html` (B54, rev:4) — незмінна.
**Артефакт:** `QR_Lens_srpill_LOCK_harness_v3.html` (device-viewed XS+15Pro, обидві теми).
**Статус:** harness-locked (12.9) — **НЕ canon**; canon лише після патч-у-прод + device-тест ТАМ.

---

## 1. ЗАЛОЧЕНІ ЗНАЧЕННЯ (device-picked Konst у harness v3)

### 1.1 Сіблінг-аватар (`.avatar`, лише пілюля; dropdown=`.sr-av` НЕ чіпати)
- `av-tint`: **L 15%** (=1:1 qr-tile) · **D 18%** — `background:color-mix(in srgb,var(--accent) N%,var(--card))`
- `av-init` (ініціал): **L `hsl(178,55%,32%)`** · **D `hsl(172,40%,45%)`** (=`--brand-acc`; accent-lock brand-harness v6)
- `av-size`: **24px** · `av-rad`: **50% (коло)** — форма = диференціація від qr-tile (squircle)
- елевація: **L drop `0 2.5px 5px -1px rgba(0,0,0,.22)`** (=qr-tile) · **D inset-тон** `inset 0 1px 0 rgba(255,255,255,.158),inset 0 -1px 0 rgba(0,0,0,.22)` (A45 — не drop)
- CSS-старт (dark-твін у `@media` A69 + `[data-theme]`):
  ```css
  .avatar{background:color-mix(in srgb,var(--accent) 15%,var(--card));color:var(--accent-text);box-shadow:0 2.5px 5px -1px rgba(0,0,0,.22)}
  [data-theme="dark"] .avatar{background:color-mix(in srgb,var(--accent) 18%,var(--card));color:#45A194;box-shadow:inset 0 1px 0 rgba(255,255,255,.158),inset 0 -1px 0 rgba(0,0,0,.22)}
  ```
  (NB: `--accent-text` світла = #237770 ≈ hsl(178,55%,32%) — можна лишити токен; D ініціал = #45A194)

### 1.2 Ім'я → `fmtSrName` (display-only, ЕКСПОРТ-безпечно)
- `srNm.textContent = fmtSrName(nm)` → «Бутуліна В.»
- `function fmtSrName(nm){const p=String(nm).trim().split(/\s+/);return p.length>1?p[0]+' '+p[1].charAt(0)+'.':nm;}`

### 1.3 Прес + chevron
- sr-pill прес: `transition:transform 100ms` + `:active{transform:scale(.96)}` (фікс «мертвого» снапу; персистентний вузол → `:active` ок, як icon-btn)
- chevron: rotate **on**, `transition:transform 380ms` (`.sr-pill.open .chev-ico{transform:rotate(180deg)}`); `.open` тогл при відкритті sh-sr

### 1.4 Tab-3 «Перейти до Аптек» (`.goto-btn`)
- прес: `.pressing scale(.90)` down 80ms lin / return **spring 280ms** `cubic-bezier(.34,1.5,.64,1)` (A67; НЕ `:active`)
- матеріал: **grounded** — solid accent + `box-shadow:0 3px 9px -2px rgba(42,140,132,.5),inset 0 1px 0 rgba(255,255,255,.22)` (L) / `inset 0 1px 0 rgba(255,255,255,.16)` (D, A45)

### 1.5 Легібельність empty-hint
- `hint-L`: **L 55** (`hsl(160,7%,55%)`) · **D 55** (`hsl(210,6%,55%)`) — трохи темніше/чіткіше за `--muted-2` базу

---

## 2. НОВЕ — Tab-3 hint-ОХАЙНІСТЬ (device-pending у v3, мій дефолт-бет)
**Спостереження Konst:** empty-hint розтягнутий на всю картку → 2-й рядок із сиротою, «кинутий на фон текст».
**Фікс (типографіка, НЕ рамка):** `.empty-hint{max-width:~240px;text-wrap:balance}` — тісний центр-блок, рівні рядки.
- **МОЯ СТАВКА (default v3):** `hint-mw 240px` + `text-wrap:balance`. Konst докручує mw на девайсі (превʼю обох текстів у v3).
- **ПОКРИВАЄ ВСІ 5 інстанцій `.empty-hint`** (спільний клас, grep-verified 12.1): Tab-3 «Оберіть аптеку» (р.888/1510) + «Немає обладнання» ×3 (р.1180/1520/1751 — Tab-1 per-outlet, Tab-3 QR, Tab-4 eq-empty).
- **⚠ КРИТИЧНО при імплементації:** «Немає обладнання» має **хардкод `<br>`** (`не встановлено<br>QR-обладнання`) → **ПРИБРАТИ `<br>` у всіх 3** інстанціях, інакше ручний брейк б'ється з balance/max-width.

---

## 3. HARNESS-STANDARD — додати до еталону (wsd 2.4, fold at canon)
Konst схвалив 2 корисні речі з цього harness → у harness-шаблон (поряд із fidelity-драбиною / preset-банком / Copy-ALL):
- **«?»-тогл легенди** — інструкція-текст схована за іконкою «?» (згорнутий дефолт), не з'їдає екран. Розкриваєш за потреби.
- **Карет згортання доку** (2.4d) — панель важелів згортається кліком по хедеру доку → чистий контекст-скрін; док внизу (thumb-zone), не накриває стейдж.
- (обидва вже в `wsd_TODO_running.md §HARNESS-ШАБЛОН — розширити при канон-сесії)

**Уроки-фікси harness v1→v3 (для протоколу):**
- Лупа через `transform:scale()` → контент вилазить за контейнер, малюється поверх сусідів (overlap-баг). Магніф-режим — НЕ голий scale; або окремий контейнер з `overflow`, або нативно більший px. (v1 фейл.)
- Прес у harness — **JS `.pressing`** (A67), НЕ `:active` (на iOS ненадійний; юзер бачив «рамку» = tap-highlight, а не scale). + глоб `-webkit-tap-highlight-color:transparent`.
- Важелі ВНИЗУ (2.4 thumb-zone), стейдж зверху — інакше не видно зміну при драгу.

---

## 4. IMPL-ЧЕКЛІСТ (наступний чат — HTML першим, 1.5; VBA не треба, ім'я display-only)
1. `.avatar` → Сіблінг-рецепт §1.1 (звірити: `.avatar` лише в пілюлі; dark-твін `@media` A69 + `[data-theme]`).
2. `srNm.textContent=fmtSrName(nm)` + хелпер §1.2 (обидва місця рендеру хедера).
3. sr-pill `transition:transform .1s` (є `:active .96`); chevron rotate + `.open` тогл на open/close sh-sr.
4. `.goto-btn` → grounded §1.4 + JS `.pressing` A67 (down 80/return spring 280; делегація на постійний вузол, `:active` прибрати).
5. `.empty-hint` → `max-width:<lock>px;text-wrap:balance` (§2) + **прибрати `<br>` ×3**.
6. `hint` колір §1.5 (per-theme).
7. `APP_BUILD` +rev (10.6); гейт node --check + tag-balance + grep 0-хардкодів.
8. device XS+15Pro обидві теми → **аж тоді canon** (12.9).

---

## 5. ЧЕРГА ПІСЛЯ sr-pill impl
freshness (`EXPORT_DATE`→вік→`--ok/warn/late`; пороги ≤30/30-90/>90) → canon-сесія (B54.4 + черга B52-B54.2, v6 TODO-фікс, +harness-standard §3) → A58 (grouped-card SR selector + About-футер, адаптувати не 1:1).
