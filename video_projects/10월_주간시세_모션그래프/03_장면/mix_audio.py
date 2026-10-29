# -*- coding: utf-8 -*-
"""문장별 음성 + BGM + 효과음을 한 파일(hf/assets/audio.wav, 48kHz 스테레오, -16 LUFS)로 합친다. 규칙: BGM -25dB, 효과음 본편 1분에 2개 이하."""
import os, subprocess, sys, wave
import numpy as np
sys.argv = [sys.argv[0]]  # build_hf가 --est를 읽지 않게
import build_hf as B

SR = 48000; HERE = B.HERE; A = f"{HERE}/audio_assets"


def load(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


L = int(B.TOTAL * SR) + SR
voice = np.zeros(L, np.float32)
for T in B.TL:
    for x in T["sents"]:
        a = load(x["wav"]); i = int((T["start"] + x["start"]) * SR); voice[i:i + len(a)] += a
voice *= 0.95 / (np.max(np.abs(voice)) + 1e-9)
bg = load(f"{A}/sfx/bgm_upbeat_loop.wav"); bgm = np.tile(bg, L // len(bg) + 1)[:L]
fade = np.ones(L, np.float32); fade[-3 * SR:] = np.linspace(1, 0, 3 * SR); fade[:SR] = np.linspace(0, 1, SR)
mix = voice + bgm * 10 ** (-25 / 20) * fade
GAIN = {"쿠궁": -8, "물방울": -14}
ev = []
intro = B.TL[0]
ev.append((intro["start"] + intro["sents"][0]["start"] + 0.25, "쿠궁"))
ev.append((intro["start"] + intro["sents"][1]["start"] + 0.15, "쿠궁"))
for T in B.TL:
    if T["s"]["kind"] == "chapter": ev.append((T["start"] + 0.1, "물방울"))
for tt, e in ev:
    x = load(f"{A}/sfx/{e}.wav") * 10 ** (GAIN[e] / 20); i = int(tt * SR); mix[i:i + len(x)] += x[:max(0, L - i)]
mix = np.clip(mix * (0.89 / (np.max(np.abs(mix)) + 1e-9)), -1, 1)
tmp = f"{HERE}/mix_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
os.makedirs(f"{B.HF}/assets", exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-16:TP=-2.0:LRA=11,alimiter=limit=0.84:level=disabled", "-ac", "2", "-ar", str(SR), f"{B.HF}/assets/audio.wav"], check=True)
os.remove(tmp)
print(f"오디오 완료: {B.TOTAL:.1f}s, 효과음 {len(ev)}개")
