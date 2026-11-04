#!/usr/bin/env bash
# ComfyUI(Comfy-Org/ComfyUI) 설치 + 서버 실행. 클라우드 컨테이너는 CPU뿐이라 느림, PC(GPU)에서는 그대로 빠르게 돈다.
# 여의도남자 TTS venv에 이미 있는 torch를 재사용해 디스크를 아낀다(없으면 CPU torch를 새로 설치).
set -e
EXT=/home/user/ext
mkdir -p "$EXT" && cd "$EXT"
[ -d ComfyUI ] || git clone -q --depth 1 https://github.com/Comfy-Org/ComfyUI.git
if [ ! -x comfy-venv/bin/python ]; then
  TTS=~/.cache/yeouido-tts/venv/bin/python
  if [ -x "$TTS" ]; then
    "$TTS" -m venv comfy-venv
    "$TTS" -c "import site;print(site.getsitepackages()[0])" > comfy-venv/lib/python3.13/site-packages/_tts_torch.pth
  else
    python3 -m venv comfy-venv
    comfy-venv/bin/pip install -q --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
  fi
  comfy-venv/bin/pip install -q --no-cache-dir --no-deps torchvision --index-url https://download.pytorch.org/whl/cpu
  grep -v -E "^(torch|torchvision)$|^#|^$" ComfyUI/requirements.txt > /tmp/comfy-req.txt
  comfy-venv/bin/pip install -q --no-cache-dir -r /tmp/comfy-req.txt
fi
if ! curl -s -m 2 http://127.0.0.1:8188/system_stats >/dev/null; then
  nohup comfy-venv/bin/python ComfyUI/main.py --cpu --listen 127.0.0.1 --port 8188 > "$EXT/comfy.log" 2>&1 &
  for i in $(seq 1 60); do curl -s -m 2 http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 3; done
fi
curl -s -m 2 http://127.0.0.1:8188/system_stats >/dev/null && echo "ComfyUI 실행 중: http://127.0.0.1:8188"
