"""Numeric look checks for a frame (PNG/JPG) against the target style numbers.

python -m toon2d.checks frame1.png [frame2.png ...]
"""
import sys

import numpy as np

TARGETS = {
    'L_mean': (43, 58), 'L_p1': (7, 19), 'L_p5': (11, 26), 'L_p95': (74, 90), 'L_std': (17, 24),
    'chroma_mean': (24, 38), 'shadow_a': (4, 22), 'shadow_b': (-16, 2), 'hi_b': (2, 20),
    'vignette': (0.62, 0.9), 'near_black_pct': (0.2, 11),
}


def srgb_to_lab(rgb):
    c = rgb.astype(np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], np.float32)
    xyz = c @ M.T
    xyz /= np.array([0.95047, 1.0, 1.08883], np.float32)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return L, a, b


def measure(rgb, caption_mask=True):
    h, w = rgb.shape[:2]
    small = rgb[::4, ::4, :3]
    L, a, b = srgb_to_lab(small)
    if caption_mask:   # ignore the caption band (white text skews highlights)
        hh = L.shape[0]
        keep = np.ones_like(L, bool)
        keep[int(hh * 0.62):int(hh * 0.78), :] = False
    else:
        keep = np.ones_like(L, bool)
    Lk, ak, bk = L[keep], a[keep], b[keep]
    sh = Lk < 35
    hi = Lk > 70
    ch = np.hypot(ak, bk)
    hh, ww = L.shape
    cy0, cy1, cx0, cx1 = int(hh * 0.35), int(hh * 0.65), int(ww * 0.35), int(ww * 0.65)
    cs = int(min(hh, ww) * 0.12)
    corners = np.concatenate([L[:cs, :cs].ravel(), L[:cs, -cs:].ravel(), L[-cs:, :cs].ravel(), L[-cs:, -cs:].ravel()])
    return {
        'L_mean': float(Lk.mean()), 'L_p1': float(np.percentile(Lk, 1)), 'L_p5': float(np.percentile(Lk, 5)),
        'L_p95': float(np.percentile(Lk, 95)), 'L_std': float(Lk.std()), 'chroma_mean': float(ch.mean()),
        'shadow_a': float(ak[sh].mean()) if sh.any() else 0.0, 'shadow_b': float(bk[sh].mean()) if sh.any() else 0.0,
        'hi_b': float(bk[hi].mean()) if hi.any() else 0.0,
        'vignette': float(corners.mean() / max(1e-3, L[cy0:cy1, cx0:cx1].mean())),
        'near_black_pct': float((Lk < 10).mean() * 100),
    }


def report(m):
    out, bad = [], 0
    for k, v in m.items():
        lo, hi = TARGETS[k]
        ok = lo <= v <= hi
        bad += not ok
        out.append('%-15s %7.2f  [%g..%g] %s' % (k, v, lo, hi, 'ok' if ok else '<-- off'))
    return '\n'.join(out), bad


def main(paths):
    from PIL import Image
    tot = 0
    for p in paths:
        rgb = np.asarray(Image.open(p).convert('RGB'))
        txt, bad = report(measure(rgb))
        tot += bad
        print('==', p, '(%d off)' % bad)
        print(txt)
    return tot


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:]) else 0)
