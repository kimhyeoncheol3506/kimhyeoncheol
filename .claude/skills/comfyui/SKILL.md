---
name: comfyui
description: ComfyUI(Comfy-Org/ComfyUI, 노드형 확산 모델 GUI·API)로 영상에 쓸 그림(배경, 장면 일러스트, 썸네일 바탕)을 만든다. "ComfyUI로 그려줘", "컴피로 배경 만들어줘", ComfyUI 워크플로(json)를 주며 돌려 달라고 할 때 사용.
---

# ComfyUI

설치 위치는 `/home/user/ext/ComfyUI`, venv는 `/home/user/ext/comfy-venv`입니다. 이 venv는 여의도남자 TTS의 torch를 같이 씁니다. TTS venv는 건드리지 않습니다.

## 켜기
`bash video-studio/setup_comfyui.sh`를 실행합니다. 설치가 안 되어 있으면 설치하고, 서버를 `127.0.0.1:8188`에서 켭니다. 컨테이너가 다시 시작되면 다시 실행합니다.

## 쓰기 (`video-studio/tools/comfy_client.py`)
- `status`: 버전, 장치, 주소를 보여 줍니다.
- `models`: 체크포인트 목록을 보여 줍니다.
- `txt2img "<영어 프롬프트>" out.png --w 1920 --h 1080 --steps 20 --seed 1 [--ckpt 이름]`: 프롬프트로 그림을 만듭니다.
- `run workflow_api.json out_dir`: ComfyUI 화면에서 Export (API)로 저장한 워크플로를 그대로 돌립니다.
- `selftest out.png`: 모델 없이 API 왕복만 확인합니다.
- `COMFY_URL=http://<PC주소>:8188`을 주면 현철님 PC(GPU)에서 켠 ComfyUI로 같은 명령이 돕니다. PC에서는 `--listen 0.0.0.0`으로 켜야 합니다.

## 주의
- 클라우드 컨테이너에는 GPU가 없습니다. SD1.5 512px 그림 한 장에 몇 분이 걸리고, SDXL은 사실상 안 됩니다. 많이 그릴 때는 PC에서 돌립니다.
- 체크포인트(.safetensors)는 `ComfyUI/models/checkpoints/`에 넣습니다. 상업 이용이 가능한 라이선스만 씁니다. 출처는 설명란에 적습니다.
- 디스크가 부족합니다(세션 허용량 약 2GB 남음). 2GB가 넘는 모델은 넣기 전에 캐시(`~/.cache/uv`, `~/.cache/pip`)를 먼저 비웁니다.
- 고정 규칙은 그대로 지킵니다. 여의도 개미 캐릭터와 여의도남자 목소리를 쓰고, 썸네일 글자와 폰트는 바꾸지 않습니다. ComfyUI는 배경, 소품, 분위기 그림에만 씁니다. 썸네일 글자는 기존 make_thumb.py로 얹습니다.
- 만든 그림은 `clip` 장면이나 HF 장면 배경(`assets/`)으로 넣습니다.
