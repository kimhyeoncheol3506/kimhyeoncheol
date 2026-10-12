"""데이터 프로파일링. 금액·수량은 평균 하나로 정상 여부를 판단하지 않고 IQR 이상값 후보만 제시한다."""
from __future__ import annotations

import re
import statistics
from collections import Counter
from decimal import Decimal
from typing import Any

from .normalize import is_blank, to_date, to_decimal
from .parsers.common import ParsedTable

_SPECIAL = re.compile(r"[^\w\s가-힣.,\-()/%:+&@#]")


def _kind(v: Any) -> str:
    if isinstance(v, bool):
        return "text"
    if isinstance(v, (int, float, Decimal)):
        return "number"
    if hasattr(v, "year") and hasattr(v, "month"):
        return "date"
    s = str(v).strip()
    if to_decimal(s)[0] is not None:
        return "number"
    if re.match(r"^\d{4}[-./]\d{1,2}[-./]\d{1,2}", s) and to_date(s)[0] is not None:
        return "date"
    return "text"


def profile_column(values: list[Any]) -> dict[str, Any]:
    n = len(values)
    present = [v for v in values if not is_blank(v)]
    missing = n - len(present)
    keyed = [str(v).strip() if isinstance(v, str) else v for v in present]
    counts = Counter(map(str, keyed))
    dup_rows = sum(c for c in counts.values() if c > 1)
    kinds = Counter(_kind(v) for v in present)
    inferred = kinds.most_common(1)[0][0] if kinds else "empty"
    out: dict[str, Any] = {
        "count": n, "missing": missing, "missing_ratio": round(missing / n, 4) if n else 0,
        "unique": len(counts), "duplicate_rows": dup_rows, "inferred_type": inferred,
        "type_mix": dict(kinds), "mixed_types": len(kinds) > 1,
        "top_values": [{"value": k, "count": c} for k, c in counts.most_common(5)],
    }
    strs = [v for v in present if isinstance(v, str)]
    out["leading_trailing_spaces"] = sum(1 for s in strs if s != s.strip())
    out["special_char_values"] = sum(1 for s in strs if _SPECIAL.search(s))
    if inferred == "number":
        nums = [d for d in (to_decimal(v)[0] for v in present) if d is not None]
        bad = [v for v in present if to_decimal(v)[0] is None]
        out["non_numeric_values"] = len(bad)
        out["non_numeric_examples"] = [str(b)[:30] for b in bad[:5]]
        if nums:
            fl = sorted(float(x) for x in nums)
            out.update({
                "min": str(min(nums)), "max": str(max(nums)), "sum": str(sum(nums)),
                "mean": round(statistics.fmean(fl), 6), "median": statistics.median(fl),
                "negative_count": sum(1 for x in nums if x < 0), "zero_count": sum(1 for x in nums if x == 0),
            })
            if len(fl) >= 8:
                q1, _, q3 = statistics.quantiles(fl, n=4)
                iqr = q3 - q1
                lo, hi = q1 - 3 * iqr, q3 + 3 * iqr
                outl = [x for x in fl if x < lo or x > hi]
                out["outlier_candidates"] = len(outl)
                out["outlier_rule"] = "IQR×3 (검토 후보일 뿐 오류 판정 아님)"
    elif inferred == "date":
        ds = [d for d in (to_date(v)[0] for v in present) if d is not None]
        out["invalid_dates"] = len(present) - len(ds)
        if ds:
            out["date_min"], out["date_max"] = min(ds).isoformat(), max(ds).isoformat()
            out["distinct_dates"] = len(set(ds))
    return out


def profile_table(t: ParsedTable) -> dict[str, Any]:
    cols = {}
    for i, c in enumerate(t.columns):
        cols[c] = profile_column([r[i] if i < len(r) else None for r in t.rows])
    full_dups = len(t.rows) - len({tuple(map(str, r)) for r in t.rows})
    return {"table": t.name, "row_count": len(t.rows), "column_count": len(t.columns),
            "duplicate_full_rows": full_dups, "columns": cols}
