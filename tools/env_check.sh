#!/usr/bin/env bash
# lens-governance (ядро) — перевірка середовища на старті сесії ядра: база · гейт · ручні завантаження · аудит · черга · каркас репо сесії · Cloudflare.
# живе доки: існує ядро (перший крок сесії ядра — CLAUDE.md, «Старт»; хук `.claude/hooks/session-start.sh` викликає його сам).
# ⚠ Змінив гейт, журнал аудиту, чергу чи `frame_check` — правиш цей файл ТИМ САМИМ комітом.
# Зразок — tools/claude-code/templates/env_check_template.sh. Значення змінних НЕ друкуються ніколи. Нічого не пише.
# Вихід: 1 — розібратись до роботи (мережа, гейт ✗, файл-«404»); ⚠ без exit 1 — сказати Konst одразу після «що ти побачиш».
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
gout=$(python3 kernel/Lens_validate.py --gov . 2>&1); gate=$(echo "$gout" | tail -1 | sed 's/─//g; s/^ *//; s/ *$//')
# ⚠ гейта — це здоров'я файлів ядра (G5 буфери · G6 обсяг · G7 мертвий буфер · G8 сироти…): назвати, які висять, а не лише число (Konst 10.10, QR CC-7)
gw=$(echo "$gout" | awk '/^\[G[0-9]+\]/{g=$1} /^  ⚠/{c[g]++} END{for(k in c) printf "%s×%d ", k, c[k]}' | tr -d '[]'); [ -n "$gw" ] && gate="$gate (⚠: ${gw% })"
x=$(echo "$gate" | grep -oE '✗ [0-9]+' | grep -oE '[0-9]+'); [ "${x:-1}" -gt 0 ] && { gate="$gate ← ✗ > 0, розібратись"; rc=1; }
last=$(grep -m1 -oE "^\| 20[0-9]{2}-[0-9]{2}-[0-9]{2}" kernel/Lens_AUDIT.md 2>/dev/null | tr -d '| ')
if [ -n "$last" ]; then days=$(( ( $(date +%s) - $(date -d "$last" +%s) ) / 86400 )); [ "$days" -gt 30 ] && aud="аудит правил: $days дн. — ПОРА" || aud="аудит правил: $days дн. тому"; else aud="аудит правил: журналу нема"; fi
# AUD-2 (05.10.2026): борг пакетного аудиту — коміти у файлах інструкцій після дати верхнього рядка журналу (той самий день не видно — прийнято)
INSTR="CLAUDE.md tools/claude-code/PROFILE.md tools/claude-code/REPO_FRAME.md tools/claude-code/ADOPT.md tools/claude-code/CLAUDE_CODE.md tools/claude-code/templates tools/cloudflare/CLOUDFLARE.md kernel/wsd"
[ -n "$last" ] && debt=$(git log --since="$last 23:59:59" --format=%s -- $INSTR 2>/dev/null | grep -vcE 'аудит: клас 0|за аудитом')
[ "${debt:-0}" -gt 0 ] && aud="$aud · ⚠ борг аудиту: $debt коміт(ів) в інструкціях після $last — пакет за класом (tools/claude-code/templates/AUDIT_template.md)"
echo "env: github=${g:-000} cloudflare=${c:-000} · ${vars% } · гейт --gov: $gate · $aud"

# ручні завантаження (Konst 04.10: «рідко, але буває») — тіло-«404» замість файла (так зламався модуль, MOD-1) · ім'я з пробілом
f404=$(git grep -l -E '^(404: Not Found|404 Not Found)$' -- . 2>/dev/null | tr '\n' ' ')
spc=$(git ls-files | grep ' ' | grep -v '^archive/' | tr '\n' ';')
[ -n "$f404" ] && { echo "✗ файл-«404» замість вмісту: $f404— відновити з історії git"; rc=1; }
[ -n "$spc" ] && echo "⚠ ім'я з пробілом (ручне завантаження?): ${spc%;} — перейменувати через _"
[ -z "$f404$spc" ] && echo "файли: ✓ тіл-«404» нема · імен із пробілом нема"

# черга ядра — відкриті рядки й вік (CQ-1: стеля — кількість і вік, не байти)
python3 - <<'PY'
import sys; sys.path.insert(0, 'kernel'); from Lens_validate import queue_open, Q_MAX, Q_AGE
q = queue_open(open('kernel/Lens_governance_CHERGA.md', encoding='utf-8').read())
old = sorted(((a, i) for i, a in q if a is not None and a > Q_AGE), reverse=True)
s = f"черга ядра: відкритих {len(q)} (стеля {Q_MAX})" + (f" · старші за {Q_AGE} дн.: {len(old)} (найстаріший {old[0][1]} — {old[0][0]} дн.)" if old else f" · старших за {Q_AGE} дн. нема")
print(("⚠ " + s + " — спершу виконати, розрізати або відкласти з датою (CQ-1)") if len(q) > Q_MAX or old else s)
PY

# журнал гачків і перевірок — ріст (≤ 30 дн. у §1, ≤ 24 КБ, рядок ≤ 700 знаків; ротація — шапка журналу)
python3 tools/claude-code/handoff_check.py journal

# каркас Claude Code — кожне репо сесії (сусідні теки з .git), включно з ядром
for d in ../*/; do [ -d "$d/.git" ] && bash tools/claude-code/frame_check.sh "$d"; done

# Cloudflare — СПІЛЬНИЙ акаунт усіх проєктів (tools/cloudflare/CLOUDFLARE.md). Лише читає; без токена — рядок «—».
[ -f tools/cloudflare/cf_budget.sh ] && bash tools/cloudflare/cf_budget.sh || echo "cloudflare: — (cf_budget.sh нема)"

[ "${g:-000}" = "000" ] && rc=1
exit $rc
