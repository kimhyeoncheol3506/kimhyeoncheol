"""AI 배경 + 코드 레이어(캐릭터·헤드라인·차트·자막) 합성 시험. Before/After 비교 이미지 생성.

사용: python tools/before_after.py <작업폴더>  (폴더에 before_sN.png, bg_sN.jpg 필요)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from studio import render as R
from studio.draw import draw_text, font, mascot
from studio.scenes import render_visual

W, H = 1920, 1080
HB = R.HEADLINE_H


def char_layer(emotion, pose, cx, cy, s, flip=False):
    key = Image.new("RGB", (W, H), (255, 0, 255))
    mascot(key, cx if not flip else W - cx, cy, s, emotion, "m", pose)
    if flip:
        key = key.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.array(key)
    m = ~((a[:, :, 0] == 255) & (a[:, :, 1] == 0) & (a[:, :, 2] == 255))
    lay = key.convert("RGBA")
    lay.putalpha(Image.fromarray((m * 255).astype("uint8")))
    # 그림자로 배경에 붙이기
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(Image.fromarray((m * 110).astype("uint8")))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(sh, (12, 14))
    out.alpha_composite(lay)
    return out


def compose(bg_path, spec, project, out):
    bg = Image.open(bg_path).convert("RGB").resize((W, H - HB), Image.LANCZOS)
    if spec.get("dim"):
        bg = ImageEnhance.Brightness(bg).enhance(spec["dim"])
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    img.paste(bg, (0, HB))
    if spec.get("panel"):  # 그래프는 반투명 카드로 배경 위에
        v = spec["panel"]
        pan = render_visual(v, W, H - HB, None, 0).convert("RGBA")
        a = np.array(pan)
        bgcol = a[5, 5, :3]
        mask = (np.abs(a[:, :, :3].astype(int) - bgcol).sum(axis=2) > 18)
        a[:, :, 3] = np.where(mask, 255, 0).astype("uint8")
        img.alpha_composite(Image.fromarray(a), (0, HB))
    for c in spec.get("chars", []):
        img.alpha_composite(char_layer(**c))
    if spec.get("big"):  # 큰 숫자 (그림 위)
        d = ImageDraw.Draw(img)
        x, y, txt, col = spec["big"]
        draw_text(d, (x, y), txt, font("black", 200), fill=tuple(col), stroke=14, stroke_fill=(15, 15, 18))
    sub = os.path.join(os.path.dirname(out), "_sub.png")
    R.subtitle_png("long", spec["sub"], sub, 1460)
    img.alpha_composite(Image.open(sub))
    hp = os.path.join(os.path.dirname(out), "_hl.png")
    R.headline_png(spec["headline"], hp, project)
    img.alpha_composite(Image.open(hp))
    tmp = os.path.join(os.path.dirname(out), "_chrome")
    os.makedirs(tmp, exist_ok=True)
    _, top = R.chrome_pngs(project, "long", tmp)
    img.alpha_composite(Image.open(top))
    img.convert("RGB").save(out)


def pair(before, after, out, label):
    b = Image.open(before).convert("RGB").resize((960, 540))
    a = Image.open(after).convert("RGB").resize((960, 540))
    g = Image.new("RGB", (1940, 620), (24, 24, 28))
    g.paste(b, (0, 70))
    g.paste(a, (980, 70))
    d = ImageDraw.Draw(g)
    draw_text(d, (480, 36), "BEFORE (지금)", font("black", 40), fill=(200, 200, 200))
    draw_text(d, (1460, 36), "AFTER (AI 배경 + 우리 캐릭터)", font("black", 40), fill=(255, 214, 10))
    draw_text(d, (970, 36), label, font("bold", 26), fill=(150, 150, 150))
    g.save(out)


if __name__ == "__main__":
    D = sys.argv[1]
    project = {"channel": {"name": "월급쟁이 재테크 스킬"}, "corner_mascot": True}
    specs = json.load(open(os.path.join(D, "specs.json"), encoding="utf-8"))
    for sid, spec in specs.items():
        after = os.path.join(D, f"after_{sid}.png")
        compose(os.path.join(D, f"bg_{sid}.jpg"), spec, project, after)
        pair(os.path.join(D, f"before_{sid}.png"), after, os.path.join(D, f"ba_{sid}.png"), spec.get("label", ""))
        print(sid)
