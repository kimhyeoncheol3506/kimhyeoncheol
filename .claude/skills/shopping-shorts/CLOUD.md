# shopping-shorts — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside). 이 문서는 클라우드에서 다른 점만 적는다.

## 공통 설치 (세션마다 한 번, 있으면 생략)
```bash
which ffmpeg ffprobe || (apt-get update && apt-get install -y ffmpeg)
apt-get install -y fonts-noto-cjk   # 한글 폰트가 깨질 때만
```
- `python` 대신 `python3`, 경로 구분은 `/`. `.bat`/`.ps1`/`explorer.exe`/`Start-Sleep`/`chcp 65001` 은 쓰지 않고 셸에서 바로 실행한다(오래 걸리면 백그라운드 실행 후 로그 확인).
- 스크립트가 PATH의 ffmpeg를 못 찾으면 `which ffmpeg` 로 위치를 확인한다(스크립트의 WinGet 탐색은 리눅스에서 그냥 건너뜀).
- 렌더러 `scripts/render_short.py` 는 표준 라이브러리+ffmpeg 라 `python3 .claude/skills/shopping-shorts/scripts/render_short.py <폴더>` 로 그대로 돈다. `만들기.bat` 은 쓰지 않는다.
- 결과 폴더: `C:\Users\Admin\Desktop\쇼핑쇼츠\...` 대신 저장소 안 `쇼핑쇼츠/<YYYYMMDD>_<상품짧은이름>/`.

## BGM (팩에서 뺐음)
- 기본 BGM `assets/bgm/beat.wav` 는 팩에 없다. **PC 원본**을 쓴다.
- 클라우드에서는 렌더러가 BGM 파일을 못 찾아 멈추지 않도록 무음 파일을 만들어 지정한다: `ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo -t 40 <폴더>/silence.wav` → project.json 에 `"bgm": "silence.wav"`. 시험 렌더 후 "BGM 없음 — PC 에서 최종 렌더" 라고 알린다.

## 음성 (여의도여자 = PC 전용)
- 여의도여자는 PC의 Voicebox(`127.0.0.1:17493`)에서만 된다. 클라우드에는 없으므로 대체 TTS를 쓴다:
  `python3 -m pip install edge-tts` → `edge-tts --voice ko-KR-SunHiNeural --rate=+8% -f script.txt --write-media voice.mp3 --write-subtitles voice.vtt` (남성은 `ko-KR-InJoonNeural`).
  edge-tts가 막히면 `gTTS`, 그것도 안 되면 무음+자막으로 만든다.
- 결과 보고(마지막 결과표)에 **"음성: 대체 TTS(여의도여자 아님) — PC에서 다시 더빙 필요"** 라고 반드시 알린다.
- 최종본을 여의도여자 목소리로 원하면 PC Remote Control 세션에서 같은 스킬을 돌리라고 안내한다.
- SKILL.md 5장의 `fetch(VB+...)` 코드는 Voicebox 전용이다. 클라우드에서는 위 edge-tts 로 `voice.wav` 를 만든다.

## 쿠팡 확인
- 쿠팡은 데이터센터 IP를 자주 막는다. 막히면 사용자가 보낸 캡처·상품명으로 진행하고, 가격·옵션은 "확인 필요" 로 표시한다.

## 결과물
- 결과 폴더는 `C:\Users\Admin\Desktop\...`/Downloads 대신 저장소 안 작업 폴더(`output/`)에 둔다. 100MB 넘는 mp4는 커밋 금지 → `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart out.mp4` 로 45MB 이하로 줄여 커밋.
- 업로드는 하지 않는다(사용자가 명령할 때만, 그리고 업로드는 PC).
