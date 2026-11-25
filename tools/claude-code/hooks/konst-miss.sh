#!/bin/bash
# живе доки: є журнал гачків і перевірок (tools/claude-code/hooks/HOOK_JOURNAL.md). Дім — lens-governance:tools/claude-code/hooks/ (HOOK-5, «так» Konst 10.10.2026).
# «Пропуски, знайдені Konst» — найсильніший сигнал для нових перевірок: вада, яку побачив Konst, а не гачок / ui_lint / гейт
# (detection engineering: «false negative» — те, що правило мало зловити, а не зловило). Konst 10.10: «це обов'язково треба рахувати».
# Подія UserPromptSubmit: у повідомленні Konst — слова-вказівки на ваду («не те», «прилипло», «не видно», «знову», «пропустив»…) →
# additionalContext: спершу виправлення з прогоном, рядок «пропуск Konst» у журналі — останнім, з хешем і зубом (AE S146; судить promise-guard.sh).
# Диспетчер логує спрацювання → handoff_check на переїзді вимагає вердикт. Похвала й розмова — тиша; хибне спрацювання — теж у журнал.
# Не вада (хибне ×4, журнал гачків 16–18.10.2026): слово всередині короткої НАЗВИ в «…» з великої літери («Увійти знову» — кнопка) і
# «не зламал…» (заперечення: «щоб це не зламало якість»); слово-вказівка саме в лапках («незрозуміло» — крок іспиту в стартовому, хибне EquipLens S39). Те саме слово поза назвою — будить, як раніше; перше повідомлення сесії не вимикається.
# Група «прийняття» (режим yes, ярлик konst-yes — В-372, AE S145; план — AE-Simulator:docs/summary/AE_SUMMARY_2026-11-13_s2.md §0.2 п. 7):
#   Konst приймає 💡 («так», «приймаю», «беремо», «згоден», «з підсиленням») — і лише коли останній звіт агента мав «💡 Пропоную» →
#   нагадування про чек-лист підсилення ①–⑦ (дім — tools/claude-code/CLAUDE_CODE.md «Практики» · «Прийнята 💡»). «як є» · «дослівно» ·
#   «без підсилення» — тиша. «так» — найчастіше слово: рахується лише першим словом речення й не «так само» / «не так» / вставне «Так, я…» (QR CC-20).
#   Диспетчер кличе yes окремо й додає до будь-якого іншого гачка (прийняття і вказівка на ваду можуть бути в одному повідомленні).
#   Режим stop (подія Stop, EquipLens S45 25.11.2026 — Konst: «чи хтось слідкує… що ти дійсно виконуєш цей чек-лист?»; до того — лише нагадування,
#   Stop-суду не було): останнє повідомлення Konst — прийняття 💡 (той самий yes() на звіт перед ним), а у відповіді нема «Підсилення» → block один раз
#   на одне повідомлення Konst (позначка /tmp/lens-kmstop-<сесія>; stop_hook_active не годиться — першим міг блокувати memory-guard). Слово «Підсилення» — мінімум, що судить машина; повноту ①–⑦ — ні (не виміряти).
# Зуби: bash konst-miss.sh selftest — 15 випадків пропусків + 13 прийняття (один — на файлі розмови) + 5 суду Stop.
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN
python3 - "$mode" <<'PY'
import json, os, re, sys
CUE = re.compile(r"(?<![\w'’])(не те|не так|чому (ти )?не|знову|ти пропустив\w*|пропустив|не помітив|не побачив|проігнорув\w*|перекіс\w*|перекошен\w*|прилип\w*|обріза\w*|обрізан\w*|погано видно|не видно|ледь (видно|помітн\w*)|губиться|з'їха\w*|з’їха\w*|стрибає|технічн\w+ текст|незрозуміл\w*|не працює|зламал\w*)(?![\w'’])", re.I)
CALM = re.compile(r"(?<![\w'’])(працює кайф|все працює|подобається|супер|чудов\w*)(?![\w'’])", re.I)

YES = re.compile(r"(?<![\w'’])(приймаю|прийнято|беремо|згоден|згодна|погоджую|з підсиленням|підсиль|підсили)(?![\w'’])|(?:^|[.!?\n]\s*)так(?![\w'’])(?!\s+само)(?!\s*,\s*(?:я|ми|ось|от|значить|отже|дивись|слухай|ну|зараз|стоп|щодо|стосовно)(?![\w'’]))", re.I)   # QR CC-20: «Так, я…» — вставне, не згода
ASIS = re.compile(r"(?<![\w'’])(як є|дослівно|без підсилення)(?![\w'’])", re.I)
IDEA = '💡 Пропоную'
SERVICE = re.compile(r"\s*(Stop hook feedback|<system-reminder>|<command-|<local-command)")

def last_report(path, tail=4_000_000):
    """Текст останньої відповіді агента (між двома повідомленнями людини) — з хвоста розмови: журнал може мати 10+ МБ."""
    try:
        with open(os.path.expanduser(path), 'rb') as f:
            f.seek(0, 2); n = f.tell(); f.seek(max(0, n - tail)); raw = f.read().decode('utf-8', 'ignore')
    except Exception: return ''
    cur, last = [], ''
    for ln in raw.splitlines():
        try: e = json.loads(ln)
        except Exception: continue
        m = e.get('message') or {}; role = m.get('role') or e.get('type'); c = m.get('content')
        txt = c if isinstance(c, str) else ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text') if isinstance(c, list) else ''
        if role == 'user' and txt and not e.get('isMeta') and not SERVICE.match(txt):   # відгук гачка Stop — не межа звіту (S145: різав звіт з 💡 навпіл)
            if cur: last = '\n'.join(cur); cur = []
        elif role == 'assistant' and isinstance(c, list):
            cur += [x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text']
    return '\n'.join(cur) if cur else last

def turn(path, tail=4_000_000):
    """(останнє справжнє повідомлення Konst, звіт агента перед ним) — для суду Stop."""
    try:
        with open(os.path.expanduser(path), 'rb') as f:
            f.seek(0, 2); n = f.tell(); f.seek(max(0, n - tail)); raw = f.read().decode('utf-8', 'ignore')
    except Exception: return '', ''
    prompt, prev, cur = '', '', []
    for ln in raw.splitlines():
        try: e = json.loads(ln)
        except Exception: continue
        m = e.get('message') or {}; role = m.get('role') or e.get('type'); c = m.get('content')
        txt = c if isinstance(c, str) else ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text') if isinstance(c, list) else ''
        if role == 'user' and txt and not e.get('isMeta') and not SERVICE.match(txt): prompt, prev, cur = txt, '\n'.join(cur), []
        elif role == 'assistant' and isinstance(c, list): cur += [x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text']
    return prompt, prev

DONE = re.compile(r"Підсилення|konst-yes[^\n]{0,40}хибне", re.I)

def stop(d, tr=None):
    p, prev = turn(d.get('transcript_path') or '') if tr is None else tr
    if not p or not yes({'prompt': p}, prev) or DONE.search(d.get('last_assistant_message') or ''): return None
    import hashlib   # раз на повідомлення Konst: stop_hook_active не годиться — першим міг блокувати інший гачок Stop (memory-guard), і тоді суд мовчав би
    mk = os.path.join(os.environ.get('LENS_MARK_DIR') or '/tmp', f"lens-kmstop-{d.get('session_id') or 'nosession'}")
    h = hashlib.sha1(p.encode()).hexdigest()[:12]
    try:
        if open(mk).read().strip() == h: return None
    except Exception: pass
    try: open(mk, 'w').write(h)
    except Exception: pass
    return ("Konst прийняв 💡, а у звіті нема блоку «Підсилення: було → стало» (чек-лист ①–⑦, tools/claude-code/CLAUDE_CODE.md «Практики» · «Прийнята 💡»). "
            "Пройди чек-лист і допиши блок; дрібний оборотний крок — одним рядком «Підсилення: …»; це не прийняття 💡 — рядок «konst-yes … хибне» в журналі гачків.")

def yes(d, rep=None):
    p = d.get('prompt') or ''
    if not YES.search(p) or ASIS.search(p): return None
    r = last_report(d.get('transcript_path') or '') if rep is None else rep
    if IDEA not in r: return None
    return ("Konst приймає 💡 — спершу підсилення за чек-листом (tools/claude-code/CLAUDE_CODE.md «Практики» · «Прийнята 💡», ядро): "
            "① суть — яку причину лікує, не симптом? ② сильніше в межах — структура (один дім, злити з наявним) · техніка (простіше · дешевше · надійніше) · "
            "контекст (знадобиться іншим → ядро) ③ світ — коли вирішує форму, три рядки з джерелом і датою ④ премортем — «через місяць шкодуємо — чому?», "
            "дірка → латка або прийнятий ризик ⑤ ціна — ліміти заміром, ручні дії Konst, зворотність ⑥ вирок — роблю / звужую / відкидаю з причиною "
            "⑦ у звіті блок «Підсилення: було → стало» + дірки й латки (нічого — що перевірив). Другий погляд (профіль ЦИКЛ п. 3) — не дублювати. "
            "Дрібний оборотний крок — одним рядком. Хибне (це не прийняття 💡) — рядком «konst-yes … хибне» в журналі гачків.")

NAME = re.compile(r"«[A-ZА-ЯІЇЄҐ][^«»\n]{0,38}»")   # назва кнопки / екрана в лапках: «Увійти знову», «Оновити сайт»
TERM = re.compile(r"«\s*" + CUE.pattern + r"\s*»", re.I)   # слово-вказівка САМЕ в лапках — термін процедури («незрозуміло» іспиту в стартовому, EquipLens S39), не скарга

STEP = re.compile(r"(?<![\w'’])незрозуміл\w*\s*[—–-]\s*виправ\w*", re.I)   # крок іспиту без лапок: «(3) незрозуміле — виправити…» (хибне EquipLens S40) — інструкція процедури, не скарга

def run(d):
    p = STEP.sub('', TERM.sub('«»', NAME.sub('«»', d.get('prompt') or '')))
    hits = sorted({m.group(1).lower() for m in CUE.finditer(p)
                   if not (m.group(1).lower().startswith('зламал') and re.search(r"(?<![\w'’])не\s+$", p[:m.start()]))
                   # AE S102: «текст — лише те, чого не видно з форми» — опис правила (підрядне «чого / що … не видно»), не скарга на ваду
                   and not (m.group(1).lower().endswith('видно') and re.search(r"(?<![\w'’])(чого|що|якого|якої|яких|яке|які)\s+$", p[:m.start()], re.I))})
    if not hits or (CALM.search(p) and len(hits) < 2): return None
    return ("Схоже, Konst вказує на ваду («" + "», «".join(hits[:4]) + "»). Якщо це вада, яку не спіймали гачки / ui_lint / гейт, — СПЕРШУ виправ "
            "і покажи прогоном (нова перевірка з тестом або пункт чек-листа очей, якщо машинно не виміряти); рядок «пропуск Konst» у журналі гачків "
            "(tools/claude-code/hooks/HOOK_JOURNAL.md §1) — ОСТАННІМ: що пропустили · чому машина не бачила · рішення з хешем коміту виправлення й зубом. "
            "Не встигаєш — «НЕ ЗРОБЛЕНО: чому · коли» в рядку і «не зроблено: …» першими рядками звіту; запис — не дія, звітувати ним не можна "
            "(сторож promise-guard, Konst S146). Не вада (розмова) — одним рядком «хибне» в журналі.")

def selftest():
    cases = [('«капсула прилипла до краю» → нагадування', 'подивись, капсула прилипла до краю картки', True),
             ('«знову технічний текст» → нагадування', 'знову технічний текст у кнопці', True),
             ('похвала → тиша', 'Адмінку оновив, працює кайф, дякую', False),
             ('звичайне доручення → тиша', 'роби 2.2, делегую', False),
             ('«не видно» навіть з похвалою, але дві вказівки → нагадування', 'супер, але іконку не видно і текст обрізаний', True),
             ('назва кнопки «Увійти знову» у стартовому → тиша', 'Далі: QRL-15 К2, «Увійти знову», документація', False),
             ('та сама кнопка, але «знову» поза назвою → нагадування', 'кнопка «Увійти знову» знову не працює', True),
             ('«щоб це не зламало якість» → тиша', 'виправ так, щоб це не зламало якість роботи, а підсилило', False),
             ('«все зламалось» → нагадування', 'після оновлення все зламалось', True),
             ('цитата з малої літери — не назва → нагадування', 'ти написав «знову технічний текст», а так не можна', True),
             ('правило «чого не видно з форми» → тиша', 'текст — лише те, чого не видно з форми; пояснене раз не повторюється', False),
             ('«а кнопку не видно» поруч із правилом → нагадування', 'текст — лише те, чого не видно з форми, а кнопку «Нова» не видно', True),
             ('термін «незрозуміло» у стартовому (іспит) → тиша', '(3) «незрозуміло» — виправити й закомітити ДО коду Ф2-3; лишається — рядком у §1', False),
             ('те саме слово без лапок → нагадування', 'тут незрозуміло, що робить кнопка', True),
             ('крок іспиту без лапок «незрозуміле — виправити» → тиша', '(3) незрозуміле — виправити й закомітити ДО коду; лишається — рядком у §1', False),
             ('«незрозуміло» поруч з вадою, не крок → нагадування', 'незрозуміло, чому картка — прилипла', True)]
    bad = 0
    for name, p, want in cases:
        ok = (run({'prompt': p}) is not None) == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    yc = [('«пропозицію приймаю» після 💡 → нагадування', 'пропозицію приймаю за чек-листом', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', True),
          ('«так, роби» після 💡 → нагадування', 'так, роби', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', True),
          ('вставне «Так, я…» після 💡 → тиша (хибне QR CC-20)', 'Так, я подивився, що там у файлі керівника', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', False),
          ('«беремо з підсиленням» → нагадування', 'Добре. Беремо з підсиленням.', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', True),
          ('«так» без 💡 у звіті → тиша', 'так, роби', 'Звіт без пропозиції.', False),
          ('«так як є» після 💡 → тиша', 'так як є', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', False),
          ('«приймаю дослівно» → тиша', 'приймаю дослівно', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', False),
          ('«так само» після 💡 → тиша', 'зроби так само, як у рейці', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', False),
          ('«не так» після 💡 → тиша', 'це не так працює', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', False),
          ('«так» посеред речення після 💡 → тиша', 'чому воно так рухається', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', False),
          ('звичайне доручення після 💡 → тиша', 'роби П3', 'Звіт.\n\n💡 Пропоную: гачок, що нагадує чек-лист.', False)]
    import tempfile
    tp = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False, encoding='utf-8')
    for e in [{'type': 'user', 'message': {'role': 'user', 'content': 'зроби план'}},
              {'type': 'assistant', 'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'Звіт.\\n\\n💡 Пропоную: гачок.'}]}},
              {'type': 'user', 'message': {'role': 'user', 'content': [{'type': 'text', 'text': 'Stop hook feedback:\nворота'}]}},
              {'type': 'assistant', 'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'дописав рядок'}]}}]: tp.write(json.dumps(e, ensure_ascii=False) + '\n')
    tp.close()
    ok = yes({'prompt': 'приймаю', 'transcript_path': tp.name}) is not None; bad += not ok; os.unlink(tp.name)
    print(('✓ ' if ok else '✗ ') + 'розмова: 💡 до відгуку гачка Stop — відгук не межа звіту → нагадування'); cases = cases + [0]
    for name, p, r, want in yc:
        ok = (yes({'prompt': p}, r) is not None) == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    cases = cases + yc
    R = 'Звіт.\n\n💡 Пропоную: гачок.'
    sc = [('Stop: прийняв 💡, у звіті нема «Підсилення» → block', {'last_assistant_message': 'Зробив.'}, ('приймаю з підсиленням', R), True),
          ('Stop: блок «Підсилення: було → стало» є → тиша', {'last_assistant_message': 'Зробив.\n\n**Підсилення: було → стало** — …'}, ('приймаю', R), False),
          ('Stop: прийняття без 💡 у звіті перед ним → тиша', {'last_assistant_message': 'Зробив.'}, ('так, роби', 'Звіт без пропозиції.'), False),
          ('Stop: «Згоден? Підсиль» після 💡 → block', {'last_assistant_message': 'Зробив.'}, ('Згоден? Підсиль.', R), True),
          ('Stop: те саме повідомлення Konst удруге → тиша (раз на повідомлення, не зациклити)', {'last_assistant_message': 'Зробив.', 'stop_hook_active': True}, ('Згоден? Підсиль.', R), False)]
    md = tempfile.mkdtemp(prefix='kmstop_'); os.environ['LENS_MARK_DIR'] = md
    if os.environ.get('KM_INJECT') == 'stop': stop.__globals__['DONE'] = re.compile(r'.')   # зуб: суд «завжди задоволений» має почервоніти
    for name, d, tr, want in sc:
        ok = (stop({'session_id': 'st', **d}, tr) is not None) == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    __import__('shutil').rmtree(md, ignore_errors=True); cases = cases + sc
    print(f'─── konst-miss selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

if sys.argv[1] == 'selftest': sys.exit(selftest())
if sys.argv[1] == 'stop':
    try: r = stop(json.loads(os.environ.get('HOOK_IN') or '{}'))
    except Exception: __import__('traceback').print_exc(); r = None
    if r: print(json.dumps({'decision': 'block', 'reason': r}, ensure_ascii=False))
    sys.exit(0)
try: out = (yes if sys.argv[1] == 'yes' else run)(json.loads(os.environ.get('HOOK_IN') or '{}'))
except Exception: __import__('traceback').print_exc(); out = None
if out: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': out}}, ensure_ascii=False))
PY
