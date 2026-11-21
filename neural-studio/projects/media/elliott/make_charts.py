"""코스피 엘리엇 파동 차트 3장 (네이버 금융 일봉 종가, 2025-03-04 ~ 2026-11-20). 종이 질감 위 손그림 느낌."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H = os.path.dirname(os.path.abspath(__file__)); NS = os.path.abspath(os.path.join(H, "..", "..", ".."))
D = [r for r in json.load(open(sys.argv[1])) if r[0] >= "20250301"]
FB = lambda s: ImageFont.truetype(os.path.join(NS, "assets", "fonts", "BlackHanSans.ttf"), s)
FP = lambda s: ImageFont.truetype(os.path.join(NS, "assets", "fonts", "Pretendard-Bold.otf"), s)
W, Hh = 1920, 1080; L, R, T, B = 170, 1560, 150, 900; YMIN, YMAX = 1500, 10000
X = lambda i: L + (R - L) * i / (len(D) - 1); Y = lambda v: B - (B - T) * (v - YMIN) / (YMAX - YMIN)
idx = {r[0]: i for i, r in enumerate(D)}
P = {"0": ("20250409", 2293.70), "1": ("20251103", 4221.87), "2": ("20251124", 3846.06), "3": ("20260226", 6307.27),
     "4": ("20260331", 5052.46), "5": ("20260622", 9114.55), "A": ("20260730", 5593.56), "B": ("20260923", 7080.92), "C?": ("20261120", 4869.96)}
INK, RED, BLUE, GOLD, GRAY = (30, 28, 34), (214, 40, 40), (40, 90, 200), (200, 140, 20), (140, 135, 125)

def base(title):
    im = Image.new("RGB", (W, Hh), (247, 242, 230)); d = ImageDraw.Draw(im)
    for v in range(2000, 10001, 1000):
        d.line([(L, Y(v)), (R, Y(v))], fill=(225, 218, 200), width=2); d.text((L - 20, Y(v)), f"{v:,}", font=FP(28), fill=GRAY, anchor="rm")
    for ym in ["202504", "202507", "202510", "202601", "202604", "202607", "202610"]:
        i = next(i for i, r in enumerate(D) if r[0].startswith(ym)); d.line([(X(i), T), (X(i), B)], fill=(232, 226, 210), width=2)
        d.text((X(i), B + 30), f"{ym[2:4]}.{int(ym[4:])}", font=FP(28), fill=GRAY, anchor="mm")
    d.text((W // 2, 70), title, font=FB(64), fill=INK, anchor="mm")
    d.text((R, B + 75), "자료: 네이버 금융 코스피 일봉 종가 · 파동 표시는 채널 해석", font=FP(24), fill=GRAY, anchor="rm")
    return im, d

def price(d, col=INK, w=5, upto=None):
    pts = [(X(i), Y(r[4])) for i, r in enumerate(D) if upto is None or r[0] <= upto]; d.line(pts, fill=col, width=w, joint="curve")

def labels(d, keys):
    for k in keys:
        dt, v = P[k]; x, y = X(idx[dt]), Y(v); up = k in ("1", "3", "5", "B")
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=RED if k[0] in "ABC" else BLUE)
        ty = y - 70 if up else y + 70
        d.ellipse([x - 38, ty - 38, x + 38, ty + 38], fill=(255, 255, 255), outline=RED if k[0] in "ABC" else BLUE, width=6)
        d.text((x, ty), k, font=FB(46), fill=RED if k[0] in "ABC" else BLUE, anchor="mm")
        d.text((x + (60 if k != "C?" else -60), ty), f"{v:,.0f}", font=FP(30), fill=INK, anchor="lm" if k != "C?" else "rm")

# ① 전체 카운트
im, d = base("코스피 엘리엇 파동 카운트 (종가)")
price(d); labels(d, ["0", "1", "2", "3", "4", "5", "A", "B", "C?"])
d.text((X(idx["20251201"]), Y(8600)), "상승 5파", font=FB(54), fill=BLUE, anchor="mm"); d.text((X(idx["20261001"]), Y(8900)), "조정 A-B-C", font=FB(54), fill=RED, anchor="mm")
im.save(os.path.join(H, "wave_count.png"))
# ② 피보나치 되돌림
im, d = base("2,293.70에서 9,114.55까지, 상승분의 피보나치 되돌림")
lo, hi = 2293.70, 9114.55
for f, c in ((0.236, GRAY), (0.382, GRAY), (0.5, GOLD), (0.618, RED), (0.786, GRAY)):
    v = hi - (hi - lo) * f; d.line([(L, Y(v)), (R, Y(v))], fill=c, width=5 if f == 0.618 else 3)
    d.text((R + 10, Y(v)), f"{f * 100:.1f}%  {v:,.0f}", font=FB(34 if f == 0.618 else 28), fill=c, anchor="lm")
price(d); labels(d, ["0", "5", "C?"])
im.save(os.path.join(H, "fib_retrace.png"))
# ③ C파 목표
im, d = base("C파는 어디까지? A파 길이로 재 본 목표")
price(d, upto="20261120"); labels(d, ["5", "A", "B", "C?"])
A = 9114.55 - 5593.56
for f, c, t in ((0.618, RED, "C = A×0.618"), (1.0, GOLD, "C = A×1.0")):
    v = 7080.92 - A * f; d.line([(X(idx["20260923"]), Y(v)), (R + 20, Y(v))], fill=c, width=5)
    d.text((R + 30, Y(v)), f"{t}\n{v:,.0f}", font=FB(34), fill=c, anchor="lm")
d.text((X(idx["20250801"]), Y(8200)), "A파: 9,115에서 5,594까지 3,521포인트", font=FB(40), fill=INK, anchor="lm")
d.text((X(idx["20250801"]), Y(7500)), "61.8% 되돌림 4,899와 거의 같은 자리", font=FB(40), fill=RED, anchor="lm")
im.save(os.path.join(H, "c_target.png"))
print("ok")
