#!/bin/bash
# живе доки: UI-кроки (HTML/CSS, стенди) робить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (черга ARCH-1 (ґ)(д)).
# Нагадування, не заборона: програма не може вимагати огляд, але може покласти факт у контекст агента в потрібну мить.
#   post  — PostToolUse (Bash): щойно зроблений `git commit` змінив .html/.css → нагадування «огляд окремим проходом» (раз на SHA)
#           + позначка «маніфест стендів прочитано», якщо виклик згадав Lens_stagebench_manifest
#   stand — PreToolUse (Write|Edit|Bash): запис .html зі «стенд / bench / harness / компер» у шляху, а маніфест у цій сесії не читано → нагадування
# Формат — hookSpecificOutput.additionalContext (code.claude.com/docs/en/hooks, 08.10.2026): текст — фактами, не наказами.
mode="$1"
python3 -c '
import json, sys, re, os, subprocess, time
mode = sys.argv[1]
d = json.load(sys.stdin)
sid = re.sub(r"[^A-Za-z0-9_-]", "", str(d.get("session_id") or "nosession"))
ti = d.get("tool_input") or {}
raw = json.dumps(ti, ensure_ascii=False)
seen = f"/tmp/lens-stand-{sid}"
def say(event, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}, ensure_ascii=False))
if mode == "post":
    if "Lens_stagebench_manifest" in raw: open(seen, "w").close()
    cmd = str(ti.get("command", ""))
    m = re.search(r"\bgit\b[^;&|]*\bcommit\b", cmd)
    if d.get("tool_name") != "Bash" or not m: sys.exit(0)
    cds = re.findall(r"(?:^|&&|;)\s*cd\s+([^\s;&|]+)", cmd[:m.start()])   # тека коміту — останній cd ПЕРЕД git commit (QR CC-3: cd після коміту збивав)
    repo = os.path.expanduser(cds[-1]) if cds else d.get("cwd") or "."
    g = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout.strip()
    sha, when = g("log", "-1", "--format=%h"), g("log", "-1", "--format=%ct")
    if not sha or not when or time.time() - int(when) > 120: sys.exit(0)          # коміту не було («nothing to commit») — HEAD старий
    mark = f"/tmp/lens-review-{sid}-{sha}"
    if os.path.exists(mark): sys.exit(0)
    ui = [f for f in g("show", "--name-only", "--format=", sha).splitlines() if re.search(r"\.(html?|css)$", f, re.I)]
    if not ui: sys.exit(0)
    open(mark, "w").close()
    say("PostToolUse", f"Коміт {sha} змінив UI-файли: {chr(44).join(ui[:5])}. За правилом Konst (черга ядра ARCH-1 (ґ), 08.10.2026) після такого кроку йде "
        "огляд окремим проходом: як користувач — кожен стан і кожна дія (таби, шіти, пошук, тапи, зміна висоти вікна); кожна тема окремо — "
        "спершу світла цілком, потім темна (тема ≠ інверсія); чек-лист: сильне · слабке · текст «як кажуть люди» · глибина (поле = well, кнопка = lift) · "
        "матеріал карток · переноси й обрізання · консоль · скрол убік; знахідки → правки → ще прохід → лише тоді прев’ю Konst.")
elif mode == "stand":
    if os.path.exists(seen): sys.exit(0)
    tool = d.get("tool_name", "")
    path = str(ti.get("file_path", "")) if tool in ("Write", "Edit") else str(ti.get("command", ""))
    if tool == "Bash" and not re.search(r"(>|\btee\b|\bcp\b|\bmv\b)", path): sys.exit(0)
    if re.search(r"\.html?\b", path, re.I) and re.search(r"(stand|stend|bench|harness|compar|стенд|компер)", path, re.I):
        open(seen, "w").close()
        say("PreToolUse", "Стенди, харнеси й компери Lens описує маніфест ядра kernel/Lens_stagebench_manifest.md (буфер — kernel/Lens_stagebench_delta_running.md); "
            "у цій сесії його ще не відкривали (lens-governance:CLAUDE.md «Звідки брати»: «будую чи правлю стенд, харнес, компер, важелі»).")
' "$mode"
exit 0
