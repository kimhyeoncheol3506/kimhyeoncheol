"""cairo 그리기 도우미 + PIL 글자 렌더링(→ cairo 표면) 캐시."""
import functools
import math
import os
import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
FALLBACK = "Pretendard-Black.otf"


def rgba(hexstr, a=None):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    al = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
    return (r, g, b, al if a is None else a)


def rgb255(hexstr):
    r, g, b, a = rgba(hexstr)
    return (int(r * 255), int(g * 255), int(b * 255), int(a * 255))


@functools.lru_cache(maxsize=64)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


@functools.lru_cache(maxsize=16)
def cmap(name):
    from fontTools.ttLib import TTFont
    return set(TTFont(os.path.join(FONT_DIR, name)).getBestCmap().keys())


def missing_glyphs(name, text):
    cm = cmap(name)
    return sorted({c for c in text if not c.isspace() and ord(c) not in cm})


def pil_to_surface(im):
    im = im.convert("RGBA")
    arr = np.asarray(im).astype(np.float32)
    a = arr[..., 3:4] / 255.0
    pre = np.concatenate([arr[..., :3] * a, arr[..., 3:4]], axis=2).astype(np.uint8)
    bgra = pre[..., [2, 1, 0, 3]].copy(order="C")
    h, w = bgra.shape[:2]
    data = bytearray(bgra.tobytes())
    surf = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, w, h, w * 4)
    return surf


def text_image(segments, fontname, size, stroke=0, stroke_color="#000000", shadow=None, align="center",
               line_gap=0.18, box=None, box_pad=(28, 14), box_radius=18):
    """segments: [[(text, color), ...] , ...]  (줄 목록, 각 줄은 색 구간 목록) -> PIL RGBA"""
    alltext = "".join(t for segs in segments for t, _ in segs)
    if missing_glyphs(fontname, alltext):   # 글리프 없는 글자(두부 □) 방지: 대체 글꼴
        fontname = FALLBACK
    f = font(fontname, size)
    lines = []
    for segs in segments:
        w = sum(f.getlength(t) for t, _ in segs)
        lines.append((segs, w))
    asc, desc = f.getmetrics()
    lh = asc + desc
    W = int(max(w for _, w in lines) + stroke * 2 + 8)
    H = int(lh * len(lines) + lh * line_gap * (len(lines) - 1) + stroke * 2 + 8)
    pad = 24 if shadow else 4
    bx, by = (box_pad if box else (0, 0))
    im = Image.new("RGBA", (W + pad * 2 + bx * 2, H + pad * 2 + by * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle([pad, pad, im.width - pad, im.height - pad], radius=box_radius, fill=rgb255(box))
    def draw_all(dd, dx, dy, fill_override=None, stroke_w=stroke):
        y = pad + by + stroke + 4 + dy
        for segs, w in lines:
            x = pad + bx + stroke + 4 + dx + ((W - stroke * 2 - 8 - w) / 2 if align == "center" else 0)
            for t, col in segs:
                dd.text((x, y), t, font=f, fill=rgb255(fill_override or col),
                        stroke_width=stroke_w, stroke_fill=rgb255(stroke_color))
                x += f.getlength(t)
            y += lh * (1 + line_gap)
    if shadow:
        sx, sy, sc = shadow
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        draw_all(ImageDraw.Draw(sh), sx, sy, fill_override=sc, stroke_w=stroke)
        sh = sh.filter(ImageFilter.GaussianBlur(4))
        sh.alpha_composite(im)
        im = sh
        d = ImageDraw.Draw(im)
    draw_all(d, 0, 0)
    return im


@functools.lru_cache(maxsize=512)
def text_surface(key_segments, fontname, size, stroke=0, stroke_color="#000000", shadow=None, align="center",
                 box=None):
    segs = [list(line) for line in key_segments]
    return pil_to_surface(text_image(segs, fontname, size, stroke, stroke_color, shadow, align, box=box))


def simple_text(text, fontname, size, color="#1B1B1B", **kw):
    return text_surface(((( text, color),),), fontname, size, **kw)


def wrap_by_width(text, fontname, size, max_w):
    f = font(fontname, size)
    out, cur = [], ""
    for word in text.split(" "):
        cand = (cur + " " + word).strip()
        if f.getlength(cand) > max_w and cur:
            out.append(cur)
            cur = word
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


def blit(ctx, surf, cx, cy, scale=1.0, alpha=1.0, anchor="center", rot=0.0):
    if scale <= 0.002 or alpha <= 0:
        return
    w, h = surf.get_width(), surf.get_height()
    ctx.save()
    ctx.translate(cx, cy)
    if rot:
        ctx.rotate(rot)
    ctx.scale(scale, scale)
    ox = {"center": -w / 2, "left": 0, "right": -w}[anchor if anchor in ("center", "left", "right") else "center"]
    ctx.set_source_surface(surf, ox, -h / 2)
    ctx.paint_with_alpha(alpha) if alpha < 1 else ctx.paint()
    ctx.restore()


def rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def ease_out_back(t, k=1.70158):
    t = min(max(t, 0), 1) - 1
    return t * t * ((k + 1) * t + k) + 1


def ease_out(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = min(max(t, 0), 1)
    return 3 * t * t - 2 * t * t * t


def pop_scale(t, dur=0.22, overshoot=1.25):
    if t >= dur:
        return 1.0
    x = t / dur
    if x < 0.6:
        return overshoot * ease_out(x / 0.6)
    return overshoot + (1 - overshoot) * ease_in_out((x - 0.6) / 0.4)
