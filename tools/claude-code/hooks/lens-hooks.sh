#!/bin/bash
# живе доки: гачки Lens вмикаються через налаштування користувача (tools/claude-code/CLAUDE_CODE.md «Гачки»).
# Диспетчер: setup script середовища вказує лише на цей файл; новий гачок — рядок тут, без правки середовища Konst.
#   pre  — PreToolUse: гачки по черзі, перший з відповіддю (deny/ask) перемагає; нагадування (review-remind stand) — останнім, щоб не глушити заборони
#   post — PostToolUse: позначки (ui-guard mark) + нагадування після коміту з UI (review-remind post)
#   stop — Stop (кінець ходу): гачок пам'яті (memory-guard, HOOK-3) — рішення Konst без коміту → агент продовжує
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
in="$(cat)"
case "$1" in
  pre)
    for g in "ui-guard.sh check" "commit-gate.sh" "review-remind.sh stand"; do
      read -r f a <<<"$g"
      out="$(printf '%s' "$in" | bash "$h/$f" $a 2>/dev/null)"
      [ -n "$out" ] && { printf '%s\n' "$out"; exit 0; }
    done ;;
  post)
    printf '%s' "$in" | bash "$h/ui-guard.sh" mark 2>/dev/null
    printf '%s' "$in" | bash "$h/review-remind.sh" post 2>/dev/null ;;
  stop)
    printf '%s' "$in" | bash "$h/memory-guard.sh" stop 2>/dev/null ;;
esac
exit 0
