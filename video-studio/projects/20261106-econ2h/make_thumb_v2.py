"""33편 썸네일 v2 (현철님 2026-11-08: 레퍼런스 글체 — 굵은 고딕, 흰 글씨+두꺼운 검정 외곽선, 강조 노랑, 따옴표 강조)
제목 '월급쟁이 필수 경제 지식 완전정리'를 세련되게, 후보 3개(A·B·C). 실존 인물 얼굴 없음(마스코트)."""
import os, shutil, subprocess, sys
ROOT = "/home/user/hf/thumb"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
Y = "#FFE14D"


def T(html, x, y, size, stroke=None, align="left", extra=""):
    """흰 글씨 + 두꺼운 검정 외곽선(뒤 레이어) + 그림자. html 안에서 <b>는 노랑"""
    sw = stroke or max(10, int(size * 0.16))
    pos = f"left:{x}px;top:{y}px" if align == "left" else f"left:0;right:0;top:{y}px;text-align:center"
    base = f"position:absolute;{pos};font-family:BH;font-size:{size}px;line-height:1.02;white-space:nowrap;letter-spacing:-2px;{extra}"
    return (f'<div style="{base};color:#000;-webkit-text-stroke:{sw}px #000;filter:drop-shadow(0 10px 0 rgba(0,0,0,.55)) drop-shadow(0 0 30px rgba(0,0,0,.6))">{html}</div>'
            f'<div style="{base};color:#fff">{html}</div>')


def candles(color="#E2B046", n=26, x0=700, w=1220, top=120, h=560, seed=3, op=.55):
    import random
    r = random.Random(seed)
    v, out, step = .7, [], w / n
    for i in range(n):
        o = v; v = max(.08, min(.95, v + r.uniform(-.14, .1) + (-.01 if i < n * .6 else .035)))
        hi, lo = max(o, v) + r.uniform(.02, .07), min(o, v) - r.uniform(.02, .07)
        cx = x0 + i * step; c = "#3DDC97" if v > o else "#FF4D5E"
        y = lambda q: top + (1 - q) * h
        out.append(f'<line x1="{cx+step*.32}" y1="{y(hi)}" x2="{cx+step*.32}" y2="{y(lo)}" stroke="{c}" stroke-width="4"/>'
                   f'<rect x="{cx+step*.12}" y="{y(max(o,v))}" width="{step*.4}" height="{max(6,abs(y(o)-y(v)))}" fill="{c}"/>')
    return f'<svg class="abs" style="left:0;top:0;opacity:{op}" width="1920" height="1080">{"".join(out)}</svg>'


def newspaper():
    cols = []
    for c in range(7):
        x = 40 + c * 270
        cols.append(f'<rect x="{x}" y="70" width="240" height="34" fill="#cfc8b8"/>')
        for k in range(38):
            wv = 240 - (k * 53 % 70) if k % 6 else 150
            cols.append(f'<rect x="{x}" y="{130 + k * 24}" width="{wv}" height="11" fill="#bdb6a6"/>')
    return f'<svg class="abs" style="left:-80px;top:-60px;transform:rotate(-7deg) scale(1.15);opacity:.22" width="2100" height="1200">{"".join(cols)}</svg>'


def mascot(name, right=40, bottom=-10, w=520, glow="#FFD43B"):
    return (f'<div class="abs" style="right:{right}px;bottom:{bottom}px;width:{w}px;height:{int(w*1.25)}px">'
            f'<img src="assets/mascot/{name}.png" style="width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 0 40px {glow}88) drop-shadow(0 24px 40px rgba(0,0,0,.8))"></div>')


def chip(text, x, y, bg=Y, fg="#111", size=44):
    return f'<div class="abs" style="left:{x}px;top:{y}px;padding:10px 28px 12px;border-radius:14px;background:{bg};color:{fg};font-family:PB;font-size:{size}px;box-shadow:0 8px 0 rgba(0,0,0,.5)">{text}</div>'


BRAND = '<div class="abs" style="left:64px;top:52px;font-family:PB;font-size:38px;color:#fff;opacity:.9;letter-spacing:-1px">월급쟁이 재테크 스킬</div>'


def design(v):
    if v == "A":  # 왼쪽 쌓기 — 따옴표 강조 + 금빛 캔들 배경
        bg = "radial-gradient(1200px 900px at 78% 45%,#2a2410 0%,#12131a 45%,#07080c 100%)"
        body = (candles() +
                '<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(7,8,12,.96) 0%,rgba(7,8,12,.75) 42%,rgba(7,8,12,0) 70%)"></div>' +
                mascot("놀람", right=50, w=600) + BRAND +
                T(f'<b style="color:{Y}">‘</b>월급쟁이 필수<b style="color:{Y}">’</b>', 64, 250, 130) +
                T('경제 지식', 58, 400, 260) +
                T(f'<b style="color:{Y}">완전정리</b>', 58, 680, 280) +
                chip("2시간 몰아보기", 1250, 70))
    elif v == "B":  # 가운데 쌓기 — 신문 배경 + 돋보기
        bg = "radial-gradient(1300px 800px at 50% 50%,#25272e 0%,#101116 60%,#050507 100%)"
        lens = ('<div class="abs" style="left:70px;top:620px;width:340px;height:340px;border-radius:50%;border:26px solid #1b1b1b;'
                'background:radial-gradient(circle at 35% 30%,rgba(255,255,255,.28),rgba(255,255,255,.05) 60%);box-shadow:0 0 0 8px #5a5a5a,0 30px 60px rgba(0,0,0,.7)">'
                '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:BH;font-size:100px;color:#FF4D5E;-webkit-text-stroke:3px #000">금리</div></div>'
                '<div class="abs" style="left:350px;top:900px;width:56px;height:200px;background:linear-gradient(90deg,#222,#444,#222);border-radius:18px;transform:rotate(-40deg);transform-origin:top"></div>')
        body = (newspaper() + '<div class="abs" style="inset:0;background:radial-gradient(900px 600px at 50% 55%,rgba(0,0,0,.65),rgba(0,0,0,.15))"></div>' + lens +
                mascot("걱정", right=20, bottom=-30, w=470) + BRAND +
                T(f'월급쟁이라면 <b style="color:{Y}">‘꼭’</b>', 0, 175, 140, align="c") +
                T('필수 경제 지식', 0, 360, 230, align="c") +
                T(f'<b style="color:{Y}">완전정리</b>', 0, 640, 270, align="c"))
    else:  # 왼쪽 큰 제목 + 노랑 하이라이트 띠 + 8개 키워드
        bg = "linear-gradient(135deg,#0d1b2a 0%,#0a0f1a 55%,#050608 100%)"
        kws = ["통화량", "리스크", "금리", "환율", "부동산", "부채", "경제위기"]
        row = "".join(f'<span style="display:inline-block;margin:0 14px 16px 0;padding:8px 22px 10px;border:3px solid #ffffff55;border-radius:999px;color:#fff;background:rgba(255,255,255,.06)">{k}</span>' for k in kws)
        body = (candles(n=30, x0=900, w=1000, top=160, h=520, seed=11, op=.35) +
                '<div class="abs" style="right:120px;top:180px;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,#FFD43B55,transparent 65%)"></div>' +
                mascot("충격", right=70, w=540) + BRAND +
                T('월급쟁이 필수', 64, 150, 140) +
                f'<div class="abs" style="left:46px;top:590px;width:1000px;height:160px;background:{Y};transform:skewX(-8deg);box-shadow:0 10px 0 rgba(0,0,0,.5)"></div>' +
                T('경제 지식', 58, 305, 235) +
                '<div class="abs" style="left:66px;top:598px;font-family:BH;font-size:150px;line-height:1.02;color:#111;letter-spacing:-2px">완전정리 <span style="font-size:96px">2시간</span></div>' +
                f'<div class="abs" style="left:64px;top:800px;width:1300px;font-family:PB;font-size:38px">{row}</div>')
    return bg, body


def render(v, dst):
    bg, body = design(v)
    html = f"""<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>
@font-face{{font-family:BH;src:url("assets/fonts/BlackHanSans-Regular.ttf")}}@font-face{{font-family:PB;src:url("assets/fonts/Pretendard-Black.otf")}}
*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#000}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{bg}}}.abs{{position:absolute}}b{{font-weight:inherit}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080">
<div class="abs clip" data-start="0" data-duration="2" data-track-index="0" style="inset:0">{body}</div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="1" style="inset:0;box-shadow:inset 0 0 220px rgba(0,0,0,.75)"></div>
</div><script>const tl=gsap.timeline({{paused:true}});window.__timelines["main"]=tl;tl.seek(0);</script></body></html>"""
    open(f"{ROOT}/index.html", "w", encoding="utf-8").write(html)
    out = f"/tmp/claude-0/hft/v2{v}"
    shutil.rmtree(out, ignore_errors=True)
    subprocess.run(["npx", "-y", "hyperframes", "snapshot", "--at", "1.0", "-o", out, "--no-end"], cwd=ROOT, check=True, capture_output=True)
    src = [f for f in os.listdir(out) if f.startswith("frame-00")][0]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/{src}", "-vf", "scale=1280:720:flags=lanczos", dst], check=True)
    return dst


if __name__ == "__main__":
    for v in (sys.argv[1:] or ["A", "B", "C"]):
        print(render(v, f"/tmp/claude-0/hft/v2_{v}.png"))
