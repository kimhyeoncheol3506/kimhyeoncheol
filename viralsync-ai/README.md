# ViralSync AI — AI 바이럴 마케팅 운영 플랫폼 (MVP)

광고대행사가 고객의 홍보 의뢰(블로그·유튜브·쇼츠·릴스·앱·상품)를 접수하고
**AI 분류·적합도 분석 → 홍보 후보 게시물 매칭 → 홍보 문구 초안 생성 → 사람의 검토·승인 → 모의 실행 → 실적 집계·보고**
까지 한 곳에서 운영하는 SaaS 웹 앱입니다.

> 이 디렉터리는 저장소 루트의 기존 사주·관상 앱과 **별개의 독립 프로젝트**입니다. 기존 코드는 수정하지 않았습니다.

## 광고 문의 → 견적 → 계약 → 집행 (문의 접수함)

크몽 등으로 들어오는 “우리 업체도 블로그 가능한가요? 가격은요?”, “예산은 얼마로 잡고 어떤 광고를 추천하나요?” 같은 문의를 처리하는 흐름입니다.

1. **문의 접수함 → + 문의 붙여넣기**: 고객 메시지 원문을 그대로 붙여넣기
2. **자동 분석** (규칙 기반, 링크 접속 없음): 브랜드, 업종(음식점·카페·뷰티·병원·교육·쇼핑·앱 등), 홈페이지/인스타/블로그/플레이스 링크 구분, 키워드, 고객이 요청한 매체, 고객 질문(가격·예산·추천·가능 여부), 예산·지역 → 빠진 정보는 “고객에게 더 물어볼 것”으로 표시
3. **추천 매체 + 3안 견적**: 고객 요청 매체를 우선하고 업종별 기본 전략(예: 음식점 = 플레이스 → 체험단 → 인스타 → 지역광고)으로 실속/표준/집중 견적 계산. 가격은 **서비스 상품** 화면의 내 가격표 기준이며, 판매하지 않는 매체는 자동 제외. 광고 매체비는 별도로 안내
4. **답변 초안**: 질문별 답변, 추천 구성, 견적, 진행 절차, 추가 요청 자료, 광고 표시·성과 비보장·크몽 안전결제 안내 포함. 견적안을 바꾸면 답변도 자동 갱신 → 복사해서 고객에게 발송
5. **계약 전환**: 클릭 한 번으로 고객·브랜드 프로필·캠페인(문의 원문 포함)·**매체별 집행 작업**을 생성하고 AI 분석 실행
6. **매체 집행 작업**: 블로그 포스팅·체험단·플레이스·인스타·광고 운영 등을 담당자에게 배정하고 진행 상태·결과물 URL을 기록 (결과물 또는 작업 내용 없이 완료 불가)

> 실제 블로그 발행·체험단 모집·플레이스 정비·광고 집행은 **사람(직원·외주)이 수행**하고 이 앱이 견적·배정·진행·결과를 관리합니다.
> 자동 게시는 각 플랫폼의 공식 API 권한을 얻은 뒤 별도 단계로 연결합니다(아래 “구현하지 않은 것” 참고).
> 데모 가격표는 샘플이며 **서비스 상품** 화면(관리자)에서 바로 수정할 수 있습니다.

## 스레드 바로 올리기 (사진·스크린샷 1장 → 내 Threads)

사이드바 **🧵 스레드 바로 올리기**에서 사진을 끌어다 놓거나, 화면 캡처 후 **Ctrl+V** 로 붙여넣고, 문구를 쓴 뒤 **스레드에 바로 게시**를 누르면 Threads 공식 API 로 내 계정에 올라갑니다.
설정 전에도 **모의 게시(테스트)** 로 흐름을 확인할 수 있습니다 (실제로는 올라가지 않음).

- JPG·PNG, 8MB 이하 (아이폰 HEIC 는 JPG 로 내보내기) · 문구 500자 (이모지는 더 많이 셈) · 24시간 250건 (Threads 제한)
- 광고·협찬 체크 시 `#광고` 자동 표시 · 게시 결과(링크·실패 사유)는 아래 기록에 남음
- 토큰은 AES-256 으로 암호화해 서버에만 저장

### 실제 게시를 켜는 3단계

**1. Meta 개발자 앱 + 토큰**
1. https://developers.facebook.com → 앱 만들기 → 사용 사례 **“Threads API 액세스”** 선택
2. 권한에 `threads_basic`, `threads_content_publish` 추가
3. 앱 역할에 본인 Threads 계정을 **Threads 테스터**로 추가하고, Threads 앱(설정 → 계정 → 웹사이트 권한 → 초대)에서 수락
4. 토큰 얻기 — 둘 중 하나
   - (간단) 앱 대시보드에서 발급한 사용자 액세스 토큰을 앱의 **스레드 바로 올리기 → 액세스 토큰 붙여넣기**에 입력
   - (권장) `.env` 에 `THREADS_APP_ID`, `THREADS_APP_SECRET`, `THREADS_REDIRECT_URI`(=`https://내공개주소/api/threads/callback`, 대시보드에도 같은 주소 등록) 설정 → **Threads 로 로그인해서 연결** 버튼 (60일 토큰, 자동 갱신)

**2. `.env` 에 암호화 키**
```
TOKEN_ENCRYPTION_KEY="아무렇게나_32자_이상_긴_문자열"
```

**3. 공개 https 주소** — Threads 서버가 이미지를 가져가야 하므로 필요합니다.
- 배포(권장): Vercel 등에 올린 주소를 `PUBLIC_BASE_URL` 에
- PC 에서 바로: Cloudflare 임시 터널
  ```powershell
  winget install --id Cloudflare.cloudflared
  cloudflared tunnel --url http://localhost:3100
  ```
  출력된 `https://xxxx.trycloudflare.com` 을 `.env` 의 `PUBLIC_BASE_URL` 에 넣고 앱 재시작 (터널을 다시 켜면 주소가 바뀜)

> 🔒 외부 주소로 열면 **데모 계정은 로그인되지 않습니다**(비밀번호가 공개돼 있으므로). 이 PC(localhost)에서 관리자로 들어가 **직원·권한**에서 본인 계정을 만든 뒤, 외부에서는 그 계정으로 로그인하세요.
> ⚠ 실제 Threads 계정·Meta 앱으로는 검증하지 못했습니다(이 개발 환경에 계정이 없음). API 호출 순서·오류 처리는 공식 문서 기준으로 구현하고 모의 서버로 테스트했습니다.

## 운영 원칙 (코드로 강제됨)

| 원칙 | 구현 |
|---|---|
| 기본값은 **모의 실행** — 외부 SNS 에 아무것도 게시하지 않음 | 모든 플랫폼 Adapter 의 실제 게시 호출은 미구현 → `NOT_CONFIGURED`/`LIVE_NOT_IMPLEMENTED` 반환, 실제 게시 버튼은 ‘게시 가능’ 플랫폼에서만 노출 |
| 광고임을 숨기지 않음 | 모든 문구에 광고 표시 문구 첨부, 실행 전 사전검사에서 광고 표시 없으면 **차단** |
| 사람 승인 없이 실행 불가 | `APPROVED` 문구만 실행 대기열 등록 가능, 본인이 생성한 문구는 본인이 승인 불가(직무 분리) |
| 허위 체험담·가짜 반응 금지 | 생성 프롬프트/템플릿에서 금지 + 안전 필터(`inspectDraft`)와 사전검사에서 의심 표현 차단 |
| 스팸·우회 금지 | 중복 게시 검사(문구 해시), 플랫폼별 일일 실행 한도, 비공식 자동화·계정 조작 기능 없음 |
| 실적 출처 구분 | `모의 실적 / 데모 데이터 / 실측(검증됨) / 미측정` 을 DB·화면·CSV·보고서에서 분리 표시 |
| URL 임의 크롤링 금지 | URL 은 형식·프로토콜·내부망 여부만 검사, “외부 콘텐츠 자동 분석: 하지 않음” 표시 |

## 빠른 시작 (로컬)

필요: **Node.js 22**, **PostgreSQL 16** (14 이상이면 동작 예상)

```bash
cd viralsync-ai
npm install
cp .env.example .env            # DATABASE_URL, SESSION_SECRET 수정
npm run db:setup                # 스키마 생성(prisma db push) + 데모 데이터
npm run build && npm run start  # http://localhost:3100
# 개발 모드: npm run dev
```

로그인 화면의 **데모 계정으로 체험** 버튼을 누르면 바로 로그인됩니다 (`DEMO_MODE=true`).

| 계정 (비밀번호 `demo1234!`) | 역할 | 접근 가능한 고객 |
|---|---|---|
| admin@demo.viralsync.example | 관리자 | 전체 |
| manager@demo.viralsync.example | 캠페인 매니저 | 고객 1~3 |
| manager2@demo.viralsync.example | 캠페인 매니저 | 고객 4~5 |
| writer@demo.viralsync.example | 콘텐츠 작성자 | 고객 1~4 |
| reviewer@demo.viralsync.example | 검토자 | 전체 5개 |
| viewer@demo.viralsync.example | 읽기 전용 | 고객 1 |
| other-admin@demo.viralsync.example | 다른 조직 관리자 | 격리 확인용 |

데모 데이터: 서비스 상품 11개(샘플 가격), 광고 문의 3건(블로그 키워드 문의·음식점 종합광고 문의·계약 전환된 카페 문의), 고객 5, 광고 의뢰 10, 가상 SNS 게시물 24, AI 문구 32, 플랫폼별 모의 실행 15건(성공·실패 포함), 실적 샘플, 정책 검토 6건, 격리 확인용 타 조직 1개.
모든 데모 데이터에는 `[데모]` 표시가 있고 URL 은 예약 도메인(`*.example`)을 사용합니다.

데모 데이터만 다시 만들기: `npm run db:reset` (`isDemo=true` 조직만 삭제 후 재생성 — 실제 조직 데이터는 건드리지 않음)

### 직접 테스트해 볼 흐름

0. 매니저로 로그인 → **문의 접수함**에서 데모 문의 확인 또는 실제 받은 문의 붙여넣기 → 견적·답변 → 계약 전환
1. 매니저로 로그인 → **고객관리 → + 고객 등록**
2. 고객 상세 → **+ 광고 의뢰 접수** → 저장 후 **AI 분석 실행** (분류·6개 점수·근거 확인)
3. **홍보 기회 탐색** → ‘평가 기준 캠페인’ 선택 → 점수 확인 → **캠페인에 연결**
4. **AI 문구 생성** → 캠페인 선택 → 생성 → 캠페인 상세에서 **검토 요청**
5. 관리자로 **직원·권한**에서 검토자에게 새 고객 접근 권한 부여 → 검토자로 **승인 관리**에서 승인/반려
6. 매니저로 **실행 관리** → 미리보기·사전검사 확인 → 실행 대기 등록 → **모의 실행**(실패 시 재시도)
7. **대시보드 / 실적·보고서** 에서 플랫폼별 게시 횟수·클릭·전환 확인, **CSV**·**월간 보고서** 출력

## Docker

```bash
docker compose up -d db
docker compose --profile setup run --rm setup   # 스키마 + 데모 데이터
docker compose up -d app                         # http://localhost:3100
```

> ⚠ 이 작업 환경에는 Docker 데몬이 없어 `docker compose` 를 **실행 검증하지 못했습니다.**
> 이미지가 사용하는 Next.js standalone 빌드(`NEXT_OUTPUT=standalone`)는 로컬에서 빌드·실행 확인했습니다.

## 환경변수 (`.env.example`)

| 변수 | 설명 |
|---|---|
| `DATABASE_URL` | PostgreSQL 연결 문자열 (필수) |
| `SESSION_SECRET` | 세션 쿠키 서명 키, 32자 이상 (필수) |
| `DEMO_MODE` | `true` 면 데모 계정 원클릭 로그인 표시 |
| `AI_PROVIDER` | `demo`(기본, 비용 0) 또는 `anthropic` |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | `AI_PROVIDER=anthropic` 일 때 사용 (기본 모델 `claude-opus-5-5`) |
| `USD_KRW_RATE` | AI 비용 원화 환산 환율 (추정치) |
| `INSTAGRAM_*`, `TIKTOK_*`, `X_*`, `FACEBOOK_*`, `YOUTUBE_*`, `BLOG_API_KEY` | SNS 공식 API 자격증명. 설정 시 연동 상태가 ‘API 연동 준비’로 바뀜 |
| `INSECURE_COOKIE` | `true` 면 production 에서도 HTTP 쿠키 허용 (로컬 Docker 용) |

API 키는 서버에서만 읽으며 브라우저 번들·로그·감사로그에 남기지 않습니다. 화면에는 누락된 **변수 이름**만(관리자에게만) 표시합니다.

## 테스트

```bash
npm run typecheck
npm run lint
npm test                 # Vitest 단위 + 통합 (통합은 별도 DB viralsync_test 를 자동 생성·동기화)
npm run build && npm run test:e2e   # Playwright E2E (별도 DB viralsync_e2e 에 데모 데이터 생성, 포트 3200)
```

E2E 에서 Chromium 경로가 필요하면 `PW_CHROMIUM_PATH=/path/to/chrome` 을 지정하세요.
테스트 DB 주소는 `TEST_DATABASE_URL`, `E2E_DATABASE_URL` 로 바꿀 수 있습니다.

### 마지막 실행 결과 (이 환경)
- 타입체크·ESLint: 오류 0
- Vitest: **12개 파일, 70개 테스트 통과** (단위 41 + 통합 29: 전체 업무 흐름, 문의→견적→전환→집행, 스레드 게시(모의 Threads 서버), 테넌트·고객 격리, 권한, CSV, AI 오류 처리)
- Playwright E2E: **15개 시나리오 통과** (문의→견적→계약 전환→작업 완료, 스크린샷 붙여넣기→스레드 모의 게시 포함), 연속 실행으로 안정성 확인

## 구조

```
viralsync-ai/
├─ prisma/schema.prisma        # 21개 모델 (요구 16개 + ClientAccess, ContentRevision, ServicePackage, Inquiry, FulfillmentTask)
├─ prisma/seed.ts              # 데모 데이터
├─ src/app/(app)/*             # 인증 필요 화면 (대시보드·고객·캠페인·탐색·문구·승인·실행·SNS·보고서·정책·직원·감사로그·검색)
├─ src/app/login               # 로그인 (데모 원클릭 + 이메일/비밀번호)
├─ src/app/api/export/*        # CSV 내보내기
├─ src/app/actions/*           # Server Actions (Zod 검증 → 서비스 호출)
├─ src/lib/services/*          # 도메인 로직: 모든 쿼리를 조직·고객 범위로 제한
├─ src/lib/auth/*              # JWT 세션 쿠키, RBAC 권한표, 테넌트 범위
├─ src/lib/analysis/*          # 규칙 기반 분류(14개 대분류·소분류)·점수 엔진
├─ src/lib/inquiry/*           # 문의 분석기·매체 추천/견적 플래너·답변 초안
├─ src/lib/ai/*                # AIProvider 인터페이스: DemoProvider / AnthropicProvider, 안전 필터
├─ src/lib/adapters/*          # 플랫폼별 Adapter (Instagram/TikTok/X/Facebook/YouTube/블로그)
├─ src/config/brand.ts         # 서비스명 변경
├─ src/app/globals.css         # 브랜드 컬러(--brand-*) 변경
└─ tests/{unit,integration,e2e}
```

자세한 설계는 [`docs/PLAN.md`](docs/PLAN.md).

### 인증
요구사항의 “Supabase 인증 또는 동등한 구조” 중 **동등한 구조**를 택했습니다: bcrypt 비밀번호 + HS256 서명 httpOnly 세션 쿠키(jose), 요청마다 DB 에서 사용자·역할·활성 여부를 다시 읽습니다.
Supabase Auth 로 바꾸려면 `src/lib/auth/current.ts` 의 `getCtx()` 에서 Supabase 세션 → `User` 매핑만 교체하면 됩니다(서비스 계층은 `Ctx` 만 사용).

### 권한 (요약)
- 관리자: 전체 / 매니저: 고객·캠페인·실행·비용 / 작성자: 분석·후보·문구 / 검토자: 승인·정책 / 읽기 전용: 조회만
- 비용 데이터·고객 연락처·SNS 인증정보는 권한이 없으면 서버에서 제거(마스킹)한 뒤 전달
- 관리자 외 역할은 `ClientAccess` 로 배정된 고객 데이터만 조회 — 다른 조직 데이터는 어떤 역할도 조회 불가

## 구현하지 않은 것 / 외부 연동에 필요한 것

**미구현 (정직하게 표시됨)**
- SNS **실제 게시·댓글 작성 호출**: 모든 Adapter 에서 미구현. 화면에 ‘실제 게시 연동 미구현’으로 표시되고 버튼이 나오지 않습니다.
- SNS **OAuth 계정 연결 화면**: 연결 계정은 데모 레코드만 있습니다.
- **실측 실적 수집**(클릭·방문·전환 트래킹, 플랫폼 인사이트 API): 없음. 모든 수치는 모의/데모로 표시됩니다.
- **게시물 자동 수집/탐색**: 없음. 후보는 직접 입력 또는 데모 데이터입니다.
- **월간 정책 자동 확인**: 스케줄러·수집기가 없어 비활성으로 표시됩니다.
- AI 분석은 규칙 기반 엔진이며, LLM 은 문구 생성에만 연결되어 있습니다. Anthropic Provider 는 코드·타입체크까지 완료했으나 **API 키가 없어 실제 호출은 검증하지 못했습니다.**
- 비밀번호 재설정·초대 메일, 파일 업로드, 다국어는 없습니다.
- 문의 분석은 규칙 기반입니다. 크몽 메시지를 자동으로 가져오는 연동은 없고(크몽 공개 API 없음), 원문을 붙여넣어야 합니다. 키워드 검색량·경쟁도 조회(네이버 검색광고 API 등)도 미연동입니다.
- 견적서 PDF·전자계약·결제 연동은 없습니다(결제는 크몽 안전결제 사용 전제).

**실제 연동 시 필요한 항목**
1. 각 플랫폼 개발자 앱 등록·앱 검수(권한 승인): Instagram/Facebook(Meta Graph API, 브랜디드 콘텐츠), TikTok Content Posting API, X API 유료 요금제, YouTube Data API(OAuth·쿼터), 블로그는 서비스별 공식 API 여부 확인
2. OAuth 토큰 **암호화 저장소**(KMS 등) — 현재 스키마에는 토큰 원문 컬럼을 의도적으로 두지 않았습니다
3. `src/lib/adapters/platforms.ts` 의 각 Adapter 에 `publishLive` 구현 + `livePublishImplemented = true`
4. 전환 추적(UTM·픽셀·서버 이벤트) 후 `PerformanceMetric.source = VERIFIED` 로 적재
5. 정책 검토 자동화가 필요하면 스케줄러(cron)와 공식 문서 변경 감지 수집기
6. 운영 배포: 마이그레이션 파일(`prisma migrate`) 전환, HTTPS, `SESSION_SECRET` 교체, `DEMO_MODE=false`

## 알려진 사항
- 시드의 정책 URL 은 대표 공식 페이지 주소이며 담당자가 실제로 확인한 기록이 아닙니다(‘[데모] 샘플’로 표시).
- `(app)` 라우트 그룹에는 `loading.tsx` 를 두지 않았습니다. Next 15.5 에서 그룹 단위 loading 경계가 있으면 캠페인 상세로의 클라이언트 이동이 약 50% 확률로 멈추는 현상을 재현했고, 제거 후 24/24 정상 이동을 확인했습니다. 대신 사이드바 이동 표시(`useLinkStatus`)와 버튼 진행 표시를 사용합니다.
- Prisma 는 AI 에이전트 실행 시 `db push --force-reset` 을 차단하므로, 데모 초기화는 데모 조직만 지우는 `SEED_RESET=true` 방식으로 구현했습니다.
