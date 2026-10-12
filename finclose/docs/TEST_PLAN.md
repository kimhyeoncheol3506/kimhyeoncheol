# 테스트 계획 (TEST_PLAN)

실행: `cd finclose/backend && python -m pytest -q` / 프런트: `cd finclose/frontend && npm test`

## 단위 테스트 (backend/tests)
| 파일 | 대상 |
|---|---|
| test_rules.py | 안전 수식 해석기, Decimal 반올림, 0 나누기, 금지 구문, 규칙 테스트케이스 |
| test_normalize.py | 금액/날짜/통화/코드 정규화, 괄호 음수, 천단위 구분자 |
| test_parsers.py | Excel 메타(수식·캐시·숨김·병합·단위), CSV(cp949), PDF 텍스트/표, 손상·암호 파일 |
| test_profiler.py | 결측·중복·혼합형 |
| test_schema_mapper.py | 동의어/유사 매핑, drift(컬럼명 변경·추가·삭제) |
| test_variance.py | 0 분모, 부호전환, 신규/소멸, 임계값 |
| test_journal.py | 차변·대변 불일치 탐지 |
| test_audit.py | 해시 체인 변조 탐지 |

## 통합 테스트 (test_workflow_*.py, test_api.py)
정상 시나리오 전체 흐름 + 실패 시나리오:
필수 파일 누락, 빈 파일, 손상 Excel, 컬럼명 변경, 잘못된 기준일, 중복 종목, 미매칭 종목, 단가 누락,
금액 단위 오류, 음수 금액, 0으로 나누기, 반올림 차이, 중복 실행, 처리 중 비정상 종료(RUNNING 복구),
저장 공간 부족(모의), PDF 표 추출 실패, 잘못된 회계 규칙, 차변·대변 불일치, 검증 실패 상태에서 확정 시도,
직무분리 위반, 재현성(동일 입력·규칙 → 동일 결과 해시), 오류 후 원본 해시 불변.

## 통과 기준
모든 테스트 통과. 실패/미실행 테스트가 있으면 성공으로 보고하지 않는다.
