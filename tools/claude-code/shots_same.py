#!/usr/bin/env python3
# живе доки: UI-рішення спершу міряються приміркою, потім переносяться в код (tools/claude-code/SHOTS.md §5 «знімок після поруч з обраним»).
# Перенос примірки → код «так само»: кроп того самого стану з примірки ⟂ кроп з коду, середня різниця пікселів (0–255) і частка помітно різних пікселів.
# Звідки (QR-Lens CC-16, 18.10.2026, пропуск Konst): значок «плитки» в коді вийшов сірим із темним колом — клас .zv-ic у шаблоні вже був зайнятий
# іншим елементом; очі агента на дрібних кадрах не побачили, ui_lint таке не міряє. Тим самим порівнянням вада видна: до виправлення — сірі плитки, після — 0,05.
#   python3 shots_same.py <примірка.png> <код.png> [--max 3] [--diff <вихід.png>]   → ✓ / ✗ (exit 1), --diff — карта різниці
#   python3 shots_same.py selftest                                                → зуби: однакові ✓, перефарбований значок ✗, зсув на 1 px — ✓ (не шум)
# Кадри — той самий стан, тема, масштаб і рамка (кроп елемента 1:1). Анімація — лише кінцевий кадр (фаза руху дає різницю — це не вада).
import sys

def load(p):
    from PIL import Image
    return Image.open(p).convert('RGB')

def compare(a, b):
    import numpy as np
    A, B = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    h, w = min(A.shape[0], B.shape[0]), min(A.shape[1], B.shape[1])
    d = abs(A[:h, :w] - B[:h, :w]).max(axis=2)
    return float(d.mean()), float((d > 40).mean()), d

def main(args):
    if args and args[0] == 'selftest':
        return selftest()
    if len(args) < 2:
        print(__doc__ or 'shots_same.py <примірка.png> <код.png> [--max 3] [--diff out.png]'); return 2
    mx = float(args[args.index('--max') + 1]) if '--max' in args else 3.0
    mean, part, d = compare(load(args[0]), load(args[1]))
    if '--diff' in args:
        from PIL import Image
        import numpy as np
        Image.fromarray((np.clip(d * 3, 0, 255)).astype('uint8')).save(args[args.index('--diff') + 1])
    ok = mean <= mx and part <= 0.02
    print(f"{'✓' if ok else '✗'} примірка ⟂ код: середня різниця {mean:.2f} (поріг {mx:g}) · помітно різних пікселів {part * 100:.1f} % (поріг 2 %)")
    return 0 if ok else 1

def selftest():
    from PIL import Image, ImageDraw, ImageChops
    def disc(col, dx=0):
        im = Image.new('RGB', (120, 120), (30, 40, 48)); g = ImageDraw.Draw(im)
        g.ellipse((14 + dx, 14, 106 + dx, 106), fill=(40, 70, 72))
        for x, y in ((38, 38), (64, 38), (38, 64)):
            g.rectangle((x + dx, y, x + dx + 18, y + 18), outline=col, width=4)
        return im
    good, same, grey, shift = disc((42, 140, 132)), disc((42, 140, 132)), disc((139, 148, 158)), disc((42, 140, 132), 1)
    r = [(compare(good, same)[0] <= 3 and compare(good, same)[1] <= 0.02, 'однакові кадри → ✓'),
         (not (compare(good, grey)[0] <= 3 and compare(good, grey)[1] <= 0.02), 'значок перефарбовано (бірюза → сірий, як у CC-16) → ✗'),
         (compare(good, shift)[1] <= 0.02 or compare(good, shift)[0] <= 3, 'зсув на 1 px → ✓ (не шум)')]
    for ok, t in r:
        print(('✓ ' if ok else '✗ ') + t)
    n = sum(ok for ok, _ in r); print(f'─── shots_same selftest: {n}/{len(r)} ───'); return 0 if n == len(r) else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
