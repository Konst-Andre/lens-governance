#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-K крок 3 — П-GH1 v2: видалення файлу з чату під тим самим PLAN-ID.
   Правки: Lens_claude_github_push.py (+--delete) · Lens_github_push_protocol.md (Ш3, §4, шапка)
   · Lens_INDEX.md (рядок надгробка, рядок скрипта). Саме видалення kernel/rules_hits.py —
   у коміті через --delete (тест механізму).
   живе доки: хід 3 G-K не влитий у репо.
   12.15: послаблення правила чинне лише у файлі — тому протокол і видалення в одному коміті.
   12.16: якорі count==1, усі стопи вище запису. П34/П37: повтор → exit 0."""
import sys, os
STG = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/lgx'
def die(m): print('✗ СТОП:', m); sys.exit(1)

E = {
'kernel/Lens_claude_github_push.py': [
 ('# Lens_claude_github_push.py · v1 · 16.09.2026 · П-GH1 · протокол: Lens_github_push_protocol.md',
  '# Lens_claude_github_push.py · v2 · 18.09.2026 (G-K: +--delete) · П-GH1 · протокол: Lens_github_push_protocol.md'),
 ('Видалення файлів, гілок, force-push — у v1 НЕ ПІДТРИМУЄТЬСЯ свідомо.',
  'Видалення ФАЙЛУ — лише --delete repo/path (v2): шлях має існувати в базі, входить у PLAN-ID,\n'
  'у dry-run окремим рядком ВИДАЛЕННЯ. Видалення гілок і force-push — НЕ ПІДТРИМУЄТЬСЯ свідомо.'),
 ('    ap.add_argument("files", nargs="+", help="repo/path=local/path")',
  '    ap.add_argument("--delete", action="append", default=[], metavar="repo/path",\n'
  '                    help="видалити файл (v2); шлях має існувати в базі")\n'
  '    ap.add_argument("files", nargs="*", help="repo/path=local/path")'),
 ('    pairs.sort()\n',
  '    pairs.sort()\n'
  '    dels = sorted({d.lstrip("/") for d in a.delete})\n'
  '    if not pairs and not dels:\n'
  '        die("нічого писати: немає ні файлів, ні --delete")\n'
  '    if set(dels) & {rp for rp, _ in pairs}:\n'
  '        die("той самий шлях і пишеться, і видаляється")\n'),
 ('    plan = h.hexdigest()[:6]\n',
  '    for rp in dels:\n'
  '        h.update(b"DEL\\0" + rp.encode())\n'
  '        st, cur = gh("GET", f"/repos/{a.repo}/contents/{rp}?ref={base}", token)\n'
  '        if st != 200 or not isinstance(cur, dict) or cur.get("type") != "file":\n'
  '            die(f"видалення: {rp} — у базі {base[:7]} такого файлу немає ({st})")\n'
  '        print(f"  · {rp}: ВИДАЛЕННЯ ({cur.get(\'size\')} б)")\n'
  '    plan = h.hexdigest()[:6]\n'),
 ('    st, tree = gh("POST", f"/repos/{a.repo}/git/trees"',
  '    for rp in dels:     # sha: None у дереві = видалення файлу (Git Data API)\n'
  '        items.append({"path": rp, "mode": "100644", "type": "blob", "sha": None})\n'
  '    st, tree = gh("POST", f"/repos/{a.repo}/git/trees"'),
],
'kernel/Lens_github_push_protocol.md': [
 ('> KERNEL v2 · читається ТОЧКОВО: коли задача — запис у GitHub із чату · v1 · 16.09.2026',
  '> KERNEL v2 · читається ТОЧКОВО: коли задача — запис у GitHub із чату · v2 · 18.09.2026 (G-K: видалення файлу під PLAN-ID)'),
 ('двоходовий PLAN-ID: запис неможливий без попереднього показаного dry-run; видалень і force-push немає',
  'двоходовий PLAN-ID: запис неможливий без попереднього показаного dry-run; видалення файлу — лише `--delete` у тому ж PLAN-ID (шлях існує в базі, у dry-run рядок ВИДАЛЕННЯ); видалень гілок і force-push немає'),
 ('> Типова ціль — нова гілка; `main` — тільки коли Konst назвав саме main. Видалення файлів/гілок і force-push — лише руками Konst на GitHub.',
  '> Типова ціль — нова гілка; `main` — тільки коли Konst назвав саме main.\n'
  '> Видалення файлу — лише `--delete` під PLAN-ID, коли Konst у цьому чаті назвав **конкретний шлях**\n'
  '> (загальне «видаляй, що треба» не рахується); у мікроскопі пушу — окремим рядком ВИДАЛЕННЯ.\n'
  '> Видалення гілок і force-push — лише руками Konst на GitHub.'),
],
'kernel/Lens_INDEX.md': [
 ('`rules_hits.py`; сам файл лишається в репо як надгробок до видалення руками —\n'
  'П-GH1 забороняє видалення з чату (§0 самері G-I). **Зарезервовані без коду: `G14`',
  '`rules_hits.py`; надгробок видалено з чату 18.09.2026 (G-K, `--delete`, П-GH1 v2),\n'
  'стан до надгробка — `archive/summaries/Lens_gov/rules_hits_v1.py`. **Зарезервовані без коду: `G14`'),
 ('двоходовий запобіжник `--dry-run` → `--confirm PLAN-ID`; без видалень і force-push (протокол `Lens_github_push_protocol.md`) |',
  'двоходовий запобіжник `--dry-run` → `--confirm PLAN-ID`; v2 — видалення файлу `--delete` під тим самим PLAN-ID; без видалення гілок і force-push (протокол `Lens_github_push_protocol.md`) |'),
],
}

cur = {p: open(os.path.join(STG, p), encoding='utf-8').read() for p in E}
if all(cur[p].count(n) == 1 for p in E for _, n in E[p]):
    print('✓ вже застосовано — нічого не пишу'); sys.exit(0)
for p, t in cur.items():
    for o, n in E[p]:
        if t.count(o) != 1: die(f'{p}: якір count={t.count(o)}: {o[:70]!r}')
out = {}
for p, t in cur.items():
    for o, n in E[p]: t = t.replace(o, n)
    out[p] = t
for p, t in out.items():
    open(os.path.join(STG, p), 'w', encoding='utf-8').write(t)
    print(f'✓ {p}: {len(cur[p].encode())} → {len(t.encode())} B')
