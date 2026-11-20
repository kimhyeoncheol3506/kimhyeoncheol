#!/usr/bin/env python3
"""contact_sheets.py <video> <outdir> [--fps 1] [--cols 4] [--rows 3] [--start 0] [--end N] [--w 480]
Extracts frames and tiles them into labelled sheets (timestamp on every tile). Use dense fps (8-10) over short ranges for animations."""
import argparse, subprocess, os, glob, tempfile
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('out')
ap.add_argument('--fps', type=float, default=1); ap.add_argument('--cols', type=int, default=4); ap.add_argument('--rows', type=int, default=3)
ap.add_argument('--start', type=float, default=0); ap.add_argument('--end', type=float, default=0); ap.add_argument('--w', type=int, default=480); ap.add_argument('--prefix', default='sheet')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); tmp = tempfile.mkdtemp()
cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(a.start)] + (['-to', str(a.end)] if a.end else []) + ['-i', a.video, '-vf', f'fps={a.fps},scale={a.w}:-1', os.path.join(tmp, 'f%05d.png')]
subprocess.run(cmd, check=True); fr = sorted(glob.glob(os.path.join(tmp, 'f*.png'))); per = a.cols * a.rows; n = 0
for i in range(0, len(fr), per):
    ims = [Image.open(f) for f in fr[i:i+per]]; w, h = ims[0].size
    sheet = Image.new('RGB', (a.cols*w, a.rows*h), (0, 0, 0)); d = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x, y = (k % a.cols)*w, (k // a.cols)*h; sheet.paste(im, (x, y)); t = a.start + (i+k)/a.fps
        d.rectangle((x+4, y+4, x+86, y+22), fill=(0, 0, 0)); d.text((x+8, y+8), f'{t:07.2f}s', fill=(255, 235, 59))
    p = os.path.join(a.out, f'{a.prefix}_{n:02d}.jpg'); sheet.save(p, quality=82); n += 1
print(f'{len(fr)} frames -> {n} sheets in {a.out}')
