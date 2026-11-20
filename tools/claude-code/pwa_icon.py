#!/usr/bin/env python3
# живе доки: продукти сімейства мають PWA з іконкою на робочому столі (кукбук A75). Дім — lens-governance:tools/claude-code/; конфіг — у репо продукту.
"""Іконка PWA «скло на аврорі» з гліфа продукту — прилад ядра (ICON-1; зразок — EquipLens S38, Konst 20.11.2026: «100% інші продукти
візьмуть — треба її в ядро»). Рецепт і чому саме так — кукбук A75 (`kernel/cookbook/Lens_iOS_cookbook_1_platform.md`), порт — «Порт у продукт покроково».

Гліф НЕ перемальовується: той самий рядок d, що малює шапка, береться рендером сторінки продукту в Chromium без мережі (селектор — з
конфігу); кольори — обчислені сторінкою для кожної теми. Кадр 390×390: фон — обчислений фон теми (аврора), гліф — шар скла (заливка-
градієнт · один рівний обідок · тінь шару · акцент — ледь-ореол), кант Liquid Glass запечено по краю маски iOS (лише any) → Chromium 1024
→ Lanczos → PNG RGB без альфи з печаткою tEXt (sha кадру). Практика «один прилад + конфіг проєкту з пресетом і перекриттями» —
@vite-pwa/assets-generator (pwa-assets.config, vite-pwa-org.netlify.app/assets-generator, 20.11.2026); джерелом у нас — не картинка, а гліф.

  python3 pwa_icon.py icons <конфіг.json> [--sheet <тека>]   — кадри (mark.svg · icon-any.html · icon-mask.html) і PNG; --sheet — аркуш
                                                              стилів на трьох шпалерах для вироку (у git — ні)
  python3 pwa_icon.py --check <конфіг.json> [--inject]       — кадри знову виходять зі сторінки ≡ закоміченим · PNG розмір / тип 2 /
                                                              печатка · маніфест (id, any і maskable окремо, розміри, фон ≡ полотну) ·
                                                              meta оболонки (A1, A55) · safe-area; --inject — 4 підкидання → «ЗЛОВИВ»
  python3 pwa_icon.py selftest                               — синтетична сторінка в тимчасовій теці: генерація → ✓ · 4 підкидання → ✗ ·
                                                              правка кадру руками → ✗ · шари поза гліфом → помилка конфігу

Конфіг (JSON у репо продукту; шляхи — від `root`, який рахується від теки конфігу):
  name · stand (сторінка, що малює гліф) · glyph (CSS-селектор svg знака) · frame (елемент, чиї фон і змінні беремо) · ink_from (селектор
  предка, чий color = лінії; нема — батько svg) · theme_js (JS перемикання теми, THEME — 'light'/'dark') · vars {g1, g2, canvas} (імена
  CSS-змінних акценту й полотна) · layers {body, rim, accent} — індекси шляхів гліфа (від'ємні — з кінця), решта — ink · style (пресет
  STYLES) · styles (перекриття пресетів) · stroke · out {brand, icons, manifest, shell, css} · seal (ключ tEXt) · template (regex мітки
  збірки в маніфесті, група 1 = шлях) · glyph_name (для шапки mark.svg) · icons (список [файл, розмір, any|mask]; нема — ICONS).
Нова роль шару (гліф інакшої будови) — правка тут разом із selftest, не обхід у продукті.
Генерація — Chromium (Playwright), Pillow; --check — stdlib + Chromium (лише для сторінки).
"""
import hashlib, json, math, os, re, shutil, struct, sys, tempfile, zlib

# габарит гліфа до сторони — A75 п.3. maskable 0.50: піврізниця діагоналі 0.354 < 0.40 — у колі безпеки r = 40 % ширини
# (web.dev «Adaptive icon support in PWAs with maskable icons», 20.11.2026)
FRAC = {'any': 0.66, 'mask': 0.50}
ICONS = [('apple-touch-icon.png', 180, 'any'), ('icon-192.png', 192, 'any'), ('icon-512.png', 512, 'any'),
         ('icon-192-mask.png', 192, 'mask'), ('icon-512-mask.png', 512, 'mask'), ('favicon-32.png', 32, 'any')]
STYLES = {  # фон · гліф: заливка (верх, низ) · обідок · лінії · акцент · тінь шару (EquipLens S38: прийнято Konst на iPhone — aurora-dark)
    'aurora-dark': dict(theme='dark', fill=('rgba(255,255,255,.26)', 'rgba(255,255,255,.08)'), rim='rgba(255,255,255,.72)',
                        ink='rgba(255,255,255,.92)', tray='acc', shadow=.25),
    'aurora-light': dict(theme='light', fill=('rgba(255,255,255,.85)', 'rgba(255,255,255,.45)'), rim='rgba(110,110,140,.45)',
                         ink=None, tray='acc', shadow=.12),
    'accent': dict(theme='light', fill=('rgba(255,255,255,.26)', 'rgba(255,255,255,.08)'), rim='rgba(255,255,255,.72)',
                   ink='rgba(255,255,255,.92)', tray='#FFFFFF', shadow=.25),
}
ICON_CSS = 390               # px сторона кадру: аврора задана в px під екран 390 — кадр тієї ж ширини
# Кант Liquid Glass: веб-кліп iOS 27 системного канту НЕ отримує (пристрій, EquipLens S38) → запікаємо по контуру маски iOS — суперeліпс
# n≈5 (точного контуру Apple не публікує: squircle.js.org · applypixels.com «The Hunt for the Squircle», 20.11.2026); лише «any».
RIM_N, RIM_W = 5.0, 0.016    # показник суперeліпса · ширина канту, частка сторони
SELF = 'lens-governance:tools/claude-code/pwa_icon.py'
INJECT = ('icon-any.html ≠', 'any maskable', 'sha кадру 0000', 'background_color #000001')


class Cfg(dict):
    def path(self, key):
        return os.path.join(self['_root'], self['out'][key]) if self['out'].get(key) else None


def load(p):
    c = Cfg(json.load(open(p, encoding='utf-8')))
    c['_root'] = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(p)), c.get('root', '.')))
    for k in ('name', 'stand', 'glyph', 'frame', 'theme_js', 'vars', 'layers', 'out', 'seal'):
        if k not in c:
            raise SystemExit(f'конфіг {p}: нема ключа «{k}» (перелік — шапка pwa_icon.py)')
    c.setdefault('style', 'aurora-dark'); c.setdefault('stroke', 1.5); c.setdefault('glyph_name', 'гліф')
    c['icons'] = [tuple(x) for x in c.get('icons', ICONS)]
    c['_styles'] = {k: dict(v, **c.get('styles', {}).get(k, {})) for k, v in STYLES.items()}
    if c['style'] not in c['_styles']:
        raise SystemExit(f'конфіг: стиль «{c["style"]}» не з {list(c["_styles"])}')
    return c


def probe_js(c):
    v = c['vars']
    ink = f"svg.closest({json.dumps(c['ink_from'])})" if c.get('ink_from') else 'svg.parentElement'
    return ("(theme) => { " + c['theme_js'].replace('THEME', 'theme') + f"""
  const sb = document.querySelector({json.dumps(c['frame'])}), svg = document.querySelector({json.dumps(c['glyph'])});
  if (!sb || !svg) return null;
  const rgb = v => {{ const t = document.createElement('i'); t.style.color = v; sb.appendChild(t);
    const c = getComputedStyle(t).color; t.remove(); return c; }};
  const cs = getComputedStyle(sb), bb = svg.getBBox();
  return {{ inner: svg.innerHTML, viewBox: svg.getAttribute('viewBox'),
    sw: getComputedStyle(svg).strokeWidth, cap: getComputedStyle(svg).strokeLinecap, join: getComputedStyle(svg).strokeLinejoin,
    ink: getComputedStyle({ink}).color, g1: rgb(cs.getPropertyValue('{v['g1']}')), g2: rgb(cs.getPropertyValue('{v['g2']}')),
    canvas: rgb(cs.getPropertyValue('{v['canvas']}')), aur: cs.backgroundImage, bgc: cs.backgroundColor,
    bbox: [bb.x, bb.y, bb.width, bb.height] }};
}}""")


def probe(c):
    """Сторінка продукту в Chromium без мережі → гліф і кольори обох тем."""
    from playwright.sync_api import sync_playwright
    html = open(os.path.join(c['_root'], c['stand']), encoding='utf-8').read()
    out, errs = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, offline=True)
        ctx.route('**/*', lambda r: r.abort())
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.set_content(html, wait_until='load')
        for t in ('light', 'dark'):
            out[t] = pg.evaluate(probe_js(c), t)
        b.close()
    if errs:
        raise SystemExit('сторінка в Chromium дала помилки JS: ' + ' | '.join(errs[:3]))
    if not all(out.values()):
        raise SystemExit(f'гліф не знайдено: селектор glyph «{c["glyph"]}» чи frame «{c["frame"]}» нічого не дав')
    return out


def hexc(col):
    m = re.match(r'rgba?\((\d+), (\d+), (\d+)', col)
    if not m:
        raise SystemExit(f'колір не розібрано: {col}')
    return '#%02X%02X%02X' % tuple(int(x) for x in m.groups())


def num(x):
    return ('%.3f' % x).rstrip('0').rstrip('.')


def mark_svg(c, pr):
    """Гліф як на сторінці (кольори — змінними теми, для порту шапки)."""
    sw = pr['sw'].replace('px', '')
    return (f'<!-- живе доки: живе знак {c["name"]} · згенеровано {SELF} icons зі сторінки {os.path.basename(c["stand"])} ({c["glyph_name"]}); руками не правити -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{pr["viewBox"]}" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="{pr["cap"]}" stroke-linejoin="{pr["join"]}">{pr["inner"]}</svg>\n')


def rim_svg():
    pts = []
    for k in range(360):
        t = 2 * math.pi * k / 360
        co, si = math.cos(t), math.sin(t)
        x, y = math.copysign(abs(co) ** (2 / RIM_N), co), math.copysign(abs(si) ** (2 / RIM_N), si)
        pts.append(f'{50 + 50 * x:.2f} {50 + 50 * y:.2f}')   # точно по краю: зовнішню половину штриха відріже маска iOS
    d = 'M' + ' L'.join(pts) + 'Z'
    return ('<svg class="rim" viewBox="0 0 100 100" preserveAspectRatio="none"><defs>'
            '<linearGradient id="rl" x1="0" y1="0" x2="1" y2="1"><stop stop-color="rgba(255,255,255,.75)"/>'
            '<stop offset=".35" stop-color="rgba(255,255,255,.14)"/><stop offset=".65" stop-color="rgba(255,255,255,.06)"/>'
            '<stop offset="1" stop-color="rgba(255,255,255,.38)"/></linearGradient>'
            '</defs>'
            f'<path d="{d}" fill="none" stroke="url(#rl)" stroke-width="{num(RIM_W * 200)}"/></svg>')


def roles(c, n):
    """Індекси шляхів → роль: body (скло: тінь, заливка, обідок) · rim (лише обідок) · accent (градієнт + ореол) · решта ink."""
    r = ['ink'] * n
    for role in ('body', 'rim', 'accent'):
        for i in c['layers'].get(role, []):
            if not -n <= i < n:
                raise SystemExit(f'конфіг layers.{role}: індекс {i} поза гліфом ({n} шляхів)')
            r[i] = role
    if 'body' not in r:
        raise SystemExit('конфіг layers: нема body — склу нема на чому лежати')
    return r


def icon_html(c, pr, kind, style):
    """Кадр 390×390: фон теми сторінки + гліф шаром скла. Кольори — літералами (окремий файл)."""
    st = c['_styles'][style]
    L = pr[st['theme']]
    sw = float(c['stroke'])
    x, y, w, h = L['bbox']
    x, y, w, h = x - sw / 2, y - sw / 2, w + sw, h + sw
    side = max(w, h) / FRAC[kind]
    vx, vy = x + w / 2 - side / 2, y + h / 2 - side / 2
    ps = re.findall(r'<path[^>]*\sd="([^"]+)"', re.sub(r'<defs>.*?</defs>', '', L['inner'], flags=re.S))
    rl = roles(c, len(ps))
    by = lambda *k: [p for p, r in zip(ps, rl) if r in k]
    cl = lambda d: d if d.rstrip()[-1:] in ('Z', 'z') else d + 'Z'
    g1, g2 = hexc(L['g1']), hexc(L['g2'])
    ink = st['ink'] or hexc(L['ink'])
    tr = 'url(#acc)' if st['tray'] == 'acc' else st['tray']
    k = f' stroke-linecap="{L["cap"]}" stroke-linejoin="{L["join"]}"'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(vx)} {num(vy)} {num(side)} {num(side)}">'
           f'<defs><linearGradient id="acc" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>'
           f'<linearGradient id="fill" x1="0" y1="0" x2=".4" y2="1"><stop stop-color="{st["fill"][0]}"/><stop offset="1" stop-color="{st["fill"][1]}"/></linearGradient>'
           '<filter id="sh" filterUnits="userSpaceOnUse" x="-20" y="-20" width="64" height="64"><feGaussianBlur stdDeviation=".9"/></filter>'
           '<filter id="glow" filterUnits="userSpaceOnUse" x="-20" y="-20" width="64" height="64"><feGaussianBlur stdDeviation=".6"/></filter></defs>'
           f'<g fill="none"{k}>'
           + ''.join(f'<path d="{cl(d)}" fill="rgba(0,0,0,{st["shadow"]})" transform="translate(0 .9)" filter="url(#sh)"/>' for d in by('body'))   # тінь шару
           + ''.join(f'<path d="{cl(d)}" fill="url(#fill)"/>' for d in by('body'))                                                             # тіло скла
           + ''.join(f'<path d="{d}" stroke="{st["rim"]}" stroke-width="{num(sw * .87)}"/>' for d in by('body', 'rim'))                       # один обідок
           + ''.join(f'<path d="{d}" stroke="{ink}" stroke-width="{num(sw)}"/>' for d in by('ink'))
           + ''.join(f'<path d="{d}" stroke="{tr}" stroke-width="{num(sw * 1.25)}" opacity=".28" filter="url(#glow)"/>' for d in by('accent'))   # ледь-ореол (S38: глоу був сильний)
           + ''.join(f'<path d="{d}" stroke="{tr}" stroke-width="{num(sw * 1.15)}"/>' for d in by('accent')) + '</g></svg>')
    bg = f'background:linear-gradient(150deg,{g1},{g2})' if style == 'accent' else f'background-color:{L["bgc"]};background-image:{L["aur"]}'
    return (f'<!-- іконка «{kind}» · стиль {style} · згенеровано {SELF} icons зі сторінки {os.path.basename(c["stand"])} (A75); руками не правити -->\n'
            f'<!doctype html><style>html,body{{margin:0}}.i{{position:relative;width:{ICON_CSS}px;height:{ICON_CSS}px;overflow:hidden;{bg}}}'
            f'.i svg{{position:absolute;inset:0;width:100%;height:100%}}</style><div class="i">{svg}{rim_svg() if kind == "any" else ""}</div>\n')


def sources(c, pr, style=None):
    style = style or c['style']
    return {'mark.svg': mark_svg(c, pr['light']), 'icon-any.html': icon_html(c, pr, 'any', style), 'icon-mask.html': icon_html(c, pr, 'mask', style)}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def raster(docs):
    """{ключ: HTML-кадр} → {ключ: RGB 1024×1024} через Chromium (кадр 390 css × масштаб 1024/390)."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import io
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for key, html in docs.items():
            pg = b.new_page(viewport={'width': ICON_CSS, 'height': ICON_CSS}, device_scale_factor=1024 / ICON_CSS)
            pg.route('**/*', lambda r: r.abort())
            pg.set_content(html)
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
            out[key] = im if im.size == (1024, 1024) else im.resize((1024, 1024), Image.LANCZOS)
            pg.close()
        b.close()
    return out


def cmd_icons(c, argv):
    from PIL import Image, PngImagePlugin
    pr = probe(c)
    brand, icons = c.path('brand'), c.path('icons')
    os.makedirs(brand, exist_ok=True); os.makedirs(icons, exist_ok=True)
    src = sources(c, pr)
    for f, t in src.items():
        open(os.path.join(brand, f), 'w', encoding='utf-8').write(t)
    big = raster({k: src['icon-' + k + '.html'] for k in FRAC})
    for f, n, k in c['icons']:
        info = PngImagePlugin.PngInfo()
        info.add_text(c['seal'], sha(src['icon-' + k + '.html']))
        big[k].resize((n, n), Image.LANCZOS).save(os.path.join(icons, f), pnginfo=info, optimize=True)
        print(f'  {os.path.relpath(os.path.join(icons, f), c["_root"])} · {n}×{n} · {os.path.getsize(os.path.join(icons, f))} Б')
    if '--sheet' in argv:
        sheet(c, pr, argv[argv.index('--sheet') + 1])
    print(f'записано {os.path.relpath(brand, c["_root"])}/ ({", ".join(src)}) і {len(c["icons"])} PNG · стиль {c["style"]}')
    return 0


def sheet(c, pr, d):
    """Аркуш вироку стилю (A75 «фон — device-рішення»): кожен стиль 180 px під маскою iOS на світлих, темних і фото-шпалерах."""
    from PIL import Image, ImageDraw
    os.makedirs(d, exist_ok=True)
    big = raster({s: icon_html(c, pr, 'any', s) for s in c['_styles']})
    n, walls, S = 180, [('#F2F2F7', 'світлі'), ('#1C1C1E', 'темні'), ('#6B8FA8', 'фото')], list(c['_styles'])
    mask = Image.new('L', (n * 4, n * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, n * 4 - 1, n * 4 - 1], radius=int(n * 4 * .225), fill=255)   # лише показ маски iOS
    mask = mask.resize((n, n), Image.LANCZOS)
    W = Image.new('RGB', (len(walls) * (len(S) * 200 + 20), 260), '#FFFFFF')
    for i, (col, _) in enumerate(walls):
        x0 = i * (len(S) * 200 + 20)
        ImageDraw.Draw(W).rectangle([x0 + 10, 10, x0 + len(S) * 200 + 10, 250], fill=col)
        for j, s in enumerate(S):
            W.paste(big[s].resize((n, n), Image.LANCZOS), (x0 + 20 + j * 200, 40), mask)
    p = os.path.join(d, 'icon_compare.png')
    W.save(p)
    print(f'  аркуш стилів: {p} (у кожній групі: ' + ' · '.join(S) + '; шпалери: ' + ' · '.join(nm for _, nm in walls) + ')')


def png_meta(path):
    """IHDR (ширина, висота, тип кольору) і tEXt — stdlib, без декодування пікселів."""
    data = open(path, 'rb').read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    i, ihdr, text = 8, None, {}
    while i < len(data):
        ln, typ = struct.unpack('>I4s', data[i:i + 8])
        body = data[i + 8:i + 8 + ln]
        if typ == b'IHDR':
            ihdr = struct.unpack('>IIBB', body[:10])
        elif typ == b'tEXt':
            k, _, v = body.partition(b'\0'); text[k.decode('latin-1')] = v.decode('latin-1')
        elif typ == b'zTXt':
            k, _, v = body.partition(b'\0'); text[k.decode('latin-1')] = zlib.decompress(v[1:]).decode('latin-1')
        i += 12 + ln
    return {'w': ihdr[0], 'h': ihdr[1], 'ctype': ihdr[3], 'text': text}


def check(c, inject=False, pr=None):
    """→ (помилки, замір). inject — 4 підкидання в пам'яті (гліф обох тем · «any maskable» · застаріла печатка · фон маніфесту)."""
    errs, rel = [], lambda p: os.path.relpath(p, c['_root'])
    pr = pr or probe(c)
    if inject:
        for t in pr:   # (1) гліф ≠ сторінці — обидві теми (іконка може бути з будь-якої; S38: підкидання лише в одну тему пропустило ваду)
            pr[t] = dict(pr[t], inner=re.sub(r'd="M(-?[\d.]+)', lambda m: f'd="M{float(m.group(1)) + .2:g}', pr[t]['inner'], count=1))
    brand, icons = c.path('brand'), c.path('icons')
    src = sources(c, pr)
    for f, t in src.items():
        p = os.path.join(brand, f)
        if not os.path.exists(p):
            errs.append(f'нема {rel(p)} — pwa_icon.py icons')
        elif open(p, encoding='utf-8').read() != t:
            errs.append(f'{rel(p)} ≠ гліфу сторінки (сторінка змінилась, прилад ядра змінився чи правили руками) — pwa_icon.py icons')
    big_any = max((x for x in c['icons'] if x[2] == 'any'), key=lambda x: x[1])[0]
    for f, n, k in c['icons']:
        p = os.path.join(icons, f)
        m = png_meta(p) if os.path.exists(p) else None
        if not m:
            errs.append(f'нема або не PNG: {rel(p)}'); continue
        if (m['w'], m['h']) != (n, n):
            errs.append(f'{rel(p)}: {m["w"]}×{m["h"]} ≠ {n}×{n}')
        if m['ctype'] != 2:
            errs.append(f'{rel(p)}: тип кольору {m["ctype"]} ≠ 2 (RGB без альфи) — iOS підкладе чорне під прозоре (A75 п.1)')
        fr = os.path.join(brand, 'icon-' + k + '.html')
        seal = sha(open(fr, encoding='utf-8').read()) if os.path.exists(fr) else '?'
        if inject and f == big_any:
            seal = '0' * 16                                           # (3) застаріла печатка
        if m['text'].get(c['seal']) != seal:
            errs.append(f'{rel(p)}: печатка {m["text"].get(c["seal"])} ≠ sha кадру {seal} — PNG застарів: pwa_icon.py icons')
    man_p, man = c.path('manifest'), None
    if man_p:
        try:
            mt = open(man_p, encoding='utf-8').read()
            if c.get('template'):
                mt = re.sub(c['template'], lambda m: m.group(1), mt)
            man = json.loads(mt)
        except (OSError, ValueError) as e:
            errs.append(f'маніфест {rel(man_p)} не прочитано: {e}')
        if man is not None and inject:
            ics = [dict(i) for i in man.get('icons', [])]
            for i in ics:
                if i.get('purpose') == 'maskable':
                    i['purpose'] = 'any maskable'; break               # (2) одна іконка на обидва призначення
            man = dict(man, icons=ics, background_color='#000001')     # (4) фон маніфесту ≠ полотну
    if man is not None:
        for k, v in (('id', './'), ('start_url', './'), ('scope', './'), ('display', 'standalone')):
            if man.get(k) != v:
                errs.append(f'маніфест: {k} = {man.get(k)!r} ≠ {v!r}' + (' — без id зміна start_url = новий застосунок (A75 п.5)' if k == 'id' else ''))
        for k in ('name', 'short_name', 'lang'):
            if not man.get(k):
                errs.append(f'маніфест: нема {k}')
        bg = hexc(pr['light']['canvas'])
        for k in ('background_color', 'theme_color'):
            if str(man.get(k, '')).upper() != bg:
                errs.append(f'маніфест: {k} {man.get(k)} ≠ {c["vars"]["canvas"]} світлої теми {bg}')
        purp = {}
        for ic in man.get('icons', []):
            pu = ic.get('purpose', 'any')
            if ' ' in pu.strip():
                errs.append(f'маніфест: purpose «{pu}» — any і maskable окремими рендерами (A75 п.3)')
            f = os.path.basename(ic.get('src', ''))
            spec = next((x for x in c['icons'] if x[0] == f), None)
            if not spec or not os.path.exists(os.path.join(os.path.dirname(man_p), ic.get('src', ''))):
                errs.append(f'маніфест: іконка {ic.get("src")} — нема файла поруч з маніфестом'); continue
            if ic.get('sizes') != f'{spec[1]}x{spec[1]}' or (spec[2] == 'mask') != (pu == 'maskable'):
                errs.append(f'маніфест: {f} sizes/purpose ≠ файлу ({spec[1]}x{spec[1]} · {spec[2]})')
            purp.setdefault(pu, set()).add(spec[1])
        for pu in ('any', 'maskable'):
            if not {192, 512} <= purp.get(pu, set()):
                errs.append(f'маніфест: для purpose «{pu}» бракує 192 і 512')
    sh_p = c.path('shell')
    if sh_p:
        sh = open(sh_p, encoding='utf-8').read()
        need = [(r'<link rel="manifest" href="[^"]*\.webmanifest[^"]*">', 'посилання на маніфест (окремий файл, A75 п.4)'),
                (r'<link rel="apple-touch-icon" href="[^"]*apple-touch-icon\.png[^"]*">', 'apple-touch-icon (iOS бере з тегу, не з маніфесту)'),
                (r'<link rel="icon" type="image/png" sizes="32x32" href="[^"]+">', 'favicon 32'),
                (r'viewport-fit=cover', 'viewport-fit=cover (без нього env(safe-area-*) = 0, A1)'),
                (r'<meta name="apple-mobile-web-app-capable" content="yes">', 'apple-mobile-web-app-capable'),
                (r'<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">', 'status-bar black-translucent'),
                (f'<meta name="theme-color" media="\\(prefers-color-scheme: light\\)" content="{hexc(pr["light"]["canvas"])}">', 'theme-color світлої ≡ полотну'),
                (f'<meta name="theme-color" media="\\(prefers-color-scheme: dark\\)" content="{hexc(pr["dark"]["canvas"])}">', 'theme-color темної ≡ полотну')]
        for rx, why in need:
            if not re.search(rx, sh):
                errs.append(f'оболонка {rel(sh_p)}: нема {why}')
    css_p = c.path('css')
    if css_p and 'min-height:calc(100% + env(safe-area-inset-top))' not in open(css_p, encoding='utf-8').read():
        errs.append(f'{rel(css_p)}: нема html{{min-height:calc(100% + env(safe-area-inset-top))}} — гола смуга знизу в standalone (A55 (1))')
    return errs, pr


def cmd_check(c, inject):
    try:
        errs, pr = check(c, inject)
    except SystemExit:
        raise
    except Exception as e:   # нема Chromium / Playwright — кажемо, не мовчимо
        print(f'  ✗ сторінку не відкрито в Chromium: {e}')
        print('НЕ ЗЛОВИВ — нема Chromium' if inject else '─── іконка: помилок 1 ✗ ───')
        return 1
    print(f'іконка {c["name"]} · {c["glyph_name"]} · штрих сторінки {pr["light"]["sw"]} · PNG {len(c["icons"])} · полотно '
          f'{hexc(pr["light"]["canvas"])} / {hexc(pr["dark"]["canvas"])} · стиль {c["style"]}' + (' · --inject' if inject else ''))
    for e in errs:
        print('  ✗ ' + e)
    if inject:
        got = [any(s in e for e in errs) for s in INJECT]
        print('ЗЛОВИВ' if all(got) else f'НЕ ЗЛОВИВ — з {len(INJECT)} підкидань спіймано {sum(got)}')
        return 1 if all(got) else 0
    print(f'─── іконка: помилок {len(errs)} ' + ('✓ ───' if not errs else '✗ ───'))
    return 1 if errs else 0


STAND_T = """<!doctype html><style>
#sbox{--g1:#5B7CFA;--g2:#B05BFA;--canvas:#EFEFF3;background-color:#EFEFF3;background-image:radial-gradient(120px 90px at 30% 20%,#C9D4FF,transparent)}
#sbox.dark{--canvas:#0F0E10;background-color:#0F0E10;background-image:radial-gradient(120px 90px at 30% 20%,#2A2F6B,transparent)}
.mk{color:#1C1C1E}#sbox.dark .mk{color:#F2F2F7}</style>
<div id="sbox"><span class="mk"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
<defs><linearGradient id="g"><stop/></linearGradient></defs><path d="M5.6 3V19Q5.6 21 7.6 21H16.4V7L12.4 3H5.6"/><path d="M12.4 3V7H16.4"/>
<path d="M8 11H14"/><path d="M8 14H12"/><path d="M4 22.4H20"/></svg></span></div>
<script>let themeMode='light';function render(){document.getElementById('sbox').className=themeMode;}</script>"""
SHELL_T = """<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#EFEFF3"><meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0F0E10">
<link rel="manifest" href="{{v:manifest.webmanifest}}"><link rel="apple-touch-icon" href="{{v:icons/apple-touch-icon.png}}">
<link rel="icon" type="image/png" sizes="32x32" href="{{v:icons/favicon-32.png}}">"""


def selftest():
    import contextlib, io
    ok = bad = 0
    def t(cond, what):
        nonlocal ok, bad
        print(('✓ ' if cond else '✗ ') + what); ok += bool(cond); bad += not cond
    cp_pr = lambda pr: json.loads(json.dumps(pr))
    d = tempfile.mkdtemp(prefix='pwa_icon_')
    try:
        os.makedirs(os.path.join(d, 'src', 'css'))
        open(os.path.join(d, 'stand.html'), 'w', encoding='utf-8').write(STAND_T)
        open(os.path.join(d, 'src', 'shell.html'), 'w', encoding='utf-8').write(SHELL_T)
        open(os.path.join(d, 'src', 'css', 'base.css'), 'w', encoding='utf-8').write('html{min-height:calc(100% + env(safe-area-inset-top))}')
        ic = [{'src': f'{{{{v:icons/{f}}}}}', 'sizes': f'{n}x{n}', 'type': 'image/png', 'purpose': 'maskable' if k == 'mask' else 'any'}
              for f, n, k in ICONS if f.startswith('icon-')]
        json.dump({'id': './', 'start_url': './', 'scope': './', 'display': 'standalone', 'name': 'Тест', 'short_name': 'Тест', 'lang': 'uk',
                   'background_color': '#EFEFF3', 'theme_color': '#EFEFF3', 'icons': ic},
                  open(os.path.join(d, 'src', 'manifest.webmanifest'), 'w', encoding='utf-8'))
        cfg = {'name': 'Тест', 'stand': 'stand.html', 'glyph': '#sbox .mk svg', 'frame': '#sbox', 'ink_from': '.mk',
               'theme_js': 'themeMode = THEME; render();', 'vars': {'g1': '--g1', 'g2': '--g2', 'canvas': '--canvas'},
               'layers': {'body': [0], 'rim': [1], 'accent': [-1]}, 'seal': 'test-src', 'template': r'\{\{v:([\w./-]+)\}\}',
               'out': {'brand': 'src/brand', 'icons': 'src/icons', 'manifest': 'src/manifest.webmanifest', 'shell': 'src/shell.html', 'css': 'src/css/base.css'}}
        cp = os.path.join(d, 'icon.json'); json.dump(cfg, open(cp, 'w', encoding='utf-8'))
        c = load(cp)
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_icons(c, [])
        ms = [png_meta(os.path.join(d, 'src', 'icons', f)) for f, _, _ in ICONS]
        t(all(m and m['ctype'] == 2 and m['text'].get('test-src') for m in ms), f'icons: {len(ICONS)} PNG, тип 2, з печаткою')
        fa = open(os.path.join(d, 'src', 'brand', 'icon-any.html'), encoding='utf-8').read()
        fm = open(os.path.join(d, 'src', 'brand', 'icon-mask.html'), encoding='utf-8').read()
        t(fa.count('fill="url(#fill)"') == 1 and fa.count('stroke="url(#acc)"') == 2 and 'class="rim"' in fa and 'class="rim"' not in fm,
          'кадр: скло лише на body, акцент з ореолом, кант лише в any')
        pr = probe(c)
        e, _ = check(c, pr=cp_pr(pr))
        t(not e, f'чисте --check: помилок {len(e)}' + (' — ' + e[0] if e else ''))
        e, _ = check(c, inject=True, pr=cp_pr(pr))
        for s in INJECT:
            t(any(s in x for x in e), f'--inject ловить «{s}»')
        p = os.path.join(d, 'src', 'brand', 'icon-mask.html')
        open(p, 'w', encoding='utf-8').write(fm.replace('.08)', '.09)', 1))
        e, _ = check(c, pr=cp_pr(pr))
        t(any('icon-mask.html ≠' in x for x in e) and any('icon-192-mask.png: печатка' in x for x in e), 'кадр, поправлений руками → ✗ кадр і печатка')
        c2 = load(cp); c2['layers'] = {'body': [0], 'accent': [9]}
        try:
            icon_html(c2, pr, 'any', 'aurora-dark'); t(False, 'шари поза гліфом → помилка конфігу')
        except SystemExit as x:
            t('поза гліфом' in str(x), 'шари поза гліфом → помилка конфігу')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'pwa_icon selftest: {ok}/{ok + bad}' + (' · є ✗' if bad else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']:
        sys.exit(selftest())
    if a[:1] == ['icons'] and len(a) > 1:
        sys.exit(cmd_icons(load(a[1]), a[2:]))
    if a[:1] == ['--check'] and len(a) > 1:
        sys.exit(cmd_check(load(a[1]), '--inject' in a))
    print(__doc__)
    sys.exit(2)
