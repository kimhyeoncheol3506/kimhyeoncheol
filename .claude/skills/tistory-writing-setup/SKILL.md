---
name: tistory-writing-setup
description: "글쓰기 세팅법". 티스토리(journal35061.tistory.com, 월급쟁이 재테크 스킬)에 5개 카테고리(주식분석 / 서울 부동산 / 경제학 책 / 재테크 기초 / 경제 뉴스 정리) 글을 하나씩, 지금부터 3·6·9·12·15시간 뒤로 예약 발행한다. 카테고리마다 네이버 블로그 인기 글 1편의 편집 스타일을 따라 쓰고, 주제는 10지선다를 만들어 랜덤으로 고른다. "글쓰기 세팅법", "티스토리 예약 글쓰기", Aside 시작 팝업에서 "예"를 눌렀을 때 실행.
---

# 글쓰기 세팅법 (티스토리 5개 카테고리 예약 발행)

## 0. 시작 조건
- Aside를 켜면 10초 뒤 Windows 팝업(`C:\Users\Admin\AsideTools\tistory-popup.ps1`, 시작프로그램 등록)이 "티스토리에 주식분석 / 서울 부동산 / 경제학 책 / 재테크 기초 /경제뉴스 정리 관련 각 카테고리 별로 글쓰기 예약을 할까요?"라고 묻는다. "예"를 누르면 Aside CLI로 이 스킬 실행 세션이 열린다.
- 사용자가 직접 "글쓰기 세팅법"이라고 해도 실행한다.

## 1. 규칙 (사용자 지정, 2026-11-04)
1. 5개 카테고리에 각각 1편씩.
2. 카테고리마다 네이버 블로그(또는 티스토리)에서 최근 1주 글을 검색해, 인지도 있고 방문자가 많은 블로거 3명을 추린 뒤 그중 1편을 골라 **그 글의 편집 방식(소제목 형식, 인용구·구분선·표 사용, 색, 말투, 길이, 그림 배치)을 그대로** 따라 쓴다. 매번 다른 편집이 되도록, 직전 실행에서 쓴 블로거는 피한다.
3. 내용 주제는 카테고리별로 10지선다를 만든 뒤 `Math.random()`으로 하나를 고른다. 사용자에게 묻지 않고 진행한다. 헷갈리는 지시만 사용자에게 묻는다.
4. 예약 시간 (2026-11-04 변경): **하루 3편, 시간은 랜덤.** 5편을 이틀에 나눠(첫날 3편, 다음날 2편) 07:00~22:59 사이에서 난수로 시각을 뽑는다(분 단위까지 랜덤, 같은 날 글끼리 최소 2시간 30분 간격). 이미 예약된 글이 있는 날은 합쳐서 3편을 넘기지 않게 다음 날로 넘긴다. 카테고리 순서도 섞는다.
   - 예: `const m=7*60+Math.floor(Math.random()*960)` 를 뽑아 정렬 후 간격 검사.
5. 등록(예약 버튼 누른 날) 기준으로도 하루 공개 발행 한도의 절반 이하만 사용. 공식 한도는 2018.10.22 이후 가입 계정 하루 공개 15건(예약 포함, **예약을 등록한 날** 기준 합산) → 최대 7건. 이 스킬은 5건이라 한도 안. 같은 날 다른 글을 이미 발행했다면 합쳐서 7건을 넘지 않게 줄인다.

## 2. 참고 블로그 고르기 (REPL)
- 검색(최근 1주, 관련도순): `fetch('https://search.naver.com/search.naver?ssc=tab.blog.all&query=<검색어>&nso=so%3Ar%2Cp%3A1w')` → 본문에서 `https://blog.naver.com/<id>/<logNo>` 추출.
- 블로그 인지도: `fetch('https://m.blog.naver.com/api/blogs/<id>', {headers:{referer:'https://m.blog.naver.com/'}})` 응답 텍스트에서 `subscriberCount`, `dayVisitorCount`, `totalVisitorCount`.
- 점수 = 구독자 + 일방문자×20. 제목에 카테고리 키워드가 있는 글만. 상위 3개 중 가장 최근·주제가 맞는 1편 선택.
- 검색어 예: 주식분석 → "주식 종목분석 급등", 서울 부동산 → "서울 아파트 재건축 정리", 경제학 책 → "경제학 책 추천 서평", 재테크 기초 → "재테크 기초 직장인 정리", 경제 뉴스 → "오늘의 경제뉴스 정리".
- 편집 분석: `PostView.naver?blogId=&logNo=` 를 openTab → `.se-main-container > .se-component` 순서(text/image/quotation:스타일/horizontalLine/table/oglink), 정렬, 색(`span[style*=color]`), 배경색, 굵게 수, 글자 수를 뽑아 그대로 흉내 낸다. (분석 탭 screenshot은 시간초과가 잦으니 쓰지 않는다.)

## 3. 주제별 자료
- 주식분석: `stock-surge-analysis` 스킬의 급등주 수집·공시·추세 지표 방법. 10개 후보 중 랜덤.
- 서울 부동산: `seoul-realestate-blog` 스킬의 트렌드 조사. `C:\Users\Admin\Desktop\AI 관련\네이버블로그_초안\부동산_구_기록.md`에 있는 최근 구는 빼고 10개 후보.
- 경제학 책: `economics-book-blog` 스킬의 20권 수집 중 `경제학책_기록.md`에 없는 10권 후보.
- 재테크 기초: 연금저축·ISA·파킹통장·소득공제 등 10개 후보.
- 경제 뉴스 정리: 최근 1주 핵심 이슈 10개 후보. 숫자는 기사 2곳 이상 교차 확인, 글 끝에 출처.
- 공통: 경험담은 실제 숫자로 계산한 "있을 법한 직장인 시나리오"만. 투자 권유 금지, 유의 문구 필수. 그림은 직접 캡처하거나 HTML로 만든 카드만(뉴스 사진·남의 블로그 이미지 금지).

## 4. 그림 만들기
- HTML 카드: openTab('about:blank') → `document.write` → 화면 캡처는 첫 시도에서 CDP 시간초과가 잦다. bringToFront + 1.5초 대기 후 재시도(최대 4회)로 전체 화면을 찍고 `boundingBox()` 값으로 `%TEMP%\crop.ps1 <src> <dst> x y w h`(System.Drawing)로 자른다.
- 주가 차트: `https://stock.naver.com/domestic/stock/<코드>/price`, 뷰포트 1800x950, "3개월" 클릭 후 전체 캡처 → 차트 (355,295,990,395), 시세 (15,205,310,430) 자르기.

## 5. 티스토리 입력·예약 (검증됨)
- 로그인은 자주 풀린다. `/manage/newpost/`가 로그인 화면으로 가면 카카오 로그인 화면을 띄우고 사용자에게 직접 로그인 요청(비밀번호 받지 않기).
- 에디터는 TinyMCE. 사진: 툴바 `button "첨부"` → 메뉴 `menuitem "사진"` 클릭과 동시에 filechooser.setFiles → 본문에 `[##_Image|kage@..._##]` 코드가 생김. 사진을 먼저 모두 올려 코드를 받아 두고, 본문 HTML에 코드를 원하는 위치에 넣는다.
- 본문: `tinymce.activeEditor.setContent('')` 후 `execCommand('mceInsertContent', false, html)` + input/change 이벤트 + 본문 끝에 공백 한 글자 입력(이걸 안 하면 저장 안 됨). 제목 `[placeholder="제목을 입력하세요"]` fill.
- 인용구 `<blockquote data-ke-style="style1|style2|style3">`, 구분선 `<hr data-ke-style="style1~style8">`, 표 `<table data-ke-style="style12|style13|style8">`, 글자 크기 `<p data-ke-size="size16">`.
- 카테고리: `combobox "카테고리 선택"` 클릭 → `option "<카테고리명>"`. 태그: `textbox "태그입력"` 에 입력+Enter 10개.
- `완료` → 발행 창: `label[for="open20"]`(공개) 클릭 → `button "예약"` → `textbox "시간"`, `textbox "분"` 입력(날짜 버튼은 기본 오늘, 다음 날이면 날짜 버튼으로 변경) → `button "공개 발행"`.
- 확인: `/manage/posts/` 목록에 `[예약]제목`과 `카테고리 · 날짜 시각`이 보이면 성공. 마지막에 목록 화면 캡처로 보고.

## 6. 기록
- 실행할 때마다 `C:\Users\Admin\Desktop\AI 관련\네이버블로그_초안\티스토리_예약_기록.md`에 날짜, 카테고리, 제목, 예약 시각, 참고한 블로거 id를 추가한다(다음 실행 때 같은 블로거·주제를 피하는 용도).
