"""설정. 모든 값은 환경변수로 재정의할 수 있으며 비밀정보는 저장하지 않는다."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # finclose/


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
        data_dir=Path(os.environ.get("FINCLOSE_DATA_DIR", BASE_DIR / "data")).resolve(),
        max_upload_mb=int(os.environ.get("FINCLOSE_MAX_UPLOAD_MB", "50")),
        max_rows=int(os.environ.get("FINCLOSE_MAX_ROWS", "200000")),
        min_free_disk_mb=int(os.environ.get("FINCLOSE_MIN_FREE_DISK_MB", "200")),
        host=os.environ.get("FINCLOSE_HOST", "127.0.0.1"),
        port=int(os.environ.get("FINCLOSE_PORT", "8000")),
    )
