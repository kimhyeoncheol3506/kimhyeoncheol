#!/usr/bin/env python3
"""세로 쇼츠(1080x1920)용 HTML 모션 장면 렌더러.

원리(스마트대디 모션 카드 방식을 배워 적용): HTML 에 window.render(t, dur, data) 순수함수를 두고,
크로미움(playwright)으로 프레임마다 t 를 넣어 화면을 찍고 ffmpeg 로 묶는다. 같은 t 면 항상 같은 그림.

  python shorts/render_card.py shorts/scene.html out.mp4 --dur 4 --data '{"kind":"hook","line1":"..."}'
  python shorts/render_card.py shorts/scene.html outdir --frames 0.5,2,3.5 --data '{...}'   # PNG 몇 장만
"""
import argparse, functools, glob, http.server, json, subprocess, sys, threading, urllib.parse
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("out")
ap.add_argument("--dur", type=float, default=4.0); ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--data", default="{}", help="HTML 에 넘길 JSON")
ap.add_argument("--frames", default="", help="이 시각들(초)만 PNG 로 저장")
ap.add_argument("--size", default="1080x1920"); ap.add_argument("--crf", type=int, default=18)
a = ap.parse_args()
W, H = map(int, a.size.split("x"))
from playwright.sync_api import sync_playwright

html = Path(a.html).resolve()
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(html.parent)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{srv.server_address[1]}/{urllib.parse.quote(html.name)}"
chrome = next(iter(sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))), None)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path=chrome)
    pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_load_state("networkidle"); pg.evaluate("document.fonts.ready")
    pg.evaluate(f"window.DATA = {a.data}")
    if a.frames:
        Path(a.out).mkdir(parents=True, exist_ok=True)
        for t in [float(x) for x in a.frames.split(",") if x.strip()]:
            pg.evaluate(f"window.render({t},{a.dur})"); p = Path(a.out) / f"f_{t:05.2f}.png"; pg.screenshot(path=str(p)); print("저장", p)
    else:
        n = round(a.dur * a.fps)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"window.render({i / a.fps},{a.dur})"); ff.stdin.write(pg.screenshot(type="png"))
        ff.stdin.close(); ff.wait(); print("완료", a.out, f"({n}프레임)")
    br.close()
    if errs: print("HTML 오류:", *errs, sep="\n  ")
srv.shutdown()
