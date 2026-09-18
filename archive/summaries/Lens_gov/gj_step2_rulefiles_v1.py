#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-J крок 2 (С1 розпилу wsd, IDX-7): гейт першим, канон потім.
   · RULE_FILES — одна оголошена константа (1.10), її читають G4 · G16 · G19 · G21
   · G4 (14.x → HISTORY) — по всіх файлах правил (сліпа зона з шапки gov-протоколу, S14)
   · G21 (новий) — номер правила з тілом визначений рівно в одному файлі правил
   · Lens_INDEX §5 — список написаних гейтів, перший вільний G22
   живе доки: С1 не влитий у репо.
   12.16: усі стопи до першого запису. П34/П37: повтор на застосованому → exit 0."""
import sys, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
V = os.path.join(ROOT, 'kernel/Lens_validate.py')
I = os.path.join(ROOT, 'kernel/Lens_INDEX.md')

def die(m): print('✗ СТОП:', m); sys.exit(1)

E = []  # (файл, старе, нове)

E.append((V,
"LIVE_DIRS = []          # теки живих самері (Project) для G19 — --live\n",
"LIVE_DIRS = []          # теки живих самері (Project) для G19 — --live\n"
"# Файли правил — ОГОЛОШЕННЯ, не здогад (wsd 1.10). Новий дім правил = рядок тут\n"
"# + рядок у Lens_INDEX. Читають G4 · G16 · G19 · G21. Мітка — у виводі G19/G21.\n"
"RULE_FILES = {'Work_Standard.md': 'wsd', 'Lens_governance_protocol.md': 'gov'}\n"))

E.append((V,
"         Project, не в репо — тому тека з ними додається: --gov . --live <тека>\n",
"         Project, не в репо — тому тека з ними додається: --gov . --live <тека>\n"
"      G21 номер правила з тілом визначений рівно в одному файлі RULE_FILES → інакше ✗\n"
"         (розпил wsd, IDX-7: перенос без вирізання дає дубль, якого не бачить ніхто)\n"))

E.append((V,
"    # G4 — 14.x резолвляться\n"
"    print('\\n[G4] посилання 14.x з wsd → HISTORY')\n"
"    w, h = R(root, 'Work_Standard.md'), R(root, 'Work_Standard_HISTORY.md')\n"
"    if os.path.exists(w) and os.path.exists(h):\n"
"        refs = sorted(set(re.findall(r'\\b14\\.\\d+\\b', open(w, encoding='utf-8').read())))\n",
"    # G4 — 14.x резолвляться (з G-J — з УСІХ файлів правил, не лише wsd)\n"
"    print('\\n[G4] посилання 14.x з файлів правил → HISTORY')\n"
"    h = R(root, 'Work_Standard_HISTORY.md')\n"
"    srcs = [R(root, f) for f in RULE_FILES if os.path.exists(R(root, f))]\n"
"    if srcs and os.path.exists(h):\n"
"        refs = sorted(set(r for p in srcs for r in\n"
"                          re.findall(r'\\b14\\.\\d+\\b', open(p, encoding='utf-8').read())))\n"))

E.append((V,
"        warn('wsd або HISTORY відсутні — гейт пропущено')\n",
"        warn('файли правил або HISTORY відсутні — гейт пропущено')\n"))

E.append((V,
"    RULE_FILES = ('Work_Standard.md', 'Lens_governance_protocol.md')\n"
"    seen_rule_file = False\n"
"    for f in sorted(live):\n"
"        if not f.endswith(RULE_FILES):\n",
"    seen_rule_file = False\n"
"    for f in sorted(live):\n"
"        if not f.endswith(tuple(RULE_FILES)):\n"))

E.append((V,
"             '(дзеркало неповне?), це НЕ зелений результат')\n"
"\n"
"    g19(root)\n",
"             '(дзеркало неповне?), це НЕ зелений результат')\n"
"\n"
"    g21(root)\n"
"    g19(root)\n"))

E.append((V,
"# ─────────────────────────── G19 · СПРАЦЮВАННЯ ПРАВИЛ ───────────────────────\n",
"# ─────────────────────────── G21 · ОДИН ДІМ НОМЕРА ──────────────────────────\n"
"def g21(root):\n"
"    \"\"\"Номер правила з тілом — рівно в одному файлі RULE_FILES (IDX-7, G-J).\n"
"    Маршрут (ROUTING або <400 B) — не тіло: на старому місці він законний.\"\"\"\n"
"    print('\\n[G21] номер правила — один дім (розпил wsd, IDX-7)')\n"
"    homes, nfiles = {}, 0\n"
"    for f, kind in RULE_FILES.items():\n"
"        try:\n"
"            body = open(R(root, f), encoding='utf-8').read()\n"
"        except OSError:\n"
"            continue\n"
"        nfiles += 1\n"
"        for part in re.split(r'\\n(?=##+\\s+`?\\d+\\.\\d+)', body):\n"
"            m = re.match(r'##+\\s+`?(\\d+\\.\\d+(?:-[а-яґєіїь])?)`?[\\s|]', part)\n"
"            if not m or 'ROUTING' in part or len(part.encode('utf-8')) < 400:\n"
"                continue\n"
"            homes.setdefault(m.group(1), []).append(kind)\n"
"    if not nfiles:\n"
"        warn('жодного файлу правил не знайдено — G21 не виконався, це НЕ зелений результат')\n"
"        return\n"
"    dups = sorted((k, v) for k, v in homes.items() if len(v) > 1)\n"
"    if dups:\n"
"        fail('номер з тілом у кількох файлах: ' +\n"
"             ' '.join(f'{k}({\"+\".join(v)})' for k, v in dups))\n"
"    else:\n"
"        ok(f'{len(homes)} номерів з тілом у {nfiles} файлах — кожен рівно в одному')\n"
"\n"
"\n"
"# ─────────────────────────── G19 · СПРАЦЮВАННЯ ПРАВИЛ ───────────────────────\n"))

E.append((V,
"    R_ = _rule_ids(R(root, 'Work_Standard.md'), 'wsd') + \\\n"
"         _rule_ids(R(root, 'Lens_governance_protocol.md'), 'gov')\n",
"    R_ = [x for f, kind in RULE_FILES.items() for x in _rule_ids(R(root, f), kind)]\n"))

E.append((I,
"Написані: `G1`–`G13`, `G16`, `G19` (спрацювання правил, К4-1).",
"Написані: `G1`–`G13`, `G16`, `G19` (спрацювання правил, К4-1), `G21` (номер правила —\n"
"один дім, `IDX-7`, G-J). Файли правил — константа `RULE_FILES` у `Lens_validate.py`;\n"
"новий дім правил = рядок там + рядок тут (`G4` `G16` `G19` `G21` читають її)."))

E.append((I,
"Перший вільний номер — **`G21`**.",
"Перший вільний номер — **`G22`**."))

# ── СТОПИ ────────────────────────────────────────────────────────────────────
txt = {p: open(p, encoding='utf-8').read() for p in (V, I)}
# точна класифікація: новий стан = кожне «нове» присутнє
new_all = all(txt[p].count(b) == 1 for p, a, b in E)
old_all = all(txt[p].count(a) == 1 and txt[p].count(b) == 0 for p, a, b in E)
if new_all:
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if not old_all:
    die('змішаний стан: ' + ' '.join(f'{txt[p].count(a)}/{txt[p].count(b)}' for p, a, b in E))

# ── ЗАПИС ────────────────────────────────────────────────────────────────────
for p, a, b in E:
    txt[p] = txt[p].replace(a, b)
for p in txt:
    open(p, 'w', encoding='utf-8').write(txt[p])
print(f'✓ {len(E)} правок · Lens_validate.py {len(txt[V].encode())} B · Lens_INDEX.md {len(txt[I].encode())} B')
