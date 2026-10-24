#!/bin/bash
# <Продукт> · старт хмарної сесії Claude Code: інструменти для гейтів.
# живе доки: гейти з CLAUDE.md потребують цих інструментів. Змінив гейт чи версію — правиш цей файл ТИМ САМИМ комітом.
# Класти в .claude/hooks/session-start.sh; реєстрація — .claude/settings.json:
#   {"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"}]}]}}
# Синхронно: сесія чекає, доки все встановиться (без гонки «гейт раніше за пакет»). Ідемпотентно.
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then exit 0; fi

# <приклади — лишити потрібне>
# Python-Playwright — версія ПАКЕТА задає ревізію браузера; образ кладе в /opt/pw-browsers лише свою → бери пару образу, не число
#   (AE S103, 24.10.2026: зашите 1.56.0 після оновлення образу шукало chromium-1194, а був 1243 — усі Python-гейти падали за 1 с):
# PWV=$(python3 -c "import json;print(json.load(open('/opt/node-tools/node_modules/playwright/package.json'))['version'])" 2>/dev/null || true)
# [ -n "$PWV" ] && { python3 -c "import importlib.metadata as m,sys; sys.exit(m.version('playwright')!='$PWV')" 2>/dev/null || pip install -q "playwright==$PWV"; }
#   + у env_check продукту — рядок «браузер»: справжній chromium.launch() (≈ 1 с), ✗ → ⚠ на старті (зразок — AE-Simulator:tools/env_check.sh)
# npm install -q --no-save --prefix "$HOME/.deps" jsdom      # + NODE_PATH нижче
# npx --yes wrangler@4 --version >/dev/null 2>&1 || true     # кеш wrangler
# (cd worker && npm install)                                  # залежності воркера

# [ -n "${CLAUDE_ENV_FILE:-}" ] && echo "export NODE_PATH=\"$HOME/.deps/node_modules\"" >> "$CLAUDE_ENV_FILE"
echo "session-start: <що встановлено>"
