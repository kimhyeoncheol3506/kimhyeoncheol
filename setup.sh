#!/usr/bin/env bash
# facetube 실행 환경 설치. 여러 번 실행해도 안전.
set -e
cd "$(dirname "$0")"
M="${FACETUBE_MODELS:-$HOME/.cache/facetube/models}"
mkdir -p "$M"

command -v ffmpeg >/dev/null || (apt-get update -q && apt-get install -y -q ffmpeg)
command -v tesseract >/dev/null && tesseract --list-langs 2>/dev/null | grep -q kor || \
  (apt-get install -y -q tesseract-ocr tesseract-ocr-kor || (apt-get update -q && apt-get install -y -q tesseract-ocr tesseract-ocr-kor))

pip install -q -r requirements.txt

GH=https://github.com/k2-fsa/sherpa-onnx/releases/download
if [ ! -d "$M/vits-mimic3-ko_KO-kss_low" ]; then
  echo "한국어 오프라인 음성 모델 받는 중…"
  curl -sL "$GH/tts-models/vits-mimic3-ko_KO-kss_low.tar.bz2" | tar xj -C "$M"
fi
if [ ! -d "$M/sherpa-onnx-zipformer-korean-2024-06-24" ]; then
  echo "한국어 음성인식(검수용) 모델 받는 중… (약 330MB)"
  curl -sL "$GH/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2" | tar xj -C "$M"
fi
echo "준비 완료"
