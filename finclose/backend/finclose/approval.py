"""검토·승인 워크플로와 확정 차단 게이트."""
from __future__ import annotations

from typing import Any

from .validation import CRITICAL, FAIL, HIGH, NOT_RUN, REVIEW_REQUIRED

ACTIONS = ("REVIEW", "ACKNOWLEDGE", "EXCEPTION", "APPROVE", "REJECT", "FINALIZE")


class ApprovalError(Exception):
    pass


def gate(run: dict[str, Any], checks: list[dict[str, Any]], approvals: list[dict[str, Any]],
         other_finalized: list[str]) -> dict[str, Any]:
    acked = {a["check_id"] for a in approvals if a["action"] == "ACKNOWLEDGE"}
    excepted = {a["check_id"] for a in approvals if a["action"] == "EXCEPTION"}
    blockers, pending = [], []
    for c in checks:
        cid = c["check_id"]
        if c["status"] == FAIL and c["severity"] == CRITICAL:
            blockers.append({"check_id": cid, "reason": f"CRITICAL 실패: {c['message']}", "exceptionable": False})
        elif c["status"] == FAIL and c["severity"] == HIGH and cid not in excepted:
            blockers.append({"check_id": cid, "reason": f"HIGH 실패(예외승인 필요): {c['message']}", "exceptionable": True})
        elif c["status"] == NOT_RUN and c.get("mandatory"):
            blockers.append({"check_id": cid, "reason": f"필수 검증 미수행: {c['message']}", "exceptionable": False})
        elif c["status"] == REVIEW_REQUIRED and cid not in acked:
            pending.append({"check_id": cid, "reason": f"검토 확인 필요: {c['message']}"})
    if other_finalized:
        blockers.append({"check_id": None, "reason": f"같은 업무·기준일로 이미 확정된 실행 존재({', '.join(other_finalized)}) — 중복 반영 위험",
                         "exceptionable": False})
    data_ok = not blockers and not pending
    return {"data_ok": data_ok, "blockers": blockers, "pending_reviews": pending,
            "can_approve": data_ok and run["status"] == "REVIEWED",
            "can_finalize": data_ok and run["status"] == "APPROVED",
            "status_after_checks": "BLOCKED" if blockers else "READY_FOR_REVIEW"}


def validate_action(action: str, run: dict[str, Any], check: dict[str, Any] | None, actor: str, role: str,
                    comment: str, g: dict[str, Any]) -> str | None:
    """허용되면 다음 실행 상태(None=변화 없음), 아니면 ApprovalError."""
    if action not in ACTIONS:
        raise ApprovalError(f"알 수 없는 작업: {action}")
    if not comment or len(comment.strip()) < 2:
        raise ApprovalError("의견/사유를 입력하세요.")
    st = run["status"]
    if st in ("FINALIZED", "REJECTED", "FAILED", "RUNNING"):
        raise ApprovalError(f"'{st}' 상태의 실행에는 작업할 수 없습니다.")
    if action in ("REVIEW", "APPROVE", "ACKNOWLEDGE", "EXCEPTION") and actor == run["created_by"]:
        raise ApprovalError("직무분리: 실행을 생성한 사용자는 검토·확인·예외승인·승인할 수 없습니다.")
    if action == "ACKNOWLEDGE":
        if not check or check["status"] != REVIEW_REQUIRED:
            raise ApprovalError("REVIEW_REQUIRED 항목만 확인 처리할 수 있습니다.")
        return None
    if action == "EXCEPTION":
        if not check or check["status"] != FAIL:
            raise ApprovalError("FAIL 항목만 예외승인할 수 있습니다.")
        if check["severity"] == CRITICAL:
            raise ApprovalError("CRITICAL 실패는 예외승인할 수 없습니다. 원천 데이터를 수정해 재실행하세요.")
        return None
    if action == "REVIEW":
        if st not in ("READY_FOR_REVIEW", "BLOCKED", "REVIEWED"):
            raise ApprovalError("검토할 수 없는 상태입니다.")
        return "REVIEWED"
    if action == "APPROVE":
        if st != "REVIEWED":
            raise ApprovalError("검토(REVIEWED) 완료 후 승인할 수 있습니다.")
        if not g["data_ok"]:
            raise ApprovalError("차단 사유가 남아 있어 승인할 수 없습니다: " + "; ".join(
                b["reason"] for b in g["blockers"] + g["pending_reviews"])[:500])
        return "APPROVED"
    if action == "REJECT":
        return "REJECTED"
    raise ApprovalError("확정은 finalize 엔드포인트를 사용하세요.")
