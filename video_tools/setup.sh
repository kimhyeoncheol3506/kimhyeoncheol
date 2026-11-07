#!/usr/bin/env bash
# 영상 도구 준비(새 세션에서 1회). ranking-video v2.14.0
#  - Remotion: video_tools/remotion_test 의 npm 의존성
#  - Manim: pango 개발 헤더(apt) + ~/.cache/manim-venv
#  - HyperFrames: npx hyperframes@0.8.214 (설치 불필요)
set -e
cd "$(dirname "$0")"
(cd remotion_test && npm install --no-audit --no-fund)
command -v pkg-config >/dev/null && pkg-config --exists pangocairo || (apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libpango1.0-dev pkg-config)
[ -x ~/.cache/manim-venv/bin/manim ] || (python3 -m venv ~/.cache/manim-venv && ~/.cache/manim-venv/bin/pip install -q manim)
echo "준비 완료: remotion $(cd remotion_test && npx remotion --version 2>/dev/null | tail -1) / $(~/.cache/manim-venv/bin/python -c 'import manim;print("manim",manim.__version__)')"
