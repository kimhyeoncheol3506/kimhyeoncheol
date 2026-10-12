# 회계처리 및 회계정책 통제 원칙 (ACCOUNTING_RULES)

## 1. 세 가지의 분리
1. **수학적 계산** — 코드(Decimal)로 자동 계산.
2. **승인된 회계정책 적용** — 템플릿의 규칙 중 `approval_status = APPROVED`인 것만 "정책"으로 취급.
3. **새로운 회계 판단** — 시스템은 근거·검토사항만 제시. 규칙 상태 `EXAMPLE`/`DRAFT`인 규칙이 사용되면
   해당 실행은 반드시 `REVIEW_REQUIRED` 검증 항목을 만든다.

시스템은 어떤 경우에도 규칙의 승인 상태를 스스로 올리지 않는다. 승인 상태 변경은 approver 역할이
사유를 입력해 새 템플릿 버전을 만들 때만 가능하다.

## 2. 계산 규칙 정의 형식 (템플릿 JSON `calculations[]`)
```json
{
  "rule_id": "CALC_EVAL_AMT", "name": "평가금액", "purpose": "...", "scope": "보유 채권 전 종목",
  "inputs": ["quantity", "price"], "expression": "quantity * price / price_unit",
  "params": {"price_unit": "10000"}, "target": "eval_amount",
  "unit": "KRW 원", "rounding": {"mode": "ROUND_HALF_UP", "by_currency": true},
  "exceptions": "단가 누락 시 계산하지 않고 예외 처리", "verification": "역산: eval*price_unit/quantity ≈ price",
  "basis": "예시 — 회사 평가정책 확인 필요", "approval_status": "EXAMPLE", "version": 1,
  "test_cases": [{"inputs": {"quantity": "1000000", "price": "10123.45"}, "currency": "KRW", "expected": "1012345"}]
}
```
- 수식은 `+ - * /`, 괄호, 숫자, 입력/파라미터 이름, `abs/min/max`만 허용하는 **안전 해석기**로 평가(eval 미사용).
- 0으로 나누기·입력 누락은 행 단위 예외로 기록되며 계산값은 비워진다(0으로 대체하지 않음).
- 템플릿 저장/활성화 시 모든 `test_cases`를 재실행하며, 실패하면 활성화 불가.

## 3. 금액 원칙
- 금액은 문자열 → `Decimal`로 변환. Excel이 float로 저장한 값은 `repr` 기반 변환(float 표현 한계는 문서화된 위험).
- 통화별 소수 자릿수: KRW 0, JPY 0, USD/EUR/CNY/HKD/GBP 2 (`rules.CURRENCY_DECIMALS`, 템플릿에서 재정의 가능).
- 반올림은 **최종 단계에서 1회**만 수행. 모드: ROUND_HALF_UP(기본), ROUND_DOWN(절사), ROUND_HALF_EVEN.
- 단위: 컬럼 명세의 `unit_multiplier`와 파일 상단의 "(단위: 천원)" 표기를 비교, 불일치 시 HIGH FAIL.
- 부호: 차변 +, 대변 + 로 각각 별도 컬럼에 기록, 음수 금액은 검증 대상.

## 4. 분개 초안
필드: 회계일자, 전표유형, 계정코드, 계정명, 차변, 대변, 통화, 거래처/종목, 부서, 적요, 원천행ID, 규칙ID,
생성사유, 승인상태. 상태는 `DRAFT`(생성) → 확정 시 `EXPORTED_FOR_UPLOAD`. **`POSTED`(원장 반영) 상태는
이 시스템이 만들지 않는다.** 채권 템플릿의 평가손익 분개는 **가상 계정코드 예시**이며 금융상품 분류
(FVPL/FVOCI/AC)에 따라 계정이 달라지므로 회사 정책 확인 전에는 예시로만 표시된다.

## 5. 회사별로 반드시 확인해야 할 사항(채권 시연 업무)
- 보유수량 단위(액면금액 vs 좌수), 평가단가 표시 단위(액면 10,000원당 여부)
- 평가단가의 경과이자 포함 여부(Dirty/Clean)
- 복수 평가기관 단가의 평균/선택 규칙
- 금융상품 분류와 평가손익 계정
- 외화채권 환산 기준환율과 시점
