"""사이버·3D 썸네일 공용 도구 (현철님 지정 2026-11-06: '3D나 더 멋지게 사이버틱하게' — 이후 모든 영상 기본)
VAR=A: 고정 글체(금빛/흰 글씨) 유지 + 3D 돌출·네온 테두리 + 사이버 그리드 배경 + 3D 막대 전광판
VAR=B: 글자도 네온(청록·자홍) 크롬 3D + 신스웨이브 그리드·태양
VAR=C: 크롬 금속 3D 글자 + 홀로그램 데이터 도시
VAR=D: 금빛 3D 블록 글자(두께감) + 회로 기판·글리치
사용(파이썬): from tools.thumb_cyber import render
  render("out.png", "A", "윗줄 문구", "아랫줄 문구", mascot="충격",
         data=dict(left="다우 +3%", right="코스피 −5.28%", left_bars=[...], right_bars=[...], chip="−5.28%",
                   line="M80,200 L...", line_color="#ff3b5c"))
마스코트: assets/mascot/<이름>.png (충격·걱정·놀람). 결과는 1280x720 PNG."""
import os, subprocess, sys, shutil
ROOT = "/home/user/hf/thumb"


def ext(col, n=16, dx=1, dy=1.4):  # 3D 돌출(겹친 그림자)
    return ",".join(f"{dx * k:.1f}px {dy * k:.1f}px 0 {col}" for k in range(1, n + 1))


GRID = """<div class="abs" style="left:-50%;top:560px;width:200%;height:900px;transform-origin:50% 0;transform:perspective(600px) rotateX(70deg);
background-image:linear-gradient(rgba(0,255,240,.75) 3px,transparent 3px),linear-gradient(90deg,rgba(0,255,240,.75) 3px,transparent 3px);background-size:90px 90px;
mask-image:linear-gradient(180deg,rgba(0,0,0,.2),#000 40%);-webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.2),#000 40%)"></div>"""


def bars3d(D):
    out = ['<div class="abs" style="left:120px;top:60px;width:1700px;height:520px;perspective:1400px">',
           '<div style="position:absolute;inset:0;transform:rotateX(16deg) rotateY(-24deg);transform-style:preserve-3d">']
    us = D.get("left_bars", [90, 120, 110, 160, 190, 240, 300, 380])
    kr = D.get("right_bars", [380, 340, 330, 270, 230, 180, 120, 70])
    for i, h in enumerate(us + kr):
        x = 60 + i * 96 + (80 if i >= 8 else 0)
        c = "#ff3b5c" if i < 8 else "#00e5ff"
        out.append(f'<div style="position:absolute;left:{x}px;bottom:0;width:56px;height:{h}px;background:linear-gradient(180deg,{c},{c}88);box-shadow:0 0 30px {c},inset 0 0 12px #fff6;transform:translateZ(0)"></div>'
                   f'<div style="position:absolute;left:{x + 56}px;bottom:0;width:26px;height:{h}px;background:{c}55;transform-origin:0 50%;transform:rotateY(90deg)"></div>'
                   f'<div style="position:absolute;left:{x}px;bottom:{h}px;width:56px;height:26px;background:#ffffffaa;transform-origin:50% 100%;transform:rotateX(90deg)"></div>')
    out.append('</div></div>')
    out.append(f'<div class="abs" style="left:150px;top:40px;font-family:BH;font-size:84px;color:#ff3b5c;text-shadow:0 0 24px #ff3b5c">{D.get("left", "")}</div>'
               f'<div class="abs" style="left:1180px;top:40px;font-family:BH;font-size:84px;color:#00e5ff;text-shadow:0 0 24px #00e5ff">{D.get("right", "")}</div>')
    return "".join(out)


def synth():
    stripes = "".join(f'<div style="position:absolute;left:0;right:0;top:{150 + k * 34}px;height:{6 + k * 3}px;background:#140022"></div>' for k in range(6))
    return (f'<div class="abs" style="left:610px;top:40px;width:700px;height:700px;border-radius:50%;background:linear-gradient(180deg,#ffe066 0%,#ff4fa3 55%,#8a2be2 100%);box-shadow:0 0 120px #ff4fa3;overflow:hidden">{stripes}</div>'
            + "".join(f'<div class="abs" style="left:{x}px;top:{560 - h}px;width:{w}px;height:{h}px;background:#0a0418;box-shadow:inset 0 0 0 3px #ff4fa366"></div>'
                      for x, w, h in [(0, 160, 260), (150, 120, 380), (260, 180, 300), (1460, 150, 340), (1600, 190, 260), (1780, 140, 400)]))


def holo_city(D):
    b = []
    for i in range(18):
        x, w, h = i * 110, 90 + (i * 37) % 50, 200 + (i * 97) % 330
        b.append(f'<div class="abs" style="left:{x}px;top:{580 - h}px;width:{w}px;height:{h}px;border:3px solid #00e5ffaa;background:linear-gradient(180deg,#00e5ff22,#7a00ff11);box-shadow:0 0 22px #00e5ff55;'
                 f'background-image:repeating-linear-gradient(180deg,#00e5ff33 0 6px,transparent 6px 28px)"></div>')
    b.append(f'<svg class="abs" style="left:0;top:0" width="1920" height="600"><path d="{D.get("line", "M80,200 L380,260 L700,230 L1000,330 L1300,420 L1600,470 L1860,560")}" fill="none" stroke="{D.get("line_color", "#ff3b5c")}" stroke-width="14" style="filter:drop-shadow(0 0 16px #ff3b5c)"/></svg>')
    return "".join(b)


def circuit(D):
    lines = []
    for k in range(26):
        y = 30 + k * 22
        x0 = (k * 173) % 1700
        lines.append(f'<path d="M{x0},{y} h{120 + (k * 41) % 260} l40,40 h{100 + (k * 29) % 200}" fill="none" stroke="#00ff9c" stroke-opacity=".55" stroke-width="4"/><circle cx="{x0}" cy="{y}" r="7" fill="#00ff9c"/>')
    chip = f'<rect x="760" y="140" width="400" height="300" rx="20" fill="#0b1a14" stroke="#00ff9c" stroke-width="8"/><text x="960" y="320" text-anchor="middle" font-family="BH" font-size="110" fill="#00ff9c" style="filter:drop-shadow(0 0 18px #00ff9c)">{D.get("chip", "")}</text>'
    return f'<svg class="abs" style="left:0;top:0;filter:drop-shadow(0 0 6px #00ff9c)" width="1920" height="620">{"".join(lines)}{chip}</svg>'




def render(dst, VAR, L1, L2, mascot="충격", data=None):
    D = data or {}
    MASCOT = mascot
    BG = {"A": ("radial-gradient(1400px 800px at 50% 40%,#1a0a3a 0%,#07041a 60%,#02010a 100%)", bars3d(D) + GRID),
          "B": ("linear-gradient(180deg,#12002b 0%,#2a0050 45%,#0a0016 70%)", synth() + GRID.replace("0,255,240", "255,79,163")),
          "C": ("linear-gradient(180deg,#02101e 0%,#041f3a 55%,#010812 100%)", holo_city(D) + GRID.replace("0,255,240", "0,229,255")),
          "D": ("linear-gradient(180deg,#02140d 0%,#031f14 60%,#010805 100%)", circuit(D))}[VAR]

    if VAR == "A":  # 고정 글체 + 3D 돌출 + 네온 테두리
        S1 = f"background:linear-gradient(180deg,#FFF6B0 0%,#FFD43B 38%,#F59F00 72%,#C26A00 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 18px #ffb300) drop-shadow(0 6px 0 #8a4b00)"
        S1b = f"color:#3a1d00;-webkit-text-stroke:30px #1a0d00;text-shadow:{ext('#000', 14)}"
        S2 = "color:#fff;filter:drop-shadow(0 0 14px #00e5ff)"
        S2b = f"color:#000;-webkit-text-stroke:44px #000;text-shadow:{ext('#00e5ff', 3, 2, 2)},{ext('#001018', 18)}"
    elif VAR == "B":  # 네온 크롬
        S1 = "color:#fff;-webkit-text-stroke:3px #00f0ff;text-shadow:0 0 12px #00f0ff,0 0 40px #00f0ff"
        S1b = f"color:#00313a;text-shadow:{ext('#003a44', 14)}"
        S2 = "background:linear-gradient(180deg,#ffffff 0%,#ffd1f0 45%,#ff4fa3 55%,#8a2be2 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 22px #ff4fa3)"
        S2b = f"color:#1a0030;-webkit-text-stroke:36px #1a0030;text-shadow:{ext('#ff4fa3', 2, 2, 2)},{ext('#2a0050', 18)}"
    elif VAR == "C":  # 크롬 금속
        S1 = "background:linear-gradient(180deg,#ffffff 0%,#b8c6d9 45%,#5b6b80 52%,#e8f0ff 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 10px #00e5ff)"
        S1b = f"color:#0b1622;-webkit-text-stroke:26px #0b1622;text-shadow:{ext('#000', 12)}"
        S2 = "background:linear-gradient(180deg,#ffffff 0%,#d9e4f5 40%,#6b7c93 52%,#ffffff 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 18px #00e5ff)"
        S2b = f"color:#000;-webkit-text-stroke:42px #000;text-shadow:{ext('#00e5ff', 2, 2, 2)},{ext('#02101e', 18)}"
    else:  # 금빛 블록 3D
        S1 = "background:linear-gradient(180deg,#FFF6B0 0%,#FFD43B 45%,#F59F00 100%);-webkit-background-clip:text;background-clip:text;color:transparent"
        S1b = f"color:#7a4a00;text-shadow:{ext('#7a4a00', 18, 1.2, 1.6)},{ext('#000', 4, 2, 3)}"
        S2 = "color:#fff"
        S2b = f"color:#888;-webkit-text-stroke:40px #000;text-shadow:{ext('#00ff9c', 2, 2, 2)},{ext('#00331f', 20, 1.2, 1.6)}"

    html = f"""<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
    @font-face{{font-family:BH;src:url("assets/fonts/BlackHanSans-Regular.ttf")}}
    @font-face{{font-family:PB;src:url("assets/fonts/Pretendard-Black.otf")}}
    *{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:1920px;height:1080px;overflow:hidden;background:#02010a}}
    #root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{BG[0]}}}
    .abs{{position:absolute}}
    .t{{position:absolute;left:84px;font-family:BH;white-space:nowrap;line-height:1;transform:skewX(-5deg)}}
    #l1b,#l1{{top:560px;font-size:170px}} #l2b,#l2{{top:745px;font-size:250px;left:96px}}
    #l1b{{{S1b}}} #l1{{{S1}}} #l2b{{{S2b}}} #l2{{{S2}}}
    .scan{{background:repeating-linear-gradient(180deg,rgba(255,255,255,.035) 0 2px,transparent 2px 5px)}}
    </style></head><body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080">
    <div class="abs clip" data-start="0" data-duration="2" data-track-index="0" style="inset:0">{BG[1]}</div>
    <div class="abs clip scan" data-start="0" data-duration="2" data-track-index="1" style="inset:0"></div>
    <div class="abs clip" data-start="0" data-duration="2" data-track-index="2" style="inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 45%,rgba(0,0,0,.6) 100%)"></div>
    <div class="abs clip" data-start="0" data-duration="2" data-track-index="3" style="right:-10px;bottom:-20px;width:440px;height:550px"><img src="assets/mascot/{MASCOT}.png" style="width:100%;height:100%;filter:drop-shadow(0 0 30px {'#00e5ff' if VAR != 'B' else '#ff4fa3'}) drop-shadow(0 20px 40px rgba(0,0,0,.7))"></div>
    <svg class="abs clip" data-start="0" data-duration="2" data-track-index="4" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><defs><filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035 0.2" numOctaves="3" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="34"/></filter></defs>
    <path d="M70,1030 C380,995 800,1055 1150,1015 C1250,1005 1280,1040 1200,1055 C860,1088 420,1078 110,1088 C40,1088 40,1050 70,1030 Z" fill="{'#E11D2E' if VAR in 'AD' else ('#ff2bd6' if VAR == 'B' else '#00b7ff')}" filter="url(#rough)" style="filter:url(#rough) drop-shadow(0 0 18px {'#ff3b5c' if VAR in 'AD' else '#ff2bd6'})"/></svg>
    <div class="t clip" id="l1b" data-start="0" data-duration="2" data-track-index="5">{L1}</div><div class="t clip" id="l1" data-start="0" data-duration="2" data-track-index="6">{L1}</div>
    <div class="t clip" id="l2b" data-start="0" data-duration="2" data-track-index="7">{L2}</div><div class="t clip" id="l2" data-start="0" data-duration="2" data-track-index="8">{L2}</div>
    <div class="abs clip" data-start="0" data-duration="2" data-track-index="9" style="right:48px;top:520px;padding:14px 34px;border-radius:40px;background:rgba(5,7,15,.85);border:4px solid {'#00e5ff' if VAR != 'B' else '#ff4fa3'};box-shadow:0 0 22px {'#00e5ff' if VAR != 'B' else '#ff4fa3'};font-family:PB;font-size:46px;color:#fff">월급쟁이 재테크 스킬</div>
    </div>
    <script>const tl=gsap.timeline({{paused:true}});window.__timelines["main"]=tl;tl.seek(0);</script></body></html>"""
    open(f"{ROOT}/index.html", "w", encoding="utf-8").write(html)
    out = f"/tmp/claude-0/hft/cy{VAR}"
    shutil.rmtree(out, ignore_errors=True)
    subprocess.run(["npx", "-y", "hyperframes", "snapshot", "--at", "1.0", "-o", out, "--no-end"], cwd=ROOT, check=True, capture_output=True)
    src = [f for f in os.listdir(out) if f.startswith("frame-00")][0]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/{src}", "-vf", "scale=1280:720:flags=lanczos", dst], check=True)
    return dst


if __name__ == "__main__":
    print(render(sys.argv[1], os.environ.get("VAR", "A"), sys.argv[2], sys.argv[3], os.environ.get("MASCOT", "충격")))
