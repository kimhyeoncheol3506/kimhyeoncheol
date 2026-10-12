"""감사 추적. 각 레코드는 이전 레코드의 해시를 포함하는 해시 체인으로 변조를 탐지한다.

감사 로그에는 비밀번호·API 키·행 단위 금액 데이터를 기록하지 않는다.
"""
from __future__ import annotations

import hashlib
from typing import Any

from .db import Database, dumps, now_iso

GENESIS = "0" * 64
_FORBIDDEN_KEYS = {"password", "passwd", "secret", "api_key", "apikey", "token"}


def _scrub(details: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in details.items():
        if k.lower() in _FORBIDDEN_KEYS:
            out[k] = "***"
        elif isinstance(v, dict):
            out[k] = _scrub(v)
        else:
            out[k] = v
    return out


def _hash(prev_hash: str, at: str, actor: str, role: str, action: str, etype: str, eid: str, details: str) -> str:
    payload = "|".join([prev_hash, at, actor, role, action, etype, eid, details])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record(db: Database, actor: str, role: str, action: str, entity_type: str, entity_id: str,
           details: dict[str, Any] | None = None) -> None:
    details_json = dumps(_scrub(details or {}))
    at = now_iso()
    with db.tx() as c:
        row = c.execute("SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
        prev = row["hash"] if row else GENESIS
        h = _hash(prev, at, actor, role, action, entity_type, entity_id, details_json)
        c.execute(
            "INSERT INTO audit_log(at, actor, role, action, entity_type, entity_id, details_json, prev_hash, hash)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (at, actor, role, action, entity_type, entity_id, details_json, prev, h),
        )


def verify_chain(db: Database) -> dict[str, Any]:
    prev = GENESIS
    rows = db.query("SELECT * FROM audit_log ORDER BY id")
    for r in rows:
        expected = _hash(prev, r["at"], r["actor"], r["role"], r["action"], r["entity_type"],
                         r["entity_id"], r["details_json"])
        if r["prev_hash"] != prev or r["hash"] != expected:
            return {"ok": False, "broken_at_id": r["id"], "count": len(rows)}
        prev = r["hash"]
    return {"ok": True, "broken_at_id": None, "count": len(rows)}
