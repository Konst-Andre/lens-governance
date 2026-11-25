#!/usr/bin/env python3
# живе доки: є реєстр відхилених 💡 `tools/claude-code/REJECTED_IDEAS.md`. Дім — lens-governance:tools/claude-code/hooks/ (EquipLens S45, 25.11.2026).
"""rejected-guard — «💡 Пропоную» не повертає відхилене Konst (подія Stop).

Чому: 💡 «обмежити іспит» з'явилась удруге (23.11 і 25.11) — відхилене жило лише в самері, машина його не бачила
(журнал гачків, «пропуск Konst» 25.11). Тепер реєстр — таблиця `tools/claude-code/REJECTED_IDEAS.md`, гачок звіряє з нею блок 💡.

Подія Stop (last_assistant_message, transcript нема потреби): блок від «💡 Пропоную» до рядка «пам'ять:» (або до кінця) →
кожен рядок реєстру: усі групи ключів (` + `) знайдено в блоці (варіант групи — `|`, основа слова, регістр не важить) →
block з цитатою Konst. Тиша: настала дата «переглянути» · у блоці є «реєстр відхилених: переглянуто» · той самий звіт удруге
(позначка /tmp/lens-rejected-<сесія>, щоб не зациклити; stop_hook_active не годиться — першим міг блокувати інший гачок Stop).
Реєстру нема чи помилка розбору — тиша (stderr — у журнал помилок диспетчера).

Запуск:  python3 rejected-guard.py stop < hook.json   → {"decision":"block","reason":…} або нічого
         python3 rejected-guard.py selftest           (REJ_INJECT=1 — суд «завжди мовчить», selftest має почервоніти)
"""
import datetime, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.environ.get('LENS_REJECTED') or os.path.join(os.path.dirname(HERE), 'REJECTED_IDEAS.md')
IDEA = re.compile(r'💡\s*\**\s*Пропоную(.*?)(?=\n\s*(?:пам.ять:|- `[█▏▎▍▌▋▊▉ ])|\Z)', re.S)   # кінець — «пам'ять:» або плашка маркера; «- `id`» пункту 💡 — не кінець
REVIEWED = re.compile(r'реєстр відхилених:\s*переглянуто', re.I)


def rows(path=REG):
    out = []
    try: txt = open(path, encoding='utf-8').read()
    except OSError: return out
    for ln in txt.splitlines():
        if not ln.startswith('| `'): continue
        c = [x.strip() for x in re.split(r'(?<!\\)\|', ln.strip().strip('|'))]
        if len(c) < 4: continue
        keys = c[0].strip('`').replace('\\|', '|')
        groups = [[v.strip().lower() for v in g.split('|') if v.strip()] for g in keys.split(' + ')]
        d = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', c[3])
        out.append({'groups': groups, 'idea': c[1], 'konst': c[2], 'review': datetime.date(int(d.group(3)), int(d.group(2)), int(d.group(1))) if d else None})
    return out


def judge(msg, reg, today=None):
    """→ рядок реєстру, з яким збіглась 💡, або None."""
    if os.environ.get('REJ_INJECT') == '1': return None
    m = IDEA.search(msg or '')
    if not m or REVIEWED.search(m.group(1)): return None
    block = m.group(1).lower(); today = today or datetime.date.today()
    for r in reg:
        if r['review'] and today >= r['review']: continue
        if r['groups'] and all(any(v in block for v in g) for g in r['groups']): return r
    return None


def stop(d, reg=None):
    msg = d.get('last_assistant_message') or ''
    r = judge(msg, rows() if reg is None else reg)
    if not r: return None
    mk = os.path.join(os.environ.get('LENS_MARK_DIR') or '/tmp', f"lens-rejected-{d.get('session_id') or 'nosession'}")
    h = hashlib.sha1(msg.encode()).hexdigest()[:12]
    try:
        if open(mk).read().strip() == h: return None
    except OSError: pass
    try: open(mk, 'w').write(h)
    except OSError: pass
    return (f"«💡 Пропоную» повторює відхилене Konst: {r['idea']}. Його слова: {r['konst']}. "
            "Прибери цю 💡 зі звіту. Якщо щось справді змінилось — допиши в неї «реєстр відхилених: переглянуто — <що змінилось>»; "
            "рішення лишається за Konst (реєстр — tools/claude-code/REJECTED_IDEAS.md). Хибне спрацювання — рядок «rejected-guard … хибне» в журналі гачків.")


def selftest():
    import tempfile, shutil
    md = tempfile.mkdtemp(prefix='rej_'); os.environ['LENS_MARK_DIR'] = md
    reg = rows()
    exam = [r for r in reg if any('іспит' in g for g in r['groups'])]
    day = datetime.date(2026, 11, 25)
    R = lambda t: 'Звіт.\n\n💡 Пропоную\n- ' + t + '\n\nпам\'ять: abc1234 (самері §0)\n'
    cases = [
        ('реєстр читається: ≥ 2 рядки, у кожного групи ключів і дата перегляду', len(reg) >= 2 and all(r['groups'] and r['review'] for r in reg)),
        ('ключі з `\\|` у таблиці розібрано на варіанти', any(len(g) > 1 for r in reg for g in r['groups'])),
        ('«обмежити іспит до 3 прогонів» → збіг (повтор 25.11)', judge(R('обмежити іспит до 3 прогонів — дешевше'), reg, day) is not None),
        ('«Іспит звузити» (регістр, інший порядок) → збіг', judge(R('Іспит звузити до §0'), reg, day) is not None),
        ('інша 💡 про іспит → тиша', judge(R('іспит на кінцевому HEAD — до справжніх 0'), reg, day) is None),
        ('слова поза блоком 💡 → тиша', judge('Звіт: Konst відхилив «обмежити іспит».\n\n💡 Пропоную\n- реєстр гачків\n', reg, day) is None),
        ('«реєстр відхилених: переглянуто — …» → тиша', judge(R('обмежити іспит; реєстр відхилених: переглянуто — ціна зросла вдесятеро'), reg, day) is None),
        ('настала дата перегляду → тиша', judge(R('обмежити іспит'), reg, datetime.date(2027, 3, 2)) is None),
        ('звіт без 💡 → тиша', judge('Звіт без пропозицій.', reg, day) is None),
        ('жирне «💡 **Пропоную:**» → теж судиться', judge('Звіт.\n\n💡 **Пропоную:** обмежити іспит\n', reg, day) is not None),
        ('пункт 💡 з «- `id`» не обриває блок → збіг далі', judge('Звіт.\n\n💡 Пропоную\n- `ROUTE-5` швидше\n- обмежити іспит\n\nпам\'ять: x\n', reg, day) is not None),
        ('плашка маркера після 💡 — кінець блоку', judge('💡 Пропоную\n- реєстр\n\n- `████   87%` контекст — обмежити іспит\n', reg, day) is None),
    ]
    d = {'session_id': 'rt', 'last_assistant_message': R('обмежити іспит до 3 прогонів')}
    if exam:
        first = stop(d, exam); second = stop(d, exam)
        cases.append(('stop: block з цитатою Konst, удруге той самий звіт → тиша', first is not None and 'Konst' in first and second is None))
    bad = 0
    for n, ok in cases: bad += not ok; print(('✓ ' if ok else '✗ ') + n)
    shutil.rmtree(md, ignore_errors=True)
    print(f'─── rejected-guard selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']: sys.exit(selftest())
    if a[:1] == ['stop']:
        try: r = stop(json.loads(sys.stdin.read() or '{}'))
        except Exception: __import__('traceback').print_exc(); r = None
        if r: print(json.dumps({'decision': 'block', 'reason': r}, ensure_ascii=False))
        sys.exit(0)
    print(__doc__); sys.exit(2)
