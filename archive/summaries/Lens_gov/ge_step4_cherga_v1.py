#!/usr/bin/env python3
# живе доки: G-E4 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-E4: kernel/Lens_governance_CHERGA.md — рядки К2-1 і G16-1 на місці. Прохід 1 — перевірки; прохід 2 — запис (Ф-4).
import sys, os, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
CEIL = 8000  # число скрипта G-D; колізія з check_cherga 8192 — IDX-10
def die(m): print('STOP:', m); sys.exit(1)
p = os.path.join(ROOT, 'kernel/Lens_governance_CHERGA.md')
t0 = open(p, encoding='utf-8').read()
NEW = {
 '| `К2-1` |': "| `К2-1` | **Правила без детектора:** gov 0/12 ✅ (G-E3) · wsd **36/68**. Шаблон вироку — `GE2_k2_gov_texts_v1.md` §1. Слабкі ✓ (`G16-1`): `1.11` `12.12` `12.17` — тим же проходом | 30.08.2026 | `G16` дає ✓ по обох файлах правил |",
 '| `G16-1` |': "| `G16-1` | **`G16` дає хибний ✓:** детектор `### N.N-б` зараховано батьку (`1.15` п.3) · будь-який підрядок «етектор»/«К2» у тілі (G-E2). Обидва — `--inject`. Тексти: `Lens_governance_session_summary_GC2a_HRUPA_G.md` §2 · `GE2_k2_gov_texts_v1.md` §4 | 17.09.2026 | ✓ лише за `**Детектор…**` у тілі до `###`; `--inject` обох дає ⚠; без хибних ⚠ (12.12) |",
}
lines = t0.split('\n'); t = t0; done = 0
for pre, new in NEW.items():
    hits = [l for l in lines if l.startswith(pre)]
    if len(hits) != 1: die(f'рядок {pre!r} ×{len(hits)}')
    if hits[0] == new: done += 1; continue
    t = t.replace(hits[0], new)
if done == len(NEW): print('no-op: усе вже застосовано'); sys.exit(0)
if done: die('частково застосовано')
b = len(t.encode('utf-8'))
if b >= CEIL: die(f'стеля: {b} B ≥ {CEIL}')
open(p, 'w', encoding='utf-8').write(t)
print('записано', len(t0.encode()), '→', b, 'B', hashlib.md5(t.encode()).hexdigest()[:8])
