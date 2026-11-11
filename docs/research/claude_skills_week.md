# 이번 주(2026-11-04~11-11) 1만 번 넘게 설치된 Claude 스킬 조사

조사: 2026-11-11 (일꾼 세션, 영상 `projects/skills3_neon.yaml` 용)

## 숫자를 어디서 셌나 (중요)
1. **skills.sh 순위표 "Trending (24h)" 탭** — https://skills.sh/trending (2026-11-11 13:29 UTC 에 원문 HTML 을 받아 숫자를 그대로 뽑음).
   - 탭 이름은 "Trending (24h)", 페이지 제목은 "Trending AI Agent Skills — This Week". 즉 **최근 24시간(또는 이번 주) 설치 수**다. 어느 쪽이든 이번 주 안의 숫자이므로, 이 칸이 1만을 넘으면 "이번 주 1만 회 이상"은 확실하다.
   - skills.sh 는 `npx skills add` 로 설치될 때 세는 곳(Vercel 이 만든 공개 스킬 레지스트리). Claude Code·Cursor·Codex 등 여러 에이전트 설치가 함께 세어진다(Claude 전용 숫자는 따로 없음).
   - 주의: 같은 저장소의 스킬들이 거의 같은 숫자(예: microsoft/azure-skills 28개가 모두 11,750 안팎)인 경우가 많다 → 저장소를 통째로 설치하면 스킬마다 1씩 오르는 것으로 보인다(관찰, 공식 설명은 못 찾음).
2. **npm 주간 다운로드** (스킬이 부르는 CLI 프로그램) — `https://api.npmjs.org/downloads/point/2026-11-04:2026-11-10/<패키지>` 를 직접 열어 확인. 스킬 설치 수가 아니라 **그 스킬이 쓰는 프로그램의 내려받기 수**다. 패키지 주인은 npm registry `repository` 칸으로 확인.
3. 누적 설치 수 — 각 skills.sh 스킬 페이지("Installs").

공식 "주간 설치 수" 칸은 skills.sh 스킬 페이지에 없다(누적만 있음). 그래서 영상에서는 "최근 24시간 설치 수"와 "npm 이번 주 다운로드"를 출처와 함께 그대로 말한다.

## 후보 표

| 스킬 이름 | 만든 곳 | 이번 주 숫자와 출처 | 무엇을 해 주나 | 해외 유튜버 언급(이번 주) |
|---|---|---|---|---|
| **find-skills** | Vercel Labs (`vercel-labs/skills`) | skills.sh 24h 설치 **17,196** (https://skills.sh/trending) · 누적 4.3M (https://skills.sh/vercel-labs/skills/find-skills) · 이 스킬이 쓰는 CLI npm `skills` 11/04~11/10 **5,302,853** 다운로드 | "○○ 하는 스킬 있어?" 하면 에이전트가 `npx skills find` 로 스킬을 찾아 설치 수·만든 곳·별 수로 골라 `npx skills add` 로 깔아 줌 | Trạm AI(베트남) "find-skills: 세계에서 가장 많이 설치된 스킬"(11h 전) · Prampar videos "Top 10 Most-Installed Claude Skills (2026)"(5일 전) · さつきのOSS研究室(일본, 2일 전) |
| **agent-browser** | Vercel Labs (`vercel-labs/agent-browser`) | skills.sh 24h **17,927** · 누적 1.5M (https://skills.sh/vercel-labs/agent-browser/agent-browser) · npm `agent-browser` 11/04~11/10 **2,439,036** | AI 에이전트가 크롬 브라우저를 직접 열고 누르고 읽음(접근성 트리 스냅샷 + `@e1` 같은 짧은 번호로 요소 지정). 로그인 유지, 화면 캡처, 데이터 뽑기 | Cand Dev "This CLI Lets AI Agents Control Your Browser (Thanks to Vercel)"(5일 전) · Skill MD "Vercel Agent Browser: 47K Stars, Every Safety Switch Off by Default"(1일 전, 보안 설정 기본 꺼짐 주의) · Model Lab agent-browser 시험 영상 |
| **hyperframes** (+ media-use 등 묶음) | HeyGen (`heygen-com/hyperframes`) | skills.sh 24h hyperframes **15,834**, media-use **15,940**, hyperframes-cli 15,769, hyperframes-registry 14,760 · 누적 1.5M (https://skills.sh/heygen-com/hyperframes/hyperframes) · npm `hyperframes` 11/04~11/10 **1,313,676** | HTML 로 장면을 쓰면 MP4 영상으로 렌더. 자막·내레이션·장면 전환·모션그래픽. "영상 편집 프로그램 없이 말로 영상 만들기" | Grow With Kaz "I Made VIRAL Animation Videos Using Claude Code (FREE Plugin)"(6일 전, 31.8만 회) · Shabbir Noor "How I Edit Long Form Videos With Claude Code (No Editor)"(1일 전, 설명란에 `claude plugin install hyperframes@hyperframes`) · Pau Berenguer "How to EDIT Videos with Claude Code and HyperFrames"(3일 전) · Ryan Lanyon(8시간 전) · RyvSX0LGNbs "HyperFrames vs Remotion vs Three.js" |
| design-mobile-apps | designed-by-ai (`designed-by-ai/skills`) | skills.sh 24h **19,921** · 누적 1.4M | 모바일 앱 화면 디자인 안내 | 이번 주 영상 언급 못 찾음. 만든 곳 정보가 적어 추천에서 뺌 |
| microsoft-foundry 외 azure-skills 28개 | Microsoft (`microsoft/azure-skills`) | skills.sh 24h 각 **약 11,750** (저장소 합계 329.1K) | Azure 클라우드 배포·진단·비용 등 | 이번 주 영상 언급 못 찾음. 회사 개발자용이라 35~50세 일반 시청자에겐 멀다 |

참고(1만 못 넘김 또는 제외):
- remotion-best-practices (remotion-dev) 24h 8,205 — 하루치는 1만 미만.
- grill-me (mattpocock) 24h 6,198, frontend-design (anthropics/skills, Anthropic 공식) 24h 4,664.
- `*/superpowers` 이름의 ai-video-generation·twitter-automation 등(bankai-skills 24,994 등): 서로 다른 여러 새 저장소가 같은 이름·거의 같은 숫자로 올라와 있어 **부풀린 숫자로 의심** → 영상에서 뺌(주의 장면에서 "숫자만 보고 깔지 말 것" 예로만, 이름은 말하지 않음).

## 해외 유튜버 이번 주 흐름 (YouTube 검색 '이번 주' 필터, 2026-11-11 확인 — 조회수·날짜는 검색 결과 표기 그대로)
- 가장 많이 다뤄진 건 **"Claude 로 영상 만들기" 스킬(HyperFrames 등)**: Grow With Kaz 2편(31.8만·13.4만 회), Rourke "Claude Opus 5.5: How To Make Motion Graphics"(20.8만 회, 4일 전), 여러 소형 채널 따라하기.
- 브라우저 조작(agent-browser, OpenCode Browse) 소개 영상 여러 편.
- AI LABS "Head Of Design At X's New Claude Skill Is Insane"(7.3만 회, 3일 전), André Lug "24 Free Skills and Plugins That Make Claude Code Much Smarter"(2.3만 회, 2일 전) 같은 모음 영상.
- 유튜버가 말한 숫자는 영상에서 "한 유튜버 정리"로만 말한다.

## 추천 3개와 고른 이유
1. **find-skills** — 24h 1.7만, 누적 430만으로 skills.sh 1위. 처음 쓰는 사람이 "스킬 찾는 스킬" 하나만 깔면 나머지를 말로 찾게 됨 → 입문 첫 순서.
2. **agent-browser** — 24h 1.8만, 프로그램 주간 244만 다운로드. 만든 곳(Vercel) 확실. "AI 가 내 대신 웹사이트 눌러 줌"은 초보도 바로 이해. 보안 기본값 주의점(해외 유튜버 지적)도 있어 '주의' 꼭지가 실하다.
3. **hyperframes** — 24h 1.6만(묶음 스킬 여럿이 모두 1.5만 안팎), 이번 주 해외 유튜버가 가장 많이 다룬 주제. 우리 채널이 실제로 쓰는 도구라 실제 쓰는 예를 보여 줄 수 있음.
- 뺀 것: design-mobile-apps(24h 1.99만으로 숫자는 가장 크지만 만든 곳·내용 확인이 약함), azure-skills(대상이 회사 개발자).

## 설치 방법(원문 확인)
- find-skills: `npx skills add https://github.com/vercel-labs/skills --skill find-skills`
- agent-browser: `npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser` + 프로그램 `npm i -g agent-browser && agent-browser install`
- hyperframes: `npx skills add https://github.com/heygen-com/hyperframes --skill hyperframes` 또는 Claude Code 플러그인 `claude plugin install hyperframes@hyperframes`(Shabbir Noor 영상 설명란). Node.js·FFmpeg 필요(같은 설명란).
- 보안 검사: 세 스킬 모두 skills.sh 페이지에서 Gen Agent Trust Hub Pass · Socket Pass · Snyk Warn.

## 출처
- https://skills.sh/trending (24h 탭, 2026-11-11)
- https://skills.sh/ (누적)
- https://skills.sh/vercel-labs/skills/find-skills · https://skills.sh/vercel-labs/agent-browser/agent-browser · https://skills.sh/heygen-com/hyperframes/hyperframes
- https://api.npmjs.org/downloads/point/2026-11-04:2026-11-10/skills · …/agent-browser · …/hyperframes
- https://agent-browser.dev · https://hyperframes.heygen.com · https://github.com/vercel-labs/skills · https://github.com/vercel-labs/agent-browser · https://github.com/heygen-com/hyperframes
- YouTube: https://youtu.be/3tpaWHaiLQ8 · https://youtu.be/Gcs3Aki9BNE · https://youtu.be/V5L2mBhk1N0 · https://youtu.be/vXSW22HhvbY · https://youtu.be/xTpy6qcdvPM · https://youtu.be/lnNtwW7R00c · https://youtu.be/cDb-wPq0Iyk
