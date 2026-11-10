# 클로드 듀엣(Claude Duet) 팩트시트 — 2026-11-10

뉴럴서랍 롱폼(S2 neon, 약 10분) `projects/duet_neon.yaml` 대본용 자료. 기준일 2026-11-10. 조사: 일꾼C(Claude).

## 0. 조사 방법
- 아래 5개 원문을 이 세션에서 **curl 로 직접 열어** 본문을 읽었다(모두 HTTP 200). [확인] = 원문에서 직접 읽은 문장.
- 참고 유튜버 자료: `analysis/muse/yeopjari_full.txt` 는 이 컨테이너에 없었다(분석 폴더가 git 에 없음). 대신 `projects/muse_neon.yaml` 의 `yeop` 출처 facts(옆자리 연구원 「AI 비서 3파전」 정리)를 그대로 썼고, 영상에서는 **"한 유튜버 정리"** 로 밝힌다.
- 확인 못 한 것: **울트라 요금제 월 가격**(요금표 본문에 숫자가 안 나옴 → 말하지 않음), 한국 출시 계획(공식 언급 없음 → "미국만"으로만 말함).

| id | 원문 | 날짜 | 주소 |
|---|---|---|---|
| product | 제품 페이지 "Claude Duet — A proactive AI agent" | 2026-11-10 열람 | https://claude.com/product/claude-duet |
| launch | 발표 글 "Introducing Claude Duet" | 2026-10-21 | https://claude.com/resources/articles/claude-duet |
| safety | "Claude Duet Safety, Privacy, and Security" | 2026-10-23 | https://claude.com/resources/articles/claude-duet-safety-privacy-and-security |
| help | 도움말 "Get started with Claude Duet" | 2026-11 갱신 | https://support.claude.com/en/articles/17631495-get-started-with-claude-duet |
| link | 도움말 "How to use Link by Stripe with Claude Duet" | 2026-11 갱신 | https://support.claude.com/en/articles/17666484-how-to-use-link-by-stripe-with-claude-duet |
| shoppay | 도움말 "How to use Shop Pay with Claude Duet" | 2026-11 갱신 | https://support.claude.com/en/articles/17666489-how-to-use-shop-pay-with-claude-duet |
| pricing | 요금표 claude.com/pricing | 2026-11-10 열람 | https://claude.com/pricing |

## 1. 무엇인가 [확인]
- "Claude works as a proactive agent. It comes to you with what needs your attention, completes tasks you ask of it, keeps working even when you step away, and checks with you before it acts on your behalf." (launch)
- 대상: "professionals and small business owners with more on their plates than they can track." (launch)
- 일반 클로드와 차이: "The Claude app waits for you to open a chat… Claude Duet comes to you." (product FAQ)
- 모델: "Powered by Opus 5.5" (product) / "You can't choose a model. Claude Duet runs on Claude Opus 5.5 and decides how much effort a job needs." (help)
- 클로드 계정의 기억·스킬·커넥터를 이어받음(product, launch, help).
- 6,000개 넘는 커넥터·플러그인(Claude Marketplace) (product, launch).
- 상태: 리서치 프리뷰(research preview), 대기 명단(waitlist). 발표 2026-10-21, 안전 글 10-23.

## 2. 누가·어디서·요금 [확인]
- 미국의 Pro·Max·Ultra 구독자, 대기 명단 초대 순서대로. Team·Enterprise 는 아직 아님(나중에 계획) (help, product).
- 필요 조건 3: Pro/Max/Ultra 플랜 · 미국 클로드 계정 · 대기 명단 초대 (help).
- 접근 권한은 대기 명단에 적은 이메일에 묶임 → 클로드 계정·폰의 구글/애플 계정 메일과 같아야 함 (help).
- 앱: iOS·안드로이드 단독 앱 + 컴퓨터에서는 claude.ai 웹 (product). 메인 클로드 앱과 따로(launch).
- 요금: "During the research preview, Claude Duet is included with Pro, Max, and Ultra plans at no extra cost." (help)
- 요금표(pricing): Free 0달러 / Pro 월 결제 20달러(연간 결제 시 월 17달러, 200달러 선결제) / Max 월 100달러(Pro의 5배 사용량) / Ultra: Pro 주간 사용량 10배·5시간 한도 없음(가격 숫자 확인 못 함).
- 사용량: 플랜 한도(5시간·주간)를 다른 클로드와 함께 씀. 아침 브리핑·점검 같은 백그라운드 일도 한도에 포함 → 채팅만 할 때보다 빨리 닳을 수 있음 (help, launch).
- 한도 리셋 선물: Pro 3번, Max·Ultra 1번, 2026-12-15 만료 (help).

## 3. 어떻게 일하나 [확인]
- 클라우드에 자기 컴퓨터(가상 머신)와 자기 브라우저 → 내 노트북·폰이 꺼져도 일함 (launch, help).
- 몇 시간마다(every few hours) 연결 계정 점검: 쉬지 않고 보면 한도가 너무 빨리 닳기 때문 (launch).
- 아침마다 짧은 브리핑, 낮에는 필요할 때만 메시지 (launch, product).
- 한 줄기 대화(스레드)에 문자·음성 메시지. 주제별 채널도 만들 수 있고 기억은 공유 (help).
- 탭: Tasks(하는 일·내 입력 필요한 일), Make(완성한 문서·시트·덱·대시보드) (help, product).
- 작업 완료 표시는 사용자만 할 수 있음 (help).
- 숫자·요약을 줄 때 어느 메일·파일·시트에서 왔는지 알려 줌 (help).
- 승인 못 하면 나머지 일은 끝내 두고 승인만 나중에 다시 가져옴 (help).

## 4. 할 수 있는 일 [확인]
- 아침 브리핑, 받은편지함·캘린더에서 나를 기다리는 것 표시, 답장 초안 (product).
- 퀵북스·스트라이프에서 미수금 찾고 독촉 메일 초안 / Gusto 급여 준비 / 링크드인 채용 공고(편집·승인 뒤) / Docusign 계약서 / HubSpot 후속 메일 / 캔바 캠페인 / 쇼피파이 스토어 (launch).
- 브리프·덱·대시보드·재무 모델, 프로토타입·웹앱 (launch, product).
- 커넥터 없는 사이트는 자기 클라우드 브라우저로 (help).
- 결제: Stripe의 Link(디지털 지갑), Shopify의 Shop Pay. 구매마다 승인 + 그 가게·그 금액에만 쓰이는 일회용 카드, 진짜 카드 번호는 공유 안 됨. 카드 끝 4자리·유효기간·청구 주소만 봄. 정기 결제는 못 함. 미국 결제 수단 필요(Link) (launch, safety, link, shoppay).
- 곧: 1Password 로그인(launch, safety).
- 테스터 사례(launch): Jess(부동산 중개) — 시키지 않았는데 잘못된 날짜에 잡힌 매물 보여 주기를 찾아냄 / Amin(플로리다 케밥 식당, 직원 약 110명) — "탭 100개를 열 필요가 없다" / Mya(브랜드 전략가) — 통화가 비행기 직전인 걸 알아채고 옮기자고 제안.

## 5. 안전장치·금지선 [확인]
- 보내기·결제·서명·삭제 전에 할 일·받는 곳·내용(받는 사람 전부)을 보여 주고 승인 대기 (safety, help, launch).
- 별도 자동 검사(클로드 코드 auto mode 분류기 확장)가 행동마다 내 의도와 맞는지 확인, 일하는 모델 바깥에서 돌아서 페이지에 숨은 지시가 못 건드림 (safety).
- **허락해도 안 되는 일**: 증권 매매, 계좌 간 이체 같은 은행 업무, 남의 계정 접속 (safety, help, launch).
- **"다시 묻지 않기"가 안 되는 일**: 결제·송금, 주문 삭제, 계정 만들기 (safety).
- 승인 피로(approval fatigue)를 고려해 묻는 횟수를 조정 중 (safety).
- 민감 정보 분류기 2단계: ① 절대 공유 안 함 — 로그인 정보, 카드·계좌 전체 번호, 신분증 번호(내가 시켜도) ② 동의 필요 — 건강·재정 등. 내가 직접 시킨 건 동의로 봄(치과 예) (safety, launch).
- 비밀번호·쿠키·로그인 토큰을 모델이 못 봄. 비밀번호는 앱 안 양식에 입력 → 일회용 키로 암호화 → 브라우저 기계에서만 풀림 (safety).
- 피싱 주의: 듀엣 로그인 양식은 내가 요청한 로그인 중 앱 안에서만 뜸. 링크·문자·메일·claude.ai 아닌 사이트로 오면 가짜 (safety).
- 브라우저는 따로 떨어진 가상 머신, 정해진 명령(열기·클릭·입력)만. 사이트 코드·쿠키는 브라우저 기계에 남음 (safety).
- 자기를 에이전트로 밝힘: 별도 User-Agent, 공개 IP 주소 공개, 출시 전 큰 사이트들에 차단 선택권 → 일부는 차단 선택 (safety).
- 시험: 레드팀, 외부 침투 테스트 회사(소스 코드 접근), 공개 버그 바운티(HackerOne) (safety, launch).
- 앱 연결 끊기: 그때부터 새 접근 멈춤, 이미 배운 기억은 메모리 리셋 전까지 남음. 계정 삭제 시 전부 지움 (safety, help).
- 프롬프트 인젝션: 읽은 내용을 정보로 다루도록 만들었지만 완벽한 방어는 없음 → 그래서 중요한 행동은 승인 (help).

## 6. 한계 [확인]
- 모델 선택 불가(오퍼스 5.5 고정), 브라우저 작업을 볼 수도 넘겨받을 수도 없음 (help, launch).
- 정해진 간격으로 점검 → 그 사이 급한 일이 올 수 있음 (help, product).
- 내 컴퓨터 파일·모든 프로젝트를 못 봄, 클로드 작업은 읽기만 (help).
- 전화·문자 못 함(이메일은 승인 뒤 가능) (help).
- 슬랙 등 일부 커넥터 제한, 마이크로소프트 365 아직, 개인 금융(Personal Finance) 안 됨 (help).
- 스레드를 잘못 읽거나 급한 정도를 잘못 판단할 수 있음 (product, launch, help).
- 업무 중심이라 티켓 예매 같은 개인 용무는 아직 덜 강함 (launch).

## 7. 한 유튜버 정리(옆자리 연구원 「AI 비서 3파전」, `projects/muse_neon.yaml` yeop facts)
- 듀엣은 클로드 프로 월 20달러에 포함, 미국 대기 명단.
- 한 매체 정리: 뮤즈 = 생활, 닷츠 = 큰 프로젝트, 듀엣 = 업무.

## 8. 영상에서 말하지 않는 것
- 울트라 가격 숫자, 한국 출시 시기, 우회 가입(VPN 등), 확인 못 한 SNS 반응.
