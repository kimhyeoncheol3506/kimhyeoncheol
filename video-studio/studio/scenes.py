"""장면 그림 생성기. 모든 장면은 콘텐츠 영역(롱폼 1920x1080, 쇼츠 1080x1080) 하나의 PNG로 그린다.

벤치마킹에서 뽑은 원칙
- 한 문장 = 한 그림 (롱폼 평균 3초마다 장면 전환)
- 마스코트의 표정·소품으로 감정을 전달하고, 숫자는 크게, 비교는 좌우로
- 자막 영역(하단)을 비워 둔다
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from .draw import (fit_font, BLUE, GOLD, GREEN, INK, PASTELS, RED, WHITE, YELLOW, draw_text, font, hex2rgb, icon, mascot, rounded,
                   text_w, wrap)


def _bg(w, h, color):
    img = Image.new("RGB", (w, h), hex2rgb(color))
    d = ImageDraw.Draw(img)
    # 바닥선 (공간감)
    fy = int(h * 0.80)
    d.rectangle([0, fy, w, h], fill=tuple(max(0, c - 14) for c in hex2rgb(color)))
    d.line([(0, fy), (w, fy)], fill=tuple(max(0, c - 40) for c in hex2rgb(color)), width=3)
    return img, d


def render_visual(v: dict, w: int, h: int, bg: str | None, idx: int) -> Image.Image:
    color = bg or PASTELS[idx % len(PASTELS)]
    img, d = _bg(w, h, color)
    if v.get("backdrop") == "office":  # v1.11.1 만화 일러스트풍 배경: 창밖 도시·책상·조명, 살짝 흐리게 (인물에 시선 집중)
        from PIL import ImageFilter
        from .thumbnail import _glow, _office
        office = _office(w, h, v.get("backdrop_theme", "gold_soft"), idx).filter(ImageFilter.GaussianBlur(2.2 * h / 1080))
        img = office.convert(img.mode)
        _glow(img, w * 0.82, h * 0.18, h * 0.32, (255, 214, 140))
        d = ImageDraw.Draw(img)
    k = v.get("type", "mascot")
    S = h / 1080  # 기준 스케일
    long = w > h
    cx = w / 2
    usable_bottom = h * (0.80 if long else 0.74)  # 자막 영역 위까지

    if k == "mascot":
        props = v.get("props", [])
        mx = cx if not props else (cx - (330 if long else 200) * S if any(p.get("pos", "right") == "right" for p in props) else cx + 330 * S)
        mascot(img, mx, h * (0.33 if long else 0.30), (1.25 if long else 1.1) * S, v.get("emotion", "neutral"), v.get("gender", "m"), v.get("pose", "normal"), v.get("label"))
        for p in props:
            pos = p.get("pos", "right")
            px = {"right": cx + (360 if long else 250) * S, "left": cx - (360 if long else 250) * S, "top": cx}.get(pos, cx)
            py = h * (0.40 if pos != "top" else 0.12)
            icon(img, p["kind"], px, py, p.get("size", 300) * S, p.get("text"), hex2rgb(p["color"]) if p.get("color") else None)
        if v.get("say"):
            _bubble(img, mx + 40 * S, h * 0.06, v["say"], S, max_w=int((620 if long else 560) * S))
    elif k == "dialogue":
        sp = v.get("speaker", "m")
        em = v.get("emotions", {})
        lx, rx = cx - (330 if long else 230) * S, cx + (330 if long else 230) * S
        sc = (1.0 if long else 0.85) * S
        mascot(img, lx, h * 0.40, sc, em.get("m", "neutral"), "m", "normal")
        mascot(img, rx, h * 0.40, sc, em.get("f", "neutral"), "f", "normal")
        # 테이블
        d.rounded_rectangle([cx - (520 if long else 470) * S, h * 0.66, cx + (520 if long else 470) * S, h * 0.72], radius=int(12 * S), fill=(214, 182, 140), outline=INK, width=int(5 * S))
        if v.get("say"):
            bx = lx if sp == "m" else rx
            _bubble(img, bx, h * 0.03, v["say"], S, max_w=int(500 * S), tail_x=bx)
        if v.get("context"):  # 상황 설명 괄호 자막 (인생 녹음 중 방식)
            draw_text(d, (cx, h * 0.76), f"({v['context']})", font("bold", int(40 * S)), fill=(90, 90, 90))
    elif k == "title":
        f = font("black", int(v.get("size", 110) * S))
        lines = "\n".join(wrap(v["text"], f, int(w * 0.85)))
        draw_text(d, (cx, h * 0.38), lines, f, fill=INK)
        if v.get("sub"):
            draw_text(d, (cx, h * 0.60), v["sub"], font("bold", int(52 * S)), fill=(80, 80, 80))
    elif k == "bignumber":
        col = {"red": RED, "blue": BLUE, "green": GREEN, "gold": GOLD}.get(v.get("color", "red"), RED)
        has_icon = bool(v.get("icon"))
        nx = cx + (170 * S if has_icon and long else 0)
        avail = (w - 2 * abs(nx - cx) - (520 * S if has_icon and long else 0)) * 0.9 if long else w * 0.9
        f = fit_font("black", int(v.get("size", 260) * S), v["value"], int(avail))
        draw_text(d, (nx, h * (0.36 if long or not has_icon else 0.40)), v["value"], f, fill=col, stroke=int(8 * S), stroke_fill=INK)
        if v.get("caption"):  # 화면 밖으로 넘치지 않게: 크기를 줄이고 그래도 길면 두 줄
            left = (w * 0.17 + 160 * S) if (has_icon and long) else 40 * S
            capw = 2 * min(nx - left, w - nx - 40 * S)
            cf = fit_font("xbold", int(64 * S), v["caption"], int(capw), min_size=int(46 * S))
            cap = "\n".join(wrap(v["caption"], cf, int(capw)))
            draw_text(d, (nx, h * 0.62 + (cf.size * 0.6 if "\n" in cap else 0)), cap, cf, fill=INK)
        if has_icon:
            ix = w * 0.17 if long else cx
            iy = h * 0.36 if long else h * 0.12
            icon(img, v["icon"], ix, iy, (300 if long else 170) * S, v.get("icon_text"))
    elif k == "bars":
        _bars(img, d, v, w, h, S, usable_bottom)
    elif k == "line":
        _line(img, d, v, w, h, S, usable_bottom)
    elif k == "compare":
        _compare(img, d, v, w, h, S)
    elif k == "checklist":
        _checklist(img, d, v, w, h, S)
    elif k == "flow":
        _flow(img, d, v, w, h, S)
    elif k == "icons":
        items = v["items"]
        n = len(items)
        gap = w / (n + 1)
        for i, it in enumerate(items):
            x = gap * (i + 1)
            icon(img, it["kind"], x, h * 0.36, (260 if long else 200) * S, it.get("text"), hex2rgb(it["color"]) if it.get("color") else None)
            if it.get("label"):
                draw_text(d, (x, h * 0.62), it["label"], font("xbold", int(52 * S)), fill=INK)
        if v.get("caption"):
            draw_text(d, (cx, h * 0.08), v["caption"], font("black", int(64 * S)), fill=INK)
    else:
        raise ValueError(f"알 수 없는 장면 타입: {k}")
    return img


def _bubble(img, x, y, text, S, max_w, tail_x=None):
    d = ImageDraw.Draw(img)
    f = font("xbold", int(46 * S))
    lines = wrap(text, f, max_w)
    tw = max(text_w(f, l) for l in lines)
    lh = int(f.size * 1.25)
    bw, bh = tw + 60 * S, lh * len(lines) + 40 * S
    x0 = max(10, min(img.width - bw - 10, x - bw / 2))
    rounded(d, [x0, y, x0 + bw, y + bh], int(28 * S), fill=WHITE, outline=INK, width=int(5 * S))
    tx = tail_x if tail_x is not None else x0 + bw / 2
    d.polygon([(tx - 18 * S, y + bh - 3), (tx + 18 * S, y + bh - 3), (tx, y + bh + 34 * S)], fill=WHITE, outline=INK)
    d.line([(tx - 18 * S, y + bh - 3), (tx + 18 * S, y + bh - 3)], fill=WHITE, width=int(7 * S))
    draw_text(d, (x0 + bw / 2, y + bh / 2), "\n".join(lines), f, fill=INK, spacing=1.25)


def _panel(d, w, h, S, title=None):
    long = w > h
    box = [w * (0.12 if long else 0.06), h * 0.06, w * (0.88 if long else 0.94), h * 0.76]
    rounded(d, box, int(24 * S), fill=WHITE, outline=INK, width=int(5 * S))
    if title:
        draw_text(d, ((box[0] + box[2]) / 2, box[1] + 70 * S), title, font("black", int(62 * S)), fill=INK)
    return box


def fmt_num(val, unit=""):
    """그래프 숫자 표기: 천 단위 쉼표, '만' 단위가 1만 이상이면 억으로 (18226만 → 1억 8,226만)."""
    if unit == "만" and abs(val) >= 10000:
        eok, man = divmod(int(round(abs(val))), 10000)
        sign = "-" if val < 0 else ""
        return f"{sign}{eok}억" + (f" {man:,}만" if man else "")
    if float(val).is_integer():
        return f"{int(val):,}{unit}"
    return f"{val:,g}{unit}"


def _bars(img, d, v, w, h, S, _ub):
    box = _panel(d, w, h, S, v.get("title"))
    items = v["items"]
    unit = v.get("unit", "")
    vmax = max(abs(x[1]) for x in items) or 1
    colors = [BLUE, (235, 104, 52), GREEN, GOLD]
    top = box[1] + 150 * S
    rowh = min(160 * S, (box[3] - top - 30 * S) / len(items))
    lx = box[0] + 40 * S
    label_w = max(text_w(font("xbold", int(46 * S)), str(x[0])) for x in items) + 30 * S
    bx0 = lx + label_w
    vf = font("black", int(52 * S))
    bmax = box[2] - bx0 - max(200 * S, max(text_w(vf, "+" + fmt_num(x[1], unit)) for x in items) + 50 * S)
    for i, (label, val) in enumerate(items):
        y = top + i * rowh + rowh / 2
        draw_text(d, (lx, y), str(label), font("xbold", int(46 * S)), fill=INK, anchor="lm")
        bw = max(6, bmax * abs(val) / vmax)
        col = colors[i % len(colors)] if v.get("highlight") is None else (RED if i == v["highlight"] else (170, 170, 170))
        txt = fmt_num(val, unit)
        if v.get("signed"):  # 수익률: 플러스 빨강 '+', 마이너스 파랑 (한국 증시 색)
            col = RED if val >= 0 else BLUE
            txt = ("+" if val > 0 else "") + txt
        d.rounded_rectangle([bx0, y - rowh * 0.3, bx0 + bw, y + rowh * 0.3], radius=int(8 * S), fill=col)
        draw_text(d, (bx0 + bw + 20 * S, y), txt, vf, fill=col if v.get("signed") else INK, anchor="lm")
    if v.get("source"):
        draw_text(d, (box[2] - 20 * S, box[3] - 28 * S), f"자료: {v['source']}", font("medium", int(26 * S)), fill=(120, 120, 120), anchor="rm")


def _line(img, d, v, w, h, S, _ub):
    box = _panel(d, w, h, S, v.get("title"))
    vals = v["values"]
    labels = v.get("labels", [""] * len(vals))
    x0, x1 = box[0] + 90 * S, box[2] - 90 * S
    y0, y1 = box[1] + 170 * S, box[3] - 90 * S
    lo, hi = min(vals), max(vals)
    if hi == lo:
        hi = lo + 1
    pts = [(x0 + (x1 - x0) * i / max(1, len(vals) - 1), y1 - (y1 - y0) * (val - lo) / (hi - lo)) for i, val in enumerate(vals)]
    d.line([(x0, y1), (x1, y1)], fill=(200, 200, 200), width=int(3 * S))
    col = {"red": RED, "blue": BLUE, "green": GREEN}.get(v.get("color", "red"), RED)
    d.line(pts, fill=col, width=int(10 * S), joint="curve")
    unit = v.get("unit", "")
    for i, (p, val) in enumerate(zip(pts, vals)):
        d.ellipse([p[0] - 12 * S, p[1] - 12 * S, p[0] + 12 * S, p[1] + 12 * S], fill=WHITE, outline=col, width=int(6 * S))
        if i in (0, len(vals) - 1) or v.get("all_labels"):
            draw_text(d, (p[0], p[1] - 45 * S), fmt_num(val, unit), font("black", int(44 * S)), fill=INK)
        draw_text(d, (p[0], y1 + 40 * S), str(labels[i]), font("bold", int(32 * S)), fill=(90, 90, 90))
    if v.get("box"):  # 증거 강조: 구간을 빨간 점선 박스로 (레퍼런스의 '차트 캡처 + 점선 박스' 연출)
        i0, i1 = v["box"][:2]
        xs = [pts[k][0] for k in range(i0, i1 + 1)]
        ys = [pts[k][1] for k in range(i0, i1 + 1)]
        bx0, bx1 = min(xs) - 40 * S, max(xs) + 40 * S
        by0, by1 = min(ys) - 80 * S, max(y1, max(ys)) + 10 * S
        dash = int(22 * S)
        for x in range(int(bx0), int(bx1), dash * 2):
            d.line([(x, by0), (min(x + dash, bx1), by0)], fill=RED, width=int(6 * S))
            d.line([(x, by1), (min(x + dash, bx1), by1)], fill=RED, width=int(6 * S))
        for y in range(int(by0), int(by1), dash * 2):
            d.line([(bx0, y), (bx0, min(y + dash, by1))], fill=RED, width=int(6 * S))
            d.line([(bx1, y), (bx1, min(y + dash, by1))], fill=RED, width=int(6 * S))
        if len(v["box"]) > 2:
            draw_text(d, ((bx0 + bx1) / 2, by0 - 34 * S), str(v["box"][2]), font("black", int(40 * S)), fill=RED)
    if v.get("source"):
        draw_text(d, (box[2] - 20 * S, box[3] - 24 * S), f"자료: {v['source']}", font("medium", int(26 * S)), fill=(120, 120, 120), anchor="rm")


def _compare(img, d, v, w, h, S):
    long = w > h
    cx = w / 2
    for side, sg, col in (("left", -1, BLUE), ("right", 1, RED)):
        it = v[side]
        x = cx + sg * (w * 0.24 if long else w * 0.25)
        bw = (w * 0.36 if long else w * 0.44) / 2
        rounded(d, [x - bw, h * 0.06, x + bw, h * 0.74], int(26 * S), fill=WHITE, outline=INK, width=int(5 * S))
        d.rounded_rectangle([x - bw, h * 0.06, x + bw, h * 0.17], radius=int(26 * S), fill=hex2rgb(it["color"]) if it.get("color") else col)
        draw_text(d, (x, h * 0.115), it["title"], font("black", int(54 * S)), fill=WHITE)
        if it.get("icon"):
            icon(img, it["icon"], x, h * 0.34, 220 * S, it.get("icon_text"))
        f = font("black", int((96 if len(it.get("value", "")) < 7 else 70) * S))
        draw_text(d, (x, h * 0.55), it.get("value", ""), f, fill=INK)
        if it.get("note"):
            draw_text(d, (x, h * 0.66), it["note"], font("bold", int(36 * S)), fill=(90, 90, 90))
    vs = v.get("mid", "VS")
    d.ellipse([cx - 70 * S, h * 0.40 - 70 * S, cx + 70 * S, h * 0.40 + 70 * S], fill=YELLOW, outline=INK, width=int(6 * S))
    draw_text(d, (cx, h * 0.40), vs, font("black", int(54 * S)), fill=INK)


def _checklist(img, d, v, w, h, S):
    box = _panel(d, w, h, S, v.get("title"))
    items = v["items"]
    checked = v.get("checked", len(items))
    top = box[1] + 160 * S
    rowh = min(110 * S, (box[3] - top - 20 * S) / len(items))
    f = font("xbold", int(48 * S))
    for i, it in enumerate(items):
        y = top + i * rowh + rowh / 2
        x = box[0] + 60 * S
        rounded(d, [x, y - 28 * S, x + 56 * S, y + 28 * S], int(10 * S), fill=WHITE, outline=INK, width=int(5 * S))
        if i < checked:
            d.line([(x + 10 * S, y), (x + 24 * S, y + 16 * S), (x + 50 * S, y - 22 * S)], fill=GREEN, width=int(10 * S))
        draw_text(d, (x + 90 * S, y), it, f, fill=INK if i < checked else (150, 150, 150), anchor="lm")


def _flow(img, d, v, w, h, S):
    steps = v["steps"]
    n = len(steps)
    long = w > h
    hi = v.get("highlight", n - 1)
    if long:
        gap = w / n
        for i, st in enumerate(steps):
            x = gap * (i + 0.5)
            col = YELLOW if i == hi else WHITE
            rounded(d, [x - gap * 0.38, h * 0.26, x + gap * 0.38, h * 0.54], int(24 * S), fill=col, outline=INK, width=int(6 * S))
            draw_text(d, (x, h * 0.20), f"{i + 1}단계", font("black", int(40 * S)), fill=(90, 90, 90))
            f = font("black", int(54 * S))
            draw_text(d, (x, h * 0.40), "\n".join(wrap(st, f, int(gap * 0.68))), f, fill=INK)
            if i < n - 1:
                ax = x + gap * 0.42
                d.polygon([(ax, h * 0.37), (ax + gap * 0.12, h * 0.40), (ax, h * 0.43)], fill=INK)
    else:
        gap = (h * 0.68) / n
        for i, st in enumerate(steps):
            y = h * 0.06 + gap * (i + 0.5)
            col = YELLOW if i == hi else WHITE
            rounded(d, [w * 0.14, y - gap * 0.36, w * 0.86, y + gap * 0.36], int(22 * S), fill=col, outline=INK, width=int(5 * S))
            draw_text(d, (w / 2, y), f"{i + 1}. {st}", font("black", int(52 * S)), fill=INK)
