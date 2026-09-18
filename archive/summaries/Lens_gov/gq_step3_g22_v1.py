#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-Q крок 3 — §0 п.2 самері G-P: гейт G22 (К2 правила wsd 1.3) у Lens_validate.py.
   живе доки: хід 3 сесії G-Q не влитий у репо.
   G22 (варіант Б, рішення Konst у G-Q): кожне *_session_summary_*.md у теках --live, якого немає
   в archive/summaries/**, має заголовок h2+ зі словами «стартове повідомлення» (без регістру),
   і в межах цього розділу (до наступного h1/h2) — fenced code block (``` або ~~~). Інакше ✗.
   Без --live — не виконується, ⓘ (як G19): підсумок базового прогону без змін.
   12.16: якорі repr, count == 1; усі стопи вище запису. Ф-20: позиційний revert == old.
   П34/П37: повтор на застосованому стані → exit 0, жодного запису, той самий md5."""
import sys, os
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx3'
P = os.path.join(STG, 'kernel/Lens_validate.py')
def die(m): print('✗ СТОП:', m); sys.exit(1)

HELP_A = "         лише цитати, одна з них `> **ROUTING →`. Заглушка ≥ 400 B → ⚠ «виключено як маршрут»\n"
HELP_N = HELP_A + ("      G22 (з --live) живе самері (у теці --live, не в archive/summaries/) без code block у розділі\n"
                   "         «стартове повідомлення» → ✗ (wsd 1.3 К2; G-J віддало §6 blockquote-ом — не копіюється)\n")
CALL_A = "    g19(root)\n"
CALL_N = "    g19(root)\n    g22(root)\n"
SEC_A = "# ────────────────────────────────── HTML ──────────────────────────────────\n"
SEC_N = '''# ─────────────────────────── G22 · СТАРТОВЕ ПОВІДОМЛЕННЯ У CODE BLOCK ──────────
def g22(root):
    """wsd 1.3 К2 (G-K §2): §6 самері — готовий до копіювання текст, тобто fenced code block.
    Перевіряє живі самері: *_session_summary_*.md у теках --live, яких немає в archive/summaries/**
    (варіант Б, G-Q: ловить і свіже самері в outputs до видачі, ще не оголошене в §5)."""
    print('\\n[G22] стартове повідомлення самері — у code block (wsd 1.3)')
    if not LIVE_DIRS:
        print('  ⓘ --live не дано — G22 не виконувався (живі самері лежать у Project, не в репо)')
        return
    arc = set()
    for _, _, fns in os.walk(os.path.join(root, 'archive', 'summaries')):
        arc |= set(fns)
    seen, bad = 0, []
    for d in LIVE_DIRS:
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            if not (n.endswith('.md') and '_session_summary_' in n) or n in arc:
                continue
            seen += 1
            lines = open(os.path.join(d, n), encoding='utf-8').read().splitlines()
            hs = [i for i, l in enumerate(lines)
                  if re.match(r'#{2,}\\s', l) and 'стартове повідомлення' in l.casefold()]
            if not hs:
                bad.append(f'{n} (немає заголовка «стартове повідомлення»)')
                continue
            sec = []
            for l in lines[hs[-1] + 1:]:
                if re.match(r'#{1,2}\\s', l):
                    break
                sec.append(l)
            if not any(re.match(r'\\s*(```|~~~)', l) for l in sec):
                bad.append(f'{n} (немає code block — blockquote/текст не копіюється)')
    if not seen:
        warn('живих самері в --live не знайдено — G22 не виконався, це НЕ зелений результат')
    elif bad:
        for b in bad:
            fail(f'G22 {b}')
    else:
        ok(f'усі {seen} живих самері мають стартове повідомлення в code block')


''' + SEC_A
EDITS = [(HELP_A, HELP_N), (CALL_A, CALL_N), (SEC_A, SEC_N)]

src = open(P, encoding='utf-8').read()
if src.count('def g22') == 1 and all(src.count(n) == 1 for _, n in EDITS):
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
if src.count('def g22') or not all(src.count(a) == 1 for a, _ in EDITS):
    die('стан змішаний: ' + ' '.join(f'{i}:{src.count(a)}/{src.count(n)}' for i, (a, n) in enumerate(EDITS)))
if 'def is_route' not in src: die('Ф-25 (5ad5f71) не застосовано — база не та')
new = src
for a, n in EDITS: new = new.replace(a, n, 1)
back = new
for a, n in reversed(EDITS):
    i = back.index(n); back = back[:i] + a + back[i + len(n):]
if back != src: die('позиційний revert ≠ старий файл')
open(P, 'w', encoding='utf-8').write(new)
print(f'✓ Lens_validate.py {len(src.encode()):6d} → {len(new.encode()):6d} B · 3 правки · revert == old')
