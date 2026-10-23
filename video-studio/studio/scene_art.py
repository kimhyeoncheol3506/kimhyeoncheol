"""코드로 그린 파스텔 장면 (v1.14.0): 방 배경 + 은유 소품 + 개미 + 자막 한 줄 + 우상단 로고.

    from studio.scene_art import compose_scene
    img = compose_scene(room="mint", props=[("chalkboard", dict(...))], ant=("설명", 0.30), subtitle="…", zoom=1.03)

규칙(현철님 Y 결정, 경제학 똑똑 분석): 한 자막 = 한 장면, 소품 하나로 뜻 전달, 숫자는 그림 속 사물에,
자막 한 줄 20자 안팎(검은 반투명 상자 + 흰 글씨), 장면마다 파스텔 배경, 우상단 채널 로고.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from .draw import font
from .mascot import POSES, draw_ant

W, H = 1920, 1080
K = 2  # 안티앨리어싱용 확대 비율

ROOMS = {  # 벽, 바닥, 창 하늘, 포인트
    "mint": ((214, 240, 226), (176, 214, 196), (190, 226, 246), (120, 190, 160)),
    "peach": ((252, 230, 208), (238, 200, 170), (200, 226, 246), (232, 160, 120)),
    "sky": ((208, 230, 250), (170, 200, 232), (232, 244, 255), (110, 160, 214)),
    "lavender": ((232, 224, 250), (204, 192, 234), (210, 228, 250), (150, 130, 206)),
    "cream": ((250, 244, 224), (232, 220, 186), (200, 228, 246), (214, 180, 110)),
}
INK = (92, 62, 48)


def _s(v):
    return int(v * K)


def _room(d, kind):
    wall, floor, sky, accent = ROOMS[kind]
    d.rectangle([0, 0, _s(W), _s(H)], fill=wall)
    d.rectangle([0, _s(H * 0.80), _s(W), _s(H)], fill=floor)
    d.rectangle([0, _s(H * 0.80) - _s(8), _s(W), _s(H * 0.80)], fill=tuple(max(0, c - 22) for c in floor))
    # 창문
    x0, y0, x1, y1 = 90, 120, 430, 520
    d.rounded_rectangle([_s(x0 - 14), _s(y0 - 14), _s(x1 + 14), _s(y1 + 14)], radius=_s(18), fill=(250, 250, 248), outline=INK, width=_s(5))
    d.rectangle([_s(x0), _s(y0), _s(x1), _s(y1)], fill=sky)
    d.line([_s((x0 + x1) / 2), _s(y0), _s((x0 + x1) / 2), _s(y1)], fill=(250, 250, 248), width=_s(10))
    d.line([_s(x0), _s((y0 + y1) / 2), _s(x1), _s((y0 + y1) / 2)], fill=(250, 250, 248), width=_s(10))
    for cx, cy, r in ((200, 240, 34), (250, 230, 44), (310, 244, 32)):
        d.ellipse([_s(cx - r), _s(cy - r * 0.7), _s(cx + r), _s(cy + r * 0.7)], fill=(255, 255, 255, 230))
    # 화분
    px, py = 1830, H * 0.80
    d.polygon([(_s(px - 60), _s(py - 100)), (_s(px + 60), _s(py - 100)), (_s(px + 44), _s(py + 30)), (_s(px - 44), _s(py + 30))], fill=accent, outline=INK)
    for ang, ln in ((-50, 150), (-20, 190), (20, 180), (55, 140), (0, 220)):
        a = math.radians(ang - 90)
        ex, ey = px + ln * math.cos(a), py - 100 + ln * math.sin(a)
        d.line([_s(px), _s(py - 100), _s(ex), _s(ey)], fill=(96, 160, 110), width=_s(8))
        d.ellipse([_s(ex - 26), _s(ey - 18), _s(ex + 26), _s(ey + 18)], fill=(130, 196, 130), outline=(70, 130, 90), width=_s(3))


def _chalkboard(d, cx, cy, w, h, lines, note=None):
    d.rounded_rectangle([_s(cx - w / 2 - 14), _s(cy - h / 2 - 14), _s(cx + w / 2 + 14), _s(cy + h / 2 + 14)], radius=_s(16), fill=(196, 156, 110), outline=INK, width=_s(5))
    d.rounded_rectangle([_s(cx - w / 2), _s(cy - h / 2), _s(cx + w / 2), _s(cy + h / 2)], radius=_s(10), fill=(54, 84, 78))
    n = len(lines)
    for i, (txt, col, size) in enumerate(lines):
        y = cy - h / 2 + h * (i + 0.5) / n
        d.text((_s(cx), _s(y)), txt, font=font("bold", _s(size)), fill=col, anchor="mm")
    if note:
        d.text((_s(cx + w / 2 - 14), _s(cy + h / 2 - 12)), note, font=font("medium", _s(26)), fill=(220, 230, 226), anchor="rd")


def _house(d, cx, base, s=1.0, col=(246, 214, 170)):
    w, h = 260 * s, 180 * s
    d.rectangle([_s(cx - w / 2), _s(base - h), _s(cx + w / 2), _s(base)], fill=col, outline=INK, width=_s(5))
    d.polygon([(_s(cx - w / 2 - 24 * s), _s(base - h)), (_s(cx), _s(base - h - 120 * s)), (_s(cx + w / 2 + 24 * s), _s(base - h))], fill=(214, 110, 100), outline=INK)
    d.rectangle([_s(cx - 34 * s), _s(base - 100 * s), _s(cx + 34 * s), _s(base)], fill=(150, 104, 80), outline=INK, width=_s(4))
    d.rectangle([_s(cx + 70 * s), _s(base - 130 * s), _s(cx + 114 * s), _s(base - 84 * s)], fill=(196, 226, 246), outline=INK, width=_s(4))
    d.rectangle([_s(cx - 114 * s), _s(base - 130 * s), _s(cx - 70 * s), _s(base - 84 * s)], fill=(196, 226, 246), outline=INK, width=_s(4))


def _rocket(d, cx, cy, s=1.0):
    d.polygon([(_s(cx), _s(cy - 150 * s)), (_s(cx + 48 * s), _s(cy - 60 * s)), (_s(cx + 48 * s), _s(cy + 60 * s)), (_s(cx - 48 * s), _s(cy + 60 * s)), (_s(cx - 48 * s), _s(cy - 60 * s))], fill=(250, 250, 252), outline=INK)
    d.polygon([(_s(cx), _s(cy - 150 * s)), (_s(cx + 48 * s), _s(cy - 60 * s)), (_s(cx - 48 * s), _s(cy - 60 * s))], fill=(226, 90, 90), outline=INK)
    d.ellipse([_s(cx - 20 * s), _s(cy - 30 * s), _s(cx + 20 * s), _s(cy + 10 * s)], fill=(160, 210, 244), outline=INK, width=_s(4))
    d.polygon([(_s(cx - 48 * s), _s(cy + 20 * s)), (_s(cx - 84 * s), _s(cy + 76 * s)), (_s(cx - 48 * s), _s(cy + 60 * s))], fill=(226, 90, 90), outline=INK)
    d.polygon([(_s(cx + 48 * s), _s(cy + 20 * s)), (_s(cx + 84 * s), _s(cy + 76 * s)), (_s(cx + 48 * s), _s(cy + 60 * s))], fill=(226, 90, 90), outline=INK)
    d.polygon([(_s(cx - 30 * s), _s(cy + 60 * s)), (_s(cx + 30 * s), _s(cy + 60 * s)), (_s(cx), _s(cy + 150 * s))], fill=(255, 190, 70))


def _arrow(d, x, y, up=True, s=1.0, col=None):
    col = col or ((226, 90, 90) if up else (96, 140, 224))
    k = 1 if up else -1
    d.polygon([(_s(x), _s(y - k * 100 * s)), (_s(x + 70 * s), _s(y)), (_s(x + 30 * s), _s(y)), (_s(x + 30 * s), _s(y + k * 110 * s)),
               (_s(x - 30 * s), _s(y + k * 110 * s)), (_s(x - 30 * s), _s(y)), (_s(x - 70 * s), _s(y))], fill=col, outline=INK)


def _piggy(d, cx, cy, s=1.0):
    d.ellipse([_s(cx - 150 * s), _s(cy - 100 * s), _s(cx + 150 * s), _s(cy + 100 * s)], fill=(250, 190, 200), outline=INK, width=_s(5))
    d.ellipse([_s(cx + 110 * s), _s(cy - 30 * s), _s(cx + 190 * s), _s(cy + 40 * s)], fill=(246, 170, 184), outline=INK, width=_s(5))
    d.ellipse([_s(cx + 140 * s), _s(cy - 8 * s), _s(cx + 154 * s), _s(cy + 6 * s)], fill=INK)
    d.polygon([(_s(cx + 60 * s), _s(cy - 94 * s)), (_s(cx + 110 * s), _s(cy - 150 * s)), (_s(cx + 120 * s), _s(cy - 80 * s))], fill=(246, 170, 184), outline=INK)
    d.ellipse([_s(cx + 70 * s), _s(cy - 30 * s), _s(cx + 94 * s), _s(cy - 6 * s)], fill=INK)
    d.rounded_rectangle([_s(cx - 50 * s), _s(cy - 100 * s), _s(cx + 30 * s), _s(cy - 86 * s)], radius=_s(6), fill=INK)
    for x in (-90, -40, 40, 90):
        d.rounded_rectangle([_s(cx + x * s - 22 * s), _s(cy + 80 * s), _s(cx + x * s + 22 * s), _s(cy + 134 * s)], radius=_s(10), fill=(246, 170, 184), outline=INK, width=_s(4))
    d.ellipse([_s(cx - 36 * s), _s(cy - 190 * s), _s(cx + 36 * s), _s(cy - 150 * s)], fill=(244, 200, 80), outline=(176, 130, 40), width=_s(4))


def _tablet(d, cx, cy, w, h, title, rows):
    d.rounded_rectangle([_s(cx - w / 2 - 14), _s(cy - h / 2 - 14), _s(cx + w / 2 + 14), _s(cy + h / 2 + 14)], radius=_s(26), fill=(70, 76, 96), outline=INK, width=_s(5))
    d.rounded_rectangle([_s(cx - w / 2), _s(cy - h / 2), _s(cx + w / 2), _s(cy + h / 2)], radius=_s(14), fill=(252, 252, 250))
    d.text((_s(cx), _s(cy - h / 2 + 44)), title, font=font("xbold", _s(40)), fill=(60, 70, 110), anchor="mm")
    for i, (txt, ok) in enumerate(rows):
        y = cy - h / 2 + 110 + i * 78
        d.rounded_rectangle([_s(cx - w / 2 + 34), _s(y - 24), _s(cx - w / 2 + 82), _s(y + 24)], radius=_s(8), outline=(120, 130, 160), width=_s(4), fill=(236, 246, 238) if ok else (252, 252, 250))
        if ok:
            d.line([_s(cx - w / 2 + 46), _s(y), _s(cx - w / 2 + 56), _s(y + 12), _s(cx - w / 2 + 72), _s(y - 14)], fill=(60, 170, 100), width=_s(8))
        d.text((_s(cx - w / 2 + 108), _s(y)), txt, font=font("bold", _s(40)), fill=(60, 60, 80), anchor="lm")


def _scale(d, cx, cy, tilt=0.0, left=None, right=None):
    d.polygon([(_s(cx - 70), _s(cy + 250)), (_s(cx + 70), _s(cy + 250)), (_s(cx + 36), _s(cy + 200)), (_s(cx - 36), _s(cy + 200))], fill=(170, 150, 120), outline=INK)
    d.rectangle([_s(cx - 12), _s(cy - 120), _s(cx + 12), _s(cy + 204)], fill=(190, 166, 130), outline=INK, width=_s(4))
    dx, dy = 230 * math.cos(tilt), 230 * math.sin(tilt)
    a, b = (cx - dx, cy - 120 - dy), (cx + dx, cy - 120 + dy)
    d.line([_s(a[0]), _s(a[1]), _s(b[0]), _s(b[1])], fill=INK, width=_s(14))
    d.ellipse([_s(cx - 20), _s(cy - 140), _s(cx + 20), _s(cy - 100)], fill=(244, 200, 80), outline=INK, width=_s(4))
    for (px, py), item in ((a, left), (b, right)):
        d.line([_s(px), _s(py), _s(px - 70), _s(py + 130)], fill=INK, width=_s(5))
        d.line([_s(px), _s(py), _s(px + 70), _s(py + 130)], fill=INK, width=_s(5))
        d.pieslice([_s(px - 100), _s(py + 70), _s(px + 100), _s(py + 190)], 0, 180, fill=(244, 214, 130), outline=INK, width=_s(5))
        if item == "house":
            _house(d, px, py + 76, 0.34)
        elif item == "coins":
            for i in range(4):
                d.ellipse([_s(px - 40), _s(py + 56 - i * 16), _s(px + 40), _s(py + 82 - i * 16)], fill=(244, 200, 80), outline=(176, 130, 40), width=_s(3))


def compose_scene(room="mint", props=(), ant=("기본", 0.30), subtitle="", zoom=1.0, logo=True, ant_height=780, ant_flip=False):
    big = Image.new("RGBA", (_s(W), _s(H)), (255, 255, 255, 255))
    d = ImageDraw.Draw(big, "RGBA")
    _room(d, room)
    for kind, kw in props:
        {"chalkboard": _chalkboard, "house": _house, "rocket": _rocket, "arrow": _arrow, "piggy": _piggy,
         "tablet": _tablet, "scale": _scale}[kind](d, **kw)
    img = big.resize((W, H), Image.LANCZOS)
    pose, ax = ant
    a = draw_ant(dict(POSES[pose]), ant_height)
    if ant_flip:
        a = a.transpose(Image.FLIP_LEFT_RIGHT)
    img.alpha_composite(a, (int(W * ax - a.width / 2), H - a.height + 70))
    dd = ImageDraw.Draw(img, "RGBA")
    if logo:
        f = font("black", 34)
        for i, t in enumerate(("월급쟁이", "재테크 스킬")):
            dd.text((W - 52, 44 + i * 40), t, font=f, fill=(255, 255, 255), anchor="ra", stroke_width=5, stroke_fill=(40, 36, 48))
    if subtitle:
        f = font("bold", 58)
        tw = f.getlength(subtitle)
        y = H - 120
        dd.rounded_rectangle([W / 2 - tw / 2 - 30, y - 50, W / 2 + tw / 2 + 30, y + 50], radius=10, fill=(0, 0, 0, 190))
        dd.text((W / 2, y), subtitle, font=f, fill=(255, 255, 255), anchor="mm")
    if zoom != 1.0:  # 미세 클로즈업
        cw, ch = W / zoom, H / zoom
        img = img.crop((int((W - cw) / 2), int((H - ch) / 2), int((W + cw) / 2), int((H + ch) / 2))).resize((W, H), Image.LANCZOS)
    return img.convert("RGB")
