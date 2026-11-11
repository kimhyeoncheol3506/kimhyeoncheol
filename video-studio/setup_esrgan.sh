#!/usr/bin/env bash
# Real-ESRGAN(CPU) 설치: torch CPU + spandrel + 가중치 2개 → /home/user/ext 아래 (저장소 밖, 약 1GB)
# 사용: bash setup_esrgan.sh  → /home/user/ext/esrgan-venv/bin/python tools/upscale.py <파일>
set -e
E=/home/user/ext; mkdir -p $E/esrgan-models
[ -x $E/esrgan-venv/bin/python ] || python3 -m venv $E/esrgan-venv
V=$E/esrgan-venv/bin
$V/pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cpu   # torchvision 도 CPU판이어야 함(PyPI판은 nms 오류)
$V/pip install -q spandrel pillow numpy
cd $E/esrgan-models
[ -s RealESRGAN_x4plus.pth ] || curl -sSL -o RealESRGAN_x4plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
[ -s RealESRGAN_x4plus_anime_6B.pth ] || curl -sSL -o RealESRGAN_x4plus_anime_6B.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth
echo "Real-ESRGAN 준비 완료"
