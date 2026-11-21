"""심플형 썸네일 (2026-11-21 현철님 지시): 어둡고 채도 낮은 살짝 흐린 배경 + 오른쪽 걱정하는 인물 1명(가상 인물/채널 캐릭터)
+ 왼쪽 아래 아주 두꺼운 고딕 2줄(1줄 흰색, 2줄 주황·노랑), 검은 외곽선. 복잡한 그래픽·아이콘 없음. 1280×720.
  python3 tools/thumb_viral/simple.py 설정.json 출력.png
설정: {"bg": 배경그림, "flip": true, "person_x": [0.55, 1.0] (선명하게 둘 오른쪽 구간 비율), "mascot": 개미PNG(선택, 배경 대신 인물로),
       "line1": "코스피 4,900", "line2": "여기서 갈린다", "color2": "#FFB000"}"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
NS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT = os.path.join(NS, "assets", "fonts", "BlackHanSans.ttf")
W, H = 1280, 720
cfg = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
bg = Image.open(cfg["bg"]).convert("RGB")
if cfg.get("flip"): bg = ImageOps.mirror(bg)
z = cfg.get("zoom", 1.0); s = max(W / bg.width, H / bg.height) * z; bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
ax = cfg.get("anchor_x", 0.5); ay = cfg.get("anchor_y", 0.5)   # 확대 뒤 어느 쪽을 남길지(1.0 = 오른쪽/아래)
ox = round((bg.width - W) * ax); oy = round((bg.height - H) * ay); bg = bg.crop((ox, oy, ox + W, oy + H))
sharp = ImageEnhance.Color(bg).enhance(cfg.get("sat_person", 0.75)); sharp = ImageEnhance.Brightness(sharp).enhance(0.9)
soft = ImageEnhance.Color(bg.filter(ImageFilter.GaussianBlur(cfg.get("blur", 7)))).enhance(0.25); soft = ImageEnhance.Brightness(soft).enhance(0.45)
a, b = cfg.get("person_x", [0.52, 0.62])   # 이 구간에서 흐림 → 선명으로 넘어감
import numpy as np
t = np.tile(np.linspace(0, 1, W), (H, 1)); mv = np.clip((b - t) / max(b - a, 1e-3), 0, 1) * 255   # 왼쪽 = 흐림(255), 오른쪽 = 선명(0)
mask = Image.fromarray(mv.astype("uint8"), "L")
im = Image.composite(soft, sharp, mask)
if cfg.get("mascot"):
    m = Image.open(cfg["mascot"]).convert("RGBA"); mh = cfg.get("mascot_h", 640); m = m.resize((round(m.width * mh / m.height), mh), Image.LANCZOS)
    glow = Image.new("RGBA", m.size, (0, 0, 0, 0)); al = m.split()[3].filter(ImageFilter.MaxFilter(15))
    glow.paste((255, 255, 255, 255), mask=al); x = W - m.width - 40; y = H - m.height + 30
    im = im.convert("RGBA"); im.alpha_composite(glow, (x, y)); im.alpha_composite(m, (x, y)); im = im.convert("RGB")
vig = Image.new("L", (W, H), 0); ImageDraw.Draw(vig).ellipse([-W * 0.3, -H * 0.4, W * 1.3, H * 1.4], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(120)); im = Image.composite(im, Image.new("RGB", (W, H), (0, 0, 0)), vig)
# 왼쪽 아래 어둡게(글자 받침)
shade = Image.new("L", (W, H), 0); ImageDraw.Draw(shade).rectangle([0, int(H * 0.45), int(W * 0.75), H], fill=150)
im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, shade.filter(ImageFilter.GaussianBlur(90)))
d = ImageDraw.Draw(im)
def fit(t, size, maxw):
    while ImageFont.truetype(FONT, size).getlength(t) > maxw and size > 40: size -= 4
    return ImageFont.truetype(FONT, size)
mw = cfg.get("text_w", 760)
f1 = fit(cfg["line1"], cfg.get("size1", 130), mw); f2 = fit(cfg["line2"], cfg.get("size2", 150), mw)
x0 = 48; y2 = H - 48 - f2.size; y1 = y2 - f1.size - 18
for (t, f, y, c) in ((cfg["line1"], f1, y1, "#FFFFFF"), (cfg["line2"], f2, y2, cfg.get("color2", "#FFB000"))):
    d.text((x0 + 6, y + 8), t, font=f, fill=(0, 0, 0), stroke_width=14, stroke_fill=(0, 0, 0))   # 그림자
    d.text((x0, y), t, font=f, fill=c, stroke_width=12, stroke_fill=(0, 0, 0))
im.save(out, optimize=True); print("저장:", out)
