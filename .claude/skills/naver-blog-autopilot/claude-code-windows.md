# Claude Code (Windows 로컬 세션) 실행 보조 문서

원본 문서(SKILL.md, references/*.md)는 Aside 기준으로 쓰여 있다. Claude Code에서 실행할 때는 원본의 순서·규칙·문체를 그대로 따르되, **Aside 전용 도구가 나오는 자리만** 아래 표대로 바꿔서 실행한다. 이 문서에 없는 내용은 원본이 우선이다.

## 0. 실행 전 확인
- Windows PC의 **로컬 Claude Code 세션**에서만 실행한다. 클라우드 세션이면 원본 지시대로 "로컬 세션에서 실행해 주세요"라고 안내하고 멈춘다.
- `playwright-cli` 명령이 있는지 확인한다(`playwright-cli --version`). 없으면 사용자에게 `npm install -g @playwright/cli` 설치를 안내하고 멈춘다(사용자 동의 없이 설치하지 않는다).
- 브라우저 조작은 같은 리포지토리의 `playwright-cli` 스킬(.claude/skills/playwright-cli/SKILL.md) 사용법을 따른다.

## 1. 도구 대응표

| 원본(Aside) | Claude Code에서 |
|---|---|
| `aside-browser` 스킬, `aside guide` | `playwright-cli` 스킬 |
| 브라우저 시작 | `playwright-cli open --headed --persistent` (화면에 띄우고, 로그인 상태를 프로필에 유지) |
| `openTab(url)` | 첫 페이지는 `playwright-cli goto <url>`, 새 탭은 `playwright-cli tab-new <url>` |
| `snapshot` | `playwright-cli snapshot` (요소 ref 확인) |
| `page.locator(...)`, `frameLocator('#mainFrame')`, `page.evaluate(...)`, `keyboard.insertText`, `waitForEvent('filechooser')` + `setFiles` | 원본 코드를 `playwright-cli run-code "async page => { ... }"` 안에 그대로 넣어 실행. 길면 `.js` 파일로 저장 후 `playwright-cli run-code --filename=<파일>` |
| 뷰포트 1800x950 | `playwright-cli resize 1800 950` |
| 스크린샷(페이지/요소) | `playwright-cli screenshot` 또는 run-code 안에서 `locator('#card').screenshot({ path: '...' })` |
| 키 입력(Ctrl+V, End, Backspace, Enter) | `playwright-cli press Control+v` 등, 또는 run-code 안에서 `page.keyboard.press(...)` |
| `fetch(url)`(뉴스 검색, RSS, 예스24, fchart, ac.stock 등) | `WebFetch` 도구. 원문(XML·JSON)이 필요하면 `curl -s "<url>"` 또는 run-code 안의 `fetch`(run-code에서 fetch 사용 가능) |
| WebSearch | Claude Code의 `WebSearch` 도구 그대로 |
| REPL에서 계산(이동평균, MACD, ADX, ATR 등) | Python(`python -c` 또는 초안 폴더에 `.py` 저장 후 실행)이나 Node로 계산. 결과 수치를 검산한다 |

## 2. 선택 질문 (10지선다 / 5지선다 / 20권)
Claude Code의 `AskUserQuestion`은 보기를 최대 4개까지만 받는다. 그래서:
1. 보기 전체(10개·5개·20개)를 **채팅에 번호 목록**으로 보여 준다. 각 줄은 원본의 label·description 형식 그대로("N. 제목 — 설명").
2. "번호로 답해 주세요(직접 입력도 가능)"라고 묻고 답을 기다린다.
3. 보기 개수·구성 규칙은 원본 그대로 지킨다. 선택이 끝나면 원본대로 더 묻지 않고 끝까지 진행한다.

## 3. 네이버 로그인
- `playwright-cli open --headed --persistent` 로 연 브라우저에서 `https://blog.naver.com/GoBlogWrite.naver` 로 이동한다.
- 로그인 화면이 나오면 **사용자가 그 창에서 직접 로그인**하게 하고 기다린다. 비밀번호를 묻거나 입력·저장하지 않는다. `--persistent` 프로필이라 다음부터는 로그인이 유지된다.
- 크롬 쿠키를 꺼내 넣는 방식은 쓰지 않는다.

## 4. 파일·경로
- 초안·그림 폴더는 원본 그대로: `C:\Users\Admin\Desktop\네이버블로그_초안\` (없으면 만든다). 기록 파일(`문체_학습노트.md`, `부동산_구_기록.md`, `경제학책_기록.md`)도 이 폴더에 둔다.
- 원본에 나오는 다른 스킬 경로는 이 스킬 안의 문서로 바꿔 읽는다.
  - `C:\Users\Admin\.aside\u\0\skills\naver-finance-blog\SKILL.md` → `references/finance-blog.md`
  - `C:\Users\Admin\.aside\u\0\skills\seoul-realestate-blog\SKILL.md` → `references/realestate-blog.md`
- 사진 업로드(`setFiles`)는 실제 파일 경로를 그대로 넘긴다. 업로드 파일이 다른 폴더에 있어야 하면 원본대로 임시 폴더로 복사해서 쓴다.

## 5. PowerShell (클립보드 HTML 붙여넣기, 이미지 자르기)
- Claude Code의 셸에서 `powershell.exe -STA -NoProfile -ExecutionPolicy Bypass -File <스크립트.ps1>` 로 **Windows PowerShell 5.1**을 호출한다(pwsh 7이 아님).
- 스크립트는 초안 폴더에 `.ps1`로 저장해서 실행한다. 한글이 들어가면 **UTF-8 BOM**으로 저장한다(PowerShell 5.1이 BOM 없는 UTF-8을 깨뜨림).
- CF_HTML 헤더 작성, `Windows.Forms.DataObject`, `System.Drawing` 자르기 방법은 원본(realestate-blog.md 5절, finance-blog.md) 그대로.
- 클립보드에 넣은 뒤 붙여넣기는 playwright-cli로: 본문 문단 클릭 → `playwright-cli press Control+v`. 붙여넣기 후 글자 수로 검증한다.

## 6. 그림 만들기 (HTML 카드·표)
- 원본의 `about:blank` + `document.write` 방식을 run-code로 그대로 실행하거나, HTML 파일을 초안 폴더에 저장하고 `playwright-cli tab-new file:///C:/Users/Admin/Desktop/네이버블로그_초안/<파일>.html` 로 연다. `python -m http.server`는 쓰지 않아도 된다.
- 요소 스크린샷은 run-code에서 `await page.locator('#card').screenshot({ path: 'C:/Users/Admin/Desktop/네이버블로그_초안/<이름>.png' })`.

## 7. 끝까지 지킬 것 (원본과 동일)
- **발행 버튼은 절대 누르지 않는다.** 상단 "저장"(임시저장)까지만. 태그 입력용으로 연 발행 설정 창 안의 "발행" 버튼도 누르지 않는다.
- 검증(표시자 0개, 그림 수, 인용구 수, 태그 10개, 임시저장 시각) 후 `playwright-cli screenshot` 으로 화면을 찍어 보고한다.
- 끝나면 브라우저는 열어 둔 채 사용자에게 넘긴다(사용자가 읽고 직접 발행).
