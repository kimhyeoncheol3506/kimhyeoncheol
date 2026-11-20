"""Fonts, in-world text and burned-in captions."""
import functools
import math
import os

import skia

from .paint import C, fill, stroke, argb, INK, HERE

FONT_PATH = os.path.join(HERE, 'fonts', 'Pretendard-ExtraBold.otf')


@functools.lru_cache(maxsize=4)
def typeface(path=FONT_PATH):
    return skia.Typeface.MakeFromFile(path)


@functools.lru_cache(maxsize=256)
def font(size):
    f = skia.Font(typeface(), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def text_width(s, size):
    return font(size).measureText(s)


def draw_text(cv, s, cx, baseline, size, col='#ffffff', outline=None, ow=0.0, align='center', skew=0.0):
    f = font(size)
    w = f.measureText(s)
    x = cx - w / 2 if align == 'center' else (cx - w if align == 'right' else cx)
    blob = skia.TextBlob.MakeFromString(s, f)
    if outline:
        cv.drawTextBlob(blob, x, baseline, stroke(outline, ow))
    cv.drawTextBlob(blob, x, baseline, fill(col))
    return w


# ----------------------------------------------------------------------------- captions
CAP_SIZE = 84            # ~7.8% of 1080 width
CAP_Y = 0.70             # centre of the caption block, fraction of height
CAP_MAX_W = 900          # inside the Shorts safe zone (90 px side margins)


def caption_lines(words, size=CAP_SIZE):
    """1-2 words -> max 2 lines that fit the safe width."""
    txt = ' '.join(words)
    if text_width(txt, size) <= CAP_MAX_W or len(words) == 1:
        return [txt]
    return [words[0], ' '.join(words[1:])]


def draw_caption(cv, words, age, W=1080, H=1920, size=CAP_SIZE):
    """age = seconds since the chunk's onset (drives the quick pop-in)."""
    if not words:
        return
    # pop: 0.86 -> 1.06 -> 1.0 over ~0.12 s
    k = min(1.0, age / 0.12)
    sc = 0.86 + 0.2 * math.sin(k * math.pi * 0.5) if k < 1 else 1.0
    if 0.6 < k < 1.0:
        sc = 1.06 - (k - 0.6) / 0.4 * 0.06
    alpha = min(1.0, age / 0.05 + 0.3)
    lines = caption_lines(words, size)
    lh = size * 1.08
    cy = H * CAP_Y - (len(lines) - 1) * lh / 2
    cv.save()
    cv.translate(W / 2, H * CAP_Y)
    cv.scale(sc, sc)
    cv.translate(-W / 2, -H * CAP_Y)
    for i, ln in enumerate(lines):
        base = cy + i * lh + size * 0.36
        f = font(size)
        w = f.measureText(ln)
        blob = skia.TextBlob.MakeFromString(ln, f)
        x = W / 2 - w / 2
        sh = skia.Paint(AntiAlias=True)
        sh.setColor4f(C((0x1b, 0x12, 0x20), 0.55 * alpha))
        sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 7))
        cv.drawTextBlob(blob, x + 3, base + 6, sh)
        cv.drawTextBlob(blob, x, base, stroke((0x1b, 0x12, 0x20), 8.5, alpha))
        cv.drawTextBlob(blob, x, base, fill('#ffffff', alpha))
    cv.restore()
