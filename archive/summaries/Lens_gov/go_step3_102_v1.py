#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-O крок 3 — §0 п.3 самері G-N: кандидат на злиття 10.2 (G-J §3, режим провалу №3) — ВІДХИЛЕНО.
   живе доки: хід 3 сесії G-O не влитий у репо.
   12.16: 10.2 прочитано цілком (1 177 B). Підстава G-J «кожен пункт має власний детектор в іншому
   правилі» перевірена гріпом kernel/: дім мають пункти 1 (3.2 · Lens_validate H1), 5 (cookbook A21),
   6 (3.9); пункти 2–4 — ніде, крім 10.2. На 10.2 посилаються 10.1 (K2), 10.7, 10.9, gov-protocol,
   маршрут wsd — видалення рве адреси. Злиття відхилено.
   Єдина правка — K2-коментар 10.2, що твердив «кожен пункт має власний детектор деінде»: хибне
   твердження про покриття = хибний ✓ (1.15). Текст правила не чіпається.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5."""
import sys, hashlib

P = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgz/kernel/wsd/Lens_patch_check_protocol.md'
def die(m): print('✗ СТОП:', m); sys.exit(1)

OLD = ('<!-- K2:n/a — інваріантний suite: кожен пункт має власний детектор деінде (3.2 синтаксис, 3.9 кнопки), '
       'сам порядок прогону сліду не лишає -->')
NEW = ('<!-- K2:n/a — інваріантний suite; власний детектор деінде мають пункти 1 (3.2 · Lens_validate H1), '
       '5 (cookbook A21), 6 (3.9); пункти 2–4 — лише тут, тому 10.2 не дубль (злиття відхилено G-O 18.09.2026). '
       'Сам порядок прогону сліду не лишає -->')
t = open(P, encoding='utf-8').read()
md = lambda s: hashlib.md5(s.encode()).hexdigest()[:8]
if t.count(NEW) == 1 and t.count(OLD) == 0:
    print(f'✓ вже застосовано (md5 {md(t)}) — нічого не пишу'); sys.exit(0)
if not (t.count(OLD) == 1 and t.count(NEW) == 0): die(f'стан змішаний OLD={t.count(OLD)} NEW={t.count(NEW)}')
k = t.index(OLD); t2 = t[:k] + NEW + t[k + len(OLD):]
if t2[:k] + OLD + t2[k + len(NEW):] != t: die('Ф-20: позиційний revert ≠ old')
open(P, 'w', encoding='utf-8').write(t2)
print(f'✓ Ф-20: revert(new) == old байт-у-байт · позиція {k}')
print(f'✓ Lens_patch_check_protocol.md {len(t.encode())} → {len(t2.encode())} B · md5 {md(t)} → {md(t2)}')
