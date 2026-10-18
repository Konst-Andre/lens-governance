#!/bin/bash
# живе доки: профіль Konst може приходити з репо (LENS_PROFILE=1, гачок старту) — tools/claude-code/ACCOUNT_MOVE.md п.1-б. Дім — ядро.
# Один рядок «профіль: …» для env_check ядра й продуктів: звідки профіль у цій сесії і чи він справді є (тиха відсутність — неможлива).
#   LENS_PROFILE=1 → гачок старту встановлено (~/.claude/settings.json → lens-hooks.sh SessionStart) і PROFILE.md є → ✓ (+ час з позначки гачка);
#                    гачка нема → ⚠ «профілю в сесії НЕМА» (setup script v3)
#   без змінної   → профіль з поля налаштувань акаунта; поки в CLAUDE.md ядра є рядок «Відкрите `ACC-1`» (стеля черги ядра — 12, тож дім відкритого — CLAUDE.md) — ⓘ нагадування спитати Konst про досвід LENS_PROFILE=1
#   bash profile_check.sh selftest — 3 випадки на підставних файлах (зуби: без гачка → ⚠)
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; k="$h/../.."
line() {   # $1 — settings.json, $2 — позначка, $3 — CLAUDE.md ядра (рядок «Відкрите `ACC-1`»)
  if [ "${LENS_PROFILE:-}" = 1 ]; then
    if grep -q 'lens-hooks.sh[^"]*SessionStart' "$1" 2>/dev/null && [ -f "$h/PROFILE.md" ]; then
      t=""; [ -f "$2" ] && t=" · покладено о $(cat "$2")"; echo "профіль: з репо (LENS_PROFILE=1) ✓ гачок старту встановлено$t"
    else echo "⚠ профіль: LENS_PROFILE=1, але гачка старту ядра нема (setup script v3) — профілю в сесії НЕМА → lens-governance:tools/claude-code/ACCOUNT_MOVE.md"; fi
  else
    o=""; grep -q '`ACC-1`' "$3" 2>/dev/null && o=" · ⓘ ACC-1: якщо це свій акаунт після резервного — першим спитай Konst про досвід LENS_PROFILE=1 і узгодь (lens-governance:tools/claude-code/ACCOUNT_MOVE.md «Профіль лише в репо»)"
    echo "профіль: з налаштувань акаунта (LENS_PROFILE нема)$o"
  fi
}
if [ "${1:-}" = selftest ]; then
  d=$(mktemp -d); echo '{"hooks":{"SessionStart":[{"hooks":[{"command":"bash lens-hooks.sh SessionStart"}]}]}}' > "$d/s.json"; echo '{}' > "$d/none.json"; echo '| `ACC-1` |' > "$d/q.md"; bad=0
  r=$(LENS_PROFILE=1 line "$d/s.json" "$d/m" "$d/q.md"); case "$r" in *✓*) echo "✓ LENS_PROFILE=1 + гачок → ✓";; *) echo "✗ $r"; bad=1;; esac
  r=$(LENS_PROFILE=1 line "$d/none.json" "$d/m" "$d/q.md"); case "$r" in ⚠*НЕМА*) echo "✓ LENS_PROFILE=1 без гачка → ⚠ (зуби)";; *) echo "✗ $r"; bad=1;; esac
  r=$(LENS_PROFILE= line "$d/s.json" "$d/m" "$d/q.md"); case "$r" in *ACC-1*) echo "✓ свій акаунт + ACC-1 відкритий → нагадування";; *) echo "✗ $r"; bad=1;; esac
  rm -rf "$d"; exit $bad
fi
line "$HOME/.claude/settings.json" /tmp/lens-profile-loaded "$k/CLAUDE.md"
