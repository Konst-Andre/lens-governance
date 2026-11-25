#!/usr/bin/env bash
# <Продукт> — перевірка середовища на старті сесії: база · мережа · змінні · гейти · живий прод.
# живе доки: існує репо (перший крок кожної сесії; див. CLAUDE.md).
# ⚠ Змінив гейт, шлях публікації чи воркера — правиш цей файл ТИМ САМИМ комітом.
# Зразок — lens-governance:tools/claude-code/templates/env_check_template.sh. Значення змінних НЕ друкуються ніколи.
set -u
cd "$(dirname "$0")/.."

# ── налаштувати під репо ──
EXTRA_VARS=""                  # імена змінних середовища через пробіл (значення не друкуються), напр. "GROQ_KEY BOT_TOKEN"
GATE_CMD="echo гейт не задано"  # головний гейт; останній рядок виводу — підсумок, чистий містить «✗ 0» (формат Lens_validate: «ПІДСУМОК: ✓ N · ⚠ N · ✗ N»); інакше exit 1, незаданий теж. Напр. "node tools/validate.js"
SUMDIR="docs/summary"           # тека самері (продукт Lens — sessions)
AUDITF="docs/AUDIT.md"          # журнал аудиту правил (продукт Lens — lens/<Продукт>_AUDIT.md)
code() { curl -sS -m 10 -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || true; }
# WARN-1 (ядро): увесь вивід — через фільтр власників ⚠ ядра (`tools/claude-code/warn_owner.py`, реєстр `tools/claude-code/WARN_OWNERS.md` — рядок з ім'ям репо):
#   ⚠ без власника / прострочене → ✗ і exit 1; прийняте → ⓘ. Себе викликає вдруге з WO_INNER=1. Зуб — ENV_INJECT=1 → «--inject ЗЛОВИВ». Ім'я репо — назва теки клону (basename $PWD) ≡ рядок реєстру.
WK=../lens-governance; [ -d "$WK" ] || WK=/tmp/lens-governance
if [ -z "${WO_INNER:-}" ] && [ -f "$WK/tools/claude-code/warn_owner.py" ]; then
  out="$(WO_INNER=1 bash tools/env_check.sh "$@" 2>&1)"; rc=$?
  printf '%s\n' "$out" | python3 "$WK/tools/claude-code/warn_owner.py" filter "$(basename "$PWD")" --repo . --kernel "$WK" ${ENV_INJECT:+--inject}; wo=$?
  [ "$rc" -ne 0 ] && exit "$rc"; exit "$wo"
fi

# база
git fetch -q origin main 2>/dev/null || true
echo "база: HEAD $(git rev-parse --short HEAD) · origin/main $(git rev-parse --short origin/main 2>/dev/null) (origin/main попереду на $(n=$(git rev-list --count HEAD..origin/main 2>/dev/null); printf %s "${n:-?}"; [ "${n:-0}" != 0 ] && printf " — треба pull"))"

# мережа · змінні · гейти · аудит
g=$(code https://api.github.com/); c=$(code https://api.cloudflare.com/client/v4/)
vars=""; for v in CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID GH_TOKEN $EXTRA_VARS; do [ -n "${!v:-}" ] && vars+="$v=так " || vars+="$v=ні "; done
gout=$(bash -c "$GATE_CMD" 2>&1); gate=$(printf '%s\n' "$gout" | tail -1)
printf '%s\n' "$gout" | awk '/^\[/{h=$0} /^[[:space:]]+⚠/{sub(/^[[:space:]]+/,""); sub(/^⚠ /,""); print "⚠ гейт: " h " — " $0}' | cut -c1-300   # текст ⚠ — окремим рядком (за «⚠ N» підсумку ховався, EquipLens S41)
case "$gate" in *"✗ 0"*) ;; *) fail=1 ;; esac   # ✗ гейта продукту — exit 1
last=$(grep -m1 -oE "^\| 20[0-9]{2}-[0-9]{2}-[0-9]{2}" "$AUDITF" 2>/dev/null | tr -d '| ')
if [ -n "$last" ]; then days=$(( ( $(date +%s) - $(date -d "$last" +%s) ) / 86400 )); [ "$days" -gt 30 ] && aud="аудит правил: $days дн. — ПОРА" || aud="аудит правил: $days дн. тому"; elif grep -qE "^\| [0-9]" "$AUDITF" 2>/dev/null; then aud="⚠ аудит правил: дата верхнього рядка журналу не ISO рррр-мм-дд — нагадування «30 днів» не бачить її (EquipLens S38)"; else aud="аудит правил: журналу нема"; fi
INSTR="CLAUDE.md"                # файли інструкцій репо (skills, профіль у репо — дописати)
# AUD-2 · AUD-4 (19.10.2026): борг пакетного аудиту — коміти в інструкціях ПІСЛЯ останнього коміту журналу аудиту (той самий день теж видно).
# Не борг: позначка «аудит: клас 0» / «за аудитом» у будь-якому рядку повідомлення (будь-який регістр) · межа неглибокого клону — $GIT_DIR/shallow,
# по одному коміту в рядку; без батька її дифф «додає» всі файли (git-scm.com/docs/shallow, 18.10.2026; AE S90 — хибні 22 файли).
# «ПОРА» — ≥ 5 файлів у борзі або найстаріший коміт боргу ≥ 7 дн. (числа — пропозиція AUD-4 08.10, «так» Konst 19.10; переглянути після 2–3 пакетів).
shallow="$(git rev-parse --git-path shallow)"; jc=$(git log -1 --format=%H -- "$AUDITF" 2>/dev/null); debt=0; dfiles=""; oldest=""
[ -n "$jc" ] && for h in $(git rev-list "$jc"..HEAD -- $INSTR 2>/dev/null); do
  grep -qx "$h" "$shallow" 2>/dev/null && continue
  git show -s --format=%B "$h" | grep -qiE 'аудит: клас 0|за аудитом' && continue
  debt=$((debt+1)); dsha="${dsha:-} $h"; dfiles="$dfiles $(git show --name-only --format= "$h" -- $INSTR | tr '\n' ' ')"; oldest=$(git show -s --format=%ct "$h")
done
if [ "$debt" -gt 0 ]; then nf=$(printf '%s\n' $dfiles | sort -u | grep -c .); age=$(( ( $(date +%s) - oldest ) / 86400 ))
  aud="$aud · ⚠ борг аудиту: $debt коміт(ів), $nf файл(ів), найстаріший $age дн."
  ah=$(python3 "${K:-$([ -d ../lens-governance ] && echo ../lens-governance || echo /tmp/lens-governance)}/tools/claude-code/audit_class.py" hint . $dsha 2>/dev/null); [ -n "$ah" ] && aud="$aud · ⓘ $ah"   # кандидат у клас 0 (ядро audit_class, 25.11.2026)
  { [ "$nf" -ge 5 ] || [ "$age" -ge 7 ]; } && aud="$aud — ПОРА пакет за класом (lens-governance:tools/claude-code/templates/AUDIT_template.md)"; fi
echo "env: github=${g:-000} cloudflare=${c:-000} · ${vars% } · гейт: $gate · $aud"
K=../lens-governance; [ -d "$K" ] || K=/tmp/lens-governance; [ -f "$K/tools/claude-code/profile_check.sh" ] && bash "$K/tools/claude-code/profile_check.sh"   # профіль: з репо (LENS_PROFILE=1) чи з налаштувань акаунта — lens-governance:tools/claude-code/ACCOUNT_MOVE.md п.1-а / 1-б

# самері — живий журнал (профіль Konst, САМЕРІ): коміти агента (трейлер Claude-Session) після останнього оновлення самері.
# >0 → попередня сесія комітила, не оновивши самері: звірити git log і дописати §0/§1 ДО роботи. Коміти Konst і ботів не рахуються.
sm=$(git log -1 --format=%h -- "$SUMDIR" 2>/dev/null)
if [ -z "$sm" ]; then echo "самері: — (у $SUMDIR ще нема)"
else n=$(git rev-list --count --grep='Claude-Session' "$sm"..HEAD 2>/dev/null); [ "${n:-0}" -gt 0 ] && echo "⚠ самері відстає: після $sm комітів агента без самері — $n (git log $sm..HEAD)" || echo "самері: ≡ (останнє оновлення $sm)"; fi

# браузер гейтів (wsd 1.21 п.4) — лишити, якщо в репо є прилади Playwright: справжній запуск Chromium з Python і Node; розбіжність пакета й образу
#   видно тут, а не падінням гейтів посеред роботи.
# pyb=$(timeout 60 python3 -c "from playwright.sync_api import sync_playwright as s
# with s() as p: b=p.chromium.launch(); print(b.version.split('.')[0]); b.close()" 2>/dev/null) && pyb="python ✓ $pyb" || pyb="python ✗ — хук старту не поставив пару образу"
# ndb=$(cd /tmp && timeout 60 node -e "import('/opt/node-tools/node_modules/playwright/index.mjs').then(async({chromium})=>{const b=await chromium.launch();console.log(b.version().split('.')[0]);await b.close()})" 2>/dev/null) && ndb="node ✓ $ndb" || ndb="node ✗"
# case "$pyb $ndb" in *✗*) echo "⚠ браузер: $pyb · $ndb";; *) echo "браузер: $pyb · $ndb";; esac

# прод (лише читання): <живий код ≡ репо; тека публікації; службове не видно — судити за ВМІСТОМ, не за HTTP-кодом>
#   GitHub Pages: запит з ?cb=<час> (обхід кешу); розбіжність ≤ 15 хв після коміту в main — ⚠ «кеш Pages», не ✗ (вікно — лише без ENV_INJECT: `&& [ -z "${ENV_INJECT:-}" ]`, інакше глушить зуб) (Cache-Control max-age=600; EquipLens S36, 19.11.2026; зразок — EquipLens:tools/env_check.sh)
echo "прод: — (додати: живий код ≡ репо; тека публікації; службове не видно — за ВМІСТОМ)"

# Спільні інструменти ядра — з КЛОНУ ядра поруч ($K, як профіль вище): виклик, не копія. Клон кладе setup script v3+ (lens-governance:tools/claude-code/CLAUDE_CODE.md «Гачки»); нема клону — рядок «ядра поруч нема»:
# налаштувати середовище, не обходити curl | python з main — виконання віддаленого коду з гілки, auto-режим його відхиляє (lens-governance:tools/claude-code/ADOPTIONS.md, рядок AE 18.10.2026).
CC="$K/tools/claude-code"
# документи — ціна читання в Claude Code (ядро DOC-1: щосесійні ≤ 200 рядків · старт ≤ 25 КБ · розділ ≤ 16 КБ · > 80 КБ з маршрутом); лише ⚠, exit 0
if [ -f "$CC/doc_health.py" ]; then python3 "$CC/doc_health.py" .; else echo "документи: — (ядра поруч нема: $K)"; fi
# прополка закритого (ядро doc_prune, ROT 25.11.2026): на старті лише показує (--dry); прибирає агент у ході коміту — без питання (CLAUDE_CODE.md «Прополка закритого»)
if [ -f "$CC/doc_prune.py" ]; then python3 "$CC/doc_prune.py" . --dry ${ENV_INJECT:+--inject} | sed 's/^прополка \(.*\)прибрано/ⓘ прополка \1прибрано — зроби: python3 $CC\/doc_prune.py . (без питання) ·/'; fi

# примірка — тека <документація>/shots/ (lens-governance:tools/claude-code/SHOTS.md): ✗ знімок без рядка · жива без знімків · файли після «прийнято»; ⚠ вік, вага, без накладки.
# Теки нема — рядок «теки shots/ нема» (продукт без UI-рішень наперед — так і є).
if [ -f "$CC/shots_check.py" ]; then python3 "$CC/shots_check.py" . || fail=1; else echo "примірка: — (ядра поруч нема: $K)"; fi
# версія застосунку B · rev (VER-1, lens-governance:tools/claude-code/VERSIONS.md) — лише репо з інтерфейсом; параметри свого продукту:
#   --code <файл коду застосунку> --re '<мітка: група B, група rev>' [--name '<шлях файлу білда з групою B>']
# if [ -f "$CC/version_check.py" ]; then python3 "$CC/version_check.py" . --code <файл> --re '<регулярка>' ${ENV_INJECT:+--inject} || fail=1; else echo "версія: — (ядра поруч нема: $K)"; fi
# маршрут (ROUTE-1, kernel/Lens_ROUTE-1_brief.md): карта кроків у черзі («… · карта кроків») — route_check; карти нема → «маршрут: карти нема», exit 0.
#   Зразок — EquipLens:tools/env_check.sh (✗ / ⚠ рядками з префіксом «маршрут:», ✗ → fail; зуб ENV_INJECT → --inject two мусить дати ✗).
if [ -f "$CC/route_check.py" ]; then
  if [ -n "${ENV_INJECT:-}" ]; then python3 "$CC/route_check.py" check . --inject two >/dev/null 2>&1 && { echo "✗ маршрут --inject не зловив два ▶"; fail=1; } || echo "маршрут --inject: ЗЛОВИВ"
  else rc_out=$(python3 "$CC/route_check.py" check . 2>&1); rc=$?; printf '%s\n' "$rc_out" | grep -E '^(✗|⚠) ' | sed 's/^/маршрут: /'; printf '%s\n' "$rc_out" | tail -1; [ $rc -ne 0 ] && fail=1; fi
fi
# зуби: ENV_INJECT=1 bash tools/env_check.sh — прилади з --inject підкидають ваду й мусять дати ✗ (зразок — QR-Lens:tools/env_check.sh; аудит 24.10.2026).
# Мітки в коді ще нема — version_check дає ✗: до першої мітки рядок вище лишити закоментованим або вписати echo "⚠ версія: мітки ще нема" (зразок — AE-Simulator:tools/env_check.sh).

# Cloudflare — СПІЛЬНИЙ акаунт усіх проєктів: бюджет (запити · збірки · прогноз) і свіжість правил. Рядки «⚠» — читати й діяти
# за lens-governance:tools/cloudflare/CLOUDFLARE.md. Скрипт лише читає й завжди exit 0. Репо без Cloudflare — прибрати цей рядок, а також c= / cloudflare= у «мережа» і CLOUDFLARE_* у vars вище.
if [ -f "$K/tools/cloudflare/cf_budget.sh" ]; then bash "$K/tools/cloudflare/cf_budget.sh"; else echo "cloudflare: — (ядра поруч нема: $K)"; fi

[ "${g:-000}" = "000" ] && exit 1
[ "${fail:-0}" = 1 ] && exit 1   # fail=1 ставлять гейт, примірка, версія, маршрут — exit 1: розібратись до роботи
exit 0
