# FinClose AI — 회계결산 지능형 자동화 플랫폼 (로컬 MVP)

증권사 회계팀의 반복 결산 업무를 **업로드 → 판독 → 매핑 → 계산 → 다중 검증 → 전기 비교 → 검토·승인 → 업로드 파일 생성**까지
처리하는 로컬 웹 앱(+ 설치형 PWA 앱)입니다. 모든 처리는 PC 안에서 이루어지며 외부로 데이터를 보내지 않습니다.

> ⚠️ **운영 사용 전 확인**: 인증이 없는 MVP입니다(화면의 사용자/역할 전환은 데모용). 원장·외부 시스템에 반영하는 기능은 없습니다.
> 시연 업무의 평가금액 산식·분개 계정은 **예시(EXAMPLE)** 이며 회사 정책으로 확인되지 않았습니다.

## 1. 빠른 시작
| OS | 명령 |
|---|---|
| Windows | `run.bat` (시연 이력 포함: `run.bat demo`) |
| macOS/Linux | `./run.sh` (시연 이력 포함: `./run.sh demo`) |

필요: Python 3.11+ (Node.js 18+는 화면을 다시 빌드할 때만 필요 — 빌드된 화면이 동봉됨).
실행 후 브라우저에서 **http://127.0.0.1:8000** 접속.

### 시연 순서 (약 5분)
1. `run.sh demo` → 과거 4개 기준일(2025-09, 2025-12, 2026-06, 2026-08)이 확정된 이력이 생성됨
2. **결산 실행** → `sample_data/bond_2026-09/`의 파일 3개를 끌어다 놓기 → **업무 식별·분석** → 계획·매핑 확인 → **실행·검증**
3. 실행 상세에서 검증 결과·증감 분석(전월/전분기/전년동기/전기말/추이) 확인
4. 상단 역할을 **검토자**(이름 변경, 예: 김검토)로 바꿔 검토필요 항목 확인 처리 → 검토 완료
5. **승인자**(예: 박승인)로 바꿔 승인 → 확정 → 다운로드 탭에서 결과 Excel·업로드 파일 받기
6. 오류 탐지 시연: `sample_data/bond_2026-09_errors/` (중복·미매칭·음수·통화오류·기준일오류·단가누락·단위오류 포함) → 확정 차단 확인
7. 그 밖의 시연: `unit_error/`(천원 단위), `format_change/`(컬럼명 변경 → 자동처리 중단), `journal/`(전표 차대 검증, CP949 CSV),
   `new_workflow_etf/`(미등록 업무 → 초안 템플릿 제안), `pdf/`(PDF 단가표 추출 → 원문 대조 필요 표시)

## 2. 앱 버전(PWA)
같은 화면을 **설치형 앱**으로 쓸 수 있습니다.
- PC(크롬/엣지): 주소창 오른쪽 설치 아이콘 또는 화면 상단 **앱으로 설치** 버튼
- 모바일: 브라우저 메뉴 → 홈 화면에 추가. 휴대폰에서 쓰려면 서버를 사내망에 열고(`FINCLOSE_HOST=0.0.0.0`) **HTTPS**(사내 인증서/리버스 프록시)를 붙여야 합니다 — 브라우저는 localhost가 아닌 http 주소에서 앱 설치를 허용하지 않습니다.
- 앱은 화면 파일만 캐시하고 **결산 데이터(API 응답)는 저장하지 않습니다.**
- 모바일 화면(폭 390px)에서 하단 탭 메뉴, 가로 스크롤 없음까지 확인했습니다.

## 3. 구현 현황
✅ 구현·테스트됨: Excel/CSV 판독(수식·캐시값·숨김·병합·단위·기준일 탐지, CP949), 데이터 프로파일링, 동의어/유사도 컬럼 매핑+수동 지정,
형식 변경 탐지·자동처리 중단, 템플릿 버전·복제·활성화·규칙 테스트, Decimal 안전 수식 엔진, 37종 검증(파일·데이터·대사·합계·계산·회계·기간),
Fraction 독립 재계산·역산·비율(단위오류)·반올림 영향 검증, 분개 초안 차대 검증, 전표 업로드 검증, 범용 대사, 기간 비교(0분모·부호전환 예외표기),
이상 증감 탐지, 결과 Excel(10시트)·HTML 보고서, 검토·확인·예외승인·승인·확정(직무분리), 확정 업로드 파일 재판독 검증(T05),
중복 실행·중복 확정 방지, 비정상 종료 복구, 해시체인 감사 로그, PWA.

🟡 제한적: PDF는 텍스트 PDF만(괘선 없는 표는 텍스트정렬 추출 — 신뢰도 낮음 표시), 신규 업무 추정은 대사형(generic_recon) 초안만,
원인 분석은 규칙 기반 후보 제시.

⛔ 미구현: 인증/SSO, 스캔 PDF OCR, 구형 .xls, 업로드 대상 시스템별 어댑터(규격 미수령 — 표준 CSV/XLSX만), 처리 스케줄러,
PostgreSQL, 데이터 암호화 저장, 외부 AI 연계(의도적 미도입).

## 4. 디렉터리
```
finclose/
├─ run.sh / run.bat          실행 스크립트
├─ CLAUDE.md                 개발 지침
├─ docs/                     PRODUCT_SPEC, ARCHITECTURE, ACCOUNTING_RULES, DATA_VALIDATION, SECURITY, TEST_PLAN, ROADMAP
├─ backend/
│  ├─ finclose/              api, service, engine, validation, rules, variance, journal, report, approval, audit,
│  │  │                      intake, profiler, schema_mapper, discovery, templates, periods, security, sample_data, seed_demo
│  │  ├─ parsers/            excel, csv_parser, pdf, common
│  │  └─ templates/          bond_ext_price_recon.json, journal_upload_check.json
│  └─ tests/                 pytest 105건
├─ frontend/                 React + TypeScript + Vite (PWA), dist/ 빌드 결과 동봉
├─ sample_data/              가상 시연 데이터
└─ data/                     실행 시 생성(DB·원본·결과) — git 제외
```

## 5. 사용 기술과 선정 이유
FastAPI·pandas 생태계(판독), openpyxl(MIT, 수식/캐시 구분), **pdfplumber(MIT)** — PyMuPDF는 AGPL이라 사내 배포 시 라이선스 검토가 필요해 제외,
SQLite(표준 라이브러리, 단일 PC MVP에 충분), 자체 검증 엔진(차단정책·NOT_RUN·예외승인 표현 — Great Expectations/Soda는 MVP 범위에서 과함),
React+Vite(정적 빌드를 FastAPI가 서빙 → 프로세스 1개). 상세: `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.

## 6. 테스트
```
./run.sh test            # 또는 run.bat test
```
최근 결과: 백엔드 **105 passed**, 프런트엔드 **3 passed**, TypeScript 타입체크 통과. 실패 시나리오 목록은 `docs/TEST_PLAN.md`.

## 7. 업무 템플릿 등록·수정
- 화면 **업무 템플릿** → JSON 수정 → **검증·규칙 테스트 실행** → 변경 사유 입력 → **새 버전 저장**(DRAFT) → 승인자가 **활성화**
  (활성화 시 모든 규칙 test_cases 재실행, 실패하면 활성화 불가, 이전 버전은 SUPERSEDED로 보존).
- 미등록 자료를 올리면 시스템이 공통 키·비교 컬럼을 추정해 **초안**을 제안 → 저장 → 승인자 활성화 → 다음 결산부터 자동 인식.
- 계산 규칙 형식: `docs/ACCOUNTING_RULES.md` §2. 담당자는 규칙을 APPROVED로 올릴 수 없습니다(승인자 권한).

## 8. 검증 규칙 수정
- 심각도·필수 여부 조정: 템플릿의 `"validation_overrides": {"D08": {"severity": "HIGH", "mandatory": true}}`
- 컬럼 범위·패턴: 컬럼 명세의 `min`, `warn_range`, `pattern`
- 역산·비율 검증: 템플릿 `verification.reverse / ratio`
- 중요성 기준(이상 증감): 화면 **설정**(관리자). 기본값은 예시이므로 회사 기준으로 등록하세요.
- 새 검증 유형 추가: `engine.py` 파이프라인에서 `book.result(...)` 호출 + `docs/DATA_VALIDATION.md` 표 + 정상/실패 테스트.

## 9. 새 결산 업무 추가
1. 대사형(두 자료 비교)이면 코드 수정 없이 `generic_recon` 템플릿으로 등록(키·비교필드·허용오차).
2. 계산이 필요한 평가형이면 `valuation_recon`을 복제해 입력 명세·규칙·검증을 바꿉니다.
3. 구조가 다른 업무(예: 경과이자, ETF 설정·환매)는 `engine.py`에 파이프라인 함수를 추가하고 `WORKFLOW_TYPES`에 등록 → 가상 데이터·테스트 작성.

## 10. 보안 주의
기본 `127.0.0.1` 바인딩. 외부 전송 없음. 원본은 읽기전용·SHA-256 기록, 실행 전 해시 재확인(변조 시 거부). 업로드 형식·크기·디스크 확인.
감사 로그 해시 체인(`감사 로그 → 무결성 검증`). 상세: `docs/SECURITY.md`. **인증이 없으므로 공용 네트워크에 열지 마세요.**

## 11. 운영 환경으로 가려면
SSO/AD 인증·권한, HTTPS, PostgreSQL·백업, 데이터 암호화, 대상 시스템 업로드 규격 어댑터, 회사 회계정책으로 규칙·계정 승인, 중요성 기준 등록.

## 12. 알려진 제한·개선 과제
- Excel float로 저장된 값은 `repr` 기반 Decimal 변환(float 표현 한계는 원천 파일의 한계).
- 기간 비교는 달력 월말 기준(영업일 조정 없음). 회계연도 말은 12월 기본.
- PDF 추출값은 항상 사람 원문 대조 대상. 셀 좌표 단위 원문 하이라이트는 미구현(페이지·표 영역·행 번호까지 제공).
- 대용량(수십만 행 이상)은 미검증 — DuckDB/Polars 도입 검토(로드맵 3~4단계).
