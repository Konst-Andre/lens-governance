#!/usr/bin/env python3
"""live_refs · сторож пастки 8 (wsd Lens_patch_check_protocol.md 1.15): прилад, що називає ЖИВІ дані продукту, — зелений учора, червоний завтра.
живе доки: продукти мають гейти, що ганяються на даних, які міняє людина (каталог куратора, теки робота).

Що ловить у коді приладів (рядкові літерали):
  · ключ живого запису — значення з JSON продукту за шляхом (`site/data/catalog.json:categories.*.items.*.c` → коди позицій);
  · конкретний файл із живої теки (`site/anc/img` → «abegin.webp», «anc/img/abegin_s.webp»).
Такий прилад падає, щойно людина видалить чи перейменує запис (AE S125: живий «Повернути фото АНЦ» прибрав abegin.webp —
крок перед роботом зупинив звірку, CI воркера не задеплоїв). Ліки — фікстура, згенерована під прилад, або «перша позиція потрібного класу».
Храповик (ratchet): наявний борг — у закоміченій базі (JSON {файл: [посилання]}); ✗ лише НОВЕ посилання; зникле з коду — ⓘ «стисни базу»
(--update лише ПРИБИРАЄ з бази, ніколи не додає; --seed — перший запис бази). Практика: eslint-ratchet · flutter_quality_ratchet ·
Notion eslint-seatbelt — борг заморожено, нові порушення червоні, база лише зменшується (03.11.2026).

Запуск:  python3 live_refs.py <корінь репо> --keys <файл.json>:<шлях.*.ключ> [--keys …] --files <тека> [--files …]
                              --tools <тека> [--tools …] --baseline <файл.json> [--update | --seed]
         python3 live_refs.py selftest      (LIVE_REFS_INJECT=1 → selftest червоніє: храповик пропускає нове)
Вихід:   ✗ <файл>: «посилання» (ключ / файл живих даних) — нове · ⓘ стисни базу · рядок ПІДСУМОК; exit 1 на ✗.
"""
import json, os, re, sys, tempfile, pathlib

LIT = re.compile(r"""(?<![\w$])(['"`])((?:(?!\1)[^\\\n]|\\.){1,200})\1""")
EXT = ('.py', '.mjs', '.js', '.sh', '.cjs')
TOK = re.compile(r'(?<![a-z0-9_-])[a-z0-9_-]{3,40}(?![a-z0-9_-])')


def walk(obj, parts):
    if not parts:
        if isinstance(obj, (str, int)): yield str(obj)
        return
    p, rest = parts[0], parts[1:]
    if p == '*':
        vals = obj.values() if isinstance(obj, dict) else obj if isinstance(obj, list) else []
        for v in vals: yield from walk(v, rest)
    elif isinstance(obj, dict) and p in obj: yield from walk(obj[p], rest)


def live_keys(root, specs):
    keys = set()
    for spec in specs:
        f, path = spec.split(':', 1)
        try: data = json.load(open(os.path.join(root, f), encoding='utf-8'))
        except Exception as e: sys.exit(f'✗ live_refs: {f} не читається ({str(e)[:60]})')
        keys |= {k for k in walk(data, path.split('.')) if len(k) >= 3}
    return keys


def live_files(root, dirs):
    names = {}
    for d in dirs:
        full = os.path.join(root, d)
        for n in (os.listdir(full) if os.path.isdir(full) else []):
            if os.path.isfile(os.path.join(full, n)): names[n] = d
    return names


def scan(root, tools, keys, files):
    found = {}
    for t in tools:
        for p in sorted(pathlib.Path(root, t).rglob('*')):
            if not p.is_file() or p.suffix not in EXT: continue
            rel = str(p.relative_to(root))
            refs = set()
            for line in p.read_text(encoding='utf-8', errors='ignore').split('\n'):
                if 'live_refs: ok' in line: continue          # свідомий виняток на рядку (з причиною поруч)
                for _, s in LIT.findall(line):
                    if s in keys: refs.add(s)
                    # код усередині рядка — селектор Playwright `[data-c="strep"]`, адреса `?c=strep`: слово з межами не [a-z0-9_-]
                    refs |= {w for w in TOK.findall(s) if w in keys and w != s}
                    base = s.rsplit('/', 1)[-1]
                    if base in files and ('/' not in s or s.rstrip('/').endswith(files[base].rstrip('/').rsplit('/', 1)[-1] + '/' + base)): refs.add(files[base].rstrip('/') + '/' + base)
            if refs: found[rel] = sorted(refs)
    return found


def judge(found, base, inject=False):
    new, gone = [], []
    for f, refs in found.items():
        for r in refs:
            if r not in base.get(f, []): new.append((f, r))
    if inject: new = []   # зуби: храповик «забуває» нове
    for f, refs in base.items():
        for r in refs:
            if r not in found.get(f, []): gone.append((f, r))
    return new, gone


def run(argv):
    root = argv[0]
    opt = {'keys': [], 'files': [], 'tools': []}
    base_f, mode = None, ''
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ('--keys', '--files', '--tools'): opt[a[2:]].append(argv[i + 1]); i += 2; continue
        if a == '--baseline': base_f = argv[i + 1]; i += 2; continue
        if a in ('--update', '--seed'): mode = a[2:]; i += 1; continue
        sys.exit('✗ live_refs: невідомий аргумент ' + a)
    if not base_f or not opt['tools']: sys.exit('✗ live_refs: потрібні --tools і --baseline')
    keys, files = live_keys(root, opt['keys']), live_files(root, opt['files'])
    found = scan(root, opt['tools'], keys, files)
    bp = os.path.join(root, base_f)
    base = json.load(open(bp, encoding='utf-8')).get('refs', {}) if os.path.exists(bp) else {}
    if mode == 'seed':
        json.dump({'about': 'живе доки: є борг пастки 8 — прилади, що називають живі дані (live_refs.py ядра). База лише зменшується: --update.', 'refs': found},
                  open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print(f'live_refs: базу записано — {sum(map(len, found.values()))} посилань у {len(found)} файлах'); return 0
    new, gone = judge(found, base, os.environ.get('LIVE_REFS_INJECT') == '1')
    for f, r in new: print(f'  ✗ {f}: «{r}» — нове посилання на живі дані (пастка 8): фікстура або перша позиція потрібного класу; свідомо — коментар «live_refs: ok — <чому>»')
    if mode == 'update' and gone:
        for f, r in gone: base[f] = [x for x in base.get(f, []) if x != r]
        base = {f: v for f, v in base.items() if v}
        json.dump({'about': 'живе доки: є борг пастки 8 — прилади, що називають живі дані (live_refs.py ядра). База лише зменшується: --update.', 'refs': base},
                  open(bp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'  ⓘ базу стиснуто на {len(gone)}'); gone = []
    elif gone: print(f'  ⓘ у базі {len(gone)} посилань, яких уже нема в коді — стисни: --update')
    debt = sum(len(v) for v in base.values())
    print(f'ПІДСУМОК live_refs: ✗ {len(new)} · борг {debt} у {len(base)} файлах · живих ключів {len(keys)} · файлів {len(files)}')
    return 1 if new else 0


def selftest():
    d = pathlib.Path(tempfile.mkdtemp(prefix='live_refs_'))
    (d / 'data').mkdir(); (d / 'img').mkdir(); (d / 'tools').mkdir()
    (d / 'data/cat.json').write_text(json.dumps({'categories': {'a': {'items': [{'c': 'alpha'}, {'c': 'beta'}]}}}))
    (d / 'img/alpha.webp').write_bytes(b'x')
    (d / 'tools/old.py').write_text("x = 'alpha'\n")
    args = [str(d), '--keys', 'data/cat.json:categories.*.items.*.c', '--files', 'img', '--tools', 'tools', '--baseline', 'base.json']
    ok = []
    def chk(n, c): ok.append(c); print(('  ✓ ' if c else '  ✗ ') + n)
    run(args + ['--seed'])
    chk('база: старий борг не червоніє', run(args) == 0)
    (d / 'tools/new.mjs').write_text("const f = fs.readFileSync('site/x/img/alpha.webp');\nconst code = \"beta\";\n")
    chk('нове посилання (файл живої теки і ключ запису) — ✗', run(args) == 1)
    (d / 'tools/new.mjs').write_text("page.click('[data-c=\"beta\"] .x')\n")
    chk('код живого запису всередині селектора [data-c="…"] — ✗', run(args) == 1)
    (d / 'tools/new.mjs').write_text("const code = 'beta'; // live_refs: ok — перевіряє саме цю позицію\nconst x = 'gamma';\n")
    chk('свідомий виняток з причиною і чужий рядок — мовчить', run(args) == 0)
    (d / 'tools/old.py').write_text("x = items[0]\n")
    run(args + ['--update'])
    chk('борг виправлено → --update стискає базу (лише прибирає)', json.load(open(d / 'base.json'))['refs'] == {})
    bad = ok.count(False)
    print(f'─── live_refs selftest: {len(ok) - bad}/{len(ok)} ───')
    return 1 if bad else 0


if __name__ == '__main__':
    if sys.argv[1:2] == ['selftest']: sys.exit(selftest())
    if len(sys.argv) < 2: sys.exit(__doc__)
    sys.exit(run(sys.argv[1:]))
