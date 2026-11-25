#!/usr/bin/env python3
# живе доки: черги репо мають стелю `doc_health` M2 (читаються цілком на старті; число — звідти, `M2_KB`).
# ROT — прополка закритого машиною, без питання (Konst 25.11.2026, EquipLens S45: «навіщо питати, коли це по замовчуванню логічно?… підсиль»).
# Що робить з чергою (`lens/*_CHERGA.md` · `kernel/*_CHERGA.md` · `docs/CHERGA.md`):
#   (а) МЕХАНІЧНО, без питання: рядок таблиці зі станом ✅ / «закрито» — геть (правило обох черг: «закритий пункт — геть, історія — самері й git»);
#       у таблиці-карті маршруту (стовпець «стан» і «далі») лишається один найновіший ✅ — «звідки прийшли». Ідентифікатори прибраного — у вивід
#       (агент кладе їх у повідомлення коміту → `git log --grep <id>`). Нема що прибрати — файл не чіпає (як `tada archive`).
#   (б) НА СТЕЛІ (файл ≥ 90 % стелі M2): ⚠ і п'ять найдовших відкритих рядків з позначкою, чи є свій бриф `<id>_brief.md` →
#       агент стискає рядок до «стан + вказівник на бриф» тим самим ходом, теж без питання (правило — ця шапка; рядок у CLAUDE_CODE.md «Що тут лежить»).
#       Мірило Adobe ai-repo-harness-guide гл.04 (25.11.2026): файл судять, коли він і завеликий, і не виводить назовні; у нас — довгий рядок без брифу.
# Світ (25.11.2026): Obsidian task-archiver (виконане — з розділом), tada (todo.txt → done.txt, нічого не пише, коли нема що); власний зразок — journal_rotate.py.
# Не беремо: запуск за розкладом — ми працюємо сесіями, тригер — закриття й розмір. На старті — лише `--dry` (env_check); пише файл агент у ході коміту.
#   python3 doc_prune.py <репо> [--dry] [--inject]   → рядок на чергу: «прополка <шлях>: прибрано N (`id`…) · X → Y Б (Z % стелі)» (або «закритих нема»)
#     + ⚠ на стелі; exit 0 (--inject: 1, якщо підкинутий закритий не прибрано)
#   python3 doc_prune.py selftest
import sys, os, re, glob, tempfile, shutil, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doc_health import M2_KB   # аудит sonnet 25.11 №7: одна стеля, один дім

CAP, NEAR = M2_KB * 1024, 0.90
CLOSED = re.compile(r'✅|(?<!не )(?<!ще не )\bзакрито\b', re.I)   # аудит sonnet 25.11 №4: «не закрито» — відкрите, не чіпати
DATE = re.compile(r'(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?')


def queues(repo):
    return sorted(set(glob.glob(os.path.join(repo, 'lens', '*_CHERGA.md')) + glob.glob(os.path.join(repo, 'kernel', '*_CHERGA.md')) +
                      glob.glob(os.path.join(repo, 'docs', 'CHERGA.md'))))


def cells(l):
    return [c.strip() for c in l.strip().strip('|').split('|')]


def prune_text(t):
    """→ (новий текст, прибрані id, найдовші відкриті [(байт, id)])."""
    ls = t.split('\n'); drop, hdr, longest = set(), None, []
    k = 0
    while k < len(ls):
        l = ls[k]
        if l.startswith('|') and k + 1 < len(ls) and re.match(r'^\|[\s:|-]+\|$', ls[k + 1].strip()):
            hdr = [c.lower() for c in cells(l)]; st = next((i for i, c in enumerate(hdr) if c == 'стан'), None)
            is_map = st is not None and 'далі' in hdr; done = []
            k += 2
            while k < len(ls) and ls[k].startswith('|'):
                c = cells(ls[k]); m = re.match(r'^\*{0,2}`([^`]+)`', c[0]) if c else None
                if m:
                    state = c[st] if st is not None and st < len(c) else ''
                    if st is not None and CLOSED.search(state): done.append((k, m.group(1), state))
                    elif st is None and CLOSED.search(c[-1]) and len(c[-1]) < 40: done.append((k, m.group(1), c[-1]))
                    else:
                        h = re.search(r'бриф не треба[^`|]*`([^`]+\.md)`', ls[k], re.I)   # «Бриф не треба: стан — `файл`» — свій дім теж дім
                        longest.append((len(ls[k].encode()), m.group(1) + (f'|{h.group(1)}' if h else '')))
                k += 1
            if is_map and done:   # карта: найновіший ✅ лишається
                def key(x):   # аудит №5: дата без року — цього року, не «найстаріша»
                    d = DATE.search(x[2]); return (int(d.group(3) or datetime.date.today().year), int(d.group(2)), int(d.group(1))) if d else (0, 0, 0)
                done.remove(max(done, key=key))
            drop |= {(i, idv) for i, idv, _ in done}
            continue
        k += 1
    out = '\n'.join(l for i, l in enumerate(ls) if i not in {d[0] for d in drop})
    return out, [d[1] for d in sorted(drop)], sorted(longest, reverse=True)[:5]


def run(repo, dry=False, inject=False):
    lines, code = [], 0
    for q in queues(repo):
        t = open(q, encoding='utf-8').read(); rel = os.path.relpath(q, repo)
        if inject:   # зуб: підкинутий закритий рядок у копії має бути прибраний
            t = re.sub(r'\n(\|[^\n]*)\n(\|[\s:|-]+\|)\n', lambda m: f'\n{m.group(1)}\n{m.group(2)}\n| `ZZ-INJ` |' + ' ✅ 01.01.2026 |' * (len(cells(m.group(1))) - 1) + '\n', t, count=1)
        out, gone, top = prune_text(t)
        if inject:
            ok = 'ZZ-INJ' in gone; lines.append(f'{"ЗЛОВИВ" if ok else "✗ НЕ ЗЛОВИВ"} prune --inject: {rel}'); code |= not ok; continue
        was, now = len(t.encode()), len(out.encode())
        if gone and not dry: open(q, 'w', encoding='utf-8').write(out)
        msg = f'прополка {rel}: ' + (f'прибрано {len(gone)} ({" ".join(f"`{g}`" for g in gone)})' if gone else 'закритих нема') + \
              f' · {was} → {now} Б ({now * 100 // CAP} % стелі){" · --dry" if dry and gone else ""}'
        lines.append(msg)
        if now >= CAP * NEAR:
            briefs = {re.sub(r'^Lens_', '', os.path.basename(p).split('_brief')[0]) for p in glob.glob(os.path.join(repo, '**', '*_brief.md'), recursive=True) if '/archive/' not in p}   # аудит №3: точний збіг id (ядро — Lens_<id>)
            lines.append(f'⚠ {rel} на стелі ({now} / {CAP} Б) — стисни найдовші відкриті до «стан + вказівник» без питання: ' +
                         ' · '.join(f'`{i.split("|")[0]}` {b} Б (' + (f'дім: `{i.split("|")[1]}`' if '|' in i else 'бриф є' if i in briefs else 'брифу нема — створи або стисни') + ')' for b, i in top))
    if not lines: lines.append('прополка: черг (*_CHERGA.md) не знайдено')
    return '\n'.join(lines), code


def selftest():
    bad, cases = 0, []; tmp = tempfile.mkdtemp(prefix='prune_')
    try:
        os.makedirs(os.path.join(tmp, 'lens'))
        q = ('# Ч\n\n## Відкрите\n\n| id | що | стан |\n|---|---|---|\n| `A-1` | відкрите | ○ |\n| `B-1` | зроблене | ✅ 20.11.2026 |\n'
             '| `C-1` | теж | закрито 21.11 |\n| `N-1` | ще ні | не закрито |\n| `D-1` | довге; Бриф не треба: стан — `lens/D.md` | ○ |\n\nкарта:\n\n| крок | що | готово, коли | далі | стан |\n|---|---|---|---|---|\n'
             '| `S1` | старе | x | `S2` | ✅ 20.11 |\n| `S2` | новіше | x | `S3` | ✅ 22.11 |\n| `S3` | зараз | x | `S4` | ▶ |\n')
        p = os.path.join(tmp, 'lens', 'X_CHERGA.md'); open(p, 'w').write(q)
        m, _ = run(tmp, dry=True); same = open(p).read() == q
        m2, _ = run(tmp); live = open(p).read()
        cases = [('--dry не пише файл', same and 'прибрано 3' in m),
                 ('закриті ✅ і «закрито» — геть', '`B-1`' not in live and '`C-1`' not in live),
                 ('відкрите лишилось', '`A-1`' in live and '`S3`' in live),
                 ('«не закрито» — відкрите, лишилось (аудит №4)', '`N-1`' in live),
                 ('карта: найновіший ✅ лишився, старіший — геть', '`S2`' in live and '`S1`' not in live),
                 ('id прибраного — у виводі (для коміту)', '`B-1`' in m2 and '`S1`' in m2)]
        m3, _ = run(tmp); cases.append(('повтор — нема що, файл не чіпає', 'закритих нема' in m3 and open(p).read() == live))
        open(p, 'w').write(live.replace('| `A-1` | відкрите | ○ |', '| `A-1` | відкрите | ○ |\n| `L-1` | ' + 'д' * 12000 + ' | ○ |'))
        m4, _ = run(tmp); cases.append(('на стелі — ⚠ з найдовшим рядком', '⚠' in m4 and '`L-1`' in m4))
        cases.append(('«бриф не треба: стан — `файл`» — дім названо, не «брифу нема»', 'дім: `lens/D.md`' in m4))
        open(os.path.join(tmp, 'lens', 'L-1_brief.md'), 'w').write('б'); open(os.path.join(tmp, 'lens', 'XL-10_brief.md'), 'w').write('б')
        m6, _ = run(tmp); cases.append(('бриф — точний збіг id: `L-1_brief.md` → «бриф є» (аудит №3)', '`L-1`' in m6 and 'бриф є' in m6))
        t6 = open(p).read(); open(p, 'w').write(t6.replace('`L-1`', '`L-2`')); os.remove(os.path.join(tmp, 'lens', 'L-1_brief.md'))
        m7, _ = run(tmp); cases.append(('`L-2` при `XL-10_brief.md` — не «бриф є» (підрядок не рахується)', '`L-2`' in m7 and 'бриф є' not in m7))
        k = prune_text('| крок | що | далі | стан |\n|---|---|---|---|\n| `S1` | а | `S2` | ✅ 20.11.' + str(datetime.date.today().year - 1) + ' |\n| `S2` | б | `S3` | ✅ 22.11 |\n')
        cases.append(('карта: «22.11» без року новіше за «20.11.<торік>» (аудит №5)', k[1] == ['S1']))
        m5, c5 = run(tmp, inject=True); cases.append(('--inject: підкинутий закритий → ЗЛОВИВ', 'ЗЛОВИВ' in m5 and c5 == 0))
        for n, ok in cases: bad += not ok; print(f'{"✓" if ok else "✗"} {n}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'─── doc_prune selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print('doc_prune.py <репо> [--dry] [--inject] | selftest'); sys.exit(2)
    if a[0] == 'selftest': sys.exit(selftest())
    m, c = run(os.path.abspath(a[0]), dry='--dry' in a, inject='--inject' in a); print(m); sys.exit(c)
