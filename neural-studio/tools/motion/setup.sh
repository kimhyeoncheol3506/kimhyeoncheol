#!/bin/bash
# 새 컨테이너에서 영상 보조 도구 다시 깔기(2026-11-07). 저장소 루트에서: bash tools/motion/setup.sh
# - Manim: 시스템 파이썬을 건드리지 않게 /root/.cache/manim-venv 에. 공식(MathTex)용 최소 LaTeX 포함.
# - Remotion·HyperFrames: tools/motion/node_modules (git 에 올리지 않음)
set -e
cd "$(dirname "$0")"
if ! /root/.cache/manim-venv/bin/manim --version >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libpango1.0-dev libcairo2-dev pkg-config python3-dev build-essential \
    texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended dvisvgm >/dev/null
  python3 -m venv /root/.cache/manim-venv
  /root/.cache/manim-venv/bin/pip install -q manim
fi
[ -d node_modules/remotion ] || DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 npm install --no-fund --no-audit
mkdir -p hyperframes/fonts && cp -n ../../assets/fonts/Pretendard-Black.otf hyperframes/fonts/ 2>/dev/null || true
/root/.cache/manim-venv/bin/manim --version; npx --no-install remotion versions | tail -1; npx --no-install hyperframes --version
