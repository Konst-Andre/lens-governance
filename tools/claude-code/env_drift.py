#!/usr/bin/env python3
# живе доки: є аркуш середовища tools/claude-code/ENVIRONMENT.md (ENV-1). Дім — lens-governance:tools/claude-code/.
"""Звірка живого хмарного середовища з аркушем ENVIRONMENT.md (ENV-1, підсилення 22.10.2026 — слово Konst:
«гачок лише нагадує — замало, агент має сам пропонувати й допомагати»).

Модель — drift detection: задекларований стан (аркуш у git) ⟂ живий (сесія); кожна розбіжність — два шляхи ліків:
повернути живе до аркуша (рядок, що й куди вставити) або, якщо живу зміну зроблено свідомо, — внести її в аркуш
(firefly.ai «Drift detection», cloudposse «Drift detection», 22.10.2026).

Що звіряє (значень секретів НЕ читає й не друкує — лише чи є змінна):
  1. змінні з §2 аркуша (рядки НАЗВА=…) — є в середовищі сесії чи ні;
  2. setup script з §3 — чи ~/.claude/settings.json ≡ JSON, який він пише (старий setup script = розбіжність);
  3. мережа — github.com, api.cloudflare.com, pypi.org (HEAD, 4 с);
  4. профіль з репо — LENS_PROFILE=1, якщо аркуш його вимагає.

Запуск: python3 tools/claude-code/env_drift.py [--sheet <ENVIRONMENT.md>] [--short]   (--short — лише підсумок і ⚠)
        python3 tools/claude-code/env_drift.py selftest
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOSTS = ("https://github.com", "https://api.cloudflare.com", "https://pypi.org")


def parse(sheet_text):
    """→ (імена змінних §2, очікуваний JSON налаштувань із §3 або None)."""
    names = []
    m = re.search(r"## 2 .*?```text\n(.*?)```", sheet_text, re.S)
    if m:
        names = [l.split("=", 1)[0].strip() for l in m.group(1).splitlines() if "=" in l]
    j = re.search(r"<<'JSON'\n(.*?)\nJSON\n", sheet_text, re.S)
    return names, (json.loads(j.group(1)) if j else None)


def check(sheet_text, environ, settings_text, net):
    names, want = parse(sheet_text)
    warn, ok = [], []
    miss = [n for n in names if not environ.get(n)]
    if miss:
        warn.append(f"⚠ змінних бракує: {', '.join(miss)} → Edit → Environment variables, рядки: "
                    + " · ".join(f"`{n}=<…>`" for n in miss))
    else:
        ok.append(f"✓ змінні аркуша є ({len(names)})")
    if want is None:
        warn.append("⚠ в аркуші не знайдено JSON setup script (§3) — звірка гачків пропущена")
    elif settings_text is None:
        warn.append("⚠ ~/.claude/settings.json нема — setup script не спрацював → Edit → Setup script: вставити §3 аркуша цілком")
    else:
        try:
            same = json.loads(settings_text) == want
        except ValueError:
            same = False
        if same:
            ok.append("✓ setup script ≡ аркушу")
        else:
            warn.append("⚠ setup script ≠ аркушу (~/.claude/settings.json ≠ §3) → Edit → Setup script: замінити §3 цілком, "
                        "діє з нової сесії; або, якщо живий новіший і свідомий, — внести його в аркуш")
    bad = [h for h, up in net.items() if not up]
    if bad:
        warn.append(f"⚠ мережа: не відповідає {', '.join(bad)} → Edit → Network")
    else:
        ok.append("✓ мережа")
    if "LENS_PROFILE" in names and environ.get("LENS_PROFILE") == "1":
        ok.append("✓ профіль з репо (LENS_PROFILE=1)")
    elif "LENS_PROFILE" in names and environ.get("LENS_PROFILE"):
        warn.append("⚠ LENS_PROFILE не 1 — повний профіль у сесію не кладеться → рядок `LENS_PROFILE=1`")
    return warn, ok


def probe():
    out = {}
    for h in HOSTS:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-I", "-m", "4", "-w", "%{http_code}", h],
                           capture_output=True, text=True)
        out[h.split("//")[1]] = r.stdout.strip() not in ("", "000")
    return out


def selftest():
    sheet = ("## 2 · Змінні\n\n```text\nA_TOKEN=<…>\nLENS_PROFILE=1\n```\n\n## 3 · Setup\n\n```bash\n"
             "cat > ~/.claude/settings.json <<'JSON'\n{\"hooks\":{\"Stop\":[]}}\nJSON\n```\n")
    env, st, net = {"A_TOKEN": "s3cr3t-value", "LENS_PROFILE": "1"}, '{"hooks":{"Stop":[]}}', {"github.com": True}
    cases = [("усе ≡ аркушу → ✓", env, st, net, 0, None),
             ("бракує змінної → ⚠ з рядком для вставки", {"LENS_PROFILE": "1"}, st, net, 1, "`A_TOKEN=<…>`"),
             ("setup script старий → ⚠ замінити §3", env, '{"hooks":{}}', net, 1, "замінити §3"),
             ("settings.json нема → ⚠ setup script не спрацював", env, None, net, 1, "не спрацював"),
             ("мережа впала → ⚠", env, st, {"github.com": False}, 1, "мережа"),
             ("LENS_PROFILE=0 → ⚠", dict(env, LENS_PROFILE="0"), st, net, 1, "LENS_PROFILE не 1")]
    bad = 0
    for name, e, s, n, want_n, want_s in cases:
        w, o = check(sheet, e, s, n)
        good = (len(w) == want_n and (want_s is None or any(want_s in x for x in w))
                and not any("s3cr3t-value" in x for x in w + o))   # значення секрету — ніколи у виводі
        bad += not good
        print(("✓ " if good else "✗ ") + name)
    print(f"─── env_drift selftest: {len(cases) - bad}/{len(cases)} ───")
    return 1 if bad else 0


def main():
    a = sys.argv[1:]
    if a[:1] == ["selftest"]:
        return selftest()
    sheet = a[a.index("--sheet") + 1] if "--sheet" in a else os.path.join(HERE, "ENVIRONMENT.md")
    sp = os.path.expanduser("~/.claude/settings.json")
    w, o = check(open(sheet, encoding="utf-8").read(), os.environ,
                 open(sp, encoding="utf-8").read() if os.path.exists(sp) else None, probe())
    name = os.path.relpath(sheet)
    print(f"середовище ≡ аркушу ({name}) ✓" if not w else f"⚠ середовище ≠ аркушу ({len(w)}) — {name}")
    for l in w + ([] if "--short" in a else o):
        print("  " + l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
