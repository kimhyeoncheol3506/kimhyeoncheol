# 제미나이 4 네온 사실 정리 (2026-11-22, 원문 열람)

영상 대본: `projects/neon4_neon.yaml`. 출처마다 열람 여부와 숫자를 적었다. 숫자는 모두 구글 자체 발표이며 독립 검증 전이다.

## 공식 출처 (직접 열람)
### 구글 블로그 「Introducing Gemini 4 Neon」 (2026-11-18)
- 주소: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/
- 가족 안의 역할: "Neon balances depth and efficiency". Carbon 은 가장 어려운 장기 작업, Hydrogen 은 빠른 일상 실행을 맡는다.
- 비용: "32% lower cost per task than Carbon". 기본 생각 단계 high 기준이다.
- 순위: AA Intelligence Index 61, #3 overall. 생각 단계 xhigh 기준이며 "just behind larger, slower models".
- 가격: 입력 3달러, 출력 15달러(100만 토큰당). 컨텍스트 100만 토큰.
- 이용처
  - Gemini API(AI Studio), Gemini for business
  - Antigravity(Pro·Ultra 유료)
  - Gemini 앱(Pro·Ultra)
  - Android Studio(유료 등급)
- 데모
  - WebGL2 스키 시뮬레이터
  - 튜링 1936년 연구실 3D
  - 사진 한 장을 10만 칸 구글 시트로
- 앱 사용 예: 청구서 분석, 영수증 대조로 환불 협상.

### 딥마인드 모델 카드
- 주소: https://deepmind.google/models/model-cards/gemini-4-neon/
- 바탕: adapted from Gemini 4 Carbon.
- 입력·출력: 텍스트·이미지·오디오·동영상을 읽고, 텍스트로 답한다.
- 길이: 컨텍스트 1M, 동기 출력 기본 64K.
- 지식 기준: 2026년 3월.
- 벤치마크 (네온 / Opus 5.5 / GPT-6.2 Sol)
  - AA 61 / 59 / 57
  - Vals 70.9 / 70.1 / 66.1
  - AutomationBench 56.3 / 42.5 / 41.3
  - Terminal-bench 4.1 65.2 / 65.8 / 61.5 → Opus 가 더 높음
- 한계
  - 환각이 생길 수 있다.
  - 생물학 CBRN 과 사이버 분야에서 위험 기준선(CCL)을 넘었을 가능성을 배제할 수 없다(아르곤 결과를 이어 씀).

### AI Studio 가격표
- 주소: https://aistudio.google.com/docs/pricing
- 네온
  - "not available on the Free tier"
  - 입력 3.00달러, 출력 15.00달러, 캐시 0.15달러
  - Batch 1.50달러 / 7.50달러
- 카본·아르곤: 11/30 까지 2달러/10달러, 12/1 부터 4달러/20달러.

### 구글 클라우드 개발자 문서
- 주소: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-4-neon
- 생각 단계: LOW, MEDIUM, HIGH, XHIGH 네 단계이고 기본값은 HIGH.
- 길이: 1,048,576 토큰(입력+출력 합산), 기본 출력 65,536.

### 한국 구독 페이지
- 주소: https://gemini.google/kr/subscriptions?hl=ko
- AI Pro: 네온·하이드로젠
- Ultra: 카본·네온·하이드로젠
- AI Pro 원화 가격은 페이지에 없음.

## 언론·리뷰 (직접 열람)
- 지디넷코리아 11/19: 네 번째 제미나이 4 모델이며, 프로·울트라 가입자에게 순차 제공.
- AI타임스 11/19: 세계 3위, 작업 비용 32% 절감.
- 이코노미트리뷴 11/19.
- The Decoder 11/18: 한 달에 네 번째, 이미지·오디오 생성은 못 함.
- Digital Trends 11/18: 구글 자체 수치라는 경고.
- Flavio Copes 11/19
  - 짧은 코딩 작업은 생각이 길어 작업당 비용이 오퍼스의 약 3배.
  - 긴 글 찾기는 오퍼스보다 42% 쌈.
  - 출력 속도 초당 약 122토큰.
  - 짧은 일에는 low 추천.
- Analytics Vidhya 11/19

## 말하지 않은 것
- AI Pro 원화 가격: 공식 페이지에 없음.
- '아르곤 대체': Digital Trends 한 곳에만 나옴.
- API 의 한국 이용 여부: 공식 문구가 없음.
- Vertex AI 라는 이름: 블로그에 없음.
- Wes Roth 영상: 직접 보지 못함.
