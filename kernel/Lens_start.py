#!/usr/bin/env python3
"""Lens_start.py — старт сесії однією командою (І-1, G-X 24.09.2026).
живе доки: назавжди (вічне, wsd 1.8) · дім: kernel/ · оголошено: Lens_INDEX.md §3 «Код і інструменти»

Що робить (нічого не пише в репо, лише читає; мережа — тільки git clone і GitHub API):
  1. clone/pull ядра lens-governance (+ продуктових репо з --product) у --root;
  2. числа бази: HEAD (sha + тема) · md5 Lens_validate.py · підсумок --gov;
  3. звірка з §5 живого самері: ✓/⚠/✗ і md5 беруться з тексту §5 — розбіжність друкується;
  4. стеля черг: розмір кожного *_CHERGA.md проти 8 192 B і порогу 7 372 B (Lens_INDEX §5);
  5. лістинг УСІХ репо власника (П-GV1): з GH_TOKEN — разом із приватними, без — лише публічні;
  6. --gov-session: друкує «Зміст» gov-протоколу (шар 1 з «ТРИ ШАРИ»);
  7. --instr ФАЙЛ: diff тексту поля Instructions проти блоку в kernel/Lens_PROJECT_instruction.md.
     Токен (github_pat_…) маскується в ОБОХ текстах до diff — у вивід не потрапляє.

Живе самері береться з Lens_INDEX §5 (рядок продукту), не вгадується за іменем чи датою (wsd 1.1).
Токен читається лише зі змінної середовища GH_TOKEN; у файли, аргументи й вивід не пишеться.

Приклади:
  GH_TOKEN=… python3 Lens_start.py --gov-session
  GH_TOKEN=… python3 Lens_start.py --product EquipLens --instr field.txt
Код виходу: 0 — база збіглась; 1 — розбіжність із §5 самері або з полем Instructions (розібратись до роботи).
"""
import argparse, difflib, hashlib, json, os, re, subprocess, sys, urllib.request

OWNER = 'Konst-Andre'
CORE = 'lens-governance'
CEIL, WARN = 8192, 7372
TOK = re.compile(r'github_pat_[A-Za-z0-9_]+')
mism = []


def sh(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, TOK.sub('<TOKEN>', (r.stdout + r.stderr).strip())


def clone(repo, root, token):
    dst = os.path.join(root, repo)
    if os.path.isdir(os.path.join(dst, '.git')):
        # fetch + ff-only від origin/main, не `pull`: клон Claude Code стоїть на гілці без upstream (G-Y)
        code, out = sh(['git', 'fetch', '-q', 'origin', 'main'], dst)
        if not code:
            code, out = sh(['git', 'merge', '-q', '--ff-only', 'origin/main'], dst)
    else:
        auth = f'x-access-token:{token}@' if token else ''
        code, out = sh(['git', 'clone', '-q', f'https://{auth}github.com/{OWNER}/{repo}.git', dst])
    if code:
        print(f'  ✗ {repo}: {out[:200]}')
        return None
    _, head = sh(['git', 'log', '-1', '--format=%h %s'], dst)
    print(f'  {repo:18} HEAD {head[:110]}')
    return dst


def repos(token):
    url = (f'https://api.github.com/user/repos?per_page=100&affiliation=owner' if token
           else f'https://api.github.com/users/{OWNER}/repos?per_page=100')
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'} if token else {})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        print(f'  ⓘ лістинг недоступний: {TOK.sub("<TOKEN>", str(e))[:120]}')
        return
    print(f'  {len(data)} репо' + ('' if token else ' (лише публічні — GH_TOKEN не дано)'))
    for r in sorted(data, key=lambda r: r['name'].lower()):
        print(f"    {r['name']:22} {'priv' if r['private'] else 'pub '} {r['pushed_at'][:10]}"
              f"{'  pages' if r.get('has_pages') else ''}")


def live_summary(core, product):
    """Перше ім'я *session_summary*.md з рядка продукту в Lens_INDEX §5 → шлях у дереві."""
    idx = open(os.path.join(core, 'kernel', 'Lens_INDEX.md'), encoding='utf-8').read()
    sec = idx.split('### Живі самері', 1)[-1].split('\n---', 1)[0]
    row = next((l for l in sec.splitlines() if l.startswith(f'| **{product}**')), '')
    m = re.search(r'`([^`]*session_summary[^`]*\.md)`', row)
    if not m:
        print(f'  ⓘ §5: рядок «{product}» без імені самері')
        return None
    name = m.group(1)
    for base, _, files in os.walk(os.path.dirname(core)):
        if name in files and '/.git' not in base:
            return os.path.join(base, name)
    print(f'  ⓘ {name} оголошено в §5, у клонах нема (живе в Project?) — звірка чисел вручну')
    return None


def base_numbers(core, summary):
    val = os.path.join(core, 'kernel', 'Lens_validate.py')
    md5 = hashlib.md5(open(val, 'rb').read()).hexdigest()
    _, out = sh([sys.executable, val, '--gov', '.'], core)
    m = re.search(r'✓ (\d+) · ⚠ (\d+) · ✗ (\d+)', out)
    got = m.groups() if m else ('?',) * 3
    print(f'  Lens_validate md5 {md5[:8]} · --gov ✓{got[0]} ⚠{got[1]} ✗{got[2]}')
    if not summary:
        return
    txt = open(summary, encoding='utf-8').read()
    s5 = re.search(r'## §5[^\n]*\n(.*?)(?=\n## )', txt, re.S)
    s5 = s5.group(1) if s5 else ''
    want = re.search(r'✓\s*(\d+)\s*·\s*⚠\s*(\d+)\s*·\s*✗\s*(\d+)', s5)
    wmd5 = re.search(r'md5 `([0-9a-f]{8})', s5)
    print(f'  §5 {os.path.basename(summary)}')
    if want:
        ok = want.groups() == got
        print(f"    --gov  {'✓' if ok else '✗'} очікувано ✓{want[1]} ⚠{want[2]} ✗{want[3]}")
        ok or mism.append('--gov')
    if wmd5:
        ok = md5.startswith(wmd5[1])
        print(f"    md5    {'✓' if ok else '✗'} очікувано {wmd5[1]}")
        ok or mism.append('md5')
    head = re.search(r'HEAD[^«\n]*«([^»]+)»', s5)
    if head:
        _, subj = sh(['git', 'log', '-1', '--format=%s'], core)
        ok = head[1].split('·')[0].strip() in subj
        print(f"    HEAD   {'✓' if ok else '⚠'} очікувано коміт «{head[1]}»")
        ok or mism.append('HEAD')


def cherga(roots):
    for root in roots:
        for base, _, files in os.walk(root):
            if '/.git' in base:
                continue
            for f in files:
                if f.endswith('_CHERGA.md'):
                    n = os.path.getsize(os.path.join(base, f))
                    flag = '✗ стеля' if n > CEIL else '⚠ поріг прополки' if n > WARN else '✓'
                    print(f'  {flag:16} {n:5} B  {os.path.relpath(os.path.join(base, f), os.path.dirname(root))}')


def gov_contents(core):
    txt = open(os.path.join(core, 'kernel', 'wsd', 'Lens_governance_protocol.md'), encoding='utf-8').read()
    m = re.search(r'## Зміст\n(.*?)\n-----', txt, re.S)
    print(m.group(1).strip() if m else '  ✗ «Зміст» не знайдено')


def instr_diff(core, field):
    canon = open(os.path.join(core, 'kernel', 'Lens_PROJECT_instruction.md'), encoding='utf-8').read()
    m = re.search(r'## ТЕКСТ ДЛЯ ПОЛЯ INSTRUCTIONS\s*```\n(.*?)\n```', canon, re.S)
    if not m:
        print('  ✗ блок «ТЕКСТ ДЛЯ ПОЛЯ INSTRUCTIONS» не знайдено')
        mism.append('instr')
        return
    norm = lambda t: [TOK.sub('<TOKEN>', l).rstrip() for l in t.strip().splitlines() if l.strip()]
    a = norm(m.group(1))[1:]           # перший рядок канону — шаблон рядка продукту
    b = norm(open(field, encoding='utf-8').read())[1:]
    d = list(difflib.unified_diff(a, b, 'канон', 'поле', n=0, lineterm=''))
    if not d:
        print('  ✓ поле ≡ канон (без рядка продукту, порожніх рядків і хвостових пробілів)')
        return
    mism.append('instr')
    print(f"  ✗ розбіжність: −{sum(l[:1] == '-' for l in d[2:])} / +{sum(l[:1] == '+' for l in d[2:])} рядків")
    for l in d[2:]:
        print('   ', l[:150])


def main():
    ap = argparse.ArgumentParser(description='Старт сесії Lens однією командою')
    ap.add_argument('--root', default='/home/claude/lens')
    ap.add_argument('--product', action='append', default=[], help='ім\'я продуктового репо (можна кілька)')
    ap.add_argument('--summary-of', default='Lens', help='рядок Lens_INDEX §5, з якого брати живе самері')
    ap.add_argument('--gov-session', action='store_true', help='друкувати «Зміст» gov-протоколу')
    ap.add_argument('--instr', help='файл із текстом поля Instructions')
    ap.add_argument('--no-list', action='store_true', help='без лістингу репо')
    a = ap.parse_args()
    token = os.environ.get('GH_TOKEN', '')
    os.makedirs(a.root, exist_ok=True)

    print('── КЛОНИ')
    core = clone(CORE, a.root, token)
    if not core:
        sys.exit(2)
    roots = [core] + [p for p in (clone(r, a.root, token) for r in a.product) if p]
    print('── ЧИСЛА БАЗИ')
    base_numbers(core, live_summary(core, a.summary_of))
    print('── ЧЕРГИ (стеля 8 192 B · поріг 7 372 B)')
    cherga(roots)
    if not a.no_list:
        print('── РЕПО (П-GV1)')
        repos(token)
    if a.gov_session:
        print('── gov-протокол · шар 1 · «Зміст»')
        gov_contents(core)
    if a.instr:
        print('── ПОЛЕ INSTRUCTIONS ⟂ kernel/Lens_PROJECT_instruction.md')
        instr_diff(core, a.instr)
    print('── ПІДСУМОК:', '✓ база збіглась' if not mism else '✗ розібратись до роботи: ' + ' · '.join(mism))
    sys.exit(1 if mism else 0)


if __name__ == '__main__':
    main()
