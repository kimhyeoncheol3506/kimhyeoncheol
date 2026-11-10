"""layout: board (2026-11-10 일꾼D, '클로드 페이블 5.2' 썸네일)
짙은 남보라 바탕 + 아래쪽 원근 네온 격자 + 왼쪽 아주 큰 흰 제목 + 하늘색 형광 상자 둘째 줄 + 셋째 줄 [[분홍 강조]]
+ 오른쪽 살짝 기울어진 네온 '점수판'(가로 막대 순위표, 1위 줄은 분홍 막대·왕관 알약) + 분홍 물음표 스티커.
기존 모양(default·tiles·versus·badge·phone·calendar·film·ticket·orbit·shield)과 겹치지 않게: 밝은 바탕·폰·달력·필름·영수증·궤도·방패가 아닌 순위 점수판.
대본:
  thumbnail:
    layout: board
    badge: "작은 꼬리표"
    line1: "큰 제목"
    line2: "하늘색 상자 글자"
    line3: "셋째 줄 [[강조]]"
    board_title: "점수판 제목"
    board_rows: [["페이블 5.2", 49.1], ["오퍼스 5.5", 45.5], ["페이블 5.1", 32.4]]   # 첫 줄 = 1위(분홍)
    board_unit: "%"          # 선택
    sticker: "?"             # 선택
    color: "#FF5C8A"         # 선택(분홍)  · color2: "#A0E7FF"(하늘)
"""
import html as _h
import re


def _mk(s, acc):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{acc}">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    acc = t.get("color", "#FF5C8A")
    sky = t.get("color2", "#A0E7FF")
    unit = t.get("board_unit", "%")
    rows = t.get("board_rows") or [["A", 50], ["B", 40], ["C", 30]]
    mx = max(float(v) for _, v in rows) or 1
    rh = []
    for i, (k, v) in enumerate(rows):
        w = 30 + 70 * float(v) / mx
        top = i == 0
        crown = '<em>1위</em>' if top else ''
        rh.append(f'<div class="row{" top" if top else ""}"><div class="k">{esc(str(k))}{crown}</div>'
                  f'<div class="bar"><i style="width:{w:.1f}%"></i><b>{esc(str(v))}{esc(unit)}</b></div></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#120C1E}}
#bg{{position:absolute;inset:0;background:radial-gradient(circle at 72% 30%,#3A1F5C 0%,#1C1236 38%,#120C1E 75%)}}
#gl{{position:absolute;left:-200px;right:-200px;bottom:-40px;height:470px;transform:perspective(520px) rotateX(58deg);transform-origin:50% 100%;
  background-image:linear-gradient(rgba(160,231,255,.32) 2px,transparent 2px),linear-gradient(90deg,rgba(160,231,255,.32) 2px,transparent 2px);
  background-size:96px 96px;-webkit-mask-image:linear-gradient(transparent,#000 60%)}}
#glow{{position:absolute;left:0;right:0;top:600px;height:6px;background:linear-gradient(90deg,transparent,{acc} 30%,#fff 50%,{acc} 70%,transparent);
  box-shadow:0 0 40px {acc},0 0 90px {acc};opacity:.75}}
#k{{position:absolute;left:84px;top:78px;font-size:52px;color:#120C1E;background:{sky};padding:8px 30px 14px;border-radius:999px;letter-spacing:-1px}}
#t1{{position:absolute;left:70px;top:168px;font-size:{t.get('size1', 230)}px;line-height:1;color:#fff;letter-spacing:-10px;white-space:nowrap;
  text-shadow:0 0 50px rgba(255,92,138,.45),0 10px 0 #000}}
#box{{position:absolute;left:66px;top:{t.get('top2', 438)}px;padding:4px 34px 16px;border:8px solid {sky};border-radius:22px;background:rgba(160,231,255,.12);
  box-shadow:0 0 40px rgba(160,231,255,.55),inset 0 0 30px rgba(160,231,255,.25)}}
#box span{{font-size:{t.get('size2', 128)}px;color:{sky};letter-spacing:-6px;white-space:nowrap;text-shadow:0 0 24px rgba(160,231,255,.8)}}
#t3{{position:absolute;left:74px;top:{t.get('top3', 690)}px;font-size:{t.get('size3', 120)}px;color:#fff;letter-spacing:-6px;white-space:nowrap;
  text-shadow:0 8px 0 #000,0 0 40px rgba(255,92,138,.5)}}
#bd{{position:absolute;left:1180px;top:150px;width:650px;padding:40px 40px 46px;border-radius:30px;background:rgba(20,12,40,.92);
  border:5px solid {acc};box-shadow:0 0 60px rgba(255,92,138,.55),0 30px 60px rgba(0,0,0,.6);transform:rotate(3deg);box-sizing:border-box}}
#bd h1{{margin:0 0 26px;font-size:54px;color:#fff;font-weight:900;letter-spacing:-2px}}
#bd h1:before{{content:"";display:inline-block;width:20px;height:20px;border-radius:10px;background:{acc};margin-right:16px;vertical-align:8px;box-shadow:0 0 20px {acc}}}
.row{{margin:22px 0 0}}
.k{{font-size:44px;color:#C9C3E3;letter-spacing:-1px;margin-bottom:8px}}
.k em{{font-style:normal;font-size:30px;color:#120C1E;background:#FFD27A;border-radius:999px;padding:2px 16px 6px;margin-left:16px;vertical-align:8px}}
.bar{{position:relative;height:66px;border-radius:18px;background:rgba(255,255,255,.07)}}
.bar i{{position:absolute;left:0;top:0;bottom:0;border-radius:18px;background:#5B5480}}
.bar b{{position:absolute;right:18px;top:4px;font-size:46px;color:#fff;font-weight:900}}
.top .k{{color:#fff}}
.top .bar i{{background:linear-gradient(90deg,{acc},#FF9DBA);box-shadow:0 0 30px {acc}}}
#st{{position:absolute;left:1000px;top:640px;width:250px;height:250px;border-radius:50%;background:{acc};color:#fff;display:flex;align-items:center;
  justify-content:center;font-size:200px;transform:rotate(-12deg);box-shadow:0 0 0 10px #120C1E,0 0 60px {acc};line-height:1;padding-bottom:16px;box-sizing:border-box}}
</style></head><body><div id="bg"></div><div id="gl"></div><div id="glow"></div>
<div id="bd"><h1>{esc(t.get('board_title', '점수판'))}</h1>{''.join(rh)}</div>
<div id="st">{esc(t.get('sticker', '?'))}</div>
<div id="k">{esc(t.get('badge', ''))}</div>
<div id="t1">{esc(t.get('line1', ''))}</div>
<div id="box"><span>{esc(t.get('line2', ''))}</span></div>
<div id="t3">{_mk(t.get('line3', ''), acc)}</div>
<script>for(const id of ['t1','t3']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1150&&f>70){{f-=6;e.style.fontSize=f+'px'}}}}
{{const e=document.querySelector('#box span');let f=parseFloat(getComputedStyle(e).fontSize);while(document.getElementById('box').getBoundingClientRect().right>1150&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
