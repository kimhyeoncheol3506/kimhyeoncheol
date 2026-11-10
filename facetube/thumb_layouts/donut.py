"""layout: donut (2026-11-10 일꾼E, '클로드 개인 재무' 썸네일)
짙은 자주→빨강 대각 바탕 + 살구색 점 물결 + 왼쪽 아주 큰 흰 제목 + 빨강 띠 위 둘째 줄 + 셋째 줄 [[살구 강조]]
+ 오른쪽 아주 큰 네온 '지출 도넛'(조각 2~4개, 가운데 자물쇠 + 글자) + 조각 이름표 + 살구색 동전 더미.
기존 모양(default·tiles·versus·badge·phone·calendar·film·ticket·orbit·shield·board)과 겹치지 않게: 순위판·영수증·방패가 아닌 원 그래프.
대본:
  thumbnail:
    layout: donut
    badge: "작은 꼬리표"
    line1: "큰 제목"
    line2: "빨강 띠 글자"
    line3: "셋째 줄 [[강조]]"
    donut_title: "도넛 위 제목"
    donut_center: "가운데 글자"
    donut_parts: [["월세·공과금", 52], ["식음료", 24], ["기타", 24]]   # 비율(합 100 아니어도 됨)
    color: "#FF4757"   # 선택(빨강) · color2: "#FFD6A5"(살구)
"""
import html as _h
import math
import re


def _mk(s, acc):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{acc}">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    acc = t.get("color", "#FF4757")
    apr = t.get("color2", "#FFD6A5")
    parts = t.get("donut_parts") or [["A", 50], ["B", 30], ["C", 20]]
    tot = sum(float(v) for _, v in parts) or 1
    cols = [acc, apr, "#8A6E72", "#C23A4B"]
    cx, cy, r, sw = 1400, 590, 260, 116
    segs, labels, a0 = [], [], 0.0
    for i, (k, v) in enumerate(parts):
        a1 = a0 + float(v) / tot
        p = lambda a: (cx + r * math.cos(2 * math.pi * a - math.pi / 2), cy + r * math.sin(2 * math.pi * a - math.pi / 2))
        x0, y0 = p(a0 + 0.006)
        x1, y1 = p(a1 - 0.006)
        big = 1 if (a1 - a0) > 0.5 else 0
        c = cols[i % len(cols)]
        glow = f'filter="url(#g)"' if i == 0 else ""
        segs.append(f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 {big} 1 {x1:.1f} {y1:.1f}" stroke="{c}" stroke-width="{sw}" fill="none" {glow}/>')
        mid = (a0 + a1) / 2
        lx = cx + (r + 120) * math.cos(2 * math.pi * mid - math.pi / 2)
        lx = min(max(lx, 1060), 1740)
        ly = cy + (r + 110) * math.sin(2 * math.pi * mid - math.pi / 2)
        labels.append(f'<div class="lb" style="left:{lx:.0f}px;top:{ly:.0f}px;border-color:{c}"><i style="background:{c}"></i>{esc(str(k))}</div>')
        a0 = a1
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#140A0C}}
#bg{{position:absolute;inset:0;background:linear-gradient(125deg,#140A0C 0%,#3B0E1A 42%,#7A1626 78%,#A3222F 100%)}}
#dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,214,165,.22) 2.6px,transparent 3px);background-size:46px 46px;
  -webkit-mask-image:radial-gradient(circle at 75% 55%,#000 0%,transparent 70%)}}
#k{{position:absolute;left:84px;top:80px;font-size:50px;color:#140A0C;background:{apr};padding:8px 30px 14px;border-radius:999px;letter-spacing:-1px}}
#t1{{position:absolute;left:70px;top:176px;font-size:{t.get('size1', 200)}px;line-height:1;color:#fff;letter-spacing:-9px;white-space:nowrap;
  text-shadow:0 10px 0 #000,0 0 50px rgba(255,71,87,.5)}}
#band{{position:absolute;left:0;top:{t.get('top2', 410)}px;padding:10px 60px 26px 70px;background:{acc};transform:rotate(-2.5deg);transform-origin:0 50%;
  box-shadow:0 14px 0 #000,0 0 60px rgba(255,71,87,.6)}}
#band span{{font-size:{t.get('size2', 170)}px;color:#fff;letter-spacing:-8px;white-space:nowrap;line-height:1.05;text-shadow:0 6px 0 rgba(0,0,0,.35)}}
#t3{{position:absolute;left:74px;top:{t.get('top3', 700)}px;font-size:{t.get('size3', 130)}px;color:#fff;letter-spacing:-6px;white-space:nowrap;
  text-shadow:0 8px 0 #000}}
#dh{{position:absolute;left:1140px;top:118px;width:520px;text-align:center;font-size:52px;color:{apr};letter-spacing:-2px}}
#ring{{position:absolute;left:0;top:0}}
#ctr{{position:absolute;left:{cx-170}px;top:{cy-120}px;width:340px;text-align:center}}
#ctr .lk{{font-size:110px;line-height:1}}
#ctr b{{display:block;font-size:56px;color:#fff;margin-top:10px;letter-spacing:-2px}}
.lb{{position:absolute;transform:translate(-50%,-50%);font-size:38px;color:#fff;background:rgba(20,10,12,.9);border:4px solid;border-radius:18px;
  padding:6px 18px 10px;white-space:nowrap}}
.lb i{{display:inline-block;width:22px;height:22px;border-radius:11px;margin-right:12px;vertical-align:2px}}
.coin{{position:absolute;width:150px;height:46px;border-radius:50%;background:{apr};border:5px solid #C98E56;box-shadow:0 6px 0 #8A5A2E}}
</style></head><body><div id="bg"></div><div id="dots"></div>
<svg id="ring" width="{W}" height="{H}"><defs><filter id="g" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<circle cx="{cx}" cy="{cy}" r="{r}" stroke="rgba(255,255,255,.08)" stroke-width="{sw}" fill="none"/>{''.join(segs)}</svg>
{''.join(labels)}
<div id="ctr"><div class="lk">🔒</div><b>{esc(t.get('donut_center', ''))}</b></div>
<div id="dh">{esc(t.get('donut_title', ''))}</div>
<div class="coin" style="left:1010px;top:930px"></div><div class="coin" style="left:1010px;top:900px"></div><div class="coin" style="left:1018px;top:870px"></div>
<div class="coin" style="left:1150px;top:950px"></div><div class="coin" style="left:1146px;top:920px"></div>
<div id="k">{esc(t.get('badge', ''))}</div>
<div id="t1">{esc(t.get('line1', ''))}</div>
<div id="band"><span>{esc(t.get('line2', ''))}</span></div>
<div id="t3">{_mk(t.get('line3', ''), apr)}</div>
<script>for(const id of ['t1','t3']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1080&&f>70){{f-=6;e.style.fontSize=f+'px'}}}}
{{const e=document.querySelector('#band span');let f=parseFloat(getComputedStyle(e).fontSize);while(document.getElementById('band').getBoundingClientRect().right>1100&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
