# fabric — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside). PC 에는 Fabric CLI + 로컬 Ollama(qwen3:8b) + 패턴 265개가 깔려 있지만 클라우드에는 없다.

## 클라우드 방식 (CLI 설치 없이)
1. 자막 받기: `python3 -m pip install -U yt-dlp` → `yt-dlp --skip-download --write-auto-subs --sub-langs ko,en --sub-format json3 -o 'sub.%(ext)s' <URL>`. 제목·설명은 `yt-dlp -J <URL>`.
2. 패턴 원문: PC 경로(`C:\Users\Admin\.config\fabric\patterns`) 대신 공개 저장소 `https://raw.githubusercontent.com/danielmiessler/fabric/main/data/patterns/<패턴>/system.md` 를 읽는다(SKILL.md 표의 패턴 이름 그대로).
3. Claude 가 직접 그 system.md 지시대로 자막을 처리하고, 결과는 한국어로 쓴다(`-g=ko` 와 같은 효과). Ollama·API 키는 필요 없다.
- `Get-ChildItem`, `$env:TEMP` 같은 PowerShell 명령은 쓰지 않는다. 패턴 목록이 필요하면 위 저장소의 `data/patterns` 폴더 목록을 본다.

## 유튜브 다운로드
- `python3 -m pip install -U yt-dlp` 후 `yt-dlp` 사용. 클라우드는 데이터센터 IP라 "Sign in to confirm you're not a bot" / 403 / 자막 없음으로 막히기 쉽다.
- 막히면 재시도로 버티지 말고 멈춘 뒤, **"유튜브 다운로드는 PC Remote Control 세션에서 해 주세요"** 라고 안내한다(필요한 URL·구간 목록은 표로 남긴다). 쿠키·로그인 정보는 받지 않는다.
- 자막만 막힌 경우: 사용자가 대본 텍스트를 붙여 주면 같은 패턴으로 처리할 수 있다고 함께 안내한다.

## 결과물
- 결과 md 는 저장소 안 `fabric_out/` 에 두고 요약은 마지막 결과표로 보고한다.
