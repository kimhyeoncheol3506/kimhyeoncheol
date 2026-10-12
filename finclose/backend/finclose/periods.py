"""결산 기간 계산(달력 기준 월말). 영업일 조정은 하지 않으며, 기준일이 월말이 아니면 경고 대상이다."""
from __future__ import annotations

import calendar
from datetime import date, timedelta


def month_end(d: date) -> date:
    return date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])


def is_month_end(d: date) -> bool:
    return d == month_end(d)


def prev_month_end(d: date) -> date:
    return date(d.year, d.month, 1) - timedelta(days=1)


def prev_quarter_end(d: date) -> date:
    q_start_month = 3 * ((d.month - 1) // 3) + 1
    return date(d.year, q_start_month, 1) - timedelta(days=1)


def same_period_last_year(d: date) -> date:
    return month_end(date(d.year - 1, d.month, 1))


def prior_fiscal_year_end(d: date, fy_end_month: int = 12) -> date:
    y = d.year if d.month > fy_end_month else d.year - 1
    return month_end(date(y, fy_end_month, 1))


def comparison_targets(d: date, fy_end_month: int = 12) -> dict[str, date]:
    return {
        "PREV_MONTH": prev_month_end(d),
        "PREV_QUARTER": prev_quarter_end(d),
        "SAME_PERIOD_LAST_YEAR": same_period_last_year(d),
        "PRIOR_YEAR_END": prior_fiscal_year_end(d, fy_end_month),
    }


def last_n_month_ends(d: date, n: int = 12) -> list[date]:
    out = [month_end(d)]
    while len(out) < n:
        out.append(prev_month_end(out[-1]))
    return list(reversed(out))


PERIOD_LABELS = {
    "PREV_MONTH": "전월 대비", "PREV_QUARTER": "전분기말 대비", "SAME_PERIOD_LAST_YEAR": "전년 동기 대비",
    "PRIOR_YEAR_END": "전기말 대비", "PRIOR_FILE": "전월 결과파일 대비",
}
