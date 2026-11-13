#!/bin/bash
# живе доки: сесії переїжджають у нові чати, а пам'ять — лише репо (профіль Konst «САМЕРІ»).
# Дім — lens-governance:tools/claude-code/hooks/ (HOOK-3.2, бриф — archive/summaries/Lens_gov/Lens_kernel_BRIEF_HOOK-3.2_closed.md; «так» Konst 09.10.2026).
# Подія UserPromptSubmit: у повідомленні Konst — команда переїзду («переїжджаємо» · «переїжджай…» · «переїхати» · «переїдемо» · «нова / нову сесію» · «стартове повідомлення»; іменник «переїзд» — ні, це розповідь) →
# tools/claude-code/handoff_check.py на кожне репо сесії (/home/user/*, де є sessions/ чи docs/summary; без .git/lens-readonly) → additionalContext: рядки ✓/⚠/✗ + чек-лист
# «очима нового агента». Повідомлення Konst не блокує. Тиша: перше повідомлення сесії (стартове саме містить «переїзд» — переїжджати
# ще нема з чого) · повтор без нових комітів (позначка /tmp/lens-handoff-<session_id> = HEAD усіх репо) · помилка розбору.
# Формат — code.claude.com/docs/en/hooks «UserPromptSubmit» (поле prompt; additionalContext ≤ 10 000 знаків), 09.10.2026.
# + HOOK-3.3 (Stop, пропуск Konst AE S136): відповідь-переїзд із «💡 Пропоную», а ні стартове в ній, ні §0 найновішого самері не мають рядка «💡 …» з її суттю → block
#   («💡 чекає вироку Konst: …» — правило AE CLAUDE.md «Самері», Konst S135; щоб Konst не повертався в закриту сесію сказати «запиши»).
# + Stop (bash handoff-remind.sh stop): переїзд оголошує АГЕНТ (стартове ```text чи «переїжджаємо» у відповіді) і є ✗ → decision: block (раз на стан HEAD; stop_hook_active → тиша).
# Клон лише для читання (звірка іншого продукту) — `touch <репо>/.git/lens-readonly`: гачок його не перевіряє (AE S103).
# + РЕВІЗІЯ (AE S109, слово Konst: «одним словом — щоб кожного разу не пояснювати»): «ревізія» · «звір пам'ять» · «звірка пам'яті» у повідомленні Konst →
#   той самий handoff_check + чек-лист «що з сесії ще не має дому» (рішення → DECISIONS · прилади → карта репо · правила → CLAUDE.md · брифи §0) — без переїзду.
# + post (bash handoff-remind.sh post, PostToolUse Bash після `git commit`): той самий handoff_check щокоміту; у контекст — лише НОВІ ✗ / ⚠ (бачені — тиша, /tmp/lens-handoff-post-<сесія>).
#   Проти шуму (досвід AE S109, гачок у перевірці): новизна — за змістом без чисел і хешів; «описи…» — по документу; «незакомічене» — лише на переїзді; «самері відстає» — від POST_LAG комітів.
# Зуби: bash handoff-remind.sh selftest — лічбу друкує сам прогін (тригер → контекст з ✗; не тригер · «в новій сесії» в розповіді · перше повідомлення · повтор → тиша;
# новий коміт → знову; Stop: стартове з ✗ → block, звичайна відповідь і повтор → тиша).
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN HC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/handoff_check.py"
python3 - "$mode" <<'PY'
import json, os, re, subprocess, sys, tempfile, glob, time
STOP_TRIG = re.compile(r"переїжджаємо|переїжджай\w*", re.I)   # Stop: лише оголошення агента, не згадка слова
REV = re.compile(r"\bревізі[яюї]\b|\bзвір\w*\s+пам.?ят\w*|\bзвірк\w+\s+пам.?ят\w*", re.I)   # ревізія пам'яті без переїзду (AE S109)
TRIG = re.compile(r"переїжджаємо|переїжджай\w*|переїхати|переїдемо|стартов\w+\s+повідомлен\w*|\bнов[ау]\s+сесі[яю]\b", re.I)   # лише команди: «переїжджаємо / переїхати / стартове / нову сесію»; іменник «переїзд» — розповідь (тричі хибне 10.10), «переїжджає» — опис (G6 «переїжджає в скрипт», хибне 10.10 QR CC-7) — журнал гачків §1
STARTER = re.compile(r'(?im)^\s*старт\w*\s*:')   # ознака стартового в блоці text — рядок «СТАРТ:» / «Старт:» (є в стартових AE і ядра). AE S139: промпт моделі давав хибний переїзд; AE S140: текст завдання для Fable («гачок старту», «самері … §0») — теж (хибне), тому вже не «старт|самері» будь-де
HC = os.environ['HC']
NARR = re.compile(r'(?:\bдо|\bпісля|\bбез|\bперед|\bвід|\bщодо|\bпро)\s+$', re.I)   # «стиснення до ревізії» — розповідь, не команда (хибне AE S143: повний прохід на слово в розповіді)
def is_rev(pr):
    return any(not NARR.search(pr[max(0, m.start() - 12):m.start()]) for m in REV.finditer(pr))

def repos(roots):
    out = []
    for root in roots:
        for d in sorted(glob.glob(os.path.join(root, '*', '.git'))):
            r = os.path.dirname(d)
            # клон лише для читання (позначка .git/lens-readonly) — не репо сесії: хибне ×2 AE S103 — вади QR і Routes, склонованих для звірки, блокували Stop
            if os.path.exists(os.path.join(r, '.git', 'lens-readonly')): continue
            if any(os.path.isdir(os.path.join(r, s)) for s in ('sessions', 'docs/summary')): out.append(r)   # Lens · не-Lens каркас (S90 AE)
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
    pr = d.get('prompt') or ''; rev = is_rev(pr) and not TRIG.search(pr)
    if not (TRIG.search(pr) or rev): return None
    if first_prompt(d.get('transcript_path') or ''): return None
    rs = repos(roots)
    if not rs: return None
    mark = os.path.join(mark_dir, 'lens-handoff-' + re.sub(r'\W', '', d.get('session_id') or 'x'))
    h = heads(rs)
    if os.path.exists(mark) and open(mark).read() == h: return None
    open(mark, 'w').write(h)
    if rev:   # REV-1 (AE S143): та сама точка ревізії, що й поріг ctx_watch і сам агент — handoff_check revision (вивід + чек-лист + мітка для precompact_guard)
        r = subprocess.run([sys.executable, HC, 'revision', *roots[:1]], capture_output=True, text=True)
        return "Гачок «ревізія пам'яті» (AE S109 · REV-1) — handoff_check revision:\n" + r.stdout.strip()[-8000:]
    r = subprocess.run([sys.executable, HC, *rs], capture_output=True, text=True)
    return ("Гачок «перевірка пам'яті перед переїздом» (HOOK-3.2) — handoff_check:\n" + r.stdout.strip()[:6000] +
            "\n\nДо стартового повідомлення: ✗ — виправ, закоміть і запуш; ⚠ — звір. Потім прочитай §0 і стартове ОЧИМА НОВОГО АГЕНТА: "
            "(а) з першого екрана ясно, що робимо далі й у якому порядку? (б) нема історії замість «як є»? "
            "(в) кожне правило сесії — у своєму домі, а не лише в самері? (г) план має «зараз і далі» зверху? "
            "(д) що новий агент мусить знати, а воно є лише в чаті (рішення, побажання й побоювання Konst — як побажання, не як догма)? "
            "Знахідки — виправ, закоміть і запуш, тоді стартове в чат. Якщо Konst не переїжджає (слово випадкове) — проігноруй цей контекст.")

def selftest():
    t = tempfile.mkdtemp(prefix='hr-'); os.environ['LENS_REV_MARK'] = os.path.join(t, 'revmark')   # REV-1: тест не ставить справжню мітку «ревізію зроблено»
    r = os.path.join(t, 'Prod')
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
    import builtins; bad = 0; _p = builtins.print; N = [0]
    def print(*a, **k):   # лічба перевірок — прогоном, не числом у коді (аудит S134: було «14/14» при 15 перевірках)
        if a and isinstance(a[0], str) and a[0][:1] in '✓✗': N[0] += 1
        _p(*a, **k)
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
    # REV-2 (AE S143): ревізія при переїзді — машиною. Свої коміти — за трейлером тестової сесії T
    os.environ['CLAUDE_CODE_REMOTE_SESSION_ID'] = 'cse_T'; rm = os.environ['LENS_REV_MARK']
    open(os.path.join(r, 'tool.py'), 'w').write('x'); sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'прилад\n\nClaude-Session: https://claude.ai/code/session_T')
    hh = subprocess.run(['git', '-C', r, 'log', '-1', '--format=%h', '--abbrev=7'], capture_output=True, text=True).stdout.strip()
    TB = '| що | дім | коміт |\n|---|---|---|\n| прилад | tool.py | ' + hh + ' |\n'
    MV = 'Переїжджаємо. ```text\nСтарт: …\n```\n'
    if os.path.exists(rm): os.remove(rm)
    o = stop(S(MV + TB, s='v1'), [t], t); ok = o is not None and 'REV-2' in o and 'ревізії після останнього коміту не було' in o
    print(('✓' if ok else '✗') + ' Stop REV-2: стартове без мітки ревізії → block'); bad += not ok
    open(rm, 'w').close(); os.utime(rm, (time.time() - 99999, time.time() - 99999))
    o = stop(S(MV + TB, s='v2'), [t], t); ok = o is not None and 'ревізії після останнього коміту' in o
    print(('✓' if ok else '✗') + ' Stop REV-2: мітка старша за останній коміт → block'); bad += not ok
    open(rm, 'w').close()
    o = stop(S(MV, s='v3'), [t], t); ok = o is not None and 'таблиці ревізії' in o and hh in o
    print(('✓' if ok else '✗') + ' Stop REV-2: свіжа мітка, без таблиці й без коміту сесії → block з обома'); bad += not ok
    o = stop(S(MV + TB, s='v4'), [t], t); ok = o is None or 'REV-2' not in o
    print(('✓' if ok else '✗') + ' Stop REV-2: свіжа мітка + таблиця + кожен коміт сесії → пропускає'); bad += not ok
    for name, d, want in [('Stop: агент дає стартове, є ✗ → block', S(MV + TB), True),
                          ('Stop: звичайна відповідь → тиша', S('Готово, коміт abc.', s='p2'), False),
                          ('Stop: «переїжджає» в описі (межа G6 переїжджає в скрипт) → тиша', S('Стара межа G6 переїжджає в новий скрипт.', s='p4'), False),
                          ('Stop: повтор через гачок (stop_hook_active) → тиша', S('```text\nx\n```', True, 'p3'), False),
                          ('Stop: блок text — промпт моделі, не стартове → тиша (хибне AE S139)', S('Чернетка промпту:\n```text\nYou are an auditor. Read files.\n```', s='p6'), False),
                          ('Stop: блок text — завдання іншій сесії («гачок старту», «самері … §0»), не стартове → тиша (хибне AE S140)', S('Текст для Fable:\n```text\nПрофіль — з репо ядра (гачок старту).\nЗАВДАННЯ: docs/fab/FAB2_TASK.md.\nКонтекст: самері docs/summary/X.md §0.\n```', s='p7'), False),
                          ('Stop: «стартове повідомлення» в реченні, без блоку — не переїзд → тиша (хибне AE S93)', S('Стартове повідомлення оновлю в самері.', s='p5'), False)]:
        out = stop(d, [t], t); ok = (out is not None and 'HOOK-3.2' in out) == want
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    # HOOK-3.3: 💡 на переїзді (пропуск Konst AE S136) — самері тестового репо без рядка 💡
    IDEA = 'Переїжджаємо. ```text\nСтарт\n💡 чекає вироку Konst: нема\n```\n💡 **Пропоную:** зробити одну сторінку-мапу продукту простими словами з перевіреної карти.'
    for name, d, want in [('Stop HOOK-3.3: переїзд + 💡, у стартовому «нема» → block', S(IDEA, s='i1'), True),
                          ('Stop HOOK-3.3: 💡 записана в стартовому → тиша', S(IDEA.replace('нема', 'сторінку-мапу продукту простими словами'), s='i2'), False),
                          ('Stop HOOK-3.3: «💡 Пропоную: ідей нема» → тиша', S('Переїжджаємо. ```text\nx\n```\n💡 Пропоную: ідей нема.', s='i3'), False),
                          ('Stop HOOK-3.3: 💡 + блок text з промптом (не стартове) → тиша (хибне AE S139)', S('Промпт:\n```text\nYou are an auditor.\n```\n💡 **Пропоную:** зробити одну сторінку-мапу продукту простими словами.', s='i5'), False),
                          ('Stop HOOK-3.3: 💡 без переїзду → тиша', S('Готово. 💡 Пропоную: зробити одну сторінку-мапу продукту простими словами.', s='i4'), False)]:
        out = stop(d, [t], t); ok = (out is not None and 'HOOK-3.3' in out) == want
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    open(os.path.join(r, '.git', 'lens-readonly'), 'w').close()
    ok = stop(S('Переїжджаємо. ```text\nСтарт: …\n```', s='p4'), [t], t) is None
    print(('✓' if ok else '✗') + ' Stop: клон лише для читання (.git/lens-readonly) → тиша (хибне AE S103)'); bad += not ok
    os.remove(os.path.join(r, '.git', 'lens-readonly'))   # далі — звичайне репо сесії
    ok = (lambda o: o is not None and 'ревізія' in o)(run(D('зроби ревізію? ні — просто ревізія пам\'яті, будь ласка', mid, 'r1'), [t], t))
    print(('✓' if ok else '✗') + ' «ревізія пам\'яті» → контекст ревізії (без переїзду)'); bad += not ok
    ok = run(D('навмисно спробувати стиснення до ревізії; після ревізії — далі; без ревізії не можна', mid, 'r2'), [t], t) is None and is_rev('Далі — ревізія') and is_rev('зроби ревізію перед стисненням')
    print(('✓' if ok else '✗') + ' «до / після / без ревізії» у розповіді → тиша; «ревізія», «зроби ревізію» → так (хибне AE S143)'); bad += not ok
    P = lambda c, s='q1': {'tool_input': {'command': c}, 'session_id': s}
    o1 = post(P('cd x && git commit -qm x'), [t], t); o2 = post(P('git commit -qm y'), [t], t); o3 = post(P('git status'), [t], t); o4 = post(P("echo '{\"command\":\"git commit -m x\"}' | bash h.sh", 'q2'), [t], t)
    ok = o1 is not None and '✗' in o1 and o2 is None and o3 is None and o4 is None
    print(('✓' if ok else '✗') + ' post: коміт → нові ✗; повтор того самого → тиша; не коміт і «git commit» у тексті echo → тиша'); bad += not ok
    mk = os.path.join(t, 'pf'); F = lambda ls: post_filter(ls, mk)[0]
    r1 = F(['⚠ бриф a.md відстає: 1 коміт(ів)', '✗ незакомічене: 2 (x)', '✗ самері відстає: після abc1234 комітів агента без самері — 1 (abc1234)', '⚠ описи, що згадують змінений у сесії код, але не мінялись: README.md (g.sh)'])
    r2 = F(['⚠ бриф a.md відстає: 2 коміт(ів)', '✗ самері відстає: після abc1234 комітів агента без самері — 3 (abc1234 def5678 0a1b2c3)', '⚠ описи, що згадують змінений у сесії код, але не мінялись: README.md (g.sh) · docs/B.md (h.py)'])
    ok = (len(r1) == 2 and not any('незакомічене' in x or 'самері' in x for x in r1)
          and len(r2) == 2 and any('самері' in x for x in r2) and any('docs/B.md' in x and 'README' not in x for x in r2) and not any('бриф a.md' in x for x in r2))
    print(('✓' if ok else '✗') + ' post: шум — те саме з іншим числом · незакомічене · самері < 3 → тиша; новий документ в «описах» і самері ≥ 3 → є'); bad += not ok
    _p(f'selftest: {N[0] - bad}/{N[0]}'); return 1 if bad else 0

POST_LAG = 3   # «самері відстає» після коміту — лише від стількох комітів (на кожен однорядковий коміт — шум; переїзд ловить усе)
def post_filter(lines, mark):
    """Шум гачка після коміту (досвід AE S109): новизна — за змістом без чисел і хешів; «описи…» — по документу; без «незакомічене»; самері — з порогом."""
    norm = lambda l: re.sub(r'\b[0-9a-f]{7,40}\b', '@', re.sub(r'\d+([.,]\d+)?', '#', l))
    seen = set(open(mark, encoding='utf-8').read().splitlines()) if os.path.exists(mark) else set()
    new, keys = [], set()
    for l in lines:
        if 'незакомічене' in l: continue   # посеред роботи це норма; перевіряє переїзд
        m = re.search(r'самері відстає.*?—\s*(\d+)', l)
        if m and int(m.group(1)) < POST_LAG: continue
        docs = re.findall(r'([\w./-]+\.md) \(([^)]*)\)', l) if 'описи' in l else []
        if docs:
            fresh = [(f, w) for f, w in docs if 'опис:' + f not in seen]; keys |= {'опис:' + f for f, _ in docs}
            if fresh: new.append(l.split(':', 1)[0] + ': ' + ' · '.join(f'{f} ({w})' for f, w in fresh))
            continue
        k = norm(l); keys.add(k)
        if k not in seen: new.append(l)
    open(mark, 'w', encoding='utf-8').write('\n'.join(sorted(seen | keys)))
    return new, keys

def post(d, roots, mark_dir='/tmp'):
    """PostToolUse Bash: щойно був `git commit` → handoff_check; у контекст лише нові ✗ / ⚠ (бачені в цій сесії — тиша)."""
    cmd = ((d.get('tool_input') or {}).get('command') or '')
    if not re.search(r'(?:^|[;&|(]\s*)git(?:\s+-C\s+\S+)?\s+commit\b', cmd) or '--dry-run' in cmd: return None   # git commit на місці команди (echo «…git commit…» — не коміт, хибне S109)
    rs = repos(roots)
    if not rs: return None
    r = subprocess.run([sys.executable, HC, *rs], capture_output=True, text=True)
    new, keys = post_filter([l.strip() for l in r.stdout.splitlines() if l.strip().startswith(('✗', '⚠'))],
                            os.path.join(mark_dir, 'lens-handoff-post-' + re.sub(r'\W', '', d.get('session_id') or 'x')))
    if not new: return None
    return ("Гачок «пам'ять після коміту» (AE S109) — handoff_check знайшов нове:\n" + '\n'.join(new)[:4000] +
            "\n✗ — виправ наступним комітом; ⚠ — звір: опис не відстає від коду? рішення / прилад / правило мають дім?")

PROP = re.compile(r'💡\s*\**\s*Пропоную\s*\**\s*:?\s*\**\s*(.+)', re.S)
WORD = re.compile(r'[А-Яа-яЇїІіЄєҐґA-Za-z]{6,}')
def latest_summary(r):
    """Найновіше живе самері репо: не-Lens — docs/summary/*SUMMARY*.md, Lens — sessions/**/*summary*.md (за часом зміни)."""
    xs = glob.glob(os.path.join(r, 'docs', 'summary', '*SUMMARY*.md')) + glob.glob(os.path.join(r, 'sessions', '**', '*summary*.md'), recursive=True)
    return max(xs, key=os.path.getmtime) if xs else None
def idea_missing(msg, rs):
    """HOOK-3.3 (пропуск Konst AE S136): відповідь-переїзд із «💡 Пропоную», а ні стартове в ній, ні §0 найновішого самері не мають рядка «💡 …» з її суттю
    (≥ 2 спільних слів від 6 літер з першого речення 💡) → суть 💡, інакше None. Правило — AE CLAUDE.md «Самері», «💡 на переїзді» (Konst S135)."""
    m = PROP.search(msg)
    if not m: return None
    idea = m.group(1).strip()
    if re.match(r'(ідей|нових)\s+нема', idea, re.I): return None   # чесне «ідей нема» — не 💡
    first = re.split(r'(?<=[.!?])\s', idea, 1)[0][:400]
    words = {w.lower() for w in WORD.findall(first)}
    if len(words) < 2: return None
    texts = [b for b in re.findall(r'```text(.*?)```', msg, re.S)]
    for r in rs:
        f = latest_summary(r)
        if f:
            t = open(f, encoding='utf-8').read(); i = t.find('§0'); texts.append(t[i:i + 12000] if i >= 0 else t[:12000])
            j = t.find('```text'); texts.append(t[j:j + 8000] if j >= 0 else '')
    for t in texts:
        for line in t.splitlines():
            if '💡' in line and len(words & {w.lower() for w in WORD.findall(line)}) >= 2: return None
    return first[:200]

TABLE = re.compile(r'\|\s*що\s*\|\s*дім\s*\|\s*коміт\s*\|', re.I)   # заголовок таблиці ревізії «що · дім · коміт»
def rev_mark():
    sid = re.sub(r'\W', '', os.environ.get('CLAUDE_CODE_SESSION_ID') or os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID') or 'x')
    return os.environ.get('LENS_REV_MARK') or f'/tmp/lens-revision-{sid}'   # та сама мітка, що handoff_check.py rev_mark()
def session_commits(r):
    """Коміти цієї сесії (трейлер Claude-Session ≡ CLAUDE_CODE_REMOTE_SESSION_ID), крім тих, що правили самері: вони записані самим комітом."""
    sid = os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID', ''); tail = sid.split('_', 1)[1] if '_' in sid else ''
    if not tail: return []
    out = subprocess.run(['git', '-C', r, 'log', '--format=%h', '--abbrev=7', f'--grep=session_{tail}'], capture_output=True, text=True).stdout.split()
    keep = []
    for h in out:
        fs = subprocess.run(['git', '-C', r, 'show', '--name-only', '--format=', h], capture_output=True, text=True).stdout.split()
        if any(re.search(r'(^docs/summary/|^sessions/.*summary)', f, re.I) for f in fs): continue   # коміт правив самері — записаний ним самим (свій хеш у самері вписати не може)
        keep.append(h)
    return keep
def rev_gap(msg, rs):
    """REV-2 (Konst AE S143: «ревізія при переїзді — машиною, щоб моя ревізія = твоя»): відповідь-переїзд пропускається, лише коли
    (а) мітка ревізії (handoff_check.py revision) свіжіша за останній коміт репо сесії; (б) у відповіді є таблиця «що · дім · коміт»;
    (в) кожен коміт сесії (крім тих, що правили самері) згаданий у відповіді або в самері репо. Звірка з фактами git, не з заявою агента
    (практика: Stop-гачок, що перевіряє стан, а не слова — codingwithroby «The Stop Hook That Won't Let Claude Lie to You», 13.11.2026)."""
    gaps = []
    m = rev_mark(); last = max((int(subprocess.run(['git', '-C', r, 'log', '-1', '--format=%ct'], capture_output=True, text=True).stdout.strip() or 0) for r in rs), default=0)
    if not os.path.exists(m) or os.path.getmtime(m) < last:
        gaps.append('ревізії після останнього коміту не було → python3 lens-governance/tools/claude-code/handoff_check.py revision (✗ — виправ, коміт, push, ще раз)')
    if not TABLE.search(msg):
        gaps.append('у відповіді нема таблиці ревізії «| що | дім | коміт |» — кожне рішення · прилад · правило сесії з домом і комітом')
    mem = msg + ''.join(open(f, encoding='utf-8').read() for f in filter(None, (latest_summary(r) for r in rs)))
    miss = [f'{os.path.basename(r)} {h}' for r in rs for h in session_commits(r) if h not in mem]
    if miss:
        gaps.append(f'коміти сесії без запису ні в таблиці, ні в самері — {len(miss)}: ' + ' · '.join(miss[:10]) + (' …' if len(miss) > 10 else '')
                    + ' → кожен у таблицю (що · дім) або рядком §1 самері')
    return gaps

def stop(d, roots, mark_dir='/tmp'):
    """Stop: переїзд оголошує агент (стартове чи «переїжджаємо» у відповіді) — є ✗ → block, щоб виправив до кінця ходу."""
    if d.get('stop_hook_active'): return None
    msg = d.get('last_assistant_message') or ''
    if not (STOP_TRIG.search(msg) or any(STARTER.search(b) for b in re.findall(r'```text(.*?)```', msg, re.S))): return None   # AE S139: блок text — стартове, лише коли в ньому «старт» / «самері» (промпт моделі в блоці text — не переїзд)   # AE S93 → S129: «стартове повідомлення» в реченні агента — не переїзд (хибне); переїзд — блок стартового чи «переїжджаємо»
    rs = repos(roots)
    if not rs: return None
    gap = idea_missing(msg, rs)   # HOOK-3.3: 💡 з відповіді-переїзду не записана — блок щоразу (stop_hook_active рятує від кола)
    if gap: return ("Гачок «💡 на переїзді» (HOOK-3.3, Stop): ти оголошуєш переїзд і даєш «💡 Пропоную: " + gap + "…», а ні стартове, ні §0 самері не мають рядка «💡 …» з нею.\n"
                    "Запиши в самері §0 і в стартове рядок «💡 чекає вироку Konst: <суть> — не як прийняту» (AE CLAUDE.md «Самері», Konst S135), закоміть і запуш, тоді стартове. "
                    "Konst не мусить повертатись у закриту сесію, щоб сказати «запиши».")
    rg = rev_gap(msg, rs)   # REV-2: ревізія при переїзді — машиною (блок щоразу; stop_hook_active рятує від кола)
    if rg: return ("Гачок «ревізія при переїзді» (REV-2, Stop): ти даєш стартове, а ревізія не доведена —\n· " + '\n· '.join(rg) +
                   "\nЗроби ревізію з виводу handoff_check (не з пам'яті), закоміть, запуш і дай у відповіді таблицю «що · дім · коміт», тоді стартове. "
                   "Якщо це не переїзд — одним рядком скажи це й заверши.")
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
if mode == 'post':
    try: out = post(json.loads(os.environ.get('HOOK_IN') or '{}'), ['/home/user'])
    except Exception: __import__('traceback').print_exc(); out = None
    if out: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': out}}, ensure_ascii=False))
    sys.exit(0)
if mode == 'stop':
    try: out = stop(json.loads(os.environ.get('HOOK_IN') or '{}'), ['/home/user'])
    except Exception: __import__('traceback').print_exc(); out = None
    if out: print(json.dumps({'decision': 'block', 'reason': out}, ensure_ascii=False))
    sys.exit(0)
try:
    d = json.loads(os.environ.get('HOOK_IN') or '{}')
    roots = ['/home/user']
    out = run(d, roots)
except Exception:
    __import__('traceback').print_exc(); out = None
if out:
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': out}}, ensure_ascii=False))
PY
