#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-H крок 1 — прополка Lens_governance_CHERGA.md + вирок по стелі (IDX-10).
   живе доки: хід 1 сесії G-H не влитий у репо.
   12.16: УСІ перевірки й стопи — вище першого open(...,'w').
   Пише ЛИШЕ в /mnt/user-data/outputs. Репо не чіпає."""
import sys, os, shutil, hashlib

SRC = '/home/claude/lg'
OUT = '/mnt/user-data/outputs'
F_CH = 'kernel/Lens_governance_CHERGA.md'
F_IX = 'kernel/Lens_INDEX.md'
F_EQ = 'products/EquipLens/EquipLens_CHERGA.md'
CEIL = 8192

def die(m):
    print('✗ СТОП:', m); sys.exit(1)

def rd(rel):
    p = os.path.join(SRC, rel)
    if not os.path.exists(p): die(f'немає {rel}')
    return open(p, encoding='utf-8').read()

ch, ix, eq = rd(F_CH), rd(F_IX), rd(F_EQ)

# ── 1. НОВІ РЯДКИ ЧЕРГИ (заміна цілого рядка за id — форма береться з файлу,
#       не з рендеру виводу, 12.19-б) ────────────────────────────────────────
ROWS = {
'К1-1': "| `К1-1` | **Правила wsd без тригера** — режим провалу №1 (`gov`, розділ К1/К2). Замір `48` протух: G-F/G-G дали тригери 18 правилам | 30.08.2026 | детектор тригера в `G16` (друга перевірка) |",
'К2-2': "| `К2-2` | **Смоук-твердження, що самі рахують очікуване** — пастка 4 до `1.15`. Норматив `✓525` після посилення детектора недійсний. Текст: `wsd_delta_running.md`, розділ «Пастка 4» | 02.09.2026 | кожне переписане твердження під `--inject` дає ✗; новий норматив ✓N заміряний і оголошений у `Lens_INDEX §5` |",
'Г-11': "| `Г-11` | Аудит супутника `EquipLens_S17_STARTPOINTS_and_QUEUE_v7.md` — 105 KB, жодного разу не ревізований; містить `З-11` і ще 29 З-номерів. Текст: `Lens_INDEX §5` | 28.08.2026 | супутник розібраний: живе → в доми, мертве → в archive |",
'IDX-9': "| `IDX-9` | **`G14`/`G15` оголошені в `Lens_INDEX`, коду в `Lens_validate.py` немає** — хибне покриття, гірше за відсутній гейт. Текст: `Lens_INDEX §5` «Стан номерів гейтів» + «Детектор протухання (`IDX-5`)» | 31.08.2026 | обидва гейти написані АБО оголошення в `§5` знято |",
'G13-1': "| `G13-1` | **`G13` сліпий до підсекцій `### N.N` без `§`** — регекс `sec_re` у `Lens_validate.py` вимагає `§`. Дірка чи дубль у ланцюгу `stagebench §8` (8.1–8.18) не ловиться; доведено `--inject` G-B3. Текст: самері `GB3` | 17.09.2026 | `G13` бачить `N.N`-ланцюги; `--inject` дубля `### 8.x` дає ✗; прогін по живому канону без хибних ✗ (12.12) |",
'G16-1': "| `G16-1` | **`G16` дає хибний ✓:** детектор `### N.N-б` зараховано батьку · будь-який підрядок «етектор»/«К2» у тілі. Слабкі ✓: gov `12.12` · `12.17`. Тексти: самері `GC2a §2` · `GE2_… §4` | 17.09.2026 | ✓ лише за `**Детектор…**` у тілі до `###`; `--inject` обох дає ⚠; без хибних ⚠ (12.12) |",
'Г-13': "| `Г-13` | **Колізія номерів між самері не ловиться:** `В-15` S21 (лок ≠ заборона) ⟂ `В-15` S22 (→ `1.17-б`); S21-текст більше ніде не живе. Текст: самері `GC2a §2` | 17.09.2026 | S21-`В-15` має дім (з `Г-11`); вирішено: реєстр В-серії чи детектор дублів |",
'К3-1': "| `К3-1` | **Досяжність правила:** без точки виклику й детектора — мертвий текст. Аудит сиріт, битих адрес і жанрів + форма прополки (гейт · чек-лист · ADR · архів). Вісь — `К4-1`. Текст: самері `GC2b §2` · `GD §2` | 17.09.2026 | гейт рахує сиріт і биті адреси; кожна сирота має виклик, детектор або виселена |",
'IDX-11': "| `IDX-11` | **`kernel/check_cherga.py` живе окремим скриптом** — дім коду гейта `Lens_validate.py` (`12.11`), номер `G17` вільний. Текст: шапка `kernel/check_cherga.py` | 31.08.2026 | влито в `Lens_validate.py` як `G17`, окремий файл видалено |",
}
DROP = ['IDX-10', 'IDX-12']
NEW_ROW = "| `К6-1` | **Тригер читання на рівні файлу, не лише правила** — К1/К2 на канон-файлі. Їде з розкладкою за жанрами (`К3-1`/`IDX-7`). Текст: самері G-H §2 | 18.09.2026 | кожен канон-файл має рядок тригера; гейт рахує файли без нього |"

lines = ch.split('\n')
idx = {}
for n, l in enumerate(lines):
    if l.startswith('| `'):
        i = l.split('`')[1]
        if i in idx: die(f'дубль id у черзі: {i}')
        idx[i] = n
for i in list(ROWS) + DROP:
    if i not in idx: die(f'id не знайдений у черзі: {i}')

# ── 2. ЯКОРІ ПРОЗИ — count == 1 кожен ────────────────────────────────────────
A_CH_PRE = """**Правила ті самі:** рядок = покажчик + вік, повний текст лишається там, де народився.
Читається цілком на старті governance-сесії. Правиться на місці, редакцій не має.
**Стеля 8 KB.**"""
N_CH_PRE = """**Правила ті самі:** рядок = покажчик + вік, повний текст лишається там, де народився.
Читається цілком на старті governance-сесії. Правиться на місці, редакцій не має.
**Стеля — `Lens_INDEX §5`** (число канонічне там, не тут)."""

A_CH_HDR = """> Заведено 30.08.2026. Аналог `<Продукт>_CHERGA.md`, але для боргів **ядра**:
> wsd · Cookbook · маніфести · гейти · індекси. Раніше такі пункти жили в
> `EquipLens_CHERGA.md` і витісняли з неї продуктове — черга продукту має стелю 8 KB."""
N_CH_HDR = """> Заведено 30.08.2026. Аналог `<Продукт>_CHERGA.md`, але для боргів **ядра**:
> wsd · Cookbook · маніфести · гейти · індекси. Підстава — `Lens_INDEX §5` «Черга ядра»."""

A_IX = "**Стеля 8 KB** — число канонічне тут, решта файлів посилається (`IDX-10`)."
N_IX = ("**Стеля 8 192 B (8 KiB)** — число канонічне **тут**, решта файлів посилається і "
        "не переказує (`12.20`). Детектор — `kernel/check_cherga.py`, константа `CEIL`; "
        "звірено 18.09.2026 (G-H, вирок Konst). Проза «8 KB» читалась і як 8 000, і як 8 192 "
        "— саме це закривало `IDX-10`.")

A_EQ = "> Стеля **8 KB** (`Lens_INDEX §5`)."
N_EQ = "> Стеля — `Lens_INDEX §5`."

for txt, anc, nm in ((ch, A_CH_PRE, 'CH preamble'), (ch, A_CH_HDR, 'CH header'),
                     (ix, A_IX, 'INDEX стеля'), (eq, A_EQ, 'EQ стеля')):
    c = txt.count(anc)
    if c != 1: die(f'якір «{nm}»: count={c}, очікував 1')

ZNIATO = ""

# ── 3. ЗАПИС (нижче всіх стопів) ─────────────────────────────────────────────
os.makedirs(OUT, exist_ok=True)
for i, t in ROWS.items():
    lines[idx[i]] = t
for i in DROP:
    lines[idx[i]] = None
out = [l for l in lines if l is not None]
# К6-1 — після К5-1, щоб К-серія трималась купи
k5 = next(n for n, l in enumerate(out) if l.startswith('| `К5-1`'))
out.insert(k5 + 1, NEW_ROW)
ch2 = '\n'.join(out).rstrip('\n') + '\n' + ZNIATO
ch2 = ch2.replace(A_CH_PRE, N_CH_PRE).replace(A_CH_HDR, N_CH_HDR)
ix2 = ix.replace(A_IX, N_IX)
eq2 = eq.replace(A_EQ, N_EQ)

n = len(ch2.encode('utf-8'))
if n > CEIL:
    die(f'результат {n} B > стелі {CEIL}')

shutil.copy(os.path.join(SRC, F_CH), os.path.join(OUT, 'Lens_governance_CHERGA_BEFORE_gh1.md'))
for rel, txt in ((F_CH, ch2), (F_IX, ix2), (F_EQ, eq2)):
    p = os.path.join(OUT, os.path.basename(rel))
    open(p, 'w', encoding='utf-8').write(txt)
    print(f'✓ {os.path.basename(rel):32s} {len(txt.encode("utf-8")):6d} B  md5={hashlib.md5(txt.encode()).hexdigest()[:8]}')

print(f'\nчерга: {len(ch.encode("utf-8"))} → {n} B (стеля {CEIL}, запас {CEIL-n} B)')
old_ids = [l.split('`')[1] for l in ch.split('\n') if l.startswith('| `')]
new_ids = [l.split('`')[1] for l in ch2.split('## Знято')[0].split('\n') if l.startswith('| `')]
print(f'id: {len(old_ids)} → {len(new_ids)}  ·  знято {sorted(set(old_ids)-set(new_ids))}  ·  додано {sorted(set(new_ids)-set(old_ids))}')
lost = [i for i in old_ids if i not in new_ids and i not in DROP]
print('втрачено без вироку:', lost if lost else 'немає ✓')
