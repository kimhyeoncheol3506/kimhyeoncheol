# Jev 사실 정리표 (2026-11-06)

대상: AI 입문자용 얼굴없는 해설 영상(약 10분).
표시 규칙:
- **[확인]**: 제가 직접 페이지를 열어 본 내용입니다. 주소를 같이 적었습니다.
- **[미확인]**: 2차 자료에만 있거나 원문을 열지 못한 내용입니다.
- **⚠모순**: 자료끼리 말이 다른 내용입니다.
- **[유튜버 자체 테스트]**: 참고 영상 속 숫자입니다. 공식 수치가 아닙니다.

조사 시점은 2026-11-06입니다. 회사 홈페이지·문서·블로그는 이날 직접 받아 읽었습니다. 개발자 콘솔(console.typesafe.ai)은 Cloudflare가 막아서 열지 못했습니다.

---

## 1. 한 줄 정의

**Jev(제브)는 글을 쓰지 않고 "판단"만 돌려주는 AI 모델입니다.** 상황(state)과 질문 목록을 보내면, 미리 정해 둔 보기 중 하나와 확률을 숫자로 돌려줍니다. 대화·글쓰기·코딩은 하지 못합니다. [확인] https://docs.typesafe.ai/introduction , https://docs.typesafe.ai/introduction/coding-agents

- 만든 곳은 미국 샌프란시스코의 **TypeSafe AI**입니다. Jev는 이 회사의 첫 공개 모델이고, 회사는 이것을 "System One 모델"이라는 새 종류라고 부릅니다. 홈페이지 문구는 "Jev is TypeSafe's first public System One Model"입니다. [확인] https://typesafe.ai
- 이름의 유래는 두 갈래입니다. "System One"은 카너먼의 책 『생각에 관한 생각(Thinking, Fast and Slow)』에 나오는 빠른 직관(시스템 1)과 느린 추론(시스템 2) 구분에서 왔습니다. "Jev"는 경제학자 윌리엄 스탠리 제번스(제번스의 역설)에서 왔습니다. 지능이 싸지면 쓰임새가 폭발적으로 늘어난다는 뜻을 담았다고 합니다. [확인] https://typesafe.ai/blog/introducing-system-one-models-and-jev

## 2. 누가 만들었나 (회사·창업자·투자)

| 항목 | 내용 | 근거 |
|---|---|---|
| 회사 | TypeSafe AI, 샌프란시스코. 2024년 창업, 2년간 비공개로 개발 | [확인] 출시 글, SiliconANGLE https://siliconangle.com/2026/09/16/typesafe-ai-exits-stealth-with-40m-to-build-ai-for-use-by-software/ |
| CEO | Diogo Almeida(디오고 알메이다). OpenAI에서 RLHF·InstructGPT를 연구했고 그 전에는 Google Brain에 있었음 | [확인] https://typesafe.ai/team |
| COO | Sasha Sheng. Meta/FAIR 연구 엔지니어 출신 | [확인] 팀 페이지 |
| CTO | Erik Gafni. Ravel 창업자, Invitae·Freenome 초기 직원 | [확인] 팀 페이지 |
| 시드 투자 | 4천만 달러, DCVC 주도. Forbes는 기업가치를 2억 달러로 보도 | [확인] SiliconANGLE. Forbes 원문은 [미확인] |
| 시리즈 A | 2026-10-09 발표. 8억 7천만 달러, 기업가치 75억 달러. a16z 주도, Sequoia·DCVC 참여, Martin Casado 이사회 합류 | [확인] https://typesafe.ai/blog/series-ai |
| 사용 규모 | "포춘 500대 기업의 3분의 1이 사용 중", "출시 며칠 만에 사용자 100만 명" | 첫째는 회사 블로그에서 [확인]했지만 회사 자체 주장입니다. 둘째는 Substack 글에만 있어 [미확인]이며, 고객 이름은 공개된 적이 없습니다 |

- "창업자가 ChatGPT를 만든 사람"이라는 표현은 과장되기 쉽습니다. 회사 팀 페이지는 "RLHF와 InstructGPT를 공동 발명했다"고 적고 있습니다. 2차 자료에 따르면 그는 InstructGPT 논문 저자 20명 중 4번째입니다([미확인]). 대본에는 "ChatGPT가 말을 잘 듣게 만든 연구(RLHF)에 참여한 사람" 정도로 쓰는 편이 안전합니다.

## 3. 출시일과 버전 역사

| 날짜 | 일 | 근거 |
|---|---|---|
| 2026-09-15 | Jev 출시(얼리 액세스, 대기자 명단). 출시 글 작성자는 Diogo Almeida | [확인] 출시 글 |
| 2026-09-18 | TechCrunch 보도. 수요가 몰려 API가 잠시 서비스를 못 했다고 함 | [확인] https://techcrunch.com/2026/09/18/a-new-kind-of-ai-model-from-a-chatgpt-inventor-is-thrilling-developers/ |
| 2026-09-21 | Vercel AI Gateway에서 Jev 호출 지원 | [확인] https://vercel.com/changelog/ai-gateway-now-supports-typesafe-clients-and-http-api-for-jev |
| 2026-09-20~22 | 전체 공개 후 신규 가입 일시 중단이라는 보도 | [미확인] 2차 블로그 여럿. ⚠모순: "대기자 명단이 없어졌다"는 글도 있음. 11-06 기준 홈페이지에 "Join Waitlist" 버튼이 있음 [확인] |
| 2026-10-07 | Jack & Jill 사례 공개 | [확인] https://typesafe.ai/blog/jack-jill-jev-case-study |
| 2026-10-09 | 시리즈 A 발표 | [확인] |
| 2026-10-14 | **Jev 1.14**(`jev-1.14.0`) 출시. 다국어 개선, 이미지 위치를 찾는 **Box** 질문 신설, 이미지 입력, 긴 문맥(262k) 옵션 | [확인] https://typesafe.ai/blog/jev-1-14 , https://docs.typesafe.ai/changelog |

**"1.14에서 눈이 생겼다"는 표현은 반만 맞습니다.** 회사 설명은 이렇습니다. "여러분이 쓰던 jev-1.13.0도 사실 처음부터 멀티모달이었다." 이미지 입력은 1.13에서도 됩니다. 1.14에서 새로 생긴 것은 이미지 속 위치를 상자로 돌려주는 Box 질문입니다. 이미지와 긴 문맥은 "Danger Zone" 헤더(`TypeSafe-Danger-Zone-Images: true`)를 켜야 쓰는 실험 기능입니다. 회사도 "아직 실서비스용으로 보증하지 않는다"고 했습니다. [확인] 1.14 블로그
⚠모순: 1.14 블로그는 이미지를 Danger Zone 헤더로 켠다고 했습니다. 그런데 현재 모델 문서는 입력 항목에 "Text, images"라고만 적었습니다. 헤더가 지금도 필요한지는 [미확인]입니다.

## 4. 쉬운 말로: 어떻게 작동하나

- **보내는 것 두 가지**: `state`(상황. 글, JSON, 이미지)와 `questions`(질문 목록). [확인] https://docs.typesafe.ai/introduction/quickstart
- **질문은 네 가지 모양만 됩니다.** [확인] 위 문서

| 질문 종류 | 하는 일 | 돌려주는 것 |
|---|---|---|
| Choice | 보기 중 하나 고르기 | 고른 보기, 보기별 확률, 확신도 |
| Score | 정해 둔 단계(루브릭)로 점수 매기기 | 점수, 단계별 확률, 확신도 |
| Noul | 이 말이 참인가? | 0~1 사이 확률 |
| Box (1.14부터) | 이미지 속 어디에 있나? | 상자 좌표, 확신도 |

- 질문 여러 개를 한 번에 보내면 **병렬로 각각 따로** 판단합니다. 질문을 늘려도 응답 시간이 거의 늘지 않습니다. 대신 질문끼리 서로의 답을 참고하지는 못합니다. [확인] 소개 문서
- 문서가 권하는 사용법은 이렇습니다. 큰 질문("이 사업계획 몇 점?")을 작은 질문(시장 크기? 기술 가능성? 차별점?)으로 쪼갭니다. 그리고 작은 답들을 **내 코드에서** 합칩니다. 회사 표현으로는 "smart if-statements(똑똑한 if문)"입니다. [확인] 소개 문서, 출시 글
- 기존 LLM과의 차이: LLM은 글자를 한 토큰씩 차례로 씁니다. Jev는 모든 답의 확률을 한 번에 냅니다(회사 표현은 "parallel sampler"). 새 학습법의 이름은 RLCD(Reinforcement Learning for Calibrated Decisions)입니다. [확인] 홈페이지·출시 글
- 학습 데이터: CEO가 TechCrunch에 "합성 데이터로만 학습했다"고 말했습니다. 구조는 공개하지 않았고, 외부에서는 오픈 웨이트 LLM 위에 만들었을 것으로 추측합니다. [확인] TechCrunch

## 5. 공식 속도·비용 주장 (정확한 숫자와 비교 대상)

### 5-1. 홈페이지 큰 글씨: "193.6x Faster, 444.6x Cheaper"
- 각주는 "based on workflows for System One tasks"입니다. [확인] https://typesafe.ai
- 출처는 회사가 직접 만든 "워크플로 평가" 4개입니다(보안 경보 처리, 에이전트 기록 점검, 송장 처리, 고객 상담). 출시 글에는 이렇게 적혀 있습니다. "홈페이지의 193.6배, 444.6배는 여기서 나왔으며, **실제 사용에서 얻을 이득 중 높은 쪽**일 것으로 본다." [확인] 출시 글, https://evals.typesafe.ai/
- **비교 대상**: 정답 기준은 "GPT-6 Astra와 Claude Fable 5.1(둘 다 high thinking) 답의 평균"입니다. 이 기준과 비교한 모델은 Claude Haiku 4.5·Sonnet 5·Opus 5, OpenAI Luna·Terra·Sol, DeepSeek v4 flash·pro입니다. [확인] evals 사이트
- **193.6배와 444.6배가 정확히 어느 모델과 비교한 값인지는 회사가 밝히지 않았습니다.** [미확인] evals 표의 반올림된 숫자로 제가 계산해 보면, "송장 처리" 워크플로의 Claude Opus 5와 거의 맞습니다. 비용 $0.4856 대 $0.0011은 약 441배, 시간 92.1초 대 0.5초는 약 184배입니다. 이 값은 추정입니다.
- 같은 evals의 **4개 평균**은 다음과 같습니다. [확인]
  - Jev: 정확도 67.8%, 건당 $0.0004, 0.4초
  - Claude Opus 5(워크플로): 73.1%, $0.1761, 37.8초
  - OpenAI Sol: 74.1%, $0.0836, 23.3초
  - OpenAI Luna: 66.8%, $0.0033, 12.9초
  - Claude Sonnet 5: 67.8%, $0.1174, 78.1초

  → **Jev는 가장 똑똑한 모델보다 정확도가 5~6%p 낮습니다.** 그 대신 비용은 수백 분의 1, 시간은 수십~수백 분의 1입니다. "같은 수준"이라는 말은 Sonnet 5나 Luna와 비슷하다는 뜻으로 받아들이는 편이 정확합니다.
- 이 평가에 대해 회사 스스로 밝힌 한계는 다음과 같습니다. [확인] 출시 글
  - 워크플로는 회사 직원이 만들어서 편향이 있을 수 있습니다.
  - OpenAI·Anthropic 모델 쪽으로 기울어진 기준입니다.
  - 속도는 미국 서부 노트북에서 쟀습니다.
  - LLM에는 회사가 만든 래퍼를 씌워서 더 느리고 비쌀 수 있습니다.

### 5-2. 그 밖의 공식 숫자
- 홈페이지 시연 화면: Jev는 $0.000081에 0.114초, LLM은 $0.013880에 8.566초 걸렸습니다. [확인] 홈페이지. 출시 글에 따르면 이 시연의 비교 상대는 GPT-5.6 Terra(기본 추론)입니다. 회사도 "입력이 짧아 우리에게 유리하게 보인다"고 인정했습니다. [확인]
- 출시 글: 응답 시간은 70ms~500ms이고, 같은 수준 지능 기준으로 "40배~200배 빠르다"고 합니다. LLM은 3~329초가 걸린다고 적었습니다. [확인]
- 홈페이지: "Claude Fable 5.1보다 입력 가격이 238배 낮다"고 합니다. [확인]
- SiliconANGLE 보도: 워크플로 1,000건당 Jev 39센트, GPT-5.6 Luna $3.31, Claude Haiku 4.5 $19.49입니다. [확인] 기사 본문. 지금 evals 수치와는 다릅니다. ⚠모순: 평가가 갱신된 것으로 보입니다.
- 외부 사례 [확인] TechCrunch
  - Vercel 엔지니어: 명령어 안전 분류기를 OpenAI Luna 5.6에서 Jev로 바꾸자 5~18배 빨라지고 더 정확해졌습니다.
  - Bryo AI CTO: 이메일 분류에서 Gemini가 조금 더 정확했지만 10~20배 비쌌습니다.
- 회사 사례 Jack & Jill [확인] 사례 글
  - Gemini 3.1 Flash Lite를 Jev로 바꿨습니다.
  - 후보자 1,000명당 비용 $0.755 → $0.092(88% 절감), 처리 시간 20.3초 → 10.3초.
  - 품질 지표는 93.9% → 94.6%입니다.
  - ⚠모순: 같은 글 안에 "지난주 약 50만 달러를 아꼈다"는 인용과 "연 50만 달러 절감 예상"이 함께 있습니다.

## 6. 가격

- **입력 100만 토큰당 $0.042**(10억 토큰당 $42)이고, **출력은 무료**입니다. 1.13과 1.14 가격이 같습니다. [확인] https://docs.typesafe.ai/models
- 회사는 "보조금으로 싸게 파는 게 아니라고 증명할 수는 없다. 가격은 앞으로 내려갈 것으로 본다"고 직접 밝혔습니다. [확인] 출시 글
- 전용 가격표 페이지는 따로 없고, 모델 문서와 홈페이지에 적혀 있습니다. [확인] /pricing 주소 없음
- **무료 사용분은 공식 문서에서 찾지 못했습니다.** [미확인]
  - 윤자동: "공식 대기 신청 후 무료 $5 크레딧을 받았다"(9-20 기준)
  - 코딩애플: "최소 5달러 결제해서 써야 한다"
  - AI 투데이: "카드 없이 구글 계정으로 시작했다"
  - ⚠모순: 세 영상의 말이 서로 다릅니다. 계정마다, 시점마다 조건이 다른 것으로 보입니다.
- Vercel 무료 프로모션은 2026-09-25에 끝났다고 합니다. [미확인] 윤자동 설명란
- OpenRouter에는 `typesafe/jev-router` 항목이 있습니다. [확인] https://openrouter.ai/api/v1/models . 버전별 항목(jev-1.13, jev-latest)이 있다는 말은 2차 자료에만 있습니다. [미확인]
- **비교용: OpenAI Decisions API**(아래 9번)는 gpt-6-luna를 쓰고 입력 100만 토큰당 $0.10, 출력 무료입니다. [확인] https://developers.openai.com/api/docs/guides/decisions

## 7. 잘하는 것과 못하는 것 (회사 공식)

**잘하는 것** [확인] 출시 글, 코딩 에이전트 문서
- 분류, 라우팅(어느 모델·팀으로 보낼지), 점수 매기기, 참·거짓 검사, 가드레일(위험 메시지 거르기), LLM 결과 검증
- 대량 처리(맵리듀스), 0.1초가 중요한 실시간 앱
- 출시 글의 재미있는 시연: 둠(Doom) 게임 플레이(초당 10회 판단, 시간당 약 7달러), 위키피디아 링크 따라가기 게임

**못하는 것 / 약점** [확인] https://docs.typesafe.ai/model-jaggedness
1. 글 쓰기, 대화, 코드 작성: 아예 안 됩니다. "글이 필요하면 다른 모델을 쓰라"고 합니다.
2. 계산과 숫자 세기: 계산은 코드로 하라고 합니다.
3. 날짜 비교: 날짜는 Jev로 뽑아내고, 비교는 코드로 하라고 합니다.
4. 여러 단계를 거치는 추론(System 2 작업)
5. 글자 그대로 읽기: 말한 뜻이 아니라 쓴 글자대로 답합니다.
6. 관계없는 내용이 많은 긴 입력: 정확도가 떨어집니다(context rot).
7. 악의적 입력(프롬프트 주입)에 흔들릴 수 있습니다.
8. 보기 순서: 앞에 있는 보기를 고르는 경향이 있습니다.
9. 영어 외 언어: 1.14에서 다국어가 개선됐다고 했지만, 참고 영상들은 한국어가 약하다고 지적합니다.

**"환각 0%"는 정확히 무슨 뜻인가**
- 회사 주장의 정확한 의미는 "답이 항상 내가 준 보기 중 하나"입니다. 즉 형식(타입)이 틀리지 않는다는 말입니다.
- 판단 자체가 틀리지 않는다는 뜻은 아닙니다. 회사도 "오답 대신 확신도를 같이 준다"는 식으로 설명합니다. [확인] 홈페이지 "Zero Hallucinations" 문구, 출시 글
- 그래프의 0%는 측정한 값이 아니라 "구조상 보장"이라서 넣은 숫자라고 회사가 직접 적었습니다. [확인]

## 8. 초보자가 써 보는 법

1. **브라우저 Playground(코드 없음)**: console.typesafe.ai/playground 에서 상황 글을 붙이고 질문을 추가합니다. [확인] 빠른 시작 문서. 가입이 막혀 있을 수 있습니다. 11-06 기준 홈페이지에 "Join Waitlist"가 있습니다.
2. **Claude Code에 공식 스킬 설치**: [확인] 빠른 시작 문서, https://docs.typesafe.ai/agent-skill
   - Claude Code에서 `claude plugin marketplace add typesafe-ai/skills`를 실행한 뒤 `claude plugin install typesafe@typesafe-ai`를 실행합니다.
   - 다른 에이전트에서는 `npx skills add typesafe-ai/skills --skill typesafe-ai`를 씁니다.
   - 이 스킬은 **Jev를 Claude의 두뇌로 바꾸는 것이 아닙니다.** Claude가 Jev를 부르는 코드를 제대로 짜도록 돕는 안내서입니다. 공식 문서에도 "Claude Code의 모델을 Jev로 바꾸는 설정은 없다"고 적혀 있습니다.
   - MCP 서버는 공식 문서에서 찾지 못했습니다. [미확인]
3. **Python SDK**: `pip install typesafe-sdk`를 설치하고, `TYPESAFE_API_KEY` 환경변수를 정한 뒤, `client.system_one(state=..., questions=...)`를 호출합니다. JavaScript는 `@typesafe-ai/sdk`입니다. [확인] 빠른 시작 문서, 모델 문서
4. **HTTP API**: `POST https://api.typesafe.ai/v1/systemone`이고, 모델 이름은 `jev-latest`(현재 1.14.0)입니다. [확인] 모델 문서
5. **우회 경로**: OpenRouter, Vercel AI Gateway. [확인] Vercel 변경 기록, OpenRouter 모델 목록

**Aside 연동**: TypeSafe 공식 문서·블로그에서는 "Aside" 연동을 찾지 못했습니다. [미확인] 확인된 브라우저 쪽 사례는 둘입니다.
- browser-use 팀의 "jev-ultrafast" 브라우저 자동화 에이전트 [미확인]
- 코딩애플이 언급한 "Jev를 브라우저와 이어 붙여 자동 탐색"
- "Jev + Aside" 조합은 배움의 달인 영상의 주장입니다(자막 상태는 아래 참고 영상 표를 보세요). 대본에는 "유튜버가 이렇게 조합했다"로만 써야 합니다.

## 9. "GPT-6 Decisions API"는 무엇인가 (중요)

- **Jev 제품이 아닙니다. OpenAI가 만든 경쟁 제품입니다.** [확인] https://developers.openai.com/api/docs/guides/decisions , OpenAI 변경 기록 https://developers.openai.com/api/docs/changelog
  - 2026-10-06: 베타 출시. 모델은 `gpt-6-luna`, 주소는 `POST /v1/decisions`. "Responses API보다 약 10배 빠르게 타입이 정해진 답을 준다"고 합니다.
  - 2026-10-22: 정식 출시(GA). 질문 한도 200→400개, 프롬프트 캐시, 질문 안 이미지 지원.
  - 질문 종류: predicate(참일 확률), choice, score. Jev의 Noul·Choice·Score와 구조가 거의 같습니다.
  - 가격: 입력 100만 토큰당 $0.10, 출력 무료. Jev($0.042)의 약 2.4배입니다.
  - Microsoft Foundry(Azure)에서도 같은 API를 제공합니다. [확인] https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/decisions
- 잔재미코딩 영상 제목 "Jev 1.14, GPT-6 Decisions API 와 성능 비교"는 **Jev 1.14와 OpenAI의 Decisions API를 비교한다**는 뜻입니다. 제목만 보면 "Jev의 Decisions API"로 오해하기 쉽습니다.
- "Decisions API가 2026-09-29 OpenAI DevDay에서 발표됐다"는 말은 2차 자료에만 있습니다. [미확인]
- 같은 이름에 주의할 점: Jev의 공식 엔드포인트 이름은 "System One API"(`/v1/systemone`)입니다. Decisions API라는 이름은 OpenAI 쪽입니다.
- GPT-6 Astra는 Jev 평가에서 정답 기준(참고 답)으로 쓰인 OpenAI 모델입니다. 회사 블로그에 따르면 GPT-5.6 Terra는 시연 비교 상대입니다.
- 비슷한 무료 대안: 오픈소스 "Laya"를 다룬 영상이 여럿 있습니다(코드팩토리, 잔재미코딩, 단테). [미확인] 내용은 확인하지 않았습니다.

## 10. 보안·개인정보

- "입력(prompt 등)으로 어떤 AI 모델도 학습하거나 미세조정하지 않는다"고 합니다. [확인] https://typesafe.ai/legal/privacy-policy
- 개인정보는 "서비스에 합리적으로 필요한 기간" 동안 보관합니다. 데이터를 저장하지 않는 옵션(ZDR)은 엔터프라이즈 고객에게만 줍니다. [확인] https://docs.typesafe.ai/legal
- 1.14부터 "모델 문제 찾기에 내 질의를 써도 된다"는 선택 동의(opt-in)가 생겼습니다. 그래도 학습에는 쓰지 않는다고 합니다. [확인] 1.14 블로그
- 고객마다 따로 미세조정하지 않고, 모든 계정이 같은 가중치를 씁니다. [확인] 모델 문서
- 서비스 서버는 미국 서부에 있습니다. [확인] 출시 글. 한국에서 쓰면 응답이 더 느릴 수 있습니다.
- 문서에 따르면 상황 글 안의 악의적 지시(프롬프트 주입)에 흔들릴 수 있습니다. [확인] 약점 문서
- API 키 관리는 일반 원칙과 같습니다. 환경변수에 두고, 유출되지 않게 합니다. [확인] 빠른 시작 문서

## 11. 최근 2주 소식 (2026-10-23 ~ 11-06)

- 10-22: OpenAI Decisions API 정식 출시. 경쟁이 본격화됐습니다. [확인]
- 10-30: 평범한 사업가 영상. MAD 팟캐스트 속 창업자 인터뷰를 해설했습니다. [확인] 유튜브 메타데이터
- 11-02: Substack 「What Exactly Is TypeSafe Defending?」. 회사의 해자(따라잡히지 않을 힘)를 의심하는 글입니다. 2018년 BERT 분류기와 비슷한 발상이라는 점, 사용자 수 같은 자체 발표 수치를 검증할 수 없다는 점을 지적합니다. [확인] https://henrymichaelson1.substack.com/p/what-exactly-is-typesafe-defending
- 11-03: implicator.ai 사용법 가이드. [미확인]
- 그 밖에 신제품·소송·경영진 변화 소식은 찾지 못했습니다. 11-06 기준 별 공식 공지가 없습니다(블로그 최신 글은 10-14 Jev 1.14). [확인] 홈페이지 블로그 목록

## 12. MAD 팟캐스트

- 평범한 사업가 영상 설명란에 "TypeSafe CEO 디오고 알메이다가 Matt Turck의 MAD 팟캐스트에서 설명한 방법"이라고 적혀 있습니다. [확인] https://www.youtube.com/watch?v=J3aTUBcsDik 설명란
- 팟캐스트 원본 회차는 열지 못했습니다. [미확인] 해설 영상의 챕터로 본 핵심 주제는 다음과 같습니다.
  - "달러당 지능"
  - "똑똑한 if문"
  - "95% 아인슈타인, 5% 미스터 빈": 95%는 천재처럼 하지만 5%는 엉뚱한 실수를 하면 자동화를 맡길 수 없다는 뜻
  - 긴 프롬프트 이메일 비서의 한계
  - 확률과 임계값

---

## 참고 영상별로 가져올 기법

(자막 원문은 `analysis/jev/<약칭>.txt`에 있습니다. 숫자는 모두 **[유튜버 자체 테스트]**입니다.)

<!-- VIDEO_SECTION -->

## 대본에 바로 쓰기 좋은 요점

<!-- SCRIPT_POINTS -->

## 주의할 점

<!-- CAVEATS -->
