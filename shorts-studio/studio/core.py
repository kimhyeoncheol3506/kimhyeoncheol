"""공통 유틸: 폰트, 이징, 손그림 선, 텍스트(키워드 강조) 렌더링."""
from __future__ import annotations

import math
import random
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
FPS = 30

FONTS = {
    "impact": "BlackHanSans-Regular.ttf",      # 후크/타이틀 (임팩트)
    "bold": "Pretendard-ExtraBold.otf",         # 자막
    "semi": "Pretendard-Bold.otf",
    "body": "Pretendard-Medium.otf",
    "hand": "Jua-Regular.ttf",                  # 둥근 손글씨 (꽁트 타이틀/말풍선/지도 제목)
    "pen": "PoorStory-Regular.ttf",             # 펜 손글씨 (지도 본문)
}

# 팔레트 (혼잡스 지도 오렌지 + 인생녹음중 파스텔)
ORANGE = (217, 102, 63)
YELLOW = (255, 214, 10)
RED = (229, 57, 53)
INK = (24, 24, 27)
WHITE = (255, 255, 255)
PAPER = (250, 249, 246)
PEACH = (252, 227, 200)
MINT = (191, 220, 214)
SKY = (205, 226, 245)


@lru_cache(maxsize=256)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / FONTS[name]), size)


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def ease_out_back(x, s=1.70158):
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def ease_out_elastic(x):
    x = clamp(x)
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi / 3)) + 1


def lerp(a, b, t):
    return a + (b - a) * t


# ---------- 글리프 대체 (폰트에 없는 문자) ----------
FALLBACK = {"→": "->", "—": "-", "–": "-", "…": "...", "·": "/", "☞": "->", "▶": ">"}


@lru_cache(maxsize=32)
def _cmap(path):
    from fontTools.ttLib import TTFont
    return set(TTFont(path).getBestCmap())


def safe_text(fnt, text):
    cm = _cmap(fnt.path)
    return "".join(c if (ord(c) in cm or c in " *\n") else FALLBACK.get(c, c) for c in text)


# ---------- 키워드 마크업 ----------
def parse_markup(text: str):
    """'평범 *강조* 평범' → [(seg, is_key)]"""
    out, key = [], False
    for i, part in enumerate(text.split("*")):
        if part:
            out.append((part, i % 2 == 1))
    return out


def strip_markup(text: str) -> str:
    return text.replace("*", "")


def text_width(fnt, text):
    return fnt.getlength(text)


def draw_rich_line(draw: ImageDraw.ImageDraw, xy, text, fnt, fill, key_fill,
                   stroke=0, stroke_fill=INK, anchor_center=True):
    """키워드 강조된 한 줄. xy=(cx, y_top) if anchor_center."""
    segs = parse_markup(safe_text(fnt, text))
    total = sum(fnt.getlength(s) for s, _ in segs)
    x, y = xy
    if anchor_center:
        x = x - total / 2
    for s, k in segs:
        draw.text((x, y), s, font=fnt, fill=key_fill if k else fill,
                  stroke_width=stroke, stroke_fill=stroke_fill)
        x += fnt.getlength(s)
    return total


def rich_block(lines, fnt, fill, key_fill, stroke=0, stroke_fill=INK,
               line_gap=1.18, pad=40):
    """여러 줄 강조 텍스트를 RGBA 이미지로 (팝인 스케일 애니메이션용)."""
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * line_gap)
    w = int(max(fnt.getlength(strip_markup(l)) for l in lines)) + pad * 2
    h = lh * len(lines) + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        draw_rich_line(d, (w / 2, pad + i * lh), l, fnt, fill, key_fill, stroke, stroke_fill)
    return im


def paste_scaled(base: Image.Image, layer: Image.Image, center, scale=1.0, alpha=1.0, rotate=0.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    lw, lh = layer.size
    im = layer
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(lw * scale)), max(1, int(lh * scale))), Image.BICUBIC)
    if rotate:
        im = im.rotate(rotate, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    x = int(center[0] - im.width / 2)
    y = int(center[1] - im.height / 2)
    base.paste(im, (x, y), im)


# ---------- 손그림 선 ----------
def wobble_points(points, amp=2.0, seed=0, step=14):
    rnd = random.Random(seed)
    out = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        dist = math.hypot(x2 - x1, y2 - y1)
        n = max(1, int(dist / step))
        for i in range(n):
            t = i / n
            out.append((lerp(x1, x2, t) + rnd.uniform(-amp, amp), lerp(y1, y2, t) + rnd.uniform(-amp, amp)))
    out.append(points[-1])
    return out


def hand_line(draw, points, fill=INK, width=5, amp=1.6, seed=0):
    pts = wobble_points(points, amp, seed)
    draw.line(pts, fill=fill, width=width, joint="curve")
    r = width / 2
    for x, y in (pts[0], pts[-1]):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def marker_ellipse_points(cx, cy, rx, ry, progress=1.0, seed=0, turns=1.12):
    """주황 마커로 두르는 동그라미 (살짝 겹치게 1.12바퀴, 손떨림)."""
    rnd = random.Random(seed)
    start = rnd.uniform(0, 2 * math.pi)
    n = 90
    total = int(n * turns * clamp(progress))
    pts = []
    jitter = [rnd.uniform(-0.04, 0.04) for _ in range(8)]
    for i in range(total + 1):
        a = start + 2 * math.pi * i / n
        k = 1 + jitter[int(i / n * 8) % 8] + 0.05 * (i / n)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a) * 0.98))
    return pts


def marker_circle(draw, cx, cy, rx, ry, progress=1.0, seed=0, fill=ORANGE, width=12):
    pts = marker_ellipse_points(cx, cy, rx, ry, progress, seed)
    if len(pts) > 1:
        draw.line(pts, fill=fill, width=width, joint="curve")


def hand_arrow(draw, p1, p2, fill=INK, width=5, seed=0, head=22):
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    nx, ny = -(p2[1] - p1[1]), (p2[0] - p1[0])
    L = math.hypot(nx, ny) or 1
    bend = 0.12 * math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    ctrl = (mx + nx / L * bend, my + ny / L * bend)
    pts = [(lerp(lerp(p1[0], ctrl[0], t), lerp(ctrl[0], p2[0], t), t),
            lerp(lerp(p1[1], ctrl[1], t), lerp(ctrl[1], p2[1], t), t)) for t in [i / 24 for i in range(25)]]
    hand_line(draw, pts, fill, width, 1.0, seed)
    ang = math.atan2(p2[1] - pts[-3][1], p2[0] - pts[-3][0])
    for s in (-1, 1):
        a = ang + math.pi + s * 0.45
        hand_line(draw, [p2, (p2[0] + head * math.cos(a), p2[1] + head * math.sin(a))], fill, width, 0.6, seed + s)


def rounded_card(size, radius, fill, shadow=True, shadow_blur=24, shadow_alpha=110):
    w, h = size
    pad = shadow_blur * 2 if shadow else 0
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 10, pad + w, pad + h + 10), radius, fill=(0, 0, 0, shadow_alpha))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(shadow_blur)))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), radius, fill=fill)
    return im, pad


def wrap_text(text, fnt, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(strip_markup(trial)) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    # 강조 마크업이 줄을 넘어가면 줄마다 닫고 다시 연다
    fixed, open_ = [], False
    for l in lines:
        s = ("*" if open_ else "") + l
        if l.count("*") % 2 == 1:
            open_ = not open_
        if open_:
            s += "*"
        fixed.append(s)
    return fixed
