> живе доки: назавжди (вічне, wsd 1.8)
> читається коли: мікроскоп перед кодом — хід архівує файли або шукає архівне джерело · не читається: на старті сесії; цілком
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

## §3-б Перейменування живих файлів — таблиця перенаправлень

Архівні файли **не переписуються** при перейменуванні живого канону: вони — історія,
написана до перейменування, і правка зробила б їх свідченням про те, чого тоді не було.
Натомість старе ім'я живе **тут**, і Claude, який зустрів його в архівному самері,
знаходить чинне за один греп.

| старе ім'я (лишилось в архіві) | чинне ім'я | коли · чому |
|---|---|---|
| `StockCheck_island_glass_FINDINGS.md` | **`products/Lens_glass_FINDINGS.md`** | 21.08.2026, EquipLens S6. Знахідки виявились крос-Lens: §1–§6 виросли на StockCheck-острівці, §9 «Виріз у склі» — на EquipLens-бульбашці. Числа лишились прив'язані до продукту, закони — ні. **17 входжень старого імені в `archive/` залишено навмисно** |

**Правило:** перейменував вічний файл → рядок сюди **в тій самій сесії**.
Перейменування без рядка тут = битий лінк у кожному архівному самері, який на нього
посилався, і «файлу не існує» замість «файл переїхав».

-----

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

### `archive/summaries/` — 89 файлів

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
- `StockCheck_session_summary_H5_0_O20_stand_PLAN.md` — план і мікроскоп стенда О-20; витіснено `H5_1_eyebrow_LOCK` (стенд v1 відхилено, О-41/О-43 закрито рішенням Р-44)
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

- `StockCheck_session_summary_H5_5_eb_LOCK_O47.md` · 13.08.2026 · StockCheck · ярус eyebrow ЛОК + О-47
- `StockCheck_session_summary_H6_0_O47_SHEET.md` · 13.08.2026 · StockCheck · шіт вибору мережі О-47
- `StockCheck_session_summary_b29_ARCHIVE_ROADMAP.md` · 13.08.2026 · StockCheck · попередня дорожня карта архіву — витіснена `G1_ARCHIVE_MANIFEST_v1.md`
- `StockCheck_session_summary_b32_1_PORTFIX_PLAN.md` · 13.08.2026 · StockCheck · план порту b32.0→b32.1
- `StockCheck_session_summary_b32_1_s1s2_DONE_O48_NEXT.md` · 13.08.2026 · StockCheck
- `StockCheck_session_summary_b32_1_s3_O48_DONE_P8_NEXT.md` · 13.08.2026 · StockCheck · О-48 фільтр мереж за областю
- `StockCheck_session_summary_b32_1_s4_PICKER_REWORK_PLAN.md` · 13.08.2026 · StockCheck
- `StockCheck_session_summary_b32_1_s5_CROP_DONE.md` · 13.08.2026 · StockCheck
- `StockCheck_session_summary_b32_1_s6s11_P8_PICKER_DONE.md` · 13.08.2026 · StockCheck · пікер мереж, числа портовані в b32.1
- `StockCheck_session_summary_b32_1_s12_ADDR_DONE_O49_SPEC.md` · 13.08.2026 · StockCheck · адресний шум О-50 закрито, спека О-49
- `StockCheck_session_summary_b32_1_s13_STAGEBENCH_v1_FAIL_v2_SPEC.md` · 13.08.2026 · StockCheck · відбраковка стенда v1 → **народження Г-1**
- `StockCheck_session_summary_b32_1_s14_STAGEBENCH_v2_DONE.md` · 13.08.2026 · StockCheck · стенд грошей v2 · **єдиний носій повного тексту Г-1…Г-3** до мерджу в буфер 13.08
- `StockCheck_session_summary_b32_1_s15c_STAGEBENCH_LOCK.md` · 13.08.2026 · StockCheck · ЛОК чисел форми грошей (device-судимо) · **єдиний носій повного тексту Г-4** до мерджу в буфер 13.08


**EquipLens — 12 самері, виселено 24.08.2026 (S14).** Живими лишились `S13` і `S14`
(`Lens_INDEX §5`, стеля `G10`). Тексти рішень S11/S12 влиті в канон — самері тримались
лише як переказ.

- `EquipLens_session_summary_S1_FOUNDATION.md`
- `EquipLens_session_summary_S2_TOKEN_HARNESS.md`
- `EquipLens_session_summary_S3_HEADBENCH_THESIS.md`
- `EquipLens_session_summary_S4_HEADBENCH_v5.md`
- `EquipLens_session_summary_S5_UX_GLASS_v7.md`
- `EquipLens_session_summary_S6_GOV_v8_TABS.md` — 3 таби (`Потреби · Обладнання · Огляд`), перейменування FINDINGS
- `EquipLens_session_summary_S7_V9_BOTTOM_HEAD.md`
- `EquipLens_session_summary_S8_LOCK_HEADGLASS.md`
- `EquipLens_session_summary_S9_BAKE_SPLIT_VOLUME.md`
- `EquipLens_session_summary_S10_VOLUME_SHADING_EDGE.md`
- `EquipLens_session_summary_S11_SPLIT_GLASSKIT.md` — 33 світлі значення шейдингу запечені, `LOCK_MIGRATE`, 5 зовнішніх Liquid Glass репо; тексти влиті в Cookbook `A91`–`A102`
- `EquipLens_session_summary_S12_GOVERNANCE_DRAIN.md` — черга 26 записів, вичерпана в S13
- `EquipLens_session_summary_S30_SCALE_VERDICT.md` · 24.09.2026 · витіснено S34/S35 (G-T)
- `EquipLens_session_summary_S31_HEAD_LEVERS.md` · 24.09.2026 · витіснено S34/S35 (G-T)
- `EquipLens_session_summary_S32_FONT.md` · 24.09.2026 · витіснено S34/S35 (G-T)
- `EquipLens_session_summary_S33_CHILLAX.md` · 24.09.2026 · витіснено S34/S35 (G-T)

### `archive/summaries/Lens_gov/` — 120 файлів *(заведено G-C3 17.09.2026; шлях з підтекою — raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*

- `Lens_session_summary_governance_A.md` · governance A (31.07)
- `Lens_session_summary_governance_B.md` · governance B
- `Lens_session_summary_governance_C.md` · governance C
- `Lens_session_summary_governance_D.md` · governance D
- `Lens_session_summary_governance_E.md` · governance E — лежав без рядка (§3 «втрачений»), закрито G-C3

- `Lens_governance_session_summary_GA_BUFERY.md` · 17.09.2026 · Lens governance · G-A: шапки буферів = факт, IDX-6 · §0 підхоплено G-B
- `Lens_governance_session_summary_GB_TRIAZH.md` · 17.09.2026 · Lens governance · G-B: тріаж stagebench-буфера · §0 підхоплено G-B2
- `Lens_governance_session_summary_GB2_ZLYTTIA_B.md` · 17.09.2026 · Lens governance · G-B2: злиття груп Б1/Б2 у manifest · §0 закрито G-B3
- `Lens_governance_session_summary_GB3_ZLYTTIA_V.md` · 17.09.2026 · Lens governance · G-B3: група В, stagebench-буфер 0 · §0 закрито G-C
- `Lens_governance_session_summary_GC1_ZLYTTIA_WSD.md` · 17.09.2026 · Lens governance · G-C1: злиття wsd-буфера, групи А/Б/В · G-C запушено 6b9943f
- `Lens_governance_session_summary_GC2a_HRUPA_G.md` · 17.09.2026 · Lens governance · G-C2a: група Г; §2 — повні тексти G16-1 · Г-13 (на нього посилається CHERGA, доступ — рівень 3 драбини §8) · G-C запушено 6b9943f
- `Lens_governance_session_summary_GC2b_FINAL_AUDYT.md` · 17.09.2026 · Lens governance · G-C2b: фінал злиття + аудит зв'язності; §2 — повний текст К3-1 · G-C запушено 6b9943f, §0 закрито G-C3
- `Lens_governance_session_summary_GC3_PUSH_ARCHIV.md` · 17.09.2026 · Lens governance · G-C3: архів governance-хвоста Project, `IDX-13` (повний текст §2) · пушено 73ff3e4, §0 закрито G-D, в архів G-E
- `Lens_governance_session_summary_GD_COOKBOOK.md` · 17.09.2026 · Lens governance · G-D: cookbook-буфер 17→12 (5 → томи 3/4/5); §2 — Ф-2 · Ф-3 · Ф-4 повним текстом · пушено 6b08c83, §0 закрито G-E/G-F, в архів G-F
- `Lens_session_summary_GH1_PUSH_Z_CHATU.md` · 17.09.2026 · Lens governance · GH1: протокол П-GH1, пуш з чату · гілку змерджено, B63 стартував
- `GA_step2_texts_v1.md` · 17.09.2026 · Lens governance · G-A: тексти вставок В1–В9 · влиті скриптом
- `GB_triage_v1.md` · 17.09.2026 · Lens governance · G-B: таблиця тріажу · злиття виконано
- `GB2_groupB1_texts_v1.md` · 17.09.2026 · Lens governance · G-B2: тексти Б1 · влиті й пушені
- `GB2_groupB2_texts_v1.md` · 17.09.2026 · Lens governance · G-B2: тексти Б2 · влиті й пушені
- `GB3_DA_texts_v1.md` · 17.09.2026 · Lens governance · G-B3: тексти Д-А · влиті й пушені
- `GB3_DB_texts_v1.md` · 17.09.2026 · Lens governance · G-B3: тексти Д-Б · влиті й пушені
- `GB3_DK_texts_v1.md` · 17.09.2026 · Lens governance · G-B3: тексти Д-К · влиті й пушені
- `ga_step1_g11_v1.py` · 17.09.2026 · Lens governance · пакет G-A: G11 · залито в репо
- `ga_step2_insert_v1.py` · 17.09.2026 · Lens governance · пакет G-A: вставки за якорями · залито в репо
- `ga_step4_index_cherga_v1.py` · 17.09.2026 · Lens governance · пакет G-A: INDEX/CHERGA · залито в репо
- `g11hist.py` · 17.09.2026 · Lens governance · G-A: історія G11 (закриття IDX-6) · IDX-6 закрито
- `gb_step1b_triage_v1.py` · 17.09.2026 · Lens governance · пакет G-B: тріаж · злиття виконано
- `gb_step2A_merge_v1.py` · 17.09.2026 · Lens governance · пакет G-B2: група А · пушено
- `gb2_step1B1_merge_v1.py` · 17.09.2026 · Lens governance · пакет G-B2: Б1 · пушено
- `gb2_step1B2_merge_v1.py` · 17.09.2026 · Lens governance · пакет G-B2: Б2 · пушено
- `gb3_step1A_merge_v1.py` · 17.09.2026 · Lens governance · пакет G-B3: А · пушено f4decb7
- `gb3_step1B_merge_v1.py` · 17.09.2026 · Lens governance · пакет G-B3: Б · пушено f4decb7
- `gb3_step1C_merge_v1.py` · 17.09.2026 · Lens governance · пакет G-B3: В · пушено f4decb7
- `gb3_step1D_addr_v1.py` · 17.09.2026 · Lens governance · пакет G-B3: літерні адреси · пушено f4decb7
- `gb3_step2_index_v1.py` · 17.09.2026 · Lens governance · пакет G-B3: INDEX · пушено f4decb7
- `gc_step1A_wsd_v1.py` · 17.09.2026 · Lens governance · пакет G-C: група А · пушено 6b9943f
- `gc_step1B_wsd_v1.py` · 17.09.2026 · Lens governance · пакет G-C: група Б · пушено 6b9943f
- `gc_step1B2_s32ref_v1.py` · 17.09.2026 · Lens governance · пакет G-C: s32-посилання · пушено 6b9943f
- `gc_step1V_wsd_v1.py` · 17.09.2026 · Lens governance · пакет G-C: група В · пушено 6b9943f
- `gc_step1G_wsd_v1.py` · 17.09.2026 · Lens governance · пакет G-C: група Г · пушено 6b9943f
- `gc_step2_final_v1.py` · 17.09.2026 · Lens governance · пакет G-C: фінал (wsd 2.35, Z_REGISTR, CHERGA, INDEX) · пушено 6b9943f
- `gc3_step1_archive_v1.py` · 17.09.2026 · Lens governance · пакет G-C3: архів 34 файлів + INDEX/CHERGA/ARCHIVE_INDEX · пушено 73ff3e4
- `gd_step1_merge_v2.py` · 17.09.2026 · Lens governance · пакет G-D: 5 записів буфера → томи 3/4/5 + Cookbook INDEX §2/§3 · пушено 6b08c83
- `gd_step2_prune_v2.py` · 17.09.2026 · Lens governance · пакет G-D: прополка cookbook-буфера + INDEX §4 + CHERGA `IDX-12` · пушено 6b08c83
- `Lens_governance_session_summary_GE_K2_PILOT.md` · 17.09.2026 · Lens governance · G-E: пілот К2-1 на gov-протоколі (0/12 ✅), шаблон вироку GE2 §1; §2 — Ф-8 (пастка підрядка G10) · Ф-9 · пушено 3a8a36a/b5e3f5c/e53824f, §0 закрито G-F, в архів G-G
- `GE2_k2_gov_texts_v1.md` · 17.09.2026 · Lens governance · G-E: тексти вироків gov-протоколу + §1 шаблон, §4 G16-1 · влиті b5e3f5c
- `ge_step1_archive_v1.py` · 17.09.2026 · Lens governance · пакет G-E: архів GC3 + gc3_step1 · пушено 3a8a36a
- `ge_step3_k2gov_v1.py` · 17.09.2026 · Lens governance · пакет G-E: К2-1 gov-протокол 5/12 → 0/12 · пушено b5e3f5c
- `ge_step4_cherga_v1.py` · 17.09.2026 · Lens governance · пакет G-E: CHERGA К2-1 + G16-1 · пушено e53824f
- `GF2_k2_wsd_texts_v1.md` · 17.09.2026 · Lens governance · G-F: тексти вироків wsd група 1 · влиті 6bc28f5
- `GF5_k2_wsd_texts_v1.md` · 17.09.2026 · Lens governance · G-F: тексти вироків wsd група 2 · влиті 3ef4dd0
- `gf_step1_archive_v1.py` · 17.09.2026 · Lens governance · пакет G-F: архів GD + gd_step1/2 · пушено f35a2e7
- `gf_step3_k2wsd_v1.py` · 17.09.2026 · Lens governance · пакет G-F: К2-1 wsd група 1 (36/68) · пушено 6bc28f5
- `gf_step4_cherga_v1.py` · 17.09.2026 · Lens governance · пакет G-F: CHERGA К2-1 36→27 · пушено 139e173
- `gf_step5_k2wsd_v1.py` · 17.09.2026 · Lens governance · пакет G-F: К2-1 wsd група 2 (27/68) · пушено 3ef4dd0
- `gf_step6_cherga_v1.py` · 17.09.2026 · Lens governance · пакет G-F: CHERGA К2-1 27→18 · пушено 3a9715a
- `Lens_governance_session_summary_GF_K2_WSD12.md` · 18.09.2026 · Lens governance · G-F: К2-1 wsd 18/68 (дві групи вироків); §2 — Ф-6 сегмент правила · Ф-7 · пушено 6bc28f5/3ef4dd0/3a9715a, §0 закрито G-G, в архів G-H
- `GG2_k2_wsd_texts_v1.md` · 18.09.2026 · Lens governance · G-G: тексти вироків wsd група 1 · влиті 818bf18
- `GG5_k2_wsd_texts_v1.md` · 18.09.2026 · Lens governance · G-G: тексти вироків wsd група 2 · влиті 818bf18
- `gg_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-G: архів GE + пакети G-E/G-F · пушено 818bf18
- `gg_step3_k2wsd_v1.py` · 18.09.2026 · Lens governance · пакет G-G: К2-1 wsd група 1 · пушено 818bf18
- `gg_step5_k2wsd_v1.py` · 18.09.2026 · Lens governance · пакет G-G: К2-1 wsd група 2, `G16` по wsd → ✓ · пушено 818bf18
- `gg_step6_cherga_v1.py` · 18.09.2026 · Lens governance · пакет G-G: CHERGA К2-1 закрито, +К4-1/К5-1/G3-1 · пушено 818bf18
- `Lens_governance_session_summary_GG_K2_ZAKRYTO.md` · 18.09.2026 · Lens governance · G-G: К2-1 закрито (gov 0/12 · wsd 0/68), канон у фазу прополки; §0 — черга 7 996 B при стелі, wsd 198 896 B · пушено 641b9bc, §0 закрито G-H/G-I, в архів G-J
- `gh_step1_cherga_v1.py` · 18.09.2026 · Lens governance · пакет G-H: прополка gov-черги 7 996→7 762 B, стеля 8 192 (IDX-10) · пушено 26c08b3
- `gh_step2_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-H: архів GF + пакет G-G (56→63), §5 → GG · пушено 26c08b3
- `rules_hits_v1.py` · 18.09.2026 · Lens governance · пакет G-H: лічильник спрацювань правил К4-1 (12/90 нулів) · джерело — коміт 26c08b3, стан до надгробка (у Project файла вже не було, G-I §0 п.7); влито як `G19` у f52f59e
- `Lens_governance_session_summary_GH_CHERGA_LICHYLNYK.md` · 18.09.2026 · Lens governance · G-H: прополка gov-черги 7 996→7 762 B, лічильник спрацювань К4-1 (12/90 нулів) · пушено 26c08b3, §0 закрито G-I/G-J, в архів G-K
- `gi_step1_intake_v1.py` · 18.09.2026 · Lens governance · пакет G-I: INTAKE дописком у рядок К3-1 черги (+208 B, без нового id, Ф-10) · пушено f52f59e · в архів G-K (G-J пропустила, G-I §0 п.7)
- `gi_step2_g19_v1.py` · 18.09.2026 · Lens governance · пакет G-I: К4-1 — rules_hits.py влито в Lens_validate.py як G19 · пушено f52f59e · в архів G-K
- `gi_step3_declare_v1.py` · 18.09.2026 · Lens governance · пакет G-I: оголошено G19, К4-1 знято з черги, §5 G20 резерв · пушено f52f59e · в архів G-K
- `gj_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-J: архів GG + пакет G-H (63→67), §5 → GI · GH · пушено ea9dd5b
- `gj_step2_rulefiles_v1.py` · 18.09.2026 · Lens governance · пакет G-J: С1 розпилу wsd — RULE_FILES, G4 по всіх файлах правил, +G21 · пушено c0b6daa
- `Lens_governance_session_summary_GI_INTAKE_G19.md` · 18.09.2026 · Lens governance · G-I: INTAKE дописком у К3-1 (+208 B), К4-1 → G19 у Lens_validate.py · пушено f52f59e · §0 закрито G-J/G-K (INTAKE-текст §2 — адреса «G-I §2» у К3-1 черги), в архів G-L
- `gk_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-K: архів GH + пакет G-I + пакет G-J (67→73), §5 → GJ · GI · пушено 3d946e7
- `gk_step2_hist_v1.py` · 18.09.2026 · Lens governance · пакет G-K: С2 розпилу wsd — шапка-changelog 2.25–2.39 → HISTORY (8 414 B, md5) · пушено 655521b
- `gk_step3_delete_v1.py` · 18.09.2026 · Lens governance · пакет G-K: П-GH1 v2 --delete, видалено надгробок kernel/rules_hits.py · пушено e417d15
- `gk_step4_f14_v1.py` · 18.09.2026 · Lens governance · пакет G-K: Ф-14 → 12.16 gov-протоколу (перенос байт-у-байт з md5) · пушено 7e2a6d0
- `Lens_governance_session_summary_GJ_ROZPYL_S1.md` · 18.09.2026 · Lens governance · G-J: архів GG + пакет G-H, С1 розпилу wsd (RULE_FILES · G4 · G21) · пушено ea9dd5b · c0b6daa · §0 виконано G-K (С2, Ф-14, архів, надгробок) або перенесено в §0 G-L (план С5/С6, 1.1 п.3, G3-1), в архів G-M
- `gl_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-L: архів GI + пакет G-K (73→78), §5 → GK · GJ, Ф-15 у коді · пушено 709f587
- `gl_step2_c3_v1.py` · 18.09.2026 · Lens governance · пакет G-L: С3 розпилу wsd — кластер 13 → Lens_PROFILE.md §7 (12 391 B, md5) · пушено 20957b9 (маршрут-заглушки виправлено таблицею в bf606d1)
- `gl_step3_c4_v1.py` · 18.09.2026 · Lens governance · пакет G-L: С4 розпилу wsd — метод вироку → Lens_verdict_protocol.md (5 фрагментів, 50 660 B, md5) + таблиця маршрутів · пушено bf606d1
- `Lens_governance_session_summary_GK_ROZPYL_S2.md` · 18.09.2026 · Lens governance · G-K: архів GH + пакет G-I/G-J, С2 розпилу wsd (шапка-changelog → HISTORY), П-GH1 v2 (--delete), Ф-14 у 12.16 · пушено 3d946e7 · 655521b · e417d15 · 7e2a6d0 · §0 виконано G-L/G-M або перенесено в §0 G-M, в архів G-N
- `gm_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-M: архів GJ + пакет G-L (78→82), §5 → GL · GK, Ф-15 у коді · пушено 46c7bc4
- `gm_step2_c5_v1.py` · 18.09.2026 · Lens governance · пакет G-M: С5 розпилу wsd — перевірка → Lens_patch_check_protocol.md (6 фрагментів, 58 125 B, md5) + сирота «Четверта пастка» + 1.1 + PROFILE §6 + RULE_FILES chk · пушено 0261817
- `gm_step3_idx7_v1.py` · 18.09.2026 · Lens governance · пакет G-M: IDX-7 закрито за власною умовою (wsd 71 289 B < 120 KiB), висяча адреса в К6-1 → К3-1 · пушено 2f426e6
- `Lens_governance_session_summary_GL_ROZPYL_S3.md` · 18.09.2026 · Lens governance · G-L: архів GI + пакет G-K, С3 (кластер 13 → Lens_PROFILE §7) і С4 (метод вироку → Lens_verdict_protocol.md) розпилу wsd, маршрут-таблиця · пушено 709f587 · 20957b9 · bf606d1 · §0 виконано G-M/G-N або перенесено в §0 G-O, в архів G-O
- `gn_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-N: архів GK + пакет G-M (82→86), §5 → GM · GL, Ф-15 у коді · пушено 5f0979a
- `gn_step2_g23_v1.py` · 18.09.2026 · Lens governance · пакет G-N: С6 розпилу wsd — G23 «канон-файл без тригера читання» у Lens_validate --gov (49 645 → 51 376 B) · пушено cc9266a
- `gn_step3_k61_v1.py` · 18.09.2026 · Lens governance · пакет G-N: С6 — рядок «читається коли / не читається» у шапки 10 канон-файлів (G23 ✗10 → 0) · пушено d33a4b8
- `gn_step4_prof_v1.py` · 18.09.2026 · Lens governance · пакет G-N: С6 (12.18) — дублі-конспекти Lens_PROFILE §3/§4 → вказівники на §7 13.3/13.1 (21 440 → 19 902 B) · пушено 23ccfda
- `gn_step5_k61close_v1.py` · 18.09.2026 · Lens governance · пакет G-N: К6-1 закрито за власною умовою (G23 ✓ 26/26), рядок знято з черги (7 460 → 7 093 B) · пушено 6e2633c
- `Lens_governance_session_summary_GM_ROZPYL_S5.md` · 18.09.2026 · Lens governance · G-M: архів GJ + пакет G-L, С5 розпилу wsd (6 фрагментів → Lens_patch_check_protocol.md), IDX-7 закрито · пушено 46c7bc4 · 0261817 · 2f426e6 · §0 виконано G-N/G-O або перенесено в §0 G-P, в архів G-P
- `go_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-O: архів GL + пакет G-N (86→92), §5 → GN · GM, Ф-15 у коді · пушено 5333f77
- `go_step2_115_v1.py` · 18.09.2026 · Lens governance · пакет G-O: 1.15 «п'ять пасток» → «шість», сирота «Четверта пастка» → пункт 6 (60 146 → 59 529 B) · пушено 98cf939
- `go_step3_102_v1.py` · 18.09.2026 · Lens governance · пакет G-O: 10.2 злиття відхилено, правка лише K2-коментаря (59 529 → 59 656 B) · пушено b79c400
- `go_step4_cherga_v1.py` · 18.09.2026 · Lens governance · пакет G-O: черга ядра — дописки G3-1 і К3-1 (Ф-18 · Ф-19), нових id немає (7 093 → 7 274 B) · пушено f642fcd
- `go_step5_prof132_v1.py` · 18.09.2026 · Lens governance · пакет G-O: Lens_PROFILE §4 «Проактивні пропозиції» → вказівник на §7 13.2 (19 902 → 19 486 B) · пушено 9d41ef3
- `go_step6_f22_v1.py` · 18.09.2026 · Lens governance · пакет G-O: Ф-22 → Lens_github_push_protocol.md (7 886 → 8 742 B) · пушено 01f9626
- `Lens_governance_session_summary_GN_ROZPYL_S6.md` · 18.09.2026 · Lens governance · G-N: архів GK + пакет G-M, С6 розпилу wsd (G23 · 10 тригерів читання · PROFILE §3/§4), К6-1 закрито · пушено 5f0979a · cc9266a · d33a4b8 · 23ccfda · 6e2633c · §0 виконано G-O/G-P, в архів G-Q
- `gp_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-P: архів GM + пакет G-O (92→99), §5 → GO · GN, Ф-15 у коді · пушено c58b49d
- `gp_step2_114_v1.py` · 18.09.2026 · Lens governance · пакет G-P: 1.14 += Ф-21 · Ф-23 · Ф-15 (gov 53 024 → 56 287 B) · пушено 6105574
- `gp_step3_1216_v1.py` · 18.09.2026 · Lens governance · пакет G-P: 12.16 += Ф-20 · Ф-17 (gov 56 287 → 59 383 B) · пушено 9c0aa86
- `gp_step4_102p4_v1.py` · 18.09.2026 · Lens governance · пакет G-P: 10.2 п.4 → загальний інваріант + приклад QR Lens (chk 59 656 → 59 861 B) · пушено c51356f
- `Lens_governance_session_summary_GO_KANON_TOCHKOVO.md` · 18.09.2026 · Lens governance · G-O: архів GL + пакет G-N, точкові правки канону (1.15 · 10.2 · черга · PROFILE 13.2 · Ф-22) · пушено 5333f77 · 98cf939 · b79c400 · f642fcd · 9d41ef3 · 01f9626 · §0 виконано G-P/G-Q, в архів G-R (§2 Ф-24 — текст для К3-1, G-R)
- `gq_step1_archive_v1.py` · 18.09.2026 · Lens governance · пакет G-Q: архів GN + пакет G-P (99→104), §5 → GP · GO, Ф-15 у коді · пушено 39681fd
- `gq_step2_f25_v1.py` · 18.09.2026 · Lens governance · пакет G-Q: Ф-25 — структурна ознака заглушки в G16/G21 (Lens_validate 51 376 → 53 206 B) · пушено 5ad5f71
- `gq_step3_g22_v1.py` · 18.09.2026 · Lens governance · пакет G-Q: гейт G22 — стартове повідомлення в code block, варіант Б (53 206 → 55 874 B) · пушено 987d7ee
- `gq_step4_g6_v1.py` · 18.09.2026 · Lens governance · пакет G-Q: G6 — маркер «читається ТОЧКОВО» знімає сигнал 120 KB (55 874 → 56 413 B) · пушено 4323edf
- `Lens_governance_session_summary_GP_VLYVANNIA_F.md` · 19.09.2026 · Lens governance · G-P: архів GM + пакет G-O, вливання Ф у gov (1.14 · 12.16), 10.2 п.4 · пушено c58b49d · 6105574 · 9c0aa86 · c51356f · §0 виконано G-Q/G-R, в архів G-S
- `gr_step1_archive_v1.py` · 19.09.2026 · Lens governance · пакет G-R: архів GO + пакет G-Q (104→109), §5 → GQ · GP, Ф-15 у коді · пушено 2f4d056
- `gr_step2_f24_v1.py` · 19.09.2026 · Lens governance · пакет G-R: Ф-24 → Lens_INDEX §5 біля стелі черги (51 141 → 51 428 B) · пушено 788f62f
- `gr_step3_g16_v1.py` · 19.09.2026 · Lens governance · пакет G-R: G16 — мітка детектора будь-де в тілі правила (Lens_validate 56 413 → 57 258 B) · пушено 1e95cb9
- `gr_step4_g16close_v1.py` · 19.09.2026 · Lens governance · пакет G-R: закриття G16-1 — gov 12.12 += мітка детектора · 12.17 += K2:n/a (gov 59 383 → 59 768 B) · пушено fcfc3ec
- `Lens_session_summary_governance_F_CHERGA_PLAN.md` · 24.09.2026 · Lens governance · governance F (план черги): витіснене G-C3 17.09.2026, у Project лежало сиротою до G-U (Ф-15, старий префікс — звірено вручну)
- `Lens_session_summary_governance_G_MASKA.md` · 24.09.2026 · Lens governance · governance G (маска, `12.20`): витіснене G-C3 17.09.2026, у Project лежало сиротою до G-U (Ф-15, старий префікс — звірено вручну)
- `gu_step1_archive_v1.py` · `gu_step2_f1_v1.py` · `gu_step3_f2_v1.py` · 24.09.2026 · Lens governance · пакет G-U (хід 1 — §5 → GT + сироти F·G; хід 2 — Ф1, дім формули; хід 3 — Ф2 для governance). Коміти `e53b104` · `2d1cc26` · хід 3
- `Lens_session_summary_governance_E_PROJECT.md` · 24.09.2026 · Lens governance · друга редакція самері governance E (11 285 B, md5 `f79e66ca`), що лежала в Project під іменем архівної (`dac233a8`, 22 929 B); перейменовано, щоб не було дубля імені

### `archive/stands/` — 28 файлів

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

- `StockCheck_port_b32_0.html` — 🗄 13.08.2026. Білд v2.24.0 b32.0 «шов»: `NETS[]` повним масивом, `S.net`, `AREA_ORDER`. Витіснений b32.2 (device✓)
- `StockCheck_b32_0_matrix_v2.js` + `b32_0_baseline.json` — 🗄 13.08.2026. Матриця b32.0 **без jsdom**: витяг функцій із живого білда регексами + baseline b31. Йти сюди за формою «матриця без DOM», не за числами
- `StockCheck_netmark_stagebench_v3_7.html` + `lock_smoke_v37.js` — 🗄 13.08.2026. Стенд мітки мережі: ярус Р-46, О-47 шіт/ніша, ЛОК-регістр Р-50. **О-20 закрито** оператором 13.08; числа живуть у `StockCheck_materiality_valuesLOCK` §11/§12
- `StockCheck_netpick_matrix.js` + `StockCheck_netpick_v3_smoke_b6.js` + `StockCheck_netpick_v3_live_b6.js` — 🗄 13.08.2026. Матриці сітки NetPick v3, числа b6. Портовано в b32.1 (s6–s11)
- `StockCheck_h2_msl_data.py` — 🗄 13.08.2026. Дані H2; витіснено `StockCheck_msl_gen.py` (b31)

### `archive/superseded/` — 7 файлів

- `Drive_Lens_concept_v1.md`
- `Drive_Lens_concept_v1_2.md`
- `KPI_Lens_categories_Excel_impl_Batch15.md`
- `farmastor_v2_data.js`
- `canon_delta_A45_material_lever_manifest.md` — 🗄 01.08.2026. Буфер **пережив ціль**: A45 канонізовано в `Lens_iOS_cookbook_3_material.md`. Йти сюди тільки за **сирими важелями компера** матеріальності, яких канон не зберіг

- `StockCheck_B32_STAGEBENCH_HANDOFF.md` — 🗄 13.08.2026. Хендофф на побудову стенда грошей. Ціль досягнута: стенд v2 побудовано й залочено (s15c)

### ❌ Втрачене при переїзді — НЕ шукати

Файли, які були **оголошені** як заархівовані, але фізично до архіву не доїхали.
Тримаються тут іменем, щоб наступний, хто спіткнеться об посилання, не витрачав
час на пошук і не вирішив, що архів зламався.

- `StockCheck_collapse_C_CANON_delta.md` — оголошений виїзд 01.08.2026 (сесія E),
  фактично **404**. Втрачено транспорт, не зміст: ціль буфера канонізована як **A72**
  у `Lens_iOS_cookbook_5_motion.md`. Закрито 13.08.2026 як Р-5, відновлення не потрібне.

**Разом: 113 файлів.** *(лічильники перераховані за фактом рядків 13.08.2026, сесія G-1 — стара цифра 81 розходилась із переліком)*
