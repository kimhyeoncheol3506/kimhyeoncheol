"""설정. 모든 값은 환경변수로 재정의할 수 있으며 비밀정보는 저장하지 않는다."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))  # PyInstaller로 묶인 데스크톱 앱
# 화면(frontend/dist)·연습 자료(sample_data)가 있는 위치. 데스크톱 앱에서는 압축이 풀린 번들 폴더.
BASE_DIR = Path(getattr(sys, "_MEIPASS", "")) if FROZEN else Path(__file__).resolve().parent.parent.parent


def user_home_dir() -> Path:
    """데스크톱 앱의 사용자 폴더: 문서/FinClose (앱을 업데이트해도 데이터가 유지되는 위치)."""
    docs = Path.home() / "Documents"
    return (docs if docs.is_dir() else Path.home()) / "FinClose"


def default_data_dir() -> Path:
    return user_home_dir() / "data" if FROZEN else BASE_DIR / "data"


@dataclass
class Settings:
    data_dir: Path
    max_upload_mb: int
    max_rows: int
    min_free_disk_mb: int
    host: str
    port: int

    @property
    def db_path(self) -> Path:
        return self.data_dir / "finclose.db"

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def runs_dir(self) -> Path:
        return self.data_dir / "runs"

    def ensure_dirs(self) -> None:
        for p in (self.data_dir, self.upload_dir, self.runs_dir):
            p.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    return Settings(
        data_dir=Path(os.environ.get("FINCLOSE_DATA_DIR") or default_data_dir()).resolve(),
        max_upload_mb=int(os.environ.get("FINCLOSE_MAX_UPLOAD_MB", "50")),
        max_rows=int(os.environ.get("FINCLOSE_MAX_ROWS", "200000")),
        min_free_disk_mb=int(os.environ.get("FINCLOSE_MIN_FREE_DISK_MB", "200")),
        host=os.environ.get("FINCLOSE_HOST", "127.0.0.1"),
        port=int(os.environ.get("FINCLOSE_PORT", "8000")),
    )
