#!/usr/bin/env python3
# живе доки: репо тримають правила частини коду в .claude/rules/*.md з `paths:`. Дім — lens-governance:tools/claude-code/hooks/.
"""Сторож правил з `paths:` — правило приходить до агента машиною, а не пам'яттю.

Чому (Konst AE S142: «розраховувати лише на те, що агент виконає правило, — 50 на 50»): Claude Code вантажить правило з `paths:` лише на
Read · Write · Edit і `cat` / `head` одного файла, НЕ на Grep (code.claude.com/docs/en/memory, 12.11.2026). Агент, що планує екран грепом або
правит файл через Bash (sed, python), правила не отримує. Вказівник у CLAUDE.md — пам'ять; цей гачок — машина.

Як: PreToolUse (диспетчер lens-hooks.sh, `pre`). Ціль виклику — file_path (Edit · Write), path / pattern (Grep · Glob) або шляхи в команді Bash.
Ціль під `paths:` правила, а правило в цій сесії ще не приходило → additionalContext з текстом правила (раз на сесію; ≤ 9 000 знаків — стеля
гачка 10 000). Read файла під `paths:` або самого правила, і Bash, що є лише `cat` / `head` одного файла, — Claude Code вантажить правило сам → лише позначка, без дубля.
Позначки — /tmp/lens-rules-<сесія>-<хеш правила>; стиснення стирає їх (диспетчер, SessionStart source=compact) — переказ правила не несе.
Блокувати не блокує (правило — контекст, не заборона). Подія InstructionsLoaded точніша, але setup script її не реєструє — не беремо.
  python3 rules-guard.py pre < подія.json   |   python3 rules-guard.py selftest
"""
import hashlib, json, os, re, sys, tempfile

MARK = os.environ.get('LENS_MARK_DIR', '/tmp')
CAP = 9000


def glob_re(g):
    out, i = '', 0
    while i < len(g):
        if g.startswith('**/', i): out += '(?:.*/)?'; i += 3
        elif g.startswith('**', i): out += '.*'; i += 2
        elif g[i] == '*': out += '[^/]*'; i += 1
        elif g[i] == '?': out += '[^/]'; i += 1
        else: out += re.escape(g[i]); i += 1
    return re.compile(out + '$')


def rules(root):
    d = os.path.join(root, '.claude', 'rules'); out = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, f)
        if not f.endswith('.md'): continue
        t = open(p, encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n', t, re.S)
        if not m or 'paths:' not in m[1]: continue
        gl = re.findall(r'^\s*-\s*["\']?([^"\'\n]+)["\']?\s*$', m[1], re.M)
        out.append((p, [glob_re(g.strip()) for g in gl], t[m.end():]))
    return out


def root_of(path):
    p = os.path.abspath(path)
    while p != '/':
        if os.path.isdir(os.path.join(p, '.claude', 'rules')): return p
        p = os.path.dirname(p)
    return None


PATH = r'(?<![\w$])((?:\.{1,2}/|/)?[\w.-]+(?:/[\w.*-]+)+/?)'
QPATH = r'[\'"]((?:\.{1,2}/|/)?[\w.-]+(?:/[\w.*-]+)+/?)[\'"]'
HEREDOC = r'<<-?\s*[\'"]?(\w+)[\'"]?[^\n]*\n(.*?)(?:\n\1\b|$)'
MSG = r'(?:^|\s)-m\s+("(?:[^"\\]|\\.)*"|\'[^\']*\')'
def mention(cmd):
    # Bash: прибрати шляхи, що лише ЗГАДАНІ в тексті (AE S143, хибне: heredoc, що правив самері, назвав `site/tools/ae_rules.js` → ~10 тис. знаків
    # правил без роботи з файлом). Тіло heredoc — лише шляхи цілим рядком у лапках ('x/y' · "x/y" — як open(...) / Path(...)); повідомлення -m "…" — геть.
    cmd = re.sub(HEREDOC, lambda m: '\n' + ' '.join(re.findall(QPATH, m.group(2))), cmd, flags=re.S)
    return re.sub(MSG, ' ', cmd)

def targets(d):
    ti = d.get('tool_input') or {}; cwd = d.get('cwd') or os.getcwd(); tool = d.get('tool_name', '')
    if tool in ('Edit', 'Write', 'Read', 'NotebookEdit'): c = [ti.get('file_path') or ti.get('notebook_path') or '']
    elif tool in ('Grep', 'Glob'): c = [ti.get('path') or '', ti.get('glob') or '', ti.get('pattern', '') if tool == 'Glob' else '']
    elif tool == 'Bash':
        cmd = str(ti.get('command', ''))
        cd = re.findall(r'(?:^|&&|;)\s*cd\s+([^\s;&|]+)', cmd); cwd = os.path.join(cwd, cd[-1]) if cd else cwd   # «cd X && …» — шляхи від X
        c = re.findall(PATH, mention(cmd))
    else: c = []
    return [os.path.normpath(os.path.join(cwd, x)) for x in c if x], tool


# Bash, що є лише `cat` / `head` ОДНОГО файла (можна з `cd X &&`): Claude Code вантажить правило сам («a Bash command that counts as a read,
# such as cat or head on a single file» — code.claude.com/docs/en/memory, 12.11.2026) → лише позначка, без дубля (S142, замість InstructionsLoaded)
NATIVE = re.compile(r'\s*(?:cd\s+[^\s;&|]+\s*&&\s*)?(?:cat|head)(?:\s+-n\s*\d+|\s+-\d+)?\s+[^\s;&|<>*]+\s*')

def mark(sid, rule): return os.path.join(MARK, f'lens-rules-{sid}-{hashlib.md5(rule.encode()).hexdigest()[:10]}')


def pre(d):
    ts, tool = targets(d); sid = re.sub(r'[^\w-]', '', str(d.get('session_id', 'nosession'))); due = {}
    for t in ts:
        r = root_of(t if os.path.isdir(t) else os.path.dirname(t) or '.')
        if not r: continue
        rel = os.path.relpath(t, r)
        for p, gl, body in rules(r):
            m = mark(sid, p)
            hit = os.path.abspath(t) == os.path.abspath(p) or any(g.match(rel) or g.match(rel.rstrip('/') + '/x') for g in gl)
            if not hit or os.path.exists(m) or p in due: continue
            if tool == 'Read' or NATIVE.fullmatch(str((d.get('tool_input') or {}).get('command', '')) if tool == 'Bash' else '-'): open(m, 'w').close(); continue   # Claude Code вантажить правило сам (path_glob_match); Read самого правила — теж
            due[p] = (os.path.relpath(p, r), rel, body.strip(), m)
    # кілька правил на тих самих шляхах (AE: site/ — editor-worker · gates · ui, разом > стелі): цілим — від найменшого, доки влазить;
    # решта — вказівник «прочитай Read», без позначки: повторюється, доки агент не прочитає (S142, наживо — ui.md обрізався б)
    full, ptr, room = [], [], CAP
    for name, rel, body, m in sorted(due.values(), key=lambda x: len(x[2])):
        if len(body) + 300 <= room: full.append(f'Правило `{name}` діє для `{rel}` (його `paths:`), а в цій сесії ще не приходило — Claude Code вантажить його лише на Read / Edit, не на Grep чи Bash (S142). Текст:\n\n{body}'); room -= len(body) + 300; open(m, 'w').close()
        else: ptr.append(f'`{name}` ({len(body)} знаків)')
    if ptr: full.append('Діють і ще не прочитані правила: ' + ' · '.join(ptr) + ' — прочитай їх Read до правки (нагадування повториться, доки не прочитаєш).')
    if full: print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': '\n\n---\n\n'.join(full)}}, ensure_ascii=False))

def selftest():
    global MARK
    d = tempfile.mkdtemp(prefix='rg-'); MARK = tempfile.mkdtemp(prefix='rgm-')
    os.makedirs(f'{d}/.claude/rules'); os.makedirs(f'{d}/site'); os.makedirs(f'{d}/tools')
    open(f'{d}/.claude/rules/ui.md', 'w').write('---\npaths:\n  - "site/**"\n  - "docs/shots/**"\n---\n# Екрани\nОдна мова родини.\n')
    open(f'{d}/.claude/rules/x.md', 'w').write('# без paths — завжди в контексті\n')
    open(f'{d}/site/index.html', 'w').write('x')
    import io, contextlib
    def run(tool, ti, sid='s1'):
        b = io.StringIO()
        with contextlib.redirect_stdout(b): pre({'tool_name': tool, 'tool_input': ti, 'cwd': d, 'session_id': sid})
        return b.getvalue()
    cases = [('Edit site/index.html → текст правила', lambda: 'Одна мова родини' in run('Edit', {'file_path': f'{d}/site/index.html'})),
             ('вдруге в тій самій сесії → тиша', lambda: run('Edit', {'file_path': f'{d}/site/index.html'}) == ''),
             ('Bash «grep -n x site/index.html» (інша сесія) → текст', lambda: 'Одна мова' in run('Bash', {'command': 'grep -n x site/index.html'}, 's2')),
             ('Bash «cd site && sed -i … index.html» → текст (шлях від cd)', lambda: 'Одна мова' in run('Bash', {'command': f'cd {d}/site && sed -i s/a/b/ ./index.html'}, 's3')),
             ('Grep path=site → текст', lambda: 'Одна мова' in run('Grep', {'pattern': 'x', 'path': f'{d}/site'}, 's4')),
             ('Read site/… → тиша (Claude Code вантажить сам), потім Edit → тиша', lambda: run('Read', {'file_path': f'{d}/site/index.html'}, 's5') == '' and run('Edit', {'file_path': f'{d}/site/index.html'}, 's5') == ''),
             ('Bash поза paths (tools/x.py) → тиша', lambda: run('Bash', {'command': 'python3 tools/x.py'}, 's6') == ''),
             ('позначку стерто (стиснення) → знову текст', lambda: (os.remove(mark('s1', f'{d}/.claude/rules/ui.md')), 'Одна мова' in run('Edit', {'file_path': f'{d}/site/index.html'}))[1]),
             ('два правила, разом > стелі: менше — цілим, більше — вказівник; Read великого → далі тиша', lambda: (open(f'{d}/.claude/rules/big.md', 'w').write('---\npaths:\n  - "site/**"\n---\n' + 'ж' * 9500), (lambda o: 'Одна мова' in o and '`.claude/rules/big.md` (9500' in o)(run('Edit', {'file_path': f'{d}/site/index.html'}, 's8')) and 'big.md' in run('Edit', {'file_path': f'{d}/site/index.html'}, 's8') and (run('Read', {'file_path': f'{d}/.claude/rules/big.md'}, 's8') == '') and run('Edit', {'file_path': f'{d}/site/index.html'}, 's8') == '')[1]),
             ('Bash «cat site/index.html» (один файл) → тиша, потім Edit → тиша (Claude Code вантажить сам)', lambda: run('Bash', {'command': 'cat site/index.html'}, 's9') == '' and run('Edit', {'file_path': f'{d}/site/index.html'}, 's9') == ''),
             ('Bash «cat site/index.html | grep x» → текст (не чисте читання)', lambda: 'Одна мова' in run('Bash', {'command': 'cat site/index.html | grep x'}, 's10')),
             ('Bash heredoc, що лише згадує шлях у тексті → тиша (AE S143, хибне)', lambda: run('Bash', {'command': "python3 - <<'PY'\ns = 'правка: див. `site/index.html` і site/a.js'\nPY"}, 's11') == ''),
             ('Bash heredoc з open(шлях у лапках) → текст (правка файла через python)', lambda: 'Одна мова' in run('Bash', {'command': "python3 - <<'PY'\nopen('site/index.html','w').write('x')\nPY"}, 's12')),
             ('Bash git commit -m «… шлях …» → тиша (згадка в повідомленні)', lambda: run('Bash', {'command': 'git add docs/a.md && git commit -m "правка поруч із site/index.html"'}, 's13') == ''),
             ('правило без paths — не чіпає', lambda: 'без paths' not in run('Edit', {'file_path': f'{d}/site/index.html'}, 's7'))]
    bad = 0
    for n, f in cases:
        ok = f(); bad += not ok; print(('✓ ' if ok else '✗ ') + n)
    print(f'rules-guard selftest: {len(cases) - bad}/{len(cases)}'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'selftest': sys.exit(selftest())
    try: pre(json.load(sys.stdin))
    except Exception: __import__('traceback').print_exc();   # сторож не ламає виклик, але падіння — у журнал помилок
