---
name: naver-blog-autopilot
description: 네이버 블로그(blog.naver.com/no4angel) 자동 글쓰기. 사용자가 "부동산글쓰기", "주식분석", "재테크 블로그 써줘"(또는 "블로그 써줘"), "경제학 책"이라고 입력하면 해당 워크플로를 처음부터 발행 직전(임시저장)까지 실행한다.
---

# 네이버 블로그 자동 글쓰기 (Aside에서 쓰던 것과 동일)
**Claude Code에서 실행할 때는 먼저 `claude-code-windows.md`를 읽고, Aside 전용 도구 자리는 그 문서의 대체 방법으로 실행한다.**

## 트리거 → 따라야 할 문서
| 사용자가 입력 | 읽을 문서 |
|---|---|
| 부동산글쓰기 | references/realestate-blog.md |
| 주식분석 | references/stock-analysis.md (+ finance-blog.md의 문체·입력 방법) |
| 재테크 블로그 써줘 / 블로그 써줘 | references/finance-blog.md |
| 경제학 책 | references/economics-book-blog.md (+ realestate-blog.md 3~5절 스타일·입력 방법) |

각 문서를 끝까지 읽고 그 순서 그대로 실행한다. 선택지는 문서에 적힌 개수(10지선다/5지선다/20권 목록)로 묻는다. 선택 후에는 더 묻지 않고 자료 조사 → 원고 → 그림 → 네이버 입력 → 태그 → 임시저장까지 끝낸다. **발행 버튼은 절대 누르지 않는다.**

## 실행 환경 (중요)
- 이 워크플로는 사용자의 PC에서 로그인된 브라우저가 필요하다. 브라우저 작업은 `aside-browser` 스킬(= Aside CLI, `aside guide`)로 수행한다. 문서 안의 `openTab`, `snapshot`, `page.locator(...)`, `frameLocator('#mainFrame')`, `filechooser` 코드는 Aside 브라우저 REPL 기준이므로 그대로 쓴다.
- 클라우드(☁) 세션에서는 이 PC의 브라우저·파일에 접근할 수 없다. 클라우드 세션이면 "로컬 세션에서 실행해 주세요"라고 안내하고 멈춘다.
- 네이버 로그인이 풀려 있으면 로그인 화면을 띄우고 사용자가 직접 로그인하게 한다. 비밀번호를 묻거나 저장하지 않는다.
- 파일 경로: 초안·그림은 C:\Users\Admin\Desktop\네이버블로그_초안\ 에 저장. 업로드용 파일이 다른 폴더에 있어야 하면 임시 폴더로 복사해서 사용.
- PowerShell 클립보드(HTML 붙여넣기)는 Windows PowerShell 5.1 `-STA`로 실행한다(realestate-blog.md 5절).

## 공통 원칙
- 숫자는 기사 2곳 이상 교차 확인, 출처를 글 끝에 남긴다.
- 경험담은 실제 수치로 계산한 "있을 법한 직장인 시나리오"로 쓰고, 지어낸 개인 수익률·매매 내역은 쓰지 않는다.
- 그림은 직접 캡처하거나 HTML로 만든 표·카드만 쓴다(뉴스 사진·남의 블로그 이미지 금지).
- 끝에 투자 유의 문구. 특정 종목 매수 권유·수익 보장 표현 금지.

