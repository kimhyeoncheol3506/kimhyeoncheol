# ViralSync AI — 개발 규칙

광고홍보 회사 운영 앱 (Next.js 15 App Router · TypeScript · Prisma/PostgreSQL · Tailwind). 사용자 호칭은 **캡틴**, 쉬운 한국어 존댓말.
운영 쪽 Claude Code 회사 폴더는 `광고홍보AI_회사/` (그 안의 CLAUDE.md 를 따름).

## 일하는 순서 (gstack 의 Think → Plan → Build → Review → Test → Ship → Reflect)
| 단계 | 스킬 | 하는 일 |
|---|---|---|
| 만들기 | `/verify` | 타입·린트·단위/통합 테스트·빌드·직원 지시서 일치까지 통과할 때까지 고침 |
| 막혔을 때 | `/investigate` | 원인부터. 고치기 3번 실패하면 멈추고 보고 |
| 검토 | `/review` | 이 앱의 불변 규칙(아래)을 깨는지 diff 검사 |
| 보안 | `/cso` | 권한·테넌트·토큰·비밀값·공개 경로 점검 |
| 시험 | `/qa` | 실제 브라우저 E2E (Node + 필요 시 Cloudflare workerd) + 화면 캡처 |
| 출고 | `/ship` | verify → qa → 문서 → 커밋·푸시 (PR 은 캡틴이 요청할 때만) |
| 문서 | `/document-release` | README·배포 안내·매뉴얼이 바뀐 동작과 맞는지 |
| 회고 | `/retro` | 주간 커밋·테스트 수·남은 일 정리 |
| 안전 | `/freeze` `/unfreeze` | 한 폴더 밖 수정 금지 / 해제 |

안전 훅(`.claude/hooks/guard.mjs`)이 항상 막는 것: `rm -rf /·~·.`, 강제 푸시, `git reset --hard`, `git clean -f`, `prisma --force-reset`·`migrate reset`, 개발 DB 의 `--accept-data-loss`, DROP/TRUNCATE, Cloudflare 배포·삭제.

## 불변 규칙 (깨면 /review 가 막는다)
1. **테넌트·고객 범위**: 조회는 `clientWhere`/`campaignWhere` 등 범위 헬퍼를 쓰고, 범위는 `AND` 안에 둬서 호출부 `id` 가 덮어쓰지 못하게.
2. **권한**: 서비스 함수 첫 줄에서 `assertCan(ctx, "...")`. 화면은 `can()` 으로 숨기기만 할 뿐 보안이 아님.
3. **사람 승인**: 외부로 나가는 것(게시·견적·계약)은 결재(ApprovalRequest)를 거친다. 홍보 문구 승인은 검수 7개(`QC_KEYS`) 필수. 가게 본인 계정 게시는 사장님 승인(`clientStatus`) 필수.
4. **광고 원칙**: 제3자 홍보는 광고 표시 필수, 본인 계정은 생략 가능. 손님·후기인 척(`FAKE_EXPERIENCE_PATTERNS`)과 효과 보장은 언제나 차단. 비공식 자동화·DM/카톡 자동 발송 금지.
5. **수치 정직**: 모의·데모 실적은 출처(`MetricSource`)로 구분, 실측처럼 표시하지 않는다.
6. **비밀값**: 키·토큰은 서버에서만, 저장 시 암호화(`TOKEN_ENCRYPTION_KEY`), 로그·화면 노출 금지. 데모 로그인은 localhost 전용.
7. **Cloudflare 호환**: DB 는 `@/lib/db` 의 `prisma` 만 사용(요청별 클라이언트), 파일은 `src/lib/threads/storage.ts` 경유(R2/디스크). `node:fs` 직접 사용 금지.
8. **단일 원본**: 직원 명부 `src/lib/company/staff.ts`, 사업 규칙 `src/lib/business/playbook.ts`. 고치면 `npm run staff:export` (테스트가 불일치를 잡음).

## 명령
- 개발 서버 `npm run dev` · DB `npm run db:push` · 데모 데이터 `npm run db:reset` · 실제 관리자 `npm run admin:create`
- 검사 `npx tsc --noEmit` · `npm run lint` · `npx vitest run` · `npm run build`
- E2E `npm run test:e2e` (빌드 후) · Cloudflare 런타임 E2E `npm run test:e2e:cf`
- 테스트 DB 는 `viralsync_test` / `viralsync_e2e` (로컬 Postgres). 꺼져 있으면 `service postgresql start`.

## 커밋
- 한국어 제목 한 줄 + 무엇·왜 목록. 모델 이름은 넣지 않는다.
- 기능 추가 시 README 의 해당 절과 ‘마지막 실행 결과’(테스트 수)를 함께 갱신.
