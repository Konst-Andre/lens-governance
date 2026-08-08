# живе доки: b29.4 не витіснено наступним білдом експорту (wsd 1.8)
#
# ЩО ПОКРИВАЄ (wsd 10.10): формат, який віддається назовні, перевіряється ПАРСЕРОМ
# АДРЕСАТА, а не оком. jsdom-матриця бачить лише байти на виході buildXlsx; чи
# відкриє їх Excel і чи цілий контракт бланка — видно лише через openpyxl.
#
# Вхід: /tmp/b29_4_check.xlsx + /tmp/b29_4_expect.json — обидва пише
# StockCheck_b29_4_export.js. Запускати ОДРАЗУ після нього, у тій самій сесії.
import json, sys, openpyxl

exp = json.load(open('/tmp/b29_4_expect.json'))
wb  = openpyxl.load_workbook('/tmp/b29_4_check.xlsx')
ws  = wb['АП']
ok = bad = 0
def c(n, v):
    global ok, bad
    if v: ok += 1
    else: bad += 1
    print(('  ✓ ' if v else '  ✗ ') + n)

print('── openpyxl · файл читається як Excel ──')
c('книга відкрилась, лист «АП» на місці', ws.title == 'АП')
c('15 колонок бланка', ws.max_column == 15)
c('рядків = 83 × %d аптек + шапка' % exp['n'], ws.max_row == exp['n']*exp['total'] + 1)
c('таблиця «АП» зі стилем TableStyleMedium7',
  'АП' in ws.tables and ws.tables['АП'].tableStyleInfo.name == 'TableStyleMedium7')
c('шапка не порожня по всіх 15', all(ws.cell(1, i+1).value for i in range(15)))
pxs = set(ws.cell(r, 1).value for r in range(2, ws.max_row+1))
# ГОЛОВНЕ твердження R5: у файлі рівно ті аптеки, що були на екрані — ні більше, ні менше
c('Proxima у файлі = Proxima зрізу (жодної зайвої аптеки)', pxs == set(exp['pxs']))
# ГОЛОВНЕ твердження О-9: дедуп дійшов до файлу, а не лишився в моделі
c('кожна аптека рівно один раз × 83 (дедуп дійшов до файлу)',
  all(sum(1 for r in range(2, ws.max_row+1) if ws.cell(r,1).value == p) == exp['total'] for p in pxs))
c('формули N/O живі структурними посиланнями',
  str(ws.cell(2,14).value).startswith('=АП[') and str(ws.cell(2,15).value).startswith('=АП['))

print("\n  ім'я файлу зрізу:", exp['fname'])
print('\n✗ ПРОВАЛІВ: %d' % bad if bad else '\n✓ УСІ %d ЗЕЛЕНІ' % ok)
sys.exit(1 if bad else 0)
