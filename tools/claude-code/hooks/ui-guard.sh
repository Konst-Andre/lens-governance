#!/bin/bash
# живе доки: UI-кроки (HTML/CSS) робить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (HOOK-1); копій у репо продуктів не тримати — гачки діють з ядра через setup script v3 (стара копія QR дублювала ядро старою логікою, прибрано CC-9).
# Гачок «UI без кукбука — не пиши»: правило «перед UI — індекс кукбука» тримає програма, не пам'ять моделі
# (урок QR-Lens CC-2, 08.10.2026: сторінку звіту зробили без кукбука → «дешево»).
#   mark  — PostToolUse (Read|Bash|Grep|WebSearch|WebFetch): згадано Lens_cookbook_INDEX або сам том кукбуку (AE S95) → позначка «кукбук»; WebSearch/WebFetch → позначка «пошук ззовні»
#   check — PreToolUse (Write|Edit|Bash), по черзі: (1) крок — код без пошуку ззовні з останнього коміту → deny (нижче «Крок»);
#     (2) теми — код теми без пошуку саме про неї → deny (нижче «Теми»); (3) UI — запис .html/.css (Write/Edit або Bash із записом) без обох позначок сесії → deny з причиною, що саме бракує
#   (пошук ззовні — з 10.10.2026, слово Konst: правило профілю «ПІДСИЛЕННЯ ІНТЕРНЕТОМ» модель пропускала)
# Позначки (3) — раз на сесію; позначку (1) скидає кожен коміт. Формат — code.claude.com/docs/en/hooks (08.10.2026).
mode="$1"
# Теми (QR CC-8, 11.10.2026, пропуск Konst: лічильник відвідувань зробили без розвідки — «пошук ззовні» відкривався раз на сесію, і перший пошук
# покривав усе до кінця): код, що торкається теми нижче, вимагає рецепт (де він є) і пошук ззовні САМЕ ПРО ЦЮ ТЕМУ в цій сесії — «тема → рецепт → інтернет → план».
#   Запити пошуку пишуться в /tmp/lens-ui-<сесія>-q (mark); check шукає в них слова теми. Мапа тем — TOPICS нижче; нова тема — рядок + випадок у selftest.
# Крок (QR CC-8, 11.10.2026, слово Konst: «звірка з інтернетом — загальне правило, не лише UI»): крок = від коміту до коміту. Перший запис коду в кроці
#   вимагає пошук ззовні з останнього коміту (позначка -step; git commit її скидає). Дрібний оборотний крок (опечатка, одна константа) —
#   `bash ui-guard.sh skip "<чому крок не вирішує форму, ≥ 20 знаків>"` (сесія — CLAUDE_CODE_SESSION_ID): причина пишеться в -skips, журнал гачків рахує.
if [ "$mode" = skip ]; then
  why="${2:-}"; sid="$(printf '%s' "${CLAUDE_CODE_SESSION_ID:-nosession}" | tr -cd 'A-Za-z0-9_-')"
  [ "${#why}" -ge 20 ] || { echo "✗ причина ≥ 20 знаків: чому цей крок не вирішує форму"; exit 1; }
  printf '%s\t%s\n' "$(date -u +%FT%TZ)" "$why" >> "/tmp/lens-ui-$sid-skips"; printf 'skip: %s\n' "$why" > "/tmp/lens-ui-$sid-step"
  echo "✓ крок без пошуку — причину записано (/tmp/lens-ui-$sid-skips)"; exit 0
fi
if [ "$mode" = selftest ]; then
  # зуби не залежать від теки запуску (AE S103: з кореня AE «обрані примірки» docs/shots давали 2 хибні ✗ — і на старій версії теж)
  case "$0" in /*) ;; *) exec bash "$(pwd)/$0" selftest;; esac; cd /   # не /tmp: там відносна ціль — «робочий файл»
  ok=0; n=0; S="selftest$$"; Q="/tmp/lens-ui-$S-q"; rm -f "$Q" "/tmp/lens-ui-$S" "/tmp/lens-ui-$S-web"; touch "/tmp/lens-ui-$S" "/tmp/lens-ui-$S-web" "/tmp/lens-ui-$S-step"   # теми перевіряються в кроці, де звірка вже була
  t() { n=$((n+1)); got=$(python3 -c 'import json,sys; print(json.dumps({"session_id":sys.argv[1],"tool_name":"Write","tool_input":{"file_path":sys.argv[2],"content":sys.argv[3]}}))' "$S" "$2" "$3" | bash "$0" check | grep -c '"deny"'); [ "$got" = "$1" ] && ok=$((ok+1)) || echo "✗ $4 → $got, очікував $1"; }
  t 1 admin/worker.js "self.registration.showNotification(t)" "пуш без пошуку про пуш → стоп"
  echo "пуш iOS Safari" >> "$Q"
  t 0 admin/worker.js "self.registration.showNotification(t)" "пуш після пошуку про пуш → тиша"
  t 1 tools/site.html "navigator.sendBeacon('/hit')" "лічильник, а пошук був лише про пуш → стоп"
  echo "аналітика сайту iphone" >> "$Q"
  t 0 tools/site.html "navigator.sendBeacon('/hit')" "лічильник після пошуку «аналітика» (назва теми кирилицею) → тиша"
  t 0 lens/PLAN.md "navigator.sendBeacon('/hit')" "документ (не код) → тиша"
  t 0 tools/claude-code/hooks/x.sh "showNotification sendBeacon" "файли гачків (мапа тем у тексті) → тиша"
  rm -f "/tmp/lens-ui-$S-step"
  t 1 tools/qr_build.py "x = 1" "крок без пошуку з останнього коміту → стоп"
  echo "{\"session_id\":\"$S\",\"tool_name\":\"WebSearch\",\"tool_input\":{\"query\":\"python openpyxl read merged cells\"}}" | bash "$0" mark
  t 0 tools/qr_build.py "x = 1" "після пошуку в цьому кроці → тиша"
  G="/tmp/lens-ui-$S-git"; rm -rf "$G"; mkdir -p "$G" && git -C "$G" init -q && touch "$G/a" && git -C "$G" add a && GIT_COMMITTER_DATE="2020-01-01T00:00:00" git -C "$G" -c user.email=t@t -c user.name=t commit -qm old
  echo "{\"session_id\":\"$S\",\"cwd\":\"$G\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"python3 t.py  # рядок тесту: git add -A && git commit -m x\"}}" | bash "$0" mark
  t 0 tools/qr_build.py "x = 2" "текст «git … commit» без свіжого коміту (тест, причина skip) крок не скидає → тиша"
  touch "$G/b" && git -C "$G" add b && git -C "$G" -c user.email=t@t -c user.name=t commit -qm new
  echo "{\"session_id\":\"$S\",\"cwd\":\"/\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"cd $G && git commit -m x\"}}" | bash "$0" mark
  t 1 tools/qr_build.py "x = 2" "справжній свіжий коміт (cd у репо) скинув крок → знову стоп"
  rm -rf "$G"
  CLAUDE_CODE_SESSION_ID="$S" bash "$0" skip "опечатка в рядку, форма не змінюється" >/dev/null
  t 0 tools/qr_build.py "x = 2" "пропуск із причиною → тиша"
  rm -f "/tmp/lens-ui-$S-step"
  tb() { n=$((n+1)); got=$(python3 -c 'import json,sys; print(json.dumps({"session_id":sys.argv[1],"tool_name":"Bash","tool_input":{"command":sys.argv[2]}}))' "$S" "$2" | bash "$0" check | grep -c '"deny"'); [ "$got" = "$1" ] && ok=$((ok+1)) || echo "✗ $3 → $got, очікував $1"; }
  tb 0 "python3 - <<X
p='lens/QR_Lens_CHERGA.md'; open(p,'w').write(t)
X
python3 kernel/Lens_validate.py --product ." "правка .md через python (гейт .py лише запускається) → тиша"
  tb 1 "python3 - <<X
p='tools/qr_build.py'; open(p,'w').write(t)
X" "правка .py через python без пошуку → стоп"
  t 0 /tmp/claude-0/x/scratchpad/probe.mjs "x = 1" "робочий файл у /tmp → тиша"
  S0=$S; S="${S}-clean"   # чиста сесія: без позначок «кукбук»/«пошук», інакше UI-перевірка мовчить за будь-якої логіки (зуби: на старій — ✗)
  tb 0 "python3 -c \"import json; d=json.load(open('/root/.claude/settings.json'))\"; grep -c ':root' site/index.html" "читання .html поруч з open() іншого файлу → тиша (хибне S90 AE)"
  tb 0 "cat > notes.md <<X
мітка APP_BUILD у site/index.html
X" "запис .md, що лише згадує .html → тиша (хибне S90 AE)"
  tb 1 "python3 - <<X
p='site/index.html'; open(p,'w').write(t)
X" "запис .html через python без кукбука й пошуку → стоп"
  tb 1 "echo '<b>x</b>' > site/index.html" "запис .html перенаправленням у чистій сесії → стоп"
  # AE S103: скрипт заміру в scratchpad — відносна ціль після cd /tmp, тіло heredoc (cat) з «> \$OUT/x.log», cp і .html у різних рядках → тиша
  tb 0 "cd /tmp/claude-0/x/scratchpad/speed && cat > before.sh <<'EOF'
t a node tools/a.js > \"\$OUT/a.log\" 2>&1
cp -r site \$OUT/sitecopy
t b python3 /tmp/Lens_validate.py --html site/index.html
echo DONE >> \$OUT/times.tsv
EOF
chmod +x before.sh" "скрипт заміру в /tmp: cd + heredoc cat + cp і .html у різних рядках → тиша (хибне ×3 AE S103)"
  tb 1 "cd site && cat > index.html <<X
<b>x</b>
X" "cd у репо + heredoc cat у .html → стоп (зуби S103)"
  tb 1 "cp /tmp/x/new.html site/index.html" "cp нового .html у репо → стоп (зуби S103)"
  tb 0 "cp site/index.html /tmp/x/old.html" "cp .html з репо в /tmp (база для порівняння) → тиша (S103)"
  touch "/tmp/lens-ui-$S-web" "/tmp/lens-ui-$S-step"
  tb 1 "echo '<b>x</b>' > site/index.html" "пошук є, кукбука нема → стоп"
  echo "{\"session_id\":\"$S\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"sed -n 864,889p kernel/cookbook/Lens_iOS_cookbook_3_material.md\"}}" | bash "$0" mark
  tb 0 "echo '<b>x</b>' > site/index.html" "прочитано том кукбуку (не індекс) → тиша (дубль AE S95)"
  rm -f "/tmp/lens-ui-$S" "/tmp/lens-ui-$S-web" "/tmp/lens-ui-$S-step"
  tb 0 "python3 - <<X
repo=open('worker/ae-proxy.js',encoding='utf-8').read()
X" "читання .js через open() без режиму запису → тиша (хибне S90 AE, правило «крок»)"
  tb 1 "python3 - <<X
open('tools/qr_build.py','w').write(t)
X" "open(…, 'w') у .py без пошуку → стоп"
  S=$S0
  R="/tmp/lens-ui-$S-repo"; rm -rf "$R"; mkdir -p "$R/lens/shots" && git -C "$R" init -q
  printf '| id | стан | що | в | вибір | куди | дата |\n|---|---|---|---|---|---|---|\n| `QRL-1_x` | обрано | x | x | x | x | 11.10.2026 |\n' > "$R/lens/shots/README.md"
  touch "/tmp/lens-ui-$S-step"
  echo "ui css pattern" >> "$Q"
  t 1 "$R/site.html" "<b>x</b>" "UI-код, у репо обрана примірка, README не відкривали → стоп"
  echo "{\"session_id\":\"$S\",\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$R/lens/shots/README.md\"}}" | bash "$0" mark
  t 0 "$R/site.html" "<b>x</b>" "README примірок відкрито → тиша"
  rm -rf "$R" "/tmp/lens-ui-$S-shots"
  rm -f "/tmp/lens-ui-$S-step" "/tmp/lens-ui-$S-skips" "/tmp/lens-ui-$S-shots"
  rm -f "$Q" "/tmp/lens-ui-$S" "/tmp/lens-ui-$S-web"; echo "ui-guard selftest: $ok/$n"; [ "$ok" = "$n" ]; exit
fi
python3 -c '
import json, sys, re, os
mode = sys.argv[1]
d = json.load(sys.stdin)
sid = re.sub(r"[^A-Za-z0-9_-]", "", str(d.get("session_id") or "nosession"))
mark = f"/tmp/lens-ui-{sid}"
ti = d.get("tool_input") or {}
tool = d.get("tool_name", "")
raw = json.dumps(ti, ensure_ascii=False)
web = mark + "-web"   # пошук практики ззовні (профіль ЦИКЛ п.4; слово Konst 10.10: правило, що не виконується, — програмою)
DEVNULL = r"\d?>>?&?\s*/dev/null|\d>&\d"   # 2>/dev/null, >/dev/null, 2>&1 — не запис (хибна відмова на «grep … 2>/dev/null», аудит 09.10)
TG = r"(?:\bp\s*=\s*|open\(\s*(?=[\x27\x22][^\x27\x22]+[\x27\x22]\s*,\s*(?:mode\s*=\s*)?[\x27\x22][wax])|Path\(\s*(?=[\x27\x22][^\x27\x22]+[\x27\x22]\s*\)\s*\.write)|>\s*|\btee\s+(?:-a\s+)?|sed\s+-i\S*\s+(?:\x27[^\x27]*\x27|\x22[^\x22]*\x22)\s+)[\x27\x22]?([\w./~-]+\.[A-Za-z]+)"
def segs(cmd):
    # Команда Bash → сегменти (рядок · && · || · ;) з текою, куди вказує попередній `cd` (AE S103, 24.10.2026, хибне ×3 на скрипт заміру в scratchpad:
    #   «cd /tmp/…/scratchpad && cat > before.sh <<EOF» — before.sh вважався файлом репо, а рядки тіла — записами shell).
    # Тіло heredoc для cat / tee — ВМІСТ файлу, не команди: пропускаємо. Тіло для інтерпретатора (python3 - <<X) — код, лишається (його записи справжні).
    out, lines, i = [], cmd.split("\n"), 0
    while i < len(lines):
        ln = lines[i]; out.append(ln); m = re.search(r"<<-?\s*[\x27\x22]?(\w+)[\x27\x22]?", ln); i += 1
        if m and re.search(r"\b(cat|tee)\b", ln):
            while i < len(lines) and lines[i].strip() != m.group(1): i += 1
            i += 1
    cur, res = d.get("cwd") or os.getcwd(), []
    for s in re.split(r"\n|&&|\|\||;", "\n".join(out)):
        m = re.match(r"\s*cd\s+([^\s;&|]+)\s*$", s)
        if m:
            p = os.path.expanduser(m.group(1).strip("\"\x27")); cur = os.path.normpath(p if os.path.isabs(p) else os.path.join(cur, p)); continue
        res.append((re.sub(DEVNULL, "", s), cur))
    return res
def absp(x, cur): x = os.path.expanduser(x); return os.path.normpath(x if os.path.isabs(x) else os.path.join(cur, x))
def tmp(x, cur): return absp(x, cur).startswith("/tmp/")   # робочі файли (scratchpad теж під /tmp) — не код репо
if mode == "mark":
    # «кукбук» — індекс АБО сам том (AE S95: том A117 прочитано цілком, а гачок бачив лише індекс → дубль-стоп; рецепт — у томі, індекс — лише маршрут)
    if "Lens_cookbook_INDEX" in raw or re.search(r"cookbook/Lens_\w*cookbook\w*\.md", raw):
        open(mark, "w").close()
    if "shots/README.md" in raw:
        open(mark + "-shots", "w").close()   # примірки репо переглянуто (SHOTS.md §5 «у роботі»)
    if tool == "Bash" and re.search(r"\bgit\b[^;&|]*\bcommit\b", str(ti.get("command", ""))) and os.path.exists(mark + "-step"):
        # коміт закрив крок — наступний починається зі звірки. Текст команди — лише фільтр: «git … commit» буває в тестових рядках і навіть
        # у причині skip (хибне ×3, QR CC-12 14.10.2026) → скидаємо, лише коли в репо команди останній коміт свіжий (≤ 120 с)
        import subprocess, time
        c = str(ti.get("command", ""))
        dd = [d.get("cwd") or os.getcwd()] + [x.strip("\"\x27") for x in re.findall(r"\bcd\s+(\S+)", c) + re.findall(r"\bgit\s+-C\s+(\S+)", c)]
        fresh = False
        for x in dd:
            r = subprocess.run(["git", "-C", os.path.expanduser(x), "log", "-1", "--format=%ct"], capture_output=True, text=True)
            if r.stdout.strip().isdigit() and time.time() - int(r.stdout.strip()) < 120: fresh = True; break
        if fresh or os.environ.get("UIG_INJECT") == "1": os.remove(mark + "-step")
    if tool in ("WebSearch", "WebFetch"):
        open(web, "w").close(); open(mark + "-step", "w").close()
        with open(mark + "-q", "a", encoding="utf-8") as f: f.write(str(ti.get("query") or ti.get("url") or "") + " " + str(ti.get("prompt") or "")[:200] + "\n")
    sys.exit(0)
# ── теми: код теми → рецепт + пошук саме про тему (див. шапку) ──
TOPICS = [   # (назва, слова в коді, слова в запиті пошуку, рецепт / зразок)
    ("пуш і сповіщення", r"PushManager|pushManager|showNotification|applicationServerKey|vapid", r"push|пуш|сповіщ|notif|vapid", "кукбук A111 (том 1: SW лише для пушу, свої ключі, cron, вигляд на iOS) · зразок — QR-Lens `admin/worker.js`"),
    ("service worker", r"serviceWorker\.register|self\.addEventListener\(\s*.(fetch|install|activate)", r"service.?worker|sw\.js", "зразок — QR-Lens `admin/worker.js` SW_JS (без кешу — рішення Konst 08.10)"),
    ("кеш і свіжість сторінки", r"cache-control|location\.reload\(|caches\.(open|match)|if-none-match|[\x27\x22]etag[\x27\x22]", r"cache|кеш|etag|stale|reload|свіж|fresh", "кукбук A79 (самоперевірка версії) · `kernel/modules/Lens_module_1_maint_v1.md`"),
    ("лічильник і аналітика", r"sendBeacon|[\x27\x22]/hit|cloudflareinsights|rumPageload|workersInvocationsAdaptive", r"analytic|аналіт|beacon|visit|відвід|лічильн|count|track", "`tools/cloudflare/CLOUDFLARE.md` §2 п.16 (Web Analytics з iPhone не доходить; свій лічильник)"),
]
code = ""
if tool in ("Write", "Edit"):
    fp = str(ti.get("file_path", ""))
    if re.search(r"\.(html?|m?js|ts|toml|py|sh)$", fp, re.I) and "tools/claude-code/hooks/" not in fp and not fp.startswith("/tmp/"): code = str(ti.get("content") or ti.get("new_string") or "")
elif tool == "Bash":
    cmd = str(ti.get("command", ""))
    # ціль запису — шлях після p='…' / open('…' / > / tee / sed -i; код — лише коли серед цілей є файл коду поза /tmp (правка .md через python — не код; хибне QR CC-8)
    # open: лише з режимом запису w/a/x (читання open без режиму — не запис; хибне S90 AE). Тут без апострофів: код у bash-лапках
    tg = [(x, cur) for s, cur in segs(cmd) for x in re.findall(TG, s)]
    # гачки ядра — свій цикл (selftest), не код продукту; шлях — справжній після cd (AE S103: з теки гачків «… > memory-guard.sh» вважався кодом)
    if "tools/claude-code/hooks/" not in cmd and any(re.search(r"\.(html?|m?js|ts|toml|py|sh)$", x, re.I) and not tmp(x, cur) and not os.path.dirname(absp(x, cur)).endswith("tools/claude-code/hooks") for x, cur in tg): code = cmd
if code:
    qs = open(mark + "-q", encoding="utf-8").read() if os.path.exists(mark + "-q") else ""
    miss = [(nm, rc, qw) for nm, cw, qw, rc in TOPICS if re.search(cw, code, re.I) and not re.search(qw, qs, re.I)]
    if not os.path.exists(mark + "-step"):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "Крок без звірки з інтернетом: з останнього коміту не було WebSearch / WebFetch (профіль: ЦИКЛ п.4 «підсилення інтернетом»; слово Konst — загальне правило, не лише UI). "
            "Пошукай, як цю задачу розвʼязують сьогодні (практика · що беремо · що ні + джерело з датою) — і план стане сильнішим. Дрібний оборотний крок (опечатка, одна константа) — "
            "`bash <ядро>/tools/claude-code/hooks/ui-guard.sh skip \"<чому крок не вирішує форму>\"`: причина піде в журнал."}}, ensure_ascii=False))
        sys.exit(0)
    if miss:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "Тема коду — " + "; ".join("«" + nm + "»: " + rc + " (запит пошуку має збігтися з /" + qw + "/)" for nm, rc, qw in miss) + ". Спершу рецепт / зразок, тоді пошук ззовні саме про цю тему (WebSearch / WebFetch) — "
            "як це роблять сьогодні, що в рецепті застаріло, чого ми не бачимо; зважити й скласти план — тоді код (тема → рецепт → інтернет → план; пошук про іншу тему цю не покриває)."}}, ensure_ascii=False))
        sys.exit(0)
need = [x for x, f in (("кукбук", mark), ("пошук ззовні", web)) if not os.path.exists(f)]
ui = re.compile(r"\.(html?|css)\b", re.I)
if tool in ("Write", "Edit"):
    hit = bool(ui.search(str(ti.get("file_path", ""))))
elif tool == "Bash":
    cmd = str(ti.get("command", ""))
    # UI — коли ЦІЛЬ запису .html/.css поза /tmp (ті самі цілі, що в «Крок» вище), або cp/mv, у ТОМУ Ж сегменті якого .html/.css, а ціль — не /tmp.
    # Було: .html будь-де + ознака запису будь-де → хибне S90 AE 18.10: grep site/index.html поруч із json.load(open('settings.json')) · правка env_check.sh, що лише згадує index.html;
    #   cp будь-де + .html будь-де → хибне AE S103: «cp -r site $OUT/x» в одному рядку, «--html site/index.html» в іншому.
    hit = False
    for s, cur in segs(cmd):
        if any(ui.search(x) and not tmp(x, cur) for x in re.findall(TG, s)): hit = True
        m = re.search(r"\b(cp|mv)\b(.*)", s)
        if m and ui.search(m.group(2)) and m.group(2).split() and not tmp(m.group(2).split()[-1].strip("\"\x27"), cur): hit = True
else:
    hit = False
if hit and not need and not os.path.exists(mark + "-shots"):
    # примірка (tools/claude-code/SHOTS.md §5): у репо є обране, а README примірок у сесії не відкривали → спершу подивитись обране
    import subprocess
    fp = str(ti.get("file_path", "")) if tool in ("Write", "Edit") else ""
    top = subprocess.run(["git", "-C", os.path.dirname(fp) if fp else (d.get("cwd") or "."), "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    live = []
    for dd in ("lens/shots", "docs/shots"):
        f = os.path.join(top, dd, "README.md") if top else ""
        if f and os.path.isfile(f):
            for line in open(f, encoding="utf-8"):
                c = [x.strip() for x in line.strip().strip("|").split("|")]
                if line.startswith("|") and len(c) >= 7 and c[1].strip("*").strip().lower() in ("обрано", "у роботі"):
                    live.append(dd + "/README.md " + c[0].strip("`"))
    if live:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "UI-крок, а в репо є обрані примірки: " + "; ".join(live[:4]) + ". Спершу відкрий README примірок і знімки обраного варіанта (Read — картинку видно), "
            "звір, чи цей крок їх стосується: так — код за обраним (накладка fit_* — чернетка), стан «у роботі»; ні — далі як є (tools/claude-code/SHOTS.md §5)."}}, ensure_ascii=False))
    sys.exit(0)
if hit and need:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "UI-крок (HTML/CSS) — бракує: " + " і ".join(need) + ". "
        + ("Кукбук: kernel/cookbook/Lens_cookbook_INDEX.md ядра (../lens-governance/ або /tmp/lens-governance/), §2 «задача → запис» → потрібні рецепти точково. " if "кукбук" in need else "")
        + ("Пошук ззовні (WebSearch / WebFetch): як цю задачу розв\u2019язують сьогодні — патерн, кращий за наш рецепт, чи вада, яку ми не бачимо. " if "пошук ззовні" in need else "")
        + "Рецепт — наш найкращий результат на свою дату, фундамент, а не стеля: знайшов краще — зроби краще й онови рецепт. "
        "Без цього кроку правка UI повторює вже розв\u2019язане сімейством або йде проти рецепта (HOOK-1)."}}, ensure_ascii=False))
sys.exit(0)
' "$mode"
