"""썸네일 컨셉 모음 (v1.8.0) — 회차마다 분위기를 50% 이상 바꾸기 위한 레이아웃들.

기존(1~4편): split(사무실+숫자 패널) / phone(남색 햇살+휴대폰) — 둘 다 어두운 배경 + 하단 빨간 띠 문구.
새 컨셉은 다섯 축(레이아웃·배경색·문구 위치·캐릭터 크기/위치·강조 요소) 중 3개 이상이 기존과 다르게 설계한다.

- versus : 2~3칸 세로 비교판(밝은 단색 칸), 상단 형광펜 문구, 승자 칸 왕관·금테, 캐릭터는 하단 작게
- chart  : 크림색 모눈종이 + 굵은 꺾은선(급등/급락), 좌상단 검정 문구 + 노랑 형광펜, 포스트잇 배지, 캐릭터 우하단
- bignum : 채도 높은 단색 배경(초록/주황/보라), 화면 절반 크기 숫자, 문구 상단 흰 글자, 캐릭터 얼굴만 오른쪽 아래에서 빼꼼
- receipt: 진한 배경 + 기울어진 영수증/고지서 종이, 빨간 도장, 문구 오른쪽 세로 배치
- archive: 흑백 옛날 사진(코드로 그린 1929 월가) + 검정 배경 빨간 초대형 글씨 + 노랑 띠 반전 문구 (v1.12.0, 역사 데이터 회차용)
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
        lc = spec.get("line_colors", {}).get(str(i))  # 줄별 글자색 (v1.13.1): 지정한 줄은 그 색 + 흰 테두리
        if lc:
            d.text((x, y), t, font=f, fill=_col(lc, WHITE), stroke_width=int(7 * S), stroke_fill=WHITE)
            d.text((x, y), t, font=f, fill=_col(lc, WHITE))
        else:
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
    if spec.get("line2_font") or spec.get("line2_color"):  # 2줄만 다른 폰트·색 (v1.12.1, 현철님 요청)
        yy = _highlight_lines(img, [(spec.get("line1", ""), False)], 40 * S, 22 * S, 80, tf, S, maxw=w * 0.92)
        l2 = spec.get("line2", "")
        f2 = fit_font(spec.get("line2_font", tf), int(spec.get("line2_size", 92) * S), l2, int(w * 0.92))
        ImageDraw.Draw(img).text((40 * S, yy + 2 * S), l2, font=f2, fill=_col(spec.get("line2_color"), RED),
                                 stroke_width=int(7 * S), stroke_fill=WHITE)
    else:
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


def _vintage_photo(pw, ph, S, seed=29):
    """코드로 그린 1929년 월가 흑백사진: 신전형 거래소 건물 + 모자 쓴 군중 + 필름 그레인·긁힘·비네팅."""
    img = Image.new("L", (pw, ph), 150)
    d = ImageDraw.Draw(img)
    for y in range(ph):  # 하늘 그라데이션
        d.line([(0, y), (pw, y)], fill=int(196 - 60 * y / ph))
    bx0, bx1, top = pw * 0.12, pw * 0.88, ph * 0.16
    d.polygon([(bx0 - 20 * S, top + 70 * S), ((bx0 + bx1) / 2, top), (bx1 + 20 * S, top + 70 * S)], fill=120)  # 박공
    d.rectangle([bx0 - 20 * S, top + 70 * S, bx1 + 20 * S, top + 96 * S], fill=104)
    n = 6
    for i in range(n):  # 기둥
        x = bx0 + (bx1 - bx0) * (i + 0.5) / n
        d.rectangle([x - 18 * S, top + 96 * S, x + 18 * S, ph * 0.66], fill=178)
        d.line([(x - 6 * S, top + 100 * S), (x - 6 * S, ph * 0.66)], fill=150, width=max(1, int(3 * S)))
    d.rectangle([bx0, top + 96 * S, bx1, ph * 0.66], outline=96, width=max(1, int(3 * S)))
    for i in range(n - 1):  # 기둥 사이 어둠
        x0 = bx0 + (bx1 - bx0) * (i + 0.5) / n + 18 * S
        x1 = bx0 + (bx1 - bx0) * (i + 1.5) / n - 18 * S
        d.rectangle([x0, top + 110 * S, x1, ph * 0.66], fill=70)
    d.rectangle([0, ph * 0.66, pw, ph], fill=92)  # 거리
    rnd = random.Random(seed)
    for row in range(5):  # 군중 (뒷줄일수록 작고 밝게)
        sc = (0.55 + row * 0.16) * S
        yb = ph * (0.70 + row * 0.07)
        tone = int(78 - row * 12)
        x = -rnd.uniform(0, 30) * S
        while x < pw + 30 * S:
            hw = rnd.uniform(26, 34) * sc
            d.rounded_rectangle([x - hw, yb - 10 * sc, x + hw, yb + 160 * sc], radius=int(16 * sc), fill=tone)  # 몸
            d.ellipse([x - 16 * sc, yb - 42 * sc, x + 16 * sc, yb - 8 * sc], fill=tone + 26)  # 얼굴
            d.ellipse([x - 26 * sc, yb - 46 * sc, x + 26 * sc, yb - 34 * sc], fill=max(10, tone - 30))  # 챙
            d.rounded_rectangle([x - 15 * sc, yb - 64 * sc, x + 15 * sc, yb - 38 * sc], radius=int(6 * sc), fill=max(10, tone - 30))  # 중절모
            x += hw * 2 + rnd.uniform(-6, 10) * sc
    a = np.array(img).astype(float)
    a += np.random.default_rng(seed).normal(0, 16, a.shape)  # 그레인
    yy, xx = np.mgrid[0:ph, 0:pw]
    r = np.sqrt(((xx - pw / 2) / (pw / 2)) ** 2 + ((yy - ph / 2) / (ph / 2)) ** 2)
    a *= np.clip(1.15 - 0.45 * r ** 2, 0.35, 1)  # 비네팅
    img = Image.fromarray(np.clip(a, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8 * S))
    d = ImageDraw.Draw(img)
    for _ in range(4):  # 짧고 옅은 긁힘
        x, y = rnd.uniform(0, pw), rnd.uniform(0, ph * 0.8)
        d.line([(x, y), (x + rnd.uniform(-4, 4) * S, y + rnd.uniform(40, 120) * S)], fill=rnd.choice([110, 175]), width=1)
    sep = Image.merge("RGB", [img.point(lambda v: min(255, int(v * 1.06 + 8))), img, img.point(lambda v: int(v * 0.88))])  # 살짝 세피아
    return sep


def _archive(spec, w, h, S, tf):
    """흑백 옛날 사진(왼쪽, 기울어진 인화지) + 검정 배경 오른쪽 초대형 빨간 글씨 + 노랑 띠 반전 문구 + 빼꼼 캐릭터 (v1.12.0, 역사 데이터 회차용)."""
    bg = _col(spec.get("archive_bg"), (16, 16, 18))
    img = Image.new("RGBA", (w, h), bg + (255,))
    pw, ph = int(w * 0.50), int(h * 0.74)
    photo = _vintage_photo(pw, ph, S).convert("RGBA")
    frame = Image.new("RGBA", (pw + int(36 * S), ph + int(96 * S)), (238, 232, 218, 255))
    frame.alpha_composite(photo, (int(18 * S), int(18 * S)))
    cap = spec.get("photo_caption", "")
    if cap:
        ImageDraw.Draw(frame).text((frame.width / 2, ph + 58 * S), cap, font=font("bold", int(38 * S)), fill=(60, 56, 50), anchor="mm")
    frame = frame.rotate(4, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 170), (int(40 * S), int(56 * S), int(40 * S) + frame.width, int(56 * S) + frame.height), frame)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16 * S)))
    img.alpha_composite(frame, (int(22 * S), int(34 * S)))
    x0, xw = w * 0.57, w * 0.41
    d = ImageDraw.Draw(img)
    big = spec.get("big", "")
    fb = fit_box(tf, int(260 * S), big, xw, h * 0.34, spacing=1.0)
    _shadow_text(img, (x0 + xw / 2, h * 0.27), big, fb, (236, 36, 44), off=10, stroke=int(6 * S), stroke_fill=(255, 255, 255))
    l1 = spec.get("line1", "")
    f1 = fit_box(tf, int(150 * S), l1, xw, h * 0.2, spacing=1.0)
    _shadow_text(img, (x0 + xw / 2, h * 0.53), l1, f1, WHITE, off=8)
    l2 = spec.get("line2", "")
    if l2:
        f2 = fit_font(tf, int(64 * S), l2, int(xw * 0.92))
        tw = f2.getlength(l2)
        d = ImageDraw.Draw(img)
        yb = h * 0.64
        d.rectangle([x0 + xw / 2 - tw / 2 - 22 * S, yb, x0 + xw / 2 + tw / 2 + 22 * S, yb + f2.size * 1.35], fill=YELLOW)
        d.text((x0 + xw / 2, yb + f2.size * 0.68), l2, font=f2, fill=INK, anchor="mm")
    img.alpha_composite(_mascot_layer(w, h, w * 0.91, h * 0.98, 0.58 * S, spec.get("emotion", "shock"), spec.get("gender", "m"), "normal", flip=True))
    return img


def _motif(img, kind, w, h, S):
    """주제를 한눈에 알리는 큰 배경 소품 (코드로 그림): up 상승 화살표 / down 하락 화살표 / coins 돈다발 / city 무너지는 도시."""
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(11)
    if kind in ("up", "down"):
        col = (236, 70, 70) if kind == "up" else (80, 140, 240)
        n = 16
        xs = [w * (0.36 + 0.62 * i / (n - 1)) for i in range(n)]
        for i, x in enumerate(xs):
            t = i / (n - 1)
            y = h * (0.62 - 0.40 * t) if kind == "up" else h * (0.22 + 0.34 * t)
            y += rnd.uniform(-14, 14) * S
            bh = rnd.uniform(40, 90) * S
            d.rectangle([x, y, x + 20 * S, y + bh], fill=col + (150,))
            d.line([(x + 10 * S, y - 22 * S), (x + 10 * S, y + bh + 22 * S)], fill=col + (150,), width=int(3 * S))
        a = [(w * 0.40, h * (0.60 if kind == "up" else 0.20)), (w * 0.62, h * (0.46 if kind == "up" else 0.34)),
             (w * 0.74, h * (0.52 if kind == "up" else 0.30)), (w * 0.96, h * (0.14 if kind == "up" else 0.58))]
        d.line(a, fill=col + (255,), width=int(26 * S), joint="curve")
        tip = a[-1]
        dy = -1 if kind == "up" else 1
        d.polygon([(tip[0] + 22 * S, tip[1] + dy * 40 * S), (tip[0] - 70 * S, tip[1] + dy * 6 * S), (tip[0] - 4 * S, tip[1] - dy * 70 * S)], fill=col + (255,))
    elif kind == "wheel":  # 12달 표지 원: 현철님 지정으로 표지 그림을 작게 넣는다 (출처 불명 표기는 후크 문구에). 파일이 없으면 우리가 그린 피자판
        import os
        from .wheel_art import COVER
        pdir = os.environ.get("THUMB_PROJECT_DIR", "")
        cp = os.path.join(pdir, COVER["2027"][0]) if pdir else ""
        if cp and os.path.exists(cp):
            src = Image.open(cp).convert("RGBA")
            (ox, oy), R = COVER["2027"][1], COVER["2027"][2]
            m = int(R * 1.04)
            circ = src.crop((ox - m, oy - m, ox + m, oy + m))
            mask = Image.new("L", circ.size, 0)
            ImageDraw.Draw(mask).ellipse([m - R, m - R, m + R, m + R], fill=255)
            circ.putalpha(mask)
            side = int(h * 0.62)
            sm = circ.resize((side, side), Image.LANCZOS)
            ring = Image.new("RGBA", (side + 16, side + 16), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse([0, 0, side + 15, side + 15], fill=(255, 255, 255, 255))
            img.alpha_composite(ring, (int(w * 0.60) - 8, int(h * 0.10) - 8))
            img.alpha_composite(sm, (int(w * 0.60), int(h * 0.10)))
        else:
            from .scene_art import _s
            from .wheel_art import wheel
            big = Image.new("RGBA", (_s(1920), _s(1080)), (0, 0, 0, 0))
            wheel(ImageDraw.Draw(big, "RGBA"), 960, 540, 500, None)
            sm = big.resize((1920, 1080), Image.LANCZOS).crop((430, 10, 1490, 1070))
            side = int(h * 0.80)
            img.alpha_composite(sm.resize((side, side), Image.LANCZOS), (int(w * 0.56), int(h * 0.04)))
    elif kind == "coins":
        for k in range(6):
            x = w * (0.62 + 0.07 * k) + rnd.uniform(-10, 10) * S
            for i in range(7 + k % 3):
                y = h * 0.70 - i * 22 * S + (k % 2) * 14 * S
                d.ellipse([x - 52 * S, y - 16 * S, x + 52 * S, y + 22 * S], fill=(244, 200, 80, 255), outline=(176, 130, 40, 255), width=int(4 * S))
    elif kind == "city":
        for i in range(8):
            x = w * (0.38 + 0.075 * i)
            bh = rnd.uniform(0.25, 0.55) * h
            d.rectangle([x, h * 0.66 - bh, x + 70 * S, h * 0.66], fill=(30, 26, 34, 255))
            for wy in range(int(h * 0.66 - bh) + 10, int(h * 0.66), int(24 * S)):
                for wx in range(int(x) + 8, int(x) + 62 * int(S), int(20 * S)):
                    if rnd.random() < 0.5:
                        d.rectangle([wx, wy, wx + 8 * S, wy + 12 * S], fill=(255, 190, 90, 200))
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for _ in range(9):
            x, y = rnd.uniform(0.4, 0.95) * w, rnd.uniform(0.25, 0.6) * h
            r = rnd.uniform(40, 90) * S
            gd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 120, 30, 170))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22 * S)))
        d2 = ImageDraw.Draw(img, "RGBA")
        d2.line([(w * 0.40, h * 0.18), (w * 0.62, h * 0.38), (w * 0.72, h * 0.30), (w * 0.96, h * 0.60)], fill=(236, 70, 70, 255), width=int(22 * S), joint="curve")


def _hero(spec, w, h, S, tf):
    """주인공형 (v1.14.0, 경제학똑똑 스타일 모방): 큰 개미 반신(위) + 주제 배경 소품 + 위쪽 작은 후크 + 아래 큼직한 2줄(흰 / 노랑·빨강)."""
    from .mascot import POSES, draw_ant
    top, bot = {"navy": ((12, 20, 52), (40, 30, 96)), "red": ((48, 8, 16), (130, 28, 36)), "black": ((8, 8, 12), (38, 38, 52)),
                "green": ((6, 36, 30), (18, 92, 70)), "purple": ((30, 14, 70), (96, 40, 150))}.get(spec.get("theme", "navy"), ((12, 20, 52), (40, 30, 96)))
    img = Image.new("RGBA", (w, h))
    px = img.load()
    g = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        g.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([w * 0.02, h * 0.0, w * 0.62, h * 0.9], fill=(255, 255, 255, 70))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60 * S)))
    _motif(img, spec.get("motif", "up"), w, h, S)
    pose = dict(POSES[spec.get("pose", "놀람")])
    ant = draw_ant(pose, int(h * 1.30))
    img.alpha_composite(ant, (int(w * spec.get("ant_x", 0.14)), int(-h * 0.04)))
    hook = spec.get("hook", "")
    if hook:
        fh = fit_font(tf, int(64 * S), hook, int(w * 0.5))
        _shadow_text(img, (w * 0.97, 52 * S), hook, fh, YELLOW, stroke=int(8 * S), anchor="rm", off=5)
    l1, l2 = spec.get("line1", ""), spec.get("line2", "")
    c2 = _col(spec.get("line2_color"), (255, 64, 64))
    f1 = fit_font(tf, int(150 * S), l1, int(w * 0.94))
    _shadow_text(img, (w * 0.5, h * 0.725), l1, f1, WHITE, stroke=int(14 * S), off=8)
    f2 = fit_font(tf, int(130 * S), l2, int(w * 0.94))
    _shadow_text(img, (w * 0.5, h * 0.895), l2, f2, c2, stroke=int(14 * S), off=8)
    if spec.get("badge"):
        fb = fit_font(tf, int(42 * S), spec["badge"], int(w * 0.25))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([24 * S, 24 * S, 24 * S + fb.getlength(spec["badge"]) + 50 * S, 92 * S], radius=int(34 * S), fill=(236, 70, 70))
        d.text((49 * S, 58 * S), spec["badge"], font=fb, fill=WHITE, anchor="lm")
    return img


CONCEPTS = {"hero": _hero, "warning": _warning, "scale": _scale, "versus": _versus, "chart": _chart, "bignum": _bignum, "receipt": _receipt, "board": _board, "archive": _archive}
# 순환 순서: 직전 회차들과 겹치지 않는 것을 고른다 (split·phone은 1~4편에서 사용)
CONCEPT_ORDER = ["hero", "warning", "scale", "versus", "chart", "bignum", "receipt", "board", "archive", "split", "phone"]


def render(spec, w, h, tf):
    S = w / 1280
    return CONCEPTS[spec["layout"]](spec, w, h, S, tf)
