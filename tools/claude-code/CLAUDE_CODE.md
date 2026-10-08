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
| `tools/claude-code/audit_prompts.sh` | `/doctor prompt-audit` за класом правки (1 — opus high · 2 — + sonnet high; проходи по черзі, вартість у виводі; `AUDIT_THIRD=fable` — лише за словом Konst; «`.`» — увесь репо — прибрано, `AUD-2`) | копіювати в `tools/` репо як є |
| `tools/claude-code/hooks/` | **гачки** (08.10.2026): диспетчер `lens-hooks.sh` · `ui-guard.sh` «UI без кукбука — не пиши» (`HOOK-1`) · `commit-gate.sh` «коміт → спершу гейт» (`HOOK-2`). Вмикання — розділ «Гачки» нижче | ставиш гачки в середовище · додаєш новий гачок |
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

## Гачки — правила, які тримає програма, а не пам'ять моделі (`HOOK-1`, `HOOK-2`; заміряно 08.10.2026)

**Навіщо.** Профіль і `CLAUDE.md` — текст: модель може «забути» (QR-Lens CC-2: сторінку звіту зробили без кукбука; коміт пішов з ✗ гейта). Гачок запускає **сам Claude Code** — модель його не обійде. **Коли правило стає гачком:** помилка дорога **і** її видно машинно (шлях файла, команда, вміст). «Прочитай X перед Y» без машинної ознаки — не гачок, а текст (інакше шум). Кожен гачок — мікроскоп + зуби (імітації stdin) + живий тест у сесії.

| гачок | подія | що робить |
|---|---|---|
| `hooks/ui-guard.sh` | Pre `Write\|Edit\|Bash` · Post `Read\|Bash\|Grep` | запис `.html`/`.css` (і через Bash) без звернення до індексу кукбука в цій сесії → відмова з причиною; раз на сесію (`HOOK-1`) |
| `hooks/commit-gate.sh` | Pre `Bash` | `git commit` → гейт ядра для кожного репо коміту (ядро `--gov` · продукт Lens `--product` · інше — тиша), ✗ → відмова з рядками ✗; ~1 с (`HOOK-2` п.1) |
| `hooks/lens-hooks.sh` | — | **диспетчер**: setup script вказує лише на нього; новий гачок = рядок тут, середовище Konst не чіпає |

- **Де діють.** Claude Code бере гачки з налаштувань **кореня сесії** і користувача (`~/.claude/settings.json`). У хмарній сесії з кількох репо корінь — `/home/user`, тож `.claude/settings.json` **репо не вантажиться** (і його `SessionStart` теж — звідси «у сесії з кількома репо — руками»). Налаштування користувача й кореня Claude Code підхоплює й посеред сесії (живі тести CC-2: HTML до індексу → відмова, після → дозвіл; коміт із підкинутим ✗ → відмова).
- **Як увімкнути назавжди** — setup script середовища (меню середовища → Edit → Setup script; поле «runs when a new session starts, before Claude Code launches»), разово; текст **остаточний** — нові гачки додаються в диспетчер ядра:

```bash
# Гачки Lens — диспетчер ядра lens-governance/tools/claude-code/hooks/lens-hooks.sh (нові гачки — там, середовище не чіпати)
mkdir -p ~/.claude
cat > ~/.claude/settings.json <<'JSON'
{"hooks":{"PreToolUse":[{"matcher":"Write|Edit|Bash","hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f pre || true"}]}],"PostToolUse":[{"matcher":"Read|Bash|Grep","hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f post || true"}]}]}}
JSON
```

- **Ядра в сесії нема** — диспетчера нема → гачки мовчать (`|| true`), сесії не заважають.
- **Гачок судить стан до команди.** `commit-gate` ганяє гейт **перед** усією Bash-командою: правка + коміт в одній команді → гейт бачить стан без правки й зупиняє (QR CC-2, 08.10: рядок в індексі дописувався в тій самій команді). Правки — однією командою, коміт — наступною.
- **Агент сам у налаштування поза репо не пише** — захист Claude Code («самозміна») блокує; лише з явним дозволом Konst на цей крок (08.10 так і було).
- **Середовища.** Хмарне середовище — це налаштування контейнера (мережа, секрети, змінні, setup script); репо обираються в кожній сесії окремо. Тож **одного середовища вистачає на всі проєкти Lens**; окреме — лише коли проєкту потрібні інші секрети чи мережа. Кілька однакових середовищ = кілька копій setup script і змінних, які розходяться. Секрети — у **Network secrets** (сесія викликає API, не бачачи значення), де це підходить; значення токена на скриншот чи в чат не потрапляє — засвітився → заміна.

## Практики коротко (правила — `PROFILE.md`, будова — `REPO_FRAME.md`; тут — і практики, яких там нема)

- **Репо в сесії:** `CLAUDE.md` кожного підключеного репо вантажиться в контекст щосесії, решта файлів — лише коли їх читають; бракує репо — `add_repo` посеред сесії (якщо доступ є) або нова сесія з ним (перевірено 04.10, AirLens S12). Репо лише для грепу — клон без `register_repo_root`: його `CLAUDE.md` тоді не вантажиться (04.10, ревізія ядра). Підключати лише потрібні.
- **Видалити гілку на GitHub:** `git push origin --delete <гілка>` через git-проксі хмарної сесії → 403 (заміряно 08.10.2026, QR CC-3; push гілок проходить, видалення — ні) → конектор `Lens_GitHub` `gh_branch` (`action: delete`, `repo: Konst-Andre/<репо>`, `expected_head` = sha гілки). Перед видаленням — гілка ⊂ `main` (`git merge-base --is-ancestor <sha> origin/main`); і перевірити `git ls-remote` після: вивід команди з `&&`/`||` бреше, коли `grep` ковтає помилку.
- **Модель і контекст — заміряні:** `get_session` (без `session_id`) → `session_context.model` · `effort_level` · `external_metadata.context_usage`.
- **Інша модель — названа наперед:** `claude -p` чи субагент — рядок у чаті до запуску (модель · effort · навіщо), `--model` явно (CLI в контейнері за замовчуванням — Sonnet, 02.10.2026).
- **Effort:** medium; high — на підказку агента лише на справжній вилці чи незворотному / прод-кроці; перемикає Konst; на Opus 5.5 / Sonnet 5.5 / Fable 5.1 з підпискою кеш не скидається (`REPO_FRAME.md` §11, джерело Anthropic 02.10.2026).
- **Аудит правил:** змінив інструкції — перед комітом дві моделі; нова модель Claude — аудит усіх інструкцій репо; раз на 30 днів. Лише підтверджене, після «так»; правки за аудитом повторно не аудитуються.
