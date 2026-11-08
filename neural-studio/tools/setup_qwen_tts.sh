#!/usr/bin/env bash
# 클라우드(또는 Voicebox 없는 컴퓨터)에서 여의도여자 음성을 직접 만들 준비. 1회, 약 10~15분, 디스크 약 5GB.
#   bash tools/setup_qwen_tts.sh   → ~/.cache/qwen-tts/venv + models/custom (Qwen3-TTS-12Hz-1.7B-CustomVoice)
set -euo pipefail
B="${QWEN_TTS_HOME:-$HOME/.cache/qwen-tts}"
mkdir -p "$B"
[ -x "$B/venv/bin/python" ] || python3 -m venv "$B/venv"
"$B/venv/bin/python" -c "import torch" 2>/dev/null || "$B/venv/bin/pip" install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu
"$B/venv/bin/python" -c "import qwen_tts" 2>/dev/null || "$B/venv/bin/pip" install -q qwen-tts soundfile huggingface_hub
[ -f "$B/models/custom/config.json" ] || "$B/venv/bin/hf" download Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --local-dir "$B/models/custom" >/dev/null
echo "준비 끝: $B/venv/bin/python , $B/models/custom"
