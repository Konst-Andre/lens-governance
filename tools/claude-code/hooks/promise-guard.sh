#!/bin/bash
# живе доки: агент звітує Konst словами «можна /compact» і рядками «пропуск Konst» у журналі гачків. Дім — lens-governance:tools/claude-code/hooks/ (AE S146, «так» Konst 14.11.2026).
# Чому (Konst S146: «мені мало того, що ти просто записав… щоб ти виконував те, що пишеш, а не просто написав»): двічі за сесію агент
#   (1) сказав «можна /compact», не прогнавши сторож стиснення, і (2) звітував рядком «пропуск Konst» у журналі як дією, хоча виправлення ще не було.
#   Правило «будь уважнішим» не спрацювало двічі → машина судить лише вимірне: сторож · хеш коміту · зуб.
# Подія Stop (code.claude.com/docs/en/hooks «Stop»: last_assistant_message, decision block + reason, stop_hook_active; 14.11.2026):
#   ① у відповіді «можна /compact» → сам проганяє сторож стиснення (precompact_guard.sh, «ручне», позначки — у тимчасову теку) → зупинив би → block з його причиною;
#   ② рядок «пропуск Konst», доданий у HOOK_JOURNAL.md цією сесією (комітами з міткою сесії + незакомічене), без хешу коміту, що є в git, і без зуба
#      (selftest · --inject · INJECT · чек-лист) → block; виняток — «НЕ ЗРОБЛЕНО: чому · коли» в рядку;
#   ③ є такий відкритий рядок цієї сесії, а у відповіді нема слів «не зроблено» в перших 1500 знаках → block (Konst бачить невиконане першим, не «записано»).
#   ④ (REV-4, AE S148) «ревізія ✓ / пройдена / зроблена / чиста» поза лапками й кодом → у відповіді печатка handoff_check.py revision
#      «ревізія ✓ · HEAD <репо>@<h7> … · ✗ 0» саме на поточному HEAD, і та сама — у мітці ревізії (пише лише revision) → інакше block.
#   stop_hook_active не пропускає (інакше друга спроба обходила б суд), але стеля — 3 зупинки поспіль, далі пропуск і рядок «⚠ обійдено» в журнал спрацювань.
# Подія UserPromptSubmit (режим open): кожен рядок журналу з «НЕ ЗРОБЛЕНО» (будь-якої сесії) → нагадування агентові на початку ходу, доки не закрито.
# Розмиті слова («записав») не судить — зупиняв би даремно. Помилка розбору → тиша (stderr — у журнал помилок диспетчера).
# Зуби: bash promise-guard.sh selftest — на тимчасових репо; PG_INJECT=1|2|3|4|5 bash promise-guard.sh selftest — кожен ✗ (зламаний суд червоніє; 4 — будь-який хеш «народився в ході»; 5 — заяву ревізії не бачить).
# Подія Stop (режим shadow, В-377 «так» Konst 14.11.2026 — тінь 2 сесії, далі блок при ≤ 1 хибній на 10 ходів): «заява дії = доказ» — у звіті
#   «записав · закомітив · запушив · виправив · додав · зробив · готово · зроблено · ✅» (не в лапках «…», не в коді, не «не …», не «у ході N» / «S1xx»)
#   → хоч один хеш коміту, що є в git і народився після останнього справжнього повідомлення Konst (transcript_path); «запушив» → він уже в origin/*;
#   кожен хеш звіту — є в git; кожне `файл:рядок` — рядок існує. + злитий сюди memory_line (FAB-1): рядок «пам'ять: …» проти стану git.
#   Вирок — рядком у /tmp/lens-shadow-<сесія>.tsv, нічого не друкує; підсумок — bash promise-guard.sh tally <сесія> (рядком у журнал гачків щосамері).
mode="${1:-stop}"
case "$mode" in selftest|tally) HOOK_IN="{}" ;; *) HOOK_IN="$(cat)" ;; esac
export HOOK_IN PG_SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 - "$mode" "${@:2}" <<'PY'
import json, os, re, subprocess, sys, tempfile
HERE = os.environ['PG_SELF']
CLAIM = re.compile(r"(?<![«\"„])(?<!не )(?<!не\s\s)можна\s+(?:робити\s+|запускати\s+)?/compact", re.I)   # у лапках — цитата правила, не заява (хибне S146, хід 11: стартове цитувало сторож)
MISS = re.compile(r"пропуск Konst", re.I)
OPEN = re.compile(r"(?<!«)НЕ ЗРОБЛЕНО:")   # мітка — з двокрапкою; згадка правила «НЕ ЗРОБЛЕНО» в лапках — не обіцянка (хибне S146, хід 9)
HASH = re.compile(r"`([0-9a-f]{7,40})`")
TEETH = re.compile(r"зуб|selftest|--inject|INJECT|чек-лист", re.I)
SAID = re.compile(r"не зроблено", re.I)
env = lambda k, d: os.environ.get(k) or d

def git(repo, *a):
    r = subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def repos():
    root = env('LENS_ROOT', '/home/user')
    return [os.path.join(root, n) for n in sorted(os.listdir(root)) if os.path.exists(os.path.join(root, n, '.git'))] if os.path.isdir(root) else []   # .git-файл — тека worktree (../AE-main)

INJ = os.environ.get('PG_INJECT', '')   # зуби selftest: 1 — будь-який хеш «є в git»; 2 — заяву «можна /compact» не бачить; 3 — коміти сесії не рахуються; 4 — будь-який хеш «народився в ході»; 5 — заяву ревізії не бачить
def exists(h):
    if INJ == '1': return True
    return any(git(r, 'cat-file', '-e', h + '^{commit}') is not None for r in repos())

def sid(d):
    s = env('CLAUDE_CODE_REMOTE_SESSION_ID', '') or d.get('session_id') or ''
    for p in ('cse_', 'session_'): s = s[len(p):] if s.startswith(p) else s
    return re.sub(r'[^A-Za-z0-9_-]', '', s)

def added_rows(d):
    """Рядки «пропуск Konst», додані в журнал цією сесією: від батька першого коміту з міткою сесії (або від HEAD) до робочої теки."""
    j = env('LENS_JOURNAL', os.path.join(HERE, 'HOOK_JOURNAL.md')); repo = os.path.dirname(j)
    s = sid(d); base = 'HEAD'
    if s and INJ != '3':
        log = git(repo, 'log', '--format=%H', f'--grep=Claude-Session: .*{s}', '--', j) or ''
        hs = log.split()
        if hs and git(repo, 'rev-parse', '-q', '--verify', hs[-1] + '^') is not None: base = hs[-1] + '^'
    diff = git(repo, 'diff', base, '--', j) or ''
    return [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++') and MISS.search(l)]

def journal_open():
    j = env('LENS_JOURNAL', os.path.join(HERE, 'HOOK_JOURNAL.md'))
    try: return [l for l in open(j, encoding='utf-8') if OPEN.search(l) and l.startswith('|')]
    except OSError: return []

def guard_says():
    t = tempfile.mkdtemp()
    e = dict(os.environ, LENS_FLAG=os.path.join(t, 'flag'), LENS_LOG=os.path.join(t, 'log'), LENS_HELD=os.path.join(t, 'held'), LENS_HOOKS=HERE)
    try:
        r = subprocess.run(['bash', env('LENS_PC_GUARD', os.path.join(HERE, 'precompact_guard.sh'))], input='{"trigger":"manual","custom_instructions":null}',
                           capture_output=True, text=True, errors='replace', env=e, timeout=float(env('PG_TIMEOUT', '45')))   # сторож ріже вивід head -c посеред літери — падіння S146
    except subprocess.TimeoutExpired:   # не встиг — не «пропустив»: заява лишається неперевіреною
        return ("сторож не відповів за " + env('PG_TIMEOUT', '45') + " с — прожени сам: echo '{\"trigger\":\"manual\"}' | LENS_HOOKS=<ядро>/tools/claude-code/hooks "
                "bash <ядро>/tools/claude-code/hooks/precompact_guard.sh; echo $? — «можна /compact» лише після виходу 0 у цьому ході")
    return (r.stderr.strip() or 'вихід 2')[:1500] if r.returncode == 2 else None

def verdict(d):
    msg = d.get('last_assistant_message') or ''
    if CLAIM.search(msg) and INJ != '2':
        g = guard_says()
        if g: return ("Ворота «сказав — перевір» (Konst S146): у відповіді «можна /compact», а сторож стиснення на цьому стані зупинить. Його слова:\n" + g +
                      "\nВиправ ✗ (ревізія → коміт → push), тоді пиши «можна /compact». ✗ не пояснювати — виправляти.")
    sg = seal_gap(msg)   # ④ REV-4: «ревізія ✓» лише з печаткою revision на поточному HEAD
    if sg: return sg
    rows = added_rows(d); bad = []; opened = []
    for r in rows:
        if OPEN.search(r): opened.append(r); continue
        hs = [h for h in HASH.findall(r) if exists(h)]
        if not hs or not TEETH.search(r): bad.append(r)
    if bad:
        return ("Ворота «записав ≠ зробив» (Konst S146): рядок «пропуск Konst» без виправлення — " + bad[0].strip()[:160] + "…\n"
                "Рядок закритий лише з хешем коміту виправлення в бектиках (`abc1234`, що є в git) і зубом (selftest · --inject · пункт чек-листа). "
                "Не встигаєш виправити в цьому ході — напиши в рядку «НЕ ЗРОБЛЕНО: чому · коли» і першими рядками звіту «не зроблено: …». Запис — не дія.")
    if opened and not SAID.search(msg[:1500]):
        return ("Ворота «записав ≠ зробив» (Konst S146): у журналі є відкритий рядок цієї сесії «НЕ ЗРОБЛЕНО» (" + opened[0].strip()[:120] +
                "…), а у звіті нема «не зроблено: …» на початку. Konst має бачити невиконане першим — допиши блок «не зроблено: що · чому · коли».")
    return None

REVCLAIM = re.compile(r"ревізі[яюї]\s*(?:[:—–-]\s*)?(?:✓|пройден|зроблен|чист)|(?:все|усе|всё)\s+записан|пам'ять\s+(?:повн|ціл)|нічого\s+не\s+загубил", re.I)   # заява «ревізія ✓ / пройдена / зроблена / чиста»; REV-5 Л3 (AE S155): і «все записано», «пам'ять повна / ціла», «нічого не загубили» — та сама заява повноти; «ревізія ✗» і «не зроблено» — ні
def hck():
    sys.path.insert(0, os.path.dirname(HERE)); import handoff_check; return handoff_check
def seal_gap(msg):
    """④ REV-4 (Konst AE S148): заява ревізії поза лапками й кодом → у відповіді має бути печатка handoff_check revision на поточному HEAD
    усіх репо сесії, і та сама печатка — у мітці ревізії (її пише лише revision: печатку не надрукуєш руками)."""
    if INJ == '5' or not REVCLAIM.search(plain(msg)): return None
    h = hck(); rs = h.session_repos(env('LENS_ROOT', '/home/user'))
    if not rs: return None
    want = h.stored_seal(rs) or h.seal(rs, 0)   # REV-5 Л3: печатка з мітки revision (у ній «машина: N» і стан іспиту), інакше — очікувана форма
    if want in msg and h.seal_ok(rs): return None
    return ("Ворота «ревізія ✓ = печатка» (REV-4, Konst AE S148): у відповіді заява ревізії, а печатки на поточному HEAD нема"
            + (" (у тексті є, але revision її не ставив — прогін на цьому HEAD дав ✗ або його не було)" if want in msg else "") +
            ".\nПрожени python3 <ядро>/tools/claude-code/handoff_check.py revision на фінальному стані (після останньої правки самері й стартового), "
            "виправ ✗, закоміть, запуш; іспит нового агента — handoff_exam.py run на цьому HEAD (REV-5 Л2: «ревізія ✓» лише з іспитом «незрозуміло 0»); "
            "ще раз revision — і встав його останній рядок як є. Без іспиту чи з «незрозуміло K» заява «✓ / все записано» — неправда: пиши печатку «ревізія ⚠ …» як є. Очікую: " + want)

def counter(d, blocked):
    f = os.path.join(env('LENS_MARK_DIR', '/tmp'), f"lens-promise-{sid(d) or 'x'}.n")
    try: n = int(open(f).read() or 0)
    except (OSError, ValueError): n = 0
    n = n + 1 if blocked else 0
    open(f, 'w').write(str(n)); return n

def stop(d):
    v = verdict(d)
    if v and counter(d, True) > 3:
        counter(d, False); print("⚠ обійдено: 3 зупинки поспіль — " + v[:120].replace('\n', ' '), file=sys.stderr); return None
    if not v: counter(d, False)
    return v

def open_ctx():
    o = journal_open()
    if not o: return None
    return ("Відкриті обіцянки «НЕ ЗРОБЛЕНО» в журналі гачків (" + str(len(o)) + "): спершу їх — виправлення з хешем і зубом, тоді рядок закрити; "
            "не встигаєш — у звіті першими рядками «не зроблено: …».\n" + "\n".join("· " + l.strip()[:220] for l in o[:5]))

# ── «заява дії = доказ» (В-377) і рядок «пам'ять: …» (злито з memory_line.py, FAB-1) — поки лише тінь ──
VERB = re.compile(r"(?<![\w-])(?<!не )(?:записав|закомітив|запушив|виправив|додав|зробив|готово|зроблено)(?![\w-])|✅", re.I)
PUSHED = re.compile(r"(?<![\w-])(?<!не )запушив", re.I)
PAST = re.compile(r"у\s+ході\s+\d+|(?<![\w-])S\d{2,3}(?![\w-])", re.I)   # «у ході 4 записав», «S145: додав» — історія, не заява цього ходу
ANYHASH = re.compile(r"(?<![\w/#.-])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)([0-9a-f]{7,12}|[0-9a-f]{40})(?![\w/.-])")   # і літера, і цифра: не число, не слово
TICKHASH = re.compile(r"`([0-9a-f]{7,12}|[0-9a-f]{40})`")   # у бектиках — будь-який (S147: ≈ 4 % коротких хешів — самі цифри, голими їх не впізнати)
def hashes(body): return list(dict.fromkeys(TICKHASH.findall(body) + ANYHASH.findall(body)))[:10]
REF = re.compile(r"`(?:([A-Za-z][\w.-]*):)?((?:[\w.-]+/)*[\w.-]+\.[A-Za-z0-9]{1,8}):(\d+)(?:[-–]\d+)?`")
MLINE = re.compile(r"(?mi)^[\s>*_`-]*пам['’ʼ]ять\s*[:—-]\s*(.+)$")
MNONE = re.compile(r"(?i)нового\s+нема")

def plain(msg):
    """Текст без коду й цитат: ```…```, `…`, «…», "…" — там дієслово не заява."""
    t = re.sub(r"```.*?```", " ", msg, flags=re.S)
    t = re.sub(r"`[^`\n]*`", " ", t)
    for _ in range(3): t = re.sub(r"«[^«»]*»", " ", t)
    return re.sub(r'"[^"\n]*"|„[^“”\n]*[“”]', " ", t)

def konst_ts(path):
    """Час останнього справжнього повідомлення (рядок, не tool_result) основної гілки запису; нема — None."""
    last = None
    try:
        for l in open(path, encoding='utf-8', errors='replace'):
            if '"user"' not in l: continue
            try: r = json.loads(l)
            except ValueError: continue
            if r.get('type') != 'user' or r.get('isSidechain') or r.get('isMeta'): continue
            c = (r.get('message') or {}).get('content')
            real = isinstance(c, str) or (isinstance(c, list) and any(isinstance(x, dict) and x.get('type') == 'text' for x in c)
                                          and not any(isinstance(x, dict) and x.get('type') == 'tool_result' for x in c))
            if real and r.get('timestamp'): last = r['timestamp']
    except OSError: return None
    if not last: return None
    import datetime; return datetime.datetime.fromisoformat(last.replace('Z', '+00:00')).timestamp()

def where(h):
    for r in repos():
        if git(r, 'cat-file', '-e', h + '^{commit}') is not None: return r
    return None

def claim_verdict(d):
    """→ (вид, текст) або None. Вид: fake-hash · bad-ref · claim-no-hash · claim-old-hash · unpushed."""
    msg = d.get('last_assistant_message') or ''
    body = re.sub(r"```.*?```", " ", msg, flags=re.S)
    hs = hashes(body)
    found = {h: where(h) for h in hs}
    fake = [h for h, r in found.items() if r is None and INJ != '1']
    if fake: return ('fake-hash', f"коміту {fake[0]} зі звіту нема в жодному репо сесії — хеш з голови?")
    for m in REF.finditer(body):
        pre, path, n = m.group(1), m.group(2), int(m.group(3))
        roots = [r for r in repos() if pre and os.path.basename(r).lower() == pre.lower()] if pre else repos()
        if pre and not roots: roots = repos()   # префікс — не назва репо сесії: шукати в усіх
        cands = [path] if os.path.isabs(path) else [os.path.join(r, path) for r in roots]
        ok = any(os.path.isfile(c) and sum(1 for _ in open(c, encoding='utf-8', errors='replace')) >= n for c in cands)
        if not ok: return ('bad-ref', f"посилання `{m.group(0).strip('`')}` — такого рядка нема в жодному репо сесії")
    lines = [l for l in plain(msg).split('\n') if VERB.search(l) and not PAST.search(l)]
    if not lines: return None
    if not hs: return ('claim-no-hash', "заява «" + VERB.search(lines[0]).group(0) + "» без хешу коміту: «" + lines[0].strip()[:100] + "»")
    t0 = konst_ts(d.get('transcript_path') or '')
    new = [h for h, r in found.items() if INJ == '4' or t0 is None or int(git(r, 'log', '-1', '--format=%ct', h).strip() or 0) >= t0]
    if not new: return ('claim-old-hash', "заява дії, а жоден хеш звіту (" + ', '.join(hs[:3]) + ") не народився в цьому ході — старий коміт за доказ")
    if any(PUSHED.search(l) for l in lines):
        un = [h for h in new if not (git(found[h], 'branch', '-r', '--contains', h) or '').strip()]
        if un: return ('unpushed', f"«запушив», а коміту {un[0]} ще нема в origin — push і read-back")
    return None

def mem_verdict(d):
    """Рядок «пам'ять: …» проти стану git (з memory_line.py, FAB-1). → (вид, текст) або None. Вид: no-line · none-dirty · no-sha · fake-sha · unpushed."""
    m = MLINE.findall(d.get('last_assistant_message') or '')
    if not m: return ('no-line', "у відповіді нема рядка «пам'ять: <коміт> (доми)» або «пам'ять: нового нема» (профіль, ЗВІТ)")
    rs = [r for r in repos() if not os.path.exists(os.path.join(r, '.git', 'lens-readonly'))]
    dirty = [os.path.basename(r) for r in rs if (git(r, 'status', '--porcelain') or '').strip()]
    ahead = [os.path.basename(r) for r in rs if (git(r, 'rev-parse', '--abbrev-ref', '@{u}') or '').strip()
             and (git(r, 'rev-list', '--count', '@{u}..HEAD') or '0').strip() not in ('', '0')]
    claim = m[-1]
    if MNONE.search(claim):
        return ('none-dirty', "«нового нема», а незакомічене: " + (', '.join(dirty) or '—') + "; не на GitHub: " + (', '.join(ahead) or '—')) if dirty or ahead else None
    shas = re.findall(r"\b[0-9a-f]{7,40}\b", claim)
    if not shas: return ('no-sha', "у рядку «пам'ять: …» нема ні хешу коміту, ні «нового нема»")
    for x in shas:
        if where(x) is None: return ('fake-sha', f"коміту {x} з рядка «пам'ять: …» нема в жодному репо сесії")
    if ahead: return ('unpushed', "коміт названо, але HEAD ще не на GitHub у: " + ', '.join(ahead))
    return None

def shadow_path(s): return os.path.join(env('LENS_SHADOW_DIR', '/tmp'), f'lens-shadow-{s}.tsv')

def shadow(d, s):
    if d.get('stop_hook_active'): return
    import time; ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    with open(shadow_path(s), 'a', encoding='utf-8') as f:
        for name, fn in (('memory-line', mem_verdict), ('claim', claim_verdict)):
            v = fn(d); f.write('\t'.join([ts, name, v[0] if v else 'тиша', (v[1][:160].replace('\t', ' ').replace('\n', ' ') if v else '')]) + '\n')

def tally(s):
    rows = [l.rstrip('\n').split('\t') for l in open(shadow_path(s), encoding='utf-8')] if os.path.exists(shadow_path(s)) else []
    out = []
    for name in ('memory-line', 'claim'):
        rr = [r for r in rows if len(r) > 2 and r[1] == name]; k = {}
        for r in rr:
            if r[2] != 'тиша': k[r[2]] = k.get(r[2], 0) + 1
        out.append(f"{name}: ходів {len(rr)} · блокував би {sum(k.values())} (" + (' · '.join(f'{a} {b}' for a, b in sorted(k.items())) or '—') + ")")
    log = os.path.join(env('LENS_SHADOW_DIR', '/tmp'), f'lens-hooks-{s}.tsv')
    old = sum(1 for l in open(log, encoding='utf-8', errors='replace') if '\tmemory-guard\t' in l) if os.path.exists(log) else 0
    return "тінь promise-guard — " + ' | '.join(out) + f" | старий memory-guard блокував {old}"

def selftest_claim():
    """Тінь на тимчасовому репо з віддаленим: старий коміт (до повідомлення Konst) · новий запушений · новий не запушений."""
    import time
    T = tempfile.mkdtemp(); root = os.path.join(T, 'w'); os.makedirs(root); o = os.path.join(T, 'o.git'); r = os.path.join(root, 'Repo')
    sh = lambda c, **e: subprocess.run(c, shell=True, cwd=r, capture_output=True, text=True, env=dict(os.environ, **e)).stdout.strip()
    subprocess.run(['git', 'init', '-q', '--bare', o]); subprocess.run(['git', 'clone', '-q', o, r], capture_output=True)
    now = int(time.time()); old_d = f'@{now - 1000} +0000'
    sh('git config user.email a@b; git config user.name t; printf "a\\nb\\nc\\n" > f.txt; git add f.txt; git commit -qm old', GIT_COMMITTER_DATE=old_d, GIT_AUTHOR_DATE=old_d)
    old = sh('git rev-parse --short HEAD')
    for _ in range(40):   # AE S151 (плаваючий ≈ 4 %): голий хеш впізнається лише з літерою й цифрою (ANYHASH) — хеш із самих цифр валив випадок «✅ … голим словом»
        sh('echo 2 >> f.txt; git commit -qam new'); new = sh('git rev-parse --short HEAD')
        if ANYHASH.fullmatch(new): break
    sh('git push -q -u origin HEAD')
    tp = os.path.join(T, 't.jsonl'); iso = lambda x: time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(x))
    with open(tp, 'w') as f:
        f.write(json.dumps({'type': 'user', 'timestamp': iso(now - 100), 'message': {'content': 'Konst: роби'}}) + '\n')
        f.write(json.dumps({'type': 'user', 'timestamp': iso(now - 10), 'message': {'content': [{'type': 'tool_result', 'content': 'x'}]}}) + '\n')
    save = {k: os.environ.get(k) for k in ('LENS_ROOT', 'LENS_SHADOW_DIR')}; os.environ.update(LENS_ROOT=root, LENS_SHADOW_DIR=T)
    D = lambda m, **k: dict({'last_assistant_message': m, 'transcript_path': tp}, **k)
    cases = []
    def c(name, fn, msg, want, **k):
        v = fn(D(msg, **k)); got = v[0] if v else None
        cases.append((name + ('' if got == want else f' (вийшло: {got})'), got == want))
    C, M = claim_verdict, mem_verdict
    cases.append(('фікстура: новий хеш — з літерою й цифрою (хеш із самих цифр голим не впізнати — плаваючий AE S151)', bool(ANYHASH.fullmatch(new))))
    c('claim: дії нема, хешу нема → тиша', C, 'План: зроблю наступним ходом.', None)
    cases.append(('claim: хеш із самих цифр у бектиках впізнано, голе число — ні (плаваючий selftest S147)', hashes('`1234567` · 7654321 · abc1234') == ['1234567', 'abc1234']))
    c('claim: «записав» без хешу → claim-no-hash', C, 'Записав у бриф.', 'claim-no-hash')
    c('claim: «записав» + новий хеш → тиша', C, f'Записав у бриф, `{new}`.', None)
    c('claim: «✅» + новий хеш голим словом → тиша', C, f'✅ П4 — ядро {new}', None)
    c('claim: «готово» лише зі старим хешем → claim-old-hash', C, f'Готово: `{old}`.', 'claim-old-hash')
    c('claim: старий + новий хеш → тиша (історія поруч з доказом)', C, f'✅ П3 `{old}` · виправив `{new}`', None)
    c('claim: «записав» у лапках → тиша', C, 'Ти просив, щоб «записав» означало слід у git.', None)
    c('claim: «не записав» → тиша', C, 'Ще не записав — наступний хід.', None)
    c('claim: «у ході 4 записав» → тиша', C, 'У ході 4 записав правило.', None)
    c('claim: «S145: додав» → тиша', C, 'S145: додав гачок.', None)
    c('claim: дієслово в коді → тиша', C, 'Сторож шукає `записав`.', None)
    c('claim: хеш з голови → fake-hash', C, 'Прилад `d00df00d1` дав ✓.', 'fake-hash')
    c('claim: `файл:рядок` існує → тиша', C, 'Див. `f.txt:3`.', None)
    c('claim: `Репо:файл:рядок` існує → тиша', C, 'Див. `Repo:f.txt:2`.', None)
    c('claim: `файл:рядок` за кінцем файла → bad-ref', C, 'Див. `f.txt:99`.', 'bad-ref')
    c('claim: `файл:рядок` файла нема → bad-ref', C, 'Див. `nope.md:1`.', 'bad-ref')
    sh('echo 3 >> f.txt; git commit -qam local'); loc = sh('git rev-parse --short HEAD')
    c('claim: «запушив» + новий, але не в origin → unpushed', C, f'Закомітив і запушив `{loc}`.', 'unpushed')
    c('claim: «закомітив» + новий не в origin → тиша (push не заявлено)', C, f'Закомітив `{loc}`.', None)
    c('memory: нема рядка → no-line', M, 'Готово.', 'no-line')
    c('memory: «нового нема», а не запушено → none-dirty', M, "пам'ять: нового нема", 'none-dirty')
    sh('git push -q')
    c('memory: «нового нема», дерево чисте → тиша', M, "пам'ять: нового нема", None)
    c('memory: хеш є і на GitHub, жирним і з ’ → тиша', M, f"**пам’ять:** `{loc}` (ядро)", None)
    c('memory: рядок без хешу → no-sha', M, "пам'ять: записав у самері", 'no-sha')
    c('memory: хеш з голови → fake-sha', M, "пам'ять: deadbee (самері)", 'fake-sha')
    sh('echo n > new.md')
    c('memory: «нового нема», новий файл → none-dirty', M, "пам'ять: нового нема", 'none-dirty')
    sh('rm new.md; echo 4 >> f.txt; git commit -qam c5')
    c('memory: коміт є, не запушено → unpushed', M, f"пам'ять: {loc}", 'unpushed')
    shadow(D('Записав.'), 'st'); shadow(D(f"✅ `{new}`\nпам'ять: {new}"), 'st'); shadow(D('x', stop_hook_active=True), 'st')
    open(os.path.join(T, 'lens-hooks-st.tsv'), 'w', encoding='utf-8').write("t\tstop\tmemory-guard\tx\n")
    s = tally('st'); ok = 'memory-line: ходів 2' in s and 'claim: ходів 2 · блокував би 1 (claim-no-hash 1)' in s and 'блокував 1' in s
    cases.append(('тінь: два ходи (третій — повтор гачка) → підсумок обох суддів і старого гачка' + ('' if ok else f' ({s})'), ok))
    for k, v in save.items():
        if v is None: os.environ.pop(k, None)
        else: os.environ[k] = v
    return cases

def selftest_seal():
    """④ REV-4: заява ревізії без печатки · печатка без прогону · стара печатка → block; свіжа печатка revision → тиша; «ревізія ✗» і цитата — тиша."""
    t = tempfile.mkdtemp(); root = os.path.join(t, 'w'); r = os.path.join(root, 'P'); os.makedirs(os.path.join(r, 'docs', 'summary'))
    G = lambda *a: subprocess.run(['git', '-C', r, *a], capture_output=True, text=True, check=True).stdout.strip()
    G('init', '-q'); G('config', 'user.email', 't@t'); G('config', 'user.name', 't')
    open(os.path.join(r, 'docs', 'summary', 'P_SUMMARY_X.md'), 'w').write('# s\n## §0 ВІДКРИТЕ\n- далі x\n## Стартове\n```text\nСтарт: x\n```\n'); G('add', '.'); G('commit', '-qm', 'base')
    old = {k: os.environ.get(k) for k in ('LENS_ROOT', 'LENS_REV_MARK', 'LENS_SELFTEST_LOG', 'LENS_KERNEL_TMP', 'CLAUDE_CODE_SESSION_ID')}
    os.environ.update(LENS_ROOT=root, LENS_REV_MARK=os.path.join(t, 'mark'), LENS_SELFTEST_LOG=os.path.join(t, 'no-selftest.log'), LENS_KERNEL_TMP=os.path.join(t, 'no-kernel'), CLAUDE_CODE_SESSION_ID='pgsealfixture', LENS_TRANSCRIPT=os.path.join(t, 'no-transcript.jsonl'))   # REV-5 (12): фікстура не бачить справжній журнал сесії (там зображення Konst)   # AE S150: revision у фікстурі читав справжні журнали сесії — selftest (там ✗) і спрацювання гачків (ui-guard без вердикту) → печатка ✗ ≠ очікуваної; тепер фікстура свого журналу не має
    h = hck(); want = h.seal([r], 0); v = lambda m: seal_gap(m) is not None
    out = []
    out.append(('④ «ревізія ✓» без печатки → block', v('Що ти побачиш: ревізія ✓, усе в домах.')))
    out.append(('④ печатка в тексті, але revision її не ставив → block', v('ревізія ✓\n' + want)))
    os.environ['LENS_EXAM_MARK'] = os.path.join(t, 'exam')
    h.revision(root); w0 = h.stored_seal([r]) or ''   # REV-5 Л3: машина ✓, іспиту нема → печатка «ревізія ⚠ … іспит не робився»
    out.append(('④ REV-5: машина ✓, іспиту нема → «ревізія пройдена» навіть з печаткою → block', v('Ревізія пройдена:\n' + w0) and w0.startswith('ревізія ⚠')))
    out.append(('④ REV-5: «все записано» без печатки ✓ → block', v('Що ти побачиш: все записано як слід, переїжджаємо.')))
    open(os.environ['LENS_EXAM_MARK'], 'w').write(h.heads([r]) + '\nіспит · незрозуміло 0\n{}\n')
    h.revision(root); want = h.stored_seal([r]) or want   # прогін ставить печатку в мітку (чисте репо + іспит на HEAD → ✓)
    out.append(('④ печатка revision на поточному HEAD (машина + іспит) → тиша', not v('Ревізія пройдена:\n' + want) and want.startswith('ревізія ✓')))
    out.append(('④ «ревізія ✗», цитата «ревізія ✓» і печатка в коді не є заявою → тиша', not v('ревізія ✗ — виправляю; правило: «ревізія ✓» лише з печаткою; `ревізія ✓`')))
    open(os.path.join(r, 'x.md'), 'w').write('x'); G('add', '.'); G('commit', '-qm', 'x')
    out.append(('④ новий коміт після ревізії → печатка стара → block', v('ревізія ✓\n' + want)))
    os.environ.pop('LENS_EXAM_MARK', None)
    for k, x in old.items():
        if x is None: os.environ.pop(k, None)
        else: os.environ[k] = x
    return out

def selftest():
    t = tempfile.mkdtemp(); root = os.path.join(t, 'w'); k = os.path.join(root, 'k'); os.makedirs(k)
    G = lambda *a: subprocess.run(['git', '-C', k, *a], capture_output=True, text=True, check=True).stdout.strip()
    G('init', '-q'); G('config', 'user.email', 't@t'); G('config', 'user.name', 't')
    j = os.path.join(k, 'HOOK_JOURNAL.md'); open(j, 'w').write('| дата | рядок |\n|---|---|\n| 01.01 | старий **пропуск Konst** без хешу |\n')
    G('add', '.'); G('commit', '-qm', 'base')
    open(os.path.join(k, 'fix.py'), 'w').write('x=1\n'); G('add', '.'); G('commit', '-qm', 'fix\n\nClaude-Session: https://x/session_TESTSID')
    fix = G('rev-parse', '--short', 'HEAD')
    ok_g = os.path.join(t, 'g0.sh'); open(ok_g, 'w').write('exit 0\n')
    no_g = os.path.join(t, 'g2.sh'); open(no_g, 'w').write('echo "Стиснення зупинено — не все збережено: k:незакомічене(1)" >&2; exit 2\n')
    os.environ.update(LENS_ROOT=root, LENS_JOURNAL=j, LENS_MARK_DIR=t, CLAUDE_CODE_REMOTE_SESSION_ID='cse_TESTSID')
    def row(text):
        open(j, 'w').write('| дата | рядок |\n|---|---|\n| 01.01 | старий **пропуск Konst** без хешу |\n' + text)
    D = lambda m: {'last_assistant_message': m, 'session_id': 'x'}
    cases = []
    def case(name, setup, msg, want, guard=ok_g):
        os.environ['LENS_PC_GUARD'] = guard; setup(); got = verdict(D(msg)) is not None
        cases.append((name, got == want))
    case('без заяви й без нових рядків → тиша', lambda: row(''), 'Готово, коміт.', False)
    case('«можна /compact», сторож пропускає → тиша', lambda: row(''), 'Від тебе: можна /compact', False)
    case('«можна /compact», сторож зупинив би → block', lambda: row(''), 'Від тебе: можна /compact', True, no_g)
    sl = os.path.join(t, 'gs.sh'); open(sl, 'w').write('sleep 5; exit 0\n'); os.environ['PG_TIMEOUT'] = '1'
    case('«можна /compact», сторож не встиг → block (не перевірено ≠ можна)', lambda: row(''), 'можна /compact', True, sl); os.environ.pop('PG_TIMEOUT')
    cut = os.path.join(t, 'gu.sh'); open(cut, 'w').write("printf 'ab\\342\\200' ; printf 'Стиснення зупинено' >&2; exit 2\n")
    case('сторож дав обрізану літеру UTF-8 → не падає, block', lambda: row(''), 'можна /compact', True, cut)
    case('цитата «можна /compact» у лапках → тиша', lambda: row(''), 'Сторож не дасть закінчити відповідь із «можна /compact» без прогону', False, no_g)
    case('«не можна /compact», сторож зупинив би → тиша', lambda: row(''), 'Поки не можна /compact: ревізія.', False, no_g)
    case('старий рядок без хешу (до сесії) → тиша', lambda: row(''), 'ок', False)
    case('новий «пропуск Konst» без хешу → block', lambda: row('| 14.11 | **пропуск Konst** — рішення: зроблю потім |\n'), 'ок', True)
    case('новий з хешем, якого нема в git → block', lambda: row('| 14.11 | **пропуск Konst** — `deadbee` selftest |\n'), 'ок', True)
    case('новий з хешем, що є, без зуба → block', lambda: row(f'| 14.11 | **пропуск Konst** — виправлено `{fix}` |\n'), 'ок', True)
    case('новий з хешем, що є, і зубом → тиша', lambda: row(f'| 14.11 | **пропуск Konst** — виправлено `{fix}`, selftest 5/5 |\n'), 'ок', False)
    case('новий «НЕ ЗРОБЛЕНО», звіт мовчить → block', lambda: row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: чому · коли |\n'), 'Готово.', True)
    case('новий «НЕ ЗРОБЛЕНО», звіт каже «не зроблено» → тиша', lambda: row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: чому · коли |\n'), 'Що ти побачиш: …\nне зроблено: центр — наступний хід', False)
    case('«не зроблено» лише в кінці довгого звіту → block', lambda: row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: x |\n'), 'а' * 1600 + ' не зроблено', True)
    row('| 14.11 | **пропуск Konst** — зроблю потім |\n'); G('add', '.'); G('commit', '-qm', 'row\n\nClaude-Session: https://x/session_TESTSID')
    cases.append(('рядок без хешу вже ЗАКОМІЧЕНО цією сесією → block', verdict(D('ок')) is not None))
    G('reset', '-q', '--hard', 'HEAD~1')
    row('| 14.11 | **пропуск Konst** — НЕ ЗРОБЛЕНО: x |\n')
    oc = open_ctx(); cases.append(('open: відкритий рядок → нагадування', bool(oc) and 'НЕ ЗРОБЛЕНО' in oc))
    row(f'| 14.11 | **пропуск Konst** — правило: або «НЕ ЗРОБЛЕНО» + звіт; виправлено `{fix}`, selftest |\n'); cases.append(('open: згадка «НЕ ЗРОБЛЕНО» в лапках — не обіцянка → тиша', open_ctx() is None and verdict(D('ок')) is None))
    row(''); cases.append(('open: відкритих нема → тиша', open_ctx() is None))
    row('| 14.11 | **пропуск Konst** — без хешу |\n'); n = [stop(D('ок')) is not None for _ in range(5)]
    cases.append(('стеля: 3 зупинки поспіль, 4-та пропускає, далі знову суд', n == [True, True, True, False, True]))
    cases += selftest_claim()
    cases += selftest_seal()
    bad = 0
    for name, ok in cases:
        bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    print(f'─── promise-guard selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

m = sys.argv[1]
if m == 'selftest': sys.exit(selftest())
if m == 'tally': print(tally(re.sub(r'[^A-Za-z0-9_-]', '', sys.argv[2] if len(sys.argv) > 2 else '') or 'nosession')); sys.exit(0)
try:
    d = json.loads(os.environ.get('HOOK_IN') or '{}')
    if m == 'shadow':
        shadow(d, re.sub(r'[^A-Za-z0-9_-]', '', sys.argv[2] if len(sys.argv) > 2 else '') or 'nosession')
    elif m == 'open':
        o = open_ctx()
        if o: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': o}}, ensure_ascii=False))
    else:
        v = stop(d)
        if v: print(json.dumps({'decision': 'block', 'reason': v}, ensure_ascii=False))
except Exception:
    __import__('traceback').print_exc()
PY
