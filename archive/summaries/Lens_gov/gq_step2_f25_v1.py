#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-Q крок 2 — §0 п.2 самері G-P, Ф-25: ознака маршрутної заглушки в G16/G21 — структурна,
   не підрядок 'ROUTING'. + К2 Ф-25: заглушка ≥ 400 B → ⚠ «виключено як маршрут».
   живе доки: хід 2 сесії G-Q не влитий у репо.
   Заглушка = фрагмент номера (обрізаний на першому h1 `# `), у якому після рядка-заголовка
   кожен непорожній рядок (крім `-----`) — цитата `>`, і хоч один — `> **ROUTING →`.
   Поріг `< 400 B` (короткий фрагмент не рахується) — без змін, поза Ф-25.
   12.16: усі стопи вище першого запису; якорі — repr, count == 1. Працює на staging.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5."""
import sys, os
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx2'
P = os.path.join(STG, 'kernel/Lens_validate.py')
def die(m): print('✗ СТОП:', m); sys.exit(1)

HELP_A = ("      G21 номер правила з тілом визначений рівно в одному файлі RULE_FILES → інакше ✗\n"
          "         (розпил wsd, IDX-7: перенос без вирізання дає дубль, якого не бачить ніхто)\n")
HELP_N = HELP_A + ("         Маршрутна заглушка (G16 · G21) — за структурою, не за словом (Ф-25): тіло до h1 —\n"
                   "         лише цитати, одна з них `> **ROUTING →`. Заглушка ≥ 400 B → ⚠ «виключено як маршрут»\n")
RF_A = ("RULE_FILES = {'Work_Standard.md': 'wsd', 'Lens_governance_protocol.md': 'gov', 'Lens_PROFILE.md': 'prof', "
        "'Lens_verdict_protocol.md': 'verd', 'Lens_patch_check_protocol.md': 'chk'}\n")
RF_N = RF_A + '''

def route_body(part):
    """Фрагмент номера без хвоста файлу: зріз на першому h1 (`# …`) — інакше останнє правило
    файлу тягне за собою розділ «# Історія…» і заглушка виглядає тілом (wsd 12.19, G-Q)."""
    return re.split(r'\\n(?=# )', part)[0]


def is_route(part):
    """Ф-25: маршрутна заглушка — структурно. Після заголовка кожен непорожній рядок
    (крім `-----`) — цитата, і хоч одна — `> **ROUTING →`. Слово ROUTING у тілі правила
    (заголовок gov 12.11, приклад у тексті) заглушкою його НЕ робить."""
    ls = [l for l in route_body(part).splitlines()[1:] if l.strip() and not re.fullmatch(r'-{3,}', l.strip())]
    return bool(ls) and all(l.startswith('>') for l in ls) and any(re.match(r'>\\s*\\*\\*ROUTING\\s*→', l) for l in ls)
'''
G16A_A = "            if 'ROUTING' in r_ or len(r_.encode('utf-8')) < 400:\n"
G16A_N = "            if is_route(r_) or len(r_.encode('utf-8')) < 400:\n"
G16B_A = "            if not ('ROUTING' in r_ or len(r_.encode('utf-8')) < 400)\n"
G16B_N = "            if not (is_route(r_) or len(r_.encode('utf-8')) < 400)\n"
DOC_A = "    Маршрут (ROUTING або <400 B) — не тіло: на старому місці він законний.\"\"\"\n"
DOC_N = ("    Маршрут (заглушка за is_route, Ф-25, або <400 B) — не тіло: на старому місці він законний.\n"
         "    К2 Ф-25: заглушка ≥ 400 B → ⚠ — тихе виключення стає видимим.\"\"\"\n")
G21A_A = ("    homes, nfiles = {}, 0\n")
G21A_N = ("    homes, nfiles, big = {}, 0, []\n")
G21B_A = ("            if not m or 'ROUTING' in part or len(part.encode('utf-8')) < 400:\n"
          "                continue\n")
G21B_N = ("            if not m:\n"
          "                continue\n"
          "            if is_route(part):\n"
          "                nb = len(route_body(part).encode('utf-8'))\n"
          "                if nb >= 400:\n"
          "                    big.append(f'{kind} {m.group(1)} ({nb} B)')\n"
          "                continue\n"
          "            if len(part.encode('utf-8')) < 400:\n"
          "                continue\n")
G21C_A = ("        warn('жодного файлу правил не знайдено — G21 не виконався, це НЕ зелений результат')\n"
          "        return\n")
G21C_N = G21C_A + ("    if big:\n"
                   "        warn('виключено як маршрут, але ≥ 400 B (Ф-25) — перевір, чи не тіло: ' + ' · '.join(big))\n")
EDITS = [(HELP_A, HELP_N), (RF_A, RF_N), (G16A_A, G16A_N), (G16B_A, G16B_N), (DOC_A, DOC_N),
         (G21A_A, G21A_N), (G21B_A, G21B_N), (G21C_A, G21C_N)]

src = open(P, encoding='utf-8').read()
old_ok = all(src.count(a) == 1 for a, _ in EDITS) and src.count('def is_route') == 0
new_ok = all(src.count(n) == 1 for _, n in EDITS) and src.count("'ROUTING' in") == 0
if new_ok:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if not old_ok:
    die('стан змішаний: ' + ' '.join(f'{i}:{src.count(a)}/{src.count(n)}' for i, (a, n) in enumerate(EDITS)))
if src.count("'ROUTING' in") != 3: die(f"очікувано 3 входження 'ROUTING' in, є {src.count(chr(39)+'ROUTING'+chr(39)+' in')}")
new = src
for a, n in EDITS: new = new.replace(a, n, 1)
# Ф-20: доказ позиційний — зворотна заміна дає рівно старий файл
back = new
for a, n in reversed(EDITS):
    i = back.index(n); back = back[:i] + a + back[i + len(n):]
if back != src: die('позиційний revert ≠ старий файл')
if "'ROUTING' in" in new: die("лишився 'ROUTING' in")
open(P, 'w', encoding='utf-8').write(new)
print(f'✓ Lens_validate.py {len(src.encode()):6d} → {len(new.encode()):6d} B · 8 правок · revert == old')
