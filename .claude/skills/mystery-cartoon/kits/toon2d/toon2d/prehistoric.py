"""Prehistoric valley: smoking volcano, long-necked dinosaur on the horizon, two flying reptiles, giant ferns and
cycads, a river, boulders, a rock outcrop with a cave mouth and a campfire (glows in sunset / night / dawn).
Built on the pinhole ground in depth bands like the other outdoor sets. Also: draw_dino (small friendly dinosaur)."""
import math

import skia

from .paint import (fill, stroke, ink, shade, mix, path_poly, path_smooth, rrect, ellipse, blurred, lin_grad,
                    rad_grad, argb, rng, INK)
from . import textures as tx
from . import setkit as sk
from .light import MOODS, halo, pool, god_rays
from .sets import Ground

GLOW_MOODS = ('sunset', 'night', 'dawn', 'golden', 'dream')


# ----------------------------------------------------------------------------- plants and rocks
def fern(cv, x, y, h, col='#4f9a3c', seed=0, ink_w=3.0):
    """Giant tree fern: short shaggy trunk + arching fronds with leaflets."""
    r = rng(seed)
    th = h * 0.32
    tw = h * 0.05
    trunk = path_poly([(x - tw, y), (x - tw * 0.7, y - th), (x + tw * 0.7, y - th), (x + tw, y)])
    cv.drawPath(trunk, fill('#6a4a32')); cv.drawPath(trunk, ink(ink_w * 0.8))
    for k in range(5):
        yy = y - th * (k + 0.5) / 5
        cv.drawLine(x - tw, yy, x + tw, yy - tw * 0.4, stroke('#4a3022', max(1, ink_w * 0.6)))
    top = (x, y - th)
    n = 9
    for k in range(n):
        a = math.radians(-170 + k * 160 / (n - 1) + r.uniform(-6, 6))
        L = h * r.uniform(0.55, 0.75)
        droop = h * 0.18
        p1 = (top[0] + math.cos(a) * L * 0.55, top[1] + math.sin(a) * L * 0.55 - droop * 0.4)
        p2 = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.5 + droop)
        c = shade(col, r.uniform(-0.18, 0.12))
        # leaflets along the frond
        for j in range(1, 11):
            u = j / 11
            px = (1 - u) ** 2 * top[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
            py = (1 - u) ** 2 * top[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
            ll = h * 0.09 * (1 - u * 0.7)
            for sgn in (-1, 1):
                lf = ellipse(px + sgn * ll * 0.4, py + ll * 0.45, ll * 0.55, ll * 0.22)
                cv.save(); cv.translate(px, py); cv.rotate(sgn * 50 + math.degrees(a) * 0.3); cv.translate(-px, -py)
                cv.drawPath(lf, fill(c)); cv.restore()
        sp = skia.Path(); sp.moveTo(*top); sp.quadTo(*p1, *p2)
        cv.drawPath(sp, stroke(shade(c, -0.35), max(1.2, h * 0.012)))
    cv.drawCircle(top[0], top[1], h * 0.05, fill(shade(col, -0.4)))


def cycad(cv, x, y, h, col='#3f8a46', seed=0, ink_w=3.0):
    """Cycad: stout trunk with diamond scale pattern + a crown of stiff straight fronds."""
    r = rng(seed)
    tw, th = h * 0.13, h * 0.45
    trunk = path_smooth([(x - tw, y), (x - tw * 1.1, y - th * 0.5), (x - tw * 0.85, y - th), (x + tw * 0.85, y - th),
                         (x + tw * 1.1, y - th * 0.5), (x + tw, y)])
    cv.drawPath(trunk, fill('#8a6a44'))
    cv.save(); cv.clipPath(trunk, doAntiAlias=True)
    step = tw * 0.5
    for j in range(int(th / step) + 2):
        for i in range(-3, 4):
            cx_, cy_ = x + i * step + (j % 2) * step / 2, y - j * step * 0.8
            cv.drawPath(path_poly([(cx_, cy_ - step * 0.4), (cx_ + step * 0.45, cy_), (cx_, cy_ + step * 0.4), (cx_ - step * 0.45, cy_)]),
                        stroke('#5a4028', max(1, h * 0.006)))
    cv.drawRect(skia.Rect.MakeLTRB(x + tw * 0.2, y - th, x + tw * 1.2, y), fill('#3a2440', 0.25))
    cv.restore()
    cv.drawPath(trunk, ink(ink_w * 0.8))
    top = (x, y - th)
    for k in range(13):
        a = math.radians(-180 + k * 15 + r.uniform(-4, 4))
        L = h * r.uniform(0.45, 0.6)
        end = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.75 + abs(math.cos(a)) * h * 0.08)
        c = shade(col, r.uniform(-0.2, 0.15))
        fr = path_poly([(top[0], top[1] - h * 0.015), end, (top[0], top[1] + h * 0.015)])
        cv.drawLine(*top, *end, stroke(c, max(2, h * 0.05), cap=skia.Paint.kRound_Cap))
        for j in range(1, 8):
            u = j / 8
            px, py = top[0] + (end[0] - top[0]) * u, top[1] + (end[1] - top[1]) * u
            nx, ny = -(end[1] - top[1]) / L, (end[0] - top[0]) / L
            ll = h * 0.05 * (1 - u * 0.5)
            cv.drawLine(px, py, px + nx * ll, py + ny * ll, stroke(shade(c, 0.1), max(1, h * 0.012)))
            cv.drawLine(px, py, px - nx * ll, py - ny * ll, stroke(shade(c, -0.1), max(1, h * 0.012)))
        cv.drawLine(*top, *end, stroke(shade(c, -0.4), max(1, h * 0.008)))


def boulder(cv, x, y, w, col='#8a7a8a', seed=0, ink_w=3.0):
    r = rng(seed)
    pts = []
    n = 9
    for k in range(n):
        a = math.pi + k * math.pi / (n - 1)
        rr = w * 0.5 * r.uniform(0.82, 1.05)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * r.uniform(0.6, 0.85)))
    pts += [(x + w * 0.5, y), (x - w * 0.5, y)]
    p = path_smooth(pts, tension=0.35)
    cv.drawPath(p, fill(col))
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    cv.drawPath(ellipse(x + w * 0.28, y, w * 0.45, w * 0.35), fill('#3a2448', 0.28))
    cv.drawPath(ellipse(x - w * 0.18, y - w * 0.32, w * 0.2, w * 0.08), fill('#ffffff', 0.25))
    for k in range(3):
        a0 = r.uniform(-0.3, 0.3)
        cv.drawLine(x - w * 0.2 + k * w * 0.15, y - w * 0.3, x - w * 0.1 + k * w * 0.15 + a0 * w * 0.1, y - w * 0.12, stroke(shade(col, -0.35), max(1, w * 0.01)))
    cv.restore()
    cv.drawPath(p, ink(ink_w))


def campfire(cv, x, y, s, t=0.0):
    """Stone ring, crossed logs, layered flames. s = pixels per metre."""
    for k in range(9):
        a = k * 2 * math.pi / 9
        cv.drawPath(ellipse(x + math.cos(a) * 0.45 * s, y + math.sin(a) * 0.12 * s, 0.13 * s, 0.08 * s), fill('#8a8494'))
        cv.drawPath(ellipse(x + math.cos(a) * 0.45 * s, y + math.sin(a) * 0.12 * s, 0.13 * s, 0.08 * s), ink(max(1, s * 0.012)))
    for sgn in (-1, 1):
        cv.drawLine(x - sgn * 0.35 * s, y + 0.02 * s, x + sgn * 0.3 * s, y - 0.12 * s, stroke('#6a4028', 0.09 * s))
        cv.drawLine(x - sgn * 0.35 * s, y + 0.02 * s, x + sgn * 0.3 * s, y - 0.12 * s, ink(max(1, s * 0.01)))
    for (w, h, col) in ((0.32, 0.75, '#e8502a'), (0.22, 0.55, '#f8a030'), (0.12, 0.34, '#fff0a0')):
        fl = path_smooth([(x - w * s, y - 0.08 * s), (x - w * 0.7 * s, y - h * 0.5 * s), (x - w * 0.2 * s, y - h * 0.75 * s),
                          (x, y - h * s), (x + w * 0.3 * s, y - h * 0.7 * s), (x + w * 0.8 * s, y - h * 0.45 * s), (x + w * s, y - 0.08 * s)])
        cv.drawPath(fl, fill(col))
    for k in range(5):
        cv.drawCircle(x + (k - 2) * 0.12 * s, y - (0.9 + k * 0.17) * s, 0.025 * s, fill('#ffd070', 0.9))


def volcano(cv, x, base, w, h, m, glow=False):
    cone = path_poly([(x - w / 2, base), (x - w * 0.08, base - h), (x + w * 0.08, base - h), (x + w / 2, base)])
    cv.drawPath(cone, fill(mix('#6a4a5a', m['fog'], 0.35)))
    cv.save(); cv.clipPath(cone, doAntiAlias=True)
    r = rng(4)
    for k in range(7):
        xx = x + r.uniform(-0.1, 0.1) * w
        cv.drawPath(path_poly([(xx - w * 0.02, base - h), (xx + w * 0.02, base - h), (xx + r.uniform(-0.4, 0.4) * w, base + 10), (xx + r.uniform(-0.4, 0.4) * w - w * 0.04, base + 10)]),
                    fill(mix('#4a3446', m['fog'], 0.35), 0.6))
    cv.drawRect(skia.Rect.MakeLTRB(x, base - h, x + w, base), fill(m['shadow'], 0.22))
    # lava streak
    lv = path_smooth([(x - w * 0.03, base - h), (x - w * 0.06, base - h * 0.7), (x - w * 0.02, base - h * 0.45), (x - w * 0.07, base - h * 0.2)], close=False)
    cv.drawPath(lv, stroke('#ff7a2a' if glow else '#b8603a', w * 0.008, 0.7))
    cv.restore()
    cv.drawPath(cone, ink(2.4, 0.6))
    cv.drawPath(ellipse(x, base - h, w * 0.07, w * 0.012), fill('#ffb050' if glow else '#8a4a3a'))
    # smoke column drifting right
    for k in range(10):
        sx = x + k * w * 0.06 + math.sin(k * 0.9) * w * 0.03
        sy = base - h - k * h * 0.22
        rr = w * (0.06 + k * 0.025)
        col = mix(mix('#6a5a6a', '#d8c8d0', k / 10), m['fog'], 0.3)
        cv.drawCircle(sx, sy, rr, fill(col, 0.9))
        cv.drawCircle(sx - rr * 0.3, sy - rr * 0.3, rr * 0.6, fill(mix(col, '#ffffff', 0.25), 0.7))


def sauropod(cv, x, base, s, col):
    """Long-necked dinosaur silhouette (s = height in px of the body hump)."""
    body = ellipse(x, base - s * 0.9, s * 1.1, s * 0.55)
    cv.drawPath(body, fill(col))
    for lx in (-0.6, -0.25, 0.3, 0.65):
        cv.drawPath(rrect(x + lx * s - s * 0.12, base - s * 0.8, s * 0.24, s * 0.8, s * 0.08), fill(shade(col, -0.08 if lx in (-0.25, 0.65) else 0)))
    neck = skia.Path(); neck.moveTo(x + s * 0.7, base - s * 1.2)
    neck.cubicTo(x + s * 1.3, base - s * 1.6, x + s * 1.4, base - s * 2.8, x + s * 1.9, base - s * 3.0)
    cv.drawPath(neck, stroke(col, s * 0.28, cap=skia.Paint.kRound_Cap))
    cv.drawPath(ellipse(x + s * 2.05, base - s * 3.02, s * 0.26, s * 0.14), fill(col))
    tail = skia.Path(); tail.moveTo(x - s * 0.9, base - s * 1.0); tail.cubicTo(x - s * 1.6, base - s * 1.0, x - s * 2.2, base - s * 0.6, x - s * 2.8, base - s * 0.3)
    cv.drawPath(tail, stroke(col, s * 0.2, cap=skia.Paint.kRound_Cap))


def flyer(cv, x, y, s, col='#5a3a5a', flap=0.0):
    """Flying reptile: membrane wings, crested head, long beak."""
    up = 0.35 + 0.25 * flap
    for sgn in (-1, 1):
        wing = path_poly([(x, y), (x + sgn * s * 0.5, y - s * up), (x + sgn * s * 1.2, y - s * (up - 0.15)),
                          (x + sgn * s * 0.75, y + s * 0.05), (x + sgn * s * 0.3, y + s * 0.12)])
        cv.drawPath(wing, fill(col))
        cv.drawLine(x + sgn * s * 0.5, y - s * up, x + sgn * s * 0.75, y + s * 0.05, stroke(shade(col, 0.25), max(1, s * 0.03)))
    cv.drawPath(ellipse(x, y + s * 0.05, s * 0.12, s * 0.22), fill(col))
    head = path_poly([(x - s * 0.06, y - s * 0.12), (x + s * 0.45, y - s * 0.22), (x + s * 0.06, y - s * 0.04)])
    cv.drawPath(head, fill(col))
    cv.drawPath(path_poly([(x - s * 0.02, y - s * 0.14), (x - s * 0.3, y - s * 0.3), (x - s * 0.06, y - s * 0.06)]), fill(col))


# ----------------------------------------------------------------------------- the set
def prehistoric(mood):
    m = MOODS[mood]
    glow = mood in GLOW_MOODS
    night = mood == 'night'
    vx, h0 = 520, 1230                               # low horizon: the valley sits behind the actors
    G = Ground(vx, h0, 1.45)
    E = {}
    tiles = [(tx.grass(900, 900, base='#7aa04a', seed=31, density=1.1, blade=34), 4, 4, (-400, 400), {})]
    objs = []

    # bubbling tar pit on the left (ground band)
    def tar(cv):
        pts = []
        for k in range(24):
            a_ = k * 2 * math.pi / 24
            X = -3.6 + math.cos(a_) * 1.9 * (1 + 0.12 * math.sin(3 * a_))
            Z = 4.4 + math.sin(a_) * 1.1
            pts.append(G.proj(X, Z))
        rim = [(x, y) for x, y in pts]
        cv.drawPath(path_smooth(rim), fill('#6a5040'))
        inner = []
        for k in range(24):
            a_ = k * 2 * math.pi / 24
            inner.append(G.proj(-3.6 + math.cos(a_) * 1.6, 4.4 + math.sin(a_) * 0.9))
        pit = path_smooth(inner)
        cv.drawPath(pit, fill('#221a26'))
        cv.save(); cv.clipPath(pit, doAntiAlias=True)
        x0, y0 = G.proj(-4.1, 4.1)
        cv.drawPath(ellipse(x0, y0, G.scale(4.1) * 0.7, G.scale(4.1) * 0.08), fill(mix('#ffffff', m['key'], 0.5), 0.25))
        r_ = rng(12)
        for k in range(6):
            bx_, by_ = G.proj(-3.6 + r_.uniform(-1.2, 1.2), 4.4 + r_.uniform(-0.6, 0.6))
            rr_ = G.scale(4.4) * r_.uniform(0.06, 0.14)
            cv.drawCircle(bx_, by_ - rr_ * 0.4, rr_, fill('#3a2e40')); cv.drawCircle(bx_, by_ - rr_ * 0.4, rr_, ink(2, 0.8))
            cv.drawCircle(bx_ - rr_ * 0.3, by_ - rr_ * 0.75, rr_ * 0.25, fill('#ffffff', 0.5))
        cv.restore()
        cv.drawPath(pit, ink(3))
    objs.append((3.4, tar))

    # river across the valley (mid band)
    def river(cv):
        zs = [16 * (1.04 ** k) for k in range(12)]
        def bank(Z0, sgn):
            pts = []
            for X in range(-80, 81, 4):
                Z = Z0 + 1.6 * math.sin(X * 0.09 + sgn)
                pts.append(G.proj(X, Z))
            return pts
        near_b, far_b = bank(18.0, 0), bank(22.0, 1.3)
        poly = near_b + far_b[::-1]
        cv.drawPath(path_poly(poly), fill('#c8b48a'))
        n2, f2 = bank(18.4, 0), bank(21.6, 1.3)
        water = path_poly(n2 + f2[::-1])
        cv.drawPath(water, fill(mix('#3f8ad0', m['sky'][2], 0.25)))
        r = rng(8)
        cv.save(); cv.clipPath(water, doAntiAlias=True)
        for k in range(60):
            X, Z = r.uniform(-40, 40), r.uniform(18.5, 21.5)
            x, y = G.proj(X, Z)
            L = G.scale(Z) * r.uniform(0.3, 0.9)
            cv.drawLine(x - L, y, x + L, y, stroke(mix('#ffffff', m['key'], 0.4), max(1, G.scale(Z) * 0.03), 0.6))
        cv.restore()
        cv.drawPath(path_poly(n2, close=False), stroke('#5a4a3a', 2.2, 0.6))
    objs.append((22.0, river))

    # cave outcrop on the right with the campfire in front
    def outcrop(cv):
        X0, Z = 4.2, 14.0
        s = G.scale(Z)
        bx, by = G.proj(X0, Z)
        pts = [(bx - 0.4 * s, by), (bx - 0.2 * s, by - 3.2 * s), (bx + 0.8 * s, by - 6.2 * s), (bx + 2.6 * s, by - 7.6 * s),
               (bx + 5.0 * s, by - 8.4 * s), (bx + 8.0 * s, by - 8.0 * s), (bx + 9.5 * s, by + 0.4 * s)]
        rock = path_smooth(pts + [(bx + 9.5 * s, by + 0.6 * s)], tension=0.3)
        cv.drawPath(rock, fill('#9a8494'))
        cv.save(); cv.clipPath(rock, doAntiAlias=True)
        for k in range(6):                                     # rock strata
            yy = by - (1.2 + k * 1.25) * s
            cv.drawPath(path_smooth([(bx - s, yy + 0.3 * s), (bx + 3 * s, yy - 0.2 * s), (bx + 6 * s, yy + 0.25 * s), (bx + 10 * s, yy - 0.1 * s)], close=False),
                        stroke(shade('#9a8494', 0.18 if k % 2 else -0.12), 0.35 * s, 0.6))
        r = rng(3)
        for k in range(14):
            yy = by - r.uniform(0.5, 8) * s
            cv.drawLine(bx + r.uniform(0, 3) * s, yy, bx + r.uniform(3, 9) * s, yy + r.uniform(-0.4, 0.4) * s, stroke('#6a5466', max(1, s * 0.03), 0.7))
        cv.drawRect(skia.Rect.MakeLTRB(bx + 3.5 * s, by - 9 * s, bx + 10 * s, by + 1 * s), fill(m['shadow'], 0.25))
        # moss on top
        cv.drawPath(path_smooth([(bx + 0.4 * s, by - 5.4 * s), (bx + 2.6 * s, by - 7.8 * s), (bx + 5.0 * s, by - 8.6 * s), (bx + 8 * s, by - 8.3 * s),
                                 (bx + 8 * s, by - 7.6 * s), (bx + 5 * s, by - 7.9 * s), (bx + 2.6 * s, by - 7.0 * s)]), fill('#5a8a3a'))
        cv.restore()
        cv.drawPath(rock, ink(3.2))
        # cave mouth
        mouth = skia.Path(); mx, my = bx + 1.8 * s, by
        mouth.moveTo(mx - 1.1 * s, my); mouth.cubicTo(mx - 1.2 * s, my - 2.6 * s, mx + 1.4 * s, my - 2.9 * s, mx + 1.5 * s, my); mouth.close()
        cv.drawPath(mouth, fill('#1e1426'))
        p = skia.Paint(AntiAlias=True)
        p.setShader(rad_grad((mx, my), 1.6 * s, [argb((255, 150, 70), 0.35 if glow else 0.08), argb((255, 150, 70), 0)]))
        cv.drawPath(mouth, p)
        cv.drawPath(mouth, ink(3.2))
        # hand prints and a painted animal beside the mouth (original cave painting)
        for k in range(3):
            hx, hy = bx + (3.6 + k * 0.5) * s, by - (2.2 + (k % 2) * 0.4) * s
            cv.drawCircle(hx, hy, 0.12 * s, fill('#a8402a', 0.75))
            for j in range(4):
                a = math.radians(-140 + j * 30)
                cv.drawLine(hx, hy, hx + math.cos(a) * 0.22 * s, hy + math.sin(a) * 0.22 * s, stroke('#a8402a', 0.05 * s, 0.75))
        ax, ay = bx + 5.6 * s, by - 3.4 * s
        cv.drawPath(ellipse(ax, ay, 0.6 * s, 0.25 * s), stroke('#a8402a', 0.06 * s, 0.7))
        for lx in (-0.35, 0.35):
            cv.drawLine(ax + lx * s, ay + 0.2 * s, ax + lx * s, ay + 0.6 * s, stroke('#a8402a', 0.06 * s, 0.7))
        cv.drawLine(ax + 0.55 * s, ay - 0.1 * s, ax + 0.95 * s, ay - 0.45 * s, stroke('#a8402a', 0.06 * s, 0.7))
    objs.append((14.0, outcrop))

    def fire(cv):
        X, Z = 3.6, 12.0
        x, y = G.proj(X, Z)
        s = G.scale(Z)
        campfire(cv, x, y, s)
        E.setdefault('near', []).append(dict(pos=(x, y - 0.4 * s), ground=y, s=s))
    objs.append((12.0, fire))

    # hero plants and rocks close to the acting area
    for k, (X, Z, kind, sz) in enumerate(((-3.2, 6.5, 'fern', 3.6), (-6.0, 9.0, 'cycad', 2.4), (-2.4, 11.0, 'boulder', 1.4),
                                          (2.6, 7.5, 'boulder', 1.0), (6.5, 8.0, 'fern', 4.2), (-9.0, 14.0, 'fern', 4.5),
                                          (1.6, 16.0, 'cycad', 2.0), (-1.2, 22.0, 'fern', 4.0))):
        if kind == 'fern':
            fn = (lambda cv, X=X, Z=Z, sz=sz, sd=k + 300: fern(cv, *G.proj(X, Z), G.scale(Z) * sz, col='#4f9a3c', seed=sd, ink_w=3))
        elif kind == 'cycad':
            fn = (lambda cv, X=X, Z=Z, sz=sz, sd=k + 300: cycad(cv, *G.proj(X, Z), G.scale(Z) * sz, seed=sd, ink_w=3))
        else:
            fn = (lambda cv, X=X, Z=Z, sz=sz, sd=k + 300: boulder(cv, *G.proj(X, Z), G.scale(Z) * sz, seed=sd, ink_w=3))
        objs.append((Z, fn))
    r = rng(21)
    for k in range(80):
        Z = 2.5 * (1.045 ** r.uniform(0, 90))
        X = r.choice([-1, -1, 1]) * r.uniform(2.2, 30)
        if 2.0 < X < 16 and 9 < Z < 18:                  # keep the cave clear
            continue
        if -6.5 < X < -0.8 and 2.8 < Z < 6.2:            # keep the tar pit clear
            continue
        if abs(X) < 1.6 and Z < 6:                       # keep the acting area clear
            continue
        kind = r.random()
        if kind < 0.4:
            fn = (lambda cv, X=X, Z=Z, sd=k: fern(cv, *G.proj(X, Z), G.scale(Z) * rng(sd).uniform(2.4, 4.0), col=rng(sd).choice(['#4f9a3c', '#5aa848', '#3f8a46']), seed=sd, ink_w=max(0.8, min(3, G.scale(Z) * 0.02))))
        elif kind < 0.65:
            fn = (lambda cv, X=X, Z=Z, sd=k: cycad(cv, *G.proj(X, Z), G.scale(Z) * rng(sd).uniform(1.6, 2.6), col=rng(sd).choice(['#3f8a46', '#4a9a52']), seed=sd, ink_w=max(0.8, min(3, G.scale(Z) * 0.02))))
        else:
            fn = (lambda cv, X=X, Z=Z, sd=k: boulder(cv, *G.proj(X, Z), G.scale(Z) * rng(sd).uniform(0.6, 1.8), col=rng(sd).choice(['#8a7a8a', '#9a8a8a', '#7a6a7a']), seed=sd, ink_w=max(0.8, min(3, G.scale(Z) * 0.02))))
        objs.append((Z, fn))

    def sky(cv):
        sk.sky(cv, m, seed=41, clouds=6, cloud_band=(-420, 420), cloud_scale=1.2,
               sun=(250, 700, 80) if mood == 'day' else None, moon=(820, 160, 60) if night else None, stars=200 if night else 0)
        if mood in ('sunset', 'dawn'):
            sp = skia.Paint(AntiAlias=True)
            sp.setShader(rad_grad((180, 1100), 600, [argb((255, 230, 160), 0.85), argb((255, 170, 110), 0.3), argb((255, 160, 120), 0)], [0.15, 0.45, 1]))
            cv.drawCircle(180, 1100, 600, sp)
            cv.drawCircle(180, 1100, 110, fill('#fff0c0'))
        col = mix('#4a2a4a', m['fog'], 0.15)
        flyer(cv, 300, 420, 120, col, 0.2)
        flyer(cv, 480, 520, 80, col, -0.6)

    def far_extra(cv):
        fogc = m['fog']
        sk.hills(cv, h0 + 20, -600, 1700, 120, mix('#5a6a7a', fogc, 0.55), seed=33, wav=320)
        volcano(cv, 860, h0 + 30, 760, 420, m, glow)
        sk.hills(cv, h0 + 36, -600, 1700, 50, mix('#4a7a4a', fogc, 0.4), seed=34, wav=200)
        sauropod(cv, 330, h0 + 30, 46, mix('#4a5a6a', fogc, 0.45))
        rr = rng(35)
        for k in range(26):
            x = rr.uniform(-400, 1500)
            sk.foliage(cv, x, h0 + 30, rr.uniform(18, 36), mix('#3f6a3a', fogc, 0.45), seed=k + 70, ink_w=0)

    bands = [('ground', 1.0, 0.35, 6.0), ('near', 2.2, 5.8, 13.0), ('mid', 5.0, 12.5, 40.0), ('far', 14.0, 38.0, 900.0)]

    def lights(name):
        def f(cv, mm):
            if name == 'mid' and mood == 'day':
                god_rays(cv, (250, 700), 70, 50, 2200, n=7, col=mm['key'], a=0.12)
            if name == 'far' and glow:
                halo(cv, 860, h0 + 30 - 420, 90, (255, 140, 70), 0.35)
            for e in E.get(name, []):
                x, y = e['pos']
                s = e['s']
                if glow:
                    halo(cv, x, y, 3.2 * s, (255, 170, 80), 0.75 if night else 0.6, core=0.12)
                    pool(cv, x, e['ground'], 2.6 * s, 0.7 * s, (255, 160, 80), 0.45)
                else:
                    halo(cv, x, y, 1.0 * s, (255, 200, 120), 0.35, core=0.2)
        return f

    layers = [('sky', 30.0, sky, dict(grade=False))]
    from .outdoor import _band_painter
    for name, pz, z0, z1 in bands:
        ob = [o for o in objs if not (getattr(o[1], '__name__', '') == 'path' and not (z0 <= o[0] < z1))]
        if name == 'far':
            ob.append((899.0, far_extra))
        opts = dict(lights=lights(name))
        if name == 'far':
            opts.update(blur=0.8)
        back = ('#2e1a44', 0.6) if mood in ('sunset', 'dawn') else None
        layers.append(('b_' + name, pz, _band_painter(G, tiles, ob, z0, z1, fog=(m['fog'], 0.35, 200), back=back), opts))

    def fg(cv):
        fern(cv, -60, 2250, 900, col='#2f6a3a', seed=5, ink_w=4)
        fern(cv, 1180, 2300, 800, col='#356f45', seed=6, ink_w=4)
    layers.append(('fg', 0.55, fg, dict(blur=10)))
    return layers, dict(ground=G, ground_y=1600, h0=h0, vx=vx, fire=(3.6, 12.0))


# ----------------------------------------------------------------------------- small friendly dinosaur
def draw_dino(cv, x, y, scale, t, mood_name='day', dir=1, expr='happy', col='#5ab88a', belly='#f2e6b8'):
    """Chubby little two-legged dinosaur, ~280 units tall (a character head is 200 wide). Feet at (x, y)."""
    from .light import grade_color, MOODS as _M
    m = _M[mood_name]
    g = lambda c: grade_color(c, m)
    br = math.sin(t * 2 * math.pi / 2.6)
    wag = math.sin(t * 2 * math.pi / 1.3) * 10
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * dir, scale)
    cv.translate(0, br * 2)
    W = 6.0
    # tail (behind)
    tail = path_smooth([(-60, -110), (-150, -90 + wag * 0.5), (-230, -60 + wag), (-160, -60 + wag * 0.4), (-70, -60)])
    cv.drawPath(tail, fill(g(col))); cv.drawPath(tail, ink(W))
    # back leg
    for lx, sh in ((-30, -0.12), (40, 0.0)):
        leg = rrect(lx - 26, -90, 52, 90, 22)
        cv.drawPath(leg, fill(g(shade(col, sh)))); cv.drawPath(leg, ink(W))
        cv.drawPath(ellipse(lx + 8, -4, 38, 14), fill(g(shade(col, sh - 0.1)))); cv.drawPath(ellipse(lx + 8, -4, 38, 14), ink(W * 0.8))
    # body
    body = ellipse(0, -140, 105, 95 * (1 + br * 0.01))
    cv.drawPath(body, fill(g(col)))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    cv.drawPath(ellipse(38, -118, 62, 70), fill(g(belly)))
    cv.drawPath(ellipse(-60, -95, 90, 60), fill(g('#3a2a5a'), 0.18))
    for k in range(5):
        cv.drawCircle(-60 + k * 22, -200 + (k % 2) * 16, 9, fill(g(shade(col, -0.2))))
    cv.restore()
    cv.drawPath(body, ink(W))
    # back plates (rounded, orange)
    for k, (px, py, rr) in enumerate(((-70, -205, 22), (-35, -232, 26), (5, -240, 24))):
        pl = path_smooth([(px - rr, py + 14), (px - rr * 0.4, py - rr), (px + rr * 0.5, py - rr * 0.9), (px + rr, py + 14)])
        cv.drawPath(pl, fill(g('#f0a040'))); cv.drawPath(pl, ink(W * 0.8))
    # little arm
    arm = path_smooth([(60, -150), (98, -140 + br * 3), (104, -124 + br * 3), (66, -132)])
    cv.drawPath(arm, fill(g(col))); cv.drawPath(arm, ink(W * 0.8))
    # head
    hx, hy = 92, -238
    head = path_smooth([(hx - 60, hy + 30), (hx - 58, hy - 40), (hx, hy - 66), (hx + 70, hy - 50), (hx + 96, hy - 6), (hx + 84, hy + 34), (hx + 20, hy + 52)])
    cv.drawPath(head, fill(g(col))); cv.drawPath(head, ink(W))
    cv.drawPath(ellipse(hx + 74, hy - 10, 5, 4), fill(INK))
    blink = (t * 0.37 + 0.2) % 1.0 < 0.035
    if blink:
        cv.drawLine(hx - 4, hy - 18, hx + 26, hy - 18, ink(5))
    else:
        cv.drawPath(ellipse(hx + 10, hy - 18, 21, 24), fill(g('#ffffff'))); cv.drawPath(ellipse(hx + 10, hy - 18, 21, 24), ink(4.5))
        cv.drawCircle(hx + 16, hy - 14, 11, fill(INK)); cv.drawCircle(hx + 20, hy - 19, 4, fill('#ffffff'))
    if expr == 'shocked':
        cv.drawPath(ellipse(hx + 52, hy + 22, 14, 12), fill(g('#7a2a3a'))); cv.drawPath(ellipse(hx + 52, hy + 22, 14, 12), ink(4))
    else:
        sm = skia.Path(); sm.moveTo(hx + 22, hy + 16); sm.quadTo(hx + 52, hy + 36, hx + 82, hy + 14)
        cv.drawPath(sm, ink(4.5))
    cv.drawCircle(hx - 14, hy + 8, 12, fill(g('#f08aa0'), 0.6))
    cv.restore()
