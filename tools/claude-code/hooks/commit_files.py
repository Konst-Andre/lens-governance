#!/usr/bin/env python3
# живе доки: коміти в репо Konst робить агент Claude Code (гачок коміту commit-gate.sh, HOOK-2 п.«нові файли»; QR CC-12, 14.10.2026, «так» Konst).
"""Сторож файлів коміту — що коміт ВНЕСЕ, перевіряється до запуску команди.

Подія: QR CC-12 — `sed` записав у корінь файл з `|` в імені, `git add -A && git commit` поніс його в main.
Гейт коміту бачить стан ДО команди, тож файл, ще не доданий у git, він не бачив. Тут дивимось і на те,
що додасть `git add -A` / `.` / `--all` / `-u` тієї ж команди.

Що ловить (кожне — ✗, коміт зупинено; решта — тиша):
  1. ім'я, яке Windows не створить: <>:"|?* і керівні символи, пробіл/крапка в кінці, CON PRN AUX NUL COM1–9 LPT1–9 (і COM¹–³ LPT¹–³), «\»
     (клон на Windows ламається; pre-commit-hooks `check-illegal-windows-names`)
  2. новий файл у КОРЕНІ репо, не названий явно в `git add <ім'я>` тієї ж команди (законні нові файли в корені —
     0 за видиму історію QR і ядра; явна назва = свідомий намір, тоді тиша)
  3. новий файл більший за 1 МБ, не названий явно (`check-added-large-files`; репо — не склад)
  4. приватний ключ у вмісті (`detect-private-key`) і файл-секрет за іменем: .env · .dev.vars (wrangler) · id_rsa · *.pem/*.key · credentials.json
     (вміст — pre-commit-hooks `detect-private-key`, github.com/pre-commit/pre-commit-hooks, 25.11.2026; імена — свій перелік: aitmpl.com/blog/secure-git-workflow,
     на яку посилались 14.10, плагіна «spac» і імен файлів не має — лише шаблони токенів провайдерів, перевірено 25.11.2026; секрети — ніколи в репо)
  5. мітки конфлікту злиття `<<<<<<< ` / `>>>>>>> ` на початку рядка (`check-merge-conflict`; у main пишуть кілька агентів)
  6. зламаний синтаксис `.json` / `.toml` (`check-json` · `check-toml`; `wrangler.toml` і `manifest.json` ламають деплой)
  7. два шляхи, що різняться лише регістром (`check-case-conflict`; Windows і Mac їх не розрізнять)
  8. зламаний синтаксис змінених скриптів — `.sh`: `bash -n` (+ `shellcheck -S error`, якщо встановлено); `.py`: компіляція
     (`check-ast`). Подія: Routes S1 22.10.2026 — вставка після `;;` зламала диспетчер гачків `lens-hooks.sh`, а з ним — усі гачки
     всіх сесій; спіймано живим прогоном, не гейтом. Лише змінені файли — як у pre-commit (дешево, ~0,1 с на файл).
     `bash -n` лише розбирає (не бачить семантики) — тому shellcheck, де є; його нема — тиша, не ✗.
  9. новий прилад (`tools/` · `.claude/` · `.github/workflows/`: .py .sh .js .mjs .cjs .ts; не `archive/`) без рядка в карті репо —
     ім'я без розширення має бути в `docs/REPO_LAYOUT.md` (або `REPO_LAYOUT.md` · ядро: `tools/claude-code/CLAUDE_CODE.md` · `kernel/Lens_REPO_LAYOUT.md`)
     чи в .md поруч із приладом (`tools/tester/TESTER.md`); у продукті ще й рядок «ядро: …» у повідомленні коміту — кандидат для інших продуктів
     (→ реєстр «Прилади продуктів» у `tools/claude-code/CLAUDE_CODE.md` ядра) чи ні й чому. Подія: AE S104 24.10.2026 — Konst: «втомився нагадувати:
     інструмент, який створюється, повинен одразу мати мітки по документах, щоб наступна сесія про нього знала, і інші продукти теж».
     Практика: перевірка в коміті за шляхом нового файлу (`git diff --cached --diff-filter=A`) → потрібний документ у тому ж коміті
     (ledgerline-docs «documentation types and rules», 24.10.2026); Danger у CI не беремо — комітить агент, ловити треба до коміту.
     «ядро: кандидат» — рядок у реєстрі ядра вже має бути, коли клон ядра поруч (../lens-governance · /tmp/lens-governance · LENS_KERNEL_DIR); нема клону — не судимо.
  10. змінено ШАПКУ наявного приладу (ті самі теки й розширення, що п. 9): рядок-назва (перший рядок шапки) або «Запуск:» / «Usage» / «Вихід:» / «живе доки»
     у шапці — провідному коментарі чи docstring після шебанга, ≤ 150 рядків (до 25.11 — «перші 40 рядків» за початком шматка диффа: довгу
     шапку, як у цього файла, не бачив, а «Usage» у тілі на рядку 41+ давав хибне ✗; аудит 24.11) — а карта репо (та сама, що п. 9, або .md поруч) у цей коміт не потрапила → ✗: опис у карті відстає
     від приладу. Правка тіла без шапки — тиша (шапку міняють, коли міняється що міряє чи як кликати). Подія: AE S104 — описи змінених приладів
     двічі за сесію правились руками. Практика: перевірка за диффом рядків використання → документ у тому ж коміті (borghei «doc-drift-detector»,
     bjornmelin «docs-align», 24.10.2026); хмарні ШІ-сервіси звірки (DriftGuard) не беремо — потрібна локальна перевірка до коміту.
  11. нова копія між щосесійними файлами (doc_health M13) у зміненому CLAUDE.md · профілі · шаблоні · rules/*.md (AE S142).
  12. нова копія в ДОДАНИХ рядках будь-якого .md репо, крім знімків і журналів (doc_health M14 — копія щосесійного шару ·
     M15 — дубль іншого документа; AE S143). Старий борг файла не блокує; свідомий виняток — <!-- copy-ok: причина --> у рядку.
  13. «храповик» розділів (AE S156, 💡 Konst «приймаю з підсиленням»): коміт, що ЗБІЛЬШУЄ розділ .md, уже більший за 16 КБ (doc_health M3 —
     та сама мірка `m3_sections`), або вносить новий такий розділ → ✗; зменшити чи не чіпати — тиша. Подія: 11 розділів > 16 КБ в AE висіли з S147 —
     M3 лише ⚠ на старті, а «Коротко» брифів дописувались далі (AE-AI §0: 16 → 19 КБ за S155). Практика — ratchet: старий борг дозволено, ріст —
     ні, поріг лише опускається (Notion «ratcheting system», Flutter Quality Ratchet, ratchets DESIGN.md — 19.11.2026). Свідомий виняток —
     <!-- ratchet-ok: причина --> у доданих рядках (як copy-ok).
  14. «храповик старту» (EquipLens S41, 22.11.2026; Konst: «повинно було так і працювати… щоб більше не повторювалося»): п.13 свідомо не міряє файли,
     що читаються ЦІЛКОМ (самері, черга, журнал гачків — doc_health M2 / J_KB), а свого храповика в них не було → самері S40 виросло 30 → 132 КБ
     за ≈100 комітів, і кожен пройшов (M2 — лише ⚠ на старті). Тепер: коміт, що ЗБІЛЬШУЄ самері (`sessions/*summary*`, `docs/summary/`) чи чергу
     (`*CHERGA.md`) понад 25 КБ або журнал гачків понад 24 КБ → ✗ з ліками: самері — нове `S<N+1>` (§0 лише відкрите), старе — в архів;
     черга — прополка; журнал ядра — `tools/claude-code/journal_rotate.py` (інший `HOOK_JOURNAL.md` — закриті рядки в архів руками: ротатор знає лише журнал ядра). Зменшити — тиша; свідомо — <!-- ratchet-ok: причина -->.
  15. «нова сесія — нове самері» (`SESS-1`, EquipLens S45 25.11.2026; Konst: «я не казав продовжувати S44… як правильно?»): коміт, що чіпає самері
     `sessions/<P>_session_summary_S<N>_*.md`, — найновіше живе самері має бути додане цим комітом або комітом із трейлером `Claude-Session:` ЦІЄЇ
     сесії (ключ — `CLAUDE_CODE_REMOTE_SESSION_ID` без `cse_` ≡ трейлер без `session_`; нема ключа — тиша). Подія: стартове «Продовження S44» —
     нова сесія 4 коміти дописувала в чуже самері (S44 почала `…DxDy`, писала `…E29`). Не контейнер: VM перезапускається й посеред розмови
     (замір 25.11: старт VM 22:22 при тій самій сесії). Свідомо — `<!-- sess-ok: причина -->` у найновішому самері.
Не беремо з pre-commit-hooks: пробіли й кінці файлів (шум у диффах даних), no-commit-to-branch (ми свідомо комітимо в main),
submodules (їх нема).

  python3 commit_files.py selftest   — тимчасове репо: кожен випадок має дати свій ✗, чиста команда — тишу
  HOOK_INJECT=1 … selftest           — сторож вимкнено → selftest червоніє (зуби)
"""
import os, re, subprocess, sys, json

WIN_BAD = re.compile(r'[<>:"|?*\\\x00-\x1f]')   # + «\» (learn.microsoft.com naming-a-file, 24.11.2026)
WIN_RESERVED = re.compile(r'^(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(\..*)?$', re.I)
BIG = 1024 * 1024
KEY = re.compile(rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY')
SECRET_NAME = re.compile(r'(^|/)(\.env(\..*)?|\.dev\.vars|id_(rsa|ed25519|ecdsa)[^/]*|[^/]*\.(pem|p12|pfx|key)|credentials\.json)$', re.I)
CONFLICT = re.compile(rb'^(?:<{7} |>{7} )', re.M)
SHELLCHECK = next((x for x in (os.environ.get('SHELLCHECK_BIN', ''), '/usr/bin/shellcheck', '/usr/local/bin/shellcheck') if x and os.path.isfile(x)), None)


def git(top, *a):
    r = subprocess.run(['git', '-C', top, *a], capture_output=True)
    return r.stdout.decode('utf-8', 'surrogateescape')


def zlist(top, *a):
    return [x for x in git(top, a[0], '-z', *a[1:]).split('\0') if x]   # -z одразу за підкомандою: після `--` git прочитав би його як шлях


def add_args(cmd):
    """Що команда додає: (усе? , явно названі шляхи)."""
    every, named = False, set()
    for seg in re.split(r'&&|\|\||;|\n', cmd):
        m = re.search(r'\bgit\s+(?:-C\s+\S+\s+)?add\b(.*)', seg)
        if not m:
            continue
        for tok in re.findall(r'"[^"]*"|\'[^\']*\'|\S+', m.group(1)):
            t = tok.strip('"\'')
            if t in ('-A', '--all', '.', '-u', '--update', ':/'):
                every = True
            elif not t.startswith('-'):
                named.add(t.rstrip('/'))
    if re.search(r'\bgit\b[^\n;&|]*\bcommit\b[^\n;&|]*\s(?:-[a-zA-Z]*a[a-zA-Z]*|--all)\b', cmd):   # git commit -a / -am / --all (не --amend; --all — аудит 24.11)
        every = True
    return every, named


HEAD_MAX = 150
JOURNAL = 'tools/claude-code/hooks/HOOK_JOURNAL.md'


def head_zone(text):
    """Шапка приладу (п. 10): провідний коментар чи docstring після шебанга → (рядки-назви, перший, останній); ≤ HEAD_MAX рядків."""
    ls = text.split('\n'); j = 1 if ls and ls[0].startswith('#!') else 0
    names, first, last = set(), None, 0
    while j < min(len(ls), HEAD_MAX):
        s = ls[j].lstrip()
        q = s[:3] if s.startswith(('"""', "'''")) else '*/' if s.startswith('/*') and '*/' not in s else None
        if q:   # блок: docstring чи /* … */ — до закриття
            k = j if q != '*/' and s.count(q) >= 2 else next((x for x in range(j + 1, len(ls)) if q in ls[x]), len(ls) - 1)
            names.add(j + 1); first = first or j + 1; last = k + 1; j = k + 1; continue
        if s.startswith(('#', '//', '/*', '*')):
            if first is None: names.add(j + 1)
            first = first or j + 1; last = j + 1
        elif s:
            break
        j += 1
    return names, first or 0, min(last, HEAD_MAX)


TOOL_RE = re.compile(r'^(tools|\.claude|\.github/workflows)/.+\.(py|sh|js|mjs|cjs|ts)$')
MAPS = ('docs/REPO_LAYOUT.md', 'REPO_LAYOUT.md', 'tools/claude-code/CLAUDE_CODE.md', 'kernel/Lens_REPO_LAYOUT.md')


def check(top, cmd):
    if os.environ.get('HOOK_INJECT') == '1':
        return []
    every, named = add_args(cmd)
    added = set(zlist(top, 'diff', '--cached', '--name-only', '--diff-filter=A'))
    changed = set(zlist(top, 'diff', '--cached', '--name-only', '--diff-filter=ACMR'))
    if every:
        new_untracked = set(zlist(top, 'ls-files', '--others', '--exclude-standard'))
        added |= new_untracked
        changed |= new_untracked | set(zlist(top, 'diff', '--name-only', '--diff-filter=ACMR'))
    else:   # явно названі в `git add` тієї ж команди — теж ідуть у коміт
        for n in named:
            for f in zlist(top, 'ls-files', '--others', '--exclude-standard', '--', n):
                added.add(f); changed.add(f)
            for f in zlist(top, 'diff', '--name-only', '--diff-filter=ACMR', '--', n):
                changed.add(f)
    explicit = lambda f: f in named or any(f.startswith(n + '/') for n in named if n not in ('.', ''))
    bad = []
    for f in sorted(added):
        parts = f.split('/')
        if any(WIN_BAD.search(p) or p.endswith((' ', '.')) or WIN_RESERVED.match(p) for p in parts):
            bad.append(f'ім\'я, якого Windows не створить: «{f}» (клон на Windows зламається) — перейменуй або прибери')
        elif '/' not in f and not explicit(f):
            bad.append(f'новий файл у корені «{f}» не названо явно — випадковий? прибери; свідомий — назви його в `git add {f}` у тій самій команді, що й коміт')
        if SECRET_NAME.search(f):
            bad.append(f'файл-секрет за іменем «{f}» — секрети ніколи в репо (змінні середовища сесії); додай у .gitignore')
        p = os.path.join(top, f)
        if os.path.isfile(p) and os.path.getsize(p) > BIG and not explicit(f):
            bad.append(f'новий файл «{f}» — {os.path.getsize(p) // 1024} КБ > 1 МБ — справді в репо? свідомо — назви його в `git add {f}` у тій самій команді, що й коміт')
    lower = {}
    for f in zlist(top, 'ls-files') + sorted(added):
        lower.setdefault(f.lower(), set()).add(f)
    for f in sorted(added):
        if len(lower.get(f.lower(), ())) > 1:
            bad.append(f'шляхи різняться лише регістром: {" · ".join(sorted(lower[f.lower()]))} (Windows і Mac їх не розрізнять)')
    for f in sorted(changed):
        p = os.path.join(top, f)
        if not os.path.isfile(p) or os.path.getsize(p) > 2 * BIG:
            continue
        b = open(p, 'rb').read()
        if KEY.search(b):
            bad.append(f'приватний ключ у «{f}» — секрети ніколи в репо; ключ — під заміну')
        if CONFLICT.search(b):
            bad.append(f'мітки конфлікту злиття в «{f}» — злиття не дороблене')
        try:
            if f.endswith('.json'):
                json.loads(b.decode('utf-8-sig'))
            elif f.endswith('.toml'):
                try: import tomllib
                except ImportError: tomllib = None   # Python < 3.11 — перевірки TOML нема, тиша (не «зламаний синтаксис»)
                if tomllib: tomllib.loads(b.decode('utf-8'))
        except Exception as e:
            bad.append(f'зламаний синтаксис «{f}»: {str(e)[:80]}')
        if f.endswith('.sh') or b.startswith(b'#!/bin/bash') or b.startswith(b'#!/usr/bin/env bash'):
            r = subprocess.run(['bash', '-n', p], capture_output=True, text=True)
            if r.returncode:
                bad.append(f'зламаний синтаксис bash «{f}»: {r.stderr.strip().splitlines()[-1][:120]}')
            elif SHELLCHECK:
                r = subprocess.run([SHELLCHECK, '-S', 'error', '-f', 'gcc'] + ([] if b.startswith(b'#!') else ['-s', 'bash']) + [p], capture_output=True, text=True)   # без шебанга — як bash (інакше SC2148 на кожному сорс-файлі)
                if r.returncode and r.stdout.strip():
                    bad.append(f'shellcheck (error) «{f}»: {r.stdout.strip().splitlines()[0][:140]}')
        elif f.endswith('.py'):
            try:
                compile(b, f, 'exec')
            except SyntaxError as e:
                bad.append(f'зламаний синтаксис Python «{f}»: рядок {e.lineno}: {e.msg}')
    # 9. новий прилад без мітки в карті репо (і без рішення «ядро:» у продукті) — AE S104
    tools = [f for f in sorted(added) if TOOL_RE.match(f) and not re.search(r'(^|/)(archive|__pycache__|fixtures?|testdata)/', f)]
    if tools:
        maps = [m for m in MAPS if os.path.isfile(os.path.join(top, m))]
        read = lambda q: open(q, encoding='utf-8', errors='replace').read()
        text = ''.join(read(os.path.join(top, m)) for m in maps)
        for f in tools:
            stem = os.path.splitext(os.path.basename(f))[0]
            near = ''.join(read(os.path.join(top, os.path.dirname(f), x)) for x in os.listdir(os.path.join(top, os.path.dirname(f))) if x.endswith('.md'))
            if stem not in text and stem not in near:
                bad.append(f'новий прилад «{f}» без рядка в карті репо ({" / ".join(maps) or "карти нема — docs/REPO_LAYOUT.md за шаблоном ядра"}) — '
                           f'що міряє · коли брати · запуск; інакше наступна сесія про нього не дізнається')
        # «ядро: кандидат» — рядок у реєстрі ядра має вже бути (аудит S104: інакше правило «тим самим ходом» ніхто не тримає); клону ядра поруч нема — не судимо
        kd = os.environ.get('LENS_KERNEL_DIR') or next((k for k in (os.path.join(os.path.dirname(top), 'lens-governance'), '/tmp/lens-governance') if os.path.isfile(os.path.join(k, 'tools/claude-code/CLAUDE_CODE.md'))), None)
        if re.search(r'ядро:\s*кандидат', cmd) and kd and os.path.isfile(os.path.join(kd, 'tools/claude-code/CLAUDE_CODE.md')):
            reg = read(os.path.join(kd, 'tools/claude-code/CLAUDE_CODE.md'))
            miss = [os.path.basename(f) for f in tools if os.path.splitext(os.path.basename(f))[0] not in reg]
            if miss: bad.append(f'«ядро: кандидат», а в реєстрі «Прилади продуктів» ядра ({kd}/tools/claude-code/CLAUDE_CODE.md) рядка нема: {", ".join(miss)} — спершу рядок і коміт ядра')
        if not os.path.isfile(os.path.join(top, 'kernel/Lens_validate.py')) and not re.search(r'ядро:\s*\S', cmd):
            bad.append(f'новий прилад ({", ".join(os.path.basename(f) for f in tools)}) — у повідомленні коміту бракує рядка «ядро: …»: кандидат для інших продуктів '
                       f'(→ реєстр «Прилади продуктів» у lens-governance:tools/claude-code/CLAUDE_CODE.md, тим самим ходом) чи ні — й чому')
    # 11. нова копія між щосесійними файлами (doc_health M13; S142, 💡 «так» Konst): коміт правки CLAUDE.md · профілю · шаблону · rules/*.md,
    #     що лишає в ЗМІНЕНОМУ файлі копію загальнішого шару → ✗ одразу, а не на старті наступної сесії. Свідомий виняток — <!-- copy-ok: … -->
    inst = {f for f in changed if f in ('CLAUDE.md', 'tools/claude-code/PROFILE.md', 'tools/claude-code/templates/CLAUDE_template.md') or re.match(r'\.claude/rules/[^/]+\.md$', f)}
    if inst:
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import doc_health as dh
            own = os.path.isfile(os.path.join(top, 'tools/claude-code/PROFILE.md'))
            nm = {'CLAUDE.md ядра' if own else 'CLAUDE.md': 'CLAUDE.md', 'профіль': 'tools/claude-code/PROFILE.md', 'шаблон CLAUDE.md': 'tools/claude-code/templates/CLAUDE_template.md'}
            for m, where, what in dh.copies(top):
                if m != 'M13': continue
                fn = where.rsplit(':', 1)[0]; fn = nm.get(fn, fn)
                if fn in inst: bad.append(f'копія між щосесійними файлами (doc_health M13): {where} — {what}. Залиш вказівник на дім або познач <!-- copy-ok: причина -->')
        except Exception: pass   # прилад ядра недоступний — сторож мовчить, M13 скаже на старті
    # 12. нова копія в будь-якому документі репо (doc_health M14 · M15; AE S143, Konst: «щоб працював на весь репозиторій — і на продукт, і на ядро»):
    #     лише ДОДАНІ рядки змінених .md (старий борг чужих комітів не блокує — він на старті ⚠ M14 / ⓘ M15); знімки й журнали — поза (SNAP).
    mds = [f for f in changed if f.endswith('.md')]
    if mds:
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import doc_health as dh
            only, old = {}, {}
            for f in mds:
                if dh.SNAP.search(f): continue
                diff = subprocess.run(['git', '-C', top, 'diff', '-U0', 'HEAD', '--', f], capture_output=True, text=True).stdout
                if not diff: diff = '@@ -0,0 +1,%d @@' % len(open(os.path.join(top, f), encoding='utf-8', errors='replace').read().split('\n'))   # новий файл
                prev = subprocess.run(['git', '-C', top, 'show', 'HEAD:' + f], capture_output=True, text=True).stdout
                old[f] = {x for l in prev.split('\n') for x in dh._shp(l)}
                only[f] = {n for a, b in re.findall(r'^@@ [^+]*\+(\d+)(?:,(\d+))? @@', diff, re.M) for n in range(int(a), int(a) + int(b if b != '' else 1))}
            for m, where, what in dh.spread(top, only, old) if only else []:
                bad.append(f'нова копія в документі (doc_health {m}): {where} — {what}')
        except Exception: pass   # прилад ядра недоступний — сторож мовчить, M14 скаже на старті
    # 13. «храповик» розділів > 16 КБ (AE S156): ріст великого розділу чи новий великий — ✗ (мірка — doc_health.m3_sections)
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import doc_health as dh
        for f in sorted(x for x in changed if x.endswith('.md')):
            fp = os.path.join(top, f)
            if not os.path.isfile(fp): continue
            new = open(fp, encoding='utf-8', errors='replace').read()
            prev = subprocess.run(['git', '-C', top, 'show', 'HEAD:' + f], capture_output=True, text=True).stdout
            if new.count('ratchet-ok:') > prev.count('ratchet-ok:'): continue   # новий виняток — за кількістю, як copy-ok рядком (аудит 24.11: «один раз на файл» заціклював агента)
            key = lambda secs: {(h, sum(1 for x in secs[:i] if x[0] == h)): b for i, (h, b) in enumerate(secs)}   # однакові заголовки — за порядковим номером
            was = key(dh.m3_sections(f, prev)) if prev else {}
            for (h, _), b in key(dh.m3_sections(f, new)).items():
                o = was.get((h, _), 0)
                if b / 1024 > dh.M3_KB and b > o:
                    bad.append(f'розділ «{h[:60].strip()}» у {f}: {b / 1024:.1f} КБ > {dh.M3_KB}' + (f' і виріс на {(b - o) / 1024:.1f} КБ' if o else ' — новий') +
                               ' (храповик): спершу стисни розділ «як є» (закрите — в archive/ з вказівником), тоді дописуй; свідомо — <!-- ratchet-ok: причина -->')
    except Exception: pass   # прилад ядра недоступний — сторож мовчить, M3 скаже на старті
    # 14. храповик старту (EquipLens S41): файли, що читаються цілком, не ростуть понад стелю
    for f in sorted(x for x in changed if x.endswith('.md') and not re.search(r'(^|/)archive/', x)):
        base = os.path.basename(f)
        kind = 'самері' if (f.startswith('sessions/') and 'summary' in base.lower()) or f.startswith('docs/summary/') else \
               'черга' if re.search(r'(^|/|_)CHERGA\.md$', f) else 'журнал' if base == 'HOOK_JOURNAL.md' else None
        fp = os.path.join(top, f)
        if not kind or not os.path.isfile(fp): continue
        new = open(fp, encoding='utf-8', errors='replace').read()
        prev = subprocess.run(['git', '-C', top, 'show', 'HEAD:' + f], capture_output=True, text=True).stdout
        if new.count('ratchet-ok:') > prev.count('ratchet-ok:'): continue
        cap = 24 if kind == 'журнал' else 25; nb, ob = len(new.encode()), len(prev.encode())
        if nb / 1024 > cap and nb > ob:
            cure = {'самері': 'нове самері S<N+1> (§0 — лише відкрите, закрите ✅ — рядком §1), старе — git mv в archive/summaries/ (sessions/README)',
                    'черга': 'прополка: закрите — геть з таблиці, історія — git; рядок > 2000 знаків — бриф',
                    'журнал': 'python3 <ядро>/tools/claude-code/journal_rotate.py <ядро> — закриті рядки → journal/<місяць>' if f == JOURNAL else
                              'закриті рядки — в архів поруч руками (journal_rotate веде лише журнал ядра ' + JOURNAL + ')'}[kind]
            bad.append(f'{kind} {f}: {nb / 1024:.1f} КБ > {cap} і росте (+{(nb - ob) / 1024:.1f} КБ; храповик старту) — {cure}; свідомо — <!-- ratchet-ok: причина -->')
    # 15. нова сесія — нове самері (SESS-1, EquipLens S45)
    key = re.sub(r'^(cse|session)_', '', os.environ.get('LENS_SESSION_KEY') or os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID') or '')
    SS = re.compile(r'^sessions/[^/]*_session_summary_S(\d+)_[^/]*\.md$')
    if key and any(SS.match(f) for f in changed):
        live = {f for f in zlist(top, 'ls-files', '--', 'sessions') if SS.match(f) and os.path.isfile(os.path.join(top, f))} | {f for f in added if SS.match(f)}
        newest = max(live, key=lambda f: int(SS.match(f).group(1)), default=None)
        if newest and newest not in added:
            body = git(top, 'log', '--diff-filter=A', '--format=%B', '--', newest) or ''
            now = open(os.path.join(top, newest), encoding='utf-8', errors='replace').read()
            was = subprocess.run(['git', '-C', top, 'show', 'HEAD:' + newest], capture_output=True, text=True).stdout
            if key not in body and now.count('sess-ok:') <= was.count('sess-ok:'):
                n = int(SS.match(newest).group(1))
                bad.append(f'самері {newest} почала інша сесія (трейлер Claude-Session її коміту ≠ цієї) — нова сесія — нове самері S{n + 1} першим комітом, '
                           f'§0 — лише відкрите; старе — в archive/summaries/, коли живих стало б 3 (sessions/README, SESS-1); свідомо — <!-- sess-ok: причина -->')
    # 10. шапка наявного приладу змінилась, карта — ні (AE S104)
    head_re = re.compile(r'(Запуск|Usage|Вихід|живе доки)\s*:', re.I)
    for f in sorted(changed - added):
        if not TOOL_RE.match(f) or re.search(r'(^|/)(archive|__pycache__|fixtures?|testdata)/', f): continue
        diff = subprocess.run(['git', '-C', top, 'diff', 'HEAD', '-U0', '--', f], capture_output=True, text=True).stdout
        hit = False   # кожен рядок диффа — своїм номером (старий для «-», новий для «+») проти шапки свого боку (аудит 24.11)
        zone = {'-': head_zone(subprocess.run(['git', '-C', top, 'show', 'HEAD:' + f], capture_output=True, text=True).stdout),
                '+': head_zone(open(os.path.join(top, f), encoding='utf-8', errors='replace').read())}
        for h in re.finditer(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@[^\n]*\n((?:[-+][^\n]*\n?)*)', diff, re.M):
            no = {'-': int(h.group(1)), '+': int(h.group(2))}
            for ln in h.group(3).splitlines():
                if not ln.startswith(('-', '+')): continue
                sd = ln[0]; n = no[sd]; no[sd] += 1; names, a, b = zone[sd]
                if n in names or (a <= n <= b and head_re.search(ln[1:])): hit = True
        if not hit: continue
        near = {os.path.join(os.path.dirname(f), x) for x in os.listdir(os.path.join(top, os.path.dirname(f) or '.')) if x.endswith('.md')}
        if not (changed & (set(MAPS) | near)):
            bad.append(f'шапку приладу «{f}» змінено (назва · «Запуск» · «Вихід» · «живе доки»), а карта репо в коміт не потрапила — онови рядок приладу '
                       f'({" / ".join(m for m in MAPS if os.path.isfile(os.path.join(top, m))) or "docs/REPO_LAYOUT.md"}): що міряє · коли брати · запуск')
    return bad


def selftest():
    import tempfile, shutil
    d = tempfile.mkdtemp(); ok = 0; n = 0
    def say(c, m):
        nonlocal ok, n; n += 1; ok += bool(c); print(('✓ ' if c else '✗ ') + m)
    try:
        g = lambda *a: subprocess.run(['git', '-C', d, *a], capture_output=True, check=True)
        g('init', '-q'); os.makedirs(d + '/lens'); open(d + '/README.md', 'w').write('x\n'); open(d + '/lens/a.md', 'w').write('x\n')
        open(d + '/wrangler.toml', 'w').write('name = "x"\n'); open(d + '/Docs.md', 'w').write('x\n')
        g('add', '.'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'init')
        say(check(d, 'git add -A && git commit -m x') == [], 'чисте дерево — тиша')
        open(d + '/lens/b.md', 'w').write('новий у теці\n')
        say(check(d, 'git add -A && git commit -m x') == [], 'новий файл у теці — тиша (законний дім)')
        os.remove(d + '/lens/b.md')
        open(d + '/eb&r=load|back', 'w').write('x')
        r = check(d, 'git add -A && git commit -m x'); say(any('Windows' in x for x in r), 'файл з | у корені через add -A → ✗ Windows (подія CC-12)')
        os.remove(d + '/eb&r=load|back')
        open(d + '/notes.txt', 'w').write('x')
        say(any('корені' in x for x in check(d, 'git add -A && git commit -m x')), 'новий файл у корені через add -A → ✗')
        say(check(d, 'git add notes.txt && git commit -m x') == [], 'той самий файл, названий явно → тиша')
        os.remove(d + '/notes.txt')
        open(d + '/lens/big.bin', 'wb').write(b'0' * (BIG + 10))
        say(any('1 МБ' in x for x in check(d, 'git add -A && git commit -m x')), 'новий файл > 1 МБ через add -A → ✗')
        say(check(d, 'git add lens/big.bin && git commit -m x') == [], 'великий, названий явно → тиша')
        os.remove(d + '/lens/big.bin')
        open(d + '/lens/k.md', 'w').write('-----BEGIN ' + 'OPENSSH PRIVATE KEY-----\nabc\n')   # шматками: цілий взірець у файлі сторож ловить у самому собі
        say(any('ключ' in x for x in check(d, 'git add -A && git commit -m x')), 'приватний ключ у вмісті → ✗')
        os.remove(d + '/lens/k.md')
        open(d + '/.dev.vars', 'w').write('X=1\n')
        say(any('секрет за іменем' in x for x in check(d, 'git add -A && git commit -m x')), '.dev.vars (секрети wrangler) через add -A → ✗')
        os.remove(d + '/.dev.vars')
        open(d + '/lens/a.md', 'w').write('<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> main\n')
        say(any('конфлікту' in x for x in check(d, 'git commit -am x')), 'мітки конфлікту у зміненому файлі (commit -a) → ✗')
        say(any('конфлікту' in x for x in check(d, 'git commit --all -m x')), 'те саме через commit --all → ✗ (аудит 24.11)')
        say(not any('конфлікту' in x for x in check(d, 'git commit --amend -m x')), 'commit --amend без -a — тиша (не «все»)')
        open(d + '/lens/a.md', 'w').write('x\n')
        open(d + '/wrangler.toml', 'w').write('name = "x\n')
        say(any('синтаксис' in x for x in check(d, 'git add -A && git commit -m x')), 'зламаний wrangler.toml → ✗')
        open(d + '/wrangler.toml', 'w').write('name = "x"\n')
        open(d + '/lens/A.md', 'w').write('x\n')
        say(any('регістром' in x for x in check(d, 'git add -A && git commit -m x')), 'lens/A.md поруч з lens/a.md → ✗ регістр')
        os.remove(d + '/lens/A.md')
        open(d + '/lens/h.sh', 'w').write('case "$1" in\n  a) echo a ;;\n  [ -z x ] && echo b\nesac\n')
        say(any('синтаксис bash' in x for x in check(d, 'git add -A && git commit -m x')), 'зламаний .sh (рядок після ;; — подія Routes S1) → ✗')
        open(d + '/lens/h.sh', 'w').write('case "$1" in\n  a) echo a ;;\nesac\n')
        say(check(d, 'git add -A && git commit -m x') == [], 'справний .sh → тиша')
        os.remove(d + '/lens/h.sh')
        open(d + '/lens/t.py', 'w').write('def f(:\n  pass\n')
        say(any('синтаксис Python' in x for x in check(d, 'git add -A && git commit -m x')), 'зламаний .py → ✗')
        os.remove(d + '/lens/t.py')
        # 9 · новий прилад без мітки (AE S104)
        os.makedirs(d + '/tools/stand'); open(d + '/tools/stand/walk_v1.py', 'w').write('x = 1\n')
        r = check(d, 'git add -A && git commit -m x'); say(any('без рядка в карті' in x for x in r) and any('ядро:' in x for x in r), 'новий прилад без карти й без «ядро:» → ✗ обидва')
        os.makedirs(d + '/docs'); open(d + '/docs/REPO_LAYOUT.md', 'w').write('прохід walk_v1 — що міряє\n')
        r = check(d, 'git add -A && git commit -m x'); say(not any('карті' in x for x in r) and any('ядро:' in x for x in r), 'у карті є, «ядро:» нема (продукт) → ✗ лише «ядро:»')
        say(check(d, "git add -A && git commit -m 'прохід\n\nядро: ні — лише AE'") == [], 'у карті є й «ядро: ні — чому» → тиша')
        kd = tempfile.mkdtemp(); os.makedirs(kd + '/tools/claude-code'); open(kd + '/tools/claude-code/CLAUDE_CODE.md', 'w').write('реєстр\n'); os.environ['LENS_KERNEL_DIR'] = kd
        say(any('реєстрі' in x for x in check(d, "git add -A && git commit -m 'ядро: кандидат'")), '«ядро: кандидат» без рядка в реєстрі ядра → ✗ (аудит S104)')
        open(kd + '/tools/claude-code/CLAUDE_CODE.md', 'w').write('| walk_v1 | AE |\n')
        say(check(d, "git add -A && git commit -m 'ядро: кандидат'") == [], '«ядро: кандидат» і рядок у реєстрі є → тиша')
        del os.environ['LENS_KERNEL_DIR']; shutil.rmtree(kd)
        os.makedirs(d + '/tools/tester'); open(d + '/tools/tester/run.py', 'w').write('x = 1\n'); open(d + '/tools/tester/TESTER.md', 'w').write('run — запуск\n')
        say(check(d, "git add -A && git commit -m 'ядро: ні — лише тут'") == [], 'прилад описано в .md поруч (tools/tester/TESTER.md) → тиша')   # «ні»: «кандидат» залежав би від клону ядра в /tmp
        os.makedirs(d + '/tools/archive'); open(d + '/tools/archive/old_v0.py', 'w').write('x = 1\n')
        say(check(d, "git add -A && git commit -m 'ядро: ні'") == [], 'прилад в archive/ → тиша')
        os.makedirs(d + '/kernel'); open(d + '/kernel/Lens_validate.py', 'w').write('x = 1\n')
        say(not any('ядро:' in x for x in check(d, 'git add docs tools kernel/Lens_validate.py && git commit -m x')), 'ядро (є kernel/Lens_validate.py) — «ядро:» не вимагається')
        shutil.rmtree(d + '/kernel')
        # 10 · шапка наявного приладу змінилась, карта — ні (AE S104)
        open(d + '/tools/stand/walk_v1.py', 'w').write('# walk_v1 · прохід\n# Запуск: python3 walk_v1.py site\nx = 1\n')
        g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'base')
        open(d + '/tools/stand/walk_v1.py', 'w').write('# walk_v1 · прохід\n# Запуск: python3 walk_v1.py site --fast\nx = 1\n')
        say(any('шапку приладу' in x for x in check(d, 'git commit -am x')), 'змінено «Запуск:» приладу, карта не в коміті → ✗')
        open(d + '/docs/REPO_LAYOUT.md', 'w').write('прохід walk_v1 — що міряє; --fast\n')
        say(not any('шапку' in x for x in check(d, 'git commit -am x')), 'та сама правка + рядок карти в коміті → тиша')
        g('checkout', '--', 'docs/REPO_LAYOUT.md')
        open(d + '/tools/stand/walk_v1.py', 'w').write('# walk_v1 · прохід\n# Запуск: python3 walk_v1.py site\nx = 2\n')
        say(not any('шапку' in x for x in check(d, 'git commit -am x')), 'правка тіла приладу без шапки → тиша')
        g('checkout', '--', 'tools/stand/walk_v1.py')
        L = ['"' * 3 + 'long · прилад'] + [f'рядок {i}' for i in range(2, 50)] + ['Запуск: python3 long.py a', '"' * 3] + ['x = 1'] * 30
        open(d + '/tools/stand/long.py', 'w').write('\n'.join(L) + '\n'); g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'long')
        open(d + '/tools/stand/long.py', 'w').write('\n'.join(L).replace('long.py a', 'long.py b') + '\n')
        say(any('шапку' in x for x in check(d, 'git commit -am x')), 'шапка 52 рядки: «Запуск:» на рядку 50 змінено, карти нема → ✗ (аудит 24.11: межа «40 рядків»)')
        g('checkout', '--', 'tools/stand/long.py')
        open(d + '/tools/stand/short.py', 'w').write('# short · прилад\n' + 'x = 1\n' * 60); g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'short')
        B = ['# short · прилад'] + ['x = 1'] * 60; B[37:48] = ['y = 2'] * 9 + ['s = "Usage: тіло"', 'y = 2']
        open(d + '/tools/stand/short.py', 'w').write('\n'.join(B) + '\n')
        say(not any('шапку' in x for x in check(d, 'git commit -am x')), '«Usage» у тілі (шматок 38–48, шапка 1 рядок) → тиша (аудит 24.11: хибне ✗ за початком шматка)')
        g('checkout', '--', 'tools/stand/short.py')
        g('rm', '-rq', 'tools', 'docs'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'clean')
        open(d + '/stray.txt', 'w').write('x')
        say(check(d, 'git add lens/a.md && git commit -m x') == [], 'нестежений файл, якого команда не додає → тиша (у коміт не піде)')
        # 11 · нова копія між щосесійними файлами (S142)
        S = 'перед будь-якою правкою покажи план мікроскоп і дочекайся слова так від konst'
        os.environ['LENS_KERNEL'] = 'none'; os.makedirs(d + '/tools/claude-code/templates', exist_ok=True)
        open(d + '/tools/claude-code/PROFILE.md', 'w').write('```text\n· ' + S + '\n```\n'); g('add', 'tools/claude-code/PROFILE.md'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'p')
        open(d + '/CLAUDE.md', 'w').write('- ' + S + '\n')
        say(any('M13' in x for x in check(d, "git add -A && git commit -m 'ядро: ні'")), 'CLAUDE.md з дослівною копією профілю → ✗ M13 (S142)')
        open(d + '/CLAUDE.md', 'w').write('- ' + S + ' <!-- copy-ok: тест -->\n')
        say(not any('M13' in x for x in check(d, "git add -A && git commit -m 'ядро: ні'")), 'та сама копія з copy-ok → тиша')
        # 12 · нова копія в документі репо (AE S143)
        g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'c')
        os.makedirs(d + '/tools/x', exist_ok=True); open(d + '/tools/x/G.md', 'w').write('# Г\nсвоє правило приладу\n')
        g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'g')
        open(d + '/tools/x/G.md', 'a').write('- ' + S + '\n')
        say(any('M14' in x for x in check(d, "git add -A && git commit -m 'ядро: ні'")), 'документ репо: доданий рядок — копія профілю → ✗ M14 (AE S143)')
        g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'old')
        open(d + '/tools/x/G.md', 'a').write('- інший рядок без копії\n')
        say(not any('M14' in x for x in check(d, "git add -A && git commit -m 'ядро: ні'")), 'стара копія в файлі, доданий рядок чистий → тиша (борг — на старті)')
        g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'o2')
        t = open(d + '/tools/x/G.md').read().replace(S, S + ' і ще кілька нових слів у кінці')
        open(d + '/tools/x/G.md', 'w').write(t)
        say(not any('M14' in x for x in check(d, "git add -A && git commit -m 'ядро: ні'")), 'правка старого рядка зі старою копією → тиша (хибне AE S143: нова лише та копія, якої не було на HEAD)')
        g('checkout', '--', 'tools/x/G.md')
        os.makedirs(d + '/docs/summary', exist_ok=True); open(d + '/docs/summary/P_SUMMARY_2026-11-13.md', 'w').write('- ' + S + '\n')
        say(not any('M14' in x for x in check(d, "git add -A && git commit -m 'ядро: ні'")), 'копія в самері (знімок) → тиша')
        # 13. храповик розділів > 16 КБ (AE S156)
        g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'o3')
        big = '## Великий\n' + 'ж' * (17 * 512) + '\n'; small = '## Малий\nx\n'
        open(d + '/lens/R.md', 'w').write(big + small); g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'r0')
        R = lambda: [x for x in check(d, "git add -A && git commit -m 'ядро: ні'") if 'храповик' in x]
        open(d + '/lens/R.md', 'w').write(big + 'ще абзац\n' + small); say(len(R()) == 1 and 'виріс' in R()[0], 'храповик: розділ > 16 КБ виріс → ✗ (AE S156)')
        open(d + '/lens/R.md', 'w').write(big[:-200] + '\n' + small); say(R() == [], 'храповик: великий розділ зменшився → тиша')
        open(d + '/lens/R.md', 'w').write(big + small + 'ще\n'); say(R() == [], 'храповик: виріс малий розділ → тиша')
        open(d + '/lens/R.md', 'w').write(big + small + '## Новий великий\n' + 'ж' * (17 * 512) + '\n'); say(len(R()) == 1 and 'новий' in R()[0], 'храповик: новий розділ > 16 КБ → ✗')
        open(d + '/lens/R.md', 'w').write(big + 'ще абзац <!-- ratchet-ok: перенос перед стисненням -->\n' + small); say(R() == [], 'храповик: свідомий виняток ratchet-ok → тиша')
        os.makedirs(d + '/archive', exist_ok=True); open(d + '/archive/old.md', 'w').write(big); say(R() == [], 'храповик: archive/ (історія) не міряється')
        g('checkout', '--', 'lens/R.md'); os.remove(d + '/archive/old.md')
        # 14. храповик старту (EquipLens S41): самері / черга / журнал понад стелю не ростуть
        os.makedirs(d + '/sessions', exist_ok=True); sf = d + '/sessions/P_session_summary_S9_X.md'
        open(sf, 'w').write('# S9\n' + 'ж\n' * 13500); g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 's9')
        S14 = lambda: [x for x in check(d, "git add -A && git commit -m 'ядро: ні'") if 'храповик старту' in x]
        open(sf, 'a').write('| 91 | ще хід |\n'); say(len(S14()) == 1 and 'S<N+1>' in S14()[0], 'храповик старту: самері > 25 КБ росте → ✗ з ліками «нове самері» (S40 — 132 КБ)')
        open(sf, 'w').write('# S9\n' + 'ж\n' * 13000); say(S14() == [], 'храповик старту: самері зменшилось → тиша')
        open(sf, 'w').write('# S9\n' + 'ж\n' * 13500 + 'ще <!-- ratchet-ok: перенос -->\n'); say(S14() == [], 'храповик старту: ratchet-ok → тиша')
        g('add', '-A'); g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'з маркером'); open(sf, 'a').write('ще рядок <!-- ratchet-ok: другий перенос -->\n'); say(S14() == [], 'храповик старту: другий ratchet-ok у файлі, де вже є маркер → тиша (аудит 24.11)')
        g('checkout', '--', 'sessions/P_session_summary_S9_X.md')
        open(d + '/lens/P_CHERGA.md', 'w').write('ж\n' * 13500); say(len(S14()) == 1 and 'прополка' in S14()[0], 'храповик старту: нова черга > 25 КБ → ✗ (черга ядра — 39 КБ)')
        os.remove(d + '/lens/P_CHERGA.md')
        os.makedirs(d + '/tools/claude-code/hooks', exist_ok=True); open(d + '/tools/claude-code/hooks/HOOK_JOURNAL.md', 'w').write('ж\n' * 13000)
        say(len(S14()) == 1 and 'journal_rotate' in S14()[0], 'храповик старту: журнал гачків > 24 КБ → ✗ з командою ротації')
        os.remove(d + '/tools/claude-code/hooks/HOOK_JOURNAL.md')
        open(d + '/lens/HOOK_JOURNAL.md', 'w').write('ж\n' * 13000)
        say(len(S14()) == 1 and 'руками' in S14()[0] and 'journal_rotate.py <' not in S14()[0], 'храповик старту: чужий журнал > 24 КБ → ✗ без команди ротатора ядра (аудит 24.11)')
        os.remove(d + '/lens/HOOK_JOURNAL.md')
        # 15. нова сесія — нове самері (SESS-1)
        ci = lambda m: g('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', m)
        s9 = d + '/sessions/P_session_summary_S9_X.md'; open(s9, 'w').write('# S9\n'); g('add', '-A'); ci('S9\n\nClaude-Session: https://claude.ai/code/session_AAA')
        S15 = lambda: [x for x in check(d, "git add -A && git commit -m 'ядро: ні'") if 'SESS-1' in x]
        os.environ['LENS_SESSION_KEY'] = 'cse_BBB'
        open(s9, 'a').write('| 1 | хід |\n'); say(len(S15()) == 1 and 'S10' in S15()[0], 'SESS-1: інша сесія дописує в чуже самері → ✗ «нове самері S10» (S44, 25.11)')
        s10 = d + '/sessions/P_session_summary_S10_Y.md'; open(s10, 'w').write('# S10\n'); say(S15() == [], 'SESS-1: нове самері в цьому ж коміті → тиша')
        g('add', '-A'); ci('S10\n\nClaude-Session: https://claude.ai/code/session_BBB'); open(s10, 'a').write('| 1 | хід |\n'); say(S15() == [], 'SESS-1: самері цієї сесії (трейлер ≡ ключ) → тиша')
        os.environ['LENS_SESSION_KEY'] = 'cse_CCC'; say(len(S15()) == 1, 'SESS-1: третя сесія в S10 → ✗')
        open(s10, 'a').write('<!-- sess-ok: Konst сказав продовжити -->\n'); say(S15() == [], 'SESS-1: sess-ok → тиша')
        g('checkout', '--', 'sessions/'); os.environ['LENS_SESSION_KEY'] = '-'; open(s10, 'a').write('x\n')
        os.environ.pop('LENS_SESSION_KEY'); os.environ.pop('CLAUDE_CODE_REMOTE_SESSION_ID', None); say(S15() == [], 'SESS-1: нема ключа сесії (локально) → тиша')
        g('checkout', '--', 'sessions/')
        os.environ.pop('LENS_KERNEL', None)
    finally:
        shutil.rmtree(d)
    print(f'─── commit_files selftest: {ok}/{n} ───')
    return ok == n


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        sys.exit(0 if selftest() else 1)
    print(__doc__)
