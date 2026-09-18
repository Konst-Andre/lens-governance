#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-J крок 1 — §0 п.1 самері G-I: архів GG + пакет G-H · ARCHIVE_INDEX 63→67 ·
   Lens_INDEX §5 governance → GI · GH.
   живе доки: хід 1 сесії G-J не влитий у репо.
   12.16: усі стопи вище першого запису. Працює на staging-дереві /home/claude/lgx.
   П34/П37: повтор на вже застосованому стані → exit 0, жодного запису, той самий md5.
   Скрипти — у Lens_gov/, не archive/scripts/ (прецедент G-A…G-H; вирок Konst, G-J)."""
import sys, os, subprocess

STG = '/home/claude/lgx'          # staging (копія свіжого clone)
CLN = '/home/claude/lg'           # чистий clone — джерело git show
PRJ = '/mnt/project'
ARC = 'archive/summaries/Lens_gov'
RH_REV = '26c08b3'                # rules_hits.py до надгробка (коміт G-H)

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

def prj(n):
    return open(os.path.join(PRJ, n), 'rb').read()

def rh():
    r = subprocess.run(['git', '-C', CLN, 'show', f'{RH_REV}:kernel/rules_hits.py'],
                       capture_output=True)
    if r.returncode != 0: die(f'git show {RH_REV}:kernel/rules_hits.py: {r.stderr!r}')
    return r.stdout

# (ім'я в архіві, джерело байтів, рядок реєстру)
PACK = [
 ('Lens_governance_session_summary_GG_K2_ZAKRYTO.md',
  lambda: prj('Lens_governance_session_summary_GG_K2_ZAKRYTO.md'),
  '18.09.2026 · Lens governance · G-G: К2-1 закрито (gov 0/12 · wsd 0/68), канон у фазу прополки; '
  '§0 — черга 7 996 B при стелі, wsd 198 896 B · пушено 641b9bc, §0 закрито G-H/G-I, в архів G-J'),
 ('gh_step1_cherga_v1.py', lambda: prj('gh_step1_cherga_v1.py'),
  '18.09.2026 · Lens governance · пакет G-H: прополка gov-черги 7 996→7 762 B, стеля 8 192 (IDX-10) · пушено 26c08b3'),
 ('gh_step2_archive_v1.py', lambda: prj('gh_step2_archive_v1.py'),
  '18.09.2026 · Lens governance · пакет G-H: архів GF + пакет G-G (56→63), §5 → GG · пушено 26c08b3'),
 ('rules_hits_v1.py', rh,
  '18.09.2026 · Lens governance · пакет G-H: лічильник спрацювань правил К4-1 (12/90 нулів) · '
  'джерело — коміт 26c08b3, стан до надгробка (у Project файла вже не було, G-I §0 п.7); '
  'влито як `G19` у f52f59e'),
]

A_CNT = '### `archive/summaries/Lens_gov/` — 63 файли'
N_CNT = '### `archive/summaries/Lens_gov/` — 67 файлів'
A_TAIL = ('- `gg_step6_cherga_v1.py` · 18.09.2026 · Lens governance · пакет G-G: CHERGA К2-1 закрито, '
          '+К4-1/К5-1/G3-1 · пушено 818bf18')
BULLETS = '\n'.join(f'- `{n}` · {d}' for n, _, d in PACK)
A_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GG_K2_ZAKRYTO.md` '
         '*(GF витіснено 18.09.2026 сесією G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
N_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GI_INTAKE_G19.md` · '
         '`Lens_governance_session_summary_GH_CHERGA_LICHYLNYK.md` '
         '*(GG витіснено 18.09.2026 сесією G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

# ── СТОПИ ────────────────────────────────────────────────────────────────────
if not os.path.isdir(os.path.join(STG, ARC)): die('немає staging-дерева lgx')
ai_p = os.path.join(STG, 'kernel/Lens_ARCHIVE_INDEX.md')
ix_p = os.path.join(STG, 'kernel/Lens_INDEX.md')
ai = open(ai_p, encoding='utf-8').read()
ix = open(ix_p, encoding='utf-8').read()

src = {n: f() for n, f, _ in PACK}
state = []
for n, _, _ in PACK:
    p = os.path.join(STG, ARC, n)
    if not os.path.exists(p): state.append('old')
    elif open(p, 'rb').read() == src[n]: state.append('new')
    else: die(f'в архіві лежить {n} з іншим вмістом')

old_ok = (ai.count(A_CNT) == 1 and ai.count(A_TAIL) == 1 and ix.count(A_IX5) == 1
          and ai.count(BULLETS) == 0 and ix.count(N_IX5) == 0)
new_ok = (ai.count(N_CNT) == 1 and ai.count(A_TAIL + '\n' + BULLETS) == 1 and ix.count(N_IX5) == 1
          and ai.count(A_CNT) == 0 and ix.count(A_IX5) == 0)

if new_ok and set(state) == {'new'}:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if not (old_ok and set(state) == {'old'}):
    die(f'стан змішаний: old_ok={old_ok} new_ok={new_ok} файли={state} '
        f'(якорі: CNT={ai.count(A_CNT)} TAIL={ai.count(A_TAIL)} IX5={ix.count(A_IX5)})')

# ── ЗАПИС ────────────────────────────────────────────────────────────────────
for n in src:
    open(os.path.join(STG, ARC, n), 'wb').write(src[n])
ai2 = ai.replace(A_CNT, N_CNT).replace(A_TAIL, A_TAIL + '\n' + BULLETS)
ix2 = ix.replace(A_IX5, N_IX5)
open(ai_p, 'w', encoding='utf-8').write(ai2)
open(ix_p, 'w', encoding='utf-8').write(ix2)

n_arc = len([x for x in os.listdir(os.path.join(STG, ARC)) if os.path.isfile(os.path.join(STG, ARC, x))])
print(f'✓ архів Lens_gov: 63 → {n_arc} файлів (оголошено 67)')
if n_arc != 67: die(f'розбіжність: фактично {n_arc}, оголошено 67')
print(f'✓ ARCHIVE_INDEX {len(ai.encode()):6d} → {len(ai2.encode()):6d} B')
print(f'✓ Lens_INDEX    {len(ix.encode()):6d} → {len(ix2.encode()):6d} B')
print('✓ §5 governance → GI_INTAKE_G19 · GH_CHERGA_LICHYLNYK')
