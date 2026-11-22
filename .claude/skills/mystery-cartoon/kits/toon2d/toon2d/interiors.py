"""More sets: planet shop, office, castle hall, ship deck. Same plane conventions as sets.py."""
import math

import skia

from .paint import (fill, stroke, ink, shade, mix, path_poly, path_smooth, rrect, ellipse, blurred, lin_grad, rad_grad,
                    argb, rng, surface, draw_tex_quad, draw_in_quad, INK)
from . import textures as tx
from . import setkit as sk
from . import props as pr
from .light import MOODS, halo, pool, god_rays, window_slash
from .text import draw_text

NIGHT = ('night',)


def room_box(cv, back, vp_floor=None, back_tex=None, left_tex=None, right_tex=None, floor_tex=None, ceil_tex=None,
             right_shade=0.18, left_shade=0.1):
    """Paint a perspective room: back wall rect + 4 receding planes to the frame edges (and beyond)."""
    x0, y0, x1, y1 = back
    E_ = (-900, -1000, 1980, 3300)
    ceil = [(E_[0], E_[1]), (E_[2], E_[1]), (x1, y0), (x0, y0)]
    lw = [(E_[0], E_[1]), (x0, y0), (x0, y1), (E_[0], E_[3])]
    rw = [(x1, y0), (E_[2], E_[1]), (E_[2], E_[3]), (x1, y1)]
    fl = [(x0, y1), (x1, y1), (E_[2], E_[3]), (E_[0], E_[3])]
    for q, t, sh in ((ceil, ceil_tex, 0.0), (lw, left_tex, left_shade), (rw, right_tex, right_shade), (fl, floor_tex, 0.0)):
        if t is not None:
            draw_tex_quad(cv, t, q)
        if sh:
            cv.drawPath(path_poly(q), fill('#4a2e66', sh))
        cv.drawPath(path_poly(q), ink(3, 0.6))
    if back_tex is not None:
        cv.drawImageRect(back_tex, skia.Rect.MakeLTRB(x0, y0, x1, y1))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), ink(3.5))
    return dict(ceil=ceil, lw=lw, rw=rw, fl=fl)


# =============================================================================== PLANET SHOP
def planet_shop(mood):
    m = MOODS[mood]
    night = mood in NIGHT
    E = {'back': [], 'counter': []}
    back = (40, 180, 1040, 1160)

    def wall(cv):
        room_box(cv, back,
                 back_tex=tx.wood_planks(1000, 980, plank=120, base='#5a3a6a', vertical=True, seed=3, nails=False),
                 left_tex=tx.wallpaper(1200, 1600, base='#4a3a7a', motif='#f2c640', stripe='#54428a'),
                 right_tex=tx.wallpaper(1200, 1600, base='#4a3a7a', motif='#f2c640', stripe='#54428a'),
                 floor_tex=tx.checker_tiles(1400, 1400, size=140, c1='#e8e0d0', c2='#3a3a6a'),
                 ceil_tex=tx.ceiling_tiles(1400, 1200, size=170, base='#d8d0e0'))
        # star sign on the back wall
        pr.sign_board(cv, 540, 330, 'PLANETS', s=1.0, col='#2a2a5a', txt='#f2c640', post=False)
        for k in range(14):
            a = k / 14 * 2 * math.pi
            cv.drawCircle(540 + math.cos(a) * 330, 270 + math.sin(a) * 70, 7, fill('#f8e8a0'))
            E['back'].append(dict(kind='lamp', pos=(540 + math.cos(a) * 330, 270 + math.sin(a) * 70), r=40, lit=True))
        # shelves with planets and price tags
        kinds = ['gas', 'red', 'ringed', 'moon', 'purple', 'shiny', 'gas', 'moon', 'red', 'ringed', 'shiny', 'purple']
        r = rng(4)
        k = 0
        for row in range(3):
            y = 600 + row * 230
            cv.drawPath(rrect(60, y, 960, 26, 4), fill('#8a5a3a')); cv.drawPath(rrect(60, y, 960, 26, 4), ink(3.5))
            cv.drawRect(skia.Rect.MakeLTRB(60, y + 26, 1020, y + 40), fill('#2a1e30', 0.35))
            for j in range(4):
                x = 170 + j * 245 + r.uniform(-20, 20)
                rad = r.uniform(58, 82)
                kind = kinds[k % len(kinds)]; k += 1
                cv.drawPath(ellipse(x, y + 4, rad * 0.8, 12), fill('#2a1e30', 0.35))
                pr.planet_kind(cv, x, y - rad - 4, rad, kind, seed=k)
                pr.price_tag(cv, x + rad * 0.7, y + 60, r.choice(['$900', '$1200', '$75', '$480', '$2000', '$310']), s=0.42, angle=r.uniform(-12, 8))
        # hanging pendant lamps
        for lx in (230, 850):
            cv.drawLine(lx, -400, lx, 120, stroke('#2a2232', 5))
            sh = path_poly([(lx - 70, 170), (lx + 70, 170), (lx + 40, 110), (lx - 40, 110)])
            cv.drawPath(sh, fill('#2f8a8a')); cv.drawPath(sh, ink(3.5))
            cv.drawPath(ellipse(lx, 172, 70, 12), fill('#f8ecc0'))
            E['back'].append(dict(kind='lamp', pos=(lx, 176), r=230, lit=True, ground=None))

    def counter(cv):
        top = 1330
        draw_tex_quad(cv, tx.wood_planks(2400, 600, plank=110, base='#b0703e', seed=9), [(-240, 1150), (1320, 1150), (1600, top), (-520, top)])
        cv.drawLine(-520, top, 1600, top, ink(4))
        cv.drawImage(tx.wood_planks(2400, 1300, plank=140, base='#7a3e26', vertical=True, seed=10), -600, top)
        cv.drawRect(skia.Rect.MakeLTRB(-600, top, 1700, top + 30), fill('#5a2a1e')); cv.drawLine(-600, top + 30, 1700, top + 30, ink(4))
        for k in range(6):
            x = -300 + k * 300
            cv.drawPath(rrect(x, top + 90, 240, 420, 14), stroke(shade('#7a3e26', -0.35), 6))
        pr.register(cv, 830, 1300, s=0.95, display='0.99', E=E['counter'])
        # Earth on a little stand with its price tag
        cv.drawPath(path_poly([(250, 1290), (350, 1290), (330, 1250), (270, 1250)]), fill('#c8a050')); cv.drawPath(path_poly([(250, 1290), (350, 1290), (330, 1250), (270, 1250)]), ink(3.5))
        pr.planet_kind(cv, 300, 1160, 96, 'earth', seed=2)
        pr.price_tag(cv, 450, 1255, '99¢', s=0.75, angle=-10)
        # bell and a jar of moons
        cv.drawPath(ellipse(620, 1288, 40, 10), fill('#8a6a3a'))
        bell = path_smooth([(586, 1286), (590, 1250), (620, 1236), (650, 1250), (654, 1286)])
        cv.drawPath(bell, fill('#e6c25a')); cv.drawPath(bell, ink(3))
        if night:
            # desk lamp practical
            cv.drawLine(80, 1290, 120, 1100, stroke('#2a2232', 9)); cv.drawLine(120, 1100, 60, 1040, stroke('#2a2232', 9))
            lp = path_poly([(10, 1030), (110, 1000), (100, 1060), (40, 1080)])
            cv.drawPath(lp, fill('#2f8a6a')); cv.drawPath(lp, ink(3))
            E['counter'].append(dict(kind='lamp', pos=(60, 1080), r=420, lit=True, ground=1290))

    def near(cv):
        pr.planet_kind(cv, -40, 2050, 260, 'purple', seed=9)
        pr.planet_kind(cv, 1150, 2150, 220, 'moon', seed=3)

    def L(key, extra=None):
        def f(cv, mm):
            for e in E[key]:
                if e['kind'] == 'glowrect':
                    x, y, w, h = e['rect']
                    halo(cv, x + w / 2, y + h / 2, w * 0.9, e['col'], 0.16, core=0.6, hot=False)
            if key == 'counter' and mood == 'golden':
                for (gx, gy_, gr) in ((300, 1160, 520), (450, 1255, 360)):
                    p = skia.Paint(AntiAlias=True)
                    p.setShader(rad_grad((gx, gy_), gr, [argb((255, 214, 120), 0.55), argb((255, 190, 90), 0.18), argb((255, 190, 90), 0)], [0, 0.45, 1]))
                    p.setBlendMode(skia.BlendMode.kScreen)
                    cv.drawCircle(gx, gy_, gr, p)
                god_rays(cv, (300, 1160), -90, 360, 900, n=18, col=(255, 226, 150), a=0.18, width=0.7)
                rr = rng(11)
                for k in range(40):
                    halo(cv, rr.uniform(60, 760), rr.uniform(900, 1420), rr.uniform(8, 22), (255, 236, 170), 0.8)
            sk.draw_emitters(cv, [e for e in E[key] if e['kind'] != 'glowrect'], mm, night or key == 'back')
            if extra:
                extra(cv, mm)
        return f

    def rays(cv, mm):
        god_rays(cv, (230, 176), 80, 50, 1300, n=6, col=mm['key'], a=0.14)
        god_rays(cv, (850, 176), 100, 50, 1300, n=6, col=mm['key'], a=0.14, seed=5)

    return [
        ('wall', 1.7, wall, dict(lights=L('back', rays), blur=0.6)),
        ('counter', 1.0, counter, dict(lights=L('counter'))),
        ('near', 0.58, near, dict(blur=12)),
    ], dict(ground_y=1330, earth=(300, 1160), register=(830, 1300))


# =============================================================================== OFFICE
def office(mood):
    m = MOODS[mood]
    night = mood in NIGHT
    E = []
    back = (-40, 260, 820, 1240)

    def room(cv):
        room_box(cv, back,
                 back_tex=tx.bricks(860, 980, bw=110, bh=56, base='#c9b79a', mortar='#a8987e', seed=4, ink_a=0.3),
                 left_tex=tx.bricks(1200, 1600, bw=110, bh=56, base='#c9b79a', mortar='#a8987e', seed=5, ink_a=0.3),
                 right_tex=tx.wood_planks(1200, 1600, plank=140, base='#8a5a3a', vertical=True, seed=6, nails=False),
                 floor_tex=tx.checker_tiles(1400, 1400, size=200, c1='#6e6862', c2='#7a746c', gloss=False),
                 ceil_tex=tx.ceiling_tiles(1400, 1200, size=160))
        # window with blinds (noir slash source)
        wx, wy, ww, wh = 40, 420, 360, 420
        sv = surface(ww, wh); sc = sv.getCanvas()
        sk.sky(sc, MOODS['day'] if not night else m, x0=0, y0=0, x1=ww, y1=wh, clouds=2, seed=5, cloud_band=(40, 120), cloud_scale=0.5)
        for k in range(5):
            bh_ = 140 + k * 40
            sc.drawRect(skia.Rect.MakeXYWH(k * 76, wh - bh_, 70, bh_), fill('#6a7aa8'))
            for j in range(int(bh_ / 30)):
                sc.drawRect(skia.Rect.MakeXYWH(k * 76 + 12, wh - bh_ + 12 + j * 30, 14, 12), fill('#f8e8a0' if night else '#bcd8f0'))
        cv.drawImage(sv.makeImageSnapshot(), wx, wy)
        for k in range(14):
            cv.drawRect(skia.Rect.MakeXYWH(wx, wy + k * 30, ww, 13), fill('#f0ece0', 0.92))
            cv.drawLine(wx, wy + k * 30 + 13, wx + ww, wy + k * 30 + 13, stroke('#b8b0a0', 2))
        cv.drawRect(skia.Rect.MakeXYWH(wx - 10, wy - 10, ww + 20, wh + 20), stroke('#f4f0e8', 16)); cv.drawRect(skia.Rect.MakeXYWH(wx - 18, wy - 18, ww + 36, wh + 36), ink(3))
        # in-world counter sign + framed portrait + clock + filing cabinet + plant
        # sales chart on an easel-style board (bars climbing, then one that drops)
        cv.drawPath(rrect(460, 320, 250, 210, 8), fill('#f4f0e8')); cv.drawPath(rrect(460, 320, 250, 210, 8), ink(4))
        for k, (hh, col) in enumerate(((50, '#3f6ac8'), (80, '#3f6ac8'), (115, '#3f6ac8'), (150, '#2f9a5a'), (40, '#d8483a'))):
            cv.drawRect(skia.Rect.MakeXYWH(485 + k * 44, 500 - hh, 30, hh), fill(col)); cv.drawRect(skia.Rect.MakeXYWH(485 + k * 44, 500 - hh, 30, hh), ink(2))
        cv.drawLine(478, 502, 695, 502, ink(3)); cv.drawLine(478, 340, 478, 502, ink(3))
        # cork board with pinned notes
        cv.drawPath(rrect(470, 580, 240, 200, 8), fill('#c8965a')); cv.drawPath(rrect(470, 580, 240, 200, 8), ink(4))
        for k, (nx, ny, nc) in enumerate(((490, 600, '#f8e070'), (590, 610, '#a8d8f0'), (510, 690, '#f8a0c0'), (610, 700, '#f4f0e8'))):
            cv.drawRect(skia.Rect.MakeXYWH(nx, ny, 76, 62), fill(nc)); cv.drawRect(skia.Rect.MakeXYWH(nx, ny, 76, 62), ink(2))
            for j in range(3):
                cv.drawLine(nx + 10, ny + 20 + j * 12, nx + 60 - j * 8, ny + 20 + j * 12, stroke('#6a6a7a', 2))
            cv.drawCircle(nx + 38, ny + 6, 6, fill(['#d8483a', '#3f6ac8', '#2f9a5a', '#e6b43c'][k]))
        sk.wall_clock(cv, 270, 330, 58)
        for k in range(3):
            y = 900 + k * 110
            cv.drawPath(rrect(600, y, 210, 104, 6), fill('#9aa2b4')); cv.drawPath(rrect(600, y, 210, 104, 6), ink(3))
            cv.drawPath(rrect(670, y + 40, 70, 18, 6), fill('#5a6278'))
        sk.plant_pot(cv, 120, 1230, 1.5)
        # ceiling light panels
        for k in range(2):
            q = [(150 + k * 420, 100), (430 + k * 420, 100), (470 + k * 420, 40), (110 + k * 420, 40)]
            cv.drawPath(path_poly(q), fill('#f8f8f0')); cv.drawPath(path_poly(q), ink(2.5))
            E.append(dict(kind='lamp', pos=(290 + k * 420, 80), r=320, lit=True, ground=None))

    def desk(cv):
        top = 1420
        draw_tex_quad(cv, tx.wood_planks(2000, 500, plank=120, base='#9a6238', seed=7, nails=False), [(-100, 1260), (1180, 1260), (1400, top), (-320, top)])
        cv.drawLine(-320, top, 1400, top, ink(4))
        cv.drawRect(skia.Rect.MakeLTRB(-320, top, 1400, top + 40), fill('#6a3a22')); cv.drawLine(-320, top + 40, 1400, top + 40, ink(4))
        cv.drawImage(tx.wood_planks(1800, 1000, plank=160, base='#7a4428', vertical=True, seed=8, nails=False), -320, top + 40)
        # monitor, keyboard, mug, papers, nameplate
        cv.drawPath(rrect(640, 1000, 360, 260, 18), fill('#3a3a4e')); cv.drawPath(rrect(640, 1000, 360, 260, 18), ink(4))
        cv.drawPath(rrect(660, 1020, 320, 210, 8), fill('#5aa0e0'))
        for k in range(5):
            cv.drawLine(690, 1060 + k * 30, 900 - (k % 2) * 60, 1060 + k * 30, stroke('#e8f4ff', 8))
        E.append(dict(kind='glowrect', rect=(660, 1020, 320, 210), col=(140, 200, 255)))
        cv.drawPath(path_poly([(790, 1260), (850, 1260), (870, 1320), (770, 1320)]), fill('#3a3a4e')); cv.drawPath(path_poly([(790, 1260), (850, 1260), (870, 1320), (770, 1320)]), ink(3))
        cv.drawPath(rrect(80, 1340, 360, 60, 10), fill('#e8e4dc')); cv.drawPath(rrect(80, 1340, 360, 60, 10), ink(3))
        for k in range(12):
            cv.drawRect(skia.Rect.MakeXYWH(96 + k * 28, 1352, 20, 14), fill('#c8c4bc'))
        cv.drawPath(rrect(480, 1330, 220, 70, 8), fill('#2a2232')); draw_text(cv, 'MANAGER', 590, 1378, 34, '#e6c25a')
        cv.save(); cv.rotate(-6)
        cv.drawPath(rrect(-40, 1300, 200, 120, 4), fill('#f8f4ec')); cv.drawPath(rrect(-40, 1300, 200, 120, 4), ink(3))
        cv.restore()
        cv.drawPath(path_smooth([(1060, 1330), (1120, 1330), (1130, 1360), (1050, 1360)]), fill('#c8343c'))
        # brass desk bell + rubber stamp on its pad
        cv.drawPath(ellipse(1010, 1404, 90, 22), fill('#3a2a30')); cv.drawPath(ellipse(1010, 1404, 90, 22), ink(4))
        bell = skia.Path(); bell.moveTo(940, 1398); bell.quadTo(942, 1320, 1010, 1316); bell.quadTo(1078, 1320, 1080, 1398); bell.close()
        cv.drawPath(bell, fill('#e6b43c')); cv.drawPath(path_smooth([(962, 1380), (968, 1340), (990, 1328)], close=False), stroke('#fff0b0', 8, 0.7))
        cv.drawPath(bell, ink(4))
        cv.drawPath(rrect(1000, 1290, 20, 28, 6), fill('#b8802a')); cv.drawPath(rrect(1000, 1290, 20, 28, 6), ink(3))
        cv.drawPath(rrect(860, 1380, 70, 24, 4), fill('#2f4ab0')); cv.drawPath(rrect(860, 1380, 70, 24, 4), ink(2.6))
        cv.drawPath(rrect(878, 1330, 34, 52, 6), fill('#8a5a3a')); cv.drawPath(rrect(878, 1330, 34, 52, 6), ink(2.6))
        cv.drawCircle(895, 1324, 16, fill('#c8343c')); cv.drawCircle(895, 1324, 16, ink(2.6))

    def lights_room(cv, mm):
        sk.draw_emitters(cv, [e for e in E if e['kind'] == 'lamp'], mm, True)
        # venetian blind stripes across the floor and right wall
        for k in range(9):
            y = 1500 + k * 70
            window_slash(cv, [(60, y), (700, y - 80), (760, y - 40), (90, y + 36)], mm['key'], 0.22 if not night else 0.12)

    def lights_desk(cv, mm):
        for e in E:
            if e['kind'] == 'glowrect':
                x, y, w, h = e['rect']
                halo(cv, x + w / 2, y + h / 2, w * 0.9, e['col'], 0.3, core=0.45, hot=False)

    return [
        ('room', 1.4, room, dict(lights=lights_room)),
        ('desk', 1.0, desk, dict(lights=lights_desk)),
    ], dict(ground_y=1300, bell=(1010, 1360))


# =============================================================================== CASTLE HALL
def castle_hall(mood):
    m = MOODS[mood]
    E = []
    back = (140, 120, 940, 1250)

    def hall(cv):
        stone = tx.stone_blocks(1200, 1600, bw=170, bh=95, base='#a8a4b4', seed=3)
        room_box(cv, back, back_tex=tx.stone_blocks(800, 1130, bw=150, bh=86, base='#b0acbc', seed=2),
                 left_tex=stone, right_tex=stone,
                 floor_tex=tx.checker_tiles(1400, 1400, size=200, c1='#8a8496', c2='#6a6478', gloss=True),
                 ceil_tex=tx.wood_planks(1400, 1000, plank=150, base='#6a4a3a', seed=4))
        # three tall lancet windows (emitters) with clear leaded glass
        rx, ry = 540, 330
        for k, (lx, top, w) in enumerate(((420, 250, 80), (540, 200, 96), (660, 250, 80))):
            lan = skia.Path(); lan.moveTo(lx - w / 2, 620); lan.lineTo(lx - w / 2, top + w * 0.6)
            lan.quadTo(lx - w / 2, top + 10, lx, top - 20); lan.quadTo(lx + w / 2, top + 10, lx + w / 2, top + w * 0.6); lan.lineTo(lx + w / 2, 620); lan.close()
            cv.drawPath(lan, fill('#cfe6f0'))
            cv.save(); cv.clipPath(lan, doAntiAlias=True)
            cv.drawRect(skia.Rect.MakeLTRB(lx - w / 2, 480, lx + w / 2, 620), fill('#9ccad8'))
            for j in range(12):
                cv.drawLine(lx - w, top + j * 40, lx + w, top + j * 40 + 40, stroke('#7a8a9a', 2.4))
                cv.drawLine(lx + w, top + j * 40, lx - w, top + j * 40 + 40, stroke('#7a8a9a', 2.4))
            cv.restore()
            cv.drawPath(lan, stroke('#d0ccd8', 14)); cv.drawPath(lan, ink(4))
        E.append(dict(kind='rose', pos=(rx, ry)))
        for cx_ in (200, 880):
            cv.drawPath(rrect(cx_ - 50, 420, 100, 830, 10), fill('#c8c4d0')); cv.drawPath(rrect(cx_ - 50, 420, 100, 830, 10), ink(4))
            for k in range(6):
                cv.drawLine(cx_ - 30 + k * 12, 440, cx_ - 30 + k * 12, 1230, stroke('#9a96a8', 3))
            cv.drawPath(rrect(cx_ - 70, 400, 140, 40, 6), fill('#b0acbc')); cv.drawPath(rrect(cx_ - 70, 400, 140, 40, 6), ink(4))
        arch = skia.Path(); arch.addArc(skia.Rect.MakeLTRB(200, 160, 880, 840), 180, 180)
        cv.drawPath(arch, stroke('#d0ccd8', 40)); cv.drawPath(arch, ink(4))
        # swallow-tail pennants with an original key emblem
        for bx_ in (290, 790):
            bn = path_poly([(bx_ - 60, 640), (bx_ + 60, 640), (bx_ + 60, 1000), (bx_, 950), (bx_ - 60, 1000)])
            cv.drawPath(bn, fill('#2f6a4a')); cv.drawPath(bn, ink(4))
            cv.drawLine(bx_ - 70, 640, bx_ + 70, 640, stroke('#7a4a2a', 12))
            cv.drawPath(path_poly([(bx_ - 60, 660), (bx_ + 60, 660), (bx_ + 60, 676), (bx_ - 60, 676)]), fill('#e6b43c'))
            cv.drawCircle(bx_, 770, 24, stroke('#e6b43c', 9))
            cv.drawLine(bx_, 794, bx_, 880, stroke('#e6b43c', 9))
            cv.drawLine(bx_, 850, bx_ + 22, 850, stroke('#e6b43c', 8)); cv.drawLine(bx_, 872, bx_ + 16, 872, stroke('#e6b43c', 8))
        # heavy oak chair of state
        th = path_poly([(450, 1250), (630, 1250), (630, 820), (610, 780), (470, 780), (450, 820)])
        cv.drawPath(th, fill('#7a4a2a')); cv.drawPath(th, ink(5))
        for k in range(4):
            cv.drawLine(480 + k * 40, 800, 480 + k * 40, 1120, stroke('#5a3220', 4))
        cv.drawPath(rrect(470, 1060, 140, 70, 16), fill('#2f6a4a')); cv.drawPath(rrect(470, 1060, 140, 70, 16), ink(4))
        for px in (450, 630):
            cv.drawCircle(px, 790, 18, fill('#a87040')); cv.drawCircle(px, 790, 18, ink(4))
        cv.drawPath(rrect(430, 1140, 220, 46, 10), fill('#7a4a2a')); cv.drawPath(rrect(430, 1140, 220, 46, 10), ink(4))
        # plain woven runner (green, two gold stripes)
        run = surface(300, 1400, '#3a6a4a')
        rc_ = run.getCanvas()
        for sx in (30, 270):
            rc_.drawLine(sx, 0, sx, 1400, stroke('#d9a648', 14))
        for k in range(0, 1400, 60):
            rc_.drawLine(50, k, 250, k + 30, stroke('#2f5a3e', 6, 0.6))
        draw_tex_quad(cv, run.makeImageSnapshot(), [(480, 1250), (600, 1250), (880, 3300), (200, 3300)])
        # torches
        for tx_ in (150, 930):
            cv.drawPath(path_poly([(tx_ - 20, 760), (tx_ + 20, 760), (tx_ + 8, 840), (tx_ - 8, 840)]), fill('#5a4a3a')); cv.drawPath(path_poly([(tx_ - 20, 760), (tx_ + 20, 760), (tx_ + 8, 840), (tx_ - 8, 840)]), ink(3))
            fl_ = path_smooth([(tx_ - 18, 762), (tx_ - 10, 720), (tx_, 690), (tx_ + 10, 720), (tx_ + 18, 762)])
            cv.drawPath(fl_, fill('#f8b040')); cv.drawPath(path_smooth([(tx_ - 8, 760), (tx_, 724), (tx_ + 8, 760)]), fill('#fff0a0'))
            E.append(dict(kind='lamp', pos=(tx_, 735), r=260, lit=True, ground=None))

    def near(cv):
        cv.drawPath(rrect(-200, -200, 260, 2600, 20), fill('#8a8696')); cv.drawPath(rrect(-200, -200, 260, 2600, 20), ink(6))
        cv.drawPath(rrect(1020, -200, 260, 2600, 20), fill('#8a8696')); cv.drawPath(rrect(1020, -200, 260, 2600, 20), ink(6))
        # chandelier
        cv.drawLine(540, -500, 540, -60, stroke('#2a2232', 6))
        cv.drawPath(ellipse(540, -40, 240, 40), stroke('#3a3040', 14))
        for k in range(7):
            x = 330 + k * 70
            cv.drawRect(skia.Rect.MakeXYWH(x - 6, -100, 12, 50), fill('#f4f0e8'))
            E.append(dict(kind='lamp', pos=(x, -110), r=90, lit=True, ground=None))

    def lights_hall(cv, mm):
        god_rays(cv, (540, 330), 90, 40, 1600, n=9, col=(255, 230, 190), a=0.2)
        halo(cv, 540, 330, 260, (255, 220, 170), 0.35)
        sk.draw_emitters(cv, [e for e in E if e['kind'] == 'lamp' and e['pos'][1] > 0], mm, True)

    def lights_near(cv, mm):
        sk.draw_emitters(cv, [e for e in E if e['kind'] == 'lamp' and e['pos'][1] < 0], mm, True)

    return [
        ('hall', 1.5, hall, dict(lights=lights_hall)),
        ('near', 0.62, near, dict(blur=8, lights=lights_near)),
    ], dict(ground_y=1500, chair=(540, 1150))


# =============================================================================== SHIP DECK
def ship_deck(mood):
    from .sets import Ground
    m = MOODS[mood]
    night = mood in NIGHT
    vx, h0 = 560, 860
    G = Ground(vx, h0, 1.6)
    E = []

    def sky(cv):
        sk.sky(cv, m, seed=21, clouds=7, cloud_band=(-420, 600), cloud_scale=1.3, moon=(820, 160, 60) if night else None,
               stars=160 if night else 0, sun=(1150, 200, 70) if mood == 'day' else None)

    def sea(cv):
        top, mid_, bot = m['sky']
        base = mix('#2a6ad0', mid_, 0.25) if not night else '#1c2a7a'
        cv.drawRect(skia.Rect.MakeLTRB(-600, h0 - 20, 1700, 2600), fill(base))
        r = rng(3)
        for k in range(220):
            y = h0 + (r.random() ** 2) * 1500
            d = (y - h0) / 1500
            x = r.uniform(-500, 1600)
            L = 20 + 120 * d
            p = skia.Path(); p.moveTo(x - L, y); p.quadTo(x, y - 10 - 20 * d, x + L, y)
            cv.drawPath(p, stroke(mix(base, '#ffffff', 0.5), 2 + 4 * d, 0.8))
        # distant island
        sk.hills(cv, h0 - 4, 60, 420, 80, mix('#4a7a5a', m['fog'], 0.4), seed=5, wav=120)
        cv.drawRect(skia.Rect.MakeLTRB(-600, h0 - 4, 1700, h0 + 6), fill(mix(base, '#ffffff', 0.4)))

    def deck(cv):
        # deck planks in perspective (runs toward the bow at the vanishing point)
        G.tile(cv, tx.wood_planks(900, 900, plank=90, base='#c08a50', vertical=True, seed=4), 3.0, 3.0, xr=(-3.4, 3.4), zr=(0.4, 26))
        # bulwark rails left and right
        for sgn in (-1, 1):
            top_pts, base_pts = [], []
            Z = 0.9
            while Z < 26:
                x, y = G.proj(sgn * 3.4, Z)
                s = G.scale(Z)
                base_pts.append((x, y)); top_pts.append((x, y - 1.0 * s))
                Z *= 1.12
            wall = path_poly(base_pts + top_pts[::-1])
            cv.drawPath(wall, fill('#8a3a2a')); cv.drawPath(wall, ink(3))
            for (x, y), (xt, yt) in zip(base_pts[::2], top_pts[::2]):
                cv.drawLine(x, y, xt, yt, stroke('#6a2a1e', 3))
            cv.drawPath(path_poly(top_pts, close=False), stroke('#d8a060', 14)); cv.drawPath(path_poly(top_pts, close=False), ink(3))
        # mast with rigging and a furled sail
        mx_, my_ = G.proj(0.0, 9.0)
        s = G.scale(9.0)
        cv.drawPath(rrect(mx_ - 0.18 * s, my_ - 30 * s, 0.36 * s, 30 * s, 6), fill('#a8743e')); cv.drawPath(rrect(mx_ - 0.18 * s, my_ - 30 * s, 0.36 * s, 30 * s, 6), ink(3))
        for k in range(4):
            cv.drawLine(mx_ - 0.18 * s, my_ - (6 + k * 6) * s, mx_ + 0.18 * s, my_ - (6 + k * 6) * s, stroke('#2a1e28', 4))
        for (top_, bot_, wd) in ((-15.0, -10.6, 2.0), (-10.0, -4.6, 2.8)):
            sail = skia.Path()
            sail.moveTo(mx_ - wd * s, my_ + top_ * s)
            sail.quadTo(mx_, my_ + (top_ - 0.6) * s, mx_ + wd * s, my_ + top_ * s)
            sail.quadTo(mx_ + (wd + 0.6) * s, my_ + (top_ + bot_) / 2 * s, mx_ + wd * 0.92 * s, my_ + bot_ * s)
            sail.quadTo(mx_, my_ + (bot_ + 1.4) * s, mx_ - wd * 0.92 * s, my_ + bot_ * s)
            sail.quadTo(mx_ - (wd + 0.6) * s, my_ + (top_ + bot_) / 2 * s, mx_ - wd * s, my_ + top_ * s)
            sail.close()
            cv.drawPath(sail, fill('#f4ecd8'))
            cv.save(); cv.clipPath(sail, doAntiAlias=True)
            for k in range(-2, 3):
                cv.drawRect(skia.Rect.MakeXYWH(mx_ + (k * 0.8 - 0.2) * s, my_ + (top_ - 1) * s, 0.4 * s, (bot_ - top_ + 3) * s), fill('#c8343c', 0.9))
            cv.drawRect(skia.Rect.MakeXYWH(mx_ + 0.3 * s, my_ + (top_ - 1) * s, wd * s, (bot_ - top_ + 3) * s), fill('#4a2e66', 0.18))
            cv.restore()
            cv.drawPath(sail, ink(3))
            cv.drawLine(mx_ - (wd + 0.2) * s, my_ + top_ * s, mx_ + (wd + 0.2) * s, my_ + top_ * s, stroke('#7a4a2a', 8))
        for sgn in (-1, 1):
            bx_, by_ = G.proj(sgn * 3.3, 6.0)
            cv.drawLine(mx_, my_ - 28 * s, bx_, by_ - G.scale(6.0), stroke('#4a3a2a', 3))
            for k in range(1, 8):
                f = k / 8
                cv.drawLine(mx_ + (bx_ - mx_) * f - 0.4 * s, my_ - 28 * s + (by_ - G.scale(6.0) - my_ + 28 * s) * f,
                            mx_ + (bx_ - mx_) * f + 0.4 * s, my_ - 28 * s + (by_ - G.scale(6.0) - my_ + 28 * s) * f, stroke('#4a3a2a', 2))
        # barrels, crates, lantern
        for (X, Z) in ((-2.5, 3.2), (-2.4, 4.6), (2.6, 5.4)):
            x, y = G.proj(X, Z)
            sc_ = G.scale(Z) / 1000
            b = rrect(x - 300 * sc_, y - 800 * sc_, 600 * sc_, 800 * sc_, 200 * sc_)
            cv.drawPath(b, fill('#9a6232'))
            for hh in (0.2, 0.8):
                cv.drawRect(skia.Rect.MakeXYWH(x - 300 * sc_, y - 800 * sc_ * (1 - hh) - 30 * sc_, 600 * sc_, 60 * sc_), fill('#4a4a5a'))
            cv.drawPath(b, ink(max(1.5, 20 * sc_)))
        x, y = G.proj(2.5, 3.0)
        sk.crate(cv, x - 0.5 * G.scale(3.0), y - 0.9 * G.scale(3.0), 1.0 * G.scale(3.0), 0.9 * G.scale(3.0), col='#b07a45')
        lx, ly = G.proj(-3.2, 2.4)
        lsz = G.scale(2.4) / 1000
        cv.drawPath(rrect(lx - 90 * lsz, ly - 1500 * lsz, 180 * lsz, 240 * lsz, 30 * lsz), fill('#f8e2a0')); cv.drawPath(rrect(lx - 90 * lsz, ly - 1500 * lsz, 180 * lsz, 240 * lsz, 30 * lsz), ink(3))
        E.append(dict(kind='lamp', pos=(lx, ly - 1380 * lsz), r=320, lit=night, ground=ly))
        # steering wheel near camera
        wx_, wy_ = G.proj(1.2, 1.8)
        ws = G.scale(1.8) / 1000
        cv.drawCircle(wx_, wy_ - 900 * ws, 400 * ws, stroke('#8a5a2a', 70 * ws)); cv.drawCircle(wx_, wy_ - 900 * ws, 400 * ws, ink(4))
        for k in range(8):
            a = k * math.pi / 4
            cv.drawLine(wx_, wy_ - 900 * ws, wx_ + math.cos(a) * 520 * ws, wy_ - 900 * ws + math.sin(a) * 520 * ws, stroke('#8a5a2a', 40 * ws))
        cv.drawCircle(wx_, wy_ - 900 * ws, 90 * ws, fill('#e6b43c')); cv.drawCircle(wx_, wy_ - 900 * ws, 90 * ws, ink(3))

    def lights(cv, mm):
        sk.draw_emitters(cv, E, mm, night)

    return [
        ('sky', 30.0, sky, dict(grade=False)),
        ('sea', 8.0, sea, dict()),
        ('deck', 1.0, deck, dict(lights=lights)),
    ], dict(ground=G, ground_y=1600, h0=h0, vx=vx)


REGISTRY = {'planet_shop': planet_shop, 'office': office, 'castle_hall': castle_hall, 'ship_deck': ship_deck}
