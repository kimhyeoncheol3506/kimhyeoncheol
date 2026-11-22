# naver-finance-blog — 클라우드(Claude Code, Linux) 실행 메모

SKILL.md는 Aside 원본이라 고치지 않는다. 클라우드에서 다른 점만 여기에 적는다.

## 클라우드에서 하는 범위
- **초안까지만.** 네이버·티스토리 로그인, 임시저장, 예약, 발행은 하지 않는다. 등록은 Aside나 PC에서 한다.
- 저장 위치: 저장소 `drafts/<블로그폴더>/YYYY-MM-DD_<영문-슬러그>.md`
  - 블로그 폴더: `naver-no4angel` / `mongtta` / `tistory-journal35061`
  - 파일 형식(2026-11-21 초안 14편과 같은 형식): 앞머리(blog, title, voice, status: 초안, checked_at, tags 10개) → 본문 → `## 이미지 아이디어` → `## 확인한 수치와 출처` 표 → `## 검토 메모`
- 글이 끝나면 커밋·푸시까지만 한다.

## Aside와 다른 점
- **선택 질문(10지선다·5지선다·20권):** 채팅에 번호 목록으로 보여 주고 번호로 답받는다. 사용자가 "알아서"라고 하거나 질문 없이 진행하라고 했으면 난수로 고른다.
- **겹침 검사:** PC의 기록 파일(`Desktop\AI 관련\네이버블로그_초안\*_기록.md`)은 클라우드에서 읽을 수 없다. 대신 아래 세 곳을 확인한다.
  1. 저장소 `drafts/` 안의 모든 초안 제목
  2. 공개 글 목록 `https://m.blog.naver.com/api/blogs/<블로그ID>/post-list?categoryNo=0&itemCount=30&page=1` (헤더 `referer: https://m.blog.naver.com/`). 클라우드에서 접근되는 것을 2026-11-22에 확인했다.
  3. 티스토리 `https://journal35061.tistory.com/` 첫 화면
  - 예약만 걸려 있고 아직 공개되지 않은 글은 위 방법으로 보이지 않는다. 그래서 초안의 검토 메모에 "PC 예약 목록과 겹침 확인"을 남긴다.
- **그림:** 클라우드에는 PowerShell이 없다.
  - HTML 카드·표는 Node의 `playwright`(설치돼 있음)나 `playwright-cli`로 열어 요소만 스크린샷을 찍는다.
  - 브라우저는 `/opt/pw-browsers/chromium`을 쓴다. 한글 폰트는 WenQuanYi가 있다.
  - 자르기는 Python PIL(설치돼 있음)로 한다.
  - png는 초안과 같은 폴더에 같은 이름으로 앞부분을 맞춰 저장한다.
- **WebSearch:** 연합·조선·중앙·매경 도메인은 검색 도구가 막는다. 다른 언론사나 공식기관 자료로 2곳 교차 확인한다.
- **Windows PC의 Claude Code에서 직접 실행하는 경우:** `../naver-blog-autopilot/claude-code-windows.md`의 도구 대응(playwright-cli, PowerShell 5.1 -STA 등)을 따른다. 초안 폴더 경로는 이 스킬 SKILL.md에 적힌 최신 경로(`Desktop\AI 관련\네이버블로그_초안`)가 우선이다.

## 클라우드 점검 결과 (2026-11-22)
- **설치돼 있음:** python3 3.13, requests, bs4, PIL, node 22, playwright 모듈, playwright-cli 0.1.22, ffmpeg
- **없음:** PowerShell
- **접근 확인(200):** stock.naver.com, fchart.stock.naver.com, api.stock.naver.com, ac.stock.naver.com, m.stock.naver.com API, dart.fss.or.kr, search.naver.com, news.google.com RSS, yes24.com, reb.or.kr, korea.kr, blog.naver.com, m.blog.naver.com API, journal35061.tistory.com, partners.coupang.com(첫 화면만)
- **막힘:** molit.go.kr(연결 끊김 → korea.kr 정책브리핑이나 언론 기사로 대체), job.alio.go.kr(연결 끊김 → 기관 채용 페이지나 기사로 대체)

## 이 스킬만의 차이
- 시장 숫자는 `api.stock.naver.com`·`fchart` 일봉으로 직접 계산할 수 있다. 차트 캡처는 `stock.naver.com` 화면을 playwright로 찍는다.
- 문체 학습노트(`문체_학습노트.md`)는 PC에만 있다. 클라우드에서는 SKILL.md의 문체 규칙만 적용하고, 검토 메모에 "PC 학습노트 반영 확인"을 남긴다.
