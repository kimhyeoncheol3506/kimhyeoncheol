# -*- coding: utf-8 -*-
"""음성 + 차분한 BGM(-26dB, 효과음 없음) → hf/assets/audio.wav (-16 LUFS)"""
import os, subprocess, sys, wave
import numpy as np
sys.argv = [sys.argv[0]]
import build_hf as B
SR = 48000
BGM = "/home/user/kimhyeoncheol/video_projects/10월_주간시세_모션그래프/03_장면/audio_assets/sfx/bgm_loop.wav"
load = lambda p: np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout, dtype=np.float32).copy()
L = int(B.TOTAL * SR) + SR; v = np.zeros(L, np.float32)
for T in B.TL:
    for x in T["S"]:
        a = load(x["wav"]); i = int((T["start"] + x["start"]) * SR); v[i:i + len(a)] += a
v *= 0.95 / (np.abs(v).max() + 1e-9)
bg = load(BGM); bg = np.tile(bg, L // len(bg) + 1)[:L]
fade = np.ones(L, np.float32); fade[:2 * SR] = np.linspace(0, 1, 2 * SR); fade[-4 * SR:] = np.linspace(1, 0, 4 * SR)
mix = np.clip((v + bg * 10 ** (-26 / 20) * fade) * 0.89 / (np.abs(v).max() + 1e-9), -1, 1)
tmp = f"{B.HERE}/mix_raw.wav"
with wave.open(tmp, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-16:TP=-2.0:LRA=11,alimiter=limit=0.84:level=disabled", "-ac", "2", "-ar", str(SR), f"{B.HF}/assets/audio.wav"], check=True); os.remove(tmp)
print(f"오디오 {B.TOTAL:.1f}s")
