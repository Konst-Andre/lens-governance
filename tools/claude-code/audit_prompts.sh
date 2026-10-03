#!/usr/bin/env bash
# Подвійний аудит інструкцій: /doctor prompt-audit двома РІЗНИМИ моделями, названими явно псевдонімами (завжди найновіша версія):
# sonnet і opus --effort high. AUDIT_THIRD=fable — третій прохід ЛИШЕ за явним словом Konst (Fable — за реальні кошти, 04.10.2026).
#
# живе доки: інструкції агента перевіряються аудитом Claude Code. Зразок: lens-governance:tools/claude-code/ — копіювати в tools/ репо як є.
#
# Запуск:  bash tools/audit_prompts.sh <файл> [<файл> …]      (шлях — від кореня репо, у якому лежить файл)
#          bash tools/audit_prompts.sh .                      (крапка — увесь репо: /doctor prompt-audit без шляху)
# Звіти:   $AUDIT_OUT (за замовчуванням /tmp/audit)/<ім'я>.<модель>.txt — у репо не комітяться.
# Аудит нічого не міняє. Синтез робить агент: знахідка обох моделей — висока впевненість; однієї — звірити грепом;
# застосовується лише підтверджене і лише після «так» Konst; рядок — у журнал аудиту репо тим самим комітом
# (docs/AUDIT.md; продукт Lens за Р-7 — lens/<Продукт>_AUDIT.md).
# Потрібен Claude Code ≥ 2.1.283 (/doctor prompt-audit). Кожен прохід — кілька хвилин; усі йдуть паралельно.
set -u
[ $# -ge 1 ] || { echo "вкажіть файл(и) або . для всього репо"; exit 2; }
OUT="${AUDIT_OUT:-/tmp/audit}"; mkdir -p "$OUT"
for f in "$@"; do
  if [ "$f" = "." ]; then arg=""; n="repo"; else [ -f "$f" ] || { echo "нема файла: $f"; exit 2; }; arg=" $f"; n=$(echo "$f" | tr '/' '_'); fi
  timeout 1500 claude -p --model sonnet "/doctor prompt-audit$arg" > "$OUT/$n.sonnet.txt" 2>&1 &
  timeout 1500 claude -p --model opus --effort high "/doctor prompt-audit$arg" > "$OUT/$n.opus.txt" 2>&1 &
  [ -n "${AUDIT_THIRD:-}" ] && timeout 1500 claude -p --model "$AUDIT_THIRD" --effort high "/doctor prompt-audit$arg" > "$OUT/$n.$AUDIT_THIRD.txt" 2>&1 &
done
wait
for f in "$@"; do if [ "$f" = "." ]; then n="repo"; else n=$(echo "$f" | tr '/' '_'); fi; for r in "$OUT/$n".*.txt; do echo "$f → $r ($(wc -c <"$r") Б)"; done; done
