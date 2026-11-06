"""유튜브 썸네일(thumbnail.jpg) — 최종 영상·youtube.txt 와 한 세트(현철님 2026-11-04, PUB-02).

모양(현철님이 준 본보기 두 장): 위 2/3 는 3D 일러스트 그림, 아래에 아주 굵은 두 줄 제목.
  첫 줄 흰색, 둘째 줄은 강조 낱말만 주황/민트. 굵은 검은 테두리 + 그림자로 작은 화면에서도 읽힌다.
그림(bg)은 AI 로 '글자 없이' 만들고(글자는 AI 가 틀리게 그리므로) 글자는 여기서 폰트로 얹는다.
대본 yaml:
  thumbnail:
    bg: assets/thumbs/aside_bg.png      # 없으면 네온 기본 배경
    tag: "AI 브라우저 · 사용법 총정리"     # 왼쪽 위 작은 띠(선택)
    line1: "엑셀 옮겨 적기 그만!"
    mid: "작은 가운데 줄"                 # 선택: line1 과 line2 사이 설명 줄(작게, 노란빛)
    line2: "[[어사이드]]가 다 해 줘요"     # [[ ]] = 강조색
    size1 / size_mid / size2: 글자 크기(px). 안 주면 줄 수에 맞춰 자동, 넓으면 화면 폭에 맞게 줄인다
    accent: "#FF8A3D"                    # 선택(기본 주황)
    align: left | center                 # 기본 left
크기: 1920x1080(유튜브 권장 1280x720 보다 크게), JPEG 2MB 이하(유튜브 상한).
"""
import html as _h
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1920, 1080
MAX_BYTES = 2 * 1024 * 1024


def _mk(s, accent):
    s = _h.escape(s)
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{accent}">\1</span>', s)


def page(t, bg_url):
    accent = t.get("accent", "#FF8A3D")
    align = t.get("align", "left")
    fonts = (ROOT / "assets" / "fonts").as_uri()
    bg = (f"background:#05070c url('{bg_url}') center/cover no-repeat;" if bg_url else
          "background:radial-gradient(ellipse at 70% 35%,#0f3b3a 0%,#07121a 45%,#03050a 100%);")
    tag = f'<div class="tag">{_h.escape(t["tag"])}</div>' if t.get("tag") else ""
    has_mid = bool(t.get("mid"))
    s1, s2 = t.get("size1", t.get("size", 132 if has_mid else 168)), t.get("size2", t.get("size", 150 if has_mid else 168))
    sm = t.get("size_mid", 70)
    mid = f'<div id="lm">{_mk(t["mid"], accent)}</div>' if has_mid else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts}/Pretendard-Black.otf')}}
@font-face{{font-family:K;font-weight:800;src:url('{fonts}/Pretendard-ExtraBold.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif}}
#bg{{position:absolute;inset:0;{bg}}}
#fade{{position:absolute;left:0;right:0;bottom:0;height:62%;background:linear-gradient(to top,rgba(0,0,0,.92) 0%,rgba(0,0,0,.72) 38%,rgba(0,0,0,0) 100%)}}
#txt{{position:absolute;left:96px;right:96px;bottom:70px;text-align:{align}}}
.l{{font-weight:900;line-height:1.08;letter-spacing:-4px;color:#fff;white-space:nowrap;
   -webkit-text-stroke:14px #000;paint-order:stroke fill;text-shadow:0 10px 0 #000,0 18px 40px rgba(0,0,0,.85)}}
#l1{{font-size:{s1}px}} #l2{{font-size:{s2}px}}
#lm{{font-weight:800;font-size:{sm}px;line-height:1.25;letter-spacing:-2px;color:#FFE27A;white-space:nowrap;margin:6px 0 10px;
   -webkit-text-stroke:10px #000;paint-order:stroke fill;text-shadow:0 6px 0 #000,0 12px 30px rgba(0,0,0,.85)}}
.tag{{position:absolute;left:96px;top:70px;padding:14px 30px;border-radius:14px;background:{accent};color:#111;font-weight:800;font-size:54px;letter-spacing:-1px;
     box-shadow:0 8px 30px rgba(0,0,0,.5)}}
</style></head><body><div id="bg"></div><div id="fade"></div>{tag}
<div id="txt"><div class="l" id="l1">{_mk(t.get('line1', ''), accent)}</div>{mid}<div class="l" id="l2">{_mk(t.get('line2', ''), accent)}</div></div>
<script>for(const id of ['l1','lm','l2']){{const e=document.getElementById(id);if(!e)continue;let f=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>{W - 192}&&f>80){{f-=4;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""


# ── layout: tiles (2026-11-04, 현철님 본보기 'Git과 GitHub' 썸네일 분위기) ──────────────────────────────
# 어두운 바탕 · 위쪽 가운데 제목(둘째 줄의 [[강조]]는 밝은 형광 상자) · 아래쪽에 반짝이는 검은 앱 타일 줄(가운데가 가장 큼)
# · 타일 뒤에서 빼꼼 내다보는 원본 마스코트. 실제 로고 대신 직접 그린 아이콘(SVG).
ICONS = {
    "branch": '<circle cx="30" cy="22" r="9"/><circle cx="30" cy="78" r="9"/><circle cx="70" cy="40" r="9"/><path d="M30 31v38M70 49c0 18-40 10-40 20" fill="none" stroke-width="7"/>',
    "commit": '<path d="M8 50h84" stroke-width="7"/><circle cx="50" cy="50" r="15"/>',
    "cloud": '<path d="M30 72h44a18 18 0 0 0 0-36 26 26 0 0 0-50 6 15 15 0 0 0 6 30z"/><path d="M52 66V44M42 54l10-10 10 10" fill="none" stroke="#111" stroke-width="6"/>',
    "save": '<path d="M20 18h48l14 14v50H20z"/><rect x="32" y="18" width="30" height="20" fill="#111"/><rect x="30" y="54" width="42" height="22" rx="3" fill="#111"/>',
    "folder": '<path d="M12 28h28l8 9h40v43H12z"/>',
    "merge": '<circle cx="28" cy="22" r="9"/><circle cx="72" cy="22" r="9"/><circle cx="50" cy="80" r="9"/><path d="M28 31c0 25 22 25 22 40M72 31c0 25-22 25-22 40" fill="none" stroke-width="7"/>',
    "cursor": '<path d="M24 10v66l17-15 12 27 11-5-12-26 23-1z" stroke="#111" stroke-width="3" stroke-linejoin="round"/>',
    "browser": '<rect x="10" y="18" width="80" height="64" rx="8"/><rect x="10" y="18" width="80" height="16" rx="8" fill="#111" opacity=".35"/><rect x="62" y="38" width="22" height="38" rx="3" fill="#111" opacity=".45"/>',
    "form": '<rect x="18" y="12" width="64" height="76" rx="6"/><rect x="28" y="28" width="44" height="9" rx="3" fill="#111"/><rect x="28" y="46" width="44" height="9" rx="3" fill="#111"/><rect x="28" y="64" width="26" height="11" rx="3" fill="#111"/>',
    "shield": '<path d="M50 10l34 12v24c0 22-15 36-34 44C31 82 16 68 16 46V22z"/><path d="M36 50l10 10 18-20" fill="none" stroke="#111" stroke-width="7"/>',
    "chat": '<path d="M14 20h72v46H44L26 82V66H14z"/><circle cx="34" cy="43" r="5" fill="#111"/><circle cx="50" cy="43" r="5" fill="#111"/><circle cx="66" cy="43" r="5" fill="#111"/>',
    "people": '<circle cx="36" cy="34" r="12"/><circle cx="66" cy="38" r="10"/><path d="M14 82c2-22 42-22 44 0zM52 82c2-18 34-18 36 0z"/>',
}


def page_tiles(t, accent):
    import json as _j
    fonts = (ROOT / "assets" / "fonts").as_uri()
    tiles = t.get("tiles") or ["folder", "commit", "branch", "cloud", "merge", "save", "people"]
    colors = t.get("tile_colors") or ["#2B2F36", "#3A3F47", "#F05033", "#FFFFFF", "#FF8A3D", "#3A3F47", "#2B2F36"]
    n = len(tiles); mid = (n - 1) / 2
    cells = []
    for i, (ic, col) in enumerate(zip(tiles, colors)):
        d = abs(i - mid); sz = int(300 - d * 44); y = int(d * 30); z = 10 - int(d)
        cells.append(f'<div class="tile" style="width:{sz}px;height:{sz}px;margin-top:{y}px;z-index:{z}">'
                     f'<svg viewBox="0 0 100 100" width="{int(sz*.5)}" height="{int(sz*.5)}" fill="{col}" stroke="{col}">{ICONS.get(ic, ICONS["commit"])}</svg></div>')
    l2 = _mk(t.get("line2", ""), accent).replace(f'<span style="color:{accent}">', '<span class="box">')
    mid_line = f'<span id="lm">{_mk(t["mid"], accent)}</span>' if t.get("mid") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts}/Pretendard-Black.otf')}}
@font-face{{font-family:K;font-weight:800;src:url('{fonts}/Pretendard-ExtraBold.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:radial-gradient(ellipse at 50% 70%,#1d2128 0%,#0b0d11 55%,#050608 100%)}}
#top{{position:absolute;left:0;right:0;top:56px;text-align:center}}
.l{{display:inline-block;font-weight:900;color:#fff;white-space:nowrap;letter-spacing:-4px;line-height:1.12;text-shadow:0 10px 30px rgba(0,0,0,.7)}}
#top>div{{display:block}} #top>div>span.w{{display:inline-block}}
#l1{{font-size:{t.get('size1', 132)}px;color:{t.get('color1', '#fff')}}} #l2{{font-size:{t.get('size2', 150)}px;margin-top:14px}}
.box{{display:inline-block;background:{accent};color:#111;padding:0 26px 6px;border-radius:10px;margin-right:18px;box-shadow:0 0 50px {accent}55}}
#lm{{display:inline-block;font-weight:800;font-size:{t.get('size_mid', 64)}px;color:#FFE27A;letter-spacing:-2px;margin-top:18px;white-space:nowrap}}
#row{{position:absolute;left:0;right:0;bottom:40px;display:flex;justify-content:center;align-items:flex-start}}
.tile{{position:relative;margin-left:-22px;border-radius:22%;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(160deg,#2a2d33 0%,#111317 55%,#07080a 100%);border:2px solid rgba(255,255,255,.08);
  box-shadow:0 30px 60px rgba(0,0,0,.75),inset 0 2px 0 rgba(255,255,255,.14),inset 0 -8px 20px rgba(0,0,0,.6)}}
.tile:first-child{{margin-left:0}}
.tile svg{{filter:drop-shadow(0 4px 10px rgba(0,0,0,.6))}}
#pal{{position:absolute;left:50%;bottom:{40+280}px;transform:translateX(-50%);width:250px;height:160px;border-radius:30px 30px 10px 10px;
  background:{t.get('pal_bg', 'linear-gradient(170deg,#7ff0d4,#2fb894)')};box-shadow:inset 0 6px 0 rgba(255,255,255,.35),0 0 60px {t.get('pal_glow', 'rgba(63,224,181,.35)')}}}
#pal i{{position:absolute;top:58px;width:26px;height:34px;background:#0b0d11;border-radius:12px}}
#pal i:first-child{{left:62px}} #pal i:last-child{{right:62px}}
#pal b{{position:absolute;top:96px;left:50%;transform:translateX(-50%);width:34px;height:14px;border-bottom:6px solid #0b0d11;border-radius:0 0 20px 20px}}
{_cyber_css(t, accent) if t.get('bg_style') == 'cyber' else ''}{_bot2_css(t) if t.get('bot') == 'v2' else ''}
</style></head><body>
{_cyber_html(t) if t.get('bg_style') == 'cyber' else ''}
<div id="top"><div><span class="l" id="l1">{_mk(t.get('line1', ''), accent)}</span></div><div><span class="l" id="l2">{l2}</span></div><div>{mid_line}</div></div>
{(_BOT2_HTML if t.get('bot') == 'v2' else '<div id="pal"><i></i><b></b><i></i></div>') if t.get('mascot', True) else ''}
<div id="row">{''.join(cells)}</div>
<script>for(const id of ['l1','l2','lm']){{const e=document.getElementById(id);if(!e)continue;let f=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>{W - 160}&&f>60){{f-=4;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""


# ── 사이버 배경(2026-11-05 현철님: "썸네일을 사이버틱하게") · 클로드봇 v2(바이저·안테나·귀·볼 불빛)
def _cyber_css(t, accent):
    c1 = t.get("cyber_c1", "#00E5FF"); c2 = t.get("cyber_c2", "#FF3DF2")
    return f"""
html,body{{background:radial-gradient(ellipse at 50% 40%,{t.get('cyber_bg1', '#1A1040')} 0%,{t.get('cyber_bg2', '#0A0A26')} 45%,#03030C 100%)!important}}
#cy{{position:absolute;inset:0;overflow:hidden}}
#cy .floor{{position:absolute;left:-30%;right:-30%;bottom:-8%;height:62%;transform:perspective(700px) rotateX(62deg);transform-origin:50% 100%;
  background-image:linear-gradient({c1}55 2px,transparent 2px),linear-gradient(90deg,{c1}55 2px,transparent 2px);background-size:90px 90px;
  -webkit-mask-image:linear-gradient(to top,#000 10%,transparent 85%);mask-image:linear-gradient(to top,#000 10%,transparent 85%)}}
#cy .hz{{position:absolute;left:0;right:0;top:48%;height:3px;background:linear-gradient(90deg,transparent,{c2},{c1},{c2},transparent);box-shadow:0 0 30px {c2},0 0 60px {c1};opacity:.75}}
#cy .glowL{{position:absolute;left:-10%;top:10%;width:55%;height:70%;background:radial-gradient(circle,{c2}33,transparent 60%)}}
#cy .glowR{{position:absolute;right:-10%;top:5%;width:55%;height:70%;background:radial-gradient(circle,{c1}33,transparent 60%)}}
#cy .scan{{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 5px)}}
#cy svg{{position:absolute;inset:0}}
"""

def _cyber_html(t):
    import random
    c1 = t.get("cyber_c1", "#00E5FF"); c2 = t.get("cyber_c2", "#FF3DF2")
    r = random.Random(11); paths = []
    for side in (0, 1):                                   # 양옆 회로선(가운데 글자는 피함)
        for k in range(7):
            y = 120 + k * 120 + r.randint(-20, 20); x0 = 0 if side == 0 else W
            dx = r.randint(140, 300); turn = r.randint(40, 90) * (1 if r.random() < .5 else -1)
            x1 = dx if side == 0 else W - dx; x2 = (x1 + 120) if side == 0 else (x1 - 120)
            col = c1 if k % 2 else c2
            paths.append(f'<path d="M{x0},{y} H{x1} L{x2},{y + turn} H{x2 + (60 if side == 0 else -60)}" stroke="{col}" stroke-width="3" fill="none" opacity=".55"/>'
                         f'<circle cx="{x2 + (60 if side == 0 else -60)}" cy="{y + turn}" r="7" fill="{col}" opacity=".9"/>')
    dots = "".join(f'<circle cx="{r.randint(0, W)}" cy="{r.randint(0, int(H * .5))}" r="{r.choice([1.5, 2, 2.5])}" fill="#fff" opacity="{r.uniform(.3, .8):.2f}"/>' for _ in range(70))
    return (f'<div id="cy"><div class="glowL"></div><div class="glowR"></div><div class="floor"></div><div class="hz"></div>'
            f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" style="filter:drop-shadow(0 0 8px {c1})">{"".join(paths)}{dots}</svg><div class="scan"></div></div>')

def _bot2_css(t):
    body = t.get("pal_bg", "linear-gradient(170deg,#C7BEFF,#7C6CF0)"); glow = t.get("pal_glow", "rgba(155,140,255,.45)")
    eye = t.get("bot_eye", "#00E5FF")
    return f"""
#bot{{position:absolute;left:50%;bottom:{40 + 280}px;transform:translateX(-50%);width:270px;height:170px}}
#bot .hd{{position:absolute;inset:0;border-radius:34px 34px 12px 12px;background:{body};
  box-shadow:inset 0 8px 0 rgba(255,255,255,.4),inset 0 -10px 18px rgba(0,0,0,.25),0 0 70px {glow},0 0 0 3px rgba(255,255,255,.18)}}
#bot .vs{{position:absolute;left:30px;right:30px;top:40px;height:70px;border-radius:26px;background:linear-gradient(180deg,#0B0E1E,#151A33);
  box-shadow:inset 0 0 0 3px rgba(255,255,255,.12),inset 0 6px 14px rgba(0,0,0,.6)}}
#bot .vs::after{{content:"";position:absolute;left:14px;top:8px;width:60px;height:10px;border-radius:6px;background:rgba(255,255,255,.18)}}
#bot .ey{{position:absolute;top:22px;width:34px;height:26px;border-radius:14px 14px 18px 18px;background:{eye};box-shadow:0 0 18px {eye},0 0 36px {eye}}}
#bot .ey.l{{left:40px}} #bot .ey.r{{right:40px}}
#bot .ch{{position:absolute;top:118px;width:26px;height:12px;border-radius:8px;background:#FF7AC8;opacity:.75;box-shadow:0 0 14px #FF7AC8}}
#bot .ch.l{{left:34px}} #bot .ch.r{{right:34px}}
#bot .ear{{position:absolute;top:52px;width:22px;height:58px;border-radius:10px;background:#2A2F45;box-shadow:inset 0 0 0 3px rgba(255,255,255,.15),0 0 16px {eye}}}
#bot .ear.l{{left:-18px}} #bot .ear.r{{right:-18px}}
#bot .an{{position:absolute;left:50%;top:-46px;width:6px;height:46px;margin-left:-3px;background:#D8D4FF;border-radius:3px}}
#bot .an::after{{content:"";position:absolute;left:50%;top:-14px;width:24px;height:24px;margin-left:-12px;border-radius:50%;background:{eye};box-shadow:0 0 20px {eye},0 0 40px {eye}}}
"""

_BOT2_HTML = '<div id="bot"><div class="an"></div><div class="ear l"></div><div class="ear r"></div><div class="hd"></div><div class="vs"><div class="ey l"></div><div class="ey r"></div></div><div class="ch l"></div><div class="ch r"></div></div>'


# ── layout: versus (2026-11-05 현철님: "완전 다른버전으로") — 좌우 반반 대결 화면 + 마주 보는 로봇 둘 + 번개 VS + 물음표 트로피
def _robot(col, eye, face):
    # 직접 그린 로봇(실제 로고 아님). face=1 오른쪽을 봄, -1 왼쪽을 봄
    sx = 1 if face > 0 else -1
    return f"""<svg viewBox="0 0 400 460" width="460" height="530" style="transform:scaleX({sx});filter:drop-shadow(0 0 40px {col}88)">
  <defs><linearGradient id="g{col[1:]}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".55"/><stop offset=".25" stop-color="{col}"/><stop offset="1" stop-color="{col}" stop-opacity=".75"/></linearGradient></defs>
  <line x1="200" y1="40" x2="200" y2="95" stroke="#E8E8F0" stroke-width="10" stroke-linecap="round"/><circle cx="200" cy="34" r="20" fill="{eye}" style="filter:drop-shadow(0 0 16px {eye})"/>
  <rect x="70" y="92" width="260" height="190" rx="56" fill="url(#g{col[1:]})" stroke="#0A0A12" stroke-width="10"/>
  <rect x="44" y="150" width="34" height="80" rx="14" fill="#2A2F45" stroke="#0A0A12" stroke-width="8"/><rect x="322" y="150" width="34" height="80" rx="14" fill="#2A2F45" stroke="#0A0A12" stroke-width="8"/>
  <rect x="104" y="138" width="192" height="96" rx="40" fill="#0B0E1E" stroke="#0A0A12" stroke-width="6"/>
  <ellipse cx="160" cy="186" rx="22" ry="28" fill="{eye}" style="filter:drop-shadow(0 0 14px {eye})"/><circle cx="168" cy="176" r="7" fill="#fff"/>
  <ellipse cx="240" cy="186" rx="22" ry="28" fill="{eye}" style="filter:drop-shadow(0 0 14px {eye})"/><circle cx="248" cy="176" r="7" fill="#fff"/>
  <rect x="120" y="292" width="160" height="120" rx="40" fill="url(#g{col[1:]})" stroke="#0A0A12" stroke-width="10"/>
  <circle cx="200" cy="352" r="22" fill="{eye}" style="filter:drop-shadow(0 0 14px {eye})"/>
  <rect x="270" y="300" width="110" height="38" rx="19" fill="url(#g{col[1:]})" stroke="#0A0A12" stroke-width="9" transform="rotate(-28 280 320)"/>
  <circle cx="372" cy="270" r="30" fill="{col}" stroke="#0A0A12" stroke-width="9"/>
</svg>"""

def page_versus(t, accent):
    fonts = (ROOT / "assets" / "fonts").as_uri()
    lc = t.get("left_color", "#FF8A3D"); rc = t.get("right_color", "#3D8BFF")
    le = t.get("left_eye", "#FFE27A"); re_ = t.get("right_eye", "#7CF7FF")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts}/Pretendard-Black.otf')}}
@font-face{{font-family:K;font-weight:800;src:url('{fonts}/Pretendard-ExtraBold.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#05060C}}
.half{{position:absolute;top:0;bottom:0;width:58%}}
#L{{left:0;background:radial-gradient(circle at 25% 55%,{lc}cc 0%,{lc}55 30%,#1a0a02 75%);clip-path:polygon(0 0,100% 0,72% 100%,0 100%)}}
#R{{right:0;background:radial-gradient(circle at 75% 55%,{rc}cc 0%,{rc}55 30%,#020a1a 75%);clip-path:polygon(28% 0,100% 0,100% 100%,0 100%)}}
.rays{{position:absolute;inset:0;background:repeating-conic-gradient(from 0deg at 50% 52%,rgba(255,255,255,.06) 0 6deg,transparent 6deg 14deg)}}
.bolt{{position:absolute;left:50%;top:-4%;height:110%;width:120px;transform:translateX(-50%) skewX(-18deg);background:linear-gradient(180deg,#fff,#FFF1A8);
  clip-path:polygon(40% 0,100% 0,62% 44%,90% 44%,20% 100%,42% 54%,10% 54%);filter:drop-shadow(0 0 30px #fff) drop-shadow(0 0 60px #FFE27A)}}
#rl{{position:absolute;left:60px;bottom:10px}} #rr{{position:absolute;right:60px;bottom:10px}}
#vs{{position:absolute;left:50%;top:50%;transform:translate(-50%,-30%) rotate(-8deg);font-weight:900;font-size:230px;color:#fff;letter-spacing:-8px;
  -webkit-text-stroke:14px #0A0A12;paint-order:stroke fill;text-shadow:0 0 50px #FFE27A,0 0 100px #FF3DF2}}
#tr{{position:absolute;left:50%;top:190px;transform:translateX(-50%);filter:drop-shadow(0 0 30px #FFE27A)}}
#ban{{position:absolute;left:50%;top:44px;transform:translateX(-50%) rotate(-2deg);padding:10px 44px 16px;background:#FFE27A;color:#0A0A12;font-weight:900;font-size:78px;letter-spacing:-3px;
  border:8px solid #0A0A12;border-radius:18px;box-shadow:10px 10px 0 #0A0A12;white-space:nowrap}}
.nm{{position:absolute;bottom:56px;font-weight:900;font-size:120px;color:#fff;letter-spacing:-5px;-webkit-text-stroke:14px #0A0A12;paint-order:stroke fill;white-space:nowrap}}
#nl{{left:470px;text-shadow:0 0 40px {lc}}} #nr{{right:500px;text-shadow:0 0 40px {rc}}}
#q{{position:absolute;left:50%;bottom:190px;transform:translateX(-50%);font-weight:900;font-size:66px;color:#FFE27A;-webkit-text-stroke:10px #0A0A12;paint-order:stroke fill;white-space:nowrap}}
</style></head><body>
<div class="half" id="L"></div><div class="half" id="R"></div><div class="rays"></div><div class="bolt"></div>
<div id="rl">{_robot(lc, le, 1)}</div><div id="rr">{_robot(rc, re_, -1)}</div>
<div id="tr"><svg viewBox="0 0 200 200" width="200" height="200"><path d="M50 20h100v50a50 50 0 0 1-100 0z" fill="#FFD23F" stroke="#0A0A12" stroke-width="9"/>
<path d="M50 34H22v14a30 30 0 0 0 32 30M150 34h28v14a30 30 0 0 1-32 30" fill="none" stroke="#0A0A12" stroke-width="9"/><rect x="88" y="118" width="24" height="30" fill="#FFD23F" stroke="#0A0A12" stroke-width="8"/>
<rect x="58" y="146" width="84" height="28" rx="6" fill="#FFD23F" stroke="#0A0A12" stroke-width="9"/><text x="100" y="92" text-anchor="middle" font-family="K" font-weight="900" font-size="66" fill="#0A0A12">?</text></svg></div>
<div id="vs">VS</div>
<div id="ban">{_h.escape(t.get('banner', ''))}</div>
<div class="nm" id="nl">{_h.escape(t.get('left_name', ''))}</div><div class="nm" id="nr">{_h.escape(t.get('right_name', ''))}</div>
<div id="q">{_h.escape(t.get('question', ''))}</div>
</body></html>"""


# ── layout: badge (2026-11-07 현철님 본보기 '피보나치 42분 풀튜토리얼'): 보랏빛 판 + 빨간 띠 + 아주 큰 흰 제목 + 노랑·연두 둘째 줄 + 연두 알약 버튼 + 오른쪽 돋보기(막대·기준선)
def page_badge(t, accent):
    import random
    fonts = (ROOT / "assets" / "fonts").as_uri()
    esc = _h.escape
    r = random.Random(5)
    # 배경: 흐린 캔들 막대(직접 그림)
    cand = []
    for i in range(60):
        x = 980 + i * 16; h = r.randint(30, 160); y = r.randint(60, 900); col = "#FF4FB0" if r.random() < .45 else "#59F28A"
        cand.append(f'<rect x="{x}" y="{y}" width="9" height="{h}" fill="{col}" opacity="{r.uniform(.08, .22):.2f}"/>')
    # 돋보기 안 막대(오르는 모양)
    bars = []
    for i in range(16):
        x = 70 + i * 34; base = 560 - i * 22 + r.randint(-20, 20); h = r.randint(40, 110); up = r.random() < .7
        col = "#59F28A" if up else "#FF5D7A"
        bars.append(f'<line x1="{x + 8}" y1="{base - h - 18}" x2="{x + 8}" y2="{base + 18}" stroke="{col}" stroke-width="3"/><rect x="{x}" y="{base - h}" width="16" height="{h}" rx="2" fill="{col}"/>')
    lv = t.get("levels") or [["회사 193배", .32], ["실측 8배", .52], ["76배 싸다", .72]]
    lines = "".join(f'<line x1="40" y1="{int(700 * y)}" x2="660" y2="{int(700 * y)}" stroke="#fff" stroke-width="5" opacity=".9"/>'
                    f'<text x="640" y="{int(700 * y) - 16}" text-anchor="end" font-family="K" font-weight="900" font-size="52" fill="#fff" stroke="#0A0A12" stroke-width="10" paint-order="stroke">{esc(n)}</text>' for n, y in lv)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#120818}}
#panel{{position:absolute;inset:26px;border-radius:44px;overflow:hidden;background:radial-gradient(ellipse at 30% 40%,#3A1460 0%,#1C0A30 55%,#0B0614 100%);
  box-shadow:0 0 0 6px #0A0A12,0 0 0 10px rgba(180,120,255,.35)}}
#grain{{position:absolute;inset:0;opacity:.35;background-image:radial-gradient(rgba(255,255,255,.12) 1px,transparent 1px);background-size:6px 6px}}
#cd{{position:absolute;inset:0}}
#badge{{position:absolute;left:96px;top:70px;padding:8px 46px 14px;border-radius:999px;background:linear-gradient(180deg,#FF5A3D,#D9261C);
  border:6px solid #0A0A12;font-weight:900;font-size:66px;color:#fff;letter-spacing:-2px;-webkit-text-stroke:3px #7A0E08;paint-order:stroke fill;box-shadow:0 8px 0 #0A0A12}}
#t1{{position:absolute;left:84px;top:180px;font-weight:900;font-size:{t.get('size1', 300)}px;line-height:1;color:#fff;letter-spacing:-12px;
  -webkit-text-stroke:22px #0A0A12;paint-order:stroke fill;text-shadow:0 14px 0 #0A0A12;white-space:nowrap}}
#t2{{position:absolute;left:90px;top:{t.get('top2', 520)}px;font-weight:900;font-size:{t.get('size2', 170)}px;line-height:1;letter-spacing:-8px;white-space:nowrap;
  background:linear-gradient(180deg,#FFF36B 0%,#D8F56A 55%,#9BE86A 100%);-webkit-background-clip:text;color:transparent;
  filter:drop-shadow(0 0 0 #0A0A12) drop-shadow(6px 6px 0 #0A0A12) drop-shadow(-6px -6px 0 #0A0A12) drop-shadow(6px -6px 0 #0A0A12) drop-shadow(-6px 6px 0 #0A0A12) drop-shadow(0 12px 0 #0A0A12)}}
#pill{{position:absolute;left:96px;top:{t.get('top3', 760)}px;display:flex;align-items:center;gap:34px;padding:20px 56px 24px 36px;border-radius:120px;
  background:linear-gradient(180deg,#E9FF8A,#B8F04E);border:8px solid #0A0A12;box-shadow:0 10px 0 #0A0A12}}
#pill span{{font-weight:900;font-size:120px;color:#0A0A12;letter-spacing:-5px;white-space:nowrap}}
#lens{{position:absolute;right:120px;top:90px;width:680px;height:680px;border-radius:50%;overflow:hidden;
  background:radial-gradient(circle at 40% 35%,#4A1C7A 0%,#22103A 60%,#0B0614 100%);
  box-shadow:0 0 0 22px #2A2034,0 0 0 30px #8B6BC9,0 0 0 38px #0A0A12,0 0 80px 40px rgba(160,90,255,.45),inset 0 0 80px rgba(0,0,0,.7)}}
#lens::after{{content:"";position:absolute;left:12%;top:8%;width:46%;height:22%;border-radius:50%;background:linear-gradient(180deg,rgba(255,255,255,.25),transparent);transform:rotate(-20deg)}}
#handle{{position:absolute;left:1600px;top:735px;width:86px;height:250px;border-radius:40px;background:linear-gradient(90deg,#5A5466,#B9B2C8,#5A5466);
  border:8px solid #0A0A12;transform:rotate(-45deg);transform-origin:50% 0}}
</style></head><body><div id="panel"><div id="grain"></div>
<svg id="cd" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(cand)}</svg>
<div id="handle"></div>
<div id="lens"><svg viewBox="0 0 700 700" width="700" height="700">{"".join(bars)}
  <polyline points="70,600 300,420 560,170" stroke="#fff" stroke-width="4" stroke-dasharray="10 10" fill="none" opacity=".8"/><circle cx="560" cy="170" r="14" fill="#fff"/>{lines}</svg></div>
<div id="badge">{esc(t.get('badge', ''))}</div>
<div id="t1">{esc(t.get('line1', ''))}</div>
<div id="t2">{esc(t.get('line2', ''))}</div>
<div id="pill"><svg viewBox="0 0 120 100" width="150" height="125"><rect x="6" y="6" width="108" height="80" rx="10" fill="#fff" stroke="#0A0A12" stroke-width="8"/>
  <line x1="6" y1="26" x2="114" y2="26" stroke="#0A0A12" stroke-width="6"/><circle cx="20" cy="16" r="3.5" fill="#0A0A12"/><circle cx="32" cy="16" r="3.5" fill="#0A0A12"/><circle cx="44" cy="16" r="3.5" fill="#0A0A12"/>
  <rect x="24" y="48" width="10" height="26" fill="#0A0A12"/><rect x="42" y="38" width="10" height="36" fill="#0A0A12"/><rect x="60" y="54" width="10" height="20" fill="#0A0A12"/>
  <circle cx="86" cy="66" r="16" fill="#fff" stroke="#0A0A12" stroke-width="7"/><line x1="98" y1="78" x2="112" y2="92" stroke="#0A0A12" stroke-width="9" stroke-linecap="round"/></svg>
  <span>{esc(t.get('pill', ''))}</span></div>
</div>
<script>for(const id of ['t1','t2']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1150&&f>80){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""


def make(proj, out_dir, proj_dir=".", log=print):
    t = proj.get("thumbnail")
    if not t:
        log("  ⚠ thumbnail: 대본에 thumbnail 칸이 없어 썸네일을 만들지 않음(PUB-02)")
        return None
    from PIL import Image
    from playwright.sync_api import sync_playwright
    bg = t.get("bg")
    bgp = None
    if bg and t.get("layout") != "tiles":
        for base in (Path(proj_dir), ROOT):
            if (base / bg).exists():
                bgp = (base / bg).resolve()
                break
        if not bgp:
            log(f"  ⚠ thumbnail: 배경 그림 {bg} 없음 → 기본 네온 배경")
    html = (Path(out_dir) / "_thumb.html").resolve()
    if t.get("layout") == "badge":
        html.write_text(page_badge(t, t.get("accent", "#FF4FB0")), encoding="utf-8")
    elif t.get("layout") == "versus":
        html.write_text(page_versus(t, t.get("accent", "#FF8A3D")), encoding="utf-8")
    elif t.get("layout") == "tiles":
        html.write_text(page_tiles(t, t.get("accent", "#D7F25A")), encoding="utf-8")
    else:
        html.write_text(page(t, bgp.as_uri() if bgp else None), encoding="utf-8")
    exe = "/opt/pw-browsers/chromium" if Path("/opt/pw-browsers/chromium").exists() else None
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(html.as_uri())
        pg.evaluate("document.fonts.ready")
        png = pg.screenshot()
        b.close()
    html.unlink()
    im = Image.open(io.BytesIO(png)).convert("RGB")
    out = Path(out_dir) / "thumbnail.jpg"
    for q in (95, 92, 88, 84, 80):
        im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        if out.stat().st_size <= MAX_BYTES:
            break
    log(f"  썸네일: {out} ({W}x{H}, {out.stat().st_size / 1024:.0f}KB)")
    return out
