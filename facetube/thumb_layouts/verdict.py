"""layout: verdict (2026-11-25 롱폼 '오퍼스 5.6 루머 팩트체크')
먹색 바탕 + 오른쪽에 크게 기울어진 물음표 숫자(big, 노랑 테두리 글자) + 그 위에 비스듬히 찍힌 빨간 판정 도장(stamp, 이중 테두리)
+ 왼쪽 큰 제목. 가로·세로 모두. 기존 모양(…neonsign)과 겹치지 않게 '큰 숫자 + 판정 도장'. 실제 회사 로고·SNS 화면 없음.
대본: thumbnail: {layout: verdict, badge, big: "5.6?", line1, line2("[[강조]]"), stamp, sub, color, color2}
"""
import html as _h
import re


def _mk(s):
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', _h.escape(s or ""))


def page(t, fonts_uri, W, H):
    acc, red = t.get("color", "#FACC15"), t.get("color2", "#F87171")
    v = H > W
    s = W / 1080 if v else H / 1080
    px = lambda n: f"{n * s:.0f}px"
    bx, by = ("50%", px(1080)) if v else ("74%", px(560))
    tl, tt = (px(70), px(220)) if v else (px(80), px(250))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#0B0B12}}
#bg{{position:absolute;inset:0;background:radial-gradient(ellipse at {bx} {'56%' if v else '52%'},#3A2E08 0%,#17130A 40%,#0B0B12 75%)}}
#dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(250,204,21,.12) {px(2.2)},transparent {px(2.6)});background-size:{px(44)} {px(44)}}}
#big{{position:absolute;left:{bx};top:{by};transform:translate(-50%,-50%) rotate(-6deg);font-size:{px(430 if v else 440)};letter-spacing:-10px;color:transparent;-webkit-text-stroke:{px(12)} {acc};filter:drop-shadow(0 0 {px(30)} rgba(250,204,21,.45))}}
#stamp{{position:absolute;left:{bx};top:{by};transform:translate(-50%,-50%) rotate(-14deg);padding:{px(18)} {px(44)} {px(26)};border:{px(10)} solid {red};outline:{px(4)} solid {red};outline-offset:{px(8)};border-radius:{px(18)};
  color:{red};font-size:{px(92)};white-space:nowrap;background:rgba(11,11,18,.55);text-shadow:0 0 {px(10)} rgba(248,113,113,.5)}}
#k{{position:absolute;left:{tl};top:calc({tt} - {px(92)});font-size:{px(44)};color:#0B0B12;background:{acc};padding:{px(6)} {px(26)} {px(12)};border-radius:{px(12)}}}
#t1{{position:absolute;left:{tl};top:{tt};font-size:{px(92 if v else 100)};color:#fff;letter-spacing:-4px;white-space:nowrap;text-shadow:0 {px(8)} 0 #000}}
#t2{{position:absolute;left:{tl};top:calc({tt} + {px(125)});font-size:{px(150 if v else 165)};color:#fff;letter-spacing:-6px;white-space:nowrap;text-shadow:0 {px(10)} 0 #000}}
#sub{{position:absolute;left:{tl};top:calc({tt} + {px(330)});font-size:{px(50)};color:#C9C9D6;white-space:nowrap}}
.hl{{color:{acc}}}
</style></head><body><div id="bg"></div><div id="dots"></div><div id="big">{_h.escape(t.get('big', '?'))}</div><div id="stamp">{_h.escape(t.get('stamp', ''))}</div>
<div id="k">{_h.escape(t.get('badge', ''))}</div><div id="t1">{_mk(t.get('line1', ''))}</div><div id="t2">{_mk(t.get('line2', ''))}</div><div id="sub">{_mk(t.get('sub', ''))}</div>
</body></html>"""
