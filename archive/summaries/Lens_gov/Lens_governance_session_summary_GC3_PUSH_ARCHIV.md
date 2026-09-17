> живе доки: governance-сесія G-D закрила §0 цього самері і звітувала пілот Docs (§0 п.3) — тоді це архів
> близнюк-пілот Claude Docs: https://claude.ai/code/artifact/dce094ad-cfa7-4d6a-975c-c34fd691d59e (джерело правди — цей .md)

# Lens governance · G-C3 · пуш G-C + архів · 17.09.2026

Попереднє: `Lens_governance_session_summary_GC2b_FINAL_AUDYT.md` (архів). Його §0 п.2–4 виконано тут.

## §0 ВІДКРИТЕ

G-C закрито: пуш `6b9943f`, архів `73ff3e4`, `main` = `73ff3e4`.

1. **Konst: завантажити в Project** це самері і `gc3_step1_archive_v1.py` з outputs.
2. **Konst: видалити з Project 34 файли** — усі вже в `archive/summaries/Lens_gov/`, read-back 37/37:
   - самері: `Lens_governance_session_summary_` GA_BUFERY · GB_TRIAZH · GB2_ZLYTTIA_B · GB3_ZLYTTIA_V · GC1_ZLYTTIA_WSD · GC2a_HRUPA_G · GC2b_FINAL_AUDYT · `Lens_session_summary_GH1_PUSH_Z_CHATU.md`
   - тексти: GA_step2_texts_v1 · GB_triage_v1 · GB2_groupB1_texts_v1 · GB2_groupB2_texts_v1 · GB3_DA/DB/DK_texts_v1
   - скрипти: ga_step1_g11 · ga_step2_insert · ga_step4_index_cherga · g11hist · gb_step1b_triage · gb_step2A_merge · gb2_step1B1/B2_merge · gb3_step1A/B/C_merge · gb3_step1D_addr · gb3_step2_index · gc_step1A/1B/1B2/1V/1G · gc_step2_final
3. **Пілот Docs — перевірка на старті наступної сесії:** чи відкривається документ-близнюк за посиланням (зокрема з іншого акаунта). Вдалось → вирок у CHERGA: де оголошувати живе самері-документ, щоб G10 не рахував фантом, і як це стикується з `gov 1.14`. Не вдалось → лишаємо `.md`. **Факт 17.09.2026 (скрін Konst):** з iPhone документ не відкрився ні в Safari, ні у viewer застосунку Claude — «This browser isn't supported. Update it to open this artifact.» Причина не встановлена (версія iOS/WebKit не звірена). Перевірити: оновлення iOS · ПК-браузер. Поки мобільний доступ не доведено, Docs **не** носій живого самері.
4. **`IDX-13`** (CHERGA) — прополка `Lens_ARCHIVE_INDEX` + сліпота G3/G10 до межі `archive/`; повний текст у §2.
5. **Кандидат (без рядка — CHERGA на стелі, 7 993 B):** прибрати ручні заливки в Project — приватне репо/тека, підключена до Project через Sync, або Claude Docs. Рішення Konst.
6. **Перенесено без змін:** G10 ✗ на самері структурний (`IDX-9`/`G15`) · `G13-1` · `G16-1` · `Г-13` · `К3-1` (повні тексти — GC2a §2 · GC2b §2, архів `Lens_gov/`) · колізія інструкції Project (gov точково) · `#s-cmp` без дому.
7. **Далі:** G-D cookbook (**17**, `A105` готовий). Прополка wsd (`К2-1` · `К1-1` · `IDX-7` · `К3-1`).

## §1 Що зроблено

| крок | вирок |
|---|---|
| 0 | клон `f4decb7` · `Lens_validate.py` `77cbf214` і `Lens_claude_github_push.py` `096e6ea4` raw = клон · ланцюг gc_step 1A→1B→1B2→1V→1G→step2: md5 = GC2b §0 п.2, повтори no-op ×6 · CHERGA 7 924 B · `--gov` ✓10 ⚠38 ✗87 |
| 2 · пуш G-C | `6b9943f` ← `f4decb7` · 6 файлів · PLAN-ID `45bc44` · read-back 6/6 · дельта +1✓ −1⚠ (G5 буфер wsd порожній), ✗ 0 |
| 3 · читання | `gov 1.14` · `12.11` · `12.16` · `12.19` · `12.19-б` · INDEX §8 · `Lens_ARCHIVE_INDEX` — цілком |
| 3 · архів | `73ff3e4` ← `6b9943f` · 37 файлів (34 НОВИЙ у `archive/summaries/Lens_gov/` + ARCHIVE_INDEX · INDEX · CHERGA) · PLAN-ID `4d22b7` · read-back 37/37 |
| 3 · правки | ARCHIVE_INDEX: секція `Lens_gov/` 39 рядків (закрито безрядковий `governance_E`) · INDEX §5 governance → `GC3_PUSH_ARCHIV` · INDEX §8 тригер: самері → `archive/summaries/` (синхр. з `gov 1.14`) · CHERGA `IDX-12` стиснуто, `IDX-13` новий, 7 993 B |
| скрипт | `gc3_step1_archive_v1.py` (md5 `62df63db`): повтор no-op, md5 ARCHIVE_INDEX `f413a886` · INDEX `1bfa488d` · CHERGA `756f2258` |

## §2 Вироки / факти сесії

Нових правил wsd не народилось. Народився один борг — `IDX-13`; рядок у CHERGA — покажчик, повний текст тут (14.29).

**`IDX-13` — повний текст.** `Lens_ARCHIVE_INDEX` розійшовся з деревом `archive/`, а гейти не бачать межі архіву.
- §2 оголошує `summaries/` «плоско, без підтек»; факт — 5 підтек (EquipLens · Lens_gov · QR_Lens · StockCheck · Фармастор).
- Лічильники: summaries 89 / stands 28 / superseded 7; факт 128 / 4 / 5. «Разом: 113» не перераховано.
- `governance_A–D` названі без `Lens_gov/` — raw за індексом дає 404.
- §3 «не архівувати те, на що посилається живий канон» ⟂ CHERGA `G16-1`/`Г-13` посилаються на GC2a, який заархівовано. Розведено рядком в ARCHIVE_INDEX (рівень 3 драбини §8); саме правило §3 не уточнене.
- **G3 обходить `archive/`**: `_FMAP` рекурсивний, назви звіряє лише з `Lens_INDEX` → архівні `.md`-не-самері дають ✗ «не названий». Клас уже був у базі (`Drive_Lens_concept_v1/_1_2` · `KPI_Lens_categories` · `Lens_iOS_cookbook.md`). **G10** групує самері за префіксом разом з архівними.
- Умова закриття: індекс = `git ls-files archive/`; §3 уточнено; G3/G10 не рахують `archive/` (або рахують проти ARCHIVE_INDEX), `--inject` в обидва боки (12.12).

**Дельта `--gov` архіву** (база `6b9943f` ✓10 ⚠38 ✗87 → ✓10 ⚠39 ✗93):

| дельта | гейт | причина |
|---|---|---|
| ✗ +7 | G3 | 7 архівних текстів `.md` не названі в `Lens_INDEX` (сліпота до `archive/`) |
| ✗ −1 | G10 | два фантоми GA/GB3 → один GC3 (самері живе в Project, `1.14`) |
| ⚠ +1 | G10 | група `Lens_governance`: 7 архівних самері без живого |

**Чому архів з текстами, ціною ✗+7.** 6 архівних скриптів (`ga_step2` · `gb2_step1B1/B2` · `gb3_step1A/B/C`) читають ці `.md` — без них пакет не відтворює стан.

**Збій у ході, виправлено.** Перший прогін скрипта впав на стелі CHERGA (8 087 B) після того, як уже записав копії, ARCHIVE_INDEX та INDEX: скрипт не атомарний. Відкат `git checkout` + `clean`, `IDX-13` скорочено, перевірку стелі перенесено до запису CHERGA.

**Факти про інструменти.** Незавторизований `api.github.com` повернув помилку замість коміту (ймовірно ліміт) — перевірку батька робити з токеном у заголовку. `git pull` у клоні зі змінами завис на 300 с — брати свіжий `clone` з `timeout`. Claude не має інструмента запису в Project knowledge; `/mnt/project` — копія лише для читання.

## §6 Стартове повідомлення (G-D)
```
Мова — українська. Lens governance · G-D · злиття cookbook-буфера (17, A105 готовий).
Самері — Lens_governance_session_summary_GC3_PUSH_ARCHIV.md (§0) + пілот Claude Docs: https://claude.ai/code/artifact/dce094ad-cfa7-4d6a-975c-c34fd691d59e
Оператора за ПК не питати (делеговано).
Крок 0: відкрити документ-пілот за посиланням і звітувати, чи прочитався (§0 п.3) · свіжий clone main = 73ff3e4 (з timeout) · --gov ✓10 ⚠39 ✗93.
Старт: Lens_INDEX · Lens_governance_CHERGA.md цілком · Lens_governance_protocol.md точково · Lens_cookbook_INDEX · буфер cookbook цілком.
⚠ Буфери і канон читати без head/tail (12.19); якорі — repr() (12.19-б); стелю CHERGA перевіряти до запису.
```
