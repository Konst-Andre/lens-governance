#!/bin/bash
# живе доки: є аркуш середовища tools/claude-code/ENVIRONMENT.md (ENV-1, ідея Konst 22.10.2026, Routes S1). Дім — lens-governance:tools/claude-code/hooks/.
# Подія UserPromptSubmit: Konst просить налаштування середовища («дай налаштування середовища», «setup script», «відтвори середовище»)
# → additionalContext: видати аркуш ENVIRONMENT.md цілком у чат (кожен блок — окремим code block із підписом поля), секрети — лише заглушки.
# Розмова ПРО середовище без прохання видати («яке середовище обрати?») — тиша: потрібне дієслово видачі або слово «setup script».
# Підсилення 22.10.2026 (Konst: «лише нагадування замало — агент має сам пропонувати й допомагати»):
#   · на прохання — ще й живу звірку env_drift.py (середовище ⟂ аркуш): агент видає не весь аркуш наосліп, а «що вже є · чого бракує · рядки для вставки»;
#   · режим post — коміт змінив аркуш ENVIRONMENT.md → агент сам пропонує Konst оновити середовище (видати змінені блоки);
#   · без прохання щостарту — рядок env_drift у tools/env_check.sh ядра (⚠ лише при розбіжності).
# Зуби: bash env-remind.sh selftest — 8 випадків.
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN HOOK_SELF="$0"
python3 - "$mode" <<'PY'
import json, os, re, subprocess, sys
ASK = re.compile(r"(?<![\w'’])(дай|давай|видай|скинь|покажи|надішли|відтвор\w*|налаштуй)\b[^.?!\n]{0,40}(середовищ\w*|environment)", re.I)
SCRIPT = re.compile(r"setup[ -]?script|сетап[ -]?скрипт", re.I)

HOOKS = os.path.dirname(os.path.abspath(os.environ.get('HOOK_SELF', '.')))

def drift():
    f = os.path.join(HOOKS, '..', 'env_drift.py')
    if not os.path.isfile(f): return ''
    try:
        r = subprocess.run([sys.executable, f, '--short'], capture_output=True, text=True, timeout=25)
        return r.stdout.strip()
    except Exception: return ''

def post(d):
    cmd = ((d.get('tool_input') or {}).get('command') or '')
    if not re.search(r"\bgit\b[^\n;&|]*\bcommit\b", cmd): return None
    cwd = d.get('cwd') or '.'
    r = subprocess.run(['git', '-C', cwd, 'log', '-1', '--since=3 minutes ago', '--name-only', '--format='], capture_output=True, text=True)
    hit = [x for x in r.stdout.split() if x.endswith('ENVIRONMENT.md')]
    if not hit: return None
    return ("Коміт змінив аркуш середовища (" + ", ".join(hit) + "). Живі середовища Konst тепер відстають від аркуша: "
            "запропонуй Konst оновити середовище — видай у чат лише змінені блоки (поле · що вставити), секрети — заглушками, "
            "і скажи, що діє з нової сесії.")

def run(d):
    p = d.get('prompt') or ''
    if not (ASK.search(p) or SCRIPT.search(p)): return None
    rep = drift()
    return ((("Жива звірка середовища з аркушем (env_drift.py):\n" + rep + "\n") if rep else '') +
            "Konst просить налаштування середовища: видай аркуш tools/claude-code/ENVIRONMENT.md ядра (для Routes — Routes:tools/ENVIRONMENT.md) "
            "цілком у чат — кожен блок окремим code block з підписом, у яке поле вставляти (назва · мережа · змінні · setup script). "
            "Секрети — лише заглушки <…>: значення вставляє Konst у налаштуваннях середовища, ніколи в чат чи репо. "
            "Почни з підсумку звірки: що вже ≡ аркушу, чого бракує, — і запропонуй рівно ті рядки, яких бракує.")

def selftest():
    cases = [('«дай налаштування середовища» → нагадування', 'дай мені налаштування середовища для основного акаунта', True),
             ('«setup script» → нагадування', 'скинь setup script, вставлю', True),
             ('«відтвори середовище» → нагадування', 'відтвори середовище Routes', True),
             ('питання про вибір середовища → тиша', 'яке середовище обрати для сесії?', False),
             ('звичайне доручення → тиша', 'роби крок 2, делегую', False),
             ('«середовище» без видачі → тиша', 'у середовищі ядра все працює', False)]
    bad = 0
    for name, p, want in cases:
        ok = (run({'prompt': p}) is not None) == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    import tempfile
    d = tempfile.mkdtemp(); g = lambda *a: subprocess.run(['git', '-C', d] + list(a), capture_output=True)
    g('init', '-q'); g('config', 'user.email', 't@t'); g('config', 'user.name', 't')
    open(os.path.join(d, 'ENVIRONMENT.md'), 'w').write('x'); g('add', '.'); g('commit', '-qm', 'x')
    ok = post({'tool_input': {'command': 'git commit -m x'}, 'cwd': d}) is not None; bad += not ok
    print(('✓ ' if ok else '✗ ') + 'коміт змінив ENVIRONMENT.md → пропозиція оновити середовище')
    open(os.path.join(d, 'other.md'), 'w').write('y'); g('add', '.'); g('commit', '-qm', 'y')
    ok = post({'tool_input': {'command': 'git commit -m y'}, 'cwd': d}) is None; bad += not ok
    print(('✓ ' if ok else '✗ ') + 'коміт без аркуша → тиша')
    cases += [0, 0]
    print(f'─── env-remind selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

if sys.argv[1] == 'selftest': sys.exit(selftest())
ev = 'PostToolUse' if sys.argv[1] == 'post' else 'UserPromptSubmit'
try: out = (post if ev == 'PostToolUse' else run)(json.loads(os.environ.get('HOOK_IN') or '{}'))
except Exception: out = None
if out: print(json.dumps({'hookSpecificOutput': {'hookEventName': ev, 'additionalContext': out}}, ensure_ascii=False))
PY
