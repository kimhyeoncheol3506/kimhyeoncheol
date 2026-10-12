"""기간 증감 분석과 이상 증감 탐지. 원인은 '후보'로만 제시하며 사실로 확정하지 않는다."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping

NEW, REMOVED, NO_CHANGE, ZERO_BASE, SIGN_CHANGE, RATE = (
    "NEW", "REMOVED", "NO_CHANGE", "N/A_ZERO_BASE", "SIGN_CHANGE", "RATE")


def change_rate(cur: Decimal | None, base: Decimal | None) -> tuple[str, Decimal | None]:
    if base is None and cur is None:
        return NO_CHANGE, None
    if base is None:
        return NEW, None
    if cur is None:
        return REMOVED, None
    if base == 0 and cur == 0:
        return NO_CHANGE, None
    if base == 0:
        return ZERO_BASE, None
    if cur != 0 and (cur > 0) != (base > 0):
        return SIGN_CHANGE, None
    return RATE, (cur - base) / abs(base)


def _share(v: Decimal | None, total: Decimal) -> Decimal | None:
    if v is None or total <= 0 or v < 0:
        return None
    return v / total


def compare(current: Mapping[Any, Mapping[str, Any]], base: Mapping[Any, Mapping[str, Any]],
            materiality: Mapping[str, Any]) -> dict[str, Any]:
    """current/base: key -> {amount: Decimal, quantity: Decimal|None, label: str}"""
    abs_th = Decimal(str(materiality.get("abs_amount", "100000000")))
    pct_th = Decimal(str(materiality.get("pct", "0.1")))
    share_th = Decimal(str(materiality.get("share_pp", "0.05")))
    qty_th = Decimal(str(materiality.get("qty_pct", "0.1")))
    tot_c = sum((v["amount"] for v in current.values() if v.get("amount") is not None), Decimal(0))
    tot_b = sum((v["amount"] for v in base.values() if v.get("amount") is not None), Decimal(0))
    rows: list[dict[str, Any]] = []
    for key in sorted(set(current) | set(base), key=str):
        c, b = current.get(key), base.get(key)
        ca, ba = (c or {}).get("amount"), (b or {}).get("amount")
        cq, bq = (c or {}).get("quantity"), (b or {}).get("quantity")
        status, rate = change_rate(ca, ba)
        delta = (ca or Decimal(0)) - (ba or Decimal(0))
        sc, sb = _share(ca, tot_c), _share(ba, tot_b)
        share_change = (sc - sb) if (sc is not None and sb is not None) else None
        flags: list[str] = []
        causes: list[str] = []
        if status == NEW:
            flags.append("신규 발생")
            causes.append("신규 취득 가능성 — 거래내역으로 확인 필요")
        elif status == REMOVED:
            flags.append("소멸")
            causes.append("매도·만기상환·분류변경 가능성 — 거래내역으로 확인 필요")
        if abs(delta) >= abs_th:
            flags.append(f"절대 증감 ≥ {abs_th:,.0f}")
        if rate is not None and abs(rate) >= pct_th:
            flags.append(f"증감률 ≥ {pct_th:.0%}")
        if status in (SIGN_CHANGE, ZERO_BASE):
            flags.append("증감률 산정 불가(부호전환/0 기준)")
        if share_change is not None and abs(share_change) >= share_th:
            flags.append(f"구성비 변화 ≥ {share_th * 100:.0f}%p")
        qty_rate = None
        if cq is not None and bq not in (None, Decimal(0)):
            qty_rate = (cq - bq) / abs(bq)
        if status == RATE:
            if qty_rate is not None and abs(qty_rate) < Decimal("0.0001") and rate is not None and rate != 0:
                causes.append("수량 불변 — 평가단가(가격) 변동이 원인일 가능성")
            if qty_rate is not None and abs(qty_rate) >= qty_th:
                causes.append("보유수량 변동 — 매매/상환 가능성(거래내역 확인 필요)")
                if rate is not None and abs(rate) < pct_th / 4:
                    flags.append("금액 유사·수량 급변")
        if causes:
            causes.append("※ 원천 거래자료로 확인되지 않은 추정입니다.")
        rows.append({
            "key": key if isinstance(key, str) else "|".join(map(str, key)),
            "label": (c or b or {}).get("label"),
            "current": ca, "base": ba, "delta": delta, "rate_status": status, "rate": rate,
            "current_qty": cq, "base_qty": bq, "qty_rate": qty_rate,
            "share_current": sc, "share_base": sb, "share_change": share_change,
            "flags": flags, "cause_candidates": causes, "anomaly": bool(flags),
        })
    t_status, t_rate = change_rate(tot_c if current else None, tot_b if base else None)
    return {
        "rows": rows,
        "total": {"current": tot_c, "base": tot_b, "delta": tot_c - tot_b, "rate_status": t_status, "rate": t_rate,
                  "current_count": len(current), "base_count": len(base),
                  "count_changed_amount_same": len(current) != len(base) and tot_c == tot_b},
        "anomaly_count": sum(1 for r in rows if r["anomaly"]),
        "thresholds": {"abs_amount": abs_th, "pct": pct_th, "share_pp": share_th, "qty_pct": qty_th},
    }
