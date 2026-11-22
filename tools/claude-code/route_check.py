#!/usr/bin/env python3
# живе доки: продукти Lens ведуть маршрут картою кроків у черзі (`ROUTE-1`, kernel/Lens_ROUTE-1_brief.md §5 крок 1 · §5-б).
# Прилад маршруту — ЄДИНИЙ, хто читає карту («… · карта кроків» у черзі продукту); гачки, ревізія, іспит, сторінка беруть його вивід (§5-б).
# Практика: робочий файл кроків, який агент читає й оновлює (Anthropic «Effective harnesses for long-running agents», 2025) + реєстр змін
#   обсягу «хто · коли · чому» (Atlassian «Scope creep», пошук 22.11.2026) — бриф §5. Розбір таблиці — за GFM: нерозекранований `|` ріже
#   клітинку й усередині бектиків, `\|` — ні (GFM spec «Tables (extension)»; rumdl table_utils — «для GFM pipes in inline code ARE delimiters»,
#   пошук 22.11.2026) → зайва клітинка — ✗: на GitHub ця таблиця теж зламана.
#   python3 route_check.py check <репо> [--queue F] [--inject two|next|summary]   → звіт, exit 1 на ✗
#   python3 route_check.py line  <репо> [--queue F]                                  → один рядок для звіту / гачка
#   python3 route_check.py selftest                                                  → зуби: тимчасові репо
# Карти нема → «маршрут: карти нема», exit 0 (старі репо — без змін).
# ✗: крок ▶ не рівно один · стан не з ▶ ○ ⏸ ✅ · клітинок ≠ заголовку · крок без «що» / «готово, коли» / «далі» (у ▶ і його «далі» «—» теж ✗;
#    далі за ланцюгом «—» = ще не визначено, норма) · «далі» на неіснуючий id · дубль id.
# ⚠: самері §0 п.1 чи рядок «ЗАРАЗ:» стартового не називає id ▶ · черга «**Зараз**» не називає ▶ і не веде на карту · «Далі» §0 брифу без живого id
#    · ✅ без дати · крок ○ / ⏸, до якого ланцюг «далі» від ▶ не доходить · рядок «Вхідні» без «→».
# ⓘ: дрейф — коміти сесії з id кроку в бектиках ⟂ усі коміти сесії (лише рахунок).
import sys, os, re, glob, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import handoff_check as hc
except Exception:   # прилад живе й без сусіда: без самері й дрейфу
    hc = None

STATES = ('▶', '○', '⏸', '✅')
DATE = re.compile(r'\d{1,2}\.\d{1,2}')
EMPTY = {'', '—', '-', '–'}


def cells(row):
    """Клітинки рядка таблиці за GFM: межа — кожен `|`, крім `\\|` (і в бектиках теж)."""
    s = row.strip()
    if s.startswith('|'): s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'): s = s[:-1]
    return [c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', s)]


def ids(text): return re.findall(r'`([^`\s]+)`', text or '')


def has_id(text, rid): return bool(re.search(rf'(?<![\w-]){re.escape(rid)}(?![\w-])', text or ''))


def find_queue(repo):
    xs = [p for p in glob.glob(os.path.join(repo, '**', '*CHERGA*.md'), recursive=True)
          if not re.search(r'/(archive|templates)/', p.replace(os.sep, '/'))]
    return sorted(xs, key=lambda p: (p.count(os.sep), p))[0] if xs else None


def parse_map(text):
    """→ dict(rows, inbox, width_bad) або None (карти нема). Карта — заголовок з «карта кроків» до наступного заголовка того ж чи вищого рівня."""
    ls = text.splitlines()
    start = next((i for i, l in enumerate(ls) if re.match(r'\s*#{1,6}\s', l) and re.search(r'карта кроків', l, re.I)), None)
    if start is None: return None
    lvl = len(re.match(r'\s*(#+)', ls[start]).group(1))
    end = next((j for j in range(start + 1, len(ls)) if re.match(rf'\s*#{{1,{lvl}}}\s', ls[j])), len(ls))
    rows, hdr, width_bad, inbox, in_inbox = [], None, [], [], False
    for n, l in enumerate(ls[start + 1:end], start + 2):
        if l.strip().startswith('|'):
            c = cells(l)
            if hdr is None:
                if any(re.search(r'крок', x, re.I) for x in c): hdr = [x.lower() for x in c]
                continue
            if all(re.fullmatch(r':?-{2,}:?', x) for x in c if x): continue
            if len(c) != len(hdr): width_bad.append(f'рядок {n}: клітинок {len(c)} ≠ {len(hdr)} заголовка (нерозекранований `|`? → `\\|`)')
            col = lambda key: next((c[k] for k, h in enumerate(hdr) if key in h and k < len(c)), '')
            rid = ids(col('крок'))
            rows.append(dict(id=rid[0] if rid else col('крок'), what=col('що'), done=col('готово'), next=col('далі'), state=col('стан')))
            continue
        if re.match(r'\s*\*\*Вхідні', l): in_inbox = True; continue
        if in_inbox:
            if re.match(r'\s*[-*]\s+\S', l): inbox.append(l.strip())
            elif l.strip(): in_inbox = False
    inbox = [x for x in inbox if not re.fullmatch(r'[-*]\s+—\s*', x)]
    return dict(rows=rows, inbox=inbox, width_bad=width_bad)


def state_of(r): return next((x for x in STATES if r['state'].strip().startswith(x)), None)


def reach(rows, frm):
    by = {r['id']: r for r in rows}; seen, todo = set(), [frm]
    while todo:
        k = todo.pop()
        if k in seen or k not in by: continue
        seen.add(k); todo += ids(by[k]['next'])
    return seen


def section0(text):
    """Тіло розділу «## …§0…» (самері, бриф)."""
    out, on = [], False
    for l in text.splitlines():
        if l.startswith('## '):
            if on: break
            on = '§0' in l; continue
        if on: out.append(l)
    return '\n'.join(out)


def check(repo, queue=None, inject=None):
    """→ dict(bad, warn, info, play, nxt, inbox_open, qrel) або None (карти нема)."""
    qp = queue or find_queue(repo)
    if qp and not os.path.isabs(qp): qp = os.path.join(repo, qp)
    if not qp or not os.path.isfile(qp): return None
    text = open(qp, encoding='utf-8').read(); m = parse_map(text)
    if m is None: return None
    rows, qrel = m['rows'], os.path.relpath(qp, repo)
    if inject == 'two':   # зуб: другий ▶
        for r in rows:
            if state_of(r) != '▶': r['state'] = '▶'; break
    if inject == 'next' and rows: rows[0]['next'] = '`NOPE-404`'   # зуб: «далі» на неіснуючий крок
    bad, warn, info = list(m['width_bad']), [], []
    if not rows: bad.append(f'{qrel}: карта без рядків')
    seen = {}
    for r in rows:
        if r['id'] in seen: bad.append(f'дубль id `{r["id"]}`')
        seen[r['id']] = r
    plays = [r['id'] for r in rows if state_of(r) == '▶']
    if len(plays) != 1: bad.append(f'крок ▶ — {len(plays)}, має бути рівно один' + (f' ({", ".join(plays)})' if plays else ''))
    play = plays[0] if len(plays) == 1 else None
    near = ({play} | set(ids(seen[play]['next']))) if play else set()
    for r in rows:
        st = state_of(r)
        if st is None: bad.append(f'`{r["id"]}`: стан «{r["state"]}» — не з {" ".join(STATES)}')
        if st == '✅' and not DATE.search(r['state']): warn.append(f'`{r["id"]}`: ✅ без дати')
        if r['what'] in EMPTY: bad.append(f'`{r["id"]}`: без «що»')
        for key, name in (('done', 'готово, коли'), ('next', 'далі')):
            v = r[key]
            if not v: bad.append(f'`{r["id"]}`: без «{name}»')
            elif v in EMPTY and r['id'] in near: bad.append(f'`{r["id"]}`: «{name}» — «{v}» у кроку ▶ чи наступного за ним')
        for n in ids(r['next']):
            if n not in seen: bad.append(f'`{r["id"]}`: «далі» → `{n}` — такого кроку нема')
    if play:
        got = reach(rows, play)
        lost = [r['id'] for r in rows if state_of(r) in ('○', '⏸') and r['id'] not in got]
        if lost: warn.append(f'ланцюг «далі» від ▶ `{play}` не доходить до {", ".join(f"`{x}`" for x in lost)}')
        zm = re.search(r'\*\*Зараз[^\n]*', text)
        if not zm: warn.append(f'{qrel}: рядка «**Зараз**» нема')
        elif not has_id(zm.group(0), play) and not re.search(r'карт\w* (маршруту|кроків)', zm.group(0)):
            warn.append(f'{qrel}: «Зараз» не називає ▶ `{play}` і не веде на карту')
        s = hc.latest_summary(repo) if hc else None
        if s and os.path.isfile(s):
            st = open(s, encoding='utf-8').read(); srel = os.path.relpath(s, repo)
            if inject == 'summary': st = st.replace(play, 'X-0')   # зуб: самері забуло ▶
            p1 = re.search(r'(?m)^1\.\s.*', section0(st))
            if not p1 or not has_id(p1.group(0), play): warn.append(f'{srel}: §0 п.1 не називає ▶ `{play}`')
            z = re.search(r'(?m)^ЗАРАЗ:.*', st)
            if z and not has_id(z.group(0), play): warn.append(f'{srel}: стартове «ЗАРАЗ:» не називає ▶ `{play}`')
    live = [r['id'] for r in rows if state_of(r) != '✅']
    for b in sorted(glob.glob(os.path.join(os.path.dirname(qp), '*_brief.md'))):
        for dl in re.findall(r'(?m)^\s*[-*]\s+\*\*Далі[^\n]*', section0(open(b, encoding='utf-8').read())):
            if not any(has_id(dl, x) for x in live): warn.append(f'{os.path.relpath(b, repo)}: §0 «Далі» без живого id карти')
    open_in = [x for x in m['inbox'] if '→' not in x]
    warn += [f'вхідні без «→ куди»: {x[:80]}' for x in open_in]
    if hc:
        try: log = hc.session_log(repo)
        except Exception: log = []
        if log:
            by = sum(1 for _, subj, _ in log if set(ids(subj)) & set(seen))
            info.append(f'за сесію комітів з id кроку {by} з {len(log)}')
    return dict(bad=bad, warn=warn, info=info, play=play, nxt=ids(seen[play]['next']) if play else [], inbox_open=open_in, qrel=qrel)


def line(res):
    if res is None: return 'маршрут: карти нема'
    s = f'маршрут: ▶ {res["play"] or "?"}' + (f' · далі {", ".join(res["nxt"])}' if res['nxt'] else '')
    s += f' · вхідних нерозібраних {len(res["inbox_open"])}' + ''.join(f' · {x}' for x in res['info'])
    return s + (f' · ✗ {len(res["bad"])}' if res['bad'] else '') + (f' · ⚠ {len(res["warn"])}' if res['warn'] else '')


def report(res):
    if res is None: return 'маршрут: карти нема (розділ «… · карта кроків» у черзі) — судити нічого', 0
    out = [f'✗ {x}' for x in res['bad']] + [f'⚠ {x}' for x in res['warn']]
    out.append(f'─── маршрут ({res["qrel"]}): ▶ {res["play"] or "?"} · ✗ {len(res["bad"])} · ⚠ {len(res["warn"])} ───')
    out.append(line(res))
    return '\n'.join(out), 1 if res['bad'] else 0


# ───────── selftest ─────────
GOOD = """# Черга
**Зараз (S1):** крок ▶ карти маршруту нижче.

#### Маршрут v1 · карта кроків

| крок | що | готово, коли | далі | стан |
|---|---|---|---|---|
| `A-1` | перше | зроблено | `A-2` | ✅ 01.01 |
| `A-2` | друге з `a\\|b` у бектиках | тест ✓ | `A-3` | ▶ |
| `A-3` | третє | телефон | `A-4` | ○ |
| `A-4` | четверте | — | маршрут v2 | ○ |

**Вхідні** (нове від Konst):
- 01.01 «ідея» → у крок `A-3`

### §1 Далі
"""
SUM = "# S1\n\n## §0 · ВІДКРИТЕ\n\n1. **Зараз — крок `A-2`.**\n\n## §6\n\n```text\nЗАРАЗ: крок A-2\n```\n"
BRIEF = "# B\n\n## §0 Коротко\n\n- **Далі:** `A-3` після `A-2`\n\n## §1\n"


def _repo(tmp, q, s, b):
    os.makedirs(os.path.join(tmp, 'lens')); os.makedirs(os.path.join(tmp, 'sessions'))
    open(os.path.join(tmp, 'lens', 'X_CHERGA.md'), 'w', encoding='utf-8').write(q)
    open(os.path.join(tmp, 'sessions', 'X_session_summary_S1_T.md'), 'w', encoding='utf-8').write(s)
    if b is not None: open(os.path.join(tmp, 'lens', 'B-1_brief.md'), 'w', encoding='utf-8').write(b)
    for a in (['init', '-q'], ['add', '-A'], ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'init']):
        subprocess.run(['git', '-C', tmp, *a], capture_output=True)


def selftest():
    R = str.replace
    cases = [   # (назва, черга, самері, бриф, inject, чекаємо ✗, підрядок у звіті)
        ('правильна карта → ✗ 0 · ⚠ 0', GOOD, SUM, BRIEF, None, False, '✗ 0 · ⚠ 0'),
        ('`\\|` у бектиках не ріже клітинку (GFM)', GOOD, SUM, BRIEF, None, False, '▶ A-2 · далі A-3'),
        ('нерозекранований `|` у бектиках → ✗ (на GitHub зламано)', R(GOOD, 'a\\|b', 'a|b'), SUM, BRIEF, None, True, 'клітинок 6'),
        ('--inject two → ✗ два ▶', GOOD, SUM, BRIEF, 'two', True, 'рівно один'),
        ('--inject next → ✗ далі на нема', GOOD, SUM, BRIEF, 'next', True, 'NOPE-404'),
        ('--inject summary → ⚠ самері', GOOD, SUM, BRIEF, 'summary', False, '§0 п.1 не називає'),
        ('✅ без дати → ⚠', R(GOOD, '✅ 01.01', '✅'), SUM, BRIEF, None, False, '✅ без дати'),
        ('«далі» ▶ — «—» → ✗', R(GOOD, '| `A-3` | ▶', '| — | ▶'), SUM, BRIEF, None, True, 'у кроку ▶'),
        ('сирота ○ → ⚠', R(GOOD, '| маршрут v2 | ○ |', '| маршрут v2 | ○ |\n| `A-9` | осторонь | x | маршрут v2 | ○ |'), SUM, BRIEF, None, False, 'не доходить'),
        ('вхідні без → ⚠', R(GOOD, '→ у крок `A-3`', 'без рішення'), SUM, BRIEF, None, False, 'вхідні без'),
        ('«Далі» брифу лише на ✅ → ⚠', GOOD, SUM, R(BRIEF, '`A-3` після `A-2`', 'після `A-1`'), None, False, '«Далі» без живого'),
        ('стартове ЗАРАЗ без ▶ → ⚠', GOOD, R(SUM, 'ЗАРАЗ: крок A-2', 'ЗАРАЗ: щось'), BRIEF, None, False, 'стартове «ЗАРАЗ:»'),
        ('«Зараз» черги — переказ без ▶ → ⚠', R(GOOD, 'крок ▶ карти маршруту нижче', 'робимо щось'), SUM, BRIEF, None, False, '«Зараз» не називає'),
        ('невідомий стан → ✗', R(GOOD, '| `A-4` | ○ |', '| `A-4` | ? |'), SUM, BRIEF, None, True, 'не з'),
    ]
    bad = 0
    for name, q, s, b, inj, want_bad, sub in cases:
        tmp = tempfile.mkdtemp(prefix='route_check_')
        try:
            _repo(tmp, q, s, b); res = check(tmp, inject=inj); txt, code = report(res)
            ok = bool(res['bad']) == want_bad and code == (1 if want_bad else 0) and sub in txt
        finally: shutil.rmtree(tmp, ignore_errors=True)
        bad += not ok; print(f'{"✓" if ok else "✗"} {name}' + ('' if ok else '\n    ' + txt.replace('\n', '\n    ')))
    tmp = tempfile.mkdtemp(prefix='route_check_')
    try:
        _repo(tmp, '# Черга\n\n| id | x |\n|---|---|\n', SUM, None); r = check(tmp); ok = r is None and report(r)[1] == 0 and line(r) == 'маршрут: карти нема'
    finally: shutil.rmtree(tmp, ignore_errors=True)
    bad += not ok; print(f'{"✓" if ok else "✗"} карти нема (старий репо) → мовчить, exit 0')
    n = len(cases) + 1
    print(f'─── route_check selftest: {n - bad}/{n} ───'); return 1 if bad else 0


def main(a):
    if not a or a[0] not in ('check', 'line', 'selftest'):
        print('route_check.py check|line <репо> [--queue F] [--inject two|next|summary] | selftest'); return 2
    if a[0] == 'selftest': return selftest()
    repo = os.path.abspath(a[1]) if len(a) > 1 and not a[1].startswith('--') else os.getcwd()
    opt, i = {}, 1
    while i < len(a):
        if a[i] in ('--queue', '--inject') and i + 1 < len(a): opt[a[i][2:]] = a[i + 1]; i += 2
        else: i += 1
    res = check(repo, opt.get('queue'), opt.get('inject'))
    if a[0] == 'line': print(line(res)); return 0
    txt, code = report(res); print(txt); return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
