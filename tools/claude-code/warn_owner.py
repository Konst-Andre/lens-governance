#!/usr/bin/env python3
# живе доки: env_check продуктів і ядра кладуть ⚠ у старт сесії (WARN-1, `kernel/Lens_WARN-1_brief.md`).
# Власник кожного ⚠ старту (WARN-1, EquipLens S41, 22.11.2026; Konst: «попередження на старті… не можна ігнорувати», 💡 «⚠ з власником» —
#   «так з підсиленням»). Фільтр виводу env_check: кожне ⚠ шукає рядок у реєстрі `tools/claude-code/WARN_OWNERS.md`:
#   · власник — пункт черги (`ID` відкритий у черзі репо чи ядра) · рішення Konst · ⓘ «чому не треба» — з датою «до» (≤ 30 дн.);
#   · знайдено → «⚠ … → `ID` (до 06.12)»; ⓘ → рядок стає ⓘ (не шум щостарту);
#   · нема власника / власник прострочив / `ID` не в черзі → ✗ (exit 1): ⚠ без дії не висить (була причина 2 пропуску «самері 132 КБ»).
# Практика: кожен алерт — з власником і ранбуком; тиша — з причиною, власником і автоматичним строком (rootly.com «Alert management best
#   practices»; AWS Well-Architected OPS10-BP02 «Have a process per alert» — 22.11.2026). Беремо: власник + строк. Не беремо: ескалацію людині
#   (чергових нема — ескалує сам рядок ✗ на старті й ревізія handoff_check (16)).
#   python3 warn_owner.py filter <репо> [--repo <тека>] [--kernel <тека>] [--inject]  < вивід env_check  → той самий вивід з власниками + підсумок
#   python3 warn_owner.py selftest
import sys, os, re, datetime, tempfile, shutil

REG = 'tools/claude-code/WARN_OWNERS.md'
OWN_DAYS = 30
CLOCK = re.compile(r'збірка йде|самері відстає|треба pull|ЗЛОВИВ|--inject')   # свій годинник: ліки — цієї години, власник не потрібен
COUNT = re.compile(r'⚠:?\s*\d+(\s|$|·|─)')   # лічильник підсумку («⚠ 1 · ✗ 0») — не предмет: текст ⚠ env_check кладе окремим рядком «⚠ <прилад>: …»
D = r'(\d{2})\.(\d{2})\.(\d{4})'


def _date(s):
    m = re.search(D, s or ''); return datetime.date(int(m[3]), int(m[2]), int(m[1])) if m else None


def registry(kernel, repo):
    p = os.path.join(kernel, REG); rows = []
    if not os.path.isfile(p): return rows
    for l in open(p, encoding='utf-8'):
        c = [x.strip().replace('\\|', '|') for x in re.split(r'(?<!\\)\|', l.strip().strip('|'))] if l.startswith('|') else []   # GFM: «\|» у клітинці — знак, не межа
        if len(c) < 5 or not c[1].startswith('`'): continue
        if c[0].strip('`') not in ('*', repo): continue
        try: rx = re.compile(c[1].strip('`'))
        except re.error: continue
        rows.append(dict(rx=rx, key=c[1], owner=c[2], since=_date(c[3]), until=_date(c[4])))
    return rows


def open_ids(kernel, repo_root):
    sys.path.insert(0, os.path.join(kernel, 'kernel'))
    try: from Lens_validate import queue_open
    except Exception: return None
    ids = set()
    for d, pat in ((kernel, 'kernel/Lens_governance_CHERGA.md'), (repo_root, None)):
        fs = [os.path.join(d, pat)] if pat else [os.path.join(dp, f) for sub in ('lens', 'docs', 'kernel') for dp, _, fl in os.walk(os.path.join(d, sub)) for f in fl if 'CHERGA' in f and f.endswith('.md') and '/archive' not in dp]
        for f in fs:
            if os.path.isfile(f): ids |= {i for i, _ in queue_open(open(f, encoding='utf-8').read())}
    return ids


def judge(text, rows, ids, today):
    """→ (стан, примітка): ok · info · bad."""
    hit = next((r for r in rows if r['rx'].search(text)), None)
    if not hit: return 'bad', f'без власника — рядок у `{REG}`: власник (`ID` черги · Konst · ⓘ чому не треба) і «до» ≤ {OWN_DAYS} дн.'
    u, s = hit['until'], hit['since']
    if not u or not s: return 'bad', f'рядок реєстру {hit["key"]} без дат «з» / «до»'
    if (u - s).days > OWN_DAYS: return 'bad', f'рядок реєстру {hit["key"]}: строк {(u - s).days} дн. > {OWN_DAYS} — тиша без кінця'
    if today > u: return 'bad', f'власник прострочив (до {u:%d.%m}) — переглянь рядок {hit["key"]} у `{REG}`'
    o = hit['owner']; m = re.match(r'\*{0,2}`([^`]+)`', o)
    if m and ids is not None and m[1] not in ids: return 'bad', f'власник `{m[1]}` — у черзі відкритого пункту нема (закрито? → прибери рядок реєстру)'
    if o.startswith('ⓘ'): return 'info', f'{o[1:].strip()} (до {u:%d.%m})'
    short = f'`{m[1]}`' if m else o.split('(')[0].strip()[:60]
    return 'ok', f'{short} (до {u:%d.%m})'


def items(line):
    """⚠ у рядку: рядок, що починається з ⚠, — один предмет; інакше — кожен сегмент « · », що починається з ⚠."""
    s = line.strip()
    if s.startswith('⚠'): return [s]
    return [g.strip() for g in s.split(' · ') if g.strip().startswith('⚠') and not COUNT.match(g.strip())]


def filt(text, repo, repo_root, kernel, today=None, inject=False):
    today = today or datetime.date.today(); rows = registry(kernel, repo); ids = open_ids(kernel, repo_root)
    lines = text.rstrip('\n').split('\n') if text.strip() else []
    if inject: lines.append('⚠ підкинуте WARN-1: попередження без власника')
    out, n, ok, info, bad, seen = [], 0, 0, 0, [], set()
    for l in lines:
        new = l
        for it in items(l):
            if CLOCK.search(it): continue
            st, note = judge(it, rows, ids, today)
            if it not in seen: n += 1; seen.add(it); ok += st == 'ok'; info += st == 'info'
            if st == 'ok': new = new.replace(it, f'{it} → {note}', 1)
            elif st == 'info': new = new.replace(it, 'ⓘ' + it[1:] + f' — прийнято: {note}', 1)
            elif it not in [b[0] for b in bad]: bad.append((it, note))
        out.append(new)
    for it, note in bad: out.append(f'✗ {it[:160]} — {note}')
    s = f'власники ⚠: на старті {n} · з власником {ok} · ⓘ {info} · без дії {len(bad)}'
    if inject: s += ' · --inject ' + ('ЗЛОВИВ' if any('підкинуте WARN-1' in b[0] for b in bad) else '✗ НЕ ЗЛОВИВ')
    out.append(('✗ ' if bad and not inject else '') + s)
    return '\n'.join(out), (1 if bad and not inject else 0)


def selftest():
    tmp = tempfile.mkdtemp(prefix='wo_'); bad = 0; T = datetime.date(2026, 11, 22)
    try:
        os.makedirs(os.path.join(tmp, 'k/tools/claude-code')); os.makedirs(os.path.join(tmp, 'k/kernel')); os.makedirs(os.path.join(tmp, 'r/lens'))
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../kernel/Lens_validate.py'), os.path.join(tmp, 'k/kernel/'))
        open(os.path.join(tmp, 'k/kernel/Lens_governance_CHERGA.md'), 'w').write('## Відкрите\n| id | що | дата | умова |\n|---|---|---|---|\n| `CF-CPU` | x | 18.11.2026 | y |\n')
        open(os.path.join(tmp, 'r/lens/R_CHERGA.md'), 'w').write('## Відкрите\n| id | що | дата | умова |\n|---|---|---|---|\n| `Q-1` | x | 20.11.2026 | y |\n')
        open(os.path.join(tmp, 'k', REG), 'w').write('| репо | ключ | власник | з | до |\n|---|---|---|---|---|\n'
            '| * | `CPU (airlens\\|7 дн)` | `CF-CPU` — лікування в сесії AirLens | 18.11.2026 | 10.12.2026 |\n'
            '| R | `борг аудиту` | Konst: «не запускати» (21.11) | 21.11.2026 | 10.12.2026 |\n'
            '| R | `A69 dark` | ⓘ стенд заморожений | 22.11.2026 | 20.12.2026 |\n'
            '| R | `старе` | `Q-1` | 01.10.2026 | 20.10.2026 |\n'
            '| R | `зник` | `Q-9` | 20.11.2026 | 10.12.2026 |\n'
            '| R | `довге` | ⓘ назавжди | 01.11.2026 | 30.12.2026 |\n'
            '| X | `чуже` | ⓘ інше репо | 20.11.2026 | 10.12.2026 |\n')
        k, r = os.path.join(tmp, 'k'), os.path.join(tmp, 'r')
        def run(t, inject=False): return filt(t, 'R', r, k, T, inject)
        cases = []
        o, c = run('⚠ ТРИВОГА cloudflare: CPU airlens p50 17.9'); cases.append(('власник `ID` відкритий у черзі ядра → «→ `CF-CPU` (до 10.12)», exit 0', '→ `CF-CPU` (до 10.12)' in o and c == 0))
        o, c = run('env: github=200 · гейт: ✓ 4 · ⚠ борг аудиту: 4 коміт(ів)'); cases.append(('⚠ усередині рядка (сегмент « · ») → власник Konst', '⚠ борг аудиту: 4 коміт(ів) → Konst: «не запускати»' in o and c == 0))
        o, c = run('⚠ стенд: [H3] A69 dark-твін'); cases.append(('ⓘ у реєстрі → рядок стає ⓘ, не ⚠; лічильник ⓘ 1', o.startswith('ⓘ стенд') and 'ⓘ 1' in o and c == 0))
        o, c = run('⚠ щось нове'); cases.append(('без власника → ✗ і exit 1', '✗ ⚠ щось нове — без власника' in o and c == 1))
        o, c = run('⚠ старе попередження'); cases.append(('власник прострочив → ✗', 'прострочив' in o and c == 1))
        o, c = run('⚠ зник пункт'); cases.append(('`ID` нема в черзі → ✗', '`Q-9` — у черзі' in o and c == 1))
        o, c = run('⚠ довге мовчання'); cases.append(('строк > 30 дн. → ✗ «тиша без кінця»', 'тиша без кінця' in o and c == 1))
        o, c = run('⚠ чуже попередження'); cases.append(('рядок чужого репо не діє → ✗ без власника', 'без власника' in o and c == 1))
        o, c = run('⚠ прод: збірка йде, перев за 10 хв'); cases.append(('свій годинник («збірка йде») — не судиться', '✗' not in o and c == 0))
        o, c = run('env: гейт: ─── ПІДСУМОК: ✓ 4 · ⚠ 1 · ✗ 0 ───'); cases.append(('лічильник «⚠ 1» підсумку — не предмет (текст — окремим рядком env_check)', '✗' not in o.replace('✗ 0', '') and c == 0))
        o, c = run('⚠ ТРИВОГА: CPU airlens\nрядок · ⚠ CPU airlens 7 дн.'); cases.append(('підсумок: на старті 2 · з власником 2 · без дії 0', 'на старті 2 · з власником 2 · ⓘ 0 · без дії 0' in o))
        o, c = run('усе гаразд', inject=True); cases.append(('--inject: підкинуте ⚠ без власника → ЗЛОВИВ', 'ЗЛОВИВ' in o and 'НЕ ЗЛОВИВ' not in o))
        for nm, okk in cases: bad += not okk; print(f'{"✓" if okk else "✗"} {nm}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'─── warn_owner selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']: sys.exit(selftest())
    if a[:1] == ['filter'] and len(a) > 1:
        def opt(n, d):
            return a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else d
        here = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        o, c = filt(sys.stdin.read(), a[1], os.path.abspath(opt('--repo', '.')), os.path.abspath(opt('--kernel', here)), inject='--inject' in a)
        print(o); sys.exit(c)
    print('warn_owner.py filter <репо> [--repo <тека>] [--kernel <тека>] [--inject] < вивід env_check | selftest'); sys.exit(2)
