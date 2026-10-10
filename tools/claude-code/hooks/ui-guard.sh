#!/bin/bash
# живе доки: UI-кроки (HTML/CSS) робить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (HOOK-1); копії в репо — як є.
# Гачок «UI без кукбука — не пиши»: правило «перед UI — індекс кукбука» тримає програма, не пам'ять моделі
# (урок QR-Lens CC-2, 08.10.2026: сторінку звіту зробили без кукбука → «дешево»).
#   mark  — PostToolUse (Read|Bash|Grep|WebSearch|WebFetch): згадано Lens_cookbook_INDEX → позначка «кукбук»; WebSearch/WebFetch → позначка «пошук ззовні»
#   check — PreToolUse (Write|Edit|Bash): запис .html/.css (Write/Edit або Bash із записом) без обох позначок → deny з причиною, що саме бракує
#   (пошук ззовні — з 10.10.2026, слово Konst: правило профілю «ПІДСИЛЕННЯ ІНТЕРНЕТОМ» модель пропускала; раз на сесію, як і кукбук)
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
web = mark + "-web"   # пошук практики ззовні (профіль ЦИКЛ п.4; слово Konst 10.10: правило, що не виконується, — програмою)
if mode == "mark":
    if "Lens_cookbook_INDEX" in raw:
        open(mark, "w").close()
    if tool in ("WebSearch", "WebFetch"):
        open(web, "w").close()
    sys.exit(0)
need = [x for x, f in (("кукбук", mark), ("пошук ззовні", web)) if not os.path.exists(f)]
if not need:
    sys.exit(0)
ui = re.compile(r"\.(html?|css)\b", re.I)
if tool in ("Write", "Edit"):
    hit = bool(ui.search(str(ti.get("file_path", ""))))
elif tool == "Bash":
    cmd = str(ti.get("command", ""))
    w = re.sub(r"\d?>>?&?\s*/dev/null|\d>&\d", "", cmd)   # 2>/dev/null, >/dev/null, 2>&1 — не запис (хибна відмова на «grep … 2>/dev/null», аудит 09.10)
    hit = bool(ui.search(cmd)) and bool(re.search(r"(>|\btee\b|\bcp\b|\bmv\b|sed\s+-i|\.write|open\()", w))
else:
    hit = False
if hit:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "UI-крок (HTML/CSS) — бракує: " + " і ".join(need) + ". "
        + ("Кукбук: kernel/cookbook/Lens_cookbook_INDEX.md ядра (../lens-governance/ або /tmp/lens-governance/), §2 «задача → запис» → потрібні рецепти точково. " if "кукбук" in need else "")
        + ("Пошук ззовні (WebSearch / WebFetch): як цю задачу розв\u2019язують сьогодні — патерн, кращий за наш рецепт, чи вада, яку ми не бачимо. " if "пошук ззовні" in need else "")
        + "Рецепт — наш найкращий результат на свою дату, фундамент, а не стеля: знайшов краще — зроби краще й онови рецепт. "
        "Без цього кроку правка UI повторює вже розв\u2019язане сімейством або йде проти рецепта (HOOK-1)."}}, ensure_ascii=False))
sys.exit(0)
' "$mode"
