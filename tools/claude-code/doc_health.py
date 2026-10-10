#!/usr/bin/env python3
# живе доки: агент Claude Code читає канон ядра й продуктів. Дім — lens-governance:tools/claude-code/ (бриф DOC-1, «так» Konst 10.10.2026, QR CC-7).
"""Здоров'я документів — скільки коштує їх ЧИТАТИ в Claude Code (не цілісність канону: її тримає гейт kernel/Lens_validate.py).
Мірки (замінили G6 «120 / 200 КБ» Project-епохи, взяті без заміру):
  M1 щосесійне — CLAUDE.md кореня і профіль (tools/claude-code/PROFILE.md) ≤ 200 рядків (code.claude.com/docs/en/memory, 10.10.2026)
  M2 старт цілком — черга (*_CHERGA.md) і живі самері (sessions/*summary*.md) ≤ 25 КБ           (число агента — звірити на 2–3 сесіях)
  M3 розділ (## / #) ≤ 16 КБ ≈ 5 тис. токенів — точкове читання платить за розділ               (число агента — звірити на 2–3 сесіях)
  M4 файл > 80 КБ — лише з «читається коли» в шапці: одним Read його не взяти (ліміт 25 тис. токенів ≈ 80–100 КБ укр. тексту, замір 10.10)
Лише ⚠ (не блокує): один рядок для env_check; адреси — --list.
  python3 doc_health.py [<репо>] [--list] | selftest
"""
import os, re, subprocess, sys, tempfile

M1_LINES, M2_KB, M3_KB, M4_KB = 200, 25, 16, 80


def files(root):
    out = subprocess.run(['git', 'ls-files', '*.md'], cwd=root, capture_output=True, text=True).stdout.split()
    return [f for f in out if not f.startswith('archive/')]


def scan(root):
    found = []   # (мірка, файл, що)
    for f in files(root):
        p = os.path.join(root, f)
        if not os.path.isfile(p): continue
        txt = open(p, encoding='utf-8', errors='replace').read(); kb = len(txt.encode()) / 1024
        if f in ('CLAUDE.md', 'tools/claude-code/PROFILE.md'):
            n = txt.count('\n') + 1
            if n > M1_LINES: found.append(('M1', f, f'{n} рядків > {M1_LINES}'))
        whole = f in ('CLAUDE.md', 'tools/claude-code/PROFILE.md') or bool(re.search(r'_CHERGA\.md$', f)) or (f.startswith('sessions/') and 'summary' in f)
        if whole and f not in ('CLAUDE.md', 'tools/claude-code/PROFILE.md') and kb > M2_KB:
            found.append(('M2', f, f'{kb:.0f} КБ > {M2_KB} — читається цілком на старті'))
        if whole: continue   # читається цілком за задумом — розмір розділу не важить, стережуть M1/M2 (перший прогін 10.10: профіль і черга — 2 хибних M3)
        for s in re.split(r'(?m)^(?=#{1,2} )', txt):
            sk = len(s.encode()) / 1024
            if sk > M3_KB and s.lstrip().startswith('#'):
                found.append(('M3', f, f'розділ {sk:.0f} КБ «{s.splitlines()[0][:60].strip()}»'))
        if kb > M4_KB and 'читається' not in '\n'.join(txt.splitlines()[:12]).lower():
            found.append(('M4', f, f'{kb:.0f} КБ без «читається коли» — одним Read не взяти'))
    return found


def line(root):
    f = scan(root)
    if not f: return '✓', f'документи: ✓ щосесійні ≤ {M1_LINES} рядків · старт ≤ {M2_KB} КБ · розділи ≤ {M3_KB} КБ · великі з маршрутом'
    by = {}
    for m, *_ in f: by[m] = by.get(m, 0) + 1
    name = {'M1': 'щосесійні задовгі', 'M2': 'файли старту завеликі', 'M3': f'розділів > {M3_KB} КБ', 'M4': f'> {M4_KB} КБ без маршруту'}
    worst = max((x for x in f if x[0] == 'M3'), key=lambda x: float(re.search(r'(\d+) КБ', x[2])[1]), default=None)
    return '⚠', 'документи: ' + ' · '.join(f'{name[m]} {n}' for m, n in sorted(by.items())) + (f' (найбільший — {worst[1]} {worst[2]})' if worst else '') + ' — деталі: doc_health.py --list'


def selftest():
    bad = 0
    def repo(fs):
        d = tempfile.mkdtemp(prefix='dh-'); subprocess.run(['git', 'init', '-q'], cwd=d, check=True)
        for f, t in fs.items():
            os.makedirs(os.path.dirname(os.path.join(d, f)) or d, exist_ok=True); open(os.path.join(d, f), 'w').write(t)
        subprocess.run(['git', 'add', '-A'], cwd=d, check=True); return d
    sec = lambda kb: '## Розділ\n' + 'х' * (kb * 512) + '\n'   # кирилиця — 2 байти на знак
    cases = [('чисте репо → ✓', {'CLAUDE.md': 'x\n' * 50, 'lens/A.md': sec(4)}, '✓', ''),
             ('CLAUDE.md 250 рядків → ⚠ M1', {'CLAUDE.md': 'x\n' * 250}, '⚠', 'щосесійні задовгі 1'),
             ('черга 30 КБ → ⚠ M2', {'lens/P_CHERGA.md': sec(30)}, '⚠', 'файли старту завеликі 1'),
             ('розділ 20 КБ → ⚠ M3', {'lens/B.md': sec(20)}, '⚠', 'розділів > 16 КБ 1'),
             ('файл 90 КБ без маршруту (розділи малі) → ⚠ M4', {'lens/C.md': ''.join(sec(9) for _ in range(10))}, '⚠', '> 80 КБ без маршруту 1'),
             ('файл 90 КБ з «Читається ТОЧКОВО» → ✓', {'lens/C.md': '> Читається ТОЧКОВО\n' + ''.join(sec(9) for _ in range(10))}, '✓', ''),
             ('профіль 18 КБ одним розділом (читається цілком) → ✓, не M3', {'tools/claude-code/PROFILE.md': sec(18)}, '✓', ''),
             ('архів не рахується → ✓', {'archive/X_CHERGA.md': sec(40)}, '✓', '')]
    for name, fs, want, part in cases:
        g, t = line(repo(fs)); ok = g == want and part in t
        print(('✓' if ok else '✗') + ' ' + name + ('' if ok else f' → {t}')); bad += not ok
    print(f'selftest: {len(cases) - bad}/{len(cases)}'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'selftest': sys.exit(selftest())
    root = a[0] if a and not a[0].startswith('--') else '.'
    if '--list' in a:
        for m, f, w in scan(root): print(f'{m} {f} — {w}')
    g, t = line(root); print((g + ' ' if g == '⚠' else '') + t)
