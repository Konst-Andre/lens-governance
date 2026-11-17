#!/usr/bin/env python3
# живе доки: продукти тримають примірки (tools/claude-code/SHOTS.md). Дім — lens-governance:tools/claude-code/ (QR CC-9, 11.10.2026).
# Перевірка теки shots/ продукту за життєвим циклом SHOTS.md §5–6. Рядок для env_check; exit 1 лише на ✗.
#   python3 shots_check.py <тека репо>            — рядок «примірка: …» (теки нема — тиша, exit 0)
#   python3 shots_check.py <тека репо> --inject   — підкидає знімок без рядка → мусить дати ✗ (зуби)
#   python3 shots_check.py selftest               — випадки в тимчасових теках
# ✗ знімок без рядка README (зведено по теці) · рядок таблиці не з 7 клітинок (AE S152: рядок з 3 клітинками мовчки випадав → 23 знімки «без рядка»;
#   `|` у коді без `\|` давав 8–9 клітинок → дата з чужої колонки, вік не судився, а GitHub зайві клітинки відкидає — GFM «Tables», github.github.com/gfm, 17.11.2026) · жива примірка без знімків · файли після «прийнято / відкинуто» · тека shots/ у ядрі (публічне репо)
# ⚠ жива старша за 14 дн. · тека > 3 МБ · живих > 5 · жива без накладки (fit_*) — не перезняти · PNG/JPG замість WebP
import os, re, sys, datetime, tempfile, shutil

LIVE = ('примірка', 'обрано', 'у роботі', 'застаріло')
DONE = ('прийнято', 'відкинуто')
IMG = re.compile(r'\.(webp|png|jpe?g)$', re.I)
MAX_AGE, MAX_MB, MAX_LIVE = 14, 3, 5


def find(repo):
    for d in ('lens/shots', 'docs/shots', 'shots'):
        if os.path.isdir(os.path.join(repo, d)):
            return d
    return None


COLS = 7   # id · стан · що · варіанти · вибір · куди · дата (SHOTS.md §4)


def cells(line):
    # клітинки рядка таблиці; `\|` (у тексті й у коді) — символ, не межа (GFM «Tables»)
    return [x.strip().replace('\\|', '|') for x in re.split(r'(?<!\\)\|', line.strip().strip('|'))]


def rows(readme, broken=None):
    # рядки таблиці примірок (від заголовка «| id |» до першого рядка не таблиці); неповний чи зайвий — у broken, не мовчки геть
    out, inside = [], False
    for line in open(readme, encoding='utf-8'):
        if not line.startswith('|'):
            inside = False
            continue
        c = cells(line)
        if c[0] == 'id':
            inside = True
            continue
        if not inside or set(c[0]) <= set('-: '):
            continue
        if len(c) != COLS:
            if broken is not None:
                broken.append((c[0].strip('`'), len(c)))
            continue
        out.append({'id': c[0].strip('`'), 'state': c[1].strip('*').strip().lower(), 'date': c[6]})
    return out


def check(repo, today=None, inject=False):
    today = today or datetime.date.today()
    d = find(repo)
    if not d:
        return [], [], 'примірка: теки shots/ нема'
    base = os.path.join(repo, d)
    bad, warn = [], []
    if os.path.exists(os.path.join(repo, 'kernel', 'Lens_INDEX.md')):
        bad.append(f'{d}/ у ядрі — репо публічне, знімки з реальними даними лише в приватному репо продукту')
    readme = os.path.join(base, 'README.md')
    broken = []
    rs = rows(readme, broken) if os.path.exists(readme) else []
    for i, n in broken:
        bad.append(f'рядок README «{i}»: клітинок {n} з {COLS}' + (' — дописати порожні' if n < COLS else ' — `|` у тексті чи коді писати `\\|`'))
    if not os.path.exists(readme):
        bad.append(f'{d}/README.md нема — стан примірок ніде не записано')
    files = {}
    for root, _, fs in os.walk(base):
        for f in fs:
            rel = os.path.relpath(os.path.join(root, f), base)
            files[rel] = os.path.getsize(os.path.join(root, f))
    if inject:
        files['zz_inject/x.webp'] = 1
    owner = lambda rel: next((r for r in rs if rel.split('/')[0] == r['id'] or rel.split('/')[0].startswith(r['id'] + '_')), None)
    orphan = {}
    for rel in sorted(files):
        if rel == 'README.md':
            continue
        r = owner(rel)
        if IMG.search(rel) and not r:
            orphan.setdefault(rel.split('/')[0] if '/' in rel else '.', []).append(rel)
        elif r and r['state'] in DONE:
            bad.append(f'{r["id"]} «{r["state"]}», а файл лишився: {rel} — видалити (історія — git)')
        if IMG.search(rel) and not rel.lower().endswith('.webp'):
            warn.append(f'не WebP: {rel}')
    for d, fs in orphan.items():   # зведено по теці: 23 однакові пункти ховали причину за обрізаним рядком env_check
        bad.append(f'знімок без рядка README: {fs[0]}' if len(fs) == 1 else f'знімків без рядка README: {d}/ — {len(fs)} (напр. {os.path.basename(fs[0])})')
    live = [r for r in rs if r['state'] in LIVE]
    for r in live:
        mine = [f for f in files if owner(f) is r]
        if not any(IMG.search(f) for f in mine):
            bad.append(f'{r["id"]} «{r["state"]}» без знімків')
        elif not any(os.path.basename(f).startswith('fit_') for f in mine):
            warn.append(f'{r["id"]} без накладки fit_* — не перезняти й не почати код з обраного')
        m = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', r['date'])
        if m:
            age = (today - datetime.date(int(m[3]), int(m[2]), int(m[1]))).days
            if age > MAX_AGE:
                warn.append(f'{r["id"]} «{r["state"]}» {age} дн. — перезняти або Konst підтверджує (застаріло)')
    unknown = [r['id'] for r in rs if r['state'] not in LIVE + DONE]
    if unknown:
        bad.append('невідомий стан у рядках: ' + ' '.join(unknown) + ' (стани — SHOTS.md §5)')
    mb = sum(v for k, v in files.items() if k != 'README.md') / 1e6
    if mb > MAX_MB:
        warn.append(f'тека {mb:.1f} МБ > {MAX_MB}')
    if len(live) > MAX_LIVE:
        warn.append(f'живих примірок {len(live)} > {MAX_LIVE}')
    head = f'примірка: живих {len(live)} · {mb:.2f} МБ'
    return bad, warn, head


def line(repo, inject=False):
    bad, warn, head = check(repo, inject=inject)
    if bad:
        return 1, '✗ ' + head + ' · ' + ' · '.join(bad + warn)
    if warn:
        return 0, '⚠ ' + head + ' · ' + ' · '.join(warn)
    return 0, head + (' ✓' if 'нема' not in head else '')


def selftest():
    ok = n = 0
    T = tempfile.mkdtemp()
    def case(name, readme, files, want, today=datetime.date(2026, 10, 11), want_txt=''):
        nonlocal ok, n
        n += 1
        r = os.path.join(T, str(n)); s = os.path.join(r, 'lens', 'shots'); os.makedirs(s)
        if readme is not None:
            open(os.path.join(s, 'README.md'), 'w', encoding='utf-8').write('| id | стан | що | варіанти | вибір | куди | дата |\n|---|---|---|---|---|---|---|\n' + readme)
        for f in files:
            p = os.path.join(s, f); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(b'x')
        bad, warn, _ = check(r, today)
        got = '✗' if bad else ('⚠' if warn else '✓')
        if got == want and want_txt in ' · '.join(bad + warn):
            ok += 1
        else:
            print(f'✗ {name} → {got}, очікував {want}: {bad + warn}')
    row = lambda i, st, dt='10.10.2026': f'| {i} | {st} | x | x | x | x | {dt} |\n'
    case('жива з усім', row('QRL-1', 'обрано'), ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css'], '✓')
    case('знімок без рядка', row('QRL-1', 'обрано'), ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css', 'QRL-2_x/a.webp'], '✗')
    case('жива без знімків', row('QRL-1', 'обрано'), ['QRL-1_t/fit_b.css'], '✗')
    case('прийнято, файли лишились', row('QRL-1', 'прийнято'), ['QRL-1_t/light.webp'], '✗')
    case('прийнято й прибрано', row('QRL-1', 'прийнято'), [], '✓')
    case('без накладки', row('QRL-1', 'обрано'), ['QRL-1_t/light.webp'], '⚠')
    case('стара', row('QRL-1', 'обрано', '20.09.2026'), ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css'], '⚠')
    case('PNG', row('QRL-1', 'обрано'), ['QRL-1_t/light.png', 'QRL-1_t/fit_b.css'], '⚠')
    case('README нема', None, ['QRL-1_t/light.webp'], '✗')
    case('невідомий стан', row('QRL-1', 'думаю'), [], '✗')
    case('рядок з 3 клітинками — ✗ з причиною', '| QRL-1 | обрано | x |\n', ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css'], '✗', want_txt='клітинок 3 з 7')
    case('`|` у коді без `\\|` — ✗ з причиною', '| QRL-1 | обрано | `?v=a|b` | x | x | x | 10.10.2026 |\n', ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css'], '✗', want_txt='клітинок 8 з 7')
    case('`\\|` у коді — одна клітинка, дата читається', '| QRL-1 | обрано | `?v=a\\|b` | x | x | x | 20.09.2026 |\n', ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css'], '⚠', want_txt='21 дн.')
    case('знімки без рядка — зведено по теці', row('QRL-1', 'обрано'), ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css'] + [f'QRL-2_x/{i}.webp' for i in range(5)], '✗', want_txt='QRL-2_x/ — 5')
    case('інша таблиця нижче не судиться', row('QRL-1', 'обрано') + '\nтекст\n\n| a | b |\n|---|---|\n| 1 | 2 |\n', ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css'], '✓')
    case('id-префікс не плутає QRL-1 і QRL-10', row('QRL-1', 'обрано'), ['QRL-1_t/light.webp', 'QRL-1_t/fit_b.css', 'QRL-10_y/a.webp'], '✗')
    shutil.rmtree(T)
    print(f'shots_check selftest: {ok}/{n}')
    return ok == n


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'selftest':
        sys.exit(0 if selftest() else 1)
    code, msg = line(a[0] if a else '.', inject='--inject' in a)
    print(msg)
    sys.exit(code)
