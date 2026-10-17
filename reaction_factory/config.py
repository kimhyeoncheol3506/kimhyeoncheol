"""환경 변수(.env)와 폴더 경로를 한 곳에서 관리한다."""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

INPUT_DIR = ROOT / "input_source"   # 원본 영상/자막/썸네일
SCRIPT_DIR = ROOT / "scripts"       # 생성된 대본 JSON
AUDIO_DIR = ROOT / "audio"          # TTS mp3 + 자막
OUTPUT_DIR = ROOT / "output"        # 최종 mp4
DATA_DIR = ROOT / "data"            # 주제 데이터셋
ASSET_DIR = ROOT / "assets"
FONT_DIR = ASSET_DIR / "fonts"
BGM_DIR = ASSET_DIR / "bgm"

for _d in (INPUT_DIR, SCRIPT_DIR, AUDIO_DIR, OUTPUT_DIR, DATA_DIR, FONT_DIR, BGM_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _float(name: str, default: float) -> float:
    try:
        return float(_env(name, str(default)))
    except ValueError:
        return default


@dataclass
class Settings:
    anthropic_api_key: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    claude_model: str = field(default_factory=lambda: _env("CLAUDE_MODEL", "claude-opus-5-5"))
    claude_effort: str = field(default_factory=lambda: _env("CLAUDE_EFFORT", "high"))

    youtube_api_key: str = field(default_factory=lambda: _env("YOUTUBE_API_KEY"))

    tts_provider: str = field(default_factory=lambda: _env("TTS_PROVIDER", "edge").lower())
    edge_voice: str = field(default_factory=lambda: _env("EDGE_VOICE", "ko-KR-InJoonNeural"))
    edge_rate: str = field(default_factory=lambda: _env("EDGE_RATE", "+8%"))
    elevenlabs_api_key: str = field(default_factory=lambda: _env("ELEVENLABS_API_KEY"))
    elevenlabs_voice_id: str = field(default_factory=lambda: _env("ELEVENLABS_VOICE_ID"))
    elevenlabs_model: str = field(default_factory=lambda: _env("ELEVENLABS_MODEL", "eleven_multilingual_v2"))
    typecast_api_key: str = field(default_factory=lambda: _env("TYPECAST_API_KEY"))
    typecast_voice_id: str = field(default_factory=lambda: _env("TYPECAST_VOICE_ID"))
    typecast_model: str = field(default_factory=lambda: _env("TYPECAST_MODEL", "ssfm-v21"))
    clova_client_id: str = field(default_factory=lambda: _env("CLOVA_CLIENT_ID"))
    clova_client_secret: str = field(default_factory=lambda: _env("CLOVA_CLIENT_SECRET"))
    clova_speaker: str = field(default_factory=lambda: _env("CLOVA_SPEAKER", "nminsang"))

    subtitle_font: str = field(default_factory=lambda: _env("SUBTITLE_FONT", "Noto Sans CJK KR"))
    source_duck_volume: float = field(default_factory=lambda: _float("SOURCE_DUCK_VOLUME", 0.12))
    bgm_file: str = field(default_factory=lambda: _env("BGM_FILE"))
    bgm_volume: float = field(default_factory=lambda: _float("BGM_VOLUME", 0.08))
    ffmpeg_path: str = field(default_factory=lambda: _env("FFMPEG_PATH"))


settings = Settings()


def ffmpeg_bin() -> str:
    """ffmpeg 실행 파일 경로: .env 지정 > 시스템 PATH > imageio-ffmpeg 내장 바이너리."""
    if settings.ffmpeg_path:
        return settings.ffmpeg_path
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover - 설치 환경 문제
        raise RuntimeError(
            "ffmpeg 를 찾을 수 없습니다. `pip install imageio-ffmpeg` 하거나 ffmpeg 를 설치하세요."
        ) from exc
