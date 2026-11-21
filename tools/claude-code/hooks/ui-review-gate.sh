#!/bin/bash
# живе доки: UI-кроки (HTML/CSS) комітить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (черга ядра HOOK-2 п.4).
# «Огляд UI — ДО коміту, не після» (урок QR-Lens CC-5, 09.10.2026: review-remind нагадував після `commit && push` — зміна вже в проді;
# агент перевірив поведінку, а не вигляд результату дії; мок тесту знав лише очікувані кінці → картка висіла двічі).
#   gate  — PreToolUse (Bash з `git commit`): у репо коміту змінено .html/.htm/.css, файл примірки shots/**/fit_* (AE S127) або JS (.js / .mjs) поза tools/ · docs/ · test/ · tests/ · .claude/ · .github/ з НОВИМ текстом людині (AE S133, UI-VOICE: рядок у лапках, ≥ 2 слова кирилицею; проти HEAD, разом з новими файлами), а позначки
#           огляду САМЕ ЦЬОГО диффу нема → deny з чек-листом. Будь-яка нова правка UI після позначки міняє дифф → знову deny.
#   done  — `bash ui-review-gate.sh done "<що переглянуто>" [тека репо]` (відмова gate дає готову команду з текою репо коміту) → позначка /tmp/lens-uireview-<хеш диффу> (рядок ≥ 40 знаків:
#           які стани, які теми, що бачить людина після дії). Самоствердження, але в потрібну мить і по конкретному диффу.
#   selftest (лічбу друкує сам прогін; серед випадків — сітка review-remind post і done ⟂ ui_lint) у тимчасовому репо (зуби: UI без позначки → deny; позначка → тиша; правка після позначки → deny; done без ui_lint → ✗).
#   gate (push) — `git push` у репо з origin `…/sandbox` (прев'ю Konst; «так з підсиленням» Konst EquipLens S40, 21.11.2026 — v10 пішов у sandbox ДО огляду,
#           v11 пройшов повз ворота коміту, бо `cp && git commit && git push` — одна команда, а гачок бачить стан ДО неї): кожен новий / змінений *.html комітів, що
#           їдуть (upstream..HEAD), має позначку видачі ЦЬОГО вмісту (/tmp/lens-issue-<blob sha>) — інакше deny з готовою командою; push разом з комітом, cp / mv /
#           записом в одній команді → deny «окремою командою»; змінений наявний *_vN.html чи кореневий index.html → deny (профіль «ПРЕВ'Ю»: новий N, корінь не чіпати).
#           Практика: Review Board — зберігати SHA схвалених файлів, пройти може лише схвалений вміст (reviews.reviewboard.org/r/13282, 21.11.2026).
#   issue — `bash ui-review-gate.sh issue <файл.html> "<огляд ≥ 40>" "<перед видачею: 1 ✓ доказ … 7 н/з, бо …>"` → позначка видачі за git hash-object файла;
#           вимагає позначку ui_lint САМЕ ЦЬОГО вмісту (`node ui_lint.mjs <файл> [--baseline <база>]` → ✗ 0; --no-lint нема: файл ui_lint бере завжди) і всі пункти
#           «Перед видачею» маніфесту (номери читаються з маніфесту): ✓ з доказом ≥ 8 знаків або «н/з, бо …». Коміт файла з позначкою видачі ворота огляду пропускають.
#   hash  — хеш диффу UI репо (для ui_lint: позначка /tmp/lens-uilint-<хеш> — машинна частина огляду; закритий бриф `archive/summaries/Lens_gov/Lens_kernel_BRIEF_HOOK-2.5_closed.md`).
#   done вимагає позначку ui_lint САМЕ ЦЬОГО диффу (✗ 0 у темах продукту — типово обидві, --themes light|dark для продукту з однією схемою) або --no-lint "<причина ≥ 30 знаків>" (сторінку не запустити) — причина пишеться в позначку.
#   --no-lint не приймається, коли дифф ДОДАЄ текст людині (рядок у лапках чи текст між тегами, ≥ 2 слова кирилицею; коментарі зрізано) — пропуск Konst EquipLens S40.
# Діє в усіх репо, де підключено гачки ядра (tools/claude-code/CLAUDE_CODE.md «Гачки»), — не лише в QR.
mode="$1"; shift
[ "$mode" = gate ] && HOOK_IN="$(cat)" || HOOK_IN="{}"   # stdin — тут: heredoc нижче займає stdin python
export HOOK_IN
UI_GATE_SELF="$(readlink -f "${BASH_SOURCE[0]}")" python3 - "$mode" "$@" <<'PY'
import json, sys, re, os, subprocess, hashlib, tempfile, shutil
mode, args = sys.argv[1], sys.argv[2:]
UI = ["*.html", "*.htm", "*.css", ":(glob)**/shots/**/fit_*", ":(glob)shots/**/fit_*"]   # AE S127 (Konst: «чи можеш так завжди?»): накладка й знімальник примірки (fit_*.js / .py) — теж UI: примірку v1 з 7 вадами огляд ловив лише з доброї волі агента
# ③ голос людині: AE S133, Konst «відчуття, що писав агент»; guide.yukon.ca «How to help people recover from a form error», 06.11.2026
CHECK = ("чек-лист огляду (як користувач, а не лише тест поведінки). "
         "① стани й теми: кожен стан і кожна дія (порожньо · завантаження · помилка · успіх · після перезавантаження) — повний екран, світла тема цілком, потім темна; "
         "не лише кропи нового: нове ⟂ старе на тому ж екрані (стара кнопка поруч з новою дією); кожен новий елемент — ще й окремим кропом 1:1, не мініатюрою "
         "(на зменшених знімках губляться капсула, «приклеєна» до краю, і розтягнуті іконки); "
         "паритет тем: покращив місце в одній темі — те саме місце в іншій, щоб жодна не відставала (обʼєм тим інструментом, що живе в темі: A66); "
         "матеріал карток (поле = well, кнопка = lift); переноси й обрізання; консоль; скрол убік; відступи — зі шкали (4 · 8 · 12 · 16 · 24), не випадкові; "
         "є примірка цього екрана (shots/README.md, «обрано» / «у роботі») — знімок «після» тим самим кадром поруч з обраним — кроп 1:1 того самого стану, обидві теми, `python3 tools/claude-code/shots_same.py <примірка.png> <код.png>` ✓ (очі на дрібних кадрах пропустили сірий значок замість бірюзового), показати Konst (tools/claude-code/SHOTS.md §5); переносиш обрану примірку в продукт — `python3 tools/claude-code/port_same.py <port_*.json>` ✓ (порт ≡ примірка за предметами, станами, темами й рухом; done без нього — ✗, SHOTS.md §1 п. 4). "
         "② дія → результат: після тапу людина бачить, що сталося, що змінилось і де перевірити самій; довга дія — хід до кінця по всіх реальних кінцях джерела "
         "(успіх · помилка · «не буде» · немає прав); кожна кнопка — шлях до кінця, приймач розуміє, є зворотна дія (wsd 3.9); "
         "мок зовнішнього джерела — лише з тих самих реальних кінців (коди відповідей, права токена, пропущені кроки), не з очікуваних. "
         "③ ієрархія й текст: одна головна дія на екран, другорядне приглушити, а не головне роздути; вага кнопок: дія > другорядна дія > перехід — різна форма, не лише колір; відворотне «прибрати» — без підтвердження: одразу + «Повернути» на місці предмета (кнопка без підкреслення, секунди, пауза під мишею); підтвердження — лише для невідворотного, і там головна сама дія з точною назвою (кукбук A108, AE S135); "
         "другорядна кнопка — підйом матеріалу, не «примара» (біле на білому з тонкою рамкою читається як вимкнене); значок і текст в одній кнопці — на одній висоті (стрілку-символ шрифт ставить нижче — SVG); "
         "одна дія — один вигляд на всіх екранах (поставити поруч той самий елемент двох екранів: рамка, лінія на всю ширину, «Видалити»); "
         "кнопка називає результат («Завантажити KPI», не «ОК»); текст «як кажуть люди», без жаргону — або прибрати, якщо зайвий; текст людині (порада, попередження, «i») — повними реченнями, як сказала б людина, що допомагає: що сталося · що зробити, звертання «ви», без стискання до телеграми; еталон і пари «було → стало» — tools/claude-code/VOICE.md; чернетку — прочитати очима того, хто читатиме, і переписати раз; "
         "помилка — що сталося · чому · що робити (каже «скажи агенту» — поруч кнопка «Скопіювати для Claude» зі знімком збою: дія · відповідь сервера · номери · час · версія сторінки). "
         "④ стан, якого не досягти на здоровій системі (збій, «не стартував», порожньо), — Konst отримує спосіб побачити його сам: демо-режим за входом або прев'ю, посилання у звіті; «іди тестуй» без такого способу — не звіт. "
         "⑤ машинне (обрізання, прилипання, контраст, тап, ряд, iOS-зум, скрол, кромка, паритет тем — перелік — у шапці скрипта) — tools/claude-code/ui_lint.mjs, ✗ 0 у темах продукту — типово обидві, --themes light|dark для продукту з однією схемою. "
         "⑥ рух (transition · animation · пружина · requestAnimationFrame) — кліп MP4 у чат (SendUserFile) + смуга кадрів очима агента: python3 tools/claude-code/clip.py <сценарій.json> <тека> (Konst AE S140); кадр — УВЕСЬ екран, не кроп предмета: рух зсуває центр і праву частину — дивись, чи вони йдуть разом (Konst AE S146; кроп без crop_why clip.py не пустить); done вимагає --clip <файл.mp4> або --no-clip \"<чому, ≥ 30 знаків>\".")

def git(top, *a, raw=False):
    r = subprocess.run(["git", "-C", top, *a], capture_output=True)
    return r.stdout if raw else r.stdout.decode("utf-8", "replace").strip()

# AE S133 (UI-VOICE, Konst: «щоб тексти були людяні — машина мусить бачити кожну зміну тексту людині»): ⚠-текст правил AE S132 пройшов повз,
# бо гачок знав лише .html / .css. Тепер ще JS (.js / .mjs) поза tools/ · docs/ · test/ · tests/ · .claude/ · .github/, де ДОДАНИЙ рядок несе рядок у лапках
# з двома й більше словами кирилицею (текст людині: повідомлення, підказка, порада). Коментарі зрізано; код без людського тексту — тиша.
HUMAN = re.compile("['\"`][^'\"`\\n]*[А-ЯІЇЄҐа-яіїєґʼ’']{2,}[\\s,.:;—–-]+[А-ЯІЇЄҐа-яіїєґʼ’']{2,}[^'\"`\\n]*['\"`]")
SKIP_JS = re.compile(r"^(tools|docs|tests?|\.claude|\.github)/")   # від кореня репо: `site/tools/ae_rules.js` — текст людині, не прилад (аудит AE S143 А1; раніше (^|/) пропускав його)
def human_js(top):
    out = []
    for f in sorted(set(git(top, "diff", "HEAD", "--name-only", "--", "*.js", "*.mjs").splitlines()) | set(git(top, "ls-files", "--others", "--exclude-standard", "--", "*.js", "*.mjs").splitlines())):
        if not f or SKIP_JS.search(f): continue
        p = os.path.join(top, f)
        if not os.path.isfile(p): continue
        tracked = bool(git(top, "ls-files", "--", f))
        lines = [l[1:] for l in git(top, "diff", "-U0", "HEAD", "--", f).splitlines() if l.startswith("+") and not l.startswith("+++")] if tracked else open(p, encoding="utf-8", errors="replace").read().splitlines()
        if any(HUMAN.search(re.sub(r"/\*.*?(\*/|$)|//.*$", "", l)) for l in lines): out.append(f)
    return out

HTML_TXT = re.compile("[>][^<>\\n]*[А-ЯІЇЄҐа-яіїєґʼ’']{2,}[\\s,.:;—–-]+[А-ЯІЇЄҐа-яіїєґʼ’']{2,}[^<>\\n]*[<]")
def human_added(top, files):   # ДОДАНИЙ текст людині в диффі UI (рядок у лапках або текст між тегами) — для заборони --no-lint (пропуск Konst EquipLens S40)
    out = []
    for f in files:
        p = os.path.join(top, f)
        if not os.path.isfile(p): continue
        lines = [l[1:] for l in git(top, "diff", "-U0", "HEAD", "--", f).splitlines() if l.startswith("+") and not l.startswith("+++")] \
            if git(top, "ls-files", "--", f) else open(p, encoding="utf-8", errors="replace").read().splitlines()
        for l in lines:
            l = re.sub(r"/\*.*?(\*/|$)|<!--.*?(-->|$)|(^|\s)//.*$", "", l)
            m = HUMAN.search(l) or HTML_TXT.search(l)
            if m: out.append(f"{f}: {m.group(0)[:60]}")
    return out

def ui_state(top):   # (файли UI, хеш диффу) — дифф проти HEAD + нові неігноровані файли
    # видалення в теці примірки (shots/ — SHOTS.md: прийнята примірка прибирається) — не UI-правка: нічого переглядати (хибне QR 18.10, журнал гачків)
    drop = {l.split("\t", 1)[1] for l in git(top, "diff", "HEAD", "--name-status", "--", *UI).splitlines()
            if l.startswith("D\t") and re.search(r"(^|/)shots/", l.split("\t", 1)[1])}
    files = sorted((set(git(top, "diff", "HEAD", "--name-only", "--", *UI).splitlines()) - drop) |
                   set(git(top, "ls-files", "--others", "--exclude-standard", "--", *UI).splitlines()))
    files = [f for f in files if f] + human_js(top)
    if not files: return [], None
    h = hashlib.sha1(git(top, "diff", "HEAD", "--", *files, raw=True))   # лише ці файли: видалення примірки не міняє хеш
    for f in git(top, "ls-files", "--others", "--exclude-standard", "--", *files).splitlines():   # нові (не в git) файли зі списку — і UI, і JS з текстом людині (аудит S134: новий JS після позначки не міняв хеш)
        p = os.path.join(top, f)
        if os.path.isfile(p): h.update(f.encode()); h.update(open(p, "rb").read())
    return files, h.hexdigest()

MOTION = re.compile(r"\btransition\s*:|@keyframes|\banimation(-name)?\s*:|requestAnimationFrame|\.animate\(|--spring|\bspring\b|will-change\s*:\s*transform", re.I)
def live_fits(top, files):   # ⑦ порт ≡ примірка (AE S145, В-373 · В-371): дифф міняє продукт (не shots/), а примірку-накладку shots/**/fit_* міняли ≤ 14 днів тому
    # світ: design QA (код ≡ задуманому дизайну) ≠ регресія (код ≡ своєму минулому) — перед злиттям, свідома різниця — окремим кошиком (hypermatic.com «visual regression testing vs design QA», 14.11.2026)
    if not [f for f in files if '/shots/' not in '/' + f]: return []
    out = git(top, "log", "--since=14.days", "--name-only", "--format=", "--", ":(glob)**/shots/**/fit_*", ":(glob)shots/**/fit_*")
    return sorted({os.path.dirname(f) for f in out.split() if f})

def motion_in(top, files):   # рух у ДОДАНИХ рядках диффу (і в нових файлах) — Konst AE S140: рух показується кліпом, не знімком
    add = [l[1:] for l in git(top, "diff", "HEAD", "--unified=0", "--", *files).splitlines() if l.startswith("+") and not l.startswith("+++")]
    for f in git(top, "ls-files", "--others", "--exclude-standard", "--", *files).splitlines():
        pth = os.path.join(top, f)
        if os.path.isfile(pth):
            try: add += open(pth, encoding="utf-8", errors="ignore").read().splitlines()
            except OSError: pass
    return any(MOTION.search(l) for l in add)

GITC = r"^\s*(?:\w+=\S*\s+)*git\b(?:\s+-[cC]\s+\S+)*\s+commit\b"   # git … commit на початку команди (як commit-gate.sh)
GITP = r"^\s*(?:\w+=\S*\s+)*git\b(?:\s+-[cC]\s+\S+)*\s+push\b"
SANDBOX = re.compile(r"/sandbox(\.git)?/?$")   # origin прев'ю Konst (як review-remind.sh stand)
def mark(hx): return f"/tmp/lens-uireview-{hx}"
def issue_mark(blob): return f"/tmp/lens-issue-{blob}"
def blob_of(p):
    r = subprocess.run(["git", "hash-object", p], capture_output=True, text=True); return r.stdout.strip()

def pre_items():   # пункти «Перед видачею» — з самого маніфесту (копія тухне; той самий розбір, що review-remind.sh stand)
    man = os.path.join(os.path.dirname(os.environ.get("UI_GATE_SELF", "x/x")), "..", "..", "..", "kernel", "Lens_stagebench_manifest.md")
    try: sec = open(man, encoding="utf-8").read().split("## Перед видачею", 1)[1].split("\n## ", 1)[0]
    except Exception: return []
    return re.findall(r"(?m)^\| (\d) \| \*\*(.+?)\*\*", sec)

def push_files(top):   # [(статус, файл)] *.html у комітах, що поїдуть: upstream..HEAD; гілки на origin нема — усе дерево HEAD
    up = git(top, "rev-parse", "--verify", "-q", "@{u}") or git(top, "rev-parse", "--verify", "-q", "refs/remotes/origin/" + (git(top, "rev-parse", "--abbrev-ref", "HEAD") or "main"))
    rows = git(top, "diff", "--name-status", "--no-renames", up, "HEAD", "--", "*.html", "*.htm").splitlines() if up else \
        ["A\t" + f for f in git(top, "ls-tree", "-r", "--name-only", "HEAD", "--", "*.html", "*.htm").splitlines()]
    return [tuple(r.split("\t", 1)) for r in rows if "\t" in r]

def push_gate(cmd, cwd):
    segs, tops = re.split(r"&&|\|\||;|\n", cmd), []
    for seg in segs:
        m = re.match(r"\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)", seg)
        if m:
            p = os.path.expanduser(m.group(1).strip("\"'")); cwd = p if os.path.isabs(p) else os.path.join(cwd, p)
        if re.match(GITP, seg):
            c = re.search(r"\bgit\s+-C\s+(\S+)", seg); top = git(os.path.join(cwd, c.group(1)) if c else cwd, "rev-parse", "--show-toplevel")
            if top and SANDBOX.search(git(top, "remote", "get-url", "origin")): tops.append(top)
    if not tops: return None
    deny = lambda why: {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": why}}
    quiet = re.sub(r"\d*>>?\s*(&\d|/dev/null)", "", cmd)
    if any(re.match(GITC, s) for s in segs) or re.search(r"(^|[\s;&|(])(cp|mv|rsync|tee|install|sed\s+-i)\s", quiet) or ">" in quiet:
        return deny("Push у sandbox — окремою командою: у цій ще коміт, копіювання чи запис, а гачок бачить стан ДО команди (так v11 EquipLens S40 пройшов повз ворота). "
                    "Спершу файл і коміт, тоді `ui-review-gate.sh issue …` на виданий файл, тоді лише `git push`.")
    over, bad = [], []
    for top in dict.fromkeys(tops):
        for st, f in push_files(top):
            if st.startswith("D"): continue
            if st.startswith("M") and (f == "index.html" or re.search(r"_v\d+\.html?$", f)): over.append(f); continue
            if not os.path.exists(issue_mark(git(top, "rev-parse", f"HEAD:{f}"))): bad.append((top, f))
    if over:
        return deny(f"Sandbox: змінено наявне — {', '.join(over[:4])}. Нова версія = новий N, наявний vN не перезаписується, кореневий index.html sandbox не чіпається "
                    "(профіль «ПРЕВ'Ю»). Поверни файл (git checkout @{u} -- <файл> і коміт) і видай як _v<N+1>.html.")
    if not bad: return None
    items = " · ".join(f"{n}) {t}" for n, t in pre_items()) or "розділ «Перед видачею» в маніфесті не знайдено — скажи Konst"
    return deny("Видача без позначки ЦЬОГО вмісту: " + ", ".join(f for _, f in bad[:4]) + (" …" if len(bad) > 4 else "") + ". Прев'ю публічне з першої секунди — огляд і пауза «Перед видачею» до push. "
                f"Кроки: node {os.path.join(os.path.dirname(os.path.dirname(os.environ.get('UI_GATE_SELF', 'x/x'))), 'ui_lint.mjs')} <файл> [--baseline <база відомих ✗>] → ✗ 0; "
                + " · ".join(f"bash {os.environ.get('UI_GATE_SELF', 'tools/claude-code/hooks/ui-review-gate.sh')} issue {os.path.join(t, f)} \"<огляд: стани, теми, що бачить людина після дії>\" \"<перед видачею: 1 ✓ доказ … 7 н/з, бо …>\"" for t, f in bad[:4])
                + f" — і push знову. Пункти: {items}. Той самий блок — у повідомленні Konst з посиланням.")

def gate(d):
    if d.get("tool_name") != "Bash": return None
    cmd = str((d.get("tool_input") or {}).get("command", ""))
    # тіла heredoc — текст, не команди (як у commit-gate.sh; аудит S134: «git commit» у heredoc давав хибну заборону)
    L, keep, i = cmd.split("\n"), [], 0
    while i < len(L):
        keep.append(L[i]); m = re.search(r"<<-?\s*[\x22]?(?:\x27)?(\w+)(?:\x27)?[\x22]?", L[i]); i += 1
        if m:
            while i < len(L) and L[i].strip() != m.group(1): i += 1
    cmd = "\n".join(keep)
    pg = push_gate(cmd, d.get("cwd") or os.getcwd())
    if pg: return pg
    if not any(re.match(GITC, s) for s in re.split(r"&&|\|\||;|\||\n", cmd)): return None
    cwd, dirs = d.get("cwd") or os.getcwd(), []
    for seg in re.split(r"&&|\|\||;|\n", cmd):   # тека коміту — як у commit-gate: останній cd перед ним, git -C, або cwd
        m = re.match(r"\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)", seg)
        if m:
            p = os.path.expanduser(m.group(1).strip("\"'")); cwd = p if os.path.isabs(p) else os.path.join(cwd, p)
        if re.match(GITC, seg):
            c = re.search(r"\bgit\s+-C\s+(\S+)", seg); dirs.append(os.path.join(cwd, c.group(1)) if c else cwd)
    bad = []
    for dd in dict.fromkeys(dirs):
        top = git(dd, "rev-parse", "--show-toplevel")
        if not top: continue
        files, hx = ui_state(top)
        # файл з позначкою видачі ЦЬОГО вмісту (issue) уже оглянуто — коміт його в sandbox не вимагає ще однієї позначки (EquipLens S40)
        if files and all(os.path.isfile(os.path.join(top, f)) and os.path.exists(issue_mark(blob_of(os.path.join(top, f)))) for f in files): continue
        if files and not os.path.exists(mark(hx)): bad.append((top, files, hx))
    if not bad: return None
    if re.search(r"ui-review-gate\.sh\s+done\b", cmd):   # AE S117 (Konst: «збалансувати старе правило, не нове»): огляд уже написано, але тією ж командою — гачок бачить стан ДО неї;
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",   # заборона та сама, без чек-листа — лише що зробити
            "permissionDecisionReason": "Позначка огляду й коміт — в одній команді: гачок бачить стан до неї. Виконай `ui-review-gate.sh done …` окремою командою, потім коміт."}}
    why = " | ".join(f"{os.path.basename(t)}: {', '.join(f[:4])}{' …' if len(f) > 4 else ''} (дифф {h[:8]})" for t, f, h in bad)
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": f"Огляд UI до коміту: змінено UI — {why}; позначки огляду цього диффу нема. "
            f"Спершу огляд окремим проходом — {CHECK}. Знахідки → правки → ще прохід. Потім позначка (тека репо — після рядка огляду): "
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

if mode == "issue":   # позначка видачі в sandbox — за вмістом файла (EquipLens S40)
    if len(args) < 3: print("issue <файл.html> \"<огляд ≥ 40>\" \"<перед видачею: 1 ✓ доказ … 7 н/з, бо …>\""); sys.exit(2)
    f, note, pre = args[0], args[1], args[2]
    if not os.path.isfile(f): print(f"✗ файла нема: {f}"); sys.exit(1)
    if len(note) < 40: print("✗ рядок огляду < 40 знаків — назви стани, теми й що бачить людина після дії"); sys.exit(1)
    items = pre_items()
    if not items: print("✗ розділ «Перед видачею» в маніфесті не знайдено — гачок відстав від маніфесту, скажи Konst"); sys.exit(1)
    marks = list(re.finditer(r"(?<![\d.,])([1-9])\s*[).:]?\s*(✓|н/з)", pre))
    weak = []
    for n, t in items:
        hit = [m for m in marks if m.group(1) == n]
        if not hit: weak.append(f"{n} (нема)"); continue
        m = hit[0]; nxt = [k.start() for k in marks if k.start() > m.start()]; body = pre[m.end():(nxt[0] if nxt else len(pre))]
        if m.group(2) == "н/з" and not re.match(r"\s*,?\s*бо\s+\S", body): weak.append(f"{n} (н/з без «бо …»)")
        elif m.group(2) == "✓" and len(re.sub(r"[\s·,;—–-]", "", body)) < 8: weak.append(f"{n} (✓ без доказу)")
    if weak: print("✗ «Перед видачею»: " + " · ".join(weak) + " — кожен пункт: «N ✓ доказ (число · вивід · знімок)» або «N н/з, бо …». Пункти: " + " · ".join(f"{n}) {t}" for n, t in items)); sys.exit(1)
    b = blob_of(f)
    if not os.path.exists(f"/tmp/lens-uilint-blob-{b}"):
        ul = os.path.join(os.path.dirname(os.path.dirname(os.environ.get("UI_GATE_SELF", "x/x"))), "ui_lint.mjs")
        print(f"✗ ui_lint цього вмісту ({b[:8]}) не пройдено: node {ul} {f} [--baseline <база відомих ✗>] → ✗ 0 (правка після прогону міняє вміст — прожени знову)"); sys.exit(1)
    open(issue_mark(b), "w").write(f"{note}\n[перед видачею] {pre}\n{os.path.abspath(f)}\n")
    print(f"✓ позначка видачі {b[:8]} · {os.path.basename(f)} — push у sandbox пропустить саме цей вміст"); sys.exit(0)

if mode == "done":
    opt = lambda k: args[args.index(k) + 1] if k in args and args.index(k) + 1 < len(args) else None
    nolint, clip, noclip = opt("--no-lint"), opt("--clip"), opt("--no-clip")
    KO = ("--no-lint", "--clip", "--no-clip", "--no-port")
    rest = [a for i, a in enumerate(args) if a not in KO and not (i > 0 and args[i - 1] in KO)]
    note = rest[0] if rest else ""
    top = git(rest[1] if len(rest) > 1 else os.getcwd(), "rev-parse", "--show-toplevel")
    if len(note) < 40: print("✗ рядок огляду < 40 знаків — назви стани, теми й що бачить людина після дії"); sys.exit(1)
    if not top: print("✗ не git-репо"); sys.exit(1)
    files, hx = ui_state(top)
    if not files: print("ⓘ змін UI нема — позначка не потрібна"); sys.exit(0)
    # машинна частина огляду (HOOK-2.5): ui_lint на ЦЬОМУ диффі дав ✗ 0 у темах продукту — типово обидві, --themes light|dark для продукту з однією схемою — або чесна причина, чому сторінку не запустити
    lint = os.path.exists(lint_mark(hx))
    # пропуск Konst EquipLens S40 (журнал гачків 20.11 (8)): огляд пройшов з --no-lint «лише перефарбовує фон», а дифф ніс панель з абзацом пояснення —
    # ui_lint №38 «пояснення — за «i»» спіймав би. Новий текст людині в диффі → --no-lint не приймається: ui_lint бере й файл (`node ui_lint.mjs <файл.html>`)
    said = [] if lint else human_added(top, files)
    if nolint and said:
        print(f"✗ --no-lint не приймається: у диффі новий текст людині ({len(said)}: " + " · ".join(said[:3]) + ("…" if len(said) > 3 else "") +
              ") — машина мусить бачити, де й як він стоїть на екрані (ui_lint №38: пояснення — за «i»). Прожени ui_lint на сторінці або файлі цього диффу"); sys.exit(1)
    if not lint and not (nolint and len(nolint) >= 30):
        ul = os.path.join(os.path.dirname(os.path.dirname(os.environ.get("UI_GATE_SELF", "x/x"))), "ui_lint.mjs")
        print(f"✗ ui_lint цього диффу ({hx[:8]}) не пройдено: node {ul} <url|файл> [--state \"<js>\"]… --repo {top} → ✗ 0 у темах продукту — типово обидві, --themes light|dark для продукту з однією схемою (старі ✗, що були до правки, — `--baseline <файл>`: перший прогін ДО правки записує базу, блокує лише нове); "
              f"сторінку не запустити — done \"<огляд>\" {top} --no-lint \"<чому, ≥ 30 знаків>\""); sys.exit(1)
    # ⑥ рух — кліп (Konst AE S140): дифф додає рух → кліп MP4 існує (> 10 КБ) або причина без кліпу
    cliprec = ""
    if motion_in(top, files):
        cp = clip and (clip if os.path.isabs(clip) else os.path.join(top, clip))
        # Ж2 FAB-2 (AE S153): кліп — свіжий, тобто знятий ПІСЛЯ останньої правки файлів диффу; інакше старий MP4 проходить на новий код
        fresh = [(os.path.getmtime(os.path.join(top, f)), f) for f in files if os.path.isfile(os.path.join(top, f))]
        newest = max(fresh) if fresh else (0, "")
        if cp and os.path.isfile(cp) and cp.endswith(".mp4") and os.path.getsize(cp) > 10000 and os.path.getmtime(cp) + 1 < newest[0]:
            print(f"✗ кліп {clip} старший за код диффу: {newest[1]} правлено після запису кліпу — зніми кліп заново (python3 tools/claude-code/clip.py <сценарій.json> <тека>), тоді done --clip"); sys.exit(1)
        if cp and os.path.isfile(cp) and cp.endswith(".mp4") and os.path.getsize(cp) > 10000: cliprec = f"\n[кліп: {clip}]"
        elif noclip and len(noclip) >= 30: cliprec = f"\n[без кліпу: {noclip}]"
        else:
            print(f"✗ у диффі є рух (transition · animation · пружина), кліпу нема: python3 tools/claude-code/clip.py <сценарій.json> <тека> → MP4 у чат (SendUserFile), "
                  f"тоді done \"<огляд>\" {top} --clip <файл.mp4>; кліп не має сенсу — --no-clip \"<чому, ≥ 30 знаків>\""); sys.exit(1)
    # ⑦ порт ≡ примірка (AE S145, Konst: «щоб наступний агент знайшов port_same сам»): жива примірка + дифф продукту → позначка port_same ✓ цього диффу або причина
    portrec, nop = "", opt("--no-port")
    fits = live_fits(top, files)
    if fits:
        pm = f"/tmp/lens-portsame-{hx}"
        if os.path.exists(pm): portrec = "\n[port_same ✓: " + open(pm).read().strip()[:160] + "]"
        elif nop and len(nop) >= 30: portrec = f"\n[без port_same: {nop}]"
        else:
            print(f"✗ жива примірка ({', '.join(fits[:3])}) і дифф продукту: порт ≡ примірка — машиною: python3 tools/claude-code/port_same.py <сценарій port_*.json біля примірки> (ядро; SHOTS.md §1 п. 4) → ✓ 0 ✗ лишає позначку цього диффу; "
                  f"дифф не переносить примірку — done \"<огляд>\" {top} --no-port \"<чому, ≥ 30 знаків>\""); sys.exit(1)
    open(mark(hx), "w").write(note + ("" if lint else f"\n[без ui_lint: {nolint}]") + cliprec + portrec + "\n" + "\n".join(files) + "\n")
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
        r = gate(ev("bash x/ui-review-gate.sh done \"огляд\" . && git commit -am x"))
        say(r is not None and len(r["hookSpecificOutput"]["permissionDecisionReason"]) < 200, "позначка й коміт однією командою → deny коротко (без чек-листа)")
        subprocess.run(["git", "-C", tmp, "stash", "-q"], check=True); os.makedirs(f"{tmp}/shots/P1", exist_ok=True)
        open(f"{tmp}/shots/P1/fit.css", "w").write("p{}"); subprocess.run(["git", "-C", tmp, "add", "-A"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "fit"], check=True)
        os.remove(f"{tmp}/shots/P1/fit.css")
        say(gate(ev("git add -A && git commit -m x")) is None, "лише видалення файлів примірки (shots/) → тиша")
        open(f"{tmp}/a.html", "w").write("<p>9</p>")
        say(gate(ev("git add -A && git commit -m x")) is not None, "зуби: видалення в shots/ + правка .html → deny")
        subprocess.run(["git", "-C", tmp, "checkout", "-q", "--", "."], check=True); subprocess.run(["git", "-C", tmp, "stash", "pop", "-q"], check=True)
        files, hx = ui_state(tmp); open(mark(hx), "w").write("огляд: світла й темна, стан після дії, перезавантаження\n")
        say(gate(ev(f"cd {tmp} && git commit -am x")) is None, "позначка цього диффу → тиша")
        open(f"{tmp}/a.html", "w").write("<p>3</p>")
        say(gate(ev("git commit -am x")) is not None, "зуби: правка UI після позначки → знову deny")
        open(f"{tmp}/b.css", "w").write("p{}")
        say(gate(ev("git add -A && git commit -m x")) is not None, "новий .css (ще не в git) теж рахується → deny")
        r = subprocess.run(["bash", os.environ["UI_GATE_SELF"], "gate"], input=json.dumps(ev("git add -A && git commit -m x")), capture_output=True, text=True)
        say('"deny"' in r.stdout, "зуби: справжній виклик гачка (JSON через stdin, як від Claude Code) → deny")
        os.makedirs(f"{tmp}/docs/shots/P9", exist_ok=True); open(f"{tmp}/docs/shots/P9/fit_x_v1.js", "w").write("1")
        say(any("fit_x_v1.js" in f for f in ui_state(tmp)[0]), "зуби (AE S127): нова накладка примірки docs/shots/**/fit_* — теж UI, огляд до коміту")
        os.remove(f"{tmp}/docs/shots/P9/fit_x_v1.js")
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
        # пропуск Konst EquipLens S40: новий текст людині + --no-lint → ✗ (рядок у лапках і текст між тегами); коментар — тиша
        open(f"{tmp}/a.html", "w").write("<p>Пояснення, звідки цей варіант</p>")
        r = dn(note, tmp, "--no-lint", "лише перефарбовує фон — сторінку не запустити"); say(r.returncode == 1 and "текст людині" in r.stdout and not os.path.exists(mark(ui_state(tmp)[1])), "зуби (EquipLens S40): текст між тегами + --no-lint → ✗")
        open(f"{tmp}/a.html", "w").write("<script>const s = 'Фон для примірки обох тем';</script>")
        r = dn(note, tmp, "--no-lint", "лише перефарбовує фон — сторінку не запустити"); say(r.returncode == 1 and "текст людині" in r.stdout, "зуби (EquipLens S40): рядок у лапках + --no-lint → ✗")
        open(f"{tmp}/a.html", "w").write("<p>5</p><!-- коментар для розробника тут -->")
        r = dn(note, tmp, "--no-lint", "лише перефарбовує фон — сторінку не запустити"); say(r.returncode == 0, "кирилиця лише в коментарі HTML + --no-lint з причиною → ✓")
        os.remove(mark(ui_state(tmp)[1])); open(f"{tmp}/a.html", "w").write("<p>3</p>")
        # ⑥ рух → кліп (Konst AE S140)
        open(f"{tmp}/m.css", "w").write(".r{transition:transform .3s}"); files, hx = ui_state(tmp); open(lint_mark(hx), "w").write("✗0")
        if os.path.exists(mark(hx)): os.remove(mark(hx))   # позначка минулого прогону з тим самим хешем
        r = dn(note, tmp); say(r.returncode == 1 and "кліп" in r.stdout and not os.path.exists(mark(hx)), "зуби: дифф з рухом без кліпу → ✗")
        open(f"{tmp}/c.mp4", "wb").write(b"0" * 20000)
        t_old = os.path.getmtime(f"{tmp}/m.css") - 60; os.utime(f"{tmp}/c.mp4", (t_old, t_old))
        r = dn(note, tmp, "--clip", f"{tmp}/c.mp4"); say(r.returncode == 1 and "старший за код" in r.stdout and not os.path.exists(mark(hx)), "зуби (Ж2): кліп, знятий ДО правки диффу → ✗ «старший за код»")
        os.utime(f"{tmp}/c.mp4", None)
        r = dn(note, tmp, "--clip", f"{tmp}/c.mp4"); say(r.returncode == 0 and "[кліп:" in open(mark(hx)).read(), "дифф з рухом + --clip <mp4> → ✓, кліп у позначці")
        os.remove(mark(hx)); r = dn(note, tmp, "--no-clip", "рух лише ховер кольору — кліп нічого не покаже"); say(r.returncode == 0, "--no-clip з причиною → ✓"); os.remove(mark(hx)); os.remove(lint_mark(hx))
        os.remove(f"{tmp}/m.css"); os.remove(f"{tmp}/c.mp4")
        # ⑦ порт ≡ примірка (AE S145): жива примірка (fit_* у коміті ≤ 14 днів) + дифф продукту → потрібна позначка port_same або --no-port
        os.makedirs(f"{tmp}/docs/shots/P8", exist_ok=True); open(f"{tmp}/docs/shots/P8/fit_y_v1.js", "w").write("1")
        subprocess.run(["git", "-C", tmp, "add", "docs/shots/P8"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "примірка"], check=True)
        files, hx = ui_state(tmp); open(lint_mark(hx), "w").write("✗0")
        for f in (mark(hx), f"/tmp/lens-portsame-{hx}"):
            if os.path.exists(f): os.remove(f)
        r = dn(note, tmp); say(r.returncode == 1 and "port_same" in r.stdout and not os.path.exists(mark(hx)), "зуби: жива примірка + дифф продукту без port_same → ✗")
        r = dn(note, tmp, "--no-port", "коротко"); say(r.returncode == 1, "зуби: --no-port без причини (< 30 знаків) → ✗")
        r = dn(note, tmp, "--no-port", "правка тексту кнопки — примірку рейки не переносить"); say(r.returncode == 0 and "без port_same" in open(mark(hx)).read(), "--no-port з причиною → ✓, причина в позначці")
        os.remove(mark(hx)); open(f"/tmp/lens-portsame-{hx}", "w").write("port_p2 ✓ 59")
        r = dn(note, tmp); say(r.returncode == 0 and "port_same ✓" in open(mark(hx)).read(), "позначка port_same цього диффу → ✓, у позначці огляду")
        os.remove(mark(hx)); os.remove(f"/tmp/lens-portsame-{hx}"); os.remove(lint_mark(hx))
        # сітка review-remind post: UI-коміт без позначки → озивається; з позначкою на ці файли → тиша (без дубля)
        rr = os.path.join(os.path.dirname(os.environ["UI_GATE_SELF"]), "review-remind.sh")
        post = lambda sid: subprocess.run(["bash", rr, "post"], input=json.dumps({"tool_name": "Bash", "session_id": sid, "cwd": tmp, "tool_input": {"command": "git commit -am x"}}), capture_output=True, text=True).stdout
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "1"], check=True)
        say(bool(post(f"st{os.getpid()}a")), "сітка: UI-коміт без позначки огляду → нагадування «обійшов огляд»")
        open(f"{tmp}/a.html", "w").write("<p>4</p>"); files, hx = ui_state(tmp)
        open(mark(hx), "w").write("огляд: світла й темна\n" + "\n".join(files) + "\n")
        subprocess.run(["git", "-C", tmp, "commit", "-qam", "2"], check=True)
        say(not post(f"st{os.getpid()}b"), "сітка: UI-коміт з позначкою → тиша (без дубля з воротами)")
        os.makedirs(f"{tmp}/shots/P2", exist_ok=True); open(f"{tmp}/shots/P2/fit.css", "w").write("p{}")
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "fit2"], check=True)
        subprocess.run(["git", "-C", tmp, "rm", "-q", "-r", "shots/P2"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "3"], check=True)
        say(not post(f"st{os.getpid()}c"), "сітка: коміт лише з видаленням примірки (shots/) → тиша (хибне AE S95)")
        os.remove(mark(hx))
        # AE S133 (UI-VOICE): JS з текстом людині — теж UI; код без тексту, прилад у tools/, коментар — тиша
        subprocess.run(["git", "-C", tmp, "checkout", "-q", "--", "."], check=True)
        os.makedirs(f"{tmp}/site", exist_ok=True); os.makedirs(f"{tmp}/tools", exist_ok=True)
        open(f"{tmp}/site/r.js", "w").write("const x = 1;\n"); open(f"{tmp}/tools/t.js", "w").write("const y = 1;\n")
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True); subprocess.run(["git", "-C", tmp, "commit", "-qm", "js"], check=True)
        open(f"{tmp}/site/r.js", "w").write("const x = 2;\n")
        say(gate(ev("git add -A && git commit -m x")) is None, "JS без тексту людині → тиша")
        open(f"{tmp}/site/r.js", "w").write("const x = 2; // 'текст для людини тут'\n")
        say(gate(ev("git add -A && git commit -m x")) is None, "кирилиця лише в коментарі JS → тиша")
        open(f"{tmp}/tools/t.js", "w").write("console.log('✓ усі перевірки пройшли');\n"); open(f"{tmp}/site/r.js", "w").write("const x = 1;\n")
        say(gate(ev("git add -A && git commit -m x")) is None, "текст у приладі tools/*.js → тиша")
        os.makedirs(f"{tmp}/site/tools", exist_ok=True); open(f"{tmp}/site/tools/rules.js", "w").write("const m = 'Додайте назву позиції';\n")
        say(gate(ev("git add -A && git commit -m x")) is not None, "зуби (AE S143 А1): текст людині в site/tools/*.js (не прилад кореня) → огляд")
        subprocess.run(["git", "-C", tmp, "rm", "-q", "--cached", "site/tools/rules.js"], capture_output=True); os.remove(f"{tmp}/site/tools/rules.js")
        open(f"{tmp}/site/r.js", "w").write("const say = 'Ця фраза звернена до вас';\n")
        say(gate(ev("git add -A && git commit -m x")) is not None, "зуби: JS поза tools/ з текстом людині (два слова кирилицею в лапках) → deny (AE S132: ⚠-текст правил пройшов повз)")
        subprocess.run(["git", "-C", tmp, "checkout", "-q", "--", "."], check=True)
        # аудит S134: новий (не доданий) JS з текстом людині ПІСЛЯ позначки → хеш міняється → deny
        open(f"{tmp}/a.html", "w").write("<p>3</p>"); _, hx = ui_state(tmp); open(mark(hx), "w").write("x\n")
        say(gate(ev("git add -A && git commit -m x")) is None, "позначка диффу .html → тиша")
        open(f"{tmp}/site/n.js", "w").write("const t = 'Нова фраза для вас';\n")
        say(gate(ev("git add -A && git commit -m x")) is not None, "зуби: новий JS з текстом людині після позначки → deny (аудит S134)")
        os.remove(f"{tmp}/site/n.js")
        say(gate(ev("python3 - <<'EOF'\nprint('git commit -m x')\nEOF")) is None, "«git commit» лише в тілі heredoc → не коміт, тиша (аудит S134)")
        say(gate(ev("cd " + tmp + " && git -C . commit -am x")) is None, "git -C … commit з позначкою → тиша")
        os.remove(mark(hx)); subprocess.run(["git", "-C", tmp, "checkout", "-q", "--", "."], check=True)
        # сторож push у sandbox (EquipLens S40): позначка видачі за вмістом файла
        sbx = tempfile.mkdtemp(); bare, sb = f"{sbx}/sandbox.git", f"{sbx}/sb"
        G = lambda *a: subprocess.run(["git", "-C", sb, *a], check=True, capture_output=True)
        subprocess.run(["git", "init", "-q", "--bare", bare], check=True); subprocess.run(["git", "init", "-q", sb], check=True)
        for c in (["config", "user.email", "t@t"], ["config", "user.name", "t"], ["remote", "add", "origin", bare]): G(*c)
        os.makedirs(f"{sb}/P"); open(f"{sb}/index.html", "w").write("<p>root</p>"); open(f"{sb}/P/s_v1.html", "w").write("<p>v1</p>")
        G("add", "-A"); G("commit", "-qm", "0"); G("push", "-q", "-u", "origin", "HEAD")
        pe = lambda cmd: {"tool_name": "Bash", "cwd": sb, "tool_input": {"command": cmd}}
        say(gate(pe("git push -q origin HEAD")) is None, "sandbox: нічого нового в push → тиша")
        open(f"{sb}/P/s_v2.html", "w").write("<p>v2</p>"); G("add", "-A"); G("commit", "-qm", "v2")
        r = gate(pe("git push -q origin HEAD 2>&1 | tail -1"))
        say(r is not None and "s_v2.html" in r["hookSpecificOutput"]["permissionDecisionReason"] and "issue" in r["hookSpecificOutput"]["permissionDecisionReason"], "зуби: новий *_vN.html у push без позначки видачі → deny з командою issue (2>&1 — не запис)")
        say(gate({"tool_name": "Bash", "cwd": tmp, "tool_input": {"command": f"git -C {tmp} push -q"}}) is None, "push в інше репо (origin не sandbox) → тиша")
        b2 = blob_of(f"{sb}/P/s_v2.html"); open(issue_mark(b2), "w").write("x\n")
        say(gate(pe(f"cd {sb} && git -c push.negotiate=true push -q origin HEAD")) is None, "позначка видачі цього вмісту → тиша (git -c … push)")
        open(f"{sb}/P/s_v3.html", "w").write("<p>v3</p>")
        say(gate(pe("git add -A && git commit -qm v3 && git push -q origin HEAD")) is not None, "зуби (v11): коміт і push однією командою → deny «окремою командою»")
        say(gate(pe(f"cp {sb}/P/s_v3.html {sb}/P/s_v4.html; git push -q origin HEAD")) is not None, "зуби: cp і push однією командою → deny")
        os.remove(f"{sb}/P/s_v3.html"); open(f"{sb}/P/s_v2.html", "w").write("<p>v2 правка після позначки</p>"); G("commit", "-qam", "v2b")
        r = gate(pe("git push -q origin HEAD"))
        say(r is not None and "без позначки" in r["hookSpecificOutput"]["permissionDecisionReason"], "зуби: правка після позначки видачі → deny (вміст інший — інший хеш)")
        G("reset", "-q", "--hard", "HEAD~1"); G("push", "-q", "origin", "HEAD"); os.remove(issue_mark(b2))
        open(f"{sb}/P/s_v1.html", "w").write("<p>v1 перезапис</p>"); G("commit", "-qam", "v1b"); open(issue_mark(blob_of(f"{sb}/P/s_v1.html")), "w").write("x\n")
        r = gate(pe("git push -q origin HEAD"))
        say(r is not None and "перезаписується" in r["hookSpecificOutput"]["permissionDecisionReason"], "зуби: перезапис наявного _v1.html (навіть з позначкою) → deny «новий N»")
        os.remove(issue_mark(blob_of(f"{sb}/P/s_v1.html"))); G("reset", "-q", "--hard", "HEAD~1")
        open(f"{sb}/index.html", "w").write("<p>root2</p>"); G("commit", "-qam", "root")
        say(gate(pe("git push -q origin HEAD")) is not None, "зуби: кореневий index.html sandbox змінено → deny")
        G("reset", "-q", "--hard", "HEAD~1"); G("rm", "-q", "P/s_v1.html"); G("commit", "-qm", "rm")
        say(gate(pe("git push -q origin HEAD")) is None, "лише видалення (знято витік) → тиша")
        G("reset", "-q", "--hard", "HEAD~1")
        open(f"{sb}/P/s_v5.html", "w").write("<p>v5</p>"); G("add", "-A"); G("commit", "-qm", "v5")
        r = subprocess.run(["bash", os.environ["UI_GATE_SELF"], "gate"], input=json.dumps(pe("git push -q origin HEAD")), capture_output=True, text=True)
        say('"deny"' in r.stdout, "зуби: справжній виклик гачка на push у sandbox (JSON через stdin) → deny")
        # issue: огляд · пункти «Перед видачею» з маніфесту · ui_lint цього вмісту
        iss = lambda *a: subprocess.run(["bash", os.environ["UI_GATE_SELF"], "issue", *a], capture_output=True, text=True)
        n_items = len(pre_items()); f5 = f"{sb}/P/s_v5.html"; b5 = blob_of(f5)
        full = " ".join(f"{k} ✓ доказ пункту {k}: вивід смоуку" for k in range(1, n_items)) + f" {n_items} н/з, бо дотик глянь на пристрої"
        say(n_items >= 5, f"пункти «Перед видачею» читаються з маніфесту ({n_items})")
        r = iss(f5, "коротко", full); say(r.returncode == 1 and not os.path.exists(issue_mark(b5)), "зуби: issue з оглядом < 40 знаків → ✗")
        r = iss(f5, note, full.replace(" 2 ✓", " 2 —")); say(r.returncode == 1 and "2 (нема)" in r.stdout, "зуби: issue без пункту 2 → ✗ «нема»")
        r = iss(f5, note, full.replace(f"{n_items} н/з, бо", f"{n_items} н/з")); say(r.returncode == 1 and "без «бо" in r.stdout, "зуби: «н/з» без причини → ✗")
        r = iss(f5, note, full.replace("3 ✓ доказ пункту 3: вивід смоуку", "3 ✓")); say(r.returncode == 1 and "3 (✓ без доказу)" in r.stdout, "зуби: «✓» без доказу → ✗")
        r = iss(f5, note, full); say(r.returncode == 1 and "ui_lint" in r.stdout and not os.path.exists(issue_mark(b5)), "зуби: issue без ui_lint цього вмісту → ✗")
        open(f"/tmp/lens-uilint-blob-{b5}", "w").write("✗0"); r = iss(f5, note, full)
        say(r.returncode == 0 and os.path.exists(issue_mark(b5)) and gate(pe("git push -q origin HEAD")) is None, "issue повний + ui_lint вмісту → ✓, push у sandbox → тиша")
        open(f"{sb}/P/s_v6.html", "w").write("<p>v6</p>"); open(issue_mark(blob_of(f"{sb}/P/s_v6.html")), "w").write("x\n")
        say(gate(pe("git add -A && git commit -qm v6")) is None, "коміт у sandbox файла з позначкою видачі → ворота огляду мовчать")
        os.remove(f"{sb}/P/s_v6.html"); open(f"{sb}/P/s_v7.html", "w").write("<p>v7</p>")
        say(gate(pe("git add -A && git commit -qm v7")) is not None, "зуби: коміт у sandbox нового .html без позначок → deny огляду")
        for p in (issue_mark(b5), f"/tmp/lens-uilint-blob-{b5}"):
            if os.path.exists(p): os.remove(p)
        shutil.rmtree(sbx, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"─── ui-review-gate selftest: {n - bad}/{n} ───"); sys.exit(1 if bad else 0)
PY
