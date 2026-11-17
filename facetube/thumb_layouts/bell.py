"""layout: bell (2026-11-17 IPO 일꾼, '앤트로픽 상장' 썸네일)
따뜻한 먹색 → 짙은 금빛 바탕 + 가는 금선 격자 + 왼쪽 큰 제목 세 줄(둘째 줄 [[ ]] 는 금색 상자)
+ 오른쪽 네온 금선으로 그린 '상장 종'(울림 물결) + 아래쪽 LED 전광판 띠(점 글자, 값·화살표 없음).
기존 모양(default·tiles·versus·badge·phone·calendar·film·ticket·orbit·shield·board·oa_viewfinder·donut·podium·omr)과 겹치지 않게:
답안지·순위판·도넛이 아닌 '종 + 전광판'. 실제 거래소·회사 로고 없이 도형으로만 그린다.
투자 권유처럼 보이지 않게 가격·오름 화살표·그래프는 넣지 않는다.
대본:
  thumbnail:
    layout: bell
    badge: "작은 꼬리표"
    line1: "첫 줄(흰색)"
    line2: "[[강조]] 둘째 줄"
    line3: "셋째 줄(은색)"
    ticker: "전광판 글자"      # 선택
    color: "#F5C451"           # 선택(금색) · color2: "#E5E7EB"(은색)
"""
import html as _h
import re


def _mk(s):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    acc = t.get("color", "#F5C451")
    sil = t.get("color2", "#E5E7EB")
    tick = esc(t.get("ticker", ""))
    grid = "".join(f'<i style="left:{x}px"></i>' for x in range(0, W, 96))
    grid += "".join(f'<u style="top:{y}px"></u>' for y in range(0, H, 96))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#0E0D0A}}
#bg{{position:absolute;inset:0;background:radial-gradient(ellipse at 78% 38%,#5A4314 0%,#2A2010 38%,#0E0D0A 75%)}}
i{{position:absolute;top:0;width:1px;height:{H}px;background:rgba(245,196,81,.07)}}
u{{position:absolute;left:0;height:1px;width:{W}px;background:rgba(245,196,81,.07)}}
#k{{position:absolute;left:80px;top:80px;font-size:50px;color:#0E0D0A;background:{acc};padding:8px 32px 14px;border-radius:14px;letter-spacing:-1px;box-shadow:0 8px 0 #000}}
#t1{{position:absolute;left:72px;top:186px;font-size:{t.get('size1', 150)}px;line-height:1;color:#fff;letter-spacing:-7px;white-space:nowrap;text-shadow:0 10px 0 #000}}
#t2{{position:absolute;left:72px;top:{t.get('top2', 380)}px;font-size:{t.get('size2', 190)}px;line-height:1.1;color:#fff;letter-spacing:-9px;white-space:nowrap;text-shadow:0 10px 0 #000}}
#t2 .hl{{background:{acc};color:#1A1406;padding:0 24px 10px;border-radius:20px;text-shadow:none;box-shadow:0 12px 0 #000,0 0 80px rgba(245,196,81,.6)}}
#t3{{position:absolute;left:78px;top:{t.get('top3', 650)}px;font-size:{t.get('size3', 96)}px;color:{sil};letter-spacing:-4px;white-space:nowrap;text-shadow:0 7px 0 #000}}
#bell{{position:absolute;left:0;top:0}}
#led{{position:absolute;left:0;right:0;top:860px;height:150px;background:#050504;border-top:6px solid #2C2410;border-bottom:6px solid #2C2410;
  display:flex;align-items:center;justify-content:center;overflow:hidden}}
#led span{{font-size:104px;letter-spacing:22px;color:{acc};white-space:nowrap;
  -webkit-mask:radial-gradient(circle,#000 58%,transparent 62%) 0 0/14px 14px;mask:radial-gradient(circle,#000 58%,transparent 62%) 0 0/14px 14px;
  text-shadow:0 0 18px rgba(245,196,81,.9)}}
</style></head><body><div id="bg"></div>{grid}
<svg id="bell" width="{W}" height="{H}"><defs><filter id="g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="gd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE7A3"/><stop offset=".5" stop-color="{acc}"/><stop offset="1" stop-color="#9A6E14"/></linearGradient></defs>
<g transform="rotate(-12 1500 430)">
<rect x="1488" y="120" width="24" height="70" rx="10" fill="{acc}" filter="url(#g)"/>
<path d="M1500 180 C1380 180 1340 280 1335 400 C1330 520 1300 600 1240 660 L1760 660 C1700 600 1670 520 1665 400 C1660 280 1620 180 1500 180 Z" fill="url(#gd)" stroke="#FFF1C7" stroke-width="8" filter="url(#g)"/>
<rect x="1215" y="650" width="570" height="46" rx="23" fill="{acc}" stroke="#FFF1C7" stroke-width="6"/>
<circle cx="1500" cy="742" r="44" fill="{acc}" stroke="#FFF1C7" stroke-width="6" filter="url(#g)"/>
<path d="M1405 270 C1385 330 1380 400 1378 470" stroke="#FFF6DA" stroke-width="16" fill="none" stroke-linecap="round" opacity=".7"/></g>
<g fill="none" stroke="{acc}" stroke-linecap="round" filter="url(#g)">
<path d="M1150 300 Q1100 420 1150 540" stroke-width="12" opacity=".9"/><path d="M1080 250 Q1010 420 1080 590" stroke-width="10" opacity=".55"/>
<path d="M1860 300 Q1910 420 1860 540" stroke-width="12" opacity=".9"/><path d="M1930 250 Q2000 420 1930 590" stroke-width="10" opacity=".55"/></g></svg>
<div id="led"><span>{tick}</span></div>
<div id="k">{esc(t.get('badge', ''))}</div>
<div id="t1">{esc(t.get('line1', ''))}</div>
<div id="t2">{_mk(t.get('line2', ''))}</div>
<div id="t3">{esc(t.get('line3', ''))}</div>
<script>for(const [id,mx] of [['t1',1120],['t2',1160],['t3',1160]]){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>mx&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
