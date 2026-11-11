"""layout: oa_viewfinder (2026-11-10 일꾼F, 'GPT-6.1 테라' 썸네일)
짙은 청록 → 하늘색 사선 바탕 + 오로라 빛 + 왼쪽 아주 큰 흰 제목 + 연노랑 띠 둘째 줄 + 셋째 줄 [[하늘 강조]]
+ 오른쪽 '카메라 뷰파인더'(네 모서리 꺾쇠·십자선·초점 상자) 안에 작은 앱 화면(상품 타일 3개, 하나가 초점 상자에 잡힘)
+ 연노랑 커서 화살표가 버튼을 누름 + 아래 가격표 스티커(옛 가격 취소선 → 새 가격).
기존 모양(default·tiles·versus·badge·phone·calendar·film·ticket·orbit·shield·board)과 겹치지 않게: 뷰파인더·초점 상자·가격표.
대본:
  thumbnail:
    layout: oa_viewfinder
    badge: "작은 꼬리표"
    line1: "큰 제목"
    line2: "연노랑 띠 글자 [[강조]]"
    line3: "셋째 줄 [[강조]]"
    price_old: "$2"          # 선택(가격표 스티커)
    price_new: "$1"
    price_label: "입력 100만 토큰당"
    color: "#22D3EE"         # 선택(하늘)  · color2: "#FDE68A"(연노랑)
"""
import html as _h
import re


def _mk(s, acc):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{acc}">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    sky = t.get("color", "#22D3EE")
    yel = t.get("color2", "#FDE68A")
    price = ""
    if t.get("price_new"):
        price = (f'<div id="pr"><div class="pl">{esc(t.get("price_label", ""))}</div>'
                 f'<div class="pv"><s>{esc(t.get("price_old", ""))}</s><b>→</b><em>{esc(t.get("price_new", ""))}</em></div></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#06141B}}
#bg{{position:absolute;inset:0;background:linear-gradient(118deg,#04222B 0%,#06343F 42%,#0E6E86 78%,#46C7E0 100%)}}
#au{{position:absolute;left:-10%;right:-10%;top:-120px;height:520px;filter:blur(40px);opacity:.75;
  background:radial-gradient(ellipse at 30% 60%,rgba(34,211,238,.55),transparent 55%),radial-gradient(ellipse at 75% 40%,rgba(253,230,138,.45),transparent 50%)}}
#dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.10) 2px,transparent 2px);background-size:44px 44px;
  -webkit-mask-image:linear-gradient(90deg,transparent 40%,#000 80%)}}
#k{{position:absolute;left:80px;top:74px;font-size:50px;color:#06141B;background:{yel};padding:8px 30px 14px;border-radius:999px;letter-spacing:-1px;
  box-shadow:0 8px 0 rgba(0,0,0,.35)}}
#t1{{position:absolute;left:66px;top:160px;font-size:{t.get('size1', 196)}px;line-height:1;color:#fff;letter-spacing:-8px;white-space:nowrap;
  text-shadow:0 10px 0 #021015,0 0 50px rgba(34,211,238,.55)}}
#t2{{position:absolute;left:62px;top:{t.get('top2', 400)}px;padding:6px 30px 18px;background:{yel};border-radius:18px;transform:rotate(-2deg);
  box-shadow:0 12px 0 #021015}}
#t2 span{{font-size:{t.get('size2', 118)}px;color:#06141B;letter-spacing:-6px;white-space:nowrap}}
#t3{{position:absolute;left:70px;top:{t.get('top3', 670)}px;font-size:{t.get('size3', 124)}px;color:#fff;letter-spacing:-6px;white-space:nowrap;
  text-shadow:0 10px 0 #021015}}
#vf{{position:absolute;left:1190px;top:110px;width:640px;height:600px}}
.cn{{position:absolute;width:110px;height:110px;border:14px solid #fff;filter:drop-shadow(0 0 18px rgba(255,255,255,.6))}}
.tl{{left:0;top:0;border-right:none;border-bottom:none;border-radius:28px 0 0 0}}
.tr{{right:0;top:0;border-left:none;border-bottom:none;border-radius:0 28px 0 0}}
.bl{{left:0;bottom:0;border-right:none;border-top:none;border-radius:0 0 0 28px}}
.br{{right:0;bottom:0;border-left:none;border-top:none;border-radius:0 0 28px 0}}
#scr{{position:absolute;left:70px;top:80px;width:500px;height:440px;border-radius:24px;background:rgba(4,30,38,.92);border:5px solid {sky};
  box-shadow:0 0 50px rgba(34,211,238,.6)}}
#scr .bar{{height:46px;border-bottom:4px solid rgba(34,211,238,.4);display:flex;gap:12px;align-items:center;padding-left:20px}}
#scr .bar i{{width:16px;height:16px;border-radius:8px;background:#5d7f8a}}
#scr .bar i:first-child{{background:{yel}}}
.tile{{position:absolute;top:80px;width:130px;height:130px;border-radius:18px;background:#0B3340;border:4px solid #1f5866}}
.tile u{{position:absolute;left:30px;top:30px;width:70px;height:70px;border-radius:14px}}
.ln{{position:absolute;left:30px;height:22px;border-radius:11px;background:#1f5866}}
#btn{{position:absolute;left:250px;top:350px;width:210px;height:62px;border-radius:31px;background:{yel};color:#06141B;font-size:34px;
  display:flex;align-items:center;justify-content:center;letter-spacing:-1px}}
#focus{{position:absolute;left:231px;top:135px;width:180px;height:180px;border:7px solid {yel};border-radius:10px;box-shadow:0 0 30px {yel}}}
#focus:after{{content:"";position:absolute;left:50%;top:50%;width:30px;height:30px;margin:-15px 0 0 -15px;border:5px solid {yel};border-radius:50%}}
#xh{{position:absolute;left:0;right:0;top:225px;height:3px;background:rgba(255,255,255,.35)}}
#xv{{position:absolute;top:0;bottom:0;left:321px;width:3px;background:rgba(255,255,255,.35)}}
#rec{{position:absolute;right:40px;top:30px;font-size:34px;color:#fff;letter-spacing:1px}}
#rec:before{{content:"";display:inline-block;width:22px;height:22px;border-radius:11px;background:#FF5A5A;margin-right:12px;vertical-align:2px;box-shadow:0 0 16px #FF5A5A}}
#cur{{position:absolute;left:1682px;top:584px;width:110px;height:140px;filter:drop-shadow(0 10px 0 #021015)}}
#pr{{position:absolute;left:1240px;top:770px;padding:20px 40px 26px;background:#fff;border-radius:24px;transform:rotate(-4deg);
  box-shadow:0 14px 0 #021015;border:6px solid #06141B}}
#pr:before{{content:"";position:absolute;left:-26px;top:50%;width:30px;height:30px;margin-top:-15px;border-radius:50%;background:#06343F;border:6px solid #06141B}}
#pr .pl{{font-size:36px;color:#3d5560;letter-spacing:-1px}}
#pr .pv{{font-size:110px;line-height:1.05;color:#06141B;letter-spacing:-4px;white-space:nowrap}}
#pr s{{color:#8aa0a8;text-decoration-thickness:10px;text-decoration-color:#FF5A5A}}
#pr b{{margin:0 20px;color:#0E6E86}}
#pr em{{font-style:normal;color:#0E7490}}
</style></head><body><div id="bg"></div><div id="au"></div><div id="dots"></div>
<div id="vf">
  <div id="scr"><div class="bar"><i></i><i></i><i></i></div>
    <div class="tile" style="left:30px"><u style="background:{sky}"></u></div>
    <div class="tile" style="left:186px;border-color:{yel}"><u style="background:{yel};border-radius:50%"></u></div>
    <div class="tile" style="left:342px"><u style="background:#7DD3C0"></u></div>
    <div class="ln" style="top:250px;width:300px"></div><div class="ln" style="top:292px;width:200px"></div>
    <div id="btn">정보 갱신</div>
  </div>
  <div id="focus"></div><div id="xh"></div><div id="xv"></div><div id="rec">AI 보는 중</div>
  <div class="cn tl"></div><div class="cn tr"></div><div class="cn bl"></div><div class="cn br"></div>
</div>
<svg id="cur" viewBox="0 0 80 100"><path d="M6 4 L6 78 L26 60 L40 92 L54 86 L40 54 L68 54 Z" fill="{yel}" stroke="#06141B" stroke-width="5"/></svg>
{price}
<div id="k">{esc(t.get('badge', ''))}</div>
<div id="t1">{esc(t.get('line1', ''))}</div>
<div id="t2"><span>{_mk(t.get('line2', ''), '#0E7490')}</span></div>
<div id="t3">{_mk(t.get('line3', ''), sky)}</div>
<script>for(const id of ['t1','t3']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1170&&f>70){{f-=6;e.style.fontSize=f+'px'}}}}
{{const e=document.querySelector('#t2 span');let f=parseFloat(getComputedStyle(e).fontSize);while(document.getElementById('t2').getBoundingClientRect().right>1170&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
