"""쇼츠 테마: 주제에 맞춰 배경·폰트·강조색을 통째로 바꾼다. script.json 의 "theme" 으로 선택.

시인성 원칙
  - 후크/자막은 흰 글씨 + 두꺼운 검정 외곽 (밝은 테마는 진한 글씨 + 흰 외곽) → 어떤 배경에서도 읽힘
  - 강조색은 배경과 보색 계열로 1개만 (키워드에만)
  - 배경은 2색 그라데이션 + 옅은 패턴 → 단색보다 고급스럽고, 주인공(카드/카톡)을 가리지 않음
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

THEMES = {
    # 직장·블라인드 사연 기본
    "office": dict(top=(13, 24, 46), bottom=(30, 58, 95), pattern="grid", accent=(255, 214, 10),
                   hook_font="impact", text=(255, 255, 255), stroke=(10, 10, 14), stamp=(229, 57, 53),
                   badge=(229, 57, 53), bar=(255, 214, 10)),
    # 돈·연봉·데이트 비용
    "money": dict(top=(8, 8, 8), bottom=(48, 38, 12), pattern="stripes", accent=(255, 200, 60),
                  hook_font="gasoek", text=(255, 255, 255), stroke=(0, 0, 0), stamp=(255, 190, 40),
                  badge=(196, 140, 20), bar=(255, 200, 60)),
    # 바람·환승·배신
    "cheat": dict(top=(20, 4, 6), bottom=(84, 12, 22), pattern="vignette", accent=(255, 72, 96),
                  hook_font="impact", text=(255, 255, 255), stroke=(0, 0, 0), stamp=(255, 50, 70),
                  badge=(200, 20, 40), bar=(255, 72, 96)),
    # 설렘·호감 신호·그린라이트
    "sweet": dict(top=(255, 222, 232), bottom=(255, 176, 200), pattern="hearts", accent=(232, 30, 110),
                  hook_font="jua", text=(40, 20, 30), stroke=(255, 255, 255), stamp=(30, 170, 90),
                  badge=(232, 30, 110), bar=(232, 30, 110)),
    # 읽씹·식은 마음·이별
    "cold": dict(top=(10, 18, 28), bottom=(36, 58, 80), pattern="dots", accent=(96, 205, 255),
                 hook_font="dohyeon", text=(255, 255, 255), stroke=(4, 8, 14), stamp=(229, 57, 53),
                 badge=(40, 120, 200), bar=(96, 205, 255)),
    # 밤·썸·스킨십 직전(수위 주의 주제)
    "night": dict(top=(16, 0, 40), bottom=(62, 10, 94), pattern="dots", accent=(255, 96, 220),
                  hook_font="impact", text=(255, 255, 255), stroke=(0, 0, 0), stamp=(255, 70, 200),
                  badge=(170, 40, 200), bar=(255, 96, 220)),
}

FONT_KEY = {"impact": "impact", "gasoek": "gasoek", "jua": "hand", "dohyeon": "dohyeon"}


def get(name: str) -> dict:
    t = dict(THEMES.get(name or "office", THEMES["office"]))
    t["name"] = name or "office"
    t["font"] = FONT_KEY[t["hook_font"]]
    return t


def background(theme: dict, size) -> Image.Image:
    W, H = size
    top, bot = theme["top"], theme["bottom"]
    grad = Image.new("RGB", (1, H))
    for y in range(H):
        k = y / (H - 1)
        grad.putpixel((0, y), tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    im = grad.resize((W, H)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    p = theme["pattern"]
    a = theme["accent"]
    light = sum(top) > 450
    ink = (0, 0, 0, 22) if light else (255, 255, 255, 16)
    if p == "grid":
        for x in range(0, W, 72):
            d.line((x, 0, x, H), fill=ink, width=2)
        for y in range(0, H, 72):
            d.line((0, y, W, y), fill=ink, width=2)
    elif p == "dots":
        for y in range(30, H, 60):
            for x in range(30 + (y // 60 % 2) * 30, W, 60):
                d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=ink)
    elif p == "stripes":
        for x in range(-H, W, 90):
            d.line((x, H, x + H, 0), fill=a + (18,), width=18)
    elif p == "hearts":
        for i, y in enumerate(range(80, H, 170)):
            for x in range(80 + (i % 2) * 85, W, 170):
                r = 16
                pts = [(x + 16 * math.sin(t) ** 3 * r / 16,
                        y - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * r / 16)
                       for t in [k / 30 * 2 * math.pi for k in range(30)]]
                d.polygon(pts, fill=(255, 255, 255, 70))
    if p == "vignette" or not light:
        v = Image.new("L", (W, H), 0)
        ImageDraw.Draw(v).ellipse((-W * 0.3, -H * 0.15, W * 1.3, H * 1.15), fill=255)
        v = v.filter(ImageFilter.GaussianBlur(160))
        dark = Image.new("RGBA", (W, H), (0, 0, 0, 150))
        dark.putalpha(v.point(lambda x: int((255 - x) * 0.6)))
        lay = Image.alpha_composite(lay, dark)
    return Image.alpha_composite(im, lay)
