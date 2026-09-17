# живе доки: G-C3 запушено з read-back (пакет сесії, потім archive/summaries/Lens_gov/)
# gc3_step1_archive_v1.py — архів governance-хвоста + ARCHIVE_INDEX + INDEX §5/§8 + CHERGA IDX-12/13
# Запуск з кореня lens-governance. Повтор = no-op, exit 0. Якір count==1 або стоп (gov 12.16).
import os, sys, shutil, hashlib
SRC = '/mnt/project'; DST = 'archive/summaries/Lens_gov'
D = '17.09.2026'
FILES = [  # файл · що всередині · чому
 ('Lens_governance_session_summary_GA_BUFERY.md','G-A: шапки буферів = факт, IDX-6','§0 підхоплено G-B'),
 ('Lens_governance_session_summary_GB_TRIAZH.md','G-B: тріаж stagebench-буфера','§0 підхоплено G-B2'),
 ('Lens_governance_session_summary_GB2_ZLYTTIA_B.md','G-B2: злиття груп Б1/Б2 у manifest','§0 закрито G-B3'),
 ('Lens_governance_session_summary_GB3_ZLYTTIA_V.md','G-B3: група В, stagebench-буфер 0','§0 закрито G-C'),
 ('Lens_governance_session_summary_GC1_ZLYTTIA_WSD.md','G-C1: злиття wsd-буфера, групи А/Б/В','G-C запушено 6b9943f'),
 ('Lens_governance_session_summary_GC2a_HRUPA_G.md','G-C2a: група Г; §2 — повні тексти G16-1 · Г-13 (на нього посилається CHERGA, доступ — рівень 3 драбини §8)','G-C запушено 6b9943f'),
 ('Lens_governance_session_summary_GC2b_FINAL_AUDYT.md','G-C2b: фінал злиття + аудит зв\'язності; §2 — повний текст К3-1','G-C запушено 6b9943f, §0 закрито G-C3'),
 ('Lens_session_summary_GH1_PUSH_Z_CHATU.md','GH1: протокол П-GH1, пуш з чату','гілку змерджено, B63 стартував'),
 ('GA_step2_texts_v1.md','G-A: тексти вставок В1–В9','влиті скриптом'),
 ('GB_triage_v1.md','G-B: таблиця тріажу','злиття виконано'),
 ('GB2_groupB1_texts_v1.md','G-B2: тексти Б1','влиті й пушені'),
 ('GB2_groupB2_texts_v1.md','G-B2: тексти Б2','влиті й пушені'),
 ('GB3_DA_texts_v1.md','G-B3: тексти Д-А','влиті й пушені'),
 ('GB3_DB_texts_v1.md','G-B3: тексти Д-Б','влиті й пушені'),
 ('GB3_DK_texts_v1.md','G-B3: тексти Д-К','влиті й пушені'),
 ('ga_step1_g11_v1.py','пакет G-A: G11','залито в репо'),
 ('ga_step2_insert_v1.py','пакет G-A: вставки за якорями','залито в репо'),
 ('ga_step4_index_cherga_v1.py','пакет G-A: INDEX/CHERGA','залито в репо'),
 ('g11hist.py','G-A: історія G11 (закриття IDX-6)','IDX-6 закрито'),
 ('gb_step1b_triage_v1.py','пакет G-B: тріаж','злиття виконано'),
 ('gb_step2A_merge_v1.py','пакет G-B2: група А','пушено'),
 ('gb2_step1B1_merge_v1.py','пакет G-B2: Б1','пушено'),
 ('gb2_step1B2_merge_v1.py','пакет G-B2: Б2','пушено'),
 ('gb3_step1A_merge_v1.py','пакет G-B3: А','пушено f4decb7'),
 ('gb3_step1B_merge_v1.py','пакет G-B3: Б','пушено f4decb7'),
 ('gb3_step1C_merge_v1.py','пакет G-B3: В','пушено f4decb7'),
 ('gb3_step1D_addr_v1.py','пакет G-B3: літерні адреси','пушено f4decb7'),
 ('gb3_step2_index_v1.py','пакет G-B3: INDEX','пушено f4decb7'),
 ('gc_step1A_wsd_v1.py','пакет G-C: група А','пушено 6b9943f'),
 ('gc_step1B_wsd_v1.py','пакет G-C: група Б','пушено 6b9943f'),
 ('gc_step1B2_s32ref_v1.py','пакет G-C: s32-посилання','пушено 6b9943f'),
 ('gc_step1V_wsd_v1.py','пакет G-C: група В','пушено 6b9943f'),
 ('gc_step1G_wsd_v1.py','пакет G-C: група Г','пушено 6b9943f'),
 ('gc_step2_final_v1.py','пакет G-C: фінал (wsd 2.35, Z_REGISTR, CHERGA, INDEX)','пушено 6b9943f'),
]
OLD = [('Lens_session_summary_governance_A.md','governance A (31.07)'),('Lens_session_summary_governance_B.md','governance B'),
       ('Lens_session_summary_governance_C.md','governance C'),('Lens_session_summary_governance_D.md','governance D'),
       ('Lens_session_summary_governance_E.md','governance E — лежав без рядка (§3 «втрачений»), закрито G-C3')]
changed = []
def md5(p): return hashlib.md5(open(p,'rb').read()).hexdigest()[:8]
# 1. копії
assert len(FILES) == 34, len(FILES)
for f,_,_ in FILES:
    s, d = os.path.join(SRC,f), os.path.join(DST,f)
    if not os.path.exists(s): sys.exit(f'STOP нема в Project: {f}')
    if os.path.exists(d):
        if md5(s) != md5(d): sys.exit(f'STOP інший вміст: {d}')
        continue
    shutil.copyfile(s,d); changed.append(d)
def edit(path, old, new, done_marker):
    t = open(path,encoding='utf-8').read()
    if done_marker in t: return
    n = t.count(old)
    if n != 1: sys.exit(f'STOP якір {n}× у {path}: {old[:60]!r}')
    if path.endswith('CHERGA.md') and len(t.replace(old,new).encode()) > 8000: sys.exit('STOP CHERGA > стелі 8000 (до запису)')
    open(path,'w',encoding='utf-8').write(t.replace(old,new)); changed.append(path)
# 2. ARCHIVE_INDEX
AI='kernel/Lens_ARCHIVE_INDEX.md'
sec = [f'### `archive/summaries/Lens_gov/` — {len(OLD)+len(FILES)} файлів *(заведено G-C3 {D}; шлях з підтекою — raw без `Lens_gov/` дає 404; лічильник «Разом» нижче і §2 «плоско» не перераховані — `IDX-13`)*','']
sec += [f'- `{f}` · {w}' for f,w in OLD] + ['']
sec += [f'- `{f}` · {D} · Lens governance · {w} · {c}' for f,w,c in FILES] + ['','']
edit(AI, '### `archive/stands/` — 28 файлів', '\n'.join(sec)+'### `archive/stands/` — 28 файлів', '### `archive/summaries/Lens_gov/`')
# 3. INDEX §5 рядок governance + §8 тригер
IX='kernel/Lens_INDEX.md'
edit(IX, "| **Lens** *(governance)* | `Lens_governance_session_summary_GB3_ZLYTTIA_V.md` · `Lens_governance_session_summary_GA_BUFERY.md` *(G_MASKA · F_CHERGA_PLAN · GB_TRIAZH · GB2_ZLYTTIA_B витіснені 17.09.2026)* |",
 "| **Lens** *(governance)* | `Lens_governance_session_summary_GC3_PUSH_ARCHIV.md` *(GA · GB_TRIAZH · GB2 · GB3 · GC1 · GC2a · GC2b · GH1 витіснені 17.09.2026 → `archive/summaries/Lens_gov/`)* |",
 'GC3_PUSH_ARCHIV')
edit(IX, 'буфер змерджено → ПК · самері випало з §5 → ПК · канон-файл розпиляно → репо `archive/`.',
 'буфер змерджено → ПК · самері випало з §5 → репо `archive/summaries/` (`gov 1.14`) · канон-файл розпиляно → репо `archive/`.',
 'самері випало з §5 → репо')
# 4. CHERGA
CH='kernel/Lens_governance_CHERGA.md'
edit(CH, "| `IDX-12` | **Буфери на злиття.** Стан 17.09.2026 (`G11` ✓): stagebench **0** · wsd **0** — ✅ **G-C закрито** (G-C1·C2a·C2b) · cookbook **17** → **G-D** (`A105` готовий) | 13.08.2026 | усі три буфери порожні, дельта в каноні |",
 "| `IDX-12` | **Буфери:** stagebench 0 · wsd 0 (G-C ✅) · cookbook **17** → G-D (`A105`) | 13.08.2026 | три буфери порожні |\n| `IDX-13` | **`ARCHIVE_INDEX` ⟂ дерево:** §2 «плоско» · лічильники · A–D без `Lens_gov/` · §3 ⟂ CHERGA→GC2a. Текст: самері GC3 | 17.09.2026 | = `git ls-files archive/` |",
 '`IDX-13`')
sz = len(open(CH,'rb').read())
if sz > 8000: sys.exit(f'STOP CHERGA {sz} B > стелі 8000')
print('змінено' if changed else 'no-op', len(changed), '| CHERGA', sz, 'B |', ' '.join(md5(p) for p in (AI,IX,CH)))
