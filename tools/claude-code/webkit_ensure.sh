#!/usr/bin/env bash
# живе доки: прилади ядра знімають сторінки в Playwright і потрібен другий рушій (родина Safari) поруч із Chromium образу.
# Дім — lens-governance:tools/claude-code/. Канон — kernel/Lens_stagebench_manifest.md §8.18 «Два рушії».
#
# WebKit — сам, як Chromium (Konst EquipLens S40 21.11.2026: «щоб ставився автоматично… версія завжди актуальна»).
# Ревізію бере з browsers.json ТОГО Playwright, що в образі (не число в коді): оновить платформа Playwright —
# наступний старт поставить нову пару сам. Новіший WebKit, ніж знає цей Playwright, не керується — «актуальна» = найновіша,
# якою керує Playwright образу (playwright.dev/docs/browsers, 21.11.2026: після оновлення пакета — знову встановлювач).
# Ставить у $PLAYWRIGHT_BROWSERS_PATH (образ: /opt/pw-browsers, там і Chromium) → require('playwright').webkit без змінних.
# І Python-пакет playwright тієї ж версії (Konst 24.11.2026: «системне, що по колу із сесії в сесію, — автоматично»): одна бібліотека
#   на обидва рушії для приладів на Python (clip · port_same · pwa_icon · pw_quiet · tester/explore); зашите число ламалось (AE S103).
#
#   bash webkit_ensure.sh bg        — у фоні (SessionStart диспетчера; лише CLAUDE_CODE_REMOTE=true); старт не чекає
#   bash webkit_ensure.sh install   — встановити, якщо нема (замок flock), тоді пробний запуск; рядок стану
#   bash webkit_ensure.sh check     — лише рядок стану (нічого не ставить); вихід 0 завжди — WebKit не гейт
#   bash webkit_ensure.sh selftest  — зуби на підкинутих теках
set -u
PW_DIR=${LENS_PW_DIR:-/opt/node-tools/node_modules/playwright}
BR=${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}
LOG=${LENS_WEBKIT_LOG:-/tmp/lens-webkit.log}
ST=${LENS_WEBKIT_STATUS:-/tmp/lens-webkit.status}
LOCK=${LENS_WEBKIT_LOCK:-/tmp/lens-webkit.lock}
PIP=${LENS_PIP:-pip}

want() {   # друкує «<rev> <версія WebKit> <версія Playwright>» або нічого
  python3 - "$PW_DIR" <<'PY' 2>/dev/null
import json, os, sys
d = sys.argv[1]
core = os.path.join(os.path.dirname(d), 'playwright-core')
bj = next((p for p in (os.path.join(core, 'browsers.json'), os.path.join(d, 'browsers.json')) if os.path.isfile(p)), None)
if not bj: sys.exit(1)
w = next((b for b in json.load(open(bj))['browsers'] if b['name'] == 'webkit'), None)
pv = json.load(open(os.path.join(d, 'package.json')))['version']
print(w['revision'], w.get('browserVersion', '?'), pv)
PY
}

state() {   # рядок стану без встановлення
  local w rev ver pv
  w=$(want) || true
  if [ -z "$w" ]; then echo "ⓘ WebKit: Playwright образу не знайдено ($PW_DIR) — рушій не ставлю"; return 2; fi
  read -r rev ver pv <<<"$w"
  if [ -f "$BR/webkit-$rev/INSTALLATION_COMPLETE" ] || { [ -d "$BR/webkit-$rev" ] && [ -n "$(ls -A "$BR/webkit-$rev" 2>/dev/null)" ]; }; then
    if [ -f "$ST" ] && grep -q "rev $rev" "$ST"; then cat "$ST"; else echo "✓ WebKit $ver (rev $rev) ≡ Playwright $pv — стоїть, пробного запуску ще не було"; fi
    return 0
  fi
  local old; old=$(ls -d "$BR"/webkit-* 2>/dev/null | head -1)
  if [ -f "$LOCK.busy" ]; then echo "⏳ WebKit $ver (rev $rev): ставиться у фоні — лог $LOG"; return 1; fi
  if [ -n "$old" ]; then echo "⚠ WebKit застарів: є $(basename "$old"), Playwright $pv хоче rev $rev — bash webkit_ensure.sh install"; return 1; fi
  echo "⚠ WebKit $ver (rev $rev) нема — bash webkit_ensure.sh install (≈1 хв)"; return 1
}

pyensure() {   # Python-пакет ≡ версії Playwright образу; є — нічого (замір 24.11: pip 5 с)
  local pv=$1
  python3 -c "import importlib.metadata as m,sys; sys.exit(m.version('playwright')!='$pv')" 2>/dev/null && return 0
  if timeout 120 $PIP install -q --break-system-packages "playwright==$pv" >>"$LOG" 2>&1; then echo "== Python-Playwright $pv поставлено" >>"$LOG"
  else echo "⚠ Python-Playwright $pv не поставився — руками: pip install playwright==$pv" >>"$LOG"; fi
}

install() {
  local w rev ver pv
  w=$(want) || { state; return 0; }
  read -r rev ver pv <<<"$w"
  exec 9>"$LOCK"; flock 9   # другий виклик чекає першого, не ставить удруге
  if ! state >/dev/null || ! grep -q "rev $rev" "$ST" 2>/dev/null; then
    : >"$LOCK.busy"
    { echo "== $(date -Is) webkit rev $rev для Playwright $pv → $BR"
      [ -d "$BR/webkit-$rev" ] || PLAYWRIGHT_BROWSERS_PATH="$BR" node "$PW_DIR/cli.js" install webkit
      if [ "$(id -u)" = 0 ]; then PLAYWRIGHT_BROWSERS_PATH="$BR" node "$PW_DIR/cli.js" install-deps webkit; else echo "не root — install-deps пропущено"; fi
    } >>"$LOG" 2>&1
    local v
    v=$(cd /tmp && PLAYWRIGHT_BROWSERS_PATH="$BR" NODE_PATH="$(dirname "$PW_DIR")" timeout 60 node -e "
      const {webkit}=require('playwright');(async()=>{const b=await webkit.launch();console.log(b.version());await b.close()})().catch(e=>{console.error(e.message.split('\n')[0]);process.exit(1)})" 2>>"$LOG")
    if [ -n "$v" ]; then echo "✓ WebKit $v (rev $rev) ≡ Playwright $pv — пробний запуск ✓ $(date +%H:%M)" >"$ST"
    else echo "⚠ WebKit rev $rev: пробний запуск не вдався — лог $LOG" >"$ST"; fi
    rm -f "$LOCK.busy"
  fi
  pyensure "$pv"
  cat "$ST"
}

case "${1:-check}" in
  check) state; exit 0 ;;
  install) install; exit 0 ;;
  bg)
    [ "${CLAUDE_CODE_REMOTE:-}" = true ] || [ -n "${LENS_WEBKIT_FORCE_BG:-}" ] || exit 0
    setsid nohup bash "${BASH_SOURCE[0]}" install >/dev/null 2>&1 </dev/null &
    exit 0 ;;
  selftest)
    t=$(mktemp -d); ok=0; n=0
    chk() { n=$((n+1)); if printf '%s' "$2" | grep -q -- "$3"; then ok=$((ok+1)); echo "✓ $1"; else echo "✗ $1 — чекав «$3», є: $2"; fi; }
    mkdir -p "$t/nm/playwright" "$t/nm/playwright-core" "$t/br"
    echo '{"version":"9.9.0"}' >"$t/nm/playwright/package.json"
    echo '{"browsers":[{"name":"chromium","revision":"1"},{"name":"webkit","revision":"77","browserVersion":"30.1"}]}' >"$t/nm/playwright-core/browsers.json"
    E="LENS_PW_DIR=$t/nm/playwright PLAYWRIGHT_BROWSERS_PATH=$t/br LENS_WEBKIT_STATUS=$t/st LENS_WEBKIT_LOCK=$t/lk"
    s=$(env $E bash "${BASH_SOURCE[0]}" check); chk "нема рушія → ⚠ нема" "$s" "⚠ WebKit 30.1 (rev 77) нема"
    mkdir -p "$t/br/webkit-70"; touch "$t/br/webkit-70/x"
    s=$(env $E bash "${BASH_SOURCE[0]}" check); chk "стара ревізія → ⚠ застарів (зуб: Playwright оновився)" "$s" "застарів: є webkit-70"
    touch "$t/lk.busy"; s=$(env $E bash "${BASH_SOURCE[0]}" check); chk "ставиться у фоні → ⏳" "$s" "⏳"; rm -f "$t/lk.busy"
    mkdir -p "$t/br/webkit-77"; touch "$t/br/webkit-77/INSTALLATION_COMPLETE"
    s=$(env $E bash "${BASH_SOURCE[0]}" check); chk "потрібна ревізія → ✓" "$s" "✓ WebKit 30.1 (rev 77) ≡ Playwright 9.9.0"
    echo "✓ WebKit 30.1 (rev 77) ≡ Playwright 9.9.0 — пробний запуск ✓ 12:00" >"$t/st"
    s=$(env $E bash "${BASH_SOURCE[0]}" check); chk "стан пробного запуску читається" "$s" "пробний запуск ✓"
    printf '#!/bin/sh\necho "$@" >%s/pip.args\n' "$t" >"$t/pip"; chmod +x "$t/pip"
    s=$(env $E LENS_PIP="$t/pip" LENS_WEBKIT_LOG="$t/log" bash "${BASH_SOURCE[0]}" install; cat "$t/pip.args" 2>/dev/null); chk "Python-пакет не тієї версії → pip playwright==<версія образу>" "$s" "playwright==9.9.0"
    s=$(env LENS_PW_DIR="$t/none" bash "${BASH_SOURCE[0]}" check); chk "нема Playwright → ⓘ, не падає" "$s" "ⓘ WebKit: Playwright образу не знайдено"
    s=$(env -u CLAUDE_CODE_REMOTE $E bash "${BASH_SOURCE[0]}" bg; echo "rc=$?"); chk "bg поза хмарою — нічого не робить" "$s" "rc=0"
    rm -rf "$t"; echo "$ok/$n"; [ "$ok" = "$n" ] ;;
  *) echo "режими: check · install · bg · selftest" >&2; exit 2 ;;
esac
