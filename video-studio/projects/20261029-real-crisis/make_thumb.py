"""썸네일: 참고 이미지의 글체(금빛 3D 1줄 + 흰 글자 검정 외곽 2줄 + 빨간 붓터치)에 영상 흐름(주가 폭락 × 환율 엇갈림)에 맞는 배경"""
import os, random, subprocess, sys, shutil
VAR = os.environ.get("VAR", "A")
ROOT = "/home/user/hf/thumb"
random.seed(26)
# 캔들: 주가 폭락(파랑=하락, 한국식) 
cs, p = [], 400.0
for i in range(26):
    o = p
    p = p - random.uniform(6, 34) + random.uniform(-12, 10) * (1 if i % 5 else -1.5)
    h, l = max(o, p) + random.uniform(6, 26), min(o, p) - random.uniform(6, 26)
    cs.append((o, p, h, l))
lo = min(c[3] for c in cs); hi = max(c[2] for c in cs)
X0, X1, Y0, Y1 = 40, 1880, 140, 1000
def Y(v): return Y1 - (v - lo) / (hi - lo) * (Y1 - Y0) * 0.9
cw = (X1 - X0) / len(cs)
candles = []
for i, (o, c, h, l) in enumerate(cs):
    x = X0 + i * cw + cw / 2
    up = c >= o
    col = "#FF4D5E" if up else "#3D8BFF"
    candles.append(f'<line x1="{x:.0f}" y1="{Y(h):.0f}" x2="{x:.0f}" y2="{Y(l):.0f}" stroke="{col}" stroke-width="5"/>'
                   f'<rect x="{x - cw * 0.3:.0f}" y="{min(Y(o), Y(c)):.0f}" width="{cw * 0.6:.0f}" height="{max(8, abs(Y(o) - Y(c))):.0f}" fill="{col}" rx="3"/>')
# 환율 급등선 (빨강, 우상향)
pts = [(X0 + (X1 - X0) * k / 9, 930 - (k / 9) ** 1.7 * 700 + random.uniform(-25, 25)) for k in range(10)]
fx = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
html = f"""<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:BH;src:url("assets/fonts/BlackHanSans-Regular.ttf")}}
@font-face{{font-family:PB;src:url("assets/fonts/Pretendard-Black.otf")}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:1920px;height:1080px;overflow:hidden;background:#05070f}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{"radial-gradient(1300px 900px at 18% 95%,#6b0f1f 0%,#2a0b18 38%,#070b18 78%)" if VAR != "B" else "radial-gradient(1500px 1000px at 80% 10%,#7a1020 0%,#2a0810 45%,#05060d 85%)"}}}
.abs{{position:absolute}}
.t{{position:absolute;left:84px;font-family:BH;white-space:nowrap;line-height:1}}
#l1b{{top:128px;font-size:244px;color:#1a0d00;-webkit-text-stroke:34px #1a0d00;transform:skewX(-5deg);filter:drop-shadow(0 18px 0 #000)}}
#l1{{top:128px;font-size:244px;background:linear-gradient(180deg,#FFF6B0 0%,#FFD43B 38%,#F59F00 72%,#C26A00 100%);-webkit-background-clip:text;background-clip:text;color:transparent;transform:skewX(-5deg);filter:drop-shadow(0 6px 0 #8a4b00)}}
#l2b{{top:430px;font-size:400px;color:#000;-webkit-text-stroke:46px #000;transform:skewX(-5deg);filter:drop-shadow(0 20px 0 #000)}}
#l2{{top:430px;font-size:400px;color:#fff;transform:skewX(-5deg)}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080">
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="0" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">
<defs><filter id="blur"><feGaussianBlur stdDeviation="3"/></filter><filter id="glow"><feGaussianBlur stdDeviation="14" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035 0.2" numOctaves="3" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="34"/></filter></defs>
<g opacity="{.85 if VAR != "A" else .7}" filter="url(#blur)">{''.join(candles)}</g>
<path d="{fx}" fill="none" stroke="#FF3B4E" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" opacity=".9"/>
<polygon points="{pts[-1][0]-60:.0f},{pts[-1][1]+10:.0f} {pts[-1][0]+30:.0f},{pts[-1][1]-70:.0f} {pts[-1][0]+36:.0f},{pts[-1][1]+50:.0f}" fill="#FF3B4E" filter="url(#glow)"/>
</svg>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="1" style="inset:0;background:radial-gradient(1500px 900px at 50% 50%,rgba(0,0,0,0) 40%,rgba(0,0,0,.65) 100%)"></div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="2" style="right:-10px;bottom:-20px;width:{540 if VAR == "A" else 620}px;height:{670 if VAR == "A" else 770}px;{"display:none;" if VAR == "B" else ""}"><img src="assets/mascot/{"충격" if VAR != "C" else "걱정"}.png" style="width:100%;height:100%;filter:drop-shadow(0 20px 40px rgba(0,0,0,.7))"></div>
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="3" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><path d="M70,862 C380,822 800,890 1150,846 C1250,834 1280,872 1200,890 C860,948 420,914 110,938 C40,938 40,884 70,862 Z" fill="#E11D2E" filter="url(#rough)"/></svg>
<div class="t clip" id="l1b" data-start="0" data-duration="2" data-track-index="4">진짜 경제위기는</div><div class="t clip" id="l1" data-start="0" data-duration="2" data-track-index="5">진짜 경제위기는</div>
<div class="t clip" id="l2b" data-start="0" data-duration="2" data-track-index="6" style="left:96px">이때 온다</div><div class="t clip" id="l2" data-start="0" data-duration="2" data-track-index="7" style="left:96px">이때 온다</div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="8" style="right:48px;top:36px;padding:14px 34px;border-radius:40px;background:rgba(5,7,15,.82);border:4px solid #F6C945;font-family:PB;font-size:46px;color:#F6C945">월급쟁이 재테크 스킬</div>
</div>
<script>const tl=gsap.timeline({{paused:true}});window.__timelines["main"]=tl;tl.seek(0);</script></body></html>"""
open(f"{ROOT}/index.html", "w", encoding="utf-8").write(html)
out = "/tmp/claude-0/hft/thumb"
shutil.rmtree(out, ignore_errors=True)
subprocess.run(["npx", "-y", "hyperframes", "snapshot", "--at", "1.0", "-o", out, "--no-end"], cwd=ROOT, check=True, capture_output=True)
src = [f for f in os.listdir(out) if f.startswith("frame-00")][0]
dst = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/hft/thumb_final.png"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/{src}", "-vf", "scale=1280:720:flags=lanczos", dst], check=True)
print(dst)
