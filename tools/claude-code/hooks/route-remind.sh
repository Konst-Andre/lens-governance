#!/bin/bash
# route-remind.sh · гачок «маршрут для Konst» (AE S135, В-332 AE; слово Konst: «щоб я не втратив маршрут — нагадуй сам; гачок для всіх продуктів, і щоб еволюціонував»).
# живе доки: Konst працює з агентами над кількома продуктами й чергами. Дім — lens-governance:tools/claude-code/hooks/ (диспетчер lens-hooks.sh, подія UserPromptSubmit).
# Що робить: читає розмову сесії (transcript_path) і рахує звіти агента (відповідь ≥ 400 знаків). Будить, коли (а) звітів ще нема — перша відповідь сесії,
#   (б) у трьох останніх звітах нема блоку «Маршрут», (в) Konst сам питає про маршрут / план / «куди рухаємось» / «загубився». Не будить, коли маршрут
#   був у двох останніх звітах і питання нема. Сам дістає маршрут: найновіше самері репо сесії (docs/summary/*SUMMARY*.md · sessions/**/*summary*.md),
#   рядок з «МАРШРУТ» у §0 і пункти під ним (≤ 1 200 знаків) — агент показує його з репо, а не з пам'яті чату (практика: файл-дорожня карта, яку агент
#   читає й оновлює — Anthropic «Effective harnesses for long-running agents», 2025; agentpatterns.ai «Goal monitoring», 07.11.2026).
# Еволюція: кожне спрацювання диспетчер пише в журнал сесії → handoff_check вимагає вердикт у HOOK_JOURNAL.md (справжнє · хибне · дубль · пропуск);
#   поріг «3 звіти» — ROUTE_EVERY (змінна середовища), маркер блоку — ROUTE_MARK (типово «Маршрут»).
# Зуби: bash route-remind.sh selftest.
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN
export LENS_HOOK_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"   # REV-5 Л2-б: питання іспиту — ../handoff_exam_questions.md
python3 - "$mode" <<'PY'
import json, os, re, sys, glob, pathlib
EVERY = int(os.environ.get('ROUTE_EVERY') or 3)
MARK = re.compile(r"(\*\*|^|\n)\s*" + re.escape(os.environ.get('ROUTE_MARK') or 'Маршрут') + r"\s*[:*]", re.I)
ASK = re.compile(r"(?<![\w'’])(маршрут(?!изац)\w*|куди (ми )?рухаємось|який план|нагадай (мені )?план|загуби\w*|що далі|де ми зараз)(?![\w'’])", re.I)

def reports(path, short=False):
    """Звіти агента: текст відповідей між повідомленнями людини, лише суттєві (≥ 400 знаків); short=True — усі (для «перша відповідь сесії»)."""
    out, cur = [], []
    try: lines = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception: return out
    for ln in lines:
        try: e = json.loads(ln)
        except Exception: continue
        m = e.get('message') or {}; role = m.get('role') or e.get('type')
        c = m.get('content')
        if role == 'user' and (isinstance(c, str) or (isinstance(c, list) and any(isinstance(x, dict) and x.get('type') == 'text' for x in c))):
            if cur: out.append('\n'.join(cur)); cur = []
        elif role == 'assistant' and isinstance(c, list):
            cur += [x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text']
    if cur: out.append('\n'.join(cur))
    return out if short else [r for r in out if len(r) >= 400]

def route_text(cwd):
    """Самері — за рівнями: сама тека · її репо (хмарна сесія: cwd = корінь сесії з репо всередині) · сусіди; перший рівень, де є самері, —
    і в ньому репо продукту раніше за ядро (аудит AE S156 №3: max(mtime) по всіх сусідах давав самері ядра без «МАРШРУТ» сесії продукту)."""
    c = pathlib.Path(cwd or '.')
    kids = lambda p: sorted(x for x in p.iterdir() if x.is_dir() and not x.name.startswith('.')) if p.exists() else []
    files = []
    for level in ([c], kids(c), [x for x in kids(c.parent) if x != c]):
        found = {}
        for r in level:
            fs = [pathlib.Path(f) for g in ('docs/summary/*SUMMARY*.md', 'sessions/**/*summary*.md') for f in glob.glob(str(r / g), recursive=True)]
            if fs: found[r] = fs
        prod = [f for r, fs in found.items() if not (r / 'kernel' / 'Lens_INDEX.md').exists() for f in fs]
        files = prod or [f for fs in found.values() for f in fs]
        if files: break
    if not files: return None, None
    f = max(files, key=lambda x: x.stat().st_mtime)
    t = f.read_text(encoding='utf-8', errors='ignore')
    i = t.find('МАРШРУТ')
    if i < 0: return str(f), None
    j = t.find('\n**0.', i + 10); k = t.find('\n## ', i + 10)
    end = min(x for x in (j, k, i + 1200) if x > 0)
    return str(f), t[t.rfind('\n', 0, i) + 1:end].strip()

PASTE = re.compile(r'(?s)<pasted_content id="[^"]*">.*?</pasted_content id="[^"]*">')   # вставлене Konst — не його питання (аудит S156 №4; code.claude.com/docs/en/hooks, 19.11.2026)

def run(d, rep=None, src=None):
    asked = bool(ASK.search(PASTE.sub(' ', d.get('prompt') or '')))
    if rep is None:
        tp = d.get('transcript_path')
        if not tp and not asked: return None   # без журналу «перша відповідь» не визначити — тиша (як memory-guard, plan-web; аудит S156 №1)
        allr = reports(tp, short=True) if tp else []
    else: allr = rep
    rep = [r for r in allr if len(r) >= 400]
    first = not allr   # перша — коли відповідей агента ще нема ЗОВСІМ, не «довгих нема» (аудит S156 №1: «Прийняв:» вимагався щоходу до першого довгого звіту)
    last = rep[-EVERY:]
    shown_recent = any(MARK.search(r) for r in rep[-2:])
    if not first and not asked and (shown_recent or len(last) < EVERY or any(MARK.search(r) for r in last)): return None
    why = 'Konst питає про маршрут' if asked else ('перша відповідь сесії' if first else f'у {EVERY} останніх звітах блоку «Маршрут» нема')
    f, rt = route_text(d.get('cwd')) if src is None else src
    body = (f"Маршрут для Konst ({why}): у цій відповіді — блок «**Маршрут:**» 3–5 рядків: де ми (пункт черги й крок) · далі (1–3 кроки) · попутно · що чекає Konst. "
            "Бери з самері §0 і черги репо, не з пам'яті чату; змінилось — спершу онови самері §0, тоді показуй.")
    if f: body += f" Самері: {f}."
    if rt: body += "\nЗ самері зараз:\n" + rt[:1200]
    if first: body = readback() + '\n' + body
    return body

def readback():
    """REV-5 Л2-б (💡 AE S155, оцінена агентом за словом Konst «оціни сам… підсиль»): переказ прийому — I-PASS «synthesis by receiver»: новий агент
    у ПЕРШІЙ відповіді сесії сам переказує прийняте, коротко й з `файл:рядок`; розбіжність, яку бачить Konst, — дешевше за діру через три ходи.
    Ціна — ≤ 6 рядків, без іншої моделі (іспит-прилад — на ревізії). Питання — той самий файл, що в іспиті (одна правда)."""
    qf = pathlib.Path(os.environ.get('LENS_HOOK_DIR') or '.') / '..' / 'handoff_exam_questions.md'
    try: qs = [ln.strip() for ln in re.findall(r'(?ms)^## \d+\n(.*?)(?=^## \d+\n|\Z)', qf.read_text(encoding='utf-8'))]
    except OSError: qs = []
    qs = ' · '.join(f'{i}) ' + q.split('?')[0].strip()   # питання цілим: обрізання на 70 знаках губило «публікація» з п. 4 (аудит S156 №2, бачено на старті S156)
                      for i, q in enumerate(qs, 1)) or 'що першим · рішення попередньої сесії й де · що чекає Konst · чого не робити · де код і гілка · що незрозуміло чи суперечить'
    return ("Переказ прийому (перша відповідь сесії): після «що ти побачиш» і рядків ⚠ / ✗ стану репо, якщо вони є, — блок «**Прийняв:**» ≤ 6 рядків, своїми словами, з `файл:рядок`, "
            f"лише з репо (не з пам'яті й не дослівно зі стартового): {qs}. Суперечність чи застаріле — назви й виправ у репо першим ходом.")

def selftest():
    R = 'x' * 450
    cases = [('перша відповідь сесії → нагадування', {'prompt': 'роби далі'}, [], True),
             ('маршрут був в останньому звіті → тиша', {'prompt': 'роби далі'}, [R, R, R + '\n**Маршрут:** де ми'], False),
             ('три звіти без маршруту → нагадування', {'prompt': 'роби далі'}, [R + '\n**Маршрут:** a', R, R, R], True),
             ('лише два звіти без маршруту після показу → тиша', {'prompt': 'ок'}, [R + '\n**Маршрут:** a', R, R], False),
             ('Konst питає «куди рухаємось» → нагадування навіть одразу після показу', {'prompt': 'нагадай, куди рухаємось?'}, [R + '\n**Маршрут:** a'], True),
             ('«я загубився в брифах» → нагадування', {'prompt': 'я вже трішки загубився в брифах'}, [R + '\n**Маршрут:** a'], True),
             ('«маршрутизація» в коді — не питання про план → тиша', {'prompt': 'поправ маршрутизацію запитів'}, [R + '\n**Маршрут:** a'], False),
             ('короткі відповіді (< 400) не рахуються як звіти → тиша', {'prompt': 'так'}, [R + '\n**Маршрут:** a'] + ['ок'] * 5, False),
             ('аудит S156 №1: три короткі відповіді — уже не перша відповідь → тиша', {'prompt': 'роби'}, ['ок', 'так', 'добре'], False),
             ('аудит S156 №4: «що далі» лише у вставленому тексті → тиша', {'prompt': 'глянь <pasted_content id="a1">\nщо далі?\n</pasted_content id="a1"> ок'}, [R + '\n**Маршрут:** a'], False),
             ('«що далі» поза вставкою → нагадування', {'prompt': '<pasted_content id="a1">\nлог\n</pasted_content id="a1"> що далі?'}, [R + '\n**Маршрут:** a'], True)]
    bad = 0
    for name, d, rep, want in cases:
        got = run(d, rep, (None, None)) is not None; ok = got == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    # витяг маршруту з самері — на тимчасовому репо
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp()) / 'repo'; (tmp / 'docs/summary').mkdir(parents=True)
    (tmp / 'docs/summary/X_SUMMARY_2026-11-07.md').write_text('## §0\n\n**0.1 · ДЕ МИ:** тут\n\n**0.2 · МАРШРУТ (S2 →):**\n  1. Крок один.\n  2. Крок два.\n\n**0.3 · ВІД KONST:** ...\n', encoding='utf-8')
    f, rt = route_text(str(tmp)); ok = bool(rt) and 'Крок два' in rt and 'ВІД KONST' not in rt; bad += not ok
    print(('✓ ' if ok else '✗ ') + 'маршрут береться з самері §0.2 (до наступного пункту §0)')
    b1 = run({'prompt': 'роби далі'}, [], (None, None)) or ''; b2 = run({'prompt': 'нагадай, куди рухаємось?'}, [R], (None, None)) or ''
    ok2 = 'Прийняв' in b1 and 'суперечить' in b1 and 'публікація' in b1 and 'рядків ⚠ / ✗' in b1 and 'Прийняв' not in b2; bad += not ok2
    print(('✓ ' if ok2 else '✗ ') + 'REV-5 Л2-б: перша відповідь сесії → «Прийняв:» з питаннями іспиту цілими («публікація» в п. 4 — аудит S156 №2), після рядків ⚠ / ✗ (№5); далі — без нього')
    ok3 = run({'prompt': 'роби далі'}) is None; bad += not ok3
    print(('✓ ' if ok3 else '✗ ') + 'аудит S156 №1: журналу сесії нема (transcript_path) і питання нема → тиша')
    # аудит S156 №3: корінь сесії з двома репо — продукт раніше за ядро, навіть коли самері ядра новіше
    ses = pathlib.Path(tempfile.mkdtemp()); (ses / 'Prod/docs/summary').mkdir(parents=True); (ses / 'lens-governance/sessions/x').mkdir(parents=True); (ses / 'lens-governance/kernel').mkdir()
    (ses / 'lens-governance/kernel/Lens_INDEX.md').write_text('x'); (ses / 'Prod/docs/summary/P_SUMMARY_2026-11-19.md').write_text('**0.2 · МАРШРУТ:** продукт\n')
    kf = ses / 'lens-governance/sessions/x/K_session_summary_X.md'; kf.write_text('ядро'); os.utime(kf, (4e9, 4e9))
    f3, rt3 = route_text(str(ses)); ok4 = bool(f3) and 'Prod' in f3 and 'продукт' in (rt3 or ''); bad += not ok4
    print(('✓ ' if ok4 else '✗ ') + 'аудит S156 №3: корінь сесії → самері продукту, не новіше самері ядра')
    print(f'─── route-remind selftest: {len(cases) + 4 - bad}/{len(cases) + 4} ───'); return 1 if bad else 0

if sys.argv[1] == 'selftest': sys.exit(selftest())
try: out = run(json.loads(os.environ.get('HOOK_IN') or '{}'))
except Exception: __import__('traceback').print_exc(); out = None
if out: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': out}}, ensure_ascii=False))
PY
