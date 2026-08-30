# Фармастор v2 — session summary · b12 (polish: material · захист · смуга · прес + MASTER_LOCK merge)

**Продукт:** Фармастор замовлення v2 (standalone, NOT Lens — техн-патерни iOS/PWA застосовні)
**Файл b12:** `Фармастор_замовлення_v2_port_b12_3.html` — БАЗА (outputs цього чату)
**Версія:** `APP_BUILD = { ver:'v2.4.0', build:'polish.b12_3', date:'17.07.2026' }`
**Дата:** 17.07.2026 · device-verified (Konst XS+Pro, обидві теми)

---

## 1 · ЗРОБЛЕНО у b12 (b12 → b12_3, усі device✓)

**Мікро-блок (3 помічені моменти + прес):**
1. **Container material (#1в+#2)** — `.icon-btn` (back+•••) і `.mi-ic` (меню) отримали material presence, обидві теми + auto-dark мірори. Через compare `Farmastor_container_material_compare_v1.html` (Konst-pick). Корінь: світлі контейнери тонули (A66 — світлу елевацію дає hairline+drop, НЕ світліша заливка).
   - Світла: fill `color-mix(in srgb,#fff 55%,<backdrop>)` (icon-btn=`--bg` · mi-ic=`--surface-3`); border `1px solid rgba(20,50,42,.12)`; drop `0 1.4px 3.6px rgba(20,50,42,.081)`.
   - Темна: fill `color-mix(in srgb,#fff 6%,var(--surface-3))`; border-color `rgba(255,255,255,.045)`; ridge `inset 0 1px 0 rgba(255,255,255,.096)` (без drop — A45).
2. **Back = Контейнер (#1а)** — уніфіковано під `.icon-btn` (пара з «•••»), текстова `‹` → SVG-шеврон (штрих як `.mi-chev`). Мертве `.icon-btn.ghost` знято (wsd 3.7).
3. **Захист від нативних iOS-взаємодій (#2)** — глобально `*{…user-select:none;-webkit-touch-callout:none}` + виняток `input,textarea,[contenteditable]` (пошук `#q` + комірки `.fld-in` редаговані). Zoom вже глушив viewport.
4. **Нижня смуга-банди (#3) — RESOLVED.** Корінь: `.sheet box-shadow:0 -8px 30px` при ЗАКРИТОМУ шіті (`translateY(100%)`, край під viewport) кидав тінь ВГОРУ в низ екрана; 3 закриті шіти → банди на всіх екранах, тема/меню-незалежно. **Фікс:** тінь лише на `.sheet.on`. ⚠️ **A55 був хибним первинним діагнозом** (device спростував) — але лишили як захист під installed-PWA (bg-matched, безпечно; Konst-keep).
5. **Прес рядків меню (A67):** (a) Excel-рядок був єдиний `.mi` без `.pressable` → допаровано (b12_2, усі 4 тапабельні натискаються). (b) **Вдавлення (b12_3):** `.mi.is-pressed` тепер tint **+** `transform:scale(.98)` (обраність + сідання-в-себе, як QR-картка), transition `.12s` повернення = «вага пальця». Реюз делегованого A67-хендлера, нуль нового JS. Device✓ «саме так».

**MASTER_LOCK merge (HIGH — DONE):** `Фармастор_v2_MASTER_LOCK.md` оновлено (283→389 р.):
- §4 ← повний §4-update (Copy-контракт + Excel deep-link + material LOCK + CSV-split) замість bulk-export.
- §6 — додано відсутній батьківський заголовок (§8-рефи більше не висять).
- §10 (НОВИЙ) — усі b11–b12 локи: меню A58 static-DOM · seg-motion 500/1.80 · confirmAction A59 · прес A67 split+`.mi` scale/tint · container material · захист · A55 · sheet-shadow-on-`.on`.

---

## 2 · КАНОНІЧНІ ЗНАЧЕННЯ b12 (у коді ✓ + у MASTER_LOCK §10 ✓)

- **Container material:** див. §1.1 вище / MASTER_LOCK §10.5 (compare-важелі Lfill55/Lbord55/Ldrop45/Linset0 · Dlift42/Dridge60/Dbord45).
- **Прес `.mi`:** `scale(.98)` + bg-tint `color-mix(surface-3, text 5%)` (device✓). Магнітуда-драбина: `.icon-btn .88` · `.card .985` · `.mi .98` · `.btn-copy .96` · `.btn-form .92`.
- **Sheet-shadow:** тільки `.sheet.on` (не на базовому `.sheet`).
- **A55:** `html{min-height:calc(100% + env(safe-area-inset-top))}` (захисний, keep).

---

## 3 · ЩО НЕ ЗРОБЛЕНО / ВІДКРИТЕ

**Governance-прибирання (дешеве):**
- `MASTER_LOCK__4_update_b11.md` — **влитий у master → можна ВИДАЛИТИ** з проєкту. Замінити master-файл у проєкті версією з outputs.

**MEDIUM — §5.1 Динаміка UI** (наступна велика фіча): дата-контракт locked (`visits[]` снапшоти §1). UI design pending. **Harness-first, mock-фікстури з edge-cases (НЕ реальні дані).** Реюз FILL-акордеона; Δ-колір за дистанцією до норми (НЕ напрямом); absent→«—»; шапка-вердикт (↑N краще · ↓N гірше · =N без змін + одне слово).

**MEDIUM — canon-merge (governance-чат):** Cookbook дельти: A54 (+seg 500/1.80, 3-сегм), A58 (+static-DOM для фіксованого меню), A66/A45 (+container material presence), A67 (+прес-split, +`.mi` scale.98/tint для list-рядків). wsd борги з попередніх сесій.

**LOW:** дуга-кільце анімація (harness-first) · eyebrow-indent підрівняти (16px vs контент ~25px) · container tint-сила (device ок).

**PENDING device (не блокери):** confirm-модал deep-look · CSV-single у Excel · UL/share iOS.

---

## 4 · ФАЙЛИ

**Поточні:**
- `Фармастор_замовлення_v2_port_b12_3.html` — БАЗА (усе b12).
- `Фармастор_v2_MASTER_LOCK.md` — master (МЕРЖ ГОТОВИЙ, замінити у проєкті).
- `Farmastor_container_material_compare_v1.html` — compare контейнерів (RESERVED-реф).
- `Work_Standard.md` / `Lens_iOS_cookbook.md` — governance.

**Видалити з проєкту:** `MASTER_LOCK__4_update_b11.md` (влитий).
**Legacy:** `..._port_b11.html`, `_b12`, `_b12_1`, `_b12_2` (замінено b12_3).

---

## 5 · УРОКИ

- **Хибний перший діагноз — device спростовує (wsd 1.5 арбітр).** A55 був правдоподібним, але НЕ полагодив нижню смугу; реальний корінь — тінь ЗАКРИТОГО шіта тече вгору в низ viewport. **Декоративні тіні гейтити на open-стан** (`.on`), інакше off-screen-елемент світить у екран.
- **Light container presence = A66:** hairline + реальний drop, НЕ світліша заливка (біле на майже-білому не читається). Compare підтвердив.
- **Прес list-рядків:** широкий рядок МОЖЕ брати м'який `scale(.98)` + tint разом («обраність + вдавлення»), не лише tint. Реюз делегованого A67 — нуль нового JS.
- **grep live-code знайшов справжню діру** (Excel-рядок без `.pressable`) — самері б це не показало (wsd 12.1).
- **color-mix токен-driven** — тримає material re-theme-safe (мережа-агностичність §0).

---

## 6 · Перехід у новий чат — стартове повідомлення

```
Перед будь-якими діями з кодом/PQ/VBA/патчами — прочитай (wsd 1.1) ЛИШЕ вказані розділи (берегти контекст; зайве не читати — прочитаєш пізніше сам):

1. Work_Standard.md — Кластер 1 (протокол+маркер 1.2) · Кластер 2.4 (compare-preview) · Кластер 10 (валідація) · Кластер 11 (патч-структура). Решту НЕ читати.
2. Lens_iOS_cookbook.md — A48 (eyebrow/акордеон sticky) · A45/A66 (material presence) · A70 (stroke-dashoffset для дуги, якщо торкнемось) · A35 (кольори станів). Решту НЕ читати.
3. Фармастор_v2_MASTER_LOCK.md (ОНОВЛЕНИЙ, single-source — §4-update ВЛИТИЙ) — §1 (дата-модель visits[]) · §5.1 (Динаміка-контракт) · §5.2/§6.4 (Home-картка, реюз) · §3 (norm-resolver для Δ-до-норми) · §6 (токени) · §10 (b11–b12 polish локи).
4. Фармастор_session_summary_v2_b12.md — ПОВНИЙ стан b12 + locked-значення + PENDING.
5. База: Фармастор_замовлення_v2_port_b12_3.html

Маркер навантаження — останнім рядком КОЖНОЇ відповіді (wsd 1.2), дублювати в ask_user_input_v0 (question, «(💬 ~N%)»).
Working-копію — у /mnt/user-data/outputs по ходу (wsd 1.6).

Стан: b12 завершено (container material + захист + нижня-смуга-фікс + прес-вдавлення), device-verified. MASTER_LOCK влитий (можна видалити MASTER_LOCK__4_update_b11.md з проєкту).

НАСТУПНИЙ КРОК (MEDIUM, велика фіча):
§5.1 ЕКРАН ПОРІВНЯННЯ (Динаміка залишків) — harness-first, mock-фікстури з edge-cases (НЕ реальні дані; mock з крафтовими кейсами > реальні для побудови/device-тесту). Контракт (MASTER_LOCK §5.1 + §1):
• Вхід: Home-картка «Динаміка» (visits≥2), per-аптека, два знімки «від/до» (дефолт — останні 2 transferred).
• Розкладка: реюз FILL-акордеона (бренд/під-група, sticky eyebrow A48). Рядок: SKU · дата-від · дата-до · Δ. Тумблер «тільки зміни». Сорт master-order + опція «за рухом».
• Кодування Δ (крук): колір за ДИСТАНЦІЄЮ до норми, НЕ за напрямом (зблизився=ok/accent · віддалився=warn→crit · стоїть=muted) + видиме сире число.
• Absent-чесність: present в одному / absent в іншому → «—», не фейкова Δ.
• Шапка-вердикт: ↑N краще · ↓N гірше · =N без змін + одне слово («Загалом: погіршилось»).

ПРАВИЛА: подвійне пояснення тех.рішень · без емодзі в UI (SVG/моно) · harness-first для eye/motion · план→підтвердж→код · маркер останнім рядком · валідація перед delivery (node --check · tag-balance · grep-anchors · absent≠0 · diff-scope) · грепати live-code (wsd 12.1), не довіряти самері понад код.
```
