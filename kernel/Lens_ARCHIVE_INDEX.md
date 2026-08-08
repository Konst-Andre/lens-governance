> живе доки: назавжди (вічне, wsd 1.8)
> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens

# Lens · ARCHIVE INDEX — що лежить в архіві й коли туди йти

> **Навіщо.** Архів фізично лежить у репо (`archive/`), **поза** project knowledge —
> інакше він з'їдає ліміт Project. Але те, чого немає в project knowledge, Claude **не бачить
> і не може шукати**. Цей файл — міст: він **лишається в Project**, коштує кілька KB
> і називає вміст архіву. Claude читає індекс локально, а сам файл тягне з мережі
> тільки коли він справді потрібен.
>
> **Без цього файлу архівація = видалення.** З ним — відкладене зберігання.

**Raw-база архіву:**
```
https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/archive/<тека>/<файл>
```

---

## §1 Коли Claude звертається до архіву — САМ, без нагадування

| тригер | що робити |
|---|---|
| «як ми робили X», «ми це вже вирішували», «колись було» — і в **живих** файлах відповіді немає | шукати по цьому індексу → `curl` потрібного файлу |
| будую **стенд** для компонента, у якого стенд уже був | взяти попередній як базу — важелі й уроки вже знайдені, не винаходити заново |
| канон посилається на самері, якого **немає** в Project (напр. «b26_1 §4») | дістати те самері з архіву |
| **регресія**: працювало раніше — зламалось | знайти батч, де воно було device✓, і звірити |
| стартує **новий продукт** | знайти найближчий аналог серед стендів і концептів |

**Коли НЕ звертатись:** штатний старт сесії · планування нової фічі з нуля ·
будь-що, на що відповідають живі файли. Архів — не джерело правди, а **свідчення**.
При суперечності живий файл виграє завжди.

---

## §2 Структура тек

```
archive/
  summaries/    самері, старші за 2 останніх на продукт (плоско, без підтек)
  stands/       стенди: bench · harness · компер (закриті) + витіснені білди
  superseded/   витіснене іншим файлом: концепти, буфери, разові брифи
```

---

> ⚠ **Виправлено 01.08.2026:** до цієї дати §2 оголошував теки `benches/ builds/
> concepts/ misc/` і підтеки `summaries/<Product>/`, яких у репо **немає**. Розбіжність
> між оголошенням і фактом ламає саме той сценарій, заради якого існує цей файл:
> Claude будував `raw`-URL за оголошеною текою й отримував 404 (wsd 1.10).
> **Правило:** структура тут звіряється з деревом репо, а не описується з наміру.

## §3 Правило заповнення

**Рядок в індекс пишеться ОДНОЧАСНО з переміщенням файлу.** Не «потім розберу».

Формат рядка: `файл · дата · продукт · що всередині (одна фраза) · чому заархівовано`

**Детектор (К2):** файл в `archive/` без рядка тут = **втрачений**, бо знайти його
можна лише випадково. Перевірка — звірити кількість файлів у теці з кількістю рядків
у відповідній секції нижче.

**Чого в архів НЕ класти:** нічого, на що посилається живий канон-файл.
Якщо wsd або Cookbook посилається на документ — він лишається в Project.

---

## §4 Реєстр — це «Перепис архіву» нижче

> ⚠ **Виправлено 01.08.2026 (сесія F).** Тут стояв ДРУГИЙ, порожній реєстр
> із підзаголовками `benches/ builds/ concepts/ misc/` — тек, яких у репо немає
> (той самий дефект, що вже виправлявся в §2, але залишений у §4).
> Два реєстри одного архіву — режим провалу «дублі з різним формулюванням»:
> незрозуміло, який головний. Єдиний реєстр — **Перепис архіву** нижче.

---

## Перепис архіву · завантажено 31.07.2026 (governance-сесія B/C)

**Як Claude це читає** — живим запитом, без завантаження в Project:

```
https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/archive/<тека>/<файл>
```

Перевірено сьогодні на `kernel/` — 200 по всіх 12 файлах. Репо публічний,
авторизації немає, тож обмеження одне: **точне ім'я файлу мусить бути тут**.
Немає в цьому переписі → я його не знайду.

**Правило.** Перед тим як сказати «цього файлу не існує» — подивитись сюди.
Файл, виселений із Project, не мертвий: він переїхав (`Lens_INDEX.md` §8).

### `archive/` — корінь

- `Lens_iOS_cookbook.md` — моноліт Cookbook, 227 KB, 78 записів. Розпиляно
  на 5 томів у сесії B; нумерація A-записів наскрізна й НЕ мінялась,
  тому старі посилання «Cookbook A45» дійсні для томів. Піднімати лише
  для археології (звірка, чи щось загубилось при розпилі).

### `archive/summaries/` — 63 файли

- `Lens_session_summary_governance_A.md`
- `Lens_session_summary_governance_B.md`
- `Lens_session_summary_governance_C.md`
- `Lens_session_summary_governance_D.md`
- `QR_Lens_session_summary_A58_harness_v1.md`
- `QR_Lens_session_summary_A58_portplan_LOCK.md`
- `QR_Lens_session_summary_A58motion_persist_PLAN.md`
- `QR_Lens_session_summary_B58_B58_2.md`
- `QR_Lens_session_summary_T2harness_v3.md`
- `QR_Lens_session_summary_srmotion_LOCK_B58plan.md`
- `QR_Lens_session_summary_srpill_LOCK.md`
- `QR_Lens_session_summary_srpill_implPLAN.md`
- `StockCheck_session_summary_Node2_1_maintBench.md`
- `StockCheck_session_summary_H3_7_stagebench_v3.md` *(лежало в архіві, в індексі названо не було — виправлено 08.08.2026)*
- `StockCheck_session_summary_H3_8_b5_channels.md` *(те саме)*
- `StockCheck_session_summary_H4_0_b32_0_PLAN.md` — розтин порту, закриття О-20, Р-28…Р-32
- `StockCheck_session_summary_H4_1_b32_0_BASELINE.md` — мікроскоп плану (7 дефектів) + BASELINE b31
- `StockCheck_session_summary_H4_2_b32_0_PATCH.md` — збірка b32.0 «шов», device✓ 08.08.2026; витіснено `H5_0_O20_stand_PLAN` (§0 і §7 перенесено туди повністю, канон уже змерджено)
- `StockCheck_session_summary_b16_materialPort.md`
- `StockCheck_session_summary_b17_collapseC.md`
- `StockCheck_session_summary_b18_collapseShip_canonMerge.md`
- `StockCheck_session_summary_b19_tails_LOCK.md`
- `StockCheck_session_summary_b22_anchoredTile.md`
- `StockCheck_session_summary_b23.md`
- `StockCheck_session_summary_b24_dpickerPort.md`
- `StockCheck_session_summary_b25_PWA.md`
- `StockCheck_session_summary_bench_v1_device.md`
- `StockCheck_session_summary_bench_v2_materialLOCK.md`
- `StockCheck_session_summary_dpicker_LOCK.md`
- `StockCheck_session_summary_headbench_v7.md`
- `StockCheck_session_summary_islandHarness_v2.md`
- `StockCheck_session_summary_islandPort_Stage1.md`
- `StockCheck_session_summary_money_home_PORT.md`
- `Фармастор_session_summary_v1_3.md`
- `Фармастор_session_summary_v2_REBUILD_brief.md`
- `Фармастор_session_summary_v2_STEP1_shell_HANDOFF.md`
- `Фармастор_session_summary_v2_STEP1_structure_LOCK.md`
- `Фармастор_session_summary_v2_STEP2_FILLharness.md`
- `Фармастор_session_summary_v2_STEP2_multibrand_DONE_labels_ideation.md`
- `Фармастор_session_summary_v2_STEP2_v6_LOCK_relabel_multibrand_plan.md`
- `Фармастор_session_summary_v2_b10_ctaDesign_dynMetric.md`
- `Фармастор_session_summary_v2_b10_ship_b11plan.md`
- `Фармастор_session_summary_v2_b11_materialLOCK.md`
- `Фармастор_session_summary_v2_b12.md`
- `Фармастор_session_summary_v2_b13_2_materialfix.md`
- `Фармастор_session_summary_v2_b13_dynamikaCore_s54.md`
- `Фармастор_session_summary_v2_b14_historyBadge_A3ring_canonMerge.md`
- `Фармастор_session_summary_v2_b14_historyBadge_harnessLOCK.md`
- `Фармастор_session_summary_v2_b5_motion_harness.md`
- `Фармастор_session_summary_v2_b6_motion_port.md`
- `Фармастор_session_summary_v2_b7_Node6_HomeHarness.md`
- `Фармастор_session_summary_v2_b7_Node7_HomeCard_LOCK.md`
- `Фармастор_session_summary_v2_b8_Node5_arcLOCK.md`
- `Фармастор_session_summary_v2_b9_arcPort_Node8_exportDyn.md`
- `Фармастор_session_summary_v2_colorLOCK_MASTERLOCK.md`
- `Фармастор_session_summary_v2_dynamika_colheaddim_v6.md`
- `Фармастор_session_summary_v2_dynamika_deltacolorB_b13handoff.md`
- `Фармастор_session_summary_v2_dynamika_harnessLOCK.md`
- `Фармастор_session_summary_v2_dynamika_v4_LOCK.md`
- `Фармастор_session_summary_v2_dynamika_v8_Glock_stickyfix.md`
- `Фармастор_session_summary_v2_planning_LOCK.md`
- `Фармастор_session_summary_v2_shell_b3_PORThandoff.md`
- `Фармастор_session_summary_v2_statusfilter_colhead.md`

### `archive/stands/` — 22 файлів

- `Dinamika_colhead_bench_v2.html`
- `Farmastor_arc_anim_harness_v1.html`
- `Farmastor_dynamika_colheaddim_v8.html`
- `Farmastor_dynamika_deltacolor_harness_v1.html`
- `Farmastor_dynamika_harness_v3.html`
- `Farmastor_dynamika_harness_v4_3.html`
- `Farmastor_fillcta_compare_v3.html`
- `Farmastor_filltail_harness_v1.html`
- `Farmastor_history_badge_harness_v2.html`
- `Farmastor_material_bench_v2.html`
- `Farmastor_motion_harness_collapse_glow_v2.html`
- `Farmastor_multibrand_harness_v1.html`
- `Farmastor_status_filter_harness_v2.html`
- `Farmastor_toparea_harness_v4.html`
- `QR_Lens_brand_harness_v6.html`
- `StockCheck_dpicker_stagebench_v2_3.html`
- `StockCheck_glyph_stagebench_v1.html`
- `StockCheck_headbench_v1.html`
- `StockCheck_island_harness_v2.html`
- `StockCheck_maint_stagebench_v3.html`
- `StockCheck_materiality_stagebench_v1.html`
- `StockCheck_materiality_stagebench_v2.html`
- `StockCheck_ctareward_bench_v3.html` — 🗄 01.08.2026. Стенд вибору **характеру нагороди** на 📋 (кандидати C/E). Результат канонізовано: Cookbook **A82**. Йти сюди при виборі нагороди для будь-якої «віддавальної» дії — важелі вже знайдені (v1/v2 застарілі, не тягнути)

### `archive/superseded/` — 5 файлів

- `Drive_Lens_concept_v1.md`
- `Drive_Lens_concept_v1_2.md`
- `KPI_Lens_categories_Excel_impl_Batch15.md`
- `farmastor_v2_data.js`
- `canon_delta_A45_material_lever_manifest.md` — 🗄 01.08.2026. Буфер **пережив ціль**: A45 канонізовано в `Lens_iOS_cookbook_3_material.md`. Йти сюди тільки за **сирими важелями компера** матеріальності, яких канон не зберіг
- `StockCheck_collapse_C_CANON_delta.md` — 🗄 01.08.2026. Те саме: ціль A72 у `Lens_iOS_cookbook_5_motion.md`

**Разом: 81 файлів.**
