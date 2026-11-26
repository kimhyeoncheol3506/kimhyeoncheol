# PC 재녹음 지시서 (2026-11-26, 매니저 작성)

현철님 PC에서 돌아가는 Claude 세션이 이 파일을 따라 하면 됩니다. Voicebox(여의도여자)는 PC에서만 됩니다.
**업로드·게시는 하지 않습니다.**

## 0. 준비
1. 이 저장소에서 `claude/funny-mendel-bng677` 브랜치를 받습니다: `git fetch origin claude/funny-mendel-bng677 && git checkout claude/funny-mendel-bng677 && git pull`
2. Voicebox 를 켭니다(`http://127.0.0.1:17493/profiles` 가 응답할 때까지 기다림).
3. 모든 빌드는 한 번에 하나씩 돌립니다.
4. 각 빌드에 `--note "PC Voicebox 재녹음(여의도여자)"` 를 붙이면 release 에 v2 세트가 생깁니다.

## 1. 롱폼 2편 (가로 neon)
| 대본 | release 폴더 |
|---|---|
| `projects/neon4_neon.yaml` | `release/제미나이4_네온_정리/` |
| `projects/opus56_neon.yaml` | `release/클로드_오퍼스56_루머_팩트체크/` |

- 빌드 명령: `python editorial/make_editorial.py <대본> --note "PC Voicebox 재녹음(여의도여자)"`
- 빌드가 끝날 때마다 `python tools/voice_audit.py output/<slug>/_work/tts --project <대본>` 를 돌립니다.
- 고칠 후보가 0건이 될 때까지 문장이나 `say_as` 를 고치고 다시 빌드합니다.

## 2. 쇼츠 3편 (가로로 빌드한 뒤 세로로 자름)
| 대본 | 세로 자르기 설정 |
|---|---|
| `projects/sh_answer4_neon.yaml` | `release/AI속이는_희미한글씨_쇼츠/short_spec.yaml` |
| `projects/sh_count100k_neon.yaml` | `release/클로드_10만세기_복수밈_쇼츠/short_spec.yaml` |
| `projects/sh_pickle_call_neon.yaml` | `release/피클AI_무단전화_13초침묵_쇼츠/short_spec.yaml` |

빌드 → 듣기 검수 0건 다음에 아래 순서로 처리합니다.
1. short_spec.yaml 을 고칩니다.
   - `out` 의 `_v1` 을 이번 버전(`_v2`)으로 바꿉니다.
   - `segs: [[0, <새 final.mp4 길이>]]` 로 새 영상 길이를 넣습니다.
2. `python tools/cut_short.py <short_spec.yaml>` 로 세로 영상을 만듭니다.
3. 폰용(720x1280)을 만듭니다: `ffmpeg -i <v2.mp4> -vf scale=720:1280 -c:v libx264 -crf 30 -c:a aac -b:a 96k <v2_폰용.mp4>`
4. 세로 썸네일을 만듭니다: `python tools/thumb_vertical.py <대본> <release 폴더>/<이름>_v2_썸네일.jpg`
5. 마지막으로 확인합니다.
   - 쇼츠는 60초 안이어야 합니다. 넘으면 대사를 줄입니다.
   - make_editorial 이 release 에 넣은 가로 mp4 는 세로본으로 덮어씁니다.

## 3. AI 안경 쇼츠 2편 (롱폼에서 잘라 만든 것)
1. `projects/glasses_neon.yaml` 롱폼을 먼저 재녹음해 빌드합니다. 결과는 `release/AI안경_시험커닝_가능할까/` v5 가 됩니다.
2. 새 롱폼 자막(`output/glasses_neon/subtitles.srt`)에서 쇼츠 구간을 다시 찾습니다.
   - 기준은 `release/AI안경_쇼츠/short1.yaml`·`short2.yaml` 의 구간과 같은 문장입니다.
   - 대조할 문장은 `release/AI안경_쇼츠/longform_v4.srt` 와 v1 쇼츠 .ass 에 있습니다.
   - 녹음이 달라지면 시각이 바뀝니다. 같은 문장이 시작·끝나는 새 시각으로 `segs` 를 고칩니다.
3. `src` 는 새 롱폼 v5, `srt` 는 새 자막, `out` 은 `_v2` 로 바꿉니다. 그다음 `python tools/cut_short.py release/AI안경_쇼츠/short1.yaml` 로 쇼츠1을 만들고, 쇼츠2도 같은 방법으로 만듭니다.
4. 쇼츠2 「수능, 이 안경 쓰면…」은 수능(11/19)이 지난 상태입니다. 날짜 표현이 틀리지 않았는지 다시 확인합니다.

## 4. 기록·커밋
- 각 release 폴더의 `버전기록.md` 에 v2 메모를 남깁니다.
  - "PC Voicebox 재녹음(여의도여자)"
  - 듣기 검수 결과
  - 쇼츠 길이
  - 올리기 전 확인표 5항목(.claude/skills/video-release/SKILL.md)
- mp4 는 커밋하지 않습니다(.gitignore). txt·jpg·ass·yaml·버전기록만 커밋하고, `claude/funny-mendel-bng677` 에 푸시합니다.
- 다 끝나면 이 클라우드 매니저 세션에 결과를 표로 알려 주세요: 편 · 길이 · 듣기 검수 · 경로.
