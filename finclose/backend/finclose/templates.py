"""업무 템플릿 레지스트리. 버전은 불변(immutable)이며 수정은 항상 새 버전을 만든다."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from . import audit
from .db import Database, dumps, loads, now_iso
from .engine import validate_template
from .rules import run_rule_tests

BUILTIN_DIR = Path(__file__).parent / "templates"
STATUSES = ("DRAFT", "ACTIVE", "INACTIVE", "SUPERSEDED")


class TemplateRegistryError(Exception):
    pass


def _row(r: dict[str, Any]) -> dict[str, Any]:
    r = dict(r)
    r["body"] = loads(r.pop("body_json"))
    r["test_result"] = loads(r.pop("test_result_json"))
    return r


def seed_builtin(db: Database) -> None:
    for p in sorted(BUILTIN_DIR.glob("*.json")):
        body = json.loads(p.read_text(encoding="utf-8"))
        if not db.one("SELECT 1 FROM templates WHERE template_key=?", (body["template_key"],)):
            tests = run_rule_tests(body.get("calculations", [])) if body.get("calculations") else {"ok": True, "results": []}
            body["version"] = 1
            db.execute(
                "INSERT INTO templates(template_key, version, name, status, body_json, created_at, created_by, change_reason, test_result_json)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (body["template_key"], 1, body["name"], "ACTIVE" if tests["ok"] else "DRAFT", dumps(body), now_iso(),
                 "system", "기본 제공 템플릿", dumps(tests)))
            audit.record(db, "system", "admin", "TEMPLATE_SEEDED", "template", f"{body['template_key']}v1", {"file": p.name})


def list_templates(db: Database) -> list[dict[str, Any]]:
    rows = db.query("SELECT * FROM templates ORDER BY template_key, version DESC")
    return [_row(r) for r in rows]


def get(db: Database, key: str, version: int | None = None) -> dict[str, Any] | None:
    if version is None:
        r = db.one("SELECT * FROM templates WHERE template_key=? AND status='ACTIVE' ORDER BY version DESC LIMIT 1", (key,))
    else:
        r = db.one("SELECT * FROM templates WHERE template_key=? AND version=?", (key, version))
    return _row(r) if r else None


def latest(db: Database, key: str) -> dict[str, Any] | None:
    r = db.one("SELECT * FROM templates WHERE template_key=? ORDER BY version DESC LIMIT 1", (key,))
    return _row(r) if r else None


def save_version(db: Database, body: dict[str, Any], actor: str, role: str, reason: str) -> dict[str, Any]:
    """새 버전을 DRAFT로 저장. 이전 버전은 수정·삭제하지 않는다."""
    if not reason or len(reason.strip()) < 2:
        raise TemplateRegistryError("변경 사유를 입력하세요.")
    body = copy.deepcopy(body)
    errs = validate_template(body)
    if errs:
        raise TemplateRegistryError("; ".join(errs))
    key = body["template_key"]
    prev = latest(db, key)
    version = (prev["version"] + 1) if prev else 1
    if prev and role not in ("admin", "approver"):
        # 승인 상태를 스스로 올리는 것을 방지: 담당자는 규칙 승인상태를 APPROVED로 바꿀 수 없다
        prev_status = {c["rule_id"]: c.get("approval_status") for c in prev["body"].get("calculations", [])}
        for c in body.get("calculations", []):
            if c.get("approval_status") == "APPROVED" and prev_status.get(c["rule_id"]) != "APPROVED":
                raise TemplateRegistryError(f"규칙 {c['rule_id']}를 APPROVED로 변경하려면 승인자 권한이 필요합니다.")
        pj = (prev["body"].get("journal") or {}).get("policy_status")
        if (body.get("journal") or {}).get("policy_status") == "APPROVED" and pj != "APPROVED":
            raise TemplateRegistryError("분개 정책을 APPROVED로 변경하려면 승인자 권한이 필요합니다.")
    body["version"] = version
    tests = run_rule_tests(body.get("calculations", [])) if body.get("calculations") else {"ok": True, "results": []}
    db.execute(
        "INSERT INTO templates(template_key, version, name, status, body_json, created_at, created_by, change_reason, test_result_json)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (key, version, body["name"], "DRAFT", dumps(body), now_iso(), actor, reason.strip(), dumps(tests)))
    audit.record(db, actor, role, "TEMPLATE_VERSION_CREATED", "template", f"{key}v{version}",
                 {"reason": reason.strip(), "tests_ok": tests["ok"], "from_version": prev and prev["version"]})
    return get(db, key, version)  # type: ignore[return-value]


def set_status(db: Database, key: str, version: int, status: str, actor: str, role: str, reason: str) -> dict[str, Any]:
    if status not in ("ACTIVE", "INACTIVE"):
        raise TemplateRegistryError("상태는 ACTIVE 또는 INACTIVE만 지정할 수 있습니다.")
    t = get(db, key, version)
    if not t:
        raise TemplateRegistryError("템플릿이 없습니다.")
    if status == "ACTIVE":
        tests = run_rule_tests(t["body"].get("calculations", [])) if t["body"].get("calculations") else {"ok": True, "results": []}
        if not tests["ok"]:
            db.execute("UPDATE templates SET test_result_json=? WHERE template_key=? AND version=?", (dumps(tests), key, version))
            raise TemplateRegistryError("규칙 테스트가 실패해 활성화할 수 없습니다.")
        with db.tx() as c:
            c.execute("UPDATE templates SET status='SUPERSEDED' WHERE template_key=? AND status='ACTIVE' AND version<>?", (key, version))
            c.execute("UPDATE templates SET status='ACTIVE', test_result_json=? WHERE template_key=? AND version=?",
                      (dumps(tests), key, version))
    else:
        db.execute("UPDATE templates SET status='INACTIVE' WHERE template_key=? AND version=?", (key, version))
    audit.record(db, actor, role, f"TEMPLATE_{status}", "template", f"{key}v{version}", {"reason": reason})
    return get(db, key, version)  # type: ignore[return-value]


def clone(db: Database, key: str, version: int, new_key: str, new_name: str, actor: str, role: str) -> dict[str, Any]:
    t = get(db, key, version)
    if not t:
        raise TemplateRegistryError("원본 템플릿이 없습니다.")
    if db.one("SELECT 1 FROM templates WHERE template_key=?", (new_key,)):
        raise TemplateRegistryError("이미 존재하는 템플릿 키입니다.")
    body = copy.deepcopy(t["body"])
    body["template_key"], body["name"] = new_key, new_name
    for c in body.get("calculations", []):
        if c.get("approval_status") == "APPROVED":
            c["approval_status"] = "DRAFT"  # 복제본은 다시 승인받아야 한다
    if body.get("journal"):
        body["journal"]["policy_status"] = "DRAFT" if body["journal"].get("policy_status") == "APPROVED" else body["journal"].get("policy_status")
    return save_version(db, body, actor, role, f"{key}v{version}에서 복제")
