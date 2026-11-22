"""In-world explanation props: everything that explains lives inside the set (no floating cards).

Every prop draws centred on (x, y) at size scale s (1.0 ~ 300 px wide) and works both baked into a set and live
(animated) in a layer. Text props take short strings.
"""
import math

import skia

from .paint import (fill, stroke, ink, shade, mix, path_poly, path_smooth, rrect, ellipse, blurred, lin_grad, rad_grad,
                    argb, rng, INK)
from .text import draw_text, text_width


def planet(cv, x, y, r, base='#4f8ad8', bands=None, land=None, ring=None, seed=0, craters=0, lit=(-0.5, -0.6)):
    """A cartoon planet: bands or continents, craters, terminator shade, highlight, optional ring."""
    rr = rng(seed)
    if ring:
        rp = skia.Path(); rp.addOval(skia.Rect.MakeLTRB(x - r * 1.9, y - r * 0.45, x + r * 1.9, y + r * 0.45))
        hole = skia.Path(); hole.addOval(skia.Rect.MakeLTRB(x - r * 1.35, y - r * 0.25, x + r * 1.35, y + r * 0.25))
        ringp = skia.Op(rp, hole, skia.PathOp.kDifference_PathOp)
        cv.save(); cv.clipRect(skia.Rect.MakeLTRB(x - r * 3, y - r * 3, x + r * 3, y))
        cv.drawPath(ringp, fill(shade(ring, -0.2))); cv.drawPath(ringp, ink(max(1.5, r * 0.035)))
        cv.restore()
    body = ellipse(x, y, r, r)
    cv.drawPath(body, fill(base))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    if bands:
        for k, col in enumerate(bands):
            yy = y - r + (k + 0.5) * 2 * r / len(bands)
            cv.drawPath(path_smooth([(x - r * 1.2, yy - r * 0.08), (x, yy + r * 0.06), (x + r * 1.2, yy - r * 0.05),
                                     (x + r * 1.2, yy + r * 0.12), (x, yy + r * 0.22), (x - r * 1.2, yy + r * 0.1)]), fill(col))
    if land:
        for k in range(5):
            cx, cy = x + rr.uniform(-0.7, 0.7) * r, y + rr.uniform(-0.7, 0.7) * r
            pts = [(cx + math.cos(a) * r * rr.uniform(0.15, 0.32), cy + math.sin(a) * r * rr.uniform(0.12, 0.28)) for a in [i * 0.9 for i in range(7)]]
            cv.drawPath(path_smooth(pts), fill(land))
        cv.drawPath(ellipse(x, y - r * 0.92, r * 0.5, r * 0.16), fill('#f4f8ff'))
    for k in range(craters):
        cx, cy, cr = x + rr.uniform(-0.6, 0.6) * r, y + rr.uniform(-0.6, 0.6) * r, r * rr.uniform(0.08, 0.16)
        cv.drawPath(ellipse(cx, cy, cr, cr * 0.8), fill(shade(base, -0.25)))
        cv.drawPath(ellipse(cx - cr * 0.15, cy - cr * 0.15, cr * 0.7, cr * 0.5), fill(shade(base, 0.12)))
    sh = skia.Path(); sh.addCircle(x + r * 0.45, y + r * 0.4, r * 1.05)
    lit_ = skia.Path(); lit_.addCircle(x - r * 0.1, y - r * 0.1, r * 0.95)
    cv.drawPath(skia.Op(sh, lit_, skia.PathOp.kDifference_PathOp), fill('#2a1e48', 0.45))
    cv.drawPath(ellipse(x + lit[0] * r * 0.6, y + lit[1] * r * 0.6, r * 0.22, r * 0.14), fill('#ffffff', 0.55))
    cv.restore()
    cv.drawPath(body, ink(max(2, r * 0.05)))
    if ring:
        cv.save(); cv.clipRect(skia.Rect.MakeLTRB(x - r * 3, y, x + r * 3, y + r * 3))
        cv.drawPath(ringp, fill(ring)); cv.drawPath(ringp, ink(max(1.5, r * 0.035)))
        cv.restore()


PLANETS = {
    'earth': dict(base='#3f7ad8', land='#5ab04a'),
    'gas': dict(base='#e0a050', bands=['#c87a3a', '#f0c070', '#d8904a', '#f4d090', '#c06a30']),
    'ringed': dict(base='#e8c87a', bands=['#d8b060', '#f0d890', '#caa050'], ring='#c8a0e8'),
    'shiny': dict(base='#8fd8f0', craters=0, bands=['#a8e8ff', '#7ac8e8']),
    'moon': dict(base='#b8b0c8', craters=7),
    'red': dict(base='#d8603a', craters=5),
    'purple': dict(base='#9a6ad8', bands=['#b88af0', '#7a4ab8', '#a87ae0'], ring='#f2c640'),
}


def planet_kind(cv, x, y, r, kind, seed=0):
    planet(cv, x, y, r, seed=seed, **PLANETS[kind])


def price_tag(cv, x, y, text, s=1.0, col='#f8f2e2', ink_col='#c8343c', angle=-8):
    cv.save(); cv.translate(x, y); cv.rotate(angle); cv.scale(s, s)
    w = max(120, text_width(text, 64) + 60)
    tag = path_poly([(-w / 2 + 30, -46), (w / 2, -46), (w / 2, 46), (-w / 2 + 30, 46), (-w / 2, 0)])
    cv.drawPath(tag, fill(col)); cv.drawPath(tag, ink(5))
    cv.drawCircle(-w / 2 + 28, 0, 8, fill('#2a1e28'))
    cv.drawLine(-w / 2 + 28, 0, -w / 2 - 30, -60, stroke('#c8a050', 3))
    draw_text(cv, text, 15, 22, 64, ink_col)
    cv.restore()


def register(cv, x, y, s=1.0, display='0.99', E=None):
    """Retro cash register with a glowing display (E receives an emitter)."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    body = path_poly([(-160, 0), (160, 0), (130, -170), (-130, -170)])
    cv.drawPath(body, fill('#c8603a')); cv.drawPath(body, ink(5))
    for k in range(3):
        for j in range(4):
            kx, ky = -90 + j * 50, -130 + k * 40
            cv.drawPath(rrect(kx - 18, ky - 13, 36, 26, 6), fill('#f4f0e8')); cv.drawPath(rrect(kx - 18, ky - 13, 36, 26, 6), ink(2.5))
    cv.drawPath(rrect(-110, -290, 220, 110, 14), fill('#7a3a2a')); cv.drawPath(rrect(-110, -290, 220, 110, 14), ink(5))
    cv.drawPath(rrect(-90, -270, 180, 70, 8), fill('#2a1e28'))
    draw_text(cv, display, 0, -215, 56, '#8fffa0')
    cv.drawPath(rrect(-170, 0, 340, 50, 8), fill('#a04a2a')); cv.drawPath(rrect(-170, 0, 340, 50, 8), ink(5))
    cv.drawCircle(0, 25, 9, fill('#e6c25a'))
    cv.restore()
    if E is not None:
        E.append(dict(kind='glowrect', rect=(x - 90 * s, y - 270 * s, 180 * s, 70 * s), col=(140, 255, 160)))


def newspaper(cv, x, y, s=1.0, title='TOWN GAZETTE', headline='BIG NEWS!', angle=0):
    cv.save(); cv.translate(x, y); cv.rotate(angle); cv.scale(s, s)
    pg = rrect(-210, -280, 420, 560, 6)
    cv.drawPath(pg, fill('#f4ecd8')); cv.drawPath(pg, ink(5))
    draw_text(cv, title, 0, -220, 44, '#2a2232')
    cv.drawLine(-180, -200, 180, -200, ink(3)); cv.drawLine(-180, -192, 180, -192, ink(1.5))
    lines = headline.split('\n')
    for k, ln in enumerate(lines):
        draw_text(cv, ln, 0, -130 + k * 62, 56, '#2a2232')
    top = -130 + len(lines) * 62
    cv.drawRect(skia.Rect.MakeLTRB(-180, top - 10, 180, top + 130), stroke('#2a2232', 3))
    cv.drawPath(path_smooth([(-150, top + 110), (-60, top + 30), (40, top + 90), (150, top + 20)], close=False), stroke('#2a2232', 4))
    for k in range(5):
        cv.drawLine(-180, top + 160 + k * 22, 180 - (k % 2) * 60, top + 160 + k * 22, stroke('#8a8090', 5))
    cv.restore()


def sign_board(cv, x, y, text, s=1.0, col='#2f4a3a', txt='#f2c640', post=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    w = max(260, text_width(text, 70) + 80)
    if post:
        cv.drawPath(rrect(-14, 0, 28, 260, 6), fill('#7a5a3a')); cv.drawPath(rrect(-14, 0, 28, 260, 6), ink(4))
    bd = rrect(-w / 2, -130, w, 130, 16)
    cv.drawPath(bd, fill(col)); cv.drawPath(rrect(-w / 2 + 12, -118, w - 24, 106, 10), stroke(shade(txt, -0.2), 4)); cv.drawPath(bd, ink(5))
    draw_text(cv, text, 0, -42, 70, txt)
    cv.restore()


def counter_display(cv, x, y, digits='318', s=1.0, label=None):
    """Chalk number slate in a wooden frame (the 'number' prop)."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    n = len(digits)
    w = n * 96 + 90
    cv.drawLine(-w / 2 + 40, -110, 0, -190, stroke('#5a3a2a', 4)); cv.drawLine(w / 2 - 40, -110, 0, -190, stroke('#5a3a2a', 4))
    cv.drawCircle(0, -190, 9, fill('#e6b43c')); cv.drawCircle(0, -190, 9, ink(2.4))
    body = rrect(-w / 2, -110, w, 220, 14)
    cv.drawPath(body, fill('#a8703a')); cv.drawPath(body, ink(5))
    cv.drawPath(rrect(-w / 2 + 22, -88, w - 44, 176, 8), fill('#2f4a3e'))
    cv.drawPath(rrect(-w / 2 + 22, -88, w - 44, 176, 8), ink(3))
    for k in range(3):
        cv.drawLine(-w / 2 + 50 + k * 70, 60 - k * 9, -w / 2 + 120 + k * 70, 52 - k * 9, stroke('#e8f0e8', 3, 0.25))
    for k, d in enumerate(digits):
        xx = -w / 2 + 45 + k * 96
        draw_text(cv, d, xx + 48, 40, 120, '#f2f4ea')
    if label:
        draw_text(cv, label, 0, 170, 48, '#2a2232')
    cv.restore()


def cross_section(cv, x, y, w, h, layers=(('#6ab04a', 0.1), ('#8a5a3a', 0.35), ('#6a4030', 0.3), ('#4a3a40', 0.25)), seed=0):
    """Ground cut-away: stacked strata with pebbles (things can be drawn inside afterwards)."""
    rr = rng(seed)
    yy = y
    for col, frac in layers:
        hh = h * frac
        cv.drawRect(skia.Rect.MakeXYWH(x, yy, w, hh), fill(col))
        for _ in range(int(w * hh / 2500)):
            px, py = x + rr.uniform(5, w - 5), yy + rr.uniform(5, hh - 5)
            cv.drawPath(ellipse(px, py, rr.uniform(4, 10), rr.uniform(3, 7)), fill(shade(col, rr.uniform(-0.3, 0.2))))
        cv.drawLine(x, yy, x + w, yy, ink(3))
        yy += hh
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), ink(5))


def calendar_page(cv, x, y, month, day, s=1.0):
    from .setkit import calendar
    calendar(cv, x - 110 * s, y - 140 * s, 220 * s, 280 * s, month, day)
