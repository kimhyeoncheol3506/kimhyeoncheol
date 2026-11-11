---
name: comfyui-image
description: "현철님 PC의 ComfyUI(로컬 AI 이미지 생성, 127.0.0.1:8188)로 B-roll 장면 그림, 썸네일 배경, 챕터 표지, 쇼츠 배경 이미지를 만든다. 퍼블릭 도메인 그림이 없거나 제목 카드로 대체한 장면을 채울 때 쓴다. 'AI 이미지', 'ComfyUI', '그림 만들어', '썸네일 배경 생성', 'B-roll 이미지' 요청에 사용. PC 전용(그래픽카드 필요)."
---

# ComfyUI 내 PC AI 이미지

**PC 전용**이다. 클라우드 세션에는 그래픽카드와 모델이 없으므로 프롬프트·워크플로만 준비하고, 생성은 현철님 PC에서 한다(Voicebox와 같은 방식).

```bash
python .claude/skills/comfyui-image/scripts/comfy_gen.py "<영어 프롬프트>" --out <폴더> [--size 16:9|9:16|1:1] [--n 4] [--style econ|history|photo|none] [--seed 7]
```
- 서버 주소는 `COMFY_URL`(기본 `http://127.0.0.1:8188`), 모델 파일은 `--ckpt` 또는 `COMFY_CKPT`(기본 `sd_xl_base_1.0.safetensors`).
- 워크플로 기본값: `workflows/sdxl_txt2img.json`(SDXL 텍스트→이미지). 다른 워크플로는 ComfyUI에서 **Save (API Format)** 로 저장한 JSON의 값 자리에 `{{PROMPT}} {{NEG}} {{SEED}} {{W}} {{H}} {{CKPT}} {{STEPS}} {{CFG}} {{BATCH}} {{PREFIX}}`를 넣어 `--workflow`로 넘긴다(Flux 등).
- 결과마다 `comfy_<seed>.json`에 프롬프트·시드·모델을 남긴다(같은 그림 다시 만들기, 설명란 표기용).
- 연결이 안 되면 "ComfyUI를 먼저 켜 주세요"로 멈춘다. 클라우드에서 돌리면 당연히 이 메시지가 난다.

## 프롬프트 규칙
- **영어로 쓴다**(SDXL 계열은 한국어를 잘 못 알아듣는다). 대본 장면을 영어 한두 문장 + 스타일로.
- 스타일 프리셋: `econ`(규칙집 다크 배경 편집 일러스트), `history`(17~19세기 유화풍), `photo`(다큐 사진풍).
- 기본 네거티브에 글자·워터마크·로고·실존 인물 닮은꼴을 막는 단어가 들어 있다. 글자는 그림에 넣지 말고 neogul-edit 슬라이드·자막으로 얹는다.
- 크기: 16:9는 1344×768로 만든 뒤 `upscale-esrgan --scale 2`로 키워 1920×1080으로 자른다. 썸네일 배경도 같은 방식으로.

## 쓰지 말아야 할 것
- 실존 인물(정치인·CEO·연예인)의 얼굴, 다른 채널의 캐릭터(너굴경제 마스코트 포함), 회사 로고·상표.
- 역사 장면을 **실제 사진이나 기록처럼** 보이게 하는 것. AI 그림은 화면 구석에 작게 'AI 생성 이미지'라고 적고, 설명란에도 밝힌다.
- 숫자·차트를 AI 그림으로 만들지 않는다(틀린다). 숫자는 neogul-edit 슬라이드·Remotion·Manim으로.

## 파이프라인에 넣기
생성 → (필요하면) `upscale-esrgan` → 16:9로 자르기(ffmpeg-edit) → neogul-edit `broll`/`hook` 장면의 `media` 또는 썸네일 HTML 배경.
