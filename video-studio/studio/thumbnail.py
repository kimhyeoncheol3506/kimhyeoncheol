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

from .draw import fit_box, GOLD, INK, RED, WHITE, YELLOW, draw_text, fit_font, font, hex2rgb, icon, mascot, vgradient

THEMES = {
    "blue": ((10, 18, 60), (60, 30, 110)),
    "red": ((60, 8, 18), (130, 30, 40)),
    "green": ((6, 40, 30), (20, 90, 70)),
    "gold": ((50, 30, 5), (120, 80, 10)),
    "dark": ((8, 8, 14), (40, 40, 60)),
    "gold_soft": ((128, 96, 46), (212, 168, 92)),
    "navy": ((14, 30, 72), (34, 62, 122)),  # 채널(월재스) 배너 색
}
# 썸네일 폰트 순환 목록 (영상마다 다른 대표 폰트, make_video가 project.json에 고정 기록)
THUMB_FONTS = ["thumb", "hook", "aggro", "gmarket", "jalnan", "ssurround"]
NAVY, NAVY2, CH_GOLD = (14, 30, 72), (30, 56, 112), (226, 190, 120)


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


def _office(w: int, h: int, theme: str, seed: int) -> Image.Image:
    """비즈니스 캐주얼 사무실 배경: 큰 창(도시 전망) + 책상 + 노트북 + 커피 + 화분. 테마 색은 창밖 하늘."""
    sky_top, sky_bot = THEMES.get(theme, THEMES["blue"])
    img = Image.new("RGB", (w, h), (232, 222, 206))
    d = ImageDraw.Draw(img, "RGBA")
    S = w / 1280
    rnd = random.Random(seed)
    # 벽 그라데이션
    for y in range(h):
        t = y / h
        lift = 62 if theme.endswith("_soft") else 0  # 옅은 톤
        d.line([(0, y), (w, y)], fill=(int(70 - 30 * t) + lift, int(58 - 25 * t) + lift, int(52 - 22 * t) + lift))
    # 창문 (하늘 + 건물 실루엣)
    wx0, wy0, wx1, wy1 = int(w * 0.03), int(h * 0.04), int(w * 0.97), int(h * 0.70)
    sky = vgradient(wx1 - wx0, wy1 - wy0, sky_top, sky_bot)
    img.paste(sky, (wx0, wy0))
    x = wx0
    while x < wx1:
        bw = rnd.randint(int(50 * S), int(120 * S))
        bh = rnd.randint(int(h * 0.12), int(h * 0.40))
        d.rectangle([x, wy1 - bh, min(wx1, x + bw), wy1], fill=(20, 22, 40, 235))
        for yy in range(int(wy1 - bh) + 10, int(wy1), int(22 * S)):
            for xx in range(x + 8, min(wx1, x + bw) - 8, int(18 * S)):
                if rnd.random() < 0.35:
                    d.rectangle([xx, yy, xx + 7 * S, yy + 10 * S], fill=(255, 214, 130, 170))
        x += bw + rnd.randint(2, 8)
    # 창틀
    for fx in (wx0, (wx0 + wx1) // 2, wx1):
        d.rectangle([fx - 7 * S, wy0, fx + 7 * S, wy1], fill=(235, 230, 220))
    d.rectangle([wx0, wy0 - 7 * S, wx1, wy0 + 7 * S], fill=(235, 230, 220))
    d.rectangle([wx0, wy1 - 7 * S, wx1, wy1 + 7 * S], fill=(235, 230, 220))
    # 책상
    soft = theme.endswith("_soft")
    d.rectangle([0, h * 0.70, w, h], fill=(176, 130, 90) if soft else (150, 104, 66))
    d.rectangle([0, h * 0.70, w, h * 0.72], fill=(146, 104, 70) if soft else (120, 80, 48))
    # 노트북 (오른쪽) — 화면에 상승 차트
    lx, ly = w * 0.70, h * 0.70
    d.polygon([(lx - 120 * S, ly), (lx + 120 * S, ly), (lx + 140 * S, ly + 14 * S), (lx - 140 * S, ly + 14 * S)], fill=(190, 195, 205))
    d.rounded_rectangle([lx - 110 * S, ly - 150 * S, lx + 110 * S, ly - 2 * S], radius=int(8 * S), fill=(40, 44, 56))
    d.rectangle([lx - 98 * S, ly - 138 * S, lx + 98 * S, ly - 14 * S], fill=(235, 245, 240))
    d.line([(lx - 85 * S, ly - 30 * S), (lx - 40 * S, ly - 60 * S), (lx, ly - 50 * S), (lx + 45 * S, ly - 100 * S), (lx + 85 * S, ly - 125 * S)],
           fill=(30, 170, 100), width=int(7 * S), joint="curve")
    # 커피잔 (왼쪽)
    cx_, cy_ = w * 0.08, h * 0.70
    d.rounded_rectangle([cx_ - 30 * S, cy_ - 60 * S, cx_ + 30 * S, cy_], radius=int(8 * S), fill=(250, 250, 248), outline=(60, 60, 60), width=int(3 * S))
    d.arc([cx_ + 18 * S, cy_ - 48 * S, cx_ + 48 * S, cy_ - 18 * S], 270, 90, fill=(60, 60, 60), width=int(5 * S))
    # 화분 (오른쪽 끝)
    px_, py_ = w * 0.93, h * 0.70
    for k in range(5):
        a = -0.9 + k * 0.45
        d.ellipse([px_ + 60 * S * a - 22 * S, py_ - 150 * S + abs(a) * 30 * S, px_ + 60 * S * a + 22 * S, py_ - 70 * S + abs(a) * 30 * S], fill=(60, 150, 80))
    d.polygon([(px_ - 35 * S, py_ - 70 * S), (px_ + 35 * S, py_ - 70 * S), (px_ + 25 * S, py_), (px_ - 25 * S, py_)], fill=(200, 110, 70))
    return img


def _glow(img: Image.Image, cx: float, cy: float, r: float, color=(255, 200, 80)) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (170,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.45))
    img.paste(layer, (0, 0), layer)


def _bottom_text(img, spec, w, h, S, vertical):
    # 하단 어두운 띠 + 문구
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    top = h * (0.60 if not vertical else 0.66)
    for y in range(int(top), h):
        a = int(min(235, (y - top) / (h * 0.10) * 235))
        bd.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    img.alpha_composite(band)
    d = ImageDraw.Draw(img)
    l1, l2 = spec.get("line1", ""), spec.get("line2", "")
    c2 = {"red": (255, 80, 90), "white": WHITE, "yellow": YELLOW}.get(spec.get("line2_color", "red"), (255, 80, 90))
    maxw = int(w * 0.94)
    tf = spec.get("font", "thumb")
    f1 = fit_font(tf, int((118 if not vertical else 150) * S), l1, maxw)
    f2 = fit_font(tf, int((118 if not vertical else 150) * S), l2, maxw)
    y1 = h * (0.745 if not vertical else 0.79)
    y2 = h * (0.895 if not vertical else 0.89)
    draw_text(d, (w / 2, y1), l1, f1, fill=YELLOW, stroke=int(12 * S), stroke_fill=(0, 0, 0))
    if l2:
        draw_text(d, (w / 2, y2), l2, f2, fill=c2, stroke=int(12 * S), stroke_fill=(0, 0, 0))


def _hook_text(img, spec, w, h, S, vertical):
    """요즘 자극형 경제 썸네일 문구: 왼쪽 정렬·살짝 기울임·Paperlogy Black.
    1줄 = 흰 글자(숫자는 노랑) + 두꺼운 외곽선, 2줄 = 빨간 띠 위 흰 글자(핵심 한 방). 글자 크기는 기존(118px@1280)과 같다."""
    import re
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    top = h * (0.55 if not vertical else 0.62)
    for y in range(int(top), h):  # 아래쪽만 옅게 어둡게 (글자 가독성)
        a = int(min(170, (y - top) / (h * 0.25) * 170))
        bd.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    img.alpha_composite(band)
    l1, l2 = spec.get("line1", ""), spec.get("line2", "")
    size = int((118 if not vertical else 150) * S)
    maxw = int(w * 0.86)
    tf = spec.get("font", "hook")
    f1 = fit_font(tf, size, l1, maxw)
    f2 = fit_font(tf, size, l2, maxw - int(60 * S)) if l2 else f1
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0 = w * 0.045
    sw = int(11 * S)
    box_col = {"red": (232, 36, 48), "gold": CH_GOLD, "yellow": YELLOW, "navy": NAVY}.get(spec.get("line2_box", "red"), (232, 36, 48))
    txt2 = INK if spec.get("line2_box") in ("gold", "yellow") else WHITE
    # 2줄(띠) 위치
    pad = 26 * S
    h2 = f2.size * 1.12
    y2b = h - h * (0.045 if not vertical else 0.05)
    y2t = y2b - h2 - 2 * pad * 0.5
    y1c = y2t - f1.size * 0.62
    # 1줄: 토큰별 색 (숫자 포함 토큰은 노랑)
    x = x0
    for tok in re.split(r"(\s+)", l1):
        if not tok:
            continue
        col = YELLOW if re.search(r"[0-9]", tok) else WHITE
        d.text((x + 6 * S, y1c + 6 * S), tok, font=f1, fill=(0, 0, 0, 160), anchor="lm", stroke_width=sw, stroke_fill=(0, 0, 0, 160))
        d.text((x, y1c), tok, font=f1, fill=col, anchor="lm", stroke_width=sw, stroke_fill=INK)
        x += f1.getlength(tok)
    if l2:
        tw = f2.getlength(l2)
        d.rectangle([x0 - 10 * S, y2t, x0 + tw + 2 * pad, y2b], fill=box_col)
        d.rectangle([x0 - 10 * S, y2t, x0 + tw + 2 * pad, y2b], outline=INK, width=int(7 * S))
        d.text((x0 + pad, (y2t + y2b) / 2), l2, font=f2, fill=txt2, anchor="lm", stroke_width=int(4 * S) if txt2 == WHITE else 0, stroke_fill=INK)
    layer = layer.rotate(float(spec.get("text_tilt", 2.5)), center=(x0, y2b), resample=Image.BICUBIC)
    img.alpha_composite(layer)


def _text(img, spec, w, h, S, vertical):
    (_bottom_text if spec.get("text_style") == "classic" else _hook_text)(img, spec, w, h, S, vertical)


def _rays(w: int, h: int, c1, c2, center, n=18) -> Image.Image:
    """햇살(선버스트) 배경."""
    import math
    img = Image.new("RGB", (w, h), c1)
    d = ImageDraw.Draw(img)
    cx, cy = center
    R = (w ** 2 + h ** 2) ** 0.5
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c2)
    return img


def _phone_concept(spec: dict, w: int, h: int, seed: int) -> Image.Image:
    """컨셉 '잔고 화면': 선버스트 배경 + 큰 휴대폰 계좌 잔고 화면 + 놀라서 가리키는 캐릭터."""
    S = w / 1280
    ph = spec.get("phone", {})
    pal = {"navy": (NAVY, NAVY2), "gold": ((255, 196, 30), (255, 220, 90)), "green": ((40, 170, 90), (70, 200, 120)), "red": ((220, 50, 60), (245, 90, 90))}
    c1, c2 = pal.get(spec.get("theme", "gold"), pal["gold"])
    img = _rays(w, h, c1, c2, (w * 0.36, h * 0.38))
    if spec.get("theme") == "navy":  # 채널 배너처럼: 남색 + 금빛 후광
        rgba = img.convert("RGBA")
        _glow(rgba, w * 0.30, h * 0.40, 330 * S, (226, 180, 90))
        img = rgba.convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    # 휴대폰 (살짝 기울임)
    pw, phh = int(470 * S), int(560 * S)
    phone = Image.new("RGBA", (pw, phh), (0, 0, 0, 0))
    pd = ImageDraw.Draw(phone)
    pd.rounded_rectangle([0, 0, pw - 1, phh - 1], radius=int(48 * S), fill=(25, 27, 35), outline=INK, width=int(8 * S))
    sx0, sy0, sx1, sy1 = 22 * S, 30 * S, pw - 22 * S, phh - 26 * S
    pd.rounded_rectangle([sx0, sy0, sx1, sy1], radius=int(30 * S), fill=(248, 250, 252))
    pd.rounded_rectangle([pw / 2 - 50 * S, 12 * S, pw / 2 + 50 * S, 26 * S], radius=int(7 * S), fill=(60, 62, 72))
    mx = pw / 2
    y = sy0 + 20 * S
    if ph.get("toast"):  # 화면 상단 알림 배너
        pd.rounded_rectangle([sx0 + 14 * S, y, sx1 - 14 * S, y + 64 * S], radius=int(18 * S), fill=(232, 236, 244))
        pd.ellipse([sx0 + 30 * S, y + 14 * S, sx0 + 66 * S, y + 50 * S], fill=GOLD)
        draw_text(pd, (sx0 + 48 * S, y + 32 * S), "₩", font("black", int(22 * S)), fill=(150, 95, 0))
        draw_text(pd, (sx0 + 82 * S, y + 32 * S), ph["toast"], fit_font("bold", int(28 * S), ph["toast"], int((sx1 - sx0) - 110 * S)), fill=INK, anchor="lm")
        y += 84 * S
    draw_text(pd, (mx, y + 22 * S), ph.get("title", "내 투자 계좌"), font("bold", int(32 * S)), fill=(90, 95, 110))
    amt = ph.get("amount", "1,000,000,000원")
    fa = fit_font("black", int(78 * S), amt, int((sx1 - sx0) * 0.90))
    draw_text(pd, (mx, y + 92 * S), amt, fa, fill=(20, 150, 80))
    if ph.get("sub"):
        draw_text(pd, (mx, y + 152 * S), ph["sub"], fit_font("bold", int(28 * S), ph["sub"], int((sx1 - sx0) * 0.9)), fill=(230, 60, 70))
    # 상승 그래프 (화면 아래쪽 영역에만)
    gy0, gy1 = y + 190 * S, sy1 - 24 * S
    gl = Image.new("RGBA", phone.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    vals = [0.05, 0.12, 0.10, 0.22, 0.30, 0.24, 0.42, 0.55, 0.72, 0.95]
    pts = [(sx0 + 30 * S + k * (sx1 - sx0 - 60 * S) / 9, gy1 - v * (gy1 - gy0)) for k, v in enumerate(vals)]
    gd.polygon(pts + [(pts[-1][0], gy1), (pts[0][0], gy1)], fill=(20, 170, 90, 60))
    gd.line(pts, fill=(20, 170, 90), width=int(9 * S), joint="curve")
    phone.alpha_composite(gl)
    phone = phone.rotate(float(spec.get("tilt", 6)), expand=True, resample=Image.BICUBIC)
    img.paste(phone, (int(w * 0.04), int(h * 0.02)), phone)
    # 캐릭터: 휴대폰을 가리키도록 좌우 반전해서 그림
    layer = Image.new("RGB", (int(w * 0.5), h), (255, 0, 255))
    mascot(layer, layer.width * 0.42, h * 0.36, 1.0 * S, spec.get("emotion", "shock"), spec.get("gender", "m"), "point")
    layer = layer.transpose(Image.FLIP_LEFT_RIGHT)
    mask = Image.eval(layer.convert("RGB").split()[1], lambda v: 255)  # placeholder, replaced below
    import numpy as _np
    arr = _np.array(layer)
    m = ~((arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255))
    mask = Image.fromarray((m * 255).astype("uint8"))
    img.paste(layer, (int(w * 0.50), 0), mask)
    return img


def make_thumbnail(spec: dict, out: str, size=(1280, 720), seed: int = 1) -> None:
    if spec.get("layout") == "phone" and size[0] > size[1]:
        w, h = size
        S = w / 1280
        img = _phone_concept(spec, w, h, seed).convert("RGBA")
        _text(img, spec, w, h, S, vertical=False)
        if spec.get("badge"):  # 원형 도장 배지
            d = ImageDraw.Draw(img)
            cx, cy, r = w * 0.53, h * 0.12, 74 * S
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=int(6 * S))
            words = spec["badge"].split(" ", 1)
            draw_text(d, (cx, cy), "\n".join(words), fit_font(spec.get("font", "thumb"), int(40 * S), max(words, key=len), int(r * 1.6)), fill=WHITE, spacing=1.05)
        img.convert("RGB").save(out, quality=95)
        return
    w, h = size
    vertical = h > w
    split = spec.get("layout", "split") == "split" and not vertical
    bg = _office(w, h, spec.get("theme", "blue"), seed) if spec.get("background", "office") == "office" else _background(w, h, spec.get("theme", "blue"), seed)
    if spec.get("theme", "").endswith("_soft"):  # 옅은 톤: 배경 전체를 한 단계 밝게
        from PIL import ImageEnhance
        bg = ImageEnhance.Brightness(bg).enhance(1.22)
    img = bg.convert("RGBA")
    S = w / 1280
    mcx = w * (0.25 if split else 0.5)
    mcy = h * (0.38 if split else (0.34 if not vertical else 0.36))
    _glow(img, mcx, mcy + 40 * S, 300 * S)
    if spec.get("money_rain"):  # 떨어지는 지폐·동전 (가운데 캐릭터·하단 문구 영역은 피함)
        rnd = random.Random(seed + 7)
        rgb = img.convert("RGB")
        d0 = ImageDraw.Draw(rgb)
        for _ in range(int(spec.get("money_rain", 14))):
            for _try in range(30):
                x, y = rnd.uniform(0.03, 0.97) * w, rnd.uniform(0.02, 0.62 if not vertical else 0.66) * h
                if (abs(x - mcx) > w * 0.17) and not (split and x > w * 0.45 and y > h * 0.06):
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
    for side in (() if split else ("left", "right")):
        it = spec.get(side)
        if not it:
            continue
        x = w * (0.17 if side == "left" else 0.83) if not vertical else w * (0.22 if side == "left" else 0.78)
        y = h * (0.40 if not vertical else 0.20)
        _glow(img, x, y, 170 * S, (255, 255, 255))
        rgb = img.convert("RGB")
        icon(rgb, it["kind"], x, y, it.get("size", 330) * S, it.get("text"), hex2rgb(it["color"]) if it.get("color") else None)
        img = rgb.convert("RGBA")
    if not split and spec.get("arrow", True) and spec.get("left") and spec.get("right"):
        d = ImageDraw.Draw(img)
        y0 = h * (0.13 if not vertical else 0.08)
        pts = [(w * 0.24 + t * w * 0.5, y0 - (1 - (2 * t - 1) ** 2) * 70 * S) for t in [i / 30 for i in range(31)]]
        d.line(pts, fill=INK, width=int(26 * S), joint="curve")
        d.line(pts, fill=GOLD, width=int(16 * S), joint="curve")
        ex, ey = pts[-1]
        d.polygon([(ex + 30 * S, ey + 10 * S), (ex - 18 * S, ey - 30 * S), (ex - 18 * S, ey + 40 * S)], fill=GOLD, outline=INK)
    rgb = img.convert("RGB")
    if split and spec.get("big"):
        big = spec["big"]
        pd = ImageDraw.Draw(rgb, "RGBA")
        hook = spec.get("text_style") != "classic"  # hook 문구는 왼쪽 위로 더 올라오므로 패널을 그 위에서 끝낸다
        x0, y0, x1, y1 = w * 0.47, h * (0.19 if spec.get("badge") else 0.08), w * 0.97, h * (0.50 if hook else 0.62)
        pd.rounded_rectangle([x0, y0, x1, y1], radius=int(28 * S), fill=(16, 22, 40, 175 if spec.get("theme", "").endswith("_soft") else 215), outline=GOLD, width=int(8 * S))
        ph = y1 - y0
        # classic(승인된 기존 썸네일)은 예전 배치 그대로, hook은 낮아진 패널에 맞춘 비율 배치
        top_y, top_sz = (y0 + ph * 0.22, min(62 * S, ph * 0.2)) if hook else (y0 + 62 * S, 62 * S)
        val_y = y0 + ph * ((0.66 if hook else 0.62) if big.get("top") else 0.5)
        val_h = ph * ((0.40 if hook else 0.48) if big.get("top") else 0.8)
        if big.get("top"):
            ft = fit_font(spec.get("font", "thumb"), int(top_sz), big["top"], int((x1 - x0) * 0.88))
            draw_text(pd, ((x0 + x1) / 2, top_y), big["top"], ft, fill=WHITE)
        fv = (fit_box(spec.get("font", "thumb"), int(210 * S), big["value"], (x1 - x0) * 0.9, val_h, spacing=1.0) if hook
              else fit_font(spec.get("font", "thumb"), int(210 * S), big["value"], int((x1 - x0) * 0.9)))
        col = hex2rgb(big["color"]) if big.get("color") else YELLOW
        draw_text(pd, ((x0 + x1) / 2, val_y), big["value"], fv, fill=col, stroke=int(10 * S), stroke_fill=(0, 0, 0))
    mascot(rgb, mcx, mcy, (0.95 if split else (0.95 if not vertical else 1.5)) * S, spec.get("emotion", "smug"), spec.get("gender", "m"), spec.get("pose", "hands"))
    img = rgb.convert("RGBA")

    _text(img, spec, w, h, S, vertical)
    d = ImageDraw.Draw(img)
    if spec.get("badge"):
        f = fit_font(spec.get("font", "thumb"), int(56 * S), spec["badge"], int(w * 0.3))
        bw = f.getbbox(spec["badge"])[2] + 50 * S
        bx0 = (w - 30 * S - bw) if split else 30 * S
        by0 = h * 0.035 if split else 30 * S
        d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + 90 * S], radius=int(16 * S), fill=RED, outline=WHITE, width=int(5 * S))
        draw_text(d, (bx0 + bw / 2, by0 + 45 * S), spec["badge"], f, fill=WHITE)
    img.convert("RGB").save(out, quality=95)
