"""바이럴형 썸네일 (2026-11-21 현철님 레퍼런스: 공포형·반전형·비교형·숫자형).
어두운 시세판 배경 + 빨간 폭락(또는 초록 급등) 화살표 + 두 줄 큰 글씨(흰색, [[강조]]는 노랑/빨강, 굵은 검정 외곽)
+ 크게 박은 숫자 + 놀란 캐릭터(실존 인물 얼굴 금지 → 채널 개미 캐릭터) + 공식 CI(흰 카드). Blender 없이 HTML 한 장, 몇 초.

사용 (neural-studio 에서):
  python3 tools/thumb_viral/make.py 설정.json 출력.png

설정 JSON
  type        "A"(공포: 빨강 폭락) | "B"(반전: 빨강 폭락 뒤 초록 급등) | "C"(비교: 좌우 두 숫자 VS) | "D"(숫자: 화면 가운데 거대한 숫자)
  line1/line2 위 두 줄 제목. [[노랑 강조]] {{빨강 강조}}
  big         (A·B·D) 큰 숫자 {"value": "-26%", "label": "이틀 만에", "color": "red"|"green"|"yellow"}
  left/right  (C) {"label": "2013년 매각 선언", "value": "4.4조", "color": "gray"|"red"|"green"}
  ticker      배경 시세판에 흐리게 깔 숫자 목록(선택)
  ci          {"png": 공식 CI png, "h": 90}  (썸네일에만, 왼쪽 위 흰 카드)
  brand       회사 공식 색(윗띠·CI 카드 테두리)
  mascot      개미 표정 (충격·놀람·계산 …) 또는 null
  stamp       (선택) 오른쪽 위 빨간 도장 문구, 예 "긴급" "반전"
  bg          (선택) AI 시네마틱 배경 그림(assets/thumb_bg/*.png). 넣으면 코드 차트 대신. 실존 인물 아닌 가상 인물만
  shade       (선택) 배경 위 어둡게 깔 CSS 그라데이션
  title_top / title_box [left, width, "left"|"center"|"right"]   제목 자리
  big.box     [left, top, width, 글자크기]   큰 숫자 자리
"""
import json, os, re, sys, random, math
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); NS = os.path.abspath(os.path.join(HERE, "..", ".."))
FONT_BH = os.path.join(NS, "assets", "fonts", "BlackHanSans.ttf")
FONT_PB = os.path.join(NS, "assets", "fonts", "Pretendard-Black.otf")
MASCOT = os.environ.get("MASCOT_DIR", "/home/user/hf/thumb/assets/mascot")
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
COL = {"red": "#ff2d2d", "green": "#22e07a", "yellow": "#ffd400", "gray": "#c9ced8", "white": "#ffffff"}


def marks(s):
    s = re.sub(r"\[\[(.+?)\]\]", r'<span style="color:#ffd400">\1</span>', s)
    return re.sub(r"\{\{(.+?)\}\}", r'<span style="color:#ff3030">\1</span>', s)


def chart_svg(kind, seed=3):
    """배경 캔들 차트 + 굵은 화살표 경로 (1920×1080)."""
    r = random.Random(seed); W, H = 1920, 1080
    if kind == "U":   # 꾸준히 크게 오름
        pts = [(0, 1000), (240, 960), (420, 980), (600, 820), (780, 850), (960, 640), (1140, 670), (1320, 460), (1500, 480), (1700, 260), (1880, 120)]
    elif kind == "B":   # 떨어졌다 크게 반등
        pts = [(0, 300), (300, 360), (520, 520), (700, 640), (860, 860), (980, 900), (1120, 760), (1300, 600), (1500, 380), (1700, 230), (1880, 120)]
    else:             # 계단식 폭락
        pts = [(0, 200), (260, 260), (420, 230), (600, 420), (760, 380), (960, 620), (1120, 560), (1320, 800), (1500, 760), (1700, 960), (1880, 1040)]
    cand = []
    for i in range(46):
        x = 30 + i * 41; t = x / W
        k = min(range(len(pts) - 1), key=lambda j: abs((pts[j][0] + pts[j + 1][0]) / 2 - x))
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]; y = y0 + (y1 - y0) * max(0, min(1, (x - x0) / max(1, x1 - x0)))
        o = y + r.uniform(-40, 40); c = y + r.uniform(-40, 40); hi, lo = min(o, c) - r.uniform(10, 50), max(o, c) + r.uniform(10, 50)
        up = c < o; col = "#e03a3a" if up else "#2f7cf6"
        cand.append(f'<line x1="{x}" y1="{hi:.0f}" x2="{x}" y2="{lo:.0f}" stroke="{col}" stroke-width="3" opacity=".55"/>'
                    f'<rect x="{x - 12}" y="{min(o, c):.0f}" width="24" height="{max(6, abs(o - c)):.0f}" fill="{col}" opacity=".55"/>')
    path = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    up = kind in ("B", "U")
    main = "#22e07a" if up else "#ff1f1f"
    tip = pts[-1]; prev = pts[-2]; ang = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
    def rot(dx, dy): return (tip[0] + dx * math.cos(ang) - dy * math.sin(ang), tip[1] + dx * math.sin(ang) + dy * math.cos(ang))
    head = " ".join(f"{x:.0f},{y:.0f}" for x, y in (rot(40, 0), rot(-70, -62), rot(-70, 62)))
    extra = ""
    if kind == "B":   # 반등 앞부분(하락 구간)은 빨강으로 겹쳐 그림
        dpath = "M " + " L ".join(f"{x},{y}" for x, y in pts[:6])
        extra = f'<path d="{dpath}" fill="none" stroke="#ff1f1f" stroke-width="34" stroke-linejoin="round" filter="url(#g)"/>'
    return f'''<svg class="abs" width="1920" height="1080" viewBox="0 0 1920 1080"><defs>
<filter id="g" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
{''.join(cand)}
<path d="{path}" fill="none" stroke="#000" stroke-opacity=".55" stroke-width="58" stroke-linejoin="round"/>
<path d="{path}" fill="none" stroke="{main}" stroke-width="34" stroke-linejoin="round" filter="url(#g)"/>{extra}
<polygon points="{head}" fill="{main}" stroke="#000" stroke-opacity=".5" stroke-width="6" filter="url(#g)"/></svg>'''


def html(cfg):
    t = cfg.get("type", "A"); brand = cfg.get("brand", "#ff2d2d")
    tick = cfg.get("ticker") or ["163.00", "-3.51%", "486.00", "+2.07", "80.50", "-12.06%", "5,093", "▼698", "2,345", "+0.84%"]
    tk = "".join(f'<div style="left:{40 + (i % 5) * 380}px;top:{90 + (i // 5) * 70 + (i % 2) * 520}px;color:{"#ff5252" if "-" in s or "▼" in s else "#38e08a"}">{s}</div>'
                 for i, s in enumerate(tick * 2))
    chk = cfg.get("chart", {"A": "down", "B": "rebound", "C": None, "D": "up"}[t])
    tint = {"down": "rgba(120,0,0,.35)", "rebound": "rgba(0,70,40,.25)", "up": "rgba(0,80,40,.28)", None: "rgba(20,30,90,.35)"}[chk]
    parts = []
    bgimg = cfg.get("bg")
    if bgimg:   # AI 시네마틱 배경(공용 배경 라이브러리 assets/thumb_bg). 있으면 코드 차트·시세판 대신 씀
        parts.append(f'<img class="abs" src="file://{bgimg}" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover">'
                     f'<div class="abs" style="left:0;top:0;width:1920px;height:1080px;background:{cfg.get("shade", "linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.05) 45%,rgba(0,0,0,.35) 100%)")}"></div>')
    ch = None if bgimg else cfg.get("chart", {"A": "down", "B": "rebound", "C": None, "D": "up"}[t])
    if ch:
        parts.append(chart_svg({"down": "A", "rebound": "B", "up": "U"}[ch]))
    if t == "C":
        parts.append('<div class="abs" style="left:958px;top:330px;width:6px;height:740px;background:linear-gradient(#fff0,#ffffffaa,#fff0)"></div>'
                     '<div class="abs vs" style="left:860px;top:640px;width:200px">VS</div>')
        for side, x in (("left", 70), ("right", 1000)):
            s = cfg[side]; c = COL.get(s.get("color", "gray"), s.get("color"))
            parts.append(f'<div class="abs lab" style="left:{x}px;top:530px;width:850px">{marks(s["label"])}</div>'
                         f'<div class="abs num" style="left:{x}px;top:630px;width:850px;font-size:240px;color:{c}">{s["value"]}</div>')
    if cfg.get("big") and t != "C":
        b = cfg["big"]; c = COL.get(b.get("color", "red"), b.get("color"))
        if t == "D":
            parts.append(f'<div class="abs lab" style="left:{0 if cfg.get("bg") else 300}px;top:540px;width:{1920 if cfg.get("bg") else 1580}px">{marks(b.get("label", ""))}</div>'
                         f'<div class="abs num" style="left:{0 if cfg.get("bg") else 300}px;top:630px;width:{1920 if cfg.get("bg") else 1580}px;font-size:340px;color:{c}">{b["value"]}</div>')
        else:
            bx, by, bw, bs = b.get("box", [960, 560, 940, 260])
            parts.append(f'<div class="abs lab" style="left:{bx}px;top:{by}px;width:{bw}px">{marks(b.get("label", ""))}</div>'
                         f'<div class="abs num" style="left:{bx}px;top:{by + 90}px;width:{bw}px;font-size:{bs}px;color:{c}">{b["value"]}</div>')
    m = cfg.get("mascot")
    if m:
        mx = 50 if t != "C" else 820; mh = 470 if t != "C" else 300
        parts.append(f'<img class="abs" src="file://{MASCOT}/{m}.png" style="left:{mx}px;top:{1080 - mh + 20}px;height:{mh}px;'
                     'filter:drop-shadow(7px 0 0 #fff) drop-shadow(-7px 0 0 #fff) drop-shadow(0 7px 0 #fff) drop-shadow(0 -7px 0 #fff) drop-shadow(0 14px 18px rgba(0,0,0,.7))">')
    ci = cfg.get("ci")
    if ci:
        im = Image.open(ci["png"]); h = ci.get("h", 90); w = h * im.width / im.height; pad = 22
        parts.append(f'<div class="abs" style="left:36px;top:40px;width:{w + 2 * pad:.0f}px;height:{h + 2 * pad:.0f}px;background:#fff;border-radius:22px;'
                     f'box-shadow:0 0 0 5px {brand},0 12px 30px rgba(0,0,0,.6)"></div>'
                     f'<img class="abs" src="file://{ci["png"]}" style="left:{36 + pad}px;top:{40 + pad}px;height:{h}px;width:{w:.0f}px">')
    if cfg.get("stamp"):
        parts.append(f'<div class="abs stamp">{cfg["stamp"]}</div>')
    top = cfg.get("title_top", 175 if ci else 50)
    tx, tw, ta = cfg.get("title_box", [40, 1840, "center"])
    def fit(txt, size):   # 한 줄에 들어가게 글자 크기 줄이기 (Black Han Sans 글자 폭 ≈ 0.95em, 공백 ≈ 0.3em)
        plain = re.sub(r"\[\[|\]\]|\{\{|\}\}", "", txt); w = sum(0.3 if ch == " " else (0.62 if ch.isascii() else 0.95) for ch in plain) * size
        return int(size * min(1, (tw - 40) / max(w, 1)))
    s1 = fit(cfg["line1"], cfg.get("size1", 172)); s2 = fit(cfg.get("line2", ""), cfg.get("size2", 158))
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:BH;src:url("file://{FONT_BH}")}}@font-face{{font-family:PB;src:url("file://{FONT_PB}")}}
*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#05070d}}
.abs{{position:absolute}}
#bg{{position:absolute;inset:0;background:radial-gradient(1200px 700px at 70% 60%,#1b2a4a 0%,#0a1020 55%,#04060c 100%)}}
#grid{{position:absolute;inset:0;background-image:linear-gradient(#ffffff0d 1px,transparent 1px),linear-gradient(90deg,#ffffff0d 1px,transparent 1px);background-size:96px 96px}}
#tick div{{position:absolute;font-family:PB;font-size:58px;opacity:.16;letter-spacing:1px}}
#tint{{position:absolute;inset:0;background:{tint}}}
#vig{{position:absolute;inset:0;background:radial-gradient(1400px 900px at 50% 45%,transparent 50%,rgba(0,0,0,.75) 100%)}}
.title{{position:absolute;left:40px;width:1840px;text-align:center;font-family:BH;line-height:1.08;white-space:nowrap;color:#fff;letter-spacing:-2px;
  -webkit-text-stroke:16px #000;paint-order:stroke fill;filter:drop-shadow(0 8px 10px rgba(0,0,0,.8))}}
.lab{{font-family:BH;font-size:86px;text-align:center;color:#fff;-webkit-text-stroke:12px #000;paint-order:stroke fill;filter:drop-shadow(0 6px 8px rgba(0,0,0,.8))}}
.num{{font-family:BH;line-height:1;text-align:center;letter-spacing:-6px;-webkit-text-stroke:20px #000;paint-order:stroke fill;
  filter:drop-shadow(0 0 30px rgba(0,0,0,.9)) drop-shadow(0 12px 14px rgba(0,0,0,.9))}}
.vs{{font-family:BH;font-size:150px;text-align:center;color:#ffd400;-webkit-text-stroke:14px #000;paint-order:stroke fill}}
.stamp{{right:46px;top:46px;padding:10px 34px;font-family:BH;font-size:84px;color:#fff;background:#e00000;border:8px solid #fff;border-radius:18px;transform:rotate(6deg);
  box-shadow:0 12px 26px rgba(0,0,0,.6)}}
</style></head><body>
<div id="bg"></div><div id="grid"></div><div id="tick">{tk}</div><div id="tint"></div>
<div class="abs" style="left:0;top:0;width:1920px;height:16px;background:{brand}"></div>
{"".join(parts)}<div id="vig" style="pointer-events:none"></div>
<div class="title" style="top:{top}px;left:{tx}px;width:{tw}px;text-align:{ta};font-size:{s1}px">{marks(cfg["line1"])}</div>
<div class="title" style="top:{top + int(s1 * 1.1)}px;left:{tx}px;width:{tw}px;text-align:{ta};font-size:{s2}px">{marks(cfg.get("line2", ""))}</div>
</body></html>'''


def shoot(page, png):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1920, "height": 1080}); hp = png + ".html"
        open(hp, "w", encoding="utf-8").write(page); pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
        pg.screenshot(path=png); b.close(); os.remove(hp)


if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1], encoding="utf-8")); out = os.path.abspath(sys.argv[2]); big = out + ".full.png"
    shoot(html(cfg), big)
    im = Image.open(big).convert("RGB").resize((1280, 720), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    im.save(out, optimize=True); os.remove(big); print("저장:", out, os.path.getsize(out) // 1024, "KB")
