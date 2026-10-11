"""휴대폰 스샷 → 쇼츠용 사연 카드 + 줄 좌표 자동 추출.

  python tools/card_from_screenshot.py <스샷.jpg> projects/<새 프로젝트> [--mask x0,y0,x1,y1 ...]

- 다크모드 X 화면(검은 배경 + 흰 카드)이면 흰 카드만 잘라내고, 블라인드 앱 원본(전체 흰 화면)이면 상단 상태바만 잘라낸다.
- 카드 안의 글자 줄을 찾아 card_regions(line1, line2 …)로 저장 → script.json의 focus 로 바로 사용.
- --mask: 회사 배지·실명 등 가릴 영역(카드 좌표). 흰색으로 덮고 회색 '?' 아바타를 그린다.
- 확인용 debug.png(줄 번호 표시)를 같이 만든다.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent


def runs(mask_1d, min_len=1, max_gap=0):
    out, start, gap = [], None, 0
    for i, v in enumerate(list(mask_1d) + [False]):
        if v:
            if start is None:
                start = i
            gap = 0
        elif start is not None:
            gap += 1
            if gap > max_gap or i == len(mask_1d):
                end = i - gap + 1
                if end - start >= min_len:
                    out.append((start, end))
                start, gap = None, 0
    return out


def find_card(g):
    h, w = g.shape
    bright = g > 225
    rows = bright[:, w // 8: w * 7 // 8].mean(axis=1) > 0.3
    cand = runs(rows, min_len=h // 6, max_gap=40)
    if not cand:
        return 0, int(h * 0.06), w, h  # 전체 흰 화면: 상태바만 제외
    y0, y1 = max(cand, key=lambda r: r[1] - r[0])
    cols = bright[y0:y1].mean(axis=0) > 0.55
    cx = runs(cols, min_len=w // 3, max_gap=6)
    x0, x1 = max(cx, key=lambda r: r[1] - r[0]) if cx else (0, w)
    return x0, y0, x1, y1


def find_lines(card_g):
    h, w = card_g.shape
    dark = card_g < 140
    rows = dark[:, int(w * 0.03): int(w * 0.97)].sum(axis=1) > 2
    lines = []
    for y0, y1 in runs(rows, min_len=12, max_gap=4):
        cols = np.where(dark[y0:y1].any(axis=0))[0]
        if len(cols) == 0:
            continue
        lines.append([int(cols.min()), max(0, y0 - 6), int(cols.max()), min(h, y1 + 6)])
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("project")
    ap.add_argument("--mask", nargs="*", default=[])
    ap.add_argument("--relabel", nargs="*", default=[],
                    help="x0,y0,x1,y1,아이디 — 그 영역을 지우고 아이디를 첫 글자+별표(S*****)로 다시 씀")
    a = ap.parse_args()
    proj = Path(a.project)
    proj.mkdir(parents=True, exist_ok=True)
    im = Image.open(a.shot).convert("RGB")
    g = np.asarray(im.convert("L"))
    x0, y0, x1, y1 = find_card(g)
    card = im.crop((x0, y0, x1, y1))
    d = ImageDraw.Draw(card)
    for m in a.mask:
        mx0, my0, mx1, my1 = map(int, m.split(","))
        d.rectangle((mx0, my0, mx1, my1), fill=(255, 255, 255))
        r = min(mx1 - mx0, my1 - my0) / 2 - 4
        cx, cy = (mx0 + mx1) / 2, (my0 + my1) / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(214, 214, 220))
        f = ImageFont.truetype(str(ROOT / "assets/fonts/Pretendard-Bold.otf"), int(r))
        d.text((cx, cy), "?", fill=(150, 150, 158), anchor="mm", font=f)
    for r in a.relabel:
        x0r, y0r, x1r, y1r, ident = r.split(",", 4)
        x0r, y0r, x1r, y1r = map(int, (x0r, y0r, x1r, y1r))
        bgc = card.getpixel((max(0, x0r - 4), y0r))
        d.rectangle((x0r, y0r, x1r, y1r), fill=bgc)
        fr = ImageFont.truetype(str(ROOT / "assets/fonts/Pretendard-Medium.otf"), int((y1r - y0r) * 0.8))
        d.text((x0r, (y0r + y1r) / 2), ident[:1] + "*" * max(2, len(ident) - 1), font=fr, fill=(150, 150, 158), anchor="lm")
    card.save(proj / "source_card.png")
    lines = find_lines(np.asarray(card.convert("L")))
    regions = {f"line{i + 1}": r for i, r in enumerate(lines)}
    (proj / "card_regions.json").write_text(json.dumps(regions, indent=1), encoding="utf-8")
    dbg = card.copy()
    dd = ImageDraw.Draw(dbg)
    f = ImageFont.truetype(str(ROOT / "assets/fonts/Pretendard-Bold.otf"), 22)
    for k, (lx0, ly0, lx1, ly1) in regions.items():
        dd.rectangle((lx0, ly0, lx1, ly1), outline=(255, 0, 0), width=2)
        dd.text((lx1 + 4, ly0), k, fill=(255, 0, 0), font=f)
    dbg.save(proj / "debug.png")
    print(f"카드 {card.size} @({x0},{y0}) · 줄 {len(regions)}개 → {proj}")


if __name__ == "__main__":
    main()
