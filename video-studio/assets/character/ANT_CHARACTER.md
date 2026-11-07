# 여의도 개미 캐릭터 설정 (34편~, 2026-11-07 현철님 지정)

## 1. 코드 마스코트 (숫자·도표 장면, 채널 배지, 썸네일 구석)
- `HF_CHAR=chibi` → `hf_story.fig_chibi`
- 2등신으로, 머리가 크고 몸이 작다.
- **머리 외곽선이 두껍다** (11px).
- 더듬이는 굵고 끝에 공이 달려 있다. 볼에 분홍 볼터치가 있다.
- 흰 몸통에 주황 V 칼라와 금빛 단추 2개가 있다.
- 감정 8종: 기본·기쁨·놀람·걱정·화남·생각·슬픔·자신감 (`mouth`·`brows`·`pose` 조합).

## 2. AI 일러스트 캐릭터 (상황 장면, 반실사 웹툰풍)
- 고정 프롬프트(영문). 모든 장면에 앞에 붙인다:
  `semi-realistic korean webtoon illustration, cute short young korean office worker man, late 20s, round friendly face, short black hair, big expressive eyes, two thin black ant antennae with round tips on top of head, white shirt with small orange collar, navy cardigan, soft cinematic lighting, detailed background, 16:9`
- 부정 프롬프트:
  `text, letters, watermark, logo, real celebrity, photo of real person, extra fingers, deformed hands, blurry, lowres`
- 캐릭터 시트를 먼저 만든다. 정면·측면 각 1장, 감정 8종(기본·기쁨·놀람·걱정·화남·생각·슬픔·자신감)이다.
  - 가장 잘 나온 정면 1장을 `assets/character/ant_ref.png`로 저장한다.
  - 이후 모든 장면은 IPAdapter 기준 이미지로 이 파일을 써서 같은 얼굴을 유지한다.
- 실존 인물(정치인·기업인·연예인)은 그리지 않는다. 필요하면 "가상의 회사 대표" 같은 익명 인물로 그린다.
- 그림 안에 글자를 넣지 않는다. 글자는 말풍선·라벨로 영상에서 얹는다(`illust` 장면).
