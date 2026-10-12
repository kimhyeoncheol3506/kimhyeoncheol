"""배경음악 합성 + 사이드체인 더킹 (저작권 클레임 없는 자체 생성 음원).

연애 튜토리얼 스튜디오(shorts-studio/studio/audio.py)의 로파이 BGM·더킹 방식을 경제 채널용으로 이식:
  - lofi   : 차분한 로파이 (롱폼 설명용)  Fmaj7 - Em7 - Dm7 - Cmaj7
  - pulse  : 쇼츠용 가벼운 펄스          Am - F - C - G
목소리가 나올 때 BGM을 자동으로 줄여(더킹) 내레이션이 묻히지 않게 한다.
"""
from __future__ import annotations

import subprocess
import wave

import numpy as np

SR = 48000
_rng = np.random.default_rng(7)


def _t(sec):
    return np.arange(int(SR * sec)) / SR


def _midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def _add(buf, i, x):
    if i >= len(buf):
        return
    m = min(len(x), len(buf) - i)
    buf[i:i + m] += x[:m]


def _ep(freq, sec):
    t = _t(sec)
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 3)
    a = int(SR * 0.01)
    env = np.exp(-t * 1.6)
    env[:a] *= np.linspace(0, 1, a)
    return x * env


def _bass(freq, sec):
    t = _t(sec)
    return np.tanh(2 * np.sin(2 * np.pi * freq * t)) * np.exp(-t * 2.5)


def _tick():
    t = _t(0.03)
    return _rng.standard_normal(len(t)) * np.exp(-t * 200) * 0.25


def _kick():
    t = _t(0.3)
    return np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 25)) / SR) * np.exp(-t * 10) * 0.3


def bgm(duration: float, style: str = "lofi") -> np.ndarray:
    bpm = 80 if style == "lofi" else 96
    beat = 60 / bpm
    bar = beat * 4
    chords = ([[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]] if style == "lofi"
              else [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 60], [55, 59, 62, 67]])
    out = np.zeros(int(SR * (duration + bar)))
    t, i = 0.0, 0
    while t < duration:
        ch = chords[i % 4]
        for k, m in enumerate(ch):
            _add(out, int(SR * (t + k * 0.012)), _ep(_midi(m + 12), bar * 0.98) * 0.11)
        b = _bass(_midi(ch[0] - 12), beat * 1.8) * 0.16
        for off in (0, beat * 2.5):
            _add(out, int(SR * (t + off)), b)
        for k in range(8):
            _add(out, int(SR * (t + k * beat / 2 + (0.02 if k % 2 else 0))), _tick() * (0.35 if k % 2 else 0.2))
        for k in (0, 2):
            _add(out, int(SR * (t + k * beat)), _kick())
        t += bar
        i += 1
    x = out[: int(SR * duration)]
    fl = int(SR * 2.0)  # 끝 2초 페이드아웃
    x[-fl:] *= np.linspace(1, 0, min(fl, len(x)))[-len(x[-fl:]):]
    fi = int(SR * 1.0)
    x[:fi] *= np.linspace(0, 1, fi)
    return x.astype(np.float32)


def read_wav(path) -> np.ndarray:
    with wave.open(str(path)) as w:
        n, ch = w.getnframes(), w.getnchannels()
        x = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    return x.reshape(-1, ch).mean(axis=1) if ch > 1 else x


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    pcm = np.stack([pcm, pcm], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def mix_bgm(video_in: str, video_out: str, style: str = "lofi", gain: float = 0.18, duck: float = 0.35) -> None:
    """영상의 내레이션 트랙에 BGM을 더킹해 섞고, -14 LUFS로 맞춰 다시 담는다."""
    tmp_v, tmp_m = video_out + ".voice.wav", video_out + ".mix.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video_in, "-vn", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", tmp_v], check=True)
    voice = read_wav(tmp_v)
    music = bgm(len(voice) / SR, style)
    env = np.abs(voice)
    k = int(SR * 0.2)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    env = np.clip(env * 14, 0, 1)
    g = gain * (1 - (1 - duck) * env)  # 목소리 나올 때 BGM을 35%로
    out = voice + music[: len(voice)] * g
    write_wav(tmp_m, np.tanh(out * 1.02) * 0.95)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video_in, "-i", tmp_m, "-map", "0:v", "-map", "1:a",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", video_out], check=True)
    for f in (tmp_v, tmp_m):
        try:
            import os
            os.remove(f)
        except OSError:
            pass
