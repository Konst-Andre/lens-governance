#!/usr/bin/env python3
# живе доки: ядро веде журнал гачків `tools/claude-code/hooks/HOOK_JOURNAL.md` зі стелею 24 КБ (handoff_check J_KB · храповик старту commit_files п.14).
# Ротація журналу гачків машиною (EquipLens S41, 22.11.2026; Konst прийняв 💡 «AUTO-1 (б) машиною» з підсиленням: «щоб більше не повторювалося»).
# Закриті рядки §1 → `journal/HOOK_JOURNAL_<РРРР-ММ>.md` (розділ «Рядки з §1 — ротація <дата> (машиною)»). Лишаються: відкриті
# («відкрите», «кандидат», «рішення Konst», «НЕ ЗРОБЛЕНО») і рядки живої сесії (CLAUDE_CODE_REMOTE_SESSION_ID — handoff_check вимагає їх вердикти тут).
# Практика — архів за порогом, відкрите («Unreleased») лишається в живому файлі, зведення дій наприкінці (earlution ai-dev-kit «Changelog archival
#   policy»; GitLab #331794 — 22.11.2026). Не беремо «курування людиною» Keep a Changelog — це журнал перевірок, не реліз-ноти.
#   python3 journal_rotate.py <корінь ядра> [--dry]   → «ротація: перенесено N · лишилось M · X → Y КБ → <архів>»
#   python3 journal_rotate.py selftest
import sys, os, re, datetime, tempfile, shutil

KEEP = re.compile(r'відкрит|кандидат|рішення Konst|НЕ ЗРОБЛЕНО', re.I)
J = 'tools/claude-code/hooks/HOOK_JOURNAL.md'


def live_key():
    s = os.environ.get('CLAUDE_CODE_REMOTE_SESSION_ID', ''); tail = s.split('_', 1)[1] if '_' in s else ''
    return f'session_{tail[:8]}' if tail else None


def rotate(root, dry=False, today=None):
    jp = os.path.join(root, J); t = open(jp, encoding='utf-8').read(); ls = t.split('\n')
    i = next((k for k, l in enumerate(ls) if l.startswith('## §1')), None)
    if i is None: return 'ротація: розділу «## §1» нема — нічого', 0
    key = live_key(); move, keep = [], []
    for k in range(i + 1, len(ls)):
        l = ls[k]
        if not re.match(r'\|\s*\d', l): continue   # лише рядки журналу (дата першою клітинкою); шапка таблиці й текст — на місці
        c = l.split('|'); verdict = c[4] if len(c) > 4 else ''
        (keep if KEEP.search(verdict) or (key and key in l) else move).append(k)
    if not move: return f'ротація: закритих рядків нема · лишилось {len(keep)}', 0
    d = today or datetime.date.today(); mv = set(move)
    rows = [ls[k] for k in move]; was = len(t.encode()); out = '\n'.join(l for k, l in enumerate(ls) if k not in mv)
    ap = os.path.join(root, 'tools/claude-code/hooks/journal', f'HOOK_JOURNAL_{d:%Y-%m}.md')
    if not dry:
        os.makedirs(os.path.dirname(ap), exist_ok=True)
        old = open(ap, encoding='utf-8').read().rstrip('\n') if os.path.isfile(ap) else \
            f'# Журнал гачків і перевірок — {d:%m.%Y} (ротація з `{J}` §1)\n\nживе доки: живий журнал гачків ядра (історія; нові рядки — лише в HOOK_JOURNAL.md).\nчитається коли: грепом за назвою перевірки чи `session_…` — цілком не читати (M21 doc_health).'
        open(ap, 'w', encoding='utf-8').write(old + f'\n\n## Рядки з §1 — ротація {d:%d.%m.%Y} (машиною, journal_rotate)\n\n'
                                              '| дата | сесія · репо | перевірка | вердикт | що змінено (коміт · тест) |\n|---|---|---|---|---|\n' + '\n'.join(rows) + '\n')
        open(jp, 'w', encoding='utf-8').write(out)
    return f'ротація: перенесено {len(rows)} · лишилось {len(keep)} · {was / 1024:.1f} → {len(out.encode()) / 1024:.1f} КБ → {os.path.relpath(ap, root)}', 0


def selftest():
    bad, cases = 0, []; tmp = tempfile.mkdtemp(prefix='jrot_')
    try:
        os.makedirs(os.path.join(tmp, 'tools/claude-code/hooks'))
        rows = ['| 01.11 | AE S1 `session_aaaaaaaa` | `x` | **справжній:** виправлено | `abc` |',
                '| 02.11 | AE S2 `session_bbbbbbbb` | `y` | **відкрите — кандидат:** ще ні | — |',
                '| 03.11 | AE S3 `session_cccccccc` | `z` | **хибне** | — |',
                '| 04.11 | EquipLens S41 `session_dddddddd` | `w` | **справжній** | `def` |']
        open(os.path.join(tmp, J), 'w').write('# Журнал\n\n## §1 Журнал\n\n| дата | сесія | перевірка | вердикт | що |\n|---|---|---|---|---|\n' + '\n'.join(rows) + '\n')
        os.environ['CLAUDE_CODE_REMOTE_SESSION_ID'] = 'session_dddddddd0000'
        msg, _ = rotate(tmp, today=datetime.date(2026, 11, 22))
        live = open(os.path.join(tmp, J)).read(); arc = open(os.path.join(tmp, 'tools/claude-code/hooks/journal/HOOK_JOURNAL_2026-11.md')).read()
        cases = [('закриті «справжній» і «хибне» → в архів місяця', 'S1 ' in arc and 'S3 ' in arc and 'S1 ' not in live and 'S3 ' not in live),
                 ('відкритий кандидат лишився', 'S2 ' in live and 'S2 ' not in arc),
                 ('рядок живої сесії лишився (його вердикти судить handoff_check тут)', 'S41' in live and 'S41' not in arc),
                 ('шапка таблиці §1 на місці', '| дата | сесія |' in live),
                 ('новий архів місяця — зі способом читання в шапці (M21)', 'читається коли' in arc),
                 ('зведення каже, скільки перенесено й лишилось', 'перенесено 2 · лишилось 2' in msg)]
        msg2, _ = rotate(tmp, today=datetime.date(2026, 11, 22))
        cases.append(('повтор — закритих нема, нічого не міняє', 'закритих рядків нема' in msg2))
        for n, ok in cases: bad += not ok; print(f'{"✓" if ok else "✗"} {n}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True); os.environ.pop('CLAUDE_CODE_REMOTE_SESSION_ID', None)
    print(f'─── journal_rotate selftest: {len(cases) - bad}/{len(cases)} ───'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print('journal_rotate.py <корінь ядра> [--dry] | selftest'); sys.exit(2)
    if a[0] == 'selftest': sys.exit(selftest())
    m, c = rotate(os.path.abspath(a[0]), dry='--dry' in a); print(m); sys.exit(c)
