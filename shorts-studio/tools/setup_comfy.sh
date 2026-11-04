#!/usr/bin/env bash
# ComfyUI(CPU) + DreamShaper 8 + LCM LoRA 설치 — 장면 삽화용 (tools/illust.py)
# 사용: bash tools/setup_comfy.sh <설치폴더>   (컨테이너가 새로 뜨면 한 번 실행, 약 5GB)
set -e
D=${1:?설치 폴더}
mkdir -p "$D"; cd "$D"
[ -d comfy ] || git clone -q --depth 1 https://github.com/Comfy-Org/ComfyUI comfy
[ -x comfyenv/bin/python ] || python3 -m venv comfyenv
comfyenv/bin/pip -q install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
comfyenv/bin/pip -q install -r comfy/requirements.txt
rm -rf ~/.cache/pip
M=comfy/models
[ -s $M/checkpoints/dreamshaper_8.safetensors ] || curl -sSL -o $M/checkpoints/dreamshaper_8.safetensors \
  https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors
[ -s $M/loras/lcm_sd15.safetensors ] || curl -sSL -o $M/loras/lcm_sd15.safetensors \
  https://huggingface.co/latent-consistency/lcm-lora-sdv1-5/resolve/main/pytorch_lora_weights.safetensors
echo "완료: COMFY_DIR=$D/comfy COMFY_PY=$D/comfyenv/bin/python python3 tools/illust.py projects/X"
