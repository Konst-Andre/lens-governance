#!/usr/bin/env bash
# frame_check — чи адаптоване репо під каркас Claude Code (детектор «репо не адаптоване», ідея Konst 04.10.2026).
#
# живе доки: Konst працює з Claude Code і каркасом `tools/claude-code/`. Ролі й теки — таблиця «три шляхи» в `ADOPT.md`;
# змінилась таблиця — правиться тут тим самим комітом.
#
# Запуск:  bash tools/claude-code/frame_check.sh <тека репо> [<тека> …]     (з кореня ядра або будь-звідки)
#          bash tools/claude-code/frame_check.sh --inject                   (перевірка детектора: копія без CLAUDE.md → мусить бути ⚠)
# Вивід:   ✓ <репо> — каркас на місці  |  ⚠ <репо> не адаптоване: бракує … → ADOPT
# Вихід:   0 — усі на місці; 1 — комусь бракує (env_check друкує, але не падає через чужий репо).
# Нічого не пише. Мережі нема.
set -u

LENS_PRODUCTS=" EquipLens stock-check QR-Lens Drive-Lens PharmaLens KPI-Lens "   # реєстр — kernel/Lens_INDEX.md §5

check() {
  local d="${1%/}" n miss=() kind
  n=$(basename "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || echo "$d")")
  [ -f "$d/CLAUDE.md" ] || { echo "⚠ $n не адаптоване: нема CLAUDE.md → ADOPT (lens-governance:tools/claude-code/ADOPT.md)"; return 1; }
  if grep -q 'основна робота — у Project' "$d/CLAUDE.md"; then echo "✓ $n — шлях В (міст): лише CLAUDE.md, так і треба"; return 0; fi
  if [ -f "$d/kernel/Lens_INDEX.md" ]; then kind="ядро"
    for p in tools/env_check.sh .claude/hooks/session-start.sh tools/claude-code/audit_prompts.sh kernel/Lens_AUDIT.md \
             kernel/Lens_governance_CHERGA.md sessions/Lens_gov; do [ -e "$d/$p" ] || miss+=("$p"); done
  elif [ -d "$d/lens" ] || [[ "$LENS_PRODUCTS" == *" $n "* ]]; then kind="продукт Lens (Р-7)"
    for p in tools/env_check.sh .claude/hooks/session-start.sh tools/audit_prompts.sh sessions; do [ -e "$d/$p" ] || miss+=("$p"); done
    for g in '_CHERGA.md' '_INDEX.md' '_AUDIT.md'; do ls "$d"/lens/*"$g" >/dev/null 2>&1 || miss+=("lens/<Продукт>$g"); done
  else kind="не-Lens"
    for p in tools/env_check.sh .claude/hooks/session-start.sh tools/audit_prompts.sh docs/CHERGA.md docs/DECISIONS.md \
             docs/ARCHITECTURE.md docs/REPO_LAYOUT.md docs/AUDIT.md docs/summary; do [ -e "$d/$p" ] || miss+=("$p"); done
  fi
  if [ ${#miss[@]} -eq 0 ]; then echo "✓ $n — каркас на місці ($kind)"; return 0; fi
  local list; list=$(printf ' · %s' "${miss[@]}"); echo "⚠ $n не адаптоване ($kind): бракує ${list# · } → ADOPT (lens-governance:tools/claude-code/ADOPT.md)"; return 1
}

if [ "${1:-}" = "--inject" ]; then
  t=$(mktemp -d); mkdir -p "$t/repo/docs/summary" "$t/repo/tools" "$t/repo/.claude/hooks"
  for p in tools/env_check.sh .claude/hooks/session-start.sh tools/audit_prompts.sh docs/CHERGA.md docs/DECISIONS.md \
           docs/ARCHITECTURE.md docs/REPO_LAYOUT.md docs/AUDIT.md; do : > "$t/repo/$p"; done
  echo x > "$t/repo/CLAUDE.md"; full=$(check "$t/repo"); rc_full=$?
  rm "$t/repo/CLAUDE.md";     gone=$(check "$t/repo"); rc_gone=$?
  echo x > "$t/repo/CLAUDE.md"; rm "$t/repo/docs/AUDIT.md"; part=$(check "$t/repo"); rc_part=$?
  rm -rf "$t"
  ok=0; [ $rc_full -eq 0 ] || ok=1; [ $rc_gone -eq 1 ] || ok=1; [ $rc_part -eq 1 ] && [[ "$part" == *docs/AUDIT.md* ]] || ok=1
  [ $ok -eq 0 ] && echo "✓ inject: повний — ✓, без CLAUDE.md — ⚠, без docs/AUDIT.md — ⚠ з назвою" || echo "✗ inject: детектор сліпий ($full | $gone | $part)"
  exit $ok
fi

[ $# -ge 1 ] || { echo "вкажіть теку репо (або --inject)"; exit 2; }
rc=0; for d in "$@"; do check "$d" || rc=1; done; exit $rc
