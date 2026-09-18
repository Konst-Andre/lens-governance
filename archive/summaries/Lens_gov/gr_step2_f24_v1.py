#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-R крок 2 — §0 п.2 самері G-Q: Ф-24 → Lens_INDEX §5, одразу після речення про стелю черги.
   живе доки: хід 2 сесії G-R не влитий у репо.
   Дім Б (рішення Konst, G-R): не рядок К3-1 черги, як пропонувало самері GO §2, а дім стелі —
   12.20 («число канонічне тут, решта посилається»); поріг Ф-10 (досі лише в архівному GH §2)
   отримує дім у каноні. 0,9 × 8 192 = 7 372,8 → без сигналу найбільше 7 372 B.
   12.16: стоп вище першого запису; якір — унікальний, count == 1.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису.
   Ф-20: позиційний revert нового стану == старий байт-у-байт — перевіряється до запису.
   Виклик: python3 gr_step2_f24_v1.py <тека staging>"""
import sys, os

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

if len(sys.argv) != 2: die('виклик: gr_step2_f24_v1.py <тека staging>')
P = os.path.join(sys.argv[1], 'kernel/Lens_INDEX.md')
OLD_SIZE, NEW_SIZE = 51141, 51428

ANCHOR = 'Проза «8 KB» читалась і як 8 000, і як 8 192 — саме це закривало `IDX-10`.'
ADD = (' **Запас** рахується до порогу Ф-10 — 90% стелі, **7 372 B**, не до 8 192: вище порогу черга '
       'вже сигналить «прополка замість розпилу» (Ф-24; тексти — самері GH §2 Ф-10 · GO §2 Ф-24).')

s = open(P, encoding='utf-8').read()
b = len(s.encode())
if s.count(ANCHOR + ADD) == 1 and s.count(ANCHOR) == 1:
    if b != NEW_SIZE: die(f'застосовано, але розмір {b} ≠ {NEW_SIZE}')
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if s.count(ANCHOR) != 1: die(f'якір: count={s.count(ANCHOR)}')
if s.count('Ф-24') != 0: die('Ф-24 уже згаданий у Lens_INDEX — стан змішаний')
if b != OLD_SIZE: die(f'база: розмір {b} ≠ {OLD_SIZE}')

i = s.index(ANCHOR) + len(ANCHOR)
s2 = s[:i] + ADD + s[i:]
# Ф-20: позиційний revert
if s2[:i] + s2[i + len(ADD):] != s: die('Ф-20: позиційний revert ≠ old')
if len(s2.encode()) != NEW_SIZE: die(f'розмір після {len(s2.encode())} ≠ {NEW_SIZE}')

open(P, 'w', encoding='utf-8').write(s2)
print(f'✓ Lens_INDEX {b} → {len(s2.encode())} B (+{len(ADD.encode())})')
print('✓ Ф-20: позиційний revert == old')
