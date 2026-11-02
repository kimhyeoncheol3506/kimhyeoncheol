"""썸네일: 참고 이미지의 글체(금빛 3D 1줄 + 흰 글자 검정 외곽 2줄 + 빨간 붓터치)에 영상 흐름(주가 폭락 × 환율 엇갈림)에 맞는 배경"""
import os, random, subprocess, sys, shutil
VAR = os.environ.get("VAR", "A")
ROOT = "/home/user/hf/thumb"
random.seed(26)
def card(x, title, col, pts, arrow):
    path = "M" + " L".join(f"{x + 70 + i * 120},{p}" for i, p in enumerate(pts))
    ex, ey = x + 70 + (len(pts) - 1) * 120, pts[-1]
    return (f'<rect x="{x}" y="40" width="880" height="420" rx="30" fill="#ffffff" fill-opacity=".08" stroke="{col}" stroke-width="8"/>'
            f'<text x="{x + 40}" y="130" font-family="BH" font-size="96" fill="{col}">{title}</text>'
            f'<path d="{path}" fill="none" stroke="{col}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>'
            f'<polygon points="{ex - 30},{ey + (30 if arrow == "up" else -30)} {ex + 40},{ey} {ex - 10},{ey + (-40 if arrow == "up" else 40)}" fill="{col}"/>')
candles = [card(60, "성장률 ↑", "#FF4D5E", [400, 380, 330, 300, 230, 170, 140], "up"), card(980, "내 통장 ↓", "#4D9BFF", [170, 200, 240, 300, 330, 380, 410], "down")]
fx = "M0,0"
pts = [(0, 0), (0, 0)]
html = f"""<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:BH;src:url("assets/fonts/BlackHanSans-Regular.ttf")}}
@font-face{{font-family:PB;src:url("assets/fonts/Pretendard-Black.otf")}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:1920px;height:1080px;overflow:hidden;background:#05070f}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{"radial-gradient(1300px 900px at 18% 95%,#6b0f1f 0%,#2a0b18 38%,#070b18 78%)" if VAR != "B" else "radial-gradient(1500px 1000px at 80% 10%,#7a1020 0%,#2a0810 45%,#05060d 85%)"}}}
.abs{{position:absolute}}
.t{{position:absolute;left:84px;font-family:BH;white-space:nowrap;line-height:1}}
#l1b{{top:500px;font-size:190px;color:#1a0d00;-webkit-text-stroke:34px #1a0d00;transform:skewX(-5deg);filter:drop-shadow(0 18px 0 #000)}}
#l1{{top:500px;font-size:190px;background:linear-gradient(180deg,#FFF6B0 0%,#FFD43B 38%,#F59F00 72%,#C26A00 100%);-webkit-background-clip:text;background-clip:text;color:transparent;transform:skewX(-5deg);filter:drop-shadow(0 6px 0 #8a4b00)}}
#l2b{{top:700px;font-size:300px;color:#000;-webkit-text-stroke:46px #000;transform:skewX(-5deg);filter:drop-shadow(0 20px 0 #000)}}
#l2{{top:700px;font-size:300px;color:#fff;transform:skewX(-5deg)}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080">
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="0" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">
<defs><filter id="blur"><feGaussianBlur stdDeviation="3"/></filter><filter id="glow"><feGaussianBlur stdDeviation="14" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035 0.2" numOctaves="3" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="34"/></filter></defs>
<g>{''.join(candles)}</g>
<path d="{fx}" fill="none" opacity="0" stroke="#FF3B4E" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" opacity=".9"/>
<polygon points="{pts[-1][0]-60:.0f},{pts[-1][1]+10:.0f} {pts[-1][0]+30:.0f},{pts[-1][1]-70:.0f} {pts[-1][0]+36:.0f},{pts[-1][1]+50:.0f}" fill="#FF3B4E" opacity="0"/>
</svg>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="1" style="inset:0;background:radial-gradient(1500px 900px at 50% 50%,rgba(0,0,0,0) 40%,rgba(0,0,0,.25) 100%)"></div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="2" style="right:-10px;bottom:-20px;width:440px;height:550px;{"display:none;" if VAR == "B" else ""}"><img src="assets/mascot/{"충격" if VAR != "C" else "걱정"}.png" style="width:100%;height:100%;filter:drop-shadow(0 20px 40px rgba(0,0,0,.7))"></div>
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="3" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><path d="M70,1010 C380,975 800,1035 1150,995 C1250,985 1280,1020 1200,1035 C860,1075 420,1060 110,1075 C40,1075 40,1030 70,1010 Z" fill="#E11D2E" filter="url(#rough)"/></svg>
<div class="t clip" id="l1b" data-start="0" data-duration="2" data-track-index="4">축하합니다,</div><div class="t clip" id="l1" data-start="0" data-duration="2" data-track-index="5">축하합니다,</div>
<div class="t clip" id="l2b" data-start="0" data-duration="2" data-track-index="6" style="left:96px">당신 빼고</div><div class="t clip" id="l2" data-start="0" data-duration="2" data-track-index="7" style="left:96px">당신 빼고</div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="8" style="right:48px;top:480px;padding:14px 34px;border-radius:40px;background:rgba(5,7,15,.82);border:4px solid #F6C945;font-family:PB;font-size:46px;color:#F6C945">월급쟁이 재테크 스킬</div>
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
