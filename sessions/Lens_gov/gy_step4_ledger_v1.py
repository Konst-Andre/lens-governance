#!/usr/bin/env python3
"""gy_step4_ledger_v1.py — G-Y: журнал переїзду — Р-8 (Claude Code не бачить Project) · хід 2-б 🔄 (А ✅, Б чекає ходу 7).
живе доки: GY витіснене двома новішими governance-самері → archive/summaries/Lens_gov/ разом із самері
"""
import sys
P = 'sessions/Lens_gov/Lens_MIGRATION_GW_ledger.md'
t = open(P, encoding='utf-8').read()
A1 = '\n\n## Відкрите — вирішити на першому продукті (EquipLens)'
R8 = ('\n| Р-8 | **Сесія Claude Code (хмара) не бачить Project:** ні інших чатів, ні knowledge-файлів, ні поля Instructions — лише свій чат, '
      'вкладення цього чату й склоновані репо. Файл «лише в Project» у такій сесії = файл, якого нема: Konst кладе його вкладенням, Claude — у дім за Р-7 з md5 | '
      'перевірено G-Y 25.09.2026 (О-4 не закрити без тексту поля; 2-б — S34 · S35 · `v17_30` лише в Project) · слово Konst «згоден» |')
A2 = '| 2-б | **EquipLens** — `products/EquipLens/` · `archive/*/EquipLens/` · Project (S34 · S35 · стенд і смоук `v17_30` · wordmark · K0 · K21 ×2 · S17) → репо `EquipLens` | ⬜ |'
N2 = ('| 2-б | **EquipLens** — `products/EquipLens/` · `archive/*/EquipLens/` · Project (S34 · S35 · стенд і смоук `v17_30` · wordmark · K0 · K21 ×2 · S17) → репо `EquipLens` | '
      '🔄 **А ✅** G-Y `EquipLens:a157222` — 36 файлів ядра → `lens/` · `archive/`, md5 ≡, до Б правити в ядрі. '
      '**Б ⏸** (прибрати з ядра) — без ходу 7 дає `--gov` ✓19 ⚠57 ✗102 проти ✓20 ⚠39 ✗95: `G10` «оголошений живим — нема» ×2 (CHERGA · Z_REGISTR), `G8` сирота-шлях ×5, архівні самері → ⚠. '
      'Project-частина — чекає вкладень (Р-8) |')
for a in (A1, A2):
    t.count(a) == 1 or sys.exit(f'СТОП: якір ×{t.count(a)}: {a[:60]}')
R7_end = t.index(A1)
new = t[:R7_end] + R8 + t[R7_end:]
assert new[:R7_end] + new[R7_end + len(R8):] == t
new = new.replace(A2, N2, 1)
open(P, 'w', encoding='utf-8').write(new)
print('✓ Р-8 · 2-б 🔄')
