---
name: econ-motion-video
description: 현철님이 경제 대본(텍스트)을 주면 HyperFrames 모션그래픽 중심의 롱폼 영상 1세트(영상+썸네일+제목·설명·태그+자막)를 만드는 검증된 절차. 26편 "진짜 위기는 이때 온다"(17분 54초, 195장면, Spotlight 마이크로피시 룩)에서 현철님이 "아주 만족"이라고 확정한 방식 그대로. 대본을 주며 "모션그래프 많이", "hyperframe", "lemo-opuscar 스타일"로 영상 제작을 요청할 때 사용.
---

# 경제 대본 → 모션그래픽 롱폼 (26편에서 확정된 방식)

기준 구현: `video-studio/projects/20261029-real-crisis/` (build.py, make_thumb.py, TREATMENT.md, CREDITS), 장면 생성기 `video-studio/tools/hf_econ.py`. 엔진·규칙은 `econ-video` 스킬을 따른다(버전 확인, 파일명 `제목_v버전_종류`, 제작일지, 목소리 규칙).

## 고정 요소
- 목소리 = 여의도남자(Qwen3-TTS 복제, 롱폼 1.08배). 인물 = 여의도 개미(감정 장면에만 등장, 포즈 48종 PNG로 내보내 HyperFrames에 배치).
- 화면 = 전부 HyperFrames 모션그래픽(`hf_econ.py` 14종: title·kpi·quote·qa·chart·dual·flow·loop·compare·check·scale·timeline·hub·signal). 그래프는 항상 "개념도 · 실제 수치 아님" 배지.
- 룩 = lemo-opuscar OPUSCAR 98 No.88 Spotlight (환경변수 `HF_LOOK=fiche`, build.py가 기본 설정): 인광 녹색 단색 + 망점·주사선·스캔 광대·먼지·비네트, 장면은 0.5초 슬라이드 입장, 챕터 카드 2초, 주인공 색(#D97757)만 강조. 다른 주제는 lemo-opuscar 스킬로 다른 스타일을 골라 `LOOK` 팔레트/오버레이만 추가.

## 절차 (순서 고정)
1. `build.py` 작성: 대본을 문장 단위 장면으로 나누고 문장마다 kind·params 지정(`S`, `S2`(긴 문장은 쉼표 기준 여러 그림), `Q`, `CH`(챕터 카드)). `meta.json`에 제목·설명·태그·채널. `TREATMENT.md`(구조 3안+선택, 사운드, 자막)와 `CREDITS`도 작성.
2. `python3 projects/<폴더>/build.py plan` → project.json.
3. 음성 테스트: 대표 문장 6~8개를 먼저 생성해 받아쓰기(faster-whisper medium: `hf download Systran/faster-whisper-medium`)로 비교. 반복해서 틀리는 낱말은 `voice/lexicon.json`에 대체 표기 추가(26편: 외환위기→외환 위기, 금융위기→금융 위기, 경제위기→경제 위기, 원·달러→원달러).
4. 본편 음성: `~/.cache/yeouido-tts/venv/bin/python voice/qwen_cloud.py <project.json>` (nohup 백그라운드, CPU라 195장면 ≈ 4시간, 장면별 캐시라 끊겨도 이어짐. 먼저 `bash video-studio/setup_cloud.sh`).
5. `voice/align.py <project.json>` (자막 싱크용 단어 시각).
6. `build.py render [장면ID,...]` — 음성 길이(+쉼)에 맞춰 장면별 mp4 렌더. 2프로세스 병렬: 두 번째는 `HF_ROOT=/home/user/hf/crisis2`(첫 프로젝트 폴더 복사본)와 장면 ID 범위를 줘서 실행.
7. `python make_video.py <project.json> --voice cloud --no-package` → `tools/verify_video.py`, `voice/sync_check.py`.
8. 썸네일: `make_thumb.py`(VAR=A/B/C) — 참고 글체(금빛 3D 윗줄 + 흰 글씨 검정 외곽 아랫줄 + 빨간 붓터치, Black Han Sans), 배경은 영상 흐름에 맞게 코드로 그림. output/thumbnail*.png로 복사 후 `studio.package.package()`로 묶음 생성.
9. 제작일지 기록, 커밋·푸시, SendUserFile로 영상·썸네일·제목설명태그·자막 전달.

## 함정 (실제로 겪은 것)
- 코드(hf_econ.py)를 고치면 렌더 캐시 키에 반영되지 않는다 → 해당 `clips/parts/<id>p*_*.mp4`를 지우고 다시 렌더.
- SVG 속성은 반드시 따옴표(`opacity="0.95"`), 안 그러면 뒤 요소가 자식으로 먹혀 사라진다. 선 그리기는 GSAP `attr:{"stroke-dashoffset"}` 사용.
- 강조 괄호 안 띄어쓰기는 `split_marked`로 어절 분해(줄바꿈이 낱말 중간에서 끊기지 않게).
- 화면 하단 ~200px은 엔진 자막 자리, 우상단은 채널 워터마크 자리 — 내용은 y 150~880 안.
- Bash에서 `pkill -f`/`pgrep -f` 패턴이 자기 명령줄에 걸려 셸이 죽는다 → `ps -eo pid,args | grep '[b]uild.py render'` 형태로 pid를 뽑아 kill.
- 백그라운드 대기 작업은 2시간 제한 → 10분 단위 foreground 대기를 반복.

## 함께 쓰는 스킬
- `scenario-kinetic-film`: 비트에 맞춘 키네틱 타이포 티저(오프닝 5~15초·엔딩 카드·쇼츠)를 만들 때 사용하고, 결과 mp4를 이 절차의 `clip` 장면으로 삽입. 롱폼 본편은 이 스킬이 기본.

## A4 Cozy Storytelling 장면 (`story` kind, 2026-10-30)
- `tools/hf_story.py`: stickman-video-director A4 그림 문법(흰 채움 둥근 머리·검은 타원 눈·한 줄 팔다리, 머리에 더듬이=여의도 개미, 풀컬러 일상 배경)을 SVG로 직접 구현. 캐스트 `ant`(주인공)·`smart`(스마트머니). 장면 사전: bed_phone·cheers·market_sucker·heirloom·cheer_sell·goose·charity·vault·hacked·check_account·wave. 새 장면은 `ENVS`/`build()`에 추가.
- 사용: `S("대사", "story", scene="bed_phone")`. 룩은 `HF_LOOK=sting`(따뜻한 팔레트)과 함께 써서 인포 패널과 통일. A4 규칙: 컷마다 다른 장소, 새 인물 임의 추가 금지, 글자는 자막으로.
- Flow 클립 병행: `projects/<폴더>/flow/PHASE_A_제안.md`(연출 제안 → 승인 후 Phase B 프롬프트). 받은 mp4는 `clip` 장면으로 교체.
- 함정: GSAP로 SVG 그룹의 x/y를 절대값으로 트윈하면 `transform="translate()"` 위치가 0으로 리셋됨 → 상대값(`"+=4"`)이나 원래 좌표 기준 값 사용.
