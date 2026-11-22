# -*- coding: utf-8 -*-
"""인물 이름만 크게: 위쪽 흰 띠 + 검은 굵은 글씨, 아래 흑백(살짝 따뜻한) 장면, 둥근 테두리."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
FD = r"C:\Users\Admin\.aside\u\0\sessions\2026-11-20_KXdg20OLpJNMO68G\tmp\toon2d\toon2d\fonts"
FP = os.path.join(FD, next(f for f in os.listdir(FD) if "Pretendard" in f))
W, H = 1080, 1920
M, R, BAR = 34, 46, 380


def make(src, name, out):
    base = Image.new("RGB", (W, H), (232, 228, 220))
    card = Image.new("RGB", (W - 2 * M, H - 2 * M), (255, 255, 255))
    cw, ch = card.size
    im = Image.open(src).convert("RGB")
    Z = float(os.environ.get("THUMB_ZOOM", "1.35")); w0, h0 = im.size; cw2, ch2 = int(w0 / Z), int(h0 / Z); cx, cy = w0 // 2, int(h0 * 0.56)
    im = im.crop((max(0, cx - cw2 // 2), max(0, min(h0 - ch2, cy - ch2 // 2)), max(0, cx - cw2 // 2) + cw2, max(0, min(h0 - ch2, cy - ch2 // 2)) + ch2))
    ih = ch - BAR
    im = ImageOps.fit(im, (cw, ih), Image.LANCZOS, centering=(0.5, 0.42))
    g = ImageOps.grayscale(im)
    g = ImageEnhance.Contrast(g).enhance(1.25)
    tone = ImageOps.colorize(g, black=(18, 14, 12), white=(246, 238, 222), mid=(132, 120, 104))
    # vignette
    vg = Image.new("L", (cw, ih), 0)
    d = ImageDraw.Draw(vg)
    d.ellipse([-cw * 0.25, -ih * 0.15, cw * 1.25, ih * 1.15], fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(120))
    tone = Image.composite(tone, Image.new("RGB", tone.size, (12, 10, 9)), vg)
    card.paste(tone, (0, BAR))
    d = ImageDraw.Draw(card)
    d.line([(0, BAR), (cw, BAR)], fill=(20, 20, 20), width=6)
    size = 300
    while size > 120:
        f = ImageFont.truetype(FP, size)
        bb = d.textbbox((0, 0), name, font=f)
        if bb[2] - bb[0] <= cw - 70 and bb[3] - bb[1] <= BAR - 70:
            break
        size -= 10
    bb = d.textbbox((0, 0), name, font=f)
    d.text(((cw - (bb[2] - bb[0])) / 2 - bb[0], (BAR - (bb[3] - bb[1])) / 2 - bb[1]), name, font=f, fill=(12, 12, 12))
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], R, fill=255)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([M + 8, M + 12, W - M + 8, H - M + 12], R, fill=110)
    base = Image.composite(Image.new("RGB", (W, H), (150, 144, 136)), base, sh.filter(ImageFilter.GaussianBlur(14)))
    base.paste(card, (M, M), mask)
    ImageDraw.Draw(base).rounded_rectangle([M, M, W - M - 1, H - M - 1], R, outline=(25, 25, 25), width=7)
    base.save(out, quality=93)


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3])
    print("ok", sys.argv[3])
