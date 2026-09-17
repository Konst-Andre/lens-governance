#!/usr/bin/env python3
# живе доки: G-B3 запушено — далі архів (пакет відтворення стану)
# G-B3 · Д-А → manifest §6 (заміна еталона) + §7 БОРГ закрито; буфер: Д-А видалено, ЛОТОК 3→2.
# Запуск з кореня клону: python3 gb3_step1A_merge_v1.py kernel GB3_DA_texts_v1.md
import sys, re, pathlib
def stop(x): print('✗ СТОП:', x); sys.exit(2)
k = pathlib.Path(sys.argv[1]); tx = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')
def blk(n):
    m = re.search(r'<<<' + n + r'\n(.*?)\n>>>', tx, re.S)
    if not m: stop('немає блоку ' + n)
    return m.group(1)
S6, S7 = blk('S6'), blk('S7')
mp = k / 'Lens_stagebench_manifest.md'; bp = k / 'Lens_stagebench_delta_running.md'
m = mp.read_text(encoding='utf-8'); b = bp.read_text(encoding='utf-8')
OLD6 = ('- **`StockCheck_island_harness_v2.html`** — поточний gold-standard: дуал device-frame (XS/light ‖ 15Pro/dark),\n'
        '  реальний масштаб, повний інтерактивний інструмент зі скролом, P0–P3 пресети, copy-bet, згортувана панель\n'
        '  (2.4(d)), реальні токени, живий контент під склом. Брати як шаблон нового stage-bench.')
OLD7 = ('**БОРГ:** зум відсутній в обох референс-шаблонах (§6). Перший стенд, що його реалізує,\n'
        'стає новим copy-from еталоном → оновити §6.')
DA = re.search(r'\n## Д-А · .*?\n---\n(?=\n## )', b, re.S)
state = [m.count(OLD6) == 0 and m.count(S6) == 1, m.count(OLD7) == 0 and m.count(S7) == 1, DA is None]
if all(state): print('· Д-А уже влито (no-op)'); sys.exit(0)
if any(state): stop(f'часткове вливання {state}')
if m.count(OLD6) != 1: stop(f'якір §6 ×{m.count(OLD6)}')
if m.count(OLD7) != 1: stop(f'якір §7 ×{m.count(OLD7)}')
if len(re.findall(r'\n## Д-А · ', b)) != 1: stop('Д-А у буфері ≠1')
lot = re.search(r'\*\*ЛОТОК: (\d+) запис\(ів\)\.\*\*', b)
if not lot or lot.group(1) != '3': stop(f'ЛОТОК ≠ 3 ({lot.group(1) if lot else None})')
m = m.replace(OLD6, S6, 1).replace(OLD7, S7, 1)
b = b[:DA.start()] + '\n' + b[DA.end():].lstrip('\n')
b = b.replace('**ЛОТОК: 3 запис(ів).**', '**ЛОТОК: 2 запис(ів).** *(G-B3 17.09.2026: Д-А влито в manifest §6 + §7 БОРГ закрито)*', 1)
mp.write_text(m, encoding='utf-8'); bp.write_text(b, encoding='utf-8')
print('✓ влито: Д-А→§6 (еталон maint_v3), §7 БОРГ закрито'); print('✓ ЛОТОК 3→2')
