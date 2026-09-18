#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-Q крок 4 — §0 п.2 самері G-P: G6 не кричить на HISTORY. Файл, що в шапці (перші 12 рядків)
   оголошує «читається ТОЧКОВО» (регістр важливий — оголошення, не згадка), звільнений від
   сигналу 120 KB (його ніхто не читає цілком). Червона межа 200 KB — для всіх, без винятків.
   живе доки: хід 4 сесії G-Q не влитий у репо.
   12.16: якорі repr, count == 1. Ф-20: позиційний revert. П34/П37: повтор → exit 0, той самий md5."""
import sys, os
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx4'
P = os.path.join(STG, 'kernel/Lens_validate.py')
def die(m): print('✗ СТОП:', m); sys.exit(1)
HELP_A = "      G6 стеля обсягу: >120KB сигнал, >200KB червона межа\n"
HELP_N = ("      G6 стеля обсягу: >120KB сигнал, >200KB червона межа · сигнал не діє на файл, що в шапці\n"
          "         оголошує «читається ТОЧКОВО» (HISTORY, томи cookbook); червона межа — для всіх (G-Q)\n")
B_A = ("        elif kb > SIGNAL_KB:\n"
       "            warn(f'{f} — {kb:.0f} KB > {SIGNAL_KB} KB сигнал: планувати розпил'); big = True\n")
B_N = ("        elif kb > SIGNAL_KB:\n"
       "            head = open(R(root, f), encoding='utf-8').read().splitlines()[:12]\n"
       "            if any('читається ТОЧКОВО' in l for l in head):\n"
       "                print(f'  ⓘ {f} — {kb:.0f} KB > {SIGNAL_KB} KB, але читається ТОЧКОВО (шапка) — сигнал не діє')\n"
       "                continue\n"
       "            warn(f'{f} — {kb:.0f} KB > {SIGNAL_KB} KB сигнал: планувати розпил'); big = True\n")
EDITS = [(HELP_A, HELP_N), (B_A, B_N)]
src = open(P, encoding='utf-8').read()
if all(src.count(n) == 1 for _, n in EDITS):
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if not all(src.count(a) == 1 for a, _ in EDITS): die('якорі: ' + str([src.count(a) for a, _ in EDITS]))
if 'def g22' not in src: die('G22 (987d7ee) не застосовано — база не та')
new = src
for a, n in EDITS: new = new.replace(a, n, 1)
back = new
for a, n in reversed(EDITS):
    i = back.index(n); back = back[:i] + a + back[i + len(n):]
if back != src: die('позиційний revert ≠ старий файл')
open(P, 'w', encoding='utf-8').write(new)
print(f'✓ Lens_validate.py {len(src.encode()):6d} → {len(new.encode()):6d} B · 2 правки · revert == old')
