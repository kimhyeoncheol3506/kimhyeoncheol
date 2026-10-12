"""바이럴 썸네일 생성기.

벤치마킹 썸네일(경제학똑똑)에서 뽑은 공식
- 화면 중앙 큰 캐릭터(표정으로 감정 전달) + 좌우에 핵심 숫자/아이콘 2개 + 둘을 잇는 화살표
- 하단 1/3: 2줄 굵은 문구 (1줄 노랑, 2줄 빨강/흰색), 두꺼운 검은 외곽선, 마지막에 '?' 등 긴장 요소
- 배경: 진한 그라데이션 + 도시 실루엣 + 차트 캔들 (경제 맥락)
- 제목 문장을 그대로 반복하지 않고 '궁금증'만 남긴다
"""
from __future__ import annotations

import random

from PIL import Image, ImageDraw, ImageFilter

from .draw import GOLD, INK, RED, WHITE, YELLOW, draw_text, fit_font, font, hex2rgb, icon, mascot, vgradient

THEMES = {
    "blue": ((10, 18, 60), (60, 30, 110)),
    "red": ((60, 8, 18), (130, 30, 40)),
    "green": ((6, 40, 30), (20, 90, 70)),
    "gold": ((50, 30, 5), (120, 80, 10)),
    "dark": ((8, 8, 14), (40, 40, 60)),
}


def _background(w: int, h: int, theme: str, seed: int) -> Image.Image:
    top, bot = THEMES.get(theme, THEMES["blue"])
    img = vgradient(w, h, top, bot)
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(seed)
    # 캔들 차트 (오른쪽 위로 상승)
    x = w * 0.05
    base = h * 0.62
    while x < w * 0.98:
        trend = (x / w) * h * 0.45
        o = base - trend + rnd.uniform(-30, 30)
        c = o + rnd.uniform(-45, 35)
        up = c < o
        col = (60, 220, 120, 120) if up else (240, 70, 70, 120)
        d.line([(x + 7, min(o, c) - rnd.uniform(5, 30)), (x + 7, max(o, c) + rnd.uniform(5, 30))], fill=col, width=3)
        d.rectangle([x, min(o, c), x + 14, max(o, c) + 2], fill=col)
        x += 26
    # 도시 실루엣
    x = 0
    while x < w:
        bw = rnd.randint(40, 110)
        bh = rnd.randint(int(h * 0.15), int(h * 0.42))
        d.rectangle([x, h * 0.70 - bh, x + bw, h], fill=(5, 8, 25, 230))
        for wy in range(int(h * 0.70 - bh) + 10, int(h * 0.70), 22):
            for wx in range(x + 8, x + bw - 8, 18):
                if rnd.random() < 0.35:
                    d.rectangle([wx, wy, wx + 7, wy + 10], fill=(255, 210, 120, 160))
        x += bw + rnd.randint(2, 10)
    return img


def _glow(img: Image.Image, cx: float, cy: float, r: float, color=(255, 200, 80)) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (170,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.45))
    img.paste(layer, (0, 0), layer)


def make_thumbnail(spec: dict, out: str, size=(1280, 720), seed: int = 1) -> None:
    w, h = size
    vertical = h > w
    img = _background(w, h, spec.get("theme", "blue"), seed).convert("RGBA")
    S = w / 1280
    mcx = w / 2
    mcy = h * (0.34 if not vertical else 0.36)
    _glow(img, mcx, mcy + 40 * S, 300 * S)
    if spec.get("money_rain"):  # 떨어지는 지폐·동전 (가운데 캐릭터·하단 문구 영역은 피함)
        rnd = random.Random(seed + 7)
        rgb = img.convert("RGB")
        d0 = ImageDraw.Draw(rgb)
        for _ in range(int(spec.get("money_rain", 14))):
            for _try in range(30):
                x, y = rnd.uniform(0.03, 0.97) * w, rnd.uniform(0.02, 0.62 if not vertical else 0.66) * h
                if abs(x - w / 2) > w * 0.16:
                    break
            if rnd.random() < 0.5:
                icon(rgb, "coin", x, y, rnd.uniform(60, 95) * S)
            else:
                bw, bh = rnd.uniform(80, 120) * S, rnd.uniform(40, 55) * S
                bill = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bill)
                bd.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=int(6 * S), fill=(110, 190, 120), outline=INK, width=max(2, int(3 * S)))
                draw_text(bd, (bw / 2, bh / 2), "₩", font("black", int(bh * 0.6)), fill=(30, 90, 50))
                bill = bill.rotate(rnd.uniform(-35, 35), expand=True)
                rgb.paste(bill, (int(x - bill.width / 2), int(y - bill.height / 2)), bill)
        img = rgb.convert("RGBA")
    for side in ("left", "right"):
        it = spec.get(side)
        if not it:
            continue
        x = w * (0.17 if side == "left" else 0.83) if not vertical else w * (0.22 if side == "left" else 0.78)
        y = h * (0.40 if not vertical else 0.20)
        _glow(img, x, y, 170 * S, (255, 255, 255))
        rgb = img.convert("RGB")
        icon(rgb, it["kind"], x, y, it.get("size", 330) * S, it.get("text"), hex2rgb(it["color"]) if it.get("color") else None)
        img = rgb.convert("RGBA")
    if spec.get("arrow", True) and spec.get("left") and spec.get("right"):
        d = ImageDraw.Draw(img)
        y0 = h * (0.13 if not vertical else 0.08)
        pts = [(w * 0.24 + t * w * 0.5, y0 - (1 - (2 * t - 1) ** 2) * 70 * S) for t in [i / 30 for i in range(31)]]
        d.line(pts, fill=INK, width=int(26 * S), joint="curve")
        d.line(pts, fill=GOLD, width=int(16 * S), joint="curve")
        ex, ey = pts[-1]
        d.polygon([(ex + 30 * S, ey + 10 * S), (ex - 18 * S, ey - 30 * S), (ex - 18 * S, ey + 40 * S)], fill=GOLD, outline=INK)
    rgb = img.convert("RGB")
    mascot(rgb, mcx, mcy, (0.95 if not vertical else 1.5) * S, spec.get("emotion", "smug"), spec.get("gender", "m"), spec.get("pose", "hands"))
    img = rgb.convert("RGBA")

    # 하단 어두운 띠 + 문구
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    top = h * (0.60 if not vertical else 0.66)
    for y in range(int(top), h):
        a = int(min(235, (y - top) / (h * 0.10) * 235))
        bd.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, band)
    d = ImageDraw.Draw(img)
    l1, l2 = spec.get("line1", ""), spec.get("line2", "")
    c2 = {"red": (255, 80, 90), "white": WHITE, "yellow": YELLOW}.get(spec.get("line2_color", "red"), (255, 80, 90))
    maxw = int(w * 0.94)
    f1 = fit_font("thumb", int((118 if not vertical else 150) * S), l1, maxw)
    f2 = fit_font("thumb", int((118 if not vertical else 150) * S), l2, maxw)
    y1 = h * (0.745 if not vertical else 0.79)
    y2 = h * (0.895 if not vertical else 0.89)
    draw_text(d, (w / 2, y1), l1, f1, fill=YELLOW, stroke=int(12 * S), stroke_fill=(0, 0, 0))
    if l2:
        draw_text(d, (w / 2, y2), l2, f2, fill=c2, stroke=int(12 * S), stroke_fill=(0, 0, 0))
    if spec.get("badge"):
        f = fit_font("thumb", int(56 * S), spec["badge"], int(w * 0.3))
        bw = f.getbbox(spec["badge"])[2] + 50 * S
        d.rounded_rectangle([30 * S, 30 * S, 30 * S + bw, 120 * S], radius=int(16 * S), fill=RED, outline=WHITE, width=int(5 * S))
        draw_text(d, (30 * S + bw / 2, 75 * S), spec["badge"], f, fill=WHITE)
    img.convert("RGB").save(out, quality=95)
