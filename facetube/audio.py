"""효과음·배경음 합성(저작권 걱정 없는 자체 생성) + 최종 믹스."""
import subprocess
import numpy as np
import soundfile as sf

SR = 44100
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, decay=8.0):
    t = np.arange(n) / SR
    e = np.exp(-t * decay)
    k = int(a * SR)
    if k:
        e[:k] *= np.linspace(0, 1, k)
    return e


def _bandnoise(n, lo, hi):
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)


def sfx(name):
    if name == "pop":
        t = _t(0.12)
        f = 500 + 900 * (t / t[-1])
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 30)
    elif name == "whoosh":
        n = int(0.38 * SR)
        x = np.zeros(n)
        for i, (lo, hi) in enumerate([(300, 900), (600, 1800), (1200, 3600), (2000, 6000)]):
            seg = _bandnoise(n, lo, hi)
            w = np.exp(-((np.arange(n) / n - (0.25 + i * 0.13)) ** 2) / 0.012)
            x += seg * w
        x /= np.max(np.abs(x)) + 1e-9
    elif name == "boom":
        t = _t(0.7)
        f = 90 * np.exp(-t * 4) + 42
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.003, 5)
        x += _bandnoise(len(t), 80, 2000) * _env(len(t), 0.001, 30) * 0.5
    elif name == "ding":
        t = _t(0.9)
        x = (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t) + 0.25 * np.sin(2 * np.pi * 3951 * t))
        x *= _env(len(t), 0.002, 5)
    elif name == "swish":
        n = int(0.18 * SR)
        x = _bandnoise(n, 2500, 9000) * np.sin(np.linspace(0, np.pi, n)) ** 2
    elif name == "tick":
        t = _t(0.04)
        x = np.sin(2 * np.pi * 2200 * t) * _env(len(t), 0.001, 90)
    elif name == "click":
        t = _t(0.03)
        x = _bandnoise(len(t), 1500, 8000) * _env(len(t), 0.0005, 200)
    elif name == "tada":
        x = np.zeros(int(1.0 * SR))
        for k, f0 in enumerate((523, 659, 784, 1047)):
            t = _t(0.8)
            s = int(k * 0.06 * SR)
            x[s:s + len(t)] += np.sin(2 * np.pi * f0 * t) * _env(len(t), 0.003, 4) * 0.5
    else:
        raise ValueError(name)
    return (x / (np.max(np.abs(x)) + 1e-9)).astype(np.float32)


# ---------------------------------------------------------------- BGM
def _pluck(freq, dur, decay=0.996):
    n = int(dur * SR)
    p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def _note(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def bgm(duration, bpm=104, mood="bright"):
    """가벼운 지식채널풍 루프: 플럭 코드 + 베이스 + 킥/하이햇."""
    beat = 60 / bpm
    bar = beat * 4
    prog = {"bright": [(60, 64, 67), (67, 71, 74), (69, 72, 76), (65, 69, 72)],
            "tense": [(57, 60, 64), (53, 57, 60), (55, 59, 62), (52, 56, 59)]}[mood]
    loop_len = bar * len(prog)
    n = int(loop_len * SR)
    x = np.zeros(n + SR)
    cache = {}
    def pl(m, d):
        k = (m, round(d, 3))
        if k not in cache:
            cache[k] = _pluck(_note(m), d)
        return cache[k]
    for bi, chord in enumerate(prog):
        b0 = bi * bar
        for e in range(8):  # 8분음표 아르페지오
            if e in (3, 7):
                continue
            m = chord[[0, 1, 2, 1, 0, 2, 1, 2][e]] + 12
            s = int((b0 + e * beat / 2) * SR)
            v = pl(m, beat * 0.9) * 0.22
            x[s:s + len(v)] += v
        bt = _t(bar)
        bass = np.sin(2 * np.pi * _note(chord[0] - 24) * bt) * np.exp(-((bt % beat) * 3)) * 0.35
        x[int(b0 * SR):int(b0 * SR) + len(bass)] += bass
        for k in range(4):
            s = int((b0 + k * beat) * SR)
            if k in (0, 2):
                kt = _t(0.25)
                kick = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-kt * 25) + 45) / SR) * np.exp(-kt * 14) * 0.5
                x[s:s + len(kick)] += kick
            for h in (0, 0.5):
                hs = s + int(h * beat * SR)
                hat = _bandnoise(int(0.05 * SR), 6000, 14000) * _env(int(0.05 * SR), 0.001, 70) * 0.06
                x[hs:hs + len(hat)] += hat
    loop = x[:n]
    reps = int(np.ceil(duration / loop_len)) + 1
    full = np.tile(loop, reps)[:int(duration * SR)]
    fade = int(1.5 * SR)
    full[:fade] *= np.linspace(0, 1, fade)
    full[-fade:] *= np.linspace(1, 0, fade)
    return (full / (np.max(np.abs(full)) + 1e-9) * 0.8).astype(np.float32)


def place(track, clip, t, gain_db=0.0):
    s = int(t * SR)
    if s >= len(track):
        return
    e = min(len(track), s + len(clip))
    track[s:e] += clip[:e - s] * (10 ** (gain_db / 20))


def mix(voice_wav, sfx_wav, bgm_wav, out_wav, style):
    a = style["audio"]
    fc = (f"[2:a]volume={a['bgm_db']}dB[b];[0:a]asplit=2[v1][v2];"
          f"[b][v1]sidechaincompress=threshold=0.03:ratio={a['duck_ratio']}:attack=20:release=350[bd];"
          f"[1:a]volume={a['sfx_db']}dB[s];"
          f"[v2][bd][s]amix=inputs=3:normalize=0,"
          f"loudnorm=I={a['loudness_lufs']}:TP=-1.5:LRA=11,aresample=48000[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice_wav, "-i", sfx_wav, "-i", bgm_wav,
                    "-filter_complex", fc, "-map", "[out]", "-ac", "2", out_wav], check=True)


def write(path, x):
    sf.write(path, np.clip(x, -1, 1), SR)
