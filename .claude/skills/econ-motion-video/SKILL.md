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

## 34편부터 새 방향 (2026-11-07 현철님 지정 · 유치한경제학급 품질 목표)
33편까지의 방식(코드 스틱맨 + 정보 패널)은 그대로 보존한다. 34편부터 아래를 기본으로 한다.

1. **캐릭터 두 겹.** 상세 설정은 `video-studio/assets/character/ANT_CHARACTER.md`.
   - 코드 마스코트: `HF_CHAR=chibi`(build.py 상단 `os.environ.setdefault("HF_CHAR","chibi")`).
     - 유치한경제학 마스코트처럼 단순하고 귀엽게 그린다. 2등신으로, 머리가 크고 **머리 외곽선이 두꺼우며** 키가 작다.
     - 더듬이·볼터치·흰 몸통에 주황 V 칼라, 감정 8종을 쓴다.
     - 숫자·도표 장면, 채널 배지, 썸네일 구석에 쓴다.
   - AI 일러스트 개미: 반실사 웹툰풍이다.
     - 정면·측면·감정 8종 캐릭터 시트를 먼저 만들고, 가장 좋은 정면을 `assets/character/ant_ref.png`로 저장한다.
     - 모든 일러스트는 이 기준 얼굴(IPAdapter)과 고정 프롬프트로 **같은 얼굴**을 유지한다.
2. **장면 구성.**
   - 장면의 **30~50%는 AI 일러스트**(인물이 나오는 상황 장면)로 한다. `S("대사", "illust", path="illust/sNNN.png", prompt="<상황 영문>", bubbles=[...], arrows=[...], zoom=(1.0,1.12), pan=(-30,-16))`
   - 일러스트는 멈춘 그림으로 두지 않는다. 켄 번스(천천히 확대·이동)를 기본으로 하고, 말풍선(`bubbles`: t,x,y,w,tail=down/left/right,at,c)과 손그림 화살표(`arrows`: x1,y1,x2,y2,c,at)를 대사 타이밍에 얹는다.
   - 나머지 50~70%는 숫자·도표 장면이다. HyperFrames가 기본이고, 정밀한 숫자 애니메이션은 Remotion, 공식·그래프는 Manim(`file` 장면)으로 한다.
3. **그림 생성 = 현철님 PC 그래픽카드(ComfyUI).**
   - 클라우드 컨테이너에는 GPU도 모델도 없다. PC에서 ComfyUI를 켜고 다음을 실행한다. `COMFY_URL=http://<PC>:8188 python3 tools/illust_batch.py projects/<폴더>`
   - 이 세션이 PC 폴더에 연결돼 있지 않으면, PC 쪽 Claude 세션(데스크톱 앱 또는 `claude remote-control`)에서 같은 명령을 실행한다.
   - 필요한 것: SDXL 계열 일러스트 체크포인트 + ComfyUI_IPAdapter_plus. 워크플로는 `tools/comfy_workflows/illust_ipadapter_api.json`이다.
   - 연결이 안 되면 `illust_batch.py`가 'AI 일러스트 대기 중' 임시 그림을 넣는다(`.placeholder` 표시 파일). 제작은 계속하고, 나중에 다시 실행하면 임시 그림만 진짜 그림으로 바뀐다. **임시 그림이 남은 채로 납품하지 않는다.**
4. **기획.**
   - 주제는 심리·습관형 50%, 시장 뉴스형 50%로 한다.
   - 제목은 역설·호기심형("~하는 진짜 이유", "97%가 결국 ~", "99%가 모르는 ~")을 쓰고, 근거·출처는 영상 안에서 지금처럼 밝힌다.
   - 구조는 이야기형이다. 가상 인물 한 명의 사연(가상임을 밝힘)으로 시작해 끝까지 끌고 가며 원리를 설명한다. 길이는 15~25분.
5. **썸네일.**
   - A·B: AI 일러스트 한 장면 + 실물 증거(계좌 화면·고지서·차트 숫자) + 2줄 큰 자막(흰·노랑, 검정 외곽)
   - C·D: 사이버·3D(`tools/thumb_cyber.py`)
   - 실존 인물 얼굴은 쓰지 않는다.
6. **바꾸지 않는 것:** 여의도남자 목소리와 발음 규칙, 편집 규칙집(자막 70px·구독 팝업·아웃트로), 장면 10초 규칙, 사실 확인과 "(보도)" 표기, 버전 묶음 규칙.

## 장면별 도구 선택 (2026-11-07 현철님 지정 · 기존 파이프라인은 그대로)
기본은 지금까지처럼 `build.py` → `hf_econ.py`/`hf_story.py` HyperFrames 장면 → 여의도남자 음성 → `make_video.py` → 규칙집 마감이다. 아래 도구는 **그 장면이 더 좋아질 때만** 골라 쓰고, 결과 mp4를 `S("대사", "file", path="<mp4>")`로 끼워 넣는다. `hf_econ.render`가 장면 길이에 맞춰 1080p30으로 자르고, 짧으면 마지막 프레임을 유지한다.

| 장면 | 도구 | 설치·사용 |
|---|---|---|
| 정보 패널, 인용, 체크리스트, 비교, 스틱맨 (대부분) | **HyperFrames** (기본, 이미 적용) | `hf_econ` 15종 + `story`. 스킬 hyperframes·hyperframes-cli·hyperframes-registry |
| 숫자 카운트업, 막대·누적 데이터, 대시보드형 인포그래픽 (정밀한 값 애니메이션이 여러 개) | **Remotion** (React) | `bash video-studio/setup_remotion.sh`, 예제 `tools/motion_tests/remotion-counter`, 스킬 `remotion-video-skill` |
| 공식·그래프·수학 설명 (복리 곡선, 72의 법칙, 손실 회복 곡선, 할인율, 수요·공급 이동) | **Manim** (Community) | `bash video-studio/setup_manim.sh`, 예제 `tools/motion_tests/manim/rule72.py`. LaTeX 미설치라 `MathTex` 대신 `Text`, 축 숫자는 직접 `Text`로 |
| 컷 리듬, 샷 구성, 오프닝·전환·타이포 동작 | **video-shotcraft** 레시피 | `.claude/skills/video-shotcraft/references/shots/` 카드 125개(opening·rhythm·transition·typography·data·camera·effects·outro)에서 원리만 가져와 HyperFrames GSAP나 Remotion으로 구현 |
| 대본 → 더빙 → 자막 → 타임라인 | **기존 파이프라인 유지** | `remotion-video-skill`은 Remotion 구조·자막 타이밍 참고용. 그 안의 edge-tts·MiniMax 음성 스크립트는 **쓰지 않는다** (목소리는 항상 여의도남자) |

- 말투, 발음 규칙(lexicon·주가 → [주까]·'그렇다면/다만' 더블 더빙 방지), 장면 10초 규칙, 규칙집 마감, 썸네일(사이버·3D), 사실 확인과 "(보도)" 표기는 도구와 상관없이 그대로 지킨다.
- 외부 도구 장면도 색은 회차 팔레트에 맞춘다. sting 기준 배경 #1b2330, 강조 금 #F2C14E, 빨강 #DE5B41(상승), 파랑 #5B93B8(하락). 상단 칩·워터마크 자리(y<150, 오른쪽 위)와 자막 자리(아래 200px)는 비운다.
- video-shotcraft의 Freesound 효과음과 `assets/audio`는 각 파일 라이선스(ATTRIBUTION)를 확인한 것만 쓰고, 출처를 설명란에 적는다.
- 디스크가 빠듯하다. 오래 걸리는 영상(2시간짜리 등)을 만들 때는 `/home/user/ext/remotion-test/node_modules`와 `/home/user/ext/manim-venv`를 지워도 된다. setup 스크립트로 다시 만들 수 있다.

## 썸네일 = 사이버·3D (2026-11-06 현철님 지정, 이후 모든 영상 기본)
- `tools/thumb_cyber.py` `render(out, "A"~"D", 윗줄, 아랫줄, mascot=, data=)` → output/thumbnail_A~D.png → `studio.package.package()`. 스타일 상세는 econ-video '내 규칙' 2026-11-06.
- 프로젝트마다 `make_thumb_cyber.py`(3~5줄)로 문구·숫자만 바꿔 호출한다.

## 썸네일 배경 회전 (2026-11-02)
- 글체는 고정, 배경색·분위기는 매 회차 변경. 사용 이력과 다음 후보는 `econ-video` 스킬 '내 규칙' 참고. 새 회차 `make_thumb.py`를 만들 때 `#root` 배경 그라데이션과 SVG 소재를 직전 회차와 다르게 바꾼다.

## 편집 규칙집 기본값 (v1.15.0, 2026-11-02 — 현철님 지정)
- 새 영상 meta.json에 항상 `"rulebook": true`, `"voice_speed_by": {"여의도남자": 1.0}`, `"scene_pause": 0.45`, `"top_title": "<짧은 제목>"`. 상세는 `rulebook-edit` 스킬과 `video-studio/편집규칙집.md`.
- 장면 설계: 한 장면 10초 이하, 해결책 파트는 좌우 전후 비교 우선, 스틱맨 장면 핵심어는 말풍선.

## 기획 체크리스트 (2026-11-03, 일본 히트작 7가지 — 상세는 econ-video '내 규칙')
- [ ] 제목에 날짜·기관·금액 2개 이상 [ ] 타깃 호명 [ ] 구체적 손실 금액(계산 근거 표시) [ ] 뉴스 1~3일 안 '긴급 해설'
- [ ] 롱폼 11분 이상(부족하면 사례·계산·시나리오 보강) [ ] 썸네일 = 실물(코드 그림) + 숫자 + 질문형 [ ] 출처 기관명을 제목·화면에 크게 (경력·자격은 지어내지 않음)
- 대본을 받으면 위 항목 중 빠진 것을 먼저 현철님께 제안하고(제목 대안 3개 등), 승인된 범위에서 반영한다.

## 배경: 흐린 풍경 + 움직이는 메시 그라데이션 (v1.16.0, 2026-11-03 — 현철님 요청)
- `HF_BG=scenery`(build.py 기본값): 정보 패널(kpi·quote·chart·compare 등) 뒤에도 스틱맨 장면의 풀컬러 공간(초원·카페·거리·거실·사무실·노을·공장·은행·지하철)을 흐리게 깔고, 그 위에 큰 방사형 블롭 3개가 장면 길이 동안 천천히 떠다니는 메시 그라데이션을 얹는다. 배경과 팔레트는 장면마다 해시로 바뀐다.
- 출처 기법: GitHub heygen-com/hyperframes 레지스트리(설치된 `hyperframes-registry` 스킬) `mk-background` 블록. 같은 레지스트리의 `mesh-gradient`·`flowing-gradient`·`aurora`는 WebGPU 셰이더라 이 클라우드(소프트웨어 렌더)에서는 쓰지 않는다 — GPU 환경에서만.
- 가독성: 틴트 50~62% + 본문 글자 그림자. 밝은 배경에서 글자가 흐려 보이면 틴트를 올린다.
- 함정(2026-11-03): 같은 HF_ROOT 폴더로 build.py render를 두 개 이상 돌리면 index.html이 섞여 엉뚱한 장면이 저장된다. 병렬은 반드시 HF_ROOT를 서로 다르게(crisis / crisis2), 이전 render가 끝났는지 `ps`로 확인하고 새로 띄운다.

## 디자인 품질 스킬 5종 (2026-11-04 설치, 모두 GitHub 원본)
| 스킬 | 출처 | 우리 영상에서 쓰는 곳 |
|---|---|---|
| `frontend-design` | anthropics/skills | 새 회차의 화면 방향(룩·팔레트·타이포)을 정할 때 — 주제에 맞는 디자인 방향 1줄 결정 |
| `ui-ux-pro-max` | nextlevelbuilder/ui-ux-pro-max-skill | 회차 팔레트·폰트 짝 확인(`scripts/search.py`로 색·폰트 조합 검색), 썸네일 배경색 회전 후보 |
| `hallmark` | Nutlope/hallmark | 완성 전 `audit`로 '양산형·AI티' 요소 걸러내기(HF 장면 HTML·썸네일 HTML 대상). 훅 설치 스크립트(install-hook.mjs)는 실행하지 않는다 |
| `emil-design-eng` | emilkowalski/skills | GSAP 애니메이션의 이징·길이·등장 순서 점검(hf_econ·hf_story 모션) |
| `web-design-guidelines` | vercel-labs/agent-skills | 장면 HTML의 결 흐트러짐(간격·정렬·대비·글자 넘침) 리뷰 |
- 순서: 기획 때 frontend-design → ui-ux-pro-max로 색·폰트 확정 → 렌더 전 샘플 프레임을 emil-design-eng·web-design-guidelines로 점검 → 납품 전 hallmark audit.
- 이 스킬들은 웹 UI용이라 영상에는 '원칙'만 적용한다(코드를 그대로 붙이지 않음).

## 모델 1 · 모델 2 (2026-11-08 현철님: "색깔을 하나 더 가져가자. 기존 모델 1, 지금 모델 2")
- **모델 1 (기본)** = 이 스킬: HyperFrames 장면(`tools/hf_econ.py`·`hf_story.py`) + 개미 마스코트 + 여의도남자 + 편집규칙집 마감. 썸네일은 사이버·3D.
- **모델 2** = 현철님 '뉴럴서랍(AI)' 세션에서 복사한 네온 에디토리얼 파이프라인 `neural-studio/`(스킬 `editorial-video`, 대본 yaml의 `style: neon`). 검은 바탕 점 격자·금빛 모서리 괄호·네온 발광 키네틱 타이포·숫자 카운터, 마스코트 없음, 목소리 여의도여자.
  - 실행: `cd neural-studio && QWEN_TTS_HOME=~/.cache/yeouido-tts python3 editorial/make_editorial.py projects/<slug>.yaml [--stills]` → `output/<slug>/final.mp4`·`subtitles.srt`·`youtube.txt`·`qc_report.md`.
  - 클라우드 준비(1회): `pip install soundfile pyyaml pycairo fonttools brotli sherpa-onnx edge-tts playwright`, `apt-get install tesseract-ocr tesseract-ocr-kor`, 검수용 음성인식 모델은 `neural-studio/setup.sh`가 받는다(~/.cache/facetube/models, 약 340MB). 여의도여자는 이미 깔린 `~/.cache/yeouido-tts`(같은 Qwen3-TTS 엔진)를 `QWEN_TTS_HOME`으로 가리키면 PC 없이 된다.
  - 본보기: `neural-studio/projects/sample10_neon_econ.yaml`(월 50만 원 20년 적립, 12초). 숫자는 `sources[].facts`·`numbers_ok`에 있어야 검수 통과.
- 현철님이 '모델 2', '네온', '뉴럴서랍 스타일'이라고 하면 모델 2, 아무 말 없으면 모델 1.

## 썸네일 원칙 · 매번 바꾸기 (2026-11-11 현철님: "이거보고 썸네일을 매번 좀 바꿔. 너무 클릭률이 낮아")
참고: 비디클래스「50만 유튜버는 썸네일을 이렇게 만듭니다 (썸네일의 모든 것)」 https://youtu.be/koJ6u7uxEwY. 모델 1·모델 2, 모든 썸네일에 적용한다.
1. **한눈에 읽힌다.** 두꺼운 글씨(Black Han Sans)를 쓰고, 글자는 배경과 분리한다(검정 외곽선이나 바탕 상자). 시선이 먼저 갈 피사체를 하나로 정한다. 얇은 글씨, 이상한 비율, 묻히는 요소는 쓰지 않는다.
2. **복잡하지 않다.** 요소가 많아도 레이아웃이 정리돼 있으면 된다. 텍스트는 폰에서 읽히는 크기로, 덜어낼 수 있는 만큼 덜어낸다(줄당 8~10자 안팎).
3. **예쁜 것보다 먹히는 것.** 후킹 문구(큰 숫자, 질문, 대비)와 궁금증을 부르는 그림을 쓴다. 약간 '쌈마이'해도 된다. 다만 영상이 답하지 않는 낚시는 금지한다.
4. **첫 10초와 일치시킨다.** 썸네일에 쓴 숫자나 질문을 영상 첫 10초 안에서 바로 보여 주거나 키운다. 하이라이트가 영상 뒤쪽에 있으면 맨 앞으로 끌어온다.
5. **제목과 다른 각도로 쓴다.** 제목 문장을 그대로 반복하지 않는다. 제목은 검색 키워드용, 썸네일은 감정과 숫자용이다.
6. **오른쪽 아래는 비운다.** 재생시간 배지가 가리는 자리라서 중요한 글자를 두지 않는다. 하단에 쫙 까는 텍스트는 피한다.
7. **두 줄이면 무게 차이를 준다.** 윗줄과 아랫줄의 굵기, 색, 바탕 상자를 다르게 한다(예: 빨강 상자 작은 줄 + 아주 큰 흰 글자).
8. **레이아웃은 회차마다 돌린다.** 직전 회차와 같은 레이아웃을 쓰지 않는다. 후보 3개도 서로 다른 레이아웃으로 만든다.
   - 순번: ① 콜라주(누끼 소품 + 흰 윤곽 + 그림자, 기본 추천) ② 2분할 VS ③ 중앙 큰 숫자 ④ 상단 텍스트 + 아래 그림 ⑤ 왼쪽 아래 2줄
   - 바탕색도 직전 회차와 다르게 한다. 사용 이력은 `video-studio/썸네일_이력.md`에 적는다.
9. 크기는 16:9 1280×720, 2MB 이하. 실존 인물 얼굴은 계속 쓰지 않는다. 대신 개미 마스코트 누끼와 실물 소품(영수증, 카드, 고지서, 계좌 화면)을 쓴다.

## 제작 도구 7종 (2026-11-11 현철님: "위 스킬을 다 접목시켜. 중복이면 스킵")
| 도구 | 상태 | 어디에 쓰나 | 실행 |
|---|---|---|---|
| FFmpeg 편집·렌더 | 이미 있음(스킵) | 장면 합치기·자막 입히기·라우드니스 -14 LUFS·정지 검사 | `make_video.py`, `verify_video.py` |
| faster-whisper 받아쓰기 | 이미 있음(스킵) | 자막 싱크 단어 시각, 발음 검수 | `voice/align.py`, `voice/qa_video.py`, `voice/sync_check.py` (TTS venv) |
| ComfyUI 내 PC AI 이미지 | 이미 있음(스킵) | AI 일러스트 장면·썸네일 그림 | `tools/illust_batch.py`, 스킬 `comfyui` |
| Remotion 코드 모션그래픽 | 이미 있음(스킵) | 정밀 숫자 카운트·대시보드 장면 | `setup_remotion.sh`, 스킬 `remotion-video` |
| **PySceneDetect 장면 나누기** | 새로 접목 | ① 현철님이 첨부한 참고 영상의 컷 위치·평균 컷 길이·분당 컷 수 + 컷별 대표 프레임 밀착 인화지 → 장면 수·10초 규칙을 참고 영상 리듬에 맞춤 ② 완성본 검수: 12초 넘게 같은 화면인 구간 찾기 | `python3 tools/scene_split.py <영상> --sheet [--max-shot 12]` → `<영상>_scenes/scenes.json·csv·contact_sheet.jpg` |
| **Real-ESRGAN 화질 키우기** | 새로 접목 (CPU) | 작은 실물 사진·스크린샷·로고 소품을 썸네일·장면 크기로 선명하게, ComfyUI 1024px 일러스트를 켄 번스용 2배, 10초 이하 자료 클립 | `bash setup_esrgan.sh` 1회 → `/home/user/ext/esrgan-venv/bin/python tools/upscale.py <png/jpg/mp4> --scale 2 --model photo\|anime` (누끼 투명도 유지, 1장 ≈ 5~10초) |
| **Blender 3D** | 새로 접목 (헤드리스) | 핵심 숫자를 금빛 3D 글자 + 쏟아지는 동전으로 세우는 강조 컷(`file` 장면), 썸네일용 투명 PNG 3D 재료 | `bash setup_blender.sh` 1회 → `/home/user/ext/blender-4.5.9-linux-x64/blender -b -P tools/blender_3d.py -- --text "117만 원" --sub "추가 납부 평균" (--still) --out <파일>` |
- 순서: 참고 영상을 받으면 먼저 `scene_split.py --sheet`로 리듬을 재고 장면 설계 → 렌더 → 합치기 후 `scene_split.py <final> --max-shot 12`를 `verify_video.py`와 함께 돌린다.
- 썸네일 소품 사진이 작거나 흐리면 `upscale.py`를 거친 뒤 얹는다. 3D 숫자 썸네일(사이버·3D)은 `blender_3d.py --still`로 만든 투명 PNG를 배경 위에 얹는다.
- Blender cycles 영상은 CPU라 느리다(1080p 프레임당 30~45초) → 4초 이하, 720p·12샘플로 백그라운드 렌더. 급하면 workbench(밋밋함).
- 설치물은 저장소 밖 `/home/user/ext`(약 2GB). 디스크가 빠듯하면 지워도 setup 스크립트로 다시 만든다.
