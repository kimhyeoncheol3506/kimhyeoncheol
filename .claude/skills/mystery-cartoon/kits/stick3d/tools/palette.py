#!/usr/bin/env python3
"""palette.py <video> <out.json> [k=8]  -> dominant colors (k-means), proportions, saturation/brightness stats, background guess, contrast."""
import subprocess, sys, json, numpy as np
v, out = sys.argv[1], sys.argv[2]; k = int(sys.argv[3]) if len(sys.argv) > 3 else 8
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', 'fps=0.5,scale=160:90', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160, 3); px = fr.reshape(-1, 3).astype(float)
rng = np.random.default_rng(1); s = px[rng.choice(len(px), min(60000, len(px)), replace=False)]; c = s[rng.choice(len(s), k, replace=False)]
for _ in range(20):
    lab = np.argmin(((s[:, None, :]-c[None])**2).sum(2), 1)
    for i in range(k):
        if (lab == i).any(): c[i] = s[lab == i].mean(0)
lab = np.argmin(((px[::7, None, :]-c[None])**2).sum(2), 1); cnt = np.bincount(lab, minlength=k)/len(lab); order = np.argsort(-cnt)
lum = lambda x: 0.2126*x[0]/255+0.7152*x[1]/255+0.0722*x[2]/255
hexs = [{'hex': '#%02x%02x%02x' % tuple(int(v) for v in c[i]), 'share': round(float(cnt[i]), 3), 'luma': round(lum(c[i]), 3)} for i in order]
mx = px.max(1); mn = px.min(1); sat = float(np.mean((mx-mn)/np.maximum(mx, 1))); br = float(px.mean()/255)
corner = fr[:, :8, :8].reshape(-1, 3).mean(0); l1, l2 = max(lum(c[i]) for i in range(k)), min(lum(c[i]) for i in range(k))
res = {'palette': hexs, 'mean_saturation': round(sat, 3), 'mean_brightness': round(br, 3), 'corner_color_guess': '#%02x%02x%02x' % tuple(int(x) for x in corner), 'contrast_ratio_extremes': round((l1+0.05)/(l2+0.05), 2), 'frames_sampled': int(len(fr))}
json.dump(res, open(out, 'w'), indent=1); print(res['palette'][:5], 'sat', res['mean_saturation'], 'bright', res['mean_brightness'])
