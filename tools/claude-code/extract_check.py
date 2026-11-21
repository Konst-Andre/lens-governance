#!/usr/bin/env python3
# живе доки: агент віддає читання великих джерел іншій моделі (Haiku) і приймає її витяг. Дім — lens-governance:tools/claude-code/ (CLAUDE_CODE.md «Велике джерело»).
# Перевірка дослівності витягу: кожне оголошення `властивість: значення` з блоків коду витягу (CSS, змінні, JS «x: y») шукається в джерелах
# дослівно — лише пробіли знято. Що не знайдено — вигадане, округлене чи «покращене» (EquipLens S40, 21.11.2026: витяг GlassKit 1.41 — 805/805 · 32/32 · 11/11).
# Практика: детермінований збіг підрядка після контрольованої нормалізації, без нечіткого порівняння (воно пропускає переказ) і цілим відрізком,
# не склеєним (dev.to «How I caught my LLM fabricating its own evidence»; the-obstacle-is-the-way spec-053, 21.11.2026).
# Переказ українською не перевіряється — лише код; 2–3 місця очима лишаються за агентом («як батько дитину», Konst 21.11.2026).
# Межа: рядок JS з двокрапкою поза CSS (`x: y` в об'єкті, мітка) теж стає «оголошенням» — його «✗» читай очима, це не вигадка.
# Запуск:  python3 extract_check.py <витяг.md> <джерело>… [--min 100]   → вихід 1, коли дослівних < --min % (типово 100) або коду нема
#          python3 extract_check.py selftest
import re, sys, os, tempfile

def decls(md):
    out = []
    for b in re.findall(r"```[a-z]*\n(.*?)```", md, re.S):
        b = re.sub(r"/\*.*?\*/|<!--.*?-->", "", b, flags=re.S)
        b = re.sub(r"(?m)(?<![:\w])//.*$", "", b)   # коментар JS (не https://)
        for m in re.finditer(r"(--?[a-zA-Z][\w-]*|[a-z-]+)\s*:\s*([^;{}\n]+?)\s*(?:;|$)", b, re.M):
            v = re.sub(r"[\"']\s*/?>.*$", "", m.group(2)).strip()   # інлайн-стиль HTML: style="height:100dvh"> — значення до лапки
            if len(v) >= 2 and not v.endswith(','): out.append(f"{m.group(1)}:{v}")
    return out

def check(md, srcs):
    norm = lambda s: re.sub(r"\s+", "", s)
    src = norm("".join(open(p, encoding='utf-8', errors='replace').read() for p in srcs))
    d = decls(md)
    return d, [x for x in d if not any(norm(x) + e in src for e in (";", "}", "\n", '"', "'"))]   # кінець оголошення: обрізаний список тіней не проходить як підрядок довшого

def main(a):
    if not a: print("extract_check.py <витяг.md> <джерело>… [--min 100] | selftest"); return 2
    if a[0] == 'selftest': return selftest()
    mn = float(a[a.index('--min') + 1]) if '--min' in a else 100.0
    a = [x for i, x in enumerate(a) if x != '--min' and (i == 0 or a[i - 1] != '--min')]
    d, bad = check(open(a[0], encoding='utf-8').read(), a[1:])
    pct = 100.0 * (len(d) - len(bad)) / max(1, len(d))
    good = bool(d) and pct >= mn
    print(f"{'✓' if good else '✗'} дослівно {len(d) - len(bad)} з {len(d)} оголошень ({pct:.0f} %, поріг {mn:.0f} %)" + ("" if d else " — у витягу нема блоків коду: перевіряти нічого"))
    for x in bad[:30]: print("  ✗ нема в джерелі:", x[:140])
    return 0 if good else 1

def selftest():
    t = tempfile.mkdtemp(); res = []
    def say(c, m): res.append(bool(c)); print(("✓ " if c else "✗ ") + m)
    src = os.path.join(t, 'a.css'); open(src, 'w').write(".pill {\n  width: 46px;\n  backdrop-filter: blur(var(--gl-blur));\n  box-shadow: var(--gl-shadow-glow), var(--gl-inset-medium);\n}\n")
    d, bad = check("Капсула:\n```css\n.pill { width: 46px; backdrop-filter: blur(var(--gl-blur)); }\n```\n", [src]); say(len(d) == 2 and not bad, "дослівний витяг → усе знайдено (пробіли не важать)")
    d, bad = check("```css\n.pill { width: 48px; }\n```", [src]); say(bad == ["width:48px"], "зуби: «покращене» значення 46 → 48 px — спіймано")
    d, bad = check("```css\nbox-shadow: var(--gl-shadow-glow);\n```", [src]); say(len(bad) == 1, "зуби: обрізаний список тіней — спіймано (оголошення звіряється цілим)")
    d, bad = check("```css\n/* width: 99px; */\n.pill { width: 46px; }\n```", [src]); say(len(d) == 1 and not bad, "коментар у блоці коду не рахується")
    m = os.path.join(t, 'x.md'); open(m, 'w').write("```css\n.pill { width: 48px; }\n```")
    say(main([m, src]) == 1, "вихід 1, коли нижче порогу")
    open(m, 'w').write("лише переказ без коду"); say(main([m, src]) == 1, "витяг без коду → ✗ (перевіряти нічого — не «зелене»)")
    print(f"─── extract_check selftest: {sum(res)}/{len(res)} ───"); return 0 if all(res) else 1

if __name__ == '__main__': sys.exit(main(sys.argv[1:]))
