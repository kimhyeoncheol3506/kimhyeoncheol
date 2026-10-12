from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from finclose import intake, sample_data
from finclose.config import Settings
from finclose.service import Service

BASE = date(2026, 9, 30)


def make_settings(tmp: Path) -> Settings:
    return Settings(data_dir=tmp / "data", max_upload_mb=5, max_rows=50_000, min_free_disk_mb=1, host="127.0.0.1", port=0)


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    return make_settings(tmp_path)


@pytest.fixture()
def svc(settings: Settings) -> Service:
    s = Service(settings)
    yield s
    s.db.close()


@pytest.fixture(scope="session")
def samples(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("samples")
    return {"dir": out, **sample_data.generate_all(out)}


def upload(svc: Service, paths, user: str = "이담당") -> list[str]:
    ids = []
    for p in paths:
        with open(p, "rb") as f:
            ids.append(intake.save_upload(svc.db, svc.settings, f, Path(p).name, user, "preparer")["id"])
    return ids


def bond_run(svc: Service, paths: dict, base: str = "2026-09-30", **kw) -> dict:
    roles = {r: upload(svc, [p])[0] for r, p in paths.items()}
    return svc.create_run("BOND_EXT_PRICE_RECON", None, base, roles, kw.pop("overrides", {}), "이담당", "preparer", **kw)


def check(run: dict, cid: str) -> dict:
    return next(c for c in run["checks"] if c["check_id"] == cid)


def approve_and_finalize(svc: Service, run: dict) -> dict:
    rid = run["id"]
    for p in run["gate"]["pending_reviews"]:
        svc.act(rid, "ACKNOWLEDGE", p["check_id"], "확인함", "김검토", "reviewer")
    svc.act(rid, "REVIEW", None, "검토 완료", "김검토", "reviewer")
    svc.act(rid, "APPROVE", None, "승인", "박승인", "approver")
    return svc.finalize(rid, "확정", "박승인", "approver")
