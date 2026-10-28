---
name: youtube-factory-playbook
description: 유튜브 영상 공장 구성도(알렉스 님 사례 12개 요소 — Claude Code+Codex, HyperFrames, ElevenLabs PVC, Higgsfield·Seedance, Blender, AutoKliq, Aside, Suno, ffmpeg·whisper, 규칙 시스템, 발행 원장, Remotion)와 우리 쪽 도입 상태. 영상 제작 파이프라인을 설계·확장하거나, 어떤 도구를 쓸지·무엇이 이미 있는지 판단하거나, 규칙·피드백·발행 기록을 관리할 때 사용.
---

# 유튜브 영상 공장 구성도 (2026-10-28 현철님이 공유한 사진 12장을 저장)

출처는 알렉스 님의 **비공개 저장소 구성도 사진**이다. 파일 경로 몇 개만 보이고 코드는 볼 수 없다. 아래 "사진 속 설명"은 사진에 적힌 것만 옮겼고, "우리 상태"는 이 환경에서 직접 확인한 것이다.

| # | 요소 | 사진 속 설명 | 우리 상태 (2026-10-28) |
|---|---|---|---|
| 1 | Claude Code + Codex | 같은 스킬(`.agents/skills`)을 두 에이전트가 공유, 한쪽이 만들고 다른 쪽이 독립 검토 | **해당 없음**: Codex 가 없고 스킬은 `.claude/skills`. 독립 검토가 필요하면 서브에이전트로 대신할 수 있으나 **현철님이 요청할 때만** 쓴다 |
| 2 | HyperFrames | HTML+GSAP 컴포지션을 영상으로 렌더. 쇼츠 키트·모션 조각·롱폼 장별 필름 엔진 | **설치함**(핵심 4개). 아직 한 번도 실행 안 함, 크롬 동작 미확인. 쓰려면 `/hyperframes` 먼저 읽기. 자체 쇼츠 렌더러(`shorts/`)와 병행 |
| 3 | ElevenLabs PVC | 본인 Professional Voice Clone, 쇼츠 표준 eleven_v4, 대본 전체를 한 번에 생성 | **선택 사항**: ElevenLabs 연결은 있으나 제한 커넥터(음성 생성·받아쓰기·목소리 설계)라 PVC 가능 여부는 미확인. 채널 목소리는 **현수로 고정**. 현철님 *본인* 목소리를 쓰고 싶을 때만 검토(본인 샘플·요금제 필요). 새로 보이는 Fish Audio 연결에도 음성 복제 도구가 있음 |
| 4 | Higgsfield · Seedance 2.5 | 영화·광고 영상 생성, 헤드리스 claude 가 Higgsfield MCP 로 호출(API 키 없음) | **불가**: 우리 Higgsfield 연결은 조회 전용(생성 불가). 대신 **Pollo 에 seedance-2-5 계열이 있어** 제가 직접 생성할 수 있다(크레딧 필요) |
| 5 | Blender 5.2 | 3D 스킷 키트, 모션, 영상 생성 전 카메라 블로킹 가이드 | **미설치**. 필요해지면 설치 가능 여부부터 확인. 지금은 개념만 저장 |
| 6 | AutoKliq | 알렉스 님이 만든 썸네일 서비스: 채널 맞춤 콘셉트 6안 → 렌더 → 편집, MCP 로만 호출 | **없음**. 썸네일은 Pavo·Digen·Pollo 이미지 + 글자는 우리가 얹기. 썸네일 합성 도구는 아직 미구현 |
| 7 | Aside | 로그인된 브라우저를 스크립트로 조작: Studio 지표 읽기, 업로드, 예약 | **미도입**. 업로드·예약·계정 작업은 현철님이 하는 원칙. 대신 아래 11번 원장에 기록. 원격 PC 연결 도구가 새로 보이나 미시험 |
| 8 | Suno | 음악은 브라우저 수동 레인으로 만들고 후반에 따로 믹스 | **도입함**: `bgm: {path, tool, model, generated_on}` 로 외부 음악 파일 사용, 기록·약관 경고·설명란 표기 (규칙 EXT-06). Suno 약관은 미확인 |
| 9 | ffmpeg · whisper.cpp | 합성, 라우드니스(-14/-16 LUFS), 정지 프레임 검사, ASR 대조 | **이미 있음**: ffmpeg 합성, -14 LUFS 정규화, freezedetect, sherpa-onnx 음성인식 대조(whisper.cpp 는 미설치). 사진은 -14/-16 두 기준이나 구분은 안 보여서 우리는 -14 로 고정 |
| 10 | 규칙 시스템 | `rules/` 아래 활성 규칙 146개, 피드백 원문이 인박스에 쌓이고 규칙·린트로 바뀜 | **도입함**: `rules/*.yaml` 38개(린트 점검 30 + 수동 8), `feedback/inbox.jsonl` 9건. `python scripts/rules/rules.py lint` |
| 11 | 발행 원장 | 업로드·예약·공개·삭제를 이벤트로 기록(401건) | **도입함**: `tools/ledger.py` + `content/history/published.jsonl`(아직 비어 있음). 앞 단계 없는 공개·삭제, 예약 시각 누락은 기록을 거부 |
| 12 | Remotion | 스킬 12개가 설치돼 있지만 실제 렌더에 쓴 기록은 못 찾음, 기본은 HyperFrames | **의도적으로 안 씀**. 필요하면 `remotion-to-hyperframes` 로 가져온다 |

## 쓰는 법

**피드백 → 규칙 (10번)**: 현철님이 한 말이 다음 영상에도 적용될 것이면
1. `python scripts/rules/rules.py add "<한 말 그대로>" --context "<어느 영상 몇 초>"`
2. `python scripts/rules/rules.py promote FB-00NN --id <영역-번호> --scope <all|shorts|longform|voice|external|process> --text "<숫자로 쓴 규칙>" [--config style.yaml키] [--code 파일:함수] | --manual`
3. `python scripts/rules/rules.py lint` 가 0 오류여야 한다. 린트는 규칙이 가리키는 설정 키·코드 함수가 실제로 있는지, 인박스 원문이 가리키는 규칙이 있는지, 7일 넘게 처리 안 된 피드백이 있는지 본다.
규칙의 원본은 `rules/*.yaml` 이다(`references/내규칙.md` 는 사람이 읽는 요약). **숫자가 없는 규칙은 지켜지지 않는다**: 가능하면 `style.yaml` 에 값을 두고 빌드가 점검하게 연결한다.

**발행 기록 (11번)**: 현철님이 "올렸어요/예약했어요/공개했어요/지웠어요"라고 알려 주시면
`python tools/ledger.py add --video <slug> --event uploaded|scheduled|published|deleted [--url ... --at ISO시각 --visibility ...]`.
`python tools/ledger.py summary`, `check` 로 확인.

**외부 음악 (8번)**: 대본 YAML 에 `bgm: {path: media/<이름>/music.mp3, tool: Suno, model: ..., generated_on: "YYYY-MM-DD"}`. 짧으면 이음새를 크로스페이드로 반복하고 앞뒤를 페이드한다.

## 다음 후보 (현철님 결정 필요)
- 썸네일 합성 도구(이미지 + 큰 글씨 2줄 + 시리즈 로고), AutoKliq 방식의 콘셉트 여러 안 만들기
- HyperFrames 첫 실행(크롬 동작 확인) 후 쇼츠 키트 활용
- 발행 후 지표 기록(조회·유지율)을 원장과 연결
