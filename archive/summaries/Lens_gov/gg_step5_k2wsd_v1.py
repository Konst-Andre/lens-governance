#!/usr/bin/env python3
# живе доки: G-G5 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-G5: К2-1 wsd група 3 — детектори/тригери/K2:n/a за GG5_k2_wsd_texts_v1.md §2 + шапка 2.39.
# Тексти — лише з файла текстів (не дублюються тут). Прохід 1 — перевірки в пам'яті; прохід 2 — запис (Ф-4). Повтор → no-op.
import sys, os, re, hashlib
ROOT  = sys.argv[1] if len(sys.argv) > 1 else '.'
TEXTS = sys.argv[2] if len(sys.argv) > 2 else '/mnt/user-data/outputs/GG5_k2_wsd_texts_v1.md'
WSD   = os.path.join(ROOT, 'kernel', 'wsd', 'Work_Standard.md')
def die(m): print('STOP:', m); sys.exit(1)

RULES = ['12.2', '12.3', '12.4', '12.5', '12.9', '12.13', '13.1', '13.3']
TRIG  = ['12.2', '12.3', '12.4', '12.5', '12.9', '13.1']
NA    = ['12.5', '13.1', '13.3']

# ── прохід 1: розбір текстів ──────────────────────────────────────────
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
need = {f'{r} det' for r in RULES} | {f'{r} trig' for r in TRIG} | {'wsd ver'}
if set(blocks) != need: die(f'набір блоків ≠ очікуваний: зайві {set(blocks)-need} · бракує {need-set(blocks)}')
for k, v in blocks.items():
    if not v.strip(): die(f'порожній блок {k}')
    if k.endswith('trig') and not v.startswith('**Тригер.**'): die(f'{k}: не починається з **Тригер.**')
    if k.endswith('det'):
        r = k.split()[0]
        if r in NA:
            if not re.fullmatch(r'<!-- K2:n/a\s*—\s*\S.*-->', v): die(f'{r}: маркер K2:n/a не за формою (латинська K, причина обов\'язкова)')
        elif not v.startswith('**Детектор (К2).**'): die(f'{k}: не починається з **Детектор (К2).**')

# ── прохід 1: розбір wsd і обчислення нового вмісту ───────────────────
body = open(WSD, encoding='utf-8').read()
old_md5 = hashlib.md5(body.encode()).hexdigest()
segs = {}
for x in re.split(r'\n(?=#{1,6}\s)', body):          # межа — БУДЬ-ЯКИЙ заголовок, інакше сегмент ковтає «# Кластер»
    m = re.match(r'##\s+(\d+\.\d+)\s', x)
    if m:
        if m.group(1) in segs: die(f'дубль правила {m.group(1)}')
        segs[m.group(1)] = x

new, done, todo = body, [], []
for r in RULES:
    if r not in segs: die(f'правила {r} немає')
    seg = segs[r]
    if body.count(seg) != 1: die(f'{r}: сегмент не унікальний ({body.count(seg)})')
    det  = blocks[f'{r} det']
    trig = blocks.get(f'{r} trig')
    n_det  = seg.count(det)
    n_trig = seg.count(trig) if trig else 1
    if n_det == 1 and n_trig == 1: done.append(r); continue
    if n_det or (trig and seg.count(trig)): die(f'{r}: половинний стан (det={n_det} trig={n_trig})')
    s = seg
    if trig:
        head = s.split('\n', 1)[0]
        if not s[len(head):].startswith('\n\n'): die(f'{r}: після заголовка немає порожнього рядка {s[len(head):len(head)+6]!r}')
        rest = s[len(head) + 2:]
        if rest.startswith('> '):                       # блокквота одразу під заголовком — тригер ПІСЛЯ неї
            q = rest.split('\n\n', 1)
            if len(q) != 2: die(f'{r}: блокквота без порожнього рядка після неї')
            s = head + '\n\n' + q[0] + '\n\n' + trig + '\n\n' + q[1]
        else:
            s = head + '\n\n' + trig + '\n\n' + rest
    if '> *Походження' in s: die(f'{r}: є «Походження» — гілка не передбачена цим скриптом')
    tail = s[len(s.rstrip('\n')):]
    core = s.rstrip('\n')
    if core.endswith('-----'):                          # детектор ПЕРЕД роздільником, не після
        core = core[:-len('-----')].rstrip('\n')
        if core.endswith('-----'): die(f'{r}: два роздільники поспіль — межа правила неясна')
        s = core + '\n\n' + det + '\n\n-----' + tail
    else:
        s = core + '\n\n' + det + '\n' + tail
    if s.count('**Детектор (К2).**') + s.count('K2:n/a') < 1: die(f'{r}: після збірки немає детектора')
    new = new.replace(seg, s); todo.append(r)

VER_ANCH = '> **Версія 2.38** (17.09.2026'
ver = blocks['wsd ver']
if new.count(ver) == 1: done.append('ver')
elif new.count(VER_ANCH) == 1 and new.count('**Версія 2.39**') == 0:
    new = new.replace(VER_ANCH, ver + '\n' + VER_ANCH); todo.append('ver')
else: die(f'шапка: якір 2.37={new.count(VER_ANCH)} 2.38={new.count("**Версія 2.39**")}')

if todo and len(todo) != len(RULES) + 1: die(f'частковий стан файла: зроблено {done}, лишилось {todo}')
nb = len(new.encode())
if nb > 200_000: die(f'wsd {nb} B > 200 KB (G6 червона межа)')

# ── прохід 2: запис ───────────────────────────────────────────────────
if not todo:
    print('no-op: усе вже застосовано', done); sys.exit(0)
open(WSD, 'w', encoding='utf-8').write(new)
back = open(WSD, encoding='utf-8').read()
if back != new: die('read-back розійшовся')
print(f'записано Work_Standard.md {len(body.encode())} → {nb} B · {old_md5[:8]} → {hashlib.md5(new.encode()).hexdigest()[:8]} · {todo}')
