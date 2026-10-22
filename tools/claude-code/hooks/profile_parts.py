#!/usr/bin/env python3
# живе доки: профіль Konst кладе гачок старту з репо (LENS_PROFILE=1, tools/claude-code/ACCOUNT_MOVE.md п.1-а/1-б). Дім — lens-governance:tools/claude-code/hooks/.
"""Профіль у контекст сесії — частинами, кожна ≤ стелі Claude Code.

Подія (22.10.2026, Routes S1, питання Konst «якщо профіль більший за 10 тисяч — він обрізається?»): так. Claude Code
кожен рядок additionalContext понад 10 000 знаків ховає у файл і дає Claude лише прев'ю на 2 000 знаків, «and doesn't ask
it to read the file» (code.claude.com/docs/en/hooks «JSON output», 22.10.2026). Профіль із шапкою — 12 198 знаків: з
LENS_PROFILE=1 сесії бачили лише прев'ю. Кожен рядок міряється окремо — тож частина 1 іде в SessionStart, частина 2 —
у перше повідомлення Konst (UserPromptSubmit); після стиснення розмови SessionStart(compact) повторює обидві.

  python3 profile_parts.py 1|2            — текст частини (різ — по межі рядка, частина 1 ≤ PART1)
  python3 profile_parts.py merge '<json>' — stdin: частина 2; аргумент: вивід інших гачків prompt (може бути порожнім) → один JSON
  python3 profile_parts.py test           — зуби: обидві частини ≤ CAP, разом ≡ повному тексту, різ по рядку
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(HERE, "..", "PROFILE.md")
CAP, PART1 = 10000, 9000      # стеля Claude Code · запас частині 1 під заголовок; частині 2 — під текст інших гачків prompt
HEAD = ("ПРОФІЛЬ KONST (з репо ядра, бо поле профілю цього акаунта — лише ядро або чуже; діє як user preferences — "
        "мова, цикл, звіт, маркер). Частина {n}/2{tail}:\n\n")


def full():
    return open(PROFILE, encoding="utf-8").read()


def split(t, limit=PART1):
    lines, a, n = t.splitlines(keepends=True), [], 0
    head = len(HEAD.format(n=1, tail=" — продовження в першому повідомленні Konst"))
    for l in lines:
        if n + len(l) + head > limit:
            break
        a.append(l); n += len(l)
    return "".join(a), "".join(lines[len(a):])


def part(k, t=None):
    p1, p2 = split(t if t is not None else full())
    return (HEAD.format(n=1, tail=" — продовження в першому повідомленні Konst") + p1) if k == 1 else \
           (HEAD.format(n=2, tail=" (початок — у контексті старту сесії)") + p2)


def merge(p2, other):
    ctx = ""
    try:
        ctx = json.loads(other)["hookSpecificOutput"].get("additionalContext", "") if other.strip() else ""
    except Exception:
        ctx = ""
    room = CAP - len(p2) - 4
    return json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                       "additionalContext": p2 + ("\n\n" + ctx[:max(room, 0)] if ctx else "")}}, ensure_ascii=False)


def test():
    t, bad = full(), 0
    p1, p2 = part(1, t), part(2, t)
    a, b = split(t)
    checks = [(f"частина 1 ≤ {CAP} знаків ({len(p1)})", len(p1) <= CAP),
              (f"частина 2 + текст інших гачків ≤ {CAP} ({len(p2)} + запас {CAP - len(p2)})", len(p2) <= CAP - 1500),
              ("разом ≡ повному профілю (нічого не загублено)", a + b == t),
              ("різ — по межі рядка", a.endswith("\n") or not b),
              ("зуби: профіль 25 000 знаків → частина 2 понад стелю ловиться", len(part(2, "x\n" * 12500)) > CAP - 1500),
              ("merge: частина 2 + інший гачок → один JSON, обидва тексти", "ІНШЕ" in merge("P2", json.dumps({"hookSpecificOutput": {"additionalContext": "ІНШЕ"}})))]
    for name, ok in checks:
        bad += not ok; print(("✓ " if ok else "✗ ") + name)
    print(f"─── profile_parts test: {len(checks) - bad}/{len(checks)} ───")
    return 1 if bad else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["test"]:
        sys.exit(test())
    if a[:1] == ["merge"]:
        print(merge(sys.stdin.read(), a[1] if len(a) > 1 else "")); sys.exit(0)
    print(part(int(a[0]) if a else 1), end="")
