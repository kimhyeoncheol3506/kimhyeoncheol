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
    elif name == "paper":            # 종이 카드가 내려앉는 소리(사각 + 톡)
        n = int(0.26 * SR)
        x = _bandnoise(n, 900, 7000) * np.sin(np.linspace(0, np.pi, n)) ** 3 * 0.8
        x += _bandnoise(n, 150, 900) * _env(n, 0.002, 40) * 0.6
    elif name == "pen":              # 형광펜 긋는 소리(짧은 마찰음)
        n = int(0.5 * SR)
        x = _bandnoise(n, 2500, 9000) * (0.6 + 0.4 * np.sin(np.linspace(0, 9 * np.pi, n)) ** 2) * np.sin(np.linspace(0, np.pi, n))
    elif name == "softwhoosh":       # 챕터 전환용 낮고 부드러운 휙
        n = int(0.9 * SR)
        x = _bandnoise(n, 120, 1600) * np.exp(-((np.arange(n) / n - 0.45) ** 2) / 0.03)
    elif name == "tada":
        x = np.zeros(int(1.0 * SR))
        for k, f0 in enumerate((523, 659, 784, 1047)):
            t = _t(0.8)
            s = int(k * 0.06 * SR)
            x[s:s + len(t)] += np.sin(2 * np.pi * f0 * t) * _env(len(t), 0.003, 4) * 0.5
    else:
        raise ValueError(name)
    return (x / (np.max(np.abs(x)) + 1e-9)).astype(np.float32)


# ---- 실제 녹음 효과음(CC0, 2026-11-24 Stickman Video Director 검토 후 도입) ----------------------------
# assets/sfx/ (catalog.json · LICENSES/). 합성음 이름 → 비슷한 역할의 파일 묶음. 같은 이름이 여러 번 나오면 파일을 돌아가며 써서
# 똑같은 소리 반복을 줄인다. 음량은 같은 이름의 합성음과 RMS 를 맞춰 기존 믹스 위계(dB 값)를 그대로 지킨다.
# 파일 안 실제 어택(최고점)이 놓을 시각에 오게 앞당길 거리(lead)를 함께 돌려준다(접촉 순간 맞추기).
import glob as _glob, os as _os
SFX_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "assets", "sfx")
SFX_PACK = {
    "cc0": {
        "whoosh": ["artisticdude-swishes/swish-*"],
        "swish": ["kenney-interface/maximize_*"],
        "pop": ["kenney-interface/select_*", "kenney-interface/pluck_*", "kenney-interface/drop_*"],
        "ding": ["kenney-interface/confirmation_*"],
        "boom": ["kenney-impact/impactPunch_heavy_*"],
        "tick": ["kenney-interface/tick_*", "kenney-interface/click_*"],
        "click": ["kenney-interface/click_*"],
        "paper": ["owlish-home-202/paper-stationery/*"],
    },
}
_sfx_count, _sfx_cache = {}, {}


def _load_any(path):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = x.mean(1)
    if sr != SR:
        x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x).astype(np.float32)
    return x


def sfx_pick(name, pack=None):
    """(clip, lead초). pack 이 없거나 파일이 없으면 합성음 그대로(lead 0)."""
    synth = sfx(name)
    pats = (SFX_PACK.get(pack) or {}).get(name)
    files = sorted(f for p in (pats or []) for f in _glob.glob(_os.path.join(SFX_DIR, p + ("" if p.endswith("*") else "")))
                   if f.lower().endswith((".ogg", ".wav", ".mp3", ".flac")))
    if not files:
        return synth, 0.0
    k = _sfx_count.get(name, 0)
    _sfx_count[name] = k + 1
    f = files[(k * 7) % len(files)]                 # 7씩 건너뛰며 돌림(바로 옆 비슷한 변형을 연달아 쓰지 않게)
    if f not in _sfx_cache:
        x = _load_any(f)
        nz = np.where(np.abs(x) > 0.02 * (np.max(np.abs(x)) + 1e-9))[0]
        if len(nz):
            x = x[max(0, nz[0] - int(0.005 * SR)):nz[-1] + int(0.02 * SR)]   # 앞뒤 무음 자르기
        rms = lambda v: float(np.sqrt(np.mean(v ** 2)) + 1e-9)
        x = x * (rms(synth) / rms(x))
        pk = np.max(np.abs(x))
        if pk > 1.0:
            x = x / pk
        lead = min(0.08, int(np.argmax(np.abs(x))) / SR)
        _sfx_cache[f] = (x.astype(np.float32), lead)
    return _sfx_cache[f]


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


def _epiano(freq, dur):
    """부드러운 전자피아노 한 음(배음 몇 개 + 느린 감쇠)."""
    t = _t(dur)
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 3) + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 6)
    k = int(0.006 * SR)
    x[:k] *= np.linspace(0, 1, k)
    return x * np.exp(-t * 1.6)


def bgm_calm(duration, bpm=70):
    """다큐·경제 해설용 잔잔한 배경음: 느린 피아노 아르페지오 + 패드, 북 없음."""
    beat = 60 / bpm
    bar = beat * 4
    prog = [(57, 60, 64, 67), (53, 57, 60, 64), (48, 52, 55, 59), (55, 59, 62, 65)]   # Am7 - Fmaj7 - Cmaj7 - G7
    loop_len = bar * len(prog)
    n = int(loop_len * SR)
    x = np.zeros(n + 4 * SR)
    for bi, ch in enumerate(prog):
        b0 = bi * bar
        for e, idx in enumerate((0, 2, 1, 3, 2, 1)):             # 한 마디에 여섯 음, 마지막 박은 쉼
            s = int((b0 + e * bar / 6.5) * SR)
            v = _epiano(_note(ch[idx] + 12), 2.4) * 0.16
            x[s:s + len(v)] += v
        t = _t(bar + 0.6)                                         # 패드: 천천히 차오르고 빠지는 화음
        env = np.sin(np.linspace(0, np.pi, len(t))) ** 1.5
        pad = sum(np.sin(2 * np.pi * _note(m) * t * (1 + det)) for m in ch[:3] for det in (-0.002, 0.002)) * env * 0.035
        s = int(b0 * SR)
        x[s:s + len(pad)] += pad
        bass = _epiano(_note(ch[0] - 12), bar) * 0.22
        x[s:s + len(bass)] += bass
    loop = x[:n] + np.concatenate([x[n:n + 4 * SR], np.zeros(n - 4 * SR)])   # 끝에 남은 울림을 처음에 겹쳐 이음새 없앰
    reps = int(np.ceil(duration / loop_len)) + 1
    full = np.tile(loop, reps)[:int(duration * SR)]
    fade = int(2.5 * SR)
    full[:fade] *= np.linspace(0, 1, fade)
    full[-fade:] *= np.linspace(1, 0, fade)
    return (full / (np.max(np.abs(full)) + 1e-9) * 0.8).astype(np.float32)


def bgm_from_file(path, duration, fade=1.5, xfade=0.5):
    """외부에서 만든 음악 파일(Suno 등)을 배경음으로 쓴다. 짧으면 이음새를 크로스페이드로 반복, 길면 자른다."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    if len(x) < SR // 2:
        raise SystemExit(f"배경음 파일을 읽을 수 없거나 너무 짧음: {path}")
    n = int(duration * SR)
    xf = min(int(xfade * SR), len(x) // 4)
    out = x
    while len(out) < n:                                   # 이음새 크로스페이드로 반복
        w = np.linspace(0, 1, xf, dtype=np.float32)
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - w) + x[:xf] * w, x[xf:]])
    out = out[:n].copy()
    f = min(int(fade * SR), n // 2)
    out[:f] *= np.linspace(0, 1, f)
    out[-f:] *= np.linspace(1, 0, f)
    return (out / (np.max(np.abs(out)) + 1e-9) * 0.8).astype(np.float32)


def make_bgm(proj, duration, default_bpm=104):
    """proj.bgm.path 가 있으면 그 파일, 없으면 직접 합성한 배경음."""
    b = proj.get("bgm") or {}
    if b.get("path"):
        import os
        path = b["path"]
        if not os.path.isabs(path):
            cand = [os.path.join(proj.get("_dir", "."), path), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)]
            path = next((c for c in cand if os.path.exists(c)), cand[0])
        if not os.path.exists(path):
            raise SystemExit(f"배경음 파일이 없음: {path}")
        return bgm_from_file(path, duration)
    if proj.get("bgm_mood") == "calm":
        return bgm_calm(duration, bpm=proj.get("bgm_bpm", 70))
    return bgm(duration, bpm=proj.get("bgm_bpm", default_bpm), mood=proj.get("bgm_mood", "bright"))


def place(track, clip, t, gain_db=0.0):
    s = int(t * SR)
    if s >= len(track):
        return
    e = min(len(track), s + len(clip))
    track[s:e] += clip[:e - s] * (10 ** (gain_db / 20))


def mix(voice_wav, sfx_wav, bgm_wav, out_wav, style):
    a = style["audio"]
    vchain = (a["voice_chain"] + ",") if a.get("voice_chain") else ""     # 목소리 다듬기(EQ·컴프레서), 없으면 그대로
    fc = (f"[2:a]volume={a['bgm_db']}dB[b];[0:a]{vchain}asplit=2[v1][v2];"
          f"[b][v1]sidechaincompress=threshold=0.03:ratio={a['duck_ratio']}:attack=20:release=350[bd];"
          f"[1:a]volume={a['sfx_db']}dB[s];"
          f"[v2][bd][s]amix=inputs=3:normalize=0,"
          f"loudnorm=I={a['loudness_lufs']}:TP=-1.5:LRA=11,aresample=48000[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice_wav, "-i", sfx_wav, "-i", bgm_wav,
                    "-filter_complex", fc, "-map", "[out]", "-ac", "2", out_wav], check=True)


def write(path, x):
    sf.write(path, np.clip(x, -1, 1), SR)
