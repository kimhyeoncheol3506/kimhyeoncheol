# 데이터 검증 및 대사 규칙 (DATA_VALIDATION)

## 1. 상태와 심각도
상태: `PASS`, `WARNING`, `FAIL`, `REVIEW_REQUIRED`, `NOT_APPLICABLE`(사유 필수), `NOT_RUN`(사유 필수, PASS 아님)
심각도: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` — 검증 규칙별로 정의(템플릿 `validation_overrides`로 조정 가능).

## 2. 차단 정책 (approval.gate)
확정(업로드 파일 생성)은 다음 중 하나라도 있으면 차단된다.
1. `FAIL` + `CRITICAL` (예외승인 불가)
2. `FAIL` + `HIGH` 중 예외승인되지 않은 것
3. 필수(`mandatory`) 검증의 `NOT_RUN`
4. 확인(acknowledge)되지 않은 `REVIEW_REQUIRED`
5. 실행 상태가 `APPROVED`가 아님
6. 같은 템플릿·같은 기준일로 이미 확정된 다른 실행 존재(중복 반영 위험)

`WARNING`/`MEDIUM FAIL`은 차단하지 않지만 Excel·보고서에 표시되고 검토 기록에 남는다.
예외승인·확인 기록은 원래 검증 결과와 함께 영구 보존된다(삭제 API 없음).

## 3. 검증 카탈로그 (채권 템플릿 기준)
| ID | 범주 | 내용 | 기본 심각도 |
|---|---|---|---|
| F01 | 파일 | 필수 입력 파일 존재 | CRITICAL |
| F02 | 파일 | 같은 파일(해시) 중복 투입 | HIGH |
| F03 | 파일 | 필수 컬럼 매핑 완료 | CRITICAL |
| F04 | 파일 | 빈 파일/데이터 행 없음 | CRITICAL |
| F05 | 파일 | 기준일 일관성(입력 간·요청 기준일) | HIGH |
| F06 | 파일 | 금액 단위 표기 vs 명세 | HIGH |
| F07 | 파일 | 형식 변경(drift) / 유사도 매핑 확인 | REVIEW_REQUIRED |
| F08 | 파일 | Excel 수식 캐시값 누락 / PDF 추출값 | REVIEW_REQUIRED |
| D01 | 데이터 | 필수값 누락 | HIGH |
| D02 | 데이터 | 키 중복(종목코드+통화) | CRITICAL |
| D03 | 데이터 | 날짜 형식 오류 | HIGH |
| D04 | 데이터 | 통화코드 유효성 | HIGH |
| D05 | 데이터 | 종목코드 형식 | MEDIUM |
| D06 | 데이터 | 숫자 필드에 문자 | HIGH |
| D07 | 데이터 | 음수 수량/단가 | HIGH |
| D08 | 데이터 | 단가 정상범위 이탈 | MEDIUM(WARNING) |
| D09 | 데이터 | 전월 대비 건수 급변 | WARNING |
| D10 | 데이터 | 결합 후 행 수 증가(중복 결합) | CRITICAL |
| R01 | 대사 | 보유종목 중 단가 미매칭 | HIGH |
| R02 | 대사 | 단가파일에만 있는 종목 | LOW(WARNING) |
| R03 | 대사 | 보유내역 '전월평가금액' vs 전월결과파일 | MEDIUM |
| R04 | 대사 | 전월 대비 신규/소멸 종목 | WARNING(정보) |
| T01 | 합계 | 원천 건수 = 처리 건수 + 예외 건수 | CRITICAL |
| T02 | 합계 | 원천 장부금액 합계 = 가공 장부금액 합계(통화별) | CRITICAL |
| T03 | 합계 | 행 합계 vs 독립 집계 평가금액(통화별) | CRITICAL |
| T04 | 합계 | 결과(업로드 대상) 합계 = 가공 합계 | CRITICAL |
| C01 | 계산 | Fraction 기반 독립 재계산 일치 | CRITICAL |
| C02 | 계산 | 역산(평가금액→단가) 허용오차 내 | HIGH |
| C03 | 계산 | 평가/장부 비율 이상(단위 오류 탐지) | HIGH(WARNING) |
| C04 | 계산 | 반올림 영향 ≤ 건수×0.5 최소단위 | MEDIUM |
| C05 | 계산 | 규칙 테스트케이스 통과 / 규칙 승인상태 | CRITICAL / REVIEW_REQUIRED |
| A01 | 회계 | 분개 초안 차변=대변(전표별·전체) | CRITICAL |
| A02 | 회계 | 분개 합계 = 평가손익 합계 | HIGH |
| V01 | 기간 | 전월·전분기·전년동기·전기말 비교 수행 | NOT_RUN 가능(비교 이력 없음) |
| V02 | 기간 | 이상 증감(중요성 기준 초과) | WARNING |
| V03 | 기간 | 수량 변동 없이 금액 급변/금액 유사·수량 급변 | WARNING |

## 4. 증감률 표기
| 상황 | 표기 |
|---|---|
| 비교금액 0, 당기 0 | `NO_CHANGE` |
| 비교금액 0, 당기 ≠ 0 | `N/A_ZERO_BASE` |
| 부호 전환 | `SIGN_CHANGE` (비율 미표시) |
| 비교 기간에 없음 | `NEW` |
| 당기에 없음 | `REMOVED` |
| 그 외 | (당기−비교)/|비교| |

## 5. 독립 검증의 원칙
같은 산식을 같은 코드로 반복하는 것은 독립 검증이 아니다. C01은 `fractions.Fraction`과 별도 구현
반올림 함수를 사용하는 **다른 코드 경로**로 재계산하고, T03은 행 합계가 아닌 통화별 집계 후 계산과 비교하며,
C02는 결과에서 입력을 역산한다.
