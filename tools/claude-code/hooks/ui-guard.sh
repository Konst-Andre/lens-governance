#!/bin/bash
# живе доки: UI-кроки (HTML/CSS) робить агент Claude Code. Дім — lens-governance:tools/claude-code/hooks/ (HOOK-1); копії в репо — як є.
# Гачок «UI без кукбука — не пиши»: правило «перед UI — індекс кукбука» тримає програма, не пам'ять моделі
# (урок QR-Lens CC-2, 08.10.2026: сторінку звіту зробили без кукбука → «дешево»).
#   mark  — PostToolUse (Read|Bash|Grep|WebSearch|WebFetch): згадано Lens_cookbook_INDEX → позначка «кукбук»; WebSearch/WebFetch → позначка «пошук ззовні»
#   check — PreToolUse (Write|Edit|Bash): запис .html/.css (Write/Edit або Bash із записом) без обох позначок → deny з причиною, що саме бракує
#   (пошук ззовні — з 10.10.2026, слово Konst: правило профілю «ПІДСИЛЕННЯ ІНТЕРНЕТОМ» модель пропускала; раз на сесію, як і кукбук)
# Раз на сесію: після одного звернення до індексу все дозволено. Формат — code.claude.com/docs/en/hooks (08.10.2026).
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
  ok=0; n=0; S="selftest$$"; Q="/tmp/lens-ui-$S-q"; rm -f "$Q" "/tmp/lens-ui-$S" "/tmp/lens-ui-$S-web"; touch "/tmp/lens-ui-$S" "/tmp/lens-ui-$S-web" "/tmp/lens-ui-$S-step"   # теми перевіряються в кроці, де звірка вже була
  t() { n=$((n+1)); got=$(python3 -c 'import json,sys; print(json.dumps({"session_id":sys.argv[1],"tool_name":"Write","tool_input":{"file_path":sys.argv[2],"content":sys.argv[3]}}))' "$S" "$2" "$3" | bash "$0" check | grep -c '"deny"'); [ "$got" = "$1" ] && ok=$((ok+1)) || echo "✗ $4 → $got, очікував $1"; }
  t 1 admin/worker.js "self.registration.showNotification(t)" "пуш без пошуку про пуш → стоп"
  echo "web push ios safari vapid" >> "$Q"
  t 0 admin/worker.js "self.registration.showNotification(t)" "пуш після пошуку про пуш → тиша"
  t 1 tools/site.html "navigator.sendBeacon('/hit')" "лічильник, а пошук був лише про пуш → стоп"
  t 0 lens/PLAN.md "navigator.sendBeacon('/hit')" "документ (не код) → тиша"
  t 0 tools/claude-code/hooks/x.sh "showNotification sendBeacon" "файли гачків (мапа тем у тексті) → тиша"
  rm -f "/tmp/lens-ui-$S-step"
  t 1 tools/qr_build.py "x = 1" "крок без пошуку з останнього коміту → стоп"
  echo "{\"session_id\":\"$S\",\"tool_name\":\"WebSearch\",\"tool_input\":{\"query\":\"python openpyxl read merged cells\"}}" | bash "$0" mark
  t 0 tools/qr_build.py "x = 1" "після пошуку в цьому кроці → тиша"
  echo "{\"session_id\":\"$S\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git commit -m x\"}}" | bash "$0" mark
  t 1 tools/qr_build.py "x = 2" "коміт скинув крок → знову стоп"
  CLAUDE_CODE_SESSION_ID="$S" bash "$0" skip "опечатка в рядку, форма не змінюється" >/dev/null
  t 0 tools/qr_build.py "x = 2" "пропуск із причиною → тиша"
  rm -f "/tmp/lens-ui-$S-step" "/tmp/lens-ui-$S-skips"
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
if mode == "mark":
    if "Lens_cookbook_INDEX" in raw:
        open(mark, "w").close()
    if tool == "Bash" and re.search(r"\bgit\b[^;&|]*\bcommit\b", str(ti.get("command", ""))) and os.path.exists(mark + "-step"):
        os.remove(mark + "-step")   # коміт закрив крок — наступний починається зі звірки
    if tool in ("WebSearch", "WebFetch"):
        open(web, "w").close(); open(mark + "-step", "w").close()
        with open(mark + "-q", "a", encoding="utf-8") as f: f.write(str(ti.get("query") or ti.get("url") or "") + " " + str(ti.get("prompt") or "")[:200] + "\n")
    sys.exit(0)
# ── теми: код теми → рецепт + пошук саме про тему (див. шапку) ──
TOPICS = [   # (назва, слова в коді, слова в запиті пошуку, рецепт / зразок)
    ("пуш і сповіщення", r"PushManager|pushManager|showNotification|applicationServerKey|vapid", r"push|сповіщ|notif|vapid", "зразок — QR-Lens `admin/worker.js` (крок 4-а: SW лише для пушу, RFC 8291/8292); рецепт кукбука — після кроку 4"),
    ("service worker", r"serviceWorker\.register|self\.addEventListener\(\s*.(fetch|install|activate)", r"service.?worker|sw\.js", "зразок — QR-Lens `admin/worker.js` SW_JS (без кешу — рішення Konst 08.10)"),
    ("кеш і свіжість сторінки", r"cache-control|location\.reload\(|caches\.(open|match)|if-none-match|[\x27\x22]etag[\x27\x22]", r"cache|кеш|etag|stale|reload|свіж|fresh", "кукбук A79 (самоперевірка версії) · `kernel/modules/Lens_module_1_maint_v1.md`"),
    ("лічильник і аналітика", r"sendBeacon|[\x27\x22]/hit|cloudflareinsights|rumPageload|workersInvocationsAdaptive", r"analytic|beacon|visit|відвід|лічильн|count|track", "`tools/cloudflare/CLOUDFLARE.md` §2 п.16 (Web Analytics з iPhone не доходить; свій лічильник)"),
]
code = ""
if tool in ("Write", "Edit"):
    fp = str(ti.get("file_path", ""))
    if re.search(r"\.(html?|m?js|ts|toml|py|sh)$", fp, re.I) and "tools/claude-code/hooks/" not in fp: code = str(ti.get("content") or ti.get("new_string") or "")
elif tool == "Bash":
    cmd = str(ti.get("command", ""))
    if "tools/claude-code/hooks/" not in cmd and re.search(r"(>|\btee\b|sed\s+-i|\.write|open\()", re.sub(r"\d?>>?&?\s*/dev/null|\d>&\d", "", cmd)): code = cmd
if code:
    qs = open(mark + "-q", encoding="utf-8").read() if os.path.exists(mark + "-q") else ""
    miss = [(nm, rc, qw) for nm, cw, qw, rc in TOPICS if re.search(cw, code, re.I) and not re.search(qw, qs, re.I)]
    if not os.path.exists(mark + "-step"):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "Крок без звірки з інтернетом: з останнього коміту не було WebSearch / WebFetch (профіль: ЦИКЛ п.4 «підсилення інтернетом»; слово Konst 11.10 — загальне правило, не лише UI). "
            "Пошукай, як цю задачу розвʼязують сьогодні (практика · що беремо · що ні + джерело з датою) — і план стане сильнішим. Дрібний оборотний крок (опечатка, одна константа) — "
            "`bash <ядро>/tools/claude-code/hooks/ui-guard.sh skip \"<чому крок не вирішує форму>\"`: причина піде в журнал."}}, ensure_ascii=False))
        sys.exit(0)
    if miss:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "Тема коду — " + "; ".join(f"«{nm}»: {rc}" for nm, rc, _ in miss) + ". Спершу рецепт / зразок, тоді пошук ззовні САМЕ ПРО ЦЮ ТЕМУ (WebSearch, запит зі словами теми) — "
            "як це роблять сьогодні, що в рецепті застаріло, чого ми не бачимо; зважити й скласти план — тоді код (тема → рецепт → інтернет → план; одного пошуку на сесію мало — QR CC-8, лічильник без розвідки)."}}, ensure_ascii=False))
        sys.exit(0)
need = [x for x, f in (("кукбук", mark), ("пошук ззовні", web)) if not os.path.exists(f)]
if not need:
    sys.exit(0)
ui = re.compile(r"\.(html?|css)\b", re.I)
if tool in ("Write", "Edit"):
    hit = bool(ui.search(str(ti.get("file_path", ""))))
elif tool == "Bash":
    cmd = str(ti.get("command", ""))
    w = re.sub(r"\d?>>?&?\s*/dev/null|\d>&\d", "", cmd)   # 2>/dev/null, >/dev/null, 2>&1 — не запис (хибна відмова на «grep … 2>/dev/null», аудит 09.10)
    hit = bool(ui.search(cmd)) and bool(re.search(r"(>|\btee\b|\bcp\b|\bmv\b|sed\s+-i|\.write|open\()", w))
else:
    hit = False
if hit:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "UI-крок (HTML/CSS) — бракує: " + " і ".join(need) + ". "
        + ("Кукбук: kernel/cookbook/Lens_cookbook_INDEX.md ядра (../lens-governance/ або /tmp/lens-governance/), §2 «задача → запис» → потрібні рецепти точково. " if "кукбук" in need else "")
        + ("Пошук ззовні (WebSearch / WebFetch): як цю задачу розв\u2019язують сьогодні — патерн, кращий за наш рецепт, чи вада, яку ми не бачимо. " if "пошук ззовні" in need else "")
        + "Рецепт — наш найкращий результат на свою дату, фундамент, а не стеля: знайшов краще — зроби краще й онови рецепт. "
        "Без цього кроку правка UI повторює вже розв\u2019язане сімейством або йде проти рецепта (HOOK-1)."}}, ensure_ascii=False))
sys.exit(0)
' "$mode"
