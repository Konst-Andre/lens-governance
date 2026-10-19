#!/bin/bash
# живе доки: UI-кроки (HTML/CSS, стенди) робить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (черга ARCH-1 (ґ)(д)).
# Нагадування, не заборона: програма не може вимагати огляд, але може покласти факт у контекст агента в потрібну мить.
#   post  — PostToolUse (диспетчер lens-hooks.sh шле Read|Bash|Grep|WebSearch|WebFetch; коміт — лише Bash, позначка маніфесту — будь-який із них): щойно зроблений `git commit` змінив .html/.css, а позначки огляду (ui-review-gate done) на ці файли
#           за останні 2 год нема → «коміт UI обійшов огляд» (раз на SHA). Є позначка — тиша: огляд до коміту вже вимагає ui-review-gate
#           (HOOK-2 п.4, 09.10.2026); тут лишилась страхувальна сітка — гачок-ворота впав, вимкнений чи коміт пройшов повз нього
#           + позначка «маніфест стендів прочитано», якщо виклик згадав Lens_stagebench_manifest
#   stand — PreToolUse (Write|Edit|Bash): запис .html зі «стенд / bench / harness / компер» у шляху, а маніфест у цій сесії не читано → нагадування
#           + ВИДАЧА: `git push` у репо з origin `…/sandbox` (прев'ю для Konst) → пункти чек-листа «Перед видачею» маніфесту, прочитані з самого маніфесту
#           (не копія: копія тухне), раз на коміт. Тригер — подія видачі, не ім'я файла (бриф SB-1 «Х7»: «stand» у konstandre/standalone — 2 хибних)
# Формат — hookSpecificOutput.additionalContext (code.claude.com/docs/en/hooks, 08.10.2026): текст — фактами, не наказами.
mode="$1"
if [ "$mode" = selftest ]; then   # stand: адреса з «stand» усередині слова — тиша; .html стенда чи компера — нагадування (хибне QR CC-8)
  ok=0; n=0
  for c in "0|curl -s https://qr-lens.konstandre.workers.dev/ | grep -o 'x[^>]*'; grep a tools/QR_Lens_zvit_template.html" \
           "1|cat a > kernel/stage/AE_stand_v3.html" "1|cp x tools/compare_v2.htm" "0|echo hi > notes.md" \
           "0|cat > docs/CHERGA.md <<X
джерело — ANC_island_animations_standalone_v1.html
X"; do
    n=$((n+1)); want="${c%%|*}"; cmd="${c#*|}"
    got=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"selftest%s" % sys.argv[2],"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$cmd" "$n$$" | bash "$0" stand | grep -c 'Стенди')
    [ "$got" = "$want" ] && ok=$((ok+1)) || echo "✗ stand: «$cmd» → $got, очікував $want"
  done
  # видача: push у sandbox → нагадування; push в інше репо і коміт у sandbox → тиша
  sb=$(mktemp -d); ot=$(mktemp -d)
  for r in "$sb|https://github.com/Konst-Andre/sandbox.git" "$ot|https://github.com/Konst-Andre/QR-Lens.git"; do
    d="${r%%|*}"; git -C "$d" init -q; git -C "$d" remote add origin "${r#*|}"; git -C "$d" -c user.name=t -c user.email=t@t commit -q --allow-empty -m x
  done
  for c in "1|cd $sb && git push -u origin main" "1|git -C $sb push origin main" "0|cd $ot && git push origin main" "0|cd $sb && git commit -m x"; do
    n=$((n+1)); want="${c%%|*}"; cmd="${c#*|}"
    got=$(python3 -c 'import json,sys; print(json.dumps({"session_id":"selftest%s" % sys.argv[2],"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$cmd" "$n$$" | bash "$0" stand | grep -c 'Пункти: 1)')
    [ "$got" = "$want" ] && ok=$((ok+1)) || echo "✗ видача: «$cmd» → $got, очікував $want"
  done
  rm -rf "$sb" "$ot"
  echo "review-remind selftest: $ok/$n"; [ "$ok" = "$n" ]; exit
fi
export RR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -c '
import json, sys, re, os, subprocess, time, ast
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
        try:   # чек-лист — один, у воротах ui-review-gate.sh (копія тут відставала — аудит 09.10)
            src = open(os.path.join(os.environ.get("RR_DIR", "."), "ui-review-gate.sh"), encoding="utf-8").read()
            check = ast.literal_eval(re.search(r"CHECK = (\(.*?\))\n\n", src, re.S).group(1))
        except Exception:
            check = "чек-лист — lens-governance:tools/claude-code/hooks/ui-review-gate.sh (CHECK)"
        say("PostToolUse", f"Коміт {chr(59).join(out)} змінив UI-файли без позначки огляду: ворота ui-review-gate його не зупинили "
            "(гачок упав, вимкнений чи коміт пройшов повз). Наступний крок — сказати Konst і зробити огляд, "
            f"окремим проходом, {check}; знахідки → правки → ще прохід → лише тоді прев\u2019ю Konst.")
elif mode == "stand":
    tool = d.get("tool_name", "")
    cmd = str(ti.get("command", "")) if tool == "Bash" else ""
    for m in re.finditer(r"\bgit\b((?:\s+-C\s+\S+)?)[^;&|]*?\bpush\b", cmd):   # видача стенда Konst = push у sandbox
        cds = re.findall(r"(?:^|&&|;)\s*cd\s+([^\s;&|]+)", cmd[:m.start()])
        repo = m.group(1).split()[-1] if m.group(1).strip() else (os.path.expanduser(cds[-1]) if cds else d.get("cwd") or ".")
        url = subprocess.run(["git", "-C", repo, "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
        if not re.search(r"/sandbox(\.git)?$", url): continue
        sha = subprocess.run(["git", "-C", repo, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        mark = f"/tmp/lens-issue-{sid}-{sha}"
        if os.path.exists(mark): sys.exit(0)
        open(mark, "w").close()
        man = os.path.join(os.environ.get("RR_DIR", "."), "..", "..", "..", "kernel", "Lens_stagebench_manifest.md")
        try:
            sec = open(man, encoding="utf-8").read().split("## Перед видачею", 1)[1].split("\n## ", 1)[0]
            items = [f"{n}) {t}" for n, t in re.findall(r"(?m)^\| (\d) \| \*\*(.+?)\*\*", sec)]
        except Exception:
            items = []
        say("PreToolUse", "Перед видачею стенда Konst (push у sandbox — далі посилання): чек-лист «Перед видачею» маніфесту lens-governance:kernel/Lens_stagebench_manifest.md, "
            "доказ кожного пункту одним блоком у повідомленні Konst (рядок паспорта · вивід смоуку · число · знімок) або «н/з, бо …». "
            + ("Пункти: " + " · ".join(items) + "." if items else "Розділ «Перед видачею» в маніфесті не знайдено — гачок відстав від маніфесту, скажи Konst."))
        sys.exit(0)
    if os.path.exists(seen): sys.exit(0)
    path = str(ti.get("file_path", "")) if tool in ("Write", "Edit") else str(ti.get("command", ""))
    if tool == "Bash" and not re.search(r"(>|\btee\b|\bcp\b|\bmv\b)", path): sys.exit(0)
    # лише в імені .html-файлу, не в усій команді: «konstandre» в адресі давало хибне (QR CC-8, 10.10)
    # і лише ЦІЛЬ запису (> · tee · аргументи cp/mv), не згадка в тексті: «…standalone_v1.html» у heredoc для .md давало хибне (S90 AE, 18.10)
    names = ([f for f in re.findall(r"(?:>\s*|\btee\s+(?:-a\s+)?)([^\s\x27\x22|;&<>]+)", path) + [w for s in re.findall(r"\b(?:cp|mv)\b[^|;&\n]*", path) for w in s.split()]]
             if tool == "Bash" else [path])
    if any(re.search(r"(stand|stend|bench|harness|compar|стенд|компер)", f, re.I) for f in names if re.search(r"\.html?$", f, re.I)):
        open(seen, "w").close()
        say("PreToolUse", "Стенди, харнеси й компери Lens описує маніфест ядра lens-governance:kernel/Lens_stagebench_manifest.md (буфер — lens-governance:kernel/Lens_stagebench_delta_running.md); "
            "у цій сесії його ще не відкривали (lens-governance:CLAUDE.md «Звідки брати»: «будую чи правлю стенд, харнес, компер, важелі»). "
            "Перед посиланням Konst (push у sandbox) стенд звіряють з розділом маніфесту «Перед видачею» — з доказом кожного пункту.")
' "$mode"
exit 0
