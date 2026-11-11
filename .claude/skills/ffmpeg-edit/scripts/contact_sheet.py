#!/usr/bin/env python3
"""영상을 n등분한 지점의 프레임을 한 장(PNG)으로 모은다.  contact_sheet.py in.mp4 out.png [--n 12] [--cols 4] [--width 480]"""
import argparse, subprocess

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("out")
ap.add_argument("--n", type=int, default=12); ap.add_argument("--cols", type=int, default=4); ap.add_argument("--width", type=int, default=480)
a = ap.parse_args()
D = dur(a.video)
ts = [D * (i + 0.5) / a.n for i in range(a.n)]
rows = (a.n + a.cols - 1) // a.cols
args, fl = [], []
for i, t in enumerate(ts):
    args += ["-ss", "%.3f" % t, "-i", a.video]
    fl.append("[%d:v]scale=%d:-2,drawtext=text='%d\\:%02d':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6[v%d]"
              % (i, a.width, int(t) // 60, int(t) % 60, i))
lay = "|".join("%s_%s" % ("+".join(["w0"] * (i % a.cols)) or "0", "+".join(["h0"] * (i // a.cols)) or "0") for i in range(a.n))
fl.append("".join("[v%d]" % i for i in range(a.n)) + "xstack=inputs=%d:layout=%s:fill=black" % (a.n, lay))
subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", ";".join(fl), "-frames:v", "1", a.out], check=True)
print("[sheet] %s (%d컷, %.1f초 영상)" % (a.out, a.n, D))
