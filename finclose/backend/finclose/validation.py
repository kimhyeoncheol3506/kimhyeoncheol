"""검증 엔진 공통 구조 + 독립 재계산 도구.

독립 재계산은 rules.py의 Decimal 해석기를 쓰지 않고 fractions.Fraction과 별도의 반올림 구현으로 수행한다.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from fractions import Fraction
from typing import Any, Mapping

PASS, WARNING, FAIL, REVIEW_REQUIRED, NOT_APPLICABLE, NOT_RUN = (
    "PASS", "WARNING", "FAIL", "REVIEW_REQUIRED", "NOT_APPLICABLE", "NOT_RUN")
STATUSES = (PASS, WARNING, FAIL, REVIEW_REQUIRED, NOT_APPLICABLE, NOT_RUN)
CRITICAL, HIGH, MEDIUM, LOW = "CRITICAL", "HIGH", "MEDIUM", "LOW"
SEVERITY_ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3}
CATEGORIES = {"F": "파일", "D": "데이터", "R": "대사", "T": "합계", "C": "계산", "A": "회계", "V": "기간비교", "J": "전표"}
MAX_DETAILS = 500


@dataclass
class Check:
    check_id: str
    name: str
    status: str
    severity: str
    message: str
    mandatory: bool = True
    method: str = ""
    details: list[dict[str, Any]] = field(default_factory=list)
    details_truncated: int = 0

    @property
    def category(self) -> str:
        return CATEGORIES.get(self.check_id[:1], "기타")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category
        return d


class CheckBook:
    """검증 결과 모음. 같은 ID는 한 번만 기록된다."""

    def __init__(self, overrides: Mapping[str, Mapping[str, Any]] | None = None):
        self.checks: dict[str, Check] = {}
        self.overrides = overrides or {}

    def add(self, check_id: str, name: str, status: str, severity: str, message: str, *,
            mandatory: bool = True, method: str = "", details: list[dict[str, Any]] | None = None) -> Check:
        assert status in STATUSES, status
        ov = self.overrides.get(check_id, {})
        severity = ov.get("severity", severity)
        mandatory = ov.get("mandatory", mandatory)
        if status in (NOT_APPLICABLE, NOT_RUN) and not message:
            raise ValueError("NOT_APPLICABLE/NOT_RUN에는 사유가 필요합니다.")
        details = details or []
        c = Check(check_id, name, status, severity, message, mandatory, method,
                  details[:MAX_DETAILS], max(0, len(details) - MAX_DETAILS))
        self.checks[check_id] = c
        return c

    def result(self, check_id: str, name: str, failures: list[dict[str, Any]], severity: str, ok_msg: str,
               fail_msg: str, *, fail_status: str = FAIL, mandatory: bool = True, method: str = "") -> Check:
        if failures:
            return self.add(check_id, name, fail_status, severity, fail_msg.format(n=len(failures)),
                            mandatory=mandatory, method=method, details=failures)
        return self.add(check_id, name, PASS, severity, ok_msg, mandatory=mandatory, method=method)

    def not_run(self, check_id: str, name: str, reason: str, severity: str = HIGH, mandatory: bool = True) -> Check:
        return self.add(check_id, name, NOT_RUN, severity, reason, mandatory=mandatory)

    def has(self, check_id: str) -> bool:
        return check_id in self.checks

    def list(self) -> list[dict[str, Any]]:
        return [c.to_dict() for c in sorted(self.checks.values(), key=lambda c: (c.check_id[:1], c.check_id))]


def summarize(checks: list[dict[str, Any]]) -> dict[str, Any]:
    by_status = {s: 0 for s in STATUSES}
    for c in checks:
        by_status[c["status"]] += 1
    return {"total": len(checks), "by_status": by_status}


# ---------------- 독립 재계산(Fraction) ----------------

def _feval(node: ast.AST, env: Mapping[str, Fraction]) -> Fraction:
    if isinstance(node, ast.Expression):
        return _feval(node.body, env)
    if isinstance(node, ast.Constant):
        return Fraction(str(node.value))
    if isinstance(node, ast.Name):
        return env[node.id]
    if isinstance(node, ast.UnaryOp):
        v = _feval(node.operand, env)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp):
        a, b = _feval(node.left, env), _feval(node.right, env)
        ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b, ast.Div: lambda: a / b}
        return ops[type(node.op)]()
    if isinstance(node, ast.Call):
        args = [_feval(x, env) for x in node.args]
        return {"abs": lambda: abs(args[0]), "min": lambda: min(args), "max": lambda: max(args)}[node.func.id]()  # type: ignore[attr-defined]
    raise ValueError("지원하지 않는 수식")


def fraction_eval(expression: str, env: Mapping[str, Any]) -> Fraction:
    tree = ast.parse(expression, mode="eval")
    return _feval(tree, {k: Fraction(str(v)) for k, v in env.items()})


def fraction_round(x: Fraction, decimals: int, mode: str) -> Fraction:
    """정수 연산 기반 반올림(rules.quantize와 다른 구현)."""
    scale = 10 ** decimals
    scaled = x * scale
    sign = -1 if scaled < 0 else 1
    a = abs(scaled)
    whole, rem = divmod(a.numerator, a.denominator)
    rem_frac = Fraction(rem, a.denominator)
    if mode == "ROUND_DOWN":
        q = whole
    elif mode == "ROUND_HALF_EVEN":
        q = whole + (1 if rem_frac > Fraction(1, 2) or (rem_frac == Fraction(1, 2) and whole % 2 == 1) else 0)
    else:  # ROUND_HALF_UP (0에서 먼 쪽)
        q = whole + (1 if rem_frac >= Fraction(1, 2) else 0)
    return Fraction(sign * q, scale)


def frac_to_dec(x: Fraction) -> Decimal:
    return Decimal(x.numerator) / Decimal(x.denominator)
