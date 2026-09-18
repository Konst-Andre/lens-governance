#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-L крок 2 — С3 розпилу wsd (IDX-7): кластер 13 (13.1 · 13.2 · 13.2-б · 13.3) → Lens_PROFILE.md §7.
   живе доки: хід 2 сесії G-L не влитий у репо.
   Ф-14 (12.16): перенос байт-у-байт; assert md5(вирізане) == md5(вставлене) ВИЩЕ першого запису
   і повторно після запису. На старому місці — маршрут за прецедентом 12.15–12.19.
   У тому ж кроці (G-J §0 п.4): RULE_FILES += Lens_PROFILE.md · «читається» у Lens_INDEX і шапці PROFILE.
   KERNEL_FILES не чіпається — PROFILE там уже є (греп G-L).
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5."""
import sys, os, re, hashlib

STG = '/home/claude/lgx'
W = os.path.join(STG, 'kernel/wsd/Work_Standard.md')
P = os.path.join(STG, 'kernel/Lens_PROFILE.md')
V = os.path.join(STG, 'kernel/Lens_validate.py')
X = os.path.join(STG, 'kernel/Lens_INDEX.md')
MD5_EXP = '9eb99ae0'
LEN_EXP = 12391

def die(m): print('✗ СТОП:', m); sys.exit(1)
md5 = lambda s: hashlib.md5(s.encode('utf-8')).hexdigest()

A_BEG = '# Кластер 13 — UX взаємодії'
A_END = '-----\n\n# Історія — окремий файл'
HEADS = ['## 13.1 ask_user_input_v0 — коли показувати',
         '## 13.2 Проактивні пропозиції — форма «💡»',
         '### 13.2-б · Дві родини пропозицій: про ПРОТОКОЛ і про РІШЕННЯ',
         '## 13.3 Двійне пояснення — два рівні, без побутових аналогій']
RT = '> **ROUTING → `Lens_PROFILE.md`** (G-L, С3 розпилу). Номер живий як адреса.'
STUB = A_BEG + '\n\n' + ''.join(f'{h}\n\n{RT}\n\n\n' for h in HEADS)
STUB = STUB[:-1]   # закінчується '\n\n' перед '-----', як у фрагменті
P7 = ('\n---\n\n## §7 Кластер 13 wsd — правила UX взаємодії *(G-L, С3 розпилу `IDX-7`: перенесено з '
      '`Work_Standard.md` байт-у-байт; номери `13.x` — адреси, маршрут лишився у wsd)*\n\n')

V_OLD = "RULE_FILES = {'Work_Standard.md': 'wsd', 'Lens_governance_protocol.md': 'gov'}"
V_NEW = ("RULE_FILES = {'Work_Standard.md': 'wsd', 'Lens_governance_protocol.md': 'gov', "
         "'Lens_PROFILE.md': 'prof'}")
X_OLD = "| `Lens_PROFILE.md` | робочий профіль оператора: стиль пояснень, віджети, зворотний зв'язок |"
X_NEW = ("| `Lens_PROFILE.md` | робочий профіль оператора: стиль пояснень, віджети, зворотний зв'язок "
         "· **§7 — правила UX `13.1` `13.2` `13.2-б` `13.3`** (з wsd, G-L) · **читається:** точково за "
         "номером `13.x` (маршрут з wsd); цілком — при заведенні Project (bootstrap п.2) |")
H_OLD = '> живе доки: назавжди (вічне, wsd 1.8)\n'
H_NEW = ('> живе доки: назавжди (вічне, wsd 1.8) · читається ТОЧКОВО: `13.x` за маршрутом з wsd; '
         'цілком — при заведенні Project\n')

w, p = open(W, encoding='utf-8').read(), open(P, encoding='utf-8').read()
v, x = open(V, encoding='utf-8').read(), open(X, encoding='utf-8').read()

# ── СТАН ─────────────────────────────────────────────────────────────────────
new_ok = (w.count(STUB + A_END) == 1 and p.count(P7) == 1 and v.count(V_NEW) == 1
          and x.count(X_NEW) == 1 and p.startswith(H_NEW) and '## 13.1 ' in p)
if new_ok:
    frag = p[p.index(P7) + len(P7):]
    if md5(frag)[:8] != MD5_EXP: die('застосований стан: md5 §7 не той')
    print(f'✓ вже застосовано — md5 §7 {md5(frag)[:8]} · нічого не пишу'); sys.exit(0)

# ── СТОПИ (усі вище першого запису, 12.16) ────────────────────────────────────
for a in (A_BEG, A_END):
    if w.count(a) != 1: die(f'якір {a!r} у wsd: {w.count(a)} входжень')
i, j = w.index(A_BEG), w.index(A_END)
if not i < j: die('якорі в неправильному порядку')
frag = w[i:j]
if len(frag.encode()) != LEN_EXP or md5(frag)[:8] != MD5_EXP:
    die(f'фрагмент {len(frag.encode())} B md5 {md5(frag)[:8]} ≠ погодженому {LEN_EXP} B {MD5_EXP}')
for h in HEADS:
    if frag.count(h + '\n') != 1: die(f'заголовок {h!r} не рівно 1 раз у фрагменті')
if re.search(r'(?m)^#{1,4} (?!Кластер 13|13\.)', frag): die('у фрагменті чужий заголовок')
if '13.1 ' in p.split('\n## §7')[0] and '## 13.' in p: die('у PROFILE вже є тіло 13.x')
for s_, a, n in ((v, V_OLD, 'RULE_FILES'), (x, X_OLD, 'рядок INDEX'), (p, H_OLD, 'шапка PROFILE')):
    if s_.count(a) != 1: die(f'{n}: якір {s_.count(a)} входжень')
if not p.startswith(H_OLD): die('шапка PROFILE не з першого рядка')
if not p.endswith('\n'): die('PROFILE не закінчується \\n')

w2 = w[:i] + STUB + w[j:]
p2 = p.replace(H_OLD, H_NEW, 1) + P7 + frag
v2 = v.replace(V_OLD, V_NEW)
x2 = x.replace(X_OLD, X_NEW)
ins = p2[p2.index(P7) + len(P7):]
assert md5(ins) == md5(frag), 'Ф-14: вставлене ≠ вирізаному'
assert w2.count(A_END) == 1 and w2.count(A_BEG) == 1

# ── ЗАПИС ────────────────────────────────────────────────────────────────────
for f, s_ in ((W, w2), (P, p2), (V, v2), (X, x2)):
    open(f, 'w', encoding='utf-8').write(s_)

# ── ДОКАЗ ПІСЛЯ ЗАПИСУ ───────────────────────────────────────────────────────
pr = open(P, encoding='utf-8').read()
got = pr[pr.index(P7) + len(P7):]
if md5(got) != md5(frag): die('Ф-14 після запису: md5 розійшовся')
print(f'✓ Ф-14: вирізано {len(frag.encode())} B md5 {md5(frag)[:8]} = вставлено {len(got.encode())} B md5 {md5(got)[:8]}')
for f, a, b in ((W, w, w2), (P, p, p2), (V, v, v2), (X, x, x2)):
    print(f'✓ {os.path.basename(f):22s} {len(a.encode()):7d} → {len(b.encode()):7d} B')
