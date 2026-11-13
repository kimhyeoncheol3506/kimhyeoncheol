# '이거 한편으로 끝' 시리즈 — 대본 작성 공통 지시 (2026-11-13 현철님 요청)

모델 2 파이프라인(neural-studio, `style: paper` 종이 인포그래픽, 목소리 여의도여자)으로 만든 「경제 속 유대인의 역사」(1시간 5분, 298장면)와 **같은 형식**으로 한 편의 대본을 쓴다. 더빙·렌더는 하지 않는다(메인 세션이 차례로 한다).

## 반드시 먼저 읽을 본보기
- `neural-studio/projects/jewecon_parts/head.yaml` (머리말 형식: slug·name·title·style·voice·summary·tags·disclaimer·say_as·numbers_ok·sources·intro·outro)
- `neural-studio/projects/jewecon_parts/ch1_3.yaml` 앞부분 150줄 (장면 쓰는 법: say / scene{kind…} / sync.at / source / theme: dark / chapter / instruct)
- `neural-studio/projects/jewecon_parts/build_jewecon.py` (조각 합치기 + @사진 키워드 → 파일), `photo_map.yaml`, `projects/media/jewecon/manifest.yaml`(사진 출처 형식)
- `neural-studio/projects/jewecon_parts/make_thumb.py` (썸네일 2종: A=역사 그림+질문, B=통념 문구+"진짜일까?"+팩트체크 띠)
- 장면 종류와 각 칸 이름: `neural-studio/editorial/scene.html` 머리말 + 각 kind 의 render 코드(필요한 칸만 확인). kind: year | chapter | doc | person | quote | bars | waffle | line | gauge | bignum | stairs | flip | pie | photo | timeline | stack | end
- 규칙집: `neural-studio/docs/편집규칙집_에디토리얼.md` (훑어보기)

## 이번 시리즈 공통
- 제목은 반드시 `(이거 한편으로 끝) ` 으로 시작. `name:` 은 폴더용 짧은 한글(띄어쓰기 없이), `brand: 월급쟁이 재테크 스킬`.
- 길이: 유대인 편과 비슷하게 **55~65분**(한글 약 17,000~20,000자, 270~310장면). 챕터 7~9개 + 인트로 + 아웃트로.
- 구조(챕터마다 반복): **역사 장면 → 쉬운 비유 → 원리 → 숫자 → 지금 내 돈에 주는 교훈**. 마지막 챕터는 '월급쟁이가 지금 내 돈을 어떻게 해야 하나'(구체적·일반적인 행동, 특정 종목 추천 금지, "투자 권유 아님").
- 인트로: 첫 20초 안에 영상이 답할 질문(?)을 던지고, 썸네일 통념 문구를 첫 10초 안에 그대로 보여 준다(썸네일=첫 10초 일치).
- 판 하나는 6~18초(대사 한글 30~90자). 종이/검정(`theme: dark`) 판을 2~4장면마다 바꾸고, 같은 kind 는 2번까지만 잇는다. 판마다 `sync.at` 에 대사 속 낱말 2~4개.
- 형광펜은 `[[ ]]`. 발음이 철자와 다른 약어·외국어는 say 안에서만 `원문{{발음}}` (화면 글자에는 쓰지 않음). 약어는 `say_as` 에도.
- **숫자·연도는 공식 통계(각국 통계청·중앙은행·IMF·World Bank·OECD·한국은행·KOSIS·국가법령)나 신뢰할 기사로 직접 원문을 열어 확인한 것만.** WebFetch 가 막히면 `curl -sL -A "Mozilla/5.0" <url>`.
  확인한 숫자는 `sources[].facts` 에 화면·대사에 쓰는 표기 그대로 넣고 `verified: true`. 확인 못 한 건 쓰지 않거나 "추정"이라고 말한다. 화면/대사에 나오는 모든 숫자(연도 포함)는 facts 나 `numbers_ok` 에 있어야 한다.
  숫자 장면(bars·waffle·line·gauge·bignum·stairs)에는 `source:` (화면 오른쪽 아래 짧은 출처) 필수.
- **특정 민족·국가 비하, 음모론, 정치적 편들기 금지.** 논쟁적 해석은 양쪽을 소개. 실존 인물은 업적·정책 위주로, 얼굴 클로즈업 사진은 쓰지 않는다.
- 사진: 위키미디어 공용 등 **퍼블릭 도메인·CC 라이선스만**, 장면 내용과 정확히 맞는 것만. `neural-studio/projects/media/<slug>/` 에 받고 `manifest.yaml`(file·title·subject·date·author·license·url) 작성, 대본에서는 `@키워드` + `photo_map.yaml`. 15~30장 정도. 못 구하면 빼도 된다(사진 없는 장면은 quote 등으로).
- 썸네일 2종(`make_thumb.py`, 유대인 편 make_thumb 와 같은 방식, 1280×720, 실존 인물 얼굴 금지):
  - **A**: 그 나라 역사·풍경 사진 + 큰 질문 문구 + 왼쪽 위 빨간 칩 "1시간 몰아보기"
  - **B**: 지정된 통념 문구(노랑) + "진짜일까?"(흰색 아주 크게) + 아래 흰 띠 팩트체크 한 줄
  - 렌더: `python3 projects/<slug>_parts/make_thumb.py` → `neural-studio/assets/thumbs/<slug>_thumb_A.png`·`_B.png` (사진은 `/home/user/hf/thumb/assets/<slug>/` 로 복사해 쓰기, make_thumb_v2.ROOT=/home/user/hf/thumb). 결과 PNG 를 Read 로 직접 보고 글자 겹침·잘림 고치기. 오른쪽 아래(재생시간 자리) 비우기.
  - head.yaml 의 `thumbnail: {file: assets/thumbs/<slug>_thumb_B.png}`.
- 고정 댓글용 출처: head 의 `sources` 가 설명란·고정 댓글로 자동 정리된다(유대인 편 `make_youtube_txt.py` 가 사용). 각 출처에 outlet·title·date·url·verified·facts.

## 만들 파일 (neural-studio 기준)
- `projects/<slug>_parts/head.yaml`, `ch*.yaml`(2~4조각), `photo_map.yaml`, `build_<slug>.py`(build_jewecon.py 를 복사해 경로만 바꿈) → 실행하면 `projects/<slug>.yaml` 생성
- `projects/media/<slug>/` 사진 + `manifest.yaml`
- `projects/<slug>_parts/make_thumb.py` + 썸네일 PNG 2장

## 끝내기 전 점검 (반드시)
1. `python3 projects/<slug>_parts/build_<slug>.py` → 장면 수·예상 분·못 찾은 사진 출력 확인
2. `python3 tools/series_lint.py projects/<slug>.yaml` → **'통과'가 나올 때까지** 고친다(예상 길이 55~65분)
3. 썸네일 PNG 두 장 Read 로 확인

## 하지 말 것
- make_editorial.py 실행(더빙·렌더) 금지 — CPU 를 메인 세션이 쓴다. `--stills` 도 금지.
- git commit/push 금지(메인 세션이 한다). 다른 편 폴더·기존 파일 수정 금지(tools/series_lint.py 포함).
- 큰 파일(사진 1장 3MB 넘으면 줄여서 저장, 긴 변 2400px 이하 jpg).

## 보고 (마지막 메시지, 한국어, 짧게)
slug · 제목 · 장면 수 · 예상 길이 · 챕터 목록 · 사진 수 · 썸네일 경로 2개 · **확인이 더 필요한 숫자/주장**(있으면) · lint 결과.
