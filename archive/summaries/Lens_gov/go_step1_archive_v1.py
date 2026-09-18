#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-O крок 1 — §0 п.1 самері G-N: архів самері GL + пакет G-N (5 скриптів) у Lens_gov/ ·
   ARCHIVE_INDEX 86→92 · Lens_INDEX §5 governance → GN · GM.
   живе доки: хід 1 сесії G-O не влитий у репо.
   Ф-15 у коді: після запису різниця «gov-файли Project мінус Lens_gov/» має дорівнювати
   рівно оголошеним живим (LIVE) — інакше ✗ «сирота».
   GI_intake_text_v1.md НЕ архівується: стоп, якщо INTAKE у gov-протоколі вже ≠ 0.
   12.16: усі стопи вище першого запису. Працює на staging /home/claude/lgx.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5.
   Зразок — gn_step1_archive_v1.py (змінено лише константи)."""
import sys, os, re

STG = '/home/claude/lgx'
PRJ = '/mnt/project'
ARC = 'archive/summaries/Lens_gov'
N_OLD, N_NEW = 86, 92

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

D = '18.09.2026 · Lens governance · '
PACK = [
 ('Lens_governance_session_summary_GL_ROZPYL_S3.md',
  D + 'G-L: архів GI + пакет G-K, С3 (кластер 13 → Lens_PROFILE §7) і С4 (метод вироку → Lens_verdict_protocol.md) '
      'розпилу wsd, маршрут-таблиця · пушено 709f587 · 20957b9 · bf606d1 · §0 виконано G-M/G-N або перенесено в §0 G-O, в архів G-O'),
 ('gn_step1_archive_v1.py',
  D + 'пакет G-N: архів GK + пакет G-M (82→86), §5 → GM · GL, Ф-15 у коді · пушено 5f0979a'),
 ('gn_step2_g23_v1.py',
  D + 'пакет G-N: С6 розпилу wsd — G23 «канон-файл без тригера читання» у Lens_validate --gov (49 645 → 51 376 B) · пушено cc9266a'),
 ('gn_step3_k61_v1.py',
  D + 'пакет G-N: С6 — рядок «читається коли / не читається» у шапки 10 канон-файлів (G23 ✗10 → 0) · пушено d33a4b8'),
 ('gn_step4_prof_v1.py',
  D + 'пакет G-N: С6 (12.18) — дублі-конспекти Lens_PROFILE §3/§4 → вказівники на §7 13.3/13.1 (21 440 → 19 902 B) · пушено 23ccfda'),
 ('gn_step5_k61close_v1.py',
  D + 'пакет G-N: К6-1 закрито за власною умовою (G23 ✓ 26/26), рядок знято з черги (7 460 → 7 093 B) · пушено 6e2633c'),
]
LIVE = {'GI_intake_text_v1.md',
        'Lens_governance_session_summary_GM_ROZPYL_S5.md',
        'Lens_governance_session_summary_GN_ROZPYL_S6.md'}

A_CNT = ('### `archive/summaries/Lens_gov/` — 86 файлів *(заведено G-C3 17.09.2026; шлях з підтекою — '
         'raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*')
N_CNT = A_CNT.replace('— 86 файлів', '— 92 файли')
A_TAIL = ('- `gm_step3_idx7_v1.py` · 18.09.2026 · Lens governance · пакет G-M: IDX-7 закрито за власною умовою '
          '(wsd 71 289 B < 120 KiB), висяча адреса в К6-1 → К3-1 · пушено 2f426e6')
BULLETS = '\n'.join(f'- `{n}` · {d}' for n, d in PACK)
A_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GM_ROZPYL_S5.md` · '
         '`Lens_governance_session_summary_GL_ROZPYL_S3.md` '
         '*(GK витіснено 18.09.2026 сесією G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
N_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GN_ROZPYL_S6.md` · '
         '`Lens_governance_session_summary_GM_ROZPYL_S5.md` '
         '*(GL витіснено 18.09.2026 сесією G-O; GK — G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

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
print('✓ §5 governance → GN_ROZPYL_S6 · GM_ROZPYL_S5')
f15()
