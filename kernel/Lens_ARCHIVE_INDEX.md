> живе доки: назавжди (вічне, wsd 1.8)
> читається коли: мікроскоп перед кодом — хід архівує файли або шукає архівне джерело · не читається: на старті сесії; цілком
> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens

# Lens · ARCHIVE INDEX — що лежить в архіві й коли туди йти

> **Навіщо — двоє дверей.** Архів лежить у репо (`archive/`).
> · **Claude Code** — архів у клоні: шукати грепом (`git grep -n <що> -- archive/`, повний список — `git ls-files archive/`); цей файл дає **сенс** рядка (що всередині, чому виселено), а не адресу.
> · **claude.ai Project** — `archive/` **не підключено** (з'їдає ліміт Project): Claude бачить лише цей файл і тягне архівний — точним іменем звідси, `gh_read` конектора (`tools/CHAT_TOOLS.md`). Немає імені тут — файл для Project не існує.
>
> **Без цього файлу архівація = видалення** (для Project) і пошук без сенсу (для Claude Code).

**Адреса архівного файла** (шлях від кореня репо, Ф1): `archive/<тека>/<файл>` — для Project raw-база
`https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/archive/<тека>/<файл>`.

---

## §1 Коли Claude звертається до архіву — САМ, без нагадування

| тригер | що робити |
|---|---|
| «як ми робили X», «ми це вже вирішували», «колись було» — і в **живих** файлах відповіді немає | Claude Code — греп по `archive/`; Project — ім'я з цього індексу → `gh_read` |
| будую **стенд** для компонента, у якого стенд уже був | взяти попередній як базу — важелі й уроки вже знайдені, не винаходити заново |
| канон посилається на самері, якого **немає** серед живих (напр. «b26_1 §4») | дістати те самері з архіву (продуктове — з `archive/` репо продукту) |
| **регресія**: працювало раніше — зламалось | знайти батч, де воно було device✓, і звірити |
| стартує **новий продукт** | знайти найближчий аналог серед стендів і концептів |

**Коли НЕ звертатись:** штатний старт сесії · планування нової фічі з нуля ·
будь-що, на що відповідають живі файли. Архів — не джерело правди, а **свідчення**.
При суперечності живий файл виграє завжди.

---

## §2 Структура тек

*(звірено `git ls-files archive/` 06.10.2026, ХІД-8 · `IDX-13`)*

```
archive/
  summaries/    самері governance і тексти їхніх кроків — уся тека в підтеці Lens_gov/
  superseded/   витіснене іншим файлом: буфер A45, ТЗ конектора lens-gh, запис токеном із чату
```
У корені `archive/` — лише моноліт кукбуку `Lens_iOS_cookbook.md`. **Продуктового архіву в ядрі нема**
(`kernel/Lens_REPO_LAYOUT.md` §4-б, Р-3): самері, стенди й матриці продуктів — `archive/` репо продукту.

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
Якщо wsd або Cookbook посилається на документ — він лишається живим (поза `archive/`).

---

## §3-б Перейменування живих файлів — таблиця перенаправлень

Архівні файли **не переписуються** при перейменуванні живого канону: вони — історія,
написана до перейменування, і правка зробила б їх свідченням про те, чого тоді не було.
Натомість старе ім'я живе **тут**, і Claude, який зустрів його в архівному самері,
знаходить чинне за один греп.

| старе ім'я (лишилось в архіві) | чинне ім'я | коли · чому |
|---|---|---|
| `StockCheck_island_glass_FINDINGS.md` | **`kernel/Lens_glass_FINDINGS.md`** | 21.08.2026, EquipLens S6. Знахідки виявились крос-Lens: §1–§6 виросли на StockCheck-острівці, §9 «Виріз у склі» — на EquipLens-бульбашці. Числа лишились прив'язані до продукту, закони — ні. **17 входжень старого імені в `archive/` залишено навмисно** |

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

## Перепис архіву *(заведено 31.07.2026 · звірено з деревом 06.10.2026, ХІД-8)*

**Правило.** Перед тим як сказати «цього файлу не існує» — греп по `archive/` (Claude Code) або
пошук тут (Project). Файл, виселений із живих, не мертвий: він переїхав (`Lens_INDEX.md` §8).
**Порядок рядків — оголошення:** `G19` бере з нього порядок сесій (`kernel/Lens_validate.py`, `_declared_order`) —
нові рядки дописувати в кінець своєї теки, не сортувати.

### `archive/` — корінь

- `Lens_iOS_cookbook.md` — моноліт Cookbook, 227 KB, 78 записів. Розпиляно
  на 5 томів у сесії B; нумерація A-записів наскрізна й НЕ мінялась,
  тому старі посилання «Cookbook A45» дійсні для томів. Піднімати лише
  для археології (звірка, чи щось загубилось при розпилі).

### `archive/summaries/` — 131 файл, усі в підтеці `Lens_gov/`

Самері продуктів (StockCheck · Фармастор · QR Lens · EquipLens · Drive Lens · KPI Lens) виїхали в `archive/summaries/`
своїх репо (Р-3, переїзд 24.09–06.10.2026). Перелік, що стояв тут до виїзду (89 рядків, лише продуктові),
— історія git цього файла до ХІД-8 (`315ad49`).

### `archive/summaries/Lens_gov/` — 131 файл *(заведено G-C3 17.09.2026; самері · тексти кроків · скрипти пакетів; кожен файл названий — звірено 06.10.2026)*

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
- `Lens_governance_session_summary_GT_S35_INVENTAR.md` · 24.09.2026 · Lens governance · G-T (інвентар перед переїздом, Ф1–Ф8 питаннями): витіснене G-V (стеля 2) з `sessions/Lens_gov/`; супутник `Lens_inventory_GT_v1.md` — теж тут з 06.10.2026 (нижче)
- `Lens_governance_session_summary_GU_F1_ADRESA.md` · 24.09.2026 · Lens governance · G-U (Ф1 адресація `Репо:шлях`, Ф2 governance-самері в репо): витіснене G-W (стеля 2) з `sessions/Lens_gov/`
- `Lens_governance_session_summary_GV_F4_KORPUS.md` · 24.09.2026 · Lens governance · G-V (Ф4 корпус у ядрі, детектор Ф1 — `G24`, Ф1 чинне): витіснене G-Y (стеля 2) з `sessions/Lens_gov/`
- `Lens_governance_session_summary_GW_F3_YADRO.md` · 24.09.2026 · Lens governance · G-W (Ф3 «ядро ⟂ продукти», журнал переїзду, Р-1…Р-7): витіснене G-Y (стеля 2) з `sessions/Lens_gov/`
- `Lens_governance_session_summary_GX_START_APP.md` · 24.09.2026 · Lens governance · G-X (Lens_start.py, GitHub App, прев'ю-стенд О-5): витіснене LGH-3 (стеля 2) з `sessions/Lens_gov/`
- `Lens_governance_session_summary_LGH1_CONNECTOR_V11.md` · 26.09.2026 · Lens governance · LGH-1 (конектор «Lens GitHub» v1.1, П-LGH1…7, докази блокера LGH-0): витіснене LGH-3, §0 перенесено в LGH-3 §0
- `Lens_governance_session_summary_LGH2_TICKET_V12.md` · 27.09.2026 · Lens governance · LGH-2 (квиток v1.2, wsd 1.9-б, П-LGH8…11): витіснене LGH-3, §0 перенесено в LGH-3 §0
- `Lens_governance_session_summary_GY_GIT_APP_2B.md` · 27.09.2026 · Lens governance · G-Y (Р-4′ · Р-8 · Р-9, коміт А EquipLens, план G-Z): витіснене G-Z, §0 перенесено в G-Z §0
- `Lens_governance_session_summary_LGH3_ADAPT_PREVIEW.md` · 27.09.2026 · Lens governance · LGH-3 (адаптер · прев'ю-стенд · інструкція v4, П-LGH12…15): витіснене G-Z, §0 перенесено в G-Z §0
- `Lens_governance_session_summary_HA_CC4_YADRO_ADOPT.md` · 05–06.10.2026 · Lens governance · H-A (ядро під каркас Claude Code, ревізія CC-4; дописувала H-B): витіснене H-B, §0 перенесено в H-B §0
- `Lens_inventory_GT_v1.md` · 24.09.2026 · Lens governance · інвентар G-T перед переїздом (Ф1–Ф8): «живе доки» виконано (формула — `kernel/Lens_REPO_LAYOUT.md`); виселено з `sessions/Lens_gov/` 06.10.2026 (ХІД-8)

### Стенди — виїхали з ядра

Теки `archive/stands/` у ядрі більше нема (05–06.10.2026, журнал GW кроки 3–4): стенди StockCheck і Фармастора — `stock-check:archive/stands/`, QR Lens — `QR-Lens:archive/stands/`. Перелік до виїзду — історія git цього файла.

### `archive/superseded/` — 4 файли *(звірено `git ls-files` 06.10.2026)*

Продуктове витіснене виїхало з продуктами: Drive Lens концепти → `Drive-Lens:archive/superseded/`, KPI → `KPI-Lens:archive/superseded/`
(05.10.2026), `farmastor_v2_data.js` · `StockCheck_B32_STAGEBENCH_HANDOFF.md` · `StockCheck_collapse_C_CANON_delta.md` — зі StockCheck у `stock-check` (06.10.2026).

- `canon_delta_A45_material_lever_manifest.md` — 🗄 01.08.2026. Буфер **пережив ціль**: A45 канонізовано в `Lens_iOS_cookbook_3_material.md`. Йти сюди тільки за **сирими важелями компера** матеріальності, яких канон не зберіг

- `lens-gh_SPEC_v1.2.md` · 27.09.2026 · Lens (інструменти чату) · ТЗ конектора lens-gh v1.2 «квиток» (контейнер ↔ воркер ↔ GitHub повз контекст), ред. 3 · задеплоєно й прийнято Konst (LGH-2), зміст влито в `tools/lens-gh/README.md` і `tools/CHAT_TOOLS.md` §2-б; до архіву лежав у теці tools/lens-gh/ під іменем SPEC_v1.2.md
- `Lens_github_push_protocol.md` · `Lens_claude_github_push.py` · 06.10.2026 · Lens (двері Project) · запис у GitHub із чату токеном (П-GH1, v2–v3, PLAN-ID) · витіснено конектором «Lens GitHub» (`tools/CHAT_TOOLS.md`, інструкція Project v4 27.09.2026); у Claude Code — `git`. Живі інструменти Project не архівуються (`Lens_INDEX` §0) — цей уже не живий (`GH-1`, ХІД-8)

### ❌ Втрачене при переїзді — НЕ шукати

Порожньо в ядрі: єдиний рядок (`StockCheck_collapse_C_CANON_delta.md`, «втрату» скасовано 30.08.2026, інцидент — історія git `kernel/Lens_INDEX.md`) — продуктовий, виїхав зі StockCheck.

**Разом: 136 файлів** — корінь 1 · `summaries/Lens_gov/` 131 · `superseded/` 4 (`git ls-files archive | wc -l`, 06.10.2026).
