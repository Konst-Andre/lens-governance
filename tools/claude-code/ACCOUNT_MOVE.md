# Переїзд на інший акаунт Claude — що перенести

> живе доки: Konst працює з кількох акаунтів Claude (основний · резервний — коли закінчились тижневі ліміти). Дім — ядро: стосується всіх проєктів.
> **Тригер для агента:** Konst пише «новий акаунт», «інший акаунт», «резервний акаунт», «переїжджаємо на акаунт» → агент **сам** диктує список нижче, позначаючи, що вже є, а чого бракує (слово Konst 10.10.2026: «щоб я не пам'ятав — ти одразу кажеш, що треба»).
> Записано 10.10.2026 (QR-Lens CC-6); перевіряти на першому реальному переїзді й поправити тут.

## Що переїжджає саме (нічого робити не треба)

Усе, що в репо: правила (`CLAUDE.md` ядра й проєктів), профіль (канонічна копія — `tools/claude-code/PROFILE.md`), гачки й `ui_lint`, кукбук, черги, самері, брифи, журнали. Новий акаунт бачить їх, щойно бачить репо.

## Що зробити руками на новому акаунті — один раз

| # | що | де | звідки взяти |
|---|---|---|---|
| 1 | **Профіль** — вставити | claude.ai → Settings → Profile (поле «personal preferences») | `lens-governance:tools/claude-code/PROFILE.md` (копія для вставки) |
| 2 | **GitHub** — під'єднати акаунт і Claude GitHub App до репо `Konst-Andre/*` | claude.ai → Settings → Connectors → GitHub; встановлення App — github.com/apps/claude | список репо — `kernel/Lens_INDEX.md` §5 |
| 3 | **Середовище Claude Code** (хмарне) — створити одне на всі проєкти | меню середовища в шапці сесії → New / Edit | — |
| 3а | · setup script **v3** (гачки) | Edit → Setup script | `lens-governance:tools/claude-code/CLAUDE_CODE.md` розділ «Гачки», блок «Гачки Lens v3» |
| 3б | · секрети: `CLOUDFLARE_API_TOKEN` · `CLOUDFLARE_ACCOUNT_ID` · `GH_TOKEN` | Edit → змінні / Network secrets | значення — у Konst (у репо їх нема і не буде) |
| 3в | · мережа: доступ до GitHub, Cloudflare API, npm/PyPI | Edit → Network | як у середовищі старого акаунта |
| 4 | **Конектори** (MCP): «Lens GitHub» — URL з ключем `https://lens-gh.konstandre.workers.dev/mcp/<ключ>`; Cloudflare Developer Platform | claude.ai → Settings → Connectors → Add custom connector | ключ — у налаштуваннях конектора старого акаунта; деталі — `tools/lens-gh/README.md` |
| 5 | **Project «Lens PWA»** (якщо працюєш у чаті claude.ai, не лише в Claude Code) — створити й вставити інструкцію | claude.ai → Projects | `kernel/Lens_PROJECT_instruction.md` |

## Перевірка, що все на місці (агент, перша сесія на новому акаунті)

- `bash tools/env_check.sh` у репо проєкту → рядок `env:` — `github=200` · `cloudflare` · `CLOUDFLARE_API_TOKEN=так` · `GH_TOKEN=так`;
- гачки живі: `ls ~/.claude/settings.json` і `bash <ядро>/tools/claude-code/hooks/handoff-remind.sh selftest`;
- конектори: виклик `gh_list` («Lens GitHub») відповідає.

## Чого НЕ робити

- Не переносити токени через чат, скриншот чи репо — лише в поле секретів середовища (засвітився → заміна).
- Не створювати друге середовище «про всяк випадок» — розійдуться копії setup script і секретів (`CLAUDE_CODE.md`, «Середовища»).
