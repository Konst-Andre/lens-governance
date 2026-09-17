#!/usr/bin/env python3
# живе доки: група Б2 влита і пушена (read-back ✓) — далі архів G-B2
# G-B2 · Крок 1 · Б2: Д-В → пункт §8.10 · Д-Г → §6-а · Д-В2 → §6-б (тіла дослівно з GB2_groupB2_texts_v1.md, 12.16)
# usage: python3 gb2_step1B2_merge_v1.py <kernel_dir> <texts_md>   exit: 0 влито/no-op · 2 стоп
import re, sys, os
kdir, tpath = sys.argv[1], sys.argv[2]
MP = os.path.join(kdir, 'Lens_stagebench_manifest.md'); BP = os.path.join(kdir, 'Lens_stagebench_delta_running.md')
m = open(MP, encoding='utf-8').read(); b = open(BP, encoding='utf-8').read(); t = open(tpath, encoding='utf-8').read()
def stop(x): print('✗ СТОП:', x); sys.exit(2)

marks = {'Д-В': 'буфера `Д-В`,', 'Д-Г': '### §6-а. ', 'Д-В2': '### §6-б. '}
have = [k for k, s in marks.items() if s in m]
gone = [k for k in marks if not re.search(r'^## ' + k + r' ·', b, re.M)]
if len(have) == 3 and len(gone) == 3: print('· група Б2 уже влита (no-op)'); sys.exit(0)
if have or gone: stop(f'часткове вливання: у manifest {have}, з буфера зникли {gone}')

def cut(start_pat):
    hs = [x.start() for x in re.finditer(start_pat, t, re.M)]
    if len(hs) != 1: stop(f'у текстах «{start_pat}» = {len(hs)}')
    s = hs[0]; e = t.find('\n---\n', s)
    return t[s:(e if e != -1 else len(t))].strip('\n')

dv = cut(r'^<!-- БЛОК Д-В').split('\n', 1)[1].strip('\n')   # без рядка-коментаря
s6a = cut(r'^### §6-а\. '); s6b = cut(r'^### §6-б\. ')

# Д-В: у кінець списку §8.10
if len(re.findall(r'^### 8\.11 ', m, re.M)) != 1: stop('якір ### 8.11 ≠ 1')
i = re.search(r'^### 8\.11 ', m, re.M).start()
head = m[:i].rstrip('\n'); m = head + '\n' + dv + '\n\n' + m[i:]

# §6-а, §6-б: перед '---' над '## §7.'
if len(re.findall(r'^## §7\. ', m, re.M)) != 1: stop('якір ## §7. ≠ 1')
j = re.search(r'^## §7\. ', m, re.M).start()
k = m.rfind('\n---\n', 0, j); k6 = re.search(r'^## §6\. ', m, re.M).start()
if not (k6 < k < j): stop('роздільник --- у кінці §6 не знайдено')
m = m[:k].rstrip('\n') + '\n\n' + s6a + '\n\n' + s6b + '\n\n' + m[k + 1:]

lot = re.search(r'\*\*ЛОТОК: (\d+) запис\(ів\)\.\*\*', b)
if not lot or lot.group(1) != '6': stop(f'ЛОТОК ≠ 6 ({lot.group(1) if lot else None})')
for key in marks:
    hs = [x.start() for x in re.finditer(r'^## ' + key + r' ·', b, re.M)]
    if len(hs) != 1: stop(f'секція буфера {key} = {len(hs)}')
    s = hs[0]; nx = re.search(r'^## ', b[s + 3:], re.M); e = s + 3 + nx.start() if nx else len(b)
    b = b[:s] + b[e:]
b = b.replace('**ЛОТОК: 6 запис(ів).**', '**ЛОТОК: 3 запис(ів).** *(G-B2 17.09.2026: група Б2 — Д-В · Д-Г · Д-В2 — влита в manifest §8.10 · §6-а · §6-б)*', 1)
heads = [h for h in re.findall(r'^##\s+(.+)$', b, re.M) if not h.lstrip().startswith(('✅', '🟡', '⚠'))]
if len(heads) != 3: stop(f'після зняття {len(heads)}, очікувано 3')
open(MP, 'w', encoding='utf-8').write(m); open(BP, 'w', encoding='utf-8').write(b)
print('✓ влито: Д-В→§8.10, Д-Г→§6-а, Д-В2→§6-б'); print('✓ ЛОТОК 6→3')
