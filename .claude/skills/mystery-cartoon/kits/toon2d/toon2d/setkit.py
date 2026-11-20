"""Reusable painted set pieces. All draw in plane coords with thin ink and 3-tone flat shading.

Emitters: functions that create light sources append to an `E` list (dicts) so the light pass can
re-draw them glowing after the mood grade (lit windows at night, lamp heads, screens...).
"""
import math

import skia

from .paint import (C, fill, stroke, ink, shade, mix, rgb, path_poly, path_smooth, rrect, ellipse, blurred,
                    lin_grad, rad_grad, argb, draw_tex_quad, draw_in_quad, rng, INK)
from . import textures as tx
from .light import halo, pool, god_rays

SET_INK = 4.2


def sky(cv, m, x0=-500, y0=-700, x1=1580, y1=1300, seed=1, clouds=8, sun=None, moon=None, stars=0,
        cloud_band=(-300, 700), cloud_scale=1.0, cloud_cols=None):
    top, mid, bot = m['sky']
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_grad((0, y0), (0, y1), [argb(top), argb(mid), argb(bot)], [0, 0.55, 1]))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), p)
    r = rng(seed)
    for _ in range(stars):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1 * 0.6)
        rr = r.uniform(1.5, 4)
        cv.drawCircle(x, y, rr, fill('#ffffff', r.uniform(0.4, 0.95)))
    if sun:
        sx, sy, sr = sun
        sp = skia.Paint(AntiAlias=True)
        sp.setShader(rad_grad((sx, sy), sr * 4, [argb(m['key'], 0.75), argb(m['key'], 0.25), argb(m['key'], 0)], [0.2, 0.45, 1]))
        cv.drawCircle(sx, sy, sr * 4, sp)
        cv.drawCircle(sx, sy, sr, fill(mix(m['key'], (255, 255, 240), 0.6)))
    if moon:
        mx_, my_, mr = moon
        mp = skia.Paint(AntiAlias=True)
        mp.setShader(rad_grad((mx_, my_), mr * 3.2, [argb((220, 226, 255), 0.55), argb((150, 160, 255), 0.15), argb((150, 160, 255), 0)], [0.25, 0.5, 1]))
        cv.drawCircle(mx_, my_, mr * 3.2, mp)
        cv.drawCircle(mx_, my_, mr, fill('#f4f2ff'))
        for k in range(4):
            cv.drawCircle(mx_ + r.uniform(-mr * 0.5, mr * 0.5), my_ + r.uniform(-mr * 0.5, mr * 0.5), mr * r.uniform(0.1, 0.2), fill('#d6d4ee', 0.8))
    cols = cloud_cols or (mix(bot, (255, 255, 255), 0.75), mix(mid, (90, 80, 150), 0.25))
    for i in range(clouds):
        cx = r.uniform(x0 + 100, x1 - 100)
        cy = r.uniform(*cloud_band)
        w = r.uniform(220, 520) * cloud_scale * (0.6 + 0.4 * (cy - cloud_band[0]) / max(1, cloud_band[1] - cloud_band[0]))
        cloud(cv, cx, cy, w, cols[0], cols[1], seed=seed * 31 + i)


def cloud(cv, x, y, w, lit, dark, seed=0, a=1.0):
    r = rng(seed)
    path = skia.Path()
    n = r.randint(5, 8)
    for k in range(n):
        u = k / (n - 1) - 0.5
        rr = w * r.uniform(0.13, 0.22) * (1 - abs(u) * 0.9)
        path.addCircle(x + u * w * 0.8, y - rr * 0.55 - (1 - abs(u) * 2) * w * 0.05, rr)
    path.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - w * 0.45, y - w * 0.08, x + w * 0.45, y + w * 0.05), w * 0.06, w * 0.06))
    path = skia.Op(path, skia.Path(), skia.PathOp.kUnion_PathOp) or path
    cv.drawPath(path, fill(dark, a))
    cv.save()
    cv.clipPath(path, doAntiAlias=True)
    cv.translate(-w * 0.03, -w * 0.06)
    cv.drawPath(path, fill(lit, a))
    cv.translate(-w * 0.03, -w * 0.05)
    cv.drawPath(path, fill(mix(lit, (255, 255, 255), 0.5), a * 0.6))
    cv.restore()


def mesa(cv, x, base, w, h, col='#c8603a', seed=0, bands=6):
    r = rng(seed)
    top = base - h
    pts = [(x - w / 2 - w * 0.12, base), (x - w / 2, top + h * 0.25), (x - w / 2 + w * 0.06, top + h * 0.06),
           (x - w * 0.2, top), (x + w * 0.25, top + 2), (x + w / 2 - w * 0.05, top + h * 0.07),
           (x + w / 2, top + h * 0.3), (x + w / 2 + w * 0.14, base)]
    body = path_poly(pts)
    cv.drawPath(body, fill(col))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    for b in range(bands):
        y = top + h * (b + 0.5) / bands + r.uniform(-6, 6)
        bh = h / bands * r.uniform(0.2, 0.45)
        pp = [(x - w, y + r.uniform(-5, 5))]
        for k in range(1, 9):
            pp.append((x - w + k * w / 4, y + r.uniform(-5, 5)))
        pp += [(x + w, y + bh), (x - w, y + bh)]
        cv.drawPath(path_poly(pp), fill(shade(col, r.choice([-0.18, 0.12, -0.08, 0.2])), 0.8))
        cv.drawPath(path_poly(pp[:9], close=False), stroke(shade(col, -0.35), 1.6, 0.6))
    # shade the right face
    cv.drawPath(path_poly([(x + w * 0.12, top - 10), (x + w, top - 10), (x + w, base + 10), (x + w * 0.3, base + 10)]),
                fill(shade(col, -0.35), 0.45))
    # top lit rim
    cv.drawPath(path_poly(pts[1:7], close=False), stroke(shade(col, 0.4), 4, 0.8))
    cv.restore()
    cv.drawPath(body, ink(2.4, 0.5))


def hills(cv, y, x0, x1, amp, col, seed=0, wav=260, a=1.0):
    r = rng(seed)
    pts = [(x0, y + 400)]
    x = x0
    while x <= x1 + wav:
        pts.append((x, y - r.uniform(0, amp)))
        x += wav * r.uniform(0.7, 1.3)
    pts.append((x1 + wav, y + 400))
    p = path_smooth(pts, close=True, tension=0.6)
    cv.drawPath(p, fill(col, a))
    return p


def foliage(cv, x, y, rad, col='#4f9a3c', seed=0, ink_w=SET_INK, lumps=7):
    r = rng(seed)
    path = skia.Path()
    for k in range(lumps):
        a = k / lumps * 2 * math.pi
        rr = rad * r.uniform(0.42, 0.6)
        path.addCircle(x + math.cos(a) * rad * 0.55, y + math.sin(a) * rad * 0.42, rr)
    path.addCircle(x, y, rad * 0.6)
    path = skia.Op(path, skia.Path(), skia.PathOp.kUnion_PathOp) or path
    cv.drawPath(path, fill(shade(col, -0.25)))
    cv.save(); cv.clipPath(path, doAntiAlias=True)
    for k in range(lumps):
        a = k / lumps * 2 * math.pi
        cv.drawCircle(x + math.cos(a) * rad * 0.45 - rad * 0.12, y + math.sin(a) * rad * 0.3 - rad * 0.2, rad * 0.4, fill(col))
    for k in range(4):
        cv.drawCircle(x - rad * 0.3 + k * rad * 0.15, y - rad * 0.45 + r.uniform(-8, 8), rad * 0.18, fill(shade(col, 0.25)))
    for k in range(int(rad / 4)):
        a = r.uniform(0, 2 * math.pi); d = r.uniform(0, rad)
        cv.drawPath(path_smooth([(x + math.cos(a) * d - 6, y + math.sin(a) * d * 0.7), (x + math.cos(a) * d, y + math.sin(a) * d * 0.7 - 5),
                                 (x + math.cos(a) * d + 6, y + math.sin(a) * d * 0.7)], close=False), stroke(shade(col, -0.4), 1.6, 0.6))
    cv.restore()
    cv.drawPath(path, ink(ink_w, 0.8))


def tree(cv, x, ground, h, col='#4f9a3c', trunk='#7a4a2a', seed=0):
    tw = h * 0.06
    tp = path_poly([(x - tw, ground), (x - tw * 0.6, ground - h * 0.6), (x + tw * 0.6, ground - h * 0.6), (x + tw, ground)])
    cv.drawPath(tp, fill(trunk)); cv.drawPath(tp, ink(SET_INK))
    cv.drawLine(x - tw * 0.2, ground - h * 0.1, x - tw * 0.2, ground - h * 0.5, stroke(shade(trunk, -0.35), 2))
    foliage(cv, x, ground - h * 0.68, h * 0.36, col, seed)


def window(cv, x, y, w, h, frame='#f2ece0', glass='#9cc4e8', curtain='#c8343c', E=None, lit=False, sill=True,
           panes=(2, 2), shutters=None, ink_w=SET_INK):
    if shutters:
        for sx in (-1, 1):
            sh_ = rrect(x + (w + 6 if sx > 0 else -w * 0.42 - 6), y, w * 0.42, h, 3)
            cv.drawPath(sh_, fill(shutters)); cv.drawPath(sh_, ink(ink_w * 0.8))
            for k in range(int(h / 14)):
                yy = y + 8 + k * 14
                xx = x + (w + 6 if sx > 0 else -w * 0.42 - 6)
                cv.drawLine(xx + 4, yy, xx + w * 0.42 - 4, yy, stroke(shade(shutters, -0.3), 1.6))
    fr = rrect(x - 8, y - 8, w + 16, h + 16, 3)
    cv.drawPath(fr, fill(frame)); cv.drawPath(fr, ink(ink_w))
    gl = skia.Rect.MakeXYWH(x, y, w, h)
    gp = skia.Paint(AntiAlias=True)
    gp.setShader(lin_grad((x, y), (x + w, y + h), [argb(shade(glass, 0.25)), argb(glass), argb(shade(glass, -0.2))]))
    cv.drawRect(gl, gp)
    if E is not None and lit:
        E.append(dict(kind='window', rect=(x, y, w, h)))
    # reflections
    cv.drawPath(path_poly([(x + w * 0.1, y + h), (x + w * 0.45, y), (x + w * 0.6, y), (x + w * 0.25, y + h)]), fill('#ffffff', 0.22))
    if curtain:
        for sx in (0, 1):
            cx = x if sx == 0 else x + w
            d = 1 if sx == 0 else -1
            cp = path_smooth([(cx, y), (cx + d * w * 0.34, y), (cx + d * w * 0.2, y + h * 0.5), (cx + d * w * 0.26, y + h), (cx, y + h)])
            cv.drawPath(cp, fill(curtain))
            for k in range(3):
                cv.drawLine(cx + d * w * (0.06 + k * 0.07), y + 4, cx + d * w * (0.05 + k * 0.06), y + h - 4, stroke(shade(curtain, -0.3), 2))
            cv.drawPath(cp, ink(ink_w * 0.7))
        cv.drawRect(skia.Rect.MakeXYWH(x - 4, y - 2, w + 8, 10), fill(shade(curtain, -0.2)))
    nx, ny = panes
    for i in range(1, nx):
        cv.drawRect(skia.Rect.MakeXYWH(x + w * i / nx - 4, y, 8, h), fill(frame))
    for j in range(1, ny):
        cv.drawRect(skia.Rect.MakeXYWH(x, y + h * j / ny - 4, w, 8), fill(frame))
    cv.drawRect(gl, ink(ink_w * 0.8))
    if sill:
        sl = rrect(x - 16, y + h + 6, w + 32, 14, 3)
        cv.drawPath(sl, fill(shade(frame, -0.1))); cv.drawPath(sl, ink(ink_w))


def door(cv, x, y, w, h, col='#7a3a2e', frame='#f2ece0', knob='#e6c25a', glass=True, E=None, lit=False):
    fr = rrect(x - 12, y - 12, w + 24, h + 12, 3)
    cv.drawPath(fr, fill(frame)); cv.drawPath(fr, ink(SET_INK))
    d = skia.Rect.MakeXYWH(x, y, w, h)
    cv.drawRect(d, fill(col))
    for (px, py, pw, ph) in ((0.12, 0.45, 0.32, 0.22), (0.56, 0.45, 0.32, 0.22), (0.12, 0.72, 0.32, 0.22), (0.56, 0.72, 0.32, 0.22)):
        rr = skia.Rect.MakeXYWH(x + w * px, y + h * py, w * pw, h * ph)
        cv.drawRect(rr, fill(shade(col, -0.15)))
        cv.drawRect(rr, stroke(shade(col, -0.45), 2))
    if glass:
        g = rrect(x + w * 0.15, y + h * 0.07, w * 0.7, h * 0.3, 4)
        cv.drawPath(g, fill('#9cc4e8')); cv.drawPath(g, ink(2.4))
        if E is not None and lit:
            E.append(dict(kind='window', rect=(x + w * 0.15, y + h * 0.07, w * 0.7, h * 0.3)))
    cv.drawRect(d, ink(SET_INK))
    cv.drawCircle(x + w * 0.85, y + h * 0.58, 6, fill(knob)); cv.drawCircle(x + w * 0.85, y + h * 0.58, 6, ink(2))


def house(cv, x, ground, w, h, wall='#9fc3c8', roof='#5b5f8a', trim='#f2ece0', door_col='#8a3a3a', seed=0,
          E=None, lit=False, side=0.32, chimney=True, windows=2, curtain='#c8343c', roof_h=None, porch_lamp=True):
    """A clapboard house in 3/4 view: lit front gable face + shaded side wall + shingled roof."""
    r = rng(seed)
    roof_h = roof_h or w * 0.42
    top = ground - h
    sw = w * side
    # side wall (receding to the right)
    sidep = path_poly([(x + w, top), (x + w + sw, top - sw * 0.28), (x + w + sw, ground - sw * 0.22), (x + w, ground)])
    tex_side = tx.clapboard(int(sw * 2) + 4, int(h * 2), board=56, base=shade(wall, -0.22), seed=seed + 1)
    draw_tex_quad(cv, tex_side, [(x + w, top), (x + w + sw, top - sw * 0.28), (x + w + sw, ground - sw * 0.22), (x + w, ground)])
    cv.drawPath(sidep, ink(SET_INK))
    if windows:
        wx, wy, ww, wh = x + w + sw * 0.3, top + h * 0.28, sw * 0.42, h * 0.32
        q = [(wx, wy - (wx - x - w) * 0.28), (wx + ww, wy - (wx + ww - x - w) * 0.28),
             (wx + ww, wy + wh - (wx + ww - x - w) * 0.24), (wx, wy + wh - (wx - x - w) * 0.24)]
        cv.drawPath(path_poly(q), fill('#7a9cc8')); cv.drawPath(path_poly(q), ink(SET_INK * 0.8))
        if E is not None and lit:
            E.append(dict(kind='quad', quad=q))
    # front face with clapboard
    face = skia.Rect.MakeXYWH(x, top, w, h)
    cv.drawImage(tx.clapboard(int(w), int(h), board=34, base=wall, seed=seed + 2), x, top)
    cv.drawRect(face, ink(SET_INK))
    # corner boards
    for cx in (x, x + w - 12):
        cv.drawRect(skia.Rect.MakeXYWH(cx, top, 12, h), fill(trim)); cv.drawRect(skia.Rect.MakeXYWH(cx, top, 12, h), ink(2))
    # gable roof front triangle + roof slope receding
    peak = (x + w / 2, top - roof_h)
    slope = path_poly([peak, (peak[0] + sw, peak[1] - sw * 0.28), (x + w + sw + 18, top - sw * 0.28), (x + w + 18, top + 4)])
    sh_img = tx.shingles(int(w * 1.4), int(roof_h * 2.2), sw=60, sh=34, base=roof, seed=seed + 3)
    draw_tex_quad(cv, sh_img, [peak, (peak[0] + sw, peak[1] - sw * 0.28), (x + w + sw + 18, top - sw * 0.28), (x + w + 18, top + 4)])
    cv.drawPath(slope, fill(shade(roof, -0.3), 0.35))
    cv.drawPath(slope, ink(SET_INK))
    gable = path_poly([(x - 18, top + 4), peak, (x + w + 18, top + 4)])
    cv.drawPath(path_poly([(x, top), peak, (x + w, top)]), fill(wall))
    cv.save(); cv.clipPath(path_poly([(x, top), peak, (x + w, top)]), doAntiAlias=True)
    cv.drawImage(tx.clapboard(int(w), int(roof_h) + 8, board=34, base=shade(wall, 0.04), seed=seed + 4), x, top - roof_h - 4)
    cv.restore()
    cv.drawPath(gable, stroke(trim, 16, cap=skia.Paint.kRound_Cap)); cv.drawPath(gable, stroke(INK, 2.2))
    # attic window
    aw = w * 0.16
    window(cv, peak[0] - aw / 2, top - roof_h * 0.55, aw, aw * 0.9, trim, curtain=None, E=E, lit=lit, sill=False, panes=(2, 2))
    if chimney:
        cxp = peak[0] + sw * 0.55
        ch = path_poly([(cxp, peak[1] - sw * 0.1), (cxp + 46, peak[1] - sw * 0.1 - 10), (cxp + 46, peak[1] + 70), (cxp, peak[1] + 80)])
        cv.save(); cv.clipPath(ch, doAntiAlias=True)
        cv.drawImage(tx.bricks(80, 200, bw=40, bh=18, base='#a04a32', seed=seed + 5), cxp - 10, peak[1] - sw * 0.1 - 20)
        cv.restore(); cv.drawPath(ch, ink(SET_INK))
        cv.drawPath(rrect(cxp - 6, peak[1] - sw * 0.1 - 22, 58, 16, 3), fill('#7a3a2e')); cv.drawPath(rrect(cxp - 6, peak[1] - sw * 0.1 - 22, 58, 16, 3), ink(2.4))
    # windows and door on front
    dw, dh = w * 0.2, h * 0.52
    dx = x + w * 0.5 - dw / 2
    door(cv, dx, ground - dh, dw, dh, door_col, trim, E=E, lit=lit)
    for k, wx in enumerate((x + w * 0.1, x + w * 0.66)):
        window(cv, wx, top + h * 0.22, w * 0.24, h * 0.34, trim, curtain=curtain, E=E, lit=lit, shutters=None, panes=(2, 2))
    # steps + base
    cv.drawPath(rrect(dx - 22, ground - 16, dw + 44, 16, 2), fill('#b8b0a8')); cv.drawPath(rrect(dx - 22, ground - 16, dw + 44, 16, 2), ink(2.4))
    cv.drawRect(skia.Rect.MakeXYWH(x, ground - 10, w, 10), fill(shade(wall, -0.35)))
    if porch_lamp:
        lx, ly = dx + dw + 30, ground - dh * 0.8
        cv.drawPath(rrect(lx - 9, ly - 14, 18, 26, 4), fill('#f4dc9a')); cv.drawPath(rrect(lx - 9, ly - 14, 18, 26, 4), ink(2.4))
        cv.drawRect(skia.Rect.MakeXYWH(lx - 11, ly - 20, 22, 7), fill('#2a2232'))
        if E is not None:
            E.append(dict(kind='lamp', pos=(lx, ly), r=110, lit=lit))
    # bushes
    for bx in (x + w * 0.1, x + w * 0.86):
        foliage(cv, bx, ground - 18, 42, '#3f8a46', seed=seed + int(bx))


def lamp_post(cv, x, ground, h=420, col='#2a2a3e', E=None, head='lantern', lit=True, scale=1.0):
    w = 12 * scale
    cv.drawPath(rrect(x - w * 1.8, ground - 30 * scale, w * 3.6, 30 * scale, 4), fill(col)); cv.drawPath(rrect(x - w * 1.8, ground - 30 * scale, w * 3.6, 30 * scale, 4), ink(SET_INK))
    cv.drawPath(rrect(x - w / 2, ground - h, w, h, 4), fill(col)); cv.drawPath(rrect(x - w / 2, ground - h, w, h, 4), ink(SET_INK))
    cv.drawLine(x - w * 0.15, ground - h + 10, x - w * 0.15, ground - 40 * scale, stroke('#6a6a8e', 2))
    hy = ground - h - 26 * scale
    if head == 'lantern':
        lp = path_poly([(x - 22 * scale, hy - 26 * scale), (x + 22 * scale, hy - 26 * scale), (x + 16 * scale, hy + 24 * scale), (x - 16 * scale, hy + 24 * scale)])
        cv.drawPath(lp, fill('#f8e2a0')); cv.drawPath(lp, ink(SET_INK))
        cv.drawPath(path_poly([(x - 30 * scale, hy - 26 * scale), (x + 30 * scale, hy - 26 * scale), (x, hy - 50 * scale)]), fill(col))
        cv.drawPath(path_poly([(x - 30 * scale, hy - 26 * scale), (x + 30 * scale, hy - 26 * scale), (x, hy - 50 * scale)]), ink(SET_INK))
        cv.drawLine(x, hy - 26 * scale, x, hy + 24 * scale, stroke(col, 3))
    else:
        cv.drawCircle(x, hy, 26 * scale, fill('#f8ecc0')); cv.drawCircle(x, hy, 26 * scale, ink(SET_INK))
    if E is not None:
        E.append(dict(kind='lamp', pos=(x, hy), r=260 * scale, lit=lit, ground=ground))  # ground -> pool + reflection
    return (x, hy)


def picket_fence(cv, x0, x1, base, h, col='#f2ece0', spacing=30, slope=0.0, scale_fn=None):
    x = x0
    while x < x1:
        s = scale_fn(x) if scale_fn else 1.0
        b = base + (x - x0) * slope
        pw = spacing * 0.62 * s
        p = path_poly([(x, b), (x, b - h * s), (x + pw / 2, b - h * s - pw * 0.5), (x + pw, b - h * s), (x + pw, b)])
        cv.drawPath(p, fill(col)); cv.drawPath(p, fill(shade(col, -0.25), 0.0))
        cv.drawRect(skia.Rect.MakeXYWH(x + pw * 0.62, b - h * s, pw * 0.38, h * s), fill(shade(col, -0.18)))
        cv.drawPath(p, ink(2.2 * s))
        x += spacing * s
    cv.drawLine(x0, base - h * 0.3, x1, base - h * 0.3 + (x1 - x0) * slope, stroke(shade(col, -0.3), 6))
    cv.drawLine(x0, base - h * 0.75, x1, base - h * 0.75 + (x1 - x0) * slope, stroke(shade(col, -0.3), 6))


def post_fence(cv, pts_base, h, col='#7a4a2a', rails=2):
    """Wooden ranch fence along a list of (x, y, scale) base points."""
    for i, (x, y, s) in enumerate(pts_base):
        p = rrect(x - 7 * s, y - h * s, 14 * s, h * s, 3 * s)
        cv.drawPath(p, fill(col)); cv.drawPath(p, ink(2.6 * s))
    for k in range(rails):
        for (x, y, s), (x2, y2, s2) in zip(pts_base[:-1], pts_base[1:]):
            yy, yy2 = y - h * s * (0.35 + k * 0.4), y2 - h * s2 * (0.35 + k * 0.4)
            q = path_poly([(x, yy - 5 * s), (x2, yy2 - 5 * s2), (x2, yy2 + 5 * s2), (x, yy + 5 * s)])
            cv.drawPath(q, fill(shade(col, 0.1))); cv.drawPath(q, ink(2 * s))


def telegraph_pole(cv, x, ground, h, s=1.0, col='#6a4a32'):
    cv.drawPath(rrect(x - 7 * s, ground - h, 14 * s, h, 3), fill(col)); cv.drawPath(rrect(x - 7 * s, ground - h, 14 * s, h, 3), ink(2.4 * s))
    for k in (0, 1):
        y = ground - h + 24 * s + k * 34 * s
        cv.drawPath(rrect(x - 60 * s, y, 120 * s, 10 * s, 2), fill(col)); cv.drawPath(rrect(x - 60 * s, y, 120 * s, 10 * s, 2), ink(2 * s))
        for dx in (-50, -20, 20, 50):
            cv.drawCircle(x + dx * s, y - 4 * s, 4.5 * s, fill('#9ad0d0'))


def cactus(cv, x, ground, h, col='#4f8a4a', seed=0):
    r = rng(seed)
    w = h * 0.18
    body = rrect(x - w / 2, ground - h, w, h, w / 2)
    arms = []
    for sx, ay, ah in ((-1, 0.45, 0.32), (1, 0.3, 0.38)):
        ax = x + sx * w * 0.5
        a = skia.Path()
        a.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(ax + (0 if sx > 0 else -w * 0.9), ground - h * ay - w * 0.35, w * 0.9, w * 0.6), w * 0.3, w * 0.3))
        a.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(ax + sx * w * 0.9 - (w * 0.6 if sx > 0 else 0) - (0 if sx > 0 else 0), ground - h * (ay + ah), w * 0.6, h * ah), w * 0.3, w * 0.3))
        arms.append(a)
    pth = body
    for a in arms:
        pth = skia.Op(pth, a, skia.PathOp.kUnion_PathOp)
    cv.drawPath(pth, fill(col))
    cv.save(); cv.clipPath(pth, doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeXYWH(x + w * 0.1, ground - h * 1.2, w * 2, h * 1.3), fill(shade(col, -0.3), 0.6))
    for k in range(-2, 3):
        cv.drawLine(x + k * w * 0.18, ground - h + 10, x + k * w * 0.18, ground, stroke(shade(col, -0.35), 1.6))
    cv.restore()
    cv.drawPath(pth, ink(SET_INK))
    for _ in range(int(h / 14)):
        px, py = x + r.uniform(-w / 2, w / 2), ground - r.uniform(10, h - 10)
        cv.drawLine(px, py, px + r.uniform(-6, 6), py - 6, stroke('#f4eedc', 1.4))


def rock(cv, x, y, w, col='#9a6a54', seed=0):
    r = rng(seed)
    pts = [(x - w / 2, y), (x - w * 0.42, y - w * 0.3), (x - w * 0.1, y - w * 0.46), (x + w * 0.3, y - w * 0.38), (x + w / 2, y - w * 0.1), (x + w * 0.46, y)]
    p = path_poly(pts)
    cv.drawPath(p, fill(col))
    cv.drawPath(path_poly([(x - w * 0.1, y - w * 0.46), (x + w * 0.3, y - w * 0.38), (x + w / 2, y - w * 0.1), (x + w * 0.46, y), (x + w * 0.05, y)]), fill(shade(col, -0.3), 0.7))
    cv.drawPath(path_poly([(x - w * 0.42, y - w * 0.3), (x - w * 0.1, y - w * 0.46), (x, y - w * 0.3)]), fill(shade(col, 0.3), 0.8))
    cv.drawPath(p, ink(SET_INK))


def crate(cv, x, y, w, h, col='#b07a45', label=None):
    r_ = skia.Rect.MakeXYWH(x, y, w, h)
    cv.drawRect(r_, fill(col))
    for k in range(1, 4):
        cv.drawLine(x, y + h * k / 4, x + w, y + h * k / 4, stroke(shade(col, -0.35), 2))
    cv.drawRect(skia.Rect.MakeXYWH(x, y, 14, h), fill(shade(col, -0.15))); cv.drawRect(skia.Rect.MakeXYWH(x + w - 14, y, 14, h), fill(shade(col, -0.15)))
    cv.drawLine(x + 14, y + h - 6, x + w - 14, y + 6, stroke(shade(col, -0.15), 12))
    cv.drawRect(r_, ink(SET_INK))
    if label:
        cv.drawPath(rrect(x + w * 0.3, y + h * 0.35, w * 0.4, h * 0.3, 3), fill('#f4ecd8'))


def frame_pic(cv, x, y, w, h, col='#a0703a', art=None):
    cv.drawPath(rrect(x, y, w, h, 4), fill(col)); cv.drawPath(rrect(x, y, w, h, 4), ink(SET_INK))
    inner = skia.Rect.MakeXYWH(x + w * 0.12, y + h * 0.12, w * 0.76, h * 0.76)
    cv.drawRect(inner, fill('#f4ecd8'))
    if art:
        art(cv, inner)
    cv.drawRect(inner, ink(2))


def calendar(cv, x, y, w, h, month='MAY', day='18', red='#c8343c'):
    from .text import draw_text
    cv.drawPath(rrect(x, y, w, h, 5), fill('#f8f4ec')); cv.drawPath(rrect(x, y, w, h, 5), ink(SET_INK))
    cv.drawPath(rrect(x, y, w, h * 0.28, 5), fill(red)); cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h * 0.28), ink(2.4))
    draw_text(cv, month, x + w / 2, y + h * 0.2, h * 0.17, '#ffffff')
    draw_text(cv, day, x + w / 2, y + h * 0.8, h * 0.42, '#2a2232')
    for k in range(3):
        cv.drawCircle(x + w * (0.25 + k * 0.25), y + 2, 5, fill('#9a9aae')); cv.drawCircle(x + w * (0.25 + k * 0.25), y + 2, 5, ink(2))


def wall_clock(cv, x, y, r, t=0.0):
    cv.drawCircle(x, y, r, fill('#c8343c')); cv.drawCircle(x, y, r, ink(SET_INK))
    cv.drawCircle(x, y, r * 0.84, fill('#f8f4ec')); cv.drawCircle(x, y, r * 0.84, ink(2))
    for k in range(12):
        a = k * math.pi / 6
        cv.drawLine(x + math.cos(a) * r * 0.66, y + math.sin(a) * r * 0.66, x + math.cos(a) * r * 0.76, y + math.sin(a) * r * 0.76, stroke('#2a2232', 3 if k % 3 == 0 else 1.6))
    a1, a2 = -math.pi / 2 + 1.1, -math.pi / 2 + 4.0
    cv.drawLine(x, y, x + math.cos(a1) * r * 0.42, y + math.sin(a1) * r * 0.42, stroke('#2a2232', 5))
    cv.drawLine(x, y, x + math.cos(a2) * r * 0.62, y + math.sin(a2) * r * 0.62, stroke('#2a2232', 3.4))
    cv.drawCircle(x, y, 5, fill('#2a2232'))
    cv.drawPath(path_poly([(x - r * 0.6, y - r * 0.2), (x - r * 0.2, y - r * 0.62), (x - r * 0.05, y - r * 0.55), (x - r * 0.48, y - r * 0.05)]), fill('#ffffff', 0.35))


def plant_pot(cv, x, y, s=1.0, col='#c8603a', leaf='#3f8a46', seed=0):
    r = rng(seed)
    for k in range(7):
        a = math.radians(-160 + k * 23 + r.uniform(-6, 6))
        L = s * r.uniform(60, 95)
        lp = path_smooth([(x, y - 30 * s), (x + math.cos(a) * L * 0.5 - 8 * s, y - 30 * s + math.sin(a) * L * 0.5), (x + math.cos(a) * L, y - 30 * s + math.sin(a) * L),
                          (x + math.cos(a) * L * 0.5 + 8 * s, y - 30 * s + math.sin(a) * L * 0.5)])
        cv.drawPath(lp, fill(shade(leaf, r.uniform(-0.2, 0.2)))); cv.drawPath(lp, ink(2 * s))
    pp = path_poly([(x - 32 * s, y - 40 * s), (x + 32 * s, y - 40 * s), (x + 24 * s, y), (x - 24 * s, y)])
    cv.drawPath(pp, fill(col)); cv.drawRect(skia.Rect.MakeXYWH(x - 36 * s, y - 46 * s, 72 * s, 12 * s), fill(shade(col, 0.15)))
    cv.drawPath(pp, ink(2.6 * s)); cv.drawRect(skia.Rect.MakeXYWH(x - 36 * s, y - 46 * s, 72 * s, 12 * s), ink(2.4 * s))


def draw_emitters(cv, E, m, night=True, scale=1.0, glass_col=None):
    """Re-draw emitters glowing (call in a lights pass after grading)."""
    key = m['key']
    gc = glass_col or mix(key, (255, 240, 200), 0.35)
    for e in E:
        if e['kind'] == 'window':
            x, y, w, h = e['rect']
            p = skia.Paint(AntiAlias=True)
            p.setShader(lin_grad((x, y), (x, y + h), [argb(mix(gc, (255, 255, 230), 0.4)), argb(gc), argb(shade(gc, -0.15))]))
            cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)
            halo(cv, x + w / 2, y + h / 2, max(w, h) * 1.3, key, 0.32 if night else 0.12, core=0.3)
        elif e['kind'] == 'quad':
            p = fill(gc)
            cv.drawPath(path_poly(e['quad']), p)
        elif e['kind'] == 'lamp' and e.get('lit', True):
            x, y = e['pos']
            rr = e['r'] * scale
            if night:
                halo(cv, x, y, rr, key, 0.75)
                if e.get('ground') is not None:
                    pool(cv, x, e['ground'], rr * 1.2, rr * 0.28, key, 0.42)
            else:
                halo(cv, x, y, rr * 0.4, key, 0.25)
