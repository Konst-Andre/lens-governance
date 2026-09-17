#!/usr/bin/env python3
# живе доки: G-F1 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-F1: GD + gd_step1_merge_v2 + gd_step2_prune_v2 → archive/summaries/Lens_gov/ · ARCHIVE_INDEX 41→44 · INDEX §5 governance → GE
# Прохід 1 — усі перевірки в пам'яті; прохід 2 — запис (Ф-4). Повтор → no-op, exit 0.
import sys, os, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SRC = '/mnt/project'
P = lambda *a: os.path.join(ROOT, *a)
md5 = lambda b: hashlib.md5(b).hexdigest()
def die(m): print('STOP:', m); sys.exit(1)

GD  = 'Lens_governance_session_summary_GD_COOKBOOK.md'
S1  = 'gd_step1_merge_v2.py'
S2  = 'gd_step2_prune_v2.py'
GE  = 'Lens_governance_session_summary_GE_K2_PILOT.md'
ARCH = 'archive/summaries/Lens_gov'
NEW = {GD: '47add0569be6a050710cc104a8ce36bc', S1: '1b066f767447750e128e023ad4ee24dc', S2: '19805ab301e36b329c02fd2188ff936a'}

IDX_OLD = ('| **Lens** *(governance)* | `' + GD + '` *(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · GH1 · GC3 '
           'витіснені 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
IDX_NEW = ('| **Lens** *(governance)* | `' + GE + '` *(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · GH1 · GC3 · GD '
           'витіснені 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

H_OLD = '### `archive/summaries/Lens_gov/` — 41 файлів *('
H_NEW = '### `archive/summaries/Lens_gov/` — 44 файлів *('
A1 = ("- `Lens_governance_session_summary_GC3_PUSH_ARCHIV.md` · 17.09.2026 · Lens governance · G-C3: архів governance-хвоста Project, `IDX-13` "
      "(повний текст §2) · пушено 73ff3e4, §0 закрито G-D, в архів G-E\n")
A1_ADD = ("- `" + GD + "` · 17.09.2026 · Lens governance · G-D: cookbook-буфер 17→12 (5 → томи 3/4/5); §2 — Ф-2 · Ф-3 · "
          "Ф-4 повним текстом · пушено 6b08c83, §0 закрито G-E/G-F, в архів G-F\n")
A2 = "- `gc3_step1_archive_v1.py` · 17.09.2026 · Lens governance · пакет G-C3: архів 34 файлів + INDEX/CHERGA/ARCHIVE_INDEX · пушено 73ff3e4\n"
A2_ADD = ("- `" + S1 + "` · 17.09.2026 · Lens governance · пакет G-D: 5 записів буфера → томи 3/4/5 + Cookbook INDEX §2/§3 · пушено 6b08c83\n"
          "- `" + S2 + "` · 17.09.2026 · Lens governance · пакет G-D: прополка cookbook-буфера + INDEX §4 + CHERGA `IDX-12` · пушено 6b08c83\n")

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
    if GD in it2: die(f'після правки повне ім\'я GD лишилось в INDEX: {it2.count(GD)} (пастка G10)')
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
