#!/bin/bash
# живе доки: профіль Konst вимагає «ПІДСИЛЕННЯ ІНТЕРНЕТОМ» у плані (ЦИКЛ п.4). Дім — lens-governance:tools/claude-code/hooks/ (HOOK-2.5, 10.10.2026).
# Слово Konst 10.10: правило «шукай ззовні» в профілі є, а модель його рідко виконує — і не лише в UI: документація, API, протоколи, формати.
# Подія Stop: відповідь агента несе план (рядок «Мікроскоп» / «## План» / «**План»), а в цьому ході не було жодного WebSearch / WebFetch
# і нема рядка «практики не знайшов» → decision: block з причиною: пошукати (три рядки: практика · беремо · не беремо + джерело з датою)
# або одним рядком сказати, чому крок не вирішує форму. Раз на хід (stop_hook_active). Помилка розбору → тиша.
# Формат — code.claude.com/docs/en/hooks «Stop» (last_assistant_message, stop_hook_active, transcript_path), 09.10.2026.
# Зуби: bash plan-web.sh selftest — 5 випадків.
mode="${1:-stop}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN
python3 - "$mode" <<'PY'
import json, re, sys, os, tempfile
PLAN = re.compile(r"(^|\n)\s*(#+\s*)?(\*\*)?\s*(План\b|Мікроскоп\b)", re.I)
SKIP = re.compile(r"практики не знайшов|крок не вирішує форму", re.I)

def real_user(x):
    if x.get('type') != 'user' or x.get('isMeta') or x.get('isCompactSummary'): return False
    c = (x.get('message') or {}).get('content')
    if isinstance(c, list) and any(isinstance(i, dict) and i.get('type') == 'tool_result' for i in c): return False
    t = c if isinstance(c, str) else ' '.join(i.get('text', '') for i in (c or []) if isinstance(i, dict))
    return bool(t.strip()) and not t.strip().startswith('<')

def verdict(d):
    if d.get('stop_hook_active'): return None
    msg = d.get('last_assistant_message') or ''
    if not PLAN.search(msg) or SKIP.search(msg): return None
    L = [json.loads(l) for l in open(os.path.expanduser(d['transcript_path']), encoding='utf-8') if l.strip()]
    idx = [i for i, x in enumerate(L) if real_user(x)]
    for x in L[(idx[-1] if idx else 0):]:
        for i in ((x.get('message') or {}).get('content') or []) if x.get('type') == 'assistant' else []:
            if isinstance(i, dict) and i.get('type') == 'tool_use' and i.get('name') in ('WebSearch', 'WebFetch'): return None
    return ("Ворота «план без світу» (профіль ЦИКЛ п.4, HOOK-2.5): у відповіді план / мікроскоп, а в цьому ході жодного пошуку ззовні. "
            "Якщо крок вирішує форму (теки, імена, формат і дім даних, інструмент, протокол, API, UI-патерн) — пошукай і допиши три рядки: "
            "практика · що беремо · що не беремо і чому + джерело з датою; для елемента інтерфейсу — 2–3 варіанти на вибір Konst. "
            "Шукав і нічого — «практики не знайшов (запити: …)». Крок не вирішує форму — одним рядком скажи це й заверши.")

def selftest():
    def tr(msgs):
        f = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False, encoding='utf-8')
        for m in msgs: f.write(json.dumps(m, ensure_ascii=False) + '\n')
        f.close(); return f.name
    U = {'type': 'user', 'message': {'content': 'роби'}}
    T = lambda name: {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': name, 'input': {}}]}}
    D = lambda msg, msgs, act=False: {'last_assistant_message': msg, 'transcript_path': tr(msgs), 'stop_hook_active': act}
    plan = 'Ось план.\n## План\n1. …\n**Мікроскоп:** числа …'
    cases = [('план без пошуку → block', D(plan, [U, T('Bash')]), True),
             ('план з WebSearch у цьому ході → тиша', D(plan, [U, T('WebSearch'), T('Bash')]), False),
             ('пошук лише в МИНУЛОМУ ході не рахується → block', D(plan, [U, T('WebSearch'), U, T('Bash')]), True),
             ('«практики не знайшов (запити: …)» → тиша', D(plan + '\nпрактики не знайшов (запити: x)', [U]), False),
             ('без плану → тиша', D('Готово, коміт abc.', [U, T('Bash')]), False),
             ('повтор через гачок (stop_hook_active) → тиша', D(plan, [U], True), False)]
    bad = 0
    for name, d, want in cases:
        ok = (verdict(d) is not None) == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    print(f'─── plan-web selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

if sys.argv[1] == 'selftest': sys.exit(selftest())
try:
    out = verdict(json.loads(os.environ.get('HOOK_IN') or '{}'))
except Exception:
    out = None
if out: print(json.dumps({'decision': 'block', 'reason': out}, ensure_ascii=False))
PY
