#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-H крок 2 — §0 п.5 самері G-G: архів GF + пакет G-G · ARCHIVE_INDEX 56→63 ·
   Lens_INDEX §5 governance → G-G.
   живе доки: хід 2 сесії G-H не влитий у репо.
   12.16: усі стопи вище першого запису. Працює на staging-дереві /home/claude/lgx."""
import sys, os, shutil, subprocess

STG = '/home/claude/lgx'
OUT = '/mnt/user-data/outputs'
PRJ = '/mnt/project'
ARC = 'archive/summaries/Lens_gov'

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

PACK = [
 ('Lens_governance_session_summary_GF_K2_WSD12.md',
  '18.09.2026 · Lens governance · G-F: К2-1 wsd 18/68 (дві групи вироків); §2 — Ф-6 сегмент правила · Ф-7 · пушено 6bc28f5/3ef4dd0/3a9715a, §0 закрито G-G, в архів G-H'),
 ('GG2_k2_wsd_texts_v1.md',
  '18.09.2026 · Lens governance · G-G: тексти вироків wsd група 1 · влиті 818bf18'),
 ('GG5_k2_wsd_texts_v1.md',
  '18.09.2026 · Lens governance · G-G: тексти вироків wsd група 2 · влиті 818bf18'),
 ('gg_step1_archive_v1.py',
  '18.09.2026 · Lens governance · пакет G-G: архів GE + пакети G-E/G-F · пушено 818bf18'),
 ('gg_step3_k2wsd_v1.py',
  '18.09.2026 · Lens governance · пакет G-G: К2-1 wsd група 1 · пушено 818bf18'),
 ('gg_step5_k2wsd_v1.py',
  '18.09.2026 · Lens governance · пакет G-G: К2-1 wsd група 2, `G16` по wsd → ✓ · пушено 818bf18'),
 ('gg_step6_cherga_v1.py',
  '18.09.2026 · Lens governance · пакет G-G: CHERGA К2-1 закрито, +К4-1/К5-1/G3-1 · пушено 818bf18'),
]

# ── СТОПИ ────────────────────────────────────────────────────────────────────
if not os.path.isdir(STG): die('немає staging-дерева lgx')
for n, _ in PACK:
    if not os.path.exists(os.path.join(PRJ, n)): die(f'немає в Project: {n}')
    if os.path.exists(os.path.join(STG, ARC, n)): die(f'уже в архіві: {n}')

ai_p = os.path.join(STG, 'kernel/Lens_ARCHIVE_INDEX.md')
ix_p = os.path.join(STG, 'kernel/Lens_INDEX.md')
ai = open(ai_p, encoding='utf-8').read()
ix = open(ix_p, encoding='utf-8').read()

A_CNT = '### `archive/summaries/Lens_gov/` — 56 файлів'
N_CNT = '### `archive/summaries/Lens_gov/` — 63 файли'
A_TAIL = '- `gf_step6_cherga_v1.py` · 17.09.2026 · Lens governance · пакет G-F: CHERGA К2-1 27→18 · пушено 3a9715a'
A_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GF_K2_WSD12.md` '
         '*(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · GH1 · GC3 · GD · GE витіснені '
         '17.09.2026 → `archive/summaries/Lens_gov/`)* |')
N_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GG_K2_ZAKRYTO.md` '
         '*(GF витіснено 18.09.2026 сесією G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

for txt, anc, nm in ((ai, A_CNT, 'ARCHIVE лічильник 56'), (ai, A_TAIL, 'ARCHIVE хвіст gf_step6'),
                     (ix, A_IX5, 'INDEX §5 governance')):
    c = txt.count(anc)
    if c != 1: die(f'якір «{nm}»: count={c}, очікував 1')

# ── ЗАПИС ────────────────────────────────────────────────────────────────────
for n, _ in PACK:
    shutil.copy(os.path.join(PRJ, n), os.path.join(STG, ARC, n))

bullets = '\n'.join(f'- `{n}` · {d}' for n, d in PACK)
ai2 = ai.replace(A_CNT, N_CNT).replace(A_TAIL, A_TAIL + '\n' + bullets)
ix2 = ix.replace(A_IX5, N_IX5)
open(ai_p, 'w', encoding='utf-8').write(ai2)
open(ix_p, 'w', encoding='utf-8').write(ix2)
shutil.copy(ai_p, os.path.join(OUT, 'Lens_ARCHIVE_INDEX.md'))
shutil.copy(ix_p, os.path.join(OUT, 'Lens_INDEX.md'))

n_arc = len([x for x in os.listdir(os.path.join(STG, ARC)) if os.path.isfile(os.path.join(STG, ARC, x))])
print(f'✓ архів Lens_gov: 56 → {n_arc} файлів (оголошено 63)')
if n_arc != 63: die(f'розбіжність: фактично {n_arc}, оголошено 63')
print(f'✓ ARCHIVE_INDEX {len(ai.encode()):6d} → {len(ai2.encode()):6d} B')
print(f'✓ Lens_INDEX    {len(ix.encode()):6d} → {len(ix2.encode()):6d} B')
print('✓ §5 governance →', 'GG_K2_ZAKRYTO')
