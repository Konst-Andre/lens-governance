# живе доки: b29.5 не витіснено наступним білдом експорту (wsd 1.8)
#
# ЩО ПОКРИВАЄ (wsd 10.10): формат, який віддається назовні, перевіряється ПАРСЕРОМ
# АДРЕСАТА, а не оком. jsdom-матриця бачить лише байти на виході buildXlsx; чи
# відкриє їх Excel і чи цілий контракт бланка — видно лише через openpyxl.
#
# ЧОГО ЦЕЙ ГЕЙТ НЕ ПОКРИВАЄ (П-20, F2.5): openpyxl — ЛІБЕРАЛЬНИЙ читач. Він
# резолвить те, що розуміє, і мовчки ігнорує посилання в нікуди між частинами
# пакета. Демо-файл b29.5 v1 пройшов його 13/13 і при цьому вимагав ремонту в
# ПК-Excel та не відкривався на iPhone. Цілісність пакета міряє окремий гейт —
# Lens_xlsx_strict.py (S1…S10). Запускати ОБИДВА, не один.
#
# Вхід: /tmp/b29_5_check.xlsx + /tmp/b29_5_expect.json — обидва пише
# StockCheck_b29_5_export.js. Запускати ОДРАЗУ після нього, у тій самій сесії.
import json, sys, datetime, openpyxl

exp = json.load(open('/tmp/b29_5_expect.json'))
wb  = openpyxl.load_workbook('/tmp/b29_5_check.xlsx')
ws  = wb['АП']
ok = bad = 0
def c(n, v):
    global ok, bad
    if v: ok += 1
    else: bad += 1
    print(('  ✓ ' if v else '  ✗ ') + n)

print('── openpyxl · файл читається як Excel ──')
c('книга відкрилась, лист «АП» на місці', ws.title == 'АП')
c('16 колонок бланка (15 + Дата візиту)', ws.max_column == 16)
c('рядків = 83 × %d БЛОКІВ + шапка' % exp['n'], ws.max_row == exp['n']*exp['total'] + 1)
c('таблиця «АП» зі стилем TableStyleMedium7',
  'АП' in ws.tables and ws.tables['АП'].tableStyleInfo.name == 'TableStyleMedium7')
c('шапка не порожня по всіх 16', all(ws.cell(1, i+1).value for i in range(16)))
c('16-та колонка названа «Дата візиту»', ws.cell(1, 16).value == 'Дата візиту')
c('ref таблиці закінчується на P', ws.tables['АП'].ref.split(':')[1].startswith('P'))

pxs = [ws.cell(r, 1).value for r in range(2, ws.max_row+1)]
c('Proxima у файлі = Proxima зрізу (жодної зайвої аптеки)', set(pxs) == set(exp['pxs']))
# О-10: дедуп ЗНЯТО — аптека тепер може повторитись, але рівно стільки разів,
# скільки блоків вона дала. Твердження b29.4 «кожна аптека рівно один раз» тут
# було б хибним ✗ на правильному файлі.
want = {p: exp['pxs'].count(p)*exp['total'] for p in set(exp['pxs'])}
c('кожна аптека × 83 × (число її візитів)',
  all(pxs.count(p) == want[p] for p in want))

# ── 16-та колонка ─────────────────────────────────────────────────────────
# ⚠ ПАСТКА (мікроскоп b29.5, Д-1/Д-2): у клітинки з датовим numFmt openpyxl
# віддає datetime, а НЕ серійне число; number_format приходить з екранованими
# крапками ('dd\\.mm\\.yyyy'). Твердження «це число» і пряме порівняння формату
# дали б ✗ на здоровому файлі — той самий клас, що TableFormula.attr_text у F2.5.
print('\n── 16-та колонка · дата ──')
d0 = ws.cell(2, 16)
c('дата прочиталась як ДАТА, не як текст і не як число',
  isinstance(d0.value, datetime.datetime))
c('формат = dd.mm.yyyy (звірка з нормалізацією бекслешів)',
  d0.number_format.replace('\\', '') == 'dd.mm.yyyy')

got = []
for b in range(exp['n']):
    r = 2 + b*exp['total']
    v = ws.cell(r, 16).value
    got.append(v.strftime('%Y-%m-%d') if isinstance(v, datetime.datetime) else v)
c('дата кожного блоку === даті візиту у зрізі', got == exp['dates'])
c('усередині блоку дата стала на ВСІ 83 рядки',
  all(ws.cell(2 + b*exp['total'] + i, 16).value == ws.cell(2 + b*exp['total'], 16).value
      for b in range(exp['n']) for i in (1, exp['total']-1)))

c('формули N/O живі структурними посиланнями',
  str(ws.cell(2,14).value).startswith('=АП[') and str(ws.cell(2,15).value).startswith('=АП['))

print("\n  ім'я файлу зрізу:", exp['fname'], '· блоків:', exp['n'], '· аптек:', exp['nph'])
print('\n✗ ПРОВАЛІВ: %d' % bad if bad else '\n✓ УСІ %d ЗЕЛЕНІ' % ok)
sys.exit(1 if bad else 0)
