#!/usr/bin/env python3
# живе доки: агент Claude Code читає канон ядра й продуктів. Дім — lens-governance:tools/claude-code/ (бриф DOC-1, «так» Konst 10.10.2026, QR CC-7).
"""Здоров'я документів — скільки коштує їх ЧИТАТИ в Claude Code (не цілісність канону: її тримає гейт kernel/Lens_validate.py).
Мірки (замінили G6 «120 / 200 КБ» Project-епохи, взяті без заміру):
  M1 щосесійне — CLAUDE.md кореня і профіль (tools/claude-code/PROFILE.md) ≤ 200 рядків (code.claude.com/docs/en/memory, 10.10.2026)
     і ≤ 20 000 знаків (AE S134, пропуск Konst: «чому я дізнаюсь лише з аудиту?» — CLAUDE.md AE мав 120 рядків, але 33 тис. знаків: рядок-абзац
     по 1–3 тис. знаків, мірка рядками сліпла; 20 000 ≈ 200 рядків по 100 знаків — число агента, не замір). Стеля документації: файл, що
     вантажиться за потребою (CLAUDE.md репо в підтеці робочої теки — так у хмарній сесії з кількома репо), обрізається понад 40 000 знаків
     у вікні 200K і 150 000 у вікні 1M (code.claude.com/docs/en/memory «Claude ignores the end of my subdirectory CLAUDE.md», 07.11.2026).
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
  M9 прилад без згадки — файл приладу (tools/ · .claude/ · .github/, не .md), чиє ім'я (без розширення) не згадує жоден живий .md.
     Чому (Konst AE S103: «чи знала б наступна сесія про все, що ми зробили?»): M5 ловить документ без файла, а файл без документа —
     ні; новий прилад, не вписаний у карту репо, наступний агент не знайде й збудує вдруге. Перший прогін 24.10: ядро 0, AE 2 справжні.
  M10–M12 кукбук машиною (Konst AE S129: «машина, яка працює на нас»; замір 05.11.2026 — 132 рецепти, без дати джерела 88; черга ядра AUTO-1 (г)).
     Рецепт — розділ «## A<N>.» / «## T<N>.» у файлі *cookbook*.md теки cookbook/; вік рядка — git blame --line-porcelain (час коміту), зведений
     по розділу, не ручне поле (Mintlify «Documentation linting», червень 2026; blame line-porcelain — oneuptime 24.01.2026, звірено 05.11.2026).
  M10 рецепт без дати джерела — лише свіжозмінений (≤ 14 днів); «**Прецедент:** <продукт · batch>» — внутрішнє джерело, дати не треба (Konst AE S129): правиш рецепт — додай «джерело, ДД.ММ.РРРР»; старі 88 разом — шум
     (hve-core documentation-maintenance: на зміні — лише змінені файли, повний прохід — окремо, 05.11.2026).
  M10–M11 — лише рядки з відомим віком: обрізаний клон (shallow) дає граничний коміт на все старше → такі рядки не міряються.
  M11 рецепт не чіпали > 180 днів → «звір зі світом» (платформи міняються; 180 — число агента S129, не замір; hve-core типово 90).
  M12 посилання A<N> / T<N> у томах і індексі кукбука (не в лотку delta_running) на рецепт, якого нема й не названо «зарезерв…» поруч з номером.
  M13 копія між щосесійними файлами — те саме речення (≥ 4 спільні послідовності по 5 слів, тобто ≥ 8 слів поспіль) у двох різних файлах,
     що приходять у кожну сесію: профіль (блок text у tools/claude-code/PROFILE.md) · CLAUDE.md ядра · CLAUDE.md репо · .claude/rules/*.md без
     `paths:`; у ядрі ще й шаблон tools/claude-code/templates/CLAUDE_template.md (з нього народжуються нові CLAUDE.md). Дім — загальніший файл
     (профіль → CLAUDE.md ядра → репо); свідомий виняток — `<!-- copy-ok: причина -->` у тому ж рядку. Плюс: правило з `paths:`, на яке не
     вказує CLAUDE.md репо → ⚠ (вантажиться лише на Read · Write · Edit і `cat` / `head` одного файла, не на Grep — code.claude.com/docs/en/memory,
     12.11.2026; агент, що лише грепає, правила не отримає). Ядра поруч нема (../lens-governance, /tmp/lens-governance, $LENS_KERNEL) → ⓘ, не ✓.
     Чому (Konst AE S142: «дивно, що ми цього раніше не помічали»): Fable FAB-1 10.11 знайшов правило аудиту в 6 місцях і «іншу модель» у 5
     (sessions/FAB-1/FAB-1_frame.md Б1 · Б3 · Б4) — рецепт дав, приладу ні; за 2 дні нічого не внесено, а CLAUDE.md AE переріс 20 тис. знаків.
     Практика — w-shingling (Broder; «Mining of Massive Datasets» гл. 3: шингл 5–9 слів, менший дає хибні збіги — infolab.stanford.edu/~ullman/mmds/ch3.pdf,
     12.11.2026); беремо шингли без minhash / LSH — файлів кілька, пряме порівняння миттєве. Замір 12.11 на ядрі й AE (кожне влучання
     переглянуто): шингл 5 і поріг 4 — 8 справжніх, 0 хибних; поріг 3 — ще 2 справжніх і 2 хибних (усталений зворот «у звіті одразу після «що ти
     побачиш»» — 7 слів; перелік тих самих шляхів-вказівників); порівняння трьох способів на стані «до» (294c7c5): звичайні слова · поріг 4 — 14 справжніх, 0 хибних;
     бектик одним словом · поріг 3 — 3–4 хибних і 4 пропуски; заглушка замість бектика — губить копії, де код щільно в тексті. Перефраз і збіг ≤ 7 слів не ловить.
  M14 копія щосесійного шару (як у M13) у будь-якому документі репо (.md з git ls-files) — ⚠: шар і так приходить щосесії, тут вказівник.
  M15 дослівний дубль між двома документами — ⓘ у рядку (старий борг; дім — назвати одному), перелік — --list. Обидва — без знімків і журналів
     (SNAP: самері, аудит, рішення, черга, журнал гачків, файли з датою в імені, archive/ · sessions/ · site/), без `коду`, шляхів і заголовків
     (вказівник на дім — не копія). Сторож коміту commit_files п. 12 — ✗ на нову копію в доданих рядках. Замір 13.11 (AE S143): ядро — M14 8 · M15 65,
     AE — M14 6 · M15 38; хибні до зрізу шляхів — 12 (усі «`шлях` «розділ»»), після — 0 у вибірці 9 з 14. Konst AE S143: «думав, що він працює на весь репо».
Лише ⚠ (не блокує): один рядок для env_check; адреси — --list.
  python3 doc_health.py [<репо>] [--list] | selftest
"""
import os, re, subprocess, sys, tempfile

M1_LINES, M2_KB, M3_KB, M4_KB = 200, 25, 16, 80
M1_CHARS, M1_CAP = 20000, 40000
M10_DAYS, M11_DAYS = 14, 180


def files(root):
    out = subprocess.run(['git', '-c', 'core.quotePath=false', 'ls-files', '*.md'], cwd=root, capture_output=True, text=True).stdout.split()
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
            elif len(txt) > M1_CHARS: found.append(('M1', f, f'{len(txt)} знаків > {M1_CHARS} ({n} рядків — довгі рядки-абзаци; стеля обрізання {M1_CAP})'))
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
    found += orphan_tools(root)
    found += cookbook(root)
    found += copies(root)
    found += spread(root)
    return found


SH_N, SH_MIN = 5, 4
def _kernel(root):
    none = os.environ.get('LENS_KERNEL') == 'none'   # selftest: детерміновано — лише саме репо
    for k in ((root,) if none else (os.environ.get('LENS_KERNEL', ''), root, os.path.join(root, '..', 'lens-governance'), '/tmp/lens-governance')):
        if k and os.path.isfile(os.path.join(k, 'tools/claude-code/PROFILE.md')): return os.path.realpath(k)
    return None

def _units(path, text_block=False):
    """(номер рядка, рядок) — без блоків коду; профіль — лише вміст блоку ```text."""
    out, code = [], False
    for i, l in enumerate(open(path, encoding='utf-8', errors='replace').read().split('\n'), 1):
        if l.startswith('```'):
            code = not code; continue
        if code == text_block: out.append((i, l))
    return out

def _sh(l):
    w = re.findall(r'\w+', re.sub(r'<!--.*?-->', ' ', l).lower())
    return {' '.join(w[i:i + SH_N]) for i in range(len(w) - SH_N + 1)}

def copies(root):
    """M13: копії між файлами, що приходять у кожну сесію (правила — шапка файла)."""
    k = _kernel(root); found = []
    own = os.path.realpath(root) == k
    src = []   # (ранг дому: менший — загальніший, ім'я, шлях, профіль?)
    if k:
        src += [(0, 'профіль', os.path.join(k, 'tools/claude-code/PROFILE.md'), True), (1, 'CLAUDE.md ядра', os.path.join(k, 'CLAUDE.md'), False)]
        if own: src.append((2, 'шаблон CLAUDE.md', os.path.join(k, 'tools/claude-code/templates/CLAUDE_template.md'), False))
    top_p = os.path.join(root, 'CLAUDE.md'); top = open(top_p, encoding='utf-8').read() if os.path.isfile(top_p) else ''
    if not own and top: src.append((2, 'CLAUDE.md', top_p, False))
    rd = os.path.join(root, '.claude', 'rules')
    for f in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        if not f.endswith('.md'): continue
        t = open(os.path.join(rd, f), encoding='utf-8').read()
        if re.match(r'---\n(?:.*\n)*?paths:', t):
            if f not in top: found.append(('M13', f'.claude/rules/{f}', 'правило з paths: — на нього не вказує CLAUDE.md (вантажиться лише на Read · Edit · cat, не на Grep)'))
        else: src.append((2, f'.claude/rules/{f}', os.path.join(rd, f), False))
    U = [(r, n, [(i, _sh(l)) for i, l in _units(p, prof) if 'copy-ok' not in l]) for r, n, p, prof in src if os.path.isfile(p)]
    for a in range(len(U)):
        for b in range(a + 1, len(U)):
            (ra, na, ua), (rb, nb, ub) = U[a], U[b]
            if not own and rb < 2: continue   # профіль ⟂ CLAUDE.md ядра — справа сесії ядра, не продукту
            for i, sa in ub:
                best = max(((len(sa & sb), j) for j, sb in ua if sa & sb), default=(0, 0))
                if best[0] >= SH_MIN: found.append(('M13', f'{nb}:{i}', f'копія {na}:{best[1]} ({best[0]} збігів по {SH_N} слів) — дім: {na}, тут — вказівник'))
    if not k: found.append(('ⓘ', '', 'ядра поруч нема — копії з профілем і CLAUDE.md ядра не міряно'))
    return found

# M14 · M15 (AE S143, Konst: «думав, що він працює на весь репозиторій — і на продукт, і на ядро»): M13 бачив лише щосесійні файли, а копії профілю
# в REPO_FRAME.md і CLAUDE_CODE.md знайшов лише аудит за $25. Тепер — кожен документ репо (.md з git ls-files), крім знімків і журналів, де цитата — норма.
# Практика: mdsmith MDS037 (pkg.go.dev/github.com/jeduden/mdsmith, 04.2026; звірено 13.11.2026) — ті самі 5-слівні шматки з нормалізацією; MinHash / LSH не беремо
# (корпус малий, прохід 0,2 с), поріг «80 % абзацу» — теж ні: шукаємо дослівний фрагмент ≥ 8 слів усередині різних рядків, не абзац-двійник.
SNAP = re.compile(r'(^|/)(archive|sessions|node_modules|\.audit_tmp|site|docs/(summary|audit|fab|e2e)|hooks/journal)/'   # історія · звіти · дані Олі
                  r'|(AUDIT|DECISIONS|CHERGA|HOOK_JOURNAL|_HISTORY|_INDEX|_delta_running)[^/]*\.md$|SUMMARY|summary'
                  r'|20\d\d-\d\d-\d\d|(^|/)review_v\d+\.md$')   # дата в імені — знімок дня, не правило; review_vN — нотатки огляду примірки
def _docs(root):
    out = subprocess.run(['git', '-c', 'core.quotePath=false', 'ls-files', '--', '*.md'], cwd=root, capture_output=True, text=True).stdout.split('\n')
    return [f for f in out if f and not SNAP.search(f)]

def _layers(root):
    """Щосесійні шари (як у M13): профіль · CLAUDE.md ядра · CLAUDE.md репо · .claude/rules без paths:. (ім'я, шлях, профіль?)"""
    k = _kernel(root); own = k and os.path.realpath(root) == k; L = []
    if k: L += [('профіль', os.path.join(k, 'tools/claude-code/PROFILE.md'), True), ('CLAUDE.md ядра', os.path.join(k, 'CLAUDE.md'), False)]
    if not own and os.path.isfile(os.path.join(root, 'CLAUDE.md')): L.append(('CLAUDE.md', os.path.join(root, 'CLAUDE.md'), False))
    rd = os.path.join(root, '.claude', 'rules')
    for f in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        p = os.path.join(rd, f)
        if f.endswith('.md') and not re.match(r'---\n(?:.*\n)*?paths:', open(p, encoding='utf-8').read()): L.append((f'.claude/rules/{f}', p, False))
    return [x for x in L if os.path.isfile(x[1])]

def _shp(l):
    """Шматки для M14 · M15: без `коду в бектиках`, шляхів і заголовків — посилання на дім і є бажаний вказівник, не копія (калібрування AE S143:
    «`tools/claude-code/templates/AUDIT_template.md` «Коли і скільки»» у 4 файлах давало хибне M14)."""
    if l.lstrip().startswith('#'): return set()
    return _sh(re.sub(r'`[^`]*`|\S*[\w-]/\S*|\S+\.(md|py|sh|mjs|js|json|html)\b', ' ', l))

def spread(root, only=None, old=None):
    """M14 — копія щосесійного шару в будь-якому документі репо (⚠: шар і так у контексті щосесії — тут вказівник).
    M15 — дослівний дубль між двома документами (ⓘ у рядку старту, перелік — --list: старий борг, дім — назвати одному з двох).
    only = {файл: {номери рядків}} — лише ці рядки (сторож коміту: додані рядки диффу); old = {файл: шматки файла на HEAD} — рахуються лише
    шматки, яких у файлі ще не було (правка старого рядка зі старим дублем — не нова копія; хибне AE S143 на власному коміті)."""
    import collections
    lay = _layers(root); lp = {os.path.realpath(p) for _, p, _ in lay}
    idx = collections.defaultdict(set)
    for n, p, prof in lay:
        for i, l in _units(p, prof):
            if 'copy-ok' not in l:
                for s in _shp(l): idx[s].add((n, i))
    docs = [f for f in _docs(root) if os.path.realpath(os.path.join(root, f)) not in lp]
    U = {f: [(i, _shp(l)) for i, l in _units(os.path.join(root, f)) if 'copy-ok' not in l] for f in docs if os.path.isfile(os.path.join(root, f))}
    di = collections.defaultdict(set)
    for f, us in U.items():
        for i, sh in us:
            for s in sh: di[s].add((f, i))
    found = []
    for f, us in U.items():
        if only is not None and f not in only: continue
        for i, sh in us:
            if only is not None and i not in only[f]: continue
            if old and f in old: sh = sh - old[f]
            c = collections.Counter(h for s in sh for h in idx.get(s, ()))
            if c and c.most_common(1)[0][1] >= SH_MIN:
                (n, j), m = c.most_common(1)[0]
                found.append(('M14', f'{f}:{i}', f'копія {n}:{j} ({m} збігів по {SH_N} слів) — шар і так приходить щосесії: тут вказівник або <!-- copy-ok: причина -->')); continue
            d = collections.Counter(h for s in sh if len(di[s]) <= 30 for h in di[s] if h[0] != f)   # > 30 місць — шаблонна фраза, не копія правила
            if d and d.most_common(1)[0][1] >= SH_MIN:
                (g, j), m = d.most_common(1)[0]
                if only is not None or (f, i) < (g, j): found.append(('M15', f'{f}:{i}', f'дубль {g}:{j} ({m} збігів по {SH_N} слів) — одне правило, один дім: другому — вказівник'))
    return found

REC = re.compile(r'(?m)^## ([AT]\d+)\.')
PREC = re.compile(r'\*\*Прецедент')   # внутрішнє джерело — наш випадок (продукт · batch / сесія), не зовнішня сторінка: дата не обов'язкова (Konst AE S129, варіант Б — A45)
DATED = re.compile(r'\b\d{2}\.\d{2}\.20\d{2}\b|\b20\d{2}-\d{2}-\d{2}\b')
def cookbook(root, now=None):
    """M10–M12: рецепти кукбука — свіжість (git blame) і посилання між рецептами."""
    import time
    now = now or time.time(); out = []
    cb = [f for f in files(root) if '/cookbook/' in '/' + f and 'cookbook' in os.path.basename(f).lower()]
    recs, reserved, refs = set(), set(), []
    sp = subprocess.run(['git', 'rev-parse', '--git-path', 'shallow'], cwd=root, capture_output=True, text=True).stdout.strip()
    sp = sp if os.path.isabs(sp) else os.path.join(root, sp)
    shallow = set(open(sp).read().split()) if sp and os.path.isfile(sp) else set()   # граничні коміти обрізаного клону (AE S129: 52 коміти) — вік рядка з них невідомий
    for f in cb:
        txt = open(os.path.join(root, f), encoding='utf-8', errors='replace').read(); lines = txt.split('\n')
        for m in re.finditer(r'\b([AT]\d+)\b\**\s*[—–-]\s*зарезерв', txt): reserved.add(m[1])
        if re.search(r'cookbook_(\d|INDEX)', f):   # тома й індекс; лоток delta_running тримає кандидатів і старі номери свідомо
            for i, l in enumerate(lines): refs += [(f, i + 1, r) for r in re.findall(r'\b([AT]\d{1,3})\b', l)]
        heads = [(i, m[1]) for i, l in enumerate(lines) for m in [REC.match(l)] if m]
        if not heads: continue
        recs.update(k for _, k in heads)
        bl = subprocess.run(['git', 'blame', '--root', '--line-porcelain', '--', f], cwd=root, capture_output=True, text=True).stdout
        ts, cur = [], {}
        for l in bl.split('\n'):   # блок рядка: шапка «<sha> …» · поля (committer-time) · «\t<текст>»
            if l.startswith('\t'): ts.append(None if cur.get('s') in shallow else cur.get('t')); cur = {}
            elif re.match(r'^[0-9a-f]{40} ', l): cur['s'] = l[:40]
            elif l.startswith('committer-time '): cur['t'] = int(l.split()[1])
        if len(ts) < len(lines) - 1: continue   # файл не в історії (новий, не закомічений) — свіжість не міряємо
        ends = [i for i, l in enumerate(lines) if re.match(r'^#{1,2} ', l)] + [len(lines)]
        for i, k in heads:
            j = min(e for e in ends if e > i); body = '\n'.join(lines[i:j]); known = [t for t in ts[i:j] if t]
            if not known: continue   # увесь рецепт — з граничного коміту: вік невідомий, не міряємо (хибне M10/M11 гірше за мовчання)
            age = (now - max(known)) / 86400
            if age > M11_DAYS: out.append(('M11', f, f'{k} не чіпали {age:.0f} дн. — звір зі світом (джерела, платформа)'))
            elif age <= M10_DAYS and not DATED.search(body) and not PREC.search(body): out.append(('M10', f, f'{k} змінено {age:.0f} дн. тому, а дати джерела нема — «джерело, ДД.ММ.РРРР»'))
    for f, n, r in refs:
        if r not in recs and r not in reserved and recs: out.append(('M12', f, f'рядок {n}: {r} — такого рецепта нема'))
    return out


def orphan_tools(root):
    """M9: прилад (tools/ · .claude/ · .github/), про який не каже жоден живий .md — ім'я без розширення."""
    ls = subprocess.run(['git', '-c', 'core.quotePath=false', 'ls-files', 'tools', '.claude', '.github'], cwd=root, capture_output=True, text=True).stdout.split('\n')
    tl = [f for f in ls if f and not f.endswith('.md') and '__pycache__' not in f and '/journal/' not in f and not f.startswith('archive/')]
    if not tl: return []
    text = '\n'.join(open(os.path.join(root, f), encoding='utf-8', errors='replace').read() for f in files(root) if os.path.isfile(os.path.join(root, f)))
    return [('M9', f, 'про прилад не каже жоден живий документ — рядок у карту репо (REPO_LAYOUT / CLAUDE_CODE.md), або в archive/')
            for f in tl if os.path.splitext(os.path.basename(f))[0] not in text]


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
    known = [k for k in subprocess.run(['git', '-c', 'core.quotePath=false', 'ls-files'], cwd=root, capture_output=True, text=True).stdout.split('\n') if k]
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
    sh = subprocess.run(['git', 'rev-parse', '--is-shallow-repository'], cwd=root, capture_output=True, text=True).stdout.strip() == 'true'
    note = ' · ⓘ свіжість рецептів не міряна — клон обрізаний (git fetch --unshallow)' if sh and any('/cookbook/' in '/' + x for x in files(root)) else ''
    note += ''.join(' · ⓘ ' + x[2] for x in f if x[0] == 'ⓘ' and x[2])
    m15 = sum(x[0] == 'M15' for x in f)
    if m15: note += f' · ⓘ дублів між документами {m15} (M15 — doc_health.py --list)'
    f = [x for x in f if x[0] not in ('ⓘ', 'M15')]
    if not f: return '✓', f'документи: ✓ щосесійні ≤ {M1_LINES} рядків і {M1_CHARS} знаків · старт ≤ {M2_KB} КБ · розділи ≤ {M3_KB} КБ · великі з маршрутом · копій нема' + note
    by = {}
    for m, *_ in f: by[m] = by.get(m, 0) + 1
    name = {'M1': 'щосесійні задовгі', 'M2': 'файли старту завеликі', 'M3': f'розділів > {M3_KB} КБ', 'M4': f'> {M4_KB} КБ без маршруту', 'M5': 'мертвих шляхів', 'M9': 'приладів без згадки', 'M6': 'черга відстала від самері', 'M7': 'мертвих адрес §', 'M8': 'правил без «Як перевірити»', 'M10': 'свіжих рецептів без дати джерела', 'M11': f'рецептів > {M11_DAYS} дн. без звірки', 'M13': 'копій між щосесійними', 'M14': 'копій щосесійного шару в документах', 'M12': 'посилань на неіснуючий рецепт'}
    worst = max((x for x in f if x[0] == 'M3'), key=lambda x: float(re.search(r'(\d+) КБ', x[2])[1]), default=None)
    return '⚠', 'документи: ' + ' · '.join(f'{name[m]} {n}' for m, n in sorted(by.items())) + (f' (найбільший — {worst[1]} {worst[2]})' if worst else '') + ' — деталі: doc_health.py --list' + note


def selftest():
    bad = 0; ENV = {}; os.environ['LENS_KERNEL'] = 'none'
    def repo(fs):
        d = tempfile.mkdtemp(prefix='dh-'); subprocess.run(['git', 'init', '-q'], cwd=d, check=True)
        for f, t in fs.items():
            os.makedirs(os.path.dirname(os.path.join(d, f)) or d, exist_ok=True); open(os.path.join(d, f), 'w').write(t)
        subprocess.run(['git', 'add', '-A'], cwd=d, check=True)
        subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 't', '--allow-empty'], cwd=d, check=True, env=dict(os.environ, **ENV)); return d
    sec = lambda kb: '## Розділ\n' + 'х' * (kb * 512) + '\n'   # кирилиця — 2 байти на знак
    Q = '## Відкрите\n| id | предмет | відкрито | умова |\n|---|---|---|---|\n| `AE-X` | x | 18.10.2026 | y |\n| `AE-Y` | y | 18.10.2026 | z |\n\n-----\n'
    cases = [('чисте репо → ✓', {'CLAUDE.md': 'x\n' * 50, 'lens/A.md': sec(4)}, '✓', ''),
             ('CLAUDE.md 250 рядків → ⚠ M1', {'CLAUDE.md': 'x\n' * 250}, '⚠', 'щосесійні задовгі 1'),
             ('CLAUDE.md 120 рядків по 300 знаків (36 тис.) → ⚠ M1 (AE S134: мірка рядками сліпла)', {'CLAUDE.md': ('ж' * 299 + '\n') * 120}, '⚠', 'щосесійні задовгі 1'),
             ('CLAUDE.md 120 рядків по 100 знаків → ✓', {'CLAUDE.md': ('ж' * 99 + '\n') * 120}, '✓', ''),
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
             ('M5: кириличний шлях (git бере його в лапки без core.quotePath=false) → ✓ — пропуск AE S99', {'ДЛЯ_ОЛІ/HANDOFF_для_Claude.md': 'x', 'README.md': 'див. `ДЛЯ_ОЛІ/HANDOFF_для_Claude.md`\n'}, '✓', ''),
             ('M5: шлях від теки документа → ✓', {'docs/a/b.md': 'поруч — `c/d.md`\n', 'docs/a/c/d.md': 'x'}, '✓', ''),
             ('M5: блок коду, розділ історії, Репо:шлях, гола назва, DECISIONS → ✓', {'README.md': '```\n`tools/x/y.py`\n```\n## Переїзд — старий шлях\n`old/a.md`\n## Далі\n`QR-Lens:tools/q.py` · `gone.py`\n', 'docs/DECISIONS.md': '`tools/dead/z.py`\n'}, '✓', ''),
             ('M6: `AE-X` ✅ у самері, у черзі відкритий → ⚠', {'docs/CHERGA.md': Q, 'docs/summary/P_SUMMARY_2026-10-18.md': '## §0\n- `AE-X` ✅ зроблено\n'}, '⚠', 'черга відстала від самері 1'),
             ('M6: «`AE-X`: підкрок ✅» і закритий у черзі `AE-Y` → ✓', {'docs/CHERGA.md': Q.replace('| `AE-Y` | y | 18.10.2026 | z |', '| `AE-Y` | y | закрито | z |'), 'docs/summary/P_SUMMARY_2026-10-18.md': '## §0\n- `AE-X`: знімок ✅\n- `AE-Y` ✅\n'}, '✓', '')]
    cases += [('M7: «§13-д» без заголовка §13 → ⚠', {'lens/S.md': '## §1 А\nx\n## §2 Б\nx\n## §3 В\nдив. §13-д\n'}, '⚠', 'мертвих адрес § 1'),
              ('M7: «§3-п.2» є заголовок · «gov §12.4» · «Бібліотека §7.1» → ✓', {'lens/S.md': '## §1 А\nx\n## §2 Б\nx\n## §3 В\nдив. §3-п.2 · gov §12.4 · Бібліотека §7.1\n'}, '✓', '')]
    cases += [('M9: прилад, про який не каже жоден .md → ⚠', {'tools/gone_v1.py': 'x', 'README.md': 'нічого\n'}, '⚠', 'приладів без згадки 1'),
              ('M9: прилад згаданий іменем без розширення → ✓', {'tools/stand/walk_v2.py': 'x', 'docs/REPO_LAYOUT.md': 'прохід walk_v2 — чинний\n'}, '✓', '')]
    F = 'Кожне правило — **Правило** · **Чому** · **Як перевірити**.\n'
    cases += [('M8: форма оголошена, розділ з правилом без перевірки → ⚠', {'lens/F.md': F + '### 1 А\n**Правило.** x\n**Як перевірити.** y\n### 2 Б\n**Правило.** z\n'}, '⚠', 'правил без «Як перевірити» 1'),
              ('M8: без оголошеної форми · K2:n/a · перевірка є → ✓', {'lens/G.md': '### 1\n**Правило.** x\n', 'lens/F.md': F + '### 1\n**Правило.** x\n<!-- K2:n/a -->\n### 2\n**Правило.** y **Як перевірити:** z\n'}, '✓', '')]
    C = 'kernel/cookbook/X_cookbook_1.md'
    cases += [('M10: свіжий рецепт без дати джерела → ⚠', {C: '# Том\n## A1. Кнопка\nтекст без дати\n## A2. Поле\nджерело web.dev, 05.11.2026\n'}, '⚠', 'свіжих рецептів без дати джерела 1'),
              ('M10–M12: дати є · посилання живе · A9 зарезервовано → ✓', {C: '# Том\n## A1. Кнопка\nпара — A2; A9 — зарезервований номер\n(2026-11-05)\n## A2. Поле\nweb.dev, 05.11.2026\n'}, '✓', ''),
              ('M10: рецепт з «**Прецедент:**» (наш випадок) без дати → ✓ (Konst S129, варіант Б)', {C: '# Том\n## A1. Кнопка\nтекст\n**Прецедент:** Drive Lens Batch 26.\n'}, '✓', ''),
              ('M12: посилання на рецепт, якого нема → ⚠', {C: '# Том\n## A1. Кнопка\nдив. A77 · 05.11.2026\n'}, '⚠', 'посилань на неіснуючий рецепт 1')]
    S = 'перед будь-якою правкою покажи план мікроскоп і дочекайся слова так від konst'
    PR = {'tools/claude-code/PROFILE.md': '# Профіль\n```text\n· ' + S + '\n```\n'}
    R = '---\npaths:\n  - "site/**"\n---\nправило\n'
    cases += [('M13: речення профілю дослівно в CLAUDE.md ядра → ⚠', dict(PR, **{'CLAUDE.md': '- ' + S.capitalize() + '.\n'}), '⚠', 'копій між щосесійними 1'),
              ('M13: те саме правило іншими словами → ✓', dict(PR, **{'CLAUDE.md': '- план і мікроскоп показати до правки; чекати згоди konst\n'}), '✓', ''),
              ('M13: дослівно, але з <!-- copy-ok: причина --> → ✓', dict(PR, **{'CLAUDE.md': '- ' + S + ' <!-- copy-ok: тест -->\n'}), '✓', ''),
              ('M13: правило з paths:, на яке не вказує CLAUDE.md → ⚠', {'CLAUDE.md': 'x\n', '.claude/rules/ui.md': R}, '⚠', 'копій між щосесійними 1'),
              ('M13: правило з paths: і вказівник у CLAUDE.md → ✓', {'CLAUDE.md': 'UI — `.claude/rules/ui.md`\n', '.claude/rules/ui.md': R}, '✓', ''),
              ('M13: спільний зворот 7 слів у різних правилах → ✓', dict(PR, **{'CLAUDE.md': '- тривога cloudflare у звіті одразу після «що ти побачиш» першою\n', 'tools/claude-code/PROFILE.md': '```text\n· рядки frame_check у звіті одразу після «що ти побачиш» з пропозицією\n```\n'}), '✓', ''),
              ('M13: ядра нема → ⓘ, не мовчазне ✓', {'CLAUDE.md': 'x\n'}, '✓', 'ⓘ ядра поруч нема')]
    cases += [('M14: речення профілю дослівно в документі репо (не щосесійному) → ⚠', dict(PR, **{'tools/G.md': '- ' + S + '\n'}), '⚠', 'копій щосесійного шару в документах 1'),
              ('M14: те саме в знімку (самері, журнал, файл з датою) → ✓', dict(PR, **{'docs/summary/P_SUMMARY_2026-11-13.md': '- ' + S + '\n', 'docs/AUDIT.md': S + '\n', 'docs/e/R_2026-11-13.md': S + '\n'}), '✓', ''),
              ('M14: лише вказівник-шлях на дім (`tools/claude-code/PROFILE.md` «ЦИКЛ») → ✓', dict(PR, **{'tools/G.md': '- цикл — `tools/claude-code/PROFILE.md` «ЦИКЛ ПЛАНУВАННЯ», тут не повторюємо\n'}), '✓', ''),
              ('M14: дослівно з <!-- copy-ok: причина --> → ✓', dict(PR, **{'tools/G.md': '- ' + S + ' <!-- copy-ok: повна версія -->\n'}), '✓', ''),
              ('M15: те саме речення у двох документах → ⓘ (не ⚠: старий борг)', {'tools/A.md': '- кожен крок звіряти з журналом рішень і писати причину в коміт\n', 'tools/B.md': 'кожен крок звіряти з журналом рішень і писати причину в коміт\n'}, '✓', 'ⓘ дублів між документами 1')]
    for name, fs, want, part in cases:
        g, t = line(repo(fs)); ok = g == want and part in t
        print(('✓' if ok else '✗') + ' ' + name + ('' if ok else f' → {t}')); bad += not ok
    ENV.update(GIT_AUTHOR_DATE='2025-01-01T00:00:00', GIT_COMMITTER_DATE='2025-01-01T00:00:00')
    g, t = line(repo({'kernel/cookbook/X_cookbook_1.md': '# Том\n## A1. Кнопка\nweb.dev, 01.01.2025\n'})); ENV.clear(); ok = g == '⚠' and 'рецептів > 180 дн. без звірки 1' in t
    print(('✓' if ok else '✗') + ' M11: рецепт не чіпали > 180 днів → ⚠' + ('' if ok else f' → {t}')); bad += not ok; cases.append(None)
    src = repo({'kernel/cookbook/X_cookbook_1.md': '# Том\n## A1. Кнопка\nбез дати\n'}); open(os.path.join(src, 'n.txt'), 'w').write('x')
    subprocess.run(['git', 'add', '-A'], cwd=src); subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 't2'], cwd=src)
    d = tempfile.mkdtemp(prefix='dh-'); subprocess.run(['git', 'clone', '-q', '--depth', '1', 'file://' + src, d], check=True)
    g, t = line(d); ok = 'свіжих рецептів' not in t and 'ⓘ свіжість рецептів не міряна' in t
    print(('✓' if ok else '✗') + ' M10: обрізаний клон — рецепт з граничного коміту не міряється' + ('' if ok else f' → {t}')); bad += not ok; cases.append(None)
    print(f'selftest: {len(cases) - bad}/{len(cases)}'); return 1 if bad else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'selftest': sys.exit(selftest())
    root = a[0] if a and not a[0].startswith('--') else '.'
    if '--list' in a:
        for m, f, w in scan(root): print(f'{m} {f} — {w}')
    g, t = line(root); print((g + ' ' if g == '⚠' else '') + t)
