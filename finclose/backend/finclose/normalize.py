"""값 정규화. 실패하면 None과 오류 사유를 돌려주며, 추측으로 값을 만들지 않는다."""
from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

ISO_CURRENCIES = {
    "KRW", "USD", "EUR", "JPY", "CNY", "HKD", "GBP", "AUD", "SGD", "CHF", "CAD", "NZD", "TWD", "INR", "VND",
}
_NUM_CLEAN = re.compile(r"[,\s₩$€¥원]")


def is_blank(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, float) and v != v:  # NaN
        return True
    return isinstance(v, str) and v.strip() in ("", "-", "N/A", "n/a", "NaN", "nan", "#N/A")


def to_decimal(v: Any) -> tuple[Decimal | None, str | None]:
    if is_blank(v):
        return None, None
    if isinstance(v, bool):
        return None, "불리언 값"
    if isinstance(v, int):
        return Decimal(v), None
    if isinstance(v, float):
        # Excel float: repr 기반 변환(이진 부동소수 표현 그대로 확장하지 않음)
        return Decimal(repr(v)), None
    if isinstance(v, Decimal):
        return v, None
    s = str(v).strip()
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg, s = True, s[1:-1]
    s = _NUM_CLEAN.sub("", s)
    if s.endswith("-") and s[:-1].replace(".", "", 1).isdigit():  # "123-" 회계식 음수
        neg, s = True, s[:-1]
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None, f"숫자가 아님: {str(v)[:30]}"
    if not d.is_finite():
        return None, "유한하지 않은 숫자"
    return (-d if neg else d), None


_DATE_PATTERNS = ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S", "%Y.%m.%d.")


def to_date(v: Any) -> tuple[date | None, str | None]:
    if is_blank(v):
        return None, None
    if isinstance(v, datetime):
        return v.date(), None
    if isinstance(v, date):
        return v, None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        s = str(int(v)) if float(v).is_integer() else str(v)
        if len(s) == 8:
            v = s
        else:
            return None, f"날짜로 해석 불가(숫자): {v}"
    s = str(v).strip()
    s = re.sub(r"\s*\(.*\)$", "", s)
    for fmt in _DATE_PATTERNS:
        try:
            return datetime.strptime(s, fmt).date(), None
        except ValueError:
            pass
    m = re.match(r"^(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일$", s)
    if m:
        try:
            return date(int(m[1]), int(m[2]), int(m[3])), None
        except ValueError:
            pass
    return None, f"날짜 형식 오류: {s[:30]}"


def to_currency(v: Any) -> tuple[str | None, str | None]:
    if is_blank(v):
        return None, None
    s = str(v).strip().upper()
    if s in ("원", "₩", "WON"):
        s = "KRW"
    if s not in ISO_CURRENCIES:
        return None, f"알 수 없는 통화: {s[:10]}"
    return s, None


def to_code(v: Any) -> tuple[str | None, str | None]:
    if is_blank(v):
        return None, None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip().upper(), None


def to_text(v: Any) -> tuple[str | None, str | None]:
    if is_blank(v):
        return None, None
    return str(v).strip(), None


CONVERTERS = {
    "decimal": to_decimal, "money": to_decimal, "date": to_date,
    "currency": to_currency, "code": to_code, "text": to_text,
}
