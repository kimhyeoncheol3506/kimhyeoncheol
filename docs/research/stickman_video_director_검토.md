# Stickman Video Director 검토와 도입 (2026-11-24)

- **출처**: X 글(@averyrunsai, 2026-11-22)과 GitHub kaomei/stickman-video-director(MIT, 커밋 1028782).
- **검토 방법**: 외부 저장소는 읽기만 했다. 스크립트·npm 은 실행하지 않았다.

## 도입한 것

### 1. CC0 효과음 450개 (13MB)
- 위치: `assets/sfx/`
- 들인 묶음: kenney interface·digital·impact·jingles, artisticdude swishes, owlish 종이·폰·카메라, 카툰 boing·squeak·horn·laughter
- 원본 sha256 과 대조했다(불일치 0).
- 라이선스 원문과 출처 증거: `assets/sfx/LICENSES/`
- 목록: `assets/sfx/catalog.json`

### 2. 효과음 코드
- `facetube/audio.py`
  - `sfx_pick()` 가 합성음 이름을 파일 묶음으로 바꾼다.
  - 같은 이름의 효과음이 반복되면 다른 파일로 돌려 쓴다.
  - 음량은 같은 이름의 합성음과 RMS 를 맞춰 기존 믹스 위계를 유지한다.
  - 파일 속 최고점이 장면 시각에 맞도록 최대 0.08초 앞당긴다.
- `style.yaml` neon 에 `sfx_pack: cc0` 를 넣었다. 대본에 `sfx_pack: null` 을 쓰면 예전 합성음으로 돌아간다.
- `editorial/make_editorial.py`: 빌드할 때 `_work/sfx_manifest.json` 을 남긴다.

### 3. 첫 3초 소리 검사
- `facetube/qc.py` 의 `opening_onset()`. 저쪽 수치(250~5000Hz, 20ms 창, -36dBFS 가 40ms 이어지는 시점, 첫 3초 안 -44dBFS 아래 0.6초)를 파이썬으로 다시 짰다.
- 기준은 0.2초다. 우리 최근 영상의 첫 소리는 0.14~0.16초라 통과한다.

### 4. 고정 댓글·음악 크레딧
- `facetube/youtube_txt.py` 에 두 칸을 추가했다.
  - `pinned_comment`: [📌 고정 댓글] 칸
  - `music_credits`: 설명란 🎵 음악 칸
- 제목 후보가 2개 미만이면 경고한다.

### 5. 규칙 문서
- 내규칙 2026-11-24 항목
- faceless-video 대본 5단계 점검
- video-release 올리기 전 확인표 5항목

## 안 한 것 (이유)
- **CC BY 효과음·Kevin MacLeod 음악**: 크레딧이 필요하고, 귀로 들어 보고 고르는 게 먼저다. `music_credits` 칸은 만들어 두었다.
- **스틱맨 전용 규칙**(모든 장면 3초 이하, 손팔 방향 등): 우리 neon 실측과 맞지 않는다.
- **Google Flow·ElevenLabs 연동**: 목소리는 여의도여자를 그대로 쓴다.

## 현철님 확인이 필요한 것
- **휙 소리 규칙 불일치**
  - `rules/editing.yaml` 은 "휙은 챕터 전환과 3장면에 1번"이다.
  - neon 빌드는 hook·title·part 를 뺀 모든 장면 전환에 휙(-16dB)을 넣는다.
  - 둘 중 하나로 맞춰야 한다.
- **새 효과음 미리듣기**: `docs/research/효과음_미리듣기_cc0.mp3`
  - 휙·스윽·팝·딩·쾅·틱·종이를 순서대로 3개씩 담았다.
