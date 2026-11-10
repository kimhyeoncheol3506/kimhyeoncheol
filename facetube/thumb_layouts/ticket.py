"""layout: ticket (2026-11-10 일꾼C, '클로드 듀엣' 썸네일)
밝은 흰·은빛 바탕(옅은 사선 줄무늬) + 왼쪽 아주 큰 검정 제목 + 빨간 띠 둘째 줄 + 셋째 줄 [[빨강 강조]]
+ 오른쪽 살짝 기울어진 '승인 요청' 영수증 카드(줄마다 상태 알약, '금지' 줄은 빨간 줄긋기) + 빨간 둥근 도장.
기존 모양(default·tiles·versus·badge·phone·calendar·film)과 겹치지 않게: 크림·파랑·노을이 아닌 은색, 폰·달력·필름이 아닌 영수증.
대본:
  thumbnail:
    layout: ticket
    badge: "작은 검정 꼬리표"
    line1: "큰 제목"
    line2: "빨간 띠 글자"
    line3: "셋째 줄 [[강조]]"
    ticket_title: "승인 요청"
    ticket_rows: [["보내기", "승인 필요"], ["결제하기", "승인 필요"], ["계좌 이체", "금지"]]   # 상태가 '금지'면 빨간 줄긋기
    stamp: "금지선"          # 선택(기본 '금지선')
    color: "#E8344E"         # 선택(빨강 포인트)
"""
import html as _h
import re


def _mk(s, acc):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{acc}">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    acc = t.get("color", "#E8344E")
    rows = t.get("ticket_rows") or [["보내기", "승인 필요"], ["결제하기", "승인 필요"], ["계좌 이체", "금지"]]
    rh = []
    for k, v in rows:
        ban = "금지" in v
        rh.append(f'<div class="row{" ban" if ban else ""}"><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif}}
#bg{{position:absolute;inset:0;background:linear-gradient(135deg,#FFFFFF 0%,#EEF0F5 45%,#D9DDE6 100%)}}
#st{{position:absolute;inset:0;opacity:.55;background:repeating-linear-gradient(135deg,transparent 0 46px,rgba(170,176,192,.18) 46px 52px)}}
#sh{{position:absolute;right:-200px;top:-260px;width:1100px;height:1100px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.95),rgba(255,255,255,0) 65%)}}
#k{{position:absolute;left:80px;top:72px;font-size:58px;color:#fff;background:#14161C;padding:10px 32px 16px;border-radius:16px;letter-spacing:-2px}}
#k i{{display:inline-block;width:22px;height:22px;border-radius:11px;background:{acc};margin-right:16px;vertical-align:6px;font-style:normal}}
#t1{{position:absolute;left:66px;top:170px;font-size:{t.get('size1', 236)}px;line-height:.95;color:#14161C;letter-spacing:-12px;white-space:nowrap;
  text-shadow:0 8px 0 rgba(20,22,28,.08)}}
#band{{position:absolute;left:58px;top:{t.get('top2', 432)}px;padding:6px 38px 18px;background:{acc};transform:rotate(-2deg);box-shadow:12px 12px 0 #14161C}}
#band span{{font-size:{t.get('size2', 124)}px;color:#fff;letter-spacing:-6px;white-space:nowrap}}
#t3{{position:absolute;left:70px;top:{t.get('top3', 660)}px;font-size:{t.get('size3', 128)}px;color:#14161C;letter-spacing:-7px;white-space:nowrap}}
#tk{{position:absolute;left:1250px;top:120px;width:560px;padding:44px 40px 60px;background:#fff;border-radius:22px;transform:rotate(5deg);
  box-shadow:0 30px 60px rgba(40,46,60,.28),0 0 0 6px #14161C;box-sizing:border-box}}
#tk:after{{content:"";position:absolute;left:0;right:0;bottom:-26px;height:30px;
  background:radial-gradient(circle at 20px 0,transparent 18px,#fff 19px) repeat-x;background-size:40px 30px}}
#tk h1{{margin:0 0 26px;font-size:62px;color:#14161C;letter-spacing:-2px;font-weight:900}}
#tk h1 b{{display:inline-block;width:56px;height:56px;border-radius:28px;background:{acc};color:#fff;font-size:40px;text-align:center;line-height:56px;margin-right:16px;vertical-align:6px}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:24px 0;border-top:4px dashed #C9CED9}}
.k{{font-size:52px;color:#14161C;letter-spacing:-2px}}
.v{{font-size:38px;color:#fff;background:#4A5163;border-radius:30px;padding:6px 22px 10px}}
.ban .k{{color:{acc};text-decoration:line-through;text-decoration-thickness:8px}}
.ban .v{{background:{acc}}}
#btn{{margin-top:30px;display:flex;gap:18px}}
#btn div{{flex:1;text-align:center;font-size:42px;padding:16px 0 20px;border-radius:40px}}
#ok{{background:#14161C;color:#fff}} #no{{border:4px solid #14161C;color:#14161C}}
#sp{{position:absolute;left:1075px;top:720px;width:270px;height:270px;border-radius:50%;border:12px solid {acc};color:{acc};display:flex;align-items:center;
  justify-content:center;transform:rotate(-16deg);font-size:72px;letter-spacing:-3px;background:rgba(255,255,255,.75);box-shadow:inset 0 0 0 6px rgba(232,52,78,.25)}}
</style></head><body><div id="bg"></div><div id="st"></div><div id="sh"></div>
<div id="tk"><h1><b>✋</b>{esc(t.get('ticket_title', '승인 요청'))}</h1>{''.join(rh)}<div id="btn"><div id="ok">승인</div><div id="no">나중에</div></div></div>
<div id="sp">{esc(t.get('stamp', '금지선'))}</div>
<div id="k"><i></i>{esc(t.get('badge', ''))}</div>
<div id="t1">{esc(t.get('line1', ''))}</div>
<div id="band"><span>{esc(t.get('line2', ''))}</span></div>
<div id="t3">{_mk(t.get('line3', ''), acc)}</div>
<script>for(const id of ['t1','t3']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1200&&f>70){{f-=6;e.style.fontSize=f+'px'}}}}
{{const e=document.querySelector('#band span');let f=parseFloat(getComputedStyle(e).fontSize);while(document.getElementById('band').getBoundingClientRect().right>1220&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
