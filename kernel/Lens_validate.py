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
    'Work_Standard_HISTORY.md', 'Lens_NEWPROJECT_bootstrap.md',
    'Lens_cookbook_INDEX.md',
    'Lens_iOS_cookbook_1_platform.md', 'Lens_iOS_cookbook_2_navigation.md',
    'Lens_iOS_cookbook_3_material.md', 'Lens_iOS_cookbook_4_components.md',
    'Lens_iOS_cookbook_5_motion.md', 'Lens_ARCHIVE_INDEX.md',
]
SIGNAL_KB, RED_KB = 120, 200

ok_n = warn_n = fail_n = 0


def ok(m):
    global ok_n; ok_n += 1; print(f'  ✓ {m}')


def warn(m):
    global warn_n; warn_n += 1; print(f'  ⚠ {m}')


def fail(m):
    global fail_n; fail_n += 1; print(f'  ✗ {m}')


# ─────────────────────────────── GOVERNANCE ───────────────────────────────

def gov(root):
    print(f'\n=== GOVERNANCE-ГЕЙТИ · {os.path.abspath(root)} ===')
    mds = sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, '*.md')))
    if not mds:
        fail('жодного .md не знайдено — не та тека?'); return

    # G1 — «живе доки» у перших 5 рядках
    print('\n[G1] рядок «живе доки» у шапці')
    bad = []
    for f in mds:
        head = open(os.path.join(root, f), encoding='utf-8').read().split('\n')[:5]
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
        p = os.path.join(root, f)
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
    idxp = os.path.join(root, 'Lens_INDEX.md')
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

    # G4 — 14.x резолвляться
    print('\n[G4] посилання 14.x з wsd → HISTORY')
    w, h = os.path.join(root, 'Work_Standard.md'), os.path.join(root, 'Work_Standard_HISTORY.md')
    if os.path.exists(w) and os.path.exists(h):
        refs = sorted(set(re.findall(r'\b14\.\d+\b', open(w, encoding='utf-8').read())))
        ht = open(h, encoding='utf-8').read()
        dead = [r for r in refs if f'## {r} ' not in ht]
        if dead:
            fail(f'висячі посилання: {", ".join(dead)}')
        else:
            ok(f'усі {len(refs)} посилань резолвляться')
    else:
        warn('wsd або HISTORY відсутні — гейт пропущено')

    # G5 — буфери
    print('\n[G5] буфери')
    for f in [x for x in mds if x.endswith('_delta_running.md')]:
        body = open(os.path.join(root, f), encoding='utf-8').read()
        entries = len(re.findall(r'^## ', body, re.M))
        if entries:
            warn(f'{f} — {entries} запис(ів); стеля 2–3 сесії, далі мерджити як є')
        else:
            ok(f'{f} — порожній')

    # G6 — обсяг
    print('\n[G6] обсяг файлів')
    big = False
    for f in mds:
        kb = os.path.getsize(os.path.join(root, f)) / 1024
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
    vols = {f: open(os.path.join(root, f), encoding='utf-8').read()
            for f in mds if re.match(r'Lens_iOS_cookbook_\d', f)}
    g7 = False
    for f in mds:
        if 'session_summary' in f:
            continue
        body = open(os.path.join(root, f), encoding='utf-8').read()
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
        body = open(os.path.join(root, f), encoding='utf-8').read()
        for ref in set(re.findall(r'`([A-Za-zА-Яа-яЇїІіЄєҐґ0-9_\-\.]+\.(?:md|py|js))`', body)):
            if not os.path.exists(os.path.join(root, ref)):
                orphans.setdefault(ref, []).append(f)
    if orphans:
        for ref, src in sorted(orphans.items()):
            warn(f'`{ref}` — згаданий у {", ".join(src)}, файлу в теці немає '
                 f'(норма, якщо в архіві; ✗, якщо ціль живого маршруту)')
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
    dark = set(re.findall(r'\[data-theme=["\']?dark["\']?\]\s*([^\{,]+)\{', src))
    media = ''.join(re.findall(r'@media\s*\(\s*prefers-color-scheme\s*:\s*dark\s*\)\s*\{(.*?)\n\}', src, re.S))
    miss = [s.strip() for s in dark if s.strip() and s.strip() not in media]
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
        gov(sys.argv[2] if len(sys.argv) > 2 else '.')
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
