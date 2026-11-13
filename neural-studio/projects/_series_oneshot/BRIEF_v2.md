# '한편으로 끝' 4편 — 줄이기 지시 v2 (2026-11-13 현철님 새 규칙, BRIEF.md 보다 우선)

먼저 `neural-studio/docs/채널규칙_제목썸네일첫15초.md` 를 읽는다(형식·썸네일·제목·첫 15초). 그다음 기존 `BRIEF.md` 의 사실 확인·금지 규칙은 그대로 지킨다.

## 할 일 (편 하나당)
1. **본편 10~15분으로 줄이기** — 이미 있는 `projects/<slug>_parts/` 60분 대본을 살려서 줄인다(새로 쓰지 말고 골라 다듬기).
   - 목표: 예상 길이 11~14분(series_lint 기준), 장면 60~85개, 챕터 4~5개 + 인트로 + 아웃트로.
   - 이야기 뼈대(역사 장면 → 비유 → 원리 → 숫자 → 내 돈 교훈)는 유지하되 가장 센 장면만 남긴다. 마지막 챕터 '월급쟁이가 지금 내 돈을 어떻게 해야 하나'는 유지("투자 권유 아님").
   - **남기는 문장은 say 글자를 한 글자도 바꾸지 않는다**(녹음 캐시를 다시 쓰기 위해 — 특히 oneshot_japan 은 앞부분 약 100문장이 이미 녹음됨). 새로 써야 하는 건 인트로·연결 문장·구독 한마디 정도.
   - 기존 60분판은 지우지 말고 `projects/<slug>_parts/long60/` 로 옮겨 보존. 새 조각은 `projects/<slug>_parts/` 에 head.yaml + ch*.yaml(1~2조각), build 스크립트도 갱신 → `projects/<slug>.yaml` 를 덮어씀.
2. **첫 15초 (인트로 다시 쓰기)**
   - 첫 문장 = 썸네일 큰 숫자의 답 또는 가장 센 숫자(예: "일본 월급은 30년 동안 거의 그대로였습니다 — …").
   - 첫 15초 안에 판 3개 이상(판 하나 4~5초, 한글 20~25자). 인사·채널 소개·배경 설명은 30초 이후.
   - 약 25~35초 지점에 "이런 계산 매주 올립니다. 구독해 두시면 다음 편도 받아 보실 수 있어요." 류 한마디(판 하나).
   - 썸네일 숫자가 첫 10초 화면에 그대로 보이게.
3. **제목** — 검색어를 맨 앞에, 그 뒤 숫자·대상. "(이거 한편으로 끝)", "/ 틀어놓고 듣는", 키워드 나열 금지. 썸네일 문구와 다른 말.
   검색어: 일본=`일본 잃어버린 30년`, 스위스=`스위스 부자 이유`, 사우디=`사우디 석유`, 아르헨티나=`아르헨티나 경제 몰락`.
   제목 후보 3개를 head.yaml 주석에 남기고 1개를 title 로. tags 첫머리에 검색어. summary(설명란 첫 2줄)도 검색어로 시작.
4. **쇼츠 2개** — `projects/<slug>_short1.yaml`, `_short2.yaml`. 형식은 `projects/demo_short_coffee.yaml`·`shorts/make_short.py`(beats: hook·twist·core·pov·todo·end, 장면 kind: hook·number·list·reveal) 를 따른다.
   - 길이 40~60초(make_short 가 40~50초를 권장하면 45~55초 목표). 본편에서 가장 센 숫자 한 묶음씩(두 쇼츠는 다른 소재).
   - 첫 줄 hook 에 숫자. 마지막 end 줄: "전체 이야기는 본편 「<본편 제목 앞부분>」에서 보실 수 있어요." 
   - voice: `{name: 여의도여자, speed: 1.0}` (backend 는 auto). sources 는 본편 sources 에서 필요한 것만 복사(verified: true 유지).
   - 쇼츠는 더빙·렌더하지 않는다. `python3 -c "import yaml;yaml.safe_load(open('projects/<slug>_short1.yaml'))"` 로 문법만 확인하고, make_short.py 에 대본만 점검하는 옵션(--check, --lint 등)이 있으면 그것도 돌린다.
5. **썸네일 2개 다시 만들기** — `projects/<slug>_parts/make_thumb.py` 를 새 규칙으로 고쳐 A·B 두 후보(1280×720):
   - 대비 구조 하나(A vs B / 숫자 두 개 / 전·후 / 1등·꼴찌). A 와 B 는 서로 다른 대비 구조나 다른 숫자로.
   - 큰 숫자 하나 + 글자 6자 이하(숫자·단위 제외). 추상어("진짜 이유", "진짜일까?", "이때 온다") 금지.
   - 밝은 배경, 편마다 다른 색: 일본=흰색(빨강 포인트), 스위스=파랑, 사우디=노랑, 아르헨티나=민트/하늘. 어두운 배경 + 빨간 붓 밑줄 금지. 채널 배지·'1시간 몰아보기' 칩 금지. 개미 마스코트는 작게, 표정이 맞을 때만(`/home/user/hf/thumb/assets/mascot/` 또는 video-studio assets 의 포즈 PNG). 실존 인물 얼굴 금지. 오른쪽 아래 재생시간 자리 비우기.
   - 숫자는 본편 sources.facts 에 있는 것만.
   - 결과 `neural-studio/assets/thumbs/<slug>_thumb_A.png`·`_B.png` 덮어쓰기, Read 로 직접 보고 고치기. 작은 크기(320×180)로 줄여서도 읽히는지 확인.
6. **비교 이미지** — 같은 주제 조회수 높은 다른 채널 썸네일 3개 + 우리 A·B 를 한 장에 나란히(2×3 격자, 각 칸 아래 채널명·조회수 작게).
   - 찾기: `yt-dlp "ytsearch15:<검색어>" --flat-playlist --print "%(id)s|%(view_count)s|%(channel)s|%(title)s"` → 조회수 상위 3개(우리 채널 '월급쟁이 재테크 스킬' 제외), 썸네일 `https://i.ytimg.com/vi/<id>/hqdefault.jpg` 를 curl 로 받기(새 빈 폴더 `/tmp/cmp_<slug>/` 에).
   - PIL 로 합쳐 `neural-studio/assets/thumbs/<slug>_compare.jpg`(가로 1920 안팎, 1MB 이하). 내부 검토용 — 다른 채널 썸네일은 이 비교 이미지에만 쓴다.
7. **점검** — `python3 projects/<slug>_parts/build_<slug>.py` → `python3 tools/series_lint.py projects/<slug>.yaml` 가 **통과**하고 예상 길이 11~14분일 때까지. (series_lint 의 "첫 4장면에 ?" 규칙은 첫 문장이 답이어도 2~4번째 판에 질문을 하나 두면 된다.)

## 하지 말 것
- make_editorial.py / make_short.py 로 더빙·렌더 금지(CPU 는 메인 세션이 씀). `--stills` 금지.
- git commit/push 금지. 다른 편 폴더, tools/·editorial/·shorts/ 코드, docs/ 규칙 문서 수정 금지.
- 디스크가 빠듯하다(여유 약 3.9GB). 큰 파일 만들지 말 것, 임시 파일은 /tmp/cmp_<slug>/ 에만.

## 보고 (마지막 메시지, 한국어, 짧게)
slug · 제목(+후보 2개) · 장면 수 · 예상 길이 · 챕터 · 첫 문장 · 썸네일 A/B 각각의 대비 구조와 문구 · 비교 이미지 경로 · 쇼츠 2개(파일·첫 줄·예상 초) · 재사용한 문장 수 대략 · 확인이 더 필요한 숫자/주장 · lint 결과.
