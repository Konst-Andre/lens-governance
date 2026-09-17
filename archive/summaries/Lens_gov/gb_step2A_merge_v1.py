#!/usr/bin/env python3
# живе доки: G-B2 влив групи Б/В і пушив manifest+буфер (read-back ✓) — далі слід у самері
"""G-B крок 2 · група А: Д-Д §8.12 · Д-Е §8.7-д · Д-З §8.14 · Д-И §8.15 · Д-І §8.16 · Д-Л §8.17.
Буфер → manifest дослівно (gov 12.16): заголовок `## Д-X · §N Назва` → `### N Назва` + рядок провенансу;
Д-Е — перед `### 8.8`, решта — у кінець по зростанню; записи знімаються з буфера, ЛОТОК −6. Повтор = no-op."""
import re, sys, pathlib
K = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'kernel')
PB, PM = K/'Lens_stagebench_delta_running.md', K/'Lens_stagebench_manifest.md'
b, m = PB.read_text(encoding='utf-8'), PM.read_text(encoding='utf-8')
IDS = ['Д-Е', 'Д-Д', 'Д-З', 'Д-И', 'Д-І', 'Д-Л']
NA = {'Д-З': '<!-- K2:n/a — правило саме про детектор; порушення ловиться `--inject` на детекторі, не грепом -->'}
def die(x): print('✗ СТОП:', x); sys.exit(2)

done = [i for i in IDS if f'*(влито з буфера `{i}`, G-B 17.09.2026)*' in m]
if len(done) == len(IDS) and all(f'## {i} · ' not in b for i in IDS):
    print('· група А уже влита (no-op)'); sys.exit(0)
if done: die(f'часткове вливання: {done}')

blocks = {}
for i in IDS:
    if b.count(f'\n## {i} · ') != 1: die(f'{i}: заголовок у буфері ≠1')
    s = b.index(f'\n## {i} · ') + 1; e = b.find('\n## ', s); e = len(b) if e < 0 else e + 1
    sec = b[s:e]
    h, body = sec.split('\n', 1)
    mm = re.match(r'## ' + re.escape(i) + r' · §([\d.]+(?:-[а-я])?) (.+)$', h)
    if not mm: die(f'{i}: заголовок не розібрано')
    num, title = mm.groups()
    if re.search(r'^### ' + re.escape(num) + ' ', m, re.M): die(f'{i}: ### {num} уже є в manifest')
    body = re.sub(r'\n+---\s*$', '', body.strip('\n')).rstrip()
    extra = ('\n\n' + NA[i]) if i in NA else ''
    blocks[i] = (num, f'### {num} {title}\n\n*(влито з буфера `{i}`, G-B 17.09.2026)*\n\n{body}{extra}\n', sec)

# Д-Е перед ### 8.8
if m.count('\n### 8.8 ') != 1: die('якір ### 8.8 ≠1')
a = m.index('\n### 8.8 ') + 1
m = m[:a] + blocks['Д-Е'][1] + '\n' + m[a:]
# решта в кінець по зростанню
for i in sorted(IDS[1:], key=lambda x: float(blocks[x][0])):
    m = m.rstrip('\n') + '\n\n' + blocks[i][1]
# з буфера
for i in IDS:
    if b.count(blocks[i][2]) != 1: die(f'{i}: секція в буфері ≠1')
    b = b.replace(blocks[i][2], '')
b = re.sub(r'\n{3,}(## )', r'\n\n\1', b)
lot = re.search(r'\*\*ЛОТОК: (\d+) запис', b)
if not lot or lot.group(1) != '15': die('ЛОТОК ≠ 15')
b = b.replace('**ЛОТОК: 15 запис(ів).**', '**ЛОТОК: 9 запис(ів).** *(G-B 17.09.2026: група А — Д-Д · Д-Е · Д-З · Д-И · Д-І · Д-Л — влита в manifest §8.7-д · §8.12 · §8.14–§8.17)*', 1)
PM.write_text(m, encoding='utf-8'); PB.write_text(b, encoding='utf-8')
print('✓ влито:', ', '.join(f'{i}→§{blocks[i][0]}' for i in IDS)); print('✓ ЛОТОК 15→9')
