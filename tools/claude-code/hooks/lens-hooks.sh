#!/bin/bash
# живе доки: гачки Lens вмикаються через налаштування користувача (tools/claude-code/CLAUDE_CODE.md «Гачки»).
# Диспетчер: setup script середовища вказує лише на цей файл — на ВСІ потрібні події, без фільтра інструментів (v2, HOOK-4, 09.10.2026).
# Новий гачок на одну з 9 подій — рядок тут (подія → файл, фільтр інструмента — тут же), setup script не чіпати; нова подія поза 9 — тоді й setup script.
# Аргумент — подія (setup script v2 і v3) або старе ім'я v1 (pre · post · stop — середовища з текстом 08.10 працюють і далі):
#   pre  | PreToolUse          — лише Write|Edit|Bash: гачки по черзі, перший з відповіддю (deny/ask) перемагає; огляд UI до коміту (ui-review-gate, HOOK-2 п.4); нагадування (review-remind stand) — останнім
#   post | PostToolUse         — лише Read|Bash|Grep|WebSearch|WebFetch: позначки (ui-guard mark: кукбук і пошук ззовні) + нагадування після коміту з UI (review-remind post)
#   stop | Stop                — гачок пам'яті (memory-guard, HOOK-3), далі перевірка перед переїздом, коли його оголошує агент (handoff-remind stop, HOOK-3.2), далі «план без світу» (plan-web, HOOK-2.5)
#   UserPromptSubmit           — перевірка пам'яті перед переїздом (handoff-remind, HOOK-3.2), інакше «пропуск, знайдений Konst» (konst-miss, HOOK-5): лише на слово-тригер (перевіряє Python: grep -i на кирилиці залежить від локалі; ~50 мс раз на повідомлення)
#   SessionStart · PostToolUseFailure · SubagentStop · PreCompact · SessionEnd — поки без гачків: вихід одразу
# Ціна: подія без гачка й інструмент поза фільтром — лише bash, без Python (заміряно 09.10: подія без гачка ~6 мс, інструмент поза фільтром ~13 мс; повний ланцюг ~140 мс — як у CLAUDE_CODE.md).
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ev="$1"
case "$ev" in pre|PreToolUse) ev=pre;; post|PostToolUse) ev=post;; stop|Stop) ev=stop;; UserPromptSubmit) ev=prompt;; *) exit 0;; esac
in="$(cat)"
tool="$(printf '%s' "$in" | grep -o '"tool_name" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
sid="$(printf '%s' "$in" | grep -o '"session_id" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' | tr -cd 'A-Za-z0-9_-')"
# журнал спрацювань (HOOK-5, 10.10.2026): кожна відповідь гачка — рядок у /tmp/lens-hooks-<сесія>.tsv (час · подія · гачок · суть);
# на переїзді handoff_check рахує їх і вимагає вердикти в tools/claude-code/hooks/HOOK_JOURNAL.md (справжнє · хибне · дубль · пропуск)
fire() {   # $1 — гачок, $2 — його вивід (не порожній)
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$ev" "$1" "$(printf '%s' "$2" | tr '\n\t' '  ' | sed 's/"permissionDecisionReason": *"//;s/"reason": *"//;s/"additionalContext": *"//' | cut -c1-200)" >> "/tmp/lens-hooks-${sid:-nosession}.tsv" 2>/dev/null
  printf '%s\n' "$2"
}
run() { out="$(printf '%s' "$in" | bash "$h/$1" $2 2>/dev/null)"; [ -n "$out" ] && { fire "${1%.sh}" "$out"; return 0; }; return 1; }
case "$ev" in
  pre)
    case "$tool" in Write|Edit|Bash) ;; *) exit 0;; esac
    for g in "ui-guard.sh check" "commit-gate.sh" "ui-review-gate.sh gate" "review-remind.sh stand"; do
      read -r f a <<<"$g"
      run "$f" "$a" && exit 0
    done ;;
  post)
    case "$tool" in Read|Bash|Grep|WebSearch|WebFetch) ;; *) exit 0;; esac
    printf '%s' "$in" | bash "$h/ui-guard.sh" mark 2>/dev/null
    run review-remind.sh post ;;
  stop)   # перший з відповіддю перемагає: гачок пам'яті, перевірка перед переїздом (HOOK-3.2), «план без світу» (HOOK-2.5)
    run memory-guard.sh stop || run handoff-remind.sh stop || run plan-web.sh stop ;;
  prompt)   # перевірка перед переїздом (HOOK-3.2), інакше — «пропуск, знайдений Konst» (HOOK-5)
    run handoff-remind.sh "" || run konst-miss.sh "" ;;
esac
exit 0
