#!/usr/bin/env python3
# живе доки: пам'ять сесії — лише репо, і сесії переїжджають у нові чати (профіль Konst «САМЕРІ»).
# Перевірка пам'яті перед переїздом (HOOK-3.2, бриф — archive/summaries/Lens_gov/Lens_kernel_BRIEF_HOOK-3.2_closed.md; «так» Konst 09.10.2026, QR-Lens CC-5).
# Ловить машинно те, що новий агент не зможе знайти чи зрозуміти: самері без §0 / стартового, самері відстає від комітів,
# мертві й голі шляхи в §0 · стартовому · «Коротко» плану, історія в §0, гейт черги, README старіший за правила.
# Якість тексту НЕ судить — це робить агент за чек-листом гачка hooks/handoff-remind.sh.
#
# Запуск:  python3 tools/claude-code/handoff_check.py <тека репо> [<тека репо> …]    → рядки ✓ / ⚠ / ✗ / ⓘ; exit 1 на ✗
#          python3 tools/claude-code/handoff_check.py selftest                         → зуби: тимчасові репо, усі випадки брифу
# «Свої» коміти — за трейлером Claude-Session ≡ CLAUDE_CODE_REMOTE_SESSION_ID (cse_X ↔ session_X); нема змінної — усі коміти агента.
import glob, os, re, subprocess, sys, tempfile, time

KERNEL_NAMES = ('lens-governance',)
EXT = r'(?:md|sh|py|mjs|js|json|toml|ya?ml|html|htm|css|xlsx|txt|csv)'
# шлях: [Репо:]тека/…/файл.розш · тека/ · або гола назва файл.розш (без теки)
PATH_RE = re.compile(r'(?<![\w/.:<>*-])(?:([A-Za-z][\w.-]*):)?((?:[\w.-]+/)+(?:[\w.-]+\.' + EXT + r')?|[\w.-]+\.' + EXT + r')(?![\w/<>*-])')
STALE_RE = re.compile(r'цей коміт|чекає вироку', re.I)
N_BRIEF, Q_ROW = 2, 2000   # (8): «пункт розтягнувся на 2+ сесії» — той самий поріг, що в шаблоні брифу; Q_ROW — як `q_long` гейта ядра (BRIEF-2 5б–5в)


def git(repo, *a):
    r = subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ''


def section(text, head_re):
    """Текст розділу «## …», чий заголовок збігся з head_re, до наступного «## »."""
    out, on = [], False
    for ln in text.splitlines():
        if ln.startswith('## '):
            if on: break
            on = bool(re.search(head_re, ln, re.I))
            continue
        if on: out.append(ln)
    return '\n'.join(out) if on or out else None


def starter(text):
    m = re.search(r'^```text[^\n]*\n(.*?)^```', text, re.M | re.S)
    return m.group(1) if m else None


SUM_DIRS = ('sessions', 'docs/summary')   # продукт Lens (Р-7) · не-Lens каркас (AE, AirLens; ADOPT.md «три шляхи»); перша наявна — як pytest rootdir (S90 AE 18.10.2026: бачило лише sessions/)


def sum_dir(repo):
    return next((d for d in SUM_DIRS if os.path.isdir(os.path.join(repo, d))), SUM_DIRS[0])


def live_summary(repo):
    """Живе самері в sessions/ або docs/summary/ (і підтеках): ще не в коміті → найновіше; інакше — останній коміт, при рівному — пізніше створене
    (заморожене попереднє й нове міняються одним комітом)."""
    best, bt = None, None
    for root, _, files in os.walk(os.path.join(repo, sum_dir(repo))):
        for f in files:
            if not (f.endswith('.md') and 'summary' in f.lower()): continue
            p = os.path.join(root, f); rel = os.path.relpath(p, repo)
            last = int(git(repo, 'log', '-1', '--format=%ct', '--', rel) or 0)
            born = git(repo, 'log', '--diff-filter=A', '--format=%ct', '--', rel).split()
            t = (float('inf'), 0) if not last else (last, int(born[-1]) if born else 0)
            if bt is None or t > bt: best, bt = rel, t
    return best


def repo_dir(repo, name):
    """Тека іншого репо для «Репо:шлях»: сусідня тека, для ядра — ще /tmp/lens-governance."""
    base = os.path.dirname(os.path.abspath(repo))
    if os.path.basename(os.path.abspath(repo)).lower() == name.lower(): return repo
    for c in os.listdir(base):
        if c.lower() == name.lower() and os.path.isdir(os.path.join(base, c)): return os.path.join(base, c)
    if name.lower() in KERNEL_NAMES and os.path.isdir('/tmp/lens-governance'): return '/tmp/lens-governance'
    return None


def check_paths(repo, text, where, lines):
    dead, bare, other, seen = [], [], set(), set()
    for m in PATH_RE.finditer(text):
        rp, p = m.group(1), m.group(2)
        if rp and rp.lower() in ('http', 'https'): continue
        if re.match(r'^[a-z0-9-]+(\.[a-z0-9-]+)*\.(com|dev|org|net|io|app|ua)/', p, re.I): continue   # адреса без https:// («dash.cloudflare.com/…») — не шлях у репо (хибне ✗ 10.10, QR CC-7)
        key = (rp or '') + ':' + p
        if key in seen: continue
        seen.add(key)
        if rp:
            d = repo_dir(repo, rp)
            if d is None: other.add(rp); continue
            if not os.path.exists(os.path.join(d, p)): dead.append(f'{rp}:{p}')
        elif '/' not in p:
            if not os.path.exists(os.path.join(repo, p)): bare.append(p)
        elif not os.path.exists(os.path.join(repo, p)):
            dead.append(p)
    n = len(seen)
    if dead: lines.append(('✗', f'{where}: мертві шляхи — ' + ' · '.join(dead[:8])))
    if bare: lines.append(('✗', f'{where}: голі назви (новий агент не знайде) — ' + ' · '.join(bare[:8]) + ' → дай повний шлях'))
    if other: lines.append(('ⓘ', f'{where}: шляхи інших репо не звірено (нема поруч) — ' + ', '.join(sorted(other))))
    if not dead and not bare: lines.append(('✓', f'{where}: шляхи живі ({n})'))


def mine_tail():
    sid = os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID', '')
    return sid.split('_', 1)[1] if '_' in sid else ''


def check_repo(repo, now=None):
    now = now or time.time()
    repo = os.path.abspath(repo)
    name = os.path.basename(repo)
    is_kernel = os.path.isdir(os.path.join(repo, 'kernel'))
    L = []
    sm = live_summary(repo)
    if not sm:
        L.append(('✗', 'самері не знайдено (sessions/ або docs/summary/)')); return name, L
    text = open(os.path.join(repo, sm), encoding='utf-8').read()
    s0, st = section(text, r'^## §0'), starter(text)
    L.append(('✓' if s0 else '✗', f'{sm}: §0 ' + ('є' if s0 else 'нема (заголовок «## §0 …»)')))
    L.append(('✓' if st else '✗', 'стартове повідомлення ' + ('є (блок text)' if st else 'нема — блок ```text у самері')))
    # (2) самері не відстає — логіка QR-Lens:tools/env_check.sh «самері відстає»
    last = git(repo, 'log', '-1', '--format=%H', '--', sm)
    tail = mine_tail()
    grep = f'session_{tail}' if tail else 'Claude-Session'
    after = git(repo, 'log', '--format=%h', f'--grep={grep}', f'{last}..HEAD') if last else ''
    n = len(after.split()) if after else 0
    owns = (not tail) or bool(git(repo, 'log', '--format=%h', f'--grep=session_{tail}', '--', sum_dir(repo) + '/'))
    if n and is_kernel and not owns:
        L.append(('ⓘ', f'самері ядра веде сесія ядра; коміти цієї сесії тут — {n}: вони мають бути в самері репо продукту (Lens_governance_protocol.md:139)'))
    elif n:
        L.append(('✗', f'самері відстає: після {last[:7]} комітів агента без самері — {n} ({" ".join(after.split()[:5])}) → §0/§1'))
    else:
        L.append(('✓', 'самері не відстає'))
    # (3) шляхи: §0 · стартове · «Коротко» планів, на які посилається §0
    if s0: check_paths(repo, s0, '§0', L)
    if st: check_paths(repo, st, 'стартове', L)
    for m in PATH_RE.finditer(s0 or ''):
        rp, p = m.group(1), m.group(2)
        if rp or not p.endswith('.md') or 'sessions/' in p or 'docs/summary/' in p: continue
        f = os.path.join(repo, p)
        if not os.path.isfile(f): continue
        k = section(open(f, encoding='utf-8').read(), r'Коротко')
        if k is not None: check_paths(repo, k, f'{p} «Коротко»', L)
    # (4) історія в §0
    if s0:
        h = sorted({m.group(0).lower() for m in STALE_RE.finditer(s0)})
        if h: L.append(('⚠', '§0 має «' + '», «'.join(h) + '» — історія чи ще відкрите? (у §0 — лише як є)'))
    # (5) гейт: черга під стелею, рядки ≤ 2000 знаків — Lens_validate.py
    kd = repo if is_kernel else repo_dir(repo, 'lens-governance')
    v = os.path.join(kd or '', 'kernel/Lens_validate.py')
    if kd and os.path.isfile(v) and (is_kernel or os.path.isdir(os.path.join(repo, 'lens'))):
        r = subprocess.run([sys.executable, v, '--gov' if is_kernel else '--product', '.'], cwd=repo, capture_output=True, text=True)
        tot = [x for x in r.stdout.splitlines() if 'ПІДСУМОК' in x]
        s = tot[-1].strip() if tot else 'підсумку нема'
        L.append(('✗' if re.search(r'✗ [1-9]', s) else '✓', 'гейт: ' + s))
    # (6) описи відстали від змін (уточнення Konst 09.10, CC-6: README був прикладом, суть — «новий агент не зрозуміє»):
    # код, змінений комітами цієї сесії → усі .md, що його згадують (README · ARCHITECTURE · план · INDEX · CLAUDE.md …), а сесія їх не міняла → ⚠ перевір
    if tail:
        ch = [x for x in git(repo, 'log', f'--grep=session_{tail}', '--name-only', '--format=').split('\n') if x]
        code = sorted({x for x in ch if not x.endswith('.md') and not x.startswith(('sessions/', 'docs/summary/', 'archive/')) and os.path.isfile(os.path.join(repo, x))})
        touched = {x for x in ch if x.endswith('.md')}
        docs = [d for d in git(repo, 'ls-files', '*.md').split('\n') if d and not d.startswith(('sessions/', 'docs/summary/', 'archive/'))]
        stale = {}
        for d in docs:
            if d in touched: continue
            try: t = open(os.path.join(repo, d), encoding='utf-8').read()
            except OSError: continue
            hits = [c for c in code if c in t or (len(os.path.basename(c)) >= 8 and os.path.basename(c) in t)]
            if hits: stale[d] = hits
        # вузловий файл (його згадують > 4 описів, що не мінялись) — згадки довідкові: один рядок ⓘ замість ⚠ на кожен документ
        # (еволюція гачка 10.10: Lens_validate.py дав ⚠ на 10 документів ядра — шум; слово Konst «гачок має самопокращуватись»)
        cnt = {c: sum(c in v for v in stale.values()) for c in code}
        hubs = sorted(c for c, n in cnt.items() if n > 4)
        if hubs:
            L.append(('ⓘ', 'вузлові файли сесії — їх згадують багато описів: ' + ' · '.join(f"{os.path.basename(c)} ({cnt[c]})" for c in hubs) + ' — перевір лише ті описи, що розповідають саме про змінену поведінку'))
            stale = {d: [c for c in v if c not in hubs] for d, v in stale.items()}; stale = {d: v for d, v in stale.items() if v}
        if stale:
            top = sorted(stale, key=lambda d: -len(stale[d]))[:6]
            L.append(('⚠', 'описи, що згадують змінений у сесії код, але не мінялись: ' + ' · '.join(f"{d} ({', '.join(os.path.basename(c) for c in stale[d][:3])})" for d in top) +
                      (f' (+{len(stale) - 6})' if len(stale) > 6 else '') + ' — перевір, чи новий агент не піде за протухлим описом'))
        elif code: L.append(('✓', f'описи змін сесії оновлено (код: {len(code)} файлів)'))
    # (8) кандидат у бриф (BRIEF-1, розширення 10.10): id відкритої черги згадано в самері ≥ N_BRIEF різних сесій, а брифу / плану з цим id нема.
    #     BRIEF-2 5б–5в (AE S94, заміри на AE): поріг 3 → 2 (= шаблон); id з літерами (`AE-PORT`) раніше були невидимі; «бриф є» = id у назві
    #     файлу брифу / плану або в його шапці (до першого `## `), а не будь-яка згадка — бриф AE-PORT згадував AE-T · D3 · E2 · POL і глушив усі.
    #     Не-Lens репо: рядок черги > Q_ROW → ⚠ «час для брифу» (у Lens це ✗ гейта `q_long`).
    qf = [f for f in (glob.glob(os.path.join(repo, 'lens', '*_CHERGA.md')) + glob.glob(os.path.join(repo, 'kernel', '*_CHERGA.md')) + glob.glob(os.path.join(repo, 'docs', 'CHERGA.md')))]
    if qf:
        qt = open(qf[0], encoding='utf-8').read(); qt = qt[qt.find('## Відкрите'):] if '## Відкрите' in qt else qt
        ids = sorted(set(re.findall(r'^\|\s*\*{0,2}`([A-Z]+-[A-Z0-9]+(?:\.\d+)?)`', qt, re.M)))
        sums = [p for p in glob.glob(os.path.join(repo, 'sessions', '**', '*summary*.md'), recursive=True) + glob.glob(os.path.join(repo, 'docs', 'summary', '**', '*.md'), recursive=True) + glob.glob(os.path.join(repo, 'archive', 'summaries', '**', '*summary*.md'), recursive=True)]
        briefs = [p for p in glob.glob(os.path.join(repo, '**', '*.md'), recursive=True) if re.search(r'brief|BRIEF|PLAN|_plan', os.path.basename(p)) and '/archive/' not in p]
        btxt = ' '.join(os.path.basename(p) + ' ' + open(p, encoding='utf-8', errors='replace').read().split('\n## ', 1)[0] for p in briefs)   # назва + шапка
        cand = []
        for i in ids:
            n = sum(1 for p in sums if re.search(r'(?<![\w-])' + re.escape(i) + r'(?![\w.])', open(p, encoding='utf-8', errors='replace').read()))
            row = next((l for l in qt.splitlines() if re.match(r'^\|\s*\*{0,2}`' + re.escape(i) + '`', l)), '')   # «бриф не треба: <чому>» у рядку черги — відповідь на цей ⚠ (18.10.2026: без неї ⚠ висів вічно)
            if n >= N_BRIEF and 'бриф не треба' not in row.lower() and not re.search(r'(?<![A-Za-z0-9-])' + re.escape(i) + r'(?![A-Za-z0-9]|\.\d)', btxt): cand.append(f'{i} ({n} самері)')
        if cand: L.append(('⚠', f'кандидат у бриф — пункт тягнеться ≥ {N_BRIEF} сесії, а брифу нема: ' + ' · '.join(cand[:5]) + ' → tools/claude-code/templates/BRIEF_template.md (з прополкою джерел) або рядок «чому не треба»'))
        if not os.path.isdir(os.path.join(repo, 'kernel')) and not glob.glob(os.path.join(repo, 'lens', '*_INDEX.md')):
            lng = [f"{m.group(1)} ({len(l)})" for l in qt.splitlines() for m in [re.match(r'^\|\s*\*{0,2}`([^`]+)`', l)] if m and len(l) > Q_ROW]
            if lng: L.append(('⚠', f'час для брифу — рядок черги > {Q_ROW} знаків (наріс шарами): ' + ' · '.join(lng[:5]) + ' → tools/claude-code/templates/BRIEF_template.md, у черзі — стан і вказівник'))
    # (9) бриф за шаблоном і свіжий (BRIEF-2, «так» Konst 19.10.2026, AE S93): бриф AE-PORT народився повз шаблон, а (3) мовчки пропускав
    #     бриф без «Коротко» — відсутність стандарту виглядала як «усе гаразд». Тепер: живий бриф без §0 «Коротко» зі Стан · Далі · Чекає — ✗
    #     (і в `kernel/`: до 19.10 там був виняток ⚠ для спільного файла брифів — розпилено, AE S94); свіжість — після останньої правки брифу є коміти, що змінили
    #     не лише .md, — ⚠ «відстає на N» (світ: stale-cli, Doc Drift Detector — історія git документа ⟂ коду, 19.10.2026; нагадування на коміт —
    #     hooks/brief-guard.sh). Сліпа пляма (та сама у світі): будь-яка правка брифу робить його «свіжим», навіть не в «Коротко».
    for p in sorted(glob.glob(os.path.join(repo, '**', '*.md'), recursive=True)):
        rel = os.path.relpath(p, repo).replace(os.sep, '/')
        if not re.search(r'(^|/)briefs/[^/]+\.md$|_brief\.md$|BRIEF[^/]*\.md$', rel) or rel.startswith('archive/') or '/archive/' in rel or 'templates/' in rel: continue
        k = section(open(p, encoding='utf-8', errors='replace').read(), r'Коротко')
        if k is None or not all(re.search(w, k) for w in ('Стан', 'Далі', 'Чекає')):
            L.append(('✗', f'бриф {rel} не за шаблоном: нема §0 «Коротко» зі Стан · Далі · Чекає → tools/claude-code/templates/BRIEF_template.md')); continue
        last = git(repo, 'log', '-1', '--format=%H', '--', rel)
        if last:
            n = sum(1 for c in git(repo, 'log', '--format=%H', f'{last}..HEAD').split() if any(f and not f.endswith('.md') for f in git(repo, 'show', '--name-only', '--format=', c).split('\n'))
                    and not re.search(r'бриф\s*:', git(repo, 'log', '-1', '--format=%B', c), re.I))   # «бриф: …» у коміті — брифи розглянуто свідомо (як brief-guard); AE S94: код BRIEF-2 робив «відсталим» бриф ARCH-1
            if n: L.append(('⚠', f'бриф {rel} відстає: {n} коміт(ів) коду після його останньої правки — §0 «Коротко» і «Кроки» ще «як є»?'))
    # (7) незбережене: контейнер скинеться — пропаде
    dirty = [x for x in subprocess.run(['git', '-C', repo, 'status', '--porcelain'], capture_output=True, text=True).stdout.split('\n') if x.strip()]
    if dirty: L.append(('✗', f'незакомічене: {len(dirty)} ({", ".join(x[3:] for x in dirty[:4])}) — коміт і push до переїзду'))
    if git(repo, 'remote'):
        if not git(repo, 'branch', '-r', '--contains', 'HEAD'): L.append(('✗', 'HEAD нема на жодній гілці GitHub — push до переїзду'))
        else:
            n_main = git(repo, 'rev-list', '--count', 'origin/main..HEAD')
            if n_main and n_main != '0': L.append(('ⓘ', f'у main нема {n_main} комітів (лише гілка сесії) — так задумано?'))
    return name, L


def hooks_journal(repos):
    """HOOK-5: спрацювання гачків цієї сесії (/tmp/lens-hooks-<сесія>.tsv, пише диспетчер) мають вердикти в журналі ядра."""
    sid = re.sub(r'[^A-Za-z0-9_-]', '', os.environ.get('CLAUDE_CODE_SESSION_ID', ''))
    log = f'/tmp/lens-hooks-{sid}.tsv' if sid else ''
    if not log or not os.path.isfile(log): return [('ⓘ', 'журнал гачків: спрацювань цієї сесії не записано (лог диспетчера порожній)')]
    rows = [l.split('\t') for l in open(log, encoding='utf-8', errors='replace') if l.strip()]
    by = {}
    for r in rows:
        if len(r) >= 3: by[r[2]] = by.get(r[2], 0) + 1
    # ядро — серед репо, поруч із ними (../lens-governance) або клон env_check; без «поруч» сесія продукту брала старий /tmp-клон → хибне ✗ (10.10)
    roots = list(repos) + [os.path.join(os.path.dirname(r), 'lens-governance') for r in repos] + ['/tmp/lens-governance']
    k = next((os.path.join(r, 'tools/claude-code/hooks/HOOK_JOURNAL.md') for r in roots if os.path.isfile(os.path.join(r, 'tools/claude-code/hooks/HOOK_JOURNAL.md'))), None)
    tail = mine_tail()
    msg = 'гачки цієї сесії спрацювали: ' + ' · '.join(f'{h} {n}' for h, n in sorted(by.items()))
    if not k: return [('⚠', msg + ' — журнал гачків не знайдено (ядра нема ні поруч, ні в /tmp/lens-governance): склонувати ядро й записати вердикти')]
    seen = tail and ('session_' + tail[:8]) in open(k, encoding='utf-8').read()
    if seen: return [('✓', msg + ' — вердикти в журналі гачків є')]
    return [('✗', msg + f' — вердиктів нема: розібрати (справжнє · хибне · дубль · пропуск) у tools/claude-code/hooks/HOOK_JOURNAL.md §1, ідентифікатор `session_{tail[:8] if tail else "?"}`; хибне чи пропуск — виправити гачок + тест')]

# Ріст журналу (Konst 10.10: «хто контролює, наскільки виріс файл?»): §1 — лише живі рядки (≤ 30 дн.), рядок — коротко (деталь — у коміті),
# файл ≤ 24 КБ (читається точково, але §0 + свіжий §1 — за один погляд). Старше → ротація в теку journal/ поруч, лічильники — у §0.
J_AGE, J_KB, J_ROW = 30, 24, 700
def journal_health(k, today=None):
    import datetime as dt
    today = today or dt.date.today()
    txt = open(k, encoding='utf-8').read()
    body = txt.split('## §1', 1)[1].split('\n## ', 1)[0] if '## §1' in txt else ''
    rows = [l for l in body.splitlines() if re.match(r'^\| \d\d\.\d\d \|', l)]
    ages = []
    for l in rows:
        d, m = map(int, re.match(r'^\| (\d\d)\.(\d\d)', l).groups())
        x = dt.date(today.year, m, d)
        if x > today: x = dt.date(today.year - 1, m, d)
        ages.append((today - x).days)
    kb = len(txt.encode()) / 1024; old = max(ages, default=0); long = sum(len(l) > J_ROW for l in rows)
    s = f'журнал гачків: §1 {len(rows)} рядків · {kb:.0f} КБ · найстаріший {old} дн.'
    why = [w for c, w in [(old > J_AGE, f'рядки старші за {J_AGE} дн. → ротація: перенести в journal/HOOK_JOURNAL_<рік-міс>.md, лічильники — у §0'),
                          (kb > J_KB, f'файл > {J_KB} КБ → ротація (те саме)'), (long, f'довгих рядків (> {J_ROW} знаків) {long} → деталь у коміт, у рядку — суть')] if c]
    return ('⚠', s + ' — ' + ' · '.join(why)) if why else ('✓', s)

# Лічильники §0 журналу (18.10.2026, AE S91): з УСІХ рядків — живий §1 + journal/*.md, а не руками.
# Вердикт = слово + число: «хибне 2» · «хибне ×3» → 2 · 3; без числа — 1. «еволюція 14» — порядковий номер → 1 (лише «×N» — кількість).
# Не рахуються: «виправлено хибне ×3» (це виправлення), «(не хибне)», число одиниці виміру («хибні 22 файли»), дата («хибне 16.10» → 1), «справжніх нема / 0» → 0.
T_CHECKS = [('ui-guard', 'ui-guard'), ('commit-gate', 'commit-gate'), ('commit_files', 'commit-gate'), ('ui-review-gate', 'ui-review-gate'),
            ('чек-лист очей', 'ui-review-gate'), ('огляд', 'ui-review-gate'), ('review-remind', 'review-remind'), ('memory-guard', 'memory-guard'),
            ('handoff-remind', 'handoff-remind'), ('plan-web', 'plan-web'), ('рецепт як закон', 'plan-web'), ('план без світу', 'plan-web'),
            ('konst-miss', 'konst-miss'), ('ui_lint', 'ui_lint'), ('handoff_check', 'handoff_check'), ('Lens_validate', 'Lens_validate'),
            ('гейт `--', 'Lens_validate'), ('doc_health', 'doc_health'), ('env_check', 'env_check'), ('frame_check', 'frame_check')]
T_COLS = [('справжніх', r'справжн\w*|влучне', False), ('хибних', r'хибн\w*', False), ('пропусків агента', r'пропуск\w*\s+(?:агента|очей\s*\(мій)', False),
          ('пропусків Konst', r'пропуск\w*(?:\s+очей)?\s+konst', False), ('еволюцій', r'еволюці\w*', True)]
def journal_tally(paths):
    import collections
    out = collections.defaultdict(collections.Counter)
    for p in paths:
        for l in open(p, encoding='utf-8'):
            if not re.match(r'^\| \d\d\.\d\d \|', l): continue
            c = l.split('|'); vl = c[4].lower() if len(c) > 4 else ''
            hits = [(c[3].find(s), k) for s, k in T_CHECKS if s in c[3]]; key = min(hits)[1] if hits else 'інше'   # перша названа в комірці
            for col, rx, ordinal in T_COLS:
                for m in re.finditer(rx, vl):
                    if re.search(r'(виправлено|не)\s*$', vl[max(0, m.start() - 12):m.start()]): continue
                    t = vl[m.end():m.end() + 12]
                    if re.match(r'[\s*:]*(нема|немає|0\b)', t): continue   # «справжніх нема» · «справжніх 0»
                    x = re.match(r'[\s*:]*×\s*(\d+)', t) or (None if ordinal else re.match(r'[\s*]*(\d+)(?![\d–-]|\.\d|\s*(?:файл|рядк|самері|кб|дн))', t))   # «16.10» — дата
                    out[key][col] += int(x.group(1)) if x else 1
    return out

def report(repos):
    bad = False
    for r in repos:
        name, L = check_repo(r)
        print(f'— {name}')
        for s, t in L:
            print(f'  {s} {t}'); bad |= s == '✗'
    print('— гачки')
    for s, t in hooks_journal([os.path.abspath(r) for r in repos]):
        print(f'  {s} {t}'); bad |= s == '✗'
    roots = [os.path.abspath(r) for r in repos]; roots += [os.path.join(os.path.dirname(r), 'lens-governance') for r in roots] + ['/tmp/lens-governance']
    k = next((os.path.join(r, JPATH) for r in roots if os.path.isfile(os.path.join(r, JPATH))), None)
    if k: s, t = journal_health(k); print(f'  {s} {t}')   # ріст — ⚠, не ✗: переїзд не блокує, але нагадує ротацію
    dh = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doc_health.py')   # документи кожного репо — ⚠ на переїзді, щоб не висіли без господаря (DOC-1)
    for r in repos:
        if os.path.isfile(dh): out = subprocess.run([sys.executable, dh, r], capture_output=True, text=True).stdout.strip().splitlines(); out and print(f'  {os.path.basename(os.path.abspath(r))}: {out[-1]}')
    return 1 if bad else 0
JPATH = 'tools/claude-code/hooks/HOOK_JOURNAL.md'


def selftest():
    def sh(d, *c): subprocess.run(c, cwd=d, check=True, capture_output=True)
    def mk(summary, extra=None, commit_after=False, new_after=False, both=False, dirty=False, code_after=False):
        d = tempfile.mkdtemp(prefix='hc-'); r = os.path.join(d, 'Prod'); os.makedirs(os.path.join(r, 'sessions')); os.makedirs(os.path.join(r, 'lens'))
        sh(r, 'git', 'init', '-q'); sh(r, 'git', 'config', 'user.email', 't@t'); sh(r, 'git', 'config', 'user.name', 't')
        open(os.path.join(r, 'lens/A.md'), 'w').write('## 0. Коротко\n- далі `lens/A.md`\n')
        open(os.path.join(r, 'CLAUDE.md'), 'w').write('x')
        later = extra if new_after else {}
        for p, t in (extra or {}).items():
            if p not in later: os.makedirs(os.path.dirname(os.path.join(r, p)), exist_ok=True); open(os.path.join(r, p), 'w').write(t)
        open(os.path.join(r, 'sessions/P_session_summary_X.md'), 'w').write(summary)
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'самері\n\nClaude-Session: https://claude.ai/code/session_' + ('OLD' if code_after else 'T'))   # опис — від попередньої сесії
        if later:
            time.sleep(1.1)
            for p, t in later.items(): open(os.path.join(r, p), 'w').write(t)
            if both:
                open(os.path.join(r, 'sessions/P_session_summary_X.md'), 'a').write('заморожено\n')
                sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'нове самері\n\nClaude-Session: https://claude.ai/code/session_T')
        if code_after:
            os.makedirs(os.path.join(r, 'tools')); open(os.path.join(r, 'tools/run_me.sh'), 'w').write('echo')
            sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'код\n' + (code_after if isinstance(code_after, str) else '') + '\nClaude-Session: https://claude.ai/code/session_T')
            open(os.path.join(r, 'sessions/P_session_summary_X.md'), 'a').write('\n'); sh(r, 'git', 'commit', '-qam', 'самері\n\nClaude-Session: https://claude.ai/code/session_T')
        if dirty: open(os.path.join(r, 'lens/A.md'), 'a').write('z')
        if commit_after:
            open(os.path.join(r, 'lens/A.md'), 'a').write('y'); sh(r, 'git', 'commit', '-qam', 'код\n\nClaude-Session: https://claude.ai/code/session_T')
        return r
    def mk_nl(summary, q='## Відкрите\n| `AE-W` | x | 18.10.2026 | y |\n'):   # не-Lens каркас (AE): самері docs/summary/<P>_SUMMARY_<дата>.md, черга docs/CHERGA.md
        d = tempfile.mkdtemp(prefix='hc-'); r = os.path.join(d, 'Prod'); os.makedirs(os.path.join(r, 'docs/summary'))
        sh(r, 'git', 'init', '-q'); sh(r, 'git', 'config', 'user.email', 't@t'); sh(r, 'git', 'config', 'user.name', 't')
        open(os.path.join(r, 'docs/CHERGA.md'), 'w').write(q); open(os.path.join(r, 'CLAUDE.md'), 'w').write('x')
        open(os.path.join(r, 'docs/summary/P_SUMMARY_2026-10-18.md'), 'w').write(summary)
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'самері\n\nClaude-Session: https://claude.ai/code/session_T')
        return r
    good_nl = '# S\n## §0 ВІДКРИТЕ\n- далі `docs/CHERGA.md`; правила — CLAUDE.md\n## §6 Стартове\n```text\nСтарт: docs/CHERGA.md → docs/summary/P_SUMMARY_2026-10-18.md\n```\n'
    good = '# S\n## §0 ВІДКРИТЕ\n- далі `lens/A.md` §0 «Коротко»; правила — CLAUDE.md\n## §6 Стартове\n```text\nСтарт: lens/A.md → sessions/P_session_summary_X.md\n```\n'
    os.environ['CLAUDE_CODE_REMOTE_SESSION_ID'] = 'cse_T'
    cases = [
        ('усе гаразд → тиша (лише ✓/ⓘ)', mk(good), None),
        ('самері без стартового → ✗', mk(good.split('## §6')[0]), 'стартове повідомлення нема'),
        ('гола назва ui-review-gate.sh → ✗', mk(good.replace('правила — CLAUDE.md', 'гачок `ui-review-gate.sh`')), 'голі назви'),
        ('мертвий lens/X.md → ✗', mk(good.replace('правила — CLAUDE.md', 'план `lens/X.md`')), 'мертві шляхи'),
        ('адреса без https:// (dash.cloudflare.com/…) — не шлях → тиша', mk(good.replace('правила — CLAUDE.md', 'посилання dash.cloudflare.com/?to=/:account/x')), None),
        ('мертвий шлях у «Коротко» плану → ✗', mk(good, {'lens/A.md': '## 0. Коротко\n- `lens/Gone.md`\n'}), 'мертві шляхи'),
        ('коміт агента після самері → ✗', mk(good, commit_after=True), 'самері відстає'),
        ('«цей коміт» у §0 → ⚠', mk(good.replace('- далі', '- цей коміт; далі')), '§0 має «цей коміт»'),
        ('нове самері ще не в коміті → бере його (без стартового → ✗)', mk(good, {'sessions/P_session_summary_Y.md': '## §0 В\n- `lens/A.md`\n'}, new_after=True), 'P_session_summary_Y'),
        ('незакомічена правка → ✗ «незакомічене»', mk(good, dirty=True), 'незакомічене'),
        ('код змінено в сесії, опис, що його згадує, — ні → ⚠ «описи»', mk(good, {'lens/B.md': 'запуск — `tools/run_me.sh`\n'}, code_after=True), 'описи, що згадують'),
        ('вузловий файл (згадують 6 описів) → ⓘ, не ⚠ на кожен', mk(good, {**{f'lens/H{i}.md': 'див. `tools/run_me.sh`\n' for i in range(6)}}, code_after=True), 'вузлові файли'),
        ('id черги в самері 3 сесій без брифу → ⚠ «кандидат у бриф»', mk(good, {'lens/P_CHERGA.md': '## Відкрите\n| `PX-1` | довгий пункт | 01.10 | x |\n', 'sessions/P_session_summary_A.md': '§1 PX-1 зроблено частину', 'sessions/P_session_summary_B.md': '§1 PX-1 ще частина', 'sessions/P_session_summary_C.md': '§1 PX-1 і знову'}), 'кандидат у бриф'),
        ('той самий пункт з «бриф не треба: …» у рядку черги → без «кандидат у бриф»', mk(good, {'lens/P_CHERGA.md': '## Відкрите\n| `PX-1` | довгий пункт; **бриф не треба:** два кроки без розвідки | 01.10 | x |\n', 'sessions/P_session_summary_A.md': '§1 PX-1 зроблено частину', 'sessions/P_session_summary_B.md': '§1 PX-1 ще частина', 'sessions/P_session_summary_C.md': '§1 PX-1 і знову'}), '!кандидат у бриф'),
        ('id з літерами (`AE-X`) у самері 2 сесій без брифу → ⚠ «кандидат» (BRIEF-2 5б)', mk(good, {'lens/P_CHERGA.md': '## Відкрите\n| `AE-X` | пункт | 01.10 | x |\n', 'sessions/P_session_summary_A.md': '§1 AE-X частина', 'sessions/P_session_summary_B.md': '§1 AE-X ще'}), 'кандидат у бриф'),
        ('чужий бриф лише згадує id у тілі → ⚠ «кандидат» усе одно', mk(good, {'lens/P_CHERGA.md': '## Відкрите\n| `AE-X` | пункт | 01.10 | x |\n', 'sessions/P_session_summary_A.md': '§1 AE-X частина', 'sessions/P_session_summary_B.md': '§1 AE-X ще', 'lens/AE-Y_brief.md': '# Y\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n- далі AE-X\n'}), 'кандидат у бриф'),
        ('бриф з id у назві → без «кандидат»', mk(good, {'lens/P_CHERGA.md': '## Відкрите\n| `AE-X` | пункт | 01.10 | x |\n', 'sessions/P_session_summary_A.md': '§1 AE-X частина', 'sessions/P_session_summary_B.md': '§1 AE-X ще', 'lens/AE-X_brief.md': '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'}), '!кандидат у бриф'),
        ('не-Lens: рядок черги > 2000 → ⚠ «час для брифу» (BRIEF-2 5в)', mk_nl(good_nl, '## Відкрите\n| `AE-W` | ' + 'x' * 2001 + ' | 18.10.2026 | y |\n'), 'час для брифу'),
        ('не-Lens: рядок черги ≤ 2000 → без «час для брифу»', mk_nl(good_nl), '!час для брифу'),
        ('старе й нове в одному коміті → бере пізніше створене', mk(good, {'sessions/P_session_summary_Y.md': '## §0 В\n- `lens/A.md`\n'}, new_after=True, both=True), 'P_session_summary_Y'),
        ('не-Lens: самері в docs/summary/ (P_SUMMARY_…) → тиша', mk_nl(good_nl), None),
        ('бриф без «§0 Коротко» → ✗ «не за шаблоном» (BRIEF-2)', mk(good, {'lens/X_brief.md': '# X\n## §0 Курс\n- щось\n'}), 'не за шаблоном'),
        ('бриф ядра без «§0 Коротко» → ✗, винятку kernel/ нема (BRIEF-2 крок 4)', mk(good, {'kernel/Lens_X_brief.md': '# X\n## §1 Навіщо\n'}), '✗:не за шаблоном'),
        ('бриф за шаблоном, код після нього з «бриф: без змін — …» → без «відстає»', mk(good, {'lens/X_brief.md': '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'}, code_after='бриф: без змін — інший пункт'), '!відстає'),
        ('бриф за шаблоном, код після нього → ⚠ «відстає» (BRIEF-2)', mk(good, {'lens/X_brief.md': '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'}, code_after=True), 'відстає'),
        ('не-Lens: самері без стартового → ✗', mk_nl(good_nl.split('## §6')[0]), 'стартове повідомлення нема'),
    ]
    bad = 0
    for name, r, want in cases:
        _, L = check_repo(r)
        strict = bool(want) and want.startswith('✗:'); want = want[2:] if strict else want   # «✗:…» — лише ✗, ⚠ не зараховується
        hit = [t for s, t in L if s in ('✗' if strict else '✗⚠')]
        ok = (not hit) if want is None else not any(want[1:] in t for t in hit) if want.startswith('!') else any(want in t for t in (hit if 'summary' not in want and 'вузлові' not in want else [t for _, t in L])) and not ('вузлові' in want and any('описи, що згадують' in t for t in hit))
        if want is None and not ok: print('   ', hit)
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    # журнал гачків: ядро поруч з продуктом (../lens-governance) — знаходить і бачить рядок сесії
    d = tempfile.mkdtemp(prefix='hj-'); prod = os.path.join(d, 'Prod'); os.makedirs(prod); jd = os.path.join(d, 'lens-governance/tools/claude-code/hooks'); os.makedirs(jd)
    os.environ['CLAUDE_CODE_SESSION_ID'] = 'hjtest' + str(os.getpid()); log = f"/tmp/lens-hooks-{os.environ['CLAUDE_CODE_SESSION_ID']}.tsv"
    open(log, 'w').write('2026-10-10T00:00:00Z\tprompt\thandoff-remind\tx\n')
    jcases = [('журнал ядра поруч з рядком сесії → ✓', '| 10.10 | `session_T` | x |\n', '✓'), ('журнал ядра поруч без рядка → ✗', '| 10.10 | `session_Z` | x |\n', '✗')]
    for name, body, want in jcases:
        open(os.path.join(jd, 'HOOK_JOURNAL.md'), 'w').write(body)
        got = hooks_journal([prod])[0][0]; ok = got == want
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    os.remove(log)
    # ріст журналу: свіжий і короткий → ✓; рядок 40 дн. → ⚠ ротація; довгий рядок → ⚠; дата «з майбутнього» = минулий рік
    import datetime as dt
    T0 = dt.date(2026, 10, 10); jf = os.path.join(jd, 'HOOK_JOURNAL.md')
    hcases = [('журнал: свіжі короткі рядки → ✓', '## §1\n| 10.10 | s | x | y | z |\n## §2\n', '✓', ''),
              ('журнал: рядок старший за 30 дн. → ⚠ ротація', '## §1\n| 31.08 | s | x | y | z |\n## §2\n', '⚠', 'ротація'),
              ('журнал: рядок довший за 700 знаків → ⚠ «деталь у коміт»', '## §1\n| 10.10 | s | ' + 'x' * 800 + ' |\n## §2\n', '⚠', 'деталь у коміт'),
              ('журнал: 20.12 при 10.10 — минулий рік (294 дн.) → ⚠', '## §1\n| 20.12 | s | x |\n## §2\n', '⚠', '294 дн.')]
    for name, body, want, part in hcases:
        open(jf, 'w').write(body); g, t = journal_health(jf, T0); ok = g == want and part in t
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    # лічильники журналу: число після слова, «×N», порядковий номер еволюції, «виправлено хибне» не рахується
    tf = tempfile.mkdtemp(prefix='jt-'); tp = os.path.join(tf, 'J.md')
    open(tp, 'w', encoding='utf-8').write('| 10.10 | s | `ui-guard` | **хибне 2** · справжнє 1 | x |\n| 11.10 | s | `ui-guard` | **виправлено хибне ×3** | x |\n'
                                          '| 11.10 | s | `ui_lint` | **еволюція 14** · пропуск Konst ×2 | x |\n| 12.10 | s | `env_check` | хибне 1: хибні 22 файли | x |\n| 13.10 | s | `ui_lint` + чек-лист очей | пропуск Konst | x |\n| 14.10 | s | `ui-guard` | вада: хибне 16.10 · справжніх нема | x |\n')
    tg = journal_tally([tp]); want = {'ui-guard': {'хибних': 3, 'справжніх': 1}, 'ui_lint': {'еволюцій': 1, 'пропусків Konst': 3}, 'env_check': {'хибних': 2}}
    tcases = [('лічильники журналу: «хибне 2», «×N», «еволюція 14» = 1, «виправлено» — ні, перевірка — перша в комірці, дата не число, «нема» = 0', all(dict(tg[k]) == v for k, v in want.items()))]
    for name, ok in tcases:
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    total = len(cases) + len(jcases) + len(hcases) + len(tcases)
    print(f'selftest: {total - bad}/{total}')
    return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__ or 'handoff_check.py <тека репо> … | selftest'); sys.exit(2)
    if a[0] == 'journal':   # рядок для env_check ядра: ріст журналу гачків щостарту
        g, t = journal_health(JPATH if len(a) < 2 else a[1]); print((g + ' ' if g == '⚠' else '') + t); sys.exit(0)
    if a[0] == 'tally':   # лічильники §0 журналу гачків з усіх рядків (живий §1 + journal/)
        jp = JPATH if len(a) < 2 else a[1]; ps = [jp] + sorted(glob.glob(os.path.join(os.path.dirname(jp), 'journal', '*.md')))
        t = journal_tally(ps); print('| перевірка | ' + ' | '.join(c for c, _, _ in T_COLS) + ' | точність |')
        prec = lambda r: f"{100 * r['справжніх'] // (r['справжніх'] + r['хибних'])} %" if r['справжніх'] + r['хибних'] else '—'   # справжні / (справжні + хибні) — на правило
        for k in sorted(t, key=lambda k: (k == 'інше', k)): print(f'| `{k}` | ' + ' | '.join(str(t[k][c]) for c, _, _ in T_COLS) + f' | {prec(t[k])} |')
        sys.exit(0)
    sys.exit(selftest() if a[0] == 'selftest' else report(a))
