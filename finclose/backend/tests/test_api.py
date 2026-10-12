from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from finclose.api import create_app


def H(user="이담당", role="preparer"):
    return {"X-FinClose-User": quote(user), "X-FinClose-Role": role}


def test_api_end_to_end(settings, samples):
    c = TestClient(create_app(settings))
    assert c.get("/api/health").json()["external_network"] == "NONE"
    files = [("files", (Path(p).name, open(p, "rb"))) for p in samples["current"].values()]
    r = c.post("/api/files", files=files, headers=H())
    assert r.status_code == 200 and all(x["ok"] for x in r.json())
    ids = [x["id"] for x in r.json()]
    a = c.post("/api/analyze", json={"file_ids": ids}, headers=H()).json()
    plan = a["plan"]
    body = {"template_key": plan["template_key"], "base_date": plan["base_date"],
            "files": {k: v["file_id"] for k, v in plan["roles"].items()}}
    run = c.post("/api/runs", json=body, headers=H()).json()
    assert run["status"] == "READY_FOR_REVIEW"
    dup = c.post("/api/runs", json=body, headers=H())
    assert dup.status_code == 409 and dup.json()["code"] == "DUPLICATE_RUN"
    rid = run["id"]
    # 권한
    assert c.post(f"/api/runs/{rid}/actions", json={"action": "APPROVE", "comment": "x"}, headers=H("뷰어", "viewer")).status_code == 403
    assert c.post("/api/files", files=[("files", ("a.csv", b"a,b\n1,2\n"))], headers=H("뷰어", "viewer")).status_code == 403
    for p in run["gate"]["pending_reviews"]:
        assert c.post(f"/api/runs/{rid}/actions", json={"action": "ACKNOWLEDGE", "check_id": p["check_id"], "comment": "확인"},
                      headers=H("김검토", "reviewer")).status_code == 200
    c.post(f"/api/runs/{rid}/actions", json={"action": "REVIEW", "comment": "검토"}, headers=H("김검토", "reviewer"))
    blocked = c.post(f"/api/runs/{rid}/finalize", json={"comment": "확정"}, headers=H("박승인", "approver"))
    assert blocked.status_code == 409
    c.post(f"/api/runs/{rid}/actions", json={"action": "APPROVE", "comment": "승인"}, headers=H("박승인", "approver"))
    fin = c.post(f"/api/runs/{rid}/finalize", json={"comment": "확정"}, headers=H("박승인", "approver"))
    assert fin.status_code == 200 and fin.json()["status"] == "FINALIZED"
    d = c.get(f"/api/runs/{rid}/files/final.xlsx?u=x&r=viewer")
    assert d.status_code == 200 and d.content[:2] == b"PK"
    assert c.get(f"/api/runs/{rid}/files/..%2Ffinclose.db?u=x&r=viewer").status_code == 404
    dash = c.get("/api/dashboard", headers=H()).json()
    assert dash["by_status"]["FINALIZED"] == 1 and dash["audit"]["ok"]
    assert c.get("/api/audit/verify", headers=H()).json()["ok"]
    assert c.put("/api/settings/materiality", json={"pct": "0.2"}, headers=H()).status_code == 403
    assert c.put("/api/settings/materiality", json={"pct": "0.2"}, headers=H("관리자", "admin")).json()["pct"] == "0.2"


def test_bad_role_and_user(settings):
    c = TestClient(create_app(settings))
    assert c.get("/api/runs", headers={"X-FinClose-Role": "root"}).status_code == 403
    assert c.get("/api/runs", headers={"X-FinClose-User": quote("<script>"), "X-FinClose-Role": "viewer"}).status_code == 403
