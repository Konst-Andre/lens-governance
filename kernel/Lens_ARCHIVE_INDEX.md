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
  summaries/<Product>/    самері, старші за 2 останніх на продукт
  benches/                стенди: bench · harness · компер (закриті)
  builds/                 витіснені preview/port HTML
  concepts/               витіснені концепт- і spec-документи
  misc/                   разові брифи, зовнішні звіти
```

---

## §3 Правило заповнення

**Рядок в індекс пишеться ОДНОЧАСНО з переміщенням файлу.** Не «потім розберу».

Формат рядка: `файл · дата · продукт · що всередині (одна фраза) · чому заархівовано`

**Детектор (К2):** файл в `archive/` без рядка тут = **втрачений**, бо знайти його
можна лише випадково. Перевірка — звірити кількість файлів у теці з кількістю рядків
у відповідній секції нижче.

**Чого в архів НЕ класти:** нічого, на що посилається живий канон-файл.
Якщо wsd або Cookbook посилається на документ — він лишається в Project.

---

## §4 Реєстр

> Порожній. Заповнюється при першій архівації (Konst: «пізніше, зараз не вистачає ресурсу»).
> Порядок: залити **всі** файли в `archive/` одним рухом → внести рядки сюди →
> аж тоді чистити project knowledge. Після заливки ціна помилкового видалення = нуль.

### summaries/

| файл | дата | продукт | що всередині | чому в архіві |
|---|---|---|---|---|
| — | — | — | — | — |

### benches/

| файл | дата | продукт | що всередині | чому в архіві |
|---|---|---|---|---|
| — | — | — | — | — |

### builds/

| файл | дата | продукт | що всередині | чому в архіві |
|---|---|---|---|---|
| — | — | — | — | — |

### concepts/ · misc/

| файл | дата | продукт | що всередині | чому в архіві |
|---|---|---|---|---|
| — | — | — | — | — |


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

### `archive/summaries/` — 54 файлів

- `QR_Lens_session_summary_A58_harness_v1.md`
- `QR_Lens_session_summary_A58_portplan_LOCK.md`
- `QR_Lens_session_summary_A58motion_persist_PLAN.md`
- `QR_Lens_session_summary_B58_B58_2.md`
- `QR_Lens_session_summary_T2harness_v3.md`
- `QR_Lens_session_summary_srmotion_LOCK_B58plan.md`
- `QR_Lens_session_summary_srpill_LOCK.md`
- `QR_Lens_session_summary_srpill_implPLAN.md`
- `StockCheck_session_summary_Node2_1_maintBench.md`
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

### `archive/superseded/` — 4 файлів

- `Drive_Lens_concept_v1.md`
- `Drive_Lens_concept_v1_2.md`
- `KPI_Lens_categories_Excel_impl_Batch15.md`
- `farmastor_v2_data.js`

**Разом: 81 файлів.**
