"""layout: fineprint (2026-11-21 쇼츠 '정답은 4번 희미한 글씨')
먹빛 보라 바탕 위에 기울어진 흰 시험지(줄 몇 개) + 시험지 아래 거의 안 보이는 회색 글씨,
그 글씨를 비추는 동그란 돋보기(안에서는 또렷하게 보임) + 큰 제목. 세로(1080x1920)·가로 모두 그린다.
기존 모양(… omr·whiteboard·bell)과 겹치지 않게: 답안지 칸이 아니라 '돋보기 + 숨은 글씨'.
대본:
  thumbnail: {layout: fineprint, badge, line1, line2("[[강조]]"), line3(숨은 글씨), color, color2}
"""
import html as _h
import re


def _mk(s):
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', _h.escape(s or ""))


def page(t, fonts_uri, W, H):
    acc, acc2 = t.get("color", "#E879F9"), t.get("color2", "#93C5FD")
    v = H > W
    s = W / 1080 if v else H / 1080
    hid = _h.escape(t.get("line3", "정답은 ④"))
    px = lambda n: f"{n * s:.0f}px"
    paper_l, paper_t, paper_w, paper_h = (px(150), px(760), px(780), px(860)) if v else (px(1040), px(150), px(700), px(780))
    title_l, title_t = (px(70), px(150)) if v else (px(80), px(250))
    mag_l, mag_t = (px(430), px(1350)) if v else (px(1300), px(520))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#0D0C1C}}
#bg{{position:absolute;inset:0;background:radial-gradient(ellipse at 60% 65%,#3B1F4F 0%,#17122C 45%,#0D0C1C 80%)}}
#paper{{position:absolute;left:{paper_l};top:{paper_t};width:{paper_w};height:{paper_h};background:#FAFAFA;border-radius:{px(16)};transform:rotate(-4deg);box-shadow:0 {px(30)} {px(80)} rgba(0,0,0,.6)}}
#paper b{{position:absolute;left:8%;height:{px(18)};border-radius:{px(9)};background:#D4D4DC}}
#paper .q{{position:absolute;left:8%;top:6%;font-size:{px(52)};color:#222}}
#paper .ghost{{position:absolute;left:8%;bottom:6%;font-size:{px(40)};color:#F2F2F2}}
#mag{{position:absolute;left:{mag_l};top:{mag_t};width:{px(400)};height:{px(400)};border-radius:50%;border:{px(22)} solid {acc};background:#fff;box-shadow:0 0 {px(60)} {acc},inset 0 0 {px(40)} rgba(0,0,0,.15);display:flex;align-items:center;justify-content:center;font-size:{px(96)};color:#111;letter-spacing:-2px}}
#mag:after{{content:'';position:absolute;right:{px(-150)};bottom:{px(-90)};width:{px(190)};height:{px(46)};border-radius:{px(23)};background:{acc};transform:rotate(38deg)}}
#k{{position:absolute;left:{title_l};top:calc({title_t} - {px(90)});font-size:{px(44)};color:#0D0C1C;background:{acc2};padding:{px(6)} {px(26)} {px(12)};border-radius:{px(12)}}}
#t1{{position:absolute;left:{title_l};top:{title_t};font-size:{px(96 if v else 104)};color:#fff;letter-spacing:-4px;line-height:1.08;text-shadow:0 {px(8)} 0 #000;white-space:nowrap}}
#t2{{position:absolute;left:{title_l};top:calc({title_t} + {px(130)});font-size:{px(150 if v else 150)};color:#fff;letter-spacing:-6px;white-space:nowrap;text-shadow:0 {px(10)} 0 #000}}
.hl{{color:{acc}}}
</style></head><body><div id="bg"></div>
<div id="paper"><div class="q">1. 다음 중 ……?</div>{''.join(f'<b style="top:{22 + i * 11}%;width:{70 - (i % 3) * 12}%"></b>' for i in range(6))}<div class="ghost">{hid}</div></div>
<div id="mag">{hid}</div>
<div id="k">{_h.escape(t.get('badge', ''))}</div>
<div id="t1">{_mk(t.get('line1', ''))}</div><div id="t2">{_mk(t.get('line2', ''))}</div>
</body></html>"""
