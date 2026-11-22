"""Flat material textures (painted, inked). They are warped into perspective by the sets."""
import math

import numpy as np
import skia

from .paint import (C, fill, stroke, ink, shade, mix, rgb, surface, rng, path_poly, path_smooth,
                    rrect, ellipse, blurred, lin_grad, INK)


def _img(s):
    return s.makeImageSnapshot()


def wood_planks(w, h, plank=90, base='#b07a45', vertical=False, seed=1, gap=3.0, nails=True, grain=True):
    """Planks running along the long axis. vertical=True -> planks run top-bottom."""
    W, H = (h, w) if vertical else (w, h)
    s = surface(W, H, base)
    cv = s.getCanvas()
    r = rng(seed)
    y = 0
    while y < H:
        ph = plank * r.uniform(0.85, 1.15)
        x = -r.uniform(0, 300)
        while x < W:
            L = r.uniform(380, 900)
            col = shade(base, r.uniform(-0.18, 0.12))
            cv.drawRect(skia.Rect.MakeXYWH(x, y, L, ph), fill(col))
            # top-light bevel and lower shade
            cv.drawRect(skia.Rect.MakeXYWH(x, y, L, ph * 0.12), fill(shade(col, 0.22), 0.6))
            cv.drawRect(skia.Rect.MakeXYWH(x, y + ph * 0.8, L, ph * 0.2), fill(shade(col, -0.25), 0.45))
            if grain:
                for g in range(r.randint(3, 6)):
                    gy = y + r.uniform(0.18, 0.82) * ph
                    pts = []
                    amp = r.uniform(1, 5)
                    for k in range(12):
                        px = x + L * k / 11
                        pts.append((px, gy + amp * math.sin(k * r.uniform(0.6, 1.4) + g)))
                    cv.drawPath(path_smooth(pts, close=False), stroke(shade(col, -0.35), r.uniform(1.0, 2.2), 0.55))
                if r.random() < 0.5:
                    kx, ky = x + r.uniform(0.2, 0.8) * L, y + r.uniform(0.3, 0.7) * ph
                    cv.drawPath(ellipse(kx, ky, r.uniform(8, 16), r.uniform(4, 7)), stroke(shade(col, -0.4), 2, 0.7))
                    cv.drawPath(ellipse(kx, ky, 3, 2), fill(shade(col, -0.45)))
            if nails:
                for nx in (x + 18, x + L - 18):
                    for ny in (y + ph * 0.3, y + ph * 0.7):
                        cv.drawCircle(nx, ny, 3.2, fill(shade(col, -0.55)))
                        cv.drawCircle(nx - 1, ny - 1, 1.2, fill(shade(col, 0.4), 0.8))
            cv.drawLine(x, y, x, y + ph, stroke(INK, gap, 0.85))
            x += L
        cv.drawLine(0, y, W, y, stroke(INK, gap, 0.9))
        y += ph
    img = _img(s)
    if vertical:
        s2 = surface(w, h)
        c2 = s2.getCanvas()
        c2.translate(w, 0)
        c2.rotate(90)
        c2.drawImage(img, 0, 0)
        img = _img(s2)
    return img


def bricks(w, h, bw=120, bh=46, base='#a04a32', mortar='#c9a88a', seed=2, ink_a=0.7):
    s = surface(w, h, mortar)
    cv = s.getCanvas()
    r = rng(seed)
    row = 0
    y = 0
    while y < h:
        off = (bw / 2) if row % 2 else 0
        x = -off
        while x < w:
            col = shade(base, r.uniform(-0.2, 0.15))
            rr = rrect(x + 3, y + 3, bw - 6, bh - 6, 4)
            cv.drawPath(rr, fill(col))
            cv.drawRect(skia.Rect.MakeXYWH(x + 5, y + 4, bw - 10, (bh - 8) * 0.25), fill(shade(col, 0.2), 0.5))
            cv.drawRect(skia.Rect.MakeXYWH(x + 5, y + bh - 10, bw - 10, 5), fill(shade(col, -0.3), 0.5))
            if r.random() < 0.25:
                cx, cy = x + r.uniform(15, bw - 15), y + r.uniform(10, bh - 10)
                cv.drawLine(cx, cy, cx + r.uniform(-14, 14), cy + r.uniform(-8, 8), stroke(shade(col, -0.45), 1.6, 0.8))
            cv.drawPath(rr, ink(2.0, ink_a))
            x += bw
        y += bh
        row += 1
    return _img(s)


def checker_tiles(w, h, size=110, c1='#e8e1d4', c2='#8a6d4b', seed=3, gloss=True):
    s = surface(w, h, c1)
    cv = s.getCanvas()
    r = rng(seed)
    for j in range(int(h // size) + 2):
        for i in range(int(w // size) + 2):
            col = c1 if (i + j) % 2 == 0 else c2
            col = shade(col, r.uniform(-0.06, 0.05))
            cv.drawRect(skia.Rect.MakeXYWH(i * size, j * size, size, size), fill(col))
            if gloss:
                pth = path_poly([(i * size + 8, j * size + 8), (i * size + size * 0.55, j * size + 8),
                                 (i * size + 8, j * size + size * 0.55)])
                cv.drawPath(pth, fill('#ffffff', 0.10))
    for k in range(int(w // size) + 2):
        cv.drawLine(k * size, 0, k * size, h, stroke(shade(c1, -0.5), 3, 0.6))
    for k in range(int(h // size) + 2):
        cv.drawLine(0, k * size, w, k * size, stroke(shade(c1, -0.5), 3, 0.6))
    return _img(s)


def gravel(w, h, palette=('#8d8f96', '#a7a9ae', '#6f7178', '#bfc0c2', '#5d5f66', '#9a958c'),
           base='#7a7c82', count=None, seed=4, smin=5, smax=14, ink_a=0.55):
    s = surface(w, h, base)
    cv = s.getCanvas()
    r = rng(seed)
    count = count or int(w * h / 260)
    for _ in range(count):
        x, y = r.uniform(0, w), r.uniform(0, h)
        rx = r.uniform(smin, smax)
        ry = rx * r.uniform(0.55, 0.85)
        col = r.choice(palette)
        cv.drawPath(ellipse(x, y + ry * 0.35, rx, ry), fill(shade(col, -0.5), 0.5))
        cv.drawPath(ellipse(x, y, rx, ry), fill(col))
        cv.drawPath(ellipse(x - rx * 0.25, y - ry * 0.35, rx * 0.45, ry * 0.3), fill(shade(col, 0.4), 0.7))
        cv.drawPath(ellipse(x, y, rx, ry), ink(1.3, ink_a))
    return _img(s)


def shingles(w, h, sw=70, sh=44, base='#5b5f8a', seed=5, scallop=False):
    s = surface(w, h, shade(base, -0.4))
    cv = s.getCanvas()
    r = rng(seed)
    row = 0
    y = -sh * 0.3
    while y < h:
        off = sw / 2 if row % 2 else 0
        x = -off
        while x < w:
            col = shade(base, r.uniform(-0.18, 0.14))
            if scallop:
                p = skia.Path()
                p.moveTo(x, y)
                p.lineTo(x + sw, y)
                p.lineTo(x + sw, y + sh * 0.6)
                p.arcTo(skia.Rect.MakeXYWH(x, y + sh * 0.2, sw, sh * 0.8), 0, 180, False)
                p.close()
            else:
                p = rrect(x + 1, y, sw - 2, sh * 1.25, 4)
            cv.drawPath(p, fill(col))
            cv.drawRect(skia.Rect.MakeXYWH(x + 4, y + sh * 0.95, sw - 8, sh * 0.25), fill(shade(col, -0.35), 0.6))
            cv.drawPath(p, ink(1.8, 0.7))
            x += sw
        y += sh
        row += 1
    return _img(s)


def clapboard(w, h, board=38, base='#9fc3c8', seed=6, ink_a=0.55):
    s = surface(w, h, base)
    cv = s.getCanvas()
    r = rng(seed)
    y = 0
    while y < h:
        col = shade(base, r.uniform(-0.04, 0.04))
        cv.drawRect(skia.Rect.MakeXYWH(0, y, w, board), fill(col))
        cv.drawRect(skia.Rect.MakeXYWH(0, y, w, board * 0.22), fill(shade(col, -0.25), 0.55))
        cv.drawRect(skia.Rect.MakeXYWH(0, y + board * 0.22, w, 2), fill(shade(col, 0.3), 0.6))
        cv.drawLine(0, y, w, y, stroke(INK, 1.8, ink_a))
        y += board
    return _img(s)


def wallpaper(w, h, base='#e9d9b8', motif='#c9a26b', stripe='#e0caa0', seed=7, step=70):
    s = surface(w, h, base)
    cv = s.getCanvas()
    for x in range(0, w + step, step):
        cv.drawRect(skia.Rect.MakeXYWH(x, 0, step * 0.42, h), fill(stripe, 0.7))
    r = rng(seed)
    for j in range(0, h + step, step):
        for i in range(0, w + step, step):
            ox = step / 2 if (j // step) % 2 else 0
            cx, cy = i + ox + step * 0.21, j + step / 2
            for k in range(4):
                a = k * math.pi / 2 + math.pi / 4
                cv.drawPath(ellipse(cx + math.cos(a) * 7, cy + math.sin(a) * 7, 5, 5), fill(motif, 0.85))
            cv.drawCircle(cx, cy, 3.2, fill(shade(motif, -0.4)))
    return _img(s)


def grass(w, h, base='#4f9a3c', seed=8, density=1.0, blade=26):
    s = surface(w, h, base)
    cv = s.getCanvas()
    r = rng(seed)
    n = int(w * h / 900 * density)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        col = shade(base, r.uniform(-0.3, 0.25))
        L = blade * r.uniform(0.5, 1.3)
        lean = r.uniform(-0.4, 0.4)
        p = path_poly([(x - 3, y), (x + L * lean, y - L), (x + 3, y)])
        cv.drawPath(p, fill(col))
    for _ in range(int(n / 40)):
        x, y = r.uniform(0, w), r.uniform(0, h)
        cv.drawCircle(x, y, r.uniform(3, 5), fill(r.choice(['#f3e27a', '#ffffff', '#f2a0c0']), 0.9))
    return _img(s)


def sand(w, h, base='#d9a066', seed=9):
    s = surface(w, h, base)
    cv = s.getCanvas()
    r = rng(seed)
    for k in range(int(h / 28)):
        y = k * 28 + r.uniform(-6, 6)
        pts = [(x, y + 5 * math.sin(x / r.uniform(60, 120) + k)) for x in range(-20, w + 40, 40)]
        cv.drawPath(path_smooth(pts, close=False), stroke(shade(base, -0.2), 2.5, 0.45))
    for _ in range(int(w * h / 1800)):
        x, y = r.uniform(0, w), r.uniform(0, h)
        rr = r.uniform(2, 7)
        col = shade(base, r.uniform(-0.4, 0.2))
        cv.drawPath(ellipse(x, y, rr, rr * 0.7), fill(col))
    return _img(s)


def stone_blocks(w, h, bw=160, bh=90, base='#9c9aa6', seed=10, mortar=None):
    mortar = mortar or shade(base, -0.45)
    s = surface(w, h, mortar)
    cv = s.getCanvas()
    r = rng(seed)
    row = 0
    y = 0
    while y < h:
        x = -(bw * 0.5 if row % 2 else r.uniform(0, bw * 0.3))
        while x < w:
            bwi = bw * r.uniform(0.75, 1.25)
            col = shade(base, r.uniform(-0.16, 0.14))
            rr = rrect(x + 4, y + 4, bwi - 8, bh - 8, 10)
            cv.drawPath(rr, fill(col))
            cv.drawPath(rrect(x + 8, y + 7, bwi - 16, (bh - 14) * 0.35, 8), fill(shade(col, 0.18), 0.6))
            cv.drawPath(rrect(x + 8, y + bh * 0.62, bwi - 16, bh * 0.28, 8), fill(shade(col, -0.22), 0.5))
            for _ in range(r.randint(0, 2)):
                cx, cy = x + r.uniform(20, bwi - 20), y + r.uniform(15, bh - 15)
                cv.drawLine(cx, cy, cx + r.uniform(-18, 18), cy + r.uniform(-12, 12), stroke(shade(col, -0.45), 2, 0.7))
            cv.drawPath(rr, ink(2.4, 0.75))
            x += bwi
        y += bh
        row += 1
    return _img(s)


def carpet(w, h, base='#8a2a33', border='#d9a648', inner='#2d3a78', seed=11):
    s = surface(w, h, base)
    cv = s.getCanvas()
    m = min(w, h) * 0.08
    cv.drawRect(skia.Rect.MakeXYWH(m * 0.4, m * 0.4, w - m * 0.8, h - m * 0.8), stroke(border, m * 0.25))
    cv.drawRect(skia.Rect.MakeXYWH(m * 1.2, m * 1.2, w - m * 2.4, h - m * 2.4), fill(inner))
    step = m * 1.4
    j = 0
    y = m * 1.2 + step / 2
    while y < h - m * 1.2:
        x = m * 1.2 + (step / 2 if j % 2 else step)
        while x < w - m * 1.2:
            d = step * 0.32
            cv.drawPath(path_poly([(x, y - d), (x + d, y), (x, y + d), (x - d, y)]), fill(border, 0.9))
            cv.drawCircle(x, y, d * 0.3, fill(base))
            x += step
        y += step
        j += 1
    for k in range(int(w / 18)):
        cv.drawLine(k * 18, 0, k * 18 + 6, m * 0.4, stroke(border, 2, 0.8))
    return _img(s)


def ceiling_tiles(w, h, size=150, base='#e6e2da', seed=12):
    s = surface(w, h, base)
    cv = s.getCanvas()
    r = rng(seed)
    for j in range(int(h // size) + 1):
        for i in range(int(w // size) + 1):
            for _ in range(10):
                cv.drawCircle(i * size + r.uniform(10, size - 10), j * size + r.uniform(10, size - 10), 1.5,
                              fill(shade(base, -0.25), 0.6))
    for k in range(int(w // size) + 2):
        cv.drawRect(skia.Rect.MakeXYWH(k * size - 3, 0, 6, h), fill(shade(base, -0.18)))
    for k in range(int(h // size) + 2):
        cv.drawRect(skia.Rect.MakeXYWH(0, k * size - 3, w, 6), fill(shade(base, -0.18)))
    return _img(s)
