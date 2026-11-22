"""Moods (light = act structure), colour grading and light effects."""
import math

import numpy as np
import skia

from .paint import C, fill, rgb, mix, path_poly, rad_grad, lin_grad, argb, blurred, PLUM

# amb: multiplier on albedo for the set; camb: lighter multiplier for characters (they stay readable)
# shadow: tint pulled into dark tones; warm: added to highlights; sat: saturation; lift: black lift strength
MOODS = {
    'day': dict(amb=(1.02, 1.0, 0.97), camb=(1.0, 0.99, 0.97), shadow=(0x5a, 0x3a, 0x6e), warm=(0.06, 0.04, -0.02),
                sat=1.12, lift=0.9, con=1.22, vignette=(206, 196, 210), sky=('#2f5fd0', '#7fa8ec', '#e9d9c6'),
                key=(255, 236, 200), fog=(196, 214, 236), shadow_cast=(0x5a, 0x4a, 0x8a)),
    'interior': dict(con=1.2, amb=(0.98, 0.92, 0.84), camb=(1.02, 0.98, 0.92), shadow=(0x5e, 0x36, 0x58), warm=(0.07, 0.04, -0.03),
                     sat=1.06, lift=0.9, vignette=(212, 200, 205), sky=('#6f9ae0', '#b3cdef', '#f2e6d0'),
                     key=(255, 228, 180), fog=(236, 222, 200), shadow_cast=(0x5e, 0x40, 0x6a)),
    'night': dict(con=1.15, amb=(0.36, 0.42, 0.96), camb=(0.76, 0.79, 1.0), shadow=(0x27, 0x23, 0x55), warm=(0.0, 0.0, 0.0),
                  sat=1.15, lift=1.0, vignette=(196, 192, 214), sky=('#141a4e', '#2c3a92', '#4a5cb8'),
                  key=(255, 190, 110), fog=(70, 84, 170), shadow_cast=(0x1c, 0x18, 0x48)),
    'dream': dict(amb=(1.06, 0.74, 1.04), camb=(1.02, 0.84, 1.0), shadow=(0x5a, 0x22, 0x6e), warm=(0.08, 0.0, 0.05),
                  sat=1.3, lift=1.0, vignette=(214, 190, 220), sky=('#5a2a9a', '#c450b0', '#ff9ad0'),
                  key=(255, 200, 240), fog=(230, 150, 210), shadow_cast=(0x5a, 0x22, 0x7e)),
    'golden': dict(con=1.2, shw=0.7, amb=(1.04, 0.84, 0.6), camb=(1.06, 0.92, 0.72), shadow=(0x4a, 0x2e, 0x5a), warm=(0.10, 0.06, -0.04),
                   sat=1.0, lift=0.95, vignette=(206, 180, 170), sky=('#c96a2a', '#f0a650', '#ffe3a0'),
                   key=(255, 214, 120), fog=(240, 190, 120), shadow_cast=(0x6a, 0x30, 0x40)),
    'sunset': dict(con=1.2, shw=0.8, amb=(1.0, 0.74, 0.8), camb=(0.9, 0.74, 0.8), shadow=(0x42, 0x22, 0x66), warm=(0.10, 0.04, -0.02),
                   sat=1.0, lift=1.0, vignette=(206, 184, 200), sky=('#4a3a8e', '#c4609a', '#ffb070'),
                   key=(255, 190, 120), fog=(236, 160, 150), shadow_cast=(0x4a, 0x28, 0x70)),
    'dawn': dict(amb=(1.02, 0.86, 0.96), camb=(1.02, 0.92, 0.98), shadow=(0x52, 0x34, 0x72), warm=(0.06, 0.03, 0.02),
                 sat=1.1, lift=1.0, vignette=(212, 198, 214), sky=('#4a66d8', '#b88ad8', '#ffc4c0'),
                 key=(255, 214, 200), fog=(236, 200, 220), shadow_cast=(0x5a, 0x3e, 0x86)),
}


def mood(name):
    return MOODS[name]


def _grade_arr(x, m, amb):
    """x float32 (...,3) in 0-1 -> graded."""
    lum = x[..., 0] * 0.3 + x[..., 1] * 0.59 + x[..., 2] * 0.11
    y = x * np.array(amb, np.float32)
    l2 = (y[..., 0] * 0.3 + y[..., 1] * 0.59 + y[..., 2] * 0.11)[..., None]
    y = l2 + (y - l2) * m['sat']
    con = m.get('con', 1.15)
    l3 = (y[..., 0] * 0.3 + y[..., 1] * 0.59 + y[..., 2] * 0.11)[..., None]
    y = y + (np.clip(0.5 + (l3 - 0.5) * con, 0, 1.2) - l3)        # luminance S-curve, hue kept
    sh = np.array(m['shadow'], np.float32) / 255.0
    w = np.clip((0.45 - lum) / 0.45, 0, 1)[..., None] ** 1.2 * m.get('shw', 0.6)
    y = y + (sh * np.clip(lum[..., None] * 1.6 + 0.35, 0, 1) - y) * w
    hw = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None]
    y = y + np.array(m['warm'], np.float32) * hw
    plum = np.array(PLUM, np.float32) / 255.0 * m['lift'] * 0.55
    y = plum + np.clip(y, 0, 1) * (1 - plum)
    return np.clip(y, 0, 1)


def grade_array(rgba, m, amb=None):
    """Grade an RGBA uint8 array (unpremultiplied) in place-ish; returns new array."""
    x = rgba[..., :3].astype(np.float32) / 255.0
    y = _grade_arr(x, m, amb or m['amb'])
    out = rgba.copy()
    out[..., :3] = (y * 255 + 0.5).astype(np.uint8)
    return out


def grade_color(c, m, char=True):
    x = np.array(rgb(c), np.float32)[None, :] / 255.0
    y = _grade_arr(x, m, m['camb'] if char else m['amb'])[0]
    return tuple(int(v * 255 + 0.5) for v in y)


# ----------------------------------------------------------------------------- effects (draw on canvas)
def halo(cv, x, y, r, col=(255, 190, 110), a=0.85, core=0.18, hot=True):
    """Soft bloom halo around a practical light (additive). hot=False: no white centre (glowing screens and displays)."""
    p = skia.Paint(AntiAlias=True)
    p.setShader(rad_grad((x, y), r, [argb(col, a), argb(col, a * 0.35), argb(col, 0)], [core, 0.45, 1.0]))
    p.setBlendMode(skia.BlendMode.kPlus)
    cv.drawCircle(x, y, r, p)
    if not hot:
        return
    p2 = skia.Paint(AntiAlias=True)
    p2.setShader(rad_grad((x, y), r * 0.22, [argb((255, 250, 230), 0.95), argb(col, 0)], [0.25, 1.0]))
    p2.setBlendMode(skia.BlendMode.kPlus)
    cv.drawCircle(x, y, r * 0.22, p2)


def pool(cv, x, y, rx, ry, col=(255, 190, 110), a=0.5):
    """Light pool on a floor/wall (screen-ish additive ellipse)."""
    cv.save()
    cv.translate(x, y)
    cv.scale(1, ry / rx)
    p = skia.Paint(AntiAlias=True)
    p.setShader(rad_grad((0, 0), rx, [argb(col, a), argb(col, a * 0.4), argb(col, 0)], [0, 0.5, 1]))
    p.setBlendMode(skia.BlendMode.kScreen)
    cv.drawCircle(0, 0, rx, p)
    cv.restore()


def god_rays(cv, src, angle_deg, spread_deg, length, n=7, col=(255, 236, 190), a=0.22, seed=3, width=0.5):
    """Volumetric shafts fanning from src."""
    import random
    r = random.Random(seed)
    for i in range(n):
        ang = math.radians(angle_deg + (i / max(1, n - 1) - 0.5) * spread_deg + r.uniform(-2, 2))
        wdt = math.radians(r.uniform(0.6, 2.4) * width * 2)
        L = length * r.uniform(0.7, 1.0)
        p1 = (src[0] + math.cos(ang - wdt) * L, src[1] + math.sin(ang - wdt) * L)
        p2 = (src[0] + math.cos(ang + wdt) * L, src[1] + math.sin(ang + wdt) * L)
        pt = skia.Paint(AntiAlias=True)
        pt.setShader(lin_grad(src, (src[0] + math.cos(ang) * L, src[1] + math.sin(ang) * L),
                              [argb(col, a * r.uniform(0.6, 1.0)), argb(col, 0)]))
        pt.setBlendMode(skia.BlendMode.kScreen)
        blurred(pt, 10)
        cv.drawPath(path_poly([src, p1, p2]), pt)


def window_slash(cv, quad, col=(255, 236, 200), a=0.35):
    p = fill(col, a, blend=skia.BlendMode.kScreen)
    blurred(p, 6)
    cv.drawPath(path_poly(quad), p)


def cast_shadow(cv, x, y, rx, ry, m, a=0.45, dx=0.0):
    """Soft tinted contact/cast shadow (multiply)."""
    col = m['shadow_cast']
    p = skia.Paint(AntiAlias=True)
    cv.save()
    cv.translate(x + dx, y)
    cv.scale(1, ry / rx)
    p.setShader(rad_grad((0, 0), rx, [argb(col, a), argb(col, a * 0.7), argb(col, 0)], [0, 0.55, 1]))
    cv.drawCircle(0, 0, rx, p)
    cv.restore()


def long_shadow(cv, foot, length, angle_deg, width, m, a=0.4):
    col = m['shadow_cast']
    ang = math.radians(angle_deg)
    nx, ny = -math.sin(ang), math.cos(ang)
    end = (foot[0] + math.cos(ang) * length, foot[1] + math.sin(ang) * length)
    quad = [(foot[0] - nx * width / 2, foot[1] - ny * width / 2), (end[0] - nx * width * 0.35, end[1] - ny * width * 0.35),
            (end[0] + nx * width * 0.35, end[1] + ny * width * 0.35), (foot[0] + nx * width / 2, foot[1] + ny * width / 2)]
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_grad(foot, end, [argb(col, a), argb(col, a * 0.15)]))
    blurred(p, 5)
    cv.drawPath(path_poly(quad), p)


def vignette(cv, w, h, m, strength=1.0):
    col = m['vignette']
    col = tuple(int(255 - (255 - c) * strength) for c in col)
    p = skia.Paint()
    p.setShader(rad_grad((w / 2, h * 0.46), math.hypot(w, h) * 0.56,
                         [argb((255, 255, 255)), argb((255, 255, 255)), argb(col)], [0, 0.45, 1.0]))
    p.setBlendMode(skia.BlendMode.kMultiply)
    cv.drawRect(skia.Rect.MakeWH(w, h), p)
