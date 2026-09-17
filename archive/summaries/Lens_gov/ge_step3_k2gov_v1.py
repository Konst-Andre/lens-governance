#!/usr/bin/env python3
# живе доки: G-E3 запушено й прочитано назад — тоді archive/summaries/Lens_gov/
# G-E3: вироки К1/К2 пілоту (GE2_k2_gov_texts_v1.md) → kernel/wsd/Lens_governance_protocol.md
# 3 тригери · 5 детекторів · Ф-7 заміна «Межа» у 12.16. Прохід 1 — перевірки в пам'яті; прохід 2 — запис (Ф-4).
import sys, os, re, hashlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
TEXTS = sys.argv[2] if len(sys.argv) > 2 else '/mnt/user-data/outputs/GE2_k2_gov_texts_v1.md'
def die(m): print('STOP:', m); sys.exit(1)
p = os.path.join(ROOT, 'kernel/wsd/Lens_governance_protocol.md')
t0 = open(p, encoding='utf-8').read()
src = open(TEXTS, encoding='utf-8').read()

def block(head):
    hits = [m.start() for m in re.finditer(r'^' + re.escape(head) + r'(?: \(.*\))?$', src, re.M)]
    if len(hits) != 1: die(f'тексти: заголовок {head!r} ×{len(hits)}')
    i = hits[0]
    m = re.search(r'```\n(.*?)\n```', src[i:], re.S)
    return m.group(1)
TRIG = {n: block(f'### {n} — тригер') for n in ('12.6', '12.7', '12.8')}
DET  = {n: block(f'### {n} — детектор') for n in ('12.6', '12.7', '12.8', '12.16', '12.18')}
f7 = src[src.find('**Ф-7'):]
MEZHA_NEW = re.search(r'```\n(.*?)\n```', f7, re.S).group(1)
MEZHA_OLD = ('**Межа 🔒.** Так робиться **дописування**. **Прополка** (видалення, перенос) вимагає\n'
             'читання й окремого поштучного погодження — скриптом не робиться.')
HEAD = {
 '12.6': '## 12.6 Governance-sync: canon цитує рядок коду + device-фікс пересинхрить Cookbook у тому ж батчі',
 '12.7': '## 12.7 Канонізація компонента з коду → capture-checklist (код-точка → елемент запису)',
 '12.8': '## 12.8 Канонізувати «перенесені» залочені рішення на СТАРТІ чату + звіряти напрям deboss/emboss з кодом',
 '12.16': '## 12.16 Канон правиться скриптом за унікальним якорем, а не переписуванням у контексті',
 '12.18': '## 12.18 Два записи з різних сесій ріжуться по унікальному, а не вливаються обидва',
}

# ── прохід 1 ───────────────────────────────────────────────────────────
applied = [DET[n] in t0 for n in DET] + [TRIG[n] in t0 for n in TRIG] + [MEZHA_NEW in t0]
if all(applied):
    if t0.count(MEZHA_OLD): die('новий і старий текст «Межа» разом')
    print('no-op: усе вже застосовано'); sys.exit(0)
if any(applied): die(f'частково застосовано: {applied}')
if t0.count(MEZHA_OLD) != 1: die(f'якір «Межа» ×{t0.count(MEZHA_OLD)}')
t = t0
for n, h in HEAD.items():
    a = '\n' + h + '\n\n'
    if t.count(a) != 1: die(f'якір заголовка {n} ×{t.count(a)}')
    i = t.find(a); j = t.find('\n## ', i + len(a))
    if j < 0: die(f'кінець секції {n} не знайдено')
    sec = t[i:j]
    if n == '12.16':
        sec = sec.replace(MEZHA_OLD, MEZHA_NEW)
    if n in TRIG:
        sec = sec.replace(a, a + TRIG[n] + '\n\n', 1)
    if not sec.endswith('\n'): die(f'секція {n} не закінчується \\n')
    sec = sec + '\n' + DET[n] + '\n'
    if sec.count('**Детектор (К2).**') != 1: die(f'{n}: заголовків детектора {sec.count("**Детектор (К2).**")}')
    t = t[:i] + sec + t[j:]
if len(t.encode()) <= len(t0.encode()): die('розмір не зріс')
# ── прохід 2 ───────────────────────────────────────────────────────────
open(p, 'w', encoding='utf-8').write(t)
print('записано', os.path.relpath(p, ROOT), len(t0.encode()), '→', len(t.encode()), 'B',
      hashlib.md5(t.encode()).hexdigest()[:8])
