# 클라우드(리눅스) 환경에서 달라지는 점

`SKILL.md` 는 현철님 PC(Windows) 기준이다. 이 클라우드 컨테이너(리눅스, GPU 없음)에서 쓸 때는 아래만 바꿔 읽는다. `SKILL.md` 자체는 고치지 않는다.

## 1. 목소리 (가장 중요)
- **Voicebox(여의도여자)는 PC에만 있다.** 클라우드에는 Voicebox가 없어 `kits/make_voice.py` 를 그대로 쓸 수 없다.
- 클라우드에서는 **대체 TTS** 를 쓴다: 이미 깔린 Qwen3-TTS 엔진(`~/.cache/yeouido-tts`, `neural-studio` 의 여의도 목소리와 같은 엔진) 또는 edge-tts. **실제 Voicebox 여의도여자 목소리와 다르다.** 클라우드에서 만든 음성은 검수·미리보기용으로 표시하고, 최종본은 PC Voicebox로 다시 녹음하는 것을 기본으로 한다(현철님이 클라우드 목소리로 내보내도 된다고 하면 예외).
- 결과물 형식은 같게 맞춘다: `voice.wav`, `script.txt`, `timings.json`(단어 시작/끝).
- 음성 없이 그림만 확인할 때는 C 엔진의 `python3 t2d.py silent P` (무음 voice.wav + 읽기 속도 타이밍).

## 2. 명령과 경로
- `python` 대신 **`python3`**. venv·`PYTHONHOME` 정리는 필요 없고 `PYTHONUTF8=1` 만 붙인다.
- Windows 경로(`C:\...`), `explorer.exe`, `.bat`(CRLF) 실행은 쓰지 않는다. 오래 걸리는 작업은 `setsid nohup bash run.sh > log 2>&1 &` 로 백그라운드 실행하고 로그를 확인한다.
- 작업은 스킬 폴더가 아니라 세션 임시 폴더(예: `/tmp/claude-0/<작업이름>/`)에 키트를 복사해서 한다.
- `PATH` 에 nodejs 폴더를 따로 넣을 필요 없음(node 22 기본 설치).

## 3. 엔진별
- **C toon2d**: `pip install -r kits/toon2d/requirements.txt`(이 컨테이너는 `imageio-ffmpeg` 만 추가 설치하면 됐다) → `PYTHONUTF8=1 python3 t2d.py doctor`. 나머지 명령은 SKILL.md 그대로. `--workers` 는 `nproc` 에 맞춘다.
- **B Stick3D**: GPU가 없으므로 렌더·스틸 모두 **`--gl=swangle`** (`--gl=angle` 아님). 스틸은 원본 `scripts/stills.mjs`(리눅스 경로)를 쓰고 `stills_win.mjs` 는 쓰지 않는다. `engine/` 에서 `npm install` 필요(node_modules 미포함, 디스크 여유 확인).
- **A 3D 콩머리**: `CHROME` 환경변수를 주지 않는다 → Playwright **기본 chromium**(컨테이너에 미리 설치됨, `playwright install` 다시 하지 말 것)을 쓴다. 인자는 `--use-angle=swiftshader --enable-unsafe-swiftshader`(CPU WebGL, 프레임당 수 초). 풀 렌더는 `nohup node render.mjs frames "0-N" &` 로.

## 4. 디스크
- 이 컨테이너는 쓰기 공간이 빠듯하다(1GB 안팎). B 엔진 `node_modules`, 프레임 jpg 폴더, 렌더 캐시는 끝나면 지운다.

## 5. 설치 확인 기록
- 2026-11-20: zip SHA256 일치(A21A4DC7…3FD79), 내용 그대로 설치. C 엔진 `doctor` OK(imageio-ffmpeg 추가 설치), `examples/demo` → `silent`(무음 21.4초) → `plan`(4장면·20비트·자막 26묶음) → `stills` 2장(1.0초·6.0초) 정상. 풀 렌더는 하지 않음.
