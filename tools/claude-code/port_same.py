#!/usr/bin/env python3
# port_same.py · «порт ≡ примірка один в один» — те, що бачить людина: еталон (справжній білд + накладка примірки з обраними ставками) ⟂ порт (новий білд).
# живе доки: UI-рішення спершу міряються приміркою-накладкою (tools/claude-code/SHOTS.md), потім переносяться в код продукту.
# Звідки (AE S145, 14.11.2026, ідея Konst — AE-Simulator:docs/DECISIONS.md В-371): «щоб не я шукав, а що ж не так, бо я ж не маю заміру анімації»;
#   приймав Konst примірку, тож еталон — сама примірка, не старий білд (style_same AE — старий ≡ новий; shots_same ядра — один кадр). Судимо показ, не код:
#   місце й розмір кожного предмета (за ознакою — шлях від кореня, не ім'я класу: у накладці й порті класи різні), обчислені стилі, пікселі кореня,
#   стани (екрани, наведення) × теми, кадри руху (rAF-семплер, запитаний одразу після дії: у кожному кадрі він іде ПІСЛЯ кроку анімації).
# Світ (14.11.2026): обчислені стилі + рамки + пікселі, з наведенням і фокусом — @mizchi/vrt, StyleProof; «пікселі не бачать інший рух у
#   замороженому кадрі» — порівнювати послідовність кадрів у часі (skillsmp «visual-debug»); шрифт підмінився — вічні хибні ✗ → чекаємо
#   document.fonts.ready і звіряємо шрифти обох боків; допуски — на корінь, не одні на все (ramotion «multi-brand visual QA»).
# Запуск: python3 port_same.py <сценарій.json> [--inject] [--shots <тека>]     · самоперевірка: python3 port_same.py selftest
#   ✗ — розбіжність понад допуск; свідома розбіжність — запис "debt" {"item": <ключ або підрядок>, "prop": <властивість | @set | pix>, "why": <причина й крок, що знімає>}.
#   --inject — до порту додається "inject_css" сценарію (підкинута вада) → мусить бути ✗ (зуби).
# Сценарій (JSON біля примірки продукту; шляхи — від теки сценарію):
#   ref {site | git+path, overlay: [js…], hide: [селектор…], query} — білд-еталон (тека або коміт: git archive) + файли накладки; hide — кнопки й панель примірки (вставляються перед </body>) · port {site, query}
#   viewport [w, h] · headers {ім'я: значення} (CSP продукту) · stubs [{url, status, body}] · ready — JS-умова «застосунок готовий» · settle (мс)
#   themes [{name, js}] · states [{name, js, hover?, wait?}] · roots [{name, sel, pick, tol_px?, pix_tol?}] · props — обчислені стилі
#   tol_px (0,5) · pix_tol (середня різниця каналу 0–255, 2) · motion [{name, setup?, trigger, sample, frames, mode?: time | shape, tol: {ім'я | *: допуск}}]
#     time — кожен кадр за часом (рівні кадри); shape — пік · западина · кінець (коли перший кадр — важкий render() застосунку)
#     key (AE S146, П4 порту v7) — значення як функція ключа: "key": <ім'я поля семплера> (напр. ширина рейки); кожен кадр еталону ⟂ значення порту
#       при тій самій величині ключа (лінійно між кадрами порту) — не залежить від частоти кадрів і швидкості рушія; межі ключа (старт · кінець) ≡ еталону;
#       ключ має бути монотонним за рух (одне згортання; подвійний клік — режим shape); допуск ключа — tol[<ключ>] (типово 1)
#   inject_css — вада для --inject · debt [...]
# Межі еволюції (Konst В-371: «щоб адаптувався й покращувався»): вміє — статичні стани, наведення, рух за часом, шрифти;
#   вміє ще — рух як функція ключа (режим key, AE S146); ще ні — немонотонний ключ (подвійний клік — поки shape),
#   фокус клавіатурою (додати "focus": селектор у стан), дотик і WebKit (лише Chromium). Нове вміння — тут, з рядком selftest і зубом;
#   новий вид предмета — roots/pick, властивість — props, стан — states (сценарій продукту, прилад не чіпати).
import json, os, sys, subprocess, tempfile, shutil, threading, functools, http.server, socketserver, pathlib, io, contextlib

KEY = "const key = e => { const p = []; for (let n = e; n && n !== r; n = n.parentElement) { const i = [...n.parentElement.children].indexOf(n) + 1; p.unshift(n.tagName.toLowerCase() + ':' + i); } return p.join('>'); };"
MEAS_JS = "([root, pick, props]) => { const r = document.querySelector(root); if (!r) return null; const out = {}; " + KEY + r"""
  for (const e of r.querySelectorAll(pick)) { if (!e.getClientRects().length) continue; const b = e.getBoundingClientRect(), c = getComputedStyle(e);
    const o = { x: b.x, y: b.y, w: b.width, h: b.height }; for (const p of props) o[p] = c.getPropertyValue(p); out[key(e)] = o; }
  const rb = r.getBoundingClientRect(); out['@root'] = { x: rb.x, y: rb.y, w: rb.width, h: rb.height }; return out; }"""
SAMPLER_JS = r"""([sample, frames]) => new Promise(res => { const S = []; let n = 0, t0 = null; const f = new Function('return (' + sample + ')');
  const tick = now => { if (t0 === null) t0 = now; let v = {}; try { v = f() || {}; } catch (_) {} S.push({ t: now - t0, ...v }); if (++n < frames) requestAnimationFrame(tick); else res(S); };
  requestAnimationFrame(tick); })"""
FONTS_JS = "async () => { await document.fonts.ready; return [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight).sort().join(', '); }"


def serve(d, headers):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def end_headers(self):
            for k, v in (headers or {}).items(): self.send_header(k, v)
            super().end_headers()
    s = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=str(d))); s.daemon_threads = True
    threading.Thread(target=s.serve_forever, daemon=True).start(); return f'http://127.0.0.1:{s.server_address[1]}/'


def stage(src, base, overlay=(), css=None, tag='x'):
    t = pathlib.Path(tempfile.mkdtemp()) / tag; shutil.copytree(src, t)
    ix = (t / 'index.html').read_text(encoding='utf-8'); add = ''
    for f in overlay:
        f = (base / f).resolve(); shutil.copy(f, t / f.name); add += f'<script src="{f.name}"></script>'
    if css:
        (t / 'port_same_inject.css').write_text(css, encoding='utf-8'); ix = ix.replace('</head>', '<link rel="stylesheet" href="port_same_inject.css"></head>', 1)
    (t / 'index.html').write_text(ix.replace('</body>', add + '</body>', 1), encoding='utf-8'); return t


def git_site(base, ref):
    """ref {git: <коміт>, path: <тека в репо>} — білд-еталон з історії (git archive): еталон не «пливе», коли гілка порту змінює робочу теку."""
    import subprocess, tarfile
    top = subprocess.run(['git', '-C', str(base), 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()
    t = pathlib.Path(tempfile.mkdtemp()); data = subprocess.run(['git', '-C', top, 'archive', ref['git'], ref.get('path', 'site')], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(data)).extractall(t, filter='data'); return (t / ref.get('path', 'site')).resolve()


def num(v):
    try: return float(str(v).replace('px', ''))
    except ValueError: return None


def interp(S, t, k):
    for a, b in zip(S, S[1:]):
        if a['t'] <= t <= b['t'] and k in a and k in b:
            p = (t - a['t']) / ((b['t'] - a['t']) or 1); return a[k] + (b[k] - a[k]) * p
    return S[-1].get(k) if S and t > S[-1]['t'] else None


def pix(a, b):
    from PIL import Image, ImageChops
    A = Image.open(io.BytesIO(a)).convert('RGB'); B = Image.open(io.BytesIO(b)).convert('RGB')
    if A.size != B.size: return 255.0
    h = ImageChops.difference(A, B).histogram(); n = A.size[0] * A.size[1] * 3
    return sum((i % 256) * c for i, c in enumerate(h)) / n


def run(scn_path, inject=False, shots=None):
    from playwright.sync_api import sync_playwright
    P = pathlib.Path(scn_path).resolve(); C = json.loads(P.read_text(encoding='utf-8')); base = P.parent
    R = git_site(base, C['ref']) if C['ref'].get('git') else (base / C['ref']['site']).resolve(); T = (base / C['port']['site']).resolve()
    props = C.get('props', []); debt = C.get('debt', [])
    hide = ''.join(f'{x}{{display:none!important}}' for x in C['ref'].get('hide', []))   # кнопки й панель самої примірки — не частина показу (AE S145: кнопка «Значки» лягла на вузьку рейку)
    dref = stage(R, base, C['ref'].get('overlay', []), css=hide or None, tag='ref'); dport = stage(T, base, (), C.get('inject_css') if inject else None, tag='port')
    U = {'ref': serve(dref, C.get('headers')) + C['ref'].get('query', ''), 'port': serve(dport, C.get('headers')) + C['port'].get('query', '')}
    V = []; ok = lambda n, c, x='': V.append(('✓' if c else '✗', n, x))
    is_debt = lambda item, prop: any(d['item'] in item and d.get('prop', prop) == prop for d in debt)
    vw, vh = C.get('viewport', [1920, 1080])
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = {}; E = {'ref': [], 'port': []}; F = {}
        for side in ('ref', 'port'):
            ctx = b.new_context(viewport={'width': vw, 'height': vh}); p = ctx.new_page()
            for s in C.get('stubs', []):
                p.route(s['url'], lambda r, *_, s=s: r.fulfill(status=s.get('status', 200), headers={'access-control-allow-origin': '*'}, content_type='application/json', body=s.get('body', '{}')))
            p.on('pageerror', lambda e, side=side: E[side].append(str(e)[:160])); p.goto(U[side])
            if C.get('ready'): p.wait_for_function(C['ready'], timeout=15000)
            F[side] = p.evaluate(FONTS_JS); p.wait_for_timeout(C.get('settle', 800)); pg[side] = p
        ok('шрифти обох боків ті самі (підміна шрифту дала б вічні хибні ✗)', F['ref'] == F['port'], f"еталон [{F['ref']}] ⟂ порт [{F['port']}]" if F['ref'] != F['port'] else F['ref'][:80])
        for th in C.get('themes', [{'name': '—', 'js': ''}]):
            for st in C.get('states', [{'name': 'спокій', 'js': ''}]):
                tag = f"{st['name']} · {th['name']}"; M = {}; shot = {}
                for side, p in pg.items():
                    p.mouse.move(vw - 2, vh - 2)
                    if th['js']: p.evaluate(th['js'])
                    if st.get('js'): p.evaluate(st['js'])
                    p.wait_for_timeout(st.get('wait', 400))
                    if st.get('hover'):
                        h = p.locator(st['hover']).first
                        if h.count(): h.hover(); p.wait_for_timeout(250)
                    M[side] = {rt['name']: p.evaluate(MEAS_JS, [rt['sel'], rt['pick'], props]) for rt in C['roots']}
                    shot[side] = {rt['name']: (p.locator(rt['sel']).first.screenshot() if p.locator(rt['sel']).count() else None) for rt in C['roots']}
                for rt in C['roots']:
                    tol = rt.get('tol_px', C.get('tol_px', .5)); ptol = rt.get('pix_tol', C.get('pix_tol', 2.0))
                    a, z = M['ref'][rt['name']], M['port'][rt['name']]
                    if a is None or z is None: ok(f'{tag} · {rt["name"]}: корінь є в обох', False, f'еталон {a is not None} · порт {z is not None}'); continue
                    miss = [m for m in sorted(set(a) ^ set(z)) if not is_debt(m, '@set')]; bad = []
                    for k in sorted(set(a) & set(z)):
                        for prop, va in a[k].items():
                            vz = z[k].get(prop); na, nz = num(va), num(vz)
                            diff = (abs(na - nz) > tol) if (na is not None and nz is not None) else (str(va) != str(vz))
                            if diff and not is_debt(k, prop): bad.append(f'{k} {prop}: {va} ⟂ {vz}')
                    ok(f'{tag} · {rt["name"]}: ті самі предмети ({len(a) - 1})', not miss, ' · '.join(miss[:4]))
                    ok(f'{tag} · {rt["name"]}: місце, розмір, стилі ≡ (допуск {tol} px)', not bad, ' · '.join(bad[:3]) + (f' … ще {len(bad) - 3}' if len(bad) > 3 else ''))
                    sa, sz = shot['ref'][rt['name']], shot['port'][rt['name']]
                    if sa and sz:
                        d = pix(sa, sz); ok(f'{tag} · {rt["name"]}: пікселі ≡ (середня різниця ≤ {ptol})', d <= ptol or is_debt(rt['name'], 'pix'), f'{d:.2f}')
                        if shots:
                            pathlib.Path(shots).mkdir(parents=True, exist_ok=True)
                            for side, im in (('ref', sa), ('port', sz)):
                                (pathlib.Path(shots) / f"{rt['name']}_{st['name']}_{th['name']}_{side}.png".replace(' ', '_').replace('/', '-').replace('·', '')).write_bytes(im)
        for mo in C.get('motion', []):
            Sx = {}
            for side, p in pg.items():
                p.mouse.move(vw - 2, vh - 2)
                if mo.get('setup'): p.evaluate(mo['setup']); p.wait_for_timeout(500)
                Sx[side] = p.evaluate("([t, s, f]) => { new Function(t)(); return (" + SAMPLER_JS + ")([s, f]); }", [mo['trigger'], mo['sample'], mo.get('frames', 40)])
                p.wait_for_timeout(300)
            a, z = Sx['ref'], Sx['port']; worst = {}; ks = [k for k in (a[0] if a else {}) if k != 't']; keys = list(ks)
            if mo.get('mode') == 'shape':   # форма руху: старт · пік · западина після піку · кінець — не залежать від ривків кадрів (AE S145: перший кадр після кліку = render() застосунку 130–200 мс)
                def sig(S, k):
                    v = [fr[k] for fr in S if k in fr]
                    if not v: return {}
                    i = max(range(len(v)), key=v.__getitem__); return {'старт': v[0], 'пік': v[i], 'западина': min(v[i:]), 'кінець': v[-1]}
                for k in ks:
                    sa, sz = sig(a, k), sig(z, k)
                    for nm in sa:
                        if nm == 'старт': continue   # перший кадр — уже після кроку чи ще до: залежить від того, коли прийшов клік
                        e = abs(sa[nm] - sz.get(nm, 1e9))
                        if e >= worst.get(k, (0, 0))[0]: worst[k] = (e, nm)
                ks = []
            if mo.get('mode') == 'key':   # AE S146: значення ≡ при тій самій величині ключа — частота кадрів і швидкість рушія не важать
                kk = mo.get('key'); tk = mo.get('tol', {}).get(kk, 1)
                def curve(S):
                    c = sorted(((fr[kk], fr) for fr in S if kk in fr), key=lambda p: p[0]); return c
                ca, cz = curve(a), curve(z)
                if not ca or not cz: worst[kk] = (1e9, 'ключа нема')
                else:
                    for nm, i in (('старт', 0), ('кінець', -1)):
                        e = abs([fr[kk] for fr in a if kk in fr][i] - [fr[kk] for fr in z if kk in fr][i])
                        if e >= worst.get(kk, (0, 0))[0]: worst[kk] = (e, nm)
                    lo, hi = cz[0][0], cz[-1][0]
                    for k in [x for x in ks if x != kk]:
                        for kv, fr in ca:
                            if not (lo <= kv <= hi) or k not in fr: continue
                            vz = None
                            for (k1, f1), (k2, f2) in zip(cz, cz[1:]):
                                if k1 <= kv <= k2 and k in f1 and k in f2:
                                    q = (kv - k1) / ((k2 - k1) or 1); vz = f1[k] + (f2[k] - f1[k]) * q; break
                            if vz is None: continue
                            e = abs(fr[k] - vz)
                            if e >= worst.get(k, (0, 0))[0]: worst[k] = (e, f'{kk} {kv:.1f}')
                    if tk != mo.get('tol', {}).get('*', .5): mo.setdefault('tol', {})[kk] = tk
                ks = []
            for k in ks:
                for fr in a:
                    vz = interp(z, fr['t'], k) if k in fr else None
                    if vz is None: continue
                    e = abs(fr[k] - vz)
                    if e >= worst.get(k, (0, 0))[0]: worst[k] = (e, fr['t'])
            tl = mo.get('tol', {})
            badm = [f'{k}: {e:.3f} на {t if isinstance(t, str) else f"{t:.0f} мс"}' for k, (e, t) in worst.items() if e > tl.get(k, tl.get('*', .5)) and not is_debt(mo['name'], k)]
            moved = any(len({round(fr.get(k, 0), 3) for fr in a}) > 1 for k in keys)
            ok(f"рух «{mo['name']}»: еталон рухається (кадрів {len(a)})", moved, '' if moved else 'значення стоять — семплер не бачить руху')
            ok(f"рух «{mo['name']}»: " + ("форма ≡ еталону (пік · западина · кінець)" if mo.get('mode') == 'shape' else f"кожне значення ≡ еталону при тому самому ключі «{mo.get('key')}»" if mo.get('mode') == 'key' else "кожен кадр ≡ еталону за часом"), moved and not badm, ' · '.join(badm[:3]) or ' · '.join(f'{k} ≤ {e:.3f}' for k, (e, _) in worst.items()))
        for side in ('ref', 'port'): ok(f'помилок сторінки 0 ({"еталон" if side == "ref" else "порт"})', not E[side], '; '.join(E[side][:2]))
        b.close()
    for st, n, x in V: print(f'{st} {n}' + (f' — {x}' if x else ''))
    bad = sum(s == '✗' for s, _, _ in V)
    print(f"─── port_same «{C.get('name', P.stem)}»: ✓ {len(V) - bad} · ✗ {bad}" + (' (--inject)' if inject else '') + (f' · борг {len(debt)}' if debt else '') + ' ───')
    if not bad and not inject:   # позначка для воріт огляду (ui-review-gate ⑦, AE S145): той самий хеш диффу UI, що рахує ворота
        try:
            top = subprocess.run(['git', '-C', str(P.resolve().parent), 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip()
            hx = subprocess.run(['bash', str(pathlib.Path(__file__).resolve().parent / 'hooks/ui-review-gate.sh'), 'hash', top], capture_output=True, text=True).stdout.strip() if top else ''
            if hx in ('', 'None'): print('ⓘ змін UI в робочій теці нема — позначку не записано (ворота судять дифф до коміту: port_same — до git commit)')
            elif hx: open(f'/tmp/lens-portsame-{hx}', 'w').write(f"{C.get('name', P.stem)} ✓ {len(V)}\n"); print(f'✓ позначка port_same для диффу {hx[:8]} — ворота огляду приймуть done')
        except Exception as e: print(f'ⓘ позначку port_same не записано ({type(e).__name__})')
    return bad


def selftest():
    """Дві крихітні сторінки: «примірка» — накладка фарбує, зсуває й рухає; порт з тим самим у коді → ✓; порт без зсуву й з іншим рухом → ✗; --inject → ✗."""
    t = pathlib.Path(tempfile.mkdtemp())
    for d in ('base', 'good', 'bad'): (t / d).mkdir()
    page = lambda css, js='': f'<!doctype html><html><head><style>body{{margin:0;font:16px sans-serif}}#r{{position:absolute;left:10px;top:10px;width:200px}}#r b{{display:block;height:20px}}{css}</style></head><body><div id=r><b>a</b><b class=x>b</b></div><script>{js}</script></body></html>'
    mv = "window.go=()=>{const e=document.querySelector('#r .x');let t0=null;const f=n=>{if(t0===null)t0=n;const p=Math.min(1,(n-t0)/%d);e.style.transform='translateX('+(p*50)+'px)';if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)}"
    (t / 'base' / 'index.html').write_text(page(''), encoding='utf-8')
    (t / 'fit.js').write_text("document.head.insertAdjacentHTML('beforeend','<style>#r .x{color:rgb(200,0,0);margin-left:6px}</style>');" + mv % 200, encoding='utf-8')
    (t / 'good' / 'index.html').write_text(page('#r .x{color:rgb(200,0,0);margin-left:6px}', mv % 200), encoding='utf-8')
    (t / 'bad' / 'index.html').write_text(page('#r .x{color:rgb(200,0,0)}', mv % 90), encoding='utf-8')
    scn = lambda port: {'name': 'selftest', 'ref': {'site': 'base', 'overlay': ['fit.js']}, 'port': {'site': port}, 'viewport': [400, 200], 'settle': 100,
                        'roots': [{'name': 'r', 'sel': '#r', 'pick': 'b'}], 'props': ['color', 'margin-left'], 'states': [{'name': 's', 'js': '', 'wait': 50}],
                        'motion': [{'name': 'зсув', 'trigger': 'go()', 'sample': "{x: new DOMMatrix(getComputedStyle(document.querySelector('#r .x')).transform).m41}", 'frames': 20, 'tol': {'x': 2}}],
                        'inject_css': '#r .x{color:rgb(0,0,200)!important}'}
    for nm in ('good', 'bad'): (t / f'{nm}.json').write_text(json.dumps(scn(nm)), encoding='utf-8')
    def q(f, **k):
        with contextlib.redirect_stdout(io.StringIO()) as o: r = run(t / f, **k)
        return r, o.getvalue()
    sh = scn('good'); sh['motion'][0]['mode'] = 'shape'; sh['motion'][0]['tol'] = {'x': 1}; (t / 'shape.json').write_text(json.dumps(sh), encoding='utf-8')
    (t / 'short').mkdir(); (t / 'short' / 'index.html').write_text(page('#r .x{color:rgb(200,0,0);margin-left:6px}', (mv % 200).replace('p*50', 'p*40')), encoding='utf-8')   # рух коротший: кінець 40 ⟂ 50
    shb = scn('short'); shb['motion'][0]['mode'] = 'shape'; shb['motion'][0]['tol'] = {'x': 1}
    (t / 'shapeb.json').write_text(json.dumps(shb), encoding='utf-8')
    # режим «ключ»: значення — функція зсуву (прозорість = x/50); порт з іншою швидкістю й тією самою функцією → ✓, з іншою функцією → ✗
    mk = "window.go=()=>{const e=document.querySelector('#r .x');let t0=null;const f=n=>{if(t0===null)t0=n;const p=Math.min(1,(n-t0)/%d),x=p*50;e.style.transform='translateX('+x+'px)';e.style.opacity=String(%s);if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)}"
    (t / 'kfit.js').write_text("document.head.insertAdjacentHTML('beforeend','<style>#r .x{color:rgb(200,0,0);margin-left:6px}</style>');" + mk % (200, 'x/50'), encoding='utf-8')
    for nm, d, fx in (('kgood', 90, 'x/50'), ('kbad', 200, '(x/50)*(x/50)')):
        (t / nm).mkdir(); (t / nm / 'index.html').write_text(page('#r .x{color:rgb(200,0,0);margin-left:6px}', mk % (d, fx)), encoding='utf-8')
        kc = scn(nm); kc['ref']['overlay'] = ['kfit.js']; kc['motion'][0].update(mode='key', key='x', frames=30, tol={'x': 1, 'o': .03})
        kc['motion'][0]['sample'] = "{x: new DOMMatrix(getComputedStyle(document.querySelector('#r .x')).transform).m41, o: +getComputedStyle(document.querySelector('#r .x')).opacity}"
        (t / f'{nm}.json').write_text(json.dumps(kc), encoding='utf-8')
    g, go = q('good.json'); bd, bo = q('bad.json'); gi, gio = q('good.json', inject=True)
    xs = lambda o: [l for l in o.splitlines() if l.startswith('✗')]
    T = [('порт ≡ примірці (стилі, місце, пікселі, рух) → ✗ 0', g == 0, go),
         ('порт без зсуву → ✗ «margin-left»', any('margin-left' in l for l in xs(bo)), bo),
         ('порт з іншою швидкістю руху → ✗ «рух … кожен кадр»', any('кожен кадр' in l for l in xs(bo)), bo),
         ('--inject (вада кольору) → ✗ «color»', any('color' in l for l in xs(gio)), gio),
         ('режим «форма»: той самий рух → ✓; коротший рух (кінець 40 ⟂ 50) → ✗', not any('форма' in l for l in xs(q('shape.json')[1])) and any('форма' in l for l in xs(q('shapeb.json')[1])), ''),
         ('режим «ключ»: інша швидкість, та сама функція → ✓; інша функція прозорості → ✗', not any('ключі' in l for l in xs(q('kgood.json')[1])) and any('ключі' in l for l in xs(q('kbad.json')[1])), q('kgood.json')[1][-500:] + q('kbad.json')[1][-500:])]
    n = 0
    for name, c, out in T:
        n += c; print(('✓' if c else '✗') + ' ' + name + ('' if c else '\n' + out[-700:]))
    print(f'─── port_same selftest: {n}/{len(T)} ───'); return n == len(T)


if __name__ == '__main__':
    A = sys.argv[1:]
    if A[:1] == ['selftest']: sys.exit(0 if selftest() else 1)
    if not A: print('python3 port_same.py <сценарій.json> [--inject] [--shots <тека>] · selftest'); sys.exit(2)
    sys.exit(1 if run(A[0], inject='--inject' in A, shots=A[A.index('--shots') + 1] if '--shots' in A else None) else 0)
