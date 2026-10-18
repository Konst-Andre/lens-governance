#!/usr/bin/env python3
# живе доки: продукти Lens мають версію застосунку (B · rev) — правило tools/claude-code/VERSIONS.md (Konst 18.10.2026, QR CC-17: «головне, щоб хтось це контролював»).
# Перевірка версії проти бази (origin/main): код застосунку змінився — версія мусить піднятись, і правильно
# (підхід — «Version Forget-Me-Not», Simply Business 2020: diff коду проти бази ⟂ мітка версії; тут — у env_check, не в CI).
#   python3 version_check.py <репо> --code <файл коду> --re '<регулярка з двома групами: B і rev>' [--name '<регулярка шляху файлу білда з групою B>'] [--base origin/main] [--inject]
#   python3 version_check.py selftest      → зуби: тимчасовий git-репо, 6 випадків
# Вивід — один рядок для env_check: «версія: B65 · rev 0 ✓ …» або «✗ версія: …» (exit 1). Що саме підняти (B чи rev) — рішення людини за VERSIONS.md;
# машина ловить «забув» (код змінився, версія та сама), «не так» (новий B — rev не з 0; версія впала) і розбіжність назви файлу білда з B.
import sys, re, os, subprocess, glob, tempfile

def git(repo, *a):
    r = subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def ver(text, rx):
    m = re.search(rx, text or '')
    return (int(m.group(1)), int(m.group(2))) if m else None

def check(repo, code, rx, name=None, base='origin/main', inject=False):
    path = os.path.join(repo, code)
    if not os.path.isfile(path): return 1, f'✗ версія: нема файлу коду {code}'
    now = open(path, encoding='utf-8').read()
    if inject: now += '\n<!-- version_check --inject: код змінився -->\n'
    v = ver(now, rx)
    if not v: return 1, f'✗ версія: у {code} не знайдено мітку версії (регулярка {rx})'
    tag = f'B{v[0]} · rev {v[1]}'
    if name:
        rel = [os.path.relpath(f, repo) for f in glob.glob(os.path.join(repo, '**', '*'), recursive=True)]
        nums = sorted({int(re.search(name, f).group(1)) for f in rel if re.search(name, f) and not f.startswith('archive/')})
        if nums != [v[0]]: return 1, f'✗ версія: {tag}, а файл білда — batch {", ".join(map(str, nums)) or "нема"} (новий B — новий файл білда, старий → archive/builds/; VERSIONS.md)'
    old = git(repo, 'show', f'{base}:{code}')
    if old is None: return 0, f'версія: {tag} ✓ (бази {base} для {code} нема — новий файл)'
    ov = ver(old, rx)
    if old == now: return 0, f'версія: {tag} ✓ (код ≡ {base})'
    if not ov: return 0, f'версія: {tag} ✓ (у базі мітки не було)'
    ot = f'B{ov[0]} · rev {ov[1]}'
    if v == ov: return 1, f'✗ версія: код змінився проти {base}, а версія та сама ({tag}) — підніми rev (виправлення, поліш) або B з rev 0 (нове, що помітить команда) — VERSIONS.md'
    if v < ov: return 1, f'✗ версія: впала {ot} → {tag}'
    if v[0] > ov[0] and v[1] != 0: return 1, f'✗ версія: новий B ({ot} → {tag}) — rev починається з 0'
    if v[0] == ov[0] and v[1] > ov[1] + 1: return 0, f'версія: {ot} → {tag} ✓ (⚠ rev стрибнув на {v[1] - ov[1]} — так задумано?)'
    return 0, f'версія: {ot} → {tag} ✓ (код змінився, версію піднято)'

def selftest():
    rx, name = r"APP_BUILD=\{batch:(\d+),rev:(\d+)", r'^build_batch(\d+)\.html$'
    d = tempfile.mkdtemp(prefix='vercheck-'); bad = 0
    def w(f, s): open(os.path.join(d, f), 'w').write(s)
    run = lambda *a: subprocess.run(['git', '-C', d, *a], capture_output=True)
    subprocess.run(['git', 'init', '-q', d]); run('config', 'user.email', 't@t'); run('config', 'user.name', 't')
    w('app.html', 'x APP_BUILD={batch:64,rev:21} a'); w('build_batch64.html', '.')
    run('add', '-A'); run('commit', '-qm', 'base')
    cases = [('код той самий', 'x APP_BUILD={batch:64,rev:21} a', None, 0), ('код змінився, версія та сама', 'x APP_BUILD={batch:64,rev:21} b', None, 1),
             ('rev +1', 'x APP_BUILD={batch:64,rev:22} b', None, 0), ('новий B, rev не 0', 'x APP_BUILD={batch:65,rev:3} b', 'build_batch65.html', 1),
             ('новий B, rev 0, файл білда старий', 'x APP_BUILD={batch:65,rev:0} b', None, 1), ('новий B, rev 0, новий файл білда', 'x APP_BUILD={batch:65,rev:0} b', 'build_batch65.html', 0)]
    for t, s, nf, want in cases:
        w('app.html', s)
        for f in glob.glob(os.path.join(d, 'build_batch*.html')): os.remove(f)
        w(nf or 'build_batch64.html', '.')
        code, msg = check(d, 'app.html', rx, name, base='HEAD')
        ok = code == want; bad += not ok
        print(('✓ ' if ok else '✗ ') + f'{t} → {"✗" if code else "✓"} ({msg})')
    print(f'─── version_check selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print('version_check.py <репо> --code F --re R [--name R] [--base REF] [--inject] | selftest'); sys.exit(2)
    if a[0] == 'selftest': sys.exit(selftest())
    opt = {'base': 'origin/main'}; i = 1
    while i < len(a):
        if a[i] == '--inject': opt['inject'] = True; i += 1
        else: opt[a[i].lstrip('-')] = a[i + 1]; i += 2
    code, msg = check(a[0], opt['code'], opt['re'], opt.get('name'), opt['base'], opt.get('inject', False))
    print(msg); sys.exit(code)
