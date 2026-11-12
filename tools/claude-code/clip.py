#!/usr/bin/env python3
# clip.py · кліп руху для Konst: сторінка → кроки (клік · наведення · текст · пауза) → MP4 (H.264, грає на iOS і ПК) + смуга кадрів, що змінюються (очі агента).
# живе доки: Konst приймає рух чи поведінку на відео, а не лише знімками (слово Konst AE S140, 12.11.2026: «щоб це була не одноразова акція»).
# Навіщо: статичний знімок не показує руху; Konst часто не біля ПК — кліп у чат (SendUserFile) він дивиться з телефона, а вирок дає на пристрої.
#   Агент дивиться смугу кадрів (Read) — так сам бачить ваду руху до показу (AE S140: значки стискались до 0 — видно лише на кадрах кліпу).
# Практика: Playwright пише .webm → ffmpeg у MP4 H.264 yuv420p + faststart (старий Safari / iOS .webm не грає; GIF більший і гірший) —
#   flaviocopes «Record a product demo with Playwright», addpipe «inline recorder on iOS»; смуга — фільтри mpdecimate + кадри → плитка
#   (FFmpeg wiki «multiple screenshots to an image (tile)», 12.11.2026).
# Запуск:  python3 clip.py <сценарій.json> <тека виходу>        (сценарій — нижче)
#          python3 clip.py selftest                              (зуби: рух → кліп і ≥ 3 кадри; без руху → ✗ «руху не видно»; стрибок на кроці з "motion" → ✗ «стрибок, не рух»)
# Сценарій JSON: {"url": "...", "name": "rail_C", "viewport": [1920, 1080] | "device": "iPhone 15",
#   "init": ["<js до завантаження>"], "ready": "<js-умова готовності>", "crop": [x, y, w, h],
#   "steps": [{"click": "<css>"}, {"hover": "<css>"}, {"move": [x, y]}, {"fill": ["<css>", "текст"]}, {"press": "Tab"}, {"eval": "<js>"}, {"wait": 900}],
#   "min_frames": 3}
#   Крок з рухом — мітка "motion": true: {"click": "<css>", "wait": 900, "motion": true}. Такий крок мусить дати ≥ 3 кадри, що змінюються,
#   у своєму вікні часу; менше — ✗ «крок N: стрибок, не рух» (FAB-2, 12.11.2026: без мітки сторінка, де анімація зникла й лишився стрибок,
#   проходила ✓ — кроки самі дають 3–4 різні кадри). Вікно кроку — годинник Python проти часу кадру відео: точність ≈ ±0,15 с, wait кроку ≥ 300 мс.
#   Кілька кліпів — список таких об'єктів. Смуга кадрів — <name>_frames.webp: до 12 кадрів рівномірно, ОСТАННІЙ кадр руху завжди в смузі; на плитці — час кадру в кліпі.
# Вихід: <name>.mp4 · <name>_frames.webp · рядок «✓ <name>: N кадрів змінюються, T с» або «✗ <name>: руху не видно (…)».
# Потребує: Python Playwright (ставить гачок старту продукту), Pillow і ffmpeg (у хмарному контейнері є; нема — ✗ з назвою).
import sys, os, json, shutil, subprocess, tempfile, pathlib, glob, time, re

def need_ffmpeg():
    if not shutil.which("ffmpeg"): print("✗ ffmpeg нема — кліп не зібрати (apt-get install -y ffmpeg)"); sys.exit(2)

def record(sc, out):
    from playwright.sync_api import sync_playwright
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    name = sc.get("name", "clip"); vid = pathlib.Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch(ignore_default_args=["--hide-scrollbars"])   # смуга прокрутки — як на ПК (SHOTS.md §3)
        if sc.get("device"):
            d = dict(p.devices[sc["device"]]); vw = d["viewport"]
            ctx = b.new_context(**d, record_video_dir=str(vid), record_video_size=vw)
        else:
            w, h = sc.get("viewport", [1920, 1080]); vw = {"width": w, "height": h}
            ctx = b.new_context(viewport=vw, record_video_dir=str(vid), record_video_size=vw)
        t0 = time.monotonic(); marks = []          # час кроків від початку запису — щоб судити рух КОЖНОГО кроку
        pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
        for js in sc.get("init", []): pg.add_init_script(js)
        pg.goto(sc["url"])
        if sc.get("ready"): pg.wait_for_function(sc["ready"], timeout=30000)
        pg.wait_for_timeout(sc.get("settle", 600))
        for s in sc.get("steps", []):
            marks.append([time.monotonic() - t0, None, s])
            if "click" in s: pg.click(s["click"])
            elif "hover" in s: pg.hover(s["hover"])
            elif "move" in s: pg.mouse.move(*s["move"], steps=8)
            elif "fill" in s: pg.fill(*s["fill"])
            elif "press" in s: pg.keyboard.press(s["press"])
            elif "eval" in s: pg.evaluate(s["eval"])
            if "wait" in s: pg.wait_for_timeout(s["wait"])
            marks[-1][1] = time.monotonic() - t0
        pg.wait_for_timeout(sc.get("tail", 500)); ctx.close(); b.close()
    src = next(vid.glob("*.webm"))
    vf = "fps=30"
    if sc.get("crop"):
        x, y, w, h = sc["crop"]; vf = f"crop={w}:{h}:{x}:{y},fps=30"
    mp4 = out / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-vf", vf + ",scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "24", "-movflags", "+faststart", str(mp4)], check=True)
    fr = pathlib.Path(tempfile.mkdtemp())
    pr = subprocess.run(["ffmpeg", "-loglevel", "info", "-y", "-i", str(mp4), "-vf", "mpdecimate=hi=64*12:lo=64*5:frac=0.33,showinfo",
                    "-fps_mode", "vfr", str(fr / "%04d.png")], check=True, capture_output=True, text=True)
    frames = sorted(glob.glob(str(fr / "*.png")))
    pts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", pr.stderr)][:len(frames)]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout.strip() or 0)
    if frames:
        from PIL import Image
        k12 = min(12, len(frames)); idx = sorted({round(i * (len(frames) - 1) / max(1, k12 - 1)) for i in range(k12)})
        from PIL import ImageDraw
        ims = [Image.open(frames[i]) for i in idx]; w, h = ims[0].size; k_ = min(1.0, 480 / w); tw, th = int(w * k_), int(h * k_)
        cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
        BAND = 18   # підпис часу — смужкою ПІД плиткою, не поверх кадру (кут кадру — логотип рейки)
        sheet = Image.new("RGB", (cols * tw + (cols - 1) * 8, rows * (th + BAND) + (rows - 1) * 8), "white")
        for k, im in enumerate(ims):
            x0, y0 = (k % cols) * (tw + 8), (k // cols) * (th + BAND + 8); lab = f"{pts[idx[k]]:.2f} s" if idx[k] < len(pts) else ""
            sheet.paste(im.resize((tw, th)), (x0, y0)); d = ImageDraw.Draw(sheet)
            d.rectangle([x0, y0 + th, x0 + tw - 1, y0 + th + BAND - 1], fill="#222"); d.text((x0 + 6, y0 + th + 3), f"{k + 1}/{len(ims)} · {lab}", fill="white")
        sheet.save(out / f"{name}_frames.webp", "WEBP", quality=80)
    n = len(frames); mn = sc.get("min_frames", 3); jumps = []
    for k, (a, b, s) in enumerate(marks):
        c = sum(1 for t in pts if a - 0.05 <= t <= (b or a) + 0.15)
        if s.get("motion") and c < 3: jumps.append(f"крок {k + 1}: {c} кадр(ів) — стрибок, не рух")
    print("   кроки (кадрів, що змінюються):", [sum(1 for t in pts if a - 0.05 <= t <= (b or a) + 0.15) for a, b, s in marks])
    ok = n >= mn and not errs and not jumps
    why = (f"руху не видно (кадрів, що змінюються, {n} < {mn})" if n < mn else "") + ("; ".join(jumps)) + (f"; помилки сторінки: {'; '.join(errs)}" if errs else "")
    print((f"✓ {name}: {n} кадрів змінюються, {dur:.1f} с → {mp4}" if ok else f"✗ {name}: {why}"))
    return ok

def selftest():
    need_ffmpeg(); bad = 0; tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "move.html").write_text("<!doctype html><style>#b{width:80px;height:80px;background:#08c;transition:transform .8s ease}#b.on{transform:translateX(400px)}</style>"
                                   "<div id=b></div><button id=t onclick=\"b.classList.toggle('on')\">рух</button>", encoding="utf-8")
    (tmp / "still.html").write_text("<!doctype html><div style='width:80px;height:80px;background:#08c'></div><button id=t>нічого</button>", encoding="utf-8")
    base = {"viewport": [640, 360], "steps": [{"click": "#t", "wait": 1000}], "min_frames": 3}
    r1 = record({**base, "url": (tmp / "move.html").as_uri(), "name": "move"}, tmp / "out")
    r2 = record({**base, "url": (tmp / "still.html").as_uri(), "name": "still"}, tmp / "out")
    (tmp / "jump.html").write_text("<!doctype html><style>#b{width:80px;height:80px;background:#08c}#b.on{transform:translateX(400px)}</style>"
                                   "<div id=b></div><button id=t onclick=\"b.classList.toggle('on')\">стрибок</button>", encoding="utf-8")
    four = [{"click": "#t", "wait": 600, "motion": True}] * 4
    r3 = record({"viewport": [640, 360], "steps": four, "url": (tmp / "jump.html").as_uri(), "name": "jump"}, tmp / "out")
    r4 = record({"viewport": [640, 360], "steps": four, "url": (tmp / "move.html").as_uri(), "name": "move4"}, tmp / "out")
    for ok, m in [(r1 and (tmp / "out/move.mp4").stat().st_size > 1000 and (tmp / "out/move_frames.webp").exists(), "сторінка з рухом → MP4 + смуга кадрів"),
                  (not r2, "зуби: сторінка без руху → ✗ «руху не видно»"),
                  (not r3, "зуби: 4 миттєві перемикання на кроках з «motion» → ✗ «стрибок, не рух» (без мітки було ✓)"),
                  (r4, "ті самі 4 кроки з переходом 0,8 с → ✓")]:
        print(("✓ " if ok else "✗ ") + m); bad += not ok
    print(f"─── clip selftest: {4 - bad}/4 ───"); sys.exit(1 if bad else 0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest": selftest()
    if len(sys.argv) < 3: print("python3 clip.py <сценарій.json> <тека> | selftest"); sys.exit(2)
    need_ffmpeg()
    data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    res = [record(sc, sys.argv[2]) for sc in (data if isinstance(data, list) else [data])]
    sys.exit(0 if all(res) else 1)
