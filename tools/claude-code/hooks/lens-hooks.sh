#!/bin/bash
# живе доки: гачки Lens вмикаються через налаштування користувача (tools/claude-code/CLAUDE_CODE.md «Гачки»).
# Диспетчер: setup script середовища вказує лише на цей файл; новий гачок — рядок тут, без правки середовища Konst.
#   pre  — PreToolUse: гачки по черзі, перший з відповіддю (deny/ask) перемагає
#   post — PostToolUse: позначки (ui-guard mark)
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
in="$(cat)"
case "$1" in
  pre)
    for g in "ui-guard.sh check" "commit-gate.sh"; do
      read -r f a <<<"$g"
      out="$(printf '%s' "$in" | bash "$h/$f" $a 2>/dev/null)"
      [ -n "$out" ] && { printf '%s\n' "$out"; exit 0; }
    done ;;
  post)
    printf '%s' "$in" | bash "$h/ui-guard.sh" mark 2>/dev/null ;;
esac
exit 0
