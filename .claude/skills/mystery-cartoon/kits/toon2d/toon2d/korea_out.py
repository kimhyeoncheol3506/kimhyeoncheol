"""Korean-history OUTDOOR sets (Goryeo / Baekje / Joseon): river_camp, mountain_pass, sea_battle, fortress_wall,
village_road. Built like outdoor.py: a pinhole Ground in metres split into depth bands, a sky plane, a blurred near
plane. Torches / beacon fires register emitters that glow in night, sunset, dawn and golden moods.
"""
import math

import skia

from .paint import (fill, stroke, ink, shade, mix, path_poly, path_smooth, rrect, ellipse, blurred, lin_grad,
                    rad_grad, argb, rng, surface)
from . import textures as tx
from . import setkit as sk
from .light import MOODS, halo, pool, god_rays
from .sets import Ground

GLOW = ('night', 'sunset', 'dawn', 'golden', 'dream')
BANDS = [('ground', 1.0, 0.35, 6.0), ('near', 2.2, 5.8, 13.0), ('mid', 5.0, 12.5, 40.0), ('far', 14.0, 38.0, 900.0)]


def _iw(s, k=0.022, lo=0.8, hi=3.4):
    return max(lo, min(hi, s * k))


# ============================================================================ painted pieces
def ink_mountains(cv, base, x0, x1, amp, col, fogc, seed=0, wav=200, a=1.0, strokes=True):
    """Ink-wash mountain ridge: sharp peaks, gradient into the fog at the foot, brush strokes down the slopes."""
    r = rng(seed)
    pts = [(x0, base + 60)]
    peaks = []
    x = x0
    while x < x1:
        x += r.uniform(wav * 0.35, wav * 0.8)
        h = amp * r.uniform(0.4, 1.0)
        pts.append((x, base - h)); peaks.append((x, base - h, h))
        x += r.uniform(wav * 0.3, wav * 0.6)
        pts.append((x, base - h * r.uniform(0.25, 0.6)))
    pts.append((x1 + 100, base + 60))
    body = path_poly(pts)
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_grad((0, base - amp), (0, base + 30), [argb(col, a), argb(mix(col, fogc, 0.75), a)]))
    cv.drawPath(body, p)
    if strokes:
        cv.save(); cv.clipPath(body, doAntiAlias=True)
        for (px, py, h) in peaks:
            for k in range(4):
                dx = r.uniform(-0.5, 0.5) * h
                sp = skia.Path(); sp.moveTo(px + dx * 0.15, py + 6)
                sp.quadTo(px + dx * 0.6, py + h * 0.35, px + dx, py + h * r.uniform(0.6, 1.0))
                cv.drawPath(sp, stroke(shade(col, -0.28), max(1.5, h * 0.035), 0.35 * a))
            cv.drawPath(path_poly([(px, py), (px + h * 0.7, base + 40), (px + h * 0.2, base + 40)]), fill(shade(col, -0.18), 0.25 * a))
        cv.restore()
        cv.drawPath(path_poly(pts[1:-1], close=False), stroke(shade(col, -0.35), 2.2, 0.45 * a))


def pine(cv, x, y, h, seed=0, iw=3.0, col='#2f5a3e', bark='#9a4a34', lean=None):
    """Twisted Korean red pine: reddish trunk with bark plates, flat layered needle pads."""
    r = rng(seed)
    lean = r.uniform(-0.35, 0.35) if lean is None else lean
    w = h * 0.045
    top = (x + lean * h * 0.6, y - h * 0.86)
    mid = (x + lean * h * 0.05 - r.uniform(0.05, 0.15) * h * (1 if lean > 0 else -1), y - h * 0.45)
    tr = skia.Path()
    tr.moveTo(x - w, y)
    tr.cubicTo(mid[0] - w, mid[1] + h * 0.1, mid[0] - w * 0.7, mid[1] - h * 0.1, top[0] - w * 0.3, top[1])
    tr.lineTo(top[0] + w * 0.3, top[1])
    tr.cubicTo(mid[0] + w * 0.7, mid[1] - h * 0.1, mid[0] + w, mid[1] + h * 0.1, x + w * 1.3, y)
    tr.close()
    cv.drawPath(tr, fill(bark))
    cv.save(); cv.clipPath(tr, doAntiAlias=True)
    for k in range(int(10)):
        yy = y - h * (0.05 + k * 0.08)
        cv.drawLine(x - w * 3, yy, x + w * 3 + lean * h, yy - w * 0.6, stroke(shade(bark, -0.3), max(0.8, w * 0.18), 0.6))
    cv.drawRect(skia.Rect.MakeLTRB(x, y - h, x + h, y + 2), fill('#3a1a2a', 0.18))
    cv.restore()
    cv.drawPath(tr, ink(iw))
    pads = []
    n = r.randint(4, 6)
    for k in range(n):
        u = 0.45 + 0.55 * k / (n - 1)
        side = -1 if k % 2 == 0 else 1
        cx_ = x + lean * h * 0.6 * u + side * h * r.uniform(0.12, 0.3) * (1.0 - 0.4 * u)
        cy_ = y - h * u
        pads.append((cx_, cy_, h * r.uniform(0.16, 0.26) * (1.15 - 0.4 * u), side, u))
    for (cx_, cy_, rw, side, u) in pads:
        bx = x + lean * h * 0.6 * u
        cv.drawLine(bx, cy_ + rw * 0.15, cx_, cy_ + rw * 0.1, stroke(bark, max(1, w * 0.45)))
        cv.drawLine(bx, cy_ + rw * 0.15, cx_, cy_ + rw * 0.1, ink(iw * 0.6))
    for (cx_, cy_, rw, side, u) in pads:
        pad = skia.Path()
        for j in range(5):
            pad.addOval(skia.Rect.MakeXYWH(cx_ - rw + j * rw * 0.42 - rw * 0.1, cy_ - rw * 0.32 + (abs(j - 2) * rw * 0.05), rw * 0.62, rw * 0.42))
        pad = skia.Op(pad, skia.Path(), skia.PathOp.kUnion_PathOp) or pad
        cv.drawPath(pad, fill(col))
        cv.save(); cv.clipPath(pad, doAntiAlias=True)
        cv.translate(-rw * 0.04, -rw * 0.12)
        cv.drawPath(pad, fill(shade(col, 0.28)))
        cv.restore()
        cv.drawPath(pad, ink(iw * 0.8))


def boulder(cv, x, y, w, col='#a8a4b0', seed=0, iw=3.0):
    r = rng(seed)
    h = w * r.uniform(0.5, 0.8)
    pts = [(x - w / 2, y), (x - w * 0.48, y - h * 0.5), (x - w * 0.25, y - h * 0.95), (x + w * 0.1, y - h),
           (x + w * 0.42, y - h * 0.7), (x + w * 0.52, y)]
    b = path_smooth(pts, tension=0.35)
    cv.drawPath(b, fill(col))
    cv.save(); cv.clipPath(b, doAntiAlias=True)
    cv.drawPath(path_poly([(x + w * 0.05, y - h * 1.1), (x + w * 0.6, y - h), (x + w * 0.6, y + 4), (x + w * 0.15, y + 4)]), fill('#3a2a4a', 0.22))
    cv.drawPath(ellipse(x - w * 0.22, y - h * 0.72, w * 0.14, h * 0.12), fill('#ffffff', 0.3))
    for k in range(3):
        cv.drawLine(x - w * 0.3 + k * w * 0.2, y - h * r.uniform(0.3, 0.8), x - w * 0.2 + k * w * 0.25, y - h * 0.1, stroke(shade(col, -0.3), max(1, w * 0.012), 0.6))
    cv.restore()
    cv.drawPath(b, ink(iw))


BANNER_COLS = [('#c8343c', '#f2c640'), ('#f2c640', '#c8343c'), ('#2d5bb0', '#f4efe4'), ('#2a2232', '#e8e2da'),
               ('#f4efe4', '#2d5bb0'), ('#2f8a5a', '#f2c640')]


def banner(cv, x, y, h, cols, seed=0, iw=3.0, dirx=1, wave=0.0, emblem=True):
    """Korean army banner on a tall pole: spear finial + red tassel, cloth with a flame-tooth fringe."""
    r = rng(seed)
    body, trim = cols
    pw = max(1.5, h * 0.012)
    cv.drawLine(x, y, x, y - h, stroke('#6a4028', pw))
    cv.drawLine(x, y, x, y - h, ink(max(0.6, iw * 0.4), 0.6))
    # finial + tassel
    tip = path_poly([(x - pw * 1.6, y - h), (x, y - h - h * 0.07), (x + pw * 1.6, y - h)])
    cv.drawPath(tip, fill('#d8d4dc')); cv.drawPath(tip, ink(max(0.6, iw * 0.5)))
    cv.drawPath(path_smooth([(x - pw * 2.2, y - h + pw), (x + pw * 2.2, y - h + pw), (x + pw * 1.4, y - h + h * 0.07), (x - pw * 1.4, y - h + h * 0.07)]), fill('#d8343c'))
    bw, bh = h * 0.3 * dirx, h * 0.4
    y0 = y - h * 0.97
    top, bot = [], []
    n = 10
    for k in range(n + 1):
        u = k / n
        dy = math.sin(u * 4.2 + seed + wave) * h * 0.02 * u
        top.append((x + bw * u, y0 + dy + u * h * 0.03))
        bot.append((x + bw * u * 0.95, y0 + bh + dy + u * h * 0.05))
    cloth = path_poly(top + bot[::-1])
    # flame-tooth fringe on the fly side and bottom
    fr = []
    for k in range(n + 1):
        px, py = bot[k]
        fr.append((px, py))
        if k < n:
            nx, ny = bot[k + 1]
            fr.append(((px + nx) / 2, (py + ny) / 2 + h * 0.045))
    fr_side = []
    fx, fy = top[-1]
    for k in range(6):
        u = k / 5
        px, py = fx + (bot[-1][0] - fx) * u, fy + (bot[-1][1] - fy) * u
        fr_side.append((px, py))
        if k < 5:
            fr_side.append((px + bw * 0.14, py + bh * 0.1))
    fringe = path_poly([(x, bot[0][1])] + fr + fr_side[::-1] + [(x, y0)])
    cv.drawPath(fringe, fill(trim)); cv.drawPath(fringe, ink(max(0.6, iw * 0.6)))
    cv.drawPath(cloth, fill(body))
    cv.save(); cv.clipPath(cloth, doAntiAlias=True)
    for k in range(3):
        u = 0.3 + k * 0.25
        cv.drawLine(x + bw * u, y0, x + bw * (u - 0.05), y0 + bh * 1.1, stroke(shade(body, -0.22), max(1, h * 0.018), 0.5))
    if emblem:
        cx_, cy_ = x + bw * 0.5, y0 + bh * 0.5
        rr = abs(bw) * 0.26
        cv.drawCircle(cx_, cy_, rr, fill(trim))
        kind = seed % 3
        if kind == 0:   # taeguk-like swirl (two-colour circle)
            hp = skia.Path(); hp.addArc(skia.Rect.MakeXYWH(cx_ - rr, cy_ - rr, 2 * rr, 2 * rr), 180, 180); hp.close()
            cv.drawPath(hp, fill(shade(body, -0.35)))
            cv.drawCircle(cx_ - rr * 0.5, cy_, rr * 0.5, fill(shade(body, -0.35)))
            cv.drawCircle(cx_ + rr * 0.5, cy_, rr * 0.5, fill(trim))
        elif kind == 1:  # three-stroke character-like mark
            for j in range(3):
                cv.drawLine(cx_ - rr * 0.55, cy_ - rr * 0.5 + j * rr * 0.5, cx_ + rr * 0.55, cy_ - rr * 0.5 + j * rr * 0.5, stroke(body, max(1, rr * 0.18)))
            cv.drawLine(cx_, cy_ - rr * 0.7, cx_, cy_ + rr * 0.7, stroke(body, max(1, rr * 0.18)))
        else:            # star / flame mark
            pts = []
            for j in range(10):
                a = -math.pi / 2 + j * math.pi / 5
                rad = rr * (0.8 if j % 2 == 0 else 0.35)
                pts.append((cx_ + math.cos(a) * rad, cy_ + math.sin(a) * rad))
            cv.drawPath(path_poly(pts), fill(body))
        cv.drawCircle(cx_, cy_, rr, ink(max(0.6, iw * 0.5)))
    cv.restore()
    cv.drawPath(cloth, ink(max(0.6, iw * 0.7)))


def torch(cv, x, y, s, E=None, key=None, glow=False):
    """Standing iron-basket torch (s = px per metre). Registers an emitter."""
    h = 2.0 * s
    cv.drawLine(x, y, x, y - h, stroke('#5a3a28', max(1.5, 0.07 * s)))
    cv.drawLine(x, y, x, y - h, ink(_iw(s, 0.012), 0.6))
    for sx in (-1, 1):
        cv.drawLine(x, y - 0.15 * s, x + sx * 0.3 * s, y + 0.02 * s, stroke('#5a3a28', max(1, 0.05 * s)))
    bk = path_poly([(x - 0.2 * s, y - h - 0.25 * s), (x + 0.2 * s, y - h - 0.25 * s), (x + 0.1 * s, y - h + 0.05 * s), (x - 0.1 * s, y - h + 0.05 * s)])
    cv.drawPath(bk, fill('#3a3040')); cv.drawPath(bk, ink(_iw(s, 0.015)))
    fy = y - h - 0.22 * s
    for (w, hh, col) in ((0.24, 0.62, '#e8502a'), (0.16, 0.46, '#f8a030'), (0.08, 0.28, '#fff0a0')):
        fl = path_smooth([(x - w * s, fy), (x - w * 0.6 * s, fy - hh * 0.5 * s), (x - w * 0.1 * s, fy - hh * 0.8 * s),
                          (x + w * 0.1 * s, fy - hh * s), (x + w * 0.5 * s, fy - hh * 0.55 * s), (x + w * s, fy)])
        cv.drawPath(fl, fill(col))
    if E is not None:
        E[key or (round(x), round(y))] = dict(pos=(x, fy - 0.25 * s), ground=y, s=s)


def emit_lights(E, glow, night, z0=None, z1=None, big=3.0):
    def f(cv, mm):
        for k, e in E.items():
            if z0 is not None and not (z0 <= e.get('Z', z0) < z1):
                continue
            x, y = e['pos']; s = e['s']
            if glow:
                halo(cv, x, y, big * s, (255, 170, 80), 0.8 if night else 0.55, core=0.12)
                pool(cv, x, e['ground'], 2.2 * s, 0.55 * s, (255, 160, 80), 0.45 if night else 0.3)
            else:
                halo(cv, x, y, 0.7 * s, (255, 200, 120), 0.3, core=0.2)
    return f


def tent(cv, x, y, w, h, col='#ece2c8', acc='#c8343c', seed=0, iw=3.0, lit=False, E=None, Z=0):
    """Army ridge tent seen from the front: canvas walls, pitched roof, dark door flap, guy ropes, coloured hem."""
    wall = h * 0.4
    body = path_poly([(x - w / 2, y), (x - w / 2, y - wall), (x, y - h), (x + w / 2, y - wall), (x + w / 2, y)])
    for sx in (-1, 1):
        cv.drawLine(x + sx * w * 0.5, y - wall, x + sx * w * 0.85, y + h * 0.02, stroke('#5a4a3a', max(0.8, iw * 0.35)))
    cv.drawPath(body, fill(col))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    cv.drawPath(path_poly([(x, y - h), (x + w / 2, y - wall), (x + w / 2, y + 2), (x + w * 0.15, y + 2)]), fill('#3a2a4a', 0.2))
    for k in range(1, 4):
        cv.drawLine(x - w / 2 + k * w / 4, y - wall + abs(k - 2) * 0 - (h - wall) * (1 - abs(k * 0.25 - 0.5) * 2), x - w / 2 + k * w / 4, y, stroke(shade(col, -0.15), max(0.8, iw * 0.35), 0.7))
    cv.drawRect(skia.Rect.MakeLTRB(x - w, y - h * 0.12, x + w, y), fill(acc))
    cv.restore()
    door = path_poly([(x - w * 0.14, y), (x, y - h * 0.62), (x + w * 0.14, y)])
    cv.drawPath(door, fill('#2a1a2a' if not lit else '#f8b060'))
    if lit and E is not None:
        E[(round(x), round(y), 't')] = dict(pos=(x, y - h * 0.25), ground=y, s=w * 0.35, Z=Z)
    cv.drawPath(path_poly([(x, y - h * 0.62), (x + w * 0.2, y), (x + w * 0.1, y)]), fill(shade(col, -0.1)))
    cv.drawPath(body, ink(iw))
    cv.drawLine(x, y - h, x, y - h - h * 0.15, stroke('#5a3a28', max(1, iw * 0.6)))
    cv.drawPath(path_poly([(x, y - h - h * 0.15), (x + w * 0.16, y - h - h * 0.11), (x, y - h - h * 0.07)]), fill(acc))


def giwa_roof(cv, cx, ye, w, h, col='#3e4352', iw=3.0, dancheong=True, seed=0):
    """Curved Korean tiled roof. ye = eave line (centre), w = eave width, h = roof height."""
    lift = h * 0.32
    L, R = cx - w / 2, cx + w / 2
    eave = skia.Path()
    eave.moveTo(L - w * 0.03, ye - lift)
    eave.quadTo(cx - w * 0.3, ye + h * 0.02, cx, ye + h * 0.02)
    eave.quadTo(cx + w * 0.3, ye + h * 0.02, R + w * 0.03, ye - lift)
    # roof body
    rp = skia.Path(eave)
    rp.lineTo(cx + w * 0.34, ye - h * 0.92)
    rp.quadTo(cx, ye - h * 0.86, cx - w * 0.34, ye - h * 0.92)
    rp.close()
    if dancheong:   # painted bracket band under the eave
        db = path_poly([(cx - w * 0.44, ye - lift * 0.35), (cx + w * 0.44, ye - lift * 0.35), (cx + w * 0.4, ye + h * 0.2), (cx - w * 0.4, ye + h * 0.2)])
        cv.drawPath(db, fill('#3a8a6a'))
        cv.save(); cv.clipPath(db, doAntiAlias=True)
        n = max(6, int(w / max(8, h * 0.18)))
        for k in range(n + 1):
            px = cx - w * 0.44 + k * w * 0.88 / n
            cv.drawCircle(px, ye + h * 0.08, max(1.2, h * 0.04), fill('#c8343c'))
            cv.drawCircle(px, ye + h * 0.08, max(0.6, h * 0.018), fill('#f2e6c0'))
        cv.drawRect(skia.Rect.MakeLTRB(cx - w, ye + h * 0.15, cx + w, ye + h * 0.22), fill('#c8343c'))
        cv.restore()
        cv.drawPath(db, ink(iw * 0.6))
    cv.drawPath(rp, fill(col))
    cv.save(); cv.clipPath(rp, doAntiAlias=True)
    n = max(8, int(w / max(6, h * 0.12)))
    for k in range(n + 1):
        u = k / n
        x0 = L + w * u
        x1 = cx - w * 0.34 + w * 0.68 * u
        cv.drawLine(x0, ye + 10, x1, ye - h * 0.9, stroke(shade(col, 0.22), max(0.8, h * 0.035), 0.8))
        cv.drawLine(x0 + w / n * 0.5, ye + 10, x1 + w * 0.68 / n * 0.5, ye - h * 0.9, stroke(shade(col, -0.3), max(0.6, h * 0.02), 0.7))
    cv.drawRect(skia.Rect.MakeLTRB(cx, ye - h, R + w, ye + h), fill('#2a1a3a', 0.12))
    cv.restore()
    cv.drawPath(rp, ink(iw))
    # ridge with upturned ends
    rg = path_poly([(cx - w * 0.38, ye - h * 0.9), (cx - w * 0.36, ye - h * 1.06), (cx + w * 0.36, ye - h * 1.06), (cx + w * 0.38, ye - h * 0.9)])
    cv.drawPath(rg, fill(shade(col, 0.15))); cv.drawPath(rg, ink(iw * 0.8))
    for sx in (-1, 1):
        orn = path_poly([(cx + sx * w * 0.36, ye - h * 1.06), (cx + sx * w * 0.42, ye - h * 1.22), (cx + sx * w * 0.385, ye - h * 0.9)])
        cv.drawPath(orn, fill(shade(col, 0.1))); cv.drawPath(orn, ink(iw * 0.7))
    # eave tile-ends (white dots)
    for k in range(13):
        u = k / 12
        t_ = abs(u - 0.5) * 2
        px = L + w * u
        py = ye + h * 0.02 - (lift + h * 0.02) * t_ ** 2.2
        cv.drawCircle(px, py, max(1, h * 0.03), fill('#e8e2da'))


def hanok(cv, x, y, w, h, s=None, seed=0, iw=3.0, lit=False, E=None, Z=0, roof='#3e4352', wall='#f0e8d8', base_col='#a8a0a8'):
    """Tiled-roof house front: stone base, timber posts, white plaster, paper lattice doors, curved roof."""
    bh = h * 0.12
    base = rrect(x - w * 0.42, y - bh, w * 0.84, bh, 2)
    cv.drawPath(base, fill(base_col))
    for k in range(6):
        cv.drawLine(x - w * 0.42 + k * w * 0.168, y - bh, x - w * 0.42 + k * w * 0.168, y, stroke(shade(base_col, -0.3), max(0.6, iw * 0.4)))
    cv.drawPath(base, ink(iw * 0.8))
    wh = h * 0.42
    wy = y - bh - wh
    cv.drawRect(skia.Rect.MakeXYWH(x - w * 0.38, wy, w * 0.76, wh), fill(wall))
    bays = 4
    for k in range(bays):
        bx = x - w * 0.38 + k * w * 0.76 / bays
        bw = w * 0.76 / bays
        dx, dw = bx + bw * 0.14, bw * 0.72
        dh = wh * 0.78
        drect = skia.Rect.MakeXYWH(dx, wy + wh * 0.12, dw, dh)
        lit_k = lit and (k + seed) % 3 != 0
        cv.drawRect(drect, fill('#f4e2b0' if lit_k else '#efe6cc'))
        for j in range(1, 4):
            cv.drawLine(dx + dw * j / 4, wy + wh * 0.12, dx + dw * j / 4, wy + wh * 0.12 + dh, stroke('#8a5a3a', max(0.6, iw * 0.35)))
        for j in range(1, 6):
            cv.drawLine(dx, wy + wh * 0.12 + dh * j / 6, dx + dw, wy + wh * 0.12 + dh * j / 6, stroke('#8a5a3a', max(0.6, iw * 0.35)))
        cv.drawRect(drect, ink(iw * 0.5))
        if lit_k and E is not None:
            E[(round(dx), round(wy), 'w')] = dict(pos=(dx + dw / 2, wy + wh * 0.5), ground=y, s=dw * 0.9, Z=Z)
    for k in range(bays + 1):
        px = x - w * 0.38 + k * w * 0.76 / bays
        cv.drawRect(skia.Rect.MakeXYWH(px - w * 0.012, wy - h * 0.04, w * 0.024, wh + h * 0.04), fill('#7a4a30'))
    cv.drawRect(skia.Rect.MakeXYWH(x - w * 0.4, wy - h * 0.05, w * 0.8, h * 0.05), fill('#7a4a30'))
    cv.drawRect(skia.Rect.MakeXYWH(x - w * 0.38, wy, w * 0.76, wh), ink(iw * 0.7))
    giwa_roof(cv, x, wy - h * 0.02, w * 1.08, h * 0.46, col=roof, iw=iw, seed=seed)


def choga(cv, x, y, w, h, seed=0, iw=3.0, lit=False, E=None, Z=0, straw='#c8a25a'):
    """Thatched-roof farmhouse (choga): mud walls, timber posts, paper door, rounded rope-netted thatch."""
    r = rng(seed)
    bh = h * 0.1
    cv.drawPath(rrect(x - w * 0.4, y - bh, w * 0.8, bh, 3), fill('#9a8e8a'))
    for k in range(7):
        cv.drawPath(ellipse(x - w * 0.36 + k * w * 0.12, y - bh * 0.5, w * 0.055, bh * 0.4), stroke('#6a5e60', max(0.6, iw * 0.35)))
    cv.drawPath(rrect(x - w * 0.4, y - bh, w * 0.8, bh, 3), ink(iw * 0.7))
    wh = h * 0.44
    wy = y - bh - wh
    wallr = skia.Rect.MakeXYWH(x - w * 0.36, wy, w * 0.72, wh)
    cv.drawRect(wallr, fill('#d2b48a'))
    cv.save(); cv.clipRect(wallr)
    for k in range(18):
        px, py = x + r.uniform(-0.36, 0.36) * w, wy + r.uniform(0.05, 0.95) * wh
        cv.drawLine(px, py, px + w * 0.03, py + r.uniform(-1, 1), stroke('#a88a62', max(0.6, iw * 0.3), 0.6))
    cv.restore()
    # door + window
    dx, dw, dh = x - w * 0.12, w * 0.2, wh * 0.82
    lit_d = lit and seed % 2 == 0
    cv.drawRect(skia.Rect.MakeXYWH(dx, wy + wh * 0.1, dw, dh), fill('#f4e2b0' if lit_d else '#ece2c8'))
    for j in range(1, 3):
        cv.drawLine(dx + dw * j / 3, wy + wh * 0.1, dx + dw * j / 3, wy + wh * 0.1 + dh, stroke('#7a4a30', max(0.6, iw * 0.35)))
    for j in range(1, 5):
        cv.drawLine(dx, wy + wh * 0.1 + dh * j / 5, dx + dw, wy + wh * 0.1 + dh * j / 5, stroke('#7a4a30', max(0.6, iw * 0.35)))
    cv.drawRect(skia.Rect.MakeXYWH(dx, wy + wh * 0.1, dw, dh), ink(iw * 0.5))
    if lit_d and E is not None:
        E[(round(dx), round(wy), 'c')] = dict(pos=(dx + dw / 2, wy + wh * 0.5), ground=y, s=dw * 0.9, Z=Z)
    wx_ = x + w * 0.14
    cv.drawRect(skia.Rect.MakeXYWH(wx_, wy + wh * 0.25, w * 0.14, wh * 0.36), fill('#ece2c8'))
    cv.drawLine(wx_ + w * 0.07, wy + wh * 0.25, wx_ + w * 0.07, wy + wh * 0.61, stroke('#7a4a30', max(0.6, iw * 0.35)))
    cv.drawRect(skia.Rect.MakeXYWH(wx_, wy + wh * 0.25, w * 0.14, wh * 0.36), ink(iw * 0.5))
    for px in (-0.36, -0.15, 0.08, 0.36):
        cv.drawRect(skia.Rect.MakeXYWH(x + px * w - w * 0.012, wy, w * 0.024, wh), fill('#6a4a30'))
    cv.drawRect(wallr, ink(iw * 0.7))
    # thatch roof (rounded loaf)
    rh = h * 0.5
    ye = wy + h * 0.04
    th = path_smooth([(x - w * 0.52, ye), (x - w * 0.5, ye - rh * 0.35), (x - w * 0.36, ye - rh * 0.85), (x, ye - rh),
                      (x + w * 0.36, ye - rh * 0.85), (x + w * 0.5, ye - rh * 0.35), (x + w * 0.52, ye),
                      (x, ye + rh * 0.06)], tension=0.45)
    cv.drawPath(th, fill(straw))
    cv.save(); cv.clipPath(th, doAntiAlias=True)
    for k in range(9):    # rope net
        u = (k + 0.5) / 9 - 0.5
        sp = skia.Path(); sp.moveTo(x + u * w * 0.5, ye - rh * 1.05); sp.quadTo(x + u * w * 0.9, ye - rh * 0.5, x + u * w * 1.1, ye + rh * 0.1)
        cv.drawPath(sp, stroke(shade(straw, -0.35), max(0.8, iw * 0.45), 0.8))
    for k in range(3):
        sp = skia.Path(); yy = ye - rh * (0.25 + k * 0.25)
        sp.moveTo(x - w * 0.6, yy + rh * 0.12); sp.quadTo(x, yy - rh * 0.12, x + w * 0.6, yy + rh * 0.12)
        cv.drawPath(sp, stroke(shade(straw, -0.35), max(0.8, iw * 0.45), 0.8))
    for k in range(40):
        px, py = x + r.uniform(-0.5, 0.5) * w, ye - r.uniform(0, 1) * rh
        cv.drawLine(px, py, px + r.uniform(-3, 3), py + rh * 0.08, stroke(shade(straw, 0.25), max(0.6, iw * 0.3), 0.7))
    cv.drawRect(skia.Rect.MakeLTRB(x + w * 0.1, ye - rh * 1.2, x + w, ye + rh), fill('#3a2a4a', 0.15))
    cv.restore()
    cv.drawPath(th, ink(iw))
    # straw fringe at the eave
    for k in range(24):
        px = x - w * 0.5 + k * w / 23
        cv.drawLine(px, ye - 2, px + r.uniform(-2, 2), ye + rh * 0.07, stroke(shade(straw, -0.2), max(0.6, iw * 0.4)))


def onggi(cv, x, y, w, iw=2.5, col='#6a3a28'):
    """Earthenware sauce jar with a lid."""
    h = w * 1.05
    body = path_smooth([(x - w * 0.28, y), (x - w * 0.5, y - h * 0.45), (x - w * 0.36, y - h * 0.88), (x + w * 0.36, y - h * 0.88),
                        (x + w * 0.5, y - h * 0.45), (x + w * 0.28, y)], tension=0.4)
    cv.drawPath(body, fill(col))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    cv.drawPath(ellipse(x - w * 0.2, y - h * 0.55, w * 0.1, h * 0.22), fill('#ffffff', 0.25))
    cv.drawLine(x - w * 0.5, y - h * 0.62, x + w * 0.5, y - h * 0.62, stroke(shade(col, 0.25), max(0.6, iw * 0.5), 0.7))
    cv.drawRect(skia.Rect.MakeLTRB(x + w * 0.1, y - h, x + w, y + 2), fill('#2a1a2a', 0.2))
    cv.restore()
    cv.drawPath(body, ink(iw))
    lid = ellipse(x, y - h * 0.9, w * 0.38, h * 0.1)
    cv.drawPath(lid, fill(shade(col, 0.15))); cv.drawPath(lid, ink(iw * 0.8))
    cv.drawCircle(x, y - h * 0.97, w * 0.06, fill(shade(col, -0.1)))


def persimmon(cv, x, y, h, seed=0, iw=3.0):
    r = rng(seed)
    bark = '#4a3438'
    def branch(x0, y0, ang, L, wd, depth):
        x1, y1 = x0 + math.cos(ang) * L, y0 + math.sin(ang) * L
        cv.drawLine(x0, y0, x1, y1, stroke(bark, wd)); cv.drawLine(x0, y0, x1, y1, ink(max(0.5, iw * 0.3), 0.5))
        if depth == 0:
            for k in range(4):
                fx, fy = x1 + r.uniform(-L * 0.4, L * 0.4), y1 + r.uniform(-L * 0.3, L * 0.3)
                cv.drawPath(ellipse(fx, fy, h * 0.03, h * 0.015), fill(r.choice(['#5a7a3a', '#c8783a', '#a85a2a'])))
            for k in range(3):
                fx, fy = x1 + r.uniform(-L * 0.35, L * 0.35), y1 + r.uniform(-L * 0.2, L * 0.35)
                cv.drawCircle(fx, fy, h * 0.022, fill('#f07a20')); cv.drawCircle(fx, fy, h * 0.022, ink(max(0.6, iw * 0.4)))
                cv.drawCircle(fx - h * 0.007, fy - h * 0.007, h * 0.006, fill('#ffffff', 0.6))
            return
        for k in range(2 + (depth > 1)):
            branch(x1, y1, ang + r.uniform(-0.7, 0.7), L * r.uniform(0.6, 0.8), wd * 0.65, depth - 1)
    tr = path_poly([(x - h * 0.03, y), (x - h * 0.015, y - h * 0.42), (x + h * 0.015, y - h * 0.42), (x + h * 0.035, y)])
    cv.drawPath(tr, fill(bark)); cv.drawPath(tr, ink(iw))
    for a in (-2.1, -1.6, -1.1):
        branch(x, y - h * 0.4, a, h * 0.22, h * 0.022, 3)


def stone_wall_run(cv, G, X, Z0, Z1, hgt=1.2, col='#9a9088', seed=0, cap=False):
    """Dry-stone wall (dol-dam) running along Z at lateral position X."""
    r = rng(seed)
    zs = []
    z = Z0
    while z < Z1:
        zs.append(z); z *= 1.07
    zs.append(Z1)
    bot = [G.proj(X, z) for z in zs]
    top = [(px, py - hgt * G.scale(z)) for (px, py), z in zip(bot, zs)]
    poly = path_poly(bot + top[::-1])
    cv.drawPath(poly, fill(col))
    cv.save(); cv.clipPath(poly, doAntiAlias=True)
    for z in zs[:-1]:
        s = G.scale(z)
        for row in range(4):
            for j in range(2):
                zz = z * (1 + j * 0.035)
                px, py = G.proj(X, zz)
                py -= (row + 0.5) / 4 * hgt * G.scale(zz)
                rw = G.scale(zz) * r.uniform(0.15, 0.25)
                e = ellipse(px, py, rw * 0.45, rw * 0.6)
                cv.drawPath(e, fill(shade(col, r.uniform(-0.15, 0.15))))
                cv.drawPath(e, ink(_iw(G.scale(zz), 0.008, 0.4, 2.0), 0.8))
    cv.restore()
    cv.drawPath(poly, ink(_iw(G.scale(Z0), 0.01, 0.6, 3.0)))
    if cap:
        cv.drawPath(path_poly(top, close=False), stroke('#3e4352', max(2, G.scale(Z0) * 0.12)))


def _water_tile(base, light, dark, seed=0, n=420):
    s = surface(600, 600, base)
    cv = s.getCanvas()
    r = rng(seed)
    for k in range(n):
        x, y = r.uniform(0, 600), r.uniform(0, 600)
        L = r.uniform(20, 70)
        p = skia.Path(); p.moveTo(x - L, y); p.quadTo(x, y - r.uniform(4, 10), x + L, y)
        cv.drawPath(p, stroke(r.choice([light, dark]), r.uniform(2, 5), 0.7))
    return s.makeImageSnapshot()


def _sky(G, m, mood, seed, heavy=False, sun=None, moon=(820, 150, 60)):
    night = mood == 'night'
    def paint(cv):
        cols = None
        if heavy:
            cols = ((150, 150, 172), (88, 88, 112)) if not night else ((70, 76, 140), (36, 38, 90))
            if mood in ('sunset', 'golden'):
                cols = ((230, 160, 140), (110, 80, 120))
        sk.sky(cv, m, seed=seed, clouds=11 if heavy else 7, cloud_band=(-450, 520), cloud_scale=1.5 if heavy else 1.2,
               sun=sun if (sun and mood in ('day', 'golden', 'sunset', 'dawn') and not heavy) else None,
               moon=moon if night else None, stars=0 if (heavy or not night) else 180, cloud_cols=cols)
        if heavy:
            p = skia.Paint(AntiAlias=True)
            p.setShader(lin_grad((0, -700), (0, 500), [argb((60, 60, 90), 0.45), argb((60, 60, 90), 0.0)]))
            cv.drawRect(skia.Rect.MakeLTRB(-600, -800, 1700, 600), p)
        if mood in ('sunset', 'dawn') and sun and not heavy:
            sx, sy = sun[0], G.h0 - 60
            sp = skia.Paint(AntiAlias=True)
            sp.setShader(rad_grad((sx, sy), 560, [argb((255, 230, 160), 0.8), argb((255, 170, 110), 0.3), argb((255, 160, 120), 0)], [0.15, 0.45, 1]))
            cv.drawCircle(sx, sy, 560, sp)
            cv.drawCircle(sx, sy, 90, fill('#fff0c0'))
    return paint


def _assemble(G, m, mood, tiles, objs, far_extra, E, sky_painter, fg, fog_a=0.35, extra=None, sky_lights=None):
    from .outdoor import _band_painter
    glow = mood in GLOW
    night = mood == 'night'
    layers = [('sky', 30.0, sky_painter, dict(grade=False, lights=sky_lights))]
    for name, pz, z0, z1 in BANDS:
        ob = [o for o in objs if not (getattr(o[1], 'per_band', False) and not (z0 <= o[0] < z1))]
        if name == 'far':
            ob.append((899.0, far_extra))
        Eb = {}
        def lights(cv, mm, z0=z0, z1=z1):
            sub = {k: e for k, e in E.items() if z0 <= e.get('Z', 0) < z1}
            emit_lights(sub, glow, night)(cv, mm)
            if name == 'mid' and mood == 'day':
                pass
        opts = dict(lights=lights)
        if name == 'far':
            opts.update(blur=0.8)
        back = ('#2e1a44', 0.55) if mood in ('sunset', 'dawn') else None
        layers.append(('k_' + name, pz, _band_painter(G, tiles, ob, z0, z1, fog=(m['fog'], fog_a, 220), back=back), opts))
    if extra:
        layers += extra
    layers.append(('fg', 0.55, fg, dict(blur=10)))
    return layers


def _per_band(fn_factory, spans):
    """One object per band (like the road in outdoor.field): fn_factory(z0, z1) -> painter."""
    out = []
    for (key, a, b) in spans:
        f = fn_factory(a, b)
        f.per_band = True
        out.append((key, f))
    return out


SPANS = ((5.99, 0.35, 6.0), (12.99, 6.0, 13.0), (39.99, 13.0, 40.0), (899.5, 40.0, 900.0))


def _place(E, Z):
    """Wrap an emitter dict so it remembers its depth (for per-band light passes)."""
    class _D(dict):
        def __setitem__(self, k, v):
            v['Z'] = Z
            E[k] = v
    return _D()


# ============================================================================ 1. RIVER CAMP (Wihwa-do, 1388)
def river_camp(mood):
    """Goryeo army camp on a river island in a rain-swollen brown river; Liaodong mountains on the far bank."""
    m = MOODS[mood]
    night = mood == 'night'
    vx, h0 = 540, 900
    G = Ground(vx, h0, 3.2)
    E = {}
    SHORE = 13.0
    FAR_BANK = 90.0
    tiles = [(tx.grass(900, 900, base='#7a8a48', seed=41, density=0.9, blade=30), 4, 4, (-400, 400), {})]
    objs = []
    river_img = _water_tile('#9a7650', '#c8a47a', '#7a5a3c', seed=4, n=160)

    def shore_z(X):
        return SHORE + 1.2 * math.sin(X * 0.35) + 0.6 * math.sin(X * 1.1 + 1)

    def river_fac(a, b):
        def paint(cv):
            lo, hi = max(a, SHORE - 2), min(b, FAR_BANK)
            if lo >= hi:
                return
            G.tile(cv, river_img, 9.0, 6.0, xr=(-500, 500), zr=(lo, hi))
            # island edge (mud bank) drawn over the water
            if a < SHORE + 3 and b > SHORE - 3:
                xs = [x * 0.5 for x in range(-80, 81)]
                edge = [G.proj(X, shore_z(X)) for X in xs]
                near_pts = [G.proj(X, max(a, 0.4) if a > 0.4 else 0.4) for X in xs]
                land = path_poly(edge + [G.proj(40, max(a, 6.0)), G.proj(-40, max(a, 6.0))])
                cv.save(); cv.clipPath(path_poly(edge + [(2000, 3000), (-1000, 3000)]), doAntiAlias=True)
                G.tile(cv, tiles[0][0], 4, 4, xr=(-400, 400), zr=(max(a, 0.4), SHORE + 3))
                cv.restore()
                cv.drawPath(path_poly(edge, close=False), stroke('#6a5040', 6))
                cv.drawPath(path_poly([(x, y + 4) for x, y in edge], close=False), stroke('#d8c0a0', 3, 0.6))
            # water sheen + floating debris + rain rings
            r = rng(int(a * 10) + 3)
            for k in range(70):
                X, Z = r.uniform(-60, 60), r.uniform(lo, hi)
                if Z < SHORE + 0.5:
                    continue
                x, y = G.proj(X, Z); s = G.scale(Z)
                cv.drawPath(ellipse(x, y, 0.35 * s, 0.07 * s), stroke(mix('#e8d8c0', m['key'], 0.3), max(0.6, 0.03 * s), 0.55))
                if k % 9 == 0:
                    cv.drawLine(x - 0.6 * s, y, x + 0.6 * s, y - 0.05 * s, stroke('#4a3020', max(1, 0.1 * s)))
        return paint
    for key, f in _per_band(river_fac, SPANS):
        objs.append((key, f))

    # tents on the island
    tents = [(-3.6, 6.0, 3.0, '#ece2c8', '#c8343c'), (3.8, 6.5, 3.2, '#e8d8a8', '#2d5bb0'), (-6.0, 8.5, 3.4, '#ece2c8', '#2a2232'),
             (6.2, 9.0, 3.4, '#e8d8a8', '#c8343c'), (-2.0, 10.5, 3.0, '#ece2c8', '#f2c640'), (2.4, 11.2, 3.0, '#e0cc98', '#2f8a5a'),
             (-8.5, 11.5, 3.4, '#e8d8a8', '#c8343c'), (8.8, 11.8, 3.2, '#ece2c8', '#2d5bb0')]
    for k, (X, Z, w, c1, c2) in enumerate(tents):
        def tn(cv, X=X, Z=Z, w=w, c1=c1, c2=c2, k=k):
            x, y = G.proj(X, Z); s = G.scale(Z)
            tent(cv, x, y, w * s, w * 0.8 * s, c1, c2, seed=k, iw=_iw(s, 0.012), lit=night and k % 2 == 0, E=_place(E, Z), Z=Z)
        objs.append((Z, tn))
    # banners: a forest of them
    r = rng(77)
    for k in range(22):
        X = r.choice([-1, 1]) * r.uniform(3.0, 12)
        Z = r.uniform(4.6, 12.4)
        if abs(X) < 2.6 and Z < 7:
            continue
        def bn(cv, X=X, Z=Z, k=k):
            x, y = G.proj(X, Z); s = G.scale(Z)
            banner(cv, x, y, 5.5 * s * rng(k).uniform(0.85, 1.1), BANNER_COLS[k % len(BANNER_COLS)], seed=k, iw=_iw(s, 0.012),
                   dirx=1 if X < 0 else -1, wave=k)
        objs.append((Z - 0.01, bn))
    # torches
    for k, (X, Z) in enumerate(((-2.3, 4.6), (2.4, 5.0), (-1.4, 8.0), (1.6, 9.5), (-4.5, 12.0), (5.0, 12.2))):
        def tc(cv, X=X, Z=Z):
            x, y = G.proj(X, Z)
            torch(cv, x, y, G.scale(Z), _place(E, Z))
        objs.append((Z, tc))
    # weapon rack + supply crates near the acting area
    def rack(cv):
        X, Z = 3.0, 5.2
        x, y = G.proj(X, Z); s = G.scale(Z)
        for dx in (-0.6, 0.6):
            cv.drawLine(x + dx * s, y, x + dx * s, y - 1.3 * s, stroke('#6a4028', 0.08 * s))
        cv.drawLine(x - 0.7 * s, y - 1.1 * s, x + 0.7 * s, y - 1.1 * s, stroke('#6a4028', 0.08 * s))
        for j in range(5):
            px = x + (-0.5 + j * 0.25) * s
            cv.drawLine(px, y, px + 0.15 * s, y - 2.2 * s, stroke('#8a6a4a', 0.04 * s))
            sp = path_poly([(px + 0.12 * s, y - 2.2 * s), (px + 0.17 * s, y - 2.5 * s), (px + 0.2 * s, y - 2.2 * s)])
            cv.drawPath(sp, fill('#c8ccd8')); cv.drawPath(sp, ink(_iw(s, 0.008)))
            cv.drawCircle(px + 0.16 * s, y - 2.15 * s, 0.05 * s, fill('#c8343c'))
        sk.crate(cv, x - 2.6 * s, y, 0.9 * s, 0.7 * s, col='#9a6a3a')
        sk.crate(cv, x - 2.3 * s, y - 0.7 * s, 0.7 * s, 0.55 * s, col='#a8763e')
    objs.append((5.2, rack))
    # raft at the shore (left)
    def raft(cv):
        X0, Z = -3.8, SHORE + 0.6
        s = G.scale(Z)
        for j in range(7):
            zz = Z + j * 0.32
            a_, b_ = G.proj(X0 - 2.2, zz), G.proj(X0 + 1.6, zz)
            cv.drawLine(a_[0], a_[1], b_[0], b_[1], stroke('#8a5a36', max(2, 0.28 * G.scale(zz))))
            cv.drawLine(a_[0], a_[1] - 0.1 * G.scale(zz), b_[0], b_[1] - 0.1 * G.scale(zz), stroke('#b07a4a', max(1, 0.08 * G.scale(zz))))
            cv.drawCircle(b_[0], b_[1], max(1, 0.13 * G.scale(zz)), fill('#d8b088'))
        for xx in (X0 - 1.5, X0 + 0.9):
            p0, p1 = G.proj(xx, Z), G.proj(xx, Z + 2.0)
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], stroke('#d8c890', max(1, 0.06 * s)))
        x, y = G.proj(X0, Z)
        cv.drawLine(x + 1.4 * s, y, x + 2.8 * s, y - 2.6 * s, stroke('#6a4028', max(1.5, 0.06 * s)))   # pole
    objs.append((SHORE + 0.6, raft))
    # rocks + reeds along the shore
    for k in range(26):
        X = r.uniform(-22, 22); Z = shore_z(X) - r.uniform(0.2, 1.2)
        def rd(cv, X=X, Z=Z, k=k):
            x, y = G.proj(X, Z); s = G.scale(Z)
            if k % 3 == 0:
                boulder(cv, x, y, 0.8 * s, '#8a8494', seed=k, iw=_iw(s, 0.012))
            else:
                for j in range(6):
                    cv.drawLine(x + j * 0.05 * s, y, x + (j - 3) * 0.12 * s, y - rng(k + j).uniform(0.6, 1.2) * s, stroke('#6a7a3a', max(1, 0.04 * s)))
        objs.append((Z, rd))

    def far_extra(cv):
        fogc = m['fog']
        ink_mountains(cv, h0 + 10, -600, 1700, 360, mix('#3e5470', fogc, 0.5), fogc, seed=3, wav=260)
        ink_mountains(cv, h0 + 30, -600, 1700, 170, mix('#2e4a50', fogc, 0.3), fogc, seed=4, wav=180)
        # far bank strip + tiny distant fort walls
        x0, yb = G.proj(-200, FAR_BANK)
        cv.drawRect(skia.Rect.MakeLTRB(-600, yb - 8, 1700, yb + 6), fill(mix('#4a5a3a', fogc, 0.3)))
        rr = rng(9)
        for k in range(30):
            sk.foliage(cv, rr.uniform(-400, 1500), yb - 4, rr.uniform(10, 22), mix('#2f4a3a', fogc, 0.35), seed=k + 90, ink_w=0)
        G.tile(cv, river_img, 9.0, 6.0, xr=(-500, 500), zr=(40.0, FAR_BANK))

    def rain(cv):
        rr = rng(5)
        for k in range(520):
            x, y = rr.uniform(-450, 1550), rr.uniform(-560, 2450)
            L = rr.uniform(40, 110)
            cv.drawLine(x, y, x - L * 0.22, y + L, stroke('#e8ecff', rr.uniform(1.2, 2.6), rr.uniform(0.18, 0.4)))

    def fg(cv):
        for (x, y, h, sd) in ((-80, 2350, 1400, 2), (1180, 2300, 1300, 5)):
            for j in range(18):
                rr = rng(sd * 10 + j)
                cv.drawPath(path_poly([(x + j * 14 - 120, y), (x + j * 14 - 120 + rr.uniform(-160, 160), y - h * rr.uniform(0.5, 1.0)), (x + j * 14 - 100, y)]),
                            fill(rr.choice(['#3a4a2a', '#4a5a30', '#2e3e26'])))
    layers = _assemble(G, m, mood, tiles, objs, far_extra, E, _sky(G, m, mood, 21, heavy=True), fg,
                       extra=[('rain', 0.8, rain, dict(grade=False))])
    return layers, dict(ground=G, ground_y=1700, h0=h0, vx=vx, raft=(-3.8, SHORE + 0.6), river_z=SHORE)


# ============================================================================ 2. MOUNTAIN PASS (Tanhyeon)
def mountain_pass(mood):
    """Narrow rocky pass: a dirt path climbing between granite cliffs, twisted pines, a wooden palisade across the
    path with banners, layered misty ink-wash mountains behind."""
    m = MOODS[mood]
    night = mood == 'night'
    vx, h0 = 540, 860
    G = Ground(vx, h0, 1.4)
    E = {}
    tiles = [(tx.grass(900, 900, base='#6a7a44', seed=51, density=0.8, blade=26), 4, 4, (-400, 400), {}),
             ]
    objs = []

    def path_x(Z):
        return 0.8 * math.sin(Z * 0.18)

    def path_fac(a, b):
        def paint(cv):
            zs = []
            z = max(a, 0.4)
            while z < min(b, 80):
                zs.append(z); z *= 1.05
            zs.append(min(b, 80))
            if len(zs) < 2:
                return
            L = [G.proj(path_x(z) - 1.3, z) for z in zs]
            R = [G.proj(path_x(z) + 1.3, z) for z in zs]
            cv.drawPath(path_poly(L + R[::-1]), fill('#c8a47a'))
            for off in (-0.5, 0.5):
                cv.drawPath(path_poly([G.proj(path_x(z) + off, z) for z in zs], close=False), stroke('#9a7a54', 10, 0.35))
            for side in (L, R):
                cv.drawPath(path_poly(side, close=False), stroke('#6a5a3a', 3, 0.6))
        return paint
    for key, f in _per_band(path_fac, SPANS):
        objs.append((key, f))

    # granite cliffs both sides (big rock faces)
    def cliff(cv, X, Z, w, h, sd, sgn):
        x, y = G.proj(X, Z); s = G.scale(Z)
        rr = rng(sd)
        pts = [(x - sgn * w * 0.1 * s, y + 0.3 * s)]
        n = 7
        for k in range(n + 1):
            u = k / n
            pts.append((x + sgn * (u * w * s), y - h * s * (0.55 + 0.45 * math.sin(u * 2.4 + sd) * rr.uniform(0.7, 1.0))))
        pts.append((x + sgn * w * s * 1.2, y + 0.3 * s))
        body = path_poly(pts)
        col = '#a8a2ae'
        cv.drawPath(body, fill(col))
        cv.save(); cv.clipPath(body, doAntiAlias=True)
        for k in range(14):
            yy = y - rr.uniform(0.1, 1.0) * h * s
            xx = x + sgn * rr.uniform(0, w) * s
            cv.drawLine(xx, yy, xx + sgn * rr.uniform(0.5, 2.0) * s, yy + rr.uniform(-0.6, 0.6) * s, stroke(shade(col, -0.32), max(1, 0.05 * s), 0.7))
            cv.drawLine(xx, yy, xx + rr.uniform(-0.3, 0.3) * s, yy + rr.uniform(0.8, 2.2) * s, stroke(shade(col, -0.25), max(1, 0.04 * s), 0.6))
        shade_x = x + sgn * w * 0.15 * s
        cv.drawRect(skia.Rect.MakeLTRB(min(shade_x, x - sgn * 30), y - h * s * 1.2, max(shade_x, x - sgn * 30), y + s), fill('#3a2a4a', 0.28))
        for k in range(6):   # moss
            xx = x + sgn * rr.uniform(0.1, 0.9) * w * s
            yy = y - rr.uniform(0.5, 1.0) * h * s
            cv.drawPath(ellipse(xx, yy, 0.6 * s, 0.18 * s), fill('#5a7a3a', 0.7))
        cv.restore()
        cv.drawPath(body, ink(_iw(s, 0.012)))
        return pts
    cliffs = [(-2.6, 4.5, 8, 5.5, 1, -1), (2.8, 5.5, 8, 6.5, 2, 1), (-2.4, 10.0, 9, 7.0, 3, -1), (2.6, 12.0, 9, 8.0, 4, 1),
              (-2.6, 20.0, 12, 10.0, 5, -1), (3.0, 24.0, 12, 11.0, 6, 1)]
    for (X, Z, w, h, sd, sgn) in cliffs:
        def cf(cv, X=X, Z=Z, w=w, h=h, sd=sd, sgn=sgn):
            pts = cliff(cv, X, Z, w, h, sd, sgn)
            s = G.scale(Z)
            # pines on the cliff top
            for j in (2, 4, 6):
                px, py = pts[j]
                pine(cv, px, py + 0.2 * s, rng(sd * 7 + j).uniform(3.5, 5.5) * s, seed=sd * 7 + j, iw=_iw(s, 0.012))
        objs.append((Z, cf))
    # palisade across the path
    PZ = 10.5
    def palisade(cv):
        x0, y0 = G.proj(-2.6, PZ)
        s = G.scale(PZ)
        n = 18
        for k in range(n):
            X = -2.6 + k * 5.4 / (n - 1)
            x, y = G.proj(X + path_x(PZ) * 0.3, PZ)
            hh = (2.3 + 0.25 * math.sin(k * 1.7)) * s
            st = path_poly([(x - 0.12 * s, y), (x - 0.12 * s, y - hh), (x, y - hh - 0.35 * s), (x + 0.12 * s, y - hh), (x + 0.12 * s, y)])
            cv.drawPath(st, fill('#8a5e3a' if k % 2 else '#7a5034'))
            cv.drawLine(x - 0.03 * s, y, x - 0.03 * s, y - hh, stroke('#5a3a24', max(1, 0.025 * s), 0.6))
            cv.drawPath(st, ink(_iw(s, 0.01)))
        for hh in (0.7, 1.7):
            a_, b_ = G.proj(-2.7, PZ), G.proj(2.9, PZ)
            cv.drawLine(a_[0], a_[1] - hh * s, b_[0], b_[1] - hh * s, stroke('#d8c890', max(2, 0.07 * s)))
        # cheval-de-frise spikes in front
        for k in range(5):
            x, y = G.proj(-2.0 + k * 1.0, PZ - 1.2)
            ss = G.scale(PZ - 1.2)
            for sgn in (-1, 1):
                cv.drawLine(x - sgn * 0.45 * ss, y, x + sgn * 0.45 * ss, y - 0.9 * ss, stroke('#7a5034', max(1.5, 0.08 * ss)))
                cv.drawLine(x - sgn * 0.45 * ss, y, x + sgn * 0.45 * ss, y - 0.9 * ss, ink(_iw(ss, 0.008)))
    objs.append((PZ, palisade))
    for k, X in enumerate((-2.2, -0.6, 1.1, 2.6)):
        def bn(cv, X=X, k=k):
            x, y = G.proj(X, PZ + 0.3); s = G.scale(PZ + 0.3)
            banner(cv, x, y, 5.0 * s, BANNER_COLS[(k + 2) % len(BANNER_COLS)], seed=k + 3, iw=_iw(s, 0.012), dirx=1 if k % 2 else -1, wave=k)
        objs.append((PZ + 0.3, bn))
    for X in (-1.9, 2.1):
        def tc(cv, X=X):
            x, y = G.proj(X, PZ - 0.6)
            torch(cv, x, y, G.scale(PZ - 0.6), _place(E, PZ - 0.6))
        objs.append((PZ - 0.6, tc))
    # boulders + pines near the acting area
    for k, (X, Z, kind, sz) in enumerate(((-2.0, 2.6, 'b', 1.2), (2.3, 3.0, 'b', 1.5), (-1.7, 6.5, 'b', 0.9), (1.9, 7.5, 'b', 1.1),
                                          (-3.4, 3.4, 'p', 6.5), (3.6, 6.8, 'p', 7.0), (-1.6, 14.0, 'b', 1.4), (1.5, 16.0, 'b', 1.0),
                                          (-1.5, 30.0, 'p', 8.0), (1.6, 36.0, 'p', 9.0))):
        if kind == 'b':
            fn = (lambda cv, X=X, Z=Z, sz=sz, k=k: boulder(cv, *G.proj(X, Z), sz * G.scale(Z), '#b0aab4', seed=k + 11, iw=_iw(G.scale(Z), 0.012)))
        else:
            fn = (lambda cv, X=X, Z=Z, sz=sz, k=k: pine(cv, *G.proj(X, Z), sz * G.scale(Z), seed=k + 31, iw=_iw(G.scale(Z), 0.012)))
        objs.append((Z, fn))
    r = rng(8)
    for k in range(60):
        Z = 2.0 * (1.05 ** r.uniform(0, 70)); X = path_x(Z) + r.choice([-1, 1]) * r.uniform(1.4, 2.4)
        def gr(cv, X=X, Z=Z, k=k):
            x, y = G.proj(X, Z); s = G.scale(Z)
            if k % 4 == 0:
                boulder(cv, x, y, 0.35 * s, '#9a96a2', seed=k, iw=_iw(s, 0.01))
            else:
                for j in range(5):
                    cv.drawLine(x, y, x + (j - 2) * 0.1 * s, y - rng(k + j).uniform(0.25, 0.5) * s, stroke('#5a7a3a', max(1, 0.03 * s)))
        objs.append((Z, gr))

    def far_extra(cv):
        fogc = m['fog']
        ink_mountains(cv, h0 + 10, -600, 1700, 520, mix('#4a5a78', fogc, 0.6), fogc, seed=11, wav=300)
        ink_mountains(cv, h0 + 30, -600, 1700, 360, mix('#3e5468', fogc, 0.45), fogc, seed=12, wav=230)
        ink_mountains(cv, h0 + 50, -600, 1700, 200, mix('#2e4a48', fogc, 0.3), fogc, seed=13, wav=170)
        # mist bands between ridges
        for yy, a in ((h0 - 120, 0.35), (h0 - 20, 0.45)):
            p = skia.Paint(AntiAlias=True)
            p.setShader(lin_grad((0, yy - 60), (0, yy + 60), [argb(fogc, 0), argb(fogc, a), argb(fogc, 0)]))
            cv.drawRect(skia.Rect.MakeLTRB(-600, yy - 60, 1700, yy + 60), p)
        rr = rng(19)
        for k in range(10):     # tiny pines on far ridges
            x = rr.uniform(-300, 1400)
            pine(cv, x, h0 + 40 - rr.uniform(0, 80), rr.uniform(30, 60), seed=k + 200, iw=0.8, col=mix('#2f5a3e', fogc, 0.4), bark=mix('#9a4a34', fogc, 0.4))

    def fg(cv):
        pine(cv, -260, 1000, 1500, seed=7, iw=7, lean=0.15)
        boulder(cv, 1180, 2300, 900, '#8a8494', seed=4, iw=6)
    layers = _assemble(G, m, mood, tiles, objs, far_extra, E, _sky(G, m, mood, 31, sun=(860, 300, 70)), fg, fog_a=0.42)
    return layers, dict(ground=G, ground_y=1700, h0=h0, vx=vx, palisade=(0.0, PZ))


# ============================================================================ 3. SEA BATTLE (panokseon deck)
def panokseon(cv, x, y, L, col='#7a5034', iw=2.0, flag='#c8343c', sails=True, seed=0):
    """Side view of a Joseon panokseon: deep hull, upper shield deck with gun ports, command pavilion, mat sails."""
    h = L * 0.16
    hull = path_poly([(x - L / 2, y - h * 0.9), (x + L / 2, y - h * 1.0), (x + L * 0.4, y), (x - L * 0.42, y)])
    cv.drawPath(hull, fill(col))
    for k in range(3):
        cv.drawLine(x - L * 0.45, y - h * (0.25 + k * 0.25), x + L * 0.45, y - h * (0.28 + k * 0.25), stroke(shade(col, -0.3), max(0.6, iw * 0.4)))
    cv.drawPath(hull, ink(iw))
    sw = rrect(x - L * 0.44, y - h * 1.9, L * 0.88, h * 0.95, 2)
    cv.drawPath(sw, fill(shade(col, 0.15)))
    for k in range(10):
        px = x - L * 0.4 + k * L * 0.088
        cv.drawRect(skia.Rect.MakeXYWH(px, y - h * 1.5, L * 0.03, h * 0.28), fill('#1e1426'))
    cv.drawPath(sw, ink(iw))
    # pavilion
    pv = skia.Rect.MakeXYWH(x - L * 0.12, y - h * 2.6, L * 0.24, h * 0.7)
    cv.drawRect(pv, fill('#c8343c')); cv.drawRect(pv, ink(iw * 0.8))
    giwa_roof(cv, x, y - h * 2.6, L * 0.3, h * 0.6, iw=iw * 0.8, dancheong=False)
    if sails:
        for k, (mx, mh) in enumerate(((-0.18, 4.6), (0.22, 4.0))):
            px = x + mx * L
            cv.drawLine(px, y - h * 1.9, px, y - h * (1.9 + mh), stroke('#5a3a24', max(1, iw * 0.9)))
            sl = path_poly([(px - L * 0.1, y - h * (1.9 + mh * 0.92)), (px + L * 0.1, y - h * (1.9 + mh * 0.95)), (px + L * 0.11, y - h * 2.4), (px - L * 0.09, y - h * 2.4)])
            cv.drawPath(sl, fill('#d8c49a'))
            for j in range(1, 6):
                yy = y - h * (2.4 + (mh * 0.92 - 0.5) * j / 6)
                cv.drawLine(px - L * 0.095, yy, px + L * 0.105, yy, stroke('#8a6a44', max(0.6, iw * 0.5)))
            cv.drawPath(sl, ink(iw * 0.8))
            cv.drawPath(path_poly([(px, y - h * (1.9 + mh)), (px + L * 0.06, y - h * (1.9 + mh - 0.2)), (px, y - h * (1.9 + mh - 0.4))]), fill(flag))


def turtle_ship(cv, x, y, L, iw=2.0, smoke_a=0.6):
    """Geobukseon silhouette: low hull, spiked shell roof with hexagon plates, dragon head breathing smoke."""
    h = L * 0.14
    hull = path_poly([(x - L / 2, y - h), (x + L / 2, y - h), (x + L * 0.42, y), (x - L * 0.44, y)])
    cv.drawPath(hull, fill('#6a4630'))
    for k in range(8):
        cv.drawRect(skia.Rect.MakeXYWH(x - L * 0.38 + k * L * 0.1, y - h * 0.75, L * 0.03, h * 0.3), fill('#1e1426'))
    cv.drawPath(hull, ink(iw))
    shell = skia.Path()
    shell.moveTo(x - L * 0.47, y - h)
    shell.cubicTo(x - L * 0.4, y - h * 2.6, x + L * 0.36, y - h * 2.6, x + L * 0.45, y - h)
    shell.close()
    cv.drawPath(shell, fill('#4a5a5a'))
    cv.save(); cv.clipPath(shell, doAntiAlias=True)
    for row in range(3):
        for k in range(10):
            px = x - L * 0.45 + k * L * 0.1 + (row % 2) * L * 0.05
            py = y - h * (1.25 + row * 0.42)
            hx = [(px + math.cos(a) * L * 0.045, py + math.sin(a) * h * 0.22) for a in [i * math.pi / 3 for i in range(6)]]
            cv.drawPath(path_poly(hx), stroke('#2e3a3e', max(0.6, iw * 0.5)))
            cv.drawLine(px, py, px, py - h * 0.12, stroke('#d8d4dc', max(0.8, iw * 0.6)))
    cv.restore()
    cv.drawPath(shell, ink(iw))
    # dragon head at the bow (right)
    hx_, hy_ = x + L * 0.5, y - h * 1.5
    head = path_smooth([(x + L * 0.42, y - h * 1.05), (x + L * 0.44, y - h * 1.7), (hx_ + L * 0.03, y - h * 2.0), (hx_ + L * 0.1, y - h * 1.65),
                        (hx_ + L * 0.08, y - h * 1.3), (x + L * 0.47, y - h * 1.0)])
    cv.drawPath(head, fill('#c8a040')); cv.drawPath(head, ink(iw))
    cv.drawCircle(hx_ + L * 0.03, y - h * 1.75, max(1, L * 0.008), fill('#c8343c'))
    for k in range(4):
        cv.drawCircle(hx_ + L * (0.14 + k * 0.05), y - h * (1.5 + k * 0.25), L * (0.025 + k * 0.012), fill('#b8b4c0', smoke_a * (1 - k * 0.2)))
    # oars
    for k in range(7):
        px = x - L * 0.35 + k * L * 0.11
        cv.drawLine(px, y - h * 0.4, px - L * 0.04, y + h * 0.6, stroke('#5a3a24', max(0.8, iw * 0.6)))


def sea_battle(mood):
    """Deck of a Joseon panokseon: plank deck, shield-wall bulwark with gun ports, command platform, mat sail and
    mast, war drum, flags; the sea beyond with other panokseon, a turtle ship and islands."""
    m = MOODS[mood]
    night = mood == 'night'
    glow = mood in GLOW
    vx, h0 = 540, 880
    G = Ground(vx, h0, 2.2)
    E = {}
    DECK = 8.0   # bulwark at Z = DECK
    deck = tx.wood_planks(800, 800, plank=100, base='#a87448', vertical=True, seed=61)
    sea = _water_tile(mix('#2f6a8a', m['fog'], 0.15), '#7ab0c8', '#1e4a6a', seed=6, n=500)
    tiles = [(sea, 6.0, 4.0, (-600, 600), {})]
    objs = []

    def deck_fac(a, b):
        def paint(cv):
            lo, hi = max(a, 0.4), min(b, DECK + 0.2)
            if lo >= hi:
                return
            G.tile(cv, deck, 2.4, 2.4, xr=(-4.8, 4.8), zr=(lo, hi))
            for X in (-4.8, 4.8):
                G.line(cv, X, lo, X, hi, stroke('#5a3a24', 8))
        return paint
    for key, f in _per_band(deck_fac, SPANS[:3]):
        objs.append((key, f))

    def bulwark(cv):
        s = G.scale(DECK)
        a_, b_ = G.proj(-6.0, DECK), G.proj(6.0, DECK)
        top = a_[1] - 1.1 * s
        wall = skia.Rect.MakeLTRB(a_[0], top, b_[0], a_[1])
        planks = tx.wood_planks(600, 300, plank=50, base='#8a5a36', seed=62)
        cv.save(); cv.clipRect(wall)
        cv.drawImageRect(planks, wall)
        for k in range(9):
            px = a_[0] + (k + 0.5) * (b_[0] - a_[0]) / 9
            port = rrect(px - 0.22 * s, top + 0.35 * s, 0.44 * s, 0.38 * s, 0.05 * s)
            cv.drawPath(port, fill('#1e1426'))
            cv.drawPath(port, stroke('#e8c050', max(1, 0.03 * s)))
            # cannon muzzle (cheonja-chongtong) poking out
            cv.drawCircle(px, top + 0.54 * s, 0.12 * s, fill('#3a3a44'))
            cv.drawCircle(px, top + 0.54 * s, 0.06 * s, fill('#0e0a16'))
        cv.drawRect(skia.Rect.MakeLTRB(a_[0], top, b_[0], top + 0.18 * s), fill('#6a4028'))
        cv.restore()
        cv.drawRect(wall, ink(_iw(s, 0.01)))
        # shields hung on top rail
        for k in range(14):
            px = a_[0] + (k + 0.5) * (b_[0] - a_[0]) / 14
            sh = ellipse(px, top + 0.02 * s, 0.22 * s, 0.24 * s)
            cv.drawPath(sh, fill('#c8343c' if k % 2 else '#2d5bb0'))
            cv.drawCircle(px, top + 0.02 * s, 0.08 * s, fill('#f2c640'))
            cv.drawPath(sh, ink(_iw(s, 0.008)))
    objs.append((DECK, bulwark))

    # mast with a big mat sail (left)
    def mast(cv):
        X, Z = -2.6, 6.0
        x, y = G.proj(X, Z); s = G.scale(Z)
        cv.drawRect(skia.Rect.MakeXYWH(x - 0.16 * s, y - 16 * s, 0.32 * s, 16 * s), fill('#7a4a2e'))
        cv.drawRect(skia.Rect.MakeXYWH(x - 0.16 * s, y - 16 * s, 0.32 * s, 16 * s), ink(_iw(s, 0.01)))
        sl = path_poly([(x - 2.4 * s, y - 13.5 * s), (x + 2.8 * s, y - 13.8 * s), (x + 3.0 * s, y - 4.0 * s), (x - 2.2 * s, y - 4.2 * s)])
        cv.drawPath(sl, fill('#dcc89c'))
        cv.save(); cv.clipPath(sl, doAntiAlias=True)
        for j in range(12):
            yy = y - (4.2 + j * 0.8) * s
            cv.drawLine(x - 3 * s, yy, x + 3.2 * s, yy - 0.02 * s, stroke('#7a5a34', max(1.5, 0.08 * s)))
        rr = rng(3)
        for j in range(60):
            px, py = x + rr.uniform(-2.4, 3.0) * s, y - rr.uniform(4.2, 13.6) * s
            cv.drawLine(px, py, px + rr.uniform(-0.3, 0.3) * s, py + 0.25 * s, stroke('#b8a070', max(1, 0.03 * s), 0.6))
        cv.drawRect(skia.Rect.MakeLTRB(x + 0.4 * s, y - 14 * s, x + 3.2 * s, y - 4 * s), fill('#3a2a4a', 0.15))
        cv.restore()
        cv.drawPath(sl, ink(_iw(s, 0.012)))
        for (px, py) in ((x - 2.2 * s, y - 4.2 * s), (x + 3.0 * s, y - 4.0 * s)):
            G.line(cv, X - 2.0, Z - 2.5, X - 0.5, Z, stroke('#d8c890', 2))
        banner(cv, x, y - 15.8 * s, 2.6 * s, ('#c8343c', '#f2c640'), seed=6, iw=_iw(s, 0.01), dirx=1)
    objs.append((6.0, mast))

    # command platform (jangdae) on the right: raised pavilion with railing
    def platform(cv):
        X, Z = 3.9, 7.0
        x, y = G.proj(X, Z); s = G.scale(Z)
        ph = 1.8 * s
        base = skia.Rect.MakeLTRB(x - 1.8 * s, y - ph, x + 1.8 * s, y)
        cv.drawImageRect(tx.wood_planks(300, 200, plank=40, base='#8a5a36', seed=63), base)
        cv.drawRect(base, ink(_iw(s, 0.012)))
        for k in range(7):   # stairs
            sy = y - k * ph / 7
            cv.drawRect(skia.Rect.MakeLTRB(x - 2.6 * s + k * 0.12 * s, sy - ph / 7, x - 1.8 * s, sy), fill(shade('#a87448', -0.05 * (k % 2))))
            cv.drawLine(x - 2.6 * s + k * 0.12 * s, sy - ph / 7, x - 1.8 * s, sy - ph / 7, ink(_iw(s, 0.006)))
        top = y - ph
        for k in range(9):
            px = x - 1.8 * s + k * 0.45 * s
            cv.drawLine(px, top, px, top - 0.9 * s, stroke('#c8343c', max(1, 0.08 * s)))
        cv.drawLine(x - 1.8 * s, top - 0.9 * s, x + 1.8 * s, top - 0.9 * s, stroke('#c8343c', max(1.5, 0.12 * s)))
        for px in (x - 1.7 * s, x + 1.7 * s):
            cv.drawLine(px, top, px, top - 3.2 * s, stroke('#9a2a30', max(1.5, 0.16 * s)))
            cv.drawLine(px, top, px, top - 3.2 * s, ink(_iw(s, 0.008)))
        giwa_roof(cv, x, top - 3.2 * s, 4.6 * s, 1.5 * s, iw=_iw(s, 0.012))
        # commander's flag (sujagi-like big yellow)
        banner(cv, x + 1.9 * s, y, 6.5 * s, ('#f2c640', '#c8343c'), seed=4, iw=_iw(s, 0.01), dirx=1)
    objs.append((7.0, platform))

    # war drum on a stand
    def drum(cv):
        X, Z = 2.4, 4.6
        x, y = G.proj(X, Z); s = G.scale(Z)
        for sx in (-1, 1):
            cv.drawLine(x + sx * 0.5 * s, y, x + sx * 0.3 * s, y - 0.9 * s, stroke('#9a2a30', max(2, 0.08 * s)))
        body = rrect(x - 0.62 * s, y - 1.75 * s, 1.24 * s, 0.95 * s, 0.35 * s)
        cv.drawPath(body, fill('#c8343c'))
        cv.save(); cv.clipPath(body, doAntiAlias=True)
        cv.drawRect(skia.Rect.MakeLTRB(x - s, y - 1.75 * s, x + s, y - 1.6 * s), fill('#2d5bb0'))
        cv.drawRect(skia.Rect.MakeLTRB(x - s, y - 0.95 * s, x + s, y - 0.8 * s), fill('#2d5bb0'))
        cv.restore()
        face = ellipse(x - 0.62 * s, y - 1.27 * s, 0.16 * s, 0.47 * s)
        cv.drawPath(face, fill('#f0e2c0')); cv.drawPath(face, ink(_iw(s, 0.008)))
        cv.drawPath(body, ink(_iw(s, 0.01)))
        for k in range(8):
            cv.drawCircle(x - 0.55 * s + k * 0.16 * s, y - 1.68 * s, 0.03 * s, fill('#f2c640'))
        cv.drawLine(x + 0.3 * s, y - 0.9 * s, x + 0.9 * s, y - 0.2 * s, stroke('#6a4028', max(1.5, 0.05 * s)))
    objs.append((4.6, drum))
    # deck clutter: coiled rope, arrow baskets, cannonballs
    def clutter(cv):
        for (X, Z, kind) in ((-1.9, 2.8, 'rope'), (2.9, 2.5, 'balls'), (-3.6, 4.4, 'arrows'), (-0.8, 7.6, 'balls'), (1.0, 8.2, 'arrows')):
            x, y = G.proj(X, Z); s = G.scale(Z)
            if kind == 'rope':
                for j in range(4):
                    cv.drawPath(ellipse(x, y - j * 0.06 * s, (0.45 - j * 0.08) * s, (0.14 - j * 0.02) * s), stroke('#d8c890', max(1.5, 0.06 * s)))
                    cv.drawPath(ellipse(x, y - j * 0.06 * s, (0.45 - j * 0.08) * s, (0.14 - j * 0.02) * s), ink(_iw(s, 0.005), 0.6))
            elif kind == 'balls':
                for j, (dx, dy) in enumerate(((-0.2, 0), (0, 0), (0.2, 0), (-0.1, -0.17), (0.1, -0.17), (0, -0.33))):
                    cv.drawCircle(x + dx * s, y - 0.1 * s + dy * s, 0.1 * s, fill('#3a3a44'))
                    cv.drawCircle(x + dx * s - 0.03 * s, y - 0.13 * s + dy * s, 0.03 * s, fill('#9a9aaa'))
            else:
                bk = rrect(x - 0.25 * s, y - 0.6 * s, 0.5 * s, 0.6 * s, 0.08 * s)
                for j in range(9):
                    px = x + (-0.2 + j * 0.05) * s
                    cv.drawLine(px, y - 0.5 * s, px + (j - 4) * 0.02 * s, y - 1.2 * s, stroke('#b8905a', max(1, 0.02 * s)))
                    cv.drawPath(path_poly([(px + (j - 4) * 0.02 * s - 0.04 * s, y - 1.15 * s), (px + (j - 4) * 0.02 * s, y - 1.3 * s), (px + (j - 4) * 0.02 * s + 0.04 * s, y - 1.15 * s)]), fill('#f4efe4'))
                cv.drawPath(bk, fill('#b0884a')); cv.drawPath(bk, ink(_iw(s, 0.01)))
    objs.append((2.4, clutter))

    def far_extra(cv):
        fogc = m['fog']
        # islands
        ink_mountains(cv, h0 + 4, -200, 380, 210, mix('#3a5a5a', fogc, 0.45), fogc, seed=21, wav=140)
        ink_mountains(cv, h0 + 4, 760, 1400, 160, mix('#3a5a5a', fogc, 0.5), fogc, seed=22, wav=120)
        ink_mountains(cv, h0 + 2, 420, 640, 70, mix('#4a6a6a', fogc, 0.6), fogc, seed=23, wav=90)
        # fleet
        for (x, yy, L, fl) in ((60, h0 + 40, 300, '#c8343c'), (900, h0 + 36, 260, '#2d5bb0'), (1260, h0 + 50, 340, '#f2c640'), (600, h0 + 18, 140, '#c8343c')):
            panokseon(cv, x, yy, L, col=mix('#7a5034', fogc, 0.25), iw=1.6, flag=fl, seed=int(x))
        turtle_ship(cv, 380, h0 + 70, 330, iw=1.8)
        # sea glints
        rr = rng(4)
        for k in range(80):
            x, y = rr.uniform(-400, 1500), h0 + rr.uniform(4, 160)
            cv.drawLine(x, y, x + rr.uniform(10, 40), y, stroke(mix('#ffffff', m['key'], 0.4), 2, 0.5))

    def fg(cv):
        # near rail + rope (blurred)
        cv.drawRect(skia.Rect.MakeLTRB(-500, 2200, 1600, 2600), fill('#6a4028'))
        cv.drawLine(-500, 2200, 1600, 2160, stroke('#4a2a1a', 40))
        sp = skia.Path(); sp.moveTo(-500, -300); sp.quadTo(200, 400, 1600, -200)
        cv.drawPath(sp, stroke('#d8c890', 26))
    sun = (880, 360, 70)
    layers = _assemble(G, m, mood, tiles, objs, far_extra, E, _sky(G, m, mood, 41, sun=sun), fg, fog_a=0.3)
    return layers, dict(ground=G, ground_y=1650, h0=h0, vx=vx, drum=(2.4, 4.6), platform=(3.9, 7.0), mast=(-2.6, 6.0))


# ============================================================================ 4. FORTRESS WALL
def fortress_wall(mood):
    """On top of a stone fortress wall: crenellated parapet (yeojang) receding on both sides, a two-storey gate
    pavilion straddling the wall walk, beacon tower (bongsudae) with smoke on a distant hill, sea beyond."""
    m = MOODS[mood]
    night = mood == 'night'
    glow = mood in GLOW
    vx, h0 = 560, 900
    G = Ground(vx, h0, 1.6)
    E = {}
    GATE = 26.0
    walk = tx.stone_blocks(800, 800, bw=200, bh=120, base='#b0a89c', seed=71)
    tiles = [(tx.grass(900, 900, base='#6a8a48', seed=72, density=0.8), 6, 6, (-600, 600), {}),
             (walk, 2.0, 2.0, (-2.6, 2.6), {})]
    objs = []

    def parapet_run(cv, X, Z0, Z1, hgt, col, ports=True, sd=0):
        zs = []
        z = Z0
        while z < Z1:
            zs.append(z); z *= 1.12
        zs.append(Z1)
        for i in range(len(zs) - 1):
            za, zb = zs[i], zs[i + 1] / 1.02
            gap_z = zs[i + 1]
            pa, pb = G.proj(X, za), G.proj(X, zb)
            sa, sb = G.scale(za), G.scale(zb)
            poly = path_poly([pa, pb, (pb[0], pb[1] - hgt * sb), (pa[0], pa[1] - hgt * sa)])
            cv.drawPath(poly, fill(col))
            cv.save(); cv.clipPath(poly, doAntiAlias=True)
            for row in range(5):
                u = (row + 1) / 5
                cv.drawLine(pa[0], pa[1] - hgt * sa * u, pb[0], pb[1] - hgt * sb * u, stroke(shade(col, -0.25), max(0.6, sa * 0.015)))
            for j in range(3):
                zz = za + (zb - za) * (j + 0.5) / 3
                p = G.proj(X, zz); ss = G.scale(zz)
                cv.drawLine(p[0], p[1] - hgt * ss * (0.2 * (j % 2)), p[0], p[1] - hgt * ss, stroke(shade(col, -0.25), max(0.6, ss * 0.012)))
            if ports:
                zm = (za + zb) / 2
                p = G.proj(X, zm); ss = G.scale(zm)
                cv.drawPath(rrect(p[0] - 0.06 * ss, p[1] - hgt * ss * 0.65, 0.12 * ss, 0.22 * ss, 0.03 * ss), fill('#1e1426'))
            cv.restore()
            # tiled cap
            cv.drawLine(pa[0], pa[1] - hgt * sa, pb[0], pb[1] - hgt * sb, stroke('#3e4352', max(2, sa * 0.12)))
            cv.drawPath(poly, ink(_iw(sa, 0.008)))

    def walls_fac(a, b):
        def paint(cv):
            lo, hi = max(a, 0.9), min(b, GATE - 1.0)
            if lo < hi:
                parapet_run(cv, 2.6, lo, hi, 1.7, '#a8a09a', True, 1)
                parapet_run(cv, -2.6, lo, hi, 0.9, '#9a948e', False, 2)
        return paint
    for key, f in _per_band(walls_fac, SPANS[:3]):
        objs.append((key, f))

    # gate pavilion (mullu)
    def gate(cv):
        x, y = G.proj(0.0, GATE); s = G.scale(GATE)
        # stone gate base with arch, spanning the wall
        base = skia.Rect.MakeLTRB(x - 5.0 * s, y - 3.4 * s, x + 5.0 * s, y + 0.2 * s)
        cv.drawImageRect(tx.stone_blocks(500, 200, bw=60, bh=34, base='#a8a09a', seed=73), base)
        cv.drawRect(base, ink(_iw(s, 0.012)))
        arch = skia.Path(); arch.moveTo(x - 1.2 * s, y + 0.2 * s); arch.lineTo(x - 1.2 * s, y - 1.6 * s)
        arch.arcTo(skia.Rect.MakeLTRB(x - 1.2 * s, y - 2.8 * s, x + 1.2 * s, y - 0.4 * s), 180, 180, False)
        arch.lineTo(x + 1.2 * s, y + 0.2 * s); arch.close()
        cv.drawPath(arch, fill('#2a1e30')); cv.drawPath(arch, ink(_iw(s, 0.012)))
        # storey 1
        for (yb, w, hh, roof_w) in ((y - 3.4 * s, 7.0, 2.2, 9.6), (y - 6.6 * s, 5.0, 1.6, 7.2)):
            body = skia.Rect.MakeLTRB(x - w / 2 * s, yb - hh * s, x + w / 2 * s, yb)
            cv.drawRect(body, fill('#f0e8d8'))
            for k in range(5):
                px = x - w / 2 * s + k * w / 4 * s
                cv.drawRect(skia.Rect.MakeXYWH(px - 0.1 * s, yb - hh * s, 0.2 * s, hh * s), fill('#9a2a30'))
            for k in range(4):
                bx = x - w / 2 * s + (k + 0.15) * w / 4 * s
                lattice = skia.Rect.MakeXYWH(bx, yb - hh * s * 0.85, w / 4 * s * 0.7, hh * s * 0.7)
                lit_k = night and k % 2 == 0
                cv.drawRect(lattice, fill('#f4d090' if lit_k else '#e8dcc0'))
                for j in range(1, 4):
                    cv.drawLine(lattice.left() + lattice.width() * j / 4, lattice.top(), lattice.left() + lattice.width() * j / 4, lattice.bottom(), stroke('#7a4a30', max(0.6, s * 0.02)))
                if lit_k:
                    E[('g', k, yb)] = dict(pos=(lattice.centerX(), lattice.centerY()), ground=yb, s=lattice.width(), Z=GATE)
            cv.drawRect(body, ink(_iw(s, 0.012)))
            # balcony rail
            cv.drawLine(x - w / 2 * s, yb - 0.3 * s, x + w / 2 * s, yb - 0.3 * s, stroke('#9a2a30', max(1, 0.1 * s)))
            giwa_roof(cv, x, yb - hh * s, roof_w * s, 1.9 * s if hh > 2 else 2.3 * s, iw=_iw(s, 0.014))
        for k in range(2):
            banner(cv, x + (-4.4 + 8.8 * k) * s, y - 3.4 * s, 4.0 * s, BANNER_COLS[k], seed=k + 8, iw=_iw(s, 0.01), dirx=-1 if k else 1)
    objs.append((GATE, gate))
    # torches + flags along the parapet, weapons
    for k, Z in enumerate((3.0, 6.0, 11.0, 18.0)):
        def tc(cv, Z=Z, k=k):
            X = 2.2 if k % 2 == 0 else -2.2
            x, y = G.proj(X, Z)
            torch(cv, x, y, G.scale(Z), _place(E, Z))
        objs.append((Z, tc))
    for k, Z in enumerate((4.5, 8.0, 14.0, 21.0)):
        def bn(cv, Z=Z, k=k):
            x, y = G.proj(2.9, Z); s = G.scale(Z)
            banner(cv, x, y - 1.7 * s, 4.0 * s, BANNER_COLS[(k + 1) % len(BANNER_COLS)], seed=k + 20, iw=_iw(s, 0.01), dirx=-1, wave=k)
        objs.append((Z + 0.01, bn))
    def stones(cv):   # pile of throwing stones + arrow basket near the acting area
        x, y = G.proj(-1.9, 2.6); s = G.scale(2.6)
        rr = rng(5)
        for k in range(14):
            boulder(cv, x + rr.uniform(-0.5, 0.5) * s, y - rr.uniform(0, 0.25) * s, rr.uniform(0.15, 0.3) * s, '#9a948e', seed=k, iw=_iw(s, 0.006))
    objs.append((2.6, stones))

    def far_extra(cv):
        fogc = m['fog']
        # sea strip on the left horizon, plains and hills
        cv.drawRect(skia.Rect.MakeLTRB(-600, h0 - 4, 1700, h0 + 40), fill(mix('#4a7a9a', fogc, 0.4)))
        rr = rng(7)
        for k in range(40):
            x = rr.uniform(-500, 1600)
            cv.drawLine(x, h0 + rr.uniform(0, 30), x + 30, h0 + rr.uniform(0, 30), stroke('#ffffff', 1.5, 0.4))
        ink_mountains(cv, h0 + 30, 300, 1700, 300, mix('#3e5a50', fogc, 0.45), fogc, seed=31, wav=240)
        ink_mountains(cv, h0 + 50, -600, 600, 230, mix('#3a5a48', fogc, 0.35), fogc, seed=32, wav=180)
        # beacon tower on the left hill
        bx, by = 170, h0 - 110
        tw = path_poly([(bx - 40, by + 10), (bx - 30, by - 60), (bx + 30, by - 60), (bx + 40, by + 10)])
        cv.drawPath(tw, fill(mix('#a8a09a', fogc, 0.25)))
        for k in range(4):
            cv.drawLine(bx - 38 + k * 2, by - k * 18, bx + 38 - k * 2, by - k * 18, stroke(mix('#6a6260', fogc, 0.3), 1.5))
        cv.drawPath(tw, ink(1.8))
        for k in range(6):
            cv.drawCircle(bx + k * 22 + 10 * math.sin(k), by - 80 - k * 46, 22 + k * 9, fill(mix('#d8d4dc', fogc, 0.2), 0.6 - k * 0.07))
        fl = path_smooth([(bx - 18, by - 60), (bx - 8, by - 92), (bx + 4, by - 110), (bx + 12, by - 84), (bx + 18, by - 60)])
        cv.drawPath(fl, fill('#f8a030'))
        E['beacon'] = dict(pos=(bx, by - 80), ground=by, s=40, Z=899)

    def fg(cv):
        # big near crenellation block (right) and a pine bough (left top)
        blk = path_poly([(1040, 2600), (1060, 1700), (1700, 1600), (1700, 2600)])
        cv.drawPath(blk, fill('#9a928c'))
        for k in range(5):
            cv.drawLine(1040, 1760 + k * 180, 1700, 1660 + k * 180, stroke('#6a625e', 10))
        cv.drawRect(skia.Rect.MakeLTRB(1020, 1580, 1700, 1690), fill('#3e4352'))
        pine(cv, -300, 300, 1400, seed=9, iw=6, lean=0.6)
    layers = _assemble(G, m, mood, tiles, objs, far_extra, E, _sky(G, m, mood, 51, sun=(820, 420, 70)), fg, fog_a=0.38)
    return layers, dict(ground=G, ground_y=1650, h0=h0, vx=vx, gate=(0.0, GATE), beacon_px=(40, h0 - 200))


# ============================================================================ 5. VILLAGE ROAD (Joseon)
def village_road(mood):
    """Joseon village: dirt road between dry-stone walls, thatched choga and a few tiled hanok, a persimmon tree,
    jangdokdae sauce jars, mountains behind."""
    m = MOODS[mood]
    night = mood == 'night'
    vx, h0 = 540, 920
    G = Ground(vx, h0, 1.45)
    E = {}
    tiles = [(tx.grass(900, 900, base='#8a8a4a', seed=81, density=0.9, blade=28), 4, 4, (-400, 400), {}),
             (tx.sand(700, 700, base='#c89a6a', seed=82), 3, 3, (-2.0, 2.0), {})]
    objs = []

    def ruts(a, b):
        def paint(cv):
            lo, hi = max(a, 0.4), min(b, 300)
            if lo >= hi:
                return
            for off in (-0.7, 0.7):
                G.line(cv, off, lo, off, hi, stroke('#a8784a', 12, 0.35))
            for X in (-2.0, 2.0):
                G.line(cv, X, lo, X, hi, stroke('#7a6a3a', 4, 0.5))
        return paint
    for key, f in _per_band(ruts, SPANS):
        objs.append((key, f))

    def walls_fac(a, b):
        def paint(cv):
            for X in (-3.0, 3.0):
                for (z0, z1) in ((1.0, 7.0), (8.5, 16.0), (17.5, 34.0), (36.0, 70.0)):
                    lo, hi = max(a, z0), min(b, z1)
                    if lo < hi:
                        stone_wall_run(cv, G, X, lo, hi, 1.15, '#a09488', seed=int(z0 * 10 + X), cap=(z0 == 8.5))
        return paint
    for key, f in _per_band(walls_fac, SPANS):
        objs.append((key, f))

    houses = [(-7.5, 8.0, 'c', 7.0), (7.5, 9.0, 'c', 7.0), (-8.0, 17.0, 'h', 9.0), (8.0, 19.0, 'c', 7.0),
              (-7.0, 30.0, 'c', 7.0), (8.0, 34.0, 'h', 9.0), (-8.5, 50.0, 'c', 7.0), (8.0, 56.0, 'c', 7.0)]
    for k, (X, Z, kind, w) in enumerate(houses):
        def hs(cv, X=X, Z=Z, kind=kind, w=w, k=k):
            x, y = G.proj(X, Z); s = G.scale(Z)
            if kind == 'c':
                choga(cv, x, y, w * s, 4.6 * s, seed=k, iw=_iw(s, 0.012), lit=night, E=_place(E, Z), Z=Z)
            else:
                hanok(cv, x, y, w * s, 6.0 * s, seed=k, iw=_iw(s, 0.012), lit=night, E=_place(E, Z), Z=Z)
        objs.append((Z + 0.5, hs))
    # persimmon tree (right, near) + jangdokdae (left)
    def pers(cv):
        x, y = G.proj(4.8, 6.0)
        persimmon(cv, x, y, 9.0 * G.scale(6.0), seed=3, iw=_iw(G.scale(6.0), 0.012))
    objs.append((6.0, pers))
    def jars(cv):
        X, Z = -4.6, 5.0
        x, y = G.proj(X, Z); s = G.scale(Z)
        plat = path_poly([(x - 1.6 * s, y), (x + 1.4 * s, y), (x + 1.2 * s, y - 0.35 * s), (x - 1.4 * s, y - 0.35 * s)])
        cv.drawPath(plat, fill('#9a948e')); cv.drawPath(plat, ink(_iw(s, 0.01)))
        for (dx, dy, w) in ((-1.0, -0.5, 0.75), (0.0, -0.55, 0.85), (0.9, -0.5, 0.7), (-0.5, -0.3, 1.0), (0.55, -0.3, 0.95)):
            onggi(cv, x + dx * s, y + dy * s + 0.3 * s - 0.3 * s, w * s, iw=_iw(s, 0.01))
    objs.append((5.0, jars))
    # gate posts, straw bundles, a ox-cart wheel, lanterns
    def props(cv):
        for (X, Z) in ((-2.6, 3.0), (2.6, 11.0)):
            x, y = G.proj(X, Z); s = G.scale(Z)
            for j in range(3):   # straw bundles
                b = path_poly([(x - 0.3 * s + j * 0.25 * s, y), (x - 0.15 * s + j * 0.25 * s, y - 1.0 * s), (x + 0.05 * s + j * 0.25 * s, y - 1.0 * s), (x + 0.15 * s + j * 0.25 * s, y)])
                cv.drawPath(b, fill('#d8b060')); cv.drawPath(b, ink(_iw(s, 0.008)))
                cv.drawLine(x - 0.22 * s + j * 0.25 * s, y - 0.6 * s, x + 0.1 * s + j * 0.25 * s, y - 0.6 * s, stroke('#8a6a30', max(1, 0.04 * s)))
        x, y = G.proj(3.4, 3.6); s = G.scale(3.6)
        cv.drawCircle(x, y - 0.6 * s, 0.6 * s, stroke('#6a4028', max(2, 0.1 * s)))
        for k in range(8):
            a = k * math.pi / 4
            cv.drawLine(x, y - 0.6 * s, x + math.cos(a) * 0.6 * s, y - 0.6 * s + math.sin(a) * 0.6 * s, stroke('#6a4028', max(1, 0.05 * s)))
        cv.drawCircle(x, y - 0.6 * s, 0.6 * s, ink(_iw(s, 0.01)))
    objs.append((3.0, props))
    for k, Z in enumerate((4.0, 12.0, 22.0)):
        def lan(cv, Z=Z, k=k):
            X = -2.8 if k % 2 == 0 else 2.8
            x, y = G.proj(X, Z); s = G.scale(Z)
            cv.drawLine(x, y, x, y - 2.2 * s, stroke('#5a3a28', max(1.5, 0.08 * s)))
            cv.drawLine(x, y - 2.2 * s, x + 0.5 * s * (1 if X < 0 else -1), y - 2.2 * s, stroke('#5a3a28', max(1, 0.06 * s)))
            lx = x + 0.45 * s * (1 if X < 0 else -1)
            lb = rrect(lx - 0.2 * s, y - 2.1 * s, 0.4 * s, 0.55 * s, 0.12 * s)
            cv.drawPath(lb, fill('#f4d8a0' if night else '#e8dcc0')); cv.drawPath(lb, ink(_iw(s, 0.008)))
            cv.drawRect(skia.Rect.MakeXYWH(lx - 0.2 * s, y - 2.15 * s, 0.4 * s, 0.08 * s), fill('#c8343c'))
            cv.drawRect(skia.Rect.MakeXYWH(lx - 0.2 * s, y - 1.6 * s, 0.4 * s, 0.08 * s), fill('#c8343c'))
            E[('lan', k)] = dict(pos=(lx, y - 1.8 * s), ground=y, s=s * 0.7, Z=Z)
        objs.append((Z, lan))
    r = rng(14)
    for k in range(40):
        Z = 4.0 * (1.06 ** r.uniform(0, 50)); X = r.choice([-1, 1]) * r.uniform(9, 30)
        def tr(cv, X=X, Z=Z, k=k):
            x, y = G.proj(X, Z)
            if k % 3 == 0:
                pine(cv, x, y, rng(k).uniform(6, 9) * G.scale(Z), seed=k + 50, iw=_iw(G.scale(Z), 0.01))
            else:
                sk.foliage(cv, x, y - 0.8 * G.scale(Z), 1.4 * G.scale(Z), rng(k).choice(['#5a7a3a', '#7a8a3a', '#a8783a']), seed=k, ink_w=_iw(G.scale(Z), 0.01))
        objs.append((Z, tr))

    def far_extra(cv):
        fogc = m['fog']
        ink_mountains(cv, h0 + 10, -600, 1700, 420, mix('#4a5a78', fogc, 0.55), fogc, seed=61, wav=280)
        ink_mountains(cv, h0 + 30, -600, 1700, 220, mix('#3e5a48', fogc, 0.35), fogc, seed=62, wav=200)
        rr = rng(63)
        for k in range(30):
            sk.foliage(cv, rr.uniform(-400, 1500), h0 + 30, rr.uniform(16, 34), mix('#3f5a3a', fogc, 0.4), seed=k + 70, ink_w=0)
        for k in range(6):   # distant roofs
            x = rr.uniform(-200, 1300)
            choga(cv, x, h0 + 28, 70, 46, seed=k + 5, iw=0.8, straw=mix('#c8a25a', fogc, 0.35))

    def fg(cv):
        persimmon(cv, -260, 2600, 3000, seed=8, iw=7)
        onggi(cv, 1150, 2500, 700, iw=6)
    layers = _assemble(G, m, mood, tiles, objs, far_extra, E, _sky(G, m, mood, 61, sun=(820, 380, 70)), fg, fog_a=0.36)
    return layers, dict(ground=G, ground_y=1700, h0=h0, vx=vx, persimmon=(4.8, 6.0), jars=(-4.6, 5.0))


REGISTRY = {'river_camp': river_camp, 'mountain_pass': mountain_pass, 'sea_battle': sea_battle,
            'fortress_wall': fortress_wall, 'village_road': village_road}
