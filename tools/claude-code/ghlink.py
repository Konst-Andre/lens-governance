#!/usr/bin/env python3
# ghlink — коміт і `файл:рядок` → markdown-посилання на GitHub, прив'язане до SHA (permalink): за тиждень показує той самий стан.
# живе доки: звіти агента Konst читає в застосунку Claude (iOS) і перевіряє доказ дотиком (Konst 24.11.2026, ядро AUDIT: «під цифрами —
# активне посилання… одразу побачити дійсно ті речі»). Аналог — Routes:tools/handoff_check.py `--md` (коміт Routes 28e7051; не читано).
# Форма (24.11.2026): коміт — …/commit/<sha>; файл — …/blob/<sha>/<шлях>#L<n>, .md — з ?plain=1 (відрендерений Markdown якорів рядків
# не має: docs.github.com «Getting permanent links to files» / «Creating a permanent link to a code snippet»). Текст посилання — звичайний,
# без бектиків: плашка в посиланні на iPhone малюється так само, як звичайне посилання (проба Konst 24.11).
# Запуск:  python3 tools/claude-code/ghlink.py [--repo <тека>] <sha | шлях[:рядок[-рядок]]> …   → рядок markdown на кожен аргумент
#          python3 tools/claude-code/ghlink.py selftest
# Чесність: SHA, якого нема на origin (не запушено), посиланням не стає — «`sha` (не запушено)»; рядок за межею файла — ✗ і вихід 1.
import os, re, subprocess, sys, tempfile

def git(root, *a):
    r = subprocess.run(['git', '-C', root, *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None

def slug(root):
    u = git(root, 'remote', 'get-url', 'origin') or ''
    m = re.search(r'[/:]([^/:]+)/([^/]+?)(?:\.git)?/?$', u)
    return f'{m.group(1)}/{m.group(2)}' if m else None

def pushed(root, sha):
    """SHA досяжний з якоїсь гілки origin — тобто посилання не дасть 404."""
    full = git(root, 'rev-parse', '--verify', '--quiet', sha + '^{commit}')
    if not full: return None
    return full if git(root, 'branch', '-r', '--contains', full) else ''

def link(root, ref, sha=None):
    s = slug(root)
    if not s: return None, f'✗ {ref}: нема origin GitHub'
    base = f'https://github.com/{s}'
    if re.fullmatch(r'[0-9a-f]{7,40}', ref):
        full = pushed(root, ref)
        if full is None: return None, f'✗ {ref}: такого коміту нема'
        if not full: return f'`{ref[:7]}` (не запушено)', None
        return f'[{ref[:7]}]({base}/commit/{full})', None
    m = re.fullmatch(r'(.+?)(?::(\d+)(?:-(\d+))?)?', ref); path, a, b = m.group(1), m.group(2), m.group(3)
    head = sha or git(root, 'rev-parse', 'HEAD'); full = pushed(root, head)
    if not full: return f'`{ref}` (не запушено)', None
    body = git(root, 'show', f'{full}:{path}')
    if body is None: return None, f'✗ {ref}: файла нема в {full[:7]}'
    n = body.count('\n') + (0 if body.endswith('\n') or not body else 1)
    for x in (a, b):
        if x and not 1 <= int(x) <= max(n, 1): return None, f'✗ {ref}: рядок {x} за межею ({n} рядків)'
    q = '?plain=1' if path.endswith(('.md', '.markdown')) and a else ''
    anchor = f'#L{a}' + (f'-L{b}' if b else '') if a else ''
    return f'[{os.path.basename(path)}' + (f':{a}' + (f'-{b}' if b else '') if a else '') + f']({base}/blob/{full}/{path}{q}{anchor})', None

def selftest():
    ok = []; d = tempfile.mkdtemp()
    run = lambda *a: subprocess.run(a, cwd=d, capture_output=True, text=True)
    run('git', 'init', '-q', '-b', 'main'); run('git', 'config', 'user.email', 't@t'); run('git', 'config', 'user.name', 't')
    open(os.path.join(d, 'a.md'), 'w').write('1\n2\n3\n'); open(os.path.join(d, 'b.py'), 'w').write('x\n')
    run('git', 'add', '.'); run('git', 'commit', '-qm', 'one')
    bare = tempfile.mkdtemp(); subprocess.run(['git', 'init', '-q', '--bare', bare], capture_output=True)
    run('git', 'remote', 'add', 'origin', 'https://github.com/Owner/repo.git'); run('git', 'config', 'remote.origin.pushurl', bare)
    run('git', 'push', '-q', bare, 'main'); run('git', 'fetch', '-q', bare, '+main:refs/remotes/origin/main')
    h = git(d, 'rev-parse', 'HEAD')
    c = lambda name, cond: ok.append((name, bool(cond)))
    l, e = link(d, h[:7]); c('коміт → …/commit/<повний sha>', l == f'[{h[:7]}](https://github.com/Owner/repo/commit/{h})' and not e)
    l, e = link(d, 'a.md:2'); c('.md:рядок → blob/<sha>/…?plain=1#L2', l == f'[a.md:2](https://github.com/Owner/repo/blob/{h}/a.md?plain=1#L2)')
    l, e = link(d, 'b.py:1'); c('код:рядок → #L1 без ?plain', l.endswith(f'/blob/{h}/b.py#L1)'))
    l, e = link(d, 'a.md:2-3'); c('діапазон → #L2-L3', l.endswith('?plain=1#L2-L3)'))
    l, e = link(d, 'a.md:9'); c('зуб: рядок за межею → ✗', l is None and 'за межею' in e)
    l, e = link(d, 'nope.md:1'); c('зуб: файла нема → ✗', l is None and 'файла нема' in e)
    open(os.path.join(d, 'a.md'), 'a').write('4\n'); run('git', 'commit', '-qam', 'two'); h2 = git(d, 'rev-parse', 'HEAD')
    l, e = link(d, h2[:7]); c('зуб: незапушений коміт — не посилання, «(не запушено)»', l == f'`{h2[:7]}` (не запушено)')
    l, e = link(d, 'a.md:4'); c('зуб: HEAD не запушено — файл теж без посилання', l == '`a.md:4` (не запушено)')
    for name, v in ok: print(('✓ ' if v else '✗ ') + name)
    bad = sum(1 for _, v in ok if not v); print(f'─── ghlink selftest: {len(ok) - bad}/{len(ok)} ───'); return 1 if bad else 0

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']: sys.exit(selftest())
    root = '.'
    if a[:1] == ['--repo']: root, a = a[1], a[2:]
    if not a: print(__doc__ or 'ghlink.py [--repo <тека>] <sha | шлях[:рядок]> …'); sys.exit(2)
    rc = 0
    for r in a:
        l, e = link(root, r)
        print(l if l else e); rc |= 0 if l else 1
    sys.exit(rc)
