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
    "hook": "Paperlogy-9Black.ttf",       # 썸네일 문구 (요즘 경제 채널형, OFL)
    "hook_xb": "Paperlogy-8ExtraBold.ttf",
    # 요즘 한국 유튜브 썸네일 대표 폰트 (모두 무료·상업 이용 가능) — 영상마다 돌려 쓴다
    "aggro": "SBAggroB.ttf",              # 샌드박스 어그로체 B
    "gmarket": "GmarketSansBold.ttf",     # G마켓 산스 Bold
    "jalnan": "JalnanOTF00.ttf",          # 여기어때 잘난체
    "ssurround": "Cafe24Ssurround.ttf",   # 카페24 써라운드 (OFL)
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


def fit_box(kind: str, size: int, s: str, max_w: float, max_h: float, min_size: int = 12, spacing: float = 1.18) -> ImageFont.FreeTypeFont:
    """여러 줄 텍스트가 (max_w × max_h) 상자 안에 다 들어가도록 글자 크기를 줄인다 (아이콘 속 글자용)."""
    n = len(s.split("\n"))
    while size > min_size and (max(text_w(font(kind, size), line) for line in s.split("\n")) > max_w or n * size * spacing > max_h):
        size = max(min_size, int(size * 0.92))
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
    """(cx, cy)는 얼굴 중심. s=1일 때 얼굴 폭 약 240px.

    v1.11.0 리디자인 (현철님 요청): '개미 같은 사람' — 굵은 윤곽선, 사람 비율(머리카락·귀·목·어깨·소매 팔),
    흰자 있는 눈과 코. 개미 요소는 굵은 더듬이와 캐러멜색 피부로 유지.
    emotion: neutral | happy | worried | shock | smug | sad | think | angry
    pose: normal | point | hands | shrug
    """
    d = ImageDraw.Draw(img)
    lw = max(4, int(11 * s))
    thin = max(3, int(7 * s))
    hw, hh = 112 * s, 122 * s
    skin = (234, 160, 86) if gender == "m" else (242, 174, 106)       # 개미 캐러멜색 피부
    shirt = (190, 222, 245) if gender == "m" else (255, 255, 255)    # 남: 하늘색 셔츠 / 여: 흰 블라우스
    cardi = (186, 138, 86) if gender == "m" else (236, 112, 112)     # 남: 카멜 가디건 / 여: 코랄 가디건
    cardi_dark = tuple(max(0, c - 50) for c in cardi)
    hair = (52, 36, 28) if gender == "m" else (86, 52, 34)

    def limb(pts, w):  # 윤곽선 있는 굵은 소매
        d.line(pts, fill=INK, width=int(w + 2 * lw), joint="curve")
        for p_ in pts:
            r = (w + 2 * lw) / 2
            d.ellipse([p_[0] - r, p_[1] - r, p_[0] + r, p_[1] + r], fill=INK)
        d.line(pts, fill=cardi, width=int(w), joint="curve")
        for p_ in pts[1:-1]:
            r = w / 2
            d.ellipse([p_[0] - r, p_[1] - r, p_[0] + r, p_[1] + r], fill=cardi)

    def hand(x, y):
        r = 25 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=skin, outline=INK, width=thin)
        d.line([(x - 8 * s, y - r + 6 * s), (x - 8 * s, y - 2 * s)], fill=INK, width=max(2, thin // 2))  # 손가락 구분선
        d.line([(x + 6 * s, y - r + 6 * s), (x + 6 * s, y - 2 * s)], fill=INK, width=max(2, thin // 2))

    neck_top = cy + hh * 0.80
    body_top = cy + hh * 1.02
    sh = 165 * s           # 어깨 반폭
    body_bot = body_top + 250 * s
    # ── 팔: 가디건 소매 (몸통 뒤에 먼저 그려 어깨 이음새를 가림) ──
    hands_ = []
    aw = 44 * s
    shL, shR = (cx - sh + 18 * s, body_top + 40 * s), (cx + sh - 18 * s, body_top + 40 * s)
    if pose == "point":
        limb([shR, (cx + 215 * s, body_top - 10 * s), (cx + 250 * s, cy - 40 * s)], aw)
        hands_.append((cx + 252 * s, cy - 58 * s))
        limb([shL, (cx - 200 * s, body_top + 120 * s), (cx - 190 * s, body_top + 200 * s)], aw)
        hands_.append((cx - 190 * s, body_top + 215 * s))
    elif pose == "shrug":
        for sg, sp in ((-1, shL), (1, shR)):
            limb([sp, (cx + sg * 230 * s, body_top + 70 * s), (cx + sg * 262 * s, body_top - 5 * s)], aw)
            hands_.append((cx + sg * 265 * s, body_top - 22 * s))
    elif pose == "hands":  # 만세
        for sg, sp in ((-1, shL), (1, shR)):
            limb([sp, (cx + sg * 215 * s, body_top - 30 * s), (cx + sg * 245 * s, cy - 70 * s)], aw)
            hands_.append((cx + sg * 248 * s, cy - 90 * s))
    else:
        for sg, sp in ((-1, shL), (1, shR)):
            limb([sp, (cx + sg * 200 * s, body_top + 110 * s), (cx + sg * 192 * s, body_top + 200 * s)], aw)
            hands_.append((cx + sg * 192 * s, body_top + 216 * s))

    # ── 몸통: 어깨가 있는 사람 상체 (셔츠 + 열린 가디건) ──
    torso = [(cx - sh, body_top + 40 * s), (cx - sh + 30 * s, body_top), (cx + sh - 30 * s, body_top), (cx + sh, body_top + 40 * s),
             (cx + sh * 0.88, body_bot), (cx - sh * 0.88, body_bot)]
    d.polygon(torso, fill=cardi, outline=INK, width=lw)
    d.polygon([(cx - 50 * s, body_top + 2 * s), (cx + 50 * s, body_top + 2 * s), (cx + 42 * s, body_bot - 4 * s), (cx - 42 * s, body_bot - 4 * s)],
              fill=shirt, outline=INK, width=thin)
    for k in range(3):
        d.ellipse([cx - 6 * s, body_top + (70 + k * 52) * s, cx + 6 * s, body_top + (82 + k * 52) * s], fill=(110, 130, 150))
    # 목
    d.rectangle([cx - 34 * s, neck_top, cx + 34 * s, body_top + 14 * s], fill=skin, outline=INK, width=thin)
    for sg in (-1, 1):  # 셔츠 깃
        d.polygon([(cx, body_top + 46 * s), (cx + sg * 62 * s, body_top - 6 * s), (cx + sg * 58 * s, body_top + 66 * s)], fill=shirt, outline=INK, width=thin)
        d.line([(cx + sg * 52 * s, body_top + 30 * s), (cx + sg * 46 * s, body_bot - 10 * s)], fill=cardi_dark, width=thin)  # 가디건 앞섶
    d.line([(cx - sh * 0.86, body_bot - 30 * s), (cx - 46 * s, body_bot - 30 * s)], fill=cardi_dark, width=thin)
    d.line([(cx + 46 * s, body_bot - 30 * s), (cx + sh * 0.86, body_bot - 30 * s)], fill=cardi_dark, width=thin)
    if label:
        draw_text(d, (cx, body_top + 190 * s), label, font("black", int(32 * s)), fill=WHITE, stroke=max(2, int(3 * s)), stroke_fill=INK)
    else:  # 가슴 ₩ 배지
        bx, by_ = cx + sh * 0.55, body_top + 92 * s
        d.ellipse([bx - 22 * s, by_ - 22 * s, bx + 22 * s, by_ + 22 * s], fill=GOLD, outline=INK, width=thin)
        draw_text(d, (bx, by_), "₩", font("black", int(26 * s)), fill=(150, 95, 0))

    for hx, hy in hands_:
        hand(hx, hy)

    # ── 더듬이 (개미 식별 요소, 굵게) ──
    for sg in (-1, 1):
        x0, y0 = cx + sg * 38 * s, cy - hh * 0.95
        x1, y1 = cx + sg * 100 * s, cy - hh - 92 * s
        d.line([(x0, y0), (cx + sg * 58 * s, cy - hh - 50 * s), (x1, y1)], fill=INK, width=lw, joint="curve")
        d.ellipse([x1 - 19 * s, y1 - 19 * s, x1 + 19 * s, y1 + 19 * s], fill=(60, 38, 26), outline=INK, width=thin)
    if gender == "f":
        rx, ry = cx + 100 * s, cy - hh - 92 * s
        for sg in (-1, 1):
            d.polygon([(rx, ry), (rx + sg * 36 * s, ry - 22 * s), (rx + sg * 36 * s, ry + 22 * s)], fill=(255, 90, 120), outline=INK, width=max(2, thin // 2))

    # ── 머리 (여성은 뒤 머리카락 먼저) ──
    if gender == "f":
        d.rounded_rectangle([cx - hw * 1.18, cy - hh * 0.9, cx + hw * 1.18, cy + hh * 1.25], radius=int(hw), fill=hair, outline=INK, width=lw)
    for sg in (-1, 1):  # 귀
        ex_ = cx + sg * hw * 0.98
        d.ellipse([ex_ - 22 * s, cy - 8 * s, ex_ + 22 * s, cy + 40 * s], fill=skin, outline=INK, width=thin)
    d.ellipse([cx - hw, cy - hh, cx + hw, cy + hh], fill=skin, outline=INK, width=lw)
    # 머리카락 (사람 느낌의 핵심): 남 — 옆 가르마 짧은 머리 / 여 — 앞머리
    if gender == "m":
        top_box = [cx - hw * 1.03, cy - hh * 1.07, cx + hw * 1.03, cy + hh * 0.05]
        d.chord(top_box, 180, 360, fill=hair, outline=INK, width=lw)
        # 옆으로 넘긴 앞머리 (이마는 드러나게)
        d.polygon([(cx - hw * 0.98, cy - hh * 0.50), (cx - hw * 0.35, cy - hh * 0.62), (cx + hw * 0.55, cy - hh * 0.40),
                   (cx + hw * 0.99, cy - hh * 0.48), (cx + hw * 0.99, cy - hh * 0.52), (cx - hw * 0.98, cy - hh * 0.53)], fill=hair)
        d.line([(cx - hw * 0.98, cy - hh * 0.50), (cx - hw * 0.35, cy - hh * 0.62), (cx + hw * 0.55, cy - hh * 0.40), (cx + hw * 0.99, cy - hh * 0.48)],
               fill=INK, width=thin, joint="curve")
        d.line([(cx - hw * 0.05, cy - hh * 1.02), (cx - hw * 0.30, cy - hh * 0.66)], fill=(96, 70, 56), width=thin)  # 가르마
    else:
        d.chord([cx - hw * 1.04, cy - hh * 1.08, cx + hw * 1.04, cy + hh * 0.30], 180, 360, fill=hair, outline=INK, width=lw)
    # 볼터치
    for sg in (-1, 1):
        d.ellipse([cx + sg * 72 * s - 18 * s, cy + 40 * s - 10 * s, cx + sg * 72 * s + 18 * s, cy + 40 * s + 10 * s], fill=(236, 112, 96))

    # ── 얼굴 ──
    ex, ey = 44 * s, cy + 8 * s
    if emotion == "happy":
        for sg in (-1, 1):
            d.arc([cx + sg * ex - 18 * s, ey - 12 * s, cx + sg * ex + 18 * s, ey + 18 * s], 200, 340, fill=INK, width=lw)
    elif emotion == "smug":
        for sg in (-1, 1):
            d.chord([cx + sg * ex - 18 * s, ey - 14 * s, cx + sg * ex + 18 * s, ey + 16 * s], 0, 180, fill=WHITE, outline=INK, width=thin)
            d.ellipse([cx + sg * ex - 7 * s, ey + 1 * s, cx + sg * ex + 7 * s, ey + 13 * s], fill=INK)
            d.line([(cx + sg * ex - 20 * s, ey), (cx + sg * ex + 20 * s, ey)], fill=INK, width=thin)
    else:
        big = 19 if emotion == "shock" else 16
        pup = 6 if emotion == "shock" else 9
        for sg in (-1, 1):
            d.ellipse([cx + sg * ex - big * s, ey - big * 1.15 * s, cx + sg * ex + big * s, ey + big * 1.15 * s], fill=WHITE, outline=INK, width=thin)
            px = cx + sg * ex + (2 if emotion != "think" else 6) * s
            d.ellipse([px - pup * s, ey - pup * s + 2 * s, px + pup * s, ey + pup * s + 2 * s], fill=INK)
    # 눈썹 (굵게)
    by = ey - 40 * s
    bw_ = lw + 2
    for sg in (-1, 1):
        if emotion in ("worried", "sad"):
            d.line([(cx + sg * ex - 22 * s, by + (10 if sg < 0 else -4) * s), (cx + sg * ex + 22 * s, by + (-4 if sg < 0 else 10) * s)], fill=INK, width=bw_)
        elif emotion == "angry":
            d.line([(cx + sg * ex - 22 * s, by + (-4 if sg < 0 else 12) * s), (cx + sg * ex + 22 * s, by + (12 if sg < 0 else -4) * s)], fill=INK, width=bw_)
        elif emotion in ("smug", "think"):
            d.line([(cx + sg * ex - 22 * s, by + (12 if sg < 0 else -2) * s), (cx + sg * ex + 22 * s, by + (-2 if sg < 0 else 12) * s)], fill=INK, width=bw_)
        elif emotion == "shock":
            d.arc([cx + sg * ex - 24 * s, by - 20 * s, cx + sg * ex + 24 * s, by + 8 * s], 200, 340, fill=INK, width=bw_)
        else:
            d.line([(cx + sg * ex - 22 * s, by), (cx + sg * ex + 22 * s, by)], fill=INK, width=bw_)
    # 코
    d.arc([cx - 12 * s, ey + 18 * s, cx + 12 * s, ey + 40 * s], 300, 80, fill=INK, width=thin)
    # 입
    my = cy + 70 * s
    if emotion == "happy":
        d.chord([cx - 36 * s, my - 20 * s, cx + 36 * s, my + 26 * s], 0, 180, fill=(200, 60, 60), outline=INK, width=thin)
        d.chord([cx - 24 * s, my - 2 * s, cx + 24 * s, my + 12 * s], 0, 180, fill=WHITE)
    elif emotion == "shock":
        d.ellipse([cx - 16 * s, my - 12 * s, cx + 16 * s, my + 24 * s], fill=(120, 30, 30), outline=INK, width=thin)
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
        sx, sy = cx + hw * 1.05, cy - hh * 0.45
        d.polygon([(sx, sy - 28 * s), (sx - 15 * s, sy + 8 * s), (sx + 15 * s, sy + 8 * s)], fill=(120, 190, 240), outline=INK)
        d.ellipse([sx - 15 * s, sy - 4 * s, sx + 15 * s, sy + 24 * s], fill=(120, 190, 240), outline=INK)
    if emotion == "think":
        d.text((cx + hw * 1.2, cy - hh * 1.1), "?", font=font("black", int(76 * s)), fill=INK, anchor="mm", stroke_width=max(2, int(3 * s)), stroke_fill=WHITE)
    if emotion == "happy":
        for dx, dy in [(-1.35, -0.9), (1.35, -0.75)]:
            star(d, cx + dx * hw, cy + dy * hh, 20 * s, GOLD)


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
        t = text or "₩"
        draw_text(d, (cx, cy), t, fit_box("black", int(90 * s), t, 120 * s, 110 * s), fill=(150, 95, 0))
    elif kind == "house":
        c = color or (232, 120, 80)
        d.polygon([(cx, cy - 110 * s), (cx - 120 * s, cy - 10 * s), (cx + 120 * s, cy - 10 * s)], fill=c, outline=INK)
        d.rectangle([cx - 90 * s, cy - 10 * s, cx + 90 * s, cy + 100 * s], fill=WHITE, outline=INK, width=lw)
        d.rectangle([cx - 25 * s, cy + 30 * s, cx + 25 * s, cy + 100 * s], fill=(150, 100, 60), outline=INK, width=lw // 2)
        if text:
            draw_text(d, (cx, cy - 40 * s), text, fit_box("black", int(42 * s), text, 110 * s, 50 * s), fill=WHITE, stroke=max(2, lw // 2))
    elif kind == "calendar":
        rounded(d, [cx - 100 * s, cy - 90 * s, cx + 100 * s, cy + 100 * s], int(18 * s), fill=WHITE, outline=INK, width=lw)
        d.rectangle([cx - 97 * s, cy - 87 * s, cx + 97 * s, cy - 40 * s], fill=color or RED)
        for sg in (-1, 1):
            d.rounded_rectangle([cx + sg * 55 * s - 8 * s, cy - 110 * s, cx + sg * 55 * s + 8 * s, cy - 65 * s], radius=int(6 * s), fill=(200, 200, 200), outline=INK, width=lw // 2)
        if text:
            draw_text(d, (cx, cy + 30 * s), text, fit_box("black", int(64 * s), text, 160 * s, 115 * s), fill=INK)
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
            t = text or "₩"
            draw_text(d, (cx, cy + 30 * s), t, fit_box("black", int(60 * s), t, 150 * s, 110 * s), fill=color, stroke=max(3, int(8 * s)), stroke_fill=INK)
        else:
            t = text or "₩"
            draw_text(d, (cx, cy + 30 * s), t, fit_box("black", int(56 * s), t, 150 * s, 110 * s), fill=(110, 70, 20))
    elif kind == "doc":
        d.rectangle([cx - 80 * s, cy - 105 * s, cx + 80 * s, cy + 105 * s], fill=WHITE, outline=INK, width=lw)
        stamp_top = cy + 95 * s
        if text:  # 도장 칸: 글자 줄 수에 맞춰 높이를 정하고, 글자가 칸 안에 다 들어가게 줄인다
            n = len(text.split("\n"))
            f = fit_box("black", int(34 * s), text, 116 * s, (34 if n == 1 else 30 * n) * s * 1.18)
            box_h = n * f.size * 1.18 + 18 * s
            stamp_top = cy + 92 * s - box_h
            d.rectangle([cx - 70 * s, stamp_top, cx + 70 * s, cy + 92 * s], fill=WHITE, outline=RED, width=lw)
            draw_text(d, (cx, (stamp_top + cy + 92 * s) / 2), text, f, fill=RED)
        for i in range(5):  # 줄 무늬는 도장 위쪽에만
            y = cy - 65 * s + i * 30 * s
            if y < stamp_top - 12 * s:
                d.line([(cx - 55 * s, y), (cx + 55 * s, y)], fill=(170, 170, 170), width=lw // 2)
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
            draw_text(d, (cx, cy), text, fit_box("black", int(30 * s), text, 88 * s, 160 * s), fill=INK)
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
