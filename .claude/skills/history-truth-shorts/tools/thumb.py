# -*- coding: utf-8 -*-
"""세로 썸네일(1080x1920): 자막 없는 원본 + 큰 제목 2~3줄 + 노란 배지.
사용: python thumb.py <원본.png> <출력.jpg> "줄1|*줄2|줄3" [배지글자] [아래로밀기px]
  - 줄 앞에 * 를 붙이면 노란색 강조
  - 배지 기본값: 그날의 진실
폰트: 엔진 fonts 폴더의 Pretendard (Poppins 는 한글 없음 - 'ExtraBold' 로 찾지 말 것)
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.environ.get("TOON2D_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "mystery-cartoon", "kits", "toon2d"))
FD = os.path.join(ENG, "toon2d", "fonts")
fp = next(os.path.join(FD, f) for f in os.listdir(FD) if "Pretendard" in f)
src, out, text = sys.argv[1], sys.argv[2], sys.argv[3]
badge = sys.argv[4] if len(sys.argv) > 4 else "그날의 진실"
SH = int(sys.argv[5]) if len(sys.argv) > 5 else 0
im = Image.open(src).convert("RGB").resize((1080, 1920))
if SH:
    base = im.crop((0, 0, 1080, 300)).resize((1080, SH + 300)).filter(ImageFilter.GaussianBlur(18))
    c = Image.new("RGB", (1080, 1920)); c.paste(base, (0, 0)); c.paste(im.crop((0, 0, 1080, 1920 - SH)), (0, SH)); im = c
ov = Image.new("L", (1080, 1920), 0); d = ImageDraw.Draw(ov)
for y in range(0, 900):
    d.line([(0, y), (1080, y)], fill=int(170 * (1 - y / 900)))
im = Image.composite(Image.new("RGB", im.size, (20, 12, 24)), im, ov)
dr = ImageDraw.Draw(im)
y = 260
for t in text.split("|"):
    col = (255, 214, 64) if t.startswith("*") else (255, 255, 255)
    t = t.lstrip("*")
    size = 150
    while size > 80:
        f = ImageFont.truetype(fp, size)
        if dr.textlength(t, font=f) <= 1000:
            break
        size -= 8
    w = dr.textlength(t, font=f)
    dr.text(((1080 - w) / 2, y), t, font=f, fill=col, stroke_width=14, stroke_fill=(25, 15, 25))
    y += int(size * 1.2)
bf = ImageFont.truetype(fp, 64)
bw = dr.textlength(badge, font=bf)
dr.rounded_rectangle([60, 110, 60 + bw + 60, 210], radius=24, fill=(255, 210, 0), outline=(25, 15, 25), width=6)
dr.text((90, 120), badge, font=bf, fill=(25, 15, 25))
im.save(out, quality=92)
print("ok", out)
