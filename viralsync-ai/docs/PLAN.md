# ViralSync AI — PRD · 아키텍처 · 작업 계획

## 1. 제품 요약 (PRD)

광고대행사 직원이 고객의 홍보 의뢰(유튜브·블로그·쇼츠·릴스·앱·상품)를 접수하고,
AI(또는 데모 규칙 엔진)로 분류·적합도 분석 → 홍보 후보 게시물 매칭 → 홍보 문구 초안 생성 →
사람의 검토·승인 → **모의 실행**(기본값) → 실적 집계·보고까지 한 화면에서 처리하는 SaaS.

### 원칙 (구현에 반영된 가드레일)
| 원칙 | 구현 위치 |
|---|---|
| 광고 표시 필수 | `lib/services/precheck.ts` — 광고 표시 문구가 없으면 실행 차단 |
| 사람 승인 없이 실행 불가 | `Publication` 생성은 `APPROVED` 콘텐츠만 허용 |
| 기본값 모의 실행 | 모든 플랫폼 Adapter 의 `publish()` 는 자격증명이 없으면 `NOT_CONFIGURED` 반환 |
| 위장·스팸 금지 | 생성기 프롬프트/템플릿이 허위 체험담·가짜 반응 생성을 금지, 중복 게시 검사·일일 한도 검사 |
| 실적 출처 구분 | `MetricSource` = `SIMULATED` / `DEMO_SEED` / `VERIFIED` / `NOT_MEASURED` |
| URL 임의 크롤링 금지 | URL 은 형식·프로토콜·사설 IP 여부만 검사, 콘텐츠는 사용자가 직접 입력 |

### 사용자 역할
관리자 / 캠페인 매니저 / 콘텐츠 작성자 / 검토자 / 읽기 전용 — 권한표는 `src/lib/auth/permissions.ts`.

## 2. 아키텍처

```
Next.js App Router (RSC + Server Actions)
 ├─ src/app/(app)/*           인증 필요 화면 (사이드바 레이아웃)
 ├─ src/app/login             데모 로그인
 ├─ src/app/api/*             CSV 내보내기 등 Route Handler
 ├─ src/lib/auth              세션(JWT 쿠키, jose) · RBAC · 테넌트 스코프
 ├─ src/lib/services          도메인 로직 (ctx 를 받아 조직/고객 범위로 쿼리) ← 테스트 대상
 ├─ src/lib/analysis          분류·점수 엔진 (규칙 기반, 근거 문자열 반환)
 ├─ src/lib/ai                AIProvider 인터페이스 · Demo/Anthropic 구현
 ├─ src/lib/adapters          SNS 플랫폼 Adapter (Instagram/TikTok/X/Facebook/YouTube/Blog)
 └─ prisma                    스키마 · 시드
```

- **테넌트 격리**: 모든 쿼리는 `ctx.organizationId` 로 필터. 관리자 외 역할은 `ClientAccess`
  로 배정된 고객만 조회 가능(`clientScope(ctx)`).
- **비밀값**: API 키는 서버 환경변수에서만 읽고(`server-only`), 브라우저 번들·로그·감사로그에 남기지 않음.
  ConnectedAccount 에는 토큰 원문 대신 "설정됨 여부"와 마스킹 값만 저장.

## 3. 데이터 모델
User, Organization, Client, ClientAccess, BrandProfile, Campaign, CampaignBrief, SocialPlatform,
ConnectedAccount, ContentCandidate, GeneratedContent, ContentRevision, Approval, Publication,
PerformanceMetric, PolicyReview, AuditLog, CostRecord — 상세는 `prisma/schema.prisma`.

캠페인 상태: `DRAFT → ANALYZED → PENDING_REVIEW → APPROVED → READY_TO_RUN → COMPLETED | FAILED`
(+ 반려 시 `CHANGES_REQUESTED`).

## 4. 작업 단계
1. 환경 확인 ✅
2. 계획 문서 ✅ (이 파일)
3. 골격·디자인 시스템·로그인·데모 모드 ✅
4. 고객·캠페인 관리 ✅
5. AI 분석·문구 생성 ✅
6. 승인·모의 실행·실적 집계 ✅
7. 정책 센터·CSV/월간 보고서·권한 관리 ✅
8. 테스트(Vitest 단위/통합, Playwright E2E) ✅
9. README·.env.example·Docker ✅
10. 결과 보고 ✅
