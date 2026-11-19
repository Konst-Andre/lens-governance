#!/usr/bin/env bash
# run-guard · «не правити дерево, яке зараз судить фоновий прогін» (AE S156, В-414). Той самий пропуск — AE S131 двічі і S156 ще раз:
#   агент правив site/ посеред фонового gates_v1, сторож дерева продукту ловив це лише в кінці (7 хв прогону — у смітник). Тут — зупинка ДО правки.
# живе доки: продукти ганяють довгі прогони (гейти, обходи) у фоні, поки агент працює далі.
# Контракт для БУДЬ-ЯКОГО продукту (рядок у ADOPT · «Що тут лежить»): прогін на старті —
#     G=$(LENS_RUN_GUARD_PID=$$ bash <ядро>/tools/claude-code/hooks/run-guard.sh lock "$PWD" site tools); trap 'rm -f "$G"' EXIT
#   ($$ — явно: усередині $(…) $PPID — це підоболонка, вона помирає одразу, і замок вважався б мертвим)
#   замок /tmp/lens-run-guard/<pid прогону>: рядок 1 — корінь, рядок 2 — теки через пробіл, рядок 3 — час старту. Процесу нема — замок прибирається сам
#   (прогін, убитий без trap, гачка не заклинить).
# pre — PreToolUse (stdin JSON): Write|Edit — file_path у теці замка → deny; Bash — команда пише в теку замка (> · >> · tee · sed -i · cp · mv · rm ·
#   install · truncate · open(…'w'/'a') · writeFile · git checkout|stash|restore|reset|pull|merge|rebase|apply|am у корені) → deny. Читання (cat, grep,
#   git diff / log / commit) не блокується: коміт не міняє вмісту, а сторож дерева продукту судить саме вміст. Свідомо — у команді «# run-guard: ok <чому>».
# selftest — зуби (RUN_GUARD_INJECT=1 — замок не бачиться → ✗).
D="${LENS_RUN_GUARD_DIR:-/tmp/lens-run-guard}"
case "${1:-}" in
  lock)
    root="$(cd "${2:-.}" && pwd)"; shift 2; mkdir -p "$D"; f="$D/${LENS_RUN_GUARD_PID:-$PPID}"
    printf '%s\n%s\n%s\n' "$root" "$*" "$(date +%H:%M)" > "$f"; echo "$f"; exit 0 ;;
  pre)
    [ -d "$D" ] || exit 0
    INJ="${RUN_GUARD_INJECT:-}" D="$D" python3 -c '
import json, os, re, sys
try: d = json.load(sys.stdin)
except Exception: sys.exit(0)
D = os.environ["D"]; tool = d.get("tool_name", ""); ti = d.get("tool_input") or {}; cwd = d.get("cwd") or os.getcwd()
locks = []
for p in os.listdir(D):
    f = os.path.join(D, p)
    try:
        os.kill(int(p), 0)
    except (ValueError, ProcessLookupError):
        try: os.remove(f)
        except OSError: pass
        continue
    except PermissionError: pass
    try: L = open(f, encoding="utf-8").read().split("\n")
    except OSError: continue
    if len(L) >= 2 and L[0]: locks.append((p, L[0].rstrip("/"), [x.strip("/") for x in L[1].split() if x], (L[2] if len(L) > 2 else "")))
if os.environ.get("INJ") == "1": locks = []
if not locks: sys.exit(0)
def hit(path):
    if not path: return None
    a = os.path.normpath(path if os.path.isabs(path) else os.path.join(cwd, path))
    for pid, root, dirs, t in locks:
        for x in dirs:
            if a == root + "/" + x or a.startswith(root + "/" + x + "/"): return (pid, root, x, t)
    return None
why = None
if tool in ("Write", "Edit", "NotebookEdit"):
    why = hit(ti.get("file_path") or ti.get("notebook_path"))
elif tool == "Bash":
    c = ti.get("command") or ""
    if "run-guard: ok" not in c:
        # ЦІЛЬ запису, не згадка теки (S156: правка docs/DECISIONS.md з текстом «tools/…» — хибний deny). Тіло heredoc — дані програми, не оболонка:
        #   у ньому шукаємо лише open(…,'w'|'a') / writeFile / write_text; перенаправлення й дієслова (sed -i · mv · rm · tee · truncate; cp · install —
        #   останній аргумент) — лише в самій оболонці. Шлях — літерал або змінна з присвоєння; «cd <тека> && …» — далі відносно неї.
        sh, body, tag = [], [], None
        for ln in c.split("\n"):
            if tag is not None:
                if ln.strip() == tag: tag = None
                else: body.append(ln)
                continue
            sh.append(ln); m = re.search(r"<<-?\s*[\x27\"]?(\w+)[\x27\"]?", ln)
            if m: tag = m.group(1)
        S, B = "\n".join(sh), "\n".join(body)
        cds = re.findall(r"(?:^|[;&|]\s*|\n\s*)cd\s+([^\s;&|]+)", S)
        if cds: cwd = os.path.normpath(os.path.join(cwd, os.path.expanduser(cds[0].strip("\x27\""))))
        G = re.compile(r"\bgit\s+(checkout|stash|restore|reset|pull|merge|rebase|apply|am|cherry-pick|switch)\b")
        tg = [m.group(1) for m in re.finditer(r"(?<![0-9&<])>>?\s*([^\s&|;<>()]+)", S)]
        for m in re.finditer(r"\b(sed\s+-i\S*|mv|rm|tee|truncate|cp|install)\b([^;&|\n#]*)", S):
            a = [x.strip("\x27\"") for x in m.group(2).split() if not x.startswith("-")]
            tg += a[-1:] if m.group(1) in ("cp", "install") else a
        names = dict(re.findall(r"\b(\w+)\s*=\s*[\x27\"]([^\x27\"\n]+)[\x27\"]", c))
        for m in re.finditer(r"(?:open\(\s*([^,\)]+)\s*,\s*[\x27\"][wa]|writeFileSync\(\s*([^,\)]+)|writeFile\(\s*([^,\)]+)|(\w+|[\x27\"][^\x27\"]+[\x27\"])\.write_text)", c):
            a = next(g for g in m.groups() if g).strip()
            tg.append(a.strip("\x27\"") if a[:1] in "\x27\"" else names.get(a, ""))
        for x in tg:
            why = hit(x)
            if why: break
        if not why and G.search(S):
            for pid, root, dirs, t in locks:
                if os.path.normpath(cwd).startswith(root) or root in c: why = (pid, root, " · ".join(dirs), t); break
if why:
    pid, root, x, t = why
    msg = (f"Зараз іде фоновий прогін (процес {pid}, старт {t}): він судить {os.path.basename(root)}/{x}. Правка цієї теки посеред прогону робить його "
           "недійсним (сторож дерева продукту скаже це лише в кінці). Що робити: дочекатись кінця прогону (сповіщення прийде само) — тим часом можна "
           "правити все поза цією текою (документи, самері, інше репо); свідомо — додай у команду «# run-guard: ok <чому>» (AE S131 · S156, В-414).")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": msg}}, ensure_ascii=False))
' ;;
  selftest)
    T=$(mktemp -d); export LENS_RUN_GUARD_DIR="$T/locks"; R="$T/repo"; mkdir -p "$R/site/tools" "$R/docs"; n=0; ok=0
    sleep 300 & SP=$!
    LENS_RUN_GUARD_PID=$SP bash "$0" lock "$R" site tools > /dev/null
    j() { python3 -c 'import json,sys; t=sys.argv[1]; print(json.dumps({"tool_name":t,"cwd":sys.argv[3],"tool_input":({"command":sys.argv[2]} if t=="Bash" else {"file_path":sys.argv[2]})}))' "$@"; }
    t() { n=$((n+1)); got=$(j "$2" "$3" "${5:-$R}" | bash "$0" pre | grep -c '"deny"'); [ "$got" = "$4" ] && { ok=$((ok+1)); echo "  ✓ $1"; } || echo "  ✗ $1 (deny=$got, чекали $4)"; }
    t "Edit у теці прогону → deny"                     Edit "$R/site/tools/ae_rules.js" 1
    t "Write поза теками прогону (docs/) → можна"      Write "$R/docs/SUMMARY.md" 0
    t "Bash: python пише site/… (S156) → deny"         Bash "python3 - <<'EOF'
p='site/tools/ae_rules.js'; open(p,'w').write('x')
EOF" 1
    t "Bash: sed -i у tools/ → deny"                   Bash "sed -i s/a/b/ tools/x.py" 1
    t "Bash: читання (grep, cat) теки → можна"         Bash "grep -n foo site/index.html; cat tools/x.py" 0
    t "Bash: git commit у корені → можна (вміст той самий)" Bash "git commit -qam x" 0
    t "Bash: git stash у корені (S131) → deny"         Bash "git stash" 1
    t "Bash: свідомо «# run-guard: ok …» → можна"      Bash "sed -i s/a/b/ tools/x.py  # run-guard: ok тест" 0
    t "Bash: запис у чуже репо з іншого кореня → можна" Bash "echo x > site/a.txt" 0 "$T"
    t "Bash: прилад з tools/ пише вивід у /tmp → можна"  Bash "node tools/x.js site > /tmp/out.log 2>&1" 0
    t "Bash: перенаправлення в site/ → deny"            Bash "echo x > site/a.txt" 1
    t "Bash: python пише docs/, а текст згадує tools/ і «> site/» (S156) → можна" Bash "python3 - <<'EOF'
p='docs/D.md'; open(p,'w').write('див. tools/gates_v1.sh; echo x > site/a')
EOF" 0
    t "Bash: cp -r site /tmp/копія (читання) → можна"   Bash "cp -r site /tmp/site_old" 0
    t "Bash: cd <корінь> && sed -i tools/… з чужого cwd → deny" Bash "cd $R && sed -i s/a/b/ tools/x.py" 1 "$T"
    kill $SP 2>/dev/null; wait $SP 2>/dev/null
    t "процес прогону помер → замок геть, правка можна" Edit "$R/site/tools/ae_rules.js" 0
    [ -e "$LENS_RUN_GUARD_DIR/$SP" ] && echo "  ✗ мертвий замок лишився" || { n=$((n+1)); ok=$((ok+1)); echo "  ✓ мертвий замок прибрано"; }
    rm -rf "$T"; echo "run-guard selftest: $ok/$n"; [ "$ok" = "$n" ] ;;
  *) echo "run-guard.sh lock <корінь> <тека>… | pre | selftest" >&2; exit 2 ;;
esac
