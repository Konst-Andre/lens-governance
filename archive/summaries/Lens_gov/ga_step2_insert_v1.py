# ga_step2_insert_v1.py · живе доки: пакет G-A залито в репо · вставки В1–В9 за якорями (gov 12.16)
import re,sys
root=sys.argv[1]; T=open('GA_step2_texts_v1.md',encoding='utf-8').read()
S={k:v.strip('\n') for k,v in re.findall(r'^## (В\d) ·[^\n]*\n(.*?)(?=^## В\d ·|^---\n\n## Шапки|\Z)',T,re.M|re.S)}
S={k:re.sub(r'\n+---\s*$','',v).strip('\n') for k,v in S.items()}
assert sorted(S)==['В1','В2','В3','В4','В5','В6','В7','В8','В9'], sorted(S)
def rd(p): return open(f'{root}/{p}',encoding='utf-8').read()
def wr(p,b): open(f'{root}/{p}','w',encoding='utf-8').write(b)
def one(b,a,p):
    n=b.count(a)
    if n!=1: sys.exit(f'СТОП {p}: якір {n}× :: {a[:50]}')
MARK='preview-as-stand'
M='kernel/Lens_stagebench_manifest.md'; b=rd(M)
if MARK in b: print('no-op',M)
else:
    a1=[l for l in b.split('\n') if l.startswith('| **phone-single-frame** |')]; assert len(a1)==1; a1=a1[0]; one(b,a1,M)
    b=b.replace(a1,a1+'\n'+S['В1'])
    a2=[l for l in b.split('\n') if l.startswith('*Прецедент: StockCheck materiality-bench, 22.07.2026')]; assert len(a2)==1; a2=a2[0]; one(b,a2,M)
    b=b.replace(a2,a2+'\n\n'+S['В2'])
    a3='  для рішень, де device-feel і є питанням'; l3=[l for l in b.split('\n') if l.startswith(a3)]; assert len(l3)==1; one(b,l3[0],M)
    b=b.replace(l3[0],l3[0]+'\n'+S['В3'])
    a4='\n### 8.10 Пастки середовища'; one(b,a4,M)
    b=b.replace(a4,'\n'+S['В4']+'\n'+a4)
    wr(M,b); print('ok',M)
def app(p,keys,old,new):
    b=rd(p)
    if S[keys[0]].split('\n')[0] in b: print('no-op',p); return
    one(b,old,p); b=b.replace(old,new)
    b=b.rstrip('\n')+'\n\n---\n\n'+'\n\n---\n\n'.join(S[k] for k in keys)+'\n'
    wr(p,b); print('ok',p)
app('kernel/Lens_stagebench_delta_running.md',['В5','В6'],'**ЛОТОК: 13 запис(ів).** *(5 старих + 2 покажчики + 4 з S25 + 1 з S26 + 1 з governance 30.08 — `Д-К`;',
    '**ЛОТОК: 15 запис(ів).** *(5 старих + 2 покажчики + 4 з S25 + 1 з S26 + 1 з governance 30.08 — `Д-К` + 2 з governance G-A 17.09 — `Д-Л` · `Д-М`;')
app('kernel/cookbook/Lens_cookbook_delta_running.md',['В7','В8'],'**ЛОТОК: 15 записів.** *(','**ЛОТОК: 17 записів.** *(`A106` · `A107` з governance G-A 17.09.2026 · ')
X='kernel/Lens_excel_protocol.md'; b=rd(X)
if '/*__EXPORT_DATE__*/' in b: print('no-op',X)
else:
    old=[l for l in b.split('\n') if l.startswith('Регенерація = замінити весь рядок `const DATA = [...];`')]; assert len(old)==1; one(b,old[0],X)
    wr(X,b.replace(old[0],S['В9'])); print('ok',X)
