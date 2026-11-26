#!/usr/bin/env python3
# живе доки: продукти Lens ведуть маршрут картою кроків (`ROUTE-1`, kernel/Lens_ROUTE-1_brief.md §5-б «Крок 5»).
# Сторінка маршруту для телефона Konst: генерується ЛИШЕ з карти — читає її `route_check.parse_map` (єдиний читач карти), руками не правиться.
#   Вигляд успадковує продукт: `<репо>/tools/route_page.json` — назва, шрифт, зібрана сторінка продукту (`probe`), з якої Chromium читає
#   обчислені токени обох тем (полотно, аврора, чорнило, скло) — копії токенів у ядрі нема. Конфігу чи Playwright нема → нейтральні токени, ⓘ.
#   Свіжість: <meta name="route-map-commit"> — останній коміт ФАЙЛА карти (не HEAD репо; рішення агента 26.11.2026, EquipLens S45).
# Практика (26.11.2026): список кроків — `ol` з `aria-current="step"` на поточному, стан — значком і словом, не кольором
#   (docs.tabler.io/ui/components/progress-step · piccalil.li «solution 008 progress stepper»); копіювання — `clipboard.writeText` прямо
#   в обробнику тапу, https; інакше — `execCommand('copy')` (webkit.org «Async Clipboard API» · MDN Clipboard.writeText).
#   Емодзі в UI — ні (EquipLens:lens/EquipLens_MASTER_LOCK.md «Емодзі в UI»): знаки стану в тексті клітинок → inline-SVG.
# Запуск:  python3 tools/claude-code/route_page.py <репо> [--queue F] [--out ТЕКА] [--no-probe] [--inject sha|emoji|md]
#            → ТЕКА/index.html (типово /tmp/route-page-<репо>/), exit 1 — сторінка не пройшла власну перевірку
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

    def step_li(r):
        st = rc.state_of(r) or '○'; date = rc.DATE.search(r['state'])
        word = STATE_WORD[st] + (f' {date.group(0)}' if st == '✅' and date else '')
        cm = commits_for(repo, r['id'], base)
        cms = ''.join(f'<li><a href="{base}/commit/{h}"><code>{h}</code></a> {html.escape(s[:90])}</li>' for h, s in cm)
        copy = f'{r["id"]} · {re.sub(r"[`*]", "", r["what"])[:80]}'
        cur = ' aria-current="step"' if st == '▶' else ''
        return (f'<li class="st st-{STATE_WORD[st].split()[0]}"{cur}><details><summary>'
                f'<span class="ic">{SVG[st]}</span><span class="sid"><code>{html.escape(r["id"])}</code></span>'
                f'<span class="sw">{html.escape(word)}</span><span class="sx">{I(r["what"])}</span></summary>'
                f'<dl><dt>Готово, коли</dt><dd>{I(r["done"])}</dd><dt>Далі</dt><dd>{I(r["next"])}</dd></dl>'
                + (f'<p class="lbl">Коміти з цим кроком</p><ul class="cm">{cms}</ul>' if cms else '')
                + f'<button type="button" class="cp" data-copy="{html.escape(copy)}">Скопіювати для Claude</button>'
                f'<span class="cpok" role="status"></span></details></li>')

    card = ''
    if play:
        nxt = ', '.join(f'<code>{html.escape(x)}</code>' for x in rc.ids(play['next'])) or I(play['next'])
        card = (f'<section class="card" aria-labelledby="now"><p class="kick" id="now"><span class="ic">{SVG["▶"]}</span>Зараз</p>'
                f'<h2><code>{html.escape(play["id"])}</code></h2><p class="what">{I(play["what"])}</p>'
                f'<p class="lbl">Готово, коли</p><p>{I(play["done"])}</p><p class="lbl">Далі</p><p>{nxt}</p></section>')
    done = sum(1 for r in rows if rc.state_of(r) == '✅')
    lst = lambda key: ''.join(f'<li>{I(x)}</li>' for x in sec.get(key, []))
    inbox = ''.join(f'<li>{I(re.sub(r"^[-*]\s+", "", x))}</li>' for x in m['inbox'])
    blocks = ''
    for key, head in (('Чекає Konst', 'Чекає Konst'), ('Попутно', 'Попутно — не зсуває крок «зараз»'), ('Зміни маршруту', 'Зміни маршруту')):
        if sec.get(key): blocks += f'<section class="blk"><h3>{head}</h3><ul>{lst(key)}</ul></section>'
    blocks += f'<section class="blk"><h3>Вхідні</h3>' + (f'<ul>{inbox}</ul>' if inbox else '<p class="mute">Нерозібраного від тебе нема.</p>') + '</section>'
    L, D = tok['light'], tok['dark']
    var = lambda t: ';'.join(f'{k}:{v}' for k, v in t.items())
    css = f"""{ff}
:root{{{var(L)};color-scheme:light}}
@media (prefers-color-scheme:dark){{:root{{{var(D)};color-scheme:dark}}}}
/* розміри нижче — власні цієї сторінки (не токени продукту): кегль ≥ 13 px, поле дотику ≥ 44 px */
*{{box-sizing:border-box}}html{{background-color:var(--canvas);background-image:var(--bg-aur);background-attachment:fixed;min-height:100%}}
body{{margin:0;font-family:{fam};color:var(--ink);font-size:15px;line-height:1.45;-webkit-text-size-adjust:100%;
padding:max(16px,env(safe-area-inset-top)) 14px max(24px,env(safe-area-inset-bottom))}}
main{{max-width:560px;margin:0 auto}}
header{{margin:4px 4px 14px}}h1{{font-size:22px;font-weight:700;margin:0 0 2px;letter-spacing:-.01em}}
.meta{{color:var(--ink-3);font-size:13px;margin:0}}
code{{font-family:inherit;font-weight:650;font-size:.94em;overflow-wrap:anywhere}}a{{color:inherit;text-decoration-color:var(--line);text-underline-offset:2px}}
.card,.blk,.steps{{background:var(--glass);border:1px solid var(--glass-rim);box-shadow:var(--lift);border-radius:20px;
-webkit-backdrop-filter:blur(12px) saturate(170%);backdrop-filter:blur(12px) saturate(170%)}}
.card{{padding:16px 16px 14px;margin-bottom:14px}}.card h2{{font-size:24px;margin:2px 0 4px}}.card .what{{font-size:16px;margin:0 0 10px}}
.kick{{display:flex;align-items:center;gap:6px;margin:0;color:var(--accent);font-weight:700;font-size:13px;letter-spacing:.04em;text-transform:uppercase}}
.lbl{{color:var(--ink-3);font-size:13px;font-weight:600;margin:10px 0 2px}}.card p{{margin:0}}
.ic{{display:inline-flex;width:20px;height:20px;flex:none}}.ic svg,.gi svg{{width:100%;height:100%}}
.gi{{display:inline-flex;width:1em;height:1em;vertical-align:-.12em;color:var(--ink-2)}}
.steps{{list-style:none;margin:0 0 14px;padding:6px 0}}.steps>li{{border-top:1px solid var(--line)}}.steps>li:first-child{{border-top:0}}
summary{{display:grid;grid-template-columns:20px auto 1fr;grid-template-areas:"i d w" "i x x";column-gap:10px;row-gap:2px;
align-items:center;min-height:44px;padding:10px 14px;cursor:pointer;list-style:none}}summary::-webkit-details-marker{{display:none}}
summary .ic{{grid-area:i;align-self:start;margin-top:1px}}.sid{{grid-area:d}}.sw{{grid-area:w;color:var(--ink-3);font-size:13px;justify-self:end}}
.sx{{grid-area:x;color:var(--ink-2);font-size:14px}}
.st-зроблено .ic{{color:var(--ink-3)}}.st-зроблено .sid,.st-зроблено .sx{{color:var(--ink-3)}}
.st-зараз .ic,.st-зараз .sw{{color:var(--accent)}}.st-зараз .sw{{font-weight:700}}.st-далі .ic{{color:var(--ink-2)}}
details>dl,details>.lbl,details>.cm,details>.cp,details>.cpok{{margin-left:44px;margin-right:14px}}
dl{{margin-top:0;margin-bottom:8px}}dt{{color:var(--ink-3);font-size:13px;font-weight:600;margin-top:6px}}dd{{margin:0}}
.cm{{padding:0;list-style:none;font-size:13px;color:var(--ink-2);margin-bottom:8px}}.cm li{{margin:2px 0}}
.cp{{font:inherit;font-size:14px;font-weight:600;min-height:44px;padding:0 16px;border-radius:var(--r-ctl,10px);border:1px solid var(--glass-rim);
background:var(--surface);color:var(--ink);margin-bottom:12px;cursor:pointer}}.cpok{{font-size:13px;color:var(--ink-3)}}
.blk{{padding:12px 16px;margin-bottom:14px}}.blk h3{{font-size:13px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.04em;margin:2px 0 6px}}
.blk ul{{margin:0;padding-left:18px}}.blk li{{margin:4px 0;font-size:14px}}.mute{{color:var(--ink-3);margin:0;font-size:14px}}
footer{{color:var(--ink-3);font-size:13px;text-align:center;margin-top:6px}}"""
    js = """document.addEventListener('click',function(e){var b=e.target.closest('.cp');if(!b)return;var t=b.dataset.copy,ok=b.nextElementSibling;
function done(m){ok.textContent=m;setTimeout(function(){ok.textContent=''},2500)}
function old(){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.position='fixed';a.style.opacity='0';
document.body.appendChild(a);a.select();var r=false;try{r=document.execCommand('copy')}catch(_){}a.remove();
done(r?'Скопійовано — встав у чат і допиши своє слово':'Не вийшло скопіювати — виділи назву кроку пальцем')}
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(function(){done('Скопійовано — встав у чат і допиши своє слово')},old)}else old()});"""
    page = f"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="route-map-commit" content="{html.escape(sha)}">
<meta name="route-map-file" content="{html.escape(qrel)}">
<meta name="robots" content="noindex">
<title>Маршрут {html.escape(title)}</title><style>{css}</style></head>
<body><main>
<header><h1>Маршрут {html.escape(title)}</h1><p class="meta">карта з коміту <code>{html.escape(sha)}</code>{(' · ' + html.escape(when)) if when else ''} · зроблено {done} з {len(rows)} кроків</p></header>
{card}
<ol class="steps" aria-label="Усі кроки маршруту">{''.join(step_li(r) for r in rows)}</ol>
{blocks}
<footer>Сторінку збирає машина з карти кроків — руками не правиться.</footer>
</main><script>{js}</script></body></html>
"""
    if inject == 'emoji': page = page.replace('</footer>', ' ✅</footer>')   # зуб: емодзі у видимому тексті
    if inject == 'md': page = page.replace('</footer>', ' **жирне**</footer>')   # зуб: markdown не перетворено
    facts = dict(sha=git(repo, 'log', '-1', '--format=%h', '--', qrel) or '?', ids=[r['id'] for r in rows], play=play['id'] if play else None)
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


def run(repo, queue=None, out=None, probe=True, inject=None):
    page, facts, notes = build(repo, queue, probe, inject)
    if page is None: print(f'сторінка маршруту: {notes[0]} — нічого не зібрано'); return 0
    out = out or os.path.join(tempfile.gettempdir(), 'route-page-' + os.path.basename(os.path.abspath(repo)))
    os.makedirs(out, exist_ok=True); path = os.path.join(out, 'index.html')
    open(path, 'w', encoding='utf-8').write(page)
    bad = verify(page, facts)
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
                ok = ok and 'Зараз' in vt and 'зроблено 01.01' in vt and '✅' not in vt and 'ідея' in vt and page.count('<svg') >= 5
        finally: shutil.rmtree(tmp, ignore_errors=True)
        fails += not ok; print(f'{"✓" if ok else "✗"} {name}' + ('' if ok else f' — {bad}'))
    tmp = tempfile.mkdtemp(prefix='route_page_')
    try:
        rc._repo(tmp, '# Черга\n\n| id | x |\n|---|---|\n', rc.SUM, None); page, _, notes = build(tmp, probe=False)
        ok = page is None and 'карти' in notes[0]
    finally: shutil.rmtree(tmp, ignore_errors=True)
    fails += not ok; print(f'{"✓" if ok else "✗"} карти нема → нічого не збирає')
    n = len(cases) + 1; print(f'─── route_page selftest: {n - fails}/{n} ───'); return 1 if fails else 0


def main(a):
    if not a: print(__doc__ or 'route_page.py <репо> [--queue F] [--out ТЕКА] [--no-probe] [--inject sha|emoji|md] | selftest'); return 2
    if a[0] == 'selftest': return selftest()
    repo = os.path.abspath(a[0]); opt, i = {}, 1
    while i < len(a):
        if a[i] in ('--queue', '--out', '--inject') and i + 1 < len(a): opt[a[i][2:]] = a[i + 1]; i += 2
        else: opt[a[i][2:]] = True; i += 1
    return run(repo, opt.get('queue'), opt.get('out'), not opt.get('no-probe'), opt.get('inject'))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
