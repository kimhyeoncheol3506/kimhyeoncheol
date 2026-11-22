# star-compilation-video — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside). 이 스킬은 **다운로드가 전부**라 클라우드에서는 EDL(클립 목록·캡션) 기획까지 하고 컴파일은 PC 로 넘기는 것이 기본이다.

## 공통 설치 (세션마다 한 번, 있으면 생략)
```bash
which ffmpeg ffprobe || (apt-get update && apt-get install -y ffmpeg)
apt-get install -y fonts-noto-cjk   # 한글 폰트가 깨질 때만
```
- `python` 대신 `python3`, 경로 구분은 `/`. `.bat`/`.ps1`/`explorer.exe`/`Start-Sleep`/`chcp 65001` 은 쓰지 않고 셸에서 바로 실행한다(오래 걸리면 백그라운드 실행 후 로그 확인).
- 스크립트가 PATH의 ffmpeg를 못 찾으면 `which ffmpeg` 로 위치를 확인한다(스크립트의 WinGet 탐색은 리눅스에서 그냥 건너뜀).

## 스크립트에 박힌 PC 경로
- 일부 스크립트 상단 상수(`FF`, `YT`, `FONTS`, `BASE_IMG` 등)가 `C:\Users\Admin\...` 로 고정돼 있다. **원본 스크립트는 고치지 않는다.**
- 클라우드에서는 작업 폴더(프로젝트 폴더나 스크래치)에 복사본을 만들고 그 복사본의 상수만 바꿔 실행한다. 예:
  `sed -e "s#^FF = .*#FF = '$(dirname $(which ffmpeg))'#" -e "s#^YT = .*#YT = '$(which yt-dlp)'#" <원본.py> > <프로젝트>/_cloud_<이름>.py`
  (FONTS 는 `.claude/skills/star-story-video/assets/fonts` 로). 복사본은 커밋하지 않는다.
- `compile.py` 의 `OLD`, `WONI` 는 PC 세션 캐시 폴더라 클라우드에는 없다(없으면 새로 다운로드). `tts_queue.py` 는 PC 전용(Voicebox 잠금 파일)이라 클라우드에서 쓰지 않는다.

## BGM (팩에서 뺐음)
- `assets/statement.mp3`(Statement – NEFFEX)는 팩에 없다. **PC 원본**을 쓴다. `compile.py` 는 `MUSIC` 환경변수로 경로를 받으므로 PC 에서는 `MUSIC=<원본 경로>` 로 돌린다.
- 클라우드에서 시험 컴파일만 할 때는 BGM 없이 만들고 "Statement BGM 없음 — PC 에서 최종 컴파일" 이라고 알린다. 다른 곡으로 바꾸지 않는다.

## 유튜브 다운로드
- `python3 -m pip install -U yt-dlp` 후 `yt-dlp` 사용. 클라우드는 데이터센터 IP라 "Sign in to confirm you're not a bot" / 403 / 자막 없음으로 막히기 쉽다.
- 막히면 재시도로 버티지 말고 멈춘 뒤, **"유튜브 다운로드는 PC Remote Control 세션에서 해 주세요"** 라고 안내한다(필요한 URL·구간 목록은 표로 남긴다). 쿠키·로그인 정보는 받지 않는다.

## 고지
- 매번 한 줄로: 짜깁기 영상은 수익화가 안 될 수 있고 저작권 위험이 있다.

## 결과물
- 결과 폴더는 `C:\Users\Admin\Desktop\...`/Downloads 대신 저장소 안 작업 폴더(`output/`)에 둔다. 100MB 넘는 mp4는 커밋 금지 → `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart out.mp4` 로 45MB 이하로 줄여 커밋.
- 업로드는 하지 않는다(사용자가 명령할 때만, 그리고 업로드는 PC).
