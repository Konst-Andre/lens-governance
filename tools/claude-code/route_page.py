#!/usr/bin/env python3
# живе доки: продукти Lens ведуть маршрут картою кроків (`ROUTE-1`, kernel/Lens_ROUTE-1_brief.md §5-б «Крок 5»).
# Сторінка маршруту для телефона Konst: генерується ЛИШЕ з карти — читає її `route_check.parse_map` (єдиний читач карти), руками не правиться.
#   Вигляд успадковує продукт: `<репо>/tools/route_page.json` — назва, шрифт, зібрана сторінка продукту (`probe`), з якої Chromium читає
#   обчислені токени обох тем (полотно, аврора, чорнило, скло) — копії токенів у ядрі нема. Конфігу чи Playwright нема → нейтральні токени, ⓘ.
#   Свіжість: <meta name="route-map-commit"> — останній коміт ФАЙЛА карти (не HEAD репо; рішення агента 26.11.2026, EquipLens S45).
#   Людині — людські слова (Konst 26.11.2026, EquipLens S46: «технічний шум… для агента, а не для людини»): файл «words» конфігу
#   (крок · що це · навіщо; повноту стереже route_check), групи «Зараз · Далі · Пізніше · Зроблено» (Now-Next-Later, prodpad.com, 26.11.2026),
#   «Після · Далі» словами, посилання «Крок у черзі» (рядок на GitHub) і «Бриф», кнопки «Зробити першим» · «Коментар» (копіюють повідомлення
#   в чат — бекенду нема), технічне — за «Для Claude — технічно»; хеш — у підвалі.
# Практика (26.11.2026): список кроків — `ol` з `aria-current="step"` на поточному, стан — значком і словом, не кольором
#   (docs.tabler.io/ui/components/progress-step · piccalil.li «solution 008 progress stepper»); копіювання — `clipboard.writeText` прямо
#   в обробнику тапу, https; інакше — `execCommand('copy')` (webkit.org «Async Clipboard API» · MDN Clipboard.writeText).
#   Емодзі в UI — ні (EquipLens:lens/EquipLens_MASTER_LOCK.md «Емодзі в UI»): знаки стану в тексті клітинок → inline-SVG.
# Запуск:  python3 tools/claude-code/route_page.py <репо> [--queue F] [--out ТЕКА] [--no-probe] [--inject sha|emoji|md]
#            → ТЕКА/index.html (типово /tmp/route-page-<репо>/), exit 1 — сторінка не пройшла власну перевірку
#          python3 tools/claude-code/route_page.py publish <репо>   → зібрати й видати (Worker Preview; ключ «preview» конфігу, CLOUDFLARE_API_TOKEN)
#          python3 tools/claude-code/route_page.py install <репо>   → git post-commit: коміт зачепив карту чи слова → `hook` видає у фоні
#   ROUTE-6 (Konst 26.11.2026, EquipLens S47): значок «Додому» і маніфест поруч зі сторінкою, нативне відчуття (кукбук A24/A25),
#   своє :active (у темній сіре підсвічування iOS лише гасило текст — «блимає»), тема Авто · Світла · Темна (localStorage телефона),
#   свіжість — видача після коміту карти + самоперевірка на відкритті й поверненні (кукбук A79 + visibilitychange).
#          python3 tools/claude-code/route_page.py selftest   → зуби на тимчасовому репо (без Chromium)
#          (те саме — `route_check.py page …`)
import sys, os, re, json, html, base64, subprocess, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_check as rc

# Токени, які сторінка бере з продукту (імена — CSS-змінні продукту; нема в продукті → нейтральне значення справа).
TOKENS = {
    '--canvas': ('#EFEFF3', '#0B0B0E'), '--bg-aur': ('none', 'none'),
    '--surface': ('#FFFFFF', '#17171E'), '--ink': ('#131318', '#F0F0F5'), '--ink-2': ('#54545F', '#A3A3AB'),
    '--ink-3': ('#8A8A96', '#71717A'), '--line': ('rgba(18,18,28,.085)', 'rgba(255,255,255,.075)'),
    '--accent': ('#E4005A', '#FF5C93'), '--accent-ink': ('#FFFFFF', '#22040F'),
    '--glass': ('rgba(255,255,255,.80)', 'rgba(23,23,30,.80)'), '--glass-rim': ('rgba(18,18,28,.09)', 'rgba(255,255,255,.11)'),
    '--lift': ('0 1px 1px rgba(16,16,24,.05),0 5px 14px rgba(16,16,24,.07)', '0 0 0 1px rgba(255,255,255,.055)'),
}
# Знаки, які iOS малює кольоровим емодзі (Emoji_Presentation і часті з VS16): у видимому тексті сторінки — ні. Монохромні гліфи
#   (✓ ✗ → ⟂ ≡ ★) — можна (правило продукту «inline-SVG або монохромні гліфи»); знаки стану карти все одно стають SVG.
EMOJI = re.compile('[☀-⛿✅✊✋✨❌❎❓-❕❗➕-➗➰➿'
                   '⏩-⏺▶◀⭐⭕\U0001F000-\U0001FAFF️]')
EMOJI_WORD = {'💡': 'ідея', '⚠️': 'увага', '⚠': 'увага', '🔒': 'замок', '🔄': 'триває'}   # відомі з карт — словом; решта — ✗ перевірки
STATE_WORD = {'✅': 'зроблено', '▶': 'зараз', '○': 'далі', '⏸': 'чекає Konst'}

# Значки стану — власна геометрія (коло 20×20), монохромні, колір — currentColor.
SVG = {
    '✅': '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8.5" fill="currentColor"/><path d="M6 10.4l2.6 2.6L14 7.6" fill="none" stroke="var(--surface)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    '▶': '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="10" cy="10" r="4.5" fill="currentColor"/></svg>',
    '○': '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    '⏸': '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 7v6M12 7v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
}


def git(repo, *a):
    r = subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ''


def gh_base(repo):
    """https://github.com/<власник>/<репо> з origin (проксі контейнера теж дає /<власник>/<репо>)."""
    u = git(repo, 'remote', 'get-url', 'origin')
    m = re.search(r'([\w.-]+)/([\w.-]+?)(?:\.git)?/?$', u)
    return f'https://github.com/{m.group(1)}/{m.group(2)}' if m else None


def sections(text):
    """Абзаци карти поза таблицею: «Попутно», «Чекає Konst», «Зміни маршруту» (список). Межі — ті самі, що в parse_map."""
    ls = text.splitlines()
    start = next((i for i, l in enumerate(ls) if re.match(r'\s*#{1,6}\s', l) and re.search(r'карта кроків', l, re.I)), None)
    if start is None: return {}
    lvl = len(re.match(r'\s*(#+)', ls[start]).group(1))
    end = next((j for j in range(start + 1, len(ls)) if re.match(rf'\s*#{{1,{lvl}}}\s', ls[j])), len(ls))
    out, cur = {}, None
    for l in ls[start + 1:end]:
        m = re.match(r'\s*\*\*(Попутно|Чекає Konst|Зміни маршруту)\*?\*?[^*]*?\*?\*?\s*[:(]?', l)
        if m and l.strip().startswith('**'):
            cur = m.group(1); body = re.sub(r'^\s*\*\*[^*]+\*\*\s*(\([^)]*\))?\s*:?\s*', '', l).strip()
            out[cur] = [body] if body else []; continue
        if cur and re.match(r'\s*[-*]\s+\S', l): out[cur].append(re.sub(r'^\s*[-*]\s+', '', l).strip()); continue
        if l.strip(): cur = None if not cur or l.strip().startswith('|') else cur
        else: cur = None if cur == 'Зміни маршруту' and out.get(cur) else cur
    return out


def inline(s, repo, kbase):
    """Рядок markdown → безпечний HTML: `код` (шлях до файла — посилання на GitHub), **жирне** (і через `код`), знаки стану → SVG."""
    base, codes = gh_base(repo), []

    def code(mt):
        t = mt.group(1); url = None
        m = re.match(r'(lens-governance):(.+?)(?::\d+)?$', t)
        if m and kbase: url = f'{kbase}/blob/main/{m.group(2)}'
        elif base and re.match(r'[\w./-]+\.\w+$', t) and os.path.isfile(os.path.join(repo, t)): url = f'{base}/blob/main/{t}'
        c = f'<code>{html.escape(t)}</code>'
        codes.append(f'<a href="{html.escape(url)}">{c}</a>' if url else c)
        return f'\x00{len(codes) - 1}\x00'

    e = html.escape(re.sub(r'`([^`]*)`', code, s or ''))          # код — у мітки, щоб **жирне** могло його обіймати
    e = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', e)
    for k, v in SVG.items(): e = e.replace(k, f'<span class="gi">{v}</span>')
    for k, v in EMOJI_WORD.items(): e = e.replace(k, v)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], e)


def probe_tokens(repo, cfg):
    """Обчислені токени продукту для light і dark з його зібраної сторінки (Chromium). → (dict, примітка)."""
    page = cfg.get('probe')
    if not page or not os.path.isfile(os.path.join(repo, page)): return None, 'ⓘ зібраної сторінки продукту нема — нейтральні токени'
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return None, 'ⓘ Playwright нема — нейтральні токени'
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for i, cs in enumerate(('light', 'dark')):
            pg = b.new_page(color_scheme=cs, viewport={'width': 393, 'height': 852})
            pg.goto('file://' + os.path.abspath(os.path.join(repo, page))); pg.wait_for_timeout(300)
            v = pg.evaluate('(V)=>{const s=getComputedStyle(document.documentElement);return Object.fromEntries(V.map(k=>[k,s.getPropertyValue(k).trim()]))}', list(TOKENS))
            res[cs] = {k: (v.get(k) or TOKENS[k][i]) for k in TOKENS}
        b.close()
    return res, f'токени — з {page} (обидві теми)'


def font_face(repo, cfg):
    f = cfg.get('font') or {}
    path = os.path.join(repo, f.get('file', ''))
    if not f.get('file') or not os.path.isfile(path): return '', 'system-ui'
    b64 = base64.b64encode(open(path, 'rb').read()).decode()
    fam = f.get('family', 'ProductFont')
    return (f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{b64}) format('woff2');"
            f"font-weight:{f.get('weight', '400 700')};font-display:swap}}"), f"'{fam}',system-ui"


def commits_for(repo, rid, base, n=4):
    if not base: return []
    log = git(repo, 'log', f'-{n}', '--format=%h\t%s', '-F', f'--grep=`{rid}`')
    return [l.split('\t', 1) for l in log.splitlines() if '\t' in l]


def build(repo, queue=None, probe=True, inject=None):
    """→ (html, факти для перевірки, примітки) або (None, None, [причина])."""
    qp = queue or rc.find_queue(repo)
    if qp and not os.path.isabs(qp): qp = os.path.join(repo, qp)
    if not qp or not os.path.isfile(qp): return None, None, ['черги нема']
    text = open(qp, encoding='utf-8').read(); m = rc.parse_map(text)
    if m is None or not m['rows']: return None, None, ['карти кроків нема']
    qrel = os.path.relpath(qp, repo)
    sha = git(repo, 'log', '-1', '--format=%h', '--', qrel) or '?'
    os.environ.setdefault('TZ', 'Europe/Kyiv')   # час коміту — київський (Konst), не пояс контейнера
    when = git(repo, 'log', '-1', '--format=%cd', '--date=format-local:%d.%m.%Y %H:%M', '--', qrel)
    if inject == 'sha': sha = '0000000'   # зуб: сторінка з чужим хешем
    cfgp = os.path.join(repo, 'tools', 'route_page.json')
    cfg = json.load(open(cfgp, encoding='utf-8')) if os.path.isfile(cfgp) else {}
    notes = []
    tok, note = probe_tokens(repo, cfg) if probe else (None, 'ⓘ без заміру токенів (--no-probe)')
    notes.append(note)
    if not tok: tok = {cs: {k: v[i] for k, v in TOKENS.items()} for i, cs in enumerate(('light', 'dark'))}
    ff, fam = font_face(repo, cfg)
    title = cfg.get('title') or os.path.basename(os.path.abspath(repo))
    base, kbase = gh_base(repo), cfg.get('kernel_github', 'https://github.com/Konst-Andre/lens-governance')
    rows, sec = m['rows'], sections(text)
    play = next((r for r in rows if rc.state_of(r) == '▶'), None)
    by = {r['id']: r for r in rows}
    I = lambda s: inline(s, repo, kbase)
    wp = rc.words_path(repo)
    words = rc.parse_words(wp) if wp and os.path.isfile(wp) else {}
    qlines = text.splitlines()
    lineno = {r['id']: next((i + 1 for i, l in enumerate(qlines) if re.match(rf'\s*\|\s*`{re.escape(r["id"])}`\s*\|', l)), None) for r in rows}
    BRIEF = re.compile(r'`((?:lens-governance:)?[\w./-]*?_brief\.md)`')

    def human(r):   # (що це, навіщо) — людський рядок; нема — «що» карти без коду й вказівників (⚠ дає route_check)
        if r['id'] in words: return words[r['id']]
        return re.sub(r'\s*\([^)]*\)|`[^`]*`|\*\*', '', r['what']).strip(' ·;:') or r['id'], ''

    def links(r):
        out = []
        if base and lineno.get(r['id']): out.append((f'{base}/blob/main/{qrel}#L{lineno[r["id"]]}', 'Крок у черзі'))
        b = BRIEF.search(r['what'] + ' ' + r['done'])
        if b:
            pth = b.group(1)
            if pth.startswith('lens-governance:'): out.append((f'{kbase}/blob/main/{pth.split(":", 1)[1]}', 'Бриф'))
            elif base: out.append((f'{base}/blob/main/{pth}', 'Бриф'))
        return ''.join(f'<a class="lnk" href="{html.escape(u)}">{t}</a>' for u, t in out)

    def rel(r):   # після чого · що далі — людськими словами
        prev = [x for x in rows if r['id'] in rc.ids(x['next'])]
        prev = [x for x in prev if rc.state_of(x) != '✅'] or prev   # найближчий незроблений попередник, не вся історія
        nxt = [by[i] for i in rc.ids(r['next']) if i in by]
        f = lambda xs: '; '.join(f'{html.escape(human(x)[0])} <code>{html.escape(x["id"])}</code>' for x in xs)
        s = ''
        if prev: s += f'<p class="rel"><span>Після</span>{f(prev)}</p>'
        s += f'<p class="rel"><span>Далі</span>{f(nxt) if nxt else I(r["next"])}</p>'
        return s

    def tech(r):
        cm = commits_for(repo, r['id'], base)
        cms = ''.join(f'<li><a href="{base}/commit/{h}"><code>{h}</code></a> {I(s[:90])}</li>' for h, s in cm)   # тема коміту — через inline: ✅ → SVG
        return (f'<details class="tech"><summary>Для Claude — технічно</summary><dl><dt>Що</dt><dd>{I(r["what"])}</dd>'
                f'<dt>Готово, коли</dt><dd>{I(r["done"])}</dd><dt>Далі</dt><dd>{I(r["next"])}</dd></dl>'
                + (f'<p class="lbl">Коміти з цим кроком</p><ul class="cm">{cms}</ul>' if cms else '') + '</details>')

    def buttons(r, first=True):
        w = human(r)[0]
        cmt = f"Konst про `{r['id']}` ({w}): "
        b = f'<button type="button" class="cp" data-copy="{html.escape(cmt)}">Коментар</button>'
        if first and play and r['id'] != play['id']:
            msg = f"Konst: `{r['id']}` ({w}) — зробити першим, до `{play['id']}`. Чому: "
            b = f'<button type="button" class="cp" data-copy="{html.escape(msg)}">Зробити першим</button>' + b
        return f'<div class="acts">{b}</div><p class="cpok" role="status"></p>'

    def step_li(r):
        st = rc.state_of(r) or '○'; date = rc.DATE.search(r['state'])
        word = {'✅': f'зроблено {date.group(0)}' if date else 'зроблено', '▶': 'зараз', '○': '', '⏸': 'чекає тебе'}[st]
        what, why = human(r)
        cur = ' aria-current="step"' if st == '▶' else ''
        return (f'<li class="st st-{STATE_WORD[st].split()[0]}"{cur}><details><summary>'
                f'<span class="ic">{SVG[st]}</span><span class="sx">{html.escape(what)}</span>'
                f'<span class="sid"><code>{html.escape(r["id"])}</code>{(" · " + html.escape(word)) if word else ""}</span></summary>'
                f'<div class="body">' + (f'<p class="why">{html.escape(why)}</p>' if why else '') + rel(r)
                + f'<div class="links">{links(r)}</div>' + buttons(r, st != '✅') + tech(r) + '</div></details></li>')

    # порядок: ланцюг «далі» від ▶ (Зараз · Далі 3 · Пізніше), решта — як у карті; зроблене — окремо, згорнуто
    chain, k = [], play['id'] if play else None
    while k and k in by and k not in chain:
        chain.append(k); nx = rc.ids(by[k]['next']); k = nx[0] if nx else None
    rest = [r['id'] for r in rows if r['id'] not in chain and rc.state_of(r) != '✅']
    after = [by[i] for i in chain[1:] + rest]
    done_rows = [r for r in rows if rc.state_of(r) == '✅']
    card = ''
    if play:
        what, why = human(play)
        card = (f'<section class="card" aria-current="step" aria-labelledby="now"><p class="kick" id="now"><span class="ic">{SVG["▶"]}</span>Зараз · <code>{html.escape(play["id"])}</code></p>'
                f'<h2>{html.escape(what)}</h2>' + (f'<p class="why">{html.escape(why)}</p>' if why else '') + rel(play)
                + f'<div class="links">{links(play)}</div>' + buttons(play, False) + tech(play) + '</section>')
    group = lambda head, xs, cls='': (f'<h3 class="gh">{head}</h3><ol class="steps {cls}" aria-label="{head}">' + ''.join(step_li(r) for r in xs) + '</ol>') if xs else ''
    steps = group('Далі', after[:3]) + group('Пізніше', after[3:])
    if done_rows:
        steps += (f'<details class="donegrp"><summary class="gh">Зроблено · {len(done_rows)}</summary>'
                  f'<ol class="steps">' + ''.join(step_li(r) for r in done_rows) + '</ol></details>')
    done = len(done_rows); pct = round(100 * done / len(rows))
    lst = lambda key: ''.join(f'<li>{I(x)}</li>' for x in sec.get(key, []))
    inbox = ''.join(f'<li>{I(re.sub(r"^[-*]\s+", "", x))}</li>' for x in m['inbox'])
    wait = f'<section class="blk"><h3>Чекає тебе</h3><ul>{lst("Чекає Konst")}</ul></section>' if sec.get('Чекає Konst') else ''
    extra = ''.join(f'<h4>{h}</h4><ul>{lst(k2)}</ul>' for k2, h in (('Попутно', 'Попутно — не зсуває «Зараз»'), ('Зміни маршруту', 'Зміни маршруту'))
                    if sec.get(k2))
    extra += '<h4>Вхідні</h4>' + (f'<ul>{inbox}</ul>' if inbox else '<p class="mute">Нерозібраного від тебе нема.</p>')
    blocks = wait + f'<details class="blk more"><summary>Для Claude — попутно, зміни маршруту, вхідні</summary>{extra}</details>'
    os.environ.setdefault('TZ', 'Europe/Kyiv')
    today = subprocess.run(['date', '+%d.%m.%Y'], capture_output=True, text=True).stdout.strip()
    upd = (when.replace(today + ' ', 'сьогодні о ') if when.startswith(today) else when.replace(' ', ' о ', 1)) if when else ''
    L, D = tok['light'], tok['dark']
    built = subprocess.run(['date', '+%d.%m.%Y %H:%M'], capture_output=True, text=True).stdout.strip()
    var = lambda t: ';'.join(f'{k}:{v}' for k, v in t.items())
    css = f"""{ff}
:root{{{var(L)};color-scheme:light}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{{var(D)};color-scheme:dark}}}}
:root[data-theme=dark]{{{var(D)};color-scheme:dark}}
/* нативне відчуття (кукбук A24, «Нативне відчуття» INDEX §2): без підсвічування тапу iOS — своє натискання, видиме в обох темах */
*{{-webkit-tap-highlight-color:transparent}}html{{-webkit-text-size-adjust:100%;overscroll-behavior-y:none}}
body{{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}}a,button,summary{{touch-action:manipulation}}
summary,.lnk,.cp,.seg button{{transition:background-color .12s}}summary:active,.lnk:active,.cp:active,.seg button:active{{background-color:var(--line)}}
/* розміри нижче — власні цієї сторінки (не токени продукту): кегль ≥ 13 px, поле дотику ≥ 44 px */
*{{box-sizing:border-box}}html{{background-color:var(--canvas);background-image:var(--bg-aur);background-attachment:fixed;min-height:100%}}
body{{margin:0;font-family:{fam};color:var(--ink);font-size:15px;line-height:1.45;-webkit-text-size-adjust:100%;
padding:max(18px,env(safe-area-inset-top)) 14px max(24px,env(safe-area-inset-bottom))}}
main{{max-width:560px;margin:0 auto}}
header{{margin:6px 4px 16px}}h1{{font-size:26px;font-weight:750;margin:0;letter-spacing:-.015em}}
.top{{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:6px 0 0}}.top .barl{{margin:0}}
.upd{{display:block;color:var(--ink-3);margin:2px 0 8px;background:none;border:0;padding:4px 0;font:inherit;font-size:13px;line-height:1.45;text-align:left;min-height:44px;cursor:pointer;border-radius:8px}}
.upd b{{font-weight:600;color:var(--ink-2)}}
.seg{{display:inline-flex;flex:none;padding:2px;border-radius:12px;background:var(--line)}}
.seg button{{font:inherit;font-size:13px;font-weight:600;color:var(--ink-2);background:none;border:0;border-radius:10px;min-height:36px;padding:0 10px;cursor:pointer}}
.seg button[aria-pressed=true]{{background:var(--surface);color:var(--ink);box-shadow:var(--lift)}}
.bar{{height:6px;border-radius:3px;background:var(--line);overflow:hidden}}.bar i{{display:block;height:100%;width:{pct}%;background:var(--accent);border-radius:3px}}
.barl{{color:var(--ink-2);font-size:13px;margin:6px 0 0}}
code{{font-family:inherit;font-weight:650;font-size:.92em;overflow-wrap:anywhere}}a{{color:inherit;text-underline-offset:2px}}
.card,.blk,.steps{{background:var(--glass);border:1px solid var(--glass-rim);box-shadow:var(--lift);border-radius:20px;
-webkit-backdrop-filter:blur(12px) saturate(170%);backdrop-filter:blur(12px) saturate(170%)}}
.card{{padding:16px 16px 12px;margin-bottom:18px}}.card h2{{font-size:21px;line-height:1.3;font-weight:700;margin:6px 0 6px;letter-spacing:-.01em}}
.kick{{display:flex;align-items:center;gap:6px;margin:0;color:var(--accent);font-weight:700;font-size:13px}}.kick code{{color:var(--ink-3)}}
.why{{color:var(--ink-2);margin:0 0 8px}}
.rel{{margin:4px 0;font-size:14px;color:var(--ink-2)}}.rel span{{display:inline-block;min-width:52px;color:var(--ink-3);font-size:13px;font-weight:600}}
.rel code{{color:var(--ink-3);font-weight:500}}
.links{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 4px}}
.lnk,.cp{{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:var(--r-ctl,10px);font:inherit;font-size:14px;font-weight:600}}
.lnk{{text-decoration:none;color:var(--accent);border:1px solid var(--line)}}
.acts{{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 0}}
.cp{{border:1px solid var(--glass-rim);background:var(--surface);color:var(--ink);cursor:pointer}}.cpok{{font-size:13px;color:var(--ink-3);margin:4px 0;min-height:1em}}
.ic{{display:inline-flex;width:20px;height:20px;flex:none}}.ic svg,.gi svg{{width:100%;height:100%}}
.gi{{display:inline-flex;width:1em;height:1em;vertical-align:-.12em;color:var(--ink-2)}}
.gh{{font-size:13px;font-weight:700;color:var(--ink-3);text-transform:uppercase;letter-spacing:.05em;margin:0 6px 8px}}
.steps{{list-style:none;margin:0 0 18px;padding:4px 0}}.steps>li{{border-top:1px solid var(--line)}}.steps>li:first-child{{border-top:0}}
summary{{cursor:pointer;list-style:none}}summary::-webkit-details-marker{{display:none}}
.st>details>summary{{display:grid;grid-template-columns:20px 1fr;column-gap:12px;row-gap:1px;align-items:start;min-height:44px;padding:11px 14px}}
.st .ic{{grid-row:span 2;margin-top:1px}}.sx{{font-size:15px;font-weight:600}}.sid{{color:var(--ink-3);font-size:13px}}.sid code{{font-weight:500}}
.st-зроблено .ic,.st-зроблено .sx{{color:var(--ink-3)}}.st-далі .ic{{color:var(--ink-2)}}.st-чекає .ic{{color:var(--accent)}}
.body{{padding:0 14px 12px 46px}}
details.tech{{margin-top:8px;border-top:1px solid var(--line);padding-top:6px}}details.tech>summary,details.more>summary{{color:var(--ink-3);font-size:13px;font-weight:600;min-height:36px;display:flex;align-items:center}}
dl{{margin:4px 0 8px;font-size:14px}}dt{{color:var(--ink-3);font-size:13px;font-weight:600;margin-top:6px}}dd{{margin:0;color:var(--ink-2)}}
.cm{{padding:0;list-style:none;font-size:13px;color:var(--ink-2);margin:0 0 6px}}.cm li{{margin:2px 0}}.lbl{{color:var(--ink-3);font-size:13px;font-weight:600;margin:8px 0 2px}}
.donegrp{{margin-bottom:18px}}.donegrp>summary{{min-height:44px;display:flex;align-items:center}}
.blk{{padding:12px 16px;margin-bottom:14px}}.blk h3{{font-size:13px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.05em;margin:2px 0 6px}}
.blk h4{{font-size:13px;color:var(--ink-3);margin:12px 0 4px}}.blk ul{{margin:0;padding-left:18px}}.blk li{{margin:4px 0;font-size:14px;color:var(--ink-2)}}
.mute{{color:var(--ink-3);margin:0;font-size:14px}}
footer{{color:var(--ink-3);font-size:13px;text-align:center;margin-top:8px}}"""
    js = """document.addEventListener('click',function(e){var b=e.target.closest('.cp');if(!b)return;var t=b.dataset.copy,ok=b.closest('.acts').nextElementSibling;
function done(m){ok.textContent=m;setTimeout(function(){ok.textContent=''},3000)}
var MSG='Скопійовано — встав у чат і допиши своє слово';
function old(){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.position='fixed';a.style.opacity='0';
document.body.appendChild(a);a.select();var r=false;try{r=document.execCommand('copy')}catch(_){}a.remove();
done(r?MSG:'Не вийшло скопіювати — спробуй ще раз')}
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(function(){done(MSG)},old)}else old()});
/* щипок (кукбук A25: iOS ігнорує user-scalable=no) */
['gesturestart','gesturechange','gestureend'].forEach(function(v){document.addEventListener(v,function(e){e.preventDefault()},{passive:false})});
/* тема: Авто · Світла · Темна — пам'ять у браузері телефона, сторінка — та сама для всіх */
var R=document.documentElement,TC=__TC__;
function theme(v){if(v==='light'||v==='dark')R.dataset.theme=v;else{delete R.dataset.theme;v='auto'}
document.querySelectorAll('.seg button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.th===v))});
document.querySelectorAll('meta[name=theme-color]').forEach(function(m){m.content=v==='auto'?TC[m.dataset.cs]:TC[v]})}
theme(R.dataset.theme);
document.querySelector('.seg').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
try{localStorage.setItem('route-theme',b.dataset.th)}catch(_){}theme(b.dataset.th)});
/* свіжість (кукбук A79 + visibilitychange): на відкритті, поверненні в застосунок і тапі сторінка питає сервер про новішу карту;
   є — переходить на ?v=<хеш> (інший URL обходить кеш браузера) */
var SHA=document.querySelector('meta[name=route-map-commit]').content,CK=document.getElementById('chk');
function hm(){var d=new Date();return ('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2)}
function fresh(){CK.textContent='перевіряю, чи нема новішого…';
fetch(location.pathname+'?_='+Date.now(),{cache:'no-store'}).then(function(r){return r.text()}).then(function(t){var m=t.match(/route-map-commit" content="([^"]+)"/);
if(m&&m[1]!==SHA){CK.textContent='є новіше — оновлюю';location.replace(location.pathname+'?v='+m[1]);return}CK.textContent='свіже · перевірено о '+hm()})
.catch(function(){CK.textContent='без мережі — показано останнє завантажене'})}
fresh();document.getElementById('upd').addEventListener('click',fresh);
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')fresh()});"""
    js = js.replace('__TC__', json.dumps({'light': L['--canvas'], 'dark': D['--canvas']}))
    page = f"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Маршрут"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" data-cs="light" media="(prefers-color-scheme: light)" content="{html.escape(L['--canvas'])}">
<meta name="theme-color" data-cs="dark" media="(prefers-color-scheme: dark)" content="{html.escape(D['--canvas'])}">
<link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="apple-touch-icon.png"><link rel="icon" href="icon.svg" type="image/svg+xml">
<script>try{{var t=localStorage.getItem('route-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t}}catch(_){{}}</script>
<meta name="route-map-commit" content="{html.escape(sha)}">
<meta name="route-map-file" content="{html.escape(qrel)}">
<meta name="robots" content="noindex">
<title>Маршрут {html.escape(title)}</title><style>{css}</style></head>
<body><main>
<header><h1>Маршрут {html.escape(title)}</h1>
<button type="button" class="upd" id="upd" aria-label="Перевірити, чи нема новішого">{f'Маршрут змінено <b>{html.escape(upd)}</b><br>' if upd else ''}<span id="chk" role="status">свіже на момент збирання</span></button>
<div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="{len(rows)}" aria-valuenow="{done}" aria-label="Зроблено кроків"><i></i></div>
<div class="top"><p class="barl">Зроблено {done} з {len(rows)}</p>
<div class="seg" role="group" aria-label="Тема"><button type="button" data-th="auto">Авто</button><button type="button" data-th="light">Світла</button><button type="button" data-th="dark">Темна</button></div></div></header>
{card}
{steps}
{blocks}
<footer>Сторінка оновлюється сама: Claude змінив маршрут — за хвилину тут нова версія, а відкрита сторінка підтягне її, щойно повернешся в неї. Нема змін — нема й оновлень.<br>Карта з коміту <code>{html.escape(sha)}</code> · зібрано {html.escape(built)}</footer>
</main><script>{js}</script></body></html>
"""
    if inject == 'emoji': page = page.replace('</footer>', ' ✅</footer>')   # зуб: емодзі у видимому тексті
    if inject == 'md': page = page.replace('</footer>', ' **жирне**</footer>')   # зуб: markdown не перетворено
    facts = dict(sha=git(repo, 'log', '-1', '--format=%h', '--', qrel) or '?', ids=[r['id'] for r in rows], play=play['id'] if play else None)
    facts.update(tok=tok, title=title, files=[qrel] + ([os.path.relpath(wp, repo)] if wp else []))
    return page, facts, notes


def visible_text(page):
    """Текст, який бачить людина: без <style>, <script>, <svg>, тегів і атрибутів."""
    t = re.sub(r'(?s)<(style|script|svg)\b.*?</\1>', ' ', page)
    return html.unescape(re.sub(r'<[^>]+>', ' ', t))


def verify(page, facts):
    """Власна перевірка сторінки → список ✗ (порожній — ✓)."""
    bad = []
    m = re.search(r'<meta name="route-map-commit" content="([^"]*)"', page)
    if not m or m.group(1) != facts['sha']: bad.append(f'хеш сторінки {m.group(1) if m else "—"} ≠ останній коміт карти {facts["sha"]}')
    cur = page.count('aria-current="step"')
    if cur != (1 if facts['play'] else 0): bad.append(f'кроків «зараз» на сторінці {cur}')
    for i in facts['ids']:
        if f'<code>{html.escape(i)}</code>' not in page: bad.append(f'кроку `{i}` нема на сторінці')
    em = sorted(set(EMOJI.findall(visible_text(page))))
    if em: bad.append('емодзі у видимому тексті: ' + ' '.join(em))
    if '**' in visible_text(page): bad.append('сирий markdown «**» у видимому тексті')
    return bad


def icon_svg(t, mask=False):
    """Значок «Додому»: шлях із трьох точок — зроблено · зараз · далі (мова значків сторінки), кольори — темна тема продукту.
    Повне полотно без своїх полів (iOS сам накладає маску, кукбук A3); maskable — вміст у безпечних 80 % (Android)."""
    bg, ac, ink = t['--canvas'], t['--accent'], t['--ink-2']
    g = ('<g transform="translate(256 256) scale(.8) translate(-256 -256)">' if mask else '<g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" fill="{bg}"/>'
            f'<radialGradient id="a" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="{ac}" stop-opacity=".28"/><stop offset="1" stop-color="{ac}" stop-opacity="0"/></radialGradient>'
            f'<rect width="512" height="512" fill="url(#a)"/>{g}'
            f'<path d="M146 372C146 300 256 318 256 256" fill="none" stroke="{ac}" stroke-width="18" stroke-linecap="round"/>'
            f'<path d="M256 256C256 194 366 212 366 140" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round" stroke-dasharray="2 34"/>'
            f'<circle cx="146" cy="372" r="40" fill="{ac}"/><path d="M127 373l13 13 26-27" fill="none" stroke="{bg}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="256" cy="256" r="44" fill="{bg}" stroke="{ac}" stroke-width="15"/><circle cx="256" cy="256" r="20" fill="{ac}"/>'
            f'<circle cx="366" cy="140" r="32" fill="{bg}" stroke="{ink}" stroke-width="13"/></g></svg>')


def assets(out, facts):
    """Поруч зі сторінкою: icon.svg, manifest.webmanifest і PNG (180 · 192 · 512 · 512-maskable) через Chromium. → примітки."""
    t = facts['tok']['dark']
    open(os.path.join(out, 'icon.svg'), 'w').write(icon_svg(t))
    icons = [('apple-touch-icon.png', 180, False), ('icon-192.png', 192, False), ('icon-512.png', 512, False), ('icon-512-mask.png', 512, True)]
    man = {'id': './', 'start_url': './', 'scope': './', 'name': f"Маршрут {facts['title']}", 'short_name': 'Маршрут', 'lang': 'uk',
           'display': 'standalone', 'background_color': t['--canvas'], 'theme_color': t['--canvas'],
           'icons': [{'src': f, 'sizes': f'{n}x{n}', 'type': 'image/png', 'purpose': 'maskable' if m else 'any'} for f, n, m in icons[1:]]}
    json.dump(man, open(os.path.join(out, 'manifest.webmanifest'), 'w'), ensure_ascii=False, indent=1)
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return ['ⓘ Playwright нема — PNG-значків нема (iOS покаже літеру)']
    with sync_playwright() as p:
        b = p.chromium.launch()
        for f, n, m in icons:
            pg = b.new_page(viewport={'width': n, 'height': n})
            pg.set_content(f'<body style="margin:0">{icon_svg(t, m).replace("<svg ", f"<svg width={n} height={n} ", 1)}</body>')
            pg.screenshot(path=os.path.join(out, f)); pg.close()
        b.close()
    return [f'значки: {len(icons)} PNG + icon.svg · маніфест']


def publish(repo, out=None):
    """Зібрати й видати сторінку (Worker Preview, lens-governance:tools/cloudflare/CLOUDFLARE.md §2-б): конфіг — ключ «preview»
    `tools/route_page.json` ({"worker": …, "name": …}); токен — CLOUDFLARE_API_TOKEN середовища (нема → ⓘ, нічого не робимо)."""
    cfg = json.load(open(os.path.join(repo, 'tools', 'route_page.json'), encoding='utf-8'))
    pv = cfg.get('preview') or {}
    if not pv.get('worker') or not os.environ.get('CLOUDFLARE_API_TOKEN'):
        print('ⓘ видачі нема: ключа «preview» у tools/route_page.json чи CLOUDFLARE_API_TOKEN у середовищі'); return 0
    out = out or os.path.join(tempfile.gettempdir(), 'route-page-' + os.path.basename(os.path.abspath(repo)))
    if run(repo, out=out): return 1
    d = tempfile.mkdtemp(prefix='route_pub_'); c = os.path.join(d, 'wrangler.toml')
    open(c, 'w').write(f'name = "{pv["worker"]}"\ncompatibility_date = "2026-11-01"\nworkers_dev = true\npreview_urls = true\n'
                       f'previews = {{}}\n[assets]\ndirectory = "{out}"\n')
    r = subprocess.run(['npx', '--yes', 'wrangler@4', 'preview', '--name', pv.get('name', 'route'), '--config', c], capture_output=True, text=True, cwd=d)
    shutil.rmtree(d, ignore_errors=True)
    print((r.stdout + r.stderr)[-600:]); print(f'─── видача сторінки маршруту: exit {r.returncode} ───'); return r.returncode


def changed_map(repo):
    """Чи останній коміт змінив карту чи людські слова (файли — з build)."""
    page, facts, _ = build(repo, probe=False)
    if not page: return False
    ch = set(git(repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines())
    return bool(ch & set(facts['files']))


HOOK = '#!/bin/sh\n# поставив lens-governance:tools/claude-code/route_page.py install — сторінка маршруту видається сама після коміту, що змінив карту\nexec python3 "{me}" hook "$(git rev-parse --show-toplevel)"\n'


def install(repo):
    hp = os.path.join(repo, git(repo, 'rev-parse', '--git-path', 'hooks')); os.makedirs(hp, exist_ok=True); f = os.path.join(hp, 'post-commit')
    if os.path.exists(f) and 'route_page.py' not in open(f).read(): return f'⚠ {f} уже є і не наш — не перезаписую'
    open(f, 'w').write(HOOK.format(me=os.path.abspath(__file__))); os.chmod(f, 0o755); return f'✓ post-commit: {f}'


def hook(repo):
    """git post-commit: карта змінилась → видача у фоні (коміт не чекає); журнал — <git-dir>/route-publish.log."""
    if not changed_map(repo): return 0
    log = os.path.join(repo, git(repo, 'rev-parse', '--git-dir'), 'route-publish.log')
    subprocess.Popen([sys.executable, os.path.abspath(__file__), 'publish', repo], stdout=open(log, 'w'), stderr=subprocess.STDOUT,
                     start_new_session=True)
    print('сторінка маршруту: карта змінилась — видаю у фоні (журнал — .git/route-publish.log)'); return 0


def run(repo, queue=None, out=None, probe=True, inject=None):
    page, facts, notes = build(repo, queue, probe, inject)
    if page is None: print(f'сторінка маршруту: {notes[0]} — нічого не зібрано'); return 0
    out = out or os.path.join(tempfile.gettempdir(), 'route-page-' + os.path.basename(os.path.abspath(repo)))
    os.makedirs(out, exist_ok=True); path = os.path.join(out, 'index.html')
    open(path, 'w', encoding='utf-8').write(page)
    bad = verify(page, facts)
    if not inject: notes += assets(out, facts)
    for n in notes: print(n)
    for b in bad: print(f'✗ {b}')
    print(f'─── сторінка маршруту: {path} · {len(page) // 1024} КБ · кроків {len(facts["ids"])} · ▶ {facts["play"] or "?"} · '
          f'карта {facts["sha"]} · ✗ {len(bad)} ───' + (' · ЗЛОВИВ' if inject and bad else ''))
    return 1 if bad else 0


def selftest():
    cases = [('правильна карта → ✓', None, False), ('--inject sha → ✗ хеш', 'sha', True), ('--inject emoji → ✗ емодзі', 'emoji', True),
             ('--inject md → ✗ сирий markdown', 'md', True)]
    fails = 0
    for name, inj, want in cases:
        tmp = tempfile.mkdtemp(prefix='route_page_')
        try:
            rc._repo(tmp, rc.GOOD.replace('| `A-3` | третє |', '| `A-3` | **третє з `коду` всередині** |'), rc.SUM, rc.BRIEF)
            page, facts, _ = build(tmp, probe=False, inject=inj); bad = verify(page, facts)
            ok = bool(bad) == want
            if inj is None:   # що бачить людина: картка ▶, стан словом, знак стану з клітинки — SVG, вхідні
                vt = visible_text(page)
                ok = ok and 'Зараз' in vt and 'зроблено 01.01' in vt and '✅' not in vt and 'ідея' in vt and page.count('<svg') >= 4
                # ROUTE-6: тема, своє натискання замість підсвічування iOS, «Додому», самоперевірка свіжості
                ok = ok and all(x in page for x in ('data-th="dark"', ':root[data-theme=dark]', '-webkit-tap-highlight-color:transparent',
                                                     'summary:active', 'rel="apple-touch-icon"', 'rel="manifest"', 'gesturestart', "cache:'no-store'"))
        finally: shutil.rmtree(tmp, ignore_errors=True)
        fails += not ok; print(f'{"✓" if ok else "✗"} {name}' + ('' if ok else f' — {bad}'))
    tmp = tempfile.mkdtemp(prefix='route_page_')
    try:
        rc._repo(tmp, '# Черга\n\n| id | x |\n|---|---|\n', rc.SUM, None); page, _, notes = build(tmp, probe=False)
        ok = page is None and 'карти' in notes[0]
    finally: shutil.rmtree(tmp, ignore_errors=True)
    fails += not ok; print(f'{"✓" if ok else "✗"} карти нема → нічого не збирає')
    tmp = tempfile.mkdtemp(prefix='route_page_')   # git post-commit: видає лише коли коміт зачепив карту (зуб — коміт без карти)
    try:
        rc._repo(tmp, rc.GOOD, rc.SUM, rc.BRIEF)
        cm = lambda f: (open(os.path.join(tmp, f), 'a').write('\n'), subprocess.run(['git', '-C', tmp, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qam', 'x'], capture_output=True))
        cm('sessions/X_session_summary_S1_T.md'); a1 = changed_map(tmp)
        cm('lens/X_CHERGA.md'); a2 = changed_map(tmp)
        ok = a1 is False and a2 is True
        ok = ok and install(tmp).startswith('✓') and 'route_page.py' in open(os.path.join(tmp, '.git', 'hooks', 'post-commit')).read()
        t = {k: v[1] for k, v in TOKENS.items()}; sv = icon_svg(t) + icon_svg(t, True)
        ok = ok and sv.count('<svg') == 2 and 'scale(.8)' in sv
    finally: shutil.rmtree(tmp, ignore_errors=True)
    fails += not ok; print(f'{"✓" if ok else "✗"} post-commit: коміт без карти → не видає, з картою → видає · install · значок (maskable 80 %)')
    n = len(cases) + 2; print(f'─── route_page selftest: {n - fails}/{n} ───'); return 1 if fails else 0


def main(a):
    if not a: print(__doc__ or 'route_page.py <репо> [--queue F] [--out ТЕКА] [--no-probe] [--inject sha|emoji|md] | selftest'); return 2
    if a[0] == 'selftest': return selftest()
    if a[0] in ('publish', 'install', 'hook') and len(a) == 2:
        r = {'publish': publish, 'install': install, 'hook': hook}[a[0]](os.path.abspath(a[1]))
        if isinstance(r, str): print(r); return 0
        return r
    repo = os.path.abspath(a[0]); opt, i = {}, 1
    while i < len(a):
        if a[i] in ('--queue', '--out', '--inject') and i + 1 < len(a): opt[a[i][2:]] = a[i + 1]; i += 2
        else: opt[a[i][2:]] = True; i += 1
    return run(repo, opt.get('queue'), opt.get('out'), not opt.get('no-probe'), opt.get('inject'))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
