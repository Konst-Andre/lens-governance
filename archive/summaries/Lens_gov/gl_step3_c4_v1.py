#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-L крок 3 — С4 розпилу wsd (IDX-7): метод вироку 1.11 1.12 1.18 1.20 · 2.4–2.15 · 4.4 4.5
   → НОВИЙ kernel/wsd/Lens_verdict_protocol.md (5 фрагментів, 50 660 B).
   + ВИПРАВЛЕННЯ С3 (20957b9): маршрут — ОДНА таблиця діапазонів у wsd (рішення G-J §3 (а)),
   а не заглушки на кожне правило: заглушки кластера 13 знімаються, їх номери йдуть у таблицю.
   Підстава: _rule_ids рахує заглушки → G19 підписує 13.x як (wsd), хоча дім — prof.
   живе доки: хід 3 сесії G-L не влитий у репо.
   Ф-14 (12.16): кожен фрагмент — assert md5(вирізане)==md5(вставлене) вище першого запису і після.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5."""
import sys, os, re, hashlib

STG = '/home/claude/lgx'
K = lambda p: os.path.join(STG, 'kernel', p)
W, NEWF = K('wsd/Work_Standard.md'), K('wsd/Lens_verdict_protocol.md')
V, X = K('Lens_validate.py'), K('Lens_INDEX.md')
def die(m): print('✗ СТОП:', m); sys.exit(1)
md5 = lambda s: hashlib.md5(s.encode('utf-8')).hexdigest()

# (перший номер, наступний заголовок-межа, байти, md5[:8]) — погоджено в мікроскопі G-L
FR = [('## 1.11 ', '## 1.13 ', 4348, 'c00a62ea'),
      ('## 1.18 ', '# Кластер 2 — ', 1379, 'bc8ea320'),
      ('## 1.20 ', '## 2.1 ', 3339, 'bc75bbdf'),
      ('## 2.4 ', '# Кластер 3 — ', 36500, '971586e3'),
      ('## 4.4 ', '# Кластери 5–6 — ', 5094, '3772def8')]
IDS = ['1.11', '1.12', '1.18', '1.20'] + [f'2.{i}' for i in range(4, 16)] + ['4.4', '4.5']

RT = '> **ROUTING → `Lens_PROFILE.md`** (G-L, С3 розпилу). Номер живий як адреса.'
H13 = ['## 13.1 ask_user_input_v0 — коли показувати',
       '## 13.2 Проактивні пропозиції — форма «💡»',
       '### 13.2-б · Дві родини пропозицій: про ПРОТОКОЛ і про РІШЕННЯ',
       '## 13.3 Двійне пояснення — два рівні, без побутових аналогій']
STUB13 = ('# Кластер 13 — UX взаємодії\n\n' + ''.join(f'{h}\n\n{RT}\n\n\n' for h in H13))[:-1]
A_END = '-----\n\n# Історія — окремий файл'
A_TOC = '-----\n\n## Зміст\n'
TABLE = ('-----\n\n## Маршрут розпилу (`IDX-7`) — номери, чиє тіло живе в інших файлах\n\n'
 '> Номер лишається дійсною адресою «wsd N» (`12.15`): знайди його тут і йди в дім. '
 'Заглушок на кожне правило немає — рішення G-J §3 (а): `_rule_ids` рахує заглушки, `G16` їх пропускає.\n\n'
 '| номери | дім | крок |\n|---|---|---|\n'
 '| ' + ' '.join(f'`{i}`' for i in IDS) + ' | `kernel/wsd/Lens_verdict_protocol.md` — метод вироку | С4 · G-L |\n'
 '| `13.1` `13.2` `13.2-б` `13.3` | `kernel/Lens_PROFILE.md` §7 — UX взаємодії | С3 · G-L |\n'
 '| `1.14` `12.6` `12.7` `12.8` `12.10` `12.11` `12.12` `12.15`–`12.19` | '
 '`kernel/wsd/Lens_governance_protocol.md` — заглушки на місці (S14, до рішення G-J) | S14 |\n\n')
HEAD = ('> живе доки: назавжди (вічне, wsd 1.8)\n'
 '> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)\n'
 '> AUTO-READ: ні. Читається ТОЧКОВО за номером — коли задача: вирок (стенд, прев\'ю, device-тест, '
 'важелі, еталон вирівнювання, замір) або проба перед вироком. Маршрут — таблиця на початку `Work_Standard.md`.\n\n'
 '# Lens · протокол вироку — як судити рендер, стенд і важіль\n\n'
 '> Розпил `wsd` (`IDX-7`), С4, G-L 18.09.2026. Правила перенесено з `Work_Standard.md` байт-у-байт '
 '(Ф-14 · `12.16`); номери не змінені (`12.15`) і лишаються дійсними адресами «wsd N». Порядок — за номером.\n\n'
 '-----\n\n')
V1O = "    'Lens_governance_protocol.md',\n"
V1N = "    'Lens_governance_protocol.md', 'Lens_verdict_protocol.md',\n"
V2O = "'Lens_PROFILE.md': 'prof'}"
V2N = "'Lens_PROFILE.md': 'prof', 'Lens_verdict_protocol.md': 'verd'}"
X1O = '`Work_Standard.md` · `Lens_governance_protocol.md` · `Work_Standard_HISTORY.md` · `wsd_delta_running.md`'
X1N = ('`Work_Standard.md` · `Lens_governance_protocol.md` · `Lens_verdict_protocol.md` · '
       '`Work_Standard_HISTORY.md` · `wsd_delta_running.md`')
X2P = '| `Lens_governance_protocol.md` | **як ведеться сам канон**'
X2ROW = ('| `Lens_verdict_protocol.md` *(`kernel/wsd/`)* | **як судити рендер**: метод вироку `1.11` `1.12` `1.18` '
         '`1.20` · `2.4`–`2.15` · `4.4` `4.5`. Розпил wsd С4 (G-L 18.09.2026). **Читається:** точково за номером — '
         'маршрут з таблиці на початку `wsd` |')

w, v, x = (open(f, encoding='utf-8').read() for f in (W, V, X))

# ── СТАН ─────────────────────────────────────────────────────────────────────
if os.path.exists(NEWF):
    nf = open(NEWF, encoding='utf-8').read()
    ok_new = (nf.startswith(HEAD) and w.count(TABLE) == 1 and w.count(STUB13) == 0
              and v.count(V1N) == 1 and v.count(V2N) == 1 and x.count(X2ROW) == 1 and x.count(X1N) == 2)
    if not ok_new: die('новий файл є, але стан змішаний')
    body = nf[len(HEAD):]
    if sum(b for *_, b, _m in FR) != len(body.encode()): die('застосований стан: байти тіла не ті')
    print(f'✓ вже застосовано — тіло {len(body.encode())} B md5 {md5(body)[:8]} · нічого не пишу'); sys.exit(0)

# ── СТОПИ (усі вище першого запису, 12.16) ────────────────────────────────────
frags, cuts = [], []
for beg, end, n, h in FR:
    if w.count(beg) != 1: die(f'якір {beg!r}: {w.count(beg)}')
    i = w.index(beg); j = w.find(end, i)
    if j < 0: die(f'межа {end!r} після {beg!r} не знайдена')
    f = w[i:j]
    if len(f.encode()) != n or md5(f)[:8] != h:
        die(f'{beg.strip()} {len(f.encode())} B md5 {md5(f)[:8]} ≠ погодженому {n} B {h}')
    if re.search(r'(?m)^# ', f): die(f'у фрагменті {beg.strip()} кластерний заголовок')
    frags.append(f); cuts.append((i, j))
got = [m.group(1) for f in frags for m in re.finditer(r'(?m)^##+ `?(\d+\.\d+(?:-[а-яґєіїь])?)', f)]
if got != IDS: die(f'номери у фрагментах {got} ≠ {IDS}')
for a, n in ((STUB13 + A_END, 'заглушки 13 + кінець'), (A_TOC, 'якір Змісту'), (V1O, 'KERNEL_FILES'),
             (V2O, 'RULE_FILES'), (X2P, 'рядок gov у INDEX')):
    s_ = v if n in ('KERNEL_FILES', 'RULE_FILES') else x if 'INDEX' in n else w
    if s_.count(a) != 1: die(f'{n}: {s_.count(a)} входжень')
if x.count(X1O) != 2: die(f'списки kernel/wsd/ у INDEX: {x.count(X1O)} ≠ 2')

w2 = w
for i, j in sorted(cuts, reverse=True): w2 = w2[:i] + w2[j:]
w2 = w2.replace(STUB13 + A_END, A_END).replace(A_TOC, TABLE + A_TOC)
nf2 = HEAD + ''.join(frags)
xl = x.split('\n'); k = next(n for n, l in enumerate(xl) if l.startswith(X2P))
xl.insert(k + 1, X2ROW); x2 = '\n'.join(xl).replace(X1O, X1N)
v2 = v.replace(V1O, V1N).replace(V2O, V2N)
body = nf2[len(HEAD):]
assert md5(body) == md5(''.join(frags)), 'Ф-14: вставлене ≠ вирізаному'
for f in frags: assert body.count(f) == 1
for i_ in IDS: assert not re.search(r'(?m)^##+ `?' + re.escape(i_) + r'[\s`]', w2), f'{i_} лишився у wsd'

# ── ЗАПИС ────────────────────────────────────────────────────────────────────
for f, s_ in ((W, w2), (NEWF, nf2), (V, v2), (X, x2)):
    open(f, 'w', encoding='utf-8').write(s_)

# ── ДОКАЗ ПІСЛЯ ЗАПИСУ ───────────────────────────────────────────────────────
rb = open(NEWF, encoding='utf-8').read()[len(HEAD):]
if md5(rb) != md5(''.join(frags)): die('Ф-14 після запису: md5 розійшовся')
for (beg, _, n, h), f in zip(FR, frags):
    print(f'✓ Ф-14 {beg.strip():8s} {n:6d} B md5 {h} → у новому файлі: {rb.count(f)}×')
print(f'✓ разом {len(rb.encode())} B md5 {md5(rb)[:8]}')
for f, a, b in ((W, w, w2), (V, v, v2), (X, x, x2)):
    print(f'✓ {os.path.basename(f):26s} {len(a.encode()):7d} → {len(b.encode()):7d} B')
print(f'✓ Lens_verdict_protocol.md   НОВИЙ {len(nf2.encode()):7d} B')
