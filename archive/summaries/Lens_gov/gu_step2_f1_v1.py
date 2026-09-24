#!/usr/bin/env python3
# gu_step2_f1_v1.py · G-U хід 2 · 24.09.2026 · живе доки: хід запушено → archive/summaries/Lens_gov/
# Ф1: новий kernel/Lens_REPO_LAYOUT.md (кладеться окремо) · Lens_INDEX §3 +рядок · §8 п.1–п.2 · §5 «перший вільний»
import sys
P=(sys.argv[1] if len(sys.argv)>1 else '.')+'/kernel/Lens_INDEX.md'; s=open(P,encoding='utf-8').read()
if 'Lens_REPO_LAYOUT.md` | **формула' in s: print('✓ вже застосовано (П34)'); sys.exit(0)
O1=("1. **Канон-посилання пишеться ІМЕНЕМ файлу, ніколи шляхом.** `Work_Standard.md`, не\n"
    "   `kernel/wsd/Work_Standard.md`. Шлях у Project не існує, посилання зі шляхом мертве.\n"
    "2. **Ім'я мусить бути унікальним по всьому дереву.** Два однойменні файли в різних\n"
    "   підтеках зіллються в Project у невизначений один. Гейт **G12** валить дубль імені.\n")
N1=("1. **Канон-посилання пишеться ІМЕНЕМ файлу — до ходу детектора Ф1.** `Work_Standard.md`, не\n"
    "   `kernel/wsd/Work_Standard.md`. Перехід на шлях від кореня репо (`Репо:шлях` — для чужого)\n"
    "   ухвалено 24.09.2026 і набирає сили з ходу детектора: `Lens_REPO_LAYOUT.md` §1.\n"
    "2. **Ім'я мусить бути унікальним по всьому дереву.** Два однойменні файли в різних\n"
    "   підтеках зіллються в Project у невизначений один. ⚠ **Детектора немає:** `G12` — файл-міст\n"
    "   `archive/` ⟂ дерево, дублі імен він не бачить (звірено з `Lens_validate.py` р.26, р.414,\n"
    "   G-U 24.09.2026; стара редакція цього пункту твердила протилежне). Заявка — **`G24`**.\n")
A2='| `Lens_ARCHIVE_INDEX.md` | що лежить в `archive/` репо + 5 тригерів, коли туди йти |\n'
N2=A2+'| `Lens_REPO_LAYOUT.md` | **формула архітектури**: тека · ім\'я · адресація · носії — по Ф (Ф1 ухвалено G-U 24.09.2026). Аналог `Routes:REPO_LAYOUT.md` |\n'
A3='Перший вільний номер — **`G22`**.'
N3=('Перший вільний номер — **`G24`** (заявка Ф1: дубль імені, `Lens_REPO_LAYOUT.md` §1). ⚠ Рядок «написані» вище '
    'протух: у коді є ще `G22` (стартове в code block, G-Q) і `G23` (тригер читання в шапці, К6-1) — звірено '
    'регексом `G\\d+` по `Lens_validate.py`, G-U 24.09.2026.')
out=s
for a,n in ((O1,N1),(A2,N2),(A3,N3)):
    if out.count(a)!=1: sys.exit(f'✗ якір ×{out.count(a)}: {a[:50]!r}')
for a,n in ((O1,N1),(A2,N2),(A3,N3)):
    k=out.index(a); new=out[:k]+n+out[k+len(a):]
    assert new[k:k+len(n)]==n and new[:k]+a+new[k+len(n):]==out, 'revert'
    out=new
open(P,'w',encoding='utf-8').write(out); print('✓ Lens_INDEX',len(s.encode()),'→',len(out.encode()),'B')
