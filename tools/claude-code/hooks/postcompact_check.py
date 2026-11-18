#!/usr/bin/env python3
# postcompact_check.py · гачок ядра: після стиснення — звірка ПЕРЕКАЗУ з фактами репо (Ж3 FAB-2; Konst 12.11.2026: «перевірка після стиснення —
#   чи модель досі розуміє, що відбувається, чи втратила пам'ять» — «важлива штука»; перенесено з чернетки AE S153, «так, прошу підсилити» Konst 18.11.2026).
# живе доки: диспетчер lens-hooks.sh кличе його на SessionStart з source «compact»; зняли виклик — файл прибрати.
# Що робить: бере текст переказу з журналу сесії (рядок isCompactSummary) і факти git кожного репо сесії — гілка · HEAD · чи HEAD на GitHub ·
#   незакомічене · коміти цієї сесії (трейлер Claude-Session) · живе самері — і кладе агентові: факти + «✓ переказ тримає …» або «⚠ у переказі БРАКУЄ …».
#   Агент пише вердикт у §1 самері рядком «стиснення N: переказ ✓ / загубив: …» (вимогу дає ctx_watch.py — тут не дублюється). Нічого не блокує.
# Підсилення проти чернетки (AE S153): (1) живе самері — за останнім комітом у docs/summary/, не за mtime (після свіжого клону mtime усіх файлів однаковий —
#   вибір був би навмання); (2) незакомічене після автостиснення — факт і перевірка «чи переказ про нього знає» (сторож PreCompact автостиснення не зупиняє);
#   (3) HEAD не на GitHub — факт; (4) без репо — один рядок «ⓘ», не мовчазне «✓»; (5) вихід — JSON SessionStart, ≤ 10 000 знаків (стеля additionalContext).
# Звідки переказ: журнал сесії, рядок isCompactSummary — пишеться ДО SessionStart(compact): AE S153 18.11.2026, рядки 1019 → 1034 журналу, 2,4 с.
#   Подію PostCompact (поле compact_summary, code.claude.com/docs/en/hooks.md, 18.11.2026) НЕ беремо: її треба вписати в setup script середовища (рішення Konst),
#   а журнал дає той самий текст без правки середовища.
# Запуск: echo '<json SessionStart>' | python3 postcompact_check.py hook     ·     python3 postcompact_check.py selftest  (зуби — 12 випадків на тимчасових репо)
import glob, json, os, subprocess, sys, tempfile

CAP = 10000

def git(r, *a):
    p = subprocess.run(['git', '-C', r, *a], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ''

def live_summary(r):
    """Живе самері — файл з останнього коміту, що зачепив docs/summary/ (або sessions/*/ ядра); нема — найпізніший за ім'ям."""
    for d in ('docs/summary', 'sessions'):
        if not os.path.isdir(os.path.join(r, d)): continue
        for f in git(r, 'log', '-5', '--format=', '--name-only', '--diff-filter=AM', '--', d).splitlines():
            if f.endswith('.md') and 'summary' in f.lower() and os.path.exists(os.path.join(r, f)): return f
    names = sorted(glob.glob(os.path.join(r, 'docs/summary/*.md')))
    return os.path.relpath(names[-1], r) if names else ''

def facts(root, sid):
    out = []
    for r in sorted(glob.glob(root.rstrip('/') + '/*/')):
        if not os.path.isdir(r + '.git') or os.path.exists(r + '.git/lens-readonly'): continue
        head = git(r, 'rev-parse', '--short', 'HEAD')
        if not head: continue
        up = git(r, 'rev-parse', '--short', '@{u}')
        dirty = [ln[3:] for ln in git(r, 'status', '--porcelain', '--untracked-files=normal').splitlines() if ln[3:]]
        commits = git(r, 'log', '-20', '--grep', 'Claude-Session: .*' + sid, '--format=%h').split() if sid else []
        out.append(dict(repo=os.path.basename(r.rstrip('/')), head=head, branch=git(r, 'branch', '--show-current'),
                        pushed=(up == head) if up else None, dirty=dirty, commits=commits, summary=live_summary(r)))
    return out

def from_transcript(path):
    last = ''
    if path and os.path.exists(path):
        for ln in open(path, encoding='utf-8', errors='replace'):
            if '"isCompactSummary"' not in ln: continue
            try: r = json.loads(ln)
            except ValueError: continue
            if r.get('isCompactSummary'):
                c = (r.get('message') or {}).get('content', '')
                last = c if isinstance(c, str) else ' '.join(x.get('text', '') for x in c if isinstance(x, dict))
    return last

def missing(text, fs):
    m = []
    for f in fs:
        if f['head'] not in text: m.append(f"HEAD {f['repo']} {f['head']}")
        lost = [c for c in f['commits'] if c not in text]
        if f['commits'] and len(lost) > len(f['commits']) // 2: m.append(f"коміти сесії в {f['repo']}: нема {len(lost)} з {len(f['commits'])}")
        if f['summary'] and os.path.basename(f['summary']) not in text: m.append(f"живе самері {f['repo']} ({os.path.basename(f['summary'])})")
        if f['dirty'] and not any(os.path.basename(p.rstrip('/')) in text for p in f['dirty']):
            m.append(f"незакомічене в {f['repo']} ({len(f['dirty'])}: {', '.join(f['dirty'][:3])})")
    return m

def report(text, fs):
    L = ['Після стиснення: переказ — не джерело; джерело — репо. Факти від програми (postcompact_check, на цю мить):']
    if not fs: return L[0] + '\nⓘ репо сесії не знайдено — звіряти нема з чим.'
    for f in fs:
        s = f"- {f['repo']} · гілка {f['branch'] or '(без гілки)'} · HEAD {f['head']}"
        s += {True: ' (на GitHub)', False: ' · ⚠ HEAD не на GitHub — push', None: ' · ⓘ без upstream'}[f['pushed']]
        if f['dirty']: s += f" · ⚠ незакомічене {len(f['dirty'])}: {', '.join(f['dirty'][:3])}"
        if f['commits']: s += f" · комітів сесії {len(f['commits'])}"
        if f['summary']: s += f" · живе самері {f['summary']}"
        L.append(s)
    if not text: L.append('ⓘ тексту переказу в журналі сесії нема — звірити не було з чим; прочитай §0 живого самері.')
    else:
        m = missing(text, fs)
        L.append('✓ переказ тримає HEAD кожного репо, коміти сесії й живе самері.' if not m else
                 '⚠ у переказі БРАКУЄ: ' + '; '.join(m) + ' — довіряй фактам вище й §0 самері, не переказу; назви це Konst у першій відповіді.')
    return '\n'.join(L)[:CAP]

def hook(inp, root, sid):
    if inp.get('source') != 'compact': return ''
    t = report(from_transcript(inp.get('transcript_path', '')), facts(root, sid))
    return json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': t}}, ensure_ascii=False)

def env_sid():
    s = os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID', '')
    for p in ('cse_', 'session_'):
        if s.startswith(p): s = s[len(p):]
    return s

def selftest():
    t = tempfile.mkdtemp(); w = t + '/w'; bad = 0; n = 0
    env = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='commit.gpgsign', GIT_CONFIG_VALUE_0='false')
    def sh(r, *c): subprocess.run(c, cwd=r, check=True, capture_output=True, env=env)
    def mk(name, files, msg):
        r = f'{w}/{name}'; os.makedirs(r, exist_ok=True)
        if not os.path.isdir(r + '/.git'): sh(r, 'git', 'init', '-q'); sh(r, 'git', 'config', 'user.email', 'a@b'); sh(r, 'git', 'config', 'user.name', 't')
        for p, body in files.items():
            os.makedirs(os.path.dirname(f'{r}/{p}'), exist_ok=True); open(f'{r}/{p}', 'w').write(body)
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', msg); return r
    def case(name, ok):
        nonlocal bad, n; n += 1; print(('✓ ' if ok else '✗ ') + name); bad += not ok
    sess = 'msg\n\nClaude-Session: https://claude.ai/code/session_TESTSID'
    r = mk('repoA', {'docs/summary/AE_SUMMARY_2026-01-02.md': '§0\n'}, 'c0')
    mk('repoA', {'docs/summary/AE_SUMMARY_2026-01-01.md': '§0\n'}, sess)   # старше за ім'ям, але останній коміт — його
    hd = git(r, 'rev-parse', '--short', 'HEAD'); good = f'HEAD repoA {hd}; самері AE_SUMMARY_2026-01-01.md'
    rep = lambda txt: report(txt, facts(w, 'TESTSID'))
    case('повний переказ → ✓', '✓ переказ тримає' in rep(good))
    case('переказ без HEAD і самері → ⚠ БРАКУЄ з назвами', all(x in rep('щось робили') for x in ('БРАКУЄ', f'HEAD repoA {hd}', 'живе самері repoA', 'коміти сесії')))
    case('переказу нема → ⓘ, а факти є', (lambda o: 'нема — звірити' in o and hd in o)(rep('')))
    os.utime(f'{r}/docs/summary/AE_SUMMARY_2026-01-02.md', (4e9, 4e9))
    case('живе самері — за комітом, не за mtime (свіжий клон)', 'AE_SUMMARY_2026-01-01.md' in rep('') and 'AE_SUMMARY_2026-01-02' not in rep(''))
    open(f'{r}/draft_x.py', 'w').write('x')
    case('незакомічене, про яке переказ мовчить → ⚠ з назвою файла', 'незакомічене в repoA (1: draft_x.py)' in rep(good))
    case('незакомічене, назване в переказі → ✓', '✓ переказ тримає' in rep(good + ' · не закомічено draft_x.py'))
    os.remove(f'{r}/draft_x.py')
    bare = t + '/remote.git'; subprocess.run(['git', 'init', '-q', '--bare', bare], check=True, capture_output=True)
    sh(r, 'git', 'remote', 'add', 'origin', bare); sh(r, 'git', 'push', '-q', '-u', 'origin', 'HEAD:main')
    br = git(r, 'branch', '--show-current'); sh(r, 'git', 'branch', '-q', '--set-upstream-to', 'origin/main', br)
    case('HEAD на GitHub → «(на GitHub)»', '(на GitHub)' in rep(good))
    mk('repoA', {'x.txt': '1'}, sess); hd2 = git(r, 'rev-parse', '--short', 'HEAD')
    case('HEAD не на GitHub → ⚠ push', 'HEAD не на GitHub' in rep(good + hd2))
    mk('repoR', {'a.txt': '1'}, 'r'); open(f'{w}/repoR/.git/lens-readonly', 'w').write('')
    case('репо лише на читання (lens-readonly) — поза звіркою', 'repoR' not in rep(good))
    tr = t + '/tr.jsonl'; open(tr, 'w').write(json.dumps({'type': 'user', 'isCompactSummary': True, 'message': {'content': [{'type': 'text', 'text': good + ' ' + hd2}]}}) + '\n')
    o = hook({'source': 'compact', 'transcript_path': tr}, w, 'TESTSID')
    case('гачок: переказ із журналу сесії (isCompactSummary) → чинний JSON SessionStart ≤ 10 000, ✓',
         (lambda d: d['hookSpecificOutput']['hookEventName'] == 'SessionStart' and len(d['hookSpecificOutput']['additionalContext']) <= CAP
          and '✓ переказ тримає' in d['hookSpecificOutput']['additionalContext'])(json.loads(o)))
    case('SessionStart не після стиснення (startup · resume) → тиша', hook({'source': 'startup'}, w, 'TESTSID') == '' == hook({'source': 'resume'}, w, 'TESTSID'))
    case('репо нема → «ⓘ репо не знайдено», не мовчазне ✓', 'не знайдено' in report(good, facts(t + '/none', 'TESTSID')))
    print(f'─── postcompact_check selftest: {n - bad}/{n} ───'); return 1 if bad else 0

if __name__ == '__main__':
    if sys.argv[1:2] == ['selftest']: sys.exit(selftest())
    try: inp = json.load(sys.stdin)
    except ValueError: inp = {}
    out = hook(inp, os.environ.get('LENS_ROOT', '/home/user'), env_sid())
    if out: print(out)
