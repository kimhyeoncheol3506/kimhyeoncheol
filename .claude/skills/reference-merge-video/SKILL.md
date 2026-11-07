---
name: reference-merge-video
description: 현철님이 참고 유튜브 영상 2개 이상(스크린샷·링크)을 주고 "이 영상들 합쳐서 내 영상으로 만들어 줘"라고 하면 쓴다. 참고 영상들의 내용 합집합을 얼굴없는 뉴럴서랍 롱폼(S2 neon, 여의도여자)으로 만든다. 길이는 참고 영상 평균, 첫 화면에 후킹. 본보기: projects/rea_full_neon.yaml (2026-11-03, 13:02, REA).
---

# 참고 영상 합치기 → 뉴럴서랍 롱폼

본보기 결과물: `projects/rea_full_neon.yaml` → `output/rea_full_neon/final.mp4` (781.9초, 장면 106개, 평균 7.4초, 5.3음절/초, -14.3 LUFS).
참고 A: AI 슬래시 「[Deep SLASH] 깃허브 발칵 뒤집은 'REA' 완벽 정리」(3NFwU6dAUws, 11:58)
참고 B: 신영선의 AI탐구 「REA부터 미친 오픈소스 전부 공유」(dQd-f0nNQtI, 14:05)

## 역할 나누기 (중요)
| 단계 | 누가 | 이유 |
|---|---|---|
| 1. 참고 영상 자막·장면 썸네일·설명란(챕터) 수집 | **Aside(현철님 PC 브라우저)** | 클라우드 세션은 유튜브 접속이 막힐 수 있음. Aside가 자막(타임스탬프)과 스토리보드(5초 간격 썸네일)를 뽑아 `analysis/<slug>/` 에 넣어 준다 |
| 2. 분석 → 구성표 → 대본 yaml | 클로드(이 세션) 또는 Aside | 아래 규칙 |
| 3. 사실 확인(원문 열기) | 둘 다. 숫자는 원문 연 것만 | `sources[].verified: true`, 숫자는 `facts` 에 |
| 4. 더빙·렌더 | **현철님 PC만** (Voicebox 여의도여자) | 바탕화면 `뉴럴서랍_영상만들기.bat` 또는 Aside. 13분 ≈ 1시간 45분(장면당 약 1분) |

## 1. 분석에서 뽑을 것
- 영상마다: 길이, 챕터(설명란), 도입 30초 문장, 파트 구조, "정리하면" 같은 반복 장치, 비유, 말투(존댓말 해설 / 말 거는 구어체), 화면 패턴(스토리보드).
- 길이 목표 = 참고 영상 길이 평균(±30초). REA: (718+845)/2 = 781초.
- **합집합 원칙**: 뼈대는 구조가 더 탄탄한 쪽(A: /what·/use·/how·/install·견해), 살은 다른 쪽의 고유 내용(B: 요리·김치 비유, 별 증가 막대, 검증 루프, 역할 나누기, 백업·재측정). 겹치는 내용은 한 번만, 더 쉬운 설명으로.
- 문장을 그대로 옮기지 않는다(재사용 콘텐츠 위험). 정보·구조·장치만 가져오고 문장은 새로 쓴다.

## 2. 구성 (REA 본보기 그대로)
1. **후킹 0~60초**: 충격 문장 + 질문(첫 20초 안에 `?`) → 센 숫자(number) → 증가 막대(bars) → 한 줄 정의(flow) → 해외 반응(doc) → "진짜 중요한 건 따로 있다" 반전 질문(hook) → 목차(agenda) → 오늘 순서(recap).
2. **파트 5~6개**: 각 파트는 `part`(민트 전체 화면 /what) 로 열고 `recap`("정리하면 ...") 으로 닫는다. `chapter:` 를 part 장면에 달면 설명란 챕터가 자동 생성.
3. 다른 참고 영상의 핵심 인사이트는 독립 파트로(REA: PART 04 /check).
4. 내 관점 한 줄(뉴럴서랍의 생각), 주의(warn) 장면은 법·약관 선을 분명히.
5. 마무리: 여운 문장 → 실천 권유 → 양날의 검 → cta(`hold: 8`, 끝 화면 자리). **다음 편 예고는 넣지 않는다**(EDIT-12): 구독·좋아요 + 설명란 안내로 닫는다.

## 3. 장면 (scene_neon.html, 15종)
hook · title · number · icons · flow · terminal · chat · list · warn · doc · cta
+ 2026-11-03 추가(AI 슬래시 실측): **part**(`num, slash, title`) · **recap**(`slash, items:[{k,v}]`) · **agenda**(`items:[{slash,text}]`, 6개까지) · **bars**(`label, bars:[{label,value,show}], sub`, 출처 필수)
- `sync.at`·`sync.beats` 에는 **띄어쓰기 없는 한 낱말**만("한 번에" ✕ → "번에" ○). 빌드가 낱말 단위로 찾다 멈춘다(2026-11-06 제브 빌드).
- 같은 종류 3번 연속 금지, 한 장면 9초 이하(대사 약 40음절 이하), `sync.at` 에 요소가 뜰 낱말.
- 실제 로고·인물 사진 대신 글자·기호 타일. 확인 못 한 SNS 글은 가짜 트윗 카드로 만들지 말고 chat 예시나 "~했다는 글"로.

## 화면 모양 바꾸기 (EDIT-13, 영상마다 다르게)
대본 맨 위에 `look:` 을 넣는다. 직전 영상과 2가지 이상 다르게 고른다.
```yaml
look: {bg: "#0B1630", acc: "#FF9F45", sky: grid, frame: bracket, cam: drift, enter: slide, bright: 0.35}
```
- sky: stars(기본 별자리) · grid(원근 바닥 격자) · dots(점 물결) · aurora(번지는 빛)
- frame: none · bracket(네 모서리 꺾쇠) · border(얇은 둥근 테두리) · bars(위 굵은 띠)
- cam: zoom(기본 3% 다가감) · drift(옆으로 흐름) · tilt(살짝 기울기) · pull(물러남)
- enter: rise(아래서 떠오름) · slide(옆에서 밀려옴) · zoom(작게→크게)
- bright: 0~1, 가장자리 어둡기를 줄여 화면을 밝게
- 지금까지: 어사이드·에고라이트·깃허브·클로드코드 = 기본(stars, 민트, zoom, rise) / 클로드 인 크롬 = 위 예시

## 4. 목소리 (장면별 톤·강약)
- 기본: `voice.instruct` (친근한 IT 해설 톤). 장면마다 `instruct:` 로 덮어쓴다(캐시 키에 포함됨).
  - 후킹: "충격적인 소식을 터뜨리듯 힘 있고 빠르게, 질문은 끝을 올려"
  - 경고: "낮고 단호하게"  · 정리(recap): "차분하게 정리하듯 또박또박" · 비유: "다정하고 부드럽게" · cta: "밝고 경쾌하게"
- 고유명사는 참고 영상 발음을 따른다: `say_as: {REA: 레아}`. 대사(say)에는 되도록 한글 발음으로 쓴다(엠씨피, 기드라, 노드제이에스).

## 5. 사실·숫자
- 숫자는 원문을 연 출처의 `facts` 또는 `numbers_ok` 에만. 날짜가 들어간 화면 글자(2026-11-03 등)도 숫자 점검 대상 → `numbers_ok` 에 연·월·일 추가.
- 참고 영상 제작자의 자체 조사 숫자는 "한 유튜버가 조사했을 땐"처럼 출처를 밝혀 쓴다.
- 법률은 국가법령정보센터 원문(예: 저작권법 제101조의4), 기업 발표는 보도자료 원문.

## 6. 빌드·검수
- PC: `python editorial/make_editorial.py projects/<slug>.yaml` (Voicebox 켜고). 새 장면은 먼저 `--stills --stand-in-voice` 로 그림만 확인(20초, 배포 금지).
- 끝나면 qc_report.md: 음성 불일치(CER>0.3), 소리 끊김, 9초 넘는 장면, facts 에 없는 숫자를 보고 고칠 장면만 다시 만든다(TTS 캐시 덕분에 바뀐 장면만 재생성).
- 최종본과 함께 `output/<slug>/youtube.txt`(제목·설명란·해시태그·출처·참고한 영상) 와 `thumbnail.jpg`(PUB-02: 글자 없는 AI 배경 `assets/thumbs/<slug>_bg.png` + 굵은 두 줄 제목) 를 보낸다. 대본에 `links`·`github`·`references`·`title_alt` 를 채워 둔다.
- 결과 보고: 길이, 챕터, 참고 영상별로 가져온 것, 검수 경고, 사람 귀로 확인할 곳.

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
