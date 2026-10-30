"""썸네일: 참고 이미지의 글체(금빛 3D 1줄 + 흰 글자 검정 외곽 2줄 + 빨간 붓터치)에 영상 흐름(주가 폭락 × 환율 엇갈림)에 맞는 배경"""
import os, random, subprocess, sys, shutil
VAR = os.environ.get("VAR", "A")
ROOT = "/home/user/hf/thumb"
random.seed(26)
rows = []
vals = [("+12%", True), ("−31%", False), ("+8%", True), ("−24%", False), ("+15%", True), ("−40%", False)]
for i, (v, g) in enumerate(vals):
    y = 150 + i * 150
    col = "#E8503A" if g else "#3F7FC1"
    rows.append(f'<rect x="{80 if g else 980}" y="{y}" width="860" height="112" rx="20" fill="{col}" opacity=".55"/>'
                f'<text x="{880 if g else 1880}" y="{y + 82}" text-anchor="end" font-family="PB" font-size="86" fill="#fff" opacity=".7">{v}</text>')
candles = rows
fx = "M0,0"
pts = [(0, 0), (0, 0)]
html = f"""<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:BH;src:url("assets/fonts/BlackHanSans-Regular.ttf")}}
@font-face{{font-family:PB;src:url("assets/fonts/Pretendard-Black.otf")}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:1920px;height:1080px;overflow:hidden;background:#05070f}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{("linear-gradient(90deg,#0e2a4d 0%,#101624 48%,#4a1210 100%)" if VAR != "C" else "linear-gradient(90deg,#4a1210 0%,#101624 52%,#0e2a4d 100%)") if VAR != "B" else "radial-gradient(1500px 1000px at 80% 10%,#7a1020 0%,#2a0810 45%,#05060d 85%)"}}}
.abs{{position:absolute}}
.t{{position:absolute;left:84px;font-family:BH;white-space:nowrap;line-height:1}}
#l1b{{top:128px;font-size:244px;color:#1a0d00;-webkit-text-stroke:34px #1a0d00;transform:skewX(-5deg);filter:drop-shadow(0 18px 0 #000)}}
#l1{{top:128px;font-size:244px;background:linear-gradient(180deg,#FFF6B0 0%,#FFD43B 38%,#F59F00 72%,#C26A00 100%);-webkit-background-clip:text;background-clip:text;color:transparent;transform:skewX(-5deg);filter:drop-shadow(0 6px 0 #8a4b00)}}
#l2b{{top:470px;font-size:268px;color:#000;-webkit-text-stroke:46px #000;transform:skewX(-5deg);filter:drop-shadow(0 20px 0 #000)}}
#l2{{top:470px;font-size:268px;color:#fff;transform:skewX(-5deg)}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080">
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="0" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">
<defs><filter id="blur"><feGaussianBlur stdDeviation="3"/></filter><filter id="glow"><feGaussianBlur stdDeviation="14" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035 0.2" numOctaves="3" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="34"/></filter></defs>
<g opacity="{.85 if VAR != "A" else .7}" filter="url(#blur)">{''.join(candles)}</g>


</svg>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="1" style="inset:0;background:radial-gradient(1500px 900px at 50% 50%,rgba(0,0,0,0) 40%,rgba(0,0,0,.65) 100%)"></div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="2" style="right:-10px;bottom:-20px;width:360px;height:450px;bottom:-30px;{"display:none;" if VAR == "A" else ""}"><img src="assets/mascot/{"충격" if VAR != "C" else "걱정"}.png" style="width:100%;height:100%;filter:drop-shadow(0 20px 40px rgba(0,0,0,.7))"></div>
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="3" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><path d="M70,862 C380,822 800,890 1150,846 C1250,834 1280,872 1200,890 C860,948 420,914 110,938 C40,938 40,884 70,862 Z" fill="#E11D2E" filter="url(#rough)"/></svg>
<div class="t clip" id="l1b" data-start="0" data-duration="2" data-track-index="4">당신이 계속</div><div class="t clip" id="l1" data-start="0" data-duration="2" data-track-index="5">당신이 계속</div>
<div class="t clip" id="l2b" data-start="0" data-duration="2" data-track-index="6" style="left:96px">가난해지는 이유</div><div class="t clip" id="l2" data-start="0" data-duration="2" data-track-index="7" style="left:96px">가난해지는 이유</div>
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
