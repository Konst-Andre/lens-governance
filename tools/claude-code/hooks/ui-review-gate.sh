#!/bin/bash
# живе доки: UI-кроки (HTML/CSS) комітить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (черга ядра HOOK-2 п.4).
# «Огляд UI — ДО коміту, не після» (урок QR-Lens CC-5, 09.10.2026: review-remind нагадував після `commit && push` — зміна вже в проді;
# агент перевірив поведінку, а не вигляд результату дії; мок тесту знав лише очікувані кінці → картка висіла двічі).
#   gate  — PreToolUse (Bash з `git commit`): у репо коміту змінено .html/.htm/.css (проти HEAD, разом з новими файлами), а позначки
#           огляду САМЕ ЦЬОГО диффу нема → deny з чек-листом. Будь-яка нова правка UI після позначки міняє дифф → знову deny.
#   done  — `bash ui-review-gate.sh done "<що переглянуто>" [тека репо]` (відмова gate дає готову команду з текою репо коміту) → позначка /tmp/lens-uireview-<хеш диффу> (рядок ≥ 40 знаків:
#           які стани, які теми, що бачить людина після дії). Самоствердження, але в потрібну мить і по конкретному диффу.
#   selftest — 13 випадків (з них 2 — сітка review-remind post, 4 — done ⟂ ui_lint) у тимчасовому репо (зуби: UI без позначки → deny; позначка → тиша; правка після позначки → deny; done без ui_lint → ✗).
#   hash  — хеш диффу UI репо (для ui_lint: позначка /tmp/lens-uilint-<хеш> — машинна частина огляду, бриф §HOOK-2.5).
#   done вимагає позначку ui_lint САМЕ ЦЬОГО диффу (✗ 0 в обох темах) або --no-lint \"<причина ≥ 30 знаків>\" (сторінку не запустити) — причина пишеться в позначку.
# Діє в усіх репо, де підключено гачки ядра (tools/claude-code/CLAUDE_CODE.md «Гачки»), — не лише в QR.
mode="$1"; shift
[ "$mode" = gate ] && HOOK_IN="$(cat)" || HOOK_IN="{}"   # stdin — тут: heredoc нижче займає stdin python
export HOOK_IN
UI_GATE_SELF="$(readlink -f "${BASH_SOURCE[0]}")" python3 - "$mode" "$@" <<'PY'
import json, sys, re, os, subprocess, hashlib, tempfile, shutil
mode, args = sys.argv[1], sys.argv[2:]
UI = ["*.html", "*.htm", "*.css"]
CHECK = ("чек-лист огляду (як користувач, а не лише тест поведінки): кожен стан і кожна дія — світла тема цілком, потім темна; "
         "дія → результат: після тапу людина бачить, що сталося, що змінилось і де перевірити самій; довга дія — хід до кінця "
         "(і всі реальні кінці джерела: успіх · помилка · «не буде» · немає прав), стан після перезавантаження; "
         "кожна кнопка — шлях до кінця, приймач розуміє, є зворотна дія (wsd 3.9); текст «як кажуть люди»; поле = well, кнопка = lift; "
         "кожен новий елемент — окремим кропом 1:1, не мініатюрою (на зменшених знімках губляться капсула, «приклеєна» до краю, і розтягнуті іконки); "
         "вага кнопок: дія > другорядна дія > перехід — різна форма, не лише колір; "
         "матеріал карток; переноси й обрізання; консоль; скрол убік; мок зовнішнього джерела — лише з його реальних кінців "
         "(коди відповідей, права токена, пропущені кроки), не з очікуваних; "
         "повний екран у кожному стані (порожньо · завантаження · помилка · успіх), не лише кропи нового: нове ⟂ старе на тому ж екрані (стара кнопка поруч з новою дією); "
         "одна головна дія на екран, другорядне приглушити, а не головне роздути; відступи — зі шкали (4 · 8 · 12 · 16 · 24), не випадкові; "
         "кнопка називає результат («Завантажити KPI», не «ОК»); помилка — що сталося · чому · що робити (каже «скажи агенту» — поруч кнопка «Скопіювати для Claude» зі знімком збою: дія · відповідь сервера · номери · час · версія сторінки); стан, якого не досягти на здоровій системі (збій, «не стартував», порожньо), — Konst отримує спосіб побачити його сам: демо-режим за входом або прев'ю, посилання у звіті; «іди тестуй» без такого способу — не звіт; текст без жаргону — або прибрати, якщо зайвий; "
         "машинне (обрізання, прилипання, контраст, тап, ряд, iOS-зум, скрол) — tools/claude-code/ui_lint.mjs, ✗ 0 в обох темах")

def git(top, *a, raw=False):
    r = subprocess.run(["git", "-C", top, *a], capture_output=True)
    return r.stdout if raw else r.stdout.decode("utf-8", "replace").strip()

def ui_state(top):   # (файли UI, хеш диффу) — дифф проти HEAD + нові неігноровані файли
    files = sorted(set(git(top, "diff", "HEAD", "--name-only", "--", *UI).splitlines()) |
                   set(git(top, "ls-files", "--others", "--exclude-standard", "--", *UI).splitlines()))
    files = [f for f in files if f]
    if not files: return [], None
    h = hashlib.sha1(git(top, "diff", "HEAD", "--", *UI, raw=True))
    for f in git(top, "ls-files", "--others", "--exclude-standard", "--", *UI).splitlines():
        p = os.path.join(top, f)
        if os.path.isfile(p): h.update(f.encode()); h.update(open(p, "rb").read())
    return files, h.hexdigest()

def mark(hx): return f"/tmp/lens-uireview-{hx}"

def gate(d):
    if d.get("tool_name") != "Bash": return None
    cmd = str((d.get("tool_input") or {}).get("command", ""))
    if not re.search(r"\bgit\b[^\n;&|]*\bcommit\b", cmd): return None
    cwd, dirs = d.get("cwd") or os.getcwd(), []
    for seg in re.split(r"&&|\|\||;|\n", cmd):   # тека коміту — як у commit-gate: останній cd перед ним, git -C, або cwd
        m = re.match(r"\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)", seg)
        if m:
            p = os.path.expanduser(m.group(1).strip("\"'")); cwd = p if os.path.isabs(p) else os.path.join(cwd, p)
        if re.search(r"\bgit\b[^\n]*\bcommit\b", seg):
            c = re.search(r"\bgit\s+-C\s+(\S+)", seg); dirs.append(os.path.join(cwd, c.group(1)) if c else cwd)
    bad = []
    for dd in dict.fromkeys(dirs):
        top = git(dd, "rev-parse", "--show-toplevel")
        if not top: continue
        files, hx = ui_state(top)
        if files and not os.path.exists(mark(hx)): bad.append((top, files, hx))
    if not bad: return None
    why = " | ".join(f"{os.path.basename(t)}: {', '.join(f[:4])}{' …' if len(f) > 4 else ''} (дифф {h[:8]})" for t, f, h in bad)
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": f"Огляд UI до коміту: змінено UI — {why}; позначки огляду цього диффу нема. "
            f"Спершу огляд окремим проходом — {CHECK}. Знахідки → правки → ще прохід. Потім позначка (тека репо — останнім аргументом): "
            + " · ".join(f"bash {os.environ.get('UI_GATE_SELF', 'tools/claude-code/hooks/ui-review-gate.sh')} done \"<що переглянуто: стани, теми, що бачить людина після дії>\" {t}" for t, _, _ in bad)
            + " — і коміть знову."}}

if mode == "gate":
    out = gate(json.loads(os.environ.get("HOOK_IN") or "{}"))
    if out: print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)

if mode == "hash":   # для ui_lint: той самий хеш диффу UI, що й тут (позначка lint — на цей дифф)
    top = git(args[0] if args else os.getcwd(), "rev-parse", "--show-toplevel")
    print(ui_state(top)[1] if top else ""); sys.exit(0)

def lint_mark(hx): return f"/tmp/lens-uilint-{hx}"

if mode == "done":
    nolint = args[args.index("--no-lint") + 1] if "--no-lint" in args and args.index("--no-lint") + 1 < len(args) else None
    rest = [a for i, a in enumerate(args) if a != "--no-lint" and not (i > 0 and args[i - 1] == "--no-lint")]
    note = rest[0] if rest else ""
    top = git(rest[1] if len(rest) > 1 else os.getcwd(), "rev-parse", "--show-toplevel")
    if len(note) < 40: print("✗ рядок огляду < 40 знаків — назви стани, теми й що бачить людина після дії"); sys.exit(1)
    if not top: print("✗ не git-репо"); sys.exit(1)
    files, hx = ui_state(top)
    if not files: print("ⓘ змін UI нема — позначка не потрібна"); sys.exit(0)
    # машинна частина огляду (HOOK-2.5): ui_lint на ЦЬОМУ диффі дав ✗ 0 в обох темах — або чесна причина, чому сторінку не запустити
    lint = os.path.exists(lint_mark(hx))
    if not lint and not (nolint and len(nolint) >= 30):
        ul = os.path.join(os.path.dirname(os.path.dirname(os.environ.get("UI_GATE_SELF", "x/x"))), "ui_lint.mjs")
        print(f"✗ ui_lint цього диффу ({hx[:8]}) не пройдено: node {ul} <url|файл> [--state \"<js>\"]… --repo {top} → ✗ 0 в обох темах; "
              f"сторінку не запустити — done \"<огляд>\" {top} --no-lint \"<чому, ≥ 30 знаків>\""); sys.exit(1)
    open(mark(hx), "w").write(note + ("" if lint else f"\n[без ui_lint: {nolint}]") + "\n" + "\n".join(files) + "\n")
    print(f"✓ позначка огляду {hx[:8]} · {os.path.basename(top)}: {', '.join(files)}" + ("" if lint else " · ⚠ без ui_lint — причина записана")); sys.exit(0)

if mode == "selftest":
    tmp = tempfile.mkdtemp(); bad = 0; n = 0
    def say(ok, m):
        global bad, n; n += 1; bad += not ok; print(("✓ " if ok else "✗ ") + m)
    try:
        for c in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]): subprocess.run(["git", "-C", tmp, *c], check=True)
        open(f"{tmp}/a.html", "w").write("<p>1</p>"); open(f"{tmp}/n.md", "w").write("x")
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "0"], check=True)
        ev = lambda cmd: {"tool_name": "Bash", "cwd": tmp, "tool_input": {"command": cmd}}
        open(f"{tmp}/n.md", "w").write("y")
        say(gate(ev("git add -A && git commit -m x")) is None, "зміна лише .md → тиша")
        open(f"{tmp}/a.html", "w").write("<p>2</p>")
        say(gate(ev("git add -A && git commit -m x")) is not None, "зуби: .html змінено, позначки нема → deny")
        say(gate(ev("git status")) is None, "не коміт → тиша")
        files, hx = ui_state(tmp); open(mark(hx), "w").write("огляд: світла й темна, стан після дії, перезавантаження\n")
        say(gate(ev(f"cd {tmp} && git commit -am x")) is None, "позначка цього диффу → тиша")
        open(f"{tmp}/a.html", "w").write("<p>3</p>")
        say(gate(ev("git commit -am x")) is not None, "зуби: правка UI після позначки → знову deny")
        open(f"{tmp}/b.css", "w").write("p{}")
        say(gate(ev("git add -A && git commit -m x")) is not None, "новий .css (ще не в git) теж рахується → deny")
        r = subprocess.run(["bash", os.environ["UI_GATE_SELF"], "gate"], input=json.dumps(ev("git add -A && git commit -m x")), capture_output=True, text=True)
        say('"deny"' in r.stdout, "зуби: справжній виклик гачка (JSON через stdin, як від Claude Code) → deny")
        os.remove(mark(hx))
        # done вимагає ui_lint на цьому диффі (HOOK-2.5)
        dn = lambda *a: subprocess.run(["bash", os.environ["UI_GATE_SELF"], "done", *a], capture_output=True, text=True)
        files, hx = ui_state(tmp); note = "огляд: світла й темна, стан після дії, перезавантаження сторінки"
        r = dn(note, tmp); say(r.returncode == 1 and "ui_lint" in r.stdout and not os.path.exists(mark(hx)), "зуби: done без ui_lint цього диффу → ✗, позначки нема")
        open(lint_mark(hx), "w").write("✗0"); r = dn(note, tmp); say(r.returncode == 0 and os.path.exists(mark(hx)), "done з позначкою ui_lint цього диффу → ✓")
        os.remove(mark(hx)); os.remove(lint_mark(hx))
        r = dn(note, tmp, "--no-lint", "коротко"); say(r.returncode == 1, "зуби: --no-lint без причини (< 30 знаків) → ✗")
        r = dn(note, tmp, "--no-lint", "CSS листа, сторінки в браузері немає — лише шаблон"); say(r.returncode == 0 and "без ui_lint" in open(mark(hx)).read(), "--no-lint з причиною → ✓, причина в позначці")
        os.remove(mark(hx))
        # сітка review-remind post: UI-коміт без позначки → озивається; з позначкою на ці файли → тиша (без дубля)
        rr = os.path.join(os.path.dirname(os.environ["UI_GATE_SELF"]), "review-remind.sh")
        post = lambda sid: subprocess.run(["bash", rr, "post"], input=json.dumps({"tool_name": "Bash", "session_id": sid, "cwd": tmp, "tool_input": {"command": "git commit -am x"}}), capture_output=True, text=True).stdout
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "1"], check=True)
        say(bool(post(f"st{os.getpid()}a")), "сітка: UI-коміт без позначки огляду → нагадування «обійшов огляд»")
        open(f"{tmp}/a.html", "w").write("<p>4</p>"); files, hx = ui_state(tmp)
        open(mark(hx), "w").write("огляд: світла й темна\n" + "\n".join(files) + "\n")
        subprocess.run(["git", "-C", tmp, "commit", "-qam", "2"], check=True)
        say(not post(f"st{os.getpid()}b"), "сітка: UI-коміт з позначкою → тиша (без дубля з воротами)")
        os.remove(mark(hx))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"─── ui-review-gate selftest: {n - bad}/{n} ───"); sys.exit(1 if bad else 0)
PY
