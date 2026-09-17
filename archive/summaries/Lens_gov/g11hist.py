import re,subprocess,sys,urllib.request
R='https://raw.githubusercontent.com/Konst-Andre/lens-governance/{}/{}'
H={'wsd':('kernel/wsd/wsd_delta_running.md','7d70844 bd829f7 29d51f2 e4993b6 dfe2d55 a631bfe 40b5d23 912472a 0b828e6 bd0858a'),
   'cb':('kernel/cookbook/Lens_cookbook_delta_running.md','d3fe019 e315072 e4993b6 8cd4cb4 f5a44f1 3f5673c bd0858a')}
for k,(p,shas) in H.items():
  print('==',k)
  for s in shas.split():
    try: b=urllib.request.urlopen(R.format(s,p)).read().decode()
    except Exception as e:
      # older path before kernel reshuffle
      print(s,'нема за шляхом'); continue
    hs=[h for h in re.findall(r'^## (.+)$',b,re.M) if not re.match(r'[✅🟡🔴⬜🗄]|Спорожнено|Відкриті|ЗАКРИТО',h.strip())]
    d=re.search(r'ЛОТОК:\s*(\d+)',b)
    print(s,'оголош',d.group(1) if d else '-','факт',len(hs),'|',' · '.join(h.split('·')[0].strip()[:10] for h in hs))
