# GPT-6.1 테라(GPT-6.1 Terra) 팩트시트 — 2026-11-10

뉴럴서랍 롱폼(`projects/terra_neon.yaml`, S2 neon) 대본용. 조사: 클로드 일꾼F.

## 0. 조사 방법과 한계
- openai.com · help.openai.com 은 이 세션에서 **403**(curl, 2026-11-10: `openai.com/index/gpt-6-1-terra/`, `help.openai.com/...chatgpt-work-and-codex`). 발표 글과 벤치마크 점수는 열지 못했다.
- 대신 오픈에이아이 공식 문서 사이트 **learn.chatgpt.com** 은 열렸다. 주소 끝에 `.md` 를 붙이면 문서 원문(마크다운)이 나온다. 아래 [확인]은 모두 curl 로 직접 받은 것이고, 받은 사본은 `docs/research/openai-src/*.md` 에 있다.
- **벤치마크 점수는 열린 공식 문서 어디에도 없었다 → 영상에서 점수를 말하지 않는다**("점수표는 이번 문서에 없었다"로만).
- 한국 원화 가격·부가세는 확인 못 함 → 달러로만 말한다.
- 주제 선택: 테라(10월 26일 API·워크·코덱스 출시, 11월 4일 닷츠 합류) 뒤에도 GPT-Image-2.6(11/4, 그림 모델)과 GPT-6-Cyber(11/5, 승인받은 보안 연구용)가 나왔지만, 둘 다 누구나 고르는 대화·업무 모델이 아니어서 **테라를 1순위 주제로** 정했다. 두 모델은 한 장면에서 "참고로"로만 말한다.

## 1. 출처 (모두 [확인])
| id | 페이지 | 주소 | 사본 |
|---|---|---|---|
| terra | GPT-6.1 Terra 모델 문서 | https://learn.chatgpt.com/api/docs/models/gpt-6.1-terra | terra_model.md |
| guide | Using GPT-6 (가족 안내·이전 안내) | https://learn.chatgpt.com/api/docs/guides/latest-model | latest.md |
| price | API 가격표 | https://learn.chatgpt.com/api/docs/pricing | pricing.md |
| apicl | API 변경 기록(10/26 테라 출시, 11/4 이미지 2.6, 11/5 사이버, 10/28 구독자 API 크레딧) | https://learn.chatgpt.com/api/docs/changelog | changelog.md |
| wn | What's new 10월 26~30일(워크·코덱스 출시) | https://learn.chatgpt.com/codex/whats-new/october-26-30-2026 | wn_oct26.md |
| wn2 | What's new 11월 2~6일(11/4 닷츠 합류) | https://learn.chatgpt.com/codex/whats-new/november-2-6-2026 | wn_nov2.md |
| wmodels | 워크·코덱스 모델 안내 | https://learn.chatgpt.com/docs/models | work_models.md |
| wprice | 워크·코덱스 요금·사용량 | https://learn.chatgpt.com/docs/pricing | work_pricing.md |
| t56 | GPT-5.6 Terra 모델 문서 | https://learn.chatgpt.com/api/docs/models/gpt-5.6-terra | terra56_model.md |
| astra | GPT-6 Astra 모델 문서 | https://learn.chatgpt.com/api/docs/models/gpt-6-astra | astra_model.md |
| cu | Computer Use 안내 | https://learn.chatgpt.com/docs/computer-use | computer_use.md |
| credit | 구독자 API 크레딧 | https://learn.chatgpt.com/api/docs/guides/chatgpt-api-credits | chatgpt_credits.md |
| ctry | API 지원 국가 | https://learn.chatgpt.com/api/docs/supported-countries | countries.md |

## 2. 무엇인가
- "빠르고 효율적인 모델 — 시각 추론, 정확한 컴퓨터 사용, 분명하고 자연스러운 글쓰기." (terra, guide)
- 쓰임 예: 상품 사진을 카탈로그 항목과 맞추기, 기술 도면 해석·비교, 앱 화면에서 행동, 글 초안·고쳐 쓰기. (terra, guide)
- 워크 예: 거래처 룩북 상품 사진을 카탈로그와 맞춰 목록 갱신, 광고 이미지의 잘림·글자 위치 점검과 고칠 목록 정리. 글은 결과를 먼저, 뒷받침은 쉬운 말로. (wn)
- GPT-6 가족 4개: 아스트라(가장 똑똑, 가장 어려운 일) · 6.1 솔(아스트라에 가까운 성능, 더 쌈) · 6.1 테라(빠르고 효율적) · 루나(가장 빠르고 쌈). (guide, wmodels)
- 워크 모델 안내 아이콘: 속도 번개 — 아스트라 2 · 6.1 솔 3 · 6.1 테라 4 · 루나 4. (wmodels)
- 모델 ID `gpt-6.1-terra`. 입력 글·이미지, 출력 글. 소리·영상 지원 안 함. 문맥 창 1,050,000(최대 입력 922,000), 최대 출력 128,000 토큰, 지식 기준 2026년 6월 1일. (terra)
- 생각 깊이(reasoning effort): none·low·medium(기본)·high·xhigh·max. medium 에서 시작, 품질 향상이 시간·토큰만큼 값질 때 올리라. (terra, guide)
- 도구 호출은 Responses API 필요(Chat Completions 는 되지만 도구는 안 됨). 쓸 수 있는 도구: 웹 검색·파일 검색·이미지 생성·코드 실행기·호스티드 셸·apply_patch·스킬·컴퓨터 사용·MCP·도구 검색. 미세조정·predicted outputs 안 됨. (terra, guide)
- 클라우드: 아마존 베드록 `openai.gpt-6.1-terra`, 구글 클라우드 비공개 미리보기. (terra)

## 3. 이전 모델과 차이
- GPT-5.6 테라: "지능과 비용의 균형", 예전 GPT-5 가족의 mini 급에 해당. 입력 2달러·출력 12달러, 지식 2026년 2월 16일, 문맥 창 1,050,000·최대 출력 128,000(같음). (t56)
- GPT-6.1 테라: 입력 1달러·출력 5달러(100만 토큰당) → 입력은 절반, 출력은 절반보다 더 내려감. 지식 6월 1일로 더 최신. (terra, price)
- 이전 안내: 같은 생각 깊이로, 평소 쓰는 이미지·작업으로 두 모델을 비교하라. Chat Completions 로 도구를 부르면 Responses 로 옮기라. (guide)
- 아스트라 대비: 아스트라는 가장 어려운 끝까지 일(코드·앱·연구), 테라는 매일 하는 글쓰기·시각 업무. 화면·시각 판단이 까다로운 일은 Computer Use 문서가 아스트라를 권함. (wmodels, cu)
- none 생각 깊이: 테라는 지원, 아스트라·6.1 솔은 미지원. (guide)

## 4. 가격·사용량
- API 표준(100만 토큰당, 27만 2천 토큰 이하): 아스트라 10/50 · 6.1 솔 2/10 · 6.1 테라 1/5 · 루나 0.1/0.5 · 5.6 테라 2/12 달러(입력/출력). (price)
- 테라 캐시 입력 0.05달러(입력의 5%), 캐시 쓰기 1.25달러(30분)·2.50달러(12시간). 272K 넘는 요청은 전체가 입력·캐시 2배, 출력 1.5배. 배치·플렉스 50% 쌈. 빠른 모드 2배. 지역 처리 10% 더. (terra)
- 워크·코덱스 크레딧(100만 토큰당): 테라 입력 25·캐시 1.25·출력 125 / 아스트라 250·25·1,250 / 5.6 테라 50·5·300. (wprice)
- 플러스·스탠다드 비즈니스, 5시간당 로컬 메시지 어림값: 아스트라 5~45 · 6.1 솔 15~160 · 6.1 테라 35~285 · 루나 350~3,000. 고정 한도 아님, 주간 한도도 있을 수 있음, 클라우드 작업은 더 씀. 프로는 현재 5시간 한도 없음. (wprice)
- 요금제(월): Free 0 · Go 8 · Plus 20 · Pro 100/200/500 달러. Free·Go 카드에는 루나만. 테라는 Plus·Pro·Business·Enterprise·Edu. (wprice, wn)
- 10월 28일부터 자격 되는 Pro·Business 구독자는 API 크레딧을 월 최대 500달러(Pro 100달러 요금제 → 100달러 등). (apicl, credit)

## 5. 어디서 쓰나
- 챗지피티 **워크**(데스크톱 앱·웹, 워크는 모바일도)와 **코덱스**. 고급(Advanced) 메뉴의 모델 목록에서 고른다. **일반 채팅(Chat)에는 없음.** 아랍에미리트 지역 처리 미지원. 엔터프라이즈는 워크스페이스·관리자 설정에 따름. (wn, wprice)
- 코덱스 CLI 0.159.0 이상, `codex -m gpt-6.1-terra`. (wmodels)
- API: 10월 26일 출시(Responses·Chat Completions). (apicl)
- 닷츠: 11월 4일 "테라가 닷츠를 움직이는 모델 중 하나"가 됨. (wn2)

## 6. 컴퓨터 사용(Computer Use) 설정·한계
- 지원 지역에서 맥·윈도우 데스크톱 앱의 워크·코덱스. 설정 > 컴퓨터 사용 > Any App 켜기. 앱을 쓰기 전 허락을 묻고 '항상 허용' 목록은 지울 수 있음. 민감·방해되는 행동 전에도 물을 수 있음. (cu)
- 맥: 화면 기록·손쉬운 사용 권한. 윈도우: 대상 앱이 활성 데스크톱에 보여야 하고, 앞에서 마우스·키보드를 움직이므로 같은 세션을 동시에 쓰기 어려움. (cu)
- 부탁 예: `@Chrome 을 열어 최근 변경 뒤에도 결제 페이지가 되는지 확인해 줘`. (cu)
- 터미널 앱·챗지피티 자신은 자동 조작 못 함, 관리자 인증·보안 권한 승인 못 함. 내 브라우저를 쓰면 클릭·양식 제출·로그인한 행동이 내 계정에서 한 것으로 취급될 수 있음. (cu)
- 결과는 원본과 대조, 특히 이미지에서 가져온 이름·숫자. (wmodels)

## 7. 한국
- API 지원 국가 목록에 South Korea 있음. (ctry)
- 원화 가격·부가세: 확인 못 함 → 달러로만.

## 8. 그 뒤에 나온 것(참고)
- 11월 4일 GPT-Image-2.6 Sunburst·Flare(그림 생성·편집). 11월 5일 GPT-6-Cyber(허가된 환경에서 취약점 조사, Daybreak 설정 필요). (apicl)
