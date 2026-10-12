#!/usr/bin/env bash
# 클라우드 세션에서 1회 실행: 여의도 목소리 엔진(Qwen3-TTS, Voicebox와 같은 엔진) + 모델 준비. 약 10~15분.
# 여의도남자 = Base 모델 + 기준음성 복제, 여의도여자 = CustomVoice 프리셋 Sohee (yeouido-voice 규격과 동일)
set -euo pipefail
BASE="${TTS_HOME:-$HOME/.cache/yeouido-tts}"
mkdir -p "$BASE"
if [ ! -x "$BASE/venv/bin/python" ]; then
  python3 -m venv "$BASE/venv"
  "$BASE/venv/bin/pip" install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu
  "$BASE/venv/bin/pip" install -q qwen-tts soundfile numpy huggingface_hub
fi
for m in Base CustomVoice; do
  d="$BASE/models/$(echo $m | tr 'A-Z' 'a-z' | sed 's/customvoice/custom/')"
  [ -f "$d/config.json" ] || "$BASE/venv/bin/hf" download "Qwen/Qwen3-TTS-12Hz-1.7B-$m" --local-dir "$d" >/dev/null
done
echo "TTS_PYTHON=$BASE/venv/bin/python"
echo "QWEN_TTS_MODELS=$BASE/models"
