"""분개 초안 생성과 차변·대변 검증. 원장 반영(POSTED) 상태는 이 모듈이 만들지 않는다."""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any, Mapping

DRAFT = "DRAFT"


def build_valuation_journal(rows: list[Mapping[str, Any]], cfg: Mapping[str, Any], base_date: str,
                            run_id: str) -> list[dict[str, Any]]:
    """평가손익(amount_field)의 부호에 따라 positive/negative 계정쌍으로 분개 초안을 만든다(통화별 전표)."""
    lines: list[dict[str, Any]] = []
    field = cfg["amount_field"]
    seq = defaultdict(int)
    for r in rows:
        amt: Decimal | None = r.get(field)
        if amt is None or amt == 0:
            continue
        pair = cfg["positive"] if amt > 0 else cfg["negative"]
        cur = r.get("currency")
        voucher = f"DRAFT-{base_date.replace('-', '')}-{cur}"
        memo = str(cfg.get("memo", "{name} 평가")).format(**{k: (v if v is not None else "") for k, v in r.items()})
        for side in ("debit", "credit"):
            seq[voucher] += 1
            lines.append({
                "voucher_no": voucher, "line_no": seq[voucher], "entry_date": base_date,
                "voucher_type": cfg.get("voucher_type", "결산"), "account_code": pair[side]["code"],
                "account_name": pair[side]["name"], "debit": abs(amt) if side == "debit" else Decimal(0),
                "credit": abs(amt) if side == "credit" else Decimal(0), "currency": cur,
                "counterparty": r.get("code"), "department": cfg.get("department", ""), "memo": memo,
                "source_row": r.get("_src"), "rule_id": cfg.get("rule_id", "JOURNAL"),
                "reason": cfg.get("reason", "평가손익 인식(예시)"), "status": DRAFT,
                "policy_status": cfg.get("policy_status", "EXAMPLE"), "run_id": run_id,
            })
    return lines


def balance_check(lines: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """전표(voucher_no, currency)별 차변합=대변합 확인. 불일치 목록 반환."""
    sums: dict[tuple, list[Decimal]] = defaultdict(lambda: [Decimal(0), Decimal(0), 0])  # type: ignore[arg-type]
    for ln in lines:
        k = (ln.get("voucher_no"), ln.get("currency"))
        sums[k][0] += ln.get("debit") or Decimal(0)
        sums[k][1] += ln.get("credit") or Decimal(0)
        sums[k][2] += 1
    bad = []
    for (v, cur), (dr, cr, n) in sorted(sums.items(), key=lambda x: str(x[0])):
        if dr != cr:
            bad.append({"voucher_no": v, "currency": cur, "debit": dr, "credit": cr, "difference": dr - cr,
                        "lines": n, "reason": "차변 합계 ≠ 대변 합계"})
    return bad
