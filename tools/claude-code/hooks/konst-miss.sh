#!/bin/bash
# живе доки: є журнал гачків і перевірок (tools/claude-code/hooks/HOOK_JOURNAL.md). Дім — lens-governance:tools/claude-code/hooks/ (HOOK-5, «так» Konst 10.10.2026).
# «Пропуски, знайдені Konst» — найсильніший сигнал для нових перевірок: вада, яку побачив Konst, а не гачок / ui_lint / гейт
# (detection engineering: «false negative» — те, що правило мало зловити, а не зловило). Konst 10.10: «це обов'язково треба рахувати».
# Подія UserPromptSubmit: у повідомленні Konst — слова-вказівки на ваду («не те», «прилипло», «не видно», «знову», «пропустив»…) →
# additionalContext: після виправлення — рядок «пропуск Konst» у журналі (що пропустили · чому машина не бачила · рішення).
# Диспетчер логує спрацювання → handoff_check на переїзді вимагає вердикт. Похвала й розмова — тиша; хибне спрацювання — теж у журнал.
# Зуби: bash konst-miss.sh selftest — 5 випадків.
mode="${1:-run}"
[ "$mode" = selftest ] && HOOK_IN="{}" || HOOK_IN="$(cat)"
export HOOK_IN
python3 - "$mode" <<'PY'
import json, os, re, sys
CUE = re.compile(r"(?<![\w'’])(не те|не так|чому (ти )?не|знову|ти пропустив\w*|пропустив|не помітив|не побачив|проігнорув\w*|перекіс\w*|перекошен\w*|прилип\w*|обріза\w*|обрізан\w*|погано видно|не видно|ледь (видно|помітн\w*)|губиться|з'їха\w*|з’їха\w*|стрибає|технічн\w+ текст|незрозуміл\w*|не працює|зламал\w*)(?![\w'’])", re.I)
CALM = re.compile(r"(?<![\w'’])(працює кайф|все працює|подобається|супер|чудов\w*)(?![\w'’])", re.I)

def run(d):
    p = d.get('prompt') or ''
    hits = sorted({m.group(1).lower() for m in CUE.finditer(p)})
    if not hits or (CALM.search(p) and len(hits) < 2): return None
    return ("Схоже, Konst вказує на ваду («" + "», «".join(hits[:4]) + "»). Якщо це вада, яку не спіймали гачки / ui_lint / гейт, — після виправлення "
            "рядок «пропуск Konst» у журналі гачків і перевірок (tools/claude-code/hooks/HOOK_JOURNAL.md §1): що пропустили · чому машина не бачила · "
            "рішення — нова перевірка (з тестом) або пункт чек-листа очей, якщо машинно не виміряти. Не вада (розмова) — одним рядком «хибне» в журналі.")

def selftest():
    cases = [('«капсула прилипла до краю» → нагадування', 'подивись, капсула прилипла до краю картки', True),
             ('«знову технічний текст» → нагадування', 'знову технічний текст у кнопці', True),
             ('похвала → тиша', 'Адмінку оновив, працює кайф, дякую', False),
             ('звичайне доручення → тиша', 'роби 2.2, делегую', False),
             ('«не видно» навіть з похвалою, але дві вказівки → нагадування', 'супер, але іконку не видно і текст обрізаний', True)]
    bad = 0
    for name, p, want in cases:
        ok = (run({'prompt': p}) is not None) == want; bad += not ok; print(('✓ ' if ok else '✗ ') + name)
    print(f'─── konst-miss selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0

if sys.argv[1] == 'selftest': sys.exit(selftest())
try: out = run(json.loads(os.environ.get('HOOK_IN') or '{}'))
except Exception: out = None
if out: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': out}}, ensure_ascii=False))
PY
