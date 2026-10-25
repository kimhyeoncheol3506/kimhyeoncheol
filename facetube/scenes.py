"""장면 종류별 그리기. 모든 함수는 (ctx, sc, t, ci, amp, st) 를 받는다.
t = 장면 안 시간(초), ci = 현재 자막 덩어리 번호, amp = 내레이션 음량(0~1, 입모양), st = style."""
import math
import functools
import cairo
from PIL import Image

from .gfx import (rgba, simple_text, text_surface, blit, rounded_rect, wrap_by_width, font,
                  ease_out, ease_out_back, ease_in_out, pil_to_surface, missing_glyphs, FALLBACK)
from .character import draw_person, draw_prop

W, H = 1920, 1080
GROUND = 0.80


def balanced_wrap(text, fontname, size, max_w):
    """한 줄에 안 들어가면 두 줄 길이가 비슷하도록 어절 단위로 나눈다."""
    f = font(fontname, size)
    if f.getlength(text) <= max_w:
        return [text]
    words = text.split(" ")
    best = min(range(1, len(words)), key=lambda i: abs(f.getlength(" ".join(words[:i])) - f.getlength(" ".join(words[i:]))))
    return [" ".join(words[:best]), " ".join(words[best:])]


def chunk_t(sc, i):
    """i번째 덩어리 시작(장면 기준 초). 범위를 넘으면 끝 값."""
    ch = sc["chunks"]
    if not ch:
        return 0.0
    i = max(0, min(i, len(ch) - 1))
    return ch[i]["start"] - sc["start"]


def per_chunk(v, ci):
    if isinstance(v, list):
        return v[min(ci, len(v) - 1)]
    return v


def background(ctx, sc, t, st):
    col = sc.get("bg") or st["palette"]["bg"][sc["index"] % len(st["palette"]["bg"])]
    ctx.set_source_rgba(*rgba(col))
    ctx.paint()
    g = cairo.RadialGradient(W / 2, H * 0.45, 80, W / 2, H * 0.45, W * 0.75)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.35)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.10)
    ctx.set_source(g)
    ctx.paint()
    # 은은하게 떠다니는 점 패턴
    ctx.set_source_rgba(1, 1, 1, 0.22)
    for k in range(18):
        x = (k * 263 + t * 12 * (1 + k % 3)) % (W + 80) - 40
        y = (k * 157) % H
        ctx.arc(x, y, 6 + (k % 4) * 4, 0, 2 * math.pi)
        ctx.fill()


def draw_cast(ctx, sc, t, ci, amp, st, default_x=None, scale=1.25, ground=None):
    cast = sc.get("cast") or [{}]
    shirts = st["character"]["shirt"]
    speaker = sc.get("speaker", 0)
    for k, c in enumerate(cast):
        x = c.get("x", default_x if default_x is not None else (0.5 if len(cast) == 1 else 0.3 + 0.4 * k / max(1, len(cast) - 1))) * W
        gy = (c.get("y") or ground or GROUND) * H
        pose = per_chunk(c.get("pose", "talk"), ci)
        draw_person(ctx, x, gy, t, pose=pose, talk_amp=amp if k == speaker else 0.0,
                    scale=c.get("scale", scale), shirt=c.get("shirt") or shirts[k % len(shirts)],
                    facing=c.get("facing", -1 if x > 0.62 * W else 1),  # 오른쪽 캐릭터는 자료 쪽을 봄
                    appear_t=t - chunk_t(sc, c.get("at", 0)) + (0.3 if c.get("at", 0) == 0 else 0),
                    seed=k)
    for p in sc.get("props", []):
        at = p.get("at", 0)
        draw_prop(ctx, p["kind"], p.get("x", 0.65) * W, p.get("y", 0.35) * H, t, scale=p.get("scale", 1.0),
                  appear_t=t - chunk_t(sc, at))


# ------------------------------------------------------------------ stage
def draw_stage(ctx, sc, t, ci, amp, st):
    draw_cast(ctx, sc, t, ci, amp, st)
    if sc.get("bubble"):
        b = sc["bubble"]
        txt = per_chunk(b if isinstance(b, (str, list)) else b["text"], ci)
        surf = simple_text(txt, "Pretendard-ExtraBold.otf", 58, color="#1B1B1B", box="#FFFFFF")
        x, y = 0.5 * W + 300, 0.36 * H
        a = ease_out_back(min(1, t / 0.25))
        blit(ctx, surf, x, y, scale=a)


# ------------------------------------------------------------------ headline (기사 제목 카드)
@functools.lru_cache(maxsize=32)
def _headline_layout(title, maxw, size):
    return wrap_by_width(title, "Pretendard-Bold.otf", size, maxw)


def draw_headline(ctx, sc, t, ci, amp, st):
    cw, x0 = 1400, (W - 1400) / 2
    title = sc["title"]
    size = 70
    lines = _headline_layout(title, cw - 140, size)
    lh = size * 1.32
    ch = 150 + lh * len(lines) + 70
    y0 = max(150, H * 0.44 - ch / 2)
    k = ease_out_back(min(1, t / 0.32))
    ctx.save()
    ctx.translate(W / 2, y0 + ch / 2 + (1 - k) * 500)
    ctx.rotate(math.radians(-1.2))
    ctx.translate(-W / 2, -(y0 + ch / 2))
    # 그림자 + 카드
    rounded_rect(ctx, x0 + 10, y0 + 16, cw, ch, 26)
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.fill()
    rounded_rect(ctx, x0, y0, cw, ch, 26)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.fill()
    # 머리띠: 매체명(텍스트, 로고 아님) + 날짜
    oc = sc.get("outlet_color", "#1F4E9E")
    ctx.rectangle(x0 + 70, y0 + 52, 10, 50)
    ctx.set_source_rgba(*rgba(oc))
    ctx.fill()
    blit(ctx, simple_text(sc.get("outlet", ""), "Pretendard-Black.otf", 44, color=oc), x0 + 96, y0 + 78, anchor="left")
    if sc.get("date"):
        blit(ctx, simple_text(sc["date"], "Pretendard-Medium.otf", 36, color="#888888"), x0 + cw - 70, y0 + 78, anchor="right")
    ctx.rectangle(x0 + 70, y0 + 128, cw - 140, 3)
    ctx.set_source_rgba(0.88, 0.88, 0.88, 1)
    ctx.fill()
    # 형광펜 강조
    hl = sc.get("highlight")
    f = font("Pretendard-Bold.otf", size)
    ty = y0 + 150 + lh / 2
    if hl:
        p = min(1, max(0, (t - chunk_t(sc, sc.get("highlight_at", 1))) / 0.35))
        for i, line in enumerate(lines):
            j = line.find(hl)
            if j >= 0 and p > 0:
                lw = f.getlength(line)
                lx = W / 2 - lw / 2 + f.getlength(line[:j])
                ww = f.getlength(hl) * ease_out(p)
                ctx.rectangle(lx - 6, ty + i * lh - size * 0.05, ww + 12, size * 0.62)
                ctx.set_source_rgba(*rgba(st["palette"]["highlight"], 0.9))
                ctx.fill()
    for i, line in enumerate(lines):
        blit(ctx, simple_text(line, "Pretendard-Bold.otf", size, color="#151515"), W / 2, ty + i * lh)
    ctx.restore()
    _mini_presenter(ctx, sc, t, ci, amp, st)


def _mini_presenter(ctx, sc, t, ci, amp, st):
    if sc.get("presenter", True):
        pose = per_chunk(sc.get("pose", "point"), ci)
        draw_person(ctx, 0.12 * W, 1.0 * H - 30, t, pose=pose, talk_amp=amp, scale=0.78,
                    shirt=st["character"]["shirt"][0], appear_t=t + 0.3)


# ------------------------------------------------------------------ number (숫자 카운트업)
def draw_number(ctx, sc, t, ci, amp, st):
    at = chunk_t(sc, sc.get("reveal_at", 0))
    p = max(0.0, min(1.0, (t - at - 0.05) / sc.get("count_sec", 0.8)))
    target = float(str(sc["value"]).replace(",", ""))
    v = target * ease_out(p)
    dec = len(str(sc["value"]).split(".")[1]) if "." in str(sc["value"]) else 0
    s = f"{v:,.{dec}f}" if sc.get("comma", True) else f"{v:.{dec}f}"
    if sc.get("label"):
        blit(ctx, simple_text(sc["label"], "Pretendard-ExtraBold.otf", 64, color="#1B1B1B"), W * 0.42, H * 0.25)
    if t >= at:
        k = 1 + 0.18 * max(0, 1 - (t - at - sc.get("count_sec", 0.8)) / 0.25) * (p >= 1)
        num = simple_text(s, "BlackHanSans.ttf", 300, color=st["palette"]["accent"], stroke=10, stroke_color="#1B1B1B")
        unit = simple_text(sc.get("unit", ""), "BlackHanSans.ttf", 150, color="#1B1B1B")
        total = num.get_width() + unit.get_width()
        cx = W * 0.42 - total / 2
        blit(ctx, num, cx + num.get_width() / 2, H * 0.50, scale=k)
        blit(ctx, unit, cx + num.get_width() + unit.get_width() / 2, H * 0.50 + 55)
    if sc.get("sub"):
        blit(ctx, simple_text(sc["sub"], "Pretendard-Bold.otf", 46, color="#444444"), W * 0.42, H * 0.70)
    draw_cast(ctx, sc, t, ci, amp, st, default_x=0.83, scale=1.05, ground=0.86)


# ------------------------------------------------------------------ compare (막대 비교)
def draw_compare(ctx, sc, t, ci, amp, st):
    items = sc["items"]
    vmax = max(float(i["value"]) for i in items)
    x0, maxw, bh = 470, 780, 130
    y = H * 0.47 - (len(items) * (bh + 60)) / 2 + bh / 2 + 30
    if sc.get("label"):
        blit(ctx, simple_text(sc["label"], "Pretendard-ExtraBold.otf", 64), W * 0.45, 190)
    for k, it in enumerate(items):
        at = chunk_t(sc, it.get("at", 0)) + k * 0.15
        p = ease_out(min(1, max(0, (t - at) / 0.7)))
        col = it.get("color") or [st["palette"]["accent2"], st["palette"]["accent"]][k % 2]
        blit(ctx, simple_text(it["label"], "Pretendard-ExtraBold.otf", 60), x0 - 30, y, anchor="right")
        w = maxw * float(it["value"]) / vmax * p
        if w > 2:
            rounded_rect(ctx, x0, y - bh / 2, w, bh, 20)
            ctx.set_source_rgba(*rgba(col))
            ctx.fill_preserve()
            ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
            ctx.set_line_width(6)
            ctx.stroke()
        if p > 0.05:
            val = float(it["value"]) * p
            txt = f"{val:,.0f}{it.get('unit', sc.get('unit', ''))}"
            blit(ctx, simple_text(txt, "BlackHanSans.ttf", 88, color="#1B1B1B"), x0 + w + 24, y, anchor="left")
        y += bh + 60
    draw_cast(ctx, sc, t, ci, amp, st, default_x=0.88, scale=0.95, ground=0.86)


# ------------------------------------------------------------------ title (오늘의 주제 카드)
def draw_title(ctx, sc, t, ci, amp, st):
    ctx.set_source_rgba(*rgba(sc.get("band", "#1B1B1B")))
    k = ease_out(min(1, t / 0.3))
    ctx.rectangle(0, H * 0.22, W * k, H * 0.36)
    ctx.fill()
    if sc.get("kicker"):
        chip = simple_text(sc["kicker"], "Pretendard-Black.otf", 44, color="#1B1B1B", box=st["palette"]["highlight"])
        blit(ctx, chip, W / 2, H * 0.22, scale=ease_out_back(min(1, max(0, t - 0.1) / 0.3)))
    lines = balanced_wrap(sc["title"], "BlackHanSans.ttf", 112, W - 300)
    for i, ln in enumerate(lines):
        s = simple_text(ln, "BlackHanSans.ttf", 112, color="#FFFFFF")
        blit(ctx, s, W / 2, H * 0.40 + (i - (len(lines) - 1) / 2) * 128, scale=ease_out_back(min(1, max(0, t - 0.15) / 0.35)))
    sc.setdefault("cast", [{"pose": "happy", "x": 0.18}, {"pose": "point", "x": 0.82, "facing": -1}])
    draw_cast(ctx, sc, t, ci, amp, st, scale=0.9, ground=0.93)


# ------------------------------------------------------------------ list (체크리스트)
def draw_list(ctx, sc, t, ci, amp, st):
    items = sc["items"]
    if sc.get("label"):
        blit(ctx, simple_text(sc["label"], "Pretendard-Black.otf", 66), W * 0.40, 150)
    for k, it in enumerate(items):
        at = chunk_t(sc, it.get("at", k)) if isinstance(it, dict) else chunk_t(sc, k)
        text = it["text"] if isinstance(it, dict) else it
        if t < at:
            continue
        p = ease_out_back(min(1, (t - at) / 0.3))
        y = 290 + k * 125
        ctx.save()
        ctx.translate(-(1 - p) * 200, 0)
        rounded_rect(ctx, 240, y - 50, 1100, 100, 24)
        ctx.set_source_rgba(1, 1, 1, 0.95)
        ctx.fill()
        blit(ctx, simple_text(f"{k + 1}", "BlackHanSans.ttf", 64, color=st["palette"]["accent"]), 300, y)
        blit(ctx, simple_text(text, "Pretendard-ExtraBold.otf", 54), 360, y, anchor="left")
        ctx.restore()
    draw_cast(ctx, sc, t, ci, amp, st, default_x=0.86, scale=1.0, ground=0.86)


# ------------------------------------------------------------------ image (자료 이미지/스크린샷)
@functools.lru_cache(maxsize=16)
def _image_surface(path, maxw, maxh):
    im = Image.open(path).convert("RGBA")
    im.thumbnail((maxw, maxh), Image.LANCZOS)
    return pil_to_surface(im)


def draw_image(ctx, sc, t, ci, amp, st):
    surf = _image_surface(sc["path"], 1500, 760)
    k = ease_out_back(min(1, t / 0.3))
    z = 1.0 + 0.06 * (t / max(0.1, sc["end"] - sc["start"]))
    w, h = surf.get_width(), surf.get_height()
    ctx.save()
    ctx.translate(W / 2, H * 0.45)
    ctx.scale(z * k, z * k)
    rounded_rect(ctx, -w / 2 - 14, -h / 2 - 14, w + 28, h + 28, 20)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.fill()
    ctx.set_source_surface(surf, -w / 2, -h / 2)
    ctx.paint()
    ctx.restore()
    _mini_presenter(ctx, sc, t, ci, amp, st)


# ------------------------------------------------------------------ clip (외부에서 만든 영상·이미지)
@functools.lru_cache(maxsize=48)
def _frame_surface(path):
    return pil_to_surface(Image.open(path).convert("RGBA"))


def draw_clip(ctx, sc, t, ci, amp, st):
    import os
    m = sc["media_info"]
    i = int(t * m["fps"])
    i = i % m["n"] if m.get("loop", True) else min(i, m["n"] - 1)       # 짧으면 반복(정지 화면 금지)
    surf = _frame_surface(os.path.join(m["dir_abs"], f"f_{i + 1:05d}.jpg"))
    w, h = surf.get_width(), surf.get_height()
    k = ease_out_back(min(1, t / 0.3))
    cx, cy = W / 2, H * 0.42
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    rounded_rect(ctx, -w / 2 - 12, -h / 2 - 12, w + 24, h + 24, 22)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.fill()
    ctx.set_source_surface(surf, -w / 2, -h / 2)
    ctx.paint()
    if sc.get("badge"):
        b = simple_text(sc["badge"], "Pretendard-Bold.otf", 30, color="#FFFFFF", box="#000000CC")
        blit(ctx, b, -w / 2 + 14 + b.get_width() / 2, -h / 2 + 14 + b.get_height() / 2)
    ctx.restore()
    _mini_presenter(ctx, sc, t, ci, amp, st)


# ------------------------------------------------------------------ outro (구독 유도)
def draw_outro(ctx, sc, t, ci, amp, st):
    sc.setdefault("cast", [{"pose": ["talk", "wave"], "x": 0.3}])
    draw_cast(ctx, sc, t, ci, amp, st, scale=1.2)
    bx, by = W * 0.66, H * 0.45
    k = ease_out_back(min(1, max(0, t - 0.2) / 0.3))
    clicked = t > sc.get("click_at", 1.6)
    label = "구독중" if clicked else "구독"
    col = "#8A8A8A" if clicked else "#FF2D2D"
    btn = simple_text(label, "Pretendard-Black.otf", 80, color="#FFFFFF", box=col)
    press = 0.92 if abs(t - sc.get("click_at", 1.6)) < 0.08 else 1.0
    blit(ctx, btn, bx, by, scale=k * press * 1.2)
    # 커서
    ca = sc.get("click_at", 1.6)
    p = ease_in_out(min(1, max(0, (t - ca + 0.6) / 0.6)))
    cx, cy = bx + 320 - 290 * p, by + 260 - 230 * p
    if t > 0.4:
        ctx.save()
        ctx.translate(cx, cy)
        ctx.move_to(0, 0)
        for px, py in ((0, 62), (16, 48), (28, 74), (40, 68), (28, 44), (50, 42)):
            ctx.line_to(px, py)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1)
        ctx.set_line_width(4)
        ctx.stroke()
        ctx.restore()
    if clicked:
        draw_prop(ctx, "sparkle", bx + 190, by - 90, t, scale=1.2, appear_t=t - ca)


DRAW = {"clip": draw_clip, "stage": draw_stage, "headline": draw_headline, "number": draw_number, "compare": draw_compare,
        "title": draw_title, "list": draw_list, "image": draw_image, "outro": draw_outro}
