#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-I крок 2 — К4-1: rules_hits.py вливається в Lens_validate.py як G19.
   Живе доки: коміт із цією правкою в main (разовий → archive/scripts).
   12.16: правка за унікальними якорями, не переписуванням файлу в контексті.
   12.11: дім коду гейта — Lens_validate.py; окремий скрипт після влиття видаляється.
"""
import sys, os, hashlib

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
P = os.path.join(ROOT, 'kernel/Lens_validate.py')

# ── 1 · шапка: оголосити G16 (був у коді, не в docstring) і G19 ──────────────
A1_OLD = """         Для дубля додатково називає, ХТО на нього посилається ззовні

  python3 Lens_validate.py --html <file.html>"""
A1_NEW = """         Для дубля додатково називає, ХТО на нього посилається ззовні
      G16 правило без детектора (К2) і без маркера K2:n/a
      G19 спрацювання правил: правило з нулем згадок у самері й без сліду
         народження — кандидат на виселення (К4-1). Живі самері лежать у
         Project, не в репо — тому тека з ними додається: --gov . --live <тека>

  python3 Lens_validate.py --html <file.html>"""

# ── 2 · тіло G19 + помічники, перед секцією HTML ─────────────────────────────
A2_OLD = """# ────────────────────────────────── HTML ──────────────────────────────────
"""
A2_NEW = '''# ─────────────────────────── G19 · СПРАЦЮВАННЯ ПРАВИЛ ───────────────────────
# К4-1. Три рішення, на яких тримається чесність числа (перенесено з
# rules_hits.py разом з кодом — без них число бреше):
#   1. ПОРЯДОК СЕСІЙ береться з ОГОЛОШЕННЯ (Lens_ARCHIVE_INDEX.md), а не з дати
#      файлу чи алфавіту: дати губляться при Sync у Project, алфавіт ставить
#      b27 перед b9 (Lens_INDEX §5).
#   2. ЗБІГ СТРОГИЙ + ВИМОГА КОНТЕКСТУ: `12.16`, wsd 1.9, §2.4 — так; голе
#      число в прозі («2.4 KB», «v2.34») — ні. Без вимоги контексту замір дав
#      2 нулі замість 12, тобто 10 хибних ✓ (1.15 пастка 1).
#   3. НАРОДЖЕННЯ ≠ СПРАЦЮВАННЯ: правило, влите вчора, має нуль за визначенням.
#      Слід народження — **N.N** у таблиці злиття самері.
#
# ЧОМУ ⚠, А НЕ ✗ (відхилення від дослівної К2 в rules_hits.py, назване вголос):
#   вирок «виселити» виносить людина, і закрити ці нулі одним ходом неможливо —
#   це робота К3-1. Вісім незакриваних ✗ дали б рівно те, від чого застерігає
#   G3-1: червоне, на яке немає дії, вчить ігнорувати червоне.

_CTX = r'(?:`|wsd\\s+|gov\\s+|§|\\bп\\.\\s?|\\(|правил\\w*\\s+)'


def _rule_pat(rid):
    """Строгий якір номера правила з вимогою контексту посилання."""
    tail = r'(?![\\d.])' if '-' in rid else r'(?![\\d.\\-])'
    return re.compile(_CTX + re.escape(rid) + tail)


def _rule_ids(path, kind):
    try:
        t = open(path, encoding='utf-8').read()
    except OSError:
        return []
    return [(m.group(1), kind) for m in
            re.finditer(r'^##+\\s+`?(\\d+\\.\\d+(?:-[а-яґєіїь])?)`?[\\s|]', t, re.M)]


def _declared_order(root):
    """Порядок сесій = порядок рядків реєстру в ARCHIVE_INDEX (оголошення, не здогад)."""
    try:
        t = open(R(root, 'Lens_ARCHIVE_INDEX.md'), encoding='utf-8').read()
    except OSError:
        return []
    names = []
    for m in re.finditer(r'^- `([^`]+\\.md)`', t, re.M):
        if m.group(1) not in names:
            names.append(m.group(1))
    return names


def g19(root):
    print('\\n[G19] спрацювання правил — нуль згадок без сліду народження (К4-1)')
    R_ = _rule_ids(R(root, 'Work_Standard.md'), 'wsd') + \\
         _rule_ids(R(root, 'Lens_governance_protocol.md'), 'gov')
    seen, RU = set(), []
    for r_, k in R_:
        if r_ not in seen:
            seen.add(r_); RU.append((r_, k))
    if not RU:
        warn('файлів правил не знайдено — G19 не виконався, це НЕ зелений результат')
        return

    found = {}
    base = os.path.join(root, 'archive', 'summaries')
    for dp, _, fns in os.walk(base):
        for n in fns:
            if n.endswith('.md'):
                found[n] = os.path.join(dp, n)
    order = _declared_order(root)
    docs = [(n, open(found[n], encoding='utf-8').read()) for n in order if n in found]
    undeclared = sorted(set(found) - set(order))
    for d in LIVE_DIRS:
        if not os.path.isdir(d):
            warn(f'--live: теки немає — {d}')
            continue
        for n in sorted(os.listdir(d)):
            if n.endswith('.md'):
                docs.append((n + ' [live]', open(os.path.join(d, n), encoding='utf-8').read()))
    if not docs:
        warn('корпусу самері не знайдено (archive/summaries порожня, --live не дано) — '
             'G19 не виконався, це НЕ зелений результат')
        return

    zeros, born_zeros = [], []
    for rid, kind in RU:
        p = _rule_pat(rid)
        if any(p.search(t) for _, t in docs):
            continue
        bp = re.compile(r'\\*\\*' + re.escape(rid) + r'\\*\\*')
        (born_zeros if any(bp.search(t) for _, t in docs) else zeros).append(f'{rid}({kind})')

    print(f'  правил {len(RU)} · самері в підрахунку {len(docs)}'
          + (f' (+{len(LIVE_DIRS)} тек живих)' if LIVE_DIRS else ''))
    if undeclared:
        warn(f'{len(undeclared)} самері в archive/ не названі в ARCHIVE_INDEX — '
             f'у підрахунок НЕ ввійшли (IDX-13)')
    if born_zeros:
        print(f'  народжені, спрацювати ще не встигли ({len(born_zeros)}): '
              f'{" ".join(born_zeros)}')
    if zeros:
        warn(f'{len(zeros)} з {len(RU)} правил без жодного сліду — кандидати на '
             f'виселення (К3-1): {" ".join(zeros)}')
    else:
        ok(f'усі {len(RU)} правил мають слід у корпусі самері')
    if not LIVE_DIRS:
        print('  ⓘ живі самері (Project) не додані: правило, що спрацювало лише в '
              'останніх сесіях, читається тут як 0. Додати: --live <тека>')


# ────────────────────────────────── HTML ──────────────────────────────────
'''

# ── 3 · виклик G19 у кінці gov() ────────────────────────────────────────────
A3_OLD = """    if not seen_rule_file:
        warn('жодного файлу правил не знайдено — гейт не виконався '
             '(дзеркало неповне?), це НЕ зелений результат')
"""
A3_NEW = """    if not seen_rule_file:
        warn('жодного файлу правил не знайдено — гейт не виконався '
             '(дзеркало неповне?), це НЕ зелений результат')

    g19(root)
"""

# ── 4 · --live у main() ─────────────────────────────────────────────────────
A4_OLD = """    if sys.argv[1] == '--gov':
        gov(sys.argv[2] if len(sys.argv) > 2 else '.')"""
A4_NEW = """    if sys.argv[1] == '--gov':
        args = sys.argv[2:]
        while '--live' in args:
            i = args.index('--live')
            if i + 1 >= len(args):
                print('--live потребує теки'); sys.exit(2)
            LIVE_DIRS.append(args[i + 1]); del args[i:i + 2]
        gov(args[0] if args else '.')"""

# ── 5 · глобал LIVE_DIRS ────────────────────────────────────────────────────
A5_OLD = "SIGNAL_KB, RED_KB = 120, 200\n"
A5_NEW = "SIGNAL_KB, RED_KB = 120, 200\nLIVE_DIRS = []          # теки живих самері (Project) для G19 — --live\n"

PATCHES = [('шапка G16+G19', A1_OLD, A1_NEW), ('тіло g19()', A2_OLD, A2_NEW),
           ('виклик у gov()', A3_OLD, A3_NEW), ('--live у main()', A4_OLD, A4_NEW),
           ('глобал LIVE_DIRS', A5_OLD, A5_NEW)]

txt = open(P, encoding='utf-8').read()
before = len(txt.encode())
for name, old, new in PATCHES:
    n = txt.count(old)
    if n != 1:
        print(f'✗ якір «{name}» не унікальний: count={n}'); sys.exit(1)
    txt = txt.replace(old, new)
    print(f'  ✓ {name}')
open(P, 'w', encoding='utf-8').write(txt)
print(f'{before} → {len(txt.encode())} B · md5 {hashlib.md5(txt.encode()).hexdigest()}')

rh = os.path.join(ROOT, 'kernel/rules_hits.py')
if os.path.exists(rh):
    os.remove(rh)
    print('  ✓ kernel/rules_hits.py видалено (дім коду гейта — Lens_validate.py, 12.11)')
print('✓ патч застосовано')
