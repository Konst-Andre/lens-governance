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
                                                              стилів × манер (рядок на манеру) на трьох шпалерах для вироку (у git — ні)
  python3 pwa_icon.py --check <конфіг.json> [--inject]       — кадри знову виходять зі сторінки ≡ закоміченим · PNG розмір / тип 2 /
                                                              печатка · маніфест (id, any і maskable окремо, розміри, фон ≡ полотну) ·
                                                              meta оболонки (A1, A55) · safe-area; --inject — 4 підкидання → «ЗЛОВИВ»
  python3 pwa_icon.py selftest                               — синтетична сторінка в тимчасовій теці: генерація → ✓ · 4 підкидання → ✗ ·
                                                              правка кадру руками → ✗ · шари поза гліфом → помилка конфігу

Конфіг (JSON у репо продукту; шляхи — від `root`, який рахується від теки конфігу):
  name · stand (сторінка, що малює гліф) · glyph (CSS-селектор svg знака) · frame (елемент, чиї фон і змінні беремо) · ink_from (селектор
  предка, чий color = лінії; нема — батько svg) · theme_js (JS перемикання теми, THEME — 'light'/'dark') · vars {g1, g2, canvas} (імена
  CSS-змінних акценту й полотна) · layers {body, rim, accent, fill, fillacc} — індекси фігур гліфа (path · rect · circle; від'ємні — з кінця), решта — ink · style (пресет
  STYLES) · styles (перекриття пресетів) · look (манера: glass-1 — типова, як було · glass-2026 — блиск по краю шару, ICON-2) · bg (свій
  фон літералом CSS, коли сторінка аврори не має) · frac {any, mask} (частка гліфа до сторони; нема — FRAC) · deco (шар-прикраса, ICON-3:
  {"kind": "magnifier", "cx", "cy", "r", "deg", "len", "w"} — лінза зі склом, ручка-циліндр і муфта в одиницях кадру 100; гліф — у центрі
  лінзи; тон ручки — від теми стилю, "tone" перекриває; "colors" {ring, dot, handle, ferrule} — точні кольори замість виведених з акценту;
  "shadow" — тінь гліфа) · stroke · out {brand, icons, manifest, shell, css} · seal (ключ tEXt) · template (regex мітки
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
    if c.get('look', 'glass-1') not in LOOKS:
        raise SystemExit(f'конфіг: манера «{c["look"]}» не з {list(LOOKS)}')
    deco_check(c)
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
    for role in ('body', 'rim', 'accent', 'fill', 'fillacc'):   # fill · fillacc — суцільна фігура кольором лінії / акценту (ICON-2)
        for i in c['layers'].get(role, []):
            if not -n <= i < n:
                raise SystemExit(f'конфіг layers.{role}: індекс {i} поза гліфом ({n} шляхів)')
            r[i] = role
    if 'body' not in r and c.get('look', 'glass-1') != 'glass-2026':   # glass-2026: скло — блиск і тінь кожного шару, тіло не обовʼязкове
        raise SystemExit('конфіг layers: нема body — склу нема на чому лежати')
    return r


LOOKS = ('glass-1', 'glass-2026')   # манера (ICON-2, Konst 26.11.2026: «не забирати те, що вже вміє, лише доповнювати… перемикатися між пресетами»)
# glass-1 — як було (типова: значки EquipLens і Маршруту не міняються, зуб — --check). glass-2026 — направлений блиск по краю кожного шару
# (світло згори-зліва; Apple Icon Composer: specular по краю шару, developer.apple.com/icon-composer, 26.11.2026), тінь під кожним шаром,
# акцент — градієнт зі світлим верхом. Практика «старий пресет лишається, новий обирають явно» — @vite-pwa/assets-generator minimal → minimal-2023.


def shapes(inner):
    """Шляхи гліфа по порядку появи: path — як є; rect · circle → path (гліф із фігур — QR Lens, ICON-2). Як usvg (docs.rs usvg shapes.rs,
    26.11.2026): радіус обрізано до половини сторони, ry = rx, коло — двома півдугами."""
    inner = re.sub(r'<defs>.*?</defs>', '', inner, flags=re.S); out = []
    for m in re.finditer(r'<(path|rect|circle)\b([^>]*)>', inner):
        tag, a = m.group(1), m.group(2)
        def g(k, d=0.0):
            v = re.search(r'\s' + k + r'="([^"]+)"', a)
            return float(v.group(1)) if v else d
        if tag == 'path':
            v = re.search(r'\sd="([^"]+)"', a)
            if v: out.append(v.group(1))
        elif tag == 'rect':
            x, y, w, h = g('x'), g('y'), g('width'), g('height'); r = min(g('rx', g('ry')), w / 2, h / 2)
            out.append(f'M{num(x + r)} {num(y)}H{num(x + w - r)}A{num(r)} {num(r)} 0 0 1 {num(x + w)} {num(y + r)}V{num(y + h - r)}'
                       f'A{num(r)} {num(r)} 0 0 1 {num(x + w - r)} {num(y + h)}H{num(x + r)}A{num(r)} {num(r)} 0 0 1 {num(x)} {num(y + h - r)}'
                       f'V{num(y + r)}A{num(r)} {num(r)} 0 0 1 {num(x + r)} {num(y)}Z')
        else:
            cx, cy, r = g('cx'), g('cy'), g('r')
            out.append(f'M{num(cx - r)} {num(cy)}A{num(r)} {num(r)} 0 1 0 {num(cx + r)} {num(cy)}A{num(r)} {num(r)} 0 1 0 {num(cx - r)} {num(cy)}Z')
    return out


def mix(h, w, t):
    a, b = [int(h[i:i + 2], 16) for i in (1, 3, 5)], [int(w[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02X%02X%02X' % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def lift(h, light):
    """Світліший тон того самого кольору без вицвітання: світлота в HLS → light, насиченість не нижча за 0,6 (mix із білим сірить — ряд 3 QR, 26.11)."""
    import colorsys
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    hh, _, ss = colorsys.rgb_to_hls(r, g, b)
    return '#%02X%02X%02X' % tuple(round(x * 255) for x in colorsys.hls_to_rgb(hh, light, max(ss, .6)))


DECO = ('magnifier',)   # шар-прикраса (ICON-3, Konst 26.11.2026: «навчити генератор шару-прикраси… хоча б на 90 %, потім доробити руками»)
# Зразок — ручний значок 12 QR Lens (QR-Lens:lens/shots/QRL-22_ikonka/gen_ikonka_r3.py): тоноване скло · тінь під обідком · відблиск-
# півмісяць · ручка-циліндр (градієнт поперек осі) · муфта свого металу (Konst 26.11: на темному «розчиняється»). Кольори — від акценту.
# Практика: Icon Composer — до 4 груп, скло · тінь · блиск — на рівні групи; тінь на білому — кольорова, на темному — нейтральна
# (developer.apple.com/videos/play/wwdc2026/8012, 26.11.2026) → прикраса — окремі групи під і над гліфом, тон — від теми. Заломлення — ні:
# у SVG дороге (feDisplacementMap) і ріже дрібний гліф.


def frac(c, kind):
    """Частка гліфа до сторони: конфіг frac → FRAC; з прикрасою — гліф у лінзі (0,53 діаметра), mask — уся композиція × FRAC mask / any."""
    f = dict(FRAC, **c.get('frac', {}))
    if c.get('deco') and 'any' not in c.get('frac', {}):
        f['any'] = c['deco']['r'] * 2 / 100 * .53
    if c.get('deco') and 'mask' not in c.get('frac', {}):
        f['mask'] = f['any'] * FRAC['mask'] / FRAC['any']
    return f[kind]


def deco_check(c):
    """Прикраса не закриває гліф: півдіагональ гліфа (частка any) — у внутрішньому колі лінзи з зазором (премортем ICON-3)."""
    d = c.get('deco')
    if not d:
        return
    if d.get('kind', 'magnifier') not in DECO:
        raise SystemExit(f'конфіг deco: вид «{d.get("kind")}» не з {list(DECO)}')
    for k in ('cx', 'cy', 'r'):
        if k not in d:
            raise SystemExit(f'конфіг deco: нема «{k}»')
    half, inner = frac(c, 'any') * 100 * math.sqrt(2) / 2, d['r'] - 2.6 - 1.9
    if half > inner:
        raise SystemExit(f'конфіг deco: гліф не влазить у лінзу — півдіагональ {half:.1f} > внутрішнього кола {inner:.1f} (менше frac.any чи більше r)')


def deco_svg(c, L, st, kind):
    """→ (під гліфом, над гліфом): дві SVG 0..100 (mask — стиснуто до центру). id з префіксом d — у кадрі три SVG в одному документі."""
    d = c['deco']
    k = frac(c, 'mask') / frac(c, 'any') if kind == 'mask' else 1
    vb = f'{num(50 - 50 / k)} {num(50 - 50 / k)} {num(100 / k)} {num(100 / k)}'
    cx, cy, r = d['cx'], d['cy'], d['r']
    g1, g2 = hexc(L['g1']), hexc(L['g2'])
    light = d.get('tone', st['theme']) == 'light'
    a = math.radians(d.get('deg', 45)); ca, sa = math.cos(a), math.sin(a)
    w, ln = d.get('w', 10), d.get('len', 15 * math.sqrt(2))
    x1, y1 = cx + (r - 4) * ca, cy + (r - 4) * sa
    x2, y2 = cx + (r + .5 + ln) * ca, cy + (r + .5 + ln) * sa
    px, py = -sa * w / 2, ca * w / 2

    def cap(ax, ay, bx, by, m):
        return (f'M{num(ax + px * m)} {num(ay + py * m)}L{num(bx + px * m)} {num(by + py * m)}A{num(w / 2 * m)} {num(w / 2 * m)} 0 0 0 {num(bx - px * m)} {num(by - py * m)}'
                f'L{num(ax - px * m)} {num(ay - py * m)}A{num(w / 2 * m)} {num(w / 2 * m)} 0 0 0 {num(ax + px * m)} {num(ay + py * m)}Z')

    def lg(i, m, stops):
        return (f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{num(x1 + px * m)}" y1="{num(y1 + py * m)}" x2="{num(x1 - px * m)}" y2="{num(y1 - py * m)}">'
                + ''.join(f'<stop offset="{o}" stop-color="{col}"/>' for o, col in stops) + '</linearGradient>')
    if light:   # світлий фон: ручка й муфта — тони акценту (значок 15)
        body = [(0, lift(g2, .24)), (.3, lift(g1, .6)), (.55, g1), (1, lift(g2, .2))]
        ferr = [(0, lift(g2, .11)), (.28, lift(g1, .62)), (.5, g1), (1, lift(g2, .09))]
    else:       # темний фон: ручка — світла, муфта — свій темніший метал (значок 12)
        body = [(0, mix('#888888', g1, .2)), (.3, '#FFFFFF'), (.55, mix('#FFFFFF', g1, .12)), (1, mix('#777777', g1, .2))]
        ferr = [(0, mix('#333333', g1, .25)), (.28, mix('#FFFFFF', g1, .1)), (.5, mix('#AAAAAA', g1, .25)), (1, mix('#262626', g1, .25))]
    co = d.get('colors', {})   # точні кольори продукту (QR Lens — літерали ручного 12); нема — від акценту
    body = list(zip((0, .3, .55, 1), co['handle'])) if 'handle' in co else body
    ferr = list(zip((0, .28, .5, 1), co['ferrule'])) if 'ferrule' in co else ferr
    fx, fy = x1 + (x2 - x1) * .38, y1 + (y2 - y1) * .38
    ro = num(r + 1.6)
    defs = ('<defs>'
            f'<radialGradient id="dtint" cx=".3" cy=".26" r=".9"><stop stop-color="{lift(g1, .94)}" stop-opacity=".42"/>'
            f'<stop offset=".42" stop-color="{lift(g1, .69)}" stop-opacity=".2"/><stop offset=".8" stop-color="{g1}" stop-opacity=".16"/>'
            f'<stop offset="1" stop-color="{mix(g2, "#000000", .85)}" stop-opacity=".5"/></radialGradient>'
            '<linearGradient id="dsp" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff" stop-opacity=".98"/><stop offset=".5" stop-color="#fff" stop-opacity=".5"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity=".18"/></linearGradient>'
            '<filter id="dsh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.8"/></filter>'
            '<filter id="dins" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6"/></filter>'
            + lg('dcy', 1, body) + lg('dfe', 1.1, ferr)
            + f'<clipPath id="dout"><path clip-rule="evenodd" d="M-10 -10H110V110H-10Z M{num(cx + r + 1.6)} {num(cy)}A{ro} {ro} 0 1 0 {num(cx - r - 1.6)} {num(cy)}'
              f'A{ro} {ro} 0 1 0 {num(cx + r + 1.6)} {num(cy)}Z"/></clipPath></defs>')
    hb, fb = cap(x1, y1, x2, y2, 1), cap(x1, y1, fx, fy, 1.08)
    C = f'cx="{num(cx)}" cy="{num(cy)}"'
    under = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{defs}<g clip-path="url(#dout)">'
             f'<path d="{hb}" fill="#000" opacity=".35" filter="url(#dsh)" transform="translate(1.2 2.2)"/><path d="{hb}" fill="url(#dcy)"/>'   # ручка-циліндр
             f'<path d="{fb}" fill="url(#dfe)"/>'                                                                                                 # муфта
             f'<path d="M{num(fx + px * 1.08)} {num(fy + py * 1.08)}L{num(fx - px * 1.08)} {num(fy - py * 1.08)}" stroke="#000" stroke-opacity=".45" stroke-width=".7"/>'
             f'<path d="{fb}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width=".5"/></g>'
             f'<circle {C} r="{num(r + 2)}" fill="#000" opacity=".3" filter="url(#dsh)" transform="translate(0 2)"/>'
             f'<circle {C} r="{num(r)}" fill="url(#dtint)"/></svg>')                                                                              # тоноване скло
    top = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
           f'<circle {C} r="{num(r - 2.6)}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="3.2" filter="url(#dins)" transform="translate(.6 .9)"/>'   # тінь під обідком
           f'<path d="M{num(cx - r * .78)} {num(cy + r * .05)}A{num(r * .8)} {num(r * .8)} 0 0 1 {num(cx + r * .05)} {num(cy - r * .78)}'
           f'A{num(r * .92)} {num(r * .92)} 0 0 0 {num(cx - r * .78)} {num(cy + r * .05)}Z" fill="#fff" opacity=".1"/>'                             # півмісяць
           f'<circle {C} r="{num(r)}" fill="none" stroke="url(#dsp)" stroke-width="3.8"/>'
           f'<circle {C} r="{num(r - 2.5)}" fill="none" stroke="#000" stroke-opacity=".22" stroke-width=".7"/>'
           f'<path d="M{num(cx - r * .72)} {num(cy - r * .34)}A{num(r * .8)} {num(r * .8)} 0 0 1 {num(cx - r * .3)} {num(cy - r * .74)}" fill="none" stroke="#fff"'
           ' stroke-opacity=".85" stroke-width="1.7" stroke-linecap="round"/>'
           f'<path d="M{num(cx + r * .5)} {num(cy + r * .62)}A{num(r * .82)} {num(r * .82)} 0 0 0 {num(cx + r * .66)} {num(cy + r * .44)}" fill="none" stroke="#fff"'
           ' stroke-opacity=".35" stroke-width="1.1" stroke-linecap="round"/></svg>')
    return under, top

def icon_html(c, pr, kind, style):
    """Кадр 390×390: фон теми сторінки + гліф шаром скла. Кольори — літералами (окремий файл)."""
    st = c['_styles'][style]
    L = pr[st['theme']]
    sw = float(c['stroke'])
    x, y, w, h = L['bbox']
    x, y, w, h = x - sw / 2, y - sw / 2, w + sw, h + sw
    side = max(w, h) / frac(c, kind)
    vx, vy = x + w / 2 - side / 2, y + h / 2 - side / 2
    if c.get('deco'):   # гліф — у центрі лінзи (mask — композиція стиснута до центру кадру)
        k = frac(c, 'mask') / frac(c, 'any') if kind == 'mask' else 1
        vx, vy = x + w / 2 - side * (.5 + (c['deco']['cx'] / 100 - .5) * k), y + h / 2 - side * (.5 + (c['deco']['cy'] / 100 - .5) * k)
    ps = shapes(L['inner']); new = c.get('look', 'glass-1') == 'glass-2026'
    dk = bool(c.get('deco'))
    rl = roles(c, len(ps))
    by = lambda *k: [p for p, r in zip(ps, rl) if r in k]
    cl = lambda d: d if d.rstrip()[-1:] in ('Z', 'z') else d + 'Z'
    g1, g2 = hexc(L['g1']), hexc(L['g2'])
    ink = st['ink'] or hexc(L['ink'])
    tr = 'url(#acc)' if st['tray'] == 'acc' else st['tray']
    k = f' stroke-linecap="{L["cap"]}" stroke-linejoin="{L["join"]}"'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(vx)} {num(vy)} {num(side)} {num(side)}">'
           + (f'<defs><linearGradient id="acc" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{lift(g1, .7)}"/><stop offset=".45" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>'
              '<linearGradient id="spec" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff" stop-opacity=".95"/><stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
              if new else f'<defs><linearGradient id="acc" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>')
           + f'<linearGradient id="fill" x1="0" y1="0" x2=".4" y2="1"><stop stop-color="{st["fill"][0]}"/><stop offset="1" stop-color="{st["fill"][1]}"/></linearGradient>'
           '<filter id="sh" filterUnits="userSpaceOnUse" x="-20" y="-20" width="64" height="64"><feGaussianBlur stdDeviation=".9"/></filter>'
           '<filter id="glow" filterUnits="userSpaceOnUse" x="-20" y="-20" width="64" height="64"><feGaussianBlur stdDeviation=".6"/></filter></defs>'
           f'<g fill="none"{k}>'
           + ''.join(f'<path d="{cl(d)}" fill="rgba(0,0,0,{st["shadow"]})" transform="translate(0 .9)" filter="url(#sh)"/>' for d in by('body'))   # тінь шару
           + (''.join(f'<path d="{d}" stroke="rgba(0,0,0,{st["shadow"]})" stroke-width="{num(sw * 1.15)}" transform="translate(0 .9)" filter="url(#sh)"/>' for d in by('rim', 'accent', 'ink'))
              + ''.join(f'<path d="{cl(d)}" fill="rgba(0,0,0,{st["shadow"]})" transform="translate(0 .9)" filter="url(#sh)"/>' for d in by('fill', 'fillacc')) if new else '')
           + ''.join(f'<path d="{cl(d)}" fill="url(#fill)"/>' for d in by('body'))                                                             # тіло скла
           + ''.join(f'<path d="{d}" stroke="{st["rim"]}" stroke-width="{num(sw * .87)}"/>' for d in by('body', 'rim'))                       # один обідок
           + ''.join(f'<path d="{d}" stroke="{ink}" stroke-width="{num(sw)}"/>' for d in by('ink'))
           + ''.join(f'<path d="{d}" stroke="{tr}" stroke-width="{num(sw * 1.25)}" opacity=".28" filter="url(#glow)"/>' for d in by('accent'))   # ледь-ореол (S38: глоу був сильний)
           + ''.join(f'<path d="{d}" stroke="{tr}" stroke-width="{num(sw * (1 if new else 1.15))}"/>' for d in by('accent'))   # glass-2026: штрих гліфа дослівно
           + ''.join(f'<path d="{cl(d)}" fill="{ink}"/>' for d in by('fill')) + ''.join(f'<path d="{cl(d)}" fill="{tr}"/>' for d in by('fillacc'))
           + (''.join(f'<path d="{d}" stroke="url(#spec)" stroke-width="{num(sw * .3)}" transform="translate({num(-sw * .2)} {num(-sw * .2)})" opacity=".75"/>'
                      for d in by('body', 'rim', 'accent', 'ink')) if new else '') + '</g></svg>')   # glass-2026: блиск по верхньо-лівому краю шару
    if dk:   # гліф у лінзі — рецепт ручного значка 12 (ICON-3, Konst 26.11: «чому не 100 %?»): тінь групою, блиск лише по штрихах, без ореолу
        col = c['deco'].get('colors', {})
        ring = col.get('ring', [lift(g1, .86), lift(g1, .61), g1])   # під склом гліф на тон світліший — тонування його гасить
        dot, u = col.get('dot', mix('#FFFFFF', g1, .05)), side / 100   # u — одиниць гліфа на одиницю кадру
        strk, flat = by('body', 'rim', 'accent', 'ink'), by('fill', 'fillacc')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(vx)} {num(vy)} {num(side)} {num(side)}"><defs>'
               f'<linearGradient id="acc" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{ring[0]}"/><stop offset=".45" stop-color="{ring[1]}"/><stop offset="1" stop-color="{ring[2]}"/></linearGradient>'
               f'<filter id="sh" filterUnits="userSpaceOnUse" x="-20" y="-20" width="64" height="64"><feGaussianBlur stdDeviation="{num(1.8 * u)}"/></filter></defs>'
               f'<g transform="translate(0 {num(1.2)})" filter="url(#sh)" opacity="{c["deco"].get("shadow", .3)}"><g fill="none" stroke="#000" stroke-width="{num(sw)}"{k}>'
               + ''.join(f'<path d="{d}"/>' for d in strk) + '</g><g fill="#000">' + ''.join(f'<path d="{cl(d)}"/>' for d in flat) + '</g></g>'
               f'<g fill="none" stroke="url(#acc)" stroke-width="{num(sw)}"{k}>' + ''.join(f'<path d="{d}"/>' for d in strk) + '</g>'
               f'<g fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="{num(.35)}" transform="translate({num(-.35)} {num(-.35)})"{k}>'   # блиск по верхньо-лівому краю
               + ''.join(f'<path d="{d}"/>' for d in strk) + '</g>'
               + ''.join(f'<path d="{cl(d)}" fill="{dot}"/>' for d in by('fill')) + ''.join(f'<path d="{cl(d)}" fill="url(#acc)"/>' for d in by('fillacc')) + '</svg>')
    bg = f'background:linear-gradient(150deg,{g1},{g2})' if style == 'accent' else f'background-color:{L["bgc"]};background-image:{L["aur"]}'
    if c.get('bg'): bg = f'background:{c["bg"]}'   # свій фон продукту літералом CSS (ICON-2: у сторінки нема аврори — QR Lens)
    du, dt = deco_svg(c, L, st, kind) if c.get('deco') else ('', '')
    return (f'<!-- іконка «{kind}» · стиль {style} · згенеровано {SELF} icons зі сторінки {os.path.basename(c["stand"])} (A75); руками не правити -->\n'
            f'<!doctype html><style>html,body{{margin:0}}.i{{position:relative;width:{ICON_CSS}px;height:{ICON_CSS}px;overflow:hidden;{bg}}}'
            f'.i svg{{position:absolute;inset:0;width:100%;height:100%}}</style><div class="i">{du}{svg}{dt}{rim_svg() if kind == "any" else ""}</div>\n')


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
    big = raster({(lk, s): icon_html(dict(c, look=lk), pr, 'any', s) for lk in LOOKS for s in c['_styles']})   # рядок на манеру (ICON-3: вибір — Konst з аркуша)
    n, walls, S = 180, [('#F2F2F7', 'світлі'), ('#1C1C1E', 'темні'), ('#6B8FA8', 'фото')], list(c['_styles'])
    mask = Image.new('L', (n * 4, n * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, n * 4 - 1, n * 4 - 1], radius=int(n * 4 * .225), fill=255)   # лише показ маски iOS
    mask = mask.resize((n, n), Image.LANCZOS)
    W = Image.new('RGB', (len(walls) * (len(S) * 200 + 20), 20 + 240 * len(LOOKS)), '#FFFFFF')
    for i, (col, _) in enumerate(walls):
        x0 = i * (len(S) * 200 + 20)
        ImageDraw.Draw(W).rectangle([x0 + 10, 10, x0 + len(S) * 200 + 10, 10 + 240 * len(LOOKS)], fill=col)
        for r, lk in enumerate(LOOKS):
            for j, s in enumerate(S):
                W.paste(big[(lk, s)].resize((n, n), Image.LANCZOS), (x0 + 20 + j * 200, 40 + 240 * r), mask)
    p = os.path.join(d, 'icon_compare.png')
    W.save(p)
    print(f'  аркуш стилів: {p} (рядки — манери: ' + ' · '.join(LOOKS) + f' (у конфігу — {c.get("look", "glass-1")}); у групі: ' + ' · '.join(S)
          + '; шпалери: ' + ' · '.join(nm for _, nm in walls) + ')')


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
        # ICON-2: манера glass-2026 — новий пресет поруч зі старим; фігури rect · circle; суцільні ролі
        t('id="spec"' not in fa and 'translate(-' not in fa, 'glass-1 (типова): кадр без нового блиску — старий пресет не змінено')
        sp = shapes('<rect x="2" y="2" width="7.5" height="7.5" rx="1.6"/><circle cx="12" cy="12" r="3"/><path d="M1 1L2 2"/>')
        t(len(sp) == 3 and sp[0].startswith('M3.6 2H7.9A1.6') and sp[1].count('A3 3') == 2 and sp[2] == 'M1 1L2 2', 'фігури: rect → шлях з дугами · circle → дві півдуги · path як є')
        q = cp_pr(pr); q['light']['inner'] = q['dark']['inner'] = ('<rect x="2" y="2" width="7.5" height="7.5" rx="1.6"/><rect x="4.4" y="4.4" width="2.7" height="2.7" rx=".7"/>'
                                                                  '<rect x="14.5" y="14.5" width="3" height="3" rx=".5"/>')
        c3 = load(cp); c3['look'] = 'glass-2026'; c3['layers'] = {'body': [0], 'fill': [1], 'fillacc': [2]}; c3['bg'] = 'linear-gradient(#123,#456)'
        h3 = icon_html(c3, q, 'any', 'aurora-dark')
        t('id="spec"' in h3 and 'stroke="url(#spec)"' in h3 and h3.count('fill="url(#acc)"') == 1 and 'background:linear-gradient(#123,#456)' in h3,
          'glass-2026: блиск по краю шару · fillacc — суцільний акцент · свій фон з конфігу')
        # ICON-3: шар-прикраса «лупа» · frac · тон · зазор (QR Lens, значок 12)
        c5 = load(cp); c5['look'] = 'glass-2026'; c5['layers'] = c3['layers']; c5['deco'] = {'kind': 'magnifier', 'cx': 44, 'cy': 44, 'r': 32}
        a5, m5 = icon_html(c5, q, 'any', 'aurora-dark'), icon_html(c5, q, 'mask', 'aurora-dark')
        t(a5.count('<svg') == 4 and 'id="dtint"' in a5 and 'id="dfe"' in a5 and a5.index('id="dtint"') < a5.index('id="acc"') < a5.index('stroke="url(#dsp)"'),
          'прикраса: скло й ручка під гліфом, обідок і блиск над ним (4 SVG: під · гліф · над · кант)')
        t(abs(frac(c5, 'any') - .3392) < 1e-3 and 'viewBox="0 0 100 100"' in a5 and 'viewBox="-16' in m5, 'frac: гліф 0,34 у лінзі r 32 · mask — композиція стиснута (FRAC mask / any)')
        lt = icon_html(c5, q, 'any', 'aurora-light'); dkc = re.search(r'id="dfe".*?stop-color="(#\w+)"', a5).group(1)
        t(dkc != re.search(r'id="dfe".*?stop-color="(#\w+)"', lt).group(1), 'тон: муфта на темному й світлому — різний метал')
        t(icon_html(dict(c5, deco=None), q, 'any', 'aurora-dark').count('<svg') == 2, 'без deco — кадр як був (гліф · кант)')
        c7 = dict(c5, deco=dict(c5['deco'], colors={'ring': ['#B8FFF0', '#5FD6C2', '#2A8C84'], 'dot': '#F4FBFA', 'handle': ['#7F9C99', '#FFFFFF', '#E3EFED', '#6F8A88']}))
        a7 = icon_html(c7, q, 'any', 'aurora-dark')
        t('stop-color="#B8FFF0"' in a7 and 'fill="#F4FBFA"' in a7 and 'stop-color="#7F9C99"' in a7 and 'filter="url(#glow)"' not in a7,
          'colors: точні кольори гліфа й ручки з конфігу · гліф у лінзі без ореолу (рецепт ручного 12)')
        c6 = dict(c5, frac={'any': .5})
        try:
            deco_check(c6); t(False, 'гліф більший за лінзу → помилка конфігу')
        except SystemExit as x:
            t('не влазить' in str(x), 'гліф більший за лінзу → помилка конфігу')
        c4 = load(cp); c4['look'] = 'glass-2099'; json.dump(dict(cfg, look='glass-2099'), open(cp, 'w', encoding='utf-8'))
        try:
            load(cp); t(False, 'невідома манера → помилка конфігу')
        except SystemExit as x:
            t('манера' in str(x), 'невідома манера → помилка конфігу')
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
