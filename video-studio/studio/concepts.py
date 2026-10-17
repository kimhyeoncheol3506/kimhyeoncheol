"""썸네일 컨셉 모음 (v1.8.0) — 회차마다 분위기를 50% 이상 바꾸기 위한 레이아웃들.

기존(1~4편): split(사무실+숫자 패널) / phone(남색 햇살+휴대폰) — 둘 다 어두운 배경 + 하단 빨간 띠 문구.
새 컨셉은 다섯 축(레이아웃·배경색·문구 위치·캐릭터 크기/위치·강조 요소) 중 3개 이상이 기존과 다르게 설계한다.

- versus : 2~3칸 세로 비교판(밝은 단색 칸), 상단 형광펜 문구, 승자 칸 왕관·금테, 캐릭터는 하단 작게
- chart  : 크림색 모눈종이 + 굵은 꺾은선(급등/급락), 좌상단 검정 문구 + 노랑 형광펜, 포스트잇 배지, 캐릭터 우하단
- bignum : 채도 높은 단색 배경(초록/주황/보라), 화면 절반 크기 숫자, 문구 상단 흰 글자, 캐릭터 얼굴만 오른쪽 아래에서 빼꼼
- receipt: 진한 배경 + 기울어진 영수증/고지서 종이, 빨간 도장, 문구 오른쪽 세로 배치
- board  : 증권 전광판(검정 LED 점판) + 시세 줄 + 초대형 등락률(하락 파랑) + 하단 빨간 속보 띠 (v1.10.0, 시장 급변 이슈용)
"""
from __future__ import annotations

import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .draw import INK, RED, WHITE, YELLOW, draw_text, fit_box, fit_font, font, hex2rgb, mascot

PALETTES = {  # 컨셉별 기본 배경 (어두운 남색 반복 피하기)
    "green": ((18, 132, 84), (12, 96, 62)),
    "orange": ((246, 128, 38), (222, 92, 20)),
    "purple": ((108, 64, 196), (78, 42, 150)),
    "teal": ((14, 140, 150), (8, 102, 112)),
    "cream": ((250, 246, 236), (242, 236, 222)),
    "black": ((22, 22, 26), (40, 40, 48)),
    "wine": ((122, 26, 52), (92, 16, 38)),
    "sky": ((52, 140, 220), (36, 112, 190)),
}


def _col(c, default):
    if not c:
        return default
    return hex2rgb(c) if isinstance(c, str) else tuple(c)


def _mascot_layer(w, h, cx, cy, s, emotion, gender, pose, flip=False):
    """마스코트를 투명 레이어로 그려 돌려준다 (좌우 반전 가능)."""
    key = (255, 0, 255)
    layer = Image.new("RGB", (w, h), key)
    mascot(layer, w - cx if flip else cx, cy, s, emotion, gender, pose)
    if flip:
        layer = layer.transpose(Image.FLIP_LEFT_RIGHT)
    arr = np.array(layer)
    m = ~((arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255))
    rgba = layer.convert("RGBA")
    rgba.putalpha(Image.fromarray((m * 255).astype("uint8")))
    return rgba


def _highlight_lines(img, lines, x, y, size, kind, S, fill=INK, marker=YELLOW, align="l", maxw=None):
    """형광펜 문구: 글자 뒤에 기울어진 마커 줄. lines=[(text, highlight?)]"""
    d = ImageDraw.Draw(img)
    yy = y
    for text, hl in lines:
        f = fit_font(kind, int(size * S), text, int(maxw or img.width * 0.9))
        tw = f.getlength(text)
        x0 = x if align == "l" else x - tw / 2
        if hl:
            d.polygon([(x0 - 14 * S, yy + f.size * 0.55), (x0 + tw + 16 * S, yy + f.size * 0.42),
                       (x0 + tw + 12 * S, yy + f.size * 1.08), (x0 - 10 * S, yy + f.size * 1.16)], fill=marker)
        d.text((x0, yy), text, font=f, fill=fill)
        yy += f.size * 1.18
    return yy


def _shadow_text(img, xy, text, f, fill, shadow=(0, 0, 0, 150), off=8, anchor="mm", stroke=0, stroke_fill=INK):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + off, xy[1] + off), text, font=f, fill=shadow, anchor=anchor, stroke_width=stroke, stroke_fill=shadow)
    sh = sh.filter(ImageFilter.GaussianBlur(off / 2))
    img.alpha_composite(sh)
    ImageDraw.Draw(img).text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def _versus(spec, w, h, S, tf):
    """세로 비교판: 밝은 단색 칸 2~3개, 상단 형광펜 문구, 승자 칸 강조."""
    cols = spec["cols"]
    n = len(cols)
    bg = _col(spec.get("bg"), (250, 246, 236))
    img = Image.new("RGBA", (w, h), bg + (255,))
    d = ImageDraw.Draw(img)
    top = h * 0.41  # 왕관이 상단 문구에 닿지 않게
    gap = 18 * S
    cw = (w - 60 * S - gap * (n - 1)) / n
    default_cols = [(66, 133, 244), (52, 168, 83), (234, 67, 53)]
    win = spec.get("winner", -1)
    for i, c in enumerate(cols):
        x0 = 30 * S + i * (cw + gap)
        col = _col(c.get("color"), default_cols[i % 3])
        d.rounded_rectangle([x0, top, x0 + cw, h - 30 * S], radius=int(26 * S), fill=col,
                            outline=(GOLD_RIM if i == win else INK), width=int((14 if i == win else 6) * S))
        fl = fit_font(tf, int(84 * S), c["label"], int(cw * 0.86))
        _shadow_text(img, (x0 + cw / 2, top + 70 * S), c["label"], fl, WHITE, off=5, stroke=int(5 * S))
        if c.get("value"):
            fv = fit_box(tf, int(110 * S), c["value"], cw * 0.88, (h - top) * 0.34, spacing=1.0)
            _shadow_text(img, (x0 + cw / 2, top + (h - top) * 0.55), c["value"], fv, YELLOW if i == win else WHITE, off=6, stroke=int(7 * S))
        if c.get("sub"):
            fs = fit_font("bold", int(34 * S), c["sub"], int(cw * 0.86))
            ImageDraw.Draw(img).text((x0 + cw / 2, h - 80 * S), c["sub"], font=fs, fill=WHITE, anchor="mm")
        if i == win:  # 왕관
            cx, cy = x0 + cw / 2, top - 6 * S
            pts = [(cx - 60 * S, cy), (cx - 70 * S, cy - 60 * S), (cx - 30 * S, cy - 30 * S), (cx, cy - 75 * S),
                   (cx + 30 * S, cy - 30 * S), (cx + 70 * S, cy - 60 * S), (cx + 60 * S, cy)]
            ImageDraw.Draw(img).polygon(pts, fill=(255, 196, 0), outline=INK)
    # 상단 문구 (검정 글자 + 형광펜)
    _highlight_lines(img, [(spec.get("line1", ""), False), (spec.get("line2", ""), True)], 36 * S, 18 * S, 74, tf, S,
                     maxw=w * (0.74 if spec.get("mascot") else 0.92))
    if spec.get("mascot"):  # 기본은 캐릭터 없이 (다른 회차와 차별)
        lay = _mascot_layer(w, h, w * 0.88, h * 0.17, 0.42 * S, spec.get("emotion", "shock"), spec.get("gender", "m"), "point", flip=True)
        img.alpha_composite(lay)
    return img


GOLD_RIM = (255, 196, 0)


def _chart(spec, w, h, S, tf):
    """크림색 모눈종이 + 굵은 꺾은선, 좌상단 문구, 포스트잇 배지, 우하단 캐릭터."""
    dark = bool(spec.get("dark"))  # 어두운 차트판(네온 선) 변형
    bg = _col(spec.get("bg"), (18, 20, 28) if dark else (250, 246, 236))
    img = Image.new("RGBA", (w, h), bg + (255,))
    d = ImageDraw.Draw(img)
    grid = (44, 48, 62) if dark else (226, 220, 205)
    for x in range(0, w, int(40 * S)):
        d.line([(x, 0), (x, h)], fill=grid, width=1)
    for y in range(0, h, int(40 * S)):
        d.line([(0, y), (w, y)], fill=grid, width=1)
    vals = spec.get("values", [0.1, 0.25, 0.2, 0.45, 0.4, 0.7, 1.0])
    down = spec.get("trend") == "down"
    x0, x1, y0, y1 = w * 0.06, w * 0.70, h * 0.42, h * 0.92
    lo, hi = min(vals), max(vals)
    pts = [(x0 + (x1 - x0) * i / (len(vals) - 1), y1 - (y1 - y0) * (v - lo) / ((hi - lo) or 1)) for i, v in enumerate(vals)]
    col = (35, 99, 235) if down else (229, 57, 53)
    if dark:
        col = (80, 220, 255) if down else (255, 70, 110)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.polygon(pts + [(pts[-1][0], y1), (pts[0][0], y1)], fill=col + (40,))
    ld.line(pts, fill=col, width=int(16 * S), joint="curve")
    ex, ey = pts[-1]
    ang = np.arctan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
    tip = (ex + 40 * S * np.cos(ang), ey + 40 * S * np.sin(ang))
    l = (ex + 30 * S * np.cos(ang + 2.4), ey + 30 * S * np.sin(ang + 2.4))
    r = (ex + 30 * S * np.cos(ang - 2.4), ey + 30 * S * np.sin(ang - 2.4))
    ld.polygon([tip, l, r], fill=col)
    img.alpha_composite(lay)
    if spec.get("point"):  # 끝점 말풍선 숫자
        fp = fit_font(tf, int(88 * S), spec["point"], int(w * 0.34))
        bx, by = min(ex, w * 0.62), max(ey - 60 * S, h * 0.47)
        tw = fp.getlength(spec["point"])
        d.rounded_rectangle([bx - tw / 2 - 24 * S, by - 62 * S, bx + tw / 2 + 24 * S, by + 50 * S], radius=int(20 * S), fill=YELLOW if dark else INK)
        d.text((bx, by - 6 * S), spec["point"], font=fp, fill=INK if dark else YELLOW, anchor="mm")
    _highlight_lines(img, [(spec.get("line1", ""), False), (spec.get("line2", ""), True)], 44 * S, 26 * S, 92, tf, S, maxw=w * 0.66,
                     fill=WHITE if dark else INK, marker=(255, 70, 110) if dark else YELLOW)
    if spec.get("badge"):  # 포스트잇
        note = Image.new("RGBA", (int(250 * S), int(170 * S)), (255, 236, 120, 255))
        nd = ImageDraw.Draw(note)
        draw_text(nd, (note.width / 2, note.height / 2), spec["badge"].replace(" ", "\n", 1),
                  fit_box(tf, int(48 * S), spec["badge"].replace(" ", "\n", 1), note.width * 0.86, note.height * 0.8), fill=INK)
        note = note.rotate(-7, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(note, (int(w * 0.76), int(h * 0.05)))
    img.alpha_composite(_mascot_layer(w, h, w * 0.86, h * 0.60, 0.72 * S, spec.get("emotion", "shock"), spec.get("gender", "m"), "point", flip=True))
    return img


def _bignum(spec, w, h, S, tf):
    """채도 높은 단색 + 화면 절반 크기 숫자 + 상단 흰 문구 + 오른쪽 아래 빼꼼 캐릭터."""
    c1, c2 = PALETTES.get(spec.get("theme", "green"), PALETTES["green"])
    img = Image.new("RGBA", (w, h), c1 + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for _ in range(26):  # 은은한 원형 무늬
        r = rnd.uniform(40, 160) * S
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        d.ellipse([x - r, y - r, x + r, y + r], outline=c2, width=int(6 * S))
    f1 = fit_font(tf, int(70 * S), spec.get("line1", ""), int(w * 0.9))
    d.text((44 * S, 30 * S), spec.get("line1", ""), font=f1, fill=WHITE, stroke_width=int(4 * S), stroke_fill=c2)
    num = spec.get("number", "?")
    fn = fit_box(tf, int(330 * S), num, w * 0.60, h * 0.48, spacing=1.0)  # 오른쪽 캐릭터와 겹치지 않게
    _shadow_text(img, (w * 0.35, h * 0.50), num, fn, YELLOW, off=12, stroke=int(12 * S))
    l2 = spec.get("line2", "")
    if l2:
        f2 = fit_font(tf, int(84 * S), l2, int(w * 0.62))
        tw = f2.getlength(l2)
        yb = h * 0.80
        d = ImageDraw.Draw(img)
        d.rectangle([36 * S, yb - 12 * S, 36 * S + tw + 40 * S, yb + f2.size * 1.12], fill=WHITE)
        d.text((56 * S, yb), l2, font=f2, fill=c2)
    lay = _mascot_layer(w, h, w * 0.86, h * 0.78, 1.25 * S, spec.get("emotion", "shock"), spec.get("gender", "m"), "normal", flip=True)
    img.alpha_composite(lay)
    if spec.get("badge"):
        fb = fit_font(tf, int(40 * S), spec["badge"], int(w * 0.3))
        tw = fb.getlength(spec["badge"])
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([w - tw - 80 * S, 30 * S, w - 30 * S, 100 * S], radius=int(35 * S), fill=INK)
        d.text((w - 55 * S - tw / 2, 65 * S), spec["badge"], font=fb, fill=WHITE, anchor="mm")
    return img


def _receipt(spec, w, h, S, tf):
    """진한 단색 + 기울어진 영수증 + 빨간 도장 + 오른쪽 문구."""
    c1, c2 = PALETTES.get(spec.get("theme", "black"), PALETTES["black"])
    img = Image.new("RGBA", (w, h), c1 + (255,))
    rw, rh = int(430 * S), int(640 * S)
    paper = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
    pd = ImageDraw.Draw(paper)
    teeth = [(x, rh - (14 * S if (x // int(20 * S)) % 2 else 0)) for x in range(0, rw + 1, int(20 * S))]
    pd.polygon([(0, 0), (rw, 0)] + teeth[::-1], fill=(252, 252, 248))
    pd.text((rw / 2, 50 * S), spec.get("receipt_title", "영수증"), font=font("black", int(44 * S)), fill=INK, anchor="mm")
    y = 110 * S
    for name, val in spec.get("rows", []):
        pd.text((30 * S, y), name, font=font("bold", int(30 * S)), fill=(70, 70, 70))
        pd.text((rw - 30 * S, y), val, font=font("bold", int(30 * S)), fill=INK, anchor="ra")
        y += 52 * S
    pd.line([(30 * S, y + 10 * S), (rw - 30 * S, y + 10 * S)], fill=INK, width=int(4 * S))
    tot = spec.get("total", "")
    pd.text((30 * S, y + 30 * S), "합계", font=font("black", int(38 * S)), fill=INK)
    pd.text((rw - 30 * S, y + 26 * S), tot, font=fit_font("black", int(44 * S), tot, int(rw * 0.6)), fill=RED, anchor="ra")
    if spec.get("stamp"):
        st = Image.new("RGBA", (int(220 * S), int(220 * S)), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.ellipse([8 * S, 8 * S, 212 * S, 212 * S], outline=(220, 30, 40, 230), width=int(10 * S))
        draw_text(sd, (110 * S, 110 * S), spec["stamp"].replace(" ", "\n", 1),
                  fit_box(tf, int(54 * S), spec["stamp"].replace(" ", "\n", 1), 160 * S, 150 * S), fill=(220, 30, 40, 230))
        st = st.rotate(18, resample=Image.BICUBIC)
        paper.alpha_composite(st, (int(rw - 240 * S), int(rh - 260 * S)))
    paper = paper.rotate(-6, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 120), (int(64 * S), int(50 * S), int(64 * S) + paper.width, int(50 * S) + paper.height), paper)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * S)))
    img.alpha_composite(paper, (int(50 * S), int(36 * S)))
    # 오른쪽 문구 (세로 스택, 흰 글자 + 노랑 강조 줄)
    x = w * 0.50
    lines = spec.get("lines") or [spec.get("line1", ""), spec.get("line2", "")]
    y = h * 0.14
    d = ImageDraw.Draw(img)
    for i, t in enumerate(lines):
        f = fit_font(tf, int(92 * S), t, int(w * 0.47))
        last = i == len(lines) - 1
        if last:
            tw = f.getlength(t)
            d.rectangle([x - 14 * S, y - 6 * S, x + tw + 14 * S, y + f.size * 1.14], fill=YELLOW)
        d.text((x, y), t, font=f, fill=INK if last else WHITE)
        y += f.size * 1.3
    img.alpha_composite(_mascot_layer(w, h, w * 0.80, h * 0.80, 0.55 * S, spec.get("emotion", "worried"), spec.get("gender", "m"), "normal", flip=False))
    return img


def _scale(spec, w, h, S, tf):
    """저울: 민트 배경, 가운데 저울(무거운 쪽이 내려감), 좌상단 형광펜 문구, 캐릭터 왼쪽 아래 작게."""
    import math
    c1 = _col(spec.get("bg"), (214, 242, 230))
    img = Image.new("RGBA", (w, h), c1 + (255,))
    d = ImageDraw.Draw(img)
    for r in range(int(w * 0.9), 0, -int(60 * S)):  # 동심원 배경
        d.ellipse([w * 0.62 - r, h * 0.62 - r, w * 0.62 + r, h * 0.62 + r], outline=(196, 232, 216), width=int(3 * S))
    cx, py = w * 0.62, h * 0.40
    tilt = math.radians(spec.get("tilt", -12))  # 음수면 왼쪽이 내려감
    L = w * 0.26
    lx, ly = cx - L * math.cos(tilt), py - L * math.sin(tilt)
    rx, ry = cx + L * math.cos(tilt), py + L * math.sin(tilt)
    d.polygon([(cx - 60 * S, h * 0.95), (cx + 60 * S, h * 0.95), (cx + 14 * S, py), (cx - 14 * S, py)], fill=(60, 64, 80))
    d.line([(lx, ly), (rx, ry)], fill=(60, 64, 80), width=int(18 * S))
    d.ellipse([cx - 26 * S, py - 26 * S, cx + 26 * S, py + 26 * S], fill=(255, 196, 0), outline=INK, width=int(5 * S))
    pans = spec.get("pans", [{"label": "A"}, {"label": "B"}])
    cols = [(42, 120, 214), (232, 58, 58)]
    for i, (x, y) in enumerate([(lx, ly), (rx, ry)]):
        p = pans[i]
        d.line([(x, y), (x - 110 * S, y + 120 * S)], fill=(60, 64, 80), width=int(5 * S))
        d.line([(x, y), (x + 110 * S, y + 120 * S)], fill=(60, 64, 80), width=int(5 * S))
        d.chord([x - 150 * S, y + 40 * S, x + 150 * S, y + 200 * S], 0, 180, fill=_col(p.get("color"), cols[i]), outline=INK, width=int(6 * S))
        fl = fit_font(tf, int(64 * S), p["label"], int(260 * S))
        _shadow_text(img, (x, y + 70 * S), p["label"], fl, WHITE, off=4, stroke=int(6 * S))
        if p.get("value"):
            fv = fit_font(tf, int(72 * S), p["value"], int(280 * S))
            _shadow_text(img, (x, y + 215 * S), p["value"], fv, YELLOW, off=5, stroke=int(8 * S))
    _highlight_lines(img, [(spec.get("line1", ""), False), (spec.get("line2", ""), True)], 40 * S, 22 * S, 80, tf, S,
                     maxw=w * 0.92, marker=(255, 150, 160))
    img.alpha_composite(_mascot_layer(w, h, w * 0.12, h * 0.72, 0.6 * S, spec.get("emotion", "think"), spec.get("gender", "m"), "normal"))
    return img


def _warning(spec, w, h, S, tf):
    """경고판: 노랑 배경 + 위아래 검정·노랑 사선 띠, 빨간 경고 삼각형, 가운데 큰 숫자, 캐릭터 오른쪽."""
    bg = _col(spec.get("bg"), (255, 214, 10))
    img = Image.new("RGBA", (w, h), bg + (255,))
    d = ImageDraw.Draw(img)
    band = int(56 * S)
    for y0 in (0, h - band):
        d.rectangle([0, y0, w, y0 + band], fill=INK)
        for x in range(-band, w + band, int(80 * S)):
            d.polygon([(x, y0 + band), (x + 40 * S, y0 + band), (x + 40 * S + band, y0), (x + band, y0)], fill=bg)
    # 경고 삼각형
    tx, ty, tr = w * 0.14, h * 0.50, 150 * S
    d.polygon([(tx, ty - tr), (tx - tr * 0.95, ty + tr * 0.7), (tx + tr * 0.95, ty + tr * 0.7)], fill=(225, 40, 40), outline=INK, width=int(10 * S))
    _shadow_text(img, (tx, ty + 18 * S), "!", font("black", int(190 * S)), WHITE, off=4)
    d = ImageDraw.Draw(img)
    f1 = fit_font(tf, int(76 * S), spec.get("line1", ""), int(w * 0.62))
    d.text((w * 0.30, h * 0.14), spec.get("line1", ""), font=f1, fill=INK)
    num = spec.get("number", "")
    fn = fit_box(tf, int(220 * S), num, w * 0.52, h * 0.34, spacing=1.0)
    _shadow_text(img, (w * 0.30 + w * 0.26, h * 0.50), num, fn, (225, 40, 40), shadow=(0, 0, 0, 90), off=8, stroke=int(10 * S), stroke_fill=INK)
    l2 = spec.get("line2", "")
    if l2:
        f2 = fit_font(tf, int(70 * S), l2, int(w * 0.44))
        tw = f2.getlength(l2)
        x0 = w * 0.30
        d = ImageDraw.Draw(img)
        d.rectangle([x0 - 12 * S, h * 0.70, x0 + tw + 24 * S, h * 0.70 + f2.size * 1.25], fill=INK)
        d.text((x0 + 6 * S, h * 0.70 + f2.size * 0.08), l2, font=f2, fill=bg)
    img.alpha_composite(_mascot_layer(w, h, w * 0.89, h * 0.52, 0.62 * S, spec.get("emotion", "shock"), spec.get("gender", "m"), "normal", flip=True))
    return img


def _board(spec, w, h, S, tf):
    """증권 전광판: 검정 LED 점판 + 종목 시세 줄(파랑 하락/빨강 상승) + 초대형 등락률 + 하단 빨간 속보 띠 + 캐릭터 오른쪽."""
    bg = _col(spec.get("board_bg"), (10, 12, 18))  # bg는 기본 썸네일에서 물려받기 쉬워 따로 둔다
    img = Image.new("RGBA", (w, h), bg + (255,))
    d = ImageDraw.Draw(img)
    step = int(14 * S)
    for y in range(0, h, step):  # LED 점판
        for x in range(0, w, step):
            d.ellipse([x, y, x + 4 * S, y + 4 * S], fill=(28, 32, 42))
    down = spec.get("trend", "down") == "down"
    main = (64, 140, 255) if down else (255, 64, 64)
    # 왼쪽 위 '속보' 꼬리표 + 1줄 문구
    tag = spec.get("tag", "속보")
    ft = font("black", int(46 * S))
    tw = ft.getlength(tag)
    d.rectangle([36 * S, 30 * S, 36 * S + tw + 36 * S, 30 * S + 66 * S], fill=(225, 30, 40))
    d.text((54 * S, 63 * S), tag, font=ft, fill=WHITE, anchor="lm")
    l1 = spec.get("line1", "")
    f1 = fit_font(tf, int(74 * S), l1, int(w * 0.80 - tw - 90 * S))
    d.text((36 * S + tw + 66 * S, 63 * S), l1, font=f1, fill=WHITE, anchor="lm")
    # 시세 줄 (종목명 · 값 · 등락)
    rows = spec.get("rows", [])
    y = h * 0.20
    for name, val, chg in rows[:3]:
        fr = font("bold", int(40 * S))
        col = (64, 140, 255) if str(chg).startswith("-") or str(chg).startswith("▼") else (255, 64, 64)
        d.text((40 * S, y), name, font=fr, fill=(200, 205, 215))
        d.text((w * 0.36, y), val, font=fr, fill=col, anchor="ra")
        d.text((w * 0.38, y), chg, font=fr, fill=col)
        y += 56 * S
    # 초대형 숫자
    num = spec.get("number", "")
    fn = fit_box(tf, int(300 * S), num, w * 0.66, h * 0.36, spacing=1.0)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((w * 0.36, h * 0.62), num, font=fn, fill=main + (200,), anchor="mm")
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18 * S)))
    ImageDraw.Draw(img).text((w * 0.36, h * 0.62), num, font=fn, fill=main, anchor="mm", stroke_width=int(4 * S), stroke_fill=WHITE)
    # 하단 속보 띠
    l2 = spec.get("line2", "")
    d = ImageDraw.Draw(img)
    by = h * 0.82
    d.rectangle([0, by, w, h], fill=(225, 30, 40))
    d.rectangle([0, by, w, by + 8 * S], fill=YELLOW)
    if l2:
        f2 = fit_box(tf, int(86 * S), l2, w * 0.70, h * 0.16, spacing=1.0)
        d.text((40 * S, (by + h) / 2 + 4 * S), l2, font=f2, fill=WHITE, anchor="lm")
    img.alpha_composite(_mascot_layer(w, h, w * 0.85, h * 0.56, 0.78 * S, spec.get("emotion", "shock"), spec.get("gender", "m"), "normal", flip=True))
    if spec.get("badge"):
        fb = fit_font(tf, int(40 * S), spec["badge"], int(w * 0.26))
        bw = fb.getlength(spec["badge"])
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([w - bw - 80 * S, 26 * S, w - 30 * S, 96 * S], radius=int(35 * S), fill=YELLOW)
        d.text((w - 55 * S - bw / 2, 61 * S), spec["badge"], font=fb, fill=INK, anchor="mm")
    return img


CONCEPTS = {"warning": _warning, "scale": _scale, "versus": _versus, "chart": _chart, "bignum": _bignum, "receipt": _receipt, "board": _board}
# 순환 순서: 직전 회차들과 겹치지 않는 것을 고른다 (split·phone은 1~4편에서 사용)
CONCEPT_ORDER = ["warning", "scale", "versus", "chart", "bignum", "receipt", "board", "split", "phone"]


def render(spec, w, h, tf):
    S = w / 1280
    return CONCEPTS[spec["layout"]](spec, w, h, S, tf)
