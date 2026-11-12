#!/usr/bin/env bash
# precompact_guard.sh · гачок ядра (з чернетки FAB-2, перенесено AE S140) (звіт docs/fab/FAB2_compact.md № 8–9; «так» Konst 12.11.2026) — сторож правила «ревізія → /compact».
# живе доки: діє правило «ревізія → /compact» (lens-governance:tools/claude-code/CLAUDE_CODE.md «Практики»); виклик — диспетчер hooks/lens-hooks.sh, подія PreCompact.
# Що робить: (1) ручне /compact, а в репо сесії є незакомічене або HEAD не на GitHub → вихід 2, стиснення не відбувається, рядок бачить Konst;
#            (2) слово Konst у самій команді — «/compact без ревізії …» — пропускає (обхід з причиною, слід у журналі диспетчера);
#            (3) автоматичне стиснення НЕ блокує ніколи (hooks «PreCompact»: блок під час рятування від ліміту контексту валить запит),
#                але пише незбережене в інструкції переказу — щоб після стиснення агент першим ділом зберіг;
#            (4) у вивід (= інструкції переказу, ≤ 10 000 знаків) — факти git від програми: репо · гілка · HEAD · коміти цієї сесії;
#            (5) при блоці лишає позначку — наступний UserPromptSubmit каже агентові «Konst пробував стиснути: зроби ревізію».
# Помилка самого гачка (вихід не 0 і не 2) стиснення не зупиняє — так влаштовано Claude Code (hooks «Exit code output»): сторож відмовляє «у відкрите».
# Запуск: echo '{"trigger":"manual","custom_instructions":null}' | LENS_ROOT=/home/user LENS_HOOKS=<тека гачків> bash precompact_guard.sh
#         bash precompact_guard.sh selftest     → 8 випадків на тимчасовому репо
set -u
guard() {
  local root="${LENS_ROOT:-/home/user}" hooks="${LENS_HOOKS:-.}" sid="${CLAUDE_CODE_REMOTE_SESSION_ID:-}" in trig ci facts="" dirty="" r n hd b cm
  sid="${sid#cse_}"; sid="${sid#session_}"
  in="$(cat)"; trig="$(printf '%s' "$in" | sed -n 's/.*"trigger"[^"]*"\([a-z]*\)".*/\1/p')"
  ci="$(printf '%s' "$in" | sed -n 's/.*"custom_instructions"[^"]*"\(.*\)".*/\1/p')"
  for r in "$root"/*/; do
    [ -d "$r.git" ] || continue; [ -e "$r.git/lens-readonly" ] && continue
    n="$(basename "$r")"; hd="$(git -C "$r" rev-parse --short HEAD 2>/dev/null)"; b="$(git -C "$r" branch --show-current 2>/dev/null)"
    [ -n "$(git -C "$r" status --porcelain 2>/dev/null | head -1)" ] && dirty="$dirty $n:незакомічене($(git -C "$r" status --porcelain | wc -l))"
    [ -n "$b" ] && [ "$(git -C "$r" rev-parse HEAD 2>/dev/null)" != "$(git -C "$r" rev-parse "origin/$b" 2>/dev/null)" ] && dirty="$dirty $n:не-на-GitHub"
    cm=""; [ -n "$sid" ] && cm="$(git -C "$r" log -12 --grep="Claude-Session: .*$sid" --format='%h %s' 2>/dev/null | cut -c1-90 | sed 's/^/    /')"
    facts="$facts
- $n · гілка ${b:-(без гілки)} · HEAD $hd${cm:+
$cm}"
  done
  if [ "$trig" = manual ] && [ -n "$dirty" ]; then
    case "$ci" in *"без ревізії"*|*"без ревизии"*) echo "$(date -u +%FT%TZ) precompact обхід: $dirty · «$ci»" >> "${LENS_LOG:-/tmp/lens-precompact.log}" ;;
      *) : > "${LENS_FLAG:-/tmp/lens-compact-blocked}"
         echo "Стиснення зупинено — не все збережено:$dirty. Напиши агентові «ревізія», після коміту й push — /compact ще раз. Свідомо стиснути так: /compact без ревізії <чому>." >&2; return 2 ;;
    esac
  fi
  [ -f "$hooks/compact_instructions.txt" ] && cat "$hooks/compact_instructions.txt"
  printf '\nФакти на мить стиснення — від програми, встав дослівно, не пригадуй:%s\n' "$facts" | head -c 4000
  [ -n "$dirty" ] && printf '\nНЕ ЗБЕРЕЖЕНО на мить стиснення:%s — у переказі першим рядком: «спершу закомітити й запушити».\n' "$dirty"
  return 0
}
selftest() {
  local t bad=0 e me; me="$(readlink -f "${BASH_SOURCE[0]}")"; t="$(mktemp -d)"; git init -q --bare "$t/o.git"; git clone -q "$t/o.git" "$t/w/repoA" 2>/dev/null
  ( cd "$t/w/repoA" && git config user.email a@b && git config user.name t && echo 1 > f && git add f && git commit -qm "c1

Claude-Session: https://claude.ai/code/session_TESTSID" && git push -q origin HEAD 2>/dev/null )
  run() { printf '{"hook_event_name":"PreCompact","trigger":"%s","custom_instructions":%s}' "$1" "${2:-null}" | CLAUDE_CODE_REMOTE_SESSION_ID=cse_TESTSID LENS_ROOT="$t/w" LENS_HOOKS="$t" LENS_FLAG="$t/flag" LENS_LOG="$t/log" bash "$me" 2>"$t/err" >"$t/out"; echo $?; }
  say() { [ "$1" = 1 ] && echo "✓ $2" || { echo "✗ $2"; bad=1; }; }
  e=$(run manual); say $([ "$e" = 0 ] && grep -q "HEAD" "$t/out" && grep -q "c1" "$t/out" && echo 1) "чисте + manual → 0; у фактах HEAD і коміт цієї сесії"
  echo x > "$t/w/repoA/new"; e=$(run manual); say $([ "$e" = 2 ] && grep -q "незакомічене" "$t/err" && [ -e "$t/flag" ] && echo 1) "незакомічене + manual → 2, рядок Konst, позначка для агента"
  e=$(run auto); say $([ "$e" = 0 ] && grep -q "НЕ ЗБЕРЕЖЕНО" "$t/out" && echo 1) "незакомічене + auto → 0 (не блокуємо), «НЕ ЗБЕРЕЖЕНО» в інструкціях"
  e=$(run manual '"без ревізії: чернетка, не шкода"'); say $([ "$e" = 0 ] && grep -q "обхід" "$t/log" && echo 1) "«/compact без ревізії …» → 0, слід у журналі"
  e=$(run manual '"збережи рішення про рейку"'); say $([ "$e" = 2 ] && echo 1) "інші слова в /compact обходу не дають → 2"
  ( cd "$t/w/repoA" && git add new && git commit -qm c2 ); e=$(run manual); say $([ "$e" = 2 ] && grep -q "не-на-GitHub" "$t/err" && echo 1) "закомічено, не запушено + manual → 2"
  ( cd "$t/w/repoA" && git push -q origin HEAD 2>/dev/null ); e=$(run manual); say $([ "$e" = 0 ] && echo 1) "запушено → 0"
  touch "$t/w/repoA/.git/lens-readonly"; echo y > "$t/w/repoA/z"; e=$(run manual); say $([ "$e" = 0 ] && echo 1) "клон лише для читання (lens-readonly) не судиться → 0"
  echo "─── precompact_guard selftest: $([ $bad = 0 ] && echo 8/8 || echo є ✗) ───"; return $bad
}
if [ "${1:-}" = selftest ]; then selftest; else guard; fi
