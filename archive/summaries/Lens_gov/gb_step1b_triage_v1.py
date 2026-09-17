#!/usr/bin/env python3
# живе доки: злиття G-B (крок 2) виконано — далі слід у самері G-B
"""G-B 1б: тріаж stagebench-буфера — 12.17 (grep -c по канону) · 12.18 (перетин ключів) · К2 · покажчики."""
import re, sys, pathlib
R = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.'); K = R/'kernel'
buf = (K/'Lens_stagebench_delta_running.md').read_text(encoding='utf-8')
canon = {'man': K/'Lens_stagebench_manifest.md', 'wsd': K/'wsd/Work_Standard.md',
         'gov': K/'wsd/Lens_governance_protocol.md'}
for p in sorted((K/'cookbook').glob('*.md')):
    canon['cb:' + p.stem.replace('Lens_cookbook_', '')] = p
ct = {k: v.read_text(encoding='utf-8') for k, v in canon.items()}
KEYS = {'Д-А': ['copy-from'], 'Д-Б': ['auto-dark', 'A69'], 'Д-В': ['userAgent'], 'Д-В2': ['живого коду'],
 'Д-Г': ['HARNESS'], 'Г-9': ['user-select', 'копіюван'], 'Д-Д': ['ієрарх'], 'Д-Е': ['ПІДСТАВ'],
 'Д-Ж': ['паспорт'], 'Д-З': ['одиниц'], 'Д-И': ['паритет'], 'Д-К': ['покатегорійно'],
 'Д-І': ['сусідн'], 'Д-Л': ['оптичн'], 'Д-М': ['самостійний прохід']}
hs = [(m.start(), m.group(1)) for m in re.finditer(r'^## ((?:Д|Г)-[А-ЯІ]\d?|Г-\d+) · ', buf, re.M)]
body = {i: buf[s:(hs[n+1][0] if n+1 < len(hs) else len(buf))] for n, (s, i) in enumerate(hs)}
print('## 12.17 · grep -c ключів у каноні (без обрізання)')
for i, ks in KEYS.items():
    row = []
    for k in ks:
        hits = {f: len(re.findall(re.escape(k), t, re.I)) for f, t in ct.items()}
        hits = {f: c for f, c in hits.items() if c}
        row.append(f'`{k}`: ' + (', '.join(f'{f}={c}' for f, c in hits.items()) or '0'))
    print(f'- {i}: ' + ' · '.join(row))
print('\n## 12.18 · ключ запису X у тілі запису Y')
for i, ks in KEYS.items():
    ov = [j for j in body if j != i and any(re.search(re.escape(k), body[j], re.I) for k in ks)]
    if ov: print(f'- {i} ← у тілах: {", ".join(ov)}')
print('\n## К2 · поштучно')
for i, b in body.items():
    det = re.findall(r'(\*\*Детектор[^*]*\*\*|K2:n/a[^>]*|### Детектор[^\n]*|### Діагностика[^\n]*)', b)
    print(f'- {i}: ' + (det[0][:60] if det else 'НЕМАЄ'))
print('\n## Покажчики · адреси файлів у тілі')
for i in ['Г-9', 'Д-Ж', 'Д-М']:
    fs = sorted(set(re.findall(r'`?([\w.-]+\.(?:md|html|js|py))`?', body[i])))
    print(f'- {i}: {fs}')
