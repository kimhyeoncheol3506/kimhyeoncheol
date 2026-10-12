"""그리기 도구: 폰트, 텍스트, 오리지널 마스코트, 아이콘.

마스코트 '여의도 개미'(남: 하늘색 셔츠+카멜 가디건 / 여: 흰 블라우스+코랄 가디건+리본, 비즈니스 캐주얼)는 이 프로젝트 전용으로 코드로 그린 오리지널 캐릭터다.
v1.3.0에서 벤치마킹 채널(정장·흰 얼굴 캐릭터)과 닮지 않도록 전면 교체: 캐러멜색 얼굴 + 더듬이 + 비즈니스 캐주얼(넥타이·정장 없음) + ₩ 배지.
"""
from __future__ import annotations

import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

INK = (24, 24, 27)
WHITE = (255, 255, 255)
YELLOW = (255, 214, 10)
RED = (232, 58, 58)
BLUE = (42, 120, 214)
GREEN = (27, 160, 110)
GOLD = (245, 185, 30)
NAVY = (31, 45, 82)

PASTELS = ["#F4E9D8", "#E3EEF7", "#E6F2E6", "#F7E4E1", "#ECE6F5", "#F5F0DC", "#E1F0F0", "#EFEFEF"]

FONTS = {
    "black": "Pretendard-Black.otf",
    "xbold": "Pretendard-ExtraBold.otf",
    "bold": "Pretendard-Bold.otf",
    "medium": "Pretendard-Medium.otf",
    "thumb": "BlackHanSans-Regular.ttf",
}


@lru_cache(maxsize=256)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[kind]), size)


def hex2rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def text_w(fnt: ImageFont.FreeTypeFont, s: str) -> int:
    b = fnt.getbbox(s)
    return b[2] - b[0]


def fit_font(kind: str, size: int, s: str, max_w: int, min_size: int = 20) -> ImageFont.FreeTypeFont:
    """한 줄 텍스트가 max_w 안에 들어가도록 글자 크기를 줄인다."""
    while size > min_size and max(text_w(font(kind, size), line) for line in s.split("\n")) > max_w:
        size = int(size * 0.92)
    return font(kind, size)


def wrap(s: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """한국어 줄바꿈: 공백 단위 우선, 한 단어가 너무 길면 글자 단위."""
    lines: list[str] = []
    for para in s.split("\n"):
        cur = ""
        for word in para.split(" "):
            cand = f"{cur} {word}".strip()
            if text_w(fnt, cand) <= max_w:
                cur = cand
                continue
            if cur:
                lines.append(cur)
            cur = ""
            for ch in word:
                if text_w(fnt, cur + ch) > max_w and cur:
                    lines.append(cur)
                    cur = ch
                else:
                    cur += ch
        lines.append(cur)
    return [l for l in lines if l != ""] or [""]


def draw_text(d: ImageDraw.ImageDraw, xy, s, fnt, fill=INK, stroke=0, stroke_fill=INK, anchor="mm", spacing=1.18):
    """여러 줄 가운데 정렬 텍스트 (anchor는 블록 기준 mm/mt/lt 등)."""
    lines = s.split("\n")
    lh = int(fnt.size * spacing)
    total = lh * len(lines)
    x, y = xy
    if anchor[1] == "m":
        y0 = y - total / 2
    elif anchor[1] == "b":
        y0 = y - total
    else:
        y0 = y
    for i, line in enumerate(lines):
        d.text((x, y0 + i * lh + lh / 2), line, font=fnt, fill=fill, anchor=anchor[0] + "m", stroke_width=stroke, stroke_fill=stroke_fill)


def rounded(d, box, r, fill=None, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def vgradient(w: int, h: int, top, bottom) -> Image.Image:
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


# ───────────────────────── 마스코트 ─────────────────────────

def mascot(img: Image.Image, cx: float, cy: float, s: float = 1.0, emotion: str = "neutral", gender: str = "m",
           pose: str = "normal", label: str | None = None) -> None:
    """(cx, cy)는 얼굴 중심. s=1일 때 얼굴 폭 약 260px.

    emotion: neutral | happy | worried | shock | smug | sad | think | angry
    pose: normal | point | hands | shrug
    """
    d = ImageDraw.Draw(img)
    lw = max(3, int(7 * s))
    hw, hh = 125 * s, 115 * s
    head_col = (236, 164, 88) if gender == "m" else (244, 178, 110)   # 개미 캐러멜색 얼굴
    shirt = (190, 222, 245) if gender == "m" else (255, 255, 255)    # 남: 하늘색 옥스퍼드 셔츠 / 여: 흰 블라우스
    cardi = (196, 150, 98) if gender == "m" else (238, 120, 120)     # 남: 카멜 니트 가디건 / 여: 코랄 가디건
    cardi_dark = tuple(max(0, c - 45) for c in cardi)

    # 몸통: 비즈니스 캐주얼 (셔츠 + 앞이 열린 가디건, 넥타이 없음)
    body_top = cy + hh * 0.80
    bw = 150 * s
    body_bot = body_top + 255 * s
    d.rounded_rectangle([cx - bw * 0.95, body_top + 20 * s, cx + bw * 0.95, body_bot], radius=int(60 * s), fill=cardi, outline=INK, width=lw)
    # 가운데 셔츠 (가디건 앞섶 사이)
    d.polygon([(cx - 48 * s, body_top + 22 * s), (cx + 48 * s, body_top + 22 * s), (cx + 40 * s, body_bot - 3 * s), (cx - 40 * s, body_bot - 3 * s)],
              fill=shirt, outline=INK)
    for k in range(3):  # 셔츠 단추
        d.ellipse([cx - 5 * s, body_top + (80 + k * 50) * s, cx + 5 * s, body_top + (90 + k * 50) * s], fill=(120, 140, 160))
    # 열린 칼라 (셔츠 깃 두 개)
    for sg in (-1, 1):
        d.polygon([(cx, body_top + 52 * s), (cx + sg * 72 * s, body_top + 4 * s), (cx + sg * 58 * s, body_top + 80 * s)], fill=shirt, outline=INK)
        d.line([(cx + sg * 50 * s, body_top + 25 * s), (cx + sg * 44 * s, body_bot - 10 * s)], fill=cardi_dark, width=max(2, lw // 2))  # 가디건 앞섶선
    # 니트 밑단 줄무늬
    d.line([(cx - bw * 0.9, body_bot - 28 * s), (cx - 44 * s, body_bot - 28 * s)], fill=cardi_dark, width=max(2, lw // 2))
    d.line([(cx + 44 * s, body_bot - 28 * s), (cx + bw * 0.9, body_bot - 28 * s)], fill=cardi_dark, width=max(2, lw // 2))
    if label:
        f = font("black", int(32 * s))
        draw_text(d, (cx, body_top + 190 * s), label, f, fill=WHITE, stroke=max(2, int(3 * s)), stroke_fill=INK)
    else:  # 가디건 가슴의 ₩ 배지
        bx, by_ = cx + bw * 0.58, body_top + 95 * s
        d.ellipse([bx - 20 * s, by_ - 20 * s, bx + 20 * s, by_ + 20 * s], fill=GOLD, outline=INK, width=max(2, lw // 2))
        draw_text(d, (bx, by_), "₩", font("black", int(24 * s)), fill=(150, 95, 0))

    # 팔 (얼굴색 둥근 손)
    arm_y = body_top + 70 * s
    hand = lambda x, y: d.ellipse([x - 20 * s, y - 20 * s, x + 20 * s, y + 20 * s], fill=head_col, outline=INK, width=max(2, lw // 2))
    if pose == "point":
        d.line([(cx + bw * 0.85, arm_y), (cx + 235 * s, cy - 30 * s)], fill=INK, width=lw)
        hand(cx + 235 * s, cy - 40 * s)
        d.line([(cx - bw * 0.85, arm_y), (cx - 195 * s, body_top + 190 * s)], fill=INK, width=lw)
        hand(cx - 195 * s, body_top + 195 * s)
    elif pose == "shrug":
        for sg in (-1, 1):
            d.line([(cx + sg * bw * 0.85, arm_y), (cx + sg * 215 * s, arm_y - 5 * s), (cx + sg * 245 * s, arm_y - 70 * s)], fill=INK, width=lw)
            hand(cx + sg * 245 * s, arm_y - 80 * s)
    elif pose == "hands":  # 만세 (두 팔을 V자로 올림)
        for sg in (-1, 1):
            d.line([(cx + sg * bw * 0.85, arm_y), (cx + sg * 200 * s, arm_y - 60 * s), (cx + sg * 235 * s, cy - 60 * s)], fill=INK, width=lw, joint="curve")
            hand(cx + sg * 238 * s, cy - 72 * s)
    else:
        d.line([(cx - bw * 0.85, arm_y), (cx - 190 * s, body_top + 200 * s)], fill=INK, width=lw)
        d.line([(cx + bw * 0.85, arm_y), (cx + 190 * s, body_top + 200 * s)], fill=INK, width=lw)
        hand(cx - 190 * s, body_top + 205 * s)
        hand(cx + 190 * s, body_top + 205 * s)

    # 더듬이 (개미 식별 요소)
    for sg in (-1, 1):
        x0, y0 = cx + sg * 40 * s, cy - hh * 0.92
        x1, y1 = cx + sg * 95 * s, cy - hh - 85 * s
        d.line([(x0, y0), (cx + sg * 55 * s, cy - hh - 45 * s), (x1, y1)], fill=INK, width=lw, joint="curve")
        d.ellipse([x1 - 15 * s, y1 - 15 * s, x1 + 15 * s, y1 + 15 * s], fill=(70, 45, 30), outline=INK, width=max(2, lw // 2))
    if gender == "f":  # 오른쪽 더듬이 리본
        rx, ry = cx + 95 * s, cy - hh - 85 * s
        d.polygon([(rx, ry), (rx + 34 * s, ry - 20 * s), (rx + 34 * s, ry + 20 * s)], fill=(255, 90, 120), outline=INK)
        d.polygon([(rx, ry), (rx - 34 * s, ry - 20 * s), (rx - 34 * s, ry + 20 * s)], fill=(255, 90, 120), outline=INK)

    # 머리 (여성: 뒤 머리카락 먼저)
    if gender == "f":
        hair = (90, 55, 35)
        d.ellipse([cx - hw * 1.12, cy - hh * 1.05, cx + hw * 1.12, cy + hh * 1.2], fill=hair, outline=INK, width=lw)
        d.rectangle([cx - hw * 1.12, cy, cx + hw * 1.12, cy + hh * 1.15], fill=hair)
        d.line([(cx - hw * 1.12, cy), (cx - hw * 1.12, cy + hh * 1.15)], fill=INK, width=lw)
        d.line([(cx + hw * 1.12, cy), (cx + hw * 1.12, cy + hh * 1.15)], fill=INK, width=lw)
    d.ellipse([cx - hw, cy - hh, cx + hw, cy + hh * 1.02], fill=head_col, outline=INK, width=lw)
    if gender == "f":
        d.chord([cx - hw * 1.02, cy - hh * 1.06, cx + hw * 1.02, cy + hh * 0.1], 180, 360, fill=(90, 55, 35), outline=INK, width=lw)
    # 볼터치
    for sg in (-1, 1):
        d.ellipse([cx + sg * 78 * s - 18 * s, cy + 30 * s - 10 * s, cx + sg * 78 * s + 18 * s, cy + 30 * s + 10 * s], fill=(240, 120, 100))

    # 얼굴
    ex = 48 * s
    ey = cy - 5 * s
    er = 13 * s
    if emotion == "happy":
        for sg in (-1, 1):
            d.arc([cx + sg * ex - 16 * s, ey - 10 * s, cx + sg * ex + 16 * s, ey + 16 * s], 200, 340, fill=INK, width=lw)
    elif emotion == "shock":
        for sg in (-1, 1):
            d.ellipse([cx + sg * ex - 15 * s, ey - 15 * s, cx + sg * ex + 15 * s, ey + 15 * s], fill=WHITE, outline=INK, width=lw // 2)
            d.ellipse([cx + sg * ex - 5 * s, ey - 5 * s, cx + sg * ex + 5 * s, ey + 5 * s], fill=INK)
    elif emotion == "smug":
        for sg in (-1, 1):
            d.line([(cx + sg * ex - 14 * s, ey + 2 * s), (cx + sg * ex + 14 * s, ey + 2 * s)], fill=INK, width=lw)
    else:
        for sg in (-1, 1):
            d.ellipse([cx + sg * ex - er, ey - er, cx + sg * ex + er, ey + er], fill=INK)
    # 눈썹
    by = ey - 48 * s
    for sg in (-1, 1):
        if emotion in ("worried", "sad"):  # 안쪽 끝이 올라간 눈썹
            d.line([(cx + sg * ex - 20 * s, by + (10 if sg < 0 else -4) * s), (cx + sg * ex + 20 * s, by + (-4 if sg < 0 else 10) * s)], fill=INK, width=lw)
        elif emotion == "angry":  # 안쪽 끝이 내려간 눈썹
            d.line([(cx + sg * ex - 20 * s, by + (-4 if sg < 0 else 12) * s), (cx + sg * ex + 20 * s, by + (12 if sg < 0 else -4) * s)], fill=INK, width=lw)
        elif emotion in ("smug", "think"):
            d.line([(cx + sg * ex - 20 * s, by + (12 if sg < 0 else -2) * s), (cx + sg * ex + 20 * s, by + (-2 if sg < 0 else 12) * s)], fill=INK, width=lw)
        elif emotion == "shock":
            d.arc([cx + sg * ex - 22 * s, by - 18 * s, cx + sg * ex + 22 * s, by + 8 * s], 200, 340, fill=INK, width=lw)
        else:
            d.line([(cx + sg * ex - 20 * s, by), (cx + sg * ex + 20 * s, by)], fill=INK, width=lw)
    # 입
    my = cy + 58 * s
    if emotion == "happy":
        d.chord([cx - 38 * s, my - 22 * s, cx + 38 * s, my + 28 * s], 0, 180, fill=(200, 60, 60), outline=INK, width=lw // 2)
    elif emotion == "shock":
        d.ellipse([cx - 16 * s, my - 14 * s, cx + 16 * s, my + 22 * s], fill=(120, 30, 30), outline=INK, width=lw // 2)
    elif emotion in ("worried", "sad", "angry"):
        d.arc([cx - 28 * s, my, cx + 28 * s, my + 30 * s], 200, 340, fill=INK, width=lw)
    elif emotion == "smug":
        d.arc([cx - 34 * s, my - 22 * s, cx + 30 * s, my + 12 * s], 20, 150, fill=INK, width=lw)
    elif emotion == "think":
        d.line([(cx - 18 * s, my + 6 * s), (cx + 22 * s, my)], fill=INK, width=lw)
    else:
        d.arc([cx - 26 * s, my - 14 * s, cx + 26 * s, my + 14 * s], 20, 160, fill=INK, width=lw)
    # 감정 기호
    if emotion in ("worried", "shock"):
        sx, sy = cx + hw * 0.95, cy - hh * 0.55
        d.polygon([(sx, sy - 26 * s), (sx - 14 * s, sy + 8 * s), (sx + 14 * s, sy + 8 * s)], fill=(120, 190, 240))
        d.ellipse([sx - 14 * s, sy - 4 * s, sx + 14 * s, sy + 22 * s], fill=(120, 190, 240))
    if emotion == "think":
        f = font("black", int(70 * s))
        d.text((cx + hw * 1.1, cy - hh * 1.1), "?", font=f, fill=INK, anchor="mm")
    if emotion == "happy":
        for k, (dx, dy) in enumerate([(-1.25, -0.9), (1.25, -0.75)]):
            star(d, cx + dx * hw, cy + dy * hh, 18 * s, GOLD)


def star(d, x, y, r, fill):
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y - rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=INK)


# ───────────────────────── 아이콘 ─────────────────────────

def icon(img: Image.Image, kind: str, cx: float, cy: float, size: float, text: str | None = None, color=None) -> None:
    d = ImageDraw.Draw(img)
    s = size / 200
    lw = max(3, int(7 * s))
    if kind == "coin":
        d.ellipse([cx - 100 * s, cy - 100 * s, cx + 100 * s, cy + 100 * s], fill=GOLD, outline=INK, width=lw)
        d.ellipse([cx - 75 * s, cy - 75 * s, cx + 75 * s, cy + 75 * s], outline=(200, 140, 10), width=lw)
        draw_text(d, (cx, cy), text or "₩", font("black", int(90 * s)), fill=(150, 95, 0))
    elif kind == "house":
        c = color or (232, 120, 80)
        d.polygon([(cx, cy - 110 * s), (cx - 120 * s, cy - 10 * s), (cx + 120 * s, cy - 10 * s)], fill=c, outline=INK)
        d.rectangle([cx - 90 * s, cy - 10 * s, cx + 90 * s, cy + 100 * s], fill=WHITE, outline=INK, width=lw)
        d.rectangle([cx - 25 * s, cy + 30 * s, cx + 25 * s, cy + 100 * s], fill=(150, 100, 60), outline=INK, width=lw // 2)
        if text:
            draw_text(d, (cx, cy - 45 * s), text, font("black", int(42 * s)), fill=WHITE, stroke=max(2, lw // 2))
    elif kind == "calendar":
        rounded(d, [cx - 100 * s, cy - 90 * s, cx + 100 * s, cy + 100 * s], int(18 * s), fill=WHITE, outline=INK, width=lw)
        d.rectangle([cx - 97 * s, cy - 87 * s, cx + 97 * s, cy - 40 * s], fill=color or RED)
        for sg in (-1, 1):
            d.rounded_rectangle([cx + sg * 55 * s - 8 * s, cy - 110 * s, cx + sg * 55 * s + 8 * s, cy - 65 * s], radius=int(6 * s), fill=(200, 200, 200), outline=INK, width=lw // 2)
        draw_text(d, (cx, cy + 32 * s), text or "", font("black", int(64 * s)), fill=INK)
    elif kind in ("arrow_up", "arrow_down"):
        c = color or (RED if kind == "arrow_up" else BLUE)
        sg = -1 if kind == "arrow_up" else 1
        pts = [(cx, cy + sg * 110 * s), (cx - 85 * s, cy + sg * 10 * s), (cx - 35 * s, cy + sg * 10 * s), (cx - 35 * s, cy - sg * 100 * s),
               (cx + 35 * s, cy - sg * 100 * s), (cx + 35 * s, cy + sg * 10 * s), (cx + 85 * s, cy + sg * 10 * s)]
        d.polygon(pts, fill=c, outline=INK)
    elif kind == "bag":
        d.ellipse([cx - 95 * s, cy - 50 * s, cx + 95 * s, cy + 110 * s], fill=(214, 170, 90), outline=INK, width=lw)
        d.polygon([(cx - 40 * s, cy - 50 * s), (cx + 40 * s, cy - 50 * s), (cx + 60 * s, cy - 100 * s), (cx - 60 * s, cy - 100 * s)], fill=(214, 170, 90), outline=INK)
        if color:  # 강조형: 지정 색 + 검은 외곽선 (썸네일용)
            draw_text(d, (cx, cy + 30 * s), text or "₩", font("black", int(60 * s)), fill=color, stroke=max(3, int(8 * s)), stroke_fill=INK)
        else:
            draw_text(d, (cx, cy + 30 * s), text or "₩", font("black", int(56 * s)), fill=(110, 70, 20))
    elif kind == "doc":
        d.rectangle([cx - 80 * s, cy - 105 * s, cx + 80 * s, cy + 105 * s], fill=WHITE, outline=INK, width=lw)
        for i in range(5):
            d.line([(cx - 55 * s, cy - 65 * s + i * 30 * s), (cx + 55 * s, cy - 65 * s + i * 30 * s)], fill=(170, 170, 170), width=lw // 2)
        if text:
            d.rectangle([cx - 70 * s, cy + 40 * s, cx + 70 * s, cy + 90 * s], outline=RED, width=lw)
            draw_text(d, (cx, cy + 65 * s), text, font("black", int(34 * s)), fill=RED)
    elif kind == "lock":
        d.arc([cx - 60 * s, cy - 120 * s, cx + 60 * s, cy + 10 * s], 180, 360, fill=INK, width=int(22 * s))
        rounded(d, [cx - 95 * s, cy - 50 * s, cx + 95 * s, cy + 100 * s], int(18 * s), fill=GOLD, outline=INK, width=lw)
        d.ellipse([cx - 15 * s, cy, cx + 15 * s, cy + 30 * s], fill=INK)
    elif kind == "building":
        c = color or (120, 140, 170)
        d.rectangle([cx - 70 * s, cy - 120 * s, cx + 70 * s, cy + 110 * s], fill=c, outline=INK, width=lw)
        for r in range(5):
            for col in range(3):
                x0 = cx - 50 * s + col * 38 * s
                y0 = cy - 100 * s + r * 40 * s
                d.rectangle([x0, y0, x0 + 22 * s, y0 + 24 * s], fill=(250, 230, 150))
        if text:
            draw_text(d, (cx, cy + 140 * s), text, font("black", int(36 * s)), fill=INK)
    elif kind == "chart_up" or kind == "chart_down":
        rounded(d, [cx - 110 * s, cy - 90 * s, cx + 110 * s, cy + 90 * s], int(14 * s), fill=WHITE, outline=INK, width=lw)
        pts = [(-80, 50), (-40, 20), (0, 35), (40, -10), (80, -55)] if kind == "chart_up" else [(-80, -55), (-40, -20), (0, -30), (40, 15), (80, 55)]
        d.line([(cx + x * s, cy + y * s) for x, y in pts], fill=RED if kind == "chart_up" else BLUE, width=int(10 * s), joint="curve")
    elif kind == "phone":
        rounded(d, [cx - 60 * s, cy - 110 * s, cx + 60 * s, cy + 110 * s], int(20 * s), fill=(40, 40, 46), outline=INK, width=lw)
        d.rectangle([cx - 50 * s, cy - 92 * s, cx + 50 * s, cy + 85 * s], fill=(235, 245, 255))
        if text:
            draw_text(d, (cx, cy), text, font("black", int(30 * s)), fill=INK)
    elif kind == "won":
        draw_text(d, (cx, cy), text or "₩", font("black", int(170 * s)), fill=color or GREEN, stroke=lw, stroke_fill=INK)
    elif kind == "flag_kr":
        d.rectangle([cx - 110 * s, cy - 75 * s, cx + 110 * s, cy + 75 * s], fill=WHITE, outline=INK, width=lw)
        r = 40 * s  # 태극: 위 빨강·아래 파랑, S자 경계
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=RED)
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 180, fill=BLUE)
        d.ellipse([cx - r, cy - r / 2, cx, cy + r / 2], fill=RED)
        d.ellipse([cx, cy - r / 2, cx + r, cy + r / 2], fill=BLUE)
        # 4괘 (건곤감리): 대각선 네 모서리에 검은 막대 3줄 (가운데가 끊긴 줄 포함)
        import math as _m
        patterns = {(-1, -1): "111", (1, 1): "000", (1, -1): "010", (-1, 1): "101"}  # 1=긴 막대, 0=끊긴 막대
        for (sx_, sy_), pat in patterns.items():
            ang = _m.atan2(sy_, sx_)
            ux, uy = _m.cos(ang), _m.sin(ang)          # 중심→모서리 방향
            px_, py_ = -uy, ux                          # 막대 방향(수직)
            for k, bit in enumerate(pat):
                dist = (52 + k * 11) * s
                mx, my = cx + ux * dist, cy + uy * dist
                half = 15 * s
                if bit == "1":
                    segs = [(-half, half)]
                else:
                    segs = [(-half, -3 * s), (3 * s, half)]
                for a0, a1 in segs:
                    d.line([(mx + px_ * a0, my + py_ * a0), (mx + px_ * a1, my + py_ * a1)], fill=INK, width=max(2, int(7 * s)))
    elif kind == "flag_us":
        d.rectangle([cx - 110 * s, cy - 75 * s, cx + 110 * s, cy + 75 * s], fill=WHITE, outline=INK, width=lw)
        for i in range(7):
            y0 = cy - 75 * s + i * 150 * s / 6.5
            if i % 2 == 0:
                d.rectangle([cx - 107 * s, y0, cx + 107 * s, y0 + 150 * s / 13], fill=RED)
        d.rectangle([cx - 107 * s, cy - 72 * s, cx - 15 * s, cy], fill=(40, 60, 140))
    else:
        raise ValueError(f"알 수 없는 아이콘: {kind}")
