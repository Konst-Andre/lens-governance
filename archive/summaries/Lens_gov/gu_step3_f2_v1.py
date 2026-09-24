#!/usr/bin/env python3
# gu_step3_f2_v1.py · G-U хід 3 · 24.09.2026 · живе доки: хід запушено → archive/summaries/Lens_gov/ (кладеться цим же ходом)
# Ф2 для governance: живі самері → sessions/Lens_gov/; пакет G-U + Project-копія E → Lens_gov/; §5 · ARCHIVE_INDEX · REPO_LAYOUT §2
import os, sys, shutil, hashlib
R = sys.argv[1] if len(sys.argv) > 1 else '.'; P = '/mnt/project'; O = '/mnt/user-data/outputs'
def die(m): print('✗', m); sys.exit(1)
md5 = lambda p: hashlib.md5(open(p,'rb').read()).hexdigest()
IX, AI, RL = (f'{R}/kernel/{f}' for f in ('Lens_INDEX.md','Lens_ARCHIVE_INDEX.md','Lens_REPO_LAYOUT.md'))
SES, GOV = f'{R}/sessions/Lens_gov', f'{R}/archive/summaries/Lens_gov'
ix, ai, rl = (open(f,encoding='utf-8').read() for f in (IX,AI,RL))
if os.path.isdir(SES) and '— 120 файлів' in ai: print('✓ вже застосовано (П34)'); sys.exit(0)
LIVE = [(f'{O}/Lens_governance_session_summary_GU_F1_ADRESA.md', 'Lens_governance_session_summary_GU_F1_ADRESA.md'),
        (f'{P}/Lens_governance_session_summary_GT_S35_INVENTAR.md', 'Lens_governance_session_summary_GT_S35_INVENTAR.md'),
        (f'{P}/Lens_inventory_GT_v1.md', 'Lens_inventory_GT_v1.md')]
ARC = [(f'{O}/gu_step1_archive_v1.py','gu_step1_archive_v1.py'), (f'{O}/gu_step2_f1_v1.py','gu_step2_f1_v1.py'),
       (f'{O}/gu_step3_f2_v1.py','gu_step3_f2_v1.py'),
       (f'{P}/Lens_session_summary_governance_E.md','Lens_session_summary_governance_E_PROJECT.md')]
for s_,d in LIVE+ARC:
    if not os.path.exists(s_): die(f'немає джерела {s_}')
for _,d in ARC:
    if os.path.exists(f'{GOV}/{d}'): die(f'вже в архіві {d}')
O5 = [l for l in ix.split('\n') if l.startswith('| **Lens** *(governance)* |')]
if len(O5)!=1 or 'GT_S35_INVENTAR' not in O5[0]: die('рядок §5 governance')
O5 = O5[0]
N5 = ('| **Lens** *(governance)* | `Lens_governance_session_summary_GU_F1_ADRESA.md` · `Lens_governance_session_summary_GT_S35_INVENTAR.md` '
      '· супутник `Lens_inventory_GT_v1.md` — **лежать у репо, тека `sessions/Lens_gov/`, не в Project** (Ф2 для governance, '
      '`Lens_REPO_LAYOUT.md` §2, G-U 24.09.2026; читати з clone/raw) *(GR · GQ витіснено G-U, файли не збережено — зміст у комітах '
      '`39681fd`…`fcfc3ec`; F · G — сироти G-C3; GP — G-S; GO — G-R; GN — G-Q; GM — G-P; GL — G-O; GK — G-N; GJ — G-M; GI — G-L; '
      'GH — G-K; GG — G-J; GF — G-H; GA…GE — 17.09.2026 → `archive/summaries/Lens_gov/`)* |')
A1 = '### `archive/summaries/Lens_gov/` — 116 файлів'
A2 = '- `Lens_session_summary_governance_G_MASKA.md` · 24.09.2026'
A2l = [l for l in ai.split('\n') if l.startswith(A2)]
if ai.count(A1)!=1 or len(A2l)!=1: die('якорі ARCHIVE_INDEX')
ROWS = ('\n- `gu_step1_archive_v1.py` · `gu_step2_f1_v1.py` · `gu_step3_f2_v1.py` · 24.09.2026 · Lens governance · пакет G-U '
        '(хід 1 — §5 → GT + сироти F·G; хід 2 — Ф1, дім формули; хід 3 — Ф2 для governance). Коміти `e53b104` · `2d1cc26` · хід 3'
        '\n- `Lens_session_summary_governance_E_PROJECT.md` · 24.09.2026 · Lens governance · друга редакція самері governance E '
        '(11 285 B, md5 `f79e66ca`), що лежала в Project під іменем архівної (`dac233a8`, 22 929 B); перейменовано, щоб не було дубля імені')
RA = '| Ф2 | самері в `sessions/` репо | ⬜ |'
RB = '| Ф2 | самері в `sessions/` репо | ✅ governance — G-U 24.09.2026 · продукти — Ф2-б, разом із Ф3 |'
RS = ('\n\n---\n\n## §2 Ф2 · Живе самері governance — у репо, тека `sessions/Lens_gov/`\n\n'
      '**Тригер.** Governance-сесія видає самері.\n\n'
      '**Дія.** Самері пушиться в `lens-governance`, тека `sessions/Lens_gov/`, тим самим ходом, що й закриття сесії. '
      'У Project **не кладеться**. `Lens_INDEX` §5 оголошує його **іменем** (Ф1 ще без детектора, §1-б) і називає теку. '
      'Витіснене (стеля 2, `wsd 1.8`) переїжджає `sessions/Lens_gov/` → `archive/summaries/Lens_gov/` — як досі з Project. '
      'Гейт `--live` дивиться на `sessions/Lens_gov/`. Скрипти кроків сесії — одразу в `archive/summaries/Lens_gov/` тим же пушем.\n\n'
      '**Чому.** G-T пообіцяла Konst «востаннє за старою схемою», а G-U повторила стару інструкцію «поклади в Project» — '
      'обіцянка без механізму (слово Konst, 24.09.2026). Живе самері — єдина причина, через яку governance ще вантажила Project.\n\n'
      '**Межа.** Лише governance. Самері продуктів — **Ф2-б**, вирішується разом із Ф3 (де в продуктовому репо живе не-деплой). '
      '`sessions/` ≠ `archive/`: живе ⟂ доказ — межу Ф4 не зачеплено.\n\n'
      '**Практика ззовні (мікроскоп G-U, 24.09.2026).**\n'
      '- `Routes:REPO_LAYOUT.md` — `sessions/` = «вмирає з подією, лишається слідом»; і живе, і минуле самері в одній теці. '
      'Беремо теку для живого. НЕ беремо злиття з архівом — у Lens `archive/` = корпус гейтів (Ф4 ще не вирішено).\n'
      '- ADR (Nygard; adr.github.io; github.com/opendatahub-io/architecture-decision-records, перевірено 24.09.2026) — '
      'рішення живуть markdown-файлами в репо поруч із кодом, витіснене лишається з позначкою. Беремо «в репо, не деінде». '
      'НЕ беремо нумерацію `0001-…` — у Lens координата в імені вже є (`G<літера>_<тема>`).')
if rl.count(RA)!=1: die('якір REPO_LAYOUT Ф2')
# --- записи ---
k=ix.index(O5); ix2=ix[:k]+N5+ix[k+len(O5):]; assert ix2[:k]+O5+ix2[k+len(N5):]==ix
ai2=ai.replace(A1,'### `archive/summaries/Lens_gov/` — 120 файлів',1)
j=ai2.index(A2l[0])+len(A2l[0]); ai3=ai2[:j]+ROWS+ai2[j:]; assert ai3[:j]+ai3[j+len(ROWS):]==ai2
rl2=rl.replace(RA,RB,1).rstrip('\n')+RS+'\n'
open(IX,'w',encoding='utf-8').write(ix2); open(AI,'w',encoding='utf-8').write(ai3); open(RL,'w',encoding='utf-8').write(rl2)
os.makedirs(SES, exist_ok=True)
for s_,d in LIVE: shutil.copyfile(s_, f'{SES}/{d}'); assert md5(s_)==md5(f'{SES}/{d}')
for s_,d in ARC: shutil.copyfile(s_, f'{GOV}/{d}'); assert md5(s_)==md5(f'{GOV}/{d}')
print('✓ sessions/Lens_gov 3 · Lens_gov 116→120 · §5 · ARCHIVE_INDEX · REPO_LAYOUT §2')
