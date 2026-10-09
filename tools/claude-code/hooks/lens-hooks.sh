#!/bin/bash
# живе доки: гачки Lens вмикаються через налаштування користувача (tools/claude-code/CLAUDE_CODE.md «Гачки»).
# Диспетчер: setup script середовища вказує лише на цей файл — на ВСІ потрібні події, без фільтра інструментів (v2, HOOK-4, 09.10.2026).
# Новий гачок — рядок тут (подія → файл, фільтр інструмента — тут же), setup script Konst більше не чіпає.
# Аргумент — подія (у setup script v2) або старе ім'я v1 (pre · post · stop — середовища з текстом 08.10 працюють і далі):
#   pre  | PreToolUse          — лише Write|Edit|Bash: гачки по черзі, перший з відповіддю (deny/ask) перемагає; огляд UI до коміту (ui-review-gate, HOOK-2 п.4); нагадування (review-remind stand) — останнім
#   post | PostToolUse         — лише Read|Bash|Grep: позначки (ui-guard mark) + нагадування після коміту з UI (review-remind post)
#   stop | Stop                — гачок пам'яті (memory-guard, HOOK-3)
#   UserPromptSubmit           — перевірка пам'яті перед переїздом (handoff-remind, HOOK-3.2): лише на слово-тригер (перевіряє Python: grep -i на кирилиці залежить від локалі; ~50 мс раз на повідомлення)
#   SessionStart · PostToolUseFailure · SubagentStop · PreCompact · SessionEnd — поки без гачків: вихід одразу
# Ціна: подія без гачка й інструмент поза фільтром — лише bash, без Python (заміряно 09.10: ~2 мс; з гачками — ~140 мс, як і в v1).
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
  stop)
    printf '%s' "$in" | bash "$h/memory-guard.sh" stop 2>/dev/null ;;
  prompt)
    printf '%s' "$in" | bash "$h/handoff-remind.sh" 2>/dev/null ;;
esac
exit 0
