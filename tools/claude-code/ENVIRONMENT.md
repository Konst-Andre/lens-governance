# Середовище Claude Code ядра й продуктів Lens — аркуш для відтворення

> живе доки: Konst працює з хмарними сесіями Claude Code. Дім тексту setup script — ЦЕЙ файл (`ENV-1`, ідея Konst 22.10.2026, Routes S1); змінився setup script, змінна чи мережа — правиться тут, тим самим комітом.
> **Секретів тут нема й не буде** — лише імена із заглушками `<…>`. Приватний чи публічний репо — не сейф: історія git зберігає все назавжди.
> **Видача:** Konst пише «дай налаштування середовища» (чи «setup script», «відтворити середовище») → агент видає блоки нижче **цілком** у чат, кожен — окремим code block, з підписом, у яке поле вставляти. Нагадує гачок `tools/claude-code/hooks/env-remind.sh` і додає живу звірку `tools/claude-code/env_drift.py`: агент починає з «що вже ≡ аркушу · чого бракує» і пропонує рівно ті рядки, яких бракує. Щостарту звірка — рядок у `tools/env_check.sh` (⚠ лише при розбіжності); коміт, що змінив цей аркуш, — гачок сам пропонує Konst оновити середовище.

Одне середовище — на ядро й усі продукти Lens (`tools/claude-code/CLAUDE_CODE.md` «Середовища»). **Свідомий виняток — Routes** (22.10.2026): інші гачки й без ключів; його аркуш — `Routes:tools/ENVIRONMENT.md`.

## 1 · Назва і мережа

- **Назва:** `Lens` (будь-яка; вона лише для вибору в меню під полем повідомлення).
- **Мережа:** Trusted, плюс доступ до Cloudflare API, npm і PyPI (`tools/claude-code/ACCOUNT_MOVE.md` п.3в).

## 2 · Змінні середовища (поле «Environment variables», по рядку `НАЗВА=значення`, без лапок)

```text
CLOUDFLARE_API_TOKEN=<токен Cloudflare — у Konst>
CLOUDFLARE_ACCOUNT_ID=<id акаунта Cloudflare — у Konst>
LENS_PROFILE=1
```

- `LENS_PROFILE=1` — профіль з репо (`tools/claude-code/PROFILE.md`) кладе гачок старту. **З 22.10.2026 — і на своєму акаунті** (рішення `ACC-1`, `tools/claude-code/ACCOUNT_MOVE.md`): у полі акаунта тоді лише ядро (6 рядків).
- `GH_TOKEN` руками не ставити: доступ до GitHub дає під'єднаний GitHub (п.3б там же).

## 3 · Setup script (поле «Setup script»), v3

```bash
# Гачки Lens v3 (09.10.2026): 9 подій → диспетчер ядра; ядро — серед репо сесії або в /tmp/lens-governance (гачки діють і в сесії лише з продуктом)
pip install -q shellcheck-py 2>/dev/null || true   # shellcheck для сторожа коміту (commit_files.py п.8), 22.10.2026
[ -d /home/user/lens-governance ] || [ -d /tmp/lens-governance ] || git clone -q --depth 1 https://github.com/Konst-Andre/lens-governance /tmp/lens-governance || true
mkdir -p ~/.claude
cat > ~/.claude/settings.json <<'JSON'
{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f SessionStart || true"}]}],"UserPromptSubmit":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f UserPromptSubmit || true"}]}],"PreToolUse":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PreToolUse || true"}]}],"PostToolUse":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PostToolUse || true"}]}],"PostToolUseFailure":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PostToolUseFailure || true"}]}],"Stop":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f Stop || true"}]}],"SubagentStop":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f SubagentStop || true"}]}],"PreCompact":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f PreCompact || true"}]}],"SessionEnd":[{"hooks":[{"type":"command","command":"f=/home/user/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] || f=/tmp/lens-governance/tools/claude-code/hooks/lens-hooks.sh; [ -f $f ] && bash $f SessionEnd || true"}]}]}}
JSON
```

## 4 · Інструменти, які ставить setup script

- `shellcheck` — сторож коміту перевіряє ним змінені `.sh` (без нього — лише `bash -n`). Звіряє `env_drift.py`.

## Перевірка після відтворення (перша сесія)

`bash tools/env_check.sh` з кореня ядра → рядки `env:` (`CLOUDFLARE_API_TOKEN=так`) і `профіль: з репо (LENS_PROFILE=1) ✓`; `bash tools/claude-code/hooks/lens-hooks.sh profile-test` → 2 × ✓.
