#!/usr/bin/env python3
# живе доки: пам'ять сесії — лише репо, і сесії переїжджають у нові чати (профіль Konst «САМЕРІ»).
# Перевірка пам'яті перед переїздом (HOOK-3.2, бриф — kernel/Lens_kernel_BRIEFS.md §HOOK-3.2; «так» Konst 09.10.2026, QR-Lens CC-5).
# Ловить машинно те, що новий агент не зможе знайти чи зрозуміти: самері без §0 / стартового, самері відстає від комітів,
# мертві й голі шляхи в §0 · стартовому · «Коротко» плану, історія в §0, гейт черги, README старіший за правила.
# Якість тексту НЕ судить — це робить агент за чек-листом гачка hooks/handoff-remind.sh.
#
# Запуск:  python3 tools/claude-code/handoff_check.py <тека репо> [<тека репо> …]    → рядки ✓ / ⚠ / ✗ / ⓘ; exit 1 на ✗
#          python3 tools/claude-code/handoff_check.py selftest                         → зуби: тимчасові репо, усі випадки брифу
# «Свої» коміти — за трейлером Claude-Session ≡ CLAUDE_CODE_REMOTE_SESSION_ID (cse_X ↔ session_X); нема змінної — усі коміти агента.
import os, re, subprocess, sys, tempfile, time

KERNEL_NAMES = ('lens-governance',)
EXT = r'(?:md|sh|py|mjs|js|json|toml|ya?ml|html|htm|css|xlsx|txt|csv)'
# шлях: [Репо:]тека/…/файл.розш · тека/ · або гола назва файл.розш (без теки)
PATH_RE = re.compile(r'(?<![\w/.:<>*-])(?:([A-Za-z][\w.-]*):)?((?:[\w.-]+/)+(?:[\w.-]+\.' + EXT + r')?|[\w.-]+\.' + EXT + r')(?![\w/<>*-])')
STALE_RE = re.compile(r'цей коміт|чекає вироку', re.I)


def git(repo, *a):
    r = subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ''


def section(text, head_re):
    """Текст розділу «## …», чий заголовок збігся з head_re, до наступного «## »."""
    out, on = [], False
    for ln in text.splitlines():
        if ln.startswith('## '):
            if on: break
            on = bool(re.search(head_re, ln, re.I))
            continue
        if on: out.append(ln)
    return '\n'.join(out) if on or out else None


def starter(text):
    m = re.search(r'^```text[^\n]*\n(.*?)^```', text, re.M | re.S)
    return m.group(1) if m else None


def live_summary(repo):
    """Живе самері в sessions/ (і sessions/*/): ще не в коміті → найновіше; інакше — останній коміт, при рівному — пізніше створене
    (заморожене попереднє й нове міняються одним комітом)."""
    best, bt = None, None
    for root, _, files in os.walk(os.path.join(repo, 'sessions')):
        for f in files:
            if not (f.endswith('.md') and 'summary' in f): continue
            p = os.path.join(root, f); rel = os.path.relpath(p, repo)
            last = int(git(repo, 'log', '-1', '--format=%ct', '--', rel) or 0)
            born = git(repo, 'log', '--diff-filter=A', '--format=%ct', '--', rel).split()
            t = (float('inf'), 0) if not last else (last, int(born[-1]) if born else 0)
            if bt is None or t > bt: best, bt = rel, t
    return best


def repo_dir(repo, name):
    """Тека іншого репо для «Репо:шлях»: сусідня тека, для ядра — ще /tmp/lens-governance."""
    base = os.path.dirname(os.path.abspath(repo))
    if os.path.basename(os.path.abspath(repo)).lower() == name.lower(): return repo
    for c in os.listdir(base):
        if c.lower() == name.lower() and os.path.isdir(os.path.join(base, c)): return os.path.join(base, c)
    if name.lower() in KERNEL_NAMES and os.path.isdir('/tmp/lens-governance'): return '/tmp/lens-governance'
    return None


def check_paths(repo, text, where, lines):
    dead, bare, other, seen = [], [], set(), set()
    for m in PATH_RE.finditer(text):
        rp, p = m.group(1), m.group(2)
        if rp and rp.lower() in ('http', 'https'): continue
        key = (rp or '') + ':' + p
        if key in seen: continue
        seen.add(key)
        if rp:
            d = repo_dir(repo, rp)
            if d is None: other.add(rp); continue
            if not os.path.exists(os.path.join(d, p)): dead.append(f'{rp}:{p}')
        elif '/' not in p:
            if not os.path.exists(os.path.join(repo, p)): bare.append(p)
        elif not os.path.exists(os.path.join(repo, p)):
            dead.append(p)
    n = len(seen)
    if dead: lines.append(('✗', f'{where}: мертві шляхи — ' + ' · '.join(dead[:8])))
    if bare: lines.append(('✗', f'{where}: голі назви (новий агент не знайде) — ' + ' · '.join(bare[:8]) + ' → дай повний шлях'))
    if other: lines.append(('ⓘ', f'{where}: шляхи інших репо не звірено (нема поруч) — ' + ', '.join(sorted(other))))
    if not dead and not bare: lines.append(('✓', f'{where}: шляхи живі ({n})'))


def mine_tail():
    sid = os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID', '')
    return sid.split('_', 1)[1] if '_' in sid else ''


def check_repo(repo, now=None):
    now = now or time.time()
    repo = os.path.abspath(repo)
    name = os.path.basename(repo)
    is_kernel = os.path.isdir(os.path.join(repo, 'kernel'))
    L = []
    sm = live_summary(repo)
    if not sm:
        L.append(('✗', 'самері в sessions/ не знайдено')); return name, L
    text = open(os.path.join(repo, sm), encoding='utf-8').read()
    s0, st = section(text, r'^## §0'), starter(text)
    L.append(('✓' if s0 else '✗', f'{sm}: §0 ' + ('є' if s0 else 'нема (заголовок «## §0 …»)')))
    L.append(('✓' if st else '✗', 'стартове повідомлення ' + ('є (блок text)' if st else 'нема — блок ```text у самері')))
    # (2) самері не відстає — логіка QR-Lens:tools/env_check.sh «самері відстає»
    last = git(repo, 'log', '-1', '--format=%H', '--', sm)
    tail = mine_tail()
    grep = f'session_{tail}' if tail else 'Claude-Session'
    after = git(repo, 'log', '--format=%h', f'--grep={grep}', f'{last}..HEAD') if last else ''
    n = len(after.split()) if after else 0
    owns = (not tail) or bool(git(repo, 'log', '--format=%h', f'--grep=session_{tail}', '--', 'sessions/'))
    if n and is_kernel and not owns:
        L.append(('ⓘ', f'самері ядра веде сесія ядра; коміти цієї сесії тут — {n}: вони мають бути в самері репо продукту (Lens_governance_protocol.md:139)'))
    elif n:
        L.append(('✗', f'самері відстає: після {last[:7]} комітів агента без самері — {n} ({" ".join(after.split()[:5])}) → §0/§1'))
    else:
        L.append(('✓', 'самері не відстає'))
    # (3) шляхи: §0 · стартове · «Коротко» планів, на які посилається §0
    if s0: check_paths(repo, s0, '§0', L)
    if st: check_paths(repo, st, 'стартове', L)
    for m in PATH_RE.finditer(s0 or ''):
        rp, p = m.group(1), m.group(2)
        if rp or not p.endswith('.md') or 'sessions/' in p: continue
        f = os.path.join(repo, p)
        if not os.path.isfile(f): continue
        k = section(open(f, encoding='utf-8').read(), r'Коротко')
        if k is not None: check_paths(repo, k, f'{p} «Коротко»', L)
    # (4) історія в §0
    if s0:
        h = sorted({m.group(0).lower() for m in STALE_RE.finditer(s0)})
        if h: L.append(('⚠', '§0 має «' + '», «'.join(h) + '» — історія чи ще відкрите? (у §0 — лише як є)'))
    # (5) гейт: черга під стелею, рядки ≤ 2000 знаків — Lens_validate.py
    kd = repo if is_kernel else repo_dir(repo, 'lens-governance')
    v = os.path.join(kd or '', 'kernel/Lens_validate.py')
    if kd and os.path.isfile(v) and (is_kernel or os.path.isdir(os.path.join(repo, 'lens'))):
        r = subprocess.run([sys.executable, v, '--gov' if is_kernel else '--product', '.'], cwd=repo, capture_output=True, text=True)
        tot = [x for x in r.stdout.splitlines() if 'ПІДСУМОК' in x]
        s = tot[-1].strip() if tot else 'підсумку нема'
        L.append(('✗' if re.search(r'✗ [1-9]', s) else '✓', 'гейт: ' + s))
    # (6) README старший за 7 дн., а CLAUDE.md новіший
    rt = int(git(repo, 'log', '-1', '--format=%ct', '--', 'README.md') or 0)
    ct = int(git(repo, 'log', '-1', '--format=%ct', '--', 'CLAUDE.md') or 0)
    if os.path.isfile(os.path.join(repo, 'README.md')):
        if not rt: L.append(('ⓘ', 'README: дата невідома (неглибока історія)'))
        elif now - rt > 7 * 86400 and ct > rt: L.append(('⚠', f'README не мінявся {int((now - rt) // 86400)} дн., а CLAUDE.md мінявся після — перевір README'))
    return name, L


def report(repos):
    bad = False
    for r in repos:
        name, L = check_repo(r)
        print(f'— {name}')
        for s, t in L:
            print(f'  {s} {t}'); bad |= s == '✗'
    return 1 if bad else 0


def selftest():
    def sh(d, *c): subprocess.run(c, cwd=d, check=True, capture_output=True)
    def mk(summary, extra=None, commit_after=False, new_after=False, both=False):
        d = tempfile.mkdtemp(prefix='hc-'); r = os.path.join(d, 'Prod'); os.makedirs(os.path.join(r, 'sessions')); os.makedirs(os.path.join(r, 'lens'))
        sh(r, 'git', 'init', '-q'); sh(r, 'git', 'config', 'user.email', 't@t'); sh(r, 'git', 'config', 'user.name', 't')
        open(os.path.join(r, 'lens/A.md'), 'w').write('## 0. Коротко\n- далі `lens/A.md`\n')
        open(os.path.join(r, 'CLAUDE.md'), 'w').write('x')
        later = extra if new_after else {}
        for p, t in (extra or {}).items():
            if p not in later: open(os.path.join(r, p), 'w').write(t)
        open(os.path.join(r, 'sessions/P_session_summary_X.md'), 'w').write(summary)
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'самері\n\nClaude-Session: https://claude.ai/code/session_T')
        if later:
            time.sleep(1.1)
            for p, t in later.items(): open(os.path.join(r, p), 'w').write(t)
            if both:
                open(os.path.join(r, 'sessions/P_session_summary_X.md'), 'a').write('заморожено\n')
                sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'нове самері\n\nClaude-Session: https://claude.ai/code/session_T')
        if commit_after:
            open(os.path.join(r, 'lens/A.md'), 'a').write('y'); sh(r, 'git', 'commit', '-qam', 'код\n\nClaude-Session: https://claude.ai/code/session_T')
        return r
    good = '# S\n## §0 ВІДКРИТЕ\n- далі `lens/A.md` §0 «Коротко»; правила — CLAUDE.md\n## §6 Стартове\n```text\nСтарт: lens/A.md → sessions/P_session_summary_X.md\n```\n'
    os.environ['CLAUDE_CODE_REMOTE_SESSION_ID'] = 'cse_T'
    cases = [
        ('усе гаразд → тиша (лише ✓/ⓘ)', mk(good), None),
        ('самері без стартового → ✗', mk(good.split('## §6')[0]), 'стартове повідомлення нема'),
        ('гола назва ui-review-gate.sh → ✗', mk(good.replace('правила — CLAUDE.md', 'гачок `ui-review-gate.sh`')), 'голі назви'),
        ('мертвий lens/X.md → ✗', mk(good.replace('правила — CLAUDE.md', 'план `lens/X.md`')), 'мертві шляхи'),
        ('мертвий шлях у «Коротко» плану → ✗', mk(good, {'lens/A.md': '## 0. Коротко\n- `lens/Gone.md`\n'}), 'мертві шляхи'),
        ('коміт агента після самері → ✗', mk(good, commit_after=True), 'самері відстає'),
        ('«цей коміт» у §0 → ⚠', mk(good.replace('- далі', '- цей коміт; далі')), '§0 має «цей коміт»'),
        ('нове самері ще не в коміті → бере його (без стартового → ✗)', mk(good, {'sessions/P_session_summary_Y.md': '## §0 В\n- `lens/A.md`\n'}, new_after=True), 'P_session_summary_Y'),
        ('старе й нове в одному коміті → бере пізніше створене', mk(good, {'sessions/P_session_summary_Y.md': '## §0 В\n- `lens/A.md`\n'}, new_after=True, both=True), 'P_session_summary_Y'),
    ]
    bad = 0
    for name, r, want in cases:
        _, L = check_repo(r)
        hit = [t for s, t in L if s in '✗⚠']
        ok = (not hit) if want is None else any(want in t for t in (hit if 'summary' not in want else [t for _, t in L]))
        if want is None and not ok: print('   ', hit)
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    print(f'selftest: {len(cases) - bad}/{len(cases)}')
    return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__ or 'handoff_check.py <тека репо> … | selftest'); sys.exit(2)
    sys.exit(selftest() if a[0] == 'selftest' else report(a))
