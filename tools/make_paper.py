#!/usr/bin/env python3
"""구겨진 종이 질감을 코드로 만든다(저작권 걱정 없는 자체 생성). 미주일기형 '종이 인포그래픽' 배경.

  python tools/make_paper.py            # → assets/textures/paper.jpg (1920x1080), paper_dark.jpg

원리: 구겨진 종이는 기울기가 제각각인 작은 면들의 모자이크다. 무작위 점으로 면(보로노이)을 나누고
면마다 기울기를 줘서 왼쪽 위 조명으로 음영을 매긴 뒤, 흐려서 면 경계를 부드러운 주름으로 만든다.
여기에 굵은 굴곡과 종이 섬유 노이즈를 얹는다. 같은 seed 면 항상 같은 그림.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent


def _smooth_noise(h, w, cell, rng):
    g = rng.standard_normal((h // cell + 2, w // cell + 2))
    im = Image.fromarray(((g - g.min()) / (np.ptp(g) + 1e-9) * 255).astype(np.uint8)).resize((w + 2 * cell, h + 2 * cell), Image.BICUBIC)
    a = np.asarray(im, dtype=np.float32)[cell:cell + h, cell:cell + w] / 255.0
    return a - a.mean()


def _facets(h, w, n, rng, scale=2, blur=2.2):
    """보로노이 면마다 무작위 기울기 → 조명 음영(작은 격자에서 계산 후 키움)."""
    sh, sw = h // scale, w // scale
    pts = np.stack([rng.uniform(0, sw, n), rng.uniform(0, sh, n)], 1).astype(np.float32)
    y, x = np.mgrid[0:sh, 0:sw].astype(np.float32)
    best = np.full((sh, sw), np.inf, np.float32)
    idx = np.zeros((sh, sw), np.int32)
    for i, (px, py) in enumerate(pts):
        d = (x - px) ** 2 + (y - py) ** 2
        m = d < best
        best[m], idx[m] = d[m], i
    tilt = rng.normal(0, 0.22, (n, 2)).astype(np.float32)
    nx, ny = tilt[idx, 0], tilt[idx, 1]
    nz = np.ones_like(nx)
    lx, ly, lz = -0.55, -0.62, 0.56                           # 왼쪽 위에서 비스듬히 비춘다
    s = (nx * lx + ny * ly + nz * lz) / np.sqrt(nx * nx + ny * ny + 1)
    im = Image.fromarray(((s - s.min()) / (np.ptp(s) + 1e-9) * 255).astype(np.uint8))
    im = im.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32) / 255.0
    return a - np.median(a)


def paper(w=1920, h=1080, seed=11, base=(227, 221, 211), strength=1.0):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    shade = 0.075 * _facets(h, w, 900, rng) + 0.06 * _facets(h, w, 120, rng, blur=4)   # 잔 주름 + 큰 면
    shade += 0.12 * _smooth_noise(h, w, 300, rng)                            # 종이 전체의 굵은 굴곡
    shade *= strength
    vign = 1 - 0.06 * (((x / w - 0.5) ** 2 + (y / h - 0.5) ** 2) * 2.2)   # 아주 약한 비네팅
    grain = rng.standard_normal((h, w)).astype(np.float32) * 0.010       # 필름 그레인 대신 종이 섬유
    b = np.array(base, np.float32)[None, None, :] / 255.0
    out = b * (1 + shade[..., None] + grain[..., None]) * vign[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "assets" / "textures"))
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    paper(seed=a.seed).save(out / "paper.jpg", quality=88)
    paper(seed=a.seed + 1, base=(30, 26, 22), strength=0.5).save(out / "paper_dark.jpg", quality=88)   # 검정 장면용(거의 안 보이는 결)
    print("저장:", out / "paper.jpg", out / "paper_dark.jpg")


if __name__ == "__main__":
    main()
