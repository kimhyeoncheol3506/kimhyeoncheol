"""31편 썸네일 A~D: 글체 고정(금빛 3D 윗줄 + 흰 글씨 검정 외곽 아랫줄 + 빨간 붓터치, Black Han Sans).
배경은 직전 회차(30편 짙은 와인색 레이더)와 다르게: A 칠판(초록) · B 뉴스 화면(청록) · C 펼친 사전(나무 책상) · D 노란 단어장.
사용: VAR=A python3 make_thumb.py out.png"""
import os, subprocess, sys, shutil
VAR = os.environ.get("VAR", "A")
ROOT = "/home/user/hf/thumb"
TXT = {"A": ("뉴스가 다 들리는", "주식용어 40"), "B": ("이 뉴스, 읽히세요?", "주식용어 40"),
       "C": ("중학생도 이해하는", "주식용어 40"), "D": ("PER? 공매도?", "이거 하나로 끝")}[VAR]
WORDS = ["PER", "공매도", "음봉", "시가총액", "PBR", "상한가", "예수금", "골든크로스", "배당", "서킷브레이커", "호가", "ROE"]
MASCOT = {"A": "놀람", "B": "걱정", "C": "놀람", "D": "충격"}[VAR]


def chalk():
    pos = [(90, 120, -6), (430, 90, 4), (840, 130, -3), (1180, 95, 5), (1500, 140, -4), (120, 300, 3), (520, 280, -5), (980, 310, 2), (1330, 290, -2)]
    cols = ["#ffffff", "#FFE27A", "#ffffff", "#9fe3ff", "#ffffff", "#FFB3B3", "#ffffff", "#FFE27A", "#9fe3ff"]
    return "".join(f'<text x="{x}" y="{y + 80}" transform="rotate({r} {x} {y})" font-family="BH" font-size="{96 if len(w) < 4 else 78}" fill="{c}" opacity=".82" filter="url(#chalkf)">{w}</text>'
                   for (x, y, r), w, c in zip(pos, WORDS, cols))


def news():
    bars = "".join(f'<rect x="{180 + i * 110}" y="{420 - h}" width="60" height="{h}" fill="{"#FF4D5E" if i % 3 else "#4D9BFF"}"/><line x1="{210 + i * 110}" y1="{400 - h}" x2="{210 + i * 110}" y2="{440}" stroke="{"#FF4D5E" if i % 3 else "#4D9BFF"}" stroke-width="6"/>'
                   for i, h in enumerate([120, 180, 90, 220, 160, 260, 140, 300, 200, 330, 250, 280, 190, 310, 260]))
    return (f'<rect x="60" y="40" width="1800" height="460" rx="24" fill="#0d3b45" stroke="#11202a" stroke-width="16"/>{bars}'
            f'<rect x="60" y="420" width="1800" height="80" fill="#E11D2E"/><text x="110" y="480" font-family="BH" font-size="56" fill="#fff">속보 · 외국인 순매도 · PER 부담 · 반도체 줄줄이 음봉 · 사이드카</text>')


def book():
    lines = "".join(f'<text x="{x}" y="{y}" font-family="BH" font-size="62" fill="#3a2a1a">{w}</text><rect x="{x}" y="{y + 18}" width="{300 + (i * 53) % 160}" height="10" rx="5" fill="#b9a58a"/><rect x="{x}" y="{y + 40}" width="{220 + (i * 37) % 160}" height="10" rx="5" fill="#cdbca2"/>'
                    for i, (x, y, w) in enumerate([(200, 150, "PER"), (200, 290, "공매도"), (200, 430, "시가총액"), (1040, 150, "음봉"), (1040, 290, "배당"), (1040, 430, "호가")]))
    return (f'<rect width="1920" height="1080" fill="#7a4a24"/><g opacity=".25">{"".join(f"<rect y={chr(34)}{k * 90}{chr(34)} width={chr(34)}1920{chr(34)} height={chr(34)}6{chr(34)} fill={chr(34)}#3d220d{chr(34)}/>" for k in range(12))}</g>'
            f'<path d="M140,60 Q520,20 940,70 L940,560 Q520,520 140,560 Z" fill="#fbf4e4"/><path d="M980,70 Q1400,20 1780,60 L1780,560 Q1400,520 980,560 Z" fill="#f6eedb"/>'
            f'<rect x="940" y="60" width="40" height="510" fill="#d9c9a8"/>{lines}')


def notebook():
    rows = "".join(f'<line x1="0" y1="{120 + k * 70}" x2="1920" y2="{120 + k * 70}" stroke="#d9b54a" stroke-width="3"/>' for k in range(14))
    tags = "".join(f'<g transform="rotate({r} {x} {y})"><rect x="{x}" y="{y}" width="{len(w) * 62 + 70}" height="110" rx="18" fill="{c}" stroke="#222" stroke-width="6"/><text x="{x + 35}" y="{y + 82}" font-family="BH" font-size="76" fill="#222">{w}</text></g>'
                   for (x, y, r, c), w in zip([(110, 70, -5, "#fff"), (560, 120, 4, "#9fe3ff"), (990, 60, -3, "#FFB3B3"), (1380, 130, 6, "#fff"), (220, 270, 3, "#C8F7C5"), (760, 300, -4, "#fff"), (1240, 290, 2, "#FFE27A")], WORDS))
    return f'<rect width="1920" height="1080" fill="#FFD84D"/>{rows}<line x1="140" y1="0" x2="140" y2="1080" stroke="#E11D2E" stroke-width="5"/>{tags}'


BG = {"A": ("radial-gradient(1400px 900px at 30% 30%,#2f6b4f 0%,#1d4634 55%,#0f2a1f 100%)", chalk()),
      "B": ("linear-gradient(180deg,#0b5560 0%,#063038 60%,#031a1f 100%)", news()),
      "C": ("#7a4a24", book()), "D": ("#FFD84D", notebook())}[VAR]
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
#l2b{{top:730px;font-size:{280 if VAR != "D" else 230}px;color:#000;-webkit-text-stroke:46px #000;transform:skewX(-5deg);filter:drop-shadow(0 20px 0 #000)}}
#l2{{top:730px;font-size:{280 if VAR != "D" else 230}px;color:#fff;transform:skewX(-5deg)}}
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
