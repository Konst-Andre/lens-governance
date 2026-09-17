#!/usr/bin/env python3
# gd_step2_prune_v2.py — (v2: стеля CHERGA перевіряється ДО будь-якого запису; рядок стиснуто) · G-D2: прополка cookbook-буфера після gd_step1_merge_v2 + INDEX §4 + CHERGA IDX-12.
# живе доки: G-D закрила злиття cookbook-буфера і самері G-D записане — тоді archive/summaries/Lens_gov/
# Поштучно погоджено Konst 17.09.2026 (gov 12.16). Стоп, якщо запис ще не в томі. Повтор = no-op.
import sys, os, re, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
CB = os.path.join(ROOT, "kernel", "cookbook")
BUF = os.path.join(CB, "Lens_cookbook_delta_running.md")
INDEX = os.path.join(ROOT, "kernel", "Lens_INDEX.md")
CHERGA = os.path.join(ROOT, "kernel", "Lens_governance_CHERGA.md")
VOL = {"A76": "Lens_iOS_cookbook_4_components.md", "A104": "Lens_iOS_cookbook_3_material.md",
       "A105": "Lens_iOS_cookbook_5_motion.md", "A106": "Lens_iOS_cookbook_5_motion.md",
       "A107": "Lens_iOS_cookbook_5_motion.md"}
def die(m): print("STOP:", m); sys.exit(2)
def rd(p): return open(p, encoding="utf-8").read()
def one(t, a, w):
    n = t.count(a)
    if n != 1: die(f"{w}: count={n}: {a!r}")

buf, idx, ch = rd(BUF), rd(INDEX), rd(CHERGA)
C_OLD = "cookbook **17** → G-D (`A105`)"
C_NEW = "cookbook **12** (G-D ✅5)"
if C_NEW not in ch:
    one(ch, C_OLD, "CHERGA IDX-12")
    ch_new = ch.replace(C_OLD, C_NEW, 1)
    if len(ch_new.encode()) > 8000: die(f"CHERGA {len(ch_new.encode())} B > стелі 8000 — нічого не записано")
else:
    ch_new = None

if "**ЛОТОК: 12 записів.**" in buf:
    print("no-op: буфер уже прополото")
else:
    for a, v in VOL.items():                      # запис мусить уже жити в томі
        if not re.search(rf"\n## {a}\.", rd(os.path.join(CB, v))): die(f"{a} не в {v} — спершу merge")
    for a in ["A105", "A106", "A107", "A104", "A76"]:
        head = f"---\n\n## {a} (cand.) · "
        one(buf, head, f"буфер {a}")
        i = buf.index(head)
        j = buf.find("\n---\n", i + len(head))
        buf = buf[:i] + (buf[j + 1:] if j != -1 else "")
    buf = buf.rstrip("\n") + "\n"
    H_OLD = ("**ЛОТОК: 17 записів.** *(`A106` · `A107` з governance G-A 17.09.2026 · 2 готові A-записи + 3 покажчики + "
             "8 покажчиків cheat-sheet S26 · + `A**nn**` вебшрифт 31.08.2026 · + A105 HSO ✅ device-lock 16.09.2026, "
             "готовий до мерджу в том 5 · шапку звірено з історією комітів 17.09.2026, IDX-6)*\n")
    H_NEW = ("**ЛОТОК: 12 записів.** *(G-D 17.09.2026: змерджено `A76` `A104` `A105` `A106` `A107` · лишились "
             "`A103` 🔒 device-раунд · `З-37` `З-40` → `Г-11` (джерела в репо немає) · `К-1`…`К-8` device✗ · "
             "`A**nn**` вебшрифт 🔒 вордмарк)*\n")
    one(buf, H_OLD, "шапка ЛОТОК")
    buf = buf.replace(H_OLD, H_NEW, 1)
    M_ANCH = "## ✅ Змерджено 01.08.2026 (сесія E)\n"
    one(buf, M_ANCH, "таблиця змерджено")
    buf = buf.replace(M_ANCH, "## ✅ Змерджено 17.09.2026 (G-D)\n\n| запис | том |\n|---|---|\n"
                      "| `A104` | 3 |\n| `A76` | 4 |\n| `A105` (+ спостереження iOS 27) · `A106` · `A107` | 5 |\n\n"
                      "Номери збережено кандидатські: на `A76` `A104` `A105` уже посилались самері й wsd.\n\n---\n\n" + M_ANCH, 1)
    for sec in ["§27 · 25.08.2026.\n", "§28 · 26.08.2026.\n"]:
        a = f"`EquipLens_S17_STARTPOINTS_and_QUEUE_v7.md` {sec}"
        one(buf, a, "покажчик " + sec)
        buf = buf.replace(a, a[:-1] + " Файла в репо немає → розгортання разом з `Г-11` (G-D 17.09.2026).\n", 1)
    open(BUF, "w", encoding="utf-8").write(buf)
    print("+ буфер: −5 записів, шапка 12, таблиця G-D, З-37/З-40 → Г-11")

I_OLD = "| `Lens_cookbook_delta_running.md` | Cookbook | 🔴 **17 записів** (заміряно 17.09.2026, G-A; `G11` ✓) · злиття — G-D |\n"
I_NEW = ("| `Lens_cookbook_delta_running.md` | Cookbook | 🟡 **12 записів** (G-D 17.09.2026: 5 змерджено в томи 3/4/5; `G11` ✓) · "
         "решта заблоковані: `A103` · `A**nn**` · `К-1`…`К-8` device✗ · `З-37`/`З-40` → `Г-11` |\n")
if I_NEW in idx: print("no-op: INDEX §4")
else:
    one(idx, I_OLD, "INDEX §4"); open(INDEX, "w", encoding="utf-8").write(idx.replace(I_OLD, I_NEW, 1)); print("+ INDEX §4")

if ch_new is None: print("no-op: CHERGA")
else:
    open(CHERGA, "w", encoding="utf-8").write(ch_new); print(f"+ CHERGA IDX-12 · {len(ch_new.encode())} B")

for p in [BUF, INDEX, CHERGA]:
    b = open(p, "rb").read(); print(f"{os.path.basename(p)}  {len(b)} B  md5 {hashlib.md5(b).hexdigest()[:8]}")
