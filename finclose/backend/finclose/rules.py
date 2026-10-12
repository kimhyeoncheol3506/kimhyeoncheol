"""계산 규칙 엔진.

- 수식은 `ast`로 파싱한 뒤 허용된 노드만 해석한다(eval/exec 미사용).
- 모든 연산은 Decimal(정밀도 50자리)로 수행하고, 반올림은 최종 단계에서 1회만 한다.
- 오류(0 나누기, 입력 누락)는 예외로 올려 호출자가 행 단위 예외로 기록한다. 0으로 대체하지 않는다.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Context, Decimal, localcontext
from typing import Any, Mapping

CURRENCY_DECIMALS: dict[str, int] = {
    "KRW": 0, "JPY": 0, "USD": 2, "EUR": 2, "CNY": 2, "HKD": 2, "GBP": 2, "AUD": 2, "SGD": 2, "CHF": 2,
}
ROUNDING_MODES = {"ROUND_HALF_UP": ROUND_HALF_UP, "ROUND_DOWN": ROUND_DOWN, "ROUND_HALF_EVEN": ROUND_HALF_EVEN}
APPROVAL_STATUSES = ("APPROVED", "EXAMPLE", "DRAFT")
_CTX = Context(prec=50)


class RuleError(Exception):
    """규칙 정의 자체가 잘못된 경우(잘못된 수식, 허용되지 않은 구문)."""


class CalcError(Exception):
    """행 단위 계산 실패(입력 누락, 0 나누기)."""


_ALLOWED_FUNCS = {"abs", "min", "max"}


def _check(node: ast.AST, allowed_names: set[str]) -> None:
    for n in ast.walk(node):
        if isinstance(n, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Load,
                          ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd)):
            continue
        if isinstance(n, ast.Constant):
            if not isinstance(n.value, (int, float, str)) or isinstance(n.value, bool):
                raise RuleError(f"허용되지 않은 상수: {n.value!r}")
            continue
        if isinstance(n, ast.Name):
            if n.id not in allowed_names and n.id not in _ALLOWED_FUNCS:
                raise RuleError(f"정의되지 않은 이름: {n.id}")
            continue
        if isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name) or n.func.id not in _ALLOWED_FUNCS or n.keywords:
                raise RuleError("허용되지 않은 함수 호출")
            continue
        raise RuleError(f"허용되지 않은 구문: {type(n).__name__}")


def compile_expression(expr: str, names: set[str]) -> ast.Expression:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise RuleError(f"수식 문법 오류: {e.msg}") from e
    _check(tree, names)
    return tree


def _eval(node: ast.AST, env: Mapping[str, Decimal]) -> Decimal:
    if isinstance(node, ast.Expression):
        return _eval(node.body, env)
    if isinstance(node, ast.Constant):
        return Decimal(str(node.value))
    if isinstance(node, ast.Name):
        v = env.get(node.id)
        if v is None:
            raise CalcError(f"입력값 누락: {node.id}")
        return v
    if isinstance(node, ast.UnaryOp):
        v = _eval(node.operand, env)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp):
        a, b = _eval(node.left, env), _eval(node.right, env)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        if isinstance(node.op, ast.Div):
            if b == 0:
                raise CalcError("0으로 나누기")
            return a / b
    if isinstance(node, ast.Call):
        args = [_eval(a, env) for a in node.args]
        fn = node.func.id  # type: ignore[attr-defined]
        if fn == "abs":
            return abs(args[0])
        if fn == "min":
            return min(args)
        if fn == "max":
            return max(args)
    raise RuleError("해석할 수 없는 수식")


def quantize(value: Decimal, decimals: int, mode: str = "ROUND_HALF_UP") -> Decimal:
    if mode not in ROUNDING_MODES:
        raise RuleError(f"알 수 없는 반올림 방식: {mode}")
    exp = Decimal(1).scaleb(-decimals)
    return value.quantize(exp, rounding=ROUNDING_MODES[mode])


def currency_decimals(currency: str | None, overrides: Mapping[str, int] | None = None) -> int:
    table = {**CURRENCY_DECIMALS, **(overrides or {})}
    if currency not in table:
        raise CalcError(f"통화 소수자릿수 미정의: {currency}")
    return table[currency]


@dataclass
class CalcRule:
    rule_id: str
    name: str
    expression: str
    target: str
    inputs: list[str]
    params: dict[str, str]
    rounding_mode: str
    by_currency: bool
    fixed_decimals: int | None
    approval_status: str
    version: int
    raw: dict[str, Any]
    _tree: ast.Expression | None = None

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "CalcRule":
        for k in ("rule_id", "expression", "target", "inputs"):
            if k not in d:
                raise RuleError(f"규칙 필수 항목 누락: {k}")
        status = d.get("approval_status", "DRAFT")
        if status not in APPROVAL_STATUSES:
            raise RuleError(f"알 수 없는 승인상태: {status}")
        rounding = d.get("rounding") or {}
        params = {k: str(v) for k, v in (d.get("params") or {}).items()}
        for v in params.values():
            Decimal(v)  # 파라미터는 숫자여야 함
        rule = cls(
            rule_id=d["rule_id"], name=d.get("name", d["rule_id"]), expression=d["expression"],
            target=d["target"], inputs=list(d["inputs"]), params=params,
            rounding_mode=rounding.get("mode", "ROUND_HALF_UP"),
            by_currency=bool(rounding.get("by_currency", True)),
            fixed_decimals=rounding.get("decimals"),
            approval_status=status, version=int(d.get("version", 1)), raw=dict(d),
        )
        if rule.rounding_mode not in ROUNDING_MODES:
            raise RuleError(f"알 수 없는 반올림 방식: {rule.rounding_mode}")
        rule._tree = compile_expression(rule.expression, set(rule.inputs) | set(params))
        return rule

    def evaluate_unrounded(self, inputs: Mapping[str, Decimal | None]) -> Decimal:
        env: dict[str, Decimal] = {k: Decimal(v) for k, v in self.params.items()}
        for name in self.inputs:
            v = inputs.get(name)
            if v is None:
                raise CalcError(f"입력값 누락: {name}")
            env[name] = v
        with localcontext(_CTX):
            return _eval(self._tree, env)  # type: ignore[arg-type]

    def decimals_for(self, currency: str | None) -> int:
        if self.by_currency:
            return currency_decimals(currency)
        return int(self.fixed_decimals or 0)

    def evaluate(self, inputs: Mapping[str, Decimal | None], currency: str | None) -> tuple[Decimal, Decimal]:
        """(반올림 전 값, 반올림 후 값)"""
        raw = self.evaluate_unrounded(inputs)
        return raw, quantize(raw, self.decimals_for(currency), self.rounding_mode)


def run_rule_tests(rule_dicts: list[Mapping[str, Any]]) -> dict[str, Any]:
    """템플릿의 모든 규칙 테스트케이스 실행. 테스트가 없는 규칙은 실패로 본다."""
    results = []
    ok = True
    for d in rule_dicts:
        rid = d.get("rule_id", "?")
        try:
            rule = CalcRule.from_dict(d)
        except (RuleError, ArithmeticError, ValueError) as e:
            results.append({"rule_id": rid, "case": None, "ok": False, "error": f"규칙 정의 오류: {e}"})
            ok = False
            continue
        cases = d.get("test_cases") or []
        if not cases:
            results.append({"rule_id": rid, "case": None, "ok": False, "error": "테스트케이스 없음"})
            ok = False
        for i, case in enumerate(cases):
            try:
                ins = {k: (Decimal(str(v)) if v is not None else None) for k, v in case.get("inputs", {}).items()}
                expect_error = case.get("expect_error")
                try:
                    _, got = rule.evaluate(ins, case.get("currency"))
                    passed = (not expect_error) and got == Decimal(str(case["expected"]))
                    detail = f"기대 {case.get('expected')} / 결과 {got}"
                except CalcError as ce:
                    passed = bool(expect_error)
                    detail = f"계산오류: {ce}"
            except Exception as e:  # 잘못된 테스트케이스 자체
                passed, detail = False, f"테스트케이스 오류: {e}"
            ok = ok and passed
            results.append({"rule_id": rid, "case": i, "ok": passed, "detail": detail})
    return {"ok": ok, "results": results}
