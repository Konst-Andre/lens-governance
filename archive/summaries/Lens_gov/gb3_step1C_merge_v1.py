#!/usr/bin/env python3
# живе доки: G-B3 запушено — далі архів (пакет відтворення стану)
# G-B3 · Д-К (урізаний, 12.17/12.18) → manifest §2 рядок 7 (+ адреси 2.4(a)/(d) → §8.4); буфер: Д-К видалено, ЛОТОК 1→0.
# Запуск з кореня клону: python3 gb3_step1C_merge_v1.py kernel GB3_DK_texts_v1.md
import sys, re, pathlib
def stop(x): print('✗ СТОП:', x); sys.exit(2)
k = pathlib.Path(sys.argv[1]); tx = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')
mm = re.search(r'<<<R7\n(.*?)\n>>>', tx, re.S)
if not mm: stop('немає блоку R7')
R7 = mm.group(1)
mp = k / 'Lens_stagebench_manifest.md'; bp = k / 'Lens_stagebench_delta_running.md'
m = mp.read_text(encoding='utf-8'); b = bp.read_text(encoding='utf-8')
OLD = '| 7 | **Стилізовані панелі важелів** | докнуті збоку/знизу, **НЕ оверлеєм стейджа** (2.4(a)); **згортувані** caret-тоглом для чистого скріну (2.4(d)) |'
DK = re.search(r'\n## Д-К · .*\Z', b, re.S)
state = [m.count(OLD) == 0 and m.count(R7) == 1, DK is None]
if all(state): print('· Д-К уже влито (no-op)'); sys.exit(0)
if any(state): stop(f'часткове вливання {state}')
if m.count(OLD) != 1: stop(f'якір §2 р.7 ×{m.count(OLD)}')
if len(re.findall(r'\n## Д-', b)) != 1: stop('у буфері не рівно один запис')
lot = re.search(r'\*\*ЛОТОК: (\d+) запис\(ів\)\.\*\*', b)
if not lot or lot.group(1) != '1': stop(f'ЛОТОК ≠ 1 ({lot.group(1) if lot else None})')
OLDW = '⚠ стеля 2–3 сесії прострочена з 13.08.2026 — це видимий борг, не норма'
if b.count(OLDW) != 1: stop(f'якір шапки ×{b.count(OLDW)}')
m = m.replace(OLD, R7, 1)
b = b[:DK.start()].rstrip('\n') + '\n'
b = re.sub(r'\n---\n*\Z', '\n', b)  # хвостовий роздільник після останнього запису не лишати
b = b.replace('**ЛОТОК: 1 запис(ів).** *(G-B3 17.09.2026: Д-Б', '**ЛОТОК: 0 запис(ів).** *(G-B3 17.09.2026: Д-К урізаний → manifest §2-п.7, решта погашена §8.12/§8.4-(a); група В закрита)* *(G-B3 17.09.2026: Д-Б', 1)
b = b.replace(OLDW, 'буфер порожній з G-B3 17.09.2026 (стеля 2–3 сесії була прострочена 13.08→17.09.2026)', 1)
mp.write_text(m, encoding='utf-8'); bp.write_text(b, encoding='utf-8')
print('✓ влито: Д-К→§2-п.7 (залишок, адреси §8.4)'); print('✓ ЛОТОК 1→0')
