#!/usr/bin/env bash
# smoke.sh — смоук §7 lens-gh v1.2 (квиток). Рецепти для CHAT_TOOLS.md живуть ТУТ і цитуються звідси дослівно.
# живе доки: живе lens-gh (tools/lens-gh/worker.js). Правка worker.js · smoke.sh · CHAT_TOOLS.md — один коміт (ТЗ §9).
# Дім: lens-governance/tools/lens-gh/smoke.sh
#
#   bash smoke.sh local   — справжній worker.js + підроблений GitHub (smoke_local.mjs), усі 6 пунктів §7 + пастки
#   bash smoke.sh live    — живий воркер; квитки видає чат (gh_ticket) і передає змінними:
#                           T_TAR T_GET T_PUT (URL квитків) · GET_SHA (очікуваний sha з квитка get) · XLSX (шлях у tar для звірки) · XLSX_SHA
#   bash smoke.sh docs    — кожен рядок-рецепт є в ../CHAT_TOOLS.md дослівно
# Вихід 0 = зелено. Кожна перевірка друкує ✓/✗.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:-local}"
OUT="${OUT:-$HERE/smoke_out}"
FAILS=0
ok()  { echo "✓ $*"; }
bad() { echo "✗ $*"; FAILS=$((FAILS+1)); }
eq()  { if [ "$1" = "$2" ]; then ok "$3"; else bad "$3 — очікував «$2», маю «$1»"; fi; }

# ---------- РЕЦЕПТИ (рядок після маркера — дослівно в CHAT_TOOLS.md і в тексті gh_ticket) ----------
recipe_clone() { # змінні: URL DIR
# RECIPE:clone
mkdir -p "$DIR" && curl --fail -sS "$URL" | tar xz --strip-components=1 -C "$DIR"
}
recipe_get() {   # змінні: URL FILE → друкує sha файлу
# RECIPE:get
curl --fail -sS "$URL" -o "$FILE" && git hash-object "$FILE"
}
recipe_put() {   # змінні: URL FILE → друкує {"sha","size"}
# RECIPE:put
{ printf '{"content":"'; base64 -w0 "$FILE"; printf '","encoding":"base64"}'; } | curl --fail-with-body -sS -X POST -H 'Content-Type: application/json' --data-binary @- "$URL"
}
recipes() { grep -A1 '^# RECIPE:' "$HERE/smoke.sh" | grep -v '^# RECIPE:' | grep -v '^--$'; }

jget() { python3 -c 'import json,sys; d=json.load(sys.stdin); print(d'"$1"')'; }
code() { curl -s -o /dev/null -w '%{http_code}' "$@"; }

if [ "$MODE" = "docs" ]; then
  DOC="$HERE/../CHAT_TOOLS.md"
  while IFS= read -r line; do
    if grep -qF -- "$line" "$DOC"; then ok "у CHAT_TOOLS: ${line:0:60}…"; else bad "нема в CHAT_TOOLS дослівно: $line"; fi
  done < <(recipes)
  [ "$FAILS" -eq 0 ] && echo "ЗЕЛЕНО (docs)" || echo "ЧЕРВОНО: $FAILS"
  exit $(( FAILS > 0 ))
fi

rm -rf "$OUT"; mkdir -p "$OUT"
cd "$OUT"

negatives() { # $1 = URL живого put-квитка, $2 = URL живого tar-квитка
  local sig="${1##*.}" pre="${1%.*}" c
  c="${sig:0:1}"; [ "$c" = "A" ] && c="B" || c="A"
  eq "$(code "$pre.$c${sig:1}" -X POST -d '{}')" 404 "§7.4 підроблений підпис → 404"
  eq "$(code "$1")" 404 "§7.4 put-квиток методом GET → 404"
  eq "$(code -X POST -d '{}' "$2")" 404 "§7.4 tar-квиток методом POST → 404"
  eq "$(curl -s "$pre.$c${sig:1}" -X POST -d '{}')" "Not found" "§7.4 тіло 404 без пояснень"
}

if [ "$MODE" = "live" ]; then
  : "${T_TAR:?}" "${T_GET:?}" "${T_PUT:?}" "${GET_SHA:?}"
  URL="$T_TAR"; DIR="$OUT/clone"; recipe_clone && ok "§7.1 tar розпаковано" || bad "§7.1 tar"
  LINT="$(ls "$DIR/lint_repo.py" "$DIR/tools/lint_repo.py" 2>/dev/null | head -1)"
  if [ -n "$LINT" ]; then (cd "$DIR" && python3 "$LINT" >"$OUT/lint.txt" 2>&1) && ok "§7.1 lint_repo.py зелений" || bad "§7.1 lint_repo.py (див. $OUT/lint.txt)"; else echo "· lint_repo.py у репо нема — пропущено"; fi
  if [ -n "${XLSX:-}" ]; then eq "$(git hash-object "$DIR/$XLSX" | cut -c1-${#XLSX_SHA})" "$XLSX_SHA" "§7.1 hash-object $XLSX"; fi
  URL="$T_GET"; FILE="$OUT/got.bin"; eq "$(recipe_get)" "$GET_SHA" "§7.2 get → sha збігається"
  for n in 1 2; do
    head -c $((150000 + n)) /dev/urandom > "$OUT/probe$n.bin"
    URL="$T_PUT"; FILE="$OUT/probe$n.bin"; R="$(recipe_put)"
    eq "$(echo "$R" | jget '["sha"]')" "$(git hash-object "$FILE")" "§7.3/6 put #$n → sha ≡ git hash-object"
    eq "$(echo "$R" | jget '["size"]')" "$(stat -c %s "$FILE")" "§7.3/6 put #$n → size точний"
    echo "   blob #$n: $(echo "$R" | jget '["sha"]')  $(stat -c %s "$FILE") б  (для gh_commit dry_run з blob)"
  done
  negatives "$T_PUT" "$T_TAR"
  echo "Далі вручну: §7.3 gh_commit dry_run {blob} · §7.5 content_base64 4823 · §7.6 два рядки put у Workers Logs"
  [ "$FAILS" -eq 0 ] && echo "ЗЕЛЕНО (live, частина контейнера)" || echo "ЧЕРВОНО: $FAILS"
  exit $(( FAILS > 0 ))
fi

# ---------- local ----------
PORT="${PORT:-8787}"; BASE="http://127.0.0.1:$PORT"; MCP="$BASE/mcp/localkey"
OUT="$OUT" PORT="$PORT" node "$HERE/smoke_local.mjs" >"$OUT/harness.out" 2>"$OUT/harness.err" &
HPID=$!; trap 'kill $HPID 2>/dev/null' EXIT
for _ in $(seq 50); do grep -q ready "$OUT/harness.out" 2>/dev/null && break; sleep 0.1; done
grep -q ready "$OUT/harness.out" || { echo "✗ стенд не піднявся"; cat "$OUT/harness.err"; exit 1; }

mcp() { # $1 = інструмент, $2 = JSON аргументів → текст результату (isError → префікс ERR:)
  curl -s "$MCP" -H 'Content-Type: application/json' -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",\"arguments\":$2}}" \
  | python3 -c 'import json,sys; r=json.load(sys.stdin)["result"]; print(("ERR:" if r.get("isError") else "")+r["content"][0]["text"])'
}
field() { sed -n "s/^$1//p" | head -1; }

eq "$(curl -s "$BASE/")" "lens-gh 1.2.0" "версія на GET /"
eq "$(curl -s "$MCP" -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jget '["result"]["tools"].__len__()')" 7 "tools/list: 7 інструментів"

# §7.1 tar → розпакувати → lint → hash-object
T="$(mcp gh_ticket '{"repo":"Konst-Andre/routes-fake","op":"tar","note":"смоук 7.1 tar"}')"; echo "$T" > ticket_tar.txt
URL="$(echo "$T" | field 'URL=')"; T_TAR="$URL"; DIR="$OUT/clone"
echo "$T" | grep -qF -- "$(recipes | sed -n 1p)" && ok "gh_ticket tar цитує RECIPE:clone дослівно" || bad "gh_ticket tar: рецепт розійшовся зі smoke.sh"
recipe_clone && ok "§7.1 tar розпаковано (--strip-components=1)" || bad "§7.1 tar"
[ -f "$DIR/README.md" ] && ok "§7.1 файли в корені теки, без префікса Konst-Andre-…" || bad "§7.1 префікс теки лишився"
(cd "$DIR" && python3 lint_repo.py >/dev/null) && ok "§7.1 lint_repo.py зелений" || bad "§7.1 lint_repo.py"
XSHA="$(mcp gh_ticket '{"repo":"Konst-Andre/routes-fake","op":"get","path":"months/2026-09/route_pass2.xlsx","note":"смоук 7.2 get"}')"
echo "$XSHA" > ticket_get.txt
GET_SHA="$(echo "$XSHA" | sed -n 's/^очікую: sha \([0-9a-f]*\) .*/\1/p')"
eq "$(git hash-object "$DIR/months/2026-09/route_pass2.xlsx")" "$GET_SHA" "§7.1 hash-object xlsx з tar ≡ sha з GitHub"
eq "$(curl -s "$BASE/__gh" | jget '["codeloadAuthHeader"]')" "[False]" "редирект на codeload: токен у query, Authorization не несеться"

# §7.2 get
URL="$(echo "$XSHA" | field 'URL=')"; FILE="$OUT/route_pass2.xlsx"
echo "$XSHA" | grep -qF -- "$(recipes | sed -n 2p)" && ok "gh_ticket get цитує RECIPE:get дослівно" || bad "gh_ticket get: рецепт розійшовся"
eq "$(recipe_get)" "$GET_SHA" "§7.2 get → sha збігається"
eq "$(stat -c %s "$FILE")" 183000 "§7.2 get → розмір 183000"
eq "$(mcp gh_ticket '{"repo":"Konst-Andre/routes-fake","op":"get","path":"months/nope.xlsx","note":"нема файлу"}' | cut -c1-4)" "ERR:" "get на неіснуючий файл → помилка вже при видачі"

# §7.3 + §7.6 put пачкою одним квитком → gh_commit dry_run {blob}
T="$(mcp gh_ticket '{"repo":"Konst-Andre/lens-target","op":"put","note":"смоук 7.6 пачка"}')"; echo "$T" > ticket_put.txt
URL="$(echo "$T" | field 'URL=')"; T_PUT="$URL"
echo "$T" | grep -qF -- "$(recipes | sed -n 3p)" && ok "gh_ticket put цитує RECIPE:put дослівно" || bad "gh_ticket put: рецепт розійшовся"
CH=""
for n in 1 2; do
  head -c $((150000 + n)) /dev/urandom > "$OUT/probe$n.xlsx"
  FILE="$OUT/probe$n.xlsx"; R="$(recipe_put)"
  S="$(echo "$R" | jget '["sha"]')"; Z="$(echo "$R" | jget '["size"]')"
  eq "$S" "$(git hash-object "$FILE")" "§7.6 put #$n → sha ≡ git hash-object"
  eq "$Z" "$(stat -c %s "$FILE")" "§7.3 put #$n → size точний"
  CH="$CH{\"path\":\"in/probe$n.xlsx\",\"blob\":\"$S\"},"
done
D="$(mcp gh_commit "{\"repo\":\"Konst-Andre/lens-target\",\"branch\":\"main\",\"message\":\"smoke\",\"dry_run\":true,\"changes\":[${CH%,}]}")"
echo "$D" > dry_blob.txt
echo "$D" | grep -q "in/probe1.xlsx · blob .* · 150001 байт" && echo "$D" | grep -q "in/probe2.xlsx · blob .* · 150002 байт" \
  && ok "§7.3 gh_commit dry_run {blob} → path · sha · точний розмір" || bad "§7.3 dry_run blob: $D"
eq "$(grep -c ' · put · Konst-Andre/lens-target · .* · смоук 7.6 пачка$' "$OUT/worker.log")" 2 "§7.6 лог: два рядки put з note"
S1="$(git hash-object "$OUT/probe1.xlsx")"
eq "$(mcp gh_commit "{\"repo\":\"Konst-Andre/routes-fake\",\"branch\":\"main\",\"message\":\"x\",\"dry_run\":true,\"changes\":[{\"path\":\"p.xlsx\",\"blob\":\"$S1\"}]}" | cut -c1-4)" "ERR:" "blob з чужого репо → помилка, не тихий коміт"
eq "$(printf '{"content":"a=b","encoding":"base64"}' | curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' --data-binary @- "$T_PUT")" 422 "put з битим base64 → 422 з причиною від GitHub"

# §7.4 квитки-відмови → 404
negatives "$T_PUT" "$T_TAR"
curl -s "$BASE/__clock?shift=700" >/dev/null
eq "$(code "$T_TAR")" 404 "§7.4 прострочений квиток (+700 с) → 404"
curl -s "$BASE/__clock?shift=0" >/dev/null
FOREIGN="$(curl -s "$BASE/__sign" -d "{\"v\":1,\"repo\":\"Other/x\",\"op\":\"get\",\"ref\":\"$(printf 'a%.0s' {1..40})\",\"path\":\"a\",\"note\":\"x\",\"exp\":$(( $(date +%s) + 300 ))}" | jget '["ticket"]')"
eq "$(code "$BASE/t/$FOREIGN")" 404 "§7.4 чужий власник (підпис справжній) → 404"
BADOP="$(curl -s "$BASE/__sign" -d "{\"v\":1,\"repo\":\"Konst-Andre/routes-fake\",\"op\":\"zip\",\"exp\":$(( $(date +%s) + 300 )),\"note\":\"x\"}" | jget '["ticket"]')"
eq "$(code "$BASE/t/$BADOP")" 404 "§7.4 невідомий op (підпис справжній) → 404"
eq "$(code "$BASE/t/garbage")" 404 "§7.4 сміття замість квитка → 404"
curl -s "$BASE/__env?drop=TICKET_KEY" >/dev/null
eq "$(code "$T_TAR")" 404 "без TICKET_KEY маршрут мовчить (404)"
eq "$(mcp gh_ticket '{"repo":"Konst-Andre/routes-fake","op":"tar","note":"x"}' | cut -c1-4)" "ERR:" "без TICKET_KEY gh_ticket відмовляє"
curl -s "$BASE/__env" >/dev/null
eq "$(mcp gh_ticket '{"repo":"Other/x","op":"tar","note":"x"}' | cut -c1-4)" "ERR:" "gh_ticket на чужого власника → відмова"
eq "$(mcp gh_ticket '{"repo":"Konst-Andre/routes-fake","op":"tar","note":""}' | cut -c1-4)" "ERR:" "gh_ticket без note → відмова"
[ "$(grep -c ' · reject · ' "$OUT/worker.log")" -ge 6 ] && ok "лог: відмови записані з причиною" || bad "лог: мало рядків reject"
grep -q 'reject · sig' "$OUT/worker.log" && grep -q 'reject · expired' "$OUT/worker.log" && grep -q 'reject · repo' "$OUT/worker.log" \
  && ok "лог: причини sig · expired · repo розрізняються" || bad "лог: причини відмов"

# §7.5 content_base64 → точний розмір (плюс обидва варіанти паддінгу)
for n in 4823 4822 4824; do
  B64="$(head -c $n /dev/urandom | base64 -w0)"
  eq "$(mcp gh_commit "{\"repo\":\"Konst-Andre/lens-target\",\"branch\":\"main\",\"message\":\"x\",\"dry_run\":true,\"changes\":[{\"path\":\"b.bin\",\"content_base64\":\"$B64\"}]}" | grep -o '(бінарний, [0-9]* байт)')" "(бінарний, $n байт)" "§7.5 content_base64 $n б → dry_run $n"
done

echo "---"; echo "лог воркера (worker.log):"; sed 's/^/   /' "$OUT/worker.log"
[ "$FAILS" -eq 0 ] && echo "ЗЕЛЕНО (local)" || echo "ЧЕРВОНО: $FAILS"
exit $(( FAILS > 0 ))
