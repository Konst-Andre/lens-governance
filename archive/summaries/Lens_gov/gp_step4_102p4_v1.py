#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-P крок 4 — §0 п.4 самері G-O: 10.2 пункт 4 (Lens_patch_check_protocol.md) — інваріант загальний,
   продуктова специфіка — позначеним прикладом.
   живе доки: хід 4 сесії G-P не влитий у репо.
   Дім 10.2 прочитано цілком (1 304 B). Грeп (12.1): selectOutlet — QR Lens
   (QR_Lens_preview_batch32_1.html, cookbook 5 A-запис press), НЕ EquipLens, як писало G-O §0 п.4.
   Дому для виселення немає: у QR Lens MASTER_LOCK немає за задумом, CHERGA не заведено,
   forward_plan — носій плану. Тому пункт лишається в 10.2, переписаний як загальний інваріант.
   Заміна рядка за якорем count == 1. Ф-20: позиційний revert. П34/П37: повтор → exit 0."""
import sys, hashlib
P = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx/kernel/wsd/Lens_patch_check_protocol.md'
def die(m): print('✗ СТОП:', m); sys.exit(1)
md = lambda s: hashlib.md5(s.encode()).hexdigest()[:8]
OLD = "- [ ] `o.i` sorted at the right place (`selectOutlet()` time), не локально в render-функціях.\n"
NEW = ("- [ ] Сортування даних — у точці вибору, не локально в render-функціях (приклад — QR Lens:\n"
       "  `o.i` сортується в `selectOutlet()`; позначка G-P 18.09.2026 — специфіка продукту як приклад, не як правило).\n")
t = open(P, encoding='utf-8').read()
if t.count(NEW) == 1 and t.count(OLD) == 0:
    print(f'✓ вже застосовано (md5 {md(t)}) — нічого не пишу'); sys.exit(0)
if t.count(OLD) != 1: die(f'якір count={t.count(OLD)} · {OLD!r}')
if 'ROUTING' in NEW: die('ROUTING у вставці — 10.2 випаде з G16/G21')
k = t.index(OLD)
t2 = t[:k] + NEW + t[k + len(OLD):]
if t2[:k] + OLD + t2[k + len(NEW):] != t: die('Ф-20: позиційний revert ≠ old')
open(P, 'w', encoding='utf-8').write(t2)
print(f'✓ Ф-20: revert == old · позиція {k}')
print(f'✓ Lens_patch_check_protocol.md {len(t.encode())} → {len(t2.encode())} B · md5 {md(t)} → {md(t2)}')
