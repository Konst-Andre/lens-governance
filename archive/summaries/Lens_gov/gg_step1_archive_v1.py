#!/usr/bin/env python3
# живе доки: G-G1 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-G1: GE самері + пакети G-E (4) і G-F (7) → archive/summaries/Lens_gov/
#       · ARCHIVE_INDEX 44→56 · INDEX §5 governance GE → GF
# Прохід 1 — усі перевірки в пам'яті (Ф-4: жодного запису до завершення перевірок);
# прохід 2 — запис; прохід 3 — read-back md5. Повтор → no-op, exit 0.
import sys, os, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SRC  = '/mnt/project'
ARCH = 'archive/summaries/Lens_gov'
P  = lambda *a: os.path.join(ROOT, *a)
md5 = lambda b: hashlib.md5(b).hexdigest()
def die(m): print('STOP:', m); sys.exit(1)

GE = 'Lens_governance_session_summary_GE_K2_PILOT.md'
GF = 'Lens_governance_session_summary_GF_K2_WSD12.md'

# ім'я → (md5 джерела, рядок для ARCHIVE_INDEX)
PKG = [
 (GE, '648977f2d6e28c9e654c652430c99cb4',
  '· 17.09.2026 · Lens governance · G-E: пілот К2-1 на gov-протоколі (0/12 ✅), шаблон вироку GE2 §1; '
  '§2 — Ф-8 (пастка підрядка G10) · Ф-9 · пушено 3a8a36a/b5e3f5c/e53824f, §0 закрито G-F, в архів G-G'),
 ('GE2_k2_gov_texts_v1.md', '4837cef3c6e8adf56cabdfbf45b87cc9',
  '· 17.09.2026 · Lens governance · G-E: тексти вироків gov-протоколу + §1 шаблон, §4 G16-1 · влиті b5e3f5c'),
 ('ge_step1_archive_v1.py', '91877ef0c8141e50462503a18f5245ae',
  '· 17.09.2026 · Lens governance · пакет G-E: архів GC3 + gc3_step1 · пушено 3a8a36a'),
 ('ge_step3_k2gov_v1.py', '6f08619a8d3309d90391ef409b0922af',
  '· 17.09.2026 · Lens governance · пакет G-E: К2-1 gov-протокол 5/12 → 0/12 · пушено b5e3f5c'),
 ('ge_step4_cherga_v1.py', '87341fb09654b8294d132823fe8d565f',
  '· 17.09.2026 · Lens governance · пакет G-E: CHERGA К2-1 + G16-1 · пушено e53824f'),
 ('GF2_k2_wsd_texts_v1.md', 'b4288ff586e43629cdce3830ef0ef0b5',
  '· 17.09.2026 · Lens governance · G-F: тексти вироків wsd група 1 · влиті 6bc28f5'),
 ('GF5_k2_wsd_texts_v1.md', '2d0ba6dee92a41be94c04f6a5afca452',
  '· 17.09.2026 · Lens governance · G-F: тексти вироків wsd група 2 · влиті 3ef4dd0'),
 ('gf_step1_archive_v1.py', 'a84afd1dd8d4d28eaa1873038225d8c8',
  '· 17.09.2026 · Lens governance · пакет G-F: архів GD + gd_step1/2 · пушено f35a2e7'),
 ('gf_step3_k2wsd_v1.py', 'fbd6f48be4a289066eff84d030beb92c',
  '· 17.09.2026 · Lens governance · пакет G-F: К2-1 wsd група 1 (36/68) · пушено 6bc28f5'),
 ('gf_step4_cherga_v1.py', 'ba7dbcea97bd23ec12b50be81dadf99e',
  '· 17.09.2026 · Lens governance · пакет G-F: CHERGA К2-1 36→27 · пушено 139e173'),
 ('gf_step5_k2wsd_v1.py', 'c4020ba393e04f76dbf6b72d6f621c23',
  '· 17.09.2026 · Lens governance · пакет G-F: К2-1 wsd група 2 (27/68) · пушено 3ef4dd0'),
 ('gf_step6_cherga_v1.py', '8443707033f4dd0e594aafd04a3ae386',
  '· 17.09.2026 · Lens governance · пакет G-F: CHERGA К2-1 27→18 · пушено 3a9715a'),
]
N_OLD, N_NEW = 44, 44 + len(PKG)

IDX_OLD = ('| **Lens** *(governance)* | `' + GE + '` *(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · '
           'GH1 · GC3 · GD витіснені 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
IDX_NEW = ('| **Lens** *(governance)* | `' + GF + '` *(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · '
           'GH1 · GC3 · GD · GE витіснені 17.09.2026 → `archive/summaries/Lens_gov/`)* |')

H_OLD = ('### `archive/summaries/Lens_gov/` — %d файлів *(заведено G-C3 17.09.2026; шлях з підтекою — '
         'raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*\n' % N_OLD)
H_NEW = H_OLD.replace('— %d файлів' % N_OLD, '— %d файлів' % N_NEW, 1)

A_TAIL = ('- `gd_step2_prune_v2.py` · 17.09.2026 · Lens governance · пакет G-D: прополка cookbook-буфера '
          '+ INDEX §4 + CHERGA `IDX-12` · пушено 6b08c83\n')
A_ADD = ''.join('- `%s` %s\n' % (f, d) for f, _, d in PKG)

# ── прохід 1: перевірки ───────────────────────────────────────────────
writes, done = {}, []
for f, h, _ in PKG:
    sp = os.path.join(SRC, f)
    if not os.path.exists(sp): die('немає джерела %s' % sp)
    src = open(sp, 'rb').read()
    if md5(src) != h: die('md5 джерела %s = %s ≠ %s' % (f, md5(src), h))
    tgt = P(ARCH, f)
    if os.path.exists(tgt):
        if md5(open(tgt, 'rb').read()) != h: die('%s існує з іншим md5' % tgt)
        done.append(f)
    else:
        writes[tgt] = src

ip = P('kernel', 'Lens_INDEX.md'); it = open(ip, encoding='utf-8').read()
if it.count(IDX_NEW) == 1 and it.count(IDX_OLD) == 0:
    done.append('INDEX')
elif it.count(IDX_OLD) == 1 and it.count(IDX_NEW) == 0:
    it2 = it.replace(IDX_OLD, IDX_NEW)
    if GE in it2: die('пастка G10: повне ім\'я GE лишилось в INDEX (%d)' % it2.count(GE))
    writes[ip] = it2.encode('utf-8')
else:
    die('INDEX якір: old=%d new=%d' % (it.count(IDX_OLD), it.count(IDX_NEW)))

ap = P('kernel', 'Lens_ARCHIVE_INDEX.md'); at = open(ap, encoding='utf-8').read()
new_state = at.count(H_NEW) == 1 and at.count(A_TAIL + A_ADD) == 1
old_state = (at.count(H_OLD) == 1 and at.count(A_TAIL) == 1 and at.count(A_ADD) == 0
             and all(at.count('- `%s`' % f) == 0 for f, _, _ in PKG))
if new_state:
    done.append('ARCHIVE_INDEX')
elif old_state:
    writes[ap] = at.replace(H_OLD, H_NEW).replace(A_TAIL, A_TAIL + A_ADD).encode('utf-8')
else:
    die('ARCHIVE_INDEX якорі: H_OLD=%d H_NEW=%d TAIL=%d ADD=%d дублі=%s'
        % (at.count(H_OLD), at.count(H_NEW), at.count(A_TAIL), at.count(A_ADD),
           [f for f, _, _ in PKG if at.count('- `%s`' % f)]))

# ── прохід 2: запис ───────────────────────────────────────────────────
if not writes:
    print('no-op: усе вже застосовано (%d позицій)' % len(done)); sys.exit(0)
for p, b in writes.items():
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(b)

# ── прохід 3: read-back і лічильники ──────────────────────────────────
for p in sorted(writes):
    back = open(p, 'rb').read()
    if md5(back) != md5(writes[p]): die('read-back розійшовся: %s' % p)
    print('записано', os.path.relpath(p, ROOT), md5(back)[:8])

n_files = len(os.listdir(P(ARCH)))
at2 = open(ap, encoding='utf-8').read()
i = at2.index('### `archive/summaries/Lens_gov/`'); j = at2.index('### `archive/stands/`', i)
n_rows = sum(1 for l in at2[i:j].splitlines() if l.startswith('- `'))
print('тека=%d · рядків у секції=%d · оголошено=%d' % (n_files, n_rows, N_NEW))
if not (n_files == n_rows == N_NEW): die('лічильники розійшлись')
missing = [f for f, _, _ in PKG if not os.path.exists(P(ARCH, f))]
if missing: die('оголошено, але немає файлу: %s' % missing)
print('OK')
