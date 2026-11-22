"""layout: neonsign (2026-11-22 롱폼 '제미나이 4 네온')
먹색 벽돌 벽 + 오른쪽에 빛나는 네온관 글자 간판(word, 테두리만 빛나는 글자) + 그 아래 세 칸 사다리(형제 모델, 가운데 칸만 켜짐)
+ 왼쪽 큰 제목 세 줄. 가로·세로 모두. 기존 모양(…bell·fineprint·odometer·silence)과 겹치지 않게 '네온 간판 + 사다리'.
실제 회사 로고는 쓰지 않는다(글자만).
대본: thumbnail: {layout: neonsign, badge, word: "NEON", line1, line2("[[강조]]"), line3, steps: ["카본","네온","하이드로젠"], color, color2}
"""
import html as _h
import re


def _mk(s):
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', _h.escape(s or ""))


def page(t, fonts_uri, W, H):
    acc, acc2 = t.get("color", "#00E5FF"), t.get("color2", "#FF7AE0")
    v = H > W
    s = W / 1080 if v else H / 1080
    px = lambda n: f"{n * s:.0f}px"
    word = _h.escape(t.get("word", "NEON"))
    steps = t.get("steps", ["카본", "네온", "하이드로젠"])
    on = 1 if len(steps) > 1 else 0
    cells = "".join(f'<div class="st{" on" if i == on else ""}">{_h.escape(x)}</div>' for i, x in enumerate(steps))
    sign_l, sign_t = ("50%", px(1000)) if v else ("74%", px(700))
    lad_t = px(1330) if v else px(900)
    tl, tt = (px(70), px(200)) if v else (px(80), px(260))
    bricks = "".join(f'<i style="left:{(c * 220 + (r % 2) * 110) * s:.0f}px;top:{r * 74 * s:.0f}px"></i>' for r in range(int(H / (74 * s)) + 1) for c in range(-1, int(W / (220 * s)) + 2))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#060A14}}
#wall i{{position:absolute;width:{px(212)};height:{px(66)};border-radius:{px(6)};background:#0D1322}}
#glow{{position:absolute;inset:0;background:radial-gradient(ellipse at {sign_l} {'55%' if v else '42%'},rgba(0,229,255,.28) 0%,rgba(255,122,224,.10) 35%,rgba(6,10,20,.85) 70%)}}
#sign{{position:absolute;left:{sign_l};top:{sign_t};transform:translate(-50%,-50%) rotate(-4deg);font-size:{px(250 if v else 230)};letter-spacing:{px(10)};color:transparent;-webkit-text-stroke:{px(9)} #E9FDFF;
  text-shadow:0 0 {px(12)} {acc},0 0 {px(40)} {acc},0 0 {px(90)} {acc};filter:drop-shadow(0 0 {px(18)} {acc})}}
#lad{{position:absolute;left:{sign_l};top:{lad_t};transform:translateX(-50%);display:flex;gap:{px(18)}}}
.st{{white-space:nowrap;padding:{px(14)} {px(30)} {px(20)};border-radius:{px(18)};border:{px(4)} solid #2A3550;color:#5D6B8A;font-size:{px(46)};background:rgba(6,10,20,.8)}}
.st.on{{border-color:{acc2};color:#fff;box-shadow:0 0 {px(30)} {acc2},inset 0 0 {px(20)} rgba(255,122,224,.35)}}
#k{{position:absolute;left:{tl};top:calc({tt} - {px(92)});font-size:{px(44)};color:#060A14;background:{acc};padding:{px(6)} {px(26)} {px(12)};border-radius:{px(12)}}}
#t1{{position:absolute;left:{tl};top:{tt};font-size:{px(96)};color:#fff;letter-spacing:-4px;white-space:nowrap;text-shadow:0 {px(8)} 0 #000}}
#t2{{position:absolute;left:{tl};top:calc({tt} + {px(125)});font-size:{px(150 if v else 175)};color:#fff;letter-spacing:-6px;white-space:nowrap;text-shadow:0 {px(10)} 0 #000}}
#t3{{position:absolute;left:{tl};top:calc({tt} + {px(310 if v else 340)});font-size:{px(58)};color:{acc2};letter-spacing:-2px;white-space:nowrap;text-shadow:0 {px(6)} 0 #000}}
.hl{{color:{acc}}}
</style></head><body><div id="wall">{bricks}</div><div id="glow"></div><div id="sign">{word}</div><div id="lad">{cells}</div>
<div id="k">{_h.escape(t.get('badge', ''))}</div><div id="t1">{_mk(t.get('line1', ''))}</div><div id="t2">{_mk(t.get('line2', ''))}</div><div id="t3">{_mk(t.get('line3', ''))}</div>
</body></html>"""
