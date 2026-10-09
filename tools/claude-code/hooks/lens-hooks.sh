#!/bin/bash
# живе доки: гачки Lens вмикаються через налаштування користувача (tools/claude-code/CLAUDE_CODE.md «Гачки»).
# Диспетчер: setup script середовища вказує лише на цей файл — на ВСІ потрібні події, без фільтра інструментів (v2, HOOK-4, 09.10.2026).
# Новий гачок на одну з 9 подій — рядок тут (подія → файл, фільтр інструмента — тут же), setup script не чіпати; нова подія поза 9 — тоді й setup script.
# Аргумент — подія (setup script v2 і v3) або старе ім'я v1 (pre · post · stop — середовища з текстом 08.10 працюють і далі):
#   pre  | PreToolUse          — лише Write|Edit|Bash: гачки по черзі, перший з відповіддю (deny/ask) перемагає; огляд UI до коміту (ui-review-gate, HOOK-2 п.4); нагадування (review-remind stand) — останнім
#   post | PostToolUse         — лише Read|Bash|Grep: позначки (ui-guard mark) + нагадування після коміту з UI (review-remind post)
#   stop | Stop                — гачок пам'яті (memory-guard, HOOK-3), далі перевірка перед переїздом, коли його оголошує агент (handoff-remind stop, HOOK-3.2)
#   UserPromptSubmit           — перевірка пам'яті перед переїздом (handoff-remind, HOOK-3.2): лише на слово-тригер (перевіряє Python: grep -i на кирилиці залежить від локалі; ~50 мс раз на повідомлення)
#   SessionStart · PostToolUseFailure · SubagentStop · PreCompact · SessionEnd — поки без гачків: вихід одразу
# Ціна: подія без гачка й інструмент поза фільтром — лише bash, без Python (заміряно 09.10: подія без гачка ~6 мс, інструмент поза фільтром ~13 мс; повний ланцюг ~140 мс — як у CLAUDE_CODE.md).
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ev="$1"
case "$ev" in pre|PreToolUse) ev=pre;; post|PostToolUse) ev=post;; stop|Stop) ev=stop;; UserPromptSubmit) ev=prompt;; *) exit 0;; esac
in="$(cat)"
tool="$(printf '%s' "$in" | grep -o '"tool_name" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
case "$ev" in
  pre)
    case "$tool" in Write|Edit|Bash) ;; *) exit 0;; esac
    for g in "ui-guard.sh check" "commit-gate.sh" "ui-review-gate.sh gate" "review-remind.sh stand"; do
      read -r f a <<<"$g"
      out="$(printf '%s' "$in" | bash "$h/$f" $a 2>/dev/null)"
      [ -n "$out" ] && { printf '%s\n' "$out"; exit 0; }
    done ;;
  post)
    case "$tool" in Read|Bash|Grep) ;; *) exit 0;; esac
    printf '%s' "$in" | bash "$h/ui-guard.sh" mark 2>/dev/null
    printf '%s' "$in" | bash "$h/review-remind.sh" post 2>/dev/null ;;
  stop)   # перший з відповіддю перемагає: гачок пам'яті, потім перевірка перед переїздом (HOOK-3.2)
    out="$(printf '%s' "$in" | bash "$h/memory-guard.sh" stop 2>/dev/null)"
    [ -n "$out" ] && { printf '%s\n' "$out"; exit 0; }
    printf '%s' "$in" | bash "$h/handoff-remind.sh" stop 2>/dev/null ;;
  prompt)
    printf '%s' "$in" | bash "$h/handoff-remind.sh" 2>/dev/null ;;
esac
exit 0
