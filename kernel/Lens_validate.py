#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lens_validate.py — єдиний гейт-скрипт сімейства Lens.
живе доки: назавжди (вічне, wsd 1.8)
KERNEL v2 · 31.07.2026

ДВА РЕЖИМИ:

  python3 Lens_validate.py --gov [тека]
      Перевірка governance-шару. Дешева, без залежностей.
      G1 «живе доки» у шапці кожного .md
      G2 збіг штампів KERNEL між файлами ядра
      G3 покриття індексом: кожен .md названий у Lens_INDEX.md
      G4 посилання 14.x з wsd резолвляться у Work_Standard_HISTORY.md
      G5 вік буферів: непорожній *_delta_running.md → нагадування про стелю 2-3 сесії
      G6 стеля обсягу: >120KB сигнал, >200KB червона межа
      G7 мертвий буфер: «Куди канонити/мерджити» вказує на неіснуючий файл
         АБО цільовий A-запис уже стоїть у томі Cookbook
      G8 сирота-посилання: `Ім'я.md` у канон-файлі, а файлу в теці немає
      G9 дубль A-номера між томами Cookbook
      G10 перепис самері: >2 на продукт → друкує список найстаріших на архів
      G11 цілісність буфера: (a) оголошене «ЛОТОК: N» ≠ фактичне число записів
         (b) дубль номера запису → слід колізії паралельних сесій (14.29)
      G12 файл-міст: оголошена структура тек ⟂ фактичне дерево archive/
      G13 нумерація секцій усередині файлу: (a) дубль §N → ✗
         (b) діра в послідовності → ⚠ (c) секції не по зростанню → ⚠
         Для дубля додатково називає, ХТО на нього посилається ззовні
      G16 правило без детектора (К2) і без маркера K2:n/a
      G19 спрацювання правил: правило з нулем згадок у самері й без сліду
         народження — кандидат на виселення (К4-1). Живі самері лежать у
         Project, не в репо — тому тека з ними додається: --gov . --live <тека>
      G21 номер правила з тілом визначений рівно в одному файлі RULE_FILES → інакше ✗
         (розпил wsd, IDX-7: перенос без вирізання дає дубль, якого не бачить ніхто)
         Маршрутна заглушка (G16 · G21) — за структурою, не за словом (Ф-25): тіло до h1 —
         лише цитати, одна з них `> **ROUTING →`. Заглушка ≥ 400 B → ⚠ «виключено як маршрут»
      G23 канон-файл kernel/**/*.md без тригера читання в шапці (перші 12 рядків:
         «читається…» або «AUTO-READ») → ✗ на файл (К6-1: файл вмикається механізмом, не пам'яттю)

  python3 Lens_validate.py --html <file.html>
      Перед-видачні гейти білда (wsd Кластер 3 / 10).
      H1 node --check по кожному inline <script> без src
      H2 баланс тегів div/span/button/a/svg/style/script
      H3 A69 dark-твін-паритет: кожне [data-theme="dark"] правило має
         близнюк у @media(prefers-color-scheme:dark)
      H4 порожні класи-гачки та голі імена без префікса (звіт, не помилка)

Код повернення: 0 — усе зелене; 1 — є ✗.

ПРИНЦИП (wsd К2): детектор мусить бути ПРАВИЛЬНИМ. Хибний ✗ шкідливіший за
відсутній детектор. Тому все, що не можна довести регексом однозначно,
рапортується як «⚠ подивись», а не «✗».
"""

import sys, os, re, glob, subprocess, tempfile

KERNEL_FILES = [
    'Lens_INDEX.md', 'Lens_PROFILE.md', 'Work_Standard.md',
    'Lens_governance_protocol.md', 'Lens_verdict_protocol.md', 'Lens_patch_check_protocol.md',
    'Work_Standard_HISTORY.md', 'Lens_NEWPROJECT_bootstrap.md',
    'Lens_cookbook_INDEX.md',
    'Lens_iOS_cookbook_1_platform.md', 'Lens_iOS_cookbook_2_navigation.md',
    'Lens_iOS_cookbook_3_material.md', 'Lens_iOS_cookbook_4_components.md',
    'Lens_iOS_cookbook_5_motion.md', 'Lens_ARCHIVE_INDEX.md',
]
SIGNAL_KB, RED_KB = 120, 200
LIVE_DIRS = []          # теки живих самері (Project) для G19 — --live
# Файли правил — ОГОЛОШЕННЯ, не здогад (wsd 1.10). Новий дім правил = рядок тут
# + рядок у Lens_INDEX. Читають G4 · G16 · G19 · G21. Мітка — у виводі G19/G21.
RULE_FILES = {'Work_Standard.md': 'wsd', 'Lens_governance_protocol.md': 'gov', 'Lens_PROFILE.md': 'prof', 'Lens_verdict_protocol.md': 'verd', 'Lens_patch_check_protocol.md': 'chk'}


def route_body(part):
    """Фрагмент номера без хвоста файлу: зріз на першому h1 (`# …`) — інакше останнє правило
    файлу тягне за собою розділ «# Історія…» і заглушка виглядає тілом (wsd 12.19, G-Q)."""
    return re.split(r'\n(?=# )', part)[0]


def is_route(part):
    """Ф-25: маршрутна заглушка — структурно. Після заголовка кожен непорожній рядок
    (крім `-----`) — цитата, і хоч одна — `> **ROUTING →`. Слово ROUTING у тілі правила
    (заголовок gov 12.11, приклад у тексті) заглушкою його НЕ робить."""
    ls = [l for l in route_body(part).splitlines()[1:] if l.strip() and not re.fullmatch(r'-{3,}', l.strip())]
    return bool(ls) and all(l.startswith('>') for l in ls) and any(re.match(r'>\s*\*\*ROUTING\s*→', l) for l in ls)

ok_n = warn_n = fail_n = 0


def ok(m):
    global ok_n; ok_n += 1; print(f'  ✓ {m}')


def warn(m):
    global warn_n; warn_n += 1; print(f'  ⚠ {m}')


def fail(m):
    global fail_n; fail_n += 1; print(f'  ✗ {m}')


# ─────────────────────────────── GOVERNANCE ───────────────────────────────

_FMAP = {}


def R(root, name):
    """Шлях за базовим іменем. Пласка тека і тека з підтеками — однаково."""
    return _FMAP.get(name, os.path.join(root, name))


def _dup_scan(root):
    seen = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in ('.git', 'node_modules', '__pycache__')]
        for fn in fns:
            if fn.endswith(('.md', '.py', '.js')):
                seen.setdefault(fn, []).append(os.path.relpath(dp, root))
    return {n: ps for n, ps in seen.items() if len(ps) > 1}


def gov(root):
    print(f'\n=== GOVERNANCE-ГЕЙТИ · {os.path.abspath(root)} ===')
    # Рекурсивний обхід (сесія F). Репо має підтеки kernel/wsd · kernel/cookbook ·
    # kernel/modules, Project після Sync — пласка тека. Гейти мусять давати ОДНАКОВИЙ
    # результат на обох, інакше «зелено в Project / червоно в репо» стає нормою.
    # Ключ усюди — БАЗОВЕ ІМ'Я: канон-посилання пишуться іменем, не шляхом.
    global _FMAP
    _FMAP = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in ('.git', 'node_modules', '__pycache__')]
        for fn in fns:
            _FMAP.setdefault(fn, os.path.join(dp, fn))
    for n, ps in _dup_scan(root).items():
        fail(f'`{n}` лежить у {len(ps)} теках ({", ".join(ps)}) — '
             f'посилання за іменем стає неоднозначним')
    mds = sorted(n for n in _FMAP if n.endswith('.md'))
    if not mds:
        fail('жодного .md не знайдено — не та тека?'); return

    # G1 — «живе доки» у перших 5 рядках
    print('\n[G1] рядок «живе доки» у шапці')
    bad = []
    for f in mds:
        head = open(R(root, f), encoding='utf-8').read().split('\n')[:5]
        if not any('живе доки' in l for l in head):
            bad.append(f)
    if bad:
        for f in bad:
            fail(f'{f} — немає «живе доки» у перших 5 рядках (wsd 1.8)')
    else:
        ok(f'усі {len(mds)} .md мають «живе доки»')

    # G2 — штампи KERNEL
    print('\n[G2] збіг штампів KERNEL')
    stamps = {}
    for f in KERNEL_FILES:
        p = R(root, f)
        if not os.path.exists(p):
            warn(f'{f} — файла немає в цій теці (ядро неповне або ще не розпиляне)')
            continue
        head = open(p, encoding='utf-8').read().split('\n')[:6]
        m = next((re.search(r'KERNEL\s+(v\d+)', l) for l in head if 'KERNEL' in l), None)
        if m:
            stamps[f] = m.group(1)
        else:
            fail(f'{f} — немає штампа KERNEL vN у шапці')
    if stamps:
        vals = set(stamps.values())
        if len(vals) == 1:
            ok(f'усі файли ядра — {vals.pop()} ({len(stamps)} шт.)')
        else:
            fail(f'ЯДРО РОЗІЙШЛОСЬ: {stamps}')

    # G3 — покриття індексом
    print('\n[G3] покриття Lens_INDEX.md')
    idxp = R(root, 'Lens_INDEX.md')
    if not os.path.exists(idxp):
        fail('Lens_INDEX.md відсутній — маршрутизатора немає (wsd 1.1)')
    else:
        idx = open(idxp, encoding='utf-8').read()
        miss = [f for f in mds if f not in idx and f != 'Lens_INDEX.md']
        summaries = [f for f in miss if 'session_summary' in f]
        rest = [f for f in miss if 'session_summary' not in f]
        if rest:
            for f in rest:
                fail(f'{f} — не названий в індексі (wsd 1.1, детектор К2)')
        else:
            ok('усі не-самері файли названі в індексі')
        if summaries:
            warn(f'самері поза індексом: {len(summaries)} шт. — очікувано, '
                 f'якщо їх ≤2 на продукт (wsd 1.8); зараз перевір вручну')

    # G4 — 14.x резолвляться (з G-J — з УСІХ файлів правил, не лише wsd)
    print('\n[G4] посилання 14.x з файлів правил → HISTORY')
    h = R(root, 'Work_Standard_HISTORY.md')
    srcs = [R(root, f) for f in RULE_FILES if os.path.exists(R(root, f))]
    if srcs and os.path.exists(h):
        refs = sorted(set(r for p in srcs for r in
                          re.findall(r'\b14\.\d+\b', open(p, encoding='utf-8').read())))
        ht = open(h, encoding='utf-8').read()
        dead = [r for r in refs if f'## {r} ' not in ht]
        if dead:
            fail(f'висячі посилання: {", ".join(dead)}')
        else:
            ok(f'усі {len(refs)} посилань резолвляться')
    else:
        warn('файли правил або HISTORY відсутні — гейт пропущено')

    # G5 — буфери
    print('\n[G5] буфери')
    for f in [x for x in mds if x.endswith('_delta_running.md')]:
        body = open(R(root, f), encoding='utf-8').read()
        # Службові заголовки («## ✅ Спорожнено…», «## 🟡 Відкриті кандидати»)
        # НЕ є записами. Без цього фільтра G5 роздував число і розходився з G11,
        # який рахує ті самі буфери правильно (сесія E: G5 казав 5, G11 — 3).
        entries = len([h for h in re.findall(r'^## (.+)$', body, re.M)
                       if not re.match(r'[✅🟡🔴⬜🗄]|Спорожнено|Відкриті|ЗАКРИТО', h.strip())])
        if entries:
            warn(f'{f} — {entries} запис(ів); стеля 2–3 сесії, далі мерджити як є')
        else:
            ok(f'{f} — порожній')

    # G6 — обсяг
    print('\n[G6] обсяг файлів')
    big = False
    for f in mds:
        kb = os.path.getsize(R(root, f)) / 1024
        if kb > RED_KB:
            fail(f'{f} — {kb:.0f} KB > {RED_KB} KB червона межа: різати на томи'); big = True
        elif kb > SIGNAL_KB:
            warn(f'{f} — {kb:.0f} KB > {SIGNAL_KB} KB сигнал: планувати розпил'); big = True
    if not big:
        ok(f'усі файли ≤ {SIGNAL_KB} KB')

    # ── G7 — мертвий буфер ────────────────────────────────────────────────
    # Тригер: файл несе рядок «Куди канонити» / «Куди мерджити».
    # Самері виключені: там це переказ чужого маршруту, не власна ціль (Д-1).
    print('\n[G7] мертвий буфер — ціль уже закрита')
    vols = {f: open(R(root, f), encoding='utf-8').read()
            for f in mds if re.match(r'Lens_iOS_cookbook_\d', f)}
    g7 = False
    for f in mds:
        # Самері й донор-модулі виключені: там «Куди канонити» — переказ чужого
        # маршруту або точка під'єднання, не власна ціль буфера (Д-1 · сесія E).
        if 'session_summary' in f or f.startswith('Lens_module_'):
            continue
        body = open(R(root, f), encoding='utf-8').read()
        lines = [l for l in body.splitlines() if re.search(r'Куди (канонити|мерджити)', l)]
        # секційний заголовок «## Куди канонити» → брати абзац під ним
        if re.search(r'^#+\s*Куди (канонити|мерджити)', body, re.M):
            for m in re.finditer(r'^#+\s*Куди (?:канонити|мерджити).*?$(.*?)(?=^#|\Z)',
                                 body, re.M | re.S):
                lines += m.group(1).splitlines()
        if not lines:
            continue
        head = '\n'.join(body.splitlines()[:12])
        # Закриття, задокументоване у файлі, — правильний стан, не порушення.
        # Без цієї гілки гейт валив би буфер саме за те, що той виконав вимогу (Д-1).
        closed = 'ЗАКРИТО' in head or 'ПЕРЕНАВЕДЕНО' in head
        blob = '\n'.join(lines)
        for tgt in set(re.findall(r'`([^`]+\.md)`', blob)):
            if tgt not in mds and not closed:
                fail(f'{f} → ціль `{tgt}` не існує в теці (розпиляна/перейменована)'); g7 = True
        for num in sorted(set(re.findall(r'\bA(\d+)\b', blob))):
            hit = [v for v, t in vols.items() if re.search(rf'^## A{num}\.', t, re.M)]
            if hit and not closed:
                fail(f'{f} → A{num} уже канонізовано ({hit[0]}) — буфер пережив ціль (wsd 1.8)')
                g7 = True
            elif hit:
                warn(f'{f} → ціль A{num} закрито й задокументовано; лишився один прохід → архів')
                g7 = True
    if not g7:
        ok('живих буферів з мертвою ціллю немає')

    # ── G8 — сирота-посилання ─────────────────────────────────────────────
    print('\n[G8] сирота-посилання в канон-файлах')
    canon = [f for f in mds if f in KERNEL_FILES]
    orphans = {}
    for f in canon:
        body = open(R(root, f), encoding='utf-8').read()
        for ref in set(re.findall(r'`([A-Za-zА-Яа-яЇїІіЄєҐґ0-9_\-\.]+\.(?:md|py|js))`', body)):
            if not os.path.exists(R(root, ref)):
                orphans.setdefault(ref, []).append(f)
    # G8 розпил (сесія E). Раніше гейт давав ⚠ на ВСЕ, чого немає в теці, —
    # і оголошено-живий, і легально-заархівований файл виглядали однаково.
    # Наслідок: `StockCheck_session_summary_b27.md`, оголошений живим у §5,
    # але фізично відсутній, потонув серед 76 ⚠ і не був помічений.
    # Тепер розділено за ОГОЛОШЕННЯМ (1.10), не за наявністю:
    #   ✗ — названий живим у Lens_INDEX §5 → відсутність = справжня втрата
    #   ⚠ — названий у Lens_ARCHIVE_INDEX → відсутність = коректний стан
    #   ⚠ — не названий ніде → невідомий стан, дивитись очима
    if orphans:
        arch = open(R(root, 'Lens_ARCHIVE_INDEX.md'), encoding='utf-8').read() \
               if os.path.exists(R(root, 'Lens_ARCHIVE_INDEX.md')) else ''
        idx8 = open(idxp, encoding='utf-8').read() if os.path.exists(idxp) else ''
        # §5 «Живі білди» — від заголовка §5 до наступного «## §»
        # Дім оголошення = РЯДКИ ТАБЛИЦЬ §5 (живі білди · живі самері), не весь §5.
        # Проза §5 містить історичні згадки («колишній `wsd_TODO_running.md`»), і без
        # цього звуження гейт давав хибний ✗ на файл, який ніхто не оголошував живим.
        # Хибний ✗ шкідливіший за відсутній детектор — привчає ігнорувати червоне.
        m5 = re.search(r'^##\s*§5\b.*?$(.*?)(?=^##\s*§|\Z)', idx8, re.M | re.S)
        rows = [l for l in (m5.group(1) if m5 else '').splitlines() if l.lstrip().startswith('|')]
        live_decl = re.sub(r'\*\([^)]*\)\*', '', '\n'.join(rows))
        lost = named = unknown = 0
        for ref, src in sorted(orphans.items()):
            where = ", ".join(src)
            if ref in live_decl:
                fail(f'`{ref}` — ОГОЛОШЕНИЙ ЖИВИМ у Lens_INDEX §5, файлу в теці немає. '
                     f'Це втрата, не архівація (wsd 1.10)'); lost += 1
            elif ref in arch:
                warn(f'`{ref}` — в архіві за Lens_ARCHIVE_INDEX (норма); згадка: {where}')
                named += 1
            else:
                warn(f'`{ref}` — не названий ні в §5, ні в ARCHIVE_INDEX; згадка: {where}')
                unknown += 1
        if not lost:
            ok(f'жодного оголошено-живого файлу не втрачено '
               f'(в архіві: {named} · без оголошення: {unknown})')
    else:
        ok('усі посилання канон-файлів резолвляться')

    # ── G9 — дубль A-номера між томами ────────────────────────────────────
    print('\n[G9] унікальність A-номерів між томами')
    seen, dup = {}, False
    for v, t in vols.items():
        for num in re.findall(r'^## (A\d+(?:\.\d+)?)\.', t, re.M):
            if num in seen:
                fail(f'{num} — і в {seen[num]}, і в {v}: дубль після розпилу'); dup = True
            else:
                seen[num] = v
    if vols and not dup:
        ok(f'{len(seen)} A-записів, дублів немає')
    elif not vols:
        warn('томів Cookbook у теці немає — гейт пропущено')

    # ── G10 — перепис самері (wsd 1.8: ≤2 на продукт) ─────────────────────
    print('\n[G10] перепис самері — що виселяти')
    groups = {}
    for f in mds:
        m = re.match(r'(.+?)_session_summary', f)
        if m:
            groups.setdefault(m.group(1), []).append(f)
    if not groups:
        ok('самері в теці немає')
    # Живі самері ОГОЛОШУЮТЬСЯ в Lens_INDEX.md §5, не вгадуються за датою:
    # при завантаженні в Project mtime губиться, а алфавіт ставить b27 перед
    # b9 → гейт пропонував би виселити найновіше (клас помилки Д-1).
    idx = open(idxp, encoding='utf-8').read() if os.path.exists(idxp) else ''
    for prod, fs in sorted(groups.items()):
        live = [f for f in fs if f in idx]
        dead = [f for f in fs if f not in idx]
        retired = re.search(rf'\*\*{re.escape(prod)}\*\*[^|]*\|[^|]*АРХІВ-УСІ', idx) \
                  or re.search(rf'{re.escape(prod)}[^\n]*АРХІВ-УСІ', idx)
        if retired:
            warn(f'{prod} — оголошено АРХІВ-УСІ ({len(fs)} шт. на виселення):')
            for f in sorted(fs):
                print(f'      · {f}')
            continue
        if not live and len(fs) > 2:
            warn(f'{prod} — {len(fs)} самері, жодне не оголошене живим у Lens_INDEX.md §5. '
                 f'Оголоси 1–2 → гейт назве решту сам')
            continue
        if len(live) > 2:
            warn(f'{prod} — живими оголошено {len(live)} самері, стеля 2 (wsd 1.8)')
        if dead:
            warn(f'{prod} — НА АРХІВ ({len(dead)} з {len(fs)}); живі: {", ".join(live) or "—"}')
            for f in dead:
                print(f'      · {f}')
        else:
            ok(f'{prod} — {len(fs)} шт., усі оголошені живими')


    # ── G11 — цілісність буфера (14.29) ───────────────────────────────────
    # Буфер — єдина точка, куди пишуть УСІ сесії, і він не має ні блокування,
    # ні контролю версій у момент запису. Дві сесії одного дня затирають одна
    # одну, і запис зникає МОВЧКИ. Тому буфер оголошує власний лічильник, а гейт
    # звіряє оголошене з фактичним (wsd 1.10: детектор не вгадує — звіряє).
    print('\n[G11] цілісність буферів — оголошено ⟂ фактично')
    bufs = [f for f in mds if f.endswith('_delta_running.md')]
    if not bufs:
        ok('буферів у теці немає')
    for f in bufs:
        txt = open(R(root, f), encoding='utf-8').read()
        # записи = H2-заголовки, крім службових (✅ спорожнено / 🟡 відкриті)
        heads = [h.strip() for h in re.findall(r'^##\s+(.+)$', txt, re.M)
                 if not h.lstrip().startswith(('✅', '🟡', '⚠'))]
        decl = re.search(r'ЛОТОК:\s*(\d+)', txt)
        if not decl:
            warn(f'{f} — немає рядка «ЛОТОК: N записів». Без оголошення гейт може '
                 f'лише рахувати, але не може виявити ЗНИКЛИЙ запис (wsd 1.10)')
        elif int(decl.group(1)) != len(heads):
            fail(f'{f} — оголошено ЛОТОК: {decl.group(1)}, фактично {len(heads)}. '
                 f'Або мердж не дописав шапку, або запис затерто паралельною сесією (14.29)')
        else:
            ok(f'{f} — {len(heads)} запис(ів), збігається з оголошенням')
        # дубль номера: «Д-2», «A76» на початку заголовка
        nums = [m.group(1) for h in heads
                if (m := re.match(r'^((?:Д-\d+|A\d+))\b', h))]
        dups = sorted({n for n in nums if nums.count(n) > 1})
        if dups:
            fail(f'{f} — дубль номера запису: {", ".join(dups)}. Слід колізії '
                 f'паралельних сесій — шукати втрачений запис у самері тієї сесії, '
                 f'що писала першою (14.29)')

    # ══════════════════════════════════════════════════════════════════════
    # G12 — файл-МІСТ: оголошена структура ⟂ фактична (сесія F)
    #
    # Клас помилки: файл описує розташування чогось, до чого сам не має доступу
    # (архів поза Project, чужий репозиторій). Опис пишеться З НАМІРУ — «як має
    # бути» — і тихо розходиться з деревом. Ламається рівно та функція, заради
    # якої міст існує: raw-URL за неіснуючою текою дає 404, і файл виглядає
    # ВТРАЧЕНИМ, хоч він на місці. Знайдено 01.08.2026 очима, не гейтом:
    # §2 оголошував benches/ builds/ concepts/ misc/, фактично stands/ superseded/.
    #
    # Ключове рішення — звірка ВСЕРЕДИНІ файлу, §2 (оголошення) ⟂ §4 (реєстр).
    # Мережа не потрібна, доступ до архіву не потрібен, результат детермінований.
    # Гейт, що вимагає мережі, не запуститься саме тоді, коли потрібен.
    print('\n[G12] файли-мости — оголошена структура ⟂ фактична')
    ap = R(root, 'Lens_ARCHIVE_INDEX.md')
    if not os.path.exists(ap):
        warn('Lens_ARCHIVE_INDEX.md не знайдено — звірка структури пропущена')
    else:
        at = open(ap, encoding='utf-8').read()
        m2 = re.search(r'^##\s*§2\b.*?$(.*?)(?=^##\s*§|\Z)', at, re.M | re.S)
        decl = set(re.findall(r'^\s{2,}([a-z_][a-z0-9_]*)/', m2.group(1), re.M)) if m2 else set()
        reg = set(re.findall(r'^###\s+`archive/([a-z0-9_]+)/`', at, re.M))
        if not decl or not reg:
            warn('Lens_ARCHIVE_INDEX: §2 або §4 не розпарсились — перевірити розмітку очима')
        else:
            only2, only4 = decl - reg, reg - decl
            if only2:
                fail(f'Lens_ARCHIVE_INDEX §2 оголошує теки, яких немає в реєстрі §4: '
                     f'{", ".join(sorted(only2))}. raw-URL за ними дасть 404 (П-3)')
            if only4:
                fail(f'Lens_ARCHIVE_INDEX §4 реєструє теки, не оголошені в §2: '
                     f'{", ".join(sorted(only4))}. Структура описана з наміру, не з дерева')
            if not only2 and not only4:
                ok(f'Lens_ARCHIVE_INDEX §2 ⟂ §4 збігаються ({len(reg)} теки)')

        # Другий рівень — ФАКТИЧНЕ дерево, лише якщо архів під рукою.
        # Фолбек тихий: відсутність архіву локально — норма (він не підключений),
        # а не помилка. ✗ тут привчав би ігнорувати червоне (b27 §10).
        cand = [os.path.join(root, 'archive'), os.path.join(root, '..', 'archive')]
        real = next((c for c in cand if os.path.isdir(c)), None)
        if real is None:
            warn('archive/ локально недоступний — звірка з ФАКТИЧНИМ деревом пропущена '
                 '(норма: archive не підключений до Project)')
        else:
            tree = {d for d in os.listdir(real) if os.path.isdir(os.path.join(real, d))}
            if reg and tree - reg:
                fail(f'archive/ містить теки, не названі в §4: {", ".join(sorted(tree - reg))}')
            if reg and reg - tree:
                fail(f'§4 називає теки, яких у archive/ немає: {", ".join(sorted(reg - tree))}')
            if reg and tree == reg:
                ok(f'Lens_ARCHIVE_INDEX ⟂ фактичне дерево archive/ ({len(tree)} теки)')

    # ── G13 — нумерація секцій усередині файлу ────────────────────────────
    # ТРИГЕР: файл дописується в кінець кілька сесій поспіль. Автор бере
    # «наступний вільний §», дивлячись на ХВІСТ файлу, а не на весь список,
    # і другий §7 народжується мовчки — markdown дублю не заперечує.
    #
    # ЧОМУ ✗, а не ⚠: посилання «FINDINGS §7» після цього адресує ДВА різні
    # місця. Читач переходить у перше, не знаходить обіцяного, і робить
    # висновок «канон бреше» — найдорожчий сорт втрати довіри до бази знань.
    # Прецедент: Lens_glass_FINDINGS мав §7 «Roadmap» і §7 «Anchored top edge»
    # одночасно; зловлено грепом вручну, гейт мовчав (EquipLens S6).
    #
    # МЕЖА: archive/ не перевіряється — історія написана як написана,
    # правити її = підробляти свідчення (те саме рішення, що в §3-б ARCHIVE_INDEX).
    print('\n[G13] нумерація секцій усередині файлу')
    # Ключ секції = число + необов'язкова літера + необов'язковий «-суфікс».
    # Дві пастки, обидві зловлені на першому ж прогоні по живому канону:
    #   (?!\.\d)  — без нього «§1.1» читається як другий «§1» (підсекція ≠ дубль);
    #   (?:-…)    — без нього «§4», «§4-preset», «§4-port» зливаються в один
    #               ключ, і гейт валить хибним ✗ файл, у якому все правильно.
    # Суфікс береться ЦІЛИМ словом, не першою літерою: інакше «§4-варіанти»
    # і «§4-в» — дві різні секції — знову дають хибний дубль.
    sec_re = re.compile(
        r'^#{1,6}\s*§(\d+(?:[a-zа-яё])?(?:-[^\s.,;:·—]+)?)(?!\.\d)', re.M | re.I)
    live = [f for f in mds if 'archive' not in R(root, f).replace('\\', '/')]
    dirty = False
    for f in live:
        body = open(R(root, f), encoding='utf-8').read()
        hits = [(m.group(1), m.start()) for m in sec_re.finditer(body)]
        if len(hits) < 2:
            continue
        keys = [k for k, _ in hits]

        # (a) ДУБЛЬ — тверде ✗
        dup = sorted({k for k in keys if keys.count(k) > 1}, key=lambda x: (len(x), x))
        for d in dup:
            dirty = True
            # хто на цей §N посилається ззовні — перетворює «є дубль»
            # на «є дубль, і ось хто в нього впирається»
            stem = f[:-3]
            ref = [g for g in live if g != f and
                   re.search(re.escape(stem) + r'[^\n]{0,40}§' + re.escape(d) + r'\b',
                             open(R(root, g), encoding='utf-8').read())]
            tail = f' · посилаються: {", ".join(ref)}' if ref else ' · зовнішніх посилань не знайдено'
            fail(f'{f} — §{d} оголошено {keys.count(d)} рази{tail}')

        # (b)/(c) — лише по верхньому рівню (§N без літери), м'яко
        top = [int(k) for k in keys if k.isdigit()]
        if len(top) >= 3:
            uniq = sorted(set(top))
            gaps = [n for n in range(uniq[0], uniq[-1]) if n not in set(top)]
            # «зарезервовано» знімає діру з підозри (прецедент A74)
            if gaps and 'зарезервован' not in body.lower():
                # стеля друку: без неї один помилковий §77 друкує 67 номерів
                # і топить решту звіту — гейт, який неможливо прочитати,
                # виродиться в гейт, який ігнорують (b27 §10).
                shown = ', §'.join(map(str, gaps[:6]))
                more = f' …та ще {len(gaps) - 6}' if len(gaps) > 6 else ''
                warn(f'{f} — діра в нумерації: немає §{shown}{more} '
                     f'(секцію видалено без перенумерації?)')
            if top != sorted(top):
                warn(f'{f} — секції йдуть не по зростанню: '
                     f'{" ".join("§" + str(n) for n in top)} (дописано не в те місце?)')
    if not dirty:
        ok(f'дублів §-номерів немає ({len(live)} файлів перевірено)')

    # ── G16 — правило без детектора (К2) ──────────────────────────────────
    # ТРИГЕР: канон дописується роками. Правило без К2 виглядає як правило,
    # займає місце як правило і НЕ ЛОВИТЬ НІЧОГО — воно створює хибне
    # відчуття покриття, що дорожче за відсутнє правило (gov К1/К2).
    #
    # ЧОМУ ⚠, а не ✗: частина правил за природою не потребує детектора —
    # вони САМІ є процедурою перевірки (10.1-10.5) або їх порушення видно
    # негайно у формі відповіді (13.1, 13.3). Механічно відрізнити такі
    # від дірок неможливо, тому вирок виносить людина — один раз, руками,
    # маркером у тілі правила:
    #     <!-- K2:n/a — причина -->
    # Правило з маркером із підрахунку виходить. Маркер без причини не
    # приймається: «n/a» без підстави — це та сама дірка, тільки тихіша.
    #
    # МЕЖА: маршрутні заглушки (тіло виїхало в інший файл) не рахуються —
    # детектор живе разом з тілом, а не з покажчиком.
    print('\n[G16] правила без детектора (К2)')
    seen_rule_file = False
    for f in sorted(live):
        if not f.endswith(tuple(RULE_FILES)):
            continue
        try:
            body = open(R(root, f), encoding='utf-8').read()
        except OSError:
            continue
        seen_rule_file = True
        parts = re.split(r'\n(?=#{2}\s*\d+\.\d+)', body)
        rules = [x for x in parts if re.match(r'#{2}\s*\d+\.\d+', x)]
        if not rules:
            continue
        naked, na = [], 0
        for r_ in rules:
            num = re.match(r'#{2}\s*(\S+)', r_).group(1)
            # маршрутна заглушка — тіло в іншому файлі
            if is_route(r_) or len(r_.encode('utf-8')) < 400:
                continue
            if re.search(r'K2:n/a\s*—\s*\S', r_):
                na += 1
                continue
            if 'етектор' in r_ or 'К2' in r_:
                continue
            naked.append(num)
        with_det = sum(
            1 for r_ in rules
            if not (is_route(r_) or len(r_.encode('utf-8')) < 400)
            and not re.search(r'K2:n/a\s*—\s*\S', r_)
            and ('етектор' in r_ or 'К2' in r_))
        total = len(naked) + na + with_det
        if not naked:
            ok(f'{f} — усі {total} правил мають детектор або маркер K2:n/a')
        else:
            pct = round(100 * len(naked) / total) if total else 0
            shown = ' '.join(naked[:12])
            more = f' …та ще {len(naked) - 12}' if len(naked) > 12 else ''
            warn(f'{f} — {len(naked)} з {total} правил ({pct}%) без детектора '
                 f'і без маркера K2:n/a: {shown}{more}')
    if not seen_rule_file:
        warn('жодного файлу правил не знайдено — гейт не виконався '
             '(дзеркало неповне?), це НЕ зелений результат')

    g21(root)
    g23(root)
    g19(root)

# ─────────────────────────── G21 · ОДИН ДІМ НОМЕРА ──────────────────────────
def g21(root):
    """Номер правила з тілом — рівно в одному файлі RULE_FILES (IDX-7, G-J).
    Маршрут (заглушка за is_route, Ф-25, або <400 B) — не тіло: на старому місці він законний.
    К2 Ф-25: заглушка ≥ 400 B → ⚠ — тихе виключення стає видимим."""
    print('\n[G21] номер правила — один дім (розпил wsd, IDX-7)')
    homes, nfiles, big = {}, 0, []
    for f, kind in RULE_FILES.items():
        try:
            body = open(R(root, f), encoding='utf-8').read()
        except OSError:
            continue
        nfiles += 1
        for part in re.split(r'\n(?=##+\s+`?\d+\.\d+)', body):
            m = re.match(r'##+\s+`?(\d+\.\d+(?:-[а-яґєіїь])?)`?[\s|]', part)
            if not m:
                continue
            if is_route(part):
                nb = len(route_body(part).encode('utf-8'))
                if nb >= 400:
                    big.append(f'{kind} {m.group(1)} ({nb} B)')
                continue
            if len(part.encode('utf-8')) < 400:
                continue
            homes.setdefault(m.group(1), []).append(kind)
    if not nfiles:
        warn('жодного файлу правил не знайдено — G21 не виконався, це НЕ зелений результат')
        return
    if big:
        warn('виключено як маршрут, але ≥ 400 B (Ф-25) — перевір, чи не тіло: ' + ' · '.join(big))
    dups = sorted((k, v) for k, v in homes.items() if len(v) > 1)
    if dups:
        fail('номер з тілом у кількох файлах: ' +
             ' '.join(f'{k}({"+".join(v)})' for k, v in dups))
    else:
        ok(f'{len(homes)} номерів з тілом у {nfiles} файлах — кожен рівно в одному')


# ─────────────────────────── G23 · ТРИГЕР ЧИТАННЯ ФАЙЛУ ─────────────────────
def g23(root):
    """К6-1 (G-H §2): тригер читання на рівні файлу, не лише правила. Канон — kernel/**/*.md.
    Шапка = перші 12 рядків; тригер — рядок з «читається» або «AUTO-READ» (форма вільна)."""
    print('\n[G23] канон-файл має тригер читання в шапці (К6-1)')
    kd = os.path.join(root, 'kernel')
    files = sorted(glob.glob(os.path.join(kd, '**', '*.md'), recursive=True))
    if not files:
        warn('теки kernel/ з .md не знайдено — G23 не виконався, це НЕ зелений результат')
        return
    miss = []
    for p in files:
        head = open(p, encoding='utf-8').read().splitlines()[:12]
        if not any(re.search(r'читається|AUTO-READ', l) for l in head):
            miss.append(os.path.relpath(p, root))
    for m in miss:
        fail(f'`{m}` — у шапці немає тригера читання (К6-1: «читається коли: … · не читається: …»)')
    if not miss:
        ok(f'{len(files)} канон-файлів — у кожного тригер читання в шапці')


# ─────────────────────────── G19 · СПРАЦЮВАННЯ ПРАВИЛ ───────────────────────
# К4-1. Три рішення, на яких тримається чесність числа (перенесено з
# rules_hits.py разом з кодом — без них число бреше):
#   1. ПОРЯДОК СЕСІЙ береться з ОГОЛОШЕННЯ (Lens_ARCHIVE_INDEX.md), а не з дати
#      файлу чи алфавіту: дати губляться при Sync у Project, алфавіт ставить
#      b27 перед b9 (Lens_INDEX §5).
#   2. ЗБІГ СТРОГИЙ + ВИМОГА КОНТЕКСТУ: `12.16`, wsd 1.9, §2.4 — так; голе
#      число в прозі («2.4 KB», «v2.34») — ні. Без вимоги контексту замір дав
#      2 нулі замість 12, тобто 10 хибних ✓ (1.15 пастка 1).
#   3. НАРОДЖЕННЯ ≠ СПРАЦЮВАННЯ: правило, влите вчора, має нуль за визначенням.
#      Слід народження — **N.N** у таблиці злиття самері.
#
# ЧОМУ ⚠, А НЕ ✗ (відхилення від дослівної К2 в rules_hits.py, назване вголос):
#   вирок «виселити» виносить людина, і закрити ці нулі одним ходом неможливо —
#   це робота К3-1. Вісім незакриваних ✗ дали б рівно те, від чого застерігає
#   G3-1: червоне, на яке немає дії, вчить ігнорувати червоне.

_CTX = r'(?:`|wsd\s+|gov\s+|§|\bп\.\s?|\(|правил\w*\s+)'


def _rule_pat(rid):
    """Строгий якір номера правила з вимогою контексту посилання."""
    tail = r'(?![\d.])' if '-' in rid else r'(?![\d.\-])'
    return re.compile(_CTX + re.escape(rid) + tail)


def _rule_ids(path, kind):
    try:
        t = open(path, encoding='utf-8').read()
    except OSError:
        return []
    return [(m.group(1), kind) for m in
            re.finditer(r'^##+\s+`?(\d+\.\d+(?:-[а-яґєіїь])?)`?[\s|]', t, re.M)]


def _declared_order(root):
    """Порядок сесій = порядок рядків реєстру в ARCHIVE_INDEX (оголошення, не здогад)."""
    try:
        t = open(R(root, 'Lens_ARCHIVE_INDEX.md'), encoding='utf-8').read()
    except OSError:
        return []
    names = []
    for m in re.finditer(r'^- `([^`]+\.md)`', t, re.M):
        if m.group(1) not in names:
            names.append(m.group(1))
    return names


def g19(root):
    print('\n[G19] спрацювання правил — нуль згадок без сліду народження (К4-1)')
    R_ = [x for f, kind in RULE_FILES.items() for x in _rule_ids(R(root, f), kind)]
    seen, RU = set(), []
    for r_, k in R_:
        if r_ not in seen:
            seen.add(r_); RU.append((r_, k))
    if not RU:
        warn('файлів правил не знайдено — G19 не виконався, це НЕ зелений результат')
        return

    found = {}
    base = os.path.join(root, 'archive', 'summaries')
    for dp, _, fns in os.walk(base):
        for n in fns:
            if n.endswith('.md'):
                found[n] = os.path.join(dp, n)
    order = _declared_order(root)
    docs = [(n, open(found[n], encoding='utf-8').read()) for n in order if n in found]
    undeclared = sorted(set(found) - set(order))
    for d in LIVE_DIRS:
        if not os.path.isdir(d):
            warn(f'--live: теки немає — {d}')
            continue
        for n in sorted(os.listdir(d)):
            if n.endswith('.md'):
                docs.append((n + ' [live]', open(os.path.join(d, n), encoding='utf-8').read()))
    if not docs:
        warn('корпусу самері не знайдено (archive/summaries порожня, --live не дано) — '
             'G19 не виконався, це НЕ зелений результат')
        return

    zeros, born_zeros = [], []
    for rid, kind in RU:
        p = _rule_pat(rid)
        if any(p.search(t) for _, t in docs):
            continue
        bp = re.compile(r'\*\*' + re.escape(rid) + r'\*\*')
        (born_zeros if any(bp.search(t) for _, t in docs) else zeros).append(f'{rid}({kind})')

    print(f'  правил {len(RU)} · самері в підрахунку {len(docs)}'
          + (f' (+{len(LIVE_DIRS)} тек живих)' if LIVE_DIRS else ''))
    if undeclared:
        warn(f'{len(undeclared)} самері в archive/ не названі в ARCHIVE_INDEX — '
             f'у підрахунок НЕ ввійшли (IDX-13)')
    if born_zeros:
        print(f'  народжені, спрацювати ще не встигли ({len(born_zeros)}): '
              f'{" ".join(born_zeros)}')
    if zeros:
        warn(f'{len(zeros)} з {len(RU)} правил без жодного сліду — кандидати на '
             f'виселення (К3-1): {" ".join(zeros)}')
    else:
        ok(f'усі {len(RU)} правил мають слід у корпусі самері')
    if not LIVE_DIRS:
        print('  ⓘ живі самері (Project) не додані: правило, що спрацювало лише в '
              'останніх сесіях, читається тут як 0. Додати: --live <тека>')


# ────────────────────────────────── HTML ──────────────────────────────────

def html(path):
    print(f'\n=== HTML-ГЕЙТИ · {os.path.basename(path)} ===')
    src = open(path, encoding='utf-8').read()

    # H1 — node --check
    print('\n[H1] node --check по inline-скриптах')
    blocks = [m for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', src, re.S)]
    if not blocks:
        warn('inline-скриптів не знайдено')
    for i, m in enumerate(blocks, 1):
        code = m.group(1)
        if not code.strip():
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
            tf.write(code); tmp = tf.name
        r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
        os.unlink(tmp)
        if r.returncode == 0:
            ok(f'скрипт #{i} ({len(code.splitlines())} рядків)')
        else:
            fail(f'скрипт #{i}: {r.stderr.strip().splitlines()[0] if r.stderr else "?"}')

    # H2 — баланс тегів
    print('\n[H2] баланс тегів')
    for tag in ('div', 'span', 'button', 'a', 'svg', 'style', 'script'):
        o = len(re.findall(rf'<{tag}[\s>]', src))
        c = len(re.findall(rf'</{tag}>', src))
        if o == c:
            ok(f'{tag}: {o}/{c}')
        else:
            warn(f'{tag}: {o}/{c} — розбіжність. Літерали в JS-шаблонах дають '
                 f'легітимну різницю: звірити з попереднім білдом, не з нулем')

    # H3 — A69 dark-твін
    print('\n[H3] A69 dark-твін-паритет')

    # Г-5: судимо РОЗІБРАНИЙ CSS без коментарів, не сирий src.
    # Причина: пояснювальний коментар, що НАЗИВАЄ селектор, читався як його наявність.
    css = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', src, re.S))
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)

    # Г-3: межа блоку — баланс дужок, не нежадібний регекс.
    # Старий `[\s\S]*?\n}` завершував @media на ПЕРШІЙ дужці з нульової колонки
    # і «ковтав» увесь файл — тому близнюк знаходився завжди (хибний ✓).
    def _media_dark(s):
        out, pat = [], re.compile(r'@media[^{]*prefers-color-scheme\s*:\s*dark[^{]*\{')
        for m in pat.finditer(s):
            i, dep = m.end(), 1
            while i < len(s) and dep:
                if s[i] == '{': dep += 1
                elif s[i] == '}': dep -= 1
                i += 1
            out.append(s[m.end():i-1])
        return ''.join(out)

    media = _media_dark(css)
    dark = set(re.findall(r'\[data-theme=["\']?dark["\']?\]\s*([^\{,]+)\{', css))
    # Г-7: збіг по підрядку != збіг сутності. `.mny` "знаходиться" всередині `.mny-x`,
    # тому близнюк доводиться лише зі знаком межі селектора ({ або ,).
    miss = [s.strip() for s in dark if s.strip()
            and not re.search(re.escape(s.strip()) + r'\s*[{,]', media)]
    if not dark:
        warn('правил [data-theme=dark] не знайдено')
    elif miss:
        for s in miss[:12]:
            fail(f'немає auto-dark близнюка: {s}')
        if len(miss) > 12:
            fail(f'…і ще {len(miss)-12}')
    else:
        ok(f'усі {len(dark)} dark-правил мають близнюк у @media')

    # H4 — голі імена класів
    print('\n[H4] голі класи без префікса (звіт)')
    naked = sorted(set(re.findall(r'\.([a-z]{2,6})\s*\{', src)))
    generic = [c for c in naked if c in ('sec', 'row', 'box', 'item', 'card', 'lbl',
                                         'sweep', 'title', 'val', 'btn', 'list', 'head')]
    if generic:
        warn(f'загальні імена без префікса: {", ".join(generic)} — ризик колізії (b26_1 §4)')
    else:
        ok('загальних імен-гачків не знайдено')


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    if sys.argv[1] == '--gov':
        args = sys.argv[2:]
        while '--live' in args:
            i = args.index('--live')
            if i + 1 >= len(args):
                print('--live потребує теки'); sys.exit(2)
            LIVE_DIRS.append(args[i + 1]); del args[i:i + 2]
        gov(args[0] if args else '.')
    elif sys.argv[1] == '--html':
        if len(sys.argv) < 3:
            print('потрібен шлях до .html'); sys.exit(2)
        html(sys.argv[2])
    else:
        print(__doc__); sys.exit(2)
    print(f'\n─── ПІДСУМОК: ✓ {ok_n} · ⚠ {warn_n} · ✗ {fail_n} ───')
    sys.exit(1 if fail_n else 0)


if __name__ == '__main__':
    main()
