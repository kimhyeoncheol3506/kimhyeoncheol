# wadda-shorts — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside). 이 문서는 클라우드에서 다른 점만 적는다.

## 공통 설치 (세션마다 한 번, 있으면 생략)
```bash
which ffmpeg ffprobe || (apt-get update && apt-get install -y ffmpeg)
apt-get install -y fonts-noto-cjk   # 한글 폰트가 깨질 때만
```
- `python` 대신 `python3`, 경로 구분은 `/`. `.bat`/`.ps1`/`explorer.exe`/`Start-Sleep`/`chcp 65001` 은 쓰지 않고 셸에서 바로 실행한다(오래 걸리면 백그라운드 실행 후 로그 확인).
- 스크립트가 PATH의 ffmpeg를 못 찾으면 `which ffmpeg` 로 위치를 확인한다(스크립트의 WinGet 탐색은 리눅스에서 그냥 건너뜀).
- 썸네일(`scripts/batch/thumbs2.py`): `.venv\Scripts\python.exe` 대신 `python3 -m pip install "opencv-python-headless<5" numpy` 후 `python3 .claude/skills/wadda-shorts/scripts/batch/thumbs2.py`. 모델은 `scripts/models/yunet.onnx`, `sface.onnx`(저장소에 있음, 해시는 `.claude/skills/ASIDE_MANIFEST.json`).
- `notify.ps1`, `run_all.ps1` 은 쓰지 않는다. 다운로드 끝난 뒤 `python3 batch.py` 를 직접 실행하고, 알림 대신 마지막 결과표로 보고한다.
- TEMP/TMP 지정은 필요 없다(리눅스 /tmp 사용).

## 유튜브 다운로드
- `python3 -m pip install -U yt-dlp` 후 `yt-dlp` 사용. 클라우드는 데이터센터 IP라 "Sign in to confirm you're not a bot" / 403 / 자막 없음으로 막히기 쉽다.
- 막히면 재시도로 버티지 말고 멈춘 뒤, **"유튜브 다운로드는 PC Remote Control 세션에서 해 주세요"** 라고 안내한다(필요한 URL·구간 목록은 표로 남긴다). 쿠키·로그인 정보는 받지 않는다.
- 이 스킬은 구간 다운로드(`dl.py`, `find_sources.py`)가 핵심이라 막히면 **기획·구간 선택(segments.json)까지만** 클라우드에서 하고, 다운로드·렌더는 PC Remote Control 로 넘긴다.

## 음성
- 이 스킬은 원본 대사를 쓰므로 TTS가 필요 없다.

## 결과물
- 결과 폴더는 `C:\Users\Admin\Desktop\...`/Downloads 대신 저장소 안 작업 폴더(`output/`)에 둔다. 100MB 넘는 mp4는 커밋 금지 → `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart out.mp4` 로 45MB 이하로 줄여 커밋.
- 업로드는 하지 않는다(사용자가 명령할 때만, 그리고 업로드는 PC).
- 업로드(`shorts-upload`)는 PC 전용이다.
