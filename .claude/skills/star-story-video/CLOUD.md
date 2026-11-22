# star-story-video — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside, PC 전용으로 작성됨). 클라우드에서는 **기획·대본·이미지·시험 렌더** 까지 하고, 최종 더빙·다운로드는 PC 로 넘기는 것이 기본이다.

## 공통 설치 (세션마다 한 번, 있으면 생략)
```bash
which ffmpeg ffprobe || (apt-get update && apt-get install -y ffmpeg)
apt-get install -y fonts-noto-cjk   # 한글 폰트가 깨질 때만
```
- `python` 대신 `python3`, 경로 구분은 `/`. `.bat`/`.ps1`/`explorer.exe`/`Start-Sleep`/`chcp 65001` 은 쓰지 않고 셸에서 바로 실행한다(오래 걸리면 백그라운드 실행 후 로그 확인).
- 스크립트가 PATH의 ffmpeg를 못 찾으면 `which ffmpeg` 로 위치를 확인한다(스크립트의 WinGet 탐색은 리눅스에서 그냥 건너뜀).
- 파이썬은 `C:\Users\Admin\.aside\runtime\bin\python.cmd` 대신 `python3`. 프로젝트 폴더는 저장소 안 `work/<멤버영문>/`.

## 스크립트에 박힌 PC 경로
- 일부 스크립트 상단 상수(`FF`, `YT`, `FONTS`, `BASE_IMG` 등)가 `C:\Users\Admin\...` 로 고정돼 있다. **원본 스크립트는 고치지 않는다.**
- 클라우드에서는 작업 폴더(프로젝트 폴더나 스크래치)에 복사본을 만들고 그 복사본의 상수만 바꿔 실행한다. 예:
  `sed -e "s#^FF = .*#FF = '$(dirname $(which ffmpeg))'#" -e "s#^YT = .*#YT = '$(which yt-dlp)'#" <원본.py> > <프로젝트>/_cloud_<이름>.py`
  (FONTS 는 `.claude/skills/star-story-video/assets/fonts` 로). 복사본은 커밋하지 않는다.
- `tools.py base-img` 의 `BASE_IMG` 는 PC 세션 폴더라 클라우드에 없다 → 복사본에서 `BASE_IMG` 를 `.claude/skills/star-story-video/assets/img` 로 바꾼다.

## BGM (팩에서 뺐음)
- `assets/bgm` 의 mp3 4개(Snowfall, My Dear One, Ripples In Time, takingflight)는 용량 때문에 팩에 없다. **PC 원본**(Aside 스킬 폴더 `star-story-video/assets/bgm`)을 쓴다.
- 클라우드에서 렌더해야 하면 BGM 없이 시험 렌더만 하고, "BGM 없음 — PC 원본으로 최종 렌더 필요" 라고 결과표에 적는다. 다른 곡을 임의로 받아 넣지 않는다.

## 음성 (여의도여자 = PC 전용)
- 여의도여자는 PC의 Voicebox(`127.0.0.1:17493`)에서만 된다. 클라우드에는 없으므로 대체 TTS를 쓴다:
  `python3 -m pip install edge-tts` → `edge-tts --voice ko-KR-SunHiNeural --rate=+8% -f script.txt --write-media voice.mp3 --write-subtitles voice.vtt` (남성은 `ko-KR-InJoonNeural`).
  edge-tts가 막히면 `gTTS`, 그것도 안 되면 무음+자막으로 만든다.
- 결과 보고(마지막 결과표)에 **"음성: 대체 TTS(여의도여자 아님) — PC에서 다시 더빙 필요"** 라고 반드시 알린다.
- 최종본을 여의도여자 목소리로 원하면 PC Remote Control 세션에서 같은 스킬을 돌리라고 안내한다.
- `scripts/tts.py` 는 Voicebox + Whisper 검수 전용이라 클라우드에서 실행하지 않는다. 대체 TTS 시험본은 `lines/` 에 줄별 wav 로 만들 수 있지만, 최종 업로드본은 PC 에서 `tts.py` 로 다시 만든다.

## 유튜브 다운로드
- `python3 -m pip install -U yt-dlp` 후 `yt-dlp` 사용. 클라우드는 데이터센터 IP라 "Sign in to confirm you're not a bot" / 403 / 자막 없음으로 막히기 쉽다.
- 막히면 재시도로 버티지 말고 멈춘 뒤, **"유튜브 다운로드는 PC Remote Control 세션에서 해 주세요"** 라고 안내한다(필요한 URL·구간 목록은 표로 남긴다). 쿠키·로그인 정보는 받지 않는다.

## 결과물
- 결과 폴더는 `C:\Users\Admin\Desktop\...`/Downloads 대신 저장소 안 작업 폴더(`output/`)에 둔다. 100MB 넘는 mp4는 커밋 금지 → `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart out.mp4` 로 45MB 이하로 줄여 커밋.
- 업로드는 하지 않는다(사용자가 명령할 때만, 그리고 업로드는 PC).
