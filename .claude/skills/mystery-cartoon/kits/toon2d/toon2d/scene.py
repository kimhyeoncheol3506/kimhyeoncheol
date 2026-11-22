"""Depth layers + pinhole parallax camera + bake cache + per-frame compositing and post."""
import hashlib
import math
import os

import numpy as np
import skia

from .paint import (C, fill, surface, to_array, from_array, blur_image, LINEAR, argb, rad_grad)
from .light import MOODS, grade_array, vignette

W, H = 1080, 1920
CX, CY = W / 2, H / 2
# plane bitmaps cover plane coords [-MX, W+MX] x [-MY, H+MY]
MX, MY = 420, 560
ENGINE_VERSION = 'v4'


class Layer:
    def __init__(self, name, z, img=None, ox=MX, oy=MY):
        self.name, self.z, self.img, self.ox, self.oy = name, z, img, ox, oy
        self.live = []  # callables fn(cv, t, mood_name) in plane coords


class Canvas:
    """A paintable plane in plane coords (bitmap with margins)."""

    def __init__(self, mx=MX, my=MY):
        self.mx, self.my = mx, my
        self.s = surface(W + 2 * mx, H + 2 * my)
        self.cv = self.s.getCanvas()
        self.cv.translate(mx, my)

    def image(self):
        return self.s.makeImageSnapshot()


def bake_plane(painter, mood_name, grade=True, haze=0.0, blur=0.0, lights=None, mx=MX, my=MY):
    """painter(cv) paints albedo in plane coords; lights(cv, mood) adds emissive passes after grading."""
    m = MOODS[mood_name]
    c = Canvas(mx, my)
    painter(c.cv)
    img = c.image()
    if grade:
        arr = to_array(img)
        arr = grade_array(arr, m)
        img = from_array(arr)
    if lights or haze > 0:
        s = surface(img.width(), img.height())
        cv = s.getCanvas()
        cv.drawImage(img, 0, 0)
        if haze > 0:
            p = fill(m['fog'], haze, blend=skia.BlendMode.kSrcATop)
            cv.drawRect(skia.Rect.MakeWH(img.width(), img.height()), p)
        if lights:
            cv.save()
            cv.translate(mx, my)
            lights(cv, m)
            cv.restore()
        img = s.makeImageSnapshot()
    if blur > 0:
        img = blur_image(img, blur)
    return img


_SRC_HASH = None


def _src_hash():
    global _SRC_HASH
    if _SRC_HASH is None:
        here = os.path.dirname(os.path.abspath(__file__))
        h = hashlib.md5()
        for f in sorted(os.listdir(here)):
            if f.endswith('.py') and f not in ('character.py', 'text.py', 'render.py', 'cli.py'):
                with open(os.path.join(here, f), 'rb') as fh:
                    h.update(fh.read())
        _SRC_HASH = h.hexdigest()[:10]
    return _SRC_HASH


def cached(key, fn, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    h = hashlib.md5((ENGINE_VERSION + _src_hash() + key).encode()).hexdigest()[:16]
    path = os.path.join(cache_dir, h + '.png')
    if os.path.exists(path):
        return skia.Image.open(path).makeRasterImage()
    img = fn().makeRasterImage()
    img.save(path, skia.kPNG)
    return img


# ----------------------------------------------------------------------------- camera
class Cam:
    def __init__(self, x=0.0, y=0.0, z=0.0, roll=0.0, zoom=1.0):
        self.x, self.y, self.z, self.roll, self.zoom = x, y, z, roll, zoom

    def lerp(self, o, t):
        return Cam(*(a + (b - a) * t for a, b in zip(
            (self.x, self.y, self.z, self.roll, self.zoom), (o.x, o.y, o.z, o.roll, o.zoom))))

    def tuple(self):
        return (self.x, self.y, self.z, self.roll, self.zoom)


FAST = skia.SamplingOptions(skia.FilterMode.kLinear)
BLUR_MAX = 22.0   # max motion-blur smear per frame (px at the subject plane)


def plane_matrix(cam, z, roll=True):
    s = z / max(0.05, (z - cam.z)) * cam.zoom
    m = skia.Matrix()
    m.preTranslate(CX, CY)
    if roll:
        m.preRotate(cam.roll)
    m.preScale(s, s)
    m.preTranslate(-CX - cam.x / z, -CY - cam.y / z)
    return m


def to_screen(cam, z, u, v):
    m = plane_matrix(cam, z)
    p = m.mapXY(u, v)
    return p.x(), p.y()


# ----------------------------------------------------------------------------- render
def composite(cv, layers, cam, t, mood_name, alpha=1.0, actor_cam=None):
    """actor_cam: camera for layers with live drawers (characters). During motion blur the characters use the
    centre-of-shutter camera, so they stay sharp (ink readable) while the painted planes blur."""
    for L in sorted(layers, key=lambda l: -l.z):
        c = actor_cam if (actor_cam is not None and L.live) else cam
        if L.z - c.z < 0.06:
            continue
        a = alpha
        if L.z < 0.8 and not L.live:
            # blurred foreground planes fade out before the camera magnifies them into a smear
            mag = L.z / max(0.05, L.z - c.z) * c.zoom
            a *= max(0.0, min(1.0, (2.0 - mag) / 0.6))
            if a <= 0.01:
                continue
        cv.save()
        cv.concat(plane_matrix(c, L.z, roll=False))   # roll is applied once to the whole frame
        if L.img is not None:
            p = skia.Paint()
            p.setAlphaf(a)
            cv.drawImage(L.img, -L.ox, -L.oy, FAST, p)
        for fn in L.live:
            fn(cv, t, mood_name)
        cv.restore()


def bloom(surf, strength=0.5, thresh=0.72):
    """Fast bloom: 1/8 downsample, keep only bright parts (alpha = brightness above threshold), blur,
    then draw back with plain src-over (other blend modes leave skia's fast path: 200+ ms)."""
    img = surf.makeImageSnapshot()
    sw, sh = W // 8, H // 8
    small = surface(sw, sh)
    sc = small.getCanvas()
    sc.save(); sc.scale(1 / 8, 1 / 8); sc.drawImage(img, 0, 0, FAST); sc.restore()
    arr = to_array(small).astype(np.float32) / 255.0
    lum = arr[..., :3].max(axis=2)
    a = np.clip((lum - thresh) / (1 - thresh), 0, 1) * strength
    out = np.empty_like(arr)
    out[..., :3] = np.clip(arr[..., :3] * 1.15 + 0.08, 0, 1)
    out[..., 3] = a
    b = blur_image(from_array(out * 255), 5)
    cv = surf.getCanvas()
    cv.save(); cv.scale(8, 8); cv.drawImage(b, 0, 0, FAST); cv.restore()


class Shot:
    """One continuous set-up: a set (layers), a mood, characters, a camera path."""

    def __init__(self, layers, mood_name, cam_fn, post=None, vignette_strength=1.3, bloom_strength=0.45):
        self.layers, self.mood, self.cam_fn = layers, mood_name, cam_fn
        self.post = post or []
        self.vs, self.bs = vignette_strength, bloom_strength

    def render(self, t, surf=None, subframes=None, dt=1 / 30):
        surf = surf or surface(W, H)
        cv = surf.getCanvas()
        cam = self.cam_fn(t)
        c2 = self.cam_fn(t + dt)
        d = math.hypot(c2.x - cam.x, c2.y - cam.y) + abs(c2.z - cam.z) * 900 + abs(c2.zoom - cam.zoom) * 900 + abs(c2.roll - cam.roll) * 10
        shutter = min(0.95, BLUR_MAX / max(d, 1e-6))          # cap the smear length on fast moves
        if subframes is None:
            e = d * shutter
            subframes = 1 if e < 10 else 3
        if subframes <= 1:
            cv.clear(argb((0x2f, 0x23, 0x2e)))
            composite(cv, self.layers, cam, t, self.mood)
        else:
            # motion blur: running average of sub-frames, all on skia's fast path
            cv.clear(argb((0x2f, 0x23, 0x2e)))
            s2 = _scratch()
            for k in range(subframes):
                tk = t + dt * ((k + 0.5) / subframes - 0.5) * shutter
                c2 = s2.getCanvas()
                c2.clear(argb((0x2f, 0x23, 0x2e)))
                composite(c2, self.layers, self.cam_fn(tk), t, self.mood, actor_cam=cam)
                p = skia.Paint(); p.setAlphaf(1.0 / (k + 1))
                cv.drawImage(s2.makeImageSnapshot(), 0, 0, FAST, p)
        if abs(cam.roll) > 0.05:
            img = surf.makeImageSnapshot()
            cv.clear(argb((0x2f, 0x23, 0x2e)))
            cv.save(); cv.translate(CX, CY); cv.rotate(cam.roll); r = abs(math.cos(math.radians(cam.roll))) + abs(math.sin(math.radians(cam.roll))) * H / W
            cv.scale(r, r); cv.translate(-CX, -CY)
            cv.drawImage(img, 0, 0, FAST); cv.restore()
        for fn in self.post:
            fn(cv, t, self.mood, cam)
        if self.bs > 0:
            bloom(surf, self.bs)
        cv.drawImage(_vignette_img(self.mood, self.vs), 0, 0, FAST)
        return surf


_MULT = skia.Paint()
_SCR = []


def _scratch():
    if not _SCR:
        _SCR.append(surface(W, H))
    return _SCR[0]

_VIG = {}


def _vignette_img(mood, strength):
    """Vignette as a src-over overlay: plum with alpha = 1 - multiply factor (same darkening, fast path)."""
    k = (mood, round(strength, 2))
    if k not in _VIG:
        s = surface(W, H, (255, 255, 255))
        vignette(s.getCanvas(), W, H, MOODS[mood], strength)
        mul = to_array(s).astype(np.float32)[..., :3].mean(axis=2) / 255.0
        ov = np.zeros((H, W, 4), np.float32)
        ov[..., 0], ov[..., 1], ov[..., 2] = 0x2f, 0x23, 0x2e
        ov[..., 3] = np.clip(1 - mul, 0, 1) * 255
        _VIG[k] = from_array(ov).makeRasterImage()
    return _VIG[k]
