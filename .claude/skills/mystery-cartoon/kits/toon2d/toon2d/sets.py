"""Painted 2D sets, each split into 4-6 depth planes. build_set(name, mood, cache_dir) -> list[Layer].

Plane coordinates = the 1080x1920 frame as seen from the reference camera; every plane has margins.
Z: sky ~12-14, far ~5, mid ~2, subject 1.0, near foreground ~0.55-0.65 (blurred).
"""
import math

import skia

from .paint import (C, fill, stroke, ink, shade, mix, rgb, path_poly, path_smooth, rrect, ellipse, blurred,
                    lin_grad, rad_grad, argb, draw_tex_quad, draw_in_quad, rng, surface, INK)
from . import textures as tx
from . import setkit as sk
from .light import MOODS, halo, pool, god_rays, window_slash, long_shadow
from .scene import Layer, bake_plane, cached, W, H, MX, MY
from .text import draw_text

NIGHTLIKE = ('night',)


def ground_quad(vx, h0, y_near, w_near, y_far_off=6, x_shift=0.0):
    """Homography quad for a ground strip centred on vx, from horizon h0 down to y_near."""
    yf = h0 + y_far_off
    wf = w_near * (yf - h0) / (y_near - h0)
    return [(vx - wf / 2 + x_shift * (yf - h0) / (y_near - h0), yf), (vx + wf / 2 + x_shift * (yf - h0) / (y_near - h0), yf),
            (vx + w_near / 2 + x_shift, y_near), (vx - w_near / 2 + x_shift, y_near)]


def gy(h0, y_near, d):
    """Screen y of a ground line at fraction d (0 = horizon, 1 = near edge)."""
    return h0 + (y_near - h0) * d


# ----------------------------------------------------------------------------- true perspective ground
F_PX = 1000.0
MIPS = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


class Ground:
    """Pinhole ground plane: x = vx + F*X/Z, y = h0 + K/Z  (X, Z in metres, K = F * camera height)."""

    def __init__(self, vx, h0, cam_h=1.4):
        self.vx, self.h0, self.K = vx, h0, F_PX * cam_h

    def proj(self, X, Z):
        return (self.vx + F_PX * X / Z, self.h0 + self.K / Z)

    def scale(self, Z):
        """pixels per metre at depth Z"""
        return F_PX / Z

    def z_at(self, y):
        return self.K / (y - self.h0)

    def matrix(self):
        return skia.Matrix.MakeAll(F_PX, self.vx, 0, 0, self.h0, self.K, 0, 1, 0)

    def tile(self, cv, img, tile_w, tile_d, xr=(-80, 80), zr=(0.4, 600), x0=0.0, repeat_x=True, alpha=1.0):
        """Fill ground region xr x zr (metres) with img repeating every tile_w x tile_d metres."""
        lm = skia.Matrix()
        lm.setScaleTranslate(tile_w / img.width(), tile_d / img.height(), x0, 0)
        tm = skia.TileMode.kRepeat
        sh = img.withDefaultMipmaps().makeShader(tm if repeat_x else skia.TileMode.kDecal, tm, MIPS, lm)
        p = skia.Paint(AntiAlias=True)
        p.setShader(sh)
        p.setAlphaf(alpha)
        cv.save()
        cv.concat(self.matrix())
        cv.drawRect(skia.Rect.MakeLTRB(xr[0], zr[0], xr[1], zr[1]), p)
        cv.restore()

    def line(self, cv, X0, Z0, X1, Z1, paint, steps=40):
        pts = [self.proj(X0 + (X1 - X0) * k / steps, Z0 + (Z1 - Z0) * k / steps) for k in range(steps + 1)]
        cv.drawPath(path_poly(pts, close=False), paint)


# =============================================================================== DESERT / RAILS
def _track_tile(seed=1):
    """One 0.65 m period of track, 3.2 m wide: ballast, one tie with plates and spikes, two rails."""
    Wt, Ht = 1280, 260
    s = surface(Wt, Ht, '#a8735a')
    cv = s.getCanvas()
    cv.drawImage(tx.gravel(Wt, Ht, seed=seed, smin=8, smax=17, count=1400), 0, 0)
    ties = tx.wood_planks(980, 104, plank=104, base='#8a6a52', seed=seed + 2, nails=False)
    cv.drawRect(skia.Rect.MakeXYWH(158, 92, 980, 40), fill('#3a2630', 0.35))
    cv.drawImage(ties, 150, 60)
    cv.drawRect(skia.Rect.MakeXYWH(150, 60, 980, 104), ink(3.2))
    for rx in (360, 920):
        cv.drawPath(rrect(rx - 54, 78, 108, 68, 6), fill('#5a4a52'))
        cv.drawPath(rrect(rx - 54, 78, 108, 68, 6), ink(2.4))
        for sx in (-36, 36):
            cv.drawCircle(rx + sx, 112, 8, fill('#3a3040')); cv.drawCircle(rx + sx - 2, 109, 3, fill('#9a8a9a'))
    for rx in (360, 920):
        cv.drawRect(skia.Rect.MakeXYWH(rx - 30, 0, 60, Ht), fill('#4a3a48'))
        cv.drawRect(skia.Rect.MakeXYWH(rx - 20, 0, 40, Ht), fill('#7a6a78'))
        cv.drawRect(skia.Rect.MakeXYWH(rx - 13, 0, 15, Ht), fill('#efe4dc'))
        cv.drawLine(rx - 30, 0, rx - 30, Ht, ink(3.4)); cv.drawLine(rx + 30, 0, rx + 30, Ht, ink(3.4))
    return s.makeImageSnapshot()


# =============================================================================== HOUSE INTERIOR (kitchen)
def kitchen(mood):
    """Farmhouse kitchen: sage plaster + white tile, honey wood floor, centred window over the sink,
    terracotta cabinets, black range with a copper hood on the right of the back wall, plate dresser on the
    big receding LEFT wall, rattan pendant, striped runner."""
    m = MOODS[mood]
    night = mood in NIGHTLIKE
    E = []
    bx0, bx1, by0, by1 = 320, 1140, 300, 1200     # back wall off to the right: the left wall recedes
    vx, vy = 720, 900
    SAGE, SAGE_D, CAB, COPPER = '#a9c49a', '#93b386', '#c8673f', '#c87a3e'

    def wmap(x, y):                                  # design canvas (1000x1040) -> back-wall plane coords
        return bx0 + (x - 40) * (bx1 - bx0) / 1000.0, by0 + (y - 260) * (by1 - by0) / 1040.0

    def room(cv):
        ceil = [(-800, -900), (1900, -900), (bx1, by0), (bx0, by0)]
        draw_tex_quad(cv, tx.wood_planks(1600, 1200, plank=130, base='#d8b48a', seed=21, nails=False), ceil)
        lw = [(-800, -900), (bx0, by0), (bx0, by1), (-800, 3200)]
        draw_tex_quad(cv, tx.wallpaper(1400, 1800, base=SAGE, motif=SAGE_D, stripe='#b4cea6', step=110), lw)
        rw = [(bx1, by0), (1900, -900), (1900, 3200), (bx1, by1)]
        draw_tex_quad(cv, tx.wallpaper(1400, 1800, base=SAGE_D, motif='#86a87a', stripe='#9cbc90', step=110), rw)
        cv.drawPath(path_poly(rw), fill('#3a2a4a', 0.16))
        cv.drawImage(tx.wallpaper(bx1 - bx0, by1 - by0, base=SAGE, motif=SAGE_D, stripe='#b4cea6', step=110), bx0, by0)
        cv.drawImage(tx.bricks(bx1 - bx0, by1 - 760, bw=64, bh=30, base='#f2efe8', mortar='#cfc8c0', seed=4, ink_a=0.18), bx0, 760)
        fl = [(bx0, by1), (bx1, by1), (1900, 3200), (-800, 3200)]
        draw_tex_quad(cv, tx.wood_planks(1400, 1400, plank=120, base='#c8925a', seed=22, nails=False), fl)
        for q in (ceil, lw, rw, fl):
            cv.drawPath(path_poly(q), ink(3, 0.6))
        # ceiling beams receding toward the back wall
        for k in range(3):
            fx = bx0 + (k + 0.5) * (bx1 - bx0) / 3
            bq = [(fx - 14, by0), (fx + 14, by0), (vx + (fx - vx) * 3.4 + 70, -900), (vx + (fx - vx) * 3.4 - 70, -900)]
            cv.drawPath(path_poly(bq), fill('#8a5a3a')); cv.drawPath(path_poly(bq), ink(3))
        # striped runner rug in perspective
        rug = surface(400, 900, '#2f4a7a')
        rc = rug.getCanvas()
        for k, col in enumerate(('#f2e6c8', '#e0a83a', '#f2e6c8', '#c8673f', '#f2e6c8', '#e0a83a', '#f2e6c8')):
            rc.drawRect(skia.Rect.MakeXYWH(0, 80 + k * 110, 400, 46), fill(col))
        for k in range(26):
            rc.drawLine(k * 16, 0, k * 16, 16, stroke('#f2e6c8', 3)); rc.drawLine(k * 16, 884, k * 16, 900, stroke('#f2e6c8', 3))
        draw_tex_quad(cv, rug.makeImageSnapshot(), [(560, 1330), (840, 1330), (1010, 2050), (330, 2050)])
        cv.drawPath(path_poly([(560, 1330), (840, 1330), (1010, 2050), (330, 2050)]), ink(2.6, 0.6))
        cv.drawRect(skia.Rect.MakeLTRB(bx0, by0, bx1, by1), ink(3))
        cv.drawRect(skia.Rect.MakeLTRB(bx0, by1 - 24, bx1, by1), fill('#8a5a3a')); cv.drawRect(skia.Rect.MakeLTRB(bx0, by1 - 24, bx1, by1), ink(2.4))

        # ---- back wall content, designed on a 1000x1040 canvas
        cv.save(); cv.translate(bx0, by0); cv.scale((bx1 - bx0) / 1000.0, (by1 - by0) / 1040.0); cv.translate(-40, -260)
        # centred window with a view of an orchard
        wx, wy, ww, wh = 330, 330, 330, 300
        sv = surface(ww, wh)
        sc = sv.getCanvas()
        sk.sky(sc, MOODS['day'] if not night else m, x0=0, y0=0, x1=ww, y1=wh, clouds=2, seed=8, cloud_band=(20, 80), cloud_scale=0.5)
        sk.hills(sc, 210, -40, ww + 40, 40, '#7ab85a', seed=6, wav=110)
        for k in range(4):
            sk.tree(sc, 30 + k * 95, 280 - (k % 2) * 16, 120, col='#4f9a3c', seed=k + 5)
        cv.drawImage(sv.makeImageSnapshot(), wx, wy)
        sk.window(cv, wx, wy, ww, wh, frame='#f2ece0', glass='#9cc4e8', curtain='#e0a83a', E=None, lit=False, panes=(3, 2))
        cv.drawPath(path_poly([(wx, wy), (wx + ww, wy), (wx + ww, wy + wh), (wx, wy + wh)]), fill('#bfe0ff', 0.12))
        for k in range(3):                               # herbs on the sill
            sk.plant_pot(cv, wx + 60 + k * 105, wy + wh + 20, 0.8, col='#c8673f', leaf=['#4f9a3c', '#6ab04a', '#3f8a46'][k], seed=k)
        # long counter with terracotta doors
        cy0 = 1000
        cv.drawPath(rrect(20, cy0, 960, 30, 4), fill('#e8dcc4')); cv.drawPath(rrect(20, cy0, 960, 30, 4), ink(3))
        for k in range(4):
            x = 30 + k * 165
            d = rrect(x, cy0 + 36, 158, 260, 6)
            cv.drawPath(d, fill(CAB)); cv.drawPath(rrect(x + 14, cy0 + 52, 130, 228, 6), stroke(shade(CAB, -0.3), 3))
            cv.drawPath(d, ink(3))
            cv.drawPath(rrect(x + 64, cy0 + 60, 30, 10, 4), fill('#2a2232'))
        sh_ = fill((0x4a, 0x2e, 0x5a), 0.35); blurred(sh_, 10)
        cv.drawRect(skia.Rect.MakeLTRB(20, cy0 + 28, 700, cy0 + 60), sh_)
        # farmhouse sink under the window
        cv.drawPath(rrect(400, cy0 - 6, 200, 90, 10), fill('#f4f0e8')); cv.drawPath(rrect(400, cy0 - 6, 200, 90, 10), ink(3))
        tp = skia.Path(); tp.moveTo(500, cy0 - 4); tp.lineTo(500, cy0 - 70); tp.quadTo(500, cy0 - 96, 530, cy0 - 92); tp.lineTo(538, cy0 - 76)
        cv.drawPath(tp, stroke(COPPER, 12)); cv.drawPath(tp, ink(2.4))
        # black range + copper hood on the right
        rx0 = 700
        cv.drawPath(rrect(rx0, cy0 - 20, 270, 316, 12), fill('#2e2a3a')); cv.drawPath(rrect(rx0, cy0 - 20, 270, 316, 12), ink(3.5))
        cv.drawPath(rrect(rx0 + 30, cy0 + 70, 210, 150, 10), fill('#4a4458')); cv.drawPath(rrect(rx0 + 30, cy0 + 70, 210, 150, 10), ink(3))
        cv.drawPath(rrect(rx0 + 46, cy0 + 86, 178, 70, 8), fill('#f2a040', 0.35))
        cv.drawLine(rx0 + 40, cy0 + 60, rx0 + 230, cy0 + 60, stroke('#c8c0b0', 8))
        for k in range(4):
            cv.drawCircle(rx0 + 50 + k * 56, cy0 + 22, 11, fill('#e8dcc4')); cv.drawCircle(rx0 + 50 + k * 56, cy0 + 22, 11, ink(2))
        cv.drawPath(rrect(rx0 + 50, cy0 - 50, 90, 34, 8), fill('#5a7ac8')); cv.drawPath(rrect(rx0 + 50, cy0 - 50, 90, 34, 8), ink(2.6))   # pot
        hood = path_poly([(rx0 - 10, 640), (rx0 + 280, 640), (rx0 + 200, 420), (rx0 + 70, 420)])
        cv.drawPath(hood, fill(COPPER)); cv.drawPath(path_poly([(rx0 + 20, 630), (rx0 + 60, 630), (rx0 + 110, 430), (rx0 + 90, 430)]), fill('#f8c890', 0.5))
        cv.drawPath(hood, ink(3.5))
        cv.drawPath(rrect(rx0 + 80, 280, 110, 145, 4), fill(shade(COPPER, -0.15))); cv.drawPath(rrect(rx0 + 80, 280, 110, 145, 4), ink(3))
        # open shelf with jars on the left of the window
        cv.drawPath(rrect(40, 560, 250, 22, 4), fill('#8a5a3a')); cv.drawPath(rrect(40, 560, 250, 22, 4), ink(2.6))
        for k, (jc, lid) in enumerate((('#f4f0e8', '#3f6ac8'), ('#f2d68a', '#c8673f'), ('#e8f0e0', '#2f8a6a'), ('#f4f0e8', '#e0a83a'))):
            x = 55 + k * 58
            cv.drawPath(rrect(x, 480 + (k % 2) * 14, 46, 80 - (k % 2) * 14, 8), fill(jc)); cv.drawPath(rrect(x, 480 + (k % 2) * 14, 46, 80 - (k % 2) * 14, 8), ink(2.4))
            cv.drawPath(rrect(x - 3, 470 + (k % 2) * 14, 52, 14, 4), fill(lid)); cv.drawPath(rrect(x - 3, 470 + (k % 2) * 14, 52, 14, 4), ink(2.2))
        sk.wall_clock(cv, 165, 380, 50)
        # hanging garlic + herb bundle from the shelf
        for k in range(3):
            hx = 70 + k * 90
            cv.drawLine(hx, 582, hx, 640, stroke('#7a5a3a', 3))
            cv.drawPath(ellipse(hx, 655, 16, 20), fill(['#f4ecd8', '#6ab04a', '#f4ecd8'][k])); cv.drawPath(ellipse(hx, 655, 16, 20), ink(2.2))
        cv.restore()

        # ---- big receding left wall: plate dresser + pan rack
        def left_wall_art(c):
            # dresser (hutch) with plates
            c.drawPath(rrect(260, 260, 420, 900, 10), fill('#6a8ab0')); c.drawPath(rrect(260, 260, 420, 900, 10), ink(4))
            for k in range(3):
                y = 330 + k * 150
                c.drawRect(skia.Rect.MakeXYWH(285, y + 110, 370, 16), fill('#4a6a90'))
                for j in range(4):
                    px = 330 + j * 90
                    c.drawCircle(px, y + 60, 40, fill('#f4f0e8')); c.drawCircle(px, y + 60, 40, ink(2.6))
                    c.drawCircle(px, y + 60, 26, stroke(['#3f6ac8', '#c8673f', '#2f8a6a', '#e0a83a'][(j + k) % 4], 5))
            c.drawPath(rrect(280, 800, 380, 340, 8), fill('#5a7aa0')); c.drawPath(rrect(280, 800, 380, 340, 8), ink(3))
            for j in range(2):
                c.drawPath(rrect(300 + j * 180, 820, 160, 300, 6), stroke('#3a5a80', 4))
                c.drawCircle(450 + j * 30 - 30 * j, 970, 9, fill('#e6c25a'))
            # copper pans on hooks
            c.drawLine(40, 300, 220, 300, stroke('#2a2232', 8))
            for k, (pr, py) in enumerate(((50, 400), (40, 380), (34, 370))):
                px = 70 + k * 60
                c.drawLine(px, 300, px, py - pr, stroke('#2a2232', 3))
                c.drawCircle(px, py, pr, fill(COPPER)); c.drawCircle(px, py, pr, ink(3))
                c.drawCircle(px - pr * 0.3, py - pr * 0.3, pr * 0.3, fill('#f8c890', 0.6))
        draw_in_quad(cv, 900, 1200, [(-800, -600), (bx0, by0 - 40), (bx0, by1 + 40), (-800, 2800)], left_wall_art)

    def lamp(cv):
        # rattan dome pendant
        cv.drawLine(720, -300, 720, 170, stroke('#2a2232', 5))
        dome = skia.Path(); dome.moveTo(610, 262); dome.quadTo(615, 160, 720, 158); dome.quadTo(825, 160, 830, 262); dome.close()
        cv.drawPath(dome, fill('#d8a060'))
        cv.save(); cv.clipPath(dome, doAntiAlias=True)
        for k in range(12):
            cv.drawLine(600 + k * 22, 270, 690 + k * 6, 150, stroke('#a8703a', 3, 0.7))
            cv.drawLine(840 - k * 22, 270, 750 - k * 6, 150, stroke('#e8b878', 2, 0.6))
        cv.restore()
        cv.drawPath(dome, ink(3.5))
        cv.drawPath(ellipse(720, 262, 110, 14), fill('#f8ecc0')); cv.drawPath(ellipse(720, 262, 110, 14), ink(3))
        E.append(dict(kind='lamp', pos=(720, 268), r=260, lit=True, ground=None))

    def near(cv):
        # table edge with a bread loaf and a teapot in the near foreground
        tp = [(-300, 1880), (520, 1820), (700, 2600), (-300, 2600)]
        draw_tex_quad(cv, tx.wood_planks(1200, 900, plank=110, base='#9a5a32', seed=24, nails=False), tp)
        cv.drawPath(path_poly(tp), ink(4))
        tea = path_smooth([(60, 1840), (40, 1740), (130, 1690), (220, 1740), (200, 1840)])
        cv.drawPath(tea, fill('#3f6ac8')); cv.drawPath(tea, ink(4))
        cv.drawPath(path_smooth([(210, 1770), (270, 1730), (290, 1700)], close=False), stroke('#3f6ac8', 18)); cv.drawPath(path_smooth([(210, 1770), (270, 1730), (290, 1700)], close=False), ink(3))
        cv.drawPath(ellipse(130, 1688, 30, 12), fill('#e8dcc4')); cv.drawPath(ellipse(130, 1688, 30, 12), ink(3))
        loaf = path_smooth([(-200, 1860), (-210, 1790), (-120, 1750), (-20, 1790), (-30, 1860)])
        cv.drawPath(loaf, fill('#d8964a')); cv.drawPath(loaf, ink(4))
        for k in range(3):
            cv.drawLine(-170 + k * 50, 1790, -150 + k * 50, 1770, stroke('#f2d08a', 6))

    def lights_room(cv, mm):
        wx, wy = wmap(495, 480)
        god_rays(cv, (wx, wy), 112, 34, 1500, n=7, col=mm['key'], a=0.24 if not night else 0.1)
        window_slash(cv, [(470, 1330), (860, 1310), (980, 1700), (360, 1740)], mm['key'], 0.36 if not night else 0.1)
        sk.draw_emitters(cv, [e for e in E if e['kind'] == 'window'], mm, night)

    def lights_lamp(cv, mm):
        halo(cv, 720, 268, 300, mm['key'], 0.55 if night else 0.3)

    return [
        ('room', 1.3, room, dict(lights=lights_room)),
        ('lamp', 0.9, lamp, dict(lights=lights_lamp)),
        ('near', 0.6, near, dict(blur=10)),
    ], dict(ground_y=1560, h0=900, vx=vx, floor_y0=by1)


# =============================================================================== SHOP COUNTER (golden explanation)
def shop_counter(mood, prop='counter'):
    m = MOODS[mood]
    E = []

    def back(cv):
        cv.drawImage(tx.wood_planks(2000, 3200, plank=150, base='#8a4a2e', vertical=True, seed=7), -500, -700)
        # shelves with jars and boxes
        r = rng(5)
        for row in range(4):
            y = 120 + row * 300
            cv.drawPath(rrect(-500, y + 200, 2100, 30, 4), fill('#6a3420')); cv.drawPath(rrect(-500, y + 200, 2100, 30, 4), ink(3))
            x = -460
            while x < 1550:
                kind = r.random()
                c = r.choice(['#d8483a', '#2f8a6a', '#e6b43c', '#3f6ac8', '#c8a0c8', '#f4f0e8'])
                if kind < 0.45:
                    w_, h_ = r.uniform(60, 90), r.uniform(100, 170)
                    cv.drawPath(rrect(x, y + 200 - h_, w_, h_, 12), fill(mix(c, '#ffffff', 0.25), 0.9))
                    cv.drawPath(rrect(x + 6, y + 200 - h_ * 0.6, w_ - 12, h_ * 0.5, 6), fill(c))
                    cv.drawPath(rrect(x - 4, y + 190 - h_, w_ + 8, 18, 4), fill(shade(c, -0.3)))
                    cv.drawPath(rrect(x, y + 200 - h_, w_, h_, 12), ink(2.6))
                elif kind < 0.8:
                    w_, h_ = r.uniform(90, 150), r.uniform(80, 140)
                    cv.drawRect(skia.Rect.MakeXYWH(x, y + 200 - h_, w_, h_), fill(c))
                    cv.drawRect(skia.Rect.MakeXYWH(x + 10, y + 200 - h_ + 14, w_ - 20, 26), fill('#f4f0e8'))
                    cv.drawRect(skia.Rect.MakeXYWH(x, y + 200 - h_, w_, h_), ink(2.6))
                else:
                    w_ = 40
                    for k in range(3):
                        cv.drawPath(rrect(x + k * 26, y + 60, 22, 140, 10), fill(shade('#5ab04a', -0.2 + k * 0.1), 0.85))
                        cv.drawPath(rrect(x + k * 26, y + 60, 22, 140, 10), ink(2.2))
                    w_ = 80
                x += w_ + r.uniform(12, 40)
        # a hanging sign
        cv.drawPath(rrect(250, -200, 560, 150, 10), fill('#2a4a3a')); cv.drawPath(rrect(250, -200, 560, 150, 10), ink(4))
        draw_text(cv, 'GENERAL STORE', 530, -105, 58, '#e6c25a')

    def counter(cv):
        top = 1320
        cv.drawPath(path_poly([(-600, top), (1700, top), (1700, top + 80), (-600, top + 80)]), fill('#5a2a1e'))
        draw_tex_quad(cv, tx.wood_planks(2400, 600, plank=120, base='#b0703e', seed=9), [(-300, 1140), (1400, 1140), (1700, top), (-600, top)])
        cv.drawLine(-600, top, 1700, top, ink(4))
        cv.drawImage(tx.wood_planks(2400, 1200, plank=140, base='#7a3e26', vertical=True, seed=10), -600, top + 80)
        cv.drawLine(-600, top + 80, 1700, top + 80, ink(4))
        # the in-world explanation prop: a brass balance scale, glowing coins on one pan, a loaf on the other,
        # and a paper lot tag tied to the post
        cx, cy = 540, 1100
        cv.drawPath(rrect(cx - 220, cy + 150, 440, 50, 20), fill('#3a2230', 0.45))
        cv.drawPath(rrect(cx - 190, cy + 100, 380, 70, 16), fill('#6a3a22')); cv.drawPath(rrect(cx - 190, cy + 100, 380, 70, 16), ink(4))
        cv.drawPath(rrect(cx - 120, cy + 70, 240, 40, 12), fill('#b8802a')); cv.drawPath(rrect(cx - 120, cy + 70, 240, 40, 12), ink(4))
        cv.drawPath(rrect(cx - 22, cy - 380, 44, 460, 14), fill('#d89a3a'))
        cv.drawRect(skia.Rect.MakeXYWH(cx - 14, cy - 370, 10, 440), fill('#fff0c0', 0.55))
        cv.drawPath(rrect(cx - 22, cy - 380, 44, 460, 14), ink(4))
        tilt_ = math.radians(-7)                                   # the coin side is heavier
        bl = 330
        bx0_, by0_ = cx - math.cos(tilt_) * bl, cy - 380 - math.sin(tilt_) * bl
        bx1_, by1_ = cx + math.cos(tilt_) * bl, cy - 380 + math.sin(tilt_) * bl
        cv.drawLine(bx0_, by0_, bx1_, by1_, stroke('#c8902e', 26)); cv.drawLine(bx0_, by0_, bx1_, by1_, stroke('#f8d890', 6, 0.7))
        p_ = skia.Path(); p_.moveTo(bx0_, by0_); p_.lineTo(bx1_, by1_)
        bp = skia.Paint(AntiAlias=True); bp.setStyle(skia.Paint.kStroke_Style); bp.setStrokeWidth(26); bp.setStrokeCap(skia.Paint.kRound_Cap)
        outl = skia.Path(); bp.getFillPath(p_, outl); cv.drawPath(outl, ink(4))
        cv.drawCircle(cx, cy - 380, 30, fill('#e6b43c')); cv.drawCircle(cx, cy - 380, 30, ink(4))
        cv.drawCircle(cx, cy - 430, 22, fill('#e6b43c')); cv.drawCircle(cx, cy - 430, 22, ink(4))
        pans = []
        for (ex_, ey_, drop) in ((bx0_, by0_, 330), (bx1_, by1_, 300)):
            py_ = ey_ + drop
            for sx in (-1, 1):
                cv.drawLine(ex_, ey_, ex_ + sx * 120, py_, stroke('#8a5a2a', 4))
            pan = skia.Path(); pan.moveTo(ex_ - 150, py_); pan.quadTo(ex_, py_ + 90, ex_ + 150, py_); pan.close()
            cv.drawPath(pan, fill('#d89a3a')); cv.drawPath(pan, ink(4))
            cv.drawPath(ellipse(ex_, py_, 150, 18), fill('#b8802a')); cv.drawPath(ellipse(ex_, py_, 150, 18), ink(3.5))
            pans.append((ex_, py_))
        (lx_, ly_), (rx_, ry_) = pans
        for j in range(7):                                          # coin stack on the heavy pan
            for i_ in range(3 - j // 3):
                xx = lx_ - 70 + i_ * 60 + (j % 2) * 8
                cv.drawPath(ellipse(xx, ly_ - 10 - j * 14, 34, 12), fill('#f2c640')); cv.drawPath(ellipse(xx, ly_ - 10 - j * 14, 34, 12), ink(2.4))
        loaf = path_smooth([(rx_ - 110, ry_ - 6), (rx_ - 100, ry_ - 80), (rx_, ry_ - 110), (rx_ + 100, ry_ - 80), (rx_ + 110, ry_ - 6)])
        cv.drawPath(loaf, fill('#d8964a')); cv.drawPath(loaf, ink(4))
        for k in range(3):
            cv.drawLine(rx_ - 60 + k * 50, ry_ - 70, rx_ - 36 + k * 50, ry_ - 96, stroke('#f2d08a', 8))
        # paper lot tag on a string
        cv.drawLine(cx + 22, cy - 200, cx + 90, cy - 120, stroke('#5a3a2a', 3))
        cv.save(); cv.translate(cx + 120, cy - 70); cv.rotate(8)
        tg = path_poly([(-46, -50), (46, -50), (46, 50), (-46, 50), (-60, 0)])
        cv.drawPath(tg, fill('#f8f2e2')); cv.drawPath(tg, ink(3))
        cv.drawCircle(-40, 0, 6, ink(2.4))
        draw_text(cv, 'LOT', 4, -10, 30, '#2a2232'); draw_text(cv, '8', 4, 40, 48, '#c8343c')
        cv.restore()
        E.append(dict(kind='glow', pos=(lx_ - 10, ly_ - 50), r=420))
        # coins on the counter
        r = rng(3)
        for k in range(14):
            x, y = r.uniform(80, 1000), r.uniform(1180, 1300)
            if abs(x - cx) < 280 and y < 1240:
                continue
            for j in range(r.randint(1, 5)):
                cv.drawPath(ellipse(x, y - j * 12, 34, 13), fill('#e6b43c')); cv.drawPath(ellipse(x, y - j * 12, 34, 13), ink(2.4))
            cv.drawPath(ellipse(x - 8, y - (j) * 12 - 3, 12, 4), fill('#fff4c0', 0.8))

    def near(cv):
        r = rng(8)
        for k in range(9):
            x, y = r.uniform(-200, 1300), r.uniform(1500, 2300)
            cv.drawPath(ellipse(x, y, 140, 52), fill('#e6b43c')); cv.drawPath(ellipse(x, y, 140, 52), ink(5))

    def lights_back(cv, mm):
        god_rays(cv, (-200, -300), 55, 28, 2600, n=7, col=mm['key'], a=0.22)

    def lights_counter(cv, mm):
        for e in E:
            x, y = e['pos']
            p = skia.Paint(AntiAlias=True)
            p.setShader(rad_grad((x, y + 40), e['r'], [argb((255, 200, 90), 0), argb((255, 200, 90), 0), argb((255, 196, 90), 0.75),
                                                      argb((255, 170, 80), 0.25), argb((255, 170, 80), 0)], [0, 0.42, 0.55, 0.75, 1]))
            p.setBlendMode(skia.BlendMode.kPlus)
            cv.drawCircle(x, y + 40, e['r'], p)
            rim = ellipse(x, y + 10, 150, 90)
            gp = stroke((255, 236, 170), 10, 0.6, blend=skia.BlendMode.kPlus); blurred(gp, 14)
            cv.drawPath(rim, gp)
        p = skia.Paint(AntiAlias=True)
        p.setShader(rad_grad((540, 980), 700, [argb((255, 210, 120), 0.35), argb((255, 210, 120), 0)]))
        p.setBlendMode(skia.BlendMode.kScreen)
        cv.drawCircle(540, 980, 700, p)
        r = rng(4)
        for k in range(26):
            x, y = r.uniform(150, 950), r.uniform(600, 1300)
            halo(cv, x, y, r.uniform(10, 26), (255, 230, 160), 0.7)

    return [
        ('back', 2.2, back, dict(blur=8, haze=0.15, lights=lights_back)),
        ('counter', 1.0, counter, dict(lights=lights_counter)),
        ('near', 0.6, near, dict(blur=14)),
    ], dict(ground_y=1300)


# =============================================================================== TOWN, top-down
def town_top(mood):
    """River town seen from above: a winding river crossing a street grid with plank bridges, blocks of
    gabled houses, and an off-centre market square with striped stalls (nothing in the middle of frame)."""
    m = MOODS[mood]
    night = mood in NIGHTLIKE
    E = []
    cx, cy = 540, 960
    XS = (-200, 170, 540, 910, 1280)                # street centre lines
    YS = (-330, 80, 490, 900, 1310, 1720, 2130)
    RW = 64
    SQUARE = (XS[0], YS[4], XS[2], YS[5])           # market square cell (lower left)

    river = path_smooth([(-560, 180), (-200, 300), (150, 560), (420, 800), (700, 1020), (980, 1160), (1250, 1420), (1620, 1600)],
                        close=False)
    meas = skia.PathMeasure(river, False)
    RP = []
    L_ = meas.getLength()
    for k in range(0, int(L_), 12):
        pos, _ = meas.getPosTan(k)
        RP.append((pos.x(), pos.y()))

    def dist_river(x, y):
        return min(math.hypot(x - a, y - b) for a, b in RP[::3])

    def ground(cv):
        cv.drawImage(tx.grass(2000, 3100, base='#5aa84a', seed=3, density=0.6), -480, -600)
        # streets
        for X in XS:
            cv.drawRect(skia.Rect.MakeLTRB(X - RW / 2, -600, X + RW / 2, 2500), fill('#6a6a86'))
        for Y in YS:
            cv.drawRect(skia.Rect.MakeLTRB(-480, Y - RW / 2, 1520, Y + RW / 2), fill('#6a6a86'))
        for X in XS:
            for y in range(-600, 2500, 60):
                cv.drawLine(X, y, X, y + 26, stroke('#f0d070', 4))
            cv.drawLine(X - RW / 2, -600, X - RW / 2, 2500, ink(3)); cv.drawLine(X + RW / 2, -600, X + RW / 2, 2500, ink(3))
        for Y in YS:
            for x in range(-480, 1520, 60):
                cv.drawLine(x, Y, x + 26, Y, stroke('#f0d070', 4))
            cv.drawLine(-480, Y - RW / 2, 1520, Y - RW / 2, ink(3)); cv.drawLine(-480, Y + RW / 2, 1520, Y + RW / 2, ink(3))
        # crossings: square patches over the dashes
        for X in XS:
            for Y in YS:
                cv.drawRect(skia.Rect.MakeLTRB(X - RW / 2 + 2, Y - RW / 2 + 2, X + RW / 2 - 2, Y + RW / 2 - 2), fill('#6a6a86'))
        # market square (paved, off-centre)
        x0, y0, x1, y1 = SQUARE[0] + RW / 2, SQUARE[1] + RW / 2, SQUARE[2] - RW / 2, SQUARE[3] - RW / 2
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fill('#d8ccb8'))
        for yy in range(int(y0), int(y1), 26):
            cv.drawLine(x0, yy, x1, yy, stroke('#b8aa96', 2))
            off = 0 if (yy // 26) % 2 else 22
            for xx in range(int(x0) + off, int(x1), 44):
                cv.drawLine(xx, yy, xx, yy + 26, stroke('#b8aa96', 2))
        cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), ink(3))
        # river: banks, water, ripples
        cv.drawPath(river, stroke('#c8b48a', 250)); cv.drawPath(river, stroke('#3a7ac0', 200))
        cv.drawPath(river, stroke('#4f92d8', 150)); cv.drawPath(river, stroke('#6ab0e8', 50, 0.5))
        r = rng(6)
        for k in range(0, len(RP) - 2, 5):
            (a, b), (c, d) = RP[k], RP[k + 2]
            off = r.uniform(-60, 60)
            nx, ny = -(d - b), (c - a)
            nl = math.hypot(nx, ny) or 1
            cv.drawLine(a + nx / nl * off, b + ny / nl * off, c + nx / nl * off, d + ny / nl * off, stroke('#d8f0ff', 3, 0.7))
        bank = skia.Paint(AntiAlias=True); bank.setStyle(skia.Paint.kStroke_Style); bank.setStrokeWidth(250)
        edge = skia.Path(); bank.getFillPath(river, edge)
        cv.drawPath(edge, ink(3))
        # plank bridges where streets cross the river
        for X in XS:
            ys = [b for a, b in RP if abs(a - X) < 7]
            if ys:
                yb = sum(ys) / len(ys)
                bridge(cv, X, yb, True)
        for Y in YS:
            xs_ = [a for a, b in RP if abs(b - Y) < 7]
            if xs_:
                xb = sum(xs_) / len(xs_)
                bridge(cv, xb, Y, False)

    def bridge(cv, x, y, vertical):
        cv.save(); cv.translate(x, y)
        if not vertical:
            cv.rotate(90)
        L, Wd = 330, RW + 16
        sh = fill(m['shadow_cast'], 0.45); blurred(sh, 6)
        cv.drawRect(skia.Rect.MakeXYWH(-Wd / 2 + 14, -L / 2 + 14, Wd, L), sh)
        cv.drawRect(skia.Rect.MakeXYWH(-Wd / 2, -L / 2, Wd, L), fill('#b07a45'))
        for k in range(int(L / 22)):
            cv.drawLine(-Wd / 2, -L / 2 + k * 22, Wd / 2, -L / 2 + k * 22, stroke('#7a4a2a', 2.4))
        for sx in (-1, 1):
            cv.drawRect(skia.Rect.MakeXYWH(sx * Wd / 2 - 6, -L / 2, 12, L), fill('#8a5a3a'))
            for k in range(6):
                cv.drawRect(skia.Rect.MakeXYWH(sx * Wd / 2 - 9, -L / 2 + k * L / 5 - 9, 18, 18), fill('#6a3a22'))
        cv.drawRect(skia.Rect.MakeXYWH(-Wd / 2, -L / 2, Wd, L), ink(3))
        cv.restore()

    def draw_house(cv, x, y, ang, hw, hd, sd):
        cols = ['#9fc3c8', '#e8c87a', '#c8a0c8', '#a8c8a0', '#e8a090', '#d8d0e8', '#f0e0c0']
        roofs = ['#3f5fb8', '#c8402e', '#2f8a7a', '#d87a2a', '#6a4ab0', '#b83a5a', '#4a8a3a']
        wall = cols[sd % len(cols)]
        roof = roofs[(sd * 5 + int(x)) % len(roofs)]
        vpx, vpy = cx, -2400
        lean = 0.07
        lx, ly = (x - vpx) * lean * 0.6, (y - vpy) * lean * 0.22
        ca, sa = math.cos(math.radians(-ang)), math.sin(math.radians(-ang))
        llx, lly = lx * ca - ly * sa, lx * sa + ly * ca
        cv.save(); cv.translate(x, y); cv.rotate(ang)
        cv.drawPath(rrect(-hw * 0.62, -hd * 0.8, hw * 1.24, hd * 1.6, 10), fill('#6ab85a'))
        cv.drawPath(rrect(-hw * 0.62, -hd * 0.8, hw * 1.24, hd * 1.6, 10), stroke('#3f8a46', 6))
        sh = fill(m['shadow_cast'], 0.4); blurred(sh, 7)
        cv.drawPath(rrect(-hw / 2 + 16 + llx, -hd / 2 + 16 + lly, hw, hd, 6), sh)
        base_q = [(-hw / 2, -hd / 2), (hw / 2, -hd / 2), (hw / 2, hd / 2), (-hw / 2, hd / 2)]
        top_q = [(px + llx, py + lly) for px, py in base_q]
        for i in range(4):
            a0, a1 = base_q[i], base_q[(i + 1) % 4]
            b0, b1 = top_q[i], top_q[(i + 1) % 4]
            side = path_poly([a0, a1, b1, b0])
            cv.drawPath(side, fill(shade(wall, -0.18 - 0.1 * i)))
            cv.drawPath(side, ink(2.2))
            mxp, myp = (a0[0] + a1[0] + b0[0] + b1[0]) / 4, (a0[1] + a1[1] + b0[1] + b1[1]) / 4
            cv.drawRect(skia.Rect.MakeXYWH(mxp - 10, myp - 7, 20, 14), fill('#9cc4e8' if not night else '#ffd890'))
            cv.drawRect(skia.Rect.MakeXYWH(mxp - 10, myp - 7, 20, 14), ink(1.6))
        if night:
            E.append(dict(kind='point', pos=(x, y)))
        ex = 10
        t0 = (top_q[0][0] - ex, top_q[0][1] - ex); t1 = (top_q[1][0] + ex, top_q[1][1] - ex)
        t2 = (top_q[2][0] + ex, top_q[2][1] + ex); t3 = (top_q[3][0] - ex, top_q[3][1] + ex)
        r0 = ((t0[0] + t3[0]) / 2 + llx * 0.5, (t0[1] + t3[1]) / 2 + lly * 0.5)
        r1 = ((t1[0] + t2[0]) / 2 + llx * 0.5, (t1[1] + t2[1]) / 2 + lly * 0.5)
        q1 = [t0, t1, r1, r0]; q2 = [r0, r1, t2, t3]
        cv.drawPath(path_poly(q1), fill(shade(roof, 0.12)))
        cv.drawPath(path_poly(q2), fill(shade(roof, -0.22)))
        for j in range(1, 5):
            f = j / 5
            for qa, qb, qc, qd, col in ((t0, t1, r1, r0, shade(roof, -0.1)), (t3, t2, r1, r0, shade(roof, -0.38))):
                pa = (qa[0] + (qd[0] - qa[0]) * f, qa[1] + (qd[1] - qa[1]) * f)
                pb = (qb[0] + (qc[0] - qb[0]) * f, qb[1] + (qc[1] - qb[1]) * f)
                cv.drawLine(*pa, *pb, stroke(col, 2.2))
        cv.drawPath(path_poly(q1), ink(2.6)); cv.drawPath(path_poly(q2), ink(2.6))
        cv.drawLine(*r0, *r1, stroke(shade(roof, 0.35), 4))
        chx, chy = r1[0] - 34, r1[1] - 18
        cv.drawPath(rrect(chx, chy, 20, 24, 3), fill('#a04a32')); cv.drawPath(rrect(chx, chy, 20, 24, 3), ink(2))
        cv.restore()

    def stall(cv, x, y, col, sd):
        sh = fill(m['shadow_cast'], 0.4); blurred(sh, 5)
        cv.drawRect(skia.Rect.MakeXYWH(x - 50 + 10, y - 34 + 12, 100, 68), sh)
        aw = skia.Rect.MakeXYWH(x - 50, y - 34, 100, 68)
        cv.drawRect(aw, fill('#f4f0e8'))
        cv.save(); cv.clipRect(aw)
        for k in range(6):
            cv.drawRect(skia.Rect.MakeXYWH(x - 50 + k * 34, y - 34, 17, 68), fill(col))
        cv.restore()
        cv.drawLine(x - 50, y, x + 50, y, stroke(shade(col, -0.3), 3))
        cv.drawRect(aw, ink(2.6))
        r = rng(sd)
        for k in range(4):                                    # crates of produce in front
            cx_ = x - 36 + k * 24
            cv.drawRect(skia.Rect.MakeXYWH(cx_ - 10, y + 38, 20, 16), fill('#b07a45')); cv.drawRect(skia.Rect.MakeXYWH(cx_ - 10, y + 38, 20, 16), ink(1.6))
            cv.drawCircle(cx_, y + 42, 6, fill(r.choice(['#d8483a', '#f2b632', '#6ab04a', '#e8803a'])))

    def houses(cv):
        r = rng(7)
        sd = 0
        for i in range(len(XS) - 1):
            for j in range(len(YS) - 1):
                x0, x1 = XS[i] + RW / 2 + 16, XS[i + 1] - RW / 2 - 16
                y0, y1 = YS[j] + RW / 2 + 16, YS[j + 1] - RW / 2 - 16
                if SQUARE[0] <= XS[i] < SQUARE[2] and YS[j] == SQUARE[1]:
                    continue
                # two rows of houses facing the streets above and below
                for row, yy in enumerate((y0 + 70, y1 - 70)):
                    n = 2
                    for k in range(n):
                        xx = x0 + (k + 0.5) * (x1 - x0) / n
                        if dist_river(xx, yy) < 190:
                            continue
                        draw_house(cv, xx, yy, 0 if row else 180, 132, 98, sd)
                        sd += 1
        # market stalls in the square + trees at its corners
        x0, y0, x1, y1 = SQUARE[0] + RW / 2, SQUARE[1] + RW / 2, SQUARE[2] - RW / 2, SQUARE[3] - RW / 2
        cols = ['#c8343c', '#3f6ac8', '#2f8a6a', '#e0a83a', '#8a4ab0', '#d8483a']
        k = 0
        for yy in (y0 + 90, y1 - 120):
            for xx in (x0 + 110, x0 + 250, x0 + 390, x0 + 530):
                if xx < x1 - 60:
                    stall(cv, xx, yy, cols[k % len(cols)], k)
                    k += 1
        for (tx_, ty_) in ((x0 + 40, y0 + 200), (x1 - 40, y0 + 200), (x0 + 40, y1 - 220), (x1 - 40, y1 - 220)):
            sh = fill(m['shadow_cast'], 0.45); blurred(sh, 6)
            cv.drawPath(ellipse(tx_ + 18, ty_ + 22, 40, 30), sh)
            sk.foliage(cv, tx_, ty_, 40, '#3f8a46', seed=int(tx_ + ty_))
        # trees along the river banks and in the gaps
        for kk in range(0, len(RP), 9):
            a, b = RP[kk]
            for side in (-1, 1):
                if kk + 1 >= len(RP):
                    continue
                c, d = RP[kk + 1]
                nx, ny = -(d - b), (c - a)
                nl = math.hypot(nx, ny) or 1
                x, y = a + side * nx / nl * 150, b + side * ny / nl * 150
                if any(abs(x - X) < RW for X in XS) or any(abs(y - Y) < RW for Y in YS):
                    continue
                rad_ = r.uniform(26, 40)
                sh = fill(m['shadow_cast'], 0.45); blurred(sh, 6)
                cv.drawPath(ellipse(x + rad_ * 0.5, y + rad_ * 0.6, rad_ * 1.05, rad_ * 0.8), sh)
                sk.foliage(cv, x, y - rad_ * 0.5, rad_, r.choice(['#3f8a46', '#4f9a3c', '#357a40']), seed=kk * 2 + side)
        # street lamps at the crossings
        for X in XS:
            for Y in YS:
                x, y = X + RW / 2 + 10, Y + RW / 2 + 10
                if dist_river(x, y) < 140:
                    continue
                cv.drawCircle(x, y, 11, fill('#f8ecc0')); cv.drawCircle(x, y, 11, ink(2.2))
                E.append(dict(kind='lamp', pos=(x, y), r=110, lit=True, ground=y))

    def lights_g(cv, mm):
        pass

    def lights_h(cv, mm):
        sk.draw_emitters(cv, [e for e in E if e['kind'] == 'lamp'], mm, night)
        if night:
            for e in E:
                if e['kind'] == 'point':
                    halo(cv, *e['pos'], 90, mm['key'], 0.18)

    def tilt(fn):
        def painter(cv):
            s_ = surface(1920, 3040)
            c2 = s_.getCanvas(); c2.translate(420, 560)
            fn(c2)
            img = s_.makeImageSnapshot()
            quad = [(-420 + 300, -560 + 160), (1500 - 300, -560 + 160), (1500 + 60, 2480), (-420 - 60, 2480)]
            draw_tex_quad(cv, img, quad)
        return painter

    return [
        ('ground', 1.0, tilt(ground), dict(lights=lights_g)),
        ('houses', 0.93, tilt(houses), dict(lights=lights_h)),
    ], dict(center=(cx, cy))


REGISTRY = {
    'kitchen': kitchen,
    'shop_counter': shop_counter,
    'town_top': town_top,
}


def _registry():
    from . import outdoor
    reg = dict(REGISTRY)
    reg.update(desert_rails=outdoor.desert_rails, street=outdoor.street, field=outdoor.field)
    from . import prehistoric
    reg.update(prehistoric=prehistoric.prehistoric)
    try:
        from . import interiors
        reg.update(interiors.REGISTRY)
    except ImportError:
        pass
    return reg


def build_set(name, mood, cache_dir, **kw):
    reg = _registry()
    spec, meta = reg[name](mood, **kw) if kw else reg[name](mood)
    layers = []
    for lname, z, painter, opts in spec:
        key = '%s|%s|%s|%s' % (name, mood, lname, sorted(kw.items()))
        img = cached(key, lambda: bake_plane(painter, mood, **opts), cache_dir)
        layers.append(Layer(lname, z, img))
    return layers, meta
