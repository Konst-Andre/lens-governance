#!/bin/bash
# живе доки: гачки Lens вмикаються через налаштування користувача (tools/claude-code/CLAUDE_CODE.md «Гачки»).
# Диспетчер: setup script середовища вказує лише на цей файл — на ВСІ потрібні події, без фільтра інструментів (v2, HOOK-4, 09.10.2026).
# Новий гачок на одну з 9 подій — рядок тут (подія → файл, фільтр інструмента — тут же), setup script не чіпати; нова подія поза 9 — тоді й setup script.
# Аргумент — подія (setup script v2 і v3) або старе ім'я v1 (pre · post · stop — середовища з текстом 08.10 працюють і далі):
#   pre  | PreToolUse          — лише Write|Edit|Bash: бриф лише з шаблону (brief-guard, BRIEF-2); далі гачки по черзі, перший з відповіддю (deny/ask) перемагає; огляд UI до коміту (ui-review-gate, HOOK-2 п.4); нагадування (review-remind stand) — останнім
#   post | PostToolUse         — лише Read|Bash|Grep|WebSearch|WebFetch: позначки (ui-guard mark: кукбук і пошук ззовні) + нагадування після коміту з UI (review-remind post)
#   stop | Stop                — гачок пам'яті (memory-guard, HOOK-3), далі перевірка перед переїздом, коли його оголошує агент (handoff-remind stop, HOOK-3.2), далі «план без світу» (plan-web, HOOK-2.5)
#   UserPromptSubmit           — перевірка пам'яті перед переїздом (handoff-remind, HOOK-3.2), інакше «пропуск, знайдений Konst» (konst-miss, HOOK-5): лише на слово-тригер (перевіряє Python: grep -i на кирилиці залежить від локалі; ~50 мс раз на повідомлення)
#   SessionStart               — профіль Konst з репо (tools/claude-code/PROFILE.md) як контекст сесії, ЛИШЕ коли в середовищі LENS_PROFILE=1: спільний акаунт, де поле
#                                профілю в налаштуваннях бачили б і чужі чати (слово Konst 18.10.2026, QR CC-18; ACCOUNT_MOVE.md п.1-б). Старт і повтор після стиснення (без matcher —
#                                на всі source). Свій акаунт — профіль у налаштуваннях, змінну не ставити (інакше профіль двічі). Зуби: bash lens-hooks.sh profile-test
#   PostToolUseFailure · SubagentStop · PreCompact · SessionEnd — поки без гачків: вихід одразу
# Ціна: подія без гачка й інструмент поза фільтром — лише bash, без Python (заміряно 09.10: подія без гачка ~6 мс, інструмент поза фільтром ~13 мс; повний ланцюг ~140 мс — як у CLAUDE_CODE.md).
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ev="$1"
# Хуки старту репо сесії (AE S90 18.10.2026): у сесії з кількома репо Claude Code бере налаштування лише з кореня (/home/user), і
# <репо>/.claude/hooks/session-start.sh не запускається — інструменти гейтів (Playwright, валідатор) тихо відсутні. Диспетчер кличе їх
# сам: кожен репо, крім свого репо сесії (його кличе Claude Code) і ядра; вивід — у журнал (SessionStart чекає JSON), змінні — через
# CLAUDE_ENV_FILE, як у самих хуків. Зуби — `lens-hooks.sh repo-hooks-test`.
repo_hooks() {
  local root="${LENS_REPOS_ROOT:-/home/user}" k f r; k="$(cd "$h/../../.." && pwd)"
  for f in "$root"/*/.claude/hooks/session-start.sh; do
    [ -f "$f" ] || continue; r="${f%/.claude/hooks/session-start.sh}"
    [ "$r" = "${CLAUDE_PROJECT_DIR:-}" ] || [ "$r" = "$k" ] && continue
    ( cd "$r" && timeout 300 bash "$f" ) >> "${LENS_REPO_HOOKS_LOG:-/tmp/lens-repo-hooks.log}" 2>&1 || echo "$(date +%T) ✗ $f" >> "${LENS_REPO_HOOKS_LOG:-/tmp/lens-repo-hooks.log}"
  done
}
if [ "$ev" = repo-hooks-test ]; then
  t=$(mktemp -d); mkdir -p "$t/a/.claude/hooks" "$t/b/.claude/hooks"
  printf 'echo a >> %s/ran\n' "$t" > "$t/a/.claude/hooks/session-start.sh"; printf 'echo b >> %s/ran\n' "$t" > "$t/b/.claude/hooks/session-start.sh"
  LENS_REPOS_ROOT="$t" CLAUDE_PROJECT_DIR="$t/b" LENS_REPO_HOOKS_LOG="$t/log" repo_hooks
  got="$(cat "$t/ran" 2>/dev/null | tr '\n' ' ')"; rm -rf "$t"
  [ "$got" = "a " ] && { echo "✓ хук репо поза сесією запущено, свій репо сесії — ні"; exit 0; } || { echo "✗ repo_hooks: запущено «$got», чекали «a »"; exit 1; }
fi
if [ "$ev" = SessionStart ] || [ "$ev" = profile-test ]; then
  [ "$ev" = SessionStart ] && repo_hooks
  # профіль — двома частинами ≤ 10 000 знаків кожна (стеля additionalContext Claude Code; понад — лише прев'ю 2 000): 1 — тут, 2 — у перше повідомлення Konst (profile_parts.py)
  prof() { [ "${LENS_PROFILE:-}" = 1 ] && [ -f "$h/../PROFILE.md" ] || return 0
    python3 -c 'import json,sys,subprocess; t=subprocess.run([sys.executable,sys.argv[1],"1"],capture_output=True,text=True).stdout; print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":t}},ensure_ascii=False))' "$h/profile_parts.py"; }
  if [ "$ev" = profile-test ]; then
    on="$(LENS_PROFILE=1 prof)"; off="$(LENS_PROFILE= prof)"; bad=0
    case "$on" in *'"hookEventName": "SessionStart"'*'Частина 1/2'*) echo "✓ LENS_PROFILE=1 → профіль у контексті (частина 1: $(printf '%s' "$on" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]))') знаків)";; *) echo "✗ LENS_PROFILE=1 → профілю нема"; bad=1;; esac
    python3 "$h/profile_parts.py" test | sed 's/^/  /'; [ "${PIPESTATUS[0]}" = 0 ] || bad=1
    [ -z "$off" ] && echo "✓ без LENS_PROFILE → тиша (профіль — у полі налаштувань акаунта)" || { echo "✗ без LENS_PROFILE → профіль усе одно"; bad=1; }
    exit $bad
  fi
  ss_sid="$(cat 2>/dev/null | grep -o '"session_id" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' | tr -cd 'A-Za-z0-9_-')"
  prof; [ "${LENS_PROFILE:-}" = 1 ] && { date +%H:%M > /tmp/lens-profile-loaded; : > "/tmp/lens-profile-part2-${ss_sid:-nosession}"; } 2>/dev/null; exit 0   # позначка для profile_check.sh (рядок «профіль» в env_check)
fi
case "$ev" in pre|PreToolUse) ev=pre;; post|PostToolUse) ev=post;; stop|Stop) ev=stop;; UserPromptSubmit) ev=prompt;; *) exit 0;; esac
in="$(cat)"
tool="$(printf '%s' "$in" | grep -o '"tool_name" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
sid="$(printf '%s' "$in" | grep -o '"session_id" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' | tr -cd 'A-Za-z0-9_-')"
# журнал спрацювань (HOOK-5, 10.10.2026): кожна відповідь гачка — рядок у /tmp/lens-hooks-<сесія>.tsv (час · подія · гачок · суть);
# на переїзді handoff_check рахує їх і вимагає вердикти в tools/claude-code/hooks/HOOK_JOURNAL.md (справжнє · хибне · дубль · пропуск)
fire() {   # $1 — гачок, $2 — його вивід (не порожній)
  # стеля Claude Code: текст гачка понад 10 000 знаків модель бачить лише прев'ю на 2 000 (docs hooks «JSON output», 22.10.2026) → рядок «⚠ стеля» у журнал спрацювань
  n="$(printf '%s' "$2" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); h=d.get("hookSpecificOutput") or {}; print(max(len(str(h.get(k,""))) for k in ("additionalContext","permissionDecisionReason")) if h else len(str(d.get("reason",""))))
except Exception: print(0)' 2>/dev/null)"
  [ "${n:-0}" -gt 10000 ] && printf '%s	%s	%s	%s
' "$(date -u +%FT%TZ)" "$ev" "$1" "⚠ СТЕЛЯ: текст гачка $n знаків > 10 000 — модель бачить лише прев'ю 2 000; розбити (profile_parts.py) або скоротити" >> "/tmp/lens-hooks-${sid:-nosession}.tsv" 2>/dev/null
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$ev" "$1" "$(printf '%s' "$2" | tr '\n\t' '  ' | sed 's/"permissionDecisionReason": *"//;s/"reason": *"//;s/"additionalContext": *"//' | cut -c1-200)" >> "/tmp/lens-hooks-${sid:-nosession}.tsv" 2>/dev/null
  printf '%s\n' "$2"
}
run() { out="$(printf '%s' "$in" | bash "$h/$1" $2 2>/dev/null)"; [ -n "$out" ] && { fire "${1%.sh}" "$out"; return 0; }; return 1; }
case "$ev" in
  pre)
    case "$tool" in Write|Edit|Bash) ;; *) exit 0;; esac
    for g in "brief-guard.sh pre" "ui-guard.sh check" "commit-gate.sh" "ui-review-gate.sh gate" "review-remind.sh stand"; do
      read -r f a <<<"$g"
      run "$f" "$a" && exit 0
    done ;;
  post)
    case "$tool" in Read|Bash|Grep|WebSearch|WebFetch) ;; *) exit 0;; esac
    printf '%s' "$in" | bash "$h/ui-guard.sh" mark 2>/dev/null
    # після коміту — два нагадування можуть збігтись (огляд UI · бриф, BRIEF-2 19.10.2026): одне повідомлення, обидва тексти
    o1="$(printf '%s' "$in" | bash "$h/review-remind.sh" post 2>/dev/null)"; o2="$(printf '%s' "$in" | bash "$h/brief-guard.sh" post 2>/dev/null)"
    [ -n "$o1" ] && [ -z "$o2" ] && fire review-remind "$o1"
    [ -z "$o1" ] && [ -n "$o2" ] && fire brief-guard "$o2"
    [ -n "$o1" ] && [ -n "$o2" ] && fire "review-remind+brief-guard" "$(python3 -c 'import json,sys; a,b=(json.loads(x)["hookSpecificOutput"] for x in sys.argv[1:3]); print(json.dumps({"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":a["additionalContext"]+"\n\n"+b["additionalContext"]}},ensure_ascii=False))' "$o1" "$o2")"
    [ -z "$o1" ] && [ -z "$o2" ] && [ "$tool" = Bash ] && { run handoff-remind.sh post || run env-remind.sh post; } ;;   # + пам'ять після коміту (AE S109): нові ✗ / ⚠ handoff_check   # коміт змінив аркуш середовища → запропонувати оновити (ENV-1)
  stop)   # перший з відповіддю перемагає: гачок пам'яті, перевірка перед переїздом (HOOK-3.2), «план без світу» (HOOK-2.5)
    run memory-guard.sh stop || run handoff-remind.sh stop || run plan-web.sh stop ;;
  prompt)   # перевірка перед переїздом (HOOK-3.2), інакше — аркуш середовища на прохання (ENV-1), інакше — «пропуск, знайдений Konst» (HOOK-5)
    o="$(run handoff-remind.sh "" || run env-remind.sh "" || run konst-miss.sh "")"
    pf="/tmp/lens-profile-part2-${sid:-nosession}"
    if [ "${LENS_PROFILE:-}" = 1 ] && [ -f "$pf" ]; then rm -f "$pf"; python3 "$h/profile_parts.py" 2 | python3 "$h/profile_parts.py" merge "$o"   # частина 2 профілю — у перше повідомлення після старту чи стиснення
    elif [ -n "$o" ]; then printf '%s\n' "$o"; fi ;;
esac
exit 0
