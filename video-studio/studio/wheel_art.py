"""12달 피자판(원형 달력) 그림 (v1.14.0, 2027 경제대예측 편). 이코노미스트 표지를 베끼지 않고 우리가 직접 그린 소품 12개.

scene_art.compose_scene의 props에 ("wheel", {...}) ("slice", {...}) ("badge", {...}) 로 쓴다. 좌표는 1920x1080 기준.
"""
import math

from PIL import ImageDraw  # noqa: F401

from .draw import font
from .scene_art import INK, K, _rocket, _s

RED, BLUE, CREAM = (214, 76, 76), (112, 168, 214), (252, 246, 232)
ICONS = {1: "fist", 2: "ship", 3: "robot", 4: "rocket", 5: "virus", 6: "thermo", 7: "faucet", 8: "flame", 9: "passport", 10: "chart", 11: "crowd", 12: "cake"}
MONTH_KO = {1: "1월", 2: "2월", 3: "3월", 4: "4월", 5: "5월", 6: "6월", 7: "7월", 8: "8월", 9: "9월", 10: "10월", 11: "11월", 12: "12월"}


def _e(d, x, y, rx, ry, **kw):
    d.ellipse([_s(x - rx), _s(y - ry), _s(x + rx), _s(y + ry)], **kw)


def icon(d, kind, cx, cy, s=1.0):
    w = _s(5)
    if kind == "fist":
        d.line([_s(cx - 30 * s), _s(cy + 120 * s), _s(cx - 30 * s), _s(cy + 40 * s)], fill=INK, width=_s(60 * s))
        d.rounded_rectangle([_s(cx - 70 * s), _s(cy - 60 * s), _s(cx + 70 * s), _s(cy + 60 * s)], radius=_s(30 * s), fill=BLUE, outline=INK, width=w)
        for i in range(3):
            d.line([_s(cx - 40 * s + i * 40 * s), _s(cy - 56 * s), _s(cx - 40 * s + i * 40 * s), _s(cy - 6 * s)], fill=INK, width=_s(4))
        d.rectangle([_s(cx - 50 * s), _s(cy + 60 * s), _s(cx + 50 * s), _s(cy + 140 * s)], fill=BLUE, outline=INK, width=w)
        for dx, dy in ((-90, 150), (-130, 100), (100, 150)):
            _e(d, cx + dx * s, cy + dy * s, 26 * s, 16 * s, outline=INK, width=_s(6))
    elif kind == "ship":
        for i, col in enumerate(((214, 76, 76), (112, 168, 214), (240, 190, 80), (96, 170, 120))):
            d.rectangle([_s(cx - 110 * s + i * 56 * s), _s(cy - 60 * s), _s(cx - 60 * s + i * 56 * s), _s(cy - 10 * s)], fill=col, outline=INK, width=_s(3))
            d.rectangle([_s(cx - 110 * s + i * 56 * s), _s(cy - 110 * s), _s(cx - 60 * s + i * 56 * s), _s(cy - 60 * s)], fill=col, outline=INK, width=_s(3))
        d.polygon([(_s(cx - 150 * s), _s(cy - 10 * s)), (_s(cx + 150 * s), _s(cy - 10 * s)), (_s(cx + 110 * s), _s(cy + 50 * s)), (_s(cx - 120 * s), _s(cy + 50 * s))], fill=(60, 70, 90), outline=INK)
        for i in range(4):
            d.arc([_s(cx - 170 * s + i * 90 * s), _s(cy + 30 * s), _s(cx - 90 * s + i * 90 * s), _s(cy + 90 * s)], 180, 360, fill=BLUE, width=_s(8))
    elif kind == "robot":
        d.rounded_rectangle([_s(cx - 70 * s), _s(cy - 90 * s), _s(cx + 70 * s), _s(cy + 10 * s)], radius=_s(24 * s), fill=(224, 228, 238), outline=INK, width=w)
        _e(d, cx - 28 * s, cy - 40 * s, 14 * s, 14 * s, fill=INK)
        _e(d, cx + 28 * s, cy - 40 * s, 14 * s, 14 * s, fill=INK)
        d.line([_s(cx), _s(cy - 90 * s), _s(cx), _s(cy - 125 * s)], fill=INK, width=_s(6))
        _e(d, cx, cy - 130 * s, 10 * s, 10 * s, fill=RED)
        d.rounded_rectangle([_s(cx - 50 * s), _s(cy + 14 * s), _s(cx + 50 * s), _s(cy + 110 * s)], radius=_s(16 * s), fill=(224, 228, 238), outline=INK, width=w)
        d.rounded_rectangle([_s(cx + 40 * s), _s(cy + 40 * s), _s(cx + 120 * s), _s(cy + 100 * s)], radius=_s(8 * s), fill=(60, 70, 100), outline=INK, width=_s(4))
    elif kind == "rocket":
        _rocket(d, cx, cy, 0.9 * s)
    elif kind == "virus":
        for k in range(12):
            a = math.radians(k * 30)
            d.line([_s(cx + 70 * s * math.cos(a)), _s(cy + 70 * s * math.sin(a)), _s(cx + 110 * s * math.cos(a)), _s(cy + 110 * s * math.sin(a))], fill=INK, width=_s(8))
            _e(d, cx + 112 * s * math.cos(a), cy + 112 * s * math.sin(a), 11 * s, 11 * s, fill=RED, outline=INK, width=_s(3))
        _e(d, cx, cy, 78 * s, 78 * s, fill=RED, outline=INK, width=w)
        for dx, dy in ((-24, -20), (22, 10), (-8, 30)):
            _e(d, cx + dx * s, cy + dy * s, 12 * s, 12 * s, fill=(240, 150, 140))
    elif kind == "thermo":
        d.rounded_rectangle([_s(cx - 28 * s), _s(cy - 130 * s), _s(cx + 28 * s), _s(cy + 70 * s)], radius=_s(28 * s), fill=(255, 255, 252), outline=INK, width=w)
        _e(d, cx, cy + 90 * s, 46 * s, 46 * s, fill=RED, outline=INK, width=w)
        d.rectangle([_s(cx - 11 * s), _s(cy - 70 * s), _s(cx + 11 * s), _s(cy + 80 * s)], fill=RED)
        for i in range(5):
            d.line([_s(cx + 34 * s), _s(cy - 100 * s + i * 34 * s), _s(cx + 58 * s), _s(cy - 100 * s + i * 34 * s)], fill=INK, width=_s(4))
    elif kind == "faucet":
        d.rounded_rectangle([_s(cx - 110 * s), _s(cy - 60 * s), _s(cx + 30 * s), _s(cy - 20 * s)], radius=_s(14 * s), fill=(170, 176, 188), outline=INK, width=w)
        d.rectangle([_s(cx + 0 * s), _s(cy - 20 * s), _s(cx + 40 * s), _s(cy + 20 * s)], fill=(170, 176, 188), outline=INK, width=w)
        d.rectangle([_s(cx - 20 * s), _s(cy - 100 * s), _s(cx + 10 * s), _s(cy - 60 * s)], fill=RED, outline=INK, width=_s(4))
        d.polygon([(_s(cx + 20 * s), _s(cy + 40 * s)), (_s(cx + 44 * s), _s(cy + 90 * s)), (_s(cx - 4 * s), _s(cy + 90 * s))], fill=BLUE, outline=INK)
        _e(d, cx + 20 * s, cy + 94 * s, 24 * s, 24 * s, fill=BLUE, outline=INK, width=_s(4))
        d.arc([_s(cx - 90 * s), _s(cy + 120 * s), _s(cx + 130 * s), _s(cy + 170 * s)], 0, 180, fill=(190, 150, 100), width=_s(6))
    elif kind == "flame":
        d.polygon([(_s(cx), _s(cy - 130 * s)), (_s(cx + 60 * s), _s(cy - 20 * s)), (_s(cx + 70 * s), _s(cy + 60 * s)), (_s(cx), _s(cy + 110 * s)), (_s(cx - 70 * s), _s(cy + 60 * s)), (_s(cx - 52 * s), _s(cy - 30 * s))], fill=(240, 120, 50), outline=INK)
        d.polygon([(_s(cx), _s(cy - 50 * s)), (_s(cx + 34 * s), _s(cy + 20 * s)), (_s(cx + 30 * s), _s(cy + 80 * s)), (_s(cx), _s(cy + 100 * s)), (_s(cx - 34 * s), _s(cy + 70 * s)), (_s(cx - 30 * s), _s(cy + 10 * s))], fill=(255, 210, 90))
        for dx in (-120, 120):
            d.polygon([(_s(cx + dx * s), _s(cy + 20 * s)), (_s(cx + (dx + 26) * s), _s(cy + 100 * s)), (_s(cx + (dx - 26) * s), _s(cy + 100 * s))], fill=(70, 130, 90), outline=INK)
    elif kind == "passport":
        d.rounded_rectangle([_s(cx - 70 * s), _s(cy - 100 * s), _s(cx + 50 * s), _s(cy + 70 * s)], radius=_s(10 * s), fill=(44, 84, 150), outline=INK, width=w)
        _e(d, cx - 10 * s, cy - 30 * s, 34 * s, 34 * s, outline=(240, 220, 150), width=_s(5))
        d.line([_s(cx - 44 * s), _s(cy - 30 * s), _s(cx + 24 * s), _s(cy - 30 * s)], fill=(240, 220, 150), width=_s(4))
        for i, t in enumerate(("$", "€", "¥")):
            d.text((_s(cx + 70 * s), _s(cy - 70 * s + i * 70 * s)), t, font=font("black", _s(56 * s)), fill=RED, anchor="mm")
    elif kind == "chart":
        d.rounded_rectangle([_s(cx - 130 * s), _s(cy - 90 * s), _s(cx + 130 * s), _s(cy + 70 * s)], radius=_s(12 * s), fill=(34, 40, 60), outline=INK, width=w)
        for i, (top, bot, up) in enumerate(((-60, -20, False), (-40, 10, False), (-20, 30, False), (0, 50, False), (10, 56, False))):
            x = cx - 90 * s + i * 44 * s
            d.line([_s(x), _s(cy + top * s - 12), _s(x), _s(cy + bot * s + 12)], fill=(96, 150, 230), width=_s(4))
            d.rectangle([_s(x - 10 * s), _s(cy + top * s), _s(x + 10 * s), _s(cy + bot * s)], fill=(96, 150, 230))
        d.line([_s(cx - 110 * s), _s(cy - 70 * s), _s(cx + 100 * s), _s(cy + 40 * s)], fill=RED, width=_s(8))
        d.rectangle([_s(cx - 10 * s), _s(cy + 70 * s), _s(cx + 10 * s), _s(cy + 110 * s)], fill=(120, 126, 140))
        d.rectangle([_s(cx - 50 * s), _s(cy + 108 * s), _s(cx + 50 * s), _s(cy + 124 * s)], fill=(120, 126, 140))
    elif kind == "crowd":
        cols = [(214, 76, 76), (112, 168, 214), (240, 190, 80), (96, 170, 120), (170, 130, 200)]
        for i in range(5):
            x = cx - 120 * s + i * 60 * s
            y = cy + (14 if i % 2 else 0) * s
            _e(d, x, y - 40 * s, 22 * s, 22 * s, fill=(250, 222, 186), outline=INK, width=_s(3))
            d.rounded_rectangle([_s(x - 26 * s), _s(y - 14 * s), _s(x + 26 * s), _s(y + 70 * s)], radius=_s(14 * s), fill=cols[i], outline=INK, width=_s(3))
        d.rectangle([_s(cx - 60 * s), _s(cy - 120 * s), _s(cx + 30 * s), _s(cy - 76 * s)], fill=(255, 255, 252), outline=INK, width=_s(4))
        d.line([_s(cx - 20 * s), _s(cy - 76 * s), _s(cx - 20 * s), _s(cy - 20 * s)], fill=INK, width=_s(5))
    elif kind == "cake":
        d.rounded_rectangle([_s(cx - 110 * s), _s(cy + 10 * s), _s(cx + 110 * s), _s(cy + 90 * s)], radius=_s(18 * s), fill=(252, 236, 232), outline=INK, width=w)
        d.rounded_rectangle([_s(cx - 80 * s), _s(cy - 50 * s), _s(cx + 80 * s), _s(cy + 14 * s)], radius=_s(16 * s), fill=(250, 214, 210), outline=INK, width=w)
        d.text((_s(cx), _s(cy + 52 * s)), "2027", font=font("black", _s(50 * s)), fill=RED, anchor="mm")
        for i in range(4):
            x = cx - 54 * s + i * 36 * s
            d.rectangle([_s(x - 6 * s), _s(cy - 90 * s), _s(x + 6 * s), _s(cy - 50 * s)], fill=BLUE, outline=INK, width=_s(2))
            d.polygon([(_s(x), _s(cy - 118 * s)), (_s(x + 9 * s), _s(cy - 94 * s)), (_s(x - 9 * s), _s(cy - 94 * s))], fill=(255, 190, 70))


def _wedge(d, cx, cy, r, m, fill, outline=INK):
    a0, a1 = (m - 1) * 30 - 90, m * 30 - 90
    d.pieslice([_s(cx - r), _s(cy - r), _s(cx + r), _s(cy + r)], a0, a1, fill=fill, outline=outline, width=_s(4))


def wheel(d, cx, cy, r=400, hl=None):
    _e(d, cx, cy, r + 14, r + 14, fill=(255, 255, 252), outline=INK, width=_s(6))
    pal = [(250, 236, 214), (226, 238, 250)]
    for m in range(1, 13):
        _wedge(d, cx, cy, r, m, (255, 226, 150) if m == hl else pal[m % 2])
    for m in range(1, 13):
        a = math.radians((m - 0.5) * 30 - 90)
        icon(d, ICONS[m], cx + r * 0.58 * math.cos(a), cy + r * 0.58 * math.sin(a), r / 760)
        d.text((_s(cx + r * 0.88 * math.cos(a)), _s(cy + r * 0.88 * math.sin(a))), str(m), font=font("black", _s(max(22, r / 11))), fill=RED if m == hl else INK, anchor="mm")
    _e(d, cx, cy, r * 0.12, r * 0.12, fill=RED, outline=INK, width=_s(4))


def slice_(d, cx, cy, month, r=380):
    """한 달 칸을 크게 펼친 조각(부채꼴 느낌의 둥근 카드) + 큰 그림 + 월 이름."""
    d.rounded_rectangle([_s(cx - r), _s(cy - r * 0.9), _s(cx + r), _s(cy + r * 0.9)], radius=_s(40), fill=(255, 250, 236), outline=INK, width=_s(6))
    icon(d, ICONS[month], cx, cy - r * 0.08, r / 230)
    d.text((_s(cx), _s(cy - r * 0.9 + 56)), MONTH_KO[month], font=font("black", _s(84)), fill=RED, anchor="mm")


def badge(d, cx, cy, month, r=110):
    _e(d, cx, cy, r, r, fill=(255, 250, 236), outline=INK, width=_s(6))
    icon(d, ICONS[month], cx, cy + 6, r / 210)
    d.rounded_rectangle([_s(cx - 54), _s(cy - r - 26), _s(cx + 54), _s(cy - r + 30)], radius=_s(26), fill=RED)
    d.text((_s(cx), _s(cy - r + 2)), MONTH_KO[month], font=font("black", _s(40)), fill=(255, 255, 255), anchor="mm")


# ── 이코노미스트 표지 그림을 12칸으로 나눠 쓰기 (v1.14.0, 현철님 지정: 비평·소개 목적의 인용, 출처 표기) ──
COVER = {  # 표지 파일, 원의 중심(x, y), 반지름(px), 출처 표기
    "2027": ("ref/cover2027.jpg", (590, 960), 525, "출처 불명 이미지 (이코노미스트 표지라고 알려짐)"),
    "2026": ("ref/cover2026.jpg", (612, 904), 572, "The Economist, The World Ahead 2026"),
}
_CACHE = {}


def _cover_img(project_dir, key):
    import os
    from PIL import Image
    path = os.path.join(project_dir, COVER[key][0])
    if path not in _CACHE:
        _CACHE[path] = Image.open(path).convert("RGB")
    return _CACHE[path]


def photo_slice(d, project_dir, key, month, cx, cy, h=720, bw=None):
    """표지 원을 12조각으로 나눈 한 달 조각(부채꼴로 오려 냄)을 크림 카드 위에 붙인다."""
    from PIL import Image, ImageDraw as ID
    src = _cover_img(project_dir, key)
    _, (ox, oy), R, label = COVER[key]
    a0, a1 = (month - 1) * 30, month * 30
    pts = [(ox, oy)] + [(ox + R * math.sin(math.radians(a0 + t * (a1 - a0) / 24)), oy - R * math.cos(math.radians(a0 + t * (a1 - a0) / 24))) for t in range(25)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    box = (int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1)
    crop = src.crop(box).convert("RGBA")
    mask = Image.new("L", crop.size, 0)
    ID.Draw(mask).polygon([(x - box[0], y - box[1]) for x, y in pts], fill=255)
    crop.putalpha(mask)
    bw = bw or h * 1.15
    k = min(h / crop.size[1], bw / crop.size[0])
    crop = crop.resize((int(crop.size[0] * k * K), int(crop.size[1] * k * K)), Image.LANCZOS)
    im = d._image
    cw, ch = crop.size
    x0, y0 = int(_s(cx) - cw / 2), int(_s(cy) - ch / 2)
    pad = _s(26)
    card = Image.new("RGBA", (cw + 2 * pad, ch + 2 * pad + _s(60)), (255, 250, 236, 255))
    ID.Draw(card).rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=_s(30), outline=INK, width=_s(6))
    im.alpha_composite(card, (x0 - pad, y0 - pad - _s(10)))
    im.alpha_composite(crop, (x0, y0))
    d2 = ID.Draw(im)
    d2.text((_s(cx), y0 + ch + pad - _s(8)), label, font=font("medium", _s(26)), fill=(120, 100, 90), anchor="mm")
    d2.rounded_rectangle([x0 - pad + _s(14), y0 - pad - _s(4), x0 - pad + _s(150), y0 - pad + _s(60)], radius=_s(28), fill=RED)
    d2.text((x0 - pad + _s(82), y0 - pad + _s(28)), MONTH_KO[month], font=font("black", _s(44)), fill=(255, 255, 255), anchor="mm")


def photo_cover(d, project_dir, key, cx, cy, h=960, lines=True):
    """표지 원 전체를 보여 주고 12칸 경계선을 얹는다."""
    from PIL import Image, ImageDraw as ID
    src = _cover_img(project_dir, key)
    _, (ox, oy), R, label = COVER[key]
    m = int(R * 1.04)
    crop = src.crop((ox - m, oy - m, ox + m, oy + m)).convert("RGBA")
    if lines:
        cd = ID.Draw(crop)
        for i in range(12):
            a = math.radians(i * 30)
            cd.line([m, m, m + R * math.sin(a), m - R * math.cos(a)], fill=(220, 60, 60, 230), width=5)
        cd.ellipse([m - R, m - R, m + R, m + R], outline=(220, 60, 60, 230), width=5)
    side = _s(h)
    crop = crop.resize((side, side), Image.LANCZOS)
    im = d._image
    x0, y0 = _s(cx) - side // 2, _s(cy) - side // 2
    im.alpha_composite(crop, (x0, y0))
    ID.Draw(im).text((_s(cx), y0 + side + _s(18)), label, font=font("medium", _s(28)), fill=(110, 90, 80), anchor="mm")
