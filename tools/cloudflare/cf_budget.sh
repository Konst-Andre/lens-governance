#!/usr/bin/env bash
# cf_budget.sh — бюджет СПІЛЬНОГО акаунта Cloudflare одним рядком (+ рядки ⚠) для env_check будь-якого репо Konst.
# живе доки: живе tools/cloudflare/CLOUDFLARE.md (звідти — ліміти, пороги, строк свіжості й дата перевірки; тут чисел нема).
# Лише ЧИТАЄ (API Cloudflare). Токен не друкує. Завжди exit 0 — бюджет не має права зламати старт сесії.
# Запуск у репо — блок із CLOUDFLARE.md §4 (не «curl | bash || echo»: на 404 збій мовчить).
# Потрібні: CLOUDFLARE_API_TOKEN (читання Pages · Workers · Account Analytics), CLOUDFLARE_ACCOUNT_ID, python3, curl.
# Перевірка зубів: CF_BUDGET_INJECT=70 — додає 70 п.п. до кожної частки → мусить надрукувати «⚠ ТРИВОГА».
set -u
tok=$(printf %s "${CLOUDFLARE_API_TOKEN:-}" | tr -d '[:space:]'); acc=$(printf %s "${CLOUDFLARE_ACCOUNT_ID:-}" | tr -d '[:space:]')
if [ -z "$tok" ] || [ -z "$acc" ]; then echo "cloudflare: — (нема CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID)"; exit 0; fi
here=$(cd "$(dirname "${BASH_SOURCE[0]:-/dev/null}")" 2>/dev/null && pwd)
if [ -n "$here" ] && [ -f "$here/CLOUDFLARE.md" ]; then doc=$(cat "$here/CLOUDFLARE.md")
else doc=$(curl -sSf -m 15 https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/tools/cloudflare/CLOUDFLARE.md 2>/dev/null); fi
[ -n "$doc" ] || { echo "cloudflare: — (CLOUDFLARE.md не прочитано)"; exit 0; }
CF_TOK="$tok" CF_ACC="$acc" CF_DOC="$doc" python3 - <<'PY' || echo "cloudflare: — (cf_budget впав; бюджет не заміряно)"
import os, re, json, datetime, urllib.request
tok, acc, doc = os.environ['CF_TOK'], os.environ['CF_ACC'], os.environ['CF_DOC']
inj = float(os.environ.get('CF_BUDGET_INJECT') or 0)
blk = re.search(r'```cf-limits\n(.*?)```', doc, re.S)
L = dict(l.split('=', 1) for l in blk.group(1).split() if '=' in l) if blk else {}
alarm = float(L.get('alarm_share', 70)); fail = float(L.get('fail_share', 90)); fresh = int(L.get('fresh_days', 30))
API = 'https://api.cloudflare.com/client/v4/accounts/' + acc
def get(url, body=None):
    rq = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
        headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(rq, timeout=20) as r: return json.load(r)
now = datetime.datetime.now(datetime.timezone.utc)
day0 = now.strftime('%Y-%m-%dT00:00:00Z'); month0 = now.strftime('%Y-%m-01')
parts, warn = [], []
def share(name, used, lim):
    if not lim: return
    p = 100.0 * used / float(lim) + inj
    mark = '✗ ' if p >= fail else ('⚠ ' if p >= alarm else '')
    parts.append(f'{mark}{name} {used}/{int(float(lim))} ({p:.0f}%)')
    if p >= alarm: warn.append(f'⚠ ТРИВОГА cloudflare: {name} — {p:.0f}% ліміту (поріг {alarm:.0f}%) · CLOUDFLARE.md §2')
# 1 · запити до воркерів сьогодні (UTC), весь акаунт
try:
    q = ('{viewer{accounts(filter:{accountTag:"%s"}){workersInvocationsAdaptive(limit:1000,filter:{datetime_geq:"%s",datetime_leq:"%s"})'
         '{sum{requests} dimensions{scriptName}}}}}') % (acc, day0, now.strftime('%Y-%m-%dT%H:%M:%SZ'))
    rows = get('https://api.cloudflare.com/client/v4/graphql', {'query': q})['data']['viewer']['accounts'][0]['workersInvocationsAdaptive']
    by = {}
    for r in rows: by[r['dimensions']['scriptName']] = by.get(r['dimensions']['scriptName'], 0) + r['sum']['requests']
    top = max(by, key=by.get) if by else '—'
    share('запити сьогодні', sum(by.values()), L.get('workers_requests_day'))
    if by: parts[-1] += f' · більше всіх {top}'
except Exception as e: parts.append('запити — не заміряно (' + type(e).__name__ + ')')
# 2 · збірки Pages цього календарного місяця + заводські налаштування
try:
    projs = get(API + '/pages/projects')['result']; total = 0; per = {}; wide = []
    for p in projs:
        n = 0
        for page in range(1, 41):
            res = get(f"{API}/pages/projects/{p['name']}/deployments?per_page=25&page={page}").get('result') or []
            n += sum(1 for d in res if d['created_on'] >= month0)
            if len(res) < 25 or (res and res[-1]['created_on'] < month0): break
        per[p['name']] = n; total += n
        c = (p.get('source') or {}).get('config') or {}
        f = [w for w, bad in (('будь-який файл', (c.get('path_includes') or ['*']) == ['*']),
                              ('усі гілки', c.get('preview_deployment_setting', 'all') == 'all')) if bad]
        if f: wide.append(p['name'] + ' (' + ' · '.join(f) + ')')
    share('збірки Pages за місяць', total, L.get('pages_builds_month'))
    if per: parts[-1] += ' · ' + ', '.join(f'{k} {v}' for k, v in sorted(per.items(), key=lambda x: -x[1]) if v)
    # прогноз на кінець місяця: темп з 1-го числа × днів у місяці
    import calendar
    dim = calendar.monthrange(now.year, now.month)[1]; lim = float(L.get('pages_builds_month') or 0)
    fc = total / max(now.day, 1) * dim
    if lim and fc + inj * lim / 100 >= lim:
        warn.append(f'⚠ ТРИВОГА cloudflare: збірки Pages — прогноз {fc:.0f}/{lim:.0f} до кінця місяця (темп {total / max(now.day, 1):.0f}/день) · CLOUDFLARE.md §2 п.1–2')
    if wide: warn.append('⚠ cloudflare: заводські збірки Pages — ' + ', '.join(wide) + ' · CLOUDFLARE.md §2 п.1–2')
except Exception as e: parts.append('збірки Pages — не заміряно (' + type(e).__name__ + ')')
parts.append('хвилини Workers Builds — не міряються (API не перевірено; дашборд)')
# 3 · свіжість правил (замкнений цикл, CLOUDFLARE.md §5)
m = re.search(r'Перевірено: (\d{4}-\d{2}-\d{2})', doc)
if m:
    age = (now.date() - datetime.date.fromisoformat(m.group(1))).days
    if age > fresh: warn.append(f'⚠ cloudflare: ліміти в CLOUDFLARE.md перевірено {age} дн. тому — звір і запропонуй правку (§5), окремим ходом')
else: warn.append('⚠ cloudflare: у CLOUDFLARE.md нема рядка «Перевірено:» — §5')
print('cloudflare: ' + ' · '.join(parts))
for w in warn: print(w)
PY
exit 0
