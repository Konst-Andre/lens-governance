# Claude Code — каркас для всіх репо Konst (вхід)

> живе доки: Konst працює з Claude Code. Змінилась практика — правиться тут або в `REPO_FRAME.md` (аудит за класом, пакетом — `tools/claude-code/templates/AUDIT_template.md` «Коли і скільки»); репо підтягують при наступному тригері аудиту.
> дім: `lens-governance:tools/claude-code/` · народився: AE-Simulator S88, 02.10.2026 (AE — приватне, інші сесії його не бачать, тому зразок тут, у публічному ядрі)

**Навіщо.** Профіль Konst приходить у кожну сесію, а файли — ні. Практика, народжена в одному репо, іншим невідома. Тут — один
каркас: як влаштувати репо, щоб агент Claude Code працював, пам'ятав між сесіями й не губив знахідки. Інший репо бере звідси,
читає й будує своє — з адаптацією.

## Що тут лежить

| файл | що | коли читати |
|---|---|---|
| `tools/claude-code/REPO_FRAME.md` | **каркас**: принципи · як агент пам'ятає · розкладка тек · документи і ролі · куди записувати · цикл сесії · перевірки · прод · анти-приклади · адаптація · джерела | заводиш або переводиш репо — цілком; далі точково |
| `tools/claude-code/ADOPT.md` | **адаптація наявного репо**: фраза запуску для Konst · шляхи А звірка / Б переїзд / В міст · етапи 0–7 · **приймання** (як довести, що нічого не зламано і пам'ять працює) · відповідність ролей для продуктів Lens (Р-7) | переводиш наявне репо — цілком |
| `tools/claude-code/ADOPTIONS.md` | журнал адаптацій: який репо, яким шляхом, тест «нова сесія без чату», що в каркасі неясно → що виправлено; черга репо | закриваєш адаптацію; правиш каркас |
| `tools/claude-code/PROFILE.md` | **профіль Konst** — канонічна копія (у налаштуваннях акаунта — копія для вставки) | правиш профіль |
| `tools/claude-code/templates/` | шаблони: `CLAUDE_template.md` · `REPO_LAYOUT_template.md` · `CHERGA_template.md` · `DECISIONS_template.md` · `ARCHITECTURE_template.md` · `SUMMARY_template.md` · `AUDIT_template.md` · `env_check_template.sh` · `session_start_template.sh` | створюєш файл, якого бракує |
| `tools/claude-code/audit_prompts.sh` | `/doctor prompt-audit` за класом правки (1 — opus high · 2 — + sonnet high; проходи по черзі, вартість у виводі; `AUDIT_THIRD=fable` — лише за словом Konst; приймає лише файли, не теки) | копіювати в `tools/` репо як є |
| `tools/claude-code/hooks/` | **гачки** — перелік, події й зуби: розділ «Гачки» нижче (диспетчер `lens-hooks.sh` + гачки, які він кличе) | ставиш гачки в середовище · додаєш новий гачок |
| `tools/claude-code/handoff_check.py` | перевірка пам'яті перед переїздом (живе самері, шляхи, описи, незбережене) — кличе гачок `handoff-remind.sh`; руками — `python3 <ядро>/tools/claude-code/handoff_check.py <тека>` | перед переїздом у нову сесію |
| `tools/claude-code/ui_lint.mjs` | машинна частина огляду UI (Playwright, 390 px, обидві теми, кожен `--state`): обрізаний текст · прилипання до краю картки · накладання · контраст 4,5:1 · тап 24/44 px · поле < 16 px (iOS-зум) · дрібний текст · скрол убік · нерівний ряд · сміття й жаргон у тексті · помилки JS; `--repo` → позначка для воріт; `<repo>/.ui-lint-accept` — прийняті Konst вади з причиною; зуби `selftest` 9/9 | перед комітом UI — вимагають ворота `ui-review-gate` |
| `tools/claude-code/MODELS.md` | моделі Claude у роботі Konst: яка де, холодний старт, еталон самері | обираєш модель для `claude -p` чи субагента |
| `tools/claude-code/frame_check.sh` | детектор «репо не адаптоване під каркас»: чого бракує за ролями `ADOPT.md` (ядро · продукт Lens · не-Lens · шлях В); `--inject` — перевірка самого детектора | запускає `env_check` ядра по кожному репо сесії; руками — `bash <ядро>/tools/claude-code/frame_check.sh <тека>` |

Поруч — `tools/cloudflare/` (`CLOUDFLARE.md` правила й бюджет спільного акаунта · `cf_budget.sh` замір для `env_check`): потрібен
кожному репо, що живе на Cloudflare.

Живі зразки: `AirLens` (воркер + Mini App, документація в `docs/`), `AE-Simulator` (сайт на Cloudflare Pages у `site/`, редактор через воркер).

## Як користуватись

**Нове репо.** Прочитати `tools/claude-code/REPO_FRAME.md` → створити з шаблонів `CLAUDE.md`, `docs/REPO_LAYOUT.md`, `docs/CHERGA.md`, `docs/DECISIONS.md`,
`docs/ARCHITECTURE.md`, `docs/AUDIT.md`, `tools/env_check.sh`, `tools/audit_prompts.sh`, хук старту → перший аудит `CLAUDE.md` (клас 2: opus high + sonnet) → коміт.

**Наявне репо** (з Claude Code чи з claude.ai Project) — процедура `tools/claude-code/ADOPT.md`. Konst вставляє в сесію репо одне речення:
```text
Адаптуй цей репо під каркас Claude Code за процедурою Konst-Andre/lens-governance, tools/claude-code/ADOPT.md (прочитай цілком). Етапи по черзі; до етапу 4 нічого не змінюй.
```

## Чекліст репо

| є? | файл | зразок |
|---|---|---|
| ☐ | `CLAUDE.md` (≤ ~200 рядків) | `templates/CLAUDE_template.md` |
| ☐ | `docs/REPO_LAYOUT.md` | `templates/REPO_LAYOUT_template.md` |
| ☐ | `docs/CHERGA.md` | `templates/CHERGA_template.md` |
| ☐ | `docs/DECISIONS.md` | `templates/DECISIONS_template.md` |
| ☐ | `docs/ARCHITECTURE.md` | `templates/ARCHITECTURE_template.md` |
| ☐ | `docs/AUDIT.md` | `templates/AUDIT_template.md` |
| ☐ | `docs/summary/<Продукт>_SUMMARY_<дата>.md` | `templates/SUMMARY_template.md` |
| ☐ | `tools/env_check.sh` (з нагадуванням про аудит) | `templates/env_check_template.sh` |
| ☐ | `tools/audit_prompts.sh` | `audit_prompts.sh` (як є) |
| ☐ | `.claude/hooks/session-start.sh` + `.claude/settings.json` | `templates/session_start_template.sh` · skill `session-start-hook` |
| ☐ | тека публікації окремо від службового | `REPO_FRAME.md` §3 |

## Гачки — правила, які тримає програма, а не пам'ять моделі (`HOOK-1`, `HOOK-2`, `ARCH-1` (д); заміряно 08.10.2026)

**Навіщо.** Профіль і `CLAUDE.md` — текст: модель може «забути» (QR-Lens CC-2: сторінку звіту зробили без кукбука; коміт пішов з ✗ гейта). Гачок запускає **сам Claude Code** — модель його не обійде. **Коли правило стає гачком:** помилка дорога **і** її видно машинно (шлях файла, команда, вміст). «Прочитай X перед Y» без машинної ознаки — не гачок, а текст (інакше шум). Кожен гачок — мікроскоп + зуби (імітації stdin) + живий тест у сесії.

| гачок | подія | що робить |
|---|---|---|
| `hooks/ui-guard.sh` | Pre `Write\|Edit\|Bash` · Post `Read\|Bash\|Grep` | запис `.html`/`.css` без **кукбука і пошуку ззовні** (WebSearch/WebFetch, з 10.10.2026 — правило профілю «ПІДСИЛЕННЯ ІНТЕРНЕТОМ» модель пропускала) (і через Bash) без звернення до індексу кукбука в цій сесії → відмова з причиною; раз на сесію (`HOOK-1`) |
| `hooks/commit-gate.sh` | Pre `Bash` | `git commit` → гейт ядра для кожного репо коміту (ядро `--gov` · продукт Lens `--product` · інше — тиша), ✗ → відмова з рядками ✗; ~1 с (`HOOK-2` п.1) |
| `hooks/ui-review-gate.sh` | Pre `Bash` (після `commit-gate`) | **огляд UI до коміту** (`HOOK-2` п.4, урок QR CC-5 09.10.2026): `git commit` у репо, де змінено `.html`/`.htm`/`.css` (проти HEAD + нові файли), а позначки огляду **саме цього диффу** нема → відмова з чек-листом (дія → результат · реальні кінці джерела в моках · кроп 1:1 кожного нового елемента · вага кнопок · теми · wsd 3.9). Позначка: `bash <ядро>/tools/claude-code/hooks/ui-review-gate.sh done "<що переглянуто>"` з теки репо (рядок ≥ 40 знаків); нова правка UI → новий дифф → знову відмова. **`done` приймається лише після `ui_lint` на цьому диффі з ✗ 0** (або `--no-lint "<причина ≥ 30 знаків>"` — сторінку не запустити; причина пишеться в позначку; бриф §HOOK-2.5, 10.10.2026). Діє в усіх репо з гачками ядра. Зуби: `selftest` 13/13 (і через справжній stdin — heredoc скрипта займає stdin, JSON гачка читати в bash; + сітка `review-remind post`) |
| `hooks/review-remind.sh` | Post `Read\|Bash\|Grep` · Pre `Write\|Edit\|Bash` (останнім) | **нагадування, не заборона** (`ARCH-1` (ґ)(д), 08.10.2026): щойно зроблений `git commit` змінив `.html`/`.css`, а позначки огляду `ui-review-gate` на ці файли за 2 год нема → «коміт UI обійшов огляд» + чек-лист (**страхувальна сітка** до воріт `ui-review-gate`: є позначка — тиша, без дубля; 09.10.2026, Konst: «об'єднати правильно»; раз на SHA; коміт старший за 2 хв — тиша); запис `.html` зі «стенд / bench / harness / компер» у шляху, а `kernel/Lens_stagebench_manifest.md` у сесії не відкривали → нагадування про маніфест (раз на сесію). Формат — `hookSpecificOutput.additionalContext`, текст фактами; **Pre без `permissionDecision` доходить до агента — перевірено наживо (QR CC-3)** |
| `hooks/memory-guard.sh` | Stop | **гачок пам'яті** (`HOOK-3`, 08.10.2026, урок QR CC-4): в останньому повідомленні Konst слова-рішення («так», «дозволяю», «згоден», «рішення»…), а в ході нема коміту (`git commit` · `gh_commit` · `push_files`) → `decision: block` з причиною: агент записує в репо або одним рядком пояснює, чому нічого. Раз на хід (`stop_hook_active`). Зуби: `bash memory-guard.sh selftest` 6/6 + живий журнал QR CC-4 (хід без коміту → block, наступний з комітом → тиша) |
| `hooks/handoff-remind.sh` + `handoff_check.py` | UserPromptSubmit · Stop | **перевірка пам'яті перед переїздом** (`HOOK-3.2`, 09.10.2026, урок QR CC-5: ручний прохід знайшов застарілий §0, голі назви файлів ядра, протухлий README — жоден гейт їх не ловив). **Коли:** у повідомленні Konst «переїжджаємо» · «переїзд» · «переїхати» · «стартове повідомлення» · «нова / нову сесію» (не «в новій сесії» — розповідь) → `additionalContext`; або переїзд оголошує **агент** (у відповіді стартове ```text чи «переїжджаємо») і є ✗ → Stop `decision: block`. **Що:** `handoff_check.py` на кожне репо `/home/user/*` з `sessions/`: живе самері (§0 і стартове є · не відстає від комітів сесії) · шляхи в §0, стартовому й «Коротко» плану живі, голі назви — ✗ · «цей коміт» у §0 — ⚠ · гейт · **описи відстали** (код, змінений комітами сесії, згадують `.md`, яких сесія не міняла — README · ARCHITECTURE · план · INDEX… — ⚠; README — лише один з описів, уточнення Konst 09.10) · **незбережене** (незакомічене · HEAD нема на GitHub — ✗; лише в гілці сесії — ⓘ) + чек-лист «очима нового агента» (а–д). Тиша — перше повідомлення сесії, повтор без нових комітів. Руками: `python3 tools/claude-code/handoff_check.py <тека>`. Зуби: `handoff_check.py selftest` 11/11 · `handoff-remind.sh selftest` 9/9 · через диспетчер наживо (UserPromptSubmit ~0,9 с; Stop → block на справжньому незакоміченому) |
| `hooks/lens-hooks.sh` | — | **диспетчер**: setup script вказує лише на нього; новий гачок = рядок тут. **Setup script (v2 і v3, `HOOK-4`):** setup script реєструє 9 подій (SessionStart · UserPromptSubmit · PreToolUse · PostToolUse · PostToolUseFailure · Stop · SubagentStop · PreCompact · SessionEnd) без фільтра інструментів; фільтр — у диспетчері (bash, до Python): подія без гачка ~6 мс, інструмент поза фільтром ~13 мс, повний ланцюг ~140 мс (заміряно). Старі імена `pre · post · stop` працюють. Новий гачок = рядок у диспетчері; нова подія поза цими 9 — єдиний випадок, коли знову треба setup script |

- **Де діють.** Claude Code бере гачки з налаштувань **кореня сесії** і користувача (`~/.claude/settings.json`). У хмарній сесії з кількох репо корінь — `/home/user`, тож `.claude/settings.json` **репо не вантажиться** (і його `SessionStart` теж — звідси «у сесії з кількома репо — руками»). Налаштування користувача й кореня Claude Code підхоплює й посеред сесії (живі тести CC-2: HTML до індексу → відмова, після → дозвіл; коміт із підкинутим ✗ → відмова).
- **Як увімкнути назавжди** — setup script середовища (меню середовища → Edit → Setup script; поле «runs when a new session starts, before Claude Code launches»), разово; текст **v3** (запасне місце ядра — `/tmp/lens-governance`); нові гачки додаються в диспетчер ядра, setup script не чіпати:

```bash
# Гачки Lens v3 (09.10.2026): 9 подій → диспетчер ядра; ядро — серед репо сесії або в /tmp/lens-governance (гачки діють і в сесії лише з продуктом)
[ -d /home/user/lens-governance ] || [ -d /tmp/lens-governance ] || git clone -q --depth 1 https://github.com/Konst-Andre/lens-governance /tmp/lens-governance || true
mkdir -p ~/.claude
cat > ~/.claude/settings.json <<'JSON'
{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f SessionStart || true"}]}],"UserPromptSubmit":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f UserPromptSubmit || true"}]}],"PreToolUse":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PreToolUse || true"}]}],"PostToolUse":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PostToolUse || true"}]}],"PostToolUseFailure":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PostToolUseFailure || true"}]}],"Stop":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f Stop || true"}]}],"SubagentStop":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f SubagentStop || true"}]}],"PreCompact":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PreCompact || true"}]}],"SessionEnd":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f SessionEnd || true"}]}]}}
JSON
```

- **Ядра серед репо сесії нема** (сесія лише з продуктом) — **v3** (09.10.2026, питання Konst «гачки діють і без ядра?»): setup script сам клонує публічне ядро в `/tmp/lens-governance` (якщо нема й там), команди гачків шукають диспетчер у `/home/user/lens-governance`, потім у `/tmp/…`. Перевірено: клон із підміненими шляхами → диспетчер із запасного місця, `ui-review-gate selftest` 9/9, `memory-guard` 6/6 звідти. Нема мережі / GitHub — `|| true`, сесії не заважає. **Середовище без setup script v3 (лише v2 чи нічого) — у сесії без ядра гачки мовчать.** `CLAUDE.md` продукту гачків не вмикає й не вимикає — їх вмикає середовище.
- **Гачок судить стан до команди.** `commit-gate` ганяє гейт **перед** усією Bash-командою: правка + коміт в одній команді → гейт бачить стан без правки й зупиняє (QR CC-2, 08.10: рядок в індексі дописувався в тій самій команді). Правки — однією командою, коміт — наступною.
- **Агент сам у налаштування поза репо не пише** — захист Claude Code («самозміна») блокує; лише з явним дозволом Konst на цей крок (08.10 так і було).
- **Середовища.** Хмарне середовище — це налаштування контейнера (мережа, секрети, змінні, setup script); репо обираються в кожній сесії окремо. Тож **одного середовища вистачає на всі проєкти Lens**; окреме — лише коли проєкту потрібні інші секрети чи мережа. Кілька однакових середовищ = кілька копій setup script і змінних, які розходяться. Секрети — у **Network secrets** (сесія викликає API, не бачачи значення), де це підходить; значення токена на скриншот чи в чат не потрапляє — засвітився → заміна.

## Практики коротко (правила — `PROFILE.md`, будова — `REPO_FRAME.md`; тут — і практики, яких там нема)

- **Репо в сесії:** `CLAUDE.md` кожного підключеного репо вантажиться в контекст щосесії, решта файлів — лише коли їх читають; бракує репо — `add_repo` посеред сесії (якщо доступ є) або нова сесія з ним (перевірено 04.10, AirLens S12). Репо лише для грепу — клон без `register_repo_root`: його `CLAUDE.md` тоді не вантажиться (04.10, ревізія ядра). Підключати лише потрібні.
- **Видалити гілку на GitHub:** з хмарної сесії `git push origin --delete` і API `DELETE git/refs` з `GH_TOKEN` → 403 (git-проксі пускає push гілок, не видалення; заміряно 08–09.10.2026). Робочий шлях — конектор «Lens GitHub» `gh_branch` (`action: delete`, `repo: Konst-Andre/<репо>`, `expected_head` — короткий sha з `action: list`). Перед видаленням — API `compare/main...<гілка>` → `ahead_by: 0` (не `git merge-base` у неглибокому клоні: він показує хибні «коміти не в main»); після — `git ls-remote` (вивід команди з `&&`/`||` бреше, коли `grep` ковтає помилку).
- **Модель і контекст — заміряні:** `get_session` (без `session_id`) → `session_context.model` · `effort_level` · `external_metadata.context_usage`.
- **Інша модель — названа наперед:** `claude -p` чи субагент — рядок у чаті до запуску (модель · effort · навіщо), `--model` явно (CLI в контейнері за замовчуванням — Sonnet, 02.10.2026).
- **Effort:** medium; high — на підказку агента лише на справжній вилці чи незворотному / прод-кроці; перемикає Konst; на Opus 5.5 / Sonnet 5.5 / Fable 5.1 з підпискою кеш не скидається (`REPO_FRAME.md` §11, джерело Anthropic 02.10.2026).
- **Аудит правил:** клас правки → проходи, пакетом перед самері; нова модель Claude — лише файли класу 2; раз на 30 днів — `CLAUDE.md` репо (формула — `tools/claude-code/templates/AUDIT_template.md` «Коли і скільки»). Лише підтверджене, після «так»; правки за аудитом повторно не аудитуються.
