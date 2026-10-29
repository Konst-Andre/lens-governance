# explore.py · тестувальник ядра — ДОСЛІДНИК: сам ходить сайтом продукту, тисне все, що можна натиснути, і пише вади (Konst 21.10.2026, AE S96).
# живе доки: у сімейства є веб-продукти. Метод, конфіг і межі — tools/tester/TESTER.md (читати перед першим запуском у новому продукті).
# Практика (21.10.2026): Playwright Agents 1.56 — planner / generator / healer; WebProber, Explorbot, AutoExplore — агент ходить сайтом без сценарію
#   і пише звіт про вади. Беремо: обхід без сценарію + звіт із шляхом повтору. Не беремо (поки): модель-дослідника — дорого й нестабільно; окремий шар потім.
# Безпека: за замовчуванням БЛОКУЄ кожен запит, що щось пише (не GET/HEAD/OPTIONS), — крім «stubs» (відповідь-заглушка) і «allow_write» з конфігу;
#   кнопки зі «словами-небезпеками» (Опублікувати, Видалити, Надіслати, Оплатити, Publish, Delete, Send, Pay…) не тисне. Тож на проді — без побічних дій.
# Запуск:  python3 explore.py <конфіг.json> [--out <тека звіту>] [--baseline <файл>] [--max N]      · python3 explore.py selftest  (зуби)
# Переглядач (AE S115): "viewers" у конфігу — сценарій viewer.py (порядок як на екрані, фокус у вікні, жест = один крок, закриття); неописаний — ⚠ сам.
# Вихід: ✗ / ⚠ у консоль + <тека>/TESTER_<час>.md (вади зі шляхом кліків, знімки ✗, покриття, заблоковані записи, пакети ПК / PWA). Код виходу 1, якщо нові ✗.
# Паузи (AE S111, PW-2 / wsd 1.21): «після старту» (settle_ms) і «після кліку» (after_click_ms) — «тиша до N» ядра (tools/claude-code/pw_quiet.py): повертається, щойно
#   таймери сторінки у вікні, скінченні анімації й запити скінчились, і так два кадри; вікно «сторінка не затихає» (0,7 с) — справжній час (pg.wait_real): воно
#   РАХУЄ зміни за час, тиша його зламала б. QUIET=0 — старі фіксовані паузи (негативний контроль, запасний режим). Звіт і консоль кажуть, скільки зекономлено.
# Кеш прогону (AE S112): кожен клік — як і раніше, з чистої сторінки, але GET-відповіді 200 беруться з пам'яті прогону (route.fetch → route.fulfill), а не з мережі:
#   відкриття сторінки 2,0 → 0,14 с (замір AE ?hdr, 28.10.2026). Не-200 не кешуються — ✗ «запит 5xx» видно щоразу. Між прогонами кешу нема (бачимо сьогоднішній сайт).
#   Вимкнути: конфіг "cache": false або TESTER_CACHE=0 (негативний контроль); окремі адреси — "nocache" (regex; напр., опитування сервера, що чекає нових даних).
import sys, os, re, json, time, pathlib, datetime, tempfile, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'claude-code'))
from pw_quiet import install as quiet_install, report as quiet_report   # пауза = подія, не число (PW-2)
import viewer as VW   # сценарій «переглядач» (AE S115, TESTER.md §8): гортає за видимим порядком, фокус у вікні, жест = один крок

DENY = r'опублікув|видали|надісла|відправ|оплат|купит|замовит|вийти з|розлогін|скинути все|publish|delete|remove|send|submit|pay|buy|logout|sign out|reset all'
TECH = r'\bundefined\b|\bNaN\b|\[object |\$\{|\bnull\b|Uncaught|TypeError|ReferenceError'
DEVICES = {'pc': dict(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1),
           'iphone': dict(viewport={'width': 375, 'height': 812}, device_scale_factor=3, is_mobile=True, has_touch=True,
                          user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1')}

# у сторінці: керуючі елементи станом зараз (видимі, досяжні, не вимкнені) — підпис, локатор для повтору, «група» для вибірки однакових
CONTROLS_JS = r"""() => {
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const path = e => { const p = []; for (let n = e; n && n.nodeType === 1 && n !== document.body; n = n.parentElement) {
      if (n.id && document.querySelectorAll('#' + CSS.escape(n.id)).length === 1) { p.unshift('#' + CSS.escape(n.id)); break; }
      let i = 1, s = n; while ((s = s.previousElementSibling)) if (s.tagName === n.tagName) i++;
      p.unshift(n.tagName.toLowerCase() + ':nth-of-type(' + i + ')'); } return (p[0] && p[0][0] === '#' ? '' : 'body > ') + p.join(' > '); };
  const out = [];
  for (const e of document.querySelectorAll('a[href],button,[role=button],[role=tab],[role=menuitem],summary,select,input[type=checkbox],input[type=radio],[onclick]')) {
    if (!vis(e) || e.closest('[inert]')) continue;
    const r = e.getBoundingClientRect(), c = document.elementFromPoint(Math.min(innerWidth - 1, Math.max(0, r.left + r.width / 2)), Math.min(innerHeight - 1, Math.max(0, r.top + r.height / 2)));
    const name = (e.getAttribute('aria-label') || e.textContent || e.getAttribute('title') || e.value || '').replace(/\s+/g, ' ').trim().slice(0, 60);
    out.push({ sel: path(e), name, tag: e.tagName.toLowerCase(), group: e.tagName + '.' + [...e.classList].sort().join('.'),
               disabled: !!(e.disabled || e.getAttribute('aria-disabled') === 'true'), current: !!(e.getAttribute('aria-current') && e.getAttribute('aria-current') !== 'false' || e.getAttribute('aria-selected') === 'true' || e.getAttribute('aria-pressed') === 'true' || e.matches('.active,.on,.current,.selected')), covered: !!(c && c !== e && !e.contains(c) && !c.contains(e)),
               href: e.tagName === 'A' ? e.getAttribute('href') : null });
  }
  return out; }"""
# у сторінці: технічне сміття у видимому тексті + атрибутах, прокрутка вбік, кнопки без назви
SCAN_JS = r"""(re) => {
  const R = new RegExp(re), out = { tech: [], hscroll: document.documentElement.scrollWidth > innerWidth + 1, noname: [] };
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { const t = n.textContent.trim(); if (t && n.parentElement && !/^(SCRIPT|STYLE)$/.test(n.parentElement.tagName) && vis(n.parentElement) && R.test(t)) out.tech.push(t.slice(0, 80)); }
  for (const e of document.querySelectorAll('[title],[aria-label],[placeholder]')) if (vis(e)) for (const a of ['title', 'aria-label', 'placeholder']) { const v = e.getAttribute(a); if (v && R.test(v)) out.tech.push(a + ': ' + v.slice(0, 60)); }
  for (const e of document.querySelectorAll('button,[role=button],a[href]')) if (vis(e) && !(e.getAttribute('aria-label') || e.textContent.trim() || e.getAttribute('title'))) out.noname.push(e.outerHTML.slice(0, 80));
  out.tech = [...new Set(out.tech)].slice(0, 8); out.noname = out.noname.slice(0, 5); return out; }"""
SIG_JS = r"""() => [location.pathname + location.hash, document.title, (document.querySelector('h1') || {}).textContent || '', document.querySelectorAll('dialog[open],[role=dialog]:not([hidden])').length,
  (window.S && S.screen) || ''].join(' | ').replace(/\s+/g, ' ').slice(0, 160)"""
INIT_JS = r"""(() => { window.__tester = { csp: [], muts: 0 };
  window.__testerScroll = () => [...document.querySelectorAll('*')].filter(e => e.scrollHeight > e.clientHeight + 4 && /auto|scroll/.test(getComputedStyle(e).overflowY)).map(e => Math.round(e.scrollTop)).concat([Math.round(scrollY)]);
  window.__testerLook = () => [document.querySelectorAll(':popover-open').length, Math.round(scrollY), [...document.querySelectorAll('*')].filter(e => e.scrollTop > 0).map(e => Math.round(e.scrollTop)).join(',')].join('|');
  document.addEventListener('securitypolicyviolation', e => window.__tester.csp.push(e.violatedDirective + ' ' + (e.blockedURI || '')));
  new MutationObserver(m => { window.__tester.muts += m.length; }).observe(document, { subtree: true, childList: true, attributes: true, characterData: true }); })();"""

def run(cfg, out_dir, baseline=None, max_clicks=None, quiet=False):
  F, COV, WR = [], {'states': [], 'clicked': 0, 'skipped_deny': [], 'skipped_disabled': 0, 'skipped_covered': 0, 'sampled': 0, 'dead': 0}, []
  deny = re.compile(cfg.get('deny', DENY), re.I); allow_lab = re.compile(cfg['allow_labels'], re.I) if cfg.get('allow_labels') else None; tech = cfg.get('tech', TECH); maxc = max_clicks or cfg.get('max_clicks', 80)
  stubs = [(re.compile(s['url']), s.get('method', 'POST').upper(), s) for s in cfg.get('stubs', [])]
  allow = [re.compile(x) for x in cfg.get('allow_write', [])]
  out_dir = pathlib.Path(out_dir); shots = out_dir / 'shots'; shots.mkdir(parents=True, exist_ok=True)
  use_cache = cfg.get('cache', True) and os.environ.get('TESTER_CACHE', '1') != '0'; nocache = re.compile(cfg['nocache']) if cfg.get('nocache') else None
  CACHE, CST = {}, {'hit': 0, 'miss': 0}   # кеш прогону: адреса → (статус, заголовки, тіло); лише GET 200
  DROP = ('content-encoding', 'content-length', 'transfer-encoding')   # тіло в кеші вже розпаковане — ці заголовки збрехали б браузеру
  def add(lvl, kind, where, msg, path=None, shot=None):
    F.append({'lvl': lvl, 'kind': kind, 'where': where, 'msg': msg, 'path': path or '', 'shot': shot or ''})
    if not quiet: print(f'{lvl} {kind} · {where} — {msg}' + (f'  [шлях: {path}]' if path else ''), flush=True)
  with sync_playwright() as p:
    b = p.chromium.launch()
    def page():
      ctx = b.new_context(bypass_csp=bool(cfg.get('bypass_csp', True)), **DEVICES[cfg.get('device', 'pc')])
      ctx.add_init_script(INIT_JS)
      if cfg.get('init_script'): ctx.add_init_script(cfg['init_script'])
      pg = quiet_install(ctx.new_page()); ev = {'err': [], 'con': [], 'req': [], 'dlg': [], 'n': 0}   # wait_for_timeout(N) — тиша до N; wait_real — справжній час
      pg.on('request', lambda r: ev.__setitem__('n', ev['n'] + 1))
      pg.on('pageerror', lambda e: ev['err'].append(str(e)[:160]))
      pg.on('console', lambda m: ev['con'].append(m.text[:160]) if m.type == 'error' else None)
      pg.on('requestfailed', lambda r: ev['req'].append(f'{r.method} {r.url[:90]} — {r.failure}') if not re.search(r'ERR_ABORTED|BLOCKED_BY_CLIENT', str(r.failure)) else None)   # свої блоки запису — не вада
      pg.on('response', lambda r: ev['req'].append(f'{r.request.method} {r.url[:90]} — {r.status}') if r.status >= 500 else None)
      pg.on('dialog', lambda d: (ev['dlg'].append(d.type + ': ' + d.message[:80]), d.dismiss()))
      def route(rt):
        rq = rt.request; m = rq.method.upper()
        if m in ('GET', 'HEAD', 'OPTIONS'):
          if m != 'GET' or not use_cache or not rq.url.startswith('http') or (nocache and nocache.search(rq.url)): return rt.continue_()
          hit = CACHE.get(rq.url)
          if hit: CST['hit'] += 1; return rt.fulfill(status=hit[0], headers=hit[1], body=hit[2])
          try: r = rt.fetch(); body = r.body()
          except Exception: return rt.continue_()   # мережа впала — хай браузер спробує сам і покаже «запит» як є
          CST['miss'] += 1
          if r.status == 200: CACHE[rq.url] = (200, {k: v for k, v in r.headers.items() if k.lower() not in DROP}, body)
          return rt.fulfill(status=r.status, headers={k: v for k, v in r.headers.items() if k.lower() not in DROP}, body=body)
        for rx, sm, s in stubs:
          if rx.search(rq.url) and sm == m:
            body = s.get('body', {}); return rt.fulfill(status=s.get('status', 200), content_type='application/json', headers={'access-control-allow-origin': '*'},
                                                       body=json.dumps(body, ensure_ascii=False) if not isinstance(body, str) else body)
        if any(a.search(rq.url) for a in allow): return rt.continue_()
        WR.append(f'{m} {rq.url[:100]}'); return rt.abort('blockedbyclient')
      pg.route('**/*', route)
      return ctx, pg, ev
    def ready(pg, start):
      pg.goto(cfg['url'], wait_until='domcontentloaded', timeout=45000)
      if cfg.get('ready'): pg.wait_for_function(cfg['ready'], timeout=30000)
      else: pg.wait_for_load_state('networkidle', timeout=30000)
      if start.get('js'): pg.evaluate(start['js'])
      pg.wait_for_timeout(cfg.get('settle_ms', 700))
    def judge(pg, ev, where, path, base_err=0):
      s = pg.evaluate(SCAN_JS, tech); csp = pg.evaluate('window.__tester ? window.__tester.csp : []')
      shot = None
      bad = ev['err'][base_err:] or s['tech'] or csp
      if bad:
        shot = f'{len(F):03d}.png'
        try: pg.screenshot(path=str(shots / shot))
        except Exception: shot = None
      for e in ev['err'][base_err:]: add('✗', 'JS-помилка', where, e, path, shot)
      if s['tech']: add('✗', 'технічний текст', where, ' | '.join(s['tech'][:4]), path, shot)
      for c in csp: add('✗', 'CSP', where, c, path, shot)
      if s['hscroll']: add('⚠', 'прокрутка вбік', where, f'сторінка ширша за екран', path)
      for x in s['noname']: add('⚠', 'кнопка без назви', where, x, path)
    known_vw = [VW.setup(v)['dialog'] for v in cfg.get('viewers', [])]; seen_vw = set()
    def unseen(pg, where, path):   # переглядач, якого конфіг не описав, — ⚠ один раз (TESTER.md §8 п. 1: «знайти переглядач сам»)
      for d in pg.evaluate(VW.UNCOVERED_JS, [known_vw, VW.NEXT, VW.PREV]):
        if d not in seen_vw: seen_vw.add(d); add('⚠', 'переглядач без перевірки', where, f'вікно {d} гортає («Попереднє / Наступне»), а в конфігу його нема — опиши в "viewers" (TESTER.md §8)', path)
    for start in cfg.get('starts', [{'name': 'головна'}]):
      ctx, pg, ev = page()
      try: ready(pg, start)
      except Exception as e: add('✗', 'старт', start['name'], f'стан не відкрився: {str(e)[:120]}'); ctx.close(); continue
      sig0 = pg.evaluate(SIG_JS); COV['states'].append(sig0)
      judge(pg, ev, start['name'], 'старт'); unseen(pg, start['name'], 'старт')
      for c in ev['con'][:5]: add('⚠', 'консоль', start['name'], c, 'старт')
      for r in ev['req'][:5]: add('✗', 'запит', start['name'], r, 'старт')
      ctrls = pg.evaluate(CONTROLS_JS); ctx.close()
      groups = {}
      for c in ctrls: groups.setdefault(c['group'], []).append(c)
      todo = []
      for g, L in groups.items():
        pick = L if len(L) < 5 else [L[0], L[len(L) // 2], L[-1]]
        COV['sampled'] += len(L) - len(pick); todo += pick
      for c in todo[:maxc]:
        label = f"{c['tag']} «{c['name'] or '—'}»"
        if c['disabled']: COV['skipped_disabled'] += 1; continue
        if c['covered']: COV['skipped_covered'] += 1; continue
        if deny.search(c['name'] or '') and not (allow_lab and allow_lab.search(c['name'] or '')): COV['skipped_deny'].append(label); continue
        if c['href'] and re.match(r'^(https?:)?//', c['href']) and not c['href'].startswith(cfg['url'][:30]): continue   # зовнішні посилання — не наш сайт
        ctx, pg, ev = page(); path = f"{start['name']} → {label}"
        try:
          ready(pg, start); e0 = len(ev['err']); m0 = pg.evaluate('window.__tester.muts'); u0 = pg.url; l0 = pg.evaluate('window.__testerLook()'); n0 = ev['n']; s0 = pg.evaluate('window.__testerScroll()')
          loc = pg.locator(c['sel']).first
          if c['tag'] == 'select':
            opts = loc.evaluate("e => [...e.options].filter(o => !o.disabled && o.value !== e.value).map(o => o.value)")
            if opts: loc.select_option(opts[0])
          else: loc.click(timeout=4000)
          pg.wait_for_timeout(cfg.get('after_click_ms', 900)); COV['clicked'] += 1
          # S110 (AE, пропуск Konst): «зсув після кліку» — натиснутий елемент на місці, адреса та сама, вікна нема, а прокрутка зрушила на 1–48 px (повзе з кожним кліком);
          #   CLS цього не бачить навмисно (hadRecentInput: зсуви ≤ 500 мс після дії не рахуються — MDN, web.dev, 28.10.2026), тому — окремий замір до / після.
          #   «сторінка не затихає» — після паузи кліку DOM міняється далі (цикл перемальовувань: поле вводу губить фокус і з'являється знову). Виняток — calm_ok (regex назв).
          calm_ok = re.compile(cfg['calm_ok'], re.I) if cfg.get('calm_ok') else None
          s1 = pg.evaluate('window.__testerScroll()')
          if pg.url == u0 and not ev['dlg'] and len(s1) == len(s0) and pg.locator(c['sel']).count() and not pg.evaluate("document.querySelectorAll('dialog[open]').length"):
            dd = [abs(a - b) for a, b in zip(s0, s1) if a != b]
            if dd and max(dd) <= 48 and not (calm_ok and calm_ok.search(c['name'] or '')):
              add('⚠', 'зсув після кліку', start['name'], f'прокрутка зрушила на {max(dd)} px без переходу — вміст «повзе» з кожним кліком', path)
          mq = pg.evaluate('window.__tester.muts'); pg.wait_real(700); storm = pg.evaluate('window.__tester.muts') - mq   # вікно ЛІЧБИ — справжній час, не тиша
          if storm > cfg.get('calm_max', 20) and not (calm_ok and calm_ok.search(c['name'] or '')):
            add('⚠', 'сторінка не затихає', start['name'], f'після кліку DOM міняється далі: {storm} змін за 0,7 с (цикл перемальовувань?)', path)
          judge(pg, ev, start['name'], path, e0); unseen(pg, start['name'], path)
          for r in ev['req'][:3]: add('✗', 'запит', start['name'], r, path)
          for d in ev['dlg']: add('⚠', 'нативне вікно', start['name'], d, path)
          moved = pg.evaluate('window.__tester.muts') - m0
          # «мертва» (практика Sentry / Inspectlet «dead click», 21.10.2026): ні DOM, ні адреса, ні вікно, ні спливне (popover), ні фокус деінде (фокус на самій кнопці — не відгук), ні прокрутка, ні запит;
          # вибраний (aria-current / .on) не судиться — клік по ньому й не мусить нічого міняти; посилання з адресою — теж ні
          if moved == 0 and pg.url == u0 and not ev['dlg'] and ev['n'] == n0 and pg.evaluate('window.__testerLook()') == l0 and not pg.evaluate("(s) => { const a = document.activeElement, c = document.querySelector(s); return !!(a && a !== document.body && a !== c && !(c && c.contains(a))); }", c['sel']) and not c['current'] and c['tag'] not in ('select',) and not c['href']:
            COV['dead'] += 1; add('⚠', 'мертва кнопка', start['name'], 'клік нічого не змінив на сторінці (ні DOM, ні адреса, ні вікно)', path)
          sig = pg.evaluate(SIG_JS)
          if sig not in COV['states']: COV['states'].append(sig)
        except Exception as e:
          add('⚠', 'клік не вдався', start['name'], str(e).split('\n')[0][:140], path)
        finally: ctx.close()
    if cfg.get('viewers'): VW.run_viewers(cfg, page, ready, add, COV)   # сценарій «переглядач» — з чистих сторінок, після кліків
    # пакети платформи — на першому старті
    st0 = (cfg.get('starts') or [{'name': 'головна'}])[0]
    if cfg.get('device', 'pc') == 'pc' and cfg.get('pack_pc', True):
      ctx, pg, ev = page(); ready(pg, st0)
      reach = pg.evaluate("""() => { const all = [...document.querySelectorAll('a[href],button,select,input,textarea,[tabindex]')].filter(e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
          return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && !e.disabled && e.tabIndex >= 0 && !e.closest('[inert]'); }); all.forEach((e, i) => e.dataset.tst = i); return all.length; }""")
      seen = set()
      for _ in range(min(reach + 5, 160)):
        pg.keyboard.press('Tab'); i = pg.evaluate("document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.tst : null")
        if i is not None: seen.add(i)
      miss = pg.evaluate("(seen) => [...document.querySelectorAll('[data-tst]')].filter(e => !seen.includes(e.dataset.tst)).map(e => (e.getAttribute('aria-label') || e.textContent || e.tagName).trim().slice(0, 40))", list(seen))
      if miss: add('⚠', 'клавіатура', st0['name'], f'Tab не доходить до {len(miss)} з {reach}: ' + ' · '.join(miss[:6]))
      ctx.close()
    if cfg.get('pwa') or cfg.get('device') == 'iphone':
      ctx, pg, ev = page(); ready(pg, st0)
      man = pg.evaluate("""async () => { const l = document.querySelector('link[rel=manifest]'); if (!l) return null; try { return await (await fetch(l.href)).json(); } catch (e) { return {error: String(e)}; } }""")
      if not man: add('⚠', 'PWA', st0['name'], 'нема <link rel=manifest> — встановити на екран не вийде')
      else:
        need = [k for k in ('name', 'start_url', 'icons') if not man.get(k)]
        if man.get('display') not in ('standalone', 'minimal-ui', 'fullscreen'): need.append('display=standalone')
        sizes = ' '.join(i.get('sizes', '') for i in man.get('icons', []))
        if '192x192' not in sizes or '512x512' not in sizes: need.append('іконки 192 і 512')
        if need: add('⚠', 'PWA', st0['name'], 'маніфест: бракує ' + ', '.join(need))
      sw = pg.evaluate("async () => !!(navigator.serviceWorker && await Promise.race([navigator.serviceWorker.getRegistration(), new Promise(r => setTimeout(() => r(null), 4000))]))")
      if not sw: add('⚠', 'PWA', st0['name'], 'сервіс-воркер не зареєстровано — без мережі застосунок не відкриється')
      else:
        ctx.set_offline(True)
        try: pg.reload(timeout=15000); txt = pg.evaluate("document.body.innerText.trim().length")
        except Exception: txt = 0
        if txt < 40: add('✗', 'PWA', st0['name'], 'без мережі сторінка порожня — офлайн не працює')
        ctx.set_offline(False)
      if not pg.evaluate("!!document.querySelector('meta[name=viewport]')"): add('⚠', 'PWA', st0['name'], 'нема meta viewport')
      ctx.close()
    b.close()
  for wr in sorted(set(WR)): F.append({'lvl': 'ⓘ', 'kind': 'запис заблоковано', 'where': '', 'msg': wr, 'path': '', 'shot': ''})   # не вада: сторінка хотіла писати — тестувальник не пустив
  # база відомих вад: блокує лише нове (як ui_lint --baseline)
  key = lambda f: f"{f['kind']}|{f['where']}|{re.sub(r'[0-9]+', '#', f['msg'])[:80]}"
  if baseline:
    bp = pathlib.Path(baseline)
    if not bp.exists(): bp.write_text(json.dumps(sorted({key(f) for f in F if f['lvl'] == '✗'}), ensure_ascii=False, indent=1), encoding='utf-8'); print(f'база записана: {bp}')
    else:
      base = set(json.loads(bp.read_text(encoding='utf-8')))
      for f in F:
        if f['lvl'] == '✗' and key(f) in base: f['lvl'] = 'ⓘ'; f['msg'] += ' — з бази'
  x = sum(f['lvl'] == '✗' for f in F); w = sum(f['lvl'] == '⚠' for f in F)
  cache_line = f"кеш: {len(CACHE)} адрес, з пам'яті {CST['hit']} · з мережі {CST['miss']}" if use_cache else 'кеш: вимкнено'
  rep = out_dir / f"TESTER_{datetime.datetime.now():%Y-%m-%d_%H%M}.md"
  lines = [f"# Тестувальник · {cfg.get('name', '')} · {datetime.datetime.now():%d.%m.%Y %H:%M}", '',
           f"{cfg['url']} · пристрій {cfg.get('device', 'pc')} · **✗ {x} · ⚠ {w}** · станів {len(COV['states'])} · кліків {COV['clicked']} · {quiet_report()} · {cache_line}", '',
           '## Вади', '', '| | вид | де | що | шлях повтору | знімок |', '|---|---|---|---|---|---|',
           *[f"| {f['lvl']} | {f['kind']} | {f['where']} | {f['msg'].replace('|', '/')} | {f['path'].replace('|', '/')} | {('shots/' + f['shot']) if f['shot'] else ''} |" for f in F if f['lvl'] != 'ⓘ'], '',
           '## Покриття — куди дійшов і куди ні', '',
           f"- станів: {len(COV['states'])} — " + ' ; '.join(COV['states'][:12]),
           f"- натиснуто: {COV['clicked']} · однакових пропущено вибіркою: {COV['sampled']} · вимкнених: {COV['skipped_disabled']} · закритих іншим шаром: {COV['skipped_covered']}",
           f"- не тиснув (слова-небезпеки): {len(COV['skipped_deny'])} — " + ' · '.join(sorted(set(COV['skipped_deny']))[:12]),
           f"- заблоковано записів (не GET): {len(WR)} — " + ' · '.join(sorted(set(WR))[:8]), '',
           *(['## Переглядачі — гортання за видимим порядком (TESTER.md §8)', '', *VW.report_lines(COV), ''] if COV.get('viewers') else []),
           '_Дослідник (S110) ще бачить «зсув після кліку» і «сторінка не затихає»; не бачить: зміст і логіку (чи правильна відповідь), дотик і WebKit, відчуття руху — це сценарії продукту й очі._']
  rep.write_text('\n'.join(lines) + '\n', encoding='utf-8')
  print(f"─── тестувальник: ✗ {x} · ⚠ {w} · станів {len(COV['states'])} · кліків {COV['clicked']} · {quiet_report()} · {cache_line} · звіт {rep} ───")
  return x, w, F, CST

SELF_PAGE = """<!doctype html><html lang=uk><head><meta charset=utf-8><meta name=viewport content="width=device-width"><title>selftest</title></head><body>
<h1>Тест</h1><p id=o>старт</p>
<button id=ok onclick="o.textContent='гаразд'">Добре</button>
BAD</body></html>"""
DEFECTS = {
  'JS-помилка': "<button onclick=\"undefinedFn()\">Зламана</button>",
  'технічний текст': "<button onclick=\"o.textContent='Ціна: '+undefined\">Ціна</button>",
  'мертва кнопка': "<button>Нічого не робить</button>",
  'popover — не мертва': "<button popovertarget=pp>Підказка</button><div id=pp popover>текст</div>",
  'прокрутка вбік': "<div style='width:3000px;height:10px'></div>",
  'кнопка без назви': "<button onclick=\"o.textContent='x'\"></button>",
  'зсув після кліку': "<div id=sc style='height:120px;overflow:auto'><div style='height:900px'>довгий список</div></div><button onclick=\"sc.scrollTop+=20;o.textContent='вибрано'\">Вибрати</button>",
  'сторінка не затихає': "<button onclick=\"setInterval(()=>{o.textContent=String(Math.random())},25)\">Перейменувати</button>",
  'запис заблоковано': "<button onclick=\"fetch('/api/save',{method:'POST',body:'{}'}).catch(()=>{});o.textContent='шлю'\">Зберегти чернетку</button>",
  # S111 (тиша): дія, відкладена на 200 мс (у вікні after_click_ms), — тиша її дочікується, тож кнопка не «мертва»
  'запит 5xx на кожній сторінці': "<script>fetch('/boom').catch(()=>{})</script><button onclick=\"o.textContent='ще'\">Ще</button>",
  'відкладена дія — не мертва': "<button onclick=\"setTimeout(()=>{o.textContent='пізніше'},200)\">Пізніше</button>",
}
def selftest():
  d = pathlib.Path(tempfile.mkdtemp(prefix='tester-')); bad = 0
  class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
      if self.path.startswith('/boom'): self.send_error(500); return   # S112: 5xx не ховається кешем — видно на кожній сторінці
      return super().do_GET()
  H = functools.partial(Q, directory=str(d))
  srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), H); srv.daemon_threads = True; threading.Thread(target=srv.serve_forever, daemon=True).start()
  url = f'http://127.0.0.1:{srv.server_address[1]}/'
  def one(name, html):
    (d / 'index.html').write_text(SELF_PAGE.replace('BAD', html), encoding='utf-8')
    return run({'name': name, 'url': url, 'device': 'pc', 'pack_pc': False, 'settle_ms': 150, 'after_click_ms': 300}, d / ('out-' + str(abs(hash(name)))), quiet=True)
  x, w, F, C = one('чиста', '')
  ok = not [f for f in F if f['lvl'] in ('✗', '⚠')]; bad += not ok; print(('✓' if ok else '✗') + ' чиста сторінка → тиша · ' + (' | '.join(f['kind'] + ': ' + f['msg'][:60] for f in F) or '0'))
  on = os.environ.get('TESTER_CACHE', '1') != '0'   # S112: кеш справді працює (друга сторінка — з пам'яті), а з TESTER_CACHE=0 — нуль
  ok = (C['hit'] > 0) == on; bad += not ok; print(('✓' if ok else '✗') + f" кеш прогону: з пам'яті {C['hit']} (очікую {'> 0' if on else '0'})")
  for k, html in DEFECTS.items():
    x, w, F, C = one(k, html)
    if k == 'запит 5xx на кожній сторінці': hit = sum(f['kind'] == 'запит' for f in F) >= 2   # старт і сторінка кліку — обидві бачать 500
    else: hit = (not any(f['kind'] == 'мертва кнопка' for f in F)) if k.endswith('не мертва') else any(f['kind'] == k for f in F)
    bad += not hit; print(('✓' if hit else '✗') + (f' «{k}» → тиша (хибної тривоги нема)' if k.endswith('не мертва') else f' підкинуто «{k}» → спіймано'))
  import shutil; shutil.copy(pathlib.Path(__file__).resolve().parent / 'selftest' / 'viewer.html', d / 'viewer.html')   # S115: зуби сценарію «переглядач»
  vb, vn = VW.selftest(run, url); bad += vb
  print(f'─── tester selftest: {len(DEFECTS) + 2 + vn - bad}/{len(DEFECTS) + 2 + vn} ───'); return bad

if __name__ == '__main__':
  a = sys.argv[1:]
  if not a: print(__doc__ or 'python3 explore.py <конфіг.json> [--out тека] [--baseline файл] [--max N] | selftest'); sys.exit(2)
  if a[0] == 'selftest': sys.exit(1 if selftest() else 0)
  cfg = json.loads(pathlib.Path(a[0]).read_text(encoding='utf-8'))
  opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
  if opt('--url'): cfg['url'] = opt('--url')
  x, w, F, _ = run(cfg, opt('--out', 'tester-out'), opt('--baseline'), int(opt('--max', 0)) or None)
  sys.exit(1 if x else 0)
