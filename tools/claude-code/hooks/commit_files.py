#!/usr/bin/env python3
# живе доки: коміти в репо Konst робить агент Claude Code (гачок коміту commit-gate.sh, HOOK-2 п.«нові файли»; QR CC-12, 14.10.2026, «так» Konst).
"""Сторож файлів коміту — що коміт ВНЕСЕ, перевіряється до запуску команди.

Подія: QR CC-12 — `sed` записав у корінь файл з `|` в імені, `git add -A && git commit` поніс його в main.
Гейт коміту бачить стан ДО команди, тож файл, ще не доданий у git, він не бачив. Тут дивимось і на те,
що додасть `git add -A` / `.` / `--all` / `-u` тієї ж команди.

Що ловить (кожне — ✗, коміт зупинено; решта — тиша):
  1. ім'я, яке Windows не створить: <>:"|?* і керівні символи, пробіл/крапка в кінці, CON PRN AUX NUL COM1–9 LPT1–9
     (клон на Windows ламається; pre-commit-hooks `check-illegal-windows-names`)
  2. новий файл у КОРЕНІ репо, не названий явно в `git add <ім'я>` тієї ж команди (законні нові файли в корені —
     0 за видиму історію QR і ядра; явна назва = свідомий намір, тоді тиша)
  3. новий файл більший за 1 МБ, не названий явно (`check-added-large-files`; репо — не склад)
  4. приватний ключ у вмісті (`detect-private-key`) і файл-секрет за іменем: .env · .dev.vars (wrangler) · id_rsa · *.pem/*.key · credentials.json
     (плагін spac для Claude Code, aitmpl.com/blog/secure-git-workflow, 14.10.2026; секрети — ніколи в репо)
  5. мітки конфлікту злиття `<<<<<<< ` / `>>>>>>> ` на початку рядка (`check-merge-conflict`; у main пишуть кілька агентів)
  6. зламаний синтаксис `.json` / `.toml` (`check-json` · `check-toml`; `wrangler.toml` і `manifest.json` ламають деплой)
  7. два шляхи, що різняться лише регістром (`check-case-conflict`; Windows і Mac їх не розрізнять)
  8. зламаний синтаксис змінених скриптів — `.sh`: `bash -n` (+ `shellcheck -S error`, якщо встановлено); `.py`: компіляція
     (`check-ast`). Подія: Routes S1 22.10.2026 — вставка після `;;` зламала диспетчер гачків `lens-hooks.sh`, а з ним — усі гачки
     всіх сесій; спіймано живим прогоном, не гейтом. Лише змінені файли — як у pre-commit (дешево, ~0,1 с на файл).
     `bash -n` лише розбирає (не бачить семантики) — тому shellcheck, де є; його нема — тиша, не ✗.
  9. новий прилад (`tools/` · `.claude/` · `.github/workflows/`: .py .sh .js .mjs .cjs .ts; не `archive/`) без рядка в карті репо —
     ім'я без розширення має бути в `docs/REPO_LAYOUT.md` (або `REPO_LAYOUT.md` · ядро: `tools/claude-code/CLAUDE_CODE.md` · `kernel/Lens_REPO_LAYOUT.md`)
     чи в .md поруч із приладом (`tools/tester/TESTER.md`); у продукті ще й рядок «ядро: …» у повідомленні коміту — кандидат для інших продуктів
     (→ реєстр «Прилади продуктів» у `tools/claude-code/CLAUDE_CODE.md` ядра) чи ні й чому. Подія: AE S104 24.10.2026 — Konst: «втомився нагадувати:
     інструмент, який створюється, повинен одразу мати мітки по документах, щоб наступна сесія про нього знала, і інші продукти теж».
     Практика: перевірка в коміті за шляхом нового файлу (`git diff --cached --diff-filter=A`) → потрібний документ у тому ж коміті
     (ledgerline-docs «documentation types and rules», 24.10.2026); Danger у CI не беремо — комітить агент, ловити треба до коміту.
     «ядро: кандидат» — рядок у реєстрі ядра вже має бути, коли клон ядра поруч (../lens-governance · /tmp/lens-governance · LENS_KERNEL_DIR); нема клону — не судимо.
Не беремо з pre-commit-hooks: пробіли й кінці файлів (шум у диффах даних), no-commit-to-branch (ми свідомо комітимо в main),
submodules (їх нема).

  python3 commit_files.py selftest   — тимчасове репо: кожен випадок має дати свій ✗, чиста команда — тишу
  HOOK_INJECT=1 … selftest           — сторож вимкнено → selftest червоніє (зуби)
"""
import os, re, subprocess, sys, json

WIN_BAD = re.compile(r'[<>:"|?*\x00-\x1f]')
WIN_RESERVED = re.compile(r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$', re.I)
BIG = 1024 * 1024
KEY = re.compile(rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY')
SECRET_NAME = re.compile(r'(^|/)(\.env(\..*)?|\.dev\.vars|id_(rsa|ed25519|ecdsa)[^/]*|[^/]*\.(pem|p12|pfx|key)|credentials\.json)$', re.I)
CONFLICT = re.compile(rb'^(?:<{7} |>{7} )', re.M)
SHELLCHECK = next((x for x in (os.environ.get('SHELLCHECK_BIN', ''), '/usr/bin/shellcheck', '/usr/local/bin/shellcheck') if x and os.path.isfile(x)), None)


def git(top, *a):
    r = subprocess.run(['git', '-C', top, *a], capture_output=True)
    return r.stdout.decode('utf-8', 'surrogateescape')


def zlist(top, *a):
    return [x for x in git(top, a[0], '-z', *a[1:]).split('\0') if x]   # -z одразу за підкомандою: після `--` git прочитав би його як шлях


def add_args(cmd):
    """Що команда додає: (усе? , явно названі шляхи)."""
    every, named = False, set()
    for seg in re.split(r'&&|\|\||;|\n', cmd):
        m = re.search(r'\bgit\s+(?:-C\s+\S+\s+)?add\b(.*)', seg)
        if not m:
            continue
        for tok in re.findall(r'"[^"]*"|\'[^\']*\'|\S+', m.group(1)):
            t = tok.strip('"\'')
            if t in ('-A', '--all', '.', '-u', '--update', ':/'):
                every = True
            elif not t.startswith('-'):
                named.add(t.rstrip('/'))
    if re.search(r'\bgit\b[^\n;&|]*\bcommit\b[^\n;&|]*\s-[a-zA-Z]*a[a-zA-Z]*\b', cmd):   # git commit -a / -am (не --amend)
        every = True
    return every, named


TOOL_RE = re.compile(r'^(tools|\.claude|\.github/workflows)/.+\.(py|sh|js|mjs|cjs|ts)$')
MAPS = ('docs/REPO_LAYOUT.md', 'REPO_LAYOUT.md', 'tools/claude-code/CLAUDE_CODE.md', 'kernel/Lens_REPO_LAYOUT.md')


def check(top, cmd):
    if os.environ.get('HOOK_INJECT') == '1':
        return []
    every, named = add_args(cmd)
    added = set(zlist(top, 'diff', '--cached', '--name-only', '--diff-filter=A'))
    changed = set(zlist(top, 'diff', '--cached', '--name-only', '--diff-filter=ACMR'))
    if every:
        new_untracked = set(zlist(top, 'ls-files', '--others', '--exclude-standard'))
        added |= new_untracked
        changed |= new_untracked | set(zlist(top, 'diff', '--name-only', '--diff-filter=ACMR'))
    else:   # явно названі в `git add` тієї ж команди — теж ідуть у коміт
        for n in named:
            for f in zlist(top, 'ls-files', '--others', '--exclude-standard', '--', n):
                added.add(f); changed.add(f)
            for f in zlist(top, 'diff', '--name-only', '--diff-filter=ACMR', '--', n):
                changed.add(f)
    explicit = lambda f: f in named or any(f.startswith(n + '/') for n in named if n not in ('.', ''))
    bad = []
    for f in sorted(added):
        parts = f.split('/')
        if any(WIN_BAD.search(p) or p.endswith((' ', '.')) or WIN_RESERVED.match(p) for p in parts):
            bad.append(f'ім\'я, якого Windows не створить: «{f}» (клон на Windows зламається) — перейменуй або прибери')
        elif '/' not in f and not explicit(f):
            bad.append(f'новий файл у корені «{f}» не названо явно — випадковий? прибери; свідомий — назви його в `git add {f}` у тій самій команді, що й коміт')
        if SECRET_NAME.search(f):
            bad.append(f'файл-секрет за іменем «{f}» — секрети ніколи в репо (змінні середовища сесії); додай у .gitignore')
        p = os.path.join(top, f)
        if os.path.isfile(p) and os.path.getsize(p) > BIG and not explicit(f):
            bad.append(f'новий файл «{f}» — {os.path.getsize(p) // 1024} КБ > 1 МБ — справді в репо? свідомо — `git add {f}` окремо')
    lower = {}
    for f in zlist(top, 'ls-files') + sorted(added):
        lower.setdefault(f.lower(), set()).add(f)
    for f in sorted(added):
        if len(lower.get(f.lower(), ())) > 1:
            bad.append(f'шляхи різняться лише регістром: {" · ".join(sorted(lower[f.lower()]))} (Windows і Mac їх не розрізнять)')
    for f in sorted(changed):
        p = os.path.join(top, f)
        if not os.path.isfile(p) or os.path.getsize(p) > 2 * BIG:
            continue
        b = open(p, 'rb').read()
        if KEY.search(b):
            bad.append(f'приватний ключ у «{f}» — секрети ніколи в репо; ключ — під заміну')
        if CONFLICT.search(b):
            bad.append(f'мітки конфлікту злиття в «{f}» — злиття не дороблене')
        try:
            if f.endswith('.json'):
                json.loads(b.decode('utf-8-sig'))
            elif f.endswith('.toml'):
                import tomllib
                tomllib.loads(b.decode('utf-8'))
        except Exception as e:
            bad.append(f'зламаний синтаксис «{f}»: {str(e)[:80]}')
        if f.endswith('.sh') or b.startswith(b'#!/bin/bash') or b.startswith(b'#!/usr/bin/env bash'):
            r = subprocess.run(['bash', '-n', p], capture_output=True, text=True)
            if r.returncode:
                bad.append(f'зламаний синтаксис bash «{f}»: {r.stderr.strip().splitlines()[-1][:120]}')
            elif SHELLCHECK:
                r = subprocess.run([SHELLCHECK, '-S', 'error', '-f', 'gcc'] + ([] if b.startswith(b'#!') else ['-s', 'bash']) + [p], capture_output=True, text=True)   # без шебанга — як bash (інакше SC2148 на кожному сорс-файлі)
                if r.returncode and r.stdout.strip():
                    bad.append(f'shellcheck (error) «{f}»: {r.stdout.strip().splitlines()[0][:140]}')
        elif f.endswith('.py'):
            try:
                compile(b, f, 'exec')
            except SyntaxError as e:
                bad.append(f'зламаний синтаксис Python «{f}»: рядок {e.lineno}: {e.msg}')
    # 9. новий прилад без мітки в карті репо (і без рішення «ядро:» у продукті) — AE S104
    tools = [f for f in sorted(added) if TOOL_RE.match(f) and not re.search(r'(^|/)(archive|__pycache__|fixtures?|testdata)/', f)]
    if tools:
        maps = [m for m in MAPS if os.path.isfile(os.path.join(top, m))]
        read = lambda q: open(q, encoding='utf-8', errors='replace').read()
        text = ''.join(read(os.path.join(top, m)) for m in maps)
        for f in tools:
            stem = os.path.splitext(os.path.basename(f))[0]
            near = ''.join(read(os.path.join(top, os.path.dirname(f), x)) for x in os.listdir(os.path.join(top, os.path.dirname(f))) if x.endswith('.md'))
            if stem not in text and stem not in near:
                bad.append(f'новий прилад «{f}» без рядка в карті репо ({" / ".join(maps) or "карти нема — docs/REPO_LAYOUT.md за шаблоном ядра"}) — '
                           f'що міряє · коли брати · запуск; інакше наступна сесія про нього не дізнається')
        # «ядро: кандидат» — рядок у реєстрі ядра має вже бути (аудит S104: інакше правило «тим самим ходом» ніхто не тримає); клону ядра поруч нема — не судимо
        kd = os.environ.get('LENS_KERNEL_DIR') or next((k for k in (os.path.join(os.path.dirname(top), 'lens-governance'), '/tmp/lens-governance') if os.path.isfile(os.path.join(k, 'tools/claude-code/CLAUDE_CODE.md'))), None)
        if re.search(r'ядро:\s*кандидат', cmd) and kd and os.path.isfile(os.path.join(kd, 'tools/claude-code/CLAUDE_CODE.md')):
            reg = read(os.path.join(kd, 'tools/claude-code/CLAUDE_CODE.md'))
            miss = [os.path.basename(f) for f in tools if os.path.splitext(os.path.basename(f))[0] not in reg]
            if miss: bad.append(f'«ядро: кандидат», а в реєстрі «Прилади продуктів» ядра ({kd}/tools/claude-code/CLAUDE_CODE.md) рядка нема: {", ".join(miss)} — спершу рядок і коміт ядра')
        if not os.path.isfile(os.path.join(top, 'kernel/Lens_validate.py')) and not re.search(r'ядро:\s*\S', cmd):
            bad.append(f'новий прилад ({", ".join(os.path.basename(f) for f in tools)}) — у повідомленні коміту бракує рядка «ядро: …»: кандидат для інших продуктів '
                       f'(→ реєстр «Прилади продуктів» у lens-governance:tools/claude-code/CLAUDE_CODE.md, тим самим ходом) чи ні — й чому')
    return bad


def selftest():
    import tempfile, shutil
    d = tempfile.mkdtemp(); ok = 0; n = 0
    def say(c, m):
        nonlocal ok, n; n += 1; ok += bool(c); print(('✓ ' if c else '✗ ') + m)
    try:
        g = lambda *a: subprocess.run(['git', '-C', d, *a], capture_output=True, check=True)
        g('init', '-q'); os.makedirs(d + '/lens'); open(d + '/README.md', 'w').write('x\n'); open(d + '/lens/a.md', 'w').write('x\n')
        open(d + '/wrangler.toml', 'w').write('name = "x"\n'); open(d + '/Docs.md', 'w').write('x\n')
        g('add', '.'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'init')
        say(check(d, 'git add -A && git commit -m x') == [], 'чисте дерево — тиша')
        open(d + '/lens/b.md', 'w').write('новий у теці\n')
        say(check(d, 'git add -A && git commit -m x') == [], 'новий файл у теці — тиша (законний дім)')
        os.remove(d + '/lens/b.md')
        open(d + '/eb&r=load|back', 'w').write('x')
        r = check(d, 'git add -A && git commit -m x'); say(any('Windows' in x for x in r), 'файл з | у корені через add -A → ✗ Windows (подія CC-12)')
        os.remove(d + '/eb&r=load|back')
        open(d + '/notes.txt', 'w').write('x')
        say(any('корені' in x for x in check(d, 'git add -A && git commit -m x')), 'новий файл у корені через add -A → ✗')
        say(check(d, 'git add notes.txt && git commit -m x') == [], 'той самий файл, названий явно → тиша')
        os.remove(d + '/notes.txt')
        open(d + '/lens/big.bin', 'wb').write(b'0' * (BIG + 10))
        say(any('1 МБ' in x for x in check(d, 'git add -A && git commit -m x')), 'новий файл > 1 МБ через add -A → ✗')
        say(check(d, 'git add lens/big.bin && git commit -m x') == [], 'великий, названий явно → тиша')
        os.remove(d + '/lens/big.bin')
        open(d + '/lens/k.md', 'w').write('-----BEGIN ' + 'OPENSSH PRIVATE KEY-----\nabc\n')   # шматками: цілий взірець у файлі сторож ловить у самому собі
        say(any('ключ' in x for x in check(d, 'git add -A && git commit -m x')), 'приватний ключ у вмісті → ✗')
        os.remove(d + '/lens/k.md')
        open(d + '/.dev.vars', 'w').write('X=1\n')
        say(any('секрет за іменем' in x for x in check(d, 'git add -A && git commit -m x')), '.dev.vars (секрети wrangler) через add -A → ✗')
        os.remove(d + '/.dev.vars')
        open(d + '/lens/a.md', 'w').write('<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> main\n')
        say(any('конфлікту' in x for x in check(d, 'git commit -am x')), 'мітки конфлікту у зміненому файлі (commit -a) → ✗')
        open(d + '/lens/a.md', 'w').write('x\n')
        open(d + '/wrangler.toml', 'w').write('name = "x\n')
        say(any('синтаксис' in x for x in check(d, 'git add -A && git commit -m x')), 'зламаний wrangler.toml → ✗')
        open(d + '/wrangler.toml', 'w').write('name = "x"\n')
        open(d + '/lens/A.md', 'w').write('x\n')
        say(any('регістром' in x for x in check(d, 'git add -A && git commit -m x')), 'lens/A.md поруч з lens/a.md → ✗ регістр')
        os.remove(d + '/lens/A.md')
        open(d + '/lens/h.sh', 'w').write('case "$1" in\n  a) echo a ;;\n  [ -z x ] && echo b\nesac\n')
        say(any('синтаксис bash' in x for x in check(d, 'git add -A && git commit -m x')), 'зламаний .sh (рядок після ;; — подія Routes S1) → ✗')
        open(d + '/lens/h.sh', 'w').write('case "$1" in\n  a) echo a ;;\nesac\n')
        say(check(d, 'git add -A && git commit -m x') == [], 'справний .sh → тиша')
        os.remove(d + '/lens/h.sh')
        open(d + '/lens/t.py', 'w').write('def f(:\n  pass\n')
        say(any('синтаксис Python' in x for x in check(d, 'git add -A && git commit -m x')), 'зламаний .py → ✗')
        os.remove(d + '/lens/t.py')
        # 9 · новий прилад без мітки (AE S104)
        os.makedirs(d + '/tools/stand'); open(d + '/tools/stand/walk_v1.py', 'w').write('x = 1\n')
        r = check(d, 'git add -A && git commit -m x'); say(any('без рядка в карті' in x for x in r) and any('ядро:' in x for x in r), 'новий прилад без карти й без «ядро:» → ✗ обидва')
        os.makedirs(d + '/docs'); open(d + '/docs/REPO_LAYOUT.md', 'w').write('прохід walk_v1 — що міряє\n')
        r = check(d, 'git add -A && git commit -m x'); say(not any('карті' in x for x in r) and any('ядро:' in x for x in r), 'у карті є, «ядро:» нема (продукт) → ✗ лише «ядро:»')
        say(check(d, "git add -A && git commit -m 'прохід\n\nядро: ні — лише AE'") == [], 'у карті є й «ядро: ні — чому» → тиша')
        kd = tempfile.mkdtemp(); os.makedirs(kd + '/tools/claude-code'); open(kd + '/tools/claude-code/CLAUDE_CODE.md', 'w').write('реєстр\n'); os.environ['LENS_KERNEL_DIR'] = kd
        say(any('реєстрі' in x for x in check(d, "git add -A && git commit -m 'ядро: кандидат'")), '«ядро: кандидат» без рядка в реєстрі ядра → ✗ (аудит S104)')
        open(kd + '/tools/claude-code/CLAUDE_CODE.md', 'w').write('| walk_v1 | AE |\n')
        say(check(d, "git add -A && git commit -m 'ядро: кандидат'") == [], '«ядро: кандидат» і рядок у реєстрі є → тиша')
        del os.environ['LENS_KERNEL_DIR']; shutil.rmtree(kd)
        os.makedirs(d + '/tools/tester'); open(d + '/tools/tester/run.py', 'w').write('x = 1\n'); open(d + '/tools/tester/TESTER.md', 'w').write('run — запуск\n')
        say(check(d, "git add -A && git commit -m 'ядро: ні — лише тут'") == [], 'прилад описано в .md поруч (tools/tester/TESTER.md) → тиша')   # «ні»: «кандидат» залежав би від клону ядра в /tmp
        os.makedirs(d + '/tools/archive'); open(d + '/tools/archive/old_v0.py', 'w').write('x = 1\n')
        say(check(d, "git add -A && git commit -m 'ядро: ні'") == [], 'прилад в archive/ → тиша')
        os.makedirs(d + '/kernel'); open(d + '/kernel/Lens_validate.py', 'w').write('x = 1\n')
        say(not any('ядро:' in x for x in check(d, 'git add docs tools kernel/Lens_validate.py && git commit -m x')), 'ядро (є kernel/Lens_validate.py) — «ядро:» не вимагається')
        shutil.rmtree(d + '/tools'); shutil.rmtree(d + '/docs'); shutil.rmtree(d + '/kernel')
        open(d + '/stray.txt', 'w').write('x')
        say(check(d, 'git add lens/a.md && git commit -m x') == [], 'нестежений файл, якого команда не додає → тиша (у коміт не піде)')
    finally:
        shutil.rmtree(d)
    print(f'─── commit_files selftest: {ok}/{n} ───')
    return ok == n


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        sys.exit(0 if selftest() else 1)
    print(__doc__)
