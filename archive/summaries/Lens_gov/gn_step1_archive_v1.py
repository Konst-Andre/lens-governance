#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-N крок 1 — §0 п.1 самері G-M: архів самері GK + пакет G-M (3 скрипти) у Lens_gov/ ·
   ARCHIVE_INDEX 82→86 · Lens_INDEX §5 governance → GM · GL.
   живе доки: хід 1 сесії G-N не влитий у репо.
   Ф-15 у коді: після запису різниця «gov-файли Project мінус Lens_gov/» має дорівнювати
   рівно оголошеним живим (LIVE) — інакше ✗ «сирота».
   GI_intake_text_v1.md НЕ архівується: «живе доки» (влитий у gov-протокол або відхилений)
   не настало — стоп, якщо INTAKE у gov-протоколі вже ≠ 0 (підстава застаріла).
   12.16: усі стопи вище першого запису. Працює на staging /home/claude/lgx.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5."""
import sys, os, re

STG = '/home/claude/lgx'
PRJ = '/mnt/project'
ARC = 'archive/summaries/Lens_gov'
N_OLD, N_NEW = 82, 86

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

D = '18.09.2026 · Lens governance · '
PACK = [
 ('Lens_governance_session_summary_GK_ROZPYL_S2.md',
  D + 'G-K: архів GH + пакет G-I/G-J, С2 розпилу wsd (шапка-changelog → HISTORY), П-GH1 v2 (--delete), '
      'Ф-14 у 12.16 · пушено 3d946e7 · 655521b · e417d15 · 7e2a6d0 · §0 виконано G-L/G-M або перенесено в §0 G-M, в архів G-N'),
 ('gm_step1_archive_v1.py',
  D + 'пакет G-M: архів GJ + пакет G-L (78→82), §5 → GL · GK, Ф-15 у коді · пушено 46c7bc4'),
 ('gm_step2_c5_v1.py',
  D + 'пакет G-M: С5 розпилу wsd — перевірка → Lens_patch_check_protocol.md (6 фрагментів, 58 125 B, md5) '
      '+ сирота «Четверта пастка» + 1.1 + PROFILE §6 + RULE_FILES chk · пушено 0261817'),
 ('gm_step3_idx7_v1.py',
  D + 'пакет G-M: IDX-7 закрито за власною умовою (wsd 71 289 B < 120 KiB), висяча адреса в К6-1 → К3-1 · пушено 2f426e6'),
]
LIVE = {'GI_intake_text_v1.md',
        'Lens_governance_session_summary_GL_ROZPYL_S3.md',
        'Lens_governance_session_summary_GM_ROZPYL_S5.md'}

A_CNT = ('### `archive/summaries/Lens_gov/` — 82 файли *(заведено G-C3 17.09.2026; шлях з підтекою — '
         'raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*')
N_CNT = A_CNT.replace('— 82 файли', '— 86 файлів')
A_TAIL = ('- `gl_step3_c4_v1.py` · 18.09.2026 · Lens governance · пакет G-L: С4 розпилу wsd — метод вироку → '
          'Lens_verdict_protocol.md (5 фрагментів, 50 660 B, md5) + таблиця маршрутів · пушено bf606d1')
BULLETS = '\n'.join(f'- `{n}` · {d}' for n, d in PACK)
A_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GL_ROZPYL_S3.md` · '
         '`Lens_governance_session_summary_GK_ROZPYL_S2.md` '
         '*(GJ витіснено 18.09.2026 сесією G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
N_IX5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GM_ROZPYL_S5.md` · '
         '`Lens_governance_session_summary_GL_ROZPYL_S3.md` '
         '*(GK витіснено 18.09.2026 сесією G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

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
print('✓ §5 governance → GM_ROZPYL_S5 · GL_ROZPYL_S3')
f15()
