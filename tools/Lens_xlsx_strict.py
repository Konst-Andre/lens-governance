#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lens_xlsx_strict.py — строгий гейт цілісності xlsx-пакета.

живе доки: існує продукт сімейства Lens, що генерує xlsx власною розміткою
           (StockCheck експорт, KPI Lens / QR Lens template). Постійний інструмент.

НАВІЩО, якщо вже є openpyxl-розбір.
openpyxl — ліберальний читач: він резолвить те, що розуміє, і мовчки ігнорує
висячі посилання між частинами пакета. Excel — суворий: те саме посилання він
називає пошкодженням і ЛАГОДИТЬ файл, показавши користувачу вікно відновлення.
Тому зелений openpyxl НЕ є доказом, що Excel відкриє файл без питань.
Цей скрипт перевіряє саме міжчастинні посилання, яких openpyxl не чіпає.

ВИКОРИСТАННЯ
    python3 Lens_xlsx_strict.py <file.xlsx> [--quiet]
Код виходу: 0 — чисто · 1 — є ✗ · 2 — файл не читається.

ЩО ПЕРЕВІРЯЄ (S1…S9)
    S1  кожен Override у [Content_Types].xml вказує на наявну частину
    S2  кожна частина .xml у пакеті має оголошений Content-Type
    S3  кожен r:id у workbook.xml / worksheets/*.xml резолвиться у своєму .rels
    S4  кожен s="N" у клітинках < count(cellXfs)
    S5  кожен dxfId / dataDxfId / headerRowDxfId / totalsRowDxfId резолвиться в <dxfs>
    S6  кожен numFmtId >= 164 у cellXfs оголошений у <numFmts>
    S7  ширина table@ref == count(tableColumns); імена колонок унікальні й непорожні
    S8  table@ref не виходить за worksheet@dimension
    S9  ⚠ формульні клітинки без кешованого <v> — прев'ю-переглядачі покажуть порожньо
    S10 ⚠ пакет складено без стиснення (method=0) — файл важить у рази більше
"""
import sys, re, zipfile
from xml.etree import ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
      'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

RES = []


def ok(code, name, extra=''):
    RES.append(('ok', code, name, extra))


def bad(code, name, extra=''):
    RES.append(('bad', code, name, extra))


def warn(code, name, extra=''):
    RES.append(('warn', code, name, extra))


def col_to_num(c):
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def parse_ref(ref):
    """'A1:P250' -> (1,1,16,250)"""
    m = re.match(r'^([A-Z]+)(\d+):([A-Z]+)(\d+)$', ref or '')
    if not m:
        return None
    return (col_to_num(m.group(1)), int(m.group(2)),
            col_to_num(m.group(3)), int(m.group(4)))


def rels_path(part):
    i = part.rfind('/')
    return part[:i + 1] + '_rels/' + part[i + 1:] + '.rels'


def main(path, quiet=False):
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        print('✗ не відкривається як zip:', e)
        return 2
    names = set(z.namelist())

    def xml(p):
        return ET.fromstring(z.read(p))

    # ---------- S1 / S2 · Content_Types ----------
    ct = xml('[Content_Types].xml')
    overrides = {o.get('PartName').lstrip('/') for o in ct.findall('ct:Override', NS)}
    defaults = {d.get('Extension').lower() for d in ct.findall('ct:Default', NS)}
    miss = sorted(p for p in overrides if p not in names)
    (ok if not miss else bad)('S1', 'Override → наявна частина', ', '.join(miss))

    undeclared = []
    for n in sorted(names):
        if n.endswith('/'):
            continue
        ext = n.rsplit('.', 1)[-1].lower() if '.' in n else ''
        if n in overrides or ext in defaults:
            continue
        undeclared.append(n)
    (ok if not undeclared else bad)('S2', 'кожна частина має Content-Type', ', '.join(undeclared))

    # ---------- S3 · r:id ----------
    RID = '{%s}id' % NS['r']
    dangling = []
    for part in sorted(n for n in names if re.match(r'xl/(workbook\.xml|worksheets/[^/]+\.xml)$', n)):
        rp = rels_path(part)
        known = set()
        if rp in names:
            for rel in xml(rp).findall('pr:Relationship', NS):
                known.add(rel.get('Id'))
        for el in xml(part).iter():
            rid = el.get(RID)
            if rid and rid not in known:
                dangling.append('%s → %s' % (part, rid))
    (ok if not dangling else bad)('S3', 'r:id резолвиться у .rels', ', '.join(dangling))

    # ---------- styles ----------
    n_xf, dxf_n, numfmts = 0, 0, set()
    if 'xl/styles.xml' in names:
        st = xml('xl/styles.xml')
        cx = st.find('m:cellXfs', NS)
        n_xf = len(cx.findall('m:xf', NS)) if cx is not None else 0
        dx = st.find('m:dxfs', NS)
        dxf_n = len(dx.findall('m:dxf', NS)) if dx is not None else 0
        nf = st.find('m:numFmts', NS)
        if nf is not None:
            numfmts = {f.get('numFmtId') for f in nf.findall('m:numFmt', NS)}
        custom = []
        if cx is not None:
            for xf in cx.findall('m:xf', NS):
                nid = xf.get('numFmtId')
                if nid and int(nid) >= 164 and nid not in numfmts:
                    custom.append(nid)
        (ok if not custom else bad)('S6', 'numFmtId>=164 оголошений у <numFmts>', ', '.join(custom))

    # ---------- S4 · s="N" ----------
    over = []
    for part in sorted(n for n in names if n.startswith('xl/worksheets/') and n.endswith('.xml')):
        for s in set(re.findall(r'\ss="(\d+)"', z.read(part).decode('utf8', 'replace'))):
            if int(s) >= n_xf:
                over.append('%s: s=%s (cellXfs=%d)' % (part, s, n_xf))
    (ok if not over else bad)('S4', 's="N" < count(cellXfs)', '; '.join(over))

    # ---------- S5 · dxfId ----------
    bad_dxf = []
    for part in sorted(n for n in names if n.endswith('.xml')):
        body = z.read(part).decode('utf8', 'replace')
        for attr, val in re.findall(r'(\w*[Dd]xfId)="(\d+)"', body):
            if int(val) >= dxf_n:
                bad_dxf.append('%s: %s=%s (dxfs=%d)' % (part, attr, val, dxf_n))
    (ok if not bad_dxf else bad)('S5', 'dxfId резолвиться в <dxfs>', '; '.join(bad_dxf))

    # ---------- S7 / S8 · таблиці ----------
    t_err, d_err = [], []
    sheet_dim = {}
    for part in sorted(n for n in names if n.startswith('xl/worksheets/') and n.endswith('.xml')):
        d = xml(part).find('m:dimension', NS)
        if d is not None:
            sheet_dim[part] = parse_ref(d.get('ref'))
    # таблиця → аркуш через .rels
    tbl_owner = {}
    for part in sheet_dim:
        rp = rels_path(part)
        if rp in names:
            for rel in xml(rp).findall('pr:Relationship', NS):
                tgt = rel.get('Target', '')
                if 'tables/' in tgt:
                    tbl_owner['xl/' + tgt.replace('../', '')] = part
    for part in sorted(n for n in names if n.startswith('xl/tables/') and n.endswith('.xml')):
        t = xml(part)
        ref = parse_ref(t.get('ref'))
        cols = t.find('m:tableColumns', NS)
        lst = cols.findall('m:tableColumn', NS) if cols is not None else []
        if ref is None:
            t_err.append('%s: ref нечитабельний' % part)
            continue
        width = ref[2] - ref[0] + 1
        if width != len(lst):
            t_err.append('%s: ref ширина %d != tableColumns %d' % (part, width, len(lst)))
        if cols is not None and cols.get('count') and int(cols.get('count')) != len(lst):
            t_err.append('%s: count=%s != фактично %d' % (part, cols.get('count'), len(lst)))
        nm = [c.get('name') for c in lst]
        if any(not x for x in nm):
            t_err.append('%s: порожнє ім\'я колонки' % part)
        if len(set(nm)) != len(nm):
            t_err.append('%s: неунікальні імена колонок' % part)
        owner = tbl_owner.get(part)
        dim = sheet_dim.get(owner)
        if dim and (ref[0] < dim[0] or ref[1] < dim[1] or ref[2] > dim[2] or ref[3] > dim[3]):
            d_err.append('%s: ref за межами dimension аркуша %s' % (part, owner))
    (ok if not t_err else bad)('S7', 'ref ширина == tableColumns, імена унікальні', '; '.join(t_err))
    (ok if not d_err else bad)('S8', 'table@ref ⊆ worksheet@dimension', '; '.join(d_err))

    # ---------- S9 · кешовані значення формул ----------
    nof = 0
    for part in sorted(n for n in names if n.startswith('xl/worksheets/') and n.endswith('.xml')):
        body = z.read(part).decode('utf8', 'replace')
        nof += len(re.findall(r'<f>[^<]*</f>\s*</c>', body))
    (ok if nof == 0 else warn)('S9', 'формули мають кешоване <v>',
                               '' if nof == 0 else '%d клітинок без <v> — прев\'ю покаже порожньо' % nof)

    # ---------- S10 · стиснення ----------
    infos = [i for i in z.infolist() if not i.filename.endswith('/')]
    stored = [i for i in infos if i.compress_type == 0 and i.file_size > 4096]
    raw = sum(i.file_size for i in infos)
    packed = sum(i.compress_size for i in infos)
    if not stored:
        ok('S10', 'пакет стиснено', '%d KB → %d KB' % (raw // 1024, packed // 1024))
    else:
        warn('S10', 'частини без стиснення (method=0)',
             '%s · %d KB могли б бути ~%d KB'
             % (', '.join(i.filename for i in stored), raw // 1024, raw // 1024 // 9))

    # ---------- вивід ----------
    sym = {'ok': '✓', 'bad': '✗', 'warn': '⚠'}
    if not quiet:
        for st, code, name, extra in RES:
            print('%s %-3s %s%s' % (sym[st], code, name, ('  → ' + extra) if extra else ''))
    n_bad = sum(1 for r in RES if r[0] == 'bad')
    n_warn = sum(1 for r in RES if r[0] == 'warn')
    print('\n%s  ✓%d ⚠%d ✗%d' % (path.rsplit('/', 1)[-1],
                                 sum(1 for r in RES if r[0] == 'ok'), n_warn, n_bad))
    return 1 if n_bad else 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], '--quiet' in sys.argv))
