"""실행: python -m finclose  (기본 127.0.0.1:8000)"""
import sys

import uvicorn

from .api import create_app
from .config import load_settings


def main() -> None:
    s = load_settings()
    if s.host not in ("127.0.0.1", "localhost"):
        print(f"[경고] {s.host}에 바인딩합니다. 인증이 없는 MVP이므로 신뢰된 사내망에서만 사용하세요.", file=sys.stderr)
    uvicorn.run(create_app(s), host=s.host, port=s.port, log_level="info")


if __name__ == "__main__":
    main()
