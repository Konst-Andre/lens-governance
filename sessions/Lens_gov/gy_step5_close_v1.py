#!/usr/bin/env python3
"""gy_step5_close_v1.py — G-Y закриття: журнал Р-4′ · Р-9 · ходи; самері GY живе, GW → archive (стеля 2); INDEX §5; ARCHIVE_INDEX.
живе доки: GY витіснене двома новішими governance-самері → archive/summaries/Lens_gov/ разом із самері
Усі стопи — перед першим записом (12.16).
"""
import os, subprocess, sys
S, A = 'sessions/Lens_gov/', 'archive/summaries/Lens_gov/'
L = S + 'Lens_MIGRATION_GW_ledger.md'; IDX = 'kernel/Lens_INDEX.md'; AIDX = 'kernel/Lens_ARCHIVE_INDEX.md'
GY = 'Lens_governance_session_summary_GY_GIT_APP_2B.md'
GX = 'Lens_governance_session_summary_GX_START_APP.md'
GW = 'Lens_governance_session_summary_GW_F3_YADRO.md'
die = lambda m: sys.exit('СТОП: ' + m)

led = open(L, encoding='utf-8').read()
R4 = '| Р-4 | Гейти ядра (`G19` · `G22` · `G10` · `G8`) читають продукти з локальних коренів `--repo`; кореня нема → ⓘ | механізм `--repo` є з G-V; мережі в гейті як не було, так і нема |'
R4n = '| ~~Р-4~~ | ~~Гейти ядра читають продукти з локальних коренів `--repo`~~ → **скасовано G-Y, див. Р-4′** | ядро не ходить у продукти |'
ANCH = '\n\n## Відкрите — вирішити на першому продукті (EquipLens)'
ADD = ('\n| Р-4′ | **Гейт перевіряє лише свій репо** (G-Y). Гейт ядра — ядро; згадка продуктового файлу в ядрі → ⓘ «перевіряє гейт продукту», не ✗. '
       'Гейт продукту — `Lens_validate.py --product <корінь>`, оголошення з `lens/<Продукт>_INDEX.md`. Шляхові згадки ядро → продукт не переписуються (Р-5) | '
       'слово Konst G-Y: ядро = мозок (як CLAUDE.md), продукт = самодостатній дім; «інструмент під себе, а не себе під інструмент» |'
       '\n| Р-9 | Код гейта продукту — **один** `Lens_validate.py` у ядрі (інструмент, як Cookbook), запускається на корені продукту; '
       'продукт оголошує живе в `lens/<Продукт>_INDEX.md` (поза `docs/` — не публікується) | делеговано Konst G-Y; копія в кожному `tools/` розійшлась би |')
R7 = '| 7 | Гейти: `G19`/`G22`/`G10` через `--repo`; детектор «продуктового в ядрі = 0» | ⬜ |'
R7n = ('| 7 | **За Р-4′, ПЕРЕД 2-б Б:** 7-а гейт ядра — тільки ядро (спершу класифікація ✗95: ядрове ⟂ продуктове) · '
       '7-б `--product <корінь>` (G1 · G3 · G10 · G14 · G24) · 7-в `EquipLens:lens/EquipLens_INDEX.md`; детектор «продуктового в ядрі = 0» | ⬜ |')
ORD = '\n**Кожен хід переносу = два коміти**'
ORDn = ('\n**Порядок (G-Y, Р-4′):** 7-а → 7-б → 7-в → 2-б Б → Project-частина 2-б (вкладення, Р-8) → 3–6 за шаблоном «індекс продукту → А → Б» → 8.\n'
        '**Кожен хід переносу = два коміти**')
for a in (R4, ANCH, R7, ORD):
    led.count(a) == 1 or die(f'журнал ×{led.count(a)}: {a[:50]}')
idx = open(IDX, encoding='utf-8').read()
oR, nR = f'`{GX}` · `{GW}` · супутник', f'`{GY}` · `{GX}` · супутник'
oH, nH = '*(GV — G-Y;', '*(GW — G-Y; GV — G-Y;'
for a in (oR, oH):
    idx.count(a) == 1 or die(f'INDEX ×{idx.count(a)}: {a}')
aidx = open(AIDX, encoding='utf-8').read()
aA = next((l + '\n' for l in aidx.splitlines() if l.startswith('- `Lens_governance_session_summary_GV_F4_KORPUS.md`')), None)
aA and aidx.count(aA) == 1 or die('якір ARCHIVE_INDEX')
line = f'- `{GW}` · 24.09.2026 · Lens governance · G-W (Ф3 «ядро ⟂ продукти», журнал переїзду, Р-1…Р-7): витіснене G-Y (стеля 2) з `sessions/Lens_gov/`\n'
for p in (S + GY, S + GX, S + GW):
    os.path.isfile(p) or die('нема ' + p)
os.path.exists(A + GW) and die('вже є ' + A + GW)

k = led.index(ANCH)
new = led[:k] + ADD + led[k:]
assert new[:k] + new[k + len(ADD):] == led
new = new.replace(R4, R4n, 1).replace(R7, R7n, 1).replace(ORD, ORDn, 1)
open(L, 'w', encoding='utf-8').write(new)
open(IDX, 'w', encoding='utf-8').write(idx.replace(oR, nR, 1).replace(oH, nH, 1))
k = aidx.index(aA) + len(aA)
na = aidx[:k] + line + aidx[k:]
assert na[:k] + na[k + len(line):] == aidx
open(AIDX, 'w', encoding='utf-8').write(na)
subprocess.run(['git', 'mv', S + GW, A + GW], check=True)
print('✓ журнал Р-4′ · Р-9 · хід 7 · порядок · GW → archive · INDEX §5 GY·GX · ARCHIVE_INDEX +GW')
