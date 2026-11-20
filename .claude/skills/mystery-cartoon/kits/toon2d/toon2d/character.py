"""Original cartoon characters: big round head, ink limbs with bent knees, detailed flat-colour costumes.

Units: head radius = 100. The figure stands with its feet at (0,0), y grows downward, so the body is at y<0.
draw_character(canvas, spec, x, y, scale, t, mood) draws one character; spec is a dict (see make()).
"""
import functools
import math
import zlib

import skia

from .paint import (C, fill, stroke, ink, shade, mix, rgb, path_poly, path_smooth, rrect, ellipse, INK, argb,
                    rad_grad, lin_grad, blurred)
from .light import grade_color

R = 100.0
HEAD_INK = 9.0
LIMB = 10.5
SKIN = (0xf6, 0xf1, 0xea)       # warm off-white head
SKIN_SHADE = (0xd6, 0xcc, 0xd6)  # lilac-grey shade side


# ============================================================================ archetypes
ARCHETYPES = {
    'worker':    dict(torso='#c8642e', accent='#e8a33a', pants='#3d4e7a', shoes='#6b3e2a', hat='hardhat',
                      parts=['overalls', 'pocket_l', 'rolled', 'bandana'], prop='wrench', hair='tuft_brown', width=1.0),
    'boss':      dict(torso='#3f5a3a', accent='#e0b43a', pants='#2e3a2c', shoes='#3a2430', hat=None,
                      parts=['shirt_v', 'tie', 'double_buttons', 'watch_chain', 'pocket_square'], prop='mug',
                      hair='slick_grey', moustache=True, width=1.22),
    'cop':       dict(torso='#7fa6d8', accent='#d8dde6', pants='#24346e', shoes='#1f1a2a', hat='peaked',
                      parts=['collar', 'pockets2', 'center_buttons', 'belt', 'badge', 'radio'], prop='baton', width=1.08),
    'cook':      dict(torso='#f4f0e8', accent='#d8483a', pants='#3a3a4e', shoes='#2a2230', hat='toque',
                      parts=['double_buttons_jacket', 'neckerchief', 'apron'], prop='ladle', width=1.05),
    'knight':    dict(torso='#a7b0c4', accent='#b8322f', pants='#8d96aa', shoes='#6f7890', hat='helm',
                      parts=['plate', 'tabard', 'rivets', 'belt_brown'], prop='sword', width=1.12, armor=True),
    'king':      dict(torso='#9a2236', accent='#e6b43c', pants='#9a2236', shoes='#5a2030', hat='crown',
                      parts=['robe', 'ermine', 'chain_medal'], prop='sceptre', width=1.15, robe=True,
                      beard='#e8e2da'),
    'scientist': dict(torso='#f2f2ee', accent='#5ab0d8', pants='#55607a', shoes='#3a2c30', hat=None,
                      parts=['labcoat', 'shirt_v_blue', 'pocket_pens', 'name_tag'], prop='flask',
                      hair='wild_white', glasses=True, width=1.04, coat=True),
    'cashier':   dict(torso='#3f8ac8', accent='#e8a83a', pants='#3a3e5a', shoes='#2a2230', hat='visor',
                      parts=['polo_collar', 'apron_green', 'name_tag'], prop='scanner', hair='bob_brown', width=1.02),
    'sailor':    dict(torso='#f4f1ea', accent='#2a4fa8', pants='#2a3c78', shoes='#2a2230', hat='sailor_cap',
                      parts=['stripes', 'sailor_collar', 'kerchief'], prop='telescope', scarf=False, width=1.02),
    'alien':     dict(torso='#7a4ab0', accent='#f2c640', pants='#4a3a7a', shoes='#2a2232', hat='antennae',
                      parts=['collar', 'center_buttons', 'belt'], prop=None, width=1.0, skin='#9fe07a', skin_shade='#6ab05a'),
    'caveman':   dict(torso='#c8904a', accent='#6a3e22', pants='#c8904a', shoes='#e8c8a8', hat=None,
                      parts=['fur_tunic'], prop='club', hair='messy_black', width=1.1),
    'kid':       dict(torso='#f2b632', accent='#d84a6a', pants='#3f78c8', shoes='#e84a4a', hat='propeller',
                      parts=['tee_star', 'shorts'], prop='balloon', hair='cowlick', width=0.92, kid=True, scarf='#d84a6a'),
}

EXPRESSIONS = {
    #            eyes      brows (l_ang, r_ang, lift)   mouth        look
    'neutral':  ('dot',    (0, 0, 0),                   'line',      (0, 0)),
    'smug':     ('half',   (-4, 8, 2),                  'smirk',     (0, 0)),
    'angry':    ('dot',    (24, -24, -6),               'grit',      (0, 0)),
    'shocked':  ('wide',   (-10, 10, 14),               'o',         (0, 0)),
    'laughing': ('happy',  (-8, 8, 10),                 'laugh',     (0, 0)),
    'scared':   ('wide_s', (-22, 22, 10),               'wavy',      (0, 0)),
    'sad':      ('dot',    (-20, 20, 2),                'frown',     (0, 0.5)),
    'sly':      ('half',   (6, -14, 0),                 'smirk',     (0.7, 0)),
    'happy':    ('dot',    (-6, 6, 6),                  'smile',     (0, 0)),
    'deadpan':  ('half',   (0, 0, -2),                  'line',      (0, 0)),
}


def make(archetype, **over):
    spec = dict(ARCHETYPES[archetype])
    spec['archetype'] = archetype
    spec.update(dict(pose='stand', expr='neutral', face=0.3, dir=1, seed=zlib.crc32(archetype.encode()) % 997))
    spec.update(over)
    return spec


# ============================================================================ poses
def _lerp(a, b, t):
    return a + (b - a) * t


def pose_angles(pose, t, seed=0):
    """Absolute limb angles in degrees (0 = straight down, +ve rotates toward +x = facing side).
    Returns dict: arm_b (back arm upper, fore), arm_f (front arm), leg_b, leg_f, lean, bob, head_tilt, sq."""
    br = math.sin(t * 2 * math.pi / 3.4 + seed)          # breathing
    P = dict(arm_b=(-14, -6), arm_f=(12, 22), leg_b=(-4, -16), leg_f=(16, -2), lean=0, bob=br * 2.2,
             head_tilt=br * 1.2, sq=1 + br * 0.012, shoulder=0, hand_b='mitt', hand_f='mitt', cross=False)
    if pose == 'stand':
        P.update(leg_b=(-4, -16), leg_f=(16, -2))
    elif pose in ('walk', 'run'):
        sp = 1.9 if pose == 'walk' else 2.8
        ph = t * sp * 2 * math.pi
        A = 26 if pose == 'walk' else 42
        s = math.sin(ph)
        kb = max(0, math.sin(ph + math.pi * 0.5))
        kf = max(0, math.sin(ph - math.pi * 0.5))
        knee = 30 if pose == 'walk' else 75
        P['leg_f'] = (A * s, A * s - knee * kf)
        P['leg_b'] = (-A * s, -A * s - knee * kb)
        armA = 24 if pose == 'walk' else 48
        P['arm_f'] = (-armA * s, -armA * s + (20 if pose == 'walk' else 70))
        P['arm_b'] = (armA * s, armA * s + (20 if pose == 'walk' else 70))
        P['bob'] = -abs(math.cos(ph)) * (7 if pose == 'walk' else 16)
        P['lean'] = 4 if pose == 'walk' else 14
        P['head_tilt'] = math.sin(ph) * 2
    elif pose == 'point':
        P.update(arm_f=(98 + br * 1.5, 92), hand_f='point', arm_b=(-18, 30), hand_b='hip', lean=-2)
    elif pose == 'shrug':
        k = 0.5 + 0.5 * math.sin(t * 2.2)
        P.update(arm_f=(55, 150 + 10 * k), arm_b=(-55, -150 - 10 * k), hand_f='palm', hand_b='palm',
                 shoulder=-10 - 4 * k, head_tilt=8 * k - 4)
    elif pose == 'arms_crossed':
        P.update(arm_f=(12, -100), arm_b=(-12, 100), cross=True, leg_b=(-8, 6), leg_f=(10, -2))
    elif pose == 'hips':
        P.update(arm_f=(42, -40), arm_b=(-42, 40), hand_f='hip', hand_b='hip', noprop=True)
    elif pose == 'hold':
        P.update(arm_f=(28, 88), hand_f='grip')
    elif pose == 'think':
        P.update(arm_f=(18, 168), hand_f='chin', arm_b=(-10, 85), cross=False)
    elif pose == 'wave':
        P.update(arm_f=(140 + 15 * math.sin(t * 9), 175 + 25 * math.sin(t * 9)), hand_f='palm')
    elif pose == 'cheer':
        P.update(arm_f=(150, 170), arm_b=(-150, -170), hand_f='mitt', hand_b='mitt', bob=-abs(math.sin(t * 6)) * 12)
    elif pose == 'sit':
        P.update(leg_f=(80, 5), leg_b=(76, 0), arm_f=(20, 70), arm_b=(-5, 40))
    return P


# ============================================================================ helpers
@functools.lru_cache(maxsize=4096)
def _g(c, mood_name):
    from .light import MOODS
    return grade_color(c, MOODS[mood_name], char=True)


class Ctx:
    def __init__(self, cv, spec, mood_name, t):
        self.cv, self.spec, self.mood, self.t = cv, spec, mood_name, t

    def g(self, c):
        return _g(rgb(c), self.mood)

    def f(self, c, a=1.0):
        return fill(self.g(c), a)


def _seg(p, ang, L):
    a = math.radians(ang)
    return (p[0] + math.sin(a) * L, p[1] + math.cos(a) * L)


def _limb(cv, p0, a1, a2, L1, L2, w=LIMB):
    p1 = _seg(p0, a1, L1)
    p2 = _seg(p1, a2, L2)
    path = skia.Path()
    path.moveTo(*p0)
    # gentle curve through the joint so limbs read as noodles, not sticks
    path.quadTo(p1[0], p1[1], (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    path.lineTo(*p2)
    cv.drawPath(path, ink(w))
    return p1, p2


def _hand(x, kind, p, ang, cv):
    """Mitten hand: white with ink outline and a thumb."""
    g = x.g
    cv.save()
    cv.translate(*p)
    cv.rotate(-ang)
    if kind == 'point':
        cv.drawPath(rrect(-11, -4, 22, 22, 10), fill(g(SKIN)))
        cv.drawPath(rrect(-11, -4, 22, 22, 10), ink(5))
        cv.drawPath(rrect(-4, 12, 9, 26, 4.5), fill(g(SKIN)))
        cv.drawPath(rrect(-4, 12, 9, 26, 4.5), ink(4.5))
    elif kind == 'palm':
        e = ellipse(0, 10, 15, 14)
        cv.drawPath(e, fill(g(SKIN)))
        cv.drawPath(e, ink(5))
        for k in (-8, 0, 8):
            cv.drawLine(k, 20, k * 1.2, 28, ink(4))
    else:
        e = ellipse(0, 9, 14, 15)
        cv.drawPath(e, fill(g(SKIN)))
        cv.drawPath(e, ink(5))
        th = ellipse(11, 3, 6, 8)
        cv.drawPath(th, fill(g(SKIN)))
        cv.drawPath(th, ink(4))
    cv.restore()


# ============================================================================ costume parts
def _torso_path(sp):
    w = sp.get('width', 1.0)
    top, hem = -300.0, sp['_hem']
    sw, hw = 50 * w, 78 * w
    if sp.get('robe'):
        hw = 92 * w
    p = skia.Path()
    p.moveTo(-sw, top + 6)
    p.cubicTo(-sw - 4, top - 14, sw + 4, top - 14, sw, top + 6)
    p.cubicTo(sw + 18, top + 60, hw + 6, hem - 70, hw, hem - 12)
    p.quadTo(hw - 2, hem + 2, hw - 14, hem + 2)
    p.lineTo(-hw + 14, hem + 2)
    p.quadTo(-hw + 2, hem + 2, -hw, hem - 12)
    p.cubicTo(-hw - 6, hem - 70, -sw - 18, top + 60, -sw, top + 6)
    p.close()
    return p, sw, hw, top, hem


def _draw_parts(x, sp, tp, sw, hw, top, hem):
    cv, g = x.cv, x.g
    T, A = sp['torso'], sp['accent']
    mid = (top + hem) / 2
    fo = sp['face'] * 10   # details drift toward the facing side
    for part in sp['parts']:
        if part == 'overalls':
            cv.drawPath(rrect(-40 + fo, top + 70, 80, hem - top - 60, 14), x.f('#3d5ea8'))
            cv.drawPath(rrect(-40 + fo, top + 70, 80, hem - top - 60, 14), ink(4))
            cv.drawPath(rrect(-22 + fo, top + 88, 44, 34, 6), x.f(shade('#3d5ea8', -0.15)))
            cv.drawPath(rrect(-22 + fo, top + 88, 44, 34, 6), stroke(g('#e8d7a0'), 2.5))
            for sx in (-1, 1):
                cv.drawLine(sx * 32 + fo, top + 72, sx * 40, top + 6, stroke(g('#3d5ea8'), 13, cap=skia.Paint.kButt_Cap))
                cv.drawLine(sx * 32 + fo, top + 72, sx * 40, top + 6, ink(3))
                cv.drawPath(rrect(sx * 32 + fo - 8, top + 64, 16, 14, 3), x.f('#e8c050'))
                cv.drawPath(rrect(sx * 32 + fo - 8, top + 64, 16, 14, 3), ink(3))
            cv.drawLine(fo, top + 128, fo, hem - 10, stroke(g('#e8d7a0'), 2.5))
        elif part == 'pocket_l':
            cv.drawPath(rrect(-hw + 18, mid + 10, 30, 32, 5), x.f(shade(T, -0.12)))
            cv.drawPath(rrect(-hw + 18, mid + 10, 30, 32, 5), ink(3))
        elif part == 'rolled':
            pass
        elif part in ('shirt_v', 'shirt_v_blue'):
            sc = '#f4f1ea' if part == 'shirt_v' else '#bcd8ec'
            cv.drawPath(path_poly([(-26 + fo, top - 4), (26 + fo, top - 4), (fo, top + 70)]), x.f(sc))
            cv.drawPath(path_poly([(-26 + fo, top - 4), (fo, top + 70), (26 + fo, top - 4)], close=False), ink(4))
            # lapels
            for sx in (-1, 1):
                lp = path_poly([(sx * 26 + fo, top - 4), (sx * 40 + fo, top + 30), (fo + sx * 4, top + 78)])
                cv.drawPath(lp, x.f(shade(T, -0.18)))
                cv.drawPath(lp, ink(3.5))
        elif part == 'tie':
            tie = path_poly([(fo - 7, top + 4), (fo + 7, top + 4), (fo + 11, top + 70), (fo, top + 86), (fo - 11, top + 70)])
            cv.drawPath(tie, x.f(A))
            for k in range(3):
                cv.drawLine(fo - 9, top + 22 + k * 18, fo + 9, top + 14 + k * 18, stroke(g(shade(A, -0.3)), 3))
            cv.drawPath(tie, ink(3.5))
            cv.drawPath(path_poly([(fo - 9, top - 2), (fo + 9, top - 2), (fo + 6, top + 10), (fo - 6, top + 10)]), x.f(shade(A, -0.15)))
        elif part == 'double_buttons':
            for k in range(3):
                for sx in (-1, 1):
                    cv.drawCircle(fo + sx * 20, top + 96 + k * 30, 5.5, x.f('#e6c25a'))
                    cv.drawCircle(fo + sx * 20, top + 96 + k * 30, 5.5, ink(2.5))
        elif part == 'watch_chain':
            p = skia.Path()
            p.moveTo(fo + 20, top + 120)
            p.quadTo(fo + 40, top + 150, fo + 58, top + 118)
            cv.drawPath(p, stroke(g('#e6c25a'), 3.5))
            cv.drawCircle(fo + 58, top + 118, 7, x.f('#e6c25a'))
            cv.drawCircle(fo + 58, top + 118, 7, ink(2.5))
        elif part == 'pocket_square':
            cv.drawPath(path_poly([(-hw * 0.55, top + 66), (-hw * 0.55 + 22, top + 66), (-hw * 0.55 + 6, top + 50)]), x.f('#f4f1ea'))
            cv.drawLine(-hw * 0.6, top + 66, -hw * 0.6 + 30, top + 66, ink(3))
        elif part == 'collar':
            for sx in (-1, 1):
                c = path_poly([(fo, top + 4), (fo + sx * 40, top - 2), (fo + sx * 30, top + 30)])
                cv.drawPath(c, x.f(shade(T, 0.12)))
                cv.drawPath(c, ink(3.5))
        elif part == 'pockets2':
            for sx in (-1, 1):
                px = fo + sx * 34 - 17
                cv.drawPath(rrect(px, top + 56, 34, 34, 5), x.f(shade(T, -0.1)))
                cv.drawPath(rrect(px, top + 56, 34, 34, 5), ink(3))
                cv.drawPath(path_poly([(px, top + 56), (px + 34, top + 56), (px + 34, top + 66), (px + 17, top + 72), (px, top + 66)]), x.f(shade(T, -0.18)))
                cv.drawPath(path_poly([(px, top + 56), (px + 34, top + 56), (px + 34, top + 66), (px + 17, top + 72), (px, top + 66)]), ink(3))
                cv.drawCircle(px + 17, top + 66, 3.5, x.f(A))
        elif part == 'center_buttons':
            cv.drawLine(fo, top + 10, fo, hem - 34, ink(3))
            for k in range(4):
                cv.drawCircle(fo + 6, top + 40 + k * 28, 5, x.f(A))
                cv.drawCircle(fo + 6, top + 40 + k * 28, 5, ink(2.2))
        elif part in ('belt', 'belt_brown'):
            bc = '#2a2232' if part == 'belt' else '#7a4a2a'
            cv.save(); cv.clipPath(tp, doAntiAlias=True)
            cv.drawRect(skia.Rect.MakeLTRB(-200, hem - 46, 200, hem - 26), x.f(bc))
            cv.drawLine(-200, hem - 46, 200, hem - 46, ink(3)); cv.drawLine(-200, hem - 26, 200, hem - 26, ink(3))
            cv.restore()
            cv.drawPath(rrect(fo - 13, hem - 49, 26, 26, 4), x.f(A if part == 'belt' else '#f2c640'))
            cv.drawPath(rrect(fo - 13, hem - 49, 26, 26, 4), ink(3))
            cv.drawPath(rrect(fo - 6, hem - 42, 12, 12, 2), x.f(bc))
        elif part == 'badge':
            bx, by = fo - 34, top + 44
            sh = path_poly([(bx - 13, by - 12), (bx + 13, by - 12), (bx + 13, by + 4), (bx, by + 16), (bx - 13, by + 4)])
            cv.drawPath(sh, x.f(A))
            cv.drawPath(sh, ink(3))
            cv.drawCircle(bx, by - 1, 5, x.f(shade(A, -0.3)))
        elif part == 'radio':
            cv.drawPath(rrect(hw * 0.55, top + 36, 18, 30, 4), x.f('#2a2232'))
            cv.drawLine(hw * 0.55 + 12, top + 36, hw * 0.55 + 12, top + 16, ink(3.5))
        elif part == 'double_buttons_jacket':
            cv.drawPath(path_poly([(fo + 30, top + 2), (fo + 30, hem - 20)], close=False), ink(3))
            for k in range(4):
                for sx in (-1, 1):
                    cv.drawCircle(fo + 8 + sx * 14, top + 50 + k * 26, 5, x.f('#d8cfc0'))
                    cv.drawCircle(fo + 8 + sx * 14, top + 50 + k * 26, 5, ink(2.2))
        elif part == 'neckerchief':
            k = path_poly([(fo - 34, top - 4), (fo + 34, top - 4), (fo + 6, top + 38)])
            cv.drawPath(k, x.f(A)); cv.drawPath(k, ink(3.5))
            cv.drawCircle(fo + 4, top + 8, 9, x.f(shade(A, -0.15))); cv.drawCircle(fo + 4, top + 8, 9, ink(3))
        elif part == 'apron':
            ap = rrect(-hw * 0.72, mid - 4, hw * 1.44, hem - mid + 2, 12)
            cv.drawPath(ap, x.f('#ffffff')); cv.drawPath(ap, ink(3.5))
            cv.drawPath(rrect(-22, mid + 30, 44, 30, 5), ink(3))
            cv.drawLine(-hw * 0.72, mid + 6, hw * 0.72, mid + 6, stroke(g('#e8e0d4'), 6))
        elif part == 'plate':
            cv.save(); cv.clipPath(tp, doAntiAlias=True)
            for k in range(4):
                y = top + 30 + k * 34
                cv.drawPath(path_smooth([(-120, y), (0, y + 12), (120, y)], close=False), stroke(g(shade(T, -0.35)), 3.5))
            cv.drawPath(ellipse(-hw * 0.35, top + 60, 18, 46), fill(g('#ffffff'), 0.35))
            cv.restore()
        elif part == 'tabard':
            tb = rrect(fo - 28, top + 20, 56, hem - top - 16, 6)
            cv.drawPath(tb, x.f(A)); cv.drawPath(tb, ink(3.5))
            cr = path_poly([(fo - 5, top + 50), (fo + 5, top + 50), (fo + 5, top + 70), (fo + 20, top + 70), (fo + 20, top + 80),
                            (fo + 5, top + 80), (fo + 5, top + 110), (fo - 5, top + 110), (fo - 5, top + 80), (fo - 20, top + 80),
                            (fo - 20, top + 70), (fo - 5, top + 70)])
            cv.drawPath(cr, x.f('#f4f1ea')); cv.drawPath(cr, ink(2.5))
        elif part == 'rivets':
            for sx in (-1, 1):
                for k in range(3):
                    cv.drawCircle(sx * (hw - 18), top + 50 + k * 40, 4.5, x.f(shade(T, 0.3)))
                    cv.drawCircle(sx * (hw - 18), top + 50 + k * 40, 4.5, ink(2))
        elif part == 'robe':
            cv.drawLine(fo, top + 30, fo, hem, ink(3.5))
            cv.save(); cv.clipPath(tp, doAntiAlias=True)
            cv.drawRect(skia.Rect.MakeLTRB(fo - 16, top + 30, fo + 16, hem + 4), x.f('#f4efe4'))
            for k in range(6):
                cv.drawPath(path_poly([(fo - 3, top + 50 + k * 34), (fo + 3, top + 50 + k * 34), (fo, top + 60 + k * 34)]), x.f('#2a2232'))
            cv.drawRect(skia.Rect.MakeLTRB(-200, hem - 26, 200, hem + 4), x.f('#f4efe4'))
            for k in range(-8, 9):
                cv.drawPath(path_poly([(k * 22 - 3, hem - 14), (k * 22 + 3, hem - 14), (k * 22, hem - 4)]), x.f('#2a2232'))
            cv.restore()
            cv.drawLine(-200, hem - 26, 200, hem - 26, ink(3))
        elif part == 'ermine':
            er = path_smooth([(-sw - 30, top + 10), (0, top + 46), (sw + 30, top + 10), (sw + 10, top - 14), (-sw - 10, top - 14)])
            cv.drawPath(er, x.f('#f4efe4')); cv.drawPath(er, ink(4))
            for k in range(-3, 4):
                cv.drawPath(path_poly([(k * 18 - 3, top + 8 + abs(k) * -2), (k * 18 + 3, top + 8), (k * 18, top + 18)]), x.f('#2a2232'))
        elif part == 'chain_medal':
            p = skia.Path(); p.moveTo(-sw, top + 20); p.quadTo(fo, top + 110, sw, top + 20)
            cv.drawPath(p, stroke(g(A), 5)); cv.drawPath(p, ink(1.5))
            cv.drawCircle(fo, top + 82, 15, x.f(A)); cv.drawCircle(fo, top + 82, 15, ink(3))
            cv.drawCircle(fo, top + 82, 7, x.f('#c8343c'))
        elif part == 'labcoat':
            cv.drawLine(fo + 4, top + 66, fo + 4, hem, ink(3.5))
            for sx in (-1, 1):
                lp = path_poly([(sx * 24 + fo, top - 6), (sx * 44 + fo, top + 30), (fo + sx * 4, top + 72)])
                cv.drawPath(lp, x.f('#e2e2dc')); cv.drawPath(lp, ink(3.5))
            for sx in (-1, 1):
                cv.drawPath(rrect(sx * 44 - 18 + fo, hem - 90, 36, 34, 5), ink(3))
        elif part == 'pocket_pens':
            px = fo - 52
            cv.drawPath(rrect(px, top + 60, 32, 30, 4), ink(3))
            for k, cc in enumerate(('#d8483a', '#3a6ad8', '#2f9a5a')):
                cv.drawPath(rrect(px + 5 + k * 9, top + 46, 6, 20, 2), x.f(cc)); cv.drawPath(rrect(px + 5 + k * 9, top + 46, 6, 20, 2), ink(1.8))
        elif part == 'name_tag':
            cv.drawPath(rrect(hw * 0.12 + fo, top + 52, 42, 22, 4), x.f('#ffffff'))
            cv.drawPath(rrect(hw * 0.12 + fo, top + 52, 42, 22, 4), ink(2.5))
            cv.drawLine(hw * 0.12 + fo + 7, top + 63, hw * 0.12 + fo + 34, top + 63, stroke(g('#2a2232'), 3))
        elif part == 'polo_collar':
            for sx in (-1, 1):
                c = path_poly([(fo, top + 2), (fo + sx * 38, top - 4), (fo + sx * 22, top + 26)])
                cv.drawPath(c, x.f(shade(T, 0.15))); cv.drawPath(c, ink(3.5))
            cv.drawLine(fo, top + 4, fo, top + 46, ink(3))
            for k in range(2):
                cv.drawCircle(fo + 5, top + 18 + k * 16, 3.5, x.f('#ffffff'))
        elif part == 'apron_green':
            ap = rrect(-hw * 0.7, mid - 14, hw * 1.4, hem - mid + 12, 10)
            cv.drawPath(ap, x.f(A)); cv.drawPath(ap, ink(3.5))
            cv.drawPath(rrect(-26, mid + 20, 52, 28, 5), ink(3))
            cv.drawLine(fo, mid + 20, fo, mid + 48, ink(2.5))
        elif part == 'stripes':
            cv.save(); cv.clipPath(tp, doAntiAlias=True)
            for k in range(9):
                y = top + 20 + k * 22
                cv.drawRect(skia.Rect.MakeLTRB(-200, y, 200, y + 10), x.f(A))
            cv.restore()
        elif part == 'sailor_collar':
            sc = path_poly([(-sw - 18, top - 4), (sw + 18, top - 4), (sw + 10, top + 40), (fo, top + 76), (-sw - 10, top + 40)])
            cv.drawPath(sc, x.f(A)); cv.drawPath(sc, ink(4))
            cv.drawPath(path_poly([(-sw - 6, top + 6), (sw + 6, top + 6), (sw, top + 34), (fo, top + 64), (-sw, top + 34)]),
                        stroke(g('#ffffff'), 3))
            cv.drawPath(path_poly([(fo - 24, top - 4), (fo + 24, top - 4), (fo, top + 40)]), x.f(sp['torso']))
        elif part == 'kerchief':
            k = path_poly([(fo - 14, top + 52), (fo + 14, top + 52), (fo + 10, top + 90), (fo, top + 80), (fo - 10, top + 90)])
            cv.drawPath(k, x.f('#d8483a')); cv.drawPath(k, ink(3))
        elif part == 'tee_star':
            cx, cy = fo, mid - 6
            pts = []
            for k in range(10):
                rr = 24 if k % 2 == 0 else 10
                a = -math.pi / 2 + k * math.pi / 5
                pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
            cv.drawPath(path_poly(pts), x.f('#ffffff')); cv.drawPath(path_poly(pts), ink(3))
            cv.drawPath(path_smooth([(-sw + 4, top + 4), (fo, top + 20), (sw - 4, top + 4)], close=False), ink(3.5))
        elif part == 'shorts':
            pass
        elif part == 'fur_tunic':
            # one-shoulder spotted fur: bare skin over the far shoulder, a strap over the near one, ragged hem
            cv.save(); cv.clipPath(tp, doAntiAlias=True)
            bare = path_poly([(-200, top - 40), (-sw - 30, top - 40), (sw * 0.2 - fo, top + 70), (-200, top + 110)])
            cv.drawPath(bare, x.f(sp.get('skin', SKIN)))
            cv.drawLine(sw * 0.2 - fo, top + 70, -sw - 30, top - 40, ink(3.5))
            r_ = [(-30, top + 120, 14), (24, top + 90, 11), (40, top + 170, 15), (-46, top + 200, 12), (6, top + 230, 13),
                  (-12, top + 150, 9), (52, top + 240, 10), (-60, top + 140, 8)]
            for (sx_, sy_, rr_) in r_:
                cv.drawPath(ellipse(sx_ + fo, sy_, rr_, rr_ * 0.75), x.f(A))
            cv.restore()
            zz = [(-hw - 4, hem - 14)]
            for k in range(9):
                zz.append((-hw + (k + 0.5) * 2 * hw / 9, hem + (16 if k % 2 == 0 else -4)))
            zz.append((hw + 4, hem - 14))
            cv.drawPath(path_poly(zz + [(hw, hem - 30), (-hw, hem - 30)]), x.f(T))
            cv.drawPath(path_poly(zz, close=False), ink(3.5))
        elif part == 'bandana':
            k = path_poly([(fo - 40, top - 2), (fo + 40, top - 2), (fo + 4, top + 46)])
            cv.drawPath(k, x.f('#3a6ab0')); cv.drawPath(k, ink(3.5))
            for j in range(5):
                cv.drawCircle(fo - 18 + j * 9, top + 8 + (j % 2) * 8, 3.2, x.f('#f4f0e8'))


# ============================================================================ head parts
def _hair(x, sp, hx, hy):
    cv, g = x.cv, x.g
    h = sp.get('hair')
    fo = sp['face'] * 20
    if not h:
        return
    if h == 'tuft_brown':
        c = '#7a4a2a'
        p = path_smooth([(hx - 70, hy - 50), (hx - 40, hy - 88), (hx + 10, hy - 98), (hx + 30, hy - 120), (hx + 34, hy - 94),
                         (hx + 70, hy - 66), (hx + 20, hy - 70), (hx - 30, hy - 66)])
        cv.drawPath(p, x.f(c)); cv.drawPath(p, ink(5))
    elif h == 'slick_grey':
        c = '#9a9cae'
        cv.save(); cv.clipPath(ellipse(hx, hy, R, R), doAntiAlias=True)
        p = path_smooth([(hx - 120, hy - 10), (hx - 96, hy - 90), (hx - 20, hy - 120), (hx + 80, hy - 100), (hx + 104, hy - 30),
                         (hx + 70, hy - 52), (hx + 10 + fo, hy - 60), (hx - 40, hy - 50), (hx - 84, hy - 30)])
        cv.drawPath(p, x.f(c))
        for k in range(4):
            cv.drawPath(path_smooth([(hx - 80 + k * 30, hy - 40 - k * 5), (hx - 50 + k * 34, hy - 92), (hx + k * 30, hy - 112)], close=False),
                        stroke(g(shade(c, 0.35)), 3))
        cv.drawPath(p, ink(5))
        cv.restore()
        # side tufts poke out over the head line
        for sx in (-1, 1):
            tp = path_smooth([(hx + sx * 92, hy - 30), (hx + sx * 108, hy - 4), (hx + sx * 94, hy + 18), (hx + sx * 86, hy - 4)])
            cv.drawPath(tp, x.f(c)); cv.drawPath(tp, ink(4.5))
    elif h == 'wild_white':
        c = '#f0eef4'
        for k in range(9):
            a = math.radians(-170 + k * 20)
            px, py = hx + math.cos(a) * 92, hy + math.sin(a) * 92
            tuft = path_smooth([(px - 22, py + 8), (px + math.cos(a) * 46, py + math.sin(a) * 46 - 6), (px + 22, py + 8)])
            cv.drawPath(tuft, x.f(c)); cv.drawPath(tuft, ink(4.5))
    elif h == 'bob_brown':
        c = '#5a3424'
        p = path_smooth([(hx - 112, hy + 40), (hx - 108, hy - 70), (hx - 20, hy - 116), (hx + 80, hy - 96), (hx + 112, hy - 10),
                         (hx + 104, hy + 40), (hx + 70, hy - 40), (hx + fo, hy - 64), (hx - 70, hy - 40)])
        cv.drawPath(p, x.f(c)); cv.drawPath(p, ink(5))
        cv.drawPath(path_smooth([(hx - 50, hy - 90), (hx - 10, hy - 104), (hx + 40, hy - 96)], close=False), stroke(g(shade(c, 0.4)), 4))
    elif h == 'messy_black':
        c = '#2e2230'
        for k in range(10):
            a = math.radians(-165 + k * 16.5)
            px, py = hx + math.cos(a) * 88, hy + math.sin(a) * 88
            L = 40 + (k * 37 % 5) * 6
            nx, ny = -math.sin(a), math.cos(a)
            tuft = path_smooth([(px - nx * 24, py - ny * 24), (px + math.cos(a + 0.25) * L, py + math.sin(a + 0.25) * L),
                                (px + nx * 24, py + ny * 24)])
            cv.drawPath(tuft, x.f(c)); cv.drawPath(tuft, ink(4.5))
        cv.save(); cv.clipPath(ellipse(hx, hy, R, R), doAntiAlias=True)
        cv.drawPath(path_smooth([(hx - 110, hy - 20), (hx - 60, hy - 96), (hx + 50, hy - 104), (hx + 110, hy - 30), (hx + 40, hy - 56), (hx + fo, hy - 40), (hx - 50, hy - 54)]), x.f(c))
        cv.restore()
    elif h == 'cowlick':
        c = '#e07a2a'
        cv.save(); cv.clipPath(ellipse(hx, hy, R, R), doAntiAlias=True)
        p = path_smooth([(hx - 110, hy - 30), (hx - 70, hy - 100), (hx + 40, hy - 110), (hx + 110, hy - 40), (hx + 60, hy - 52),
                         (hx + 20 + fo, hy - 40), (hx - 30, hy - 56), (hx - 70, hy - 40)])
        cv.drawPath(p, x.f(c)); cv.drawPath(p, ink(5))
        cv.restore()
        sway = math.sin(x.t * 3.1) * 6
        lick = path_smooth([(hx + 6, hy - 96), (hx + 20 + sway, hy - 146), (hx + 44 + sway, hy - 140), (hx + 22, hy - 100)])
        cv.drawPath(lick, x.f(c)); cv.drawPath(lick, ink(4.5))


def _hat(x, sp, hx, hy, wob):
    cv, g = x.cv, x.g
    h = sp.get('hat')
    if not h:
        return
    A = sp['accent']
    cv.save()
    cv.translate(hx, hy - 70)
    cv.rotate(wob)
    cv.translate(-hx, -(hy - 70))
    if h == 'hardhat':
        c = '#f0b030'
        dome = skia.Path()
        dome.addArc(skia.Rect.MakeLTRB(hx - 96, hy - 160, hx + 96, hy - 20), 180, 180)
        dome.close()
        cv.drawPath(dome, x.f(c))
        cv.drawPath(path_poly([(hx - 14, hy - 158), (hx + 14, hy - 158), (hx + 10, hy - 90), (hx - 10, hy - 90)]), x.f(shade(c, 0.25)))
        cv.drawPath(ellipse(hx - 46, hy - 120, 16, 24), fill(g('#ffffff'), 0.45))
        cv.drawPath(dome, ink(6))
        brim = rrect(hx - 120, hy - 96, 240, 22, 11)
        cv.drawPath(brim, x.f(shade(c, -0.12))); cv.drawPath(brim, ink(6))
    elif h == 'peaked':
        c = '#24346e'
        top = path_smooth([(hx - 100, hy - 74), (hx - 112, hy - 136), (hx, hy - 162), (hx + 112, hy - 136), (hx + 100, hy - 74)])
        cv.drawPath(top, x.f(c)); cv.drawPath(top, ink(6))
        cv.drawPath(rrect(hx - 100, hy - 100, 200, 30, 6), x.f(shade(c, -0.2)))
        cv.drawPath(rrect(hx - 100, hy - 100, 200, 30, 6), ink(5))
        vis = path_smooth([(hx - 30, hy - 74), (hx + 120, hy - 78), (hx + 140, hy - 60), (hx + 40, hy - 56)])
        cv.drawPath(vis, x.f('#1c1a2a')); cv.drawPath(vis, ink(5))
        sh = path_poly([(hx - 14, hy - 140), (hx + 14, hy - 140), (hx + 14, hy - 120), (hx, hy - 108), (hx - 14, hy - 120)])
        cv.drawPath(sh, x.f(A)); cv.drawPath(sh, ink(3))
    elif h == 'toque':
        c = '#ffffff'
        band = rrect(hx - 74, hy - 120, 148, 50, 8)
        puff = skia.Path()
        for k, (dx, dy, rr) in enumerate([(-60, -170, 44), (-20, -200, 50), (30, -196, 48), (66, -164, 40), (0, -150, 60)]):
            puff.addCircle(hx + dx, hy + dy, rr)
        body = skia.Path()
        body.addRect(skia.Rect.MakeLTRB(hx - 72, hy - 170, hx + 72, hy - 100))
        puff = skia.Op(puff, body, skia.PathOp.kUnion_PathOp)
        cv.drawPath(puff, x.f(c)); cv.drawPath(puff, ink(6))
        for k in range(-1, 2):
            cv.drawPath(path_smooth([(hx + k * 40 - 18, hy - 186), (hx + k * 40, hy - 176), (hx + k * 40 + 18, hy - 186)], close=False), stroke(g('#d8d4dc'), 4))
        for k in range(-2, 3):
            cv.drawLine(hx + k * 26, hy - 160, hx + k * 24, hy - 118, stroke(g('#d8d4dc'), 4))
        cv.drawPath(band, x.f('#f0eef0')); cv.drawPath(band, ink(6))
    elif h == 'helm':
        # open-face kettle hat: steel dome with a centre ridge and a wide flat brim, face fully visible
        c = '#b4bccc'
        brim = ellipse(hx, hy - 46, 156, 24)
        cv.drawPath(brim, x.f(shade(c, -0.08))); cv.drawPath(brim, ink(6))
        dome = path_smooth([(hx - 98, hy - 50), (hx - 90, hy - 118), (hx - 40, hy - 154), (hx, hy - 160), (hx + 40, hy - 154),
                            (hx + 90, hy - 118), (hx + 98, hy - 50)])
        cv.drawPath(dome, x.f(c))
        cv.save(); cv.clipPath(dome, doAntiAlias=True)
        sh = skia.Path(); sh.addCircle(hx + 50, hy - 60, R)
        cv.drawPath(sh, fill(g(shade(c, -0.3)), 0.35))
        cv.drawPath(ellipse(hx - 52, hy - 118, 14, 30), fill(g('#ffffff'), 0.55))
        cv.restore()
        cv.drawPath(dome, ink(6))
        cv.drawPath(path_smooth([(hx, hy - 160), (hx + 3, hy - 110), (hx, hy - 56)], close=False), ink(4))
        cv.drawPath(rrect(hx - 98, hy - 66, 196, 18, 6), x.f(shade(c, -0.18))); cv.drawPath(rrect(hx - 98, hy - 66, 196, 18, 6), ink(4))
        for k in range(7):
            cv.drawCircle(hx - 78 + k * 26, hy - 57, 3.6, x.f(shade(c, 0.35)))
    elif h == 'crown':
        c = '#e6b43c'
        cr = path_poly([(hx - 70, hy - 84), (hx - 80, hy - 156), (hx - 40, hy - 118), (hx, hy - 170), (hx + 40, hy - 118),
                        (hx + 80, hy - 156), (hx + 70, hy - 84)])
        cv.drawPath(cr, x.f(c)); cv.drawPath(cr, ink(6))
        cv.drawPath(rrect(hx - 74, hy - 100, 148, 24, 6), x.f(shade(c, -0.15))); cv.drawPath(rrect(hx - 74, hy - 100, 148, 24, 6), ink(5))
        for k, gc in enumerate(('#c8343c', '#2d5bb0', '#2f9a5a')):
            cv.drawCircle(hx - 40 + k * 40, hy - 88, 7, x.f(gc)); cv.drawCircle(hx - 40 + k * 40, hy - 88, 7, ink(2.5))
        for px in (-80, 0, 80):
            cv.drawCircle(hx + px, hy - 160 - (10 if px == 0 else 0), 8, x.f('#f4efe4')); cv.drawCircle(hx + px, hy - 160 - (10 if px == 0 else 0), 8, ink(3))
        cv.drawPath(path_poly([(hx - 50, hy - 126), (hx - 46, hy - 106), (hx - 60, hy - 106)]), fill(g('#fff6d0'), 0.7))
    elif h == 'visor':
        c = A
        band = rrect(hx - 92, hy - 82, 184, 24, 10)
        vis = path_smooth([(hx - 20, hy - 70), (hx + 130, hy - 76), (hx + 140, hy - 56), (hx + 20, hy - 54)])
        cv.drawPath(vis, x.f(c)); cv.drawPath(vis, ink(5))
        cv.drawPath(band, x.f(shade(c, -0.12))); cv.drawPath(band, ink(5))
    elif h == 'sailor_cap':
        c = '#ffffff'
        cap = path_smooth([(hx - 96, hy - 66), (hx - 80, hy - 120), (hx, hy - 134), (hx + 80, hy - 120), (hx + 96, hy - 66)])
        cv.drawPath(cap, x.f(c)); cv.drawPath(cap, ink(6))
        cv.drawPath(rrect(hx - 98, hy - 86, 196, 24, 8), x.f(A)); cv.drawPath(rrect(hx - 98, hy - 86, 196, 24, 8), ink(5))
        sway = math.sin(x.t * 3.3) * 8 + wob * 2
        for k in (0, 1):
            rb = path_poly([(hx - 92, hy - 76 + k * 8), (hx - 130 + sway - k * 6, hy - 30 + k * 10), (hx - 116 + sway - k * 6, hy - 22 + k * 10), (hx - 88, hy - 66 + k * 8)])
            cv.drawPath(rb, x.f(A)); cv.drawPath(rb, ink(3.5))
    elif h == 'antennae':
        for sx in (-1, 1):
            sway = math.sin(x.t * 3.4 + sx) * 9 + wob * 2
            p = skia.Path(); p.moveTo(hx + sx * 30, hy - 88)
            p.quadTo(hx + sx * 40, hy - 150, hx + sx * 56 + sway, hy - 176)
            cv.drawPath(p, ink(7))
            cv.drawCircle(hx + sx * 56 + sway, hy - 180, 16, x.f('#f2c640')); cv.drawCircle(hx + sx * 56 + sway, hy - 180, 16, ink(5))
            cv.drawCircle(hx + sx * 52 + sway, hy - 186, 5, fill('#ffffff', 0.8))
    elif h == 'propeller':
        c = '#3f78c8'
        cap = skia.Path(); cap.addArc(skia.Rect.MakeLTRB(hx - 98, hy - 150, hx + 98, hy - 30), 180, 180); cap.close()
        cv.drawPath(cap, x.f(c))
        cv.save(); cv.clipPath(cap, doAntiAlias=True)
        for k, cc in enumerate(('#d84a6a', '#f2b632', '#2f9a5a')):
            cv.drawPath(path_poly([(hx, hy - 90), (hx - 140 + k * 100, hy - 160), (hx - 90 + k * 100, hy - 160)]), x.f(cc))
        cv.restore()
        cv.drawPath(cap, ink(6))
        cv.drawLine(hx, hy - 150, hx, hy - 170, ink(5))
        sp_a = x.t * 14
        L = 70 * abs(math.cos(sp_a))
        cv.drawPath(ellipse(hx - L / 2, hy - 172, L / 2 + 2, 9), x.f('#d84a6a'))
        cv.drawPath(ellipse(hx + L / 2, hy - 172, L / 2 + 2, 9), x.f('#f2b632'))
        cv.drawPath(ellipse(hx - L / 2, hy - 172, L / 2 + 2, 9), ink(3.5)); cv.drawPath(ellipse(hx + L / 2, hy - 172, L / 2 + 2, 9), ink(3.5))
        cv.drawCircle(hx, hy - 172, 7, x.f('#f4f0e8')); cv.drawCircle(hx, hy - 172, 7, ink(3))
    cv.restore()


def _eye(x, kind, ex, ey, look, blink, side):
    cv, g = x.cv, x.g
    if blink > 0.5 and kind not in ('happy',):
        cv.drawPath(path_smooth([(ex - 13, ey + 2), (ex, ey + 6), (ex + 13, ey + 2)], close=False), ink(6))
        return
    lx, ly = look[0] * 6, look[1] * 6
    if kind == 'dot':
        cv.drawPath(ellipse(ex + lx, ey + ly, 11, 15), fill(INK))
        cv.drawCircle(ex + lx - 3.5, ey + ly - 6, 3.6, fill('#ffffff', 0.95))
    elif kind == 'half':
        cv.drawPath(ellipse(ex + lx * 1.4, ey + 3 + ly, 11, 12), fill(INK))
        cv.drawCircle(ex + lx * 1.4 - 3, ey - 1, 3, fill('#ffffff', 0.9))
        lid = skia.Path(); lid.addRect(skia.Rect.MakeLTRB(ex - 18, ey - 22, ex + 18, ey + 1))
        cv.drawPath(lid, fill(g(SKIN)))
        cv.drawLine(ex - 15, ey + 1, ex + 15, ey + 1, ink(6))
    elif kind in ('wide', 'wide_s'):
        rr = 21 if kind == 'wide' else 19
        cv.drawCircle(ex, ey - 2, rr, fill('#ffffff'))
        cv.drawCircle(ex, ey - 2, rr, ink(5.5))
        pr = 7 if kind == 'wide' else 4.5
        cv.drawCircle(ex + lx, ey - 2 + ly, pr, fill(INK))
    elif kind == 'happy':
        p = skia.Path(); p.moveTo(ex - 14, ey + 6); p.quadTo(ex, ey - 16, ex + 14, ey + 6)
        cv.drawPath(p, ink(6.5))


def _mouth(x, kind, mx, my, t):
    cv, g = x.cv, x.g
    if kind == 'line':
        cv.drawLine(mx - 13, my, mx + 13, my, ink(6))
    elif kind == 'smile':
        p = skia.Path(); p.moveTo(mx - 18, my - 4); p.quadTo(mx, my + 14, mx + 18, my - 4)
        cv.drawPath(p, ink(6))
    elif kind == 'smirk':
        p = skia.Path(); p.moveTo(mx - 14, my + 3); p.quadTo(mx + 4, my + 6, mx + 18, my - 6)
        cv.drawPath(p, ink(6))
    elif kind == 'frown':
        p = skia.Path(); p.moveTo(mx - 15, my + 6); p.quadTo(mx, my - 8, mx + 15, my + 6)
        cv.drawPath(p, ink(6))
    elif kind == 'o':
        cv.drawPath(ellipse(mx, my + 2, 9, 12), fill(g('#5a2236')))
        cv.drawPath(ellipse(mx, my + 2, 9, 12), ink(5))
    elif kind == 'grit':
        r_ = rrect(mx - 24, my - 9, 48, 20, 6)
        cv.drawPath(r_, fill('#ffffff'))
        for k in (-12, 0, 12):
            cv.drawLine(mx + k, my - 9, mx + k, my + 11, ink(3))
        cv.drawLine(mx - 24, my + 1, mx + 24, my + 1, ink(3))
        cv.drawPath(r_, ink(5))
    elif kind == 'laugh':
        op = 1 + 0.25 * math.sin(t * 18)
        p = skia.Path(); p.moveTo(mx - 24, my - 6); p.lineTo(mx + 24, my - 6); p.quadTo(mx + 22, my + 26 * op, mx, my + 26 * op)
        p.quadTo(mx - 22, my + 26 * op, mx - 24, my - 6); p.close()
        cv.drawPath(p, fill(g('#5a2236')))
        cv.save(); cv.clipPath(p, doAntiAlias=True)
        cv.drawPath(ellipse(mx + 2, my + 24 * op, 14, 9), fill(g('#e86a7a')))
        cv.drawRect(skia.Rect.MakeLTRB(mx - 24, my - 7, mx + 24, my + 1), fill('#ffffff'))
        cv.restore()
        cv.drawPath(p, ink(5))
    elif kind == 'wavy':
        p = skia.Path(); p.moveTo(mx - 18, my)
        for k in range(4):
            p.quadTo(mx - 18 + k * 9 + 4.5, my + (6 if k % 2 else -6), mx - 18 + (k + 1) * 9, my)
        cv.drawPath(p, ink(5))


def _blink(t, seed):
    period = 3.1 + (seed % 7) * 0.23
    ph = (t + seed * 0.37) % period
    return 1.0 if ph < 0.11 else 0.0


def _draw_head(x, sp, hx, hy, tilt, P):
    cv, g = x.cv, x.g
    eyes, brows, mouth, look = EXPRESSIONS[sp['expr']]
    look = sp.get('look', look)
    fo = sp['face'] * 22
    cv.save()
    cv.translate(hx, hy + 60)
    cv.rotate(tilt)
    cv.translate(-hx, -(hy + 60))
    skin = sp.get('skin', SKIN)
    skin_sh = sp.get('skin_shade', SKIN_SHADE)
    head = ellipse(hx, hy, R, R * 0.98)
    # back hair (behind head)
    if sp.get('hair') == 'bob_brown':
        cv.drawPath(path_smooth([(hx - 112, hy + 48), (hx - 100, hy - 60), (hx + 100, hy - 60), (hx + 112, hy + 48)]), x.f('#4a2a1c'))
    cv.drawPath(head, x.f(skin))
    # shade crescent (light from upper-left) and soft cheek blush
    cv.save(); cv.clipPath(head, doAntiAlias=True)
    sh = skia.Path(); sh.addCircle(hx + 34, hy + 22, R * 1.0)
    sh2 = skia.Path(); sh2.addCircle(hx - 6, hy - 6, R * 0.98)
    crescent = skia.Op(sh, sh2, skia.PathOp.kDifference_PathOp)
    cv.drawPath(crescent, fill(g(skin_sh), 0.85))
    if sp.get('expr') == 'angry':
        cv.drawPath(head, fill(g('#e0506a'), 0.28))
    cv.drawPath(ellipse(hx + fo + 52, hy + 38, 16, 9), fill(g('#f2a0a8'), 0.45))
    cv.restore()
    if sp.get('beard'):
        bd = path_smooth([(hx - 70 + fo, hy + 30), (hx + fo, hy + 150), (hx + 70 + fo, hy + 30), (hx + 40 + fo, hy + 60), (hx + fo, hy + 70), (hx - 40 + fo, hy + 60)])
        cv.drawPath(bd, x.f(sp['beard'])); cv.drawPath(bd, ink(5))
    cv.drawPath(head, ink(HEAD_INK))
    # face
    ey = hy + 6
    blink = _blink(x.t, sp['seed'])
    for side in (-1, 1):
        ex = hx + fo + side * 30 * (1 - abs(sp['face']) * 0.12)
        _eye(x, eyes, ex, ey, look, blink, side)
        ang = brows[0] if side < 0 else brows[1]
        by = ey - 38 - brows[2]
        cv.save(); cv.translate(ex, by); cv.rotate(ang)
        cv.drawLine(-15, 0, 15, 0, stroke(INK, 9))
        cv.restore()
    if sp.get('glasses'):
        for side in (-1, 1):
            cv.drawCircle(hx + fo + side * 30, ey - 2, 24, stroke(INK, 5))
            cv.drawPath(ellipse(hx + fo + side * 30 - 8, ey - 12, 7, 4), fill('#ffffff', 0.5))
        cv.drawLine(hx + fo - 6, ey - 4, hx + fo + 6, ey - 4, ink(4))
    mx, my = hx + fo * 1.1, hy + 52
    if sp.get('moustache'):
        ms = path_smooth([(mx - 36, my - 2), (mx - 18, my - 20), (mx, my - 12), (mx + 18, my - 20), (mx + 36, my - 2), (mx, my - 4)])
        cv.drawPath(ms, x.f('#8a8a9e')); cv.drawPath(ms, ink(4))
        my += 6
    if sp.get('talk'):
        mouth = 'o' if int(x.t * 9) % 2 == 0 else ('smile' if mouth in ('smile', 'smirk', 'laugh') else 'line')
    _mouth(x, mouth, mx, my, x.t)
    # comic extras
    if sp['expr'] == 'scared':
        sx_, sy_ = hx + 92, hy - 46 + (x.t * 30) % 30
        dp = path_smooth([(sx_, sy_ - 22), (sx_ + 12, sy_), (sx_, sy_ + 10), (sx_ - 12, sy_)])
        cv.drawPath(dp, fill(g('#8fd0ff'))); cv.drawPath(dp, ink(3.5))
    if sp['expr'] == 'angry':
        for k, sx in enumerate((-1, 1)):
            pf = 1 + 0.2 * math.sin(x.t * 8 + k)
            for j in range(3):
                cv.drawCircle(hx + sx * (110 + j * 16), hy - 90 - j * 22, (14 - j * 3) * pf, fill('#f4f0f6', 0.92))
                cv.drawCircle(hx + sx * (110 + j * 16), hy - 90 - j * 22, (14 - j * 3) * pf, ink(3))
    # rim light on the lit edge
    from .light import MOODS
    key = MOODS[x.mood]['key']
    rim = skia.Path(); rim.addArc(skia.Rect.MakeLTRB(hx - R + 8, hy - R + 8, hx + R - 8, hy + R - 8), 150, 95)
    cv.drawPath(rim, stroke(mix(key, (255, 255, 255), 0.45), 9 if x.mood in ('sunset', 'dawn') else 6, 0.95 if x.mood in ('sunset', 'dawn') else 0.85))
    rim2 = skia.Path(); rim2.addArc(skia.Rect.MakeLTRB(hx - R + 8, hy - R + 8, hx + R - 8, hy + R - 8), -40, 70)
    cv.drawPath(rim2, stroke(mix(key, (255, 255, 255), 0.2), 4, 0.35))
    _hair(x, sp, hx, hy)
    wob = math.sin(x.t * 2.7 + sp['seed']) * 1.5 + P.get('wob', 0)
    _hat(x, sp, hx, hy, wob)
    cv.restore()


# ============================================================================ props
def _prop(x, kind, p, ang):
    cv, g = x.cv, x.g
    if not kind:
        return
    cv.save()
    cv.translate(*p)
    cv.rotate(-ang)
    if kind == 'wrench':
        cv.drawPath(rrect(-7, 0, 14, 90, 6), x.f('#9aa2b4')); cv.drawPath(rrect(-7, 0, 14, 90, 6), ink(4))
        hd = path_smooth([(-22, 92), (-18, 120), (-6, 108), (6, 108), (18, 120), (22, 92), (0, 84)])
        cv.drawPath(hd, x.f('#9aa2b4')); cv.drawPath(hd, ink(4))
    elif kind == 'mug':
        cv.drawPath(rrect(-20, 4, 40, 44, 8), x.f('#f4f1ea')); cv.drawPath(rrect(-20, 4, 40, 44, 8), ink(4))
        cv.drawPath(ellipse(24, 24, 10, 12), stroke(INK, 4))
        cv.drawLine(-12, 18, 12, 18, stroke(g('#c8343c'), 5))
        for k in (-8, 6):
            st = skia.Path(); st.moveTo(k, -2); st.quadTo(k + 10, -16, k, -28); cv.drawPath(st, stroke(g('#ffffff'), 3, 0.6))
    elif kind == 'club':
        club = path_smooth([(-7, -40), (7, -40), (14, 40), (26, 110), (22, 150), (0, 162), (-22, 150), (-24, 110), (-12, 40)])
        cv.drawPath(club, x.f('#9a6a3a'))
        cv.drawLine(-4, -30, 4, 140, stroke(g('#c89a5a'), 4, 0.7))
        for (kx, ky) in ((14, 96), (-16, 124), (8, 140)):
            cv.drawCircle(kx, ky, 5, x.f('#6a4022'))
        cv.drawPath(club, ink(4))
    elif kind == 'baton':
        cv.drawPath(rrect(-6, -10, 12, 80, 5), x.f('#2a2232')); cv.drawPath(rrect(-6, -10, 12, 80, 5), ink(3))
    elif kind == 'ladle':
        cv.drawPath(rrect(-4, -50, 8, 110, 4), x.f('#b8bccc')); cv.drawPath(rrect(-4, -50, 8, 110, 4), ink(3.5))
        cv.drawPath(ellipse(0, 66, 22, 16), x.f('#b8bccc')); cv.drawPath(ellipse(0, 66, 22, 16), ink(4))
    elif kind == 'sword':
        cv.drawPath(path_poly([(-9, 30), (9, 30), (7, 190), (0, 210), (-7, 190)]), x.f('#d8dce8'))
        cv.drawLine(0, 36, 0, 196, stroke(g('#ffffff'), 3, 0.7))
        cv.drawPath(path_poly([(-9, 30), (9, 30), (7, 190), (0, 210), (-7, 190)]), ink(4))
        cv.drawPath(rrect(-32, 18, 64, 14, 6), x.f('#e6b43c')); cv.drawPath(rrect(-32, 18, 64, 14, 6), ink(4))
        cv.drawPath(rrect(-6, -16, 12, 36, 4), x.f('#7a4a2a')); cv.drawPath(rrect(-6, -16, 12, 36, 4), ink(3.5))
        cv.drawCircle(0, -20, 9, x.f('#e6b43c')); cv.drawCircle(0, -20, 9, ink(3))
    elif kind == 'sceptre':
        cv.drawPath(rrect(-5, -120, 10, 200, 5), x.f('#e6b43c')); cv.drawPath(rrect(-5, -120, 10, 200, 5), ink(3.5))
        cv.drawCircle(0, -130, 18, x.f('#c8343c')); cv.drawCircle(0, -130, 18, ink(4))
        cv.drawCircle(-5, -136, 6, fill('#ffffff', 0.7))
    elif kind == 'flask':
        fl = path_poly([(-9, -30), (9, -30), (9, -6), (30, 40), (-30, 40), (-9, -6)])
        cv.drawPath(fl, fill(g('#e8f4f4'), 0.9))
        liq = path_poly([(-20, 18), (20, 18), (30, 40), (-30, 40)])
        cv.drawPath(liq, x.f('#5ad85a'))
        for k in range(3):
            cv.drawCircle(-6 + k * 8, 10 - (x.t * 40 + k * 13) % 40, 4, stroke(g('#5ad85a'), 2.5))
        cv.drawPath(fl, ink(4))
    elif kind == 'scanner':
        sc = path_poly([(-14, -10), (14, -10), (20, 20), (40, 26), (40, 44), (-14, 44)])
        cv.drawPath(sc, x.f('#2a2232')); cv.drawPath(sc, ink(3.5))
        cv.drawLine(40, 34, 70, 34, stroke(g('#ff4040'), 3, 0.8))
    elif kind == 'telescope':
        cv.drawPath(rrect(-9, -20, 18, 120, 4), x.f('#c89848')); cv.drawPath(rrect(-9, -20, 18, 120, 4), ink(4))
        cv.drawPath(rrect(-12, 30, 24, 16, 3), x.f('#7a4a2a')); cv.drawPath(rrect(-12, 30, 24, 16, 3), ink(3))
    elif kind == 'balloon':
        sway = math.sin(x.t * 1.7) * 14
        st = skia.Path(); st.moveTo(0, 0); st.cubicTo(10, -60, -10 + sway, -120, sway, -170)
        cv.drawPath(st, ink(2.5))
        b = ellipse(sway, -220, 42, 50)
        cv.drawPath(b, x.f('#d84a6a')); cv.drawPath(ellipse(sway - 14, -238, 10, 16), fill('#ffffff', 0.5)); cv.drawPath(b, ink(5))
    cv.restore()


# ============================================================================ main
def draw_character(cv, spec, x, y, scale, t, mood_name='day'):
    sp = dict(spec)
    P = pose_angles(sp['pose'], t, sp['seed'])
    kid = sp.get('kid')
    leg = 112 if kid else 150
    sp['_hem'] = -leg + (40 if sp.get('robe') else 0) + (55 if sp.get('coat') else 0)
    ctx = Ctx(cv, sp, mood_name, t)
    g = ctx.g
    cv.save()
    cv.translate(x, y)
    s = scale * (0.86 if kid else 1.0)
    cv.scale(s * sp['dir'], s)
    bob = P['bob']
    cv.translate(0, bob)
    # -- legs (behind torso)
    hipy = -leg
    shoe = g(sp['shoes'])
    for side, key in ((-1, 'leg_b'), (1, 'leg_f')):
        a1, a2 = P[key]
        hip = (side * 26, hipy - 4)
        Lth = leg * 0.53
        p1, p2 = _limb(cv, hip, a1, a2, Lth, leg - Lth + 6)
        sh = path_smooth([(p2[0] - 12, p2[1] - 6), (p2[0] + 26, p2[1] - 8), (p2[0] + 30, p2[1] + 6), (p2[0] - 14, p2[1] + 8)])
        cv.drawPath(sh, fill(shoe)); cv.drawPath(sh, ink(5))
    if kid and 'shorts' in sp['parts']:
        sh = rrect(-52, hipy - 30, 104, 44, 10)
        cv.drawPath(sh, ctx.f(sp['pants'])); cv.drawPath(sh, ink(5))
    # -- torso
    cv.save()
    cv.rotate(P['lean'])
    cv.scale(1, P['sq'])
    tp, sw, hw, top, hem = _torso_path(sp)
    # back arm behind torso
    sh_y = top + 18 + P['shoulder']
    arms = []
    for side, key, hk in ((-1, 'arm_b', 'hand_b'), (1, 'arm_f', 'hand_f')):
        arms.append((side, P[key], P[hk]))
    def draw_arm(side, angs, hk, prop=None):
        sh_ = (side * (sw - 6), sh_y)
        L1, L2 = 62, 58
        if P['cross'] and True:
            p1 = _seg(sh_, angs[0], L1)
            ang2 = angs[1]
            p2 = _seg(p1, ang2, L2)
            cv.drawLine(*sh_, *p1, ink(LIMB))
            cv.drawLine(*p1, *p2, ink(LIMB))
            _hand(ctx, 'mitt', p2, ang2, cv)
            return p2, ang2
        p1, p2 = _limb(cv, sh_, angs[0], angs[1], L1, L2)
        if prop:
            _prop(ctx, prop, p2, angs[1])
        _hand(ctx, hk, p2, angs[1], cv)
        return p2, angs[1]
    if not P['cross']:
        draw_arm(*arms[0])
    if sp.get('scarf'):
        sway = math.sin(t * 3.0 + 1) * 10
        sc = path_smooth([(-30, top + 10), (-60 - sway, top + 70), (-92 - sway * 1.5, top + 120), (-70 - sway, top + 126), (-36, top + 30)])
        cv.drawPath(sc, ctx.f(sp['scarf'])); cv.drawPath(sc, ink(4))
    cv.drawPath(tp, ctx.f(sp['torso']))
    # torso shade side + rim
    cv.save(); cv.clipPath(tp, doAntiAlias=True)
    shd = skia.Path(); shd.addOval(skia.Rect.MakeLTRB(hw * 0.25, top - 60, hw * 2.2, hem + 60))
    _draw_parts(ctx, sp, tp, sw, hw, top, hem)
    cv.drawPath(shd, fill(g((0x4a, 0x30, 0x66)), 0.20))
    gl = skia.Path(); gl.addOval(skia.Rect.MakeLTRB(-hw * 0.82, top + 20, -hw * 0.5, hem - 40))
    cv.drawPath(gl, fill('#ffffff', 0.14))
    cv.restore()
    from .light import MOODS
    key = MOODS[mood_name]['key']
    cv.save(); cv.clipPath(tp, doAntiAlias=True)
    tl = skia.Paint(AntiAlias=True)
    tl.setShader(lin_grad((0, top - 20), (0, hem), [argb((255, 255, 255), 0.16), argb((255, 255, 255), 0), argb((40, 20, 60), 0.22)], [0, 0.45, 1]))
    cv.drawRect(skia.Rect.MakeLTRB(-200, top - 30, 200, hem + 10), tl)
    cv.restore()
    rim = skia.Path(); rim.moveTo(-sw - 2, top + 20); rim.cubicTo(-sw - 16, top + 70, -hw - 4, hem - 70, -hw + 2, hem - 16)
    cv.drawPath(rim, stroke(mix(key, (255, 255, 255), 0.4), 5, 0.75))
    cv.drawPath(tp, ink(7.5))
    if sp.get('scarf'):
        cv.drawPath(rrect(-sw - 6, top - 8, (sw + 6) * 2, 26, 12), ctx.f(sp['scarf'])); cv.drawPath(rrect(-sw - 6, top - 8, (sw + 6) * 2, 26, 12), ink(4))
    # front arm
    if P['cross']:
        draw_arm(*arms[0])
        draw_arm(*arms[1])
    else:
        prop = sp.get('prop') if (sp.get('show_prop', True) and not P.get('noprop')) else None
        if sp.get('hold_fn'):
            prop = None
        hp, ha = draw_arm(*arms[1], prop=prop)
        if sp.get('hold_fn'):
            cv.save(); cv.translate(*hp); sp['hold_fn'](cv, t, mood_name); cv.restore()
            _hand(ctx, 'mitt', hp, ha, cv)
    # head
    _draw_head(ctx, sp, 0, top - 75, P['head_tilt'], P)
    cv.restore()
    cv.restore()


def head_box(scale):
    """Approx. head centre offset from the feet (for framing)."""
    return (0, -375 * scale)
