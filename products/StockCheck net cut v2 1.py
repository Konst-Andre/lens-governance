#!/usr/bin/env python3
# живе доки: не зібрано nets_assets_v2.js (вузол A1.2)
# дім: Lens_INDEX §5 «Живі стенди й інструменти» · заведено 06.08.2026, сесія H3.4
#
# Різак знаків мереж v2. Пікселі бере з ЯРУСУ 1 (локап, найбільша роздільність),
# пропорцію — з ЯРУСУ 2 (плитка, рішення оператора). Різати 112² з плитки 178–350px
# означало б віддати різкість там, де вона доступна безкоштовно.
#
# Прозорість робиться ЗАЛИВКОЮ ВІД РАМКИ, не глобальним порогом: джерела не мають
# альфи (усі 16 — RGB), і поріг «світліше за X → прозоре» вибив би білий хрест
# усередині зеленого квадрата й контрформи літер Мед-Сервіса. Це асерт Г3 гейта.

import json, os
import numpy as np
from PIL import Image
from scipy import ndimage
# О-35 (06.08.2026): було `from StockCheck_marks_gate import ...` — дім v1.
# Різак v2.1 і гейт v2.1 мусять ділити ОДНЕ визначення знака; імпорт із v1
# тихо повернув би доfilter-ну поведінку (пил у bbox) при наступному прогоні.
from StockCheck_marks_gate_v2_1 import sig_bbox   # спільне визначення «що є знаком»

BOX_MARK, BOX_MINI = 224, 112
K_MARK = 1.00      # ВАЖІЛЬ (Д-1): інсет mark = інсет markMini × K.
                   # 1.00 = однакова пропорція в обох боксах. Числа, яке б
                   # виправдало інше значення, ЩЕ НЕМАЄ — судиться на стенді, вузол B.
SOFT = 18

SLUG = {
    'anc': 'ANC', 'apteka_911': 'A911', 'apteka_nc': 'APTEKA_NC',
    'apteky_zaporizhzhia': 'NARODNA', 'dorra_group': 'CENTRALNA',
    'fakultet': 'FAKULTET', 'liky_poltavshchyny': 'LIKY_POLTAVSHCHYNY',
    'linda_farm': 'LINDA_FARM', 'med_service': 'MED_SERVIS',
    'moja_apteka': 'MOYA_APTEKA', 'sirius': 'BAZHAEMO',
    'solomia_service': 'PODOROZHNYK', 'triol': 'TRIOL',
    'uah': 'UAH',            # Р-3: slug ZDRAVYTSIA називав мережу однією з її марок
    'zaitseva_lv': 'ZAITSEVA',  # Д-5: у реєстрі був slug:null (рядок був mono)
}


def rgba_from(path):
    """RGB без альфи → RGBA. Прозорим стає лише фон, з'єднаний із рамкою."""
    a = np.array(Image.open(path).convert('RGB')).astype(int)
    fr = np.concatenate([a[0, :], a[-1, :], a[:, 0], a[:, -1]])
    bg = np.median(fr, axis=0)
    dev = np.abs(a - bg).max(axis=-1)

    lbl, n = ndimage.label(dev <= SOFT)
    outside = np.isin(lbl, list(set(np.unique(
        np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))) - {0}))

    alpha = np.clip((dev - 4) / (SOFT * 1.2) * 255, 0, 255)   # м'який край зберігається
    alpha[~outside] = 255                                      # усе, що не фон → щільне
    out = np.dstack([a, alpha]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def seal(img):
    """
    Запечатати прозорі зони, не з'єднані з рамкою БОКСУ.
    Чому після ресемплу, а не тільки на джерелі: якщо контур знака має розрив
    (трикутник Факультету), внутрішня білизна на повному полотні з'єднана
    із зовнішнім фоном і законно отримує alpha≈0. Обрізання по bbox символу
    цей зв'язок РІЖЕ — і та сама зона стає замкненою діркою. Тому пломба
    ставиться в кінці, у координатах готового боксу.
    """
    a = np.array(img)
    tr = a[..., 3] <= 16
    lbl, n = ndimage.label(tr)
    if n:
        edge = set(np.unique(np.concatenate(
            [lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))) - {0}
        inner = ~np.isin(lbl, list(edge)) & tr
        a[..., 3][inner] = 255
    return Image.fromarray(a, 'RGBA')


def fit(img, box, inset):
    """Вписати за довшою стороною так, щоб max(w,h)/box == inset."""
    # sig_bbox, не getbbox(): getbbox бере bbox УСІХ непрозорих пікселів,
    # включно з пилом, і знак їде вліво та недомасштабовується (Г5/Г6)
    bb = sig_bbox(np.array(img.getchannel('A')) > 16)
    img = img.crop(bb)
    t = box * inset
    s = t / max(img.width, img.height)
    img = img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))),
                     Image.LANCZOS)
    canvas = Image.new('RGBA', (box, box), (0, 0, 0, 0))
    canvas.paste(img, ((box - img.width) // 2, (box - img.height) // 2), img)
    return seal(canvas)


if __name__ == '__main__':
    layers = {x['src']: x for x in json.load(open('layers_v2.json'))}
    for d in ('out/mark', 'out/mini'):
        os.makedirs(d, exist_ok=True)

    print(f'{"slug":22} {"інсет":>6} {"mark":>10} {"mini":>10}')
    print('-' * 54)
    tot = 0
    for src, L in sorted(layers.items()):
        slug = SLUG[os.path.splitext(src)[0]]
        full = rgba_from(f'nets_in/{src}')
        x0, y0, x1, y1 = L['symbol']
        sym = full.crop((x0, y0, x1, y1))

        im_mark = fit(sym, BOX_MARK, min(0.96, L['inset'] * K_MARK))
        im_mini = fit(sym, BOX_MINI, L['inset'])
        pm, pi = f'out/mark/{slug}.webp', f'out/mini/{slug}.webp'
        im_mark.save(pm, 'WEBP', quality=92, method=6)
        im_mini.save(pi, 'WEBP', quality=92, method=6)
        a, b = os.path.getsize(pm), os.path.getsize(pi)
        tot += a + b
        print(f'{slug:22} {L["inset"]:6.3f} {a/1024:8.1f}К {b/1024:8.1f}К')
    print('-' * 54)
    print(f'разом {tot/1024:.1f} КБ сирих (v1: 195.5 КБ)')
