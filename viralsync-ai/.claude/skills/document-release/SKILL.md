---
name: document-release
description: 바뀐 동작에 맞게 README·docs·회사 폴더 매뉴얼·직원 지시서를 점검하고 고친다. /ship 때마다, 또는 기능을 바꾼 뒤 사용.
---
# /document-release — 기술 문서 담당

1. 이번 변경(`git diff` 또는 마지막 출고 이후)에서 **사용자가 보는 동작**이 바뀐 것을 목록으로.
2. 각 항목을 문서와 대조:
   - `README.md` — 기능 절, 운영 원칙, 명령, ‘마지막 실행 결과’(실제로 방금 돌린 테스트 수만)
   - `docs/DEPLOY_CLOUDFLARE.md` — 환경변수·바인딩·단계
   - `.env.example` — 새 환경변수
   - `src/lib/company/staff.ts`·`manuals.ts`·`playbook.ts` 를 바꿨으면 `npm run staff:export`
   - `광고홍보AI_회사/CLAUDE.md` — 회사 폴더 규칙에 영향이 있으면
3. 문서에 **구현하지 않은 기능을 했다고 쓰지 않는다.** 검증 못 한 것은 ‘미검증’으로.
4. 결과: 고친 문서 목록, 남은 불일치(있으면).
