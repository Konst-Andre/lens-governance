#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""К4-1 · лічильник спрацювань правил. ВЛИТИЙ у Lens_validate.py як G19 (G-I, 18.09.2026).
   Живе доки: видалений руками на GitHub — П-GH1 забороняє видалення з чату.
   Дім коду гейта — Lens_validate.py (12.11). Цей файл більше не правити: правки
   тут у гейт не потрапляють. Режими --extra/--window/--loose/--full збережені
   як довідка; у гейті лишився один — --live.
   К2: правило з нулем спрацювань лишається в каноні без явного вироку → ✗.

   Три рішення, на яких тримається чесність числа:
   1. ПОРЯДОК СЕСІЙ береться з ОГОЛОШЕННЯ (`Lens_ARCHIVE_INDEX.md`, реєстр
      `archive/summaries/**`), а не з дати файлу чи алфавіту — дати губляться
      при завантаженні в Project, алфавіт ставить b27 перед b9 (`Lens_INDEX §5`).
   2. ЗБІГ СТРОГИЙ: `1.1` не рахує `1.15`, `11.1`, `18.09`; `12.1` не рахує
      `12.19` і не привласнює `12.1-б` (`1.15` пастка 3 · той самий дефект,
      що `G16-1`).
   3. СЛІПА ЗОНА НАЗВАНА: живі самері лежать у Project, не в репо. Правило,
      що спрацювало лише в останніх сесіях, тут читається як 0. Тому --extra."""
import re, os, sys, argparse

def rule_ids(path, kind):
    t = open(path, encoding='utf-8').read()
    return [(m.group(1), kind) for m in
            re.finditer(r'^##+\s+`?(\d+\.\d+(?:-[а-яґєіїь])?)`?[\s|]', t, re.M)]

CTX = r'(?:`|wsd\s+|gov\s+|§|\bп\.\s?|\(|правил\w*\s+)'
def pat(rid, strict=True):
    """Строгий якір номера правила. strict=True вимагає КОНТЕКСТУ посилання
       (`12.16`, wsd 1.9, §2.4) — голе число в прозі («2.4 KB», «v2.34»)
       спрацюванням не рахується (`1.15` пастка 1: хибний ✓ дорожчий за хибний ✗)."""
    tail = r'(?![\d.])' if '-' in rid else r'(?![\d.\-])'
    head = CTX if strict else r'(?<![\d.])'
    return re.compile(head + re.escape(rid) + tail)

def declared_order(root):
    """Порядок сесій = порядок рядків реєстру в ARCHIVE_INDEX (оголошення, не здогад)."""
    t = open(os.path.join(root, 'kernel/Lens_ARCHIVE_INDEX.md'), encoding='utf-8').read()
    names = []
    for m in re.finditer(r'^- `([^`]+\.md)`', t, re.M):
        if m.group(1) not in names: names.append(m.group(1))
    return names

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--extra', action='append', default=[], help='тека з живими самері (Project)')
    ap.add_argument('--window', type=int, default=0, help='рахувати лише N останніх сесій')
    ap.add_argument('--loose', action='store_true', help='без вимоги контексту (для звірки в обидва боки)')
    ap.add_argument('--full', action='store_true', help='показати всі правила, не лише нулі')
    a = ap.parse_args()

    R = rule_ids(os.path.join(a.root, 'kernel/wsd/Work_Standard.md'), 'wsd') + \
        rule_ids(os.path.join(a.root, 'kernel/wsd/Lens_governance_protocol.md'), 'gov')
    seen = set(); RU = []
    for r, k in R:
        if r not in seen: seen.add(r); RU.append((r, k))

    order = declared_order(a.root)
    docs = []                                    # (ім'я, текст) у порядку сесій
    base = os.path.join(a.root, 'archive/summaries')
    found = {}
    for dp, _, fns in os.walk(base):
        for n in fns:
            if n.endswith('.md'): found[n] = os.path.join(dp, n)
    for n in order:
        if n in found: docs.append((n, open(found[n], encoding='utf-8').read()))
    undeclared = sorted(set(found) - set(order))
    for d in a.extra:
        for n in sorted(os.listdir(d)):
            if n.endswith('.md'):
                docs.append((n + ' [live]', open(os.path.join(d, n), encoding='utf-8').read()))
    if a.window: docs = docs[-a.window:]

    rows = []
    for rid, kind in RU:
        p = pat(rid, not a.loose)
        hits = [(n, len(p.findall(t))) for n, t in docs]
        tot = sum(c for _, c in hits)
        files = [n for n, c in hits if c]
        # народження ≠ спрацювання: у таблицях злиття правило стоїть як **N.N**
        bp = re.compile(r'\*\*' + re.escape(rid) + r'\*\*')
        born = any(bp.search(t) for _, t in docs)
        rows.append((rid, kind, tot, len(files), files[-1] if files else '—', born))

    zeros = [r for r in rows if r[2] == 0]
    nz = [r for r in zeros if not r[5]]
    print(f'[К4-1] правил {len(RU)} (wsd {sum(1 for _,k in RU if k=="wsd")} · gov {sum(1 for _,k in RU if k=="gov")})'
          f' · самері в підрахунку {len(docs)}' + (f' (вікно {a.window})' if a.window else ''))
    if undeclared:
        print(f'  ⚠ {len(undeclared)} самері в archive/ не названі в ARCHIVE_INDEX — у підрахунок НЕ ввійшли (`IDX-13`)')
    print(f'  → спрацювало 0 разів: {len(zeros)} із {len(RU)}'
          f'  (з них щойно влиті, народження в таблиці злиття: {len(zeros)-len(nz)}'
          f' · без жодного сліду: {len(nz)})\n')
    show = rows if a.full else zeros
    print(f"{'правило':10s} {'дім':4s} {'згадок':>7s} {'самері':>7s}  {'влите':5s} останнє")
    for rid, kind, tot, nf, last, born in show:
        print(f'{rid:10s} {kind:4s} {tot:7d} {nf:7d}  {"так" if born else "—":5s} {last[:46]}')
    if not a.extra:
        print('\n⚠ живі самері (Project) у підрахунок не входять — правило, що спрацювало'
              '\n  лише в останніх сесіях, читається тут як 0. Додати: --extra <тека>')
    return 0

sys.exit(main())
