#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-K крок 2 — С2 розпилу wsd (IDX-7): шапка-changelog 2.25–2.39 → Work_Standard_HISTORY.md.
   живе доки: С2 не влитий у репо.
   12.16: фрагмент прочитано цілком (G-K хід 2); якорі count==1; усі стопи вище запису.
   Перенос байт-у-байт: assert md5(вирізане) == md5(вставлене) до і після запису
   (практика Ф-14; саме Ф-14 ще не чинне — фрагмент читано повністю).
   Лишається у wsd: абзац-маршрут «Цей файл містить ТІЛЬКИ правила…» + рядок поточної версії.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису."""
import sys, os, hashlib

STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
W = os.path.join(STG, 'kernel/wsd/Work_Standard.md')
H = os.path.join(STG, 'kernel/wsd/Work_Standard_HISTORY.md')
md5 = lambda s: hashlib.md5(s.encode('utf-8')).hexdigest()
def die(m): print('✗ СТОП:', m); sys.exit(1)

w = open(W, encoding='utf-8').read()
h = open(H, encoding='utf-8').read()

# якорі блоку A (2.39…2.31) і блоку B (2.30 + «Останні дві версії» 2.29…2.25)
A_BEG = '> **Версія 2.39** (17.09.2026 · Lens governance G-G'
A_END = '> кластера 12 + `1.14` + К1/К2 → `Lens_governance_protocol.md`; на місцях маршрутні рядки).\n>\n'
ROUTE = '> **Цей файл містить ТІЛЬКИ правила.**'
B_BEG = '>\n> - **2.30** (15.08.2026)'
B_END = '`Lens_sandbox_manifest.md`.\n'

POINTER = ('> **Версія 2.39** (17.09.2026) · changelog версій 2.25–2.39 виселено 18.09.2026 (G-K, С2 розпилу, `IDX-7`) '
           '→ `Work_Standard_HISTORY.md`, розділ «Шапка-changelog wsd 2.25–2.39».\n>\n')
H_ANCH = '-----\n\n## Повний рядок версій (історичний, до виселення)'
H_HEAD = ('## Шапка-changelog wsd 2.25–2.39 *(виселено з `Work_Standard.md` 18.09.2026, G-K, С2 розпилу `IDX-7`; '
          'байт-у-байт, md5 звірено)*\n\n')

if w.count(POINTER) == 1 and h.count(H_HEAD) == 1 and w.count(A_BEG) == 0 and w.count('> - **2.30** (15.08.2026)') == 0:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)

for k, s, t in (('A_BEG', A_BEG, w), ('A_END', A_END, w), ('ROUTE', ROUTE, w), ('B_BEG', B_BEG, w),
                ('B_END', B_END, w), ('H_ANCH', H_ANCH, h)):
    if t.count(s) != 1: die(f'якір {k} count={t.count(s)} (потрібно 1): {s[:60]!r}')
if h.count(H_HEAD) or w.count(POINTER): die('змішаний стан')

a0 = w.index(A_BEG); a1 = w.index(A_END) + len(A_END)
r0 = w.index(ROUTE)
b0 = w.index(B_BEG); b1 = w.index(B_END, b0) + len(B_END)
if not (a0 < a1 == r0 < b0 < b1): die(f'порядок блоків: a0={a0} a1={a1} r0={r0} b0={b0} b1={b1}')
cutA, cutB = w[a0:a1], w[b0:b1]
# у вирізаному не повинно бути тіл правил (G21) — заголовків «## N.N»
if any(l.startswith('#') for l in (cutA + cutB).split('\n')): die('у фрагменті заголовок — це не шапка')
cut = cutA + cutB

w2 = w[:a0] + POINTER + w[a1:b0] + w[b1:]
i = h.index(H_ANCH) + len('-----\n\n')
h2 = h[:i] + H_HEAD + cut + '\n-----\n\n' + h[i:]

pasted = h2[i + len(H_HEAD): i + len(H_HEAD) + len(cut)]
assert md5(cut) == md5(pasted), 'md5 вирізаного ≠ вставленого'
assert w2.count(A_BEG) == 0 and w2.count(ROUTE) == 1 and w2.count(POINTER) == 1

open(W, 'w', encoding='utf-8').write(w2)
open(H, 'w', encoding='utf-8').write(h2)
# звірка після запису — з диска
h3 = open(H, encoding='utf-8').read()
assert md5(h3[i + len(H_HEAD): i + len(H_HEAD) + len(cut)]) == md5(cut), 'md5 після запису розійшовся'
print(f'✓ перенесено {len(cut.encode())} B, md5 {md5(cut)} = вставлене (до і після запису)')
print(f'✓ wsd     {len(w.encode()):6d} → {len(w2.encode()):6d} B')
print(f'✓ HISTORY {len(h.encode()):6d} → {len(h2.encode()):6d} B')
