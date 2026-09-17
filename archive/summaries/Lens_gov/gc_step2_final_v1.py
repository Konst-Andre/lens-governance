#!/usr/bin/env python3
# живе доки: G-C2b запушено з read-back (потім — archive разом із пакетом gc_step*)
# G-C2b крок 2: wsd 2.35 · Z_REGISTR ×4 · CHERGA · INDEX. Запуск з кореня репо ПІСЛЯ 1G.
# Якорі — repr()-байти (gov 12.19-б); усі перевірки count==1 ДО першого запису (12.16); повтор = no-op.
import sys, hashlib
W='kernel/wsd/Work_Standard.md'; Z='products/EquipLens/EquipLens_Z_REGISTR.md'
C='kernel/Lens_governance_CHERGA.md'; I='kernel/Lens_INDEX.md'
S='Lens_governance_session_summary_GC2a_HRUPA_G.md'
V235=("> **Версія 2.35** (17.09.2026 · Lens governance G-C1/G-C2a/G-C2b — `wsd_delta_running` злито до нуля).\n"
"> Нові: `1.20` звірка ідеї з Cookbook INDEX (+ вісь 6 у `1.9`) · `2.13` умовний вирок · `2.14` масштаб\n"
"> стенда · `2.15` анулювання device-вироку · `4.5` носій ≠ корінь. Підправила: `1.19-б` «дім названий» ≠\n"
"> рядок у файлі · `1.17-б` оснастка навігації перед кодом · `12.1-б` греп ≠ свідчення про сеанс.\n"
"> gov: `12.19-б` рендер виводу ≠ байти. Погашено за `12.17`: `Г-8` · `Г-12` (дім — `Lens_INDEX` §5).\n"
"> Аудит зв'язності → `К3-1` (`Lens_governance_CHERGA.md`).\n>\n")
A234='> **Версія 2.34** (03.09.2026 · AE-Simulator'
def zrow(n,tail_old,tail_new): return (tail_old,tail_new)
OPS=[
 (W, A234, V235+A234),
 (Z, '`EquipLens_session_summary_S20_K7b_GLASS_PALETTE.md`:54 | ⬜ тільки самері |', '`EquipLens_session_summary_S20_K7b_GLASS_PALETTE.md`:54 | ✅ у каноні · gov `12.19-б` |'),
 (Z, '`EquipLens_S17_STARTPOINTS_and_QUEUE_v7.md`:1231 | 🟡 у буфері |', '`EquipLens_S17_STARTPOINTS_and_QUEUE_v7.md`:1231 | ✅ у каноні · wsd `12.1-б` |'),
 (Z, '`EquipLens_session_summary_S25_K10_EDGE.md`:69 | 🟡 у буфері |', '`EquipLens_session_summary_S25_K10_EDGE.md`:69 | ✅ у каноні · wsd `2.15` |'),
 (Z, '`EquipLens_session_summary_S27_K22a_CARD_DONE.md`:118 | ⬜ тільки самері |', '`EquipLens_session_summary_S27_K22a_CARD_DONE.md`:118 | ✅ у каноні · gov `12.19-б` |'),
 (I, '| `Work_Standard.md` | правила роботи. Кластери 1–13. **v2.31** — governance-частина виїхала (нижче) |',
     '| `Work_Standard.md` | правила роботи. Кластери 1–13. Версія — у шапці файла (`12.20`); governance-частина виїхала в розпилі S14 (нижче) |'),
 (I, '`--gov` (G1–G6 governance)', '`--gov` (G1–G13 · G16 governance; номери — §5 «Стан номерів гейтів»)'),
 (I, '🔴 **10 записів** (заміряно 17.09.2026, G-A; шапку зведено з фактом — `IDX-6` закрито, `G11` ✓). Стеля 2–3 сесії прострочена · злиття — G-C |',
     '🟢 **порожній** (G-C2b 17.09.2026, `G11` ✓) · злиття G-C завершено: А погашено `Г-8` `Г-12` · Б → `1.19-б` · `2.13` · `2.14` · В → `1.20` · `2.15` · `4.5` · Г → `12.1-б` · `1.17-б` · gov `12.19-б` |'),
 (I, "(звірено грепом `Lens_validate.py` 31.08.2026).", "(звірено грепом `Lens_validate.py` 17.09.2026, G-C2b)."),
 (I, "Перший вільний номер — **`G17`**. Буфер `Г-10` претендує на `G12`, а `G12` зайнятий\n(файли-мости) — колізію розвести (`Г-12'`).",
     "Заявки без коду: `G17` — детектор черг (`IDX-11`) · `G18` — кандидат детектора `1.19-б`.\nПерший вільний номер — **`G19`**. Колізію `Г-10`/`G12` розведено G-C (`Г-12'` закрито)."),
]
def cline(t,prefix):
  ls=[l for l in t.split('\n') if l.startswith(prefix)]; return ls
ct=open(C,encoding='utf-8').read()
NEW_IDX12=("| `IDX-12` | **Буфери на злиття.** Стан 17.09.2026 (`G11` ✓): stagebench **0** · wsd **0** — ✅ **G-C закрито** (G-C1·C2a·C2b) · cookbook **17** → **G-D** (`A105` готовий) | 13.08.2026 | усі три буфери порожні, дельта в каноні |")
ROWS=("\n| `G16-1` | **`G16` зараховує детектор підправила `### N.N-б` батьку `## N.N`** — хибний ✓ (`1.15` п.3), доведено `--inject` (`12.1-б`). Близнюк `G13-1`. Текст: `"+S+"` §2 | 17.09.2026 | детектор рахується в тілі правила до `###` або підправило — окрема одиниця; `--inject` дає ⚠ голому батьку; без хибних ⚠ (12.12) |"
"\n| `Г-13` | **Колізія номерів між самері не ловиться:** `В-15` S21 (лок ≠ заборона) ⟂ `В-15` S22 (→ `1.17-б`); S21-текст більше ніде не живе. Текст: там само §2 | 17.09.2026 | S21-`В-15` має дім (з `Г-11`); вирішено: реєстр В-серії чи детектор дублів |"
"\n| `К3-1` | **Досяжність правила:** без точки виклику й детектора — мертвий текст. Аудит G-C2b: сироти wsd `1.7` `1.13` `3.8` · биті адреси `wsd 14.x` ×8, `wsd 6.5/6.6` ×2 · «wsd цілком» у 5 файлах при 182 KB · HISTORY без 2.30–2.34. Вісь прополки поряд `К2-1`/`К1-1`/`IDX-7` | 17.09.2026 | гейт рахує сиріт і биті адреси; кожна сирота має виклик, детектор або виселена |")
g1=cline(ct,'| `G13-1` |'); x6=cline(ct,'| `IDX-6` |'); g12=cline(ct,"| `Г-12'` |"); i12=cline(ct,'| `IDX-12` |')
done_c = ('| `К3-1` |' in ct)
if not done_c:
  for nm,l in (('G13-1',g1),('IDX-6',x6),("Г-12'",g12),('IDX-12',i12)):
    if len(l)!=1 or ct.count(l[0])!=1: sys.exit(f'СТОП: CHERGA рядок {nm} count={len(l)}')
  ct2=ct.replace(x6[0]+'\n','').replace(g12[0]+'\n','').replace(i12[0],NEW_IDX12).replace(g1[0],g1[0]+ROWS)
  if len(ct2.encode())>8000: sys.exit(f'СТОП: CHERGA {len(ct2.encode())} B > 8000 (стеля)')
# перевірка всіх OPS до запису
buf={}
plan=[]
for f,o,n in OPS:
  t=buf.setdefault(f,open(f,encoding='utf-8').read())
  if t.count(n)==1 and t.count(o)==(1 if o in n else 0): plan.append('skip'); continue
  if t.count(o)!=1: sys.exit(f'СТОП: якір count={t.count(o)} у {f}: {o[:60]!r}')
  buf[f]=t.replace(o,n); plan.append('do')
if not done_c: buf[C]=ct2
changed=[f for f in buf if buf[f]!=open(f,encoding='utf-8').read()]
for f in changed: open(f,'w',encoding='utf-8').write(buf[f])
md=lambda f: hashlib.md5(open(f,'rb').read()).hexdigest()[:8]
print(('записано: '+', '.join(changed)) if changed else 'no-op', '|', ' '.join(md(f) for f in (W,Z,C,I)), '| CHERGA', len(open(C,'rb').read()),'B')
