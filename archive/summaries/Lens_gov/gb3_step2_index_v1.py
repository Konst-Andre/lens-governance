#!/usr/bin/env python3
# живе доки: G-B3 запушено — далі архів (пакет відтворення стану)
# G-B3 · Крок 2: CHERGA IDX-12 оновлено + рядок G13-1 · INDEX §4 stagebench порожній · INDEX §5 governance-самері.
# Запуск з кореня клону: python3 gb3_step2_index_v1.py kernel
import sys, re, pathlib
def stop(x): print('✗ СТОП:', x); sys.exit(2)
k = pathlib.Path(sys.argv[1]); cp = k/'Lens_governance_CHERGA.md'; ip = k/'Lens_INDEX.md'
c = cp.read_text(encoding='utf-8'); ix = ip.read_text(encoding='utf-8')
def row(t, prefix):
    r = [l for l in t.split('\n') if l.startswith(prefix)]
    if len(r) != 1: stop(f'рядок «{prefix[:30]}» ×{len(r)}')
    return r[0]
NEW12 = "| `IDX-12` | **Буфери на злиття.** Стан 17.09.2026 (G-B3, `G11` ✓): stagebench **0** — ✅ **G-B закрито** (G-B · G-B2 · G-B3) · wsd **10** · cookbook **17**. Далі **G-C** wsd → **G-D** cookbook (`A105` готовий) | 13.08.2026 | усі три буфери порожні, дельта в каноні |"
G131 = "| `G13-1` | **`G13` сліпий до підсекцій `### N.N` без `§`.** Дубль або дірка в ланцюгу `Lens_stagebench_manifest.md` §8 (8.1–8.18) не ловиться — доведено `--inject` G-B3 17.09.2026 (дубль `## §N` ловить ✗). Причина — регекс `sec_re` у `Lens_validate.py` (вимагає `§`, відсікає `N.N`) | 17.09.2026 | `G13` бачить `N.N`-ланцюги; `--inject` дубля `### 8.x` дає ✗; прогін по живому канону без хибних ✗ (12.12) |"
NEW4 = "| `Lens_stagebench_delta_running.md` | `Lens_stagebench_manifest.md` | 🟢 **порожній** (G-B3 17.09.2026, `G11` ✓) · злиття G-B завершено: група А → §8.7-д · §8.12 · §8.14–§8.17 · Б → §8.10 · §8.11 · §8.13 · §8.18 · §6-а · §6-б · В → §6 · §8.9 · §2-п.7 |"
NEW5 = "| **Lens** *(governance)* | `Lens_governance_session_summary_GB3_ZLYTTIA_V.md` · `Lens_governance_session_summary_GA_BUFERY.md` *(G_MASKA · F_CHERGA_PLAN · GB_TRIAZH · GB2_ZLYTTIA_B витіснені 17.09.2026)* |"
done = [NEW12 in c, G131 in c, NEW4 in ix, NEW5 in ix]
if all(done): print('· Крок 2 уже влито (no-op)'); sys.exit(0)
if any(done): stop(f'часткове вливання {done}')
o12 = row(c, '| `IDX-12` |'); o4 = row(ix, '| `Lens_stagebench_delta_running.md` |'); o5 = row(ix, '| **Lens** *(governance)* |')
if 'stagebench **15**' not in o12: stop('IDX-12 не в очікуваному стані')
if '15 записів' not in o4: stop('INDEX §4 не в очікуваному стані')
if 'G_MASKA' not in o5: stop('INDEX §5 не в очікуваному стані')
c = c.replace(o12, NEW12 + '\n' + G131, 1)
ix = ix.replace(o4, NEW4, 1).replace(o5, NEW5, 1)
if len(c.encode('utf-8')) > 8192: stop(f'CHERGA > 8 KB ({len(c.encode())})')
cp.write_text(c, encoding='utf-8'); ip.write_text(ix, encoding='utf-8')
print('✓ CHERGA: IDX-12 оновлено + G13-1'); print('✓ INDEX: §4 stagebench порожній · §5 governance-самері')
