#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-N крок 5 — закрити К6-1 у Lens_governance_CHERGA.md: умова виходу («кожен канон-файл має рядок
   тригера; гейт рахує файли без нього») доведена на репо — G23 ✓ 26/26 (cc9266a · d33a4b8).
   Згадки К6-1 в ARCHIVE_INDEX (анотація) і Lens_validate.py (походження G23) — історія, не адреси.
   живе доки: хід 5 сесії G-N не влитий у репо.
   12.16: стопи вище запису · П34/П37: повтор → exit 0, той самий md5."""
import sys, os
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
Q = os.path.join(STG, 'kernel/Lens_governance_CHERGA.md')
def die(m): print('✗ СТОП:', m); sys.exit(1)
t = open(Q, encoding='utf-8').read()
rows = [l for l in t.split('\n') if l.startswith('| `К6-1` |')]
if not rows:
    if '`К6-1`' in t: die('К6-1 згадано поза рядком — перевірити руками')
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if len(rows) != 1 or t.count(rows[0] + '\n') != 1: die(f'рядок К6-1 ×{len(rows)}')
t2 = t.replace(rows[0] + '\n', '', 1)
if '`К6-1`' in t2: die('після зняття лишилась згадка К6-1')
open(Q, 'w', encoding='utf-8').write(t2)
print(f'✓ черга {len(t.encode())} → {len(t2.encode())} B · К6-1 знято')
