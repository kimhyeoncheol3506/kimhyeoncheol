# 썸네일 layout: shield (2026-11-10, 제미나이 4 카본) — 짙은 초록·민트 회로판 바탕 + 오른쪽 큰 방패(가운데 자물쇠·큰 숫자)
#   + 왼쪽 아주 굵은 두 줄 제목(둘째 줄 [[강조]]는 민트) + 방패 둘레 육각 칩 3개 + 아래 '경고 테이프' 띠.
# 대본 thumbnail 칸: badge, line1, line2, stat, stat_label, chips[3], lock(띠 글자), accent(기본 #3DF5B0)
# 실제 회사 로고는 그리지 않는다(방패·자물쇠는 직접 그린 도형).
import html
import re


def _mk(s, acc):
    s = html.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", lambda m: f'<span style="color:{acc}">{m.group(1)}</span>', s)


def page(t, fonts_uri, W, H):
    acc = t.get("accent", "#3DF5B0")
    chips = (t.get("chips") or ["찾기", "확인", "고치기"])[:3]
    pos = [(1180, 150), (1700, 330), (1650, 760)]
    chip_html = "".join(
        f'<div class="hex" style="left:{x - 95}px;top:{y - 82}px"><span>{html.escape(c)}</span></div>' for (x, y), c in zip(pos, chips))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#04140F}}
#bg{{position:absolute;inset:0;background:radial-gradient(circle at 72% 45%,#0F4A35 0%,#072A1F 38%,#04140F 75%)}}
#grid{{position:absolute;inset:0;opacity:.22;background-image:linear-gradient({acc}33 2px,transparent 2px),linear-gradient(90deg,{acc}33 2px,transparent 2px);background-size:80px 80px}}
#wires{{position:absolute;inset:0}}
#shield{{position:absolute;left:1130px;top:120px;width:560px;height:680px;overflow:visible}}
#chip{{position:absolute;left:80px;top:80px;font-size:52px;color:#04140F;background:{acc};padding:10px 32px 16px;border-radius:14px;letter-spacing:-1px;box-shadow:0 0 40px {acc}88}}
#t1{{position:absolute;left:72px;top:210px;font-size:{t.get('size1', 168)}px;line-height:1.02;color:#fff;letter-spacing:-8px;white-space:nowrap;
  -webkit-text-stroke:14px #021009;paint-order:stroke fill;text-shadow:0 12px 0 #021009}}
#t2{{position:absolute;left:72px;top:430px;font-size:{t.get('size2', 168)}px;line-height:1.02;color:#fff;letter-spacing:-8px;white-space:nowrap;
  -webkit-text-stroke:14px #021009;paint-order:stroke fill;text-shadow:0 12px 0 #021009}}
#stat{{position:absolute;left:1130px;top:470px;width:560px;text-align:center;font-size:118px;color:#fff;letter-spacing:-4px;text-shadow:0 0 30px {acc},0 6px 0 #021009}}
#statl{{position:absolute;left:1130px;top:610px;width:560px;text-align:center;font-size:40px;color:{acc};letter-spacing:-1px}}
.hex{{position:absolute;width:190px;height:164px;clip-path:polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%);background:{acc};display:flex;align-items:center;justify-content:center}}
.hex span{{display:flex;align-items:center;justify-content:center;width:172px;height:148px;clip-path:inherit;background:#062A1E;color:#fff;font-size:44px;letter-spacing:-2px}}
#tape{{position:absolute;left:-40px;right:-40px;top:880px;height:120px;transform:rotate(-2.5deg);
  background:repeating-linear-gradient(135deg,{acc} 0 46px,#04140F 46px 92px);box-shadow:0 10px 30px #0008}}
#tape b{{position:absolute;left:50%;top:50%;transform:translate(-50%,-52%);background:#04140F;color:#fff;font-size:66px;padding:4px 50px 12px;border:5px solid {acc};border-radius:16px;white-space:nowrap;letter-spacing:-2px}}
</style></head><body><div id="bg"></div><div id="grid"></div>
<svg id="wires" width="{W}" height="{H}"><g stroke="{acc}" stroke-width="5" fill="none" opacity=".55">
<path d="M1180 150 H1000 V60"/><path d="M1700 330 H1860 V120"/><path d="M1650 760 H1880"/><path d="M1130 600 H1010 V820"/></g>
<g fill="{acc}"><circle cx="1000" cy="60" r="12"/><circle cx="1860" cy="120" r="12"/><circle cx="1880" cy="760" r="12"/><circle cx="1010" cy="820" r="12"/></g></svg>
<svg id="shield" viewBox="0 0 560 680"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14C98C"/><stop offset="1" stop-color="#05402B"/></linearGradient></defs>
<path d="M280 20 L520 110 V330 C520 500 400 610 280 660 C160 610 40 500 40 330 V110 Z" fill="url(#g)" stroke="{acc}" stroke-width="14" style="filter:drop-shadow(0 0 40px {acc})"/>
<path d="M280 70 L475 145 V330 C475 470 380 560 280 605 C180 560 85 470 85 330 V145 Z" fill="#04140F" opacity=".55"/>
<rect x="205" y="250" width="150" height="120" rx="20" fill="{acc}"/><path d="M230 250 V205 a50 50 0 0 1 100 0 V250" stroke="{acc}" stroke-width="22" fill="none"/>
<circle cx="280" cy="300" r="16" fill="#04140F"/><rect x="273" y="300" width="14" height="40" rx="6" fill="#04140F"/></svg>
{chip_html}
<div id="stat">{html.escape(t.get('stat', ''))}</div>
<div id="statl">{html.escape(t.get('stat_label', ''))}</div>
<div id="chip">{html.escape(t.get('badge', ''))}</div>
<div id="t1">{_mk(t.get('line1', ''), acc)}</div>
<div id="t2">{_mk(t.get('line2', ''), acc)}</div>
<div id="tape"><b>🔒 {html.escape(t.get('lock', ''))}</b></div>
<script>for(const id of ['t1','t2']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1100&&f>70){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
