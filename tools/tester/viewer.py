# viewer.py · тестувальник ядра — сценарій «ПЕРЕГЛЯДАЧ» (велике фото, слайди, «наступний запис»): гортає за тим порядком, який бачить людина?
# живе доки: живе explore.py. Метод, конфіг і межі — tools/tester/TESTER.md §8 (AE S115, «так» Konst 29.10.2026). Викликає explore.run (шар поруч із кліками).
# Вада класу (AE S114, двічі пропущена агентом): переглядач гортає за ВНУТРІШНІМ списком (прихована таблиця під плитками, порядок DOM ≠ CSS-порядок,
#   відфільтроване), а людина бачить інший — «перескакує кудись униз». Сестри: після кроку фокус падає на сторінку (стрілки вже не доходять);
#   жест тачпада (десятки подій колеса) гортає 4 замість 1; крок перемальовує весь перелік — «зависання».
# Практика (звірено 29.10.2026): W3C WAI Carousels «Functionality» — «Попереднє / Наступне» фокус НЕ переносять, позиція «Item x of y»;
#   APG «Dialog (Modal)» — фокус у вікні, Esc закриває, фокус повертається тому, хто відкрив, а якщо його вже нема — логічному елементу.
# Перевірки (кожна — окремий рядок звіту): (а) порядок = видимий (геометрія getClientRects, рядок за рядком), край — по колу / стоп за конфігом;
#   (б) окремо клавіші ← / →, кнопки, колесо; (в) фокус у вікні після кожного кроку; (г) лічильник «N з M»; (д) жест: 40 подій колеса по 16 мс = 1 крок,
#   3 клацання колеса за 0,4 с = 1 крок; (е) час кроку (у сторінці: подія → кадр після зміни) ≤ max_ms — ⚠; (є) закрити Esc · «✕» · клік поза →
#   фокус на тому, хто відкрив, чи на показаному; вибір у списку синхронний, якщо заявлено; (ж) переглядач іншого екрана не бере стан попереднього.
# Паузи: кроки колеса — СПРАВЖНІЙ час (pg.wait_real): замок жесту живе на Date.now(), «тиша» його не бачить і повернулась би одразу → хибний ✗.
import re, time, json

NEXT = r'наступн|next|›|→'
PREV = r'попередн|prev|‹|←'
CLOSE = r'закрити|close|✕|×'
COUNTER = r'(\d+)\s*(?:з|із|из|of|/)\s*(\d+)'
# у сторінці: час кроку — від події (захоплення на window) до кадру після першої зміни DOM
TIMING_JS = r"""(() => { const T = window.__vw = { t0: 0, t1: 0, wait: false };
  ['keydown', 'click', 'wheel'].forEach(t => addEventListener(t, () => { T.t0 = performance.now(); T.t1 = 0; T.wait = false; }, true));
  new MutationObserver(() => { if (!T.t0 || T.t1 || T.wait) return; T.wait = true; requestAnimationFrame(() => setTimeout(() => { T.t1 = performance.now(); T.wait = false; }, 0)); })
    .observe(document, { subtree: true, childList: true, attributes: true, characterData: true }); })();"""
# у сторінці: переглядачі, яких конфіг не описав (вікно з «Попереднє» і «Наступне»)
UNCOVERED_JS = r"""([known, nx, pv]) => { const N = new RegExp(nx, 'i'), P = new RegExp(pv, 'i'), out = [];
  for (const d of document.querySelectorAll('dialog[open],[role=dialog]:not([hidden])')) {
    if (known.some(k => { try { return d.matches(k); } catch (e) { return false; } })) continue;
    const L = [...d.querySelectorAll('button,[role=button]')].map(b => (b.getAttribute('aria-label') || b.textContent || '').trim());
    if (L.some(t => N.test(t)) && L.some(t => P.test(t))) out.push(d.tagName.toLowerCase() + (d.id ? '#' + d.id : '') + [...d.classList].map(c => '.' + c).join('')); }
  return out; }"""


def _js(v):
  return json.dumps(v, ensure_ascii=False)


def setup(V):
  """Нормалізує опис переглядача з конфігу: усе, що сторінка має знати, — рядками JS."""
  v = dict(V)
  v.setdefault('id', 'e => e.dataset.id || e.dataset.c || e.dataset.pc')
  v.setdefault('eligible', 'id => true')
  v.setdefault('dialog', 'dialog[open]')
  v.setdefault('current', f"(d => d && (d.dataset.id || d.dataset.c || d.dataset.pc))(document.querySelector({_js(v['dialog'])}))")
  v.setdefault('wrap', True); v.setdefault('steps', 6); v.setdefault('max_ms', 150); v.setdefault('wheel_gap_ms', 700)
  v.setdefault('skip', {})
  return v


def _order(pg, v):
  # видимий порядок: елементи з розміром на екрані, рядок за рядком (верх, потім лівий край) — ловить і CSS-порядок, і прихований дубль
  return pg.evaluate(f"""() => {{ const idf = {v['id']}, ok = {v['eligible']};
    const L = [...document.querySelectorAll({_js(v['items'])})].filter(e => e.getClientRects().length && !e.closest('dialog'))
      .map(e => ({{ e, r: e.getBoundingClientRect() }})).sort((p, q) => p.r.top - q.r.top);
    const rows = []; for (const x of L) {{ const R = rows[rows.length - 1]; if (R && x.r.top < R.top + Math.max(4, R.h / 2)) R.xs.push(x); else rows.push({{ top: x.r.top, h: x.r.height, xs: [x] }}); }}
    const ids = rows.flatMap(R => R.xs.sort((p, q) => p.r.left - q.r.left)).map(x => idf(x.e));
    return ids.filter((c, i) => c && ids.indexOf(c) === i && ok(c)); }}""")


def _cur(pg, v):
  return pg.evaluate(f"() => {v['current']}")


def _open(pg, v, cid):
  # відкрити на позиції cid так, як людина: клік по елементу переліку → (кнопка «Збільшити», якщо є) → вікно
  pg.evaluate(f"""(c) => {{ const idf = {v['id']}; document.querySelectorAll('[data-vw-t],[data-vw-opener]').forEach(e => {{ e.removeAttribute('data-vw-t'); e.removeAttribute('data-vw-opener'); }});
    const e = [...document.querySelectorAll({_js(v['items'])})].find(e => e.getClientRects().length && !e.closest('dialog') && idf(e) === c); if (e) e.setAttribute('data-vw-t', '1'); }}""", cid)
  pg.locator('[data-vw-t]').first.click(timeout=5000)
  if v.get('opener'):
    pg.wait_for_function(f"() => !!document.querySelector({_js(v['opener'])})", timeout=5000, polling=100)
    o = pg.locator(v['opener']).first; o.evaluate("e => e.setAttribute('data-vw-opener', '1')"); o.click(timeout=5000)
  else: pg.evaluate("() => { const e = document.querySelector('[data-vw-t]'); if (e) e.setAttribute('data-vw-opener', '1'); }")
  pg.wait_for_function(f"() => !!document.querySelector({_js(v['dialog'])})", timeout=5000, polling=100)
  pg.wait_for_timeout(300)


def _btn(pg, v, rx_key, sel_key):
  if v.get(sel_key): return pg.locator(f"{v['dialog']} {v[sel_key]}").first
  rx = {'next': NEXT, 'prev': PREV, 'close': CLOSE}[rx_key]
  i = pg.evaluate(f"""(rx) => {{ const R = new RegExp(rx, 'i'), d = document.querySelector({_js(v['dialog'])});
    const B = d ? [...d.querySelectorAll('button,[role=button]')] : []; return B.findIndex(b => R.test(b.getAttribute('aria-label') || b.textContent || '')); }}""", rx)
  return pg.locator(f"{v['dialog']} :is(button,[role=button])").nth(i) if i >= 0 else None


def _state(pg, v):
  d = pg.evaluate(f"""() => {{ const d = document.querySelector({_js(v['dialog'])}), a = document.activeElement;
    return {{ open: !!d, focus_in: !!(d && a && d.contains(a)), text: d ? d.innerText : '', sel: {v['sync'] if v.get('sync') else 'null'}, t: window.__vw ? (window.__vw.t1 && window.__vw.t0 ? window.__vw.t1 - window.__vw.t0 : null) : null }}; }}""")
  d['cur'] = _cur(pg, v); return d


def _wait_change(pg, v, before, ms=2500):
  try: pg.wait_for_function(f"(b) => {v['current']} !== b", arg=before, timeout=ms, polling=50)
  except Exception: pass
  pg.wait_real(60)   # кадр після зміни — щоб час кроку (rAF → setTimeout) встиг записатись


def _counter(text, rx):
  m = re.search(rx, text or ''); return (int(m.group(1)), int(m.group(2))) if m else None


def run_viewers(cfg, page, ready, add, COV):
  """Сценарій «переглядач» для кожного опису cfg['viewers'] + перехресні cfg['viewer_cross']. Знахідки — через add(); підсумки — COV['viewers']."""
  starts = {s['name']: s for s in cfg.get('starts', [])}
  VS = {V['name']: setup(V) for V in cfg.get('viewers', [])}
  COV['viewers'] = []

  def begin(v):
    ctx, pg, ev = page(); pg.add_init_script(TIMING_JS)
    st = dict(starts.get(v.get('start'), {'name': v.get('start') or 'головна'}))
    if v.get('js'): st['js'] = ((st.get('js') or '') + ';' + v['js']).strip(';')
    ready(pg, st); return ctx, pg, ev, st['name']

  for name, v in VS.items():
    line = {'name': name, 'n': 0, 'ok': [], 'bad': [], 'ms': []}; COV['viewers'].append(line)
    skip = v['skip']; cnt_rx = v.get('counter', COUNTER)
    def flag(lvl, check, msg, path):
      if check in skip: line['ok'].append(f'{check} — пропущено: {skip[check]}'); return
      add(lvl, 'переглядач: ' + check, name, msg, path); line['bad'].append(check)

    # ── (а)(б)(в)(г)(е) канал за каналом: клавіші · кнопки · колесо — кожен з чистої сторінки ──
    for chan in ('клавіші', 'кнопки', 'колесо'):
      ctx = None
      try:
        ctx, pg, ev, sname = begin(v)
        L = _order(pg, v); line['n'] = len(L)
        if len(L) < 2: line['ok'].append(f'{chan}: видимих позицій {len(L)} — гортати нічого'); break
        k = min(v['steps'], len(L) - 1)
        at = len(L) // 2 if chan == 'кнопки' else 0
        _open(pg, v, L[at]); s = _state(pg, v)
        path = f"{sname} → відкрити «{L[at]}»"
        if s['cur'] != L[at]: flag('✗', 'порядок', f'відкрив «{L[at]}» — вікно показує «{s["cur"]}»', path); continue
        if chan == 'колесо':
          box = pg.evaluate(f"() => {{ const r = document.querySelector({_js(v['dialog'])}).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }}")
          pg.mouse.move(*box)
        seq = [1] * k + [-1] * k + ([-1] if chan == 'клавіші' else [])   # клавіші — ще й край: ← з першої
        pos, errs = at, {}
        for j, dd in enumerate(seq):
          edge = (pos + dd) < 0 or (pos + dd) >= len(L)
          exp = L[(pos + dd) % len(L)] if (not edge or v['wrap']) else L[pos]
          before = s['cur']
          if chan == 'клавіші': pg.keyboard.press('ArrowRight' if dd > 0 else 'ArrowLeft')
          elif chan == 'кнопки':
            b = _btn(pg, v, 'next' if dd > 0 else 'prev', 'next' if dd > 0 else 'prev')
            if b is None: errs.setdefault('порядок', f'кнопки «{"Наступне" if dd > 0 else "Попереднє"}» у вікні нема'); break
            b.click(timeout=4000)
          else:
            pg.mouse.wheel(0, 100 if dd > 0 else -100); pg.wait_real(v['wheel_gap_ms'])
          if exp != before: _wait_change(pg, v, before)
          else: pg.wait_real(250)
          s = _state(pg, v); step = f"{'→' if dd > 0 else '←'} крок {j + 1}"
          if s['cur'] != exp:
            where = ' (край: ' + ('по колу' if v['wrap'] else 'стоп') + ')' if edge else ''
            errs.setdefault('порядок', f'{chan}, {step}{where}: чекав «{exp}» (видимий {"наступний" if dd > 0 else "попередній"}), показало «{s["cur"]}» · видимий ряд: {" ".join(L[:10])}{" …" if len(L) > 10 else ""}')
            pos = L.index(s['cur']) if s['cur'] in L else pos
          else: pos = L.index(exp)
          if chan != 'колесо' and not s['focus_in']: errs.setdefault('фокус', f'{chan}, {step}: фокус вийшов з вікна (на «{pg.evaluate("document.activeElement ? document.activeElement.tagName : null")}») — наступна стрілка вже не дійде')
          c = _counter(s['text'], cnt_rx)
          if c and s['cur'] in L and c != (L.index(s['cur']) + 1, len(L)): errs.setdefault('лічильник', f'{chan}, {step}: «{c[0]} з {c[1]}», а видимо — {L.index(s["cur"]) + 1} з {len(L)}')
          if v.get('sync') and s['sel'] != s['cur']: errs.setdefault('вибір у списку', f'{chan}, {step}: вікно показує «{s["cur"]}», у списку вибрано «{s["sel"]}» (заявлено: синхронно)')
          if s['t'] is not None and chan != 'колесо': line['ms'].append(s['t'])
        for chk, msg in errs.items(): flag('✗', chk, msg, path + f' → {chan} ×{len(seq)}')
        if not errs: line['ok'].append(chan)
        # ── (д) жест: інерція тачпада і серія клацань колеса — по одному кроку ──
        if chan == 'колесо':
          base = s['cur']; i0 = L.index(base) if base in L else 0
          for g, (deltas, gap) in {'тачпад 40 подій по 16 мс': ([max(2, round(60 * 0.9 ** i)) for i in range(40)], 0.016),
                                   'колесо 3 клацання за 0,4 с': ([100, 100, 100], 0.133)}.items():
            if 'жест' in skip: break
            b0 = _cur(pg, v); i0 = L.index(b0) if b0 in L else 0
            for dlt in deltas: pg.mouse.wheel(0, dlt); time.sleep(gap)
            pg.wait_real(v['wheel_gap_ms'])
            c1 = _cur(pg, v); moved = ((L.index(c1) - i0) % len(L)) if c1 in L else None
            if moved != 1: flag('✗', 'жест', f'{g}: зрушило на {moved if moved is not None else "?"} (має бути рівно 1) — «{b0}» → «{c1}»', path + f' → {g}')
            else: line['ok'].append(f'жест: {g}')
      except Exception as e:
        flag('✗', 'не відкрився', f'{chan}: {str(e).splitlines()[0][:140]}', name)
      finally:
        if ctx: ctx.close()
    if line['ms']:
      ms = sorted(line['ms']); med = ms[len(ms) // 2]
      if med > v['max_ms']: flag('⚠', 'повільний крок', f'медіана кроку {med:.0f} мс > {v["max_ms"]} (крок перемальовує перелік? — «зависання»)', name + ' → клавіші / кнопки')
    # ── (є) закрити трьома способами — фокус на тому, хто відкрив, чи на показаному ──
    if line['n'] >= 2 and 'закриття' not in skip:
      for how in ('Esc', '«✕»', 'клік поза'):
        ctx = None
        try:
          ctx, pg, ev, sname = begin(v); L = _order(pg, v); _open(pg, v, L[0])
          b = _cur(pg, v); pg.keyboard.press('ArrowRight'); _wait_change(pg, v, b); shown = _cur(pg, v)   # крок перед закриттям: часто саме він прибирає того, хто відкрив
          if how == 'Esc': pg.keyboard.press('Escape')
          elif how == '«✕»':
            x = _btn(pg, v, 'close', 'close')
            if x is None: flag('✗', 'закриття', 'кнопки «✕» / «Закрити» у вікні нема', sname); continue
            x.click(timeout=4000)
          else:
            pt = pg.evaluate(f"() => {{ const r = document.querySelector({_js(v['dialog'])}).getBoundingClientRect(); return r.left > 30 ? [r.left / 2, innerHeight / 2] : [8, 8]; }}")
            pg.mouse.click(*pt)
          pg.wait_real(250)
          r = pg.evaluate(f"""(sh) => {{ const idf = {v['id']}, a = document.activeElement, open = !!document.querySelector({_js(v['dialog'])});
            const it = a && a.closest && a.closest({_js(v['items'])}), extra = {_js(v.get('close_focus') or '')};
            const ok = !!(a && a !== document.body && a.isConnected && (a.hasAttribute('data-vw-opener') || (it && idf(it) === sh) || (extra && a.matches(extra))));
            return {{ open, ok, on: a ? (a.tagName + ' ' + (a.getAttribute('aria-label') || a.textContent || '').trim().slice(0, 30)) : null }}; }}""", shown)
          path = f"{sname} → відкрити «{L[0]}» → → → {how}"
          if r['open']: flag('✗', 'закриття', f'{how}: вікно не закрилось', path)
          elif not r['ok']: flag('✗', 'закриття', f'{how}: фокус після закриття — «{r["on"]}», а не той, хто відкрив, чи показана позиція «{shown}» (APG Dialog)', path)
          else: line['ok'].append(f'закриття {how}')
        except Exception as e: flag('✗', 'закриття', f'{how}: {str(e).splitlines()[0][:140]}', name)
        finally:
          if ctx: ctx.close()

  # ── (ж) переглядач іншого екрана не бере стан попереднього ──
  for X in cfg.get('viewer_cross', []):
    a, b = VS.get(X['from']), VS.get(X['to'])
    if not a or not b: add('⚠', 'переглядач: конфіг', 'viewer_cross', f'нема переглядача «{X["from"] if not a else X["to"]}»'); continue
    ctx = None; nm = f'{X["from"]} → {X["to"]}'
    try:
      ctx, pg, ev, sname = begin(a); La = _order(pg, a); _open(pg, a, La[0]); c = _cur(pg, a); pg.keyboard.press('ArrowRight'); _wait_change(pg, a, c); pg.keyboard.press('Escape'); pg.wait_real(250)
      st = starts.get(b.get('start'), {}); js = ';'.join(x for x in (st.get('js'), b.get('js')) if x)
      if js: pg.evaluate(js)
      pg.wait_for_timeout(cfg.get('settle_ms', 700))
      Lb = _order(pg, b); _open(pg, b, Lb[0]); s0 = _cur(pg, b); pg.keyboard.press('ArrowRight'); _wait_change(pg, b, s0); s = _state(pg, b); cn = _counter(s['text'], b.get('counter', COUNTER))
      bad = []
      if s0 != Lb[0]: bad.append(f'відкрив «{Lb[0]}» — показало «{s0}»')
      if s['cur'] not in Lb[:2]: bad.append(f'крок → дав «{s["cur"]}» — його нема серед видимих другого екрана')
      if cn and cn[1] != len(Lb): bad.append(f'лічильник «… з {cn[1]}», а видимих {len(Lb)}')
      if bad: add('✗', 'переглядач: стан іншого екрана', nm, ' · '.join(bad), f'{sname} → відкрити → → → Esc → {X["to"]} → відкрити → →')
      COV['viewers'].append({'name': nm, 'n': len(Lb), 'ok': [] if bad else ['стан не просочився'], 'bad': ['стан іншого екрана'] if bad else [], 'ms': []})
    except Exception as e: add('✗', 'переглядач: стан іншого екрана', nm, str(e).splitlines()[0][:140])
    finally:
      if ctx: ctx.close()


def report_lines(COV):
  out = []
  for l in COV.get('viewers', []):
    ms = sorted(l['ms']); med = f' · крок ≈ {ms[len(ms) // 2]:.0f} мс' if ms else ''
    out.append(f"- **{l['name']}** — видимих {l['n']}{med} · ✓ {', '.join(l['ok']) or '—'}" + (f" · ✗ {', '.join(sorted(set(l['bad'])))}" if l['bad'] else ''))
  return out


# ── зуби: сторінка-зразок selftest/viewer.html, чиста — тиша; кожна ?bad= — свій ✗ ──
SELF_CFG = {'steps': 3, 'wheel_gap_ms': 450, 'items': '#main .grid .it',   # 3 кроки й пауза 450 мс (замок зразка 350) — зуби швидше, суть та сама
             'eligible': "id => id !== 'a4'", 'opener': '#zoom', 'dialog': 'dialog#v[open]', 'sync': "(document.querySelector('#main .it.sel') || {dataset: {}}).dataset.id"}
SELF_BAD = {'order': 'порядок', 'focus': 'фокус', 'wheel': 'жест', 'slow': 'повільний крок', 'counter': 'лічильник', 'closefocus': 'закриття', 'leak': 'стан іншого екрана'}


def selftest(run, url):
  bad = 0
  def one(q):
    cfg = {'name': 'viewer ' + (q or 'чиста'), 'url': url + 'viewer.html' + (f'?bad={q}' if q else ''), 'device': 'pc', 'pack_pc': False, 'max_clicks': 0, 'settle_ms': 150, 'after_click_ms': 300,
           'starts': [{'name': 'екран А'}], 'viewers': [dict(SELF_CFG, name='А', start='екран А'), dict(SELF_CFG, name='Б', start='екран А', js="show('b')")],
           'viewer_cross': [{'from': 'А', 'to': 'Б'}]}
    import tempfile; return run(cfg, tempfile.mkdtemp(prefix='tester-vw-'), quiet=True)[2]
  F = one('')
  noise = [f for f in F if f['lvl'] in ('✗', '⚠')]
  bad += bool(noise); print(('✗' if noise else '✓') + ' переглядач: чистий зразок → тиша · ' + (' | '.join(f["kind"] + ': ' + f["msg"][:90] for f in noise) or '0'))
  for q, kind in SELF_BAD.items():
    F = one(q); hit = any(f['kind'] == 'переглядач: ' + kind for f in F)
    bad += not hit; print(('✓' if hit else '✗') + f' переглядач: підкинуто «{q}» → «{kind}» ' + ('спіймано' if hit else 'НЕ спіймано · ' + ' | '.join(f["kind"] for f in F if f['lvl'] != 'ⓘ')))
  return bad, len(SELF_BAD) + 1
