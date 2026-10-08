#!/bin/bash
# живе доки: пам'ять сесії — лише репо (профіль Konst «ДЖЕРЕЛА ПРАВДИ»: факт, правило чи домовленість із чату — у репо в тому ж ході).
# Дім — lens-governance:tools/claude-code/hooks/ (HOOK-3, 08.10.2026; урок QR-Lens CC-4: хід із рішеннями Konst закінчено «пам'ять: нового нема» без коміту).
# Подія Stop (кінець ходу агента): в останньому повідомленні Konst є слова-рішення, а в цьому ході не було жодного коміту
# (git commit / gh_commit / push_files / create_or_update_file) → {"decision":"block"} з причиною: агент продовжує й записує або пояснює, чому нічого.
# Один раз на хід: stop_hook_active = true (агент уже продовжує через гачок) → тиша. Помилка розбору → тиша (гачок не ламає роботу).
# Формат — code.claude.com/docs/en/hooks «Stop» (stop_hook_active, transcript_path; decision/reason), 08.10.2026.
# Зуби: bash memory-guard.sh selftest — 4 випадки (рішення без коміту → block; з комітом → тиша; без рішень → тиша; повтор → тиша).
mode="${1:-stop}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN
python3 - "$mode" <<'PY'
import json, re, sys, os, tempfile
CUE = re.compile(r"(?<![\w'’])(так|ні|згоден|згодна|дозволяю|приймаю|делегую|вирішуй|вирішив|вирішила|рішення|давай|поїхали|не треба|не потрібно|бери|роби)(?![\w'’])", re.I)
COMMIT = re.compile(r"\bgit\b[^\n;&|]*\bcommit\b|gh_commit|push_files|create_or_update_file")

def real_user(x):
    if x.get('type') != 'user' or x.get('isMeta') or x.get('isCompactSummary'): return None
    c = (x.get('message') or {}).get('content')
    if isinstance(c, str): t = c
    elif isinstance(c, list):
        if any(i.get('type') == 'tool_result' for i in c if isinstance(i, dict)): return None
        t = ' '.join(i.get('text', '') for i in c if isinstance(i, dict) and i.get('type') == 'text')
    else: return None
    t = t.strip()
    return None if not t or t.startswith('<') else t

def verdict(d):
    if d.get('stop_hook_active'): return None
    L = [json.loads(l) for l in open(os.path.expanduser(d['transcript_path']), encoding='utf-8') if l.strip()]
    idx = [i for i, x in enumerate(L) if real_user(x)]
    if not idx: return None
    u = real_user(L[idx[-1]])
    cues = sorted({m.group(1).lower() for m in CUE.finditer(u)})
    if not cues: return None
    for x in L[idx[-1] + 1:]:
        if x.get('type') != 'assistant': continue
        for i in (x.get('message') or {}).get('content') or []:
            if isinstance(i, dict) and i.get('type') == 'tool_use' and COMMIT.search(json.dumps(i.get('input') or {}, ensure_ascii=False) + ' ' + str(i.get('name'))):
                return None
    return ("Гачок пам'яті (HOOK-3): в останньому повідомленні Konst є слова-рішення (" + ', '.join(cues[:6]) + "), а в цьому ході не було коміту. "
            "Профіль Konst: факт, рішення чи домовленість із чату — у репо в тому ж ході (самері §0/§1, черга, дім знання) → коміт → рядок «пам'ять: <коміт>». "
            "Якщо нового справді нема (питання без рішення, «так» — не рішення) — одним рядком поясни це Konst і заверши хід.")

def selftest():
    def tr(msgs):
        f = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False, encoding='utf-8')
        for m in msgs: f.write(json.dumps(m, ensure_ascii=False) + '\n')
        f.close(); return f.name
    U = lambda t: {'type': 'user', 'message': {'content': t}}
    A = lambda cmd: {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': cmd}}]}}
    R = {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'content': 'ok'}]}}
    cases = [('рішення без коміту → block', [U('Так, згоден, прод не захищаємо'), A('ls'), R], False, True),
             ('рішення з комітом → тиша', [U('Дозволяю, поїхали'), A('cd x && git add -A && git commit -qm t'), R], False, False),
             ('без слів-рішень → тиша', [U('Що там зі збіркою?'), A('ls'), R], False, False),
             ('повтор (stop_hook_active) → тиша', [U('Так, згоден'), A('ls'), R], True, False),
             ('«так» усередині слова не рахується → тиша', [U('Таким чином дивлюсь'), A('ls')], False, False),
             ('сповіщення системи не є повідомленням Konst → тиша', [U('Так'), A('git commit -m a'), R, U('<task-notification>done</task-notification>')], False, False)]
    bad = 0
    for name, msgs, active, want in cases:
        got = verdict({'transcript_path': tr(msgs), 'stop_hook_active': active}) is not None
        print(('✓ ' if got == want else '✗ ') + name); bad += got != want
    print(f"─── memory-guard selftest: {len(cases) - bad}/{len(cases)} ───"); return bad

if sys.argv[1] == 'selftest': sys.exit(1 if selftest() else 0)
try:
    r = verdict(json.loads(os.environ.get('HOOK_IN') or '{}'))
    if r: print(json.dumps({'decision': 'block', 'reason': r}, ensure_ascii=False))
except Exception:
    pass
PY
