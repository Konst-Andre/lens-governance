#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-N крок 2 — С6 розпилу wsd (К6-1), частина 1: детектор першим.
   Lens_validate.py --gov отримує G23 «канон-файл без тригера читання»: кожен kernel/**/*.md
   має в шапці (перші 12 рядків) рядок з «читається» або «AUTO-READ» — інакше ✗ на файл.
   Форма вільна свідомо: 16 робочих шапок уже мають тригер іншими словами; буквальне
   «читається коли» зробило б їх ✗ за стиль (режим провалу №3). Номер G23, не G22:
   G22 названий кандидатом у §0 п.5 самері G-M (урок IDX-14 — адреса не міняє предмет).
   живе доки: хід 2 сесії G-N не влитий у репо.
   12.16: стопи вище запису · П34/П37: повтор → exit 0, той самий md5."""
import sys, os
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
V = os.path.join(STG, 'kernel/Lens_validate.py')
def die(m): print('✗ СТОП:', m); sys.exit(1)

A_DOC = ("      G21 номер правила з тілом визначений рівно в одному файлі RULE_FILES → інакше ✗\n"
         "         (розпил wsd, IDX-7: перенос без вирізання дає дубль, якого не бачить ніхто)\n")
N_DOC = A_DOC + ("      G23 канон-файл kernel/**/*.md без тригера читання в шапці (перші 12 рядків:\n"
                 "         «читається…» або «AUTO-READ») → ✗ на файл (К6-1: файл вмикається механізмом, не пам'яттю)\n")
A_CALL = "    g21(root)\n    g19(root)\n"
N_CALL = "    g21(root)\n    g23(root)\n    g19(root)\n"
A_FN = "\n\n# ─────────────────────────── G19 · СПРАЦЮВАННЯ ПРАВИЛ ───────────────────────\n"
FN = '''

# ─────────────────────────── G23 · ТРИГЕР ЧИТАННЯ ФАЙЛУ ─────────────────────
def g23(root):
    """К6-1 (G-H §2): тригер читання на рівні файлу, не лише правила. Канон — kernel/**/*.md.
    Шапка = перші 12 рядків; тригер — рядок з «читається» або «AUTO-READ» (форма вільна)."""
    print('\\n[G23] канон-файл має тригер читання в шапці (К6-1)')
    kd = os.path.join(root, 'kernel')
    files = sorted(glob.glob(os.path.join(kd, '**', '*.md'), recursive=True))
    if not files:
        warn('теки kernel/ з .md не знайдено — G23 не виконався, це НЕ зелений результат')
        return
    miss = []
    for p in files:
        head = open(p, encoding='utf-8').read().splitlines()[:12]
        if not any(re.search(r'читається|AUTO-READ', l) for l in head):
            miss.append(os.path.relpath(p, root))
    for m in miss:
        fail(f'`{m}` — у шапці немає тригера читання (К6-1: «читається коли: … · не читається: …»)')
    if not miss:
        ok(f'{len(files)} канон-файлів — у кожного тригер читання в шапці')
'''
N_FN = FN + A_FN

v = open(V, encoding='utf-8').read()
new_ok = v.count(N_DOC) == 1 and v.count(N_CALL) == 1 and v.count(N_FN) == 1
old_ok = (v.count(A_DOC) == 1 and v.count(A_CALL) == 1 and v.count(A_FN) == 1
          and 'def g23' not in v and 'G23' not in v)
if new_ok:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if not old_ok:
    die(f'стан змішаний: DOC={v.count(A_DOC)} CALL={v.count(A_CALL)} FN={v.count(A_FN)} g23={"G23" in v}')
v2 = v.replace(A_DOC, N_DOC).replace(A_CALL, N_CALL).replace(A_FN, N_FN)
compile(v2, V, 'exec')
open(V, 'w', encoding='utf-8').write(v2)
print(f'✓ Lens_validate.py {len(v.encode()):6d} → {len(v2.encode()):6d} B · G23 додано')
