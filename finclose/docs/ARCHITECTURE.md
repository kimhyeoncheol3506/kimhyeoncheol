# 아키텍처 (ARCHITECTURE)

## 1. 기술 선택과 근거
| 영역 | 선택 | 근거 / 기각한 대안 |
|---|---|---|
| 백엔드 | Python 3.11+ / FastAPI / uvicorn | 데이터 처리 생태계, 타입 검증(pydantic) |
| 표 처리 | 표준 csv·openpyxl 직접 판독, **Decimal**(금액 계산) | pandas는 기능상 불필요해 제외(데스크톱 앱 용량 축소, float 금액 연산 위험 제거) |
| Excel | openpyxl (MIT) | 수식/캐시값을 별도 로드해 구분 가능 |
| PDF | **pdfplumber (MIT)** | PyMuPDF는 AGPL-3.0 → 사내 배포 시 라이선스 검토 필요해 기본 채택 안 함 |
| DB | SQLite (표준 라이브러리) | 로컬 단일 사용자 MVP에 충분. DuckDB/PostgreSQL은 대용량·다중 사용자 단계에서 도입 |
| 검증 | 자체 검증 엔진 | Great Expectations/Soda는 회계 특화 상태(NOT_RUN, 예외승인, 차단정책) 표현이 어려워 MVP에서 미도입 |
| 프런트엔드 | React 18 + TypeScript + Vite | 정적 빌드 후 FastAPI가 서빙 → 단일 프로세스 실행 |
| 앱 버전 | PWA(manifest + service worker) | 별도 스토어 배포 없이 PC/모바일 설치. 서비스워커는 **앱 껍데기만 캐시, API 데이터는 캐시하지 않음** |
| 테스트 | pytest, vitest | |

## 2. 처리 흐름
```
업로드 → 원본보관(읽기전용, SHA-256) → 판독(Parser) → 프로파일 → 업무식별(Discovery)
 → 매핑/형식변경 확인(Schema Mapper) → 처리계획(Plan) → [사용자 확인] → 실행(Engine)
 → 독립검증(Validation) → 증감분석(Variance) → 보고서/Excel(Report) → 검토/승인(Approval)
 → 확정 시 업로드 파일 생성(Export) → 전 단계 감사기록(Audit)
```
각 실행은 `data/runs/<run_id>.tmp/`에서 생성 후 원자적 rename. 중간 실패 시 원본·기존 결과는 영향 없음.

## 3. 모듈 (backend/finclose)
| 모듈 | 파일 | 책임 | 입력 → 출력 |
|---|---|---|---|
| File Intake | intake.py | 크기/형식/매직바이트/디스크 확인, 안전 저장, 해시 | UploadFile → FileRecord |
| Document Parser | parsers/excel.py, csv_parser.py, pdf.py | 시트·헤더·수식·병합·숨김·단위·기준일 탐지 | 파일경로 → ParsedFile(tables, metadata) |
| Data Profiler | profiler.py | 결측·중복·고유값·통계·혼합형·공백 | Table → Profile |
| Schema Mapper | schema_mapper.py | 동의어/유사도 매핑, drift 탐지 | Table + 컬럼명세 → Mapping, Drift |
| Workflow Discovery | discovery.py | 템플릿 유사도 점수, 신규 업무 초안 | 파일들 → 후보/초안 |
| Workflow Builder / Template Registry | templates.py, templates/*.json | 템플릿 버전·상태·규칙 테스트 | JSON ↔ DB |
| Transformation Engine | engine.py, normalize.py | 정규화, 결합, 계산 실행 | 매핑된 테이블 → 가공행 |
| Accounting Rule Engine | rules.py, journal.py | 안전 수식 해석(Decimal), 반올림, 분개 초안 | 규칙 + 행 → 값/분개 |
| Reconciliation / Validation | validation.py | 7개 범주 검증, 상태/심각도 | 실행 컨텍스트 → CheckResult[] |
| Variance / Anomaly | variance.py | 기간 비교, 이상 증감 | 당기/비교 행 → VarianceRow[] |
| Report / Export | report.py | Excel 9시트, HTML 보고서, 업로드 파일 | 실행 결과 → 파일 |
| Approval Workflow | approval.py | 차단 게이트, 검토·승인·예외·확정 | 실행 + 행위자 → 상태 |
| Audit Trail | audit.py | 해시 체인 감사 로그 | 이벤트 → audit_log |
| Security Layer | security.py | 역할·권한, 파일명 정화 | 요청 → 허용/거부 |

## 4. 저장 구조
```
finclose/data/            (FINCLOSE_DATA_DIR 로 변경 가능, git 제외)
  finclose.db             SQLite: files, templates, runs, approvals, audit_log, settings
  uploads/<file_id>.<ext> 원본(읽기전용 권한)
  runs/<run_id>/          processed.json, result.xlsx, report.html, upload_*.csv(확정 후)
```
## 5. 실행 상태 머신
`RUNNING → (FAILED | BLOCKED | READY_FOR_REVIEW) → REVIEWED → APPROVED → FINALIZED`, 언제든 `REJECTED`.
`BLOCKED`(차단 사유 존재)도 검토/예외승인으로 해소 후 승인 가능, 단 CRITICAL은 예외승인 불가.
