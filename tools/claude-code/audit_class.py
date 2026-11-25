#!/usr/bin/env python3
# живе доки: репо Lens рахують «борг аудиту» в env_check (коміт інструкцій без рядка в журналі аудиту). Дім — lens-governance:tools/claude-code/.
"""Підказка класу аудиту для боргу — «кандидат у клас 0» (EquipLens S44, 25.11.2026; 💡 агента, Konst: «приймаю, підсиль»).

Подія: правка CLAUDE.md S41 («живих рівно 2» → «≤ 2, кожне ≤ 25 КБ») 3 дні висіла боргом класу 2, Konst мусив згадувати, що аудитувати;
насправді рядок лише звівся до канону, на який сам посилається (`sessions/README.md`), — клас 0, $0.
Правило підказки (тиша при будь-якому сумніві): у коміті змінено ≤ 3 рядки інструкцій (- і + порівну), і кожне НОВЕ слово кожного
рядка є у файлі-каноні, на який рядок посилається бектиками (`шлях`, файл є в репо). Тоді — «кандидат у клас 0»; рішення й рядок у
журналі аудиту — агент (підказка не знімає борг сама).
Практика: «пропуск перевірки» — лише для дрібниць, а невизначеність веде до глибшої перевірки, не легшої (Qodo «adaptive router for code
review depth», 25.11.2026); поріг тривіальної правки — ≤ 3 змінених рядки (git-chronicle `TRIVIAL_THRESHOLD`, docs.rs, 25.11.2026).
Не беремо: автоматичне зняття боргу — нові слова, що випадково є в каноні, можуть змінити сенс правила.

  python3 audit_class.py hint <репо> <sha>…   → рядок «кандидат у клас 0: …» або нічого (exit 0 завжди)
  python3 audit_class.py selftest             → зуби на тимчасовому репо
"""
import os, re, subprocess, sys, tempfile, shutil

WORD = re.compile(r"[\w≤≥<>=+%.,-]+", re.U)
MAXL = 3


def git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True).stdout


def words(s): return {w.strip('.,') for w in WORD.findall(s) if w.strip('.,')}


def candidate(repo, sha):
    d = git(repo, 'show', '-U0', '--format=', sha, '--', 'CLAUDE.md', '.claude/settings.json', '.claude/rules', '.claude/skills')
    minus = [l[1:] for l in d.splitlines() if l.startswith('-') and not l.startswith('---')]
    plus = [l[1:] for l in d.splitlines() if l.startswith('+') and not l.startswith('+++')]
    if not plus or len(plus) != len(minus) or len(plus) > MAXL: return None
    canons = []
    for old, new in zip(minus, plus):
        paths = [p for p in re.findall(r'`([^`\s]+\.(?:md|json|toml|txt))`', new) if os.path.isfile(os.path.join(repo, p))]
        if not paths: return None
        canon = words(' '.join(open(os.path.join(repo, p), encoding='utf-8', errors='replace').read() for p in paths))
        if not (words(new) - words(old)) <= canon: return None
        canons += paths
    return sorted(set(canons))


def hint(repo, shas):
    c = [(s[:7], candidate(repo, s)) for s in shas]
    ok = [(s, p) for s, p in c if p]
    if not ok or len(ok) != len(c): return ''   # лише коли кожен коміт боргу — кандидат
    return ('кандидат у клас 0: ' + ' · '.join(f'{s} → канон {", ".join(p)}' for s, p in ok) +
            ' (≤ 3 рядки, нові слова — з канону) — звір і запиши рядок класу 0 у журнал аудиту')


def selftest():
    d = tempfile.mkdtemp(); ok = n = 0
    def say(c, m):
        nonlocal ok, n; n += 1; ok += bool(c); print(('✓ ' if c else '✗ ') + m)
    g = lambda *a: subprocess.run(['git', '-C', d, '-c', 'user.email=t@t', '-c', 'user.name=t', *a], capture_output=True, check=True)
    def commit(text):
        open(d + '/CLAUDE.md', 'w').write(text); g('commit', '-qam', 'x'); return git(d, 'rev-parse', 'HEAD').strip()
    try:
        g('init', '-q'); os.makedirs(d + '/sessions')
        open(d + '/sessions/README.md', 'w').write('Живих самері ≤ 2, кожне ≤ 25 КБ.\n')
        open(d + '/CLAUDE.md', 'w').write('- Самері — живих рівно 2 (`sessions/README.md`); витіснене — в архів.\n'); g('add', '.'); g('commit', '-qm', 'i')
        a = commit('- Самері — живих ≤ 2, кожне ≤ 25 КБ (`sessions/README.md`); витіснене — в архів.\n')
        say('кандидат' in hint(d, [a]), 'рядок звівся до канону (подія S41) → кандидат у клас 0')
        b = commit('- Самері — живих ≤ 2, кожне ≤ 25 КБ і без історії (`sessions/README.md`); витіснене — в архів.\n')
        say(hint(d, [b]) == '', 'нові слова, яких нема в каноні («без історії») → тиша')
        c = commit('- Самері — живих ≤ 2, кожне ≤ 25 КБ; витіснене — в архів.\n')
        say(hint(d, [c]) == '', 'рядок без посилання на канон → тиша')
        e = commit('- Самері — живих ≤ 2, кожне ≤ 25 КБ (`sessions/README.md`); витіснене — в архів.\n- новий рядок\n')
        say(hint(d, [e]) == '', 'доданий рядок (+ без -) → тиша')
        say(hint(d, [a, b]) == '', 'не кожен коміт боргу — кандидат → тиша')
    finally:
        shutil.rmtree(d)
    print(f'─── audit_class selftest: {ok}/{n} ───'); return ok == n


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']: sys.exit(0 if selftest() else 1)
    if a[:1] == ['hint'] and len(a) >= 3:
        h = hint(a[1], a[2:]); h and print(h); sys.exit(0)
    print(__doc__)
