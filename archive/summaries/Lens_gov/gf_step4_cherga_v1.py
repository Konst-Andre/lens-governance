#!/usr/bin/env python3
# живе доки: G-F4 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-F4: CHERGA `К2-1` на місці — wsd 36/68 → 27/68 (G-F3 група 1) · 1.11 зі слабких ✓ прибрано. Без нових id.
# Прохід 1 — перевірки й стеля в пам'яті; прохід 2 — запис (Ф-4). Повтор → no-op.
import sys, os, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
P = os.path.join(ROOT, 'kernel', 'Lens_governance_CHERGA.md')
CEIL = 8000
def die(m): print('STOP:', m); sys.exit(1)
OLD = ("wsd **36/68**. Шаблон вироку — `GE2_k2_gov_texts_v1.md` §1. "
       "Слабкі ✓ (`G16-1`): `1.11` `12.12` `12.17` — тим же проходом")
NEW = ("wsd **27/68** (G-F3: гр.1 ✅). Шаблон вироку — `GE2_k2_gov_texts_v1.md` §1. "
       "Слабкі ✓ (`G16-1`): `12.12` `12.17` — тим же проходом")
t = open(P, encoding='utf-8').read()
if t.count(NEW) == 1 and t.count(OLD) == 0:
    print('no-op: усе вже застосовано'); sys.exit(0)
if t.count(OLD) != 1 or t.count(NEW) != 0: die(f'якір: old={t.count(OLD)} new={t.count(NEW)}')
n = t.replace(OLD, NEW)
b0, b1 = len(t.encode()), len(n.encode())
if b1 > CEIL: die(f'стеля CHERGA: {b1} B > {CEIL}')
open(P, 'w', encoding='utf-8').write(n)
print(f'записано CHERGA {b0} → {b1} B · {hashlib.md5(n.encode()).hexdigest()[:8]}')
