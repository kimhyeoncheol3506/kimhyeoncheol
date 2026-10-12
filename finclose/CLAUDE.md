# FinClose AI — 개발 지침 (CLAUDE.md)

증권사 회계결산 자동화 플랫폼(로컬 MVP). 상위 저장소의 다른 프로젝트(Next.js 사주 사이트)와 무관하며 `finclose/` 안에서만 작업한다.

## 구조
- `backend/finclose/` Python(FastAPI). 진입점 `python -m finclose`. 모듈 책임은 `docs/ARCHITECTURE.md`.
- `backend/finclose/templates/*.json` 기본 업무 템플릿(최초 실행 시 DB에 v1으로 등록).
- `frontend/` React+TS+Vite PWA. `npm run build` → `frontend/dist`(FastAPI가 서빙, 사용자 편의를 위해 커밋함).
- `sample_data/` 가상 데이터(`python -m finclose.sample_data`로 재생성).

## 명령
- 테스트: `cd backend && .venv/bin/python -m pytest` / `cd frontend && npm test`
- 타입체크·빌드: `cd frontend && npx tsc -b && npm run build`
- 실행: `./run.sh` (또는 `run.sh demo`로 과거 이력 생성)

## 반드시 지킬 원칙
1. 금액은 `Decimal`(서버), 문자열(API·프런트). float 금지. 반올림은 최종 1회.
2. 계산·검증은 결정론적 코드. 외부 AI·외부 네트워크 호출을 추가하지 않는다(사용자 명시 승인 없이는).
3. 규칙 승인상태(APPROVED)를 코드가 자동으로 올리지 않는다. 담당자 역할은 승인 불가.
4. NOT_RUN을 PASS로 취급하지 않는다. 새 검증은 `CheckBook.add/result`로 상태·심각도·사유를 남긴다.
5. 원장 반영(POSTED) 기능을 만들지 않는다. 업로드 파일 생성까지만.
6. 원본 파일·과거 실행·승인 기록·감사 로그를 수정·삭제하는 코드를 만들지 않는다(새 버전/새 레코드로).
7. 새 업무는 템플릿 JSON + (필요 시) `engine.py` 파이프라인 + 정상/실패 테스트를 함께 추가한다.
8. 테스트가 실패하거나 실행하지 않았으면 완료로 보고하지 않는다. 미구현은 문서에 ⛔/🟡로 표시한다.
