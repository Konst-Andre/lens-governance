#!/usr/bin/env python3
# живе доки: ревізія має іспит нового агента (REV-5 Л2, «так» Konst 18.11.2026, AE S155). Бриф — `kernel/Lens_REV-5_brief.md`.
# Іспит нового агента: інша модель БЕЗ пам'яті сесії читає лише записане (стартове → самері §0 → черга → що вони називають) і відповідає на
#   питання `tools/claude-code/handoff_exam_questions.md`. Записане перевіряє той, хто його не писав: машина (`handoff_check`) судить наявне,
#   а розбіжності й застарілі рядки бачить лише читач (S155: машина «✗ 0», іспит haiku — ще 5 дір). Відповіді й мітка з HEAD — у /tmp; печатку
#   ревізії (`handoff_check.py revision`) робить ЧЕСНОЮ: «іспит ✓ · незрозуміло 0» / «іспит · незрозуміло K» / «іспит не робився».
# Світ: I-PASS — приймальник переказує сам (UCSF, 2012; 18.11.2026); «Handoff Debt» — ціну передачі міряє наступник (arXiv 2606.02875, 06.2026).
#   `claude -p`: --allowedTools лише схвалює, НЕ обмежує — тому ще --permission-mode dontAsk (решту відхиляє) і --disallowedTools;
#   --max-budget-usd — стеля (оцінка клієнта, може перейти — запас); total_cost_usd у JSON (code.claude.com/docs/en/headless · best-practices, 18.11.2026).
# Запуск:  python3 tools/claude-code/handoff_exam.py run [<корінь з репо>] [--model haiku]   → відповіді + рядок «іспит …», мітка /tmp/lens-exam-<сесія>.md
#          python3 tools/claude-code/handoff_exam.py state [<корінь>]                         → рядок стану мітки (на HEAD? незрозуміло K)
#          python3 tools/claude-code/handoff_exam.py selftest                                 → зуби на підставній моделі (LENS_EXAM_CMD), без витрат
# Вихід:   run — 0, якщо відповіді повні (6 блоків); 1 — модель не відповіла чи формат зламано. Оцінку «правда з репо» робить агент таблицею.
# Інша модель (профіль «ІНША МОДЕЛЬ»): перед run агент називає в чаті модель · effort · навіщо. Інструменти моделі — лише Read · Grep · Glob.
import json, os, re, shlex, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
QFILE = os.path.join(HERE, 'handoff_exam_questions.md')
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

def run_model(root, text, model):
    """claude -p у stream-json: усі повідомлення моделі (не лише останнє — прогін на зуби 18.11: `result` дав лише приписку після відповіді).
    --setting-sources local — без гачків користувача (профіль середовища робив з екзаменованого працівника: «Пам'ять: нового нема»)."""
    cmd = os.environ.get('LENS_EXAM_CMD')
    argv = shlex.split(cmd) if cmd else ['claude', '-p', '--model', model, '--output-format', 'stream-json', '--verbose', '--max-turns', '40',
                                         '--max-budget-usd', BUDGET, '--setting-sources', 'local', '--disable-slash-commands', '--no-session-persistence',
                                         '--append-system-prompt', EXAMINEE, '--permission-mode', 'dontAsk', '--allowedTools', 'Read', 'Grep', 'Glob',
                                         '--disallowedTools', 'Bash', 'Edit', 'Write', 'NotebookEdit', 'WebFetch', 'WebSearch', 'Agent', 'Task']
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
    return len([l for l in m.group(1).splitlines() if re.match(r'\s*[-*•]\s+\S', l) and not re.match(r'\s*[-*•]\s+—\s*$', l)])

def complete(ans, qs): return all(re.search(rf'(?m)^## {n}\b', ans) for n, _ in qs)

def run(root='/home/user', model='haiku'):
    rs = hc.session_repos(root); repo = subject(rs)
    if not repo: return 'іспит: репо з самері не знайдено', 1
    qs = questions(); t0 = time.time()
    ans, meta = run_model(root, prompt(root, repo, rs, qs), model)
    k = unclear(ans); ok = complete(ans, qs)
    line = f"іспит {heads_short(rs)} · незрозуміло {k}" if ok and k is not None else 'іспит неповний (модель не дала всі блоки)'
    open(mark_path(), 'w', encoding='utf-8').write(f"{hc.heads(rs)}\n{line}\n{json.dumps(meta, ensure_ascii=False)}\n\n{ans}\n")
    cost = meta.get('total_cost_usd'); turns = meta.get('num_turns')
    tail = f" · модель {model} · {int(time.time() - t0)} с" + (f" · ≈${cost:.3f}" if isinstance(cost, (int, float)) else '') + (f' · ходів {turns}' if turns else '')
    if meta.get('error'): tail += f" · помилка: {meta['error'][-200:]}"
    return f"{ans}\n\n{line}{tail}\n(мітка: {mark_path()} — звір кожну відповідь з репо таблицею «питання · відповідь · правда з репо · ✓/✗»)", 0 if ok else 1

def state(rs):
    """→ (на_HEAD, K або None, рядок). Для печатки ревізії (Л3)."""
    try: ls = open(mark_path(), encoding='utf-8').read().split('\n')
    except OSError: return False, None, 'іспит не робився'
    m = re.search(r'незрозуміло (\d+)', ls[1] if len(ls) > 1 else '')
    k = int(m.group(1)) if m else None
    if ls[0] != hc.heads(rs) or os.environ.get('EXAM_INJECT') == 'stale': return False, k, 'іспит застарів (HEAD змінився після нього)'
    return True, k, (f'іспит ✓ · незрозуміло 0' if k == 0 else f'іспит · незрозуміло {k}' if k is not None else 'іспит неповний')

def selftest():
    bad = n = 0
    def case(name, ok):
        nonlocal bad, n; n += 1; print(('✓ ' if ok else '✗ ') + name); bad += not ok
    d = tempfile.mkdtemp(prefix='hx-'); r = os.path.join(d, 'Prod'); os.makedirs(os.path.join(r, 'docs/summary'))
    sh = lambda *c: subprocess.run(c, cwd=r, check=True, capture_output=True)
    sh('git', 'init', '-q'); sh('git', 'config', 'user.email', 't@t'); sh('git', 'config', 'user.name', 't')
    open(os.path.join(r, 'docs/summary/P_SUMMARY_2026-11-18.md'), 'w').write('# S\n## §0 ВІДКРИТЕ\n- AE-Q зараз\n## Стартове\n```text\nСТАРТ: AE-Q крок 2\n```\n')
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
    case('стан на тому самому HEAD → «іспит ✓ · незрозуміло 0»', state(rs)[2] == 'іспит ✓ · незрозуміло 0')
    fake(full + '- черга каже X · `docs/CHERGA.md:3` ⟂ `docs/summary/P.md:5`\n- застаріле «чекає» · `a.md:2`\n'); out, code = run(d)
    case('2 суперечності в блоці 6 → «незрозуміло 2», стан без ✓', 'незрозуміло 2' in out and state(rs)[2] == 'іспит · незрозуміло 2')
    fake('## 1\nлише одне'); out, code = run(d)
    case('модель не дала всі блоки → «іспит неповний», вихід 1', code == 1 and 'неповний' in out and state(rs)[2] == 'іспит неповний')
    fake(full + '—\n'); run(d); open(os.path.join(r, 'x'), 'w').write('1'); sh('git', 'add', '-A'); sh('git', 'commit', '-qm', 'новий')
    case('новий коміт після іспиту → «іспит застарів», не ✓', not state(rs)[0] and 'застарів' in state(rs)[2])
    os.remove(mark_path())
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
    if a[:1] == ['state']:
        print(state(hc.session_repos(a[1] if len(a) > 1 else '/home/user'))[2]); sys.exit(0)
    if a[:1] == ['run']:
        model = a[a.index('--model') + 1] if '--model' in a else 'haiku'
        rest = [x for x in a[1:] if not x.startswith('--') and x != model]
        out, code = run(rest[0] if rest else '/home/user', model); print(out); sys.exit(code)
    print('handoff_exam.py run [<корінь>] [--model haiku] | state [<корінь>] | selftest'); sys.exit(2)
