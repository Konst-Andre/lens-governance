#!/usr/bin/env bash
# frame_init — закласти каркас Claude Code у нове не-Lens репо одним ходом (FAB-1, 10.11.2026).
# Запуск:  bash <ядро>/tools/claude-code/frame_init.sh <тека репо> "<Продукт>"
# живе доки: нові репо Konst заводяться під каркас Claude Code (tools/claude-code/REPO_FRAME.md). Продукт Lens (Р-7: lens/, sessions/) — не вміє, свідомо.
# Нічого не перезаписує: наявний файл — «є, пропущено». Наприкінці — перелік незаповнених <…> і frame_check.
# Зуби: bash frame_init.sh selftest — порожня тека → 10 файлів, хук виконуваний і зареєстрований; вдруге — нічого не перезаписано.
set -euo pipefail
if [ "${1:-}" = selftest ]; then
  t=$(mktemp -d); mkdir "$t/r"; git -C "$t/r" init -q; bad=0; me="${BASH_SOURCE[0]}"
  o1="$(bash "$me" "$t/r" "Демо" 2>&1)"; n=$(printf '%s\n' "$o1" | grep -c '^створено: ')
  [ "$n" -eq 10 ] && echo "✓ порожня тека → створено 10 файлів" || { echo "✗ створено $n, чекали 10"; bad=1; }
  [ -x "$t/r/.claude/hooks/session-start.sh" ] && grep -q 'session-start.sh' "$t/r/.claude/settings.json" && echo "✓ хук виконуваний і зареєстрований" || { echo "✗ хук не виконуваний або не зареєстрований"; bad=1; }
  grep -q '^# Демо — як працюємо' "$t/r/CLAUDE.md" && ! grep -q '<дд.мм.рррр>' "$t/r/docs/CHERGA.md" && echo "✓ назву продукту й дату підставлено" || { echo "✗ підстановка не спрацювала"; bad=1; }
  case "$o1" in *"не заповнено"*) echo "✓ frame_check після закладки нагадує заповнити шаблон";; *) echo "✗ frame_check не нагадав про незаповнений шаблон"; bad=1;; esac
  echo "своє" > "$t/r/CLAUDE.md"; o2="$(bash "$me" "$t/r" "Демо" 2>&1)"
  [ "$(cat "$t/r/CLAUDE.md")" = "своє" ] && ! printf '%s\n' "$o2" | grep -q '^створено: ' && echo "✓ повторний запуск нічого не перезаписав" || { echo "✗ повторний запуск щось перезаписав"; bad=1; }
  rm -rf "$t"; exit $bad
fi
R="${1:?тека репо}"; P="${2:?назва продукту}"; K="$(cd "$(dirname "$0")" && pwd)"; T="$K/templates"; D="$(date +%d.%m.%Y)"
put() {   # $1 — шаблон, $2 — ціль
  [ -e "$R/$2" ] && { echo "є, пропущено: $2"; return 0; }
  mkdir -p "$(dirname "$R/$2")"
  sed -e "s/<Продукт>/$P/g" -e "s/<дд\.мм\.рррр>/$D/g" "$T/$1" > "$R/$2"; echo "створено: $2"
}
put CLAUDE_template.md            CLAUDE.md
put REPO_LAYOUT_template.md       docs/REPO_LAYOUT.md
put CHERGA_template.md            docs/CHERGA.md
put DECISIONS_template.md         docs/DECISIONS.md
put ARCHITECTURE_template.md      docs/ARCHITECTURE.md
put AUDIT_template.md             docs/AUDIT.md
put env_check_template.sh         tools/env_check.sh
put session_start_template.sh     .claude/hooks/session-start.sh
[ -e "$R/tools/audit_prompts.sh" ] || { cp "$K/audit_prompts.sh" "$R/tools/audit_prompts.sh"; echo "створено: tools/audit_prompts.sh (копія ядра як є)"; }
mkdir -p "$R/docs/summary" "$R/archive"; [ -n "$(ls -A "$R/docs/summary")" ] || : > "$R/docs/summary/.gitkeep"
[ -e "$R/.claude/settings.json" ] || { printf '%s\n' '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"}]}]}}' > "$R/.claude/settings.json"; echo "створено: .claude/settings.json (реєстрація хука старту)"; }
chmod +x "$R/.claude/hooks/session-start.sh" "$R/tools/env_check.sh"
echo "— заповнити <…> (що лишилось порожнім):"; grep -rc '<[^<>|]\{2,\}>' "$R/CLAUDE.md" "$R/docs" "$R/tools/env_check.sh" 2>/dev/null | grep -v ':0$' | sed 's/^/   /' || true
echo "— frame_check (⚠ «шаблон не заповнено» — очікувано, доки не заповниш <…> у CLAUDE.md):"; bash "$K/frame_check.sh" "$R" || true
