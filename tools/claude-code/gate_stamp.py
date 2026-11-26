#!/usr/bin/env python3
# живе доки: у продукті Lens `main` = деплой і push у `main` робить агент (EquipLens S47, 26.11.2026).
# Печатка гейта для push у `main`: `env_check` продукту в кінці пише печатку — дерево робочої теки (з неігнорованими новими
# файлами) і код виходу; git-гачок `pre-push` (ставить `install`, кличе `prepush`) пускає push у refs/heads/main лише коли
# дерево коміту ≡ дереву печатки і код 0. Ліки від пропуску «гейт ; коміт ; push» (EquipLens S46 e98ad4e, S47 5f1d02c):
# гачок Claude Code `commit-gate` ганяє лише `Lens_validate`, а ✗ були в інших приладах `env_check`.
# Чому git-гачок, а не розбір команди в PreToolUse: він бачить справжній ref і SHA (будь-який синтаксис push) і спрацьовує
# ПІСЛЯ попередніх ланок команди — `env_check && … && git push` проходить, `env_check ; … ; git push` — ні.
# Практика: перевірка, прив'язана до вмісту коміту (status checks GitHub — до SHA; тут — до дерева, бо коміт печатки ще нема);
# не беремо захист гілки на сервері — він вимагав би CI з повним env_check (Chromium, хвилини) і ручних налаштувань Konst.
# Обхід: `git push --no-verify`, конектор GitHub (MCP) — гачок їх не бачить (прийнятий ризик; правило — CLAUDE.md продукту «Гілка»).
# Запуск:  gate_stamp.py write <репо> <код>   (у кінці env_check; ENV_INJECT — не пише)
#          gate_stamp.py prepush <репо>        (stdin git pre-push: «<лок. ref> <лок. sha> <віддал. ref> <віддал. sha>»)
#          gate_stamp.py install <репо>        (.git/hooks/pre-push; кличе session-start продукту)
#          gate_stamp.py selftest              (тимчасове репо: зелена ✓ · змінене дерево ✗ · код 1 ✗ · нема печатки ✗ · інша гілка ✓)
import json, os, subprocess, sys, tempfile, shutil, time

ME = os.path.abspath(__file__)
Z = '0' * 40

def git(repo, *a, env=None):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, env=env)

def stamp_path(repo):
    return os.path.join(repo, git(repo, 'rev-parse', '--git-dir').stdout.strip(), 'lens-gate-stamp.json')

def work_tree(repo):
    """Дерево робочої теки: копія індексу + add -A (неігноровані нові файли теж) → write-tree; справжній індекс не чіпаємо."""
    gd = os.path.join(repo, git(repo, 'rev-parse', '--git-dir').stdout.strip())
    fd, tmp = tempfile.mkstemp(); os.close(fd)
    try:
        if os.path.exists(os.path.join(gd, 'index')): shutil.copy(os.path.join(gd, 'index'), tmp)
        else: os.remove(tmp)
        env = dict(os.environ, GIT_INDEX_FILE=tmp)
        git(repo, 'add', '-A', env=env)
        return git(repo, 'write-tree', env=env).stdout.strip()
    finally:
        if os.path.exists(tmp): os.remove(tmp)

def write(repo, code):
    s = {'tree': work_tree(repo), 'code': int(code), 'head': git(repo, 'rev-parse', 'HEAD').stdout.strip(), 'time': int(time.time())}
    with open(stamp_path(repo), 'w') as f: json.dump(s, f)
    return s

def prepush(repo, lines):
    try: s = json.load(open(stamp_path(repo)))
    except Exception: s = None
    for ln in lines:
        p = ln.split()
        if len(p) < 4 or p[2] != 'refs/heads/main' or p[1] == Z: continue
        tree = git(repo, 'rev-parse', p[1] + '^{tree}').stdout.strip()
        if not s:
            return 1, '✗ push у main зупинено: печатки env_check нема — прожени `bash tools/env_check.sh` і push тим самим ланцюжком через «&&»'
        if s['code'] != 0:
            return 1, f"✗ push у main зупинено: останній env_check — exit {s['code']} (червоний): виправ ✗, тоді env_check && push"
        if s['tree'] != tree:
            return 1, f"✗ push у main зупинено: коміт {p[1][:7]} — не те дерево, що судив env_check (печатка {s['tree'][:7]}, коміт {tree[:7]}): правка після гейта — прожени env_check знову"
    return 0, ''

HOOK = '#!/bin/sh\n# поставив lens-governance:tools/claude-code/gate_stamp.py install — push у main лише з зеленою печаткою env_check\nexec python3 "{me}" prepush "$(git rev-parse --show-toplevel)"\n'

def install(repo):
    hp = os.path.join(repo, git(repo, 'rev-parse', '--git-path', 'hooks').stdout.strip())
    os.makedirs(hp, exist_ok=True); f = os.path.join(hp, 'pre-push')
    if os.path.exists(f) and 'gate_stamp.py' not in open(f).read():
        return f'⚠ {f} уже є і не наш — не перезаписую'
    open(f, 'w').write(HOOK.format(me=ME)); os.chmod(f, 0o755)
    return f'✓ pre-push: {f}'

def selftest():
    ok = n = 0
    d = tempfile.mkdtemp(); r = os.path.join(d, 'r')
    try:
        os.makedirs(r); git(r, 'init', '-q', '-b', 'main')
        for k, v in (('user.email', 't@t'), ('user.name', 't')): git(r, 'config', k, v)
        open(os.path.join(r, 'a.txt'), 'w').write('1'); git(r, 'add', '-A'); git(r, 'commit', '-qm', 'a')
        def case(name, cond):
            nonlocal ok, n; n += 1; ok += bool(cond); print(('✓ ' if cond else '✗ ') + name)
        def push(ref='refs/heads/main'):
            h = git(r, 'rev-parse', 'HEAD').stdout.strip(); return prepush(r, [f'HEAD {h} {ref} {Z}'])[0]
        case('нема печатки → push у main ✗', push() == 1)
        open(os.path.join(r, 'b.txt'), 'w').write('new'); write(r, 0)
        git(r, 'add', '-A'); git(r, 'commit', '-qm', 'b')
        case('печатка зелена до коміту, коміт того самого дерева (з новим файлом) → ✓', push() == 0)
        open(os.path.join(r, 'a.txt'), 'w').write('2'); git(r, 'commit', '-qam', 'c')
        case('правка після печатки → ✗ (зуб: дерево)', push() == 1)
        write(r, 1)
        case('печатка червона (exit 1) → ✗ (зуб: код)', push() == 1)
        case('push в іншу гілку → не стереже', push('refs/heads/claude/x') == 0)
        h = git(r, 'rev-parse', 'HEAD').stdout.strip()
        case('видалення ref (нульовий SHA) → не стереже', prepush(r, [f'(delete) {Z} refs/heads/main {h}'])[0] == 0)
        case('install → .git/hooks/pre-push з викликом prepush', install(r).startswith('✓') and 'prepush' in open(os.path.join(r, '.git/hooks/pre-push')).read())
        write(r, 0); bare = os.path.join(d, 'o.git'); subprocess.run(['git', 'init', '-q', '--bare', bare]); git(r, 'remote', 'add', 'o', bare)
        case('справжній git push: зелена печатка того дерева → проходить', git(r, 'push', '-q', 'o', 'HEAD:main').returncode == 0)
        open(os.path.join(r, 'a.txt'), 'w').write('3'); git(r, 'commit', '-qam', 'd')
        case('справжній git push: коміт після печатки → git відмовляє (зуб наскрізний)', git(r, 'push', '-q', 'o', 'HEAD:main').returncode != 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'gate_stamp selftest: {ok}/{n}'); return 0 if ok == n else 1

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['write'] and len(a) == 3:
        s = write(a[1], a[2]); print(f"печатка env_check: дерево {s['tree'][:7]} · exit {s['code']}"); sys.exit(0)
    if a[:1] == ['prepush'] and len(a) == 2:
        c, msg = prepush(a[1], sys.stdin.read().splitlines())
        if msg: print(msg, file=sys.stderr)
        sys.exit(c)
    if a[:1] == ['install'] and len(a) == 2: print(install(a[1])); sys.exit(0)
    if a[:1] == ['selftest']: sys.exit(selftest())
    print('gate_stamp.py write <репо> <код> | prepush <репо> | install <репо> | selftest'); sys.exit(2)
