#!/usr/bin/env python3
"""장면 1개 렌더/미리보기 CLI.
  python shorts/render_card.py shorts/scene.html out.mp4 --dur 4 --data '{"kind":"hook",...}'
  python shorts/render_card.py shorts/scene.html outdir --dur 4 --frames 0.5,3.9 --data '{...}'   # PNG 만
렌더할 때마다 아래 18% 가 비었는지 검사해 결과를 출력한다."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_lib import render_scene

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("out")
ap.add_argument("--dur", type=float, default=4.0); ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--data", default="{}"); ap.add_argument("--frames", default="")
a = ap.parse_args()
data = json.loads(a.data)
if a.frames:
    v = render_scene(a.html, data, a.dur, None, a.fps, frames_dir=a.out, frames_at=[float(x) for x in a.frames.split(",")])
else:
    v = render_scene(a.html, data, a.dur, a.out, a.fps)
print("아래 18% 검사:", "✅ 비어 있음" if not v else f"⚠ 침범 {len(v)}곳 {v[:5]}")
