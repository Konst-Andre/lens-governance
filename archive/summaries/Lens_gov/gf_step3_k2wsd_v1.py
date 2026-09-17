#!/usr/bin/env python3
# живе доки: G-F3 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-F3: К2-1 wsd група 1 — детектори/тригери/K2:n/a за GF2_k2_wsd_texts_v1.md §4 + шапка 2.36.
# Тексти — лише з файла текстів (не дублюються тут). Прохід 1 — перевірки в пам'яті; прохід 2 — запис (Ф-4). Повтор → no-op.
import sys, os, re, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
TEXTS = sys.argv[2] if len(sys.argv) > 2 else '/mnt/user-data/outputs/GF2_k2_wsd_texts_v1.md'
WSD = os.path.join(ROOT, 'kernel', 'wsd', 'Work_Standard.md')
def die(m): print('STOP:', m); sys.exit(1)

# ── прохід 1: розбір текстів ───────────────────────────────────────────
src = open(TEXTS, encoding='utf-8').read()
i = src.find('\n@@ ')
if i < 0: die('у файлі текстів немає блоків @@')
blocks, key, buf = {}, None, []
for line in src[i + 1:].split('\n'):
    if line.startswith('@@ '):
        if key: blocks[key] = '\n'.join(buf).rstrip('\n')
        key, buf = line[3:].strip(), []
        if key == 'END': break
    else: buf.append(line)
if key != 'END': die('немає @@ END')
RULES = ['1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.11', '1.12', '1.13', '2.1']
TRIG = ['1.5', '1.6', '1.11', '1.12', '1.13']
need = {f'{r} det' for r in RULES} | {f'{r} trig' for r in TRIG} | {'wsd ver'}
if set(blocks) != need: die(f'набір блоків ≠ очікуваний: зайві {set(blocks)-need} · бракує {need-set(blocks)}')
for k, v in blocks.items():
    if not v.strip(): die(f'порожній блок {k}')
    if k.endswith('det') and k != '1.4 det' and not v.startswith('**Детектор (К2).**'): die(f'{k}: не починається з **Детектор (К2).**')
    if k.endswith('trig') and not v.startswith('**Тригер.**'): die(f'{k}: не починається з **Тригер.**')
if not re.fullmatch(r'<!-- K2:n/a\s*—\s*\S.*-->', blocks['1.4 det']): die('1.4: маркер K2:n/a не за формою (латинська K)')

# ── прохід 1: розбір wsd і обчислення нового вмісту ───────────────────
body = open(WSD, encoding='utf-8').read()
old_md5 = hashlib.md5(body.encode()).hexdigest()
parts = re.split(r'\n(?=#{2}\s*\d+\.\d+)', body)
segs = {}
for x in parts:
    m = re.match(r'#{2}\s*(\S+)', x)
    if m and re.match(r'#{2}\s*\d+\.\d+', x):
        if m.group(1) in segs: die(f'дубль правила {m.group(1)}')
        segs[m.group(1)] = x
new, done, todo = body, [], []
for r in RULES:
    if r not in segs: die(f'правила {r} немає')
    seg = segs[r]
    if body.count(seg) != 1: die(f'{r}: сегмент не унікальний ({body.count(seg)})')
    det = blocks[f'{r} det']; trig = blocks.get(f'{r} trig')
    has_det = seg.count(det) == 1; has_trig = trig is None or seg.count(trig) == 1
    if has_det and has_trig: done.append(r); continue
    if (seg.count(det) > 0) != (trig is not None and seg.count(trig) > 0) and trig is not None: die(f'{r}: половинний стан (det={seg.count(det)} trig={seg.count(trig)})')
    if seg.count(det) or (trig and seg.count(trig)): die(f'{r}: частковий стан')
    s = seg
    if trig:
        head = s.split('\n', 1)[0]
        if not s[len(head):].startswith('\n\n'): die(f'{r}: після заголовка немає порожнього рядка {s[len(head):len(head)+6]!r}')
        s = head + '\n\n' + trig + '\n\n' + s[len(head) + 2:]
    ORIG = '\n> *Походження'
    if s.count(ORIG) == 1:
        s = s.replace(ORIG, '\n\n' + det + '\n' + ORIG)
    elif s.count(ORIG) == 0:
        tail = s[len(s.rstrip('\n')):]
        s = s.rstrip('\n') + '\n\n' + det + '\n' + tail
    else: die(f'{r}: «Походження» {s.count(ORIG)} разів')
    if s.count('**Детектор (К2).**') + s.count('K2:n/a') < 1: die(f'{r}: після збірки немає детектора')
    new = new.replace(seg, s); todo.append(r)

VER_ANCH = '> **Версія 2.35** (17.09.2026'
ver = blocks['wsd ver']
if new.count(ver) == 1: done.append('ver')
elif new.count(VER_ANCH) == 1 and new.count('**Версія 2.36**') == 0:
    new = new.replace(VER_ANCH, ver + '\n' + VER_ANCH); todo.append('ver')
else: die(f'шапка: якір 2.35={new.count(VER_ANCH)} 2.36={new.count("**Версія 2.36**")}')

if todo and len(todo) != len(RULES) + 1: die(f'частковий стан файла: зроблено {done}, треба {todo}')
nb = len(new.encode())
if nb > 200_000: die(f'wsd {nb} B > 200 KB (G6 червона межа)')

# ── прохід 2: запис ────────────────────────────────────────────────────
if not todo:
    print('no-op: усе вже застосовано', done); sys.exit(0)
open(WSD, 'w', encoding='utf-8').write(new)
print(f'записано Work_Standard.md {len(body.encode())} → {nb} B · {old_md5[:8]} → {hashlib.md5(new.encode()).hexdigest()[:8]} · {todo}')
