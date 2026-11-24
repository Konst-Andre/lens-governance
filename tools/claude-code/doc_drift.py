#!/usr/bin/env python3
# doc_drift — Haiku-звірка описів на ревізії: пари «опис ↔ змінений у сесії код» → «суперечить / застаріло / ок» з ДОСЛІВНОЮ цитатою опису.
# живе доки: ревізія (`handoff_check revision`) дає ⚠ «описи, що згадують змінений код, але не мінялись», і хтось має їх прочитати
#   (Konst 24.11.2026, ядро AUDIT: «крок ревізії — найсильніше місце для Haiku… розвинь у чітку дію інструментом»).
# Чому так (практика 24.11.2026): дешевий детермінований відбір кандидатів + LLM-суддя + рішення людини — DocPulse (github.com/YoniRaviv/DocPulse:
#   граф зв'язків → підозрілі розділи → LLM-верифікатор; режим `--suspects-only` без моделі = наш `--dry`), understandingdata.com «Doc Drift
#   Detection in CI»; «LLM не годиться як самостійний детектор дрейфу» (arxiv 2604.03447) → Haiku лише позначає, вирок — Opus, читаючи свої рядки.
#   Не беремо: автоправки (DocPulse комітить сам) — правка опису йде звичайним ходом агента.
# Відбір пар — `handoff_check.stale_docs` (одне правило з ⚠ ревізії). Модель — haiku effort low, без інструментів, один виклик на всі пари
#   (податок старту ≈ 17 тис. без інструментів — замір 24.11); цитата, якої нема в описі дослівно, — «?», не ⚠ (зуб на вигадку моделі).
# Запуск:  python3 tools/claude-code/doc_drift.py run [<репо>] [--dry] [--max N]   (перед run — у чат: модель · effort · навіщо)
#          python3 tools/claude-code/doc_drift.py selftest
# Вихід: 0 — звірено (⚠ — порада, не гейт) · 1 — відповідь моделі не прочитана · 2 — виклик неправильний.
import json, os, re, shlex, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import handoff_check as hc

MODEL, EFFORT, MAX = 'haiku', 'low', 25
VERDICTS = ('суперечить', 'застаріло', 'ок', 'не стосується')

def tail():
    return os.environ.get('LENS_DD_TAIL') or hc.mine_tail()

def snippets(text, c, n=2, width=700):
    out = []
    for i, ln in enumerate(text.split('\n'), 1):
        k = ln.find(c) if c in ln else ln.find(os.path.basename(c))
        if k < 0: continue
        a = max(0, k - width // 2); out.append((i, ln[a:a + width]))
        if len(out) >= n: break
    return out

def change(repo, t, c):
    subj = hc.git(repo, 'log', f'--grep=session_{t}', '--format=%h %s', '--', c).split('\n')
    shas = [x.split()[0] for x in subj if x]
    diff = ''
    if shas:
        d = hc.git(repo, 'diff', f'{shas[-1]}^', shas[0], '--', c)
        diff = '\n'.join(l for l in d.split('\n') if l[:1] in '+-' and not l.startswith(('+++', '---')))[:2500]
    return [x[:300] for x in subj if x][:6], diff

def pairs(repo, t, mx=MAX):
    code, stale = hc.stale_docs(repo, t)
    out = []
    for d in sorted(stale, key=lambda d: -len(stale[d])):
        txt = open(os.path.join(repo, d), encoding='utf-8').read()
        for c in stale[d]:
            sn = snippets(txt, c)
            if sn: out.append({'doc': d, 'code': c, 'lines': sn})
            if len(out) >= mx: return code, out
    return code, out

def prompt(repo, t, ps):
    ch, blocks = {}, []
    for p in ps:
        if p['code'] not in ch: ch[p['code']] = change(repo, t, p['code'])
    for c, (subj, diff) in ch.items():
        blocks.append(f"### Код `{c}` — коміти сесії:\n" + '\n'.join(subj) + f"\nЗміни (+/−):\n{diff or '(дифу нема)'}")
    for i, p in enumerate(ps, 1):
        blocks.append(f"### Пара {i}: опис `{p['doc']}` згадує `{p['code']}`\n" + '\n'.join(f"[рядок {n}] {s}" for n, s in p['lines']))
    return ("Ти звіряєш описи з кодом. Нижче — що змінилось у коді за сесію, і рядки документів, що цей код згадують.\n"
            "Для КОЖНОЇ пари: чи рядок опису після цих змін іще правдивий? Вердикт одне з: суперечить · застаріло · ок · не стосується "
            "(«не стосується» — рядок згадує файл, але не описує змінену поведінку). Цитата — ДОСЛІВНИЙ шматок рядка опису (10–25 слів), "
            "не переказ: її перевірять пошуком. Відповідь — лише JSON-масив без тексту довкола: "
            '[{"pair": 1, "line": <номер рядка>, "verdict": "...", "quote": "...", "why": "одне речення"}]\n\n' + '\n\n'.join(blocks))

def ask(text, model=MODEL, effort=EFFORT):
    cmd = os.environ.get('LENS_DD_CMD')
    argv = shlex.split(cmd) if cmd else ['claude', '-p', '--model', model, '--effort', effort, '--tools', '', '--output-format', 'json',
                                         '--max-turns', '1', '--setting-sources', 'local', '--no-session-persistence']
    r = subprocess.run(argv, input=text, capture_output=True, text=True, timeout=600)
    try: out = json.loads(r.stdout); res, cost = out.get('result', ''), out.get('total_cost_usd')
    except ValueError: res, cost = r.stdout, None
    m = re.search(r'\[.*\]', res or '', re.S)
    try: return json.loads(m.group(0)) if m else None, cost
    except ValueError: return None, cost

def norm(s): return re.sub(r'\s+', ' ', s or '').strip().strip('`«»"\'').strip()

def run(repo='.', dry=False, mx=MAX):
    t = tail()
    if not t: return 'ⓘ сесію не визначено (CLAUDE_CODE_REMOTE_SESSION_ID) — нема з чим звіряти', 0
    code, ps = pairs(repo, t, mx)
    if not code: return 'ⓘ змін коду в комітах сесії нема — описам нема від чого відставати', 0
    if not ps: return f'✓ описів, що згадують змінений код ({len(code)} файлів) і не мінялись, нема', 0
    text = prompt(repo, t, ps)
    if dry:
        return (f'пар {len(ps)} (код {len(code)} файлів) · запит ≈ {len(text.encode()) * 10 // 34 // 1000} тис. токенів (3,4 байта на токен) — моделі не кличу\n' +
                '\n'.join(f"  {p['doc']}:{p['lines'][0][0]} ↔ {p['code']}" for p in ps)), 0
    ans, cost = ask(text)
    if ans is None: return '✗ відповідь моделі не JSON — звір описи сам (пари: --dry)', 1
    L, bad, odd = [], 0, 0
    for a in ans:
        try: p = ps[int(a.get('pair', 0)) - 1]
        except (ValueError, IndexError): odd += 1; continue
        v, q = a.get('verdict', ''), norm(a.get('quote'))
        if v not in ('суперечить', 'застаріло'): continue
        body = norm(open(os.path.join(repo, p['doc']), encoding='utf-8').read())
        if not q or q not in body:
            odd += 1; L.append(f"? {p['doc']}:{a.get('line', '?')} — модель каже «{v}», але цитати в описі нема дослівно — прочитай рядок сам ({p['code']})"); continue
        bad += 1; L.append(f"⚠ {p['doc']}:{a.get('line', '?')} — {v}: «{q[:160]}» — {a.get('why', '')[:200]} (код: {p['code']})")
    head = f"звірка описів (haiku {EFFORT}): пар {len(ps)} · ⚠ {bad} · ? {odd}" + (f" · ≈${cost:.3f}" if isinstance(cost, (int, float)) else '')
    tailline = '— ⚠ і ? прочитай сам (Read offset/limit) і виправ опис або назви, чому він правий; модель — кандидат, не вирок' if L else '— суперечностей не знайдено'
    return '\n'.join([head] + L + [tailline]), 0

def selftest():
    ok = []; c = lambda n, v: ok.append((n, bool(v)))
    d = tempfile.mkdtemp(); g = lambda *a: subprocess.run(['git', '-C', d, *a], capture_output=True, text=True)
    g('init', '-q'); g('config', 'user.email', 't@t'); g('config', 'user.name', 't')
    os.makedirs(f'{d}/tools'); open(f'{d}/tools/run_me.sh', 'w').write('echo a\n')
    open(f'{d}/B.md', 'w').write('# Опис\nЗапуск — `tools/run_me.sh` без аргументів друкує літеру a.\n')
    g('add', '.'); g('commit', '-qm', 'old')
    open(f'{d}/tools/run_me.sh', 'w').write('echo "${1:?аргумент обовʼязковий}"\n'); g('commit', '-qam', 'тепер з аргументом\n\nClaude-Session: x/session_TEST')
    os.environ['LENS_DD_TAIL'] = 'TEST'
    out, rc = run(d, dry=True); c('--dry: пара B.md ↔ tools/run_me.sh, моделі не кличе', 'B.md:2 ↔ tools/run_me.sh' in out and rc == 0)
    fake = os.path.join(d, 'fake.sh')
    def model(answer):
        open(fake, 'w').write('#!/bin/sh\ncat >/dev/null\nprintf \'%s\' ' + shlex.quote(json.dumps({'result': answer, 'total_cost_usd': 0.001})) + '\n'); os.chmod(fake, 0o755)
        os.environ['LENS_DD_CMD'] = fake
    model(json.dumps([{'pair': 1, 'line': 2, 'verdict': 'суперечить', 'quote': 'Запуск — `tools/run_me.sh` без аргументів друкує літеру a', 'why': 'тепер аргумент обовʼязковий'}], ensure_ascii=False))
    out, rc = run(d); c('справжня цитата + «суперечить» → ⚠ з рядком', '⚠ B.md:2 — суперечить' in out and '⚠ 1' in out)
    model(json.dumps([{'pair': 1, 'line': 2, 'verdict': 'суперечить', 'quote': 'скрипт приймає прапор --force', 'why': 'x'}], ensure_ascii=False))
    out, rc = run(d); c('зуб: вигадана цитата → «?», не ⚠', '? B.md:2' in out and '⚠ 0' in out)
    model(json.dumps([{'pair': 1, 'line': 2, 'verdict': 'ок', 'quote': 'Запуск', 'why': ''}], ensure_ascii=False))
    out, rc = run(d); c('«ок» → суперечностей не знайдено', 'суперечностей не знайдено' in out and rc == 0)
    model('я не зміг'); out, rc = run(d); c('зуб: відповідь не JSON → ✗, вихід 1', out.startswith('✗') and rc == 1)
    os.environ['LENS_DD_TAIL'] = 'NONE'; out, rc = run(d); c('комітів сесії нема → ⓘ', out.startswith('ⓘ змін коду'))
    for k in ('LENS_DD_TAIL', 'LENS_DD_CMD'): os.environ.pop(k, None)
    for n, v in ok: print(('✓ ' if v else '✗ ') + n)
    bad = sum(1 for _, v in ok if not v); print(f'─── doc_drift selftest: {len(ok) - bad}/{len(ok)} ───'); return 1 if bad else 0

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']: sys.exit(selftest())
    if a[:1] != ['run']: print('doc_drift.py run [<репо>] [--dry] [--max N] | selftest'); sys.exit(2)
    mx = int(a[a.index('--max') + 1]) if '--max' in a else MAX
    rest = [x for x in a[1:] if not x.startswith('--') and x != str(mx)]
    out, rc = run(rest[0] if rest else '.', '--dry' in a, mx); print(out); sys.exit(rc)
