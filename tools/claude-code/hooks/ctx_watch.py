#!/usr/bin/env python3
# ctx_watch.py · гачок ядра (чернетка FAB-2 AE S140 `AE-Simulator:docs/fab/drafts/ctx_watch.py` → перенесено AE S141, «так» Konst 12.11.2026, В-352)
# живе доки: діє правило «ревізія → /compact» (`tools/claude-code/CLAUDE_CODE.md` «Практики») і поріг контексту нічної зміни (`tools/claude-code/NIGHT_SHIFT.md` §3);
#   виклик — диспетчер `hooks/lens-hooks.sh` (UserPromptSubmit · PostToolUse Bash після `git commit` · SessionStart compact).
# Що робить: лічить контекст із журналу сесії й каже, коли пора ревізія — раніше, ніж Claude Code стисне сам. Нічого не блокує («тінню», FAB-2 рядок 4).
#   контекст = остання відповідь основної гілки: usage.input + cache_read + cache_creation (формула statusline). Звірено AE S141: 371 612 проти
#     preTokens 371 723, які Claude Code записав на стисненні; get_session → context_usage у ту саму мить казав 158 731 — відстає, для порогів не годиться.
#   поріг стиснення T = PCT/100 × (W − 20 000): W — CLAUDE_CODE_AUTO_COMPACT_WINDOW (без неї — 1 000 000), PCT — CLAUDE_AUTOCOMPACT_PCT_OVERRIDE
#     (у хмарі 92 ставить платформа, серед змінних середовища Konst його нема). Звірено з get_session → autocompact_state.threshold на двох точках
#     (AE S141): W 1 млн → 901 600 · W 450 тис. → 395 600 (effective_window 430 000).
#   поріг ревізії R = T − найбільший крок − 25 000 (ціна самої ревізії; AE S145, В-373: було 15 000 — заміряно ≥ 24 тис.: ревізія з ✗ почалась ≈ 372 тис.
#   і не закінчилась до автостиснення на 396 тис.). Крок — приріст контексту між двома `git commit` після останнього стиснення,
#     не менше 55 000 (найбільший крок AE S141 — 55 400). Ⓘ «на межі предмета» — від min(250 000, R − 70 000).
# Вироки: на повідомлення Konst — завжди рядок «контекст · % вікна · ревізія на · стиснень у сесії» (з нього маркер, В-353) або ⓘ межа предмета · ⚠ ревізія зараз ·
#   ⚠ кеш холодний (пауза > TTL при ≥ 250 тис.); після коміту — лише ⚠; лік стиснень (compact_boundary) ≥ 2 / ≥ 3 → вимога переїзду (вдень · вночі).
# Ліміти (В-364 п. 2 AE, «так» Konst з підсиленням 13.11.2026): до рядка на повідомлення Konst — «ліміти ЧЧ:ХХ: 5 год X · тиждень Y (сесія: +…)».
#   Джерело — лише результати list_events (rate_limit_event) у журналі сесії: гачок сам лімітів не бачить, тому це ОСТАННІЙ ЗАМІР агента з часом, не «живі» цифри;
#   замір > 60 хв або вікно 5 год уже скинулось → «зміряй», старих цифр не показує; «сесія» — різниця від першого заміру в тому ж вікні (ціна кроку — різницею);
#   стиснення не губить (той самий журнал); пороги нічної зміни — NIGHT_SHIFT.md §3, тут не дублюються. Звірено AE S144: list_events 0,10 · 0,25 о 00:33 ≡ застосунок «Використання» 10 % · 25 % о 00:27.
# Після стиснення (AE S144): перше повідомлення Konst ще без відповіді агента → рядок «≈ переказ + постійна база» замість тиші (база — BASE).
# Запуск: echo '<json гачка>' | python3 ctx_watch.py hook   ·   python3 ctx_watch.py line [журнал]   ·   python3 ctx_watch.py selftest
import datetime, glob, json, os, sys, time, tempfile

RESERVE_OUT, STEP_MIN, REV_COST, SOFT, TTL_S = 20_000, 55_000, 25_000, 250_000, 3600
CAP_DAY, CAP_NIGHT = 2, 3
STALE_S = 3600     # В-364 п. 2 (б): замір лімітів старший за годину — «зміряй»
BASE = 80_000      # постійна база контексту (AE S144, застосунок «Використання» після стиснення № 2: 95,5 тис. = інструменти MCP 35,2 · системні 20,8 · CLAUDE.md двох репо 11,5 ·
                   #   навички 5,6 · системний промпт 5,6 · інструкції MCP 1,5 + переказ і профіль ≈ 15; відкладені інструменти (108 тис.) у вікно не входять)   # стиснень на сесію до переїзду: вдень · у нічну зміну (В-353, `tools/claude-code/CLAUDE_CODE.md` «Скільки стиснень»)

def limits(env=os.environ):
    w = int(env.get('CLAUDE_CODE_AUTO_COMPACT_WINDOW') or 1_000_000); pct = int(env.get('CLAUDE_AUTOCOMPACT_PCT_OVERRIDE') or 92)
    return w, int(pct * (w - RESERVE_OUT) / 100)

def ctx_of(u): return u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('cache_read_input_tokens', 0)

def read(path):
    """→ (останній запит (час, usage) | None, найбільший крок між комітами після останнього стиснення)."""
    last, commits, seen = None, [], set(); read.boundary = {}; read.comp = 0; read.ttl = TTL_S
    for ln in open(path, encoding='utf-8', errors='replace'):
        try: r = json.loads(ln)
        except ValueError: continue
        if r.get('subtype') == 'compact_boundary': last, commits, read.boundary = None, [], r.get('compactMetadata') or {}; read.comp += 1; continue
        if r.get('isSidechain'): continue
        m = r.get('message') if isinstance(r.get('message'), dict) else {}
        u = m.get('usage')
        if r.get('type') == 'assistant' and u:
            last = (r.get('timestamp'), u); cc = u.get('cache_creation') or {}   # В-377 Б: тривалість кешу — з останньої відповіді, що його писала
            if os.environ.get('CTX_INJECT') != '1':   # зуб selftest: тип кешу не читається → «5 хв» зникає
                if cc.get('ephemeral_1h_input_tokens', 0) > 0: read.ttl = 3600
                elif cc.get('ephemeral_5m_input_tokens', 0) > 0: read.ttl = 300
            for c in m.get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('id') not in seen and 'git commit' in str((c.get('input') or {}).get('command', '')):
                    seen.add(c.get('id')); commits.append(ctx_of(u))
    step = max([b - a for a, b in zip(commits, commits[1:]) if b > a] + [0])
    return last, step

def ts_of(iso): return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp()

def rates(path):
    """В-364 п. 2 (а): заміри лімітів з результатів list_events у журналі → [(час, 5 год, скид 5 год, тиждень, скид тижня)], упорядковано за ЧАСОМ ПОДІЇ
    (не за порядком у журналі: list_events з курсором повертає старі події пізніше за нові — AE S144)."""
    out = {}
    try:
        for ln in open(path, encoding='utf-8', errors='replace'):
            if 'unifiedWindows' not in ln: continue   # швидкий відсів: журнал — мегабайти
            try: r = json.loads(ln)
            except ValueError: continue
            if r.get('type') != 'user' or r.get('isSidechain'): continue
            for c in (r.get('message') or {}).get('content') or []:
                if not isinstance(c, dict) or c.get('type') != 'tool_result': continue
                cc = c.get('content'); texts = [x.get('text', '') for x in cc if isinstance(x, dict)] if isinstance(cc, list) else [str(cc)]
                for t in texts:
                    try: data = (json.loads(t).get('ccr') or {}).get('data') or []
                    except (ValueError, AttributeError): continue
                    for e in data:
                        i = ((e.get('rate_limit_event') or {}).get('internal_anthropic_catchall') or {}).get('rate_limit_info') or {}
                        w = i.get('unifiedWindows') or {}; f, s = w.get('five_hour') or {}, w.get('seven_day') or {}
                        if 'utilization' in f and 'utilization' in s and e.get('created_at'):
                            out[e['created_at']] = (ts_of(e['created_at']), f['utilization'], f.get('resetsAt', 0), s['utilization'], s.get('resetsAt', 0))
    except OSError: return []
    return sorted(out.values())

def kyiv(t):
    try:
        from zoneinfo import ZoneInfo; return datetime.datetime.fromtimestamp(t, ZoneInfo('Europe/Kyiv')).strftime('%H:%M')
    except Exception: return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%H:%M UTC')

def lim(path, now):
    """Хвіст рядка: останній замір лімітів (київський час) і різниця за сесію — або «зміряй»."""
    rs = rates(path) if path and os.path.exists(path) else []
    if not rs: return ' · ліміти: заміру нема — list_events kinds ["rate_limit_event"]'
    t, f, fr, s, sr = rs[-1]; d = lambda x: f'{x:.2f}'.replace('.', ',')
    if now >= fr > 0: return f' · ліміти: замір {kyiv(t)} застарів (вікно 5 год скинулось о {kyiv(fr)}) — зміряй (list_events)'
    if now - t > STALE_S: return f' · ліміти: замір {kyiv(t)} застарів ({(now - t) / 60:.0f} хв) — зміряй (list_events)'
    w5 = [x for x in rs if x[2] == fr][0][1]; w7 = [x for x in rs if x[4] == sr][0][3]
    return f' · ліміти {kyiv(t)}: 5 год {d(f)} · тиждень {d(s)} (сесія: тиждень +{d(s - w7)}; це вікно 5 год +{d(f - w5)}; скид 5 год {kyiv(fr)})'

def marker(path, now, why='<причина>'):
    """Маркер — останній блок звіту, зібраний машиною (Konst S147: «щоб я не шукав його в тексті відповіді»): список, рядок на показник —
    зліва плашка інлайн-коду однакової ширини (смуга + відсоток), справа пояснення; погляд іде вниз одним стовпчиком.
    КАТАЛОГ ВИГЛЯДІВ (проба на iPhone, Konst 24.11.2026, ядро AUDIT) — щоб наступна зміна почалась з готового, а не з нуля:
      А таблиця «плашка | пояснення» — читається легко, «надто масивно» (5–6 рядків екрана щовідповіді);
      Б стовпчик-список «плашка — пояснення» — ОБРАНО: «за один погляд сканую всі показники», ієрархія;
      В один рядок, кожне число плашкою — «очима бігати вліво-вправо»; до 24.11 — один рядок, плашка лише контексту (v23);
      до v23 — 12 клітинок █▓░ одним рядком зі словом «ctx» і емодзі — «зайвий шум, слова інструменту».
    Посилення Б (24.11): усі плашки однієї ширини (15 знаків) — пояснення стоять рівно; 5 год і тиждень — теж смугою: відсотки порівнюються
    оком (практика рядків стану Claude Code — смуги 5h / 7d зі скидом поруч: github dantereve/claude-code-usage-statusline, leeguooooo/
    claude-code-usage-bar, 24.11.2026; кольору markdown не має — тривога жирним). Дешева розвідка нового вигляду: намалювати 2–3 варіанти
    прямо в чаті → скрін Konst з iPhone → вибір; смуга — Block Elements (█ і восьмі ▏…▉: найширша підтримка шрифтів; ▰▱ / ■□ — ризик
    у мобільних шрифтах), порожнє — пробіли (фон плашки = доріжка).
    Тривога — жирним поясненням: ліміт ≥ 0,75 (поріг allowed_warning API), контекст ≥ порогу ревізії. Замір лімітів старший за 10 хв —
    з часом заміру; за годину — «зміряй» (24.11: старий замір 48 % показано, коли API вже давав 0,90)."""
    n = numbers(path); pct = n['ctx'] * 100 // n['w'] if n['w'] else 0
    def plate(p):
        c = min(p, 100) * 10 / 100; f = int(c); part = ' ▏▎▍▌▋▊▉'[int((c - f) * 8)] if f < 10 else ''
        return f"`{('█' * f + part).rstrip().ljust(10)} {f'{p}%':>4}`"
    def text(t, x): return f"**{t}**" if x else t
    rows = [f"- {plate(pct)} " + text('контекст — пора ревізія' if n['w'] and n['ctx'] >= n['r'] else 'контекст', n['w'] and n['ctx'] >= n['r']) + f" · {why}"]
    rs = rates(path) if path and os.path.exists(path) else []
    if rs and now - rs[-1][0] <= STALE_S and not (now >= rs[-1][2] > 0):
        t, f5, r5, w7, r7 = rs[-1]
        try:
            from zoneinfo import ZoneInfo; day = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'нд'][datetime.datetime.fromtimestamp(r7, ZoneInfo('Europe/Kyiv')).weekday()] + ' '
        except Exception: day = ''
        old = f" (замір {kyiv(t)})" if now - t > 600 else ''
        rows.append(f"- {plate(round(f5 * 100))} " + text(f"5 год · скид {kyiv(r5)}", f5 >= 0.75) + old)
        rows.append(f"- {plate(round(w7 * 100))} " + text(f"тиждень · скид {day}{kyiv(r7)}", w7 >= 0.75) + old)
    else: rows.append(f"- `{'?':>15}` ліміти — зміряй")
    cc = cache(n, now)
    if cc: rows.append(f"- `{('до ' + cc.split('теплий до ≈', 1)[1].split(' ')[0]) if 'теплий до' in cc else 'холодний':>15}` кеш" + ('' if 'теплий до' in cc else ' — перший запит перепише контекст'))
    return '\n'.join(rows)

def numbers(path, env=os.environ):
    last, step = read(path) if path and os.path.exists(path) else (None, 0)
    w, t = limits(env); step = max(step, STEP_MIN); r = t - step - REV_COST
    return dict(last=last, ctx=ctx_of(last[1]) if last else 0, w=w, t=t, r=r, soft=min(SOFT, r - 70_000), step=step, comp=getattr(read, 'comp', 0) if last or path else 0,
                post=(getattr(read, 'boundary', {}) or {}).get('postTokens', 0) if path else 0, ttl=getattr(read, 'ttl', TTL_S) if last else TTL_S)

def cache(n, now):
    """В-377 Б (Konst S146: «знати наперед, до котрої відповідь дешевша»): «кеш 1 год: теплий до ≈HH:MM (Київ)» = остання відповідь основної гілки
    (будь-якого типу — і та, що на фонову задачу) + TTL її кешу. Рядок приходить на повідомлення Konst і після коміту, тож похибка — хвилини: «≈».
    Кожне читання кешу продовжує йому життя (platform.claude.com «Prompt caching», 14.11.2026 — В-377 AE) — тому від останньої відповіді, не від першої."""
    if not n['last']: return ''
    until = ts_of(n['last'][0]) + n['ttl']; lab = '1 год' if n['ttl'] >= 3600 else f"{n['ttl'] // 60} хв"; t = kyiv(until)
    z = '' if 'UTC' in t else ' (Київ)'
    return f" · кеш {lab}: теплий до ≈{t}{z}" if now < until else f" · кеш {lab}: холодний з ≈{t}{z} — перший запит перепише контекст"


def cap(n):
    c = n['comp']
    if c >= CAP_NIGHT: return f" · ⚠ стиснень {c} ≥ {CAP_NIGHT} — переїзд: вдень на найближчій межі предмета, вночі — на межі кроку (ревізія → ранковий звіт → стоп)"
    if c >= CAP_DAY: return f" · стиснень {c} — вдень переїзд на найближчій межі предмета (вночі — до {CAP_NIGHT})"
    return ''

def verdict(n, now, event):
    if not n['last']:   # AE S144: перше повідомлення після стиснення — відповіді ще нема; було тихо, Konst дивився в застосунок
        if event == 'UserPromptSubmit' and n['comp'] and n['post']:
            e = n['post'] + BASE
            return f"контекст ≈ {e // 1000} тис. (переказ {n['post'] // 1000} + постійна база ≈ {BASE // 1000}; точне — після першої відповіді) · {e * 100 // n['w']}% вікна {n['w'] // 1000} тис. · ревізія на {n['r'] // 1000} тис. · стиснень у сесії {n['comp']} (ctx_watch)" + cap(n)
        return None
    ctx, u = n['ctx'], n['last'][1]
    gap = now - datetime.datetime.fromisoformat(n['last'][0].replace('Z', '+00:00')).timestamp()
    ttl = n['ttl']
    k = lambda x: f'{x // 1000} тис.'
    tail = f"(стиснення на {k(n['t'])}, ревізія на {k(n['r'])}; найбільший крок {k(n['step'])} — ctx_watch)"
    if event == 'UserPromptSubmit' and gap > ttl and ctx >= SOFT:
        return f"⚠ кеш холодний (пауза {gap / 60:.0f} хв > {ttl // 60}) · контекст {k(ctx)} — перший запит перепише його весь. Ревізію зроблено → нова сесія зі стартового; ні → коротка ревізія → /compact {tail}"
    if ctx >= n['r']:
        return f"⚠ контекст {k(ctx)} ≥ порога ревізії — зараз: ревізія (усе в коміти, самері §0) → вдень запропонуй Konst /compact, вночі — далі за NIGHT_SHIFT §3 {tail}" + cap(n)
    if event == 'UserPromptSubmit' and ctx >= n['soft']:
        return f"ⓘ контекст {k(ctx)} — на найближчій межі предмета: ревізія → /compact {tail}" + cap(n)
    if event == 'UserPromptSubmit':   # В-353: рядок щоповідомлення — маркер навантаження береться з нього, без окремого виклику інструмента
        return f"контекст {k(ctx)} · {ctx * 100 // n['w']}% вікна {k(n['w'])} · ревізія на {k(n['r'])} · стиснень у сесії {n['comp']} (ctx_watch)" + cache(n, now) + cap(n)
    return None

def newest(home='~'):
    # S141: найновіший журнал — не обов'язково свій: дочірній `claude -p` (аудит) пише свій у ту саму теку → чужі числа (108 тис. і 0 стиснень
    #   замість 243 тис. і 1). Свій — за CLAUDE_CODE_SESSION_ID (= ім'я файла журналу, звірено 12.11.2026); нема — найновіший.
    sid = os.environ.get('CLAUDE_CODE_SESSION_ID', '')
    own = glob.glob(os.path.expanduser(f'{home}/.claude/projects/*/{sid}.jsonl')) if sid else []
    fs = own or glob.glob(os.path.expanduser(f'{home}/.claude/projects/*/*.jsonl'))
    return max(fs, key=os.path.getmtime) if fs else ''

def line(path):
    n = numbers(path); k = lambda x: f'{x // 1000} тис.'
    return f"контекст {k(n['ctx'])} · {n['ctx'] * 100 // n['w']}% вікна {k(n['w'])} · стиснення на {k(n['t'])} · ревізія на {k(n['r'])} (найбільший крок {k(n['step'])}) · стиснень у сесії {n['comp']}" + cache(n, time.time()) + lim(path, time.time())

def _hc():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import handoff_check; return handoff_check

def revise():
    """REV-1 (AE S143, В-361): поріг ревізії сам запускає handoff_check revision (повний прохід + чек-лист + мітка для precompact_guard),
    раз на стан HEAD усіх репо сесії (повтор без нових комітів — короткий рядок). Помилка — рядок, не падіння гачка."""
    try:
        hc = _hc(); once = f'/tmp/lens-ctxrev-{hc.sid()}'
        t, _ = hc.revision(os.environ.get('LENS_ROOT') or '/home/user', once)
        if not t: return ' · ревізію на цьому HEAD уже дано (ctx_watch) — після виправлень і коміту дасть знову'
        # AE S154 (💡 ретро нічної зміни, «так» Konst): за порогом кожен коміт давав повний звіт ≈ 3 тис. токенів (3 рази поспіль,
        # незмінний, крім одного ✗). Повний — перший раз; далі — лише ✗ і рядки, яких не було в попередньому прогоні, + печатка.
        prev_p = once + '.txt'; prev = open(prev_p, encoding='utf-8').read() if os.path.exists(prev_p) else None
        open(prev_p, 'w', encoding='utf-8').write(t)
        if prev is None:
            return '\n\nРЕВІЗІЯ — сама, на порозі (REV-1; той самий прохід, що на слово Konst «ревізія»):\n' + t[:6000]
        body, seal = t.split('\n\n' + hc.CHECKLIST)[0], t.rstrip().splitlines()[-1]
        old = set(prev.splitlines())
        new = [l for l in body.splitlines() if l.strip() and (l not in old or l.strip().startswith('✗')) and l != seal]
        return ('\n\nРЕВІЗІЯ на порозі — лише ✗ і нове проти попереднього прогону (повний звіт і чек-лист — '
                'python3 <ядро>/tools/claude-code/handoff_check.py revision):\n' + '\n'.join(new[:60]) + ('\n' if new else '') + seal)
    except Exception as e: return f' · ревізія сама не запустилась ({type(e).__name__}) — python3 <ядро>/tools/claude-code/handoff_check.py revision'

def hook(inp, now=None):
    ev = inp.get('hook_event_name') or 'UserPromptSubmit'
    if ev == 'PostToolUse' and 'git commit' not in str((inp.get('tool_input') or {}).get('command', '')): return ''
    n = numbers(inp.get('transcript_path', ''))
    if ev == 'SessionStart':
        if inp.get('source') != 'compact': return ''
        b, k = getattr(read, 'boundary', {}), lambda x: f'{x // 1000} тис.'
        v = (f"Після стиснення № {n['comp']} ({b.get('trigger', '?')}): контекст {k(b.get('preTokens', 0))} → {k(b.get('postTokens', 0))} (лише переказ; разом із постійною базою ≈ {k(b.get('postTokens', 0) + BASE)}, точне — у рядку ctx_watch після першої відповіді) · " if b else 'Після стиснення: ') + \
            f"наступне стиснення на {k(n['t'])}, ревізія на {k(n['r'])} (ctx_watch). Перша відповідь — звір переказ із самері §0 і допиши в §1 рядок «стиснення N: переказ ✓ / що загубив»." + cap(n)
        try: os.remove(_hc().rev_mark())   # REV-1: мітка «ревізію зроблено» — до стиснення; після нього для ручного /compact потрібна нова
        except (OSError, ImportError): pass
    else:
        v = verdict(n, now or time.time(), ev)
        if v and v.startswith(('⚠ контекст', '⚠ кеш холодний')): v += revise()   # REV-1: на порозі — та сама ревізія, що й на слово Konst (і вночі: після коміту)
        if ev == 'UserPromptSubmit' and os.path.exists(inp.get('transcript_path') or ''):   # В-364 п. 2: ліміти — лише на повідомлення Konst, не після коміту
            v = (v or 'ctx_watch') + lim(inp.get('transcript_path', ''), now or time.time()) + \
                '\nмаркер (S147) — наприкінці відповіді: list_events kinds ["rate_limit_event"] → python3 <ядро>/tools/claude-code/hooks/ctx_watch.py marker "<причина>" → останній рядок звіту як є'
    return json.dumps({'hookSpecificOutput': {'hookEventName': ev, 'additionalContext': v}}, ensure_ascii=False) if v else ''

def selftest():
    d = tempfile.mkdtemp(); bad = 0; total = 0; T0 = 1_800_000_000
    iso = lambda s: datetime.datetime.fromtimestamp(s, datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    def a(ctx, ago=60, commit=False, side=False, h1=True, tid='x'):
        c = [{'type': 'tool_use', 'id': f'{tid}{ctx}', 'input': {'command': 'git commit -m x'}}] if commit else []
        return {'type': 'assistant', 'isSidechain': side, 'timestamp': iso(T0 - ago), 'message': {'id': f'm{ctx}{side}', 'content': c,
                'usage': {'input_tokens': 2, 'cache_read_input_tokens': ctx - 1002, 'cache_creation_input_tokens': 1000,
                          'cache_creation': {'ephemeral_1h_input_tokens': 1000 if h1 else 0, 'ephemeral_5m_input_tokens': 0 if h1 else 1000}}}}
    def tr(name, rows):
        p = f'{d}/{name}.jsonl'; open(p, 'w').write('\n'.join(json.dumps(r) for r in rows) + '\n'); return p
    E = {'CLAUDE_CODE_AUTO_COMPACT_WINDOW': '450000', 'CLAUDE_AUTOCOMPACT_PCT_OVERRIDE': '92'}
    def case(name, ok):
        nonlocal bad, total; print(('✓ ' if ok else '✗ ') + name); bad += not ok; total += 1
    case('поріг стиснення: W 450 тис. → 395 600, W 1 млн → 901 600 (обидва = autocompact_state.threshold, AE S141)',
         limits(E)[1] == 395_600 and limits({'CLAUDE_AUTOCOMPACT_PCT_OVERRIDE': '92'})[1] == 901_600)
    os.environ.update(E, LENS_ROOT=f'{d}/empty', LENS_REV_MARK=f'{d}/revmark')   # REV-1: тест не ганяє ревізію справжніх репо й не ставить справжню мітку
    v = lambda p, ev='UserPromptSubmit', ago=0: verdict(numbers(p), T0 + ago, ev)
    case('120 тис., повідомлення Konst — інформаційний рядок (маркер без виклику інструмента)', (v(tr('a', [a(120_000)])) or '').startswith('контекст 120 тис. · 26% вікна'))
    case('120 тис. після коміту — тиша', v(tr('a2', [a(120_000)]), 'PostToolUse') is None)
    case('260 тис. — ⓘ межа предмета', (v(tr('b', [a(260_000)])) or '').startswith('ⓘ'))
    case('320 тис. (> 395,6 − 55 − 25 = 315,6) — ⚠ ревізія зараз', (v(tr('c', [a(320_000)])) or '').startswith('⚠ контекст'))
    p = tr('d', [a(100_000, commit=True), a(190_000, commit=True), a(300_000)])
    case('крок 90 тис. між комітами → поріг ревізії 280,6 тис.; 300 тис. — ⚠', numbers(p)['r'] == 280_600 and (v(p) or '').startswith('⚠ контекст'))
    p = tr('e', [a(100_000, commit=True), a(300_000, commit=True), {'type': 'system', 'subtype': 'compact_boundary'}, a(110_000, commit=True), a(120_000)])
    case('після стиснення кроки рахуються наново; 120 тис. — без ⚠', numbers(p)['step'] == STEP_MIN and not (v(p) or '').startswith('⚠'))
    case('відповідь субагента (isSidechain) не рахується', (v(tr('f', [a(120_000), a(390_000, side=True)])) or '').startswith('контекст 120 тис.'))
    B = {'type': 'system', 'subtype': 'compact_boundary'}
    case('2 стиснення — «переїзд на межі предмета»', 'стиснень 2 — вдень переїзд' in (v(tr('n', [a(300_000), B, a(300_000), B, a(120_000)])) or ''))
    case('3 стиснення — ⚠ переїзд і вночі', '⚠ стиснень 3' in (v(tr('o', [B, B, B, a(120_000)])) or ''))
    case('1 стиснення — без вимоги переїзду', 'переїзд' not in (v(tr('q', [B, a(120_000)])) or 'переїзд'))
    case('300 тис., пауза 70 хв — ⚠ кеш холодний', (v(tr('g', [a(300_000, ago=4200)])) or '').startswith('⚠ кеш холодний'))
    case('кеш 5 хв (кредити), пауза 6 хв — ⚠ кеш холодний', (v(tr('h', [a(300_000, ago=360, h1=False)])) or '').startswith('⚠ кеш холодний'))
    case('після коміту (PostToolUse): ⓘ мовчить, ⚠ каже', v(tr('i', [a(260_000)]), 'PostToolUse') is None and (v(tr('j', [a(330_000)]), 'PostToolUse') or '').startswith('⚠'))
    case('PostToolUse не коміт — тиша', hook({'hook_event_name': 'PostToolUse', 'tool_input': {'command': 'ls'}, 'transcript_path': tr('k', [a(330_000)])}) == '')
    case('PostToolUse коміт — JSON з additionalContext', '"additionalContext"' in hook({'hook_event_name': 'PostToolUse', 'tool_input': {'command': 'git commit -m y'}, 'transcript_path': tr('l', [a(330_000)])}, T0))
    case('журналу нема — тиша', hook({'transcript_path': f'{d}/none.jsonl'}) == '')
    p = tr('m', [a(370_000), {'type': 'system', 'subtype': 'compact_boundary', 'compactMetadata': {'trigger': 'auto', 'preTokens': 371_723, 'postTokens': 14_494}}])
    o = hook({'hook_event_name': 'SessionStart', 'source': 'compact', 'transcript_path': p})
    case('SessionStart compact: «№ 1», «371 тис. → 14 тис.», пороги, вимога рядка «стиснення N»', all(x in o for x in ('№ 1', '371 тис. → 14 тис.', 'ревізія на 315 тис.', 'стиснення N')))
    case('SessionStart startup — тиша', hook({'hook_event_name': 'SessionStart', 'source': 'startup', 'transcript_path': p}) == '')
    h = f'{d}/home'; os.makedirs(f'{h}/.claude/projects/p1'); os.makedirs(f'{h}/.claude/projects/p2')
    open(f'{h}/.claude/projects/p1/OWN.jsonl', 'w').write('x'); time.sleep(0.01); open(f'{h}/.claude/projects/p2/CHILD.jsonl', 'w').write('x')
    os.environ['CLAUDE_CODE_SESSION_ID'] = 'OWN'
    case('рядок руками: свій журнал за CLAUDE_CODE_SESSION_ID, не новіший чужий (аудит claude -p)', newest(h).endswith('OWN.jsonl'))
    # REV-1: поріг ревізії сам дає повний прохід (раз на HEAD); нижче порога — ні; після стиснення мітка ревізії знімається
    import subprocess; rt = f'{d}/root'; rp = f'{rt}/Prod'; os.makedirs(f'{rp}/docs/summary')
    open(f'{rp}/docs/summary/P_SUMMARY_X.md', 'w').write('## §0 ВІДКРИТЕ\n- x\n\n```text\nСТАРТ: x\n```\n')
    for c in (['init', '-q'], ['-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 's', '--allow-empty'], ['add', '-A'], ['-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 's2']):
        subprocess.run(['git', '-C', rp, *c], capture_output=True)
    os.environ.update(LENS_ROOT=rt, CLAUDE_CODE_SESSION_ID='REVTEST', LENS_REV_MARK=f'{d}/revmark')
    for f in ('/tmp/lens-ctxrev-REVTEST', '/tmp/lens-ctxrev-REVTEST.txt'):
        if os.path.exists(f): os.remove(f)
    o1 = hook({'hook_event_name': 'UserPromptSubmit', 'transcript_path': tr('r1', [a(330_000)])}, T0); o2 = hook({'hook_event_name': 'PostToolUse', 'tool_input': {'command': 'git commit -m z'}, 'transcript_path': tr('r2', [a(330_000)])}, T0)
    case('330 тис. — ⚠ і сама ревізія: вивід handoff_check + чек-лист, мітка для сторожа стиснення', 'РЕВІЗІЯ — сама' in o1 and '— Prod' in o1 and 'Звіт Konst' in o1 and os.path.exists(f'{d}/revmark'))
    case('той самий HEAD після коміту (і вночі) — без повтору проходу, короткий рядок', 'уже дано' in o2 and 'РЕВІЗІЯ — сама' not in o2)
    case('260 тис. (ⓘ) — ревізію сама не запускає', 'РЕВІЗІЯ' not in (hook({'transcript_path': tr('r3', [a(260_000)])}, T0) or ''))
    hook({'hook_event_name': 'SessionStart', 'source': 'compact', 'transcript_path': p})
    case('після стиснення мітку ревізії знято (ручний /compact знову вимагатиме ревізію)', not os.path.exists(f'{d}/revmark'))
    [os.remove(x) for x in ('/tmp/lens-ctxrev-REVTEST', '/tmp/lens-ctxrev-REVTEST.txt') if os.path.exists(x)]
    # В-364 п. 2 (AE S144): ліміти з результатів list_events у журналі
    def le(*evs, sid=False):   # evs: (секунд до T0, 5 год, скид 5 год, тиждень)
        data = [{'created_at': iso(T0 - ago), 'rate_limit_event': {'internal_anthropic_catchall': {'rate_limit_info': {'unifiedWindows': {
                 'five_hour': {'utilization': f5, 'resetsAt': r5}, 'seven_day': {'utilization': w7, 'resetsAt': T0 + 9 * 86400}}}}}} for ago, f5, r5, w7 in evs]
        return {'type': 'user', 'isSidechain': sid, 'message': {'role': 'user', 'content': [{'type': 'tool_result', 'content': [{'type': 'text', 'text': json.dumps({'ccr': {'data': data}})}]}]}}
    R5 = T0 + 3 * 3600; os.environ['LENS_ROOT'] = f'{d}/empty'
    L = lambda rows, ago=0: hook({'transcript_path': tr('lim', rows)}, T0 + ago)
    o = L([le((7200, 0.01, R5, 0.18)), a(120_000), le((600, 0.12, R5, 0.25)), le((9000, 0.0, R5, 0.17))])
    case('ліміти: найновіший замір за часом події (не за порядком у журналі — курсор повертає старі пізніше); сесія — від першого заміру того ж вікна',
         '5 год 0,12 · тиждень 0,25' in o and 'тиждень +0,08' in o and 'це вікно 5 год +0,12' in o)
    case('замір старший за 60 хв — «зміряй», старих цифр нема', 'застарів (70 хв)' in (o := L([a(120_000), le((4200, 0.3, R5, 0.2))])) and '0,30' not in o)
    case('вікно 5 год уже скинулось — «зміряй»', 'вікно 5 год скинулось' in L([a(120_000), le((600, 0.3, T0 - 60, 0.2))]))
    case('заміру нема — підказка list_events', 'заміру нема' in L([a(120_000)]))
    case('замір субагента (isSidechain) не рахується', 'заміру нема' in L([a(120_000), le((60, 0.5, R5, 0.5), sid=True)]))
    case('після коміту ліміти не друкуються (шум уночі)', 'ліміти' not in (hook({'hook_event_name': 'PostToolUse', 'tool_input': {'command': 'git commit -m y'}, 'transcript_path': tr('lc', [a(330_000), le((60, 0.1, R5, 0.2))])}, T0) or ''))
    o = hook({'transcript_path': tr('pc', [a(300_000), {'type': 'system', 'subtype': 'compact_boundary', 'compactMetadata': {'trigger': 'manual', 'preTokens': 300_000, 'postTokens': 16_000}}])}, T0)
    case('перше повідомлення після стиснення (відповіді ще нема) — «≈ 96 тис.» замість тиші', 'контекст ≈ 96 тис.' in o and 'точне — після першої відповіді' in o)
    # В-377 Б: «кеш … теплий до ≈HH:MM» — від останньої відповіді + TTL її кешу
    c1 = v(tr('k1', [a(120_000, ago=60)])) or ''
    case('кеш 1 год: «теплий до» = остання відповідь + 60 хв, київський час', f'кеш 1 год: теплий до ≈{kyiv(T0 - 60 + 3600)}' in c1)
    case('кеш 5 хв (кредити): «теплий до» = остання відповідь + 5 хв', f'кеш 5 хв: теплий до ≈{kyiv(T0 - 60 + 300)}' in (v(tr('k2', [a(120_000, ago=60, h1=False)])) or ''))
    z = a(130_000, ago=30); z['message']['usage'].update(cache_creation_input_tokens=0, cache_creation={'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 0})
    case('відповідь без запису кешу (лише читання) — тип від попередньої (5 хв), час — від неї', f'кеш 5 хв: теплий до ≈{kyiv(T0 - 30 + 300)}' in (v(tr('k3', [a(120_000, ago=90, h1=False), z])) or ''))
    case('пауза > TTL при малому контексті — «холодний з», без ⚠', 'кеш 1 год: холодний з' in (o := v(tr('k4', [a(120_000, ago=4000)])) or '') and not o.startswith('⚠'))
    case('рядок руками (line) теж має «кеш … теплий до / холодний з»', 'кеш 1 год:' in line(tr('k5', [a(120_000)])))
    # S147 → 24.11 (вигляд Б): маркер — список, плашки однакової ширини
    mk = marker(tr('mk', [a(207_000, ago=60), le((300, 0.44, R5, 0.52))]), T0, 'три коміти')
    rows = mk.split('\n'); plates = [r.split('`')[1] for r in rows]
    case('маркер Б: 4 рядки списку — контекст · 5 год · тиждень · кеш; причина при контексті', len(rows) == 4 and all(r.startswith('- `') for r in rows)
         and rows[0] == '- `████▌       46%` контекст · три коміти' and '5 год · скид ' in rows[1] and 'тиждень · скид ' in rows[2] and f'до {kyiv(T0 - 60 + 3600)}' in rows[3])
    case('маркер Б: плашки однієї ширини (пояснення рівно)', len({len(p) for p in plates}) == 1)
    case('маркер Б: 5 год і тиждень — смугою з відсотком', rows[1].startswith('- `████▍       44%`') and rows[2].startswith('- `█████▏      52%`'))
    case('маркер: замір лімітів старший за 10 хв → час заміру поруч', '(замір ' in marker(tr('mk4', [a(207_000), le((900, 0.44, R5, 0.52))]), T0))
    case('маркер: замір лімітів старший за 60 хв → «ліміти — зміряй», старих цифр нема', 'ліміти — зміряй' in (o := marker(tr('mk2', [a(207_000), le((4000, 0.44, R5, 0.52))]), T0)) and '44%' not in o)
    case('маркер: ліміт ≥ 75 % (поріг API) → пояснення жирним', '**5 год · скид ' in marker(tr('mk3', [a(207_000), le((60, 0.85, R5, 0.52))]), T0))
    # S154: повторна ревізія на порозі — лише ✗ і нове + печатка; перша — повна
    class _F:
        CHECKLIST = 'ЧЕК'; n = 0
        def sid(self): return 'st-' + str(os.getpid())
        def revision(self, root, once):
            _F.n += 1; return (f'  ✓ старе\n  ✗ біда\n  ⚠ нове{_F.n}\n\nЧЕК\n\nревізія ✗ · HEAD x@{_F.n}', True)
    global _hc; keep = _hc; _hc = lambda: _F()
    try:
        r1, r2 = revise(), revise()
    finally:
        _hc = keep
        for x in ('', '.txt'):
            try: os.remove(f'/tmp/lens-ctxrev-st-{os.getpid()}' + x)
            except OSError: pass
    case('ревізія на порозі: перша — повна з чек-листом', 'ЧЕК' in r1 and '✓ старе' in r1)
    case('ревізія на порозі: друга — лише ✗ і нове + печатка, без старого ✓ і чек-листа',
         '✗ біда' in r2 and '⚠ нове2' in r2 and '✓ старе' not in r2 and 'ЧЕК' not in r2 and r2.rstrip().endswith('HEAD x@2'))
    print(f'─── ctx_watch selftest: {total - bad}/{total} ───'); return 1 if bad else 0

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'hook'
    if cmd == 'selftest': sys.exit(selftest())
    if cmd == 'hold':   # AE S145 (В-373): для precompact_guard — «контекст · стеля відкладення автостиснення» (стеля = W − 20 000, вікно Claude Code)
        n = numbers(sys.argv[2] if len(sys.argv) > 2 else ''); print(n['ctx'], n['w'] - RESERVE_OUT); sys.exit(0)
    if cmd == 'line': print(line(sys.argv[2] if len(sys.argv) > 2 else newest())); sys.exit(0)
    if cmd == 'marker': print(marker(newest(), time.time(), sys.argv[2] if len(sys.argv) > 2 else '<причина>')); sys.exit(0)
    try: inp = json.load(sys.stdin)
    except ValueError: inp = {}
    out = hook(inp)
    if out: print(out)
