#!/usr/bin/env python3
# живе доки: агент Claude Code читає канон ядра й продуктів. Дім — lens-governance:tools/claude-code/ (бриф DOC-1, «так» Konst 10.10.2026, QR CC-7).
"""Здоров'я документів — скільки коштує їх ЧИТАТИ в Claude Code (не цілісність канону: її тримає гейт kernel/Lens_validate.py).
Мірки (замінили G6 «120 / 200 КБ» Project-епохи, взяті без заміру):
  M1 щосесійне — CLAUDE.md кореня і профіль (tools/claude-code/PROFILE.md) ≤ 200 рядків (code.claude.com/docs/en/memory, 10.10.2026)
  M2 старт цілком — черга (*_CHERGA.md), живі самері (sessions/*summary*.md) і найновіше самері не-Lens (docs/summary/) ≤ 25 КБ
  M3 розділ (# / ## / ###) ≤ 16 КБ ≈ 5 тис. токенів — точкове читання платить за розділ; не міряє історію (той самий список, що M5)
     і розділ, що на ≥ 80 % — один блок коду для копіювання (блок неподільний, його беруть цілим)
     (M2 · M3 — числа агента 10.10; звірено 10–18.10: 8+ сесій QR · AE · ядра, точність doc_health 84 % — журнал гачків §0;
     ліміт Read CLI 25 тис. токенів, застосунок ПК — 10 тис.: github.com/anthropics/claude-code/issues/40357, 19.10.2026 — звіт користувачів)
  M4 файл > 80 КБ — лише з «читається коли» в шапці: одним Read його не взяти (ліміт 25 тис. токенів ≈ 80–100 КБ укр. тексту, замір 10.10)
  M5 мертві шляхи — `шлях/зі/слешем.розш` у живому .md, якого нема в репо (ні від кореня, ні від теки документа, ні як хвіст
     наявного шляху: `data/x.json` = `site/data/x.json`). Не перевіряє: історію (archive/ · sessions/ · summary/ · journal/ · DECISIONS ·
     AUDIT · HOOK_JOURNAL · ADOPTIONS · FINDINGS; розділи із заголовком «переїзд/старий/історія/було»), блоки коду ```, `Репо:шлях`,
     голі назви (їх ловить handoff_check у самері), у ядрі — tools/claude-code/ (описує шляхи продуктів). Майбутній файл — у «лапках», не в бектиках.
     Чому (пропуск Konst 18.10.2026, AE S90): README і ARCHITECTURE протухли з 02.10, і жодна перевірка не бачила; практика — детермінована
     перевірка посилань у документах (hyperhive check-doc-refs; lychee: виключення за шляхом, блоки коду не перевіряються, 18.10.2026).
  M6 черга відстала — пункт, який живе самері позначило закритим (`ID` ✅ · `ID` — закрито), у черзі досі відкритий (`queue_open`
     ядра). Позначка — одразу після `id`, як ключове слово «closes #N» у GitHub/GitLab: «`ID`: підкрок ✅» — не закриття
     (пропозиція агента, «так» Konst 18.10.2026, AE S90).
  M7 мертва адреса в межах файла — складена `§N-x` / `§N.M` / `§N(…)` у живому .md з ≥ 3 заголовками «§N», а заголовка §N нема і поруч не названо
     чужого документа (ім'я файла, wsd, самері, «Бібліотека §…»). Чому (аудит маніфесту стендів 19.10.2026): п'ять `§13-*` вели в нікуди — M5 бачить шляхи,
     не адреси; практика — звірка адреси з заголовками того ж файла, блоки коду — геть (lychee «anchors», 19.10.2026; наші § — текст, не посилання).
  M8 правило без перевірки — у документі, що оголошує форму «Кожне правило — **Правило** · … **Як перевірити**» (маніфест стендів §3), розділ
     (## / ###), де «**Правило» більше, ніж «Як перевірити», і нема `K2:n/a`. Чому (💡 Konst 19.10.2026, бриф SB-1 Х6): правило без способу
     перевірки виконується «на око»; Х3–Х4 перепису пропустили шість таких (§1 · §3-п.15 · §8.1 · §8.2 · §8.9 · §8.10) — побачив лише замір.
     Практика — системна інженерія NASA: метод перевірки (inspection · analysis · demonstration · test) називається, коли вимогу пишуть
     (LSU / NASA «Writing Requirements» L22.02; NTRS 20110008330 Ares I-X, 19.10.2026).
Лише ⚠ (не блокує): один рядок для env_check; адреси — --list.
  python3 doc_health.py [<репо>] [--list] | selftest
"""
import os, re, subprocess, sys, tempfile

M1_LINES, M2_KB, M3_KB, M4_KB = 200, 25, 16, 80


def files(root):
    out = subprocess.run(['git', 'ls-files', '*.md'], cwd=root, capture_output=True, text=True).stdout.split()
    return [f for f in out if not f.startswith('archive/') and '/journal/' not in '/' + f]   # journal/ — архів ротації журналу гачків, читається грепом (18.10.2026: 73 КБ дало хибне M3)


def scan(root):
    found = []   # (мірка, файл, що)
    nl = sorted(f for f in files(root) if f.startswith('docs/summary/') and f.endswith('.md'))
    newest_nl = max(nl, key=lambda f: (re.findall(r'\d{4}-\d{2}-\d{2}', f) or [''])[0] + (re.findall(r'_s(\d+)\.md$', f) or ['0'])[0].zfill(3)) if nl else None
    for f in files(root):
        p = os.path.join(root, f)
        if not os.path.isfile(p): continue
        txt = open(p, encoding='utf-8', errors='replace').read(); kb = len(txt.encode()) / 1024
        if f in ('CLAUDE.md', 'tools/claude-code/PROFILE.md'):
            n = txt.count('\n') + 1
            if n > M1_LINES: found.append(('M1', f, f'{n} рядків > {M1_LINES}'))
        whole = f in ('CLAUDE.md', 'tools/claude-code/PROFILE.md') or bool(re.search(r'_CHERGA\.md$', f)) or (f.startswith('sessions/') and 'summary' in f) or f == newest_nl   # не-Lens: лише найновіше самері читається на старті (AE S91)
        if whole and f not in ('CLAUDE.md', 'tools/claude-code/PROFILE.md') and kb > M2_KB:
            found.append(('M2', f, f'{kb:.0f} КБ > {M2_KB} — читається цілком на старті'))
        if whole: continue   # читається цілком за задумом — розмір розділу не важить, стережуть M1/M2 (перший прогін 10.10: профіль і черга — 2 хибних M3)
        for s in re.split(r'(?m)^(?=#{1,3} )', txt):   # до ### — найменший розділ, який агент бере окремо (грепом «§3-г»); до ## давало хибне: план адмінки QR §3 = 12 КБ таблиця + 4 × 3–6 КБ (10.10)
            sk = len(s.encode()) / 1024
            code = sum(len(b.encode()) for b in re.findall(r'(?ms)^```.*?^```', s))
            if sk > M3_KB and s.lstrip().startswith('#') and not M5_HIST.search(f) and code < 0.8 * len(s.encode()):   # історія — грепом (як M5); блок коду — неподільний (Twig «code splitting», MDKeyChunker arXiv 2603.23533, 19.10.2026)
                found.append(('M3', f, f'розділ {sk:.0f} КБ «{s.splitlines()[0][:60].strip()}»'))
        if kb > M4_KB and 'читається' not in '\n'.join(txt.splitlines()[:12]).lower():
            found.append(('M4', f, f'{kb:.0f} КБ без «читається коли» — одним Read не взяти'))
    found += dead_paths(root)
    found += queue_behind(root)
    found += dead_sections(root)
    found += unchecked_rules(root)
    return found


def queue_behind(root):
    """M6: `ID` ✅ / закрито в живому самері, а в черзі пункт відкритий."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        sys.path.insert(0, os.path.join(here, '..', '..', 'kernel')); sys.path.insert(0, here)
        from Lens_validate import queue_open
        from handoff_check import live_summary
    except Exception:
        return []
    import glob
    q = next((os.path.join(root, p) for p in ['docs/CHERGA.md', 'kernel/Lens_governance_CHERGA.md'] if os.path.isfile(os.path.join(root, p))), None) \
        or next(iter(glob.glob(os.path.join(root, 'lens', '*_CHERGA.md'))), None)
    sm = live_summary(root)
    if not q or not sm: return []
    ids = [i for i, _ in queue_open(open(q, encoding='utf-8').read())]
    txt = open(os.path.join(root, sm), encoding='utf-8', errors='replace').read()
    return [('M6', sm, f'`{i}` закрито в самері, у черзі ({os.path.relpath(q, root)}) — відкритий') for i in ids
            if re.search(r'`' + re.escape(i) + r'`\**\s*[·—–-]?\s*(✅|закрит)', txt)]


M5_HIST = re.compile(r'(^|/)(archive|sessions|summary|journal)/|DECISIONS|AUDIT|HOOK_JOURNAL|ADOPTIONS|FINDINGS|ARCHIVE_INDEX')
M5_SECT = re.compile(r'(?i)переїзд|старий|старі|істор|було|history')
M5_PATH = re.compile(r'^[\w.-]+(/[\w.-]+)+\.(md|js|mjs|py|sh|html|json|toml|yml|yaml|css|txt)$')


def dead_paths(root):
    """M5: `шлях/до/файла.розш` у живому .md, якого нема в репо (правила — шапка файла)."""
    known = [k for k in subprocess.run(['git', 'ls-files'], cwd=root, capture_output=True, text=True).stdout.split('\n') if k]
    ks, alld = set(known), set()
    for k in known:
        d = os.path.dirname(k)
        while d: alld.add(d); d = os.path.dirname(d)
    kernel = os.path.isfile(os.path.join(root, 'kernel/Lens_INDEX.md'))
    out = []
    for f in known:
        if not f.endswith('.md') or M5_HIST.search(f) or (kernel and f.startswith('tools/claude-code/')): continue
        p_ = os.path.join(root, f)
        if not os.path.isfile(p_): continue
        txt = re.sub(r'(?ms)^```.*?^```', '', open(p_, encoding='utf-8', errors='replace').read())
        for s in re.split(r'(?m)^(?=#{1,4} )', txt):
            if s.startswith('#') and M5_SECT.search(s.splitlines()[0]): continue
            for m in re.finditer(r'`([^`\s]+)`', s):
                p = re.sub(r':\d+(-\d+)?$', '', m.group(1)).rstrip('/').rstrip('.,;:)')
                if re.match(r'^[A-Za-z][\w.-]*:', p) or not M5_PATH.match(p): continue
                if any(c in ks or c in alld for c in (p, os.path.normpath(os.path.join(os.path.dirname(f), p)))): continue
                if any(k.endswith('/' + p) for k in known): continue
                out.append(('M5', f, p))
    return out


M7_OTHER = re.compile(r'(\.md|\.py|\.sh|\.mjs|\.js|wsd|gov|INDEX|самері|CLAUDE|ядра|профіл|PROFILE|бриф|том|кукбук|Cookbook|REPO_FRAME|ADOPT|SHOTS|PREVIEW|ADAPT|CHAT_TOOLS|CLOUDFLARE|HOOK_JOURNAL|маніфест|manifest|`[A-Za-z-]+:|\bS\d+|\bCC-\d+)', re.I)
def dead_sections(root):
    """M7: складена адреса `§N-x` / `§N.M` / `§N(…)` без заголовка §N у тому ж файлі (правила — шапка файла)."""
    out = []
    for f in files(root):
        if re.search(r'(^|/)(sessions|summary|journal)/|DECISIONS|AUDIT|HOOK_JOURNAL|ADOPTIONS|_HISTORY|CHERGA|delta_running|INDEX', f): continue
        p_ = os.path.join(root, f)
        if not os.path.isfile(p_): continue
        t = re.sub(r'(?ms)^```.*?^```', '', open(p_, encoding='utf-8', errors='replace').read())
        heads = {m.group(1) for m in re.finditer(r'(?m)^#{1,4}\s+.*?§\s?(\d+)', t)}
        if len(heads) < 3: continue
        for m in re.finditer(r'(?<![\w`])§\s?(\d+)(?=[-.(])(?!\.\d{2,})', t):
            if m.group(1) == '0' or m.group(1) in heads: continue
            ls = t.rfind('\n', 0, m.start()) + 1
            if t[ls:].lstrip().startswith('#'): continue
            pre = t[max(ls, m.start() - 70):m.start()]
            if M7_OTHER.search(pre) or re.search(r"[А-ЯҐЄІЇA-Z][\w’'-]{2,}\s+$", pre): continue   # «Бібліотека §7.1» — чужий документ
            out.append(('M7', f, t[m.start():m.start() + 12].split()[0].rstrip(').,;:')))
    return out


M8_FORM = 'Кожне правило — **Правило**'
def unchecked_rules(root):
    """M8: у документі з оголошеною формою правила — розділ, де «**Правило» більше, ніж «Як перевірити» (правила — шапка файла)."""
    out = []
    for f in files(root):
        p_ = os.path.join(root, f)
        if not f.endswith('.md') or not os.path.isfile(p_): continue
        t = open(p_, encoding='utf-8', errors='replace').read()
        if M8_FORM not in t: continue
        for s in re.split(r'(?m)^(?=#{2,3} )', re.sub(r'(?ms)^```.*?^```', '', t)):
            if not s.startswith('#') or 'K2:n/a' in s: continue
            r, c = len(re.findall(r'\*\*Правило', s)), s.count('Як перевірити')
            if r > c: out.append(('M8', f, f'«{s.splitlines()[0][:50].strip()}» — правил {r}, перевірок {c}'))
    return out


def line(root):
    f = scan(root)
    if not f: return '✓', f'документи: ✓ щосесійні ≤ {M1_LINES} рядків · старт ≤ {M2_KB} КБ · розділи ≤ {M3_KB} КБ · великі з маршрутом'
    by = {}
    for m, *_ in f: by[m] = by.get(m, 0) + 1
    name = {'M1': 'щосесійні задовгі', 'M2': 'файли старту завеликі', 'M3': f'розділів > {M3_KB} КБ', 'M4': f'> {M4_KB} КБ без маршруту', 'M5': 'мертвих шляхів', 'M6': 'черга відстала від самері', 'M7': 'мертвих адрес §', 'M8': 'правил без «Як перевірити»'}
    worst = max((x for x in f if x[0] == 'M3'), key=lambda x: float(re.search(r'(\d+) КБ', x[2])[1]), default=None)
    return '⚠', 'документи: ' + ' · '.join(f'{name[m]} {n}' for m, n in sorted(by.items())) + (f' (найбільший — {worst[1]} {worst[2]})' if worst else '') + ' — деталі: doc_health.py --list'


def selftest():
    bad = 0
    def repo(fs):
        d = tempfile.mkdtemp(prefix='dh-'); subprocess.run(['git', 'init', '-q'], cwd=d, check=True)
        for f, t in fs.items():
            os.makedirs(os.path.dirname(os.path.join(d, f)) or d, exist_ok=True); open(os.path.join(d, f), 'w').write(t)
        subprocess.run(['git', 'add', '-A'], cwd=d, check=True); return d
    sec = lambda kb: '## Розділ\n' + 'х' * (kb * 512) + '\n'   # кирилиця — 2 байти на знак
    Q = '## Відкрите\n| id | предмет | відкрито | умова |\n|---|---|---|---|\n| `AE-X` | x | 18.10.2026 | y |\n| `AE-Y` | y | 18.10.2026 | z |\n\n-----\n'
    cases = [('чисте репо → ✓', {'CLAUDE.md': 'x\n' * 50, 'lens/A.md': sec(4)}, '✓', ''),
             ('CLAUDE.md 250 рядків → ⚠ M1', {'CLAUDE.md': 'x\n' * 250}, '⚠', 'щосесійні задовгі 1'),
             ('черга 30 КБ → ⚠ M2', {'lens/P_CHERGA.md': sec(30)}, '⚠', 'файли старту завеликі 1'),
             ('розділ 20 КБ → ⚠ M3', {'lens/B.md': sec(20)}, '⚠', 'розділів > 16 КБ 1'),
             ('файл 90 КБ без маршруту (розділи малі) → ⚠ M4', {'lens/C.md': ''.join(sec(9) for _ in range(10))}, '⚠', '> 80 КБ без маршруту 1'),
             ('файл 90 КБ з «Читається ТОЧКОВО» → ✓', {'lens/C.md': '> Читається ТОЧКОВО\n' + ''.join(sec(9) for _ in range(10))}, '✓', ''),
             ('## з двома ### по 10 КБ → ✓ (точково береться ###)', {'lens/D.md': '## Великий\n' + sec(1) + '### А\n' + 'х' * 5120 + '\n### Б\n' + 'х' * 5120 + '\n'}, '✓', ''),
             ('профіль 18 КБ одним розділом (читається цілком) → ✓, не M3', {'tools/claude-code/PROFILE.md': sec(18)}, '✓', ''),
             ('архів не рахується → ✓', {'archive/X_CHERGA.md': sec(40)}, '✓', ''),
             ('M3: журнал історії (AUDIT) 20 КБ одним розділом → ✓', {'lens/P_AUDIT.md': sec(20)}, '✓', ''),
             ('M3: розділ — блок коду 20 КБ → ✓; той самий обсяг текстом → ⚠', {'lens/M.md': '## Код\n```css\n' + 'a' * 20480 + '\n```\n', 'lens/T.md': sec(20)}, '⚠', 'розділів > 16 КБ 1'),
             ('не-Lens: найновіше самері 30 КБ → ⚠ M2', {'docs/summary/P_SUMMARY_2026-10-01.md': sec(3), 'docs/summary/P_SUMMARY_2026-10-18_s2.md': sec(30)}, '⚠', 'файли старту завеликі 1'),
             ('не-Lens: старе самері 30 КБ, найновіше мале → ✓', {'docs/summary/P_SUMMARY_2026-10-01.md': sec(10) * 3, 'docs/summary/P_SUMMARY_2026-10-18_s2.md': sec(3)}, '✓', ''),
             ('архів ротації journal/ не рахується → ✓', {'tools/claude-code/hooks/journal/HOOK_JOURNAL_2026-10.md': sec(40)}, '✓', ''),
             ('M5: мертвий шлях у живому .md → ⚠', {'README.md': 'див. `tools/gone_v1.py`\n'}, '⚠', 'мертвих шляхів 1'),
             ('M5: хвіст наявного шляху (`data/x.json` = `site/data/x.json`) → ✓', {'site/data/x.json': '{}', 'README.md': 'дані — `data/x.json`\n'}, '✓', ''),
             ('M5: шлях від теки документа → ✓', {'docs/a/b.md': 'поруч — `c/d.md`\n', 'docs/a/c/d.md': 'x'}, '✓', ''),
             ('M5: блок коду, розділ історії, Репо:шлях, гола назва, DECISIONS → ✓', {'README.md': '```\n`tools/x/y.py`\n```\n## Переїзд — старий шлях\n`old/a.md`\n## Далі\n`QR-Lens:tools/q.py` · `gone.py`\n', 'docs/DECISIONS.md': '`tools/dead/z.py`\n'}, '✓', ''),
             ('M6: `AE-X` ✅ у самері, у черзі відкритий → ⚠', {'docs/CHERGA.md': Q, 'docs/summary/P_SUMMARY_2026-10-18.md': '## §0\n- `AE-X` ✅ зроблено\n'}, '⚠', 'черга відстала від самері 1'),
             ('M6: «`AE-X`: підкрок ✅» і закритий у черзі `AE-Y` → ✓', {'docs/CHERGA.md': Q.replace('| `AE-Y` | y | 18.10.2026 | z |', '| `AE-Y` | y | закрито | z |'), 'docs/summary/P_SUMMARY_2026-10-18.md': '## §0\n- `AE-X`: знімок ✅\n- `AE-Y` ✅\n'}, '✓', '')]
    cases += [('M7: «§13-д» без заголовка §13 → ⚠', {'lens/S.md': '## §1 А\nx\n## §2 Б\nx\n## §3 В\nдив. §13-д\n'}, '⚠', 'мертвих адрес § 1'),
              ('M7: «§3-п.2» є заголовок · «gov §12.4» · «Бібліотека §7.1» → ✓', {'lens/S.md': '## §1 А\nx\n## §2 Б\nx\n## §3 В\nдив. §3-п.2 · gov §12.4 · Бібліотека §7.1\n'}, '✓', '')]
    F = 'Кожне правило — **Правило** · **Чому** · **Як перевірити**.\n'
    cases += [('M8: форма оголошена, розділ з правилом без перевірки → ⚠', {'lens/F.md': F + '### 1 А\n**Правило.** x\n**Як перевірити.** y\n### 2 Б\n**Правило.** z\n'}, '⚠', 'правил без «Як перевірити» 1'),
              ('M8: без оголошеної форми · K2:n/a · перевірка є → ✓', {'lens/G.md': '### 1\n**Правило.** x\n', 'lens/F.md': F + '### 1\n**Правило.** x\n<!-- K2:n/a -->\n### 2\n**Правило.** y **Як перевірити:** z\n'}, '✓', '')]
    for name, fs, want, part in cases:
        g, t = line(repo(fs)); ok = g == want and part in t
        print(('✓' if ok else '✗') + ' ' + name + ('' if ok else f' → {t}')); bad += not ok
    print(f'selftest: {len(cases) - bad}/{len(cases)}'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'selftest': sys.exit(selftest())
    root = a[0] if a and not a[0].startswith('--') else '.'
    if '--list' in a:
        for m, f, w in scan(root): print(f'{m} {f} — {w}')
    g, t = line(root); print((g + ' ' if g == '⚠' else '') + t)
