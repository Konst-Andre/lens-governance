#!/usr/bin/env python3
# живе доки: пам'ять сесії — лише репо, і сесії переїжджають у нові чати (профіль Konst «САМЕРІ»).
# Перевірка пам'яті перед переїздом (HOOK-3.2, бриф — archive/summaries/Lens_gov/Lens_kernel_BRIEF_HOOK-3.2_closed.md; «так» Konst 09.10.2026, QR-Lens CC-5).
# Ловить машинно те, що новий агент не зможе знайти чи зрозуміти: самері без §0 / стартового, самері відстає від комітів,
# мертві й голі шляхи в §0 · стартовому · «Коротко» плану, історія в §0, гейт черги, README старіший за правила.
# Якість тексту НЕ судить — це робить агент за чек-листом гачка hooks/handoff-remind.sh.
#
# Запуск:  python3 tools/claude-code/handoff_check.py <тека репо> [<тека репо> …]    → рядки ✓ / ⚠ / ✗ / ⓘ; exit 1 на ✗
#          python3 tools/claude-code/handoff_check.py selftest                         → зуби: тимчасові репо, усі випадки брифу
#          python3 tools/claude-code/handoff_check.py revision [<корінь>] [--table]    → ревізія + печатка «ревізія ✓ · HEAD … · ✗ 0» (REV-1 · REV-4); --table — заготовка таблиці з git log
#          HC_INJECT=rev4 … selftest → ✗ (зуб REV-4: коміти без запису не бачить, печатку не звіряє)
# «Свої» коміти — за трейлером Claude-Session ≡ CLAUDE_CODE_REMOTE_SESSION_ID (cse_X ↔ session_X); нема змінної — усі коміти агента.
import glob, json, os, re, subprocess, sys, tempfile, time

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
    t = os.environ.get('LENS_KERNEL_TMP', '/tmp/lens-governance')   # AE S150: selftest вимикає — інакше фікстура продукту брала справжній клон env_check і ганяла Lens_validate (✗ Р-9 «усе гаразд»)
    if name.lower() in KERNEL_NAMES and os.path.isdir(t): return t
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


ID_RE = r'[A-Z][A-Z0-9]*-[A-Z0-9]+(?:\.\d+)?'
NOW_RE = re.compile(r'ЗАРАЗ|ПЕРШИЙ|ПЕРШИМ|першим кроком')

def absence(repo, text, s0, st, sm, qf, tail, L):
    """REV-5 Л1: (11) рішення сесії ⇒ черга чи бриф · (13) стартове не старше за §0 · (14) id відкритого пункту не був закритий · (15) §1 по порядку.
    (12) зображення Konst ⇒ файл у репо — рівень сесії, у report() (журнал сесії один на всі репо)."""
    qtxt = open(qf[0], encoding='utf-8').read() if qf else ''
    # (11) В-N, доданий комітами сесії, ⇒ згаданий у ЧЕРЗІ (Л1 як прийняв Konst 18.11: «рішення ⇒ рядок черги тієї ж сесії») або позначений
    #      виконаним (✅ у тексті рішення). Бриф і §0 — не дім: S155 В-408 · В-409 стояли в брифах і §0, а черга (її «ЧИННИЙ ПОРЯДОК») їх не знала —
    #      новий агент іде з черги. Повтор на AE 214c2f1: з брифом як домом діра ① мовчала.
    for dp in ('docs/DECISIONS.md', 'lens/DECISIONS.md'):
        fp = os.path.join(repo, dp)
        if not os.path.isfile(fp): continue
        if not tail: L.append(('ⓘ', '(11) рішення сесії ⇒ черга: не перевірено — нема ідентифікатора сесії')); continue
        added = sorted(set(re.findall(r'^\+- \*\*([ВB]-\d+)\*\*', git(repo, 'log', f'--grep=session_{tail}', '-p', '--format=', '--', dp), re.M)), key=lambda x: int(x[2:]))
        dtext = open(fp, encoding='utf-8').read()
        def entry(v):
            m = re.search(r'^- \*\*' + re.escape(v) + r'\*\*.*?(?=^- \*\*[ВB]-\d+\*\*|\Z)', dtext, re.M | re.S); return m.group(0) if m else ''
        lost = [v for v in added if entry(v) and '✅' not in entry(v) and not re.search(r'(?<![\w-])' + re.escape(v) + r'(?!\d)', qtxt)]
        if lost: L.append(('✗', f'(11) рішення сесії без рядка черги: {", ".join(lost)} — новий агент іде з черги (бриф і §0 — не дім); В-N у рядок пункту черги, або «✅ виконано» в самому рішенні'))
        elif added: L.append(('✓', f'(11) рішення сесії в черзі: {len(added)}'))
    # (13) стартове не старше за §0: (а) id із заголовка рядка §0 з «ЗАРАЗ / ПЕРШИЙ» — у стартовому; (б) §0 мінявся комітами сесії після
    #      останньої зміни стартового → ⚠ (тиша — «стартове: без змін» у коміті, як «бриф: без змін»)
    if s0 and st:
        need = sorted({i for ln in s0.splitlines() for head in [ln.split(':**', 1)[0] if ':**' in ln else ''] if NOW_RE.search(head)
                       for i in re.findall(r'(?<![\w-])' + ID_RE + r'(?![\w-])', head)})
        miss = [i for i in need if i not in st]
        if miss: L.append(('✗', f'(13) стартове мовчить про те, що §0 називає першим: {", ".join(miss)} — новий агент почне не з того'))
        if tail:
            n, seen_st = 0, False
            for c in git(repo, 'log', '--format=%H', f'--grep=session_{tail}', '--', sm).split():
                cur, prev = git(repo, 'show', f'{c}:{sm}'), git(repo, 'show', f'{c}^:{sm}')
                if (starter(cur) or '') != (starter(prev) or ''): seen_st = True; break
                if (section(cur, r'^## §0') or '') != (section(prev, r'^## §0') or '') and not re.search(r'стартове\s*:\s*без змін', git(repo, 'log', '-1', '--format=%B', c), re.I): n += 1
            if n and seen_st: L.append(('✗' if n >= 3 else '⚠', f'(13) стартове старше за §0 на {n} коміт(ів) сесії — перечитай його «як є» (або «стартове: без змін — чому» у коміті)'))
    # (14) id відкритого пункту вже був і закрився (S155: `REV-2` узято вдруге — новий агент знайшов закритий з тим самим id): історія файла черги —
    #      рядок `| `id` |` додано → прибрано → додано знову. git log -S рахує зміну ЧИСЛА входжень (правка рядка число не міняє); --pickaxe-regex —
    #      POSIX ERE, тому без \s (git-scm diffcore-pickaxe; baeldung.com/ops/git-commit-search-string, 18.11.2026)
    if qf:
        op = qtxt[qtxt.find('## Відкрите'):] if '## Відкрите' in qtxt else ''
        k = op.find('\n## ', 5); op = op[:k] if k > 0 else op
        rel = os.path.relpath(qf[0], repo)
        again = []
        for i in sorted(set(re.findall(r'(?m)^\|\s*\*{0,2}`(' + ID_RE + r')`', op))):
            hist = git(repo, 'log', '--format=%h', '--pickaxe-regex', '-S', r'\| *\*{0,2}`' + i.replace('.', r'\.') + r'`\*{0,2} *\|', '--', rel).split()
            if len(hist) >= 3: again.append(f'{i} ({len(hist)} змін)')
        if again: L.append(('✗', '(14) id відкритого пункту вже був закритий раніше — новий агент сплутає: ' + ' · '.join(again[:5]) + ' → наступний вільний id (повтор старої вади — назви його в рядку)'))
    # (15) рядки §1 по порядку (S155: «історія §1 не по порядку»)
    s1 = section(text, r'^## §1')
    if s1:
        nums = [int(m.group(1)) for m in re.finditer(r'(?m)^(\d+)\. ', s1)]
        br = next((f'{a} → {b}' for a, b in zip(nums, nums[1:]) if b <= a), None)
        if br: L.append(('✗', f'(15) §1 не по порядку: {br} — новий агент читає історію навпаки'))

def session_transcript():
    """Журнал сесії Claude Code: LENS_TRANSCRIPT або найсвіжіший ~/.claude/projects/*/*.jsonl (поточна сесія пише в нього просто зараз)."""
    p = os.environ.get('LENS_TRANSCRIPT')
    if p: return p if os.path.isfile(p) else None
    xs = glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl'))
    return max(xs, key=os.path.getmtime) if xs else None

IMG_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif')

def attachments(repos, tr=None):
    """(12) REV-5 Л1: зображення, які Konst прислав у чат (блок image у повідомленні user, не знімки інструментів), ⇒ стільки ж файлів-зображень
    у комітах сесії або рядок «не зберігаємо — <чому>» у самері (S155: концепти Konst жили лише в чаті). → (знак, текст) або None."""
    if os.environ.get('HC_INJECT') == 'rev5': return None   # зуб selftest
    tr = tr or session_transcript()
    if not tr or not os.path.isfile(tr): return ('ⓘ', '(12) вкладення Konst: не перевірено — журналу сесії нема')
    n = 0
    for ln in open(tr, encoding='utf-8', errors='replace'):
        if '"image"' not in ln: continue
        try: r = json.loads(ln)
        except ValueError: continue
        c = (r.get('message') or {}).get('content')
        if r.get('type') == 'user' and not r.get('isCompactSummary') and isinstance(c, list): n += sum(1 for x in c if isinstance(x, dict) and x.get('type') == 'image')
    if not n: return None
    tail = mine_tail()
    if not tail: return ('ⓘ', f'(12) вкладення Konst: {n} у чаті — не перевірено, чи в репо (нема ідентифікатора сесії)')
    saved = sum(1 for r in repos for f in git(r, 'log', f'--grep=session_{tail}', '--diff-filter=A', '--name-only', '--format=').split('\n') if f.lower().endswith(IMG_EXT))
    said = any(re.search(r'не зберігаємо', open(s, encoding='utf-8').read(), re.I) for s in filter(None, (latest_summary(r) for r in repos)))
    if saved >= n or said: return ('✓', f'(12) вкладення Konst: {n} у чаті · {saved} у репо' + (' · «не зберігаємо» у самері' if said else ''))
    return ('✗', f'(12) вкладення Konst лише в чаті: {n} зображень, у комітах сесії — {saved} → копія в репо (docs/shots/…) або рядок «не зберігаємо — чому» в самері')


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
    # (1-б) номер рішення двічі (AE S140: Fable і Opus паралельно в main взяли той самий В-348 — rebase злив обидва без конфлікту)
    for dp in ('docs/DECISIONS.md', 'lens/DECISIONS.md'):
        fp = os.path.join(repo, dp)
        if not os.path.isfile(fp): continue
        nums = re.findall(r'^- \*\*([ВB]-\d+)\*\*', open(fp, encoding='utf-8').read(), re.M)
        dup = sorted({x for x in nums if nums.count(x) > 1})
        if dup: L.append(('✗', f'{dp}: номер рішення двічі — {", ".join(dup)} (паралельні сесії взяли той самий; новіший → наступний вільний, посилання — теж)'))
    # (2) самері не відстає — логіка QR-Lens:tools/env_check.sh «самері відстає»
    last = git(repo, 'log', '-1', '--format=%H', '--', sm)
    tail = mine_tail()
    grep = f'session_{tail}' if tail else 'Claude-Session'
    after = git(repo, 'log', '--format=%h', f'--grep={grep}', f'{last}..HEAD') if last else ''
    if after:   # AE S145 (В-370): самері живе в main, код — на гілці; коміт гілки, названий у самері main (чи origin/main), — не відстає
        # AE S146: на гілці самері тієї ж назви — старе; у main нова сесія завела своє (`_s2`) → читати 3 найновіші самері теки з main, а не лише файл з назвою гілки
        def _main_sm(r):
            d = os.path.dirname(sm); fs = sorted(x for x in git(repo, 'ls-tree', '--name-only', r, '--', d + '/').split() if 'summary' in x.lower())
            return ''.join(git(repo, 'show', f'{r}:{f}') for f in (fs[-3:] or [sm]))
        ref = ''.join(_main_sm(r) for r in ('main', 'origin/main')) if git(repo, 'rev-parse', '--abbrev-ref', 'HEAD') != 'main' else ''
        cov = [h for h in after.split() if ref and h[:7] in ref]
        if cov: after = ' '.join(h for h in after.split() if h not in cov)
    n = len(after.split()) if after else 0
    owns = (not tail) or bool(git(repo, 'log', '--format=%h', f'--grep=session_{tail}', '--', os.path.dirname(sm) + '/'))   # тека самого самері, не вся sessions/: AE S139 — тека sessions/FAB-1/ давала хибне ✗ «самері ядра відстає»
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
        # REV-3 (AE S151, 16.11.2026; 💡 S147 «так, з підсиленням» Konst): «відстає» — лише коміти, що зачепили ПРЕДМЕТ брифу, не будь-який код репо
        #   (до того — 11 хибних ⚠ на кожній ревізії AE). Предмет: рядок шапки «стежить за: `шлях` · `тека/` · `ґлоб*`» → інакше шляхи в бектиках
        #   з §0 «Коротко», що існують у репо → інакше стара логіка з підказкою «додай «стежить за»». «стоїть до: дд.мм.рррр» у шапці — бриф свідомо
        #   стоїть: до дати мовчимо. Світ: `stale` (socket.dev/npm/package/@whenlabs/stale, 16.11.2026) — документ «відстає», коли файли, на які він
        #   посилається, мали коміти після нього; беремо мапу «документ → свої шляхи»; поріг віку (30 дн.) не беремо — у нас свіжість комітами.
        head = open(p, encoding='utf-8', errors='replace').read().split('\n## ', 1)[0]
        hold = re.search(r'стоїть до:\s*(\d{2})\.(\d{2})\.(\d{4})', head)
        if hold and time.strftime('%Y%m%d') <= hold.group(3) + hold.group(2) + hold.group(1): continue
        wl = re.search(r'(?m)стежить за:\s*(.+)$', head)
        subj = re.findall(r'`([^`:]+)`', wl.group(1).split(' — ')[0]) if wl else [x for x in re.findall(r'`([^`\s:]+/[^`\s:]*|[^`\s:/]+\.[a-z]{1,5})`', k) if os.path.exists(os.path.join(repo, x.rstrip('*')))]
        hit = lambda f: not subj or any(f == x or (x.endswith('/') and f.startswith(x)) or __import__('fnmatch').fnmatch(f, x) for x in subj)
        if last:
            n = sum(1 for c in git(repo, 'log', '--format=%H', f'{last}..HEAD').split() if any(f and not f.lower().endswith(NOT_CODE) and hit(f) for f in git(repo, 'show', '--name-only', '--format=', c).split('\n'))
                    and not re.search(r'бриф\s*:', git(repo, 'log', '-1', '--format=%B', c), re.I))   # «бриф: …» у коміті — брифи розглянуто свідомо (як brief-guard); AE S94: код BRIEF-2 робив «відсталим» бриф ARCH-1
            if n: L.append(('⚠', f'бриф {rel} відстає: {n} коміт(ів) ' + ('його предмета' if subj else 'коду (предмет не названо — додай у шапку «стежить за: `шлях`»)') + ' після його останньої правки — §0 «Коротко» і «Кроки» ще «як є»?'))
    # (10) черга ≡ брифи (Konst AE S151, 17.11.2026: «для кожного пункту черги вкажемо посилання на бриф… щоб такого більше не траплялося»).
    #      Урок: бриф AE-AI жив без свого пункту — шлях до нього стояв лише в чужих рядках (AE-SCN, «Відкладено»), і маршрут його не побачив.
    #      (а) бриф-сирота: id живого брифу (`<id>_brief.md`, у ядрі `Lens_<id>_brief.md`) не стоїть у першій клітинці рядка «Відкрите»
    #          і не є пунктом «Відкладено» (пункт починається з `id` або несе «бриф `шлях`») → ⚠; згадка шляху в чужому рядку — не власник;
    #      (б) рядок «Відкрите» без шляху до брифу (`…_brief.md`) → ⚠; «бриф не треба» — вже не відповідь (те саме слово Konst).
    if qf:
        qfull = open(qf[0], encoding='utf-8').read()
        def part(head):
            i = qfull.find(head)
            if i < 0: return ''
            j = qfull.find('\n## ', i + 1); return qfull[i:j if j > 0 else len(qfull)]
        op, dfr = part('## Відкрите'), part('## Відкладено')
        first = [m.group(1) for m in re.finditer(r'(?m)^\|([^|]*)\|', op)]
        own_open = set(re.findall(r'`([^`]+)`', ' '.join(first)))
        items = [l for l in dfr.splitlines() if l.startswith('- ')]
        orphan = []
        for b in sorted(glob.glob(os.path.join(repo, '**', '*_brief.md'), recursive=True)):
            rel = os.path.relpath(b, repo).replace(os.sep, '/')
            if rel.startswith('archive/') or '/archive/' in rel or 'templates/' in rel: continue
            bid = re.sub(r'^Lens_', '', os.path.basename(b)[:-len('_brief.md')])
            if bid in own_open: continue
            if any(re.match(r'^- \*{0,2}`' + re.escape(bid) + '`', l) or re.search(r'бриф\s+`[^`]*' + re.escape(os.path.basename(b)) + '`', l) for l in items): continue
            orphan.append(rel)
        if orphan: L.append(('⚠', 'бриф-сирота — живий бриф без свого пункту черги (рядок «Відкрите» з його id у першій клітинці або пункт «Відкладено»): ' + ' · '.join(orphan[:6]) + ' → рядок черги, або бриф закрито → archive/'))
        # AE S155 (Konst 18.11: «обери сам, що краще — нове чи старе»): бриф — за тригером CLAUDE.md ядра, не на кожен пункт (практика: тікета досить
        #   для малого й оборотного, документ — за розміром і ризиком; Google «Design Docs at Google», Polar handbook, 18.11.2026);
        #   «не загубитись» (В-397) тримає свій рядок «Відкрите» + «бриф-сирота»; тут — лише рядок > 2000 знаків без брифу (тригер «рядок черги > 2000»)
        nob = [m.group(1) for l in op.splitlines() for m in [re.match(r'^\|\s*\*{0,2}`([^`]+)`', l)] if m and len(l) > 2000 and not re.search(r'_brief\.md', l)]
        if nob: L.append(('⚠', 'рядок черги > 2000 знаків без брифу — час для брифу (тригер `CLAUDE.md` ядра): ' + ' · '.join(nob[:6]) + ' → tools/claude-code/templates/BRIEF_template.md'))
    # (11)–(15) REV-5 Л1 (Konst AE S155, 18.11.2026: «ревізія ✓, а купа дірок… ліки»): перевірки ВІДСУТНОСТІ. Корінь: (1)–(10) судять те, що є
    #   (шлях живий, самері не відстає), а діра S155 — те, чого нема (рішення без рядка черги, стартове старе, id уже був). Світ: «Handoff Debt»
    #   (arXiv 2606.02875, 06.2026; 18.11.2026) — передачу губить саме відсутнє: непояснені зміни й докази перевірки. HC_INJECT=rev5 вимикає — зуб selftest.
    if os.environ.get('HC_INJECT') != 'rev5':
        absence(repo, text, s0, st, sm, qf, tail, L)
    # (7) незбережене: контейнер скинеться — пропаде
    dirty = [x for x in subprocess.run(['git', '-C', repo, 'status', '--porcelain'], capture_output=True, text=True).stdout.split('\n') if x.strip()]
    if dirty: L.append(('✗', f'незакомічене: {len(dirty)} ({", ".join(x[3:] for x in dirty[:4])}) — коміт і push до переїзду'))
    if git(repo, 'remote'):
        if not git(repo, 'branch', '-r', '--contains', 'HEAD'): L.append(('✗', 'HEAD нема на жодній гілці GitHub — push до переїзду'))
        else:
            n_main = git(repo, 'rev-list', '--count', 'origin/main..HEAD')
            if n_main and n_main != '0': L.append(('ⓘ', f'у main нема {n_main} комітів (лише гілка сесії) — так задумано?'))
    return name, L


def hook_crashes(sid, path=None):
    """Падіння гачків цієї сесії: диспетчер пише stderr гачків у /tmp/lens-hook-errors-<сесія>.log, гачки друкують traceback замість тиші.
    Є «Traceback» → ✗ з останнім рядком помилки (виправити гачок + тест, рядок «пропуск» у журналі гачків)."""
    f = path or f'/tmp/lens-hook-errors-{sid}.log'
    if not os.path.isfile(f): return []
    t = open(f, encoding='utf-8', errors='replace').read()
    n = t.count('Traceback (most recent call last)')
    if not n: return []
    last = [l for l in t.splitlines() if re.match(r'^\w*(Error|Exception)\b', l)][-1:] or ['?']
    return [('✗', f'гачки падали {n} раз(и) — останнє: {last[0][:160]} → {f}; виправ гачок + тест, рядок «пропуск» у журналі гачків, тоді очисти файл')]

INFO_HOOKS = {'ctx-watch'}   # рядок лічильника контексту щоходу — інформація, вердикту не потребує (AE S144)

def hooks_journal(repos):
    """HOOK-5: спрацювання гачків цієї сесії (/tmp/lens-hooks-<сесія>.tsv, пише диспетчер) мають вердикти в журналі ядра."""
    sid = re.sub(r'[^A-Za-z0-9_-]', '', os.environ.get('CLAUDE_CODE_SESSION_ID', ''))
    log = f'/tmp/lens-hooks-{sid}.tsv' if sid else ''
    sta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hooks', 'selftest_all.py')   # AE S143: фоновий прогін усіх selftest зі старту
    red = subprocess.run([sys.executable, sta, 'report'], capture_output=True, text=True).stdout.splitlines() if os.path.isfile(sta) else []
    crash = [(l[0], 'selftest: ' + l[2:]) for l in red if l[:1] in '✗⚠'] + hook_crashes(sid)   # ⚠ — плаваючий тест   # AE S143: впалий гачок мовчить — без цього рядка падіння виглядає як «нема що сказати»
    if not log or not os.path.isfile(log): return crash + [('ⓘ', 'журнал гачків: спрацювань цієї сесії не записано (лог диспетчера порожній)')]
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
    # AE S144: раніше один рядок сесії давав ✓ усім гачкам — handoff-remind ×2 після першого запису пройшов без вердикту.
    # Тепер кожен гачок, що спрацював, має бути названий у рядку цієї сесії; INFO_HOOKS — лічильники, не рішення.
    key = 'session_' + tail[:8] if tail else None
    mine = [l for l in open(k, encoding='utf-8').read().splitlines() if key and key in l]
    miss = [h for h in sorted(by) if h not in INFO_HOOKS and not any(h in l for l in mine)]
    if not miss: return crash + [('✓', msg + ' — вердикти в журналі гачків є')]
    if mine: return crash + [('✗', msg + f' — без вердикту: {", ".join(miss)} (рядки сесії `{key}` є, але цих гачків не названо) — дописати в tools/claude-code/hooks/HOOK_JOURNAL.md §1')]
    return crash + [('✗', msg + f' — вердиктів нема: розібрати (справжнє · хибне · дубль · пропуск) у tools/claude-code/hooks/HOOK_JOURNAL.md §1, ідентифікатор `session_{tail[:8] if tail else "?"}`; хибне чи пропуск — виправити гачок + тест')]

# Ріст журналу (Konst 10.10: «хто контролює, наскільки виріс файл?»): §1 — лише живі рядки (≤ 30 дн.), рядок — коротко (деталь — у коміті),
# файл ≤ 24 КБ (читається точково, але §0 + свіжий §1 — за один погляд). Старше → ротація в теку journal/ поруч, лічильники — у §0.
J_AGE, J_KB, J_ROW = 30, 24, 700
def journal_health(k, today=None):
    import datetime as dt
    today = today or dt.date.today()
    txt = open(k, encoding='utf-8').read()
    body = txt.split('## §1', 1)[1].split('\n## ', 1)[0] if '## §1' in txt else ''
    rows = [l for l in body.splitlines() if re.match(r'^\| \d\d\.\d\d(?:\.\d{4})? \|', l)]   # AE S130: рядки пишуться «| 06.11.2026 |» — без року в шаблоні лічба була 0
    ages = []
    for l in rows:
        d, m = map(int, re.match(r'^\| (\d\d)\.(\d\d)', l).groups())
        x = dt.date(today.year, m, d)
        if (x - today).days > 2: x = dt.date(today.year - 1, m, d)   # AE S145: рядок за київською датою на день попереду контейнера UTC — не «минулий рік» (було 364 дн.)
        elif x > today: x = today
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
    a = attachments([os.path.abspath(r) for r in repos])
    if a: print('— сесія'); print(f'  {a[0]} {a[1]}'); bad |= a[0] == '✗'
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
JPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hooks', 'HOOK_JOURNAL.md')   # AE S143: відносний шлях падав поза коренем ядра

# REV-1 (AE S143, В-361, Konst: «твоя ревізія повинна працювати так, як моя»): ОДНА точка ревізії для всіх тригерів —
#   слово Konst (hooks/handoff-remind.sh) · поріг контексту (hooks/ctx_watch.py, і вночі — після коміту) · сам агент перед «можна /compact».
#   `revision` — репо сесії → повний прохід + чек-лист «що з сесії ще не має дому» + мітка REV_MARK (її вимагає hooks/precompact_guard.sh для ручного /compact;
#   знімає ctx_watch після стиснення). `gate` — лише ✗ рядки, exit 1 на ✗ (для сторожа стиснення), мітки не пише.
CHECKLIST = ("Ревізія — без переїзду: ✗ — виправ, закоміть і запуш; ⚠ — звір. Потім пройди сесію (git log з її початку) і для КОЖНОГО: рішення Konst чи агента → `DECISIONS` (В-N) або бриф; "
             "новий прилад → карта репо (REPO_LAYOUT) + «Прилади продуктів» ядра; нове правило → CLAUDE.md / профіль / рецепт; зміна стану → брифи §0 і черга; урок → свій дім + рядок у самері; "
             "💡 без відповіді → самері §0 «💡 чекає вироку Konst». Звіт Konst — таблиця «що · дім · коміт» (заготовка — handoff_check.py revision --table, з git log) і «чого ще нема». "
             "Іспит нового агента (REV-5 Л2) — `python3 <ядро>/tools/claude-code/handoff_exam.py run` на фінальному HEAD (модель · effort · навіщо — у чат до запуску): звір кожну відповідь таблицею «питання · відповідь · правда з репо · ✓/✗», виправ, закоміть, повтори; печатка «ревізія ✓» — лише з іспитом на HEAD і «незрозуміло 0». "
             "З пам'яті сесії ревізія не робиться — лише з цього виводу. Правив самері чи стартове після цього прогону — revision ще раз: печатка нижче старіє з HEAD; "
             "у звіті — її рядок як є, не «ревізія ✓» своїми словами (гачок promise-guard зупинить).")

def sid():
    return re.sub(r'\W', '', os.environ.get('CLAUDE_CODE_SESSION_ID') or os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID') or 'x')

def rev_mark(): return os.environ.get('LENS_REV_MARK') or f'/tmp/lens-revision-{sid()}'

def session_repos(root='/home/user'):
    """Репо сесії — як hooks/handoff-remind.sh: є sessions/ чи docs/summary, без .git/lens-readonly."""
    out = []
    for d in sorted(glob.glob(os.path.join(root, '*', '.git'))):
        r = os.path.dirname(d)
        if os.path.exists(os.path.join(d, 'lens-readonly')): continue
        if any(os.path.isdir(os.path.join(r, x)) for x in ('sessions', 'docs/summary')): out.append(r)
    return out

def heads(rs): return ' '.join(git(r, 'rev-parse', 'HEAD') for r in rs)

# REV-4 (AE S148, Konst: «чому ревізія наче зроблена, а потім знайшлись мертві шляхи й помилки?»): одна перевірка для revision і гачка Stop REV-2
#   (hooks/handoff-remind.sh імпортує ці функції — копії нема) · печатка на HEAD замість слова агента · таблиця з git log, не з пам'яті.
#   Практика: Stop-гачок звіряє заяву з файлом стану, який пише сама перевірка (codingwithroby «The Stop Hook That Won't Let Claude Lie to You»;
#   ctxgrd «Verifying agent work», 15.11.2026); суд моделлю — не беремо (дорого, не вимірне).
SUMF = re.compile(r'(^docs/summary/|^sessions/.*summary)', re.I)

def latest_summary(r):
    """Найновіше самері репо за часом зміни: не-Lens — docs/summary/*SUMMARY*.md, Lens — sessions/**/*summary*.md."""
    xs = glob.glob(os.path.join(r, 'docs', 'summary', '*SUMMARY*.md')) + glob.glob(os.path.join(r, 'sessions', '**', '*summary*.md'), recursive=True)
    return max(xs, key=os.path.getmtime) if xs else None

def session_log(r):
    """Коміти цієї сесії (трейлер Claude-Session ≡ CLAUDE_CODE_REMOTE_SESSION_ID), новіші першими: [(h7, тема, правив самері)]."""
    s = os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID', ''); tail = s.split('_', 1)[1] if '_' in s else ''
    if not tail: return []
    out = []
    for ln in git(r, 'log', '--format=%h\x1f%s', '--abbrev=7', f'--grep=session_{tail}').splitlines():
        h, subj = ln.split('\x1f', 1)
        out.append((h, subj, any(SUMF.search(f) for f in git(r, 'show', '--name-only', '--format=', h).split())))
    return out

def uncovered_commits(rs, text=''):
    """Коміти сесії, яких нема ні в text (відповідь агента), ні в найновішому самері жодного репо сесії. Коміт, що правив самері, — записаний
    ним самим (свій хеш у самері вписати не може). → ['репо h7', …]"""
    if os.environ.get('HC_INJECT') == 'rev4': return []
    mem = text + ''.join(open(f, encoding='utf-8').read() for f in filter(None, (latest_summary(r) for r in rs)))
    return [f'{os.path.basename(r)} {h}' for r in rs for h, _, s in session_log(r) if not s and h not in mem]

def exam_state(rs):
    """REV-5 Л2 → Л3: стан іспиту нового агента (handoff_exam.py) на поточному HEAD: (на_HEAD, K, рядок)."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import handoff_exam
        return handoff_exam.state(rs)
    except Exception as e: return False, None, f'іспит: стан не прочитано ({type(e).__name__})'

def seal(rs, n_bad, n_checks=None, n_unver=0):
    """Печатка ревізії: агент цитує її, а не пише «ревізія ✓» сам; стара з першим новим комітом будь-якого репо сесії.
    REV-5 Л3 (Konst AE S155: «був 100 % впевнений… а тут купа дірок»): печатка каже, ЩО перевірено, — «ревізія ✓» лише коли машина ✗ 0
    І іспит нового агента на цьому HEAD без незрозумілого; інакше «ревізія ⚠ · … · іспит не робився / незрозуміло K» — звучить як є, не як «повно».
    «не перевірено M» — окрема категорія, не «пройдено» (практика Linaro LAVA: пропущене — свій статус, бракує очікуваного — провал; 18.11.2026)."""
    on, k, ex = exam_state(rs)
    word = '✗' if n_bad else ('✓' if on and k == 0 else '⚠')
    return (f"ревізія {word} · HEAD " + ' '.join(f'{os.path.basename(r)}@{git(r, "rev-parse", "--short=7", "HEAD")}' for r in rs) + f' · ✗ {n_bad}'
            + (f' · машина: {n_checks} перевірок' if n_checks is not None else '') + (f' · не перевірено {n_unver}' if n_unver else '') + f' · {ex}')

def stored_seal(rs):
    """Печатка з мітки ревізії, якщо мітка — на поточному HEAD усіх репо сесії; інакше None."""
    try: ls = open(rev_mark(), encoding='utf-8').read().splitlines()
    except OSError: return None
    return ls[1] if len(ls) > 1 and ls[0].split(' ', 1)[-1] == heads(rs) else None

def seal_ok(rs):
    """Мітка ревізії несе «ревізія ✓» саме на поточному HEAD усіх репо сесії (її пише лише revision), і іспит досі на цьому HEAD без незрозумілого."""
    if os.environ.get('HC_INJECT') == 'rev4': return True
    s = stored_seal(rs)
    if not s or not s.startswith('ревізія ✓'): return False
    on, k, _ = exam_state(rs)
    return bool(on and k == 0)

def rev_table(rs):
    """`revision --table`: таблиця ревізії з git log сесії (що · коміт); «дім» дописує агент."""
    rows = [f"| {subj[:90].replace('|', '/')} | ? | {os.path.basename(r)} `{h}` |" for r in rs for h, subj, _ in reversed(session_log(r))]
    return '| що | дім | коміт |\n|---|---|---|\n' + ('\n'.join(rows) if rows else '| (комітів сесії нема) | — | — |')

def revision(root='/home/user', once=None):
    """→ (текст, є ✗). once — файл-позначка: той самий HEAD усіх репо, що й минулого разу → ('', False) (повтор не шумить)."""
    import contextlib, io
    rs = session_repos(root)
    if not rs: return '', False
    h = heads(rs)
    if once and os.path.exists(once) and open(once).read() == h: return '', False
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): bad = report(rs)
    txt = buf.getvalue().strip()
    miss = uncovered_commits(rs)   # REV-4 (а): те саме, що судить гачок Stop REV-2 на переїзді
    if miss: txt += (f'\n  ✗ коміти сесії без запису в самері — {len(miss)}: ' + ' · '.join(miss[:10]) + (' …' if len(miss) > 10 else '')
                     + ' → рядком §1 самері (що · дім · коміт)')
    ls_ = [l.strip() for l in txt.splitlines()]
    s = seal(rs, sum(1 for l in ls_ if l.startswith('✗')), sum(1 for l in ls_ if l[:1] in '✓⚠✗ⓘ'), sum(1 for l in ls_ if l.startswith('ⓘ') and 'не перевірено' in l))
    open(rev_mark(), 'w').write(f'{int(time.time())} {h}\n{s}')   # precompact_guard дивиться лише, чи мітка є; другий рядок — для promise-guard ④
    if once: open(once, 'w').write(h)
    return txt + '\n\n' + CHECKLIST + '\n\n' + s, bool(bad or miss)

def gate(root='/home/user'):
    import contextlib, io
    rs = session_repos(root); buf = io.StringIO()
    with contextlib.redirect_stdout(buf): report(rs) if rs else 0
    return [l.strip() for l in buf.getvalue().splitlines() if l.strip().startswith('✗')]



# (9) «код» для свіжості брифу — усе, крім документів і даних (AE S120, кандидат журналу гачків S119: коміти даних Олі з редактора й робота АНЦ —
#     .json · фото — робили брифи «відсталими» без жодної зміни коду). Перелік — що НЕ код: невідоме розширення лишається кодом (сліпої плями нема).
NOT_CODE = ('.md', '.json', '.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.avif', '.csv', '.tsv', '.txt', '.xlsx', '.pdf')


def selftest():
    os.environ['LENS_KERNEL_TMP'] = os.path.join(tempfile.gettempdir(), 'hc-no-kernel-clone')   # фікстури не бачать /tmp/lens-governance контейнера
    _e = tempfile.mkstemp(suffix='.jsonl')[1]; os.environ['LENS_TRANSCRIPT'] = _e   # REV-5 (12): фікстури не бачать справжній журнал сесії (у ньому зображення Konst)
    def sh(d, *c): subprocess.run(c, cwd=d, check=True, capture_output=True)
    def mk(summary, extra=None, commit_after=False, new_after=False, both=False, dirty=False, code_after=False, data_after=False):
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
        if data_after:   # AE S120: коміт лише даних (редактор / робот) — не «код» для свіжості брифу
            os.makedirs(os.path.join(r, 'site/data'), exist_ok=True); os.makedirs(os.path.join(r, 'site/anc/img'), exist_ok=True)
            open(os.path.join(r, 'site/data/catalog.json'), 'w').write('{}'); open(os.path.join(r, 'site/anc/img/a.webp'), 'w').write('x')
            sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'дані з редактора: site/data/catalog.json')
        if dirty: open(os.path.join(r, 'lens/A.md'), 'a').write('z')
        if commit_after:
            open(os.path.join(r, 'lens/A.md'), 'a').write('y'); sh(r, 'git', 'commit', '-qam', 'код\n\nClaude-Session: https://claude.ai/code/session_T')
        return r
    def mk_nl(summary, q='## Відкрите\n| `AE-W` | x — бриф `docs/briefs/AE-W_brief.md` | 18.10.2026 | y |\n'):   # не-Lens каркас (AE): самері docs/summary/<P>_SUMMARY_<дата>.md, черга docs/CHERGA.md
        d = tempfile.mkdtemp(prefix='hc-'); r = os.path.join(d, 'Prod'); os.makedirs(os.path.join(r, 'docs/summary'))
        sh(r, 'git', 'init', '-q'); sh(r, 'git', 'config', 'user.email', 't@t'); sh(r, 'git', 'config', 'user.name', 't')
        open(os.path.join(r, 'docs/CHERGA.md'), 'w').write(q); open(os.path.join(r, 'CLAUDE.md'), 'w').write('x')
        open(os.path.join(r, 'docs/summary/P_SUMMARY_2026-10-18.md'), 'w').write(summary)
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'самері\n\nClaude-Session: https://claude.ai/code/session_T')
        return r
    Q10 = '## Відкрите\n| `AE-W` | x — бриф `docs/briefs/AE-W_brief.md` | 18.10.2026 | y |\n'
    def mk_q(q):   # (10): не-Lens каркас + бриф AE-X за шаблоном
        r = mk_nl(good_nl, q); os.makedirs(os.path.join(r, 'docs/briefs'))
        open(os.path.join(r, 'docs/briefs/AE-X_brief.md'), 'w').write('# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n')
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'бриф\n\nClaude-Session: https://claude.ai/code/session_T'); return r
    def mk_br(named, new=False):   # AE S145 (В-370): самері — у main, код — на гілці claude/x; коміт гілки названо (чи ні) у самері main; new — у новому самері main (`_s2`, AE S146)
        r = mk_nl(good_nl); sh(r, 'git', 'branch', '-M', 'main'); sh(r, 'git', 'checkout', '-qb', 'claude/x')
        open(os.path.join(r, 'code.txt'), 'w').write('1'); sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'код\n\nClaude-Session: https://claude.ai/code/session_T')
        h = subprocess.run(['git', '-C', r, 'rev-parse', '--short=7', 'HEAD'], capture_output=True, text=True).stdout.strip()
        sh(r, 'git', 'checkout', '-q', 'main'); open(os.path.join(r, 'docs/summary/P_SUMMARY_2026-10-18' + ('_s2' if new else '') + '.md'), 'a').write(f'\n- код гілки `{h if named else "0000000"}`\n')
        if new: sh(r, 'git', 'add', '-A')
        sh(r, 'git', 'commit', '-qam', 'самері\n\nClaude-Session: https://claude.ai/code/session_T'); sh(r, 'git', 'checkout', '-q', 'claude/x')
        return r
    def mk_k():   # ядро: самері в sessions/Lens_gov/ від сесії ядра; сесія продукту комітить робочу теку sessions/FAB-1/ (AE S139)
        d = tempfile.mkdtemp(prefix='hc-'); r = os.path.join(d, 'lens-governance'); os.makedirs(os.path.join(r, 'sessions/Lens_gov')); os.makedirs(os.path.join(r, 'kernel'))
        sh(r, 'git', 'init', '-q'); sh(r, 'git', 'config', 'user.email', 't@t'); sh(r, 'git', 'config', 'user.name', 't')
        open(os.path.join(r, 'CLAUDE.md'), 'w').write('x'); open(os.path.join(r, 'kernel/K.md'), 'w').write('x')
        open(os.path.join(r, 'sessions/Lens_gov/Lens_governance_session_summary_X.md'), 'w').write('# S\n## §0 ВІДКРИТЕ\n- далі\n## Стартове\n```text\nСтарт\n```\n')
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'самері\n\nClaude-Session: https://claude.ai/code/session_OLD')
        os.makedirs(os.path.join(r, 'sessions/FAB-1')); open(os.path.join(r, 'sessions/FAB-1/FAB-1_README.md'), 'w').write('x')
        sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'тека\n\nClaude-Session: https://claude.ai/code/session_T')
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
        ('номер рішення двічі (В-348 ×2, AE S140) → ✗', mk(good, {'lens/DECISIONS.md': '- **В-348** · a\n- **В-348** · b\n- **В-347** · c\n'}), 'номер рішення двічі'),
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
        ('REV-3: «стежить за: `site/` — пояснення `tools/`», код лише в tools/ → без «відстає» (шлях після « — » — не предмет)', mk(good, {'lens/X_brief.md': '# X\n> стежить за: `site/` · `worker/*.js` — пояснення, а не предмет: `tools/`\n' + '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'[4:]}, code_after=True), '!відстає'),
        ('REV-3: «стежить за: `tools/`», код у tools/ → ⚠ «відстає» «його предмета» (зуб)', mk(good, {'lens/X_brief.md': '# X\n> стежить за: `tools/`\n' + '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'[4:]}, code_after=True), 'відстає: 1 коміт(ів) його предмета'),
        ('REV-3: без рядка — шлях з §0 `lens/A.md`, код у tools/ → без «відстає»', mk(good, {'lens/X_brief.md': '# X\n## §0 Коротко\n- **Стан:** a · `lens/A.md`\n- **Далі:** b\n- **Чекає Konst:** c\n'}, code_after=True), '!відстає'),
        ('REV-3: «стоїть до: 31.12.2099» → тиша до дати', mk(good, {'lens/X_brief.md': '# X\n> стоїть до: 31.12.2099\n' + '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'[4:]}, code_after=True), '!відстає'),
        ('REV-3: «стоїть до: 01.01.2020» (минуло) → ⚠ «відстає» (зуб)', mk(good, {'lens/X_brief.md': '# X\n> стоїть до: 01.01.2020\n' + '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'[4:]}, code_after=True), 'відстає'),
        ('бриф за шаблоном, після нього лише коміт даних (.json · фото) → без «відстає» (AE S120)', mk(good, {'lens/X_brief.md': '# X\n## §0 Коротко\n- **Стан:** a\n- **Далі:** b\n- **Чекає Konst:** c\n'}, data_after=True), '!відстає'),
        ('не-Lens: самері без стартового → ✗', mk_nl(good_nl.split('## §6')[0]), 'стартове повідомлення нема'),
        ('гілка: коміт коду названо в самері main → не відстає (AE S145, В-370)', mk_br(True), '!самері відстає'),
        ('гілка: коміт коду НЕ названо в самері main → ✗ відстає (зуб)', mk_br(False), 'самері відстає'),
        ('гілка: коміт коду названо в НОВОМУ самері main (`_s2`), на гілці — старе → не відстає (AE S146, хибне ✗ блокувало /compact)', mk_br(True, True), '!самері відстає'),
        ('ядро: коміт сесії продукту в sessions/FAB-1/, самері — sessions/Lens_gov/ → ⓘ, не ✗ «відстає» (хибне AE S139)', mk_k(), '!самері відстає'),
        # (10) черга ≡ брифи (AE S151): фікстура — черга + бриф docs/briefs/AE-X_brief.md за шаблоном
        ('(10) бриф без свого рядка, шлях лише в чужому рядку → ⚠ бриф-сирота (зуб, урок AE-AI)', mk_q(Q10 + '| `AE-W` | x, див. `docs/briefs/AE-X_brief.md` | 18.10.2026 | y |\n'), 'бриф-сирота'),
        ('(10) id брифу в першій клітинці рядка «Відкрите» → без «сирота»', mk_q(Q10 + '| `AE-W` · `AE-X` | x | 18.10.2026 | y |\n'), '!бриф-сирота'),
        ('(10) пункт «Відкладено» з «бриф `шлях`» → без «сирота»', mk_q(Q10 + '\n## Відкладено свідомо\n- **довідник** — бриф `docs/briefs/AE-X_brief.md`\n'), '!бриф-сирота'),
        ('(10) «Відкладено» лише згадує шлях (без «бриф») → ⚠ бриф-сирота (зуб)', mk_q(Q10 + '\n## Відкладено свідомо\n- **щось** (крок 1, `docs/briefs/AE-X_brief.md`)\n'), 'бриф-сирота'),
        ('(10) рядок «Відкрите» > 2000 знаків без шляху брифу → ⚠ «час для брифу» (зуб)', mk_nl(good_nl, '## Відкрите\n| `AE-W` | ' + 'x' * 2100 + ' | 18.10.2026 | y |\n'), 'без брифу — час для брифу'),
        ('(10) короткий рядок без брифу → тиша (AE S155: бриф за тригером, не на кожен пункт)', mk_nl(good_nl, '## Відкрите\n| `AE-W` | x | 18.10.2026 | y |\n'), '!без брифу'),
        ('(10) рядок «Відкрите» зі шляхом брифу → без «без брифу»', mk_nl(good_nl), '!без брифу'),
    ]
    # REV-5 Л1 (11)(13)(14)(15): діри AE S155 — кожна мусить дати ✗ (13б — ⚠); чиста фікстура — тиша (справа вгорі: mk_nl(good_nl))
    def mk5(summary=None, q=Q10, dec=None, steps=()):
        r = mk_nl(summary or good_nl, q)
        if dec is not None:   # В-1 — від попередньої сесії, В-2 — додано цією
            open(os.path.join(r, 'docs/DECISIONS.md'), 'w').write(dec.split('\n', 1)[1]); sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', 'старе\n\nClaude-Session: https://claude.ai/code/session_OLD')
            open(os.path.join(r, 'docs/DECISIONS.md'), 'w').write(dec); sh(r, 'git', 'commit', '-qam', 'рішення\n\nClaude-Session: https://claude.ai/code/session_T')
        for path, body, msg in steps:
            fp = os.path.join(r, path); os.makedirs(os.path.dirname(fp), exist_ok=True); open(fp, 'w').write(body)
            sh(r, 'git', 'add', '-A'); sh(r, 'git', 'commit', '-qm', msg + '\n\nClaude-Session: https://claude.ai/code/session_T')
        return r
    S5 = lambda s0, st='Старт: docs/CHERGA.md', s1='': f'# S\n## §0 ВІДКРИТЕ\n{s0}\n## §1 ХОДИ\n{s1}\n## §6 Стартове\n```text\n{st}\n```\n'
    SM = 'docs/summary/P_SUMMARY_2026-10-18.md'
    D5 = '- **В-2** · **нове рішення** про екран\n- **В-1** · старе\n'
    cases += [
        ('(11) S155 ①: рішення сесії (В-2) без рядка черги й брифу, лише в §0 → ✗', mk5(S5('- **0.1 · В-2:** далі'), dec=D5), '(11) рішення сесії без рядка черги'),
        ('(11) рішення сесії названо в черзі → тиша', mk5(q=Q10 + '| `AE-Q` | за В-2 | 18.10.2026 | y |\n', dec=D5), '!(11)'),
        ('(11) рішення сесії з «✅ виконано» → тиша', mk5(dec=D5.replace('про екран', 'про екран ✅ виконано `abc1234`')), '!(11)'),
        ('(13а) S155 ③/⑤: §0 «ЗАРАЗ» називає AE-W, стартове — ні → ✗', mk5(S5('- **0.1 · AE-W — ЗАРАЗ:** крок 2')), '(13) стартове мовчить'),
        ('(13а) стартове називає AE-W → тиша', mk5(S5('- **0.1 · AE-W — ЗАРАЗ:** крок 2', 'Старт: AE-W крок 2; docs/CHERGA.md')), '!(13) стартове мовчить'),
        ('(13б) S155 ③: §0 змінено 2 комітами після стартового → ⚠ «старше за §0 на 2»', mk5(steps=[(SM, S5('- a'), 'с1'), (SM, S5('- b'), 'с2'), (SM, S5('- c'), 'с3')]), 'старше за §0 на 2'),
        ('(13б) S155 ③ (повтор на AE 6c0a4db — 12 комітів): §0 змінено 3 комітами після стартового → ✗, не лише ⚠', mk5(steps=[(SM, S5('- a'), 'с1'), (SM, S5('- b'), 'с2'), (SM, S5('- c'), 'с3'), (SM, S5('- d'), 'с4')]), '✗:старше за §0 на 3'),
        ('(13б) ті самі коміти з «стартове: без змін — …» → тиша', mk5(steps=[(SM, S5('- a'), 'с1'), (SM, S5('- b'), 'с2 стартове: без змін — дрібне'), (SM, S5('- c'), 'с3 стартове: без змін — дрібне')]), '!старше за §0'),
        ('(14) S155 ④: id `AE-Q` додано → закрито → узято знову → ✗', mk5(steps=[('docs/CHERGA.md', Q10 + '| `AE-Q` | перше | 1 | y |\n', 'додав'), ('docs/CHERGA.md', Q10, 'закрив'), ('docs/CHERGA.md', Q10 + '| `AE-Q` | інше | 2 | y |\n', 'знову')]), '(14) id відкритого пункту'),
        ('(14) рядок `AE-Q` лише правився (число входжень те саме) → тиша', mk5(steps=[('docs/CHERGA.md', Q10 + '| `AE-Q` | перше | 1 | y |\n', 'додав'), ('docs/CHERGA.md', Q10 + '| `AE-Q` | правка | 1 | y |\n', 'правка'), ('docs/CHERGA.md', Q10 + '| `AE-Q` | ще | 1 | y |\n', 'ще')]), '!(14)'),
        ('(15) S155 ⑦: §1 «1 · 3 · 2» → ✗', mk5(S5('- a', s1='1. перший\n3. третій\n2. другий')), '(15) §1 не по порядку'),
        ('(15) §1 по порядку → тиша', mk5(S5('- a', s1='1. перший\n2. другий\n3. третій')), '!(15)'),
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
    jcases = [('журнал ядра поруч з рядком сесії → ✓', '| 10.10 | `session_T` | `handoff-remind` | x |\n', '✓', 'handoff-remind'),
              ('журнал ядра поруч без рядка → ✗', '| 10.10 | `session_Z` | x |\n', '✗', 'handoff-remind'),
              ('рядок сесії є, але гачка в ньому нема → ✗ (дірка AE S144)', '| 10.10 | `session_T` | `env-remind` | x |\n', '✗', 'handoff-remind\nx\tprompt\tenv-remind'),
              ('спрацював лише ctx-watch → ✓ без рядка', '| 10.10 | `session_Z` | x |\n', '✓', 'ctx-watch')]
    for name, body, want, hooks in jcases:
        open(log, 'w').write(''.join(f'2026-10-10T00:00:00Z\tprompt\t{h.split(chr(9))[-1]}\tx\n' for h in hooks.split('\n')))
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
              ('журнал: 20.12 при 10.10 — минулий рік (294 дн.) → ⚠', '## §1\n| 20.12 | s | x |\n## §2\n', '⚠', '294 дн.'),
              ('журнал: 11.10 при 10.10 (Київ попереду UTC) — сьогодні, не минулий рік → ✓', '## §1\n| 11.10.2026 | s | x | y | z |\n## §2\n', '✓', '0 дн.')]
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
    # REV-1: одна точка ревізії — revision (вивід + чек-лист + мітка, повтор на тому самому HEAD — тиша) · gate (лише ✗) · клон лише для читання — не репо сесії
    os.environ['LENS_REV_MARK'] = os.path.join(tf, 'rev'); rg = os.path.dirname(mk(good)); rd = os.path.dirname(mk(good, dirty=True)); once = os.path.join(tf, 'once')
    t1, _ = revision(rg, once); t2, _ = revision(rg, once)
    ro = os.path.dirname(mk(good, dirty=True)); open(os.path.join(ro, 'Prod', '.git', 'lens-readonly'), 'w').close()
    rcases = [('revision: повний вивід + чек-лист «що без дому» + мітка для сторожа стиснення', 'Звіт Konst — таблиця' in t1 and '— Prod' in t1 and os.path.exists(os.environ['LENS_REV_MARK'])),
              ('revision: той самий HEAD удруге (once) → тиша', t2 == ''),
              ('gate: незакомічене → ✗; чисте → нічого', any('незакомічене' in x for x in gate(rd)) and not any('незакомічене' in x for x in gate(rg))),
              ('gate: клон лише для читання (.git/lens-readonly) не судиться', gate(ro) == [])]
    ef = os.path.join(rg, 'err.log'); open(ef, 'w').write('DeprecationWarning: x\n')
    c0 = hook_crashes('x', ef); open(ef, 'a').write('Traceback (most recent call last):\n  File "h"\nKeyError: \'tool_input\'\n'); c1 = hook_crashes('x', ef)
    rcases.append(('гачок впав (Traceback у журналі помилок) → ✗ з KeyError; лише попередження → тиша (AE S143)', c0 == [] and c1 and c1[0][0] == '✗' and 'KeyError' in c1[0][1]))
    # REV-4: коміт сесії без запису в самері → ✗ і печатка ✗ · записав → печатка ✓ у мітці · новий коміт → печатка стара · таблиця з git log
    os.environ['LENS_REV_MARK'] = os.path.join(tf, 'rev4'); r4 = mk(good, commit_after=True); g4 = os.path.dirname(r4)
    h4 = git(r4, 'rev-parse', '--short=7', 'HEAD'); ta, ba = revision(g4)
    open(os.path.join(r4, 'sessions/P_session_summary_X.md'), 'a').write(f'\n- код `{h4}`\n'); sh(r4, 'git', 'commit', '-qam', 'самері\n\nClaude-Session: https://claude.ai/code/session_T')
    os.environ['LENS_EXAM_MARK'] = os.path.join(tf, 'exam4')
    tn, _ = revision(g4); okn = seal_ok([r4])   # REV-5 Л3: машина ✗ 0, іспиту нема → «ревізія ⚠ · … · іспит не робився», не «✓»
    open(os.environ['LENS_EXAM_MARK'], 'w').write(heads([r4]) + '\nіспит · незрозуміло 2\n{}\n'); tk, _ = revision(g4); okk = seal_ok([r4])
    open(os.environ['LENS_EXAM_MARK'], 'w').write(heads([r4]) + '\nіспит · незрозуміло 0\n{}\n')
    tb, bb = revision(g4); okb = seal_ok([r4])
    open(os.path.join(r4, 'lens/A.md'), 'a').write('w'); sh(r4, 'git', 'commit', '-qam', 'ще прилад\n\nClaude-Session: https://claude.ai/code/session_T')
    stale = seal_ok([r4]); tab = rev_table([r4])
    rcases += [('REV-4 (а): коміт сесії без запису в самері → ✗ з хешем, печатка «ревізія ✗»', ba and 'коміти сесії без запису' in ta and h4 in ta and ta.splitlines()[-1].startswith('ревізія ✗')),
               ('REV-5 Л3: машина ✗ 0, іспиту нема → «ревізія ⚠ … іспит не робився», мітка не дає ✓ (S155: «✗ 0» звучало як «повно»)', tn.splitlines()[-1].startswith('ревізія ⚠') and 'іспит не робився' in tn.splitlines()[-1] and 'машина: ' in tn.splitlines()[-1] and not okn),
               ('REV-5 Л3: іспит на HEAD «незрозуміло 2» → «ревізія ⚠ · … незрозуміло 2»', tk.splitlines()[-1].startswith('ревізія ⚠') and 'незрозуміло 2' in tk.splitlines()[-1] and not okk),
               ('REV-4 (б) + REV-5: записав коміт у самері, іспит на HEAD «незрозуміло 0» → печатка «ревізія ✓ · HEAD … · ✗ 0 · машина … · іспит ✓» і в мітці', not bb and tb.splitlines()[-1].startswith('ревізія ✓') and '· ✗ 0 ·' in tb.splitlines()[-1] and 'іспит ✓' in tb.splitlines()[-1] and okb),
               ('REV-4 (г): новий коміт після ревізії → печатка стара (і іспит — теж)', not stale),
               ('REV-4 (в): --table — заголовок «що · дім · коміт» і кожен коміт сесії', '| що | дім | коміт |' in tab and h4 in tab and 'ще прилад' in tab)]
    # REV-5 Л1 (12): вкладення Konst — журнал сесії з 2 зображеннями user (і 1 зображенням у tool_result — не рахується)
    trp = os.path.join(tf, 'tr.jsonl'); img = {'type': 'image', 'source': {'type': 'base64', 'data': 'x'}}
    open(trp, 'w').write(json.dumps({'type': 'user', 'message': {'content': [{'type': 'text', 'text': 'концепти'}, img, img]}}) + '\n'
                         + json.dumps({'type': 'user', 'message': {'content': [{'type': 'tool_result', 'content': [img]}]}}) + '\n')
    ra = mk_nl(good_nl); a0 = attachments([ra], trp)
    os.makedirs(os.path.join(ra, 'docs/shots')); [open(os.path.join(ra, f'docs/shots/c{i}.webp'), 'w').write('x') for i in (1, 2)]
    sh(ra, 'git', 'add', '-A'); sh(ra, 'git', 'commit', '-qm', 'концепти\n\nClaude-Session: https://claude.ai/code/session_T'); a1 = attachments([ra], trp)
    rb = mk_nl(good_nl.replace('- далі', '- скриншот вади — не зберігаємо: лише показ; далі')); a2 = attachments([rb], trp)
    open(os.path.join(tf, 'tr0.jsonl'), 'w').write(json.dumps({'type': 'user', 'message': {'content': 'текст'}}) + '\n')
    rcases += [('(12) S155 ②: 2 зображення Konst у чаті, у репо 0 → ✗ (зображення з tool_result не рахуються)', a0 and a0[0] == '✗' and '2 зображень' in a0[1]),
               ('(12) 2 зображення збережено комітом сесії → ✓', a1 and a1[0] == '✓'),
               ('(12) «не зберігаємо» в самері → ✓', a2 and a2[0] == '✓'),
               ('(12) зображень нема → тиша', attachments([ra], os.path.join(tf, 'tr0.jsonl')) is None),
               ('(12) журналу нема → ⓘ «не перевірено», не ✓', (attachments([ra], os.path.join(tf, 'none.jsonl')) or ('',))[0] == 'ⓘ')]
    os.environ.pop('LENS_REV_MARK'); os.environ.pop('LENS_EXAM_MARK', None)
    for name, ok in rcases:
        print(('✓' if ok else '✗') + ' ' + name); bad += not ok
    total = len(cases) + len(jcases) + len(hcases) + len(tcases) + len(rcases)
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
    if a[0] == 'revision':   # REV-1: ревізія агента = ревізія Konst — той самий прохід, що й на слово «ревізія»
        if '--table' in a:   # REV-4 (в): заготовка таблиці ревізії з git log сесії
            print(rev_table(session_repos(next((x for x in a[1:] if x != '--table'), '/home/user')))); sys.exit(0)
        t, b = revision(a[1] if len(a) > 1 else '/home/user'); print(t or 'репо сесії не знайдено'); sys.exit(1 if b else 0)
    if a[0] == 'gate':   # REV-1: для hooks/precompact_guard.sh — лише ✗
        x = gate(a[1] if len(a) > 1 else '/home/user'); print('\n'.join(x)); sys.exit(1 if x else 0)
    sys.exit(selftest() if a[0] == 'selftest' else report(a))
