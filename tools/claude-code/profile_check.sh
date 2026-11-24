#!/bin/bash
# живе доки: профіль Konst може приходити з репо (LENS_PROFILE=1, гачок старту) — tools/claude-code/ACCOUNT_MOVE.md п.1-б. Дім — ядро.
# Один рядок «профіль: …» для env_check ядра й продуктів: звідки профіль у цій сесії і чи він справді є (тиха відсутність — неможлива).
#   LENS_PROFILE=1 → гачок старту встановлено (~/.claude/settings.json → lens-hooks.sh SessionStart) і PROFILE.md є → ✓ (+ час з позначки гачка);
#                    гачка нема → ⚠ «профілю в сесії НЕМА» (setup script v3)
#   без змінної   → ⓘ, не ⚠: так буває законно — автономне середовище зі своїм профілем у репо (Routes: ядро підключають лише перейняти щось,
#                    Konst 24.11.2026; ⚠ там був би хибною тривогою щоразу). Сесія Lens без змінної — профіль ядра не покладено: ліки в рядку.
#   bash profile_check.sh selftest — 3 випадки на підставних файлах (зуби: без гачка → ⚠; без змінної — ⓘ з ліками, не ⚠)
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; k="$h/../.."
line() {   # $1 — settings.json, $2 — позначка, $3 — CLAUDE.md ядра (рядок «Відкрите `ACC-1`»)
  if [ "${LENS_PROFILE:-}" = 1 ]; then
    if grep -q 'lens-hooks.sh[^"]*SessionStart' "$1" 2>/dev/null && [ -f "$h/PROFILE.md" ]; then
      t=""; [ -f "$2" ] && t=" · покладено о $(cat "$2")"; echo "профіль: з репо (LENS_PROFILE=1) ✓ гачок старту встановлено$t"
    else echo "⚠ профіль: LENS_PROFILE=1, але гачка старту ядра нема (setup script v3) — профілю в сесії НЕМА → lens-governance:tools/claude-code/ACCOUNT_MOVE.md"; fi
  else
    echo "ⓘ профіль: LENS_PROFILE нема — профіль ядра не покладено (законно в автономному середовищі зі своїм профілем, як Routes); сесія Lens — середовище → Environment variables → LENS_PROFILE=1 (lens-governance:tools/claude-code/ACCOUNT_MOVE.md п.1-а)"
  fi
}
if [ "${1:-}" = selftest ]; then
  d=$(mktemp -d); echo '{"hooks":{"SessionStart":[{"hooks":[{"command":"bash lens-hooks.sh SessionStart"}]}]}}' > "$d/s.json"; echo '{}' > "$d/none.json"; echo '| `ACC-1` |' > "$d/q.md"; bad=0
  r=$(LENS_PROFILE=1 line "$d/s.json" "$d/m" "$d/q.md"); case "$r" in *✓*) echo "✓ LENS_PROFILE=1 + гачок → ✓";; *) echo "✗ $r"; bad=1;; esac
  r=$(LENS_PROFILE=1 line "$d/none.json" "$d/m" "$d/q.md"); case "$r" in ⚠*НЕМА*) echo "✓ LENS_PROFILE=1 без гачка → ⚠ (зуби)";; *) echo "✗ $r"; bad=1;; esac
  r=$(LENS_PROFILE= line "$d/s.json" "$d/m" "$d/q.md"); case "$r" in ⓘ*LENS_PROFILE=1*) echo "✓ без LENS_PROFILE → ⓘ з ліками, не ⚠ (автономне середовище — не тривога, Konst 24.11)";; *) echo "✗ $r"; bad=1;; esac
  rm -rf "$d"; exit $bad
fi
line "$HOME/.claude/settings.json" /tmp/lens-profile-loaded "$k/CLAUDE.md"
