"""32편 썸네일 A~D: 글체 고정(금빛 3D 윗줄 + 흰 글씨 검정 외곽 아랫줄 + 빨간 붓터치, Black Han Sans).
배경은 30편(와인)·31편(칠판·뉴스·사전·단어장)과 다르게: A 미국·한국 양분 전광판 · B 보랏빛 의사당 + 거부권 도장 · C 청록 서버실 · D 주황 새벽 세 갈래 길.
사용: VAR=A python3 make_thumb.py out.png"""
import os, subprocess, sys, shutil
VAR = os.environ.get("VAR", "A")
ROOT = "/home/user/hf/thumb"
TXT = {"A": ("같은 선거, 정반대", "코스피 −5%?"), "B": ("민주당 압승인데", "거부권 변수"),
       "C": ("데이터센터 규제?", "반도체 어디로"), "D": ("2027년 내 계좌", "시나리오 3")}[VAR]
MASCOT = {"A": "충격", "B": "걱정", "C": "놀람", "D": "걱정"}[VAR]


def split_board():
    up = "".join(f'<rect x="{110 + i * 70}" y="{430 - h}" width="40" height="{h}" fill="#FF4D5E"/>' for i, h in enumerate([90, 120, 110, 160, 150, 210, 260, 330]))
    dn = "".join(f'<rect x="{1060 + i * 70}" y="{110 + (330 - h)}" width="40" height="{h}" fill="#4D9BFF"/>' for i, h in enumerate([330, 300, 310, 250, 230, 170, 120, 70]))
    return (f'<rect width="960" height="1080" fill="#0d1f4a"/><rect x="960" width="960" height="1080" fill="#3a0c16"/><rect x="954" width="12" height="1080" fill="#000"/>'
            f'<text x="110" y="100" font-family="BH" font-size="70" fill="#fff">미국 다우</text><text x="560" y="110" font-family="BH" font-size="110" fill="#FF4D5E">+3%</text>{up}'
            f'<path d="M700,420 L860,170" stroke="#FF4D5E" stroke-width="26" stroke-linecap="round"/><polygon points="830,140 900,120 885,195" fill="#FF4D5E"/>'
            f'<text x="1060" y="100" font-family="BH" font-size="70" fill="#fff">코스피</text><text x="1390" y="110" font-family="BH" font-size="110" fill="#4D9BFF">−5.28%</text>{dn}')


def capitol():
    cols = "".join(f'<rect x="{560 + i * 90}" y="250" width="38" height="230" fill="#e9e3f5"/>' for i, _ in enumerate(range(9)))
    return (f'<circle cx="960" cy="140" r="110" fill="#e9e3f5"/><rect x="900" y="40" width="120" height="40" fill="#e9e3f5"/><rect x="520" y="230" width="880" height="30" fill="#e9e3f5"/>{cols}'
            f'<rect x="480" y="480" width="960" height="40" fill="#e9e3f5"/>'
            f'<g transform="translate(1340,300) rotate(-14)"><rect x="-260" y="-95" width="520" height="190" rx="22" fill="rgba(0,0,0,.25)" stroke="#E11D2E" stroke-width="18"/><text y="45" text-anchor="middle" font-family="BH" font-size="130" fill="#E11D2E">거부권</text></g>')


def servers():
    racks = "".join(f'<rect x="{120 + i * 300}" y="60" width="220" height="440" rx="10" fill="#0b2a33" stroke="#1f6f7f" stroke-width="6"/>' +
                    "".join(f'<rect x="{140 + i * 300}" y="{80 + k * 50}" width="180" height="30" rx="4" fill="#123d48"/><circle cx="{300 + i * 300}" cy="{95 + k * 50}" r="7" fill="{"#3cf0c8" if (i + k) % 3 else "#ff5a5a"}"/>' for k in range(8))
                    for i in range(6))
    return racks + '<g stroke="#E11D2E" stroke-width="40" stroke-linecap="round"><path d="M640,90 L1280,470"/><path d="M1280,90 L640,470"/></g>'


def roads():
    return ('<circle cx="960" cy="520" r="260" fill="#FFD27A" opacity=".85"/><rect y="460" width="1920" height="620" fill="#7a3a12"/>'
            '<path d="M960,1080 L900,470 L1020,470 Z" fill="#f2c14e"/><path d="M960,1080 L300,470 L420,470 Z" fill="#5B93B8"/><path d="M960,1080 L1500,470 L1620,470 Z" fill="#DE5B41"/>'
            '<text x="300" y="440" font-family="BH" font-size="90" fill="#fff">B</text><text x="930" y="440" font-family="BH" font-size="90" fill="#fff">A</text><text x="1530" y="440" font-family="BH" font-size="90" fill="#fff">C</text>')


BG = {"A": ("#0d1f4a", split_board()),
      "B": ("radial-gradient(1400px 900px at 50% 20%,#5b3a8f 0%,#2a1747 55%,#120a22 100%)", capitol()),
      "C": ("linear-gradient(180deg,#062a30 0%,#041a1f 100%)", servers()),
      "D": ("linear-gradient(180deg,#ff9a3c 0%,#d9531e 45%,#5a2208 100%)", roads())}[VAR]
html = f"""<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:BH;src:url("assets/fonts/BlackHanSans-Regular.ttf")}}
@font-face{{font-family:PB;src:url("assets/fonts/Pretendard-Black.otf")}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:1920px;height:1080px;overflow:hidden;background:#05070f}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{BG[0]}}}
.abs{{position:absolute}}
.t{{position:absolute;left:84px;font-family:BH;white-space:nowrap;line-height:1}}
#l1b{{top:540px;font-size:170px;color:#1a0d00;-webkit-text-stroke:34px #1a0d00;transform:skewX(-5deg);filter:drop-shadow(0 18px 0 #000)}}
#l1{{top:540px;font-size:170px;background:linear-gradient(180deg,#FFF6B0 0%,#FFD43B 38%,#F59F00 72%,#C26A00 100%);-webkit-background-clip:text;background-clip:text;color:transparent;transform:skewX(-5deg);filter:drop-shadow(0 6px 0 #8a4b00)}}
#l2b{{top:730px;font-size:250px;color:#000;-webkit-text-stroke:46px #000;transform:skewX(-5deg);filter:drop-shadow(0 20px 0 #000)}}
#l2{{top:730px;font-size:250px;color:#fff;transform:skewX(-5deg)}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080">
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="0" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">
<defs><filter id="chalkf"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="5"/></filter>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035 0.2" numOctaves="3" seed="4" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="34"/></filter></defs>
{BG[1]}
</svg>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="1" style="inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.55) 100%)"></div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="2" style="right:-10px;bottom:-20px;width:440px;height:550px"><img src="assets/mascot/{MASCOT}.png" style="width:100%;height:100%;filter:drop-shadow(0 20px 40px rgba(0,0,0,.7))"></div>
<svg class="abs clip" data-start="0" data-duration="2" data-track-index="3" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><path d="M70,1020 C380,985 800,1045 1150,1005 C1250,995 1280,1030 1200,1045 C860,1080 420,1070 110,1080 C40,1080 40,1040 70,1020 Z" fill="#E11D2E" filter="url(#rough)"/></svg>
<div class="t clip" id="l1b" data-start="0" data-duration="2" data-track-index="4">{TXT[0]}</div><div class="t clip" id="l1" data-start="0" data-duration="2" data-track-index="5">{TXT[0]}</div>
<div class="t clip" id="l2b" data-start="0" data-duration="2" data-track-index="6" style="left:96px">{TXT[1]}</div><div class="t clip" id="l2" data-start="0" data-duration="2" data-track-index="7" style="left:96px">{TXT[1]}</div>
<div class="abs clip" data-start="0" data-duration="2" data-track-index="8" style="right:48px;top:{530 if VAR != "B" else 520}px;padding:14px 34px;border-radius:40px;background:rgba(5,7,15,.82);border:4px solid #F6C945;font-family:PB;font-size:46px;color:#F6C945">월급쟁이 재테크 스킬</div>
</div>
<script>const tl=gsap.timeline({{paused:true}});window.__timelines["main"]=tl;tl.seek(0);</script></body></html>"""
open(f"{ROOT}/index.html", "w", encoding="utf-8").write(html)
out = f"/tmp/claude-0/hft/thumb{VAR}"
shutil.rmtree(out, ignore_errors=True)
subprocess.run(["npx", "-y", "hyperframes", "snapshot", "--at", "1.0", "-o", out, "--no-end"], cwd=ROOT, check=True, capture_output=True)
src = [f for f in os.listdir(out) if f.startswith("frame-00")][0]
dst = sys.argv[1] if len(sys.argv) > 1 else f"/tmp/claude-0/hft/thumb_{VAR}.png"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/{src}", "-vf", "scale=1280:720:flags=lanczos", dst], check=True)
print(dst)
