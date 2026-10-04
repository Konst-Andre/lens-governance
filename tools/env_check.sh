#!/usr/bin/env bash
# lens-governance (ядро) — перевірка середовища на старті сесії ядра: база · гейт · ручні завантаження · аудит · черга · каркас репо сесії · Cloudflare.
# живе доки: існує ядро (перший крок сесії ядра — CLAUDE.md, «Старт»; хук `.claude/hooks/session-start.sh` викликає його сам).
# ⚠ Змінив гейт, журнал аудиту, чергу чи `frame_check` — правиш цей файл ТИМ САМИМ комітом.
# Зразок — tools/claude-code/templates/env_check_template.sh. Значення змінних НЕ друкуються ніколи. Нічого не пише.
# Вихід: 1 — розібратись до роботи (мережа, гейт ✗, файл-«404»); ⚠ без exit 1 — сказати Konst першим рядком звіту.
set -u
cd "$(dirname "$0")/.."
code() { curl -sS -m 10 -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || true; }
rc=0

# база
git fetch -q origin main 2>/dev/null || true
echo "база: $(git branch --show-current) HEAD $(git rev-parse --short HEAD) · origin/main $(git rev-parse --short origin/main 2>/dev/null) (main попереду на $(git rev-list --count HEAD..origin/main 2>/dev/null))"

# мережа · змінні · гейт · аудит
g=$(code https://api.github.com/); c=$(code https://api.cloudflare.com/client/v4/)
vars=""; for v in CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID GH_TOKEN; do [ -n "${!v:-}" ] && vars+="$v=так " || vars+="$v=ні "; done
gate=$(python3 kernel/Lens_validate.py --gov . 2>&1 | tail -1 | sed 's/─//g; s/^ *//; s/ *$//')
x=$(echo "$gate" | grep -oE '✗ [0-9]+' | grep -oE '[0-9]+'); [ "${x:-1}" -gt 0 ] && { gate="$gate ← ✗ > 0, розібратись"; rc=1; }
last=$(grep -m1 -oE "^\| 20[0-9]{2}-[0-9]{2}-[0-9]{2}" kernel/Lens_AUDIT.md 2>/dev/null | tr -d '| ')
if [ -n "$last" ]; then days=$(( ( $(date +%s) - $(date -d "$last" +%s) ) / 86400 )); [ "$days" -gt 30 ] && aud="аудит правил: $days дн. — ПОРА" || aud="аудит правил: $days дн. тому"; else aud="аудит правил: журналу нема"; fi
echo "env: github=${g:-000} cloudflare=${c:-000} · ${vars% } · гейт --gov: $gate · $aud"

# ручні завантаження (Konst 04.10: «рідко, але буває») — тіло-«404» замість файла (так зламався модуль, MOD-1) · ім'я з пробілом
f404=$(git grep -l -E '^(404: Not Found|404 Not Found)$' -- . 2>/dev/null | tr '\n' ' ')
spc=$(git ls-files | grep ' ' | grep -v '^archive/' | tr '\n' ';')
[ -n "$f404" ] && { echo "✗ файл-«404» замість вмісту: $f404— відновити з історії git"; rc=1; }
[ -n "$spc" ] && echo "⚠ ім'я з пробілом (ручне завантаження?): ${spc%;} — перейменувати через _"
[ -z "$f404$spc" ] && echo "файли: ✓ тіл-«404» нема · імен із пробілом нема"

# черга ядра — відкриті рядки й вік (CQ-1: стеля — кількість і вік, не байти)
python3 - <<'PY'
import re, datetime
t = open('kernel/Lens_governance_CHERGA.md', encoding='utf-8').read()
sec = t.split('## Відкрите', 1)[1].split('\n-----', 1)[0]
rows = [l for l in sec.splitlines() if l.startswith('| `') and '| закрито |' not in l]
today = datetime.date.today(); ages = []
for l in rows:
    m = re.search(r'\| (\d{2})\.(\d{2})\.(\d{4}) \|', l)
    if m: ages.append(((today - datetime.date(int(m[3]), int(m[2]), int(m[1]))).days, l.split('`')[1]))
old = sorted([a for a in ages if a[0] > 30], reverse=True)
print(f"черга ядра: відкритих {len(rows)}" + (f" · старші за 30 дн.: {len(old)} (найстаріший {old[0][1]} — {old[0][0]} дн.)" if old else " · старших за 30 дн. нема"))
PY

# каркас Claude Code — кожне репо сесії (сусідні теки з .git), включно з ядром
for d in ../*/; do [ -d "$d/.git" ] && bash tools/claude-code/frame_check.sh "$d"; done

# Cloudflare — СПІЛЬНИЙ акаунт усіх проєктів (tools/cloudflare/CLOUDFLARE.md). Лише читає; без токена — рядок «—».
[ -f tools/cloudflare/cf_budget.sh ] && bash tools/cloudflare/cf_budget.sh || echo "cloudflare: — (cf_budget.sh нема)"

[ "${g:-000}" = "000" ] && rc=1
exit $rc
