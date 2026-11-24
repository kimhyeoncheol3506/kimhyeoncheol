# mystery-cartoon — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside). 이 문서는 클라우드에서 다른 점만 적는다.

## 공통 설치 (세션마다 한 번, 있으면 생략)
```bash
which ffmpeg ffprobe || (apt-get update && apt-get install -y ffmpeg)
apt-get install -y fonts-noto-cjk   # 한글 폰트가 깨질 때만
```
- `python` 대신 `python3`, 경로 구분은 `/`. `.bat`/`.ps1`/`explorer.exe`/`Start-Sleep`/`chcp 65001` 은 쓰지 않고 셸에서 바로 실행한다(오래 걸리면 백그라운드 실행 후 로그 확인).
- 스크립트가 PATH의 ffmpeg를 못 찾으면 `which ffmpeg` 로 위치를 확인한다(스크립트의 WinGet 탐색은 리눅스에서 그냥 건너뜀).

## 엔진별
- **C toon2d (클라우드 권장, 가장 빠름)**:
  ```bash
  cd .claude/skills/mystery-cartoon/kits/toon2d
  python3 -m pip install -r requirements.txt imageio-ffmpeg Pillow
  python3 t2d.py doctor   # skia 가 libEGL 을 못 찾으면: apt-get install -y libegl1 libgl1 libfontconfig1
  ```
  venv 없이 시스템 python3 사용. `PYTHONUTF8=1`. 렌더는 `--workers $(nproc)`, 명령 제한시간이 짧으면 `--budget 200` 으로 DONE 까지 반복.
- **B 스틱맨(Remotion)**: `engine/` 에서 `npm install`. `--gl=angle` 대신 `--gl=swangle`(GPU 없음), `--concurrency=$(nproc)`. 느리면 C로 바꾸자고 제안.
- **A 3D 콩머리(three.js)**: `CHROME=/opt/pw-browsers/chromium` 계열 경로를 쓰거나 render.mjs 대신 미리 설치된 Playwright(`require('playwright')`)로 띄운다. `playwright install` 은 하지 않는다. CPU 렌더라 매우 느리므로 짧은 구간만.

## 음성 (여의도여자 = PC 전용)
- 여의도여자는 PC의 Voicebox(`127.0.0.1:17493`)에서만 된다. 클라우드에는 없으므로 대체 TTS를 쓴다:
  `python3 -m pip install edge-tts` → `edge-tts --voice ko-KR-SunHiNeural --rate=+8% -f script.txt --write-media voice.mp3 --write-subtitles voice.vtt` (남성은 `ko-KR-InJoonNeural`).
  edge-tts가 막히면 `gTTS`, 그것도 안 되면 무음+자막으로 만든다.
- 결과 보고(마지막 결과표)에 **"음성: 대체 TTS(여의도여자 아님) — PC에서 다시 더빙 필요"** 라고 반드시 알린다.
- 최종본을 여의도여자 목소리로 원하면 PC Remote Control 세션에서 같은 스킬을 돌리라고 안내한다.
- `kits/make_voice.py` 는 Voicebox 전용이라 클라우드에서 쓰지 않는다. 대체 TTS 결과로 `timings.json` 을 만들 때는 edge-tts 자막(vtt) 시간을 쓰거나, 역사 쇼츠용 `.claude/skills/history-truth-shorts/tools/cloud_voice.py` 를 그대로 쓸 수 있다(그 스킬의 CLOUD.md 참고).

## 결과물
- 결과 폴더는 `C:\Users\Admin\Desktop\...`/Downloads 대신 저장소 안 작업 폴더(`output/`)에 둔다. 100MB 넘는 mp4는 커밋 금지 → `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart out.mp4` 로 45MB 이하로 줄여 커밋.
- 업로드는 하지 않는다(사용자가 명령할 때만, 그리고 업로드는 PC).

## 뉴럴서랍 브랜치에서 더한 점 (2026-11-20 설치 때 적은 내용 보존, 2026-11-22 Aside 원본 동기화 때 옮김)
- **대체 음성(이 저장소 우선)**: 이 저장소에는 여의도여자와 같은 엔진·프리셋인 Qwen3-TTS(Sohee)가 있다: `bash tools/setup_qwen_tts.sh`(10~15분, 약 9GB 메모리) → `facetube/voice.py` · `tools/qwen_tts_worker.py`. edge-tts 보다 여의도여자에 가깝다. 그래도 PC Voicebox 녹음이 아니므로 "PC 재녹음 필요"는 똑같이 적는다. 결과는 make_voice.py 와 같은 형식(voice.wav·script.txt·timings.json)으로 맞춘다.
- **듣기 검수**: 내규칙 그대로 `tools/voice_audit.py` 로 문장마다 두 번 받아 적어 0건까지 고친다.
- **C toon2d 검증 기록(2026-11-20)**:
  - 실행 결과: doctor OK(libegl1·libgl1·libfontconfig1 설치 후). 데모 `t2d.py silent examples/demo --script examples/demo/script.txt --duration 15` 다음 plan 15.05초·4장면, stills 10장 정상.
  - 오류: words.json 이 없으면 plan 이 실패한다. silent 또는 words 를 먼저 돌린다.
  - 무시해도 되는 경고: `Fontconfig warning ... reset-dirs`.
- **B 스틸**: `stills_win.mjs` 는 Windows 용이다. 원본 `scripts/stills.mjs` 를 쓰고 경로만 맞춘다.
- **A**: `CHROME` 을 비워 두면 render.mjs 의 `executablePath: process.env.CHROME` 이 Playwright 기본 chromium 으로 실행된다.
- **결과물**: 최종본은 `release/<주제>/` 세트(영상·폰용·썸네일·유튜브.txt·버전기록.md)로 낸다(`.claude/skills/video-release/SKILL.md`). 영상 mp4 는 `.gitignore`(release/**/*.mp4)로 커밋되지 않는다.
- **작업 위치**: 스킬 폴더는 읽기 전용으로 두고 scratchpad 에 복사해서 작업한다.
- **효과음(2026-11-24)**: 이 저장소 `assets/sfx/` 에 CC0 효과음 450개가 있다(크레딧 불필요, `assets/sfx/catalog.json`). 카툰용으로 boing·squeak·horn·laughter 도 들어 있으니 toon2d 효과음이 모자라면 여기서 고른다.
