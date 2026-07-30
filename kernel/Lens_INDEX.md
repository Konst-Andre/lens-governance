> живе доки: назавжди (вічне, wsd 1.8) · **читається ПЕРШИМ у кожній сесії** (wsd 1.1)
> KERNEL v1 · 30.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)

# Lens · INDEX — маршрутизатор бази знань

**Ядро: KERNEL v1 (30.07.2026).** Усі файли §3 «Вічне» мусять нести цей самий штамп у 2-му рядку.
Штамп не збігається → ядро розійшлось між Projects → правити ДО початку роботи ( §3).

> **Що це.** Єдина карта: *яке питання → який файл*. Коштує ~6 KB і скорочує решту читань,
> бо називає адресата задачі одразу, замість «прочитати wsd наосліп і сподіватись».
> Заведено 30.07.2026 (governance-пас, сесія A).
>
> **Правило актуальності.** Послався на файл, якого тут немає → або файл заведено поза
> wsd 1.8, або індекс протух. Правиться в тій самій сесії, не відкладається. *(wsd 1.1, детектор К2.)*

---

## §1 Порядок читання на старті сесії

| # | файл | коли |
|---|---|---|
| 1 | **`Lens_INDEX.md`** | завжди |
| 2 | **останнє самері продукту** | завжди (відкриті питання — зверху) |
| 3 | **`Work_Standard.md`** | завжди, цілком — це протокол |
| 4 | `Lens_iOS_cookbook.md` | точково за індексом, якщо задача торкається iOS/PWA/UI |
| 5 | `<Product>_MASTER_LOCK.md` + релевантні `*_valuesLOCK.md` | якщо торкаємось локнутого компонента |
| 6 | `Work_Standard_HISTORY.md` | **лише** якщо правило посилається на `14.x` і треба контекст |

---

## §2 Чотири ролі — чотири доми (wsd 12.11)

| роль | питання | дім |
|---|---|---|
| **протокол** | *як ми працюємо* | `Work_Standard.md` |
| **патерн** | *як робиться ця річ* | `Lens_iOS_cookbook.md` (том за темою) |
| **значення** | *які саме числа* | `*_valuesLOCK.md` · `*_MASTER_LOCK.md` |
| **код** | *дай робочий фрагмент* | донор-модуль `Lens_module_*` |

Не влізло в жодну → **метод роботи** = власний маніфест · **чужий ефект** = `Lens_fx_candidates.md` ·
**канон-ціль зайнята** = відповідний `*_delta_running.md`.

---

## §3 Вічне — канон

### Протокол
| файл | що в ньому |
|---|---|
| `Work_Standard.md` | правила роботи. Кластери 1–13 + форма запису К1/К2 |
| `Work_Standard_HISTORY.md` | changelog усіх версій + Кластер 14 «Прецеденти» (14.1–14.21) + Кластер 15 |

### Патерни
| файл | що в ньому |
|---|---|
| `Lens_iOS_cookbook.md` | A1–A72 універсальні iOS/PWA/UI патерни + Частина B продукт-специфічне + Частина C deploy-чек-ліст |

### Методи роботи (не код продукту)
| файл | що в ньому |
|---|---|
| `Lens_stagebench_manifest.md` | стенди: bench / harness / компер — рецепт і еталони |
| `Lens_sandbox_manifest.md` | пісочниця: копія білда із синтетичними даними, 7 кроків |
| `Lens_fx_candidates.md` | реєстр **зовнішніх** ефектів (FX-1 Border Beam · FX-2 Liquid metal · FX-3 Thinking orbs) |
| `Lens_PROFILE.md` | робочий профіль оператора: стиль пояснень, віджети, зворотний зв'язок |
| `Lens_NEWPROJECT_bootstrap.md` | рецепт заведення нового Project із тим самим ядром |
| `Lens_PROJECT_instruction.md` | готовий текст інструкції Project + що змінилось проти старої |

### Значення — по продуктах
| продукт | файли |
|---|---|
| **StockCheck** | `StockCheck_MASTER_LOCK.md` · `StockCheck_brand_valuesLOCK.md` · `StockCheck_materiality_valuesLOCK.md` · `StockCheck_glyph_valuesLOCK.md` · `StockCheck_tails_valuesLOCK.md` · `StockCheck_money_home_valuesLOCK.md` · `StockCheck_island_glass_FINDINGS.md` · `StockCheck_NETS_register.md` |
| **QR Lens** | `QR_Lens_srpill_valuesLOCK.md` · `QR_Lens_srmotion_valuesLOCK.md` · `QR_Lens_probrow_PARAMS_LOCK.md` · `QR_Lens_statusgauge_BENCHLOCK.md` · `QR_Lens_CTA_mechanic_LOCK.md` · `QR_Lens_export_contract_v1.md` |
| **Фармастор** *(попередня назва StockCheck)* | `Фармастор_v2_MASTER_LOCK.md` · `Фармастор_history_badge_valuesLOCK.md` · `Фармастор_v2_PORT_REGISTER.md` |
| **Drive Lens** | `Drive_Lens_concept_v1_3.md` · `Drive_Lens_logic_audit_findings.md` |

### Код і інструменти
| файл | що це |
|---|---|
| `StockCheck_maint_jsdom_matrix.js` | jsdom-матриця блоку «Обслуговування», 61 твердження |
| `StockCheck_b27_jsdom_matrix.js` | jsdom-матриця b27 (CTA sweep + тост), 34 твердження |
| `StockCheck_icon_gen.py` | генератор іконок PWA з локнутого гліфа |
| `Lens_validate.py` | гейт-скрипт: `--gov` (G1–G6 governance) · `--html <file>` (H1–H4 білд) |

---

## §4 Буфери — статус

| буфер | канон-ціль | стан |
|---|---|---|
| `Lens_cookbook_delta_running.md` | Cookbook | 🟡 2 записи (A73/A75 cand.) |
| `Lens_stagebench_delta_running.md` | `Lens_stagebench_manifest.md` | 🟡 4 записи (додано Д-В з b27 §2) |
| `wsd_delta_running.md` | `Work_Standard.md` | 🟡 3 записи (4 відкриті кандидати + Д-1) |

**Правило:** буфер — не архів. Лежить довше 2–3 сесій → мерджити як є.

---

## §5 Живі білди

| продукт | білд | стан |
|---|---|---|
| **StockCheck** | `StockCheck_port_b27.html` — v2.16.0 · b27 | 🟢 device✓, проєкт зафіксовано |
| **QR Lens** | `QR_Lens_preview_batch58_2.html` | 🟡 відкрита черга Phase 3 |
| **KPI Lens** | `KPI_Lens_v2_preview_batch15_2.html` | 🟡 VBA/PQ у черзі |
| **Drive Lens** | — | 🟡 Tab-3 / Tab-4 відкриті |

Плани продуктів: `QR_Lens_forward_plan.md` *(колишній `wsd_TODO_running.md`)*.

---

## §6 Що зараз у роботі

**Governance-пас** (з `StockCheck_session_summary_b27.md` §11):

| сесія | зміст | стан |
|---|---|---|
| **A** | виселення історії з wsd · `Lens_INDEX` · `Lens_PROFILE` · `wsd_delta_running` · розділ TODO | ✅ 30.07.2026 |
| B | Cookbook → тематичні томи + `Lens_cookbook_INDEX.md`; розібрати cookbook-буфер тим самим проходом | ⬜ |
| C | прополка wsd за К1/К2 · злиття дублів 12.x/13.x | ⬜ |
| D | `Lens_matrix_INDEX.md` + `Lens_jsdom_boot.js` + `Lens_module_maint_v1` + A-запис на handoff-sweep | ⬜ |
| E | чистка теки за wsd 1.8 · мердж stagebench-буфера · MASTER_LOCK refresh | ⬜ |

---

## §7 Некласифіковане — розібрати в сесії E

Файли, що лежать у теці, але не мають дому за wsd 12.11. Кожен → або в дім, або в архів.

| файл | ймовірний дім |
|---|---|
| `KONST_MEMORY_FINAL.md` | **перевірити на дублювання з `Lens_PROFILE.md`** → злити або в архів |
| `Equipment_name_.md` | значення QR Lens → у `QR_Lens_*_LOCK` або архів |
| `StockCheck_collapse_C_CANON_delta.md` | буфер, ціль = Cookbook → мерджити в сесії B |
| `canon_delta_A45_material_lever_manifest.md` | буфер, ціль = Cookbook A45 → сесії B |
| `wsd_TODO_delta_collapsible-cat-levers.md` | буфер → злити у `wsd_delta_running.md` |
| `QR_Lens_bannerJank_external_brief.md` | одноразове (закрито) → архів |
| `KPI_Lens_categories_Excel_impl_Batch15.md` | одноразове → архів |
| `Drive_Lens_concept_v1.md` · `_v1_2.md` | витіснені `_v1_3` → архів |
| `VTM_Lens_foundation_spec_v0_3.md` · `VTM_Lens_deep-research-report_GPT.md` · `Аналіз_Дизайну_ВТМ_Lens_Gemini__3_6.md` | **VTM Lens** — п'ятий продукт, ще не заведений; свій Project |

**Детектор (К2):** `python3 Lens_validate.py --gov .` → гейт G3 валить кожен .md,
не названий у цьому файлі. Секція §7 — легальний дім для «ще не розібраного»,
але вона мусить порожніти, а не рости.
