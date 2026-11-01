---
name: qa
description: 실제 브라우저로 앱을 시험한다 — Playwright E2E 전체(Node), 필요하면 Cloudflare workerd 런타임 E2E, 바뀐 화면 캡처 확인. 화면·흐름을 바꾼 뒤나 /ship 전에 사용.
---
# /qa — QA 리드

1. `npm run build` 후 `PW_CHROMIUM_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome npx playwright test` (로컬 경로가 다르면 PW_CHROMIUM_PATH 생략).
   - E2E 는 `viralsync_e2e` DB 를 매번 데모 데이터로 새로 만든다.
2. DB·저장소·서버 액션·미들웨어를 바꿨다면 Cloudflare 런타임도: `npm run test:e2e:cf`.
3. 실패하면: 오류의 `error-context.md` 페이지 스냅샷을 읽고 원인이 **앱**인지 **테스트 선택자**인지 먼저 가린다.
   - 앱 버그 → 고치고, 그 버그를 잡는 회귀 검사를 테스트에 추가.
   - 선택자 문제 → 역할·레이블 기반 선택자로 고친다 (`getByRole`, `getByLabel`). 기대 동작을 약하게 만들지 않는다.
4. 바뀐 화면은 Playwright 스크립트로 스크린샷을 찍어 직접 보고(데스크톱 1400px, 모바일 420px) 깨진 배치·잘린 글자·빈 상태를 확인한다.
5. 새 기능에는 E2E 시나리오를 최소 1개 추가: 정상 흐름 + 막혀야 하는 경우 1개.
6. 보고: `E2E N/N (Node) · N/N (workerd)` + 확인한 화면 목록 + 고친 것.
