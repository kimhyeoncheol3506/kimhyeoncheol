---
name: editorial-video
description: 미주일기 스타일(구겨진 종이 인포그래픽 + 차분한 여의도여자 해설) 가로 롱폼·파일럿을 주제 한 줄로 기획·자료조사·대본·제작·검수까지 끝낸다. "미주일기 스타일로 ○○ 영상", "종이 인포그래픽 영상", "에디토리얼 영상 만들어줘", 보고서·경제·기술 해설 영상을 요청할 때 사용.
---

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
