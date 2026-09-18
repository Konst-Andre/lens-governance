#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-M крок 2 — С5 розпилу wsd (IDX-7): перевірка 1.10 1.13 1.15 1.16 · кластер 3 · 4.1–4.3 · кластер 10
   + сирота «Четверта пастка» з-під # Кластер 2 (Ф-18) одразу за 1.15
   → НОВИЙ kernel/wsd/Lens_patch_check_protocol.md (6 фрагментів, 58 125 B).
   Рішення плану G-J §3 (Ф-17): (а) маршрут — РЯДОК у таблиці, не заглушки · (в) окремий файл ·
   10.2 не зливати (злиття міняє байти → поза Ф-14).
   Поза фрагментами (новий текст): рядок-примітка над сиротою · wsd 1.1 п.1 і «Чому» (число 6 KB знято, 12.20)
   і п.3 (точково) · Зміст ×3 · Lens_INDEX рядок 3 · Lens_PROFILE §6 · KERNEL_FILES · RULE_FILES 'chk'.
   живе доки: хід 2 сесії G-M не влитий у репо.
   Ф-14 (12.16): кожен фрагмент — md5 вирізане == вставлене вище першого запису і після.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5."""
import sys, os, re, hashlib

STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
K = lambda p: os.path.join(STG, 'kernel', p)
W, NEWF = K('wsd/Work_Standard.md'), K('wsd/Lens_patch_check_protocol.md')
V, X, P = K('Lens_validate.py'), K('Lens_INDEX.md'), K('Lens_PROFILE.md')
def die(m): print('✗ СТОП:', m); sys.exit(1)
md5 = lambda s: hashlib.md5(s.encode('utf-8')).hexdigest()

# (початок, межа-кінець, включити межу?, байти, md5[:8]) — погоджено в мікроскопі G-M
FR = [('## 1.10 ', '## 1.14 ', 4134, '6c587f6f'),
      ('## 1.15 ', '## 1.16 ', 8457, 'c60eb30d'),
      ('**Четверта пастка', '\n-----\n\n## 1.19 ', 1199, '4ee8718f'),
      ('## 1.16 ', '## 1.17 ', 2691, '03c7e35b'),
      ('# Кластер 3 — ', '# Кластери 5–6 — ', 23661, 'c88dbc7d'),
      ('# Кластер 10 — ', '# Кластер 11 — ', 17983, '9707e919')]
IDS = (['1.10', '1.13', '1.15', '1.16'] + [f'3.{i}' for i in range(1, 13)]
       + ['4.1', '4.2', '4.3'] + [f'10.{i}' for i in range(1, 11)])
H1_OK = {'# Кластер 3 — Pre-patch protocol', '# Python', '# JavaScript',
         '# Кластер 4 — Діагностика перед патчем', '# Кластер 10 — Post-patch verification'}

NOTE = ('> **Сирота з-під `# Кластер 2` (Ф-18, G-M 18.09.2026).** Абзац нижче стояв у `wsd` поза будь-яким '
        'правилом. Це четверта пастка `1.15` у редакції S12 (EquipLens S10 2-Д: «чотири пастки хибного ✓ і ✗», '
        '4-та — лічильник глибини ⟂ регекс). Мердж v2.34 (03.09.2026) віддав номер 4 іншій пастці («тест '
        'перераховує власне очікування»), а ця випала зі списку — лічильник «п\'ять» у заголовку `1.15` її не '
        'враховує. Перенесено байт-у-байт; перенумерація — окремим кроком (правка, не перенос).\n\n')
GLUE = '\n-----\n\n'          # сирота закінчується «(12.12).\n» — розділювач перед 1.16

HEAD = ('> живе доки: назавжди (вічне, wsd 1.8)\n'
 '> KERNEL v2 · 31.07.2026 — спільне ядро сімейства Lens (переносне між Projects, `Lens_NEWPROJECT_bootstrap.md`)\n'
 '> AUTO-READ: ні. Читається ТОЧКОВО за номером — коли задача: пишеться чи правиться детектор (гейт, смоук, '
 'твердження) · патч перед видачею · діагноз помилки перед патчем · перевірка після патча · тестові дані й '
 'дані користувача між білдами. Маршрут — таблиця на початку `Work_Standard.md`.\n\n'
 '# Lens · протокол перевірки патча — до видачі й після\n\n'
 '> Розпил `wsd` (`IDX-7`), С5, G-M 18.09.2026. Правила перенесено з `Work_Standard.md` байт-у-байт '
 '(Ф-14 · `12.16`); номери не змінені (`12.15`) і лишаються дійсними адресами «wsd N». Порядок — за номером; '
 'заголовки кластерів 3, 4 і 10 переїхали разом із правилами.\n\n'
 '-----\n\n')

A_TROW = '| `13.1` `13.2` `13.2-б` `13.3` | `kernel/Lens_PROFILE.md` §7 — UX взаємодії | С3 · G-L |\n'
N_TROW = ('| ' + ' '.join(f'`{i}`' for i in IDS) + ' | `kernel/wsd/Lens_patch_check_protocol.md` — '
          'перевірка патча: детектор, до видачі, діагноз, після | С5 · G-M |\n')
WR = [  # (старе, нове) — точкові правки wsd, кожне count == 1
 ('1. **`Lens_INDEX.md`** — завжди першим. ~6 KB, відповідає на «який файл відповідає на моє питання» ДО того, '
  'як витрачено контекст на великі читання.\n',
  '1. **`Lens_INDEX.md`** — завжди першим. Відповідає на «який файл відповідає на моє питання» ДО того, '
  'як витрачено контекст на великі читання.\n'),
 ('1. **`Work_Standard.md`** (цей файл) — цілком, як протокол.\n',
  '1. **`Work_Standard.md`** (цей файл) — точково: «Зміст» і таблиця «Маршрут розпилу» на початку, далі лише '
  'потрібні номери; номер із таблиці читається в його домі (рядок «**Читається:**» у `Lens_INDEX`).\n'),
 ('Індекс коштує 6 KB і скорочує решту читань', 'Індекс коштує одне читання і скорочує решту читань'),
 ('1. Pre-patch protocol — перед видачею патчу\n',
  '1. Pre-patch protocol — перед видачею патчу → **`Lens_patch_check_protocol.md`**\n'),
 ('1. Діагностика перед патчем\n',
  '1. Діагностика перед патчем → `4.1`–`4.3` **`Lens_patch_check_protocol.md`** · `4.4` `4.5` **`Lens_verdict_protocol.md`**\n'),
 ('1. Post-patch verification\n', '1. Post-patch verification → **`Lens_patch_check_protocol.md`**\n'),
]
XR = [
 ('| 3 | **`Work_Standard.md`** | завжди, цілком — це протокол |',
  '| 3 | **`Work_Standard.md`** | завжди — точково: «Зміст» і таблиця маршрутів, далі потрібні номери |'),
 ('`Lens_verdict_protocol.md` · `Work_Standard_HISTORY.md`',
  '`Lens_verdict_protocol.md` · `Lens_patch_check_protocol.md` · `Work_Standard_HISTORY.md`'),
]
X_AFTER = '| `Lens_verdict_protocol.md` *(`kernel/wsd/`)*'
X_ROW = ('| `Lens_patch_check_protocol.md` *(`kernel/wsd/`)* | **як перевіряти патч**: детектор в обидва боки '
         '`1.10` `1.13` `1.15` `1.16` · до видачі кластер 3 · діагноз `4.1`–`4.3` · після кластер 10. '
         'Розпил wsd С5 (G-M 18.09.2026). **Читається:** точково за номером — маршрут з таблиці на початку `wsd` |')
PR = ('- Не пропонувати сплітити протокол на томи «бо великий» — wsd читається цілком (wsd 12.11).',
      '- Не пропонувати різати канон-файл «бо великий» — ріжуться ролі й жанри, не байти (`12.11`; розпил '
      '`wsd` G-J…G-M); `wsd` читається точково за маршрутом.')
VR = [("    'Lens_governance_protocol.md', 'Lens_verdict_protocol.md',\n",
       "    'Lens_governance_protocol.md', 'Lens_verdict_protocol.md', 'Lens_patch_check_protocol.md',\n"),
      ("'Lens_verdict_protocol.md': 'verd'}",
       "'Lens_verdict_protocol.md': 'verd', 'Lens_patch_check_protocol.md': 'chk'}")]

w, v, x, p = (open(f, encoding='utf-8').read() for f in (W, V, X, P))

# ── СТАН: уже застосовано? ───────────────────────────────────────────────────
if os.path.exists(NEWF):
    nf = open(NEWF, encoding='utf-8').read()
    ok = (nf.startswith(HEAD) and w.count(N_TROW) == 1 and all(w.count(n) == 1 for _, n in WR)
          and all(x.count(n) >= 1 for _, n in XR) and x.count(X_ROW) == 1 and p.count(PR[1]) == 1
          and all(v.count(n) == 1 for _, n in VR))
    if not ok: die('новий файл є, але стан змішаний')
    body = nf[len(HEAD):]
    if sum(n for *_, n, _h in FR) + len((NOTE + GLUE).encode()) != len(body.encode()):
        die('застосований стан: байти тіла не ті')
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
    bad = [l for l in re.findall(r'(?m)^# .*$', f) if l not in H1_OK]
    if bad: die(f'у фрагменті {beg.strip()} непогоджений #-заголовок {bad}')
    frags.append(f); cuts.append((i, j))
got = [m.group(1) for f in frags for m in re.finditer(r'(?m)^##+ `?(\d+\.\d+(?:-[а-яґєіїь])?)', f)]
if got != ['1.10', '1.13', '1.15', '1.16'] + IDS[4:]: die(f'номери у фрагментах {got}')
if w.count(A_TROW) != 1: die('якір рядка таблиці маршрутів')
for a, _ in WR:
    if w.count(a) != 1: die(f'wsd якір {a[:40]!r}: {w.count(a)}')
if x.count(XR[0][0]) != 1 or x.count(XR[1][0]) != 2: die('Lens_INDEX: рядок 3 / списки kernel/wsd/')
if x.count(X_AFTER) != 1: die('Lens_INDEX: рядок verd')
if p.count(PR[0]) != 1: die('PROFILE §6 якір')
for a, _ in VR:
    if v.count(a) != 1: die(f'validate якір {a.strip()[:40]!r}')

# ── ЗБИРАННЯ ─────────────────────────────────────────────────────────────────
w2 = w
for i, j in sorted(cuts, reverse=True): w2 = w2[:i] + w2[j:]
w2 = w2.replace(A_TROW, A_TROW + N_TROW)
for a, b in WR: w2 = w2.replace(a, b)
body = frags[0] + frags[1] + NOTE + frags[2] + GLUE + frags[3] + frags[4] + frags[5]
nf2 = HEAD + body
for f in frags: assert body.count(f) == 1, 'Ф-14: фрагмент не рівно раз'
def unglue(b):  # позиційно: примітка стоїть одразу за фр.2, склейка — одразу за фр.3
    a = len(frags[0]) + len(frags[1]); c = a + len(NOTE) + len(frags[2])
    assert b[a:a + len(NOTE)] == NOTE and b[c:c + len(GLUE)] == GLUE, 'Ф-14: примітка/склейка не на місці'
    return b[:a] + b[a + len(NOTE):c] + b[c + len(GLUE):]
assert md5(unglue(body)) == md5(''.join(frags)), 'Ф-14: вставлене ≠ вирізаному'
for i_ in IDS: assert not re.search(r'(?m)^##+ `?' + re.escape(i_) + r'[\s`]', w2), f'{i_} лишився у wsd'
assert 'Четверта пастка' not in w2
xl = x.split('\n'); k = next(n for n, l in enumerate(xl) if l.startswith(X_AFTER))
xl.insert(k + 1, X_ROW); x2 = '\n'.join(xl)
for a, b in XR: x2 = x2.replace(a, b)
p2 = p.replace(PR[0], PR[1])
v2 = v
for a, b in VR: v2 = v2.replace(a, b)

# ── ЗАПИС ────────────────────────────────────────────────────────────────────
for f, s_ in ((W, w2), (NEWF, nf2), (V, v2), (X, x2), (P, p2)):
    open(f, 'w', encoding='utf-8').write(s_)

# ── ДОКАЗ ПІСЛЯ ЗАПИСУ ───────────────────────────────────────────────────────
rb = open(NEWF, encoding='utf-8').read()[len(HEAD):]
if md5(unglue(rb)) != md5(''.join(frags)): die('Ф-14 після запису: md5 розійшовся')
for (beg, _, n, h), f in zip(FR, frags):
    if rb.count(f) != 1: die(f'Ф-14 після запису: {beg.strip()} не рівно раз')
    print(f'✓ Ф-14 {beg.strip()[:18]:18s} {n:6d} B md5 {h} → у новому файлі 1×')
print(f'✓ фрагменти разом {sum(n for *_, n, _h in FR)} B md5 {md5("".join(frags))[:8]} · + примітка {len(NOTE.encode())} B + склейка {len(GLUE.encode())} B')
for f, a, b in ((W, w, w2), (V, v, v2), (X, x, x2), (P, p, p2)):
    print(f'✓ {os.path.basename(f):28s} {len(a.encode()):7d} → {len(b.encode()):7d} B')
print(f'✓ Lens_patch_check_protocol.md НОВИЙ {len(nf2.encode()):7d} B')
