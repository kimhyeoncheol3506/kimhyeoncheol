"""쇼츠 장면 렌더 라이브러리: scene.html 을 프레임으로 찍어 mp4 로 만들고, '아래 18% 비움'을 픽셀로 검사한다."""
import functools, glob, http.server, io, subprocess, threading, urllib.parse
from pathlib import Path
import numpy as np
from PIL import Image

W, H = 1080, 1920


class _Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *x):
        pass


def _draw(pg, t, dur):
    pg.evaluate(f"window.render({t},{dur})")
    pg.evaluate("window.__ready ? window.__ready() : null")      # 영상 프레임 이미지가 다 뜰 때까지


def _bottom_diff(pg, t, dur, y0):
    """내용을 보이게/숨기게 두 번 찍어 아래 영역(y0~끝)의 차이 픽셀 수를 센다. 0 이면 비어 있음."""
    clip = {"x": 0, "y": y0, "width": W, "height": H - y0}
    pg.evaluate("document.body.classList.remove('hide')")
    _draw(pg, t, dur)
    a = np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=clip, type="png"))).convert("RGB")).astype(int)
    pg.evaluate("document.body.classList.add('hide')")
    b = np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=clip, type="png"))).convert("RGB")).astype(int)
    pg.evaluate("document.body.classList.remove('hide')")
    return int((np.abs(a - b).max(axis=2) > 10).sum())


def render_scene(html, data, dur, out_mp4, fps=30, crf=18, empty_ratio=0.18, guard_every=0.4, frames_dir=None, frames_at=()):
    """장면 하나를 렌더. 돌려주는 값: 아래 영역 침범 목록 [(t, 픽셀수)]"""
    from playwright.sync_api import sync_playwright
    import json
    html = Path(html).resolve()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Q, directory=str(html.parent)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/{urllib.parse.quote(html.name)}"
    chrome = next(iter(sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))), None)
    y0 = int(round(H * (1 - empty_ratio)))
    viol, errs = [], []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.evaluate("window.DATA = " + json.dumps(data, ensure_ascii=False))
        n = max(1, round(dur * fps))
        step = max(1, round(guard_every * fps))
        if out_mp4:
            ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                                   "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", str(out_mp4)],
                                  stdin=subprocess.PIPE)
        for i in range(n):
            t = i / fps
            _draw(pg, t, dur)
            if out_mp4:
                ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
            if i % step == 0 or i == n - 1:
                bad = _bottom_diff(pg, t, dur, y0)
                if bad > 0:
                    viol.append((round(t, 2), bad))
        for t in frames_at:
            _draw(pg, t, dur)
            Path(frames_dir).mkdir(parents=True, exist_ok=True)
            pg.screenshot(path=str(Path(frames_dir) / f"f_{t:05.2f}.png"))
        if out_mp4:
            ff.stdin.close()
            ff.wait()
        br.close()
    srv.shutdown()
    if errs:
        raise RuntimeError("HTML 오류: " + "; ".join(errs[:3]))
    return viol
