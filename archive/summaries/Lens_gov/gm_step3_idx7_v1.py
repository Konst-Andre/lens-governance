#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-M крок 3 — закрити IDX-7 у Lens_governance_CHERGA.md: умова «wsd під 120 KiB» доведена на репо
   (0261817: wsd 71 289 B, G6 ⚠ зник). Рядок знімається; висяча адреса `IDX-7` у рядку К6-1 → лише `К3-1`
   (урок IDX-14: закритий id у живому рядку черги = адреса в нікуди).
   живе доки: хід 3 сесії G-M не влитий у репо.
   12.16: стопи вище запису · П34/П37: повтор → exit 0, той самий md5."""
import sys, os
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
Q = os.path.join(STG, 'kernel/Lens_governance_CHERGA.md')
W = os.path.join(STG, 'kernel/wsd/Work_Standard.md')
def die(m): print('✗ СТОП:', m); sys.exit(1)
ROW = ('| `IDX-7` | Розпил wsd: **194 KiB при межі 200** (G-G) — **блокувальний**: наступна вставка впреться в G6. '
       'Ріже не байти, а жанри (`К3-1`) | 30.08.2026 | wsd під 120 KiB або розкладений за жанрами |\n')
K6O, K6N = 'Їде з розкладкою за жанрами (`К3-1`/`IDX-7`).', 'Їде з розкладкою за жанрами (`К3-1`).'
q = open(Q, encoding='utf-8').read()
if q.count(ROW) == 0 and q.count(K6N) == 1 and q.count(K6O) == 0:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if q.count(ROW) != 1 or q.count(K6O) != 1: die(f'стан змішаний: ROW={q.count(ROW)} K6={q.count(K6O)}')
ws = os.path.getsize(W)
if ws >= 120 * 1024: die(f'умова IDX-7 не виконана: wsd {ws} B')
q2 = q.replace(ROW, '').replace(K6O, K6N)
open(Q, 'w', encoding='utf-8').write(q2)
print(f'✓ умова: wsd {ws} B < {120*1024} · IDX-7 знято · К6-1 без висячої адреси')
print(f'✓ черга {len(q.encode())} → {len(q2.encode())} B (стеля 8192)')
