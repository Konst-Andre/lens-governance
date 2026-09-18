#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-K крок 1 — §0 п.7 самері G-J + дірка G-I: архів GH + пакет G-I (3 скрипти) +
   пакет G-J · ARCHIVE_INDEX 67→73 · Lens_INDEX §5 governance → GJ · GI.
   живе доки: хід 1 сесії G-K не влитий у репо.
   GI_intake_text_v1.md НЕ архівується: його «живе доки» (влитий у gov-протокол
   або відхилений) не настало, INTAKE у gov-протоколі — 0 входжень.
   12.16: усі стопи вище першого запису. Працює на staging /home/claude/lgx.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5.
   Скрипти — у Lens_gov/, не archive/scripts/ (вирок G-J)."""
import sys, os

STG = '/home/claude/lgx'
PRJ = '/mnt/project'
ARC = 'archive/summaries/Lens_gov'
N_OLD, N_NEW = 67, 73

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

D = '18.09.2026 · Lens governance · '
PACK = [
 ('Lens_governance_session_summary_GH_CHERGA_LICHYLNYK.md',
  D + 'G-H: прополка gov-черги 7 996→7 762 B, лічильник спрацювань К4-1 (12/90 нулів) · '
      'пушено 26c08b3, §0 закрито G-I/G-J, в архів G-K'),
 ('gi_step1_intake_v1.py',
  D + 'пакет G-I: INTAKE дописком у рядок К3-1 черги (+208 B, без нового id, Ф-10) · пушено f52f59e · '
      'в архів G-K (G-J пропустила, G-I §0 п.7)'),
 ('gi_step2_g19_v1.py',
  D + 'пакет G-I: К4-1 — rules_hits.py влито в Lens_validate.py як G19 · пушено f52f59e · в архів G-K'),
 ('gi_step3_declare_v1.py',
  D + 'пакет G-I: оголошено G19, К4-1 знято з черги, §5 G20 резерв · пушено f52f59e · в архів G-K'),
 ('gj_step1_archive_v1.py',
  D + 'пакет G-J: архів GG + пакет G-H (63→67), §5 → GI · GH · пушено ea9dd5b'),
 ('gj_step2_rulefiles_v1.py',
  D + 'пакет G-J: С1 розпилу wsd — RULE_FILES, G4 по всіх файлах правил, +G21 · пушено c0b6daa'),
]

A_CNT = ('### `archive/summaries/Lens_gov/` — 67 файлів *(заведено G-C3 17.09.2026; шлях з підтекою — '
         'raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*')
N_CNT = A_CNT.replace('— 67 файлів', '— 73 файли')
A_TAIL = ('- `rules_hits_v1.py` · 18.09.2026 · Lens governance · пакет G-H: лічильник спрацювань правил К4-1 '
          '(12/90 нулів) · джерело — коміт 26c08b3, стан до надгробка (у Project файла вже не було, '
          'G-I §0 п.7); влито як `G19` у f52f59e')
BULLETS = '\n'.join(f'- `{n}` · {d}' for n, d in PACK)
A_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GI_INTAKE_G19.md` · '
         '`Lens_governance_session_summary_GH_CHERGA_LICHYLNYK.md` '
         '*(GG витіснено 18.09.2026 сесією G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
N_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GJ_ROZPYL_S1.md` · '
         '`Lens_governance_session_summary_GI_INTAKE_G19.md` '
         '*(GH витіснено 18.09.2026 сесією G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

# ── СТОПИ ────────────────────────────────────────────────────────────────────
if not os.path.isdir(os.path.join(STG, ARC)): die('немає staging-дерева lgx')
ai_p = os.path.join(STG, 'kernel/Lens_ARCHIVE_INDEX.md')
ix_p = os.path.join(STG, 'kernel/Lens_INDEX.md')
ai = open(ai_p, encoding='utf-8').read()
ix = open(ix_p, encoding='utf-8').read()
src = {n: open(os.path.join(PRJ, n), 'rb').read() for n, _ in PACK}

state = []
for n in src:
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
        f'(CNT={ai.count(A_CNT)} TAIL={ai.count(A_TAIL)} IX5={ix.count(A_IX5)})')

# ── ЗАПИС ────────────────────────────────────────────────────────────────────
for n in src:
    open(os.path.join(STG, ARC, n), 'wb').write(src[n])
ai2 = ai.replace(A_CNT, N_CNT).replace(A_TAIL, A_TAIL + '\n' + BULLETS)
ix2 = ix.replace(A_IX5, N_IX5)
open(ai_p, 'w', encoding='utf-8').write(ai2)
open(ix_p, 'w', encoding='utf-8').write(ix2)

n_arc = len([x for x in os.listdir(os.path.join(STG, ARC)) if os.path.isfile(os.path.join(STG, ARC, x))])
print(f'✓ архів Lens_gov: {N_OLD} → {n_arc} файлів (оголошено {N_NEW})')
if n_arc != N_NEW: die(f'розбіжність: фактично {n_arc}, оголошено {N_NEW}')
print(f'✓ ARCHIVE_INDEX {len(ai.encode()):6d} → {len(ai2.encode()):6d} B')
print(f'✓ Lens_INDEX    {len(ix.encode()):6d} → {len(ix2.encode()):6d} B')
print('✓ §5 governance → GJ_ROZPYL_S1 · GI_INTAKE_G19')
