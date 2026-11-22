---
name: x-pool-collect
description: 쓰레드봇 "X" 주제용 소재 모으기. 사용자(@no4angel1981)가 팔로우하는 X 계정들의 최근 조회수 높은 원글을 twitter 글로벌로 수집해 C:\Users\Admin\AsideTools\threads-bot\xpool\pool.json 에 합친다. "X 풀 수집", "x-pool-collect" 요청 시 사용. 질문하지 말고 끝까지 진행.
---

# X 풀 수집 (1회 실행)

브라우저 탭을 열 필요 없음. REPL의 `twitter` 글로벌(로그인 계정 @no4angel1981)만 쓴다. 사용자에게 아무것도 묻지 않는다. X에 글/좋아요/팔로우 등 쓰기 동작은 절대 하지 않는다(읽기만).

## 절차 (REPL 한 번에 실행해도 됨)
1. `fs.readFile('C:\\Users\\Admin\\AsideTools\\threads-bot\\xpool\\following.json','utf8')` → 핸들 배열. 그중 무작위 25개.
2. 핸들마다 `await twitter.getUserTweets(h, {count: 20})` (실패하면 건너뜀, 호출 사이 `sleep(800)`).
3. 원글만 남김: `inReplyToId` 없음, 리트윗 아님(`text`가 "RT @"로 시작하지 않음, `author.screenName`이 h와 같음), 광고 아님.
   최근 72시간(`createdAt`) 안의 글만.
4. 작성자별 조회수 중앙값 대비 비율 `rel = views / median(views)`. `rel >= 1.2` 이거나 그 작성자 상위 2개.
5. 버림: 홍보/경품/giveaway/airdrop/referral/추천인 코드/"link in bio"/특정 코인 매수 선동(shill)/정치 선전/성인/도박(rainbet 등). 텍스트 20자 미만 버림.
   우선: 한국어 글, 또는 금융·주식·코인·AI·경제 주제.
6. 항목 형식:
   `{id, url: "https://x.com/<h>/status/<id>", author: h, text, views, likes, rel, media: [사진/영상 썸네일 url 배열], createdAt: ISO, lang: "ko"|"en"|..., topicHint: "주식|코인|AI|경제|기타"}`
   lang은 한글 포함 여부로 판단해도 됨.
7. 기존 `C:\Users\Admin\AsideTools\threads-bot\xpool\pool.json`(없으면 `{"items":[]}`)을 읽어 id 기준 중복 제거 후 합침. 기존 항목의 `used:true`는 유지. `createdAt` 최신순 200개만 남겨 UTF-8로 저장:
   `{"updated": ISO, "items": [...]}`
8. 마지막에 "X 풀: 새로 N개, 전체 M개" 한 줄만 출력하고 끝.
