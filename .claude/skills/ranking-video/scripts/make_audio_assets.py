# -*- coding: utf-8 -*-
"""효과음 5종 + 로파이 BGM 루프 합성 (ranking-video v1.2.0). 외부 음원 없이 numpy로 직접 만들어 저작권 걱정이 없다.

사용법: python3 -I make_audio_assets.py  (현재 폴더에 sfx/ 생성)
"""
import numpy as np, wave, os
SR = 48000; os.makedirs("sfx", exist_ok=True)
rng = np.random.default_rng(7)
def save(name, x):
    x = np.clip(x / (np.max(np.abs(x)) + 1e-9) * 0.9, -1, 1)
    with wave.open(f"sfx/{name}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
def t(d): return np.arange(int(SR * d)) / SR
# 칼 소리: 짧은 고역 노이즈 + 나무 도마 저역 톡
tt = t(0.25); n = rng.standard_normal(len(tt)); hp = n - np.convolve(n, np.ones(8) / 8, "same")
save("칼 소리", hp * np.exp(-tt * 60) + 0.8 * np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 35))
# 물방울: 위로 휘는 사인 블립
tt = t(0.3); f = 600 + 1400 * (1 - np.exp(-tt * 25)); ph = 2 * np.pi * np.cumsum(f) / SR
save("물방울", np.sin(ph) * np.exp(-tt * 18) * (1 - np.exp(-tt * 400)))
# 쿠궁: 저역 하강 사인 + 노이즈 어택
tt = t(1.4); f = 70 * np.exp(-tt * 1.2) + 35; ph = 2 * np.pi * np.cumsum(f) / SR
save("쿠궁", np.sin(ph) * np.exp(-tt * 2.5) + 0.3 * rng.standard_normal(len(tt)) * np.exp(-tt * 30))
# 코인: 두 음 벨
tt = t(0.6); a = np.sin(2 * np.pi * 1975 * tt) * np.exp(-tt * 8); b = np.sin(2 * np.pi * 2637 * tt) * np.exp(-(tt - 0.08).clip(0) * 6) * (tt > 0.08)
save("코인", a * 0.6 + b)
# 갈매기: 하강 처프 2회
out = np.zeros(int(SR * 1.2))
for st in (0.0, 0.45):
    tt = t(0.35); f = 2200 - 900 * tt / 0.35 + 150 * np.sin(2 * np.pi * 30 * tt); ph = 2 * np.pi * np.cumsum(f) / SR
    s = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.sin(np.pi * tt / 0.35) ** 1.5; i = int(st * SR); out[i:i + len(s)] += s
save("갈매기", out)
# BGM: 82BPM 로파이 코드 루프 (Cmaj7-Am7-Fmaj7-G7), 16마디
bpm = 82; beat = 60 / bpm; bar = beat * 4
chords = [[48, 52, 55, 59, 64], [45, 52, 55, 60, 64], [41, 48, 52, 57, 60], [43, 50, 53, 59, 62]]
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
L = int(SR * bar * 16); bgm = np.zeros(L)
for b in range(16):
    c = chords[b % 4]; st = int(b * bar * SR); tt = t(bar)
    env = (1 - np.exp(-tt * 12)) * np.exp(-tt * 0.5)
    for m in c:
        f = mtof(m); bgm[st:st + len(tt)] += env * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 3)) * 0.18
    bt = t(bar); bass = np.sin(2 * np.pi * mtof(c[0] - 12) * bt) * np.exp(-(bt % (beat * 2)) * 3) * 0.5
    bgm[st:st + len(bt)] += bass
    for k in range(4):
        i = st + int(k * beat * SR); kt = t(0.25)
        if k in (0, 2): bgm[i:i + len(kt)] += np.sin(2 * np.pi * (55 + 60 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * 0.9
        for h in (0, 0.5):
            j = i + int(h * beat * SR); ht = t(0.05); bgm[j:j + len(ht)] += rng.standard_normal(len(ht)) * np.exp(-ht * 90) * 0.08
lp = np.convolve(bgm, np.ones(6) / 6, "same")
save("bgm_loop", lp)
print("ok", round(L / SR, 1), "s loop")
