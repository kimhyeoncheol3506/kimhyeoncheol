#!/usr/bin/env python3
"""Contact sheet of stills:  python3 sheet.py stills/x sheet.jpg [cols]"""
import sys, glob
from PIL import Image
d, out = sys.argv[1], sys.argv[2]; W = int(sys.argv[3]) if len(sys.argv) > 3 else 7
fs = sorted(glob.glob(d + "/f*.jpg")); im0 = Image.open(fs[0]); TW = 270 if im0.height > im0.width else 480; TH = round(TW * im0.height / im0.width)
ims = [Image.open(f).resize((TW, TH)) for f in fs]
sh = Image.new("RGB", (TW * min(W, len(ims)), TH * ((len(ims) + W - 1) // W)))
for i, im in enumerate(ims): sh.paste(im, ((i % W) * TW, (i // W) * TH))
sh.save(out, quality=88); print(out, len(ims))
