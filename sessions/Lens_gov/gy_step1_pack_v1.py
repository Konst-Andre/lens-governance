#!/usr/bin/env python3
"""gy_step1_pack_v1.py — G-Y хід 1: пакет G-X → репо (12.16: вставка за якорем, count == 1).
живе доки: GY витіснене двома новішими governance-самері → archive/summaries/Lens_gov/ разом із самері

1. самері GX → sessions/Lens_gov/ (байт-у-байт із транспорту, md5 звіряється);
2. журнал переїзду → на місце (редакція G-X із транспорту, md5 звіряється);
3. GV → archive/summaries/Lens_gov/ (git mv, стеля 2);
4. Lens_INDEX §5 «Lens (governance)»: GX · GW; історія + «GV — G-Y»;
5. Lens_ARCHIVE_INDEX: рядок GV після рядка GU.
Усі стопи — перед першим записом.
"""
import hashlib, os, subprocess, sys

SRC = sys.argv[1]  # тека транспорту (завантаження з Project)
S = 'sessions/Lens_gov/'
A = 'archive/summaries/Lens_gov/'
GX = 'Lens_governance_session_summary_GX_START_APP.md'
GV = 'Lens_governance_session_summary_GV_F4_KORPUS.md'
GW = 'Lens_governance_session_summary_GW_F3_YADRO.md'
LEDGER = 'Lens_MIGRATION_GW_ledger.md'
IDX = 'kernel/Lens_INDEX.md'
AIDX = 'kernel/Lens_ARCHIVE_INDEX.md'
T_GX = os.path.join(SRC, 'da15b4be-Lens_governance_session_summary_GX_START_APP.md')
T_LEDGER = os.path.join(SRC, '9bfbb32f-Lens_MIGRATION_GW_ledger.md')


def die(m):
    sys.exit('СТОП: ' + m)


md5 = lambda b: hashlib.md5(b).hexdigest()
rd = lambda p: open(p, 'rb').read()

# ── стопи
for p in (T_GX, T_LEDGER, S + GV, S + GW, S + LEDGER, IDX, AIDX):
    os.path.isfile(p) or die(f'нема {p}')
os.path.exists(S + GX) and die(f'{S + GX} уже є')
os.path.exists(A + GV) and die(f'{A + GV} уже є')

idx = open(IDX, encoding='utf-8').read()
old_row = f'`{GW}` · `{GV}` · супутник'
new_row = f'`{GX}` · `{GW}` · супутник'
old_hist = '*(GU — G-W; GT — G-V;'
new_hist = '*(GV — G-Y; GU — G-W; GT — G-V;'
for a in (old_row, old_hist):
    idx.count(a) == 1 or die(f'якір INDEX ×{idx.count(a)}: {a}')

aidx = open(AIDX, encoding='utf-8').read()
anchor = ('- `Lens_governance_session_summary_GU_F1_ADRESA.md` · 24.09.2026 · Lens governance · G-U '
          '(Ф1 адресація `Репо:шлях`, Ф2 governance-самері в репо): витіснене G-W (стеля 2) з `sessions/Lens_gov/`\n')
aidx.count(anchor) == 1 or die(f'якір ARCHIVE_INDEX ×{aidx.count(anchor)}')
line = (f'- `{GV}` · 24.09.2026 · Lens governance · G-V (Ф4 корпус у ядрі, детектор Ф1 — `G24`, Ф1 чинне): '
        'витіснене G-Y (стеля 2) з `sessions/Lens_gov/`\n')

# ── записи
gx = rd(T_GX)
open(S + GX, 'wb').write(gx)
assert md5(rd(S + GX)) == md5(gx)
led = rd(T_LEDGER)
open(S + LEDGER, 'wb').write(led)
assert md5(rd(S + LEDGER)) == md5(led)
subprocess.run(['git', 'mv', S + GV, A + GV], check=True)

new_idx = idx.replace(old_row, new_row, 1).replace(old_hist, new_hist, 1)
k = new_idx.index(new_hist)
assert new_idx[k:k + len(new_hist)] == new_hist and len(new_idx) - len(idx) == len('GV — G-Y; ')
open(IDX, 'w', encoding='utf-8').write(new_idx)

k = aidx.index(anchor) + len(anchor)
new_aidx = aidx[:k] + line + aidx[k:]
assert new_aidx[:k] + new_aidx[k + len(line):] == aidx  # revert за позицією (12.16, Ф-20)
open(AIDX, 'w', encoding='utf-8').write(new_aidx)

print(f'✓ {GX} md5 {md5(gx)[:8]} · {LEDGER} md5 {md5(led)[:8]} · {GV} → {A} · INDEX §5 · ARCHIVE_INDEX +1 рядок')
