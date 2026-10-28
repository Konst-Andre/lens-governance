"""pw_quiet · пауза приладу Playwright = «усе, що мало статись у вікні, сталось», а не простій (wsd 1.21; народився в AE S103, В-216).
живе доки: прилади Playwright (Python) чекають через page.wait_for_timeout. Пара для Node — pw_quiet.mjs; скрипт сторінки — pw_quiet.js (один на обидві).

Пауза N мс гарантувала: що мало статись за N мс — сталось. quiet гарантує те саме і повертається, щойно це правда:
таймери сторінки (setTimeout) з терміном у вікні · скінченні анімації й переходи (document.getAnimations(): лишилось = endTime − currentTime,
MDN 24.10.2026) · запити в дорозі (fetch · XHR) · і так два кадри поспіль. Інакше — чекає до межі N, як раніше. setInterval не тримає.
Не беремо Playwright Clock (playwright.dev/python/docs/clock): підробляє й requestAnimationFrame — для приладів з мережею ризик.
Замір AE S103: проходи 46 → 21 с і 90 → 46 с; знахідки пункт у пункт ті самі; на старому білді — ті самі ✗.

Вживання:  sys.path.insert(0, '<ядро>/tools/claude-code'); from pw_quiet import install, report
           install(page) — одразу після new_page(); далі page.wait_for_timeout(N) — «тиша до N»; print(report()) — у кінці.
Опитування стану з боку приладу («до 50 разів по 100 мс: чи дійшов запис у Python-заглушку») — справжній час: page.wait_real(ms)
(AE S103: «тиша» на тихій сторінці повертається за 15 мс, 50 кругів минали раніше, ніж запис — п. 114 «блимнув»).
Умова на стан сторінки перед залежним кроком («нова позиція вже в чернетці», «вікно відкрите») — page.wait_for_function(js, timeout, polling=100)
у try → ✗ з назвою події, не «тиша» і не власний цикл: «тиша» міряє вікно, а не відгук сторінки під навантаженням (AE S113: 1 з 4 паралельних проходів
обривався на 30 с; умову події — заміряти станом, не вгадувати: після Enter правка йшла на наступне поле, а не закривалась).
QUIET=0 (або AE_QUIET=0) — старі паузи: негативний контроль «старий ⟂ новий» і запасний режим. Init script CSP не блокує.
Самоперевірка:  python3 pw_quiet.py selftest
"""
import os, sys, time

JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pw_quiet.js')
STATS = {'calls': 0, 'saved_ms': 0.0, 'cap': 0}


def off():
    return os.environ.get('QUIET') == '0' or os.environ.get('AE_QUIET') == '0'


def install(pg):
    """Підміняє pg.wait_for_timeout на «тишу до N мс». QUIET=0 — без змін."""
    if off():
        pg.wait_real = pg.wait_for_timeout
        return pg
    pg.add_init_script(path=JS)
    real = pg.wait_for_timeout
    pg.wait_real = real   # цикли-опитування стану з боку приладу — справжній час

    def quiet(ms):
        t0 = time.monotonic()
        try:
            r = pg.evaluate('ms => window.__aeQuiet ? window.__aeQuiet(ms) : "none"', ms)
        except Exception:
            # перехід сторінки посеред очікування — добираємо решту справжнім часом
            r = 'err'
        left = ms - (time.monotonic() - t0) * 1000
        if r in ('none', 'err') and left > 0:
            real(left)
        STATS['calls'] += 1
        STATS['cap'] += r == 'cap'
        STATS['saved_ms'] += max(0, ms - (time.monotonic() - t0) * 1000)

    pg.wait_for_timeout = quiet
    return pg


def report():
    """Рядок для кінця приладу: скільки пауз і скільки часу зекономлено."""
    if off() or not STATS['calls']:
        return 'тиша: вимкнено (QUIET=0) — фіксовані паузи'
    return f"тиша: пауз {STATS['calls']} · до межі {STATS['cap']} · зекономлено {STATS['saved_ms'] / 1000:.0f} с"


def selftest():
    from playwright.sync_api import sync_playwright
    ok = 0; n = 0
    def t(cond, name):
        nonlocal ok, n; n += 1; ok += bool(cond); print(('✓' if cond else '✗') + ' ' + name)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = install(b.new_page())
        pg.goto('data:text/html,<button onclick="setTimeout(()=>document.body.dataset.ok=1,120)">b</button><div id=a style="transition:opacity .25s">x</div>')
        s = time.monotonic(); pg.wait_for_timeout(500); d = (time.monotonic() - s) * 1000
        t(d < 200, f'порожня сторінка → не чекає межу ({d:.0f} мс < 200)')
        pg.click('button'); s = time.monotonic(); pg.wait_for_timeout(500); d = (time.monotonic() - s) * 1000
        t(pg.evaluate('document.body.dataset.ok') == '1' and 110 <= d < 400, f'таймер 120 мс у вікні → дочекано ({d:.0f} мс), результат є')
        pg.evaluate("setTimeout(()=>{},900)"); s = time.monotonic(); pg.wait_for_timeout(300); d = (time.monotonic() - s) * 1000
        t(d < 200, f'таймер поза вікном (900 > 300) → не тримає ({d:.0f} мс)')
        pg.evaluate("document.getElementById('a').style.opacity='0'"); s = time.monotonic(); pg.wait_for_timeout(600); d = (time.monotonic() - s) * 1000
        t(220 <= d < 500 and pg.evaluate("getComputedStyle(document.getElementById('a')).opacity") == '0', f'перехід 250 мс → дочекано кінця ({d:.0f} мс)')
        pg.evaluate("setInterval(()=>{},50)"); s = time.monotonic(); pg.wait_for_timeout(300); d = (time.monotonic() - s) * 1000
        t(d < 200, f'setInterval не тримає ({d:.0f} мс)')
        s = time.monotonic(); pg.wait_real(300); d = (time.monotonic() - s) * 1000
        t(d >= 290, f'wait_real — справжній час для циклів-опитування ({d:.0f} мс ≥ 290)')
        b.close()
    os.environ['QUIET'] = '0'
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = install(b.new_page()); pg.goto('data:text/html,x')
        s = time.monotonic(); pg.wait_for_timeout(300); d = (time.monotonic() - s) * 1000
        t(d >= 290, f'QUIET=0 → стара пауза ({d:.0f} мс ≥ 290)'); b.close()
    print(f'─── pw_quiet selftest: {ok}/{n} ───'); return ok == n


if __name__ == '__main__' and sys.argv[1:] == ['selftest']:
    sys.exit(0 if selftest() else 1)
