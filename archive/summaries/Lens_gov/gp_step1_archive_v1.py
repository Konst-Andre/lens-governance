#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-P крок 1 — §0 п.1 самері G-O: архів самері GM + пакет G-O (6 скриптів) у Lens_gov/ ·
   ARCHIVE_INDEX 92→99 · Lens_INDEX §5 governance → GO · GN.
   живе доки: хід 1 сесії G-P не влитий у репо.
   Ф-15 у коді: після запису різниця «gov-файли Project мінус Lens_gov/» має дорівнювати
   рівно оголошеним живим (LIVE) — інакше ✗ «сирота».
   GI_intake_text_v1.md НЕ архівується: стоп, якщо INTAKE у gov-протоколі вже ≠ 0.
   12.16: усі стопи вище першого запису. Працює на staging /home/claude/lgx.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5.
   Зразок — go_step1_archive_v1.py (змінено лише константи й докстрінг)."""
import sys, os, re

STG = '/home/claude/lgx'
PRJ = '/mnt/project'
ARC = 'archive/summaries/Lens_gov'
N_OLD, N_NEW = 92, 99

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

D = '18.09.2026 · Lens governance · '
PACK = [
 ('Lens_governance_session_summary_GM_ROZPYL_S5.md',
  D + 'G-M: архів GJ + пакет G-L, С5 розпилу wsd (6 фрагментів → Lens_patch_check_protocol.md), IDX-7 закрито '
      '· пушено 46c7bc4 · 0261817 · 2f426e6 · §0 виконано G-N/G-O або перенесено в §0 G-P, в архів G-P'),
 ('go_step1_archive_v1.py',
  D + 'пакет G-O: архів GL + пакет G-N (86→92), §5 → GN · GM, Ф-15 у коді · пушено 5333f77'),
 ('go_step2_115_v1.py',
  D + 'пакет G-O: 1.15 «п\'ять пасток» → «шість», сирота «Четверта пастка» → пункт 6 (60 146 → 59 529 B) · пушено 98cf939'),
 ('go_step3_102_v1.py',
  D + 'пакет G-O: 10.2 злиття відхилено, правка лише K2-коментаря (59 529 → 59 656 B) · пушено b79c400'),
 ('go_step4_cherga_v1.py',
  D + 'пакет G-O: черга ядра — дописки G3-1 і К3-1 (Ф-18 · Ф-19), нових id немає (7 093 → 7 274 B) · пушено f642fcd'),
 ('go_step5_prof132_v1.py',
  D + 'пакет G-O: Lens_PROFILE §4 «Проактивні пропозиції» → вказівник на §7 13.2 (19 902 → 19 486 B) · пушено 9d41ef3'),
 ('go_step6_f22_v1.py',
  D + 'пакет G-O: Ф-22 → Lens_github_push_protocol.md (7 886 → 8 742 B) · пушено 01f9626'),
]
LIVE = {'GI_intake_text_v1.md',
        'Lens_governance_session_summary_GN_ROZPYL_S6.md',
        'Lens_governance_session_summary_GO_KANON_TOCHKOVO.md'}

A_CNT = ('### `archive/summaries/Lens_gov/` — 92 файли *(заведено G-C3 17.09.2026; шлях з підтекою — '
         'raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*')
N_CNT = A_CNT.replace('— 92 файли', '— 99 файлів')
A_TAIL = ('- `gn_step5_k61close_v1.py` · 18.09.2026 · Lens governance · пакет G-N: К6-1 закрито за власною умовою '
          '(G23 ✓ 26/26), рядок знято з черги (7 460 → 7 093 B) · пушено 6e2633c')
BULLETS = '\n'.join(f'- `{n}` · {d}' for n, d in PACK)
A_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GN_ROZPYL_S6.md` · '
         '`Lens_governance_session_summary_GM_ROZPYL_S5.md` '
         '*(GL витіснено 18.09.2026 сесією G-O; GK — G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
N_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GO_KANON_TOCHKOVO.md` · '
         '`Lens_governance_session_summary_GN_ROZPYL_S6.md` '
         '*(GM витіснено 18.09.2026 сесією G-P; GL — G-O; GK — G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

def gov_project():
    return {f for f in os.listdir(PRJ)
            if f.startswith('Lens_governance_session_summary_') or re.match(r'g[a-z]+\d?_step', f)
            or re.match(r'G[A-Z]+\d?_', f) or f == 'g11hist.py'}

# ── СТОПИ ────────────────────────────────────────────────────────────────────
if not os.path.isdir(os.path.join(STG, ARC)): die('немає staging-дерева lgx')
gp = open(os.path.join(STG, 'kernel/wsd/Lens_governance_protocol.md'), encoding='utf-8').read()
if gp.count('INTAKE') != 0: die('INTAKE уже в gov-протоколі — GI_intake_text_v1.md більше не живий, переглянути LIVE')
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

def f15():
    arc = set(os.listdir(os.path.join(STG, ARC)))
    rest = gov_project() - arc
    if rest != LIVE: die(f'Ф-15 сирота: різниця {sorted(rest ^ LIVE)}')
    print(f'✓ Ф-15: Project мінус Lens_gov/ = рівно живі {sorted(LIVE)}')

if new_ok and set(state) == {'new'}:
    f15(); print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
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
print('✓ §5 governance → GO_KANON_TOCHKOVO · GN_ROZPYL_S6')
f15()
