#!/bin/bash
# живе доки: UI-кроки (HTML/CSS, стенди) робить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (черга ARCH-1 (ґ)(д)).
# Нагадування, не заборона: програма не може вимагати огляд, але може покласти факт у контекст агента в потрібну мить.
#   post  — PostToolUse (Bash): щойно зроблений `git commit` змінив .html/.css, а позначки огляду (ui-review-gate done) на ці файли
#           за останні 2 год нема → «коміт UI обійшов огляд» (раз на SHA). Є позначка — тиша: огляд до коміту вже вимагає ui-review-gate
#           (HOOK-2 п.4, 09.10.2026); тут лишилась страхувальна сітка — гачок-ворота впав, вимкнений чи коміт пройшов повз нього
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
    ms = list(re.finditer(r"\bgit\b[^;&|]*\bcommit\b", cmd))
    if d.get("tool_name") != "Bash" or not ms: sys.exit(0)
    out = []
    for m in ms:   # кожен коміт команди — зі своєю текою (QR CC-3: два коміти в одній команді, другий — з UI, гачок дивився лише на перший)
        cds = re.findall(r"(?:^|&&|;)\s*cd\s+([^\s;&|]+)", cmd[:m.start()])   # тека коміту — останній cd ПЕРЕД цим git commit
        repo = os.path.expanduser(cds[-1]) if cds else d.get("cwd") or "."
        if not os.path.isabs(repo): repo = os.path.normpath(os.path.join(os.path.expanduser(cds[-2]) if len(cds) > 1 and os.path.isabs(os.path.expanduser(cds[-2])) else d.get("cwd") or ".", repo))
        g = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout.strip()
        sha, when = g("log", "-1", "--format=%h"), g("log", "-1", "--format=%ct")
        if not sha or not when or time.time() - int(when) > 120: continue          # коміту не було («nothing to commit») — HEAD старий
        mark = f"/tmp/lens-review-{sid}-{sha}"
        if os.path.exists(mark): continue
        ui = [f for f in g("show", "--name-only", "--format=", sha).splitlines() if re.search(r"\.(html?|css)$", f, re.I)]
        if not ui: continue
        open(mark, "w").close()
        import glob
        seen_ui = set()
        for mk in glob.glob("/tmp/lens-uireview-*"):   # позначки ui-review-gate: рядок огляду + файли диффу
            if time.time() - os.path.getmtime(mk) < 7200: seen_ui |= set(open(mk, encoding="utf-8").read().splitlines()[1:])
        if set(ui) <= seen_ui: continue
        out.append(f"{sha} ({chr(44).join(ui[:5])})")
    if out:
        say("PostToolUse", f"Коміт {chr(59).join(out)} змінив UI-файли **без позначки огляду** (ворота ui-review-gate його не зупинили — "
            "гачок упав, вимкнений чи коміт пройшов повз). Скажи Konst і зроби огляд зараз, до наступного кроку (HOOK-2 п.4; ARCH-1 (ґ)): "
            "огляд окремим проходом: як користувач — кожен стан і кожна дія (таби, шіти, пошук, тапи, зміна висоти вікна); кожна тема окремо — "
            "спершу світла цілком, потім темна (тема ≠ інверсія); чек-лист: **кожна кнопка — шлях до кінця, приймач її розуміє, є зворотна дія (wsd 3.9 «Без заглушок»)** · сильне · слабке · текст «як кажуть люди» · глибина (поле = well, кнопка = lift) · "
            "матеріал карток · переноси й обрізання · консоль · скрол убік; знахідки → правки → ще прохід → лише тоді прев\u2019ю Konst.")
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
