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
#         bash precompact_guard.sh selftest     → 11 випадків на тимчасовому репо + обгортка PreCompact (шаблон ENVIRONMENT.md і живий ~/.claude/settings.json)
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
  # REV-1 (AE S143, В-361): «можна /compact» — лише після ревізії машиною, не з пам'яті: ✗ handoff_check (брифи · рішення · журнали) і мітка
  #   «ревізію зроблено після останнього стиснення» (пише handoff_check revision — слово Konst, поріг ctx_watch чи сам агент; знімає ctx_watch після стиснення).
  local hc="$hooks/../handoff_check.py" x="" mark="${LENS_REV_MARK:-/tmp/lens-revision-$(printf '%s' "${CLAUDE_CODE_SESSION_ID:-${CLAUDE_CODE_REMOTE_SESSION_ID:-x}}" | tr -cd '[:alnum:]_')}"
  [ -z "$dirty" ] && [ -f "$hc" ] && x="$(python3 "$hc" gate "$root" 2>/dev/null | head -8 | cut -c1-300)"
  [ -n "$x" ] && dirty="$dirty handoff_check:✗($(printf '%s\n' "$x" | wc -l))"
  [ -f "$hc" ] && [ ! -f "$mark" ] && dirty="$dirty ревізії-після-стиснення-не-було"
  if [ "$trig" = manual ] && [ -n "$dirty" ]; then
    case "$ci" in *"без ревізії"*|*"без ревизии"*) echo "$(date -u +%FT%TZ) precompact обхід: $dirty · «$ci»" >> "${LENS_LOG:-/tmp/lens-precompact.log}" ;;
      *) : > "${LENS_FLAG:-/tmp/lens-compact-blocked}"
         echo "Стиснення зупинено — не все збережено:$dirty.${x:+
$x}
Напиши агентові «ревізія» (або агент сам: python3 lens-governance/tools/claude-code/handoff_check.py revision), після виправлень, коміту й push — /compact ще раз. Свідомо стиснути так: /compact без ревізії <чому>." >&2; return 2 ;;
    esac
  fi
  [ -f "$hooks/compact_instructions.txt" ] && cat "$hooks/compact_instructions.txt"
  printf '\nФакти на мить стиснення — від програми, встав дослівно, не пригадуй:%s\n' "$facts" | head -c 4000
  [ -n "$dirty" ] && printf '\nНЕ ЗБЕРЕЖЕНО на мить стиснення:%s%s — у переказі першим рядком: «спершу: ревізія (handoff_check revision), виправити ✗, закомітити й запушити».\n' "$dirty" "${x:+
$x}"
  return 0
}
selftest() {
  local t bad=0 e me; me="$(readlink -f "${BASH_SOURCE[0]}")"; t="$(mktemp -d)"; git init -q --bare "$t/o.git"; git clone -q "$t/o.git" "$t/w/repoA" 2>/dev/null
  mkdir -p "$t/w/repoA/docs/summary"; printf '## §0 ВІДКРИТЕ\n- x\n\n```text\nСТАРТ: x\n```\n' > "$t/w/repoA/docs/summary/A_SUMMARY_X.md"
  ( cd "$t/w/repoA" && git config user.email a@b && git config user.name t && echo 1 > f && git add -A && git commit -qm "c1

Claude-Session: https://claude.ai/code/session_TESTSID" && git push -q origin HEAD 2>/dev/null )
  run() { printf '{"hook_event_name":"PreCompact","trigger":"%s","custom_instructions":%s}' "$1" "${2:-null}" | CLAUDE_CODE_REMOTE_SESSION_ID=cse_TESTSID CLAUDE_CODE_SESSION_ID=TESTSID LENS_REV_MARK="$t/rev" LENS_ROOT="$t/w" LENS_HOOKS="$t/hooks" LENS_FLAG="$t/flag" LENS_LOG="$t/log" bash "$me" 2>"$t/err" >"$t/out"; echo $?; }
  say() { [ "$1" = 1 ] && echo "✓ $2" || { echo "✗ $2"; bad=1; }; }
  mkdir -p "$t/hooks"; cp "$(dirname "$me")/../handoff_check.py" "$t/"; cp "$(dirname "$me")/../doc_health.py" "$t/" 2>/dev/null
  e=$(run manual); say $([ "$e" = 2 ] && grep -q "ревізії-після-стиснення-не-було" "$t/err" && echo 1) "REV-1: чисте, але ревізії після стиснення не було + manual → 2"
  e=$(run auto); say $([ "$e" = 0 ] && grep -q "НЕ ЗБЕРЕЖЕНО.*ревізії" "$t/out" && echo 1) "REV-1: без ревізії + auto → 0, у переказі «спершу: ревізія»"
  touch "$t/rev"
  e=$(run manual); say $([ "$e" = 0 ] && grep -q "HEAD" "$t/out" && grep -q "c1" "$t/out" && echo 1) "чисте + ревізія є + manual → 0; у фактах HEAD і коміт цієї сесії"
  sed -i 's/```text/```txt/' "$t/w/repoA/docs/summary/A_SUMMARY_X.md"; ( cd "$t/w/repoA" && git commit -qam c1b && git push -q origin HEAD 2>/dev/null )
  e=$(run manual); say $([ "$e" = 2 ] && grep -q "handoff_check:✗" "$t/err" && grep -q "стартове повідомлення нема" "$t/err" && echo 1) "REV-1: ✗ handoff_check (самері без стартового) + manual → 2, рядок ✗ бачить Konst"
  sed -i 's/```txt/```text/' "$t/w/repoA/docs/summary/A_SUMMARY_X.md"; ( cd "$t/w/repoA" && git commit -qam c1c && git push -q origin HEAD 2>/dev/null )
  echo x > "$t/w/repoA/new"; e=$(run manual); say $([ "$e" = 2 ] && grep -q "незакомічене" "$t/err" && [ -e "$t/flag" ] && echo 1) "незакомічене + manual → 2, рядок Konst, позначка для агента"
  e=$(run auto); say $([ "$e" = 0 ] && grep -q "НЕ ЗБЕРЕЖЕНО" "$t/out" && echo 1) "незакомічене + auto → 0 (не блокуємо), «НЕ ЗБЕРЕЖЕНО» в інструкціях"
  e=$(run manual '"без ревізії: чернетка, не шкода"'); say $([ "$e" = 0 ] && grep -q "обхід" "$t/log" && echo 1) "«/compact без ревізії …» → 0, слід у журналі"
  e=$(run manual '"збережи рішення про рейку"'); say $([ "$e" = 2 ] && echo 1) "інші слова в /compact обходу не дають → 2"
  ( cd "$t/w/repoA" && git add new && git commit -qm c2 ); e=$(run manual); say $([ "$e" = 2 ] && grep -q "не-на-GitHub" "$t/err" && echo 1) "закомічено, не запушено + manual → 2"
  ( cd "$t/w/repoA" && git push -q origin HEAD 2>/dev/null ); e=$(run manual); say $([ "$e" = 0 ] && echo 1) "запушено → 0"
  touch "$t/w/repoA/.git/lens-readonly"; echo y > "$t/w/repoA/z"; e=$(run manual); say $([ "$e" = 0 ] && echo 1) "клон лише для читання (lens-readonly) не судиться → 0"
  # S143 (тест Konst): `/compact` пройшов, бо обгортка в ~/.claude/settings.json закінчувалась «|| true» і ковтала вихід 2. Тест — справжнім шляхом виклику:
  printf '#!/bin/bash\nexit 2\n' > "$t/fake.sh"
  for s in "$(dirname "$me")/../ENVIRONMENT.md" "$HOME/.claude/settings.json"; do [ -f "$s" ] || continue
    c="$(grep -o '"PreCompact":\[{"hooks":\[{"type":"command","command":"[^"]*"' "$s" | sed 's/.*"command":"//; s/"$//')"
    [ -n "$c" ] || continue; e=$(bash -c "${c//\/home\/user\/lens-governance\/tools\/claude-code\/hooks\/lens-hooks.sh/$t/fake.sh}" </dev/null >/dev/null 2>&1; echo $?)
    say "$([ "$e" = 2 ] && echo 1)" "обгортка PreCompact ($(basename "$s")) пропускає вихід 2 — «/compact» справді зупиняється"; done
  echo "─── precompact_guard selftest: $([ $bad = 0 ] && echo 11+обгортки || echo є ✗) ───"; return $bad
}
if [ "${1:-}" = selftest ]; then selftest; else guard; fi
