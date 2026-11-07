#!/usr/bin/env bash
# Manim Community 설치 (공식·그래프 설명 장면용). venv: /home/user/ext/manim-venv (~480MB). LaTeX는 설치하지 않음 → MathTex 대신 Text 사용.
set -e
pkg-config --exists pangocairo || { apt-get update -q && apt-get install -y -q libpango1.0-dev python3-dev; }
[ -x /home/user/ext/manim-venv/bin/manim ] || { python3 -m venv /home/user/ext/manim-venv && /home/user/ext/manim-venv/bin/pip install -q --no-cache-dir manim; }
/home/user/ext/manim-venv/bin/python -c "import manim;print('manim', manim.__version__)"
# 테스트: cd /home/user/ext/manim-test && /home/user/ext/manim-venv/bin/manim -qm --fps 30 <scene.py> <Scene>
