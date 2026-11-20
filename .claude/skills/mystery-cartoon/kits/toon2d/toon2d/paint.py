"""Low-level drawing toolkit on top of skia: colours, paints, ink, textures, perspective."""
import math
import os
import random

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
INK = (0x1b, 0x12, 0x20)          # deep plum ink, never pure black
PLUM = (0x2f, 0x23, 0x2e)         # darkest fill allowed
LINEAR = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


# ----------------------------------------------------------------------------- colour
def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def C(c, a=1.0):
    """Any colour spec -> skia Color4f. c: '#hex', (r,g,b) 0-255, or Color4f."""
    if isinstance(c, skia.Color4f):
        return skia.Color4f(c.fR, c.fG, c.fB, c.fA * a)
    if isinstance(c, str):
        c = hexc(c)
    if len(c) == 4:
        a = a * c[3] / 255.0
    return skia.Color4f(c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, a)


def rgb(c):
    if isinstance(c, str):
        return hexc(c)
    return tuple(int(v) for v in c[:3])


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def shade(c, k):
    """k<0 darker toward plum-violet, k>0 lighter toward warm cream."""
    if k < 0:
        return mix(c, (0x3a, 0x26, 0x48), -k)
    return mix(c, (0xff, 0xf4, 0xdc), k)


# ----------------------------------------------------------------------------- paints
def fill(c, a=1.0, blend=None, shader=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(C(c, a))
    if blend is not None:
        p.setBlendMode(blend)
    if shader is not None:
        p.setShader(shader)
    return p


def stroke(c, w, a=1.0, cap=skia.Paint.kRound_Cap, join=skia.Paint.kRound_Join, blend=None):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=cap, StrokeJoin=join)
    p.setColor4f(C(c, a))
    if blend is not None:
        p.setBlendMode(blend)
    return p


def ink(w, a=1.0):
    return stroke(INK, w, a)


def blurred(paint, sigma):
    if sigma > 0.3:
        paint.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return paint


def lin_grad(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)],
                                          [C(c).toColor() if not isinstance(c, int) else c for c in cols], pos)


def rad_grad(ctr, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*ctr), r,
                                          [C(c).toColor() if not isinstance(c, int) else c for c in cols], pos)


def argb(c, a=1.0):
    c = rgb(c)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), c[0], c[1], c[2])


# ----------------------------------------------------------------------------- paths
def path_poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def path_smooth(pts, close=True, tension=0.5):
    """Catmull-Rom through points -> cubic path."""
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else pts[(i + 1) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def rrect(x, y, w, h, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    return p


def ellipse(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def draw_inked(cv, path, col, w=3.0, a=1.0, ink_a=1.0):
    cv.drawPath(path, fill(col, a))
    if w > 0:
        cv.drawPath(path, ink(w, ink_a))


# ----------------------------------------------------------------------------- surfaces
def surface(w, h, clear=None):
    s = skia.Surface(int(w), int(h))
    s.getCanvas().clear(C(clear).toColor() if clear is not None else skia.ColorTRANSPARENT)
    return s


def to_array(img_or_surface):
    img = img_or_surface.makeImageSnapshot() if isinstance(img_or_surface, skia.Surface) else img_or_surface
    return img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)


def from_array(a):
    """RGBA (unpremultiplied) array -> premultiplied raster image (premul keeps draws on skia's fast path)."""
    a = a.astype(np.float32)
    al = a[..., 3:4] / 255.0
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], axis=2)
    pm = np.ascontiguousarray(np.clip(pm + 0.5, 0, 255).astype(np.uint8))
    img = skia.Image.fromarray(pm, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    # convert once to the surface's native pixel format (BGRA on Windows) so later draws never swizzle
    s = skia.Surface(img.width(), img.height())
    s.getCanvas().clear(skia.ColorTRANSPARENT)
    s.getCanvas().drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(BlendMode=skia.BlendMode.kSrc))
    return s.makeImageSnapshot().makeRasterImage()


def blur_image(img, sigma):
    if sigma < 0.3:
        return img
    s = surface(img.width(), img.height())
    p = skia.Paint(ImageFilter=skia.ImageFilters.Blur(sigma, sigma, skia.TileMode.kDecal))
    s.getCanvas().drawImage(img, 0, 0, LINEAR, p)
    return s.makeImageSnapshot()


# ----------------------------------------------------------------------------- perspective
def quad_matrix(w, h, quad):
    """Matrix mapping rect (0,0,w,h) onto quad [tl, tr, br, bl]."""
    m = skia.Matrix()
    m.setPolyToPoly([skia.Point(0, 0), skia.Point(w, 0), skia.Point(w, h), skia.Point(0, h)],
                    [skia.Point(*q) for q in quad])
    return m


def draw_tex_quad(cv, tex_img, quad, alpha=1.0):
    """Draw a texture image warped onto a 4-point quad (perspective)."""
    cv.save()
    cv.clipPath(path_poly(quad), doAntiAlias=True)
    cv.concat(quad_matrix(tex_img.width(), tex_img.height(), quad))
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(alpha)
    cv.drawImage(tex_img, 0, 0, LINEAR, p)
    cv.restore()


def draw_in_quad(cv, w, h, quad, fn):
    """Run fn(canvas) in a w x h design space mapped onto quad."""
    cv.save()
    cv.clipPath(path_poly(quad), doAntiAlias=True)
    cv.concat(quad_matrix(w, h, quad))
    fn(cv)
    cv.restore()


# ----------------------------------------------------------------------------- noise
def rng(seed):
    return random.Random(seed)


def value_noise(w, h, scale, seed=0, octaves=3):
    """Smooth value noise in [0,1], numpy, (h, w)."""
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / (2 ** o)))
        gw, gh = w // s + 3, h // s + 3
        g = r.random((gh, gw)).astype(np.float32)
        ys = np.linspace(0, h / s, h, endpoint=False)
        xs = np.linspace(0, w / s, w, endpoint=False)
        y0 = ys.astype(int); x0 = xs.astype(int)
        fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
        out += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
        tot += amp
        amp *= 0.5
    return out / tot
