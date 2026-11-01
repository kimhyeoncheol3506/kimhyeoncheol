---
name: verify
description: 타입체크·린트·단위/통합 테스트·빌드·직원 지시서 일치를 돌리고, 실패하면 고쳐서 모두 통과시킨다. 코드를 고친 뒤, 커밋 전, /ship 전에 사용.
---
# /verify — 빌드 루프

1. Postgres 확인: `pg_isready || service postgresql start`
2. 순서대로 실행하고 **처음 실패한 단계에서 멈춰 고친 뒤 처음부터 다시**:
   - `npx prisma generate` (스키마를 바꿨다면 `npx prisma db push --skip-generate`)
   - `npx tsc --noEmit`
   - `npm run lint`
   - `npx tsx scripts/export-staff.ts --check` (실패하면 `npm run staff:export`)
   - `npx vitest run`
   - `npm run build`
3. 같은 실패를 3번 고쳐도 안 되면 멈추고 `/investigate` 로 원인부터 찾는다.
4. 테스트를 지우거나 `skip`·약하게 바꿔서 통과시키지 않는다. 기대값을 바꿨다면 왜 바뀌었는지 보고.
5. 끝나면 한 줄 보고: `tsc ✓ · lint ✓ · staff ✓ · vitest N/N ✓ · build ✓` 와 고친 것 목록.
