#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-Q крок 1 — §0 п.1 самері G-P: архів самері GN + пакет G-P (4 скрипти) у Lens_gov/ ·
   ARCHIVE_INDEX 99→104 · Lens_INDEX §5 governance → GP · GO.
   живе доки: хід 1 сесії G-Q не влитий у репо.
   Ф-15 (канон 1.14) у коді: після запису різниця «gov-файли Project мінус Lens_gov/» має дорівнювати
   рівно оголошеним живим (LIVE) — інакше ✗ «сирота».
   GI_intake_text_v1.md НЕ архівується: стоп, якщо INTAKE у gov-протоколі вже ≠ 0.
   12.16: усі стопи вище першого запису. Працює на staging /home/claude/lgx.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5.
   Зразок — gp_step1_archive_v1.py (змінено лише константи й докстрінг)."""
import sys, os, re

STG = '/home/claude/lgx'
PRJ = '/mnt/project'
ARC = 'archive/summaries/Lens_gov'
N_OLD, N_NEW = 99, 104

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

D = '18.09.2026 · Lens governance · '
PACK = [
 ('Lens_governance_session_summary_GN_ROZPYL_S6.md',
  D + 'G-N: архів GK + пакет G-M, С6 розпилу wsd (G23 · 10 тригерів читання · PROFILE §3/§4), К6-1 закрито '
      '· пушено 5f0979a · cc9266a · d33a4b8 · 23ccfda · 6e2633c · §0 виконано G-O/G-P, в архів G-Q'),
 ('gp_step1_archive_v1.py',
  D + 'пакет G-P: архів GM + пакет G-O (92→99), §5 → GO · GN, Ф-15 у коді · пушено c58b49d'),
 ('gp_step2_114_v1.py',
  D + 'пакет G-P: 1.14 += Ф-21 · Ф-23 · Ф-15 (gov 53 024 → 56 287 B) · пушено 6105574'),
 ('gp_step3_1216_v1.py',
  D + 'пакет G-P: 12.16 += Ф-20 · Ф-17 (gov 56 287 → 59 383 B) · пушено 9c0aa86'),
 ('gp_step4_102p4_v1.py',
  D + 'пакет G-P: 10.2 п.4 → загальний інваріант + приклад QR Lens (chk 59 656 → 59 861 B) · пушено c51356f'),
]
LIVE = {'GI_intake_text_v1.md',
        'Lens_governance_session_summary_GO_KANON_TOCHKOVO.md',
        'Lens_governance_session_summary_GP_VLYVANNIA_F.md'}

A_CNT = ('### `archive/summaries/Lens_gov/` — 99 файлів *(заведено G-C3 17.09.2026; шлях з підтекою — '
         'raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*')
N_CNT = A_CNT.replace('— 99 файлів', '— 104 файли')
A_TAIL = ('- `go_step6_f22_v1.py` · 18.09.2026 · Lens governance · пакет G-O: Ф-22 → Lens_github_push_protocol.md '
          '(7 886 → 8 742 B) · пушено 01f9626')
BULLETS = '\n'.join(f'- `{n}` · {d}' for n, d in PACK)
A_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GO_KANON_TOCHKOVO.md` · '
         '`Lens_governance_session_summary_GN_ROZPYL_S6.md` '
         '*(GM витіснено 18.09.2026 сесією G-P; GL — G-O; GK — G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
N_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GP_VLYVANNIA_F.md` · '
         '`Lens_governance_session_summary_GO_KANON_TOCHKOVO.md` '
         '*(GN витіснено 18.09.2026 сесією G-Q; GM — G-P; GL — G-O; GK — G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

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
print('✓ §5 governance → GP_VLYVANNIA_F · GO_KANON_TOCHKOVO')
f15()
