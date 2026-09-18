#!/usr/bin/env python3
# живе доки: у claude.ai немає офіційного GitHub-конектора із записом (тоді — в archive/superseded)
# Lens_claude_github_push.py · v2 · 18.09.2026 (G-K: +--delete) · П-GH1 · протокол: Lens_github_push_protocol.md
"""Пуш з чату Claude у GitHub одним атомарним комітом (Git Data API).

ЗАПОБІЖНИК (двоходовий):
  хід 1:  --dry-run  → нічого не пише, друкує diff-зведення і PLAN-ID
  хід 2:  --confirm PLAN-ID  → пише, ТІЛЬКИ якщо PLAN-ID збігся
PLAN-ID = хеш(репо + ціль + SHA бази + шляхи + вміст). Змінився хоч байт
або репо пішло вперед → інший PLAN-ID → запис відмовлено.

Токен — лише зі змінної середовища GH_TOKEN (ніколи з аргументів чи файлів).
Видалення ФАЙЛУ — лише --delete repo/path (v2): шлях має існувати в базі, входить у PLAN-ID,
у dry-run окремим рядком ВИДАЛЕННЯ. Видалення гілок і force-push — НЕ ПІДТРИМУЄТЬСЯ свідомо.

Приклад:
  export GH_TOKEN=...   # з інструкції Project
  python3 Lens_claude_github_push.py --repo Konst-Andre/lens-governance \
      --branch gh-push/x --message "..." --dry-run  kernel/A.md=./A.md
  python3 Lens_claude_github_push.py ...те саме... --confirm 3f9a1c
Ціль: --branch <нова або своя гілка> (типово) | --main (лише з явного «так» Konst).
"""
import argparse, base64, difflib, hashlib, json, os, re, sys, urllib.request, urllib.error

API = "https://api.github.com"
FORBIDDEN_PATH = [re.compile(r"AE_WORK_index_X.*\.html$")]          # В-31/В-94
SECRET = re.compile(rb"github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{30,}")


def die(msg, code=2):
    print("✗ " + msg); sys.exit(code)


def gh(method, path, token, body=None, ok=(200, 201)):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        data = json.loads(e.read() or b"{}")
        if e.code in ok:
            return e.code, data
        return e.code, data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--branch")
    g.add_argument("--main", action="store_true")
    ap.add_argument("--message", required=True)
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--dry-run", action="store_true")
    m.add_argument("--confirm", metavar="PLAN-ID")
    ap.add_argument("--delete", action="append", default=[], metavar="repo/path",
                    help="видалити файл (v2); шлях має існувати в базі")
    ap.add_argument("files", nargs="*", help="repo/path=local/path")
    a = ap.parse_args()

    token = os.environ.get("GH_TOKEN") or die("немає GH_TOKEN у середовищі")
    target = "main" if a.main else a.branch
    if not a.main and target in ("main", "master"):
        die("--branch не може бути main — для main є окремий --main")

    pairs = []
    for spec in a.files:
        if "=" not in spec:
            die(f"формат repo/path=local/path: {spec}")
        rp, lp = spec.split("=", 1)
        rp = rp.lstrip("/")
        if any(p.search(rp) for p in FORBIDDEN_PATH):
            die(f"заборонений шлях (робочий index не пушимо): {rp}")
        data = open(lp, "rb").read()
        if SECRET.search(data):
            die(f"у файлі схожий на токен рядок — запис заблоковано: {lp}")
        pairs.append((rp, data))
    pairs.sort()
    dels = sorted({d.lstrip("/") for d in a.delete})
    if not pairs and not dels:
        die("нічого писати: немає ні файлів, ні --delete")
    if set(dels) & {rp for rp, _ in pairs}:
        die("той самий шлях і пишеться, і видаляється")

    st, ref = gh("GET", f"/repos/{a.repo}/git/ref/heads/{target}", token)
    branch_exists = st == 200
    if not branch_exists:
        if a.main:
            die("не знайдено main")
        st, ref = gh("GET", f"/repos/{a.repo}/git/ref/heads/main", token)
        if st != 200:
            die(f"база main недоступна: {st} {ref.get('message')}")
    base = ref["object"]["sha"]

    h = hashlib.sha256(f"{a.repo}|{target}|{base}|{a.message}".encode())
    print(f"репо {a.repo} · ціль {target}{'' if branch_exists else ' (НОВА гілка від main)'} · база {base[:7]}")
    for rp, data in pairs:
        h.update(rp.encode() + b"\0" + hashlib.sha256(data).digest())
        st, cur = gh("GET", f"/repos/{a.repo}/contents/{rp}?ref={base}", token)
        if st == 200:
            old = base64.b64decode(cur["content"]).decode("utf-8", "replace").splitlines()
            try:
                new = data.decode("utf-8").splitlines()
                d = list(difflib.unified_diff(old, new, lineterm="", n=0))
                add = sum(1 for x in d if x.startswith("+") and not x.startswith("+++"))
                rem = sum(1 for x in d if x.startswith("-") and not x.startswith("---"))
                tag = "без змін" if not d else f"ЗМІНА +{add} −{rem}"
            except UnicodeDecodeError:
                tag = "ЗМІНА (бінарний)"
        else:
            tag = f"НОВИЙ ({len(data)} б)"
        print(f"  · {rp}: {tag}")
    for rp in dels:
        h.update(b"DEL\0" + rp.encode())
        st, cur = gh("GET", f"/repos/{a.repo}/contents/{rp}?ref={base}", token)
        if st != 200 or not isinstance(cur, dict) or cur.get("type") != "file":
            die(f"видалення: {rp} — у базі {base[:7]} такого файлу немає ({st})")
        print(f"  · {rp}: ВИДАЛЕННЯ ({cur.get('size')} б)")
    plan = h.hexdigest()[:6]
    print(f"PLAN-ID: {plan}")

    if a.dry_run:
        print("dry-run: нічого не записано. Для запису — той самий виклик з --confirm " + plan)
        return
    if a.confirm != plan:
        die(f"PLAN-ID не збігся ({a.confirm} ≠ {plan}): план змінився — спершу новий --dry-run")

    st, bc = gh("GET", f"/repos/{a.repo}/git/commits/{base}", token)
    items = []
    for rp, data in pairs:
        st, blob = gh("POST", f"/repos/{a.repo}/git/blobs", token,
                      {"content": base64.b64encode(data).decode(), "encoding": "base64"})
        if st != 201:
            die(f"blob {rp}: {st} {blob.get('message')}")
        items.append({"path": rp, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    for rp in dels:     # sha: None у дереві = видалення файлу (Git Data API)
        items.append({"path": rp, "mode": "100644", "type": "blob", "sha": None})
    st, tree = gh("POST", f"/repos/{a.repo}/git/trees", token, {"base_tree": bc["tree"]["sha"], "tree": items})
    if st != 201:
        die(f"tree: {st} {tree.get('message')}")
    st, cm = gh("POST", f"/repos/{a.repo}/git/commits", token,
                {"message": a.message, "tree": tree["sha"], "parents": [base]})
    if st != 201:
        die(f"commit: {st} {cm.get('message')}")
    if branch_exists:   # тільки fast-forward, force=False
        st, r = gh("PATCH", f"/repos/{a.repo}/git/refs/heads/{target}", token, {"sha": cm["sha"], "force": False})
    else:
        st, r = gh("POST", f"/repos/{a.repo}/git/refs", token, {"ref": f"refs/heads/{target}", "sha": cm["sha"]})
    if st not in (200, 201):
        die(f"ref {target}: {st} {r.get('message')} — коміт {cm['sha'][:7]} створено, але не прив'язано")
    print(f"✓ коміт {cm['sha'][:7]} → {target}")
    print(f"  https://github.com/{a.repo}/commit/{cm['sha']}")


if __name__ == "__main__":
    main()
