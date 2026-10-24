#!/bin/bash
# живе доки: коміти в репо Lens робить агент Claude Code (lens-governance: kernel/Lens_governance_CHERGA.md HOOK-2 п.1).
# Гачок «коміт → спершу гейт»: Bash із `git commit` → для кожного репо, де комітять, ганяє гейт ядра;
# ✗ → deny з рядками ✗ (урок QR-Lens CC-2, 08.10.2026: `| tail -1` сховав exit гейта → коміт з ✗).
#   ядро (є kernel/Lens_validate.py) → --gov · продукт Lens (є lens/*_INDEX.md) → --product · інше репо → тиша.
# Репо коміту: останній `cd <шлях>` перед `git commit` у тому ж ланцюжку, `git -C <шлях>` або cwd гачка. Гейт ~1 с.
# + база (AE S94, аудит 19.10 A1): при ✗ — той самий гейт на HEAD (тимчасовий worktree, ~1 с, лише коли коміт уже зупинено);
#   ✗, що є й на HEAD, позначено «(було до правки)» — агент одразу бачить, що ✗ не його, і називає його Konst.
# + сторож файлів коміту (commit_files.py, HOOK-2 п.«нові файли», QR CC-12 14.10.2026) — у БУДЬ-ЯКОМУ репо: що коміт внесе, включно з `git add -A` тієї ж команди.
if [ "${1-}" = selftest ]; then   # AE S104: пошук `git commit` — справжній коміт ⟂ текст у тілі heredoc
  ok=0; n=0; me="$(readlink -f "${BASH_SOURCE[0]}")"
  t(){ n=$((n+1)); local got; got=$(python3 -c "import json,sys; print(json.dumps({\"tool_name\":\"Bash\",\"tool_input\":{\"command\":sys.argv[1]}}))" "$2" | COMMIT_GATE_DETECT=1 bash "$me"); [ "$got" = "$1" ] && { ok=$((ok+1)); echo "✓ $3"; } || echo "✗ $3 → $got, очікував $1"; }
  t none "python3 - <<'EOF'
say(check(d, \"git add -A && git commit -m x\") == [], 'випадок')
EOF" "тіло heredoc з текстом «git add -A && git commit» → не коміт (хибне AE S104)"
  t commit "cd /x && git add -A && git commit -m x" "справжній коміт після cd → коміт"
  t commit "git add -A && git commit -q -F - <<'EOF'
повідомлення
ядро: ні
EOF" "коміт з повідомленням у heredoc → коміт"
  echo "commit-gate selftest: $ok/$n"; [ "$ok" = "$n" ]; exit
fi
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" python3 -c '
import json, sys, re, os, glob, subprocess
d = json.load(sys.stdin)
if d.get("tool_name") != "Bash": sys.exit(0)
cmd = str((d.get("tool_input") or {}).get("command", ""))
# тіла heredoc — текст (скрипт, повідомлення коміту), не команди: для пошуку `git commit` їх вирізаємо (AE S104 24.10.2026, хибне: python3 - <<EOF
#   з рядками selftest «git add -A && git commit -m …» → гейт ганявся й зупиняв правку); повний cmd — далі в commit_files (там «ядро: …» з повідомлення)
L, keep, i = cmd.split("\n"), [], 0
while i < len(L):
    keep.append(L[i]); m = re.search(r"<<-?\s*[\x22]?(?:\x27)?(\w+)(?:\x27)?[\x22]?", L[i]); i += 1
    if m:
        while i < len(L) and L[i].strip() != m.group(1): i += 1
scan = "\n".join(keep)
GITC = r"^\s*(?:\w+=\S*\s+)*git\b(?:\s+-[cC]\s+\S+)*\s+commit\b"   # git … commit на початку команди; у тексті рядка (Python, heredoc) — ні (хибне 08.10 QR CC-4 · 19.10 AE S94)
found = any(re.match(GITC, s) for s in re.split(r"&&|\|\||;|\||\n", scan))
if os.environ.get("COMMIT_GATE_DETECT") == "1": print("commit" if found else "none"); sys.exit(0)   # selftest: лише пошук коміту
if not found: sys.exit(0)
cwd, dirs = d.get("cwd") or os.getcwd(), []
for seg in re.split(r"&&|\|\||;|\n", scan):
    m = re.match(r"\s*cd\s+(\"[^\"]+\"|\x27[^\x27]+\x27|\S+)", seg)
    if m: cwd = os.path.expanduser(m.group(1).strip("\"\x27")) if os.path.isabs(os.path.expanduser(m.group(1).strip("\"\x27"))) else os.path.join(cwd, m.group(1).strip("\"\x27"))
    if re.match(GITC, seg):
        c = re.search(r"\bgit\s+-C\s+(\S+)", seg)
        dirs.append(os.path.join(cwd, c.group(1)) if c else cwd)
kern = next((k for k in ("/home/user/lens-governance", "/tmp/lens-governance") if os.path.exists(k + "/kernel/Lens_validate.py")), None)
bad = []
sys.path.insert(0, os.environ.get("H", ""))
try:
    import commit_files
except Exception:
    commit_files = None
for dd in dict.fromkeys(dirs):
    top = subprocess.run(["git", "-C", dd, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not top: continue
    if commit_files:
        try:
            cf = commit_files.check(top, cmd)
        except Exception:
            cf = []
        if cf: bad.append(os.path.basename(top) + " — файли коміту: " + " · ".join(cf[:6]))
    if os.path.exists(top + "/kernel/Lens_validate.py"):
        run = ["python3", top + "/kernel/Lens_validate.py", "--gov", top]
    elif glob.glob(top + "/lens/*_INDEX.md") and kern:
        run = ["python3", kern + "/kernel/Lens_validate.py", "--product", top]
    else:
        continue
    try:
        r = subprocess.run(run, capture_output=True, text=True, cwd=top, timeout=60)
    except subprocess.TimeoutExpired:   # без цього Python падає з 1 → Claude Code вважає помилку гачка незначною і пропускає коміт без гейта
        bad.append(f"{os.path.basename(top)}: гейт не встиг за 60 с — запусти руками"); continue
    if r.returncode != 0:
        lines = [l.strip() for l in r.stdout.splitlines() if "✗" in l and "ПІДСУМОК" not in l][:8]
        base = set()
        wt = subprocess.run(["mktemp", "-d"], capture_output=True, text=True).stdout.strip()
        try:   # база — той самий гейт на HEAD; збій бази не блокує відповідь гачка
            if wt and subprocess.run(["git", "-C", top, "worktree", "add", "-q", "--detach", wt + "/b", "HEAD"], capture_output=True).returncode == 0:
                rb = [x.replace(top, wt + "/b") if x.startswith(top) else x for x in run]
                if os.path.exists(top + "/kernel/Lens_validate.py"): rb[1] = wt + "/b/kernel/Lens_validate.py"
                ob = subprocess.run(rb, capture_output=True, text=True, cwd=wt + "/b", timeout=60).stdout.replace(wt + "/b", top)
                base = {l.strip() for l in ob.splitlines() if "✗" in l}
        except Exception:
            pass
        finally:
            subprocess.run(["git", "-C", top, "worktree", "remove", "--force", wt + "/b"], capture_output=True); subprocess.run(["rm", "-rf", wt])
        bad.append(f"{os.path.basename(top)}: " + " · ".join(l + (" (було до правки)" if l in base else "") for l in lines))
if bad:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "Гейт ✗ — коміт зупинено (HOOK-2 п.1). " + " | ".join(bad) +
        " → виправ ✗ і коміть знову; гачок пропускає лише ✗ 0; ✗ з позначкою «(було до правки)» є й на HEAD — не твій: назви його Konst. Гейт бачить стан ДО всієї команди: правки — однією командою, коміт — наступною."}}, ensure_ascii=False))
sys.exit(0)
'
