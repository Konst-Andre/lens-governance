#!/usr/bin/env bash
# <Продукт> — перевірка середовища на старті сесії: база · мережа · змінні · гейти · живий прод.
# живе доки: існує репо (перший крок кожної сесії; див. CLAUDE.md).
# ⚠ Змінив гейт, шлях публікації чи воркера — правиш цей файл ТИМ САМИМ комітом.
# Зразок — lens-governance:tools/claude-code/templates/env_check_template.sh. Значення змінних НЕ друкуються ніколи.
set -u
cd "$(dirname "$0")/.."

# ── налаштувати під репо ──
EXTRA_VARS=""                  # імена змінних середовища через пробіл (значення не друкуються), напр. "GROQ_KEY BOT_TOKEN"
GATE_CMD="echo гейт не задано"
SUMDIR="docs/summary"           # тека самері (продукт Lens — sessions)  # головний гейт; останній рядок виводу — підсумок, напр. "node tools/validate.js"
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

# самері — живий журнал (профіль Konst, САМЕРІ): коміти агента (трейлер Claude-Session) після останнього оновлення самері.
# >0 → попередня сесія комітила, не оновивши самері: звірити git log і дописати §0/§1 ДО роботи. Коміти Konst і ботів не рахуються.
sm=$(git log -1 --format=%h -- "$SUMDIR" 2>/dev/null)
if [ -z "$sm" ]; then echo "самері: — (у $SUMDIR ще нема)"
else n=$(git rev-list --count --grep='Claude-Session' "$sm"..HEAD 2>/dev/null); [ "${n:-0}" -gt 0 ] && echo "⚠ самері відстає: після $sm комітів агента без самері — $n (git log $sm..HEAD)" || echo "самері: ≡ (останнє оновлення $sm)"; fi

# прод (лише читання): <живий код ≡ репо; тека публікації; службове не видно — судити за ВМІСТОМ, не за HTTP-кодом>
echo "прод: — (додати: живий код ≡ репо; тека публікації; службове не видно — за ВМІСТОМ)"

# Cloudflare — СПІЛЬНИЙ акаунт усіх проєктів: бюджет (запити · збірки · прогноз) і свіжість правил. Рядки «⚠» — читати й діяти
# за lens-governance:tools/cloudflare/CLOUDFLARE.md. Скрипт лише читає й завжди exit 0. Репо без Cloudflare — рядок прибрати.
# ⚠ не «curl | bash || echo»: bash на порожньому вході (404) виходить з 0, і збій мовчить
if cfb=$(curl -sSf -m 20 https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/tools/cloudflare/cf_budget.sh 2>/dev/null); then
  printf '%s\n' "$cfb" | bash; else echo "cloudflare: — (cf_budget не завантажено)"; fi

[ "${g:-000}" = "000" ] && exit 1
exit 0
