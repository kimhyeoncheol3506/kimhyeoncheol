---
name: ship
description: 출고 — verify·review·qa·문서 갱신을 거쳐 커밋하고 현재 브랜치에 푸시한다. PR 은 캡틴이 요청할 때만. 기능이 끝났을 때 사용.
---
# /ship — 릴리스 엔지니어

1. `git status` 로 바뀐 것 확인. 임시 파일·스크린샷·`test-results`·`.open-next`·`.dev.vars` 가 들어가지 않게.
2. `/verify` → `/review` → `/qa` 순서. 하나라도 실패하면 멈추고 고친다.
3. `/document-release` 로 README(기능 절·‘마지막 실행 결과’ 테스트 수)·배포 안내·매뉴얼 갱신.
4. 커밋: 한국어 제목 + 무엇·왜 목록, 세션이 정한 공동 작성자 줄. 모델 이름은 넣지 않는다.
5. `git push -u origin <현재 브랜치>` (네트워크 오류만 2·4·8·16초 간격으로 재시도). 강제 푸시 금지.
6. 운영 배포(`cf:deploy`)는 하지 않는다 — 캡틴이 Cloudflare 에서 직접. 필요하면 안내만.
7. 캡틴에게 보고: 무엇이 바뀌었나(쉬운 말) · 확인 결과 숫자 · 캡틴이 할 일(예: `npm run db:push`).
