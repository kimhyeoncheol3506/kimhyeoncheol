# Claude Code vs Codex 팩트시트 (2026-11-05)

AI 초보용 약 10분 비교 영상의 대본 자료다.

- **[확인]**: 2026-11-05에 그 페이지나 저장소 파일을 직접 열어 본 것.
- **[미확인]**: 웹 검색 요약이나 유튜버 발언으로만 본 것. 대본에 쓰기 전에 다시 확인해야 한다.
- **⚠모순**: 자료끼리 말이 다른 곳.

> **접속 제한**: 이 세션에서는 OpenAI 쪽 사이트(developers.openai.com, chatgpt.com, help.openai.com, openai.com)에 접속하지 못했다(DNS 차단).
> 그래서 OpenAI 쪽 사실은 GitHub `openai/codex` 저장소(2026-11-05 13:38 UTC 커밋 1e9e8bd)에서 확인한 것만 [확인]이다.
> 요금·사용량 숫자는 모두 [미확인]이다. 세션 네트워크 설정에서 위 도메인을 허용하면 다시 확인할 수 있다.

참고 영상 자막 원문(gitignore 폴더)
- `analysis/claude_vs_codex/a_sebhastian.txt`
- `analysis/claude_vs_codex/b_hostinger.txt`
- `analysis/claude_vs_codex/c_techwithtim.txt`

---

## 1. 한눈에 비교표

| 항목 | Claude Code (Anthropic) | Codex (OpenAI) |
|---|---|---|
| 정체 | 코드베이스를 읽고, 파일을 고치고, 명령을 실행하는 "에이전트형 코딩 도구" [확인] | "컴퓨터에서 돌아가는 OpenAI의 코딩 에이전트" [확인] |
| 쓰는 곳 | 터미널 CLI, IDE(VS Code·Cursor 확장, JetBrains), 데스크톱 앱(Code 탭), 웹(claude.ai/code 클라우드 세션), GitHub `@claude` [확인] | 터미널 CLI, IDE(VS Code·Cursor·Windsurf), 데스크톱 앱(`codex app`), 웹 클라우드 에이전트 "Codex Web"(chatgpt.com/codex) [확인: README] |
| 무료로 쓸 수 있나 | **안 됨.** Free 플랜에는 Claude Code가 없다 [확인] | Free·Go에도 들어 있다는 자료가 있다 [미확인]. README는 "Plus, Pro, Business, Edu, Enterprise" 사용을 권장한다 [확인] |
| 입문 가격 | Pro $20/월(연간 결제 시 $17) [확인] | Plus $20/월 [미확인]. Go $8 [미확인] |
| 상위 플랜 | Max $100(Pro의 5배), Ultra $200(Pro의 10배, 인증 계정은 5시간 제한 없음) [확인] | Pro $100 / $200 / $500 [미확인] |
| 팀 플랜 | Team 표준석 $20(연간)/$25(월), 프리미엄석 $100/$125. Enterprise $20/석 + API 요금 [확인] | Business, Enterprise, Edu [플랜 이름만 확인: 소스 코드] |
| 기본 모델 | **Opus 5.5**. Pro 이상 모든 플랜의 기본이다 [확인] | 저장소에 들어 있는 모델 목록에서 1순위는 **GPT-6.1-Sol**("Latest workhorse model") [확인]. 실제 기본값은 서버가 정한다 [확인: 11-04 커밋 "Use server model defaults"] |
| 고를 수 있는 모델 | Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.1(최상위, Pro는 사용량 크레딧으로, Max·Ultra는 주간 한도의 절반까지) [확인] | GPT-6-Astra(최상위), GPT-6.1-Sol, GPT-6.1 Terra, GPT-6-Sol, GPT-6-Luna(빠르고 저렴), GPT-5.6 Sol·Terra·Luna, GPT-5.5(레거시) [확인: models.json] |
| 컨텍스트 창 | Opus 5.5·Sonnet 5.5는 기본 1M 토큰 [확인] | 대부분 기본 272K, 최대 872K(Terra 6.1은 기본 500K) [확인: models.json] |
| 오픈소스 | **아님.** "© Anthropic PBC. All rights reserved." 상용 약관을 따른다 [확인] | **오픈소스, Apache-2.0** [확인] |
| 설치 | `curl -fsSL https://claude.ai/install.sh \| bash` / Windows `irm https://claude.ai/install.ps1 \| iex`. npm 설치는 deprecated [확인] | `curl -fsSL https://chatgpt.com/codex/install.sh \| sh` / Windows PowerShell 설치 스크립트, `npm i -g @openai/codex`, `brew install --cask codex` [확인] |
| 윈도우 | 네이티브(Windows 10 1809+)와 WSL 둘 다 지원. Git for Windows 권장 [확인] | Windows 설치 스크립트가 있고, Windows 전용 샌드박스 코드를 계속 고치는 중(11-03 커밋 여러 개) [확인] |
| 프로젝트 규칙 파일 | CLAUDE.md. **AGENTS.md도 대신 읽을 수 있다** [확인] | AGENTS.md(`/init`이 만들어 준다) [확인] |
| 계획 모드 | plan 모드(읽기만, Shift+Tab으로 전환) [확인] | `/plan` = "switch to Plan mode" [확인] |
| 서브에이전트 | Subagents, 에이전트 팀 [확인] | `/agents`(에이전트 커맨드 센터), `/multi-agents` [확인] |
| 훅·스킬·MCP·플러그인 | 넷 다 있음. Mods(화면과 동작을 바꾸는 플러그인)도 있다 [확인] | `/hooks`, `/skills`, `/mcp`, `/plugins` 넷 다 있음 [확인] |
| 권한·안전 | 권한 모드: auto(기본, 다른 모델이 위험한 동작을 걸러 줌) / Manual(default) / acceptEdits / plan / bypassPermissions(격리된 환경 전용) [확인] | 샌드박스: read-only / workspace-write / danger-full-access. 승인: untrusted / on-request / never / granular. 자동 리뷰 모델("Codex Auto Review", Guardian) [확인] |
| 클라우드 작업 | 클라우드 세션: Pro·Max·Ultra·Team, Enterprise(프리미엄석 등). 사용량 한도 안에서 쓰고 VM 요금은 따로 없다 [확인] | Codex Web(클라우드 에이전트) [확인: README]. 11월 초 커밋들이 클라우드 클라이언트를 확장 중 [확인] |
| 코드 리뷰·GitHub | 관리형 Code Review는 **Team·Enterprise 전용**(PR에 인라인 댓글, 승인·차단은 안 함). `/code-review`는 모든 플랜. GitHub Actions `@claude` [확인] | `/review`(내 변경 리뷰) [확인]. GitHub 자동 PR 리뷰, "@codex fix this" [미확인: Hostinger 영상] |
| 상대 도구 가져오기 | — | **`/import` = "Claude Code에서 설정·프로젝트·최근 대화 가져오기"** [확인] |
| 사용량 한도 | 5시간 창 + 주간 한도. Claude 채팅·Cowork와 같은 한도를 나눠 쓴다. Ultra 인증 계정은 5시간 제한 없음 [확인] | Plus 기준 5시간마다 Sol 15~160 메시지, Astra 5~45 메시지(OpenAI 추정치), 주간 한도 별도. Pro는 현재 5시간 제한 없음 [미확인] |
| GitHub 별 개수 | 약 15만(Nathan) / 14.2만(Tim, 2개월 전) [미확인] | 약 13만(Nathan) / 10.6만(Tim) [미확인] |

### 출처 URL
**Claude 쪽 (모두 [확인])**
- 요금: https://claude.com/pricing
- 기본 모델·Fable·1M 창: https://code.claude.com/docs/en/model-config.md
- 권한 모드: https://code.claude.com/docs/en/permission-modes.md
- 클라우드 세션: https://code.claude.com/docs/en/claude-code-on-the-web.md
- Code Review: https://code.claude.com/docs/en/code-review.md
- 사용량 창: https://code.claude.com/docs/en/costs.md
- CLAUDE.md·AGENTS.md: https://code.claude.com/docs/en/memory.md
- 설치·Windows: https://code.claude.com/docs/en/setup.md
- 그 밖의 기능: https://code.claude.com/docs/en/sub-agents.md, /hooks.md, /skills.md, /mcp.md, /github-actions.md
- 라이선스: https://github.com/anthropics/claude-code/blob/main/LICENSE.md
- 최신 버전: CHANGELOG.md v2.1.318

**Codex 쪽 ([확인])**
- 라이선스: https://github.com/openai/codex/blob/main/LICENSE (Apache 2.0)
- README: https://github.com/openai/codex/blob/main/README.md
- 모델 목록: `codex-rs/models-manager/models.json`
- 슬래시 명령: `codex-rs/tui/src/slash_command.rs`
- 샌드박스·승인: `codex-rs/protocol/src/config_types.rs`, `protocol.rs`
- 플랜 종류(free, go, plus, pro, prolite, promax, team, business 등): `codex-rs/protocol/src/auth.rs`
- 릴리스: https://github.com/openai/codex/releases (최신 안정판 rust-v0.166.0, 11-04~05 0.167/0.168 알파)

**Codex 쪽 ([미확인]: 열어 보지 못함)**
- 요금·한도: https://developers.openai.com/codex/pricing (검색 요약으로만 봄)
- https://chatgpt.com/pricing
- https://help.openai.com/en/articles/11369540-codex-in-chatgpt

---

## 2. 모델·가격 자세히

**Claude [확인]** (출처: https://claude.com/pricing, https://www.anthropic.com/news, https://www.anthropic.com/news/claude-opus-5-5)
- 출시일: Opus 5.5 2026-09-22, Sonnet 5.5 2026-09-28, Haiku 5.5 2026-10-07.
- Opus 5.5 API 가격(100만 토큰당): 입력 $4, 출력 $20. 빠른 모드는 $8/$40.
- Fable 5.1은 "장시간 에이전트용 차세대 모델"이다. 어느 플랜에서도 기본 모델이 아니다.
- 플랜별 Fable: Pro는 사용량 크레딧으로, Max·Ultra는 주간 한도의 50%까지.

**OpenAI [미확인]** (출처: 웹 검색 요약)
- GPT-6.1 Sol: 2026-09-29 DevDay에서 발표. Plus·Pro·Business·Enterprise·Edu에서 Codex로 쓸 수 있다.
- Nathan 영상 기준 API 가격: Sol $2/$10, Terra $1/$5, Luna $0.10/$0.50.
- 저장소에는 모델 이름과 컨텍스트 창이 있다 [확인]. 출시일과 가격은 저장소에 없다.

**⚠모순: 요금제**
- Claude $200 플랜
  - 현재 공식 페이지: Ultra $200 = Pro의 10배 [확인].
  - Nathan(8일 전)과 Tim(2개월 전): "Max $200 = 20배"라고 말함.
  - Max 20배는 없어졌다(어제 팩트시트와 같음).
- Claude $20 플랜의 모델
  - Tim(2개월 전): "Pro는 기본이 Sonnet 5이고, Opus는 Max $100부터".
  - 현재 공식: Pro에 Opus가 들어 있고, 기본 모델은 Opus 5.5 [확인].
  - 즉 Tim이 말한 '$20 비대칭'은 이제 성립하지 않는다.
- Codex 5시간 제한
  - Tim: "7월에 유료 플랜의 5시간 제한을 일시적으로 없앴다".
  - Nathan·Hostinger: Plus는 5시간 창이 있고 Pro만 없다.
  - 현재 상태는 [미확인]이다.
- OpenAI Pro 가격
  - Tim: "$100부터". Nathan: "$100/$200/$500". 검색 요약은 Nathan과 같다.
  - Hostinger: "9월 29일 $200 Pro를 다시 열었지만 한도는 줄었다" [미확인].
- Codex 무료 사용
  - 검색 요약: Free·Go 포함(Free는 데스크톱 앱 Luna만이라는 자료도 있음).
  - README: Plus 이상을 권장.
  - 결론: "무료로 맛보기 가능"까지만 말하고 [미확인]으로 남긴다.

---

## 3. 회사가 발표한 벤치마크 (모두 '회사 자체 발표')

**Anthropic, Opus 5.5 출시글** (2026-09-22, https://www.anthropic.com/news/claude-opus-5-5) [확인]

| 벤치마크 | Opus 5.5 | GPT-6 Astra | GPT-5.6 Sol |
|---|---|---|---|
| Terminal-Bench 4.0 | 66.4% | 57.9% | 37.3% |
| FrontierCode v1.1 | 54.4% | 53.3% | 47.5% |
| AutomationBench | 40.0% | 41.4% | — |
| Terminal-Bench-Science 0.1 | 58.7% | 64.6% | — |

- 각주: Terminal-Bench는 Opus 5.5를 xhigh effort로, Astra는 high effort(OpenAI 발표값)로 돌린 결과다. **설정이 다르다.**
- SWE-bench Verified 숫자는 이 글에 **없다**.

**OpenAI, GPT-6.1 Sol** [미확인] (출처: windowsreport, itbrief, unite.ai 등 검색 요약)
- Terminal-Bench-Science 0.1 기준 작업당 비용: Sol $5.47, Opus 5.5 $23.21, Astra $23.80.
- DeepSWE v1.1에서 Astra와 같은 점수를 약 1/5 비용으로 냈다고 함.
- SWE-bench Verified는 발표하지 않은 것으로 보인다.

**⚠모순**: 두 회사 모두 "우리가 더 좋고 더 싸다"고 주장한다. 고른 벤치마크와 effort 설정이 서로 다르다. Nathan과 Tim이 영상에서 둘 다 이 점을 짚었다.

**독립 벤치마크** [미확인] ("senior suite bench" 'tasteful solve', Nathan 영상 화면)
- Opus 5.5 39.3%, Astra 36.8%.
- 기본 해결률: 61.8% 대 60%.
- 작업당 토큰: Opus 41K, Astra 19K.

---

## 4. 최근 2주 소식 (10-22 ~ 11-05)

**Anthropic** [확인]
- Agent Skills를 Agentic AI Foundation에 기증(10-22).
- S-1 상장 신청서 제출(10-26).
- Claude Code 최신 버전 v2.1.318.
- 새 코딩 모델은 없음. Haiku 5.5는 10-07로 2주보다 이전이다.

**OpenAI Codex** [확인: 커밋과 태그]
- 0.160~0.166 안정판이 나왔고, 0.167·0.168 알파 진행 중.
- 클라우드 클라이언트 기능을 대거 추가(11-03~05).
- 새 TUI 세션은 서버가 정한 기본 모델을 쓰도록 바뀜(11-04).
- Guardian 자동 리뷰, Windows 샌드박스, 스킬 권한을 강화.
- 이름만 보이는 것: 숨김 모델 "Daybreak Blue/Red"(사이버보안용), `/daybreak`, `/pets`, `/goal`, `/voice`. 발표 시점은 [미확인].

---

## 5. 참고 영상 정리

모든 숫자는 **"유튜버 자체 테스트"**다. 한 번씩만 돌린 결과다.

### a) Nathan Sebhastian — "Claude Code vs Codex - Real Cost & Performance Test (2026)"
- 기본 정보: 22:45, 2026-10-28 업로드, https://www.youtube.com/watch?v=qcEkQEZdEyM
- 챕터: 0:00 인트로 / 4:18 개요 / 8:10 벤치 세팅 / 8:51 과제1 코드베이스 설명 / 10:43 과제2 앱 만들기 / 14:35 과제3 5,600줄 리팩터 / 16:16 과제4 모호한 버그 / 17:27 과제5 PR 리뷰 / 18:40 결론
- 첫 30초 후킹
  - "매일 쓸 거면 뭐?"라고 묻는다.
  - 다섯 과제를 한 번에 나열한다.
  - "시간·토큰을 쟀다", "모델 3단계씩, 총 30번 실행, 모델이 못 보는 숨은 테스트로 채점"이라고 말한다.
- 설정
  - 모델을 같은 등급끼리 붙였다: Haiku-Luna, Sonnet-Terra, Opus-Sol.
  - 모두 medium effort, CLI 헤드리스 모드.
  - 자체 러너를 만들어 매번 새 폴더에서 같은 프롬프트로 돌렸다.
  - 숨은 테스트로 합격·불합격을 매겼다.
- 과제별 결과

| 과제 | 결과 |
|---|---|
| 1. 처음 보는 코드 설명 | 6개 중 5개 만점, Luna만 틀림. Opus는 2분 30초에 258줄, Terra는 1분 안에 68줄로 같은 점수 |
| 2. 칸반 앱(숨은 테스트 62개) | Luna 빼고 모두 만점. Claude 모델들은 1,600~2,700줄, Terra는 345줄을 2분에 씀. UI는 Opus가 더 좋았다는 주관 평가 |
| 3. 5,600줄 리팩터(기존 테스트 765개) | 6개 모두 테스트 통과. 그런데 문서 예제 테스트를 Sonnet은 3개, Luna는 2개 깨뜨렸고, Terra는 9개를 지웠다. Opus만 예제를 계속 찾을 수 있게 보완(7분, Sonnet·Terra는 약 2분) |
| 4. 모호한 버그 신고(12월 함정) | 전원 40초 안에 해결. Sol 첫 실행은 6분 동안 멈춰 다시 돌림(37초) |
| 5. 버그 3개 심은 PR | 전원 3개 모두 찾음. Codex는 3개만 보고, Claude는 4~6개를 더 지적. Opus와 Terra는 계획에 없던 4번째 버그(파일 덮어쓰기)까지 찾음 |

- 최종 결과
  - Opus와 Sol은 둘 다 만점이고 총 시간도 18분 32초 대 18분 29초로 거의 같다.
  - API 비용은 Opus 약 $5, Sol 약 $1.24로 4배 차이.
  - Haiku는 다섯 과제 모두 만점에 $0.91. 대신 가장 느리고 토큰을 가장 많이 썼다.
  - Terra는 다섯 과제를 5분 30초 안에 약 $0.30으로 끝냈다.
  - 30번 실행 중 25번이 만점.
- 채점: 숨은 테스트 합격 여부 + 시간·토큰·줄 수 + API 환산 비용.
- 결론
  - 일상적인 빠른 코딩에는 Codex.
  - 깊이(리뷰, 안전한 리팩터)를 원하면 Claude Code.
  - 예산이 빠듯하면 작은 모델도 충분하다.
  - 여유가 있으면 둘 다 $20씩 구독해서 Codex로 쓰고 Claude로 계획·리뷰.
  - "한 달 $20으로 내 작업에 직접 돌려 보라."
- 쓸 만한 기법
  - "벤치마크가 결론을 못 내는 3가지 이유" 도입부.
  - 회사 차트를 나란히 놓고 "숙제를 스스로 채점한다"는 비유.
  - "모델은 엔진, 하네스는 자동차" 비유.
  - 같은 등급끼리 대진표.
  - 과제마다 결과표(점수·시간·줄 수).
  - 두 앱을 직접 눌러 보는 데모.
  - 함정 문제(12월에는 13월이 없음)를 퀴즈처럼 보여 주기.
  - "테스트 통과 ≠ 안 망가짐" 반전.
  - 스스로 밝히는 솔직함("한 번만 돌린 거라 시간은 들쭉날쭉").
  - 마지막 질문 "여러분은?".

### b) Hostinger Academy — "Codex vs Claude Code: Which AI Coding Agent Is the BEST? (2026)"
- 기본 정보: 9:46, 2026-11-02 업로드, https://www.youtube.com/watch?v=Ga0Jkde7P0I
- 챕터: 0:00 인트로 / 0:18 모델 vs 에이전트 / 1:15 공통점 / 1:55 깊이 vs 효율 / 3:07 워크플로·GitHub / 4:27 가격·한도 / 5:41 속도·토큰 효율 / 6:38 무엇을 고를까 / 7:44 Hostinger Connector(광고) / 8:44 프로젝트 문맥 팁 / 9:25 결론
- 첫 30초 후킹: "점점 구별하기 어려워진다"고 시작한다. "Claude가 GPT를 이겼다"는 말이 모델 얘기인지 제품 얘기인지 되묻는다.
- 테스트: 직접 테스트는 **없다.** 설명형 영상이다.
- 인용한 숫자
  - "2026년 어떤 비교에서 Claude Code가 토큰을 3~4배 더 씀(대신 Codex 결과물이 더 단순)" [출처 없음].
  - "Plus는 5시간마다 Sol 15~160, Astra 5~45 메시지(OpenAI 추정치)".
- 주장
  - Claude는 시스템 전체를 이해하려는 시니어 엔지니어, Codex는 티켓만 처리하는 엔지니어.
  - Claude: 통제, Agent SDK, GitHub·GitLab(베타).
  - Codex: GitHub 자동 PR 리뷰가 강하고 "@codex fix this"가 된다.
  - Claude의 관리형 리뷰는 Team·Enterprise용 리서치 프리뷰이고 리뷰마다 요금이 붙는다.
  - $20 플랜: Codex는 Sol·Luna에 Astra 조금, Claude는 Opus 5.5·Sonnet 5.5에 Fable은 크레딧.
- 결론
  - 프론트·디자인, 모호한 문제, 탐색과 계획, 맞춤 워크플로가 필요하면 Claude Code.
  - 가성비, 군더더기 없는 실행, 구현·리팩터 위주, GitHub 중심이면 Codex.
  - 둘 다 쓸 때는 Claude가 설계, Codex가 구현(또는 Codex가 구현하고 Claude가 리뷰).
- 쓸 만한 기법
  - 10분 안에 "공통점 → 차이 → 가격 → 속도 → 추천" 순서로 정리하는 구조.
  - "시니어 vs 티켓 처리 엔지니어" 의인화.
  - 마지막 팁: "CLAUDE.md·AGENTS.md에 담은 프로젝트 지식이 도구보다 오래 간다. 도구를 바꿔도 남는다."

### c) Tech With Tim — "Codex vs Claude - an Honest Comparison"
- 기본 정보: 22:56, 약 2개월 전(9월 초 추정) 업로드, https://www.youtube.com/watch?v=sbuwHi1Sz6k
- 메타데이터(챕터)는 봇 차단으로 받지 못했다. 자막은 받았다.
- 모델 세대: GPT-5.6 Sol, Opus 5, Sonnet 5, Fable 5. **지금 기준으로 한 세대 전**이다.
- 흐름: 인트로 → 하네스 설명 → 스폰서(boot.dev, 약 2:50~4:20) → 제품 지형 → 회사 벤치마크 → 독립 벤치마크 → API 가격 → 구독 → 사용량 → 기능 수렴 → 데모 5개(12:50~) → 추천(20:40~)
- 첫 30초 후킹: Nathan과 거의 같다(같은 5개 과제, 직접 시간 재고 검증, "벤치마크로는 결판 안 난다, 독립 벤치마크는 동률").
- 과제별 결과

| 과제 | 결과 |
|---|---|
| 1. Textual 코드 분석 | Opus 5가 Sol보다 5배 넘게 오래 걸렸고, 635줄을 씀 |
| 2. 습관 추적 앱 | Codex가 더 빠름. Opus는 테스트 27개를 만듦. 겉모습은 Codex 쪽이 더 나았다고 평가 |
| 3. 5,040줄 리팩터 | 7개 중 6개 성공(Haiku 실패, 원본을 안 지움). Opus 5는 36분(Sol의 약 5배)이 걸렸고 검증 도구를 따로 만듦 |
| 4. 버그 | 전원 성공. Sol이 2줄로 가장 간결하게 고침. Claude는 약 3배 더 걸림 |
| 5. 버그 심은 PR | 전원 3개 모두 찾고 4번째 버그까지 발견. Claude가 더 오래 걸리고 더 많이 함 |

- 인용한 숫자
  - API: Sol $5/$30, Opus 5 $5/$25, Fable 5 $10/$50, Luna $0.20/$1.20(당시 가격).
  - 사용량: 커뮤니티 추정 Plus 5시간마다 Sol 10~100, Luna 2,000. Claude Pro 약 45 프롬프트.
  - 체감: Codex가 사용량을 3~4배 덜 씀.
  - 독립 벤치마크: Fable 5·Opus 5·GPT-5.6이 34.7%로 동률.
- 결론
  - 빠르고 효율적인 쪽을 원하면 Codex. 같은 정답을 4~7배 빠르게 내고, 한도가 넉넉하고, $20에 최상위 모델이 들어 있다.
  - 깊이를 원하면 Claude Code.
  - 형편이 되면 둘 다 쓰기($40). 서로 실수하는 곳이 달라서 교차 검증이 된다.
- 쓸 만한 기법
  - 제목의 "Honest" 프레이밍.
  - "숙제를 스스로 채점한다".
  - 모델 대칭이 안 맞는다는 지적("$20에 받는 모델이 다르다").
  - 데모 화면에서 실제 앱을 조작.
  - "종교 전쟁은 끝났다"는 마무리.

**⚠모순(영상끼리)**
- Nathan(10월)과 Tim(9월)은 과제 구성과 문구가 거의 같다. 둘 중 하나가 다른 쪽을 본떠 다시 만든 것으로 보인다.
- 모델 세대와 가격이 서로 다르니, 숫자는 **최신인 Nathan 것을 우선**한다.

---

## 6. 참고 영상별로 가져올 기법

1. **(a·c) "벤치마크로는 결판이 안 난다" 도입**
   - 두 회사 차트를 나란히 놓고 "둘 다 자기가 1등"을 보여 준다.
   - "숙제를 스스로 채점한다"는 자막으로 받는다.
2. **(a·b·c) 엔진과 자동차 비유**
   - 모델은 엔진, Claude Code·Codex는 자동차다.
   - 초보에게 '모델'과 '도구'를 구분해 주는 핵심 그림이다. 세 영상 모두 쓴다.
3. **(a) 라운드제 + 점수판**
   - 과제 5라운드를 진행한다.
   - 라운드마다 점수, 시간, 비용, 줄 수를 보여 주는 결과 카드를 띄운다.
   - 마지막에 종합 점수판과 트로피를 보여 준다. 결론은 "무승부, 그런데 성격이 다르다".
4. **(a·c) 나란히 만든 결과물 데모**: 같은 앱을 좌우로 놓고 클릭해 본다. 초보 눈에도 차이가 보인다.
5. **(a) 함정 퀴즈**
   - "12월에는 13월이 없다", "60초 뒤 실행인데 30초 뒤 만료되면?" 같은 문제를 시청자에게 먼저 던지고 정답을 공개한다.
6. **(a) 반전 포인트**: "테스트 전부 통과인데 절반이 뭔가를 망가뜨렸다."
7. **(a·c) 비용표**: 같은 결과를 내는 데 Opus 약 $5, Sol 약 $1.24. "4배 영수증"으로 시각화한다.
8. **(b) 의인화 캐릭터**
   - "시니어 엔지니어 Claude"(질문 많음, 꼼꼼, 느림)와 "티켓 처리 Codex"(시킨 것만, 빠름).
   - 동그라미 캐릭터 두 명으로 바로 연출할 수 있다.
9. **(b·a·c) "이런 분은 X" 추천 카드**: 마지막에 체크리스트 2열로 보여 준다.
10. **(a·b·c) "둘 다 쓰기" 조합**: Claude가 설계·리뷰하고 Codex가 구현하는 그림.
11. **(b) 마지막 팁**: 규칙 파일(CLAUDE.md, AGENTS.md)은 도구가 바뀌어도 남는 내 자산이다.
12. **(a) 솔직함 장치**: "한 번만 돌린 거라 다를 수 있음"을 자막 각주로 넣는다.

---

## 7. 대본에 바로 쓰기 좋은 요점

- **한 줄 정의**: 둘 다 "내 컴퓨터 폴더 안에서 코드를 읽고, 고치고, 실행까지 하는 AI 비서"다. Claude Code는 Anthropic, Codex는 OpenAI(ChatGPT 회사) 것이다. [확인]
- **어디서 쓰나**: 둘 다 터미널, VS Code 같은 편집기, 데스크톱 앱, 웹(클라우드)에서 쓸 수 있다. [확인]
- **가격**
  - 시작 가격은 둘 다 월 $20: Claude Pro [확인], ChatGPT Plus [미확인].
  - Claude는 무료 플랜에서 Claude Code를 못 쓴다 [확인].
  - Codex는 무료나 Go($8)에서도 맛보기가 가능하다는 자료가 있다 [미확인].
- **위 단계**
  - Claude: Max $100(5배), Ultra $200(10배) [확인].
  - ChatGPT: Pro $100·$200·$500 [미확인].
  - 옛 영상의 "Max $200 = 20배"는 지금은 틀렸다.
- **$20에 받는 모델**
  - Claude Pro의 기본은 Opus 5.5 [확인].
  - Codex Plus는 GPT-6.1 Sol 등을 쓰고 최상위 Astra도 조금 쓸 수 있다 [미확인].
  - 2개월 전 영상의 "Claude $20은 Sonnet뿐"은 지금은 틀렸다.
- **오픈소스**
  - Codex CLI는 Apache-2.0 오픈소스라 코드를 누구나 볼 수 있다 [확인].
  - Claude Code는 비공개 상용 라이선스다 [확인].
- **기능은 거의 같아졌다**: 계획 모드, 서브에이전트, 훅, 스킬, MCP, 플러그인, 코드 리뷰 [확인]. "기능이 아니라 성격과 가격으로 고르는 시대."
- **신기한 사실**: Codex에는 `/import`가 있다. "Claude Code에서 설정과 최근 대화를 가져오기"라는 기능이다. 그만큼 경쟁이 치열하다. [확인]
- **규칙 파일**: Claude는 CLAUDE.md, Codex는 AGENTS.md를 읽는다. Claude Code는 AGENTS.md도 읽을 수 있다. [확인]
- **성격 차이** (유튜버 3명이 같은 결론)
  - Claude는 시키지 않은 것까지 더 하고, 더 길게 쓰고, 더 오래 걸린다.
  - Codex는 시킨 것만 빨리 한다.
- **비용 차이** (Nathan의 자체 테스트, API 환산)
  - 둘 다 만점에 시간도 3초 차이였다.
  - 비용은 Opus 약 $5, Sol 약 $1.24로 약 4배 차이.
- **반전** (Nathan의 자체 테스트): 테스트 765개를 전부 통과했는데도 6개 중 3개는 문서 예제를 망가뜨렸다. "초록불 = 끝"이 아니다.
- **작은 모델도 충분하다** (Nathan의 자체 테스트): 가장 싼 Haiku가 다섯 과제 모두 만점에 $0.91. 쉬운 버그는 모든 모델이 40초 안에 고쳤다.
- **회사 벤치마크는 각자 유리한 판이다** (회사 자체 발표)
  - Anthropic 발표: Terminal-Bench 4.0에서 Opus 5.5 66.4%, Astra 57.9%.
  - 하지만 effort 설정이 서로 다르다.
- **추천 공식**
  - 빠르고 싸게 많이 → Codex.
  - 꼼꼼한 리뷰와 큰 작업 → Claude Code.
  - 돈이 되면 둘 다(설계·리뷰는 Claude, 구현은 Codex).
  - 가장 좋은 방법: 한 달 $20로 내 작업에 직접 써 보기.
- **사용량**
  - Claude는 5시간 창과 주간 한도가 있고 채팅과 한도를 같이 쓴다 [확인].
  - Codex는 Plus 기준 5시간마다 15~160 메시지(OpenAI 추정치) [미확인].
  - 세 유튜버 모두 "Codex가 한도가 더 넉넉하다고 느낀다"고 했다(체감).
