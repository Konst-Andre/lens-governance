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
#   поріг ревізії R = T − найбільший крок − 15 000 (ціна самої ревізії). Крок — приріст контексту між двома `git commit` після останнього стиснення,
#     не менше 55 000 (найбільший крок AE S141 — 55 400). Ⓘ «на межі предмета» — від min(250 000, R − 70 000).
# Вироки: на повідомлення Konst — завжди рядок «контекст · % вікна · ревізія на · стиснень у сесії» (з нього маркер, В-353) або ⓘ межа предмета · ⚠ ревізія зараз ·
#   ⚠ кеш холодний (пауза > TTL при ≥ 250 тис.); після коміту — лише ⚠; лік стиснень (compact_boundary) ≥ 2 / ≥ 3 → вимога переїзду (вдень · вночі).
# Запуск: echo '<json гачка>' | python3 ctx_watch.py hook   ·   python3 ctx_watch.py line [журнал]   ·   python3 ctx_watch.py selftest
import datetime, glob, json, os, sys, time, tempfile

RESERVE_OUT, STEP_MIN, REV_COST, SOFT, TTL_S = 20_000, 55_000, 15_000, 250_000, 3600
CAP_DAY, CAP_NIGHT = 2, 3   # стиснень на сесію до переїзду: вдень · у нічну зміну (В-353, `tools/claude-code/CLAUDE_CODE.md` «Скільки стиснень»)

def limits(env=os.environ):
    w = int(env.get('CLAUDE_CODE_AUTO_COMPACT_WINDOW') or 1_000_000); pct = int(env.get('CLAUDE_AUTOCOMPACT_PCT_OVERRIDE') or 92)
    return w, int(pct * (w - RESERVE_OUT) / 100)

def ctx_of(u): return u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('cache_read_input_tokens', 0)

def read(path):
    """→ (останній запит (час, usage) | None, найбільший крок між комітами після останнього стиснення)."""
    last, commits, seen = None, [], set(); read.boundary = {}; read.comp = 0
    for ln in open(path, encoding='utf-8', errors='replace'):
        try: r = json.loads(ln)
        except ValueError: continue
        if r.get('subtype') == 'compact_boundary': last, commits, read.boundary = None, [], r.get('compactMetadata') or {}; read.comp += 1; continue
        if r.get('isSidechain'): continue
        m = r.get('message') if isinstance(r.get('message'), dict) else {}
        u = m.get('usage')
        if r.get('type') == 'assistant' and u:
            last = (r.get('timestamp'), u)
            for c in m.get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('id') not in seen and 'git commit' in str((c.get('input') or {}).get('command', '')):
                    seen.add(c.get('id')); commits.append(ctx_of(u))
    step = max([b - a for a, b in zip(commits, commits[1:]) if b > a] + [0])
    return last, step

def numbers(path, env=os.environ):
    last, step = read(path) if path and os.path.exists(path) else (None, 0)
    w, t = limits(env); step = max(step, STEP_MIN); r = t - step - REV_COST
    return dict(last=last, ctx=ctx_of(last[1]) if last else 0, w=w, t=t, r=r, soft=min(SOFT, r - 70_000), step=step, comp=getattr(read, 'comp', 0) if last or path else 0)

def cap(n):
    c = n['comp']
    if c >= CAP_NIGHT: return f" · ⚠ стиснень {c} ≥ {CAP_NIGHT} — переїзд: вдень на найближчій межі предмета, вночі — на межі кроку (ревізія → ранковий звіт → стоп)"
    if c >= CAP_DAY: return f" · стиснень {c} — вдень переїзд на найближчій межі предмета (вночі — до {CAP_NIGHT})"
    return ''

def verdict(n, now, event):
    if not n['last']: return None
    ctx, u = n['ctx'], n['last'][1]
    gap = now - datetime.datetime.fromisoformat(n['last'][0].replace('Z', '+00:00')).timestamp()
    ttl = TTL_S if (u.get('cache_creation') or {}).get('ephemeral_1h_input_tokens', 0) or not u.get('cache_creation_input_tokens') else 300
    k = lambda x: f'{x // 1000} тис.'
    tail = f"(стиснення на {k(n['t'])}, ревізія на {k(n['r'])}; найбільший крок {k(n['step'])} — ctx_watch)"
    if event == 'UserPromptSubmit' and gap > ttl and ctx >= SOFT:
        return f"⚠ кеш холодний (пауза {gap / 60:.0f} хв > {ttl // 60}) · контекст {k(ctx)} — перший запит перепише його весь. Ревізію зроблено → нова сесія зі стартового; ні → коротка ревізія → /compact {tail}"
    if ctx >= n['r']:
        return f"⚠ контекст {k(ctx)} ≥ порога ревізії — зараз: ревізія (усе в коміти, самері §0) → вдень запропонуй Konst /compact, вночі — далі за NIGHT_SHIFT §3 {tail}" + cap(n)
    if event == 'UserPromptSubmit' and ctx >= n['soft']:
        return f"ⓘ контекст {k(ctx)} — на найближчій межі предмета: ревізія → /compact {tail}" + cap(n)
    if event == 'UserPromptSubmit':   # В-353: рядок щоповідомлення — маркер навантаження береться з нього, без окремого виклику інструмента
        return f"контекст {k(ctx)} · {ctx * 100 // n['w']}% вікна {k(n['w'])} · ревізія на {k(n['r'])} · стиснень у сесії {n['comp']} (ctx_watch)" + cap(n)
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
    return f"контекст {k(n['ctx'])} · {n['ctx'] * 100 // n['w']}% вікна {k(n['w'])} · стиснення на {k(n['t'])} · ревізія на {k(n['r'])} (найбільший крок {k(n['step'])}) · стиснень у сесії {n['comp']}"

def hook(inp, now=None):
    ev = inp.get('hook_event_name') or 'UserPromptSubmit'
    if ev == 'PostToolUse' and 'git commit' not in str((inp.get('tool_input') or {}).get('command', '')): return ''
    n = numbers(inp.get('transcript_path', ''))
    if ev == 'SessionStart':
        if inp.get('source') != 'compact': return ''
        b, k = getattr(read, 'boundary', {}), lambda x: f'{x // 1000} тис.'
        v = (f"Після стиснення № {n['comp']} ({b.get('trigger', '?')}): контекст {k(b.get('preTokens', 0))} → {k(b.get('postTokens', 0))} · " if b else 'Після стиснення: ') + \
            f"наступне стиснення на {k(n['t'])}, ревізія на {k(n['r'])} (ctx_watch). Перша відповідь — звір переказ із самері §0 і допиши в §1 рядок «стиснення N: переказ ✓ / що загубив»." + cap(n)
    else: v = verdict(n, now or time.time(), ev)
    return json.dumps({'hookSpecificOutput': {'hookEventName': ev, 'additionalContext': v}}, ensure_ascii=False) if v else ''

def selftest():
    d = tempfile.mkdtemp(); bad = 0; T0 = 1_800_000_000
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
        nonlocal bad; print(('✓ ' if ok else '✗ ') + name); bad += not ok
    case('поріг стиснення: W 450 тис. → 395 600, W 1 млн → 901 600 (обидва = autocompact_state.threshold, AE S141)',
         limits(E)[1] == 395_600 and limits({'CLAUDE_AUTOCOMPACT_PCT_OVERRIDE': '92'})[1] == 901_600)
    os.environ.update(E)
    v = lambda p, ev='UserPromptSubmit', ago=0: verdict(numbers(p), T0 + ago, ev)
    case('120 тис., повідомлення Konst — інформаційний рядок (маркер без виклику інструмента)', (v(tr('a', [a(120_000)])) or '').startswith('контекст 120 тис. · 26% вікна'))
    case('120 тис. після коміту — тиша', v(tr('a2', [a(120_000)]), 'PostToolUse') is None)
    case('260 тис. — ⓘ межа предмета', (v(tr('b', [a(260_000)])) or '').startswith('ⓘ'))
    case('330 тис. (> 395,6 − 55 − 15 = 325,6) — ⚠ ревізія зараз', (v(tr('c', [a(330_000)])) or '').startswith('⚠ контекст'))
    p = tr('d', [a(100_000, commit=True), a(190_000, commit=True), a(300_000)])
    case('крок 90 тис. між комітами → поріг ревізії 290,6 тис.; 300 тис. — ⚠', numbers(p)['r'] == 290_600 and (v(p) or '').startswith('⚠ контекст'))
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
    case('SessionStart compact: «№ 1», «371 тис. → 14 тис.», пороги, вимога рядка «стиснення N»', all(x in o for x in ('№ 1', '371 тис. → 14 тис.', 'ревізія на 325 тис.', 'стиснення N')))
    case('SessionStart startup — тиша', hook({'hook_event_name': 'SessionStart', 'source': 'startup', 'transcript_path': p}) == '')
    h = f'{d}/home'; os.makedirs(f'{h}/.claude/projects/p1'); os.makedirs(f'{h}/.claude/projects/p2')
    open(f'{h}/.claude/projects/p1/OWN.jsonl', 'w').write('x'); time.sleep(0.01); open(f'{h}/.claude/projects/p2/CHILD.jsonl', 'w').write('x')
    os.environ['CLAUDE_CODE_SESSION_ID'] = 'OWN'
    case('рядок руками: свій журнал за CLAUDE_CODE_SESSION_ID, не новіший чужий (аудит claude -p)', newest(h).endswith('OWN.jsonl'))
    print(f'─── ctx_watch selftest: {20 - bad}/20 ───'); return 1 if bad else 0

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'hook'
    if cmd == 'selftest': sys.exit(selftest())
    if cmd == 'line': print(line(sys.argv[2] if len(sys.argv) > 2 else newest())); sys.exit(0)
    try: inp = json.load(sys.stdin)
    except ValueError: inp = {}
    out = hook(inp)
    if out: print(out)
