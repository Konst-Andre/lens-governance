# StockCheck — Session Summary · Money-Home (ПОРТ ЗАКРИТО)

**Статус:** money-home **device-verified OK** у продукті. Живий білд = **`StockCheck_port_b21.html`**.
**Ключове усвідомлення сесії:** StockCheck = ребренд+еволюція Фармастора (та сама тека, НЕ окремий проєкт; «бекпорт» — хибна посилка). Пам'ять #23 оновлено.

---

## §РІШЕННЯ (що зроблено)

**Нова фіча — money-home:** показ грошового розриву vs MSL на філ-екрані.
- **Арифметика (реальна, in-app):** `order = MSL_ярус − залишок(введений)` · `money = order × p` (Custom.Price, поле `p` у `MSL[]`). Категорія₴ = Σ по OTC/IW; бренд₴ = Σ по бренду.
- **Знак:** `+` = треба дозамовити / можемо продати · `−` = overstock (перезатарено, не продамо).
- **КРИТИЧНА ЛОГІКА (фікс b20→b21):** рахуємо **ЛИШЕ введені SKU** (`data[k]!==undefined`). Невведені не рахуються; дім категорії/бренду **прихований** (`.money.empty`), поки в scope немає жодного введення. Цифра набігає, поки реп відмічає полицю — як в онлайн-Excel (N=MSL−Залишок, O=N×Price).
- **Дві родини:** A = бейдж-дім (біля OTC/IW угорі) · B = акордеон-дім (у хедері бренду; бейджа НЕ треба — бренд каже категорію).
- **Скоуп** = Бренд (locked-дефолт; sub/both лишились опціями харнеса, у продукт НЕ тягнув).
- **Матеріал/значення** — див. `StockCheck_money_home_valuesLOCK.md` (full·semantic·pill·12·700; A45 per-theme; gap A6/B2; слот лічильника 56px → дім вирівняно; грн; overstock=мінус). Device-locked XS+15Pro, обидві теми.

**Процес (для історії):** харнес v1 (чернетка, порушив маніфести) → **stagebench v2** (правильний, per manifest) → **valuesLOCK.md** → порт **b20** → логіка-фікс **b21**.

**Порт-хуки в b21 (де живе фіча):** CSS `.money/.pair/.prow/.bright` (після `.tchip` dark) · хедер реструктуризовано (пари бейдж+гроші / прогрес у `.prow`) · `brandCard` інжектить `.bright{money,bcnt}` · helpers `brandMoney/catMoney/setMoney/updHeadMoney/updBrandMoney` (після `IW_BRANDS`) · хуки в `updProg` (хедер) + `refreshCounters` (бренд).

---

## §ПАРКІНГ — актуалізації (наступна сесія, ПЕРШИМ)
1. **Rename-чистка:** StockCheck=Фармастор по всіх файлах, де стара назва / плутанина двох проєктів.
2. **wsd-гард:** «перед будь-яким bench/harness — читати `Lens_stagebench_manifest` + A45 ПЕРШИМ» (корінь моєї помилки цієї сесії).
3. **stagebench-маніфест:** додати обов'язкові **стейдж-зум +/−** та чіткий **hide-panel** (Konst не міг наблизити контент; ручний зум ламав сторінку).
4. **PORT_REGISTER / MASTER_LOCK:** внести money-home (DONE b21) + посилання на valuesLOCK.
5. **Опція:** сума на під-секціях у продукті (зараз лише Бренд-скоуп).

## §ЧЕРГА — дизайн (не чіпали)
- **Острівець** — anchored unique-tile (квадратити верхні кути, §5-B не чіпати), судити ТІЛЬКИ на девайсі.
- **Дуга/винагорода** — motion hole #1. NB: у b19+ вже є `fireReward` (glow/wash+ring+pop+collapse на brand-done) — перевірити, чи «схована винагорода» (arc на home-картці після copy→Перенесені) ще відкрита, чи закрита цим.
- netBtn toast «кнопка на майбутнє».

---

## §ПАПЕРИ (дельта сесії)
- **`StockCheck_port_b21.html`** — живий білд, device-verified ← головний
- **`StockCheck_money_home_valuesLOCK.md`** — канон значень money-home
- `StockCheck_money_home_stagebench_v2.html` — стенд (референс-якість, per manifest)
- (superseded: b20, harness_v1)

## §READ-ЕКОНОМІЯ (наступний чат)
1. **ЦЕЙ самері** — першим (§РІШЕННЯ + §ПАРКІНГ + §ЧЕРГА)
2. `StockCheck_money_home_valuesLOCK.md` — значення money-home
3. `StockCheck_port_b21.html` — живий білд (grep: `.money` / `moneyOtc` / `brandMoney` / `updHeadMoney` / `.bright`)
4. `Lens_stagebench_manifest.md` + `canon_delta_A45_material_lever_manifest.md` — ПЕРЕД будь-яким новим bench (урок сесії)
5. `Фармастор_v2_PORT_REGISTER.md` + `Фармастор_v2_MASTER_LOCK.md` — реєстр/черга
6. `Lens_iOS_cookbook.md` + `Work_Standard.md` — governance

---

## §СТАРТЕР для наступного чату
```
Привіт! StockCheck (= ребренд Фармастора, та сама тека — НЕ окремий проєкт).
Money-home ЗАКРИТО й device-verified. Живий білд: StockCheck_port_b21.html.

Read-економія (по порядку):
1. StockCheck_session_summary_money_home_PORT.md — ПЕРШИМ (§РІШЕННЯ+§ПАРКІНГ+§ЧЕРГА)
2. StockCheck_money_home_valuesLOCK.md — значення money-home
3. StockCheck_port_b21.html — живий білд (grep .money/moneyOtc/brandMoney/.bright)
4. Lens_stagebench_manifest.md + canon_delta_A45_material_lever_manifest.md — ПЕРЕД будь-яким bench
5. Фармастор_v2_PORT_REGISTER.md + Фармастор_v2_MASTER_LOCK.md
6. Lens_iOS_cookbook.md + Work_Standard.md

ЗАДАЧА (обери): АКТУАЛІЗАЦІЇ (паркінг) — rename StockCheck=Фармастор по файлах ·
wsd-гард «читати stagebench+A45 перед bench» · stagebench-маніфест +/−зум+hide-panel ·
PORT_REGISTER+MASTER_LOCK внести money-home. АБО ДИЗАЙН-ЧЕРГА — острівець
(anchored-tile, тільки девайс) · дуга/винагорода motion hole #1 (звірити з fireReward b19+).

Правила: HTML+CSS патч першим тоді JS · plan→confirm→code · обидві теми ·
node --check+tag-balance+grep-anchor+diff-scope · маркер навантаження в КІНЦІ кожної
відповіді (wsd 1.2) + дубль у ask_user_input_v0 · двійне пояснення для нового/несподіваного ·
working-копії в outputs по ходу. Перед bench/harness — читати stagebench-маніфест+A45.
```
