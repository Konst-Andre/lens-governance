#!/bin/bash
# живе доки: сесії переїжджають у нові чати, а пам'ять — лише репо (профіль Konst «САМЕРІ»).
# Дім — lens-governance:tools/claude-code/hooks/ (HOOK-3.2, бриф — kernel/Lens_kernel_BRIEFS.md §HOOK-3.2; «так» Konst 09.10.2026).
# Подія UserPromptSubmit: у повідомленні Konst — «переїжджаємо» · «переїзд» · «нова сесія» · «стартове повідомлення» →
# tools/claude-code/handoff_check.py на кожне репо сесії (/home/user/*, де є sessions/) → additionalContext: рядки ✓/⚠/✗ + чек-лист
# «очима нового агента». Повідомлення Konst не блокує. Тиша: перше повідомлення сесії (стартове саме містить «переїзд» — переїжджати
# ще нема з чого) · повтор без нових комітів (позначка /tmp/lens-handoff-<session_id> = HEAD усіх репо) · помилка розбору.
# Формат — code.claude.com/docs/en/hooks «UserPromptSubmit» (поле prompt; additionalContext ≤ 10 000 знаків), 09.10.2026.
# + Stop (bash handoff-remind.sh stop): переїзд оголошує АГЕНТ (стартове ```text чи «переїжджаємо» у відповіді) і є ✗ → decision: block (раз на стан HEAD; stop_hook_active → тиша).
# Зуби: bash handoff-remind.sh selftest — 9 випадків (тригер → контекст з ✗; не тригер · «в новій сесії» в розповіді · перше повідомлення · повтор → тиша;
# новий коміт → знову; Stop: стартове з ✗ → block, звичайна відповідь і повтор → тиша).
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN HC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/handoff_check.py"
python3 - "$mode" <<'PY'
import json, os, re, subprocess, sys, tempfile, glob
TRIG = re.compile(r"переїжджа\w*|переїхати|переїдемо|стартов\w+\s+повідомлен\w*|\bнов[ау]\s+сесі[яю]\b", re.I)   # лише команди: «переїжджаємо / переїхати / стартове / нову сесію»; іменник «переїзд» — розповідь (тричі хибне 10.10, журнал гачків §1)
HC = os.environ['HC']

def repos(roots):
    out = []
    for root in roots:
        for d in sorted(glob.glob(os.path.join(root, '*', '.git'))):
            r = os.path.dirname(d)
            if os.path.isdir(os.path.join(r, 'sessions')): out.append(r)
    return out

def heads(rs):
    return ' '.join(subprocess.run(['git', '-C', r, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip() for r in rs)

def first_prompt(tp):
    try:
        for l in open(os.path.expanduser(tp), encoding='utf-8'):
            if l.strip() and json.loads(l).get('type') == 'assistant': return False
    except (OSError, ValueError): return False
    return True

def run(d, roots, mark_dir='/tmp'):
    if not TRIG.search(d.get('prompt') or ''): return None
    if first_prompt(d.get('transcript_path') or ''): return None
    rs = repos(roots)
    if not rs: return None
    mark = os.path.join(mark_dir, 'lens-handoff-' + re.sub(r'\W', '', d.get('session_id') or 'x'))
    h = heads(rs)
    if os.path.exists(mark) and open(mark).read() == h: return None
    open(mark, 'w').write(h)
    r = subprocess.run([sys.executable, HC, *rs], capture_output=True, text=True)
    return ("Гачок «перевірка пам'яті перед переїздом» (HOOK-3.2) — handoff_check:\n" + r.stdout.strip()[:6000] +
            "\n\nДо стартового повідомлення: ✗ — виправ і закоміть; ⚠ — звір. Потім прочитай §0 і стартове ОЧИМА НОВОГО АГЕНТА: "
            "(а) з першого екрана ясно, що робимо далі й у якому порядку? (б) нема історії замість «як є»? "
            "(в) кожне правило сесії — у своєму домі, а не лише в самері? (г) план має «зараз і далі» зверху? "
            "(д) що новий агент мусить знати, а воно є лише в чаті (рішення, побажання й побоювання Konst — як побажання, не як догма)? "
            "Знахідки — виправ і закоміть, тоді стартове в чат. Якщо Konst не переїжджає (слово випадкове) — проігноруй цей контекст.")

def selftest():
    t = tempfile.mkdtemp(prefix='hr-'); r = os.path.join(t, 'Prod')
    os.makedirs(os.path.join(r, 'sessions'))
    sh = lambda *c: subprocess.run(c, cwd=r, check=True, capture_output=True)
    sh('git', 'init', '-q'); sh('git', 'config', 'user.email', 't@t'); sh('git', 'config', 'user.name', 't')
    open(os.path.join(r, 'sessions/P_session_summary_X.md'), 'w').write('## §0 ВІДКРИТЕ\n- гачок `ui-review-gate.sh`\n')
    sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 's')
    tr = lambda msgs: (lambda f: (f.write('\n'.join(json.dumps(m) for m in msgs)), f.close(), f.name)[2])(tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False))
    mid = tr([{'type': 'user', 'message': {'content': 'привіт'}}, {'type': 'assistant', 'message': {'content': []}}])
    first = tr([{'type': 'user', 'message': {'content': 'старт'}}])
    D = lambda p, tp, s='s1': {'prompt': p, 'transcript_path': tp, 'session_id': s}
    cases = [('«переїжджаємо» → контекст з ✗', D('Ок, переїжджаємо', mid), '✗'),
             ('не тригер → тиша', D('Що там зі збіркою?', mid, 's2'), None),
             ('перше повідомлення сесії (стартове з «переїздом») → тиша', D('Гачок перевірки перед переїздом', first, 's3'), None),
             ('повтор без нових комітів → тиша', D('нова сесія', mid), None)]
    bad = 0
    for name, d, want in cases:
        out = run(d, [t], t)
        ok = (out is None) if want is None else (out is not None and want in out and 'НОВОГО АГЕНТА' in out)
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    open(os.path.join(r, 'x.md'), 'w').write('x'); sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'x')
    ok = run(D('Стартове повідомлення дай', mid), [t], t) is not None
    print(('✓' if ok else '✗') + ' новий коміт після проходу → знову'); bad += not ok
    ok = run(D('боюсь, що в новій сесії агент нічого не зрозуміє, а гачок перед переїздом перевіряє документи. Бо переїзд це по суті кінець сесії', mid, 's5'), [t], t) is None
    print(('✓' if ok else '✗') + ' «в новій сесії» · «перед переїздом» у розповіді (хибне 09.10) → тиша'); bad += not ok
    S = lambda m, a=False, s='p1': {'last_assistant_message': m, 'stop_hook_active': a, 'session_id': s}
    for name, d, want in [('Stop: агент дає стартове, є ✗ → block', S('Переїжджаємо. ```text\nСтарт: …\n```'), True),
                          ('Stop: звичайна відповідь → тиша', S('Готово, коміт abc.', s='p2'), False),
                          ('Stop: повтор через гачок (stop_hook_active) → тиша', S('```text\nx\n```', True, 'p3'), False)]:
        out = stop(d, [t], t); ok = (out is not None and '✗' in out) == want
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    print(f'selftest: {9 - bad}/9'); return 1 if bad else 0

def stop(d, roots, mark_dir='/tmp'):
    """Stop: переїзд оголошує агент (стартове чи «переїжджаємо» у відповіді) — є ✗ → block, щоб виправив до кінця ходу."""
    if d.get('stop_hook_active'): return None
    msg = d.get('last_assistant_message') or ''
    if not (TRIG.search(msg) or re.search(r'```text', msg)): return None
    rs = repos(roots)
    if not rs: return None
    mark = os.path.join(mark_dir, 'lens-handoff-stop-' + re.sub(r'\W', '', d.get('session_id') or 'x'))
    h = heads(rs)
    if os.path.exists(mark) and open(mark).read() == h: return None
    open(mark, 'w').write(h)
    r = subprocess.run([sys.executable, HC, *rs], capture_output=True, text=True)
    bad = [l for l in r.stdout.splitlines() if l.strip().startswith('✗')]
    if not bad: return None
    return ("Гачок «перевірка пам'яті перед переїздом» (HOOK-3.2, Stop): ти оголошуєш переїзд, а handoff_check має ✗ —\n" + '\n'.join(bad)[:4000] +
            "\nВиправ, закоміть і запуш, тоді стартове. Якщо це не переїзд — одним рядком скажи це й заверши.")

mode = sys.argv[1]
if mode == 'selftest': sys.exit(selftest())
if mode == 'stop':
    try: out = stop(json.loads(os.environ.get('HOOK_IN') or '{}'), ['/home/user'])
    except Exception: out = None
    if out: print(json.dumps({'decision': 'block', 'reason': out}, ensure_ascii=False))
    sys.exit(0)
try:
    d = json.loads(os.environ.get('HOOK_IN') or '{}')
    roots = ['/home/user']
    out = run(d, roots)
except Exception:
    out = None
if out:
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': out}}, ensure_ascii=False))
PY
