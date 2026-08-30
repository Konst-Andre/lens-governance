# Фармастор v2 — session summary · b6 motion port (13.07.2026)

## Що зроблено цієї сесії

**1. Harness v1 → v2 (полагоджено 5 дефектів).** `Farmastor_motion_harness_collapse_glow_v2.html`:
- **glowSpread double-unit баг** — важіль писав `Npx`, CSS робив `calc(Npx*1px)` = invalid → німб гас після першого драгу. Фікс: raw-важелі (glowSpread, ringW) пишуть UNITLESS, CSS сам множить `*1px`.
- **light glow невидимий** — це не баг, це фізика (німб = темна метафора, A45/A66). Введено **окрему light-reward механіку**: `::before` fill-wash (accent-soft) + inset ring-flash.
- **per-theme важелі (wsd 2.4c)** — активна тема показує свій reward-набір (dark: glow* · light: wash/ring) + спільні.
- **caret-згортання панелі (wsd 2.4d)** — чистий контекст-скрін.
- **frame-gap трійка (wsd 2.4)** — max-gap / dropped>33 / Δbaseline у смужці панелі.

**2. MOTION reward — LOCKED v2 (device✓ dark, bake ×1):**
```
shared:  --collapseDur:700ms; --collapseEase:ease-in-out;
         --popDur:800ms; --popEase:ease-in-out; --popOver:4.5;
dark:    --glowDur:900ms; --glowSpread:16; --glowOp:0.9;      (глоу німб ::after)
light:   --washDur:900ms; --washOp:0.7; --ringW:5; --ringOp:0.9; (wash+ring ::before)
lead-before-collapse: 140ms
```
- frame-gap (харнес): dark max 23ms dropped 0 · light max 18ms dropped 0. **Δ від'ємна — артефакт iOS idle-throttle** (простій ~30fps, рух ~60fps); гейт = max+dropped, не Δ.
- Таст-нотатки (не блокери): `glowOp .9` яскраво (ок для транзиту; фолбек .7) · `ringW 5` жирне (свідома компенсація opacity-конверта wash↔ring; якщо колись треба тонке-різке кільце → decouple v2.1).

**3. Порт motion b5 → b6.** `Фармастор_замовлення_v2_port_b6.html`:
- Ключове відкриття грепу: **b5 згортав `display:block/none`** (миттєво, не анімовно) → конвертовано у **grid-rows** (`.bwrap` 1fr→0fr, transition collapseDur/Ease). `.collapsed` клас замість inline display.
- Reward-псевдо на `.brand`: `::after` glow · `::before` wash+ring (token-adaptive → A69-clean, без dark-mirror). `.bhdr,.bwrap{z-index:1}` — контент над wash-тінтом.
- `fireReward(brand)`: `resolvedTheme()` → dark=glowing / light=washing + popping, collapse@lead140, cleanup@settle. Guard `dataset.rewarding`.
- Тригер: `refreshCounters` коли brand→done (було миттєве `display:none` — стало `fireReward`).
- Ручний `toggleBrand` теж переведено на `.collapsed` (плавно, той самий grid-rows).
- **Валідація:** node --check ✓ (2 блоки) · div-баланс +1/+1 vs b5 · 0 orphan `display`-тоглів · FILL-логіка (onInput/normFor/fillLevel/dchipHtml/copyValues + absent≠0 delete) НЕДОТОРКАНА.
- **Device✓ (dark):** рендер чистий, нічого не поламано; скрін підтвердив тір-чіпи/eyebrow/акордеон/ghost-норми/pack-чіпи.

## b6 — що ще звірити на девайсі (не блокує, підтвердити наступним проходом)
- **Reward-fire:** заповнити останнє поле бренду → pop+німб(dark)/wash(light)+collapse@140. (Скріни показали рендер, не сам reward-момент.)
- **Світла тема** reward (mint wash + ring).
- **XS frame** під час колапсу (layout-prop; харнес dropped 0, звірити на залізі).

## Шлях зафіксовано → онови MASTER_LOCK §9

📌 **Встав цей блок замість поточного §9 у `Фармастор_v2_MASTER_LOCK.md`:**

```markdown
## §9 · ЩО ДАЛІ (upd b6, 13.07.2026)

**Motion reward — LOCKED v2 (device✓ dark, bake ×1):**
- shared: collapseDur 700ms/ease-in-out · popDur 800ms/ease-in-out · popOver 4.5%
- dark (glow німб ::after): glowDur 900ms · glowSpread 16 (unitless) · glowOp 0.9
- light (wash+ring ::before): washDur 900ms · washOp 0.7 · ringW 5 (unitless) · ringOp 0.9
- lead-before-collapse 140ms · collapse = grid-rows 1fr→0fr
- Тригер: brand→done у refreshCounters → fireReward (resolvedTheme гілкує dark/light).
- Харнес-істина: Farmastor_motion_harness_collapse_glow_v2.html (raw-важелі, per-theme, frame-gap).

**Node-черга (порт-план 8 нод; 1-5 FILL злиті у b-серії):**
- ✅ Node 1-5 FILL (b4/b5): поле, ghost-норма, δ-чіп, eyebrow A48, copy-preview.
- ✅ Motion reward port (b6).
- ▶ Node 6 — СТАН v2: visits[] знімки + snapshot-on-copy A1 + міграція v1→v2 (§1). Чиста логіка, беквбон, розблоковує §5.1.
- Node 7 — HOME: 3-станові картки (§5), harness-first вигляд.
- Node 8 — COPY §4: 📋→M{X}, знести xlsx-стек −425 КБ. (Прим.: copyValues by-kode вже є у b5/b6 як preview; xlsx-стек ще не знесений — звірити.)
- Node 5 — ПІКЕР: harness-first рядок (§5) — див. LABELING нижче.
- §5.1 ПОРІВНЯННЯ: після node 6 (дата-контракт вже залочений).

**Ідея-тріаж:**
- 🔜 All-done reward — коли аптека 83/83 (фліпає Home-картку). Наступний harness, поки motion свіжий.
- ⏸ Витягнути акордеон спільним примітивом — ВІДКЛАДЕНО (передчасно, поки FILL не стабільний; Konst).
- 💡 Invariant-тест absent≠0 — named-invariant у валідацію після node 6 (сторож проти val||'' пастки).

**? OPEN-design (harness-first, device-арбітр):** Home-картка (3 стани) · пікер-рядок · §5.1 UI.

**🆕 NODE-5 LABELING (device-surfaced 13.07):** назва аптеки = `[TIER] Місто — Область, м.Місто, вул.X, N` → місто дублюється 2-3×, область баласт. На FILL-хедері ідентифікатор (вулиця) обрізається за «Дніпропетровська обл., м.Дніпро…». Фікс: display-name resolver (зняти область, дедуп місто) → ідентич-лінія ВЕДЕ вулицею, місто тихо/на рівні групи. Пікер: місто=sticky-група (§5 вже планує), рядок=вулиця сильна+Proxima дрібним. FILL-title=вулиця, не область. ⚠️ дата-кейв'ят: назва — один склеєний рядок у xlsx → parse крихко (просп./вул./пров./ТЦ/прим.) АБО почистити джерело на city+addr.
```

## Активні файли
- `Фармастор_замовлення_v2_port_b6.html` — продукт (motion злитий, device✓ dark)
- `Farmastor_motion_harness_collapse_glow_v2.html` — motion-харнес істини (re-tune тут)
- `Фармастор_v2_MASTER_LOCK.md` — джерело правди (онови §9 блоком вище)

---

## 🚀 Стартер для нового чату (копіюй у новий чат)

```
Продовжуємо Фармастор v2. Прочитай перед будь-яким кодом (wsd 1.1):
1. /mnt/project/Work_Standard.md (wsd)
2. /mnt/project/Lens_iOS_cookbook.md (A45/A48/A66/A69)
3. /mnt/project/Фармастор_v2_MASTER_LOCK.md (особливо оновлений §9 — Шлях)
4. Самері: Фармастор_session_summary_v2_b6_motion_port.md (повний стан + node-черга)

Маркер навантаження — останнім рядком КОЖНОЇ відповіді (wsd 1.2),
дублювати в ask_user_input_v0 (поле question). Working-копії → /mnt/user-data/outputs.

СТАН: motion reward LOCKED v2 злито у b6 (Фармастор_замовлення_v2_port_b6.html),
device✓ dark-рендер. Харнес-істина: Farmastor_motion_harness_collapse_glow_v2.html.

ЗВІРИТИ НА ДЕВАЙСІ (не блокує): reward-fire (заповнити останнє поле бренду →
pop+німб/wash+collapse@140) · світла тема reward · XS frame під час колапсу.

ДАЛІ по §9 node-черзі:
  🔜 All-done reward harness (коли 83/83; поки motion-контекст свіжий) — АБО одразу
  ▶ Node 6 — стан v2: visits[] + snapshot-on-copy A1 + міграція v1→v2 (§1).
     Далі Node 7 Home (harness-first), Node 5 пікер (+ NODE-5 LABELING фікс),
     Node 8 copy §4 (знести xlsx-стек), §5.1 порівняння.

Скажу, з чого починаємо. Спершу план (wsd 1.5 plan→confirm→code), без коду до команди.
```
