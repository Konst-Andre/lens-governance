#!/usr/bin/env bash
# <Продукт> — перевірка середовища на старті сесії: база · мережа · змінні · гейти · живий прод.
# живе доки: існує репо (перший крок кожної сесії; див. CLAUDE.md).
# ⚠ Змінив гейт, шлях публікації чи воркера — правиш цей файл ТИМ САМИМ комітом.
# Зразок — lens-governance:tools/claude-code/templates/env_check_template.sh. Значення змінних НЕ друкуються ніколи.
set -u
cd "$(dirname "$0")/.."

# ── налаштувати під репо ──
EXTRA_VARS=""                  # імена змінних середовища через пробіл (значення не друкуються), напр. "GROQ_KEY BOT_TOKEN"
GATE_CMD="echo гейт не задано"  # головний гейт; останній рядок виводу — підсумок, напр. "node tools/validate.js"
code() { curl -sS -m 10 -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || true; }

# база
git fetch -q origin main 2>/dev/null || true
echo "база: HEAD $(git rev-parse --short HEAD) · origin/main $(git rev-parse --short origin/main 2>/dev/null) (main попереду на $(git rev-list --count HEAD..origin/main 2>/dev/null))"

# мережа · змінні · гейти · аудит
g=$(code https://api.github.com/); c=$(code https://api.cloudflare.com/client/v4/)
vars=""; for v in CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID GH_TOKEN $EXTRA_VARS; do [ -n "${!v:-}" ] && vars+="$v=так " || vars+="$v=ні "; done
gate=$(bash -c "$GATE_CMD" 2>&1 | tail -1)
last=$(grep -m1 -oE "^\| 20[0-9]{2}-[0-9]{2}-[0-9]{2}" docs/AUDIT.md 2>/dev/null | tr -d '| ')
if [ -n "$last" ]; then days=$(( ( $(date +%s) - $(date -d "$last" +%s) ) / 86400 )); [ "$days" -gt 30 ] && aud="аудит правил: $days дн. — ПОРА" || aud="аудит правил: $days дн. тому"; else aud="аудит правил: журналу нема"; fi
echo "env: github=${g:-000} cloudflare=${c:-000} · ${vars% } · гейт: $gate · $aud"

# прод (лише читання): <живий код ≡ репо; тека публікації; службове не видно — судити за ВМІСТОМ, не за HTTP-кодом>
echo "прод: — (додати: живий код ≡ репо; тека публікації; службове не видно — за ВМІСТОМ)"

[ "${g:-000}" = "000" ] && exit 1
exit 0
