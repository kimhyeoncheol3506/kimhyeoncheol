"""여러 이미지를 격자 한 장으로.  python tools/grid.py out.png cols img1 img2 ..."""
import sys

from PIL import Image

out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
tw, th = 324, 576
rows = (len(files) + cols - 1) // cols
im = Image.new("RGB", (tw * cols + 8 * (cols + 1), th * rows + 8 * (rows + 1)), (30, 30, 30))
for i, f in enumerate(files):
    r, c = divmod(i, cols)
    im.paste(Image.open(f).convert("RGB").resize((tw, th)), (8 + c * (tw + 8), 8 + r * (th + 8)))
im.save(out, quality=88)
print(out)
