#!/usr/bin/env python3
"""G-I крок 1 — INTAKE заводиться дописком у рядок `К3-1` gov-черги, не новим id.
   Живе доки: коміт із цією правкою в main (разовий, потім → archive/scripts).
   Підстава форми: Ф-10 (черга не тримає нових рядків) · 12.16 (правка скриптом
   за унікальним якорем) · 12.11 (дім названо: kernel/Lens_governance_CHERGA.md, рядок К3-1).
"""
import sys, hashlib, os

CEIL = 8192
PATH = sys.argv[1] if len(sys.argv) > 1 else 'kernel/Lens_governance_CHERGA.md'

OLD = ('| `К3-1` | **Досяжність правила:** без точки виклику й детектора — мертвий текст. '
       'Аудит сиріт, битих адрес і жанрів + форма прополки (гейт · чек-лист · ADR · архів). '
       'Вісь — `К4-1`. Текст: самері `GC2b §2` · `GD §2` | 17.09.2026 | '
       'гейт рахує сиріт і биті адреси; кожна сирота має виклик, детектор або виселена |')

NEW = ('| `К3-1` | **Досяжність правила:** без точки виклику й детектора — мертвий текст. '
       'Аудит сиріт/адрес/жанрів + форма прополки. '
       '**INTAKE** — ворота народження правила: шматки в `13.2`·К1/К2·`12.11`, конвеєра нема; '
       '`13.2` шле в `12.11`, закритий у продуктовій сесії. '
       'Вісь — `К4-1`. Текст: `GC2b §2` · `GD §2` · `G-I §2` | 17.09.2026 | '
       'гейт рахує сиріт і биті адреси; кожна сирота має виклик, детектор або виселена; '
       'INTAKE — секція в gov-протоколі + `G20` |')

txt = open(PATH, encoding='utf-8').read()
before = len(txt.encode())

n = txt.count(OLD)
if n != 1:
    print(f'✗ якір не унікальний: count={n}')
    sys.exit(1)

out = txt.replace(OLD, NEW)
after = len(out.encode())

print(f'якір  ✓ count=1')
print(f'було  {before} B · стало {after} B · дельта {after-before:+d} B')
print(f'стеля {CEIL} · запас {CEIL-after} B')

if after > CEIL:
    print('✗ вихід за стелю — не записую')
    sys.exit(1)

open(PATH, 'w', encoding='utf-8').write(out)
print('md5', hashlib.md5(out.encode()).hexdigest())
print('✓ записано:', os.path.abspath(PATH))
