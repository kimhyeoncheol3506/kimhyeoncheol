"""대본(script.json) + 내레이션(timings.json) → 장면/자막 타임라인."""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .core import FPS, strip_markup

CHARS_PER_SEC = 6.8  # 아나운서 톤 한국어 평균 낭독 속도(공백 제외) - 음성 없을 때 추정용


@dataclass
class Chunk:
    text: str
    start: float
    end: float


@dataclass
class Scene:
    idx: int
    id: str
    data: dict
    start: float
    voice_start: float
    voice_end: float
    end: float
    chunks: list[Chunk] = field(default_factory=list)
    audio: Path | None = None

    @property
    def visual(self):
        return self.data.get("visual", {})

    def local(self, t):
        return t - self.start

    def chunk_at(self, t):
        for i, c in enumerate(self.chunks):
            if c.start <= t < c.end:
                return i, c
        if self.chunks and t >= self.chunks[-1].start:
            return len(self.chunks) - 1, self.chunks[-1]
        return -1, None


def estimate_duration(text: str) -> float:
    n = len(re.sub(r"\s", "", text))
    commas = text.count(",") + text.count("…") + text.count(".") + text.count("?")
    return n / CHARS_PER_SEC + commas * 0.18 + 0.2


VOICE_CHAIN = ",".join([
    # 문장 사이 긴 무음(0.3초↑)은 0.22초로 줄여 말 흐름을 사람처럼 촘촘하게
    "silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-42dB:stop_silence=0.22",
    "highpass=f=75",                                   # 저음 웅웅거림 제거
    "equalizer=f=220:t=q:w=1:g=1.5",                   # 가슴 울림(따뜻함)
    "equalizer=f=3200:t=q:w=1.2:g=2.5",                # 발음 또렷함(존재감)
    "acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=2",  # 방송용 컴프레션
])


def polish(wav: Path, speed: float = 1.0) -> Path:
    """방송 톤 후처리 + (선택) 음높이 유지 속도 조절. 결과는 narration/_tempo/ 에 캐시."""
    out = wav.parent / "_tempo" / f"{wav.stem}_p{speed:.2f}.wav"
    if not out.exists() or out.stat().st_mtime < wav.stat().st_mtime:
        out.parent.mkdir(exist_ok=True)
        af = VOICE_CHAIN + (f",atempo={speed}" if abs(speed - 1.0) > 1e-3 else "")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", af, str(out)])
    return out


def build(project_dir: Path, script: dict) -> tuple[list[Scene], float]:
    narr = project_dir / "narration"
    timings = {}
    tf = narr / "timings.json"
    if tf.exists():
        for row in json.loads(tf.read_text(encoding="utf-8")):
            timings[row["id"]] = row
    lead = script.get("lead_in", 0.15)
    gap = script.get("gap", 0.25)
    t = lead
    scenes = []
    for i, sd in enumerate(script["scenes"]):
        wav = narr / f"{sd['id']}.wav"
        speed = sd.get("speed", script.get("voice_speed", 1.0))
        if wav.exists():
            wav = polish(wav, speed)
        if wav.exists():
            from .audio import wav_duration
            vdur = wav_duration(wav)
            audio = wav
        else:
            vdur = estimate_duration(sd["say"])
            audio = None
        pre = sd.get("pause_before", 0.0)
        post = sd.get("pause_after", gap)
        start = t
        vs = start + pre
        ve = vs + vdur
        end = ve + post
        sc = Scene(i, sd["id"], sd, start, vs, ve, end, audio=audio)
        caps = sd.get("cap", [])
        if caps:
            weights = [max(2, len(strip_markup(c).replace(" ", ""))) for c in caps]
            tot = sum(weights)
            ct = vs
            for c, w in zip(caps, weights):
                d = vdur * w / tot
                sc.chunks.append(Chunk(c, ct, ct + d))
                ct += d
            sc.chunks[-1].end = end
        scenes.append(sc)
        t = end
    total = t + script.get("tail", 0.6)
    return scenes, total


def scene_at(scenes, t):
    for s in scenes:
        if s.start <= t < s.end:
            return s
    return scenes[-1]


class FrameWriter:
    """RGB 프레임을 ffmpeg로 파이프 → mp4 (+오디오 mux)."""

    def __init__(self, path: Path, size, audio: Path | None, fps=FPS, crf=18):
        w, h = size
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
               "-r", str(fps), "-i", "-"]
        if audio:
            cmd += ["-i", str(audio)]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
                "-movflags", "+faststart"]
        if audio:
            cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",  # 유튜브 표준 음량
                    "-c:a", "aac", "-b:a", "192k", "-shortest"]
        cmd += [str(path)]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def write(self, img):
        self.p.stdin.write(img.convert("RGB").tobytes())

    def close(self):
        self.p.stdin.close()
        if self.p.wait() != 0:
            raise RuntimeError("ffmpeg failed")
