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

KDIR="$(cd "$(dirname "$0")/../../kernel" && pwd)"   # queue_open — одна мірка черги (CQ-1)
LENS_PRODUCTS=" EquipLens stock-check QR-Lens Drive-Lens PharmaLens KPI-Lens "   # реєстр — kernel/Lens_INDEX.md §5

SHARED_TOOLS="doc_health.py shots_check.py"   # спільні інструменти ядра для env_check кожного репо (DOC-1, 10.10.2026; примірка — SHOTS.md, QR CC-9 11.10.2026: інструмент, про який продукт не знає, не працює). Виклик, не копія — копії розходяться (практика reusable workflows, earthly.dev · GitHub Docs, 11.10.2026)

check() {
  local d="${1%/}" n miss=() kind
  n=$(basename "$(git -C "$d" rev-parse --show-toplevel 2>/dev/null || echo "$d")")
  [ -f "$d/CLAUDE.md" ] || { echo "⚠ $n не адаптоване: нема CLAUDE.md → ADOPT (lens-governance:tools/claude-code/ADOPT.md)"; return 1; }
  if grep -q 'основна робота — у Project' "$d/CLAUDE.md"; then echo "✓ $n — шлях В (міст): лише CLAUDE.md, так і треба"; return 0; fi
  # автономне репо (Konst AE S103 про Routes: «він сам по собі, свої інструменти й гачки, ядра не стосується»): CLAUDE.md каже, що ядро
  #   в сесії не підключається → каркас ядра не вимагається. Без цього ⚠ щосесії — шум, що привчає пропускати ⚠ (Datadog, Rootly «alert fatigue»,
  #   24.10.2026: глушити вузько, з доказом, у приладі; перевіряти, що справжня умова досі спрацьовує — зуби нижче)
  if grep -q 'автономний' "$d/CLAUDE.md" && grep -qE '(ядро|lens-governance).{0,60}не підключається' "$d/CLAUDE.md"; then echo "✓ $n — автономне (свої правила, гачки й гейти; каркас ядра не вимагається)"; return 0; fi
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
  # CQ-1 (05.10.2026): черга — таблиця з `id` і датою, інакше лічильник стелі (kernel/Lens_INDEX.md §5) її не бачить
  local q; q=$(ls "$d"/kernel/Lens_governance_CHERGA.md "$d"/lens/*_CHERGA.md "$d"/docs/CHERGA.md 2>/dev/null | head -1)
  if [ -n "$q" ]; then
    local qs; qs=$(python3 -c "import sys; sys.path.insert(0, '$KDIR'); from Lens_validate import queue_open as f; r=f(open('$q', encoding='utf-8').read()); print(len(r), sum(a is not None for _, a in r))" 2>/dev/null)
    case "$qs" in "0 0") miss+=("${q#$d/} — черга не таблицею з \`id\` і датою (CQ-1)");; *" 0") miss+=("${q#$d/} — пункти без дати (CQ-1)");; esac
  fi
  # Спільні інструменти ядра (Konst 10.10, QR CC-7: «інструмент, що можна розповсюдити на всі продукти, — правильно розмістити»): кожен
  # кличеться з env_check репо, інакше продукт не отримує покращень. Новий такий інструмент — сюди + у шаблон env_check ТИМ САМИМ комітом.
  local tool; for tool in $SHARED_TOOLS; do
    [ -s "$d/tools/env_check.sh" ] && ! grep -q "$tool" "$d/tools/env_check.sh" && miss+=("tools/env_check.sh не кличе $tool — рядок із шаблону ядра (tools/claude-code/templates/env_check_template.sh)")
  done
  # ENV-CLONE (Konst 18.10.2026, AE S90): інструменти ядра — з клону поруч, не curl з main (клон кладе setup script v3; віддалений скрипт з гілки — зайвий ризик; шаблон env_check)
  [ -s "$d/tools/env_check.sh" ] && grep -q 'raw.githubusercontent.com/Konst-Andre/lens-governance/main/tools/' "$d/tools/env_check.sh" && miss+=("tools/env_check.sh тягне інструменти ядра curl з main — на клон ядра поруч (templates/env_check_template.sh)")
  # UI-1 (Konst 18.10.2026, QR CC-16): репо з інтерфейсом — рядок «Дизайн-основа:» у CLAUDE.md (токени · як бере друга поверхня · префікси класів, REPO_FRAME §3-б)
  if [ "$kind" != "ядро" ] && [ -n "$(find "$d" -name '*.html' -not -path '*/archive/*' -not -path '*/node_modules/*' -not -path '*/.git/*' -print -quit 2>/dev/null)" ] && ! grep -q 'Дизайн-основа' "$d/CLAUDE.md"; then
    miss+=("CLAUDE.md: рядок «Дизайн-основа:» — де токени, як їх бере друга поверхня, префікси класів (UI-1, lens-governance:tools/claude-code/REPO_FRAME.md §3-б)")
  fi
  # VER-1 (Konst 18.10.2026, QR CC-17): репо з інтерфейсом — env_check кличе version_check.py (версія B · rev; tools/claude-code/VERSIONS.md)
  if [ "$kind" != "ядро" ] && [ -s "$d/tools/env_check.sh" ] && [ -n "$(find "$d" -name '*.html' -not -path '*/archive/*' -not -path '*/node_modules/*' -not -path '*/.git/*' -print -quit 2>/dev/null)" ] && ! grep -q 'version_check' "$d/tools/env_check.sh"; then
    miss+=("tools/env_check.sh не кличе version_check.py — версія застосунку B · rev без нагляду (VER-1, lens-governance:tools/claude-code/VERSIONS.md; рядок — templates/env_check_template.sh)")
  fi
  # PW-1 (AE S103, 24.10.2026): хук старту з зашитим playwright==N — після оновлення образу (chromium-1243) зашите 1.56.0 шукало 1194, і всі
  #   Python-гейти AE падали за 1 с. Версія — пара образу (templates/session_start_template.sh), рядок «браузер» в env_check (wsd 1.21 п.4)
  grep -qE 'playwright==[0-9]' "$d/.claude/hooks/session-start.sh" 2>/dev/null && miss+=(".claude/hooks/session-start.sh зашиває playwright==N — пара образу, не число (PW-1, wsd 1.21; зразок — templates/session_start_template.sh)")
  # PW-2 (AE S103): гейт, названий у CLAUDE.md, з ≥ 3 фіксованими паузами і без pw_quiet — простій «на око» (AE: ≈ 27 хв → 60 с). Практика —
  #   eslint-plugin-playwright no-wait-for-timeout, Biome noPlaywrightWaitForTimeout (24.10.2026); у нас ⚠ і виняток, бо pw_quiet робить старі паузи безпечними.
  #   Межа — «названий у CLAUDE.md»: старі версії приладів, що лишились поруч, не шумлять. Пауза справді потрібна — «pause-ok» у файлі з причиною.
  local pw2=() f2 c2; while IFS= read -r f2; do
    c2=$(grep -cE 'wait_for_timeout\(|waitForTimeout\(' "$f2" 2>/dev/null); [ "${c2:-0}" -ge 3 ] || continue
    grep -qE 'pw_quiet|quiet_v1|pause-ok' "$f2" && continue
    grep -qE "(^|[^A-Za-z0-9_])$(basename "${f2%.*}")([^A-Za-z0-9_]|$)" "$d/CLAUDE.md" && pw2+=("$(basename "$f2") ($c2)")
  done < <(find "$d/tools" -type f \( -name '*.py' -o -name '*.mjs' -o -name '*.js' \) -not -path '*/archive/*' -not -path '*/node_modules/*' 2>/dev/null)
  [ ${#pw2[@]} -gt 0 ] && miss+=("гейти з фіксованими паузами без pw_quiet: ${pw2[*]} — пауза = подія (PW-2, wsd 1.21; lens-governance:tools/claude-code/pw_quiet.py · pw_quiet.mjs)")
  # AUD-2 (05.10.2026): скрипт аудиту — копія зразка «як є»; стара копія жене дорогі паралельні проходи без класу
  [ -s "$d/tools/audit_prompts.sh" ] && ! cmp -s "$d/tools/audit_prompts.sh" "$KDIR/../tools/claude-code/audit_prompts.sh" && miss+=("tools/audit_prompts.sh ≠ зразок ядра — скопіювати (AUD-2)")
  if [ ${#miss[@]} -eq 0 ]; then echo "✓ $n — каркас на місці ($kind)"; return 0; fi
  local list; list=$(printf ' · %s' "${miss[@]}"); echo "⚠ $n не адаптоване ($kind): бракує ${list# · } → ADOPT (lens-governance:tools/claude-code/ADOPT.md)"; return 1
}

if [ "${1:-}" = "--inject" ]; then
  t=$(mktemp -d); mkdir -p "$t/repo/docs/summary" "$t/repo/tools" "$t/repo/.claude/hooks"
  for p in tools/env_check.sh .claude/hooks/session-start.sh tools/audit_prompts.sh docs/CHERGA.md docs/DECISIONS.md \
           docs/ARCHITECTURE.md docs/REPO_LAYOUT.md docs/AUDIT.md; do : > "$t/repo/$p"; done
  cp "$KDIR/../tools/claude-code/audit_prompts.sh" "$t/repo/tools/audit_prompts.sh"
  printf '## Відкрите\n\n| id | предмет | дата |\n|---|---|---|\n| `Ч-1` | x | 05.10.2026 |\n\n-----\n' > "$t/repo/docs/CHERGA.md"
  echo x > "$t/repo/CLAUDE.md"; full=$(check "$t/repo"); rc_full=$?
  rm "$t/repo/CLAUDE.md";     gone=$(check "$t/repo"); rc_gone=$?
  echo x > "$t/repo/CLAUDE.md"; rm "$t/repo/docs/AUDIT.md"; part=$(check "$t/repo"); rc_part=$?
  : > "$t/repo/docs/AUDIT.md"; printf '1. пункт списком\n' > "$t/repo/docs/CHERGA.md"; qlist=$(check "$t/repo"); rc_q=$?
  printf '## Відкрите\n\n| id | предмет | дата |\n|---|---|---|\n| `Ч-1` | x | 05.10.2026 |\n\n-----\n' > "$t/repo/docs/CHERGA.md"; qok=$(check "$t/repo"); rc_qok=$?
  echo 'echo база' > "$t/repo/tools/env_check.sh"; sh0=$(check "$t/repo"); rc_sh0=$?; echo 'python3 doc_health.py .' >> "$t/repo/tools/env_check.sh"; shd=$(check "$t/repo"); rc_shd=$?; echo 'python3 shots_check.py .' >> "$t/repo/tools/env_check.sh"; sh1=$(check "$t/repo"); rc_sh1=$?
  : > "$t/repo/docs/index.html"; ui0=$(check "$t/repo"); rc_ui0=$?; echo 'Дизайн-основа: :root у docs/index.html · префікс app-' > "$t/repo/CLAUDE.md"; ver0=$(check "$t/repo"); rc_ver0=$?; echo 'python3 version_check.py .' >> "$t/repo/tools/env_check.sh"; ui1=$(check "$t/repo"); rc_ui1=$?; rm "$t/repo/docs/index.html"; echo x > "$t/repo/CLAUDE.md"
  echo 'curl -sSf https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/tools/cloudflare/cf_budget.sh | bash' >> "$t/repo/tools/env_check.sh"; cl1=$(check "$t/repo"); rc_cl1=$?
  sed -i '$d' "$t/repo/tools/env_check.sh"
  echo "# стара копія" >> "$t/repo/tools/audit_prompts.sh"; aud=$(check "$t/repo"); rc_aud=$?
  rm -rf "$t"
  [ $rc_cl1 -eq 1 ] && [[ "$cl1" == *"curl з main"* ]] || ok_cl=1   # ENV-CLONE (AE S90): curl з main у env_check — ⚠
  ok=${ok_cl:-0}; [ $rc_full -eq 0 ] || ok=1; [ $rc_gone -eq 1 ] || ok=1; [ $rc_part -eq 1 ] && [[ "$part" == *docs/AUDIT.md* ]] || ok=1; [ $rc_q -eq 1 ] && [[ "$qlist" == *CQ-1* ]] || ok=1; [ $rc_qok -eq 0 ] || ok=1; [ $rc_aud -eq 1 ] && [[ "$aud" == *AUD-2* ]] || ok=1
  [ $rc_ui0 -eq 1 ] && [[ "$ui0" == *UI-1* ]] || ok=1; [ $rc_ui1 -eq 0 ] || ok=1   # UI-1: інтерфейс без «Дизайн-основа» — ⚠, з рядком — ✓
  [ $rc_ver0 -eq 1 ] && [[ "$ver0" == *VER-1* ]] || ok=1   # VER-1 (QR CC-17): інтерфейс, env_check без version_check — ⚠
  [ $rc_sh0 -eq 1 ] && [[ "$sh0" == *doc_health.py* ]] || ok=1; [ $rc_sh1 -eq 0 ] || ok=1; [ $rc_shd -eq 1 ] && [[ "$shd" == *shots_check.py* ]] && [[ "$shd" != *doc_health.py* ]] || ok=1   # примірка (CC-9): кличе doc_health, а shots_check ні → ⚠ саме з його назвою
  # PW-1 · PW-2 (AE S103): зашитий playwright — ⚠; гейт з CLAUDE.md з паузами без pw_quiet — ⚠; з pw_quiet — ✓
  t2=$(mktemp -d); mkdir -p "$t2/r/tools" "$t2/r/.claude/hooks"; echo 'гейт: tools/walk_v1.py' > "$t2/r/CLAUDE.md"
  echo 'pip install "playwright==1.56.0"' > "$t2/r/.claude/hooks/session-start.sh"; pw1=$(check "$t2/r")
  printf 'pg.wait_for_timeout(100)\npg.wait_for_timeout(100)\npg.wait_for_timeout(100)\n' > "$t2/r/tools/walk_v1.py"; pw2=$(check "$t2/r")
  echo 'from pw_quiet import install' >> "$t2/r/tools/walk_v1.py"; pw2q=$(check "$t2/r"); rm -rf "$t2"
  [[ "$pw1" == *PW-1* ]] && [[ "$pw2" == *walk_v1.py*"PW-2"* ]] && [[ "$pw2q" != *PW-2* ]] || { ok=1; printf "✗ inject PW:\n1 %s\n2 %s\n3 %s\n" "$pw1" "$pw2" "$pw2q" | cut -c1-600; }
  # автономне (AE S103): CLAUDE.md «автономний … ядро … не підключається» → ✓ без переліку; лише «автономний» без цього — звичайна перевірка
  t3=$(mktemp -d); mkdir -p "$t3/r"; printf 'Routes автономний: ядро `lens-governance` у сесії не підключається.\n' > "$t3/r/CLAUDE.md"; au1=$(check "$t3/r")
  printf 'Продукт автономний у рішеннях.\n' > "$t3/r/CLAUDE.md"; au0=$(check "$t3/r"); rm -rf "$t3"
  [[ "$au1" == *автономне* ]] && [[ "$au0" == *"не адаптоване"* ]] || { ok=1; echo "✗ inject автономне: $au1 | $au0" | cut -c1-200; }
  [ $ok -eq 0 ] && echo "✓ inject: повний — ✓, без CLAUDE.md — ⚠, без docs/AUDIT.md — ⚠ з назвою, черга списком — ⚠ CQ-1, черга таблицею — ✓, стара копія скрипта аудиту — ⚠ AUD-2, інтерфейс без «Дизайн-основа» — ⚠ UI-1, env_check без спільного інструмента — ⚠ з назвою, з ним — ✓, curl інструментів ядра з main — ⚠" || echo "✗ inject: детектор сліпий ($full | $gone | $part)"
  exit $ok
fi

[ $# -ge 1 ] || { echo "вкажіть теку репо (або --inject)"; exit 2; }
rc=0; for d in "$@"; do check "$d" || rc=1; done; exit $rc
