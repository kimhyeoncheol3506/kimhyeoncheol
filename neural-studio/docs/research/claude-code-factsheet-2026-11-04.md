# Claude Code 팩트시트 (2026-11-04 확인, 1차 자료만)

영상 「클로드코드 쌩초보도 딸깍」 대본용. 모든 항목은 2026-11-04 공식 페이지를 curl 로 직접 열어 확인(문서는 code.claude.com/docs/en/<page>.md).

## 많이 틀리는 것 (옛 영상과 달라진 점)
- 요금제: **Max $100(Pro의 5배)**, **Ultra $200(Pro의 10배, 인증 계정은 5시간 제한 없음)**. 'Max 20x'는 더 이상 없음. 무료(Free) 플랜에는 Claude Code 없음. Pro $20/월(연간 결제 시 $17/월). — https://claude.com/pricing
- 권한 모드: v2.1.283부터 **auto 가 기본 시작 모드**(배경에서 다른 모델이 위험한 동작을 걸러 줌). 하나하나 묻는 모드는 이제 **Manual**(default). Shift+Tab: auto → default → acceptEdits → plan. bypassPermissions 는 '격리된 컨테이너·VM 전용'. — /permission-modes
- `#` 메모 단축키 삭제(“CLAUDE.md 를 고쳐 달라고 말하라”). `/agents` 는 이제 메뉴 대신 안내만. — /changelog, /commands
- 기본 모델: Pro·Max·Ultra·Team·Enterprise·API 모두 **Opus 5.5**. Fable 5.1은 /model fable 로 고름(어느 요금제에서도 기본 아님). — /model-config

## 정의·어디서 쓰나
- “Claude Code is an agentic coding tool that reads your codebase, edits files, runs commands, and integrates with your development tools.” 터미널·IDE(VS Code/Cursor 확장, JetBrains 플러그인)·데스크톱 앱(Code 탭)·웹(claude.ai/code). 모바일 앱은 세션을 보는 리모컨. 유료 구독 필요. — /overview, /desktop, /mobile

## 설치
- macOS·Linux·WSL: `curl -fsSL https://claude.ai/install.sh | bash` / Windows PowerShell: `irm https://claude.ai/install.ps1 | iex` (자동 업데이트). Homebrew `brew install --cask claude-code`, WinGet `winget install Anthropic.ClaudeCode`. npm(Node 22+, sudo 금지). 확인: `claude --version`. 요구: macOS 13+, Windows 10 1809+, RAM 4GB+.
- 첫 실행: `cd 내프로젝트` → `claude` → 브라우저로 로그인.

## 초보 핵심
- `/init`(CLAUDE.md 만들기), CLAUDE.md(내가 쓰는 규칙)·Auto memory(클로드가 쓰는 메모), `/memory`
- `/help` `/clear` `/compact` `/model` `/resume` `/rewind`(=/checkpoint, /undo) `/usage`(=/cost) `/config` `/context` `/diff` `/plugin` `/mcp`
- Esc = 멈추기(한 일은 남김), Esc 두 번(빈 입력) = 되감기 메뉴, `@` = 파일 지정, `!` = 셸 명령
- 체크포인트: 보낸 프롬프트마다 저장. 단 Bash 로 바뀐 파일·바깥에서 바꾼 파일은 추적 안 됨 → Git 으로(깃허브 영상과 연결)

## 확장
- Skills(SKILL.md, /스킬이름) · Subagents(따로 일하고 요약만) · Hooks(정해진 순간 자동 실행) · MCP(외부 도구 연결 표준) · Plugins(묶음, 공식 마켓 claude-plugins-official)
- **Mods**: 클로드 코드의 모양과 동작을 바꾸는 플러그인(JS/TS). 2026-10-01 v2.1.287 추가. 믿을 만한 곳 것만 설치. /diff 도 내장 모드. — /plugins/mods/overview

## 최근 2주(2026-10-21~11-04)
- 새 모델 없음. 최신 v2.1.318(11-04). Opus 4.8 fast mode 지원 종료 예고(11-30 제거). Agent Skills 를 Agentic AI Foundation 에 기증(10-22).

## 안전
- 승인 전에 코드·명령을 직접 확인할 책임은 사용자에게. plan 모드로 먼저 살펴보기, /diff 로 바뀐 내용 보기, git push 같은 건 ask 규칙.

※ 확인 못 함: API 토큰 가격, Mods 블로그 발표문, # 단축키 삭제 날짜.
