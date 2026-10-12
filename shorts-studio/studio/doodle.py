"""인생녹음중 스타일의 콩 캐릭터 + 소품 낙서 (모두 코드로 직접 그림 → 저작권 문제 없음)."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from .core import INK, WHITE, YELLOW, hand_line, lerp

LW = 7  # 기본 선 두께


def bean(draw: ImageDraw.ImageDraw, cx, base_y, h, gender="m", expr="neutral",
         talking=0.0, t=0.0, look=0.0, arm="down", seed=1):
    """콩 캐릭터. base_y=발끝, h=키. talking 0~1 (입 벌림), look -1~1 (시선)."""
    w = h * 0.52
    bob = math.sin(t * 2 * math.pi * 0.8 + seed) * h * 0.008
    top = base_y - h + bob
    body = (cx - w / 2, top, cx + w / 2, base_y + bob)
    draw.rounded_rectangle(body, radius=w / 2, fill=WHITE, outline=INK, width=LW)
    hy = top + h * 0.33  # 눈 높이
    ex = w * 0.17
    er = h * 0.034
    for s in (-1, 1):
        x = cx + s * ex + look * w * 0.06
        if expr == "happy":
            draw.arc((x - er * 1.4, hy - er, x + er * 1.4, hy + er * 1.6), 200, 340, fill=INK, width=LW - 2)
        elif expr == "shock":
            draw.ellipse((x - er * 1.3, hy - er * 1.3, x + er * 1.3, hy + er * 1.3), fill=WHITE, outline=INK, width=LW - 3)
            draw.ellipse((x - er * 0.35, hy - er * 0.35, x + er * 0.35, hy + er * 0.35), fill=INK)
        elif expr == "meh":
            draw.line((x - er * 1.2, hy, x + er * 1.2, hy), fill=INK, width=LW - 2)
        elif expr == "sad":  # 감은 눈(∩) + 눈물
            draw.arc((x - er * 1.4, hy - er * 0.6, x + er * 1.4, hy + er * 1.8), 200, 340, fill=INK, width=LW - 2)
            tx, ty = x + s * er * 0.6, hy + er * 1.6 + (t * 60 % 1) * er * 2.5
            draw.ellipse((tx - er * 0.55, ty - er * 0.2, tx + er * 0.55, ty + er * 1.2), fill=(110, 170, 235), outline=INK, width=2)
        else:
            draw.ellipse((x - er, hy - er, x + er, hy + er), fill=WHITE, outline=INK, width=LW - 3)
            px = x + look * er * 0.4
            draw.ellipse((px - er * 0.42, hy - er * 0.42, px + er * 0.42, hy + er * 0.42), fill=INK)
    if expr == "sad":  # 눈썹: 안쪽이 올라간 八자
        for s in (-1, 1):
            x = cx + s * ex + look * w * 0.06
            draw.line((x - s * er * 1.0, hy - er * 2.9, x + s * er * 1.6, hy - er * 2.0), fill=INK, width=LW - 1)
    if expr in ("angry", "smug"):  # 눈썹: angry=안쪽으로 내려감, smug=한쪽만 치켜뜸
        for s in (-1, 1):
            x = cx + s * ex + look * w * 0.06
            if expr == "angry":
                draw.line((x + s * er * 1.7, hy - er * 2.9, x - s * er * 0.8, hy - er * 1.4), fill=INK, width=LW)
            elif s == 1:
                draw.arc((x - er * 1.6, hy - er * 3.2, x + er * 1.6, hy - er * 1.4), 200, 340, fill=INK, width=LW - 2)
    if gender == "mom":  # 안경
        for s in (-1, 1):
            x = cx + s * ex + look * w * 0.06
            draw.ellipse((x - er * 2.0, hy - er * 1.8, x + er * 2.0, hy + er * 1.8), outline=INK, width=LW - 3)
        draw.line((cx - ex + er * 2.0 + look * w * 0.06, hy, cx + ex - er * 2.0 + look * w * 0.06, hy), fill=INK, width=LW - 3)
    my = hy + h * 0.1
    mw = w * 0.13
    mx = cx + look * w * 0.05
    if talking > 0.15:
        oh = h * 0.05 * talking
        draw.ellipse((mx - mw * 0.7, my - oh / 2, mx + mw * 0.7, my + oh), fill=INK)
    elif expr == "happy":
        draw.arc((mx - mw, my - mw * 0.8, mx + mw, my + mw * 0.6), 20, 160, fill=INK, width=LW - 2)
    elif expr == "shock":
        draw.ellipse((mx - mw * 0.45, my - mw * 0.3, mx + mw * 0.45, my + mw * 0.7), outline=INK, width=LW - 3)
    elif expr in ("angry", "sad"):
        draw.arc((mx - mw, my, mx + mw, my + mw * 1.4), 200, 340, fill=INK, width=LW - 2)
    elif expr in ("smirk", "smug"):
        draw.arc((mx - mw, my - mw, mx + mw * 0.6, my + mw * 0.3), 30, 120, fill=INK, width=LW - 2)
    else:
        draw.line((mx - mw * 0.6, my, mx + mw * 0.6, my), fill=INK, width=LW - 2)
    # 머리카락
    if gender == "mom":  # 뽀글 파마
        for i in range(11):
            ang = math.pi * (0.05 + 0.9 * i / 10)
            px = cx - math.cos(ang) * w * 0.52
            py = top + h * 0.16 - math.sin(ang) * h * 0.17
            r = w * 0.11
            draw.ellipse((px - r, py - r, px + r, py + r), fill=(150, 150, 158), outline=INK, width=LW - 2)
    elif gender == "gm":  # 할머니: 흰 쪽머리
        r = w * 0.17
        draw.ellipse((cx - r, top - r * 1.3, cx + r, top + r * 0.7), fill=(225, 225, 230), outline=INK, width=LW - 2)
        for s2 in (-1, 1):
            draw.arc((cx + s2 * w * 0.08 - w * 0.4, top + h * 0.0, cx + s2 * w * 0.08 + w * 0.4, top + h * 0.22),
                     200 if s2 < 0 else 270, 270 if s2 < 0 else 340, fill=(160, 160, 168), width=LW - 1)
    elif gender == "gp":  # 할아버지: 대머리 + 옆머리 흰 털
        for s2 in (-1, 1):
            for k in range(3):
                bx = cx + s2 * w * (0.44 + 0.02 * k)
                by = top + h * (0.14 + 0.04 * k)
                draw.ellipse((bx - w * 0.07, by - w * 0.05, bx + w * 0.07, by + w * 0.05), fill=(230, 230, 235), outline=INK, width=2)
        hand_line(draw, [(cx - w * 0.12, top + h * 0.06), (cx + w * 0.12, top + h * 0.06)], INK, LW - 3, 0.6, seed)
    elif gender == "m":
        for i, dx in enumerate((-0.14, -0.04, 0.06, 0.15)):
            x0 = cx + dx * w
            hand_line(draw, [(x0, top + h * 0.035), (x0 + w * 0.05, top - h * 0.06)], INK, LW - 2, 0.8, seed + i)
    else:
        hl = [(cx - w * 0.05, top + h * 0.01), (cx - w * 0.35, top + h * 0.08), (cx - w * 0.62, top + h * 0.32),
              (cx - w * 0.85, top + h * 0.38)]
        hand_line(draw, hl, INK, LW - 2, 1.0, seed)
        hr = [(cx + w * 0.02, top + h * 0.01), (cx + w * 0.36, top + h * 0.1), (cx + w * 0.6, top + h * 0.3),
              (cx + w * 0.82, top + h * 0.36)]
        hand_line(draw, hr, INK, LW - 2, 1.0, seed + 3)
        hand_line(draw, [(cx - w * 0.1, top - h * 0.03), (cx + w * 0.08, top + h * 0.03)], INK, LW - 2, 0.5, seed + 5)
        hand_line(draw, [(cx + w * 0.1, top - h * 0.03), (cx - w * 0.06, top + h * 0.03)], INK, LW - 2, 0.5, seed + 6)
    # 팔
    ay = top + h * 0.58
    for s in (-1, 1):
        sx = cx + s * w * 0.49
        if arm == "up" and s == 1:
            wave = math.sin(t * 6) * h * 0.02
            pts = [(sx, ay), (sx + w * 0.3, ay - h * 0.18 + wave), (sx + w * 0.34, ay - h * 0.3 + wave)]
        elif arm == "point" and s == 1:
            pts = [(sx, ay), (sx + w * 0.45, ay - h * 0.04)]
        elif arm == "think" and s == 1:
            pts = [(sx, ay), (sx - w * 0.1, ay - h * 0.12), (cx + w * 0.12, hy + h * 0.16)]
        else:
            pts = [(sx, ay), (sx + s * w * 0.13, ay + h * 0.11), (sx + s * w * 0.11, ay + h * 0.19)]
        hand_line(draw, pts, INK, LW - 1, 0.6, seed + 10 + s)


# ---------- 소품 ----------
def sparkle(draw, cx, cy, r, fill=(255, 196, 60), t=0.0):
    k = 1 + 0.15 * math.sin(t * 5 + cx)
    r *= k
    pts = []
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill, outline=INK)


def money_stack(draw, x, y, w, n=3):
    green, light = (88, 200, 120), (190, 240, 200)
    h = w * 0.32
    for i in range(n):
        yy = y - i * h * 0.55
        draw.rounded_rectangle((x, yy, x + w, yy + h), 8, fill=green, outline=INK, width=4)
        draw.rectangle((x + w * 0.35, yy + 4, x + w * 0.5, yy + h - 4), fill=light)


def heart(draw, cx, cy, r, fill=(240, 80, 90)):
    pts = []
    for i in range(60):
        a = i / 60 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * r / 16, cy + y * r / 16))
    draw.polygon(pts, fill=fill, outline=INK)
    draw.line(pts + [pts[0]], fill=INK, width=5)


def ticket(draw, cx, cy, w, fill=(255, 214, 120)):
    h = w * 0.5
    x0, y0 = cx - w / 2, cy - h / 2
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), 12, fill=fill, outline=INK, width=5)
    for s in (-1, 1):
        draw.ellipse((cx + s * w / 2 - h * 0.15, cy - h * 0.15, cx + s * w / 2 + h * 0.15, cy + h * 0.15),
                     fill=(250, 249, 246), outline=INK, width=5)
    for i in range(5):
        yy = y0 + h * 0.15 + i * h * 0.15
        draw.line((cx + w * 0.22, yy, cx + w * 0.22, yy + h * 0.07), fill=INK, width=4)


def chat_bubble_icon(draw, cx, cy, r):
    draw.ellipse((cx - r, cy - r * 0.75, cx + r, cy + r * 0.75), fill=WHITE, outline=INK, width=5)
    draw.polygon([(cx - r * 0.4, cy + r * 0.6), (cx - r * 0.7, cy + r * 1.05), (cx - r * 0.05, cy + r * 0.7)],
                 fill=WHITE, outline=INK)
    for i in (-1, 0, 1):
        draw.ellipse((cx + i * r * 0.4 - 7, cy - 7, cx + i * r * 0.4 + 7, cy + 7), fill=INK)


def clock(draw, cx, cy, r, t=0.0):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=INK, width=6)
    a1 = -math.pi / 2 + t * 0.6
    a2 = -math.pi / 2 + t * 4
    draw.line((cx, cy, cx + r * 0.5 * math.cos(a1), cy + r * 0.5 * math.sin(a1)), fill=INK, width=7)
    draw.line((cx, cy, cx + r * 0.78 * math.cos(a2), cy + r * 0.78 * math.sin(a2)), fill=(229, 57, 53), width=5)


def soju(draw, cx, base_y, h):
    w = h * 0.32
    green = (70, 170, 110)
    draw.rounded_rectangle((cx - w / 2, base_y - h * 0.68, cx + w / 2, base_y), 14, fill=green, outline=INK, width=5)
    draw.polygon([(cx - w / 2, base_y - h * 0.66), (cx - w * 0.17, base_y - h * 0.88), (cx + w * 0.17, base_y - h * 0.88),
                  (cx + w / 2, base_y - h * 0.66)], fill=green, outline=INK)
    draw.rectangle((cx - w * 0.17, base_y - h, cx + w * 0.17, base_y - h * 0.86), fill=green, outline=INK, width=5)
    draw.rectangle((cx - w * 0.38, base_y - h * 0.48, cx + w * 0.38, base_y - h * 0.22), fill=WHITE, outline=INK, width=4)
    # 잔
    gx = cx + w * 1.1
    draw.polygon([(gx - w * 0.3, base_y - h * 0.3), (gx + w * 0.3, base_y - h * 0.3), (gx + w * 0.22, base_y),
                  (gx - w * 0.22, base_y)], fill=(230, 245, 250), outline=INK)
    draw.line([(gx - w * 0.3, base_y - h * 0.3), (gx + w * 0.3, base_y - h * 0.3), (gx + w * 0.22, base_y),
               (gx - w * 0.22, base_y), (gx - w * 0.3, base_y - h * 0.3)], fill=INK, width=5)


def phone(draw, cx, cy, h):
    w = h * 0.5
    draw.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 16, fill=(40, 40, 46), outline=INK, width=5)
    draw.rounded_rectangle((cx - w / 2 + 10, cy - h / 2 + 16, cx + w / 2 - 10, cy + h / 2 - 16), 8, fill=(170, 210, 255))


def check_box(draw, x, y, s, checked=True, progress=1.0):
    draw.rectangle((x, y, x + s, y + s), outline=INK, width=5)
    if checked and progress > 0:
        p1, p2, p3 = (x + s * 0.18, y + s * 0.5), (x + s * 0.42, y + s * 0.78), (x + s * 0.95, y - s * 0.1)
        if progress < 0.4:
            q = progress / 0.4
            draw.line([p1, (lerp(p1[0], p2[0], q), lerp(p1[1], p2[1], q))], fill=(229, 57, 53), width=8)
        else:
            q = (progress - 0.4) / 0.6
            draw.line([p1, p2, (lerp(p2[0], p3[0], q), lerp(p2[1], p3[1], q))], fill=(229, 57, 53), width=8, joint="curve")


def speech_bubble(size, text_lines, fnt, tail="left", fill=WHITE):
    """말풍선 RGBA 이미지."""
    from .core import draw_rich_line, strip_markup, ORANGE
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * 1.12)
    tw = max(fnt.getlength(strip_markup(l)) for l in text_lines)
    w = int(tw + 80)
    h = int(lh * len(text_lines) + 56)
    im = Image.new("RGBA", (w + 20, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), 36, fill=fill, outline=INK, width=6)
    tx = 10 + (w * 0.25 if tail == "left" else w * 0.7)
    d.polygon([(tx, 10 + h - 4), (tx + 40, 10 + h - 4), (tx + (0 if tail == "left" else 46), 10 + h + 46)],
              fill=fill)
    d.line([(tx, 10 + h - 1), (tx + (0 if tail == "left" else 46), 10 + h + 46), (tx + 40, 10 + h - 1)],
           fill=INK, width=6, joint="curve")
    for i, l in enumerate(text_lines):
        draw_rich_line(d, (10 + w / 2, 10 + 24 + i * lh), l, fnt, INK, ORANGE)
    return im
