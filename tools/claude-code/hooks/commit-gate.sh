#!/bin/bash
# живе доки: коміти в репо Lens робить агент Claude Code (lens-governance: kernel/Lens_governance_CHERGA.md HOOK-2 п.1).
# Гачок «коміт → спершу гейт»: Bash із `git commit` → для кожного репо, де комітять, ганяє гейт ядра;
# ✗ → deny з рядками ✗ (урок QR-Lens CC-2, 08.10.2026: `| tail -1` сховав exit гейта → коміт з ✗).
#   ядро (є kernel/Lens_validate.py) → --gov · продукт Lens (є lens/*_INDEX.md) → --product · інше репо → тиша.
# Репо коміту: останній `cd <шлях>` перед `git commit` у тому ж ланцюжку, `git -C <шлях>` або cwd гачка. Гейт ~1 с.
python3 -c '
import json, sys, re, os, glob, subprocess
d = json.load(sys.stdin)
if d.get("tool_name") != "Bash": sys.exit(0)
cmd = str((d.get("tool_input") or {}).get("command", ""))
if not re.search(r"\bgit\b[^\n;&|]*\bcommit\b", cmd): sys.exit(0)
cwd, dirs = d.get("cwd") or os.getcwd(), []
for seg in re.split(r"&&|\|\||;|\n", cmd):
    m = re.match(r"\s*cd\s+(\"[^\"]+\"|\x27[^\x27]+\x27|\S+)", seg)
    if m: cwd = os.path.expanduser(m.group(1).strip("\"\x27")) if os.path.isabs(os.path.expanduser(m.group(1).strip("\"\x27"))) else os.path.join(cwd, m.group(1).strip("\"\x27"))
    if re.search(r"\bgit\b[^\n]*\bcommit\b", seg):
        c = re.search(r"\bgit\s+-C\s+(\S+)", seg)
        dirs.append(os.path.join(cwd, c.group(1)) if c else cwd)
kern = next((k for k in ("/home/user/lens-governance", "/tmp/lens-governance") if os.path.exists(k + "/kernel/Lens_validate.py")), None)
bad = []
for dd in dict.fromkeys(dirs):
    top = subprocess.run(["git", "-C", dd, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not top: continue
    if os.path.exists(top + "/kernel/Lens_validate.py"):
        run = ["python3", top + "/kernel/Lens_validate.py", "--gov", top]
    elif glob.glob(top + "/lens/*_INDEX.md") and kern:
        run = ["python3", kern + "/kernel/Lens_validate.py", "--product", top]
    else:
        continue
    r = subprocess.run(run, capture_output=True, text=True, cwd=top, timeout=60)
    if r.returncode != 0:
        lines = [l.strip() for l in r.stdout.splitlines() if "✗" in l][:8]
        bad.append(f"{os.path.basename(top)}: " + " · ".join(lines))
if bad:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "Гейт ✗ — коміт зупинено (HOOK-2 п.1). " + " | ".join(bad) +
        " → виправ ✗ або, якщо ✗ було й до правки, назви це Konst; потім коміть знову."}}, ensure_ascii=False))
sys.exit(0)
'
