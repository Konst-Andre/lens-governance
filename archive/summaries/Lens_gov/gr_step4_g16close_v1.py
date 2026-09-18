#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-R крок 4 — закриття черги `G16-1` канонічною частиною (код — хід 3, `1e95cb9`).
   живе доки: хід 4 сесії G-R не влитий у репо.
   gov 12.12: детектор є (гейт G13), бракувало мітки → абзац `**Детектор (К2).**`.
   gov 12.17: правило саме є процедурою перевірки → `K2:n/a — причина` (клас 10.1–10.5).
   Черга: рядок `G16-1` видаляється як закритий. Умова «лише до ###» відкинута замірами G-R
   (текст — самері G-R §2).
   12.16: стопи вище першого запису. Ф-20: позиційний revert кожного файлу == old. П34/П37.
   Виклик: python3 gr_step4_g16close_v1.py <тека staging>"""
import sys, os

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

if len(sys.argv) != 2: die('виклик: gr_step4_g16close_v1.py <тека staging>')
PG = os.path.join(sys.argv[1], 'kernel/wsd/Lens_governance_protocol.md')
PC = os.path.join(sys.argv[1], 'kernel/Lens_governance_CHERGA.md')
G_OLD, C_OLD = 59383, 7274

A1 = '**Урок про сам детектор (К2).**'
I1 = ('**Детектор (К2).** Гейт `G13` (`--gov`) — три перевірки з таблиці вище; `--inject` дубля §N '
      'дає ✗, діри чи зворотного порядку — ⚠.\n\n')
A2 = '**Родич:** `12.1`.\n'
I2 = '\n<!-- K2:n/a — правило саме є процедурою перевірки (грeп цільового файлу перед вливанням), як 10.1–10.5 -->\n'

g = open(PG, encoding='utf-8').read()
c = open(PC, encoding='utf-8').read()
rows = [l for l in c.splitlines(True) if l.startswith('| `G16-1` |')]

if g.count(I1 + A1) == 1 and g.count(A2 + I2) == 1 and not rows:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if len(g.encode()) != G_OLD: die(f'база gov: {len(g.encode())} ≠ {G_OLD}')
if len(c.encode()) != C_OLD: die(f'база черги: {len(c.encode())} ≠ {C_OLD}')
if g.count(A1) != 1 or g.count(A2) != 1: die(f'якорі gov: {g.count(A1)} · {g.count(A2)}')
if g.count(I1) or g.count(I2): die('вставки вже частково є — стан змішаний')
if len(rows) != 1: die(f'рядок G16-1 у черзі: {len(rows)}')

i1 = g.index(A1)
g1 = g[:i1] + I1 + g[i1:]
i2 = g1.index(A2) + len(A2)
g2 = g1[:i2] + I2 + g1[i2:]
ic = c.index(rows[0])
c2 = c[:ic] + c[ic + len(rows[0]):]

# Ф-20: позиційний revert
r1 = g2[:i2] + g2[i2 + len(I2):]
if r1[:i1] + r1[i1 + len(I1):] != g: die('Ф-20 gov: revert ≠ old')
if c2[:ic] + rows[0] + c2[ic:] != c: die('Ф-20 черга: revert ≠ old')

open(PG, 'w', encoding='utf-8').write(g2)
open(PC, 'w', encoding='utf-8').write(c2)
print(f'✓ gov   {len(g.encode())} → {len(g2.encode())} B')
print(f'✓ черга {len(c.encode())} → {len(c2.encode())} B (запас до 7 372 B: {7372 - len(c2.encode())} B)')
print('✓ Ф-20: позиційний revert обох == old')
