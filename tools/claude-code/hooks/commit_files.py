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
Не беремо з pre-commit-hooks: пробіли й кінці файлів (шум у диффах даних), no-commit-to-branch (ми свідомо комітимо в main),
перевірки Python-коду (нема такого коду в продуктах), submodules (їх нема).

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
            bad.append(f'новий файл у корені «{f}» не названо явно — випадковий? прибери; свідомий — `git add {f}` окремо')
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
