#!/usr/bin/env python3
# живе доки: G-B3 запушено — далі архів (пакет відтворення стану)
# G-B3 · Д-Б (урізаний, 12.17/12.18) → manifest кінець §8.9; буфер: Д-Б видалено, ЛОТОК 2→1.
# Запуск з кореня клону: python3 gb3_step1B_merge_v1.py kernel GB3_DB_texts_v1.md
import sys, re, pathlib
def stop(x): print('✗ СТОП:', x); sys.exit(2)
k = pathlib.Path(sys.argv[1]); tx = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')
mm = re.search(r'<<<S89\n(.*?)\n>>>', tx, re.S)
if not mm: stop('немає блоку S89')
S = mm.group(1)
mp = k / 'Lens_stagebench_manifest.md'; bp = k / 'Lens_stagebench_delta_running.md'
m = mp.read_text(encoding='utf-8'); b = bp.read_text(encoding='utf-8')
DB = re.search(r'\n## Д-Б · .*?\n---\n(?=\n## )', b, re.S)
state = [m.count(S) == 1, DB is None]
if all(state): print('· Д-Б уже влито (no-op)'); sys.exit(0)
if any(state): stop(f'часткове вливання {state}')
A = '\n### 8.10 '
if m.count(A) != 1: stop(f'якір 8.10 ×{m.count(A)}')
if len(re.findall(r'\n## Д-Б · ', b)) != 1: stop('Д-Б у буфері ≠1')
lot = re.search(r'\*\*ЛОТОК: (\d+) запис\(ів\)\.\*\*', b)
if not lot or lot.group(1) != '2': stop(f'ЛОТОК ≠ 2 ({lot.group(1) if lot else None})')
i = m.index(A); head = m[:i].rstrip('\n')
m = head + '\n\n' + S + '\n\n' + m[i:].lstrip('\n')
b = b[:DB.start()] + '\n' + b[DB.end():].lstrip('\n')
b = b.replace('**ЛОТОК: 2 запис(ів).** *(G-B3 17.09.2026: Д-А', '**ЛОТОК: 1 запис(ів).** *(G-B3 17.09.2026: Д-Б урізаний → manifest §8.9, решта погашена A69/H3)* *(G-B3 17.09.2026: Д-А', 1)
mp.write_text(m, encoding='utf-8'); bp.write_text(b, encoding='utf-8')
print('✓ влито: Д-Б→§8.9 (залишок)'); print('✓ ЛОТОК 2→1')
