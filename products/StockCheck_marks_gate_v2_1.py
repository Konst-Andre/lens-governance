#!/usr/bin/env python3
# живе доки: StockCheck ріже растрові знаки мереж автоматично
# дім: Lens_INDEX §5 «Живі стенди й інструменти» (гейт G3) · заведено 06.08.2026, сесія H3.4
# канон: П-33 (торкання краю) · П-34 (глобальний параметр) · самері H3.3 §4
#
# Гейт нарізки знаків мереж. Ставиться ПЕРЕД різаком, не після:
# обрізання невидиме для лічильника файлів, ваги й валідності PNG — воно
# ловиться лише оком на контактному листі, тобто випадково й пізно.
#
#   python3 StockCheck_marks_gate_v2_1.py --selftest
#   python3 StockCheck_marks_gate_v2_1.py --dir out/mark --box 224 --expect 15
#   python3 StockCheck_marks_gate_v2_1.py --dir out/mini --box 112 --expect 15
#
# Д-16 (06.08.2026): пороги Г2 більше НЕ передаються прапорцем щоразу.
# Було три різні числа в трьох місцях — 0.30 у цьому коментарі, 0.35 у argparse,
# 0.28 у каноні (Р-12). Прогін на дефолтах давав ХИБНИЙ червоний на MOYA_APTEKA
# (fill 0.315). Тепер дефолт = канон; заглушки більше немає.

import argparse, sys, os, glob
import numpy as np
from PIL import Image
from scipy import ndimage

A_ON = 16          # альфа, вище якої піксель вважається вмістом
HOLE_MIN = 12      # px² — дірка, менша за це, це антиаліас, не дірка
DUST_REL = 0.02    # компонента, легша за цю частку найбільшої, — пил, не знак
BBOX_TOL = 0.01    # допуск Г5/Г6, частка сторони боксу


# ── значущий bbox — спільне визначення «що є знаком» ───────────────────────────
def sig_bbox(mask, rel=DUST_REL):
    """
    bbox зв'язних компонент, що важать ≥rel від найбільшої. Повертає (x0,y0,x1,y1)
    у стилі PIL.getbbox() — права й нижня межі ексклюзивні. None на порожній масці.

    Чому не getbbox() по всій масці: у джерелах Мед-Сервіса й Факультета справа
    від знака сидять поодинокі пікселі з альфою вище порога. Вони не торкаються
    краю (Г1 мовчить) і не утворюють замкненої зони (Г3 мовчить), але розтягують
    bbox на 30% ширини. Далі все рахується від роздутого боксу: центрування дає
    зсув, вписування за інсетом дає недомасштаб. Тому bbox мусить питати не
    "де є непрозорі пікселі", а "де є знак".
    """
    lbl, n = ndimage.label(mask)
    if n == 0:
        return None
    sz = np.array(ndimage.sum(mask, lbl, range(1, n + 1)))
    keep = [i + 1 for i, v in enumerate(sz >= sz.max() * rel) if v]
    ms = np.isin(lbl, keep)
    ys, xs = np.where(ms)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def raw_bbox(mask):
    ys, xs = mask.any(axis=1).nonzero()[0], mask.any(axis=0).nonzero()[0]
    if len(ys) == 0:
        return None
    return int(xs[0]), int(ys[0]), int(xs[-1]) + 1, int(ys[-1]) + 1


# ── завантаження ───────────────────────────────────────────────────────────────
def load_mask(path):
    """→ (mask, w, h). mask=True там, де є вміст."""
    im = Image.open(path).convert('RGBA')
    a = np.array(im)
    return a[..., 3] > A_ON, im.width, im.height


# ── Г1 · торкання краю (П-33) ─────────────────────────────────────────────────
def g1_edge(mask):
    """Маска не має торкатись межі боксу. Торкається → знак обрізаний."""
    hits = []
    if mask[0, :].any():   hits.append('верх')
    if mask[-1, :].any():  hits.append('низ')
    if mask[:, 0].any():   hits.append('ліво')
    if mask[:, -1].any():  hits.append('право')
    return (not hits), ('+'.join(hits) if hits else '')


# ── Г2 · заповнення ────────────────────────────────────────────────────────────
def g2_fill(mask, lo, hi, own_plate):
    """
    Площа bbox вмісту / площа боксу.
    Нижче lo — інсет перестарався, знак загубився в порожнечі.
    Вище hi — знак упирається в бокс.

    Д-3: верхня межа НЕ застосовується до знаків із власною плитою.
    АНЦ (суцільне коло), Фармастор (суцільний квадрат) — у них знак І Є плиткою,
    заповнення >0.92 законне. Це окремий клас (О-27), не виняток «бо так вийшло».
    """
    ys, xs = mask.any(axis=1).nonzero()[0], mask.any(axis=0).nonzero()[0]
    if len(ys) == 0 or len(xs) == 0:
        return False, 0.0, 'порожній бокс'
    bb = (ys[-1] - ys[0] + 1) * (xs[-1] - xs[0] + 1)
    fill = bb / mask.size
    if fill < lo:
        return False, fill, f'<{lo:.2f} знак загубився'
    if fill > hi and not own_plate:
        return False, fill, f'>{hi:.2f} упирається в бокс'
    return True, fill, ''


# ── Г3 · дірки від альфи ───────────────────────────────────────────────────────
def g3_holes(mask):
    """
    Прозорих зв'язних компонент має бути рівно 1 — зовнішня.
    Друга і далі = білі ділянки ВСЕРЕДИНІ знака стали прозорими:
    хрест у зеленому квадраті Фармастора, контрформи літер Мед-Сервіса.
    Джерела не мають альфи (заміряно: усі 16 — RGB), тому прозорість
    робиться заливкою від рамки, а не глобальним порогом. Це його детектор.
    """
    lbl, n = ndimage.label(~mask)
    if n == 0:
        return False, 0, 'немає прозорого фону взагалі'
    border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]])))
    border.discard(0)
    sizes = ndimage.sum_labels(np.ones_like(lbl), lbl, index=range(1, n + 1))
    holes = [i + 1 for i in range(n)
             if (i + 1) not in border and sizes[i] >= HOLE_MIN]
    if holes:
        return False, len(holes), f'{len(holes)} дірок, найбільша {int(max(sizes[h-1] for h in holes))}px²'
    return True, 0, ''


# ── Г5 · пил у bbox ───────────────────────────────────────────────────────────
def g5_dust(mask, box):
    """
    bbox значущих компонент має збігатися з bbox повної маски.
    Розбіжність = різак центрував і масштабував знак від роздутого боксу.
    Це ДІАГНОЗ: називає причину, яку Г6 бачить лише як наслідок.
    """
    sig, raw = sig_bbox(mask), raw_bbox(mask)
    if sig is None or raw is None:
        return False, 0.0, 'порожній бокс'
    drift = max(abs(sig[i] - raw[i]) for i in range(4))
    tol = box * BBOX_TOL
    if drift > tol:
        return False, drift, f'пил розтягує bbox на {drift}px (допуск {tol:.1f})'
    return True, drift, ''


# ── Г6 · центрування ──────────────────────────────────────────────────────────
def g6_center(mask, box):
    """
    Центр значущого bbox має збігатися з центром боксу.
    Ловить зсув там, де Г5 уже зелений: після ресемплу пил вимивається нижче
    A_ON, bbox стискається до знака — і дефект лишається тільки як зсув.
    Поодинці Г5 і Г6 пропускають по половині випадків.
    """
    sig = sig_bbox(mask)
    if sig is None:
        return False, (0.0, 0.0), 'порожній бокс'
    dx = (sig[0] + sig[2] - 1) / 2 - (box - 1) / 2
    dy = (sig[1] + sig[3] - 1) / 2 - (box - 1) / 2
    tol = box * BBOX_TOL
    if abs(dx) > tol or abs(dy) > tol:
        return False, (dx, dy), f'зсув dx={dx:+.1f} dy={dy:+.1f} (допуск ±{tol:.1f})'
    return True, (dx, dy), ''


# ── Г4 · комплект ──────────────────────────────────────────────────────────────
def g4_set(files, box, expect):
    """Кількість + квадратність + точний розмір боксу."""
    errs = []
    if expect and len(files) != expect:
        errs.append(f'файлів {len(files)}, очікується {expect}')
    for f in files:
        im = Image.open(f)
        if im.width != im.height:
            errs.append(f'{os.path.basename(f)} не квадратний {im.width}x{im.height}')
        elif box and im.width != box:
            errs.append(f'{os.path.basename(f)} {im.width}² ≠ {box}²')
    return (not errs), errs


# ── прогін ─────────────────────────────────────────────────────────────────────
def run(dirpath, box, expect, lo, hi, own_plate, quiet=False):
    files = sorted(glob.glob(os.path.join(dirpath, '*.webp')) +
                   glob.glob(os.path.join(dirpath, '*.png')))
    if not files:
        print(f'✗ Г4 · у {dirpath} немає файлів'); return False

    ok4, errs4 = g4_set(files, box, expect)
    rows, red = [], 0
    for f in files:
        slug = os.path.splitext(os.path.basename(f))[0]
        mask, _, _ = load_mask(f)
        o1, w1 = g1_edge(mask)
        o2, fill, w2 = g2_fill(mask, lo, hi, slug.upper() in own_plate)
        o3, nh, w3 = g3_holes(mask)
        o5, dr, w5 = g5_dust(mask, box or mask.shape[0])
        o6, dxy, w6 = g6_center(mask, box or mask.shape[0])
        bad = [t for t, o in (('Г1', o1), ('Г2', o2), ('Г3', o3),
                              ('Г5', o5), ('Г6', o6)) if not o]
        if bad: red += 1
        rows.append((slug, fill, bad, ' · '.join(x for x in (w1, w2, w3, w5, w6) if x)))

    if not quiet:
        print(f'\n{"slug":26} {"fill":>6}  стан')
        print('-' * 78)
        for slug, fill, bad, why in rows:
            mark = '✓' if not bad else '✗ ' + '+'.join(bad)
            print(f'{slug:26} {fill:6.3f}  {mark}{("  — " + why) if why else ""}')
        if errs4:
            print('\nГ4:')
            for e in errs4: print('  ✗ ' + e)
        print(f'\n{"🟢 ЗЕЛЕНИЙ" if (red == 0 and ok4) else "🔴 ЧЕРВОНИЙ"} · '
              f'рядків {len(rows)} · червоних {red} · Г4 {"✓" if ok4 else "✗"}')
    return red == 0 and ok4


# ── самотест (wsd 1.9 вісь 2) ──────────────────────────────────────────────────
def _box(box, inset, hole=False, touch=False, dust=False, shift=0):
    """Синтетичний знак: суцільний квадрат із заданим інсетом."""
    a = np.zeros((box, box, 4), np.uint8)
    m = 0 if touch else int(box * inset)
    a[m:box - m, m + shift:box - m + shift] = (10, 131, 54, 255)
    if hole:
        c, r = box // 2, box // 8
        a[c - r:c + r, c - r:c + r, 3] = 0
    if dust:
        a[box // 2, box - m // 2] = (10, 131, 54, 255)   # 1px пилу в порожнечі
    return Image.fromarray(a, 'RGBA')


def selftest():
    """
    Головна перевірка — не «чи ловить дефект», а «чи НЕ дає хибний ✗
    на коректному результаті». Гейт, що валить правильний вихід, гірший
    за відсутній: він змушує правити те, що не зламане.
    """
    d = '/tmp/_gate_selftest'
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(d + '/*'): os.remove(f)

    cases = [
        ('ctrl_ok',        _box(224, 0.12),                    True,  'еталон, інсет 12%'),
        ('ctrl_edge',      _box(224, 0.12, touch=True),        False, 'Г1 — торкається краю'),
        ('ctrl_tiny',      _box(224, 0.38),                    False, 'Г2 — знак загубився'),
        ('ctrl_hole',      _box(224, 0.12, hole=True),         False, 'Г3 — дірка від альфи'),
        ('farmastor',      _box(224, 0.02),                    True,  'Г2 — власна плита, >hi законно'),
        ('ctrl_dust',      _box(224, 0.12, dust=True),         False, 'Г5 — пил розтягує bbox'),
        ('ctrl_shift',     _box(224, 0.20, shift=20),          False, 'Г6 — зсув без пилу, Г5 зелений'),
    ]
    print('САМОТЕСТ · синтетичний контроль\n' + '-' * 78)
    allok = True
    for name, im, want, note in cases:
        im.save(f'{d}/{name}.png')
        got = run(d, 224, 1, 0.35, 0.92, {'FARMASTOR'}, quiet=True)
        for f in glob.glob(d + '/*'): os.remove(f)
        ok = (got == want)
        allok &= ok
        print(f'{"✓" if ok else "✗ ГЕЙТ БРАКОВАНИЙ"}  {name:14} очік={"зел" if want else "черв"} '
              f'факт={"зел" if got else "черв"}  — {note}')
    print('-' * 78)
    print('🟢 гейт придатний' if allok else '🔴 гейт бракований — правити ГЕЙТ, не результат')
    return allok


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dir'); p.add_argument('--box', type=int)
    p.add_argument('--expect', type=int, default=0)
    # Пороги Г2 калібровані ПО ЗАМІРУ 15 знаків (П-38, Р-12 у самері H3.4 §2).
    # 0.28 — нижче Сіріуса (0.319) і Моєї Аптеки (0.321), обидва коректні:
    #        знаки горизонтально витягнуті, вписані по довшій стороні.
    # 0.85 — вище фактичного максимуму 0.735 (Аптека НЦ), із запасом.
    # НЕ міняти без нового прогону розподілу — це не смаковий параметр.
    p.add_argument('--fill-min', type=float, default=0.28)
    p.add_argument('--fill-max', type=float, default=0.85)
    p.add_argument('--own-plate', default='')
    p.add_argument('--selftest', action='store_true')
    a = p.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if not a.dir:
        p.error('--dir або --selftest')
    op = {s.strip().upper() for s in a.own_plate.split(',') if s.strip()}
    sys.exit(0 if run(a.dir, a.box, a.expect, a.fill_min, a.fill_max, op) else 1)
