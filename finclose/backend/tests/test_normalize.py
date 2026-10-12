from datetime import date, datetime
from decimal import Decimal

import pytest

from finclose.normalize import to_code, to_currency, to_date, to_decimal


@pytest.mark.parametrize("raw,expected", [
    ("1,234,567", "1234567"), ("(1,234)", "-1234"), ("123-", "-123"), ("₩1,000", "1000"), (" 12.50 ", "12.50"),
    (1234, "1234"), (0.1, "0.1"), ("-0.0001", "-0.0001"), (Decimal("5"), "5"),
])
def test_to_decimal(raw, expected):
    v, err = to_decimal(raw)
    assert err is None and v == Decimal(expected)


@pytest.mark.parametrize("raw", ["abc", "12a", "1.2.3", "Infinity"])
def test_to_decimal_errors(raw):
    v, err = to_decimal(raw)
    assert v is None and err


@pytest.mark.parametrize("raw", [None, "", "-", float("nan"), "#N/A"])
def test_blank_is_none_not_zero(raw):
    assert to_decimal(raw) == (None, None)


@pytest.mark.parametrize("raw", ["2026-09-30", "2026.09.30", "20260930", "2026/09/30", "2026년 9월 30일",
                                 datetime(2026, 9, 30, 0, 0), date(2026, 9, 30), 20260930])
def test_to_date(raw):
    assert to_date(raw) == (date(2026, 9, 30), None)


@pytest.mark.parametrize("raw", ["2026-02-30", "30/09/2026", "어제", 45000])
def test_to_date_errors(raw):
    v, err = to_date(raw)
    assert v is None and err


def test_currency():
    assert to_currency("krw") == ("KRW", None)
    assert to_currency("원") == ("KRW", None)
    assert to_currency("KRWW")[1]


def test_code_from_float():
    assert to_code(123.0) == ("123", None)
    assert to_code(" kr9test00001 ") == ("KR9TEST00001", None)
