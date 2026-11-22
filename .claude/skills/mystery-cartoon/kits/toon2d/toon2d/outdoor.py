"""Outdoor sets built in world metres on a pinhole ground, split into depth bands (one plane each).

Each band = (plane_z, Z_near, Z_far): the plane gets the ground between Z_near and Z_far plus every object
standing in that range, so nearer planes correctly hide farther ones and the camera can fly through.
"""
import math

import skia

from .paint import (fill, stroke, ink, shade, mix, path_poly, path_smooth, rrect, ellipse, blurred, lin_grad,
                    rad_grad, argb, rng, surface, INK)
from . import textures as tx
from . import setkit as sk
from .light import MOODS, halo, pool, god_rays
from .sets import Ground, _track_tile

NIGHT = ('night',)


def _band_painter(G, tiles, objs, z0, z1, fog=None, back=None):
    """tiles: list of (img, tw, td, xr, kw); objs: list of (Z, fn(cv)) -> painter for one band.
    fog=(rgb, max_alpha, depth_px): screen-space gradient toward the horizon, identical in all bands.
    back=(rgb, alpha): backlight shade growing toward the bottom of frame (sunset/dawn)."""
    def paint(cv):
        for img, tw, td, xr, kw in tiles:
            # the ground fill reaches nearer than the band's own range: on deep push-ins the nearer band's
            # plane moves more than this one, and the extra ground hides any gap between them
            G.tile(cv, img, tw, td, xr=xr, zr=(max(0.35, z0 * 0.55), z1), **kw)
        for Z, fn in sorted(objs, key=lambda o: -o[0]):
            if z0 <= Z < z1:
                fn(cv)
        if fog:
            col, a, dpx = fog
            p = skia.Paint(AntiAlias=True)
            p.setShader(lin_grad((0, G.h0 - dpx * 1.2), (0, G.h0), [argb(col, 0), argb(col, a)]))
            p.setBlendMode(skia.BlendMode.kSrcATop)
            cv.drawRect(skia.Rect.MakeLTRB(-700, G.h0 - dpx * 1.2, 1800, G.h0 + 2), p)
            p2 = skia.Paint(AntiAlias=True)
            p2.setShader(lin_grad((0, G.h0), (0, G.h0 + dpx), [argb(col, a), argb(col, 0)]))
            p2.setBlendMode(skia.BlendMode.kSrcATop)
            cv.drawRect(skia.Rect.MakeLTRB(-700, G.h0, 1800, G.h0 + dpx), p2)
        if back:
            col, a = back
            p = skia.Paint(AntiAlias=True)
            p.setShader(lin_grad((0, G.h0 + 120), (0, 2400), [argb(col, 0), argb(col, a)]))
            p.setBlendMode(skia.BlendMode.kSrcATop)
            cv.drawRect(skia.Rect.MakeLTRB(-700, G.h0, 1800, 2600), p)
    return paint


def _sky_band(G, m, **kw):
    def paint(cv):
        sk.sky(cv, m, **kw)
    return paint


# =============================================================================== DESERT / RAILS
def desert_rails(mood):
    m = MOODS[mood]
    night = mood in NIGHT
    vx, h0 = 560, 760
    G = Ground(vx, h0, 1.25)
    r = rng(13)
    E = {'mid': [], 'far': []}
    sand = tx.sand(900, 900, base='#e08c4c', seed=3)
    track = _track_tile()
    tiles = [(sand, 5.0, 5.0, (-400, 400), {}), (track, 3.2, 0.65, (-1.6, 1.6), dict(x0=-1.6, repeat_x=False))]
    objs = []

    # -- hoodoos: tall stacked-rock pillars standing in the desert on the left (no continuous wall)
    def hoodoo(cv, X, Z, hgt, sd):
        x, y = G.proj(X, Z)
        s = G.scale(Z)
        rr = rng(sd)
        segs = rr.randint(3, 5)
        yb = y
        w = 0.55 * hgt * s * rr.uniform(0.8, 1.1)
        cols = ['#c8603a', '#d8784a', '#b8502e', '#e0905a']
        for k in range(segs):
            hh = hgt / segs * s * rr.uniform(0.8, 1.2)
            wt = w * rr.uniform(0.7, 0.95)
            body = path_smooth([(x - w / 2, yb), (x - wt / 2 - 0.1 * s, yb - hh * 0.5), (x - wt / 2, yb - hh),
                                (x + wt / 2, yb - hh), (x + wt / 2 + 0.1 * s, yb - hh * 0.5), (x + w / 2, yb)])
            col = cols[(k + sd) % len(cols)]
            cv.drawPath(body, fill(col))
            cv.save(); cv.clipPath(body, doAntiAlias=True)
            cv.drawRect(skia.Rect.MakeLTRB(x + w * 0.1, yb - hh - 10, x + w, yb + 10), fill(m['shadow'], 0.28))
            cv.drawLine(x - w / 2, yb - hh * 0.35, x + w / 2, yb - hh * 0.4, stroke(shade(col, -0.3), max(1, s * 0.05)))
            cv.restore()
            cv.drawPath(body, ink(max(1.0, min(3.2, s * 0.03))))
            yb -= hh * 0.96
            w = wt
        cap = ellipse(x + 0.1 * s, yb - 0.25 * s, w * 0.9, 0.42 * s)
        cv.drawPath(cap, fill('#8a4a3a')); cv.drawPath(cap, ink(max(1.0, min(3.2, s * 0.03))))
        cv.drawPath(ellipse(x - 0.1 * s, yb - 0.4 * s, w * 0.5, 0.12 * s), fill('#c8805a', 0.7))

    for k, (X, Z, hgt) in enumerate(((-6.0, 10.0, 4.5), (-9.5, 16.0, 6.0), (-6.5, 26.0, 3.5), (-14.0, 34.0, 7.0),
                                     (-9.0, 50.0, 5.0), (-20.0, 64.0, 8.0), (9.0, 75.0, 5.0), (-15.0, 100.0, 6.0))):
        objs.append((Z, lambda cv, X=X, Z=Z, hgt=hgt, sd=k + 3: hoodoo(cv, X, Z, hgt, sd)))

    # cacti and rocks scattered by world coordinates
    for k in range(70):
        X = r.choice([-1, 1]) * r.uniform(2.6, 16)
        Z = 2.0 * (1.08 ** r.uniform(0, 50))
        if r.random() < 0.35:
            def cac(cv, X=X, Z=Z, sd=k):
                x, y = G.proj(X, Z)
                sk.cactus(cv, x, y, 2.2 * G.scale(Z) * rng(sd).uniform(0.5, 1.0) / 2.2 * 1.6, seed=sd)
            objs.append((Z, cac))
        else:
            def rk(cv, X=X, Z=Z, sd=k):
                x, y = G.proj(X, Z)
                sk.rock(cv, x, y, G.scale(Z) * rng(sd).uniform(0.2, 0.9), col=rng(sd).choice(['#b06a4a', '#c98a6a', '#8a4a3a']), seed=sd)
            objs.append((Z, rk))

    def water_tower(cv):
        X, Z = 5.0, 15.0
        x, y = G.proj(X, Z)
        s = G.scale(Z)
        for lx in (-1.4, -0.5, 0.5, 1.4):
            cv.drawLine(x + lx * s, y, x + lx * 0.8 * s, y - 4.2 * s, stroke('#6a4a32', max(2, 0.14 * s))); cv.drawLine(x + lx * s, y, x + lx * 0.8 * s, y - 4.2 * s, ink(1.6, 0.6))
        for hh in (1.4, 2.8):
            cv.drawLine(x - 1.3 * s, y - hh * s, x + 1.3 * s, y - hh * s, stroke('#6a4a32', max(1.5, 0.08 * s)))
        cv.drawLine(x - 1.3 * s, y - 0.2 * s, x + 1.1 * s, y - 2.6 * s, stroke('#6a4a32', max(1.2, 0.06 * s)))
        tank = rrect(x - 1.5 * s, y - 7.4 * s, 3.0 * s, 3.2 * s, 0.2 * s)
        cv.drawPath(tank, fill('#a8683e'))
        for k in range(7):
            cv.drawLine(x - 1.5 * s + k * 0.5 * s, y - 7.4 * s, x - 1.5 * s + k * 0.5 * s, y - 4.2 * s, stroke('#7a4a2a', max(1, 0.04 * s)))
        for hh in (5.0, 6.6):
            cv.drawLine(x - 1.5 * s, y - hh * s, x + 1.5 * s, y - hh * s, stroke('#3a3040', max(1.5, 0.08 * s)))
        cv.drawRect(skia.Rect.MakeLTRB(x + 0.4 * s, y - 7.4 * s, x + 1.5 * s, y - 4.2 * s), fill(m['shadow'], 0.25))
        cv.drawPath(tank, ink(3))
        roof = path_poly([(x - 1.75 * s, y - 7.4 * s), (x, y - 8.6 * s), (x + 1.75 * s, y - 7.4 * s)])
        cv.drawPath(roof, fill('#5a3a3a')); cv.drawPath(roof, ink(3))
        sp = skia.Path(); sp.moveTo(x - 1.5 * s, y - 4.8 * s); sp.lineTo(x - 2.4 * s, y - 4.2 * s); sp.lineTo(x - 2.4 * s, y - 3.4 * s)
        cv.drawPath(sp, stroke('#3a3040', max(2, 0.12 * s)))
    objs.append((15.0, water_tower))
    # mesas at the horizon (far band)
    def far_extra(cv):
        sk.hills(cv, h0 + 14, -600, 1700, 30, mix(m['fog'], '#c8603a', 0.45), seed=2, wav=300)
        sk.mesa(cv, -60, h0 + 22, 560, 250, '#c8603a', seed=5)
        sk.mesa(cv, 1080, h0 + 22, 420, 190, '#bd5634', seed=6)
        sk.mesa(cv, 330, h0 + 24, 240, 110, '#d07048', seed=7, bands=4)
        sk.mesa(cv, 700, h0 + 20, 180, 70, '#d07048', seed=9, bands=3)

    bands = [('ground', 1.0, 0.35, 4.2), ('mid', 3.0, 3.8, 30.0), ('far', 10.0, 26.0, 900.0)]

    def lights(name):
        def f(cv, mm):
            sk.draw_emitters(cv, E.get(name, []), mm, True)
            if name == 'mid' and not night:
                god_rays(cv, (1250, 60), 125, 40, 2400, n=7, col=mm['key'], a=0.13)
        return f

    def sky_glow(cv, mm):
        p = skia.Paint(AntiAlias=True)
        p.setShader(lin_grad((0, h0 - 520), (0, h0 + 20), [argb((255, 200, 150), 0), argb((255, 214, 170), 0.55)]))
        cv.drawRect(skia.Rect.MakeLTRB(-600, h0 - 520, 1700, h0 + 40), p)

    layers = [('sky', 30.0, _sky_band(G, m, seed=4, clouds=8, cloud_band=(-450, 560), cloud_scale=1.4,
                                       sun=(1250, 60, 70) if not night else None,
                                       moon=(840, 160, 60) if night else None, stars=160 if night else 0), dict(grade=False, lights=None if night else sky_glow))]
    for name, pz, z0, z1 in bands:
        ob = list(objs)
        if name == 'far':
            ob.append((899.0, far_extra))
        opts = dict(lights=lights(name))
        if name == 'far':
            opts.update(blur=0.8)
        layers.append((name, pz, _band_painter(G, tiles, ob, z0, z1, fog=('#f4c8a8', 0.38, 220)), opts))

    def near(cv):
        sk.rock(cv, 20, 2120, 520, col='#a8604a', seed=3)
        sk.rock(cv, 1110, 2160, 600, col='#9a5440', seed=4)
        sk.cactus(cv, 1230, 1900, 700, seed=8)
    layers.append(('near', 0.55, near, dict(blur=9)))
    return layers, dict(ground=G, ground_y=1600, h0=h0, vx=vx)


# =============================================================================== STREET (houses, lamps)
def street(mood):
    m = MOODS[mood]
    night = mood in NIGHT
    vx, h0 = 540, 930
    G = Ground(vx, h0, 1.45)
    E = {}
    tiles = [(tx.grass(800, 800, base='#3f7a3f', seed=9), 4, 4, (-400, 400), {}),
             (tx.checker_tiles(600, 600, size=150, c1='#b8b0c0', c2='#a8a0b8', seed=6, gloss=False), 2.4, 2.4, (-5.2, 5.2), {}),
             (tx.bricks(720, 720, bw=120, bh=60, base='#5a5a7a', mortar='#3a3a52', seed=5, ink_a=0.35), 2.4, 2.4, (-2.9, 2.9), {})]
    objs = []

    def curbs(cv):
        for sgn in (-1, 1):
            G.line(cv, sgn * 2.9, 0.4, sgn * 2.9, 900, stroke('#d8d0e0', 9))
            G.line(cv, sgn * 3.05, 0.4, sgn * 3.05, 900, ink(2.6))
            G.line(cv, sgn * 2.75, 0.4, sgn * 2.75, 900, ink(1.8, 0.6))
        z = 2.6
        while z < 300:
            q = [G.proj(-0.06, z), G.proj(0.06, z), G.proj(0.06, z + 1.4), G.proj(-0.06, z + 1.4)]
            cv.drawPath(path_poly(q), fill('#f0d070', 0.9))
            z += 3.5
    for zz in (0.36, 5.9, 39.0):
        objs.append((zz, curbs))   # one per band (drawn first in each band, clipped by the band's ground)

    houses = []
    cols = [('#9fc3c8', '#4f5a8a', '#8a3a3a', '#c8343c'), ('#e8c87a', '#7a4a5a', '#2f5a8a', '#2f8a6a'),
            ('#c8a0c8', '#3f4a7a', '#2f6a5a', '#e8b040'), ('#a8c8a0', '#6a3a4a', '#8a3a3a', '#c8343c'),
            ('#e8a090', '#4f5a8a', '#2f5a8a', '#f2ece0'), ('#d8d0e8', '#5a6a4a', '#7a3a2e', '#2f8a6a')]
    k = 0
    for Z in (7.5, 15, 26, 42, 70, 110):
        for sgn in (-1, 1):
            houses.append((Z + (2.5 if sgn > 0 else 0), sgn, cols[k % len(cols)], k))
            k += 1
    for Z, sgn, (wall, roof, dc, cur), sd in houses:
        def hs(cv, Z=Z, sgn=sgn, wall=wall, roof=roof, dc=dc, cur=cur, sd=sd):
            s = G.scale(Z)
            wm = 8.5
            X = sgn * (6.0 + wm / 2)
            x, y = G.proj(X, Z)
            Ek = E.setdefault(Z, [])
            if sgn < 0:
                sk.house(cv, x - wm * s / 2, y, wm * s, 4.6 * s, wall=wall, roof=roof, door_col=dc, curtain=cur, seed=sd,
                         E=Ek, lit=night, side=0.3)
            else:
                n0 = len(Ek)
                cv.save(); cv.translate(x, 0); cv.scale(-1, 1); cv.translate(-x, 0)
                sk.house(cv, x - wm * s / 2, y, wm * s, 4.6 * s, wall=wall, roof=roof, door_col=dc, curtain=cur, seed=sd,
                         E=Ek, lit=night, side=0.3)
                cv.restore()
                for e in Ek[n0:]:   # mirror emitter coords
                    if e['kind'] == 'window':
                        ex, ey, ew, eh = e['rect']; e['rect'] = (2 * x - ex - ew, ey, ew, eh)
                    elif e['kind'] == 'lamp':
                        e['pos'] = (2 * x - e['pos'][0], e['pos'][1])
                    elif e['kind'] == 'quad':
                        e['quad'] = [(2 * x - qx, qy) for qx, qy in e['quad']]
            # picket fence along the sidewalk edge
            fx0, fy0 = G.proj(sgn * 5.4, Z - 3.0)
            fx1, fy1 = G.proj(sgn * 5.4, Z + 4.5)
            n = 14
            for i in range(n):
                zz = Z - 3.0 + 7.5 * i / (n - 1)
                px, py = G.proj(sgn * 5.4, zz)
                ss = G.scale(zz) / 1000
                pk = path_poly([(px - 6 * ss * 10, py), (px - 6 * ss * 10, py - 90 * ss * 10), (px, py - 104 * ss * 10), (px + 6 * ss * 10, py - 90 * ss * 10), (px + 6 * ss * 10, py)])
                cv.drawPath(pk, fill('#ece6f2')); cv.drawPath(pk, ink(max(1.0, 2.2 * ss * 10)))
            for hh in (0.3, 0.7):
                pts = [(G.proj(sgn * 5.4, Z - 3 + 7.5 * i / 10)[0], G.proj(sgn * 5.4, Z - 3 + 7.5 * i / 10)[1] - hh * 90 * G.scale(Z - 3 + 7.5 * i / 10) / 100) for i in range(11)]
                cv.drawPath(path_poly(pts, close=False), stroke('#c8c0d0', max(2, 6 * G.scale(Z) / 300)))
            sk.foliage(cv, *G.proj(sgn * 5.9, Z - 1.5), 0.9 * G.scale(Z - 1.5), '#3f8a46', seed=sd + 3)
        houses_fn = hs
        objs.append((Z, houses_fn))
    # lamp posts at the curb
    lamps = []
    for k, Z in enumerate((3.2, 11, 21, 34, 55, 90)):
        sgn = 1 if k % 2 == 0 else -1
        def lp(cv, Z=Z, sgn=sgn):
            x, y = G.proj(sgn * 3.4, Z)
            s = G.scale(Z) / 230
            sk.lamp_post(cv, x, y, 600 * s, E=E.setdefault(Z, []), scale=s, lit=night)
        objs.append((Z, lp))
    # hydrants and mailboxes at the curb
    for k, Z in enumerate((4.6, 9.0, 16.5, 29.0, 47.0)):
        sgn = -1 if k % 2 == 0 else 1
        def hyd(cv, Z=Z, sgn=sgn, k=k):
            x, y = G.proj(sgn * 3.6, Z)
            s = G.scale(Z) / 1000
            if k % 2 == 0:
                b = rrect(x - 110 * s, y - 520 * s, 220 * s, 520 * s, 60 * s)
                cv.drawPath(b, fill('#d8483a')); cv.drawPath(rrect(x - 140 * s, y - 440 * s, 280 * s, 70 * s, 20 * s), fill('#b83228'))
                cv.drawPath(ellipse(x, y - 520 * s, 110 * s, 60 * s), fill('#e86a5a'))
                cv.drawPath(b, ink(max(1, 30 * s))); cv.drawPath(rrect(x - 140 * s, y - 440 * s, 280 * s, 70 * s, 20 * s), ink(max(1, 24 * s)))
            else:
                cv.drawPath(rrect(x - 30 * s, y - 900 * s, 60 * s, 900 * s, 10 * s), fill('#6a4a3a')); cv.drawPath(rrect(x - 30 * s, y - 900 * s, 60 * s, 900 * s, 10 * s), ink(max(1, 20 * s)))
                mb = rrect(x - 160 * s, y - 1180 * s, 320 * s, 300 * s, 120 * s)
                cv.drawPath(mb, fill('#3f6ac8')); cv.drawPath(mb, ink(max(1, 26 * s)))
                cv.drawPath(rrect(x + 150 * s, y - 1220 * s, 30 * s, 160 * s, 6 * s), fill('#d8483a'))
        objs.append((Z, hyd))
    # overhead wires between the lamp-side poles
    def wires(cv):
        for sgn in (-1, 1):
            for hh in (5.2, 5.6):
                pts = []
                Z = 3.0
                while Z < 45:
                    x, y = G.proj(sgn * 3.4, Z)
                    pts.append((x, y - hh * G.scale(Z) + 0.25 * G.scale(Z) * ((Z * 7) % 3 == 0)))
                    Z *= 1.25
                cv.drawPath(path_smooth(pts, close=False), stroke('#1c1a3a', 2.2, 0.8))
    objs.append((5.95, wires))
    # trees between houses
    for k in range(12):
        Z = 11 * (1.32 ** k)
        sgn = 1 if k % 2 else -1
        def tr(cv, Z=Z, sgn=sgn, sd=k):
            x, y = G.proj(sgn * 11.5, Z)
            sk.tree(cv, x, y, 7 * G.scale(Z), '#3a7a46', seed=sd)
        objs.append((Z + 3, tr))

    def far_extra(cv):
        sk.hills(cv, h0 + 8, -600, 1700, 70, mix('#2f6a4a', m['fog'], 0.35), seed=4, wav=240)

    bands = [('ground', 1.0, 0.35, 6.0), ('near', 2.2, 5.8, 13.0), ('mid', 5.0, 12.5, 40.0), ('far', 14.0, 38.0, 900.0)]

    def lights(z0, z1):
        def f(cv, mm):
            for Z, es in E.items():
                if z0 <= Z < z1:
                    sk.draw_emitters(cv, es, mm, night)
                    if night:
                        for e in es:
                            if e['kind'] == 'window':
                                ex, ey, ew, eh = e['rect']
                                if ew > 30:
                                    pool(cv, ex + ew / 2, ey + eh * 3.2, ew * 1.6, ew * 0.35, mm['key'], 0.22)
                            if e['kind'] == 'lamp' and e.get('ground') is not None:
                                x, y = e['pos']; gy_ = e['ground']
                                L_ = (gy_ - y) * 1.3
                                p = skia.Paint(AntiAlias=True)
                                p.setShader(lin_grad((x, gy_), (x, gy_ + L_), [argb(mm['key'], 0.55), argb(mm['key'], 0)]))
                                p.setBlendMode(skia.BlendMode.kScreen)
                                blurred(p, max(2, L_ * 0.03))
                                w_ = max(6, L_ * 0.07)
                                cv.drawPath(path_poly([(x - w_, gy_), (x + w_, gy_), (x + w_ * 0.4, gy_ + L_), (x - w_ * 0.4, gy_ + L_)]), p)
        return f

    layers = [('sky', 30.0, _sky_band(G, m, seed=11, clouds=6, cloud_band=(-400, 450), cloud_scale=1.2,
                                       moon=(800, 140, 70) if night else None, stars=240 if night else 0,
                                       cloud_cols=((96, 104, 200), (44, 46, 120)) if night else None), dict(grade=False))]
    for name, pz, z0, z1 in bands:
        ob = [o for o in objs if not (o[1].__name__ == 'curbs' and not (z0 <= o[0] < z1))]
        if name == 'far':
            ob.append((899.0, far_extra))
        opts = dict(lights=lights(z0, z1))
        if name == 'far':
            opts.update(blur=0.8)
        layers.append(('b_' + name, pz, _band_painter(G, tiles, ob, z0, z1, fog=(m['fog'], 0.35, 200)), opts))

    def fg(cv):
        sk.foliage(cv, -40, 2120, 300, '#2f6a3f', seed=3)
        sk.foliage(cv, 1160, 2080, 260, '#356f45', seed=4)
        sk.foliage(cv, -120, -380, 260, '#2a5a3a', seed=5)
        sk.foliage(cv, 60, -470, 200, '#2a5a3a', seed=6)
    layers.append(('fg', 0.55, fg, dict(blur=10)))
    return layers, dict(ground=G, ground_y=1600, h0=h0, vx=vx)


# =============================================================================== FIELD (sunset / dawn ending)
def field(mood):
    """Open meadow: a dirt road that bends away to the left, a lone oak with a rope swing on the right,
    round hay bales, a farmhouse and silo on the far hills, a hot-air balloon, sun low on the right."""
    m = MOODS[mood]
    vx, h0 = 520, 930
    G = Ground(vx, h0, 1.5)
    sun = (860, 860, 130)
    tiles = [(tx.grass(900, 900, base='#b07a48', seed=5, density=1.3, blade=40), 4, 4, (-400, 400), {})]
    objs = []

    def road_x(Z):
        return 0.6 - 5.5 * (1 - math.exp(-max(Z - 2.0, 0) / 14.0))

    def road(z0, z1):
        def paint(cv):
            zs = []
            z = max(z0, 0.4)
            while z < z1:
                zs.append(z)
                z *= 1.06
            zs.append(z1)
            left = [G.proj(road_x(z) - 1.6, z) for z in zs]
            right = [G.proj(road_x(z) + 1.6, z) for z in zs]
            cv.drawPath(path_poly(left + right[::-1]), fill('#e4a46a'))
            for off in (-0.7, 0.7):
                pts = [G.proj(road_x(z) + off, z) for z in zs]
                cv.drawPath(path_poly(pts, close=False), stroke('#b87040', max(2, 16), 0.4))
            for side in (left, right):
                cv.drawPath(path_poly(side, close=False), stroke('#8a5a3a', 3, 0.6))
        return paint
    for (zz, a, b) in ((0.36, 0.35, 6.4), (6.1, 6.0, 42.0), (40.0, 40.0, 900.0)):
        fn = road(a, b)
        fn.__name__ = 'road'
        objs.append((zz, fn))

    def off_road(X, Z, margin=2.4):
        return abs(X - road_x(Z)) > margin

    # lone oak with a rope swing
    def oak(cv):
        X, Z = 4.6, 8.5
        x, y = G.proj(X, Z)
        s = G.scale(Z)
        trunk = path_poly([(x - 0.45 * s, y), (x - 0.3 * s, y - 3.4 * s), (x + 0.3 * s, y - 3.4 * s), (x + 0.5 * s, y)])
        cv.drawPath(trunk, fill('#6a3a3a')); cv.drawPath(trunk, ink(3))
        br = path_poly([(x - 0.2 * s, y - 3.0 * s), (x - 2.4 * s, y - 4.0 * s), (x - 2.3 * s, y - 4.25 * s), (x - 0.1 * s, y - 3.4 * s)])
        cv.drawPath(br, fill('#6a3a3a')); cv.drawPath(br, ink(2.6))
        sx0 = x - 1.9 * s
        for dx in (-0.35, 0.35):
            cv.drawLine(sx0 + dx * s, y - 3.95 * s, sx0 + dx * s, y - 0.9 * s, stroke('#e8d0a0', max(1.5, 0.04 * s)))
        cv.drawPath(rrect(sx0 - 0.5 * s, y - 0.95 * s, 1.0 * s, 0.14 * s, 3), fill('#8a5a3a')); cv.drawPath(rrect(sx0 - 0.5 * s, y - 0.95 * s, 1.0 * s, 0.14 * s, 3), ink(2))
        for (dx, dy, rad, col) in ((-1.6, -5.0, 2.0, '#6a7a3a'), (1.2, -5.4, 2.2, '#5a6a34'), (0.0, -6.4, 2.4, '#7a8a42'), (-0.6, -4.6, 1.6, '#6a7a3a')):
            sk.foliage(cv, x + dx * s, y + dy * s, rad * s, col, seed=int(dx * 10 + 50), ink_w=3)
        sp = fill('#2a1440', 0.45); blurred(sp, 20)
        cv.drawPath(ellipse(x - 1.5 * s, y + 0.05 * s, 3.4 * s, 0.35 * s), sp)
    objs.append((8.5, oak))

    # round hay bales on the left
    for k, (X, Z) in enumerate(((-3.6, 4.2), (-5.4, 6.0), (-4.2, 11.0), (-8.0, 15.0), (-6.0, 24.0), (3.6, 30.0))):
        def bale(cv, X=X, Z=Z, sd=k):
            x, y = G.proj(X, Z)
            s = G.scale(Z)
            R = 0.75 * s
            body = rrect(x - 0.9 * s, y - 2 * R, 1.8 * s, 2 * R, R * 0.4)
            cv.drawPath(body, fill('#e0a85a'))
            cv.drawPath(ellipse(x + 0.9 * s - R * 0.35, y - R, R * 0.35, R), fill('#f0c070'))
            for j in range(4):
                cv.drawPath(ellipse(x + 0.9 * s - R * 0.35, y - R, R * 0.35 * (1 - j * 0.22), R * (1 - j * 0.22)), stroke('#b8783a', max(1, 0.03 * s)))
            for j in range(5):
                cv.drawLine(x - 0.7 * s + j * 0.3 * s, y - 2 * R + 4, x - 0.7 * s + j * 0.3 * s, y - 4, stroke('#c8883e', max(1, 0.02 * s), 0.6))
            cv.drawPath(body, ink(max(1, min(3, 0.04 * s))))
            sp = fill('#2a1440', 0.4); blurred(sp, max(1, 0.1 * s))
            cv.drawPath(ellipse(x - 0.9 * s, y, 1.3 * s, 0.2 * s), sp)
        objs.append((Z, bale))

    r = rng(9)
    for k in range(110):
        Z = 2.0 * (1.05 ** r.uniform(0, 80))
        X = r.choice([-1, 1]) * r.uniform(3.2, 30)
        if not off_road(X, Z, 2.6):
            continue
        def bush(cv, X=X, Z=Z, sd=k):
            x, y = G.proj(X, Z)
            sk.foliage(cv, x, y - 0.25 * G.scale(Z), 0.55 * G.scale(Z), rng(sd).choice(['#8a6a3a', '#9a5a4a', '#7a6a3a']), seed=sd,
                       ink_w=max(0.6, 3 * min(1, G.scale(Z) / 300)), lumps=5)
        objs.append((Z, bush))
    for k in range(400):
        Z = 3.0 * (1.03 ** r.uniform(0, 140))
        X = r.choice([-1, 1]) * r.uniform(2.0, 40)
        if not off_road(X, Z, 2.0):
            continue
        def wheat(cv, X=X, Z=Z, sd=k):
            x, y = G.proj(X, Z)
            L = 0.7 * G.scale(Z)
            rr = rng(sd)
            cv.drawLine(x, y, x + rr.uniform(-0.1, 0.1) * L, y - L, stroke(rr.choice(['#e8b060', '#f0c878', '#d89a50']), max(1, L / 40)))
            cv.drawPath(ellipse(x, y - L, L / 18 + 1, L / 7 + 1), fill('#f4c878'))
        objs.append((Z, wheat))

    def sky(cv):
        top, mid, bot = m['sky']
        p = skia.Paint(AntiAlias=True)
        p.setShader(lin_grad((0, -700), (0, 1000), [argb(top), argb(mid), argb(bot), argb(mix(bot, (255, 236, 180), 0.6))], [0, 0.45, 0.85, 1]))
        cv.drawRect(skia.Rect.MakeLTRB(-600, -800, 1700, 1400), p)
        sx, sy, sr = sun
        sp = skia.Paint(AntiAlias=True)
        sp.setShader(rad_grad((sx, sy), sr * 5, [argb((255, 236, 170), 0.9), argb((255, 180, 110), 0.35), argb((255, 160, 120), 0)], [0.18, 0.45, 1]))
        cv.drawCircle(sx, sy, sr * 5, sp)
        cv.drawCircle(sx, sy, sr, fill('#fff2c8'))
        rr = rng(16)
        for k in range(8):                                  # puffy cumulus with lit undersides (no long streaks)
            x, y = rr.uniform(-300, 1300), rr.uniform(-420, 600)
            w = rr.uniform(220, 420)
            d = 1 - (y + 420) / 1020
            body = mix('#6a4a9a', '#e07a9a', 1 - d)
            lit = mix('#ffa070', '#ffe090', 1 - d)
            sk.cloud(cv, x, y, w, lit, body, seed=k)
        # hot-air balloon
        bx, by = 250, 260
        env = path_smooth([(bx - 90, by - 10), (bx - 70, by - 120), (bx, by - 150), (bx + 70, by - 120), (bx + 90, by - 10), (bx + 30, by + 80), (bx - 30, by + 80)])
        cv.drawPath(env, fill('#e0a83a'))
        cv.save(); cv.clipPath(env, doAntiAlias=True)
        for k in range(-2, 3, 2):
            cv.drawPath(ellipse(bx + k * 36, by - 20, 18, 140), fill('#c8343c'))
        cv.drawRect(skia.Rect.MakeLTRB(bx + 20, by - 160, bx + 100, by + 90), fill('#4a2a6a', 0.25))
        cv.restore()
        cv.drawPath(env, ink(3))
        for dx in (-26, 26):
            cv.drawLine(bx + dx, by + 76, bx + dx * 0.6, by + 120, stroke('#3a2a4a', 2))
        cv.drawPath(rrect(bx - 22, by + 118, 44, 34, 6), fill('#8a5a3a')); cv.drawPath(rrect(bx - 22, by + 118, 44, 34, 6), ink(2.6))
        for k in range(5):
            bx2, by2 = 700 + k * 28 + rr.uniform(-8, 8), 300 + rr.uniform(-30, 30)
            p2 = skia.Path(); p2.moveTo(bx2 - 10, by2); p2.quadTo(bx2 - 5, by2 - 6, bx2, by2); p2.quadTo(bx2 + 5, by2 - 6, bx2 + 10, by2)
            cv.drawPath(p2, stroke('#3a2a4a', 2.5))

    def far_extra(cv):
        sk.hills(cv, h0 + 10, -600, 1700, 110, '#7a4a7a', seed=18, wav=380)
        sk.hills(cv, h0 + 30, -600, 1700, 50, '#8a5a6a', seed=19, wav=240)
        # farmhouse + silo on the left hill
        fx, fy = 150, h0 - 40
        cv.drawRect(skia.Rect.MakeXYWH(fx - 70, fy - 60, 140, 70), fill('#5a3a6a'))
        cv.drawPath(path_poly([(fx - 84, fy - 58), (fx, fy - 120), (fx + 84, fy - 58)]), fill('#4a2a5a'))
        for k in range(3):
            cv.drawRect(skia.Rect.MakeXYWH(fx - 50 + k * 40, fy - 40, 16, 18), fill('#f8d080'))
        cv.drawPath(rrect(fx + 90, fy - 150, 52, 160, 6), fill('#5a3a6a'))
        cv.drawPath(ellipse(fx + 116, fy - 150, 26, 22), fill('#4a2a5a'))
        rr = rng(13)
        for k in range(14):
            x = rr.uniform(-300, 1400)
            if abs(x - vx) < 80:
                continue
            sk.foliage(cv, x, h0 + 6, rr.uniform(22, 46), '#5a3a6a', seed=k + 40, ink_w=0)

    bands = [('ground', 1.0, 0.35, 6.4), ('mid', 4.0, 6.0, 42.0), ('far', 14.0, 40.0, 900.0)]

    def lights_sky(cv, mm):
        god_rays(cv, sun[:2], -90, 300, 1900, n=16, col=(255, 230, 170), a=0.16, width=0.9)

    def glow(cv, mm):
        # low sun glow, screen-blended; it fades in over 160 px above the horizon instead of starting at a hard edge
        # (a hard top edge showed as a haze band across the oak on every parallax band)
        lp = skia.Paint()
        lp.setBlendMode(skia.BlendMode.kScreen)
        cv.saveLayer(None, lp)
        p = skia.Paint(AntiAlias=True)
        p.setShader(rad_grad((sun[0], h0), 900, [argb((255, 214, 150), 0.42), argb((255, 190, 150), 0.08), argb((255, 190, 150), 0)], [0, 0.5, 1]))
        cv.drawRect(skia.Rect.MakeLTRB(-600, h0 - 120, 1700, 2600), p)
        m_ = skia.Paint(AntiAlias=True)
        m_.setShader(lin_grad((0, h0 - 120), (0, h0 + 40), [argb((255, 255, 255), 0), argb((255, 255, 255), 1)]))
        m_.setBlendMode(skia.BlendMode.kDstIn)
        cv.drawRect(skia.Rect.MakeLTRB(-600, h0 - 120, 1700, h0 + 40), m_)
        cv.restore()

    layers = [('sky', 30.0, sky, dict(grade=False, lights=lights_sky))]
    for name, pz, z0, z1 in bands:
        ob = [o for o in objs if not (o[1].__name__ == 'road' and not (z0 <= o[0] < z1))]
        if name == 'far':
            ob.append((899.0, far_extra))
        opts = dict(lights=glow)
        if name == 'far':
            opts.update(blur=0.8)
        layers.append((name, pz, _band_painter(G, tiles, ob, z0, z1, fog=('#f0a8a0', 0.4, 180), back=('#2e1a44', 0.78)), opts))

    def near(cv):
        rr = rng(12)
        for k in range(70):
            x = rr.choice([rr.uniform(-300, 200), rr.uniform(900, 1400)])
            y = rr.uniform(1900, 2500)
            L = rr.uniform(200, 460)
            cv.drawPath(path_poly([(x - 9, y), (x + rr.uniform(-90, 90), y - L), (x + 9, y)]), fill(rr.choice(['#5a3a4a', '#6a4250', '#4a2e40'])))
        for k in range(26):
            x, y = rr.choice([rr.uniform(-250, 160), rr.uniform(940, 1350)]), rr.uniform(2050, 2450)
            cv.drawLine(x, y, x + rr.uniform(-20, 20), y - 150, stroke('#3a2a3a', 8))
            for j in range(5):
                a_ = j * 1.256
                cv.drawCircle(x + math.cos(a_) * 26, y - 160 + math.sin(a_) * 26, 22, fill(rr.choice(['#f2b632', '#e86a8a', '#f4f0e8'])))
            cv.drawCircle(x, y - 160, 14, fill('#7a3a2a'))
    layers.append(('near', 0.55, near, dict(blur=10)))
    return layers, dict(ground=G, ground_y=1600, h0=h0, vx=vx, sun=sun)
