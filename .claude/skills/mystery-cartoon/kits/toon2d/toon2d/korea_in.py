"""Korean-history sets (Joseon / Three Kingdoms look): palace_hall, study_room, map_table, map_table_late, gate_court.

Same plane conventions as interiors.py: def name(mood) -> ([(layer, z, painter, opts), ...], meta).
Set canvas 1080 x 1920 (h 1920 = whole set). Light sources go into E lists and are re-drawn in lights=.

Map coordinates (map_table / map_table_late, plane z 1.0, flat top-down so these are frame centres):
  Liaodong (요동) 360,600   Gungnae-seong 600,650   Baekdu-san 690,600   Yalu mouth / Wihwado 450,735
  Pyongyang 505,860   Gaegyeong 520,990   Hanyang 545,1040   Sabi (Buyeo) 525,1170   Gyeongju 745,1245
  Busan 760,1340   Daeyaseong 640,1240   Tancheon/Tanhyeon 590,1150   Gibeolpo (Baengma-gang mouth) 488,1180
  Ganghwa-do 488,1015   Hansan-do 700,1385   Chilcheollyang 735,1380   Tsushima 800,1450
  Japan Kyushu 860,1560   Shandong tip 360,975   whole peninsula frame [600, 1060, 900]
"""
import math

import skia

from .paint import (fill, stroke, ink, shade, mix, path_poly, path_smooth, rrect, ellipse, lin_grad, rad_grad,
                    argb, rng, surface, draw_tex_quad, INK)
from . import textures as tx
from . import setkit as sk
from .light import MOODS, halo, pool, god_rays, window_slash
from .text import draw_text

NIGHT = ('night',)
RED = '#b8322c'
TEAL = '#2f8a78'
BLUE = '#2d5ba8'
GOLD = '#f2c640'


# =============================================================================== shared pieces
def dancheong(cv, x0, y0, x1, y1, seed=0, base=TEAL):
    """Painted bracket band: teal base, blue top stripe, red/white/gold rosettes, thin ink."""
    h = y1 - y0
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fill(base))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + h * 0.16), fill(BLUE))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y1 - h * 0.12, x1, y1), fill('#f0e6cc'))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y1 - h * 0.06, x1, y1), fill(RED))
    step = max(24.0, h * 1.25)
    cy = y0 + h * 0.5
    x = x0 + step / 2
    cv.save(); cv.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    while x < x1 + step:
        r = h * 0.3
        for k in range(8):
            a = k * math.pi / 4
            cv.drawCircle(x + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85, r * 0.42, fill('#f4ecd8'))
        cv.drawCircle(x, cy, r * 0.8, fill(RED))
        cv.drawCircle(x, cy, r * 0.45, fill('#e88a3a'))
        cv.drawCircle(x, cy, r * 0.22, fill(GOLD))
        cv.drawCircle(x, cy, r * 0.8, ink(1.6, 0.7))
        d = path_poly([(x + step / 2, cy - h * 0.28), (x + step / 2 + h * 0.18, cy), (x + step / 2, cy + h * 0.28),
                       (x + step / 2 - h * 0.18, cy)])
        cv.drawPath(d, fill('#3a78c8')); cv.drawPath(d, ink(1.4, 0.6))
        x += step
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), ink(3))


def pillar(cv, x, top, bot, w, col=RED, band=True):
    p = rrect(x - w / 2, top, w, bot - top, 4)
    cv.drawPath(p, fill(col))
    cv.drawRect(skia.Rect.MakeLTRB(x + w * 0.12, top, x + w / 2, bot), fill(shade(col, -0.22)))
    cv.drawRect(skia.Rect.MakeLTRB(x - w * 0.36, top, x - w * 0.22, bot), fill(shade(col, 0.22), 0.7))
    if band:
        dancheong(cv, x - w / 2, top, x + w / 2, top + w * 0.9, seed=int(x))
    cv.drawPath(p, ink(4))
    # stone plinth (chuchu-dol)
    cv.drawPath(rrect(x - w * 0.7, bot - 8, w * 1.4, w * 0.45, 6), fill('#b8b2a8'))
    cv.drawPath(rrect(x - w * 0.7, bot - 8, w * 1.4, w * 0.45, 6), ink(3.5))


def _eave(x0, x1, eave_y, lift, u):
    w = x1 - x0
    p0 = (x0 - w * 0.02, eave_y - lift); c = (x0 + w / 2, eave_y + lift * 0.55); p2 = (x1 + w * 0.02, eave_y - lift)
    a, b, d = (1 - u) ** 2, 2 * u * (1 - u), u * u
    return a * p0[0] + b * c[0] + d * p2[0], a * p0[1] + b * c[1] + d * p2[1]


def giwa_roof(cv, x0, x1, eave_y, ridge_y, col='#4e5060', lift=60, seed=0, rafters=True):
    """Curved Korean tiled roof: sagging eave with upturned corners, tile rows, ridge with end tiles."""
    w = x1 - x0
    rl, rr = x0 + w * 0.2, x1 - w * 0.2
    p = skia.Path()
    p.moveTo(rl, ridge_y)
    p.lineTo(rr, ridge_y)
    p.cubicTo(rr + w * 0.08, ridge_y + (eave_y - ridge_y) * 0.55, x1 - w * 0.05, eave_y - 10, x1 + w * 0.02, eave_y - lift)
    p.quadTo(x0 + w / 2, eave_y + lift * 0.55, x0 - w * 0.02, eave_y - lift)
    p.cubicTo(x0 + w * 0.05, eave_y - 10, rl - w * 0.08, ridge_y + (eave_y - ridge_y) * 0.55, rl, ridge_y)
    p.close()
    if rafters:
        # dancheong rafter ends under the eave
        sub = skia.Path()
        sub.moveTo(x0 + w * 0.02, eave_y - lift * 0.7)
        sub.quadTo(x0 + w / 2, eave_y + lift * 0.55 + 46, x1 - w * 0.02, eave_y - lift * 0.7)
        sub.quadTo(x0 + w / 2, eave_y + lift * 0.55 + 6, x0 + w * 0.02, eave_y - lift * 0.7)
        cv.drawPath(sub, fill(TEAL)); cv.drawPath(sub, ink(3))
        n = int(w / 26)
        for k in range(1, n):
            xx, yy = _eave(x0, x1, eave_y, lift, 0.04 + 0.92 * k / n)
            yy += 20
            cv.drawCircle(xx, yy, 7.5, fill('#e8a33a')); cv.drawCircle(xx, yy, 3.5, fill(RED))
    cv.drawPath(p, fill(col))
    cv.save(); cv.clipPath(p, doAntiAlias=True)
    n = int(w / 22)
    for k in range(n + 1):
        u = k / n
        bx = x0 - w * 0.02 + (w * 1.04) * u
        tx_ = rl + (rr - rl) * u
        cv.drawLine(tx_, ridge_y, bx, eave_y + lift, stroke(shade(col, 0.28), 5))
        cv.drawLine(tx_ + 6, ridge_y, bx + 8, eave_y + lift, stroke(shade(col, -0.3), 2.5))
    cv.drawRect(skia.Rect.MakeLTRB(x0 - 200, ridge_y, x1 + 200, ridge_y + (eave_y - ridge_y) * 0.3), fill('#ffffff', 0.08))
    cv.restore()
    cv.drawPath(p, ink(5))
    # eave end tiles (round)
    n = int(w / 30)
    for k in range(n + 1):
        xx, yy = _eave(x0, x1, eave_y, lift, k / n)
        cv.drawCircle(xx, yy - 2, 7, fill(shade(col, -0.25))); cv.drawCircle(xx, yy - 2, 7, ink(2))
    # ridge
    rh = max(16, (eave_y - ridge_y) * 0.12)
    rp = path_smooth([(rl - 30, ridge_y + rh * 0.4), (rl - 44, ridge_y - rh * 1.6), (rl - 6, ridge_y - rh),
                      (rr + 6, ridge_y - rh), (rr + 44, ridge_y - rh * 1.6), (rr + 30, ridge_y + rh * 0.4)])
    cv.drawPath(rp, fill(shade(col, -0.2))); cv.drawPath(rp, ink(4.5))
    cv.drawLine(rl, ridge_y - rh * 0.3, rr, ridge_y - rh * 0.3, stroke('#e8e2d8', 4, 0.8))
    # little guardian figures (japsang) on the hips
    for sgn in (-1, 1):
        for k in range(4):
            u = 0.25 + k * 0.13
            if sgn < 0:
                xx = rl + (x0 - rl) * u; yy = ridge_y + (eave_y - lift - ridge_y) * u
            else:
                xx = rr + (x1 - rr) * u; yy = ridge_y + (eave_y - lift - ridge_y) * u
            pass


def lantern(cv, x, y, s=1.0, E=None, cord=200):
    """Cheongsa-chorong: blue silk top, red body, gold frame."""
    cv.drawLine(x, y - cord * s, x, y - 50 * s, stroke('#2a2232', 3 * s))
    cv.drawPath(path_poly([(x - 30 * s, y - 50 * s), (x + 30 * s, y - 50 * s), (x + 20 * s, y - 64 * s), (x - 20 * s, y - 64 * s)]), fill(GOLD))
    top = rrect(x - 36 * s, y - 52 * s, 72 * s, 26 * s, 8 * s)
    cv.drawPath(top, fill('#2d4fa8')); cv.drawPath(top, ink(2.5 * s))
    body = rrect(x - 34 * s, y - 28 * s, 68 * s, 70 * s, 14 * s)
    cv.drawPath(body, fill('#d8402e'))
    for k in (-1, 0, 1):
        cv.drawLine(x + k * 17 * s, y - 26 * s, x + k * 17 * s, y + 40 * s, stroke('#8a2420', 2 * s))
    cv.drawPath(body, ink(2.8 * s))
    cv.drawPath(rrect(x - 30 * s, y + 40 * s, 60 * s, 12 * s, 4 * s), fill('#2d4fa8'))
    for k in range(-3, 4):
        cv.drawLine(x + k * 8 * s, y + 52 * s, x + k * 8 * s, y + 80 * s, stroke('#e8a33a', 2.2 * s))
    if E is not None:
        E.append(dict(kind='lamp', pos=(x, y + 6 * s), r=170 * s, lit=True, ground=None, body=(x, y, s)))


def lantern_glow(cv, e, night):
    x, y, s = e['body']
    if night:
        body = rrect(x - 34 * s, y - 28 * s, 68 * s, 70 * s, 14 * s)
        p = skia.Paint(AntiAlias=True)
        p.setShader(rad_grad((x, y + 6 * s), 60 * s, [argb('#fff0b0'), argb('#ff8a40'), argb('#c8302a')], [0, 0.5, 1]))
        cv.drawPath(body, p)
        cv.drawPath(body, ink(2.4 * s, 0.7))


def lattice(cv, x0, y0, x1, y1, step=26, col='#6a3a24', w=4.0, paper='#f3e8cc', frame=None, glow=None):
    """Changho lattice door: hanji paper + wooden grid (tti-sal), optional frame colour."""
    r = skia.Rect.MakeLTRB(x0, y0, x1, y1)
    if paper is not None:
        cv.drawRect(r, fill(paper))
        if glow:
            p = skia.Paint(AntiAlias=True)
            p.setShader(rad_grad(((x0 + x1) / 2, (y0 + y1) / 2), max(x1 - x0, y1 - y0) * 0.8,
                                 [argb(glow, 0.9), argb(glow, 0.0)]))
            cv.drawRect(r, p)
    xx = x0 + step
    while xx < x1 - 2:
        cv.drawLine(xx, y0, xx, y1, stroke(col, w * 0.7))
        xx += step
    yy = y0 + step * 1.6
    while yy < y1 - 2:
        cv.drawLine(x0, yy, x1, yy, stroke(col, w * 0.7))
        yy += step * 1.6
    cv.drawRect(r, stroke(frame or col, w * 2.4))
    cv.drawRect(r, ink(2.5))


def rank_stone(cv, x, base, s=1.0, col='#c8c2b4'):
    p = path_poly([(x - 22 * s, base), (x + 22 * s, base), (x + 18 * s, base - 60 * s), (x, base - 74 * s), (x - 18 * s, base - 60 * s)])
    cv.drawPath(path_poly([(x - 30 * s, base + 2), (x + 30 * s, base + 2), (x + 26 * s, base - 8 * s), (x - 26 * s, base - 8 * s)]), fill(shade(col, -0.2)))
    cv.drawPath(p, fill(col))
    cv.drawRect(skia.Rect.MakeLTRB(x + 4 * s, base - 62 * s, x + 18 * s, base), fill(shade(col, -0.18)))
    cv.drawLine(x - 4 * s, base - 52 * s, x - 4 * s, base - 16 * s, stroke(shade(col, -0.35), 3 * s))
    cv.drawPath(p, ink(2.6 * s))


def maru_floor(w, h, base='#c89a62', seed=3):
    return tx.wood_planks(w, h, plank=110, base=base, vertical=True, seed=seed, nails=False)


def coffer_ceiling(w, h):
    s = surface(w, h, '#2f6a5a')
    cv = s.getCanvas()
    step = 150
    for yy in range(0, h, step):
        for xx in range(0, w, step):
            cv.drawRect(skia.Rect.MakeXYWH(xx + 10, yy + 10, step - 20, step - 20), fill('#3a8a72'))
            cv.drawCircle(xx + step / 2, yy + step / 2, 42, fill(RED))
            for k in range(8):
                a = k * math.pi / 4
                cv.drawCircle(xx + step / 2 + math.cos(a) * 34, yy + step / 2 + math.sin(a) * 34, 14, fill('#f4ecd8'))
            cv.drawCircle(xx + step / 2, yy + step / 2, 22, fill(GOLD))
            cv.drawRect(skia.Rect.MakeXYWH(xx + 10, yy + 10, step - 20, step - 20), stroke('#c8342c', 5))
        cv.drawLine(0, yy, w, yy, stroke('#7a4a2a', 14))
    for xx in range(0, w, step):
        cv.drawLine(xx, 0, xx, h, stroke('#7a4a2a', 14))
    return s.makeImageSnapshot()


def room_box(cv, back, back_tex=None, left_tex=None, right_tex=None, floor_tex=None, ceil_tex=None):
    x0, y0, x1, y1 = back
    E_ = (-900, -1000, 1980, 3300)
    quads = dict(ceil=[(E_[0], E_[1]), (E_[2], E_[1]), (x1, y0), (x0, y0)],
                 lw=[(E_[0], E_[1]), (x0, y0), (x0, y1), (E_[0], E_[3])],
                 rw=[(x1, y0), (E_[2], E_[1]), (E_[2], E_[3]), (x1, y1)],
                 fl=[(x0, y1), (x1, y1), (E_[2], E_[3]), (E_[0], E_[3])])
    for k, t, sh in (('ceil', ceil_tex, 0.12), ('lw', left_tex, 0.1), ('rw', right_tex, 0.2), ('fl', floor_tex, 0.0)):
        if t is not None:
            draw_tex_quad(cv, t, quads[k])
        if sh:
            cv.drawPath(path_poly(quads[k]), fill('#4a2e66', sh))
        cv.drawPath(path_poly(quads[k]), ink(3, 0.6))
    if back_tex is not None:
        cv.drawImageRect(back_tex, skia.Rect.MakeLTRB(x0, y0, x1, y1))
    return quads


def ilwol_screen(cv, x0, y0, x1, y1):
    """Sun, moon and five peaks screen (painted, original rendering)."""
    w, h = x1 - x0, y1 - y0
    cv.drawPath(rrect(x0 - 22, y0 - 22, w + 44, h + 44, 6), fill('#7a2a22'))
    cv.drawPath(rrect(x0 - 22, y0 - 22, w + 44, h + 44, 6), ink(4))
    cv.save(); cv.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_grad((0, y0), (0, y1), [argb('#2a5fb8'), argb('#5a90d0'), argb('#9cc0e0')]))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), p)
    # sun (right) and moon (left)
    cv.drawCircle(x0 + w * 0.78, y0 + h * 0.16, w * 0.075, fill('#d8302a')); cv.drawCircle(x0 + w * 0.78, y0 + h * 0.16, w * 0.075, ink(2.5))
    cv.drawCircle(x0 + w * 0.22, y0 + h * 0.16, w * 0.075, fill('#f4f2ea')); cv.drawCircle(x0 + w * 0.22, y0 + h * 0.16, w * 0.075, ink(2.5))
    # five peaks: centre tallest
    peaks = [(0.5, 0.26, 0.2), (0.3, 0.38, 0.17), (0.7, 0.38, 0.17), (0.1, 0.5, 0.15), (0.9, 0.5, 0.15)]
    for (u, top, hw) in sorted(peaks, key=lambda q: q[1]):
        px = x0 + w * u
        pk = path_smooth([(px - w * hw * 1.4, y0 + h * 0.86), (px - w * hw * 0.6, y0 + h * (top + 0.12)), (px, y0 + h * top),
                          (px + w * hw * 0.6, y0 + h * (top + 0.12)), (px + w * hw * 1.4, y0 + h * 0.86)])
        cv.drawPath(pk, fill('#2f7a6a'))
        cv.save(); cv.clipPath(pk, doAntiAlias=True)
        for k in range(6):
            yy = y0 + h * (top + 0.06 + k * 0.08)
            cv.drawLine(px - w * 0.3, yy + 30, px + w * 0.3, yy - 10, stroke('#3fa08a', 6, 0.6))
        cv.drawPath(ellipse(px - w * hw * 0.25, y0 + h * (top + 0.2), w * hw * 0.25, h * 0.2), fill('#1f5a5a', 0.6))
        cv.restore()
        cv.drawPath(pk, ink(3))
    # waterfalls
    for u in (0.4, 0.6):
        xx = x0 + w * u
        cv.drawRect(skia.Rect.MakeLTRB(xx - 6, y0 + h * 0.48, xx + 6, y0 + h * 0.8), fill('#f2f4f8'))
        for k in range(5):
            cv.drawLine(xx - 3, y0 + h * (0.5 + k * 0.06), xx - 3, y0 + h * (0.53 + k * 0.06), stroke('#9cc0e0', 2))
    # red pines on the sides
    for u, sgn in ((0.04, 1), (0.96, -1)):
        bx = x0 + w * u
        tr = path_poly([(bx - 9, y0 + h * 0.86), (bx + 9, y0 + h * 0.86), (bx + 6 + sgn * 18, y0 + h * 0.35), (bx - 6 + sgn * 18, y0 + h * 0.35)])
        cv.drawPath(tr, fill('#b8462a')); cv.drawPath(tr, ink(2.5))
        for k in range(4):
            cx_ = bx + sgn * (18 + k * 10); cy_ = y0 + h * (0.36 + k * 0.1)
            cv.drawPath(ellipse(cx_ + sgn * 24, cy_, 44, 16), fill('#2a6a3a')); cv.drawPath(ellipse(cx_ + sgn * 24, cy_, 44, 16), ink(2.2))
    # waves
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0 + h * 0.8, x1, y1), fill('#2a4f9a'))
    for row in range(3):
        yy = y0 + h * (0.84 + row * 0.06)
        xx = x0 - 30 + (row % 2) * 30
        while xx < x1 + 40:
            wv = skia.Path(); wv.addArc(skia.Rect.MakeLTRB(xx - 30, yy - 22, xx + 30, yy + 22), 180, 180)
            cv.drawPath(wv, stroke('#f2f4f8', 5))
            cv.drawPath(wv, stroke('#1a2f6a', 1.5))
            xx += 60
    cv.restore()
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), ink(3.5))


# =============================================================================== PALACE HALL
def palace_hall(mood):
    night = mood in NIGHT
    E = []
    back = (130, 160, 950, 1260)

    def hall(cv):
        wall = surface(820, 1100, '#c8b48a')
        wc = wall.getCanvas()
        # back wall: red posts + lattice panels on the sides of the screen
        for x_ in (0, 160, 660, 820):
            wc.drawRect(skia.Rect.MakeXYWH(x_ - 14, 0, 28, 1100), fill(RED))
        lattice(wc, 20, 320, 150, 980, step=22)
        lattice(wc, 670, 320, 800, 980, step=22)
        dancheong(wc, 0, 0, 820, 90)
        right_w = tx.wood_planks(1200, 1600, plank=140, base='#a8463a', vertical=True, seed=8, nails=False)
        room_box(cv, back, back_tex=wall.makeImageSnapshot(), left_tex=right_w, right_tex=right_w,
                 floor_tex=maru_floor(1400, 1400, '#c8945a'), ceil_tex=coffer_ceiling(1500, 1200))
        # side-wall lattice doors (perspective via draw_in_quad-like strips)
        for sgn in (-1, 1):
            for k in range(3):
                xa = 130 - 130 * k * 0.55 if sgn < 0 else 950 + 130 * k * 0.55
                xb = 130 - 130 * (k + 0.8) * 0.55 if sgn < 0 else 950 + 130 * (k + 0.8) * 0.55
                ya_t = 420 - (abs(xa - 540) - 410) * 0.9
                yb_t = 420 - (abs(xb - 540) - 410) * 0.9
                ya_b = 1180 + (abs(xa - 540) - 410) * 1.6
                yb_b = 1180 + (abs(xb - 540) - 410) * 1.6
                q = [(xa, ya_t), (xb, yb_t), (xb, yb_b), (xa, ya_b)]
                cv.drawPath(path_poly(q), fill('#efe2c2'))
                for j in range(1, 6):
                    u = j / 6
                    cv.drawLine(xa + (xb - xa) * u, ya_t + (yb_t - ya_t) * u, xa + (xb - xa) * u, ya_b + (yb_b - ya_b) * u, stroke('#6a3a24', 3))
                for j in range(1, 12):
                    u = j / 12
                    cv.drawLine(xa, ya_t + (ya_b - ya_t) * u, xb, yb_t + (yb_b - yb_t) * u, stroke('#6a3a24', 3))
                cv.drawPath(path_poly(q), stroke(RED, 8)); cv.drawPath(path_poly(q), ink(3))
                if night:
                    E.append(dict(kind='quadglow', quad=q))
        # screen behind the throne
        ilwol_screen(cv, 300, 470, 780, 1080)
        # canopy (dangga) above the throne
        giwa_roof(cv, 330, 750, 400, 300, col='#3a7a6a', lift=36, rafters=True)
        for x_ in (360, 720):
            cv.drawLine(x_, 410, x_, 470, stroke(GOLD, 6))
        cv.drawPath(path_poly([(350, 410), (730, 410), (700, 450), (380, 450)]), fill(RED))
        for k in range(12):
            cv.drawCircle(380 + k * 29, 452, 6, fill(GOLD))
        cv.drawPath(path_poly([(350, 410), (730, 410), (700, 450), (380, 450)]), ink(3))
        # raised dais with stairs
        dais = path_poly([(260, 1110), (820, 1110), (880, 1240), (200, 1240)])
        cv.drawPath(dais, fill('#8a3a2a')); cv.drawPath(dais, ink(4))
        for k in range(6):
            cv.drawLine(240 + k * 120, 1150, 240 + k * 120, 1230, stroke(GOLD, 3, 0.6))
        dancheong(cv, 220, 1205, 860, 1240)
        for k in range(3):
            st = rrect(430 - k * 20, 1240 + k * 22, 220 + k * 40, 22, 3)
            cv.drawPath(st, fill(mix('#c8b8a0', '#8a6a5a', k * 0.2))); cv.drawPath(st, ink(3))
        # throne (eojwa): red lacquer chair with gold dragon-ish curls (abstract)
        back_p = path_poly([(450, 1150), (630, 1150), (640, 940), (600, 900), (480, 900), (440, 940)])
        cv.drawPath(back_p, fill('#c8342c')); cv.drawPath(back_p, ink(4.5))
        cv.drawPath(rrect(470, 930, 140, 150, 10), fill('#9a2420'))
        for k in range(3):
            cv.drawCircle(540, 970 + k * 40, 12, stroke(GOLD, 4))
        cv.drawPath(rrect(470, 930, 140, 150, 10), stroke(GOLD, 5))
        for px in (440, 640):
            cv.drawPath(rrect(px - 18, 1040, 36, 80, 8), fill('#b02e28')); cv.drawPath(rrect(px - 18, 1040, 36, 80, 8), ink(3.5))
            cv.drawCircle(px, 1036, 16, fill(GOLD)); cv.drawCircle(px, 1036, 16, ink(3))
        cv.drawPath(rrect(450, 1100, 180, 44, 8), fill('#d8402e')); cv.drawPath(rrect(450, 1100, 180, 44, 8), ink(4))
        cv.drawPath(rrect(470, 1092, 140, 18, 6), fill(GOLD)); cv.drawPath(rrect(470, 1092, 140, 18, 6), ink(2.5))
        # big red pillars
        for x_ in (205, 875):
            pillar(cv, x_, 160, 1290, 84)
        # hanging lanterns inside
        for x_, y_ in ((290, 620), (790, 620)):
            lantern(cv, x_, y_, 1.2, E, cord=420)
        # bronze incense burners on the floor
        for x_ in (330, 750):
            cv.drawPath(path_poly([(x_ - 40, 1300), (x_ + 40, 1300), (x_ + 30, 1360), (x_ - 30, 1360)]), fill('#7a6a4a'))
            cv.drawPath(path_poly([(x_ - 40, 1300), (x_ + 40, 1300), (x_ + 30, 1360), (x_ - 30, 1360)]), ink(3.5))
            for sx in (-24, 0, 24):
                cv.drawLine(x_ + sx, 1360, x_ + sx * 1.3, 1392, stroke('#5a4a3a', 7))
            cv.drawPath(ellipse(x_, 1296, 44, 10), fill('#9a8a5a')); cv.drawPath(ellipse(x_, 1296, 44, 10), ink(3))
            cv.drawPath(path_smooth([(x_, 1290), (x_ - 10, 1240), (x_ + 8, 1200), (x_ - 4, 1150)], close=False), stroke('#e8e0f0', 4, 0.4))
        # floor sheen strip toward camera
        cv.drawPath(path_poly([(470, 1260), (610, 1260), (760, 2400), (320, 2400)]), fill('#ffffff', 0.07))

    def near(cv):
        for x_ in (-60, 1140):
            pillar(cv, x_, -400, 2700, 230, band=False)
        dancheong(cv, -300, -260, 1400, -120)
        lantern(cv, 940, 60, 1.7, E, cord=500)

    def lights_hall(cv, mm):
        if not night:
            god_rays(cv, (900, 200), 120, 30, 1500, n=6, col=(255, 236, 200), a=0.12)
        for e in E:
            if e['kind'] == 'quadglow':
                cv.drawPath(path_poly(e['quad']), fill(mm['key'], 0.38))
        lit = [e for e in E if e['kind'] == 'lamp' and e['pos'][1] > 200]
        for e in lit:
            lantern_glow(cv, e, night)
        sk.draw_emitters(cv, lit, mm, night)

    def lights_near(cv, mm):
        lit = [e for e in E if e['kind'] == 'lamp' and e['pos'][1] <= 200]
        for e in lit:
            lantern_glow(cv, e, night)
        sk.draw_emitters(cv, lit, mm, night)

    return [
        ('hall', 1.5, hall, dict(lights=lights_hall)),
        ('near', 0.62, near, dict(blur=9, lights=lights_near)),
    ], dict(ground_y=1500, throne=(540, 1100), screen=(540, 780))


# =============================================================================== STUDY ROOM
def study_room(mood):
    night = mood in NIGHT
    E = []
    back = (120, 260, 960, 1230)
    doors = [(150 + k * 200, 380, 330 + k * 200, 1150) for k in range(4)]

    def room(cv):
        wall = surface(840, 970, '#e2d2ae')
        wc = wall.getCanvas()
        wc.drawImage(tx.wallpaper(840, 970, base='#e6d6b2', motif='#d4bf94', stripe='#ddcba4', step=80), 0, 0)
        jangpan = surface(1200, 1200, '#d8a850')
        jc = jangpan.getCanvas()
        r = rng(5)
        for yy in range(0, 1200, 150):
            for xx in range(0, 1200, 150):
                jc.drawRect(skia.Rect.MakeXYWH(xx, yy, 150, 150), fill(mix('#e0b25a', '#c8923e', r.random() * 0.5)))
                jc.drawRect(skia.Rect.MakeXYWH(xx, yy, 150, 150), stroke('#a87430', 3))
        side = tx.wood_planks(1200, 1600, plank=130, base='#9a6a3e', vertical=True, seed=11, nails=False)
        room_box(cv, back, back_tex=wall.makeImageSnapshot(), left_tex=side, right_tex=side,
                 floor_tex=jangpan.makeImageSnapshot(), ceil_tex=tx.wood_planks(1400, 1100, plank=90, base='#b08050', seed=12, nails=False))
        # rafters on the ceiling
        for k in range(7):
            x_ = 160 + k * 127
            cv.drawLine(x_, 260, -900 + (x_ + 900) * 1.0 + (x_ - 540) * 2.2, -1000, stroke('#6a4228', 18))
        # back wall posts + lattice doors (changhoji)
        for k, (a, b, c, d) in enumerate(doors):
            lattice(cv, a, b, c, d, step=24, col='#7a4a2a', paper='#f6ecd2')
        for x_ in (130, 950):
            cv.drawRect(skia.Rect.MakeLTRB(x_ - 16, 260, x_ + 16, 1230), fill('#6a4228')); cv.drawRect(skia.Rect.MakeLTRB(x_ - 16, 260, x_ + 16, 1230), ink(3))
        cv.drawRect(skia.Rect.MakeLTRB(120, 340, 960, 370), fill('#6a4228')); cv.drawRect(skia.Rect.MakeLTRB(120, 1150, 960, 1180), fill('#6a4228'))
        # hanging calligraphy scroll between doors
        cv.drawPath(rrect(512, 300, 56, 30, 4), fill('#5a3a24'))
        # bookshelf (chaekjang) on the left
        cv.drawPath(path_poly([(-200, 380), (120, 450), (120, 1230), (-200, 1460)]), fill('#7a4a2a'))
        for k in range(5):
            y_a = 470 + k * 150; y_b = 400 + k * 200
            cv.drawPath(path_poly([(-200, y_b), (120, y_a), (120, y_a + 14), (-200, y_b + 20)]), fill('#5a3220'))
            rr_ = rng(20 + k)
            xx = -180
            while xx < 100:
                bw = rr_.uniform(26, 44)
                t_ = (xx + 200) / 320
                ya = y_b + (y_a - y_b) * t_
                col = rr_.choice(['#2d4f8a', '#3a5a9a', '#c8b88a', '#8a2a2a', '#2f6a5a'])
                bh = 110 + 30 * t_
                cv.drawPath(path_poly([(xx, ya), (xx + bw, ya + 4), (xx + bw, ya - bh), (xx, ya - bh - 4)]), fill(col))
                cv.drawPath(path_poly([(xx, ya), (xx + bw, ya + 4), (xx + bw, ya - bh), (xx, ya - bh - 4)]), ink(2.5))
                cv.drawLine(xx + 6, ya - 10, xx + 6, ya - bh + 10, stroke('#f2ece0', 2))
                xx += bw + 4
        # folding screen (byeongpung): freestanding, zig-zag panels on the floor at the right
        for k in range(4):
            xa = 720 + k * 60; xb = xa + 60
            dy = 0 if k % 2 == 0 else 18
            q = [(xa, 860 + dy), (xb, 878 - dy), (xb, 1262 - dy), (xa, 1244 + dy)]
            cv.drawPath(path_poly(q), fill('#f0e4c4' if k % 2 == 0 else '#dccca4'))
            rr_ = rng(40 + k)
            for j in range(3):
                xx = xa + 30 + rr_.uniform(-6, 6); yy = 900 + j * 110
                cv.drawLine(xx, yy, xx + rr_.uniform(-6, 6), yy + rr_.uniform(50, 80), stroke('#2a2228', rr_.uniform(5, 8)))
                cv.drawLine(xx - 14, yy + 20, xx + 16, yy + 26, stroke('#2a2228', 4.5))
            cv.drawPath(path_poly(q), stroke('#5a2a2a', 8)); cv.drawPath(path_poly(q), ink(3))
        # low writing desk (seoan) with brush, inkstone, scroll, books
        top = path_poly([(270, 1290), (650, 1290), (690, 1340), (230, 1340)])
        cv.drawPath(path_poly([(240, 1340), (680, 1340), (680, 1362), (240, 1362)]), fill('#5a3220'))
        for x_ in (255, 665):
            cv.drawPath(rrect(x_ - 10, 1360, 20, 90, 4), fill('#5a3220')); cv.drawPath(rrect(x_ - 10, 1360, 20, 90, 4), ink(3))
            cv.drawPath(path_smooth([(x_ - 18, 1450), (x_, 1440), (x_ + 18, 1450)], close=False), ink(5))
        cv.drawPath(top, fill('#8a5a34')); cv.drawPath(top, ink(4))
        # unrolled paper with brush lines
        cv.drawPath(path_poly([(340, 1298), (520, 1298), (530, 1330), (330, 1330)]), fill('#f8f2e2'))
        for k in range(6):
            cv.drawLine(500 - k * 26, 1303, 498 - k * 26, 1326, stroke('#2a2228', 3.2))
        cv.drawPath(path_poly([(340, 1298), (520, 1298), (530, 1330), (330, 1330)]), ink(2))
        cv.drawPath(rrect(560, 1300, 60, 26, 6), fill('#2a2a30')); cv.drawPath(ellipse(578, 1310, 14, 6), fill('#0e0e14'))
        cv.drawLine(300, 1320, 380, 1296, stroke('#a07040', 5)); cv.drawLine(380, 1296, 396, 1292, stroke('#1a1418', 7))
        for k in range(4):
            cv.drawPath(rrect(250, 1252 - k * 14, 70, 14, 2), fill('#2d4f8a' if k % 2 else '#c8b88a')); cv.drawPath(rrect(250, 1252 - k * 14, 70, 14, 2), ink(2))
        cv.drawPath(rrect(250, 1266, 70, 24, 2), fill('#2d4f8a')); cv.drawPath(rrect(250, 1266, 70, 24, 2), ink(2))
        # brush holder
        cv.drawPath(rrect(625, 1240, 34, 52, 6), fill('#e8e4d8')); cv.drawPath(rrect(625, 1240, 34, 52, 6), ink(2.5))
        for k in range(3):
            cv.drawLine(632 + k * 9, 1244, 626 + k * 12, 1196, stroke('#a07040', 4))
        # cushion (boryo)
        cv.drawPath(path_poly([(360, 1440), (560, 1440), (600, 1500), (320, 1500)]), fill('#8a2a3a'))
        cv.drawPath(path_poly([(360, 1440), (560, 1440), (600, 1500), (320, 1500)]), ink(3))
        cv.drawLine(340, 1470, 580, 1470, stroke(GOLD, 3, 0.7))
        # oil lamp stand (deungjan)
        lx, ly = 690, 1020
        cv.drawLine(lx, ly + 20, lx, 1360, stroke('#5a3a24', 10)); cv.drawLine(lx, ly + 20, lx, 1360, ink(2))
        cv.drawPath(ellipse(lx, 1366, 48, 12), fill('#5a3a24')); cv.drawPath(ellipse(lx, 1366, 48, 12), ink(3))
        cv.drawPath(ellipse(lx, ly + 20, 36, 9), fill('#7a5a3a')); cv.drawPath(ellipse(lx, ly + 20, 36, 9), ink(3))
        cv.drawPath(path_smooth([(lx - 7, ly + 12), (lx, ly - 22), (lx + 7, ly + 12)]), fill('#f8b040'))
        E.append(dict(kind='lamp', pos=(lx, ly - 2), r=300, lit=True, ground=1366))
        # moon/sun slash on the floor through the doors
        E.append(dict(kind='slash'))

    def near(cv):
        # blurred book stack and a hanging lattice edge
        for k in range(5):
            cv.drawPath(rrect(-80 + k * 6, 2050 - k * 60, 380, 60, 6), fill('#2d4f8a' if k % 2 else '#c8b88a'))
            cv.drawPath(rrect(-80 + k * 6, 2050 - k * 60, 380, 60, 6), ink(5))
        cv.drawRect(skia.Rect.MakeLTRB(1040, -300, 1300, 2600), fill('#6a4228'))
        lattice(cv, 1070, -300, 1400, 2600, step=60, col='#5a3220', w=8, paper='#e8d8b0')

    def lights_room(cv, mm):
        for (a, b, c, d) in doors:
            if night:
                p = skia.Paint(AntiAlias=True)
                p.setShader(lin_grad((0, b), (0, d), [argb((150, 170, 255), 0.55), argb((110, 130, 230), 0.4)]))
                cv.drawRect(skia.Rect.MakeLTRB(a, b, c, d), p)
                lattice(cv, a, b, c, d, step=24, col='#3a2a3a', paper=None)
            else:
                cv.drawRect(skia.Rect.MakeLTRB(a, b, c, d), fill(mm['key'], 0.15))
                lattice(cv, a, b, c, d, step=24, col='#7a4a2a', paper=None)
        if not night:
            window_slash(cv, [(300, 1230), (760, 1230), (900, 1700), (160, 1700)], col=mm['key'], a=0.22)
        sk.draw_emitters(cv, [e for e in E if e['kind'] == 'lamp'], mm, night)

    def lights_near(cv, mm):
        if night:
            cv.drawRect(skia.Rect.MakeLTRB(1070, -300, 1400, 2600), fill((120, 140, 240), 0.25))

    return [
        ('room', 1.5, room, dict(lights=lights_room)),
        ('near', 0.6, near, dict(blur=11, lights=lights_near)),
    ], dict(ground_y=1500, desk=(460, 1310), lamp=(690, 1020), screen=(840, 1060))


# =============================================================================== MAP TABLE
LAND = [(40, 120), (1040, 120), (1040, 520), (940, 560), (900, 620), (820, 680), (760, 760), (720, 880), (770, 1000),
        (795, 1120), (790, 1210), (762, 1335), (700, 1385), (640, 1400), (580, 1395), (520, 1362), (482, 1262),
        (500, 1150), (470, 1062), (482, 980), (430, 900), (470, 820), (440, 740), (400, 700), (330, 760), (290, 805),
        (320, 720), (330, 655), (250, 625), (180, 650), (200, 760), (260, 860), (230, 930), (365, 965), (330, 1010),
        (200, 1040), (150, 1100), (170, 1250), (140, 1400), (100, 1550), (40, 1620)]
CITIES = dict(Pyongyang=(505, 860), Gaegyeong=(520, 990), Hanyang=(545, 1040), Sabi=(525, 1170), Gyeongju=(745, 1245),
              Busan=(760, 1340), Liaodong=(360, 600), Gungnae=(600, 650), Wihwado=(450, 735))


def _map_paper(cv, labels, seed=1):
    r = rng(seed)
    # paper with torn edge
    pts = []
    for k in range(40):
        pts.append((60 + k * 24, 150 + r.uniform(-8, 8)))
    for k in range(64):
        pts.append((1020 + r.uniform(-8, 8), 150 + k * 25))
    for k in range(40):
        pts.append((1020 - k * 24, 1750 + r.uniform(-8, 8)))
    for k in range(64):
        pts.append((60 + r.uniform(-8, 8), 1750 - k * 25))
    paper = path_poly(pts)
    cv.drawPath(paper, fill('#2a1a14', 0.35)) if False else None
    sh = skia.Paint(AntiAlias=True); sh.setColor(argb('#2a1a14', 0.45)); sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    cv.save(); cv.translate(14, 18); cv.drawPath(paper, sh); cv.restore()
    cv.drawPath(paper, fill('#9cc8b8'))
    cv.save(); cv.clipPath(paper, doAntiAlias=True)
    # sea wave hatching
    for yy in range(160, 1760, 34):
        for xx in range(40, 1060, 70):
            ox = (yy // 34 % 2) * 35
            wv = skia.Path(); wv.addArc(skia.Rect.MakeLTRB(xx + ox - 14, yy - 7, xx + ox + 14, yy + 7), 200, 140)
            cv.drawPath(wv, stroke('#6aa092', 2, 0.6))
    land = path_smooth(LAND, tension=0.35)
    cv.drawPath(land, fill('#e8d6a8'))
    cv.save(); cv.clipPath(land, doAntiAlias=True)
    # mountains (little ink peaks) along the spine and in Manchuria
    for (mx, my) in [(700, 820), (730, 900), (740, 980), (720, 1080), (690, 1160), (640, 1290), (600, 760), (650, 700),
                     (540, 520), (700, 480), (820, 420), (420, 420), (260, 380), (900, 300), (600, 300)]:
        for k in range(3):
            px = mx + (k - 1) * 22
            pk = path_poly([(px - 18, my + 12), (px, my - 16 - (k == 1) * 8), (px + 18, my + 12)])
            cv.drawPath(pk, fill('#b8c48a')); cv.drawPath(pk, stroke('#5a4a3a', 2.2))
    cv.restore()
    cv.drawPath(land, stroke('#5a3a2a', 4))
    # coast shading line
    cv.drawPath(land, stroke('#4a8a7a', 10, 0.25))
    # islands: Jeju, Tsushima, Japan (Kyushu + Honshu), Ganghwa
    for (cx_, cy_, rx, ry) in [(570, 1490, 34, 16), (800, 1450, 10, 24), (488, 1015, 10, 8)]:
        cv.drawPath(ellipse(cx_, cy_, rx, ry), fill('#e8d6a8')); cv.drawPath(ellipse(cx_, cy_, rx, ry), stroke('#5a3a2a', 3))
    jp = path_smooth([(840, 1490), (900, 1470), (920, 1530), (900, 1610), (850, 1640), (820, 1590)], tension=0.4)
    hon = path_smooth([(900, 1440), (960, 1380), (1040, 1290), (1060, 1250), (1060, 1420), (1000, 1450), (930, 1470)], tension=0.4)
    for p in (jp, hon):
        cv.drawPath(p, fill('#e8d6a8')); cv.drawPath(p, stroke('#5a3a2a', 3.5))
    # rivers: Yalu (to Baekdu) and Tumen, Taedong, Han, Geum, Nakdong
    rivers = [[(440, 740), (500, 700), (560, 690), (620, 640), (690, 600)], [(690, 600), (780, 610), (900, 620)],
              [(470, 870), (530, 850), (590, 830)], [(482, 1030), (560, 1045), (640, 1040)],
              [(488, 1180), (560, 1150), (610, 1110)], [(740, 1340), (720, 1260), (700, 1170)]]
    for k, rv in enumerate(rivers):
        cv.drawPath(path_smooth(rv, close=False), stroke('#3a7aa8', 7 if k == 0 else 5))
    # Baekdu-san
    cv.drawPath(path_poly([(660, 615), (690, 570), (720, 615)]), fill('#f4f2ea')); cv.drawPath(path_poly([(660, 615), (690, 570), (720, 615)]), stroke('#5a4a3a', 3))
    # cities (red seals)
    for name, (x_, y_) in CITIES.items():
        cv.drawCircle(x_, y_, 9, fill('#c8302a')); cv.drawCircle(x_, y_, 9, stroke('#5a1a14', 2.5))
    for (txt, x_, y_, sz) in labels:
        draw_text(cv, txt, x_, y_, sz, col='#3a2418', outline='#f2e6c4', ow=6)
    # compass rose + folds + stains
    cx_, cy_ = 940, 1660
    for k in range(4):
        a = k * math.pi / 2
        cv.drawPath(path_poly([(cx_, cy_), (cx_ + math.cos(a - 0.3) * 18, cy_ + math.sin(a - 0.3) * 18), (cx_ + math.cos(a) * 60, cy_ + math.sin(a) * 60)]), fill('#5a3a2a'))
    cv.drawCircle(cx_, cy_, 26, stroke('#5a3a2a', 3))
    for yy in (560, 1160):
        cv.drawLine(40, yy, 1060, yy, stroke('#8a7050', 3, 0.35))
    cv.drawLine(540, 140, 540, 1780, stroke('#8a7050', 3, 0.3))
    for k in range(6):
        cv.drawCircle(r.uniform(80, 1000), r.uniform(180, 1720), r.uniform(30, 90), fill('#a07a40', 0.07))
    p = skia.Paint(AntiAlias=True)
    p.setShader(rad_grad((540, 950), 1000, [argb('#000000', 0), argb('#5a3a14', 0.35)], [0.6, 1]))
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, 1100, 1900), p)
    cv.restore()
    cv.drawPath(paper, stroke('#8a6a40', 3))


def _marker(cv, x, y, col, s=1.0):
    cv.drawPath(ellipse(x + 6, y + 4, 22 * s, 8 * s), fill('#1a1014', 0.35))
    cv.drawPath(rrect(x - 14 * s, y - 16 * s, 28 * s, 20 * s, 5 * s), fill('#8a5a30')); cv.drawPath(rrect(x - 14 * s, y - 16 * s, 28 * s, 20 * s, 5 * s), ink(2.5))
    cv.drawLine(x, y - 16 * s, x, y - 80 * s, stroke('#5a3a24', 4 * s))
    fl = path_poly([(x, y - 80 * s), (x + 42 * s, y - 70 * s), (x, y - 56 * s)])
    cv.drawPath(fl, fill(col)); cv.drawPath(fl, ink(2.5))


def _map_set(mood, labels, markers):
    night = mood in NIGHT
    E = []

    def table(cv):
        cv.drawImage(tx.wood_planks(1900, 3100, plank=180, base='#7a4a2a', vertical=False, seed=21, nails=False), -420, -560)
        _map_paper(cv, labels)
        for (x_, y_, col) in markers:
            _marker(cv, x_, y_, col)
        # paperweights at corners
        for (x_, y_) in ((70, 170), (1010, 1740)):
            cv.drawPath(rrect(x_ - 50, y_ - 20, 100, 40, 10), fill('#3a3a44')); cv.drawPath(rrect(x_ - 50, y_ - 20, 100, 40, 10), ink(3))
        # candle at top right (practical)
        cx_, cy_ = 980, 80
        cv.drawPath(ellipse(cx_, cy_ + 60, 60, 18), fill('#8a6a3a')); cv.drawPath(ellipse(cx_, cy_ + 60, 60, 18), ink(3))
        cv.drawPath(rrect(cx_ - 18, cy_ - 40, 36, 100, 6), fill('#f4ecd8')); cv.drawPath(rrect(cx_ - 18, cy_ - 40, 36, 100, 6), ink(3))
        cv.drawPath(path_smooth([(cx_ - 8, cy_ - 40), (cx_, cy_ - 80), (cx_ + 8, cy_ - 40)]), fill('#f8b040'))
        E.append(dict(kind='lamp', pos=(cx_, cy_ - 55), r=420, lit=True, ground=None))

    def near(cv):
        # blurred brush and inkstone in the bottom-left foreground
        cv.drawLine(-200, 2250, 420, 1900, stroke('#a07040', 34)); cv.drawLine(-200, 2250, 420, 1900, ink(4))
        cv.drawPath(path_smooth([(420, 1885), (500, 1850), (520, 1880), (440, 1920)]), fill('#1a1418'))
        cv.drawPath(rrect(760, 2050, 320, 160, 20), fill('#2a2a30')); cv.drawPath(rrect(760, 2050, 320, 160, 20), ink(6))
        cv.drawPath(ellipse(900, 2120, 90, 40), fill('#0e0e14'))

    def lights(cv, mm):
        sk.draw_emitters(cv, E, mm, night)
        if night:
            pool(cv, 900, 300, 600, 400, mm['key'], 0.25)

    return [
        ('table', 1.0, table, dict(lights=lights)),
        ('near', 0.6, near, dict(blur=12)),
    ], dict(cities=dict(CITIES), peninsula=(600, 1060), yalu=(450, 735), busan=(760, 1340))


def map_table(mood):
    """Three Kingdoms era (7th c.): 고구려 / 백제 / 신라 / 당 / 왜."""
    labels = [('고구려', 600, 500, 64), ('요동', 330, 560, 44), ('압록강', 560, 740, 34), ('백제', 470, 1230, 52),
              ('신라', 710, 1200, 52), ('당', 150, 1180, 72), ('왜', 950, 1560, 56), ('평양', 505, 900, 28),
              ('사비', 560, 1205, 26), ('서라벌', 745, 1285, 26), ('황해', 300, 1300, 40), ('동해', 900, 900, 40)]
    markers = [(600, 1150, '#2d5ba8'), (690, 1090, '#d8a020'), (300, 1200, '#c8302a')]
    return _map_set(mood, labels, markers)


def map_table_late(mood):
    """Goryeo/Joseon era: 요동 / 명 / 조선 / 일본, Hanyang, Busan."""
    labels = [('요동', 360, 560, 56), ('만주', 700, 360, 48), ('압록강', 560, 740, 34), ('위화도', 400, 790, 26),
              ('명', 150, 1180, 80), ('조선', 640, 1110, 60), ('한양', 600, 1050, 28), ('개경', 470, 980, 24), ('부산', 760, 1385, 28),
              ('일본', 960, 1560, 56), ('대마도', 840, 1475, 22), ('황해', 300, 1300, 40), ('동해', 900, 900, 40)]
    markers = [(470, 720, '#c8302a'), (350, 640, '#d8a020'), (820, 1500, '#2a2a30')]
    return _map_set(mood, labels, markers)


# =============================================================================== GATE COURT
def gate_court(mood):
    night = mood in NIGHT
    m = MOODS[mood]
    E = []
    hy = 1080   # base of the hall terrace

    def sky(cv):
        sk.sky(cv, m, seed=7, clouds=7, cloud_band=(-400, 520), cloud_scale=1.2,
               moon=(820, 180, 56) if night else None, stars=150 if night else 0,
               sun=(200, 160, 60) if mood == 'day' else ((880, 700, 90) if mood in ('sunset', 'golden') else None))

    def mountain(cv):
        sk.hills(cv, 820, -500, 1600, 260, mix('#4a6a5a', m['fog'], 0.35), seed=3, wav=420)
        sk.hills(cv, 900, -500, 1600, 120, mix('#5a7a5a', m['fog'], 0.2), seed=9, wav=220)
        r = rng(2)
        for k in range(26):
            sk.foliage(cv, r.uniform(-400, 1500), r.uniform(840, 920), r.uniform(30, 60), col=mix('#3a6a3a', m['fog'], 0.2), seed=k, lumps=5)

    def hall(cv):
        # side corridors (haenggak) left and right
        for (a, b) in ((-420, 230), (850, 1500)):
            cv.drawRect(skia.Rect.MakeLTRB(a, 900, b, hy), fill('#e8dcc4'))
            for x_ in range(int(a), int(b), 70):
                cv.drawRect(skia.Rect.MakeLTRB(x_, 900, x_ + 12, hy), fill(RED))
            cv.drawRect(skia.Rect.MakeLTRB(a, 1040, b, hy), fill('#9a948a'))
            giwa_roof(cv, a, b, 900, 820, lift=10, rafters=False)
        # stone terrace (woldae) with balustrade and stairs
        ter = path_poly([(170, 1000), (910, 1000), (960, hy + 30), (120, hy + 30)])
        cv.drawImage(tx.stone_blocks(840, 110, bw=120, bh=55, base='#c4bcae', seed=4), 120, 1000)
        cv.drawPath(ter, ink(4))
        for x_ in range(150, 940, 46):
            cv.drawLine(x_, 990, x_, 1004, stroke('#d8d0c4', 9))
        cv.drawLine(140, 988, 940, 988, stroke('#d8d0c4', 8)); cv.drawLine(140, 988, 940, 988, ink(2))
        st = path_poly([(470, 1000), (610, 1000), (640, hy + 30), (440, hy + 30)])
        cv.drawPath(st, fill('#d8d0c2'))
        for k in range(6):
            yy = 1004 + k * 18
            cv.drawLine(462 - k * 6, yy, 618 + k * 6, yy, stroke('#8a8478', 3))
        cv.drawPath(path_poly([(515, 1000), (565, 1000), (575, hy + 30), (505, hy + 30)]), fill('#bdb2a0'))
        cv.drawPath(st, ink(3.5))
        # hall body: pillars + lattice doors
        cv.drawRect(skia.Rect.MakeLTRB(200, 760, 880, 1000), fill('#d8c8a8'))
        xs = [210 + k * (660 / 7) for k in range(8)]
        for k in range(7):
            lattice(cv, xs[k] + 10, 790, xs[k + 1] - 10, 990, step=16, col='#2f6a5a', paper='#efe4c8', frame='#3a7a6a')
            if night:
                E.append(dict(kind='window', rect=(xs[k] + 10, 790, xs[k + 1] - xs[k] - 20, 200)))
        for x_ in xs:
            pillar(cv, x_, 740, 1000, 22)
        dancheong(cv, 190, 728, 890, 770)
        # double-eaved roof
        giwa_roof(cv, 120, 960, 730, 600, lift=48)
        cv.drawRect(skia.Rect.MakeLTRB(300, 560, 780, 640), fill('#d8c8a8'))
        for x_ in range(300, 790, 60):
            cv.drawRect(skia.Rect.MakeLTRB(x_ - 6, 560, x_ + 6, 640), fill(RED))
        dancheong(cv, 290, 540, 790, 572)
        giwa_roof(cv, 230, 850, 545, 400, lift=54)
        # name plaque (abstract gold strokes on a dark board)
        cv.drawPath(rrect(470, 584, 140, 50, 4), fill('#2a2a3a')); cv.drawPath(rrect(470, 584, 140, 50, 4), stroke(GOLD, 4))
        draw_text(cv, '대전', 540, 624, 34, col=GOLD)
        # eave lanterns
        for x_ in (230, 850):
            lantern(cv, x_, 860, 0.8, E, cord=90)

    def yard(cv):
        stone = tx.stone_blocks(1100, 1100, bw=150, bh=100, base='#bdb6a8', seed=6)
        draw_tex_quad(cv, stone, [(-420, hy + 20), (1500, hy + 20), (2600, 2600), (-1520, 2600)])
        # royal path (eodo): three lanes, centre raised
        cv.drawPath(path_poly([(440, hy + 30), (640, hy + 30), (980, 2600), (100, 2600)]), fill('#a8a090'))
        cv.drawPath(path_poly([(500, hy + 30), (580, hy + 30), (720, 2600), (360, 2600)]), fill('#ccc4b4'))
        for sx in (440, 500, 580, 640):
            cv.drawLine(sx, hy + 30, 540 + (sx - 540) * 4.2, 2600, ink(2.5, 0.6))
        # rank stones in two rows
        for k in range(6):
            t = k / 5.0
            yb = hy + 60 + (t ** 1.6) * 640
            sc = 0.45 + 1.1 * (yb - hy) / 700
            for sgn in (-1, 1):
                xx = 540 + sgn * (140 + (yb - hy) * 0.55)
                rank_stone(cv, xx, yb, sc)
        # big drum on a stand (left)
        dx, dy = 110, 1440
        for sx in (-70, 70):
            cv.drawLine(dx + sx, dy + 230, dx + sx * 0.6, dy - 40, stroke('#8a2a24', 16)); cv.drawLine(dx + sx, dy + 230, dx + sx * 0.6, dy - 40, ink(3))
        cv.drawPath(ellipse(dx, dy, 120, 110), fill('#a8402e'))
        cv.drawPath(ellipse(dx + 30, dy, 80, 104), fill('#e8d8b8'))
        cv.drawCircle(dx + 34, dy, 46, fill('#c8302a')); cv.drawCircle(dx + 34, dy, 46, stroke(GOLD, 6))
        for k in range(10):
            a = k * math.pi / 5
            cv.drawCircle(dx + 30 + math.cos(a) * 70, dy + math.sin(a) * 92, 5, fill(GOLD))
        cv.drawPath(ellipse(dx, dy, 120, 110), ink(4))
        cv.drawPath(ellipse(dx + 30, dy, 80, 104), ink(3))
        # banners (right) - flame-edged flags
        for k, (bx, col) in enumerate(((880, '#e8b830'), (960, '#c8302a'), (1040, '#2d5ba8'))):
            top = 1060 + k * 40
            cv.drawLine(bx, top, bx, 1760, stroke('#5a3a24', 9)); cv.drawLine(bx, top, bx, 1760, ink(2))
            pts = [(bx, top + 20), (bx - 150, top + 30)]
            for j in range(6):
                pts.append((bx - 150 + (j % 2) * -24, top + 60 + j * 34))
            pts.append((bx, top + 260))
            fl = path_poly(pts)
            cv.drawPath(fl, fill(col)); cv.drawPath(fl, ink(3))
            cv.drawCircle(bx - 70, top + 140, 26, stroke('#f4ecd8', 5))
            cv.drawCircle(bx, top - 6, 9, fill(GOLD))

    def near(cv):
        # blurred pine branch top-left + stone balustrade post bottom-right

        cv.drawPath(rrect(900, 1900, 300, 600, 20), fill('#bdb6a8')); cv.drawPath(rrect(900, 1900, 300, 600, 20), ink(6))
        cv.drawPath(ellipse(1050, 1890, 140, 40), fill('#d0c8ba')); cv.drawPath(ellipse(1050, 1890, 140, 40), ink(5))

    def lights_hall(cv, mm):
        sk.draw_emitters(cv, [e for e in E if e['kind'] == 'window'], mm, night)
        for e in E:
            if e['kind'] == 'window':
                x, y, w, h = e['rect']
                lattice(cv, x, y, x + w, y + h, step=16, col='#2a3a3a', paper=None)
        lit = [e for e in E if e['kind'] == 'lamp']
        for e in lit:
            lantern_glow(cv, e, night)
        sk.draw_emitters(cv, lit, mm, night)
        if night:
            pool(cv, 540, hy + 40, 500, 60, mm['key'], 0.3)

    return [
        ('sky', 30.0, sky, dict(grade=False)),
        ('mountain', 10.0, mountain, dict(haze=0.25)),
        ('hall', 3.0, hall, dict(lights=lights_hall)),
        ('yard', 1.0, yard, dict()),
        ('near', 0.6, near, dict(blur=10)),
    ], dict(ground_y=1700, stairs=(540, 1040), hall=(540, 780), drum=(140, 1440))


REGISTRY = {'palace_hall': palace_hall, 'study_room': study_room, 'map_table': map_table,
            'map_table_late': map_table_late, 'gate_court': gate_court}
