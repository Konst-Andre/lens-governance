#!/usr/bin/env python3
# gd_step1_merge_v2.py — (v2: дата звірки A105 = 17.09 веб, паспорт сам цього вимагає) · G-D1: 5 готових записів cookbook-буфера → томи 3/4/5 + Cookbook INDEX §2/§3.
# живе доки: G-D закрила злиття cookbook-буфера і самері G-D записане — тоді archive/summaries/Lens_gov/
# Буфер НЕ чіпає (прополка — окремий хід, gov 12.16). Повтор = no-op (П34).
# Запуск: python3 gd_step1_merge_v1.py <корінь репо lens-governance>
import sys, os, re, hashlib

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
CB = os.path.join(ROOT, "kernel", "cookbook")
BUF = os.path.join(CB, "Lens_cookbook_delta_running.md")
IDX = os.path.join(CB, "Lens_cookbook_INDEX.md")
V = {3: "Lens_iOS_cookbook_3_material.md", 4: "Lens_iOS_cookbook_4_components.md",
     5: "Lens_iOS_cookbook_5_motion.md"}
SEP = {3: "-----", 4: "-----", 5: "---"}   # звірено repr() по кожному тому

def die(m): print("STOP:", m); sys.exit(2)
def rd(p): return open(p, encoding="utf-8").read()
def one(text, anchor, what):
    n = text.count(anchor)
    if n != 1: die(f"{what}: якір count={n} (очікую 1): {anchor!r}")

OBS_A105 = ("> 🕒 **[09.2026] Спостереження (12.10).** Device ✓ iOS 18 · iOS 26.6+. "
            "iOS 27 і 26.7 вийшли 14.09.2026 "
            "(https://www.macrumors.com/2026/09/14/apple-releases-ios-26-7/) — на iOS 27 "
            "тик прямого дотику до `switch` **не перевірено**. Перевірити device на iOS 27 перед портом.\n")

# (A, том, заголовок у буфері, новий заголовок, чи рядок «том» у тілі, статус-позначка)
PLAN = [
    ("A104", 3, "## A104 (cand.) · ", "## A104. "),
    ("A76",  4, "## A76 (cand.) · ",  "## A76. "),
    ("A105", 5, "## A105 (cand.) · ", "## A105. "),
    ("A106", 5, "## A106 (cand.) · ", "## A106. "),
    ("A107", 5, "## A107 (cand.) · ", "## A107. "),
]
SUFFIX = {"A76": " ✅", "A106": " ✅"}   # A104/A105 ✅ уже в заголовку буфера; A107 без device → без знака

def extract(buf, head):
    one(buf, head, "буфер")
    i = buf.index(head)
    j = buf.find("\n---\n", i)
    return buf[i:] if j == -1 else buf[i:j + 1]

def reform(a, block, head_old, head_new):
    lines = block.split("\n")
    title = lines[0][len(head_old):].rstrip() + SUFFIX.get(a, "")
    body = [l for l in lines[1:] if not re.match(r"^\*\*(Цільовий том|Том при мерджі):\*\*", l)]
    out = head_new + title + "\n" + "\n".join(body)
    if a == "A105":
        anchor = "Протухлий запис не портується.\n"
        one(out, anchor, "A105 паспорт")
        out = out.replace(anchor, anchor + ">\n" + OBS_A105, 1)
        d_old = "**Звірено: 16.09.2026.**"
        one(out, d_old, "A105 дата звірки")
        out = out.replace(d_old, "**Звірено: 17.09.2026 (веб) · device 16.09.2026.**", 1)
    return out.rstrip("\n") + "\n"

buf = rd(BUF)
vols = {k: rd(os.path.join(CB, f)) for k, f in V.items()}
idx = rd(IDX)
changed = {}

for a, vol, ho, hn in PLAN:
    if re.search(rf"\n## {a}\.", vols[vol]):
        print(f"no-op: {a} уже в томі {vol}"); continue
    for k, t in vols.items():
        if re.search(rf"\n## {a}\.", t): die(f"{a} уже є в іншому томі {k} (G9)")
    entry = reform(a, extract(buf, ho), ho, hn)
    vols[vol] = vols[vol].rstrip("\n") + "\n\n" + SEP[vol] + "\n\n" + entry
    changed[vol] = True
    print(f"+ {a} → том {vol}")

# INDEX §2 (задача → запис) — після останнього рядка §2
S2_ANCHOR = "| Світлотінь перенесли зі щільного тіла на скло — читається інакше | `A102` | **3** |\n"
S2_ROWS = [
    ("| Ряд «підпис + число» рветься на два від самих цифр | `A76` | **4** |\n"),
    ("| Смуга по кромці скла під скролом — судити тільки на 1:1 | `A104` | **3** |\n"),
    ("| Тактильний тик iOS у PWA без `vibrate()` | `A105` | **5** |\n"),
    ("| Spring на багатокадровій анімації смикається | `A106` | **5** |\n"),
    ("| Останні кадри руху зникають ривком (клас зняли раніше) | `A107` | **5** |\n"),
]
# INDEX §3 (номер → том)
S3_A76_ANCHOR = "| `A75` | Іконки PWA: генерація з локнутого гліфа + межі платформи ✅ | **1** |\n"
S3_A102_ANCHOR = "| `A102` | Шейдинг не має власного адресата — його дає прозорість тіла ✅ | **3** |\n"
S3_A76 = "| `A76` | Метрична легенда, що не рве рядок ✅ | **4** |\n"
S3_TAIL = ("| `A104` | Скло судиться тільки на 1:1: дробовий масштаб родить крайовий артефакт ✅ | **3** |\n"
           "| `A105` | HSO — системний тик iOS у PWA через «свіч під пальцем» ✅ | **5** |\n"
           "| `A106` | Ease застосовується до кожного відрізка keyframes ✅ | **5** |\n"
           "| `A107` | Тривалість руху ≤ примусове зняття класу | **5** |\n")

if "| `A76` | Метрична" in idx:
    print("no-op: INDEX уже має рядки")
else:
    for an, w in [(S2_ANCHOR, "§2"), (S3_A76_ANCHOR, "§3 A75"), (S3_A102_ANCHOR, "§3 A102")]:
        one(idx, an, "INDEX " + w)
    idx = idx.replace(S2_ANCHOR, S2_ANCHOR + "".join(S2_ROWS), 1)
    idx = idx.replace(S3_A76_ANCHOR, S3_A76_ANCHOR + S3_A76, 1)
    idx = idx.replace(S3_A102_ANCHOR, S3_A102_ANCHOR + S3_TAIL, 1)
    changed["idx"] = True
    print("+ INDEX §2 ×5 · §3 ×5")

for k in V:
    if changed.get(k): open(os.path.join(CB, V[k]), "w", encoding="utf-8").write(vols[k])
if changed.get("idx"): open(IDX, "w", encoding="utf-8").write(idx)

for p in [IDX] + [os.path.join(CB, f) for f in V.values()]:
    b = open(p, "rb").read()
    print(f"{os.path.basename(p)}  {len(b)} B  md5 {hashlib.md5(b).hexdigest()[:8]}")
