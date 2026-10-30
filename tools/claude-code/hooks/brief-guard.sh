#!/bin/bash
# живе доки: пункти черги, що наросли рішеннями, ведуться брифами (tools/claude-code/templates/BRIEF_template.md; черга ядра BRIEF-2).
# Гачок «бриф — з шаблону і не протухає» (BRIEF-2, «так» Konst 19.10.2026, AE S93). Причина: бриф AE-PORT народився повз шаблон
# (скопіював форму kernel/Lens_kernel_BRIEFS.md; правило про шаблон жило лише в REPO_LAYOUT, далеко від дії) і за день мав 6 зроблених
# знахідок зі статусом «на вирок». Світ: «документ — тим самим PR, що й код» (docs-as-code) + шар «код → документ» (19.10.2026).
#   pre  — PreToolUse Write: НОВИЙ файл брифу (…/briefs/*.md, *_brief.md, *BRIEF*.md; не шаблон, не archive/) без «§0 Коротко»
#          → deny: «бриф — лише з шаблону». Правка наявного брифу — тиша (стару форму лікує перебудова, не блок).
#          + ознака за змістом (BRIEF-2 5г, AE S94): новий .md із «## §1 Навіщо» і «## §5 Кроки», але не з назвою брифу → deny «назви
#          `<id>_brief.md`» — інакше бриф не бачать ні цей гачок, ні handoff_check (8)/(9). Замір 19.10: обидва заголовки мають лише брифи (6 файлів).
#   post — PostToolUse Bash з `git commit`: коміт змінив не лише .md, а живий бриф репо в коміт не потрапив і в повідомленні нема
#          «бриф:» → нагадування (не блок): онови §0 «Коротко» брифу або напиши в коміті «бриф: без змін — <чому>».
#          AE S116: називає лише бриф, чий текст згадує змінений файл (шлях або ім'я) — хибне ×4 (AE S111–S113, S116: брифи ядра MOTION-1 /
#          ARCH-1 на кожен коміт приладу, жоден з них приладу не згадує); бриф без згадки — тиша (свідомий ризик: бриф кроку зазвичай називає свій файл).
#   selftest — зуби.
# Формат — hookSpecificOutput (code.claude.com/docs/en/hooks): pre — permissionDecision deny; post — additionalContext, фактами.
mode="${1:-pre}"
if [ "$mode" = selftest ]; then
  t=$(mktemp -d); n=0; ok=0; me="${BASH_SOURCE[0]}"
  chk() { n=$((n+1)); if [ "$2" = "$3" ]; then ok=$((ok+1)); echo "✓ $1"; else echo "✗ $1 — чекали «$3», маємо «$2»"; fi; }
  j() { python3 -c 'import json,sys; print(json.dumps({"tool_name":sys.argv[1],"cwd":sys.argv[2],"tool_input":{"file_path":sys.argv[3],"content":sys.argv[4],"command":sys.argv[3]}}))' "$@"; }
  mkdir -p "$t/r/docs/briefs" "$t/r/site"; git -C "$t/r" init -q; git -C "$t/r" config user.email t@t; git -C "$t/r" config user.name t
  printf '# B\n## §0 Коротко\n- **Стан:** x · `site/a.js`\n' > "$t/r/docs/briefs/X_brief.md"; printf '# W\n## §0 Коротко\n- **Стан:** інше\n' > "$t/r/docs/briefs/W_brief.md"; echo a > "$t/r/site/a.js"; echo a > "$t/r/site/b.js"; git -C "$t/r" add -A; git -C "$t/r" commit -qm init
  r=$(j Write "$t/r" "$t/r/docs/briefs/Y_brief.md" "# Y\n## Курс" | bash "$me" pre | grep -c deny); chk "новий бриф без «§0 Коротко» → deny" "$r" 1
  r=$(j Write "$t/r" "$t/r/docs/briefs/Y_brief.md" "# Y
## §0 Коротко
- **Стан:** y" | bash "$me" pre | grep -c deny); chk "новий бриф із шаблону → тиша" "$r" 0
  r=$(j Write "$t/r" "$t/r/docs/briefs/X_brief.md" "# стара форма" | bash "$me" pre | grep -c deny); chk "правка наявного брифу → тиша" "$r" 0
  r=$(j Write "$t/r" "$t/r/archive/briefs/Z_brief.md" "# Z" | bash "$me" pre | grep -c deny); chk "archive/ → тиша" "$r" 0
  r=$(j Write "$t/r" "$t/r/docs/plan_X.md" "# X
## §0 Коротко
## §1 Навіщо
## §5 Кроки" | bash "$me" pre | grep -c deny); chk "бриф за змістом під чужою назвою → deny (5г)" "$r" 1
  r=$(j Write "$t/r" "$t/r/docs/notes.md" "# N
## Навіщо
текст" | bash "$me" pre | grep -c deny); chk "лише «Навіщо» без «Кроки» → тиша" "$r" 0
  echo b > "$t/r/site/a.js"; git -C "$t/r" commit -qam "код без брифу"
  r=$(j Bash "$t/r" "git commit -m x" "" | bash "$me" post | grep -c additionalContext); chk "коміт коду без брифу → нагадування" "$r" 1
  echo c > "$t/r/site/a.js"; git -C "$t/r" commit -qam "код; бриф: без змін — дрібниця"
  r=$(j Bash "$t/r" "git commit -m x" "" | bash "$me" post | grep -c additionalContext); chk "«бриф: без змін — …» у коміті → тиша" "$r" 0
  echo d > "$t/r/site/a.js"; printf '\n- **Далі:** z\n' >> "$t/r/docs/briefs/X_brief.md"; git -C "$t/r" commit -qam "код + бриф"
  r=$(j Bash "$t/r" "git commit -m x" "" | bash "$me" post | grep -c additionalContext); chk "код + бриф одним комітом → тиша" "$r" 0
  echo e > "$t/r/site/b.js"; git -C "$t/r" commit -qam "код, якого жоден бриф не згадує"
  r=$(j Bash "$t/r" "git commit -m x" "" | bash "$me" post | grep -c additionalContext); chk "код, якого бриф не згадує → тиша (S116)" "$r" 0
  echo f > "$t/r/site/a.js"; git -C "$t/r" commit -qam "код зі згадкою"
  r=$(j Bash "$t/r" "git commit -m x" "" | bash "$me" post | grep -o 'X_brief[^,)]*\|W_brief' | sort -u | tr '\n' ' '); chk "названо лише бриф, що згадує файл (S116)" "$r" "X_brief.md "
  printf 'x\n' >> "$t/r/docs/briefs/X_brief.md"; git -C "$t/r" commit -qam "лише документ"
  r=$(j Bash "$t/r" "git commit -m x" "" | bash "$me" post | grep -c additionalContext); chk "коміт лише .md → тиша" "$r" 0
  rm -rf "$t"; echo "brief-guard selftest: $ok/$n"; [ "$ok" = "$n" ]; exit
fi
python3 -c '
import json, sys, os, re, subprocess
mode = sys.argv[1]; d = json.load(sys.stdin); ti = d.get("tool_input") or {}
BRIEF = re.compile(r"(/briefs/[^/]+\.md$|_brief\.md$|BRIEF[^/]*\.md$)")
def live(p): return BRIEF.search(p) and "/archive/" not in p and "templates/" not in p
if mode == "pre":
    if d.get("tool_name") != "Write": sys.exit(0)
    p = str(ti.get("file_path", "")); c = str(ti.get("content", ""))
    if os.path.exists(p) or not p.endswith(".md") or "/archive/" in p or "templates/" in p: sys.exit(0)
    if not live(p):
        if re.search(r"(?m)^##\s*(?:§1\s+)?Навіщо", c) and re.search(r"(?m)^##\s*(?:§5\s+)?Кроки", c):
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason":
                "За змістом це бриф (§1 Навіщо + §5 Кроки), а назва — ні: назви файл `<id>_brief.md` (або поклади в теку `briefs/`) — інакше його не бачать ні цей гачок, ні handoff_check (8)/(9), і він протухне непомітно (BRIEF-2 5г)."}}, ensure_ascii=False))
        sys.exit(0)
    if re.search(r"§0\s+Коротко", c): sys.exit(0)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason":
        "Новий бриф — лише з шаблону: скопіюй lens-governance:tools/claude-code/templates/BRIEF_template.md (§0 Коротко: Стан · Далі · Чекає → §1 Навіщо → §2 Готово, коли → §3 Рішення → §4 Що є → §5 Кроки → §6 Відкрите → §7 Як спрацював) і заповни. Бриф AE-PORT народився повз шаблон і за день протух (BRIEF-2, AE S93)."}}, ensure_ascii=False))
    sys.exit(0)
if d.get("tool_name") != "Bash" or not re.search(r"\bgit\b[^\n;&|]*\bcommit\b", str(ti.get("command", ""))): sys.exit(0)
cwd = d.get("cwd") or os.getcwd()
m = re.findall(r"\bcd\s+(\S+)", str(ti.get("command", "")))
if m: cwd = os.path.join(cwd, os.path.expanduser(m[-1]))
top = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
if not top: sys.exit(0)
msg = subprocess.run(["git", "-C", top, "log", "-1", "--format=%B"], capture_output=True, text=True).stdout
files = [x for x in subprocess.run(["git", "-C", top, "show", "--name-only", "--format=", "HEAD"], capture_output=True, text=True).stdout.split("\n") if x.strip()]
if not files or all(f.endswith(".md") for f in files) or re.search(r"бриф\s*:", msg, re.I): sys.exit(0)
briefs = [os.path.relpath(os.path.join(r, f), top) for r, _, fs in os.walk(top) if "/.git" not in r for f in fs if live(os.path.join(r, f).replace(os.sep, "/"))]
if not briefs or any(b in files for b in briefs): sys.exit(0)
code = [f for f in files if not f.endswith(".md")]
def names(b):   # AE S116: бриф стосується коміту, лише якщо згадує змінений файл — шляхом або іменем
    try: t = open(os.path.join(top, b), encoding="utf-8", errors="replace").read()
    except OSError: return False
    return any(f in t or os.path.basename(f) in t for f in code)
briefs = [b for b in briefs if names(b)]
if not briefs: sys.exit(0)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
    "Коміт змінив код (" + ", ".join(f for f in files if not f.endswith(".md"))[:120] + "), а живий бриф (" + ", ".join(briefs[:3]) + ") у нього не потрапив. Якщо коміт закриває чи змінює крок — §0 «Коротко» і рядок «Кроки» брифу правляться тим самим або наступним комітом; якщо бриф не стосується — рядок «бриф: без змін — <чому>» у повідомленні коміту (BRIEF-2)."}}, ensure_ascii=False))
' "$mode"
