#!/usr/bin/env python3
# clip.py · кліп руху для Konst: сторінка → кроки (клік · наведення · текст · пауза) → MP4 (H.264, грає на iOS і ПК) + смуга кадрів, що змінюються (очі агента).
# живе доки: Konst приймає рух чи поведінку на відео, а не лише знімками (слово Konst AE S140, 12.11.2026: «щоб це була не одноразова акція»).
# Навіщо: статичний знімок не показує руху; Konst часто не біля ПК — кліп у чат (SendUserFile) він дивиться з телефона, а вирок дає на пристрої.
#   Агент дивиться смугу кадрів (Read) — так сам бачить ваду руху до показу (AE S140: значки стискались до 0 — видно лише на кадрах кліпу).
# Практика: Playwright пише .webm → ffmpeg у MP4 H.264 yuv420p + faststart (старий Safari / iOS .webm не грає; GIF більший і гірший) —
#   flaviocopes «Record a product demo with Playwright», addpipe «inline recorder on iOS»; смуга — фільтри mpdecimate + кадри → плитка
#   (FFmpeg wiki «multiple screenshots to an image (tile)», 12.11.2026).
# Запуск:  python3 clip.py <сценарій.json> <тека виходу>        (сценарій — нижче)
#          python3 clip.py selftest                              (зуби: сторінка з рухом → кліп і ≥ 3 різні кадри; без руху → ✗ «руху не видно»)
# Сценарій JSON: {"url": "...", "name": "rail_C", "viewport": [1920, 1080] | "device": "iPhone 15",
#   "init": ["<js до завантаження>"], "ready": "<js-умова готовності>", "crop": [x, y, w, h],
#   "steps": [{"click": "<css>"}, {"hover": "<css>"}, {"move": [x, y]}, {"fill": ["<css>", "текст"]}, {"press": "Tab"}, {"eval": "<js>"}, {"wait": 900}],
#   "min_frames": 3}
#   Кілька кліпів — список таких об'єктів. Смуга кадрів — <name>_frames.webp (до 12 кадрів, що змінюються).
# Вихід: <name>.mp4 · <name>_frames.webp · рядок «✓ <name>: N кадрів змінюються, T с» або «✗ <name>: руху не видно (…)».
# Потребує: Python Playwright (ставить гачок старту продукту), Pillow і ffmpeg (у хмарному контейнері є; нема — ✗ з назвою).
import sys, os, json, shutil, subprocess, tempfile, pathlib, glob

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
        pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
        for js in sc.get("init", []): pg.add_init_script(js)
        pg.goto(sc["url"])
        if sc.get("ready"): pg.wait_for_function(sc["ready"], timeout=30000)
        pg.wait_for_timeout(sc.get("settle", 600))
        for s in sc.get("steps", []):
            if "click" in s: pg.click(s["click"])
            elif "hover" in s: pg.hover(s["hover"])
            elif "move" in s: pg.mouse.move(*s["move"], steps=8)
            elif "fill" in s: pg.fill(*s["fill"])
            elif "press" in s: pg.keyboard.press(s["press"])
            elif "eval" in s: pg.evaluate(s["eval"])
            if "wait" in s: pg.wait_for_timeout(s["wait"])
        pg.wait_for_timeout(sc.get("tail", 500)); ctx.close(); b.close()
    src = next(vid.glob("*.webm"))
    vf = "fps=30"
    if sc.get("crop"):
        x, y, w, h = sc["crop"]; vf = f"crop={w}:{h}:{x}:{y},fps=30"
    mp4 = out / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-vf", vf + ",scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "24", "-movflags", "+faststart", str(mp4)], check=True)
    fr = pathlib.Path(tempfile.mkdtemp())
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-vf", "mpdecimate=hi=64*12:lo=64*5:frac=0.33,setpts=N/FRAME_RATE/TB",
                    "-fps_mode", "vfr", str(fr / "%04d.png")], check=True)
    frames = sorted(glob.glob(str(fr / "*.png")))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout.strip() or 0)
    if frames:
        from PIL import Image
        step = max(1, len(frames) // 12); pick = frames[::step][:12]
        ims = [Image.open(f) for f in pick]; w, h = ims[0].size; k_ = min(1.0, 480 / w); tw, th = int(w * k_), int(h * k_)
        cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw + (cols - 1) * 8, rows * th + (rows - 1) * 8), "white")
        for k, im in enumerate(ims): sheet.paste(im.resize((tw, th)), ((k % cols) * (tw + 8), (k // cols) * (th + 8)))
        sheet.save(out / f"{name}_frames.webp", "WEBP", quality=80)
    n = len(frames); mn = sc.get("min_frames", 3)
    ok = n >= mn and not errs
    why = (f"руху не видно (кадрів, що змінюються, {n} < {mn})" if n < mn else "") + (f"; помилки сторінки: {'; '.join(errs)}" if errs else "")
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
    for ok, m in [(r1 and (tmp / "out/move.mp4").stat().st_size > 1000 and (tmp / "out/move_frames.webp").exists(), "сторінка з рухом → MP4 + смуга кадрів"),
                  (not r2, "зуби: сторінка без руху → ✗ «руху не видно»")]:
        print(("✓ " if ok else "✗ ") + m); bad += not ok
    print(f"─── clip selftest: {2 - bad}/2 ───"); sys.exit(1 if bad else 0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest": selftest()
    if len(sys.argv) < 3: print("python3 clip.py <сценарій.json> <тека> | selftest"); sys.exit(2)
    need_ffmpeg()
    data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    res = [record(sc, sys.argv[2]) for sc in (data if isinstance(data, list) else [data])]
    sys.exit(0 if all(res) else 1)
