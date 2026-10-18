#!/bin/bash
# живе доки: профіль Konst вимагає «ПІДСИЛЕННЯ ІНТЕРНЕТОМ» у плані (ЦИКЛ п.4). Дім — lens-governance:tools/claude-code/hooks/ (HOOK-2.5, 10.10.2026).
# Слово Konst 10.10: правило «шукай ззовні» в профілі є, а модель його рідко виконує — і не лише в UI: документація, API, протоколи, формати.
# Подія Stop: відповідь агента несе план (рядок «Мікроскоп» / «## План» / «**План»), а в цьому ході не було жодного WebSearch / WebFetch
# і нема рядка «практики не знайшов» → decision: block з причиною: пошукати (три рядки: практика · беремо · не беремо + джерело з датою)
# або одним рядком сказати, чому крок не вирішує форму. Раз на хід (stop_hook_active). Помилка розбору → тиша.
# Формат — code.claude.com/docs/en/hooks «Stop» (last_assistant_message, stop_hook_active, transcript_path), 09.10.2026.
# Друге правило (QR CC-15, Konst 16.10.2026: «кукбук — довідник, як інтернет, не інструкція»; агент читав рецепт як закон): план спирається на номер
# рецепта (A66, B3.2 …), а рядка синтезу «рецепт ⟂ світ ⟂ замір → рішення» нема → block: рецепт — точка старту, рішення — з трьох джерел.
# Рецептом вважається лише номер, що Є в індексі кукбуку (kernel/cookbook/Lens_cookbook_INDEX.md; A66.2 — бо є A66): номер версії застосунку
# «B65.1» (батч QR) — не рецепт (хибне ×2, журнал гачків 18.10.2026, QR CC-17 · CC-18). Індексу нема → як раніше, будь-який A/B-номер.
# Зуби: bash plan-web.sh selftest — 13 випадків.
mode="${1:-stop}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN PW_SELF="${BASH_SOURCE[0]}"
python3 - "$mode" <<'PY'
import json, re, sys, os, tempfile
PLAN = re.compile(r"(^|\n)\s*(#+\s*)?(\*\*)?\s*(План\b|Мікроскоп\b)", re.I)
SKIP = re.compile(r"практики не знайшов|крок не вирішує форму", re.I)
RECIPE = re.compile(r"(?<![\w-])[AАBВ]\d{1,3}(\.\d+)?(?![\w])")
KNOWN = set()
try:
    _ix = os.path.join(os.path.dirname(os.path.abspath(os.environ.get('PW_SELF', ''))), '..', '..', '..', 'kernel', 'cookbook', 'Lens_cookbook_INDEX.md')
    KNOWN = set(re.findall(r"`([AB]\d+(?:\.\d+)?)`", open(_ix, encoding='utf-8').read()))
except Exception: pass
LAT = str.maketrans('АВ', 'AB')
def recipes(msg):
    out = []
    for m in RECIPE.finditer(msg):
        t = m.group(0).translate(LAT)
        if not KNOWN or t in KNOWN or t.split('.')[0] in KNOWN: out.append(t)
    return out
SYNTH = re.compile(r"рецепт(\s+[AАBВ]?[\d.]+)?\s*[⟂+·]\s*світ|рецепт не стосується", re.I)

def real_user(x):
    if x.get('type') != 'user' or x.get('isMeta') or x.get('isCompactSummary'): return False
    c = (x.get('message') or {}).get('content')
    if isinstance(c, list) and any(isinstance(i, dict) and i.get('type') == 'tool_result' for i in c): return False
    t = c if isinstance(c, str) else ' '.join(i.get('text', '') for i in (c or []) if isinstance(i, dict))
    return bool(t.strip()) and not t.strip().startswith('<')

def verdict(d):
    if d.get('stop_hook_active'): return None
    msg = d.get('last_assistant_message') or ''
    if not PLAN.search(msg): return None
    rc = recipes(msg)
    if rc and not SYNTH.search(msg):
        return ("Ворота «рецепт як закон» (Konst 16.10.2026: кукбук — довідник, як інтернет, не інструкція; HOOK-2.5): план спирається на рецепт "
                f"({rc[0]}), а рядка синтезу нема. Допиши рядком: «рецепт ⟂ світ ⟂ замір → рішення» — що каже рецепт, що каже пошук, "
                "що показав замір цього екрана, і що беремо / де робимо краще за рецепт (тоді онови рецепт). Рецепт згаданий лише як довідка — «рецепт не стосується: …».")
    if SKIP.search(msg): return None
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
             ('повтор через гачок (stop_hook_active) → тиша', D(plan, [U], True), False),
             ('план на рецепті A66 з пошуком, без синтезу → block', D(plan + '\nЗа A66 — тінь знизу.', [U, T('WebSearch')]), True),
             ('план на рецепті з рядком «рецепт ⟂ світ ⟂ замір» → тиша', D(plan + '\nрецепт A66 ⟂ світ (Material) ⟂ замір 2,25 → беремо підпис', [U, T('WebSearch')]), False),
             ('«рецепт не стосується» → тиша', D(plan + '\nB3.2 — рецепт не стосується: інший екран', [U, T('WebSearch')]), False),
             ('номер черги QRL-15 / коміт a66b — не рецепт → тиша', D(plan + '\nQRL-15, коміт a66b0f2', [U, T('WebSearch')]), False),
             ('версія застосунку B65.1 / B57 — не рецепт → тиша', D(plan + '\nВерсія: B65.1 — чому; задум B57', [U, T('WebSearch')]), False),
             ('справжній рецепт серії B (B3.2) без синтезу → block', D(plan + '\nЗа B3.2 — так.', [U, T('WebSearch')]), True),
             ('підрецепт A66.2 (є A66) без синтезу → block', D(plan + '\nЗа A66.2 — кант.', [U, T('WebSearch')]), True),
             ('кирилична «А27» = A27 → block', D(plan + '\nЗа А27 — без руху.', [U, T('WebSearch')]), True)]
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
