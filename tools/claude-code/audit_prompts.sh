#!/usr/bin/env bash
# Аудит інструкцій за класом правки: /doctor prompt-audit моделями, названими явно псевдонімами (завжди найновіша версія).
# Клас 1 — opus --effort high · клас 2 — ще й sonnet --effort high · клас 0 — аудиту нема (скрипт не потрібен).
# AUDIT_THIRD=fable — ще прохід ЛИШЕ за явним словом Konst (Fable — за реальні кошти, 04.10.2026).
# Формула (клас, пакет, перед запуском) — lens-governance:tools/claude-code/templates/AUDIT_template.md «Коли і скільки» (AUD-2).
#
# живе доки: інструкції агента перевіряються аудитом Claude Code. Зразок: lens-governance:tools/claude-code/ — копіювати в tools/ репо як є
# (frame_check ядра порівнює копію з зразком: різниця — ⚠).
#
# Запуск:  bash tools/audit_prompts.sh <1|2> <файл> [<файл> …]      (шлях — від кореня репо, у якому лежить файл)
# Файл — лише в теці репо: дочірній claude -p не читає /tmp і скретчпад батька (доступ відхилено → аудит порожній; QR CC-9, 11.10.2026).
#          Розділ великого тому — витяг у <репо>/.audit_tmp/, після аудиту теку прибрати (репо ядра публічне; untracked-тека дає ✗ гейта --gov).
# Звіти:   $AUDIT_OUT (за замовчуванням /tmp/audit)/<ім'я>.<модель>.txt (+ .json — сирий вивід) — у репо не комітяться.
# Проходи — ПО ЧЕРЗІ (opus першим); перша відповідь з «limit» або помилкою — стоп, решта не запускається.
# Вартість кожного проходу ($, токени, хвилини) — у підсумку → у колонку «проходи» журналу аудиту.
# Аудит нічого не міняє. Синтез робить агент: знахідка обох моделей — висока впевненість; однієї — звірити грепом;
# застосовується лише підтверджене і лише після «так» Konst; рядок — у журнал аудиту репо (шлях — у CLAUDE.md репо).
# Потрібен Claude Code ≥ 2.1.283 (/doctor prompt-audit).
set -u
cls="${1:-}"; shift || true
case "$cls" in 1) models="opus";; 2) models="opus sonnet";; *) echo "перший аргумент — клас правки 1 або 2 (клас 0 — без аудиту)"; exit 2;; esac
[ -n "${AUDIT_THIRD:-}" ] && models="$models $AUDIT_THIRD"
[ $# -ge 1 ] || { echo "вкажіть файл(и)"; exit 2; }
for f in "$@"; do [ -f "$f" ] || { echo "нема файла: $f"; exit 2; }; done
OUT="${AUDIT_OUT:-/tmp/audit}"; mkdir -p "$OUT"
# Аудит зі світом і з руками — типовий з 19.10.2026 (AUD-5, A/B AE S94 на AE CLAUDE.md, opus high: старий $1.47 — 0 знахідок, 2 докази, 0 джерел;
# зі світом $1.56 — 4 знахідки (хибних 0), 15 доказів `файл:рядок`, 8 зовнішніх тверджень звірено з документацією). Аудитор: лише читання
# (Read · Grep · Glob · git log/blame/show/ls-files/diff · grep · ls · wc) + WebSearch · WebFetch; решта — тиха відмова (dontAsk); стеля $ на прохід;
# ядро поруч — доступ на читання (--add-dir); правила — lens-governance:tools/claude-code/templates/AUDIT_world_prompt.md. AUDIT_WORLD=0 — старий режим.
# Після проходу — машинна перевірка доказів `файл:рядок` (практика 2026: знахідка з доказом + детермінована перевірка доказу).
world=()
if [ "${AUDIT_WORLD:-1}" != 0 ]; then
  sd="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  wp=$(for c in "$sd/templates" "$sd/../../lens-governance/tools/claude-code/templates" "$PWD/../lens-governance/tools/claude-code/templates" /tmp/lens-governance/tools/claude-code/templates; do
         [ -f "$c/AUDIT_world_prompt.md" ] && { echo "$c/AUDIT_world_prompt.md"; break; }; done)
  if [ -z "$wp" ]; then echo "⚠ правил аудитора (AUDIT_world_prompt.md) не знайдено — ядро не поруч; аудит у старому режимі"
  else
    kd="$(cd "$(dirname "$wp")/../../.." && pwd)"
    # --setting-sources "": без наших налаштувань — гачки (профіль, env_check, ui-guard, Stop) аудиторові не потрібні й заважають; вхід (OAuth) не чіпає,
    # на відміну від --bare (лише ANTHROPIC_API_KEY — у контейнері нема). Замір haiku 19.10: запис у кеш на старті 17.9 → 6.9 тис. ток., профілю в контексті нема.
    world=(--setting-sources "" --tools "Read,Grep,Glob,Bash,WebSearch,WebFetch" --permission-mode dontAsk --max-budget-usd "${AUDIT_BUDGET:-4}"
           --allowedTools "Read" "Grep" "Glob" "WebSearch" "WebFetch" "Bash(git log:*)" "Bash(git blame:*)" "Bash(git show:*)" "Bash(git ls-files:*)" "Bash(git diff:*)" "Bash(grep:*)" "Bash(ls:*)" "Bash(wc:*)"
           --append-system-prompt "$(cat "$wp")")
    [ "$kd" != "$(pwd -P)" ] && world+=(--add-dir "$kd")
  fi
fi
total=0
for f in "$@"; do
  n=$(echo "$f" | tr '/' '_')
  for m in $models; do
    eff="--effort high"   # sonnet теж high: 06.10 на wsd знайшов ядро знахідок opus за пів ціни; без --effort думав у 7 разів менше
    timeout 1500 claude -p --model "$m" $eff "${world[@]}" --output-format json "/doctor prompt-audit $f" > "$OUT/$n.$m.json" 2> "$OUT/$n.$m.err"   # stderr окремо: попередження CLI (06.10: «Ignoring … permissions») ламали JSON
    line=$(python3 - "$OUT/$n.$m.json" "$OUT/$n.$m.txt" <<'PY'
import json, sys
raw = open(sys.argv[1], encoding='utf-8', errors='replace').read()
try:
    d = json.loads(raw)
except ValueError:
    err = open(sys.argv[1][:-5] + '.err', encoding='utf-8', errors='replace').read() if raw.strip() == '' else raw
    open(sys.argv[2], 'w').write(raw); print('ERR не JSON —', err.strip()[-160:].replace('\n', ' ')); sys.exit()
res = d.get('result') or ''
open(sys.argv[2], 'w').write(res)
u = d.get('usage', {}); tok = sum(u.get(k) or 0 for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))
bad = d.get('is_error') or (len(res) < 400 and 'limit' in res.lower())   # коротка відповідь про ліміт ≠ звіт, що згадує «limit»
print(('ERR ' if bad else 'OK ') + f"${d.get('total_cost_usd', 0):.2f} · вхід {tok // 1000} тис. ток · вихід {(u.get('output_tokens') or 0) // 1000} тис. · {(d.get('duration_ms') or 0) // 60000} хв")
PY
)
    echo "$f · $m → $OUT/$n.$m.txt · ${line#* }"
    # докази: кожне `файл:рядок` у звіті — файл є, рядок існує (детермінована перевірка; пошук роздуває хибні — HALLMARK 2026)
    python3 - "$OUT/$n.$m.txt" "$OUT/$n.$m.json" <<'PY'
import re, sys, os, json, collections
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read()
refs = set(re.findall(r'`([\w./-]+\.\w+):(\d+)(?:[–-]\d+)?`', txt)); bad = []
for f, n in refs:
    p = f if os.path.isfile(f) else next((x for x in (os.path.join(r, f) for r in ('.', '..')) if os.path.isfile(x)), None)
    if not p:   # коротке ім'я без теки — шукаємо серед файлів репо (лише однозначне)
        c = [x for x in os.popen('git ls-files').read().split('\n') if x == f or x.endswith('/' + f)]; p = c[0] if len(c) == 1 else None
    if not p or int(n) > sum(1 for _ in open(p, encoding='utf-8', errors='replace')): bad.append(f'{f}:{n}')
try:
    d = json.load(open(sys.argv[2], encoding='utf-8')); den = collections.Counter(x['tool_name'] for x in d.get('permission_denials') or [])
except Exception:
    den = {}
print(f'   докази: посилань `файл:рядок` {len(refs)}, зламаних {len(bad)}' + (' — ' + ' · '.join(sorted(bad)[:6]) if bad else '') +
      f' · вебадрес {len(set(re.findall(r"https?://[^\s)`|>]+", txt)))} · відмов інструментів {sum(den.values())}' + (f' ({dict(den)})' if den else ''))
PY
    c=$(echo "$line" | grep -oE '\$[0-9.]+' | tr -d '$'); total=$(python3 -c "print(round($total + ${c:-0}, 2))")
    case "$line" in ERR*) echo "СТОП: помилка або ліміт — решту проходів не запущено (сумарно \$$total)"; exit 1;; esac
  done
done
echo "сумарно: \$$total (еквівалент API; на підписці — частка квоти)"
