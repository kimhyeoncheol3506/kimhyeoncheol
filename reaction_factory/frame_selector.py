"""AI 이미지 선택: 장면 전환 기반 후보 프레임 추출 → Claude 비전으로 장면 설명·점수 매기기.

- 균등 간격만 쓰던 대표 프레임 대신, 화면이 크게 바뀌는 순간(scene change)을 우선 후보로 뽑는다.
- Claude 가 각 프레임을 보고 '무슨 장면인지 / 반응 강도 / 썸네일 적합도 / 흔들림·자막 가림' 을 평가한다.
- 이 카탈로그가 대본 프롬프트에 들어가서, Claude 가 나레이션 내용에 맞는 사진을 고르고
  편집기는 썸네일과 '빈 구간 채우기'(같은 장면 반복 대신 다른 사진 삽입)에 쓴다.
"""
from __future__ import annotations

import base64
import re
import subprocess
from pathlib import Path

import anthropic
from pydantic import BaseModel, Field

from config import ffmpeg_bin, settings
from utils import console, load_json, media_duration, run_ffmpeg, save_json


# ─────────────────────────── 후보 추출 ───────────────────────────
def scene_change_times(video: Path, threshold: float = 0.32) -> list[float]:
    """ffmpeg scene 점수로 화면 전환 시각 목록."""
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-i", str(video), "-vf",
         f"scale=320:-2,select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return [float(t) for t in re.findall(r"pts_time:([\d.]+)", proc.stderr)]


def pick_times(duration: float, scenes: list[float], count: int, min_gap: float = 2.5) -> list[float]:
    """장면 전환 시각(+0.4초, 전환 직후 흐림 회피)과 균등 간격을 섞어 count 개를 고른다."""
    lo, hi = duration * 0.03, duration * 0.97
    uniform = [duration * (0.05 + 0.9 * (i + 0.5) / count) for i in range(count)]
    chosen: list[float] = []
    for t in [s + 0.4 for s in scenes if lo <= s + 0.4 <= hi] + uniform:
        if all(abs(t - c) >= min_gap for c in chosen):
            chosen.append(t)
    if len(chosen) > count:  # 장면이 너무 많으면 전체 구간에 고르게 솎아낸다
        chosen.sort()
        step = len(chosen) / count
        chosen = [chosen[int(i * step)] for i in range(count)]
    return sorted(chosen[:count])


def extract_frames(video: Path, out_dir: Path, *, count: int = 20, duration: float | None = None) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("frame_*.jpg"):
        old.unlink()
    duration = duration or media_duration(video)
    times = pick_times(duration, scene_change_times(video), count)
    paths = []
    for i, t in enumerate(times):
        p = out_dir / f"frame_{i:02d}_{t:.1f}s.jpg"
        run_ffmpeg(["-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-q:v", "2", p])
        paths.append(p)
    return paths


def frame_time(path: Path) -> float:
    m = re.search(r"_([\d.]+)s\.jpg$", path.name)
    return float(m.group(1)) if m else 0.0


def list_frames(folder: Path) -> list[Path]:
    return sorted((folder / "frames").glob("frame_*.jpg"))


# ─────────────────────────── Claude 비전 분석 ───────────────────────────
class FrameInfo(BaseModel):
    index: int
    description: str = Field(description="장면 설명(한국어 한 문장, 누가 무엇을 하고 있는지)")
    reaction: int = Field(description="인물 반응·감정 강도 0~10 (놀람, 웃음, 감탄 등)")
    thumbnail_score: int = Field(description="썸네일 적합도 0~10 (표정이 크게 보이고 선명하며 한눈에 상황이 읽힘)")
    usable: bool = Field(description="흐림·암전·전환 중·원본 자막/로고가 화면을 크게 가리면 false")


class FrameCatalog(BaseModel):
    frames: list[FrameInfo]


def _thumb_b64(path: Path, width: int = 512) -> str:
    small = path.with_suffix(".small.jpg")
    run_ffmpeg(["-i", path, "-vf", f"scale={width}:-2", "-q:v", "5", small])
    data = base64.standard_b64encode(small.read_bytes()).decode()
    small.unlink(missing_ok=True)
    return data


def analyze_frames(folder: Path, context: str = "") -> list[dict]:
    """frames/ 의 사진들을 Claude 로 평가해서 frames.json 에 저장. 키가 없으면 시각 정보만 저장."""
    frames = list_frames(folder)
    catalog = [{"index": i, "time": frame_time(p), "file": p.name, "description": "", "reaction": 5,
                "thumbnail_score": 5, "usable": True} for i, p in enumerate(frames)]
    if not frames or not settings.anthropic_api_key:
        save_json(folder / "frames.json", catalog)
        return catalog

    content: list[dict] = []
    for i, p in enumerate(frames):
        content.append({"type": "text", "text": f"[프레임 {i}] {frame_time(p):.1f}초"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                    "data": _thumb_b64(p)}})
    content.append({"type": "text", "text": (
        f"해외반응 영상의 후보 프레임 {len(frames)}장입니다. {context}\n"
        "각 프레임을 평가해 frames 배열로 돌려주세요(index 는 위 번호 그대로).")})

    console.print(f"[bold]AI 이미지 선택[/] 프레임 {len(frames)}장 분석 …")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    try:
        resp = client.beta.messages.parse(
            model=settings.claude_model,
            max_tokens=16000,
            messages=[{"role": "user", "content": content}],
            output_format=FrameCatalog,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        parsed = resp.parsed_output if resp.stop_reason != "refusal" else None
    except anthropic.APIError as exc:
        console.print(f"[yellow]프레임 분석 실패(균등 점수로 진행): {exc}[/]")
        parsed = None
    if parsed:
        for f in parsed.frames:
            if 0 <= f.index < len(catalog):
                catalog[f.index].update(description=f.description, reaction=f.reaction,
                                        thumbnail_score=f.thumbnail_score, usable=f.usable)
    save_json(folder / "frames.json", catalog)
    return catalog


def load_catalog(folder: Path) -> list[dict]:
    path = folder / "frames.json"
    if path.exists():
        return load_json(path)
    return [{"index": i, "time": frame_time(p), "file": p.name, "description": "", "reaction": 5,
             "thumbnail_score": 5, "usable": True} for i, p in enumerate(list_frames(folder))]


def best_thumbnail(folder: Path) -> Path | None:
    frames = list_frames(folder)
    cat = [c for c in load_catalog(folder) if c["usable"] and c["index"] < len(frames)]
    if not cat:
        return frames[0] if frames else None
    best = max(cat, key=lambda c: (c["thumbnail_score"], c["reaction"]))
    return frames[best["index"]]
