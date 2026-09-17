#!/usr/bin/env python3
# живе доки: група Б1 влита і пушена (read-back ✓) — далі архів G-B2
# G-B2 · Крок 1 · Б1: Г-9 → §8.11 · Д-Ж → §8.13 · Д-М → §8.18 (тіла дослівно з GB2_groupB1_texts_v1.md, 12.16)
# usage: python3 gb2_step1B1_merge_v1.py <kernel_dir> <texts_md>
# exit: 0 = влито або no-op · 2 = стоп (нічого не записано)
import re, sys, os

kdir, tpath = sys.argv[1], sys.argv[2]
MP = os.path.join(kdir, 'Lens_stagebench_manifest.md')
BP = os.path.join(kdir, 'Lens_stagebench_delta_running.md')
m = open(MP, encoding='utf-8').read()
b = open(BP, encoding='utf-8').read()
t = open(tpath, encoding='utf-8').read()

def stop(msg):
    print('✗ СТОП:', msg); sys.exit(2)

# (номер, запис буфера, якір вставки або None = кінець)
PLAN = [('8.11', 'Г-9', '### 8.12 '), ('8.13', 'Д-Ж', '### 8.14 '), ('8.18', 'Д-М', None)]

have = [n for n, _, _ in PLAN if re.search(r'^### ' + re.escape(n) + r' ', m, re.M)]
gone = [k for _, k, _ in PLAN if not re.search(r'^## ' + k + r' ·', b, re.M)]
if len(have) == 3 and len(gone) == 3:
    print('· група Б1 уже влита (no-op)'); sys.exit(0)
if have or gone:
    stop(f'часткове вливання: у manifest є {have}, з буфера зникли {gone}')

# тіла з файлу текстів: від '### N ' до роздільника '\n---\n' або кінця
def body(n):
    hits = [x.start() for x in re.finditer(r'^### ' + re.escape(n) + r' ', t, re.M)]
    if len(hits) != 1: stop(f'у текстах «### {n}» = {len(hits)}')
    s = hits[0]; e = t.find('\n---\n', s)
    return t[s:(e if e != -1 else len(t))].rstrip('\n') + '\n'

for n, k, anchor in PLAN:
    blk = body(n)
    if anchor is None:
        m = m.rstrip('\n') + '\n\n' + blk
    else:
        c = len(re.findall(r'^' + re.escape(anchor), m, re.M))
        if c != 1: stop(f'якір «{anchor}» = {c}')
        i = re.search(r'^' + re.escape(anchor), m, re.M).start()
        m = m[:i] + blk + '\n' + m[i:]

# буфер: секція від '## K ·' до наступного '## ' або кінця
lot = re.search(r'\*\*ЛОТОК: (\d+) запис\(ів\)\.\*\*', b)
if not lot or lot.group(1) != '9': stop(f'ЛОТОК ≠ 9 ({lot.group(1) if lot else None})')
for _, k, _ in PLAN:
    hs = [x.start() for x in re.finditer(r'^## ' + k + r' ·', b, re.M)]
    if len(hs) != 1: stop(f'секція буфера {k} = {len(hs)}')
    s = hs[0]; nx = re.search(r'^## ', b[s + 3:], re.M)
    e = s + 3 + nx.start() if nx else len(b)
    b = b[:s] + b[e:]
b = re.sub(r'(\n---\n)+\s*$', '\n', b.rstrip('\n') + '\n')  # висячий роздільник у кінці
b = b.replace('**ЛОТОК: 9 запис(ів).**',
              '**ЛОТОК: 6 запис(ів).** *(G-B2 17.09.2026: група Б1 — Г-9 · Д-Ж · Д-М — влита в manifest §8.11 · §8.13 · §8.18)*', 1)

heads = [h for h in re.findall(r'^##\s+(.+)$', b, re.M) if not h.lstrip().startswith(('✅', '🟡', '⚠'))]
if len(heads) != 6: stop(f'після зняття записів {len(heads)}, очікувано 6')

open(MP, 'w', encoding='utf-8').write(m)
open(BP, 'w', encoding='utf-8').write(b)
print('✓ влито: Г-9→§8.11, Д-Ж→§8.13, Д-М→§8.18')
print('✓ ЛОТОК 9→6')
