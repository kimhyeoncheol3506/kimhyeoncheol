# -*- coding: utf-8 -*-
"""롱폼(16:9)용 이름 썸네일 1280x720: thumb_name.py 와 같은 규칙(이름만, 위 흰 띠 + 검은 굵은 글씨, 아래 세피아 장면, 둥근 테두리).
사용: python thumb_name_wide.py <원본 이미지> "이름" <출력.jpg>   (원본은 자막 없는 프레임: nocap.py)
환경변수 THUMB_CY(0~1, 장면 세로 중심, 기본 0.45), THUMB_ZOOM(기본 1.0)
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.environ.get("TOON2D_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "mystery-cartoon", "kits", "toon2d"))
FD = os.path.join(ENG, "toon2d", "fonts")
FP = os.path.join(FD, next(f for f in os.listdir(FD) if "Pretendard" in f))
W, H = 1280, 720
M, R, BAR = 18, 26, 190


def make(src, name, out):
    base = Image.new("RGB", (W, H), (232, 228, 220))
    card = Image.new("RGB", (W - 2 * M, H - 2 * M), (255, 255, 255))
    cw, ch = card.size
    ih = ch - BAR
    im = Image.open(src).convert("RGB")
    w0, h0 = im.size
    Z = float(os.environ.get("THUMB_ZOOM", "1.0")); cy = float(os.environ.get("THUMB_CY", "0.45"))
    tw = w0 / Z; th = tw * ih / cw
    if th > h0:
        th = h0 / Z; tw = th * cw / ih
    top = max(0, min(h0 - th, cy * h0 - th / 2)); left = (w0 - tw) / 2
    im = im.crop((int(left), int(top), int(left + tw), int(top + th))).resize((cw, ih), Image.LANCZOS)
    g = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.25)
    tone = ImageOps.colorize(g, black=(18, 14, 12), white=(246, 238, 222), mid=(132, 120, 104))
    vg = Image.new("L", (cw, ih), 0)
    ImageDraw.Draw(vg).ellipse([-cw * 0.2, -ih * 0.3, cw * 1.2, ih * 1.3], fill=255)
    tone = Image.composite(tone, Image.new("RGB", tone.size, (12, 10, 9)), vg.filter(ImageFilter.GaussianBlur(90)))
    card.paste(tone, (0, BAR))
    d = ImageDraw.Draw(card)
    d.line([(0, BAR), (cw, BAR)], fill=(20, 20, 20), width=5)
    size = 170
    while size > 70:
        f = ImageFont.truetype(FP, size)
        bb = d.textbbox((0, 0), name, font=f)
        if bb[2] - bb[0] <= cw - 80 and bb[3] - bb[1] <= BAR - 44:
            break
        size -= 6
    bb = d.textbbox((0, 0), name, font=f)
    d.text(((cw - (bb[2] - bb[0])) / 2 - bb[0], (BAR - (bb[3] - bb[1])) / 2 - bb[1]), name, font=f, fill=(12, 12, 12))
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], R, fill=255)
    base.paste(card, (M, M), mask)
    ImageDraw.Draw(base).rounded_rectangle([M, M, W - M - 1, H - M - 1], R, outline=(25, 25, 25), width=5)
    base.save(out, quality=92)


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3])
    print("ok", sys.argv[3])
