#!/usr/bin/env python3
"""motion_stats.py <video> <out.json> [fps=10]  -> motion energy per step, global camera translation (phase correlation), shake amplitude, static ratio.
No OpenCV needed. Use the series to place cuts/camera moves; use contact_sheets (dense) to read individual animations."""
import subprocess, sys, json, numpy as np
v, out = sys.argv[1], sys.argv[2]; fps = float(sys.argv[3]) if len(sys.argv) > 3 else 10
W, H = 128, 72
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'fps={fps},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)/255
en, dx, dy = [], [], []; win = np.outer(np.hanning(H), np.hanning(W))
for i in range(1, len(fr)):
    en.append(float(np.abs(fr[i]-fr[i-1]).mean()))
    A = np.fft.fft2(fr[i-1]*win); B = np.fft.fft2(fr[i]*win); R = A*np.conj(B); R /= np.abs(R)+1e-9; r = np.fft.ifft2(R).real
    y, x = np.unravel_index(np.argmax(r), r.shape); x = x-W if x > W//2 else x; y = y-H if y > H//2 else y; dx.append(float(x)/W); dy.append(float(y)/H)
en = np.array(en); dxa = np.array(dx); dya = np.array(dy); k = 5; ma = lambda a: np.convolve(a, np.ones(k)/k, 'same')
peaks = [round((i+1)/fps, 2) for i in range(len(en)) if en[i] > en.mean()+2*en.std()]
res = {'fps': fps, 'steps': len(en), 'mean_energy': round(float(en.mean()), 5), 'static_ratio': round(float((en < 0.002).mean()), 3), 'energy_peaks_s': peaks[:200],
       'median_abs_pan_x_per_step': round(float(np.median(np.abs(dxa))), 5), 'median_abs_pan_y_per_step': round(float(np.median(np.abs(dya))), 5),
       'shake_std_x': round(float(np.std(dxa-ma(dxa))), 5), 'shake_std_y': round(float(np.std(dya-ma(dya))), 5),
       'energy_series': [round(float(x), 4) for x in en[::2]], 'pan_x_series': [round(float(x), 4) for x in dxa[::2]], 'pan_y_series': [round(float(x), 4) for x in dya[::2]]}
json.dump(res, open(out, 'w')); print({k: res[k] for k in ('mean_energy', 'static_ratio', 'median_abs_pan_x_per_step', 'shake_std_x')}, 'peaks', len(peaks))
