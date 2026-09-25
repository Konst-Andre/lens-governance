#!/usr/bin/env python3
"""gy_step3_preview_v1.py — G-Y хід 3: прев'ю-стенд (О-5) → push-протокол §8 + рядок інструкції.
живе доки: GY витіснене двома новішими governance-самері → archive/summaries/Lens_gov/ разом із самері

12.12: вічний файл дописується в кінець · 12.16: вставка за якорем count == 1, доказ — revert за позицією.
"""
import sys

PROT = 'kernel/Lens_github_push_protocol.md'
INSTR = 'kernel/Lens_PROJECT_instruction.md'
LEDGER = 'sessions/Lens_gov/Lens_MIGRATION_GW_ledger.md'

SEC = '''
## §8 Прев'ю-стенд — `Konst-Andre/sandbox` (О-5, ідея Konst G-X · форма ухвалена G-Y 25.09.2026)

> Слово «пісочниця» зайняте `Lens_sandbox_manifest.md` (копія білда із синтетичними даними).
> Репо `sandbox` у правилах зветься **прев'ю-стенд**.

**Тригер.** Є HTML (прев'ю білда, мокап, стенд), який Konst має побачити на пристрої до вироку.

**Дія.** Новий файл у `Konst-Andre/sandbox` за шляхом `<Продукт>/<файл>_vN.html`
(`<Продукт>` = ім'я продуктового репо: `EquipLens` · `QR-Lens` · `stock-check` · `Drive-Lens`).
**Одне прев'ю = одна адреса:** нова версія → новий `N`; наявний файл не перезаписується.
Адреса для Konst: `https://konst-andre.github.io/sandbox/<Продукт>/<файл>_vN.html` — у відповіді разом із SHA коміту.
Корінь `index.html` не чіпається: це вітрина AE-Simulator (S80–S83).
Репо публічне → кладеться лише те, що можна показати публічно (синтетичні дані — `Lens_sandbox_manifest.md`).
Прев'ю — не канон: живий білд і стенди лишаються в репо продукту; прополка `sandbox` — лише зі слова Konst.

**Чому.** Перезапис однієї адреси (`index.html`) ламає порівняння «було ⟂ стало» і дає вирок не тій версії:
кеш Pages і service worker віддають стару сторінку під тією самою адресою. Адреса з версією — це і є версія.

**Анти-приклад.** `sandbox` до G-Y: `index.html` переписувався щопрев'ю (`a15e3b2` → `d52160b`, п'ять комітів);
попередню версію видно лише в історії git, не за адресою.

**Детектор (К2).** Read-back коміту в `sandbox`: `git diff --name-status <SHA>^ <SHA>` — рядок `M` на
`*_v*.html` (перезапис версії) або будь-яка зміна кореневого `index.html` з Lens-сесії → ✗.
'''

LINE_ANCHOR = '· Пишу через GitHub REST API з контейнера. Кожен запис — лише після «так» у мікроскопі.\n'
LINE = ("· Прев'ю на пристрій — прев'ю-стенд: sandbox/<Продукт>/<файл>_vN.html, одна адреса = одна версія,\n"
        "  наявний файл не перезаписується (kernel/Lens_github_push_protocol.md §8).\n")

L_OLD = ('- **О-5 · Прев\'ю-стенд `sandbox`** (ідея Konst G-X): одне прев\'ю = одна адреса '
         '`sandbox/<продукт>/<файл_vN>.html`; дім — `kernel/Lens_github_push_protocol.md` + рядок інструкції. '
         'Форма чекає «так».')
L_NEW = ('- ~~**О-5 · Прев\'ю-стенд `sandbox`**~~ → **закрито G-Y** (Konst делегував): `kernel/Lens_github_push_protocol.md` §8 '
         '+ рядок інструкції (блок GITHUB). Історія: (ідея Konst G-X): одне прев\'ю = одна адреса '
         '`sandbox/<продукт>/<файл_vN>.html`; дім — `kernel/Lens_github_push_protocol.md` + рядок інструкції. '
         'Форма чекає «так».')


def die(m):
    sys.exit('СТОП: ' + m)


prot = open(PROT, encoding='utf-8').read()
'## §8 ' in prot and die('§8 уже є')
prot.endswith('\n') or die('протокол без \\n у кінці')
instr = open(INSTR, encoding='utf-8').read()
instr.count(LINE_ANCHOR) == 1 or die(f'якір інструкції ×{instr.count(LINE_ANCHOR)}')
led = open(LEDGER, encoding='utf-8').read()
led.count(L_OLD) == 1 or die(f'якір журналу ×{led.count(L_OLD)}')

new_prot = prot + SEC
assert new_prot[:len(prot)] == prot
k = instr.index(LINE_ANCHOR) + len(LINE_ANCHOR)
new_instr = instr[:k] + LINE + instr[k:]
assert new_instr[:k] + new_instr[k + len(LINE):] == instr
new_led = led.replace(L_OLD, L_NEW, 1)

open(PROT, 'w', encoding='utf-8').write(new_prot)
open(INSTR, 'w', encoding='utf-8').write(new_instr)
open(LEDGER, 'w', encoding='utf-8').write(new_led)
print(f'✓ {PROT} +{len(SEC.encode())} B · {INSTR} +1 рядок (2 фізичні) · журнал О-5 закрито')
