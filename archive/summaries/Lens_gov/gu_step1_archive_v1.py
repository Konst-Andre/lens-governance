#!/usr/bin/env python3
# gu_step1_archive_v1.py · G-U хід 1 · 24.09.2026
# живе доки: хід запушено → archive/summaries/Lens_gov/ (пакет G-U)
# §5 governance → GT; сироти F_CHERGA_PLAN · G_MASKA (витіснені G-C3 17.09, не архівовані) → Lens_gov/.
# GR · GQ: файли не збережено (інший акаунт, вирок Konst — не шукати); зміст у комітах; з §5 знімаються, в архів не кладуться.
import os, sys, shutil, hashlib
R = sys.argv[1] if len(sys.argv) > 1 else '.'
P = '/mnt/project'
def die(m): print('✗', m); sys.exit(1)
IX, AI = f'{R}/kernel/Lens_INDEX.md', f'{R}/kernel/Lens_ARCHIVE_INDEX.md'
GOV = f'{R}/archive/summaries/Lens_gov'
MOVE = ['Lens_session_summary_governance_F_CHERGA_PLAN.md', 'Lens_session_summary_governance_G_MASKA.md']
ix, ai = open(IX, encoding='utf-8').read(), open(AI, encoding='utf-8').read()

if 'GT_S35_INVENTAR' in ix and '— 116 файлів' in ai and all(os.path.exists(f'{GOV}/{f}') for f in MOVE):
    print('✓ вже застосовано — конвеєр не запускається (П34)'); sys.exit(0)
OLD5 = [l for l in ix.split('\n') if l.startswith('| **Lens** *(governance)* |')]
if len(OLD5) != 1: die(f'рядок §5 governance: {len(OLD5)} ≠ 1')
OLD5 = OLD5[0]
if 'GR_G16_STRUKTURA' not in OLD5 or 'GQ_HEITY_TRY' not in OLD5: die('рядок §5 не той, що очікувався (GR · GQ)')
NEW5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GT_S35_INVENTAR.md` '
        '*(стеля не задіяна: самері G-S не написане — лише коміти `c4e44bd`…`176c7a0`; '
        'GR · GQ витіснено 24.09.2026 сесією G-U — **файли не збережено** (сесії йшли з іншого акаунта; вирок Konst: не шукати); зміст — у комітах G-Q `39681fd`…`4323edf` і G-R `2f4d056`…`fcfc3ec`, адрес тексту на ці самері в `kernel/`·`products/` 0 (греп 24.09); '
        'F · G — сироти G-C3 → `archive/summaries/Lens_gov/` 24.09.2026; GP витіснено G-S; GO — G-R; GN — G-Q; GM — G-P; GL — G-O; '
        'GK — G-N; GJ — G-M; GI — G-L; GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* · '
        'супутник `Lens_inventory_GT_v1.md` — вхідний документ формули, живе доки формулу не записано в `kernel/` |')

A1 = '### `archive/summaries/Lens_gov/` — 114 файлів'
A2 = [l for l in ai.split('\n') if l.startswith('- `gr_step4_g16close_v1.py` ·')]
if ai.count(A1) != 1 or len(A2) != 1 or ai.count(A2[0]) != 1: die('якорі ARCHIVE_INDEX')
ROWS = ('\n- `Lens_session_summary_governance_F_CHERGA_PLAN.md` · 24.09.2026 · Lens governance · governance F (план черги): '
        'витіснене G-C3 17.09.2026, у Project лежало сиротою до G-U (Ф-15, старий префікс — звірено вручну)'
        '\n- `Lens_session_summary_governance_G_MASKA.md` · 24.09.2026 · Lens governance · governance G (маска, `12.20`): '
        'витіснене G-C3 17.09.2026, у Project лежало сиротою до G-U (Ф-15, старий префікс — звірено вручну)')
for f in MOVE:
    if not os.path.exists(f'{P}/{f}'): die(f'немає в Project: {f}')
    if os.path.exists(f'{GOV}/{f}'): die(f'вже в архіві: {f}')
# --- усі стопи вище; записи нижче ---
k = ix.index(OLD5); ix2 = ix[:k] + NEW5 + ix[k+len(OLD5):]
assert ix2[:k] + OLD5 + ix2[k+len(NEW5):] == ix, 'revert §5'
ai2 = ai.replace(A1, '### `archive/summaries/Lens_gov/` — 116 файлів', 1)
j = ai2.index(A2[0]) + len(A2[0]); ai3 = ai2[:j] + ROWS + ai2[j:]
assert ai3[j:j+len(ROWS)] == ROWS and ai3[:j] + ai3[j+len(ROWS):] == ai2, 'revert ARCHIVE_INDEX'
open(IX, 'w', encoding='utf-8').write(ix2); open(AI, 'w', encoding='utf-8').write(ai3)
for f in MOVE:
    shutil.copyfile(f'{P}/{f}', f'{GOV}/{f}')
    a = hashlib.md5(open(f'{P}/{f}','rb').read()).hexdigest(); b = hashlib.md5(open(f'{GOV}/{f}','rb').read()).hexdigest()
    if a != b: die(f'md5 копії {f}')
    print('→', f, a[:8])
# Ф-15: gov-файли Project мінус Lens_gov/ = рівно оголошені живі
gov = sorted(f for f in os.listdir(P) if ('governance' in f or f.startswith(('g', 'G'))) and f.endswith(('.md', '.py')))
rest = [f for f in gov if not os.path.exists(f'{GOV}/{f}')]
LIVE = {'Lens_governance_session_summary_GT_S35_INVENTAR.md'}
print('Ф-15 різниця:', rest)
same = [f for f in gov if os.path.exists(f'{GOV}/{f}')]
for f in same:
    a = hashlib.md5(open(f'{P}/{f}','rb').read()).hexdigest(); b = hashlib.md5(open(f'{GOV}/{f}','rb').read()).hexdigest()
    if a != b: print(f'⚠ ім\'я в архіві, вміст інший: {f} Project {a[:8]} ⟂ archive {b[:8]} — не чіпається, рішення Konst')
orph = [f for f in rest if f not in LIVE]
if orph: die(f'сирота: {orph}')
print(f'✓ §5 {len(ix)}→{len(ix2)} B · ARCHIVE_INDEX {len(ai)}→{len(ai3)} B · Lens_gov 114→116')
