#!/usr/bin/env python3
# cookbook_check.py — кукбук звіряє сам себе й ядро; лише читає. Запуск з кореня ядра: python3 tools/claude-code/cookbook_check.py [--quiet] [корінь]
# живе доки: кукбук ядра має індекс §3 і номери A / B / T. Народився з чернетки FAB-1 (sessions/FAB-1/FAB-1_cookbook.md §7), ставка K6
# прийнята Konst 18.11.2026; у env_check ядра — рядком ⚠ / ✗ (прогін ≈ 0,06 с, замір 18.11.2026). Практика — CI звіряє механічне
# (покажчики, мапи), прозу пише людина (ADR eslint-plugin-vite 0002; ggen toc.yml — «fail CI if out of date»; 18.11.2026).
# Перевіряє: (3) мапа §3 ↔ заголовки томів (✗) · запис, якого індекс не згадує (⚠) · (4) номери wsd → дім сьогодні (⚠ — заголовка нема; ⓘ — живе не у wsd)
#   · (5) файли-джерела, яких у репо нема (ⓘ, число — FAB-1 Н1, борг) · (6) мітки «pending / не перевірено» (ⓘ, число).
# Не перевіряє (свідомо): шапку «Записи тому» і вагу тому в індексі — обидві прибрано з тексту 18.11.2026 (брехали; мапу тримає §3).
# --quiet — лише ⚠ / ✗ і підсумок (для env_check). Вихід 1, коли є ✗.
import glob, os, re, subprocess, sys
QUIET = '--quiet' in sys.argv
args = [x for x in sys.argv[1:] if x != '--quiet']
root = args[0] if args else '.'
cb = os.path.join(root, 'kernel/cookbook')
vols = {v: f for f in sorted(glob.glob(cb + '/Lens_*cookbook_[1-6]_*.md')) for v in [re.search(r'_(\d)_', f).group(1)]}
bad = warn = 0
def info(text):
    if not QUIET: print('ⓘ', text)
def out(mark, text):
    global bad, warn
    bad += mark == '✗'; warn += mark == '⚠'; print(mark, text)
heads = {}                                   # номер → (том, рядок)
for v, f in vols.items():
    L = open(f, encoding='utf-8').read().split('\n')
    mine = []
    for i, l in enumerate(L, 1):
        m = re.match(r'^#{2,3}\s+((?:A|B|T)\d+(?:\.\d+)?(?:-б)?)[. ·]', l) or re.match(r'^\*\*((?:A|B)\d+\.\d+)\.', l)
        if m: heads[m.group(1)] = (v, i); mine.append(m.group(1))
I = open(cb + '/Lens_cookbook_INDEX.md', encoding='utf-8').read().split('\n')
idx = {}
for i, l in enumerate(I, 1):                 # 3. мапа §3 ↔ заголовки
    m = re.match(r'^\| `((?:A|B|T)[\d.]+)` \|.*\| \*\*(\d)\*\* \|$', l)
    if m: idx[m.group(1)] = (m.group(2), i)
for k, (v, i) in idx.items():
    if k not in heads: out('✗', f'індекс:{i} → {k}: заголовка нема в жодному томі')
    elif heads[k][0] != v: out('✗', f'індекс:{i} → {k}: том {v}, а лежить у томі {heads[k][0]}')
whole = '\n'.join(I)
for k, (v, i) in heads.items():
    if k not in idx and not re.search(r'`' + re.escape(k) + r'[`\s(]', whole): out('⚠', f'{k} (том {v}:{i}) — індекс не згадує ніде')
wsd = {}                                     # 4. номери wsd → де вони сьогодні
for f in glob.glob(root + '/kernel/wsd/*.md') + [root + '/kernel/Lens_excel_protocol.md']:
    for l in open(f, encoding='utf-8'):
        m = re.match(r'^## (\d{1,2}\.\d{1,2}(?:-[а-я])?) ', l)
        if m: wsd.setdefault(m.group(1), []).append(os.path.basename(f))
cited = {}
files = sorted(glob.glob(cb + '/*.md'))
for f in files:
    for i, l in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'(?:wsd|Work_Standard\.md`?) (\d{1,2}\.\d{1,2}|Д-\d+)', l): cited.setdefault(m.group(1), []).append(f'{os.path.basename(f)[5:19]}:{i}')
for n in sorted(cited, key=lambda s: [int(t) for t in re.findall(r'\d+', s)]):
    homes = wsd.get(n, []); home = 'Work_Standard.md' if 'Work_Standard.md' in homes else (homes[0] if homes else None)
    if not home: out('⚠', f'wsd {n}: заголовка нема ({len(cited[n])} посилань, перше {cited[n][0]})')
    elif home != 'Work_Standard.md': info(f'wsd {n} живе в {home} ({len(cited[n])} посилань)')
tracked = {os.path.basename(p) for p in subprocess.run(['git', '-C', root, 'ls-files'], capture_output=True, text=True).stdout.split('\n')}
gone = {}                                    # 5. названі файли-джерела, яких у репо нема
for f in files:
    for i, l in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'(?<![:\w/])`?((?:QR_Lens|Drive_Lens|StockCheck|EquipLens|KPI_Lens|Lens)_[\w.]+\.(?:html|js|py|md))', l):
            if m.group(1) not in tracked: gone.setdefault(m.group(1), f'{os.path.basename(f)[5:19]}:{i}')
if gone: info(f'файлів-джерел поза репо (FAB-1 Н1, борг): {len(gone)} (напр. {", ".join(list(gone)[:3])})')
age = sum(len(re.findall(r'pending|Перевірити при|не перевірено', open(f, encoding='utf-8').read())) for f in files)
info(f'міток «pending / перевірити при / не перевірено»: {age}')   # 6. вік — лише число
print(f'кукбук: записів {len(heads)} · індекс §3 {len(idx)} · ✗ {bad} · ⚠ {warn}')
sys.exit(1 if bad else 0)
