# 클라우드(리눅스 컨테이너)에서 쓸 때 달라지는 점

SKILL.md 와 kits/ 는 현철님 PC(Windows) 기준 원본 그대로 둔다. 클라우드 세션에서는 이 문서대로 바꿔서 실행한다. 작업은 항상 세션 scratchpad 에 복사해서(스킬 폴더는 읽기 전용).

## 공통
- 파이썬은 `python3`(venv 권장: `python3 -m venv <tmp>/venv`). `PYTHONUTF8=1`.
- Windows 경로·`explorer.exe`·`.bat`(run_render.bat, run_b.bat) 는 쓰지 않는다. 같은 명령을 bash 로 직접 실행하고, 오래 걸리는 렌더는 백그라운드 실행(`run_in_background`) + 완료 알림으로 기다린다.
- 경로는 `/home/user/kimhyeoncheol/...` 또는 scratchpad 절대경로. `C:\...` 가 박힌 곳은 리눅스 경로로 바꿔서 쓴다.

## 목소리(가장 큰 차이)
- Voicebox(여의도여자)는 PC에만 있다. `kits/make_voice.py`(127.0.0.1:17493 Voicebox API)는 클라우드에서 동작하지 않는다.
- 대체: 이 저장소의 Qwen3-TTS(`bash tools/setup_qwen_tts.sh` 로 설치, `facetube/voice.py` · `tools/qwen_tts_worker.py`)로 문장별 음성을 만들고, voice.wav·script.txt·timings.json 형식을 make_voice.py 와 같게 맞춘다.
- **실제 목소리가 여의도여자와 다르다.** 클라우드에서 만든 음성은 '대체 목소리'라고 결과 보고·버전기록에 반드시 적는다. 최종 여의도여자 더빙은 PC 에서.
- 목소리 없이 그림만 확인할 때는 C 엔진의 `t2d.py silent <P> --script script.txt --duration 15`(무음 + 자막 타이밍).
- 듣기 검수 규칙(내규칙·`tools/voice_audit.py`)은 그대로 적용.

## C: toon2d (클라우드 검증됨, 2026-11-20)
- `pip install -r requirements.txt`(faster-whisper 는 선택, `--from timings.json` 쓰면 불필요).
- skia-python 은 시스템 라이브러리가 필요: `apt-get install -y libegl1 libgl1 libfontconfig1`(없으면 doctor 가 `libEGL.so.1` 없음으로 실패).
- 순서는 SKILL.md 와 같음: `python3 t2d.py doctor` → `words P --from timings.json`(또는 `silent`) → `plan P` → `stills P` → `render P --workers 2~4 --budget 500`(DONE 까지 반복) → `join P` → `check P`. 컨테이너 CPU 가 PC보다 적으니 `--workers` 는 `nproc` 이하로.
- `Fontconfig warning ... reset-dirs` 경고는 무시해도 된다.

## B: Stick3D
- `engine/` 에서 `npm install`. PATH 에 `C:\Program Files\nodejs` 추가는 불필요(리눅스 node 사용).
- 렌더는 GPU 가 없으므로 `--gl=swangle`: `npx remotion render <Id> out.mp4 --gl=swangle --concurrency=<nproc 이하>`.
- 스틸은 원본 `scripts/stills.mjs`(리눅스 경로 기준) 쪽을 쓰고 경로만 맞춘다. `stills_win.mjs` 는 Windows 용.

## A: 3D 콩머리(cartoon3d)
- `npm i playwright` 후 **`CHROME` 환경변수 없이** Playwright 기본 chromium 을 쓴다(컨테이너에 미리 깔려 있음, `playwright install` 금지). render.mjs 의 `executablePath: process.env.CHROME` 은 CHROME 이 비어 있으면 기본 chromium 으로 실행된다. 기본 chromium 을 못 찾으면 `CHROME=/opt/pw-browsers/chromium` 계열 경로를 지정.
- `node render.mjs frames "0-N"` 를 bash 로 직접(run_render.bat 대신). 프레임당 시간이 PC보다 길 수 있으니 먼저 짧은 구간으로 시험.
- 소리 합성 `audio.py`, 자막 번인(ffmpeg, Pretendard)은 동일. 마무리 loudnorm -14 LUFS.

## 결과물
- 최종본은 이 저장소 규칙대로 `release/<주제>/` 세트(영상·폰용·썸네일·유튜브.txt·버전기록.md)로 낸다(`.claude/skills/video-release/SKILL.md`). 업로드는 현철님 명령이 있을 때만.
