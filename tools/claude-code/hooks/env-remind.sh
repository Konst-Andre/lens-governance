#!/bin/bash
# живе доки: є аркуш середовища tools/claude-code/ENVIRONMENT.md (ENV-1, ідея Konst 22.10.2026, Routes S1). Дім — lens-governance:tools/claude-code/hooks/.
# Подія UserPromptSubmit: Konst просить налаштування середовища («дай налаштування середовища», «setup script», «відтвори середовище»)
# → additionalContext: видати аркуш ENVIRONMENT.md цілком у чат (кожен блок — окремим code block із підписом поля), секрети — лише заглушки.
# Розмова ПРО середовище без прохання видати («яке середовище обрати?») — тиша: потрібне дієслово видачі або слово «setup script».
# Зуби: bash env-remind.sh selftest — 6 випадків.
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN
python3 - "$mode" <<'PY'
import json, os, re, sys
ASK = re.compile(r"(?<![\w'’])(дай|давай|видай|скинь|покажи|надішли|відтвор\w*|налаштуй)\b[^.?!\n]{0,40}(середовищ\w*|environment)", re.I)
SCRIPT = re.compile(r"setup[ -]?script|сетап[ -]?скрипт", re.I)

def run(d):
    p = d.get('prompt') or ''
    if not (ASK.search(p) or SCRIPT.search(p)): return None
    return ("Konst просить налаштування середовища: видай аркуш tools/claude-code/ENVIRONMENT.md ядра (для Routes — Routes:tools/ENVIRONMENT.md) "
            "цілком у чат — кожен блок окремим code block з підписом, у яке поле вставляти (назва · мережа · змінні · setup script). "
            "Секрети — лише заглушки <…>: значення вставляє Konst у налаштуваннях середовища, ніколи в чат чи репо.")

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
    print(f'─── env-remind selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

if sys.argv[1] == 'selftest': sys.exit(selftest())
try: out = run(json.loads(os.environ.get('HOOK_IN') or '{}'))
except Exception: out = None
if out: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': out}}, ensure_ascii=False))
PY
