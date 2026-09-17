#!/usr/bin/env python3
# живе доки: G-B3 запушено — далі архів (пакет відтворення стану)
# G-B3 · §0 п.3 (GB2): літерні адреси 2.4(a)/(b)/(c)/(d) у manifest → §8.4-(x). Голі «wsd 2.4» не чіпати (§8 р.305: маршрут дійсний).
# Запуск з кореня клону: python3 gb3_step1D_addr_v1.py kernel
import sys, re, pathlib
def stop(x): print('✗ СТОП:', x); sys.exit(2)
mp = pathlib.Path(sys.argv[1]) / 'Lens_stagebench_manifest.md'; m = mp.read_text(encoding='utf-8')
LET = r'(?<![`§\w])2\.4\(([abcd])\)'
# зона: від «## §2.» до «## §5.» (рядки 47–187); історичні згадки поза нею не адреси
s = m.index('\n## §2. '); e = m.index('\n## §5. ')
zone = m[s:e]; n = len(re.findall(LET, zone))
if n == 0 and '§8.4-(' in zone: print('· адреси уже замінено (no-op)'); sys.exit(0)
if n != 6: stop(f'очікував 6 літерних адрес у §2–§4, знайшов {n}')
if re.search(LET, m[:s] + m[e:]): stop('літерна адреса поза зоною — вирішувати поштучно')
zone = re.sub(LET, r'§8.4-(\1)', zone)
mp.write_text(m[:s] + zone + m[e:], encoding='utf-8'); print('✓ 6 адрес 2.4(x) → §8.4-(x)')
