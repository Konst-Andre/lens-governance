#!/usr/bin/env python3
# живе доки: G-E1 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-E1: GC3 + gc3_step1 → archive/summaries/Lens_gov/ · ARCHIVE_INDEX 39→41 · INDEX §5 governance → GD
# Прохід 1 — усі перевірки в пам'яті; прохід 2 — запис (Ф-4). Повтор → no-op, exit 0.
import sys, os, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SRC = '/mnt/project'
P = lambda *a: os.path.join(ROOT, *a)
md5 = lambda b: hashlib.md5(b).hexdigest()
def die(m): print('STOP:', m); sys.exit(1)

GC3 = 'Lens_governance_session_summary_GC3_PUSH_ARCHIV.md'
SCR = 'gc3_step1_archive_v1.py'
GD  = 'Lens_governance_session_summary_GD_COOKBOOK.md'
ARCH = 'archive/summaries/Lens_gov'
NEW = {GC3: '33996e9b3ab1518b7e66a7b7e31c04c8', SCR: '62df63dbaa58cafe77e52af4361219a5'}

IDX_OLD = ('| **Lens** *(governance)* | `' + GC3 + '` *(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · GH1 '
           'витіснені 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
IDX_NEW = ('| **Lens** *(governance)* | `' + GD + '` *(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · GH1 · GC3 '
           'витіснені 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

H_OLD = '### `archive/summaries/Lens_gov/` — 39 файлів *('
H_NEW = '### `archive/summaries/Lens_gov/` — 41 файлів *('
A1 = ("- `Lens_governance_session_summary_GC2b_FINAL_AUDYT.md` · 17.09.2026 · Lens governance · G-C2b: фінал злиття + "
      "аудит зв'язності; §2 — повний текст К3-1 · G-C запушено 6b9943f, §0 закрито G-C3\n")
A1_ADD = ("- `" + GC3 + "` · 17.09.2026 · Lens governance · G-C3: архів governance-хвоста Project, `IDX-13` "
          "(повний текст §2) · пушено 73ff3e4, §0 закрито G-D, в архів G-E\n")
A2 = "- `gc_step2_final_v1.py` · 17.09.2026 · Lens governance · пакет G-C: фінал (wsd 2.35, Z_REGISTR, CHERGA, INDEX) · пушено 6b9943f\n"
A2_ADD = "- `" + SCR + "` · 17.09.2026 · Lens governance · пакет G-C3: архів 34 файлів + INDEX/CHERGA/ARCHIVE_INDEX · пушено 73ff3e4\n"

# ── прохід 1: перевірки ────────────────────────────────────────────────
writes = {}
done = []
for f, h in NEW.items():
    src = open(os.path.join(SRC, f), 'rb').read()
    if md5(src) != h: die(f'md5 джерела {f} = {md5(src)} ≠ {h}')
    tgt = P(ARCH, f)
    if os.path.exists(tgt):
        if md5(open(tgt, 'rb').read()) != h: die(f'{tgt} існує з іншим md5')
        done.append(f)
    else:
        writes[tgt] = src

ip = P('kernel', 'Lens_INDEX.md'); it = open(ip, encoding='utf-8').read()
if it.count(IDX_NEW) == 1 and it.count(IDX_OLD) == 0: done.append('INDEX')
elif it.count(IDX_OLD) == 1 and it.count(IDX_NEW) == 0:
    it2 = it.replace(IDX_OLD, IDX_NEW)
    if GC3 in it2: die(f'після правки повне ім\'я GC3 лишилось в INDEX: {it2.count(GC3)} (пастка G10)')
    writes[ip] = it2.encode('utf-8')
else: die(f'INDEX якір: old={it.count(IDX_OLD)} new={it.count(IDX_NEW)}')

ap = P('kernel', 'Lens_ARCHIVE_INDEX.md'); at = open(ap, encoding='utf-8').read()
state_new = at.count(H_NEW) == 1 and at.count(A1 + A1_ADD) == 1 and at.count(A2 + A2_ADD) == 1
state_old = at.count(H_OLD) == 1 and at.count(A1) == 1 and at.count(A2) == 1 \
            and at.count(A1_ADD) == 0 and at.count(A2_ADD) == 0
if state_new: done.append('ARCHIVE_INDEX')
elif state_old:
    writes[ap] = at.replace(H_OLD, H_NEW).replace(A1, A1 + A1_ADD).replace(A2, A2 + A2_ADD).encode('utf-8')
else:
    die(f'ARCHIVE_INDEX якорі: H_OLD={at.count(H_OLD)} H_NEW={at.count(H_NEW)} A1={at.count(A1)} A2={at.count(A2)} '
        f'A1_ADD={at.count(A1_ADD)} A2_ADD={at.count(A2_ADD)}')

# ── прохід 2: запис ────────────────────────────────────────────────────
if not writes:
    print('no-op: усе вже застосовано', done); sys.exit(0)
for p, b in writes.items():
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(b)
for p in sorted(writes): print('записано', os.path.relpath(p, ROOT), md5(open(p, 'rb').read())[:8])
