#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-I крок 3 — оголосити G19 і закрити К4-1.
   Живе доки: коміт із цією правкою в main (разовий → archive/scripts).
   Підстава: IDX-9 навпаки — код, не названий в індексі, так само хибний, як
   індекс, що обіцяє неіснуючий код. Закритий рядок черги видаляється, деталь → самері §1.
"""
import sys, os, hashlib

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
CEIL = 8192

IDX = os.path.join(ROOT, 'kernel/Lens_INDEX.md')
CHE = os.path.join(ROOT, 'kernel/Lens_governance_CHERGA.md')

I1_OLD = ('| `Lens_validate.py` | гейт-скрипт: `--gov` (G1–G13 · G16 governance; '
          'номери — §5 «Стан номерів гейтів») · `--html <file>` (H1–H4 білд) |')
I1_NEW = ('| `Lens_validate.py` | гейт-скрипт: `--gov [тека] [--live <тека живих самері>]` '
          '(G1–G13 · G16 · G19 governance; номери — §5 «Стан номерів гейтів») · '
          '`--html <file>` (H1–H4 білд) |')

I2_OLD = ('⚠ **Стан номерів гейтів** (звірено грепом `Lens_validate.py` 17.09.2026, G-C2b).\n'
          'Написані: `G1`–`G13`, `G16`. **Зарезервовані без коду: `G14` (черги продуктів) ·\n'
          '`G15` (протухання §5)** — індекс обіцяє машинну перевірку, якої не існує; борг `IDX-9`.\n'
          'Заявки без коду: `G17` — детектор черг (`IDX-11`) · `G18` — кандидат детектора `1.19-б`.\n'
          "Перший вільний номер — **`G19`**. Колізію `Г-10`/`G12` розведено G-C (`Г-12'` закрито).")
I2_NEW = ('⚠ **Стан номерів гейтів** (звірено грепом `Lens_validate.py` 18.09.2026, G-I).\n'
          'Написані: `G1`–`G13`, `G16`, `G19` (спрацювання правил, К4-1 — влитий з\n'
          '`rules_hits.py`, окремий скрипт видалено). **Зарезервовані без коду: `G14`\n'
          '(черги продуктів) · `G15` (протухання §5)** — індекс обіцяє машинну перевірку,\n'
          'якої не існує; борг `IDX-9`.\n'
          'Заявки без коду: `G17` — детектор черг (`IDX-11`) · `G18` — кандидат детектора `1.19-б` ·\n'
          '`G20` — ворота INTAKE (`К3-1`).\n'
          "Перший вільний номер — **`G21`**. Колізію `Г-10`/`G12` розведено G-C (`Г-12'` закрито).")

C_OLD = ('| `К4-1` | **Лічильник спрацювань правил.** `kernel/rules_hits.py` написаний і '
         'звірений в обидва боки: **12 із 90 правил з нулем** (8 без сліду, 4 народжені). '
         'Вісь для `К3-1`/`IDX-7`. Тексти: самері G-G §2 · G-H §2 | 18.09.2026 | '
         'влито в `Lens_validate.py` як `G19`, нульові у виводі |\n')
C_NEW = ''

ok = True
for path, pairs in ((IDX, [('§2 рядок Lens_validate', I1_OLD, I1_NEW),
                           ('§5 стан номерів гейтів', I2_OLD, I2_NEW)]),
                    (CHE, [('зняття рядка К4-1', C_OLD, C_NEW)])):
    txt = open(path, encoding='utf-8').read()
    before = len(txt.encode())
    for name, old, new in pairs:
        n = txt.count(old)
        if n != 1:
            print(f'✗ якір «{name}» не унікальний: count={n}'); ok = False; break
        txt = txt.replace(old, new)
        print(f'  ✓ {name}')
    else:
        after = len(txt.encode())
        if path == CHE and after > CEIL:
            print(f'✗ черга {after} > {CEIL}'); sys.exit(1)
        open(path, 'w', encoding='utf-8').write(txt)
        tail = f' · запас {CEIL-after} B' if path == CHE else ''
        print(f'  {os.path.basename(path)}: {before} → {after} B ({after-before:+d}){tail}'
              f' · md5 {hashlib.md5(txt.encode()).hexdigest()}')
        continue
    sys.exit(1)
print('✓ крок 3 застосовано')
