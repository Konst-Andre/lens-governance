#!/bin/bash
# живе доки: UI-кроки (HTML/CSS) робить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (HOOK-1); копії в репо — як є.
# Гачок «UI без кукбука — не пиши»: правило «перед UI — індекс кукбука» тримає програма, не пам'ять моделі
# (урок QR-Lens CC-2, 08.10.2026: сторінку звіту зробили без кукбука → «дешево»).
#   mark  — PostToolUse (Read|Bash|Grep): у виклику згадано Lens_cookbook_INDEX → позначка сесії
#   check — PreToolUse (Write|Edit|Bash): запис .html/.css (Write/Edit або Bash із записом) без позначки → deny з причиною
# Раз на сесію: після одного звернення до індексу все дозволено. Формат — code.claude.com/docs/en/hooks (08.10.2026).
mode="$1"
python3 -c '
import json, sys, re, os
mode = sys.argv[1]
d = json.load(sys.stdin)
sid = re.sub(r"[^A-Za-z0-9_-]", "", str(d.get("session_id") or "nosession"))
mark = f"/tmp/lens-ui-{sid}"
ti = d.get("tool_input") or {}
tool = d.get("tool_name", "")
raw = json.dumps(ti, ensure_ascii=False)
if mode == "mark":
    if "Lens_cookbook_INDEX" in raw:
        open(mark, "w").close()
    sys.exit(0)
if os.path.exists(mark):
    sys.exit(0)
ui = re.compile(r"\.(html?|css)\b", re.I)
if tool in ("Write", "Edit"):
    hit = bool(ui.search(str(ti.get("file_path", ""))))
elif tool == "Bash":
    cmd = str(ti.get("command", ""))
    hit = bool(ui.search(cmd)) and bool(re.search(r"(>|\btee\b|\bcp\b|\bmv\b|sed\s+-i|\.write|open\()", cmd))
else:
    hit = False
if hit:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "UI-крок (HTML/CSS) без кукбука: спершу відкрий kernel/cookbook/Lens_cookbook_INDEX.md ядра (../lens-governance/ або /tmp/lens-governance/) "
        "(§2 «задача → запис» → потрібні рецепти точково) і знайди зразки ззовні (профіль, ЦИКЛ п.4). Рецепт — фундамент, не шаблон. "
        "Після одного звернення до індексу гачок пропускає все в цій сесії (HOOK-1)."}}, ensure_ascii=False))
sys.exit(0)
' "$mode"
