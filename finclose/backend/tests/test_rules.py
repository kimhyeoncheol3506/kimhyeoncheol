from decimal import Decimal

import pytest

from finclose.rules import CalcError, CalcRule, RuleError, compile_expression, currency_decimals, quantize, run_rule_tests

BASE_RULE = {"rule_id": "R1", "expression": "quantity * price / price_unit", "inputs": ["quantity", "price"],
             "params": {"price_unit": "10000"}, "target": "v", "approval_status": "EXAMPLE",
             "test_cases": [{"inputs": {"quantity": "100", "price": "10000"}, "currency": "KRW", "expected": "100"}]}


def test_evaluate_decimal_and_rounding():
    r = CalcRule.from_dict(BASE_RULE)
    raw, rounded = r.evaluate({"quantity": Decimal("333"), "price": Decimal("10000.5")}, "KRW")
    assert raw == Decimal("333.016650")
    assert rounded == Decimal("333")
    _, usd = r.evaluate({"quantity": Decimal("1000000"), "price": Decimal("10050.125")}, "USD")
    assert usd == Decimal("1005012.50")


@pytest.mark.parametrize("mode,expected", [("ROUND_HALF_UP", "3"), ("ROUND_DOWN", "2"), ("ROUND_HALF_EVEN", "2")])
def test_rounding_modes(mode, expected):
    assert quantize(Decimal("2.5"), 0, mode) == Decimal(expected)


def test_half_up_negative_away_from_zero():
    assert quantize(Decimal("-2.5"), 0, "ROUND_HALF_UP") == Decimal("-3")


def test_division_by_zero_is_row_error_not_zero():
    r = CalcRule.from_dict({**BASE_RULE, "params": {"price_unit": "0"}})
    with pytest.raises(CalcError, match="0으로"):
        r.evaluate({"quantity": Decimal(1), "price": Decimal(1)}, "KRW")


def test_missing_input():
    r = CalcRule.from_dict(BASE_RULE)
    with pytest.raises(CalcError, match="누락"):
        r.evaluate({"quantity": Decimal(1), "price": None}, "KRW")


@pytest.mark.parametrize("expr", ["__import__('os').system('x')", "quantity.real", "(lambda: 1)()", "quantity ** 2",
                                  "open('x')", "[1][0]", "quantity if price else 1"])
def test_forbidden_syntax(expr):
    with pytest.raises(RuleError):
        compile_expression(expr, {"quantity", "price"})


def test_unknown_name_rejected():
    with pytest.raises(RuleError, match="정의되지 않은"):
        CalcRule.from_dict({**BASE_RULE, "expression": "quantity * fx"})


def test_unknown_currency_decimals():
    with pytest.raises(CalcError):
        currency_decimals("XYZ")


def test_rule_tests_detect_wrong_expected_and_missing_cases():
    bad = {**BASE_RULE, "test_cases": [{"inputs": {"quantity": "100", "price": "10000"}, "currency": "KRW", "expected": "101"}]}
    none = {**BASE_RULE, "rule_id": "R2", "test_cases": []}
    res = run_rule_tests([bad, none])
    assert not res["ok"]
    assert any("테스트케이스 없음" in (r.get("error") or "") for r in res["results"])


def test_wrong_rule_definition_reported():
    res = run_rule_tests([{**BASE_RULE, "expression": "quantity *"}])
    assert not res["ok"] and "규칙 정의 오류" in res["results"][0]["error"]


def test_invalid_approval_status():
    with pytest.raises(RuleError):
        CalcRule.from_dict({**BASE_RULE, "approval_status": "AUTO_APPROVED"})
