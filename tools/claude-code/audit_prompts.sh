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
total=0
for f in "$@"; do
  n=$(echo "$f" | tr '/' '_')
  for m in $models; do
    eff="--effort high"   # sonnet теж high: 06.10 на wsd знайшов ядро знахідок opus за пів ціни; без --effort думав у 7 разів менше
    timeout 1500 claude -p --model "$m" $eff --output-format json "/doctor prompt-audit $f" > "$OUT/$n.$m.json" 2> "$OUT/$n.$m.err"   # stderr окремо: попередження CLI (06.10: «Ignoring … permissions») ламали JSON
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
    c=$(echo "$line" | grep -oE '\$[0-9.]+' | tr -d '$'); total=$(python3 -c "print(round($total + ${c:-0}, 2))")
    case "$line" in ERR*) echo "СТОП: помилка або ліміт — решту проходів не запущено (сумарно \$$total)"; exit 1;; esac
  done
done
echo "сумарно: \$$total (еквівалент API; на підписці — частка квоти)"
