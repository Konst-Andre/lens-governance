#!/usr/bin/env python3
# живе доки: гачки й прилади ядра мають режим selftest (tools/claude-code/hooks/, tools/claude-code/). Дім — lens-governance:tools/claude-code/hooks/.
"""Усі selftest гачків і приладів ядра — машиною, не пам'яттю (Konst AE S143: «тести є, але самі не запускаються»;
перший улов того ж дня — memory-guard і plan-web падали в тесті диспетчера, і ніхто не бачив).

Практика: самоперевірка на старті + тиша, доки все зелене, голос — лише на збій (startup self-test · canary «не будити щохвилини»:
martincapodici.com «Production tests», 13.05.2025; oneuptime.com «Independent canaries», 2026; перевірено 13.11.2026).

  python3 selftest_all.py all              — усі по черзі; друкує лише ✗ і підсумок; пише /tmp/lens-selftest-<сесія>.log
  python3 selftest_all.py bg               — те саме у фоні (SessionStart диспетчера; старт не чекає ~60 с)
  python3 selftest_all.py files <шлях>…    — лише тести цих файлів (commit-gate: змінив гачок → його тест до коміту)
  python3 selftest_all.py report           — рядки для handoff_check: ✗ з журналу останнього прогону або нічого
  python3 selftest_all.py selftest         — зуби самого запускача (зелений · червоний · без тесту · падіння)
Судить: вихід ≠ 0 · «N/M» з N ≠ M в останніх рядках · «є ✗» · тайм-аут. Рядки «✗ …» усередині виводу — НЕ збій
(детектори друкують очікуваний ✗ своїх випадків: clip, live_refs).
"""
import os, re, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
SKIP = {'selftest_all.py', 'audit_prompts.sh'}          # себе не ганяє; аудит — запуск моделей, не тест
NO_TEST_OK = {'profile_parts.py'}                        # бібліотека profile-test диспетчера — тестується там
SPECIAL = {'lens-hooks.sh': ['start-test', 'profile-test']}   # диспетчер: свої режими замість selftest
TIMEOUT = 150


def sid():
    return re.sub(r'\W', '', os.environ.get('CLAUDE_CODE_SESSION_ID') or os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID') or 'x')


def log_path():
    return os.environ.get('LENS_SELFTEST_LOG') or f'/tmp/lens-selftest-{sid()}.log'


def has_test(f):
    try: return 'selftest' in open(f, encoding='utf-8', errors='replace').read()
    except OSError: return False


def discover(dirs=(HERE, TOOLS)):
    out, missing = [], []
    for d in dirs:
        for n in sorted(os.listdir(d)):
            f = os.path.join(d, n)
            if not os.path.isfile(f) or not n.endswith(('.sh', '.py')) or n in SKIP: continue
            if n in SPECIAL or has_test(f): out.append(f)
            elif d == HERE and n not in NO_TEST_OK: missing.append(f)   # гачок без selftest — дірка (прилади поза hooks/ — не всі мають)
    return out, missing


def run_one(f, timeout=TIMEOUT):
    n = os.path.basename(f)
    modes = SPECIAL.get(n, ['selftest'])
    for m in modes:
        cmd = (['python3', f, m] if f.endswith('.py') else ['bash', f, m])
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=os.path.dirname(f), stdin=subprocess.DEVNULL,
                               env=dict(os.environ, LENS_NO_SELFTEST='1'))   # start-test кличе SessionStart → без цього bg ганяв би сам себе по колу
        except subprocess.TimeoutExpired:
            return False, f'{n} {m}: не встиг за {timeout} с'
        out = (r.stdout + r.stderr).strip().splitlines()
        tail = '\n'.join(out[-3:])
        frac = [(int(a), int(b)) for a, b in re.findall(r'(\d+)\s*/\s*(\d+)', tail)]
        bad = r.returncode != 0 or 'є ✗' in tail or any(a != b for a, b in frac[-1:])
        if bad:
            fx = [l.strip() for l in out if l.strip().startswith('✗')][:2]
            return False, f'{n} {m}: вихід {r.returncode} · ' + (' · '.join(fx) or (out[-1] if out else 'без виводу'))[:220]
    return True, n


def run(files, missing=()):
    t0, fails = time.time(), [f'{os.path.relpath(m, TOOLS)}: гачок без selftest — допиши режим selftest (чек-лист нового гачка, CLAUDE_CODE.md «Гачки»)' for m in missing]
    n = 0
    for f in files:
        ok, msg = run_one(f); n += 1
        if not ok: fails.append(msg)
    return fails, n, time.time() - t0


def main(a):
    if not a or a[0] == 'all':
        import fcntl
        lk = open(log_path() + '.lock', 'w')
        try: fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)   # один прогін за раз: другий старт / bg не множить процеси
        except OSError: print('selftest: прогін уже йде'); return 0
        files, missing = discover()
        fails, n, dt = run(files, missing)
        head = f'selftest усіх гачків і приладів ядра: {n - len([x for x in fails if "без selftest" not in x])}/{n} · {dt:.0f} с · {time.strftime("%H:%M")}'
        txt = '\n'.join([head] + ['✗ ' + x for x in fails])
        try: open(log_path(), 'w', encoding='utf-8').write(txt + '\n')
        except OSError: pass
        print(txt if fails else head); return 1 if fails else 0
    if a[0] == 'bg':
        if os.environ.get('LENS_NO_SELFTEST'): return 0   # запобіжник кола й на рівні самого запускача
        subprocess.Popen([sys.executable, os.path.abspath(__file__), 'all'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL, start_new_session=True)
        return 0
    if a[0] == 'files':
        fs = [os.path.abspath(x) for x in a[1:] if os.path.isfile(x)]
        fs = [f for f in fs if os.path.basename(f) not in SKIP and (os.path.basename(f) in SPECIAL or has_test(f))]
        fails, n, dt = run(fs)
        for x in fails: print('✗ ' + x)
        return 1 if fails else 0
    if a[0] == 'report':
        try: t = open(log_path(), encoding='utf-8').read().splitlines()
        except OSError: return 0
        for l in t[1:]:
            if l.startswith('✗'): print(l)
        return 0
    if a[0] == 'selftest':
        return selftest()
    print(__doc__); return 2


def selftest():
    d = tempfile.mkdtemp(prefix='sta-'); h = os.path.join(d, 'hooks'); os.makedirs(h)
    W = lambda p, s: open(p, 'w').write(s)
    W(os.path.join(h, 'green.sh'), '[ "$1" = selftest ] && { echo "✗ очікуваний ✗ детектора"; echo "─── green: 3/3 ───"; exit 0; }\n')
    W(os.path.join(h, 'red.sh'), '[ "$1" = selftest ] && { echo "✗ зламано"; echo "red: 2/3"; exit 0; }\n')
    W(os.path.join(h, 'crash.py'), 'import sys\nif sys.argv[1:] == ["selftest"]: raise KeyError("transcript_path")\n')
    W(os.path.join(h, 'notest.sh'), 'echo гачок\n')
    files, missing = discover((h,))
    global HERE; old = HERE; HERE = h
    try: files, missing = discover((h,))
    finally: HERE = old
    res = {os.path.basename(f): run_one(f, 20) for f in files}
    cases = [('зелений тест з очікуваними «✗» у виводі → ✓ (не хибне на clip / live_refs)', res.get('green.sh', (False,))[0]),
             ('«2/3» при виході 0 → ✗ (не вірити коду виходу)', not res.get('red.sh', (True,))[0]),
             ('падіння Python (KeyError) → ✗ з назвою помилки', not res.get('crash.py', (True,))[0] and 'вихід 1' in res['crash.py'][1]),
             ('гачок без selftest → у списку дірок', [os.path.basename(m) for m in missing] == ['notest.sh'])]
    os.environ['LENS_SELFTEST_LOG'] = os.path.join(d, 'log')
    W(os.environ['LENS_SELFTEST_LOG'], 'selftest …: 1/2\n✗ red.sh selftest: вихід 0 · ✗ зламано\n')
    r = subprocess.run([sys.executable, os.path.abspath(__file__), 'report'], capture_output=True, text=True, env=os.environ)
    cases.append(('report: лише рядки ✗ з журналу прогону', r.stdout.strip() == '✗ red.sh selftest: вихід 0 · ✗ зламано'))
    bad = 0
    for name, ok in cases:
        print(('✓ ' if ok else '✗ ') + name); bad += not ok
    print(f'─── selftest_all selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
