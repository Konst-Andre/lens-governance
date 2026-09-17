# ga_step1_g11_v1.py · живе доки: пакет G-A залито в репо · IDX-6: шапки буферів = факт
import sys
E=[('kernel/wsd/wsd_delta_running.md',
 '**ЛОТОК: 6 записів.** *(3 покажчики + 3 повні записи)*',
 '**ЛОТОК: 10 записів.** *(4 покажчики: Г-8 · З-42 · В-15 · Г-12 + 6 повних: Г-10 · Д-7 · Д-8 · Д-9 · Д-10 · `2.13` · шапку звірено з історією комітів 17.09.2026, IDX-6)*'),
('kernel/cookbook/Lens_cookbook_delta_running.md',
 '**ЛОТОК: 14 записів.** *(2 готові A-записи + 3 покажчики + 8 покажчиків cheat-sheet S26 · + A105 HSO ✅ device-lock 16.09.2026, готовий до мерджу в том 5)*',
 '**ЛОТОК: 15 записів.** *(2 готові A-записи + 3 покажчики + 8 покажчиків cheat-sheet S26 · + `A**nn**` вебшрифт 31.08.2026 · + A105 HSO ✅ device-lock 16.09.2026, готовий до мерджу в том 5 · шапку звірено з історією комітів 17.09.2026, IDX-6)*')]
root=sys.argv[1]
for p,old,new in E:
  f=f'{root}/{p}'; b=open(f,encoding='utf-8').read()
  if new in b: print('no-op',p); continue
  n=b.count(old)
  if n!=1: sys.exit(f'СТОП {p}: якір {n}×')
  open(f,'w',encoding='utf-8').write(b.replace(old,new)); print('ok',p)
