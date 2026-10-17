"""공통 헬퍼: 콘솔 출력, ffmpeg 실행, 길이 측정, 시간 포맷."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console

from config import ffmpeg_bin

console = Console()


def run_ffmpeg(args: list[str], *, quiet: bool = True) -> None:
    """ffmpeg 를 실행하고 실패하면 stderr 마지막 부분을 보여 준다."""
    cmd = [ffmpeg_bin(), "-hide_banner", "-y"]
    if quiet:
        cmd += ["-loglevel", "error"]
    cmd += [str(a) for a in args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
        raise RuntimeError(f"ffmpeg 실패 (code {proc.returncode})\n$ {' '.join(cmd)}\n{tail}")


_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")


def media_duration(path: str | Path) -> float:
    """미디어 길이(초). ffprobe 가 없어도 되도록 `ffmpeg -i` 출력에서 읽는다."""
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-i", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    m = _DURATION_RE.search(proc.stderr)
    if not m:
        raise RuntimeError(f"길이를 읽을 수 없습니다: {path}")
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def has_audio_stream(path: str | Path) -> bool:
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-i", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return "Audio:" in proc.stderr


def fmt_hms(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def parse_hms(value: str | float | int) -> float:
    """'1:23', '01:02:03.5', 83 → 초."""
    if isinstance(value, (int, float)):
        return float(value)
    parts = [float(p) for p in str(value).strip().split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def slugify(text: str, max_len: int = 40) -> str:
    text = re.sub(r"[^\w가-힣\-]+", "_", text, flags=re.UNICODE).strip("_")
    return text[:max_len] or "untitled"


def human_count(n: int | None) -> str:
    if n is None:
        return "?"
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}억"
    if n >= 10_000:
        return f"{n / 10_000:.1f}만"
    return f"{n:,}"


def save_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


_SIZE_RE = re.compile(r"Video:.*?\b(\d{2,5})x(\d{2,5})\b")


def video_size(path: str | Path) -> tuple[int, int]:
    """(가로, 세로) 픽셀. 회전 메타데이터가 있는 세로 영상도 고려."""
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-i", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    m = _SIZE_RE.search(proc.stderr)
    if not m:
        raise RuntimeError(f"해상도를 읽을 수 없습니다: {path}")
    w, h = int(m.group(1)), int(m.group(2))
    if re.search(r"rotation of -?90|rotate\s*:\s*-?90|displaymatrix: rotation of -?90", proc.stderr):
        w, h = h, w
    return w, h
