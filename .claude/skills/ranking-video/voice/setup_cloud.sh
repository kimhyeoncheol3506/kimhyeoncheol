#!/usr/bin/env bash
# 새 클라우드 세션에서 1회 실행: 음성 엔진(Qwen3-TTS) + 받아쓰기(Whisper) + 모델 준비. 약 10~15분.
#   bash shorts-studio/setup_cloud.sh            → 끝나면 TTS_PYTHON / QWEN_TTS_MODELS 경로 출력
set -euo pipefail
BASE="${TTS_HOME:-$HOME/.cache/shorts-tts}"
mkdir -p "$BASE"
pip install -q pillow numpy fonttools
if [ ! -x "$BASE/venv/bin/python" ]; then
  python3 -m venv "$BASE/venv"
  "$BASE/venv/bin/pip" install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu
  "$BASE/venv/bin/pip" install -q qwen-tts soundfile faster-whisper huggingface_hub
fi
for m in Base CustomVoice VoiceDesign; do
  d="$BASE/models/$(echo $m | tr 'A-Z' 'a-z' | sed 's/customvoice/custom/;s/voicedesign/design/')"
  [ -f "$d/config.json" ] || "$BASE/venv/bin/hf" download "Qwen/Qwen3-TTS-12Hz-1.7B-$m" --local-dir "$d" >/dev/null
done
echo "TTS_PYTHON=$BASE/venv/bin/python"
echo "QWEN_TTS_MODELS=$BASE/models"
