# motion/ — 쇼츠에 끼워 넣는 모션 클립 (Remotion · HyperFrames · Manim)

모두 **1080x1920 · 30fps mp4** 를 만들고, 쇼츠 대본의 한 장면을 `"visual": {"mode": "clip", "clip": "<프로젝트 기준 mp4 경로>"}` 로 바꾸면
렌더러(`studio/short.py clip_frame`)가 그 장면 동안 클립을 화면 전체로 재생한다. 후크 문구·자막·진행바는 그 위에 그대로 얹힌다
(클립 속 핵심 요소는 y 450~1350 안에 두기: 위는 후크, 아래는 자막 자리). 클립이 장면보다 짧으면 마지막 프레임 유지.

| 폴더 | 도구 | 예시 (5초 테스트 통과) | 렌더 |
|---|---|---|---|
| `remotion/` | Remotion 4 (React) | `src/CountUp.tsx` 금액 카운트업 (예: 순자산 8억) | `cd remotion && npx remotion render src/index.ts CountUp out/x.mp4 --props='{"label":"밥값","value":80000,"unit":"원","caption":"첫 데이트"}'` |
| `hyperframes/stat-card/` | HyperFrames (HTML+GSAP) | A vs B 비율 막대 (예: 남자가 낸다 38% vs 번갈아 62%) | `cd hyperframes && npx hyperframes render stat-card -o out/x.mp4 --workers 2` |
| `manim/` | Manim Community 0.22 | `trust_graph.py` 거짓말 횟수 vs 신뢰 그래프 | `$MANIM -qh --fps 30 -r 1080,1920 --media_dir media trust_graph.py TrustGraph -o x.mp4` |

설치 (컨테이너가 새로 뜨면):
- Remotion: `cd motion/remotion && npm ci` (브라우저는 미리 깔린 `/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell`, `remotion.config.ts`)
- HyperFrames: `cd motion/hyperframes && npm i hyperframes` (`PUPPETEER_EXECUTABLE_PATH` 에 같은 headless_shell 지정 가능)
- Manim: `apt-get install -y libpango1.0-dev libcairo2-dev pkg-config` → `python3 -m venv <scratch>/manimenv && <scratch>/manimenv/bin/pip install manim` (`MANIM=<scratch>/manimenv/bin/manim`). TeX 없음 → `Text()`만, `MathTex`/축 숫자 라벨(include_numbers) 금지.

라이선스: Remotion은 개인·3인 이하 회사 무료(그 이상은 회사 라이선스) · HyperFrames Apache-2.0 · Manim MIT. 폰트는 `assets/fonts`(OFL)만 쓴다.
