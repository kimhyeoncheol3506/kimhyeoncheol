# -*- coding: utf-8 -*-
"""사용자 제작 썸네일 형식 '시장 사진 + 금색 큰 제목 + 흰색 큰 부제 + 빨간 붓터치' (ranking-video v2.11.0)

참고 원본: references/썸네일_참고/시세변화형_20261029.png (사용자가 직접 만든 '노량진수산시장 / 10월 주간 시세변화')
구성(1920×1080):
  - 배경: 시장 사진 전체(가운데 크롭) + 아주 살짝 어둡게
  - 윗줄(line1): 금색 그라데이션 아주 큰 글자 + 검정 굵은 외곽선 + 그림자, 오른쪽으로 약 2.5° 올라가게 기울임
  - 아랫줄(line2): 흰색 아주 큰 글자 + 검정 굵은 외곽선 + 그림자, 같은 기울기, 윗줄보다 약간 넓게
  - 붉은 붓터치: 아랫줄 왼쪽 아래에 가늘고 긴 빨간 붓 자국
  - 로고(선택): 오른쪽 위(--logo 투명 PNG, 가로 360px 안쪽)
사용:
  python3 -I make_thumbnail_title.py --photo 사진.jpg --line1 "노량진수산시장" --line2 "10월 주간 시세변화" --out 썸네일.png [--logo 로고.png]
규칙: 윗줄 첫 단어는 '노량진수산시장'(내_규칙). 글자는 화면 가로 75~95%를 채운다.
"""
import argparse, math, os, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
FONT = os.path.expanduser("~/.cache/ranking-video/fonts/BlackHanSans-Regular.ttf")


def font(size):
    if not os.path.exists(FONT):
        os.makedirs(os.path.dirname(FONT), exist_ok=True)
        subprocess.run(["curl", "-sL", "-m", "120", "-o", FONT, "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/blackhansans/BlackHanSans-Regular.ttf"], check=True)
    return ImageFont.truetype(FONT, size)


def fit(text, width, max_size):
    lo, hi = 40, max_size
    while lo < hi:
        mid = (lo + hi + 1) // 2; b = font(mid).getbbox(text)
        if b[2] - b[0] <= width: lo = mid
        else: hi = mid - 1
    return font(lo)


def text_layer(text, f, gradient, stroke, shadow=14):
    pad = stroke + shadow + 30; b = f.getbbox(text); w, h = b[2] - b[0] + pad * 2, b[3] - b[1] + pad * 2 + 20
    pos = (pad - b[0], pad - b[1])
    mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).text(pos, text, font=f, fill=255)
    outline = Image.new("L", (w, h), 0); ImageDraw.Draw(outline).text(pos, text, font=f, fill=255, stroke_width=stroke)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sh.putalpha(outline.filter(ImageFilter.GaussianBlur(shadow)).point(lambda v: int(v * 0.85)))
    layer.alpha_composite(sh, (0, shadow // 2 + 6))
    ol = Image.new("RGBA", (w, h), (12, 8, 6, 255)); ol.putalpha(outline); layer.alpha_composite(ol)
    if gradient:
        g = Image.new("RGBA", (w, h)); gd = ImageDraw.Draw(g); top, bot = gradient
        y0, y1 = pos[1] + b[1], pos[1] + b[3]
        for y in range(h):
            t = min(1, max(0, (y - y0) / max(1, y1 - y0))); gd.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
        g.putalpha(mask); layer.alpha_composite(g)
    else:
        fl = Image.new("RGBA", (w, h), (255, 255, 255, 255)); fl.putalpha(mask); layer.alpha_composite(fl)
    return layer


def paste_rot(im, layer, cx, cy, angle):
    r = layer.rotate(angle, resample=Image.BICUBIC, expand=True); im.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2)))


def brush(w, h):
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    pts = [(0, h * .55), (w * .06, h * .25), (w * .5, h * .12), (w * .93, h * .3), (w, h * .52), (w * .9, h * .78), (w * .48, h * .9), (w * .05, h * .88)]
    d.polygon(pts, fill=(229, 35, 27, 255))
    for i in range(3):  # 붓 결
        y = h * (.3 + i * .18); d.line([(w * (.06 + i * .05), y), (w * (.9 - i * .06), y + 2)], fill=(185, 16, 12, 110), width=2)
    return L


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--photo", required=True); ap.add_argument("--line1", required=True); ap.add_argument("--line2", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--logo"); a = ap.parse_args()
    im = Image.open(a.photo).convert("RGB"); s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).convert("RGBA")
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dark)
    for y in range(H): dd.line([(0, y), (W, y)], fill=(0, 0, 0, int(30 + 70 * (y / H) ** 2)))
    im.alpha_composite(dark)
    f1 = fit(a.line1, int(W * .75), 330); f2 = fit(a.line2, int(W * .86), 330)
    l1 = text_layer(a.line1, f1, ((255, 226, 110), (236, 160, 0)), 18); l2 = text_layer(a.line2, f2, None, 18)
    paste_rot(im, l1, W * .52, H * .415, 2.5); paste_rot(im, l2, W * .50, H * .70, 2.5)
    b = brush(int(W * .46), 78); im.alpha_composite(b.rotate(1.2, expand=True, resample=Image.BICUBIC), (int(W * .12), int(H * .845)))
    if a.logo and os.path.exists(a.logo):
        lg = Image.open(a.logo).convert("RGBA"); k = min(1.0, 360 / lg.width); lg = lg.resize((int(lg.width * k), int(lg.height * k)), Image.LANCZOS); im.alpha_composite(lg, (W - lg.width - 40, 20))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); im.convert("RGB").save(a.out, quality=95); print("썸네일:", a.out)


if __name__ == "__main__":
    main()
