# watch — 윈도우 PC(Aside / Remote Control)와 Claude Code 클라우드에서의 차이

SKILL.md 는 원본(mathiaschu/watch v1.0.0, 커밋 14c780e, MIT)을 그대로 둔다. 이 문서는 다른 점만 적는다.
원본의 `${CLAUDE_SKILL_DIR}` 은 이 폴더(`.claude/skills/watch`)를 뜻한다. `hooks/`, `commands/` 는 플러그인 설치용이라 스킬 폴더에서는 동작하지 않는다(무시해도 됨).

## 언제 쓰나
- 유튜브·인스타·X·틱톡 링크나 mp4 파일을 주며 "이 영상 분석해줘", "첫 3초에 뭘 보여줬어?", "자막을 어떻게 깔았어?"처럼 **화면까지 봐야 하는** 요청.
- 대사만 요약하면 되는 요청은 fabric 을 쓴다(더 가볍다). 둘을 같이 써도 된다: watch 로 장면+대본 추출 → fabric 패턴으로 정리.

## 윈도우 PC (권장: 유튜브 링크 분석은 여기서)
1. `python3` 대신 `python` 을 쓴다(윈도우의 `python3` 는 스토어 스텁).
2. 의존성 (한 번만):
   ```powershell
   winget install Gyan.FFmpeg
   winget install yt-dlp.yt-dlp        # 또는 pip install --user -U yt-dlp
   pip install -U openai-whisper        # 받아쓰기(CPU). mlx-whisper 는 애플 실리콘 맥 전용이라 윈도우에서 설치 안 됨
   ```
   - openai-whisper 는 PyTorch 를 함께 받는다(약 2GB+). 설치 후 첫 실행 때 `base` 모델(약 140MB)을 내려받는다.
   - ffmpeg 를 winget 으로 깔았으면 새 터미널을 열어야 PATH 에 잡힌다.
   - 점검: `python .claude\skills\watch\scripts\setup.py --check` → 출력 없이 끝나면(종료코드 0) 준비 완료. 3 이면 whisper 미설치, 2 면 ffmpeg/yt-dlp 미설치.
3. 실행:
   ```powershell
   python .claude\skills\watch\scripts\watch.py "<URL 또는 mp4 경로>" --out-dir "%TEMP%\watch-작업"
   ```
   - 자막이 있는 영상은 자막을 쓰고, 없으면 openai-whisper 로 받아쓴다(CPU라 10분 영상에 수 분).
   - 받아쓰기가 너무 느리거나 필요 없으면 `--no-whisper`(장면 사진만).
   - Aside 셸에서 임시 폴더 문제가 나면 fabric 처럼 `$env:TEMP` 를 쓰기 가능한 폴더로 바꾸고 `--out-dir` 을 지정한다.
4. 로그인이 필요한 소스(인스타, 일부 X)는 원본 안내대로 `--cookies-from-browser chrome` 을 쓸 수 있다. 이것은 **사용자 PC 브라우저의 로그인 정보를 쓰는 옵션**이므로 사용자가 요청했을 때만 쓴다.
5. 결과로 나온 장면 사진(jpg)을 하나씩 읽고 대본과 함께 답한다. 10분 넘는 영상은 `--start/--end` 로 구간을 먼저 좁힌다.

## Claude Code 클라우드(Linux)
- **유튜브 링크는 거의 항상 막힌다.** 2026-11-25 시험에서 yt-dlp 가 "Sign in to confirm you're not a bot"으로 거절됐다(데이터센터 IP). 재시도로 버티지 말고, **"유튜브 링크 분석은 PC 세션에서 해 주세요"** 라고 안내한다. 쿠키·로그인 정보는 받지 않는다.
- 클라우드에서 되는 방법: 사용자가 **mp4 파일**을 주면 `python3 scripts/watch.py <파일경로> --out-dir <작업폴더>` 로 장면 추출+받아쓰기가 된다.
  - 받아쓰기 엔진: `python3 -m pip install -U openai-whisper`(무거움). 이미 faster-whisper 를 쓰는 환경이면 `--no-whisper` 로 장면만 뽑고 받아쓰기는 faster-whisper 로 따로 해도 된다.
  - ffmpeg 가 없으면 `apt-get install -y ffmpeg`.
- 작업 폴더·장면 사진은 커밋하지 않는다(세션 스크래치 폴더에 둔다).
