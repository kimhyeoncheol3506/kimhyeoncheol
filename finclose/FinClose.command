#!/usr/bin/env bash
# macOS: Finder에서 더블클릭하면 FinClose 데스크톱 앱 실행(소스 버전, Python 3.11+ 필요). 연습 모드: ./FinClose.command --demo
cd "$(dirname "$0")"
if [ ! -x backend/.venv/bin/python ]; then
  echo "처음 실행 준비 중입니다..."
  python3 -m venv backend/.venv && backend/.venv/bin/pip install -q -r backend/requirements.txt || { echo "Python 3.11 이상이 필요합니다."; read -r; exit 1; }
fi
cd backend && exec .venv/bin/python -m finclose.desktop "$@"
