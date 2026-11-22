---
name: threads-auto-post
description: "쓰레드 자동글" 1편 작성·게시. 프롬프트로 받은 주제(AI/부동산/주식/코인)와 글 길이로, 지금 가장 핫한 최신 뉴스 1개를 찾아 쌩초보가 지나가며 툭 던지는 블라인드/X 말투로 Threads(threads.com)에 바로 게시한다. "쓰레드 자동글", "쓰레드 글 써줘" 요청 시 사용.
---

# 쓰레드 자동글 (1회 실행 = 1편 게시)

스케줄러(`C:\Users\Admin\AsideTools\threads-scheduler.ps1`)가 1~3시간 난수 간격으로 `aside exec`를 불러 이 스킬을 실행한다.
프롬프트에 `주제=`, `길이=`, `첨부=`가 들어온다. 없으면 직접 난수로 정한다(주제 4개 균등, 길이 아래 표 가중치, 첨부는 4~5편 중 1편꼴, 연속 첨부 금지. 나머지는 `없음`).
사용자에게 아무것도 묻지 말고 끝까지 진행한다. 확인 없이 바로 게시한다(사용자 승인 완료).

## 1. 최신 핫뉴스 1개 고르기
- WebSearch(advanced)로 해당 주제의 "오늘/최근 몇 시간" 뉴스를 찾는다. 예: AI → "AI 오늘 발표", "오픈AI 엔비디아 속보"; 부동산 → "서울 아파트 오늘", "부동산 대책 속보"; 주식 → "코스피 오늘 마감", "특징주 급등"; 코인 → "비트코인 오늘 시세", "코인 속보".
- 네이버뉴스 속보 목록도 좋다(최신순, n.news.naver.com 기사 링크가 바로 나옴. `a.sa_text_title`의 innerText/href): 주식 https://news.naver.com/breakingnews/section/101/258 , 부동산 https://news.naver.com/breakingnews/section/101/260 , AI/IT https://news.naver.com/breakingnews/section/105/230 , 코인은 WebSearch "비트코인 속보" 또는 네이버 최신순 검색(https://search.naver.com/search.naver?where=news&sort=1&query=비트코인).
- 후보 중 **발행 시각이 가장 최근**이면서 화제성 있는 것 1개. 24시간 넘은 뉴스는 쓰지 않는다.
- `C:\Users\Admin\.aside\u\0\skills\user\threads-auto-post\posted.md` 최근 20줄을 읽고 같은 뉴스/같은 소재면 다른 걸로 바꾼다.
- 숫자(지수, 가격, 금리 등)는 기사에 있는 값만 쓴다. 지어내지 않는다.

## 2. 글 쓰기 규칙 (제일 중요)
화자: 이제 막 투자·AI 공부 시작한 30대 직장인 쌩초보. 뉴스 보다가 혼잣말처럼 툭 던짐. 내 얘기, 내 느낌 위주.

말투 (블라인드/X 실글 리듬):
- 반말 혼잣말 + 음슴체 섞기: "~임", "~함", "~듯", "~네", "~냐", "~노?", "~던데", "~각", "아 몰라"
- "ㅋㅋ", "ㅋㅋㅋ", "ㄷㄷ", "ㄹㅇ", "ㅠ", ";;", ".." 는 자연스럽게 0~2번. 매번 넣지 말 것
- 초보스러운 반응: "이거 사야됨?", "나만 모르는거임?", "뭔 소린지 반은 모르겠는데", "일단 장바구니만 담아둠", "물려있는 사람 손"
- 은어 약간: 국장/미장, 떡상/떡락, 물림, 존버, 익절/손절, 줍줍, 하닉/삼전, 비트, 집값 등
- 맞춤법 살짝 대충(띄어쓰기 빼먹기, "되/돼" 정도), 마침표 거의 안 씀, 줄바꿈으로 호흡
- 욕설·비하·정치 편들기·특정인 조롱 금지. 투자 권유("사라/팔아라" 단정) 금지, 그냥 내 생각/고민으로

절대 금지 (AI 티 나는 것):
- 이모지, 해시태그 남발(0개 기본, 넣어도 1개), 링크(첨부=뉴스링크/유튜브일 때만 1개 허용), 제목, 굵은 글씨, 글머리 기호, 번호 목록
- "정리하면", "핵심은", "결론적으로", "~에 대해 알아보자", "여러분", "~하시길 바랍니다", "주목할 만하다", "시사하는 바"
- 기사 요약체, 균형 잡힌 장단점 나열, 마지막에 교훈/질문으로 깔끔하게 마무리하는 구조
- 매번 같은 시작("오늘", "와")·같은 끝맺음 반복. 최근 게시글과 첫 단어가 겹치지 않게

길이 (프롬프트 `길이=` 값, 공백 포함 글자수):
| 값 | 글자수 | 모양 |
|-|-|-|
| 초단문 | 10~40 | 한 줄 툭 |
| 짧게 | 40~100 | 1~3줄 |
| 보통 | 100~220 | 3~6줄 |
| 길게 | 220~400 | 내 상황 썰 조금 + 뉴스 반응 |
최대 450자(Threads 500자 제한).

계정 주인(no3angel_k, "평범한 직장인. 4차산업에 관심이 많음")이 직접 쓴 실제 글 톤. 이게 1순위 기준:
- "학령인구가 ㄷㄷ" / "맞네" / "수학의 진심" / "운동의 해답을 찾았다. 이것만하면 될 듯"
- "완전 쌩초보로 유튜브 영상도 하나 만들었다. 실제로 내가 사용하는 도구로만 ㅋ"

예시 톤 (복붙 금지, 리듬만 참고):
- "비트 또 오르네 ㅋㅋ 나 팔고나니까 오르는거 국룰임?"
- "AI가 코딩 다 한다는데\n나는 아직 엑셀 vlookup도 검색해서 씀..\n이거 늦은거냐"
- "서울 집값 또 신고가래\n월급 300 모아서 언제 사냐 계산기 두드리다 그냥 껐음 ㅋㅋ"
- "코스피 빨간불인데 내 계좌만 파란불인거 실화냐;;"

## 2-1. 첨부 (매체) — AI 티 줄이기용
프롬프트 `첨부=` 값대로 한다. 사람이 폰으로 캡처하거나 링크 공유하는 느낌이 핵심. 본문은 첨부를 보고 반응하는 말투로("이거 봄?", "캡처해둠", "방금 본 영상인데", "이 차트 실화냐").
| 값 | 하는 일 |
|-|-|
| 없음 | 텍스트만 |
| 기사캡처 | 고른 기사를 폰 화면처럼 캡처해서 이미지 1장 첨부 |
| 차트캡처 | 주식=코스피/종목, 코인=비트코인 차트를 폰 화면처럼 캡처해서 첨부. 주제가 AI/부동산이면 기사캡처로 대신 |
| 뉴스링크 | 본문 마지막 줄에 기사 URL만 붙임(Threads가 자동으로 기사 카드 만듦). 네이버 기사는 n.news.naver.com 주소 사용 |
| 유튜브 | 같은 뉴스/주제의 최신 유튜브 영상 1개를 찾아 본문 마지막 줄에 URL(https://youtu.be/ID)을 붙임 |

캡처 방법 (REPL, 2026-11-04 테스트 완료). 이미지는 `C:\Users\Admin\.aside\u\0\skills\user\threads-auto-post\tmp\` 에 저장(폴더 없으면 생성):
- 공통: `await page.setViewportSize({width:400,height:780})` 후 페이지 열기 → 캡처 → 끝나면 `setViewportSize({width:1280,height:900})`로 되돌림.
- 기사캡처: 네이버 기사 `https://n.news.naver.com/mnews/article/...` 를 열고
  `page.evaluate(()=>{const t=document.querySelector('.media_end_head_headline, #title_area'); if(t){t.scrollIntoView({block:'start'}); window.scrollBy(0,-60);} })` → 0.7초 뒤 `page.screenshot({path})`. 다른 언론사 원문이면 같은 기사를 네이버뉴스에서 찾아 쓴다(데스크톱 사이트는 폰 화면처럼 안 나옴).
- 차트캡처: 코스피 `https://m.stock.naver.com/domestic/index/KOSPI/total`, 코스닥 `.../index/KOSDAQ/total`, 개별종목 `https://m.stock.naver.com/domestic/stock/종목코드/total`, 비트코인 `https://m.stock.naver.com/crypto/UPBIT/BTC`(이더리움 ETH, 리플 XRP). 2.5초 기다린 뒤 `page.screenshot({path, clip:{x:0,y:0,width:400,height:500}})` (가격+차트 부분만).
- 유튜브: `youtube.search('키워드', {limit:8, lang:'ko', region:'KR'})` → 후보마다 `youtube.getMetadata(id)`로 게시일 확인, 48시간 이내 + 조회수 있는 것 중 1개. 없으면 7일 이내까지 허용, 그래도 없으면 첨부=뉴스링크로 바꿈. 쇼츠/광고/라이브 제외.
- 캡처 이미지는 `display()`로 한 번 보고, 로딩 중/팝업/빈 화면이면 다시 찍는다.

## 3. Threads에 게시
(2026-11-04 실제 게시 성공한 절차)
1. `openTab('https://www.threads.com/')` → `snapshot(page,{interactive:true})`. 로그인 상태면 피드 상단에 button "텍스트 필드가 비어 있습니다..."("새로운 소식을 공유해보세요.")가 있다.
2. 로그인 팝업("Threads에서 소통해보세요", "Instagram으로 계속하기")이 보이면 로그아웃 상태: 게시하지 말고 `notification`으로 "쓰레드 로그인이 풀렸어요. Aside 브라우저에서 threads.com 다시 로그인해주세요" 알린 뒤 로그에 `LOGIN_REQUIRED` 남기고 종료.
3. 그 버튼 클릭 → dialog "새로운 스레드"가 열리고 textbox(본문)에 포커스. "커뮤니티 또는 주제" 칸은 비워둔다.
4. 줄마다 `page.keyboard.insertText(line)`, 줄 사이 `page.keyboard.press('Enter')` (Enter는 줄바꿈이고 게시 안 됨).
5. 이미지 첨부면: `page.locator('[role="dialog"] input[type="file"]').first().setInputFiles(경로)` → 3초 대기 → dialog에 "이미지"와 삭제 버튼이 보이면 성공. (이미지와 링크를 같이 넣으면 링크 카드는 안 생김. 링크 첨부일 땐 이미지 넣지 말 것. 링크만 넣으면 3초 뒤 기사/영상 카드가 자동 생성됨)
6. `document.querySelectorAll('[role="dialog"] [contenteditable="true"]')` innerText로 입력값 확인 → dialog 안 button "게시" 클릭.
7. 취소해야 할 땐 "취소" → "임시 저장하시겠어요?"에서 "저장 안 함".
8. 4초 뒤 `https://www.threads.com/@no3angel_k` 열어 첫 글이 방금 쓴 본문(첨부 포함)인지 확인.
9. 탭 닫기. tmp 폴더 이미지는 지워도 됨.

## 4. 기록
`C:\Users\Admin\.aside\u\0\skills\user\threads-auto-post\posted.md` 맨 아래에 한 줄 추가 (UTF-8, Bash에서 한글 깨짐 주의: REPL `fs.appendFile` 사용):
`- 2026-11-05 14:32 | 주식 | 짧게 | 첨부:차트캡처 | 뉴스제목(언론사, 발행시각) | 본문 한 줄로(줄바꿈은 / )`
실패 시에도 `FAIL: 이유`로 한 줄 남긴다.
