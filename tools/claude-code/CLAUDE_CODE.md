# Claude Code — каркас для всіх репо Konst (вхід)

> живе доки: Konst працює з Claude Code. Змінилась практика — правиться тут або в `REPO_FRAME.md` (подвійний аудит перед комітом); репо підтягують при наступному тригері аудиту.
> дім: `lens-governance:tools/claude-code/` · народився: AE-Simulator S88, 02.10.2026 (AE — приватне, інші сесії його не бачать, тому зразок тут, у публічному ядрі)

**Навіщо.** Профіль Konst приходить у кожну сесію, а файли — ні. Практика, народжена в одному репо, іншим невідома. Тут — один
каркас: як влаштувати репо, щоб агент Claude Code працював, пам'ятав між сесіями й не губив знахідки. Інший репо бере звідси,
читає й будує своє — з адаптацією.

## Що тут лежить

| файл | що | коли читати |
|---|---|---|
| `tools/claude-code/REPO_FRAME.md` | **каркас**: принципи · як агент пам'ятає · розкладка тек · документи і ролі · куди записувати · цикл сесії · перевірки · прод · анти-приклади · адаптація · джерела | заводиш або переводиш репо — цілком; далі точково |
| `tools/claude-code/PROFILE.md` | **профіль Konst** — канонічна копія (у налаштуваннях акаунта — копія для вставки) | правиш профіль |
| `tools/claude-code/templates/` | шаблони: `CLAUDE_template.md` · `REPO_LAYOUT_template.md` · `CHERGA_template.md` · `DECISIONS_template.md` · `ARCHITECTURE_template.md` · `SUMMARY_template.md` · `AUDIT_template.md` · `env_check_template.sh` · `session_start_template.sh` | створюєш файл, якого бракує |
| `tools/claude-code/audit_prompts.sh` | подвійний `/doctor prompt-audit` (sonnet + opus high; `AUDIT_THIRD=fable`; «`.`» — увесь репо) | копіювати в `tools/` репо як є |

Живі зразки: `AirLens` (воркер + Mini App, документація в `docs/`), `AE-Simulator` (сайт на Cloudflare Pages у `site/`, редактор через воркер).

## Як користуватись

**Нове репо.** Прочитати `tools/claude-code/REPO_FRAME.md` → створити з шаблонів `CLAUDE.md`, `docs/REPO_LAYOUT.md`, `docs/CHERGA.md`, `docs/DECISIONS.md`,
`docs/ARCHITECTURE.md`, `docs/AUDIT.md`, `tools/env_check.sh`, `tools/audit_prompts.sh`, хук старту → перший подвійний аудит `CLAUDE.md` → коміт.

**Наявне репо (Claude Code).** Звірити з чеклістом нижче; чого бракує — сказати Konst, запропонувати окремим ходом, створити після «так».
Наявне не переписувати заради шаблону: шаблон — форма, зміст — від репо.

**Репо з claude.ai Project.** Розвідка (хто що читає, за яким шляхом; греп перед «не потрібно») → питання Konst → діагноз і план
малими кроками (кожен — коміт із перевіркою, що прод живий) → переїзд на гілці → перегляд → злиття. Зразок — самері `AE-Simulator` S88.
Поле Instructions у Project → покажчик на `CLAUDE.md` або видалити.

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

## Практики коротко (повний текст — `PROFILE.md`, будова — `REPO_FRAME.md`)

- **Модель і контекст — заміряні:** `get_session` (без `session_id`) → `session_context.model` · `effort_level` · `external_metadata.context_usage`.
- **Інша модель — названа наперед:** `claude -p` чи субагент — рядок у чаті до запуску (модель · effort · навіщо), `--model` явно (CLI в контейнері за замовчуванням — Sonnet, 02.10.2026).
- **Effort:** medium; high — на підказку агента лише на справжній вилці чи незворотному / прод-кроці; перемикає Konst; на Opus 5.5 / Sonnet 5.5 / Fable 5.1 з підпискою кеш не скидається.
- **Аудит правил:** змінив інструкції — перед комітом дві моделі; нова модель Claude — усі; раз на 30 днів. Лише підтверджене, після «так»; правки за аудитом повторно не аудитуються.
