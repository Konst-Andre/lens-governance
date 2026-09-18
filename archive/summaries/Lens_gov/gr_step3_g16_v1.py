#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-R крок 3 — §0 п.3 самері G-Q, Ф-26 = черга `G16-1`: ознака детектора в G16 — структурна.
   живе доки: хід 3 сесії G-R не влитий у репо.
   Було: 'етектор' in r_ or 'К2' in r_ (підрядок будь-де → «правило без детектора» = ✓).
   Стало: мітка на початку рядка `**Детектор…**` (відступ і `>` дозволені) будь-де в тілі правила.
   Умову G16-1 «лише до ###» відкинуто замірами G-R: 7 ⚠, з них ≥4 хибні (2.3 · 13.2 · 1.19 · 12.10);
   «будь-де» дає рівно 2 — gov 12.12 · 12.17, які G16-1 сам назвав «слабкими ✓».
   12.16: стопи вище першого запису. Ф-20: позиційний revert == old. П34/П37: повтор → exit 0.
   Виклик: python3 gr_step3_g16_v1.py <тека staging>"""
import sys, os, hashlib

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

if len(sys.argv) != 2: die('виклик: gr_step3_g16_v1.py <тека staging>')
P = os.path.join(sys.argv[1], 'kernel/Lens_validate.py')
MD5_OLD = 'e75829c312e8adbd23d09b4abb083be3'

OLD_COND = "'етектор' in r_ or 'К2' in r_"
NEW_COND = 'DET_LABEL.search(r_)'

A_CMT = ("    # детектор живе разом з тілом, а не з покажчиком.\n"
         "    print('\\n[G16] правила без детектора (К2)')\n")
N_CMT = ("    # детектор живе разом з тілом, а не з покажчиком.\n"
         "    #\n"
         "    # ОЗНАКА (Ф-26, G-R): мітка `**Детектор…**` на початку рядка (відступ і `>`\n"
         "    # дозволені) будь-де в тілі правила, включно з підрозділами `### N.N-б`.\n"
         "    # Не підрядок: «правило без детектора» · «**Урок про детектор**» · слово «К2»\n"
         "    # давали ✓ без детектора (1.15 пастка 5). «Лише до ###» відкинуто: детектор\n"
         "    # батька часто стоїть після підрозділу (2.3 · 13.2 · 1.19) → хибний ⚠ (12.12).\n"
         "    DET_LABEL = re.compile(r'(?m)^[ \\t>]*\\*\\*Детектор[^*\\n]*\\*\\*')\n"
         "    print('\\n[G16] правила без детектора (К2)')\n")
A_HLP = "      G16 правило без детектора (К2) і без маркера K2:n/a\n"
N_HLP = ("      G16 правило без детектора (К2) і без маркера K2:n/a · детектор = мітка\n"
         "         `**Детектор…**` на початку рядка, не підрядок у тексті (Ф-26, G-R)\n")

raw = open(P, 'rb').read()
s = raw.decode('utf-8')
new_ok = (s.count(OLD_COND) == 0 and s.count(NEW_COND) == 2 and s.count(N_CMT) == 1
          and s.count(N_HLP) == 1)
if new_ok:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if hashlib.md5(raw).hexdigest() != MD5_OLD: die('база: md5 Lens_validate.py ≠ e75829c3')
for a, n in ((OLD_COND, 2), (A_CMT, 1), (A_HLP, 1)):
    if s.count(a) != n: die(f'якір {a[:40]!r}: count={s.count(a)} ≠ {n}')

s2 = s.replace(OLD_COND, NEW_COND).replace(A_CMT, N_CMT).replace(A_HLP, N_HLP)
# Ф-20: позиційний revert
rv = s2.replace(N_HLP, A_HLP).replace(N_CMT, A_CMT).replace(NEW_COND, OLD_COND)
if rv != s: die('Ф-20: позиційний revert ≠ old')
compile(s2, P, 'exec')
open(P, 'w', encoding='utf-8').write(s2)
print(f'✓ Lens_validate.py {len(raw)} → {len(s2.encode())} B · md5 {hashlib.md5(s2.encode()).hexdigest()[:8]}')
print('✓ Ф-20: позиційний revert == old')
