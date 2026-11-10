#!/usr/bin/env python3
# живе доки: гачок пам'яті (memory-guard.sh) судить за списком слів-рішень; це — кандидат на заміну, поки лише в «тіні» (FAB-1, 10.11.2026).
"""Гачок пам'яті за ЗАЯВЛЕНИМ рядком «пам'ять: …» — перевірка без вгадування.

Навіщо. memory-guard шукає в словах Konst «так · ні · згоден · поїхали…» і вгадує, чи було рішення: точність 36 % (4 справжніх · 7 хибних,
`handoff_check.py tally` 10.11.2026), звороти латаються без кінця. Профіль уже вимагає в кожній відповіді рядок «пам'ять: <коміт> (доми)»
або «пам'ять: нового нема» — це заява, яку машина звіряє зі станом git: рядок є · названий коміт існує й уже на GitHub · «нового нема» — а дерево чисте.

  python3 memory_line.py                  — Stop: stdin — JSON гачка → {"decision":"block","reason":…} або тиша. У диспетчер НЕ підключено.
  python3 memory_line.py shadow <сесія>   — тінь: той самий вирок рядком у /tmp/lens-shadow-<сесія>.tsv; нічого не друкує й не блокує
  python3 memory_line.py tally <сесія>    — підсумок тіні за сесію одним рядком: поруч — скільки разів блокував старий memory-guard
  python3 memory_line.py selftest         — зуби (тимчасове репо з віддаленим)

Вхід — code.claude.com/docs/en/hooks «Stop input» (last_assistant_message, stop_hook_active), 10.11.2026. Помилка розбору → тиша.
Клон «лише для читання» (.git/lens-readonly) не судиться — як у handoff-remind. Репо без віддаленої гілки — «не на GitHub» не рахується.
"""
import json, os, re, subprocess, sys, time

LINE = re.compile(r"(?mi)^[\s>*_`-]*пам['’ʼ]ять\s*[:—-]\s*(.+)$")
NONE = re.compile(r"(?i)нового\s+нема")
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")


def git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True).stdout.strip()


def repos(root):
    return [os.path.join(root, d) for d in sorted(os.listdir(root))
            if os.path.isdir(os.path.join(root, d, '.git')) and not os.path.exists(os.path.join(root, d, '.git', 'lens-readonly'))]


def verdict(d, root='/home/user'):
    """→ (вид, текст) або None. Вид: no-line · none-dirty · no-sha · fake-sha · unpushed."""
    if d.get('stop_hook_active'):
        return None
    m = LINE.findall(d.get('last_assistant_message') or '')
    if not m:
        return ('no-line', "Гачок пам'яті: у відповіді нема рядка «пам'ять: <коміт> (доми)» або «пам'ять: нового нема» (профіль, ЗВІТ). "
                           "Допиши його — або запиши зміст ходу в репо й назви коміт.")
    claim, rs = m[-1], repos(root)
    dirty = [os.path.basename(r) for r in rs if git(r, 'status', '--porcelain')]
    ahead = [os.path.basename(r) for r in rs
             if git(r, 'rev-parse', '--abbrev-ref', '@{u}') and git(r, 'rev-list', '--count', '@{u}..HEAD') not in ('', '0')]
    if NONE.search(claim):
        if dirty or ahead:
            return ('none-dirty', "Гачок пам'яті: рядок каже «нового нема», а в репо є незбережене — незакомічене: " + (', '.join(dirty) or '—') +
                    "; не на GitHub: " + (', '.join(ahead) or '—') + ". Закоміть і запуш, або одним рядком поясни, чому це лишається.")
        return None
    shas = SHA.findall(claim)
    if not shas:
        return ('no-sha', "Гачок пам'яті: у рядку «пам'ять: …» нема ні хеша коміту, ні «нового нема».")
    for s in shas:
        if not any(subprocess.run(['git', '-C', r, 'cat-file', '-e', s + '^{commit}'], capture_output=True).returncode == 0 for r in rs):
            return ('fake-sha', f"Гачок пам'яті: коміту {s} з рядка «пам'ять: …» нема в жодному репо сесії — хеш з голови?")
    if ahead:
        return ('unpushed', "Гачок пам'яті: коміт названо, але HEAD ще не на GitHub у: " + ', '.join(ahead) + " — push і read-back.")
    return None


def shadow_path(sid):
    return os.path.join(os.environ.get('LENS_SHADOW_DIR', '/tmp'), f'lens-shadow-{sid}.tsv')


def shadow(d, sid, root='/home/user'):
    if d.get('stop_hook_active'):
        return
    v = verdict(d, root)
    with open(shadow_path(sid), 'a', encoding='utf-8') as f:
        f.write('\t'.join([time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'memory-line', v[0] if v else 'тиша', (v[1][:160] if v else '')]) + '\n')


def tally(sid):
    rows = [l.rstrip('\n').split('\t') for l in open(shadow_path(sid), encoding='utf-8')] if os.path.exists(shadow_path(sid)) else []
    kinds = {}
    for r in rows:
        if len(r) > 2 and r[2] != 'тиша':
            kinds[r[2]] = kinds.get(r[2], 0) + 1
    old, log = 0, os.path.join(os.environ.get('LENS_SHADOW_DIR', '/tmp'), f'lens-hooks-{sid}.tsv')
    if os.path.exists(log):
        old = sum(1 for l in open(log, encoding='utf-8', errors='replace') if '\tmemory-guard\t' in l)
    names = {'no-line': 'без рядка', 'none-dirty': '«нового нема» при незбереженому', 'no-sha': 'рядок без хеша', 'fake-sha': 'хеш з голови', 'unpushed': 'не запушено'}
    det = ' · '.join(f'{names.get(k, k)} {n}' for k, n in sorted(kinds.items())) or '—'
    return f"тінь memory-line: ходів {len(rows)} · блокував би {sum(kinds.values())} ({det}) · старий memory-guard блокував {old}"


def selftest():
    import tempfile
    T = tempfile.mkdtemp(); r = os.path.join(T, 'repo'); o = os.path.join(T, 'origin.git')
    subprocess.run(['git', 'init', '-q', '--bare', o]); subprocess.run(['git', 'clone', '-q', o, r], capture_output=True)
    sh = lambda c: subprocess.run(c, shell=True, cwd=r, capture_output=True)
    sh('git config user.email a@b; git config user.name t; echo 1 > f; git add f; git commit -qm c1; git push -q -u origin HEAD')
    h = git(r, 'rev-parse', '--short', 'HEAD'); bad = 0
    def case(name, msg, want, prep=None, active=False):
        nonlocal bad
        if prep: sh(prep)
        v = verdict({'last_assistant_message': msg, 'stop_hook_active': active}, T)
        got = v[0] if v else None
        print(('✓ ' if got == want else '✗ ') + name + ('' if got == want else f' (вийшло: {got})')); bad += got != want
    case('нема рядка → блок', 'Готово.', 'no-line')
    case('«нового нема», дерево чисте → тиша', "звіт\nпам'ять: нового нема\n██ 10%", None)
    case('коміт названо, він є і на GitHub → тиша', f"пам'ять: {h} (самері §0)", None)
    case('рядок жирним і з типографським апострофом → розпізнано', f"**пам’ять:** `{h}` (ядро)", None)
    case('рядок без хеша і без «нового нема» → блок', "пам'ять: записав у самері", 'no-sha')
    case('хеш з голови → блок', "пам'ять: deadbee (самері)", 'fake-sha')
    case('«нового нема», а є новий незакомічений файл → блок', "пам'ять: нового нема", 'none-dirty', 'echo 2 > new.md')
    case('«нового нема», а змінено наявний файл → блок', "пам'ять: нового нема", 'none-dirty', 'rm new.md; echo 2 >> f')
    case('коміт є, але не запушено → блок', f"пам'ять: {h}", 'unpushed', 'git commit -qam c2')
    case('повтор через гачок (stop_hook_active) → тиша', '', None, None, True)
    os.environ['LENS_SHADOW_DIR'] = T
    shadow({'last_assistant_message': 'Готово.'}, 'st', T); shadow({'last_assistant_message': "пам'ять: нового нема"}, 'st', T)
    open(os.path.join(T, 'lens-hooks-st.tsv'), 'w', encoding='utf-8').write("t\tstop\tmemory-guard\tx\n")
    s = tally('st'); ok = 'ходів 2' in s and 'блокував би 2' in s and 'старий memory-guard блокував 1' in s
    print(('✓ ' if ok else '✗ ') + 'тінь: два ходи → два рядки у файлі; підсумок рахує й старий гачок' + ('' if ok else f' ({s})')); bad += not ok
    print(f'─── memory_line selftest: {11 - bad}/11 ───'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['selftest']:
        sys.exit(selftest())
    if a[:1] == ['tally']:
        print(tally(a[1] if len(a) > 1 else 'nosession')); sys.exit(0)
    try:
        d = json.load(sys.stdin)
        if a[:1] == ['shadow']:
            shadow(d, a[1] if len(a) > 1 else 'nosession')
        else:
            v = verdict(d)
            if v:
                print(json.dumps({'decision': 'block', 'reason': v[1]}, ensure_ascii=False))
    except Exception:
        pass
