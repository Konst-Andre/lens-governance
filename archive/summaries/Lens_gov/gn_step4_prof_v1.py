#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-N крок 4 — С6 розпилу wsd, частина 3 (§0 п.2 G-M): дублі-конспекти в Lens_PROFILE.md (12.18).
   §3 «Двійне пояснення (wsd 13.3)» і пункт §4 «Віджет ask_user_input_v0 (wsd 13.1)» — тіла правил
   лежать у тому ж файлі (§7). Звірено цілком (12.16): у конспектах унікального немає, крім статусу
   «головне правило комунікації» — він лишається у вказівнику. Заголовок §3 лишається (G13, нумерація).
   Пункт «Проактивні пропозиції (13.2)» — той самий клас, НЕ чіпається (тіло 13.2 не прочитано цілком).
   живе доки: хід 4 сесії G-N не влитий у репо.
   Стоп: md5 §7 до == після. П34/П37: повтор → exit 0, той самий md5."""
import sys, os, hashlib
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
P = os.path.join(STG, 'kernel/Lens_PROFILE.md')
def die(m): print('✗ СТОП:', m); sys.exit(1)
t = open(P, encoding='utf-8').read()
H3 = '## §3 Двійне пояснення (wsd 13.3) — головне правило комунікації\n\n'
i3 = t.find(H3); e3 = t.find('\n---\n\n## §4 Формат відповіді', i3)
W0 = '- **Віджет `ask_user_input_v0`** (wsd 13.1) — показувати'
W1 = '- **Проактивні пропозиції** (wsd 13.2)'
N3 = H3 + 'Головне правило комунікації. Тіло — §7 `13.3` (два рівні разом, без побутових аналогій).\n'
NW = '- **Віджет `ask_user_input_v0`** — тіло правила: §7 `13.1`.\n'
def s7(x):
    return hashlib.md5(x[x.index('## §7 '):].encode()).hexdigest()
if t.count(N3) == 1 and t.count(NW) == 1 and t.count(W0) == 0:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if t.count(H3) != 1 or e3 < 0: die(f'якір §3 ×{t.count(H3)} / кінець {e3}')
if t.count(W0) != 1 or t.count(W1) != 1: die(f'якорі §4: віджет ×{t.count(W0)} · 13.2 ×{t.count(W1)}')
iw = t.index(W0); ew = t.index(W1)
if not (i3 < e3 < iw < ew < t.index('## §7 ')): die('порядок якорів не той')
before = s7(t)
t2 = t[:i3] + N3 + t[e3:iw] + NW + t[ew:]
if s7(t2) != before: die('§7 змінився')
open(P, 'w', encoding='utf-8').write(t2)
print(f'✓ Lens_PROFILE.md {len(t.encode())} → {len(t2.encode())} B · §7 md5 {before[:8]} незмінний')
