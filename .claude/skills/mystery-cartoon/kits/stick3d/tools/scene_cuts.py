#!/usr/bin/env python3
"""scene_cuts.py <video> <out.json> [threshold=0.18]  -> hard-cut times, shot lengths and stats (low cut count + high motion = continuous-camera style)."""
import subprocess, re, json, sys, statistics
v, out = sys.argv[1], sys.argv[2]; thr = float(sys.argv[3]) if len(sys.argv) > 3 else 0.18
log = subprocess.run(['ffmpeg', '-hide_banner', '-i', v, '-vf', f"select='gt(scene,{thr})',showinfo", '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
cuts = sorted(set(round(float(x), 3) for x in re.findall(r'pts_time:([\d.]+)', log)))
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v]))
b = [0.0] + cuts + [dur]; lens = [round(b[i+1]-b[i], 2) for i in range(len(b)-1)]
res = {'threshold': thr, 'duration': round(dur, 2), 'cuts': cuts, 'shot_lengths': lens, 'n_shots': len(lens), 'avg': round(statistics.mean(lens), 2), 'min': min(lens), 'max': max(lens), 'median': round(statistics.median(lens), 2)}
json.dump(res, open(out, 'w'), indent=1); print({k: v for k, v in res.items() if k not in ('cuts', 'shot_lengths')})
