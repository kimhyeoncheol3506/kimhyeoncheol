"""효과음/BGM 합성(저작권 걱정 없는 자체 생성) + 내레이션 믹싱 + 사이드체인 더킹."""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 44100
_rng = np.random.default_rng(7)


def _t(sec):
    return np.arange(int(SR * sec)) / SR


def _env(n, attack=0.005, release=None, curve=6.0):
    a = max(1, int(SR * attack))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    if release is None:
        e[a:] = np.exp(-curve * np.linspace(0, 1, n - a))
    return e


def _lowpass(x, alpha):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # 짧은 효과음에만 사용
        acc += alpha * (v - acc)
        y[i] = acc
    return y


def _bandsweep_noise(sec, f0, f1):
    """노이즈를 시간에 따라 움직이는 공진 필터로 → 휙 소리."""
    n = int(SR * sec)
    noise = _rng.standard_normal(n)
    f = np.linspace(f0, f1, n)
    out = np.zeros(n)
    y1 = y2 = 0.0
    r = 0.97
    for i in range(n):
        w = 2 * np.pi * f[i] / SR
        y = noise[i] * (1 - r) + 2 * r * np.cos(w) * y1 - r * r * y2
        y2, y1 = y1, y
        out[i] = y
    return out / (np.abs(out).max() + 1e-9)


def sfx_whoosh(sec=0.45):
    x = _bandsweep_noise(sec, 400, 3200)
    n = len(x)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * e * 0.55


def sfx_pop():
    t = _t(0.09)
    f = np.linspace(950, 280, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, curve=9) * 0.6


def sfx_boom():
    t = _t(1.2)
    f = 38 + 70 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    hit = _rng.standard_normal(len(t)) * np.exp(-t * 40) * 0.5
    x = body + hit
    return np.tanh(x * 1.8) * 0.75


def sfx_ding():
    t = _t(1.1)
    x = (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t) + 0.25 * np.sin(2 * np.pi * 3955 * t))
    return x * np.exp(-t * 4.5) * _env(len(t), 0.002, release=False) * 0.3


def sfx_stamp():
    t = _t(0.6)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 120 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)
    click = _rng.standard_normal(len(t)) * np.exp(-t * 90)
    return np.tanh((thud + 0.6 * click) * 2.2) * 0.8


def sfx_scratch():
    t = _t(0.55)
    f = 900 + 700 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 2)
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    noise = _rng.standard_normal(len(t)) * 0.3
    return (saw * 0.5 + noise) * np.exp(-t * 3) * 0.35


def sfx_marker():
    """마커로 동그라미 그리는 쓱쓱 소리."""
    x = _bandsweep_noise(0.5, 2500, 3800)
    n = len(x)
    e = (0.6 + 0.4 * np.sin(np.linspace(0, 6 * np.pi, n))) * np.sin(np.linspace(0, np.pi, n))
    return x * e * 0.22


def sfx_riser(sec=1.2):
    x = _bandsweep_noise(sec, 300, 5000)
    return x * np.linspace(0, 1, len(x)) ** 2 * 0.4


def sfx_tick():
    t = _t(0.03)
    return _rng.standard_normal(len(t)) * np.exp(-t * 200) * 0.25


SFX = {
    "whoosh": sfx_whoosh, "pop": sfx_pop, "boom": sfx_boom, "ding": sfx_ding,
    "stamp": sfx_stamp, "scratch": sfx_scratch, "marker": sfx_marker,
    "riser": sfx_riser, "tick": sfx_tick,
}
_sfx_cache: dict[str, np.ndarray] = {}


def get_sfx(name):
    if name not in _sfx_cache:
        _sfx_cache[name] = SFX[name]().astype(np.float32)
    return _sfx_cache[name]


# ---------- BGM ----------
def _add(buf, i, x):
    if i >= len(buf):
        return
    m = min(len(x), len(buf) - i)
    buf[i:i + m] += x[:m]


def _note(freq, sec, kind="ep"):
    t = _t(sec)
    if kind == "ep":  # 일렉피아노 느낌
        x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 3)
        return x * np.exp(-t * 1.6) * _env(len(t), 0.01, release=False)
    if kind == "bass":
        return np.tanh(2 * np.sin(2 * np.pi * freq * t)) * np.exp(-t * 2.5)
    raise ValueError(kind)


def _midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def bgm_lofi(duration, bpm=84):
    """로파이 루프: Fmaj7 - Em7 - Dm7 - Cmaj7."""
    beat = 60 / bpm
    bar = beat * 4
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
    n = int(SR * (duration + bar))
    out = np.zeros(n)
    t = 0.0
    i = 0
    while t < duration:
        ch = chords[i % 4]
        for k, m in enumerate(ch):
            s = _note(_midi(m + 12), bar * 0.98) * 0.11
            st = int(SR * (t + k * 0.012))
            _add(out, st, s)
        b = _note(_midi(ch[0] - 12), beat * 1.8, "bass") * 0.16
        for off in (0, beat * 2.5):
            st = int(SR * (t + off))
            _add(out, st, b)
        for k in range(8):  # 하이햇
            h = sfx_tick() * (0.35 if k % 2 else 0.2)
            st = int(SR * (t + k * beat / 2 + (0.02 if k % 2 else 0)))
            _add(out, st, h)
        for k in (0, 2):  # 킥
            kk = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-_t(0.3) * 25)) / SR) * np.exp(-_t(0.3) * 10) * 0.3
            st = int(SR * (t + k * beat))
            _add(out, st, kk)
        t += bar
        i += 1
    return out[: int(SR * duration)].astype(np.float32)


def bgm_tension(duration, bpm=100):
    """사연 쇼츠용 긴장감 펄스: 8분음표 베이스 + 하이햇."""
    beat = 60 / bpm
    n = int(SR * (duration + 2))
    out = np.zeros(n)
    roots = [45, 45, 41, 43]  # A A F G
    t, bar_i = 0.0, 0
    while t < duration:
        r = roots[bar_i % 4]
        for k in range(8):
            s = _note(_midi(r - 12), beat / 2 * 0.9, "bass") * 0.13
            st = int(SR * (t + k * beat / 2))
            _add(out, st, s)
            h = sfx_tick() * 0.25
            _add(out, st, h)
        pad = _note(_midi(r + 24), beat * 4, "ep") * 0.05
        st = int(SR * t)
        _add(out, st, pad)
        t += beat * 4
        bar_i += 1
    return out[: int(SR * duration)].astype(np.float32)


# ---------- IO / 믹싱 ----------
def read_wav(path) -> np.ndarray:
    with wave.open(str(path)) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw == 2:
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    elif sw == 4:
        x = np.frombuffer(raw, np.int32).astype(np.float32) / 2147483648
    else:
        raise ValueError(f"unsupported sample width {sw}")
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        src = np.arange(len(x)) / sr
        dst = np.arange(int(len(x) * SR / sr)) / SR
        x = np.interp(dst, src, x).astype(np.float32)
    return x


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype(np.int16)
    if pcm.ndim == 1:
        pcm = np.stack([pcm, pcm], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def wav_duration(path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def mix(duration, voices, sfx_events, bgm=None, bgm_gain=0.5, duck=0.35):
    """voices: [(start, np.array)], sfx_events: [(start, name, gain)]"""
    n = int(SR * duration) + SR
    voice = np.zeros(n, np.float32)
    for st, x in voices:
        i = int(SR * st)
        _add(voice, i, x)
    peak = np.abs(voice).max()
    if peak > 0:
        voice *= 0.89 / peak  # 내레이션 -1dB 정규화
    fx = np.zeros(n, np.float32)
    for st, name, g in sfx_events:
        s = get_sfx(name) * g
        i = int(SR * max(0, st))
        _add(fx, i, s)
    out = voice + fx * 0.8
    if bgm is not None:
        b = np.zeros(n, np.float32)
        b[: len(bgm)] = bgm[:n]
        # 사이드체인: 목소리 나올 때 BGM 감쇠
        env = np.abs(voice)
        k = int(SR * 0.15)
        env = np.convolve(env, np.ones(k) / k, mode="same")
        env = np.clip(env * 12, 0, 1)
        gain = bgm_gain * (1 - (1 - duck) * env)
        fade = np.ones(n, np.float32)
        fl = int(SR * 1.5)
        end = int(SR * duration)
        fade[max(0, end - fl):end] = np.linspace(1, 0, min(fl, end))
        fade[end:] = 0
        out += b * gain * fade
    out = out[: int(SR * duration)]
    return np.tanh(out * 1.05) * 0.89  # 소프트 리미터 + 1dB 여유(AAC 인코딩 오버슈트 방지)
