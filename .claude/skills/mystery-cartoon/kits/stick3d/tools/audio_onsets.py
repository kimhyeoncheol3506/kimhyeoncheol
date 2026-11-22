#!/usr/bin/env python3
"""audio_onsets.py <video> <out.json>  -> onset times, level (dB), spectral centroid, duration and a class guess per onset + density per minute.
Claude cannot hear audio; this is measurement only. Speech onsets are included (filter by context/silence map)."""
import subprocess, sys, json, numpy as np
v, out = sys.argv[1], sys.argv[2]; SR = 16000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vn', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32)/32768
if len(x) < SR: json.dump({'error': 'no/short audio'}, open(out, 'w')); print('no audio'); sys.exit(0)
N, HOP = 512, 160; win = np.hanning(N); n = 1+(len(x)-N)//HOP
S = np.abs(np.array([np.fft.rfft(x[i*HOP:i*HOP+N]*win) for i in range(n)])); f = np.fft.rfftfreq(N, 1/SR)
flux = np.maximum(0, np.diff(S, axis=0)).sum(1); flux = np.r_[0, flux]; thr = flux.mean()+1.6*flux.std(); minD = 8
ons = []; last = -minD
for i in range(2, n-2):
    if flux[i] > thr and flux[i] >= flux[i-1] and flux[i] >= flux[i+1] and i-last >= minD: ons.append(i); last = i
rms = np.sqrt(np.convolve(x**2, np.ones(HOP*3)/(HOP*3), 'same')); res = []
for i in ons:
    a = i*HOP; seg = x[a:a+int(SR*0.06)]; sp = S[i:i+6].mean(0)+1e-9; cen = float((f*sp).sum()/sp.sum()); flat = float(np.exp(np.log(sp).mean())/sp.mean())
    pk = rms[a:a+int(SR*0.3)].max() if a < len(rms) else 0; end = a
    while end < min(len(rms)-1, a+SR) and rms[end] > 0.2*pk: end += 80
    d = (end-a)/SR; lvl = 20*np.log10(np.sqrt((seg**2).mean())+1e-9)
    cl = 'click/tick' if d < 0.09 and cen > 2500 else 'pop/blip' if d < 0.35 and flat < 0.25 else 'whoosh/riser (noisy)' if flat >= 0.25 and d >= 0.2 else 'impact/thump' if cen < 600 else 'tonal/chime' if flat < 0.15 and d >= 0.35 else 'other'
    res.append({'t': round(a/SR, 3), 'level_db': round(float(lvl), 1), 'centroid_hz': round(cen), 'flatness': round(flat, 2), 'dur_s': round(d, 2), 'class_guess': cl})
dur = len(x)/SR; cls = {}
for r in res: cls[r['class_guess']] = cls.get(r['class_guess'], 0)+1
summ = {'duration_s': round(dur, 2), 'onsets': len(res), 'per_minute': round(len(res)/dur*60, 1), 'class_counts': cls, 'rms_db_mean': round(float(20*np.log10(np.sqrt((x**2).mean())+1e-9)), 1)}
json.dump({'summary': summ, 'onsets': res}, open(out, 'w'), indent=1); print(summ)
