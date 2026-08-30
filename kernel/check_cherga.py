#!/usr/bin/env python3
"""Детектор прополки черг. Живе доки: черги EquipLens/governance живі.
   К2: ловить загублений id, перетин черг, порожній крок, вихід за стелю."""
import re, os, sys
CEIL = 8192
def ids(txt):
    out=[]
    for line in txt.splitlines():
        if not line.startswith('|'): continue
        for c in [x.strip() for x in line.strip('|').split('|')][:2]:
            m=re.fullmatch(r'`([^`]+)`',c)
            if m: out.append(m.group(1)); break
    return out
def norm(i):
    """К11-п.3 → К11 · К12·Н-10 → К12. НЕ чіпає `К2-1`: продуктовий `К2`
       (DARK-шейдинг) і governance `К2-1` (правила без детектора) — різні предмети,
       зрізання цифри після дефіса злило б їх у хибний перетин."""
    return re.sub(r'(·.*|-п\.\d+)$', '', i)

old=open(sys.argv[1],encoding='utf-8').read()
new=open(sys.argv[2],encoding='utf-8').read()
gov=open(sys.argv[3],encoding='utf-8').read()
O,N,G=set(ids(old)),set(ids(new)),set(ids(gov))
znyato=set(re.findall(r'`([^`]+)`',new.split('## Знято')[1])) if '## Знято' in new else set()
Nn={norm(i) for i in N}; Gn={norm(i) for i in G}; Zn={norm(i) for i in znyato}
bad=[]
x=sorted(Nn&Gn);                    bad += [f'id у двох чергах: {i}' for i in x]
lost=sorted(i for i in O if norm(i) not in Nn|Gn|Zn)
bad += [f'загублений id: {i}' for i in lost]
steps=set(re.findall(r'\|\s*\*\*(\d)\*\*\s*\|',new))
bad += [f'крок без id: {s}' for s in '123456789' if s not in steps]
for f in sys.argv[2:4]:
    n=os.path.getsize(f)
    if n>CEIL: bad += [f'стеля: {f} = {n} B > {CEIL}']
print('[CHERGA]', '✗ '+str(len(bad)) if bad else f'✓ вхід {len(O)} · вихід {len(N)} · gov {len(G)} · знято {len(Zn)}')
for b in bad: print('  ✗', b)
sys.exit(1 if bad else 0)
