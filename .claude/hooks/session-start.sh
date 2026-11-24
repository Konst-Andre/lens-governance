#!/bin/bash
# lens-governance (ядро) · старт хмарної сесії Claude Code: env_check ядра — його вивід агент бачить першим (каркас кожного репо сесії, гейт, черга, Cloudflare).
# живе доки: існує tools/env_check.sh. Гейт ядра — stdlib Python; ставить лише Python-Playwright для приладів з браузером (clip · port_same · pwa_icon · pw_quiet · tester/explore —
#   Konst 24.11.2026: «системне, що по колу із сесії в сесію, — автоматично»). Зразок — tools/claude-code/templates/session_start_template.sh.
# У сесії з кількома репо, що стартує не з кореня ядра, хук може не спрацювати (AE, 02.10) — тоді CLAUDE.md, «Старт»: `bash tools/env_check.sh` руками.
# Сесію не блокує: завжди exit 0; «✗» і «⚠» у виводі — сказати Konst першим рядком звіту.
set -u
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then exit 0; fi
# Python-Playwright — пара до Node-Playwright образу (версія пакета задає ревізію браузера в /opt/pw-browsers; зашите число ламалось — AE S103).
# Є і збігається — нічого; нема — pip (замір 24.11: 5 с); PyPI недосяжний — рядок ⚠, сесія йде далі.
PWV=$(python3 -c "import json;print(json.load(open('/opt/node-tools/node_modules/playwright/package.json'))['version'])" 2>/dev/null || true)
if [ -n "$PWV" ] && ! python3 -c "import importlib.metadata as m,sys; sys.exit(m.version('playwright')!='$PWV')" 2>/dev/null; then
  timeout 90 pip install -q --break-system-packages "playwright==$PWV" >/dev/null 2>&1 && echo "session-start: Python-Playwright $PWV поставлено" || echo "⚠ Python-Playwright $PWV не поставився — прилади з браузером (clip, port_same, pwa_icon) впадуть; руками: pip install playwright==$PWV"
fi
echo "session-start (ядро): env_check"
bash "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}/tools/env_check.sh" 2>&1 || echo "env_check: exit $? — розібратись до роботи"
exit 0
