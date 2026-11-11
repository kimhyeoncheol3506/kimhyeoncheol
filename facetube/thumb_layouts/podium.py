"""layout: podium (2026-11-11 스킬3 일꾼, '이번 주 클로드 스킬 TOP 3' 썸네일)
밝은 형광 연두 바탕 + 굵은 검정 사선 줄무늬 + 왼쪽 아주 큰 검정 제목(둘째 줄 검정 띠 위 연두 글자, 셋째 줄 [[보라 강조]])
+ 오른쪽 '시상대' 3칸(2·1·3 순서, 가운데가 가장 높음) 위에 직접 그린 기호 타일(돋보기·마우스 화살표·재생 버튼)
+ 위쪽 보라 별 도장('1만+'). 실제 로고·인물 없음, 그림 생성 없음(크레딧 0).
기존 모양(default·tiles·versus·badge·phone·calendar·film·ticket·orbit·shield·board·oa_viewfinder·donut)과 겹치지 않게: 시상대·밝은 연두 바탕.
대본:
  thumbnail:
    layout: podium
    badge: "작은 꼬리표"
    line1: "큰 제목"
    line2: "검정 띠 [[강조]]"
    line3: "셋째 줄 [[강조]]"
    podium: [{rank: "1", icon: find, name: "스킬 찾기"}, {rank: "2", icon: cursor, name: "..."}, {rank: "3", icon: play, name: "..."}]
    stamp: "1만+"            # 선택(별 도장 글자)
    color: "#D4FF3A"          # 선택(바탕 연두) · color2: "#7B5CFF"(보라)
"""
import html as _h
import re

ICONS = {
    "find": '<svg viewBox="0 0 100 100"><circle cx="42" cy="42" r="26" fill="none" stroke="#111" stroke-width="12"/><path d="M61 61 L86 86" stroke="#111" stroke-width="15" stroke-linecap="round"/></svg>',
    "cursor": '<svg viewBox="0 0 100 100"><path d="M22 10 L22 80 L40 64 L53 92 L67 85 L54 58 L80 58 Z" fill="#111"/></svg>',
    "play": '<svg viewBox="0 0 100 100"><rect x="8" y="18" width="84" height="64" rx="14" fill="#111"/><path d="M42 34 L66 50 L42 66 Z" fill="{acc}"/></svg>',
}
_ORDER = {"find": "find", "cursor": "cursor", "play": "play"}


def _mk(s, acc):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{acc}">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    acc = t.get("color", "#D4FF3A")
    vio = t.get("color2", "#7B5CFF")
    pod = t.get("podium") or []
    defaults = ["find", "cursor", "play"]
    by_rank = {}
    for i, p in enumerate(pod[:3]):
        by_rank[str(p.get("rank", i + 1))] = (p, p.get("icon") or defaults[i])
    cols = []
    # 2 · 1 · 3 순서로, 높이는 1 > 2 > 3
    spec = [("2", 300, 1220), ("1", 400, 1450), ("3", 230, 1680)]
    for rank, h, x in spec:
        p, ic = by_rank.get(rank, ({"name": ""}, "find"))
        svg = ICONS.get(ic, ICONS["find"]).replace("{acc}", acc)
        cols.append(
            f'<div class="col" style="left:{x - 105}px;height:{h}px"><div class="num">{esc(rank)}</div>'
            f'<div class="nm">{esc(p.get("name", ""))}</div></div>'
            f'<div class="ico" style="left:{x - 85}px;top:{1000 - h - 200}px">{svg}</div>')
    stamp = t.get("stamp", "1만+")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:{acc}}}
#bg{{position:absolute;inset:0;background:repeating-linear-gradient(-28deg,rgba(0,0,0,.07) 0 34px,transparent 34px 110px)}}
#glow{{position:absolute;left:1050px;top:80px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.75),transparent 62%)}}
#floor{{position:absolute;left:0;right:0;top:1000px;height:80px;background:#111}}
#k{{position:absolute;left:78px;top:70px;font-size:48px;color:{acc};background:#111;padding:8px 30px 14px;border-radius:999px;letter-spacing:-1px;transform:rotate(-2deg)}}
#t1{{position:absolute;left:66px;top:158px;font-size:{t.get('size1', 176)}px;line-height:1;color:#111;letter-spacing:-8px;white-space:nowrap;
  text-shadow:6px 8px 0 rgba(255,255,255,.65)}}
#t2{{position:absolute;left:58px;top:{t.get('top2', 370)}px;padding:8px 32px 22px;background:#111;border-radius:20px;transform:rotate(-1.5deg);
  box-shadow:10px 12px 0 {vio}}}
#t2 span{{font-size:{t.get('size2', 150)}px;color:#fff;letter-spacing:-7px;white-space:nowrap}}
#t3{{position:absolute;left:70px;top:{t.get('top3', 660)}px;font-size:{t.get('size3', 128)}px;color:#111;letter-spacing:-6px;white-space:nowrap;
  text-shadow:6px 8px 0 rgba(255,255,255,.65)}}
.col{{position:absolute;bottom:80px;width:210px;background:#111;border-radius:22px 22px 0 0;border:6px solid #111;
  box-shadow:inset 0 10px 0 rgba(255,255,255,.12)}}
.col .num{{position:absolute;left:0;right:0;top:18px;text-align:center;font-size:120px;line-height:1;color:{acc}}}
.col .nm{{position:absolute;left:0;right:0;top:150px;text-align:center;font-size:36px;color:#fff;letter-spacing:-1px;line-height:1.1;padding:0 8px}}
.ico{{position:absolute;width:170px;height:170px;border-radius:36px;background:#fff;border:8px solid #111;box-shadow:0 12px 0 #111;
  display:flex;align-items:center;justify-content:center}}
.ico svg{{width:120px;height:120px}}
#st{{position:absolute;left:1650px;top:60px;width:230px;height:230px;transform:rotate(12deg)}}
#st svg{{position:absolute;inset:0}}
#st b{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:64px;color:#fff;letter-spacing:-3px;font-weight:900}}
</style></head><body><div id="bg"></div><div id="glow"></div><div id="floor"></div>
{''.join(cols)}
<div id="st"><svg viewBox="0 0 100 100"><polygon fill="{vio}" stroke="#111" stroke-width="4" points="50,2 61,20 82,14 79,36 98,46 82,60 88,82 66,80 56,98 44,82 22,90 22,68 2,58 18,42 10,22 32,22 40,4"/></svg><b>{esc(stamp)}</b></div>
<div id="k">{esc(t.get('badge', ''))}</div>
<div id="t1">{_mk(t.get('line1', ''), vio)}</div>
<div id="t2"><span>{_mk(t.get('line2', ''), acc)}</span></div>
<div id="t3">{_mk(t.get('line3', ''), vio)}</div>
<script>for(const id of ['t1','t3']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1100&&f>70){{f-=6;e.style.fontSize=f+'px'}}}}
{{const e=document.querySelector('#t2 span');let f=parseFloat(getComputedStyle(e).fontSize);while(document.getElementById('t2').getBoundingClientRect().right>1100&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
