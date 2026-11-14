"""썸네일 기본 디자인 '3D 대비형' 만들기 (채널규칙 2-1, 기준 그림 assets/thumbs/style_ref/3d_contrast_japan.webp).

사용 (neural-studio 에서):
  python3 tools/thumb3d_contrast/make.py projects/oneshot_japan_parts/thumb3d.json assets/thumbs/oneshot_japan_thumb_3d.png
      [--work 임시폴더] [--samples 40] [--threads 2] [--reuse]   # --reuse: Blender 레이어 다시 안 그리고 HTML 만 다시 합성

순서: 설정 JSON → Blender(scene.py, -t 2)로 3D 제목·숫자·화살표·소품을 투명 PNG(1920×1080)로 →
      HTML(흰 바탕 그라데이션·빨간 윗띠·유리 구슬·'vs'·꼬리표·개미·그림자)로 합성 → Chrome 캡처 → 1280×720 축소 + 샤픈.
한 장 약 3~5분(4코어가 바쁠 때, 32~40샘플).

설정 JSON (예: projects/oneshot_japan_parts/thumb3d.json)
  title1, title2           위 2줄 제목 (남색 3D)
  left / right             {"label": 꼬리표(검은 글자), "value": 3D 숫자, "color": "red"|"navy"|"gray"}
  connector                "vs"(회색 글자, 기본) | "arrow"(전→후, 굵은 3D 화살표)
  bubble                   "left" | "right" | null  — 그 숫자 뒤 반투명 유리 구슬 (빨강 쪽에)
  props_left/props_right   소품 이름 목록 (scene.py PROPS: coins cash peso building shield drums oil pumpjack
                           chart_down chart_up vault watch pill). {"name":..,"x":..,"y":..,"s":..,"symbol":"¥"} 로 자리·크기 지정 가능
  mascot                   개미 표정(가리킴 계산 놀람 수익 승리 아이디어 충격 환호) 또는 {"name":..,"x":..,"y":..,"h":..}
  layout                   (선택) scene.py LAYOUT 덮어쓰기, 예 {"right": {"c": [1450, 740]}}
  samples                  (선택) Cycles 샘플
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.abspath(os.path.join(HERE, "..", ".."))
BLENDER = os.environ.get("BLENDER", "/home/user/ext/blender-4.5.9-linux-x64/blender")
FONT = next(p for p in (os.path.join(NS, "assets", "fonts", "BlackHanSans.ttf"),
                        "/home/user/hf/thumb/assets/fonts/BlackHanSans-Regular.ttf") if os.path.exists(p))
MASCOT_DIR = os.environ.get("MASCOT_DIR", "/home/user/hf/thumb/assets/mascot")
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
MASCOT_H = 330  # 화면 높이의 약 30%


def blender(cfg_path, layer, samples, threads):
    cmd = [BLENDER, "-b", "-t", str(threads), "-P", os.path.join(HERE, "scene.py"), "--",
           "--cfg", cfg_path, "--out", layer, "--samples", str(samples)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or not os.path.exists(layer):
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit("Blender 렌더 실패")


def sticker(h):
    w = max(4, round(h / 55))
    return (f"drop-shadow({w}px 0 0 #fff) drop-shadow(-{w}px 0 0 #fff) drop-shadow(0 {w}px 0 #fff) drop-shadow(0 -{w}px 0 #fff) "
            "drop-shadow(0 10px 14px rgba(20,30,60,.35))")


def html(cfg, layer, info):
    L, R = info["left"], info["right"]
    parts = []
    # 유리 구슬 (빨강 숫자 뒤)
    b = cfg.get("bubble")
    bubble_r = 0
    if b in ("left", "right"):
        bb = info[b]
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2 - 10
        d = max(bb[2] - bb[0], bb[3] - bb[1]) * 1.02 + 30
        d = min(d, 800)
        bubble_r = cx + d / 2
        parts.append(
            f'<div class="abs" style="left:{cx - d / 2:.0f}px;top:{cy - d / 2:.0f}px;width:{d:.0f}px;height:{d:.0f}px;border-radius:50%;'
            'background:radial-gradient(circle at 34% 28%,rgba(255,255,255,.95) 0,rgba(255,215,225,.75) 6%,rgba(232,110,135,.6) 28%,'
            'rgba(205,50,82,.66) 60%,rgba(160,14,46,.84) 90%,rgba(125,6,34,.9) 100%);'
            'box-shadow:inset -30px -40px 80px rgba(120,0,30,.35),inset 20px 20px 60px rgba(255,255,255,.45),0 40px 60px rgba(120,20,40,.18)"></div>'
            f'<div class="abs" style="left:{cx - d * 0.30:.0f}px;top:{cy - d * 0.40:.0f}px;width:{d * 0.30:.0f}px;height:{d * 0.16:.0f}px;border-radius:50%;'
            'transform:rotate(-28deg);background:radial-gradient(closest-side,rgba(255,255,255,.9),rgba(255,255,255,0))"></div>')
        # 바닥 그림자
        parts.append(f'<div class="abs" style="left:{cx - d * 0.4:.0f}px;top:{cy + d * 0.46:.0f}px;width:{d * 0.8:.0f}px;height:{d * 0.1:.0f}px;'
                     'border-radius:50%;background:radial-gradient(closest-side,rgba(90,20,40,.25),rgba(90,20,40,0))"></div>')
    # 3D 레이어
    parts.append(f'<img class="abs" src="file://{layer}" style="left:0;top:0;width:1920px;height:1080px;'
                 'filter:drop-shadow(0 3px 2px rgba(10,20,50,.45)) drop-shadow(0 14px 16px rgba(15,25,60,.35))">')
    # 꼬리표
    for side, bb in (("left", L), ("right", R)):
        lab = cfg[side].get("label")
        if not lab:
            continue
        cx = (bb[0] + bb[2]) / 2 + cfg[side].get("label_dx", 0)
        parts.append(
            f'<div class="abs tag" style="left:{cx - 400:.0f}px;width:800px;top:{bb[1] - 128:.0f}px">{lab}</div>')
    # vs / 개미
    mid = cfg.get("connector", "vs")
    gap_l, gap_r = L[2], R[0]
    if mid == "vs":
        vx = gap_l + 95
        if b == "left":
            vx = max(vx, bubble_r + 75)
        vy = (L[1] + L[3]) / 2 + 10
        parts.append(f'<div class="abs vs" style="left:{vx - 100:.0f}px;width:200px;top:{vy - 70:.0f}px">vs</div>')
        mx = (vx + 70 + gap_r) / 2
    else:  # 화살표: 개미는 화살표 아래
        ar = info.get("arrow", [gap_l, 0, gap_r, 700])
        mx = (ar[0] + ar[2]) / 2
        my = 1062
    m = cfg.get("mascot")
    if m:
        if isinstance(m, str):
            m = {"name": m}
        h = m.get("h", MASCOT_H if mid == "vs" else 270)
        x = m.get("x", mx)
        y = m.get("y", R[3] + 10 if mid == "vs" else my)  # 발끝
        parts.append(f'<img class="abs" src="file://{MASCOT_DIR}/{m["name"]}.png" style="left:{x - h * 0.4:.0f}px;top:{y - h:.0f}px;'
                     f'width:{h * 0.8:.0f}px;height:{h:.0f}px;object-fit:contain;filter:{sticker(h)}">')
    body = "".join(parts)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:BH;src:url("file://{FONT}")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;
 background:radial-gradient(1400px 800px at 50% 42%,#ffffff 0%,#fafbfc 45%,#eceef2 100%)}}
.abs{{position:absolute}}
.tag{{font-family:BH;font-size:104px;line-height:1;text-align:center;color:#141414;letter-spacing:-1px;
 -webkit-text-stroke:5px #fff;paint-order:stroke fill;filter:drop-shadow(0 5px 5px rgba(0,0,0,.25))}}
.vs{{font-family:BH;font-size:120px;line-height:1;text-align:center;color:#8b9099;letter-spacing:-2px;
 text-shadow:2px 2px 0 #6f747d,4px 4px 0 #6f747d,6px 6px 0 #5d626a,8px 10px 12px rgba(0,0,0,.3)}}
</style></head><body><div id="root">
<div class="abs" style="left:0;top:0;width:1920px;height:22px;background:linear-gradient(180deg,#f0141e,#c9000c)"></div>
{body}
</div></body></html>"""


def shoot(page_html, png):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        hp = png + ".html"
        open(hp, "w", encoding="utf-8").write(page_html)
        pg.goto("file://" + hp)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        pg.screenshot(path=png)
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cfg")
    ap.add_argument("out")
    ap.add_argument("--work")
    ap.add_argument("--samples", type=int)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--reuse", action="store_true")
    a = ap.parse_args()
    cfg_path = os.path.abspath(a.cfg)
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    name = os.path.splitext(os.path.basename(a.out))[0]
    work = os.path.abspath(a.work or os.path.join(tempfile.gettempdir(), "thumb3d_contrast", name))
    os.makedirs(work, exist_ok=True)
    layer = os.path.join(work, "layer.png")
    t0 = time.time()
    if not (a.reuse and os.path.exists(layer)):
        blender(cfg_path, layer, a.samples or cfg.get("samples", 40), a.threads)
    t1 = time.time()
    info = json.load(open(os.path.join(work, "layer.json")))
    big = os.path.join(work, "full.png")
    shoot(html(cfg, layer, info), big)
    im = Image.open(big).convert("RGB").resize((1280, 720), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    im.save(a.out, optimize=True)
    if os.path.getsize(a.out) > 2_000_000:
        im.convert("P", palette=Image.ADAPTIVE, colors=256).save(a.out, optimize=True)
    shutil.copy(os.path.join(work, "layer.json"), os.path.join(work, "layout_used.json"))
    print(f"저장: {a.out} ({os.path.getsize(a.out) // 1024}KB) · Blender {t1 - t0:.0f}초 · 합성 {time.time() - t1:.0f}초")


if __name__ == "__main__":
    main()
