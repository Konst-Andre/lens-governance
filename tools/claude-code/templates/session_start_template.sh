#!/bin/bash
# <Продукт> · старт хмарної сесії Claude Code: інструменти для гейтів.
# живе доки: гейти з CLAUDE.md потребують цих інструментів. Змінив гейт чи версію — правиш цей файл ТИМ САМИМ комітом.
# Класти в .claude/hooks/session-start.sh; реєстрація — .claude/settings.json:
#   {"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"}]}]}}
# Синхронно: сесія чекає, доки все встановиться (без гонки «гейт раніше за пакет»). Ідемпотентно.
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then exit 0; fi

# <приклади — лишити потрібне>
# pip install -q "playwright==1.56.0"                       # версія під браузер /opt/pw-browsers
# npm install -q --no-save --prefix "$HOME/.deps" jsdom      # + NODE_PATH нижче
# npx --yes wrangler@4 --version >/dev/null 2>&1 || true     # кеш wrangler
# (cd worker && npm install)                                  # залежності воркера

# [ -n "${CLAUDE_ENV_FILE:-}" ] && echo "export NODE_PATH=\"$HOME/.deps/node_modules\"" >> "$CLAUDE_ENV_FILE"
echo "session-start: <що встановлено>"
