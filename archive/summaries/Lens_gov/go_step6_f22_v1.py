#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-O крок 6 — §0 п.5 самері G-N (частина): Ф-22 → Lens_github_push_protocol.md, абзац «Кінець ходу пушу».
   живе доки: хід 6 сесії G-O не влитий у репо.
   Ф-22 (G-N §2): read-back у sh без brace-expansion дає хибний ✗. Вставка одразу після
   «Без read-back пуш не завершений.» — там, де правило read-back і живе. Решта п.5 (Ф-15/17/20/21 → gov) — G-P.
   Ф-20: доказ позиційний. П34/П37: повтор → exit 0, жодного запису, той самий md5."""
import sys, hashlib
P = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgf/kernel/Lens_github_push_protocol.md'
def die(m): print('✗ СТОП:', m); sys.exit(1)
ANCH = "read-back кожного файла з репо, md5 = локальний; розбіжність → стоп і звіт.\nБез read-back пуш не завершений.\n"
ADD = ("\n**Хибний ✗ у read-back (Ф-22, G-N 18.09.2026).** `bash_tool` виконує `sh`: `{a,b}` не розгортається,\n"
       "`cmp` отримує неіснуючий шлях → «N/M» на правильному коміті. Read-back — через `bash -c '…'` або\n"
       "з повним переліком шляхів; кирилицю й діфи гейта — через `python3` (`difflib`), не `diff | grep`.\n"
       "Read-back «N/M» з N < M перед будь-якою дією повторюється з друком кожного шляху й md5 обох сторін;\n"
       "шлях, якого немає з обох боків, — помилка команди, не коміту. Хибний ✗ тут шкідливіший за відсутній:\n"
       "він штовхає «виправляти» правильний стан.\n")
t = open(P, encoding='utf-8').read()
md = lambda s: hashlib.md5(s.encode()).hexdigest()[:8]
if t.count(ANCH + ADD) == 1:
    print(f'✓ вже застосовано (md5 {md(t)}) — нічого не пишу'); sys.exit(0)
if not (t.count(ANCH) == 1 and t.count('Ф-22') == 0): die(f'стан змішаний ANCH={t.count(ANCH)} Ф22={t.count("Ф-22")}')
k = t.index(ANCH) + len(ANCH)
t2 = t[:k] + ADD + t[k:]
if t2[:k] + t2[k + len(ADD):] != t: die('Ф-20: позиційний revert ≠ old')
open(P, 'w', encoding='utf-8').write(t2)
print(f'✓ Ф-20: revert == old · позиція {k}')
print(f'✓ Lens_github_push_protocol.md {len(t.encode())} → {len(t2.encode())} B · md5 {md(t)} → {md(t2)}')
