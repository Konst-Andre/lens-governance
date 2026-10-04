#!/bin/bash
# lens-governance (ядро) · старт хмарної сесії Claude Code: env_check ядра — його вивід агент бачить першим (каркас кожного репо сесії, гейт, черга, Cloudflare).
# живе доки: існує tools/env_check.sh. Інструментів ставити не треба (гейт ядра — stdlib Python). Зразок — tools/claude-code/templates/session_start_template.sh.
# У сесії з кількома репо, що стартує не з кореня ядра, хук може не спрацювати (AE, 02.10) — тоді CLAUDE.md, «Старт»: `bash tools/env_check.sh` руками.
# Сесію не блокує: завжди exit 0; «✗» і «⚠» у виводі — сказати Konst першим рядком звіту.
set -u
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then exit 0; fi
echo "session-start (ядро): env_check"
bash "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}/tools/env_check.sh" 2>&1 || echo "env_check: exit $? — розібратись до роботи"
exit 0
