#!/bin/bash
# живе доки: агент звітує Konst словами «можна /compact» і рядками «пропуск Konst» у журналі гачків. Дім — lens-governance:tools/claude-code/hooks/ (AE S146, «так» Konst 14.11.2026).
# Чому (Konst S146: «мені мало того, що ти просто записав… щоб ти виконував те, що пишеш, а не просто написав»): двічі за сесію агент
#   (1) сказав «можна /compact», не прогнавши сторож стиснення, і (2) звітував рядком «пропуск Konst» у журналі як дією, хоча виправлення ще не було.
#   Правило «будь уважнішим» не спрацювало двічі → машина судить лише вимірне: сторож · хеш коміту · зуб.
# Подія Stop (code.claude.com/docs/en/hooks «Stop»: last_assistant_message, decision block + reason, stop_hook_active; 14.11.2026):
#   ① у відповіді «можна /compact» → сам проганяє сторож стиснення (precompact_guard.sh, «ручне», позначки — у тимчасову теку) → зупинив би → block з його причиною;
#   ② рядок «пропуск Konst», доданий у HOOK_JOURNAL.md цією сесією (комітами з міткою сесії + незакомічене), без хешу коміту, що є в git, і без зуба
#      (selftest · --inject · INJECT · чек-лист) → block; виняток — «НЕ ЗРОБЛЕНО: чому · коли» в рядку;
#   ③ є такий відкритий рядок цієї сесії, а у відповіді нема слів «не зроблено» в перших 1500 знаках → block (Konst бачить невиконане першим, не «записано»).
#   stop_hook_active не пропускає (інакше друга спроба обходила б суд), але стеля — 3 зупинки поспіль, далі пропуск і рядок «⚠ обійдено» в журнал спрацювань.
# Подія UserPromptSubmit (режим open): кожен рядок журналу з «НЕ ЗРОБЛЕНО» (будь-якої сесії) → нагадування агентові на початку ходу, доки не закрито.
# Розмиті слова («записав») не судить — зупиняв би даремно. Помилка розбору → тиша (stderr — у журнал помилок диспетчера).
# Зуби: bash promise-guard.sh selftest — 18 випадків на тимчасовому репо; PG_INJECT=1|2|3 bash promise-guard.sh selftest — кожен ✗ (зламаний суд червоніє).
mode="${1:-stop}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN PG_SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 - "$mode" <<'PY'
import json, os, re, subprocess, sys, tempfile
HERE = os.environ['PG_SELF']
CLAIM = re.compile(r"(?<!не )(?<!не\s\s)можна\s+(?:робити\s+|запускати\s+)?/compact", re.I)
MISS = re.compile(r"пропуск Konst", re.I)
OPEN = re.compile(r"(?<!«)НЕ ЗРОБЛЕНО:")   # мітка — з двокрапкою; згадка правила «НЕ ЗРОБЛЕНО» в лапках — не обіцянка (хибне S146, хід 9)
HASH = re.compile(r"`([0-9a-f]{7,40})`")
TEETH = re.compile(r"зуб|selftest|--inject|INJECT|чек-лист", re.I)
SAID = re.compile(r"не зроблено", re.I)
env = lambda k, d: os.environ.get(k) or d

def git(repo, *a):
    r = subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def repos():
    root = env('LENS_ROOT', '/home/user')
    return [os.path.join(root, n) for n in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, n, '.git'))] if os.path.isdir(root) else []

INJ = os.environ.get('PG_INJECT', '')   # зуби selftest: 1 — будь-який хеш «є в git»; 2 — заяву «можна /compact» не бачить; 3 — коміти сесії не рахуються
def exists(h):
    if INJ == '1': return True
    return any(git(r, 'cat-file', '-e', h + '^{commit}') is not None for r in repos())

def sid(d):
    s = env('CLAUDE_CODE_REMOTE_SESSION_ID', '') or d.get('session_id') or ''
    for p in ('cse_', 'session_'): s = s[len(p):] if s.startswith(p) else s
    return re.sub(r'[^A-Za-z0-9_-]', '', s)

def added_rows(d):
    """Рядки «пропуск Konst», додані в журнал цією сесією: від батька першого коміту з міткою сесії (або від HEAD) до робочої теки."""
    j = env('LENS_JOURNAL', os.path.join(HERE, 'HOOK_JOURNAL.md')); repo = os.path.dirname(j)
    s = sid(d); base = 'HEAD'
    if s and INJ != '3':
        log = git(repo, 'log', '--format=%H', f'--grep=Claude-Session: .*{s}', '--', j) or ''
        hs = log.split()
        if hs and git(repo, 'rev-parse', '-q', '--verify', hs[-1] + '^') is not None: base = hs[-1] + '^'
    diff = git(repo, 'diff', base, '--', j) or ''
    return [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++') and MISS.search(l)]

def journal_open():
    j = env('LENS_JOURNAL', os.path.join(HERE, 'HOOK_JOURNAL.md'))
    try: return [l for l in open(j, encoding='utf-8') if OPEN.search(l) and l.startswith('|')]
    except OSError: return []

def guard_says():
    t = tempfile.mkdtemp()
    e = dict(os.environ, LENS_FLAG=os.path.join(t, 'flag'), LENS_LOG=os.path.join(t, 'log'), LENS_HELD=os.path.join(t, 'held'), LENS_HOOKS=HERE)
    try:
        r = subprocess.run(['bash', env('LENS_PC_GUARD', os.path.join(HERE, 'precompact_guard.sh'))], input='{"trigger":"manual","custom_instructions":null}',
                           capture_output=True, text=True, env=e, timeout=float(env('PG_TIMEOUT', '45')))
    except subprocess.TimeoutExpired:   # не встиг — не «пропустив»: заява лишається неперевіреною
        return ("сторож не відповів за " + env('PG_TIMEOUT', '45') + " с — прожени сам: echo '{\"trigger\":\"manual\"}' | LENS_HOOKS=<ядро>/tools/claude-code/hooks "
                "bash <ядро>/tools/claude-code/hooks/precompact_guard.sh; echo $? — «можна /compact» лише після виходу 0 у цьому ході")
    return (r.stderr.strip() or 'вихід 2')[:1500] if r.returncode == 2 else None

def verdict(d):
    msg = d.get('last_assistant_message') or ''
    if CLAIM.search(msg) and INJ != '2':
        g = guard_says()
        if g: return ("Ворота «сказав — перевір» (Konst S146): у відповіді «можна /compact», а сторож стиснення на цьому стані зупинить. Його слова:\n" + g +
                      "\nВиправ ✗ (ревізія → коміт → push), тоді пиши «можна /compact». ✗ не пояснювати — виправляти.")
    rows = added_rows(d); bad = []; opened = []
    for r in rows:
        if OPEN.search(r): opened.append(r); continue
        hs = [h for h in HASH.findall(r) if exists(h)]
        if not hs or not TEETH.search(r): bad.append(r)
    if bad:
        return ("Ворота «записав ≠ зробив» (Konst S146): рядок «пропуск Konst» без виправлення — " + bad[0].strip()[:160] + "…\n"
                "Рядок закритий лише з хешем коміту виправлення в бектиках (`abc1234`, що є в git) і зубом (selftest · --inject · пункт чек-листа). "
                "Не встигаєш виправити в цьому ході — напиши в рядку «НЕ ЗРОБЛЕНО: чому · коли» і першими рядками звіту «не зроблено: …». Запис — не дія.")
    if opened and not SAID.search(msg[:1500]):
        return ("Ворота «записав ≠ зробив» (Konst S146): у журналі є відкритий рядок цієї сесії «НЕ ЗРОБЛЕНО» (" + opened[0].strip()[:120] +
                "…), а у звіті нема «не зроблено: …» на початку. Konst має бачити невиконане першим — допиши блок «не зроблено: що · чому · коли».")
    return None

def counter(d, blocked):
    f = os.path.join(env('LENS_MARK_DIR', '/tmp'), f"lens-promise-{sid(d) or 'x'}.n")
    try: n = int(open(f).read() or 0)
    except (OSError, ValueError): n = 0
    n = n + 1 if blocked else 0
    open(f, 'w').write(str(n)); return n

def stop(d):
    v = verdict(d)
    if v and counter(d, True) > 3:
        counter(d, False); print("⚠ обійдено: 3 зупинки поспіль — " + v[:120].replace('\n', ' '), file=sys.stderr); return None
    if not v: counter(d, False)
    return v

def open_ctx():
    o = journal_open()
    if not o: return None
    return ("Відкриті обіцянки «НЕ ЗРОБЛЕНО» в журналі гачків (" + str(len(o)) + "): спершу їх — виправлення з хешем і зубом, тоді рядок закрити; "
            "не встигаєш — у звіті першими рядками «не зроблено: …».\n" + "\n".join("· " + l.strip()[:220] for l in o[:5]))

def selftest():
    t = tempfile.mkdtemp(); root = os.path.join(t, 'w'); k = os.path.join(root, 'k'); os.makedirs(k)
    G = lambda *a: subprocess.run(['git', '-C', k, *a], capture_output=True, text=True, check=True).stdout.strip()
    G('init', '-q'); G('config', 'user.email', 't@t'); G('config', 'user.name', 't')
    j = os.path.join(k, 'HOOK_JOURNAL.md'); open(j, 'w').write('| дата | рядок |\n|---|---|\n| 01.01 | старий **пропуск Konst** без хешу |\n')
    G('add', '.'); G('commit', '-qm', 'base')
    open(os.path.join(k, 'fix.py'), 'w').write('x=1\n'); G('add', '.'); G('commit', '-qm', 'fix\n\nClaude-Session: https://x/session_TESTSID')
    fix = G('rev-parse', '--short', 'HEAD')
    ok_g = os.path.join(t, 'g0.sh'); open(ok_g, 'w').write('exit 0\n')
    no_g = os.path.join(t, 'g2.sh'); open(no_g, 'w').write('echo "Стиснення зупинено — не все збережено: k:незакомічене(1)" >&2; exit 2\n')
    os.environ.update(LENS_ROOT=root, LENS_JOURNAL=j, LENS_MARK_DIR=t, CLAUDE_CODE_REMOTE_SESSION_ID='cse_TESTSID')
    def row(text):
        open(j, 'w').write('| дата | рядок |\n|---|---|\n| 01.01 | старий **пропуск Konst** без хешу |\n' + text)
    D = lambda m: {'last_assistant_message': m, 'session_id': 'x'}
    cases = []
    def case(name, setup, msg, want, guard=ok_g):
        os.environ['LENS_PC_GUARD'] = guard; setup(); got = verdict(D(msg)) is not None
        cases.append((name, got == want))
    case('без заяви й без нових рядків → тиша', lambda: row(''), 'Готово, коміт.', False)
    case('«можна /compact», сторож пропускає → тиша', lambda: row(''), 'Від тебе: можна /compact', False)
    case('«можна /compact», сторож зупинив би → block', lambda: row(''), 'Від тебе: можна /compact', True, no_g)
    sl = os.path.join(t, 'gs.sh'); open(sl, 'w').write('sleep 5; exit 0\n'); os.environ['PG_TIMEOUT'] = '1'
    case('«можна /compact», сторож не встиг → block (не перевірено ≠ можна)', lambda: row(''), 'можна /compact', True, sl); os.environ.pop('PG_TIMEOUT')
    case('«не можна /compact», сторож зупинив би → тиша', lambda: row(''), 'Поки не можна /compact: ревізія.', False, no_g)
    case('старий рядок без хешу (до сесії) → тиша', lambda: row(''), 'ок', False)
    case('новий «пропуск Konst» без хешу → block', lambda: row('| 14.11 | **пропуск Konst** — рішення: зроблю потім |\n'), 'ок', True)
    case('новий з хешем, якого нема в git → block', lambda: row('| 14.11 | **пропуск Konst** — `deadbee` selftest |\n'), 'ок', True)
    case('новий з хешем, що є, без зуба → block', lambda: row(f'| 14.11 | **пропуск Konst** — виправлено `{fix}` |\n'), 'ок', True)
    case('новий з хешем, що є, і зубом → тиша', lambda: row(f'| 14.11 | **пропуск Konst** — виправлено `{fix}`, selftest 5/5 |\n'), 'ок', False)
    case('новий «НЕ ЗРОБЛЕНО», звіт мовчить → block', lambda: row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: чому · коли |\n'), 'Готово.', True)
    case('новий «НЕ ЗРОБЛЕНО», звіт каже «не зроблено» → тиша', lambda: row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: чому · коли |\n'), 'Що ти побачиш: …\nне зроблено: центр — наступний хід', False)
    case('«не зроблено» лише в кінці довгого звіту → block', lambda: row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: x |\n'), 'а' * 1600 + ' не зроблено', True)
    row('| 14.11 | **пропуск Konst** — зроблю потім |\n'); G('add', '.'); G('commit', '-qm', 'row\n\nClaude-Session: https://x/session_TESTSID')
    cases.append(('рядок без хешу вже ЗАКОМІЧЕНО цією сесією → block', verdict(D('ок')) is not None))
    G('reset', '-q', '--hard', 'HEAD~1')
    row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: x |\n')
    oc = open_ctx(); cases.append(('open: відкритий рядок → нагадування', bool(oc) and 'НЕ ЗРОБЛЕНО' in oc))
    row(f'| 14.11 | **пропуск Konst** — правило: або «НЕ ЗРОБЛЕНО» + звіт; виправлено `{fix}`, selftest |\n'); cases.append(('open: згадка «НЕ ЗРОБЛЕНО» в лапках — не обіцянка → тиша', open_ctx() is None and verdict(D('ок')) is None))
    row(''); cases.append(('open: відкритих нема → тиша', open_ctx() is None))
    row('| 14.11 | **пропуск Konst** — без хешу |\n'); n = [stop(D('ок')) is not None for _ in range(5)]
    cases.append(('стеля: 3 зупинки поспіль, 4-та пропускає, далі знову суд', n == [True, True, True, False, True]))
    bad = 0
    for name, ok in cases:
        bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    print(f'─── promise-guard selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

m = sys.argv[1]
if m == 'selftest': sys.exit(selftest())
try:
    d = json.loads(os.environ.get('HOOK_IN') or '{}')
    if m == 'open':
        o = open_ctx()
        if o: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': o}}, ensure_ascii=False))
    else:
        v = stop(d)
        if v: print(json.dumps({'decision': 'block', 'reason': v}, ensure_ascii=False))
except Exception:
    __import__('traceback').print_exc()
PY
