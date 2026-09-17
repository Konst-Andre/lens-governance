# ga_step4_index_cherga_v1.py · живе доки: пакет G-A залито в репо · IDX-6 закрито, IDX-12 прогрес, INDEX §4 = факт
import sys
root=sys.argv[1]
def row(p,start,new):
    f=f'{root}/{p}'; b=open(f,encoding='utf-8').read(); L=[l for l in b.split('\n') if l.startswith(start)]
    if len(L)!=1: sys.exit(f'СТОП {p} {start} {len(L)}×')
    if L[0]==new: print('no-op',start); return
    open(f,'w',encoding='utf-8').write(b.replace(L[0],new)); print('ok',start)
C='kernel/Lens_governance_CHERGA.md'
row(C,'| `IDX-6`','| `IDX-6` | ✅ **ЗАКРИТО 17.09.2026 (G-A).** Затирання не було: історія комітів — кожна версія буфера надмножина попередньої. Шапку не оновлювали при **дописуванні**: wsd 28.08 `Г-12` · 29.08 `Д-9` `Д-10` · 31.08 `2.13`; cookbook 31.08 `A**nn**`. Шапки = факт, `G11` ✓ по трьох. Скрипт звірки — `g11hist.py` (пакет G-A) | 30.08.2026 | виконано |')
row(C,'| `IDX-12`','| `IDX-12` | **Три буфери прострочені на злиття.** Стан 17.09.2026 (G-A, raw): stagebench **15** записів · wsd **10** · cookbook **17**. Порядок злиття: **G-B** stagebench (номери `§8.11`–`§8.17` зайняті записами буфера — мерджити підряд) → **G-C** wsd → **G-D** cookbook (`A105` готовий). `IDX-6` закрито — перешкоди порядку немає | 13.08.2026 | усі три буфери порожні, дельта в каноні |')
I='kernel/Lens_INDEX.md'
row(I,'| `Lens_cookbook_delta_running.md` | Cookbook','| `Lens_cookbook_delta_running.md` | Cookbook | 🔴 **17 записів** (заміряно 17.09.2026, G-A; `G11` ✓) · злиття — G-D |')
row(I,'| `Lens_stagebench_delta_running.md` | `Lens','| `Lens_stagebench_delta_running.md` | `Lens_stagebench_manifest.md` | 🔴 **15 записів** (Д-А…Д-М; заміряно 17.09.2026, G-A; `G11` ✓; ⚠ стеля 2–3 сесії прострочена з 13.08.2026) · злиття — G-B |')
row(I,'| `wsd_delta_running.md`','| `wsd_delta_running.md` *(фізично `kernel/wsd/`, **не** `kernel/`)* | `Work_Standard.md` | 🔴 **10 записів** (заміряно 17.09.2026, G-A; шапку зведено з фактом — `IDX-6` закрито, `G11` ✓). Стеля 2–3 сесії прострочена · злиття — G-C |')
