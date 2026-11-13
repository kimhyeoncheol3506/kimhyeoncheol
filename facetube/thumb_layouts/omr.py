"""layout: omr (2026-11-13 안경 일꾼, 'AI 안경 시험 커닝' 썸네일)
남색 먹빛 → 난초 보라 대각 바탕 + 아주 작은 별 + 왼쪽 큰 제목 세 줄(둘째 줄 [[ ]] 는 보라 상자)
+ 오른쪽 기울어진 OMR 답안지(번호 줄·동그라미, 일부 칠함) + 그 위 네온 선으로 그린 안경 기호(렌즈 속 '?')
+ 안경 카메라에서 답안지로 내려가는 스캔 빛.
기존 모양(default·tiles·versus·badge·phone·calendar·film·ticket·orbit·shield·board·oa_viewfinder·donut·podium)과 겹치지 않게:
순위판·도넛·방패가 아닌 '답안지 + 안경'. 실제 제품 모양·로고 없이 도형으로만 그린다.
대본:
  thumbnail:
    layout: omr
    badge: "작은 꼬리표"
    line1: "첫 줄(흰색)"
    line2: "[[강조]] 둘째 줄"
    line3: "셋째 줄(하늘색)"
    color: "#E879F9"    # 선택(난초 보라) · color2: "#93C5FD"(하늘)
    marks: [1, 4, 2, 3, 1]   # 선택: 답안지 줄마다 칠할 번호(1~4)
"""
import html as _h
import re


def _mk(s, acc):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", rf'<span class="hl">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    acc = t.get("color", "#E879F9")
    sky = t.get("color2", "#93C5FD")
    marks = t.get("marks") or [1, 4, 2, 3, 1, 4]
    rows = []
    for i, m in enumerate(marks):
        bub = "".join(f'<i class="{"on" if j == m else ""}">{j}</i>' for j in range(1, 5))
        rows.append(f'<div class="row"><b>{i + 1}</b>{bub}</div>')
    stars = "".join(f'<s style="left:{(i * 397) % 1920}px;top:{(i * 223) % 1080}px;opacity:{.15 + .5 * ((i * 37) % 10) / 10:.2f}"></s>' for i in range(70))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#0D0C1C}}
#bg{{position:absolute;inset:0;background:linear-gradient(120deg,#0D0C1C 0%,#1B1238 45%,#4A1A5E 80%,#7A2A86 100%)}}
#glow{{position:absolute;left:1000px;top:60px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(232,121,249,.35),transparent 65%)}}
s{{position:absolute;width:4px;height:4px;border-radius:2px;background:#fff}}
#k{{position:absolute;left:80px;top:84px;font-size:48px;color:#0D0C1C;background:{sky};padding:8px 30px 14px;border-radius:999px;letter-spacing:-1px}}
#t1{{position:absolute;left:72px;top:186px;font-size:{t.get('size1', 170)}px;line-height:1;color:#fff;letter-spacing:-8px;white-space:nowrap;text-shadow:0 10px 0 #000}}
#t2{{position:absolute;left:72px;top:{t.get('top2', 400)}px;font-size:{t.get('size2', 170)}px;line-height:1.1;color:#fff;letter-spacing:-8px;white-space:nowrap;text-shadow:0 10px 0 #000}}
#t2 .hl{{background:{acc};color:#170A20;padding:0 22px 8px;border-radius:22px;text-shadow:none;box-shadow:0 12px 0 #000,0 0 70px rgba(232,121,249,.7)}}
#t3{{position:absolute;left:78px;top:{t.get('top3', 690)}px;font-size:{t.get('size3', 92)}px;color:{sky};letter-spacing:-4px;white-space:nowrap;text-shadow:0 7px 0 #000}}
#card{{position:absolute;left:1240px;top:330px;width:520px;height:660px;background:#FBF7EE;border-radius:26px;transform:rotate(8deg);
  box-shadow:0 30px 0 rgba(0,0,0,.55),0 0 0 8px rgba(255,255,255,.12);padding:34px 40px;box-sizing:border-box}}
#card .hd{{height:64px;border-radius:12px;background:#F3D6F7;margin-bottom:26px;display:flex;align-items:center;padding-left:24px;font-size:40px;color:#7A2A86;letter-spacing:-1px}}
.row{{display:flex;align-items:center;gap:22px;height:84px;border-bottom:3px dashed #E6DCC8}}
.row b{{width:56px;font-size:44px;color:#3B2F4A}}
.row i{{font-style:normal;width:62px;height:62px;border-radius:50%;border:5px solid #B68BC1;box-sizing:border-box;display:flex;align-items:center;justify-content:center;font-size:30px;color:#B68BC1}}
.row i.on{{background:#2A1438;border-color:#2A1438;color:transparent}}
#beam{{position:absolute;left:0;top:0}}
#gl{{position:absolute;left:0;top:0}}
</style></head><body><div id="bg"></div><div id="glow"></div>{stars}
<div id="card"><div class="hd">답안지</div>{''.join(rows)}</div>
<svg id="beam" width="{W}" height="{H}"><defs><linearGradient id="bm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky}" stop-opacity=".75"/><stop offset="1" stop-color="{sky}" stop-opacity="0"/></linearGradient></defs>
<polygon points="1470,250 1250,720 1790,800" fill="url(#bm)" opacity=".55"/></svg>
<svg id="gl" width="{W}" height="{H}"><defs><filter id="g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<g filter="url(#g)" stroke="{acc}" stroke-width="22" fill="rgba(13,12,28,.55)" stroke-linejoin="round" stroke-linecap="round">
<rect x="1110" y="120" width="300" height="210" rx="86"/><rect x="1530" y="120" width="300" height="210" rx="86"/>
<path d="M1410 200 Q1470 160 1530 200" fill="none"/><path d="M1110 170 L1040 150" fill="none"/><path d="M1830 170 L1890 150" fill="none"/></g>
<circle cx="1470" cy="250" r="18" fill="{sky}" filter="url(#g)"/>
<text x="1260" y="272" text-anchor="middle" font-family="K" font-size="170" fill="#fff">?</text>
<text x="1680" y="272" text-anchor="middle" font-family="K" font-size="170" fill="#fff">?</text></svg>
<div id="k">{esc(t.get('badge', ''))}</div>
<div id="t1">{esc(t.get('line1', ''))}</div>
<div id="t2">{_mk(t.get('line2', ''), acc)}</div>
<div id="t3">{esc(t.get('line3', ''))}</div>
<script>for(const [id,mx] of [['t1',1180],['t2',1220],['t3',1180]]){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>mx&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
