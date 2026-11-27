"""output/<프로젝트>/frame_*.png 를 한 장으로 (검수용).  python tools/contact.py out.png proj1 proj2 ..."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
out, projs = sys.argv[1], sys.argv[2:]
tw, th = 240, 427
rows = []
for p in projs:
    fs = sorted((ROOT / "output" / p).glob("frame_*.png"))
    rows.append((p, fs))
n = max(len(f) for _, f in rows)
im = Image.new("RGB", (tw * n, (th + 30) * len(rows)), (40, 40, 40))
d = ImageDraw.Draw(im)
for r, (p, fs) in enumerate(rows):
    d.text((6, r * (th + 30) + 6), p, fill=(255, 255, 0))
    for c, f in enumerate(fs):
        im.paste(Image.open(f).convert("RGB").resize((tw, th)), (c * tw, r * (th + 30) + 30))
im.save(out)
print(out)
