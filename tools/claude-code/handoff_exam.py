#!/usr/bin/env python3
# живе доки: ревізія має іспит нового агента (REV-5 Л2, «так» Konst 18.11.2026, AE S155). Бриф — `kernel/Lens_REV-5_brief.md`.
# Іспит нового агента: інша модель БЕЗ пам'яті сесії читає лише записане (стартове → самері §0 → черга → що вони називають) і відповідає на
#   питання `tools/claude-code/handoff_exam_questions.md`. Записане перевіряє той, хто його не писав: машина (`handoff_check`) судить наявне,
#   а розбіжності й застарілі рядки бачить лише читач (S155: машина «✗ 0», іспит haiku — ще 5 дір). Відповіді й мітка з HEAD — у /tmp; печатку
#   ревізії (`handoff_check.py revision`) робить ЧЕСНОЮ: «іспит ✓ · незрозуміло 0» / «іспит · незрозуміло K» / «іспит не робився».
# Світ: I-PASS — приймальник переказує сам (UCSF, 2012; 18.11.2026); «Handoff Debt» — ціну передачі міряє наступник (arXiv 2606.02875, 06.2026).
#   `claude -p`: --allowedTools лише схвалює, НЕ обмежує — тому ще --permission-mode dontAsk (решту відхиляє) і --disallowedTools;
#   --max-budget-usd — стеля (оцінка клієнта, може перейти — запас); total_cost_usd у JSON (code.claude.com/docs/en/headless · best-practices, 18.11.2026).
# Запуск:  python3 tools/claude-code/handoff_exam.py run [<корінь з репо>] [--model haiku] [--effort medium]   → відповіді + рядок «іспит … · модель · effort», мітка /tmp/lens-exam-<сесія>.md
#          python3 tools/claude-code/handoff_exam.py state [<корінь>]                         → рядок стану мітки (на HEAD? незрозуміло K)
#          python3 tools/claude-code/handoff_exam.py selftest                                 → зуби на підставній моделі (LENS_EXAM_CMD), без витрат
# Вихід:   run — 0, якщо відповіді повні (6 блоків); 1 — модель не відповіла чи формат зламано. Оцінку «правда з репо» робить агент таблицею.
# Інша модель (профіль «ІНША МОДЕЛЬ»): перед run агент називає в чаті модель · effort · навіщо. Інструменти моделі — лише Read · Grep · Glob.
# Вирок (💡 S36 п.7-б, «так з підсиленням» Konst EquipLens S40 21.11.2026): haiku дає 6–7 пунктів «незрозуміло», справжніх 2–3, решта —
#   рядки історії, прочитані як стан → «незрозуміло 0» недосяжне, печатка втрачала сенс. Тепер агент судить КОЖЕН пункт блоку 6:
#     python3 tools/claude-code/handoff_exam.py verdict <файл> [<корінь>]   рядки «N ✓|✗|? <шлях:рядок> <чому>» (порядок пунктів блоку 6)
#   ✓ справжній · ? не певен — рахується як справжній · ✗ не справжній — лише з доказом: `шлях:рядок` існує (від кореня сесії чи репо), «чому» ≥ 10 знаків;
#   бракує пункту — вирок не прийнято (практика сортування знахідок: справжнє · хибне · не певен, хибне — з доказом контексту, людина звіряє —
#   sei.cmu.edu «Evaluating static analysis alerts with LLMs» · arxiv 2510.02534 ZeroFalse, 21.11.2026).
#   Печатка: «справжніх 0 з K» = ✓ (K видно — скільки відкинуто, Konst може звірити); «справжніх R з K» — ні; вирок не дано — як було, «незрозуміло K».
#   Справжні виправляються → новий HEAD → новий іспит: вирок живе лише на HEAD своєї мітки.
# Журнал після іспиту (💡 EquipLens S46, «так» Konst 26.11.2026 — делегував): запис результату іспиту рядком §1 самері старив печатку, і кожна
#   ревізія кінчалась зайвим іспитом або «⚠». Тепер іспит живий, якщо від HEAD мітки до HEAD кожного репо — лише ДОДАНІ рядки таблиці §1
#   найновішого самері (≤ JOURNAL_MAX, без видалень, інших файлів і §0 · §6; HEAD мітки — предок). Не «ігнор шляху»: path-filter дає
#   «зелену заглушку, що нічого не тестує» (mergify.com «path filters are not a CI gate»; docs.github.com troubleshooting required status
#   checks, 26.11.2026) — тут перевірка щоразу розбирає diff і печатка каже «після іспиту — лише рядки §1 (N)». Зуб: EXAM_INJECT=journal.
# Effort — завжди явно (S40 21.11.2026: без --effort рівень обирав CLI, і його не видно ні в init stream-json, ні в --debug-file — Konst не знав,
#   на чому йшли 4 іспити). Обирає агент, не питаючи («так» Konst 21.11.2026): medium — типово (новий агент сесії працює на medium,
#   профіль EFFORT — іспит міряє саме його); high — щоб розвести «діра у файлах» ⟂ «слабке читання», коли пункт «незрозумілого»
#   спірний чи повторився після виправлення. Рівень — у рядку «іспит …» і в мітці.
import json, os, re, shlex, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
QFILE = os.path.join(HERE, 'handoff_exam_questions.md')
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')   # claude --help, 2.1.330, 21.11.2026
BUDGET = '1.00'   # $ на один іспит — стеля; haiku на AE ≈ заміряно в брифі REV-5 §5 крок 4
sys.path.insert(0, HERE)
import handoff_check as hc   # одна правда: репо сесії, HEAD, стартове, самері

def questions(path=QFILE):
    t = open(path, encoding='utf-8').read()
    return [(m.group(1), m.group(2).strip()) for m in re.finditer(r'(?ms)^## (\d+)\n(.*?)(?=^## \d+\n|\Z)', t)]

def mark_path(): return os.environ.get('LENS_EXAM_MARK') or f'/tmp/lens-exam-{hc.sid()}.md'

def heads_short(rs): return ' '.join(f'{os.path.basename(r)}@{hc.git(r, "rev-parse", "--short=7", "HEAD")}' for r in rs)

def subject(rs):
    """Репо, з якого новий агент стартує: продукт (не ядро) з живим самері; лише ядро — ядро."""
    prod = [r for r in rs if not os.path.isdir(os.path.join(r, 'kernel')) and hc.latest_summary(r)]
    return (prod or [r for r in rs if hc.latest_summary(r)] or [None])[0]

def prompt(root, repo, rs, qs):
    sm = hc.latest_summary(repo); st = hc.starter(open(sm, encoding='utf-8').read()) or '(стартового нема)'
    q = '\n\n'.join(f'## {n}\n{t}' for n, t in qs)
    return (f"Ти — новий агент. Пам'яті попередньої сесії в тебе НЕМА: є лише репо в теці {root} (теки: {', '.join(os.path.basename(r) for r in rs)}).\n"
            f"Тобі щойно дали це стартове повідомлення:\n\n<<<\n{st.strip()}\n>>>\n\n"
            "Прочитай те, на що воно посилає (самері §0, черга, брифи, журнал рішень — Read · Grep · Glob, абсолютні шляхи), і відповідай на питання нижче. "
            "Відповідай лише з файлів; на кожне твердження — `файл:рядок`. Не вгадуй: не знайшов — так і пиши. Шукай і суперечності між файлами.\n"
            "Формат відповіді — суворо блоки «## 1» … «## 6», у тому ж порядку, без вступу.\n\n" + q)

EXAMINEE = ("Ти — екзаменований новий агент, не працівник сесії: нічого не правиш, не комітиш, не пишеш звіт, маркер чи рядок «пам'ять». "
            "Уся відповідь — ОДНИМ останнім повідомленням: блоки «## 1» … «## 6» цілком.")

def exam_argv(model, effort):
    return ['claude', '-p', '--model', model, '--effort', effort, '--output-format', 'stream-json', '--verbose', '--max-turns', '40',
            '--max-budget-usd', BUDGET, '--setting-sources', 'local', '--disable-slash-commands', '--no-session-persistence',
            '--append-system-prompt', EXAMINEE, '--permission-mode', 'dontAsk', '--allowedTools', 'Read', 'Grep', 'Glob',
            '--disallowedTools', 'Bash', 'Edit', 'Write', 'NotebookEdit', 'WebFetch', 'WebSearch', 'Agent', 'Task']

def run_model(root, text, model, effort='medium'):
    """claude -p у stream-json: усі повідомлення моделі (не лише останнє — прогін на зуби 18.11: `result` дав лише приписку після відповіді).
    --setting-sources local — без гачків користувача (профіль середовища робив з екзаменованого працівника: «Пам'ять: нового нема»)."""
    cmd = os.environ.get('LENS_EXAM_CMD')
    argv = shlex.split(cmd) if cmd else exam_argv(model, effort)
    p = subprocess.run(argv, input=text, capture_output=True, text=True, cwd=root, timeout=900)
    texts, meta = [], {}
    for ln in p.stdout.splitlines():
        try: e = json.loads(ln)
        except ValueError: continue
        if e.get('type') == 'assistant':
            texts += [c.get('text', '') for c in (e.get('message') or {}).get('content', []) if isinstance(c, dict) and c.get('type') == 'text']
        elif e.get('type') == 'result':
            meta = {k: e.get(k) for k in ('total_cost_usd', 'num_turns', 'duration_ms', 'is_error', 'subtype') if k in e}
            if e.get('result'): texts.append(e['result'])
    if not texts: return '', {'error': (p.stderr or p.stdout)[-400:]}
    full = [x for x in texts if re.search(r'(?m)^## 1\b', x) and re.search(r'(?m)^## 6\b', x)]
    return (full[-1] if full else '\n\n'.join(texts)).strip(), meta

def unclear(ans):
    """Пункти блоку 6: None — блоку нема (відповідь неповна); 0 — «—»."""
    m = re.search(r'(?ms)^## 6\b[^\n]*\n(.*?)(?=^## \d+\b|\Z)', ans)
    if not m: return None
    return len([l for l in m.group(1).splitlines() if re.match(r'\s*[-*•]\s+\S', l) and not re.match(r'\s*[-*•]\s+—\s*$', l)
                and not re.match(r'\s*[-*•]\s+свідомо пропущено\b', l, re.I)])   # лічильник «Свідомо лишено» — не пункт (питання 6, EquipLens S40)

def complete(ans, qs): return all(re.search(rf'(?m)^## {n}\b', ans) for n, _ in qs)

def run(root='/home/user', model='haiku', effort='medium'):
    if effort not in EFFORTS: return f'іспит: effort «{effort}» — не з {EFFORTS}', 2
    rs = hc.session_repos(root); repo = subject(rs)
    if not repo: return 'іспит: репо з самері не знайдено', 1
    qs = questions(); t0 = time.time()
    ans, meta = run_model(root, prompt(root, repo, rs, qs), model, effort)
    k = unclear(ans); ok = complete(ans, qs)
    line = f"іспит {heads_short(rs)} · незрозуміло {k}" if ok and k is not None else 'іспит неповний (модель не дала всі блоки)'
    open(mark_path(), 'w', encoding='utf-8').write(f"{hc.heads(rs)}\n{line}\n{json.dumps(dict(meta, model=model, effort=effort), ensure_ascii=False)}\n\n{ans}\n")
    cost = meta.get('total_cost_usd'); turns = meta.get('num_turns')
    tail = f" · модель {model} · effort {effort} · {int(time.time() - t0)} с" + (f" · ≈${cost:.3f}" if isinstance(cost, (int, float)) else '') + (f' · ходів {turns}' if turns else '')
    if meta.get('error'): tail += f" · помилка: {meta['error'][-200:]}"
    return f"{ans}\n\n{line}{tail}\n(мітка: {mark_path()} — звір кожну відповідь з репо таблицею «питання · відповідь · правда з репо · ✓/✗»)", 0 if ok else 1

VLINE = re.compile(r'^\s*(\d+)\s*[|·.)]?\s*(✓|✗|\?)\s*[|·]?\s*`?([^\s`|]+:\d+)?`?\s*[|·—-]?\s*(.*)$')

def _ref_ok(ref, root, rs):
    path, line = ref.rsplit(':', 1)
    for base in [root] + list(rs):
        f = path if os.path.isabs(path) else os.path.join(base, path)
        if os.path.isfile(f):
            try: return 1 <= int(line) <= sum(1 for _ in open(f, encoding='utf-8', errors='replace'))
            except OSError: return False
    return False

def verdict(src, root='/home/user'):
    """Вирок агента на кожен пункт блоку 6 мітки (той самий HEAD) → дописується в мітку. → (рядок, код)."""
    rs = hc.session_repos(root)
    try: txt = open(mark_path(), encoding='utf-8').read().split('\n<!--VERDICT-->')[0]
    except OSError: return 'вирок: мітки іспиту нема — спершу run', 1
    ls = txt.split('\n'); k = unclear(txt.split('\n\n', 1)[-1])
    if ls[0] != hc.heads(rs): return 'вирок: мітка іспиту — не на поточному HEAD (новий коміт після іспиту) → спершу run', 1
    if not k: return 'вирок: у блоці 6 нема пунктів — судити нічого', 1
    items, errs = {}, []
    for l in open(src, encoding='utf-8').read().splitlines():
        m = VLINE.match(l)
        if not m: continue
        n, v, ref, why = int(m.group(1)), m.group(2), m.group(3), m.group(4).strip()
        if v == '✗' and not ref: errs.append(f'{n}: ✗ без `шлях:рядок`')
        elif ref and not _ref_ok(ref, root, rs): errs.append(f'{n}: `{ref}` — нема такого файла чи рядка')
        elif v == '✗' and len(why) < 10: errs.append(f'{n}: ✗ без «чому» (≥ 10 знаків)')
        items[n] = dict(v=v, ref=ref, why=why)
    miss = [n for n in range(1, k + 1) if n not in items]
    if miss: errs.append(f'бракує пунктів {miss} з {k}')
    if errs: return 'вирок не прийнято: ' + ' · '.join(errs), 1
    real = sum(1 for n in range(1, k + 1) if items[n]['v'] != '✗')   # ? — не певен = справжній
    open(mark_path(), 'w', encoding='utf-8').write(txt + '\n<!--VERDICT-->\n' + json.dumps({'head': ls[0], 'k': k, 'real': real, 'items': items}, ensure_ascii=False) + '\n')
    return f'вирок прийнято: справжніх {real} з {k}' + (' — виправ, закоміть, новий іспит' if real else ' — печатка «іспит ✓»'), 0

JOURNAL_MAX = 3   # рядків §1 після іспиту: запис результату — 1–2; більше — це вже новий зміст, нехай його читає іспит

def journal_only(rs, old):
    """Від HEAD мітки (old — рядок hc.heads) до HEAD кожного репо — лише додані рядки таблиці §1 найновішого самері? → (так/ні, N рядків)."""
    olds = old.split(' ')
    if len(olds) != len(rs): return False, 0
    n = 0
    for r, h0 in zip(rs, olds):
        h = hc.git(r, 'rev-parse', 'HEAD')
        if h == h0: continue
        if subprocess.run(['git', '-C', r, 'merge-base', '--is-ancestor', h0, h], capture_output=True).returncode: return False, 0
        full = hc.latest_summary(r)
        rel = os.path.relpath(full, r) if full else ''
        if os.environ.get('EXAM_INJECT') == 'journal': n += 1; continue   # зуб: без розбору diff
        if not rel or hc.git(r, 'diff', '--name-only', h0, h).split('\n') != [rel]: return False, 0
        L = hc.git(r, 'show', f'{h}:{rel}').split('\n')
        i1 = next((i for i, x in enumerate(L) if re.match(r'## §1\b', x)), None)
        if i1 is None: return False, 0
        i2 = next((i for i in range(i1 + 1, len(L)) if L[i].startswith('## ')), len(L))
        for m in re.finditer(r'^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', hc.git(r, 'diff', '-U0', h0, h, '--', rel), re.M):
            dele, c, d = int(m.group(1) or 1), int(m.group(2)), int(m.group(3) or 1)
            if dele: return False, 0
            for ln in range(c - 1, c - 1 + d):
                if not (i1 < ln < i2 and L[ln].startswith('| ')): return False, 0
            n += d
    return n <= JOURNAL_MAX, n

def state(rs):
    """→ (на_HEAD, K або None, рядок). Для печатки ревізії (Л3)."""
    try: ls = open(mark_path(), encoding='utf-8').read().split('\n')
    except OSError: return False, None, 'іспит не робився'
    m = re.search(r'незрозуміло (\d+)', ls[1] if len(ls) > 1 else '')
    k = int(m.group(1)) if m else None
    jn = 0
    if os.environ.get('EXAM_INJECT') == 'stale': return False, k, 'іспит застарів (HEAD змінився після нього)'
    if ls[0] != hc.heads(rs):
        ok, jn = journal_only(rs, ls[0])
        if not ok or not jn: return False, k, 'іспит застарів (HEAD змінився після нього; не лише рядки §1 самері)'
    tail = f' · після іспиту — лише рядки §1 ({jn})' if jn else ''
    vj = '\n'.join(ls).split('\n<!--VERDICT-->\n')
    if k and len(vj) > 1:
        try: v = json.loads(vj[1].strip().split('\n')[0])
        except ValueError: v = {}
        if v.get('head') == ls[0] and v.get('k') == k:   # вирок на k пунктів цього HEAD → печатку судить кількість справжніх
            return True, v['real'], (f'іспит ✓ · справжніх 0 з {k} (✗ {k} з доказом)' if v['real'] == 0 else f'іспит · справжніх {v["real"]} з {k}') + tail
    return True, k, (f'іспит ✓ · незрозуміло 0' if k == 0 else f'іспит · незрозуміло {k}' if k is not None else 'іспит неповний') + tail

def selftest():
    bad = n = 0
    def case(name, ok):
        nonlocal bad, n; n += 1; print(('✓ ' if ok else '✗ ') + name); bad += not ok
    d = tempfile.mkdtemp(prefix='hx-'); r = os.path.join(d, 'Prod'); os.makedirs(os.path.join(r, 'docs/summary'))
    sh = lambda *c: subprocess.run(c, cwd=r, check=True, capture_output=True)
    sh('git', 'init', '-q'); sh('git', 'config', 'user.email', 't@t'); sh('git', 'config', 'user.name', 't')
    open(os.path.join(r, 'docs/summary/P_SUMMARY_2026-11-18.md'), 'w').write('# S\n## §0 ВІДКРИТЕ\n- AE-Q зараз\n## §1 · ХІД\n| # | що |\n|---|---|\n| 1 | a |\n## Стартове\n```text\nСТАРТ: AE-Q крок 2\n```\n')
    sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'c')
    os.environ['LENS_EXAM_MARK'] = os.path.join(d, 'mark.md')
    stub = os.path.join(d, 'stub.py'); seen = os.path.join(d, 'seen.txt')
    def fake(answer):
        open(stub, 'w').write(f"import sys,json\nopen({seen!r},'w').write(sys.stdin.read())\n"
                              f"print(json.dumps({{'type': 'assistant', 'message': {{'content': [{{'type': 'text', 'text': {answer!r}}}]}}}}))\n"
                              f"print(json.dumps({{'type': 'result', 'result': 'Пам\\'ять: нового нема', 'total_cost_usd': 0.01, 'num_turns': 3}}))\n")
        os.environ['LENS_EXAM_CMD'] = f'{sys.executable} {stub}'
    full = '\n'.join(f'## {i}\nвідповідь `a.md:1`' for i in range(1, 6)) + '\n## 6\n'
    rs = [r]
    fake(full + '—\n'); out, code = run(d)
    p = open(seen).read() if os.path.exists(seen) else ''
    case('prompt: стартове самері + усі 6 питань + «`файл:рядок`»', 'СТАРТ: AE-Q крок 2' in p and all(f'## {i}' in p for i in range(1, 7)) and '`файл:рядок`' in p)
    case('відповідь у середньому повідомленні, останнє — приписка (прогін 18.11) → береться повна', code == 0)
    case('повна відповідь, блок 6 «—» → «незрозуміло 0», вихід 0, мітка з HEAD', code == 0 and 'незрозуміло 0' in out and state(rs)[:2] == (True, 0))
    case('рівень у рядку «іспит …» і в мітці', 'effort medium' in out and '"effort": "medium"' in open(mark_path()).read())
    case('стан на тому самому HEAD → «іспит ✓ · незрозуміло 0»', state(rs)[2] == 'іспит ✓ · незрозуміло 0')
    fake(full + '- черга каже X · `docs/CHERGA.md:3` ⟂ `docs/summary/P.md:5`\n- застаріле «чекає» · `a.md:2`\n- свідомо пропущено: 7\n'); out, code = run(d)
    case('2 суперечності + рядок «свідомо пропущено: 7» у блоці 6 → «незрозуміло 2» (лічильник — не пункт), стан без ✓', 'незрозуміло 2' in out and state(rs)[2] == 'іспит · незрозуміло 2')
    vf = os.path.join(d, 'v.md'); W = lambda t: (open(vf, 'w').write(t), vf)[1]
    S = 'Prod/docs/summary/P_SUMMARY_2026-11-18.md'
    case('вирок: ✗ з неіснуючим рядком → не прийнято, стан без ✓', verdict(W(f'1 ✗ {S}:99 рядок історії, не стан\n2 ✗ {S}:2 рядок історії, не стан\n'), d)[1] == 1 and state(rs)[2] == 'іспит · незрозуміло 2')
    case('вирок: бракує пункту → не прийнято', verdict(W(f'1 ✗ {S}:2 рядок історії, не стан\n'), d)[1] == 1)
    case('вирок: ✗ без «чому» → не прийнято', verdict(W(f'1 ✗ {S}:2 так\n2 ✗ {S}:3 рядок історії, не стан\n'), d)[1] == 1)
    case('вирок: обидва ✗ з доказом → «іспит ✓ · справжніх 0 з 2», печатка ✓', verdict(W(f'1 ✗ `{S}:2` рядок історії, не стан\n2 · ✗ · docs/summary/P_SUMMARY_2026-11-18.md:3 · читач не дочитав\n'), d)[1] == 0 and state(rs)[:2] == (True, 0) and 'справжніх 0 з 2' in state(rs)[2])
    case('вирок: «?» не певен → рахується справжнім, не ✓', verdict(W(f'1 ? не певен, чи стан\n2 ✗ {S}:3 рядок історії, не стан\n'), d)[1] == 0 and state(rs)[:2] == (True, 1))
    case('вирок: один ✓ → «справжніх 1 з 2», не ✓', verdict(W(f'1 ✓ {S}:2 справжнє\n2 ✗ {S}:3 рядок історії, не стан\n'), d)[1] == 0 and state(rs)[2] == 'іспит · справжніх 1 з 2')
    fake('## 1\nлише одне'); out, code = run(d)
    case('модель не дала всі блоки → «іспит неповний», вихід 1', code == 1 and 'неповний' in out and state(rs)[2] == 'іспит неповний')
    fake(full + '—\n'); run(d); open(os.path.join(r, 'x'), 'w').write('1'); sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'новий')
    case('новий коміт після іспиту → «іспит застарів», не ✓', not state(rs)[0] and 'застарів' in state(rs)[2])
    SP = os.path.join(r, 'docs/summary/P_SUMMARY_2026-11-18.md')
    def edit(old, new, extra=None):   # правка самері (+ інший файл) → коміт
        t = open(SP).read(); assert old in t; open(SP, 'w').write(t.replace(old, new, 1))
        if extra: open(os.path.join(r, extra), 'w').write('1')
        sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'j')
    fresh = lambda: (fake(full + '—\n'), run(d))
    fresh(); edit('| 1 | a |\n', '| 1 | a |\n| 2 | іспит 17 |\n')
    case('журнал: після іспиту лише 1 рядок §1 → іспит живий, печатка каже «лише рядки §1 (1)»', state(rs)[0] and 'лише рядки §1 (1)' in state(rs)[2])
    edit('- AE-Q зараз', '- AE-Q далі')
    case('журнал: потім правка §0 → «застарів»', not state(rs)[0] and 'застарів' in state(rs)[2])
    fresh(); edit('| 1 | a |\n', '| 1 | a |\n| 3 | b |\n', extra='y')
    case('журнал: рядок §1 + інший файл → «застарів»', not state(rs)[0])
    fresh(); edit('| 1 | a |\n', '| 1 | a |\n' + ''.join(f'| {i} | c |\n' for i in range(4, 8)))
    case(f'журнал: {JOURNAL_MAX + 1} рядки §1 → «застарів» (новий зміст читає іспит)', not state(rs)[0])
    fresh(); edit('| 1 | a |\n', '| 1 | А |\n')
    case('журнал: зміна наявного рядка §1 (видалення) → «застарів»', not state(rs)[0])
    fresh(); edit('| 1 | А |\n', '| 1 | А |\n| 9 | d |\n', extra='z')
    os.environ['EXAM_INJECT'] = 'journal'; inj = state(rs)[0]; os.environ.pop('EXAM_INJECT')
    case('зуб: EXAM_INJECT=journal (без розбору diff) → інший файл пройшов би; без зуба — «застарів»', inj and not state(rs)[0])
    os.remove(mark_path())
    case('effort явно в команді моделі (S40: без нього рівень не видно)', exam_argv('haiku', 'medium')[3:6] == ['haiku', '--effort', 'medium'])
    case('effort не з переліку → вихід 2, моделі не кличе', run(d, 'haiku', 'ultra')[1] == 2)
    case('мітки нема → «іспит не робився»', state(rs)[2] == 'іспит не робився')
    os.environ['EXAM_INJECT'] = 'stale'; fake(full + '—\n'); run(d)
    case('зуб: EXAM_INJECT=stale → «застарів» на тому самому HEAD (перевірка HEAD справді діє)', not state(rs)[0])
    os.environ.pop('EXAM_INJECT'); os.environ.pop('LENS_EXAM_CMD'); os.environ.pop('LENS_EXAM_MARK')
    qs = questions()
    case('питання з файла: 6 блоків, останній — про суперечності', len(qs) == 6 and 'суперечить' in qs[-1][1])
    print(f'─── handoff_exam selftest: {n - bad}/{n} ───'); return 1 if bad else 0

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']: sys.exit(selftest())
    if a[:1] == ['verdict'] and len(a) > 1:
        out, code = verdict(a[1], a[2] if len(a) > 2 else '/home/user'); print(out); sys.exit(code)
    if a[:1] == ['state']:
        print(state(hc.session_repos(a[1] if len(a) > 1 else '/home/user'))[2]); sys.exit(0)
    if a[:1] == ['run']:
        model = a[a.index('--model') + 1] if '--model' in a else 'haiku'
        effort = a[a.index('--effort') + 1] if '--effort' in a else 'medium'
        rest = [x for x in a[1:] if not x.startswith('--') and x not in (model, effort)]
        out, code = run(rest[0] if rest else '/home/user', model, effort); print(out); sys.exit(code)
    print('handoff_exam.py run [<корінь>] [--model haiku] [--effort medium] | verdict <файл> [<корінь>] | state [<корінь>] | selftest'); sys.exit(2)
