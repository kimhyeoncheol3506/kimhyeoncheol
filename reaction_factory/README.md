# 해외반응 숏폼·롱폼 원클릭 생성기 (Reaction Factory)

키워드나 주제 하나로 **소스 탐색 → 원본 다운로드 → Claude 대본 → AI 음성 → 자막 → 자동 컷편집 → MP4**까지 한 번에 만듭니다.

```
python main.py auto --yes        # 주제 자동 선택부터 완성 영상까지 '딸깍'
```

---

## 1. 전체 구조

```
 ┌───────────┐   ┌──────────────┐   ┌────────────────┐   ┌──────────────┐   ┌──────────────┐
 │ topics.py │──▶│ downloader.py│──▶│script_generator│──▶│ tts_engine.py│──▶│  editor.py   │
 │ 주제 100개 │   │ 탐색·스코어링 │   │ Claude 대본     │   │ 세그먼트 TTS │   │ FFmpeg 조립  │
 │ 자동 매칭  │   │ 영상·자막·프레임│   │ (구조화 JSON)   │   │ + 타임라인    │   │ + subtitles.py│
 └───────────┘   └──────────────┘   └────────────────┘   └──────────────┘   └──────────────┘
        ▲                                                                           │
        └──────────── main.py (CLI · 대화형 모드 · output/<run_id>/project.json 로 이어하기) ◀┘
```

| 단계 | 모듈 | 하는 일 |
|---|---|---|
| 1. 소스 탐색 | `downloader.py` | YouTube Data API(또는 키 없으면 yt-dlp)로 최근 N일 영상 검색 → **구독자 ≤ 5만 & 조회수 터진 영상**을 점수화(조회 속도 45% · 구독자 대비 조회수 40% · 참여율 15%) → 랭킹 JSON + 상위 10개 썸네일 저장 |
| 1-2. 다운로드 | `downloader.py` | mp4(≤1080p), 자막(원어/영어/한국어, 타임스탬프), 메타데이터, 챕터, **많이 다시 본 구간(heatmap)** |
| 1-3. AI 이미지 선택 | `frame_selector.py` | 화면 전환(scene change) 기반 후보 사진 20장 → **Claude 비전**이 장면 설명·반응 강도·썸네일 점수·사용 가능 여부 평가 → 대본·썸네일·빈 구간 채우기에 사용 |
| 2. 주제 DB | `topics.py`, `data/topics.json` | 10개 카테고리 × 10 = **100개 주제**와 랭킹, 검색어, 후킹 앵글. 구글 트렌드 매칭으로 자동 선택, 실제 검색 결과로 점수 재보정 |
| 3. 대본 | `script_generator.py` | Claude 가 **[10% 차별화 + 후킹 + 본문 + 아웃트로]** 구조의 롱폼·숏폼 대본을 JSON 스키마로 생성. 컷마다 **나레이션 / 원본 반응 / 인물 더빙** 중 하나를 고르고, 사진(프레임 카탈로그 기반)·효과음·화면 문구·컷편집 가이드까지 지정. 제목 후보·썸네일 문구·설명란·태그·고정 댓글 포함 |
| 4. 음성·자막 | `tts_engine.py`, `subtitles.py` | 세그먼트별 TTS(edge 무료 / ElevenLabs / Typecast / CLOVA) → **무음 제거**(앞뒤 무음 + 문장 사이 긴 쉼 압축, 단어 타이밍 자동 보정) → **캐릭터별 목소리**(해설자·등장인물마다 다른 목소리) → 단어 단위로 맞춘 `.srt` + 디자인된 `.ass`(더빙 자막엔 인물 이름표) |
| 5. 편집 | `editor.py`, `sfx.py` | 원본 컷 + 나레이션(원본 소리 덕킹) + 원본 반응(번역 자막) + 인물 더빙 + **효과음 자동 삽입** + **빈 구간 채우기**(같은 장면 반복 시 AI 추천 사진으로 교체) + 상단 배너/제목 + BGM + -14 LUFS → **롱폼 1920×1080 / 숏폼 1080×1920 MP4**, AI 썸네일, 업로드 문구, **검수용 편집 프로젝트(FCPXML)** |
| 진행 보드 | `dashboard.py` | 01 영상 자료 → 02 대본 → 03 목소리 → 04 사진·편집 → 05 완성 단계별 상태와 **제작·전달 결과**(목소리 길이·무음 제거량·인트로 첫 문장 길이·사진/자막/효과음 수) + 후킹이 늘어지면 경고 |

### 폴더

```
reaction_factory/
├── main.py              # 진입점 (CLI + 대화형 '딸깍' 모드)
├── config.py            # .env 로딩, 경로, ffmpeg 찾기
├── downloader.py        # 탐색·스코어링·다운로드·자막 파싱
├── frame_selector.py    # 장면 전환 사진 추출 + Claude 비전 평가
├── sfx.py               # 효과음 (assets/sfx 파일 또는 내장 합성음)
├── dashboard.py         # 단계별 진행 보드 + 제작·전달 결과
├── speech_text.py       # 자막 표기 → TTS 읽기 변환(숫자·영어·기호)
├── voice_qa.py          # 번역투·문어체·감탄사 더빙·더빙 길이 검사
├── tests/               # 읽기 변환·검수 회귀 테스트
├── topics.py            # 주제 DB, 자동 매칭, 구글 트렌드, 점수 재보정
├── script_generator.py  # Claude 대본 (Pydantic 스키마)
├── tts_engine.py        # TTS 공급자 + 타임라인
├── subtitles.py         # SRT / ASS 자막
├── editor.py            # FFmpeg 컷편집·조립·썸네일
├── utils.py
├── data/topics.json     # 주제 100개
├── data/pronunciation.json  # 사용자 발음 사전
├── assets/fonts/        # 자막 폰트(.ttf/.otf)를 넣는 곳
├── assets/bgm/          # 배경음악 mp3
├── assets/sfx/          # 효과음 교체용 (whoosh/pop/ding/boom/rise/shutter .mp3|.wav)
├── input_source/        # <영상ID>/video.mp4, transcript.json, meta.json, frames/, frames.json(AI 평가)  ·  _discovery/ 랭킹+썸네일
├── scripts/             # <run_id>.json (편집기용), <run_id>.md (사람용 대본·컷편집 가이드)
├── audio/               # <run_id>/<long|short>/seg_*.mp3, narration_full.mp3, timeline.json
└── output/              # <run_id>/<long|short>/*_final.mp4, subtitles.srt/.ass, thumbnail.jpg, upload.txt
```

---

## 2. 빠른 시작 (10분)

### ① 준비물
- **Python 3.10 이상** — https://www.python.org/downloads/ (Windows 설치 시 *Add python.exe to PATH* 체크)
- ffmpeg 는 따로 설치하지 않아도 됩니다(`imageio-ffmpeg` 가 자동 제공). 이미 설치돼 있으면 그걸 씁니다.

### ② 설치
```bash
cd reaction_factory
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

### ③ API 키 넣기
```bash
cp .env.example .env        # Windows: copy .env.example .env
```
`.env` 를 메모장으로 열고:

| 키 | 필수? | 발급 |
|---|---|---|
| `ANTHROPIC_API_KEY` | **필수** | https://console.anthropic.com → API Keys |
| `YOUTUBE_API_KEY` | 권장 | https://console.cloud.google.com → 프로젝트 만들기 → *API 및 서비스 → 라이브러리* 에서 **YouTube Data API v3** 사용 설정 → *사용자 인증 정보 → API 키 만들기* |
| `TTS_PROVIDER` | 선택 | 기본 `edge`(무료, 키 불필요). 고품질은 `elevenlabs` / `typecast` / `clova` 와 해당 키 |

> YouTube 키가 없으면 yt-dlp 검색으로 대체합니다. 이때 유튜브가 "봇 확인"을 요구하면 `.env` 에 `YTDLP_COOKIES_FROM_BROWSER=chrome` 을 넣으세요(크롬에 유튜브 로그인 상태).

### ④ 폰트 (자막이 □□ 로 나오면)
`assets/fonts/` 에 한글 폰트 파일을 넣고 `.env` 의 `SUBTITLE_FONT` 를 그 폰트 이름으로 바꾸세요.
추천: [Pretendard](https://github.com/orioncactus/pretendard), [Noto Sans KR](https://fonts.google.com/noto/specimen/Noto+Sans+KR), 굵은 예능체는 [Black Han Sans](https://fonts.google.com/specimen/Black+Han+Sans).
Windows 기본 폰트를 쓰려면 `SUBTITLE_FONT=Malgun Gothic`.

### ⑤ 실행
```bash
python main.py
```
주제 고르기 → 기간·구독자 상한 → 영상 번호 → 형식(롱폼/숏폼/둘 다) 순서로 묻고, 끝나면 `output/<run_id>/` 에 결과가 생깁니다.

---

## 3. 명령어

```bash
# 주제
python main.py topics                       # TOP 20
python main.py topics --category all        # 카테고리별 TOP 10 전부
python main.py topics --category k_food
python main.py topics --match "korean corn dog"        # 문장 → 주제 자동 매칭
python main.py topics --recalibrate T001    # 실제 검색 결과로 점수 재계산(랭킹 갱신)

# 소스 탐색 (랭킹 + 썸네일 10장 → input_source/_discovery/)
python main.py discover --topic 1
python main.py discover -q "korean street food reaction" -q "외국인 길거리 음식 반응" --days 3 --max-subs 30000

# 완전 자동 (주제 자동 → 탐색 → 상위 영상으로 제작)
python main.py auto --yes
python main.py auto --topic T061 --sources 3 --minutes 10 --yes     # 원본 3개를 엮은 10분 롱폼
python main.py auto --format short --yes                            # 쇼츠만

# 특정 영상으로 바로 제작 (유튜브 URL/ID 또는 내 mp4 — 같은 이름의 .srt 가 있으면 자막도 사용)
python main.py make --video https://youtu.be/XXXXXXXXXXX --topic 1
python main.py make --video ./my_clip.mp4 --format short --extra "가격 비교를 꼭 넣어줘"

# 중간에 끊겼거나, 대본을 고친 뒤 음성/편집만 다시
python main.py resume --run 20261017_101500_삼겹살_첫_경험
python main.py resume --run 20261017_101500_삼겹살_첫_경험 --from tts
```

**대본 직접 수정 → 재편집:** `scripts/<run_id>.json` 의 `narration`, `clip_start/clip_end`, `on_screen_text` 등을 고치고 `resume --from tts` 하면 바뀐 내용으로 다시 만듭니다. (`.md` 는 보기용)

---

## 4. 결과물

```
output/<run_id>/
├── project.json             # 진행 상태 (이어하기용)
├── long/  long_final.mp4    # 1920x1080, 업로드용
│          subtitles.srt     # 유튜브에 따로 올릴 수 있는 자막
│          subtitles.ass     # 영상에 구워진 디자인 자막
│          thumbnail.jpg     # AI 썸네일 점수 1위 사진 + 썸네일 문구
│          upload.txt        # 제목·제목 후보·설명란(출처 포함)·태그·고정 댓글
│          report.json       # 컷·사진·효과음·더빙·자막 줄 수
│          edit_project/     # 검수용: segments/*.mp4(컷별, 자막 없음) + timeline.fcpxml + subtitles.srt
└── short/ short_final.mp4   # 1080x1920 (흐린 배경 + 원본 + 상단 제목 + 배너)
```

---

## 5. 동작 원리 메모

- **가성비 점수**(`downloader.compute_score`): `0.45·log(시간당 조회수)` + `0.40·log(조회수/구독자)` + `0.15·참여율`, 0~100점. 구독자 대비 3배 이상이면 🔥떡상, 시간당 1천 회 이상이면 ⚡급상승 표시. 가중치는 함수 안에서 바로 조정할 수 있습니다.
- **YouTube API 할당량**: 검색어 1개당 약 102 유닛(search 100 + videos 1 + channels 1). 하루 기본 10,000 유닛 → 검색어 약 90개.
- **대본**: `claude-opus-5-5` + 구조화 출력(Pydantic 스키마)이라 편집기가 바로 읽습니다. 정책상 거절되면 서버가 대체 모델로 자동 재시도(`fallbacks: "default"`)합니다. 원본 타임코드는 생성 후 실제 길이 안으로 자동 보정됩니다.
- **싱크**: 세그먼트마다 TTS 를 따로 만들어 실제 길이를 잰 뒤 그 길이만큼 원본을 잘라 붙입니다. edge / ElevenLabs 는 단어 단위 타이밍을 받아 자막을 맞춥니다.
- **편집 레이아웃**: narration 구간은 원본 소리를 12%로 줄이고 나레이션을 얹고, original 구간은 원본 리액션 소리 그대로 + 노란 번역 자막 + 살짝 줌, dub 구간은 원본 소리 25% + 인물 목소리 더빙 + 이름표 자막. frame 구간은 사진 줌인.
- **무음 제거**: `silencedetect`(-50dB)로 쉼을 찾아 앞뒤 무음과 0.25초(`MAX_PAUSE`)보다 긴 쉼을 잘라 냅니다. 말끝 잔향 0.15초는 남겨 '~요'가 잘리지 않고, 단어 타이밍도 잘린 만큼 당겨서 자막 싱크가 유지됩니다.
- **캐릭터 목소리**: edge 는 한국어 보이스 3종을 성별·나이별 피치/속도로 변형해 인물마다 다르게 배정합니다. ElevenLabs·Typecast·CLOVA 는 `.env` 의 `CHARACTER_VOICES_MALE/FEMALE` 에 보이스 ID 를 넣으면 순서대로 배정됩니다.
- **AI 사진 평가 비용**: 원본 1개당 비전 호출 1번(512px 사진 20장, effort=low).
- MoviePy 대신 FFmpeg 를 직접 호출합니다. 긴 영상에서 훨씬 빠르고 메모리를 적게 쓰며, ASS 자막(libass)을 그대로 구울 수 있기 때문입니다.

## 6. AI 음성이 '바보처럼' 들리지 않게 하는 장치

| 흔한 원인 | 이 프로그램의 처리 | 위치 |
|---|---|---|
| 숫자를 엉뚱하게 읽음 ("3개"→삼 개, "6월"→육월, "12,000원"→십이 영영영) | 자막은 그대로 두고 음성만 실제 발음으로 변환: 세 개, 유월, 만 이천 원, 스무 살, 첫 번째, 두 시 삼십 분, 삼십 퍼센트, 오 달러, 이십 대 | `speech_text.py` |
| 영어·약어를 이상하게 읽음 (KFC, BTS, Oh my god) | 사전 → 한글 발음, 대문자 약어 → 알파벳 한글 읽기(케이티엑스), 못 바꾼 단어는 경고 | `speech_text.py`, `data/pronunciation.json` |
| ㅋㅋ·이모지·~·… 를 읽거나 이상하게 끊음 | 읽기 전에 제거/쉼표로 변환 | `speech_text.py` |
| 모든 문장이 같은 속도·높이(기계 박자) | 문장마다 따로 합성, 감정(emotion)·질문/감탄에 따라 속도·피치 변화, 문장 사이 0.14초 숨 | `tts_engine.synth_expressive` |
| 번역기 말투(그녀는, ~것이다, 매우) / 해설이 문어체(~했다.) | 대본 직후 검사 → Claude 가 해당 대사만 구어체로 재작성 | `voice_qa.py`, `script_generator.polish_speech` |
| '와!', 'Oh my god!' 같은 감탄사를 AI 가 연기 | 짧은 감탄사 더빙은 자동으로 **원본 소리 + 번역 자막**으로 전환 | `voice_qa.demote_exclamation_dubs` |
| 더빙이 인물의 입보다 길게 계속됨 | 원본 발화 길이에 맞춰 최대 1.18배까지 자연스럽게 당기고, 그래도 길면 경고 | `tts_engine.fit_duration` |
| 목소리마다 음량이 들쭉날쭉 | 세그먼트별 -16 LUFS 로 통일 + 저음 잡음 제거 | `tts_engine.normalize_loudness` |
| 더빙 밑에 원본 목소리가 크게 겹침 | 더빙 구간 원본 음량 25% (`DUB_DUCK_VOLUME`, 더 낮추려면 0.15) | `editor.py` |

틀리게 읽는 단어를 발견하면 `data/pronunciation.json` 에 `"표기": "읽기"` 를 추가하세요(가장 먼저 적용).
변환 규칙 회귀 테스트: `python tests/test_speech_text.py`, `python tests/test_voice_qa.py`.

## 7. 검수 20분 루틴

1. 마지막 **제작·전달 결과** 패널의 ⚠ 경고부터 확인(예: 숏폼 인트로 첫 문장이 3초를 넘으면 이탈 위험).
2. `scripts/<run_id>.md` 로 대본·컷 구성을 훑고, 고칠 문장이 있으면 `scripts/<run_id>.json` 을 수정 → `resume --from tts`.
3. 컷 단위로 손보고 싶으면 `edit_project/timeline.fcpxml` 을 **DaVinci Resolve(무료)** 로 열기(파일 → 가져오기 → 타임라인).
   CapCut/Premiere 는 `segments/` 영상을 순서대로 놓고 `subtitles.srt` 를 불러오면 됩니다.
4. 효과음이 마음에 안 들면 `assets/sfx/` 에 같은 이름(`whoosh.mp3` 등)으로 넣고 `resume --from edit`.

## 8. 문제 해결

| 증상 | 해결 |
|---|---|
| `Sign in to confirm you're not a bot` | `YOUTUBE_API_KEY` 설정, 또는 `YTDLP_COOKIES_FROM_BROWSER=chrome` |
| 자막 글자가 □ 로 나옴 | ④ 폰트 설정 |
| `조건에 맞는 영상이 없습니다` | `--days 7 --max-subs 100000 --min-views 1000` 처럼 조건 완화 |
| edge TTS 오류 | 인터넷 연결 확인. 임시로 `TTS_PROVIDER=silent` 로 편집만 테스트 가능 |
| 대본이 잘림(max_tokens) | `--minutes` 를 줄이거나 `--sources` 를 줄이기 |
| yt-dlp 다운로드 실패 | `pip install -U yt-dlp` (유튜브 변경에 맞춰 자주 업데이트됨) |

## 9. 저작권·정책 주의

남의 영상을 쓰는 해외반응 콘텐츠는 저작권 신고·수익화 거절(재사용 콘텐츠) 위험이 있습니다.
- 가능하면 **원작자에게 사용 허락**을 받고, 설명란에 출처를 표기하세요(`upload.txt` 에 자동 포함).
- 원본을 길게 그대로 쓰지 말고, 나레이션·정보·편집으로 **변형을 충분히** 더하세요(대본의 '10% 차별화'는 최소치입니다).
- 직접 촬영본이나 허락받은 영상은 `make --video ./파일.mp4` 로 바로 쓸 수 있습니다.
