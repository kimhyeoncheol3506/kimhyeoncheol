"""ffmpeg 도우미: 폰트 찾기, 기본 효과음/BGM 합성, 오디오 분석(무음 구간·온셋)."""
import array
import glob
import os
import re
import shutil
import subprocess
from pathlib import Path

from .rules import ROOT

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

FONT_CANDIDATES = [
    ("assets/fonts/*.ttf", None), ("assets/fonts/*.otf", None), ("assets/fonts/*.ttc", None),
    ("C:/Windows/Fonts/malgunbd.ttf", "Malgun Gothic"),
    ("C:/Windows/Fonts/malgun.ttf", "Malgun Gothic"),
    ("/System/Library/Fonts/AppleSDGothicNeo.ttc", "Apple SD Gothic Neo"),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", "Noto Sans CJK KR"),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "Noto Sans CJK KR"),
    ("/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf", "NanumGothic"),
    ("/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf", "NanumGothic"),
    ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "WenQuanYi Zen Hei"),
]


def run(args, cwd=None, check=True):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"ffmpeg 실패({p.returncode}):\n{p.stderr[-3000:]}")
    return p


def _family(path):
    if shutil.which("fc-scan"):
        p = subprocess.run(["fc-scan", "--format", "%{family[0]}\n", path], capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip().splitlines()[0]
    return Path(path).stem


def find_font(rules):
    f = rules["font"]
    if f["file"] != "auto":
        path = str((ROOT / f["file"]).resolve()) if not os.path.isabs(f["file"]) else f["file"]
        return path, (f["name"] if f["name"] != "auto" else _family(path))
    for pattern, name in FONT_CANDIDATES:
        pat = str(ROOT / pattern) if not os.path.isabs(pattern) and not pattern.startswith("C:") else pattern
        hits = sorted(glob.glob(pat))
        if hits:
            name = f["name"] if f["name"] != "auto" else (name or _family(hits[0]))
            return hits[0], name
    raise RuntimeError("한글 폰트를 찾지 못했습니다. assets/fonts/ 에 .ttf 한글 폰트를 넣어주세요 "
                       "(예: Pretendard, 나눔고딕 — 무료).")


# ── 기본 효과음 / BGM 합성 (사용자가 같은 이름의 파일을 넣으면 그걸 사용) ──
SYNTH = {
    "assets/sfx/ding.wav": ("0.7*sin(2*PI*1568*t)*exp(-14*t)+0.3*sin(2*PI*3136*t)*exp(-20*t)", 0.35),
    "assets/sfx/boing.wav": ("0.6*sin(2*PI*(220*t+700*t*t))*exp(-7*t)*(1+0.3*sin(2*PI*16*t))", 0.4),
    "assets/sfx/pop.wav": ("0.8*sin(2*PI*(160-100*t)*t)*exp(-22*t)+0.3*(random(0)*2-1)*exp(-70*t)", 0.25),
    "assets/sfx/tick.wav": ("0.7*sin(2*PI*2200*t)*exp(-80*t)+0.3*(random(0)*2-1)*exp(-150*t)", 0.08),
}
B = 60 / 128  # 128 BPM
BEAT = (
    f"0.9*sin(2*PI*52*mod(t,{B})*(1+2*exp(-30*mod(t,{B}))))*exp(-9*mod(t,{B}))"           # 킥
    f"+0.35*(random(0)*2-1)*exp(-22*mod(t+{B},{2*B}))"                                     # 스네어(2,4박)
    f"+0.10*(random(1)*2-1)*exp(-90*mod(t+{B/2},{B}))"                                     # 하이햇
    f"+0.20*sin(2*PI*if(lt(mod(t,{8*B}),{4*B}),55,if(lt(mod(t,{8*B}),{6*B}),49,61.7))*t)"  # 베이스
    f"*(0.6+0.4*exp(-6*mod(t,{B/2})))"
)


def ensure_default_assets(rules, log=print):
    made = []
    for rel, (expr, d) in SYNTH.items():
        if not (ROOT / rel).exists():
            (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
            run([FFMPEG, "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d={d}",
                 "-af", "aformat=channel_layouts=stereo", str(ROOT / rel)])
            made.append(rel)
    bgm = rules["editing"]["bgm"]["file"]
    if not (ROOT / bgm).exists():
        (ROOT / bgm).parent.mkdir(parents=True, exist_ok=True)
        run([FFMPEG, "-y", "-f", "lavfi", "-i", f"aevalsrc='{BEAT}':s=48000:d=16",
             "-af", "aformat=channel_layouts=stereo,alimiter=limit=0.9,volume=0.9", str(ROOT / bgm)])
        made.append(bgm)
    if made:
        log("  · 임시 효과음/BGM 생성: " + ", ".join(made) + "  (같은 이름의 무료 음원으로 교체 가능)")


# ── 분석 ────────────────────────────────────────────────────────────
def probe_duration(path):
    p = run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(p.stdout.strip())


def read_pcm(path, sr=8000):
    p = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True)
    a = array.array("f")
    a.frombytes(p.stdout[: len(p.stdout) // 4 * 4])
    return a, sr


def detect_onsets(path, sr=8000, win=0.005, floor=0.02, ratio=3.0, refractory=0.08):
    """효과음 스템에서 '소리가 시작되는 순간'을 찾는다 (겹쳐도 잡히도록 에너지 급상승 기준)."""
    a, sr = read_pcm(path, sr)
    n = int(sr * win)
    env = [max((abs(x) for x in a[i:i + n]), default=0) for i in range(0, len(a), n)]
    onsets, last = [], -1e9
    for i, e in enumerate(env):
        prev = env[max(0, i - 6):max(0, i - 1)] or [0]
        t = i * win
        if e > floor and e > ratio * (sum(prev) / len(prev)) + 0.005 and t - last >= refractory:
            onsets.append(round(t, 3))
            last = t
    return onsets


def peak_between(path, t0, t1, sr=8000):
    a, sr = read_pcm(path, sr)
    seg = a[int(t0 * sr):int(t1 * sr)]
    return max((abs(x) for x in seg), default=0.0)


def speech_segments(voice_path, noise_db=-35, min_gap=0.2):
    """내레이션 파일의 말소리 구간 (공백 min_gap 이상에서 끊김)."""
    p = run([FFMPEG, "-i", str(voice_path), "-af", f"silencedetect=n={noise_db}dB:d={min_gap}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    total = probe_duration(voice_path)
    segs, cur = [], 0.0
    for s, e in zip(starts, ends + [total]):
        if s > cur + 0.05:
            segs.append((round(cur, 3), round(s, 3)))
        cur = e
    if cur < total - 0.05:
        segs.append((round(cur, 3), round(total, 3)))
    return segs
