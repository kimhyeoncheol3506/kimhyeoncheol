"""layout: silence (2026-11-21 쇼츠 '피클 AI 전화 13초 침묵')
먹빛 초록 바탕 + 가운데 큰 통화 타이머(00:13) + 그 아래 납작하게 멈춘 음성 파형(가운데만 일직선) + 빨간 '통화 종료' 동그라미
+ 큰 제목. 세로·가로 모두. 기존 'phone' 모양(휴대폰 틀)과 겹치지 않게 틀 없이 '타이머 + 끊긴 파형'만.
대본: thumbnail: {layout: silence, badge, line1, line2("[[강조]]"), line3, timer: "00:13", color, color2}
"""
import html as _h
import re


def _mk(s):
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', _h.escape(s or ""))


def page(t, fonts_uri, W, H):
    acc, acc2 = t.get("color", "#4ADE80"), t.get("color2", "#FCA5A5")
    v = H > W
    s = W / 1080 if v else H / 1080
    px = lambda n: f"{n * s:.0f}px"
    n = 34
    bars = "".join(f'<i style="height:{px(6 if 9 <= i <= 26 else 30 + (i * 37) % 120)}"></i>' for i in range(n))
    tl, tt = (px(70), px(180)) if v else (px(90), px(150))
    tm_t, wv_t, end_t = (px(820), px(1180), px(1420)) if v else (px(280), px(660), px(780))
    cx = "50%" if v else "72%"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#07130C}}
#bg{{position:absolute;inset:0;background:radial-gradient(ellipse at {cx} 60%,#123D22 0%,#0A2014 45%,#07130C 80%)}}
#tm{{position:absolute;left:{cx};top:{tm_t};transform:translateX(-50%);font-size:{px(250)};color:#fff;letter-spacing:-6px;text-shadow:0 0 {px(50)} rgba(74,222,128,.5)}}
#wv{{position:absolute;left:{cx};top:{wv_t};transform:translate(-50%,-50%);display:flex;align-items:center;gap:{px(10)}}}
#wv i{{display:block;width:{px(14)};border-radius:{px(7)};background:{acc}}}
#end{{position:absolute;left:{cx};top:{end_t};transform:translateX(-50%);width:{px(180)};height:{px(180)};border-radius:50%;background:#EF4444;display:flex;align-items:center;justify-content:center;font-size:{px(90)};box-shadow:0 0 {px(60)} rgba(239,68,68,.6)}}
#k{{position:absolute;left:{tl};top:calc({tt} - {px(90)});font-size:{px(44)};color:#07130C;background:{acc};padding:{px(6)} {px(26)} {px(12)};border-radius:{px(12)}}}
#t1{{position:absolute;left:{tl};top:{tt};font-size:{px(92 if v else 100)};color:#fff;letter-spacing:-4px;white-space:nowrap;text-shadow:0 {px(8)} 0 #000}}
#t2{{position:absolute;left:{tl};top:calc({tt} + {px(125)});font-size:{px(170 if v else 160)};color:#fff;letter-spacing:-7px;white-space:nowrap;text-shadow:0 {px(10)} 0 #000}}
#t3{{position:absolute;left:{tl};top:calc({tt} + {px(330)});font-size:{px(80)};color:{acc2};letter-spacing:-3px;white-space:nowrap;text-shadow:0 {px(6)} 0 #000}}
.hl{{color:{acc}}}
</style></head><body><div id="bg"></div><div id="tm">{_h.escape(t.get('timer', '00:13'))}</div><div id="wv">{bars}</div><div id="end">📞</div>
<div id="k">{_h.escape(t.get('badge', ''))}</div><div id="t1">{_mk(t.get('line1', ''))}</div><div id="t2">{_mk(t.get('line2', ''))}</div><div id="t3">{_mk(t.get('line3', ''))}</div>
</body></html>"""
