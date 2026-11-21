"""layout: odometer (2026-11-21 쇼츠 '클로드 10만까지 세기')
검붉은 바탕 + 아래쪽 큰 기계식 숫자 계기판(칸마다 숫자, 마지막 칸은 굴러가는 중) + 계기판 위에 붉은 화난 눈 두 개(AI의 '복수' 농담)
+ 큰 제목. 세로·가로 모두. 기존 모양(…bell·fineprint)과 겹치지 않게 '주행거리계 숫자판'.
대본: thumbnail: {layout: odometer, badge, line1, line2("[[강조]]"), digits: "099999", color, color2}
"""
import html as _h
import re


def _mk(s):
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', _h.escape(s or ""))


def page(t, fonts_uri, W, H):
    acc, acc2 = t.get("color", "#F43F5E"), t.get("color2", "#FDE047")
    v = H > W
    s = W / 1080 if v else H / 1080
    px = lambda n: f"{n * s:.0f}px"
    dg = t.get("digits", "099999")
    cell = 150 if v else 190
    cells = "".join(f'<div class="c{" roll" if i == len(dg) - 1 else ""}"><span>{_h.escape(d)}</span>{"<em>0</em>" if i == len(dg) - 1 else ""}</div>' for i, d in enumerate(dg))
    od_t = px(1180) if v else px(700)
    eyes_t = px(860) if v else px(520)
    tl, tt = (px(70), px(180)) if v else (px(90), px(150))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#13070B}}
#bg{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 72%,#5A1020 0%,#2A0A12 45%,#13070B 80%)}}
#od{{position:absolute;left:50%;top:{od_t};transform:translateX(-50%);display:flex;gap:{px(14)};padding:{px(26)};background:#1C1C22;border-radius:{px(30)};border:{px(8)} solid #3A3A44;box-shadow:0 0 {px(80)} rgba(244,63,94,.45)}}
.c{{position:relative;width:{px(cell)};height:{px(cell * 1.45)};overflow:hidden;border-radius:{px(14)};background:linear-gradient(180deg,#0A0A0C,#26262E 50%,#0A0A0C);display:flex;align-items:center;justify-content:center;font-size:{px(cell * 1.05)};color:#F5F5F7}}
.c.roll span{{transform:translateY(-38%);color:{acc2}}} .c.roll em{{position:absolute;font-style:normal;transform:translateY(62%);color:{acc2}}}
.c:after{{content:'';position:absolute;left:0;right:0;top:50%;height:{px(3)};background:rgba(0,0,0,.6)}}
#eyes{{position:absolute;left:50%;top:{eyes_t};transform:translateX(-50%);display:flex;gap:{px(150)}}}
#eyes i{{display:block;width:{px(170)};height:{px(80)};background:{acc};box-shadow:0 0 {px(60)} {acc};border-radius:50% 50% 50% 50% / 0 0 100% 100%}}
#eyes i:first-child{{transform:rotate(14deg)}} #eyes i:last-child{{transform:rotate(-14deg)}}
#k{{position:absolute;left:{tl};top:calc({tt} - {px(90)});font-size:{px(44)};color:#13070B;background:{acc2};padding:{px(6)} {px(26)} {px(12)};border-radius:{px(12)}}}
#t1{{position:absolute;left:{tl};top:{tt};font-size:{px(92 if v else 100)};color:#fff;letter-spacing:-4px;white-space:nowrap;text-shadow:0 {px(8)} 0 #000}}
#t2{{position:absolute;left:{tl};top:calc({tt} + {px(125)});font-size:{px(170 if v else 160)};color:#fff;letter-spacing:-7px;white-space:nowrap;text-shadow:0 {px(10)} 0 #000}}
.hl{{color:{acc}}}
</style></head><body><div id="bg"></div><div id="eyes"><i></i><i></i></div><div id="od">{cells}</div>
<div id="k">{_h.escape(t.get('badge', ''))}</div><div id="t1">{_mk(t.get('line1', ''))}</div><div id="t2">{_mk(t.get('line2', ''))}</div>
</body></html>"""
