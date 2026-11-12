#!/bin/bash
# живе доки: гачки Lens вмикаються через налаштування користувача (tools/claude-code/CLAUDE_CODE.md «Гачки»).
# Диспетчер: setup script середовища вказує лише на цей файл — на ВСІ потрібні події, без фільтра інструментів (v2, HOOK-4, 09.10.2026).
# Новий гачок на одну з 9 подій — рядок тут (подія → файл, фільтр інструмента — тут же), setup script не чіпати; нова подія поза 9 — тоді й setup script.
# Аргумент — подія (setup script v2 і v3) або старе ім'я v1 (pre · post · stop — середовища з текстом 08.10 працюють і далі):
#   pre  | PreToolUse          — лише Write|Edit|Bash: бриф лише з шаблону (brief-guard, BRIEF-2); далі гачки по черзі, перший з відповіддю (deny/ask) перемагає; огляд UI до коміту (ui-review-gate, HOOK-2 п.4); нагадування (review-remind stand) — останнім
#   post | PostToolUse         — лише Read|Bash|Grep|WebSearch|WebFetch: позначки (ui-guard mark: кукбук і пошук ззовні) + нагадування після коміту з UI (review-remind post)
#   stop | Stop                — гачок пам'яті (memory-guard, HOOK-3), далі перевірка перед переїздом, коли його оголошує агент (handoff-remind stop, HOOK-3.2), далі «план без світу» (plan-web, HOOK-2.5)
#   UserPromptSubmit           — + маршрут для Konst (route-remind, AE S135 — додається до будь-якого) · перевірка пам'яті перед переїздом (handoff-remind, HOOK-3.2), інакше «пропуск, знайдений Konst» (konst-miss, HOOK-5): лише на слово-тригер (перевіряє Python: grep -i на кирилиці залежить від локалі; ~50 мс раз на повідомлення)
#   SessionStart               — профіль Konst з репо (tools/claude-code/PROFILE.md) як контекст сесії, ЛИШЕ коли в середовищі LENS_PROFILE=1: спільний акаунт, де поле
#                                профілю в налаштуваннях бачили б і чужі чати (слово Konst 18.10.2026, QR CC-18; ACCOUNT_MOVE.md п.1-б). Старт і повтор після стиснення (без matcher —
#                                на всі source). Свій акаунт — профіль у налаштуваннях, змінну не ставити (інакше профіль двічі). Зуби: bash lens-hooks.sh profile-test
#   PostToolUseFailure · SubagentStop · PreCompact · SessionEnd — поки без гачків: вихід одразу
# Ціна: подія без гачка й інструмент поза фільтром — лише bash, без Python (заміряно 09.10: подія без гачка ~6 мс, інструмент поза фільтром ~13 мс; повний ланцюг ~140 мс — як у CLAUDE_CODE.md).
h="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ev="$1"
mrg() {   # AE S141: два виводи гачків (JSON hookSpecificOutput) → один; additionalContext — через порожній рядок; подія — з першого
  [ -z "$1" ] && { printf '%s' "$2"; return; }; [ -z "$2" ] && { printf '%s' "$1"; return; }
  python3 -c 'import json,sys
x=json.loads(sys.argv[1]); y=json.loads(sys.argv[2]); h=x.setdefault("hookSpecificOutput",{}); h["additionalContext"]=(h.get("additionalContext","")+"\n\n"+y["hookSpecificOutput"]["additionalContext"]).strip(); print(json.dumps(x,ensure_ascii=False))' "$1" "$2" 2>/dev/null || printf '%s' "$1"
}
# Хуки старту репо сесії (AE S90 18.10.2026): у сесії з кількома репо Claude Code бере налаштування лише з кореня (/home/user), і
# <репо>/.claude/hooks/session-start.sh не запускається — інструменти гейтів (Playwright, валідатор) тихо відсутні. Диспетчер кличе їх
# сам: кожен репо, крім свого репо сесії (його кличе Claude Code) і ядра; вивід — у журнал (SessionStart чекає JSON), змінні — через
# CLAUDE_ENV_FILE, як у самих хуків. Зуби — `lens-hooks.sh repo-hooks-test`.
repo_hooks() {
  local root="${LENS_REPOS_ROOT:-/home/user}" k f r; k="$(cd "$h/../../.." && pwd)"
  for f in "$root"/*/.claude/hooks/session-start.sh; do
    [ -f "$f" ] || continue; r="${f%/.claude/hooks/session-start.sh}"
    [ "$r" = "${CLAUDE_PROJECT_DIR:-}" ] || [ "$r" = "$k" ] && continue
    ( cd "$r" && timeout 300 bash "$f" ) < /dev/null >> "${LENS_REPO_HOOKS_LOG:-/tmp/lens-repo-hooks.log}" 2>&1 || echo "$(date +%T) ✗ $f" >> "${LENS_REPO_HOOKS_LOG:-/tmp/lens-repo-hooks.log}"
  done
}
if [ "$ev" = repo-hooks-test ]; then
  t=$(mktemp -d); mkdir -p "$t/a/.claude/hooks" "$t/b/.claude/hooks"
  printf 'echo a >> %s/ran\n' "$t" > "$t/a/.claude/hooks/session-start.sh"; printf 'echo b >> %s/ran\n' "$t" > "$t/b/.claude/hooks/session-start.sh"
  LENS_REPOS_ROOT="$t" CLAUDE_PROJECT_DIR="$t/b" LENS_REPO_HOOKS_LOG="$t/log" repo_hooks
  got="$(cat "$t/ran" 2>/dev/null | tr '\n' ' ')"; rm -rf "$t"
  [ "$got" = "a " ] && { echo "✓ хук репо поза сесією запущено, свій репо сесії — ні"; exit 0; } || { echo "✗ repo_hooks: запущено «$got», чекали «a »"; exit 1; }
fi
# env_check кожного репо сесії — сам, на старті (HOOK-2 (5), FAB-1 10.11.2026): у сесії з кількома репо його запускав агент руками, і стартове
# щоразу це нагадувало. Тут — прогін у файл (SessionStart: стеля гачка 600 с; UserPromptSubmit — лише 30 с, code.claude.com/docs/en/hooks
# «Common fields», 10.11.2026), а рядки ⚠ / ✗ кладе в контекст перше повідомлення (гілка prompt нижче). Зеленого не друкуємо — лише перелік репо.
env_all() {   # $1 — ідентифікатор сесії
  local root="${LENS_REPOS_ROOT:-/home/user}" r o="${LENS_ENV_DIR:-/tmp}/lens-env-${1:-nosession}.txt" bad names=""
  [ "${LENS_ENV_AUTO:-1}" = 0 ] && return 0   # вимикач без правки коду: змінна середовища LENS_ENV_AUTO=0 → як раніше, env_check руками
  : > "$o" 2>/dev/null || return 0
  for r in "$root"/*/; do r="${r%/}"; [ -f "$r/tools/env_check.sh" ] || continue
    [ -e "$r/.git/lens-readonly" ] && continue   # клон лише для читання (звірка іншого продукту) — не судимо, як handoff-remind
    # тривога — рядок, що ПОЧИНАЄТЬСЯ з ⚠ / ✗, або несе «✗ N» з N > 0, «ПОРА», «треба pull», «розібратись»; підсумки на кшталт «✓19 · ⚠24 · ✗0» — не тривога
    bad="$( (cd "$r" && timeout 180 bash tools/env_check.sh 2>&1) < /dev/null | grep -E '^[[:space:]]*(⚠|✗)|✗ ?[1-9]|ПОРА|треба pull|розібратись' | cut -c1-400 )"
    names="$names $(basename "$r")"
    [ -n "$bad" ] && printf '── %s ──\n%s\n' "$(basename "$r")" "$bad" >> "$o"
  done
  [ -n "$names" ] || { rm -f "$o"; return 0; }
  awk '/^── /||!s[$0]++' "$o" > "$o.t" 2>/dev/null && mv "$o.t" "$o"   # однаковий рядок двох репо (спільний Cloudflare) — один раз
  [ -s "$o" ] || printf 'env_check: ⚠ / ✗ нема (репо:%s)\n' "$names" >> "$o"
}
if [ "$ev" = start-test ]; then   # зуби FAB-1: пауза не дублює профіль · стиснення повторює · env_check у файл і в перше повідомлення · текст для стиснення
  t=$(mktemp -d); mkdir -p "$t/repos/a/tools" "$t/repos/b/tools" "$t/repos/c"; bad=0
  printf 'echo "база: ok"\necho "env: гейт ✓19 · ⚠24 · ✗0"\necho "⚠ тест: увага"\necho "✗ тест: червоне"\necho "гейт: ✓ 5 · ✗ 3 — глянь"\necho "⚠ спільне: хмара"\n' > "$t/repos/a/tools/env_check.sh"; printf 'echo "усе гаразд"\necho "⚠ спільне: хмара"\n' > "$t/repos/b/tools/env_check.sh"
  go() { printf '{"session_id":"%s","source":"%s"}' "$1" "$2" | LENS_PROFILE=1 LENS_REPOS_ROOT="$t/repos" LENS_ENV_DIR="$t" LENS_MARK_DIR="$t" LENS_SKILLS_DIR="$t/skills" bash "${BASH_SOURCE[0]}" SessionStart; }
  o="$(go s1 resume)";  [ -z "$o" ] && [ ! -e "$t/lens-profile-part2-s1" ] && echo "✓ пауза (resume): профілю й позначки частини 2 нема" || { echo "✗ resume: профіль або позначка є"; bad=1; }
  o="$(go s2 fork)";    [ -z "$o" ] && [ ! -e "$t/lens-profile-part2-s2" ] && echo "✓ копія розмови (fork): так само" || { echo "✗ fork: профіль або позначка є"; bad=1; }
  o="$(go s3 compact)"; case "$o" in *'Частина 1/2'*) [ -e "$t/lens-profile-part2-s3" ] && [ ! -e "$t/lens-env-s3.txt" ] && echo "✓ стиснення (compact): профіль повторено, env_check не ганяється" || { echo "✗ compact: позначки нема або env_check ганявся"; bad=1; };; *) echo "✗ compact: профілю нема"; bad=1;; esac
  o="$(go s4 startup)"; case "$o" in *'Частина 1/2'*) grep -q '⚠ тест: увага' "$t/lens-env-s4.txt" 2>/dev/null && grep -q '✗ тест: червоне' "$t/lens-env-s4.txt" && grep -q '✗ 3 — глянь' "$t/lens-env-s4.txt" && ! grep -q 'база: ok' "$t/lens-env-s4.txt" && ! grep -q '⚠24' "$t/lens-env-s4.txt" && [ "$(grep -c 'спільне: хмара' "$t/lens-env-s4.txt")" = 1 ] && echo "✓ старт (startup): профіль + файл env_check — лише тривоги (підсумок «⚠24 · ✗0» мовчить, «✗ 3» — ні), однаковий рядок двох репо — раз" || { echo "✗ startup: файл env_check не той: $(tr '\n' '|' < "$t/lens-env-s4.txt" 2>/dev/null | cut -c1-200)"; bad=1; };; *) echo "✗ startup: профілю нема"; bad=1;; esac
  p="$(printf '{"session_id":"s4","prompt":"працюємо"}' | LENS_PROFILE=1 LENS_REPOS_ROOT="$t/repos" LENS_ENV_DIR="$t" LENS_MARK_DIR="$t" bash "${BASH_SOURCE[0]}" UserPromptSubmit)"
  case "$p" in *'Частина 2/2'*'✗ тест: червоне'*) [ ! -e "$t/lens-env-s4.txt" ] && echo "✓ перше повідомлення: частина 2 профілю + рядки env_check; файл спожито" || { echo "✗ файл env_check не спожито"; bad=1; };; *) echo "✗ перше повідомлення без рядків env_check: $(printf '%s' "$p" | cut -c1-160)"; bad=1;; esac
  mkdir -p "$t/repos/a/.git"; : > "$t/repos/a/.git/lens-readonly"; printf 'echo "усе гаразд"\n' > "$t/repos/b/tools/env_check.sh"; o="$(go s5 startup)"; grep -q 'нема (репо: b)' "$t/lens-env-s5.txt" 2>/dev/null && echo "✓ усе зелене → один рядок «⚠ / ✗ нема (репо: …)»; клон лише для читання (з тривогами) не ганяється" || { echo "✗ зелений підсумок: $(cat "$t/lens-env-s5.txt" 2>/dev/null)"; bad=1; }
  o="$(printf '{"session_id":"s7","source":"startup"}' | LENS_ENV_AUTO=0 LENS_PROFILE=1 LENS_REPOS_ROOT="$t/repos" LENS_ENV_DIR="$t" LENS_MARK_DIR="$t" LENS_SKILLS_DIR="$t/skills" bash "${BASH_SOURCE[0]}" SessionStart)"
  [ ! -e "$t/lens-env-s7.txt" ] && case "$o" in *'Частина 1/2'*) true;; *) false;; esac && echo "✓ вимикач LENS_ENV_AUTO=0: env_check не ганяється, профіль на місці" || { echo "✗ вимикач LENS_ENV_AUTO=0 не спрацював"; bad=1; }
  rm -rf "$t/skills"; o="$(go s8 startup)"; case "$o" in *'"reloadSkills": true'*'Частина 1/2'*|*'Частина 1/2'*'"reloadSkills": true'*) [ -f "$t/skills/night/SKILL.md" ] && echo "✓ навички ядра: скопійовано в теку навичок, reloadSkills у тому ж JSON, що й профіль" || { echo "✗ навички: файла нема"; bad=1; };; *) echo "✗ навички: reloadSkills нема у виводі"; bad=1;; esac
  o="$(go s9 startup)"; case "$o" in *reloadSkills*) echo "✗ навички без змін → reloadSkills зайвий"; bad=1;; *'Частина 1/2'*) echo "✓ навички без змін → без reloadSkills, профіль на місці";; *) echo "✗ навички без змін: профілю нема"; bad=1;; esac
  c="$(printf '{}' | bash "${BASH_SOURCE[0]}" PreCompact)"; n=${#c}; [ "$n" -gt 200 ] && [ "$n" -le 10000 ] && echo "✓ PreCompact: інструкції для переказу ($n знаків ≤ 10 000)" || { echo "✗ PreCompact: $n знаків"; bad=1; }
  s="$(printf '{"session_id":"s6","last_assistant_message":"Готово, без рядка."}' | LENS_SHADOW_DIR="$t" bash "${BASH_SOURCE[0]}" Stop)"
  [ -z "$s" ] && grep -q 'memory-line	no-line' "$t/lens-shadow-s6.tsv" 2>/dev/null && echo "✓ Stop: тінь memory-line записала вирок і нічого не заблокувала" || { echo "✗ тінь: вивід «$s», файл: $(cat "$t/lens-shadow-s6.tsv" 2>/dev/null | cut -c1-120)"; bad=1; }
  # AE S141 (В-352): ctx_watch у трьох місцях — після коміту · повідомлення Konst · після стиснення; кожне — один чинний JSON
  python3 -c 'import json,sys
u=lambda c:{"input_tokens":2,"cache_read_input_tokens":c-1002,"cache_creation_input_tokens":1000,"cache_creation":{"ephemeral_1h_input_tokens":1000}}
r=[{"type":"assistant","timestamp":"2099-01-01T00:00:00Z","message":{"id":"m1","content":[],"usage":u(330000)}},{"type":"system","subtype":"compact_boundary","compactMetadata":{"trigger":"auto","preTokens":371723,"postTokens":14494}}]
open(sys.argv[1],"w").write(json.dumps(r[0])+"\n"); open(sys.argv[2],"w").write("\n".join(json.dumps(x) for x in r)+"\n")' "$t/big.jsonl" "$t/cmp.jsonl"
  ok() { printf '%s' "$1" | python3 -c 'import json,sys; d=json.loads(sys.stdin.read()); a=d["hookSpecificOutput"]["additionalContext"]; sys.exit(0 if all(x in a for x in sys.argv[1:]) else 1)' "${@:2}" 2>/dev/null; }
  e="CLAUDE_CODE_AUTO_COMPACT_WINDOW=450000 CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=92"
  o="$(printf '{"session_id":"c1","hook_event_name":"PostToolUse","tool_name":"Bash","tool_input":{"command":"git commit -m x"},"transcript_path":"%s"}' "$t/big.jsonl" | env $e LENS_ROOT="$t/none" bash "${BASH_SOURCE[0]}" PostToolUse)"
  ok "$o" "⚠ контекст 330 тис." "ревізія на 325 тис." && echo "✓ ctx_watch після коміту: 330 тис. → ⚠ одним JSON" || { echo "✗ ctx_watch після коміту: «$(printf '%s' "$o" | cut -c1-120)»"; bad=1; }
  o="$(printf '{"session_id":"c2","hook_event_name":"UserPromptSubmit","prompt":"далі","transcript_path":"%s"}' "$t/big.jsonl" | env $e LENS_REPOS_ROOT="$t/repos" LENS_ENV_DIR="$t" LENS_MARK_DIR="$t" bash "${BASH_SOURCE[0]}" UserPromptSubmit)"
  ok "$o" "⚠ контекст 330 тис." && echo "✓ ctx_watch на повідомлення Konst: ⚠ у контексті" || { echo "✗ ctx_watch на повідомлення: «$(printf '%s' "$o" | cut -c1-120)»"; bad=1; }
  o="$(printf '{"session_id":"c3","hook_event_name":"SessionStart","source":"compact","transcript_path":"%s"}' "$t/cmp.jsonl" | env $e LENS_PROFILE=1 LENS_REPOS_ROOT="$t/repos" LENS_ENV_DIR="$t" LENS_MARK_DIR="$t" LENS_SKILLS_DIR="$t/skills" bash "${BASH_SOURCE[0]}" SessionStart)"
  ok "$o" "Частина 1/2" "371 тис. → 14 тис." && echo "✓ ctx_watch після стиснення: «371 тис. → 14 тис.» і профіль в одному JSON" || { echo "✗ ctx_watch після стиснення: «$(printf '%s' "$o" | tail -c 160)»"; bad=1; }
  rm -rf "$t"; exit $bad
fi
if [ "$ev" = SessionStart ] || [ "$ev" = profile-test ]; then
  ss_in=""; [ "$ev" = SessionStart ] && ss_in="$(cat 2>/dev/null)"   # JSON події — читаємо ПЕРШИМ: хук репо міг би з'їсти stdin
  [ "$ev" = SessionStart ] && repo_hooks
  # профіль — двома частинами ≤ 10 000 знаків кожна (стеля additionalContext Claude Code; понад — лише прев'ю 2 000): 1 — тут, 2 — у перше повідомлення Konst (profile_parts.py)
  prof() { [ "${LENS_PROFILE:-}" = 1 ] && [ -f "$h/../PROFILE.md" ] || return 0
    python3 -c 'import json,sys,subprocess; t=subprocess.run([sys.executable,sys.argv[1],"1"],capture_output=True,text=True).stdout; print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":t}},ensure_ascii=False))' "$h/profile_parts.py"; }
  if [ "$ev" = profile-test ]; then
    on="$(LENS_PROFILE=1 prof)"; off="$(LENS_PROFILE= prof)"; bad=0
    case "$on" in *'"hookEventName": "SessionStart"'*'Частина 1/2'*) echo "✓ LENS_PROFILE=1 → профіль у контексті (частина 1: $(printf '%s' "$on" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]))') знаків)";; *) echo "✗ LENS_PROFILE=1 → профілю нема"; bad=1;; esac
    python3 "$h/profile_parts.py" test | sed 's/^/  /'; [ "${PIPESTATUS[0]}" = 0 ] || bad=1
    [ -z "$off" ] && echo "✓ без LENS_PROFILE → тиша (профіль — у полі налаштувань акаунта)" || { echo "✗ без LENS_PROFILE → профіль усе одно"; bad=1; }
    exit $bad
  fi
  ss_sid="$(printf '%s' "$ss_in" | grep -o '"session_id" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' | tr -cd 'A-Za-z0-9_-')"
  ss_src="$(printf '%s' "$ss_in" | grep -o '"source" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
  # FAB-1 (10.11.2026): після паузи машини (resume) і при копії розмови (fork) профіль уже в розмові — позначку частини 2 не ставимо. Замір: за 2,5 год
  #   сесії частина 2 прийшла 5 разів при одній частині 1 (4 дублі по 3 899 знаків). Після стиснення (compact) повтор потрібен — лишається.
  #   source — code.claude.com/docs/en/hooks «SessionStart input» (startup · resume · clear · compact · fork), 10.11.2026.
  case "$ss_src" in resume|fork) exit 0 ;; esac
  case "$ss_src" in startup|"") env_all "${ss_sid:-nosession}" ;; esac
  md="${LENS_MARK_DIR:-/tmp}"
  # AE S141 (В-351, «так» Konst на /night): навички ядра (tools/claude-code/skills/*/SKILL.md) → ~/.claude/skills/; навички репо в хмарній сесії
  #   з кількома репо самі не вантажаться (тека сесії — не репо; code.claude.com/docs/en/skills «Where skills live», 12.11.2026) → копія + reloadSkills
  #   (hooks «Reload skills that a hook installs»: без нього навичка, записана гачком, може не з'явитися до першого повідомлення). Ключ — у той самий JSON.
  rs=0; for d in "$h"/../skills/*/; do [ -f "$d/SKILL.md" ] || continue; sd="${LENS_SKILLS_DIR:-$HOME/.claude/skills}/$(basename "$d")"
    cmp -s "$d/SKILL.md" "$sd/SKILL.md" 2>/dev/null || { mkdir -p "$sd" && cp "$d/SKILL.md" "$sd/SKILL.md" && rs=1; }; done 2>/dev/null
  o="$(prof)"; [ "$ss_src" = compact ] && o="$(mrg "$o" "$(printf '%s' "$ss_in" | python3 "$h/ctx_watch.py" hook 2>/dev/null)")"   # AE S141 (В-352): після стиснення — рядок «контекст · стиснення на · ревізія на»
  if [ "$rs" = 1 ]; then [ -n "$o" ] || o='{"hookSpecificOutput":{"hookEventName":"SessionStart"}}'; printf '%s' "$o" | python3 -c 'import json,sys; d=json.load(sys.stdin); d["hookSpecificOutput"]["reloadSkills"]=True; print(json.dumps(d,ensure_ascii=False))'
  elif [ -n "$o" ]; then printf '%s\n' "$o"; fi; [ "${LENS_PROFILE:-}" = 1 ] && { date +%H:%M > /tmp/lens-profile-loaded; : > "$md/lens-profile-part2-${ss_sid:-nosession}"; } 2>/dev/null; exit 0   # позначка для profile_check.sh (рядок «профіль» в env_check)
fi
# PreCompact (CTX-1, FAB-1 10.11.2026): stdout гачка Claude Code бере як інструкції для переказу при стисненні (code.claude.com/docs/en/hooks «PreCompact output»,
#   10.11.2026; ≤ 10 000 знаків) — один файл ядра на всі репо замість розділу «Compact instructions» у кожному CLAUDE.md
[ "$ev" = PreCompact ] && { LENS_HOOKS="$h" bash "$h/precompact_guard.sh"; exit $?; }   # AE S140 (FAB-2, «так» Konst): сторож «ревізія → /compact» — ручне стиснення з незакоміченим / незапушеним → вихід 2 (зупинено), авто — ніколи; інструкції переказу + факти git — його stdout
case "$ev" in pre|PreToolUse) ev=pre;; post|PostToolUse) ev=post;; stop|Stop) ev=stop;; UserPromptSubmit) ev=prompt;; *) exit 0;; esac
in="$(cat)"
tool="$(printf '%s' "$in" | grep -o '"tool_name" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
sid="$(printf '%s' "$in" | grep -o '"session_id" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' | tr -cd 'A-Za-z0-9_-')"
# журнал спрацювань (HOOK-5, 10.10.2026): кожна відповідь гачка — рядок у /tmp/lens-hooks-<сесія>.tsv (час · подія · гачок · суть);
# на переїзді handoff_check рахує їх і вимагає вердикти в tools/claude-code/hooks/HOOK_JOURNAL.md (справжнє · хибне · дубль · пропуск)
fire() {   # $1 — гачок, $2 — його вивід (не порожній)
  # стеля Claude Code: текст гачка понад 10 000 знаків модель бачить лише прев'ю на 2 000 (docs hooks «JSON output», 22.10.2026) → рядок «⚠ стеля» у журнал спрацювань
  n="$(printf '%s' "$2" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); h=d.get("hookSpecificOutput") or {}; print(max(len(str(h.get(k,""))) for k in ("additionalContext","permissionDecisionReason")) if h else len(str(d.get("reason",""))))
except Exception: print(0)' 2>/dev/null)"
  [ "${n:-0}" -gt 10000 ] && printf '%s	%s	%s	%s
' "$(date -u +%FT%TZ)" "$ev" "$1" "⚠ СТЕЛЯ: текст гачка $n знаків > 10 000 — модель бачить лише прев'ю 2 000; розбити (profile_parts.py) або скоротити" >> "/tmp/lens-hooks-${sid:-nosession}.tsv" 2>/dev/null
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$ev" "$1" "$(printf '%s' "$2" | tr '\n\t' '  ' | sed 's/"permissionDecisionReason": *"//;s/"reason": *"//;s/"additionalContext": *"//' | cut -c1-200)" >> "/tmp/lens-hooks-${sid:-nosession}.tsv" 2>/dev/null
  printf '%s\n' "$2"
}
run() { out="$(printf '%s' "$in" | bash "$h/$1" $2 2>/dev/null)"; [ -n "$out" ] && { fire "${1%.sh}" "$out"; return 0; }; return 1; }
case "$ev" in
  pre)
    case "$tool" in Write|Edit|Bash) ;; *) exit 0;; esac
    for g in "brief-guard.sh pre" "ui-guard.sh check" "commit-gate.sh" "ui-review-gate.sh gate" "review-remind.sh stand"; do
      read -r f a <<<"$g"
      run "$f" "$a" && exit 0
    done ;;
  post)
    case "$tool" in Read|Bash|Grep|WebSearch|WebFetch) ;; *) exit 0;; esac
    printf '%s' "$in" | bash "$h/ui-guard.sh" mark 2>/dev/null
    # після коміту — два нагадування можуть збігтись (огляд UI · бриф, BRIEF-2 19.10.2026): одне повідомлення, обидва тексти
    o1="$(printf '%s' "$in" | bash "$h/review-remind.sh" post 2>/dev/null)"; o2="$(printf '%s' "$in" | bash "$h/brief-guard.sh" post 2>/dev/null)"
    po=""   # AE S141: вивід збирається в одне повідомлення — після коміту до нього додається рядок ctx_watch (один JSON на подію)
    [ -n "$o1" ] && [ -z "$o2" ] && po="$(fire review-remind "$o1")"
    [ -z "$o1" ] && [ -n "$o2" ] && po="$(fire brief-guard "$o2")"
    [ -n "$o1" ] && [ -n "$o2" ] && po="$(fire "review-remind+brief-guard" "$(python3 -c 'import json,sys; a,b=(json.loads(x)["hookSpecificOutput"] for x in sys.argv[1:3]); print(json.dumps({"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":a["additionalContext"]+"\n\n"+b["additionalContext"]}},ensure_ascii=False))' "$o1" "$o2")")"
    [ -z "$o1" ] && [ -z "$o2" ] && [ "$tool" = Bash ] && po="$(run handoff-remind.sh post || run env-remind.sh post)"
    # AE S141 (В-352): після кожного `git commit` — ctx_watch: ⚠, коли контекст ≥ порога ревізії (крок нічної зміни закінчується комітом, а повідомлень Konst уночі нема)
    c=""; [ "$tool" = Bash ] && c="$(printf '%s' "$in" | python3 "$h/ctx_watch.py" hook 2>/dev/null)"; [ -n "$c" ] && po="$(mrg "$po" "$(fire ctx-watch "$c")")"
    [ -n "$po" ] && printf '%s\n' "$po" ;;   # + пам'ять після коміту (AE S109): нові ✗ / ⚠ handoff_check   # коміт змінив аркуш середовища → запропонувати оновити (ENV-1)
  stop)   # перший з відповіддю перемагає: гачок пам'яті, перевірка перед переїздом (HOOK-3.2), «план без світу» (HOOK-2.5)
    # тінь (FAB-1, 10.11.2026): кандидат на заміну memory-guard — перевірка рядка «пам'ять: …» проти стану git. Лише пише вирок у
    #   /tmp/lens-shadow-<сесія>.tsv, нічого не друкує й не блокує; підсумок сесії — python3 memory_line.py tally <сесія> (рядком у журнал гачків)
    printf '%s' "$in" | python3 "$h/memory_line.py" shadow "${sid:-nosession}" > /dev/null 2>&1
    run memory-guard.sh stop || run handoff-remind.sh stop || run plan-web.sh stop ;;
  prompt)   # перевірка перед переїздом (HOOK-3.2), інакше — аркуш середовища на прохання (ENV-1), інакше — «пропуск, знайдений Konst» (HOOK-5)
    o="$(run handoff-remind.sh "" || run env-remind.sh "" || run konst-miss.sh "")"
    r="$(run route-remind.sh "")"   # AE S135 · маршрут для Konst — додається до будь-якого іншого гачка, не витісняє (route-remind.sh)
    [ -n "$r" ] && o="$(python3 -c 'import json,sys
a,b=sys.argv[1],sys.argv[2]
if not a.strip(): print(b); sys.exit()
x=json.loads(a); y=json.loads(b); h=x.setdefault("hookSpecificOutput",{"hookEventName":"UserPromptSubmit"})
h["additionalContext"]=(h.get("additionalContext","")+"\n\n"+y["hookSpecificOutput"]["additionalContext"]).strip(); print(json.dumps(x,ensure_ascii=False))' "$o" "$r" 2>/dev/null || printf '%s' "$o")"
    c="$(printf '%s' "$in" | python3 "$h/ctx_watch.py" hook 2>/dev/null)"; [ -n "$c" ] && o="$(mrg "$o" "$(fire ctx-watch "$c")")"   # AE S141 (В-352): контекст ≥ порогів ревізії / кеш холодний
    ef="${LENS_ENV_DIR:-/tmp}/lens-env-${sid:-nosession}.txt"   # FAB-1: ⚠ / ✗ env_check кожного репо, зібрані на старті (env_all) — раз, у перше повідомлення
    if [ -s "$ef" ]; then
      o="$(python3 -c 'import json,sys
a=sys.argv[1]; e=open(sys.argv[2],encoding="utf-8",errors="replace").read()[:4000]
txt="СТАН РЕПО НА СТАРТІ (env_check кожного репо сесії — прогнав гачок старту; тут лише рядки ⚠ / ✗, повний вивід — bash tools/env_check.sh у репо). Скажи про них Konst одразу після «що ти побачиш»:\n"+e
try: x=json.loads(a) if a.strip() else {}
except Exception: x={}
h=x.setdefault("hookSpecificOutput",{"hookEventName":"UserPromptSubmit"}); h["additionalContext"]=(txt+"\n\n"+h.get("additionalContext","")).strip(); print(json.dumps(x,ensure_ascii=False))' "$o" "$ef" 2>/dev/null || printf '%s' "$o")"
      rm -f "$ef"
    fi
    pf="${LENS_MARK_DIR:-/tmp}/lens-profile-part2-${sid:-nosession}"
    if [ "${LENS_PROFILE:-}" = 1 ] && [ -f "$pf" ]; then rm -f "$pf"; python3 "$h/profile_parts.py" 2 | python3 "$h/profile_parts.py" merge "$o"   # частина 2 профілю — у перше повідомлення після старту чи стиснення
    elif [ -n "$o" ]; then printf '%s\n' "$o"; fi ;;
esac
exit 0
