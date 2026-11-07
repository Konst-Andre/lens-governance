#!/bin/bash
# route-remind.sh · гачок «маршрут для Konst» (AE S135, В-332 AE; слово Konst: «щоб я не втратив маршрут — нагадуй сам; гачок для всіх продуктів, і щоб еволюціонував»).
# живе доки: Konst працює з агентами над кількома продуктами й чергами. Дім — lens-governance:tools/claude-code/hooks/ (диспетчер lens-hooks.sh, подія UserPromptSubmit).
# Що робить: читає розмову сесії (transcript_path) і рахує звіти агента (відповідь ≥ 400 знаків). Будить, коли (а) звітів ще нема — перша відповідь сесії,
#   (б) у трьох останніх звітах нема блоку «Маршрут», (в) Konst сам питає про маршрут / план / «куди рухаємось» / «загубився». Не будить, коли маршрут
#   був у двох останніх звітах і питання нема. Сам дістає маршрут: найновіше самері репо сесії (docs/summary/*SUMMARY*.md · sessions/**/*summary*.md),
#   рядок з «МАРШРУТ» у §0 і пункти під ним (≤ 1 200 знаків) — агент показує його з репо, а не з пам'яті чату (практика: файл-дорожня карта, яку агент
#   читає й оновлює — Anthropic «Effective harnesses for long-running agents», 2025; agentpatterns.ai «Goal monitoring», 07.11.2026).
# Еволюція: кожне спрацювання диспетчер пише в журнал сесії → handoff_check вимагає вердикт у HOOK_JOURNAL.md (справжнє · хибне · дубль · пропуск);
#   поріг «3 звіти» — ROUTE_EVERY (змінна середовища), маркер блоку — ROUTE_MARK (типово «Маршрут»).
# Зуби: bash route-remind.sh selftest.
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN
python3 - "$mode" <<'PY'
import json, os, re, sys, glob, pathlib
EVERY = int(os.environ.get('ROUTE_EVERY') or 3)
MARK = re.compile(r"(\*\*|^|\n)\s*" + re.escape(os.environ.get('ROUTE_MARK') or 'Маршрут') + r"\s*[:*]", re.I)
ASK = re.compile(r"(?<![\w'’])(маршрут(?!изац)\w*|куди (ми )?рухаємось|який план|нагадай (мені )?план|загуби\w*|що далі|де ми зараз)(?![\w'’])", re.I)

def reports(path):
    """Звіти агента: текст відповідей між повідомленнями людини, лише суттєві (≥ 400 знаків)."""
    out, cur = [], []
    try: lines = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception: return out
    for ln in lines:
        try: e = json.loads(ln)
        except Exception: continue
        m = e.get('message') or {}; role = m.get('role') or e.get('type')
        c = m.get('content')
        if role == 'user' and (isinstance(c, str) or (isinstance(c, list) and any(isinstance(x, dict) and x.get('type') == 'text' for x in c))):
            if cur: out.append('\n'.join(cur)); cur = []
        elif role == 'assistant' and isinstance(c, list):
            cur += [x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text']
    if cur: out.append('\n'.join(cur))
    return [r for r in out if len(r) >= 400]

def route_text(cwd):
    roots = [pathlib.Path(cwd or '.')]
    roots += [p for p in roots[0].parent.iterdir() if p.is_dir()] if roots[0].parent.exists() else []
    files = []
    for r in roots:
        for g in ('docs/summary/*SUMMARY*.md', 'sessions/**/*summary*.md'):
            files += [pathlib.Path(f) for f in glob.glob(str(r / g), recursive=True)]
    if not files: return None, None
    f = max(files, key=lambda x: x.stat().st_mtime)
    t = f.read_text(encoding='utf-8', errors='ignore')
    i = t.find('МАРШРУТ')
    if i < 0: return str(f), None
    j = t.find('\n**0.', i + 10); k = t.find('\n## ', i + 10)
    end = min(x for x in (j, k, i + 1200) if x > 0)
    return str(f), t[t.rfind('\n', 0, i) + 1:end].strip()

def run(d, rep=None, src=None):
    rep = reports(d.get('transcript_path') or '') if rep is None else [r for r in rep if len(r) >= 400]
    asked = bool(ASK.search(d.get('prompt') or ''))
    last = rep[-EVERY:]
    shown_recent = any(MARK.search(r) for r in rep[-2:])
    if rep and not asked and (shown_recent or len(last) < EVERY or any(MARK.search(r) for r in last)): return None
    why = 'Konst питає про маршрут' if asked else ('перша відповідь сесії' if not rep else f'у {EVERY} останніх звітах блоку «Маршрут» нема')
    f, rt = route_text(d.get('cwd')) if src is None else src
    body = (f"Маршрут для Konst ({why}): у цій відповіді — блок «**Маршрут:**» 3–5 рядків: де ми (пункт черги й крок) · далі (1–3 кроки) · попутно · що чекає Konst. "
            "Бери з самері §0 і черги репо, не з пам'яті чату; змінилось — спершу онови самері §0, тоді показуй.")
    if f: body += f" Самері: {f}."
    if rt: body += "\nЗ самері зараз:\n" + rt[:1200]
    return body

def selftest():
    R = 'x' * 450
    cases = [('перша відповідь сесії → нагадування', {'prompt': 'роби далі'}, [], True),
             ('маршрут був в останньому звіті → тиша', {'prompt': 'роби далі'}, [R, R, R + '\n**Маршрут:** де ми'], False),
             ('три звіти без маршруту → нагадування', {'prompt': 'роби далі'}, [R + '\n**Маршрут:** a', R, R, R], True),
             ('лише два звіти без маршруту після показу → тиша', {'prompt': 'ок'}, [R + '\n**Маршрут:** a', R, R], False),
             ('Konst питає «куди рухаємось» → нагадування навіть одразу після показу', {'prompt': 'нагадай, куди рухаємось?'}, [R + '\n**Маршрут:** a'], True),
             ('«я загубився в брифах» → нагадування', {'prompt': 'я вже трішки загубився в брифах'}, [R + '\n**Маршрут:** a'], True),
             ('«маршрутизація» в коді — не питання про план → тиша', {'prompt': 'поправ маршрутизацію запитів'}, [R + '\n**Маршрут:** a'], False),
             ('короткі відповіді (< 400) не рахуються як звіти → тиша', {'prompt': 'так'}, [R + '\n**Маршрут:** a'] + ['ок'] * 5, False)]
    bad = 0
    for name, d, rep, want in cases:
        got = run(d, rep, (None, None)) is not None; ok = got == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    # витяг маршруту з самері — на тимчасовому репо
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp()) / 'repo'; (tmp / 'docs/summary').mkdir(parents=True)
    (tmp / 'docs/summary/X_SUMMARY_2026-11-07.md').write_text('## §0\n\n**0.1 · ДЕ МИ:** тут\n\n**0.2 · МАРШРУТ (S2 →):**\n  1. Крок один.\n  2. Крок два.\n\n**0.3 · ВІД KONST:** ...\n', encoding='utf-8')
    f, rt = route_text(str(tmp)); ok = bool(rt) and 'Крок два' in rt and 'ВІД KONST' not in rt; bad += not ok
    print(('✓ ' if ok else '✗ ') + 'маршрут береться з самері §0.2 (до наступного пункту §0)')
    print(f'─── route-remind selftest: {len(cases) + 1 - bad}/{len(cases) + 1} ───'); return 1 if bad else 0

if sys.argv[1] == 'selftest': sys.exit(selftest())
try: out = run(json.loads(os.environ.get('HOOK_IN') or '{}'))
except Exception: out = None
if out: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': out}}, ensure_ascii=False))
PY
