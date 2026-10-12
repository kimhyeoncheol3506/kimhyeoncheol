#!/usr/bin/env bash
# FinClose AI 로컬 실행 (macOS/Linux)
#   ./run.sh          설치(최초 1회) 후 서버 실행 → http://127.0.0.1:8000
#   ./run.sh test     백엔드·프런트엔드 테스트
#   ./run.sh demo     시연용 과거 이력 생성 후 실행
#   ./run.sh desktop  데스크톱 앱 창으로 실행(창을 닫으면 종료)
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
PY="${PYTHON:-python3}"

if [ ! -x backend/.venv/bin/python ]; then
  echo "[1/3] Python 가상환경 생성 및 패키지 설치"
  "$PY" -m venv backend/.venv
  backend/.venv/bin/pip install -q --upgrade pip
  backend/.venv/bin/pip install -q -r backend/requirements-dev.txt
fi

if command -v npm >/dev/null 2>&1; then
  if [ ! -d frontend/node_modules ]; then
    echo "[2/3] 프런트엔드 패키지 설치"
    (cd frontend && npm install --no-audit --no-fund)
  fi
  if [ "${1:-}" != "test" ]; then
    echo "[2/3] 프런트엔드 빌드"
    (cd frontend && npm run build >/dev/null)
  fi
elif [ ! -d frontend/dist ]; then
  echo "Node.js(npm)가 없고 빌드된 화면(frontend/dist)도 없습니다. Node.js 18+를 설치하세요." >&2
  exit 1
else
  echo "[2/3] Node.js 없음 — 동봉된 빌드 화면(frontend/dist) 사용"
fi

cd backend
case "${1:-}" in
  test)
    .venv/bin/python -m pytest
    if command -v npm >/dev/null 2>&1; then (cd "$ROOT/frontend" && npm test); fi
    exit 0 ;;
  demo)
    .venv/bin/python -m finclose.seed_demo ;;
  desktop)
    exec .venv/bin/python -m finclose.desktop "${@:2}" ;;
esac
echo "[3/3] 서버 시작: http://${FINCLOSE_HOST:-127.0.0.1}:${FINCLOSE_PORT:-8000}  (종료: Ctrl+C)"
exec .venv/bin/python -m finclose
