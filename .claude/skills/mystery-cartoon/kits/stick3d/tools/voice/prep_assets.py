#!/usr/bin/env python3
"""Asset prep used for video 02. usage (edit the dicts or import):
  photos -> 1280x720 jpg (public/<dir>/name.jpg)
  circle_logo(src, out): scales the logo so EVERY glyph pixel stays inside the circle (<=80% radius) => nothing cropped
  square_crop(src, out, color_test): crops a flat-colour logo square out of a wider canvas (e.g. red square on white), rounded corners
"""
from PIL import Image, ImageDraw
import numpy as np, sys
def photo(src, out): Image.open(src).convert('RGB').resize((1280,720), Image.LANCZOS).save(out, quality=88)
def circle_logo(src, out, margin=0.80, size=512):
    g = Image.open(src).convert('RGB'); a = np.array(g).astype(int); h, w = a.shape[:2]
    bg = np.median(np.concatenate([a[:10,:10].reshape(-1,3), a[:10,-10:].reshape(-1,3), a[-10:,:10].reshape(-1,3), a[-10:,-10:].reshape(-1,3)]), axis=0)
    ys, xs = np.nonzero(np.abs(a-bg).sum(axis=2) > 90); cx, cy = w/2, h/2
    rmax = float(np.max(np.hypot(xs-cx, ys-cy))); s = margin*(min(w,h)/2)/rmax
    S = 1024; circ = Image.new('L', (S,S), 0); ImageDraw.Draw(circ).ellipse((0,0,S-1,S-1), fill=255)
    can = Image.new('RGBA', (S,S), (0,0,0,0)); can.paste(Image.new('RGBA', (S,S), tuple(int(v) for v in bg)+(255,)), (0,0), circ)
    gs = g.resize((int(w*s*S/min(w,h)), int(h*s*S/min(w,h))), Image.LANCZOS).convert('RGBA'); tmp = Image.new('RGBA', (S,S), (0,0,0,0)); tmp.paste(gs, ((S-gs.size[0])//2, (S-gs.size[1])//2))
    can = Image.alpha_composite(can, Image.composite(tmp, Image.new('RGBA', (S,S), (0,0,0,0)), circ)); can.resize((size,size), Image.LANCZOS).save(out)
    print('glyph max radius', round(rmax,1), 'scale', round(s,3))
def square_crop(src, out, test, radius=72):
    im = Image.open(src).convert('RGB'); a = np.array(im).astype(int); ys, xs = np.nonzero(test(a))
    sq = im.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1)).resize((400,400), Image.LANCZOS).convert('RGBA'); mk = Image.new('L', (400,400), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0,0,399,399), radius=radius, fill=255); sq.putalpha(mk); sq.save(out)
if __name__ == '__main__': print(__doc__)
