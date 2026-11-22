# neogul-edit — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside). 이 문서는 클라우드에서 다른 점만 적는다.

## 공통 설치 (세션마다 한 번, 있으면 생략)
```bash
which ffmpeg ffprobe || (apt-get update && apt-get install -y ffmpeg)
apt-get install -y fonts-noto-cjk   # 한글 폰트가 깨질 때만
```
- `python` 대신 `python3`, 경로 구분은 `/`. `.bat`/`.ps1`/`explorer.exe`/`Start-Sleep`/`chcp 65001` 은 쓰지 않고 셸에서 바로 실행한다(오래 걸리면 백그라운드 실행 후 로그 확인).
- 스크립트가 PATH의 ffmpeg를 못 찾으면 `which ffmpeg` 로 위치를 확인한다(스크립트의 WinGet 탐색은 리눅스에서 그냥 건너뜀).
- `scripts/neogul_edit.py` 는 표준 라이브러리+ffmpeg 만 쓰므로 그대로 `python3 scripts/neogul_edit.py ...` 로 실행된다.

## 음성 (여의도여자 = PC 전용)
- 여의도여자는 PC의 Voicebox(`127.0.0.1:17493`)에서만 된다. 클라우드에는 없으므로 대체 TTS를 쓴다:
  `python3 -m pip install edge-tts` → `edge-tts --voice ko-KR-SunHiNeural --rate=+8% -f script.txt --write-media voice.mp3 --write-subtitles voice.vtt` (남성은 `ko-KR-InJoonNeural`).
  edge-tts가 막히면 `gTTS`, 그것도 안 되면 무음+자막으로 만든다.
- 결과 보고(마지막 결과표)에 **"음성: 대체 TTS(여의도여자 아님) — PC에서 다시 더빙 필요"** 라고 반드시 알린다.
- 최종본을 여의도여자 목소리로 원하면 PC Remote Control 세션에서 같은 스킬을 돌리라고 안내한다.
- `voice` 명령은 `--voice 여의도여자` 를 빼면 Windows TTS(Heami)를 쓰는데 리눅스에는 없다. 클라우드에서는 위 edge-tts로 **문장별 wav**(대본 한 줄 = 파일 하나, `01.wav, 02.wav …`)를 만든 뒤 `voice script.txt --out-dir <폴더> --wav-dir <문장별음성폴더>` 로 voice.wav·voice.srt 를 만든다.

## 너굴분석(참고 영상 받기)
- SKILL.md 의 ytultra.com + REPL fetch 방식은 Aside 전용이다. 클라우드에서는 `yt-dlp -f 18 <URL>` 을 먼저 시도한다.

## 유튜브 다운로드
- `python3 -m pip install -U yt-dlp` 후 `yt-dlp` 사용. 클라우드는 데이터센터 IP라 "Sign in to confirm you're not a bot" / 403 / 자막 없음으로 막히기 쉽다.
- 막히면 재시도로 버티지 말고 멈춘 뒤, **"유튜브 다운로드는 PC Remote Control 세션에서 해 주세요"** 라고 안내한다(필요한 URL·구간 목록은 표로 남긴다). 쿠키·로그인 정보는 받지 않는다.

## 결과물
- 결과 폴더는 `C:\Users\Admin\Desktop\...`/Downloads 대신 저장소 안 작업 폴더(`output/`)에 둔다. 100MB 넘는 mp4는 커밋 금지 → `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart out.mp4` 로 45MB 이하로 줄여 커밋.
- 업로드는 하지 않는다(사용자가 명령할 때만, 그리고 업로드는 PC).

## 점검 기록 (2026-11-22, 이 세션)
- edge-tts: 이 클라우드에서는 speech.platform.bing.com 인증서 검증 실패(edge-tts가 자체 certifi 인증서만 써서 프록시 인증서를 안 받음). 대체 TTS는 이미 깔린 Qwen3-TTS(`~/.cache/yeouido-tts`)를 쓴다.
