---
name: editorial-video
description: [모델 2 · neural-studio/ 파이프라인 — 현철님이 '모델 2'·'네온'·'뉴럴서랍 스타일'을 말할 때만. 그 밖의 경제 영상은 econ-motion-video] 미주일기 스타일(구겨진 종이 인포그래픽 + 차분한 여의도여자 해설) 가로 롱폼·파일럿을 주제 한 줄로 기획·자료조사·대본·제작·검수까지 끝낸다. "미주일기 스타일로 ○○ 영상", "종이 인포그래픽 영상", "에디토리얼 영상 만들어줘", 보고서·경제·기술 해설 영상을 요청할 때 사용.
---

> **이 저장소(경제 채널)에서 쓰는 법 — 2026-11-08 현철님 '뉴럴서랍(AI)' 세션(브랜치 claude/funny-mendel-bng677)에서 복사.**
> 이 스킬의 파이프라인은 `neural-studio/` 폴더에 통째로 있다. 본문의 경로(`editorial/…`, `docs/…`, `projects/…`, `style.yaml`, `facetube/…`, `shorts/…`, `output/…`)는 모두 `neural-studio/` 기준이니 `cd neural-studio` 후 실행한다.
> 경제 채널(월재스)에서는 **모델 1** = 기존 `econ-motion-video`(HyperFrames·개미 마스코트·여의도남자·규칙집), **모델 2** = 이 파이프라인의 `style: neon`(검은 배경·금빛 네온 키네틱 타이포). 현철님이 '모델 2', '네온', '뉴럴서랍 스타일'이라고 할 때만 쓴다.

# 에디토리얼 롱폼 (미주일기 스타일)

현철님은 주제 한 줄만 준다. 기획, 1차 자료 확인, 대본, 장면 설계, 제작, 검수는 전부 내가 한다. 편집 질문은 하지 않는다.

## 먼저 읽기
- `docs/편집규칙집_에디토리얼.md`: 54장면 분해와 규칙 번호(CUT·SUB·EMP·SFX·BGM·VOX·BROLL·CAM·INTRO·OUTRO·SCR). **대본은 이 번호를 지켜 쓴다.**
- `.claude/skills/faceless-video/references/내규칙.md`: 현철님 피드백. 이 파일이 규칙집보다 우선한다.
- 예시 대본: `projects/pilot_editorial_ai2030.yaml`. 장면 종류 17개는 `editorial/scene.html` 머리말에 있다.

## 절차
1. **기획**: 핵심 질문 1개, 충격 숫자 2개, 챕터 4~6개(각 2~2.5분), 결론 질문 한 줄을 정한다.
2. **자료**
   - 1차 자료 원문을 직접 연다. WebFetch가 막히면 `curl -sL -A "Mozilla/5.0"`로 받는다.
   - 쓸 숫자를 `sources[].facts`에 적고 `verified: true`로 표시한다.
   - 사진은 라이선스를 확인한 것만 `projects/media/`에 넣고 `photos:`에 출처를 적는다.
3. **대본**: `projects/<slug>.yaml`
   - 판 하나 = `scenes[]` 한 항목이고 6~18초다. 판마다 `sync.at`에 요소가 나올 낱말 2~4개를 적는다.
   - 종이와 검정 판을 2~4장면마다 바꾼다. 같은 종류는 2번까지만 잇는다.
   - 인트로는 `year` → 대립 인용(`doc`/`person`) → 질문 순서다. 챕터 첫 장면에는 `chapter: <제목>`을 단다.
   - 아웃트로는 계단 그림을 다시 쓰며 제언하고 질문형으로 닫은 뒤, `kind: end, hold: 15`로 끝 화면을 둔다.
4. **빠른 확인**: `python editorial/make_editorial.py projects/<slug>.yaml --stills` → `output/<slug>/stills.png`를 Read로 직접 보고 겹침, 잘림, 빈 화면을 고친다.
5. **목소리**: 여의도여자만 쓴다(VOICE-03). 발음은 VOICE-05 발음 사전(docs/발음사전.md)을 거친다. 철자와 소리가 다른 고유명사·약어는 대본에 `원문{{발음}}` 으로 적는다.
   - Voicebox는 현철님 PC에만 있으므로 음성 생성과 영상 빌드는 PC에 연결된 세션에서 한다.
   - 연결이 없으면 그렇게 알리고 다른 목소리로 대체하지 않는다.
   - 쉼, 된소리, 숫자 기호 읽기는 코드가 자동으로 처리한다(`phrase_breaks`·`tense_hints`·`to_speech`).
   - 새로 틀리는 낱말이 나오면 `facetube/g2p.py TENSE_WORDS`에 추가한다.
6. **제작**: `python editorial/make_editorial.py projects/<slug>.yaml` → `output/<slug>/final.mp4`, `subtitles.srt`, `description.md`, `youtube.txt`(제목·설명란·해시태그·출처) + `thumbnail.jpg`(대본 `thumbnail:` 칸, PUB-02) — 최종본과 함께 보낸다, `qc_report.md`
7. **자체 검수**
   - `qc_report.md`의 항목을 모두 확인한다: 자막 오타, 음성↔대본, 소리 끊김, 화면 멈춤, 검은 화면, 개인정보, 스타일 점검.
   - ⚠가 있으면 고쳐서 다시 빌드하고, 0이 되거나 원인을 설명할 수 있을 때까지 반복한다.
   - `contact_sheet.png`도 Read로 본다.
8. **파일럿 먼저**: 롱폼 전에 30초 파일럿(장면 5개)을 만들어 SendUserFile로 보내고 컨펌을 받는다.

## 규칙 수치
`style.yaml editorial:`(속도 4.6~6.2음절/초, 판 18초 상한, 효과음 분당 8개, 자막 34자). 바꾸면 규칙집 표도 같이 고친다.

## 최종본을 보낼 때
영상·유튜브 텍스트·썸네일 세트를 주제 이름+버전으로 내보낸다 → `.claude/skills/video-release/SKILL.md` (PUB-01·02·03).


## 아래 자막 크기 (EDIT-15, 2026-11-05)
- 롱폼 아래 자막은 예전의 1.3배: neon 47px · paper 42px(`editorial/scene_neon.html`·`scene.html` 의 `#cap`). 긴 문장은 자동으로 줄이되 neon 34px · paper 31px 밑으로는 줄이지 않는다. 쇼츠는 그대로(84px).

## 장면별 도구 고르기 (2026-11-07, 기본 파이프라인 위에 '더하기'만)
기본은 그대로다: 대본 yaml → `editorial/make_editorial.py`(scene_neon/scene.html, 여의도여자 더빙, 자막 1.3배, 검수, PUB 세트). 아래 도구는 **특정 장면만 따로 렌더한 mp4 를 `scene: {kind: clip, video: …}` 로 끼울 때** 쓴다(자막·출처·틀·더빙·검수는 기존 그대로 얹힘). 설치·시험 기록: `.claude/skills/VIDEO-TOOLS.md`, 다시 깔기 `bash tools/motion/setup.sh`.

| 장면 | 먼저 쓸 것 | 쓸 도구 | 본보기 |
|---|---|---|---|
| 숫자 세기·비교 막대·인포그래픽 | 기존 `number`·`bars`·`score` | 더 화려한 차트·3D·데이터 연동이 필요하면 **Remotion**(React) 또는 **HyperFrames**(HTML+GSAP) | `tools/motion/remotion/Root.tsx` · `tools/motion/hyperframes/index.html` |
| 큰 제목 키네틱 타이포·글자 애니메이션 | 기존 `hook`(fx stamp/glitch/type) | **HyperFrames** + `hyperframes-registry`(블록 약 450개) | `/hyperframes` 스킬 먼저 읽기 |
| 공식·그래프·원리 설명(함수, 확률, 비용 곡선, 알고리즘 단계) | — | **Manim**(`/root/.cache/manim-venv/bin/manim`, 한글 Pretendard·MathTex) | `tools/motion/manim/test_scene.py` |
| 컷 리듬·샷 구성(오프닝, 전환, 카메라, 강조 순간) | 기존 look·cam·enter | **video-shotcraft** 샷 카드(`references/shots/`의 opening·transition·camera·typography·rhythm·data 등 124장)와 `aesthetic-rules.md`의 R(리듬) 규칙을 읽고 장면 배치에 반영 | 예: 핵심 숫자 뒤 1초 쉼(R1), 화면 전체 충격은 영상당 3번 이하(R4) |
| 대본→더빙→자막→타임라인 전체를 React 로 | (쓰지 않음: 우리 파이프라인이 그 역할) | `remotion-video` 스킬은 Remotion 문법·템플릿 참고용으로만 | — |

규칙
- 한 영상에 clip 장면은 **전체 장면의 20% 이하**로(채널 통일감 유지). 클립 길이는 장면 대사 길이와 맞추고, 짧으면 마지막 프레임에 머문다(`loop: true` 면 반복).
- 클립 안 글자도 우리 규칙을 지킨다: Pretendard·검은 테두리, 숫자는 출처 facts 에 있는 것만, 실제 회사 로고 그리지 않기.
- 클립 렌더 결과는 `output/_motion_test/` 같은 작업 폴더에 두고 git 에 올리지 않는다(소스 .tsx/.html/.py 는 `projects/clips/<slug>/` 에 커밋).
- 유료·외부 업로드 스크립트(video-shotcraft `publish/`, MiniMax TTS)는 현철님이 요청할 때만.
